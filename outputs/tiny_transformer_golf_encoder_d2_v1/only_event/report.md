# Hourly Transformer Encoder - only_event

## Representation

- Days: `700`
- Token shape: `48 x 187`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.843268`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627335 | 0.672487 | 0.702504 | 0.676516 | 0.575898 | 0.580107 | 0.536690 | 0.647145 |
| transformer_logreg_c0p1_w0p05 | 0.627336 | 0.672488 | 0.702459 | 0.676534 | 0.575904 | 0.580112 | 0.536713 | 0.647139 |
| transformer_logreg_c0p3_w0p05 | 0.627336 | 0.672488 | 0.702444 | 0.676540 | 0.575905 | 0.580114 | 0.536721 | 0.647137 |
| transformer_logreg_c0p03_w0p1 | 0.627339 | 0.672055 | 0.700235 | 0.675405 | 0.576417 | 0.580866 | 0.539106 | 0.647292 |
| transformer_logreg_c0p1_w0p1 | 0.627342 | 0.672058 | 0.700149 | 0.675442 | 0.576426 | 0.580881 | 0.539157 | 0.647281 |
| transformer_logreg_c0p3_w0p1 | 0.627343 | 0.672059 | 0.700120 | 0.675454 | 0.576429 | 0.580887 | 0.539175 | 0.647278 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627663 | 0.673155 | 0.704760 | 0.677849 | 0.575764 | 0.579903 | 0.534902 | 0.647312 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624469`
- Drift vs reference: `0.065971`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671891 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.691768 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.671898 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_logreg_c0p3_w0p05 | 0.647137 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.