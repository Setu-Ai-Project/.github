"""
moderator.py (DEPRECATED)
=========================
Notice: This module is deprecated as part of the Wave 2 moderation consolidation.
All safety rules, entity masking, PII/injection filters, output text guardrails,
and mascot safety responses are now centrally maintained in `moderation.py`.

Please import directly from moderation.py:
    from moderation import moderate_prompt, moderate_output_text, ContentModerationError

This file is maintained as a backward-compatibility forwarder so existing callers
and unit tests continue to function without interruption.
"""

import warnings
from moderation import (
    moderate_prompt,
    moderate_output_text,
    moderate_image_response,
    ContentModerationError,
    ModerationResult,
    MODERATION_CATEGORIES,
    BUG_SAFETY_RESPONSES,
    UNSAFE_CATEGORIES,
    mask_entities,
)

warnings.warn(
    "moderator.py is deprecated and will be removed in a future release. "
    "Please update imports to use moderation.py instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "moderate_prompt",
    "moderate_output_text",
    "moderate_image_response",
    "ContentModerationError",
    "ModerationResult",
    "MODERATION_CATEGORIES",
    "BUG_SAFETY_RESPONSES",
    "UNSAFE_CATEGORIES",
    "mask_entities",
]


if __name__ == "__main__":
    print("=" * 60)
    print("Testing moderator.py (Backward-Compatibility Shim)")
    print("=" * 60)

    # Test that legacy dict access works
    res = moderate_prompt("A watercolor painting of a friendly robot")
    print(f"  Legacy res['is_safe']: {res['is_safe']}")
    assert res["is_safe"] is True

    # Test unsafe prompt through shim
    res_unsafe = moderate_prompt("A bloody battle with swords")
    print(f"  Legacy res_unsafe['is_safe']: {res_unsafe['is_safe']}")
    assert res_unsafe["is_safe"] is False
    print(f"  Legacy res_unsafe['mascot_message']: {res_unsafe['mascot_message'][:50]}...")

    print("\nmoderator.py deprecation shim verified successfully!")
