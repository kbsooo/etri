# Hourly Transformer Encoder - no_sleep

## Representation

- Encoder type: `gru`
- Encoder params: `3175`
- Days: `700`
- Token shape: `48 x 335`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.489073`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p35 | 0.627277 | 0.673777 | 0.703008 | 0.677444 | 0.575581 | 0.580456 | 0.534871 | 0.645805 |
| transformer_ridge_resid_a1_w0p2 | 0.627289 | 0.673375 | 0.703555 | 0.677484 | 0.575515 | 0.580169 | 0.534734 | 0.646188 |
| transformer_ridge_resid_a5_w0p35 | 0.627289 | 0.673763 | 0.703043 | 0.677474 | 0.575579 | 0.580435 | 0.534881 | 0.645851 |
| transformer_ridge_resid_a5_w0p2 | 0.627302 | 0.673372 | 0.703586 | 0.677508 | 0.575516 | 0.580158 | 0.534747 | 0.646229 |
| transformer_logreg_c0p3_w0p1 | 0.627321 | 0.672029 | 0.700133 | 0.675537 | 0.576575 | 0.581062 | 0.538573 | 0.647337 |
| transformer_logreg_c0p3_w0p05 | 0.627328 | 0.672482 | 0.702426 | 0.676580 | 0.575961 | 0.580234 | 0.536463 | 0.647155 |
| transformer_ridge_resid_a20_w0p35 | 0.627332 | 0.673721 | 0.703162 | 0.677571 | 0.575571 | 0.580371 | 0.534917 | 0.646007 |
| transformer_ridge_resid_a20_w0p2 | 0.627346 | 0.673363 | 0.703686 | 0.677583 | 0.575518 | 0.580125 | 0.534787 | 0.646357 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624396`
- Drift vs reference: `0.067513`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.671797 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.692481 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.672289 |
| S1 | transformer_ridge_resid_a1_w0p2 | 0.575515 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.645805 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.