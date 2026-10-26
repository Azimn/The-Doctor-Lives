"""Portable simulated worlds must share one Pretorius, not a world-specific mind."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.virtual_world_port import (
    VirtualWorldEnvironmentPort, VirtualWorldReceipt, VirtualWorldSource,
)

LAB_AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return cfg


class TinyVirtualWorld:
    """An actual mutable second simulated world, NOT robot hardware."""

    def __init__(self, world_id="other-world", epoch="session-1"):
        self.world_id = world_id
        self.world_epoch = epoch
        self.location = "observatory"
        self._ledger = {}
        self._requests = {}
        self.transitions = 0

    def _record(self, receipt):
        self._ledger[(receipt.kind, receipt.event_id)] = receipt
        return receipt

    def observe(self):
        if self.location == "observatory":
            text = "I see stars through the glass observatory ceiling."
        else:
            text = "I see sunlight falling across the greenhouse floor."
        return self._ledger.get(("observation", "view-" + self.location)) or self._record(
            VirtualWorldReceipt(
                self.world_id, self.world_epoch,
                "view-" + self.location, "observation", text,
            )
        )

    def act(self, op, *, event_id, **args):
        prior = self._ledger.get(("action", event_id))
        if prior is not None:
            if self._requests[event_id] != (op, tuple(sorted(args.items()))):
                raise RuntimeError("Action event ID used with different request")
            return prior
        if op != "go" or args.get("to") not in ("observatory", "greenhouse"):
            raise PermissionError("World does not permit that action")
        if args["to"] == self.location:
            raise PermissionError("Already at destination")
        self.location = args["to"]
        self.transitions += 1
        self._requests[event_id] = (op, tuple(sorted(args.items())))
        return self._record(VirtualWorldReceipt(
            self.world_id, self.world_epoch, event_id, "action",
            ("I step into the greenhouse." if self.location == "greenhouse"
             else "I return to the observatory."),
            operation="go",
        ))

    def verify_receipt(self, receipt):
        return self._ledger.get((receipt.kind, receipt.event_id)) == receipt


class PortableVirtualWorldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.runtime = SixOrganRuntime.open(
            self.root / "brain", neural_config=small_config()
        )
        self.world = TinyVirtualWorld()

    def test_real_world_actions_first_person_memory_and_idempotent_restart(self):
        with self.assertRaises(PermissionError):
            VirtualWorldEnvironmentPort(self.runtime, self.world)
        provider = VirtualWorldEnvironmentPort(
            self.runtime, self.world, authorized=True,
        )
        self.assertIsInstance(self.world, VirtualWorldSource)
        entered = provider.observe()
        self.assertEqual(entered.status, "admitted")
        self.assertEqual(entered.first_person,
                         "I see stars through the glass observatory ceiling.")
        moved = provider.act("go", event_id="door-1", to="greenhouse")
        self.assertEqual(moved.status, "admitted")
        self.assertEqual(self.world.location, "greenhouse")
        arrived = provider.observe()
        self.assertEqual(arrived.status, "admitted")
        self.assertEqual(entered.source_kind, "other-world")
        self.assertEqual(self.world.transitions, 1)
        for entry in (entered, moved, arrived):
            memory = self.runtime._port.brain.store.get_memory(entry.memory_id)
            self.assertEqual(memory["text"], entry.first_person)
            self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
            for forbidden in ("world_epoch", "session-1", "door-1", "other-world"):
                self.assertNotIn(forbidden, memory["text"])
        self.runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "brain")
        other_port = VirtualWorldEnvironmentPort(
            reopened, self.world, authorized=True,
        )
        tick = reopened._port.brain.store.tick
        replay = other_port.act("go", event_id="door-1", to="greenhouse")
        self.assertEqual(replay.status, "already_admitted")
        self.assertEqual(replay.memory_id, moved.memory_id)
        self.assertEqual(reopened._port.brain.store.tick, tick)
        self.assertEqual(self.world.transitions, 1)
        self.assertEqual(other_port.observe().status, "already_admitted")

    def test_two_worlds_are_isolated_by_world_and_epoch_source_namespaces(self):
        a = VirtualWorldEnvironmentPort(self.runtime, self.world, authorized=True)
        first = a.observe()
        other = TinyVirtualWorld(world_id="island", epoch="session-1")
        second = VirtualWorldEnvironmentPort(
            self.runtime, other, authorized=True,
        ).observe()
        self.assertNotEqual(first.memory_id, second.memory_id)
        self.assertEqual(first.first_person, second.first_person)
        with self.runtime._port.brain.store.connect() as conn:
            sources = {
                x["source"] for x in conn.execute(
                    "SELECT source FROM memories WHERE id IN (?, ?)",
                    (first.memory_id, second.memory_id),
                )
            }
        self.assertEqual(len(sources), 2)
        self.assertTrue(any("other-world" in x for x in sources))
        self.assertTrue(any("island" in x for x in sources))
        # Neither world can mutate the other's physical state.
        VirtualWorldEnvironmentPort(
            self.runtime, other, authorized=True,
        ).act("go", event_id="door-1", to="greenhouse")
        self.assertEqual(other.location, "greenhouse")
        self.assertEqual(self.world.location, "observatory")

    def test_reject_forged_receipt_and_deny_nonexistent_actions_without_memory(self):
        provider = VirtualWorldEnvironmentPort(
            self.runtime, self.world, authorized=True,
        )
        baseline = self.runtime._port.brain.store.digest()
        with self.assertRaises(PermissionError):
            provider.act("teleport", event_id="fake-event", to="moon")
        self.assertEqual(self.runtime._port.brain.store.digest(), baseline)
        forged = VirtualWorldReceipt(
            "other-world", "session-1", "forged", "observation",
            "I see a golden treasure beside me.",
        )
        with self.assertRaises(PermissionError):
            provider._admit(forged, kind="observation")
        with self.assertRaises(PermissionError):
            provider._admit(
                VirtualWorldReceipt(
                    "other-world", "wrong-epoch", "view-observatory",
                    "observation", "I see stars through the glass observatory ceiling.",
                ),
                kind="observation",
            )
        self.assertEqual(self.runtime._port.brain.store.digest(), baseline)

    def test_action_replay_with_changed_intent_is_rejected(self):
        provider = VirtualWorldEnvironmentPort(
            self.runtime, self.world, authorized=True,
        )
        original = provider.act("go", event_id="door-1", to="greenhouse")
        with self.assertRaises(RuntimeError):
            provider.act("go", event_id="door-1", to="observatory")
        self.assertEqual(self.world.transitions, 1)
        self.assertEqual(
            self.runtime._port.brain.store.get_memory(original.memory_id)["text"],
            original.first_person,
        )


@unittest.skipUnless(LAB_AVAILABLE, "Pinned real Laboratory dependency required")
class LabToVirtualWorldTransitionTests(unittest.TestCase):
    def test_lab_to_another_live_simulated_world_and_back_preserves_one_identity(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from doctor_lives.environment_port import LaboratoryEnvironmentPort

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = SixOrganRuntime.open(
                root / "brain", neural_config=small_config()
            )
            habitat = SpatialHabitat.create(root / "lab.sqlite3")
            HomeLife(habitat).initialize()
            DailyRhythm(habitat).initialize()
            lab = LaboratoryEnvironmentPort(
                runtime, SubjectPort(habitat), authorized=True
            )
            before = lab.observe()
            other_world = TinyVirtualWorld("alternate-sim")
            alternate = VirtualWorldEnvironmentPort(
                runtime, other_world, authorized=True,
            )
            after = alternate.observe()
            moved = alternate.act("go", event_id="switchroom", to="greenhouse")
            self.assertEqual(other_world.location, "greenhouse")
            again_lab = lab.observe()
            self.assertEqual(again_lab.status, "already_admitted")
            self.assertEqual(before.memory_id, again_lab.memory_id)
            self.assertNotEqual(before.memory_id, after.memory_id)
            self.assertNotEqual(after.memory_id, moved.memory_id)
            runtime.checkpoint()
            new = SixOrganRuntime.open(root / "brain")
            ids = {m["id"] for m in new._port.brain.store.memories(False)}
            self.assertTrue({before.memory_id, after.memory_id, moved.memory_id}.issubset(ids))
            self.assertIs(runtime._port, lab._bridge.doctor)
            self.assertFalse((root / "brain" / "other_brain.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
