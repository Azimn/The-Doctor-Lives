#!/usr/bin/env python3
"""Validate and render the 34-Article engineering dashboard, using only stdlib.

Usage:
    python tools/render_articles_progress.py
    python tools/render_articles_progress.py --check
    python tools/render_articles_progress.py --stdout

The JSON source is the editable record. Never edit generated Markdown directly.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "articles_34_progress.json"
OUTPUT = ROOT / "docs" / "experiments" / "ARTICLES_34_PROGRESS.md"
GATES = ("defined", "mechanism", "integrated",
         "causal_controls", "independent_transfer")
WEIGHTS = {"defined": 10, "mechanism": 25, "integrated": 25,
           "causal_controls": 20, "independent_transfer": 20}
QUALIFICATIONS = {"Unassessable", "Supported", "Unsupported"}
BAR_WIDTH = 20


def score(item: dict, weights: dict = WEIGHTS) -> int:
    """Percent measures completed engineering gates, not Article qualification."""
    return max(1, sum(weights[gate] for gate in GATES if item["gates"][gate]))


def progress_bar(points: int, *, width: int = BAR_WIDTH) -> str:
    if type(points) is not int or not 1 <= points <= 100:
        raise ValueError("Progress must be an integer between 1 and 100")
    filled = (points * width + 50) // 100
    return "█" * filled + "░" * (width - filled)


def validate(data: dict) -> None:
    if data.get("schema") != "pretorius.articles34.engineering-progress.v1":
        raise ValueError("Unknown tracker schema")
    if data.get("gate_weights") != WEIGHTS or sum(WEIGHTS.values()) != 100:
        raise ValueError("Engineering gate weights must be fixed and total 100")
    if set(data.get("gate_labels", {})) != set(GATES):
        raise ValueError("Every engineering gate needs a label")
    date.fromisoformat(data["reviewed_on"])
    if not re.fullmatch(r"[0-9a-f]{64}", data.get("source_document_sha256", "")):
        raise ValueError("Expected SHA-256 of the canonical revised manuscript")
    items = data.get("articles")
    if not isinstance(items, list) or len(items) != 34:
        raise ValueError("Exactly 34 canonical Articles are required")
    if [item.get("id") for item in items] != list(range(1, 35)):
        raise ValueError("Article IDs must be unique and in original 1..34 order")
    refs = data.get("work_ref_urls", {})
    for item in items:
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            raise ValueError("Missing Article title")
        if item.get("baseline_readiness") not in {"Missing", "Partial", "Implemented"}:
            raise ValueError("Invalid baseline readiness")
        if not isinstance(item.get("mechanism"), str) or not item["mechanism"].strip():
            raise ValueError("Each Article needs an existing mechanism or stated gap")
        if not isinstance(item.get("next_step"), str):
            raise ValueError("Every Article needs a next-step field")
        flags = item.get("gates")
        if not isinstance(flags, dict) or set(flags) != set(GATES):
            raise ValueError("Each Article needs exactly the five gate flags")
        if any(type(value) is not bool for value in flags.values()):
            raise ValueError("Gate states must be booleans")
        if flags["integrated"] and not flags["mechanism"]:
            raise ValueError("Integration requires an implemented mechanism")
        if flags["causal_controls"] and not flags["integrated"]:
            raise ValueError("Causal controls require an integrated mechanism")
        if flags["independent_transfer"] and not flags["causal_controls"]:
            raise ValueError("Transfer requires causal controls")
        if score(item) == 100 and not all(flags.values()):
            raise ValueError("100 means every engineering gate is addressed")
        if score(item) < 100 and not item["next_step"].strip():
            raise ValueError("Incomplete Articles need actionable next work")
        qualification = item.get("qualification")
        if qualification not in QUALIFICATIONS:
            raise ValueError("Qualification is separate from engineering progress")
        if qualification != "Unassessable" and not item.get("qualification_evidence"):
            raise ValueError("Article qualification requires linked assessment evidence")
        links = item.get("work_refs", [])
        if not isinstance(links, list) or not links or any(ref not in refs for ref in links):
            raise ValueError("All work references must resolve to source links")


def escape_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ").strip()


def render(data: dict) -> str:
    validate(data)
    items = data["articles"]
    grades = [score(item, data["gate_weights"]) for item in items]
    average = round(sum(grades) / 34)
    addressed = sum(n == 100 for n in grades)
    supported = sum(item["qualification"] == "Supported" for item in items)
    plain_code = chr(96)
    lines = [
        "# Articles of Artificiality: 34-Article progress tracker",
        "",
        f"**Reviewed:** {data['reviewed_on']}  ",
        "**Scope:** Pretorius, including documented experimental work in unmerged PRs #61 and #63.",
        "",
        "## Overall engineering progress",
        "",
        f"{plain_code}{progress_bar(average)}{plain_code} **{average}/100** across all 34 Articles",
        "",
        f"**Engineering addressed (100/100):** {addressed}/34.  ",
        f"**Full-domain Article qualifications Supported:** {supported}/34.",
        "",
        "The percentages are transparent **engineering progress estimates**, not empirical",
        "probabilities, consciousness scores, or results of the manuscript's Article",
        "qualification procedure. A score of **100/100 means every engineering gate",
        "is addressed**, including independent transfer evidence. Even at 100, the",
        "separate full-domain qualification remains Unassessable until its registered",
        "assessment supports a different outcome.",
        "",
        "### Progress gates",
        "",
    ]
    for name in GATES:
        lines.append(f"- **{data['gate_weights'][name]} points:** "
                     f"{escape_cell(data['gate_labels'][name])}.")
    lines.extend([
        "",
        "All Articles currently have a defined scope (10 points). A further 25 points",
        "requires a prototype, 25 an actual integrated runtime mechanism, 20 a",
        "discriminating controlled experiment, and 20 independent held-out transfer.",
        "A fully unstarted Article would receive the minimum display value of 1.",
        "Gate decisions are a reviewable engineering assessment of the evidence,",
        "not an automatically inferred property of the code.",
        "",
        "## Article-by-Article dashboard",
        "",
        "| # | Article | Engineering progress | Qualification | Next evidence gate | Work |",
        "| :--: | --- | --- | --- | --- | --- |",
    ])
    for item, points in zip(items, grades):
        refs = ", ".join(f"[{ref}]({data['work_ref_urls'][ref]})"
                         for ref in item["work_refs"])
        lines.append(
            f"| {item['id']:02d} | {escape_cell(item['title'])} "
            f"| {plain_code}{progress_bar(points)}{plain_code} **{points}/100** "
            f"| {item['qualification']} "
            f"| {escape_cell(item['next_step'] or 'All engineering gates complete')} "
            f"| {refs} |"
        )
    lines.extend([
        "",
        "## How to update",
        "",
        "Edit " + plain_code + "research/articles_34_progress.json" + plain_code +
        " when an Article advances. Update its boolean gate, evidence",
        "references, next step, and review date in the **same commit**. Set an",
        "Article's qualification separately, and only with assessment evidence.",
        "",
        "Regenerate using:",
        "",
        plain_code * 3 + "bash",
        "python tools/render_articles_progress.py",
        "python tools/render_articles_progress.py --check",
        plain_code * 3,
        "",
        "The standalone CI workflow rejects stale dashboard output and invalid",
        "scoring transitions. This document is generated; do not hand-edit it.",
        "",
        "The original numbering is fixed. Article 11 contains identity and",
        "recognition considerations; Article 23 includes convergent profundity.",
        "The canonical revised manuscript is identified by SHA-256 " +
        plain_code + data["source_document_sha256"] + plain_code + ".",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true",
                        help="Fail if checked-in Markdown differs from the JSON")
    action.add_argument("--stdout", action="store_true",
                        help="Print the generated dashboard without writing")
    args = parser.parse_args(argv)
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    doc = render(data)
    if args.stdout:
        sys.stdout.write(doc)
    elif args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != doc:
            print("Article progress dashboard is stale. Run the renderer.", file=sys.stderr)
            return 1
        print("Articles dashboard is current (34 records)")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(doc, encoding="utf-8")
        print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
