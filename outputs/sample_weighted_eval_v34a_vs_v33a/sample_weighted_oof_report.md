# Sample-weighted OOF diagnostics

- Baseline: `v33a`
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
| v34a | 0.570913 | 0.525503 | 0.000466 | 0.000048 | 0.000467 | 0.000879 | True |
| v33a | 0.571019 | 0.525969 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v33a | Q1 | 0.629286 | 0.609364 | 0.000000 |
| v33a | Q2 | 0.629928 | 0.575145 | 0.000000 |
| v33a | Q3 | 0.592104 | 0.436283 | 0.000000 |
| v33a | S1 | 0.545277 | 0.555032 | 0.000000 |
| v33a | S2 | 0.521602 | 0.490523 | 0.000000 |
| v33a | S3 | 0.493502 | 0.440873 | 0.000000 |
| v33a | S4 | 0.585430 | 0.574563 | 0.000000 |
| v34a | Q1 | 0.629286 | 0.609364 | 0.000000 |
| v34a | Q2 | 0.629928 | 0.575145 | 0.000000 |
| v34a | Q3 | 0.591363 | 0.433020 | 0.003263 |
| v34a | S1 | 0.545277 | 0.555032 | 0.000000 |
| v34a | S2 | 0.521602 | 0.490523 | 0.000000 |
| v34a | S3 | 0.493502 | 0.440873 | 0.000000 |
| v34a | S4 | 0.585430 | 0.574563 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v33a | mid | 100 | 0.000000 |
| v33a | late | 116 | 0.000000 |
| v33a | tail_20pct | 22 | 0.000000 |
| v34a | mid | 100 | 0.000341 |
| v34a | late | 116 | 0.000117 |
| v34a | tail_20pct | 22 | 0.000607 |
