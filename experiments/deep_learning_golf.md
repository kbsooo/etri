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

## v2 Expanded Latent Golf Views

Script: `scripts/train_latent_deep_learning_golf.py`

Output: `outputs/latent_deep_learning_golf_v2_expanded_views/`

Nested stress: `outputs/nested_latent_deep_learning_golf_v2_expanded_views/`

Input:

- v1 channel-patch views:
  - `full`
  - `no_sleep`
  - `only_cross_modal`
  - `only_event`
  - `only_rhythm`
- v2 channel-patch views:
  - `full`
  - `no_sleep`
  - `only_cross_modal`
  - `only_event`
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
| best global expanded latent decoder | 0.624475 | 0.003179 | 0.076352 | `only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2` |
| full-OOF targetwise | 0.621446 | 0.006208 | 0.073280 | optimistic |
| nested targetwise | 0.626385 | 0.001269 | n/a | targetwise selection mostly discounts away |

Targetwise full-OOF gain vs subject prior:

| target | gain |
| --- | ---: |
| Q1 | 0.004454 |
| Q2 | 0.018569 |
| Q3 | 0.013833 |
| S1 | 0.002644 |
| S2 | 0.001544 |
| S3 | 0.001498 |
| S4 | 0.000913 |

Top fixed global sources:

| source | OOF logloss | drift vs v83 | note |
| --- | ---: | ---: | --- |
| `only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2` | 0.624475 | 0.076352 | best fixed global |
| `only_event__absolute_plus_deviation__linear_k4_b0.2` | 0.624517 | 0.075763 | nearly tied, no bottleneck nonlinearity needed |
| `only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.2` | 0.624903 | 0.077759 | rhythm-only remains useful |
| `only_cross_modal__deviation__linear_k4_b0.2` | 0.625415 | 0.075137 | previous v1 winner |

Nested interpretation:

- Expanded views improve the fixed global latent floor from `0.625415` to `0.624475`.
- The full-OOF targetwise score (`0.621446`) is mostly selection optimism; nested targetwise falls to `0.626385`.
- Therefore the useful carry-forward signal is not target-specific source picking. It is the fixed `only_event + absolute_plus_deviation + low-rank rank 2 / k=4` decoder.
- `only_event` becoming the best global source is important. It says small event/rhythm/state changes are more label-readable than the full fused latent when the decoder is forced to stay tiny.
- The decoder remains extremely small: mean params are 29 for the best global candidate, which fits the "hidden dim may still be too big" hypothesis.

Decision:

- Treat `0.624475` as the new fixed latent golf floor.
- Do not chase the full targetwise `0.621446` without nested or pre-fixed target rules.
- Next branch should train tiny sequence encoders from token grids with the same small-decoder discipline. A new tiny GRU/Transformer only matters if its fixed global or nested score beats `0.624475` without creating uncontrolled drift.

## v1 Tiny Transformer Dimension Golf

Encoder script: `scripts/train_hourly_transformer_encoder.py`

Golf decoder script: `scripts/train_latent_deep_learning_golf.py`

Nested stress script: `scripts/nested_deep_learning_golf_selection.py`

Outputs:

- `outputs/tiny_transformer_golf_encoder_d2_v1/`
- `outputs/tiny_transformer_golf_encoder_d4_v1/`
- `outputs/tiny_transformer_golf_encoder_d8_v1/`
- `outputs/tiny_transformer_d2_latent_golf_v1/`
- `outputs/tiny_transformer_d4_latent_golf_v1/`
- `outputs/tiny_transformer_d8_latent_golf_v1/`
- `outputs/nested_tiny_transformer_d2_latent_golf_v1/`
- `outputs/nested_tiny_transformer_d4_latent_golf_v1/`
- `outputs/nested_tiny_transformer_d8_latent_golf_v1/`

Input:

- 30-minute event-hybrid token grid: `artifacts/multires_30min_event_hybrid_grid.parquet`
- 48 tokens per day.
- Views:
  - `only_event`
  - `only_rhythm`
  - `only_cross_modal`
  - `no_sleep`
- Token features include value, missingness, time/panel context, and subject/time deviation features from the existing sequence builder.
- Encoder is a 1-layer, 1-head Transformer with `d_model` in `2`, `4`, `8`.
- Decoder uses the same golf grid: linear, low-rank rank 1-2, tiny MLP hidden 1-2; top-k 1/2/4; subject-prior blends 0.1/0.2.

Result:

| d_model | encoder probe best | encoder best view | golf fixed global | full-OOF targetwise | nested targetwise | nested gain vs subject prior | selection optimism | note |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 0.624469 | `only_event` | 0.626826 | 0.624200 | 0.627956 | -0.000302 | 0.003317 | too compressed; targetwise signal is selection noise |
| 4 | 0.623719 | `only_cross_modal` | 0.625489 | 0.623174 | 0.626112 | 0.001542 | 0.002860 | first dimension where nested signal survives |
| 8 | 0.622084 | `only_cross_modal` | 0.626371 | 0.623600 | 0.625441 | 0.002213 | 0.001841 | strongest nested tiny Transformer signal |

Best fixed global sources:

| d_model | source | OOF logloss | note |
| ---: | --- | ---: | --- |
| 2 | `only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1` | 0.626826 | not enough latent capacity |
| 4 | `only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2` | 0.625489 | better but still below expanded latent floor |
| 8 | `only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1` | 0.626371 | nested targetwise good, fixed global weak |

Nested target clues:

- `d_model=4`: Q1/Q3 repeatedly select `only_event__deviation__mlp_h2_k4_wd0.1_b0.2`; S2 repeatedly selects `only_event__deviation__mlp_h2_k2`.
- `d_model=8`: Q2 selects `only_cross_modal__deviation__linear_k4_b0.2` in all five nested folds; S1 selects `only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1` in four folds; S3 selects `only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1` in four folds.

Interpretation:

- `d_model=2` is too small: it produces attractive full-OOF targetwise results, but nested validation drops below subject prior.
- `d_model=4` is the first viable tiny Transformer latent size.
- `d_model=8` gives the best nested targetwise result (`0.625441`) and the lowest selection optimism (`0.001841`), so sequence capacity helps.
- However, no tiny Transformer fixed global decoder beats the expanded existing-latent fixed floor (`0.624475`). The current robust lesson is not "use the tiny Transformer directly"; it is that specific low-dimensional target rules are stable:
  - Q2: cross-modal deviation linear axis.
  - S1: event absolute+deviation low-rank axis.
  - S3: cross-modal absolute+deviation tiny one-hidden-axis.
- This supports the user's concern: tiny heads can expose signal, but fully automatic targetwise picking still needs nested/fixed rules.

Decision:

- Carry forward `d_model=8` as the best tiny Transformer representation for target-rule mining.
- Keep `d_model=4` as the minimum viable size.
- Reject `d_model=2` for now.
- Next sequence branch should test tiny GRU with the same 30-minute token views to see whether recurrent compression gives a stronger fixed global decoder than Transformer CLS.

## v1 Tiny GRU Dimension Golf

Encoder script: `scripts/train_hourly_transformer_encoder.py --encoder-type gru`

Golf decoder script: `scripts/train_latent_deep_learning_golf.py`

Nested stress script: `scripts/nested_deep_learning_golf_selection.py`

Outputs:

- `outputs/tiny_gru_golf_encoder_d2_v1/`
- `outputs/tiny_gru_golf_encoder_d4_v1/`
- `outputs/tiny_gru_golf_encoder_d8_v1/`
- `outputs/tiny_gru_d2_latent_golf_v1/`
- `outputs/tiny_gru_d4_latent_golf_v1/`
- `outputs/tiny_gru_d8_latent_golf_v1/`
- `outputs/nested_tiny_gru_d2_latent_golf_v1/`
- `outputs/nested_tiny_gru_d4_latent_golf_v1/`
- `outputs/nested_tiny_gru_d8_latent_golf_v1/`

Input:

- Same 30-minute event-hybrid token grid and views as the tiny Transformer sweep.
- Encoder is a 1-layer GRU with hidden size `2`, `4`, or `8`.
- Decoder grid is identical to the Transformer sweep.

Result:

| d_model | encoder probe best | encoder best view | encoder params | golf fixed global | full-OOF targetwise | nested targetwise | nested gain vs subject prior | selection optimism | note |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 0.624398 | `no_sleep` | 1,727 | 0.626739 | 0.624249 | 0.627061 | 0.000593 | 0.002423 | better than Transformer d2 nested, but weak |
| 4 | 0.622912 | `only_cross_modal` | 1,015 | 0.626403 | 0.623314 | 0.625675 | 0.001979 | 0.002347 | best GRU setting |
| 8 | 0.623662 | `no_sleep` | 6,239 | 0.626520 | 0.624135 | 0.627370 | 0.000284 | 0.002978 | larger GRU does not help |

Comparison to tiny Transformer:

- Best GRU nested targetwise: `0.625675` at `d_model=4`.
- Best Transformer nested targetwise: `0.625441` at `d_model=8`.
- Best GRU fixed global: `0.626403`, still weaker than the expanded latent fixed floor (`0.624475`).
- GRU has a smoother encoder probe than d2 Transformer, but its golf-decoded fixed signal remains weak.

Interpretation:

- Recurrent compression is not the missing breakthrough by itself.
- The sweet spot for GRU is `d_model=4`, not `8`; increasing hidden size introduces more selection-looking signal without improving nested validation.
- Transformer d8 remains the better tiny sequence representation for mining stable target rules, especially Q2 cross-modal deviation and S1/S3 event/cross-modal axes.
- The most useful conclusion is architectural: sequence encoders should stay tiny, but decoder rules must be fixed or nested. Larger sequence capacity alone does not solve the 450-label bottleneck.

Decision:

- Keep tiny GRU as a checked negative/secondary branch.
- Continue sequence work from the stronger tiny Transformer d8 branch, but use the GRU d4 result as evidence that `d_model=4` is often enough.
- Next improvement should not simply increase hidden size. It should change tokenization or make target rules fixed from nested selection counts.
