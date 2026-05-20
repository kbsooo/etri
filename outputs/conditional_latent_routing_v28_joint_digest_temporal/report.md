# Conditional latent routing

- Base OOF: `0.557163`
- Routed OOF: `0.546506`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.604281 | 0.593998 | 0.010283 | 1 |
| Q1 | q1_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.593998 | 0.592514 | 0.001484 | 2 |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.592514 | 0.591251 | 0.001263 | 3 |
| Q1 | q1_social_rhythm_knn_label | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.591251 | 0.589963 | 0.001287 | 4 |
| Q1 | q1_social_rhythm_logreg | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.589963 | 0.588780 | 0.001183 | 5 |
| Q2 | q2_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.610811 | 0.605093 | 0.005718 | 1 |
| Q2 | q2_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.605093 | 0.601612 | 0.003481 | 2 |
| Q2 | q2_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.601612 | 0.599651 | 0.001961 | 3 |
| Q2 | q2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.599651 | 0.598801 | 0.000850 | 4 |
| Q2 | q2_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.598801 | 0.598271 | 0.000530 | 5 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.597243 | 0.591266 | 0.005977 | 1 |
| Q3 | q3_phone_recovery_logreg | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.591266 | 0.587078 | 0.004188 | 2 |
| Q3 | q3_temporal_deviation_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.587078 | 0.583872 | 0.003207 | 3 |
| Q3 | q3_phone_recovery_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.583872 | 0.582511 | 0.001361 | 4 |
| Q3 | q3_phone_recovery_logreg | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.582511 | 0.581729 | 0.000782 | 5 |
| S1 | s1_temporal_recovery_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.532737 | 0.529691 | 0.003046 | 1 |
| S1 | s1_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.529691 | 0.527660 | 0.002031 | 2 |
| S1 | s1_temporal_recovery_logreg | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.527660 | 0.526339 | 0.001321 | 3 |
| S1 | s1_temporal_recovery_hgb | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.526339 | 0.525225 | 0.001114 | 4 |
| S1 | s1_temporal_recovery_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.525225 | 0.524744 | 0.000481 | 5 |
| S2 | s2_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.509835 | 0.505292 | 0.004543 | 1 |
| S2 | s2_volatility_shift_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.505292 | 0.502151 | 0.003141 | 2 |
| S2 | s2_circadian_disruption_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.502151 | 0.500446 | 0.001705 | 3 |
| S2 | s2_temporal_deviation_proto | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.500446 | 0.499354 | 0.001092 | 4 |
| S2 | s2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.499354 | 0.498804 | 0.000550 | 5 |
| S3 | s3_temporal_deviation_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.480275 | 0.479363 | 0.000912 | 1 |
| S3 | s3_temporal_deviation_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.479363 | 0.478483 | 0.000880 | 2 |
| S3 | s3_temporal_recovery_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.478483 | 0.477841 | 0.000642 | 3 |
| S3 | s3_phone_recovery_knn_label | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.477841 | 0.477608 | 0.000233 | 4 |
| S3 | s3_body_recovery_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.477608 | 0.477494 | 0.000113 | 5 |
| S4 | s4_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.564959 | 0.562419 | 0.002540 | 1 |
| S4 | s4_modality_desync_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.562419 | 0.560339 | 0.002081 | 2 |
| S4 | s4_modality_desync_proto | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.560339 | 0.558489 | 0.001850 | 3 |
| S4 | s4_temporal_recovery_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.558489 | 0.556977 | 0.001512 | 4 |
| S4 | s4_temporal_recovery_proto | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.556977 | 0.555720 | 0.001257 | 5 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.557163 | 0.604281 | 0.610811 | 0.597243 | 0.532737 | 0.509835 | 0.480275 | 0.564959 |
| conditional_latent_routing | 0.546506 | 0.588780 | 0.598271 | 0.581729 | 0.524744 | 0.498804 | 0.477494 | 0.555720 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.604281 | 0.593998 | 0.010283 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.604281 | 0.594737 | 0.009544 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.604281 | 0.595651 | 0.008630 |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.604281 | 0.596823 | 0.007458 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.604281 | 0.596985 | 0.007296 |
| Q1 | q1_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.604281 | 0.597609 | 0.006672 |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.604281 | 0.598039 | 0.006242 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.597243 | 0.591266 | 0.005977 |
| Q2 | q2_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.610811 | 0.605093 | 0.005718 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.597243 | 0.591550 | 0.005693 |
| Q1 | q1_temporal_deviation_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.604281 | 0.598613 | 0.005668 |
| Q1 | q1_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.604281 | 0.598648 | 0.005633 |
| Q1 | q1_temporal_deviation_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.604281 | 0.598689 | 0.005592 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.604281 | 0.598803 | 0.005478 |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.604281 | 0.598847 | 0.005434 |
| Q1 | q1_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.604281 | 0.598877 | 0.005404 |
| Q1 | q1_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.604281 | 0.599094 | 0.005187 |
| Q1 | q1_temporal_deviation_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.604281 | 0.599176 | 0.005105 |
| Q1 | q1_temporal_recovery_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.604281 | 0.599323 | 0.004958 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.597243 | 0.592316 | 0.004928 |
