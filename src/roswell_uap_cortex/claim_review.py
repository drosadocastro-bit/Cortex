"""Claim review docket construction."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.citations import CitationFormatter
from roswell_uap_cortex.review_priority import ReviewPriorityEngine
from roswell_uap_cortex.models import (
    ClaimEvaluationResult,
    ClaimEvaluationWarning,
    ClaimEvaluationWarningType,
    ClaimEvidenceAssessment,
    ClaimEvidenceAssessmentType,
    ClaimReviewDocket,
    ClaimReviewItem,
    ClaimReviewQueue,
    DiscourseCitation,
    EvidenceAssessmentSummary,
    EvidenceQualityAssessment,
    EvidenceQualitySummary,
    NormalizedClaim,
    ProvenanceRecord,
    ReviewRecommendation,
    ReviewRecommendationType,
    SourceLineageRecord,
)


@dataclass(slots=True)
class ClaimReviewEngine:
    """Build deterministic human-review dockets from claim evaluation output."""

    priority_engine: ReviewPriorityEngine = field(default_factory=ReviewPriorityEngine)
    citation_formatter: CitationFormatter = field(default_factory=CitationFormatter)

    def build_docket(
        self,
        normalized_claims: list[NormalizedClaim],
        evaluation: ClaimEvaluationResult,
        *,
        provenance_by_evidence_id: dict[str, ProvenanceRecord] | None = None,
        lineage_by_evidence_id: dict[str, SourceLineageRecord] | None = None,
        evidence_quality_by_evidence_id: dict[str, EvidenceQualityAssessment] | None = None,
        title: str = "Claim Review Docket",
    ) -> ClaimReviewDocket:
        provenance_by_evidence_id = provenance_by_evidence_id or {}
        lineage_by_evidence_id = lineage_by_evidence_id or {}
        evidence_quality_by_evidence_id = evidence_quality_by_evidence_id or {}
        assessments_by_claim = self._assessments_by_claim(evaluation.assessments)

        items = [
            self._item_for_claim(
                claim,
                assessments_by_claim.get(claim.normalized_claim_id, []),
                evidence_quality_by_evidence_id=evidence_quality_by_evidence_id,
            )
            for claim in sorted(normalized_claims, key=lambda claim: claim.canonical_key.value)
        ]
        citations = self._citations_for_items(items, provenance_by_evidence_id, lineage_by_evidence_id)
        recommendations = self._merge_recommendations([rec for item in items for rec in item.recommendations])
        docket_id = str(uuid5(NAMESPACE_URL, "claim-review:" + "|".join(item.canonical_topic for item in items)))
        return ClaimReviewDocket(
            docket_id=docket_id,
            title=title,
            items=items,
            citations=citations,
            warnings=list(evaluation.warnings),
            recommendations=recommendations,
            notes=[
                "claim review docket is deterministic and does not confirm or reject claims",
                "support, contradiction, uncertainty, and provenance remain separated",
            ],
        )

    def build_queue(self, dockets: list[ClaimReviewDocket]) -> ClaimReviewQueue:
        ordered = sorted(
            dockets,
            key=lambda docket: (
                -max((item.priority_score for item in docket.items), default=0.0),
                docket.title,
                docket.docket_id,
            ),
        )
        return ClaimReviewQueue(
            dockets=ordered,
            notes=["review queue ordering is deterministic and priority is not truth confidence"],
        )

    def _item_for_claim(
        self,
        claim: NormalizedClaim,
        assessments: list[ClaimEvidenceAssessment],
        *,
        evidence_quality_by_evidence_id: dict[str, EvidenceQualityAssessment],
    ) -> ClaimReviewItem:
        summaries = [self._summary(assessment) for assessment in assessments]
        quality_summaries = [
            self._quality_summary(quality)
            for evidence_id, quality in sorted(evidence_quality_by_evidence_id.items())
            if evidence_id in {summary.evidence_id for summary in summaries}
        ]
        support = [summary for summary in summaries if summary.assessment_type is ClaimEvidenceAssessmentType.POSSIBLE_SUPPORT]
        contradiction = [
            summary
            for summary in summaries
            if summary.assessment_type
            in {ClaimEvidenceAssessmentType.POSSIBLE_CONTRADICTION, ClaimEvidenceAssessmentType.NEEDS_REVIEW}
        ]
        uncertainty = [
            summary
            for summary in summaries
            if summary.assessment_type in {ClaimEvidenceAssessmentType.UNCERTAIN, ClaimEvidenceAssessmentType.NEEDS_REVIEW}
            or summary.uncertainty_score > 0
        ]
        irrelevant = {
            summary.evidence_id
            for summary in summaries
            if summary.assessment_type is ClaimEvidenceAssessmentType.IRRELEVANT
        }
        warning_types = sorted(
            {warning for summary in summaries for warning in summary.warning_types},
            key=lambda warning: warning.value,
        )
        item = ClaimReviewItem(
            normalized_claim_id=claim.normalized_claim_id,
            canonical_topic=claim.canonical_key.value,
            canonical_text=claim.canonical_text,
            support_summaries=support,
            contradiction_summaries=contradiction,
            uncertainty_summaries=uncertainty,
            quality_summaries=quality_summaries,
            irrelevant_evidence_ids=irrelevant,
            provenance_ids={pid for summary in summaries for pid in summary.provenance_ids} | set(claim.provenance_ids),
            lineage_ids={summary.lineage_id for summary in summaries if summary.lineage_id} | set(claim.lineage_ids),
            warning_types=warning_types,
            recommendations=self._recommendations(warning_types, support, contradiction, uncertainty),
            notes=["review item only; no claim mutation or truth decision"],
            unsupported=claim.unsupported,
            confidence=claim.confidence,
        )
        priority, score, reasons = self.priority_engine.score(item)
        item.priority = priority
        item.priority_score = score
        item.notes.extend(f"priority:{reason}" for reason in reasons)
        return item

    def _quality_summary(self, assessment: EvidenceQualityAssessment) -> EvidenceQualitySummary:
        dimensions = assessment.dimension_scores
        weak_dimensions = [
            name
            for name, score in [
                ("provenance_completeness", dimensions.provenance_completeness),
                ("lineage_clarity", dimensions.lineage_clarity),
                ("source_transparency", dimensions.source_transparency),
                ("observation_directness", dimensions.observation_directness),
                ("contamination_resistance", dimensions.contamination_resistance),
                ("contradiction_stability", dimensions.contradiction_stability),
                ("temporal_specificity", dimensions.temporal_specificity),
                ("extraction_confidence", dimensions.extraction_confidence),
            ]
            if score < 0.55
        ]
        warning_types = sorted(
            {warning.warning_type for warning in assessment.warnings},
            key=lambda warning: warning.value,
        )
        return EvidenceQualitySummary(
            evidence_id=assessment.evidence_id,
            quality_label=assessment.quality_label,
            quality_score=assessment.quality_score,
            review_priority_score=assessment.review_priority_score,
            weak_dimensions=weak_dimensions,
            warning_types=warning_types,
            reason_codes=list(assessment.reason_codes),
        )

    def _summary(self, assessment: ClaimEvidenceAssessment) -> EvidenceAssessmentSummary:
        warning_types = sorted(
            {warning.warning_type for warning in assessment.warnings},
            key=lambda warning: warning.value,
        )
        return EvidenceAssessmentSummary(
            evidence_id=assessment.evidence_id,
            assessment_type=assessment.assessment_type,
            support_score=assessment.support_score,
            contradiction_score=assessment.contradiction_score,
            uncertainty_score=assessment.uncertainty_score,
            independence_score=assessment.independence_score,
            provenance_ids=set(assessment.provenance_ids),
            lineage_id=assessment.lineage_id,
            reason_codes=list(assessment.reason_codes),
            warning_types=warning_types,
        )

    def _recommendations(
        self,
        warning_types: list[ClaimEvaluationWarningType],
        support: list[EvidenceAssessmentSummary],
        contradiction: list[EvidenceAssessmentSummary],
        uncertainty: list[EvidenceAssessmentSummary],
    ) -> list[ReviewRecommendation]:
        recommendations = [
            ReviewRecommendation(
                ReviewRecommendationType.PRESERVE_UNSUPPORTED,
                "Keep the claim in review state; assessment is not confirmation.",
            )
        ]
        if contradiction:
            recommendations.append(
                ReviewRecommendation(
                    ReviewRecommendationType.REVIEW_CONTRADICTION,
                    "Review contradiction pressure without treating it as disproof.",
                    {summary.evidence_id for summary in contradiction},
                )
            )
        if ClaimEvaluationWarningType.MISSING_PROVENANCE in warning_types or any(not s.provenance_ids for s in uncertainty):
            recommendations.append(
                ReviewRecommendation(
                    ReviewRecommendationType.VERIFY_PROVENANCE,
                    "Verify missing or weak provenance before relying on this assessment.",
                    {summary.evidence_id for summary in uncertainty if not summary.provenance_ids},
                )
            )
        if ClaimEvaluationWarningType.SAME_LINEAGE_NOT_CORROBORATION in warning_types:
            recommendations.append(
                ReviewRecommendation(
                    ReviewRecommendationType.CHECK_SOURCE_INDEPENDENCE,
                    "Check source independence; same-lineage repetition is not corroboration.",
                )
            )
        if (
            ClaimEvaluationWarningType.SPECULATIVE_EVIDENCE_CAUTION in warning_types
            or ClaimEvaluationWarningType.REPORTED_CLAIM_CAUTION in warning_types
        ):
            recommendations.append(
                ReviewRecommendation(
                    ReviewRecommendationType.REVIEW_SPECULATIVE_OR_REPORTED,
                    "Keep speculative or reported evidence labeled during review.",
                )
            )
        if support and contradiction:
            recommendations.append(
                ReviewRecommendation(
                    ReviewRecommendationType.HUMAN_REVIEW,
                    "Human review required because support and contradiction signals both appear.",
                )
            )
        return self._merge_recommendations(recommendations)

    def _citations_for_items(
        self,
        items: list[ClaimReviewItem],
        provenance_by_evidence_id: dict[str, ProvenanceRecord],
        lineage_by_evidence_id: dict[str, SourceLineageRecord],
    ) -> list[DiscourseCitation]:
        citations: list[DiscourseCitation] = []
        for item in items:
            summaries = item.support_summaries + item.contradiction_summaries + item.uncertainty_summaries
            for summary in sorted(summaries, key=lambda entry: entry.evidence_id):
                citations.append(
                    self.citation_formatter.citation_for(
                        summary.evidence_id,
                        provenance=provenance_by_evidence_id.get(summary.evidence_id),
                        lineage=lineage_by_evidence_id.get(summary.evidence_id),
                    )
                )
        return self.citation_formatter.merge(citations)

    def _assessments_by_claim(
        self,
        assessments: list[ClaimEvidenceAssessment],
    ) -> dict[str, list[ClaimEvidenceAssessment]]:
        grouped: dict[str, list[ClaimEvidenceAssessment]] = {}
        for assessment in sorted(assessments, key=lambda item: (item.normalized_claim_id, item.evidence_id)):
            grouped.setdefault(assessment.normalized_claim_id, []).append(assessment)
        return grouped

    def _merge_recommendations(self, recommendations: list[ReviewRecommendation]) -> list[ReviewRecommendation]:
        merged: dict[ReviewRecommendationType, ReviewRecommendation] = {}
        for recommendation in recommendations:
            existing = merged.get(recommendation.recommendation_type)
            if not existing:
                merged[recommendation.recommendation_type] = recommendation
            else:
                existing.related_ids.update(recommendation.related_ids)
        return [merged[key] for key in sorted(merged, key=lambda item: item.value)]
