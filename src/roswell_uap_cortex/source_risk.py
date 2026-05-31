"""Deterministic source risk profiling."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    ContaminationFlagType,
    EvidenceItem,
    LineageType,
    ObservationType,
    SourceLineageRecord,
    SourceRiskSignal,
    SourceTrust,
)


@dataclass(slots=True)
class SourceRiskProfiler:
    """Profile source risk without accepting or rejecting the source."""

    def profile(
        self,
        source_id: str,
        evidence_items: list[EvidenceItem],
        *,
        provenance_visible: bool,
        lineage_records: list[SourceLineageRecord],
        contamination_flags: set[ContaminationFlagType],
        source_trust: SourceTrust | None = None,
    ) -> tuple[float, list[SourceRiskSignal]]:
        signals: list[SourceRiskSignal] = []

        def add(signal_type: str, score: float, message: str, related_ids: set[str] | None = None) -> None:
            signals.append(SourceRiskSignal(signal_type, score, message, related_ids or set()))

        evidence_ids = {item.id for item in evidence_items}
        if not provenance_visible:
            add("missing_provenance", 0.3, "One or more source records lack visible provenance.", evidence_ids)

        if any(record.lineage_type is LineageType.DERIVATIVE_SOURCE for record in lineage_records):
            add("derivative_lineage", 0.2, "Source lineage includes derivative records.", evidence_ids)

        if any(record.duplicate_source_uri for record in lineage_records):
            add("repeated_source_uri", 0.18, "Source URI repetition is visible in lineage.", evidence_ids)

        if len({record.lineage_id for record in lineage_records}) == 1 and len(evidence_items) > 1:
            add("same_lineage_repetition", 0.12, "Multiple evidence records share one lineage.", evidence_ids)

        if contamination_flags:
            add(
                "contamination_flags",
                min(0.35, 0.08 * len(contamination_flags)),
                "Contamination flags are present for this source.",
                evidence_ids,
            )

        observation_types = {str(item.metadata.get("observation_type", "")) for item in evidence_items}
        if ObservationType.SPECULATION.value in observation_types:
            add("speculative_content", 0.12, "Speculative content appears in evidence from this source.", evidence_ids)
        if ObservationType.REPORTED_CLAIM.value in observation_types:
            add("reported_claim_content", 0.1, "Reported-claim content appears in evidence from this source.", evidence_ids)

        if source_trust and source_trust.source_risk_score >= 0.6:
            add("source_trust_risk", 0.18, "Source trust inputs currently indicate elevated risk.", {source_id})

        total = _clamp(sum(signal.score for signal in signals))
        return total, sorted(signals, key=lambda signal: (signal.signal_type, signal.message))
