"""Deterministic candidate claim normalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.claim_normalization_guardrails import ClaimNormalizationGuardrails
from roswell_uap_cortex.models import (
    CandidateClaim,
    CandidateClaimOrigin,
    ClaimCanonicalKey,
    ClaimNormalizationPolicy,
    ClaimNormalizationResult,
    NormalizedClaim,
)
from roswell_uap_cortex.text import SimpleTokenizer


@dataclass(slots=True)
class ClaimNormalizer:
    """Group candidate claims by deterministic canonical keys."""

    policy: ClaimNormalizationPolicy = field(default_factory=ClaimNormalizationPolicy)
    tokenizer: SimpleTokenizer = field(default_factory=SimpleTokenizer)
    guardrails: ClaimNormalizationGuardrails = field(default_factory=ClaimNormalizationGuardrails)

    def normalize(self, candidates: list[CandidateClaim]) -> ClaimNormalizationResult:
        groups: dict[ClaimCanonicalKey, list[CandidateClaim]] = {}
        for candidate in candidates:
            key = self._canonical_key(candidate)
            groups.setdefault(key, []).append(candidate)

        normalized: list[NormalizedClaim] = []
        warnings = []
        for key, grouped in sorted(groups.items(), key=lambda item: item[0].value):
            group_warnings = self.guardrails.warnings_for_group(grouped)
            warnings.extend(group_warnings)
            normalized.append(self._normalized_claim(key, grouped, group_warnings))

        return ClaimNormalizationResult(
            normalized_claims=normalized,
            warnings=warnings,
            notes=["deterministic claim normalization; no support or confirmation created"],
        )

    def _canonical_key(self, candidate: CandidateClaim) -> ClaimCanonicalKey:
        reporting_boilerplate = {"witness", "reported", "stated", "claimed", "said"}
        tokens = tuple(
            sorted(
                token
                for token in self.tokenizer.tokenize(candidate.text)
                if token not in reporting_boilerplate
            )
        )
        value = "-".join(tokens) or "unknown"
        return ClaimCanonicalKey(
            value=value,
            origin_bucket=self._origin_bucket(candidate.origin),
            token_fingerprint=tokens,
        )

    def _origin_bucket(self, origin: CandidateClaimOrigin) -> str:
        if self.policy.allow_cross_origin_merge:
            if origin is CandidateClaimOrigin.FROM_METADATA and not self.policy.allow_metadata_event_merge:
                return "metadata"
            return "mixed"
        if origin is CandidateClaimOrigin.FROM_SPECULATION and self.policy.isolate_speculation:
            return "speculation"
        if origin is CandidateClaimOrigin.FROM_METADATA and self.policy.isolate_metadata:
            return "metadata"
        return origin.value

    def _normalized_claim(
        self,
        key: ClaimCanonicalKey,
        candidates: list[CandidateClaim],
        warnings,
    ) -> NormalizedClaim:
        candidate_ids = {candidate.id for candidate in candidates}
        evidence_ids = {
            candidate.source_evidence_id
            for candidate in candidates
            if candidate.source_evidence_id
        }
        provenance_ids = set().union(*(candidate.provenance_ids for candidate in candidates))
        lineage_ids = {
            str(candidate.metadata["lineage_id"])
            for candidate in candidates
            if candidate.metadata.get("lineage_id")
        }
        canonical_text = sorted(candidate.text for candidate in candidates)[0]
        return NormalizedClaim(
            normalized_claim_id=str(uuid5(NAMESPACE_URL, f"normalized-claim:{key.origin_bucket}:{key.value}")),
            canonical_key=key,
            canonical_text=canonical_text,
            candidate_claim_ids=candidate_ids,
            origin_types={candidate.origin for candidate in candidates},
            evidence_ids=evidence_ids,
            provenance_ids=provenance_ids,
            lineage_ids=lineage_ids,
            warning_flags=list(warnings),
            unsupported=True,
            confidence=0.0,
            notes=["normalized candidate claim group; organization not validation"],
        )
