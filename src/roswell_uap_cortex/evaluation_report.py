"""Deterministic text formatting for evaluation reports."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import EvaluationReport


@dataclass(slots=True)
class EvaluationReportFormatter:
    """Create compact deterministic evaluation reports."""

    def format(self, report: EvaluationReport) -> str:
        scenario_count = len(report.results)
        passed = sum(1 for result in report.results if result.passed)
        failed = scenario_count - passed
        lines = [
            "# Synthetic Evaluation Report",
            f"scenario_count: {scenario_count}",
            f"passed_scenarios: {passed}",
            f"failed_scenarios: {failed}",
            f"overall_framework_behavior_pass_rate: {report.overall_pass_rate:.3f}",
            "## Metrics",
        ]
        for metric in sorted(report.metrics, key=lambda item: item.name):
            lines.append(f"- {metric.name}: {metric.value:.3f}")
        lines.append("## Failed Behaviors")
        failures = [
            failure
            for result in sorted(report.results, key=lambda item: item.scenario_id)
            for failure in result.failures
        ]
        if failures:
            for failure in failures:
                lines.append(
                    f"- {failure.scenario_id}::{failure.behavior.value}: {failure.message}"
                )
        else:
            lines.append("- none")
        lines.append("## Limitations")
        for limitation in report.limitations:
            lines.append(f"- {limitation}")
        return "\n".join(lines)
