"""Working-memory construction for bounded review sessions."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ActivatedContext,
    ClaimReviewDocket,
    DiscourseResponse,
    ReasoningOutput,
    ReviewFocus,
    ReviewSessionState,
    SourceReviewDocket,
)


@dataclass(slots=True)
class WorkingMemoryEngine:
    """Build active review state without mutating source records."""

    def build_state(
        self,
        *,
        query: str = "",
        claim_dockets: list[ClaimReviewDocket] | None = None,
        source_dockets: list[SourceReviewDocket] | None = None,
        activated_context: ActivatedContext | None = None,
        reasoning_output: ReasoningOutput | None = None,
        discourse_response: DiscourseResponse | None = None,
    ) -> ReviewSessionState:
        claim_dockets = claim_dockets or []
        source_dockets = source_dockets or []
        focus = ReviewFocus(query=query)
        state = ReviewSessionState(active_focus=focus)

        for docket in sorted(claim_dockets, key=lambda item: item.docket_id):
            state.active_claim_docket_ids.add(docket.docket_id)
            for item in docket.items:
                focus.focus_ids.add(item.normalized_claim_id)
                focus.claim_topics.add(item.canonical_topic)
                focus.evidence_ids.update(summary.evidence_id for summary in item.support_summaries)
                focus.evidence_ids.update(summary.evidence_id for summary in item.contradiction_summaries)
                if item.contradiction_summaries:
                    state.contradiction_ids.add(item.normalized_claim_id)
                    state.unresolved_item_ids.add(item.normalized_claim_id)
                if item.uncertainty_summaries:
                    state.unresolved_item_ids.add(item.normalized_claim_id)
                    state.uncertainty_notes.append(f"claim:{item.canonical_topic}:uncertainty_visible")

        for docket in sorted(source_dockets, key=lambda item: item.docket_id):
            state.active_source_docket_ids.add(docket.docket_id)
            for item in docket.items:
                focus.focus_ids.add(item.source_id)
                focus.source_ids.add(item.source_id)
                focus.evidence_ids.update(item.evidence_ids)
                if item.risk_signals:
                    state.unresolved_item_ids.add(item.source_id)
                    state.uncertainty_notes.append(f"source:{item.source_id}:risk_visible")

        if activated_context:
            state.active_context_ids.update(activated_context.activated_memory_ids)
            state.active_context_ids.update(activated_context.activated_claim_ids)
            state.active_context_ids.update(activated_context.activated_evidence_ids)
            state.active_context_ids.update(activated_context.activated_entity_ids)
            state.uncertainty_notes.extend(sorted(activated_context.uncertainty_notes))

        if reasoning_output:
            state.active_context_ids.update(reasoning_output.supporting_context_ids)
            state.active_context_ids.update(reasoning_output.contested_context_ids)
            state.contradiction_ids.update(reasoning_output.contested_context_ids)
            state.unresolved_item_ids.update(reasoning_output.contested_context_ids)
            state.uncertainty_notes.extend(note.note for note in reasoning_output.uncertainty_notes)

        if discourse_response:
            if discourse_response.contradictions.items:
                state.unresolved_item_ids.add("discourse:contradictions")
            state.uncertainty_notes.extend(discourse_response.uncertainty_summary.items)

        state.uncertainty_notes = sorted(set(state.uncertainty_notes))
        state.notes.append("working memory is review state only; it does not mutate evidence, claims, sources, or graph")
        return state
