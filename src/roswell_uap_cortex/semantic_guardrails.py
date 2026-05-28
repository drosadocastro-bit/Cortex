"""Guardrails for semantic similarity and clustering."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    ContaminationFlagType,
    SemanticRecord,
    SemanticSimilarityResult,
    SemanticWarning,
    SemanticWarningType,
)


@dataclass(slots=True)
class SemanticContaminationGuard:
    """Prevent semantic similarity from becoming confirmation."""

    def apply(
        self,
        result: SemanticSimilarityResult,
        first: SemanticRecord,
        second: SemanticRecord,
    ) -> SemanticSimilarityResult:
        self._warn(
            result,
            SemanticWarningType.SIMILARITY_NOT_CONFIRMATION,
            "Semantic similarity is not confirmation.",
            {first.record_id, second.record_id},
        )
        self._warn(
            result,
            SemanticWarningType.PARAPHRASE_NOT_INDEPENDENCE,
            "Paraphrase similarity does not imply independent evidence.",
            {first.record_id, second.record_id},
        )
        if result.lineage_overlap:
            result.similarity_score = min(result.similarity_score, 0.45)
            self._warn(
                result,
                SemanticWarningType.SAME_LINEAGE_ECHO,
                "Same-lineage semantic match was downgraded.",
                {first.record_id, second.record_id},
            )
        if not first.provenance_ids or not second.provenance_ids:
            result.similarity_score = min(result.similarity_score, 0.65)
            self._warn(
                result,
                SemanticWarningType.MISSING_PROVENANCE,
                "High semantic similarity with missing provenance requires caution.",
                {first.record_id, second.record_id},
            )
        if first.contested or second.contested:
            self._warn(
                result,
                SemanticWarningType.CONTESTED_MATCH,
                "Contested semantic match remains contested.",
                {first.record_id, second.record_id},
            )
        contamination_flags = set(first.contamination_flags) | set(second.contamination_flags)
        if ContaminationFlagType.FICTIONAL_CONTAMINATION_TERMS.value in contamination_flags:
            self._warn(
                result,
                SemanticWarningType.FICTIONAL_CONTAMINATION,
                "Fictional contamination flag propagated into semantic result.",
                {first.record_id, second.record_id},
            )
        return result

    def _warn(
        self,
        result: SemanticSimilarityResult,
        warning_type: SemanticWarningType,
        message: str,
        related_ids: set[str],
    ) -> None:
        if any(warning.warning_type is warning_type for warning in result.warning_flags):
            return
        result.warning_flags.append(
            SemanticWarning(
                warning_type=warning_type,
                message=message,
                related_ids=related_ids,
            )
        )
