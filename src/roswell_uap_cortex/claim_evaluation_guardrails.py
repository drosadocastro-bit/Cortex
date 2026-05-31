"""Guardrails for claim support and contradiction assessment."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ClaimEvaluationWarning,
    ClaimEvaluationWarningType,
    EvidenceItem,
    ObservationType,
)


@dataclass(slots=True)
class ClaimEvidenceGuardrails:
    """Keep support/contradiction signals from becoming truth claims."""

    def warnings_for(
        self,
        *,
        evidence: EvidenceItem,
        provenance_visible: bool,
        same_lineage: bool = False,
        needs_review: bool = False,
    ) -> list[ClaimEvaluationWarning]:
        related = {evidence.id}
        warnings = [
            ClaimEvaluationWarning(
                ClaimEvaluationWarningType.EVALUATION_NOT_TRUTH,
                "Evidence evaluation organizes signals; it does not decide truth.",
                related,
            ),
            ClaimEvaluationWarning(
                ClaimEvaluationWarningType.SUPPORT_NOT_CONFIRMATION,
                "Possible support is not confirmation.",
                related,
            ),
            ClaimEvaluationWarning(
                ClaimEvaluationWarningType.CONTRADICTION_NOT_DISPROOF,
                "Possible contradiction is not disproof.",
                related,
            ),
        ]
        observation_type = evidence.metadata.get("observation_type")
        if observation_type == ObservationType.SPECULATION.value:
            warnings.append(
                ClaimEvaluationWarning(
                    ClaimEvaluationWarningType.SPECULATIVE_EVIDENCE_CAUTION,
                    "Speculative evidence cannot strongly support factual claims.",
                    related,
                )
            )
        if observation_type == ObservationType.REPORTED_CLAIM.value:
            warnings.append(
                ClaimEvaluationWarning(
                    ClaimEvaluationWarningType.REPORTED_CLAIM_CAUTION,
                    "Reported claim evidence remains reported.",
                    related,
                )
            )
        if observation_type == ObservationType.METADATA_STATEMENT.value:
            warnings.append(
                ClaimEvaluationWarning(
                    ClaimEvaluationWarningType.METADATA_NOT_EVENT_TRUTH,
                    "Metadata statements cannot become event truth.",
                    related,
                )
            )
        if not provenance_visible:
            warnings.append(
                ClaimEvaluationWarning(
                    ClaimEvaluationWarningType.MISSING_PROVENANCE,
                    "Missing provenance forces caution.",
                    related,
                )
            )
        if same_lineage:
            warnings.append(
                ClaimEvaluationWarning(
                    ClaimEvaluationWarningType.SAME_LINEAGE_NOT_CORROBORATION,
                    "Same-lineage support does not corroborate independently.",
                    related,
                )
            )
        if needs_review:
            warnings.append(
                ClaimEvaluationWarning(
                    ClaimEvaluationWarningType.NEEDS_REVIEW,
                    "Support and contradiction pressure both require review.",
                    related,
                )
            )
        return warnings
