from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class CertificateBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    module_id: int = Field(foreign_key="modules.id", index=True, nullable=False)
    image_url: str = Field(nullable=False, max_length=500)
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Certificate(CertificateBase, table=True):
    __tablename__ = "certificates"
    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_user_module_certificate"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)


class CertificateCreate(CertificateBase):
    pass


class CertificateRead(CertificateBase):
    id: int
