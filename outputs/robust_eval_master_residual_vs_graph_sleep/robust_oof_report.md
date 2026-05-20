# Robust OOF diagnostics

- Baseline: `graph_sleep_blend`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_p025guard | 0.583456 | 0.587368 | 0.011177 | 0.605449 | 5 | 0.000000 | 0.000904 | 0.002641 | 0.004436 | True |
| master_resid_w03 | 0.583798 | 0.587749 | 0.011289 | 0.606060 | 5 | 0.000000 | 0.000735 | 0.002299 | 0.003882 | True |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 5 | 0.000000 | 0.000172 | 0.001633 | 0.003129 | True |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| master_resid_w03 | 0.001009 | 0.000000 | 0.003072 | 0.001253 | 0.009296 | 0.001012 | 0.000449 |
| targetwise_p025guard | 0.001787 | 0.000000 | 0.004200 | 0.001656 | 0.009296 | 0.001012 | 0.000536 |
| temporal_label_min3_blend | 0.000028 | 0.000000 | 0.000502 | 0.000358 | 0.009296 | 0.001012 | 0.000237 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_blend | 0.009904 | 0.080000 |
| master_resid_w03 | 0.014490 | 0.080000 |
| targetwise_p025guard | 0.014460 | 0.080000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
