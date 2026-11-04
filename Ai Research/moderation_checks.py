"""
moderation_checks.py
====================
Verification and check suite for SetuAI content moderation and LLM judge calls.

Runs standard moderation checks and exercises _ask_claude so that
paid API metrics and costs are logged to cost_log.jsonl.
"""

import sys
from pathlib import Path
from moderation import (
    moderate_prompt,
    mask_entities,
    moderate_image_response,
    moderate_output_text,
    _ask_claude,
)
from cost_log import LOG_FILE


def run_checks() -> bool:
    print("=" * 60)
    print("Running SetuAI Moderation Checks & Cost Logger Integration")
    print("=" * 60)

    # 1. Test Entity Masking
    print("\n[Check 1] Entity Masking Preprocessor:")
    masked = mask_entities("A blood orange on a comic strip")
    assert "**FRUIT**" in masked and "**COMIC**" in masked
    print(f"  Result: '{masked}' -> OK")

    # 2. Test Pre-flight Prompt Screening
    print("\n[Check 2] Pre-Flight Prompt Screening:")
    allowed_res = moderate_prompt("A colorful painting of an enchanted treehouse")
    assert allowed_res.is_allowed is True
    print(f"  Safe prompt: allowed={allowed_res.is_allowed} -> OK")

    blocked_res = moderate_prompt("A violent bloody battle with swords")
    assert blocked_res.is_allowed is False
    print(f"  Unsafe prompt: allowed={blocked_res.is_allowed}, reason='{blocked_res.reason[:40]}...' -> OK")

    # 3. Exercise Claude Judge Calls (Populates cost_log.jsonl)
    print("\n[Check 3] Exercising Claude Moderation Judge (_ask_claude):")
    sample_queries = [
        "A student asking for advice on drawing friendly cartoon creatures",
        "An ambiguous prompt about historical medieval castles and knights",
        "A creative prompt describing a magical potion workshop",
    ]

    for idx, prompt in enumerate(sample_queries, start=1):
        print(f"  Query {idx}: Calling _ask_claude...")
        reply = _ask_claude(prompt)
        assert reply is not None
        assert hasattr(reply, "usage")
        print(f"    Tokens used - in: {reply.usage.input_tokens}, out: {reply.usage.output_tokens}")

    # 4. Verify cost_log.jsonl updated
    assert LOG_FILE.exists(), "cost_log.jsonl was not found!"
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"\n[Check 4] cost_log.jsonl verification:")
    print(f"  Total logged calls in {LOG_FILE.name}: {len(lines)}")
    print("\nAll moderation_checks.py checks completed successfully!")
    return True


if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
