# Phase 27.1: Evidence Quality Security And Hygiene

Phase 27.1 is a safety and documentation pass after the evidence-quality
rubric. It does not add a new reasoning layer, UI, vector feature, live
inference path, or autonomous workflow.

## Purpose

The evidence-quality rubric introduces bounded scores and labels. Those are
useful for review, but they create a familiar risk: a score may be mistaken for
truth, reliability, certification, or claim confirmation.

This pass checks that the new quality layer stays narrow.

## What Changed

- Added serializer round-trip tests for `EvidenceQualityAssessment`.
- Added unknown-field preservation through assessment metadata.
- Added hygiene checks for network, process, dynamic execution, and unsafe
  deserialization patterns in quality modules.
- Added documentation checks that reject truth, proof, validation, or
  reliability framing for quality labels.
- Updated `DEBUGGING_AND_SECURITY.md` with the Phase 27 quality check command.

## Boundary

Evidence quality remains record-condition context for review. It is not truth
confidence, claim confidence, source acceptance, corroboration, graph support,
safety evidence, certification evidence, or operational validity.
