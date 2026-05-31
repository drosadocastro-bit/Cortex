"""Guardrails for candidate claim normalization."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    CandidateClaim,
    CandidateClaimOrigin,
    ClaimNormalizationWarning,
    ClaimNormalizationWarningType,
)


@dataclass(slots=True)
class ClaimNormalizationGuardrails:
    """Keep canonical grouping separate from validation or support."""

    def warnings_for_group(self, candidates: list[CandidateClaim]) -> list[ClaimNormalizationWarning]:
        ids = {candidate.id for candidate in candidates}
        warnings = [
            ClaimNormalizationWarning(
                ClaimNormalizationWarningType.NORMALIZATION_NOT_VALIDATION,
                "Claim normalization is organization, not validation.",
                ids,
            ),
            ClaimNormalizationWarning(
                ClaimNormalizationWarningType.UNSUPPORTED_TOPIC_ONLY,
                "Normalized claims enter the matrix as unsupported topics only.",
                ids,
            ),
        ]
        lineage_ids = [
            str(candidate.metadata.get("lineage_id"))
            for candidate in candidates
            if candidate.metadata.get("lineage_id")
        ]
        if len(lineage_ids) != len(set(lineage_ids)):
            warnings.append(
                ClaimNormalizationWarning(
                    ClaimNormalizationWarningType.SAME_LINEAGE_REPETITION,
                    "Same-lineage repeated candidate claims do not imply corroboration.",
                    ids,
                )
            )
        if len(candidates) > 1:
            warnings.append(
                ClaimNormalizationWarning(
                    ClaimNormalizationWarningType.REPEATED_CLAIMS_NOT_CORROBORATION,
                    "Repeated candidate claims do not create support.",
                    ids,
                )
            )
        origins = {candidate.origin for candidate in candidates}
        if CandidateClaimOrigin.FROM_SPECULATION in origins:
            warnings.append(
                ClaimNormalizationWarning(
                    ClaimNormalizationWarningType.SPECULATION_ORIGIN_VISIBLE,
                    "Speculation-origin claims remain visibly speculative.",
                    ids,
                )
            )
        if CandidateClaimOrigin.FROM_REPORTED_CLAIM in origins:
            warnings.append(
                ClaimNormalizationWarning(
                    ClaimNormalizationWarningType.REPORTED_ORIGIN_VISIBLE,
                    "Reported claims remain reported, not direct evidence.",
                    ids,
                )
            )
        if CandidateClaimOrigin.FROM_METADATA in origins:
            warnings.append(
                ClaimNormalizationWarning(
                    ClaimNormalizationWarningType.METADATA_NOT_EVENT_TRUTH,
                    "Metadata-origin claims do not become event truth.",
                    ids,
                )
            )
        if len(origins) > 1:
            warnings.append(
                ClaimNormalizationWarning(
                    ClaimNormalizationWarningType.AMBIGUOUS_ORIGIN_MERGE,
                    "Multiple origin types are present in the normalized group.",
                    ids,
                )
            )
        return warnings
