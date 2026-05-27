"""Timeline ordering for exact, approximate, partial, and unknown event dates."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from roswell_uap_cortex.models import EventNode, TimelineDatePrecision


@dataclass(slots=True)
class TimelineEngine:
    """Store and query events chronologically when dates are knowable."""

    events: dict[str, EventNode] = field(default_factory=dict)

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
        if event.event_date is not None:
            return event.event_date
        if event.earliest_possible_date is not None:
            return event.earliest_possible_date
        if event.date_precision is TimelineDatePrecision.UNKNOWN:
            return None
        return None
