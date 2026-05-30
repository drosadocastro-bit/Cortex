# ADR-015: OWASP-Inspired Hard Adversarial Suite

## Status

Accepted.

## Context

The first adversarial suite was useful as a smoke test: it proved that known
guardrails fire on obvious synthetic attacks. A perfect resistance rate is not
credible as a hard adversarial benchmark, because detector-aligned fixtures can
overestimate robustness.

## Decision

Add an OWASP-inspired hard adversarial suite with non-perfect outcomes by
design. The suite maps selected OWASP LLM Top 10 risk categories into Cortex's
deterministic epistemic domain:

- prompt injection
- sensitive information disclosure
- data/model poisoning
- improper output handling
- excessive agency
- vector and embedding weaknesses
- misinformation
- unbounded consumption

The hard suite reports:

- `resisted`
- `near_miss`
- `failed_expected`
- `failed_unexpected`
- `inconclusive`

## Why Non-Perfect Results Matter

A hard adversarial suite should reveal uncertainty about the framework itself.
Near misses and expected failures keep the report honest and prevent a perfect
score from becoming a false assurance signal.

## Current Calibration

The initial hard suite intentionally includes:

- obvious attacks that are resisted
- brittle near misses
- one expected failure around polished speculation
- one inconclusive sensitive-metadata fixture

This makes the hard suite a calibration tool, not a marketing score.

## Consequences

- Future high-risk phases should add hard adversarial scenarios before claiming
  guardrail completeness.
- Expected failures should be tracked as AI debt or design debt.
- Hard reports must include limitations.
- A future accidental perfect hard score should be reviewed skeptically.
