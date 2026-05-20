# Robust OOF diagnostics

- Baseline: `latent_temporal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_diffusion | 0.602876 | 0.606255 | 0.009653 | 0.620163 | 5 | 0.004777 | 0.005093 | 0.009737 | 0.014265 | True |
| robust_safe | 0.609898 | 0.613600 | 0.010580 | 0.628611 | 5 | 0.000000 | 0.001172 | 0.002715 | 0.004252 | True |
| latent_temporal | 0.612613 | 0.616651 | 0.011538 | 0.631994 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_diffusion | 0.008183 | 0.006638 | 0.006083 | 0.008675 | 0.007109 | 0.004777 | 0.026693 |
| latent_temporal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| robust_safe | 0.005864 | 0.003137 | 0.002908 | 0.005932 | 0.000000 | 0.000000 | 0.001167 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_diffusion | 0.008890 | 0.028000 |
| latent_temporal | 0.009483 | 0.000000 |
| robust_safe | 0.009333 | 0.000000 |
