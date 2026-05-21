# Hourly Transformer Encoder - no_sleep

## Representation

- Encoder type: `transformer`
- Encoder params: `3283`
- Days: `700`
- Token shape: `24 x 123`
- Base hourly features selected: `29`
- Mean token missing fraction: `0.083785`
- Device: `mps`
- SSL final loss: `0.579238`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.627245 | 0.672144 | 0.698148 | 0.676017 | 0.576519 | 0.580957 | 0.538755 | 0.648176 |
| transformer_logreg_c0p3_w0p05 | 0.627286 | 0.672541 | 0.701429 | 0.676819 | 0.575930 | 0.580179 | 0.536517 | 0.647590 |
| transformer_logreg_c0p1_w0p05 | 0.627369 | 0.672605 | 0.701751 | 0.676787 | 0.575894 | 0.580198 | 0.536756 | 0.647593 |
| transformer_logreg_c0p1_w0p1 | 0.627395 | 0.672258 | 0.698759 | 0.675946 | 0.576434 | 0.580997 | 0.539195 | 0.648175 |
| transformer_logreg_c0p03_w0p05 | 0.627447 | 0.672671 | 0.702252 | 0.676729 | 0.575825 | 0.580225 | 0.536877 | 0.647553 |
| transformer_logreg_c0p03_w0p1 | 0.627542 | 0.672387 | 0.699736 | 0.675825 | 0.576289 | 0.581052 | 0.539420 | 0.648089 |
| transformer_ridge_resid_a1_w0p1 | 0.627582 | 0.673320 | 0.703580 | 0.678212 | 0.575860 | 0.580513 | 0.533712 | 0.647880 |
| transformer_ridge_resid_a1_w0p05 | 0.627593 | 0.673228 | 0.704246 | 0.677973 | 0.575757 | 0.580163 | 0.534224 | 0.647561 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623672`
- Drift vs reference: `0.069017`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.672008 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.685810 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673252 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | transformer_ridge_resid_a1_w0p35 | 0.531802 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.