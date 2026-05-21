# Hourly Transformer Encoder - only_cross_modal

## Representation

- Days: `700`
- Token shape: `48 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.371983`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a20_w0p35 | 0.625886 | 0.675265 | 0.696486 | 0.679730 | 0.578586 | 0.576860 | 0.534900 | 0.639378 |
| transformer_ridge_resid_a5_w0p35 | 0.626062 | 0.675822 | 0.696054 | 0.680284 | 0.579295 | 0.576447 | 0.535382 | 0.639152 |
| transformer_logreg_c0p3_w0p2 | 0.626161 | 0.672174 | 0.691193 | 0.675152 | 0.580547 | 0.578535 | 0.540807 | 0.644721 |
| transformer_logreg_c0p3_w0p1 | 0.626270 | 0.672233 | 0.697267 | 0.676180 | 0.577484 | 0.578398 | 0.537064 | 0.645263 |
| transformer_ridge_resid_a20_w0p2 | 0.626339 | 0.674239 | 0.699362 | 0.678799 | 0.577231 | 0.577809 | 0.534622 | 0.642309 |
| transformer_ridge_resid_a5_w0p2 | 0.626353 | 0.674487 | 0.698944 | 0.679096 | 0.577555 | 0.577427 | 0.534858 | 0.642104 |
| transformer_logreg_c0p1_w0p1 | 0.626462 | 0.672292 | 0.697864 | 0.676032 | 0.577253 | 0.579034 | 0.537153 | 0.645607 |
| transformer_logreg_c0p1_w0p2 | 0.626491 | 0.672274 | 0.692249 | 0.674855 | 0.580035 | 0.579697 | 0.541016 | 0.645314 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622084`
- Drift vs reference: `0.069124`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.672174 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.684685 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673396 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a5_w0p35 | 0.576447 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a5_w0p35 | 0.639152 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.