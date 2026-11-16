from fastapi import APIRouter, Depends

from auth import get_current_user
from models.user import User, UserMeResponse

router = APIRouter(tags=["Authentication"])


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserMeResponse:
    """Protected: returns the currently authenticated user's profile."""
    return UserMeResponse(
        id=current_user.id,  # type: ignore
        clerk_id=current_user.clerk_id,
        name=current_user.name,
        email=current_user.email,
    )
