"""Build deterministic review bundles from sessions and dockets."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.models import (
    ClaimReviewDocket,
    EvidenceQualitySummary,
    ReviewBundle,
    ReviewBundleManifest,
    ReviewBundleSection,
    ReviewSession,
    SessionAuditTrail,
    SourceReviewDocket,
)
from roswell_uap_cortex.review_bundle_guardrails import ReviewBundleGuardrails


@dataclass(slots=True)
class ReviewBundleBuilder:
    """Compose review state into an exportable bundle without conclusions."""

    guardrails: ReviewBundleGuardrails = field(default_factory=ReviewBundleGuardrails)

    def build(
        self,
        session: ReviewSession,
        *,
        claim_dockets: list[ClaimReviewDocket] | None = None,
        source_dockets: list[SourceReviewDocket] | None = None,
        audit_trail: SessionAuditTrail | None = None,
    ) -> ReviewBundle:
        claim_dockets = claim_dockets or []
        source_dockets = source_dockets or []
        sections = [
            self._session_summary(session),
            self._active_focus(session),
            self._claim_dockets(claim_dockets),
            self._source_dockets(source_dockets),
            self._evidence_quality(claim_dockets, source_dockets),
            self._unresolved(session),
            self._deferred(session),
            self._uncertainty(session),
            self._contradictions(session),
            self._provenance(claim_dockets, source_dockets),
            self._audit_trail(audit_trail),
            self._limitations(),
        ]
        bundle_id = str(uuid5(NAMESPACE_URL, "review-bundle:" + session.session_id + ":" + "|".join(section.section_id for section in sections)))
        manifest = ReviewBundleManifest(
            bundle_id=bundle_id,
            section_counts={section.section_id: len(section.items) for section in sections},
            notes=["review bundle is exportable review state, not a final report"],
        )
        bundle = ReviewBundle(
            manifest=manifest,
            sections=sections,
            limitations=list(self._limitations().items),
        )
        bundle.warnings.extend(self.guardrails.check(bundle))
        return bundle

    def _session_summary(self, session: ReviewSession) -> ReviewBundleSection:
        return ReviewBundleSection(
            "session_summary",
            "Session Summary",
            [
                f"session_id:{session.session_id}",
                f"title:{session.title}",
                f"decisions:{len(session.decisions)}",
            ],
            {session.session_id},
        )

    def _active_focus(self, session: ReviewSession) -> ReviewBundleSection:
        focus = session.state.active_focus
        return ReviewBundleSection(
            "active_focus",
            "Active Focus",
            [
                f"query:{focus.query or 'none'}",
                f"focus_ids:{self._csv(focus.focus_ids)}",
                f"claim_topics:{self._csv(focus.claim_topics)}",
                f"source_ids:{self._csv(focus.source_ids)}",
            ],
            set(focus.focus_ids),
        )

    def _claim_dockets(self, dockets: list[ClaimReviewDocket]) -> ReviewBundleSection:
        items = []
        ids = set()
        for docket in sorted(dockets, key=lambda item: item.docket_id):
            ids.add(docket.docket_id)
            for item in docket.items:
                items.append(
                    f"{item.normalized_claim_id}:{item.canonical_topic}: support={len(item.support_summaries)} contradiction={len(item.contradiction_summaries)} uncertainty={len(item.uncertainty_summaries)}"
                )
        return ReviewBundleSection("claim_dockets", "Claim Review Dockets", items or ["none"], ids)

    def _source_dockets(self, dockets: list[SourceReviewDocket]) -> ReviewBundleSection:
        items = []
        ids = set()
        for docket in sorted(dockets, key=lambda item: item.docket_id):
            ids.add(docket.docket_id)
            for item in docket.items:
                items.append(f"{item.source_id}: risk={item.risk_score:.2f} reliability={item.reliability_score:.2f}")
        return ReviewBundleSection("source_dockets", "Source Review Dockets", items or ["none"], ids)

    def _evidence_quality(
        self,
        claim_dockets: list[ClaimReviewDocket],
        source_dockets: list[SourceReviewDocket],
    ) -> ReviewBundleSection:
        summaries: dict[str, EvidenceQualitySummary] = {}
        related_ids: set[str] = set()
        for docket in claim_dockets:
            for item in docket.items:
                for summary in item.quality_summaries:
                    summaries.setdefault(summary.evidence_id, summary)
                    related_ids.add(summary.evidence_id)
        for docket in source_dockets:
            for item in docket.items:
                for summary in item.quality_summaries:
                    summaries.setdefault(summary.evidence_id, summary)
                    related_ids.add(summary.evidence_id)

        items = [
            self._quality_line(summary)
            for summary in sorted(summaries.values(), key=lambda entry: entry.evidence_id)
        ]
        if items:
            items.append("boundary:evidence quality is review context, not claim confirmation or source truth")
        return ReviewBundleSection("evidence_quality", "Evidence Quality", items or ["none"], related_ids)

    def _quality_line(self, summary: EvidenceQualitySummary) -> str:
        weak = self._csv(set(summary.weak_dimensions))
        warnings = self._csv({warning.value for warning in summary.warning_types})
        return (
            f"evidence:{summary.evidence_id}: "
            f"label={summary.quality_label.value} "
            f"quality_score={summary.quality_score:.2f} "
            f"review_priority={summary.review_priority_score:.2f} "
            f"weak_dimensions={weak} "
            f"warnings={warnings}"
        )

    def _unresolved(self, session: ReviewSession) -> ReviewBundleSection:
        return ReviewBundleSection("unresolved", "Unresolved Items", sorted(session.state.unresolved_item_ids) or ["none"])

    def _deferred(self, session: ReviewSession) -> ReviewBundleSection:
        items = [f"{item.item_type}:{item.item_id}:{item.reason}" for item in session.state.deferred_items]
        return ReviewBundleSection("deferred", "Deferred Items", sorted(items) or ["none"])

    def _uncertainty(self, session: ReviewSession) -> ReviewBundleSection:
        return ReviewBundleSection("uncertainty", "Uncertainty Notes", sorted(session.state.uncertainty_notes) or ["none"])

    def _contradictions(self, session: ReviewSession) -> ReviewBundleSection:
        return ReviewBundleSection("contradictions", "Contradictions", sorted(session.state.contradiction_ids) or ["none"])

    def _provenance(
        self,
        claim_dockets: list[ClaimReviewDocket],
        source_dockets: list[SourceReviewDocket],
    ) -> ReviewBundleSection:
        refs: set[str] = set()
        for docket in claim_dockets:
            refs.update(citation.label or citation.provenance_id or citation.evidence_id or "uncited" for citation in docket.citations)
        for docket in source_dockets:
            refs.update(citation.label or citation.provenance_id or citation.evidence_id or "uncited" for citation in docket.citations)
        return ReviewBundleSection("provenance", "Provenance And Citations", sorted(refs) or ["missing"])

    def _audit_trail(self, trail: SessionAuditTrail | None) -> ReviewBundleSection:
        if not trail:
            return ReviewBundleSection("audit_trail", "Audit Trail", ["missing"])
        items = [f"{record.created_at.isoformat()}:{record.event_type}:{record.item_type or ''}:{record.item_id or ''}" for record in trail.records]
        return ReviewBundleSection("audit_trail", "Audit Trail", items or ["none"], {trail.session_id})

    def _limitations(self) -> ReviewBundleSection:
        return ReviewBundleSection(
            "limitations",
            "Limitations",
            [
                "Review bundles are not final reports.",
                "Review bundles do not confirm claims or reject sources.",
                "Review bundles preserve uncertainty, contradictions, provenance, and audit state for human inspection.",
            ],
        )

    def _csv(self, values: set[str]) -> str:
        return ", ".join(sorted(values)) if values else "none"
