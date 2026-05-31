"""Guardrails for review bundle exports."""

from __future__ import annotations

from dataclasses import dataclass
import re

from roswell_uap_cortex.models import ReviewBundle, ReviewBundleWarning


@dataclass(slots=True)
class ReviewBundleGuardrails:
    """Detect certainty inflation and missing review boundaries."""

    banned_terms: tuple[str, ...] = (
        "confirmed",
        "proven",
        "debunked",
        "validated",
        "verified true",
        "definitive",
    )

    def check(self, bundle: ReviewBundle) -> list[ReviewBundleWarning]:
        warnings: list[ReviewBundleWarning] = []
        flattened = " ".join(
            " ".join([section.title, *section.items])
            for section in bundle.sections
        ).casefold()
        for term in self.banned_terms:
            if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", flattened):
                warnings.append(
                    ReviewBundleWarning(
                        "certainty_language",
                        f"Review bundle contains certainty-inflating term: {term}",
                    )
                )

        section_ids = {section.section_id for section in bundle.sections}
        if "limitations" not in section_ids and not bundle.limitations:
            warnings.append(ReviewBundleWarning("missing_limitations", "Review bundle must include limitations."))
        if "audit_trail" not in section_ids:
            warnings.append(ReviewBundleWarning("missing_audit_trail", "Review bundle is missing audit trail section."))
        if "unresolved" in section_ids and "contradictions" not in section_ids:
            warnings.append(
                ReviewBundleWarning(
                    "missing_contradictions",
                    "Unresolved items are present without a contradiction section.",
                )
            )
        if "provenance" not in section_ids:
            warnings.append(
                ReviewBundleWarning(
                    "missing_provenance",
                    "Review bundle is missing provenance/citation references.",
                )
            )
        else:
            provenance = next(section for section in bundle.sections if section.section_id == "provenance")
            if provenance.items == ["missing"]:
                warnings.append(
                    ReviewBundleWarning(
                        "missing_provenance",
                        "Review bundle provenance/citation references are missing.",
                    )
                )
        return warnings
