# Channel Patch Transformer - only_rhythm

## Representation

- Tensor: `values/masks [days=700, channels=37, tokens=48]`
- Patch length: `4`
- Patches per channel: `12`
- Observed fraction: `0.842062`
- Device: `mps`
- SSL final loss: `0.698634`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a20_w0p35 | 0.623803 | 0.674873 | 0.688885 | 0.670003 | 0.573865 | 0.577710 | 0.529750 | 0.651538 |
| transformer_ridge_resid_a5_w0p35 | 0.623903 | 0.674727 | 0.690665 | 0.672758 | 0.572857 | 0.577441 | 0.528553 | 0.650318 |
| transformer_logreg_c0p3_w0p2 | 0.623903 | 0.672600 | 0.689269 | 0.669557 | 0.575209 | 0.576486 | 0.530915 | 0.653284 |
| transformer_ridge_resid_a5_w0p2 | 0.624154 | 0.672809 | 0.694135 | 0.673125 | 0.573254 | 0.577136 | 0.530383 | 0.648236 |
| transformer_logreg_c0p1_w0p2 | 0.624255 | 0.672701 | 0.689912 | 0.669423 | 0.575110 | 0.576897 | 0.532688 | 0.653052 |
| transformer_logreg_c0p3_w0p35 | 0.624257 | 0.674563 | 0.681796 | 0.666343 | 0.577557 | 0.578151 | 0.530693 | 0.660697 |
| transformer_ridge_resid_a1_w0p2 | 0.624338 | 0.671460 | 0.693607 | 0.675462 | 0.572517 | 0.577649 | 0.531057 | 0.648612 |
| transformer_logreg_c0p1_w0p35 | 0.624411 | 0.674185 | 0.682036 | 0.665608 | 0.577144 | 0.578402 | 0.533575 | 0.659927 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620471`
- Drift vs reference: `0.098322`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_ridge_resid_a1_w0p2 | 0.671460 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.681796 |
| Q3 | transformer_logreg_c0p1_w0p35 | 0.665608 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.572121 |
| S2 | transformer_logreg_c0p3_w0p2 | 0.576486 |
| S3 | transformer_ridge_resid_a5_w0p35 | 0.528553 |
| S4 | subject_prior_a8 | 0.647272 |