# Robust OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_min3 | 0.584100 | 0.587901 | 0.010857 | 0.605259 | 3 | 0.000000 | -0.000680 | 0.000363 | 0.001382 | False |
| graph_min3_blend | 0.584100 | 0.587901 | 0.010857 | 0.605259 | 3 | 0.000000 | -0.000680 | 0.000363 | 0.001382 | False |
| graph_min4 | 0.584425 | 0.588425 | 0.011428 | 0.607046 | 4 | 0.000000 | -0.000165 | 0.000038 | 0.000234 | False |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_min3 | 0.000253 | 0.000480 | 0.000538 | 0.000000 | 0.000000 | 0.000267 | 0.001001 |
| graph_min3_blend | 0.000253 | 0.000480 | 0.000538 | 0.000000 | 0.000000 | 0.000267 | 0.001001 |
| graph_min4 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000267 | 0.000000 |
| temporal_label_min3_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_min3 | 0.014039 | 0.084000 |
| graph_min3_blend | 0.014039 | 0.084000 |
| graph_min4 | 0.014373 | 0.084000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
