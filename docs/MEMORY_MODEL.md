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

Phase 14 adds deterministic observation classification at sensory intake.
`ObservationClassifier` labels extracted spans as direct observation,
interpretation, speculation, reported claim, metadata statement, or unknown.
The label and marker notes travel into evidence metadata so downstream layers do
not need to guess whether a span was observed, interpreted, reported, or
speculated.

Phase 15 adds deterministic candidate claim extraction. `ClaimExtractionEngine`
can create `CandidateClaim` records from classified observations, but extracted
claims begin unsupported with confidence `0.0`. Claim extraction preserves
origin, source observation id, evidence id, provenance ids, and warnings. It
does not create support, graph edges, or confirmation.

Phase 16 adds deterministic claim normalization and safe matrix integration.
`ClaimNormalizer` groups candidate claims by canonical keys while preserving
candidate ids, evidence ids, provenance ids, lineage ids, and origin types.
`ClaimMatrixIntegrator` registers normalized claims as unsupported candidate
topics only. It does not create support evidence, contradiction evidence, graph
edges, or confidence.

Phase 17 adds deterministic claim evidence evaluation. `ClaimEvidenceEvaluator`
compares normalized claims with evidence records and emits possible support,
possible contradiction, uncertainty, irrelevant, or needs-review assessments.
These assessments are review signals. They do not confirm claims, disprove
claims, create graph edges, or mutate evidence.

Phase 27 adds deterministic evidence-quality assessment. `EvidenceQualityEngine`
scores provenance completeness, lineage clarity, source transparency,
observation directness, contamination resistance, contradiction stability,
temporal specificity, and extraction confidence. Quality labels such as
`fragile`, `reviewable`, `strong_context`, and `contested` describe evidence
condition for review only. They do not confirm claims, create graph edges,
increase claim confidence, or erase uncertainty.

Phase 18 adds claim review dockets. `ClaimReviewEngine` packages normalized
claims, evidence assessments, and optional evidence-quality summaries into
`ClaimReviewDocket` records for human inspection. `ReviewPriorityEngine` orders
attention by contradiction pressure, missing provenance, same-lineage
repetition, speculative or reported evidence, uncertainty, and quality
fragility. Review priority is not truth confidence.

Phase 19 adds source reliability review dockets. `SourceReviewEngine` groups
evidence by source id and packages provenance ids, lineage ids, contamination
flags, evidence-quality summaries, reliability signals, risk signals, and recommendations into
`SourceReviewDocket` records. Source review is not source truth, source
rejection, or claim confirmation.

Phase 20 adds working memory and review session state. `WorkingMemoryEngine`
collects claim dockets, source dockets, activated context, reasoning output,
and discourse output into `ReviewSessionState`. `ReviewSessionEngine` records
review decisions and deterministic deltas. These session records are workflow
annotations, not evidence, claim confirmation, source rejection, or graph
mutation.

Phase 21 adds session persistence and audit trails. `SessionPersistenceStore`
saves `ReviewSession` and `SessionAuditTrail` records into deterministic local
JSON with manifest metadata, schema version, record counts, and checksum.
`SessionAuditLogger` records workflow events only. Loading a session snapshot
does not create evidence, claims, source truth, or graph edges.

Phase 22 adds review bundles. `ReviewBundleBuilder` composes sessions, claim
dockets, source dockets, audit trails, unresolved items, deferred items,
uncertainty notes, contradictions, provenance references, and limitations into
structured export packets. Phase 29 extends bundles with evidence-quality
summaries while keeping quality as review context only. A bundle is not a final
report and does not resolve claims or sources.

Phase 23 adds a synthetic demo workspace. `DemoWorkspaceBuilder` creates tiny
synthetic raw inputs and runs them through ingestion, claim extraction,
normalization, evaluation, claim/source review, working memory, audit, and
review bundle export. The demo is architecture exercise only, not real-world
validation.

The review workflow is mapped separately in `docs/WORKFLOW_MAP.md` to keep
claim dockets, source dockets, working memory, review sessions, audit trails,
bundles, and demo output from duplicating responsibility or implying truth.

Phase 24 adds a review-to-reasoning boundary. `ReviewInfluencePolicy` converts
review workflow state into attention, context, and discourse hints.
`ReviewContextAdapter` carries those hints as visibility and uncertainty notes.
These hints do not mutate evidence, confirm claims, alter source trust, create
graph edges, or change claim matrix confidence.

Phase 25 adds read-only presentation view models. `PresentationBuilder` and
`DemoPresentationBuilder` adapt review workflow and synthetic demo state into
display-ready records. Presentation preserves unsupported claims,
contradictions, deferred items, uncertainty, provenance, limitations, and
synthetic labels without creating evidence, claims, graph edges, review
decisions, or truth state.

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

## Offline Memory Consolidation And Dream Replay

Phase 31 adds `DreamReplayEngine` as a deterministic rest-cycle layer above the
existing memory mechanisms. Dream replay consumes existing `MemoryRecord`
objects and emits `DreamReplayResult` artifacts with consolidation notes,
duplicate candidates, stale-memory signals, contradiction visibility, archival
visibility, warnings, and bounded recommendations.

Dream replay coordinates memory review. It does not replace or secretly invoke
memory decay, memory activation, contradiction registration, or duplicate
merging. In particular:

- decay still decides how memory strength changes over time;
- merge still decides whether duplicate memories are actually collapsed;
- contradiction pressure still marks unresolved conflicts;
- dream replay only recommends what may deserve later review.

Dream artifacts are internal cognitive artifacts, not evidence. Replayed
memories do not become more true, repeated replay is not corroboration, and
recommendations do not mutate memory state.
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

`ClaimEvidenceEvaluator` can feed bounded assessment results into the claim
matrix through `register_evidence_assessments()`. Possible support and possible
contradiction remain separated, while mixed high support and contradiction
pressure becomes review pressure. Repeated same-lineage paraphrases are
downgraded before confidence is computed.

`ClaimReviewDocket` turns those assessment signals into a compact review
package with support summaries, contradiction summaries, uncertainty summaries,
citations, warnings, and recommendations. It does not change claim status or
create evidence relationships.

## Source Independence

`IndependenceScorer` helps distinguish independent corroboration from repeated
lineage. Same-lineage or same-source evidence contributes cautiously, while
separate primary sources can increase confidence more. Unknown lineage remains
medium-low because missing provenance is not confirmation.

`LineageTracker` assigns ingestion lineage ids before evidence reaches graph,
claim-matrix, or retrieval layers. Derivative records and repeated source URIs
share visible lineage metadata so later independence scoring can treat them
cautiously.

`SourceRiskProfiler` uses provenance visibility, derivative lineage, repeated
source URIs, same-lineage repetition, contamination flags, speculative or
reported content, and source-trust risk inputs to build bounded source-risk
signals. These signals guide review; they do not accept or reject a source.

`EvidenceQualityEngine` gathers evidence-condition signals into a bounded
assessment while keeping each dimension visible. Missing provenance, derivative
lineage, contamination flags, contradiction pressure, uncertain timing, and low
observation directness remain warnings rather than hidden deductions.

## Working Memory

Working memory is the active review workspace. It tracks what is currently in
focus, which dockets are active, which context ids are present, which items
have been reviewed, which items have been deferred, and which contradictions or
uncertainties remain unresolved.

Deferral is not deletion. Review is not confirmation. Session deltas describe
workflow changes only.

Session audit trails preserve review history across runs. They describe what
the workflow did, not what external reality is.

Review bundles are memory exports for inspection. They are useful for future UI
and sharing, but they remain bounded review state rather than conclusions.
Evidence-quality sections preserve record condition for review; they do not
turn quality labels into findings.

The demo workspace is useful for future UI because it gives a safe canonical
session to render without touching real data.

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

## Investigative Discourse

Phase 7 adds `DiscourseEngine`, `CitationFormatter`, `NarrativeBuilder`,
`UncertaintyFormatter`, and `DiscourseGuardrails`. Discourse transforms
activated context and bounded reasoning output into structured sections for
human review.

Discourse is separate from reasoning. It presents observed evidence, possible
associations, contradictions, weak associations, speculative hypotheses,
provenance notes, uncertainty summaries, missing information, reasoning
warnings, and citations without creating new evidence or confirming claims.

Narrative output is deterministic and separated into observations,
interpretations, speculation, and uncertainty. Provenance citations remain
visible, contradiction visibility is mandatory, and speculative content stays
labeled. The CLI harness provides terminal output only; future web interfaces
should render the same structured discourse rather than replacing it.

## Snapshot Persistence

Phase 8 adds `SnapshotBuilder`, `Serializer`, `PersistenceStore`,
`SnapshotValidator`, and `PersistenceGuardrails`. The persistence layer saves
evidence, memory, claims, graph records, provenance, lineage, activated context,
reasoning, and discourse into deterministic local JSON snapshots.

Snapshots include a manifest, schema version, record counts, checksum, and
notes. Loading a snapshot reconstructs records for review but does not create
new claims, graph edges, evidence, or truth state automatically.

Unknown fields are preserved for future migrations. Discourse remains persisted
as discourse, separate from evidence. Archived memories remain archived,
contradiction pressure is preserved, and provenance warnings remain visible.

## Evaluation Harness

Phase 8.1 adds `EvaluationHarness`, `EpistemicMetrics`, `ScenarioFactory`,
`EvaluationGuardrails`, and `EvaluationReportFormatter`. The harness uses tiny
synthetic scenarios to check whether the framework preserves its epistemic
rules under stress.

Evaluation measures behavior such as provenance visibility, contradiction
preservation, association-not-confirmation, same-lineage caution, uncertainty
exposure, bounded confidence, contamination warning visibility, and no state
mutation.

These metrics are not truth metrics. Passing synthetic scenarios does not
validate any real-world UAP conclusion or evidentiary claim. Every report
includes limitations.

## Graph And Temporal Infrastructure

Phase 9 adds `GraphBackend`, `NetworkXGraphBackend`, and
`TemporalReasoningHelper`. The original in-memory graph engine remains
available, while NetworkX provides deterministic traversal, contradiction
lookup, lineage paths, focused subgraphs, and temporal-link traversal behind an
abstraction.

Graph traversal is sorted and duplicate edges are deduplicated by source,
endpoint, and relationship type. Provenance metadata, evidence ids, edge types,
and contradiction relationships remain visible.

`TimelineEngine` now uses `python-dateutil` only through conservative wrappers.
Full ISO dates can become exact dates. Month, year, and fuzzy month hints become
approximate ranges with uncertainty notes. Unknown dates remain unknown.

Future graph databases should preserve the same backend interface and epistemic
guardrails.

## Controlled Semantic Layer

Phase 10 adds `EmbeddingBackend`, `MockEmbeddingBackend`,
`SemanticSimilarityEngine`, `SemanticClusterEngine`,
`HybridRetrievalCoordinator`, and `SemanticContaminationGuard`.

Semantic records carry role, provenance ids, lineage id, source id, tags,
entities, contradiction pressure, contested state, and contamination flags.
Similarity combines deterministic mock embedding similarity, lexical overlap,
tags, entities, source independence, lineage overlap, and contradiction
pressure.

Semantic similarity is not confirmation. Same-lineage echoes are downgraded,
missing provenance creates warnings, fictional contamination propagates, and
contested semantic matches remain visible.

Semantic clusters are labeled `possible_related_cluster`. They preserve member
ids, duplicate lineage ids, and contested member ids without implying
equivalence, support, or confirmation. Hybrid retrieval preserves associative,
graph, timeline, and semantic component scores separately.

## Reality Boundary

Phase 11 adds `CognitiveArtifact`, `InferenceProvenanceTracker`,
`CognitiveArtifactRegistry`, `RecursiveInferenceGuard`,
`RealityBoundaryEngine`, and `LiveInferenceSafetyGuard`.

The boundary layer separates evidence, claims, reasoning outputs, discourse
outputs, semantic clusters, speculative hypotheses, retrieval results,
synthetic evaluations, and external inputs. Generated cognition can be useful
for review, but it is not external reality.

Discourse cannot become evidence automatically. Reasoning outputs cannot mutate
claims directly. Semantic clusters cannot create graph support edges. Synthetic
evaluation artifacts remain synthetic, and speculative hypotheses remain
speculative.

Inference provenance chains remain queryable so recursive inference,
self-citation, discourse reuse, and semantic recursion can be detected before
future live inference systems are connected.

## Attention And Salience

Phase 12 adds `AttentionFocusBuilder`, `AttentionEngine`,
`SaliencePolicyEngine`, `AttentionGate`, and `AttentionGuardrails`.

Attention scores review priority across memories, evidence, claims, graph
nodes, semantic clusters, reasoning outputs, discourse artifacts, and cognitive
artifacts. Salience is not truth confidence. It is a bounded signal that helps
decide what deserves human or downstream review first.

Attention can boost contradiction pressure, fragile provenance, contamination
risk, temporal importance, novelty, recurrence, uncertainty load, and focus
matches. It can downgrade duplicate same-lineage records, low-novelty
repetition, and archived low-strength memories unless they become relevant
again.

`AttentionGate` separates records selected for context from records selected
for review. Noisy, contaminated, or fragile records may be highly salient for
review while remaining untrusted. Deferred records are not deleted and are not
declared irrelevant forever.

Policy presets change review ordering but cannot disable contradiction
visibility, provenance warnings, association-not-confirmation, or reality
boundary rules.

## Adversarial Epistemic Testing

Phase 13 adds `AdversarialHarness`, `AdversarialScenarioFactory`, and
`AdversarialReportFormatter`. These scenarios intentionally try to make the
framework confuse repetition, semantic similarity, discourse, synthetic
fixtures, speculation, weak provenance, or attention policy with evidence or
truth.

Adversarial findings are framework-behavior findings only. A resisted attack
means the current synthetic fixture triggered the expected guardrail. It does
not prove real-world validity, scientific accuracy, or claim truth.

Phase 13.1 adds an OWASP-inspired hard adversarial suite. Unlike the smoke
suite, hard findings are not expected to be perfect. Outcomes include
`resisted`, `near_miss`, `failed_expected`, `failed_unexpected`, and
`inconclusive` so the framework can document weaknesses without turning tests
into false assurance.

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

