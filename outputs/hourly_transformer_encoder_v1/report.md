# Hourly Transformer Encoder v1

## Goal

Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes 24 hourly tokens, and a Transformer learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise |
| --- | --- | --- | --- | --- | --- |
| no_sleep | 0.257547 | 0.625144 | 0.620859 | 0.078103 | 0.070577 |
| full | 0.283291 | 0.626318 | 0.622449 | 0.067657 | 0.069569 |
| only_core | 0.259294 | 0.626500 | 0.623360 | 0.066951 | 0.066308 |
| no_phone | 0.271903 | 0.626431 | 0.623444 | 0.068386 | 0.067577 |
| no_gps | 0.281721 | 0.627067 | 0.623866 | 0.066284 | 0.066722 |

## Best Candidate

- Best view: `no_sleep`
- OOF avg logloss: `0.620859`
- Drift vs reference: `0.070577`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.669511 |
| Q2 | 0.669603 |
| Q3 | 0.673412 |
| S1 | 0.575158 |
| S2 | 0.579856 |
| S3 | 0.531848 |
| S4 | 0.646622 |

## Decision

This run is an encoder validity test, not a final submission strategy. Adoption requires the Transformer latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.