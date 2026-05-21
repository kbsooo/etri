# Channel-Independent Patch Transformer Encoder v1

## Goal

Test the SOTA-style data structure for heterogeneous lifelog sequences: value/mask tensor pairs, channel-independent patch encoding, and static context injected into the day CLS token.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise | channels |
| --- | --- | --- | --- | --- | --- | --- |
| full | 0.628591 | 0.623066 | 0.619152 | 0.089453 | 0.086491 | 110 |
| no_sleep | 0.615370 | 0.623808 | 0.620952 | 0.082931 | 0.087176 | 87 |
| only_event | 0.513430 | 0.625007 | 0.621840 | 0.085678 | 0.075592 | 45 |

## Best Candidate

- Best view: `full`
- OOF avg logloss: `0.619152`
- Drift vs v83 reference: `0.086491`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.672077 |
| Q2 | 0.675145 |
| Q3 | 0.667583 |
| S1 | 0.567879 |
| S2 | 0.572732 |
| S3 | 0.531378 |
| S4 | 0.647272 |

## Decision

This branch replaces time-wise stacked tokens with channel-independent patch tokens. It is a representation test; adoption depends on whether the latent is more label-readable and less drift-prone than the previous `[B,T,F]` Transformer branch.