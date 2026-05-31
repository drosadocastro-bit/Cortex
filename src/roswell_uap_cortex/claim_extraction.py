"""Deterministic candidate claim extraction without confirmation."""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from roswell_uap_cortex.models import (
    CandidateClaim,
    CandidateClaimOrigin,
    ClaimExtractionPolicy,
    ClaimExtractionResult,
    ClaimExtractionWarning,
    ClaimExtractionWarningType,
    EvidenceItem,
    ExtractedObservation,
    ObservationType,
    ProvenanceRecord,
)


@dataclass(slots=True)
class ClaimExtractionEngine:
    """Extract candidate claims while keeping them unsupported."""

    policy: ClaimExtractionPolicy = field(default_factory=ClaimExtractionPolicy)

    def extract(
        self,
        observations: list[ExtractedObservation] | None = None,
        *,
        evidence_by_id: dict[str, EvidenceItem] | None = None,
        provenance_by_evidence_id: dict[str, ProvenanceRecord] | None = None,
    ) -> ClaimExtractionResult:
        observations = observations or []
        evidence_by_id = evidence_by_id or {}
        provenance_by_evidence_id = provenance_by_evidence_id or {}
        result = ClaimExtractionResult(
            extraction_notes=["deterministic candidate claim extraction; no confirmation created"]
        )

        for observation in observations:
            if not self._allowed(observation.observation_type):
                continue
            evidence = evidence_by_id.get(observation.evidence_id or "")
            provenance = provenance_by_evidence_id.get(observation.evidence_id or "")
            candidate = self._candidate_from_observation(observation, evidence, provenance)
            result.candidate_claims.append(candidate)
            result.warnings.extend(candidate.warnings)

        return result

    def _candidate_from_observation(
        self,
        observation: ExtractedObservation,
        evidence: EvidenceItem | None,
        provenance: ProvenanceRecord | None,
    ) -> CandidateClaim:
        origin = self._origin_for(observation.observation_type)
        provenance_ids = {provenance.id} if provenance else set()
        warnings = self._warnings_for(observation, provenance)
        text = self._normalize_claim_text(observation.text)
        return CandidateClaim(
            text=text,
            canonical_topic=self._canonical_topic(text),
            origin=origin,
            source_observation_id=observation.id,
            source_evidence_id=observation.evidence_id,
            provenance_ids=provenance_ids,
            observation_type=observation.observation_type,
            speculative=observation.observation_type is ObservationType.SPECULATION,
            extraction_notes=[
                "candidate claim extracted for review only",
                f"source observation type: {observation.observation_type.value}",
            ],
            warnings=warnings,
            metadata={
                "source_evidence_id": None if evidence is None else evidence.id,
                "source_id": None if evidence is None else evidence.source_id,
                "extraction_not_confirmation": True,
            },
        )

    def _allowed(self, observation_type: ObservationType) -> bool:
        if observation_type is ObservationType.DIRECT_OBSERVATION:
            return self.policy.extract_from_direct_observation
        if observation_type is ObservationType.REPORTED_CLAIM:
            return self.policy.extract_from_reported_claim
        if observation_type is ObservationType.INTERPRETATION:
            return self.policy.extract_from_interpretation
        if observation_type is ObservationType.SPECULATION:
            return self.policy.extract_from_speculation
        if observation_type is ObservationType.METADATA_STATEMENT:
            return self.policy.extract_from_metadata
        return False

    def _origin_for(self, observation_type: ObservationType) -> CandidateClaimOrigin:
        return {
            ObservationType.DIRECT_OBSERVATION: CandidateClaimOrigin.FROM_DIRECT_OBSERVATION,
            ObservationType.REPORTED_CLAIM: CandidateClaimOrigin.FROM_REPORTED_CLAIM,
            ObservationType.INTERPRETATION: CandidateClaimOrigin.FROM_INTERPRETATION,
            ObservationType.SPECULATION: CandidateClaimOrigin.FROM_SPECULATION,
            ObservationType.METADATA_STATEMENT: CandidateClaimOrigin.FROM_METADATA,
        }.get(observation_type, CandidateClaimOrigin.UNKNOWN)

    def _warnings_for(
        self,
        observation: ExtractedObservation,
        provenance: ProvenanceRecord | None,
    ) -> list[ClaimExtractionWarning]:
        related = {observation.id}
        warnings = [
            ClaimExtractionWarning(
                ClaimExtractionWarningType.EXTRACTION_NOT_CONFIRMATION,
                "Candidate claim extraction is not claim confirmation.",
                related,
            )
        ]
        type_warning = {
            ObservationType.DIRECT_OBSERVATION: (
                ClaimExtractionWarningType.DIRECT_OBSERVATION_CAUTION,
                "Direct observation can seed a candidate claim, but does not prove it.",
            ),
            ObservationType.REPORTED_CLAIM: (
                ClaimExtractionWarningType.REPORTED_CLAIM_NOT_VERIFIED,
                "Reported claim remains reported and unverified.",
            ),
            ObservationType.INTERPRETATION: (
                ClaimExtractionWarningType.INTERPRETATION_NOT_OBSERVATION,
                "Interpretation is not promoted to direct observation.",
            ),
            ObservationType.SPECULATION: (
                ClaimExtractionWarningType.SPECULATION_REMAINS_SPECULATION,
                "Speculative source span remains speculative.",
            ),
            ObservationType.METADATA_STATEMENT: (
                ClaimExtractionWarningType.METADATA_NOT_CLAIM_SUPPORT,
                "Metadata does not become claim support.",
            ),
        }.get(observation.observation_type)
        if type_warning:
            warnings.append(ClaimExtractionWarning(type_warning[0], type_warning[1], related))
        if provenance is None and self.policy.require_provenance_note:
            warnings.append(
                ClaimExtractionWarning(
                    ClaimExtractionWarningType.MISSING_PROVENANCE,
                    "Candidate claim has no attached provenance record.",
                    related,
                )
            )
        return warnings

    def _normalize_claim_text(self, text: str) -> str:
        return " ".join(text.strip().rstrip(".!?").split())

    def _canonical_topic(self, text: str) -> str:
        tokens = re.findall(r"[a-z0-9]+", text.casefold())
        stopwords = {"a", "an", "and", "as", "at", "because", "it", "of", "the", "that", "was"}
        filtered = [token for token in tokens if token not in stopwords]
        return "-".join(filtered[:6]) or "unknown"
