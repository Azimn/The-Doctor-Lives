"""Swatch Internet Time on engineer surfaces only; UTC owns persistence."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.engineer_time import EngineerTimeCode, engineer_time
from doctor_lives.speech_emission import SpeechEmissionJournal, SpeechSinkAck, digest


class EngineerTimeTests(unittest.TestCase):
    def test_canonical_biel_fixed_utc_plus_one_examples(self):
        samples = [
            ("2026-10-12T23:00:00+00:00", "2026-10-13", "@000"),
            ("2026-10-12T11:00:00+00:00", "2026-10-12", "@500"),
            ("2026-10-12T00:00:00+00:00", "2026-10-12", "@041"),
            ("2026-10-12T22:59:59.999999+00:00", "2026-10-12", "@999"),
            ("2026-10-12T23:00:00.000001+00:00", "2026-10-13", "@000"),
        ]
        for iso, expected_date, beat in samples:
            with self.subTest(iso=iso):
                code = engineer_time(datetime.fromisoformat(iso))
                self.assertEqual((code.bmt_date, code.beat),
                                 (expected_date, beat))
                self.assertTrue(code.utc_iso.endswith("Z"))

    def test_switched_utc_offsets_give_identical_global_beat(self):
        utc = datetime(2026, 10, 12, 14, 30, 50, tzinfo=timezone.utc)
        chicago = utc.astimezone(timezone(timedelta(hours=-5)))
        self.assertEqual(engineer_time(utc), engineer_time(chicago))
        with self.assertRaises(ValueError):
            engineer_time(datetime(2026, 10, 12, 12))
        with self.assertRaises(ValueError):
            engineer_time("2026-10-12")

    def test_receipt_utc_and_bmt_are_identical_across_restart(self):
        fixed = engineer_time(datetime(
            2026, 10, 12, 23, 15, 0, tzinfo=timezone.utc
        ))
        with tempfile.TemporaryDirectory() as td:
            with SpeechEmissionJournal(td) as journal:
                journal.prepare("message-1", "I see the door.",
                                before_tick=7,before_neural_tick=7)
                with patch("doctor_lives.speech_emission.engineer_time",
                           return_value=fixed):
                    receipt = journal.emit_once(
                        "message-1",
                        lambda text, key: SpeechSinkAck(
                            key, "stdout-test", digest(text),
                        ),
                    )
                self.assertEqual(receipt.emitted_beat, "@010")
                self.assertEqual(receipt.emitted_bmt_date, "2026-10-13")
                self.assertEqual(receipt.emitted_utc, fixed.utc_iso)
            with SpeechEmissionJournal(td) as reopened:
                with patch("doctor_lives.speech_emission.engineer_time",
                           side_effect=AssertionError("must not restamp")):
                    repeated = reopened.emit_once("message-1", lambda *_: (
                        self.fail("must not re-emit")
                    ))
                self.assertEqual(repeated, receipt)
                self.assertEqual(reopened._row("message-1")[8], "@010")

    def test_legacy_emission_journal_migrates_without_inventing_old_timestamp(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "speech_emission.sqlite3"
            db = sqlite3.connect(path)
            db.execute(
                "CREATE TABLE emissions (delivery_key TEXT PRIMARY KEY,"
                "content TEXT NOT NULL,content_sha256 TEXT NOT NULL,"
                "state TEXT NOT NULL,sink_id TEXT,before_tick INTEGER NOT NULL,"
                "before_neural_tick INTEGER NOT NULL)"
            )
            db.execute("INSERT INTO emissions VALUES (?,?,?,?,?,?,?)",
                       ("old", "I spoke.", digest("I spoke."),
                        "acknowledged", "stdout", 1, 1))
            db.commit()
            db.close()
            with SpeechEmissionJournal(td) as journal:
                old = journal.emit_once("old", lambda *_: (
                    self.fail("cannot play old speech twice")
                ))
                self.assertIsNone(old.emitted_beat)
                self.assertIsNone(old.emitted_utc)
                self.assertEqual(journal._row("old")[2], "acknowledged")


if __name__ == "__main__":
    unittest.main()
