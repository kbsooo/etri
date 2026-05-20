# Conditional latent routing

- Base OOF: `0.509456`
- Routed OOF: `0.507926`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.551278 | 0.550617 | 0.000661 | 1 |
| Q1 | q1_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.550617 | 0.550468 | 0.000149 | 2 |
| Q2 | q2_temporal_state_recurrence_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.562225 | 0.560974 | 0.001250 | 1 |
| Q2 | q2_temporal_state_recurrence_logreg | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.560974 | 0.560445 | 0.000530 | 2 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.532111 | 0.530015 | 0.002096 | 1 |
| Q3 | q3_temporal_state_recurrence_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.530015 | 0.529737 | 0.000277 | 2 |
| S1 | s1_temporal_state_recurrence_hgb | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.498505 | 0.498210 | 0.000295 | 1 |
| S2 | s2_temporal_state_recurrence_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.479181 | 0.478764 | 0.000416 | 1 |
| S3 | s3_temporal_state_recurrence_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.435259 | 0.433767 | 0.001492 | 1 |
| S4 | s4_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.507634 | 0.504089 | 0.003545 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.509456 | 0.551278 | 0.562225 | 0.532111 | 0.498505 | 0.479181 | 0.435259 | 0.507634 |
| conditional_latent_routing | 0.507926 | 0.550468 | 0.560445 | 0.529737 | 0.498210 | 0.478764 | 0.433767 | 0.504089 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | s4_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.507634 | 0.504089 | 0.003545 |
| S4 | s4_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.507634 | 0.504262 | 0.003372 |
| S4 | s4_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.507634 | 0.504632 | 0.003002 |
| S4 | s4_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.507634 | 0.505254 | 0.002380 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.532111 | 0.530015 | 0.002096 |
| S4 | s4_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.507634 | 0.505686 | 0.001948 |
| S4 | s4_temporal_state_recurrence_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.507634 | 0.505806 | 0.001827 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.532111 | 0.530319 | 0.001792 |
| S4 | s4_temporal_state_recurrence_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.507634 | 0.505917 | 0.001717 |
| S4 | s4_temporal_state_recurrence_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.507634 | 0.506042 | 0.001592 |
| S3 | s3_temporal_state_recurrence_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.435259 | 0.433679 | 0.001580 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.532111 | 0.530589 | 0.001522 |
| S4 | s4_temporal_state_recurrence_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.507634 | 0.506133 | 0.001501 |
| S3 | s3_temporal_state_recurrence_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.435259 | 0.433767 | 0.001492 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.532111 | 0.530681 | 0.001430 |
| S4 | s4_temporal_state_recurrence_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.507634 | 0.506215 | 0.001419 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.532111 | 0.530759 | 0.001352 |
| S3 | s3_temporal_state_recurrence_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.435259 | 0.433967 | 0.001292 |
| S4 | s4_temporal_state_recurrence_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.507634 | 0.506342 | 0.001292 |
| S4 | s4_temporal_state_recurrence_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.507634 | 0.506358 | 0.001276 |
