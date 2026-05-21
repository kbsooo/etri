# Hourly Transformer Encoder - only_cross_modal

## Representation

- Days: `700`
- Token shape: `48 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.656102`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627372 | 0.672644 | 0.702837 | 0.676578 | 0.575847 | 0.579985 | 0.536579 | 0.647136 |
| transformer_logreg_c0p1_w0p05 | 0.627376 | 0.672656 | 0.702831 | 0.676607 | 0.575845 | 0.579970 | 0.536591 | 0.647134 |
| transformer_logreg_c0p3_w0p05 | 0.627379 | 0.672662 | 0.702832 | 0.676633 | 0.575844 | 0.579956 | 0.536593 | 0.647135 |
| transformer_logreg_c0p03_w0p1 | 0.627409 | 0.672384 | 0.700905 | 0.675533 | 0.576337 | 0.580592 | 0.538840 | 0.647276 |
| transformer_logreg_c0p1_w0p1 | 0.627418 | 0.672412 | 0.700893 | 0.675592 | 0.576334 | 0.580563 | 0.538862 | 0.647272 |
| transformer_logreg_c0p3_w0p1 | 0.627424 | 0.672424 | 0.700894 | 0.675644 | 0.576332 | 0.580535 | 0.538866 | 0.647275 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627717 | 0.673376 | 0.705045 | 0.678076 | 0.575704 | 0.579677 | 0.534942 | 0.647198 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624729`
- Drift vs reference: `0.064549`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.694354 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.672402 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.575673 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.578666 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.646799 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.