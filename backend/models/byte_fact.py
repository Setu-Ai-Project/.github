from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class ByteFactBase(SQLModel):
    module_id: int = Field(foreign_key="modules.id", index=True, nullable=False)
    fact: str = Field(min_length=1, max_length=1000)


class ByteFact(ByteFactBase, table=True):
    __tablename__: str = "byte_facts"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ByteFactCreate(ByteFactBase):
    pass


class ByteFactRead(ByteFactBase):
    id: int
    created_at: datetime
