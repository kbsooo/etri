# Hourly Transformer Encoder - no_sleep

## Representation

- Days: `700`
- Token shape: `24 x 65`
- Base hourly features selected: `29`
- Mean token missing fraction: `0.083785`
- Device: `mps`
- SSL final loss: `0.257547`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p2 | 0.625144 | 0.670239 | 0.681318 | 0.673412 | 0.578301 | 0.586890 | 0.534490 | 0.651355 |
| transformer_logreg_c0p1_w0p2 | 0.625275 | 0.669866 | 0.683568 | 0.674530 | 0.576771 | 0.586057 | 0.534925 | 0.651206 |
| transformer_logreg_c0p3_w0p1 | 0.625394 | 0.670683 | 0.691919 | 0.674923 | 0.576089 | 0.582420 | 0.533480 | 0.648244 |
| transformer_ridge_resid_a20_w0p2 | 0.625603 | 0.671962 | 0.688402 | 0.676793 | 0.576534 | 0.586569 | 0.531848 | 0.647111 |
| transformer_logreg_c0p1_w0p1 | 0.625604 | 0.670651 | 0.693236 | 0.675637 | 0.575384 | 0.582119 | 0.533837 | 0.648366 |
| transformer_ridge_resid_a5_w0p2 | 0.625756 | 0.671660 | 0.686101 | 0.675797 | 0.577564 | 0.588242 | 0.533407 | 0.647519 |
| transformer_ridge_resid_a5_w0p1 | 0.625878 | 0.671556 | 0.694536 | 0.676147 | 0.576009 | 0.583240 | 0.533035 | 0.646622 |
| transformer_logreg_c0p03_w0p2 | 0.625883 | 0.669511 | 0.686416 | 0.675479 | 0.576112 | 0.585478 | 0.536487 | 0.651700 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620859`
- Drift vs reference: `0.070577`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.669511 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.669603 |
| Q3 | transformer_logreg_c0p3_w0p2 | 0.673412 |
| S1 | transformer_logreg_c0p03_w0p1 | 0.575158 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | transformer_ridge_resid_a20_w0p2 | 0.531848 |
| S4 | transformer_ridge_resid_a5_w0p1 | 0.646622 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.