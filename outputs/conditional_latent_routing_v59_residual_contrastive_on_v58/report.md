# Conditional latent routing

- Base OOF: `0.498265`
- Routed OOF: `0.497895`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.543228 | 0.542996 | 0.000232 | 1 |
| Q2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.549630 | 0.549511 | 0.000119 | 1 |
| Q3 | joint_metric_attention_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.517398 | 0.517240 | 0.000159 | 1 |
| S1 | joint_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.488311 | 0.488128 | 0.000183 | 1 |
| S1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.488128 | 0.488003 | 0.000125 | 2 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.475045 | 0.474664 | 0.000382 | 1 |
| S2 | joint_residual_metric_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.474664 | 0.474612 | 0.000052 | 2 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427995 | 0.427545 | 0.000449 | 1 |
| S3 | joint_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.427545 | 0.427209 | 0.000337 | 2 |
| S4 | joint_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.486248 | 0.485694 | 0.000553 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.498265 | 0.543228 | 0.549630 | 0.517398 | 0.488311 | 0.475045 | 0.427995 | 0.486248 |
| conditional_latent_routing | 0.497895 | 0.542996 | 0.549511 | 0.517240 | 0.488003 | 0.474612 | 0.427209 | 0.485694 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | joint_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.486248 | 0.485694 | 0.000553 |
| S4 | joint_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.486248 | 0.485760 | 0.000487 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427995 | 0.427545 | 0.000449 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.475045 | 0.474617 | 0.000428 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.427995 | 0.427608 | 0.000387 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.475045 | 0.474664 | 0.000382 |
| S4 | joint_pls_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.486248 | 0.485869 | 0.000379 |
| S4 | joint_local_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.486248 | 0.485878 | 0.000370 |
| S4 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.486248 | 0.485879 | 0.000369 |
| S3 | joint_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.427995 | 0.427658 | 0.000337 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.475045 | 0.474746 | 0.000299 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.427995 | 0.427700 | 0.000295 |
| S4 | joint_local_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.486248 | 0.485960 | 0.000288 |
| S4 | joint_local_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.486248 | 0.485966 | 0.000282 |
| S4 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.486248 | 0.485968 | 0.000280 |
| S3 | joint_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.427995 | 0.427730 | 0.000265 |
| S3 | joint_metric_neighbor_hgb | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.427995 | 0.427731 | 0.000264 |
| Q1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.543228 | 0.542968 | 0.000260 |
| S3 | joint_metric_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427995 | 0.427738 | 0.000256 |
| S3 | joint_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427995 | 0.427739 | 0.000256 |
