# Channel Patch Transformer - only_event

## Representation

- Tensor: `values/masks [days=700, channels=45, tokens=48]`
- Patch length: `4`
- Patches per channel: `12`
- Observed fraction: `1.000000`
- Device: `mps`
- SSL final loss: `0.472596`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a5_w0p35 | 0.620908 | 0.674212 | 0.680441 | 0.669273 | 0.568098 | 0.575055 | 0.533860 | 0.645414 |
| transformer_ridge_resid_a20_w0p35 | 0.621823 | 0.674063 | 0.684066 | 0.670353 | 0.570436 | 0.575898 | 0.530685 | 0.647259 |
| transformer_logreg_c0p3_w0p35 | 0.622022 | 0.672865 | 0.676151 | 0.667350 | 0.573192 | 0.577246 | 0.531264 | 0.656087 |
| transformer_ridge_resid_a1_w0p2 | 0.622194 | 0.672175 | 0.685628 | 0.670515 | 0.569470 | 0.575183 | 0.537822 | 0.644561 |
| transformer_ridge_resid_a5_w0p2 | 0.622424 | 0.672467 | 0.688578 | 0.671462 | 0.570282 | 0.575711 | 0.533271 | 0.645196 |
| transformer_logreg_c0p3_w0p2 | 0.622613 | 0.671641 | 0.686083 | 0.670241 | 0.572494 | 0.575995 | 0.531264 | 0.650574 |
| transformer_logreg_c0p1_w0p35 | 0.623192 | 0.672974 | 0.678997 | 0.667733 | 0.574081 | 0.578299 | 0.533105 | 0.657151 |
| transformer_ridge_resid_a20_w0p2 | 0.623346 | 0.672842 | 0.691190 | 0.672370 | 0.571871 | 0.576697 | 0.531886 | 0.646568 |

## Target-Wise Selection

- Target-wise avg logloss: `0.619042`
- Drift vs reference: `0.096649`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.671641 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.676151 |
| Q3 | transformer_logreg_c0p3_w0p35 | 0.667350 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.567847 |
| S2 | transformer_ridge_resid_a5_w0p35 | 0.575055 |
| S3 | transformer_ridge_resid_a20_w0p35 | 0.530685 |
| S4 | transformer_ridge_resid_a1_w0p2 | 0.644561 |