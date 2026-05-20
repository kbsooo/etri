# Conditional latent routing

- Base OOF: `0.486989`
- Routed OOF: `0.486989`

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
| base | 0.486989 | 0.532067 | 0.541544 | 0.507506 | 0.476227 | 0.459189 | 0.418446 | 0.473941 |
| conditional_latent_routing | 0.486989 | 0.532067 | 0.541544 | 0.507506 | 0.476227 | 0.459189 | 0.418446 | 0.473941 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | joint_neural_mixture_metric_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.507506 | 0.507526 | -0.000020 |
| S4 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.473941 | 0.473963 | -0.000022 |
| S3 | joint_neural_mixture_knn_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.418446 | 0.418473 | -0.000027 |
| Q3 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.507506 | 0.507535 | -0.000028 |
| Q2 | joint_neural_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.541544 | 0.541576 | -0.000032 |
| S3 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.418446 | 0.418479 | -0.000032 |
| S4 | joint_neural_mixture_metric_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.473941 | 0.473978 | -0.000037 |
| Q3 | joint_neural_mixture_metric_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.507506 | 0.507548 | -0.000041 |
| S4 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.473941 | 0.473987 | -0.000046 |
| S3 | joint_neural_mixture_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.418446 | 0.418494 | -0.000047 |
| S3 | joint_neural_mixture_knn_resid | second_half | 0.500000 | 1.000001 | 0.010000 | 159 | 193 | 0.418446 | 0.418501 | -0.000054 |
| S3 | joint_neural_mixture_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.418446 | 0.418503 | -0.000057 |
| Q3 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.507506 | 0.507564 | -0.000058 |
| Q2 | joint_neural_mixture_knn_resid | first_half | 0.000000 | 0.500000 | 0.005000 | 291 | 57 | 0.541544 | 0.541605 | -0.000062 |
| Q3 | joint_neural_mixture_metric_knn_resid | late | 0.666000 | 1.000001 | 0.015000 | 116 | 120 | 0.507506 | 0.507571 | -0.000064 |
| S3 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.418446 | 0.418512 | -0.000065 |
| Q2 | joint_neural_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.541544 | 0.541610 | -0.000066 |
| S1 | joint_neural_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.476227 | 0.476295 | -0.000067 |
| S2 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.459189 | 0.459259 | -0.000070 |
| S4 | joint_neural_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.015000 | 116 | 120 | 0.473941 | 0.474012 | -0.000071 |
