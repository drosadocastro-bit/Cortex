"""Adapter abstraction for future local or cloud LLM backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from roswell_uap_cortex.models import ReasoningContext, ReasoningOutput


@dataclass(slots=True)
class LocalLLMAdapter(ABC):
    """Abstract reasoning adapter; implementations must not mutate project state."""

    backend_name: str = "abstract"

    @abstractmethod
    def reason(self, context: ReasoningContext) -> ReasoningOutput:
        """Return structured reasoning from supplied context only."""
