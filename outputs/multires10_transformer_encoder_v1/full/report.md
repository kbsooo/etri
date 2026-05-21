# Hourly Transformer Encoder - full

## Representation

- Days: `700`
- Token shape: `144 x 267`
- Base hourly features selected: `65`
- Mean token missing fraction: `0.226526`
- Device: `mps`
- SSL final loss: `0.331980`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627318 | 0.673543 | 0.701751 | 0.676941 | 0.576179 | 0.579103 | 0.535327 | 0.648383 |
| transformer_logreg_c0p1_w0p05 | 0.627332 | 0.673923 | 0.701438 | 0.676645 | 0.576364 | 0.579312 | 0.535081 | 0.648560 |
| transformer_ridge_resid_a20_w0p05 | 0.627394 | 0.674619 | 0.703168 | 0.677192 | 0.576048 | 0.579046 | 0.533758 | 0.647927 |
| transformer_logreg_c0p3_w0p05 | 0.627401 | 0.674289 | 0.701413 | 0.676285 | 0.576493 | 0.579765 | 0.534944 | 0.648621 |
| transformer_logreg_c0p03_w0p1 | 0.627410 | 0.674225 | 0.698904 | 0.676366 | 0.577021 | 0.579073 | 0.536387 | 0.649892 |
| transformer_ridge_resid_a20_w0p1 | 0.627425 | 0.676277 | 0.701734 | 0.676901 | 0.576642 | 0.578617 | 0.532958 | 0.648846 |
| transformer_ridge_resid_a5_w0p05 | 0.627505 | 0.675060 | 0.703079 | 0.676721 | 0.576091 | 0.579834 | 0.533724 | 0.648024 |
| transformer_logreg_c0p1_w0p1 | 0.627516 | 0.675045 | 0.698384 | 0.675859 | 0.577457 | 0.579591 | 0.535945 | 0.650334 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624279`
- Drift vs reference: `0.067753`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.690301 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a20_w0p1 | 0.578617 |
| S3 | transformer_ridge_resid_a20_w0p2 | 0.532060 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.