# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| only_event | 0.843268 | 0.627335 | 0.624469 | 0.063777 | 0.065971 |
| only_rhythm | 0.625616 | 0.627310 | 0.624559 | 0.065891 | 0.065134 |
| no_sleep | 0.661971 | 0.627359 | 0.624668 | 0.063714 | 0.065036 |
| only_cross_modal | 0.656102 | 0.627372 | 0.624729 | 0.063726 | 0.064549 |

## Best Candidate

- Best view: `only_event`
- OOF avg logloss: `0.624469`
- Drift vs reference: `0.065971`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.671891 |
| Q2 | 0.691768 |
| Q3 | 0.671898 |
| S1 | 0.575702 |
| S2 | 0.579856 |
| S3 | 0.533031 |
| S4 | 0.647137 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.