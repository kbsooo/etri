# Hourly Transformer Encoder - only_event

## Representation

- Encoder type: `gru`
- Encoder params: `987`
- Days: `700`
- Token shape: `48 x 187`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.851184`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627403 | 0.672647 | 0.702949 | 0.676490 | 0.575945 | 0.580062 | 0.536539 | 0.647187 |
| transformer_logreg_c0p1_w0p05 | 0.627411 | 0.672667 | 0.702957 | 0.676504 | 0.575957 | 0.580060 | 0.536543 | 0.647187 |
| transformer_logreg_c0p3_w0p05 | 0.627413 | 0.672674 | 0.702960 | 0.676509 | 0.575962 | 0.580059 | 0.536544 | 0.647186 |
| transformer_logreg_c0p03_w0p1 | 0.627468 | 0.672374 | 0.701118 | 0.675354 | 0.576515 | 0.580740 | 0.538795 | 0.647380 |
| transformer_logreg_c0p1_w0p1 | 0.627485 | 0.672415 | 0.701135 | 0.675384 | 0.576538 | 0.580735 | 0.538805 | 0.647380 |
| transformer_logreg_c0p3_w0p1 | 0.627490 | 0.672429 | 0.701141 | 0.675394 | 0.576547 | 0.580733 | 0.538809 | 0.647380 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627703 | 0.673318 | 0.705077 | 0.677854 | 0.575765 | 0.579883 | 0.534776 | 0.647248 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624953`
- Drift vs reference: `0.064774`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.695014 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.671726 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.647161 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.