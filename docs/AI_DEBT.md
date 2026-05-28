# AI Debt Register

This project preserves uncertainty by design. AI debt tracks places where future
automation, retrieval, summarization, or scoring could accidentally make the
system appear more certain than the evidence allows.

Each item records the risk, current mitigation, future trigger, and a clear
constraint on what the system must not do.

## Inference Debt

Risk:
Future LLM-assisted extraction or summarization may turn ambiguous evidence into
clean claims that appear more resolved than the source material.

Current mitigation:
All current engines are deterministic. Claims remain separate from evidence, and
claim status labels preserve unsupported, contested, and unresolved states.

Future trigger:
Before adding LLM extraction, every generated claim must retain source spans,
evidence ids, uncertainty notes, and a review state.

Must not do:
Do not treat an LLM-generated claim as evidence.

## Local Reasoning Debt

Risk:
Future local inference through Nemotron, LM Studio, Ollama, vLLM, or another
backend may produce fluent reasoning that hides contradiction, weak provenance,
or same-lineage repetition.

Current mitigation:
`CognitiveReasoningEngine` operates on bounded activated context, uses a
deterministic mock reasoner in tests, applies reasoning guardrails, and does not
mutate evidence, claims, lineage, provenance, or graph structures.

Future trigger:
Before enabling real local inference, adapter outputs must be validated against
the same structured `ReasoningOutput` schema and guardrail checks.

Must not do:
Do not let an LLM create graph edges, mutate evidence, confirm claims, or remove
contradictions from context.

## Provenance Debt

Risk:
Imported notes, documents, or summaries may lose source, author, lineage,
publication date, or chain-of-custody metadata.

Current mitigation:
Evidence, relationship edges, claim contributions, source trust records,
ingestion provenance records, and lineage records carry explicit provenance
fields.

Future trigger:
Before expanding ingestion beyond small deterministic fixtures, importers must
reject, quarantine, or explicitly flag records that cannot preserve provenance
metadata.

Must not do:
Do not silently ingest source material without a source id.

## Ingestion Debt

Risk:
Raw input normalization may accidentally turn sensory intake into claim
confirmation, especially if future parsers extract confident-looking statements
from ambiguous text.

Current mitigation:
`IngestionNormalizer` creates evidence, observations, provenance, lineage,
contamination flags, and warnings. It does not create claims, support edges, or
graph relationships.

Future trigger:
Before adding richer document parsing, OCR, media extraction, or batch import,
fixtures must include malformed, derivative, anonymous, speculative, and
missing-provenance cases.

Must not do:
Do not confirm, support, or rank claims during ingestion.

## Similarity Debt

Risk:
Future vector search may retrieve semantically similar claims from the same
lineage and make repetition look like independent corroboration.

Current mitigation:
The claim matrix does not use semantic similarity for confirmation.
Independence scoring keeps same-source and same-lineage evidence from inflating
confidence.

Future trigger:
Before adding vector search, retrieval results must expose source ids,
lineage ids, duplicate risk, and copy-chain context.

Must not do:
Do not increase claim confidence solely because multiple records are
semantically similar.

## Temporal Debt

Risk:
Fuzzy dates, partial dates, and unknown chronology may be over-normalized into
precise event order.

Current mitigation:
Timeline events store exact dates, possible ranges, precision, and date notes.
Unknown dates remain unknown and are not fabricated for ordering.

Future trigger:
Before adding natural-language date parsing, parsed dates must preserve
precision and parser uncertainty.

Must not do:
Do not convert "sometime in July" or "late 1947" into a false exact date.

## Scoring Debt

Risk:
Bounded confidence scores may be read as truth probabilities even though they
are heuristic investigation aids.

Current mitigation:
Scores are clamped between `0.0` and `1.0`, and claim statuses preserve
contested and unresolved states.

Future trigger:
Before exposing scores in reports or UI, labels must explain that scores
represent structured support, contradiction, trust, and independence signals,
not factual certainty.

Must not do:
Do not display claim confidence as a probability that the claim is true.

## Evaluation Debt

Risk:
New retrieval, ingestion, or AI features may pass unit tests while weakening
epistemic safeguards.

Current mitigation:
Tests currently cover memory merging, source trust, lineage, contamination,
corroboration, timeline ordering, claim matrix behavior, graph relationships,
duplicate edge prevention, contradiction retrieval, associative retrieval, and
evidence ingestion.

Future trigger:
Before new capabilities are added, tests must include negative cases that prove
unsupported, repeated, derivative, or ingested evidence does not become
confirmation.

Must not do:
Do not add AI, ingestion, vector search, or ranking features without tests for
false confidence failure modes.

## UX And Reporting Debt

Risk:
Reports or future interfaces may visually emphasize a single answer and hide
uncertainty, contradiction, or provenance.

Current mitigation:
No web UI exists yet. `DiscourseEngine` produces deterministic structured
sections with citations, contradictions, weak associations, speculative labels,
missing information, and review-required status.

Future trigger:
Before building a web interface or generated reports, every rendered claim view
must preserve the same discourse sections, citations, reasoning warnings,
contradictions, and uncertainty notes.

Must not do:
Do not present a contested or weakly supported claim as a resolved finding.

## Discourse Debt

Risk:
Readable narrative may accidentally smooth over uncertainty, omit provenance, or
inflate possible associations into conclusions.

Current mitigation:
`NarrativeBuilder` uses deterministic templates and separates observations,
interpretations, speculation, and uncertainty. `DiscourseGuardrails` preserves
provenance visibility, contradiction visibility, speculative labeling, and
certainty-language warnings.

Future trigger:
Before adding LLM-written narratives or a web discourse interface, generated
text must pass deterministic discourse guardrails and preserve citations.

Must not do:
Do not let polished narrative override structured evidence, citations,
contradictions, or review-required warnings.

## Persistence Debt

Risk:
Saved snapshots may be treated as authoritative truth state, or future schema
changes may silently discard fields needed to preserve provenance and
uncertainty.

Current mitigation:
`PersistenceStore` saves local JSON snapshots with manifests, schema versions,
record counts, and deterministic checksums. `Serializer` preserves unknown
fields, and `PersistenceGuardrails` keeps loaded discourse, archived memories,
contradiction pressure, and provenance boundaries visible.

Future trigger:
Before adding a database, sync service, or migration tooling, snapshots must
remain importable as immutable archival records with explicit schema migration
steps.

Must not do:
Do not load a snapshot in a way that creates new evidence, confirms claims,
creates graph edges, or promotes discourse into truth.

## Evaluation Debt

Risk:
Synthetic evaluation scores may be mistaken for scientific validity,
real-world accuracy, or validation of UAP conclusions.

Current mitigation:
`EvaluationHarness` measures framework behavior only. `EvaluationReportFormatter`
includes limitations in every report, and `EpistemicMetrics` exposes bounded
guardrail rates rather than truth metrics.

Future trigger:
Before adding real data, vector retrieval, or real model inference, new
synthetic scenarios should be added for the failure modes those features
introduce.

Must not do:
Do not interpret passing synthetic scenarios as real-world truth validation.

## Dependency Boundary Debt

Risk:
Infrastructure libraries may smuggle assumptions into graph traversal,
temporal parsing, or future persistence/database behavior.

Current mitigation:
`networkx` and `python-dateutil` are used only behind deterministic wrappers.
Graph traversal is sorted, duplicate edges are deduplicated, and temporal
parsing preserves fuzzy-date uncertainty instead of fabricating precision.

Future trigger:
Before adding a graph database, vector database, or additional parsing library,
the dependency must sit behind an interface with tests for provenance,
contradiction visibility, deterministic ordering, and uncertainty preservation.

Must not do:
Do not let infrastructure dependencies decide truth, erase uncertainty, or
replace provenance-aware framework models.

## Semantic Layer Debt

Risk:
Future embeddings or vector databases may make semantically similar records
look confirmed, equivalent, or independently corroborated.

Current mitigation:
`SemanticSimilarityEngine` uses deterministic mock embeddings by default.
Semantic records carry provenance, lineage, role, contradiction pressure, and
contamination flags. `SemanticContaminationGuard` warns on same-lineage echoes,
missing provenance, contested matches, paraphrase risk, and fictional
contamination.

Future trigger:
Before adding real embedding models or a vector database, every backend must
pass the same semantic guardrail tests and preserve component scores in hybrid
retrieval.

Must not do:
Do not treat semantic similarity, paraphrase, or cluster membership as claim
confirmation or independent corroboration.

## VLM Perception Debt

Risk:
Future vision-language perception may describe images or video frames in ways
that appear observationally certain while depending on model interpretation.

Current mitigation:
No VLM perception layer exists. Existing ingestion and reasoning layers require
provenance, contamination warnings, uncertainty notes, and no claim
confirmation.

Future trigger:
Before adding VLM perception, outputs must be modeled as observations with
source provenance, frame or timestamp references, uncertainty notes, and review
state.

Must not do:
Do not treat VLM descriptions as primary evidence without provenance and
uncertainty labeling.
