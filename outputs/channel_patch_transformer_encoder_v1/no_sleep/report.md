# Channel Patch Transformer - no_sleep

## Representation

- Tensor: `values/masks [days=700, channels=87, tokens=48]`
- Patch length: `4`
- Patches per channel: `12`
- Observed fraction: `0.918565`
- Device: `mps`
- SSL final loss: `0.571212`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p2 | 0.623416 | 0.673832 | 0.687038 | 0.668974 | 0.573423 | 0.576212 | 0.532886 | 0.651544 |
| transformer_logreg_c0p3_w0p35 | 0.623572 | 0.676797 | 0.678440 | 0.665216 | 0.574783 | 0.577641 | 0.534283 | 0.657842 |
| transformer_ridge_resid_a20_w0p2 | 0.623954 | 0.674105 | 0.691907 | 0.671474 | 0.572253 | 0.576697 | 0.534495 | 0.646743 |
| transformer_logreg_c0p1_w0p2 | 0.623964 | 0.673999 | 0.686971 | 0.668832 | 0.573693 | 0.577507 | 0.534881 | 0.651862 |
| transformer_logreg_c0p1_w0p35 | 0.624059 | 0.676550 | 0.677586 | 0.664566 | 0.574897 | 0.579297 | 0.537523 | 0.657998 |
| transformer_ridge_resid_a5_w0p2 | 0.624154 | 0.674165 | 0.693290 | 0.671499 | 0.571382 | 0.574465 | 0.538502 | 0.645777 |
| transformer_logreg_c0p3_w0p1 | 0.624854 | 0.673037 | 0.695070 | 0.672814 | 0.573955 | 0.577097 | 0.533211 | 0.648792 |
| transformer_logreg_c0p03_w0p2 | 0.624886 | 0.674120 | 0.688306 | 0.669566 | 0.574232 | 0.578768 | 0.537412 | 0.651800 |

## Target-Wise Selection

- Target-wise avg logloss: `0.618767`
- Drift vs reference: `0.100180`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.677586 |
| Q3 | transformer_logreg_c0p1_w0p35 | 0.664566 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.569332 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.569299 |
| S3 | transformer_logreg_c0p3_w0p2 | 0.532886 |
| S4 | transformer_ridge_resid_a1_w0p2 | 0.645522 |