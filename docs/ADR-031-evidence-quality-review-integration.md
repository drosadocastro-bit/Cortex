# ADR-031: Evidence Quality Review Integration

## Status

Accepted.

## Context

Phase 27 introduced a deterministic evidence-quality rubric. The next risk is
integration drift: once quality labels appear in claim or source review dockets,
they could be misread as claim support, source acceptance, or reliability.

The review workflow needs access to evidence condition, but only as review
visibility and priority pressure.

## Decision

Add compact `EvidenceQualitySummary` records to claim and source review items.
These summaries expose:

- quality label
- quality score
- review priority score
- weak dimensions
- quality warning types
- reason codes

`ClaimReviewEngine` and `SourceReviewEngine` may accept precomputed
`EvidenceQualityAssessment` records and include summaries in their dockets.
`ReviewPriorityEngine` may use fragile, insufficient, contested, missing
provenance, or contamination quality signals to increase review priority.

## Boundary

Evidence quality integration must not:

- change claim confidence
- change claim status
- accept or reject a source
- create graph edges
- alter source trust records
- collapse contradiction pressure
- treat `strong_context` as confirmation
- treat `fragile` or `contested` as rejection

Quality is an attention and visibility signal only.

## Consequences

Review dockets now show evidence-condition context next to support,
contradiction, and uncertainty summaries. This gives reviewers a better view of
why an evidence item may need attention without turning that attention into a
truth claim.

The evidence docket formatter prints a boundary note stating that evidence
quality is review context, not claim confirmation.

## Future Work

A future UI may render these summaries as badges or panels, but it must consume
the bounded view of quality rather than recalculating quality into confidence,
source acceptance, or claim support.
