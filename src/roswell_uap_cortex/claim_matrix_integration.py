"""Safe integration of normalized claims into the claim matrix."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.claim_matrix import ClaimMatrixEngine
from roswell_uap_cortex.models import (
    ClaimMatrixIntegrationResult,
    ClaimMatrixStatus,
    ClaimNode,
    ClaimNormalizationWarning,
    ClaimNormalizationWarningType,
    NormalizedClaim,
)


@dataclass(slots=True)
class ClaimMatrixIntegrator:
    """Register normalized candidate topics without support or confirmation."""

    claim_matrix: ClaimMatrixEngine = field(default_factory=ClaimMatrixEngine)

    def integrate(self, normalized_claims: list[NormalizedClaim]) -> ClaimMatrixIntegrationResult:
        result = ClaimMatrixIntegrationResult(
            notes=["normalized claims registered as unsupported candidate topics only"]
        )
        for normalized in normalized_claims:
            claim = ClaimNode(
                text=normalized.canonical_text,
                canonical_topic=normalized.canonical_key.value,
                evidence_ids=set(),
                status=ClaimMatrixStatus.UNSUPPORTED,
                confidence=0.0,
                metadata={
                    "normalized_claim_id": normalized.normalized_claim_id,
                    "candidate_claim_ids": sorted(normalized.candidate_claim_ids),
                    "source_evidence_ids": sorted(normalized.evidence_ids),
                    "provenance_ids": sorted(normalized.provenance_ids),
                    "lineage_ids": sorted(normalized.lineage_ids),
                    "origin_types": sorted(origin.value for origin in normalized.origin_types),
                    "integration_not_support": True,
                },
            )
            entry = self.claim_matrix.register_unsupported_candidate_topic(
                normalized.canonical_key.value,
                claim,
            )
            result.registered_topics.add(entry.canonical_topic)
            result.claim_node_ids.add(claim.id)
            result.warnings.extend(normalized.warning_flags)
            result.warnings.append(
                ClaimNormalizationWarning(
                    ClaimNormalizationWarningType.UNSUPPORTED_TOPIC_ONLY,
                    "Claim matrix registration did not add support evidence.",
                    {normalized.normalized_claim_id},
                )
            )
        return result
