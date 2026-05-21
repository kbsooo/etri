# Hourly Transformer Encoder - full

## Representation

- Days: `700`
- Token shape: `24 x 111`
- Base hourly features selected: `52`
- Mean token missing fraction: `0.191884`
- Device: `mps`
- SSL final loss: `0.283291`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.626318 | 0.670979 | 0.697052 | 0.675543 | 0.577120 | 0.580585 | 0.533393 | 0.649556 |
| transformer_logreg_c0p1_w0p1 | 0.626347 | 0.671579 | 0.696855 | 0.674880 | 0.577768 | 0.580478 | 0.533809 | 0.649062 |
| transformer_logreg_c0p03_w0p1 | 0.626542 | 0.671886 | 0.697354 | 0.674739 | 0.577806 | 0.580641 | 0.534455 | 0.648914 |
| transformer_logreg_c0p3_w0p05 | 0.626701 | 0.671828 | 0.700736 | 0.676413 | 0.576197 | 0.579832 | 0.533711 | 0.648189 |
| transformer_logreg_c0p1_w0p05 | 0.626755 | 0.672162 | 0.700672 | 0.676126 | 0.576554 | 0.579824 | 0.533984 | 0.647966 |
| transformer_logreg_c0p1_w0p2 | 0.626830 | 0.671609 | 0.690688 | 0.673518 | 0.581221 | 0.583412 | 0.534978 | 0.652387 |
| transformer_logreg_c0p03_w0p05 | 0.626889 | 0.672349 | 0.700964 | 0.676106 | 0.576596 | 0.579940 | 0.534355 | 0.647915 |
| transformer_ridge_resid_a20_w0p1 | 0.626898 | 0.671848 | 0.700345 | 0.676612 | 0.576801 | 0.580402 | 0.533297 | 0.648984 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622449`
- Drift vs reference: `0.069569`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_ridge_resid_a1_w0p2 | 0.668064 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.684871 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.671984 |
| S1 | transformer_ridge_resid_a1_w0p2 | 0.572181 |
| S2 | transformer_ridge_resid_a1_w0p05 | 0.579739 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.