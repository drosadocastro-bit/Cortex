# Adversarial Epistemic Stress Report

Generated: 2026-06-02

Reading guide: see `docs/ADVERSARIAL_RESULTS_GUIDE.md` for how this smoke
report differs from calibration baselines, hard adversarial results, and
remediation tracking.

Command:

```powershell
$env:PYTHONPATH='src'; python -c "from roswell_uap_cortex import AdversarialHarness, AdversarialScenarioFactory, AdversarialReportFormatter; print(AdversarialReportFormatter().format(AdversarialHarness().run(AdversarialScenarioFactory().all())))"
```

## Summary

- Scenario count: 17
- Resisted scenarios: 17
- Failed scenarios: 0
- Resistance rate: 1.000

## Findings

- adversarial-authority-laundering: resisted; attack=authority_laundering; failure_mode=inspiration_as_certification
- adversarial-confidence-inflation: resisted; attack=confidence_inflation; failure_mode=unsupported_confidence_inflation
- adversarial-contradiction-suppression: resisted; attack=contradiction_suppression; failure_mode=hidden_contradiction
- adversarial-discourse-contamination: resisted; attack=discourse_contamination; failure_mode=discourse_as_evidence
- adversarial-missing-data-prettification: resisted; attack=missing_data_prettification; failure_mode=missing_as_harmless
- adversarial-missing-provenance-camouflage: resisted; attack=missing_provenance_camouflage; failure_mode=provenance_gap_hidden
- adversarial-multilingual-certainty-inflation: resisted; attack=multilingual_certainty_inflation; failure_mode=non_english_certainty_inflation
- adversarial-policy-abuse: resisted; attack=policy_abuse; failure_mode=guardrail_disabled_by_policy
- adversarial-presentation-aggregation-trap: resisted; attack=presentation_aggregation_trap; failure_mode=aggregation_as_corroboration
- adversarial-provenance-laundering: resisted; attack=provenance_laundering; failure_mode=false_independence
- adversarial-quality-score-laundering: resisted; attack=quality_score_laundering; failure_mode=quality_as_confirmation
- adversarial-review-state-laundering: resisted; attack=review_state_laundering; failure_mode=review_as_confirmation
- adversarial-semantic-echo-chamber: resisted; attack=semantic_echo_chamber; failure_mode=similarity_as_confirmation
- adversarial-speculation-hardening: resisted; attack=speculation_hardening; failure_mode=speculation_as_fact
- adversarial-synthetic-to-real: resisted; attack=synthetic_to_real_confusion; failure_mode=synthetic_as_real_evidence
- adversarial-temporal-overreach: resisted; attack=temporal_overreach; failure_mode=fabricated_temporal_precision
- adversarial-transferability-leap: resisted; attack=transferability_leap; failure_mode=transferability_as_operational_authority

## Calibration

The lightweight wording detector is calibrated with expanded synthetic
true-positive, true-negative, false-positive, and false-negative examples:

- cases: 16
- true_positives: 5
- true_negatives: 4
- false_positives: 3
- false_negatives: 4
- accuracy: 0.562
- precision: 0.625
- recall: 0.556
- false_positive_rate: 0.429
- false_negative_rate: 0.444
- multilingual_cases: 5

The false-positive examples include benign or negated authority and
confirmation language. The false-negative examples include soft certainty
inflation and subtle Spanish certainty wording not covered by the lightweight
detector. These are retained as known limitations, not hidden failures.

See `docs/ADVERSARIAL_CALIBRATION_BASELINE.md` for the locked calibration
baseline and interpretation rules.

## Limitations

- Adversarial scenarios are synthetic stress tests, not real-world validation.
- Resistance means expected guardrail behavior was observed in fixtures only.
- Findings do not establish truth or falsity of any external claim.
- Calibration checks wording patterns only, not general semantic understanding.
- Precision and recall are detector-behavior metrics, not safety validation.
