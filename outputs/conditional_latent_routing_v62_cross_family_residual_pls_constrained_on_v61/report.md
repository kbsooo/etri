# Conditional latent routing

- Base OOF: `0.496127`
- Routed OOF: `0.495269`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291.000000 | 57.000000 | 0.540771 | 0.538766 | 0.002005 |
| Q2 | joint_cross_family_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291.000000 | 57.000000 | 0.547326 | 0.546331 | 0.000996 |
| Q3 | joint_cross_family_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450.000000 | 250.000000 | 0.515709 | 0.514353 | 0.001356 |
| S1 | joint_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291.000000 | 57.000000 | 0.487250 | 0.486470 | 0.000781 |
| S2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 |
| S3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 |
| S4 | joint_cross_family_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.483982 | 0.483112 | 0.000870 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.496127 | 0.540771 | 0.547326 | 0.515709 | 0.487250 | 0.472948 | 0.424903 | 0.483982 |
| conditional_latent_routing | 0.495269 | 0.538766 | 0.546331 | 0.514353 | 0.486470 | 0.472948 | 0.424903 | 0.483112 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.540771 | 0.538766 | 0.002005 |
| Q1 | joint_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.540771 | 0.539065 | 0.001707 |
| Q1 | joint_target_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.540771 | 0.539133 | 0.001638 |
| Q1 | joint_target_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.540771 | 0.539324 | 0.001447 |
| Q3 | joint_cross_family_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.515709 | 0.514353 | 0.001356 |
| Q3 | joint_s_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.515709 | 0.514353 | 0.001356 |
| Q1 | joint_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.540771 | 0.539486 | 0.001285 |
| Q3 | joint_s_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.515709 | 0.514457 | 0.001251 |
| Q3 | joint_cross_family_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.515709 | 0.514457 | 0.001251 |
| Q3 | joint_s_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.515709 | 0.514474 | 0.001234 |
| Q3 | joint_cross_family_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.515709 | 0.514474 | 0.001234 |
| Q1 | joint_target_qs_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.540771 | 0.539648 | 0.001124 |
| Q3 | joint_cross_family_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.515709 | 0.514631 | 0.001078 |
| Q3 | joint_s_residual_pls_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.515709 | 0.514631 | 0.001078 |
| Q3 | joint_cross_family_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.515709 | 0.514666 | 0.001043 |
| Q3 | joint_s_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.515709 | 0.514666 | 0.001043 |
| Q2 | joint_cross_family_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.547326 | 0.546331 | 0.000996 |
| Q2 | joint_s_residual_pls_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.547326 | 0.546331 | 0.000996 |
| Q3 | joint_s_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.515709 | 0.514727 | 0.000982 |
| Q3 | joint_cross_family_residual_pls_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.515709 | 0.514727 | 0.000982 |
