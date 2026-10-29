"""No-network integrity and provenance negatives for the offline wheelhouse."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "offline_wheelhouse.py"
spec = importlib.util.spec_from_file_location("offline_wheelhouse", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
DOCTOR = "a" * 40
LAB = "b" * 40


class OfflineWheelhouseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "the_doctor_lives-0.5.0rc2-py3-none-any.whl").write_bytes(b"doctor")
        (self.root / "pretorius_laboratory-0.1.0-py3-none-any.whl").write_bytes(b"lab")
        (self.root / "numpy-2.0.0-py3-none-any.whl").write_bytes(b"dependency")

    def test_seal_verify_and_tampered_wheel(self):
        module.seal(self.root, DOCTOR, LAB)
        self.assertEqual(len(module.verify(self.root, DOCTOR, LAB)["wheels"]), 3)
        with self.assertRaises(ValueError):
            module.verify(self.root, DOCTOR, "c" * 40)
        with self.assertRaises(FileExistsError):
            module.seal(self.root, DOCTOR, LAB)
        (self.root / "numpy-2.0.0-py3-none-any.whl").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            module.verify(self.root, DOCTOR, LAB)

    def test_added_removed_wheels_and_manifest_rehash(self):
        module.seal(self.root, DOCTOR, LAB)
        (self.root / "unlisted-1.0-py3-none-any.whl").write_bytes(b"unlisted")
        with self.assertRaisesRegex(ValueError, "member set mismatch"):
            module.verify(self.root, DOCTOR, LAB)
        (self.root / "unlisted-1.0-py3-none-any.whl").unlink()
        (self.root / "numpy-2.0.0-py3-none-any.whl").unlink()
        with self.assertRaisesRegex(ValueError, "member set mismatch"):
            module.verify(self.root, DOCTOR, LAB)
        path = self.root / module.MANIFEST
        data = json.loads(path.read_text())
        data["doctor_source_sha"] = "c" * 40
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "source commit mismatch"):
            module.verify(self.root, DOCTOR, LAB)

    def test_symlink_and_non_wheel_fail_closed(self):
        module.seal(self.root, DOCTOR, LAB)
        (self.root / "foreign.txt").write_text("unexpected")
        with self.assertRaisesRegex(ValueError, "Unexpected wheelhouse member"):
            module.verify(self.root, DOCTOR, LAB)
        (self.root / "foreign.txt").unlink()
        (self.root / "linked.whl").symlink_to(self.root / "numpy-2.0.0-py3-none-any.whl")
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.verify(self.root, DOCTOR, LAB)

    def test_missing_lab_and_bad_pins(self):
        (self.root / "pretorius_laboratory-0.1.0-py3-none-any.whl").unlink()
        with self.assertRaisesRegex(ValueError, "Required distribution missing"):
            module.seal(self.root, DOCTOR, LAB)
        with self.assertRaisesRegex(ValueError, "exact 40-character"):
            module.seal(self.root, "short", LAB)


if __name__ == "__main__":
    unittest.main()
