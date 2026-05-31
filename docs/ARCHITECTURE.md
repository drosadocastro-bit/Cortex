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
- Semantic similarity is not confirmation.
- Discourse is not evidence.
- Salience is review priority, not belief.
