# Conditional latent routing

- Base OOF: `0.483657`
- Routed OOF: `0.483267`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291.000000 | 57.000000 | 0.527420 | 0.527365 | 0.000055 | 1 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.539802 | 0.539350 | 0.000452 | 1 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100.000000 | 130.000000 | 0.503916 | 0.502953 | 0.000962 | 1 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.502953 | 0.502451 | 0.000503 | 2 |
| S1 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.472622 | 0.472387 | 0.000236 | 1 |
| S2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S3 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100.000000 | 130.000000 | 0.414965 | 0.414676 | 0.000289 | 1 |
| S3 | joint_proto_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116.000000 | 120.000000 | 0.414676 | 0.414442 | 0.000234 | 2 |
| S4 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.483657 | 0.527420 | 0.539802 | 0.503916 | 0.472622 | 0.455641 | 0.414965 | 0.471233 |
| conditional_latent_routing | 0.483267 | 0.527365 | 0.539350 | 0.502451 | 0.472387 | 0.455641 | 0.414442 | 0.471233 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | joint_neural_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.502953 | 0.000962 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.502953 | 0.000962 |
| Q3 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.503026 | 0.000890 |
| Q3 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.503916 | 0.503026 | 0.000890 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503144 | 0.000772 |
| Q3 | joint_neural_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503144 | 0.000772 |
| Q3 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503218 | 0.000698 |
| Q3 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.503916 | 0.503218 | 0.000698 |
| Q3 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503364 | 0.000551 |
| Q3 | joint_neural_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503364 | 0.000551 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.503916 | 0.503413 | 0.000503 |
| Q3 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503431 | 0.000485 |
| Q3 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.503916 | 0.503431 | 0.000485 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.539802 | 0.539350 | 0.000452 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.539802 | 0.539350 | 0.000452 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.503916 | 0.503509 | 0.000407 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.539802 | 0.539413 | 0.000390 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.539802 | 0.539413 | 0.000390 |
| S3 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.414965 | 0.414630 | 0.000336 |
| S3 | joint_proto_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.414965 | 0.414655 | 0.000310 |
