from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_adr_031_documents_review_integration_boundary() -> None:
    text = read("docs/ADR-031-evidence-quality-review-integration.md")

    for phrase in [
        "EvidenceQualitySummary",
        "change claim confidence",
        "accept or reject a source",
        "create graph edges",
        "treat `strong_context` as confirmation",
        "Quality is an attention and visibility signal only.",
    ]:
        assert phrase in text


def test_quality_review_integration_is_linked_from_core_docs() -> None:
    for path in [
        "README.md",
        "docs/MEMORY_MODEL.md",
        "docs/WORKFLOW_MAP.md",
        "docs/ARCHITECTURE.md",
        "docs/AI_DEBT.md",
    ]:
        assert "evidence-quality" in read(path).casefold() or "EvidenceQualitySummary" in read(path)


def test_workflow_map_distinguishes_quality_pressure_from_weight() -> None:
    text = read("docs/WORKFLOW_MAP.md")

    assert "Evidence-quality summaries may raise review pressure, not evidentiary weight." in text


def test_readme_lists_phase28_test_and_adr() -> None:
    text = read("README.md")

    assert "ADR-031-evidence-quality-review-integration.md" in text
    assert "test_phase28_quality_review_integration.py" in text
