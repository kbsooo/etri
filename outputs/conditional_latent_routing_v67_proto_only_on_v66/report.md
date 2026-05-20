# Conditional latent routing

- Base OOF: `0.489729`
- Routed OOF: `0.489493`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q3 | joint_proto_neural_multiview_residual_knn_resid | second_half | 0.015000 | 0.000051 | 1 | 0.500000 | 1.000001 | 159.000000 | 193.000000 | 0.509450 | 0.509398 |
| S1 | joint_proto_neural_multiview_residual_knn_logitresid | mid | 0.025000 | 0.000052 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.479082 | 0.479030 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.100000 | 0.001311 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.466655 | 0.465344 |
| S2 | joint_proto_neural_residual_knn_resid | second_half | 0.015000 | 0.000054 | 2 | 0.500000 | 1.000001 | 159.000000 | 193.000000 | 0.465344 | 0.465289 |
| S3 | joint_proto_neural_multiview_residual_knn_resid | mid | 0.050000 | 0.000185 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.419794 | 0.419609 |
| S4 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.489729 | 0.533569 | 0.543122 | 0.509450 | 0.479082 | 0.466655 | 0.419794 | 0.476432 |
| conditional_latent_routing | 0.489493 | 0.533569 | 0.543122 | 0.509398 | 0.479030 | 0.465289 | 0.419609 | 0.476432 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.466655 | 0.465307 | 0.001348 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.466655 | 0.465344 | 0.001311 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.466655 | 0.465511 | 0.001144 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.466655 | 0.465550 | 0.001105 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.466655 | 0.465775 | 0.000880 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.466655 | 0.465850 | 0.000805 |
| S2 | joint_proto_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.466655 | 0.465975 | 0.000680 |
| S2 | joint_proto_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.466655 | 0.466087 | 0.000568 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.466655 | 0.466151 | 0.000504 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.466655 | 0.466216 | 0.000439 |
| S2 | joint_proto_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.466655 | 0.466238 | 0.000417 |
| S2 | joint_proto_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.466655 | 0.466287 | 0.000368 |
| S2 | joint_proto_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.466655 | 0.466308 | 0.000347 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291 | 57 | 0.466655 | 0.466336 | 0.000319 |
| S2 | joint_proto_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.466655 | 0.466368 | 0.000287 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.466655 | 0.466382 | 0.000273 |
| S2 | joint_proto_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.466655 | 0.466427 | 0.000228 |
| S2 | joint_proto_neural_multiview_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.466655 | 0.466431 | 0.000224 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.010000 | 291 | 57 | 0.466655 | 0.466437 | 0.000218 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.466655 | 0.466470 | 0.000185 |
