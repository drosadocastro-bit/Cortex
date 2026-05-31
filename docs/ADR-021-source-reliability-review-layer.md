# ADR-021: Source Reliability Review Layer

Status: Accepted

## Context

Cortex now has a disciplined claim-review path. The source side needs the same
visibility before future UI, live inference, larger ingestion, or semantic
retrieval work expands the system.

Source reliability review must not decide whether a source is true, false,
accepted, or rejected. It should expose review signals: provenance gaps,
lineage risk, contamination flags, trust inputs, repetition, and source usage.

## Decision

Add `SourceReviewEngine`, `SourceRiskProfiler`, and `SourceReviewFormatter`.

The review layer groups evidence by `source_id` and creates
`SourceReviewDocket` records. Each `SourceReviewItem` preserves:

- source id
- evidence ids
- provenance ids
- lineage ids
- contamination flags
- reliability signals
- risk signals
- bounded recommendations
- review priority

## Why Source Review Is Not Source Truth

A source can have strong provenance and still be wrong. A source can have risk
signals and still contain useful evidence. For this reason, reliability and
risk scores are review aids only. They do not confirm claims, reject sources,
or create graph relationships.

## Why Provenance And Lineage Matter

Source review is meaningful only when provenance and lineage remain visible.
Derivative sources, repeated source URIs, same-lineage repetition, missing
provenance, speculative content, reported claims, and contamination flags all
shape how cautiously a source should be reviewed.

## Why This Is Separate From Claim Review

Claim review asks what evidence appears to support, contradict, or complicate a
claim. Source review asks what should be known about the sources behind that
evidence. Keeping those workflows separate prevents source risk from becoming a
claim truth decision.

## Consequences

Positive:

- Source risks become explicit before future real data ingestion.
- Trust inputs remain reviewable without becoming source truth.
- Dockets can be rendered by future UI without inventing new semantics.
- Claim and source review can reference the same evidence while preserving
  separate boundaries.

Tradeoffs:

- Risk scoring is intentionally simple and conservative.
- The layer depends on available provenance, lineage, and contamination
  metadata.
- Future source taxonomies may need richer signals, but must preserve the same
  boundary.

## Non-Goals

- No source acceptance or rejection.
- No truth decisions.
- No graph edge creation.
- No LLM/API calls.
- No vector database use.
- No autonomous source vetting.
