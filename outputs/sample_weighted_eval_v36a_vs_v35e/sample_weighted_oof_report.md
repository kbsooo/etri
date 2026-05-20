# Sample-weighted OOF diagnostics

- Baseline: `v35e`
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
| v36a | 0.563651 | 0.520544 | 0.003586 | 0.000091 | 0.003584 | 0.007077 | True |
| v35e | 0.570315 | 0.524131 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v35e | Q1 | 0.629286 | 0.609364 | 0.000000 |
| v35e | Q2 | 0.628794 | 0.572544 | 0.000000 |
| v35e | Q3 | 0.590057 | 0.430024 | 0.000000 |
| v35e | S1 | 0.543530 | 0.551024 | 0.000000 |
| v35e | S2 | 0.521602 | 0.490523 | 0.000000 |
| v35e | S3 | 0.493502 | 0.440873 | 0.000000 |
| v35e | S4 | 0.585430 | 0.574563 | 0.000000 |
| v36a | Q1 | 0.622909 | 0.597544 | 0.011820 |
| v36a | Q2 | 0.601545 | 0.569430 | 0.003115 |
| v36a | Q3 | 0.580818 | 0.426272 | 0.003752 |
| v36a | S1 | 0.542876 | 0.544606 | 0.006418 |
| v36a | S2 | 0.521602 | 0.490523 | 0.000000 |
| v36a | S3 | 0.493502 | 0.440873 | 0.000000 |
| v36a | S4 | 0.582306 | 0.574563 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v35e | mid | 100 | 0.000000 |
| v35e | late | 116 | 0.000000 |
| v35e | tail_20pct | 22 | 0.000000 |
| v36a | mid | 100 | 0.000000 |
| v36a | late | 116 | 0.012376 |
| v36a | tail_20pct | 22 | 0.007472 |
