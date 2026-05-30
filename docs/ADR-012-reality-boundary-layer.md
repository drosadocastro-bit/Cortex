# ADR-012: Reality Boundary Layer

## Status

Accepted.

## Context

Future live inference systems may generate fluent reasoning, discourse,
semantic clusters, retrieval summaries, and speculative hypotheses. Those
outputs can be useful for investigation, but they are not external reality and
must not be promoted into evidence by repetition, polish, or recursive reuse.

## Decision

Phase 11 adds a deterministic reality-boundary layer:

- `CognitiveArtifact` and `ArtifactType` label generated and imported objects by
  epistemic role.
- `InferenceProvenanceTracker` records origin chains for generated artifacts.
- `CognitiveArtifactRegistry` preserves artifact type separation and queryable
  lineage.
- `RecursiveInferenceGuard` detects self-citation, reasoning-about-reasoning,
  discourse-as-evidence, semantic recursion, and bounded-depth violations.
- `RealityBoundaryEngine` and `LiveInferenceSafetyGuard` block unsafe
  promotions and graph-support creation.

## Why Cognition Must Remain Separated From Reality

Reasoning, discourse, retrieval, semantic similarity, and synthetic evaluation
are internal cognitive operations. They can help organize attention, but they do
not add new external observations. The boundary layer makes this distinction
explicit before real LLM or VLM inference is introduced.

## Why Discourse Is Not Evidence

Discourse is a human-review presentation layer. It can cite evidence and expose
uncertainty, but its narrative form must not become a new evidence source. A
summary of evidence is not another independent observation.

## Why Recursive Inference Is Dangerous

Generated outputs can accidentally cite earlier generated outputs, creating
feedback loops that appear more confident over time. Recursive reasoning can
make internal repetition look like corroboration. The recursive guard emits
warnings when self-reference, reasoning-about-reasoning, or semantic recursion
appears.

## Why Self-Citation Contamination Matters

If a discourse output or semantic cluster is later reused as evidence, the
system can contaminate its own source pool. The boundary layer tracks artifact
chains so investigators can see when an output depends on prior cognition rather
than external input.

## Why Provenance Chains Remain Mandatory

Every artifact needs an origin path. Missing provenance blocks unsafe promotion,
and inference provenance remains queryable so later review can distinguish
external input from reasoning, discourse, retrieval, semantic clustering, and
synthetic evaluation.

## Consequences

- Semantic clusters cannot create support edges.
- Reasoning outputs cannot mutate claims directly.
- Discourse outputs cannot become evidence automatically.
- Synthetic evaluations remain synthetic and do not validate real-world claims.
- Speculative hypotheses remain speculative.
- Future live inference integrations must pass the same boundary checks.
