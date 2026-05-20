# Conditional latent routing

- Base OOF: `0.486152`
- Routed OOF: `0.485308`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.530515 | 0.530401 | 0.000114 | 1 |
| Q2 | joint_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.541332 | 0.541213 | 0.000118 | 1 |
| Q3 | joint_panel_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.506621 | 0.504957 | 0.001664 | 1 |
| Q3 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.504957 | 0.504545 | 0.000412 | 2 |
| S1 | joint_neural_multiview_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.475868 | 0.475230 | 0.000638 | 1 |
| S1 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.475230 | 0.475179 | 0.000050 | 2 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.458462 | 0.457076 | 0.001386 | 1 |
| S3 | joint_neural_qs_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.417891 | 0.417184 | 0.000707 | 1 |
| S3 | joint_neural_multiview_qs_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.417184 | 0.416664 | 0.000520 | 2 |
| S4 | joint_target_neural_multiview_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.472379 | 0.472145 | 0.000235 | 1 |
| S4 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.472145 | 0.472075 | 0.000070 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.486152 | 0.530515 | 0.541332 | 0.506621 | 0.475868 | 0.458462 | 0.417891 | 0.472379 |
| conditional_latent_routing | 0.485308 | 0.530401 | 0.541213 | 0.504545 | 0.475179 | 0.457076 | 0.416664 | 0.472075 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | joint_panel_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.506621 | 0.504957 | 0.001664 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.458462 | 0.457076 | 0.001386 |
| Q3 | joint_panel_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.506621 | 0.505325 | 0.001296 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.506621 | 0.505420 | 0.001201 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.458462 | 0.457265 | 0.001197 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.458462 | 0.457307 | 0.001155 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.458462 | 0.457403 | 0.001059 |
| Q3 | joint_panel_neural_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.506621 | 0.505688 | 0.000933 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.506621 | 0.505694 | 0.000927 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.458462 | 0.457549 | 0.000913 |
| Q3 | joint_panel_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.506621 | 0.505725 | 0.000896 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.458462 | 0.457615 | 0.000847 |
| Q3 | joint_panel_neural_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.506621 | 0.505846 | 0.000775 |
| S3 | joint_neural_qs_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.417891 | 0.417184 | 0.000707 |
| S1 | joint_neural_multiview_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.475868 | 0.475230 | 0.000638 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.506621 | 0.505985 | 0.000636 |
| S3 | joint_neural_qs_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.417891 | 0.417315 | 0.000577 |
| S1 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.475868 | 0.475295 | 0.000573 |
| S1 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.475868 | 0.475295 | 0.000573 |
| S1 | joint_neural_multiview_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.475868 | 0.475295 | 0.000572 |
