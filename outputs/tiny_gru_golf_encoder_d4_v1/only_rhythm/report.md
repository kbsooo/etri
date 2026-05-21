# Hourly Transformer Encoder - only_rhythm

## Representation

- Encoder type: `gru`
- Encoder params: `1339`
- Days: `700`
- Token shape: `48 x 131`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `0.670799`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p35 | 0.626842 | 0.672344 | 0.705008 | 0.679404 | 0.576314 | 0.576159 | 0.536072 | 0.642590 |
| transformer_ridge_resid_a5_w0p35 | 0.626853 | 0.672333 | 0.704999 | 0.679387 | 0.576238 | 0.576239 | 0.536040 | 0.642732 |
| transformer_ridge_resid_a20_w0p35 | 0.626895 | 0.672313 | 0.704978 | 0.679329 | 0.576006 | 0.576507 | 0.535937 | 0.643197 |
| transformer_ridge_resid_a1_w0p2 | 0.626999 | 0.672480 | 0.704760 | 0.678656 | 0.575824 | 0.577493 | 0.535468 | 0.644313 |
| transformer_ridge_resid_a5_w0p2 | 0.627013 | 0.672484 | 0.704762 | 0.678648 | 0.575786 | 0.577553 | 0.535451 | 0.644411 |
| transformer_ridge_resid_a20_w0p2 | 0.627062 | 0.672503 | 0.704770 | 0.678619 | 0.575673 | 0.577749 | 0.535396 | 0.644724 |
| transformer_logreg_c0p3_w0p1 | 0.627227 | 0.671513 | 0.700330 | 0.675969 | 0.577114 | 0.580086 | 0.539256 | 0.646322 |
| transformer_logreg_c0p1_w0p1 | 0.627256 | 0.671617 | 0.700374 | 0.675902 | 0.576980 | 0.580212 | 0.539213 | 0.646497 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623478`
- Drift vs reference: `0.067552`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p2 | 0.670810 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.693083 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673054 |
| S1 | transformer_ridge_resid_a20_w0p1 | 0.575620 |
| S2 | transformer_ridge_resid_a1_w0p35 | 0.576159 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.642590 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.