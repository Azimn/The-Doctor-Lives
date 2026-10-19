#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--annotations", required=True, type=Path)
    p.add_argument("--completeness", required=True, type=Path)
    p.add_argument("--ids-output", required=True, type=Path)
    p.add_argument("--summary-output", required=True, type=Path)
    args = p.parse_args()

    ann = pd.read_csv(
        args.annotations,
        sep="\t",
        usecols=["root_id", "flow"],
        dtype={"root_id": "Int64", "flow": "string"},
    )
    comp = pd.read_csv(args.completeness, index_col=0)
    backend_ids = {int(v) for v in comp.index}

    flow = ann["flow"].fillna("").str.strip().str.lower()
    aff = ann.loc[flow.eq("afferent"), "root_id"].dropna()
    annotation_afferents = {int(v) for v in aff.tolist()}
    ids = sorted(annotation_afferents & backend_ids)
    if not ids:
        raise SystemExit("no official afferent IDs intersect the pinned backend")

    payload = "".join(f"{v}\n" for v in ids).encode("utf-8")
    args.ids_output.parent.mkdir(parents=True, exist_ok=True)
    args.ids_output.write_bytes(payload)

    summary = {
        "annotation_rows": int(len(ann)),
        "annotation_afferent_rows": int(flow.eq("afferent").sum()),
        "annotation_afferent_unique_ids": int(len(annotation_afferents)),
        "backend_neurons": int(len(backend_ids)),
        "intersection_afferents": int(len(ids)),
        "candidate_ids_sha256": sha256_bytes(payload),
        "first_id": int(ids[0]),
        "last_id": int(ids[-1]),
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
