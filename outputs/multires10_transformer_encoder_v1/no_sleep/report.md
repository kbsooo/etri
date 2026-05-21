# Hourly Transformer Encoder - no_sleep

## Representation

- Days: `700`
- Token shape: `144 x 191`
- Base hourly features selected: `46`
- Mean token missing fraction: `0.189667`
- Device: `mps`
- SSL final loss: `0.323767`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p1 | 0.626483 | 0.673743 | 0.693714 | 0.678376 | 0.577015 | 0.580134 | 0.532405 | 0.649994 |
| transformer_logreg_c0p3_w0p1 | 0.626552 | 0.674020 | 0.693252 | 0.678571 | 0.577141 | 0.580501 | 0.532112 | 0.650266 |
| transformer_logreg_c0p03_w0p1 | 0.626582 | 0.673414 | 0.695032 | 0.678108 | 0.576705 | 0.579946 | 0.533418 | 0.649450 |
| transformer_logreg_c0p1_w0p05 | 0.626821 | 0.673259 | 0.699079 | 0.677925 | 0.576150 | 0.579626 | 0.533276 | 0.648436 |
| transformer_logreg_c0p3_w0p05 | 0.626827 | 0.673370 | 0.698799 | 0.677987 | 0.576186 | 0.579800 | 0.533106 | 0.648542 |
| transformer_logreg_c0p03_w0p05 | 0.626902 | 0.673119 | 0.699796 | 0.677824 | 0.576020 | 0.579552 | 0.533818 | 0.648187 |
| transformer_logreg_c0p03_w0p2 | 0.627065 | 0.674981 | 0.686745 | 0.679354 | 0.579113 | 0.582366 | 0.533944 | 0.652955 |
| transformer_logreg_c0p1_w0p2 | 0.627109 | 0.675843 | 0.684547 | 0.680150 | 0.579925 | 0.582921 | 0.532150 | 0.654227 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622058`
- Drift vs reference: `0.077234`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.674271 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a20_w0p05 | 0.575571 |
| S2 | transformer_logreg_c0p03_w0p05 | 0.579552 |
| S3 | transformer_logreg_c0p3_w0p2 | 0.531740 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.