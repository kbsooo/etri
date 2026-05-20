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
| v38a | 0.549791 | 0.511677 | 0.012454 | 0.007495 | 0.012443 | 0.017476 | True |
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
| v38a | Q1 | 0.605224 | 0.583358 | 0.026006 |
| v38a | Q2 | 0.583196 | 0.564229 | 0.008315 |
| v38a | Q3 | 0.566015 | 0.412839 | 0.017186 |
| v38a | S1 | 0.537065 | 0.533682 | 0.017341 |
| v38a | S2 | 0.510022 | 0.485373 | 0.005151 |
| v38a | S3 | 0.477811 | 0.429751 | 0.011123 |
| v38a | S4 | 0.569201 | 0.572506 | 0.002057 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v35e | mid | 100 | 0.000000 |
| v35e | late | 116 | 0.000000 |
| v35e | tail_20pct | 22 | 0.000000 |
| v38a | mid | 100 | 0.016358 |
| v38a | late | 116 | 0.026268 |
| v38a | tail_20pct | 22 | 0.010265 |
