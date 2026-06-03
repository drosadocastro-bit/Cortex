# ADR-029: Adversarial Calibration Expansion

## Status

Accepted.

## Context

The first adversarial calibration baseline was useful as a smoke test, but its
small size made the detector look cleaner than it really was. A result such as
`0.714` accuracy was encouraging, but it did not expose enough false positives,
false negatives, multilingual gaps, negation weaknesses, or soft certainty
inflation.

Cortex is an epistemic research framework, not a detector of truth or a
validated safety system. Its adversarial testing should therefore prefer honest
error visibility over reassuring scores.

## Decision

Expand the calibration set from seven cases to sixteen cases and record:

- true positives
- true negatives
- false positives
- false negatives
- accuracy
- precision
- recall
- false positive rate
- false negative rate
- multilingual case count
- known limitation count

Add typed calibration categories for:

- review-state laundering
- benign provenance boundaries
- overbroad authority language
- subtle certainty inflation
- multilingual certainty pressure
- negated confirmation language
- transferability pressure
- presentation aggregation traps
- benign safety boundaries
- technical inspiration boundaries

The detector itself remains lightweight and phrase based. Phase 26.3 measures
its current limits; it does not optimize the detector toward a better-looking
score.

## Rationale

Accuracy alone can hide important behavior. A detector that overflags benign
certification disclaimers or misses soft proof language needs that weakness
documented explicitly. Precision and recall help expose whether the detector is
too eager, too weak, or both.

The expanded baseline intentionally includes known failures:

- benign certification language that is overflagged
- negated Spanish confirmation that is overflagged
- soft English proof language that is missed
- subtle Spanish certainty language that is missed

These failures are not embarrassing noise. They are part of the framework's
credibility because they show what Cortex does not yet handle.

## Consequences

The expanded baseline has a lower accuracy than the initial smoke baseline:

- accuracy: `0.562`
- precision: `0.625`
- recall: `0.556`

This is acceptable and desirable at this stage. The goal is not to claim robust
detection. The goal is to keep failure modes inspectable before future live
inference, UI, multilingual ingestion, vector retrieval, or transferability
work.

## Boundaries

This calibration is not:

- real-world validation
- safety evidence
- certification evidence
- multilingual robustness proof
- predictive-maintenance transferability evidence
- proof that Cortex can detect manipulation in real investigations

It is a deterministic synthetic behavior baseline for a small detector inside a
research sandbox.
