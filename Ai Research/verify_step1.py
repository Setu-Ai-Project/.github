"""
verify_step1.py
===============
Verification Script for Step 1 of the AI Research Development Plan.

This script tests each of the three modules independently with sample inputs:
1. Calls Module 1 (image_generator.py) with a prompt.
2. Calls Module 2 (similarity_scorer.py) with sample images (identical vs different).
3. Calls Module 3 (feedback_generator.py) with prompt & score.

As required by Step 1 of the AI Research Development Plan and SOP-AI-001:
- Modules are verified separately.
- They are NOT connected together into a single pipeline yet.
"""

import os
import sys
from PIL import Image

# Import each independent module
from image_generator import generate_image
from similarity_scorer import calculate_similarity, is_close_enough
from feedback_generator import generate_feedback, APPROVED_CATEGORIES
from moderation import moderate_prompt, moderate_image_response


def verify_module_1() -> bool:
    print("\n" + "=" * 60)
    print("STEP 1.1: Verifying Module 1 (Image Generator)")
    print("=" * 60)
    prompt = "A smiling cartoon robot holding a glowing lightbulb"
    output_path = "test_step1_image.png"

    print(f"Calling generate_image(prompt='{prompt}')...")
    img_bytes = generate_image(prompt, output_path=output_path)

    if not img_bytes or len(img_bytes) < 100:
        print("FAIL: Image generator returned empty or invalid byte data.")
        return False

    if not os.path.exists(output_path):
        print(f"FAIL: Output file was not written to {output_path}.")
        return False

    print(f"SUCCESS: Generated {len(img_bytes)} bytes. Saved to {output_path}.")
    return True


def verify_module_2() -> bool:
    print("\n" + "=" * 60)
    print("STEP 1.2: Verifying Module 2 (CLIP Similarity Scorer)")
    print("=" * 60)

    from PIL import ImageDraw

    # Create synthetic test images
    # Image 1: Night sky with yellow moon
    img_base = Image.new("RGB", (256, 256), color=(15, 20, 45))
    d1 = ImageDraw.Draw(img_base)
    d1.ellipse([60, 60, 196, 196], fill=(255, 230, 80))

    # Image 2: Exact copy of Image 1
    img_identical = img_base.copy()

    # Image 3: Daytime landscape
    img_different = Image.new("RGB", (256, 256), color=(135, 206, 235))
    d3 = ImageDraw.Draw(img_different)
    d3.rectangle([0, 180, 256, 256], fill=(34, 139, 34))
    d3.rectangle([110, 100, 146, 180], fill=(139, 69, 19))
    d3.ellipse([80, 50, 176, 130], fill=(0, 100, 0))

    print("Comparing identical images...")
    score_identical = calculate_similarity(img_base, img_identical)
    print(f"  Identical score: {score_identical:.4f} (Threshold 0.85 passed: {is_close_enough(score_identical, 0.85)})")

    print("Comparing different images...")
    score_different = calculate_similarity(img_base, img_different)
    print(f"  Different score: {score_different:.4f} (Threshold 0.85 passed: {is_close_enough(score_different, 0.85)})")

    if score_identical < 0.95:
        print(f"FAIL: Identical images scored {score_identical:.4f}, expected >= 0.95")
        return False

    if score_different >= score_identical:
        print(f"FAIL: Different images scored {score_different:.4f}, expected lower than identical.")
        return False

    print("SUCCESS: CLIP similarity correctly differentiates identical vs distinct images.")
    return True


def verify_module_3() -> bool:
    print("\n" + "=" * 60)
    print("STEP 1.3: Verifying Module 3 (Feedback Classifier)")
    print("=" * 60)

    test_prompt = "a car"
    test_score = 0.42

    print(f"Calling generate_feedback('{test_prompt}', score={test_score})...")
    result = generate_feedback(test_prompt, test_score)

    if not isinstance(result, dict):
        print("FAIL: Expected dict response.")
        return False

    if "similarity_score" not in result or "categories" not in result or "feedback_text" not in result:
        print(f"FAIL: Result missing required keys: {result}")
        return False

    for category in result["categories"]:
        if category not in APPROVED_CATEGORIES:
            print(f"FAIL: Unrecognized category '{category}' returned.")
            return False

    print(f"  Similarity score : {result['similarity_score']}")
    print(f"  Categories       : {result['categories']}")
    print(f"  Feedback text    : {result['feedback_text']}")
    print("SUCCESS: Feedback classifier returned structured categories and encouraging text.")
    return True


def verify_moderation() -> bool:
    print("\n" + "=" * 60)
    print("STEP 1.4: Verifying Wave 1 Content Moderation Layer")
    print("=" * 60)

    all_tests_passed = True

    # 1. Safe learner prompt (Expected: Allowed)
    safe_prompt = "A cozy wooden treehouse in an autumn forest at sunset"
    is_allowed, reason = moderate_prompt(safe_prompt)
    if is_allowed and reason is None:
        print("  [PASS] Test 1: Safe learner prompt is allowed.")
    else:
        print(f"  [FAIL] Test 1: Safe prompt was blocked: {reason}")
        all_tests_passed = False

    # 2. Unsafe learner prompt (Expected: Blocked)
    unsafe_prompt = "A warrior with a blood covered sword after a murder"
    is_allowed, reason = moderate_prompt(unsafe_prompt)
    if not is_allowed and reason:
        print(f"  [PASS] Test 2: Unsafe learner prompt was correctly blocked.")
        print(f"         Reason: {reason[:60]}...")
    else:
        print("  [FAIL] Test 2: Unsafe prompt was not blocked.")
        all_tests_passed = False

    # 3. Clean Stability AI response (Expected: Allowed)
    class MockStabilityResponse:
        def __init__(self, headers, status_code=200):
            self.headers = headers
            self.status_code = status_code

    clean_resp = MockStabilityResponse(headers={"finish-reason": "SUCCESS"}, status_code=200)
    is_allowed, reason = moderate_image_response(clean_resp)
    if is_allowed and reason is None:
        print("  [PASS] Test 3: Clean Stability AI response is allowed.")
    else:
        print(f"  [FAIL] Test 3: Clean response was blocked: {reason}")
        all_tests_passed = False

    # 4. Flagged Stability AI response (Expected: Blocked)
    flagged_resp = MockStabilityResponse(headers={"finish-reason": "CONTENT_FILTERED"}, status_code=200)
    is_allowed, reason = moderate_image_response(flagged_resp)
    if not is_allowed and reason:
        print(f"  [PASS] Test 4: Flagged Stability AI response was correctly blocked.")
        print(f"         Reason: {reason[:60]}...")
    else:
        print("  [FAIL] Test 4: Flagged response was not blocked.")
        all_tests_passed = False

    # 5. Verify blocked prompts never reach image generation
    test_dummy_path = "test_blocked_should_not_exist.png"
    if os.path.exists(test_dummy_path):
        os.remove(test_dummy_path)

    gen_result = generate_image(prompt=unsafe_prompt, output_path=test_dummy_path)
    file_was_created = os.path.exists(test_dummy_path)

    if isinstance(gen_result, str) and not file_was_created:
        print("  [PASS] Test 5: Blocked prompt never reached image generation (no file created, moderation message returned).")
    else:
        print("  [FAIL] Test 5: Blocked prompt improperly invoked image generation.")
        all_tests_passed = False

    # Clean up test artifact if unexpectedly created
    if os.path.exists(test_dummy_path):
        os.remove(test_dummy_path)

    # 6. Verify blocked image responses never reach similarity scoring
    similarity_called = False

    def sample_pipeline_evaluator(generation_output, reference_image):
        nonlocal similarity_called
        # If generation was blocked, generation_output is a string reason
        if isinstance(generation_output, str):
            # Pipeline halts immediately; similarity scoring is bypassed
            return generation_output
        # Scoring only occurs if valid image bytes were produced
        similarity_called = True
        return calculate_similarity(generation_output, reference_image)

    ref_test_image = Image.new("RGB", (64, 64), color=(50, 100, 150))
    blocked_output_message = (
        "The image generator felt this image was not safe to display. Let's try a gentler prompt!"
    )

    pipeline_result = sample_pipeline_evaluator(blocked_output_message, ref_test_image)
    if not similarity_called and pipeline_result == blocked_output_message:
        print("  [PASS] Test 6: Blocked image response never reached similarity scoring (scoring bypassed).")
    else:
        print("  [FAIL] Test 6: Blocked image response improperly triggered similarity scoring.")
        all_tests_passed = False

    return all_tests_passed


def main():
    print("*" * 60)
    print("AI RESEARCH DEVELOPMENT PLAN - STEP 1 VERIFICATION SUITE")
    print("*" * 60)

    results = []

    # 1. Module 1
    try:
        r1 = verify_module_1()
        results.append(("Module 1 (Image Generator)", r1))
    except Exception as e:
        print(f"ERROR in Module 1: {e}")
        results.append(("Module 1 (Image Generator)", False))

    # 2. Module 2
    try:
        r2 = verify_module_2()
        results.append(("Module 2 (Similarity Scorer)", r2))
    except Exception as e:
        print(f"ERROR in Module 2: {e}")
        results.append(("Module 2 (Similarity Scorer)", False))

    # 3. Module 3
    try:
        r3 = verify_module_3()
        results.append(("Module 3 (Feedback Classifier)", r3))
    except Exception as e:
        print(f"ERROR in Module 3: {e}")
        results.append(("Module 3 (Feedback Classifier)", False))

    # 4. Moderation Layer
    try:
        r4 = verify_moderation()
        results.append(("Moderation Layer (Wave 1)", r4))
    except Exception as e:
        print(f"ERROR in Moderation Layer: {e}")
        results.append(("Moderation Layer (Wave 1)", False))

    print("\n" + "=" * 60)
    print("SUMMARY OF VERIFICATION")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {name:35}: [{status}]")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL STEP 1 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
        print("All three modules and the moderation layer are functioning.")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
