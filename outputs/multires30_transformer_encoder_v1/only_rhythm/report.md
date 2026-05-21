# Hourly Transformer Encoder - only_rhythm

## Representation

- Days: `700`
- Token shape: `48 x 99`
- Base hourly features selected: `23`
- Mean token missing fraction: `0.235066`
- Device: `mps`
- SSL final loss: `0.377078`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p05 | 0.627214 | 0.671099 | 0.700172 | 0.678621 | 0.577302 | 0.578784 | 0.534198 | 0.650322 |
| transformer_logreg_c0p1_w0p05 | 0.627308 | 0.671361 | 0.700803 | 0.678284 | 0.576910 | 0.579069 | 0.534831 | 0.649902 |
| transformer_logreg_c0p3_w0p1 | 0.627360 | 0.669515 | 0.695933 | 0.679891 | 0.579368 | 0.578677 | 0.534317 | 0.653817 |
| transformer_logreg_c0p03_w0p05 | 0.627395 | 0.671680 | 0.701496 | 0.677854 | 0.576511 | 0.579416 | 0.535371 | 0.649435 |
| transformer_logreg_c0p1_w0p1 | 0.627460 | 0.669942 | 0.697077 | 0.679121 | 0.578518 | 0.579164 | 0.535472 | 0.652925 |
| transformer_logreg_c0p03_w0p1 | 0.627567 | 0.670508 | 0.698372 | 0.678179 | 0.577679 | 0.579775 | 0.536511 | 0.651947 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627832 | 0.672332 | 0.702360 | 0.679344 | 0.577854 | 0.579370 | 0.533916 | 0.649647 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622599`
- Drift vs reference: `0.068967`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.667699 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.682704 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_logreg_c0p3_w0p1 | 0.578677 |
| S3 | transformer_ridge_resid_a1_w0p1 | 0.532316 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.