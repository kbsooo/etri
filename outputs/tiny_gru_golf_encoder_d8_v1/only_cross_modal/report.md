# Hourly Transformer Encoder - only_cross_modal

## Representation

- Encoder type: `gru`
- Encoder params: `2159`
- Days: `700`
- Token shape: `48 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.376127`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.627059 | 0.672773 | 0.699160 | 0.675939 | 0.576447 | 0.581193 | 0.537320 | 0.646584 |
| transformer_logreg_c0p1_w0p1 | 0.627096 | 0.672648 | 0.699245 | 0.676046 | 0.576530 | 0.581056 | 0.537530 | 0.646615 |
| transformer_ridge_resid_a20_w0p2 | 0.627106 | 0.674458 | 0.701117 | 0.679155 | 0.574699 | 0.581219 | 0.533139 | 0.645957 |
| transformer_ridge_resid_a5_w0p2 | 0.627128 | 0.674743 | 0.701133 | 0.678911 | 0.574556 | 0.581502 | 0.532963 | 0.646087 |
| transformer_ridge_resid_a1_w0p2 | 0.627144 | 0.674862 | 0.701166 | 0.678801 | 0.574513 | 0.581614 | 0.532907 | 0.646146 |
| transformer_logreg_c0p03_w0p1 | 0.627170 | 0.672487 | 0.699556 | 0.676016 | 0.576588 | 0.580898 | 0.537945 | 0.646697 |
| transformer_logreg_c0p3_w0p05 | 0.627183 | 0.672853 | 0.701896 | 0.676779 | 0.575890 | 0.580289 | 0.535814 | 0.646760 |
| transformer_ridge_resid_a20_w0p35 | 0.627201 | 0.675679 | 0.699249 | 0.680452 | 0.574486 | 0.582543 | 0.532479 | 0.645522 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624042`
- Drift vs reference: `0.066484`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.690301 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.574339 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | transformer_ridge_resid_a1_w0p35 | 0.532273 |
| S4 | transformer_ridge_resid_a20_w0p35 | 0.645522 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.