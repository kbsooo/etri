# Conditional latent routing

- Base OOF: `0.514945`
- Routed OOF: `0.514658`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116.000000 | 120.000000 | 0.552813 | 0.552688 | 0.000125 | 1 |
| Q2 | q2_temporal_leadlag_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116.000000 | 120.000000 | 0.571188 | 0.570963 | 0.000224 | 1 |
| Q2 | q2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.100000 | 100.000000 | 130.000000 | 0.570963 | 0.570849 | 0.000114 | 2 |
| Q3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S1 | s1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291.000000 | 57.000000 | 0.500659 | 0.500456 | 0.000204 | 1 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100.000000 | 130.000000 | 0.487423 | 0.486476 | 0.000948 | 1 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159.000000 | 193.000000 | 0.440884 | 0.440488 | 0.000396 | 1 |
| S4 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.514945 | 0.552813 | 0.571188 | 0.541882 | 0.500659 | 0.487423 | 0.440884 | 0.509768 |
| conditional_latent_routing | 0.514658 | 0.552688 | 0.570849 | 0.541882 | 0.500456 | 0.486476 | 0.440488 | 0.509768 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.487423 | 0.486451 | 0.000972 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.487423 | 0.486476 | 0.000948 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.487423 | 0.486510 | 0.000913 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.487423 | 0.486613 | 0.000810 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.487423 | 0.486737 | 0.000686 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.487423 | 0.486907 | 0.000516 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.440884 | 0.440457 | 0.000427 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.440884 | 0.440488 | 0.000396 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.440884 | 0.440502 | 0.000382 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.440884 | 0.440539 | 0.000345 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.487423 | 0.487133 | 0.000290 |
| S1 | s1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.500659 | 0.500379 | 0.000280 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.440884 | 0.440608 | 0.000276 |
| S3 | s3_temporal_leadlag_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.440884 | 0.440619 | 0.000265 |
| S1 | s1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.500659 | 0.500410 | 0.000249 |
| Q2 | q2_temporal_leadlag_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.571188 | 0.570948 | 0.000240 |
| Q2 | q2_temporal_leadlag_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.571188 | 0.570963 | 0.000224 |
| Q1 | q1_temporal_leadlag_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.552813 | 0.552595 | 0.000218 |
| S2 | s2_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.487423 | 0.487207 | 0.000216 |
| S2 | s2_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.487423 | 0.487214 | 0.000209 |
