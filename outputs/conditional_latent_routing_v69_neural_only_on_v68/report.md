# Conditional latent routing

- Base OOF: `0.486989`
- Routed OOF: `0.486228`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.532067 | 0.530912 | 0.001154 | 1 |
| Q1 | joint_proto_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.530912 | 0.530709 | 0.000203 | 2 |
| Q2 | joint_neural_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.541544 | 0.541484 | 0.000059 | 1 |
| Q3 | joint_proto_neural_multiview_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.507506 | 0.506621 | 0.000885 | 1 |
| S1 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.476227 | 0.476024 | 0.000204 | 1 |
| S2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.459189 | 0.458802 | 0.000387 | 1 |
| S2 | joint_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.458802 | 0.458489 | 0.000313 | 2 |
| S3 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.418446 | 0.417949 | 0.000498 | 1 |
| S3 | joint_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291 | 57 | 0.417949 | 0.417891 | 0.000057 | 2 |
| S4 | joint_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.473941 | 0.472778 | 0.001163 | 1 |
| S4 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.472778 | 0.472379 | 0.000399 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.486989 | 0.532067 | 0.541544 | 0.507506 | 0.476227 | 0.459189 | 0.418446 | 0.473941 |
| conditional_latent_routing | 0.486228 | 0.530709 | 0.541484 | 0.506621 | 0.476024 | 0.458489 | 0.417891 | 0.472379 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | joint_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.473941 | 0.472778 | 0.001163 |
| Q1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.532067 | 0.530912 | 0.001154 |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.532067 | 0.530912 | 0.001154 |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.532067 | 0.531087 | 0.000980 |
| Q1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.532067 | 0.531087 | 0.000980 |
| S4 | joint_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.473941 | 0.473035 | 0.000906 |
| Q3 | joint_proto_neural_multiview_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.507506 | 0.506621 | 0.000885 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.473941 | 0.473061 | 0.000880 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.473941 | 0.473061 | 0.000880 |
| S4 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.473941 | 0.473110 | 0.000831 |
| Q3 | joint_proto_neural_multiview_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.507506 | 0.506725 | 0.000781 |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.532067 | 0.531331 | 0.000736 |
| Q1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.532067 | 0.531331 | 0.000736 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.473941 | 0.473253 | 0.000688 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.473941 | 0.473253 | 0.000688 |
| S4 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.473941 | 0.473278 | 0.000663 |
| S4 | joint_neural_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.473941 | 0.473314 | 0.000627 |
| Q3 | joint_proto_neural_multiview_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.507506 | 0.506901 | 0.000605 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.507506 | 0.506926 | 0.000580 |
| S4 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.473941 | 0.473371 | 0.000570 |
