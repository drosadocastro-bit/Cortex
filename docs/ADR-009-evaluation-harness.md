# ADR-009: Evaluation Harness

## Status

Accepted.

## Context

Before real data, vector retrieval, or real model inference, the framework needs
deterministic checks that its epistemic rules still hold under stress. These
checks must evaluate framework behavior, not real-world truth.

## Decision

Phase 8.1 adds a synthetic evaluation harness:

- `ScenarioFactory` creates tiny synthetic scenarios.
- `EvaluationHarness` inspects artifacts and records pass/fail behavior.
- `EpistemicMetrics` computes bounded behavior rates.
- `EvaluationReportFormatter` emits deterministic reports.
- `EvaluationGuardrails` attaches mandatory limitations to every report.

Expected behaviors include provenance visibility, contradiction preservation,
unsupported-claim suppression, association-confirmation separation, speculative
labeling, same-lineage caution, uncertainty exposure, contamination warning
visibility, bounded confidence, and no state mutation.

## Rationale

### Evaluation Before Real Data

Synthetic scenarios make it possible to stress the framework before real
investigative material is introduced.

### Synthetic Tests Are Not Real-World Validation

Passing scenarios means the framework preserved required behavior in engineered
cases. It does not validate any UAP conclusion or evidentiary claim.

### Epistemic Behavior Is Separate From Truth

Metrics measure whether the system preserves uncertainty, provenance,
contradiction, and guardrails. They are not accuracy or truth metrics.

### Mutation Safety Matters

Evaluation checks that framework state is not silently mutated while testing.
This protects evidence, graph, discourse, and persistence boundaries.

### Association Is Not Confirmation

The harness treats association-confirmation separation as a core metric because
similarity and repetition are recurring sources of false confidence.

### Limitations Are Mandatory

Every evaluation report includes limitations so pass rates are not mistaken for
scientific validity or real-world truth.

## Consequences

The project now has executable checks for its epistemic commitments. Future
features should add scenarios before expanding capability.
