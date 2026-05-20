# Conditional latent routing

- Base OOF: `0.484026`
- Routed OOF: `0.484026`

## Selected Moves

| target | source | bin | weight | improvement | move_index |
| --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |
| Q2 | base | all | 0.000000 | 0.000000 | 0 |
| Q3 | base | all | 0.000000 | 0.000000 | 0 |
| S1 | base | all | 0.000000 | 0.000000 | 0 |
| S2 | base | all | 0.000000 | 0.000000 | 0 |
| S3 | base | all | 0.000000 | 0.000000 | 0 |
| S4 | base | all | 0.000000 | 0.000000 | 0 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.484026 | 0.527627 | 0.540598 | 0.504044 | 0.472902 | 0.455850 | 0.415578 | 0.471582 |
| conditional_latent_routing | 0.484026 | 0.527627 | 0.540598 | 0.504044 | 0.472902 | 0.455850 | 0.415578 | 0.471582 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_neural_bin_gate_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.415578 | 0.415617 | -0.000039 |
| S3 | joint_neural_bin_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.415578 | 0.415617 | -0.000040 |
| Q1 | joint_neural_bin_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.527627 | 0.527671 | -0.000045 |
| S1 | joint_neural_bin_gate_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.472902 | 0.472947 | -0.000045 |
| S3 | joint_neural_bin_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.415578 | 0.415624 | -0.000046 |
| S4 | joint_neural_bin_gate_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.471582 | 0.471633 | -0.000051 |
| S3 | joint_neural_bin_gate_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.415578 | 0.415637 | -0.000059 |
| S4 | joint_neural_bin_gate_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.471582 | 0.471645 | -0.000063 |
| S4 | joint_neural_bin_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.471582 | 0.471646 | -0.000064 |
| Q1 | joint_neural_bin_gate_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.527627 | 0.527697 | -0.000070 |
| S1 | joint_neural_bin_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.472902 | 0.472980 | -0.000077 |
| S4 | joint_neural_bin_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.471582 | 0.471660 | -0.000078 |
| S3 | joint_neural_bin_gate_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.415578 | 0.415657 | -0.000079 |
| S3 | joint_neural_bin_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.415578 | 0.415657 | -0.000079 |
| S3 | joint_neural_bin_gate_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.415578 | 0.415657 | -0.000080 |
| S1 | joint_neural_bin_gate_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.472902 | 0.472990 | -0.000088 |
| Q1 | joint_neural_bin_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.527627 | 0.527716 | -0.000089 |
| S1 | joint_neural_bin_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.472902 | 0.472992 | -0.000090 |
| S1 | joint_neural_bin_gate_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.472902 | 0.472992 | -0.000090 |
| S3 | joint_neural_bin_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.010000 | 159 | 193 | 0.415578 | 0.415671 | -0.000094 |
