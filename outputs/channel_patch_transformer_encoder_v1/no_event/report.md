# Channel Patch Transformer - no_event

## Representation

- Tensor: `values/masks [days=700, channels=65, tokens=48]`
- Patch length: `4`
- Patches per channel: `12`
- Observed fraction: `0.807161`
- Device: `mps`
- SSL final loss: `0.683440`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p2 | 0.624087 | 0.671458 | 0.689413 | 0.671931 | 0.574862 | 0.577702 | 0.531290 | 0.651949 |
| transformer_ridge_resid_a5_w0p2 | 0.624172 | 0.672226 | 0.695692 | 0.674989 | 0.573086 | 0.574750 | 0.531649 | 0.646815 |
| transformer_ridge_resid_a20_w0p35 | 0.624490 | 0.673108 | 0.690946 | 0.672566 | 0.573701 | 0.577242 | 0.535668 | 0.648198 |
| transformer_ridge_resid_a5_w0p35 | 0.624547 | 0.673652 | 0.694157 | 0.675708 | 0.572726 | 0.572788 | 0.534723 | 0.648073 |
| transformer_logreg_c0p3_w0p35 | 0.624596 | 0.672362 | 0.682064 | 0.670225 | 0.577128 | 0.579986 | 0.531703 | 0.658707 |
| transformer_ridge_resid_a1_w0p2 | 0.624664 | 0.673490 | 0.697026 | 0.678387 | 0.573281 | 0.571386 | 0.530717 | 0.648363 |
| transformer_ridge_resid_a20_w0p2 | 0.624670 | 0.672426 | 0.694898 | 0.673702 | 0.573791 | 0.577630 | 0.533100 | 0.647146 |
| transformer_logreg_c0p1_w0p2 | 0.624767 | 0.672192 | 0.690239 | 0.671347 | 0.574891 | 0.578807 | 0.534421 | 0.651473 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620150`
- Drift vs reference: `0.093270`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.671458 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.682064 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.668441 |
| S1 | transformer_ridge_resid_a5_w0p35 | 0.572726 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.568893 |
| S3 | transformer_ridge_resid_a1_w0p2 | 0.530717 |
| S4 | transformer_ridge_resid_a5_w0p1 | 0.646749 |