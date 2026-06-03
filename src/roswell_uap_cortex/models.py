"""Core domain models for uncertain investigative evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class ClaimStatus(str, Enum):
    """Resolution state for claims without asserting truth."""

    UNASSESSED = "unassessed"
    SUPPORTED = "supported"
    CONTESTED = "contested"
    CONTRADICTED = "contradicted"
    RETRACTED = "retracted"


class GraphNodeType(str, Enum):
    """Types of nodes available to the investigative graph."""

    EVIDENCE = "evidence"
    CLAIM = "claim"
    SOURCE = "source"
    EVENT = "event"
    ENTITY = "entity"
    MEMORY = "memory"


class RelationshipType(str, Enum):
    """Deterministic relationship types in the investigative graph."""

    MENTIONS = "mentions"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFERENCES = "references"
    SAME_EVENT_CANDIDATE = "same_event_candidate"
    TEMPORAL_BEFORE = "temporal_before"
    TEMPORAL_AFTER = "temporal_after"
    DERIVED_FROM = "derived_from"
    DUPLICATE_OF = "duplicate_of"


class TimelineDatePrecision(str, Enum):
    """How precise an event date is known to be."""

    EXACT = "exact"
    MONTH = "month"
    YEAR = "year"
    APPROXIMATE = "approximate"
    UNKNOWN = "unknown"


class ClaimMatrixStatus(str, Enum):
    """Claim matrix status labels that preserve unresolved uncertainty."""

    UNSUPPORTED = "unsupported"
    WEAKLY_SUPPORTED = "weakly_supported"
    CONTESTED = "contested"
    SUPPORTED = "supported"
    UNRESOLVED = "unresolved"


class AssociationLabel(str, Enum):
    """Association labels are retrieval hints, not relationship confirmations."""

    POSSIBLE_ASSOCIATION = "possible_association"
    WEAK_ASSOCIATION = "weak_association"
    CONTESTED_ASSOCIATION = "contested_association"


class EvidenceCategory(str, Enum):
    """Epistemic category for evidence or evidence-like assertions."""

    PRIMARY = "primary"
    SECONDARY_INTERPRETATION = "secondary_interpretation"
    SPECULATION = "speculation"
    CONTAMINATED_REPETITION = "contaminated_repetition"
    UNSUPPORTED_CLAIM = "unsupported_claim"


class RawInputType(str, Enum):
    """Supported raw ingestion input types."""

    DOCUMENT = "document"
    TRANSCRIPT = "transcript"
    NOTE = "note"
    IMAGE_METADATA = "image_metadata"
    VIDEO_METADATA = "video_metadata"
    UNKNOWN = "unknown"


class ObservationType(str, Enum):
    """How an extracted span relates to observation, interpretation, or report."""

    DIRECT_OBSERVATION = "direct_observation"
    INTERPRETATION = "interpretation"
    SPECULATION = "speculation"
    REPORTED_CLAIM = "reported_claim"
    METADATA_STATEMENT = "metadata_statement"
    UNKNOWN = "unknown"


class CandidateClaimOrigin(str, Enum):
    """Where a candidate claim was extracted from; not a truth source."""

    FROM_DIRECT_OBSERVATION = "from_direct_observation"
    FROM_REPORTED_CLAIM = "from_reported_claim"
    FROM_INTERPRETATION = "from_interpretation"
    FROM_SPECULATION = "from_speculation"
    FROM_METADATA = "from_metadata"
    UNKNOWN = "unknown"


class ClaimExtractionWarningType(str, Enum):
    """Warnings emitted during candidate claim extraction."""

    EXTRACTION_NOT_CONFIRMATION = "extraction_not_confirmation"
    DIRECT_OBSERVATION_CAUTION = "direct_observation_caution"
    REPORTED_CLAIM_NOT_VERIFIED = "reported_claim_not_verified"
    INTERPRETATION_NOT_OBSERVATION = "interpretation_not_observation"
    SPECULATION_REMAINS_SPECULATION = "speculation_remains_speculation"
    METADATA_NOT_CLAIM_SUPPORT = "metadata_not_claim_support"
    MISSING_PROVENANCE = "missing_provenance"


class ClaimNormalizationWarningType(str, Enum):
    """Warnings emitted while grouping candidate claims."""

    NORMALIZATION_NOT_VALIDATION = "normalization_not_validation"
    SAME_LINEAGE_REPETITION = "same_lineage_repetition"
    REPEATED_CLAIMS_NOT_CORROBORATION = "repeated_claims_not_corroboration"
    SPECULATION_ORIGIN_VISIBLE = "speculation_origin_visible"
    REPORTED_ORIGIN_VISIBLE = "reported_origin_visible"
    METADATA_NOT_EVENT_TRUTH = "metadata_not_event_truth"
    AMBIGUOUS_ORIGIN_MERGE = "ambiguous_origin_merge"
    UNSUPPORTED_TOPIC_ONLY = "unsupported_topic_only"


class ClaimEvidenceAssessmentType(str, Enum):
    """Claim/evidence relation signal type; not truth or disproof."""

    POSSIBLE_SUPPORT = "possible_support"
    POSSIBLE_CONTRADICTION = "possible_contradiction"
    UNCERTAIN = "uncertain"
    IRRELEVANT = "irrelevant"
    NEEDS_REVIEW = "needs_review"


class ClaimEvaluationWarningType(str, Enum):
    """Warnings emitted by claim evidence assessment."""

    SUPPORT_NOT_CONFIRMATION = "support_not_confirmation"
    CONTRADICTION_NOT_DISPROOF = "contradiction_not_disproof"
    SAME_LINEAGE_NOT_CORROBORATION = "same_lineage_not_corroboration"
    REPEATED_PARAPHRASE_NOT_INDEPENDENCE = "repeated_paraphrase_not_independence"
    SPECULATIVE_EVIDENCE_CAUTION = "speculative_evidence_caution"
    REPORTED_CLAIM_CAUTION = "reported_claim_caution"
    METADATA_NOT_EVENT_TRUTH = "metadata_not_event_truth"
    MISSING_PROVENANCE = "missing_provenance"
    NEEDS_REVIEW = "needs_review"
    EVALUATION_NOT_TRUTH = "evaluation_not_truth"


class ReviewPriority(str, Enum):
    """Claim review priority; not truth confidence or operational urgency."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReviewRecommendationType(str, Enum):
    """Bounded review recommendations that do not confirm or reject claims."""

    PRESERVE_UNSUPPORTED = "preserve_unsupported"
    REVIEW_CONTRADICTION = "review_contradiction"
    VERIFY_PROVENANCE = "verify_provenance"
    CHECK_SOURCE_INDEPENDENCE = "check_source_independence"
    REVIEW_SPECULATIVE_OR_REPORTED = "review_speculative_or_reported"
    HUMAN_REVIEW = "human_review"


class SourceReviewPriority(str, Enum):
    """Source review priority; not source truth or rejection."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SourceReviewRecommendationType(str, Enum):
    """Bounded recommendations for source reliability review."""

    PRESERVE_SOURCE_UNCERTAINTY = "preserve_source_uncertainty"
    VERIFY_PROVENANCE = "verify_provenance"
    REVIEW_LINEAGE = "review_lineage"
    CHECK_CONTAMINATION = "check_contamination"
    REVIEW_SOURCE_TRUST_INPUTS = "review_source_trust_inputs"
    HUMAN_REVIEW = "human_review"


class ReviewDecisionType(str, Enum):
    """Human-review annotation type; not a truth decision."""

    REVIEWED = "reviewed"
    DEFERRED = "deferred"
    KEEP_UNRESOLVED = "keep_unresolved"
    REQUEST_MORE_PROVENANCE = "request_more_provenance"
    REQUEST_SOURCE_REVIEW = "request_source_review"


class ReviewInfluenceScope(str, Enum):
    """Where review workflow annotations may have bounded influence."""

    ATTENTION = "attention"
    CONTEXT = "context"
    DISCOURSE = "discourse"


class ReviewInfluenceWarningType(str, Enum):
    """Warnings that keep review workflow influence from becoming truth."""

    REVIEW_STATE_NOT_TRUTH = "review_state_not_truth"
    REVIEWED_NOT_CONFIRMED = "reviewed_not_confirmed"
    DEFERRED_NOT_ERASED = "deferred_not_erased"
    SOURCE_RISK_NOT_REJECTION = "source_risk_not_rejection"
    PRIORITY_NOT_CONFIDENCE = "priority_not_confidence"
    BUNDLE_NOT_REASONING_INPUT = "bundle_not_reasoning_input"
    AUDIT_NOT_EVIDENCE = "audit_not_evidence"
    PROVENANCE_GAP_VISIBLE = "provenance_gap_visible"


class LineageType(str, Enum):
    """Ingestion lineage classification."""

    PRIMARY_SOURCE = "primary_source"
    SECONDARY_SOURCE = "secondary_source"
    DERIVATIVE_SOURCE = "derivative_source"
    UNKNOWN_LINEAGE = "unknown_lineage"


class ContaminationFlagType(str, Enum):
    """Deterministic contamination and source-quality warnings."""

    MISSING_DATE = "missing_date"
    MISSING_SOURCE_URI = "missing_source_uri"
    MISSING_TITLE = "missing_title"
    DERIVATIVE_SOURCE = "derivative_source"
    REPEATED_SOURCE_URI = "repeated_source_uri"
    ANONYMOUS_SOURCE = "anonymous_source"
    SPECULATIVE_LANGUAGE = "speculative_language"
    FICTIONAL_CONTAMINATION_TERMS = "fictional_contamination_terms"
    WEAK_CHAIN_OF_CUSTODY = "weak_chain_of_custody"


class EvidenceQualityLabel(str, Enum):
    """Evidence condition label for review context, not truth confidence."""

    INSUFFICIENT = "insufficient"
    FRAGILE = "fragile"
    REVIEWABLE = "reviewable"
    STRONG_CONTEXT = "strong_context"
    CONTESTED = "contested"


class EvidenceQualityWarningType(str, Enum):
    """Warnings that keep evidence quality from becoming truth."""

    QUALITY_NOT_TRUTH = "quality_not_truth"
    REVIEW_SIGNAL_ONLY = "review_signal_only"
    MISSING_PROVENANCE = "missing_provenance"
    DERIVATIVE_LINEAGE = "derivative_lineage"
    UNKNOWN_LINEAGE = "unknown_lineage"
    CONTAMINATION_RISK_VISIBLE = "contamination_risk_visible"
    CONTRADICTION_PRESSURE_VISIBLE = "contradiction_pressure_visible"
    TEMPORAL_UNCERTAINTY_VISIBLE = "temporal_uncertainty_visible"
    LOW_OBSERVATION_DIRECTNESS = "low_observation_directness"


class ConfidenceBand(str, Enum):
    """Context-support band for reasoning output, not truth confidence."""

    INSUFFICIENT_CONTEXT = "insufficient_context"
    LOW = "low"
    MEDIUM = "medium"
    HIGH_CONTEXT_SUPPORT = "high_context_support"
    CONTESTED = "contested"


class ReasoningWarningType(str, Enum):
    """Typed guardrail warnings for bounded reasoning."""

    ASSOCIATION_NOT_CONFIRMATION = "association_not_confirmation"
    CONTRADICTION_VISIBLE = "contradiction_visible"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    MISSING_PROVENANCE = "missing_provenance"
    SAME_LINEAGE_REPETITION = "same_lineage_repetition"
    FICTIONAL_CONTAMINATION = "fictional_contamination"
    SPECULATIVE_HYPOTHESIS = "speculative_hypothesis"


class DiscourseWarningType(str, Enum):
    """Typed warnings for human-facing discourse."""

    SPECULATION_LABELED = "speculation_labeled"
    UNSUPPORTED_REMAINS_UNSUPPORTED = "unsupported_remains_unsupported"
    PROVENANCE_VISIBLE = "provenance_visible"
    CONTRADICTION_VISIBLE = "contradiction_visible"
    NO_FABRICATED_EVIDENCE = "no_fabricated_evidence"
    CERTAINTY_LANGUAGE_AVOIDED = "certainty_language_avoided"
    CONTAMINATION_WARNING = "contamination_warning"
    MISSING_PROVENANCE = "missing_provenance"


class ExpectedBehaviorType(str, Enum):
    """Epistemic behaviors evaluated by synthetic scenarios."""

    PROVENANCE_VISIBLE = "provenance_visible"
    CONTRADICTIONS_PRESERVED = "contradictions_preserved"
    UNSUPPORTED_CLAIM_NOT_CONFIRMED = "unsupported_claim_not_confirmed"
    ASSOCIATION_NOT_CONFIRMATION = "association_not_confirmation"
    SPECULATIVE_LABELED = "speculative_labeled"
    SAME_LINEAGE_NOT_INDEPENDENT = "same_lineage_not_independent"
    UNCERTAINTY_EXPOSED = "uncertainty_exposed"
    CONTAMINATION_WARNING_VISIBLE = "contamination_warning_visible"
    CONFIDENCE_BOUNDED = "confidence_bounded"
    NO_STATE_MUTATION = "no_state_mutation"
    SEMANTIC_SIMILARITY_NOT_CONFIRMATION = "semantic_similarity_not_confirmation"
    SEMANTIC_LINEAGE_ECHO_DOWNGRADED = "semantic_lineage_echo_downgraded"
    SEMANTIC_MISSING_PROVENANCE_WARNING = "semantic_missing_provenance_warning"
    CONTESTED_SEMANTIC_CLUSTER_VISIBLE = "contested_semantic_cluster_visible"
    DISCOURSE_NOT_EVIDENCE = "discourse_not_evidence"
    REASONING_NOT_CLAIM_MUTATION = "reasoning_not_claim_mutation"
    SEMANTIC_CLUSTER_NOT_GRAPH_SUPPORT = "semantic_cluster_not_graph_support"
    RECURSIVE_INFERENCE_DETECTED = "recursive_inference_detected"
    SYNTHETIC_NOT_REAL_EVIDENCE = "synthetic_not_real_evidence"
    SPECULATION_REMAINS_SPECULATION = "speculation_remains_speculation"
    ATTENTION_SALIENCE_NOT_CONFIDENCE = "attention_salience_not_confidence"
    ATTENTION_CONTRADICTION_VISIBLE = "attention_contradiction_visible"
    ATTENTION_PROVENANCE_WARNING_VISIBLE = "attention_provenance_warning_visible"
    ATTENTION_CONTAMINATION_WARNING_VISIBLE = "attention_contamination_warning_visible"
    ATTENTION_SAME_LINEAGE_SUPPRESSED = "attention_same_lineage_suppressed"
    CLAIM_NORMALIZATION_NOT_VALIDATION = "claim_normalization_not_validation"
    NORMALIZED_CLAIMS_UNSUPPORTED = "normalized_claims_unsupported"
    REVIEW_STATE_NOT_TRUTH = "review_state_not_truth"
    DEFERRED_REVIEW_VISIBLE = "deferred_review_visible"
    SOURCE_RISK_NOT_REJECTION = "source_risk_not_rejection"
    PRESENTATION_NOT_REASONING = "presentation_not_reasoning"
    PRESENTATION_NO_AGGREGATION_SEMANTICS = "presentation_no_aggregation_semantics"
    PRESENTATION_MISSING_DATA_VISIBLE = "presentation_missing_data_visible"
    DEMO_PRESENTATION_SYNTHETIC_ONLY = "demo_presentation_synthetic_only"
    EVIDENCE_QUALITY_NOT_CONFIRMATION = "evidence_quality_not_confirmation"
    EVIDENCE_QUALITY_REVIEW_ONLY = "evidence_quality_review_only"
    EVIDENCE_QUALITY_WARNINGS_VISIBLE = "evidence_quality_warnings_visible"


class SemanticWarningType(str, Enum):
    """Typed warnings for semantic retrieval and clustering."""

    SIMILARITY_NOT_CONFIRMATION = "similarity_not_confirmation"
    SAME_LINEAGE_ECHO = "same_lineage_echo"
    MISSING_PROVENANCE = "missing_provenance"
    CONTESTED_MATCH = "contested_match"
    FICTIONAL_CONTAMINATION = "fictional_contamination"
    PARAPHRASE_NOT_INDEPENDENCE = "paraphrase_not_independence"


class AttentionSignal(str, Enum):
    """Signals used to calculate review salience, not truth confidence."""

    RELEVANCE = "relevance"
    NOVELTY = "novelty"
    CONTRADICTION_PRESSURE = "contradiction_pressure"
    PROVENANCE_FRAGILITY = "provenance_fragility"
    SOURCE_TRUST = "source_trust"
    SOURCE_INDEPENDENCE = "source_independence"
    TEMPORAL_IMPORTANCE = "temporal_importance"
    CONTAMINATION_RISK = "contamination_risk"
    RECURRENCE = "recurrence"
    UNCERTAINTY_LOAD = "uncertainty_load"
    USER_FOCUS_MATCH = "user_focus_match"


class AttentionWarningType(str, Enum):
    """Typed warnings emitted by attention guardrails."""

    SALIENCE_NOT_BELIEF = "salience_not_belief"
    CONTAMINATION_SALIENT_NOT_TRUSTED = "contamination_salient_not_trusted"
    SAME_LINEAGE_DOWNGRADED = "same_lineage_downgraded"
    CONTRADICTION_VISIBLE = "contradiction_visible"
    PROVENANCE_WARNING_VISIBLE = "provenance_warning_visible"
    ARCHIVAL_UNCERTAINTY_PRESERVED = "archival_uncertainty_preserved"
    FOCUS_DOES_NOT_OVERRIDE_PROVENANCE = "focus_does_not_override_provenance"
    SPECULATION_REMAINS_SPECULATION = "speculation_remains_speculation"


class AdversarialAttackVector(str, Enum):
    """Synthetic attack vectors against epistemic guardrails."""

    PROVENANCE_LAUNDERING = "provenance_laundering"
    SEMANTIC_ECHO_CHAMBER = "semantic_echo_chamber"
    DISCOURSE_CONTAMINATION = "discourse_contamination"
    CONFIDENCE_INFLATION = "confidence_inflation"
    CONTRADICTION_SUPPRESSION = "contradiction_suppression"
    SPECULATION_HARDENING = "speculation_hardening"
    SYNTHETIC_TO_REAL_CONFUSION = "synthetic_to_real_confusion"
    MISSING_PROVENANCE_CAMOUFLAGE = "missing_provenance_camouflage"
    TEMPORAL_OVERREACH = "temporal_overreach"
    POLICY_ABUSE = "policy_abuse"
    REVIEW_STATE_LAUNDERING = "review_state_laundering"
    PRESENTATION_AGGREGATION_TRAP = "presentation_aggregation_trap"
    MISSING_DATA_PRETTIFICATION = "missing_data_prettification"
    TRANSFERABILITY_LEAP = "transferability_leap"
    AUTHORITY_LAUNDERING = "authority_laundering"
    MULTILINGUAL_CERTAINTY_INFLATION = "multilingual_certainty_inflation"
    QUALITY_SCORE_LAUNDERING = "quality_score_laundering"


class AdversarialExpectedFailureMode(str, Enum):
    """Failure modes an adversarial scenario attempts to trigger."""

    FALSE_INDEPENDENCE = "false_independence"
    SIMILARITY_AS_CONFIRMATION = "similarity_as_confirmation"
    DISCOURSE_AS_EVIDENCE = "discourse_as_evidence"
    UNSUPPORTED_CONFIDENCE_INFLATION = "unsupported_confidence_inflation"
    HIDDEN_CONTRADICTION = "hidden_contradiction"
    SPECULATION_AS_FACT = "speculation_as_fact"
    SYNTHETIC_AS_REAL_EVIDENCE = "synthetic_as_real_evidence"
    PROVENANCE_GAP_HIDDEN = "provenance_gap_hidden"
    FABRICATED_TEMPORAL_PRECISION = "fabricated_temporal_precision"
    GUARDRAIL_DISABLED_BY_POLICY = "guardrail_disabled_by_policy"
    REVIEW_AS_CONFIRMATION = "review_as_confirmation"
    AGGREGATION_AS_CORROBORATION = "aggregation_as_corroboration"
    MISSING_AS_HARMLESS = "missing_as_harmless"
    TRANSFERABILITY_AS_OPERATIONAL_AUTHORITY = "transferability_as_operational_authority"
    INSPIRATION_AS_CERTIFICATION = "inspiration_as_certification"
    NON_ENGLISH_CERTAINTY_INFLATION = "non_english_certainty_inflation"
    QUALITY_AS_CONFIRMATION = "quality_as_confirmation"


class AdversarialCalibrationErrorType(str, Enum):
    """Known wording-detector calibration categories."""

    REVIEW_STATE_LAUNDERING = "review_state_laundering"
    BENIGN_PROVENANCE_BOUNDARY = "benign_provenance_boundary"
    OVERBROAD_AUTHORITY_LANGUAGE = "overbroad_authority_language"
    SUBTLE_CERTAINTY_INFLATION = "subtle_certainty_inflation"
    MULTILINGUAL_CERTAINTY = "multilingual_certainty"
    NEGATED_CONFIRMATION_LANGUAGE = "negated_confirmation_language"
    TRANSFERABILITY_PRESSURE = "transferability_pressure"
    PRESENTATION_AGGREGATION_TRAP = "presentation_aggregation_trap"
    BENIGN_SAFETY_BOUNDARY = "benign_safety_boundary"
    TECHNICAL_INSPIRATION_BOUNDARY = "technical_inspiration_boundary"


class HardAdversarialOutcome(str, Enum):
    """Honest outcomes for hard adversarial tests."""

    RESISTED = "resisted"
    NEAR_MISS = "near_miss"
    FAILED_EXPECTED = "failed_expected"
    FAILED_UNEXPECTED = "failed_unexpected"
    INCONCLUSIVE = "inconclusive"


class OWASPLLMRisk(str, Enum):
    """OWASP LLM Top 10 inspired risk categories mapped to Cortex."""

    LLM01_PROMPT_INJECTION = "LLM01_prompt_injection"
    LLM02_SENSITIVE_INFORMATION_DISCLOSURE = "LLM02_sensitive_information_disclosure"
    LLM04_DATA_AND_MODEL_POISONING = "LLM04_data_and_model_poisoning"
    LLM05_IMPROPER_OUTPUT_HANDLING = "LLM05_improper_output_handling"
    LLM06_EXCESSIVE_AGENCY = "LLM06_excessive_agency"
    LLM08_VECTOR_AND_EMBEDDING_WEAKNESSES = "LLM08_vector_and_embedding_weaknesses"
    LLM09_MISINFORMATION = "LLM09_misinformation"
    LLM10_UNBOUNDED_CONSUMPTION = "LLM10_unbounded_consumption"


class ArtifactType(str, Enum):
    """Artifact roles kept separate by the reality boundary layer."""

    EVIDENCE = "evidence"
    CLAIM = "claim"
    REASONING_OUTPUT = "reasoning_output"
    DISCOURSE_OUTPUT = "discourse_output"
    SEMANTIC_CLUSTER = "semantic_cluster"
    SPECULATIVE_HYPOTHESIS = "speculative_hypothesis"
    RETRIEVAL_RESULT = "retrieval_result"
    SYNTHETIC_EVALUATION = "synthetic_evaluation"
    EXTERNAL_INPUT = "external_input"


@dataclass(slots=True)
class CognitiveArtifact:
    """Generated or imported artifact whose epistemic role must not drift."""

    artifact_id: str
    artifact_type: ArtifactType | str
    content: str = ""
    source_artifact_ids: set[str] = field(default_factory=set)
    source_evidence_ids: set[str] = field(default_factory=set)
    provenance_ids: set[str] = field(default_factory=set)
    layer_origin: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.artifact_type, str):
            self.artifact_type = ArtifactType(self.artifact_type)


@dataclass(slots=True)
class InferenceBoundaryRecord:
    """Queryable provenance for a cognitive artifact."""

    artifact_id: str
    artifact_type: ArtifactType | str
    source_artifact_ids: set[str] = field(default_factory=set)
    source_evidence_ids: set[str] = field(default_factory=set)
    provenance_ids: set[str] = field(default_factory=set)
    reasoning_layer_origin: str | None = None
    discourse_layer_origin: str | None = None
    semantic_layer_origin: str | None = None
    synthetic_scenario_origin: str | None = None
    depth: int = 0
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.artifact_type, str):
            self.artifact_type = ArtifactType(self.artifact_type)


@dataclass(slots=True)
class RecursiveInferenceWarning:
    """Warning emitted when inference begins citing itself."""

    warning_type: str
    message: str
    artifact_ids: set[str] = field(default_factory=set)
    severity: str = "warning"


@dataclass(slots=True)
class RealityBoundaryViolation:
    """A blocked boundary crossing or unsafe cognitive promotion."""

    violation_type: str
    message: str
    artifact_ids: set[str] = field(default_factory=set)
    blocked: bool = True


@dataclass(slots=True)
class CognitiveSeparationState:
    """Current artifact registry state plus boundary findings."""

    artifacts: dict[str, CognitiveArtifact] = field(default_factory=dict)
    boundary_records: dict[str, InferenceBoundaryRecord] = field(default_factory=dict)
    warnings: list[RecursiveInferenceWarning] = field(default_factory=list)
    violations: list[RealityBoundaryViolation] = field(default_factory=list)


@dataclass(slots=True)
class AttentionWarning:
    """Attention warning that keeps review priority separate from belief."""

    warning_type: AttentionWarningType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.warning_type, str):
            self.warning_type = AttentionWarningType(self.warning_type)


@dataclass(slots=True)
class SalienceScore:
    """Bounded salience score for review priority, not evidence confidence."""

    component_scores: dict[AttentionSignal | str, float] = field(default_factory=dict)
    final_salience_score: float = 0.0
    reason_codes: list[str] = field(default_factory=list)
    warnings: list[AttentionWarning] = field(default_factory=list)
    bounded: bool = True

    def __post_init__(self) -> None:
        self.component_scores = {
            AttentionSignal(key) if isinstance(key, str) else key: max(0.0, min(1.0, value))
            for key, value in self.component_scores.items()
        }
        self.final_salience_score = max(0.0, min(1.0, self.final_salience_score))


@dataclass(slots=True)
class AttentionCandidate:
    """A record or artifact candidate for review-priority scoring."""

    record_id: str
    record_type: str
    label: str = ""
    text: str = ""
    tags: set[str] = field(default_factory=set)
    entity_ids: set[str] = field(default_factory=set)
    event_ids: set[str] = field(default_factory=set)
    claim_topics: set[str] = field(default_factory=set)
    source_id: str | None = None
    lineage_id: str | None = None
    provenance_ids: set[str] = field(default_factory=set)
    contradiction_pressure: float = 0.0
    contamination_risk: float = 0.0
    source_trust: float = 0.5
    source_independence: float = 0.5
    recurrence: float = 0.0
    novelty: float = 0.5
    temporal_importance: float = 0.0
    uncertainty_load: float = 0.0
    archived: bool = False
    contested: bool = False
    speculative: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AttentionPolicy:
    """Named deterministic salience policy with immutable guardrail flags."""

    name: str
    weights: dict[AttentionSignal, float] = field(default_factory=dict)
    preserve_contradictions: bool = True
    preserve_provenance_warnings: bool = True
    preserve_association_not_confirmation: bool = True
    preserve_reality_boundaries: bool = True


@dataclass(slots=True)
class AttentionFocus:
    """Current investigation focus used to calculate salience."""

    query_text: str = ""
    focus_terms: set[str] = field(default_factory=set)
    target_entities: set[str] = field(default_factory=set)
    target_event_ids: set[str] = field(default_factory=set)
    target_claim_topics: set[str] = field(default_factory=set)
    time_window: tuple[date | None, date | None] | None = None
    investigation_mode: str = "conservative"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AttentionDecision:
    """Ranked attention output; deferred records are not deleted."""

    selected_records: list[AttentionCandidate] = field(default_factory=list)
    selected_for_context: list[AttentionCandidate] = field(default_factory=list)
    selected_for_review: list[AttentionCandidate] = field(default_factory=list)
    deferred_records: list[AttentionCandidate] = field(default_factory=list)
    archived_records_considered: list[AttentionCandidate] = field(default_factory=list)
    salience_by_id: dict[str, SalienceScore] = field(default_factory=dict)
    attention_warnings: list[AttentionWarning] = field(default_factory=list)


@dataclass(slots=True)
class SnapshotMetadata:
    """Metadata for an immutable persistence snapshot."""

    snapshot_id: str
    created_at: datetime
    schema_version: str
    record_counts: dict[str, int] = field(default_factory=dict)
    checksum: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PersistenceManifest:
    """Manifest that identifies the snapshot format and producer."""

    metadata: SnapshotMetadata
    saved_by: str = "roswell_uap_cortex"
    format: str = "json_snapshot"


@dataclass(slots=True)
class PersistenceRecord:
    """Serialized record wrapper preserving unknown fields."""

    record_type: str
    payload: dict[str, Any]
    record_id: str | None = None
    unknown_fields: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PersistenceEnvelope:
    """Top-level immutable snapshot envelope."""

    manifest: PersistenceManifest
    records: dict[str, list[PersistenceRecord]] = field(default_factory=dict)


@dataclass(slots=True)
class SaveResult:
    """Result of saving a persistence snapshot."""

    path: str
    envelope: PersistenceEnvelope
    checksum: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    success: bool = True


@dataclass(slots=True)
class LoadResult:
    """Result of loading a persistence snapshot."""

    path: str
    envelope: PersistenceEnvelope | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    success: bool = True


@dataclass(slots=True)
class SessionAuditRecord:
    """One deterministic review-session audit event."""

    event_type: str
    session_id: str
    item_id: str | None = None
    item_type: str | None = None
    notes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))
    record_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id:
            self.record_id = str(uuid5(NAMESPACE_URL, f"session-audit:{self.session_id}:{self.event_type}:{self.item_type}:{self.item_id}:{'|'.join(self.notes)}"))


@dataclass(slots=True)
class SessionAuditTrail:
    """Ordered audit records for review-session workflow."""

    session_id: str
    records: list[SessionAuditRecord] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SessionPersistenceEnvelope:
    """Persisted session state plus audit trail."""

    manifest: PersistenceManifest
    sessions: list["ReviewSession"] = field(default_factory=list)
    audit_trails: list[SessionAuditTrail] = field(default_factory=list)
    records: dict[str, list[PersistenceRecord]] = field(default_factory=dict)


@dataclass(slots=True)
class SessionSaveResult:
    """Result of saving session persistence data."""

    path: str
    envelope: SessionPersistenceEnvelope
    checksum: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    success: bool = True


@dataclass(slots=True)
class SessionLoadResult:
    """Result of loading session persistence data."""

    path: str
    envelope: SessionPersistenceEnvelope | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    success: bool = True


@dataclass(slots=True)
class ReviewBundleWarning:
    """Warning emitted while building or formatting a review bundle."""

    warning_type: str
    message: str
    related_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class ReviewBundleSection:
    """A deterministic section in an exportable review bundle."""

    section_id: str
    title: str
    items: list[str] = field(default_factory=list)
    related_ids: set[str] = field(default_factory=set)
    warnings: list[ReviewBundleWarning] = field(default_factory=list)


@dataclass(slots=True)
class ReviewBundleManifest:
    """Manifest for review bundle exports."""

    bundle_id: str
    created_at: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))
    schema_version: str = "phase-22-review-bundle-v1"
    section_counts: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReviewBundle:
    """Structured review bundle; not a final report or conclusion."""

    manifest: ReviewBundleManifest
    sections: list[ReviewBundleSection] = field(default_factory=list)
    warnings: list[ReviewBundleWarning] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReviewBundleExportResult:
    """Result of formatting/exporting a review bundle."""

    bundle: ReviewBundle
    content: str = ""
    warnings: list[ReviewBundleWarning] = field(default_factory=list)
    success: bool = True


@dataclass(slots=True)
class DemoWorkspaceManifest:
    """Manifest for a fully synthetic demo workspace."""

    demo_id: str
    title: str = "Synthetic Cortex Demo Workspace"
    synthetic_only: bool = True
    schema_version: str = "phase-23-demo-workspace-v1"
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DemoWorkspace:
    """Synthetic raw workspace inputs for demonstration only."""

    manifest: DemoWorkspaceManifest
    raw_inputs: list["RawInput"] = field(default_factory=list)


@dataclass(slots=True)
class DemoWorkspaceResult:
    """Canonical synthetic demo output across the Cortex pipeline."""

    workspace: DemoWorkspace
    ingestion_results: list["IngestionResult"] = field(default_factory=list)
    candidate_claims: list["CandidateClaim"] = field(default_factory=list)
    normalized_claims: list["NormalizedClaim"] = field(default_factory=list)
    claim_evaluation: "ClaimEvaluationResult | None" = None
    claim_review_docket: "ClaimReviewDocket | None" = None
    source_review_docket: "SourceReviewDocket | None" = None
    review_session: "ReviewSession | None" = None
    audit_trail: SessionAuditTrail | None = None
    review_bundle: ReviewBundle | None = None
    formatted_bundle: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PresentationWarning:
    """Warning emitted for read-only presentation/view-model output."""

    warning_type: str
    message: str
    related_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class WorkflowStageView:
    """Display-ready workflow stage; not executable workflow state."""

    stage_id: str
    title: str
    status: str = "available"
    summary: str = ""
    related_ids: set[str] = field(default_factory=set)
    warnings: list[PresentationWarning] = field(default_factory=list)


@dataclass(slots=True)
class ClaimReviewCardView:
    """Display-ready claim review card; not claim truth state."""

    claim_id: str
    canonical_topic: str
    text: str
    priority: str = "low"
    priority_score: float = 0.0
    unsupported: bool = True
    confidence_label: str = "not_truth_confidence"
    support_count: int = 0
    contradiction_count: int = 0
    uncertainty_count: int = 0
    provenance_ids: set[str] = field(default_factory=set)
    lineage_ids: set[str] = field(default_factory=set)
    warnings: list[PresentationWarning] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.priority_score = max(0.0, min(1.0, self.priority_score))


@dataclass(slots=True)
class SourceReviewCardView:
    """Display-ready source review card; not source acceptance or rejection."""

    source_id: str
    priority: str = "low"
    priority_score: float = 0.0
    risk_score: float = 0.0
    reliability_score: float = 0.0
    evidence_count: int = 0
    provenance_ids: set[str] = field(default_factory=set)
    lineage_ids: set[str] = field(default_factory=set)
    contamination_flags: set[str] = field(default_factory=set)
    warnings: list[PresentationWarning] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.priority_score = max(0.0, min(1.0, self.priority_score))
        self.risk_score = max(0.0, min(1.0, self.risk_score))
        self.reliability_score = max(0.0, min(1.0, self.reliability_score))


@dataclass(slots=True)
class SessionTimelineView:
    """Display-ready review session timeline; not audit evidence."""

    session_id: str
    events: list[str] = field(default_factory=list)
    reviewed_ids: set[str] = field(default_factory=set)
    deferred_ids: set[str] = field(default_factory=set)
    unresolved_ids: set[str] = field(default_factory=set)
    warnings: list[PresentationWarning] = field(default_factory=list)


@dataclass(slots=True)
class BundlePreviewView:
    """Display-ready review bundle preview; not a final report."""

    bundle_id: str
    section_titles: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    warnings: list[PresentationWarning] = field(default_factory=list)


@dataclass(slots=True)
class ReviewDashboardView:
    """Read-only dashboard-shaped view of review workflow state."""

    title: str
    synthetic_only: bool = False
    stages: list[WorkflowStageView] = field(default_factory=list)
    claim_cards: list[ClaimReviewCardView] = field(default_factory=list)
    source_cards: list[SourceReviewCardView] = field(default_factory=list)
    session_timeline: SessionTimelineView | None = None
    bundle_preview: BundlePreviewView | None = None
    unresolved_ids: set[str] = field(default_factory=set)
    deferred_ids: set[str] = field(default_factory=set)
    contradiction_ids: set[str] = field(default_factory=set)
    uncertainty_notes: list[str] = field(default_factory=list)
    provenance_refs: set[str] = field(default_factory=set)
    warnings: list[PresentationWarning] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DemoPresentation:
    """Synthetic demo presentation fixture for future UI work."""

    demo_id: str
    dashboard: ReviewDashboardView
    formatted_bundle_preview: str = ""
    boundary_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvaluationInput:
    """Artifacts inspected by the deterministic evaluation harness."""

    activated_context: "ActivatedContext | None" = None
    reasoning_output: "ReasoningOutput | None" = None
    discourse_response: "DiscourseResponse | None" = None
    persistence_envelope: PersistenceEnvelope | None = None
    evidence_items: list["EvidenceItem"] = field(default_factory=list)
    claims: list["ClaimNode"] = field(default_factory=list)
    lineage_records: list["SourceLineageRecord"] = field(default_factory=list)
    cognitive_state: CognitiveSeparationState | None = None
    attention_decision: AttentionDecision | None = None
    normalized_claims: list["NormalizedClaim"] = field(default_factory=list)
    review_influence: ReviewInfluenceResult | None = None
    review_dashboard: ReviewDashboardView | None = None
    demo_presentation: DemoPresentation | None = None
    evidence_quality_assessments: list["EvidenceQualityAssessment"] = field(default_factory=list)
    before_state_hash: str | None = None
    after_state_hash: str | None = None


@dataclass(slots=True)
class EvaluationExpectedBehavior:
    """A behavior expectation for a scenario."""

    behavior: ExpectedBehaviorType
    description: str = ""


@dataclass(slots=True)
class EvaluationScenario:
    """Synthetic scenario for evaluating epistemic framework behavior."""

    scenario_id: str
    title: str
    description: str
    inputs: EvaluationInput
    expected_behaviors: list[EvaluationExpectedBehavior]
    tags: set[str] = field(default_factory=set)
    risk_level: str = "medium"


@dataclass(slots=True)
class EvaluationFailure:
    """A structured failed behavior result."""

    scenario_id: str
    behavior: ExpectedBehaviorType
    message: str
    related_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class EvaluationMetric:
    """A bounded aggregate metric."""

    name: str
    value: float
    description: str = ""


@dataclass(slots=True)
class EvaluationResult:
    """Per-scenario evaluation result."""

    scenario_id: str
    behavior_results: dict[ExpectedBehaviorType, bool] = field(default_factory=dict)
    failures: list[EvaluationFailure] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(self.behavior_results.values()) if self.behavior_results else False


@dataclass(slots=True)
class EvaluationReport:
    """Aggregate evaluation report for synthetic scenarios."""

    results: list[EvaluationResult] = field(default_factory=list)
    metrics: list[EvaluationMetric] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    overall_pass_rate: float = 0.0


@dataclass(slots=True)
class AdversarialScenario:
    """Tiny synthetic adversarial stress scenario; never real-world validation."""

    scenario_id: str
    title: str
    attack_vector: AdversarialAttackVector | str
    expected_failure_mode: AdversarialExpectedFailureMode | str
    description: str = ""
    inputs: EvaluationInput = field(default_factory=EvaluationInput)
    expected_behaviors: list[ExpectedBehaviorType] = field(default_factory=list)
    tags: set[str] = field(default_factory=set)
    risk_level: str = "adversarial_synthetic"

    def __post_init__(self) -> None:
        if isinstance(self.attack_vector, str):
            self.attack_vector = AdversarialAttackVector(self.attack_vector)
        if isinstance(self.expected_failure_mode, str):
            self.expected_failure_mode = AdversarialExpectedFailureMode(self.expected_failure_mode)


@dataclass(slots=True)
class AdversarialFinding:
    """Observed outcome for one adversarial scenario."""

    scenario_id: str
    attack_vector: AdversarialAttackVector
    expected_failure_mode: AdversarialExpectedFailureMode
    resisted: bool
    triggered_behaviors: list[ExpectedBehaviorType] = field(default_factory=list)
    failed_behaviors: list[ExpectedBehaviorType] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AdversarialReport:
    """Aggregate adversarial stress-test report."""

    findings: list[AdversarialFinding] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    @property
    def scenario_count(self) -> int:
        return len(self.findings)

    @property
    def resisted_count(self) -> int:
        return sum(1 for finding in self.findings if finding.resisted)

    @property
    def resistance_rate(self) -> float:
        if not self.findings:
            return 0.0
        return self.resisted_count / len(self.findings)


@dataclass(slots=True)
class AdversarialCalibrationCase:
    """One detector-calibration case for adversarial wording."""

    case_id: str
    text: str
    expected_attack: bool
    detected_attack: bool = False
    language: str = "en"
    error_type: AdversarialCalibrationErrorType | str = AdversarialCalibrationErrorType.SUBTLE_CERTAINTY_INFLATION
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.error_type, str):
            self.error_type = AdversarialCalibrationErrorType(self.error_type)


@dataclass(slots=True)
class AdversarialCalibrationReport:
    """Confusion-matrix style calibration for adversarial wording checks."""

    cases: list[AdversarialCalibrationCase] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    @property
    def true_positives(self) -> int:
        return sum(1 for case in self.cases if case.expected_attack and case.detected_attack)

    @property
    def true_negatives(self) -> int:
        return sum(1 for case in self.cases if not case.expected_attack and not case.detected_attack)

    @property
    def false_positives(self) -> int:
        return sum(1 for case in self.cases if not case.expected_attack and case.detected_attack)

    @property
    def false_negatives(self) -> int:
        return sum(1 for case in self.cases if case.expected_attack and not case.detected_attack)

    @property
    def accuracy(self) -> float:
        if not self.cases:
            return 0.0
        return (self.true_positives + self.true_negatives) / len(self.cases)

    @property
    def precision(self) -> float:
        denominator = self.true_positives + self.false_positives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator

    @property
    def recall(self) -> float:
        denominator = self.true_positives + self.false_negatives
        if denominator == 0:
            return 0.0
        return self.true_positives / denominator

    @property
    def false_positive_rate(self) -> float:
        denominator = self.false_positives + self.true_negatives
        if denominator == 0:
            return 0.0
        return self.false_positives / denominator

    @property
    def false_negative_rate(self) -> float:
        denominator = self.false_negatives + self.true_positives
        if denominator == 0:
            return 0.0
        return self.false_negatives / denominator

    @property
    def multilingual_case_count(self) -> int:
        return sum(1 for case in self.cases if case.language != "en")

    @property
    def known_limitation_count(self) -> int:
        return sum(1 for case in self.cases if case.notes)


@dataclass(slots=True)
class HardAdversarialScenario:
    """OWASP-inspired hard stress scenario with expected honest outcome."""

    scenario_id: str
    title: str
    owasp_risk: OWASPLLMRisk | str
    attack_vector: AdversarialAttackVector | str
    expected_failure_mode: AdversarialExpectedFailureMode | str
    expected_outcome: HardAdversarialOutcome | str
    description: str = ""
    inputs: EvaluationInput = field(default_factory=EvaluationInput)
    expected_behaviors: list[ExpectedBehaviorType] = field(default_factory=list)
    near_miss_reason: str = ""
    tags: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.owasp_risk, str):
            self.owasp_risk = OWASPLLMRisk(self.owasp_risk)
        if isinstance(self.attack_vector, str):
            self.attack_vector = AdversarialAttackVector(self.attack_vector)
        if isinstance(self.expected_failure_mode, str):
            self.expected_failure_mode = AdversarialExpectedFailureMode(self.expected_failure_mode)
        if isinstance(self.expected_outcome, str):
            self.expected_outcome = HardAdversarialOutcome(self.expected_outcome)


@dataclass(slots=True)
class HardAdversarialFinding:
    """Observed hard adversarial result with calibration notes."""

    scenario_id: str
    owasp_risk: OWASPLLMRisk
    attack_vector: AdversarialAttackVector
    expected_failure_mode: AdversarialExpectedFailureMode
    outcome: HardAdversarialOutcome
    expected_outcome: HardAdversarialOutcome
    passed_behaviors: list[ExpectedBehaviorType] = field(default_factory=list)
    failed_behaviors: list[ExpectedBehaviorType] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class HardAdversarialReport:
    """Aggregate hard adversarial report with non-perfect outcomes allowed."""

    findings: list[HardAdversarialFinding] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    @property
    def scenario_count(self) -> int:
        return len(self.findings)

    def outcome_counts(self) -> dict[HardAdversarialOutcome, int]:
        counts = {outcome: 0 for outcome in HardAdversarialOutcome}
        for finding in self.findings:
            counts[finding.outcome] += 1
        return counts

    @property
    def calibration_passed(self) -> bool:
        outcomes = {finding.outcome for finding in self.findings}
        return HardAdversarialOutcome.RESISTED in outcomes and any(
            outcome in outcomes
            for outcome in (
                HardAdversarialOutcome.NEAR_MISS,
                HardAdversarialOutcome.FAILED_EXPECTED,
                HardAdversarialOutcome.INCONCLUSIVE,
            )
        )


@dataclass(slots=True)
class EmbeddingVector:
    """A deterministic embedding vector container."""

    values: list[float]
    model: str = "mock"


@dataclass(slots=True)
class SemanticWarning:
    """A warning emitted by semantic infrastructure."""

    warning_type: SemanticWarningType
    message: str
    related_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class SemanticRecord:
    """Record prepared for controlled semantic comparison."""

    record_id: str
    text: str
    record_role: str = "unknown"
    tags: set[str] = field(default_factory=set)
    entity_ids: set[str] = field(default_factory=set)
    provenance_ids: set[str] = field(default_factory=set)
    source_id: str | None = None
    lineage_id: str | None = None
    contradiction_pressure: float = 0.0
    contested: bool = False
    contamination_flags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SemanticSimilarityResult:
    """Semantic similarity result; score is not truth confidence."""

    record_a_id: str
    record_b_id: str
    similarity_score: float
    similarity_reason: list[str] = field(default_factory=list)
    source_independence: float = 0.0
    lineage_overlap: bool = False
    contradiction_pressure: float = 0.0
    warning_flags: list[SemanticWarning] = field(default_factory=list)


@dataclass(slots=True)
class SemanticCluster:
    """A possible related semantic cluster, never equivalence or confirmation."""

    cluster_id: str
    member_ids: set[str] = field(default_factory=set)
    cluster_label: str = "possible_related_cluster"
    duplicate_lineage_ids: set[str] = field(default_factory=set)
    contested_member_ids: set[str] = field(default_factory=set)
    warnings: list[SemanticWarning] = field(default_factory=list)


@dataclass(slots=True)
class HybridRetrievalResult:
    """Hybrid retrieval output preserving component scores separately."""

    record_id: str
    associative_score: float = 0.0
    graph_score: float = 0.0
    timeline_score: float = 0.0
    semantic_similarity_score: float = 0.0
    provenance_visible: bool = False
    ranking_score: float = 0.0
    uncertainty_notes: list[str] = field(default_factory=list)
    semantic_warnings: list[SemanticWarning] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceItem:
    """A source-backed artifact or observation, never a truth claim by itself."""

    summary: str
    source_id: str
    evidence_type: str
    category: EvidenceCategory = EvidenceCategory.UNSUPPORTED_CLAIM
    observed_at: datetime | None = None
    recorded_at: datetime = field(default_factory=utc_now)
    id: str = field(default_factory=lambda: str(uuid4()))
    confidence: float = 0.5
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvidenceQualityDimensionScores:
    """Separated evidence-condition signals; no dimension is a truth score."""

    provenance_completeness: float = 0.0
    lineage_clarity: float = 0.0
    source_transparency: float = 0.0
    observation_directness: float = 0.0
    contamination_resistance: float = 0.0
    contradiction_stability: float = 0.0
    temporal_specificity: float = 0.0
    extraction_confidence: float = 0.0

    def __post_init__(self) -> None:
        self.provenance_completeness = max(0.0, min(1.0, self.provenance_completeness))
        self.lineage_clarity = max(0.0, min(1.0, self.lineage_clarity))
        self.source_transparency = max(0.0, min(1.0, self.source_transparency))
        self.observation_directness = max(0.0, min(1.0, self.observation_directness))
        self.contamination_resistance = max(0.0, min(1.0, self.contamination_resistance))
        self.contradiction_stability = max(0.0, min(1.0, self.contradiction_stability))
        self.temporal_specificity = max(0.0, min(1.0, self.temporal_specificity))
        self.extraction_confidence = max(0.0, min(1.0, self.extraction_confidence))


@dataclass(slots=True)
class EvidenceQualityWarning:
    """A quality warning that keeps uncertainty visible."""

    warning_type: EvidenceQualityWarningType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.warning_type, str):
            self.warning_type = EvidenceQualityWarningType(self.warning_type)


@dataclass(slots=True)
class EvidenceQualityAssessment:
    """Bounded review assessment of evidence condition, not truth confidence."""

    evidence_id: str
    dimension_scores: EvidenceQualityDimensionScores
    quality_label: EvidenceQualityLabel | str
    quality_score: float = 0.0
    review_priority_score: float = 0.0
    provenance_ids: set[str] = field(default_factory=set)
    lineage_id: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    warnings: list[EvidenceQualityWarning] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.quality_label, str):
            self.quality_label = EvidenceQualityLabel(self.quality_label)
        self.quality_score = max(0.0, min(1.0, self.quality_score))
        self.review_priority_score = max(0.0, min(1.0, self.review_priority_score))


@dataclass(slots=True)
class RawInput:
    """Raw sensory input before normalization into evidence records."""

    input_id: str
    input_type: RawInputType | str = RawInputType.UNKNOWN
    title: str | None = None
    raw_text: str = ""
    source_uri: str | None = None
    source_kind: str = "unknown"
    collected_at: datetime | None = None
    declared_event_hint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.input_type, str):
            self.input_type = RawInputType(self.input_type)


@dataclass(slots=True)
class ExtractedObservation:
    """A deterministic observation span extracted from raw text."""

    input_id: str
    text: str
    sequence: int
    id: str = ""
    start_offset: int | None = None
    end_offset: int | None = None
    evidence_id: str | None = None
    observation_type: ObservationType = ObservationType.UNKNOWN
    interpretation_markers: list[str] = field(default_factory=list)
    speculation_markers: list[str] = field(default_factory=list)
    reported_speech_markers: list[str] = field(default_factory=list)
    classification_notes: list[str] = field(default_factory=list)
    extraction_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.observation_type, str):
            self.observation_type = ObservationType(self.observation_type)
        if not self.id:
            self.id = str(uuid5(NAMESPACE_URL, f"observation:{self.input_id}:{self.sequence}:{self.text}"))


@dataclass(slots=True)
class ProvenanceRecord:
    """Mandatory provenance for ingested evidence."""

    evidence_id: str
    source_uri: str
    source_kind: str
    ingestion_method: str
    extraction_method: str
    original_input_id: str
    id: str = ""
    extracted_span: tuple[int, int] | None = None
    page_number: int | None = None
    timestamp_range: tuple[str, str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = str(uuid5(NAMESPACE_URL, f"provenance:{self.original_input_id}:{self.evidence_id}"))


@dataclass(slots=True)
class SourceLineageRecord:
    """Lineage assigned during ingestion so repetition remains visible."""

    evidence_id: str
    source_id: str
    lineage_id: str
    lineage_type: LineageType = LineageType.UNKNOWN_LINEAGE
    source_uri: str | None = None
    parent_source_id: str | None = None
    derived_from: str | None = None
    duplicate_source_uri: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ContaminationFlag:
    """A deterministic warning about source quality or contamination risk."""

    flag_type: ContaminationFlagType
    input_id: str
    evidence_id: str | None = None
    source_uri: str | None = None
    note: str = ""


@dataclass(slots=True)
class IngestionResult:
    """Auditable output of deterministic raw-input normalization."""

    raw_input_id: str
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    observations: list[ExtractedObservation] = field(default_factory=list)
    provenance_records: list[ProvenanceRecord] = field(default_factory=list)
    lineage_records: list[SourceLineageRecord] = field(default_factory=list)
    contamination_flags: list[ContaminationFlag] = field(default_factory=list)
    source_trust_hints: dict[str, Any] = field(default_factory=dict)
    ingestion_warnings: list[str] = field(default_factory=list)
    ingestion_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimExtractionWarning:
    """Warning that extraction created a candidate, not confirmation."""

    warning_type: ClaimExtractionWarningType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.warning_type, str):
            self.warning_type = ClaimExtractionWarningType(self.warning_type)


@dataclass(slots=True)
class CandidateClaim:
    """A claim-like statement extracted for review, initially unsupported."""

    text: str
    canonical_topic: str
    origin: CandidateClaimOrigin | str
    source_observation_id: str | None = None
    source_evidence_id: str | None = None
    provenance_ids: set[str] = field(default_factory=set)
    observation_type: ObservationType = ObservationType.UNKNOWN
    status: ClaimMatrixStatus = ClaimMatrixStatus.UNSUPPORTED
    confidence: float = 0.0
    speculative: bool = False
    extraction_notes: list[str] = field(default_factory=list)
    warnings: list[ClaimExtractionWarning] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.origin, str):
            self.origin = CandidateClaimOrigin(self.origin)
        if isinstance(self.observation_type, str):
            self.observation_type = ObservationType(self.observation_type)
        if not self.id:
            self.id = str(uuid5(NAMESPACE_URL, f"candidate-claim:{self.origin.value}:{self.text}"))


@dataclass(slots=True)
class ClaimExtractionPolicy:
    """Deterministic extraction policy; extraction never confirms claims."""

    extract_from_direct_observation: bool = True
    extract_from_reported_claim: bool = True
    extract_from_interpretation: bool = True
    extract_from_speculation: bool = True
    extract_from_metadata: bool = False
    require_provenance_note: bool = True


@dataclass(slots=True)
class ClaimExtractionResult:
    """Candidate claims plus warnings produced by deterministic extraction."""

    candidate_claims: list[CandidateClaim] = field(default_factory=list)
    warnings: list[ClaimExtractionWarning] = field(default_factory=list)
    extraction_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ClaimCanonicalKey:
    """Deterministic key for grouping candidate claims."""

    value: str
    origin_bucket: str
    token_fingerprint: tuple[str, ...] = ()


@dataclass(slots=True)
class ClaimNormalizationWarning:
    """Warning emitted during claim normalization or matrix integration."""

    warning_type: ClaimNormalizationWarningType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.warning_type, str):
            self.warning_type = ClaimNormalizationWarningType(self.warning_type)


@dataclass(slots=True)
class NormalizedClaim:
    """Canonical candidate-claim group; organization, not validation."""

    normalized_claim_id: str
    canonical_key: ClaimCanonicalKey
    canonical_text: str
    candidate_claim_ids: set[str] = field(default_factory=set)
    origin_types: set[CandidateClaimOrigin] = field(default_factory=set)
    evidence_ids: set[str] = field(default_factory=set)
    provenance_ids: set[str] = field(default_factory=set)
    lineage_ids: set[str] = field(default_factory=set)
    warning_flags: list[ClaimNormalizationWarning] = field(default_factory=list)
    unsupported: bool = True
    confidence: float = 0.0
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimNormalizationPolicy:
    """Controls cautious candidate-claim grouping."""

    allow_cross_origin_merge: bool = False
    allow_metadata_event_merge: bool = False
    isolate_speculation: bool = True
    isolate_metadata: bool = True


@dataclass(slots=True)
class ClaimNormalizationResult:
    """Normalized claims plus grouping warnings."""

    normalized_claims: list[NormalizedClaim] = field(default_factory=list)
    warnings: list[ClaimNormalizationWarning] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimMatrixIntegrationResult:
    """Result of safely registering normalized claims in the claim matrix."""

    registered_topics: set[str] = field(default_factory=set)
    claim_node_ids: set[str] = field(default_factory=set)
    warnings: list[ClaimNormalizationWarning] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimEvaluationWarning:
    """Warning attached to a claim/evidence assessment."""

    warning_type: ClaimEvaluationWarningType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.warning_type, str):
            self.warning_type = ClaimEvaluationWarningType(self.warning_type)


@dataclass(slots=True)
class ClaimSupportSignal:
    """Possible support signal; not confirmation."""

    evidence_id: str
    score: float = 0.0
    reason_codes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimContradictionSignal:
    """Possible contradiction signal; not disproof."""

    evidence_id: str
    score: float = 0.0
    reason_codes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimUncertaintySignal:
    """Uncertainty signal that should remain visible."""

    evidence_id: str
    score: float = 0.0
    reason_codes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimEvidenceAssessment:
    """Deterministic relation assessment between a normalized claim and evidence."""

    normalized_claim_id: str
    evidence_id: str
    observation_id: str | None = None
    provenance_ids: set[str] = field(default_factory=set)
    lineage_id: str | None = None
    support_score: float = 0.0
    contradiction_score: float = 0.0
    uncertainty_score: float = 0.0
    independence_score: float = 0.0
    assessment_type: ClaimEvidenceAssessmentType = ClaimEvidenceAssessmentType.IRRELEVANT
    reason_codes: list[str] = field(default_factory=list)
    warnings: list[ClaimEvaluationWarning] = field(default_factory=list)


@dataclass(slots=True)
class ClaimEvaluationPolicy:
    """Thresholds for conservative evidence assessment."""

    support_threshold: float = 0.35
    contradiction_threshold: float = 0.35
    review_threshold: float = 0.35
    speculative_support_cap: float = 0.3
    reported_support_cap: float = 0.45
    metadata_support_cap: float = 0.0


@dataclass(slots=True)
class ClaimEvaluationResult:
    """Claim evidence assessments and warnings."""

    assessments: list[ClaimEvidenceAssessment] = field(default_factory=list)
    support_signals: list[ClaimSupportSignal] = field(default_factory=list)
    contradiction_signals: list[ClaimContradictionSignal] = field(default_factory=list)
    uncertainty_signals: list[ClaimUncertaintySignal] = field(default_factory=list)
    warnings: list[ClaimEvaluationWarning] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceAssessmentSummary:
    """Compact evidence assessment summary for claim review dockets."""

    evidence_id: str
    assessment_type: ClaimEvidenceAssessmentType | str
    support_score: float = 0.0
    contradiction_score: float = 0.0
    uncertainty_score: float = 0.0
    independence_score: float = 0.0
    provenance_ids: set[str] = field(default_factory=set)
    lineage_id: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    warning_types: list[ClaimEvaluationWarningType] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.assessment_type, str):
            self.assessment_type = ClaimEvidenceAssessmentType(self.assessment_type)
        self.support_score = max(0.0, min(1.0, self.support_score))
        self.contradiction_score = max(0.0, min(1.0, self.contradiction_score))
        self.uncertainty_score = max(0.0, min(1.0, self.uncertainty_score))
        self.independence_score = max(0.0, min(1.0, self.independence_score))


@dataclass(slots=True)
class ReviewRecommendation:
    """A cautious next-step recommendation for human review."""

    recommendation_type: ReviewRecommendationType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.recommendation_type, str):
            self.recommendation_type = ReviewRecommendationType(self.recommendation_type)


@dataclass(slots=True)
class ClaimReviewItem:
    """Review item for one normalized claim."""

    normalized_claim_id: str
    canonical_topic: str
    canonical_text: str
    priority: ReviewPriority | str = ReviewPriority.LOW
    priority_score: float = 0.0
    support_summaries: list[EvidenceAssessmentSummary] = field(default_factory=list)
    contradiction_summaries: list[EvidenceAssessmentSummary] = field(default_factory=list)
    uncertainty_summaries: list[EvidenceAssessmentSummary] = field(default_factory=list)
    irrelevant_evidence_ids: set[str] = field(default_factory=set)
    provenance_ids: set[str] = field(default_factory=set)
    lineage_ids: set[str] = field(default_factory=set)
    warning_types: list[ClaimEvaluationWarningType] = field(default_factory=list)
    recommendations: list[ReviewRecommendation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    unsupported: bool = True
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if isinstance(self.priority, str):
            self.priority = ReviewPriority(self.priority)
        self.priority_score = max(0.0, min(1.0, self.priority_score))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass(slots=True)
class ClaimReviewDocket:
    """Deterministic claim review package; presentation, not truth state."""

    docket_id: str
    title: str
    items: list[ClaimReviewItem] = field(default_factory=list)
    citations: list[DiscourseCitation] = field(default_factory=list)
    warnings: list[ClaimEvaluationWarning] = field(default_factory=list)
    recommendations: list[ReviewRecommendation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ClaimReviewQueue:
    """Priority-ordered review dockets."""

    dockets: list[ClaimReviewDocket] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Claim:
    """An assertion derived from evidence, with explicit uncertainty."""

    text: str
    evidence_ids: set[str] = field(default_factory=set)
    id: str = field(default_factory=lambda: str(uuid4()))
    status: ClaimStatus = ClaimStatus.UNASSESSED
    confidence: float = 0.5
    uncertainty_notes: str = ""
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class EntityNode:
    """A person, organization, place, object, or concept mentioned by evidence."""

    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    entity_type: str = "unknown"
    aliases: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EventNode:
    """A dated or undated event without fabricated chronology."""

    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    event_date: date | None = None
    earliest_possible_date: date | None = None
    latest_possible_date: date | None = None
    date_precision: TimelineDatePrecision = TimelineDatePrecision.UNKNOWN
    date_note: str = ""
    evidence_ids: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ClaimNode:
    """A graph-ready claim separated from its supporting evidence."""

    text: str
    canonical_topic: str
    id: str = field(default_factory=lambda: str(uuid4()))
    evidence_ids: set[str] = field(default_factory=set)
    status: ClaimMatrixStatus = ClaimMatrixStatus.UNSUPPORTED
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SourceNode:
    """A source as a first-class graph node."""

    source_id: str
    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    source_type: str = "unknown"
    trust_score: float = 0.5
    lineage_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RelationshipEdge:
    """A provenance-carrying relationship between two graph nodes."""

    from_node_id: str
    to_node_id: str
    relation: RelationshipType
    source_id: str
    confidence: float = 0.5
    evidence_ids: set[str] = field(default_factory=set)
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class AssociationScore:
    """Deterministic association signals; not a truth score."""

    lexical_overlap: float = 0.0
    tag_overlap: float = 0.0
    entity_overlap: float = 0.0
    timeline_proximity: float = 0.0
    source_independence: float = 0.0
    contradiction_penalty: float = 0.0
    final_association_score: float = 0.0


@dataclass(slots=True)
class AssociationCandidate:
    """A possible retrieval association with inspectable reasons."""

    record_id: str
    record_type: str
    label: str
    score: AssociationScore
    association_label: AssociationLabel = AssociationLabel.POSSIBLE_ASSOCIATION
    association_reason: list[str] = field(default_factory=list)
    memory_ids: set[str] = field(default_factory=set)
    claim_ids: set[str] = field(default_factory=set)
    evidence_ids: set[str] = field(default_factory=set)
    entity_ids: set[str] = field(default_factory=set)
    source_id: str | None = None
    lineage_id: str | None = None
    claim_status: ClaimMatrixStatus | None = None
    uncertainty_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetrievalContext:
    """Optional query-side context for deterministic associative retrieval."""

    query: str
    query_tags: set[str] = field(default_factory=set)
    query_entity_ids: set[str] = field(default_factory=set)
    query_canonical_topics: set[str] = field(default_factory=set)
    query_date: date | None = None
    source_id: str | None = None
    lineage_id: str | None = None


@dataclass(slots=True)
class ActivatedContext:
    """A focused retrieval context for downstream deterministic reasoning."""

    activated_memory_ids: set[str] = field(default_factory=set)
    activated_claim_ids: set[str] = field(default_factory=set)
    activated_evidence_ids: set[str] = field(default_factory=set)
    activated_entity_ids: set[str] = field(default_factory=set)
    weak_associations: list[AssociationCandidate] = field(default_factory=list)
    contested_associations: list[AssociationCandidate] = field(default_factory=list)
    uncertainty_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class UncertaintyNote:
    """A structured uncertainty note carried through reasoning."""

    note: str
    related_ids: set[str] = field(default_factory=set)
    severity: str = "caution"


@dataclass(slots=True)
class ReasoningWarning:
    """A guardrail warning emitted by reasoning."""

    warning_type: ReasoningWarningType
    message: str
    related_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class ReasoningObservation:
    """A bounded observation made from supplied context only."""

    text: str
    context_ids: set[str] = field(default_factory=set)
    speculative: bool = False


@dataclass(slots=True)
class ReasoningContext:
    """Compact structured context passed into local reasoning."""

    activated_context: ActivatedContext
    selected_candidates: list[AssociationCandidate] = field(default_factory=list)
    evidence_items: list[EvidenceItem] = field(default_factory=list)
    claims: list[ClaimNode] = field(default_factory=list)
    memories: list["MemoryRecord"] = field(default_factory=list)
    provenance_records: list[ProvenanceRecord] = field(default_factory=list)
    lineage_records: list[SourceLineageRecord] = field(default_factory=list)
    uncertainty_notes: list[UncertaintyNote] = field(default_factory=list)


@dataclass(slots=True)
class ReasoningRequest:
    """A bounded local reasoning request."""

    query: str
    activated_context: ActivatedContext
    candidates: list[AssociationCandidate] = field(default_factory=list)
    max_context_items: int = 8


@dataclass(slots=True)
class ReasoningOutput:
    """Structured local reasoning output; confidence band is not truth confidence."""

    observations: list[ReasoningObservation] = field(default_factory=list)
    supporting_context_ids: set[str] = field(default_factory=set)
    contested_context_ids: set[str] = field(default_factory=set)
    uncertainty_notes: list[UncertaintyNote] = field(default_factory=list)
    reasoning_warnings: list[ReasoningWarning] = field(default_factory=list)
    possible_hypotheses: list[ReasoningObservation] = field(default_factory=list)
    confidence_band: ConfidenceBand = ConfidenceBand.INSUFFICIENT_CONTEXT
    provenance_summary: str = ""
    requires_review: bool = False


@dataclass(slots=True)
class DiscourseCitation:
    """Deterministic citation bound to evidence, source, provenance, or lineage."""

    evidence_id: str | None = None
    source_id: str | None = None
    lineage_id: str | None = None
    provenance_id: str | None = None
    page_number: int | None = None
    timestamp_range: tuple[str, str] | None = None
    label: str = ""


@dataclass(slots=True)
class DiscourseWarning:
    """A warning emitted by discourse guardrails."""

    warning_type: DiscourseWarningType
    message: str
    related_ids: set[str] = field(default_factory=set)


@dataclass(slots=True)
class DiscourseSection:
    """A compact explainable section for investigative review."""

    title: str
    items: list[str] = field(default_factory=list)
    citations: list[DiscourseCitation] = field(default_factory=list)
    warnings: list[DiscourseWarning] = field(default_factory=list)


@dataclass(slots=True)
class InvestigativeNarrative:
    """Deterministic narrative separated by epistemic role."""

    observations: str = ""
    interpretations: str = ""
    speculation: str = ""
    uncertainty: str = ""


@dataclass(slots=True)
class DiscourseRequest:
    """Request to transform reasoning into human-review discourse."""

    query: str
    activated_context: ActivatedContext
    reasoning_output: ReasoningOutput


@dataclass(slots=True)
class DiscourseResponse:
    """Structured discourse output for human review."""

    observed_evidence: DiscourseSection
    possible_associations: DiscourseSection
    contradictions: DiscourseSection
    weak_associations: DiscourseSection
    speculative_hypotheses: DiscourseSection
    provenance_notes: DiscourseSection
    uncertainty_summary: DiscourseSection
    missing_information: DiscourseSection
    reasoning_warnings: list[ReasoningWarning] = field(default_factory=list)
    citations: list[DiscourseCitation] = field(default_factory=list)
    narrative: InvestigativeNarrative = field(default_factory=InvestigativeNarrative)
    review_required: bool = False


@dataclass(slots=True)
class SourceTrust:
    """Trust metadata for a source, separate from individual evidence confidence."""

    source_id: str
    reliability: float = 0.5
    transparency: float = 0.5
    corroboration_history: float = 0.5
    source_authority: float = 0.5
    chain_of_custody: float = 0.5
    publication_distance: float = 0.5
    redaction_level: float = 0.0
    independent_corroboration: float = 0.0
    media_type: str = "unknown"
    contamination_flags: list[str] = field(default_factory=list)
    source_trust_score: float = 0.5
    source_risk_score: float = 0.5
    uncertainty_notes: str = ""
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class SourceReliabilitySignal:
    """Positive source-review signal; not proof the source is true."""

    signal_type: str
    score: float = 0.0
    message: str = ""
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.score = max(0.0, min(1.0, self.score))


@dataclass(slots=True)
class SourceRiskSignal:
    """Source-review risk signal; not source rejection."""

    signal_type: str
    score: float = 0.0
    message: str = ""
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.score = max(0.0, min(1.0, self.score))


@dataclass(slots=True)
class SourceReviewRecommendation:
    """A bounded source-review recommendation."""

    recommendation_type: SourceReviewRecommendationType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.recommendation_type, str):
            self.recommendation_type = SourceReviewRecommendationType(self.recommendation_type)


@dataclass(slots=True)
class SourceReviewItem:
    """Review item for one source id."""

    source_id: str
    priority: SourceReviewPriority | str = SourceReviewPriority.LOW
    priority_score: float = 0.0
    reliability_score: float = 0.0
    risk_score: float = 0.0
    evidence_ids: set[str] = field(default_factory=set)
    provenance_ids: set[str] = field(default_factory=set)
    lineage_ids: set[str] = field(default_factory=set)
    contamination_flags: set[ContaminationFlagType] = field(default_factory=set)
    reliability_signals: list[SourceReliabilitySignal] = field(default_factory=list)
    risk_signals: list[SourceRiskSignal] = field(default_factory=list)
    recommendations: list[SourceReviewRecommendation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.priority, str):
            self.priority = SourceReviewPriority(self.priority)
        self.priority_score = max(0.0, min(1.0, self.priority_score))
        self.reliability_score = max(0.0, min(1.0, self.reliability_score))
        self.risk_score = max(0.0, min(1.0, self.risk_score))
        self.contamination_flags = {
            ContaminationFlagType(flag) if isinstance(flag, str) else flag
            for flag in self.contamination_flags
        }


@dataclass(slots=True)
class SourceReviewDocket:
    """Deterministic source review package; not source truth or rejection."""

    docket_id: str
    title: str
    items: list[SourceReviewItem] = field(default_factory=list)
    citations: list[DiscourseCitation] = field(default_factory=list)
    recommendations: list[SourceReviewRecommendation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReviewFocus:
    """Current focus of a review session."""

    query: str = ""
    focus_ids: set[str] = field(default_factory=set)
    claim_topics: set[str] = field(default_factory=set)
    source_ids: set[str] = field(default_factory=set)
    evidence_ids: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReviewedItem:
    """A human-review annotation that does not mutate the reviewed record."""

    item_id: str
    item_type: str
    reviewed_at: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))
    notes: list[str] = field(default_factory=list)
    decision_id: str | None = None


@dataclass(slots=True)
class DeferredItem:
    """A deferred review item that remains visible."""

    item_id: str
    item_type: str
    reason: str = ""
    deferred_at: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))
    decision_id: str | None = None


@dataclass(slots=True)
class ReviewDecision:
    """A deterministic review annotation, not confirmation or rejection."""

    item_id: str
    item_type: str
    decision_type: ReviewDecisionType | str
    notes: list[str] = field(default_factory=list)
    reviewer: str = "human"
    decision_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))

    def __post_init__(self) -> None:
        if isinstance(self.decision_type, str):
            self.decision_type = ReviewDecisionType(self.decision_type)
        if not self.decision_id:
            self.decision_id = str(uuid5(NAMESPACE_URL, f"review-decision:{self.item_type}:{self.item_id}:{self.decision_type.value}:{'|'.join(self.notes)}"))


@dataclass(slots=True)
class ReviewStateSignal:
    """A review workflow signal allowed to guide attention, context, or discourse."""

    signal_type: str
    item_id: str
    item_type: str = "unknown"
    allowed_scopes: set[ReviewInfluenceScope | str] = field(default_factory=set)
    priority: float = 0.0
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.allowed_scopes = {
            ReviewInfluenceScope(scope) if isinstance(scope, str) else scope
            for scope in self.allowed_scopes
        }
        self.priority = max(0.0, min(1.0, self.priority))


@dataclass(slots=True)
class ReviewInfluenceWarning:
    """Boundary warning emitted while adapting review state for downstream use."""

    warning_type: ReviewInfluenceWarningType | str
    message: str
    related_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if isinstance(self.warning_type, str):
            self.warning_type = ReviewInfluenceWarningType(self.warning_type)


@dataclass(slots=True)
class ReviewInfluenceResult:
    """Read-only influence contract from review workflow to later layers."""

    signals: list[ReviewStateSignal] = field(default_factory=list)
    prioritized_ids: set[str] = field(default_factory=set)
    must_include_ids: set[str] = field(default_factory=set)
    deferred_ids: set[str] = field(default_factory=set)
    unresolved_ids: set[str] = field(default_factory=set)
    provenance_gap_ids: set[str] = field(default_factory=set)
    source_review_warning_ids: set[str] = field(default_factory=set)
    contradiction_ids: set[str] = field(default_factory=set)
    uncertainty_notes: list[str] = field(default_factory=list)
    discourse_annotations: list[str] = field(default_factory=list)
    warnings: list[ReviewInfluenceWarning] = field(default_factory=list)


@dataclass(slots=True)
class ReviewSessionState:
    """Active working-memory state for a review session."""

    active_focus: ReviewFocus = field(default_factory=ReviewFocus)
    active_claim_docket_ids: set[str] = field(default_factory=set)
    active_source_docket_ids: set[str] = field(default_factory=set)
    active_context_ids: set[str] = field(default_factory=set)
    reviewed_items: list[ReviewedItem] = field(default_factory=list)
    deferred_items: list[DeferredItem] = field(default_factory=list)
    unresolved_item_ids: set[str] = field(default_factory=set)
    uncertainty_notes: list[str] = field(default_factory=list)
    contradiction_ids: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SessionDelta:
    """Deterministic description of a review-session update."""

    session_id: str
    added_reviewed_ids: set[str] = field(default_factory=set)
    added_deferred_ids: set[str] = field(default_factory=set)
    added_unresolved_ids: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReviewSession:
    """A review session over working memory; annotation state only."""

    session_id: str
    title: str
    state: ReviewSessionState = field(default_factory=ReviewSessionState)
    decisions: list[ReviewDecision] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime(1970, 1, 1, tzinfo=timezone.utc))
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceLineageRecord:
    """A deterministic source lineage node for a claim or evidence item."""

    source_id: str
    claim_key: str
    id: str = field(default_factory=lambda: str(uuid4()))
    original_source_id: str | None = None
    parent_source_id: str | None = None
    source_kind: str = "unknown"
    transformations: list[str] = field(default_factory=list)
    contamination_flags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.original_source_id is None:
            self.original_source_id = self.source_id


@dataclass(slots=True)
class ContaminationReport:
    """Flags contamination risk without deleting or resolving the record."""

    record_id: str
    flags: list[str] = field(default_factory=list)
    risk_score: float = 0.0


@dataclass(slots=True)
class CorroborationAssessment:
    """Distinguish independent corroboration from repeated sourcing."""

    claim_key: str
    independent_source_ids: list[str] = field(default_factory=list)
    repeated_source_ids: list[str] = field(default_factory=list)
    independent_count: int = 0
    repeated_count: int = 0
    corroboration_score: float = 0.0


@dataclass(slots=True)
class MemoryRecord:
    """A bounded memory with provenance, decay state, and duplicate merge support."""

    content: str
    evidence_ids: set[str] = field(default_factory=set)
    id: str = field(default_factory=lambda: str(uuid4()))
    normalized_key: str | None = None
    strength: float = 0.5
    memory_strength: float = 0.5
    decay_rate: float = 0.03
    contradiction_pressure: float = 0.0
    archival: bool = False
    access_count: int = 0
    activation_count: int = 0
    consistency_count: int = 1
    created_at: datetime = field(default_factory=utc_now)
    last_accessed_at: datetime = field(default_factory=utc_now)
    last_activated_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    linked_memory_ids: list[str] = field(default_factory=list)
    needs_review: bool = False
    uncertainty_preserved: bool = False
    source_confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.normalized_key is None:
            self.normalized_key = self.content_key(self.content)
        if self.memory_strength == 0.5 and self.strength != 0.5:
            self.memory_strength = self.strength
        self.strength = self.memory_strength

    @staticmethod
    def content_key(content: str) -> str:
        return " ".join(content.casefold().strip().split())


@dataclass(slots=True)
class GraphNode:
    """A graph node for evidence-first investigative reasoning."""

    node_type: GraphNodeType
    label: str
    id: str = field(default_factory=lambda: str(uuid4()))
    related_ids: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Contradiction:
    """An explicit unresolved conflict between claims or evidence records."""

    subject_id: str
    conflicting_id: str
    reason: str
    id: str = field(default_factory=lambda: str(uuid4()))
    severity: float = 0.5
    resolved: bool = False
    created_at: datetime = field(default_factory=utc_now)
