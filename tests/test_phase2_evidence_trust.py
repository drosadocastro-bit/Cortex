from roswell_uap_cortex import (
    ContaminationEngine,
    CorroborationLayer,
    EvidenceLineageEngine,
    EvidenceLineageRecord,
    SourceTrust,
    SourceTrustEngine,
)


def test_source_trust_engine_scores_authoritative_low_risk_source_above_repost() -> None:
    engine = SourceTrustEngine()
    archival = SourceTrust(
        source_id="archive-1",
        reliability=0.9,
        transparency=0.8,
        source_authority=0.9,
        chain_of_custody=0.95,
        publication_distance=0.05,
        redaction_level=0.1,
        independent_corroboration=0.5,
        media_type="archival_document",
    )
    repost = SourceTrust(
        source_id="video-1",
        reliability=0.25,
        transparency=0.2,
        source_authority=0.1,
        chain_of_custody=0.1,
        publication_distance=0.9,
        redaction_level=0.0,
        independent_corroboration=0.0,
        media_type="tiktok",
        contamination_flags=["copy-chain contamination", "speculative escalation"],
    )

    engine.evaluate(archival)
    engine.evaluate(repost)

    assert archival.source_trust_score > repost.source_trust_score
    assert archival.source_risk_score < repost.source_risk_score
    assert 0.0 <= archival.source_trust_score <= 1.0
    assert 0.0 <= repost.source_risk_score <= 1.0


def test_lineage_engine_tracks_original_source_through_retellings() -> None:
    engine = EvidenceLineageEngine()
    original = EvidenceLineageRecord(
        source_id="archive",
        claim_key="claim-a",
        source_kind="archival_document",
    )
    copied = EvidenceLineageRecord(
        source_id="book",
        claim_key="claim-a",
        original_source_id="archive",
        parent_source_id="archive",
        source_kind="book",
    )
    retelling = EvidenceLineageRecord(
        source_id="video",
        claim_key="claim-a",
        original_source_id="archive",
        parent_source_id="book",
        source_kind="youtube",
    )
    index = engine.index_by_source([original, copied, retelling])

    assert engine.original_source_for(retelling, index) == "archive"
    assert engine.copy_chain_for(retelling, index) == ["video", "book", "archive"]
    assert engine.share_original_source(copied, retelling, index) is True


def test_contamination_engine_flags_copy_chains_and_speculative_escalation() -> None:
    engine = ContaminationEngine()
    records = [
        EvidenceLineageRecord(
            source_id="archive",
            claim_key="claim-a",
            source_kind="archival_document",
        ),
        EvidenceLineageRecord(
            source_id="forum",
            claim_key="claim-a",
            original_source_id="archive",
            parent_source_id="archive",
            source_kind="forum",
            transformations=["speculative"],
        ),
        EvidenceLineageRecord(
            source_id="tiktok",
            claim_key="claim-a",
            original_source_id="archive",
            parent_source_id="forum",
            source_kind="tiktok",
            transformations=["dramatized"],
        ),
    ]

    reports = {report.record_id: report for report in engine.assess_lineage(records)}
    tiktok_report = reports[records[2].id]

    assert "copy-chain contamination" in tiktok_report.flags
    assert "semantic duplication" in tiktok_report.flags
    assert "fictional contamination" in tiktok_report.flags
    assert "speculative escalation" in tiktok_report.flags
    assert tiktok_report.risk_score > 0.0


def test_contamination_engine_flags_citation_loops_and_source_ambiguity() -> None:
    engine = ContaminationEngine()
    ambiguous = EvidenceLineageRecord(
        source_id="unknown-post",
        claim_key="claim-b",
        original_source_id=None,
        parent_source_id="unknown-post",
        source_kind="unknown",
    )

    report = engine.assess_lineage([ambiguous])[0]

    assert "citation loop" in report.flags
    assert "source ambiguity" in report.flags


def test_corroboration_layer_separates_repetition_from_independence() -> None:
    layer = CorroborationLayer()
    records = [
        EvidenceLineageRecord(
            source_id="archive",
            claim_key="claim-a",
            source_kind="archival_document",
        ),
        EvidenceLineageRecord(
            source_id="book",
            claim_key="claim-a",
            original_source_id="archive",
            parent_source_id="archive",
            source_kind="book",
        ),
        EvidenceLineageRecord(
            source_id="independent-transcript",
            claim_key="claim-a",
            source_kind="transcript",
        ),
    ]

    assessment = layer.assess(records, claim_key="claim-a")

    assert assessment.independent_count == 2
    assert assessment.repeated_count == 1
    assert assessment.independent_source_ids == ["archive", "independent-transcript"]
    assert assessment.repeated_source_ids == ["book"]
    assert assessment.corroboration_score == 2 / 3
