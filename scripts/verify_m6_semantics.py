"""Read-only M6 40-family semantic holdout. Frozen before any M6 mapper edit."""
from __future__ import annotations
import json
from pathlib import Path
from doctor_lives.semantic_intentions import semantic_category

FROZEN = Path(__file__).resolve().parents[1] / "tests/data/m6_semantic_heldout.json"

def measure() -> dict:
    source = json.loads(FROZEN.read_text(encoding="utf-8"))
    groups = source["families"]
    if len(groups) != 40 or len({g["id"] for g in groups}) != 40:
        raise AssertionError("Frozen 40-family corpus has changed")
    predictions = []
    for g in groups:
        if len(g["paraphrases"]) != 3:
            raise AssertionError("Each held-out intention must have three paraphrases")
        actual = [semantic_category(t) for t in g["paraphrases"]]
        predictions.append({"id": g["id"], "expected": g["category"], "mapped": actual,
                            "correct": sum(x == g["category"] for x in actual),
                            "stable": actual[0] == actual[1] == actual[2]})
    return {
        "schema": "pretorius.m6.semantic-heldout-report.v1",
        "source": FROZEN.as_posix(),
        "families": 40, "examples": 120,
        "category_correct": sum(g["correct"] for g in predictions),
        "category_accuracy": sum(g["correct"] for g in predictions) / 120,
        "stable_families": sum(g["stable"] for g in predictions),
        "paraphrase_stability": sum(g["stable"] for g in predictions) / 40,
        "predictions": predictions,
        "tuned_on_heldout": False,
    }

if __name__ == "__main__":
    print(json.dumps(measure(), sort_keys=True))
