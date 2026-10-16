"""Run Article 7 isolated-home causal comparisons and retain full receipts."""
import argparse
import json
from pathlib import Path

from doctor_lives.home_motivation_causal import run_isolated_motivation_pilot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_isolated_motivation_pilot()
    result_text = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result_text, encoding="utf-8")
    print(result_text, end="")


if __name__ == "__main__":
    main()
