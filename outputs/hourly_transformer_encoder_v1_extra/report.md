# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| only_rhythm | 0.270226 | 0.624185 | 0.619825 | 0.070480 | 0.071960 |
| only_cross_modal | 0.216304 | 0.625056 | 0.620680 | 0.070413 | 0.076263 |
| no_missingness | 0.519439 | 0.626219 | 0.622597 | 0.066756 | 0.070938 |

## Best Candidate

- Best view: `only_rhythm`
- OOF avg logloss: `0.619825`
- Drift vs reference: `0.071960`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.668831 |
| Q2 | 0.671803 |
| Q3 | 0.666235 |
| S1 | 0.573140 |
| S2 | 0.578532 |
| S3 | 0.533031 |
| S4 | 0.647202 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.