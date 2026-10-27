"""
eval_skeleton.py
================
Evaluates classify_feedback against the benchmark dataset in eval_set.csv.
Reads each test case, checks if any predicted category matches the expected ones,
and reports the overall match rate.
"""

import csv
from feedback import classify_feedback

CSV_FILE = "eval_set.csv"


def run_eval():
    """
    Reads eval_set.csv and evaluates feedback predictions against expected categories.
    """
    total_cases = 0
    matched_cases = 0

    print("Running Evaluation on eval_set.csv...\n")
    print(f"{'id':<4} | {'expected':<40} | {'got':<40} | result")
    print("-" * 95)

    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            case_id = row["id"]
            prompt = row["prompt"]
            score = float(row["score"])
            
            # Pass None if target_description is empty
            target_description = row["target_description"].strip() or None

            # Split expected categories by '|'
            expected_raw = row["expected_categories"].strip()
            expected_list = [c.strip() for c in expected_raw.split("|") if c.strip()]
            expected_set = set(expected_list)

            # Call the feedback classifier
            result = classify_feedback(prompt, score, target_description)
            
            # Extract returned category IDs
            got_list = [cat["id"] for cat in result.get("categories", [])]
            got_set = set(got_list)

            # Check for match:
            # - If expected categories are provided: match if there is at least one overlap
            # - If no categories are expected (e.g. invalid/empty prompt): match if none are returned
            if expected_set:
                is_match = bool(got_set & expected_set)
            else:
                is_match = (len(got_set) == 0 and not result.get("ok", True))

            if is_match:
                matched_cases += 1
                status = "MATCH"
            else:
                status = "MISMATCH"

            total_cases += 1

            # Format outputs for display
            expected_display = "|".join(expected_list) if expected_list else "(none)"
            got_display = ",".join(got_list) if got_list else "(none)"

            print(f"{case_id:<4} | {expected_display:<40} | {got_display:<40} | {status}")

    print("-" * 95)
    match_rate = (matched_cases / total_cases * 100) if total_cases > 0 else 0
    print(f"\nTotal Match Rate: {matched_cases}/{total_cases} ({match_rate:.1f}%)")


if __name__ == "__main__":
    run_eval()
