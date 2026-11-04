"""
cost_model.py
=============
Cost Estimation Model for a Single Prompt-Challenge Attempt in SetuAI.

Calculates the granular breakdown of paid external API costs for ONE full
student attempt across the entire challenge execution lifecycle:
1. Pre-flight / Judge Prompt Moderation (Claude judge)
2. Image Generation (Stability AI Core API)
3. Image Output Moderation (Claude vision / response inspection)
4. Feedback Categorization (Claude LLM)
5. CLIP Similarity Scoring ($0.00 - runs 100% locally)

RULES:
- Never invent or hardcode pricing numbers; reads rates dynamically from prices.json.
- Token counts are initialized to (0, 0) drafts until calibrated with averages from analyze_log.py.
"""

import json
from pathlib import Path
from typing import Dict, Tuple, Any

# Resolve paths inside Ai Research/
BASE_DIR: Path = Path(__file__).resolve().parent
PRICES_FILE: Path = BASE_DIR / "prices.json"

# ==============================================================================
# Token Usage Estimates: (input_tokens, output_tokens)
# ==============================================================================
# NOTE TO DEVELOPER / RESEARCHER:
# Replace these default (0, 0) values with the empirical averages calculated by
# analyze_log.py once real student test attempts have populated cost_log.jsonl!
TOKENS: Dict[str, Tuple[int, int]] = {
    "moderation_prompt": (0, 0),  # Average (input_tokens, output_tokens) for prompt moderation judge
    "moderation_image": (0, 0),   # Average (input_tokens, output_tokens) for image moderation checks
    "feedback": (0, 0),           # Average (input_tokens, output_tokens) for Claude feedback generation
}


def load_prices() -> Dict[str, Any]:
    """
    Reads pricing configuration from prices.json.

    Returns default zero rates if the file is missing or unreadable to prevent crashes.
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
        return {
            "claude_judge": {"input_per_million": 0.0, "output_per_million": 0.0},
            "image_generation": {"per_image": 0.0},
        }


class CostAttemptResult(dict):
    """
    Dictionary representing cost components for one attempt.
    Supports both formatted keys ("moderation (prompt)") and snake_case aliases ("moderation_prompt").
    """

    _ALIASES = {
        "moderation_prompt": "moderation (prompt)",
        "image_gen": "image generation",
        "image_generation": "image generation",
        "moderation_image": "moderation (image)",
        "similarity_score": "similarity",
    }

    def __getitem__(self, key: str) -> Any:
        canonical_key = self._ALIASES.get(key, key)
        return super().__getitem__(canonical_key)

    def get(self, key: str, default: Any = None) -> Any:
        canonical_key = self._ALIASES.get(key, key)
        return super().get(canonical_key, default)


def cost_per_attempt() -> CostAttemptResult:
    """
    Computes and returns a dictionary of cost components for ONE full attempt.

    Components calculated:
    - "moderation (prompt)": Token cost for LLM judge screening prompt text.
    - "image generation": Cost per single generated image from Stability AI.
    - "moderation (image)": Cost for provider/LLM vision moderation check on generated image.
    - "feedback": Token cost for Claude analyzing prompt + score and generating feedback.
    - "similarity": $0.00 (Local open-source CLIP ViT-B/32 inference).
    - "total": Sum of all component costs.

    Returns:
    - CostAttemptResult: Dictionary containing rounded cost breakdown in USD.
    """
    prices = load_prices()

    # Rate definitions from prices.json
    claude_rates = prices.get("claude_judge", {})
    rate_in = float(claude_rates.get("input_per_million", 0.0))
    rate_out = float(claude_rates.get("output_per_million", 0.0))

    img_rates = prices.get("image_generation", {})
    rate_per_image = float(img_rates.get("per_image", 0.0))

    # 1. Moderation (prompt) cost
    mod_prompt_in, mod_prompt_out = TOKENS.get("moderation_prompt", (0, 0))
    cost_mod_prompt = (mod_prompt_in * rate_in / 1_000_000.0) + (mod_prompt_out * rate_out / 1_000_000.0)

    # 2. Image generation cost (1 image generated per student attempt)
    cost_image_gen = 1 * rate_per_image

    # 3. Moderation (image) cost
    mod_img_in, mod_img_out = TOKENS.get("moderation_image", (0, 0))
    cost_mod_img = (mod_img_in * rate_in / 1_000_000.0) + (mod_img_out * rate_out / 1_000_000.0)

    # 4. Feedback cost
    fb_in, fb_out = TOKENS.get("feedback", (0, 0))
    cost_feedback = (fb_in * rate_in / 1_000_000.0) + (fb_out * rate_out / 1_000_000.0)

    # 5. Local similarity scoring (CLIP model running locally in PyTorch)
    cost_similarity = 0.0

    # Calculate Total
    total = cost_mod_prompt + cost_image_gen + cost_mod_img + cost_feedback + cost_similarity

    result = CostAttemptResult({
        "moderation (prompt)": round(cost_mod_prompt, 6),
        "image generation": round(cost_image_gen, 6),
        "moderation (image)": round(cost_mod_img, 6),
        "feedback": round(cost_feedback, 6),
        "similarity": round(cost_similarity, 6),
        "total": round(total, 6),
    })

    return result


# ==============================================================================
# Worst-Case vs. Expected Cost Definitions
# ==============================================================================
# - WORST-CASE DAILY COST:
#   The theoretical upper bound on spending per student. Assumes a learner hits
#   100% of their daily allowed quota (e.g. all 20 attempts and 5 hints).
#   Used by infrastructure and finance teams to size risk limits and balance caps.
#
# - EXPECTED DAILY COST / PLATFORM BUDGET:
#   The realistic financial projection based on average learner behavior.
#   In practice, students rarely exhaust their full daily limit; most complete
#   a challenge in 3–5 attempts and 1–2 hints.
# ==============================================================================

def daily_cost_per_user(
    attempt_limit: int,
    hint_limit: int = 0,
    cost_per_hint: float = 0.0,
) -> float:
    """
    Calculates the WORST-CASE daily API cost for ONE user.

    Assumes the student consumes 100% of their allocated daily attempts and hints.

    Parameters:
    - attempt_limit (int): Maximum challenge attempts allowed per user per day.
    - hint_limit (int): Maximum hints allowed per user per day (default 0).
    - cost_per_hint (float): Estimated API cost per hint request (default 0.0).

    Returns:
    - float: Total maximum daily cost in USD rounded to 6 decimal places.
    """
    attempt_cost = cost_per_attempt()["total"]
    worst_case = (attempt_limit * attempt_cost) + (hint_limit * cost_per_hint)
    return round(worst_case, 6)


def total_daily_budget(
    active_users: int,
    expected_attempts_per_user: float,
    expected_hints_per_user: float = 0.0,
    cost_per_hint: float = 0.0,
) -> float:
    """
    Calculates the total EXPECTED daily platform budget across all active users.

    Uses average/projected user engagement rather than the worst-case ceiling.

    Parameters:
    - active_users (int): Count of daily active learners on the platform.
    - expected_attempts_per_user (float): Projected average attempts per active user.
    - expected_hints_per_user (float): Projected average hints per active user.
    - cost_per_hint (float): Estimated API cost per hint request.

    Returns:
    - float: Total expected daily spending in USD rounded to 6 decimal places.
    """
    attempt_cost = cost_per_attempt()["total"]
    avg_user_cost = (expected_attempts_per_user * attempt_cost) + (expected_hints_per_user * cost_per_hint)
    total_budget = active_users * avg_user_cost
    return round(total_budget, 6)


if __name__ == "__main__":
    print("=" * 64)
    print("        SETUAI COST MODEL — ESTIMATE PER ATTEMPT        ")
    print("=" * 64)

    costs = cost_per_attempt()

    print(f"  - moderation (prompt) : ${costs['moderation (prompt)']:.6f}")
    print(f"  - image generation    : ${costs['image generation']:.6f}")
    print(f"  - moderation (image)  : ${costs['moderation (image)']:.6f}")
    print(f"  - feedback            : ${costs['feedback']:.6f}")
    print(f"  - similarity          : ${costs['similarity']:.6f}  (Local CLIP, $0.00)")
    print("-" * 64)
    print(f"  TOTAL ESTIMATED COST  : ${costs['total']:.6f}")
    print("=" * 64)

    # Worst-case cost per user per day table for limits 5, 10, 15, and 20
    print("\n" + "=" * 64)
    print("     WORST-CASE DAILY COST PER USER (BY ATTEMPT LIMIT)          ")
    print("=" * 64)
    print(f"{'Attempt Limit':<16} | {'Hint Limit':<12} | {'Worst-Case Cost / User / Day':<26}")
    print("-" * 64)

    # Assume draft hint limit of 5 hints and 0.0 draft cost_per_hint
    for attempts in [5, 10, 15, 20]:
        wc_cost = daily_cost_per_user(attempt_limit=attempts, hint_limit=5, cost_per_hint=0.0)
        print(f"{attempts:<16} | {5:<12} | ${wc_cost:<25.6f}")

    print("=" * 64)
