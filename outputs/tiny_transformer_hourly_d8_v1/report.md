# Hourly Sequence Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes token sequence, and a tiny sequence encoder learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | encoder_type | encoder_params | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- | --- | --- |
| only_rhythm | transformer | 2875 | 0.685259 | 0.626964 | 0.623310 | 0.066125 | 0.067350 |
| only_cross_modal | transformer | 2807 | 0.545127 | 0.626985 | 0.623493 | 0.063760 | 0.066589 |
| no_sleep | transformer | 3283 | 0.579238 | 0.627245 | 0.623672 | 0.066481 | 0.069017 |
| full | transformer | 4847 | 0.634570 | 0.626964 | 0.624104 | 0.066095 | 0.066923 |

## Best Candidate

- Best view: `only_rhythm`
- OOF avg logloss: `0.623310`
- Drift vs reference: `0.067350`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.671667 |
| Q2 | 0.691443 |
| Q3 | 0.671298 |
| S1 | 0.575225 |
| S2 | 0.577115 |
| S3 | 0.533031 |
| S4 | 0.643391 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the sequence latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.