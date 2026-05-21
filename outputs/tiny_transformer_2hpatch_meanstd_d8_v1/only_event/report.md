# Hourly Transformer Encoder - only_event

## Representation

- Encoder type: `transformer`
- Encoder params: `7454`
- Days: `700`
- Token shape: `12 x 374`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean_std`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.210269`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.627091 | 0.672427 | 0.699447 | 0.676076 | 0.577692 | 0.579916 | 0.537146 | 0.646937 |
| transformer_logreg_c0p1_w0p1 | 0.627116 | 0.672214 | 0.699571 | 0.675895 | 0.577480 | 0.580085 | 0.537681 | 0.646887 |
| transformer_logreg_c0p03_w0p1 | 0.627169 | 0.672012 | 0.699761 | 0.675696 | 0.577267 | 0.580329 | 0.538172 | 0.646949 |
| transformer_logreg_c0p3_w0p05 | 0.627205 | 0.672677 | 0.702078 | 0.676856 | 0.576537 | 0.579638 | 0.535703 | 0.646944 |
| transformer_logreg_c0p1_w0p05 | 0.627220 | 0.672569 | 0.702144 | 0.676766 | 0.576431 | 0.579725 | 0.535981 | 0.646925 |
| transformer_logreg_c0p03_w0p05 | 0.627249 | 0.672467 | 0.702243 | 0.676665 | 0.576324 | 0.579850 | 0.536233 | 0.646961 |
| transformer_ridge_resid_a20_w0p2 | 0.627398 | 0.673610 | 0.703484 | 0.678382 | 0.578239 | 0.578308 | 0.533915 | 0.645850 |
| transformer_ridge_resid_a20_w0p1 | 0.627457 | 0.673326 | 0.704119 | 0.678056 | 0.576916 | 0.579027 | 0.534264 | 0.646494 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623735`
- Drift vs reference: `0.065921`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671785 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.690291 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.672783 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a20_w0p35 | 0.577427 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a20_w0p35 | 0.645127 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.