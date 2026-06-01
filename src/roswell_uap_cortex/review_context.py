"""Adapt review influence hints into read-only context adjustments."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import ActivatedContext, ReviewInfluenceResult


@dataclass(slots=True)
class ReviewContextAdapter:
    """Apply review hints to activated context without changing records."""

    def adapt(
        self,
        activated_context: ActivatedContext,
        influence: ReviewInfluenceResult,
    ) -> ActivatedContext:
        """Return a copied context enriched with review visibility notes.

        The adapter cannot know whether a generic review id is evidence, claim,
        memory, or source. It therefore only carries review influence as
        uncertainty notes. Type-specific inclusion is handled by
        `ContextWindowBuilder` when it receives record maps.
        """

        notes = list(activated_context.uncertainty_notes)
        notes.extend(influence.uncertainty_notes)
        notes.extend(influence.discourse_annotations)
        notes.extend(warning.message for warning in influence.warnings)
        if influence.deferred_ids:
            notes.append("deferred review items remain unresolved; they are not erased")
        if influence.contradiction_ids:
            notes.append("review workflow requires contradiction visibility")

        return ActivatedContext(
            activated_memory_ids=set(activated_context.activated_memory_ids),
            activated_claim_ids=set(activated_context.activated_claim_ids),
            activated_evidence_ids=set(activated_context.activated_evidence_ids),
            activated_entity_ids=set(activated_context.activated_entity_ids),
            weak_associations=list(activated_context.weak_associations),
            contested_associations=list(activated_context.contested_associations),
            uncertainty_notes=sorted(set(notes)),
        )
