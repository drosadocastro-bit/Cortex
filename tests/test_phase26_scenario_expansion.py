from pathlib import Path

from roswell_uap_cortex import (
    EvaluationHarness,
    ExpectedBehaviorType,
    ScenarioDatasetBuilder,
    ScenarioFactory,
)
from roswell_uap_cortex.evaluation_report import EvaluationReportFormatter


def test_scenario_factory_includes_review_and_presentation_expansion() -> None:
    scenarios = ScenarioFactory().all()
    scenario_ids = {scenario.scenario_id for scenario in scenarios}

    assert "synthetic-review-state-not-truth" in scenario_ids
    assert "synthetic-deferred-review-visible" in scenario_ids
    assert "synthetic-source-risk-not-rejection" in scenario_ids
    assert "synthetic-presentation-not-reasoning" in scenario_ids
    assert "synthetic-presentation-no-aggregation" in scenario_ids
    assert "synthetic-presentation-missing-data-visible" in scenario_ids
    assert "synthetic-demo-presentation-only" in scenario_ids
    assert all("synthetic" in scenario.tags for scenario in scenarios)


def test_expanded_scenarios_pass_without_claiming_real_world_validity() -> None:
    scenarios = [
        scenario
        for scenario in ScenarioFactory().all()
        if {"review-influence", "presentation"} & scenario.tags
    ]
    report = EvaluationHarness().run(scenarios)
    text = EvaluationReportFormatter().format(report)

    assert report.overall_pass_rate == 1.0
    assert "real-world truth" in text
    assert "certify operational use" not in text.casefold()


def test_new_behavior_metrics_are_bounded_and_visible() -> None:
    report = EvaluationHarness().run(ScenarioFactory().all())
    metrics = {metric.name: metric.value for metric in report.metrics}

    assert metrics["review_state_boundary_rate"] == 1.0
    assert metrics["presentation_boundary_rate"] == 1.0
    assert metrics["synthetic_demo_presentation_rate"] == 1.0
    assert all(0.0 <= value <= 1.0 for value in metrics.values())


def test_scenario_dataset_summary_is_deterministic_and_limited() -> None:
    first = ScenarioDatasetBuilder().build()
    second = ScenarioDatasetBuilder().build()

    assert first == second
    assert first.scenario_count == len(first.scenarios)
    assert first.tag_counts["presentation"] >= 4
    assert first.tag_counts["review-influence"] >= 3
    assert first.behavior_counts[ExpectedBehaviorType.PRESENTATION_NOT_REASONING.value] >= 1
    assert any("not real-world validation" in limitation for limitation in first.limitations)


def test_phase26_docs_describe_scenario_expansion_without_transfer_claims() -> None:
    root = Path(__file__).resolve().parents[1]
    dataset_doc = (root / "docs" / "SYNTHETIC_SCENARIO_DATASET.md").read_text(encoding="utf-8")
    adr = (root / "docs" / "ADR-028-synthetic-scenario-expansion.md").read_text(encoding="utf-8")

    assert "Review influence boundary scenarios" in dataset_doc
    assert "Presentation contract scenarios" in dataset_doc
    assert "Predictive maintenance transferability remains deferred" in dataset_doc
    assert "scenario coverage is not certification" in adr
