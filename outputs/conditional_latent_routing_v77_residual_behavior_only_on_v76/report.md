# Conditional latent routing

- Base OOF: `0.480978`
- Routed OOF: `0.480863`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | joint_residual_behavior_neural_multiview_knn_resid | first_half | 0.025000 | 0.000275 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.538870 | 0.538595 |
| Q3 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S2 | joint_residual_behavior_neural_metric_knn_resid | mid | 0.050000 | 0.000145 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.453129 | 0.452984 |
| S3 | joint_residual_behavior_neural_multiview_metric_knn_resid | mid | 0.075000 | 0.000386 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.411283 | 0.410897 |
| S4 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.480978 | 0.525443 | 0.538870 | 0.501289 | 0.469875 | 0.453129 | 0.411283 | 0.466958 |
| conditional_latent_routing | 0.480863 | 0.525443 | 0.538595 | 0.501289 | 0.469875 | 0.452984 | 0.410897 | 0.466958 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_residual_behavior_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.411283 | 0.410897 | 0.000386 |
| S3 | joint_residual_behavior_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.411283 | 0.410929 | 0.000354 |
| S3 | joint_residual_behavior_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.411283 | 0.410936 | 0.000347 |
| Q2 | joint_residual_behavior_neural_multiview_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.538870 | 0.538595 | 0.000275 |
| S3 | joint_residual_behavior_neural_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.411283 | 0.411039 | 0.000244 |
| S3 | joint_residual_behavior_neural_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.411283 | 0.411047 | 0.000236 |
| S3 | joint_residual_behavior_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.411283 | 0.411060 | 0.000223 |
| S3 | joint_residual_behavior_neural_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.411283 | 0.411113 | 0.000170 |
| S3 | joint_residual_behavior_neural_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.411283 | 0.411127 | 0.000156 |
| S2 | joint_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.453129 | 0.452978 | 0.000151 |
| S2 | joint_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.453129 | 0.452984 | 0.000145 |
| S3 | joint_residual_behavior_neural_multiview_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.411283 | 0.411142 | 0.000141 |
| S3 | joint_residual_behavior_neural_multiview_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.411283 | 0.411151 | 0.000132 |
| S2 | joint_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.453129 | 0.453010 | 0.000119 |
| S3 | joint_residual_behavior_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.411283 | 0.411164 | 0.000118 |
| S3 | joint_residual_behavior_neural_multiview_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.411283 | 0.411183 | 0.000100 |
| Q2 | joint_residual_behavior_neural_multiview_knn_resid | all | 0.000000 | 1.000001 | 0.025000 | 450 | 250 | 0.538870 | 0.538771 | 0.000099 |
| S2 | joint_residual_behavior_neural_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.453129 | 0.453033 | 0.000096 |
| S3 | joint_residual_behavior_neural_multiview_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.411283 | 0.411203 | 0.000080 |
| Q2 | joint_residual_behavior_neural_multiview_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.538870 | 0.538827 | 0.000043 |
