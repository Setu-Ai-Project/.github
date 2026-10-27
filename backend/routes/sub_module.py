"""Sub-module management and query routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, select

try:
    from database import get_session
    from models.sub_module import SubModule, SubModuleRead
except ImportError:
    from backend.database import get_session
    from backend.models.sub_module import SubModule, SubModuleRead

router = APIRouter(prefix="/sub-modules", tags=["Sub-Modules"])


@router.get("/", response_model=List[SubModuleRead])
def get_sub_modules(
    module_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """Fetch sub-modules, optionally filtered by module_id."""
    statement = select(SubModule)
    if module_id is not None:
        statement = statement.where(SubModule.module_id == module_id)
    statement = statement.order_by(col(SubModule.order))
    sub_modules = session.exec(statement).all()
    return sub_modules


@router.get("/{sub_module_id}", response_model=SubModuleRead)
def get_sub_module_by_id(sub_module_id: int, session: Session = Depends(get_session)):
    """Fetch an existing sub-module by its ID."""
    sub_module = session.get(SubModule, sub_module_id)
    if not sub_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-module not found",
        )
    return sub_module
