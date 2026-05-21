# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| no_sleep | 0.349807 | 0.623839 | 0.618590 | 0.074093 | 0.077763 |
| only_cross_modal | 0.224222 | 0.624121 | 0.620658 | 0.079576 | 0.079591 |
| only_rhythm | 0.377078 | 0.627214 | 0.622599 | 0.063744 | 0.068967 |
| full | 0.371269 | 0.626666 | 0.623381 | 0.066888 | 0.069564 |

## Best Candidate

- Best view: `no_sleep`
- OOF avg logloss: `0.618590`
- Drift vs reference: `0.077763`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.669906 |
| Q2 | 0.662907 |
| Q3 | 0.673823 |
| S1 | 0.575702 |
| S2 | 0.578962 |
| S3 | 0.522255 |
| S4 | 0.646574 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.