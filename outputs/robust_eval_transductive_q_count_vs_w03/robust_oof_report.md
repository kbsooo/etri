# Robust OOF diagnostics

- Baseline: `primary_w03`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0010.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transductive_q_count | 0.581514 | 0.585389 | 0.011070 | 0.603125 | 4 | 0.000000 | 0.000049 | 0.002283 | 0.004527 | True |
| primary_w03 | 0.583798 | 0.587749 | 0.011289 | 0.606060 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_w03 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| transductive_q_count | 0.001838 | 0.012379 | 0.001767 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| primary_w03 | 0.014490 | 0.080000 |
| transductive_q_count | 0.015357 | 0.080000 |
