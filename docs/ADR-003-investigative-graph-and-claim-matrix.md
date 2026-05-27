# ADR-003: Investigative Graph and Claim Matrix

## Status

Accepted.

## Context

Investigations in uncertain evidence domains are relational. Evidence mentions
entities, supports or contradicts claims, references sources, derives from prior
records, and anchors events in time with varying precision.

Linear notes and semantic similarity alone cannot represent this structure. Two
items that sound similar may share a copy chain, repeat the same weak source, or
describe separate events. Similarity is useful for discovery, but it is not
confirmation.

## Decision

Phase 3 adds a deterministic relational layer:

- `RelationshipGraphEngine` stores nodes and provenance-carrying edges.
- `TimelineEngine` stores events with exact, approximate, partial, or unknown
  dates.
- `ClaimMatrixEngine` separates claims from evidence and tracks support,
  contradiction, source trust, and bounded confidence.
- `IndependenceScorer` estimates whether evidence items are meaningfully
  independent based on source, lineage, publication date, and author metadata.

The layer remains in-memory, deterministic, and testable. It does not ingest
real UAP data, call LLMs, use vector databases, or decide truth.

## Rationale

### Investigation Is Graph-Shaped

Evidence does not exist in isolation. A source can reference another source, a
claim can mention an entity, and two claims can contradict each other. A graph
lets the system preserve those relationships without collapsing them into a
single narrative.

### Timelines Are First-Class Objects

Chronology is often central to investigative reasoning. The timeline stores
exact dates when available, approximate ranges when known, and unknown dates as
unknown. It never fabricates missing dates to force ordering.

### Claims Are Separate From Evidence

Evidence is an artifact or observation. A claim is an assertion derived from one
or more pieces of evidence. Separating them prevents the system from treating
the existence of evidence as proof that a claim is true.

### Semantic Similarity Is Not Confirmation

Repeatedly seeing similar wording may indicate copying, summarization, or
contamination rather than corroboration. The graph and claim matrix keep source
lineage visible so repetition is not mistaken for independent support.

### Source Independence Matters

Confidence should increase more when separate primary sources support a claim
than when the same lineage repeats it. Unknown lineage remains cautious because
missing provenance should not create artificial certainty.

## Consequences

The system can now ask structured questions such as:

- What claims does this source support or contradict?
- Which events are known to occur before another event?
- Which contradictions are unresolved around this claim?
- Is support independent, or repeated from the same lineage?

The cost is additional bookkeeping. Each edge and claim contribution must carry
provenance metadata so the engines can remain deterministic and auditable.
