# Hourly Transformer Encoder - only_event

## Representation

- Days: `700`
- Token shape: `48 x 187`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.410200`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p05 | 0.627395 | 0.672561 | 0.701928 | 0.676722 | 0.576559 | 0.580348 | 0.536280 | 0.647368 |
| transformer_logreg_c0p1_w0p05 | 0.627403 | 0.672537 | 0.702005 | 0.676729 | 0.576486 | 0.580283 | 0.536363 | 0.647422 |
| transformer_logreg_c0p03_w0p05 | 0.627418 | 0.672510 | 0.702180 | 0.676716 | 0.576373 | 0.580212 | 0.536511 | 0.647424 |
| transformer_logreg_c0p3_w0p1 | 0.627449 | 0.672171 | 0.699208 | 0.675818 | 0.577766 | 0.581249 | 0.538195 | 0.647736 |
| transformer_logreg_c0p1_w0p1 | 0.627465 | 0.672126 | 0.699343 | 0.675827 | 0.577616 | 0.581139 | 0.538362 | 0.647842 |
| transformer_logreg_c0p03_w0p1 | 0.627492 | 0.672076 | 0.699662 | 0.675797 | 0.577390 | 0.581014 | 0.538661 | 0.647846 |
| transformer_ridge_resid_a1_w0p1 | 0.627571 | 0.673609 | 0.702770 | 0.678215 | 0.576161 | 0.579993 | 0.534954 | 0.647291 |
| transformer_ridge_resid_a1_w0p05 | 0.627589 | 0.673377 | 0.703834 | 0.677973 | 0.575917 | 0.579909 | 0.534854 | 0.647260 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624439`
- Drift vs reference: `0.066281`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671847 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.690251 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673127 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p05 | 0.647260 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.