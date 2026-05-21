# Channel Patch Transformer - full

## Representation

- Tensor: `values/masks [days=700, channels=110, tokens=48]`
- Patch length: `8`
- Patches per channel: `6`
- Observed fraction: `0.886050`
- Device: `mps`
- SSL final loss: `0.628591`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a20_w0p35 | 0.623066 | 0.674199 | 0.683893 | 0.672512 | 0.571943 | 0.576575 | 0.531650 | 0.650693 |
| transformer_ridge_resid_a5_w0p35 | 0.623245 | 0.676006 | 0.684519 | 0.674052 | 0.570377 | 0.574685 | 0.531602 | 0.651477 |
| transformer_ridge_resid_a1_w0p2 | 0.623385 | 0.674532 | 0.689527 | 0.674353 | 0.569943 | 0.573758 | 0.531378 | 0.650205 |
| transformer_ridge_resid_a5_w0p2 | 0.623619 | 0.673063 | 0.690522 | 0.673733 | 0.571688 | 0.575657 | 0.532026 | 0.648646 |
| transformer_logreg_c0p3_w0p2 | 0.623947 | 0.672290 | 0.685237 | 0.671060 | 0.574517 | 0.577586 | 0.532862 | 0.654076 |
| transformer_ridge_resid_a20_w0p2 | 0.623951 | 0.672658 | 0.690728 | 0.673369 | 0.572755 | 0.577161 | 0.532431 | 0.648551 |
| transformer_ridge_resid_a1_w0p35 | 0.624237 | 0.681595 | 0.683386 | 0.676938 | 0.567879 | 0.572732 | 0.531963 | 0.655163 |
| transformer_logreg_c0p1_w0p2 | 0.624253 | 0.672221 | 0.686132 | 0.670570 | 0.574672 | 0.578615 | 0.534092 | 0.653470 |

## Target-Wise Selection

- Target-wise avg logloss: `0.619152`
- Drift vs reference: `0.086491`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.672077 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.675145 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.667583 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.567879 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.572732 |
| S3 | transformer_ridge_resid_a1_w0p2 | 0.531378 |
| S4 | subject_prior_a8 | 0.647272 |