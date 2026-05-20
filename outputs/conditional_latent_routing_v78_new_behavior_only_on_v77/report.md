# Conditional latent routing

- Base OOF: `0.480038`
- Routed OOF: `0.479863`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q3 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S2 | joint_cross_family_residual_behavior_neural_metric_knn_resid | first_half | 0.025000 | 0.000060 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.451806 | 0.451745 |
| S2 | joint_target_residual_behavior_neural_knn_resid | late | 0.025000 | 0.000062 | 2 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.451745 | 0.451683 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.100000 | 0.000887 | 1 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.410320 | 0.409433 |
| S3 | joint_cross_family_residual_behavior_neural_knn_resid | mid | 0.100000 | 0.000115 | 2 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.409433 | 0.409318 |
| S4 | joint_cross_family_residual_behavior_neural_knn_resid | first_half | 0.025000 | 0.000100 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.466289 | 0.466189 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.480038 | 0.525112 | 0.536798 | 0.500706 | 0.469235 | 0.451806 | 0.410320 | 0.466289 |
| conditional_latent_routing | 0.479863 | 0.525112 | 0.536798 | 0.500706 | 0.469235 | 0.451683 | 0.409318 | 0.466189 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.410320 | 0.409433 | 0.000887 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.410320 | 0.409504 | 0.000816 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.410320 | 0.409510 | 0.000810 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.410320 | 0.409546 | 0.000774 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.410320 | 0.409587 | 0.000733 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.410320 | 0.409665 | 0.000655 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.410320 | 0.409682 | 0.000637 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.410320 | 0.409719 | 0.000601 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.410320 | 0.409797 | 0.000523 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.410320 | 0.409815 | 0.000505 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.410320 | 0.409839 | 0.000481 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.410320 | 0.409851 | 0.000468 |
| S3 | joint_target_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.410320 | 0.409880 | 0.000440 |
| S3 | joint_target_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.410320 | 0.409905 | 0.000415 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.410320 | 0.409931 | 0.000389 |
| S3 | joint_target_residual_behavior_neural_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.410320 | 0.409953 | 0.000367 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.410320 | 0.409957 | 0.000363 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.410320 | 0.410020 | 0.000300 |
| S3 | joint_cross_family_residual_behavior_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.410320 | 0.410044 | 0.000276 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.410320 | 0.410044 | 0.000276 |
