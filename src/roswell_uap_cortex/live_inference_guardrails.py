"""Safety rules for future live inference integrations."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ArtifactType,
    CognitiveArtifact,
    RealityBoundaryViolation,
)


@dataclass(slots=True)
class LiveInferenceSafetyGuard:
    """Deterministic guardrails that keep generated cognition separated."""

    max_recursion_depth: int = 3

    def validate_promotion(
        self,
        artifact: CognitiveArtifact,
        target_type: ArtifactType | str,
        *,
        explicit: bool = False,
    ) -> RealityBoundaryViolation | None:
        if isinstance(target_type, str):
            target_type = ArtifactType(target_type)

        if target_type is ArtifactType.EVIDENCE:
            if artifact.artifact_type is ArtifactType.DISCOURSE_OUTPUT:
                return self._violation(
                    "discourse_not_evidence",
                    "Discourse output cannot become evidence automatically.",
                    artifact,
                )
            if artifact.artifact_type is ArtifactType.REASONING_OUTPUT:
                return self._violation(
                    "reasoning_not_evidence",
                    "Reasoning output remains reasoning, not evidence.",
                    artifact,
                )
            if artifact.artifact_type is ArtifactType.SYNTHETIC_EVALUATION:
                return self._violation(
                    "synthetic_not_real_evidence",
                    "Synthetic evaluations cannot become real-world evidence.",
                    artifact,
                )
            if artifact.artifact_type is ArtifactType.SPECULATIVE_HYPOTHESIS:
                return self._violation(
                    "speculation_remains_speculation",
                    "Speculative hypotheses remain speculative.",
                    artifact,
                )
            if not explicit:
                return self._violation(
                    "automatic_promotion_blocked",
                    "Evidence promotion requires explicit review.",
                    artifact,
                )
            if not artifact.provenance_ids:
                return self._violation(
                    "missing_provenance_blocks_promotion",
                    "Missing provenance blocks unsafe promotion.",
                    artifact,
                )

        if target_type is ArtifactType.CLAIM and artifact.artifact_type is ArtifactType.REASONING_OUTPUT:
            return self._violation(
                "reasoning_not_claim_mutation",
                "Reasoning outputs cannot mutate claims directly.",
                artifact,
            )

        return None

    def validate_graph_support(self, artifact: CognitiveArtifact) -> RealityBoundaryViolation | None:
        if artifact.artifact_type is ArtifactType.SEMANTIC_CLUSTER:
            return self._violation(
                "semantic_cluster_not_graph_support",
                "Semantic clusters cannot create graph support edges.",
                artifact,
            )
        if artifact.artifact_type is ArtifactType.RETRIEVAL_RESULT:
            return self._violation(
                "retrieval_not_fact",
                "Retrieval outputs are not facts or support edges.",
                artifact,
            )
        return None

    def validate_depth(self, depth: int, artifact_id: str) -> RealityBoundaryViolation | None:
        if depth > self.max_recursion_depth:
            return RealityBoundaryViolation(
                "recursion_depth_exceeded",
                "Recursive inference depth exceeded the configured bound.",
                {artifact_id},
            )
        return None

    def _violation(
        self,
        violation_type: str,
        message: str,
        artifact: CognitiveArtifact,
    ) -> RealityBoundaryViolation:
        return RealityBoundaryViolation(violation_type, message, {artifact.artifact_id})
