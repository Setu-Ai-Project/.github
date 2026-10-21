from dataclasses import dataclass, field


@dataclass
class VerificationResult:
    passed: bool
    feedback: list[str] = field(default_factory=list)


def verify_answer(answer_text: str, rules: dict) -> VerificationResult:
    # 1. Empty answer check: if text is empty, return immediately
    text = (answer_text or "").strip()
    if not text:
        return VerificationResult(False, ["Your answer is empty. Write your answer and try again."])

    # 2. Setup rules, lowered text, word count, and feedback collector
    rules = rules or {}
    lowered = text.lower()
    word_count = len(text.split())
    feedback: list[str] = []

    # 3. Check min_words (int): if set and word_count < min_words, add error
    min_words = rules.get("min_words")
    if min_words is not None and word_count < min_words:
        feedback.append(f"Your answer is too short. Aim for at least {min_words} words (you wrote {word_count}).")

    # 4. Check required_keywords (list): for each keyword not found, add error
    required_keywords = rules.get("required_keywords") or []
    for keyword in required_keywords:
        if keyword.lower() not in lowered:
            feedback.append(f"Your answer should mention '{keyword}'.")

    # 5. Check must_include_any_of (list): if non-empty and none found, add error
    any_of = rules.get("must_include_any_of") or []
    if any_of and not any(item.lower() in lowered for item in any_of):
        feedback.append("Include at least one of these ideas: " + ", ".join(any_of) + ".")

    # 6. Check forbidden_words (list): for each word found, add error
    forbidden_words = rules.get("forbidden_words") or []
    for word in forbidden_words:
        if word.lower() in lowered:
            feedback.append(f"Please remove '{word}' and be more specific.")

    # 7. Return verification result (passed if no feedback messages)
    return VerificationResult(passed=len(feedback) == 0, feedback=feedback)
