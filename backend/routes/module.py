"""Module management and query routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, select

try:
    from database import get_session
    from models.module import Module, ModuleRead
except ImportError:
    from backend.database import get_session
    from backend.models.module import Module, ModuleRead

router = APIRouter(prefix="/modules", tags=["Modules"])


@router.get("/", response_model=List[ModuleRead])
def get_modules(session: Session = Depends(get_session)):
    """Fetch all modules ordered by their order field."""
    statement = select(Module).order_by(col(Module.order))
    modules = session.exec(statement).all()
    return modules


@router.get("/{module_id}", response_model=ModuleRead)
def get_module_by_id(module_id: int, session: Session = Depends(get_session)):
    """Fetch an existing module by its ID."""
    module = session.get(Module, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )
    return module
