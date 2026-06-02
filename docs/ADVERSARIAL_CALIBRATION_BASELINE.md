# Adversarial Calibration Baseline

Generated: 2026-06-02

This baseline records the lightweight adversarial wording detector exactly as it
behaves today. It is a credibility artifact, not a safety score. The point is to
keep true positives, true negatives, false positives, and false negatives
visible so future work cannot hide detector weakness behind a perfect-looking
number.

## Baseline Result

- true positives: 3
- true negatives: 2
- false positives: 1
- false negatives: 1
- accuracy: 0.714

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

The known false positive is useful because it shows overbroad boundary language.
The known false negative is useful because it shows that Spanish certainty
pressure needs more careful coverage before any multilingual claims are made.

## Future Work

Future calibration may add a small phrase registry, language-tagged cases,
near-miss categories, and separate metrics for precision and recall. That work
should expand the honest error surface rather than making the report look
cleaner than the system really is.
