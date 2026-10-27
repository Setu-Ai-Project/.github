import pytest
from services.verifier import VerificationResult, verify_answer

RULES = {"min_words": 8, "required_keywords": ["mood", "style"]}
GOOD = "calm beach at sunset with a warm mood in watercolor style"


def test_too_short():
    # 1. verify_answer("a beach", RULES) -> passed is False; one feedback line contains "too short" and "(you wrote 2)".
    result = verify_answer("a beach", RULES)
    assert result.passed is False
    assert any("too short" in line and "(you wrote 2)" in line for line in result.feedback)


def test_missing_required_keyword():
    # 2. verify_answer("a calm beach at sunset with warm orange light everywhere", RULES) -> fails, and "Your answer should mention 'mood'." is in the feedback.
    result = verify_answer("a calm beach at sunset with warm orange light everywhere", RULES)
    assert result.passed is False
    assert "Your answer should mention 'mood'." in result.feedback


def test_good_answer_passes():
    # 3. verify_answer(GOOD, RULES) -> passed is True, feedback == [].
    result = verify_answer(GOOD, RULES)
    assert result.passed is True
    assert result.feedback == []


def test_good_answer_case_insensitive():
    # 4. verify_answer(GOOD.upper(), RULES) -> passes (case-insensitive).
    result = verify_answer(GOOD.upper(), RULES)
    assert result.passed is True
    assert result.feedback == []


@pytest.mark.parametrize("empty_answer", ["", "   ", None])
def test_empty_or_whitespace_or_none(empty_answer):
    # 5. For each of "", "   " and None: fails with feedback == ["Your answer is empty. Write your answer and try again."].
    result = verify_answer(empty_answer, RULES)
    assert result.passed is False
    assert result.feedback == ["Your answer is empty. Write your answer and try again."]


def test_forbidden_words():
    # 6. verify_answer("a nice Thing here", {"forbidden_words": ["thing"]}) -> fails with ["Please remove 'thing' and be more specific."].
    result = verify_answer("a nice Thing here", {"forbidden_words": ["thing"]})
    assert result.passed is False
    assert result.feedback == ["Please remove 'thing' and be more specific."]


def test_must_include_any_of():
    # 7. {"must_include_any_of": ["sunset", "sunrise", "dusk"]}: "golden dusk sky" passes; "blue sky" fails with ["Include at least one of these ideas: sunset, sunrise, dusk."].
    rules = {"must_include_any_of": ["sunset", "sunrise", "dusk"]}
    passed_result = verify_answer("golden dusk sky", rules)
    assert passed_result.passed is True
    assert passed_result.feedback == []

    failed_result = verify_answer("blue sky", rules)
    assert failed_result.passed is False
    assert failed_result.feedback == ["Include at least one of these ideas: sunset, sunrise, dusk."]


def test_empty_or_none_rules():
    # 8. verify_answer("anything at all", {}) and verify_answer("anything at all", None) -> both pass.
    res_empty = verify_answer("anything at all", {})
    assert res_empty.passed is True
    assert res_empty.feedback == []

    res_none = verify_answer("anything at all", None)
    assert res_none.passed is True
    assert res_none.feedback == []


def test_min_words_exact_threshold():
    # 9. verify_answer("one two three four five six seven eight", {"min_words": 8}) -> passes (exactly 8 words is enough).
    result = verify_answer("one two three four five six seven eight", {"min_words": 8})
    assert result.passed is True
    assert result.feedback == []


def test_feedback_order():
    # 10. verify_answer("a beach", RULES).feedback has exactly 3 lines in this order: the too-short line, the 'mood' line, the 'style' line.
    result = verify_answer("a beach", RULES)
    assert result.passed is False
    assert len(result.feedback) == 3
    assert "too short" in result.feedback[0] and "(you wrote 2)" in result.feedback[0]
    assert result.feedback[1] == "Your answer should mention 'mood'."
    assert result.feedback[2] == "Your answer should mention 'style'."


def test_required_keywords_case_insensitivity():
    # 11. verify_answer("I like Mood", {"required_keywords": ["MOOD"]}) -> passes (both sides are lower-cased).
    result = verify_answer("I like Mood", {"required_keywords": ["MOOD"]})
    assert result.passed is True
    assert result.feedback == []


def test_unknown_rule_keys_ignored():
    # Unknown rule keys should be ignored
    result = verify_answer("just a simple answer", {"unknown_key": 123, "another_flag": True})
    assert result.passed is True
    assert result.feedback == []
