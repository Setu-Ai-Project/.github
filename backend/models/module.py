from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class ModuleBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    order: int = Field(ge=0, index=True)


class Module(ModuleBase, table=True):
    __tablename__ = "modules"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ModuleCreate(ModuleBase):
    pass


class ModuleRead(ModuleBase):
    id: int
    created_at: datetime
