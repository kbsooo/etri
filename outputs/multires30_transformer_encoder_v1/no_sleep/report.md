# Hourly Transformer Encoder - no_sleep

## Representation

- Days: `700`
- Token shape: `48 x 191`
- Base hourly features selected: `46`
- Mean token missing fraction: `0.150518`
- Device: `mps`
- SSL final loss: `0.349807`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a5_w0p2 | 0.623839 | 0.670529 | 0.682528 | 0.679074 | 0.579404 | 0.580921 | 0.527207 | 0.647211 |
| transformer_ridge_resid_a20_w0p2 | 0.624070 | 0.671623 | 0.685667 | 0.679380 | 0.578319 | 0.579675 | 0.526103 | 0.647723 |
| transformer_logreg_c0p3_w0p2 | 0.624306 | 0.671924 | 0.677226 | 0.678774 | 0.582667 | 0.581123 | 0.526572 | 0.651857 |
| transformer_ridge_resid_a1_w0p2 | 0.624472 | 0.669906 | 0.681532 | 0.678685 | 0.579840 | 0.583584 | 0.529836 | 0.647920 |
| transformer_ridge_resid_a20_w0p35 | 0.624604 | 0.672965 | 0.676173 | 0.683249 | 0.583101 | 0.583615 | 0.522255 | 0.650871 |
| transformer_logreg_c0p3_w0p1 | 0.624890 | 0.671621 | 0.689788 | 0.677472 | 0.578320 | 0.579028 | 0.529399 | 0.648603 |
| transformer_logreg_c0p1_w0p2 | 0.624920 | 0.672739 | 0.680992 | 0.678866 | 0.580930 | 0.580647 | 0.528256 | 0.652008 |
| transformer_ridge_resid_a1_w0p1 | 0.624928 | 0.670499 | 0.691581 | 0.677210 | 0.576533 | 0.580728 | 0.531312 | 0.646630 |

## Target-Wise Selection

- Target-wise avg logloss: `0.618590`
- Drift vs reference: `0.077763`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_ridge_resid_a1_w0p2 | 0.669906 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.662907 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_logreg_c0p1_w0p1 | 0.578962 |
| S3 | transformer_ridge_resid_a20_w0p35 | 0.522255 |
| S4 | transformer_ridge_resid_a5_w0p1 | 0.646574 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.