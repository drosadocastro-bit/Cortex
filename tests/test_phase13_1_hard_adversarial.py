from roswell_uap_cortex import (
    HardAdversarialHarness,
    HardAdversarialOutcome,
    HardAdversarialReportFormatter,
    HardAdversarialScenarioFactory,
    OWASPLLMRisk,
)


def test_hard_adversarial_factory_maps_to_owasp_inspired_risks() -> None:
    scenarios = HardAdversarialScenarioFactory().all()
    risks = {scenario.owasp_risk for scenario in scenarios}

    assert len(scenarios) == 8
    assert OWASPLLMRisk.LLM01_PROMPT_INJECTION in risks
    assert OWASPLLMRisk.LLM08_VECTOR_AND_EMBEDDING_WEAKNESSES in risks
    assert OWASPLLMRisk.LLM10_UNBOUNDED_CONSUMPTION in risks


def test_hard_suite_is_not_perfect_by_design() -> None:
    report = HardAdversarialHarness().run(HardAdversarialScenarioFactory().all())
    counts = report.outcome_counts()

    assert counts[HardAdversarialOutcome.RESISTED] > 0
    assert counts[HardAdversarialOutcome.NEAR_MISS] > 0
    assert counts[HardAdversarialOutcome.FAILED_EXPECTED] > 0
    assert counts[HardAdversarialOutcome.INCONCLUSIVE] > 0
    assert report.calibration_passed


def test_hard_suite_has_no_unexpected_failures_initially() -> None:
    report = HardAdversarialHarness().run(HardAdversarialScenarioFactory().all())

    assert report.outcome_counts()[HardAdversarialOutcome.FAILED_UNEXPECTED] == 0


def test_hard_prompt_injection_is_marked_near_miss() -> None:
    finding = HardAdversarialHarness().run(
        [HardAdversarialScenarioFactory().prompt_injection_note()]
    ).findings[0]

    assert finding.outcome is HardAdversarialOutcome.NEAR_MISS
    assert "obvious" in " ".join(finding.notes)


def test_hard_polished_misinformation_is_expected_failure() -> None:
    finding = HardAdversarialHarness().run(
        [HardAdversarialScenarioFactory().misinformation_polished_speculation()]
    ).findings[0]

    assert finding.outcome is HardAdversarialOutcome.FAILED_EXPECTED
    assert finding.failed_behaviors


def test_hard_sensitive_metadata_is_inconclusive() -> None:
    finding = HardAdversarialHarness().run(
        [HardAdversarialScenarioFactory().sensitive_metadata_disclosure()]
    ).findings[0]

    assert finding.outcome is HardAdversarialOutcome.INCONCLUSIVE
    assert "does not prove enough" in " ".join(finding.notes)


def test_hard_report_formatter_is_deterministic_and_honest() -> None:
    report = HardAdversarialHarness().run(HardAdversarialScenarioFactory().all())
    formatter = HardAdversarialReportFormatter()
    text = formatter.format(report)

    assert text == formatter.format(report)
    assert "near_miss:" in text
    assert "failed_expected:" in text
    assert "calibration_passed: true" in text


def test_hard_report_limitations_prevent_truth_claims() -> None:
    report = HardAdversarialHarness().run(HardAdversarialScenarioFactory().all())

    assert any("not penetration-test certification" in item for item in report.limitations)
    assert any("do not validate real-world UAP claims" in item for item in report.limitations)
