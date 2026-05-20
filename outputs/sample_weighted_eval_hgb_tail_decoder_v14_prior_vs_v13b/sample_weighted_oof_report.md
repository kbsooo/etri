# Sample-weighted OOF diagnostics

- Baseline: `v13b`
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
| v14 | 0.576224 | 0.556820 | 0.001118 | 0.000802 | 0.001120 | 0.001428 | True |
| v13b | 0.576376 | 0.557938 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v13b | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v13b | Q2 | 0.633849 | 0.602819 | 0.000000 |
| v13b | Q3 | 0.602486 | 0.506174 | 0.000000 |
| v13b | S1 | 0.552632 | 0.570736 | 0.000000 |
| v13b | S2 | 0.524707 | 0.503027 | 0.000000 |
| v13b | S3 | 0.497139 | 0.476906 | 0.000000 |
| v13b | S4 | 0.591049 | 0.628554 | 0.000000 |
| v14 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v14 | Q2 | 0.633849 | 0.602819 | 0.000000 |
| v14 | Q3 | 0.602486 | 0.506174 | 0.000000 |
| v14 | S1 | 0.552444 | 0.568887 | 0.001849 |
| v14 | S2 | 0.524347 | 0.500922 | 0.002105 |
| v14 | S3 | 0.496841 | 0.475125 | 0.001781 |
| v14 | S4 | 0.590836 | 0.626463 | 0.002091 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v13b | mid | 100 | 0.000000 |
| v13b | late | 116 | 0.000000 |
| v13b | tail_20pct | 22 | 0.000000 |
| v14 | mid | 100 | 0.000170 |
| v14 | late | 116 | 0.000441 |
| v14 | tail_20pct | 22 | 0.002096 |
