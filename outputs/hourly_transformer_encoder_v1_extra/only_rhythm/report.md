# Hourly Transformer Encoder - only_rhythm

## Representation

- Days: `700`
- Token shape: `24 x 53`
- Base hourly features selected: `23`
- Mean token missing fraction: `0.314130`
- Device: `mps`
- SSL final loss: `0.270226`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a20_w0p35 | 0.624185 | 0.669874 | 0.682400 | 0.671174 | 0.575115 | 0.579966 | 0.540899 | 0.649865 |
| transformer_ridge_resid_a20_w0p2 | 0.624266 | 0.669911 | 0.689892 | 0.672679 | 0.573793 | 0.578612 | 0.537014 | 0.647962 |
| transformer_ridge_resid_a5_w0p2 | 0.624320 | 0.669498 | 0.687597 | 0.672894 | 0.573140 | 0.578532 | 0.538865 | 0.649717 |
| transformer_logreg_c0p3_w0p2 | 0.624450 | 0.668831 | 0.682281 | 0.669174 | 0.575254 | 0.583121 | 0.542781 | 0.649711 |
| transformer_logreg_c0p1_w0p2 | 0.624740 | 0.669109 | 0.685097 | 0.669513 | 0.575718 | 0.583495 | 0.540976 | 0.649271 |
| transformer_logreg_c0p3_w0p1 | 0.624989 | 0.670099 | 0.692254 | 0.672750 | 0.574406 | 0.580178 | 0.537610 | 0.647628 |
| transformer_logreg_c0p1_w0p1 | 0.625285 | 0.670378 | 0.693893 | 0.673064 | 0.574801 | 0.580511 | 0.536822 | 0.647528 |
| transformer_ridge_resid_a5_w0p1 | 0.625291 | 0.670669 | 0.695246 | 0.674609 | 0.573631 | 0.578553 | 0.536277 | 0.648049 |

## Target-Wise Selection

- Target-wise avg logloss: `0.619825`
- Drift vs reference: `0.071960`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.668831 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.671803 |
| Q3 | transformer_logreg_c0p1_w0p35 | 0.666235 |
| S1 | transformer_ridge_resid_a5_w0p2 | 0.573140 |
| S2 | transformer_ridge_resid_a5_w0p2 | 0.578532 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_logreg_c0p1_w0p05 | 0.647202 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.