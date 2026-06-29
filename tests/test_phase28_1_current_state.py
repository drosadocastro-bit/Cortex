from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_current_state_documents_reorientation_snapshot() -> None:
    text = read("docs/CURRENT_STATE.md")

    for phrase in [
        "Last verified: 2026-06-29",
        "`453 passed` after Phase 33 predictive-memory updates",
        "evidence quality assessment",
        "evidence-quality-aware review packaging",
        "Cortex still does not",
        "does not decide truth",
        "Phase 34: Hard-Adversarial Remediation Or Predictive-Memory Boundary Evaluation",
        "Phase 33 added predictive memory as an expectation layer for review attention only.",
    ]:
        assert phrase in text


def test_current_state_preserves_boundary_language() -> None:
    text = read("docs/CURRENT_STATE.md")

    for phrase in [
        "not a roadmap, product claim, validation report, or assurance case",
        "Evidence quality must remain record condition, not truth confidence.",
        "Review bundles now preserve evidence-quality summaries",
        "must not convert those improvements into truth",
    ]:
        assert phrase in text


def test_readme_links_current_state() -> None:
    text = read("README.md")

    assert "CURRENT_STATE.md" in text
    assert "reorientation snapshot" in text
