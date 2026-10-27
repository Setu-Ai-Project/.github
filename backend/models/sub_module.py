from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class SubModuleBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    order: int = Field(ge=0, index=True)
    module_id: int = Field(foreign_key="modules.id", index=True, nullable=False)


class SubModule(SubModuleBase, table=True):
    __tablename__ = "sub_modules"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SubModuleCreate(SubModuleBase):
    pass


class SubModuleRead(SubModuleBase):
    id: int
    created_at: datetime
