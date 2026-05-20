# Conditional latent routing

- Base OOF: `0.498265`
- Routed OOF: `0.498031`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.543228 | 0.542996 | 0.000232 | 1 |
| Q2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.549630 | 0.549511 | 0.000119 | 1 |
| Q3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.517398 | 0.517323 | 0.000075 | 1 |
| S1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.488311 | 0.488186 | 0.000125 | 1 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.475045 | 0.474664 | 0.000382 | 1 |
| S2 | joint_residual_metric_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.474664 | 0.474612 | 0.000052 | 2 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427995 | 0.427545 | 0.000449 | 1 |
| S3 | joint_residual_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.427545 | 0.427469 | 0.000077 | 2 |
| S4 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.486248 | 0.486118 | 0.000130 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.498265 | 0.543228 | 0.549630 | 0.517398 | 0.488311 | 0.475045 | 0.427995 | 0.486248 |
| conditional_latent_routing | 0.498031 | 0.542996 | 0.549511 | 0.517323 | 0.488186 | 0.474612 | 0.427469 | 0.486118 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427995 | 0.427545 | 0.000449 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.475045 | 0.474617 | 0.000428 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.427995 | 0.427608 | 0.000387 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.475045 | 0.474664 | 0.000382 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.475045 | 0.474746 | 0.000299 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.427995 | 0.427700 | 0.000295 |
| Q1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.543228 | 0.542968 | 0.000260 |
| Q1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.543228 | 0.542996 | 0.000232 |
| S3 | joint_residual_metric_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.427995 | 0.427811 | 0.000184 |
| Q1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.543228 | 0.543047 | 0.000181 |
| S2 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.475045 | 0.474871 | 0.000175 |
| S3 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.427995 | 0.427827 | 0.000168 |
| S3 | joint_residual_metric_neighbor_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.427995 | 0.427844 | 0.000150 |
| S3 | joint_residual_metric_neighbor_hgb | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.427995 | 0.427852 | 0.000143 |
| S1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.488311 | 0.488171 | 0.000140 |
| S4 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.486248 | 0.486118 | 0.000130 |
| S1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.488311 | 0.488182 | 0.000129 |
| S1 | joint_residual_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.488311 | 0.488186 | 0.000125 |
| S3 | joint_residual_metric_neighbor_hgb | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.427995 | 0.427872 | 0.000123 |
| S3 | joint_residual_metric_neighbor_hgb | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.427995 | 0.427872 | 0.000122 |
