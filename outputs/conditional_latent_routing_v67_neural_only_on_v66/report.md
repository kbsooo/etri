# Conditional latent routing

- Base OOF: `0.489729`
- Routed OOF: `0.489030`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_panel_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.533569 | 0.533453 | 0.000117 | 1 |
| Q2 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.543122 | 0.542315 | 0.000807 | 1 |
| Q3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.509450 | 0.508788 | 0.000661 | 1 |
| S1 | joint_panel_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479082 | 0.478324 | 0.000758 | 1 |
| S1 | joint_neural_s_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.478324 | 0.478086 | 0.000238 | 2 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.466655 | 0.465344 | 0.001311 | 1 |
| S2 | joint_proto_neural_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.015000 | 159 | 193 | 0.465344 | 0.465289 | 0.000054 | 2 |
| S3 | joint_neural_cross_family_residual_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.419794 | 0.419327 | 0.000467 | 1 |
| S4 | joint_target_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.476432 | 0.476009 | 0.000423 | 1 |
| S4 | joint_neural_multiview_s_residual_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.476009 | 0.475951 | 0.000058 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.489729 | 0.533569 | 0.543122 | 0.509450 | 0.479082 | 0.466655 | 0.419794 | 0.476432 |
| conditional_latent_routing | 0.489030 | 0.533453 | 0.542315 | 0.508788 | 0.478086 | 0.465289 | 0.419327 | 0.475951 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.466655 | 0.465307 | 0.001348 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.466655 | 0.465344 | 0.001311 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.466655 | 0.465511 | 0.001144 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.466655 | 0.465550 | 0.001105 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.466655 | 0.465775 | 0.000880 |
| Q2 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.543122 | 0.542315 | 0.000807 |
| S2 | joint_proto_neural_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.466655 | 0.465850 | 0.000805 |
| S1 | joint_panel_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479082 | 0.478324 | 0.000758 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.479082 | 0.478385 | 0.000697 |
| Q2 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.543122 | 0.542430 | 0.000692 |
| S2 | joint_proto_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.466655 | 0.465975 | 0.000680 |
| Q3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.509450 | 0.508788 | 0.000661 |
| S1 | joint_panel_neural_multiview_residual_knn_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.479082 | 0.478463 | 0.000619 |
| S1 | joint_panel_neural_multiview_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.479082 | 0.478479 | 0.000603 |
| S2 | joint_proto_neural_residual_knn_logitresid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.466655 | 0.466087 | 0.000568 |
| Q3 | joint_neural_residual_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.509450 | 0.508895 | 0.000555 |
| Q2 | joint_neural_multiview_q_residual_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.543122 | 0.542598 | 0.000524 |
| S2 | joint_proto_neural_multiview_residual_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.466655 | 0.466151 | 0.000504 |
| S3 | joint_neural_q_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.419794 | 0.419292 | 0.000502 |
| S3 | joint_neural_cross_family_residual_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.419794 | 0.419292 | 0.000502 |
