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

## v1 Nested Selection Stress

Script: `scripts/nested_deep_learning_golf_selection.py`

Output: `outputs/nested_deep_learning_golf_selection_v1/`

This diagnostic reuses `outputs/deep_learning_golf_v1/golf_fold_losses.csv`. It selects the best source for each target on four folds and scores that chosen source on the held-out fold.

Result:

| candidate | OOF logloss | gain vs subject prior | note |
| --- | ---: | ---: | --- |
| subject_prior | 0.627654 | 0.000000 | baseline |
| best global tiny decoder | 0.625725 | 0.001929 | still credible |
| full-OOF targetwise | 0.622155 | 0.005499 | optimistic |
| nested targetwise | 0.627983 | -0.000329 | targetwise selection does not survive |

Conclusion:

- The apparent `0.005499` full-OOF targetwise gain was almost exactly selection optimism (`0.005829`).
- The robust signal is not target-specific source selection. It is the fixed global low-rank model: `raw_plus_deviation__lowrank_r3_k2_wd0.1_b0.2`.
- This is useful because it clarifies the next decoder rule: do not targetwise-pick tiny models from a wide grid unless the selection is nested or fixed in advance.
- For the next branch, use the tiny global low-rank result as the minimum credible decoder floor, then test whether sequence encoders create a better fixed representation.

## v1 Latent Golf on Channel-Patch Transformer CLS

Script: `scripts/train_latent_deep_learning_golf.py`

Output: `outputs/latent_deep_learning_golf_v1/`

Nested stress: `outputs/nested_latent_deep_learning_golf_selection_v1/`

Input:

- Existing channel-patch Transformer CLS embeddings from:
  - `full`
  - `no_sleep`
  - `only_cross_modal`
- Fold-local subject-relative variants:
  - `deviation`
  - `absolute_plus_deviation`
- Tiny decoders:
  - linear
  - low-rank rank 1-2
  - tiny MLP hidden 1-2

Result:

| candidate | OOF logloss | gain vs subject prior | drift vs v83 | note |
| --- | ---: | ---: | ---: | --- |
| subject_prior | 0.627654 | 0.000000 | 0.061947 | baseline |
| best global latent tiny decoder | 0.625415 | 0.002239 | 0.075137 | `only_cross_modal__deviation__linear_k4_b0.2` |
| full-OOF targetwise | 0.621691 | 0.005963 | 0.071488 | optimistic |
| nested targetwise | 0.625650 | 0.002004 | n/a | survives selection stress |

Interpretation:

- Unlike daily aggregate golf, latent golf keeps a positive nested gain (`0.002004`) after targetwise selection stress.
- The best global model is not nonlinear or large: it is a plain linear decoder over 4 selected subject-relative axes from the `only_cross_modal` channel-patch Transformer view.
- This is the clearest evidence so far that the Transformer encoder is not useless; it creates a small but more robust label-readable latent than daily aggregate golf.
- The robust source is specifically `only_cross_modal::deviation`, so the useful latent is a personal deviation in cross-modal state, not absolute day identity.
- Drift is higher than subject prior and daily golf, so this is a breakthrough signal branch, not a direct public-safe submission.

Next:

1. Expand latent golf to include `only_event`, `only_rhythm`, and v2 channel-patch views.
2. Keep the global/nested discipline: do not trust full-OOF targetwise selection.
3. Build tiny sequence encoders only if they can beat this fixed latent floor (`0.625415` global, `0.625650` nested targetwise).
