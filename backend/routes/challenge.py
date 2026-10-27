"""Routes for challenge completion and progression awards.

TODO: this endpoint must later be restricted so learners cannot call it directly
to skip challenges; completion should come only from validated submissions
(Pair B2's POST /submissions with status passed).
"""

from fastapi import APIRouter, Depends, HTTPException, status

try:
    from middleware.auth import get_current_user
    from models.challenge import (
        ChallengeCompletionRequest,
        ChallengeCompletionResponse,
    )
    from models.user import User
    from services.progression import (
        ChallengeNotFound,
        UserNotFound,
        award_xp,
    )
except ImportError:
    from backend.middleware.auth import get_current_user
    from backend.models.challenge import (
        ChallengeCompletionRequest,
        ChallengeCompletionResponse,
    )
    from backend.models.user import User
    from backend.services.progression import (
        ChallengeNotFound,
        UserNotFound,
        award_xp,
    )

router = APIRouter(tags=["Challenges"])


def _complete_challenge(user_id: int, challenge_id: int) -> dict:
    """Shared helper to award XP and map domain exceptions to HTTP 404."""
    try:
        return award_xp(user_id=user_id, challenge_id=challenge_id)
    except ChallengeNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


def complete_challenge_by_body(
    payload: ChallengeCompletionRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Complete a challenge for the authenticated learner.

    TODO: this endpoint must later be restricted so learners cannot call it directly
    to skip challenges; completion should come only from validated submissions
    (Pair B2's POST /submissions with status passed).
    """
    # Any user_id sent by the client is ignored; user identity is derived strictly from auth
    return _complete_challenge(user_id=current_user.id, challenge_id=payload.challenge_id)


router.add_api_route(
    "/complete-challenge",
    complete_challenge_by_body,
    methods=["POST"],
    response_model=ChallengeCompletionResponse,
    summary="Complete a challenge for the authenticated learner",
)
