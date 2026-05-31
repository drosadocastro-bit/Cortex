"""Source reliability review docket construction."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.citations import CitationFormatter
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.source_risk import SourceRiskProfiler
from roswell_uap_cortex.models import (
    ContaminationFlag,
    ContaminationFlagType,
    DiscourseCitation,
    EvidenceItem,
    ProvenanceRecord,
    SourceLineageRecord,
    SourceReliabilitySignal,
    SourceReviewDocket,
    SourceReviewItem,
    SourceReviewPriority,
    SourceReviewRecommendation,
    SourceReviewRecommendationType,
    SourceTrust,
)


@dataclass(slots=True)
class SourceReviewEngine:
    """Build source review dockets without deciding source truth."""

    risk_profiler: SourceRiskProfiler = field(default_factory=SourceRiskProfiler)
    citation_formatter: CitationFormatter = field(default_factory=CitationFormatter)

    def build_docket(
        self,
        evidence_items: list[EvidenceItem],
        *,
        provenance_records: list[ProvenanceRecord] | None = None,
        lineage_records: list[SourceLineageRecord] | None = None,
        contamination_flags: list[ContaminationFlag] | None = None,
        source_trust_records: list[SourceTrust] | None = None,
        title: str = "Source Reliability Review Docket",
    ) -> SourceReviewDocket:
        provenance_records = provenance_records or []
        lineage_records = lineage_records or []
        contamination_flags = contamination_flags or []
        source_trust_records = source_trust_records or []

        provenance_by_evidence = {record.evidence_id: record for record in provenance_records}
        lineage_by_evidence: dict[str, list[SourceLineageRecord]] = {}
        for record in lineage_records:
            lineage_by_evidence.setdefault(record.evidence_id, []).append(record)
        trust_by_source = {record.source_id: record for record in source_trust_records}

        items = [
            self._item_for_source(
                source_id,
                grouped,
                provenance_by_evidence=provenance_by_evidence,
                lineage_records=[record for item in grouped for record in lineage_by_evidence.get(item.id, [])],
                contamination_flags=self._flags_for_source(source_id, grouped, contamination_flags),
                source_trust=trust_by_source.get(source_id),
            )
            for source_id, grouped in self._group_by_source(evidence_items).items()
        ]
        items = sorted(items, key=lambda item: (-item.priority_score, item.source_id))
        citations = self._citations(items, provenance_by_evidence, lineage_by_evidence)
        recommendations = self._merge_recommendations([rec for item in items for rec in item.recommendations])
        docket_id = str(uuid5(NAMESPACE_URL, "source-review:" + "|".join(item.source_id for item in items)))
        return SourceReviewDocket(
            docket_id=docket_id,
            title=title,
            items=items,
            citations=citations,
            recommendations=recommendations,
            notes=[
                "source review is a reliability review aid, not source truth or rejection",
                "risk and reliability signals remain separate from claim confirmation",
            ],
        )

    def _item_for_source(
        self,
        source_id: str,
        evidence_items: list[EvidenceItem],
        *,
        provenance_by_evidence: dict[str, ProvenanceRecord],
        lineage_records: list[SourceLineageRecord],
        contamination_flags: set[ContaminationFlagType],
        source_trust: SourceTrust | None,
    ) -> SourceReviewItem:
        provenance_visible = all(item.id in provenance_by_evidence for item in evidence_items)
        risk_score, risk_signals = self.risk_profiler.profile(
            source_id,
            evidence_items,
            provenance_visible=provenance_visible,
            lineage_records=lineage_records,
            contamination_flags=contamination_flags,
            source_trust=source_trust,
        )
        reliability_signals = self._reliability_signals(source_id, evidence_items, source_trust, provenance_visible)
        reliability_score = self._reliability_score(reliability_signals, risk_score)
        priority, priority_score = self._priority(risk_score)
        return SourceReviewItem(
            source_id=source_id,
            priority=priority,
            priority_score=priority_score,
            reliability_score=reliability_score,
            risk_score=risk_score,
            evidence_ids={item.id for item in evidence_items},
            provenance_ids={provenance_by_evidence[item.id].id for item in evidence_items if item.id in provenance_by_evidence},
            lineage_ids={record.lineage_id for record in lineage_records},
            contamination_flags=contamination_flags,
            reliability_signals=reliability_signals,
            risk_signals=risk_signals,
            recommendations=self._recommendations(risk_signals, source_trust),
            notes=["source review item only; no evidence, claim, graph, or trust mutation"],
        )

    def _reliability_signals(
        self,
        source_id: str,
        evidence_items: list[EvidenceItem],
        source_trust: SourceTrust | None,
        provenance_visible: bool,
    ) -> list[SourceReliabilitySignal]:
        signals: list[SourceReliabilitySignal] = []
        if provenance_visible:
            signals.append(
                SourceReliabilitySignal(
                    "provenance_visible",
                    0.35,
                    "Provenance is visible for the grouped source evidence.",
                    {item.id for item in evidence_items},
                )
            )
        if source_trust:
            signals.append(
                SourceReliabilitySignal(
                    "source_trust_inputs",
                    source_trust.source_trust_score,
                    "Source trust inputs are available for review.",
                    {source_id},
                )
            )
        if len(evidence_items) == 1:
            signals.append(
                SourceReliabilitySignal(
                    "single_record_visible",
                    0.1,
                    "Single evidence record is visible without repetition pressure.",
                    {evidence_items[0].id},
                )
            )
        return sorted(signals, key=lambda signal: signal.signal_type)

    def _reliability_score(self, signals: list[SourceReliabilitySignal], risk_score: float) -> float:
        return _clamp(sum(signal.score for signal in signals) * 0.6 + (1 - risk_score) * 0.4)

    def _priority(self, risk_score: float) -> tuple[SourceReviewPriority, float]:
        priority_score = _clamp(risk_score)
        if priority_score >= 0.75:
            return SourceReviewPriority.URGENT, priority_score
        if priority_score >= 0.5:
            return SourceReviewPriority.HIGH, priority_score
        if priority_score >= 0.25:
            return SourceReviewPriority.MEDIUM, priority_score
        return SourceReviewPriority.LOW, priority_score

    def _recommendations(
        self,
        risk_signals: list,
        source_trust: SourceTrust | None,
    ) -> list[SourceReviewRecommendation]:
        signal_types = {signal.signal_type for signal in risk_signals}
        recommendations = [
            SourceReviewRecommendation(
                SourceReviewRecommendationType.PRESERVE_SOURCE_UNCERTAINTY,
                "Keep source reliability as review state, not source truth.",
            )
        ]
        if "missing_provenance" in signal_types:
            recommendations.append(
                SourceReviewRecommendation(
                    SourceReviewRecommendationType.VERIFY_PROVENANCE,
                    "Verify provenance gaps before leaning on this source.",
                )
            )
        if {"derivative_lineage", "repeated_source_uri", "same_lineage_repetition"} & signal_types:
            recommendations.append(
                SourceReviewRecommendation(
                    SourceReviewRecommendationType.REVIEW_LINEAGE,
                    "Review lineage and repetition before treating records as independent.",
                )
            )
        if "contamination_flags" in signal_types:
            recommendations.append(
                SourceReviewRecommendation(
                    SourceReviewRecommendationType.CHECK_CONTAMINATION,
                    "Inspect contamination flags without rejecting the source automatically.",
                )
            )
        if source_trust is None or "source_trust_risk" in signal_types:
            recommendations.append(
                SourceReviewRecommendation(
                    SourceReviewRecommendationType.REVIEW_SOURCE_TRUST_INPUTS,
                    "Review source trust inputs; they are signals, not truth decisions.",
                )
            )
        if len(signal_types) >= 2:
            recommendations.append(
                SourceReviewRecommendation(
                    SourceReviewRecommendationType.HUMAN_REVIEW,
                    "Human review recommended because multiple source risk signals are visible.",
                )
            )
        return self._merge_recommendations(recommendations)

    def _flags_for_source(
        self,
        source_id: str,
        evidence_items: list[EvidenceItem],
        contamination_flags: list[ContaminationFlag],
    ) -> set[ContaminationFlagType]:
        evidence_ids = {item.id for item in evidence_items}
        source_uris = {source_id, *[str(item.metadata.get("source_uri", "")) for item in evidence_items]}
        return {
            flag.flag_type
            for flag in contamination_flags
            if flag.evidence_id in evidence_ids or flag.source_uri in source_uris
        }

    def _citations(
        self,
        items: list[SourceReviewItem],
        provenance_by_evidence: dict[str, ProvenanceRecord],
        lineage_by_evidence: dict[str, list[SourceLineageRecord]],
    ) -> list[DiscourseCitation]:
        citations: list[DiscourseCitation] = []
        for item in items:
            for evidence_id in sorted(item.evidence_ids):
                lineages = lineage_by_evidence.get(evidence_id, [])
                lineage = lineages[0] if lineages else None
                citations.append(
                    self.citation_formatter.citation_for(
                        evidence_id,
                        provenance=provenance_by_evidence.get(evidence_id),
                        lineage=lineage,
                        source_id=item.source_id,
                    )
                )
        return self.citation_formatter.merge(citations)

    def _group_by_source(self, evidence_items: list[EvidenceItem]) -> dict[str, list[EvidenceItem]]:
        grouped: dict[str, list[EvidenceItem]] = {}
        for item in sorted(evidence_items, key=lambda evidence: (evidence.source_id, evidence.id)):
            grouped.setdefault(item.source_id, []).append(item)
        return grouped

    def _merge_recommendations(
        self,
        recommendations: list[SourceReviewRecommendation],
    ) -> list[SourceReviewRecommendation]:
        merged: dict[SourceReviewRecommendationType, SourceReviewRecommendation] = {}
        for recommendation in recommendations:
            existing = merged.get(recommendation.recommendation_type)
            if not existing:
                merged[recommendation.recommendation_type] = recommendation
            else:
                existing.related_ids.update(recommendation.related_ids)
        return [merged[key] for key in sorted(merged, key=lambda item: item.value)]
