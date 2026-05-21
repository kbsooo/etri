# Hourly Transformer Encoder - no_sleep

## Representation

- Encoder type: `transformer`
- Encoder params: `12486`
- Days: `700`
- Token shape: `12 x 670`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean_std`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.218091`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626879 | 0.670896 | 0.698241 | 0.676239 | 0.577297 | 0.579787 | 0.538374 | 0.647319 |
| transformer_logreg_c0p1_w0p1 | 0.626964 | 0.671158 | 0.698506 | 0.676033 | 0.577176 | 0.580052 | 0.538504 | 0.647323 |
| transformer_logreg_c0p03_w0p1 | 0.627063 | 0.671428 | 0.698897 | 0.675857 | 0.577026 | 0.580305 | 0.538607 | 0.647320 |
| transformer_logreg_c0p3_w0p05 | 0.627100 | 0.671900 | 0.701430 | 0.676932 | 0.576337 | 0.579600 | 0.536346 | 0.647153 |
| transformer_ridge_resid_a20_w0p35 | 0.627131 | 0.671538 | 0.698643 | 0.679899 | 0.578011 | 0.578573 | 0.536936 | 0.646315 |
| transformer_ridge_resid_a20_w0p2 | 0.627142 | 0.671988 | 0.700797 | 0.678927 | 0.576937 | 0.578937 | 0.535828 | 0.646578 |
| transformer_logreg_c0p1_w0p05 | 0.627144 | 0.672038 | 0.701572 | 0.676831 | 0.576274 | 0.579729 | 0.536408 | 0.647156 |
| transformer_ridge_resid_a5_w0p2 | 0.627184 | 0.671315 | 0.700780 | 0.679388 | 0.577380 | 0.578695 | 0.536167 | 0.646562 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623280`
- Drift vs reference: `0.069724`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p35 | 0.669379 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.687273 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673408 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.577850 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a20_w0p35 | 0.646315 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.