# Conditional latent routing

- Base OOF: `0.483657`
- Routed OOF: `0.483097`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_cross_family_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.527420 | 0.526923 | 0.000497 | 1 |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.526923 | 0.526868 | 0.000055 | 2 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.539802 | 0.539350 | 0.000452 | 1 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.502953 | 0.000962 | 1 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.502953 | 0.502451 | 0.000503 | 2 |
| S1 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.472622 | 0.472410 | 0.000212 | 1 |
| S2 | joint_cross_family_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.455641 | 0.455589 | 0.000052 | 1 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.414965 | 0.414514 | 0.000451 | 1 |
| S3 | joint_proto_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.414514 | 0.414280 | 0.000234 | 2 |
| S4 | joint_target_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.471233 | 0.470727 | 0.000506 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.483657 | 0.527420 | 0.539802 | 0.503916 | 0.472622 | 0.455641 | 0.414965 | 0.471233 |
| conditional_latent_routing | 0.483097 | 0.526868 | 0.539350 | 0.502451 | 0.472410 | 0.455589 | 0.414280 | 0.470727 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.502953 | 0.000962 |
| Q3 | joint_neural_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.502953 | 0.000962 |
| Q3 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.503026 | 0.000890 |
| Q3 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.503026 | 0.000890 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503144 | 0.000772 |
| Q3 | joint_neural_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503144 | 0.000772 |
| Q3 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503218 | 0.000698 |
| Q3 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503218 | 0.000698 |
| Q3 | joint_neural_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503364 | 0.000551 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503364 | 0.000551 |
| S4 | joint_target_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.471233 | 0.470715 | 0.000519 |
| S4 | joint_target_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.471233 | 0.470727 | 0.000506 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.503916 | 0.503413 | 0.000503 |
| Q1 | joint_s_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.527420 | 0.526923 | 0.000497 |
| Q1 | joint_cross_family_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.527420 | 0.526923 | 0.000497 |
| Q3 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503431 | 0.000485 |
| Q3 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503431 | 0.000485 |
| S3 | joint_residual_metric_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.414965 | 0.414511 | 0.000455 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.539802 | 0.539350 | 0.000452 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.539802 | 0.539350 | 0.000452 |
