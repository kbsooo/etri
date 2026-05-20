# Robust OOF diagnostics

- Baseline: `v32`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v33a | 0.571019 | 0.572287 | 0.003623 | 0.577482 | 2 | 0.000000 | -0.000089 | 0.000497 | 0.001081 | False |
| v33b | 0.571169 | 0.572395 | 0.003502 | 0.577482 | 2 | 0.000000 | -0.000013 | 0.000347 | 0.000712 | False |
| v33c | 0.571211 | 0.572425 | 0.003468 | 0.577482 | 2 | 0.000000 | -0.000021 | 0.000304 | 0.000632 | False |
| v32 | 0.571516 | 0.572647 | 0.003233 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v32 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33a | 0.003481 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33b | 0.002429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33c | 0.002131 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| v32 | 0.021535 | 0.156000 |
| v33a | 0.021609 | 0.156000 |
| v33b | 0.021618 | 0.156000 |
| v33c | 0.021561 | 0.156000 |
