"""Deterministic adversarial report formatting."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import AdversarialReport


@dataclass(slots=True)
class AdversarialReportFormatter:
    """Render compact adversarial findings in deterministic order."""

    def format(self, report: AdversarialReport) -> str:
        lines = [
            "# Adversarial Epistemic Stress Report",
            f"scenario_count: {report.scenario_count}",
            f"resisted_scenarios: {report.resisted_count}",
            f"failed_scenarios: {report.scenario_count - report.resisted_count}",
            f"resistance_rate: {report.resistance_rate:.3f}",
            "## Findings",
        ]
        for finding in sorted(report.findings, key=lambda item: item.scenario_id):
            status = "resisted" if finding.resisted else "failed"
            lines.append(
                "- "
                f"{finding.scenario_id}: {status}; "
                f"attack={finding.attack_vector.value}; "
                f"failure_mode={finding.expected_failure_mode.value}"
            )
        lines.append("## Limitations")
        lines.extend(f"- {limitation}" for limitation in report.limitations)
        return "\n".join(lines)
