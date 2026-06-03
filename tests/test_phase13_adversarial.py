from roswell_uap_cortex import (
    AdversarialAttackVector,
    AdversarialExpectedFailureMode,
    AdversarialHarness,
    AdversarialReportFormatter,
    AdversarialScenarioFactory,
)


def test_adversarial_factory_returns_synthetic_attack_scenarios() -> None:
    scenarios = AdversarialScenarioFactory().all()

    assert len(scenarios) == 17
    assert all("synthetic" in scenario.tags for scenario in scenarios)
    assert all("adversarial" in scenario.tags for scenario in scenarios)


def test_adversarial_scenarios_cover_expected_attack_vectors() -> None:
    vectors = {scenario.attack_vector for scenario in AdversarialScenarioFactory().all()}

    assert vectors == set(AdversarialAttackVector)


def test_adversarial_scenarios_cover_expected_failure_modes() -> None:
    modes = {scenario.expected_failure_mode for scenario in AdversarialScenarioFactory().all()}

    assert modes == set(AdversarialExpectedFailureMode)


def test_adversarial_harness_runs_deterministically() -> None:
    scenarios = AdversarialScenarioFactory().all()
    harness = AdversarialHarness()

    first = harness.run(scenarios)
    second = harness.run(scenarios)

    assert [(finding.scenario_id, finding.resisted) for finding in first.findings] == [
        (finding.scenario_id, finding.resisted) for finding in second.findings
    ]


def test_adversarial_findings_record_pass_fail_per_attack() -> None:
    report = AdversarialHarness().run(AdversarialScenarioFactory().all())

    assert report.scenario_count == 17
    assert report.resisted_count == 17
    assert report.resistance_rate == 1.0
    assert all(finding.triggered_behaviors for finding in report.findings)
    assert all(not finding.failed_behaviors for finding in report.findings)


def test_provenance_laundering_attack_is_resisted_by_lineage_guardrail() -> None:
    report = AdversarialHarness().run([AdversarialScenarioFactory().provenance_laundering()])
    finding = report.findings[0]

    assert finding.attack_vector is AdversarialAttackVector.PROVENANCE_LAUNDERING
    assert finding.expected_failure_mode is AdversarialExpectedFailureMode.FALSE_INDEPENDENCE
    assert finding.resisted


def test_discourse_contamination_attack_is_blocked() -> None:
    report = AdversarialHarness().run([AdversarialScenarioFactory().discourse_contamination()])
    finding = report.findings[0]

    assert finding.attack_vector is AdversarialAttackVector.DISCOURSE_CONTAMINATION
    assert finding.expected_failure_mode is AdversarialExpectedFailureMode.DISCOURSE_AS_EVIDENCE
    assert finding.resisted


def test_policy_abuse_does_not_disable_attention_guardrails() -> None:
    report = AdversarialHarness().run([AdversarialScenarioFactory().policy_abuse()])
    finding = report.findings[0]

    assert finding.attack_vector is AdversarialAttackVector.POLICY_ABUSE
    assert finding.expected_failure_mode is AdversarialExpectedFailureMode.GUARDRAIL_DISABLED_BY_POLICY
    assert finding.resisted


def test_adversarial_report_includes_limitations() -> None:
    report = AdversarialHarness().run(AdversarialScenarioFactory().all())

    assert report.limitations
    assert any("not real-world validation" in limitation for limitation in report.limitations)


def test_adversarial_report_formatting_is_deterministic() -> None:
    report = AdversarialHarness().run(AdversarialScenarioFactory().all())
    formatter = AdversarialReportFormatter()

    assert formatter.format(report) == formatter.format(report)
    assert "resistance_rate: 1.000" in formatter.format(report)
    assert "Findings" in formatter.format(report)


def test_review_and_presentation_attacks_are_resisted() -> None:
    factory = AdversarialScenarioFactory()
    scenarios = [
        factory.review_state_laundering(),
        factory.presentation_aggregation_trap(),
        factory.missing_data_prettification(),
        factory.transferability_leap(),
        factory.authority_laundering(),
        factory.multilingual_certainty_inflation(),
    ]
    report = AdversarialHarness().run(scenarios)

    assert report.scenario_count == 6
    assert report.resisted_count == 6


def test_evidence_quality_laundering_attack_is_resisted() -> None:
    report = AdversarialHarness().run([AdversarialScenarioFactory().quality_score_laundering()])
    finding = report.findings[0]

    assert finding.attack_vector is AdversarialAttackVector.QUALITY_SCORE_LAUNDERING
    assert finding.expected_failure_mode is AdversarialExpectedFailureMode.QUALITY_AS_CONFIRMATION
    assert finding.resisted


def test_adversarial_calibration_reports_confusion_matrix_buckets() -> None:
    report = AdversarialHarness().calibrate(AdversarialScenarioFactory().calibration_cases())

    assert report.true_positives >= 1
    assert report.true_negatives >= 1
    assert report.false_positives >= 1
    assert report.false_negatives >= 1
    assert 0.0 <= report.accuracy <= 1.0
    assert any(case.language == "es" for case in report.cases)
    assert any("False positives and false negatives" in limitation for limitation in report.limitations)


def test_adversarial_detector_avoids_provenance_false_positive() -> None:
    harness = AdversarialHarness()

    assert not harness.detect_boundary_attack_text("Provenance remains visible.")
    assert harness.detect_boundary_attack_text("Reviewed, therefore confirmed.")
