"""Routes for learner challenge submissions (Step 6 Contract)."""

from datetime import timezone
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from database import get_session
from middleware.auth import get_current_user
from models.challenge import Challenge
from models.submission import (
    Submission,
    SubmissionCreate,
    SubmissionResponse,
)
from models.user import User
from realtime.notify import notify_progress
from services.ai_moderation import check_learner_text_safety
from services.progression import award_xp
from services.verifier import verify_answer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions", tags=["Submissions"])


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

    # 2. Determine attempt number
    prev_count = session.exec(
        select(Submission).where(
            Submission.user_id == current_user.id,
            Submission.challenge_id == payload.challenge_id,
        )
    ).all()
    attempt_number = len(prev_count) + 1

    # 2.5 AI Research Safety Moderation check
    is_safe, safety_feedback = check_learner_text_safety(payload.answer_text)
    if not is_safe:
        submission = Submission(
            user_id=current_user.id,
            challenge_id=payload.challenge_id,
            answer_text=payload.answer_text,
            status="needs_revision",
            xp_awarded=0,
            attempt_number=attempt_number,
        )
        submission.feedback = [safety_feedback or "Let's keep our submissions friendly, safe, and creative!"]
        session.add(submission)
        session.commit()
        session.refresh(submission)
        return _to_response(submission)

    # 3. Verify answer against pedagogical challenge rules
    rules = {"min_words": 5}
    verification = verify_answer(payload.answer_text, rules)

    xp_awarded = 0
    if verification.passed:
        sub_status = "passed"
        feedback = ["Great work! Your answer meets all the requirements."]
        try:
            res = award_xp(user_id=current_user.id, challenge_id=payload.challenge_id)
            xp_awarded = res.get("xp_awarded", 0)
            try:
                notify_progress(res)
            except Exception:
                logger.warning("Realtime progress notification failed for user %s", current_user.id)
        except Exception as exc:
            logger.error("Failed to award XP on passing submission: %s", exc)
    else:
        sub_status = "needs_revision"
        feedback = verification.feedback

    # 4. Save submission record
    submission = Submission(
        user_id=current_user.id,
        challenge_id=payload.challenge_id,
        answer_text=payload.answer_text,
        status=sub_status,
        xp_awarded=xp_awarded,
        attempt_number=attempt_number,
    )
    submission.feedback = feedback
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
    stmt = stmt.order_by(Submission.created_at.desc())  # type: ignore

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
