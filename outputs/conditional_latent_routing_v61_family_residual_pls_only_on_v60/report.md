# Conditional latent routing

- Base OOF: `0.497145`
- Routed OOF: `0.496175`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_residual_pls_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.541876 | 0.540771 | 0.001105 | 1 |
| Q2 | joint_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.547846 | 0.547601 | 0.000246 | 1 |
| Q2 | joint_residual_pls_neighbor_logreg | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.547601 | 0.547326 | 0.000275 | 2 |
| Q3 | joint_s_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.516314 | 0.515762 | 0.000552 | 1 |
| Q3 | joint_s_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.515762 | 0.515709 | 0.000054 | 2 |
| S1 | joint_q_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.487638 | 0.487250 | 0.000388 | 1 |
| S2 | joint_q_residual_pls_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.474404 | 0.473283 | 0.001120 | 1 |
| S3 | joint_q_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.426779 | 0.424903 | 0.001875 | 1 |
| S4 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.485159 | 0.483982 | 0.001178 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.497145 | 0.541876 | 0.547846 | 0.516314 | 0.487638 | 0.474404 | 0.426779 | 0.485159 |
| conditional_latent_routing | 0.496175 | 0.540771 | 0.547326 | 0.515709 | 0.487250 | 0.473283 | 0.424903 | 0.483982 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_q_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.426779 | 0.424903 | 0.001875 |
| S3 | joint_q_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.426779 | 0.425098 | 0.001681 |
| S3 | joint_q_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.426779 | 0.425173 | 0.001606 |
| S3 | joint_q_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.426779 | 0.425349 | 0.001429 |
| S3 | joint_q_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.426779 | 0.425560 | 0.001218 |
| S4 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.485159 | 0.483982 | 0.001178 |
| S4 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.485159 | 0.484037 | 0.001122 |
| S2 | joint_q_residual_pls_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.474404 | 0.473283 | 0.001120 |
| S3 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.426779 | 0.425673 | 0.001106 |
| Q1 | joint_residual_pls_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.541876 | 0.540771 | 0.001105 |
| S3 | joint_q_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.426779 | 0.425700 | 0.001078 |
| Q1 | joint_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.541876 | 0.540856 | 0.001020 |
| S3 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.426779 | 0.425776 | 0.001003 |
| Q1 | joint_residual_pls_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.541876 | 0.540873 | 0.001002 |
| S4 | joint_target_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.485159 | 0.484198 | 0.000961 |
| S2 | joint_q_residual_pls_knn_logitresid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.474404 | 0.473451 | 0.000952 |
| Q1 | joint_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.541876 | 0.540935 | 0.000941 |
| S2 | joint_q_residual_pls_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.474404 | 0.473503 | 0.000900 |
| S2 | joint_q_residual_pls_knn_logitresid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.474404 | 0.473549 | 0.000855 |
| S3 | joint_target_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.426779 | 0.425982 | 0.000796 |
