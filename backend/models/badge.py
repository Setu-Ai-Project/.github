from typing import Optional
from sqlmodel import Field, SQLModel


class BadgeBase(SQLModel):
    slug: str = Field(unique=True, index=True, nullable=False, max_length=100)
    name: str = Field(min_length=1, max_length=150, nullable=False)
    description: str = Field(default="", max_length=500)
    rule_type: str = Field(nullable=False, max_length=100)
    rule_value: int = Field(nullable=False, ge=0)


class Badge(BadgeBase, table=True):
    __tablename__ = "badges"

    id: Optional[int] = Field(default=None, primary_key=True)


class BadgeCreate(BadgeBase):
    pass


class BadgeRead(BadgeBase):
    id: int
