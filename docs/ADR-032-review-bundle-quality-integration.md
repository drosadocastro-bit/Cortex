# ADR-032: Review Bundle Quality Integration

## Status

Accepted.

## Context

Evidence-quality summaries now appear in claim and source review dockets. Review
bundles are the exportable review packet, so they must preserve that quality
context without making the bundle look like a final finding.

The risk is familiar: a compact export can make bounded review signals appear
more authoritative than they are.

## Decision

Add an `Evidence Quality` section to every review bundle.

When claim or source dockets contain `EvidenceQualitySummary` records, the
bundle preserves:

- evidence id
- quality label
- quality score
- review priority score
- weak dimensions
- quality warning types

The section also includes a boundary note:

`evidence quality is review context, not claim confirmation or source truth`

If a non-empty quality section is missing this boundary, review-bundle
guardrails emit a `missing_quality_boundary` warning.

## Boundary

Review bundle quality integration must not:

- create final reports
- confirm claims
- reject evidence
- accept or reject sources
- create graph edges
- alter claim confidence
- hide uncertainty or contradiction
- treat `strong_context` as confirmation
- treat `fragile` or `contested` as rejection

Quality remains record-condition context for review.

## Consequences

Bundles now carry evidence-condition context forward from claim and source
review. This makes exported review packets more complete while preserving the
same epistemic boundaries as the underlying dockets.

Empty quality sections remain explicit as `none`. This avoids silently implying
quality was evaluated when no quality summaries are present.

## Future Work

Future bundle or UI presentation may render quality summaries more elegantly,
but should consume this bounded section rather than deriving new truth,
confidence, or source-acceptance semantics from quality labels.
