# Conditional latent routing

- Base OOF: `0.492249`
- Routed OOF: `0.491846`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_target_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116.000000 | 120.000000 | 0.536881 | 0.536438 | 0.000443 | 1 |
| Q2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| Q3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S1 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S2 | joint_target_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.469928 | 0.468642 | 0.001286 | 1 |
| S3 | joint_target_neural_multiview_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450.000000 | 250.000000 | 0.422249 | 0.421548 | 0.000700 | 1 |
| S4 | joint_target_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116.000000 | 120.000000 | 0.479160 | 0.478901 | 0.000259 | 1 |
| S4 | joint_target_neural_multiview_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100.000000 | 130.000000 | 0.478901 | 0.478766 | 0.000135 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.492249 | 0.536881 | 0.544093 | 0.511662 | 0.481773 | 0.469928 | 0.422249 | 0.479160 |
| conditional_latent_routing | 0.491846 | 0.536438 | 0.544093 | 0.511662 | 0.481773 | 0.468642 | 0.421548 | 0.478766 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_target_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.469928 | 0.468642 | 0.001286 |
| S2 | joint_target_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.469928 | 0.468919 | 0.001009 |
| S2 | joint_target_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.469928 | 0.468927 | 0.001001 |
| S2 | joint_target_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.469928 | 0.469103 | 0.000825 |
| S3 | joint_target_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.422249 | 0.421540 | 0.000709 |
| S2 | joint_target_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.469928 | 0.469224 | 0.000704 |
| S3 | joint_target_neural_multiview_residual_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.422249 | 0.421548 | 0.000700 |
| S3 | joint_target_neural_multiview_residual_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.422249 | 0.421597 | 0.000651 |
| S3 | joint_target_neural_multiview_residual_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.422249 | 0.421625 | 0.000623 |
| S3 | joint_target_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.422249 | 0.421642 | 0.000607 |
| S2 | joint_target_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.469928 | 0.469329 | 0.000599 |
| S2 | joint_target_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.469928 | 0.469367 | 0.000561 |
| S2 | joint_target_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.469928 | 0.469449 | 0.000480 |
| Q1 | joint_target_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.536881 | 0.536421 | 0.000460 |
| S3 | joint_target_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.422249 | 0.421790 | 0.000459 |
| Q1 | joint_target_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.536881 | 0.536438 | 0.000443 |
| S3 | joint_target_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.422249 | 0.421813 | 0.000436 |
| Q1 | joint_target_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.536881 | 0.536454 | 0.000427 |
| Q1 | joint_target_neural_multiview_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.536881 | 0.536469 | 0.000412 |
| S3 | joint_target_neural_multiview_residual_knn_resid | all | 0.000000 | 1.000001 | 0.025000 | 450 | 250 | 0.422249 | 0.421850 | 0.000398 |
