"""
limits.py
=========
In-Memory Daily Rate Limiter for SetuAI Learner Attempts and Hints.

PROTOTYPE NOTICE:
This in-memory implementation is a PROTOTYPE for AI research and local testing.
- Counts vanish on server/script restarts.
- Counts do not synchronize across distributed backend worker nodes or servers.
- The Backend team will store and enforce the real persistent counts in the database
  (PostgreSQL/Redis) as part of their Step 9 architecture.

Execution Rules:
1. Keeps counts in memory keyed by (user_id, action, UTC date).
2. Counts a use ONLY if the request is allowed.
3. If limit is reached, returns a kind, child-friendly message and does not increment.
4. Raises ValueError for any unrecognized action.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple, Any

# Path to configuration inside Ai Research/
CONFIG_FILE: Path = Path(__file__).resolve().parent / "limits_config.json"

# In-memory store: (user_id, action, utc_date) -> int (count of allowed uses today)
_USAGE_STORE: Dict[Tuple[str, str, str], int] = {}


@dataclass
class LimitResult:
    """
    Result returned by the rate limit check.

    Attributes:
    - allowed (bool): True if the action is permitted within daily limits; False otherwise.
    - used (int): Number of permitted actions consumed by the user today (including this one if allowed).
    - limit (int): Maximum actions allowed per day.
    - user_message (str): Kind, supportive feedback for the learner when a limit is reached.
    """
    allowed: bool
    used: int
    limit: int
    user_message: str


def load_limits_config() -> Dict[str, Any]:
    """
    Loads daily limit settings from limits_config.json.
    Falls back to safe default draft numbers if the file is missing or unreadable.
    """
    if not CONFIG_FILE.exists():
        return {
            "day_boundary": "UTC",
            "limits": {
                "prompt_attempt": 15,
                "hint": 5,
            },
        }

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "day_boundary": "UTC",
            "limits": {
                "prompt_attempt": 15,
                "hint": 5,
            },
        }


def check_and_record(user_id: str, action: str) -> LimitResult:
    """
    Validates whether a user can perform an action and records usage if allowed.

    Parameters:
    - user_id (str): Unique identifier for the student or session.
    - action (str): Action being attempted ('prompt_attempt' or 'hint').

    Returns:
    - LimitResult: Contains allowed status, used count, limit, and child-friendly message.

    Raises:
    - ValueError: If the action is not recognized in limits_config.json.
    """
    config = load_limits_config()
    limits_map = config.get("limits", {})

    if action not in limits_map:
        raise ValueError(
            f"Unknown action: '{action}'. Recognized actions from limits_config.json: {list(limits_map.keys())}"
        )

    limit = int(limits_map[action])

    # Date formatted as YYYY-MM-DD in UTC
    utc_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    store_key = (str(user_id), str(action), utc_date)

    current_used = _USAGE_STORE.get(store_key, 0)

    if current_used < limit:
        # Action is ALLOWED: increment usage and record
        new_used = current_used + 1
        _USAGE_STORE[store_key] = new_used
        return LimitResult(
            allowed=True,
            used=new_used,
            limit=limit,
            user_message="",
        )
    else:
        # Action is BLOCKED: do NOT increment count
        if action == "prompt_attempt":
            msg = f"You have used all {limit} tries for today. Come back tomorrow!"
        elif action == "hint":
            msg = f"You have used all {limit} hints for today. Try again tomorrow!"
        else:
            msg = f"You have used all {limit} for today. Come back tomorrow!"

        return LimitResult(
            allowed=False,
            used=current_used,
            limit=limit,
            user_message=msg,
        )


def _reset_store() -> None:
    """Helper to clear in-memory state during unit test runs."""
    _USAGE_STORE.clear()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing limits.py (In-Memory Prototype)")
    print("=" * 60)

    _reset_store()
    test_user = "student_jane_doe"

    # Test prompt attempts up to limit (15)
    print(f"Testing 'prompt_attempt' for user: {test_user} (Limit: 15)")
    for i in range(1, 16):
        res = check_and_record(test_user, "prompt_attempt")
        assert res.allowed is True
        assert res.used == i
    print(f"  Attempts 1 to 15 successfully allowed. Final used: {res.used}")

    # Attempt 16 must be blocked and NOT increment count
    blocked_res = check_and_record(test_user, "prompt_attempt")
    print(f"  Attempt 16 result: allowed={blocked_res.allowed}, used={blocked_res.used}")
    print(f"  Message: '{blocked_res.user_message}'")
    assert blocked_res.allowed is False
    assert blocked_res.used == 15
    assert "You have used all 15 tries for today. Come back tomorrow!" == blocked_res.user_message

    # Test hints limit (5) independently
    print(f"\nTesting 'hint' for user: {test_user} (Limit: 5)")
    for i in range(1, 6):
        res_hint = check_and_record(test_user, "hint")
        assert res_hint.allowed is True
        assert res_hint.used == i
    print(f"  Hints 1 to 5 successfully allowed. Final used: {res_hint.used}")

    # Hint 6 must be blocked
    blocked_hint = check_and_record(test_user, "hint")
    print(f"  Hint 6 result: allowed={blocked_hint.allowed}, used={blocked_hint.used}")
    print(f"  Message: '{blocked_hint.user_message}'")
    assert blocked_hint.allowed is False
    assert blocked_hint.used == 5
    assert "You have used all 5 hints for today. Try again tomorrow!" == blocked_hint.user_message

    # Test unknown action raising ValueError
    print("\nTesting unknown action error handling:")
    try:
        check_and_record(test_user, "unknown_action_type")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"  Correctly raised ValueError: {e}")

    print("\nAll limits.py self-tests PASSED successfully!")
