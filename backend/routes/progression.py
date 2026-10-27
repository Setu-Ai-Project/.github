"""User progression and overview routes."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

try:
    from config.progression_rules import xp_to_next_level
    from database import get_session
    from middleware.auth import get_current_user_id
    from models.badge import Badge
    from models.certificate import Certificate
    from models.user import User
    from models.user_badge import UserBadge
except ImportError:
    from backend.config.progression_rules import xp_to_next_level
    from backend.database import get_session
    from backend.middleware.auth import get_current_user_id
    from backend.models.badge import Badge
    from backend.models.certificate import Certificate
    from backend.models.user import User
    from backend.models.user_badge import UserBadge

router = APIRouter(prefix="/progress", tags=["Progression"])


class BadgeProgressRead(BaseModel):
    slug: str
    name: str
    awarded_at: datetime


class CertificateProgressRead(BaseModel):
    module_id: int
    image_url: str
    issued_at: datetime


class UserProgressMeRead(BaseModel):
    total_xp: int
    level: int
    xp_to_next_level: int
    badges: list[BadgeProgressRead] = []
    certificates: list[CertificateProgressRead] = []


@router.get("/me", response_model=UserProgressMeRead)
def get_my_progress(
    clerk_user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> UserProgressMeRead:
    """Fetch current user's level, XP, remaining XP, earned badges, and certificates."""
    statement = select(User).where(User.clerk_user_id == clerk_user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    xp_needed = xp_to_next_level(user.total_xp)

    badge_stmt = (
        select(Badge.slug, Badge.name, UserBadge.awarded_at)
        .join(Badge, UserBadge.badge_id == Badge.id)
        .where(UserBadge.user_id == user.id)
        .order_by(UserBadge.awarded_at.asc())
    )
    badge_rows = session.exec(badge_stmt).all()
    badges = [
        BadgeProgressRead(slug=slug, name=name, awarded_at=awarded_at)
        for slug, name, awarded_at in badge_rows
    ]

    cert_stmt = (
        select(Certificate.module_id, Certificate.image_url, Certificate.issued_at)
        .where(Certificate.user_id == user.id)
        .order_by(Certificate.issued_at.asc())
    )
    cert_rows = session.exec(cert_stmt).all()
    certificates = [
        CertificateProgressRead(
            module_id=module_id, image_url=image_url, issued_at=issued_at
        )
        for module_id, image_url, issued_at in cert_rows
    ]

    return UserProgressMeRead(
        total_xp=user.total_xp,
        level=user.level,
        xp_to_next_level=xp_needed,
        badges=badges,
        certificates=certificates,
    )
