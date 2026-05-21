# Hourly Transformer Encoder - only_event

## Representation

- Days: `700`
- Token shape: `48 x 187`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.215611`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627393 | 0.673435 | 0.701566 | 0.677364 | 0.576521 | 0.580210 | 0.536025 | 0.646634 |
| transformer_logreg_c0p03_w0p1 | 0.627475 | 0.673978 | 0.698530 | 0.677155 | 0.577685 | 0.580967 | 0.537623 | 0.646388 |
| transformer_logreg_c0p1_w0p05 | 0.627500 | 0.673884 | 0.701805 | 0.677187 | 0.576580 | 0.580421 | 0.536138 | 0.646486 |
| transformer_logreg_c0p3_w0p05 | 0.627592 | 0.674248 | 0.702024 | 0.676725 | 0.576584 | 0.580613 | 0.536301 | 0.646648 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_logreg_c0p1_w0p1 | 0.627729 | 0.674909 | 0.699050 | 0.676850 | 0.577854 | 0.581427 | 0.537867 | 0.646144 |
| transformer_ridge_resid_a1_w0p05 | 0.627820 | 0.674856 | 0.703680 | 0.675417 | 0.576861 | 0.580841 | 0.535702 | 0.647385 |
| subject_prior_a16 | 0.627839 | 0.672177 | 0.699188 | 0.673823 | 0.577202 | 0.582206 | 0.541687 | 0.648586 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623701`
- Drift vs reference: `0.068245`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.688880 |
| Q3 | transformer_ridge_resid_a1_w0p35 | 0.670297 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a20_w0p2 | 0.645962 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.