from __future__ import annotations

import argparse
import json

from doctor_lives.neural_robustness import (
    run_robustness,
    validate_robustness_protocol_surface,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run frozen B07 Neural Convergence robustness probes."
    )
    parser.add_argument("--seed", type=int)
    parser.add_argument("--control-dir")
    parser.add_argument("--challenger-dir")
    parser.add_argument("--b06-dir")
    parser.add_argument("--independent-control-dir")
    parser.add_argument("--independent-seed", type=int)
    parser.add_argument("--output-dir")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if args.validate_only:
        print(json.dumps(
            validate_robustness_protocol_surface(),
            indent=2,
            sort_keys=True,
        ))
        return

    required = {
        "seed": args.seed,
        "control_dir": args.control_dir,
        "challenger_dir": args.challenger_dir,
        "b06_dir": args.b06_dir,
        "independent_control_dir": args.independent_control_dir,
        "independent_seed": args.independent_seed,
        "output_dir": args.output_dir,
    }
    missing = [name for name, value in required.items() if value is None]
    if missing:
        parser.error("missing required arguments: " + ", ".join(missing))

    result = run_robustness(**required)
    print(json.dumps(
        {
            "status": result["status"],
            "seed": result["seed"],
            "repository_sha": result["repository_sha"],
            "artifact_sha256": result["artifact_sha256"],
            "contrasts": result["contrasts"],
        },
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
