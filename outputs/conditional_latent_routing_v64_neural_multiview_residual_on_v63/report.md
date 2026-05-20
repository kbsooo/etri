# Conditional latent routing

- Base OOF: `0.493630`
- Routed OOF: `0.492249`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.537081 | 0.536881 | 0.000200 | 1 |
| Q2 | joint_neural_multiview_qs_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.544730 | 0.544365 | 0.000365 | 1 |
| Q2 | joint_neural_multiview_cross_family_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.544365 | 0.544093 | 0.000271 | 2 |
| Q3 | joint_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.512852 | 0.511662 | 0.001189 | 1 |
| S1 | joint_neural_qs_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.483382 | 0.482465 | 0.000917 | 1 |
| S1 | joint_neural_multiview_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.482465 | 0.481773 | 0.000692 | 2 |
| S2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.471486 | 0.470152 | 0.001334 | 1 |
| S2 | joint_metric_neighbor_hgb | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.470152 | 0.469928 | 0.000224 | 2 |
| S3 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.424022 | 0.422974 | 0.001048 | 1 |
| S3 | joint_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.422974 | 0.422249 | 0.000725 | 2 |
| S4 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.481857 | 0.479954 | 0.001903 | 1 |
| S4 | joint_neural_multiview_s_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.479954 | 0.479160 | 0.000793 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.493630 | 0.537081 | 0.544730 | 0.512852 | 0.483382 | 0.471486 | 0.424022 | 0.481857 |
| conditional_latent_routing | 0.492249 | 0.536881 | 0.544093 | 0.511662 | 0.481773 | 0.469928 | 0.422249 | 0.479160 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.481857 | 0.479954 | 0.001903 |
| S4 | joint_neural_qs_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.481857 | 0.480216 | 0.001641 |
| S4 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.481857 | 0.480280 | 0.001577 |
| S2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.471486 | 0.470152 | 0.001334 |
| S4 | joint_neural_qs_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.481857 | 0.480532 | 0.001325 |
| S2 | joint_neural_q_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.471486 | 0.470246 | 0.001241 |
| S2 | joint_neural_cross_family_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.471486 | 0.470246 | 0.001241 |
| S4 | joint_neural_q_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.481857 | 0.480635 | 0.001222 |
| S4 | joint_neural_cross_family_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.481857 | 0.480635 | 0.001222 |
| S2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.471486 | 0.470287 | 0.001199 |
| Q3 | joint_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.512852 | 0.511662 | 0.001189 |
| S4 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.481857 | 0.480673 | 0.001184 |
| S4 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.481857 | 0.480695 | 0.001161 |
| S4 | joint_neural_qs_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.481857 | 0.480718 | 0.001139 |
| S4 | joint_neural_multiview_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.481857 | 0.480779 | 0.001078 |
| Q3 | joint_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.512852 | 0.511774 | 0.001078 |
| S2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.471486 | 0.470412 | 0.001074 |
| S4 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.481857 | 0.480807 | 0.001050 |
| S3 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.424022 | 0.422974 | 0.001048 |
| S4 | joint_neural_multiview_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.481857 | 0.480836 | 0.001021 |
