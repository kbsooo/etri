# Hourly Transformer Encoder - only_cross_modal

## Representation

- Encoder type: `transformer`
- Encoder params: `2807`
- Days: `700`
- Token shape: `24 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.084194`
- Device: `mps`
- SSL final loss: `0.545127`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p2 | 0.626985 | 0.673147 | 0.693787 | 0.678173 | 0.577114 | 0.582711 | 0.534867 | 0.649094 |
| transformer_ridge_resid_a1_w0p1 | 0.627144 | 0.673000 | 0.698964 | 0.677863 | 0.576281 | 0.581148 | 0.534709 | 0.648045 |
| transformer_ridge_resid_a5_w0p2 | 0.627160 | 0.673339 | 0.696272 | 0.677690 | 0.576940 | 0.582089 | 0.535071 | 0.648719 |
| transformer_logreg_c0p3_w0p1 | 0.627169 | 0.672454 | 0.697390 | 0.675339 | 0.577056 | 0.581350 | 0.538558 | 0.648038 |
| transformer_logreg_c0p3_w0p05 | 0.627223 | 0.672664 | 0.700992 | 0.676467 | 0.576173 | 0.580372 | 0.536378 | 0.647515 |
| transformer_ridge_resid_a5_w0p1 | 0.627282 | 0.673124 | 0.700351 | 0.677634 | 0.576212 | 0.580900 | 0.534853 | 0.647902 |
| transformer_ridge_resid_a1_w0p05 | 0.627354 | 0.673047 | 0.701870 | 0.677789 | 0.575960 | 0.580474 | 0.534717 | 0.647624 |
| transformer_logreg_c0p1_w0p05 | 0.627389 | 0.672762 | 0.702043 | 0.676470 | 0.576079 | 0.580298 | 0.536573 | 0.647498 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623493`
- Drift vs reference: `0.066589`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.684405 |
| Q3 | transformer_logreg_c0p1_w0p35 | 0.672005 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.