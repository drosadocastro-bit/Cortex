from pathlib import Path

from roswell_uap_cortex import AdversarialHarness, AdversarialScenarioFactory


ROOT = Path(__file__).resolve().parents[1]


def test_adversarial_calibration_baseline_is_locked() -> None:
    report = AdversarialHarness().calibrate(AdversarialScenarioFactory().calibration_cases())

    assert report.true_positives == 3
    assert report.true_negatives == 2
    assert report.false_positives == 1
    assert report.false_negatives == 1
    assert round(report.accuracy, 3) == 0.714


def test_adversarial_calibration_preserves_honest_error_cases() -> None:
    cases = AdversarialScenarioFactory().calibration_cases()
    case_ids = {case.case_id for case in cases}

    assert "calibration-false-positive-certification-boundary" in case_ids
    assert "calibration-false-negative-subtle-spanish" in case_ids
    assert any(case.language == "es" for case in cases)


def test_adversarial_calibration_baseline_doc_sets_interpretation_rules() -> None:
    text = (ROOT / "docs" / "ADVERSARIAL_CALIBRATION_BASELINE.md").read_text()

    assert "Do not tune toward a perfect-looking score." in text
    assert "not certification" in text
    assert "real-world safety evidence" in text
    assert "Do not treat multilingual coverage as complete." in text


def test_adversarial_findings_link_to_calibration_baseline() -> None:
    text = (ROOT / "docs" / "ADVERSARIAL_FINDINGS.md").read_text()

    assert "ADVERSARIAL_CALIBRATION_BASELINE.md" in text
