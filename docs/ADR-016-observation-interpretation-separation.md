# ADR-016: Observation And Interpretation Separation

## Status

Accepted.

## Context

The ingestion layer is the framework's sensory intake boundary. If direct
observation, interpretation, speculation, reported claims, and metadata collapse
at intake, every downstream layer inherits a blurred record.

This is especially risky before future live inference, because fluent reasoning
can make interpreted or speculative material appear observationally grounded.

## Decision

Add deterministic observation classification:

- `ObservationType`
- `ObservationClassifier`
- extended `ExtractedObservation` classification fields
- ingestion metadata propagation for observation type and markers

Classification labels include:

- `direct_observation`
- `interpretation`
- `speculation`
- `reported_claim`
- `metadata_statement`
- `unknown`

## Why Deterministic Rules

This phase uses simple marker rules only. No LLM or model inference is used.
The classifier is intentionally cautious: ambiguous spans remain unknown, and
mixed markers receive classification notes.

## Why This Is Not Truth Assessment

Classifying a span as direct observation does not mean the observation is true.
It means the text is shaped like an observation rather than interpretation,
speculation, reported speech, or metadata. Provenance, lineage, source trust,
and contradiction handling still matter.

## Consequences

- Ingestion can preserve intake type before evidence reaches memory, graph,
  claims, retrieval, reasoning, or discourse.
- Reported speech remains a reported claim, not verified observation.
- Speculation remains speculation even when it mentions an object or event.
- Interpretation is not promoted into observation.
- Metadata statements are separated from source-backed observations.
