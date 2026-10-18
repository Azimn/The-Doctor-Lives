"""Reproduce frozen Article 7 transfer and archive all world/brain outcomes.

This script makes NO score or qualification tracker edits; failed/partial
cases remain records, not tuning feedback for the frozen pilot.
"""
import argparse
import json
from pathlib import Path

from doctor_lives.home_motivation_transfer import run_transfer_screen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    report = (
        run_transfer_screen(cases=("tired_and_thirsty",),
                            seeds=(1842,))
        if args.smoke else run_transfer_screen()
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    summary = {key: report[key] for key in (
        "schema", "seeds", "registered_case_count", "totals", "by_case",
        "resumes", "screening", "independent_transfer_gate",
        "engineering_score_before_and_after", "not_independent_blinded_holdout",
    )}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
