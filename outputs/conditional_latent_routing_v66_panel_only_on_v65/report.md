# Conditional latent routing

- Base OOF: `0.490915`
- Routed OOF: `0.490907`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q3 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S2 | joint_panel_neural_residual_knn_resid | mid | 0.025000 | 0.000057 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.468049 | 0.467992 |
| S3 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S4 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.490915 | 0.534360 | 0.543546 | 0.511237 | 0.480399 | 0.468049 | 0.421222 | 0.477591 |
| conditional_latent_routing | 0.490907 | 0.534360 | 0.543546 | 0.511237 | 0.480399 | 0.467992 | 0.421222 | 0.477591 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.468049 | 0.467992 | 0.000057 |
| Q1 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.534360 | 0.534311 | 0.000049 |
| Q1 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.534360 | 0.534314 | 0.000046 |
| S2 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.468049 | 0.468003 | 0.000045 |
| S4 | joint_panel_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291 | 57 | 0.477591 | 0.477551 | 0.000039 |
| Q1 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.534360 | 0.534324 | 0.000036 |
| S2 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.468049 | 0.468015 | 0.000034 |
| S4 | joint_panel_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.010000 | 291 | 57 | 0.477591 | 0.477558 | 0.000033 |
| S4 | joint_panel_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.477591 | 0.477558 | 0.000032 |
| Q1 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.534360 | 0.534334 | 0.000026 |
| S2 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.468049 | 0.468024 | 0.000024 |
| S3 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.421222 | 0.421200 | 0.000022 |
| S3 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.421222 | 0.421201 | 0.000021 |
| S3 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.421222 | 0.421202 | 0.000020 |
| S4 | joint_panel_neural_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.005000 | 291 | 57 | 0.477591 | 0.477571 | 0.000020 |
| S2 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.468049 | 0.468030 | 0.000019 |
| S3 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.421222 | 0.421207 | 0.000015 |
| S3 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.421222 | 0.421207 | 0.000015 |
| Q1 | joint_panel_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.534360 | 0.534346 | 0.000014 |
| S3 | joint_panel_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.421222 | 0.421209 | 0.000013 |
