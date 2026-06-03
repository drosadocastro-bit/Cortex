# ADR-030: Evidence Quality Rubric

## Status

Accepted.

## Context

Cortex already preserves provenance, lineage, contamination warnings,
observation type, contradiction pressure, and temporal uncertainty. Those
signals are useful, but they are distributed across several records. Before
adding broader reasoning, UI, real data, or transferability work, the framework
needs a deterministic way to describe evidence condition without turning that
condition into truth.

## Decision

Add an evidence-quality rubric with separated dimensions:

- provenance completeness
- lineage clarity
- source transparency
- observation directness
- contamination resistance
- contradiction stability
- temporal specificity
- extraction confidence

The rubric produces an `EvidenceQualityAssessment` with a bounded
`quality_score`, a bounded `review_priority_score`, warnings, reason codes, and
one label:

- `insufficient`
- `fragile`
- `reviewable`
- `strong_context`
- `contested`

These labels describe review condition only. They are not truth confidence,
claim confidence, source acceptance, corroboration, or graph support.

## Rationale

Evidence can be well documented and still contradicted. It can be direct but
missing provenance. It can have clear lineage but contain contamination flags.
A single aggregate score must therefore not hide important dimensions.

The rubric keeps dimensions separate and emits warnings for missing provenance,
derivative or unknown lineage, contamination risk, contradiction pressure,
temporal uncertainty, low observation directness, and the recurring rule that
quality is not truth.

## Consequences

Evidence quality can help order review attention. Fragile, contaminated,
contradicted, derivative, or missing-provenance records can be surfaced earlier.

Evidence quality cannot:

- confirm a claim
- reject evidence
- create graph edges
- increase claim matrix confidence
- turn review priority into belief
- erase contradiction or uncertainty

The adversarial suite now includes quality-score laundering, where a strong
quality label is tested against attempts to turn evidence condition into claim
confirmation.

## Boundaries

This rubric is deterministic and synthetic-testable. It is not a scientific
validity score, safety score, source truth score, or operational reliability
metric. It exists to make evidence condition more inspectable before downstream
review, reasoning, discourse, or future UI.
