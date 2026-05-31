"""Deterministic source review formatting."""

from __future__ import annotations

from dataclasses import dataclass, field

from roswell_uap_cortex.citations import CitationFormatter
from roswell_uap_cortex.models import SourceReviewDocket, SourceReviewItem


@dataclass(slots=True)
class SourceReviewFormatter:
    """Format source review dockets without source-truth language."""

    citation_formatter: CitationFormatter = field(default_factory=CitationFormatter)

    def format(self, docket: SourceReviewDocket) -> str:
        lines = [f"# {docket.title}", ""]
        for item in sorted(docket.items, key=lambda entry: entry.source_id):
            lines.extend(self._item(item))
            lines.append("")
        if docket.citations:
            lines.append("## Citations")
            for citation in self.citation_formatter.merge(list(docket.citations)):
                lines.append(f"- {self.citation_formatter.format(citation)}")
            lines.append("")
        lines.append("## Boundary")
        lines.append("- Source review is not source truth, source rejection, or claim confirmation.")
        return "\n".join(lines).strip()

    def _item(self, item: SourceReviewItem) -> list[str]:
        lines = [
            f"## Source: {item.source_id}",
            f"- Priority: {item.priority.value} ({item.priority_score:.2f})",
            f"- Reliability signal: {item.reliability_score:.2f}",
            f"- Risk signal: {item.risk_score:.2f}",
            f"- Evidence: {', '.join(sorted(item.evidence_ids)) if item.evidence_ids else 'none'}",
        ]
        if item.contamination_flags:
            lines.append("- Contamination flags: " + ", ".join(sorted(flag.value for flag in item.contamination_flags)))
        if item.risk_signals:
            lines.append("- Risk signals: " + ", ".join(signal.signal_type for signal in item.risk_signals))
        if item.reliability_signals:
            lines.append("- Reliability signals: " + ", ".join(signal.signal_type for signal in item.reliability_signals))
        if item.recommendations:
            lines.append("- Recommendations: " + " | ".join(rec.message for rec in item.recommendations))
        return lines
