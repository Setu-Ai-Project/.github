from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.byte_fact import ByteFact, ByteFactRead

router = APIRouter(prefix="/byte-facts", tags=["Byte Facts"])


@router.get("/", response_model=list[ByteFactRead])
def get_byte_facts(
    module_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """Fetch byte facts, optionally filtered by module_id."""
    statement = select(ByteFact)
    if module_id is not None:
        statement = statement.where(ByteFact.module_id == module_id)
    return session.exec(statement).all()


@router.get("/{byte_fact_id}", response_model=ByteFactRead)
def get_byte_fact_by_id(
    byte_fact_id: int,
    session: Session = Depends(get_session),
):
    """Fetch a single byte fact by its ID."""
    statement = select(ByteFact).where(ByteFact.id == byte_fact_id)
    byte_fact = session.exec(statement).first()
    if not byte_fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Byte fact not found",
        )
    return byte_fact
