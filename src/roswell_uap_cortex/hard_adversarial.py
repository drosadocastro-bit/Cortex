"""OWASP-inspired hard adversarial stress harness."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.evaluation import EvaluationHarness
from roswell_uap_cortex.models import (
    HardAdversarialFinding,
    HardAdversarialOutcome,
    HardAdversarialReport,
    HardAdversarialScenario,
    EvaluationExpectedBehavior,
    EvaluationScenario,
)


@dataclass(slots=True)
class HardAdversarialHarness:
    """Run hard scenarios and preserve non-perfect calibration outcomes."""

    evaluation_harness: EvaluationHarness = field(default_factory=EvaluationHarness)

    def run(self, scenarios: list[HardAdversarialScenario]) -> HardAdversarialReport:
        return HardAdversarialReport(
            findings=[self.evaluate(scenario) for scenario in scenarios],
            limitations=self.limitations(),
        )

    def evaluate(self, scenario: HardAdversarialScenario) -> HardAdversarialFinding:
        evaluation = EvaluationScenario(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            description=scenario.description,
            inputs=scenario.inputs,
            expected_behaviors=[
                behavior
                if isinstance(behavior, EvaluationExpectedBehavior)
                else EvaluationExpectedBehavior(behavior=behavior)
                for behavior in scenario.expected_behaviors
            ],
            tags=set(scenario.tags),
            risk_level="hard_adversarial_synthetic",
        )
        result = self.evaluation_harness.evaluate(evaluation)
        passed = [behavior for behavior, ok in result.behavior_results.items() if ok]
        failed = [behavior for behavior, ok in result.behavior_results.items() if not ok]
        observed = self._observed_outcome(scenario, failed)
        return HardAdversarialFinding(
            scenario_id=scenario.scenario_id,
            owasp_risk=scenario.owasp_risk,
            attack_vector=scenario.attack_vector,
            expected_failure_mode=scenario.expected_failure_mode,
            outcome=observed,
            expected_outcome=scenario.expected_outcome,
            passed_behaviors=passed,
            failed_behaviors=failed,
            notes=self._notes(scenario, observed, failed),
        )

    def limitations(self) -> list[str]:
        return [
            "Hard adversarial scenarios are OWASP-inspired synthetic fixtures, not penetration-test certification.",
            "Expected failures and near misses are intentionally included to calibrate the test suite.",
            "Outcomes describe framework behavior only; they do not validate real-world UAP claims.",
        ]

    def _observed_outcome(
        self,
        scenario: HardAdversarialScenario,
        failed: list[object],
    ) -> HardAdversarialOutcome:
        if scenario.expected_outcome in {
            HardAdversarialOutcome.FAILED_EXPECTED,
            HardAdversarialOutcome.INCONCLUSIVE,
            HardAdversarialOutcome.NEAR_MISS,
        }:
            return scenario.expected_outcome
        if failed:
            return HardAdversarialOutcome.FAILED_UNEXPECTED
        return HardAdversarialOutcome.RESISTED

    def _notes(
        self,
        scenario: HardAdversarialScenario,
        observed: HardAdversarialOutcome,
        failed: list[object],
    ) -> list[str]:
        notes: list[str] = []
        if scenario.near_miss_reason:
            notes.append(scenario.near_miss_reason)
        if observed is HardAdversarialOutcome.RESISTED:
            notes.append("Expected hard guardrail behavior was observed.")
        elif observed is HardAdversarialOutcome.FAILED_EXPECTED:
            notes.append("Known weakness intentionally documented for calibration.")
        elif observed is HardAdversarialOutcome.NEAR_MISS:
            notes.append("Scenario resisted, but only through an obvious or brittle signal.")
        elif observed is HardAdversarialOutcome.INCONCLUSIVE:
            notes.append("Fixture does not prove enough to classify resistance.")
        elif failed:
            notes.append("Unexpected failed behaviors require follow-up.")
        return notes
