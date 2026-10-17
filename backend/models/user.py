from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

try:
    from pydantic import EmailStr
except ImportError:
    EmailStr = str  # type: ignore


class UserBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(index=True, max_length=255)


class User(UserBase, table=True):
    __tablename__: str = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, nullable=False, max_length=255)
    hashed_password: str = Field(nullable=False)
    # Links this row to the learner's Clerk login (e.g. "user_2abc"). Empty for old users.
    clerk_user_id: Optional[str] = Field(
        default=None, unique=True, index=True, max_length=255
    )
    total_xp: int = Field(default=0, nullable=False, ge=0)
    level: int = Field(default=1, nullable=False, ge=1)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UserCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)


class UserRead(UserBase):
    id: int
    total_xp: int = 0
    level: int = 1
    created_at: datetime
