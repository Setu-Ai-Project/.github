"""Routes for learner challenge submissions (Step 6 Contract)."""

from datetime import timezone
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, func, select

from database import get_session
from middleware.auth import get_current_user
from models.challenge import Challenge
from models.submission import (
    Submission,
    SubmissionCreate,
    SubmissionResponse,
    SubmissionStatus,
)
from models.user import User
from realtime.notify import notify_progress
from services.ai_moderation import check_learner_text_safety
from services.progression import award_xp
from services.verifier import verify_answer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions", tags=["Submissions"])

PASS_MESSAGE = "Great work! Your answer meets all the requirements."
SAFETY_FALLBACK_MESSAGE = "Let's keep our submissions friendly, safe, and creative!"
# Used for challenges that don't have their own rules yet, so an answer still
# has to be a real attempt rather than a single word.
DEFAULT_RULES = {"min_words": 5}


def _to_response(sub: Submission) -> SubmissionResponse:
    created = sub.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    created_iso = created.isoformat().replace("+00:00", "Z")
    if not created_iso.endswith("Z"):
        created_iso += "Z"

    return SubmissionResponse(
        submission_id=sub.id or 0,
        challenge_id=sub.challenge_id,
        status=sub.status,
        feedback=sub.feedback,
        xp_awarded=sub.xp_awarded,
        attempt_number=sub.attempt_number,
        created_at=created_iso,
    )


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
def create_submission(
    payload: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SubmissionResponse:
    """Submit an answer for verification and progression (Step 6)."""
    # 1. Validate challenge exists
    challenge = session.get(Challenge, payload.challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    text = payload.answer_text.strip()

    # 2. Attempt number, and whether this learner already passed this challenge
    mine = (
        Submission.user_id == current_user.id,
        Submission.challenge_id == challenge.id,
    )
    previous = session.exec(select(func.count()).select_from(Submission).where(*mine)).one()
    attempt_number = previous + 1
    already_passed = session.exec(
        select(Submission).where(*mine, Submission.status == SubmissionStatus.PASSED)
    ).first() is not None

    # 3. AI Research safety moderation. Blank answers skip it so the verifier
    # gives the contract's "Your answer is empty" message instead.
    if text:
        is_safe, safety_feedback = check_learner_text_safety(text)
        if not is_safe:
            submission = Submission(
                user_id=current_user.id,
                challenge_id=challenge.id,
                answer_text=text,
                status=SubmissionStatus.NEEDS_REVISION,
                attempt_number=attempt_number,
            )
            submission.feedback = [safety_feedback or SAFETY_FALLBACK_MESSAGE]
            session.add(submission)
            session.commit()
            session.refresh(submission)
            return _to_response(submission)

    # 4. Save as pending first, so there is a record of what the learner sent
    # even if something below fails.
    submission = Submission(
        user_id=current_user.id,
        challenge_id=challenge.id,
        answer_text=text,
        status=SubmissionStatus.PENDING,
        attempt_number=attempt_number,
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)

    # 5. Verify the answer against this challenge's rules
    verification = verify_answer(text, challenge.rules or DEFAULT_RULES)

    if verification.passed:
        # 6. Passed: award XP on the first pass only (award_xp also guards itself).
        # award_xp errors are not caught: the request fails, the row stays pending
        # (pending doesn't count as passed), and the learner can retry for their XP.
        submission.status = SubmissionStatus.PASSED
        submission.feedback = [PASS_MESSAGE]
        if not already_passed:
            res = award_xp(user_id=current_user.id, challenge_id=challenge.id)
            submission.xp_awarded = res.get("xp_awarded", 0)
            try:
                notify_progress(res)
            except Exception:
                logger.warning("Realtime progress notification failed for user %s", current_user.id)
    else:
        # 7. Needs revision: store the specific feedback (a new list, so it saves)
        submission.status = SubmissionStatus.NEEDS_REVISION
        submission.feedback = list(verification.feedback)

    # 8. Save the result and respond
    session.add(submission)
    session.commit()
    session.refresh(submission)

    return _to_response(submission)


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> SubmissionResponse:
    """Retrieve a specific submission by ID."""
    submission = session.get(Submission, submission_id)
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )
    return _to_response(submission)


@router.get("", response_model=List[SubmissionResponse])
def list_submissions(
    challenge_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[SubmissionResponse]:
    """List submissions for the current authenticated user."""
    stmt = select(Submission).where(Submission.user_id == current_user.id)
    if challenge_id is not None:
        stmt = stmt.where(Submission.challenge_id == challenge_id)
    stmt = stmt.order_by(Submission.created_at.desc(), Submission.id.desc())  # type: ignore

    results = session.exec(stmt).all()
    return [_to_response(sub) for sub in results]


@router.post("/moderate")
def moderate_learner_input(
    payload: dict,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Real-time endpoint for frontend to check prompt text safety before submitting."""
    text = payload.get("text", "")
    is_safe, reason = check_learner_text_safety(text)
    return {"is_safe": is_safe, "reason": reason}
