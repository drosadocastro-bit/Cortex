# ADR-028: Synthetic Scenario Expansion Before Transferability Claims

## Status

Accepted.

## Context

Cortex is mature enough to ask whether its epistemic review architecture might
transfer to adjacent domains such as predictive maintenance advising. That
question is valuable, especially when inspired by aerospace AI safety and
assurance thinking.

However, transferability should not be asserted too early. A small, careful
research framework should first deepen its own synthetic behavior coverage.

## Decision

Expand the deterministic synthetic scenario dataset before implementing any
predictive-maintenance transferability layer.

The expansion adds scenario coverage for:

- review influence as attention/context/discourse hints, not truth
- deferred review items staying visible
- source risk remaining warning state, not rejection
- presentation view models remaining display state, not reasoning
- presentation grouping having no aggregation semantics
- missing presentation data remaining visibly missing
- demo presentation remaining synthetic-only

## Consequences

Cortex gets stronger evidence about its own framework behavior without
generalizing to a new operational domain.

The phrase "scenario coverage" remains bounded: scenario coverage is not
certification, real-world validation, operational safety evidence, or proof
that Cortex can advise maintenance action.

Put plainly: scenario coverage is not certification.

## Non-Goals

- No predictive maintenance module is added.
- No aircraft, maintenance, or real operational data is ingested.
- No fault prediction, diagnostic, dispatch, airworthiness, or replacement
  recommendation behavior is added.
- No certification or deployment-readiness claim is made.

## Future Trigger

Revisit transferability only after a larger body of synthetic scenario results,
adversarial findings, demo runs, and boundary evaluations exists.
