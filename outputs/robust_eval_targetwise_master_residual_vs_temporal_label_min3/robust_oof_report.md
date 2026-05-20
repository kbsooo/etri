# Robust OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_p025guard | 0.583456 | 0.587368 | 0.011177 | 0.605449 | 5 | 0.000000 | 0.000024 | 0.001008 | 0.002005 | True |
| master_resid_min3_w05 | 0.583496 | 0.587403 | 0.011160 | 0.605459 | 5 | 0.000000 | 0.000025 | 0.000967 | 0.001924 | True |
| master_resid_min3_w03 | 0.583798 | 0.587749 | 0.011289 | 0.606060 | 5 | 0.000000 | 0.000099 | 0.000665 | 0.001244 | True |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| master_resid_min3_w03 | 0.000981 | 0.000000 | 0.002570 | 0.000895 | 0.000000 | 0.000000 | 0.000211 |
| master_resid_min3_w05 | 0.001473 | 0.000000 | 0.003698 | 0.001298 | 0.000000 | 0.000000 | 0.000299 |
| targetwise_p025guard | 0.001759 | 0.000000 | 0.003698 | 0.001298 | 0.000000 | 0.000000 | 0.000299 |
| temporal_label_min3_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| master_resid_min3_w03 | 0.014490 | 0.080000 |
| master_resid_min3_w05 | 0.014527 | 0.080000 |
| targetwise_p025guard | 0.014460 | 0.080000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
