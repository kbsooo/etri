# Hourly Sequence Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes token sequence, and a tiny sequence encoder learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | encoder_type | encoder_params | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal | transformer | 2711 | 0.243696 | 0.625355 | 0.622174 | 0.069761 | 0.070366 |
| no_sleep | transformer | 6791 | 0.301952 | 0.626709 | 0.623265 | 0.066544 | 0.067282 |
| only_event | transformer | 4275 | 0.305107 | 0.627164 | 0.623620 | 0.063164 | 0.068051 |
| only_rhythm | transformer | 3323 | 0.319734 | 0.627521 | 0.624716 | 0.063734 | 0.064603 |

## Best Candidate

- Best view: `only_cross_modal`
- OOF avg logloss: `0.622174`
- Drift vs reference: `0.070366`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.672177 |
| Q2 | 0.687613 |
| Q3 | 0.673289 |
| S1 | 0.575702 |
| S2 | 0.575968 |
| S3 | 0.532715 |
| S4 | 0.637752 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the sequence latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.