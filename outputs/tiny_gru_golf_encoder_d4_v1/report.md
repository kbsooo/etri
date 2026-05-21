# Hourly Sequence Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes token sequence, and a tiny sequence encoder learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | encoder_type | encoder_params | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal | gru | 1015 | 0.454964 | 0.626767 | 0.622912 | 0.064311 | 0.067098 |
| only_rhythm | gru | 1339 | 0.670799 | 0.626842 | 0.623478 | 0.064387 | 0.067552 |
| no_sleep | gru | 3175 | 0.489073 | 0.627277 | 0.624396 | 0.065043 | 0.067513 |
| only_event | gru | 1843 | 0.539109 | 0.627367 | 0.624659 | 0.064182 | 0.066635 |

## Best Candidate

- Best view: `only_cross_modal`
- OOF avg logloss: `0.622912`
- Drift vs reference: `0.067098`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.671714 |
| Q2 | 0.689071 |
| Q3 | 0.673136 |
| S1 | 0.575702 |
| S2 | 0.577956 |
| S3 | 0.533031 |
| S4 | 0.639772 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the sequence latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.