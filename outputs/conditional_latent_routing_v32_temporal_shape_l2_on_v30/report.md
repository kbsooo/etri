# Conditional latent routing

- Base OOF: `0.535694`
- Routed OOF: `0.533214`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.576137 | 0.575066 | 0.001072 | 1 |
| Q1 | q1_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.575066 | 0.574467 | 0.000599 | 2 |
| Q1 | q1_temporal_acceleration_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.574467 | 0.574088 | 0.000379 | 3 |
| Q1 | q1_temporal_momentum_proto | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.574088 | 0.573840 | 0.000248 | 4 |
| Q1 | q1_temporal_extreme_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.573840 | 0.573598 | 0.000241 | 5 |
| Q1 | q1_temporal_momentum_logreg | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.573598 | 0.573486 | 0.000113 | 6 |
| Q2 | q2_temporal_extreme_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.588109 | 0.587019 | 0.001089 | 1 |
| Q2 | q2_temporal_acceleration_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.587019 | 0.586184 | 0.000836 | 2 |
| Q2 | q2_temporal_extreme_knn_label | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.586184 | 0.586047 | 0.000137 | 3 |
| Q2 | q2_temporal_momentum_logreg | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.586047 | 0.585996 | 0.000051 | 4 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.564253 | 0.562330 | 0.001923 | 1 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.562330 | 0.560849 | 0.001481 | 2 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.560849 | 0.559776 | 0.001073 | 3 |
| Q3 | q3_temporal_acceleration_logreg | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.559776 | 0.559416 | 0.000360 | 4 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.559416 | 0.559150 | 0.000267 | 5 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.559150 | 0.558924 | 0.000225 | 6 |
| S1 | s1_temporal_momentum_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.520553 | 0.520100 | 0.000453 | 1 |
| S1 | s1_temporal_acceleration_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.520100 | 0.519770 | 0.000330 | 2 |
| S1 | s1_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.519770 | 0.519620 | 0.000150 | 3 |
| S1 | s1_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.519620 | 0.519547 | 0.000073 | 4 |
| S1 | s1_temporal_acceleration_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.519547 | 0.519466 | 0.000080 | 5 |
| S1 | s1_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.519466 | 0.519394 | 0.000073 | 6 |
| S2 | s2_temporal_acceleration_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.491305 | 0.491241 | 0.000064 | 1 |
| S2 | s2_temporal_momentum_logreg | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.491241 | 0.491178 | 0.000063 | 2 |
| S3 | s3_temporal_acceleration_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.468053 | 0.466652 | 0.001402 | 1 |
| S3 | s3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.466652 | 0.465985 | 0.000667 | 2 |
| S3 | s3_temporal_extreme_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.465985 | 0.465372 | 0.000612 | 3 |
| S3 | s3_temporal_extreme_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.465372 | 0.464998 | 0.000374 | 4 |
| S3 | s3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.464998 | 0.464649 | 0.000349 | 5 |
| S3 | s3_temporal_acceleration_knn_label | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.464649 | 0.464365 | 0.000285 | 6 |
| S4 | s4_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.541448 | 0.540760 | 0.000688 | 1 |
| S4 | s4_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.540760 | 0.540157 | 0.000603 | 2 |
| S4 | s4_temporal_extreme_proto | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.540157 | 0.539635 | 0.000522 | 3 |
| S4 | s4_temporal_extreme_proto | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.539635 | 0.539287 | 0.000348 | 4 |
| S4 | s4_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.539287 | 0.539221 | 0.000065 | 5 |
| S4 | s4_temporal_momentum_hgb | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.539221 | 0.539153 | 0.000068 | 6 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.535694 | 0.576137 | 0.588109 | 0.564253 | 0.520553 | 0.491305 | 0.468053 | 0.541448 |
| conditional_latent_routing | 0.533214 | 0.573486 | 0.585996 | 0.558924 | 0.519394 | 0.491178 | 0.464365 | 0.539153 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.564253 | 0.562282 | 0.001971 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.564253 | 0.562330 | 0.001923 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.564253 | 0.562424 | 0.001829 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.564253 | 0.562494 | 0.001759 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.564253 | 0.562539 | 0.001714 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.564253 | 0.562820 | 0.001433 |
| S3 | s3_temporal_acceleration_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.468053 | 0.466652 | 0.001402 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.564253 | 0.562934 | 0.001319 |
| S3 | s3_temporal_acceleration_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.468053 | 0.466739 | 0.001314 |
| S3 | s3_temporal_acceleration_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.468053 | 0.466836 | 0.001218 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.564253 | 0.563063 | 0.001190 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.564253 | 0.563068 | 0.001185 |
| Q1 | q1_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.576137 | 0.575023 | 0.001114 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.564253 | 0.563160 | 0.001093 |
| Q2 | q2_temporal_extreme_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.588109 | 0.587019 | 0.001089 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.564253 | 0.563173 | 0.001080 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.564253 | 0.563180 | 0.001073 |
| Q1 | q1_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.576137 | 0.575066 | 0.001072 |
| S3 | s3_temporal_acceleration_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.468053 | 0.466986 | 0.001068 |
| Q1 | q1_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.576137 | 0.575075 | 0.001063 |
