# Robust OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Candidate count: 5
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_min3 | 0.584048 | 0.588345 | 0.012277 | 0.608550 | 3 | 0.000000 | -0.000785 | 0.000415 | 0.001547 | False |
| calendar_blend | 0.584048 | 0.588345 | 0.012277 | 0.608550 | 3 | 0.000000 | -0.000785 | 0.000415 | 0.001547 | False |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| markov_min3 | 0.584293 | 0.588579 | 0.012246 | 0.608504 | 3 | 0.000000 | -0.000507 | 0.000170 | 0.000858 | False |
| markov_blend | 0.584293 | 0.588579 | 0.012246 | 0.608504 | 3 | 0.000000 | -0.000507 | 0.000170 | 0.000858 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_blend | 0.000000 | 0.000000 | 0.000000 | 0.001172 | 0.000584 | 0.000000 | 0.001150 |
| calendar_min3 | 0.000000 | 0.000000 | 0.000000 | 0.001172 | 0.000584 | 0.000000 | 0.001150 |
| markov_blend | 0.001189 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| markov_min3 | 0.001189 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| calendar_blend | 0.014400 | 0.080000 |
| calendar_min3 | 0.014400 | 0.080000 |
| markov_blend | 0.014726 | 0.080000 |
| markov_min3 | 0.014726 | 0.080000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
