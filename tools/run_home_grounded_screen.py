"""Execute and preserve matched physically grounded Doctor household actions."""
import argparse
import json
from pathlib import Path

from doctor_lives.home_grounded_screen import run_grounded_screen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    result = (
        run_grounded_screen(cases=("empty_tea",), seeds=(1842,))
        if args.smoke else run_grounded_screen())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
    print(json.dumps({key: result[key] for key in
          ("schema", "cases", "seeds", "offers_per_trial", "totals",
           "checks", "article8_score_before_after")},
          indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
