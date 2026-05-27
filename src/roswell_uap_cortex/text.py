"""Small deterministic text utilities for retrieval."""

from __future__ import annotations

import string
from dataclasses import dataclass, field


@dataclass(slots=True)
class SimpleTokenizer:
    """Lowercase, strip punctuation, remove basic stopwords, and return token sets."""

    stopwords: set[str] = field(
        default_factory=lambda: {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "in",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "this",
            "to",
            "was",
            "were",
            "with",
        }
    )

    def tokenize(self, text: str) -> set[str]:
        translation = str.maketrans({character: " " for character in string.punctuation})
        normalized = text.casefold().translate(translation)
        return {
            token
            for token in normalized.split()
            if token and token not in self.stopwords
        }


def overlap_score(first: set[str], second: set[str]) -> float:
    """Return deterministic Jaccard overlap for two token-like sets."""
    if not first or not second:
        return 0.0
    return len(first & second) / len(first | second)
