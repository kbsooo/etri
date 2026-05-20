# Sample-weighted OOF diagnostics

- Baseline: `v21`
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
| v22 | 0.574235 | 0.534793 | 0.003562 | 0.001323 | 0.003551 | 0.005940 | True |
| v21 | 0.574597 | 0.538355 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| v21 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v21 | Q2 | 0.631830 | 0.582987 | 0.000000 |
| v21 | Q3 | 0.605187 | 0.485406 | 0.000000 |
| v21 | S1 | 0.548476 | 0.559783 | 0.000000 |
| v21 | S2 | 0.524347 | 0.500922 | 0.000000 |
| v21 | S3 | 0.493610 | 0.443399 | 0.000000 |
| v21 | S4 | 0.585965 | 0.578635 | 0.000000 |
| v22 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v22 | Q2 | 0.631830 | 0.582987 | 0.000000 |
| v22 | Q3 | 0.602648 | 0.460472 | 0.024934 |
| v22 | S1 | 0.548476 | 0.559783 | 0.000000 |
| v22 | S2 | 0.524347 | 0.500922 | 0.000000 |
| v22 | S3 | 0.493610 | 0.443399 | 0.000000 |
| v22 | S4 | 0.585965 | 0.578635 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v21 | mid | 100 | 0.000000 |
| v21 | late | 116 | 0.000000 |
| v21 | tail_20pct | 22 | 0.000000 |
| v22 | mid | 100 | 0.000000 |
| v22 | late | 116 | 0.001407 |
| v22 | tail_20pct | 22 | 0.007421 |
