# API And Model Map

This map is a light-pruning artifact. It does not change package structure or
public exports. It explains how the current broad `roswell_uap_cortex.__init__`
surface should be read while Cortex is still in research mode.

The current public API is broad for tests, examples, and rapid phase work. It
should not be interpreted as a final namespace design.

## Public Surface Posture

| Area | Examples | Posture |
| --- | --- | --- |
| Cognitive core | `EvidenceItem`, `EvidenceQualityAssessment`, `ClaimNode`, `MemoryRecord`, `RelationshipEdge`, `TimelineEngine`, `ClaimMatrixEngine` | Foundational |
| Ingestion and provenance | `RawInput`, `IngestionNormalizer`, `ProvenanceRecord`, `SourceLineageRecord`, `ContaminationFlag` | Foundational |
| Claim pipeline | `CandidateClaim`, `ClaimNormalizer`, `ClaimEvidenceEvaluator`, `ClaimReviewEngine` | Canonical review path |
| Review workflow | `SourceReviewEngine`, `WorkingMemoryEngine`, `ReviewSessionEngine`, `ReviewInfluencePolicy` | Canonical review path |
| Session and export | `SessionPersistenceStore`, `SessionAuditLogger`, `ReviewBundleBuilder` | Workflow persistence and export |
| Presentation contract | `PresentationBuilder`, `DemoPresentationBuilder`, view models | Display contract, not UI |
| Reasoning and discourse | `CognitiveReasoningEngine`, `ContextWindowBuilder`, `DiscourseEngine` | Bounded review-oriented cognition |
| Evaluation and adversarial | `EvaluationHarness`, `AdversarialHarness`, `HardAdversarialHarness` | Testing and calibration |
| Experimental extensions | semantic layer, NetworkX backend, mock embeddings, local LLM adapter | Extension points |

## Model Ownership

`models.py` currently holds many dataclasses and enums so the project can stay
simple and deterministic during rapid research phases. This is acceptable for
now, but the ownership boundaries should remain visible:

- Evidence/provenance models describe supplied or normalized records.
- Evidence-quality models describe record condition for review only.
- Claim models organize assertions without confirming them.
- Graph and timeline models preserve relationships and chronology.
- Retrieval, attention, semantic, and reasoning models describe context
  selection and review support.
- Review workflow models describe human review state only.
- Session, audit, bundle, and presentation models describe workflow display and
  persistence artifacts only.
- Evaluation and adversarial models describe synthetic behavior checks only.

No model group should silently promote its records into another group.

## Current Non-Refactor Decision

Do not split `models.py`, reorganize package folders, or reduce root exports
yet. The codebase is still evolving, and compatibility matters for tests and
examples.

Allowed light pruning:

- improve maps and ownership docs
- group future documentation by layer
- add small tests that keep maps linked
- clarify comments or names when a boundary is misleading
- avoid exporting brand-new helpers unless they are part of the canonical path

Deferred larger refactors:

- splitting `models.py` by layer
- creating `core`, `review`, `presentation`, `testing`, or `experimental`
  namespaces
- reducing `__init__.py` exports
- moving modules into subpackages
- changing dataclass shapes only for organization

## Future Namespace Sketch

If the project stabilizes enough to justify package movement, a possible split
could be:

```text
roswell_uap_cortex.core
roswell_uap_cortex.ingestion
roswell_uap_cortex.claims
roswell_uap_cortex.review
roswell_uap_cortex.reasoning
roswell_uap_cortex.presentation
roswell_uap_cortex.persistence
roswell_uap_cortex.evaluation
roswell_uap_cortex.experimental
```

This is a sketch, not a migration plan.

## Refactor Triggers

Consider deeper refactoring only when at least one of these is true:

- multiple modules duplicate the same ownership boundary
- tests require repeated imports from unrelated layers
- presentation, review, or reasoning logic begins to overlap
- `models.py` changes become hard to audit safely
- a future UI needs stable import namespaces

Until then, prefer clearer maps over file movement.
