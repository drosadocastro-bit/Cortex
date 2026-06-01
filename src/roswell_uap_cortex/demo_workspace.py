"""Fully synthetic demo workspace for the canonical Cortex pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid5

from roswell_uap_cortex.claim_evaluation import ClaimEvidenceEvaluator
from roswell_uap_cortex.claim_extraction import ClaimExtractionEngine
from roswell_uap_cortex.claim_normalization import ClaimNormalizer
from roswell_uap_cortex.claim_review import ClaimReviewEngine
from roswell_uap_cortex.demo_workspace_guardrails import DemoWorkspaceGuardrails
from roswell_uap_cortex.ingestion import IngestionNormalizer
from roswell_uap_cortex.models import (
    DemoWorkspace,
    DemoWorkspaceManifest,
    DemoWorkspaceResult,
    RawInput,
    RawInputType,
    ReviewDecisionType,
)
from roswell_uap_cortex.review_bundle import ReviewBundleBuilder
from roswell_uap_cortex.review_bundle_formatter import ReviewBundleFormatter
from roswell_uap_cortex.review_session import ReviewSessionEngine
from roswell_uap_cortex.session_audit import SessionAuditLogger
from roswell_uap_cortex.source_review import SourceReviewEngine
from roswell_uap_cortex.working_memory import WorkingMemoryEngine


DEMO_TIME = datetime(1947, 7, 8, tzinfo=timezone.utc)


@dataclass(slots=True)
class DemoWorkspaceBuilder:
    """Run a small synthetic investigation through the canonical path."""

    ingestion: IngestionNormalizer = field(default_factory=IngestionNormalizer)
    claim_extractor: ClaimExtractionEngine = field(default_factory=ClaimExtractionEngine)
    claim_normalizer: ClaimNormalizer = field(default_factory=ClaimNormalizer)
    claim_evaluator: ClaimEvidenceEvaluator = field(default_factory=ClaimEvidenceEvaluator)
    claim_review: ClaimReviewEngine = field(default_factory=ClaimReviewEngine)
    source_review: SourceReviewEngine = field(default_factory=SourceReviewEngine)
    working_memory: WorkingMemoryEngine = field(default_factory=WorkingMemoryEngine)
    session_engine: ReviewSessionEngine = field(default_factory=ReviewSessionEngine)
    audit_logger: SessionAuditLogger = field(default_factory=SessionAuditLogger)
    bundle_builder: ReviewBundleBuilder = field(default_factory=ReviewBundleBuilder)
    bundle_formatter: ReviewBundleFormatter = field(default_factory=ReviewBundleFormatter)
    guardrails: DemoWorkspaceGuardrails = field(default_factory=DemoWorkspaceGuardrails)

    def build(self) -> DemoWorkspaceResult:
        workspace = self.synthetic_workspace()
        self.guardrails.validate_workspace(workspace)

        ingestion_results = [self.ingestion.ingest(raw) for raw in workspace.raw_inputs]
        evidence = [item for result in ingestion_results for item in result.evidence_items]
        observations = [item for result in ingestion_results for item in result.observations]
        provenance = [item for result in ingestion_results for item in result.provenance_records]
        lineage = [item for result in ingestion_results for item in result.lineage_records]
        contamination = [item for result in ingestion_results for item in result.contamination_flags]
        provenance_by_evidence = {record.evidence_id: record for record in provenance}
        lineage_by_evidence = {record.evidence_id: record for record in lineage}

        extraction = self.claim_extractor.extract(
            observations,
            evidence_by_id={item.id: item for item in evidence},
            provenance_by_evidence_id=provenance_by_evidence,
        )
        normalized = self.claim_normalizer.normalize(extraction.candidate_claims).normalized_claims
        evaluation = self.claim_evaluator.evaluate(
            normalized,
            evidence,
            provenance_by_evidence_id=provenance_by_evidence,
            lineage_by_evidence_id=lineage_by_evidence,
        )
        claim_docket = self.claim_review.build_docket(
            normalized,
            evaluation,
            provenance_by_evidence_id=provenance_by_evidence,
            lineage_by_evidence_id=lineage_by_evidence,
            title="Synthetic Claim Review Docket",
        )
        source_docket = self.source_review.build_docket(
            evidence,
            provenance_records=provenance,
            lineage_records=lineage,
            contamination_flags=contamination,
            title="Synthetic Source Review Docket",
        )
        state = self.working_memory.build_state(
            query="synthetic bright light review",
            claim_dockets=[claim_docket],
            source_dockets=[source_docket],
        )
        session = self.session_engine.start_session("Synthetic Cortex Demo Session", state)
        self.session_engine.record_decision(
            session,
            item_id=sorted(state.unresolved_item_ids)[0] if state.unresolved_item_ids else "demo:none",
            item_type="demo_review_item",
            decision_type=ReviewDecisionType.KEEP_UNRESOLVED,
            notes=["synthetic demo keeps unresolved state visible"],
        )
        audit_trail = self.audit_logger.build_trail(
            session,
            [
                self.audit_logger.start(session),
                self.audit_logger.decision(session, session.decisions[-1]),
                self.audit_logger.report(session, "synthetic demo review bundle formatted"),
            ],
        )
        bundle = self.bundle_builder.build(
            session,
            claim_dockets=[claim_docket],
            source_dockets=[source_docket],
            audit_trail=audit_trail,
        )
        formatted = self.bundle_formatter.format(bundle).content
        return DemoWorkspaceResult(
            workspace=workspace,
            ingestion_results=ingestion_results,
            candidate_claims=extraction.candidate_claims,
            normalized_claims=normalized,
            claim_evaluation=evaluation,
            claim_review_docket=claim_docket,
            source_review_docket=source_docket,
            review_session=session,
            audit_trail=audit_trail,
            review_bundle=bundle,
            formatted_bundle=formatted,
            notes=[
                "demo workspace uses synthetic inputs only",
                "demo output is review state, not real-world validation",
            ],
        )

    def synthetic_workspace(self) -> DemoWorkspace:
        raw_inputs = [
            RawInput(
                input_id="demo-primary",
                input_type=RawInputType.DOCUMENT,
                title="Synthetic Primary Note",
                raw_text="Observer saw a bright light moving west. The object remained above the tree line.",
                source_uri="synthetic://demo-primary",
                source_kind="archival_document",
                collected_at=DEMO_TIME,
                metadata={"author": "synthetic records desk", "tags": {"synthetic", "demo"}},
            ),
            RawInput(
                input_id="demo-contradiction",
                input_type=RawInputType.NOTE,
                title="Synthetic Contradiction Note",
                raw_text="Observer saw no bright light moving west.",
                source_uri="synthetic://demo-contradiction",
                source_kind="note",
                collected_at=DEMO_TIME,
                metadata={"tags": {"synthetic", "contradiction"}},
            ),
            RawInput(
                input_id="demo-derivative",
                input_type=RawInputType.NOTE,
                title="Synthetic Derivative Repost",
                raw_text="Witness reported that the observer saw a bright light moving west.",
                source_uri="synthetic://demo-derivative",
                source_kind="repost",
                collected_at=DEMO_TIME,
                metadata={"parent_source_id": "synthetic://demo-primary", "tags": {"synthetic", "derivative"}},
            ),
            RawInput(
                input_id="demo-contaminated",
                input_type=RawInputType.NOTE,
                title="Synthetic Speculative Contaminated Note",
                raw_text="Maybe the bright light was a warp drive or federation starship.",
                source_uri="synthetic://demo-contaminated",
                source_kind="note",
                collected_at=DEMO_TIME,
                metadata={"tags": {"synthetic", "contamination"}},
            ),
            RawInput(
                input_id="demo-incomplete",
                input_type=RawInputType.NOTE,
                title=None,
                raw_text="Anonymous note says a light moved west.",
                source_uri=None,
                source_kind="anonymous",
                collected_at=None,
                metadata={"author": "anonymous", "tags": {"synthetic", "incomplete"}},
            ),
        ]
        demo_id = str(uuid5(NAMESPACE_URL, "synthetic-cortex-demo-workspace"))
        return DemoWorkspace(
            manifest=DemoWorkspaceManifest(
                demo_id=demo_id,
                notes=[
                    "all sources use synthetic:// or unknown demo identifiers",
                    "no real UAP data is included",
                ],
            ),
            raw_inputs=raw_inputs,
        )
