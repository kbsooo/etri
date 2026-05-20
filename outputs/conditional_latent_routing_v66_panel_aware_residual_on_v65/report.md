# Conditional latent routing

- Base OOF: `0.490915`
- Routed OOF: `0.489729`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.534360 | 0.533896 | 0.000464 | 1 |
| Q1 | joint_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.533896 | 0.533569 | 0.000327 | 2 |
| Q2 | joint_pls_logreg | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.543546 | 0.543257 | 0.000289 | 1 |
| Q2 | joint_cross_family_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.543257 | 0.543122 | 0.000136 | 2 |
| Q3 | joint_neural_qs_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.511237 | 0.510184 | 0.001053 | 1 |
| Q3 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.510184 | 0.509450 | 0.000735 | 2 |
| S1 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.480399 | 0.479505 | 0.000894 | 1 |
| S1 | joint_metric_neighbor_hgb | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.479505 | 0.479082 | 0.000423 | 2 |
| S2 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468049 | 0.467023 | 0.001026 | 1 |
| S2 | joint_cross_family_residual_pls_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.467023 | 0.466655 | 0.000368 | 2 |
| S3 | joint_target_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.421222 | 0.419794 | 0.001428 | 1 |
| S4 | joint_cross_family_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.477591 | 0.476735 | 0.000856 | 1 |
| S4 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.476735 | 0.476432 | 0.000303 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.490915 | 0.534360 | 0.543546 | 0.511237 | 0.480399 | 0.468049 | 0.421222 | 0.477591 |
| conditional_latent_routing | 0.489729 | 0.533569 | 0.543122 | 0.509450 | 0.479082 | 0.466655 | 0.419794 | 0.476432 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_target_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.421222 | 0.419794 | 0.001428 |
| S3 | joint_target_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.421222 | 0.419855 | 0.001367 |
| S3 | joint_target_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.421222 | 0.419990 | 0.001232 |
| S3 | joint_target_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.421222 | 0.420094 | 0.001128 |
| S3 | joint_target_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.421222 | 0.420140 | 0.001082 |
| Q3 | joint_neural_qs_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.511237 | 0.510184 | 0.001053 |
| S2 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468049 | 0.467023 | 0.001026 |
| Q3 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.511237 | 0.510267 | 0.000969 |
| S1 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.480399 | 0.479505 | 0.000894 |
| S1 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.480399 | 0.479505 | 0.000894 |
| S3 | joint_target_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.421222 | 0.420330 | 0.000892 |
| S2 | joint_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.468049 | 0.467177 | 0.000872 |
| S2 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468049 | 0.467177 | 0.000871 |
| S2 | joint_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.468049 | 0.467187 | 0.000861 |
| S4 | joint_cross_family_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.477591 | 0.476735 | 0.000856 |
| S4 | joint_q_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.477591 | 0.476735 | 0.000856 |
| S2 | joint_q_residual_pls_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.468049 | 0.467200 | 0.000848 |
| S2 | joint_cross_family_residual_pls_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.468049 | 0.467200 | 0.000848 |
| S3 | joint_target_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.421222 | 0.420385 | 0.000837 |
| Q3 | joint_neural_qs_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.511237 | 0.510414 | 0.000823 |
