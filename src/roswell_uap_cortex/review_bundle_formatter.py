"""Markdown formatting for review bundles."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.models import ReviewBundle, ReviewBundleExportResult
from roswell_uap_cortex.review_bundle_guardrails import ReviewBundleGuardrails


@dataclass(slots=True)
class ReviewBundleFormatter:
    """Render review bundles as bounded Markdown."""

    guardrails: ReviewBundleGuardrails = field(default_factory=ReviewBundleGuardrails)

    def format(self, bundle: ReviewBundle) -> ReviewBundleExportResult:
        warnings = [*bundle.warnings, *self.guardrails.check(bundle)]
        lines = [
            "# Cortex Review Bundle",
            "",
            f"- Bundle: {bundle.manifest.bundle_id}",
            f"- Schema: {bundle.manifest.schema_version}",
            "",
        ]
        for section in bundle.sections:
            lines.append(f"## {section.title}")
            for item in section.items:
                lines.append(f"- {item}")
            lines.append("")
        if warnings:
            lines.append("## Bundle Warnings")
            for warning in warnings:
                lines.append(f"- {warning.warning_type}: {warning.message}")
            lines.append("")
        content = "\n".join(lines).strip()
        return ReviewBundleExportResult(
            bundle=bundle,
            content=content,
            warnings=warnings,
            success=not any(warning.warning_type == "certainty_language" for warning in warnings),
        )
