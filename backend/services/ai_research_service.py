"""AI Research Integration Service for SetuAI Backend.

Connects the FastAPI backend directly to the AI Research modules:
- Content Moderation (Ai Research/moderation.py)
- Bug Mascot Mistake Detection (Ai Research/bug_stage1/bug_stage1.py)
- Prompt Feedback Classifier (Ai Research/feedback.py)
- Similarity Scorer (Ai Research/similarity_scorer.py)
"""

import logging
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Ensure 'Ai Research' directory and subdirectories are on sys.path
_backend_dir = Path(__file__).resolve().parent.parent
_repo_root = _backend_dir.parent
_ai_research_dir = _repo_root / "Ai Research"
_bug_stage1_dir = _ai_research_dir / "bug_stage1"

for p in (_ai_research_dir, _bug_stage1_dir):
    if p.exists() and str(p) not in sys.path:
        sys.path.append(str(p))

# -----------------------------------------------------------------------------
# 1. Moderation Engine
# -----------------------------------------------------------------------------
try:
    # pyrefly: ignore[missing-import]
    from moderation import moderate_prompt, ModerationResult
    _HAS_MODERATION = True
except Exception as exc:
    logger.warning("Could not import Ai Research/moderation.py directly (%s). Using fallback regex.", exc)
    _HAS_MODERATION = False


def check_content_safety(text: str) -> Tuple[bool, Optional[str]]:
    """Evaluates learner text against child-safety rules.

    Returns:
        (is_allowed: bool, reason: Optional[str])
    """
    if not text or not text.strip():
        return False, "Your submission is empty. Please enter an answer."

    if _HAS_MODERATION:
        try:
            res: ModerationResult = moderate_prompt(text)
            is_allowed = bool(res.is_allowed if hasattr(res, "is_allowed") else res[0])
            reason = res.reason if hasattr(res, "reason") else res[1]
            return is_allowed, reason
        except Exception as exc:
            logger.error("AI Research moderation engine raised error: %s", exc)

    # Standard fallback safety filter
    lowered = text.lower()
    unsafe_keywords = ["suicide", "kill myself", "blood", "murder", "weapon", "bomb", "shoot"]
    for word in unsafe_keywords:
        if word in lowered:
            return False, "Let's keep our prompts friendly, safe, and creative!"

    return True, None


# -----------------------------------------------------------------------------
# 2. Bug Stage 1 Mistake Detection
# -----------------------------------------------------------------------------
_MISTAKES_CACHE: Dict[str, List[Dict[str, Any]]] = {}

try:
    # pyrefly: ignore[missing-import]
    from bug_stage1 import find_mistakes, load_mistakes
    _HAS_BUG_STAGE1 = True

    # Preload sample mistakes
    sample_file = _bug_stage1_dir / "sample_mistakes.json"
    if sample_file.exists():
        _MISTAKES_CACHE["default"] = load_mistakes(str(sample_file))
except Exception as exc:
    logger.warning("Could not import Ai Research/bug_stage1 (%s).", exc)
    _HAS_BUG_STAGE1 = False


def detect_mistakes(text: str, module_key: str = "default") -> List[Dict[str, str]]:
    """Checks learner text against human-tagged mistake patterns.

    Returns a list of warnings: [{"id", "matched", "explanation", "fix_hint"}]
    """
    if not _HAS_BUG_STAGE1 or not text or not text.strip():
        return []

    mistakes = _MISTAKES_CACHE.get(module_key) or _MISTAKES_CACHE.get("default", [])
    if not mistakes:
        return []

    try:
        return find_mistakes(text, mistakes)
    except Exception as exc:
        logger.error("Error in bug mistake detection: %s", exc)
        return []


# -----------------------------------------------------------------------------
# 3. AI Research Status
# -----------------------------------------------------------------------------
def get_ai_research_status() -> Dict[str, Any]:
    """Returns the operational status of all AI Research integrations."""
    return {
        "moderation_engine_loaded": _HAS_MODERATION,
        "bug_mistake_detector_loaded": _HAS_BUG_STAGE1,
        "mistakes_catalog_count": len(_MISTAKES_CACHE.get("default", [])),
    }
