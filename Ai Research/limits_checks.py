"""
limits_checks.py
================
Verification test suite for SetuAI daily limits and rate limiting.

Tests:
1. Loops limit + 2 attempts for "test_user" on "prompt_attempt", printing allowed or BLOCKED.
2. Asserts the last attempt is blocked with a non-empty message.
3. Asserts user isolation: "another_user" is still allowed.
4. Asserts action isolation: "test_user" can still request a "hint".
"""

import sys
from limits import check_and_record, load_limits_config, _reset_store


def run_limits_checks() -> bool:
    print("=" * 60)
    print("Running SetuAI Daily Limits Verification Suite")
    print("=" * 60)

    # Start with a clean in-memory state for reproducible test execution
    _reset_store()

    config = load_limits_config()
    limit = int(config["limits"]["prompt_attempt"])
    test_user = "test_user"
    total_attempts = limit + 2

    print(f"\n[Step 1] Looping {total_attempts} attempts for '{test_user}' on 'prompt_attempt' (Limit: {limit}):")

    last_result = None
    for i in range(1, total_attempts + 1):
        res = check_and_record(test_user, "prompt_attempt")
        last_result = res
        if res.allowed:
            print(f"  Attempt {i:>2}: allowed (used: {res.used}/{res.limit})")
        else:
            print(f"  Attempt {i:>2}: BLOCKED — {res.user_message}")

    # Assertions
    print("\n[Step 2] Verifying boundary and isolation assertions:")

    # 1. Assert last attempt is blocked with a non-empty message
    assert last_result is not None, "No attempts recorded"
    assert not last_result.allowed, f"Expected last attempt to be blocked, but was allowed!"
    assert last_result.user_message and len(last_result.user_message.strip()) > 0, (
        "Expected non-empty user_message on blocked attempt!"
    )
    print("  ✓ Assertion 1: Last attempt is blocked with a non-empty message.")

    # 2. Assert another user is still allowed (per-user quota isolation)
    another_res = check_and_record("another_user", "prompt_attempt")
    assert another_res.allowed, "Expected 'another_user' to be allowed!"
    print(f"  ✓ Assertion 2: 'another_user' is still allowed (used: {another_res.used}/{another_res.limit}).")

    # 3. Assert test_user can still use hint (per-action quota isolation)
    hint_res = check_and_record(test_user, "hint")
    assert hint_res.allowed, "Expected 'test_user' to still be allowed to use 'hint'!"
    print(f"  ✓ Assertion 3: 'test_user' can still use 'hint' (used: {hint_res.used}/{hint_res.limit}).")

    print("\n" + "=" * 60)
    print("VERIFY PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_limits_checks()
    sys.exit(0 if success else 1)
