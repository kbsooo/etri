# Conditional latent routing

- Base OOF: `0.516460`
- Routed OOF: `0.513510`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.350000 | 234 | 0 | 0.555379 | 0.552674 | 0.002705 | 1 |
| Q1 | q1_temporal_leadlag_knn_resid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.552674 | 0.551721 | 0.000953 | 2 |
| Q1 | q1_temporal_leadlag_knn_logitresid | tail | 0.800000 | 1.000001 | 0.350000 | 22 | 120 | 0.551721 | 0.551279 | 0.000442 | 3 |
| Q1 | q1_temporal_leadlag_proto | early | 0.000000 | 0.333000 | 0.050000 | 234 | 0 | 0.551279 | 0.551050 | 0.000229 | 4 |
| Q1 | q1_sleep_retrieval_meta | late_mid | 0.666000 | 0.800000 | 0.150000 | 94 | 0 | 0.551050 | 0.550926 | 0.000125 | 5 |
| Q1 | q1_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.550926 | 0.550816 | 0.000110 | 6 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.550816 | 0.550740 | 0.000076 | 7 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.573849 | 0.571453 | 0.002396 | 1 |
| Q2 | q2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.571453 | 0.571029 | 0.000424 | 2 |
| Q2 | q2_temporal_leadlag_knn_label | tail | 0.800000 | 1.000001 | 0.200000 | 22 | 120 | 0.571029 | 0.570677 | 0.000352 | 3 |
| Q2 | q2_temporal_leadlag_knn_label | tail | 0.800000 | 1.000001 | 0.150000 | 22 | 120 | 0.570677 | 0.570626 | 0.000052 | 4 |
| Q2 | q2_temporal_leadlag_knn_logitresid | tail | 0.800000 | 1.000001 | 0.150000 | 22 | 120 | 0.570626 | 0.570566 | 0.000060 | 5 |
| Q2 | q2_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.050000 | 94 | 0 | 0.570566 | 0.570511 | 0.000055 | 6 |
| Q2 | q2_temporal_leadlag_proto | late_mid | 0.666000 | 0.800000 | 0.025000 | 94 | 0 | 0.570511 | 0.570440 | 0.000070 | 7 |
| Q3 | q3_temporal_leadlag_logreg | early | 0.000000 | 0.333000 | 0.050000 | 234 | 0 | 0.542039 | 0.541649 | 0.000390 | 1 |
| Q3 | q3_temporal_leadlag_knn_logitresid | late_mid | 0.666000 | 0.800000 | 0.100000 | 94 | 0 | 0.541649 | 0.541362 | 0.000287 | 2 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.541362 | 0.541138 | 0.000225 | 3 |
| Q3 | q3_sleep_retrieval_meta | late_mid | 0.666000 | 0.800000 | 0.150000 | 94 | 0 | 0.541138 | 0.540996 | 0.000142 | 4 |
| Q3 | q3_temporal_leadlag_knn_logitresid | late_mid | 0.666000 | 0.800000 | 0.075000 | 94 | 0 | 0.540996 | 0.540857 | 0.000139 | 5 |
| Q3 | q3_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.540857 | 0.540797 | 0.000061 | 6 |
| Q3 | q3_temporal_leadlag_knn_resid | tail | 0.800000 | 1.000001 | 0.075000 | 22 | 120 | 0.540797 | 0.540743 | 0.000054 | 7 |
| S1 | s1_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.350000 | 94 | 0 | 0.502133 | 0.499489 | 0.002645 | 1 |
| S1 | s1_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.075000 | 234 | 0 | 0.499489 | 0.498813 | 0.000676 | 2 |
| S1 | s1_temporal_leadlag_knn_label | tail | 0.800000 | 1.000001 | 0.150000 | 22 | 120 | 0.498813 | 0.498688 | 0.000125 | 3 |
| S1 | s1_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.150000 | 94 | 0 | 0.498688 | 0.498543 | 0.000145 | 4 |
| S1 | s1_temporal_leadlag_proto | late_mid | 0.666000 | 0.800000 | 0.050000 | 94 | 0 | 0.498543 | 0.498491 | 0.000052 | 5 |
| S2 | s2_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.488554 | 0.487286 | 0.001269 | 1 |
| S2 | s2_sleep_retrieval_meta | early | 0.000000 | 0.333000 | 0.150000 | 234 | 0 | 0.487286 | 0.486768 | 0.000517 | 2 |
| S2 | s2_temporal_leadlag_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.486768 | 0.486372 | 0.000396 | 3 |
| S2 | s2_sleep_retrieval_meta | tail | 0.800000 | 1.000001 | 0.250000 | 22 | 120 | 0.486372 | 0.486062 | 0.000310 | 4 |
| S2 | s2_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.100000 | 94 | 0 | 0.486062 | 0.485820 | 0.000242 | 5 |
| S2 | s2_temporal_leadlag_logreg | late_mid | 0.666000 | 0.800000 | 0.050000 | 94 | 0 | 0.485820 | 0.485597 | 0.000223 | 6 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.443108 | 0.440884 | 0.002224 | 1 |
| S3 | s3_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.250000 | 234 | 0 | 0.440884 | 0.440473 | 0.000411 | 2 |
| S3 | s3_temporal_leadlag_logreg | late_mid | 0.666000 | 0.800000 | 0.025000 | 94 | 0 | 0.440473 | 0.440379 | 0.000095 | 3 |
| S3 | s3_temporal_leadlag_proto | early | 0.000000 | 0.333000 | 0.025000 | 234 | 0 | 0.440379 | 0.440283 | 0.000095 | 4 |
| S4 | s4_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.100000 | 234 | 0 | 0.510161 | 0.508990 | 0.001171 | 1 |
| S4 | s4_temporal_leadlag_hgb | early | 0.000000 | 0.333000 | 0.050000 | 234 | 0 | 0.508990 | 0.508716 | 0.000275 | 2 |
| S4 | s4_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.050000 | 94 | 0 | 0.508716 | 0.508559 | 0.000156 | 3 |
| S4 | s4_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.050000 | 234 | 0 | 0.508559 | 0.508458 | 0.000102 | 4 |
| S4 | s4_temporal_leadlag_hgb | early | 0.000000 | 0.333000 | 0.025000 | 234 | 0 | 0.508458 | 0.508380 | 0.000078 | 5 |
| S4 | s4_temporal_leadlag_hgb | tail | 0.800000 | 1.000001 | 0.050000 | 22 | 120 | 0.508380 | 0.508329 | 0.000051 | 6 |
| S4 | s4_temporal_leadlag_knn_logitresid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.508329 | 0.508277 | 0.000052 | 7 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.516460 | 0.555379 | 0.573849 | 0.542039 | 0.502133 | 0.488554 | 0.443108 | 0.510161 |
| conditional_latent_routing | 0.513510 | 0.550740 | 0.570440 | 0.540743 | 0.498491 | 0.485597 | 0.440283 | 0.508277 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.350000 | 234 | 0 | 0.555379 | 0.552674 | 0.002705 |
| S1 | s1_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.350000 | 94 | 0 | 0.502133 | 0.499489 | 0.002645 |
| Q1 | q1_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.250000 | 234 | 0 | 0.555379 | 0.552769 | 0.002610 |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.555379 | 0.552813 | 0.002566 |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.555379 | 0.552890 | 0.002489 |
| Q1 | q1_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.555379 | 0.552957 | 0.002421 |
| Q1 | q1_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.200000 | 234 | 0 | 0.555379 | 0.552963 | 0.002415 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.573849 | 0.571453 | 0.002396 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.555379 | 0.553005 | 0.002373 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.555379 | 0.553010 | 0.002369 |
| S1 | s1_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.250000 | 94 | 0 | 0.502133 | 0.499836 | 0.002298 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.573849 | 0.571612 | 0.002237 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.443108 | 0.440884 | 0.002224 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.443108 | 0.440910 | 0.002198 |
| Q1 | q1_temporal_leadlag_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.555379 | 0.553186 | 0.002192 |
| S3 | s3_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.350000 | 234 | 0 | 0.443108 | 0.440938 | 0.002170 |
| Q1 | q1_temporal_leadlag_knn_resid | early | 0.000000 | 0.333000 | 0.150000 | 234 | 0 | 0.555379 | 0.553282 | 0.002097 |
| S3 | s3_temporal_leadlag_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.443108 | 0.441038 | 0.002070 |
| S1 | s1_temporal_leadlag_knn_resid | late_mid | 0.666000 | 0.800000 | 0.200000 | 94 | 0 | 0.502133 | 0.500100 | 0.002033 |
| Q2 | q2_temporal_leadlag_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.573849 | 0.571847 | 0.002002 |
