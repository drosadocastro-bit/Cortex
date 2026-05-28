"""Timeline ordering for exact, approximate, partial, and unknown event dates."""

from __future__ import annotations

from dataclasses import dataclass, field
import calendar
from datetime import date, datetime
import re

from dateutil import parser

from roswell_uap_cortex.models import EventNode, TimelineDatePrecision
from roswell_uap_cortex.temporal import TemporalReasoningHelper


@dataclass(slots=True)
class TimelineEngine:
    """Store and query events chronologically when dates are knowable."""

    events: dict[str, EventNode] = field(default_factory=dict)
    temporal_helper: TemporalReasoningHelper = field(default_factory=TemporalReasoningHelper)

    def add_event(self, event: EventNode) -> EventNode:
        self.events[event.id] = event
        return event

    def ordered_events(self) -> list[EventNode]:
        return sorted(
            self.events.values(),
            key=lambda event: (
                self._sort_date(event) is None,
                self._sort_date(event) or date.max,
                event.label.casefold(),
                event.id,
            ),
        )

    def events_before(self, target_event_id: str) -> list[EventNode]:
        target = self.events[target_event_id]
        target_date = self._sort_date(target)
        if target_date is None:
            return []
        return [
            event
            for event in self.ordered_events()
            if event.id != target_event_id
            and (event_date := self._sort_date(event)) is not None
            and event_date < target_date
        ]

    def events_after(self, target_event_id: str) -> list[EventNode]:
        target = self.events[target_event_id]
        target_date = self._sort_date(target)
        if target_date is None:
            return []
        return [
            event
            for event in self.ordered_events()
            if event.id != target_event_id
            and (event_date := self._sort_date(event)) is not None
            and event_date > target_date
        ]

    def _sort_date(self, event: EventNode) -> date | None:
        return self.temporal_helper.sort_date(event)

    def event_from_date_hint(
        self,
        *,
        label: str,
        date_hint: str | None,
        id: str | None = None,
        evidence_ids: set[str] | None = None,
    ) -> EventNode:
        """Create an event from a date hint without fabricating exact dates."""
        event = EventNode(label=label, evidence_ids=evidence_ids or set())
        if id is not None:
            event.id = id
        if not date_hint or date_hint.casefold().strip() in {"unknown", "unk", "n/a"}:
            event.date_precision = TimelineDatePrecision.UNKNOWN
            event.date_note = "date hint was unknown"
            return event

        hint = date_hint.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", hint):
            parsed = parser.isoparse(hint).date()
            event.event_date = parsed
            event.earliest_possible_date = parsed
            event.latest_possible_date = parsed
            event.date_precision = TimelineDatePrecision.EXACT
            event.date_note = "exact date parsed from full ISO date"
            return event
        if re.fullmatch(r"\d{4}-\d{2}", hint):
            year, month = [int(part) for part in hint.split("-")]
            event.earliest_possible_date = date(year, month, 1)
            event.latest_possible_date = self._month_end(year, month)
            event.date_precision = TimelineDatePrecision.MONTH
            event.date_note = "month precision preserved; no day fabricated"
            return event
        if re.fullmatch(r"\d{4}", hint):
            year = int(hint)
            event.earliest_possible_date = date(year, 1, 1)
            event.latest_possible_date = date(year, 12, 31)
            event.date_precision = TimelineDatePrecision.YEAR
            event.date_note = "year precision preserved; no month or day fabricated"
            return event

        tokens = hint.split()
        if len(tokens) == 2 and re.fullmatch(r"\d{4}", tokens[1]):
            try:
                parsed = parser.parse(hint, default=datetime(int(tokens[1]), 1, 1)).date()
            except (ValueError, OverflowError):
                event.date_precision = TimelineDatePrecision.UNKNOWN
                event.date_note = f"unparseable date hint: {hint}"
                return event
            event.earliest_possible_date = date(parsed.year, parsed.month, 1)
            event.latest_possible_date = self._month_end(parsed.year, parsed.month)
            event.date_precision = TimelineDatePrecision.APPROXIMATE
            event.date_note = "approximate month parsed; no exact day fabricated"
            return event

        event.date_precision = TimelineDatePrecision.UNKNOWN
        event.date_note = f"date hint preserved as unknown or unsupported: {hint}"
        return event

    def _month_end(self, year: int, month: int) -> date:
        if month == 12:
            return date(year, 12, 31)
        return date(year, month, calendar.monthrange(year, month)[1])
