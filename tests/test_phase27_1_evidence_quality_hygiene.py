from pathlib import Path
import re

from roswell_uap_cortex import (
    EvidenceQualityAssessment,
    EvidenceQualityDimensionScores,
    EvidenceQualityLabel,
    EvidenceQualityWarning,
    EvidenceQualityWarningType,
    PersistenceRecord,
    Serializer,
)


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def sample_assessment() -> EvidenceQualityAssessment:
    return EvidenceQualityAssessment(
        evidence_id="quality-evidence-1",
        dimension_scores=EvidenceQualityDimensionScores(
            provenance_completeness=0.9,
            lineage_clarity=0.8,
            source_transparency=0.7,
            observation_directness=1.0,
            contamination_resistance=0.9,
            contradiction_stability=0.6,
            temporal_specificity=0.8,
            extraction_confidence=0.75,
        ),
        quality_label=EvidenceQualityLabel.REVIEWABLE,
        quality_score=0.79,
        review_priority_score=0.32,
        provenance_ids={"prov-1"},
        lineage_id="line-1",
        reason_codes=["provenance_complete", "source_uri_visible"],
        warnings=[
            EvidenceQualityWarning(
                EvidenceQualityWarningType.QUALITY_NOT_TRUTH,
                "Quality is not truth.",
                {"quality-evidence-1"},
            ),
            EvidenceQualityWarning(
                EvidenceQualityWarningType.REVIEW_SIGNAL_ONLY,
                "Quality is review context only.",
                {"quality-evidence-1"},
            ),
        ],
        notes=["synthetic quality fixture"],
    )


def test_evidence_quality_assessment_serializes_and_round_trips() -> None:
    record = Serializer().serialize_record(sample_assessment())
    restored = Serializer().deserialize_record(record)

    assert record.record_type == "EvidenceQualityAssessment"
    assert restored.evidence_id == "quality-evidence-1"
    assert restored.quality_label is EvidenceQualityLabel.REVIEWABLE
    assert restored.dimension_scores.provenance_completeness == 0.9
    assert restored.provenance_ids == {"prov-1"}
    assert restored.warnings[0].warning_type is EvidenceQualityWarningType.QUALITY_NOT_TRUTH


def test_evidence_quality_unknown_fields_are_preserved_in_metadata_when_safe() -> None:
    record = PersistenceRecord(
        record_type="EvidenceQualityAssessment",
        record_id="quality-evidence-unknown",
        payload={
            "evidence_id": "quality-evidence-unknown",
            "dimension_scores": {
                "provenance_completeness": 0.5,
                "lineage_clarity": 0.5,
            },
            "quality_label": "fragile",
            "quality_score": 0.4,
            "review_priority_score": 0.7,
            "future_field": "preserved",
        },
    )

    restored = Serializer().deserialize_record(record)

    assert restored.evidence_id == "quality-evidence-unknown"
    assert restored.quality_label is EvidenceQualityLabel.FRAGILE
    assert restored.metadata["unknown_fields"] == {"future_field": "preserved"}


def test_evidence_quality_modules_avoid_security_risky_patterns() -> None:
    forbidden = re.compile(
        r"import requests|urllib|httpx|socket|subprocess|eval\(|exec\(|pickle|yaml\.load|os\.system",
        re.IGNORECASE,
    )
    for path in [
        ROOT / "src" / "roswell_uap_cortex" / "evidence_quality.py",
        ROOT / "src" / "roswell_uap_cortex" / "evidence_quality_guardrails.py",
    ]:
        assert not forbidden.search(path.read_text(encoding="utf-8"))


def test_evidence_quality_docs_do_not_frame_quality_as_truth_or_reliability() -> None:
    combined = "\n".join(
        read(path)
        for path in [
            "docs/ADR-030-evidence-quality-rubric.md",
            "docs/AI_DEBT.md",
            "docs/MEMORY_MODEL.md",
            "docs/WORKFLOW_MAP.md",
            "docs/ARCHITECTURE.md",
        ]
    ).casefold()

    forbidden_phrases = [
        "strong_context means true",
        "strong_context means reliable",
        "quality confirms",
        "quality proves",
        "quality validates",
        "quality score is truth",
        "quality score is reliability",
    ]
    assert all(phrase not in combined for phrase in forbidden_phrases)


def test_debugging_security_doc_mentions_evidence_quality_hygiene() -> None:
    text = read("docs/DEBUGGING_AND_SECURITY.md")

    assert "Phase 27 Evidence Quality Check" in text
    assert "quality labels are not truth confidence" in text


def test_phase27_1_hygiene_doc_is_linked_and_bounded() -> None:
    readme = read("README.md")
    doc = read("docs/PHASE_27_1_EVIDENCE_QUALITY_HYGIENE.md")

    assert "PHASE_27_1_EVIDENCE_QUALITY_HYGIENE.md" in readme
    assert "does not add a new reasoning layer" in doc
    assert "Evidence quality remains record-condition context for review." in doc
