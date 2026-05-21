# Hourly Transformer Encoder - only_cross_modal

## Representation

- Encoder type: `transformer`
- Encoder params: `2711`
- Days: `700`
- Token shape: `12 x 95`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.243696`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p35 | 0.625355 | 0.673609 | 0.697900 | 0.680857 | 0.578019 | 0.576401 | 0.532905 | 0.637794 |
| transformer_ridge_resid_a5_w0p35 | 0.625370 | 0.674367 | 0.698335 | 0.680350 | 0.578104 | 0.575968 | 0.532715 | 0.637752 |
| transformer_ridge_resid_a20_w0p35 | 0.625640 | 0.675070 | 0.698848 | 0.679769 | 0.578144 | 0.576550 | 0.532761 | 0.638334 |
| transformer_ridge_resid_a1_w0p2 | 0.625894 | 0.673202 | 0.699954 | 0.679435 | 0.576693 | 0.577339 | 0.533374 | 0.641261 |
| transformer_ridge_resid_a5_w0p2 | 0.625966 | 0.673700 | 0.700332 | 0.679156 | 0.576833 | 0.577160 | 0.533299 | 0.641285 |
| transformer_logreg_c0p3_w0p2 | 0.626151 | 0.672305 | 0.692916 | 0.675159 | 0.580253 | 0.578625 | 0.539613 | 0.644187 |
| transformer_ridge_resid_a20_w0p2 | 0.626194 | 0.674142 | 0.700745 | 0.678837 | 0.576949 | 0.577616 | 0.533370 | 0.641702 |
| transformer_logreg_c0p3_w0p1 | 0.626257 | 0.672279 | 0.698146 | 0.676188 | 0.577319 | 0.578469 | 0.536413 | 0.644986 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622174`
- Drift vs reference: `0.070366`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.687613 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673289 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a5_w0p35 | 0.575968 |
| S3 | transformer_ridge_resid_a5_w0p35 | 0.532715 |
| S4 | transformer_ridge_resid_a5_w0p35 | 0.637752 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.