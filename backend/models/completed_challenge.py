from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class CompletedChallengeBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    challenge_id: int = Field(foreign_key="challenges.id", index=True, nullable=False)
    xp_awarded: int = Field(default=0, ge=0)
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CompletedChallenge(CompletedChallengeBase, table=True):
    __tablename__ = "completed_challenges"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_user_completed_challenge"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)


class CompletedChallengeCreate(CompletedChallengeBase):
    pass


class CompletedChallengeRead(CompletedChallengeBase):
    id: int
