# Hourly Transformer Encoder - only_cross_modal

## Representation

- Days: `700`
- Token shape: `48 x 79`
- Base hourly features selected: `18`
- Mean token missing fraction: `0.083173`
- Device: `mps`
- SSL final loss: `0.224222`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p2 | 0.624121 | 0.673258 | 0.690552 | 0.676139 | 0.571763 | 0.572246 | 0.534957 | 0.649932 |
| transformer_logreg_c0p1_w0p2 | 0.624289 | 0.671318 | 0.689760 | 0.676611 | 0.572920 | 0.573091 | 0.536229 | 0.650096 |
| transformer_ridge_resid_a20_w0p2 | 0.624802 | 0.674781 | 0.695725 | 0.678892 | 0.571523 | 0.575403 | 0.531063 | 0.646224 |
| transformer_logreg_c0p3_w0p1 | 0.624922 | 0.672507 | 0.696481 | 0.676328 | 0.572708 | 0.574840 | 0.533859 | 0.647735 |
| transformer_logreg_c0p03_w0p2 | 0.624956 | 0.670290 | 0.690521 | 0.676648 | 0.573916 | 0.575724 | 0.537872 | 0.649723 |
| transformer_ridge_resid_a5_w0p2 | 0.624981 | 0.677912 | 0.696644 | 0.677700 | 0.571500 | 0.575617 | 0.530481 | 0.645012 |
| transformer_logreg_c0p1_w0p1 | 0.625115 | 0.671613 | 0.696206 | 0.676669 | 0.573451 | 0.575387 | 0.534564 | 0.647916 |
| transformer_logreg_c0p03_w0p1 | 0.625561 | 0.671176 | 0.696768 | 0.676784 | 0.574065 | 0.576850 | 0.535459 | 0.647828 |

## Target-Wise Selection

- Target-wise avg logloss: `0.620658`
- Drift vs reference: `0.079591`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.670290 |
| Q2 | transformer_logreg_c0p1_w0p35 | 0.683894 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | transformer_ridge_resid_a5_w0p2 | 0.571500 |
| S2 | transformer_logreg_c0p3_w0p35 | 0.571930 |
| S3 | transformer_ridge_resid_a5_w0p35 | 0.529470 |
| S4 | transformer_ridge_resid_a1_w0p2 | 0.643698 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.