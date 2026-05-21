# Hourly Transformer Encoder - no_sleep

## Representation

- Days: `700`
- Token shape: `48 x 335`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.314283`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p1 | 0.626434 | 0.673801 | 0.698112 | 0.677624 | 0.575853 | 0.577530 | 0.532548 | 0.649568 |
| transformer_logreg_c0p03_w0p1 | 0.626471 | 0.673314 | 0.698217 | 0.677156 | 0.576194 | 0.578146 | 0.533269 | 0.648999 |
| transformer_logreg_c0p3_w0p1 | 0.626606 | 0.674317 | 0.698104 | 0.678102 | 0.575616 | 0.577382 | 0.532455 | 0.650264 |
| transformer_logreg_c0p03_w0p2 | 0.626691 | 0.674543 | 0.692885 | 0.677325 | 0.577913 | 0.578403 | 0.533662 | 0.652108 |
| transformer_logreg_c0p1_w0p05 | 0.626823 | 0.673320 | 0.701328 | 0.677573 | 0.575592 | 0.578388 | 0.533356 | 0.648202 |
| transformer_logreg_c0p1_w0p2 | 0.626859 | 0.675722 | 0.692991 | 0.678456 | 0.577426 | 0.577400 | 0.532514 | 0.653505 |
| transformer_ridge_resid_a20_w0p1 | 0.626873 | 0.675296 | 0.701173 | 0.679155 | 0.574700 | 0.578717 | 0.531183 | 0.647885 |
| transformer_logreg_c0p3_w0p05 | 0.626873 | 0.673547 | 0.701287 | 0.677786 | 0.575437 | 0.578287 | 0.533263 | 0.648502 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622582`
- Drift vs reference: `0.073262`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.687422 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a1_w0p1 | 0.573624 |
| S2 | transformer_logreg_c0p3_w0p2 | 0.577338 |
| S3 | transformer_ridge_resid_a20_w0p35 | 0.526417 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.