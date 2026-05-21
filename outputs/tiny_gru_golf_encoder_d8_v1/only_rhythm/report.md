# Hourly Transformer Encoder - only_rhythm

## Representation

- Encoder type: `gru`
- Encoder params: `2771`
- Days: `700`
- Token shape: `48 x 131`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `0.578894`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p1 | 0.627249 | 0.672189 | 0.700155 | 0.676188 | 0.575780 | 0.579801 | 0.538514 | 0.648115 |
| transformer_logreg_c0p3_w0p1 | 0.627249 | 0.672210 | 0.699943 | 0.676228 | 0.575750 | 0.579573 | 0.538550 | 0.648490 |
| transformer_logreg_c0p3_w0p05 | 0.627276 | 0.672570 | 0.702335 | 0.676922 | 0.575529 | 0.579425 | 0.536432 | 0.647715 |
| transformer_logreg_c0p1_w0p05 | 0.627281 | 0.672562 | 0.702449 | 0.676907 | 0.575551 | 0.579551 | 0.536414 | 0.647534 |
| transformer_logreg_c0p03_w0p1 | 0.627290 | 0.672220 | 0.700442 | 0.676066 | 0.575931 | 0.580103 | 0.538504 | 0.647762 |
| transformer_logreg_c0p03_w0p05 | 0.627308 | 0.672580 | 0.702601 | 0.676849 | 0.575638 | 0.579716 | 0.536408 | 0.647367 |
| transformer_ridge_resid_a20_w0p05 | 0.627623 | 0.673332 | 0.704989 | 0.678126 | 0.575330 | 0.579302 | 0.534911 | 0.647374 |
| transformer_ridge_resid_a5_w0p05 | 0.627629 | 0.673358 | 0.704948 | 0.678105 | 0.575318 | 0.579240 | 0.534976 | 0.647456 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624076`
- Drift vs reference: `0.066067`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p1_w0p2 | 0.672115 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.691801 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a20_w0p35 | 0.574178 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.576315 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.