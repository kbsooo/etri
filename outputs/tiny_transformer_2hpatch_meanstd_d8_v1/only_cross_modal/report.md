# Hourly Transformer Encoder - only_cross_modal

## Representation

- Encoder type: `transformer`
- Encoder params: `4326`
- Days: `700`
- Token shape: `12 x 190`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean_std`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.185118`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626912 | 0.671442 | 0.696562 | 0.676498 | 0.577879 | 0.580106 | 0.538344 | 0.647551 |
| transformer_logreg_c0p1_w0p1 | 0.626988 | 0.671520 | 0.697010 | 0.676238 | 0.577710 | 0.580287 | 0.538559 | 0.647593 |
| transformer_ridge_resid_a1_w0p2 | 0.626993 | 0.672304 | 0.699563 | 0.680108 | 0.577685 | 0.579790 | 0.534106 | 0.645396 |
| transformer_ridge_resid_a5_w0p2 | 0.627079 | 0.672517 | 0.699408 | 0.679753 | 0.577486 | 0.579834 | 0.534275 | 0.646279 |
| transformer_logreg_c0p03_w0p1 | 0.627081 | 0.671585 | 0.697776 | 0.675977 | 0.577396 | 0.580548 | 0.538630 | 0.647658 |
| transformer_ridge_resid_a20_w0p2 | 0.627097 | 0.672821 | 0.699434 | 0.679238 | 0.577141 | 0.579773 | 0.534725 | 0.646543 |
| transformer_logreg_c0p3_w0p05 | 0.627102 | 0.672174 | 0.700567 | 0.677063 | 0.576612 | 0.579724 | 0.536314 | 0.647259 |
| transformer_logreg_c0p1_w0p05 | 0.627147 | 0.672216 | 0.700800 | 0.676933 | 0.576528 | 0.579825 | 0.536436 | 0.647289 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622773`
- Drift vs reference: `0.067951`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.670719 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.681888 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673813 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_logreg_c0p3_w0p05 | 0.579724 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.644532 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.