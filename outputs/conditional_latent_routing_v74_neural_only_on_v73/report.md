# Conditional latent routing

- Base OOF: `0.483097`
- Routed OOF: `0.482220`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.526868 | 0.526613 | 0.000255 | 1 |
| Q2 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.539350 | 0.539167 | 0.000183 | 1 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.502451 | 0.501873 | 0.000577 | 1 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.472410 | 0.471086 | 0.001325 | 1 |
| S1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.471086 | 0.470550 | 0.000536 | 2 |
| S2 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.455589 | 0.453825 | 0.001765 | 1 |
| S3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.414280 | 0.413425 | 0.000855 | 1 |
| S3 | joint_proto_neural_multiview_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.413425 | 0.412963 | 0.000463 | 2 |
| S4 | joint_neural_context_gate_hgb_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.470727 | 0.470611 | 0.000116 | 1 |
| S4 | joint_neural_context_bin_gate_logreg_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.470611 | 0.470548 | 0.000063 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.483097 | 0.526868 | 0.539350 | 0.502451 | 0.472410 | 0.455589 | 0.414280 | 0.470727 |
| conditional_latent_routing | 0.482220 | 0.526613 | 0.539167 | 0.501873 | 0.470550 | 0.453825 | 0.412963 | 0.470548 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.455589 | 0.453825 | 0.001765 |
| S2 | joint_neural_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.455589 | 0.453825 | 0.001765 |
| S2 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.455589 | 0.454152 | 0.001437 |
| S2 | joint_neural_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.455589 | 0.454152 | 0.001437 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.472410 | 0.471086 | 0.001325 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.472410 | 0.471222 | 0.001189 |
| S2 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.455589 | 0.454547 | 0.001042 |
| S2 | joint_neural_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.455589 | 0.454547 | 0.001042 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.472410 | 0.471475 | 0.000935 |
| S3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.414280 | 0.413425 | 0.000855 |
| S3 | joint_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.414280 | 0.413573 | 0.000707 |
| S3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.414280 | 0.413590 | 0.000690 |
| S3 | joint_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.414280 | 0.413695 | 0.000585 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.502451 | 0.501873 | 0.000577 |
| S2 | joint_neural_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.455589 | 0.455022 | 0.000567 |
| S2 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.455589 | 0.455022 | 0.000567 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.472410 | 0.471864 | 0.000546 |
| S1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.472410 | 0.471874 | 0.000536 |
| S3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.414280 | 0.413784 | 0.000496 |
| S3 | joint_proto_neural_multiview_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.414280 | 0.413785 | 0.000496 |
