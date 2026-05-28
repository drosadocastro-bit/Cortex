from datetime import datetime, timezone
from pathlib import Path

from roswell_uap_cortex import (
    ContaminationFlagType,
    GraphNode,
    GraphNodeType,
    IndependenceScorer,
    IngestionNormalizer,
    LineageType,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
)
from roswell_uap_cortex.independence import EvidenceIndependenceInput


FIXTURES = Path(__file__).parent / "fixtures" / "ingestion"


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def primary_raw() -> RawInput:
    return RawInput(
        input_id="primary-1",
        input_type=RawInputType.DOCUMENT,
        title="Synthetic Primary Document",
        raw_text=fixture_text("primary_document.txt"),
        source_uri="fixture://primary-document",
        source_kind="archival_document",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
        metadata={"author": "records office", "tags": {"synthetic", "primary"}},
    )


def test_raw_input_normalizes_into_ingestion_result() -> None:
    result = IngestionNormalizer().ingest(primary_raw())

    assert result.raw_input_id == "primary-1"
    assert result.observations
    assert result.ingestion_notes == ["deterministic ingestion; no claim confirmation created"]


def test_ingestion_creates_evidence_item_records() -> None:
    result = IngestionNormalizer().ingest(primary_raw())

    assert result.evidence_items
    assert all(item.source_id == "fixture://primary-document" for item in result.evidence_items)
    assert all(item.metadata["raw_input_id"] == "primary-1" for item in result.evidence_items)


def test_provenance_is_attached_to_every_evidence_item() -> None:
    result = IngestionNormalizer().ingest(primary_raw())

    provenance_by_evidence = {
        provenance.evidence_id: provenance for provenance in result.provenance_records
    }
    assert set(provenance_by_evidence) == {item.id for item in result.evidence_items}
    assert all(provenance.source_uri for provenance in result.provenance_records)
    assert all(item.metadata["provenance_id"] for item in result.evidence_items)


def test_missing_source_date_and_title_are_flagged() -> None:
    raw = RawInput(
        input_id="incomplete-1",
        input_type=RawInputType.NOTE,
        title=None,
        raw_text=fixture_text("incomplete_source.txt"),
        source_uri=None,
        source_kind="unknown",
        metadata={"author": "anonymous"},
    )

    result = IngestionNormalizer().ingest(raw)
    flag_types = {flag.flag_type for flag in result.contamination_flags}

    assert ContaminationFlagType.MISSING_SOURCE_URI in flag_types
    assert ContaminationFlagType.MISSING_DATE in flag_types
    assert ContaminationFlagType.MISSING_TITLE in flag_types
    assert set(result.ingestion_warnings) >= {
        "missing_source_uri",
        "missing_date",
        "missing_title",
    }


def test_duplicate_source_uri_is_flagged() -> None:
    normalizer = IngestionNormalizer()
    raw = primary_raw()
    duplicate = RawInput(
        input_id="duplicate-1",
        input_type=RawInputType.NOTE,
        title="Duplicate Synthetic Note",
        raw_text=fixture_text("derivative_repost_note.txt"),
        source_uri=raw.source_uri,
        source_kind="note",
        collected_at=raw.collected_at,
    )

    normalizer.ingest(raw)
    result = normalizer.ingest(duplicate)

    assert ContaminationFlagType.REPEATED_SOURCE_URI in {
        flag.flag_type for flag in result.contamination_flags
    }


def test_derivative_lineage_is_tracked() -> None:
    normalizer = IngestionNormalizer()
    normalizer.ingest(primary_raw())
    derivative = RawInput(
        input_id="derivative-1",
        input_type=RawInputType.NOTE,
        title="Synthetic Repost Note",
        raw_text=fixture_text("derivative_repost_note.txt"),
        source_uri="fixture://repost-note",
        source_kind="repost",
        collected_at=datetime(1947, 7, 9, tzinfo=timezone.utc),
        metadata={"parent_source_id": "fixture://primary-document"},
    )

    result = normalizer.ingest(derivative)

    assert {record.lineage_type for record in result.lineage_records} == {
        LineageType.DERIVATIVE_SOURCE
    }
    assert all(record.parent_source_id == "fixture://primary-document" for record in result.lineage_records)


def test_fictional_contamination_terms_are_flagged() -> None:
    raw = RawInput(
        input_id="contaminated-1",
        input_type=RawInputType.NOTE,
        title="Synthetic Speculative Note",
        raw_text=fixture_text("speculative_contaminated_note.txt"),
        source_uri="fixture://speculative-note",
        source_kind="note",
        collected_at=datetime(1947, 7, 10, tzinfo=timezone.utc),
    )

    result = IngestionNormalizer().ingest(raw)

    assert ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS in {
        flag.flag_type for flag in result.contamination_flags
    }


def test_speculative_language_is_flagged() -> None:
    raw = RawInput(
        input_id="speculative-1",
        input_type=RawInputType.NOTE,
        title="Synthetic Speculative Note",
        raw_text=fixture_text("speculative_contaminated_note.txt"),
        source_uri="fixture://speculative-note",
        source_kind="note",
        collected_at=datetime(1947, 7, 10, tzinfo=timezone.utc),
    )

    result = IngestionNormalizer().ingest(raw)

    assert ContaminationFlagType.SPECULATIVE_LANGUAGE in {
        flag.flag_type for flag in result.contamination_flags
    }


def test_lineage_tracker_assigns_same_lineage_to_derivative_evidence() -> None:
    normalizer = IngestionNormalizer()
    primary = normalizer.ingest(primary_raw())
    derivative = normalizer.ingest(
        RawInput(
            input_id="derivative-2",
            input_type=RawInputType.NOTE,
            title="Synthetic Repost Note",
            raw_text=fixture_text("derivative_repost_note.txt"),
            source_uri="fixture://repost-note-2",
            source_kind="repost",
            collected_at=datetime(1947, 7, 9, tzinfo=timezone.utc),
            metadata={"parent_source_id": "fixture://primary-document"},
        )
    )

    assert derivative.lineage_records[0].lineage_id == primary.lineage_records[0].lineage_id


def test_independence_scorer_can_see_lineage_id_from_ingested_evidence_metadata() -> None:
    normalizer = IngestionNormalizer()
    primary = normalizer.ingest(primary_raw()).evidence_items[0]
    derivative = normalizer.ingest(
        RawInput(
            input_id="derivative-3",
            input_type=RawInputType.NOTE,
            title="Synthetic Repost Note",
            raw_text=fixture_text("derivative_repost_note.txt"),
            source_uri="fixture://repost-note-3",
            source_kind="repost",
            collected_at=datetime(1947, 7, 9, tzinfo=timezone.utc),
            metadata={"parent_source_id": "fixture://primary-document"},
        )
    ).evidence_items[0]

    score = IndependenceScorer().score_pair(
        EvidenceIndependenceInput(
            source_id=primary.source_id,
            lineage_id=primary.metadata["lineage_id"],
        ),
        EvidenceIndependenceInput(
            source_id=derivative.source_id,
            lineage_id=derivative.metadata["lineage_id"],
        ),
    )

    assert score == 0.1


def test_ingestion_does_not_create_claim_confirmations() -> None:
    result = IngestionNormalizer().ingest(primary_raw())

    assert not hasattr(result, "claims")
    assert all("confirmed" not in note for note in result.ingestion_notes)


def test_ingestion_does_not_create_graph_edges_automatically() -> None:
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.EVIDENCE, label="synthetic evidence"))

    IngestionNormalizer().ingest(primary_raw())

    assert graph.edges == {}


def test_all_outputs_are_deterministic() -> None:
    first = IngestionNormalizer().ingest(primary_raw())
    second = IngestionNormalizer().ingest(primary_raw())

    assert [item.id for item in first.evidence_items] == [item.id for item in second.evidence_items]
    assert [item.recorded_at for item in first.evidence_items] == [
        item.recorded_at for item in second.evidence_items
    ]
    assert [record.id for record in first.provenance_records] == [
        record.id for record in second.provenance_records
    ]
    assert [record.lineage_id for record in first.lineage_records] == [
        record.lineage_id for record in second.lineage_records
    ]
