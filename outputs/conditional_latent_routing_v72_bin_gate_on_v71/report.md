# Conditional latent routing

- Base OOF: `0.484026`
- Routed OOF: `0.483657`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_multiview_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.527627 | 0.527420 | 0.000207 | 1 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.540598 | 0.539802 | 0.000795 | 1 |
| Q3 | joint_panel_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.504044 | 0.503916 | 0.000128 | 1 |
| S1 | joint_cross_family_residual_pls_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.472902 | 0.472622 | 0.000280 | 1 |
| S2 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.455850 | 0.455641 | 0.000209 | 1 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.415578 | 0.415035 | 0.000543 | 1 |
| S3 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.415035 | 0.414965 | 0.000069 | 2 |
| S4 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.471582 | 0.471363 | 0.000219 | 1 |
| S4 | joint_cross_family_residual_pls_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.471363 | 0.471233 | 0.000129 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.484026 | 0.527627 | 0.540598 | 0.504044 | 0.472902 | 0.455850 | 0.415578 | 0.471582 |
| conditional_latent_routing | 0.483657 | 0.527420 | 0.539802 | 0.503916 | 0.472622 | 0.455641 | 0.414965 | 0.471233 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.540598 | 0.539802 | 0.000795 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.540598 | 0.539802 | 0.000795 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.540598 | 0.539906 | 0.000692 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.540598 | 0.539906 | 0.000692 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.540598 | 0.539907 | 0.000691 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.540598 | 0.539907 | 0.000691 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.540598 | 0.539978 | 0.000619 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.540598 | 0.539978 | 0.000619 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.415578 | 0.415035 | 0.000543 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.540598 | 0.540067 | 0.000531 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.540598 | 0.540067 | 0.000531 |
| S3 | joint_residual_metric_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.415578 | 0.415072 | 0.000505 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.540598 | 0.540110 | 0.000488 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.540598 | 0.540110 | 0.000488 |
| S3 | joint_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.415578 | 0.415161 | 0.000417 |
| S3 | joint_residual_metric_neighbor_hgb | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.415578 | 0.415189 | 0.000388 |
| Q2 | joint_neural_s_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.540598 | 0.540293 | 0.000305 |
| Q2 | joint_neural_cross_family_residual_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.540598 | 0.540293 | 0.000305 |
| Q2 | joint_neural_s_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.540598 | 0.540312 | 0.000285 |
| Q2 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.540598 | 0.540312 | 0.000285 |
