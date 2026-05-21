# Hourly Transformer Encoder - no_phone

## Representation

- Days: `700`
- Token shape: `24 x 99`
- Base hourly features selected: `46`
- Mean token missing fraction: `0.208402`
- Device: `mps`
- SSL final loss: `0.271903`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626431 | 0.671957 | 0.695514 | 0.677643 | 0.576264 | 0.580775 | 0.533747 | 0.649116 |
| transformer_logreg_c0p1_w0p1 | 0.626513 | 0.672282 | 0.696470 | 0.677538 | 0.576325 | 0.580658 | 0.533698 | 0.648619 |
| transformer_logreg_c0p03_w0p1 | 0.626725 | 0.672365 | 0.697620 | 0.677300 | 0.576406 | 0.580807 | 0.534117 | 0.648462 |
| transformer_logreg_c0p3_w0p05 | 0.626774 | 0.672349 | 0.699914 | 0.677560 | 0.575711 | 0.579940 | 0.533994 | 0.647950 |
| transformer_logreg_c0p1_w0p05 | 0.626847 | 0.672543 | 0.700444 | 0.677536 | 0.575777 | 0.579917 | 0.533975 | 0.647739 |
| transformer_logreg_c0p03_w0p05 | 0.626985 | 0.672610 | 0.701069 | 0.677440 | 0.575843 | 0.580043 | 0.534194 | 0.647694 |
| transformer_logreg_c0p1_w0p2 | 0.627079 | 0.672811 | 0.690134 | 0.678228 | 0.578681 | 0.583658 | 0.534515 | 0.651529 |
| transformer_logreg_c0p3_w0p2 | 0.627168 | 0.672421 | 0.688597 | 0.678660 | 0.578826 | 0.584167 | 0.534694 | 0.652811 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623444`
- Drift vs reference: `0.067577`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p3_w0p1 | 0.671957 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.682492 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | transformer_ridge_resid_a20_w0p2 | 0.533009 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.