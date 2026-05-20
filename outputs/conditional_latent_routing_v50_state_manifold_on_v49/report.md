# Conditional latent routing

- Base OOF: `0.507926`
- Routed OOF: `0.506657`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_state_recurrence_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.550468 | 0.550023 | 0.000445 | 1 |
| Q2 | q2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.560445 | 0.559694 | 0.000751 | 1 |
| Q2 | q2_temporal_state_transition_logreg | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.559694 | 0.559150 | 0.000544 | 2 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.529737 | 0.526272 | 0.003466 | 1 |
| S1 | s1_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.498210 | 0.497572 | 0.000638 | 1 |
| S1 | s1_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.497572 | 0.497013 | 0.000559 | 2 |
| S2 | s2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.478764 | 0.478511 | 0.000253 | 1 |
| S3 | s3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.433767 | 0.432870 | 0.000897 | 1 |
| S3 | s3_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.432870 | 0.432507 | 0.000363 | 2 |
| S4 | s4_temporal_state_recurrence_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.504089 | 0.503270 | 0.000819 | 1 |
| S4 | s4_temporal_state_recurrence_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.503270 | 0.503123 | 0.000147 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.507926 | 0.550468 | 0.560445 | 0.529737 | 0.498210 | 0.478764 | 0.433767 | 0.504089 |
| conditional_latent_routing | 0.506657 | 0.550023 | 0.559150 | 0.526272 | 0.497013 | 0.478511 | 0.432507 | 0.503123 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.529737 | 0.526272 | 0.003466 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.529737 | 0.526651 | 0.003086 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.529737 | 0.527187 | 0.002551 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.529737 | 0.527724 | 0.002013 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.529737 | 0.527879 | 0.001859 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.529737 | 0.527955 | 0.001782 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.529737 | 0.528022 | 0.001715 |
| Q3 | q3_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.529737 | 0.528054 | 0.001683 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.529737 | 0.528193 | 0.001545 |
| Q3 | q3_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.529737 | 0.528196 | 0.001541 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.529737 | 0.528284 | 0.001454 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.529737 | 0.528372 | 0.001366 |
| Q3 | q3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.529737 | 0.528421 | 0.001317 |
| Q3 | q3_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.529737 | 0.528435 | 0.001303 |
| Q3 | q3_temporal_state_transition_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.529737 | 0.528459 | 0.001278 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.529737 | 0.528489 | 0.001248 |
| Q3 | q3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.529737 | 0.528516 | 0.001221 |
| Q3 | q3_temporal_state_transition_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.529737 | 0.528561 | 0.001177 |
| Q3 | q3_temporal_state_transition_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.529737 | 0.528611 | 0.001126 |
| Q3 | q3_temporal_state_transition_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.529737 | 0.528638 | 0.001099 |
