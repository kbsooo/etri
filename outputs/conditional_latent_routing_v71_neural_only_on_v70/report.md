# Conditional latent routing

- Base OOF: `0.485258`
- Routed OOF: `0.484048`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_target_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.530257 | 0.528363 | 0.001894 | 1 |
| Q1 | joint_neural_q_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.528363 | 0.527627 | 0.000736 | 2 |
| Q2 | joint_neural_multiview_qs_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.541065 | 0.540665 | 0.000400 | 1 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.504545 | 0.504044 | 0.000501 | 1 |
| S1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.475179 | 0.473807 | 0.001372 | 1 |
| S1 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.473807 | 0.472902 | 0.000905 | 2 |
| S2 | joint_neural_multiview_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.457025 | 0.455978 | 0.001047 | 1 |
| S2 | joint_proto_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.455978 | 0.455850 | 0.000128 | 2 |
| S3 | joint_proto_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.416664 | 0.416033 | 0.000632 | 1 |
| S3 | joint_proto_neural_multiview_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.416033 | 0.415560 | 0.000473 | 2 |
| S4 | joint_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.472072 | 0.471689 | 0.000383 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.485258 | 0.530257 | 0.541065 | 0.504545 | 0.475179 | 0.457025 | 0.416664 | 0.472072 |
| conditional_latent_routing | 0.484048 | 0.527627 | 0.540665 | 0.504044 | 0.472902 | 0.455850 | 0.415560 | 0.471689 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_target_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.530257 | 0.528363 | 0.001894 |
| Q1 | joint_target_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.530257 | 0.528490 | 0.001767 |
| Q1 | joint_target_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.530257 | 0.528848 | 0.001409 |
| S1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.475179 | 0.473807 | 0.001372 |
| S1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.475179 | 0.474076 | 0.001103 |
| S2 | joint_proto_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.457025 | 0.455943 | 0.001081 |
| S2 | joint_neural_multiview_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.457025 | 0.455978 | 0.001047 |
| S2 | joint_neural_multiview_q_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.457025 | 0.455978 | 0.001047 |
| S2 | joint_proto_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.457025 | 0.456103 | 0.000922 |
| S1 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.475179 | 0.474274 | 0.000905 |
| S2 | joint_neural_multiview_q_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.457025 | 0.456135 | 0.000890 |
| S2 | joint_neural_multiview_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.457025 | 0.456135 | 0.000890 |
| S1 | joint_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.475179 | 0.474342 | 0.000837 |
| Q1 | joint_target_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.530257 | 0.529436 | 0.000820 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.457025 | 0.456228 | 0.000796 |
| S1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.475179 | 0.474389 | 0.000790 |
| S1 | joint_neural_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.475179 | 0.474390 | 0.000789 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.457025 | 0.456265 | 0.000759 |
| S1 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.475179 | 0.474432 | 0.000747 |
| Q1 | joint_neural_q_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.530257 | 0.529521 | 0.000736 |
