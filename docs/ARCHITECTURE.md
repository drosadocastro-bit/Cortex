# Architecture

Roswell UAP Cortex is an experimental cognitive framework for preserving
uncertainty in noisy evidence domains. It is not an operational analysis tool,
truth engine, or autonomous investigator.

## Canonical Flow

The main experimental path is:

```text
raw input
-> ingestion / normalization
-> evidence / provenance / lineage
-> candidate claim extraction
-> claim normalization / unsupported topic registration
-> claim evidence evaluation / support and contradiction review
-> claim review dockets / human review queue
-> source reliability review
-> working memory / review session state
-> session persistence / audit trail
-> review bundle export
-> memory / graph / claims
-> associative retrieval / attention
-> activated context
-> bounded reasoning
-> discourse / review output
-> persistence / evaluation / adversarial testing
```

Every major subsystem should either fit this path or be documented as an
auxiliary or experimental extension.

## Consolidation Cadence

Every five major phases, Cortex should pause feature expansion for an
architecture consolidation, debugging, and security hygiene pass. These pauses
are part of the design discipline, not cleanup afterthoughts.

See `docs/GOVERNANCE.md` for the recurring consolidation rule and checklist.

## Layers

Core domain models:
`models.py` contains the dataclasses and enums used by the rest of the project.
These are intentionally simple, serializable, and deterministic.

Ingestion, provenance, and lineage:
Raw inputs are normalized into evidence, observations, provenance records,
lineage records, and contamination flags. Ingestion does not confirm claims or
create graph support. Observation classification separates direct observation,
interpretation, speculation, reported claims, metadata statements, and unknown
spans before records move downstream.

Candidate claim extraction:
Classified observations can seed `CandidateClaim` records for review. Candidate
claims are not support, confirmation, or graph relationships. They start
unsupported and preserve their observation origin and provenance.

Claim normalization:
Candidate claims can be grouped under deterministic canonical keys and
registered in the claim matrix as unsupported topics. Normalization organizes
candidate claims, but it does not validate them or create support.

Claim support and contradiction evaluation:
Normalized claims can be compared with evidence records to produce possible
support, possible contradiction, uncertainty, irrelevant, or needs-review
signals. These are review signals only. They do not decide truth, mutate
evidence, create support graph edges, or erase contradiction pressure.

Claim review workflow:
Claim review dockets organize normalized claims, evidence assessment summaries,
citations, lineage, warnings, uncertainty, and cautious recommendations for
human inspection. Review priority is an attention signal, not truth
confidence.

Source reliability review:
Source review dockets organize evidence by source id and expose provenance
quality, lineage risk, contamination flags, source-trust inputs, and bounded
recommendations. Source review is not source truth, source rejection, or claim
confirmation.

Working memory and review sessions:
Working memory holds active claim dockets, source dockets, activated context,
reasoning output, discourse output, reviewed items, deferred items,
unresolved items, contradictions, and uncertainty notes. Review decisions are
workflow annotations, not truth decisions.

Session persistence and audit:
Session persistence saves review sessions, decisions, deferred items,
unresolved items, and audit trails as deterministic local JSON. Loading session
state does not apply decisions to evidence, claims, sources, or graph records.

Review bundle export:
Review bundles compose sessions, dockets, audit trails, unresolved items,
uncertainty, provenance, contradictions, and limitations into structured
Markdown-ready review packets. A bundle is not a final report or conclusion.

Cognitive state:
Memory, graph, claim matrix, source trust, contradiction pressure, and temporal
ordering preserve investigative structure without deciding truth.

Retrieval, activation, and attention:
Associative retrieval, semantic comparison, hybrid retrieval, and salience
gating prioritize review context. Association and salience are not
confirmation.

Bounded reasoning and discourse:
Reasoning operates only on supplied activated context. Discourse presents
structured review sections with citations, warnings, contradictions, and
uncertainty visible.

Persistence and evaluation:
Snapshots preserve state as immutable local JSON records. Evaluation and
adversarial harnesses test framework behavior, not real-world validity.

Reality boundary:
Generated cognition, discourse, retrieval, semantic clusters, speculative
hypotheses, synthetic evaluations, and external input remain separate artifact
types.

## Extension Layers

The following are intentionally experimental or auxiliary:

- controlled semantic layer and mock embeddings
- hard adversarial scenarios
- attention policy presets
- future local LLM adapters
- future VLM perception
- future vector database integration

These layers should preserve the same epistemic rules as the core path.

## Design Constraints

- Evidence first, not answer first.
- Provenance must remain visible.
- Contradictions are valuable state.
- Unknown or fuzzy dates must not become false exact dates.
- Repetition is not independent corroboration.
- Support is not confirmation.
- Contradiction is not disproof.
- Review priority is not truth confidence.
- Source review is not source truth.
- Review session decisions are not claim confirmation or source rejection.
- Audit trails are workflow history, not evidence.
- Review bundles are not final reports.
- Semantic similarity is not confirmation.
- Discourse is not evidence.
- Salience is review priority, not belief.
