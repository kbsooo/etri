# Conditional latent routing

- Base OOF: `0.479449`
- Routed OOF: `0.478327`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116.000000 | 120.000000 | 0.524853 | 0.521789 | 0.003064 | 1 |
| Q2 | joint_residual_behavior_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291.000000 | 57.000000 | 0.535474 | 0.534964 | 0.000510 | 1 |
| Q2 | joint_target_late_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116.000000 | 120.000000 | 0.534964 | 0.534703 | 0.000261 | 2 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100.000000 | 130.000000 | 0.500706 | 0.498183 | 0.002523 | 1 |
| S1 | joint_target_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159.000000 | 193.000000 | 0.468781 | 0.468009 | 0.000773 | 1 |
| S2 | joint_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100.000000 | 130.000000 | 0.451615 | 0.451200 | 0.000415 | 1 |
| S3 | joint_s23_late_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116.000000 | 120.000000 | 0.408746 | 0.408435 | 0.000312 | 1 |
| S4 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.479449 | 0.524853 | 0.535474 | 0.500706 | 0.468781 | 0.451615 | 0.408746 | 0.465970 |
| conditional_latent_routing | 0.478327 | 0.521789 | 0.534703 | 0.498183 | 0.468009 | 0.451200 | 0.408435 | 0.465970 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.524853 | 0.521789 | 0.003064 |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.524853 | 0.522200 | 0.002653 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.500706 | 0.498183 | 0.002523 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.500706 | 0.498500 | 0.002206 |
| Q1 | joint_target_late_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.524853 | 0.522648 | 0.002206 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.500706 | 0.498596 | 0.002109 |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.524853 | 0.522811 | 0.002043 |
| Q1 | joint_target_late_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.524853 | 0.522813 | 0.002040 |
| Q1 | joint_target_late_residual_behavior_neural_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.524853 | 0.522881 | 0.001973 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.500706 | 0.498738 | 0.001967 |
| Q1 | joint_target_late_residual_behavior_neural_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.524853 | 0.522893 | 0.001960 |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.524853 | 0.522955 | 0.001898 |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.524853 | 0.522959 | 0.001894 |
| Q3 | joint_target_late_residual_behavior_neural_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.500706 | 0.498814 | 0.001891 |
| Q1 | joint_target_late_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.524853 | 0.523195 | 0.001658 |
| Q1 | joint_target_late_residual_behavior_neural_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.524853 | 0.523201 | 0.001653 |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.524853 | 0.523206 | 0.001647 |
| Q1 | joint_target_late_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.524853 | 0.523231 | 0.001622 |
| Q3 | joint_target_late_residual_behavior_neural_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.500706 | 0.499123 | 0.001583 |
| Q3 | joint_target_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.500706 | 0.499133 | 0.001573 |
