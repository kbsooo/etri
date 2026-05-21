# Hourly Transformer Encoder - only_cross_modal

## Representation

- Encoder type: `gru`
- Encoder params: `527`
- Days: `700`
- Token shape: `48 x 95`
- Base hourly features selected: `22`
- Mean token missing fraction: `0.068051`
- Device: `mps`
- SSL final loss: `0.952805`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627362 | 0.672646 | 0.702941 | 0.676405 | 0.575865 | 0.580098 | 0.536534 | 0.647046 |
| transformer_logreg_c0p1_w0p05 | 0.627365 | 0.672664 | 0.702949 | 0.676409 | 0.575865 | 0.580101 | 0.536538 | 0.647029 |
| transformer_logreg_c0p3_w0p05 | 0.627366 | 0.672670 | 0.702952 | 0.676410 | 0.575865 | 0.580102 | 0.536539 | 0.647023 |
| transformer_logreg_c0p03_w0p1 | 0.627392 | 0.672377 | 0.701112 | 0.675184 | 0.576371 | 0.580826 | 0.538772 | 0.647103 |
| transformer_logreg_c0p1_w0p1 | 0.627399 | 0.672416 | 0.701128 | 0.675192 | 0.576371 | 0.580833 | 0.538782 | 0.647072 |
| transformer_logreg_c0p3_w0p1 | 0.627401 | 0.672428 | 0.701133 | 0.675195 | 0.576372 | 0.580835 | 0.538785 | 0.647061 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_ridge_resid_a20_w0p05 | 0.627684 | 0.673392 | 0.705119 | 0.677814 | 0.575702 | 0.579926 | 0.534730 | 0.647105 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624756`
- Drift vs reference: `0.064587`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.695100 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.671132 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.646295 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.