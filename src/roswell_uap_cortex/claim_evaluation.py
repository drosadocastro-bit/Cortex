"""Deterministic claim evidence assessment."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.claim_contradiction_evaluator import ClaimContradictionEvaluator
from roswell_uap_cortex.claim_evaluation_guardrails import ClaimEvidenceGuardrails
from roswell_uap_cortex.independence import EvidenceIndependenceInput, IndependenceScorer
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    ClaimContradictionSignal,
    ClaimEvaluationPolicy,
    ClaimEvaluationResult,
    ClaimEvidenceAssessment,
    ClaimEvidenceAssessmentType,
    ClaimSupportSignal,
    ClaimUncertaintySignal,
    EvidenceItem,
    ExtractedObservation,
    NormalizedClaim,
    ObservationType,
    ProvenanceRecord,
    SourceLineageRecord,
)
from roswell_uap_cortex.text import SimpleTokenizer, overlap_score


@dataclass(slots=True)
class ClaimEvidenceEvaluator:
    """Assess possible support/contradiction signals without truth decisions."""

    policy: ClaimEvaluationPolicy = field(default_factory=ClaimEvaluationPolicy)
    tokenizer: SimpleTokenizer = field(default_factory=SimpleTokenizer)
    contradiction_evaluator: ClaimContradictionEvaluator = field(default_factory=ClaimContradictionEvaluator)
    guardrails: ClaimEvidenceGuardrails = field(default_factory=ClaimEvidenceGuardrails)
    independence_scorer: IndependenceScorer = field(default_factory=IndependenceScorer)

    def evaluate(
        self,
        normalized_claims: list[NormalizedClaim],
        evidence_items: list[EvidenceItem],
        *,
        observations_by_id: dict[str, ExtractedObservation] | None = None,
        provenance_by_evidence_id: dict[str, ProvenanceRecord] | None = None,
        lineage_by_evidence_id: dict[str, SourceLineageRecord] | None = None,
    ) -> ClaimEvaluationResult:
        observations_by_id = observations_by_id or {}
        provenance_by_evidence_id = provenance_by_evidence_id or {}
        lineage_by_evidence_id = lineage_by_evidence_id or {}
        result = ClaimEvaluationResult(notes=["deterministic claim evidence assessment; no truth decision created"])

        for normalized in normalized_claims:
            for evidence in evidence_items:
                assessment = self._assess(
                    normalized,
                    evidence,
                    observations_by_id=observations_by_id,
                    provenance=provenance_by_evidence_id.get(evidence.id),
                    lineage=lineage_by_evidence_id.get(evidence.id),
                )
                result.assessments.append(assessment)
                result.warnings.extend(assessment.warnings)
                if assessment.support_score > 0:
                    result.support_signals.append(
                        ClaimSupportSignal(evidence.id, assessment.support_score, list(assessment.reason_codes))
                    )
                if assessment.contradiction_score > 0:
                    result.contradiction_signals.append(
                        ClaimContradictionSignal(evidence.id, assessment.contradiction_score, list(assessment.reason_codes))
                    )
                if assessment.uncertainty_score > 0:
                    result.uncertainty_signals.append(
                        ClaimUncertaintySignal(evidence.id, assessment.uncertainty_score, list(assessment.reason_codes))
                    )
        return result

    def _assess(
        self,
        normalized: NormalizedClaim,
        evidence: EvidenceItem,
        *,
        observations_by_id: dict[str, ExtractedObservation],
        provenance: ProvenanceRecord | None,
        lineage: SourceLineageRecord | None,
    ) -> ClaimEvidenceAssessment:
        claim_tokens = set(normalized.canonical_key.token_fingerprint)
        evidence_tokens = self.tokenizer.tokenize(evidence.summary)
        lexical = overlap_score(claim_tokens, evidence_tokens)
        reasons: list[str] = []
        if lexical > 0:
            reasons.append("lexical_overlap")

        support_score = lexical
        contradiction_score, contradiction_reasons = self.contradiction_evaluator.contradiction_score(normalized, evidence)
        reasons.extend(contradiction_reasons)

        observation_type = evidence.metadata.get("observation_type", ObservationType.UNKNOWN.value)
        uncertainty_score = 0.0
        if not provenance:
            uncertainty_score += 0.35
            reasons.append("missing_provenance")
        if observation_type in {
            ObservationType.SPECULATION.value,
            ObservationType.REPORTED_CLAIM.value,
            ObservationType.METADATA_STATEMENT.value,
            ObservationType.UNKNOWN.value,
        }:
            uncertainty_score += 0.25
            reasons.append(f"observation_type:{observation_type}")

        if observation_type == ObservationType.SPECULATION.value:
            support_score = min(support_score, self.policy.speculative_support_cap)
        if observation_type == ObservationType.REPORTED_CLAIM.value:
            support_score = min(support_score, self.policy.reported_support_cap)
        if observation_type == ObservationType.METADATA_STATEMENT.value:
            support_score = min(support_score, self.policy.metadata_support_cap)

        same_lineage = bool(lineage and lineage.lineage_id in normalized.lineage_ids)
        if same_lineage:
            support_score *= 0.45
            reasons.append("same_lineage_downgraded")

        independence_score = self.independence_scorer.score_group(
            [
                EvidenceIndependenceInput(
                    source_id=evidence.source_id,
                    lineage_id=None if lineage is None else lineage.lineage_id,
                    source_kind=evidence.evidence_type,
                )
            ]
        )

        support_score = _clamp(support_score)
        contradiction_score = _clamp(contradiction_score)
        uncertainty_score = _clamp(uncertainty_score)
        needs_review = (
            support_score >= self.policy.review_threshold
            and contradiction_score >= self.policy.review_threshold
        )

        assessment_type = self._assessment_type(support_score, contradiction_score, uncertainty_score, needs_review)
        warnings = self.guardrails.warnings_for(
            evidence=evidence,
            provenance_visible=provenance is not None,
            same_lineage=same_lineage,
            needs_review=needs_review,
        )
        observation_id = evidence.metadata.get("observation_id")
        return ClaimEvidenceAssessment(
            normalized_claim_id=normalized.normalized_claim_id,
            evidence_id=evidence.id,
            observation_id=observation_id if isinstance(observation_id, str) else None,
            provenance_ids={provenance.id} if provenance else set(),
            lineage_id=None if lineage is None else lineage.lineage_id,
            support_score=support_score,
            contradiction_score=contradiction_score,
            uncertainty_score=uncertainty_score,
            independence_score=_clamp(independence_score),
            assessment_type=assessment_type,
            reason_codes=sorted(set(reasons)),
            warnings=warnings,
        )

    def _assessment_type(
        self,
        support_score: float,
        contradiction_score: float,
        uncertainty_score: float,
        needs_review: bool,
    ) -> ClaimEvidenceAssessmentType:
        if needs_review:
            return ClaimEvidenceAssessmentType.NEEDS_REVIEW
        if contradiction_score >= self.policy.contradiction_threshold:
            return ClaimEvidenceAssessmentType.POSSIBLE_CONTRADICTION
        if support_score >= self.policy.support_threshold:
            return ClaimEvidenceAssessmentType.POSSIBLE_SUPPORT
        if uncertainty_score > 0:
            return ClaimEvidenceAssessmentType.UNCERTAIN
        return ClaimEvidenceAssessmentType.IRRELEVANT
