"""Conservative temporal reasoning helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import EventNode, TimelineDatePrecision


@dataclass(slots=True)
class TemporalComparison:
    """Conservative comparison between uncertain event dates."""

    relation: str
    ambiguous: bool = False
    impossible: bool = False
    notes: list[str] = None

    def __post_init__(self) -> None:
        if self.notes is None:
            self.notes = []


@dataclass(slots=True)
class TemporalReasoningHelper:
    """Compare approximate dates without fabricating precision."""

    def compare(self, first: EventNode, second: EventNode) -> TemporalComparison:
        first_range = self.date_range(first)
        second_range = self.date_range(second)
        if first_range is None or second_range is None:
            return TemporalComparison("unknown", ambiguous=True, notes=["one or both dates are unknown"])
        first_start, first_end = first_range
        second_start, second_end = second_range
        if first_end < second_start:
            return TemporalComparison("before")
        if first_start > second_end:
            return TemporalComparison("after")
        if first_start == second_start and first_end == second_end:
            return TemporalComparison("same_or_overlapping", ambiguous=first_start != first_end)
        return TemporalComparison("overlapping", ambiguous=True)

    def detect_impossible_sequence(self, before_event: EventNode, after_event: EventNode) -> bool:
        comparison = self.compare(before_event, after_event)
        return comparison.relation == "after"

    def timeline_proximity(self, first: EventNode, second: EventNode) -> float:
        first_anchor = self.sort_date(first)
        second_anchor = self.sort_date(second)
        if first_anchor is None or second_anchor is None:
            return 0.0
        days = abs((first_anchor - second_anchor).days)
        return _clamp(1 / (1 + days / 30))

    def date_range(self, event: EventNode) -> tuple[date, date] | None:
        if event.event_date:
            return (event.event_date, event.event_date)
        if event.earliest_possible_date and event.latest_possible_date:
            return (event.earliest_possible_date, event.latest_possible_date)
        if event.earliest_possible_date:
            return (event.earliest_possible_date, event.earliest_possible_date)
        if event.date_precision is TimelineDatePrecision.UNKNOWN:
            return None
        return None

    def sort_date(self, event: EventNode) -> date | None:
        if event.event_date:
            return event.event_date
        if event.earliest_possible_date:
            return event.earliest_possible_date
        return None
