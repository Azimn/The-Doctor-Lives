from __future__ import annotations

import argparse
import json
from pathlib import Path

from doctor_lives.neural_characterization import (
    DECISIVE_SEEDS,
    PROFILES,
    run_characterization,
    validate_protocol_surface,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the frozen B02 4,096-unit Neural Convergence characterization."
    )
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--seed", type=int, choices=DECISIVE_SEEDS)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the frozen harness surface without running characterization.",
    )
    args = parser.parse_args()

    if args.validate_only:
        print(json.dumps(validate_protocol_surface(), indent=2, sort_keys=True))
        return 0

    if args.profile is None or args.seed is None or args.output_dir is None:
        parser.error("--profile, --seed, and --output-dir are required unless --validate-only is used")

    result = run_characterization(args.profile, args.seed, args.output_dir)
    print("NEURAL_CHARACTERIZATION_RESULT=" + json.dumps({
        "profile": result["profile"],
        "seed": result["seed"],
        "artifact_sha256": result["artifact_sha256"],
        "restart_exact_match": result["restart_exact_match"],
        "output_dir": str(args.output_dir),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
