"""Adversarial epistemic stress testing harness."""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from roswell_uap_cortex.evaluation import EvaluationHarness
from roswell_uap_cortex.models import (
    AdversarialCalibrationCase,
    AdversarialCalibrationReport,
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

    def calibrate(self, cases: list[AdversarialCalibrationCase]) -> AdversarialCalibrationReport:
        calibrated = [
            AdversarialCalibrationCase(
                case_id=case.case_id,
                text=case.text,
                expected_attack=case.expected_attack,
                detected_attack=self.detect_boundary_attack_text(case.text),
                language=case.language,
                error_type=case.error_type,
                notes=list(case.notes),
            )
            for case in cases
        ]
        return AdversarialCalibrationReport(
            cases=calibrated,
            limitations=[
                "Calibration checks wording patterns only, not general semantic understanding.",
                "False positives and false negatives are retained as detector limitations.",
                "Multilingual cases are synthetic and incomplete.",
                "Precision and recall are behavior metrics, not real-world safety validation.",
            ],
        )

    def detect_boundary_attack_text(self, text: str) -> bool:
        normalized = text.casefold()
        phrases = (
            "therefore confirmed",
            "reviewed therefore confirmed",
            "reviewed, therefore confirmed",
            "high priority means true",
            "source risk means reject",
            "warnings together prove",
            "grouped cards corroborate",
            "missing provenance is harmless",
            "validated for predictive maintenance",
            "certified for predictive maintenance",
            "certification",
            "safety certified",
            "operational authority",
            "safe to dispatch",
            "confirmado",
            "certificado",
            "validado",
            "seguro para despacho",
        )
        if any(phrase in normalized for phrase in phrases):
            return True
        return any(
            re.search(rf"(?<![a-z0-9]){term}(?![a-z0-9])", normalized)
            for term in ("confirmed", "definitive", "verified true", "debunked")
        )

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
