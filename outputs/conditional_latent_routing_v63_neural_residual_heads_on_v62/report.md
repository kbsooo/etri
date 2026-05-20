# Conditional latent routing

- Base OOF: `0.495010`
- Routed OOF: `0.493630`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_target_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.538766 | 0.537826 | 0.000940 | 1 |
| Q1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.537826 | 0.537081 | 0.000745 | 2 |
| Q2 | joint_cross_family_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.545849 | 0.544730 | 0.001119 | 1 |
| Q3 | joint_neural_cross_family_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.514353 | 0.512852 | 0.001501 | 1 |
| S1 | joint_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.486117 | 0.483382 | 0.002735 | 1 |
| S2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.472604 | 0.471962 | 0.000642 | 1 |
| S2 | joint_cross_family_residual_pls_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.471962 | 0.471486 | 0.000476 | 2 |
| S3 | joint_cross_family_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.424623 | 0.424226 | 0.000396 | 1 |
| S3 | joint_neural_cross_family_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.424226 | 0.424022 | 0.000205 | 2 |
| S4 | joint_local_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.482758 | 0.482151 | 0.000607 | 1 |
| S4 | joint_cross_family_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.482151 | 0.481857 | 0.000294 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.495010 | 0.538766 | 0.545849 | 0.514353 | 0.486117 | 0.472604 | 0.424623 | 0.482758 |
| conditional_latent_routing | 0.493630 | 0.537081 | 0.544730 | 0.512852 | 0.483382 | 0.471486 | 0.424022 | 0.481857 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | joint_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.486117 | 0.483382 | 0.002735 |
| S1 | joint_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.486117 | 0.483787 | 0.002330 |
| S1 | joint_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.486117 | 0.484070 | 0.002047 |
| S1 | joint_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.486117 | 0.484343 | 0.001774 |
| S1 | joint_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.486117 | 0.484360 | 0.001757 |
| S1 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.486117 | 0.484594 | 0.001523 |
| S1 | joint_neural_residual_knn_logitresid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.486117 | 0.484608 | 0.001509 |
| Q3 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.514353 | 0.512852 | 0.001501 |
| Q3 | joint_neural_cross_family_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.514353 | 0.512852 | 0.001501 |
| S1 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.486117 | 0.484733 | 0.001384 |
| S1 | joint_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.486117 | 0.484759 | 0.001358 |
| S1 | joint_neural_residual_knn_logitresid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.486117 | 0.484765 | 0.001352 |
| S1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.486117 | 0.484777 | 0.001340 |
| Q3 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.514353 | 0.513073 | 0.001280 |
| Q3 | joint_neural_cross_family_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.514353 | 0.513073 | 0.001280 |
| S1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.486117 | 0.484950 | 0.001167 |
| Q2 | joint_s_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.545849 | 0.544730 | 0.001119 |
| Q2 | joint_cross_family_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.545849 | 0.544730 | 0.001119 |
| S1 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.486117 | 0.485017 | 0.001100 |
| Q2 | joint_cross_family_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.545849 | 0.544798 | 0.001051 |
