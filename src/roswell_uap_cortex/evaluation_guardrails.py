"""Guardrails for interpreting synthetic evaluation results."""

from __future__ import annotations

from dataclasses import dataclass


EVALUATION_LIMITATIONS = [
    "Synthetic evaluation measures framework behavior, not real-world truth.",
    "Passing scenarios do not validate any UAP conclusion or evidentiary claim.",
    "Metrics are guardrail indicators, not scientific validity scores.",
]


@dataclass(slots=True)
class EvaluationGuardrails:
    """Attach mandatory limitations to every evaluation report."""

    def limitations(self) -> list[str]:
        return list(EVALUATION_LIMITATIONS)
