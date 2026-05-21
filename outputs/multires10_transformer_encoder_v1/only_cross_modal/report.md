# Hourly Transformer Encoder - only_cross_modal

## Representation

- Days: `700`
- Token shape: `144 x 79`
- Base hourly features selected: `18`
- Mean token missing fraction: `0.099351`
- Device: `mps`
- SSL final loss: `0.203389`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p2 | 0.624650 | 0.670014 | 0.690539 | 0.677022 | 0.576188 | 0.575695 | 0.534676 | 0.648413 |
| transformer_logreg_c0p03_w0p2 | 0.624893 | 0.669456 | 0.691339 | 0.676927 | 0.575883 | 0.576435 | 0.536082 | 0.648130 |
| transformer_logreg_c0p3_w0p2 | 0.624976 | 0.670871 | 0.690645 | 0.676982 | 0.576783 | 0.576495 | 0.533784 | 0.649273 |
| transformer_ridge_resid_a20_w0p2 | 0.625325 | 0.672897 | 0.695606 | 0.680328 | 0.574907 | 0.577353 | 0.531213 | 0.644971 |
| transformer_logreg_c0p1_w0p1 | 0.625356 | 0.670894 | 0.696752 | 0.676870 | 0.575239 | 0.576862 | 0.533860 | 0.647017 |
| transformer_logreg_c0p3_w0p1 | 0.625438 | 0.671247 | 0.696722 | 0.676728 | 0.575469 | 0.577209 | 0.533336 | 0.647356 |
| transformer_logreg_c0p03_w0p1 | 0.625555 | 0.670689 | 0.697277 | 0.676919 | 0.575113 | 0.577253 | 0.534651 | 0.646986 |
| transformer_ridge_resid_a20_w0p1 | 0.626044 | 0.672604 | 0.699709 | 0.678584 | 0.574940 | 0.577978 | 0.532735 | 0.645758 |

## Target-Wise Selection

- Target-wise avg logloss: `0.621938`
- Drift vs reference: `0.074023`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.669456 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.684676 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a20_w0p2 | 0.574907 |
| S2 | transformer_logreg_c0p1_w0p2 | 0.575695 |
| S3 | transformer_ridge_resid_a20_w0p35 | 0.530039 |
| S4 | transformer_ridge_resid_a20_w0p2 | 0.644971 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.