# Conditional latent routing

- Base OOF: `0.481505`
- Routed OOF: `0.481505`

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
| base | 0.481505 | 0.525837 | 0.539061 | 0.501390 | 0.470091 | 0.453197 | 0.412158 | 0.468803 |
| conditional_latent_routing | 0.481505 | 0.525837 | 0.539061 | 0.501390 | 0.470091 | 0.453197 | 0.412158 | 0.468803 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_neural_context_attention_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.412158 | 0.412260 | -0.000102 |
| S1 | joint_neural_context_attention_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.470091 | 0.470203 | -0.000112 |
| S3 | joint_neural_context_attention_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.412158 | 0.412329 | -0.000170 |
| S3 | joint_neural_context_attention_knn_logitresid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.412158 | 0.412346 | -0.000187 |
| S3 | joint_neural_context_attention_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.412158 | 0.412368 | -0.000210 |
| S1 | joint_neural_context_metric_attention_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.470091 | 0.470332 | -0.000241 |
| S1 | joint_neural_context_attention_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.470091 | 0.470335 | -0.000244 |
| S3 | joint_neural_context_attention_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.412158 | 0.412422 | -0.000263 |
| S3 | joint_neural_context_metric_attention_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.412158 | 0.412443 | -0.000285 |
| Q1 | joint_neural_context_attention_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.525837 | 0.526162 | -0.000325 |
| S3 | joint_neural_context_metric_attention_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.412158 | 0.412496 | -0.000338 |
| S3 | joint_neural_context_metric_attention_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.412158 | 0.412503 | -0.000345 |
| S3 | joint_neural_context_metric_attention_knn_logitresid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.412158 | 0.412516 | -0.000358 |
| S3 | joint_neural_context_attention_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.412158 | 0.412517 | -0.000359 |
| S3 | joint_neural_context_attention_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.412158 | 0.412550 | -0.000391 |
| S1 | joint_neural_context_attention_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.470091 | 0.470484 | -0.000393 |
| S2 | joint_neural_context_attention_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.453197 | 0.453597 | -0.000400 |
| S1 | joint_neural_context_attention_knn_logitresid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.470091 | 0.470499 | -0.000408 |
| S3 | joint_neural_context_metric_attention_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.412158 | 0.412567 | -0.000408 |
| S1 | joint_neural_context_metric_attention_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.470091 | 0.470510 | -0.000419 |
