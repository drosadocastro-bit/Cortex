from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_adr_032_documents_bundle_quality_boundary() -> None:
    text = read("docs/ADR-032-review-bundle-quality-integration.md")

    for phrase in [
        "Evidence Quality",
        "missing_quality_boundary",
        "not claim confirmation or source truth",
        "create final reports",
        "alter claim confidence",
        "Quality remains record-condition context for review.",
    ]:
        assert phrase in text


def test_bundle_quality_is_linked_from_core_docs() -> None:
    for path in [
        "README.md",
        "docs/MEMORY_MODEL.md",
        "docs/ARCHITECTURE.md",
        "docs/WORKFLOW_MAP.md",
        "docs/AI_DEBT.md",
        "docs/CURRENT_STATE.md",
    ]:
        text = read(path)
        assert "evidence-quality" in text.casefold() or "Evidence Quality" in text


def test_current_state_no_longer_lists_phase29_as_next() -> None:
    text = read("docs/CURRENT_STATE.md")

    assert "Phase 32" in text
    assert "Review Bundle Quality Integration" not in text


def test_readme_lists_phase29_artifacts() -> None:
    text = read("README.md")

    assert "ADR-032-review-bundle-quality-integration.md" in text
    assert "test_phase29_review_bundle_quality.py" in text

