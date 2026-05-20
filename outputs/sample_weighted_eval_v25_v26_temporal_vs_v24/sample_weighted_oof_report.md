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
| v26_targetwise | 0.573829 | 0.533048 | 0.001187 | 0.000560 | 0.001183 | 0.001810 | True |
| v25_s1s2_mid | 0.573704 | 0.533149 | 0.001086 | 0.000499 | 0.001078 | 0.001676 | True |
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
| v25_s1s2_mid | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v25_s1s2_mid | Q2 | 0.631432 | 0.579084 | 0.000000 |
| v25_s1s2_mid | Q3 | 0.602648 | 0.460472 | 0.000000 |
| v25_s1s2_mid | S1 | 0.547464 | 0.557462 | 0.002321 |
| v25_s1s2_mid | S2 | 0.522044 | 0.495638 | 0.005284 |
| v25_s1s2_mid | S3 | 0.493610 | 0.443399 | 0.000000 |
| v25_s1s2_mid | S4 | 0.585965 | 0.578635 | 0.000000 |
| v26_targetwise | Q1 | 0.632767 | 0.617350 | 0.000000 |
| v26_targetwise | Q2 | 0.631432 | 0.579084 | 0.000000 |
| v26_targetwise | Q3 | 0.602648 | 0.460472 | 0.000000 |
| v26_targetwise | S1 | 0.548339 | 0.556761 | 0.003022 |
| v26_targetwise | S2 | 0.522044 | 0.495638 | 0.005284 |
| v26_targetwise | S3 | 0.493610 | 0.443399 | 0.000000 |
| v26_targetwise | S4 | 0.585965 | 0.578635 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| v24 | mid | 100 | 0.000000 |
| v24 | late | 116 | 0.000000 |
| v24 | tail_20pct | 22 | 0.000000 |
| v25_s1s2_mid | mid | 100 | 0.002126 |
| v25_s1s2_mid | late | 116 | 0.000004 |
| v25_s1s2_mid | tail_20pct | 22 | 0.000000 |
| v26_targetwise | mid | 100 | 0.002126 |
| v26_targetwise | late | 116 | -0.000533 |
| v26_targetwise | tail_20pct | 22 | 0.000209 |
