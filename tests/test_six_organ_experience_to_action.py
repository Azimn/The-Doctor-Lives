"""Real Laboratory experience-to-work-action tests; no production defaults altered."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import sys

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.experience_to_action import (
    execute_bench_action, propose_bench_action,
)
from doctor_lives.neural import DEFAULT_CONFIG

LAB_AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None
_PAGE = (
    "When my instruments look worn, I should repair the apparatus "
    "before I experiment."
)


def brain_config():
    c = dict(DEFAULT_CONFIG)
    c.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return c



# This fixture is executed by a fresh interpreter. os._exit deliberately
# bypasses Python cleanup, simulating process loss at either commit boundary.
# The original Laboratory and original BrainStore are reopened from disk.
_COLD_CRASH_CHILD = r'''
import json
import os
from pathlib import Path
import sys

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.subject_port import SubjectPort

world_path, brain_path, intent_path, mode = sys.argv[1:]
intent = json.loads(Path(intent_path).read_text(encoding="utf-8"))
assert set(intent) == {"event_id", "op"} and intent["op"] == "repair"
event_id = intent["event_id"]
world = SpatialHabitat(world_path)
subject = SubjectPort(world)
doctor = PretoriusBrainPort(brain_path)
bridge = DoctorHomeBridge(doctor, subject, authorized=True)

def receipt():
    with world._open() as db:
        row = db.execute(
            "SELECT event_hash FROM rhythm_events WHERE event_id=?",
            (event_id,),
        ).fetchone()
    assert row is not None, "No durable Laboratory action receipt"
    return "laboratory-home:action:" + row[0]

if mode in ("world_commit", "brain_commit"):
    original = bridge._admit_verified
    def interrupt(frame, source, **kwargs):
        assert source == receipt(), "Wrong physical receipt at crash boundary"
        if mode == "world_commit":
            os._exit(73)
        admitted = original(frame, source, **kwargs)
        assert admitted["status"] == "admitted"
        assert sum(m["source"] == source
                   for m in doctor.brain.store.memories(False)) == 1
        os._exit(74)
    bridge._admit_verified = interrupt
    bridge.act(intent["op"], event_id=event_id)
    raise AssertionError("Crash interception did not execute")
elif mode == "recover":
    outcome = bridge.act(intent["op"], event_id=event_id)
    source = receipt()
    memory = doctor.brain.store.get_memory(outcome["memory_id"])
    assert memory["source"] == source
    assert memory["text"] == outcome["subject"]["inner"]
    assert memory["evidence_class"] == "lived_runtime_memory"
    denied = False
    try:
        bridge.act("experiment", event_id=event_id)
    except RuntimeError:
        denied = True
    assert denied, "Conflicting replay unexpectedly accepted"
    print(json.dumps({
        "status": outcome["status"], "memory_id": outcome["memory_id"],
        "source": source, "text": memory["text"],
        "conflict_denied": denied,
    }), flush=True)
else:
    raise AssertionError("Unknown child mode")
'''


# Both children open the SAME original brain and world. The winner is killed
# after an independently committed physical receipt, before memory admission.
_RACE_CHILD = r'''
import json
import os
from pathlib import Path
import sys
import time

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.subject_port import SubjectPort

world_path, brain_path, gate_path, op, event_id = sys.argv[1:]
world = SpatialHabitat(world_path)
doctor = PretoriusBrainPort(brain_path)
bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
args = {"station": "station:center"} if op == "walk" else {"minutes": 30}
Path(gate_path + "." + op + ".ready").write_text("ready", encoding="utf-8")
deadline = time.monotonic() + 45
while not Path(gate_path).is_file():
    assert time.monotonic() < deadline, "Start barrier timed out"
    time.sleep(.01)

def die_after_world(frame, source, **kwargs):
    assert source.startswith("laboratory-home:action:")
    with world._open() as db:
        table = "embodied_events" if op == "walk" else "rhythm_events"
        receipt = db.execute(
            "SELECT event_hash FROM " + table + " WHERE event_id=?",
            (event_id,),
        ).fetchone()
    assert receipt and source == "laboratory-home:action:" + receipt[0]
    os._exit(75)

bridge._admit_verified = die_after_world
try:
    bridge.act(op, event_id=event_id, **args)
except RuntimeError as exc:
    print(json.dumps({"status": "denied", "reason": str(exc)}), flush=True)
else:
    raise AssertionError("A successful contender did not hit the crash boundary")
'''

@unittest.skipUnless(LAB_AVAILABLE, "Requires real pinned physical Laboratory")
class VerifiedExperienceToActionTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from pretorius_lab.book_library import BookLibrary

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.port = PretoriusBrainPort(root / "brain", neural_config=brain_config())
        self.subject = SubjectPort(self.world)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        self.books = BookLibrary(self.world)
        self.books.initialize()

    def world_state(self):
        self.subject.verify()
        with self.world._open() as db:
            return json.loads(db.execute(
                "SELECT value FROM rhythm_meta WHERE key='state'"
            ).fetchone()[0])

    def history_count(self, op):
        with self.world._open() as db:
            return db.execute(
                "SELECT count(*) FROM rhythm_events WHERE "
                "json_extract(envelope,'$.op')=?", (op,),
            ).fetchone()[0]

    def walk(self, station, event):
        result = self.bridge.act("walk", event_id=event, station=station)
        self.assertIn(result["status"], ("admitted", "already_admitted"))

    def wear_by_actually_working(self):
        self.walk("station:center", "fixture-to-center")
        self.walk("station:bench", "fixture-to-bench")
        self.assertEqual(self.world_state()["apparatus"], 2)
        wore = self.bridge.act("experiment", event_id="fixture-real-work-wear")
        self.assertEqual(wore["status"], "admitted")
        self.assertEqual(self.world_state()["apparatus"], 1)
        self.assertEqual(self.history_count("experiment"), 1)
        self.walk("station:center", "fixture-from-bench")

    def read_real_page(self, *, book_id="book:001", title="Bench notes", page=_PAGE):
        self.books.install(
            book_id, edition_id="real-manual-" + book_id.split(":")[1],
            title=title, author="Original Laboratory Research Fixture",
            pages=[page], source_class="original_fixture",
            source_reference="Experience-to-action test original authored page",
            event_id="fixture-install-" + book_id.replace(":", "-"),
        )
        if self.subject.embodied.verify()["station"] == "station:threshold":
            self.walk("station:center", "reading-to-center")
        self.walk("station:shelf:3", "reading-to-shelf")
        opened = self.bridge.act(
            "book", event_id="physical-open-" + book_id.replace(":", "-"),
            book_id=book_id, operation="open",
        )
        self.assertEqual(opened["status"], "admitted")
        read = self.bridge.act(
            "book", event_id="physical-read-" + book_id.replace(":", "-"),
            book_id=book_id, operation="read",
        )
        self.assertEqual(read["status"], "admitted")
        memory = self.port.brain.store.get_memory(read["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertIn(page, memory["text"])
        self.walk("station:center", "reading-from-shelf")
        self.walk("station:bench", "reading-to-bench")
        return read["memory_id"]

    def test_lived_read_lesion_restoration_real_action_and_replay(self):
        self.wear_by_actually_working()
        read_id = self.read_real_page()
        before = self.subject.verify()["world_epoch"]
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "repair",
        )
        self.assertEqual(
            propose_bench_action(
                self.bridge, read_memory_id=read_id, memory_enabled=False
            ).action,
            "experiment",
        )
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, read_id, self.port.brain.store.tick,
                "isolated reversible research memory lesion",
            )
            self.port.brain.store.bump_state_version(db)
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "experiment",
        )
        with self.port.brain.store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (read_id,))
            self.port.brain.store.bump_state_version(db)
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "repair",
        )
        self.assertEqual(self.subject.verify()["world_epoch"], before)
        self.assertEqual(self.world_state()["apparatus"], 1)
        # An equal-information literal rule also recommends repair: TIE.
        self.assertEqual(
            "repair" if self.world_state()["apparatus"] == 1 else "experiment",
            "repair",
        )
        with self.assertRaises(PermissionError):
            execute_bench_action(
                self.bridge, read_memory_id=read_id,
                event_id="learned-repair", expected_action="repair",
            )
        acted = execute_bench_action(
            self.bridge, read_memory_id=read_id, event_id="learned-repair",
            expected_action="repair", authorized_world_action=True,
        )
        self.assertEqual(acted["status"], "admitted")
        self.assertEqual(self.world_state()["apparatus"], 3)
        self.assertEqual(self.history_count("repair"), 1)
        self.assertEqual(self.world_state()["repairs"], 1)
        memory = self.port.brain.store.get_memory(acted["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertIn("replace the worn component", memory["text"])
        retry = self.bridge.act("repair", event_id="learned-repair")
        self.assertEqual(retry["status"], "already_admitted")
        self.assertEqual(retry["memory_id"], acted["memory_id"])
        self.port.save()
        reopened = PretoriusBrainPort(self.port.brain.state_dir)
        restarted = DoctorHomeBridge(reopened, self.subject, authorized=True)
        replay = restarted.act("repair", event_id="learned-repair")
        self.assertEqual(replay["status"], "already_admitted")
        self.assertEqual(self.history_count("repair"), 1)

    def test_different_book_identity_and_page_paraphrase(self):
        self.wear_by_actually_working()
        read_id = self.read_real_page(
            book_id="book:007", title="Practical apparatus maintenance",
            page=("When my instruments look worn, I should repair the "
                  "workbench mechanism before I experiment."),
        )
        proposal = propose_bench_action(self.bridge, read_memory_id=read_id)
        self.assertEqual(proposal.action, "repair")
        self.assertEqual(proposal.origin, "host_bounded_manual_interpreter")
        physical = execute_bench_action(
            self.bridge, read_memory_id=read_id,
            event_id="variant-repair", expected_action="repair",
            authorized_world_action=True,
        )
        self.assertEqual(physical["status"], "admitted")
        self.assertEqual(self.world_state()["repairs"], 1)

    def test_unworn_bench_does_not_trigger_manual(self):
        read_id = self.read_real_page()
        self.assertEqual(self.world_state()["apparatus"], 2)
        proposed = propose_bench_action(self.bridge, read_memory_id=read_id)
        self.assertEqual(proposed.action, "experiment")
        self.assertIsNone(proposed.read_memory_id)
        physical = execute_bench_action(
            self.bridge, read_memory_id=read_id,
            event_id="unworn-experiment", expected_action="experiment",
            authorized_world_action=True,
        )
        self.assertEqual(physical["status"], "admitted")
        self.assertEqual(self.world_state()["experiments"], 1)
        self.assertEqual(self.history_count("repair"), 0)

    def test_secondhand_claim_does_not_count_as_read(self):
        self.wear_by_actually_working()
        report = self.port.ingest({
            "channel": "world",
            "text": "A stranger claims I read a book saying: " + _PAGE,
            "source": "unverified-stranger-manual",
        })
        m = self.port.brain.store.get_memory(report["memory_id"])
        self.assertEqual(m["evidence_class"], "external_statement")
        self.walk("station:bench", "report-to-bench")
        self.assertEqual(
            propose_bench_action(
                self.bridge, read_memory_id=report["memory_id"]
            ).action,
            "experiment",
        )
        with self.assertRaises(RuntimeError):
            execute_bench_action(
                self.bridge, read_memory_id=report["memory_id"],
                event_id="false-repair", expected_action="repair",
                authorized_world_action=True,
            )
        self.assertEqual(self.history_count("repair"), 0)



    def _assert_cold_process_recovery(self, *, boundary, exit_code):
        """Force process death, reopen both persisted authorities, and replay.

        The durable intent file is the host's action-identity recovery source.
        Without that record a host cannot safely infer which action to replay.
        This test does not claim to solve missing-intent recovery.
        """
        self.wear_by_actually_working()
        read_id = self.read_real_page()
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "repair",
        )
        self.port.save()
        root = Path(self.tmp.name)
        intent_path = root / "pending-action.json"
        with intent_path.open("w", encoding="utf-8") as handle:
            json.dump({"event_id": "cold-" + boundary, "op": "repair"}, handle)
            handle.flush()
            os.fsync(handle.fileno())
        world_path = root / "world.sqlite3"
        brain_path = root / "brain"

        def run_child(mode):
            return subprocess.run(
                [sys.executable, "-c", _COLD_CRASH_CHILD,
                 str(world_path), str(brain_path), str(intent_path), mode],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=120, check=False,
            )

        crashed = run_child(boundary)
        self.assertEqual(
            crashed.returncode, exit_code,
            f"Child did not die at {boundary}: {crashed.stderr}\n{crashed.stdout}",
        )
        with self.world._open() as db:
            rows = db.execute(
                "SELECT event_hash FROM rhythm_events WHERE event_id=?",
                ("cold-" + boundary,),
            ).fetchall()
        self.assertEqual(len(rows), 1)
        source = "laboratory-home:action:" + rows[0][0]
        self.assertEqual(self.history_count("repair"), 1)
        self.assertEqual(self.world_state()["repairs"], 1)
        self.assertEqual(self.world_state()["apparatus"], 3)

        # This read is a NEW BrainStore object after the child has exited.
        cold_brain = PretoriusBrainPort(brain_path)
        before = [
            m for m in cold_brain.brain.store.memories(False)
            if m["source"] == source
        ]
        self.assertEqual(len(before), 0 if boundary == "world_commit" else 1)

        recovered = run_child("recover")
        self.assertEqual(
            recovered.returncode, 0,
            f"Cold recovery failed: {recovered.stderr}\n{recovered.stdout}",
        )
        result = json.loads(recovered.stdout)
        self.assertEqual(
            result["status"],
            "admitted" if boundary == "world_commit" else "already_admitted",
        )
        self.assertEqual(result["source"], source)
        self.assertEqual(result["text"], "I replace the worn component in my apparatus.")
        self.assertTrue(result["conflict_denied"])

        # Another fresh interpreter must replay the exact identity, not act again.
        repeated = run_child("recover")
        self.assertEqual(
            repeated.returncode, 0,
            f"Cold replay failed: {repeated.stderr}\n{repeated.stdout}",
        )
        replay = json.loads(repeated.stdout)
        self.assertEqual(replay["status"], "already_admitted")
        self.assertEqual(replay["memory_id"], result["memory_id"])
        self.assertEqual(replay["source"], source)
        self.assertEqual(self.history_count("repair"), 1)
        self.assertEqual(self.world_state()["repairs"], 1)
        self.assertEqual(self.history_count("experiment"), 1)
        final_brain = PretoriusBrainPort(brain_path)
        self.assertEqual(sum(
            m["source"] == source for m in final_brain.brain.store.memories(False)
        ), 1)

    def test_cross_domain_event_id_collision_denied_without_side_effect(self):
        """A durable action ID must not execute in a second domain table."""
        first = self.bridge.act(
            "walk", event_id="cross-domain-embodied", station="station:center",
        )
        self.assertEqual(first["status"], "admitted")
        before = self.subject.verify()
        memories_before = len(self.port.brain.store.memories(False))
        with self.assertRaisesRegex(RuntimeError, "another Laboratory action domain"):
            self.bridge.act(
                "advance", event_id="cross-domain-embodied", minutes=30,
            )
        self.assertEqual(self.subject.verify(), before)
        self.assertEqual(len(self.port.brain.store.memories(False)), memories_before)
        with self.world._open() as db:
            self.assertIsNone(db.execute(
                "SELECT event_hash FROM rhythm_events WHERE event_id=?",
                ("cross-domain-embodied",),
            ).fetchone())
        replay = self.bridge.act(
            "walk", event_id="cross-domain-embodied", station="station:center",
        )
        self.assertEqual(replay["status"], "already_admitted")
        self.assertEqual(replay["memory_id"], first["memory_id"])

        rhythm = self.bridge.act(
            "advance", event_id="cross-domain-rhythm", minutes=30,
        )
        self.assertEqual(rhythm["status"], "admitted")
        before = self.subject.verify()
        memories_before = len(self.port.brain.store.memories(False))
        with self.assertRaisesRegex(RuntimeError, "another Laboratory action domain"):
            self.bridge.act(
                "walk", event_id="cross-domain-rhythm", station="station:bench",
            )
        self.assertEqual(self.subject.verify(), before)
        self.assertEqual(len(self.port.brain.store.memories(False)), memories_before)
        with self.world._open() as db:
            self.assertIsNone(db.execute(
                "SELECT event_hash FROM embodied_events WHERE event_id=?",
                ("cross-domain-rhythm",),
            ).fetchone())
        replay = self.bridge.act(
            "advance", event_id="cross-domain-rhythm", minutes=30,
        )
        self.assertEqual(replay["status"], "already_admitted")
        self.assertEqual(replay["memory_id"], rhythm["memory_id"])

    def test_two_process_same_id_cross_domain_race_and_cold_recovery(self):
        """R5: one killed winner, one denied rival, one recovered lived action."""
        import time
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort

        root = Path(self.tmp.name)
        event_id = "racing-cross-domain-intent"
        gate = root / "race-start"
        world_path = root / "world.sqlite3"
        brain_path = root / "brain"
        processes = []
        try:
            for op in ("walk", "advance"):
                processes.append((
                    op,
                    subprocess.Popen(
                        [sys.executable, "-c", _RACE_CHILD,
                         str(world_path), str(brain_path), str(gate), op,
                         event_id],
                        cwd=Path(__file__).resolve().parents[1],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True,
                    ),
                ))
            deadline = time.monotonic() + 45
            while not all(
                Path(str(gate) + "." + op + ".ready").exists()
                for op, _ in processes
            ):
                self.assertLess(time.monotonic(), deadline, "Race children not ready")
                self.assertTrue(all(p.poll() is None for _, p in processes))
                time.sleep(.02)
            gate.write_text("go", encoding="utf-8")
            outcomes = [(op, p.returncode, out, err)
                        for op, p in processes
                        for out, err in [p.communicate(timeout=120)]]
        finally:
            for _, p in processes:
                if p.poll() is None:
                    p.kill()
                    p.communicate(timeout=10)

        killed = [op for op, code, _, _ in outcomes if code == 75]
        denied = [(op, json.loads(out)) for op, code, out, _ in outcomes
                  if code == 0]
        self.assertEqual(len(killed), 1, outcomes)
        self.assertEqual(len(denied), 1, outcomes)
        self.assertEqual(denied[0][1]["status"], "denied")
        self.assertIn("already reserved", denied[0][1]["reason"])

        with self.world._open() as db:
            receipts = [
                (table, row[0])
                for table in ("embodied_events", "rhythm_events")
                for row in db.execute(
                    "SELECT event_hash FROM " + table + " WHERE event_id=?",
                    (event_id,),
                ).fetchall()
            ]
        self.assertEqual(len(receipts), 1)
        self.assertEqual(
            receipts[0][0],
            "embodied_events" if killed[0] == "walk" else "rhythm_events",
        )
        source = "laboratory-home:action:" + receipts[0][1]
        cold = PretoriusBrainPort(brain_path)
        self.assertFalse(any(
            m["source"] == source for m in cold.brain.store.memories(False)
        ))
        resumed = DoctorHomeBridge(
            cold, SubjectPort(SpatialHabitat(world_path)), authorized=True,
        )
        pending = resumed.pending_action_intents()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["event_id"], event_id)
        self.assertEqual(pending[0]["op"], killed[0])
        recovered = resumed.recover_pending_actions()
        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0]["status"], "admitted")
        self.assertEqual(resumed.pending_action_intents(), ())
        memory = cold.brain.store.get_memory(recovered[0]["memory_id"])
        self.assertEqual(memory["source"], source)
        self.assertEqual(memory["text"], recovered[0]["subject"]["inner"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertEqual(sum(
            m["source"] == source for m in cold.brain.store.memories(False)
        ), 1)
        with self.assertRaises(RuntimeError):
            loser = "advance" if killed[0] == "walk" else "walk"
            loser_args = ({"minutes": 30} if loser == "advance"
                          else {"station": "station:center"})
            resumed.act(loser, event_id=event_id, **loser_args)
        replay = resumed.act(
            killed[0], event_id=event_id, **pending[0]["args"],
        )
        self.assertEqual(replay["status"], "already_admitted")
        self.assertEqual(replay["memory_id"], recovered[0]["memory_id"])
        with self.world._open() as db:
            self.assertEqual(sum(
                db.execute(
                    "SELECT COUNT(*) FROM " + table + " WHERE event_id=?",
                    (event_id,),
                ).fetchone()[0]
                for table in ("embodied_events", "rhythm_events")
            ), 1)

    def test_cold_process_exit_after_world_before_brain_recovery(self):
        self._assert_cold_process_recovery(
            boundary="world_commit", exit_code=73,
        )

    def test_cold_process_exit_after_brain_before_host_ack_recovery(self):
        self._assert_cold_process_recovery(
            boundary="brain_commit", exit_code=74,
        )

    def test_crash_after_real_repair_world_commit_recovers_exactly_once(self):
        """R5: an interrupted physical repair must not be lost or duplicated.

        This deliberately kills Doctor admission AFTER the authoritative
        Laboratory has committed the repair. Reopening the original BrainStore
        must recover that exact first-person receipt, not synthesize an event.
        """
        from unittest.mock import patch

        self.wear_by_actually_working()
        read_id = self.read_real_page()
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "repair",
        )
        original_admit = self.bridge._admit_verified

        def crash_only_after_world(frame, source, **kwargs):
            if source.startswith("laboratory-home:action:"):
                raise RuntimeError("injected crash after world commit")
            return original_admit(frame, source, **kwargs)

        with patch.object(
            self.bridge, "_admit_verified", side_effect=crash_only_after_world,
        ):
            with self.assertRaisesRegex(
                RuntimeError, "injected crash after world commit",
            ):
                execute_bench_action(
                    self.bridge, read_memory_id=read_id,
                    event_id="crash-repair", expected_action="repair",
                    authorized_world_action=True,
                )

        self.assertEqual(self.history_count("repair"), 1)
        self.assertEqual(self.world_state()["apparatus"], 3)
        self.assertEqual(self.world_state()["repairs"], 1)
        with self.world._open() as db:
            row = db.execute(
                "SELECT event_hash FROM rhythm_events WHERE event_id=?",
                ("crash-repair",),
            ).fetchone()
        self.assertIsNotNone(row)
        source = "laboratory-home:action:" + row[0]
        self.assertFalse(any(
            m["source"] == source
            for m in self.port.brain.store.memories(False)
        ))

        # New process-equivalent objects, original world and original brain.
        reopened = PretoriusBrainPort(self.port.brain.state_dir)
        restarted = DoctorHomeBridge(reopened, self.subject, authorized=True)
        recovered = restarted.act("repair", event_id="crash-repair")
        self.assertEqual(recovered["status"], "admitted")
        memory = reopened.brain.store.get_memory(recovered["memory_id"])
        self.assertEqual(memory["source"], source)
        self.assertEqual(memory["text"], recovered["subject"]["inner"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")

        replay = restarted.act("repair", event_id="crash-repair")
        self.assertEqual(replay["status"], "already_admitted")
        self.assertEqual(replay["memory_id"], recovered["memory_id"])
        self.assertEqual(self.history_count("repair"), 1)
        self.assertEqual(self.world_state()["repairs"], 1)
        self.assertEqual(sum(
            m["source"] == source
            for m in reopened.brain.store.memories(False)
        ), 1)

        # A different requested action cannot launder the prior world receipt.
        with self.assertRaises(RuntimeError):
            restarted.act("experiment", event_id="crash-repair")
        self.assertEqual(self.history_count("experiment"), 1)
        self.assertEqual(self.history_count("repair"), 1)


if __name__ == "__main__":
    unittest.main()
