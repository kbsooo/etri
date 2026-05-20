# Sample-weighted OOF diagnostics

- Baseline: `v34a`
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
| v34a | 0.570913 | 0.525503 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| stack | 0.567602 | 0.528334 | -0.002831 | -0.004551 | -0.002824 | -0.001103 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v34a | Q1 | 0.629286 | 0.609364 | 0.000000 |
| v34a | Q2 | 0.629928 | 0.575145 | 0.000000 |
| v34a | Q3 | 0.591363 | 0.433020 | 0.000000 |
| v34a | S1 | 0.545277 | 0.555032 | 0.000000 |
| v34a | S2 | 0.521602 | 0.490523 | 0.000000 |
| v34a | S3 | 0.493502 | 0.440873 | 0.000000 |
| v34a | S4 | 0.585430 | 0.574563 | 0.000000 |
| stack | Q1 | 0.627521 | 0.606525 | 0.002838 |
| stack | Q2 | 0.614045 | 0.595497 | -0.020352 |
| stack | Q3 | 0.586762 | 0.437798 | -0.004778 |
| stack | S1 | 0.544666 | 0.550956 | 0.004076 |
| stack | S2 | 0.521602 | 0.490523 | 0.000000 |
| stack | S3 | 0.493502 | 0.440873 | 0.000000 |
| stack | S4 | 0.585119 | 0.576162 | -0.001599 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v34a | mid | 100 | 0.000000 |
| v34a | late | 116 | 0.000000 |
| v34a | tail_20pct | 22 | 0.000000 |
| stack | mid | 100 | 0.002786 |
| stack | late | 116 | 0.001783 |
| stack | tail_20pct | 22 | -0.009096 |
