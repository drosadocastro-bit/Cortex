# Code Walkthrough

This document explains how the current code works at a practical level. It is
written for maintainers who want to understand the moving parts without turning
the framework into a product manual.

## The Big Idea

Cortex stores and moves structured uncertainty. It does not decide truth.

Most modules do one of four things:

- create records
- connect records
- rank records for review
- preserve warnings, provenance, and uncertainty while records move downstream

## Core Models

`src/roswell_uap_cortex/models.py` is the center of the project. It defines the
dataclasses and enums shared by all engines.

Important record families:

- `EvidenceItem`: a source-backed observation or artifact.
- `ProvenanceRecord`: where an evidence item came from.
- `SourceLineageRecord`: how a source relates to earlier sources.
- `MemoryRecord`: a remembered investigative item with strength and decay.
- `ClaimNode`: a claim separated from evidence.
- `RelationshipEdge`: a graph edge with source, confidence, evidence ids, and
  notes.
- `ActivatedContext`: focused retrieval context for reasoning.
- `ReasoningOutput`: bounded reasoning output, not truth.
- `DiscourseResponse`: structured human-review output.
- `CognitiveArtifact`: a generated or imported artifact with a protected
  epistemic type.

The models are intentionally plain dataclasses so they can be serialized,
tested, and inspected.

## Ingestion

`ingestion.py` contains `IngestionNormalizer`.

It accepts a `RawInput` and produces an `IngestionResult`.

The normalizer:

- splits raw text into deterministic observations
- classifies each observation span as direct observation, interpretation,
  speculation, reported claim, metadata statement, or unknown
- creates `EvidenceItem` records
- attaches provenance through `ProvenanceExtractor`
- assigns source lineage through `LineageTracker`
- runs contamination checks through `ContaminationDetector`

What it does not do:

- it does not confirm claims
- it does not create graph edges
- it does not call an LLM
- it does not decide whether the raw input is true

`observation_classifier.py` contains `ObservationClassifier`, the deterministic
marker rules used by ingestion. The classifier records markers and notes on
`ExtractedObservation`, then ingestion copies those fields into evidence
metadata.

## Candidate Claim Extraction

`claim_extraction.py` contains `ClaimExtractionEngine`.

It reads classified `ExtractedObservation` records and optional evidence and
provenance maps. It produces `CandidateClaim` records for review.

Candidate claims preserve:

- source observation id
- source evidence id
- provenance ids
- observation type
- origin such as `from_reported_claim` or `from_speculation`
- extraction warnings

Every candidate claim starts unsupported with confidence `0.0`. Extraction does
not create graph edges, support relationships, or claim confirmation.

## Claim Normalization

`claim_normalization.py` contains `ClaimNormalizer`.

It groups `CandidateClaim` records by deterministic canonical keys. Keys use
tokenized claim text plus an origin bucket so speculation and metadata stay
isolated by default.

`NormalizedClaim` records preserve:

- candidate claim ids
- source evidence ids
- provenance ids
- lineage ids
- origin types
- warnings

`claim_matrix_integration.py` contains `ClaimMatrixIntegrator`. It registers
normalized claims as unsupported candidate topics in `ClaimMatrixEngine`.
Integration does not add supporting evidence, contradiction evidence, graph
edges, or confidence.

## Claim Evidence Evaluation

`claim_evaluation.py` contains `ClaimEvidenceEvaluator`.

It compares `NormalizedClaim` records with `EvidenceItem` records and produces
bounded assessment records:

- possible support
- possible contradiction
- uncertain
- irrelevant
- needs review

The evaluator uses deterministic token overlap, observation classification,
provenance visibility, lineage visibility, and contradiction markers. It emits
warnings when support must not be read as confirmation, contradiction must not
be read as disproof, provenance is missing, evidence is speculative or
reported, metadata is being evaluated, or same-lineage repetition is present.

`claim_contradiction_evaluator.py` contains small deterministic contradiction
checks for negation, mutually exclusive terms, and date mismatch.

`claim_evaluation_guardrails.py` keeps the output language cautious.

`ClaimMatrixEngine.register_evidence_assessments()` can consume assessment
results, but it still keeps support and contradiction separate. Duplicate
same-lineage evidence is grouped before scoring and does not create independent
corroboration.

## Claim Review Workflow

`claim_review.py` contains `ClaimReviewEngine`.

It turns normalized claims plus `ClaimEvaluationResult` records into
`ClaimReviewDocket` packages for human inspection. A docket keeps possible
support, possible contradiction, uncertainty, irrelevant evidence, citations,
lineage ids, warning types, and recommendations separate.

`review_priority.py` contains `ReviewPriorityEngine`. It scores review priority
from contradiction visibility, missing provenance, same-lineage repetition,
speculative or reported evidence, low independence, and uncertainty signals.
Review priority is not truth confidence.

`evidence_docket.py` contains `EvidenceDocketFormatter`. It renders compact
deterministic text and repeats the boundary that dockets do not confirm or
reject claims.

## Source Reliability Review

`source_review.py` contains `SourceReviewEngine`.

It groups `EvidenceItem` records by source id and builds `SourceReviewDocket`
packages. A source docket keeps evidence ids, provenance ids, lineage ids,
contamination flags, reliability signals, risk signals, and recommendations
separate.

`source_risk.py` contains `SourceRiskProfiler`. It creates bounded risk
signals from missing provenance, derivative lineage, repeated source URIs,
same-lineage repetition, contamination flags, speculative or reported content,
and source-trust risk inputs.

`source_review_formatter.py` contains `SourceReviewFormatter`. It renders the
docket while preserving the boundary that source review is not source truth,
source rejection, or claim confirmation.

## Working Memory And Review Sessions

`working_memory.py` contains `WorkingMemoryEngine`.

It builds `ReviewSessionState` from claim dockets, source dockets, activated
context, reasoning output, and discourse output. The state tracks active focus
ids, active docket ids, active context ids, reviewed items, deferred items,
unresolved items, contradiction ids, and uncertainty notes.

`review_session.py` contains `ReviewSessionEngine`. It starts deterministic
sessions, resumes existing session state, and records `ReviewDecision`
annotations. Decisions can mark items reviewed, deferred, unresolved, or in
need of more provenance or source review. They do not confirm claims or reject
sources.

`session_formatter.py` contains `SessionFormatter`, which renders compact
session reports while repeating the boundary that session state is workflow
annotation only.

## Session Persistence And Audit

`session_audit.py` contains `SessionAuditLogger`.

It creates deterministic audit records for session starts, resumes, decisions,
and report-formatting events. Audit records describe workflow activity only.

`session_persistence.py` contains `SessionPersistenceStore`. It saves
`ReviewSession` and `SessionAuditTrail` records into local JSON with a manifest,
schema version, record counts, deterministic snapshot id, and checksum. Loading
does not apply decisions to evidence, claims, sources, or graph records.

`session_audit_formatter.py` contains `SessionAuditFormatter`, which renders
audit events and their limitations.

## Review Bundles

`review_bundle.py` contains `ReviewBundleBuilder`.

It composes a `ReviewSession`, claim review dockets, source review dockets, and
an optional audit trail into a structured `ReviewBundle`. The bundle has
sections for session summary, active focus, dockets, unresolved items, deferred
items, uncertainty, contradictions, provenance, audit trail, and limitations.

`review_bundle_guardrails.py` contains `ReviewBundleGuardrails`. It warns about
certainty-inflating language and missing provenance, audit, contradiction, or
limitation sections.

`review_bundle_formatter.py` contains `ReviewBundleFormatter`, which renders
the bundle as bounded Markdown. The output is a review packet, not a final
report.

## Provenance, Lineage, And Contamination

`provenance.py` creates mandatory provenance records.

`lineage.py` assigns lineage ids and marks derivative or duplicate sources.

`contamination.py` emits deterministic warning flags for missing dates, missing
source URIs, derivative sources, speculative language, fictional contamination
terms, weak chain of custody, and related risks.

These warnings are carried forward. They are not conclusions.

## Memory

`memory.py` contains `MemoryDecayEngine`.

Memory records can:

- decay over time
- reinforce when duplicates merge
- become archival when weak
- preserve contradiction pressure

Memory strength is bounded and should not be read as truth confidence.

## Graph, Timeline, And Claims

`graph.py` contains the in-memory `RelationshipGraphEngine`.

It stores nodes and provenance-carrying relationship edges. Duplicate edges are
merged instead of accumulating.

`timeline.py` stores events with exact, partial, approximate, or unknown dates.
Unknown dates remain unknown.

`claim_matrix.py` groups claims by canonical topic and separates supporting
evidence from contradicting evidence. Same-lineage evidence does not count as
independent corroboration.

## Retrieval And Activation

`associative.py` computes deterministic possible associations using lexical
overlap, tags, entities, topics, timeline proximity, source independence, and
contradiction pressure.

`ActivationContextBuilder` turns top candidates into `ActivatedContext`.

Association means possible relevance. It is not support or confirmation.

## Attention

`attention.py`, `focus.py`, `salience_policy.py`, and `attention_gate.py`
implement review-priority scoring.

Attention can prioritize records because they are relevant, novel,
contradictory, provenance-fragile, contaminated, timeline-important, or matched
to the current focus.

`AttentionGate` separates:

- selected records
- selected-for-context records
- selected-for-review records
- deferred records
- archived records considered

Salience is not belief. Deferred does not mean irrelevant forever.

## Semantic Layer

`embedding_backend.py` defines an embedding backend abstraction and a
deterministic mock backend.

`semantic.py` compares `SemanticRecord` objects. It combines mock vector
similarity with lexical overlap, tags, entities, source independence, lineage
overlap, and contradiction pressure.

`semantic_clustering.py` groups possible related records, but clusters do not
imply equivalence.

`hybrid_retrieval.py` combines associative, graph, timeline, and semantic
signals while preserving component scores separately.

Semantic similarity is not confirmation.

## Reasoning

`context_builder.py` builds compact `ReasoningContext` objects from activated
context, candidates, evidence, claims, provenance, and lineage.

`reasoning.py` contains `CognitiveReasoningEngine`.

`mock_reasoner.py` provides deterministic structured output for tests.

Reasoning:

- preserves contradictions
- labels speculation
- carries uncertainty notes
- summarizes provenance
- does not mutate evidence, claims, graph, provenance, or lineage

The `confidence_band` field describes context support, not truth confidence.

## Discourse

`discourse.py` turns reasoning output into structured human-review sections:

- observed evidence
- possible associations
- contradictions
- weak associations
- speculative hypotheses
- provenance notes
- uncertainty summary
- missing information

`citations.py`, `narrative.py`, `uncertainty.py`, and
`discourse_guardrails.py` keep the output readable but bounded.

Discourse is not evidence.

## Persistence

`snapshot.py` builds `PersistenceEnvelope` snapshots.

`serialization.py` converts dataclasses to JSON-compatible dictionaries and can
restore known models.

`persistence.py` saves and loads local JSON snapshots.

`snapshot_validator.py` and `persistence_guardrails.py` check schema versions,
counts, checksums, provenance, lineage, contradiction pressure, and loaded
record boundaries.

Loading a snapshot does not create new truth state.

## Reality Boundary

`reality_boundary.py`, `artifact_registry.py`, `inference_provenance.py`,
`recursive_guard.py`, and `live_inference_guardrails.py` protect the boundary
between generated cognition and external evidence.

They prevent:

- discourse becoming evidence automatically
- reasoning mutating claims directly
- semantic clusters creating support edges
- synthetic evaluations becoming real-world evidence
- speculative hypotheses becoming evidence
- self-citation loops going unnoticed

## Evaluation And Adversarial Tests

`evaluation.py`, `metrics.py`, `scenarios.py`, and `evaluation_report.py`
provide deterministic synthetic behavior checks.

`adversarial.py` and `adversarial_scenarios.py` provide smoke-style
adversarial tests.

`hard_adversarial.py` and `hard_adversarial_scenarios.py` provide
OWASP-inspired hard tests with honest outcomes such as `near_miss`,
`failed_expected`, and `inconclusive`.

These tests measure framework behavior. They do not validate real-world claims.

## CLI

`cli.py` provides a small deterministic terminal harness. It creates synthetic
evidence, runs reasoning and discourse, and prints structured output.

It does not ingest real data, call a network service, or execute user prompts.

## How To Read The Code

Start with:

1. `models.py`
2. `ingestion.py`
3. `claim_matrix.py`, `graph.py`, and `timeline.py`
4. `claim_evaluation.py`
5. `claim_review.py`
6. `source_review.py`
7. `working_memory.py` and `review_session.py`
8. `session_persistence.py` and `session_audit.py`
9. `review_bundle.py`
10. `associative.py` and `attention.py`
11. `context_builder.py` and `reasoning.py`
12. `discourse.py`
13. `persistence.py` and `snapshot.py`
14. `evaluation.py`, `adversarial.py`, and `hard_adversarial.py`

That order follows the main architecture path and makes the framework easier to
understand.
