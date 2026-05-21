# Channel-Independent Patch Transformer Encoder v1

## Goal

Test the SOTA-style data structure for heterogeneous lifelog sequences: value/mask tensor pairs, channel-independent patch encoding, and static context injected into the day CLS token.

## View Comparison

| view | ssl_loss | best_global | targetwise | drift_global | drift_targetwise | channels |
| --- | --- | --- | --- | --- | --- | --- |
| no_sleep | 0.544799 | 0.622732 | 0.619763 | 0.100101 | 0.095294 | 87 |
| only_event | 0.418007 | 0.622922 | 0.620124 | 0.113700 | 0.092020 | 45 |
| full | 0.548379 | 0.623211 | 0.620647 | 0.083987 | 0.088246 | 110 |

## Best Candidate

- Best view: `no_sleep`
- OOF avg logloss: `0.619763`
- Drift vs v83 reference: `0.095294`

## Target Loss

| target | loss |
| --- | --- |
| Q1 | 0.672177 |
| Q2 | 0.678317 |
| Q3 | 0.664687 |
| S1 | 0.567533 |
| S2 | 0.576432 |
| S3 | 0.532307 |
| S4 | 0.646889 |

## Decision

This branch replaces time-wise stacked tokens with channel-independent patch tokens. It is a representation test; adoption depends on whether the latent is more label-readable and less drift-prone than the previous `[B,T,F]` Transformer branch.