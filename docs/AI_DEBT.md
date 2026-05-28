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
No UI exists yet. Documentation states that the system should ask better
questions rather than decide truth.

Future trigger:
Before building UI or generated reports, every claim view must show provenance,
supporting evidence, contradicting evidence, status, and unresolved notes.

Must not do:
Do not present a contested or weakly supported claim as a resolved finding.
