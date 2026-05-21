# Channel Patch Transformer - no_sparse_position

## Representation

- Tensor: `values/masks [days=700, channels=103, tokens=48]`
- Patch length: `4`
- Patches per channel: `12`
- Observed fraction: `0.898241`
- Device: `mps`
- SSL final loss: `0.568122`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p2 | 0.623002 | 0.668093 | 0.689208 | 0.673943 | 0.570999 | 0.578133 | 0.530399 | 0.650241 |
| transformer_ridge_resid_a20_w0p35 | 0.623303 | 0.672801 | 0.685581 | 0.673552 | 0.572091 | 0.579426 | 0.530433 | 0.649239 |
| transformer_ridge_resid_a1_w0p35 | 0.623416 | 0.667913 | 0.683054 | 0.676035 | 0.570205 | 0.581093 | 0.530314 | 0.655295 |
| transformer_ridge_resid_a5_w0p35 | 0.623425 | 0.672177 | 0.686075 | 0.675458 | 0.570674 | 0.579653 | 0.530236 | 0.649699 |
| transformer_ridge_resid_a5_w0p2 | 0.623739 | 0.671301 | 0.691486 | 0.674512 | 0.571825 | 0.578121 | 0.531164 | 0.647763 |
| transformer_logreg_c0p3_w0p2 | 0.623771 | 0.671510 | 0.686296 | 0.672207 | 0.573599 | 0.578083 | 0.531476 | 0.653225 |
| transformer_ridge_resid_a20_w0p2 | 0.624120 | 0.672071 | 0.691776 | 0.674055 | 0.572794 | 0.578598 | 0.531738 | 0.647807 |
| transformer_logreg_c0p1_w0p2 | 0.624251 | 0.671330 | 0.687537 | 0.671953 | 0.574085 | 0.578436 | 0.533275 | 0.653141 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620093`
- Drift vs reference: `0.094730`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_ridge_resid_a1_w0p35 | 0.667913 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.677137 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.669943 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.570205 |
| S2 | transformer_logreg_c0p3_w0p1 | 0.578040 |
| S3 | transformer_ridge_resid_a5_w0p35 | 0.530236 |
| S4 | transformer_ridge_resid_a5_w0p05 | 0.647177 |