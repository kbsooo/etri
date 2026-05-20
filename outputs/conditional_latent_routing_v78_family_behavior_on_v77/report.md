# Conditional latent routing

- Base OOF: `0.480038`
- Routed OOF: `0.479449`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_context_secondhalf_gate_logreg_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.525112 | 0.524927 | 0.000185 | 1 |
| Q1 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100.000000 | 130.000000 | 0.524927 | 0.524853 | 0.000073 | 2 |
| Q2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291.000000 | 57.000000 | 0.536798 | 0.535788 | 0.001010 | 1 |
| Q2 | joint_cross_family_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159.000000 | 193.000000 | 0.535788 | 0.535474 | 0.000314 | 2 |
| Q3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S1 | joint_neighbor_hgb | late | 0.666000 | 1.000001 | 0.200000 | 116.000000 | 120.000000 | 0.469235 | 0.468808 | 0.000428 | 1 |
| S1 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.025000 | 100.000000 | 130.000000 | 0.468808 | 0.468781 | 0.000026 | 2 |
| S2 | joint_neural_context_secondhalf_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100.000000 | 130.000000 | 0.451806 | 0.451677 | 0.000128 | 1 |
| S2 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116.000000 | 120.000000 | 0.451677 | 0.451615 | 0.000062 | 2 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.410320 | 0.409433 | 0.000887 | 1 |
| S3 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100.000000 | 130.000000 | 0.409433 | 0.408746 | 0.000687 | 2 |
| S4 | joint_pls_hgb | second_half | 0.500000 | 1.000001 | 0.075000 | 159.000000 | 193.000000 | 0.466289 | 0.466070 | 0.000219 | 1 |
| S4 | joint_cross_family_residual_behavior_neural_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291.000000 | 57.000000 | 0.466070 | 0.465970 | 0.000100 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.480038 | 0.525112 | 0.536798 | 0.500706 | 0.469235 | 0.451806 | 0.410320 | 0.466289 |
| conditional_latent_routing | 0.479449 | 0.524853 | 0.535474 | 0.500706 | 0.468781 | 0.451615 | 0.408746 | 0.465970 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.536798 | 0.535788 | 0.001010 |
| Q2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.536798 | 0.535869 | 0.000929 |
| Q2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.536798 | 0.535885 | 0.000913 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.410320 | 0.409433 | 0.000887 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.410320 | 0.409504 | 0.000816 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.410320 | 0.409510 | 0.000810 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.410320 | 0.409546 | 0.000774 |
| Q2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.536798 | 0.536054 | 0.000744 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.410320 | 0.409587 | 0.000733 |
| Q2 | joint_neural_multiview_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.536798 | 0.536110 | 0.000688 |
| Q2 | joint_neural_multiview_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.536798 | 0.536110 | 0.000688 |
| S3 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.410320 | 0.409633 | 0.000687 |
| S3 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.410320 | 0.409660 | 0.000660 |
| S3 | joint_target_residual_behavior_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.410320 | 0.409665 | 0.000655 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.410320 | 0.409682 | 0.000637 |
| S3 | joint_target_residual_behavior_neural_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.410320 | 0.409719 | 0.000601 |
| S3 | joint_metric_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.410320 | 0.409748 | 0.000572 |
| Q2 | joint_neural_multiview_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.536798 | 0.536228 | 0.000569 |
| Q2 | joint_neural_multiview_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.536798 | 0.536228 | 0.000569 |
| S3 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.410320 | 0.409764 | 0.000556 |
