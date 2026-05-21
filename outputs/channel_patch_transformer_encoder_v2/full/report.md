# Channel Patch Transformer - full

## Representation

- Tensor: `values/masks [days=700, channels=110, tokens=48]`
- Patch length: `4`
- Patches per channel: `12`
- Observed fraction: `0.886050`
- Device: `mps`
- SSL final loss: `0.577827`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a5_w0p35 | 0.622782 | 0.673973 | 0.690695 | 0.669418 | 0.570357 | 0.574361 | 0.531192 | 0.649478 |
| transformer_ridge_resid_a1_w0p2 | 0.623006 | 0.673035 | 0.692502 | 0.671439 | 0.571531 | 0.572522 | 0.529470 | 0.650545 |
| transformer_ridge_resid_a5_w0p2 | 0.623470 | 0.672255 | 0.693596 | 0.671573 | 0.571835 | 0.575286 | 0.532116 | 0.647631 |
| transformer_ridge_resid_a20_w0p35 | 0.623542 | 0.673900 | 0.690451 | 0.670160 | 0.572030 | 0.577029 | 0.532549 | 0.648674 |
| transformer_logreg_c0p3_w0p2 | 0.623598 | 0.671789 | 0.688907 | 0.669842 | 0.573309 | 0.576613 | 0.532450 | 0.652274 |
| transformer_logreg_c0p3_w0p35 | 0.623728 | 0.673110 | 0.681561 | 0.666447 | 0.574506 | 0.578020 | 0.533390 | 0.659061 |
| transformer_ridge_resid_a20_w0p2 | 0.624307 | 0.672779 | 0.694223 | 0.672349 | 0.572843 | 0.577367 | 0.533102 | 0.647487 |
| transformer_logreg_c0p1_w0p2 | 0.624372 | 0.672579 | 0.690550 | 0.670153 | 0.573915 | 0.577961 | 0.533470 | 0.651978 |

## Target-Wise Selection

- Target-wise avg logloss: `0.619794`
- Drift vs reference: `0.085971`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.671789 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.681561 |
| Q3 | transformer_logreg_c0p3_w0p35 | 0.666447 |
| S1 | transformer_ridge_resid_a5_w0p35 | 0.570357 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.572522 |
| S3 | transformer_ridge_resid_a1_w0p35 | 0.528734 |
| S4 | transformer_ridge_resid_a5_w0p05 | 0.647147 |