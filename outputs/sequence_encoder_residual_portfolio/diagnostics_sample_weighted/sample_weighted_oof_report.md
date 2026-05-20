# Sample-weighted OOF diagnostics

- Baseline: `trp_base`
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
| trp_plus_gru28_s3tail_w100 | 0.574138 | 0.536249 | 0.000884 | 0.000418 | 0.000881 | 0.001404 | True |
| trp_base | 0.574228 | 0.537133 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| trp_base | Q1 | 0.632824 | 0.617903 | 0.000000 |
| trp_base | Q2 | 0.632493 | 0.589713 | 0.000000 |
| trp_base | Q3 | 0.600885 | 0.491149 | 0.000000 |
| trp_base | S1 | 0.552471 | 0.569155 | 0.000000 |
| trp_base | S2 | 0.519173 | 0.448795 | 0.000000 |
| trp_base | S3 | 0.495089 | 0.457758 | 0.000000 |
| trp_base | S4 | 0.586660 | 0.585457 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | Q1 | 0.632824 | 0.617903 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | Q2 | 0.632493 | 0.589713 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | Q3 | 0.600885 | 0.491149 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | S1 | 0.552471 | 0.569155 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | S2 | 0.519173 | 0.448795 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | S3 | 0.494458 | 0.451570 | 0.006188 |
| trp_plus_gru28_s3tail_w100 | S4 | 0.586660 | 0.585457 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| trp_base | mid | 100 | 0.000000 |
| trp_base | late | 116 | 0.000000 |
| trp_base | tail_20pct | 22 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | mid | 100 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | late | 116 | 0.000349 |
| trp_plus_gru28_s3tail_w100 | tail_20pct | 22 | 0.001842 |
