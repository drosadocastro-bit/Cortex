# Synthetic Evaluation Report

Generated: 2026-05-29

Command:

```powershell
$env:PYTHONPATH='src'; python -c "from roswell_uap_cortex.cli import build_demo_evaluation_report; print(build_demo_evaluation_report())"
```

## Summary

- Scenario count: 38
- Passed scenarios: 38
- Failed scenarios: 0
- Overall framework-behavior pass rate: 1.000

## Metrics

- association_confirmation_separation_rate: 1.000
- bounded_confidence_rate: 1.000
- contamination_warning_rate: 1.000
- contradiction_preservation_rate: 1.000
- lineage_contamination_detection_rate: 1.000
- no_mutation_rate: 1.000
- presentation_boundary_rate: 1.000
- provenance_visibility_rate: 1.000
- review_state_boundary_rate: 1.000
- synthetic_demo_presentation_rate: 1.000
- uncertainty_exposure_rate: 1.000
- unsupported_claim_suppression_rate: 1.000

## Failed Behaviors

- none

## Limitations

- Synthetic evaluation measures framework behavior, not real-world truth.
- Passing scenarios do not validate any UAP conclusion or evidentiary claim.
- Metrics are guardrail indicators, not scientific validity scores.
