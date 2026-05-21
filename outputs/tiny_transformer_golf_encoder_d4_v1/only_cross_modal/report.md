# Hourly Transformer Encoder - only_cross_modal

## Representation

- Days: `700`
- Token shape: `48 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.414070`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626997 | 0.672063 | 0.699732 | 0.675897 | 0.576832 | 0.579623 | 0.538363 | 0.646467 |
| transformer_logreg_c0p1_w0p1 | 0.627025 | 0.672073 | 0.699844 | 0.675833 | 0.576742 | 0.579731 | 0.538463 | 0.646491 |
| transformer_ridge_resid_a20_w0p35 | 0.627071 | 0.673054 | 0.701750 | 0.679648 | 0.577622 | 0.577494 | 0.536696 | 0.643231 |
| transformer_logreg_c0p03_w0p1 | 0.627081 | 0.672087 | 0.700035 | 0.675697 | 0.576585 | 0.579969 | 0.538622 | 0.646569 |
| transformer_ridge_resid_a1_w0p2 | 0.627088 | 0.672783 | 0.702542 | 0.678838 | 0.576859 | 0.578344 | 0.535564 | 0.644687 |
| transformer_ridge_resid_a5_w0p2 | 0.627089 | 0.672791 | 0.702574 | 0.678818 | 0.576825 | 0.578351 | 0.535553 | 0.644711 |
| transformer_ridge_resid_a20_w0p2 | 0.627094 | 0.672820 | 0.702682 | 0.678751 | 0.576715 | 0.578380 | 0.535517 | 0.644791 |
| transformer_ridge_resid_a5_w0p35 | 0.627128 | 0.673051 | 0.701752 | 0.679777 | 0.577831 | 0.577474 | 0.536899 | 0.643112 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623719`
- Drift vs reference: `0.065768`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.672022 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.691812 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.672919 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.577470 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.643077 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.