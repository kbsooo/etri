# Hourly Transformer Encoder - no_gps

## Representation

- Days: `700`
- Token shape: `24 x 101`
- Base hourly features selected: `47`
- Mean token missing fraction: `0.200032`
- Device: `mps`
- SSL final loss: `0.281721`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p1 | 0.627067 | 0.670871 | 0.698890 | 0.676422 | 0.575224 | 0.582216 | 0.536516 | 0.649329 |
| transformer_logreg_c0p3_w0p1 | 0.627069 | 0.670156 | 0.700443 | 0.676763 | 0.575913 | 0.581428 | 0.537079 | 0.647700 |
| transformer_logreg_c0p1_w0p1 | 0.627081 | 0.670382 | 0.699574 | 0.676611 | 0.575371 | 0.581963 | 0.536907 | 0.648756 |
| transformer_logreg_c0p3_w0p05 | 0.627081 | 0.671423 | 0.702446 | 0.677086 | 0.575546 | 0.580241 | 0.535617 | 0.647206 |
| transformer_logreg_c0p1_w0p05 | 0.627123 | 0.671566 | 0.702034 | 0.677042 | 0.575304 | 0.580581 | 0.535554 | 0.647782 |
| transformer_ridge_resid_a1_w0p05 | 0.627124 | 0.671266 | 0.705299 | 0.677196 | 0.575522 | 0.579387 | 0.534840 | 0.646361 |
| transformer_ridge_resid_a1_w0p1 | 0.627126 | 0.669901 | 0.706139 | 0.677062 | 0.575849 | 0.579629 | 0.535393 | 0.645909 |
| transformer_logreg_c0p03_w0p05 | 0.627149 | 0.671841 | 0.701724 | 0.676979 | 0.575256 | 0.580761 | 0.535376 | 0.648109 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623866`
- Drift vs reference: `0.066722`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_ridge_resid_a1_w0p2 | 0.668818 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.690871 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_logreg_c0p03_w0p1 | 0.575224 |
| S2 | transformer_ridge_resid_a1_w0p05 | 0.579387 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p1 | 0.645909 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.