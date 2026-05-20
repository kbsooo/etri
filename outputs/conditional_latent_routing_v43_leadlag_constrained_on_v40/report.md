# Conditional latent routing

- Base OOF: `0.516460`
- Routed OOF: `0.514945`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.555379 | 0.552813 | 0.002566 | 1 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.573849 | 0.571612 | 0.002237 | 1 |
| Q2 | q2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.571612 | 0.571188 | 0.000424 | 2 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.542039 | 0.541882 | 0.000156 | 1 |
| S1 | s1_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.502133 | 0.501229 | 0.000904 | 1 |
| S1 | s1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.501229 | 0.500659 | 0.000570 | 2 |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.488554 | 0.487423 | 0.001131 | 1 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.443108 | 0.440884 | 0.002224 | 1 |
| S4 | s4_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.510161 | 0.509768 | 0.000393 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.516460 | 0.555379 | 0.573849 | 0.542039 | 0.502133 | 0.488554 | 0.443108 | 0.510161 |
| conditional_latent_routing | 0.514945 | 0.552813 | 0.571188 | 0.541882 | 0.500659 | 0.487423 | 0.440884 | 0.509768 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.555379 | 0.552813 | 0.002566 |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.555379 | 0.552890 | 0.002489 |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.555379 | 0.552957 | 0.002421 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.555379 | 0.553005 | 0.002373 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.555379 | 0.553010 | 0.002369 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.573849 | 0.571612 | 0.002237 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.443108 | 0.440884 | 0.002224 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.443108 | 0.440910 | 0.002198 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.555379 | 0.553186 | 0.002192 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.443108 | 0.441038 | 0.002070 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.573849 | 0.571847 | 0.002002 |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.555379 | 0.553377 | 0.002002 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.555379 | 0.553586 | 0.001793 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.443108 | 0.441413 | 0.001695 |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.555379 | 0.553713 | 0.001666 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.573849 | 0.572187 | 0.001662 |
| S3 | s3_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.443108 | 0.441559 | 0.001549 |
| S3 | s3_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.443108 | 0.441620 | 0.001488 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.555379 | 0.553891 | 0.001488 |
| S3 | s3_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.443108 | 0.441629 | 0.001479 |
