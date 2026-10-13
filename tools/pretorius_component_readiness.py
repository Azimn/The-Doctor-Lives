"""Nonmutating Doctor Lives component installation and wiring audit.

This is an engineer preflight, NOT a three-organ runtime. Importability,
repository integration and live activation are separate properties. The
preflight never instantiates Pretorius, creates a BrainStore, invokes a model,
or changes any cognitive, Sensus or Ipseity data.
"""
from __future__ import annotations

import argparse
import ast
import importlib
from importlib import metadata, util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_IPSEITY_VERSION = "0.9.11"
REQUIRED_SENSUS_SCHEMA = "sensus.scene.v0.1"


def _probe_module(module_name: str, required: tuple[str, ...]) -> dict[str, Any]:
    """An explicitly invoked local package check; no model operations."""
    try:
        spec = util.find_spec(module_name)
        if spec is None:
            return {"importable": False, "api_complete": False,
                    "reason": "module_not_found"}
        module = importlib.import_module(module_name)
        missing = [attr for attr in required if not hasattr(module, attr)]
        return {"importable": True, "api_complete": not missing,
                "reason": "ok" if not missing else "missing_expected_api",
                "missing_attributes": missing}
    except (ImportError, OSError, RuntimeError, ValueError, TypeError) as exc:
        return {"importable": False, "api_complete": False,
                "reason": "import_error:" + type(exc).__name__}


def audit(root: Path = ROOT) -> dict[str, Any]:
    package = root / "doctor_lives"
    local_cli = package / "ipseity_local.py"
    bridge = package / "ipseity_integration.py"
    policy = package / "cognition.py"
    if not (local_cli.is_file() and bridge.is_file() and policy.is_file()):
        raise FileNotFoundError("Expected installed Doctor Lives package source is missing")

    # Static, versioned source inspection, NOT a proof of no model bypasses.
    cli_text = local_cli.read_text(encoding="utf-8")
    bridge_text = bridge.read_text(encoding="utf-8")
    policy_ast = ast.parse(policy.read_text(encoding="utf-8"))
    policies = [
        node for node in ast.walk(policy_ast)
        if isinstance(node, ast.ClassDef) and node.name == "PretoriusBrain"
    ]
    has_research_recall = bool(policies) and any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "research_endogenous_recall"
        for node in policies[0].body
    )
    ipseity_path_in_source = (
        "DoctorSyntheticIpseitySession" in cli_text
        and "session.deliver_next" in cli_text
        and "SubjectOnlyRendererPort" in bridge_text
        and "require_drained=True" in bridge_text
    )
    ip = _probe_module(
        "synthetic_ipseity",
        ("Kind", "DurableIpseityHost", "SubjectOnlyRendererPort",
         "LocalOllamaRenderer"),
    )
    try:
        version = metadata.version("synthetic-ipseity")
    except metadata.PackageNotFoundError:
        version = None
    ip["distribution_version"] = version
    ip["required_version"] = REQUIRED_IPSEITY_VERSION
    ip["donor_compatible"] = False
    if ip["api_complete"] and version == REQUIRED_IPSEITY_VERSION:
        try:
            from synthetic_ipseity import Kind
            ip["donor_compatible"] = hasattr(Kind, "PROJECTED_SUBJECT_EVENT")
        except ImportError:
            ip["donor_compatible"] = False
    ip["doctor_integration_code_present"] = bool(ipseity_path_in_source)
    ip["supported_cli_uses_gate_when_installed"] = bool(
        ipseity_path_in_source and ip["donor_compatible"]
    )
    ip["globally_enforced"] = False  # Not a hostile-Python sandbox.

    se = _probe_module(
        "sensus_artificialis", ("Sensus", "Percept", "Evidence", "Scene"),
    )
    se["schema_compatible"] = False
    se["affectus_importable"] = False
    if se["api_complete"]:
        try:
            pkg = importlib.import_module("sensus_artificialis")
            se["schema_compatible"] = (
                pkg.SCHEMA_VERSION == REQUIRED_SENSUS_SCHEMA
            )
            se["affectus_importable"] = (
                util.find_spec("sensus_artificialis.affectus") is not None
            )
        except (ImportError, AttributeError, ValueError):
            pass
    se["doctor_runtime_wired"] = False
    se["adoption_gate"] = (
        "No cross-project rewiring before the 2026-10-23 blind-ablation "
        "window ends; later adoption still requires independent review."
    )

    en = {
        "research_method_present_in_installed_code": bool(has_research_recall),
        "research_pr": "Azimn/The-Doctor-Lives#57",
        "doctor_runtime_wired": False,
        "production_approved": False,
        "research_result": "13/18 vs strong gap rule 14/18; advantage unproven",
    }
    staged_components_available = bool(
        ip["donor_compatible"] and ipseity_path_in_source
        and se["schema_compatible"] and has_research_recall
    )
    return {
        "schema": "the-doctor-lives.component-readiness.v1",
        "mode": "nonmutating_local_inspection",
        "synthetic_ipseity": ip,
        "sensus_communis_artificialis": se,
        "endogenous_recall": en,
        "all_three_importable_or_present": staged_components_available,
        "all_three_active_in_production": False,
        "nonclaims": [
            "An importable component is not necessarily wired or active.",
            "An upstream GitHub merge does not install a package on this machine.",
            "No first-person Sensus admission or autonomous recall is demonstrated.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-staging-components", action="store_true",
        help="Exit nonzero unless all three are locally importable/present; "
             "never implies safe production activation.",
    )
    parser.add_argument(
        "--require-production", action="store_true",
        help="Fail closed until all three are truly live (not yet authorized).",
    )
    args = parser.parse_args(argv)
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_staging_components and not result["all_three_importable_or_present"]:
        return 2
    if args.require_production and not result["all_three_active_in_production"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
