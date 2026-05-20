# Robust OOF diagnostics

- Baseline: `latent_temporal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_original | 0.602876 | 0.606255 | 0.009653 | 0.620163 | 5 | 0.004777 | 0.005093 | 0.009737 | 0.014265 | True |
| graph_subjectless_long | 0.605081 | 0.608467 | 0.009673 | 0.621541 | 5 | 0.003363 | 0.003910 | 0.007532 | 0.011270 | True |
| latent_temporal | 0.612613 | 0.616651 | 0.011538 | 0.631994 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_original | 0.008183 | 0.006638 | 0.006083 | 0.008675 | 0.007109 | 0.004777 | 0.026693 |
| graph_subjectless_long | 0.008690 | 0.005702 | 0.008318 | 0.007054 | 0.006777 | 0.003363 | 0.012821 |
| latent_temporal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_original | 0.008890 | 0.028000 |
| graph_subjectless_long | 0.010611 | 0.028000 |
| latent_temporal | 0.009483 | 0.000000 |
