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

`observation_classifier.py` contains the deterministic marker rules used by
ingestion. The classifier records markers and notes on `ExtractedObservation`,
then ingestion copies those fields into evidence metadata.

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
4. `associative.py` and `attention.py`
5. `context_builder.py` and `reasoning.py`
6. `discourse.py`
7. `persistence.py` and `snapshot.py`
8. `evaluation.py`, `adversarial.py`, and `hard_adversarial.py`

That order follows the main architecture path and makes the framework easier to
understand.
