# Hourly Transformer Encoder - only_rhythm

## Representation

- Days: `700`
- Token shape: `48 x 131`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `0.601936`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627482 | 0.672310 | 0.702921 | 0.676750 | 0.576284 | 0.580330 | 0.536355 | 0.647425 |
| transformer_logreg_c0p1_w0p05 | 0.627495 | 0.672248 | 0.702826 | 0.676762 | 0.576456 | 0.580393 | 0.536317 | 0.647461 |
| transformer_logreg_c0p3_w0p05 | 0.627501 | 0.672213 | 0.702711 | 0.676738 | 0.576601 | 0.580426 | 0.536342 | 0.647477 |
| transformer_logreg_c0p03_w0p1 | 0.627611 | 0.671683 | 0.701077 | 0.675871 | 0.577207 | 0.581247 | 0.538364 | 0.647832 |
| transformer_logreg_c0p1_w0p1 | 0.627644 | 0.671567 | 0.700896 | 0.675899 | 0.577558 | 0.581372 | 0.538311 | 0.647905 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_logreg_c0p3_w0p1 | 0.627665 | 0.671502 | 0.700679 | 0.675853 | 0.577857 | 0.581441 | 0.538383 | 0.647938 |
| subject_prior_a16 | 0.627839 | 0.672177 | 0.699188 | 0.673823 | 0.577202 | 0.582206 | 0.541687 | 0.648586 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624872`
- Drift vs reference: `0.065461`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.670778 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.693960 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673503 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.