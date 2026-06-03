"""Guardrails for evidence-quality assessment."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    EvidenceQualityAssessment,
    EvidenceQualityWarning,
    EvidenceQualityWarningType,
)


@dataclass(slots=True)
class EvidenceQualityGuardrails:
    """Keep evidence quality as review context, not truth or confirmation."""

    def baseline_warnings(self, evidence_id: str) -> list[EvidenceQualityWarning]:
        return [
            EvidenceQualityWarning(
                EvidenceQualityWarningType.QUALITY_NOT_TRUTH,
                "Evidence quality describes record condition, not whether the evidence is true.",
                {evidence_id},
            ),
            EvidenceQualityWarning(
                EvidenceQualityWarningType.REVIEW_SIGNAL_ONLY,
                "Evidence quality may guide review ordering and context visibility only.",
                {evidence_id},
            ),
        ]

    def validates_boundary(self, assessment: EvidenceQualityAssessment) -> bool:
        warning_types = {warning.warning_type for warning in assessment.warnings}
        return {
            EvidenceQualityWarningType.QUALITY_NOT_TRUTH,
            EvidenceQualityWarningType.REVIEW_SIGNAL_ONLY,
        }.issubset(warning_types)
