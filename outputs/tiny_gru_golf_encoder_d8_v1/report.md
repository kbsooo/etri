# Hourly Sequence Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes token sequence, and a tiny sequence encoder learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | encoder_type | encoder_params | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- | --- | --- |
| no_sleep | gru | 6239 | 0.451946 | 0.627233 | 0.623662 | 0.066297 | 0.066908 |
| only_cross_modal | gru | 2159 | 0.376127 | 0.627059 | 0.624042 | 0.066650 | 0.066484 |
| only_rhythm | gru | 2771 | 0.578894 | 0.627249 | 0.624076 | 0.066424 | 0.066067 |
| only_event | gru | 3723 | 0.371961 | 0.627336 | 0.624594 | 0.064041 | 0.067183 |

## Best Candidate

- Best view: `no_sleep`
- OOF avg logloss: `0.623662`
- Drift vs reference: `0.066908`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.671419 |
| Q2 | 0.688251 |
| Q3 | 0.673823 |
| S1 | 0.575662 |
| S2 | 0.577338 |
| S3 | 0.533031 |
| S4 | 0.646112 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the sequence latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.