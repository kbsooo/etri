# Robust OOF diagnostics

- Baseline: `hgb_tail_decoder_v8`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v12_hourly | 0.576672 | 0.578212 | 0.004400 | 0.584720 | 3 | 0.000000 | 0.000254 | 0.001434 | 0.002639 | False |
| hgb_tail_decoder_v8 | 0.578106 | 0.580097 | 0.005687 | 0.588869 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v12_hourly | 0.000000 | 0.001938 | 0.004553 | 0.000000 | 0.002913 | 0.000000 | 0.000635 |
| hgb_tail_decoder_v8 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| hgb_tail_decoder_v12_hourly | 0.017554 | 0.096000 |
| hgb_tail_decoder_v8 | 0.019000 | 0.076000 |
