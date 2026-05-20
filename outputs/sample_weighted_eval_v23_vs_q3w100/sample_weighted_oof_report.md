# Sample-weighted OOF diagnostics

- Baseline: `q3w100`
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
| v23 | 0.574109 | 0.533560 | 0.011174 | 0.007280 | 0.011151 | 0.015115 | True |
| q3w100 | 0.575682 | 0.544735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| q3w100 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| q3w100 | Q2 | 0.631830 | 0.582987 | 0.000000 |
| q3w100 | Q3 | 0.607743 | 0.510501 | 0.000000 |
| q3w100 | S1 | 0.552444 | 0.568887 | 0.000000 |
| q3w100 | S2 | 0.524347 | 0.500922 | 0.000000 |
| q3w100 | S3 | 0.494675 | 0.453861 | 0.000000 |
| q3w100 | S4 | 0.585965 | 0.578635 | 0.000000 |
| v23 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v23 | Q2 | 0.630951 | 0.574360 | 0.008627 |
| v23 | Q3 | 0.602648 | 0.460472 | 0.050029 |
| v23 | S1 | 0.548476 | 0.559783 | 0.009104 |
| v23 | S2 | 0.524347 | 0.500922 | 0.000000 |
| v23 | S3 | 0.493610 | 0.443399 | 0.010462 |
| v23 | S4 | 0.585965 | 0.578635 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| q3w100 | mid | 100 | 0.000000 |
| q3w100 | late | 116 | 0.000000 |
| q3w100 | tail_20pct | 22 | 0.000000 |
| v23 | mid | 100 | 0.002555 |
| v23 | late | 116 | 0.003898 |
| v23 | tail_20pct | 22 | 0.020571 |
