# Channel Patch Transformer - no_sleep

## Representation

- Tensor: `values/masks [days=700, channels=87, tokens=48]`
- Patch length: `8`
- Patches per channel: `6`
- Observed fraction: `0.918565`
- Device: `mps`
- SSL final loss: `0.615370`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p2 | 0.623808 | 0.676655 | 0.691869 | 0.673346 | 0.572312 | 0.574608 | 0.528767 | 0.649102 |
| transformer_ridge_resid_a5_w0p35 | 0.624242 | 0.677310 | 0.690384 | 0.675460 | 0.572342 | 0.574702 | 0.527793 | 0.651701 |
| transformer_ridge_resid_a5_w0p2 | 0.624287 | 0.674525 | 0.693468 | 0.674937 | 0.572765 | 0.575644 | 0.529649 | 0.649021 |
| transformer_logreg_c0p3_w0p2 | 0.624586 | 0.673511 | 0.688422 | 0.673102 | 0.574398 | 0.575772 | 0.532448 | 0.654451 |
| transformer_ridge_resid_a20_w0p35 | 0.624734 | 0.675897 | 0.688623 | 0.675865 | 0.574179 | 0.576259 | 0.529900 | 0.652416 |
| transformer_ridge_resid_a20_w0p2 | 0.624937 | 0.674025 | 0.693354 | 0.675483 | 0.573805 | 0.576902 | 0.531412 | 0.649575 |
| transformer_ridge_resid_a1_w0p1 | 0.624992 | 0.674004 | 0.697211 | 0.674929 | 0.573534 | 0.576640 | 0.530972 | 0.647653 |
| transformer_logreg_c0p1_w0p2 | 0.625064 | 0.673561 | 0.689283 | 0.673358 | 0.574730 | 0.576512 | 0.534499 | 0.653508 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620952`
- Drift vs reference: `0.087176`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.680534 |
| Q3 | transformer_logreg_c0p1_w0p35 | 0.672436 |
| S1 | transformer_ridge_resid_a1_w0p2 | 0.572312 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.574142 |
| S3 | transformer_ridge_resid_a5_w0p35 | 0.527793 |
| S4 | subject_prior_a8 | 0.647272 |