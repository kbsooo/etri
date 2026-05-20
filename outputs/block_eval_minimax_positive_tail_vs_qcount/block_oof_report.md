# Block OOF diagnostics

- Baseline: `qcount`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.581592 | 0.000009 | 0.000259 | 0.000586 | 0.000096 | 0.000091 | 0.000135 | -0.000329 | -0.000404 | -0.001124 | -0.000798 | True |
| minimax_positive_tail | 0.581830 | 0.000005 | 0.000022 | 0.000037 | 0.000026 | 0.000002 | 0.000004 | -0.000024 | -0.000030 | -0.000022 | -0.000023 | True |
| qcount | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qcount | all | 450 | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount | early_third | 151 | 0.581015 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount | mid_third | 147 | 0.571831 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount | late_third | 152 | 0.592373 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount | tail_20pct | 95 | 0.598552 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | all | 450 | 0.581592 | 0.000259 | 0.000009 | 0.000259 | 0.000502 |
| multi_signal | early_third | 151 | 0.580429 | 0.000586 | 0.000133 | 0.000586 | 0.001028 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000096 | -0.000324 | 0.000096 | 0.000515 |
| multi_signal | late_third | 152 | 0.592282 | 0.000091 | -0.000329 | 0.000091 | 0.000518 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000135 | -0.000404 | 0.000135 | 0.000664 |
| minimax_positive_tail | all | 450 | 0.581830 | 0.000022 | 0.000005 | 0.000022 | 0.000039 |
| minimax_positive_tail | early_third | 151 | 0.580977 | 0.000037 | 0.000007 | 0.000037 | 0.000067 |
| minimax_positive_tail | mid_third | 147 | 0.571805 | 0.000026 | -0.000006 | 0.000026 | 0.000057 |
| minimax_positive_tail | late_third | 152 | 0.592371 | 0.000002 | -0.000024 | 0.000002 | 0.000029 |
| minimax_positive_tail | tail_20pct | 95 | 0.598548 | 0.000004 | -0.000030 | 0.000004 | 0.000039 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| qcount | Q1 | 0.655598 | 0.000000 |
| qcount | Q2 | 0.642916 | 0.000000 |
| qcount | Q3 | 0.605835 | 0.000000 |
| qcount | S1 | 0.550398 | 0.000000 |
| qcount | S2 | 0.565627 | 0.000000 |
| qcount | S3 | 0.528912 | 0.000000 |
| qcount | S4 | 0.597326 | 0.000000 |
| multi_signal | Q1 | 0.656396 | -0.000798 |
| multi_signal | Q2 | 0.642320 | 0.000596 |
| multi_signal | Q3 | 0.605681 | 0.000154 |
| multi_signal | S1 | 0.550509 | -0.000111 |
| multi_signal | S2 | 0.565290 | 0.000336 |
| multi_signal | S3 | 0.529003 | -0.000091 |
| multi_signal | S4 | 0.596773 | 0.000553 |
| minimax_positive_tail | Q1 | 0.655613 | -0.000015 |
| minimax_positive_tail | Q2 | 0.642906 | 0.000010 |
| minimax_positive_tail | Q3 | 0.605822 | 0.000012 |
| minimax_positive_tail | S1 | 0.550402 | -0.000004 |
| minimax_positive_tail | S2 | 0.565609 | 0.000018 |
| minimax_positive_tail | S3 | 0.528934 | -0.000023 |
| minimax_positive_tail | S4 | 0.597308 | 0.000018 |
