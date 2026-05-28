from datetime import datetime, timezone
from pathlib import Path

from roswell_uap_cortex import (
    ActivatedContext,
    Claim,
    Contradiction,
    DiscourseResponse,
    DiscourseSection,
    EvidenceItem,
    GraphNode,
    GraphNodeType,
    MemoryRecord,
    PersistenceRecord,
    PersistenceStore,
    ProvenanceRecord,
    RelationshipGraphEngine,
    SaveResult,
    Serializer,
    SnapshotBuilder,
    SnapshotValidator,
    SourceLineageRecord,
)


LOCAL_TMP = Path("tests/.tmp_persistence")
FIXED_TIME = datetime(2026, 5, 28, 10, 0, tzinfo=timezone.utc)


def local_path(name: str) -> Path:
    LOCAL_TMP.mkdir(exist_ok=True)
    return LOCAL_TMP / name


def sample_evidence() -> EvidenceItem:
    return EvidenceItem(
        id="evidence-1",
        summary="Synthetic persisted evidence",
        source_id="synthetic://source",
        evidence_type="note",
        observed_at=FIXED_TIME,
        recorded_at=FIXED_TIME,
        metadata={"lineage_id": "line-1", "nested": {"a": 1}},
    )


def sample_provenance() -> ProvenanceRecord:
    return ProvenanceRecord(
        evidence_id="evidence-1",
        source_uri="synthetic://source",
        source_kind="synthetic_note",
        ingestion_method="test",
        extraction_method="test",
        original_input_id="input-1",
    )


def sample_lineage() -> SourceLineageRecord:
    return SourceLineageRecord(
        evidence_id="evidence-1",
        source_id="synthetic://source",
        lineage_id="line-1",
        source_uri="synthetic://source",
    )


def sample_discourse() -> DiscourseResponse:
    empty = DiscourseSection(title="empty")
    return DiscourseResponse(
        observed_evidence=DiscourseSection(title="Observed", items=["Observed evidence only."]),
        possible_associations=empty,
        contradictions=empty,
        weak_associations=empty,
        speculative_hypotheses=empty,
        provenance_notes=DiscourseSection(title="Provenance", items=["Provenance visible."]),
        uncertainty_summary=empty,
        missing_information=empty,
    )


def sample_envelope():
    return SnapshotBuilder().build(
        evidence_items=[sample_evidence()],
        claims=[
            Claim(
                id="claim-1",
                text="Synthetic claim",
                evidence_ids={"evidence-1"},
                created_at=FIXED_TIME,
                updated_at=FIXED_TIME,
            )
        ],
        memory_records=[
            MemoryRecord(
                id="memory-1",
                content="Archived synthetic memory",
                archival=True,
                contradiction_pressure=0.4,
                created_at=FIXED_TIME,
                last_accessed_at=FIXED_TIME,
            )
        ],
        graph_nodes=[GraphNode(id="node-1", node_type=GraphNodeType.EVIDENCE, label="Evidence")],
        contradictions=[
            Contradiction(
                id="contradiction-1",
                subject_id="claim-1",
                conflicting_id="claim-2",
                reason="test",
                created_at=FIXED_TIME,
            )
        ],
        provenance_records=[sample_provenance()],
        lineage_records=[sample_lineage()],
        activated_contexts=[ActivatedContext(activated_evidence_ids={"evidence-1"})],
        discourse_responses=[sample_discourse()],
    )


def test_snapshots_save_and_load_deterministically() -> None:
    envelope = sample_envelope()
    path = local_path("snapshot_save_load.json")

    save_result = PersistenceStore().save(envelope, path)
    load_result = PersistenceStore().load(path)

    assert isinstance(save_result, SaveResult)
    assert load_result.success is True
    assert load_result.envelope is not None
    assert load_result.envelope.manifest.metadata.checksum == envelope.manifest.metadata.checksum


def test_identical_content_produces_identical_checksum_hash() -> None:
    first = sample_envelope()
    second = sample_envelope()

    assert first.manifest.metadata.snapshot_id == second.manifest.metadata.snapshot_id
    assert first.manifest.metadata.checksum == second.manifest.metadata.checksum


def test_record_counts_are_correct() -> None:
    envelope = sample_envelope()

    assert envelope.manifest.metadata.record_counts["evidence_items"] == 1
    assert envelope.manifest.metadata.record_counts["claims"] == 1
    assert envelope.manifest.metadata.record_counts["discourse_responses"] == 1


def test_datetime_fields_round_trip_deterministically() -> None:
    record = Serializer().serialize_record(sample_evidence())
    restored = Serializer().deserialize_record(record)

    assert restored.observed_at == datetime(2026, 5, 28, 10, 0, tzinfo=timezone.utc)


def test_metadata_round_trips_without_loss() -> None:
    record = Serializer().serialize_record(sample_evidence())
    restored = Serializer().deserialize_record(record)

    assert restored.metadata["nested"] == {"a": 1}
    assert restored.metadata["lineage_id"] == "line-1"


def test_archived_memories_remain_archived_after_load() -> None:
    path = local_path("snapshot_archived.json")
    PersistenceStore().save(sample_envelope(), path)
    loaded = PersistenceStore().load(path).envelope
    record = loaded.records["memory_records"][0]
    restored = Serializer().deserialize_record(record)

    assert restored.archival is True


def test_contradiction_pressure_is_preserved_after_load() -> None:
    path = local_path("snapshot_pressure.json")
    PersistenceStore().save(sample_envelope(), path)
    record = PersistenceStore().load(path).envelope.records["memory_records"][0]
    restored = Serializer().deserialize_record(record)

    assert restored.contradiction_pressure == 0.4


def test_evidence_provenance_is_preserved_after_load() -> None:
    path = local_path("snapshot_provenance.json")
    PersistenceStore().save(sample_envelope(), path)
    loaded = PersistenceStore().load(path).envelope

    assert loaded.records["provenance_records"][0].payload["evidence_id"] == "evidence-1"


def test_discourse_responses_remain_discourse_records() -> None:
    path = local_path("snapshot_discourse.json")
    PersistenceStore().save(sample_envelope(), path)
    loaded = PersistenceStore().load(path)

    assert loaded.envelope.records["discourse_responses"][0].record_type == "DiscourseResponse"
    assert any("discourse remains discourse" in warning for warning in loaded.warnings)


def test_corrupted_checksum_is_detected() -> None:
    envelope = sample_envelope()
    envelope.manifest.metadata.checksum = "bad"
    result = SnapshotValidator().validate(envelope)

    assert "snapshot checksum mismatch" in result.errors


def test_incompatible_schema_version_is_rejected_or_warned() -> None:
    envelope = sample_envelope()
    envelope.manifest.metadata.schema_version = "future-v999"

    result = SnapshotValidator().validate(envelope)

    assert result.errors == ["incompatible schema version: future-v999"]


def test_unknown_fields_are_preserved_instead_of_silently_dropped() -> None:
    record = PersistenceRecord(
        record_type="EvidenceItem",
        record_id="evidence-unknown",
        payload={
            "id": "evidence-unknown",
            "summary": "Unknown field test",
            "source_id": "synthetic://source",
            "evidence_type": "note",
            "surprise": "preserve me",
        },
    )

    restored = Serializer().deserialize_record(record)

    assert restored.metadata["unknown_fields"] == {"surprise": "preserve me"}


def test_persistence_never_creates_graph_edges_claims_or_evidence_automatically() -> None:
    graph = RelationshipGraphEngine()
    path = local_path("snapshot_no_apply.json")

    PersistenceStore().save(sample_envelope(), path)
    loaded = PersistenceStore().load(path)

    assert graph.edges == {}
    assert len(loaded.envelope.records["claims"]) == 1
    assert len(loaded.envelope.records["evidence_items"]) == 1


def test_save_uses_atomic_write_behavior_where_practical() -> None:
    path = local_path("snapshot_direct_write.json")
    PersistenceStore().save(sample_envelope(), path)

    assert path.exists()
    assert not (LOCAL_TMP / "snapshot_direct_write.json.tmp").exists()
