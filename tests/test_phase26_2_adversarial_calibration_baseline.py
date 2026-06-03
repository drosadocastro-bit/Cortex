from pathlib import Path

from roswell_uap_cortex import (
    AdversarialCalibrationErrorType,
    AdversarialHarness,
    AdversarialScenarioFactory,
)


ROOT = Path(__file__).resolve().parents[1]


def test_adversarial_calibration_baseline_is_locked() -> None:
    report = AdversarialHarness().calibrate(AdversarialScenarioFactory().calibration_cases())

    assert len(report.cases) == 16
    assert report.true_positives == 5
    assert report.true_negatives == 4
    assert report.false_positives == 3
    assert report.false_negatives == 4
    assert round(report.accuracy, 3) == 0.562
    assert round(report.precision, 3) == 0.625
    assert round(report.recall, 3) == 0.556
    assert round(report.false_positive_rate, 3) == 0.429
    assert round(report.false_negative_rate, 3) == 0.444


def test_adversarial_calibration_preserves_honest_error_cases() -> None:
    cases = AdversarialScenarioFactory().calibration_cases()
    case_ids = {case.case_id for case in cases}

    assert "calibration-false-positive-certification-boundary" in case_ids
    assert "calibration-false-negative-subtle-spanish" in case_ids
    assert "calibration-false-negative-soft-proof" in case_ids
    assert "calibration-false-positive-spanish-negated-confirmed" in case_ids
    assert any(case.language == "es" for case in cases)


def test_adversarial_calibration_error_taxonomy_is_visible() -> None:
    report = AdversarialHarness().calibrate(AdversarialScenarioFactory().calibration_cases())
    error_types = {case.error_type for case in report.cases}

    assert AdversarialCalibrationErrorType.REVIEW_STATE_LAUNDERING in error_types
    assert AdversarialCalibrationErrorType.OVERBROAD_AUTHORITY_LANGUAGE in error_types
    assert AdversarialCalibrationErrorType.SUBTLE_CERTAINTY_INFLATION in error_types
    assert AdversarialCalibrationErrorType.MULTILINGUAL_CERTAINTY in error_types
    assert AdversarialCalibrationErrorType.NEGATED_CONFIRMATION_LANGUAGE in error_types
    assert AdversarialCalibrationErrorType.TRANSFERABILITY_PRESSURE in error_types


def test_adversarial_calibration_split_metrics_are_bounded() -> None:
    report = AdversarialHarness().calibrate(AdversarialScenarioFactory().calibration_cases())

    assert 0.0 <= report.precision <= 1.0
    assert 0.0 <= report.recall <= 1.0
    assert 0.0 <= report.false_positive_rate <= 1.0
    assert 0.0 <= report.false_negative_rate <= 1.0
    assert report.multilingual_case_count == 5
    assert report.known_limitation_count == 7


def test_adversarial_calibration_baseline_doc_sets_interpretation_rules() -> None:
    text = (ROOT / "docs" / "ADVERSARIAL_CALIBRATION_BASELINE.md").read_text()

    assert "Do not tune toward a perfect-looking score." in text
    assert "not certification" in text
    assert "real-world safety evidence" in text
    assert "Do not treat multilingual coverage as complete." in text
    assert "precision: 0.625" in text
    assert "recall: 0.556" in text
    assert "Error Taxonomy" in text


def test_adversarial_findings_link_to_calibration_baseline() -> None:
    text = (ROOT / "docs" / "ADVERSARIAL_FINDINGS.md").read_text()

    assert "ADVERSARIAL_CALIBRATION_BASELINE.md" in text
