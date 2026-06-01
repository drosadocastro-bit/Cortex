"""Synthetic demo presentation adapter for future UI fixtures."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.demo_workspace import DemoWorkspaceBuilder
from roswell_uap_cortex.models import DemoPresentation, DemoWorkspaceResult
from roswell_uap_cortex.presentation import PresentationBuilder
from roswell_uap_cortex.review_influence import ReviewInfluencePolicy


@dataclass(slots=True)
class DemoPresentationBuilder:
    """Build a deterministic presentation fixture from the synthetic demo."""

    demo_builder: DemoWorkspaceBuilder = field(default_factory=DemoWorkspaceBuilder)
    presentation_builder: PresentationBuilder = field(default_factory=PresentationBuilder)
    influence_policy: ReviewInfluencePolicy = field(default_factory=ReviewInfluencePolicy)

    def build(self, result: DemoWorkspaceResult | None = None) -> DemoPresentation:
        result = result or self.demo_builder.build()
        claim_dockets = [result.claim_review_docket] if result.claim_review_docket else []
        source_dockets = [result.source_review_docket] if result.source_review_docket else []
        influence = self.influence_policy.evaluate(
            result.review_session,
            claim_dockets=claim_dockets,
            source_dockets=source_dockets,
        ) if result.review_session else None
        dashboard = self.presentation_builder.build_dashboard(
            title=result.workspace.manifest.title,
            synthetic_only=result.workspace.manifest.synthetic_only,
            claim_dockets=claim_dockets,
            source_dockets=source_dockets,
            session=result.review_session,
            audit_trail=result.audit_trail,
            bundle=result.review_bundle,
            review_influence=influence,
            notes=result.notes,
        )
        return DemoPresentation(
            demo_id=result.workspace.manifest.demo_id,
            dashboard=dashboard,
            formatted_bundle_preview=result.formatted_bundle,
            boundary_notes=[
                "demo presentation is synthetic display state only",
                "presentation does not confirm claims or reject sources",
                "future UI should render these view models without adding reasoning",
            ],
        )
