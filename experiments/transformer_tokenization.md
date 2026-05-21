# Transformer Tokenization Experiments

Last updated: 2026-05-21

## Goal

Find a better input representation for the Transformer encoder. The working hypothesis is that most of the gain should come from tokenization and preprocessing, not from making the head bigger.

The comparison now covers:

- 24 hourly tokens from prebuilt hourly artifacts.
- 144 raw-derived 10-minute tokens.
- 48 raw-derived 30-minute tokens.
- 48 raw-derived 30-minute event-hybrid tokens.
- Channel-independent value/mask patch tokens over the 30-minute event-hybrid grid.
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

## Event-Hybrid 30-Minute Grid

Script: `scripts/build_multires_token_grid.py --event-hybrid`

Output:

- `artifacts/multires_30min_event_hybrid_grid.parquet`
- `outputs/event_hybrid30_transformer_encoder_v1/`

This branch added explicit episode-style features on top of the raw-derived 30-minute grid:

- sensor-present flags by modality,
- no-wear / phone-active / charging / moving / social-audio / low-coverage states,
- state start/end indicators,
- missing and present run lengths,
- event and transition density.

Result:

| representation | best view | targetwise OOF | interpretation |
| --- | ---: | ---: | --- |
| 30-minute event-hybrid stacked `[B,T,F]` | `no_sleep` | `0.622582` | episode features alone did not improve the stacked Transformer branch |

Decision:

- The event features are useful as a cleaner missingness/state vocabulary, but concatenating them into `[B,T,F]` did not create a stronger latent.
- This failure supports moving from time-wise stacking to value/mask channel-patch tokenization.

## Channel-Independent Patch Transformer

Script: `scripts/train_channel_patch_transformer_encoder.py`

Outputs:

- `outputs/channel_patch_transformer_encoder_v1/`
- `outputs/channel_patch_transformer_patch_sweep_v1/patch2/`
- `outputs/channel_patch_transformer_patch_sweep_v1/patch8/`

Architecture:

```text
30-minute event-hybrid grid
-> values [B, C, T] and masks [B, C, T]
-> channel-independent patches [B, C, P, patch_len]
-> shared temporal Transformer per channel
-> channel Transformer over modality/channel summaries
-> static context injected into CLS: subject, weekday, month, panel index/position
-> masked patch reconstruction SSL
-> fold-safe subject-prior residual/logistic probe
```

This is the first branch that implements the SOTA-style data structure discussed during planning: channel-independent patching, value/mask tensor pairs, and static context joint embedding.

### Main Patch Length 4 Result

Patch length 4 means 4 x 30-minute tokens = 2-hour patches.

| view | targetwise OOF | drift vs v83 | channels |
| --- | ---: | ---: | ---: |
| `no_sleep` | `0.618767` | `0.100180` | 87 |
| `only_event` | `0.619042` | `0.096649` | 45 |
| `full` | `0.619794` | `0.085971` | 110 |
| `no_sparse_position` | `0.620093` | `0.094730` | 103 |
| `no_event` | `0.620150` | `0.093270` | 65 |
| `only_rhythm` | `0.620471` | `0.098322` | 37 |
| `only_cross_modal` | `0.620719` | `0.095392` | 69 |

Best target losses for `no_sleep`:

| target | loss |
| --- | ---: |
| Q1 | `0.672177` |
| Q2 | `0.677586` |
| Q3 | `0.664566` |
| S1 | `0.569332` |
| S2 | `0.569299` |
| S3 | `0.532886` |
| S4 | `0.645522` |

### Patch Sweep

| patch length | best view | targetwise OOF | drift vs v83 | interpretation |
| ---: | --- | ---: | ---: | --- |
| 2 | `no_sleep` | `0.619763` | `0.095294` | too fine; more temporal detail did not help |
| 4 | `no_sleep` | `0.618767` | `0.100180` | best current channel-patch setting |
| 8 | `full` | `0.619152` | `0.086491` | more stable but too coarse |

Decision:

- The new data structure is valid: its first serious run is essentially tied with the best stacked 30-minute branch.
- The best view remains `no_sleep`, suggesting sleep/body channels can blur the current label-readable latent when naively included.
- Patch length 4 is the current default. Patch 2 overfits/noises the latent; patch 8 loses useful transitions.
- The branch is not yet a public submission candidate because drift remains high, especially for the `no_sleep` best view.
- Next high-value work is not a bigger encoder; it is a decoder/fusion layer that uses modality/channel latents with drift-aware regularization.

## Channel Latent Fusion Decoder

Scripts:

- `scripts/train_channel_patch_transformer_encoder.py`
- `scripts/train_channel_latent_fusion_decoder.py`

Outputs:

- `outputs/channel_patch_transformer_encoder_v2/`
- `outputs/channel_latent_fusion_decoder_relative_v1/`
- `outputs/channel_latent_fusion_decoder_curated_v1/`

Motivation:

The first channel-patch encoder still decoded only a collapsed day CLS vector. That loses the reason we moved to channel-independent tokens in the first place. The v2 encoder now saves both:

```text
day CLS:        [B, D]
channel latent: [B, C, D]
```

The fusion decoder groups channel latents into modality experts:

- `event`
- `body`
- `phone`
- `mobility`
- `ambience`
- `radio`
- `light`
- `cross`
- combined groups such as `behavior`, `physio`, and `all_groups`

It then evaluates fold-safe probes over each expert and target-wise fuses the useful ones.

### Subject-Relative Deviation Decoder

The target definition is subject-relative: each label is 1 when the self-report is above that subject's own experimental-period average. Therefore absolute latent coordinates are a poor decoder input. The fusion decoder now tests subject-centered latent variants:

```text
z_rel(subject, day) = z(subject, day) - mean_train_subject(z)
```

This directly removes the subject baseline before the supervised probe sees the latent.

### Results

| decoder | candidate mode | targetwise OOF | drift vs v83 | interpretation |
| --- | --- | ---: | ---: | --- |
| channel-patch CLS baseline | collapsed CLS | `0.618767` | `0.100180` | best prior channel-patch encoder |
| channel latent fusion | relative-only | `0.618158` | `0.075584` | subject-relative latent reduces drift strongly |
| channel latent fusion | curated absolute + relative | `0.616980` | `0.077224` | best current channel-patch decoder |

Best curated target-wise sources:

| target | selected source | loss |
| --- | --- | ---: |
| Q1 | `full__cls_plus_physio__abs_plus_subrel_train` | `0.662714` |
| Q2 | `only_cross_modal__cls_plus_all_groups__subrel_train` | `0.686355` |
| Q3 | `full__cls_plus_all_groups__subrel_train` | `0.659397` |
| S1 | `full__cls_plus_physio__abs_plus_subrel_train` | `0.564499` |
| S2 | `full__cls_plus_body` | `0.575857` |
| S3 | `full__cls_plus_all_groups__abs_plus_subrel_train` | `0.526221` |
| S4 | `only_event__cls__abs_plus_subrel_train` | `0.643818` |

Decision:

- This is the first positive result from the new data structure beyond parity with the stacked Transformer branch.
- The user's subject-relative deviation hypothesis is supported: relative-only fusion improves OOF and cuts drift by about 25% versus the best channel-patch CLS baseline.
- The best curated model uses a mix of absolute and relative latents, meaning absolute state is not useless, but subject-relative coordinates are the main drift-control mechanism.
- Next step: make subject-relative centering fold-safe inside the decoder rather than precomputing one train-subject mean for all OOF rows, then test a compact nonlinear fusion head over the selected modality experts.
