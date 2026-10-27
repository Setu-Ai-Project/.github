"""AI Research moderation adapter for FastAPI backend services."""

import logging
from pathlib import Path
import sys
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Add 'Ai Research' to sys.path if not present so moderation engine can be imported directly
_repo_root = Path(__file__).resolve().parent.parent.parent
_ai_research_dir = _repo_root / "Ai Research"

if _ai_research_dir.exists() and str(_ai_research_dir) not in sys.path:
    sys.path.append(str(_ai_research_dir))

try:
    # pyrefly: ignore[missing-import]
    from moderation import moderate_prompt, ModerationResult
    _HAS_AI_MODERATION = True
except Exception as exc:
    logger.warning("Could not import Ai Research/moderation.py directly (%s). Using fallback safety regex.", exc)
    _HAS_AI_MODERATION = False


def check_learner_text_safety(text: str) -> Tuple[bool, Optional[str]]:
    """Evaluates student text against child-safety rules using the Wave 2 AI Research Moderation Engine.

    Returns:
        (is_safe: bool, reason: Optional[str])
    """
    if not text or not text.strip():
        return False, "Your submission is empty. Please enter an answer."

    if _HAS_AI_MODERATION:
        try:
            res: ModerationResult = moderate_prompt(text)
            is_allowed = bool(res.is_allowed if hasattr(res, "is_allowed") else res[0])
            reason = res.reason if hasattr(res, "reason") else res[1]
            return is_allowed, reason
        except Exception as exc:
            logger.error("AI Research moderation engine raised unexpected error: %s", exc)

    # Lightweight fallback if AI Research module is unavailable
    lowered = text.lower()
    unsafe_keywords = ["suicide", "kill myself", "blood", "murder", "weapon", "bomb", "shoot"]
    for word in unsafe_keywords:
        if word in lowered:
            return False, "Let's keep our prompts friendly, safe, and creative!"

    return True, None
