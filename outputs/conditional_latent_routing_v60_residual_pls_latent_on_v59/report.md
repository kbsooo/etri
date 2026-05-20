# Conditional latent routing

- Base OOF: `0.497895`
- Routed OOF: `0.497145`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.542996 | 0.541876 | 0.001121 | 1 |
| Q2 | joint_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.549511 | 0.547846 | 0.001665 | 1 |
| Q3 | joint_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.517240 | 0.516415 | 0.000824 | 1 |
| Q3 | joint_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.516415 | 0.516314 | 0.000101 | 2 |
| S1 | joint_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.488003 | 0.487750 | 0.000252 | 1 |
| S1 | joint_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291 | 57 | 0.487750 | 0.487638 | 0.000112 | 2 |
| S2 | joint_local_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.474612 | 0.474404 | 0.000208 | 1 |
| S3 | joint_metric_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427209 | 0.426885 | 0.000324 | 1 |
| S3 | joint_metric_neighbor_logreg | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.426885 | 0.426779 | 0.000106 | 2 |
| S4 | joint_local_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.485694 | 0.485269 | 0.000425 | 1 |
| S4 | joint_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.485269 | 0.485159 | 0.000110 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.497895 | 0.542996 | 0.549511 | 0.517240 | 0.488003 | 0.474612 | 0.427209 | 0.485694 |
| conditional_latent_routing | 0.497145 | 0.541876 | 0.547846 | 0.516314 | 0.487638 | 0.474404 | 0.426779 | 0.485159 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | joint_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.549511 | 0.547846 | 0.001665 |
| Q2 | joint_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.549511 | 0.547995 | 0.001517 |
| Q2 | joint_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.549511 | 0.548308 | 0.001204 |
| Q1 | joint_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.542996 | 0.541876 | 0.001121 |
| Q2 | joint_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.549511 | 0.548409 | 0.001103 |
| Q2 | joint_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.549511 | 0.548555 | 0.000956 |
| Q1 | joint_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.542996 | 0.542042 | 0.000955 |
| Q3 | joint_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.517240 | 0.516415 | 0.000824 |
| Q2 | joint_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.549511 | 0.548766 | 0.000745 |
| Q2 | joint_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.549511 | 0.548780 | 0.000732 |
| Q1 | joint_residual_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.542996 | 0.542275 | 0.000721 |
| Q3 | joint_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.517240 | 0.516522 | 0.000718 |
| Q2 | joint_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.025000 | 450 | 250 | 0.549511 | 0.548806 | 0.000705 |
| Q2 | joint_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.549511 | 0.548898 | 0.000613 |
| Q2 | joint_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.549511 | 0.548911 | 0.000600 |
| Q3 | joint_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.517240 | 0.516640 | 0.000600 |
| Q3 | joint_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.517240 | 0.516664 | 0.000576 |
| Q2 | joint_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.549511 | 0.548949 | 0.000563 |
| Q2 | joint_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.549511 | 0.548951 | 0.000561 |
| Q3 | joint_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.517240 | 0.516688 | 0.000551 |
