# Channel-Independent Patch Transformer Encoder v1

## Goal

Test the SOTA-style data structure for heterogeneous lifelog sequences: value/mask tensor pairs, channel-independent patch encoding, and static context injected into the day CLS token.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise | channels |
| --- | --- | --- | --- | --- | --- | --- |
| no_sleep | 0.571212 | 0.623416 | 0.618767 | 0.085055 | 0.100180 | 87 |
| only_event | 0.472596 | 0.620908 | 0.619042 | 0.099625 | 0.096649 | 45 |
| full | 0.577827 | 0.622782 | 0.619794 | 0.094483 | 0.085971 | 110 |
| only_cross_modal | 0.464938 | 0.623727 | 0.620719 | 0.085839 | 0.095392 | 69 |

## Best Candidate

- Best view: `no_sleep`
- OOF avg logloss: `0.618767`
- Drift vs v83 reference: `0.100180`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.672177 |
| Q2 | 0.677586 |
| Q3 | 0.664566 |
| S1 | 0.569332 |
| S2 | 0.569299 |
| S3 | 0.532886 |
| S4 | 0.645522 |

## Decision

This branch replaces time-wise stacked tokens with channel-independent patch tokens. It is a representation test; adoption depends on whether the latent is more label-readable and less drift-prone than the previous `[B,T,F]` Transformer branch.