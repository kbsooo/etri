# Hourly Transformer Encoder - only_event

## Representation

- Days: `700`
- Token shape: `48 x 187`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.532398`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p2 | 0.627281 | 0.673895 | 0.702668 | 0.678784 | 0.575619 | 0.578139 | 0.535010 | 0.646855 |
| transformer_ridge_resid_a5_w0p2 | 0.627302 | 0.673789 | 0.702777 | 0.678789 | 0.575741 | 0.578216 | 0.534979 | 0.646821 |
| transformer_logreg_c0p3_w0p05 | 0.627303 | 0.672474 | 0.701988 | 0.676813 | 0.576330 | 0.579798 | 0.536450 | 0.647269 |
| transformer_logreg_c0p3_w0p1 | 0.627317 | 0.672026 | 0.699309 | 0.676000 | 0.577332 | 0.580326 | 0.538655 | 0.647569 |
| transformer_logreg_c0p1_w0p05 | 0.627320 | 0.672445 | 0.702071 | 0.676791 | 0.576363 | 0.579889 | 0.536457 | 0.647226 |
| transformer_logreg_c0p1_w0p1 | 0.627339 | 0.671961 | 0.699460 | 0.675955 | 0.577390 | 0.580475 | 0.538656 | 0.647472 |
| transformer_logreg_c0p03_w0p05 | 0.627348 | 0.672445 | 0.702254 | 0.676734 | 0.576316 | 0.579975 | 0.536501 | 0.647211 |
| transformer_ridge_resid_a20_w0p2 | 0.627364 | 0.673541 | 0.703079 | 0.678792 | 0.576025 | 0.578420 | 0.534915 | 0.646777 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623975`
- Drift vs reference: `0.066796`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671640 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.690246 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673376 |
| S1 | transformer_ridge_resid_a1_w0p1 | 0.575608 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.577238 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a20_w0p35 | 0.646687 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.