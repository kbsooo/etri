# Hourly Transformer Encoder - only_rhythm

## Representation

- Encoder type: `transformer`
- Encoder params: `2875`
- Days: `700`
- Token shape: `24 x 99`
- Base hourly features selected: `23`
- Mean token missing fraction: `0.314130`
- Device: `mps`
- SSL final loss: `0.685259`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626964 | 0.672013 | 0.699638 | 0.675209 | 0.576078 | 0.579826 | 0.539353 | 0.646630 |
| transformer_logreg_c0p1_w0p1 | 0.627012 | 0.671972 | 0.699891 | 0.675316 | 0.576240 | 0.579770 | 0.539202 | 0.646690 |
| transformer_logreg_c0p3_w0p05 | 0.627113 | 0.672472 | 0.702152 | 0.676415 | 0.575667 | 0.579549 | 0.536765 | 0.646770 |
| transformer_logreg_c0p1_w0p05 | 0.627146 | 0.672454 | 0.702291 | 0.676471 | 0.575760 | 0.579530 | 0.536708 | 0.646811 |
| transformer_logreg_c0p03_w0p1 | 0.627157 | 0.672018 | 0.700271 | 0.675458 | 0.576583 | 0.579842 | 0.539097 | 0.646828 |
| transformer_ridge_resid_a20_w0p2 | 0.627167 | 0.674155 | 0.704186 | 0.677680 | 0.575225 | 0.577951 | 0.536217 | 0.644756 |
| transformer_logreg_c0p03_w0p05 | 0.627231 | 0.672480 | 0.702498 | 0.676544 | 0.575949 | 0.579579 | 0.536677 | 0.646892 |
| transformer_ridge_resid_a5_w0p2 | 0.627268 | 0.674449 | 0.703602 | 0.677683 | 0.575453 | 0.578253 | 0.536736 | 0.644699 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623310`
- Drift vs reference: `0.067350`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p1_w0p2 | 0.671667 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.691443 |
| Q3 | transformer_logreg_c0p3_w0p35 | 0.671298 |
| S1 | transformer_ridge_resid_a20_w0p2 | 0.575225 |
| S2 | transformer_ridge_resid_a20_w0p35 | 0.577115 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a5_w0p35 | 0.643391 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.