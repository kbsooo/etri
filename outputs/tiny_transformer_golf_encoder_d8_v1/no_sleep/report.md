# Hourly Transformer Encoder - no_sleep

## Representation

- Days: `700`
- Token shape: `48 x 335`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.513267`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a1_w0p35 | 0.626481 | 0.676234 | 0.700497 | 0.680098 | 0.574996 | 0.575159 | 0.533822 | 0.644562 |
| transformer_ridge_resid_a5_w0p35 | 0.626488 | 0.675110 | 0.700864 | 0.679935 | 0.575541 | 0.575159 | 0.533891 | 0.644917 |
| transformer_ridge_resid_a1_w0p2 | 0.626622 | 0.674800 | 0.701816 | 0.679002 | 0.574981 | 0.576769 | 0.533717 | 0.645271 |
| transformer_ridge_resid_a20_w0p35 | 0.626667 | 0.674499 | 0.701474 | 0.679816 | 0.576079 | 0.575446 | 0.533803 | 0.645548 |
| transformer_ridge_resid_a5_w0p2 | 0.626703 | 0.674195 | 0.702122 | 0.678923 | 0.575351 | 0.576823 | 0.533872 | 0.645638 |
| transformer_ridge_resid_a20_w0p2 | 0.626864 | 0.673864 | 0.702546 | 0.678861 | 0.575702 | 0.577076 | 0.533896 | 0.646104 |
| transformer_logreg_c0p3_w0p1 | 0.626901 | 0.672419 | 0.699966 | 0.676116 | 0.576649 | 0.578963 | 0.537185 | 0.647012 |
| transformer_logreg_c0p1_w0p1 | 0.626980 | 0.672377 | 0.700013 | 0.676022 | 0.576817 | 0.579152 | 0.537317 | 0.647162 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623671`
- Drift vs reference: `0.067414`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.692406 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673381 |
| S1 | transformer_ridge_resid_a1_w0p2 | 0.574981 |
| S2 | transformer_ridge_resid_a5_w0p35 | 0.575159 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.644562 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.