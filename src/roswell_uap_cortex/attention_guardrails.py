"""Guardrails for attention and salience scoring."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    AttentionCandidate,
    AttentionWarning,
    AttentionWarningType,
)


@dataclass(slots=True)
class AttentionGuardrails:
    """Keep salience as review priority, never belief or evidence validity."""

    def warnings_for(self, candidate: AttentionCandidate) -> list[AttentionWarning]:
        warnings = [
            AttentionWarning(
                AttentionWarningType.SALIENCE_NOT_BELIEF,
                "Salience is review priority, not evidence confidence.",
                {candidate.record_id},
            )
        ]
        if candidate.contamination_risk > 0:
            warnings.append(
                AttentionWarning(
                    AttentionWarningType.CONTAMINATION_SALIENT_NOT_TRUSTED,
                    "Contaminated records can be salient for review without being trusted.",
                    {candidate.record_id},
                )
            )
        if not candidate.provenance_ids:
            warnings.append(
                AttentionWarning(
                    AttentionWarningType.PROVENANCE_WARNING_VISIBLE,
                    "Missing provenance remains visible in attention output.",
                    {candidate.record_id},
                )
            )
        if candidate.contradiction_pressure > 0 or candidate.contested:
            warnings.append(
                AttentionWarning(
                    AttentionWarningType.CONTRADICTION_VISIBLE,
                    "Contradictory or contested records remain visible.",
                    {candidate.record_id},
                )
            )
        if candidate.archived:
            warnings.append(
                AttentionWarning(
                    AttentionWarningType.ARCHIVAL_UNCERTAINTY_PRESERVED,
                    "Archival state does not delete or resolve uncertainty.",
                    {candidate.record_id},
                )
            )
        if candidate.speculative:
            warnings.append(
                AttentionWarning(
                    AttentionWarningType.SPECULATION_REMAINS_SPECULATION,
                    "Speculative artifacts remain speculative.",
                    {candidate.record_id},
                )
            )
        return warnings

    def required_guardrails_enabled(self, policy_flags: dict[str, bool]) -> bool:
        return all(policy_flags.values())
