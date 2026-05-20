# Conditional latent routing

- Base OOF: `0.485258`
- Routed OOF: `0.485258`

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
| base | 0.485258 | 0.530257 | 0.541065 | 0.504545 | 0.475179 | 0.457025 | 0.416664 | 0.472072 |
| conditional_latent_routing | 0.485258 | 0.530257 | 0.541065 | 0.504545 | 0.475179 | 0.457025 | 0.416664 | 0.472072 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_neural_learned_gate_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.416664 | 0.416680 | -0.000016 |
| S3 | joint_neural_learned_gate_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.416664 | 0.416681 | -0.000016 |
| S3 | joint_neural_learned_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.416664 | 0.416687 | -0.000023 |
| S1 | joint_neural_learned_gate_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.475179 | 0.475210 | -0.000031 |
| S3 | joint_neural_learned_gate_knn_logitresid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.416664 | 0.416696 | -0.000031 |
| S3 | joint_neural_learned_gate_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.416664 | 0.416698 | -0.000033 |
| Q3 | joint_neural_learned_gate_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.504545 | 0.504579 | -0.000034 |
| S3 | joint_neural_learned_gate_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.416664 | 0.416703 | -0.000038 |
| S3 | joint_neural_learned_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.010000 | 159 | 193 | 0.416664 | 0.416710 | -0.000045 |
| S1 | joint_neural_learned_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.475179 | 0.475227 | -0.000047 |
| S3 | joint_neural_learned_gate_knn_logitresid | late | 0.666000 | 1.000001 | 0.015000 | 116 | 120 | 0.416664 | 0.416712 | -0.000048 |
| S3 | joint_neural_learned_gate_knn_resid | late | 0.666000 | 1.000001 | 0.015000 | 116 | 120 | 0.416664 | 0.416715 | -0.000050 |
| S1 | joint_neural_learned_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.475179 | 0.475232 | -0.000053 |
| S3 | joint_neural_learned_gate_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.416664 | 0.416724 | -0.000059 |
| S3 | joint_neural_learned_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.416664 | 0.416725 | -0.000060 |
| S1 | joint_neural_learned_gate_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.475179 | 0.475241 | -0.000062 |
| Q3 | joint_neural_learned_gate_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.504545 | 0.504613 | -0.000068 |
| S2 | joint_neural_learned_gate_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.457025 | 0.457093 | -0.000068 |
| S3 | joint_neural_learned_gate_knn_resid | second_half | 0.500000 | 1.000001 | 0.015000 | 159 | 193 | 0.416664 | 0.416733 | -0.000069 |
| S1 | joint_neural_learned_gate_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.475179 | 0.475253 | -0.000074 |
