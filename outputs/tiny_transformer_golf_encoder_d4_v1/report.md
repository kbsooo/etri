# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| only_cross_modal | 0.414070 | 0.626997 | 0.623719 | 0.066281 | 0.065768 |
| only_event | 0.532398 | 0.627281 | 0.623975 | 0.063161 | 0.066796 |
| no_sleep | 0.539526 | 0.627269 | 0.624593 | 0.066239 | 0.067168 |
| only_rhythm | 0.601936 | 0.627482 | 0.624872 | 0.063732 | 0.065461 |

## Best Candidate

- Best view: `only_cross_modal`
- OOF avg logloss: `0.623719`
- Drift vs reference: `0.065768`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.672022 |
| Q2 | 0.691812 |
| Q3 | 0.672919 |
| S1 | 0.575702 |
| S2 | 0.577470 |
| S3 | 0.533031 |
| S4 | 0.643077 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.