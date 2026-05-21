# Channel Patch Transformer - full

## Representation

- Tensor: `values/masks [days=700, channels=110, tokens=48]`
- Patch length: `2`
- Patches per channel: `24`
- Observed fraction: `0.886050`
- Device: `mps`
- SSL final loss: `0.548379`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p2 | 0.623211 | 0.670609 | 0.692209 | 0.674787 | 0.571018 | 0.573577 | 0.530698 | 0.649579 |
| transformer_ridge_resid_a5_w0p35 | 0.623326 | 0.672795 | 0.689752 | 0.675104 | 0.571190 | 0.573974 | 0.530022 | 0.650447 |
| transformer_logreg_c0p3_w0p2 | 0.623770 | 0.671594 | 0.689356 | 0.671633 | 0.573951 | 0.575738 | 0.530945 | 0.653173 |
| transformer_ridge_resid_a5_w0p2 | 0.623792 | 0.671798 | 0.693359 | 0.674471 | 0.572207 | 0.575187 | 0.531369 | 0.648151 |
| transformer_ridge_resid_a20_w0p35 | 0.623863 | 0.673373 | 0.690137 | 0.673595 | 0.572334 | 0.576151 | 0.531527 | 0.649922 |
| transformer_ridge_resid_a1_w0p35 | 0.624034 | 0.672642 | 0.688604 | 0.677059 | 0.571075 | 0.574845 | 0.530104 | 0.653906 |
| transformer_logreg_c0p1_w0p2 | 0.624126 | 0.671934 | 0.690635 | 0.671598 | 0.573790 | 0.576275 | 0.531839 | 0.652809 |
| transformer_logreg_c0p3_w0p35 | 0.624226 | 0.672848 | 0.682605 | 0.669997 | 0.575722 | 0.576742 | 0.530954 | 0.660712 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620647`
- Drift vs reference: `0.088246`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_ridge_resid_a1_w0p2 | 0.670609 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.682605 |
| Q3 | transformer_logreg_c0p1_w0p35 | 0.669424 |
| S1 | transformer_ridge_resid_a1_w0p2 | 0.571018 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.573577 |
| S3 | transformer_ridge_resid_a5_w0p35 | 0.530022 |
| S4 | subject_prior_a8 | 0.647272 |