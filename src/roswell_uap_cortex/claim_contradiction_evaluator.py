"""Deterministic contradiction markers for claim/evidence assessment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re

from roswell_uap_cortex.models import EvidenceItem, NormalizedClaim


NEGATION_MARKERS = {"not", "no", "never", "none", "without"}
MUTUALLY_EXCLUSIVE = [
    ("east", "west"),
    ("north", "south"),
    ("before", "after"),
    ("landed", "airborne"),
    ("day", "night"),
]


@dataclass(slots=True)
class ClaimContradictionEvaluator:
    """Detect possible contradiction without deciding which side is true."""

    def contradiction_score(self, normalized_claim: NormalizedClaim, evidence: EvidenceItem) -> tuple[float, list[str]]:
        claim_tokens = set(normalized_claim.canonical_key.token_fingerprint)
        evidence_tokens = self._tokens(evidence.summary)
        reasons: list[str] = []
        score = 0.0

        if claim_tokens.intersection(evidence_tokens) and evidence_tokens.intersection(NEGATION_MARKERS):
            score += 0.45
            reasons.append("negation_near_claim_tokens")

        for first, second in MUTUALLY_EXCLUSIVE:
            if first in claim_tokens and second in evidence_tokens:
                score += 0.4
                reasons.append(f"mutually_exclusive:{first}/{second}")
            if second in claim_tokens and first in evidence_tokens:
                score += 0.4
                reasons.append(f"mutually_exclusive:{second}/{first}")

        claim_dates = self._dates(normalized_claim.canonical_text)
        evidence_dates = self._dates(evidence.summary)
        if claim_dates and evidence_dates and claim_dates.isdisjoint(evidence_dates):
            score += 0.5
            reasons.append("exact_date_conflict")

        return min(score, 1.0), reasons

    def _tokens(self, text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", text.casefold()))

    def _dates(self, text: str) -> set[date]:
        found: set[date] = set()
        for year, month, day in re.findall(r"\b(\d{4})-(\d{2})-(\d{2})\b", text):
            try:
                found.add(date(int(year), int(month), int(day)))
            except ValueError:
                continue
        return found
