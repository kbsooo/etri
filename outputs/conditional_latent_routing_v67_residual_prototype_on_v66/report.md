# Conditional latent routing

- Base OOF: `0.489729`
- Routed OOF: `0.488680`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_panel_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.533569 | 0.533453 | 0.000117 | 1 |
| Q1 | joint_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.533453 | 0.533398 | 0.000055 | 2 |
| Q2 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.543122 | 0.542315 | 0.000807 | 1 |
| Q2 | joint_residual_pls_neighbor_logreg | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.542315 | 0.542175 | 0.000140 | 2 |
| Q3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.509450 | 0.508788 | 0.000661 | 1 |
| S1 | joint_panel_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479082 | 0.478324 | 0.000758 | 1 |
| S1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.478324 | 0.478086 | 0.000238 | 2 |
| S2 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.466655 | 0.463798 | 0.002857 | 1 |
| S2 | joint_cross_family_residual_pls_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.463798 | 0.463496 | 0.000302 | 2 |
| S3 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.419794 | 0.419292 | 0.000502 | 1 |
| S4 | joint_cross_family_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.476432 | 0.475827 | 0.000605 | 1 |
| S4 | joint_pls_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.475827 | 0.475524 | 0.000304 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.489729 | 0.533569 | 0.543122 | 0.509450 | 0.479082 | 0.466655 | 0.419794 | 0.476432 |
| conditional_latent_routing | 0.488680 | 0.533398 | 0.542175 | 0.508788 | 0.478086 | 0.463496 | 0.419292 | 0.475524 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.466655 | 0.463798 | 0.002857 |
| S2 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.466655 | 0.464226 | 0.002429 |
| S2 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.466655 | 0.464825 | 0.001830 |
| S2 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.466655 | 0.465088 | 0.001567 |
| S2 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.466655 | 0.465115 | 0.001540 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.466655 | 0.465307 | 0.001348 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.466655 | 0.465344 | 0.001311 |
| S2 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.466655 | 0.465361 | 0.001294 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.466655 | 0.465511 | 0.001144 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.466655 | 0.465550 | 0.001105 |
| S2 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.466655 | 0.465624 | 0.001031 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.466655 | 0.465775 | 0.000880 |
| Q2 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.543122 | 0.542315 | 0.000807 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.466655 | 0.465850 | 0.000805 |
| S2 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.025000 | 450 | 250 | 0.466655 | 0.465861 | 0.000794 |
| S1 | joint_panel_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479082 | 0.478324 | 0.000758 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479082 | 0.478385 | 0.000697 |
| Q2 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.543122 | 0.542430 | 0.000692 |
| S2 | joint_proto_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.466655 | 0.465975 | 0.000680 |
| Q3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.509450 | 0.508788 | 0.000661 |
