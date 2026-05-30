"""Report formatter for OWASP-inspired hard adversarial tests."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import HardAdversarialOutcome, HardAdversarialReport


@dataclass(slots=True)
class HardAdversarialReportFormatter:
    """Render hard adversarial results with honest outcome counts."""

    def format(self, report: HardAdversarialReport) -> str:
        counts = report.outcome_counts()
        lines = [
            "# OWASP-Inspired Hard Adversarial Report",
            f"scenario_count: {report.scenario_count}",
            f"resisted: {counts[HardAdversarialOutcome.RESISTED]}",
            f"near_miss: {counts[HardAdversarialOutcome.NEAR_MISS]}",
            f"failed_expected: {counts[HardAdversarialOutcome.FAILED_EXPECTED]}",
            f"failed_unexpected: {counts[HardAdversarialOutcome.FAILED_UNEXPECTED]}",
            f"inconclusive: {counts[HardAdversarialOutcome.INCONCLUSIVE]}",
            f"calibration_passed: {str(report.calibration_passed).lower()}",
            "## Findings",
        ]
        for finding in sorted(report.findings, key=lambda item: item.scenario_id):
            lines.append(
                "- "
                f"{finding.scenario_id}: outcome={finding.outcome.value}; "
                f"owasp={finding.owasp_risk.value}; "
                f"attack={finding.attack_vector.value}; "
                f"failure_mode={finding.expected_failure_mode.value}"
            )
        lines.append("## Limitations")
        lines.extend(f"- {limitation}" for limitation in report.limitations)
        return "\n".join(lines)
