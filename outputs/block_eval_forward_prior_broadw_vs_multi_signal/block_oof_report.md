# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| forward_prior_broadw | 0.573959 | 0.002961 | 0.007633 | 0.006646 | 0.005396 | 0.010779 | 0.006753 | 0.003068 | -0.002283 | -0.004516 | 0.000000 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| forward_prior_broadw | all | 450 | 0.573959 | 0.007633 | 0.002961 | 0.007633 | 0.012279 |
| forward_prior_broadw | early_third | 151 | 0.573783 | 0.006646 | -0.002038 | 0.006646 | 0.015589 |
| forward_prior_broadw | mid_third | 147 | 0.566339 | 0.005396 | -0.001931 | 0.005396 | 0.012767 |
| forward_prior_broadw | late_third | 152 | 0.581503 | 0.010779 | 0.003068 | 0.010779 | 0.018420 |
| forward_prior_broadw | tail_20pct | 95 | 0.591664 | 0.006753 | -0.002283 | 0.006753 | 0.015877 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | Q1 | 0.656396 | 0.000000 |
| multi_signal | Q2 | 0.642320 | 0.000000 |
| multi_signal | Q3 | 0.605681 | 0.000000 |
| multi_signal | S1 | 0.550509 | 0.000000 |
| multi_signal | S2 | 0.565290 | 0.000000 |
| multi_signal | S3 | 0.529003 | 0.000000 |
| multi_signal | S4 | 0.596773 | 0.000000 |
| forward_prior_broadw | Q1 | 0.635178 | 0.021218 |
| forward_prior_broadw | Q2 | 0.605362 | 0.036958 |
| forward_prior_broadw | Q3 | 0.588406 | 0.017275 |
| forward_prior_broadw | S1 | 0.550509 | 0.000000 |
| forward_prior_broadw | S2 | 0.565290 | 0.000000 |
| forward_prior_broadw | S3 | 0.529003 | 0.000000 |
| forward_prior_broadw | S4 | 0.596773 | 0.000000 |
