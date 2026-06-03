"""Deterministic formatting for claim review dockets."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.citations import CitationFormatter
from roswell_uap_cortex.models import ClaimReviewDocket, ClaimReviewItem, EvidenceAssessmentSummary


@dataclass(slots=True)
class EvidenceDocketFormatter:
    """Format review dockets without certainty-inflating language."""

    citation_formatter: CitationFormatter = field(default_factory=CitationFormatter)

    def format(self, docket: ClaimReviewDocket) -> str:
        lines = [f"# {docket.title}", ""]
        for item in sorted(docket.items, key=lambda entry: entry.canonical_topic):
            lines.extend(self._format_item(item))
            lines.append("")
        if docket.citations:
            lines.append("## Citations")
            for citation in self.citation_formatter.merge(list(docket.citations)):
                lines.append(f"- {self.citation_formatter.format(citation)}")
            lines.append("")
        lines.append("## Boundary")
        lines.append("- This docket is for review only; it does not confirm or reject claims.")
        return "\n".join(lines).strip()

    def _format_item(self, item: ClaimReviewItem) -> list[str]:
        lines = [
            f"## Claim: {item.canonical_topic}",
            f"- Text: {item.canonical_text}",
            f"- Priority: {item.priority.value} ({item.priority_score:.2f})",
            f"- Unsupported remains unsupported: {str(item.unsupported).lower()}",
        ]
        lines.extend(self._section("Possible support", item.support_summaries, "support_score"))
        lines.extend(self._section("Possible contradiction", item.contradiction_summaries, "contradiction_score"))
        lines.extend(self._section("Uncertainty", item.uncertainty_summaries, "uncertainty_score"))
        lines.extend(self._quality_section(item))
        if item.warning_types:
            lines.append("- Warnings: " + ", ".join(sorted(warning.value for warning in item.warning_types)))
        if item.recommendations:
            lines.append("- Recommendations: " + " | ".join(rec.message for rec in item.recommendations))
        return lines

    def _quality_section(self, item: ClaimReviewItem) -> list[str]:
        if not item.quality_summaries:
            return ["- Evidence quality: none"]
        lines = ["- Evidence quality:"]
        for summary in sorted(item.quality_summaries, key=lambda entry: entry.evidence_id):
            weak = ",".join(summary.weak_dimensions) if summary.weak_dimensions else "none"
            warnings = ",".join(sorted(warning.value for warning in summary.warning_types)) if summary.warning_types else "none"
            lines.append(
                "  - "
                f"evidence:{summary.evidence_id} "
                f"label:{summary.quality_label.value} "
                f"quality_score:{summary.quality_score:.2f} "
                f"review_priority:{summary.review_priority_score:.2f} "
                f"weak_dimensions:{weak} "
                f"warnings:{warnings}"
            )
        lines.append("  - boundary:evidence quality is review context, not claim confirmation")
        return lines

    def _section(
        self,
        label: str,
        summaries: list[EvidenceAssessmentSummary],
        score_field: str,
    ) -> list[str]:
        if not summaries:
            return [f"- {label}: none"]
        lines = [f"- {label}:"]
        for summary in sorted(summaries, key=lambda item: item.evidence_id):
            score = getattr(summary, score_field)
            lines.append(f"  - evidence:{summary.evidence_id} score:{score:.2f} type:{summary.assessment_type.value}")
        return lines
