# Robust OOF diagnostics

- Baseline: `latent_temporal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| robust_safe | 0.609898 | 0.613600 | 0.010580 | 0.628611 | 5 | 0.000000 | 0.001172 | 0.002715 | 0.004252 | True |
| master_temporal | 0.609688 | 0.613270 | 0.010234 | 0.626969 | 5 | 0.000000 | -0.000017 | 0.002925 | 0.005781 | False |
| q_ranker_tuned | 0.610583 | 0.614419 | 0.010960 | 0.629743 | 4 | 0.000000 | -0.000055 | 0.002030 | 0.004199 | False |
| latent_temporal | 0.612613 | 0.616651 | 0.011538 | 0.631994 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| latent_temporal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| master_temporal | 0.004821 | 0.002427 | 0.003860 | 0.007821 | 0.000000 | 0.000000 | 0.001549 |
| q_ranker_tuned | 0.007825 | 0.003972 | 0.002412 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| robust_safe | 0.005864 | 0.003137 | 0.002908 | 0.005932 | 0.000000 | 0.000000 | 0.001167 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| latent_temporal | 0.009483 | 0.000000 |
| master_temporal | 0.008927 | 0.000000 |
| q_ranker_tuned | 0.008993 | 0.000000 |
| robust_safe | 0.009333 | 0.000000 |
