# Block OOF diagnostics

- Baseline: `trp_base`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weather_s4midtail_w030 | 0.573799 | -0.000357 | 0.000429 | 0.000000 | 0.000033 | 0.001238 | 0.000921 | -0.000347 | -0.000473 | -0.002352 | 0.000000 | False |
| weather_s4tail_w050 | 0.573964 | -0.000212 | 0.000264 | 0.000000 | 0.000000 | 0.000780 | 0.001249 | -0.000639 | -0.001001 | -0.000785 | 0.000000 | False |
| trp_base | 0.574228 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trp_base | all | 450 | 0.574228 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | late_third | 152 | 0.574306 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | tail_20pct | 95 | 0.573442 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4tail_w050 | all | 450 | 0.573964 | 0.000264 | -0.000212 | 0.000264 | 0.000761 |
| weather_s4tail_w050 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4tail_w050 | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4tail_w050 | late_third | 152 | 0.573525 | 0.000780 | -0.000639 | 0.000780 | 0.002218 |
| weather_s4tail_w050 | tail_20pct | 95 | 0.572193 | 0.001249 | -0.001001 | 0.001249 | 0.003519 |
| weather_s4midtail_w030 | all | 450 | 0.573799 | 0.000429 | -0.000357 | 0.000429 | 0.001194 |
| weather_s4midtail_w030 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4midtail_w030 | mid_third | 147 | 0.567745 | 0.000033 | -0.001644 | 0.000033 | 0.001685 |
| weather_s4midtail_w030 | late_third | 152 | 0.573067 | 0.001238 | -0.000347 | 0.001238 | 0.002825 |
| weather_s4midtail_w030 | tail_20pct | 95 | 0.572521 | 0.000921 | -0.000473 | 0.000921 | 0.002369 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| trp_base | Q1 | 0.651214 | 0.000000 |
| trp_base | Q2 | 0.621548 | 0.000000 |
| trp_base | Q3 | 0.564188 | 0.000000 |
| trp_base | S1 | 0.549259 | 0.000000 |
| trp_base | S2 | 0.537785 | 0.000000 |
| trp_base | S3 | 0.519546 | 0.000000 |
| trp_base | S4 | 0.576600 | 0.000000 |
| weather_s4tail_w050 | Q1 | 0.651214 | 0.000000 |
| weather_s4tail_w050 | Q2 | 0.621548 | 0.000000 |
| weather_s4tail_w050 | Q3 | 0.564188 | 0.000000 |
| weather_s4tail_w050 | S1 | 0.549259 | 0.000000 |
| weather_s4tail_w050 | S2 | 0.537785 | 0.000000 |
| weather_s4tail_w050 | S3 | 0.519546 | 0.000000 |
| weather_s4tail_w050 | S4 | 0.571137 | 0.005463 |
| weather_s4midtail_w030 | Q1 | 0.651214 | 0.000000 |
| weather_s4midtail_w030 | Q2 | 0.621548 | 0.000000 |
| weather_s4midtail_w030 | Q3 | 0.564188 | 0.000000 |
| weather_s4midtail_w030 | S1 | 0.549259 | 0.000000 |
| weather_s4midtail_w030 | S2 | 0.537785 | 0.000000 |
| weather_s4midtail_w030 | S3 | 0.519546 | 0.000000 |
| weather_s4midtail_w030 | S4 | 0.567933 | 0.008667 |
