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

## Observation Classification Debt

Risk:
Deterministic marker rules may misclassify subtle language, especially when
direct observation and interpretation appear in the same sentence.

Current mitigation:
`ObservationClassifier` preserves marker lists and classification notes.
Unknown or mixed spans remain explicit instead of being promoted into direct
observation.

Future trigger:
Before adding LLM-assisted extraction, richer NLP parsing, OCR, transcripts, or
media perception, fixtures must include ambiguous observation/interpretation
boundaries and reported-speech variants.

Must not do:
Do not treat an observation-type label as truth, source reliability, or claim
confirmation.

## Claim Extraction Debt

Risk:
Extracted candidate claims may be mistaken for supported claims, especially when
future LLM extraction produces fluent claim text.

Current mitigation:
`ClaimExtractionEngine` creates `CandidateClaim` records only. They start
unsupported with confidence `0.0`, preserve origin and provenance, and carry
warnings that extraction is not confirmation.

Future trigger:
Before adding LLM-assisted claim extraction, extracted claims must retain source
spans, observation type, provenance ids, uncertainty notes, and review status.

Must not do:
Do not create support edges, increase claim confidence, or mark a claim
supported merely because it was extracted from text.

## Claim Normalization Debt

Risk:
Canonical grouping may make repeated or paraphrased candidate claims look more
supported than they are.

Current mitigation:
`ClaimNormalizer` emits warnings that normalization is not validation. It
preserves candidate ids, origin types, provenance ids, evidence ids, and lineage
ids. `ClaimMatrixIntegrator` registers normalized claims as unsupported topics
without support evidence or confidence.

Future trigger:
Before adding richer paraphrase matching, LLM claim extraction, or semantic
claim clustering, normalization must keep origin and lineage visible and must
add adversarial tests for repeated same-lineage phrasing.

Must not do:
Do not treat normalized claim grouping, repeated phrasing, or canonical topic
registration as corroboration.

## Claim Evaluation Debt

Risk:
Future claim evaluators may turn possible support into confirmation, possible
contradiction into disproof, or mixed evidence into an overconfident status.

Current mitigation:
`ClaimEvidenceEvaluator` emits bounded assessment records and warnings.
`ClaimContradictionEvaluator` detects only deterministic contradiction signals,
and `ClaimEvidenceGuardrails` labels support, contradiction, speculation,
reported claims, metadata, missing provenance, and same-lineage repetition as
review constraints.

Future trigger:
Before adding semantic matching, LLM-assisted comparison, richer temporal
reasoning, or graph-backed claim evaluation, new tests must show that support
does not confirm, contradiction does not disprove, and same-lineage paraphrases
do not inflate confidence.

Must not do:
Do not promote a claim, create support graph edges, or mutate evidence merely
because an evaluator found lexical, semantic, or narrative alignment.

## Claim Review Debt

Risk:
Review queues and dockets may make high-priority items look more believable or
more important than low-priority items.

Current mitigation:
`ClaimReviewEngine` packages assessment signals for inspection without mutating
claims, evidence, or graph state. `ReviewPriorityEngine` labels priority as a
review signal, and `EvidenceDocketFormatter` states that dockets do not confirm
or reject claims.

Future trigger:
Before adding a web UI, reporting layer, or interactive review workflow,
rendered dockets must preserve support, contradiction, uncertainty, provenance,
lineage, and recommendations as separate sections.

Must not do:
Do not display claim review priority as truth confidence, evidence validity, or
an instruction to resolve a claim automatically.

## Source Review Debt

Risk:
Source reliability review may be mistaken for source acceptance, source
rejection, or claim confirmation.

Current mitigation:
`SourceReviewEngine` creates review dockets only. `SourceRiskProfiler` emits
bounded risk signals from provenance, lineage, contamination, observation type,
and source-trust inputs. `SourceReviewFormatter` states that source review is
not source truth or source rejection.

Future trigger:
Before adding a UI, larger ingestion pipeline, live inference, or source
ranking display, source review must keep reliability signals, risk signals,
citations, lineage, contamination flags, and recommendations visibly separate.

Must not do:
Do not treat a high source reliability signal as proof, or a high source risk
signal as automatic rejection of all evidence from that source.

## Review Session Debt

Risk:
Review-session decisions may be mistaken for claim resolution, source
acceptance, source rejection, or evidence mutation.

Current mitigation:
`WorkingMemoryEngine` builds active session state from existing dockets and
context without mutating records. `ReviewSessionEngine` records decisions as
workflow annotations only, and `SessionFormatter` states that session decisions
are not claim confirmation, source rejection, or evidence mutation.

Future trigger:
Before adding UI, multi-user collaboration, persistence of sessions, or live
inference handoff, session decisions must remain separate from evidence,
claims, source trust, graph edges, and discourse.

Must not do:
Do not treat a reviewed item as confirmed, a deferred item as irrelevant, or a
session delta as a truth-state change.

## Session Persistence Debt

Risk:
Persisted sessions and audit trails may be mistaken for evidence history or
truth-state history instead of review workflow history.

Current mitigation:
`SessionPersistenceStore` stores sessions and audit trails in a separate local
JSON envelope. It validates schema version, record counts, and checksum.
`SessionAuditFormatter` includes limitations, and loading a session snapshot
does not create evidence, claims, source truth, or graph edges.

Future trigger:
Before adding UI session restore, collaborative review, or database-backed
sessions, session audit events must remain visibly separate from evidence,
claim status, source trust, graph state, and discourse.

Must not do:
Do not treat an audit event, reviewed item, or persisted decision as proof that
an external event happened or that a claim/source was resolved.

## Review Bundle Debt

Risk:
Exported Markdown bundles may appear like official findings or final reports.

Current mitigation:
`ReviewBundleBuilder` keeps sessions, claim dockets, source dockets, audit
trails, uncertainty, contradictions, provenance, and limitations in separate
sections. `ReviewBundleGuardrails` warns on certainty-inflating language and
missing provenance or limitations.

Future trigger:
Before adding UI export, PDF output, generated summaries, or public sharing,
bundle renderers must preserve limitations, provenance, uncertainty, deferred
items, and unresolved contradictions.

Must not do:
Do not label a review bundle as a final report, confirmed finding, validated
claim, or source rejection.

## Demo Workspace Debt

Risk:
Synthetic demo output may be mistaken for real-world evidence, system
validation, or an example investigation result.

Current mitigation:
`DemoWorkspaceBuilder` uses synthetic-only raw inputs and
`DemoWorkspaceGuardrails` rejects non-synthetic source identifiers. Demo docs
state that the workspace is an architecture exercise only.

Future trigger:
Before using the demo in UI, screenshots, presentations, or public docs, labels
must state that all content is synthetic and not real-world validation.

Must not do:
Do not mix real UAP data into the demo workspace or describe demo output as a
finding.

## Review-To-Reasoning Boundary Debt

Risk:
Human-review workflow state can accidentally become hidden reasoning input.
Reviewed items may look confirmed, deferred items may disappear, source-risk
flags may look like rejection, and bundle/audit records may be mistaken for
evidence.

Current mitigation:
`ReviewInfluencePolicy` converts review state into bounded attention, context,
and discourse hints. `ReviewContextAdapter` carries those hints as uncertainty
and visibility notes. Tests assert that reviewed claims do not gain confidence,
deferred items remain visible, source risk is not rejection, session decisions
do not create graph edges, and bundles do not alter claim matrix state.

Future trigger:
Before adding UI workflows, live LLM reasoning, or analyst-facing editing,
review influence must remain explicit and auditable.

Must not do:
Do not treat review decisions, audit records, review bundles, or display
priority as evidence, confirmation, source truth, or graph support.

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
missing information, and review-required status. The review/session/export/demo
arc now provides dockets, working memory, audit trails, review bundles, and a
synthetic demo fixture that future UI should render without inventing truth
semantics.

Future trigger:
Before building a web interface or generated reports, every rendered claim view
must preserve the same discourse sections, citations, reasoning warnings,
contradictions, uncertainty notes, review decisions, audit limitations, and
synthetic-demo labels.

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

## Reality Boundary Debt

Risk:
Future live inference may recursively reuse reasoning, discourse, retrieval
results, semantic clusters, or synthetic evaluations until generated cognition
appears to be external evidence.

Current mitigation:
`RealityBoundaryEngine`, `CognitiveArtifactRegistry`,
`InferenceProvenanceTracker`, `RecursiveInferenceGuard`, and
`LiveInferenceSafetyGuard` preserve artifact type separation, track inference
provenance chains, detect self-citation, and block unsafe promotion.

Future trigger:
Before adding real local LLM inference, VLM perception, vector databases, or
agentic loops, generated artifacts must be registered and checked against the
reality boundary.

Must not do:
Do not let discourse, reasoning, semantic clusters, retrieval results,
synthetic evaluations, or speculative hypotheses become evidence or claim
confirmation automatically.

## Attention Debt

Risk:
Salience scoring may be mistaken for belief, evidence validity, or truth
confidence, especially when contaminated or contradictory records are ranked
highly for review.

Current mitigation:
`AttentionEngine`, `AttentionGate`, `SaliencePolicyEngine`, and
`AttentionGuardrails` label salience as review priority, keep selected-for-review
separate from selected-for-context, preserve provenance and contradiction
warnings, and downgrade repeated same-lineage records.

Future trigger:
Before attention scores are shown in reports, UI, agent loops, or live
inference prompts, display labels must explain that salience is not truth
confidence.

Must not do:
Do not interpret attention priority as evidence validity, claim confirmation,
or permission to suppress contradictions, provenance gaps, contamination flags,
or speculative labels.

## Adversarial Testing Debt

Risk:
Synthetic adversarial scenarios may be mistaken for proof that the framework is
robust against real-world manipulation, noisy data, or deliberate deception.

Current mitigation:
`AdversarialHarness` and `AdversarialScenarioFactory` record attacks and
findings as framework-behavior stress tests only. `docs/ADVERSARIAL_FINDINGS.md`
includes limitations with every report.

Future trigger:
Before adding live inference, real data ingestion, vector databases, web UI
ranking, or autonomous workflows, add adversarial scenarios for the new failure
modes those features introduce.

Must not do:
Do not treat resisted synthetic attacks as real-world validation or as evidence
that any external claim is true or false.

## Hard Adversarial Calibration Debt

Risk:
A perfect hard-adversarial score may create false assurance that the system is
robust against prompt injection, data poisoning, semantic echo, output
reingestion, misinformation, or duplicate flooding.

Current mitigation:
The OWASP-inspired hard suite intentionally includes `near_miss`,
`failed_expected`, and `inconclusive` outcomes. `docs/HARD_ADVERSARIAL_FINDINGS.md`
documents those outcomes separately from the smoke adversarial report.
`docs/HARD_ADVERSARIAL_REMEDIATION.md` maps each non-perfect outcome to a
specific remediation target and acceptance criteria.

Future trigger:
When live LLM inference, VLM perception, larger ingestion, vector databases, or
tool-use capabilities are added, hard adversarial scenarios must be expanded and
expected failures converted into explicit design tasks.

Must not do:
Do not optimize the hard adversarial suite toward a perfect score. A credible
hard suite should preserve known weaknesses and near misses until they are
actually fixed.

Open remediation items:
- `hard-llm01-prompt-injection-note`: deterministic instruction-contamination
  detection for prompt-like source content.
- `hard-llm02-sensitive-metadata-disclosure`: metadata visibility boundaries for
  public, internal, and private fields.
- `hard-llm09-polished-misinformation`: speculation-hardening checks that do not
  depend only on literal trigger words.
- `hard-llm10-duplicate-flood`: bounded workload, truncation notes, and
  duplicate-flood reporting.

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
