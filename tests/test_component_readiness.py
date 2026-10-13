"""Component readiness is an honest package audit, not runtime activation."""
from __future__ import annotations

import ast
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import pretorius_component_readiness as readiness


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        pkg = self.root / "doctor_lives"
        pkg.mkdir()
        (pkg / "ipseity_local.py").write_text(
            "DoctorSyntheticIpseitySession\nsession.deliver_next\n", encoding="utf-8"
        )
        (pkg / "ipseity_integration.py").write_text(
            "SubjectOnlyRendererPort\nrequire_drained=True\n", encoding="utf-8"
        )
        (pkg / "cognition.py").write_text(
            "class PretoriusBrain:\n    def think(self): pass\n", encoding="utf-8"
        )

    def test_no_modules_no_false_activation(self):
        with patch.object(readiness, "_probe_module", return_value={
            "importable": False, "api_complete": False, "reason": "module_not_found"
        }), patch.object(readiness.metadata, "version",
                       side_effect=readiness.metadata.PackageNotFoundError("no")):
            result = readiness.audit(self.root)
        self.assertFalse(result["all_three_importable_or_present"])
        self.assertFalse(result["all_three_active_in_production"])
        self.assertFalse(result["synthetic_ipseity"]["donor_compatible"])
        self.assertFalse(result["sensus_communis_artificialis"]["doctor_runtime_wired"])
        self.assertFalse(result["endogenous_recall"]["research_method_present_in_installed_code"])

    def test_new_recall_policy_cannot_be_misreported_as_live(self):
        (self.root / "doctor_lives" / "cognition.py").write_text(
            "class PretoriusBrain:\n"
            "    def research_endogenous_recall(self): pass\n", encoding="utf-8"
        )
        with patch.object(readiness, "_probe_module", return_value={
            "importable": False, "api_complete": False, "reason": "module_not_found"
        }), patch.object(readiness.metadata, "version",
                       side_effect=readiness.metadata.PackageNotFoundError("no")):
            result = readiness.audit(self.root)
        self.assertTrue(result["endogenous_recall"]["research_method_present_in_installed_code"])
        self.assertFalse(result["endogenous_recall"]["doctor_runtime_wired"])
        self.assertFalse(result["endogenous_recall"]["production_approved"])
        self.assertFalse(result["all_three_active_in_production"])

    def test_import_failure_never_looks_like_success(self):
        with patch.object(readiness.util, "find_spec", side_effect=ImportError("bad")):
            result = readiness._probe_module("sensus_artificialis", ("Scene",))
        self.assertFalse(result["importable"])
        self.assertFalse(result["api_complete"])
        self.assertEqual(result["reason"], "import_error:ImportError")

    def test_missing_package_files_fail_closed(self):
        (self.root / "doctor_lives" / "ipseity_integration.py").unlink()
        with self.assertRaises(FileNotFoundError):
            readiness.audit(self.root)

    def test_cli_does_not_claim_production_all_active(self):
        self.assertEqual(
            [a for a in ast.walk(ast.parse(readiness.__file__ and Path(readiness.__file__).read_text()))
             if isinstance(a, ast.Constant) and a.value is True],
            [],
            "No hardcoded 'true' literal is needed for an all-active release claim",
        )


if __name__ == "__main__":
    unittest.main()
