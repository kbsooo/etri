# Hourly Transformer Encoder - only_cross_modal

## Representation

- Days: `700`
- Token shape: `24 x 51`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.084194`
- Device: `mps`
- SSL final loss: `0.216304`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p2 | 0.625056 | 0.672584 | 0.696710 | 0.677422 | 0.573541 | 0.582703 | 0.523655 | 0.648780 |
| transformer_ridge_resid_a5_w0p2 | 0.625229 | 0.672542 | 0.695060 | 0.677748 | 0.573474 | 0.582977 | 0.526733 | 0.648070 |
| transformer_ridge_resid_a1_w0p1 | 0.625321 | 0.671903 | 0.699296 | 0.676721 | 0.573682 | 0.580337 | 0.528152 | 0.647156 |
| transformer_logreg_c0p3_w0p1 | 0.625659 | 0.671034 | 0.694370 | 0.675373 | 0.575032 | 0.581212 | 0.533976 | 0.648619 |
| transformer_logreg_c0p3_w0p2 | 0.625664 | 0.670683 | 0.686407 | 0.674267 | 0.576175 | 0.584460 | 0.535668 | 0.651990 |
| transformer_ridge_resid_a5_w0p1 | 0.625795 | 0.672228 | 0.698927 | 0.677223 | 0.574025 | 0.580847 | 0.530183 | 0.647128 |
| transformer_logreg_c0p1_w0p1 | 0.626070 | 0.671475 | 0.695202 | 0.675478 | 0.575815 | 0.581158 | 0.534962 | 0.648399 |
| transformer_ridge_resid_a20_w0p2 | 0.626191 | 0.673007 | 0.694903 | 0.678128 | 0.575248 | 0.583877 | 0.530389 | 0.647786 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620680`
- Drift vs reference: `0.076263`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.670683 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.678873 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673789 |
| S1 | transformer_ridge_resid_a5_w0p2 | 0.573474 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | transformer_ridge_resid_a1_w0p35 | 0.521082 |
| S4 | transformer_ridge_resid_a1_w0p05 | 0.647001 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.