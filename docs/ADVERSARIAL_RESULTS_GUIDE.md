# Adversarial Results Guide

This guide explains how to read Cortex adversarial artifacts without turning
synthetic test behavior into safety claims, truth claims, or certification
language.

## Document Map

`ADVERSARIAL_FINDINGS.md`
: Current smoke adversarial stress report. It records whether deterministic
guardrails resisted the standard synthetic attack scenarios.

`ADVERSARIAL_CALIBRATION_BASELINE.md`
: Detector-calibration baseline. It records true positives, true negatives,
false positives, false negatives, split metrics, and the current error
taxonomy for lightweight adversarial wording checks.

`ADR-029-adversarial-calibration-expansion.md`
: Rationale for expanding calibration after the smoke baseline. It explains why
lower, more honest metrics are preferable to a cleaner-looking score.

`HARD_ADVERSARIAL_FINDINGS.md`
: OWASP-inspired hard adversarial report. It intentionally includes resisted,
near-miss, expected-failure, unexpected-failure, and inconclusive outcomes.

`HARD_ADVERSARIAL_REMEDIATION.md`
: Follow-up list for hard-suite near misses, expected failures, and
inconclusive outcomes.

`AI_DEBT.md`
: Longer-term risk register. It tracks where future LLMs, vector retrieval,
UI, multilingual ingestion, connectors, or transferability work could weaken
epistemic boundaries.

## How To Read The Results

Adversarial resistance means a synthetic scenario observed the expected
guardrail behavior. It does not mean the framework is robust against real-world
manipulation.

Calibration accuracy, precision, recall, false-positive rate, and
false-negative rate describe detector behavior on tiny synthetic examples only.
They are not safety metrics.

Hard-adversarial outcomes are intentionally not optimized toward perfection.
Near misses, expected failures, and inconclusive cases are useful because they
preserve known weakness.

## Naming Boundaries

Smoke adversarial results:
: Standard synthetic attack scenarios in `ADVERSARIAL_FINDINGS.md`.

Calibration baseline:
: Lightweight wording-detector behavior in
`ADVERSARIAL_CALIBRATION_BASELINE.md`.

Hard adversarial results:
: OWASP-inspired stress fixtures in `HARD_ADVERSARIAL_FINDINGS.md`.

Remediation tracking:
: Concrete follow-up targets in `HARD_ADVERSARIAL_REMEDIATION.md`.

AI debt:
: Risk watchpoints and future triggers in `AI_DEBT.md`.

## Interpretation Rules

- Do not treat synthetic resistance as real-world validation.
- Do not treat detector metrics as certification, safety evidence, or
  predictive-maintenance readiness.
- Do not hide false positives, false negatives, near misses, expected failures,
  or inconclusive outcomes.
- Do not tune adversarial tests toward perfect-looking scores.
- Do not treat multilingual examples as broad language coverage.
- Do not treat hard-suite results as penetration-test certification.

## Why This Exists

Cortex is designed to preserve uncertainty and boundary separation. The
adversarial documents should therefore make framework weakness more visible,
not less. This guide keeps each document's role narrow so the adversarial layer
does not become a confusing pile of overlapping reports.
