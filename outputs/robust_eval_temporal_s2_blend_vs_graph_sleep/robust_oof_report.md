# Robust OOF diagnostics

- Baseline: `graph_sleep_blend`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_s2_blend | 0.584769 | 0.588848 | 0.011655 | 0.607774 | 5 | 0.000000 | 0.000142 | 0.001328 | 0.002525 | True |
| temporal_label_s2 | 0.584614 | 0.588748 | 0.011811 | 0.607999 | 5 | 0.000000 | -0.000008 | 0.001483 | 0.002970 | False |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_s2 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.010380 | 0.000000 | 0.000000 |
| temporal_s2_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.009296 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_blend | 0.009904 | 0.080000 |
| temporal_label_s2 | 0.014806 | 0.080000 |
| temporal_s2_blend | 0.013825 | 0.080000 |
