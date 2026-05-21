# Hourly Transformer Encoder - only_cross_modal

## Representation

- Encoder type: `gru`
- Encoder params: `1015`
- Days: `700`
- Token shape: `48 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.454964`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p35 | 0.626767 | 0.676213 | 0.700535 | 0.679569 | 0.577117 | 0.577987 | 0.536174 | 0.639772 |
| transformer_ridge_resid_a5_w0p35 | 0.626857 | 0.675926 | 0.700993 | 0.679565 | 0.577395 | 0.577957 | 0.535955 | 0.640210 |
| transformer_ridge_resid_a1_w0p2 | 0.626929 | 0.674580 | 0.702072 | 0.678703 | 0.576365 | 0.578652 | 0.535488 | 0.642640 |
| transformer_ridge_resid_a5_w0p2 | 0.627009 | 0.674460 | 0.702366 | 0.678715 | 0.576559 | 0.578651 | 0.535372 | 0.642937 |
| transformer_logreg_c0p3_w0p1 | 0.627018 | 0.672045 | 0.698846 | 0.675829 | 0.576928 | 0.580483 | 0.539214 | 0.645782 |
| transformer_ridge_resid_a20_w0p35 | 0.627074 | 0.675467 | 0.701887 | 0.679561 | 0.577905 | 0.577956 | 0.535593 | 0.641150 |
| transformer_logreg_c0p1_w0p1 | 0.627136 | 0.672003 | 0.699263 | 0.675856 | 0.577121 | 0.580442 | 0.539140 | 0.646130 |
| transformer_logreg_c0p3_w0p05 | 0.627159 | 0.672482 | 0.701735 | 0.676730 | 0.576128 | 0.579920 | 0.536760 | 0.646357 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622912`
- Drift vs reference: `0.067098`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671714 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.689071 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673136 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a20_w0p35 | 0.577956 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.639772 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.