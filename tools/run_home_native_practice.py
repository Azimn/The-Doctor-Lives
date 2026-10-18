"""Run frozen native-mapped Article 8 pilot, recording successes AND nulls."""
import argparse
import json
from pathlib import Path
from doctor_lives.home_native_practice import run_native_practice_screen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    r = run_native_practice_screen()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    keys = (
        "schema", "seeds", "neural_opportunities", "native_choice_distribution",
        "native_mapped_categories_seen_during_training", "training_accepted",
        "training_material_benefits", "training_blocked",
        "advice_abstentions", "heldout_neural_agreement",
        "all_worlds_verified", "all_restored_practices_verified",
        "observed_both_task_classes", "article_8_engineering_score_before_and_after",
    )
    print(json.dumps({k: r[k] for k in keys}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
