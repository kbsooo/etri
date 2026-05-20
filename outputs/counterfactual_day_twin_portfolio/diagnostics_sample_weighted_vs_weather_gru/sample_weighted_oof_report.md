# Sample-weighted OOF diagnostics

- Baseline: `weather_gru_base`
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
| dae_q1tail_w050 | 0.573732 | 0.532261 | 0.001399 | 0.000263 | 0.001405 | 0.002579 | True |
| dae_q1tail_w030 | 0.573773 | 0.532664 | 0.000997 | 0.000304 | 0.001000 | 0.001723 | True |
| weather_gru_base | 0.573874 | 0.533661 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| weather_gru_base | Q1 | 0.632824 | 0.617903 | 0.000000 |
| weather_gru_base | Q2 | 0.632493 | 0.589713 | 0.000000 |
| weather_gru_base | Q3 | 0.600885 | 0.491149 | 0.000000 |
| weather_gru_base | S1 | 0.552471 | 0.569155 | 0.000000 |
| weather_gru_base | S2 | 0.519173 | 0.448795 | 0.000000 |
| weather_gru_base | S3 | 0.494458 | 0.451570 | 0.000000 |
| weather_gru_base | S4 | 0.584815 | 0.567341 | 0.000000 |
| dae_q1tail_w030 | Q1 | 0.632113 | 0.610927 | 0.006976 |
| dae_q1tail_w030 | Q2 | 0.632493 | 0.589713 | 0.000000 |
| dae_q1tail_w030 | Q3 | 0.600885 | 0.491149 | 0.000000 |
| dae_q1tail_w030 | S1 | 0.552471 | 0.569155 | 0.000000 |
| dae_q1tail_w030 | S2 | 0.519173 | 0.448795 | 0.000000 |
| dae_q1tail_w030 | S3 | 0.494458 | 0.451570 | 0.000000 |
| dae_q1tail_w030 | S4 | 0.584815 | 0.567341 | 0.000000 |
| dae_q1tail_w050 | Q1 | 0.631826 | 0.608108 | 0.009795 |
| dae_q1tail_w050 | Q2 | 0.632493 | 0.589713 | 0.000000 |
| dae_q1tail_w050 | Q3 | 0.600885 | 0.491149 | 0.000000 |
| dae_q1tail_w050 | S1 | 0.552471 | 0.569155 | 0.000000 |
| dae_q1tail_w050 | S2 | 0.519173 | 0.448795 | 0.000000 |
| dae_q1tail_w050 | S3 | 0.494458 | 0.451570 | 0.000000 |
| dae_q1tail_w050 | S4 | 0.584815 | 0.567341 | 0.000000 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| weather_gru_base | mid | 100 | 0.000000 |
| weather_gru_base | late | 116 | 0.000000 |
| weather_gru_base | tail_20pct | 22 | 0.000000 |
| dae_q1tail_w030 | mid | 100 | 0.000000 |
| dae_q1tail_w030 | late | 116 | 0.000394 |
| dae_q1tail_w030 | tail_20pct | 22 | 0.002076 |
| dae_q1tail_w050 | mid | 100 | 0.000000 |
| dae_q1tail_w050 | late | 116 | 0.000553 |
| dae_q1tail_w050 | tail_20pct | 22 | 0.002915 |
