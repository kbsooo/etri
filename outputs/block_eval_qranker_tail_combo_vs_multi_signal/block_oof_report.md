# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qranker_q3q1tail_s4_q2_s1 | 0.580692 | 0.000136 | 0.000900 | 0.000000 | 0.000570 | 0.002114 | 0.002757 | 0.000016 | -0.000626 | -0.000764 | 0.000000 | True |
| qranker_q3q1tail_s4_q2 | 0.580868 | 0.000006 | 0.000724 | 0.000000 | 0.000144 | 0.002004 | 0.002757 | -0.000052 | -0.000626 | -0.000545 | 0.000000 | True |
| tail_q3_support_s4 | 0.581296 | 0.000024 | 0.000296 | 0.000000 | 0.000047 | 0.000832 | 0.000859 | 0.000156 | 0.000024 | -0.000613 | 0.000000 | True |
| qranker_q3q1tail_s4 | 0.580908 | -0.000040 | 0.000685 | 0.000000 | 0.000047 | 0.001981 | 0.002699 | -0.000104 | -0.000710 | -0.000789 | 0.000000 | False |
| qranker_q3tail_s4 | 0.581045 | -0.000162 | 0.000548 | 0.000000 | 0.000047 | 0.001576 | 0.002050 | -0.000448 | -0.001259 | -0.000657 | 0.000000 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| tail_q3_support_s4 | all | 450 | 0.581296 | 0.000296 | 0.000024 | 0.000296 | 0.000579 |
| tail_q3_support_s4 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| tail_q3_support_s4 | mid_third | 147 | 0.571687 | 0.000047 | -0.000370 | 0.000047 | 0.000473 |
| tail_q3_support_s4 | late_third | 152 | 0.591450 | 0.000832 | 0.000156 | 0.000832 | 0.001533 |
| tail_q3_support_s4 | tail_20pct | 95 | 0.597558 | 0.000859 | 0.000024 | 0.000859 | 0.001777 |
| qranker_q3tail_s4 | all | 450 | 0.581045 | 0.000548 | -0.000162 | 0.000548 | 0.001334 |
| qranker_q3tail_s4 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_q3tail_s4 | mid_third | 147 | 0.571687 | 0.000047 | -0.000370 | 0.000047 | 0.000473 |
| qranker_q3tail_s4 | late_third | 152 | 0.590706 | 0.001576 | -0.000448 | 0.001576 | 0.003870 |
| qranker_q3tail_s4 | tail_20pct | 95 | 0.596367 | 0.002050 | -0.001259 | 0.002050 | 0.005838 |
| qranker_q3q1tail_s4 | all | 450 | 0.580908 | 0.000685 | -0.000040 | 0.000685 | 0.001499 |
| qranker_q3q1tail_s4 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_q3q1tail_s4 | mid_third | 147 | 0.571687 | 0.000047 | -0.000370 | 0.000047 | 0.000473 |
| qranker_q3q1tail_s4 | late_third | 152 | 0.590300 | 0.001981 | -0.000104 | 0.001981 | 0.004311 |
| qranker_q3q1tail_s4 | tail_20pct | 95 | 0.595718 | 0.002699 | -0.000710 | 0.002699 | 0.006568 |
| qranker_q3q1tail_s4_q2 | all | 450 | 0.580868 | 0.000724 | 0.000006 | 0.000724 | 0.001526 |
| qranker_q3q1tail_s4_q2 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_q3q1tail_s4_q2 | mid_third | 147 | 0.571591 | 0.000144 | -0.000271 | 0.000144 | 0.000572 |
| qranker_q3q1tail_s4_q2 | late_third | 152 | 0.590278 | 0.002004 | -0.000052 | 0.002004 | 0.004319 |
| qranker_q3q1tail_s4_q2 | tail_20pct | 95 | 0.595660 | 0.002757 | -0.000626 | 0.002757 | 0.006602 |
| qranker_q3q1tail_s4_q2_s1 | all | 450 | 0.580692 | 0.000900 | 0.000136 | 0.000900 | 0.001755 |
| qranker_q3q1tail_s4_q2_s1 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_q3q1tail_s4_q2_s1 | mid_third | 147 | 0.571165 | 0.000570 | -0.000217 | 0.000570 | 0.001367 |
| qranker_q3q1tail_s4_q2_s1 | late_third | 152 | 0.590167 | 0.002114 | 0.000016 | 0.002114 | 0.004456 |
| qranker_q3q1tail_s4_q2_s1 | tail_20pct | 95 | 0.595660 | 0.002757 | -0.000626 | 0.002757 | 0.006602 |

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
| tail_q3_support_s4 | Q1 | 0.656396 | 0.000000 |
| tail_q3_support_s4 | Q2 | 0.642320 | 0.000000 |
| tail_q3_support_s4 | Q3 | 0.602598 | 0.003082 |
| tail_q3_support_s4 | S1 | 0.550509 | 0.000000 |
| tail_q3_support_s4 | S2 | 0.565290 | 0.000000 |
| tail_q3_support_s4 | S3 | 0.529003 | 0.000000 |
| tail_q3_support_s4 | S4 | 0.594033 | 0.002740 |
| qranker_q3tail_s4 | Q1 | 0.656396 | 0.000000 |
| qranker_q3tail_s4 | Q2 | 0.642320 | 0.000000 |
| qranker_q3tail_s4 | Q3 | 0.597390 | 0.008290 |
| qranker_q3tail_s4 | S1 | 0.550509 | 0.000000 |
| qranker_q3tail_s4 | S2 | 0.565290 | 0.000000 |
| qranker_q3tail_s4 | S3 | 0.529003 | 0.000000 |
| qranker_q3tail_s4 | S4 | 0.594033 | 0.002740 |
| qranker_q3q1tail_s4 | Q1 | 0.653558 | 0.002839 |
| qranker_q3q1tail_s4 | Q2 | 0.642320 | 0.000000 |
| qranker_q3q1tail_s4 | Q3 | 0.597390 | 0.008290 |
| qranker_q3q1tail_s4 | S1 | 0.550509 | 0.000000 |
| qranker_q3q1tail_s4 | S2 | 0.565290 | 0.000000 |
| qranker_q3q1tail_s4 | S3 | 0.529003 | 0.000000 |
| qranker_q3q1tail_s4 | S4 | 0.594033 | 0.002740 |
| qranker_q3q1tail_s4_q2 | Q1 | 0.653558 | 0.002839 |
| qranker_q3q1tail_s4_q2 | Q2 | 0.642163 | 0.000157 |
| qranker_q3q1tail_s4_q2 | Q3 | 0.597390 | 0.008290 |
| qranker_q3q1tail_s4_q2 | S1 | 0.550509 | 0.000000 |
| qranker_q3q1tail_s4_q2 | S2 | 0.565290 | 0.000000 |
| qranker_q3q1tail_s4_q2 | S3 | 0.529003 | 0.000000 |
| qranker_q3q1tail_s4_q2 | S4 | 0.594033 | 0.002740 |
| qranker_q3q1tail_s4_q2_s1 | Q1 | 0.653558 | 0.002839 |
| qranker_q3q1tail_s4_q2_s1 | Q2 | 0.642163 | 0.000157 |
| qranker_q3q1tail_s4_q2_s1 | Q3 | 0.597390 | 0.008290 |
| qranker_q3q1tail_s4_q2_s1 | S1 | 0.549735 | 0.000774 |
| qranker_q3q1tail_s4_q2_s1 | S2 | 0.565290 | 0.000000 |
| qranker_q3q1tail_s4_q2_s1 | S3 | 0.529003 | 0.000000 |
| qranker_q3q1tail_s4_q2_s1 | S4 | 0.594033 | 0.002740 |
