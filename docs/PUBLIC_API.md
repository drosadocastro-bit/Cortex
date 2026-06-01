# Public API Discipline

The current `roswell_uap_cortex.__init__` exports are broad for convenience
during early research phases. This is a transitional public surface, not a
promise that every helper is foundational.

## Foundational Exports

Stable framework primitives include:

- domain records such as `EvidenceItem`, `ClaimNode`, `MemoryRecord`,
  `ProvenanceRecord`, `SourceLineageRecord`, `RelationshipEdge`, and
  `Contradiction`
- core enums such as `RelationshipType`, `ClaimMatrixStatus`,
  `TimelineDatePrecision`, and `ArtifactType`
- engines on the canonical path such as `IngestionNormalizer`,
  `ClaimExtractionEngine`, `ClaimNormalizer`, `ClaimEvidenceEvaluator`,
  `ClaimReviewEngine`, `SourceReviewEngine`, `RelationshipGraphEngine`,
  `WorkingMemoryEngine`, `ReviewSessionEngine`, `SessionPersistenceStore`,
  `ReviewBundleBuilder`, `DemoWorkspaceBuilder`, `TimelineEngine`, `ClaimMatrixEngine`,
  `AssociativeRetrievalEngine`, `AttentionEngine`, `CognitiveReasoningEngine`,
  `DiscourseEngine`, `SnapshotBuilder`, `PersistenceStore`, and
  `EvaluationHarness`

## Extension Exports

These are useful but should be treated as extension points:

- semantic and hybrid retrieval components
- NetworkX graph backend
- local LLM adapter abstraction
- mock embedding and mock reasoning components
- attention policies
- reality-boundary registry helpers
- docket formatters and priority helpers used to present review state

## Experimental / Testing Exports

These are intentionally available for tests and research workflows, but should
not be treated as the main identity of the package:

- synthetic scenario factories
- adversarial and hard adversarial harnesses
- report formatters
- guardrail helper classes

## Future Cleanup Direction

Before a production-style package boundary is considered, split the public API
into explicit namespaces such as:

- `roswell_uap_cortex.core`
- `roswell_uap_cortex.experimental`
- `roswell_uap_cortex.testing`
- `roswell_uap_cortex.docs` or documentation-only artifacts

Do not export every new class by default. Prefer internal modules unless a class
is needed by tests, examples, documented external use, or the canonical flow.

The review/session/export/demo arc increased the number of public symbols.
Future UI view models should avoid further broadening the root API unless a
symbol is truly part of the documented canonical path.

Use `docs/WORKFLOW_MAP.md` as the ownership reference before exporting new
review workflow objects. New objects should have a clear home in cognitive core,
review workflow, session/audit, export/demo, or evaluation.

## Compatibility Note

For now, broad exports remain in place so existing tests and examples continue
to work. API reduction should be a deliberate compatibility step, not a casual
cleanup.
