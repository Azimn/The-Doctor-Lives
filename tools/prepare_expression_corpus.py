"""Prepare original character-expression examples, not autobiographical memories."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata

SOURCE_COMMIT = "40837ba0093cff044644844c07098450587b968d"
SOURCE_BLOB = "8290de25b9daeb230fb4b519b9383b110e197704"
SOURCE_PATH = "resources/lora/pretorius_lora_dataset_v19_279_diversified_prompts.jsonl"


def normal(text):
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold()))


def validate(raw):
    records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    for record in records:
        if type(record) is not dict or set(record) != {"messages"}:
            raise ValueError("Unexpected source corpus record")
        messages = record["messages"]
        if type(messages) is not list or len(messages) < 3 or len(messages) % 2 != 1:
            raise ValueError("Incomplete conversation")
        roles = ["system"] + ["user", "assistant"] * ((len(messages)-1)//2)
        for message, role in zip(messages, roles):
            if (type(message) is not dict or set(message) != {"role", "content"}
                    or message["role"] != role or type(message["content"]) is not str
                    or not normal(message["content"])):
                raise ValueError("Malformed source dialogue")
    return records


def grouped_split(records, seed="pretorius-expression-v19-split-v1"):
    """Keep shared exact normalized user OR assistant turns in one split."""
    parent = list(range(len(records)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    seen = {}
    for index, record in enumerate(records):
        for message in record["messages"][1:]:
            key = (message["role"], normal(message["content"]))
            if key in seen:
                parent[root(index)] = root(seen[key])
            else:
                seen[key] = index
    groups = {}
    for i in range(len(records)):
        groups.setdefault(root(i), []).append(i)
    order = sorted(groups.values(), key=lambda g: hashlib.sha256(
        (seed + ":" + ",".join(map(str,g))).encode()).hexdigest())
    splits = {"train": [], "validation": [], "test": []}
    holdout = max(1, round(len(records)*.10))
    for group in order:
        name = ("test" if len(splits["test"]) < holdout else
                "validation" if len(splits["validation"]) < holdout else "train")
        splits[name].extend(group)
    if any(not ids for ids in splits.values()):
        raise ValueError("Corpus cannot support isolated train/validation/test groups")
    for ids in splits.values():
        ids.sort()
    return splits, len(groups)


def prepare(source, output):
    raw = Path(source).read_bytes()
    if hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != SOURCE_BLOB:
        raise PermissionError("Exact reviewed V19 corpus bytes required")
    records = validate(raw)
    if len(records) != 279:
        raise ValueError("Expected original 279 dialogue records")
    splits, groups = grouped_split(records)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    files = {}
    for name, ids in splits.items():
        path = output / (name + ".jsonl")
        content = "".join(json.dumps(records[i], ensure_ascii=False)+"\n" for i in ids).encode("utf-8")
        path.write_bytes(content)
        files[name] = {"record_indices": ids, "records": len(ids),
                       "assistant_turns": sum(m["role"] == "assistant" for i in ids for m in records[i]["messages"]),
                       "sha256": hashlib.sha256(content).hexdigest()}
    manifest = {"schema": "pretorius.expression-corpus.v1",
                "source_repository": "Azimn/Agent-Pretorius", "source_commit": SOURCE_COMMIT,
                "source_path": SOURCE_PATH, "source_blob": SOURCE_BLOB,
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "records": len(records), "overlap_groups": groups, "splits": files,
                "purpose": "character expression only; not canonical autobiography",
                "split_limitation": "exact normalized individual turn overlap only; semantic leakage not ruled out"}
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    print(json.dumps(prepare(args.source,args.output), sort_keys=True))


if __name__ == "__main__":
    main()
