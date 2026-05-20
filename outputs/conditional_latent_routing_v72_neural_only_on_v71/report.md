# Conditional latent routing

- Base OOF: `0.484026`
- Routed OOF: `0.483815`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159.000000 | 193.000000 | 0.527627 | 0.527420 | 0.000207 | 1 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.540598 | 0.539802 | 0.000795 | 1 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116.000000 | 120.000000 | 0.504044 | 0.503916 | 0.000128 | 1 |
| S1 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291.000000 | 57.000000 | 0.455850 | 0.455799 | 0.000052 | 1 |
| S3 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159.000000 | 193.000000 | 0.415578 | 0.415342 | 0.000236 | 1 |
| S3 | joint_neural_qs_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291.000000 | 57.000000 | 0.415342 | 0.415284 | 0.000058 | 2 |
| S4 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.484026 | 0.527627 | 0.540598 | 0.504044 | 0.472902 | 0.455850 | 0.415578 | 0.471582 |
| conditional_latent_routing | 0.483815 | 0.527420 | 0.539802 | 0.503916 | 0.472902 | 0.455799 | 0.415284 | 0.471582 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.540598 | 0.539802 | 0.000795 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.540598 | 0.539802 | 0.000795 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.540598 | 0.539906 | 0.000692 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.540598 | 0.539906 | 0.000692 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.540598 | 0.539907 | 0.000691 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.540598 | 0.539907 | 0.000691 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.540598 | 0.539978 | 0.000619 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.540598 | 0.539978 | 0.000619 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.540598 | 0.540067 | 0.000531 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.540598 | 0.540067 | 0.000531 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.540598 | 0.540110 | 0.000488 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.540598 | 0.540110 | 0.000488 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.540598 | 0.540293 | 0.000305 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.540598 | 0.540293 | 0.000305 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.540598 | 0.540312 | 0.000285 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.540598 | 0.540312 | 0.000285 |
| S3 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.415578 | 0.415342 | 0.000236 |
| S3 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.415578 | 0.415342 | 0.000236 |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.527627 | 0.527414 | 0.000213 |
| Q1 | joint_neural_multiview_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.527627 | 0.527414 | 0.000213 |
