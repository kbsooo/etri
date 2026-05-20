# Conditional latent routing

- Base OOF: `0.482206`
- Routed OOF: `0.481614`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291.000000 | 57.000000 | 0.526613 | 0.525972 | 0.000641 | 1 |
| Q1 | joint_neural_context_bin_gate_hgb_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159.000000 | 193.000000 | 0.525972 | 0.525837 | 0.000135 | 2 |
| Q2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| Q3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116.000000 | 120.000000 | 0.501873 | 0.501390 | 0.000483 | 1 |
| S1 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S2 | joint_neural_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291.000000 | 57.000000 | 0.453825 | 0.453197 | 0.000628 | 1 |
| S3 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291.000000 | 57.000000 | 0.412963 | 0.412512 | 0.000450 | 1 |
| S3 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159.000000 | 193.000000 | 0.412512 | 0.412158 | 0.000354 | 2 |
| S4 | joint_proto_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.470452 | 0.469105 | 0.001347 | 1 |
| S4 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100.000000 | 130.000000 | 0.469105 | 0.468998 | 0.000107 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.482206 | 0.526613 | 0.539167 | 0.501873 | 0.470550 | 0.453825 | 0.412963 | 0.470452 |
| conditional_latent_routing | 0.481614 | 0.525837 | 0.539167 | 0.501390 | 0.470550 | 0.453197 | 0.412158 | 0.468998 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | joint_proto_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.470452 | 0.469105 | 0.001347 |
| S4 | joint_proto_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.470452 | 0.469139 | 0.001312 |
| S4 | joint_proto_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.470452 | 0.469160 | 0.001292 |
| S4 | joint_proto_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.470452 | 0.469296 | 0.001156 |
| S4 | joint_proto_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.470452 | 0.469338 | 0.001113 |
| S4 | joint_proto_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.470452 | 0.469340 | 0.001112 |
| S4 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.470452 | 0.469432 | 0.001019 |
| S4 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.470452 | 0.469522 | 0.000929 |
| S4 | joint_proto_neural_metric_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.470452 | 0.469575 | 0.000877 |
| S4 | joint_proto_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.470452 | 0.469603 | 0.000849 |
| S4 | joint_proto_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.470452 | 0.469617 | 0.000835 |
| S4 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.470452 | 0.469712 | 0.000740 |
| Q1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.526613 | 0.525938 | 0.000675 |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.526613 | 0.525938 | 0.000675 |
| Q1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.526613 | 0.525972 | 0.000641 |
| Q1 | joint_neural_cross_family_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.526613 | 0.525972 | 0.000641 |
| S2 | joint_neural_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.453825 | 0.453197 | 0.000628 |
| S2 | joint_neural_q_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.453825 | 0.453197 | 0.000628 |
| S2 | joint_neural_cross_family_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.453825 | 0.453270 | 0.000555 |
| S2 | joint_neural_q_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.453825 | 0.453270 | 0.000555 |
