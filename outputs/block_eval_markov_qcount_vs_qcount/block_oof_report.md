# Block OOF diagnostics

- Baseline: `block_aware_qcount`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| markov_qcount | 0.581474 | -0.000621 | 0.000377 | 0.001798 | -0.000292 | -0.000387 | -0.000513 | -0.002224 | -0.003031 | -0.007489 | -0.006672 | False |
| block_aware_qcount | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | all | 450 | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | early_third | 151 | 0.581015 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | mid_third | 147 | 0.571831 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | late_third | 152 | 0.592373 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | tail_20pct | 95 | 0.598552 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| markov_qcount | all | 450 | 0.581474 | 0.000377 | -0.000621 | 0.000377 | 0.001385 |
| markov_qcount | early_third | 151 | 0.579217 | 0.001798 | 0.000098 | 0.001798 | 0.003600 |
| markov_qcount | mid_third | 147 | 0.572122 | -0.000292 | -0.001990 | -0.000292 | 0.001425 |
| markov_qcount | late_third | 152 | 0.592760 | -0.000387 | -0.002224 | -0.000387 | 0.001416 |
| markov_qcount | tail_20pct | 95 | 0.599065 | -0.000513 | -0.003031 | -0.000513 | 0.001978 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| block_aware_qcount | Q1 | 0.655598 | 0.000000 |
| block_aware_qcount | Q2 | 0.642916 | 0.000000 |
| block_aware_qcount | Q3 | 0.605835 | 0.000000 |
| block_aware_qcount | S1 | 0.550398 | 0.000000 |
| block_aware_qcount | S2 | 0.565627 | 0.000000 |
| block_aware_qcount | S3 | 0.528912 | 0.000000 |
| block_aware_qcount | S4 | 0.597326 | 0.000000 |
| markov_qcount | Q1 | 0.662270 | -0.006672 |
| markov_qcount | Q2 | 0.639671 | 0.003245 |
| markov_qcount | Q3 | 0.605117 | 0.000718 |
| markov_qcount | S1 | 0.550398 | 0.000000 |
| markov_qcount | S2 | 0.565627 | 0.000000 |
| markov_qcount | S3 | 0.528912 | 0.000000 |
| markov_qcount | S4 | 0.597326 | 0.000000 |
