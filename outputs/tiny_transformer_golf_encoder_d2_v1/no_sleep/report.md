# Hourly Transformer Encoder - no_sleep

## Representation

- Days: `700`
- Token shape: `48 x 335`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.661971`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627359 | 0.672482 | 0.702822 | 0.676346 | 0.575998 | 0.580102 | 0.536600 | 0.647163 |
| transformer_logreg_c0p1_w0p05 | 0.627361 | 0.672474 | 0.702819 | 0.676342 | 0.576015 | 0.580104 | 0.536613 | 0.647162 |
| transformer_logreg_c0p3_w0p05 | 0.627364 | 0.672470 | 0.702825 | 0.676341 | 0.576026 | 0.580102 | 0.536618 | 0.647165 |
| transformer_logreg_c0p03_w0p1 | 0.627382 | 0.672042 | 0.700875 | 0.675070 | 0.576634 | 0.580825 | 0.538905 | 0.647324 |
| transformer_logreg_c0p1_w0p1 | 0.627388 | 0.672028 | 0.700869 | 0.675064 | 0.576669 | 0.580829 | 0.538932 | 0.647323 |
| transformer_logreg_c0p3_w0p1 | 0.627393 | 0.672019 | 0.700882 | 0.675063 | 0.576691 | 0.580824 | 0.538942 | 0.647330 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627679 | 0.673187 | 0.704960 | 0.677726 | 0.575908 | 0.579852 | 0.534861 | 0.647257 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624668`
- Drift vs reference: `0.065036`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.671820 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.694310 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.670802 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a20_w0p2 | 0.579848 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_logreg_c0p1_w0p05 | 0.647162 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.