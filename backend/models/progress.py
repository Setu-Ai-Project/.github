from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ProgressBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    module_id: int = Field(foreign_key="modules.id", index=True, nullable=False)
    completed: bool = Field(default=False, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)


class Progress(ProgressBase, table=True):
    __tablename__ = "progress"  # type: ignore
    __table_args__ = (UniqueConstraint("user_id", "module_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ProgressCreate(ProgressBase):
    pass


class ProgressRead(ProgressBase):
    id: int
    created_at: datetime
