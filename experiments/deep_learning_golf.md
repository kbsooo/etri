# Deep Learning Golf Experiments

Last updated: 2026-05-21

## Purpose

Restart the neural Encoder-Decoder path from the smallest possible models. The aim is not to tune a public-anchor submission, but to find the first parameter scale where our own subject-relative features create label signal.

Rules for this branch:

- Use v83 only as a drift reference, not as a teacher.
- Start from bias-only and subject-prior baselines.
- Keep neural decoders tiny: linear, low-rank rank 1-4, and tanh MLP hidden 1-4.
- Keep input dimensionality tiny too: fold-local top-k feature selection with k in 1, 2, 4, 8.
- Record parameter count, OOF logloss/F1, target gain vs subject prior, prediction mean shift, panel drift, and subject drift.

## v1 Daily Subject-Relative Golf

Script: `scripts/train_deep_learning_golf.py`

Output: `outputs/deep_learning_golf_v1/`

Input:

- Raw lifelog daily/window aggregates from `scripts/train_tiny_deviation_encoder.py`.
- Fold-local subject-relative transforms: delta, z-score, and ratio against the subject's fit-fold baseline.
- Raw + subject-relative variants.

Models:

- `bias_global`: target train mean only.
- `subject_prior`: fold-safe subject-smoothed target rate.
- Linear decoders.
- Low-rank decoders with rank 1-4.
- Tiny MLP decoders with hidden 1-4.

Result:

| candidate | OOF logloss | gain vs subject prior | drift vs v83 | note |
| --- | ---: | ---: | ---: | --- |
| subject_prior | 0.627654 | 0.000000 | 0.061947 | baseline |
| best global tiny decoder | 0.625725 | 0.001929 | 0.068649 | low-rank rank 3, k=2, 34 params |
| targetwise tiny decoder | 0.622155 | 0.005499 | 0.067578 | targetwise selected, optimistic until nested |

Targetwise gain vs subject prior:

| target | gain |
| --- | ---: |
| Q1 | 0.007254 |
| Q2 | 0.012439 |
| Q3 | 0.011960 |
| S1 | 0.000410 |
| S2 | 0.000816 |
| S3 | 0.002547 |
| S4 | 0.003067 |

Interpretation:

- The user's "hidden dim may still be too big" concern was correct. The best global model uses only two selected input axes and a rank-3 bottleneck.
- The signal is strongest for Q1/Q2/Q3, weaker for S-family. This looks like a simple subject-relative day-state axis rather than a rich deep latent yet.
- `raw_plus_deviation` dominates the global leaderboard, while pure `deviation` appears only in targetwise Q2/S1. Absolute day state plus personal deviation is better than deviation alone in this daily aggregate view.
- Drift is slightly higher than subject prior but far below the more aggressive Transformer MoE branch. This is a useful small-model floor, not a breakthrough submission.

Failure risk:

- Targetwise selection is full-OOF selected and may be optimistic.
- The best global gain is small (`0.001929`), so it proves signal exists but does not yet solve the score gap.
- The branch still uses day/window aggregates, not tiny GRU/Transformer sequence encoders.

Next:

1. Nested targetwise selection for this golf grid.
2. Same golf decoder over channel-patch Transformer latents, but with bottleneck 1-4 and no large embedding head.
3. Tiny GRU/Transformer sequence encoders with `d_model`/hidden 1, 2, 4, 8 and the same subject-relative decoder discipline.
