# ADR-014: Adversarial Epistemic Testing

## Status

Accepted.

## Context

The framework now has provenance, lineage, contradiction preservation,
associative retrieval, semantic discipline, reasoning guardrails, discourse,
persistence, evaluation, reality boundaries, and attention gating. The next
risk is assuming those layers are strong merely because normal scenarios pass.

Adversarial testing intentionally tries to make the framework confuse internal
cognition, repetition, semantic similarity, discourse, synthetic fixtures, or
attention priority with evidence or truth.

## Decision

Add a deterministic adversarial stress-testing layer:

- `AdversarialScenario` describes a synthetic attack vector and expected failure
  mode.
- `AdversarialHarness` runs scenarios through existing deterministic guardrails.
- `AdversarialFinding` records whether the framework resisted the attempted
  failure.
- `AdversarialReportFormatter` produces a compact findings report.
- `AdversarialScenarioFactory` provides tiny synthetic attacks only.

## Attack Families

The initial adversarial suite covers:

- provenance laundering
- semantic echo chamber
- discourse contamination
- confidence inflation
- contradiction suppression
- speculation hardening
- synthetic-to-real confusion
- missing provenance camouflage
- temporal overreach
- policy abuse

## Why This Is Separate From Evaluation

Evaluation checks expected epistemic behavior. Adversarial testing tries to
break that behavior. A passing adversarial suite means only that the current
synthetic attacks were resisted; it does not validate real-world claims or prove
the framework cannot fail.

## Findings Discipline

Adversarial findings are framework-behavior findings. They are not truth
findings. A resisted attack means a guardrail fired in a small deterministic
fixture. A failed attack means a framework weakness was exposed and should be
documented as AI debt.

## Consequences

- Future phases can add adversarial scenarios before enabling higher-risk
  capabilities.
- Findings can be documented without claiming scientific validity.
- Guardrail regressions become easier to detect.
- The system keeps a stronger posture: it is tested against attempts to fool
  itself, not just happy-path behavior.
