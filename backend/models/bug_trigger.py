from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class BugTriggerBase(SQLModel):
    module_id: int = Field(foreign_key="modules.id", index=True, nullable=False)
    trigger_phrase: str = Field(min_length=1, max_length=255)
    warning_message: str = Field(min_length=1, max_length=1000)


class BugTrigger(BugTriggerBase, table=True):
    __tablename__: str = "bug_triggers"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BugTriggerCreate(BugTriggerBase):
    pass


class BugTriggerRead(BugTriggerBase):
    id: int
    created_at: datetime
