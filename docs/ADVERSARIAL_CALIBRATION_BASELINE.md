# Adversarial Calibration Baseline

Generated: 2026-06-02

Reading guide: see `docs/ADVERSARIAL_RESULTS_GUIDE.md` for how this calibration
baseline differs from smoke adversarial findings and hard adversarial results.

This baseline records the lightweight adversarial wording detector exactly as it
behaves today. It is a credibility artifact, not a safety score. The point is to
keep true positives, true negatives, false positives, and false negatives
visible so future work cannot hide detector weakness behind a perfect-looking
number.

Phase 26.2 established a small smoke baseline with accuracy `0.714`. Phase 26.3
expands that into a harder calibration set with more benign boundary language,
soft certainty inflation, negated confirmation wording, Spanish variants,
presentation aggregation traps, and transferability pressure.

## Expanded Baseline Result

- calibration cases: 16
- true positives: 5
- true negatives: 4
- false positives: 3
- false negatives: 4
- accuracy: 0.562
- precision: 0.625
- recall: 0.556
- false positive rate: 0.429
- false negative rate: 0.444
- multilingual cases: 5
- known limitation notes: 7

This accuracy is not certification, operational validation, real-world safety evidence,
or proof that Cortex is robust against multilingual adversarial input.
It is a deterministic synthetic baseline for framework-behavior calibration.

## Calibration Cases

- `calibration-true-positive-review`: detects review-state laundering in
  English wording that tries to turn review into confirmation.
- `calibration-true-negative-provenance`: does not flag a benign sentence that
  says provenance remains visible and bounded.
- `calibration-false-positive-certification-boundary`: intentionally records a
  benign boundary note that contains certification language and is overflagged.
- `calibration-false-negative-subtle-spanish`: intentionally records subtle
  Spanish certainty wording that the lightweight detector does not currently
  catch.
- `calibration-true-positive-spanish`: detects direct Spanish confirmation
  language.
- `calibration-true-negative-spanish`: does not flag a benign Spanish sentence
  about provenance visibility.
- `calibration-true-positive-transferability`: detects transferability language
  that tries to turn Cortex into operational or dispatch authority.
- `calibration-false-negative-soft-proof`: records soft proof language that is
  not currently caught.
- `calibration-true-positive-priority-truth`: detects review priority being
  laundered into truth.
- `calibration-true-positive-presentation-grouping`: detects presentation
  grouping being laundered into corroboration.
- `calibration-true-negative-safety-boundary`: does not flag a benign sentence
  saying safety is not evaluated.
- `calibration-false-positive-certification-negation`: records negated
  certification language that is still overflagged.
- `calibration-true-negative-technical-inspiration`: does not flag technical
  inspiration language that stays within bounds.
- `calibration-false-negative-spanish-confirma`: records a Spanish verb form
  that is not currently caught.
- `calibration-false-positive-spanish-negated-confirmed`: records negated
  Spanish confirmation language that is overflagged.
- `calibration-false-negative-safe-assumption`: records soft safe-assumption
  wording that is not currently caught.

## Error Taxonomy

- `review_state_laundering`: review status or priority is framed as truth.
- `benign_provenance_boundary`: provenance visibility language that should not
  trigger an attack finding.
- `overbroad_authority_language`: certification or authority words appear in a
  bounded or negated sentence and may be overflagged.
- `subtle_certainty_inflation`: soft wording such as proof, assumption, or
  implication attempts to inflate certainty.
- `multilingual_certainty`: non-English certainty pressure, currently covered
  only by tiny synthetic examples.
- `negated_confirmation_language`: confirmation words appear inside negation
  and may be overflagged.
- `transferability_pressure`: synthetic framework behavior is pushed toward
  predictive-maintenance, dispatch, certification, or operational authority.
- `presentation_aggregation_trap`: grouping or card layout is framed as
  corroboration.
- `benign_safety_boundary`: safety language that explicitly says safety is not
  evaluated.
- `technical_inspiration_boundary`: technical papers or concepts used as
  bounded inspiration rather than authority.

## Interpretation Rules

- Do not tune toward a perfect-looking score.
- Do not remove false positives or false negatives from the report unless the
  detector behavior actually changes and the baseline is updated openly.
- Do not treat the baseline as evidence that Cortex can detect real-world
  adversarial language.
- Do not treat the baseline as evidence that Cortex is suitable for predictive
  maintenance, dispatch, certification, or operational safety use.
- Do not treat multilingual coverage as complete.

## Known Weaknesses

The detector is phrase based. It can catch direct wording such as confirmation,
certification, and operational-authority pressure, but it does not perform
general semantic understanding. Subtle paraphrases, sarcasm, translation
variants, and domain-specific euphemisms can evade it.

The known false positives are useful because they show overbroad boundary
language and negation weakness. The known false negatives are useful because
they show that soft certainty pressure and Spanish wording need more careful
coverage before any stronger claims are made.

## Future Work

Future calibration may add a small phrase registry, language-tagged cases,
near-miss categories, and broader precision/recall analysis. That work should
expand the honest error surface rather than making the report look cleaner than
the system really is.
