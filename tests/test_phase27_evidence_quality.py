from roswell_uap_cortex import (
    AdversarialAttackVector,
    AdversarialExpectedFailureMode,
    AdversarialHarness,
    AdversarialScenarioFactory,
    ClaimMatrixStatus,
    ClaimNode,
    ContaminationFlagType,
    EvidenceItem,
    EvidenceQualityEngine,
    EvidenceQualityGuardrails,
    EvidenceQualityLabel,
    EvidenceQualityWarningType,
    LineageType,
    ObservationType,
    ProvenanceRecord,
    RelationshipGraphEngine,
    SourceLineageRecord,
    TimelineDatePrecision,
)


def provenance(evidence_id: str = "e1") -> ProvenanceRecord:
    return ProvenanceRecord(
        evidence_id=evidence_id,
        source_uri=f"synthetic://{evidence_id}",
        source_kind="synthetic",
        ingestion_method="fixture",
        extraction_method="fixture",
        original_input_id=f"input-{evidence_id}",
    )


def lineage(
    evidence_id: str = "e1",
    lineage_type: LineageType = LineageType.PRIMARY_SOURCE,
) -> SourceLineageRecord:
    return SourceLineageRecord(
        evidence_id,
        "source",
        f"lineage-{lineage_type.value}",
        lineage_type=lineage_type,
        derived_from="parent" if lineage_type is LineageType.DERIVATIVE_SOURCE else None,
    )


def evidence(
    evidence_id: str = "e1",
    *,
    observation_type: ObservationType = ObservationType.DIRECT_OBSERVATION,
    confidence: float = 0.8,
) -> EvidenceItem:
    return EvidenceItem(
        "synthetic evidence item",
        "source",
        "note",
        id=evidence_id,
        confidence=confidence,
        metadata={
            "observation_type": observation_type.value,
            "date_precision": TimelineDatePrecision.EXACT.value,
        },
    )


def test_evidence_quality_scores_complete_primary_evidence_as_strong_context() -> None:
    assessment = EvidenceQualityEngine().assess(
        evidence(),
        provenance=provenance(),
        lineage=lineage(),
    )

    assert assessment.quality_label is EvidenceQualityLabel.STRONG_CONTEXT
    assert assessment.quality_score > 0.75
    assert EvidenceQualityWarningType.QUALITY_NOT_TRUTH in {warning.warning_type for warning in assessment.warnings}


def test_missing_provenance_lowers_quality_and_stays_visible() -> None:
    assessment = EvidenceQualityEngine().assess(evidence(), lineage=lineage())

    assert assessment.dimension_scores.provenance_completeness < 0.3
    assert EvidenceQualityWarningType.MISSING_PROVENANCE in {warning.warning_type for warning in assessment.warnings}
    assert assessment.quality_label in {EvidenceQualityLabel.FRAGILE, EvidenceQualityLabel.REVIEWABLE}


def test_derivative_lineage_lowers_quality_without_rejecting_evidence() -> None:
    primary = EvidenceQualityEngine().assess(evidence("primary"), provenance=provenance("primary"), lineage=lineage("primary"))
    derivative = EvidenceQualityEngine().assess(
        evidence("derivative"),
        provenance=provenance("derivative"),
        lineage=lineage("derivative", LineageType.DERIVATIVE_SOURCE),
    )

    assert derivative.dimension_scores.lineage_clarity < primary.dimension_scores.lineage_clarity
    assert EvidenceQualityWarningType.DERIVATIVE_LINEAGE in {warning.warning_type for warning in derivative.warnings}
    assert derivative.quality_label is not EvidenceQualityLabel.INSUFFICIENT


def test_contamination_flags_lower_quality_and_remain_visible() -> None:
    item = evidence()
    item.metadata["contamination_flags"] = [
        ContaminationFlagType.SPECULATIVE_LANGUAGE.value,
        ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS.value,
    ]

    assessment = EvidenceQualityEngine().assess(item, provenance=provenance(), lineage=lineage())

    assert assessment.dimension_scores.contamination_resistance < 1.0
    assert EvidenceQualityWarningType.CONTAMINATION_RISK_VISIBLE in {warning.warning_type for warning in assessment.warnings}


def test_contradiction_pressure_creates_contested_quality_label() -> None:
    assessment = EvidenceQualityEngine().assess(
        evidence(),
        provenance=provenance(),
        lineage=lineage(),
        contradiction_pressure=0.8,
    )

    assert assessment.quality_label is EvidenceQualityLabel.CONTESTED
    assert assessment.dimension_scores.contradiction_stability < 0.3
    assert EvidenceQualityWarningType.CONTRADICTION_PRESSURE_VISIBLE in {warning.warning_type for warning in assessment.warnings}


def test_speculative_and_unknown_dates_reduce_quality_without_fabrication() -> None:
    item = evidence(observation_type=ObservationType.SPECULATION, confidence=0.5)
    item.metadata["date_precision"] = TimelineDatePrecision.UNKNOWN.value

    assessment = EvidenceQualityEngine().assess(item, provenance=provenance(), lineage=lineage())

    assert assessment.dimension_scores.observation_directness < 0.3
    assert assessment.dimension_scores.temporal_specificity < 0.3
    assert EvidenceQualityWarningType.LOW_OBSERVATION_DIRECTNESS in {warning.warning_type for warning in assessment.warnings}
    assert EvidenceQualityWarningType.TEMPORAL_UNCERTAINTY_VISIBLE in {warning.warning_type for warning in assessment.warnings}


def test_evidence_quality_does_not_confirm_claims_or_create_edges() -> None:
    item = evidence()
    claim = ClaimNode("synthetic claim", "topic", status=ClaimMatrixStatus.UNSUPPORTED, confidence=0.0)
    graph = RelationshipGraphEngine()

    assessment = EvidenceQualityEngine().assess(item, provenance=provenance(), lineage=lineage())

    assert assessment.quality_label is EvidenceQualityLabel.STRONG_CONTEXT
    assert claim.status is ClaimMatrixStatus.UNSUPPORTED
    assert claim.confidence == 0.0
    assert graph.edges == {}


def test_evidence_quality_can_rank_review_attention_only() -> None:
    engine = EvidenceQualityEngine()
    strong = engine.assess(evidence("strong"), provenance=provenance("strong"), lineage=lineage("strong"))
    fragile = engine.assess(evidence("fragile"), lineage=lineage("fragile", LineageType.DERIVATIVE_SOURCE), contradiction_pressure=0.7)

    ranked = engine.rank_for_review([strong, fragile])

    assert ranked[0].evidence_id == "fragile"
    assert ranked[0].review_priority_score > ranked[1].review_priority_score


def test_evidence_quality_guardrails_require_non_truth_warnings() -> None:
    assessment = EvidenceQualityEngine().assess(evidence(), provenance=provenance(), lineage=lineage())

    assert EvidenceQualityGuardrails().validates_boundary(assessment)


def test_quality_score_laundering_adversarial_scenario_is_resisted() -> None:
    report = AdversarialHarness().run([AdversarialScenarioFactory().quality_score_laundering()])
    finding = report.findings[0]

    assert finding.attack_vector is AdversarialAttackVector.QUALITY_SCORE_LAUNDERING
    assert finding.expected_failure_mode is AdversarialExpectedFailureMode.QUALITY_AS_CONFIRMATION
    assert finding.resisted
