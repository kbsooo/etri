# Hourly Transformer Encoder - no_sleep

## Representation

- Days: `700`
- Token shape: `48 x 335`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.539526`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p1 | 0.627269 | 0.671914 | 0.701297 | 0.675649 | 0.575847 | 0.580765 | 0.538411 | 0.647001 |
| transformer_logreg_c0p1_w0p1 | 0.627274 | 0.671879 | 0.701149 | 0.675773 | 0.575966 | 0.580656 | 0.538520 | 0.646974 |
| transformer_logreg_c0p3_w0p1 | 0.627288 | 0.671874 | 0.701014 | 0.675872 | 0.576122 | 0.580487 | 0.538676 | 0.646973 |
| transformer_logreg_c0p1_w0p05 | 0.627293 | 0.672393 | 0.702961 | 0.676693 | 0.575644 | 0.580005 | 0.536381 | 0.646974 |
| transformer_logreg_c0p03_w0p05 | 0.627294 | 0.672414 | 0.703038 | 0.676632 | 0.575590 | 0.580065 | 0.536332 | 0.646990 |
| transformer_logreg_c0p3_w0p05 | 0.627297 | 0.672387 | 0.702889 | 0.676741 | 0.575717 | 0.579913 | 0.536457 | 0.646972 |
| transformer_ridge_resid_a1_w0p2 | 0.627498 | 0.673062 | 0.705310 | 0.678792 | 0.576486 | 0.579512 | 0.533212 | 0.646109 |
| transformer_ridge_resid_a1_w0p1 | 0.627529 | 0.673081 | 0.705106 | 0.678250 | 0.576040 | 0.579660 | 0.533917 | 0.646646 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624593`
- Drift vs reference: `0.067168`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p1_w0p2 | 0.671571 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.694897 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.672922 |
| S1 | transformer_logreg_c0p03_w0p05 | 0.575590 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.579378 |
| S3 | transformer_ridge_resid_a1_w0p35 | 0.532432 |
| S4 | transformer_ridge_resid_a20_w0p35 | 0.645362 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.