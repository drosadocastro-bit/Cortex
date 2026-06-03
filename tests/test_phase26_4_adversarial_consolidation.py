from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_adversarial_results_guide_maps_document_roles() -> None:
    text = read("docs/ADVERSARIAL_RESULTS_GUIDE.md")

    for phrase in [
        "ADVERSARIAL_FINDINGS.md",
        "ADVERSARIAL_CALIBRATION_BASELINE.md",
        "ADR-029-adversarial-calibration-expansion.md",
        "HARD_ADVERSARIAL_FINDINGS.md",
        "HARD_ADVERSARIAL_REMEDIATION.md",
        "AI_DEBT.md",
        "Smoke adversarial results",
        "Calibration baseline",
        "Hard adversarial results",
        "Remediation tracking",
    ]:
        assert phrase in text


def test_adversarial_results_guide_preserves_boundary_language() -> None:
    text = read("docs/ADVERSARIAL_RESULTS_GUIDE.md")

    for phrase in [
        "synthetic resistance as real-world validation",
        "detector metrics as certification",
        "Do not hide false positives",
        "Do not tune adversarial tests toward perfect-looking scores.",
        "Do not treat multilingual examples as broad language coverage.",
        "not safety metrics",
    ]:
        assert phrase in text


def test_adversarial_reports_link_to_results_guide() -> None:
    for path in [
        "docs/ADVERSARIAL_FINDINGS.md",
        "docs/ADVERSARIAL_CALIBRATION_BASELINE.md",
        "docs/ADR-029-adversarial-calibration-expansion.md",
        "docs/HARD_ADVERSARIAL_FINDINGS.md",
    ]:
        assert "ADVERSARIAL_RESULTS_GUIDE.md" in read(path)


def test_phase26_4_consolidation_doc_states_no_new_capability() -> None:
    text = read("docs/PHASE_26_4_ADVERSARIAL_CONSOLIDATION.md")

    for phrase in [
        "does not add a new cognitive layer",
        "No detector accuracy improvement was attempted.",
        "No adversarial outcome was reclassified to look cleaner.",
        "No hard-suite remediation was marked complete.",
        "does not validate Cortex against real-world adversarial manipulation",
    ]:
        assert phrase in text


def test_readme_links_adversarial_consolidation_docs() -> None:
    text = read("README.md")

    assert "ADVERSARIAL_RESULTS_GUIDE.md" in text
    assert "PHASE_26_4_ADVERSARIAL_CONSOLIDATION.md" in text
