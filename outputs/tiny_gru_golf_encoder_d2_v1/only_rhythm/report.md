# Hourly Transformer Encoder - only_rhythm

## Representation

- Encoder type: `gru`
- Encoder params: `707`
- Days: `700`
- Token shape: `48 x 131`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `1.063691`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627394 | 0.672516 | 0.702634 | 0.676486 | 0.575994 | 0.580244 | 0.536715 | 0.647168 |
| transformer_logreg_c0p1_w0p05 | 0.627405 | 0.672521 | 0.702610 | 0.676499 | 0.576027 | 0.580266 | 0.536742 | 0.647167 |
| transformer_logreg_c0p3_w0p05 | 0.627409 | 0.672523 | 0.702601 | 0.676503 | 0.576041 | 0.580273 | 0.536751 | 0.647167 |
| transformer_logreg_c0p03_w0p1 | 0.627453 | 0.672095 | 0.700516 | 0.675357 | 0.576628 | 0.581105 | 0.539127 | 0.647344 |
| transformer_logreg_c0p1_w0p1 | 0.627476 | 0.672105 | 0.700472 | 0.675384 | 0.576696 | 0.581149 | 0.539181 | 0.647343 |
| transformer_logreg_c0p3_w0p1 | 0.627484 | 0.672109 | 0.700456 | 0.675394 | 0.576725 | 0.581164 | 0.539199 | 0.647343 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627683 | 0.673217 | 0.704721 | 0.677876 | 0.575853 | 0.580021 | 0.534969 | 0.647124 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624599`
- Drift vs reference: `0.065120`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671909 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.693188 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.671906 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.646602 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.