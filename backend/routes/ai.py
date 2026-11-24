"""AI Research API endpoints exposing AI capabilities to Frontend and Services."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel

from services.ai_research_service import (
    check_content_safety,
    detect_mistakes,
    get_ai_research_status,
)

router = APIRouter(prefix="/ai", tags=["AI Research"])


class ModerateRequest(BaseModel):
    text: str


class ModerateResponse(BaseModel):
    is_safe: bool
    reason: Optional[str] = None


class CheckMistakesRequest(BaseModel):
    text: str
    module_id: Optional[str] = "default"


class MistakeItem(BaseModel):
    id: str
    matched: str
    explanation: str
    fix_hint: str


class CheckMistakesResponse(BaseModel):
    mistakes: List[MistakeItem]
    count: int


@router.get("/status", summary="Check loaded AI Research models and engines")
def ai_status() -> Dict[str, Any]:
    """Returns availability and status of AI Research components."""
    return get_ai_research_status()


@router.post(
    "/moderate",
    response_model=ModerateResponse,
    summary="Evaluate learner prompt or answer for child safety",
)
def moderate_text(payload: ModerateRequest) -> ModerateResponse:
    """Evaluates input text against AI Research child-safety moderation rules."""
    is_safe, reason = check_content_safety(payload.text)
    return ModerateResponse(is_safe=is_safe, reason=reason)


@router.post(
    "/mistakes",
    response_model=CheckMistakesResponse,
    summary="Match answer against human-tagged mistake patterns (Bug Mascot)",
)
def check_for_mistakes(payload: CheckMistakesRequest) -> CheckMistakesResponse:
    """Uses Bug Stage 1 static mistake matcher from AI Research."""
    mistakes = detect_mistakes(payload.text, payload.module_id or "default")
    items = [
        MistakeItem(
            id=m["id"],
            matched=m["matched"],
            explanation=m["explanation"],
            fix_hint=m.get("fix_hint", ""),
        )
        for m in mistakes
    ]
    return CheckMistakesResponse(mistakes=items, count=len(items))
