from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_review_reasoning_boundary_documents_typed_influence_summary() -> None:
    text = read("docs/REVIEW_REASONING_BOUNDARY.md")

    for field_name in [
        "signals",
        "prioritized_ids",
        "must_include_ids",
        "deferred_ids",
        "unresolved_ids",
        "provenance_gap_ids",
        "source_review_warning_ids",
        "contradiction_ids",
        "uncertainty_notes",
        "discourse_annotations",
        "warnings",
    ]:
        assert f"`{field_name}`" in text

    assert "review influence can affect inclusion and ordering, not evidentiary weighting" in text


def test_ai_debt_tracks_review_boundary_watchpoints() -> None:
    text = read("docs/AI_DEBT.md")

    assert "Review-To-Reasoning Boundary Debt" in text
    assert "ContextWindowBuilder" in text
    assert "inclusion and ordering, not evidentiary weighting" in text
    assert "`README.md` is becoming a capability ledger" in text
