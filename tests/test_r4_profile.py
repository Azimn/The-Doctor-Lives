"""Profile wrappers preserve returns, exceptions and nested accounting."""
import io
import types
import unittest
from unittest.mock import patch

from tools.profile_r4_boundaries import TimingRecorder


class ProfileBoundaryTests(unittest.TestCase):
    def test_nested_exclusive_is_not_double_counted(self):
        p = TimingRecorder(io.StringIO())
        with p.span("operator_auditor", "outer"):
            with p.span("persistence_evidence", "inner"):
                pass
        outer = p.rows[("operator_auditor","outer")][0]
        inner = p.rows[("persistence_evidence","inner")][0]
        self.assertEqual(outer[0], outer[2]+inner[0])

    def test_wrapper_preserves_return_and_exception(self):
        module = types.ModuleType("sample")
        def fn(x):
            if x is None:
                raise ValueError("original")
            return x
        module.fn = fn
        p = TimingRecorder(io.StringIO())
        with patch("tools.profile_r4_boundaries.importlib.import_module", return_value=module):
            restore = p.install("sample", None, "fn", "cognitive_processing", "test")
        marker = object()
        self.assertIs(module.fn(marker), marker)
        with self.assertRaisesRegex(ValueError,"original"):
            module.fn(None)
        restore()
        self.assertIs(module.fn, fn)
        self.assertEqual(len(next(iter(p.rows.values()))), 2)

    def test_flush_emits_zero_model_calls_and_clears_window(self):
        import json
        out = io.StringIO()
        p = TimingRecorder(out)
        with p.span("physical_world","fixture"):
            pass
        p.flush("test")
        row = json.loads(out.getvalue())
        self.assertEqual(row["phases"]["model_inference"]["calls"],0)
        self.assertFalse(row["autonomy_credit"])
        self.assertEqual(p.rows,{})
