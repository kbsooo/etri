# Hourly Transformer Encoder - only_rhythm

## Representation

- Days: `700`
- Token shape: `48 x 131`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `0.625616`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p1 | 0.627310 | 0.672201 | 0.701359 | 0.674639 | 0.575971 | 0.580743 | 0.538924 | 0.647335 |
| transformer_logreg_c0p1_w0p1 | 0.627318 | 0.672230 | 0.701402 | 0.674602 | 0.575959 | 0.580743 | 0.538953 | 0.647338 |
| transformer_logreg_c0p3_w0p1 | 0.627323 | 0.672242 | 0.701416 | 0.674592 | 0.575962 | 0.580743 | 0.538964 | 0.647341 |
| transformer_logreg_c0p03_w0p05 | 0.627324 | 0.672560 | 0.703063 | 0.676129 | 0.575667 | 0.580061 | 0.536619 | 0.647165 |
| transformer_logreg_c0p1_w0p05 | 0.627327 | 0.672574 | 0.703083 | 0.676109 | 0.575660 | 0.580061 | 0.536635 | 0.647166 |
| transformer_logreg_c0p3_w0p05 | 0.627329 | 0.672579 | 0.703090 | 0.676103 | 0.575661 | 0.580061 | 0.536640 | 0.647167 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627655 | 0.673233 | 0.705248 | 0.677565 | 0.575511 | 0.579837 | 0.534964 | 0.647231 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624559`
- Drift vs reference: `0.065134`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.696039 |
| Q3 | transformer_logreg_c0p3_w0p35 | 0.669205 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.574604 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.579806 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.647051 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.