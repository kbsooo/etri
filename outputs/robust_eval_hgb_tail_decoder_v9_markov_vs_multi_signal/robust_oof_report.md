# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v9_markov_q1 | 0.577938 | 0.580235 | 0.006564 | 0.590363 | 5 | 0.001235 | 0.001573 | 0.003654 | 0.005905 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v9_markov_q1 | 0.003869 | 0.003755 | 0.012511 | 0.001235 | 0.001399 | 0.001257 | 0.001555 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| hgb_tail_decoder_v9_markov_q1 | 0.019487 | 0.076000 |
| multi_signal | 0.015133 | 0.080000 |
