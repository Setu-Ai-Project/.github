"""
test_similarity.py
==================
Test script to compare sample images using similarity_scorer.
"""

import os
from similarity_scorer import score_similarity, THRESHOLD


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    same_a_path = os.path.join(base_dir, "sample_images", "same_a.png")
    same_b_path = os.path.join(base_dir, "sample_images", "same_b.png")
    different_path = os.path.join(base_dir, "sample_images", "different.png")

    # Compare same_a.png with same_b.png
    score_same = score_similarity(same_a_path, same_b_path)
    status_same = "PASS" if score_same >= THRESHOLD else "FAIL"

    # Compare same_a.png with different.png
    score_diff = score_similarity(same_a_path, different_path)
    status_diff = "PASS" if score_diff >= THRESHOLD else "FAIL"

    # Output results
    print(f"Threshold: {THRESHOLD}")
    print(f"Comparison 1 (same_a.png vs same_b.png):")
    print(f"  Score : {score_same:.4f}")
    print(f"  Result: {status_same}")

    print(f"\nComparison 2 (same_a.png vs different.png):")
    print(f"  Score : {score_diff:.4f}")
    print(f"  Result: {status_diff}")


if __name__ == "__main__":
    main()
