# Evidence and Source Trust Architecture

Phase 2 adds an epistemic layer above memory. Memory can preserve and retrieve
records, but trust architecture decides how cautiously each record should be
handled.

The framework distinguishes:

- primary evidence
- secondary interpretation
- speculation
- contaminated repetition
- unsupported claims

It does not delete uncertainty, collapse conflicts, or enforce conclusions.

## SourceTrustEngine

`SourceTrustEngine` scores source trust and source risk from explicit fields:

- `source_authority`
- `chain_of_custody`
- `publication_distance`
- `redaction_level`
- `independent_corroboration`
- `media_type`
- `contamination_flags`

Outputs are stored as:

- `source_trust_score`
- `source_risk_score`

These scores are not truth labels. They are caution controls.

## EvidenceLineageEngine

`EvidenceLineageEngine` tracks source ancestry:

```text
original source
  -> copied source
    -> video retelling
      -> forum repost
        -> short-form speculation
```

Lineage prevents repeated copies of the same claim from being counted as
independent evidence.

## ContaminationEngine

`ContaminationEngine` flags deterministic risk patterns:

- copy-chain contamination
- semantic duplication
- citation loops
- fictional contamination
- speculative escalation
- source ambiguity

Flags increase caution without deleting the record.

## CorroborationLayer

`CorroborationLayer` separates same-source repetition from independent
corroboration. If five records all descend from one original source, they count
as one source lineage, not five independent confirmations.

## Relationship to Memory

Memory strength controls cognitive prominence. Source trust controls epistemic
caution. A strong memory can still be risky if it is a contaminated repetition.
A weak memory can remain important if it preserves a rare original source.
