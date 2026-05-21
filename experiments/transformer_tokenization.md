# Transformer Tokenization Experiments

Last updated: 2026-05-21

## Goal

Find a better input representation for the Transformer encoder. The working hypothesis is that most of the gain should come from tokenization and preprocessing, not from making the head bigger.

The comparison now covers:

- 24 hourly tokens from prebuilt hourly artifacts.
- 144 raw-derived 10-minute tokens.
- 48 raw-derived 30-minute tokens.
- Feature-family views: `full`, `no_sleep`, `only_rhythm`, `only_cross_modal`, plus earlier hourly ablations.
- Subject-token deviation features: value, missingness, and per-subject same-token z/deviation.
- A small MoE head over Transformer experts.

## Token Builders

Script: `scripts/build_multires_token_grid.py`

Raw object-list streams are summarized before binning:

- GPS: speed, lat/lon volatility, altitude.
- HR: mean/std/min/max/rMSSD/count.
- Ambience: coarse speech/music/vehicle/outdoor/indoor/alarm/silence buckets.
- WiFi/BLE: scan count, unique device count, RSSI mean/max.
- Usage: app count, total/max usage time.
- Scalar streams: activity, screen, charging, light, pedometer.

The builder keeps coverage and missingness as first-class signal instead of forward-filling everything away.

Generated reports:

- `artifacts/multires_10min_grid_report.md`
- `artifacts/multires_30min_grid_report.md`

## Encoder Experiments

Script: `scripts/train_hourly_transformer_encoder.py`

This script now supports arbitrary fixed within-day token tables:

```text
token table + token_col + tokens_per_day
-> fixed subject-day sequence
-> optional subject-token deviation features
-> masked-token Transformer SSL
-> day embedding
-> fold-safe subject-prior residual probe
```

### Current Results

| tokenization | best view | targetwise OOF | interpretation |
| --- | ---: | ---: | --- |
| 24 hourly | `only_rhythm` | `0.619825` | coarse rhythm is useful and relatively stable |
| 10-minute raw grid + deviation | `only_cross_modal` | `0.621938` | too sparse globally, but cross-modal short events help |
| 30-minute raw grid + deviation | `no_sleep` | `0.618590` | best single tokenization so far; preserves events without 10-minute sparsity |

The 30-minute result is the first tokenization improvement over the 24-hour branch, but it is still not enough alone. It points to 30-minute/event-level preprocessing as the next best data representation.

## MoE Head

Script: `scripts/train_transformer_moe_head.py`

Output: `outputs/transformer_moe_head_v1/`

The MoE head treats each tokenization/view prediction as an expert. It trains a small nested logistic head per target using:

- expert logits,
- expert dispersion,
- panel position,
- fold-safe subject prior.

Results:

- Best nested MoE: `nested_moe_logreg_c0p3`
- OOF avg logloss: `0.611527`
- Drift vs v83 reference: `0.086812`
- Full-OOF targetwise expert diagnostic: `0.614175`

This is the strongest independent Transformer branch so far and beats the prior independent fixed-permission policy OOF (`0.615095`). The caveat is drift: the MoE branch moves farther from v83/public-aligned coordinates, so it is a breakthrough signal, not yet a submission-safe candidate.

Target-source pattern:

- Q1: 10-minute `only_rhythm`
- Q2: 30-minute `no_sleep`
- Q3: 24-hour `only_rhythm`
- S1/S2/S4: 30-minute `only_cross_modal`
- S3: 24-hour `only_cross_modal`

## Head Diagnostics

### Embedding-level MoE

Script: `scripts/train_transformer_embedding_moe.py`

Output: `outputs/transformer_embedding_moe_head_v1/`

This head reads view embeddings directly. Each Transformer view embedding is reduced inside the outer fold with PCA, then a small target-specific logistic head sees:

- reduced embeddings,
- optional expert logits,
- panel position,
- fold-safe subject prior.

Result:

- Best: `logit_plus_embedding_pca2_c0p01`
- OOF avg logloss: `0.636678`

Decision:

- Negative result. Directly reading SSL embeddings with 450 labels is much worse than prediction-level MoE (`0.611527`).
- This says the current SSL embeddings are not linearly label-readable enough. The useful signal appears after each view has already been decoded into target probabilities.
- Do not spend the next step on larger embedding heads unless the SSL objective itself becomes more label-aligned.

### Nested expert-selection optimism

Script: `scripts/nested_transformer_expert_selection.py`

Output: `outputs/nested_transformer_expert_selection_v1/`

This diagnostic estimates how much of the full-OOF targetwise expert selection is selection bias:

- Full-OOF targetwise expert selection: `0.614175`
- Nested targetwise expert selection: `0.617817`
- Estimated selection optimism: `0.003642`
- Full-selection submission drift vs v83: `0.089719`

Stable nested selections:

- Q1: 10-minute `only_rhythm`, selected `5/5`.
- Q2: 30-minute `no_sleep`, selected `5/5`.
- Q3: 24-hour `only_rhythm`, selected `4/5` plus one nearby 24-hour rhythm global source.
- S4: 30-minute `only_cross_modal`, selected `4/5`.

Less stable:

- S1/S2/S3 move among 30-minute cross-modal, 24-hour cross-modal, and 30-minute no-sleep.

Decision:

- The targetwise view pattern is not just noise. Q1/Q2/Q3/S4 have stable source preferences.
- The full-OOF `0.614175` should be discounted to roughly `0.6178` for honest source-selection expectation.
- The prediction-level nested MoE (`0.611527`) remains the strongest Transformer breakthrough signal, but it needs drift and public-coordinate stress testing.

## Current Decision

Adopt the Transformer/MoE branch as a real breakthrough direction.

Do not conclude that 10-minute is better just because it is finer. The current evidence says:

```text
24-hour rhythm is stable.
10-minute is too sparse globally.
30-minute is the best raw-derived resolution so far.
MoE over resolutions/views is better than choosing one global tokenization.
```

Next high-value experiments:

1. Build a 30-minute + event-token hybrid instead of only fixed bins.
2. Stress-test prediction-level MoE drift/public-coordinate sensitivity.
3. Add explicit missing-gap episode tokens for sensor off/charging/wear-time states.
4. Revisit embedding-level heads only after the SSL objective is more label-aligned.
