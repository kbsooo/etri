# Conditional latent routing

- Base OOF: `0.481505`
- Routed OOF: `0.480978`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neighbor_hgb | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.525837 | 0.525443 | 0.000395 | 1 |
| Q2 | joint_neural_multiview_qs_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.539061 | 0.538895 | 0.000166 | 1 |
| Q2 | joint_pls_ridge | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.538895 | 0.538870 | 0.000024 | 2 |
| Q3 | joint_panel_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.501390 | 0.501289 | 0.000101 | 1 |
| S1 | joint_neural_context_bin_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.470091 | 0.469930 | 0.000161 | 1 |
| S1 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.469930 | 0.469875 | 0.000056 | 2 |
| S2 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.453197 | 0.453129 | 0.000068 | 1 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.412158 | 0.411303 | 0.000855 | 1 |
| S3 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.411303 | 0.411283 | 0.000020 | 2 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467246 | 0.001556 | 1 |
| S4 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.467246 | 0.466958 | 0.000289 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.481505 | 0.525837 | 0.539061 | 0.501390 | 0.470091 | 0.453197 | 0.412158 | 0.468803 |
| conditional_latent_routing | 0.480978 | 0.525443 | 0.538870 | 0.501289 | 0.469875 | 0.453129 | 0.411283 | 0.466958 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467246 | 0.001556 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467246 | 0.001556 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.467499 | 0.001303 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.467499 | 0.001303 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.467825 | 0.000977 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.467825 | 0.000977 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.412158 | 0.411303 | 0.000855 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467991 | 0.000811 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467991 | 0.000811 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468803 | 0.468023 | 0.000780 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468803 | 0.468023 | 0.000780 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.412158 | 0.411472 | 0.000686 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.468116 | 0.000686 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.468116 | 0.000686 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.468803 | 0.468248 | 0.000554 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.468803 | 0.468248 | 0.000554 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.468293 | 0.000510 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.468293 | 0.000510 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.412158 | 0.411673 | 0.000486 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468803 | 0.468401 | 0.000402 |
