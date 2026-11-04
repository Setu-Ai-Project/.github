"""
analyze_log.py
==============
Log Analyzer & Cost Reporter for SetuAI.

Reads cost_log.jsonl and summarizes paid API consumption by feature:
- Number of calls made
- Average input tokens consumed per call
- Average output tokens produced per call
- Total estimated USD cost

Handles missing, non-existent, or empty log files gracefully.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Default path to cost_log.jsonl inside Ai Research/
DEFAULT_LOG_FILE: Path = Path(__file__).resolve().parent / "cost_log.jsonl"


def analyze_log(log_path: Optional[Path] = None) -> bool:
    """
    Parses cost_log.jsonl and prints a aggregated usage & cost report grouped by feature.

    Parameters:
    - log_path (Optional[Path]): Specific path to log file; defaults to cost_log.jsonl.

    Returns:
    - bool: True if logs were successfully analyzed, False if file was missing or empty.
    """
    target_path = log_path or DEFAULT_LOG_FILE

    # 1. Handle missing file
    if not target_path.exists():
        print(f"[INFO] Log file not found: '{target_path.name}'.")
        print("       No API calls have been logged yet. Run moderation_checks.py to generate activity.")
        return False

    # 2. Read and parse lines
    entries = []
    with open(target_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            cleaned = line.strip()
            if not cleaned:
                continue
            try:
                entries.append(json.loads(cleaned))
            except json.JSONDecodeError as e:
                print(f"[WARNING] Skipping malformed JSON line {line_num}: {e}")

    # 3. Handle empty file
    if not entries:
        print(f"[INFO] Log file '{target_path.name}' is currently empty.")
        print("       No API usage records found.")
        return False

    # 4. Aggregate metrics by feature
    # Structure: feature -> {"calls": int, "input_tokens": int, "output_tokens": int, "est_cost": float}
    stats: Dict[str, Dict[str, Any]] = {}

    for entry in entries:
        feature = str(entry.get("feature", "unknown_feature"))
        inp = int(entry.get("input_tokens", 0))
        out = int(entry.get("output_tokens", 0))
        cost = float(entry.get("est_cost", 0.0))

        if feature not in stats:
            stats[feature] = {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "est_cost": 0.0,
            }

        stats[feature]["calls"] += 1
        stats[feature]["input_tokens"] += inp
        stats[feature]["output_tokens"] += out
        stats[feature]["est_cost"] += cost

    # 5. Print formatted summary report
    print("=" * 72)
    print("                SETUAI API USAGE & COST SUMMARY REPORT                ")
    print("=" * 72)
    print(f"Source Log File: {target_path.name} | Total Logged Events: {len(entries)}")
    print("-" * 72)
    print(
        f"{'Feature':<24} | {'Calls':<6} | {'Avg In Tok':<10} | {'Avg Out Tok':<11} | {'Total Est Cost ($)':<18}"
    )
    print("-" * 72)

    total_all_calls = 0
    total_all_cost = 0.0

    for feature, data in sorted(stats.items()):
        calls = data["calls"]
        avg_in = data["input_tokens"] / calls if calls > 0 else 0.0
        avg_out = data["output_tokens"] / calls if calls > 0 else 0.0
        total_cost = data["est_cost"]

        total_all_calls += calls
        total_all_cost += total_cost

        print(
            f"{feature:<24} | {calls:<6} | {avg_in:<10.1f} | {avg_out:<11.1f} | ${total_cost:<17.6f}"
        )

    print("-" * 72)
    print(f"{'OVERALL TOTALS':<24} | {total_all_calls:<6} | {'-':<10} | {'-':<11} | ${total_all_cost:<17.6f}")
    print("=" * 72)
    return True


if __name__ == "__main__":
    # Allow passing custom file path via command line argument if desired
    custom_file = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    analyze_log(custom_file)
