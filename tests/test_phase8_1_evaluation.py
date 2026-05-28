from roswell_uap_cortex import (
    EvaluationExpectedBehavior,
    EvaluationHarness,
    EvaluationInput,
    EvaluationReportFormatter,
    EvaluationScenario,
    ExpectedBehaviorType,
    ScenarioFactory,
)
from roswell_uap_cortex.cli import build_demo_evaluation_report
from roswell_uap_cortex.metrics import EpistemicMetrics


def test_evaluation_scenarios_run_deterministically() -> None:
    scenarios = ScenarioFactory().all()
    first = EvaluationHarness().run(scenarios)
    second = EvaluationHarness().run(scenarios)

    assert EvaluationReportFormatter().format(first) == EvaluationReportFormatter().format(second)


def test_expected_behaviors_produce_pass_fail_records() -> None:
    scenario = EvaluationScenario(
        scenario_id="synthetic-failure",
        title="Synthetic Failure",
        description="Synthetic only.",
        inputs=EvaluationInput(),
        expected_behaviors=[
            EvaluationExpectedBehavior(ExpectedBehaviorType.PROVENANCE_VISIBLE)
        ],
        tags={"synthetic"},
    )

    result = EvaluationHarness().evaluate(scenario)

    assert result.behavior_results[ExpectedBehaviorType.PROVENANCE_VISIBLE] is False
    assert result.failures[0].behavior is ExpectedBehaviorType.PROVENANCE_VISIBLE


def test_all_metrics_are_bounded_between_zero_and_one() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())

    assert report.metrics
    assert all(0.0 <= metric.value <= 1.0 for metric in report.metrics)
    assert 0.0 <= report.overall_pass_rate <= 1.0


def test_provenance_visibility_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["provenance_visibility_rate"] == 1.0


def test_contradiction_preservation_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["contradiction_preservation_rate"] == 1.0


def test_unsupported_claim_suppression_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["unsupported_claim_suppression_rate"] == 1.0


def test_association_not_confirmation_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["association_confirmation_separation_rate"] == 1.0


def test_same_lineage_contamination_detection_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["lineage_contamination_detection_rate"] == 1.0


def test_uncertainty_exposure_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["uncertainty_exposure_rate"] == 1.0


def test_contamination_warning_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["contamination_warning_rate"] == 1.0


def test_no_mutation_metric_works() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["no_mutation_rate"] == 1.0


def test_evaluation_reports_include_limitations() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())

    assert any("not real-world truth" in limitation for limitation in report.limitations)
    assert "## Limitations" in EvaluationReportFormatter().format(report)


def test_passing_scenarios_do_not_claim_real_world_truth() -> None:
    formatted = EvaluationReportFormatter().format(
        EvaluationHarness().run(ScenarioFactory().all())
    )

    assert "real-world truth" in formatted
    assert "validates real-world" not in formatted.casefold()


def test_scenario_factory_returns_synthetic_scenarios_only() -> None:
    scenarios = ScenarioFactory().all()

    assert scenarios
    assert all("synthetic" in scenario.tags for scenario in scenarios)
    assert all("Synthetic" in scenario.description for scenario in scenarios)


def test_report_formatting_is_deterministic() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())

    assert EvaluationReportFormatter().format(report) == EvaluationReportFormatter().format(report)


def test_cli_evaluation_report_is_deterministic() -> None:
    first = build_demo_evaluation_report()
    second = build_demo_evaluation_report()

    assert first == second
    assert "# Synthetic Evaluation Report" in first


def test_metric_rate_returns_zero_when_behavior_is_absent() -> None:
    assert EpistemicMetrics().rate([], ExpectedBehaviorType.PROVENANCE_VISIBLE) == 0.0
