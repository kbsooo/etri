# Hourly Sequence Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes token sequence, and a tiny sequence encoder learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | encoder_type | encoder_params | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal | transformer | 4326 | 0.185118 | 0.626912 | 0.622773 | 0.066838 | 0.067951 |
| no_sleep | transformer | 12486 | 0.218091 | 0.626879 | 0.623280 | 0.067093 | 0.069724 |
| only_event | transformer | 7454 | 0.210269 | 0.627091 | 0.623735 | 0.066321 | 0.065921 |
| only_rhythm | transformer | 5550 | 0.264092 | 0.627491 | 0.624916 | 0.063800 | 0.063950 |

## Best Candidate

- Best view: `only_cross_modal`
- OOF avg logloss: `0.622773`
- Drift vs reference: `0.067951`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.670719 |
| Q2 | 0.681888 |
| Q3 | 0.673813 |
| S1 | 0.575702 |
| S2 | 0.579724 |
| S3 | 0.533031 |
| S4 | 0.644532 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the sequence latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.