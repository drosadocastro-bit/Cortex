# ADR-013: Attention And Salience Gating

## Status

Accepted.

## Context

By Phase 12 the framework can preserve evidence, provenance, source lineage,
contradictions, graph context, semantic associations, reasoning outputs,
discourse, persistence snapshots, evaluation scenarios, and reality-boundary
records. Preservation alone creates a new problem: too much context can bury the
records most in need of review.

## Decision

Add a deterministic attention and salience layer:

- `AttentionFocusBuilder` converts a query and target entities, events, claim
  topics, time windows, and mode into a structured focus.
- `AttentionEngine` computes bounded salience scores from auditable component
  signals.
- `SaliencePolicyEngine` provides conservative, exploratory,
  contradiction-first, provenance-first, and contamination-watch presets.
- `AttentionGate` produces selected, deferred, archived-considered,
  selected-for-context, and selected-for-review records.
- `AttentionGuardrails` keeps salience separated from belief, confidence, and
  evidence validity.

## Why Attention Is Needed

The system preserves uncertainty by retaining contradictions, weak associations,
contamination flags, provenance gaps, and speculative hypotheses. A review
priority layer helps decide what should be looked at first without deleting or
resolving anything.

## Why Salience Is Not Truth

Salience means "review priority." It does not mean a record is valid, trusted,
confirmed, or likely true. The final salience score is bounded between `0.0` and
`1.0`, but it is not evidence confidence.

## Why Noisy Records Can Be Salient

Contaminated, speculative, or provenance-fragile records may deserve attention
because they can distort investigation. Attention escalates those records for
review while preserving warnings that they are not trusted.

## Context Overload

Attention mitigates context overload and lost-in-the-middle risk by ranking
records before downstream context building. It can influence ordering and
selection, but it does not mutate evidence, claims, provenance, graph
relationships, reasoning outputs, or discourse.

## Policy Presets

Policy presets change weighting only. They cannot disable contradiction
visibility, provenance warnings, association-not-confirmation, or reality
boundary rules.

## Consequences

- Deferred records are not deleted or declared irrelevant.
- Contested and contradictory records remain visible.
- Same-lineage repetition is downgraded so it cannot dominate attention.
- Focus matching cannot override provenance warnings.
- Archived records may be considered for reactivation without erasing
  uncertainty.
