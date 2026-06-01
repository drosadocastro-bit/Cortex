"""Bounded influence contract from review workflow to downstream context."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ClaimReviewDocket,
    ClaimReviewItem,
    ReviewDecisionType,
    ReviewInfluenceResult,
    ReviewInfluenceScope,
    ReviewInfluenceWarning,
    ReviewInfluenceWarningType,
    ReviewPriority,
    ReviewSession,
    ReviewStateSignal,
    SourceReviewDocket,
    SourceReviewRecommendationType,
)


@dataclass(slots=True)
class ReviewInfluencePolicy:
    """Convert review workflow state into hints, never evidentiary weight."""

    def evaluate(
        self,
        session: ReviewSession,
        *,
        claim_dockets: list[ClaimReviewDocket] | None = None,
        source_dockets: list[SourceReviewDocket] | None = None,
    ) -> ReviewInfluenceResult:
        claim_dockets = claim_dockets or []
        source_dockets = source_dockets or []
        result = ReviewInfluenceResult()

        self._active_focus(session, result)
        self._review_decisions(session, result)
        self._claim_dockets(claim_dockets, result)
        self._source_dockets(source_dockets, result)
        self._session_state(session, result)
        self._boundary_warnings(result)
        self._dedupe(result)
        return result

    def _active_focus(self, session: ReviewSession, result: ReviewInfluenceResult) -> None:
        focus = session.state.active_focus
        for item_id in sorted(focus.focus_ids | focus.evidence_ids | focus.source_ids):
            result.prioritized_ids.add(item_id)
            result.signals.append(
                ReviewStateSignal(
                    signal_type="active_focus",
                    item_id=item_id,
                    item_type="review_focus",
                    allowed_scopes={
                        ReviewInfluenceScope.ATTENTION,
                        ReviewInfluenceScope.CONTEXT,
                        ReviewInfluenceScope.DISCOURSE,
                    },
                    priority=0.7,
                    notes=["active focus may prioritize context but cannot change truth state"],
                )
            )
        if focus.query:
            result.discourse_annotations.append(f"active review focus query: {focus.query}")

    def _review_decisions(self, session: ReviewSession, result: ReviewInfluenceResult) -> None:
        for decision in sorted(session.decisions, key=lambda item: item.decision_id):
            result.signals.append(
                ReviewStateSignal(
                    signal_type=f"decision:{decision.decision_type.value}",
                    item_id=decision.item_id,
                    item_type=decision.item_type,
                    allowed_scopes={ReviewInfluenceScope.ATTENTION, ReviewInfluenceScope.DISCOURSE},
                    priority=0.4,
                    notes=list(decision.notes),
                )
            )
            if decision.decision_type is ReviewDecisionType.REVIEWED:
                result.prioritized_ids.add(decision.item_id)
                result.discourse_annotations.append(
                    f"{decision.item_type}:{decision.item_id} was reviewed as workflow annotation only"
                )
                result.warnings.append(
                    ReviewInfluenceWarning(
                        ReviewInfluenceWarningType.REVIEWED_NOT_CONFIRMED,
                        "reviewed items are not confirmed claims or accepted sources",
                        {decision.item_id},
                    )
                )
            elif decision.decision_type is ReviewDecisionType.KEEP_UNRESOLVED:
                result.unresolved_ids.add(decision.item_id)
                result.must_include_ids.add(decision.item_id)
            elif decision.decision_type in {
                ReviewDecisionType.DEFERRED,
                ReviewDecisionType.REQUEST_MORE_PROVENANCE,
                ReviewDecisionType.REQUEST_SOURCE_REVIEW,
            }:
                result.deferred_ids.add(decision.item_id)
                result.unresolved_ids.add(decision.item_id)
                if decision.decision_type is ReviewDecisionType.REQUEST_MORE_PROVENANCE:
                    result.provenance_gap_ids.add(decision.item_id)
                if decision.decision_type is ReviewDecisionType.REQUEST_SOURCE_REVIEW:
                    result.source_review_warning_ids.add(decision.item_id)
                result.warnings.append(
                    ReviewInfluenceWarning(
                        ReviewInfluenceWarningType.DEFERRED_NOT_ERASED,
                        "deferred review items remain unresolved and must not be erased",
                        {decision.item_id},
                    )
                )

    def _claim_dockets(self, dockets: list[ClaimReviewDocket], result: ReviewInfluenceResult) -> None:
        for docket in sorted(dockets, key=lambda item: item.docket_id):
            for item in sorted(docket.items, key=lambda value: value.normalized_claim_id):
                result.prioritized_ids.add(item.normalized_claim_id)
                result.signals.append(
                    ReviewStateSignal(
                        signal_type="claim_review_priority",
                        item_id=item.normalized_claim_id,
                        item_type="claim_review_item",
                        allowed_scopes={ReviewInfluenceScope.ATTENTION, ReviewInfluenceScope.CONTEXT},
                        priority=item.priority_score,
                        notes=[f"priority:{item.priority.value}"],
                    )
                )
                if self._is_high_priority(item):
                    result.must_include_ids.add(item.normalized_claim_id)
                if item.unsupported:
                    result.unresolved_ids.add(item.normalized_claim_id)
                    result.uncertainty_notes.append(
                        f"claim {item.normalized_claim_id} remains unsupported in review workflow"
                    )
                if item.contradiction_summaries:
                    result.contradiction_ids.add(item.normalized_claim_id)
                    result.unresolved_ids.add(item.normalized_claim_id)
                    result.must_include_ids.add(item.normalized_claim_id)
                    result.uncertainty_notes.append(
                        f"claim {item.normalized_claim_id} has contradiction summaries visible for review"
                    )
                if not item.provenance_ids:
                    result.provenance_gap_ids.add(item.normalized_claim_id)

    def _source_dockets(self, dockets: list[SourceReviewDocket], result: ReviewInfluenceResult) -> None:
        for docket in sorted(dockets, key=lambda item: item.docket_id):
            for item in sorted(docket.items, key=lambda value: value.source_id):
                result.prioritized_ids.add(item.source_id)
                result.signals.append(
                    ReviewStateSignal(
                        signal_type="source_review_risk",
                        item_id=item.source_id,
                        item_type="source_review_item",
                        allowed_scopes={ReviewInfluenceScope.ATTENTION, ReviewInfluenceScope.DISCOURSE},
                        priority=max(item.priority_score, item.risk_score),
                        notes=[f"risk:{item.risk_score:.2f}", f"reliability:{item.reliability_score:.2f}"],
                    )
                )
                if item.risk_score > 0.0 or item.risk_signals or item.contamination_flags:
                    result.source_review_warning_ids.add(item.source_id)
                    result.uncertainty_notes.append(
                        f"source {item.source_id} has review warnings; this is not source rejection"
                    )
                if not item.provenance_ids:
                    result.provenance_gap_ids.add(item.source_id)
                if any(
                    recommendation.recommendation_type is SourceReviewRecommendationType.VERIFY_PROVENANCE
                    for recommendation in item.recommendations
                ):
                    result.provenance_gap_ids.add(item.source_id)

    def _session_state(self, session: ReviewSession, result: ReviewInfluenceResult) -> None:
        result.unresolved_ids.update(session.state.unresolved_item_ids)
        result.must_include_ids.update(session.state.unresolved_item_ids)
        result.contradiction_ids.update(session.state.contradiction_ids)
        for item in session.state.deferred_items:
            result.deferred_ids.add(item.item_id)
            result.unresolved_ids.add(item.item_id)
        for note in sorted(session.state.uncertainty_notes):
            result.uncertainty_notes.append(f"session uncertainty: {note}")

    def _boundary_warnings(self, result: ReviewInfluenceResult) -> None:
        result.warnings.append(
            ReviewInfluenceWarning(
                ReviewInfluenceWarningType.REVIEW_STATE_NOT_TRUTH,
                "review workflow state may guide attention, context, and discourse only",
                set(result.prioritized_ids | result.unresolved_ids),
            )
        )
        if result.prioritized_ids:
            result.warnings.append(
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.PRIORITY_NOT_CONFIDENCE,
                    "review priority changes ordering only; it is not confidence",
                    set(result.prioritized_ids),
                )
            )
        if result.source_review_warning_ids:
            result.warnings.append(
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.SOURCE_RISK_NOT_REJECTION,
                    "source review risk is not source rejection",
                    set(result.source_review_warning_ids),
                )
            )
        if result.provenance_gap_ids:
            result.warnings.append(
                ReviewInfluenceWarning(
                    ReviewInfluenceWarningType.PROVENANCE_GAP_VISIBLE,
                    "provenance gaps remain visible for downstream review",
                    set(result.provenance_gap_ids),
                )
            )

    def _dedupe(self, result: ReviewInfluenceResult) -> None:
        result.uncertainty_notes = sorted(set(result.uncertainty_notes))
        result.discourse_annotations = sorted(set(result.discourse_annotations))
        warning_by_key = {
            (warning.warning_type.value, warning.message, tuple(sorted(warning.related_ids))): warning
            for warning in result.warnings
        }
        result.warnings = [warning_by_key[key] for key in sorted(warning_by_key)]
        signal_by_key = {
            (signal.signal_type, signal.item_type, signal.item_id): signal
            for signal in result.signals
        }
        result.signals = [signal_by_key[key] for key in sorted(signal_by_key)]

    def _is_high_priority(self, item: ClaimReviewItem) -> bool:
        return item.priority in {ReviewPriority.HIGH, ReviewPriority.URGENT}
