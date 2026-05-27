"""Deterministic source independence scoring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True, frozen=True)
class EvidenceIndependenceInput:
    """Minimal provenance needed to judge whether evidence is independent."""

    source_id: str
    lineage_id: str | None = None
    publication_date: date | None = None
    author: str | None = None
    source_kind: str = "unknown"


@dataclass(slots=True)
class IndependenceScorer:
    """Score source independence without treating similarity as confirmation."""

    primary_source_kinds: frozenset[str] = frozenset(
        {"primary", "official_record", "archival_document", "transcript", "witness"}
    )

    def score_pair(
        self,
        first: EvidenceIndependenceInput,
        second: EvidenceIndependenceInput,
    ) -> float:
        if first.lineage_id and first.lineage_id == second.lineage_id:
            return 0.1
        if first.source_id == second.source_id:
            return 0.15
        if first.author and second.author and first.author.casefold() == second.author.casefold():
            return 0.3
        if first.lineage_id is None or second.lineage_id is None:
            return 0.4
        if (
            first.source_kind in self.primary_source_kinds
            and second.source_kind in self.primary_source_kinds
        ):
            return 0.85
        return 0.65

    def score_group(self, items: list[EvidenceIndependenceInput]) -> float:
        if not items:
            return 0.0
        if len(items) == 1:
            item = items[0]
            return 0.4 if item.lineage_id is None else 0.55

        scores = [
            self.score_pair(first, second)
            for index, first in enumerate(items)
            for second in items[index + 1 :]
        ]
        return sum(scores) / len(scores)
