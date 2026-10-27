from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.spark_term import SparkTerm, SparkTermRead

router = APIRouter(prefix="/spark-terms", tags=["Spark Terms"])


@router.get("/", response_model=list[SparkTermRead])
def get_spark_terms(
    module_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """Fetch spark terms, optionally filtered by module_id."""
    statement = select(SparkTerm)
    if module_id is not None:
        statement = statement.where(SparkTerm.module_id == module_id)
    return session.exec(statement).all()


@router.get("/{spark_term_id}", response_model=SparkTermRead)
def get_spark_term_by_id(
    spark_term_id: int,
    session: Session = Depends(get_session),
):
    """Fetch a single spark term by its ID."""
    statement = select(SparkTerm).where(SparkTerm.id == spark_term_id)
    spark_term = session.exec(statement).first()
    if not spark_term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spark term not found",
        )
    return spark_term
