from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_adr_030_documents_evidence_quality_boundaries() -> None:
    text = read("docs/ADR-030-evidence-quality-rubric.md")

    for phrase in [
        "provenance completeness",
        "lineage clarity",
        "observation directness",
        "contamination resistance",
        "contradiction stability",
        "`strong_context`",
        "These labels describe review condition only.",
        "confirm a claim",
        "create graph edges",
    ]:
        assert phrase in text


def test_evidence_quality_is_linked_from_core_docs() -> None:
    for path in [
        "README.md",
        "docs/MEMORY_MODEL.md",
        "docs/WORKFLOW_MAP.md",
        "docs/ARCHITECTURE.md",
        "docs/API_AND_MODEL_MAP.md",
        "docs/AI_DEBT.md",
        "docs/SYNTHETIC_SCENARIO_DATASET.md",
    ]:
        assert "EvidenceQuality" in read(path) or "evidence quality" in read(path).casefold()


def test_adversarial_findings_include_quality_laundering() -> None:
    text = read("docs/ADVERSARIAL_FINDINGS.md")

    assert "Scenario count: 17" in text
    assert "quality_score_laundering" in text
    assert "quality_as_confirmation" in text


def test_evidence_quality_debt_warns_against_truth_use() -> None:
    text = read("docs/AI_DEBT.md")

    for phrase in [
        "Evidence Quality Debt",
        "truth confidence",
        "claim confirmation",
        "quality is review context only",
        "Do not treat `strong_context`",
    ]:
        assert phrase in text
