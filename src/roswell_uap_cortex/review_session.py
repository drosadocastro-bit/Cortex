"""Deterministic review session state management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.models import (
    DeferredItem,
    ReviewDecision,
    ReviewDecisionType,
    ReviewedItem,
    ReviewSession,
    ReviewSessionState,
    SessionDelta,
)


EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


@dataclass(slots=True)
class ReviewSessionEngine:
    """Start, resume, and annotate review sessions without truth mutation."""

    def start_session(
        self,
        title: str,
        state: ReviewSessionState | None = None,
        *,
        session_id: str | None = None,
    ) -> ReviewSession:
        state = state or ReviewSessionState()
        session_id = session_id or str(uuid5(NAMESPACE_URL, f"review-session:{title}:{self._state_key(state)}"))
        return ReviewSession(
            session_id=session_id,
            title=title,
            state=state,
            created_at=EPOCH,
            updated_at=EPOCH,
            notes=["review session annotations are not evidence, claim confirmation, or source rejection"],
        )

    def resume_session(self, session: ReviewSession) -> ReviewSession:
        session.notes = sorted(set(session.notes + ["session resumed without mutating reviewed records"]))
        return session

    def record_decision(
        self,
        session: ReviewSession,
        *,
        item_id: str,
        item_type: str,
        decision_type: ReviewDecisionType | str,
        notes: list[str] | None = None,
    ) -> SessionDelta:
        decision = ReviewDecision(
            item_id=item_id,
            item_type=item_type,
            decision_type=decision_type,
            notes=notes or [],
            created_at=EPOCH,
        )
        session.decisions.append(decision)
        session.updated_at = EPOCH
        delta = SessionDelta(session_id=session.session_id)

        if decision.decision_type is ReviewDecisionType.REVIEWED:
            if all(item.item_id != item_id for item in session.state.reviewed_items):
                session.state.reviewed_items.append(
                    ReviewedItem(
                        item_id=item_id,
                        item_type=item_type,
                        reviewed_at=EPOCH,
                        notes=list(decision.notes),
                        decision_id=decision.decision_id,
                    )
                )
            delta.added_reviewed_ids.add(item_id)
        elif decision.decision_type in {ReviewDecisionType.DEFERRED, ReviewDecisionType.REQUEST_MORE_PROVENANCE, ReviewDecisionType.REQUEST_SOURCE_REVIEW}:
            if all(item.item_id != item_id for item in session.state.deferred_items):
                session.state.deferred_items.append(
                    DeferredItem(
                        item_id=item_id,
                        item_type=item_type,
                        reason="; ".join(decision.notes),
                        deferred_at=EPOCH,
                        decision_id=decision.decision_id,
                    )
                )
            session.state.unresolved_item_ids.add(item_id)
            delta.added_deferred_ids.add(item_id)
            delta.added_unresolved_ids.add(item_id)
        elif decision.decision_type is ReviewDecisionType.KEEP_UNRESOLVED:
            session.state.unresolved_item_ids.add(item_id)
            delta.added_unresolved_ids.add(item_id)

        delta.notes.append("decision recorded as review annotation only; no truth state changed")
        return delta

    def _state_key(self, state: ReviewSessionState) -> str:
        parts = [
            *sorted(state.active_focus.focus_ids),
            *sorted(state.active_claim_docket_ids),
            *sorted(state.active_source_docket_ids),
            *sorted(state.active_context_ids),
            *sorted(state.unresolved_item_ids),
        ]
        return "|".join(parts)
