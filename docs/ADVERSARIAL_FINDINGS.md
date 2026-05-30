# Adversarial Epistemic Stress Report

Generated: 2026-05-29

Command:

```powershell
$env:PYTHONPATH='src'; python -c "from roswell_uap_cortex import AdversarialHarness, AdversarialScenarioFactory, AdversarialReportFormatter; print(AdversarialReportFormatter().format(AdversarialHarness().run(AdversarialScenarioFactory().all())))"
```

## Summary

- Scenario count: 10
- Resisted scenarios: 10
- Failed scenarios: 0
- Resistance rate: 1.000

## Findings

- adversarial-confidence-inflation: resisted; attack=confidence_inflation; failure_mode=unsupported_confidence_inflation
- adversarial-contradiction-suppression: resisted; attack=contradiction_suppression; failure_mode=hidden_contradiction
- adversarial-discourse-contamination: resisted; attack=discourse_contamination; failure_mode=discourse_as_evidence
- adversarial-missing-provenance-camouflage: resisted; attack=missing_provenance_camouflage; failure_mode=provenance_gap_hidden
- adversarial-policy-abuse: resisted; attack=policy_abuse; failure_mode=guardrail_disabled_by_policy
- adversarial-provenance-laundering: resisted; attack=provenance_laundering; failure_mode=false_independence
- adversarial-semantic-echo-chamber: resisted; attack=semantic_echo_chamber; failure_mode=similarity_as_confirmation
- adversarial-speculation-hardening: resisted; attack=speculation_hardening; failure_mode=speculation_as_fact
- adversarial-synthetic-to-real: resisted; attack=synthetic_to_real_confusion; failure_mode=synthetic_as_real_evidence
- adversarial-temporal-overreach: resisted; attack=temporal_overreach; failure_mode=fabricated_temporal_precision

## Limitations

- Adversarial scenarios are synthetic stress tests, not real-world validation.
- Resistance means expected guardrail behavior was observed in fixtures only.
- Findings do not establish truth or falsity of any external claim.
