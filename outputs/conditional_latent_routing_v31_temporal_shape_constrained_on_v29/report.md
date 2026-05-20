# Conditional latent routing

- Base OOF: `0.544772`
- Routed OOF: `0.538054`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.584413 | 0.581954 | 0.002459 | 1 |
| Q1 | q1_temporal_momentum_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.581954 | 0.579841 | 0.002113 | 2 |
| Q1 | q1_temporal_momentum_logreg | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.579841 | 0.577564 | 0.002276 | 3 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.597428 | 0.592155 | 0.005273 | 1 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.592155 | 0.591037 | 0.001118 | 2 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.580165 | 0.570523 | 0.009642 | 1 |
| Q3 | q3_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.570523 | 0.567221 | 0.003302 | 2 |
| Q3 | q3_temporal_extreme_logreg | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.567221 | 0.566194 | 0.001027 | 3 |
| S1 | s1_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.523509 | 0.522492 | 0.001017 | 1 |
| S2 | s2_temporal_momentum_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.497488 | 0.493853 | 0.003635 | 1 |
| S2 | s2_temporal_momentum_logreg | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.493853 | 0.492802 | 0.001051 | 2 |
| S3 | s3_temporal_acceleration_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.477055 | 0.474871 | 0.002184 | 1 |
| S3 | s3_temporal_extreme_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.474871 | 0.472705 | 0.002166 | 2 |
| S3 | s3_temporal_acceleration_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.472705 | 0.471607 | 0.001098 | 3 |
| S4 | s4_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.553348 | 0.548047 | 0.005301 | 1 |
| S4 | s4_temporal_momentum_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.548047 | 0.545807 | 0.002240 | 2 |
| S4 | s4_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.545807 | 0.544684 | 0.001123 | 3 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.544772 | 0.584413 | 0.597428 | 0.580165 | 0.523509 | 0.497488 | 0.477055 | 0.553348 |
| conditional_latent_routing | 0.538054 | 0.577564 | 0.591037 | 0.566194 | 0.522492 | 0.492802 | 0.471607 | 0.544684 |

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
