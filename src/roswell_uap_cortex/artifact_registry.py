"""Registry for generated cognitive artifacts and their boundary metadata."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.inference_provenance import InferenceProvenanceTracker
from roswell_uap_cortex.live_inference_guardrails import LiveInferenceSafetyGuard
from roswell_uap_cortex.models import (
    ArtifactType,
    CognitiveArtifact,
    CognitiveSeparationState,
    InferenceBoundaryRecord,
    RealityBoundaryViolation,
    RecursiveInferenceWarning,
)
from roswell_uap_cortex.recursive_guard import RecursiveInferenceGuard


@dataclass(slots=True)
class CognitiveArtifactRegistry:
    """Register artifacts while preserving type separation and provenance."""

    tracker: InferenceProvenanceTracker = field(default_factory=InferenceProvenanceTracker)
    recursive_guard: RecursiveInferenceGuard = field(default_factory=RecursiveInferenceGuard)
    safety_guard: LiveInferenceSafetyGuard = field(default_factory=LiveInferenceSafetyGuard)
    state: CognitiveSeparationState = field(default_factory=CognitiveSeparationState)

    def register(self, artifact: CognitiveArtifact) -> CognitiveArtifact:
        self.state.artifacts[artifact.artifact_id] = artifact
        record = self.tracker.record_artifact(artifact)
        self.state.boundary_records[artifact.artifact_id] = record

        depth_violation = self.safety_guard.validate_depth(record.depth, artifact.artifact_id)
        if depth_violation:
            self.state.violations.append(depth_violation)

        warnings = self.recursive_guard.inspect(artifact, self.tracker)
        self.state.warnings.extend(warnings)
        return artifact

    def validate_promotion(
        self,
        artifact_id: str,
        target_type: ArtifactType | str,
        *,
        explicit: bool = False,
    ) -> RealityBoundaryViolation | None:
        artifact = self.state.artifacts[artifact_id]
        violation = self.safety_guard.validate_promotion(artifact, target_type, explicit=explicit)
        if violation:
            self.state.violations.append(violation)
        return violation

    def validate_graph_support(self, artifact_id: str) -> RealityBoundaryViolation | None:
        violation = self.safety_guard.validate_graph_support(self.state.artifacts[artifact_id])
        if violation:
            self.state.violations.append(violation)
        return violation

    def origin(self, artifact_id: str) -> InferenceBoundaryRecord | None:
        return self.state.boundary_records.get(artifact_id)

    def lineage(self, artifact_id: str) -> list[InferenceBoundaryRecord]:
        return self.tracker.chain_for(artifact_id)

    def relationships(self, artifact_id: str) -> set[str]:
        artifact = self.state.artifacts.get(artifact_id)
        return set() if artifact is None else set(artifact.source_artifact_ids)

    def contamination_chain(self, artifact_id: str) -> list[RecursiveInferenceWarning]:
        lineage_ids = {record.artifact_id for record in self.lineage(artifact_id)}
        return [
            warning
            for warning in self.state.warnings
            if warning.artifact_ids.intersection(lineage_ids)
        ]
