# Hourly Transformer Encoder - no_sleep

## Representation

- Encoder type: `transformer`
- Encoder params: `6791`
- Days: `700`
- Token shape: `12 x 335`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.301952`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p35 | 0.626709 | 0.676247 | 0.696637 | 0.678924 | 0.580648 | 0.575985 | 0.536158 | 0.642361 |
| transformer_ridge_resid_a1_w0p2 | 0.626734 | 0.674612 | 0.699207 | 0.678132 | 0.578357 | 0.577294 | 0.535454 | 0.644084 |
| transformer_ridge_resid_a5_w0p2 | 0.627047 | 0.674220 | 0.701401 | 0.678022 | 0.578195 | 0.578013 | 0.535422 | 0.644052 |
| transformer_ridge_resid_a1_w0p1 | 0.627078 | 0.673793 | 0.701838 | 0.677857 | 0.576977 | 0.578454 | 0.535082 | 0.645543 |
| transformer_logreg_c0p3_w0p1 | 0.627119 | 0.672263 | 0.699828 | 0.675568 | 0.577566 | 0.579972 | 0.538290 | 0.646346 |
| transformer_ridge_resid_a5_w0p35 | 0.627139 | 0.675408 | 0.700365 | 0.678523 | 0.580303 | 0.577078 | 0.536063 | 0.642230 |
| transformer_logreg_c0p1_w0p1 | 0.627199 | 0.672090 | 0.700192 | 0.675621 | 0.577529 | 0.580122 | 0.538378 | 0.646458 |
| transformer_logreg_c0p3_w0p05 | 0.627209 | 0.672588 | 0.702258 | 0.676601 | 0.576450 | 0.579636 | 0.536309 | 0.646624 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623265`
- Drift vs reference: `0.067282`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671655 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.691959 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.672289 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.575985 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a5_w0p35 | 0.642230 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.