"""Claim matrix grouping and bounded confidence scoring."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from roswell_uap_cortex.independence import EvidenceIndependenceInput, IndependenceScorer
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import ClaimMatrixStatus, ClaimNode


@dataclass(slots=True)
class ClaimEvidenceContribution:
    """Evidence contribution to a claim topic."""

    evidence_id: str
    source_id: str
    confidence: float = 0.5
    source_trust: float = 0.5
    lineage_id: str | None = None
    publication_date: date | None = None
    author: str | None = None
    source_kind: str = "unknown"

    def independence_input(self) -> EvidenceIndependenceInput:
        return EvidenceIndependenceInput(
            source_id=self.source_id,
            lineage_id=self.lineage_id,
            publication_date=self.publication_date,
            author=self.author,
            source_kind=self.source_kind,
        )


@dataclass(slots=True)
class ClaimMatrixEntry:
    """Aggregated claim state for a canonical topic."""

    canonical_topic: str
    claims: list[ClaimNode] = field(default_factory=list)
    supporting_evidence: list[ClaimEvidenceContribution] = field(default_factory=list)
    contradicting_evidence: list[ClaimEvidenceContribution] = field(default_factory=list)
    source_trust_contribution: float = 0.0
    claim_confidence: float = 0.0
    status: ClaimMatrixStatus = ClaimMatrixStatus.UNSUPPORTED


@dataclass(slots=True)
class ClaimMatrixEngine:
    """Group claims and evaluate support while preserving contradictions."""

    independence_scorer: IndependenceScorer = field(default_factory=IndependenceScorer)
    entries: dict[str, ClaimMatrixEntry] = field(default_factory=dict)

    def add_claim(self, claim: ClaimNode) -> ClaimMatrixEntry:
        entry = self.entries.setdefault(
            claim.canonical_topic,
            ClaimMatrixEntry(canonical_topic=claim.canonical_topic),
        )
        if all(existing.id != claim.id for existing in entry.claims):
            entry.claims.append(claim)
        self.evaluate(claim.canonical_topic)
        return entry

    def register_unsupported_candidate_topic(
        self,
        canonical_topic: str,
        claim: ClaimNode,
    ) -> ClaimMatrixEntry:
        claim.status = ClaimMatrixStatus.UNSUPPORTED
        claim.confidence = 0.0
        entry = self.entries.setdefault(
            canonical_topic,
            ClaimMatrixEntry(canonical_topic=canonical_topic),
        )
        if all(existing.id != claim.id for existing in entry.claims):
            entry.claims.append(claim)
        if not entry.supporting_evidence and not entry.contradicting_evidence:
            entry.status = ClaimMatrixStatus.UNSUPPORTED
            entry.claim_confidence = 0.0
            for existing in entry.claims:
                existing.status = ClaimMatrixStatus.UNSUPPORTED
                existing.confidence = 0.0
        return entry

    def add_support(
        self,
        canonical_topic: str,
        contribution: ClaimEvidenceContribution,
    ) -> ClaimMatrixEntry:
        entry = self.entries.setdefault(
            canonical_topic,
            ClaimMatrixEntry(canonical_topic=canonical_topic),
        )
        if all(item.evidence_id != contribution.evidence_id for item in entry.supporting_evidence):
            entry.supporting_evidence.append(contribution)
        return self.evaluate(canonical_topic)

    def add_contradiction(
        self,
        canonical_topic: str,
        contribution: ClaimEvidenceContribution,
    ) -> ClaimMatrixEntry:
        entry = self.entries.setdefault(
            canonical_topic,
            ClaimMatrixEntry(canonical_topic=canonical_topic),
        )
        if all(item.evidence_id != contribution.evidence_id for item in entry.contradicting_evidence):
            entry.contradicting_evidence.append(contribution)
        return self.evaluate(canonical_topic)

    def evaluate(self, canonical_topic: str) -> ClaimMatrixEntry:
        entry = self.entries.setdefault(
            canonical_topic,
            ClaimMatrixEntry(canonical_topic=canonical_topic),
        )
        support_score = self._weighted_evidence_score(entry.supporting_evidence)
        contradiction_score = self._weighted_evidence_score(entry.contradicting_evidence)
        entry.source_trust_contribution = self._source_trust_average(entry.supporting_evidence)

        total = support_score + contradiction_score
        if total == 0:
            entry.claim_confidence = 0.0
        else:
            strength = min(total, 1.0)
            balance = support_score / total
            entry.claim_confidence = _clamp(balance * strength)

        if not entry.supporting_evidence and not entry.contradicting_evidence:
            entry.status = ClaimMatrixStatus.UNSUPPORTED
        elif support_score > 0 and contradiction_score >= 0.2:
            entry.status = ClaimMatrixStatus.CONTESTED
        elif support_score >= 0.55:
            entry.status = ClaimMatrixStatus.SUPPORTED
        elif support_score > 0:
            entry.status = ClaimMatrixStatus.WEAKLY_SUPPORTED
        else:
            entry.status = ClaimMatrixStatus.UNRESOLVED

        for claim in entry.claims:
            claim.confidence = entry.claim_confidence
            claim.status = entry.status
        return entry

    def _weighted_evidence_score(self, evidence: list[ClaimEvidenceContribution]) -> float:
        if not evidence:
            return 0.0

        by_independent_key: dict[str, list[ClaimEvidenceContribution]] = defaultdict(list)
        for item in evidence:
            key = item.lineage_id or f"unknown:{item.source_id}"
            by_independent_key[key].append(item)

        total = 0.0
        for grouped in by_independent_key.values():
            strongest = max(_clamp(item.confidence) * _clamp(item.source_trust) for item in grouped)
            duplicate_bonus = 0.05 * max(len(grouped) - 1, 0)
            independence = self.independence_scorer.score_group(
                [item.independence_input() for item in grouped]
            )
            total += strongest * (0.65 + independence * 0.35) + duplicate_bonus
        return _clamp(total)

    def _source_trust_average(self, evidence: list[ClaimEvidenceContribution]) -> float:
        if not evidence:
            return 0.0
        return sum(_clamp(item.source_trust) for item in evidence) / len(evidence)
