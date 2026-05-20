# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qranker_tail_full | 0.580692 | 0.000136 | 0.000900 | 0.000000 | 0.000570 | 0.002114 | 0.002757 | 0.000016 | -0.000626 | -0.000764 | 0.000000 | True |
| qranker_tail_w065 | 0.580839 | 0.000178 | 0.000753 | 0.000000 | 0.000570 | 0.001678 | 0.002058 | 0.000251 | -0.000195 | -0.000764 | 0.000000 | True |
| tail_q3_support_s4 | 0.581296 | 0.000024 | 0.000296 | 0.000000 | 0.000047 | 0.000832 | 0.000859 | 0.000156 | 0.000024 | -0.000613 | 0.000000 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_tail_full | all | 450 | 0.580692 | 0.000900 | 0.000136 | 0.000900 | 0.001755 |
| qranker_tail_full | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_tail_full | mid_third | 147 | 0.571165 | 0.000570 | -0.000217 | 0.000570 | 0.001367 |
| qranker_tail_full | late_third | 152 | 0.590167 | 0.002114 | 0.000016 | 0.002114 | 0.004456 |
| qranker_tail_full | tail_20pct | 95 | 0.595660 | 0.002757 | -0.000626 | 0.002757 | 0.006602 |
| qranker_tail_w065 | all | 450 | 0.580839 | 0.000753 | 0.000178 | 0.000753 | 0.001373 |
| qranker_tail_w065 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_tail_w065 | mid_third | 147 | 0.571165 | 0.000570 | -0.000217 | 0.000570 | 0.001367 |
| qranker_tail_w065 | late_third | 152 | 0.590604 | 0.001678 | 0.000251 | 0.001678 | 0.003296 |
| qranker_tail_w065 | tail_20pct | 95 | 0.596359 | 0.002058 | -0.000195 | 0.002058 | 0.004628 |
| tail_q3_support_s4 | all | 450 | 0.581296 | 0.000296 | 0.000024 | 0.000296 | 0.000579 |
| tail_q3_support_s4 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| tail_q3_support_s4 | mid_third | 147 | 0.571687 | 0.000047 | -0.000370 | 0.000047 | 0.000473 |
| tail_q3_support_s4 | late_third | 152 | 0.591450 | 0.000832 | 0.000156 | 0.000832 | 0.001533 |
| tail_q3_support_s4 | tail_20pct | 95 | 0.597558 | 0.000859 | 0.000024 | 0.000859 | 0.001777 |

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
| qranker_tail_full | Q1 | 0.653558 | 0.002839 |
| qranker_tail_full | Q2 | 0.642163 | 0.000157 |
| qranker_tail_full | Q3 | 0.597390 | 0.008290 |
| qranker_tail_full | S1 | 0.549735 | 0.000774 |
| qranker_tail_full | S2 | 0.565290 | 0.000000 |
| qranker_tail_full | S3 | 0.529003 | 0.000000 |
| qranker_tail_full | S4 | 0.594033 | 0.002740 |
| qranker_tail_w065 | Q1 | 0.654473 | 0.001923 |
| qranker_tail_w065 | Q2 | 0.642163 | 0.000157 |
| qranker_tail_w065 | Q3 | 0.599530 | 0.006150 |
| qranker_tail_w065 | S1 | 0.549735 | 0.000774 |
| qranker_tail_w065 | S2 | 0.565290 | 0.000000 |
| qranker_tail_w065 | S3 | 0.529003 | 0.000000 |
| qranker_tail_w065 | S4 | 0.594033 | 0.002740 |
| tail_q3_support_s4 | Q1 | 0.656396 | 0.000000 |
| tail_q3_support_s4 | Q2 | 0.642320 | 0.000000 |
| tail_q3_support_s4 | Q3 | 0.602598 | 0.003082 |
| tail_q3_support_s4 | S1 | 0.550509 | 0.000000 |
| tail_q3_support_s4 | S2 | 0.565290 | 0.000000 |
| tail_q3_support_s4 | S3 | 0.529003 | 0.000000 |
| tail_q3_support_s4 | S4 | 0.594033 | 0.002740 |
