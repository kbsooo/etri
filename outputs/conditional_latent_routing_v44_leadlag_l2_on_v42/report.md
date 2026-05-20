# Conditional latent routing

- Base OOF: `0.513510`
- Routed OOF: `0.513329`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | q2_sleep_retrieval_meta | mid | 0.075000 | 0.000134 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.570440 | 0.570306 |
| Q3 | q3_sleep_retrieval_meta | first_half | 0.050000 | 0.000156 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.540743 | 0.540587 |
| S1 | s1_temporal_leadlag_knn_resid | first_half | 0.025000 | 0.000158 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.498491 | 0.498333 |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.050000 | 0.000524 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.485597 | 0.485073 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.075000 | 0.000298 | 1 | 0.500000 | 1.000001 | 159.000000 | 193.000000 | 0.440283 | 0.439985 |
| S4 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.513510 | 0.550740 | 0.570440 | 0.540743 | 0.498491 | 0.485597 | 0.440283 | 0.508277 |
| conditional_latent_routing | 0.513329 | 0.550740 | 0.570306 | 0.540587 | 0.498333 | 0.485073 | 0.439985 | 0.508277 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.485597 | 0.484985 | 0.000612 |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.485597 | 0.484991 | 0.000606 |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.485597 | 0.485073 | 0.000524 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.485597 | 0.485207 | 0.000390 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.485597 | 0.485226 | 0.000371 |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.485597 | 0.485233 | 0.000364 |
| S2 | s2_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.485597 | 0.485248 | 0.000349 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.440283 | 0.439949 | 0.000335 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.485597 | 0.485263 | 0.000334 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.440283 | 0.439950 | 0.000333 |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.485597 | 0.485271 | 0.000326 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.485597 | 0.485271 | 0.000326 |
| S2 | s2_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.485597 | 0.485285 | 0.000312 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.440283 | 0.439985 | 0.000298 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.440283 | 0.440023 | 0.000260 |
| S2 | s2_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.025000 | 450 | 250 | 0.485597 | 0.485345 | 0.000252 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.485597 | 0.485345 | 0.000252 |
| S1 | s1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.498491 | 0.498248 | 0.000243 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.440283 | 0.440050 | 0.000233 |
| S1 | s1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.025000 | 450 | 250 | 0.498491 | 0.498268 | 0.000223 |
