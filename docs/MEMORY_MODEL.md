# Memory Model

The memory model treats investigation as uncertainty-preserving cognition. A
memory is not a truth claim. It is a weighted record with provenance, activation
history, contradiction pressure, and possible archival state.

## Sensory Memory

Sensory memory is the first landing zone for raw observations, notes, document
fragments, or reports. In the framework this is represented by `EvidenceItem`.
It records source, time, summary, tags, and confidence without asserting that
the observed content is true.

Phase 5 adds `RawInput`, `IngestionNormalizer`, and `ExtractedObservation` as
the sensory intake layer. Raw documents, transcripts, notes, and metadata are
normalized into evidence records with deterministic extraction notes.

Ingestion does not create claim confirmations, support edges, or truth
assertions. It records what was supplied and preserves uncertainty for later
reasoning.

## Provenance Extraction

`ProvenanceExtractor` creates a `ProvenanceRecord` for every ingested evidence
item. Provenance preserves source URI, source kind, ingestion method, extraction
method, original input id, extracted span, and optional page or timestamp
metadata.

Provenance is mandatory. If source information is missing, the missingness is
flagged and represented explicitly rather than erased.

## Attention Filtering

Attention filtering determines which evidence-backed memories become active.
Phase 1 models this through `MemoryActivationEngine`. Activation increments
`activation_count`, updates `last_activated_at`, and increases
`memory_strength` within a hard `0.0` to `1.0` bound.

## Episodic Memory

`MemoryRecord` represents an episodic investigative memory: a bounded remembered
idea connected to evidence ids, tags, activation state, contradiction pressure,
and related memories.

Important fields include:

- `memory_strength`: current cognitive weight.
- `activation_count`: repeated attention or use.
- `last_activated_at`: time anchor for decay.
- `contradiction_pressure`: unresolved conflict load.
- `archival`: low-prominence state for weak memories.
- `linked_memory_ids`: associative and contradiction links.
- `source_confidence`: optional source-confidence signal.

The legacy `strength` field remains aligned with `memory_strength` for backward
compatibility.

## Semantic Compression

`SemanticCompressionEngine` creates deterministic summaries from duplicate,
near-duplicate, or topic-equivalent memories. It does not use an LLM, vector
database, or probabilistic summarizer.

Compressed memories preserve:

- merged memory ids
- strongest tags
- total activation count
- average contradiction pressure
- highest source confidence when present

Compression reduces clutter without treating repetition as proof.

## Associative Activation

Activation strengthens memories that are repeatedly useful. This supports
working investigation patterns where relevant memories become easier to surface.
Activation is bounded so repetition cannot create certainty.

An archival memory may return to active status only when reactivation pushes its
strength across a clear threshold.

Phase 4 adds deterministic associative activation through
`AssociativeRetrievalEngine` and `ActivationContextBuilder`. Retrieval can
surface possible associations between memories, claims, evidence, and entities
using lexical overlap, shared tags, shared entities, canonical topics, timeline
proximity, source independence, and contradiction pressure.

Association is not confirmation. Retrieved candidates are labeled as possible,
weak, or contested associations, and no support relationship is created by
retrieval.

## Memory Decay

`MemoryDecayEngine` applies time-aware decay based on days since the last
activation. Unused memories gradually lose strength. Weak unused memories decay
faster, while contradiction pressure slows decay so unresolved conflicts are not
silently erased.

Memory strength is always clamped between `0.0` and `1.0`.

## Archival Transition

When a memory falls below the archival threshold, it is marked `archival=True`.
Archival records remain available for provenance, later review, and possible
reactivation. They are not deleted.

## Contradiction Preservation

`ContradictionPressureEngine` links conflicting memories and increases
`contradiction_pressure` on both records. It also marks records as needing review
and preserving uncertainty.

Contradictions are not automatically resolved. Neither memory overwrites the
other, and neither is deleted merely because conflict exists.

## Graph Relationships

`RelationshipGraphEngine` stores an in-memory investigative graph connecting
entities, events, claims, sources, evidence, and contradictions. Edges carry a
relationship type, source id, confidence, evidence ids, and notes so graph
context remains provenance-backed.

Supported edge types include `mentions`, `supports`, `contradicts`,
`references`, `same_event_candidate`, `temporal_before`, `temporal_after`,
`derived_from`, and `duplicate_of`.

## Timeline Memory

`TimelineEngine` treats events as first-class memory objects. Exact dates can be
ordered chronologically. Approximate or partial dates keep their uncertainty
through date ranges and notes. Unknown dates remain unknown and are not
fabricated for ordering.

## Claim Matrix

`ClaimMatrixEngine` groups claim nodes by canonical topic while keeping evidence
separate from the claim itself. It tracks supporting evidence, contradicting
evidence, source trust contribution, bounded claim confidence, and unresolved
status labels such as `unsupported`, `weakly_supported`, `contested`,
`supported`, and `unresolved`.

This preserves contradiction instead of forcing premature resolution.

## Source Independence

`IndependenceScorer` helps distinguish independent corroboration from repeated
lineage. Same-lineage or same-source evidence contributes cautiously, while
separate primary sources can increase confidence more. Unknown lineage remains
medium-low because missing provenance is not confirmation.

`LineageTracker` assigns ingestion lineage ids before evidence reaches graph,
claim-matrix, or retrieval layers. Derivative records and repeated source URIs
share visible lineage metadata so later independence scoring can treat them
cautiously.

## Contamination Flags

`ContaminationDetector` attaches deterministic warning flags such as
`missing_date`, `missing_source_uri`, `missing_title`, `derivative_source`,
`repeated_source_uri`, `anonymous_source`, `speculative_language`,
`fictional_contamination_terms`, and `weak_chain_of_custody`.

These flags are review signals, not conclusions. They help preserve uncertainty
at sensory intake time.

## Correlation Guard

`CorrelationGuard` keeps future retrieval and vector-correlation work from
turning similarity into confirmation. It downgrades high lexical overlap when
source independence is low, reduces association scores under contradiction
pressure, and adds caution notes for unknown lineage.

Weak associations remain available for review instead of being promoted to
support. Contested associations remain visible so contradiction is not filtered
out of activated context.

## Bounded Reasoning

Phase 6 adds `CognitiveReasoningEngine`, `ContextWindowBuilder`,
`ReasoningGuardrails`, and a deterministic `MockReasoner`. Reasoning operates
on activated context after retrieval and ingestion have already preserved
provenance, lineage, contamination flags, and contradiction state.

The local reasoning layer does not mutate evidence, claims, provenance, lineage,
or graph structures. It produces structured observations, uncertainty notes,
warnings, speculative hypotheses, a provenance summary, and a categorical
`confidence_band` that represents context support rather than truth.

Context windows are intentionally compact. They prioritize strong associations,
source diversity, contradiction visibility, timeline relevance, and lineage
diversity while trimming low-value duplicate lineage. This reduces
lost-in-the-middle risk before future local LLM or VLM components are added.

Reasoning guardrails keep unsupported claims unsupported, preserve contested
associations, label hypotheses as speculative, downgrade missing provenance,
and warn when fictional contamination or repeated lineage is present.

## Vector-Ready Design

The association score separates lexical, tag, entity, timeline, source
independence, contradiction, and final activation signals. Future embeddings can
be added as another retrieval signal, but vector similarity remains secondary to
provenance, lineage, contradiction preservation, and source independence.

## Retrieval Priority

Vector similarity may later help locate candidates, but it remains secondary.
Investigation should prefer:

1. Source provenance and trust.
2. Timeline placement.
3. Graph relationships.
4. Explicit contradiction state.
5. Vector similarity as an assistive index.

## AI Debt

Future AI-assisted features must preserve the same uncertainty constraints as
the deterministic engines. `docs/AI_DEBT.md` tracks known risks around
inference, provenance, semantic similarity, temporal parsing, scoring,
evaluation, and reporting.

New AI, ingestion, vector search, or generated-report features should address
the relevant debt entries before they are treated as complete.
