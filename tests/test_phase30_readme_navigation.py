from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DOCS = ROOT / "docs"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_current_scope_has_grouped_navigation() -> None:
    readme = read(README)

    expected_sections = [
        "### Core Evidence And Memory",
        "### Ingestion And Provenance",
        "### Claims, Quality, And Review",
        "### Reasoning, Retrieval, And Discourse",
        "### Persistence, Evaluation, And Safety",
        "### Navigation Notes",
    ]

    for section in expected_sections:
        assert section in readme

    assert "The initial framework provides:" not in readme


def test_readme_table_of_contents_links_to_scope_subsections() -> None:
    readme = read(README)

    expected_links = [
        "  - [Core Evidence And Memory](#core-evidence-and-memory)",
        "  - [Ingestion And Provenance](#ingestion-and-provenance)",
        "  - [Claims, Quality, And Review](#claims-quality-and-review)",
        "  - [Reasoning, Retrieval, And Discourse](#reasoning-retrieval-and-discourse)",
        "  - [Persistence, Evaluation, And Safety](#persistence-evaluation-and-safety)",
        "  - [Navigation Notes](#navigation-notes)",
    ]

    for link in expected_links:
        assert link in readme


def test_readme_navigation_points_to_ownership_maps() -> None:
    readme = read(README)

    for doc_name in [
        "CURRENT_STATE.md",
        "WORKFLOW_MAP.md",
        "API_AND_MODEL_MAP.md",
        "ADVERSARIAL_RESULTS_GUIDE.md",
        "AI_DEBT.md",
    ]:
        assert f"docs/{doc_name}" in readme


def test_current_state_marks_readme_reorganization_as_completed() -> None:
    current_state = read(DOCS / "CURRENT_STATE.md")

    assert "Phase 34: Hard-Adversarial Remediation Or Predictive-Memory Boundary Evaluation" in current_state
    assert "Phase 33 added predictive memory as an expectation layer for review attention only." in current_state
    assert "README scope reorganization" not in current_state


def test_ai_debt_tracks_readme_regression_risk() -> None:
    ai_debt = read(DOCS / "AI_DEBT.md")

    assert "`README.md` Current Scope is now grouped" in ai_debt
    assert "flat capability ledger again" in ai_debt


def test_phase30_navigation_doc_defines_boundary() -> None:
    phase_doc = read(DOCS / "PHASE_30_DOCUMENTATION_NAVIGATION.md")

    assert "documentation-only consolidation pass" in phase_doc
    assert "does not add runtime behavior" in phase_doc
    assert "Documentation organization is not validation." in phase_doc
