# Sample-weighted OOF diagnostics

- Baseline: `v35a`
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
| v35e | 0.570315 | 0.524131 | 0.000800 | 0.000293 | 0.000800 | 0.001312 | True |
| v35a | 0.570663 | 0.524930 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v35a | Q1 | 0.629286 | 0.609364 | 0.000000 |
| v35a | Q2 | 0.629928 | 0.575145 | 0.000000 |
| v35a | Q3 | 0.591363 | 0.433020 | 0.000000 |
| v35a | S1 | 0.543530 | 0.551024 | 0.000000 |
| v35a | S2 | 0.521602 | 0.490523 | 0.000000 |
| v35a | S3 | 0.493502 | 0.440873 | 0.000000 |
| v35a | S4 | 0.585430 | 0.574563 | 0.000000 |
| v35e | Q1 | 0.629286 | 0.609364 | 0.000000 |
| v35e | Q2 | 0.628794 | 0.572544 | 0.002601 |
| v35e | Q3 | 0.590057 | 0.430024 | 0.002996 |
| v35e | S1 | 0.543530 | 0.551024 | 0.000000 |
| v35e | S2 | 0.521602 | 0.490523 | 0.000000 |
| v35e | S3 | 0.493502 | 0.440873 | 0.000000 |
| v35e | S4 | 0.585430 | 0.574563 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v35a | mid | 100 | 0.000000 |
| v35a | late | 116 | 0.000000 |
| v35a | tail_20pct | 22 | 0.000000 |
| v35e | mid | 100 | 0.001489 |
| v35e | late | 116 | 0.000068 |
| v35e | tail_20pct | 22 | 0.000000 |
