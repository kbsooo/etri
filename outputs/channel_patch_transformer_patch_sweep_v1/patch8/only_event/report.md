# Channel Patch Transformer - only_event

## Representation

- Tensor: `values/masks [days=700, channels=45, tokens=48]`
- Patch length: `8`
- Patches per channel: `6`
- Observed fraction: `1.000000`
- Device: `mps`
- SSL final loss: `0.513430`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p2 | 0.625007 | 0.672739 | 0.690419 | 0.672321 | 0.573964 | 0.578008 | 0.533809 | 0.653790 |
| transformer_logreg_c0p1_w0p2 | 0.625126 | 0.672745 | 0.689818 | 0.672033 | 0.573920 | 0.578648 | 0.534963 | 0.653758 |
| transformer_ridge_resid_a20_w0p2 | 0.625337 | 0.673466 | 0.694893 | 0.674247 | 0.572541 | 0.578778 | 0.534243 | 0.649190 |
| transformer_ridge_resid_a20_w0p35 | 0.625487 | 0.675185 | 0.691300 | 0.673944 | 0.571659 | 0.579981 | 0.534778 | 0.651563 |
| transformer_ridge_resid_a5_w0p2 | 0.625637 | 0.674328 | 0.695958 | 0.674582 | 0.572661 | 0.577674 | 0.536005 | 0.648249 |
| transformer_logreg_c0p03_w0p2 | 0.625648 | 0.672983 | 0.690925 | 0.672212 | 0.574227 | 0.579264 | 0.536973 | 0.652953 |
| transformer_logreg_c0p3_w0p1 | 0.625673 | 0.672527 | 0.696753 | 0.674475 | 0.574251 | 0.578042 | 0.533695 | 0.649968 |
| transformer_logreg_c0p1_w0p1 | 0.625819 | 0.672608 | 0.696626 | 0.674421 | 0.574293 | 0.578447 | 0.534318 | 0.650023 |

## Target-Wise Selection

- Target-wise avg logloss: `0.621840`
- Drift vs reference: `0.075592`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.682477 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.670024 |
| S1 | transformer_ridge_resid_a20_w0p35 | 0.571659 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.576326 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p05 | 0.647188 |