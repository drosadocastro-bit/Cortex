"""Recursive inference guards for self-citation and inference loops."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.inference_provenance import InferenceProvenanceTracker
from roswell_uap_cortex.models import (
    ArtifactType,
    CognitiveArtifact,
    RecursiveInferenceWarning,
)


@dataclass(slots=True)
class RecursiveInferenceGuard:
    """Detect bounded recursion risks in cognitive artifact chains."""

    max_depth: int = 3

    def inspect(
        self,
        artifact: CognitiveArtifact,
        tracker: InferenceProvenanceTracker,
    ) -> list[RecursiveInferenceWarning]:
        warnings: list[RecursiveInferenceWarning] = []

        if artifact.artifact_id in artifact.source_artifact_ids:
            warnings.append(
                RecursiveInferenceWarning(
                    "self_citation_loop",
                    "Artifact directly cites itself as an origin.",
                    {artifact.artifact_id},
                )
            )

        chain = tracker.chain_for(artifact.artifact_id)
        chain_ids = {record.artifact_id for record in chain}
        if len(chain_ids) != len(chain):
            warnings.append(
                RecursiveInferenceWarning(
                    "recursive_chain_loop",
                    "Artifact provenance chain contains repeated inference references.",
                    chain_ids,
                )
            )

        parent_types = {
            tracker.records[parent_id].artifact_type
            for parent_id in artifact.source_artifact_ids
            if parent_id in tracker.records
        }
        if artifact.artifact_type is ArtifactType.REASONING_OUTPUT and ArtifactType.REASONING_OUTPUT in parent_types:
            warnings.append(
                RecursiveInferenceWarning(
                    "reasoning_about_reasoning",
                    "Reasoning output derives from another reasoning output.",
                    {artifact.artifact_id, *artifact.source_artifact_ids},
                )
            )
        if artifact.artifact_type is ArtifactType.EVIDENCE and ArtifactType.DISCOURSE_OUTPUT in parent_types:
            warnings.append(
                RecursiveInferenceWarning(
                    "discourse_reused_as_evidence",
                    "Discourse output is being reused as evidence.",
                    {artifact.artifact_id, *artifact.source_artifact_ids},
                )
            )
        if artifact.artifact_type is ArtifactType.SEMANTIC_CLUSTER and ArtifactType.SEMANTIC_CLUSTER in parent_types:
            warnings.append(
                RecursiveInferenceWarning(
                    "semantic_cluster_recursion",
                    "Semantic cluster derives from another semantic cluster.",
                    {artifact.artifact_id, *artifact.source_artifact_ids},
                )
            )

        record = tracker.records.get(artifact.artifact_id)
        if record and record.depth > self.max_depth:
            warnings.append(
                RecursiveInferenceWarning(
                    "recursion_depth_exceeded",
                    "Artifact provenance chain exceeds bounded recursion depth.",
                    {record.artifact_id},
                )
            )

        return sorted(warnings, key=lambda warning: warning.warning_type)
