# Conditional latent routing

- Base OOF: `0.492249`
- Routed OOF: `0.490915`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.536881 | 0.534989 | 0.001892 | 1 |
| Q1 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.534989 | 0.534360 | 0.000629 | 2 |
| Q2 | joint_neural_multiview_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.544093 | 0.543605 | 0.000489 | 1 |
| Q2 | joint_cross_family_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.543605 | 0.543546 | 0.000059 | 2 |
| Q3 | joint_qs_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.511662 | 0.511237 | 0.000426 | 1 |
| S1 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.481773 | 0.481049 | 0.000724 | 1 |
| S1 | joint_metric_neighbor_hgb | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.481049 | 0.480399 | 0.000649 | 2 |
| S2 | joint_target_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.469928 | 0.468642 | 0.001286 | 1 |
| S2 | joint_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.468642 | 0.468049 | 0.000593 | 2 |
| S3 | joint_neural_multiview_qs_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.422249 | 0.421551 | 0.000697 | 1 |
| S3 | joint_target_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.421551 | 0.421222 | 0.000329 | 2 |
| S4 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479160 | 0.478289 | 0.000872 | 1 |
| S4 | joint_neural_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.478289 | 0.477591 | 0.000698 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.492249 | 0.536881 | 0.544093 | 0.511662 | 0.481773 | 0.469928 | 0.422249 | 0.479160 |
| conditional_latent_routing | 0.490915 | 0.534360 | 0.543546 | 0.511237 | 0.480399 | 0.468049 | 0.421222 | 0.477591 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_multiview_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.536881 | 0.534989 | 0.001892 |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.536881 | 0.534989 | 0.001892 |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.536881 | 0.535241 | 0.001640 |
| Q1 | joint_neural_multiview_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.536881 | 0.535241 | 0.001640 |
| S2 | joint_target_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.469928 | 0.468642 | 0.001286 |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.536881 | 0.535625 | 0.001255 |
| Q1 | joint_neural_multiview_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.536881 | 0.535625 | 0.001255 |
| Q1 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.536881 | 0.535834 | 0.001047 |
| Q1 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.536881 | 0.535834 | 0.001047 |
| S2 | joint_target_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.469928 | 0.468919 | 0.001009 |
| S2 | joint_target_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.469928 | 0.468927 | 0.001001 |
| Q1 | joint_neural_multiview_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.536881 | 0.535898 | 0.000983 |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.536881 | 0.535898 | 0.000983 |
| Q1 | joint_neural_multiview_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.536881 | 0.535974 | 0.000907 |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.536881 | 0.535974 | 0.000907 |
| Q1 | joint_neural_multiview_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.536881 | 0.536004 | 0.000877 |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.536881 | 0.536004 | 0.000877 |
| S4 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479160 | 0.478289 | 0.000872 |
| S2 | joint_target_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.469928 | 0.469103 | 0.000825 |
| Q1 | joint_neural_s_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.536881 | 0.536066 | 0.000815 |
