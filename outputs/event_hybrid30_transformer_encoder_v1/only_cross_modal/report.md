# Hourly Transformer Encoder - only_cross_modal

## Representation

- Days: `700`
- Token shape: `48 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.214551`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626520 | 0.672142 | 0.698699 | 0.677908 | 0.576689 | 0.578244 | 0.532256 | 0.649702 |
| transformer_logreg_c0p1_w0p1 | 0.626659 | 0.672092 | 0.698700 | 0.677932 | 0.576720 | 0.578706 | 0.532763 | 0.649704 |
| transformer_logreg_c0p3_w0p05 | 0.626819 | 0.672427 | 0.701554 | 0.677662 | 0.575938 | 0.578744 | 0.533168 | 0.648244 |
| transformer_logreg_c0p1_w0p05 | 0.626931 | 0.672440 | 0.701581 | 0.677707 | 0.575999 | 0.579021 | 0.533481 | 0.648289 |
| transformer_logreg_c0p03_w0p1 | 0.626952 | 0.672295 | 0.699116 | 0.677886 | 0.576656 | 0.579441 | 0.533698 | 0.649571 |
| transformer_logreg_c0p03_w0p05 | 0.627114 | 0.672576 | 0.701825 | 0.677713 | 0.576005 | 0.579423 | 0.534000 | 0.648253 |
| transformer_logreg_c0p1_w0p2 | 0.627322 | 0.672504 | 0.694474 | 0.679214 | 0.579322 | 0.579370 | 0.532734 | 0.653636 |
| transformer_logreg_c0p3_w0p2 | 0.627347 | 0.672901 | 0.694687 | 0.679426 | 0.579583 | 0.578771 | 0.532106 | 0.653958 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623696`
- Drift vs reference: `0.071779`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p1_w0p1 | 0.672092 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.691752 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a1_w0p05 | 0.575646 |
| S2 | transformer_logreg_c0p3_w0p1 | 0.578244 |
| S3 | transformer_ridge_resid_a20_w0p35 | 0.527047 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.