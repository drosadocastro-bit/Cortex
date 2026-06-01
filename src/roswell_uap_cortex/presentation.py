"""Read-only workflow view models for future UI and demo presentation."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.models import (
    BundlePreviewView,
    ClaimReviewCardView,
    ClaimReviewDocket,
    PresentationWarning,
    ReviewBundle,
    ReviewDashboardView,
    ReviewInfluenceResult,
    ReviewSession,
    SessionAuditTrail,
    SessionTimelineView,
    SourceReviewDocket,
    SourceReviewRecommendationType,
    SourceReviewCardView,
    WorkflowStageView,
)
from roswell_uap_cortex.presentation_guardrails import PresentationGuardrails


@dataclass(slots=True)
class PresentationBuilder:
    """Build deterministic display contracts without mutating workflow state."""

    guardrails: PresentationGuardrails = field(default_factory=PresentationGuardrails)

    def build_dashboard(
        self,
        *,
        title: str,
        synthetic_only: bool,
        claim_dockets: list[ClaimReviewDocket] | None = None,
        source_dockets: list[SourceReviewDocket] | None = None,
        session: ReviewSession | None = None,
        audit_trail: SessionAuditTrail | None = None,
        bundle: ReviewBundle | None = None,
        review_influence: ReviewInfluenceResult | None = None,
        notes: list[str] | None = None,
    ) -> ReviewDashboardView:
        claim_dockets = claim_dockets or []
        source_dockets = source_dockets or []
        notes = notes or []

        dashboard = ReviewDashboardView(
            title=title,
            synthetic_only=synthetic_only,
            stages=self._stages(claim_dockets, source_dockets, session, bundle),
            claim_cards=self._claim_cards(claim_dockets),
            source_cards=self._source_cards(source_dockets),
            session_timeline=self._session_timeline(session, audit_trail),
            bundle_preview=self._bundle_preview(bundle),
            uncertainty_notes=sorted(set(notes)),
            limitations=list(bundle.limitations) if bundle else [],
        )
        self._merge_session_state(dashboard, session)
        self._merge_influence(dashboard, review_influence)
        self._collect_provenance(dashboard, claim_dockets, source_dockets, bundle)
        return self.guardrails.apply(dashboard)

    def _stages(
        self,
        claim_dockets: list[ClaimReviewDocket],
        source_dockets: list[SourceReviewDocket],
        session: ReviewSession | None,
        bundle: ReviewBundle | None,
    ) -> list[WorkflowStageView]:
        return [
            WorkflowStageView("claim_review", "Claim Review", summary=f"{sum(len(docket.items) for docket in claim_dockets)} claim cards"),
            WorkflowStageView("source_review", "Source Review", summary=f"{sum(len(docket.items) for docket in source_dockets)} source cards"),
            WorkflowStageView("review_session", "Review Session", status="available" if session else "missing", summary="workflow annotations only"),
            WorkflowStageView("bundle_preview", "Bundle Preview", status="available" if bundle else "missing", summary="not a final report"),
        ]

    def _claim_cards(self, dockets: list[ClaimReviewDocket]) -> list[ClaimReviewCardView]:
        cards: list[ClaimReviewCardView] = []
        for docket in sorted(dockets, key=lambda item: item.docket_id):
            for item in sorted(docket.items, key=lambda value: value.normalized_claim_id):
                warnings = [
                    PresentationWarning("unsupported_visible", "Unsupported claim remains visibly unsupported.", {item.normalized_claim_id})
                ] if item.unsupported else []
                if item.contradiction_summaries:
                    warnings.append(PresentationWarning("contradiction_visible", "Contradiction summaries remain visible.", {item.normalized_claim_id}))
                cards.append(
                    ClaimReviewCardView(
                        claim_id=item.normalized_claim_id,
                        canonical_topic=item.canonical_topic,
                        text=item.canonical_text,
                        priority=item.priority.value,
                        priority_score=item.priority_score,
                        unsupported=item.unsupported,
                        support_count=len(item.support_summaries),
                        contradiction_count=len(item.contradiction_summaries),
                        uncertainty_count=len(item.uncertainty_summaries),
                        provenance_ids=set(item.provenance_ids),
                        lineage_ids=set(item.lineage_ids),
                        warnings=warnings,
                        notes=sorted(set(item.notes + ["display priority is not truth confidence"])),
                    )
                )
        return cards

    def _source_cards(self, dockets: list[SourceReviewDocket]) -> list[SourceReviewCardView]:
        cards: list[SourceReviewCardView] = []
        for docket in sorted(dockets, key=lambda item: item.docket_id):
            for item in sorted(docket.items, key=lambda value: value.source_id):
                warnings = [
                    PresentationWarning("source_risk_not_rejection", "Source review risk is not source rejection.", {item.source_id})
                ] if item.risk_score > 0.0 or item.risk_signals else []
                if any(
                    recommendation.recommendation_type is SourceReviewRecommendationType.VERIFY_PROVENANCE
                    for recommendation in item.recommendations
                ):
                    warnings.append(PresentationWarning("provenance_gap_visible", "Source provenance gap remains visible.", {item.source_id}))
                cards.append(
                    SourceReviewCardView(
                        source_id=item.source_id,
                        priority=item.priority.value,
                        priority_score=item.priority_score,
                        risk_score=item.risk_score,
                        reliability_score=item.reliability_score,
                        evidence_count=len(item.evidence_ids),
                        provenance_ids=set(item.provenance_ids),
                        lineage_ids=set(item.lineage_ids),
                        contamination_flags={flag.value for flag in item.contamination_flags},
                        warnings=warnings,
                        notes=sorted(set(item.notes + ["source review is not source acceptance or rejection"])),
                    )
                )
        return cards

    def _session_timeline(
        self,
        session: ReviewSession | None,
        audit_trail: SessionAuditTrail | None,
    ) -> SessionTimelineView | None:
        if session is None:
            return None
        events = []
        if audit_trail:
            events.extend(
                f"{record.created_at.isoformat()}:{record.event_type}:{record.item_type or ''}:{record.item_id or ''}"
                for record in sorted(audit_trail.records, key=lambda item: item.record_id)
            )
        return SessionTimelineView(
            session_id=session.session_id,
            events=sorted(events),
            reviewed_ids={item.item_id for item in session.state.reviewed_items},
            deferred_ids={item.item_id for item in session.state.deferred_items},
            unresolved_ids=set(session.state.unresolved_item_ids),
            warnings=[PresentationWarning("audit_not_evidence", "Audit timeline is workflow history, not evidence.", {session.session_id})],
        )

    def _bundle_preview(self, bundle: ReviewBundle | None) -> BundlePreviewView | None:
        if bundle is None:
            return None
        return BundlePreviewView(
            bundle_id=bundle.manifest.bundle_id,
            section_titles=[section.title for section in sorted(bundle.sections, key=lambda item: item.section_id)],
            limitations=list(bundle.limitations),
            warnings=[
                PresentationWarning(warning.warning_type, warning.message, set(warning.related_ids))
                for warning in bundle.warnings
            ],
        )

    def _merge_session_state(self, dashboard: ReviewDashboardView, session: ReviewSession | None) -> None:
        if session is None:
            return
        dashboard.unresolved_ids.update(session.state.unresolved_item_ids)
        dashboard.deferred_ids.update(item.item_id for item in session.state.deferred_items)
        dashboard.contradiction_ids.update(session.state.contradiction_ids)
        dashboard.uncertainty_notes = sorted(set(dashboard.uncertainty_notes + session.state.uncertainty_notes))

    def _merge_influence(self, dashboard: ReviewDashboardView, influence: ReviewInfluenceResult | None) -> None:
        if influence is None:
            return
        dashboard.unresolved_ids.update(influence.unresolved_ids)
        dashboard.deferred_ids.update(influence.deferred_ids)
        dashboard.contradiction_ids.update(influence.contradiction_ids)
        dashboard.uncertainty_notes = sorted(set(dashboard.uncertainty_notes + influence.uncertainty_notes + influence.discourse_annotations))
        dashboard.warnings.extend(
            PresentationWarning(warning.warning_type.value, warning.message, set(warning.related_ids))
            for warning in influence.warnings
        )

    def _collect_provenance(
        self,
        dashboard: ReviewDashboardView,
        claim_dockets: list[ClaimReviewDocket],
        source_dockets: list[SourceReviewDocket],
        bundle: ReviewBundle | None,
    ) -> None:
        for card in dashboard.claim_cards:
            dashboard.provenance_refs.update(card.provenance_ids)
        for card in dashboard.source_cards:
            dashboard.provenance_refs.update(card.provenance_ids)
        for docket in claim_dockets:
            dashboard.provenance_refs.update(citation.label or citation.provenance_id or citation.evidence_id or "uncited" for citation in docket.citations)
        for docket in source_dockets:
            dashboard.provenance_refs.update(citation.label or citation.provenance_id or citation.evidence_id or "uncited" for citation in docket.citations)
        if bundle:
            for section in bundle.sections:
                if section.section_id == "provenance":
                    dashboard.provenance_refs.update(item for item in section.items if item != "missing")
