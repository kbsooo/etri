# Block OOF diagnostics

- Baseline: `v35e`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v36a | 0.563651 | 0.002036 | 0.006663 | 0.006318 | 0.004142 | 0.009445 | 0.008419 | -0.000233 | -0.005246 | -0.004207 | 0.000000 | True |
| v35e | 0.570315 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v35e | all | 450 | 0.570315 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | mid_third | 147 | 0.562686 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | late_third | 152 | 0.567706 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | tail_20pct | 95 | 0.567406 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v36a | all | 450 | 0.563651 | 0.006663 | 0.002036 | 0.006663 | 0.011269 |
| v36a | early_third | 151 | 0.574049 | 0.006318 | -0.002148 | 0.006318 | 0.014731 |
| v36a | mid_third | 147 | 0.558545 | 0.004142 | -0.001080 | 0.004142 | 0.009323 |
| v36a | late_third | 152 | 0.558260 | 0.009445 | -0.000233 | 0.009445 | 0.019007 |
| v36a | tail_20pct | 95 | 0.558987 | 0.008419 | -0.005246 | 0.008419 | 0.021955 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v35e | Q1 | 0.647814 | 0.000000 |
| v35e | Q2 | 0.612710 | 0.000000 |
| v35e | Q3 | 0.532843 | 0.000000 |
| v35e | S1 | 0.542220 | 0.000000 |
| v35e | S2 | 0.550381 | 0.000000 |
| v35e | S3 | 0.515956 | 0.000000 |
| v35e | S4 | 0.572014 | 0.000000 |
| v36a | Q1 | 0.628935 | 0.018879 |
| v36a | Q2 | 0.584521 | 0.028189 |
| v36a | Q3 | 0.524980 | 0.007863 |
| v36a | S1 | 0.540285 | 0.001935 |
| v36a | S2 | 0.550381 | 0.000000 |
| v36a | S3 | 0.515956 | 0.000000 |
| v36a | S4 | 0.562765 | 0.009249 |
