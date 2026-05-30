"""Inference provenance chains for generated cognitive artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.models import (
    ArtifactType,
    CognitiveArtifact,
    InferenceBoundaryRecord,
)


@dataclass(slots=True)
class InferenceProvenanceTracker:
    """Track artifact origins without treating inference as external truth."""

    records: dict[str, InferenceBoundaryRecord] = field(default_factory=dict)

    def record_artifact(self, artifact: CognitiveArtifact) -> InferenceBoundaryRecord:
        parent_depths = [
            self.records[parent_id].depth
            for parent_id in artifact.source_artifact_ids
            if parent_id in self.records
        ]
        record = InferenceBoundaryRecord(
            artifact_id=artifact.artifact_id,
            artifact_type=artifact.artifact_type,
            source_artifact_ids=set(artifact.source_artifact_ids),
            source_evidence_ids=set(artifact.source_evidence_ids),
            provenance_ids=set(artifact.provenance_ids),
            reasoning_layer_origin=self._origin_for(artifact, ArtifactType.REASONING_OUTPUT),
            discourse_layer_origin=self._origin_for(artifact, ArtifactType.DISCOURSE_OUTPUT),
            semantic_layer_origin=self._origin_for(artifact, ArtifactType.SEMANTIC_CLUSTER),
            synthetic_scenario_origin=self._origin_for(artifact, ArtifactType.SYNTHETIC_EVALUATION),
            depth=(max(parent_depths) + 1) if parent_depths else 0,
            notes=[f"artifact_type={artifact.artifact_type.value}", f"layer_origin={artifact.layer_origin}"],
        )
        self.records[artifact.artifact_id] = record
        return record

    def chain_for(self, artifact_id: str) -> list[InferenceBoundaryRecord]:
        """Return deterministic provenance chain from artifact to its ancestors."""
        ordered: list[InferenceBoundaryRecord] = []
        seen: set[str] = set()

        def visit(current_id: str) -> None:
            if current_id in seen or current_id not in self.records:
                return
            seen.add(current_id)
            record = self.records[current_id]
            ordered.append(record)
            for parent_id in sorted(record.source_artifact_ids):
                visit(parent_id)

        visit(artifact_id)
        return ordered

    def _origin_for(self, artifact: CognitiveArtifact, artifact_type: ArtifactType) -> str | None:
        if artifact.artifact_type is artifact_type:
            return artifact.layer_origin
        for parent_id in sorted(artifact.source_artifact_ids):
            parent = self.records.get(parent_id)
            if parent and parent.artifact_type is artifact_type:
                return parent.artifact_id
        return None
