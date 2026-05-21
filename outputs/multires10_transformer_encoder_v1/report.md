# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| only_cross_modal | 0.203389 | 0.624650 | 0.621938 | 0.078776 | 0.074023 |
| no_sleep | 0.323767 | 0.626483 | 0.622058 | 0.069763 | 0.077234 |
| only_rhythm | 0.313242 | 0.627354 | 0.623055 | 0.063534 | 0.069591 |
| full | 0.331980 | 0.627318 | 0.624279 | 0.064093 | 0.067753 |

## Best Candidate

- Best view: `only_cross_modal`
- OOF avg logloss: `0.621938`
- Drift vs reference: `0.074023`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.669456 |
| Q2 | 0.684676 |
| Q3 | 0.673823 |
| S1 | 0.574907 |
| S2 | 0.575695 |
| S3 | 0.530039 |
| S4 | 0.644971 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.