#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def sha_array(a: np.ndarray) -> str:
    x = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(str(x.dtype).encode())
    h.update(np.asarray(x.shape, dtype=np.int64).tobytes())
    h.update(x.tobytes())
    return h.hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_reduce(values: np.ndarray, row_ptr: np.ndarray, op: str) -> np.ndarray:
    """Reduce CSR edge values per source, including zero-outdegree neurons.

    np.add.reduceat cannot accept a start index equal to len(values), which is
    exactly what a trailing empty CSR row produces. Reduce only non-empty rows
    and scatter the results back into a zero-initialized per-neuron vector.
    """
    counts = np.diff(row_ptr)
    nonempty = np.flatnonzero(counts > 0)
    work = values if op == "sum" else values.astype(np.float64) ** 2 if op == "sumsq" else None
    if work is None:
        raise ValueError(op)
    out = np.zeros(counts.size, dtype=np.result_type(work.dtype, np.float64 if op == "sumsq" else work.dtype))
    if nonempty.size:
        starts = row_ptr[:-1][nonempty]
        out[nonempty] = np.add.reduceat(work, starts)
    return out


def build_source_csr(df: pd.DataFrame, n: int):
    pre = df["Presynaptic_Index"].to_numpy(dtype=np.int64, copy=False)
    post = df["Postsynaptic_Index"].to_numpy(dtype=np.int64, copy=False)
    weight = df["Excitatory x Connectivity"].to_numpy(copy=False)
    order = np.lexsort((post, pre))
    pre = pre[order]
    post = post[order]
    weight = weight[order]
    if len(pre) and (
        pre.min() < 0 or post.min() < 0 or pre.max() >= n or post.max() >= n
    ):
        raise ValueError("edge endpoint outside neuron range")
    key = pre * np.int64(n) + post
    if len(key) > 1 and np.any(key[1:] == key[:-1]):
        raise ValueError("source connectivity contains parallel neuron pairs")
    degrees = np.bincount(pre, minlength=n).astype(np.int64)
    row_ptr = np.concatenate(([0], np.cumsum(degrees))).astype(np.int64)
    return row_ptr, post.astype(np.int32), np.asarray(weight), pre.astype(np.int32)


def balanced_scaffold(n: int, e: int):
    q, rem = divmod(e, n)
    degrees = np.full(n, q, dtype=np.int64)
    degrees[:rem] += 1
    row_ptr = np.concatenate(([0], np.cumsum(degrees))).astype(np.int64)
    src = np.repeat(np.arange(n, dtype=np.int32), degrees)
    starts = np.repeat(row_ptr[:-1], degrees)
    pos = np.arange(e, dtype=np.int64) - starts
    dst = ((src.astype(np.int64) + 1 + pos) % n).astype(np.int32)
    max_degree = int(degrees.max(initial=0))
    for i in range(max(0, n - max_degree - 1), n):
        a, b = int(row_ptr[i]), int(row_ptr[i + 1])
        if b > a:
            dst[a:b].sort()
    return row_ptr, dst, src


def source_invariants(row_ptr: np.ndarray, weights: np.ndarray) -> dict[str, str]:
    pos = (weights > 0).astype(np.int64)
    neg = (weights < 0).astype(np.int64)
    return {
        "positive_edges_per_source": sha_array(row_reduce(pos, row_ptr, "sum")),
        "negative_edges_per_source": sha_array(row_reduce(neg, row_ptr, "sum")),
        "signed_sum_per_source": sha_array(row_reduce(weights, row_ptr, "sum")),
        "abs_sum_per_source": sha_array(row_reduce(np.abs(weights), row_ptr, "sum")),
        "sumsq_per_source": sha_array(row_reduce(weights, row_ptr, "sumsq")),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--condition", required=True, choices=["degree", "random"])
    p.add_argument("--seed", required=True, type=int)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--completeness", required=True, type=Path)
    p.add_argument("--shuffle-repo", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--validation-output", required=True, type=Path)
    args = p.parse_args()

    sys.path.insert(0, str(args.shuffle_repo / "src"))
    from lif.shuffle_pack import shuffle_edges

    n = int(pd.read_csv(args.completeness).shape[0])
    source_df = pd.read_parquet(
        args.source,
        columns=["Presynaptic_Index", "Postsynaptic_Index", "Excitatory x Connectivity"],
    )
    src_row_ptr, source_dst, source_weights, source_pre = build_source_csr(source_df, n)
    e = int(len(source_dst))
    source_in = np.bincount(source_dst, minlength=n)
    source_out = np.diff(src_row_ptr)
    source_weight_sorted_sha = sha_array(np.sort(source_weights))

    if args.condition == "degree":
        row_ptr = src_row_ptr
        base_dst = source_dst
        base_weights = source_weights
        expected_in = source_in
        expected_out = source_out
        before_source_invariants = source_invariants(row_ptr, base_weights)
    else:
        row_ptr, base_dst, source_pre = balanced_scaffold(n, e)
        rng = np.random.default_rng(args.seed + 10000)
        base_weights = source_weights[rng.permutation(e)]
        expected_in = np.bincount(base_dst, minlength=n)
        expected_out = np.diff(row_ptr)
        before_source_invariants = None

    new_dst, new_weights, stats = shuffle_edges(
        row_ptr, base_dst, base_weights, seed=args.seed, max_rounds=1000
    )
    pre = np.repeat(np.arange(n, dtype=np.int32), np.diff(row_ptr))
    if len(pre) != e:
        raise RuntimeError("edge count changed")
    new_in = np.bincount(new_dst, minlength=n)
    new_out = np.bincount(pre, minlength=n)
    if not np.array_equal(new_in, expected_in):
        raise RuntimeError("in-degree preservation failed")
    if not np.array_equal(new_out, expected_out):
        raise RuntimeError("out-degree preservation failed")

    same_row = np.diff(pre.astype(np.int64)) == 0
    if len(new_dst) > 1 and np.any(np.diff(new_dst.astype(np.int64))[same_row] <= 0):
        raise RuntimeError("parallel/unsorted destinations remain")

    if args.condition == "degree":
        after = source_invariants(row_ptr, new_weights)
        if before_source_invariants != after:
            raise RuntimeError("per-source signed-weight invariants changed")
    else:
        if sha_array(np.sort(new_weights)) != source_weight_sorted_sha:
            raise RuntimeError("global signed-weight multiset changed")

    self_loops = int(np.count_nonzero(pre == new_dst))
    self_loop_fraction = self_loops / e
    if self_loop_fraction > 0.001:
        raise RuntimeError(
            f"self-loop fraction {self_loop_fraction:.6g} exceeds frozen 0.001 gate"
        )

    out_df = pd.DataFrame(
        {
            "Presynaptic_Index": pre,
            "Postsynaptic_Index": new_dst.astype(np.int32, copy=False),
            "Excitatory x Connectivity": new_weights,
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(args.output, index=False)
    del out_df

    validation = {
        "condition": args.condition,
        "seed": args.seed,
        "neurons": n,
        "edges": e,
        "repair_rounds": int(stats["repair_rounds"]),
        "edges_kept_against_shuffle_source": int(stats["edges_kept"]),
        "self_loops": self_loops,
        "self_loop_fraction": self_loop_fraction,
        "in_degree_sha256": sha_array(new_in),
        "out_degree_sha256": sha_array(new_out),
        "global_signed_weight_multiset_sha256": sha_array(np.sort(new_weights)),
        "source_global_signed_weight_multiset_sha256": source_weight_sorted_sha,
        "source_invariants_preserved": args.condition == "degree",
        "parallel_edges": 0,
        "connectivity_parquet_sha256": sha_file(args.output),
    }
    if args.condition == "degree":
        validation["per_source_invariants"] = before_source_invariants
        validation["matches_intact_in_degree"] = bool(np.array_equal(new_in, source_in))
        validation["matches_intact_out_degree"] = bool(np.array_equal(new_out, source_out))
        if not validation["matches_intact_in_degree"] or not validation["matches_intact_out_degree"]:
            raise RuntimeError("degree control does not exactly match intact degrees")

    args.validation_output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
