from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.bug_trigger import BugTrigger, BugTriggerRead

from pydantic import BaseModel
from services.ai_research_service import detect_mistakes

router = APIRouter(prefix="/bug-triggers", tags=["Bug Triggers"])


class CheckMistakesPayload(BaseModel):
    text: str
    module_id: Optional[str] = "default"


@router.post("/check", summary="Check learner text for Bug mistakes using AI Research")
def check_bug_mistakes(payload: CheckMistakesPayload) -> list[dict]:
    """Matches text against human-tagged mistake phrases and returns Bug hints."""
    return detect_mistakes(payload.text, payload.module_id or "default")



@router.get("/", response_model=list[BugTriggerRead])
def get_bug_triggers(
    module_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """Fetch bug triggers, optionally filtered by module_id."""
    statement = select(BugTrigger)
    if module_id is not None:
        statement = statement.where(BugTrigger.module_id == module_id)
    return session.exec(statement).all()


@router.get("/{bug_trigger_id}", response_model=BugTriggerRead)
def get_bug_trigger_by_id(
    bug_trigger_id: int,
    session: Session = Depends(get_session),
):
    """Fetch a single bug trigger by its ID."""
    statement = select(BugTrigger).where(BugTrigger.id == bug_trigger_id)
    bug_trigger = session.exec(statement).first()
    if not bug_trigger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug trigger not found",
        )
    return bug_trigger
