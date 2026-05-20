# Conditional latent routing

- Base OOF: `0.486152`
- Routed OOF: `0.486144`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q3 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S3 | joint_neural_gated_mixture_knn_resid | mid | 0.025000 | 0.000062 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.417891 | 0.417829 |
| S4 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.486152 | 0.530515 | 0.541332 | 0.506621 | 0.475868 | 0.458462 | 0.417891 | 0.472379 |
| conditional_latent_routing | 0.486144 | 0.530515 | 0.541332 | 0.506621 | 0.475868 | 0.458462 | 0.417829 | 0.472379 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.417891 | 0.417829 | 0.000062 |
| S3 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.417891 | 0.417833 | 0.000058 |
| S3 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.417891 | 0.417845 | 0.000046 |
| S3 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.417891 | 0.417858 | 0.000033 |
| S3 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.417891 | 0.417873 | 0.000018 |
| S3 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.417891 | 0.417894 | -0.000003 |
| S2 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.458462 | 0.458491 | -0.000029 |
| S3 | joint_neural_gated_mixture_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.417891 | 0.417921 | -0.000030 |
| S3 | joint_neural_gated_mixture_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.417891 | 0.417943 | -0.000052 |
| S2 | joint_neural_gated_mixture_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.458462 | 0.458515 | -0.000053 |
| S1 | joint_neural_gated_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.475868 | 0.475923 | -0.000055 |
| S3 | joint_neural_gated_mixture_metric_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.417891 | 0.417947 | -0.000056 |
| S2 | joint_neural_gated_mixture_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.458462 | 0.458521 | -0.000059 |
| S3 | joint_neural_gated_mixture_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.417891 | 0.417952 | -0.000061 |
| S1 | joint_neural_gated_mixture_knn_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.475868 | 0.475930 | -0.000062 |
| S3 | joint_neural_gated_mixture_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.417891 | 0.417955 | -0.000063 |
| S2 | joint_neural_gated_mixture_metric_knn_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.458462 | 0.458526 | -0.000064 |
| S2 | joint_neural_gated_mixture_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.458462 | 0.458527 | -0.000065 |
| S3 | joint_neural_gated_mixture_metric_knn_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.417891 | 0.417961 | -0.000070 |
| S4 | joint_neural_gated_mixture_knn_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.472379 | 0.472453 | -0.000074 |
