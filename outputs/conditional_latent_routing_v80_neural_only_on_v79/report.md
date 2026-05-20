# Conditional latent routing

- Base OOF: `0.478230`
- Routed OOF: `0.477768`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.521789 | 0.521188 | 0.000601 | 1 |
| Q1 | joint_neural_multiview_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.521188 | 0.520922 | 0.000265 | 2 |
| Q2 | joint_residual_behavior_neural_metric_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.534703 | 0.534601 | 0.000102 | 1 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.498183 | 0.497878 | 0.000305 | 1 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.497878 | 0.497697 | 0.000181 | 2 |
| S1 | joint_neural_gated_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.467950 | 0.467589 | 0.000361 | 1 |
| S1 | joint_s23_late_residual_behavior_neural_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.467589 | 0.467526 | 0.000063 | 2 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.451165 | 0.450855 | 0.000310 | 1 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.408038 | 0.407355 | 0.000683 | 1 |
| S3 | joint_residual_behavior_neural_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.407355 | 0.407026 | 0.000329 | 2 |
| S4 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.465779 | 0.465747 | 0.000032 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.478230 | 0.521789 | 0.534703 | 0.498183 | 0.467950 | 0.451165 | 0.408038 | 0.465779 |
| conditional_latent_routing | 0.477768 | 0.520922 | 0.534601 | 0.497697 | 0.467526 | 0.450855 | 0.407026 | 0.465747 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.408038 | 0.407355 | 0.000683 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.408038 | 0.407401 | 0.000637 |
| Q1 | joint_s23_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.521789 | 0.521176 | 0.000613 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.521789 | 0.521188 | 0.000601 |
| Q1 | joint_s23_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.521789 | 0.521192 | 0.000597 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.521789 | 0.521242 | 0.000547 |
| Q1 | joint_s23_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.521789 | 0.521261 | 0.000528 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.408038 | 0.407513 | 0.000525 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.521789 | 0.521274 | 0.000515 |
| Q1 | joint_s23_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.521789 | 0.521290 | 0.000499 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.408038 | 0.407601 | 0.000437 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.521789 | 0.521360 | 0.000429 |
| Q1 | joint_s23_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.521789 | 0.521378 | 0.000411 |
| S1 | joint_neural_gated_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.467950 | 0.467589 | 0.000361 |
| Q1 | joint_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.521789 | 0.521433 | 0.000356 |
| Q1 | joint_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.521789 | 0.521444 | 0.000345 |
| S3 | joint_residual_behavior_neural_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.408038 | 0.407710 | 0.000329 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.408038 | 0.407715 | 0.000323 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.451165 | 0.450855 | 0.000310 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.498183 | 0.497878 | 0.000305 |
