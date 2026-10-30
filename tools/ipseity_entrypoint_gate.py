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

REVIEWED_OPERATOR_GLOSS = {"local_subject_gloss.py": {"http"}}
# M4/M5 opt-in research adapters are separate from the subject renderer.
REVIEWED_LOCAL_RESEARCH = {"open_inference.py": {"urllib"},
                           "semantic_intentions.py": {"urllib"}}
REVIEWED_LOCAL_TRANSPORT = {"local_ollama_transport.py": {"http"}}

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
        expected = RESEARCH_ONLY.get(file.name, REVIEWED_OPERATOR_GLOSS.get(
            file.name, REVIEWED_LOCAL_RESEARCH.get(file.name,
                REVIEWED_LOCAL_TRANSPORT.get(file.name, set()))))
        if found != expected:
            raise AssertionError(
                f"Unreviewed model/process/network import in {file.name}: "
                f"{sorted(found)}; expected {sorted(expected)}"
            )
        if file.name in REVIEWED_LOCAL_RESEARCH:
            # Existing M4 proposer and M5 embeddings are research-only.
            # Require the literal loopback allowlist and their sole Ollama
            # route, not an arbitrary URL/provider or subject-renderer bypass.
            route = ("/api/generate" if file.name == "open_inference.py"
                     else "/api/embed")
            required = ('url=urlsplit(endpoint)', 'url.scheme!="http"',
                        'url.hostname not in ("localhost","127.0.0.1","::1")',
                        'url.username', 'url.password', 'url.query',
                        'url.fragment', 'url.path.strip("/")', route)
            calls = [n for n in ast.walk(root) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Name)]
            if (not all(part in content for part in required)
                    or sum(n.func.id == "post_local_ollama" for n in calls) != 1
                    or "urlopen(" in content or "Request(" in content):
                raise AssertionError("Unreviewed local research provider route")
            audits[file.name] = "audited loopback-only research adapter, not renderer"
        if file.name in REVIEWED_LOCAL_TRANSPORT:
            calls = [n for n in ast.walk(root) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute)]
            connections = [n for n in calls if n.func.attr == "HTTPConnection"]
            requests = [n for n in calls if n.func.attr == "request"]
            required = ('"::1" if hostname == "::1" else "127.0.0.1"',
                        'route not in ("/api/generate", "/api/embed")',
                        'if response.status != 200:', 'response.read(max_response_bytes + 1)')
            if (len(connections) != 1 or len(requests) != 1
                    or not all(part in content for part in required)
                    or "urlopen(" in content):
                raise AssertionError("Unreviewed local research HTTP transport")
            audits[file.name] = "direct numeric-loopback POST; no proxies or redirects"
        if file.name == "local_subject_gloss.py":
            # Only this operator-only adapter may use a network import, and
            # only for a literal fixed-loopback Ollama POST. This does not
            # authorize an alternative subjective renderer or provider URL.
            calls = [node for node in ast.walk(root)
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
            connections = [node for node in calls if node.func.attr == "HTTPConnection"]
            requests = [node for node in calls if node.func.attr == "request"]
            def literal(node):
                return node.value if isinstance(node, ast.Constant) else None
            if (len(connections) != 1 or len(connections[0].args) < 2
                    or [literal(a) for a in connections[0].args[:2]]
                    != ["127.0.0.1", 11434]
                    or len(requests) != 1 or len(requests[0].args) < 2
                    or [literal(a) for a in requests[0].args[:2]]
                    != ["POST", "/api/generate"]):
                raise AssertionError("Operator gloss must use only fixed-loopback Ollama")
            audits[file.name] = "fixed-loopback operator gloss only; not a subject renderer"
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
