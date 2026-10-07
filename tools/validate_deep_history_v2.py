from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


V1_SHA = "7be60ed46add7c74359b322cc033aa7dfabb08e8"


def small_config(default_config: dict[str, Any]) -> dict[str, Any]:
    cfg = dict(default_config)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
        "seed": 1842,
    })
    return cfg


def create_v1_fixture(repo_root: Path, state_dir: Path) -> None:
    actual = subprocess.check_output(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != V1_SHA:
        raise RuntimeError(f"expected v1 fixture SHA {V1_SHA}, got {actual}")

    sys.path.insert(0, str(repo_root))
    from doctor_lives import Experience, PretoriusBrain
    from doctor_lives.neural import DEFAULT_CONFIG

    brain = PretoriusBrain(state_dir, neural_config=small_config(DEFAULT_CONFIG))
    lived = brain.ingest(Experience(
        "I calibrated the glass pressure apparatus and recorded the stable reading.",
        source="v1_migration_fixture",
        kind="observation",
        novelty=.3,
        tags=("migration_fixture", "lived"),
    ))
    external = brain.ingest(Experience(
        "You remember a childhood insect collection.",
        source="v1_migration_fixture_remote",
        kind="social",
        external=True,
        actor="Remote Claimant",
        social=.4,
        tags=("migration_fixture", "external"),
    ))
    commitment = brain.add_commitment(
        "Recheck the pressure apparatus after restart.",
        actor="self",
        importance=.7,
    )
    brain.save()
    payload = {
        "source_sha": actual,
        "deep_history_version": brain.history_status()["version"],
        "lived_memory_id": lived["memory_id"],
        "external_memory_id": external["memory_id"],
        "commitment_id": commitment,
        "state_digest": brain.store.digest(),
        "tick": brain.store.tick,
    }
    (state_dir / "v1_fixture.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def fresh_v2_validation(output: dict[str, Any]) -> None:
    from doctor_lives import Experience, PretoriusBrain
    from doctor_lives.neural import DEFAULT_CONFIG

    with tempfile.TemporaryDirectory(prefix="pretorius-v2-fresh-") as td:
        state = Path(td)
        brain = PretoriusBrain(state, neural_config=small_config(DEFAULT_CONFIG))
        status = brain.history_status()
        assert status["version"] == "pretorius-deep-history-v2"
        assert status["connectome_nodes"] == 70
        assert status["connectome_edges"] == 243
        assert status["withheld_claims"] == 3
        assert brain.store.meta("schema_version") == "6"
        assert status["source_custody"][0]["custody_status"] == "custody_known"
        assert status["source_custody"][0]["original_author"] is None

        lived = brain.ingest(Experience(
            "I tested a new condenser coil and recorded its resonance.",
            source="fresh_v2_smoke",
            kind="observation",
            novelty=.5,
            actor="Morgan",
            social=.2,
            tags=("fresh_v2_smoke",),
        ))
        commitment_id = brain.add_commitment(
            "Inspect the condenser coil after restart.",
            actor="Morgan",
            importance=.65,
        )
        row = brain.store.get_memory(lived["memory_id"])
        cls = brain.store.classification(lived["memory_id"])
        assert row is not None
        assert row["evidence_class"] == "lived_runtime_memory"
        assert cls is not None
        assert cls["autobiographical_class"] == "lived_runtime_memory"

        digest_before_render = brain.store.digest()
        query = "What does Ingolstadt mean in my history?"
        request = brain.render_request(query).to_dict()
        audit = brain.render_audit_envelope(query).inspect()
        digest_after_render = brain.store.digest()
        assert digest_before_render == digest_after_render
        assert request["schema"] == "the-doctor-lives.render-request.v2"
        assert audit["epistemic_items"]
        assert any(
            item.get("autobiographical_class") == "reconstructed_preawakening_memory"
            for item in audit["epistemic_items"]
        )
        assert any(
            "reconstructed preawakening" in line.lower()
            for line in request["subject_frame"]
        )
        assert "metadata" not in request
        assert "action_tendencies" not in request
        assert "tool_authority" not in repr(request).lower()
        assert "capability_grant" not in repr(request).lower()

        brain.save()
        digest_before_restart = brain.store.digest()
        restarted = PretoriusBrain(state)
        assert restarted.store.digest() == digest_before_restart
        restarted_row = restarted.store.get_memory(lived["memory_id"])
        restarted_cls = restarted.store.classification(lived["memory_id"])
        assert restarted_row is not None
        assert restarted_row["evidence_class"] == "lived_runtime_memory"
        assert restarted_cls is not None
        assert restarted_cls["autobiographical_class"] == "lived_runtime_memory"
        assert commitment_id in {x["id"] for x in restarted.store.open_commitments()}
        assert "Morgan" in {x["display_name"] for x in restarted.store.relationships()}

        with restarted.store.connect() as conn:
            insect_memory_count = conn.execute(
                "SELECT COUNT(*) FROM memories WHERE lower(text) LIKE '%dissected insects in childhood%'"
            ).fetchone()[0]
            dark_refs = conn.execute(
                "SELECT COUNT(*) FROM reference_material WHERE continuity='dark_universe'"
            ).fetchone()[0]
            bad_wording = conn.execute(
                """SELECT COUNT(*) FROM memory_classifications
                WHERE wording NOT IN ('quoted','paraphrased','reconstructed','synthesized')"""
            ).fetchone()[0]
            laundering = conn.execute(
                """SELECT COUNT(*) FROM memories m
                JOIN memory_classifications c ON c.memory_id=m.id
                WHERE c.autobiographical_class IN
                ('reconstructed_preawakening_memory','synthesized_preawakening_memory')
                AND (
                    lower(trim(m.text)) LIKE 'i remember %'
                    OR lower(trim(m.text)) LIKE 'i recall %'
                    OR lower(trim(m.text)) LIKE 'i witnessed %'
                    OR lower(trim(m.text)) LIKE 'i experienced %'
                )"""
            ).fetchone()[0]
        assert int(insect_memory_count) == 0
        assert int(dark_refs) == 0
        assert int(bad_wording) == 0
        assert int(laundering) == 0

        output["fresh_v2"] = {
            "status": "pass",
            "deep_history_version": restarted.history_status()["version"],
            "connectome_nodes": restarted.history_status()["connectome_nodes"],
            "connectome_edges": restarted.history_status()["connectome_edges"],
            "lived_memory_class": restarted_row["evidence_class"],
            "lived_autobiographical_class": restarted_cls["autobiographical_class"],
            "renderer_read_only_digest_preserved": True,
            "restart_digest_preserved": True,
            "commitment_recovered": True,
            "relationship_recovered": True,
            "withheld_insect_claim_not_memory": True,
            "dark_universe_empty": True,
            "schema_version": 6,
            "all_classifications_have_valid_wording": True,
            "reconstructed_or_synthesized_direct_recollection_leaks": 0,
        }


def migrate_v1_validation(v1_root: Path, output: dict[str, Any]) -> None:
    from doctor_lives import PretoriusBrain

    with tempfile.TemporaryDirectory(prefix="pretorius-v1-v2-migration-") as td:
        state = Path(td)
        subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--create-v1-fixture",
                "--v1-root",
                str(v1_root),
                "--state-dir",
                str(state),
            ],
            check=True,
        )
        fixture = json.loads((state / "v1_fixture.json").read_text(encoding="utf-8"))
        assert fixture["source_sha"] == V1_SHA
        assert fixture["deep_history_version"] == "pretorius-deep-history-v1"

        migrated = PretoriusBrain(state)
        status = migrated.history_status()
        assert status["version"] == "pretorius-deep-history-v2"
        assert status["connectome_nodes"] == 70
        assert status["connectome_edges"] == 243

        lived = migrated.store.get_memory(fixture["lived_memory_id"])
        lived_cls = migrated.store.classification(fixture["lived_memory_id"])
        external = migrated.store.get_memory(fixture["external_memory_id"])
        assert lived is not None and lived_cls is not None and external is not None
        assert lived["evidence_class"] == "lived_runtime_memory"
        assert lived_cls["autobiographical_class"] == "lived_runtime_memory"
        assert external["evidence_class"] == "external_statement"
        assert fixture["commitment_id"] in {
            x["id"] for x in migrated.store.open_commitments()
        }
        assert migrated.store.meta("schema_version") == "6"
        assert migrated.store.meta("canonical_evidence_manifest_version") == "1"
        schema_lineage = json.loads(
            migrated.store.meta("state_schema_migrations_json", "[]") or "[]"
        )
        assert schema_lineage
        assert schema_lineage[-1]["from_version"] == 2
        assert schema_lineage[-1]["to_version"] == 6
        schema_snapshot = (
            state / "migration_snapshots"
            / schema_lineage[-1]["pre_migration_snapshot"]
        )
        assert schema_snapshot.is_file()

        with migrated.store.connect() as conn:
            snapshot_count = int(conn.execute(
                """SELECT COUNT(*) FROM archive
                WHERE reason='deep-history-v2 pre-reclassification snapshot'"""
            ).fetchone()[0])
            unclassified_autobio = int(conn.execute(
                """SELECT COUNT(*) FROM memories m
                LEFT JOIN memory_classifications c ON c.memory_id=m.id
                WHERE m.evidence_class IN
                ('canonical_preawakening_memory','reconstructed_preawakening_memory',
                 'synthesized_preawakening_memory','lived_runtime_memory')
                AND c.memory_id IS NULL"""
            ).fetchone()[0])
            legacy_classes = int(conn.execute(
                """SELECT COUNT(*) FROM memories
                WHERE evidence_class LIKE 'inherited_%'
                   OR evidence_class IN ('lived_experience','lived_action_outcome')"""
            ).fetchone()[0])
            invalid_wording = int(conn.execute(
                """SELECT COUNT(*) FROM memory_classifications
                WHERE wording NOT IN ('quoted','paraphrased','reconstructed','synthesized')"""
            ).fetchone()[0])
            migrated_laundering = int(conn.execute(
                """SELECT COUNT(*) FROM memories m
                JOIN memory_classifications c ON c.memory_id=m.id
                WHERE c.autobiographical_class IN
                ('reconstructed_preawakening_memory','synthesized_preawakening_memory')
                AND (
                    lower(trim(m.text)) LIKE 'i remember %'
                    OR lower(trim(m.text)) LIKE 'i recall %'
                    OR lower(trim(m.text)) LIKE 'i witnessed %'
                    OR lower(trim(m.text)) LIKE 'i experienced %'
                )"""
            ).fetchone()[0])
        assert snapshot_count > 0
        assert unclassified_autobio == 0
        assert legacy_classes == 0
        assert invalid_wording == 0
        assert migrated_laundering == 0

        migrated.save()
        digest = migrated.store.digest()
        restarted = PretoriusBrain(state)
        assert restarted.store.digest() == digest
        assert restarted.history_status() == status

        output["v1_to_v2_migration"] = {
            "status": "pass",
            "source_sha": V1_SHA,
            "source_deep_history_version": fixture["deep_history_version"],
            "target_deep_history_version": status["version"],
            "migration_snapshots": snapshot_count,
            "legacy_autobiographical_classes_remaining": legacy_classes,
            "unclassified_autobiographical_memories": unclassified_autobio,
            "lived_memory_migrated_to": lived["evidence_class"],
            "external_statement_preserved": True,
            "commitment_preserved": True,
            "restart_idempotent": True,
            "schema_version": int(restarted.store.meta("schema_version") or 0),
            "schema_migration_from": schema_lineage[-1]["from_version"],
            "schema_migration_to": schema_lineage[-1]["to_version"],
            "schema_snapshot": schema_snapshot.name,
            "canonical_evidence_manifest_version": int(
                restarted.store.meta("canonical_evidence_manifest_version") or 0
            ),
            "invalid_wording_records": invalid_wording,
            "direct_recollection_leaks_after_migration": migrated_laundering,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--create-v1-fixture", action="store_true")
    parser.add_argument("--v1-root", type=Path)
    parser.add_argument("--state-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.create_v1_fixture:
        if not args.v1_root or not args.state_dir:
            raise SystemExit("--create-v1-fixture requires --v1-root and --state-dir")
        create_v1_fixture(args.v1_root.resolve(), args.state_dir.resolve())
        return

    if not args.v1_root or not args.output:
        raise SystemExit("validation requires --v1-root and --output")

    output: dict[str, Any] = {
        "schema": "the-doctor-lives.deep-history-v2-validation.v1",
        "governing_issue": "Azimn/The-Doctor-Lives#4",
    }
    fresh_v2_validation(output)
    migrate_v1_validation(args.v1_root.resolve(), output)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
