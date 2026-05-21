# Hourly Sequence Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes token sequence, and a tiny sequence encoder learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | encoder_type | encoder_params | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- | --- | --- |
| no_sleep | gru | 1727 | 0.671745 | 0.627347 | 0.624398 | 0.064062 | 0.066493 |
| only_rhythm | gru | 707 | 1.063691 | 0.627394 | 0.624599 | 0.063739 | 0.065120 |
| only_cross_modal | gru | 527 | 0.952805 | 0.627362 | 0.624756 | 0.063729 | 0.064587 |
| only_event | gru | 987 | 0.851184 | 0.627403 | 0.624953 | 0.063783 | 0.064774 |

## Best Candidate

- Best view: `no_sleep`
- OOF avg logloss: `0.624398`
- Drift vs reference: `0.066493`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.671481 |
| Q2 | 0.694122 |
| Q3 | 0.671158 |
| S1 | 0.575375 |
| S2 | 0.579698 |
| S3 | 0.533031 |
| S4 | 0.645922 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the sequence latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.