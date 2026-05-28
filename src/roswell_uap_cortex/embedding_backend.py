"""Embedding backend abstraction with deterministic mock implementation."""

from __future__ import annotations

import hashlib
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from roswell_uap_cortex.models import EmbeddingVector
from roswell_uap_cortex.text import SimpleTokenizer


class EmbeddingBackend(ABC):
    """Abstract interface for future embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingVector:
        """Embed one text string."""

    def embed_batch(self, texts: list[str]) -> list[EmbeddingVector]:
        return [self.embed_text(text) for text in texts]


@dataclass(slots=True)
class MockEmbeddingBackend(EmbeddingBackend):
    """Deterministic token-hash embedding backend for tests and local defaults."""

    dimensions: int = 16
    tokenizer: SimpleTokenizer = field(default_factory=SimpleTokenizer)
    model_name: str = "mock-token-hash-v1"

    def embed_text(self, text: str) -> EmbeddingVector:
        vector = [0.0 for _ in range(self.dimensions)]
        for token in sorted(self.tokenizer.tokenize(text)):
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % self.dimensions
            vector[bucket] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return EmbeddingVector(values=vector, model=self.model_name)
