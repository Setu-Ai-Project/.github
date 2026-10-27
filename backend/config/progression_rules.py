"""Progression engine rules and pure calculation functions.

This module defines the XP thresholds for levels 1 through 5 and pure
functions for determining a user's level and remaining XP to the next level.
It has zero dependencies on databases, routes, or external services.
"""

LEVEL_THRESHOLDS: dict[int, int] = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 1000,
}

MAX_LEVEL: int = max(LEVEL_THRESHOLDS.keys())


def level_for_xp(total_xp: int) -> int:
    """Return the highest level whose threshold is less than or equal to total_xp.

    If total_xp is negative, it treats total_xp as 0 (Level 1).
    """
    effective_xp = max(0, total_xp)
    current_level = 1
    for lvl in sorted(LEVEL_THRESHOLDS.keys()):
        if effective_xp >= LEVEL_THRESHOLDS[lvl]:
            current_level = lvl
        else:
            break
    return current_level


def xp_to_next_level(total_xp: int) -> int:
    """Return the XP remaining until the next level, or 0 at the maximum level.

    If total_xp is negative, it treats total_xp as 0.
    """
    effective_xp = max(0, total_xp)
    current_lvl = level_for_xp(effective_xp)
    if current_lvl >= MAX_LEVEL:
        return 0

    next_lvl = current_lvl + 1
    next_threshold = LEVEL_THRESHOLDS[next_lvl]
    return max(0, next_threshold - effective_xp)
