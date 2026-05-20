# Conditional latent routing

- Base OOF: `0.480978`
- Routed OOF: `0.480038`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_residual_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.525443 | 0.525167 | 0.000276 | 1 |
| Q1 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.525167 | 0.525112 | 0.000055 | 2 |
| Q2 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.538870 | 0.537359 | 0.001512 | 1 |
| Q2 | joint_neural_context_secondhalf_gate_logreg_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.537359 | 0.536798 | 0.000561 | 2 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.501289 | 0.500706 | 0.000584 | 1 |
| S1 | joint_neighbor_hgb | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.469875 | 0.469537 | 0.000338 | 1 |
| S1 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.469537 | 0.469235 | 0.000302 | 2 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.453129 | 0.451806 | 0.001324 | 1 |
| S3 | joint_panel_neural_multiview_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.411283 | 0.410667 | 0.000616 | 1 |
| S3 | joint_neural_context_bin_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.410667 | 0.410320 | 0.000347 | 2 |
| S4 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.466958 | 0.466425 | 0.000532 | 1 |
| S4 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.466425 | 0.466289 | 0.000137 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.480978 | 0.525443 | 0.538870 | 0.501289 | 0.469875 | 0.453129 | 0.411283 | 0.466958 |
| conditional_latent_routing | 0.480038 | 0.525112 | 0.536798 | 0.500706 | 0.469235 | 0.451806 | 0.410320 | 0.466289 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.538870 | 0.537359 | 0.001512 |
| Q2 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.538870 | 0.537365 | 0.001505 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.453129 | 0.451806 | 0.001324 |
| S2 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.453129 | 0.451806 | 0.001324 |
| Q2 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.538870 | 0.537556 | 0.001314 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.453129 | 0.451878 | 0.001251 |
| S2 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.453129 | 0.451878 | 0.001251 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.453129 | 0.451940 | 0.001189 |
| S2 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.453129 | 0.451940 | 0.001189 |
| Q2 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.538870 | 0.537750 | 0.001120 |
| Q2 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.538870 | 0.537752 | 0.001118 |
| Q2 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.538870 | 0.537772 | 0.001099 |
| S2 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.453129 | 0.452105 | 0.001024 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.453129 | 0.452105 | 0.001024 |
| Q2 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.538870 | 0.537862 | 0.001008 |
| Q2 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.538870 | 0.538028 | 0.000842 |
| Q2 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.538870 | 0.538052 | 0.000818 |
| Q2 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.538870 | 0.538075 | 0.000795 |
| S2 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.453129 | 0.452349 | 0.000780 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.453129 | 0.452349 | 0.000780 |
