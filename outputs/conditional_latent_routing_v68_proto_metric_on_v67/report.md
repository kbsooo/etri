# Conditional latent routing

- Base OOF: `0.488680`
- Routed OOF: `0.486989`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_target_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.533398 | 0.532315 | 0.001083 | 1 |
| Q1 | joint_residual_contrast_hgb | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.532315 | 0.532067 | 0.000248 | 2 |
| Q2 | joint_target_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.542175 | 0.541660 | 0.000514 | 1 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.541660 | 0.541544 | 0.000117 | 2 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.508788 | 0.507648 | 0.001141 | 1 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.507648 | 0.507506 | 0.000142 | 2 |
| S1 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.478086 | 0.477011 | 0.001075 | 1 |
| S1 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.477011 | 0.476227 | 0.000783 | 2 |
| S2 | joint_target_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.463496 | 0.459388 | 0.004108 | 1 |
| S2 | joint_cross_family_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.459388 | 0.459189 | 0.000199 | 2 |
| S3 | joint_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.419292 | 0.418446 | 0.000845 | 1 |
| S4 | joint_neural_multiview_s_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.475524 | 0.474484 | 0.001040 | 1 |
| S4 | joint_target_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.474484 | 0.473941 | 0.000543 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.488680 | 0.533398 | 0.542175 | 0.508788 | 0.478086 | 0.463496 | 0.419292 | 0.475524 |
| conditional_latent_routing | 0.486989 | 0.532067 | 0.541544 | 0.507506 | 0.476227 | 0.459189 | 0.418446 | 0.473941 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_target_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.463496 | 0.459388 | 0.004108 |
| S2 | joint_target_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.463496 | 0.460030 | 0.003466 |
| S2 | joint_target_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.463496 | 0.460901 | 0.002596 |
| S2 | joint_target_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.463496 | 0.462041 | 0.001456 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.463496 | 0.462222 | 0.001274 |
| S2 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.463496 | 0.462222 | 0.001274 |
| S2 | joint_neural_multiview_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.463496 | 0.462347 | 0.001150 |
| S2 | joint_neural_multiview_q_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.463496 | 0.462347 | 0.001150 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.508788 | 0.507648 | 0.001141 |
| Q1 | joint_target_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.533398 | 0.532315 | 0.001083 |
| S1 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.478086 | 0.477011 | 0.001075 |
| S2 | joint_neural_multiview_q_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.463496 | 0.462424 | 0.001073 |
| S2 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.463496 | 0.462424 | 0.001073 |
| S4 | joint_neural_multiview_s_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.475524 | 0.474484 | 0.001040 |
| S2 | joint_neural_multiview_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.463496 | 0.462499 | 0.000998 |
| S2 | joint_neural_multiview_q_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.463496 | 0.462499 | 0.000998 |
| S4 | joint_neural_multiview_s_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.475524 | 0.474555 | 0.000969 |
| Q1 | joint_target_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.533398 | 0.532446 | 0.000952 |
| S1 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.478086 | 0.477165 | 0.000920 |
| S2 | joint_target_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291 | 57 | 0.463496 | 0.462582 | 0.000914 |
