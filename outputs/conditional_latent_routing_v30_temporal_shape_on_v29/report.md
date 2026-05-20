# Conditional latent routing

- Base OOF: `0.544772`
- Routed OOF: `0.535694`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_momentum_logreg | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.584413 | 0.581291 | 0.003122 | 1 |
| Q1 | q1_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.581291 | 0.578511 | 0.002779 | 2 |
| Q1 | q1_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.578511 | 0.577098 | 0.001413 | 3 |
| Q1 | q1_temporal_momentum_logreg | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.577098 | 0.576742 | 0.000356 | 4 |
| Q1 | q1_temporal_acceleration_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.576742 | 0.576313 | 0.000429 | 5 |
| Q1 | q1_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.576313 | 0.576137 | 0.000176 | 6 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.597428 | 0.591824 | 0.005604 | 1 |
| Q2 | q2_temporal_extreme_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.591824 | 0.590594 | 0.001230 | 2 |
| Q2 | q2_temporal_extreme_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.590594 | 0.589605 | 0.000989 | 3 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.589605 | 0.588968 | 0.000637 | 4 |
| Q2 | q2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.588968 | 0.588486 | 0.000482 | 5 |
| Q2 | q2_temporal_momentum_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.588486 | 0.588109 | 0.000378 | 6 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.580165 | 0.570523 | 0.009642 | 1 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.570523 | 0.567221 | 0.003302 | 2 |
| Q3 | q3_temporal_extreme_logreg | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.567221 | 0.566194 | 0.001027 | 3 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.566194 | 0.565162 | 0.001033 | 4 |
| Q3 | q3_temporal_acceleration_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.565162 | 0.564517 | 0.000644 | 5 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.564517 | 0.564253 | 0.000264 | 6 |
| S1 | s1_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.523509 | 0.522432 | 0.001077 | 1 |
| S1 | s1_temporal_momentum_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.522432 | 0.521676 | 0.000756 | 2 |
| S1 | s1_temporal_acceleration_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.521676 | 0.521208 | 0.000467 | 3 |
| S1 | s1_temporal_extreme_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.521208 | 0.520964 | 0.000244 | 4 |
| S1 | s1_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.520964 | 0.520730 | 0.000234 | 5 |
| S1 | s1_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.520730 | 0.520553 | 0.000177 | 6 |
| S2 | s2_temporal_momentum_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.497488 | 0.493615 | 0.003874 | 1 |
| S2 | s2_temporal_momentum_logreg | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.493615 | 0.492156 | 0.001458 | 2 |
| S2 | s2_temporal_extreme_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.492156 | 0.491682 | 0.000475 | 3 |
| S2 | s2_temporal_momentum_proto | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.491682 | 0.491489 | 0.000193 | 4 |
| S2 | s2_temporal_acceleration_knn_resid | all | 0.000000 | 1.000001 | 0.025000 | 450 | 250 | 0.491489 | 0.491380 | 0.000109 | 5 |
| S2 | s2_temporal_momentum_knn_label | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.491380 | 0.491305 | 0.000075 | 6 |
| S3 | s3_temporal_extreme_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.477055 | 0.474079 | 0.002976 | 1 |
| S3 | s3_temporal_acceleration_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.474079 | 0.471587 | 0.002491 | 2 |
| S3 | s3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.471587 | 0.470502 | 0.001086 | 3 |
| S3 | s3_temporal_acceleration_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.470502 | 0.469468 | 0.001034 | 4 |
| S3 | s3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.469468 | 0.468641 | 0.000827 | 5 |
| S3 | s3_temporal_extreme_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.468641 | 0.468053 | 0.000587 | 6 |
| S4 | s4_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.553348 | 0.548047 | 0.005301 | 1 |
| S4 | s4_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.548047 | 0.545311 | 0.002736 | 2 |
| S4 | s4_temporal_extreme_proto | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.545311 | 0.543779 | 0.001531 | 3 |
| S4 | s4_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.543779 | 0.542656 | 0.001123 | 4 |
| S4 | s4_temporal_acceleration_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.542656 | 0.542126 | 0.000531 | 5 |
| S4 | s4_temporal_momentum_hgb | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.542126 | 0.541448 | 0.000678 | 6 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.544772 | 0.584413 | 0.597428 | 0.580165 | 0.523509 | 0.497488 | 0.477055 | 0.553348 |
| conditional_latent_routing | 0.535694 | 0.576137 | 0.588109 | 0.564253 | 0.520553 | 0.491305 | 0.468053 | 0.541448 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.580165 | 0.570523 | 0.009642 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.580165 | 0.572689 | 0.007476 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.580165 | 0.573945 | 0.006220 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.597428 | 0.591824 | 0.005604 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.580165 | 0.574812 | 0.005353 |
| S4 | s4_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.553348 | 0.548047 | 0.005301 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.597428 | 0.592155 | 0.005273 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.580165 | 0.575319 | 0.004846 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.597428 | 0.592695 | 0.004733 |
| S4 | s4_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.553348 | 0.548748 | 0.004600 |
| S4 | s4_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.553348 | 0.549336 | 0.004012 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.580165 | 0.576157 | 0.004008 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.597428 | 0.593491 | 0.003938 |
| S2 | s2_temporal_momentum_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.497488 | 0.493615 | 0.003874 |
| S2 | s2_temporal_momentum_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.497488 | 0.493853 | 0.003635 |
| S2 | s2_temporal_momentum_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.497488 | 0.493921 | 0.003567 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.580165 | 0.576812 | 0.003353 |
| Q3 | q3_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.580165 | 0.576881 | 0.003284 |
| S4 | s4_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.553348 | 0.550086 | 0.003262 |
| S2 | s2_temporal_momentum_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.497488 | 0.494357 | 0.003132 |
