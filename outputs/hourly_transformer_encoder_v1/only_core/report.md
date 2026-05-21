# Hourly Transformer Encoder - only_core

## Representation

- Days: `700`
- Token shape: `24 x 95`
- Base hourly features selected: `44`
- Mean token missing fraction: `0.200662`
- Device: `mps`
- SSL final loss: `0.259294`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626500 | 0.671867 | 0.696227 | 0.674436 | 0.578892 | 0.582082 | 0.533554 | 0.648443 |
| transformer_logreg_c0p1_w0p1 | 0.626690 | 0.671664 | 0.696854 | 0.675372 | 0.578378 | 0.582323 | 0.533762 | 0.648479 |
| transformer_logreg_c0p03_w0p1 | 0.626769 | 0.671742 | 0.697470 | 0.675796 | 0.577685 | 0.582089 | 0.534063 | 0.648537 |
| transformer_logreg_c0p3_w0p05 | 0.626813 | 0.672285 | 0.700327 | 0.675895 | 0.577091 | 0.580597 | 0.533872 | 0.647624 |
| transformer_ridge_resid_a1_w0p1 | 0.626824 | 0.675328 | 0.698509 | 0.674507 | 0.576715 | 0.580800 | 0.534367 | 0.647544 |
| transformer_ridge_resid_a1_w0p05 | 0.626882 | 0.673796 | 0.701492 | 0.675778 | 0.575952 | 0.579911 | 0.534077 | 0.647170 |
| transformer_logreg_c0p1_w0p05 | 0.626940 | 0.672207 | 0.700676 | 0.676408 | 0.576862 | 0.580772 | 0.533988 | 0.647664 |
| transformer_logreg_c0p03_w0p05 | 0.627005 | 0.672278 | 0.701017 | 0.676658 | 0.576530 | 0.580692 | 0.534144 | 0.647716 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623360`
- Drift vs reference: `0.066308`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p1_w0p1 | 0.671664 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.683420 |
| Q3 | transformer_logreg_c0p3_w0p2 | 0.672697 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a5_w0p05 | 0.647150 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.