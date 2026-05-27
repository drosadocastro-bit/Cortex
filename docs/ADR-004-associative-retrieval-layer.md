# ADR-004: Associative Retrieval Layer

## Status

Accepted.

## Context

Investigators need help surfacing related memories, claims, entities, and
evidence without the system deciding that related means confirmed. Future vector
search may improve discovery, but semantic similarity is not corroboration.

Phase 4 adds deterministic associative retrieval using lightweight lexical and
metadata signals before introducing any vector database or embedding model.

## Decision

Add an associative retrieval layer based on standard-library logic:

- `SimpleTokenizer` lowercases text, strips punctuation, removes basic
  stopwords, and returns deterministic token sets.
- `AssociativeRetrievalEngine` ranks possible associations using lexical
  overlap, shared tags, shared entities, canonical topics, timeline proximity,
  source independence, and contradiction pressure.
- `CorrelationGuard` downgrades risky correlations and records caution notes.
- `ActivationContextBuilder` converts ranked candidates into an
  `ActivatedContext` while preserving weak and contested associations.

All returned candidates are labeled `possible_association` unless the activation
builder marks them as weak or contested. No support edge is created by
retrieval.

## Rationale

### Vector Search Is Secondary

Vector search can help locate candidates, but it cannot determine whether two
records are independently corroborating, copied from the same lineage, or in
contradiction. Provenance, source independence, timeline placement, and explicit
conflict remain higher-priority signals.

### Association Is Not Confirmation

A retrieved item is a possible context item, not evidence that a claim is true.
The association score is an activation aid and must not be displayed or used as
a truth probability.

### Lightweight Retrieval Comes First

Standard-library lexical retrieval makes the scoring pipeline inspectable before
future embeddings add another signal. This lets tests define the guardrails
early: similar wording can retrieve context, but it cannot create support,
resolve contradiction, or inflate confidence through repetition.

### Future Embedding Readiness

The `AssociationScore` model already separates lexical, tag, entity, timeline,
source-independence, contradiction, and final association signals. A future
embedding score can be added as another input while still passing through the
same correlation guard.

### Focused Context And Lost-In-The-Middle

`ActivatedContext` gathers the most relevant memory, claim, evidence, and entity
ids into a focused context window. This prepares the system for future report,
review, or AI-assisted workflows where too much undifferentiated context would
bury important contradictions or provenance.

## Consequences

The system can now retrieve likely related records deterministically, preserve
weak and contested associations, and expose caution notes. The cost is that
association ranking remains intentionally simple until a future vector layer is
added under the same safeguards.
