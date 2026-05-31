"""Deterministic review session formatting."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import ReviewSession


@dataclass(slots=True)
class SessionFormatter:
    """Format review sessions without certainty-inflating language."""

    def format(self, session: ReviewSession) -> str:
        state = session.state
        lines = [
            f"# {session.title}",
            "",
            f"- Session: {session.session_id}",
            f"- Focus query: {state.active_focus.query or 'none'}",
            f"- Active focus ids: {self._csv(state.active_focus.focus_ids)}",
            f"- Claim dockets: {self._csv(state.active_claim_docket_ids)}",
            f"- Source dockets: {self._csv(state.active_source_docket_ids)}",
            f"- Reviewed items: {self._csv({item.item_id for item in state.reviewed_items})}",
            f"- Deferred items: {self._csv({item.item_id for item in state.deferred_items})}",
            f"- Unresolved items: {self._csv(state.unresolved_item_ids)}",
            f"- Contradiction ids: {self._csv(state.contradiction_ids)}",
            "",
            "## Uncertainty",
        ]
        if state.uncertainty_notes:
            lines.extend(f"- {note}" for note in sorted(state.uncertainty_notes))
        else:
            lines.append("- none")
        lines.extend(
            [
                "",
                "## Boundary",
                "- Session decisions are human-review annotations, not claim confirmation, source rejection, or evidence mutation.",
            ]
        )
        return "\n".join(lines)

    def _csv(self, values: set[str]) -> str:
        return ", ".join(sorted(values)) if values else "none"
