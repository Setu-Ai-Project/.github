from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

try:
    from pydantic import EmailStr
except ImportError:
    EmailStr = str  # type: ignore


class UserBase(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None, index=True, max_length=255)


class User(UserBase, table=True):
    __tablename__: str = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Clerk user ID per Step D specification (e.g. "user_2abc"). Nullable for existing legacy users.
    clerk_id: Optional[str] = Field(
        default=None, unique=True, index=True, max_length=255
    )
    # Maintained for backwards compatibility with existing progression & realtime routes
    clerk_user_id: Optional[str] = Field(
        default=None, unique=True, index=True, max_length=255
    )
    email: Optional[EmailStr] = Field(
        default=None, unique=True, index=True, nullable=True, max_length=255
    )
    hashed_password: Optional[str] = Field(default=None, nullable=True)
    total_xp: int = Field(default=0, nullable=False, ge=0)
    level: int = Field(default=1, nullable=False, ge=1)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __init__(self, **data):
        # Automatically keep clerk_id and clerk_user_id in sync
        if "clerk_id" in data and "clerk_user_id" not in data:
            data["clerk_user_id"] = data["clerk_id"]
        elif "clerk_user_id" in data and "clerk_id" not in data:
            data["clerk_id"] = data["clerk_user_id"]
        super().__init__(**data)


class UserCreate(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)


class UserRead(UserBase):
    id: int
    clerk_id: Optional[str] = None
    total_xp: int = 0
    level: int = 1
    created_at: datetime


class UserMeResponse(SQLModel):
    """Dedicated response model for GET /me per Step F specification."""

    id: int
    clerk_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
