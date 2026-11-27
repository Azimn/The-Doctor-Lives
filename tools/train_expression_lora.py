"""Explicit local LoRA training of the Expression renderer, never the brain.

Requires a separately installed PyTorch/Transformers/PEFT environment and a
local, reviewed base-model snapshot. No network downloads or automatic adapter
deployment. Assistant-only supervised loss; held-out test remains separate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def tokens(tokenizer, messages):
    return list(tokenizer.apply_chat_template(messages, tokenize=True,
                                               add_generation_prompt=False))


def masked_example(tokenizer, messages, maximum):
    """Require prefix-compatible chat template; fail rather than mask wrong text."""
    full = tokens(tokenizer, messages)
    labels = [-100] * len(full)
    for i, message in enumerate(messages):
        if message["role"] != "assistant":
            continue
        prompt = list(tokenizer.apply_chat_template(messages[:i], tokenize=True,
                                                    add_generation_prompt=True))
        response = tokens(tokenizer, messages[:i+1])
        if (full[:len(response)] != response or response[:len(prompt)] != prompt
                or len(response) <= len(prompt)):
            raise ValueError("Base chat template not prefix-compatible for assistant-only masking")
        labels[len(prompt):len(response)] = response[len(prompt):]
    if len(full) > maximum:
        raise ValueError("Conversation exceeds context budget; do not silently truncate corpus")
    if all(x == -100 for x in labels):
        raise ValueError("Empty assistant supervision")
    return {"input_ids": full, "attention_mask": [1]*len(full), "labels": labels}


def read_split(root, manifest, name):
    raw = (root/(name+".jsonl")).read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest["splits"][name]["sha256"]:
        raise PermissionError("Expression training split changed")
    return [json.loads(line)["messages"] for line in raw.decode("utf-8").splitlines() if line]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-length", type=int, default=4096)
    parser.add_argument("--epochs", type=float, default=2.)
    parser.add_argument("--seed", type=int, default=1842)
    args = parser.parse_args()
    if args.output.exists() or not (args.base_model/"config.json").is_file():
        raise ValueError("Use a new output directory and an existing local base model")
    import os
    os.environ["HF_HUB_OFFLINE"]="1"
    os.environ["TRANSFORMERS_OFFLINE"]="1"
    import torch
    from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                              TrainingArguments, set_seed)
    from peft import LoraConfig, get_peft_model
    set_seed(args.seed)
    manifest = json.loads((args.corpus/"manifest.json").read_text("utf-8"))
    if manifest["source_blob"] != "8290de25b9daeb230fb4b519b9383b110e197704":
        raise PermissionError("Unexpected original expression corpus")
    base = args.base_model.resolve(strict=True)
    tokenizer = AutoTokenizer.from_pretrained(str(base), local_files_only=True, trust_remote_code=False)
    if not tokenizer.chat_template:
        raise ValueError("Base model needs an explicit reviewed chat template")
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    class Data(torch.utils.data.Dataset):
        def __init__(self, name):
            self.rows = [masked_example(tokenizer, m, args.max_length)
                         for m in read_split(args.corpus, manifest, name)]
        def __len__(self): return len(self.rows)
        def __getitem__(self, i): return self.rows[i]
    train, validation, test = Data("train"), Data("validation"), Data("test")
    def collate(rows):
        length=max(len(r["input_ids"]) for r in rows)
        return {k:torch.tensor([r[k]+[pad]*(length-len(r[k])) for r in rows])
                for k,pad in (("input_ids",tokenizer.pad_token_id),("attention_mask",0),("labels",-100))}
    model = AutoModelForCausalLM.from_pretrained(str(base), local_files_only=True,
                                               trust_remote_code=False, use_safetensors=True)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(task_type="CAUSAL_LM", r=16, lora_alpha=32,
                                             lora_dropout=.05, target_modules="all-linear"))
    trainer = Trainer(model=model, args=TrainingArguments(
        output_dir=str(args.output), per_device_train_batch_size=1,
        per_device_eval_batch_size=1, gradient_accumulation_steps=8,
        learning_rate=2e-4, num_train_epochs=args.epochs,
        seed=args.seed, eval_strategy="epoch", save_strategy="epoch",
        report_to=[], remove_unused_columns=False),
        train_dataset=train, eval_dataset=validation, data_collator=collate)
    trainer.train()
    metrics = trainer.evaluate(test, metric_key_prefix="heldout")
    model.save_pretrained(args.output/"adapter", safe_serialization=True)
    tokenizer.save_pretrained(args.output/"adapter")
    # Preserve exact local base bytes identity, not merely a model nickname.
    hashes={}
    for path in sorted(base.rglob("*")):
        if path.is_file():
            with path.open("rb") as stream:
                hashes[str(path.relative_to(base))]=hashlib.file_digest(stream,"sha256").hexdigest()
    (args.output/"training_receipt.json").write_text(json.dumps({
        "base_files_sha256":hashes, "corpus_manifest":manifest,
        "seed":args.seed, "epochs":args.epochs, "max_length":args.max_length,
        "heldout_metrics":metrics, "adapter_deployed":False,
        "character_behavior_qualified":False},indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
