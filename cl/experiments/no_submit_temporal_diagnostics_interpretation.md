# No-submit experiment note — label temporal diagnostics

User constraint: do **not** spend public submissions casually. Tiny 3rd-decimal local differences are not evidence.

## What I tested

Script:

```text
scripts/59_label_temporal_diagnostics_no_submit.py
```

Outputs:

```text
experiments/label_temporal_diagnostics_no_submit.csv
experiments/label_temporal_diagnostics_no_submit_summary.csv
experiments/label_temporal_diagnostics_no_submit_report.md
```

This uses only train labels under masked validation. It does **not** create submission files.

Splits tested:

- `testpattern`: masks train rows shaped like actual test positions.
- `random_gap`: same-subject middle/late gaps.
- `tail`: future-only tail masks.

Predictors tested:

- global label mean
- subject mean
- previous label / next label / nearest label
- previous+next interpolation
- exponential same-subject smoothers
- local 3-neighbor mean

## Structural takeaways, not decimal-chasing

### Strongest label-temporal target: Q2

Q2 consistently benefits from local same-subject label smoothing across test-pattern, random-gap, and tail masks.

This makes Q2 genuinely state-like, but learned calibrator had tail risk earlier, so the next experiment should be **better-constrained Q2 temporal features**, not an immediate submission.

### S2 also has real temporal structure

S2 is not best with short-neighbor smoothing; it prefers broader `tau30` style smoothing and also had the cleanest tiny-DL signal earlier.

This supports a non-submission experiment direction:

- S2-specific latent/representation probes
- broader-timescale behavior state features
- avoid overreacting to day-to-day label flips

### S1/S3 look mostly subject-baseline dominated

For S1 and S3, subject mean is hard to beat. Extra temporal smoothing generally does not help in this diagnostic.

So for now, do not spend modeling effort or public submissions on S1/S3 unless a new feature family has a clear mechanism.

### Q1 is split-dependent

Q1 improves in test-pattern/random-gap but fails on tail. That means Q1 is probably interpolation-friendly but not stable future-forecasting-friendly.

Use Q1 only in diagnostics unless a validation design matching actual public split gets stronger.

### Q3 is suspicious

Q3 label smoothing looks good on interleaved masks, but tail/global behavior is weird. This supports the previous idea that Q3 can easily overfit validation assumptions.

Do not submit Q3 changes without controlled evidence.

### S4 is weak/moderate

S4 has some broad temporal signal on random-gap/tail, but not enough to call strong. It still deserves mechanism-feature work, not public submission.

## Practical next experiments

No public submission yet.

Next useful experiments:

1. **Q2 constrained temporal-state model**
   - Small monotonic/smoothed model using local label features only.
   - Gate against tail and random-gap, not just test-pattern.
   - Penalize prediction shift explicitly.

2. **S2 broad-timescale latent probe**
   - Since S2 likes `tau30` and tiny DL, test broader weekly/monthly behavioral-state features.
   - Use latent features as components, not full replacement.

3. **Q3 falsification test**
   - Build diagnostic that intentionally varies Q3 only in validation, not public.
   - If Q3 is unstable across masks, freeze it to base.

4. **S1/S3 deprioritize**
   - Treat as subject-baseline dominated until a mechanism appears.

## Submission bar

A candidate should not be proposed unless it clears a coarse structural bar, e.g.:

- improves the same target family across test-pattern + random-gap + tail, not just one split;
- has a plausible mechanism;
- has small/moderate test prediction shift;
- changes only targets with clear evidence;
- expected gain is large enough to matter, not a third-decimal local-CV artifact.
