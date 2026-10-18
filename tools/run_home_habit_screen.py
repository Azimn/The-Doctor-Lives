"""Execute Article 8 source-grounded household habit screen, storing full records."""
import argparse
import json
from pathlib import Path
from doctor_lives.home_habit_screen import run_habit_screen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = run_habit_screen()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(
            report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "schema", "article_08_engineering_score_before_and_after",
        "totals", "all_training_receipts_verified",
        "all_material_worlds_verified", "all_recalled_acts_physically_completed",
        "predeclared_screen_met")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
