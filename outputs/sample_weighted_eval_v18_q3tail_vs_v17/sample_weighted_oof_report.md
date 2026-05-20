# Sample-weighted OOF diagnostics

- Baseline: `v17`
- Weights match train rows to the submission sample panel-position distribution.

## Position bins

| bin | train_frac | sample_frac | weight_ratio |
| --- | --- | --- | --- |
| [0.000,0.333) | 0.520000 | 0.000000 | 0.000000 |
| [0.333,0.667) | 0.226667 | 0.520000 | 2.294118 |
| [0.667,0.800) | 0.204444 | 0.000000 | 0.000000 |
| [0.800,1.000) | 0.048889 | 0.480000 | 9.818182 |

## Candidate summary

| name | uniform_avg_log_loss | weighted_avg_log_loss | weighted_delta_vs_baseline | weighted_p025 | weighted_p500 | weighted_p975 | promote_weighted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v18_q3tail | 0.574823 | 0.543055 | 0.001442 | 0.000682 | 0.001448 | 0.002204 | True |
| v17 | 0.574969 | 0.544497 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v17 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v17 | Q2 | 0.632101 | 0.585648 | 0.000000 |
| v17 | Q3 | 0.602486 | 0.506174 | 0.000000 |
| v17 | S1 | 0.552444 | 0.568887 | 0.000000 |
| v17 | S2 | 0.524347 | 0.500922 | 0.000000 |
| v17 | S3 | 0.494675 | 0.453861 | 0.000000 |
| v17 | S4 | 0.585965 | 0.578635 | 0.000000 |
| v18_q3tail | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v18_q3tail | Q2 | 0.632101 | 0.585648 | 0.000000 |
| v18_q3tail | Q3 | 0.601458 | 0.496081 | 0.010092 |
| v18_q3tail | S1 | 0.552444 | 0.568887 | 0.000000 |
| v18_q3tail | S2 | 0.524347 | 0.500922 | 0.000000 |
| v18_q3tail | S3 | 0.494675 | 0.453861 | 0.000000 |
| v18_q3tail | S4 | 0.585965 | 0.578635 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v17 | mid | 100 | 0.000000 |
| v17 | late | 116 | 0.000000 |
| v17 | tail_20pct | 22 | 0.000000 |
| v18_q3tail | mid | 100 | 0.000000 |
| v18_q3tail | late | 116 | 0.000570 |
| v18_q3tail | tail_20pct | 22 | 0.003004 |
