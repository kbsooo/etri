# Channel Patch Transformer - only_event

## Representation

- Tensor: `values/masks [days=700, channels=45, tokens=48]`
- Patch length: `2`
- Patches per channel: `24`
- Observed fraction: `1.000000`
- Device: `mps`
- SSL final loss: `0.418007`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p35 | 0.622922 | 0.670471 | 0.681235 | 0.663456 | 0.574118 | 0.579053 | 0.532131 | 0.659990 |
| transformer_logreg_c0p1_w0p35 | 0.623055 | 0.671135 | 0.681205 | 0.663904 | 0.574108 | 0.579447 | 0.532934 | 0.658651 |
| transformer_ridge_resid_a20_w0p35 | 0.623073 | 0.671347 | 0.687554 | 0.667303 | 0.571676 | 0.581010 | 0.531837 | 0.650786 |
| transformer_logreg_c0p3_w0p2 | 0.623101 | 0.670192 | 0.688842 | 0.667935 | 0.573149 | 0.577141 | 0.531725 | 0.652720 |
| transformer_ridge_resid_a5_w0p35 | 0.623314 | 0.671418 | 0.689167 | 0.666206 | 0.570390 | 0.580474 | 0.533580 | 0.651961 |
| transformer_logreg_c0p1_w0p2 | 0.623451 | 0.670879 | 0.689314 | 0.668501 | 0.573340 | 0.577606 | 0.532283 | 0.652238 |
| transformer_ridge_resid_a1_w0p2 | 0.623517 | 0.670551 | 0.692898 | 0.668147 | 0.571027 | 0.578793 | 0.533717 | 0.649488 |
| transformer_ridge_resid_a5_w0p2 | 0.623670 | 0.670775 | 0.692683 | 0.669535 | 0.571717 | 0.578620 | 0.533385 | 0.648977 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620124`
- Drift vs reference: `0.092020`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.670192 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.681205 |
| Q3 | transformer_logreg_c0p3_w0p35 | 0.663456 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.569879 |
| S2 | transformer_logreg_c0p3_w0p2 | 0.577141 |
| S3 | transformer_logreg_c0p3_w0p2 | 0.531725 |
| S4 | subject_prior_a8 | 0.647272 |