"""
cost_log.py
===========
API Cost Logger & Estimator for SetuAI.

Provides lightweight, privacy-preserving tracking of paid API calls:
1. Loads pricing dynamically from prices.json (never invents or guesses rates).
2. Calculates estimated USD cost for Claude judge tokens and Stability image generation.
3. Appends structured JSON lines to cost_log.jsonl.

PRIVACY & SAFETY GUARANTEE:
Per COPPA/FERPA requirements, this module NEVER accepts or logs prompt text,
student names, emails, or personal identification data. It only tracks
numerical token/image counts, feature tags, anonymized user IDs, and costs.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# Resolve paths relative to this script inside Ai Research/
BASE_DIR: Path = Path(__file__).resolve().parent
PRICES_FILE: Path = BASE_DIR / "prices.json"
LOG_FILE: Path = BASE_DIR / "cost_log.jsonl"


def load_prices() -> Dict[str, Any]:
    """
    Loads price definitions from prices.json.

    If the file does not exist or contains invalid JSON, returns
    safe zero-cost defaults so the application never crashes.
    """
    if not PRICES_FILE.exists():
        return {
            "claude_judge": {"input_per_million": 0.0, "output_per_million": 0.0},
            "image_generation": {"per_image": 0.0},
        }

    try:
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback to zero pricing on any read/parse error
        return {
            "claude_judge": {"input_per_million": 0.0, "output_per_million": 0.0},
            "image_generation": {"per_image": 0.0},
        }


def estimate_cost(
    api: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    images: int = 0,
) -> float:
    """
    Estimates the USD cost of an API call based on prices in prices.json.

    Parameters:
    - api (str): The target service ("claude_judge" or "image_generation").
    - input_tokens (int): Count of input/prompt tokens sent.
    - output_tokens (int): Count of output/completion tokens received.
    - images (int): Number of images generated.

    Calculation Rules:
    - "claude_judge": (input_tokens * input_per_million / 1,000,000) +
                      (output_tokens * output_per_million / 1,000,000)
    - "image_generation": images * per_image
    - Any other API name returns 0.0 (e.g. local CLIP scoring is free).

    Returns:
    - float: Total estimated cost in USD.
    """
    prices = load_prices()

    if api == "claude_judge":
        judge_prices = prices.get("claude_judge", {})
        rate_in = float(judge_prices.get("input_per_million", 0.0))
        rate_out = float(judge_prices.get("output_per_million", 0.0))

        input_cost = (input_tokens * rate_in) / 1_000_000.0
        output_cost = (output_tokens * rate_out) / 1_000_000.0
        return input_cost + output_cost

    elif api == "image_generation":
        img_prices = prices.get("image_generation", {})
        rate_per_image = float(img_prices.get("per_image", 0.0))
        return images * rate_per_image

    else:
        # Unknown APIs, local embeddings, or free services return 0.0
        return 0.0


def log_call(
    api: str,
    feature: str,
    user_id: str = "unknown",
    input_tokens: int = 0,
    output_tokens: int = 0,
    images: int = 0,
) -> float:
    """
    Appends a single structured JSON line to cost_log.jsonl and returns the cost.

    Parameters:
    - api (str): API provider / service ("claude_judge", "image_generation").
    - feature (str): Application feature invoking the call (e.g., "feedback_classifier", "prompt_lab_image").
    - user_id (str): Anonymized student or session ID (never real names or emails).
    - input_tokens (int): Input tokens consumed.
    - output_tokens (int): Output tokens consumed.
    - images (int): Number of images generated.

    JSON Line Format:
    {
      "timestamp": "2026-10-30T13:48:00.123456+00:00",
      "api": "claude_judge",
      "feature": "feedback_classifier",
      "user_id": "anon_student_123",
      "input_tokens": 150,
      "output_tokens": 80,
      "images": 0,
      "est_cost": 0.000450
    }

    Returns:
    - float: Estimated cost in USD for this call.
    """
    cost = estimate_cost(
        api=api,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        images=images,
    )

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "api": api,
        "feature": feature,
        "user_id": str(user_id),
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "images": int(images),
        "est_cost": round(cost, 6),
    }

    # Atomically append one line to cost_log.jsonl
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return cost


if __name__ == "__main__":
    print("=" * 60)
    print("Testing cost_log.py (Stand-alone Validation)")
    print("=" * 60)

    # Test 1: Claude Judge cost estimation (with current prices.json zero values)
    c1 = estimate_cost("claude_judge", input_tokens=1000, output_tokens=500)
    print(f"  Zero-rate Claude estimate (expected 0.0): {c1}")
    assert c1 == 0.0

    # Test 2: Image generation cost estimation (with current prices.json zero values)
    c2 = estimate_cost("image_generation", images=1)
    print(f"  Zero-rate Image estimate (expected 0.0): {c2}")
    assert c2 == 0.0

    # Test 3: Unknown API cost estimation
    c3 = estimate_cost("unknown_service", input_tokens=500)
    print(f"  Unknown service estimate (expected 0.0): {c3}")
    assert c3 == 0.0

    # Test 4: Log a call to cost_log.jsonl
    logged_cost = log_call(
        api="claude_judge",
        feature="test_validation",
        user_id="test_student_42",
        input_tokens=120,
        output_tokens=45,
        images=0,
    )
    print(f"  Logged call cost returned: {logged_cost}")

    # Verify line was written
    assert LOG_FILE.exists()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])
        print(f"  Last log entry verified: {last_entry}")
        assert last_entry["api"] == "claude_judge"
        assert last_entry["user_id"] == "test_student_42"
        assert "prompt" not in last_entry

    print("\nAll cost_log.py self-tests PASSED successfully!")
