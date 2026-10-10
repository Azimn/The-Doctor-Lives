"""Matched PretoriusBrain clone validation without modifying production execution.

The main repository regression suite runs one exploratory probe. The
standalone audit workflow runs the entire fixed set and captures the trace.
"""
from __future__ import annotations

import unittest

from research_prototypes.ritual_interface.run_cloned_state_causal import (
    run_cloned_state_experiment,
)


class ClonedStateCausalTests(unittest.TestCase):
    def test_real_brain_clones_share_start_and_neural_checkpoint(self):
        result = run_cloned_state_experiment(
            ("Henry Frankenstein requests a review of the experiment.",),
            include_contradiction=True,
        )
        self.assertEqual(result["schema"], "scc-self-binding-causal-clones-v1")
        self.assertEqual(result["summary"]["total_probes"], 2)
        self.assertEqual(result["summary"]["total_arms"], 10)
        source = result["source"]
        for probe in result["probes"]:
            self.assertEqual({x["mode"] for x in probe["arms"]},
                             {"off", "low", "normal", "high", "shuffled"})
            for arm in probe["arms"]:
                self.assertEqual(arm["source_store_digest"], source["store"])
                self.assertEqual(arm["source_neural_sha256"], source["neural"])
                self.assertEqual(arm["canonical_manifest"], source["manifest"])
                self.assertEqual(arm["source_state_version"], source["state_version"])
                self.assertEqual(len(arm["retrieval"]), 1)
                self.assertEqual(arm["probe_index"], probe["probe_index"])
            off = next(x for x in probe["arms"] if x["mode"] == "off")
            self.assertTrue(all(
                part["activated"]["total_bonus"] == 0 and part["direct"]["total_bonus"] == 0
                for part in off["retrieval"]
            ))
            if probe["verified_world_contradiction"]:
                self.assertTrue(all(
                    part["activated"]["total_bonus"] == 0 and part["direct"]["total_bonus"] == 0
                    and part["activated"]["contradiction_freeze"]
                    for arm in probe["arms"] for part in arm["retrieval"]
                ))
                self.assertTrue(all(
                    arm["selected_action"] == off["selected_action"]
                    and arm["selected_memory_ids"] == off["selected_memory_ids"]
                    for arm in probe["arms"]
                ))

    def test_run_rejects_bad_experiment_probes(self):
        with self.assertRaises(ValueError):
            run_cloned_state_experiment((), include_contradiction=False)
        with self.assertRaises(ValueError):
            run_cloned_state_experiment(("",), include_contradiction=False)


if __name__ == "__main__":
    unittest.main()
