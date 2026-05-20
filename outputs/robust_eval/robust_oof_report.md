# Robust OOF diagnostics

- Baseline: `latent_temporal`
- Candidate count: 6
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| master_temporal | 0.609688 | 0.613270 | 0.010234 | 0.626969 | 5 | 0.000000 | -0.000017 | 0.002925 | 0.005781 | False |
| q_ranker_tuned | 0.610583 | 0.614419 | 0.010960 | 0.629743 | 4 | 0.000000 | -0.000055 | 0.002030 | 0.004199 | False |
| latent_temporal | 0.612613 | 0.616651 | 0.011538 | 0.631994 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| master_targetwise | 0.616072 | 0.622440 | 0.010396 | 0.633918 | 1 | -0.018193 | -0.009814 | -0.003459 | 0.002880 | False |
| latent_targetwise | 0.616835 | 0.623001 | 0.011657 | 0.637617 | 1 | -0.013909 | -0.007617 | -0.004222 | -0.000834 | False |
| master_best_global | 0.622993 | 0.630469 | 0.013564 | 0.643993 | 0 | -0.018193 | -0.016972 | -0.010380 | -0.004108 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| latent_targetwise | -0.000551 | -0.004916 | -0.001955 | 0.000000 | -0.013909 | -0.000175 | -0.008047 |
| latent_temporal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| master_best_global | -0.018085 | -0.017360 | -0.005173 | -0.000243 | -0.018193 | -0.010370 | -0.003233 |
| master_targetwise | -0.004618 | -0.003983 | 0.000937 | 0.006616 | -0.018193 | -0.001738 | -0.003233 |
| master_temporal | 0.004821 | 0.002427 | 0.003860 | 0.007821 | 0.000000 | 0.000000 | 0.001549 |
| q_ranker_tuned | 0.007825 | 0.003972 | 0.002412 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| latent_targetwise | 0.008280 | 0.000000 |
| latent_temporal | 0.009483 | 0.000000 |
| master_best_global | 0.009038 | 0.000000 |
| master_targetwise | 0.007581 | 0.000000 |
| master_temporal | 0.008927 | 0.000000 |
| q_ranker_tuned | 0.008993 | 0.000000 |
