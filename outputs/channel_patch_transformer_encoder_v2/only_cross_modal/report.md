# Channel Patch Transformer - only_cross_modal

## Representation

- Tensor: `values/masks [days=700, channels=69, tokens=48]`
- Patch length: `4`
- Patches per channel: `12`
- Observed fraction: `0.977029`
- Device: `mps`
- SSL final loss: `0.464938`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p2 | 0.623727 | 0.671168 | 0.689119 | 0.671902 | 0.573298 | 0.576778 | 0.532323 | 0.651499 |
| transformer_ridge_resid_a20_w0p35 | 0.623752 | 0.672642 | 0.690662 | 0.673485 | 0.571582 | 0.577477 | 0.533339 | 0.647075 |
| transformer_ridge_resid_a5_w0p35 | 0.623845 | 0.672392 | 0.691634 | 0.675253 | 0.570582 | 0.575744 | 0.534367 | 0.646946 |
| transformer_logreg_c0p1_w0p2 | 0.623978 | 0.671456 | 0.689596 | 0.671162 | 0.573416 | 0.577515 | 0.533572 | 0.651130 |
| transformer_ridge_resid_a1_w0p2 | 0.623982 | 0.671171 | 0.693965 | 0.675461 | 0.571335 | 0.575299 | 0.533883 | 0.646757 |
| transformer_logreg_c0p1_w0p35 | 0.624017 | 0.672090 | 0.681754 | 0.668570 | 0.574397 | 0.579340 | 0.535193 | 0.656774 |
| transformer_logreg_c0p3_w0p35 | 0.624072 | 0.672026 | 0.681822 | 0.670286 | 0.574488 | 0.578551 | 0.533415 | 0.657918 |
| transformer_ridge_resid_a5_w0p2 | 0.624076 | 0.671565 | 0.694378 | 0.674723 | 0.571890 | 0.576294 | 0.533509 | 0.646176 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620719`
- Drift vs reference: `0.095392`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.671168 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.681754 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.667886 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.570433 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.575295 |
| S3 | transformer_logreg_c0p3_w0p2 | 0.532323 |
| S4 | transformer_ridge_resid_a5_w0p2 | 0.646176 |