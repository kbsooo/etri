# Block OOF diagnostics

- Baseline: `weather_gru_base`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dae_q1tail_w050 | 0.573732 | -0.000217 | 0.000143 | 0.000000 | 0.000000 | 0.000422 | 0.000675 | -0.000647 | -0.001046 | -0.000683 | 0.000000 | False |
| dae_q1tail_w030 | 0.573773 | -0.000117 | 0.000102 | 0.000000 | 0.000000 | 0.000301 | 0.000481 | -0.000352 | -0.000558 | -0.000387 | 0.000000 | False |
| weather_gru_base | 0.573874 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| weather_gru_base | all | 450 | 0.573874 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_gru_base | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_gru_base | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_gru_base | late_third | 152 | 0.573259 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_gru_base | tail_20pct | 95 | 0.571767 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| dae_q1tail_w030 | all | 450 | 0.573773 | 0.000102 | -0.000117 | 0.000102 | 0.000333 |
| dae_q1tail_w030 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| dae_q1tail_w030 | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| dae_q1tail_w030 | late_third | 152 | 0.572958 | 0.000301 | -0.000352 | 0.000301 | 0.001011 |
| dae_q1tail_w030 | tail_20pct | 95 | 0.571286 | 0.000481 | -0.000558 | 0.000481 | 0.001609 |
| dae_q1tail_w050 | all | 450 | 0.573732 | 0.000143 | -0.000217 | 0.000143 | 0.000516 |
| dae_q1tail_w050 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| dae_q1tail_w050 | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| dae_q1tail_w050 | late_third | 152 | 0.572837 | 0.000422 | -0.000647 | 0.000422 | 0.001581 |
| dae_q1tail_w050 | tail_20pct | 95 | 0.571092 | 0.000675 | -0.001046 | 0.000675 | 0.002511 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| weather_gru_base | Q1 | 0.651214 | 0.000000 |
| weather_gru_base | Q2 | 0.621548 | 0.000000 |
| weather_gru_base | Q3 | 0.564188 | 0.000000 |
| weather_gru_base | S1 | 0.549259 | 0.000000 |
| weather_gru_base | S2 | 0.537785 | 0.000000 |
| weather_gru_base | S3 | 0.517680 | 0.000000 |
| weather_gru_base | S4 | 0.571137 | 0.000000 |
| dae_q1tail_w030 | Q1 | 0.649110 | 0.002104 |
| dae_q1tail_w030 | Q2 | 0.621548 | 0.000000 |
| dae_q1tail_w030 | Q3 | 0.564188 | 0.000000 |
| dae_q1tail_w030 | S1 | 0.549259 | 0.000000 |
| dae_q1tail_w030 | S2 | 0.537785 | 0.000000 |
| dae_q1tail_w030 | S3 | 0.517680 | 0.000000 |
| dae_q1tail_w030 | S4 | 0.571137 | 0.000000 |
| dae_q1tail_w050 | Q1 | 0.648260 | 0.002954 |
| dae_q1tail_w050 | Q2 | 0.621548 | 0.000000 |
| dae_q1tail_w050 | Q3 | 0.564188 | 0.000000 |
| dae_q1tail_w050 | S1 | 0.549259 | 0.000000 |
| dae_q1tail_w050 | S2 | 0.537785 | 0.000000 |
| dae_q1tail_w050 | S3 | 0.517680 | 0.000000 |
| dae_q1tail_w050 | S4 | 0.571137 | 0.000000 |
