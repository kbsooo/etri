# Robust OOF diagnostics

- Baseline: `graph_sleep_blend`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 5 | 0.000000 | 0.000172 | 0.001633 | 0.003129 | True |
| temporal_s2_blend | 0.584769 | 0.588848 | 0.011655 | 0.607774 | 5 | 0.000000 | 0.000142 | 0.001328 | 0.002525 | True |
| temporal_label_min3 | 0.584289 | 0.588358 | 0.011626 | 0.607349 | 5 | 0.000000 | -0.000021 | 0.001807 | 0.003667 | False |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3 | 0.000024 | 0.000000 | 0.000501 | 0.000398 | 0.010380 | 0.001090 | 0.000257 |
| temporal_label_min3_blend | 0.000028 | 0.000000 | 0.000502 | 0.000358 | 0.009296 | 0.001012 | 0.000237 |
| temporal_s2_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.009296 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_blend | 0.009904 | 0.080000 |
| temporal_label_min3 | 0.015567 | 0.080000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
| temporal_s2_blend | 0.013825 | 0.080000 |
