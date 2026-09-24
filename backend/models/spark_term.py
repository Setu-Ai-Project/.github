from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class SparkTermBase(SQLModel):
    module_id: int = Field(foreign_key="modules.id", index=True, nullable=False)
    term: str = Field(min_length=1, max_length=150)
    definition: str = Field(min_length=1, max_length=1000)


class SparkTerm(SparkTermBase, table=True):
    __tablename__: str = "spark_terms"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SparkTermCreate(SparkTermBase):
    pass


class SparkTermRead(SparkTermBase):
    id: int
    created_at: datetime
