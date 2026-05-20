# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v4 | 0.578841 | 0.000962 | 0.002751 | 0.000000 | 0.000859 | 0.007314 | 0.010367 | 0.002205 | 0.002123 | -0.002191 | 0.000000 | True |
| new_tail_decoder_v3 | 0.579032 | 0.000782 | 0.002560 | 0.000000 | 0.000859 | 0.006748 | 0.009462 | 0.001739 | 0.001385 | -0.000595 | 0.000000 | True |
| oldbalanced_plus_q1fastmid | 0.580760 | 0.000277 | 0.000832 | 0.000000 | 0.000956 | 0.001539 | 0.001150 | 0.000458 | 0.000037 | -0.000489 | 0.000000 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| new_tail_decoder_v3 | all | 450 | 0.579032 | 0.002560 | 0.000782 | 0.002560 | 0.004451 |
| new_tail_decoder_v3 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| new_tail_decoder_v3 | mid_third | 147 | 0.570876 | 0.000859 | -0.000451 | 0.000859 | 0.002180 |
| new_tail_decoder_v3 | late_third | 152 | 0.585534 | 0.006748 | 0.001739 | 0.006748 | 0.012178 |
| new_tail_decoder_v3 | tail_20pct | 95 | 0.588955 | 0.009462 | 0.001385 | 0.009462 | 0.017892 |
| hgb_tail_decoder_v4 | all | 450 | 0.578841 | 0.002751 | 0.000962 | 0.002751 | 0.004739 |
| hgb_tail_decoder_v4 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v4 | mid_third | 147 | 0.570876 | 0.000859 | -0.000451 | 0.000859 | 0.002180 |
| hgb_tail_decoder_v4 | late_third | 152 | 0.584968 | 0.007314 | 0.002205 | 0.007314 | 0.013047 |
| hgb_tail_decoder_v4 | tail_20pct | 95 | 0.588051 | 0.010367 | 0.002123 | 0.010367 | 0.019346 |
| oldbalanced_plus_q1fastmid | all | 450 | 0.580760 | 0.000832 | 0.000277 | 0.000832 | 0.001417 |
| oldbalanced_plus_q1fastmid | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| oldbalanced_plus_q1fastmid | mid_third | 147 | 0.570779 | 0.000956 | -0.000355 | 0.000956 | 0.002288 |
| oldbalanced_plus_q1fastmid | late_third | 152 | 0.590742 | 0.001539 | 0.000458 | 0.001539 | 0.002641 |
| oldbalanced_plus_q1fastmid | tail_20pct | 95 | 0.597267 | 0.001150 | 0.000037 | 0.001150 | 0.002404 |

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
| new_tail_decoder_v3 | Q1 | 0.653391 | 0.003005 |
| new_tail_decoder_v3 | Q2 | 0.631202 | 0.011118 |
| new_tail_decoder_v3 | Q3 | 0.579802 | 0.025879 |
| new_tail_decoder_v3 | S1 | 0.549735 | 0.000774 |
| new_tail_decoder_v3 | S2 | 0.565290 | 0.000000 |
| new_tail_decoder_v3 | S3 | 0.525282 | 0.003721 |
| new_tail_decoder_v3 | S4 | 0.594033 | 0.002740 |
| hgb_tail_decoder_v4 | Q1 | 0.653391 | 0.003005 |
| hgb_tail_decoder_v4 | Q2 | 0.631202 | 0.011118 |
| hgb_tail_decoder_v4 | Q3 | 0.575844 | 0.029837 |
| hgb_tail_decoder_v4 | S1 | 0.549735 | 0.000774 |
| hgb_tail_decoder_v4 | S2 | 0.565290 | 0.000000 |
| hgb_tail_decoder_v4 | S3 | 0.525282 | 0.003721 |
| hgb_tail_decoder_v4 | S4 | 0.594033 | 0.002740 |
| oldbalanced_plus_q1fastmid | Q1 | 0.652467 | 0.003929 |
| oldbalanced_plus_q1fastmid | Q2 | 0.642163 | 0.000157 |
| oldbalanced_plus_q1fastmid | Q3 | 0.602504 | 0.003176 |
| oldbalanced_plus_q1fastmid | S1 | 0.549735 | 0.000774 |
| oldbalanced_plus_q1fastmid | S2 | 0.565290 | 0.000000 |
| oldbalanced_plus_q1fastmid | S3 | 0.529003 | 0.000000 |
| oldbalanced_plus_q1fastmid | S4 | 0.594033 | 0.002740 |
