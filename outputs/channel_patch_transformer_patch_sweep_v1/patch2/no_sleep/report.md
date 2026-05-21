# Channel Patch Transformer - no_sleep

## Representation

- Tensor: `values/masks [days=700, channels=87, tokens=48]`
- Patch length: `2`
- Patches per channel: `24`
- Observed fraction: `0.918565`
- Device: `mps`
- SSL final loss: `0.544799`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a5_w0p35 | 0.622732 | 0.675987 | 0.687194 | 0.667258 | 0.569527 | 0.576805 | 0.533650 | 0.648703 |
| transformer_ridge_resid_a1_w0p2 | 0.623097 | 0.674535 | 0.689910 | 0.668377 | 0.569816 | 0.576432 | 0.533941 | 0.648665 |
| transformer_ridge_resid_a1_w0p35 | 0.623152 | 0.678475 | 0.684384 | 0.664687 | 0.567533 | 0.577475 | 0.537217 | 0.652288 |
| transformer_ridge_resid_a20_w0p35 | 0.623327 | 0.675219 | 0.687594 | 0.668709 | 0.572315 | 0.577534 | 0.533254 | 0.648665 |
| transformer_ridge_resid_a5_w0p2 | 0.623496 | 0.673692 | 0.692195 | 0.670467 | 0.571157 | 0.576751 | 0.533092 | 0.647116 |
| transformer_logreg_c0p3_w0p2 | 0.623516 | 0.673412 | 0.687150 | 0.669638 | 0.573346 | 0.576639 | 0.532307 | 0.652118 |
| transformer_logreg_c0p3_w0p35 | 0.623612 | 0.675674 | 0.678317 | 0.666135 | 0.574901 | 0.578292 | 0.533177 | 0.658787 |
| transformer_ridge_resid_a20_w0p2 | 0.624167 | 0.673601 | 0.693062 | 0.671559 | 0.572871 | 0.577546 | 0.533090 | 0.647438 |

## Target-Wise Selection

- Target-wise avg logloss: `0.619763`
- Drift vs reference: `0.095294`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.678317 |
| Q3 | transformer_ridge_resid_a1_w0p35 | 0.664687 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.567533 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.576432 |
| S3 | transformer_logreg_c0p3_w0p2 | 0.532307 |
| S4 | transformer_ridge_resid_a5_w0p1 | 0.646889 |