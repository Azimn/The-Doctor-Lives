from __future__ import annotations

import argparse
import json
from pathlib import Path

from doctor_lives.neural_characterization import DECISIVE_SEEDS
from doctor_lives.neural_lesions import (
    run_causal_lesions,
    validate_lesion_protocol_surface,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run frozen B06 recurrent-core causal lesions using preserved "
            "B04/B05 artifacts."
        )
    )
    parser.add_argument("--seed", type=int, choices=DECISIVE_SEEDS)
    parser.add_argument("--control-dir", type=Path)
    parser.add_argument("--challenger-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if args.validate_only:
        print(
            json.dumps(
                validate_lesion_protocol_surface(),
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if (
        args.seed is None
        or args.control_dir is None
        or args.challenger_dir is None
        or args.output_dir is None
    ):
        parser.error(
            "--seed, --control-dir, --challenger-dir, and --output-dir "
            "are required unless --validate-only is used"
        )

    result = run_causal_lesions(
        args.seed,
        args.control_dir,
        args.challenger_dir,
        args.output_dir,
    )
    print(
        "NEURAL_LESION_RESULT="
        + json.dumps(
            {
                "seed": result["seed"],
                "artifact_sha256": result["artifact_sha256"],
                "intact_sham_behavioral_match_to_b05_restart": result[
                    "causal_contrasts"
                ]["intact_sham_behavioral_match_to_b05_restart"],
                "targeted_minus_random_damage": result[
                    "causal_contrasts"
                ]["targeted_minus_random_damage"],
                "output_dir": str(args.output_dir),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
