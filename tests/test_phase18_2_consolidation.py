from datetime import datetime, timezone
from pathlib import Path
import re

from roswell_uap_cortex import (
    ClaimEvaluationResult,
    ClaimExtractionEngine,
    ClaimEvidenceEvaluator,
    ClaimNormalizer,
    ClaimReviewEngine,
    EvidenceDocketFormatter,
    GraphNode,
    GraphNodeType,
    IngestionNormalizer,
    RawInput,
    RawInputType,
    RelationshipGraphEngine,
    ReviewPriorityEngine,
)


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "roswell_uap_cortex"


def raw(text: str) -> RawInput:
    return RawInput(
        input_id="phase-18-2",
        input_type=RawInputType.NOTE,
        title="Synthetic Consolidation Fixture",
        raw_text=text,
        source_uri="fixture://phase-18-2",
        source_kind="note",
        collected_at=datetime(1947, 7, 8, tzinfo=timezone.utc),
    )


def test_claim_pipeline_boundaries_remain_ordered_and_non_mutating() -> None:
    ingestion = IngestionNormalizer().ingest(raw("The observer saw a bright light moving west."))
    evidence = ingestion.evidence_items[0]
    evidence_metadata_before = dict(evidence.metadata)
    graph = RelationshipGraphEngine()
    graph.add_node(GraphNode(node_type=GraphNodeType.CLAIM, label="claim"))

    extraction = ClaimExtractionEngine().extract(
        ingestion.observations,
        evidence_by_id={item.id: item for item in ingestion.evidence_items},
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
    )
    normalized = ClaimNormalizer().normalize(extraction.candidate_claims).normalized_claims
    evaluation = ClaimEvidenceEvaluator().evaluate(
        normalized,
        ingestion.evidence_items,
        provenance_by_evidence_id={record.evidence_id: record for record in ingestion.provenance_records},
        lineage_by_evidence_id={record.evidence_id: record for record in ingestion.lineage_records},
    )
    docket = ClaimReviewEngine().build_docket(normalized, evaluation)

    assert normalized[0].unsupported
    assert normalized[0].confidence == 0.0
    assert evidence.metadata == evidence_metadata_before
    assert graph.edges == {}
    assert "does not confirm or reject claims" in " ".join(docket.notes)


def test_claim_review_public_api_surface_is_intentional() -> None:
    assert ClaimReviewEngine
    assert EvidenceDocketFormatter
    assert ReviewPriorityEngine
    assert ClaimEvaluationResult


def test_phase_14_to_18_modules_avoid_network_process_and_dynamic_execution_patterns() -> None:
    forbidden = re.compile(
        r"import requests|urllib|httpx|socket|subprocess|eval\(|exec\(|pickle|yaml\.load|os\.system",
        re.IGNORECASE,
    )
    modules = [
        "observation_classifier.py",
        "claim_extraction.py",
        "claim_normalization.py",
        "claim_evaluation.py",
        "claim_contradiction_evaluator.py",
        "claim_review.py",
        "review_priority.py",
        "evidence_docket.py",
    ]

    offenders = [module for module in modules if forbidden.search((SRC / module).read_text(encoding="utf-8"))]

    assert offenders == []


def test_phase_14_to_18_documentation_map_exists() -> None:
    walkthrough = (ROOT / "docs" / "CODE_WALKTHROUGH.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")

    for phrase in [
        "ObservationClassifier",
        "ClaimExtractionEngine",
        "ClaimNormalizer",
        "ClaimEvidenceEvaluator",
        "ClaimReviewEngine",
    ]:
        assert phrase in walkthrough
    assert "claim review dockets / human review queue" in architecture
