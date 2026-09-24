"""Progress tracking and query routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

try:
    from database import get_session
    from models.progress import Progress, ProgressRead
except ImportError:
    from backend.database import get_session
    from backend.models.progress import Progress, ProgressRead

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/", response_model=List[ProgressRead])
def get_progress(
    user_id: Optional[int] = None,
    module_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """Fetch progress records, optionally filtered by user_id and/or module_id."""
    statement = select(Progress)
    if user_id is not None:
        statement = statement.where(Progress.user_id == user_id)
    if module_id is not None:
        statement = statement.where(Progress.module_id == module_id)
    progress_records = session.exec(statement).all()
    return progress_records


@router.get("/{progress_id}", response_model=ProgressRead)
def get_progress_by_id(progress_id: int, session: Session = Depends(get_session)):
    """Fetch an existing progress record by its ID."""
    progress = session.get(Progress, progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )
    return progress
