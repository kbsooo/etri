# Conditional latent routing

- Base OOF: `0.488680`
- Routed OOF: `0.488537`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q3 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S1 | joint_proto_neural_metric_knn_resid | late | 0.025000 | 0.000050 | 1 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.478086 | 0.478035 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.050000 | 0.000503 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.463496 | 0.462994 |
| S2 | joint_proto_neural_metric_knn_resid | second_half | 0.015000 | 0.000061 | 2 | 0.500000 | 1.000001 | 159.000000 | 193.000000 | 0.462994 | 0.462933 |
| S3 | joint_proto_neural_multiview_metric_knn_resid | mid | 0.100000 | 0.000278 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.419292 | 0.419014 |
| S4 | joint_proto_neural_metric_knn_logitresid | late | 0.050000 | 0.000108 | 1 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.475524 | 0.475416 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.488680 | 0.533398 | 0.542175 | 0.508788 | 0.478086 | 0.463496 | 0.419292 | 0.475524 |
| conditional_latent_routing | 0.488537 | 0.533398 | 0.542175 | 0.508788 | 0.478035 | 0.462933 | 0.419014 | 0.475416 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.463496 | 0.462994 | 0.000503 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.463496 | 0.463014 | 0.000482 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.463496 | 0.463145 | 0.000352 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.463496 | 0.463181 | 0.000315 |
| S3 | joint_proto_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.419292 | 0.419014 | 0.000278 |
| S3 | joint_proto_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.419292 | 0.419027 | 0.000264 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.015000 | 291 | 57 | 0.463496 | 0.463260 | 0.000237 |
| S3 | joint_proto_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.419292 | 0.419075 | 0.000216 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.010000 | 291 | 57 | 0.463496 | 0.463330 | 0.000167 |
| S3 | joint_proto_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.419292 | 0.419162 | 0.000130 |
| S3 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.419292 | 0.419163 | 0.000129 |
| S3 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.419292 | 0.419164 | 0.000127 |
| S4 | joint_proto_neural_metric_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.475524 | 0.475416 | 0.000108 |
| S4 | joint_proto_neural_metric_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.475524 | 0.475426 | 0.000098 |
| S3 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.419292 | 0.419197 | 0.000094 |
| S2 | joint_proto_neural_multiview_metric_knn_resid | first_half | 0.000000 | 0.500000 | 0.005000 | 291 | 57 | 0.463496 | 0.463408 | 0.000088 |
| S3 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.419292 | 0.419205 | 0.000086 |
| S3 | joint_proto_neural_multiview_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.419292 | 0.419208 | 0.000083 |
| S2 | joint_proto_neural_metric_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.463496 | 0.463418 | 0.000078 |
| S4 | joint_proto_neural_metric_knn_logitresid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.475524 | 0.475449 | 0.000075 |
