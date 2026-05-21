# Hourly Transformer Encoder - only_event

## Representation

- Encoder type: `gru`
- Encoder params: `3723`
- Days: `700`
- Token shape: `48 x 187`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.371961`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627336 | 0.672503 | 0.702372 | 0.676777 | 0.576177 | 0.580049 | 0.536337 | 0.647140 |
| transformer_logreg_c0p03_w0p1 | 0.627357 | 0.672066 | 0.700019 | 0.675921 | 0.577018 | 0.580733 | 0.538440 | 0.647298 |
| transformer_logreg_c0p1_w0p05 | 0.627377 | 0.672590 | 0.702312 | 0.676849 | 0.576347 | 0.579958 | 0.536428 | 0.647157 |
| transformer_logreg_c0p3_w0p05 | 0.627403 | 0.672638 | 0.702297 | 0.676867 | 0.576451 | 0.579908 | 0.536498 | 0.647165 |
| transformer_logreg_c0p1_w0p1 | 0.627448 | 0.672246 | 0.699906 | 0.676071 | 0.577371 | 0.580569 | 0.538631 | 0.647340 |
| transformer_logreg_c0p3_w0p1 | 0.627507 | 0.672349 | 0.699879 | 0.676113 | 0.577587 | 0.580482 | 0.538774 | 0.647362 |
| transformer_ridge_resid_a20_w0p05 | 0.627612 | 0.673564 | 0.704499 | 0.678104 | 0.575724 | 0.579787 | 0.534530 | 0.647078 |
| transformer_ridge_resid_a20_w0p1 | 0.627614 | 0.673992 | 0.704040 | 0.678468 | 0.575781 | 0.579741 | 0.534365 | 0.646915 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624594`
- Drift vs reference: `0.067183`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671849 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.691692 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673607 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.579691 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a20_w0p35 | 0.646586 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.