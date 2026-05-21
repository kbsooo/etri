# Hourly Transformer Encoder - no_sleep

## Representation

- Encoder type: `gru`
- Encoder params: `6239`
- Days: `700`
- Token shape: `48 x 335`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.451946`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p1 | 0.627233 | 0.672033 | 0.698783 | 0.676406 | 0.577041 | 0.580510 | 0.538351 | 0.647504 |
| transformer_logreg_c0p03_w0p1 | 0.627235 | 0.671850 | 0.699024 | 0.676040 | 0.576757 | 0.580684 | 0.538551 | 0.647738 |
| transformer_logreg_c0p1_w0p05 | 0.627268 | 0.672484 | 0.701735 | 0.677014 | 0.576169 | 0.579924 | 0.536329 | 0.647225 |
| transformer_logreg_c0p3_w0p1 | 0.627277 | 0.672193 | 0.698780 | 0.676662 | 0.577264 | 0.580423 | 0.538236 | 0.647381 |
| transformer_logreg_c0p03_w0p05 | 0.627278 | 0.672395 | 0.701868 | 0.676833 | 0.576034 | 0.580021 | 0.536436 | 0.647356 |
| transformer_logreg_c0p3_w0p05 | 0.627285 | 0.672562 | 0.701726 | 0.677139 | 0.576276 | 0.579873 | 0.536263 | 0.647155 |
| transformer_ridge_resid_a20_w0p2 | 0.627296 | 0.674276 | 0.702059 | 0.680118 | 0.575829 | 0.578296 | 0.534032 | 0.646459 |
| transformer_ridge_resid_a5_w0p2 | 0.627386 | 0.674579 | 0.702136 | 0.680493 | 0.576069 | 0.578200 | 0.533968 | 0.646255 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623662`
- Drift vs reference: `0.066908`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671419 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.688251 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a20_w0p05 | 0.575662 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.577338 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.646112 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.