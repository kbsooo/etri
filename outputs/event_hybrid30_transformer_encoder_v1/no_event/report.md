# Hourly Transformer Encoder - no_event

## Representation

- Days: `700`
- Token shape: `48 x 267`
- Base hourly features selected: `65`
- Mean token missing fraction: `0.192839`
- Device: `mps`
- SSL final loss: `0.371269`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p1 | 0.626666 | 0.672618 | 0.698227 | 0.677440 | 0.576048 | 0.581158 | 0.534184 | 0.646985 |
| transformer_logreg_c0p3_w0p1 | 0.626687 | 0.672788 | 0.697847 | 0.677953 | 0.576793 | 0.581281 | 0.533162 | 0.646985 |
| transformer_logreg_c0p03_w0p1 | 0.626694 | 0.672644 | 0.698955 | 0.676825 | 0.575611 | 0.580729 | 0.534925 | 0.647172 |
| transformer_logreg_c0p3_w0p05 | 0.626884 | 0.672768 | 0.701142 | 0.677653 | 0.575982 | 0.580184 | 0.533624 | 0.646833 |
| transformer_logreg_c0p1_w0p05 | 0.626914 | 0.672711 | 0.701371 | 0.677444 | 0.575652 | 0.580174 | 0.534178 | 0.646872 |
| transformer_logreg_c0p03_w0p05 | 0.626968 | 0.672755 | 0.701777 | 0.677176 | 0.575464 | 0.580004 | 0.534591 | 0.647013 |
| transformer_ridge_resid_a20_w0p1 | 0.627037 | 0.673918 | 0.701588 | 0.679761 | 0.575801 | 0.579803 | 0.532152 | 0.646235 |
| transformer_ridge_resid_a5_w0p1 | 0.627178 | 0.674609 | 0.701416 | 0.681114 | 0.576356 | 0.579244 | 0.530969 | 0.646539 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623381`
- Drift vs reference: `0.069564`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.689266 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_logreg_c0p03_w0p05 | 0.575464 |
| S2 | transformer_ridge_resid_a1_w0p1 | 0.578824 |
| S3 | transformer_ridge_resid_a1_w0p2 | 0.527877 |
| S4 | transformer_ridge_resid_a20_w0p1 | 0.646235 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.