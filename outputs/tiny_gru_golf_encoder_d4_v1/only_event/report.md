# Hourly Transformer Encoder - only_event

## Representation

- Encoder type: `gru`
- Encoder params: `1843`
- Days: `700`
- Token shape: `48 x 187`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.539109`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p05 | 0.627367 | 0.672403 | 0.702515 | 0.676623 | 0.576137 | 0.580186 | 0.536454 | 0.647248 |
| transformer_logreg_c0p1_w0p05 | 0.627374 | 0.672405 | 0.702522 | 0.676623 | 0.576087 | 0.580191 | 0.536523 | 0.647266 |
| transformer_logreg_c0p03_w0p05 | 0.627381 | 0.672414 | 0.702560 | 0.676606 | 0.576003 | 0.580189 | 0.536611 | 0.647282 |
| transformer_logreg_c0p3_w0p1 | 0.627407 | 0.671887 | 0.700311 | 0.675628 | 0.576931 | 0.580994 | 0.538593 | 0.647508 |
| transformer_logreg_c0p1_w0p1 | 0.627417 | 0.671886 | 0.700318 | 0.675625 | 0.576828 | 0.581002 | 0.538721 | 0.647538 |
| transformer_logreg_c0p03_w0p1 | 0.627424 | 0.671897 | 0.700383 | 0.675585 | 0.576655 | 0.580993 | 0.538892 | 0.647565 |
| transformer_ridge_resid_a1_w0p1 | 0.627549 | 0.673019 | 0.704418 | 0.677896 | 0.575839 | 0.580077 | 0.534520 | 0.647072 |
| transformer_ridge_resid_a1_w0p2 | 0.627549 | 0.672973 | 0.704033 | 0.678108 | 0.576077 | 0.580326 | 0.534365 | 0.646960 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624659`
- Drift vs reference: `0.066635`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671532 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.693017 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.672515 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p2 | 0.646960 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.