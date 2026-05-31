"""Deterministic formatting for session audit trails."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import ReviewSession, SessionAuditTrail


@dataclass(slots=True)
class SessionAuditFormatter:
    """Format session audit trails with explicit limitations."""

    def format(self, session: ReviewSession, trail: SessionAuditTrail) -> str:
        lines = [
            f"# Session Audit: {session.title}",
            "",
            f"- Session: {session.session_id}",
            f"- Events: {len(trail.records)}",
            "",
            "## Events",
        ]
        for record in trail.records:
            target = f" {record.item_type}:{record.item_id}" if record.item_id and record.item_type else ""
            note = f" notes:{'; '.join(record.notes)}" if record.notes else ""
            lines.append(f"- {record.created_at.isoformat()} {record.event_type}{target}{note}")
        lines.extend(
            [
                "",
                "## Limitations",
                "- Audit records describe review workflow only.",
                "- Audit records are not evidence, claim confirmation, source rejection, or graph mutation.",
            ]
        )
        return "\n".join(lines)
