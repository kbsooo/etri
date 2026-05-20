# Robust OOF diagnostics

- Baseline: `q3w100`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_q3w100_min3 | 0.575567 | 0.576318 | 0.002144 | 0.577983 | 3 | 0.000000 | -0.000467 | 0.000114 | 0.000705 | False |
| q3w100 | 0.575682 | 0.576404 | 0.002064 | 0.578006 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_q3w100_min3 | 0.000000 | 0.000000 | 0.000000 | 0.000078 | 0.000000 | 0.000169 | 0.000554 |
| q3w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_q3w100_min3 | 0.020644 | 0.128000 |
| q3w100 | 0.021103 | 0.132000 |
