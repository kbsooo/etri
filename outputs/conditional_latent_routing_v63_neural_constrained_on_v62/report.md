# Conditional latent routing

- Base OOF: `0.495010`
- Routed OOF: `0.494207`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.538766 | 0.538022 | 0.000745 |
| Q2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 |
| Q3 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450.000000 | 250.000000 | 0.514353 | 0.512852 | 0.001501 |
| S1 | joint_neural_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450.000000 | 250.000000 | 0.486117 | 0.483382 | 0.002735 |
| S2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.472604 | 0.471962 | 0.000642 |
| S3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 |
| S4 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.495010 | 0.538766 | 0.545849 | 0.514353 | 0.486117 | 0.472604 | 0.424623 | 0.482758 |
| conditional_latent_routing | 0.494207 | 0.538022 | 0.545849 | 0.512852 | 0.483382 | 0.471962 | 0.424623 | 0.482758 |

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
| Q3 | joint_neural_cross_family_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.514353 | 0.513073 | 0.001280 |
| Q3 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.514353 | 0.513073 | 0.001280 |
| S1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.486117 | 0.484950 | 0.001167 |
| S1 | joint_neural_s_residual_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.486117 | 0.485017 | 0.001100 |
| S1 | joint_neural_residual_knn_logitresid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.486117 | 0.485068 | 0.001050 |
| Q3 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.514353 | 0.513338 | 0.001015 |
| Q3 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.514353 | 0.513338 | 0.001015 |
