# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| only_cross_modal | 0.371983 | 0.625886 | 0.622084 | 0.067804 | 0.069124 |
| no_sleep | 0.513267 | 0.626481 | 0.623671 | 0.067051 | 0.067414 |
| only_rhythm | 0.538083 | 0.627194 | 0.624341 | 0.066246 | 0.066469 |
| only_event | 0.410200 | 0.627395 | 0.624439 | 0.064227 | 0.066281 |

## Best Candidate

- Best view: `only_cross_modal`
- OOF avg logloss: `0.622084`
- Drift vs reference: `0.069124`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.672174 |
| Q2 | 0.684685 |
| Q3 | 0.673396 |
| S1 | 0.575702 |
| S2 | 0.576447 |
| S3 | 0.533031 |
| S4 | 0.639152 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.