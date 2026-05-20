# Robust OOF diagnostics

- Baseline: `v31`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v32_w065 | 0.571516 | 0.572647 | 0.003233 | 0.577482 | 2 | 0.000000 | -0.000064 | 0.000187 | 0.000443 | False |
| v32_w050 | 0.571554 | 0.572677 | 0.003208 | 0.577482 | 2 | 0.000000 | -0.000045 | 0.000149 | 0.000346 | False |
| v31 | 0.571703 | 0.572794 | 0.003117 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v31 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v32_w050 | 0.000000 | 0.001041 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v32_w065 | 0.000000 | 0.001310 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| v31 | 0.022075 | 0.156000 |
| v32_w050 | 0.021660 | 0.156000 |
| v32_w065 | 0.021535 | 0.156000 |
