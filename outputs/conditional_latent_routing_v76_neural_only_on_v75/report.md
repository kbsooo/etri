# Conditional latent routing

- Base OOF: `0.481505`
- Routed OOF: `0.481166`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | joint_neural_multiview_qs_residual_knn_resid | first_half | 0.050000 | 0.000166 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.539061 | 0.538895 |
| Q3 | joint_panel_neural_residual_knn_logitresid | late | 0.050000 | 0.000101 | 1 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.501390 | 0.501289 |
| S1 | joint_neural_context_bin_gate_hgb_logitresid | late | 0.150000 | 0.000161 | 1 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.470091 | 0.469930 |
| S1 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.025000 | 0.000056 | 2 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.469930 | 0.469875 |
| S2 | joint_neural_s_residual_knn_resid | first_half | 0.025000 | 0.000057 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.453197 | 0.453140 |
| S3 | joint_neural_mixture_metric_knn_resid | mid | 0.075000 | 0.000258 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.412158 | 0.411900 |
| S3 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.050000 | 0.000020 | 2 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.411900 | 0.411880 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.200000 | 0.001556 | 1 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.468803 | 0.467246 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.481505 | 0.525837 | 0.539061 | 0.501390 | 0.470091 | 0.453197 | 0.412158 | 0.468803 |
| conditional_latent_routing | 0.481166 | 0.525837 | 0.538895 | 0.501289 | 0.469875 | 0.453140 | 0.411880 | 0.467246 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467246 | 0.001556 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467246 | 0.001556 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.467499 | 0.001303 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.467499 | 0.001303 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.467825 | 0.000977 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.467825 | 0.000977 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467991 | 0.000811 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.468803 | 0.467991 | 0.000811 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468803 | 0.468023 | 0.000780 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468803 | 0.468023 | 0.000780 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.468116 | 0.000686 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.468803 | 0.468116 | 0.000686 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.468803 | 0.468248 | 0.000554 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.468803 | 0.468248 | 0.000554 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.468293 | 0.000510 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.468803 | 0.468293 | 0.000510 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468803 | 0.468401 | 0.000402 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.468803 | 0.468401 | 0.000402 |
| S4 | joint_neural_q_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.468803 | 0.468506 | 0.000296 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.468803 | 0.468506 | 0.000296 |
