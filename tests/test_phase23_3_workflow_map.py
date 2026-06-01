from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_workflow_map_documents_main_review_path_and_layer_ownership() -> None:
    text = read("docs/WORKFLOW_MAP.md")

    for phrase in [
        "raw input",
        "candidate claims",
        "claim review dockets",
        "source reliability dockets",
        "working memory",
        "review session",
        "audit trail",
        "review bundle",
        "synthetic demo",
        "Cognitive core",
        "Review workflow",
        "Session and audit",
        "Export and demo",
        "Evaluation and adversarial testing",
    ]:
        assert phrase in text


def test_workflow_map_names_review_modules_and_their_boundaries() -> None:
    text = read("docs/WORKFLOW_MAP.md")

    for module in [
        "claim_review.py",
        "evidence_docket.py",
        "source_review.py",
        "review_priority.py",
        "working_memory.py",
        "review_session.py",
        "session_audit.py",
        "session_persistence.py",
        "review_bundle.py",
        "review_bundle_formatter.py",
        "review_bundle_guardrails.py",
        "demo_workspace.py",
    ]:
        assert module in text

    for boundary in [
        "A docket is a review package, not a decision.",
        "A session decision is a workflow annotation, not a claim update.",
        "An audit event is workflow history, not evidence.",
        "A bundle is a bounded review packet, not a final report.",
        "A demo workspace is an architecture exercise, not validation against reality.",
    ]:
        assert boundary in text


def test_public_docs_point_to_workflow_map() -> None:
    for path in [
        "README.md",
        "docs/ARCHITECTURE.md",
        "docs/MEMORY_MODEL.md",
        "docs/PUBLIC_API.md",
    ]:
        assert "WORKFLOW_MAP.md" in read(path)
