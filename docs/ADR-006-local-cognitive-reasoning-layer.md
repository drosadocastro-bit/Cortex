# ADR-006: Local Cognitive Reasoning Layer

## Status

Accepted.

## Context

The framework now has ingestion, provenance, lineage, contamination flags,
associative retrieval, activated context, graph relationships, timelines, and
claim matrices. A local reasoning layer can help organize that context, but it
must not become an oracle.

Future local inference may use Nemotron Nano 30B through LM Studio, Ollama,
vLLM, or another backend. Phase 6 prepares the interface while keeping tests
deterministic through a mock reasoner.

## Decision

Add a bounded local cognitive reasoning layer:

- `ContextWindowBuilder` compacts activated context to reduce duplicate lineage
  flooding and lost-in-the-middle risk.
- `LocalLLMAdapter` defines an abstract adapter interface for future inference
  backends.
- `MockReasoner` provides deterministic structured outputs for tests.
- `ReasoningGuardrails` enforces association-not-confirmation, contradiction
  visibility, unsupported-claim preservation, speculative labeling, provenance
  warnings, same-lineage caution, and fictional-contamination warnings.
- `CognitiveReasoningEngine` coordinates context building, adapter reasoning,
  and guardrail validation.

The reasoning layer does not mutate evidence, graph edges, claims, provenance,
or lineage.

## Rationale

### The LLM Is Not Truth

The LLM is a bounded reasoning component operating on supplied context. It can
surface observations, warnings, uncertainty notes, and speculative hypotheses,
but it cannot confirm claims or create evidence.

### Activated Context Is Bounded

Reasoning over every related record risks burying provenance, contradiction, and
low-quality source warnings. A compact context window prioritizes strong
associations, source diversity, contradiction visibility, and lineage diversity.

### Contradiction Visibility Is Mandatory

Contested context must remain visible. The system should not hide contradictions
to produce cleaner prose or a more resolved answer.

### Context Collapse Must Be Mitigated

Duplicate lineage and repeated wording can dominate a context window. The
builder trims low-value duplicate context so the reasoning layer sees a focused
set of records instead of a pile of copies.

### Reasoning Is Separate From Ingestion

Ingestion records sensory evidence and provenance. Reasoning interprets only the
activated context supplied to it. Keeping these layers separate prevents raw
input normalization from becoming claim confirmation.

### Provenance Remains First-Class

Reasoning output includes a provenance summary and warnings when provenance is
missing. Missing provenance lowers the context-support band and requires review.

## Consequences

Phase 6 creates a safe adapter point for future local models, including
Nemotron through LM Studio, while keeping the current project deterministic and
testable. Future VLM perception can use the same boundary: perception may create
structured observations, but it must not bypass provenance, lineage, or
reasoning guardrails.
