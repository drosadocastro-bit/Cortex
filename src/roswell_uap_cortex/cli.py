"""Tiny deterministic CLI harness for investigative discourse."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from roswell_uap_cortex.discourse import DiscourseEngine
from roswell_uap_cortex.evaluation import EvaluationHarness
from roswell_uap_cortex.evaluation_report import EvaluationReportFormatter
from roswell_uap_cortex.models import (
    ActivatedContext,
    DiscourseRequest,
    EvidenceItem,
    ProvenanceRecord,
    ReasoningRequest,
    SourceLineageRecord,
)
from roswell_uap_cortex.reasoning import CognitiveReasoningEngine
from roswell_uap_cortex.scenarios import ScenarioFactory


def build_demo_discourse(prompt: str) -> str:
    evidence = EvidenceItem(
        id="cli-evidence-1",
        summary=f"Synthetic CLI note related to: {prompt}",
        source_id="synthetic://cli",
        evidence_type="note",
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        metadata={"lineage_id": "cli-lineage-1", "contamination_flags": []},
    )
    provenance = ProvenanceRecord(
        evidence_id=evidence.id,
        source_uri=evidence.source_id,
        source_kind="synthetic_cli_note",
        ingestion_method="deterministic_cli_fixture",
        extraction_method="manual_fixture",
        original_input_id="cli-input-1",
    )
    lineage = SourceLineageRecord(
        evidence_id=evidence.id,
        source_id=evidence.source_id,
        lineage_id="cli-lineage-1",
        source_uri=evidence.source_id,
    )
    activated = ActivatedContext(activated_evidence_ids={evidence.id})
    reasoning = CognitiveReasoningEngine().reason(
        ReasoningRequest(query=prompt, activated_context=activated),
        evidence_by_id={evidence.id: evidence},
        provenance_by_evidence_id={evidence.id: provenance},
        lineage_by_evidence_id={evidence.id: lineage},
    )
    discourse = DiscourseEngine().build(
        DiscourseRequest(
            query=prompt,
            activated_context=activated,
            reasoning_output=reasoning,
        ),
        evidence_by_id={evidence.id: evidence},
        provenance_by_evidence_id={evidence.id: provenance},
        lineage_by_evidence_id={evidence.id: lineage},
    )
    return render_response(discourse)


def render_response(response) -> str:
    sections = [
        response.observed_evidence,
        response.possible_associations,
        response.contradictions,
        response.weak_associations,
        response.speculative_hypotheses,
        response.provenance_notes,
        response.uncertainty_summary,
        response.missing_information,
    ]
    lines: list[str] = []
    for section in sections:
        lines.append(f"## {section.title}")
        if section.items:
            lines.extend(f"- {item}" for item in section.items)
        else:
            lines.append("- none")
    lines.append("## Citations")
    if response.citations:
        lines.extend(f"- {citation.label}" for citation in response.citations)
    else:
        lines.append("- none")
    lines.append("## Review")
    lines.append(f"- required: {str(response.review_required).lower()}")
    return "\n".join(lines)


def build_demo_evaluation_report() -> str:
    scenarios = ScenarioFactory().all()
    report = EvaluationHarness().run(scenarios)
    return EvaluationReportFormatter().format(report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic investigative discourse.")
    parser.add_argument("prompt", help="Investigative prompt")
    args = parser.parse_args(argv)
    print(build_demo_discourse(args.prompt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
