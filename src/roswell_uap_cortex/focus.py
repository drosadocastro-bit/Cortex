"""Attention focus construction."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from roswell_uap_cortex.models import AttentionFocus
from roswell_uap_cortex.text import SimpleTokenizer


@dataclass(slots=True)
class AttentionFocusBuilder:
    """Build deterministic investigation focus metadata."""

    tokenizer: SimpleTokenizer = field(default_factory=SimpleTokenizer)

    def build(
        self,
        query_text: str = "",
        *,
        target_entities: set[str] | None = None,
        target_event_ids: set[str] | None = None,
        target_claim_topics: set[str] | None = None,
        time_window: tuple[date | None, date | None] | None = None,
        investigation_mode: str = "conservative",
        metadata: dict[str, object] | None = None,
    ) -> AttentionFocus:
        return AttentionFocus(
            query_text=query_text,
            focus_terms=self.tokenizer.tokenize(query_text),
            target_entities=target_entities or set(),
            target_event_ids=target_event_ids or set(),
            target_claim_topics=target_claim_topics or set(),
            time_window=time_window,
            investigation_mode=investigation_mode,
            metadata=dict(metadata or {}),
        )
