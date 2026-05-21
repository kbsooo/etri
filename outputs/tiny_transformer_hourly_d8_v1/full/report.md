# Hourly Transformer Encoder - full

## Representation

- Encoder type: `transformer`
- Encoder params: `4847`
- Days: `700`
- Token shape: `24 x 215`
- Base hourly features selected: `52`
- Mean token missing fraction: `0.191884`
- Device: `mps`
- SSL final loss: `0.634570`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626964 | 0.672241 | 0.698644 | 0.675769 | 0.576374 | 0.580388 | 0.537449 | 0.647880 |
| transformer_logreg_c0p3_w0p05 | 0.627123 | 0.672574 | 0.701651 | 0.676681 | 0.575848 | 0.579847 | 0.535833 | 0.647426 |
| transformer_logreg_c0p1_w0p1 | 0.627133 | 0.672225 | 0.699175 | 0.675892 | 0.576547 | 0.580651 | 0.537549 | 0.647894 |
| transformer_logreg_c0p1_w0p05 | 0.627216 | 0.672571 | 0.701933 | 0.676750 | 0.575938 | 0.579992 | 0.535888 | 0.647438 |
| transformer_logreg_c0p03_w0p05 | 0.627330 | 0.672645 | 0.702350 | 0.676751 | 0.575981 | 0.580117 | 0.536001 | 0.647467 |
| transformer_logreg_c0p03_w0p1 | 0.627342 | 0.672364 | 0.699965 | 0.675883 | 0.576620 | 0.580875 | 0.537755 | 0.647936 |
| transformer_ridge_resid_a1_w0p2 | 0.627377 | 0.674799 | 0.701925 | 0.677861 | 0.575015 | 0.579439 | 0.534031 | 0.648569 |
| transformer_ridge_resid_a1_w0p1 | 0.627395 | 0.673869 | 0.703198 | 0.677692 | 0.575266 | 0.579564 | 0.534355 | 0.647821 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624104`
- Drift vs reference: `0.066923`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.688142 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673687 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.574981 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.579439 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.