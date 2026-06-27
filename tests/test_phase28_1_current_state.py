from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_current_state_documents_reorientation_snapshot() -> None:
    text = read("docs/CURRENT_STATE.md")

    for phrase in [
        "Last verified: 2026-06-27",
        "`406 passed` before Phase 30 documentation-only updates",
        "evidence quality assessment",
        "evidence-quality-aware review packaging",
        "Cortex still does not",
        "does not decide truth",
        "Phase 31: Review Bundle Quality Guardrail Expansion Or Hard-Adversarial Remediation",
        "Phase 30 reorganized README navigation and scope grouping.",
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
