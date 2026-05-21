# Hourly Transformer Encoder - only_rhythm

## Representation

- Days: `700`
- Token shape: `144 x 99`
- Base hourly features selected: `23`
- Mean token missing fraction: `0.251521`
- Device: `mps`
- SSL final loss: `0.313242`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p05 | 0.627354 | 0.670330 | 0.702124 | 0.677317 | 0.576323 | 0.578902 | 0.536565 | 0.649921 |
| transformer_logreg_c0p3_w0p05 | 0.627381 | 0.670026 | 0.702149 | 0.677591 | 0.576742 | 0.578726 | 0.536273 | 0.650161 |
| transformer_logreg_c0p03_w0p05 | 0.627382 | 0.670785 | 0.702317 | 0.677135 | 0.575969 | 0.579215 | 0.536757 | 0.649493 |
| transformer_ridge_resid_a1_w0p05 | 0.627471 | 0.670424 | 0.705294 | 0.678291 | 0.575547 | 0.578211 | 0.534198 | 0.650332 |
| transformer_ridge_resid_a5_w0p05 | 0.627567 | 0.670605 | 0.704906 | 0.678435 | 0.575941 | 0.578411 | 0.534475 | 0.650198 |
| transformer_logreg_c0p03_w0p1 | 0.627572 | 0.668806 | 0.699986 | 0.676748 | 0.576693 | 0.579359 | 0.539364 | 0.652050 |
| transformer_ridge_resid_a20_w0p05 | 0.627574 | 0.670936 | 0.704612 | 0.678321 | 0.575881 | 0.578618 | 0.534790 | 0.649864 |
| transformer_logreg_c0p1_w0p1 | 0.627595 | 0.667966 | 0.699665 | 0.677175 | 0.577459 | 0.578884 | 0.539050 | 0.652967 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623055`
- Drift vs reference: `0.069591`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p35 | 0.661873 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.693313 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a1_w0p05 | 0.575547 |
| S2 | transformer_ridge_resid_a5_w0p2 | 0.576523 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.