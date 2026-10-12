"""Static release inventory of Pretorius's shipped model-access entrypoints.

The gate is intentionally narrow: it proves that the current package
has no *new unreviewed provider-import paths*. It is not a sandbox,
transitive-dependency audit or proof that dynamic Python cannot bypass
SubjectOnlyRendererPort. Independent runtime review remains mandatory.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "doctor_lives"

# Historical engineer/research-only paths, NOT authorized production renderers.
RESEARCH_ONLY = {
    "vector_fly_eval.py": {"urllib"},  # Direct external Ollama experiments.
    "neural_characterization.py": {"subprocess"},
    "neural_lesions.py": {"subprocess"},
    "neural_robustness.py": {"subprocess"},
}

MODEL_PROVIDER_ROOTS = {
    "urllib", "requests", "httpx", "http", "openai", "anthropic",
    "ollama", "transformers", "subprocess", "litellm", "llama_cpp",
    "vllm", "huggingface_hub", "google", "socket",
}
AUTHORIZED_LOCAL_MODULES = {
    "ipseity_local.py",
    "ipseity_integration.py",
    "local_turn_journal.py",
}


def imports(tree: ast.AST) -> set[str]:
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module.split(".")[0])
    return result


def run() -> dict:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))
    scripts = project["project"]["scripts"]
    if scripts.get("doctor-lives-local") != "doctor_lives.ipseity_local:main":
        raise AssertionError("Only audited CLI may be the local protected entrypoint")
    audits = {}
    for file in sorted(PACKAGE.glob("*.py")):
        content = file.read_text("utf-8")
        root = ast.parse(content, filename=str(file))
        found = imports(root) & MODEL_PROVIDER_ROOTS
        if found != RESEARCH_ONLY.get(file.name, set()):
            raise AssertionError(
                f"Unreviewed model/process/network import in {file.name}: "
                f"{sorted(found)}; expected {sorted(RESEARCH_ONLY.get(file.name, set()))}"
            )
        if file.name in AUTHORIZED_LOCAL_MODULES:
            if found:
                raise AssertionError("Production subject modules may not directly access provider")
            audits[file.name] = "no direct network/process imports"
        if "LocalOllamaRenderer" in content and file.name != "ipseity_local.py":
            if file.name != "ipseity_integration.py" or "LocalOllamaRenderer" not in (
                content.split('"""',2)[1]
            ):
                raise AssertionError(
                    "Unreviewed direct production local model call: " + file.name
                )
    local = (PACKAGE / "ipseity_local.py").read_text("utf-8")
    broker = (PACKAGE / "ipseity_integration.py").read_text("utf-8")
    journal = (PACKAGE / "local_turn_journal.py").read_text("utf-8")
    if not all(x in local for x in (
        "LocalOllamaRenderer", "DoctorSyntheticIpseitySession",
        "LocalTurnJournal", "session.deliver_next", "session.pending_count",
    )):
        raise AssertionError("Expected protected local entrypoint flow changed")
    if not all(x in broker for x in (
        "SubjectOnlyRendererPort", "DurableIpseityHost",
        "SubjectRendererCapability.read", "require_drained=True",
    )):
        raise AssertionError("Expected authoritative subject rendering gate changed")
    if not all(x in journal for x in ("BEGIN IMMEDIATE", "message_sha256")):
        raise AssertionError("Expected local-turn concurrency gate changed")
    return {
        "gate": "production-entrypoint-provider-inventory-v1",
        "status": "PASS",
        "package_files_scanned": len(list(PACKAGE.glob("*.py"))),
        "protected_entrypoint": scripts["doctor-lives-local"],
        "research_only_paths": {
            k: sorted(v) for k, v in sorted(RESEARCH_ONLY.items())
        },
        "production_modules": sorted(audits),
        "nonclaim": "Static allowlist only; trusted in-process Python remains capable of bypass.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
