# Hourly Transformer Encoder - full

## Representation

- Days: `700`
- Token shape: `48 x 447`
- Base hourly features selected: `110`
- Mean token missing fraction: `0.113950`
- Device: `mps`
- SSL final loss: `0.335143`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p1 | 0.626623 | 0.682024 | 0.697800 | 0.674006 | 0.573850 | 0.580812 | 0.533986 | 0.643884 |
| transformer_ridge_resid_a1_w0p05 | 0.626895 | 0.677392 | 0.701084 | 0.675652 | 0.574531 | 0.580062 | 0.534186 | 0.645357 |
| transformer_logreg_c0p3_w0p1 | 0.626948 | 0.677418 | 0.699180 | 0.674467 | 0.575649 | 0.581530 | 0.534939 | 0.645456 |
| transformer_logreg_c0p3_w0p05 | 0.627059 | 0.675136 | 0.701848 | 0.675939 | 0.575417 | 0.580431 | 0.534561 | 0.646080 |
| transformer_ridge_resid_a5_w0p1 | 0.627059 | 0.679903 | 0.700305 | 0.675068 | 0.574065 | 0.581420 | 0.534300 | 0.644351 |
| transformer_logreg_c0p03_w0p1 | 0.627083 | 0.674789 | 0.700294 | 0.675125 | 0.575993 | 0.581472 | 0.535521 | 0.646388 |
| transformer_logreg_c0p1_w0p1 | 0.627123 | 0.676058 | 0.700096 | 0.674837 | 0.575864 | 0.581807 | 0.535152 | 0.646046 |
| transformer_logreg_c0p1_w0p05 | 0.627170 | 0.674471 | 0.702340 | 0.676154 | 0.575553 | 0.580582 | 0.534680 | 0.646407 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623472`
- Drift vs reference: `0.069957`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_ridge_resid_a1_w0p35 | 0.691166 |
| Q3 | transformer_logreg_c0p3_w0p35 | 0.672078 |
| S1 | transformer_ridge_resid_a5_w0p2 | 0.573717 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p2 | 0.642282 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.