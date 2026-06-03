"""Deterministic evidence-quality rubric."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.evidence_quality_guardrails import EvidenceQualityGuardrails
from roswell_uap_cortex.memory import _clamp
from roswell_uap_cortex.models import (
    ContaminationFlagType,
    EvidenceItem,
    EvidenceQualityAssessment,
    EvidenceQualityDimensionScores,
    EvidenceQualityLabel,
    EvidenceQualityWarning,
    EvidenceQualityWarningType,
    ExtractedObservation,
    LineageType,
    ObservationType,
    ProvenanceRecord,
    SourceLineageRecord,
    TimelineDatePrecision,
)


@dataclass(slots=True)
class EvidenceQualityEngine:
    """Assess evidence condition without confirming claims or mutating records."""

    guardrails: EvidenceQualityGuardrails = field(default_factory=EvidenceQualityGuardrails)

    def assess(
        self,
        evidence: EvidenceItem,
        *,
        provenance: ProvenanceRecord | None = None,
        lineage: SourceLineageRecord | None = None,
        observation: ExtractedObservation | None = None,
        contradiction_pressure: float = 0.0,
    ) -> EvidenceQualityAssessment:
        reasons: list[str] = []
        warnings = self.guardrails.baseline_warnings(evidence.id)

        provenance_score = self._provenance_score(evidence, provenance, reasons, warnings)
        lineage_score = self._lineage_score(evidence, lineage, reasons, warnings)
        source_score = self._source_transparency_score(evidence, provenance, reasons)
        observation_score = self._observation_score(evidence, observation, reasons, warnings)
        contamination_score = self._contamination_resistance_score(evidence, lineage, reasons, warnings)
        contradiction_score = self._contradiction_stability_score(evidence, contradiction_pressure, reasons, warnings)
        temporal_score = self._temporal_score(evidence, reasons, warnings)
        extraction_score = self._extraction_score(evidence, reasons)

        dimensions = EvidenceQualityDimensionScores(
            provenance_completeness=provenance_score,
            lineage_clarity=lineage_score,
            source_transparency=source_score,
            observation_directness=observation_score,
            contamination_resistance=contamination_score,
            contradiction_stability=contradiction_score,
            temporal_specificity=temporal_score,
            extraction_confidence=extraction_score,
        )
        quality_score = self._average(
            [
                dimensions.provenance_completeness,
                dimensions.lineage_clarity,
                dimensions.source_transparency,
                dimensions.observation_directness,
                dimensions.contamination_resistance,
                dimensions.contradiction_stability,
                dimensions.temporal_specificity,
                dimensions.extraction_confidence,
            ]
        )
        if dimensions.provenance_completeness < 0.3:
            quality_score = min(quality_score, 0.74)
        if dimensions.lineage_clarity < 0.4:
            quality_score = min(quality_score, 0.74)
        if dimensions.contamination_resistance < 0.85:
            quality_score = min(quality_score, 0.74)
        if dimensions.contamination_resistance < 0.5:
            quality_score = min(quality_score, 0.64)
        label = self._label(quality_score, contradiction_pressure)
        review_priority = self._review_priority_score(quality_score, contradiction_pressure, warnings)

        return EvidenceQualityAssessment(
            evidence_id=evidence.id,
            dimension_scores=dimensions,
            quality_label=label,
            quality_score=quality_score,
            review_priority_score=review_priority,
            provenance_ids={provenance.id} if provenance else set(),
            lineage_id=None if lineage is None else lineage.lineage_id,
            reason_codes=sorted(set(reasons)),
            warnings=warnings,
            notes=["evidence quality is a bounded review signal, not claim confirmation"],
        )

    def rank_for_review(self, assessments: list[EvidenceQualityAssessment]) -> list[EvidenceQualityAssessment]:
        """Return fragile or contested evidence first for review attention only."""

        return sorted(
            assessments,
            key=lambda assessment: (-assessment.review_priority_score, assessment.evidence_id),
        )

    def _provenance_score(
        self,
        evidence: EvidenceItem,
        provenance: ProvenanceRecord | None,
        reasons: list[str],
        warnings: list[EvidenceQualityWarning],
    ) -> float:
        if provenance and provenance.source_uri and provenance.original_input_id:
            reasons.append("provenance_complete")
            return 1.0
        metadata_ids = evidence.metadata.get("provenance_ids", set())
        if metadata_ids:
            reasons.append("provenance_metadata_only")
            return 0.65
        reasons.append("missing_provenance")
        warnings.append(
            EvidenceQualityWarning(
                EvidenceQualityWarningType.MISSING_PROVENANCE,
                "Missing provenance lowers evidence quality and remains visible.",
                {evidence.id},
            )
        )
        return 0.15

    def _lineage_score(
        self,
        evidence: EvidenceItem,
        lineage: SourceLineageRecord | None,
        reasons: list[str],
        warnings: list[EvidenceQualityWarning],
    ) -> float:
        if lineage is None:
            reasons.append("missing_lineage")
            warnings.append(
                EvidenceQualityWarning(
                    EvidenceQualityWarningType.UNKNOWN_LINEAGE,
                    "Unknown lineage is treated cautiously.",
                    {evidence.id},
                )
            )
            return 0.35
        lineage_type = LineageType(lineage.lineage_type) if isinstance(lineage.lineage_type, str) else lineage.lineage_type
        if lineage_type is LineageType.PRIMARY_SOURCE:
            reasons.append("primary_lineage")
            return 1.0
        if lineage_type is LineageType.SECONDARY_SOURCE:
            reasons.append("secondary_lineage")
            return 0.7
        if lineage_type is LineageType.DERIVATIVE_SOURCE or lineage.derived_from or lineage.parent_source_id:
            reasons.append("derivative_lineage")
            warnings.append(
                EvidenceQualityWarning(
                    EvidenceQualityWarningType.DERIVATIVE_LINEAGE,
                    "Derivative lineage lowers independence and review quality.",
                    {evidence.id},
                )
            )
            return 0.3
        reasons.append("unknown_lineage")
        warnings.append(
            EvidenceQualityWarning(
                EvidenceQualityWarningType.UNKNOWN_LINEAGE,
                "Unknown lineage is treated cautiously.",
                {evidence.id},
            )
        )
        return 0.45

    def _source_transparency_score(
        self,
        evidence: EvidenceItem,
        provenance: ProvenanceRecord | None,
        reasons: list[str],
    ) -> float:
        source_text = f"{evidence.source_id} {evidence.metadata.get('author', '')}".casefold()
        if any(term in source_text for term in ("anonymous", "unknown", "redacted")):
            reasons.append("low_source_transparency")
            return 0.25
        if provenance and provenance.source_uri:
            reasons.append("source_uri_visible")
            return 0.9
        if evidence.source_id:
            reasons.append("source_id_visible")
            return 0.65
        reasons.append("source_missing")
        return 0.15

    def _observation_score(
        self,
        evidence: EvidenceItem,
        observation: ExtractedObservation | None,
        reasons: list[str],
        warnings: list[EvidenceQualityWarning],
    ) -> float:
        observation_type = observation.observation_type if observation else evidence.metadata.get("observation_type", ObservationType.UNKNOWN.value)
        if isinstance(observation_type, str):
            observation_type = ObservationType(observation_type)
        scores = {
            ObservationType.DIRECT_OBSERVATION: 1.0,
            ObservationType.METADATA_STATEMENT: 0.65,
            ObservationType.REPORTED_CLAIM: 0.5,
            ObservationType.INTERPRETATION: 0.45,
            ObservationType.SPECULATION: 0.2,
            ObservationType.UNKNOWN: 0.35,
        }
        score = scores[observation_type]
        reasons.append(f"observation_type:{observation_type.value}")
        if score < 0.55:
            warnings.append(
                EvidenceQualityWarning(
                    EvidenceQualityWarningType.LOW_OBSERVATION_DIRECTNESS,
                    "Interpretive, reported, speculative, or unknown observations lower quality.",
                    {evidence.id},
                )
            )
        return score

    def _contamination_resistance_score(
        self,
        evidence: EvidenceItem,
        lineage: SourceLineageRecord | None,
        reasons: list[str],
        warnings: list[EvidenceQualityWarning],
    ) -> float:
        flags = {str(flag.value if isinstance(flag, ContaminationFlagType) else flag) for flag in evidence.metadata.get("contamination_flags", [])}
        flags.update(str(flag.value if isinstance(flag, ContaminationFlagType) else flag) for flag in evidence.metadata.get("contamination_flag_types", []))
        if lineage and lineage.duplicate_source_uri:
            flags.add(ContaminationFlagType.REPEATED_SOURCE_URI.value)
        if lineage and (LineageType(lineage.lineage_type) if isinstance(lineage.lineage_type, str) else lineage.lineage_type) is LineageType.DERIVATIVE_SOURCE:
            flags.add(ContaminationFlagType.DERIVATIVE_SOURCE.value)
        if not flags:
            reasons.append("no_contamination_flags")
            return 1.0
        reasons.extend(f"contamination:{flag}" for flag in sorted(flags))
        warnings.append(
            EvidenceQualityWarning(
                EvidenceQualityWarningType.CONTAMINATION_RISK_VISIBLE,
                "Contamination flags lower quality and remain visible.",
                {evidence.id},
            )
        )
        return _clamp(1.0 - min(0.85, 0.18 * len(flags)))

    def _contradiction_stability_score(
        self,
        evidence: EvidenceItem,
        contradiction_pressure: float,
        reasons: list[str],
        warnings: list[EvidenceQualityWarning],
    ) -> float:
        pressure = max(float(evidence.metadata.get("contradiction_pressure", contradiction_pressure)), contradiction_pressure)
        pressure = _clamp(pressure)
        if pressure > 0:
            reasons.append("contradiction_pressure")
            warnings.append(
                EvidenceQualityWarning(
                    EvidenceQualityWarningType.CONTRADICTION_PRESSURE_VISIBLE,
                    "Contradiction pressure remains visible and lowers stability.",
                    {evidence.id},
                )
            )
        return _clamp(1.0 - pressure)

    def _temporal_score(
        self,
        evidence: EvidenceItem,
        reasons: list[str],
        warnings: list[EvidenceQualityWarning],
    ) -> float:
        precision = evidence.metadata.get("date_precision")
        if isinstance(precision, TimelineDatePrecision):
            precision = precision.value
        if evidence.observed_at:
            reasons.append("observed_at_present")
            return 1.0
        scores = {
            TimelineDatePrecision.EXACT.value: 1.0,
            TimelineDatePrecision.MONTH.value: 0.75,
            TimelineDatePrecision.YEAR.value: 0.55,
            TimelineDatePrecision.APPROXIMATE.value: 0.45,
            TimelineDatePrecision.UNKNOWN.value: 0.25,
        }
        score = scores.get(str(precision), 0.25)
        reasons.append(f"date_precision:{precision or 'unknown'}")
        if score < 0.6:
            warnings.append(
                EvidenceQualityWarning(
                    EvidenceQualityWarningType.TEMPORAL_UNCERTAINTY_VISIBLE,
                    "Unknown or approximate timing lowers temporal specificity.",
                    {evidence.id},
                )
            )
        return score

    def _extraction_score(self, evidence: EvidenceItem, reasons: list[str]) -> float:
        score = evidence.metadata.get("extraction_confidence", evidence.confidence)
        reasons.append("extraction_confidence")
        return _clamp(float(score))

    def _label(self, score: float, contradiction_pressure: float) -> EvidenceQualityLabel:
        if contradiction_pressure >= 0.65:
            return EvidenceQualityLabel.CONTESTED
        if score < 0.35:
            return EvidenceQualityLabel.INSUFFICIENT
        if score < 0.55:
            return EvidenceQualityLabel.FRAGILE
        if score < 0.75:
            return EvidenceQualityLabel.REVIEWABLE
        return EvidenceQualityLabel.STRONG_CONTEXT

    def _review_priority_score(
        self,
        quality_score: float,
        contradiction_pressure: float,
        warnings: list[EvidenceQualityWarning],
    ) -> float:
        warning_pressure = min(0.35, 0.05 * len(warnings))
        return _clamp((1.0 - quality_score) * 0.55 + _clamp(contradiction_pressure) * 0.3 + warning_pressure)

    def _average(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return _clamp(sum(values) / len(values))
