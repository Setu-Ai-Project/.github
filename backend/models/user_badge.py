from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class UserBadgeBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    badge_id: int = Field(foreign_key="badges.id", index=True, nullable=False)
    awarded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UserBadge(UserBadgeBase, table=True):
    __tablename__ = "user_badges"
    __table_args__ = (
        UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)


class UserBadgeCreate(UserBadgeBase):
    pass


class UserBadgeRead(UserBadgeBase):
    id: int
