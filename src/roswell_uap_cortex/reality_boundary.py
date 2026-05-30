"""Reality boundary engine for separating evidence from generated cognition."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.artifact_registry import CognitiveArtifactRegistry
from roswell_uap_cortex.models import (
    ArtifactType,
    CognitiveArtifact,
    CognitiveSeparationState,
    RealityBoundaryViolation,
)


@dataclass(slots=True)
class RealityBoundaryEngine:
    """Validate cognitive separation rules for future live inference layers."""

    registry: CognitiveArtifactRegistry = field(default_factory=CognitiveArtifactRegistry)

    def register_artifact(self, artifact: CognitiveArtifact) -> CognitiveArtifact:
        return self.registry.register(artifact)

    def validate_cognitive_separation(self) -> CognitiveSeparationState:
        """Return state after checking current records for unsafe drift."""
        for artifact_id, artifact in sorted(self.registry.state.artifacts.items()):
            if artifact.artifact_type in {
                ArtifactType.DISCOURSE_OUTPUT,
                ArtifactType.REASONING_OUTPUT,
                ArtifactType.SYNTHETIC_EVALUATION,
                ArtifactType.SPECULATIVE_HYPOTHESIS,
            }:
                self.registry.validate_promotion(artifact_id, ArtifactType.EVIDENCE)
            if artifact.artifact_type in {ArtifactType.SEMANTIC_CLUSTER, ArtifactType.RETRIEVAL_RESULT}:
                self.registry.validate_graph_support(artifact_id)
        return self.registry.state

    def prevent_evidence_promotion(self, artifact_id: str) -> RealityBoundaryViolation | None:
        return self.registry.validate_promotion(artifact_id, ArtifactType.EVIDENCE)

    def prevent_claim_mutation(self, artifact_id: str) -> RealityBoundaryViolation | None:
        return self.registry.validate_promotion(artifact_id, ArtifactType.CLAIM)

    def prevent_graph_support(self, artifact_id: str) -> RealityBoundaryViolation | None:
        return self.registry.validate_graph_support(artifact_id)

    def provenance_chain(self, artifact_id: str):
        return self.registry.lineage(artifact_id)
