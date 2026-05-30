"""Adversarial epistemic stress testing harness."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.evaluation import EvaluationHarness
from roswell_uap_cortex.models import (
    AdversarialFinding,
    AdversarialReport,
    AdversarialScenario,
    EvaluationExpectedBehavior,
    EvaluationScenario,
)


@dataclass(slots=True)
class AdversarialHarness:
    """Run synthetic adversarial scenarios against deterministic guardrails."""

    evaluation_harness: EvaluationHarness = field(default_factory=EvaluationHarness)

    def run(self, scenarios: list[AdversarialScenario]) -> AdversarialReport:
        findings = [self.evaluate(scenario) for scenario in scenarios]
        return AdversarialReport(findings=findings, limitations=self.limitations())

    def evaluate(self, scenario: AdversarialScenario) -> AdversarialFinding:
        evaluation_scenario = EvaluationScenario(
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
            risk_level=scenario.risk_level,
        )
        result = self.evaluation_harness.evaluate(evaluation_scenario)
        triggered = [
            behavior for behavior, passed in result.behavior_results.items() if passed
        ]
        failed = [
            behavior for behavior, passed in result.behavior_results.items() if not passed
        ]
        return AdversarialFinding(
            scenario_id=scenario.scenario_id,
            attack_vector=scenario.attack_vector,
            expected_failure_mode=scenario.expected_failure_mode,
            resisted=not failed,
            triggered_behaviors=triggered,
            failed_behaviors=failed,
            notes=self._notes(result.passed),
        )

    def limitations(self) -> list[str]:
        return [
            "Adversarial scenarios are synthetic stress tests, not real-world validation.",
            "Resistance means expected guardrail behavior was observed in fixtures only.",
            "Findings do not establish truth or falsity of any external claim.",
        ]

    def _notes(self, resisted: bool) -> list[str]:
        if resisted:
            return ["Expected boundary behavior resisted the synthetic attack."]
        return ["Synthetic attack exposed a missing or weakened guardrail behavior."]
