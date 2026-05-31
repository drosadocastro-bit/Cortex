"""Deterministic review-session audit logging."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from roswell_uap_cortex.models import ReviewDecision, ReviewSession, SessionAuditRecord, SessionAuditTrail


EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


@dataclass(slots=True)
class SessionAuditLogger:
    """Create audit records for session workflow events."""

    default_timestamp: datetime = EPOCH

    def start(self, session: ReviewSession) -> SessionAuditRecord:
        return self.record("session_started", session.session_id, notes=[session.title])

    def resume(self, session: ReviewSession) -> SessionAuditRecord:
        return self.record("session_resumed", session.session_id, notes=[session.title])

    def decision(self, session: ReviewSession, decision: ReviewDecision) -> SessionAuditRecord:
        return self.record(
            f"decision:{decision.decision_type.value}",
            session.session_id,
            item_id=decision.item_id,
            item_type=decision.item_type,
            notes=list(decision.notes),
        )

    def report(self, session: ReviewSession, note: str = "session report formatted") -> SessionAuditRecord:
        return self.record("session_report", session.session_id, notes=[note])

    def record(
        self,
        event_type: str,
        session_id: str,
        *,
        item_id: str | None = None,
        item_type: str | None = None,
        notes: list[str] | None = None,
    ) -> SessionAuditRecord:
        return SessionAuditRecord(
            event_type=event_type,
            session_id=session_id,
            item_id=item_id,
            item_type=item_type,
            notes=notes or [],
            created_at=self.default_timestamp,
        )

    def build_trail(
        self,
        session: ReviewSession,
        records: list[SessionAuditRecord],
    ) -> SessionAuditTrail:
        ordered = sorted(records, key=lambda record: (record.created_at.isoformat(), record.event_type, record.record_id))
        return SessionAuditTrail(
            session_id=session.session_id,
            records=ordered,
            notes=["audit trail records workflow events only; not evidence or truth state"],
        )
