"""
feedback_generator.py
=====================
Module 3: Anthropic API Feedback Generation.

This module formats learner prompt data and similarity scores, calls the
Anthropic API (Claude), and produces structured, constructive feedback aligned
with Bug's mascot voice (helpful, encouraging, never harsh).

Why this is separate:
In Step 1 & 3 of the AI Research Development Plan, feedback classification is
explicitly isolated from image generation and similarity scoring. If the feedback
tone or categories need tuning, this module can be tested and updated without
touching image models or rerunning expensive vision computations.

The 5 Fixed Feedback Categories (from SOP-AI-001):
  1. missing details
  2. poor specificity
  3. incorrect composition
  4. ambiguous instructions
  5. missing style information

Usage:
    from feedback_generator import generate_feedback

    result = generate_feedback(
        learner_prompt="a dog in a field",
        similarity_score=0.45
    )
    print(result["categories"])
    print(result["feedback_text"])
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Safety & Content Moderation integration (Track B2 Wave 1)
from moderator import moderate_prompt, moderate_output_text, ContentModerationError

# The 5 approved categories defined in the AI Research SOP & Development Plan
APPROVED_CATEGORIES = [
    "missing details",
    "poor specificity",
    "incorrect composition",
    "ambiguous instructions",
    "missing style information",
]

DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"


def build_feedback_prompt(learner_prompt: str, similarity_score: float) -> str:
    """
    Constructs the prompt template instructing Claude to evaluate the learner's prompt
    against the 5 fixed categories and respond in Bug's encouraging mascot voice.

    Args:
        learner_prompt: The prompt text submitted by the learner.
        similarity_score: The calculated CLIP similarity score (0.0 to 1.0).

    Returns:
        str: The fully formatted system/user prompt string.
    """
    categories_str = "\n".join([f"- {cat}" for cat in APPROVED_CATEGORIES])

    return f"""You are 'Bug', a friendly, encouraging learning mascot in SetuAI's AI Prompt Lab.
Your goal is to guide learners to write clearer, more expressive image-generation prompts.
Never sound scary, blunt, or mocking. Be warm, supportive, and constructive!

A learner just submitted this prompt:
"{learner_prompt}"

The image similarity score achieved was: {similarity_score:.2f} out of 1.00.

Evaluate the learner's prompt and choose which of the following FIXED categories apply:
{categories_str}

Rules:
1. Choose ONLY from the 5 approved categories above. Do NOT invent new categories.
2. If the similarity score is high (>= 0.80), you may return an empty list of categories.
3. For each selected category, provide exactly one encouraging sentence explaining how the learner can improve.
4. Provide an overall cheerful 1-2 sentence feedback message in Bug's voice.
5. Return your response ONLY as valid JSON in this exact structure:
{{
  "categories": ["selected_category_1", "selected_category_2"],
  "feedback_text": "Bug's warm, encouraging feedback message here."
}}
"""


def _mock_feedback(learner_prompt: str, similarity_score: float) -> Dict[str, Any]:
    """
    Generates a deterministic mock feedback dictionary when no Anthropic API key is provided.
    Allows beginners to test the module structure without incurring API costs.
    """
    print("[feedback_generator] Notice: ANTHROPIC_API_KEY not found or set to placeholder.")
    print("[feedback_generator] Generating structured response in mock mode.")

    if similarity_score >= 0.80:
        categories = []
        feedback = "Fantastic work! Bug here — your prompt created an image that closely matched the goal! You're getting the hang of prompt engineering!"
    else:
        # Assign realistic categories based on prompt length and keywords
        categories = []
        words = learner_prompt.strip().split()
        if len(words) < 5:
            categories.append("poor specificity")
            categories.append("missing details")
        if not any(w in learner_prompt.lower() for w in ["style", "digital", "oil", "photo", "realistic", "watercolor", "3d"]):
            categories.append("missing style information")

        if not categories:
            categories = ["missing details"]

        feedback = (
            f"Bug here to help! You reached a similarity score of {similarity_score:.2f}. "
            "You have a great starting idea! Try adding specific colors, lighting, and an artistic style to make your picture pop even more."
        )

    return {
        "similarity_score": round(similarity_score, 4),
        "categories": categories,
        "feedback_text": feedback,
    }


def generate_feedback(
    learner_prompt: str,
    similarity_score: float,
    api_key: Optional[str] = None,
    model: str = DEFAULT_ANTHROPIC_MODEL,
    skip_moderation: bool = False,
) -> Dict[str, Any]:
    """
    Calls the Anthropic API to generate structured feedback from a learner prompt
    and similarity score, with pre-flight input and post-flight output moderation.

    Args:
        learner_prompt: The prompt text submitted by the learner.
        similarity_score: Numeric score between 0.0 and 1.0.
        api_key: Optional Anthropic API key (defaults to ANTHROPIC_API_KEY env var).
        model: Anthropic model to use (default: claude-3-5-haiku-20241022).
        skip_moderation: If True, bypasses local moderation checks (default: False).

    Returns:
        dict:
            {
                "similarity_score": float,
                "categories": List[str],
                "feedback_text": str,
                "is_safe": bool
            }

    Raises:
        ValueError: If prompt is empty or similarity_score is out of bounds.
        RuntimeError: If API call fails.
    """
    if not learner_prompt or not learner_prompt.strip():
        raise ValueError("Learner prompt cannot be empty.")

    if not (0.0 <= similarity_score <= 1.0):
        raise ValueError(f"similarity_score must be between 0.0 and 1.0, got {similarity_score}")

    # Layer 1: Pre-Flight Input Moderation (Track B2 Wave 1)
    if not skip_moderation:
        mod_input = moderate_prompt(learner_prompt)
        if not mod_input["is_safe"]:
            return {
                "similarity_score": round(similarity_score, 4),
                "categories": [],
                "feedback_text": mod_input["mascot_message"],
                "is_safe": False,
                "moderation": mod_input,
            }

    key = api_key or os.getenv("ANTHROPIC_API_KEY")

    # Beginner-friendly mock fallback
    if not key or key == "your_anthropic_api_key_here":
        mock_res = _mock_feedback(learner_prompt, similarity_score)
        # Layer 3: Output moderation on mock feedback text
        mod_out = moderate_output_text(mock_res["feedback_text"])
        mock_res["feedback_text"] = mod_out["sanitized_text"]
        mock_res["is_safe"] = True
        return mock_res

    # Import Anthropic client only when key is provided
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "The 'anthropic' package is required. Install it with: pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=key)
    prompt_content = build_feedback_prompt(learner_prompt, similarity_score)

    print(f"[feedback_generator] Requesting feedback for prompt: '{learner_prompt}' (Score: {similarity_score:.2f})...")

    try:
        response = client.messages.create(
            model=model,
            max_tokens=600,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt_content}],
        )

        raw_text = response.content[0].text.strip()

        # Parse JSON from response
        # Extract JSON substring if wrapped in markdown backticks
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
        else:
            parsed = json.loads(raw_text)

        categories = parsed.get("categories", [])
        # Sanitize categories against the approved list
        validated_categories = [c.strip().lower() for c in categories if c.strip().lower() in APPROVED_CATEGORIES]
        feedback_text = parsed.get("feedback_text", "").strip()

        # Layer 3: Output Moderation Guardrail on LLM generated text
        mod_out = moderate_output_text(feedback_text)
        sanitized_text = mod_out["sanitized_text"]

        return {
            "similarity_score": round(similarity_score, 4),
            "categories": validated_categories,
            "feedback_text": sanitized_text,
            "is_safe": mod_out["is_safe"],
        }

    except Exception as e:
        raise RuntimeError(f"Failed to generate feedback via Anthropic API: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing feedback_generator.py (Module 3)")
    print("=" * 60)

    test_prompt = "cat"
    test_score = 0.35

    print(f"\nEvaluating test input:")
    print(f"  Learner Prompt: '{test_prompt}'")
    print(f"  Similarity Score: {test_score:.2f}")

    result = generate_feedback(test_prompt, test_score)

    print("\nFeedback Result:")
    print(f"  Similarity Score : {result['similarity_score']}")
    print(f"  Categories       : {result['categories']}")
    print(f"  Feedback Text    : {result['feedback_text']}")
    print(f"  Is Safe          : {result.get('is_safe', True)}")

    # Check that categories are valid
    for cat in result["categories"]:
        assert cat in APPROVED_CATEGORIES, f"Unexpected category: {cat}"

    # Test unsafe prompt handling
    unsafe_p = "unsafe_test with profanity"
    print(f"\nEvaluating unsafe test input: '{unsafe_p}'")
    unsafe_res = generate_feedback(unsafe_p, 0.40)
    print(f"  Is Safe          : {unsafe_res['is_safe']}")
    print(f"  Feedback Text    : {unsafe_res['feedback_text']}")
    assert unsafe_res["is_safe"] is False

    print("\nModule 3 verification completed successfully.")
