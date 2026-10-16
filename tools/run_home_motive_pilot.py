"""Execute first physical Doctor home-motive four-arm comparison."""
import argparse
import json
from pathlib import Path

from doctor_lives.home_motive_pilot import run_motive_pilot


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = run_motive_pilot()
    serialized = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
