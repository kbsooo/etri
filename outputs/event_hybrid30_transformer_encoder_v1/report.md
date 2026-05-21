# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| no_sleep | 0.314283 | 0.626434 | 0.622582 | 0.067411 | 0.073262 |
| no_event | 0.371269 | 0.626666 | 0.623381 | 0.066888 | 0.069564 |
| full | 0.335143 | 0.626623 | 0.623472 | 0.064517 | 0.069957 |
| only_cross_modal | 0.214551 | 0.626520 | 0.623696 | 0.070239 | 0.071779 |
| only_event | 0.215611 | 0.627393 | 0.623701 | 0.064369 | 0.068245 |

## Best Candidate

- Best view: `no_sleep`
- OOF avg logloss: `0.622582`
- Drift vs reference: `0.073262`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.672177 |
| Q2 | 0.687422 |
| Q3 | 0.673823 |
| S1 | 0.573624 |
| S2 | 0.577338 |
| S3 | 0.526417 |
| S4 | 0.647272 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.