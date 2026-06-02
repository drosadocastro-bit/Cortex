from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_api_and_model_map_documents_layer_ownership_without_refactor() -> None:
    text = read("docs/API_AND_MODEL_MAP.md")

    for phrase in [
        "does not change package structure",
        "Cognitive core",
        "Ingestion and provenance",
        "Claim pipeline",
        "Review workflow",
        "Presentation contract",
        "Evaluation and adversarial",
        "Do not split `models.py`",
        "Deferred larger refactors",
        "This is a sketch, not a migration plan.",
    ]:
        assert phrase in text


def test_api_and_model_map_is_linked_from_public_docs() -> None:
    for path in [
        "README.md",
        "docs/PUBLIC_API.md",
        "docs/WORKFLOW_MAP.md",
        "docs/PHASE_25_2_CONSOLIDATION.md",
    ]:
        assert "API_AND_MODEL_MAP.md" in read(path)


def test_public_api_map_discourages_premature_export_and_namespace_churn() -> None:
    text = read("docs/API_AND_MODEL_MAP.md")

    assert "avoid exporting brand-new helpers unless they are part of the canonical path" in text
    assert "reducing `__init__.py` exports" in text
    assert "prefer clearer maps over file movement" in text
