# Conditional latent routing

- Base OOF: `0.478230`
- Routed OOF: `0.477997`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100.000000 | 130.000000 | 0.521789 | 0.521188 | 0.000601 | 1 |
| Q2 | joint_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159.000000 | 193.000000 | 0.534703 | 0.534668 | 0.000035 | 1 |
| Q3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S1 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100.000000 | 130.000000 | 0.451165 | 0.450855 | 0.000310 | 1 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159.000000 | 193.000000 | 0.408038 | 0.407355 | 0.000683 | 1 |
| S4 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.478230 | 0.521789 | 0.534703 | 0.498183 | 0.467950 | 0.451165 | 0.408038 | 0.465779 |
| conditional_latent_routing | 0.477997 | 0.521188 | 0.534668 | 0.498183 | 0.467950 | 0.450855 | 0.407355 | 0.465779 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.408038 | 0.407355 | 0.000683 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.408038 | 0.407401 | 0.000637 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.521789 | 0.521188 | 0.000601 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.521789 | 0.521242 | 0.000547 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.408038 | 0.407513 | 0.000525 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.521789 | 0.521274 | 0.000515 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.408038 | 0.407601 | 0.000437 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.521789 | 0.521360 | 0.000429 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.408038 | 0.407715 | 0.000323 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.451165 | 0.450855 | 0.000310 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.451165 | 0.450875 | 0.000290 |
| S3 | joint_cross_family_late_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.408038 | 0.407766 | 0.000272 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.451165 | 0.450892 | 0.000272 |
| S3 | joint_cross_family_late_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.408038 | 0.407777 | 0.000261 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.451165 | 0.450911 | 0.000253 |
| Q1 | joint_family_late_residual_behavior_neural_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.521789 | 0.521542 | 0.000246 |
| S3 | joint_cross_family_late_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.408038 | 0.407798 | 0.000240 |
| S3 | joint_cross_family_late_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.408038 | 0.407833 | 0.000205 |
| S2 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.451165 | 0.450969 | 0.000195 |
| S3 | joint_cross_family_late_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.408038 | 0.407850 | 0.000188 |
