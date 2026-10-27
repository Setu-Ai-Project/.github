import pytest
from config.progression_rules import (
    LEVEL_THRESHOLDS,
    MAX_LEVEL,
    level_for_xp,
    xp_to_next_level,
)


@pytest.mark.parametrize(
    "total_xp, expected_level, expected_remaining",
    [
        (0, 1, 100),
        (99, 1, 1),
        (100, 2, 150),
        (249, 2, 1),
        (250, 3, 250),
        (500, 4, 500),
        (1000, 5, 0),
        (10000, 5, 0),
    ],
)
def test_progression_thresholds_and_remaining(
    total_xp: int, expected_level: int, expected_remaining: int
):
    assert level_for_xp(total_xp) == expected_level
    assert xp_to_next_level(total_xp) == expected_remaining


def test_level_boundaries():
    # 99 vs 100 boundary (Level 1 -> Level 2)
    assert level_for_xp(99) == 1
    assert xp_to_next_level(99) == 1
    assert level_for_xp(100) == 2
    assert xp_to_next_level(100) == 150

    # 249 vs 250 boundary (Level 2 -> Level 3)
    assert level_for_xp(249) == 2
    assert xp_to_next_level(249) == 1
    assert level_for_xp(250) == 3
    assert xp_to_next_level(250) == 250

    # 499 vs 500 boundary (Level 3 -> Level 4)
    assert level_for_xp(499) == 3
    assert xp_to_next_level(499) == 1
    assert level_for_xp(500) == 4
    assert xp_to_next_level(500) == 500

    # 999 vs 1000 boundary (Level 4 -> Level 5 / MAX_LEVEL)
    assert level_for_xp(999) == 4
    assert xp_to_next_level(999) == 1
    assert level_for_xp(1000) == 5
    assert xp_to_next_level(1000) == 0


def test_edge_cases_negative_xp():
    assert level_for_xp(-10) == 1
    assert xp_to_next_level(-10) == 100
    assert level_for_xp(-1) == 1
    assert xp_to_next_level(-1) == 100


def test_constants():
    assert LEVEL_THRESHOLDS[1] == 0
    assert LEVEL_THRESHOLDS[5] == 1000
    assert MAX_LEVEL == 5
