"""Guardrails for deterministic investigative discourse."""

from __future__ import annotations

from dataclasses import dataclass

from roswell_uap_cortex.models import (
    DiscourseResponse,
    DiscourseWarning,
    DiscourseWarningType,
    ReasoningWarningType,
)


@dataclass(slots=True)
class DiscourseGuardrails:
    """Ensure discourse exposes uncertainty and avoids certainty inflation."""

    forbidden_certainty_terms: tuple[str, ...] = (
        "proves",
        "proven",
        "confirms",
        "confirmed",
        "definitely",
        "established fact",
    )

    def apply(self, response: DiscourseResponse) -> DiscourseResponse:
        self._add_warning(
            response,
            DiscourseWarningType.PROVENANCE_VISIBLE,
            "Provenance citations remain visible in discourse.",
        )
        self._add_warning(
            response,
            DiscourseWarningType.NO_FABRICATED_EVIDENCE,
            "Discourse is limited to supplied reasoning and activated context.",
        )

        if response.contradictions.items:
            response.review_required = True
            self._add_warning(
                response,
                DiscourseWarningType.CONTRADICTION_VISIBLE,
                "Contradiction visibility cannot be suppressed.",
            )

        if response.speculative_hypotheses.items:
            response.review_required = True
            self._add_warning(
                response,
                DiscourseWarningType.SPECULATION_LABELED,
                "Speculative content remains labeled.",
            )

        if response.missing_information.items:
            response.review_required = True
            self._add_warning(
                response,
                DiscourseWarningType.MISSING_PROVENANCE,
                "Missing information remains visible.",
            )

        if any(
            warning.warning_type is ReasoningWarningType.UNSUPPORTED_CLAIM
            for warning in response.reasoning_warnings
        ):
            response.review_required = True
            self._add_warning(
                response,
                DiscourseWarningType.UNSUPPORTED_REMAINS_UNSUPPORTED,
                "Unsupported claims remain unsupported.",
            )

        if any(
            warning.warning_type is ReasoningWarningType.FICTIONAL_CONTAMINATION
            for warning in response.reasoning_warnings
        ):
            response.review_required = True
            self._add_warning(
                response,
                DiscourseWarningType.CONTAMINATION_WARNING,
                "Contamination warnings remain visible.",
            )

        narrative_text = " ".join(
            [
                response.narrative.observations,
                response.narrative.interpretations,
                response.narrative.speculation,
                response.narrative.uncertainty,
            ]
        ).casefold()
        if not any(term in narrative_text for term in self.forbidden_certainty_terms):
            self._add_warning(
                response,
                DiscourseWarningType.CERTAINTY_LANGUAGE_AVOIDED,
                "Narrative avoids certainty-inflating language.",
            )
        return response

    def _add_warning(
        self,
        response: DiscourseResponse,
        warning_type: DiscourseWarningType,
        message: str,
    ) -> None:
        if any(warning.warning_type is warning_type for warning in response.observed_evidence.warnings):
            return
        warning = DiscourseWarning(warning_type=warning_type, message=message)
        response.observed_evidence.warnings.append(warning)
