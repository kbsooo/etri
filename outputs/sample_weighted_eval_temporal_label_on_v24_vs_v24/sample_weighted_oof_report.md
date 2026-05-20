# Sample-weighted OOF diagnostics

- Baseline: `v24`
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
| temporal_label | 0.573944 | 0.533273 | 0.000962 | -0.000313 | 0.000948 | 0.002192 | False |
| v24 | 0.574178 | 0.534235 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v24 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v24 | Q2 | 0.631432 | 0.579084 | 0.000000 |
| v24 | Q3 | 0.602648 | 0.460472 | 0.000000 |
| v24 | S1 | 0.548476 | 0.559783 | 0.000000 |
| v24 | S2 | 0.524347 | 0.500922 | 0.000000 |
| v24 | S3 | 0.493610 | 0.443399 | 0.000000 |
| v24 | S4 | 0.585965 | 0.578635 | 0.000000 |
| temporal_label | Q1 | 0.632767 | 0.617350 | 0.000000 |
| temporal_label | Q2 | 0.631432 | 0.579084 | 0.000000 |
| temporal_label | Q3 | 0.602648 | 0.460472 | 0.000000 |
| temporal_label | S1 | 0.548339 | 0.556761 | 0.003022 |
| temporal_label | S2 | 0.522845 | 0.497210 | 0.003712 |
| temporal_label | S3 | 0.493610 | 0.443399 | 0.000000 |
| temporal_label | S4 | 0.585965 | 0.578635 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v24 | mid | 100 | 0.000000 |
| v24 | late | 116 | 0.000000 |
| v24 | tail_20pct | 22 | 0.000000 |
| temporal_label | mid | 100 | 0.002126 |
| temporal_label | late | 116 | -0.001002 |
| temporal_label | tail_20pct | 22 | -0.000259 |
