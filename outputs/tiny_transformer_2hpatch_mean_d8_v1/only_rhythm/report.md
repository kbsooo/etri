# Hourly Transformer Encoder - only_rhythm

## Representation

- Encoder type: `transformer`
- Encoder params: `3323`
- Days: `700`
- Token shape: `12 x 131`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `0.319734`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627521 | 0.672943 | 0.702802 | 0.676659 | 0.576138 | 0.579993 | 0.536774 | 0.647339 |
| transformer_logreg_c0p1_w0p05 | 0.627562 | 0.673051 | 0.702682 | 0.676534 | 0.576304 | 0.580064 | 0.536815 | 0.647483 |
| transformer_logreg_c0p3_w0p05 | 0.627578 | 0.673116 | 0.702596 | 0.676375 | 0.576434 | 0.580084 | 0.536854 | 0.647586 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_logreg_c0p03_w0p1 | 0.627699 | 0.672952 | 0.700829 | 0.675700 | 0.576907 | 0.580598 | 0.539235 | 0.647672 |
| transformer_logreg_c0p1_w0p1 | 0.627786 | 0.673169 | 0.700605 | 0.675465 | 0.577239 | 0.580736 | 0.539318 | 0.647967 |
| transformer_logreg_c0p3_w0p1 | 0.627822 | 0.673298 | 0.700448 | 0.675166 | 0.577497 | 0.580779 | 0.539392 | 0.648177 |
| subject_prior_a16 | 0.627839 | 0.672177 | 0.699188 | 0.673823 | 0.577202 | 0.582206 | 0.541687 | 0.648586 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624716`
- Drift vs reference: `0.064603`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.693215 |
| Q3 | transformer_logreg_c0p3_w0p35 | 0.671755 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.