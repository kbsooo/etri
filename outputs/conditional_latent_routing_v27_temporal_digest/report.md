# Conditional latent routing

- Base OOF: `0.550558`
- Routed OOF: `0.545176`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.591282 | 0.587336 | 0.003946 | 1 |
| Q1 | q1_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.587336 | 0.586447 | 0.000889 | 2 |
| Q1 | q1_temporal_recovery_hgb | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.586447 | 0.585544 | 0.000903 | 3 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.585544 | 0.584932 | 0.000612 | 4 |
| Q2 | q2_temporal_deviation_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.605005 | 0.602162 | 0.002844 | 1 |
| Q2 | q2_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.602162 | 0.599459 | 0.002703 | 2 |
| Q2 | q2_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.599459 | 0.598617 | 0.000842 | 3 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.598617 | 0.597978 | 0.000638 | 4 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.588775 | 0.583074 | 0.005701 | 1 |
| Q3 | q3_temporal_deviation_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.583074 | 0.581942 | 0.001132 | 2 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.581942 | 0.580994 | 0.000948 | 3 |
| Q3 | q3_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.580994 | 0.580331 | 0.000662 | 4 |
| S1 | s1_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.531237 | 0.528756 | 0.002481 | 1 |
| S1 | s1_temporal_recovery_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.528756 | 0.526402 | 0.002354 | 2 |
| S1 | s1_temporal_recovery_hgb | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.526402 | 0.525326 | 0.001077 | 3 |
| S1 | s1_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.525326 | 0.524657 | 0.000669 | 4 |
| S2 | s2_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.502215 | 0.498930 | 0.003286 | 1 |
| S2 | s2_temporal_deviation_proto | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.498930 | 0.497837 | 0.001092 | 2 |
| S2 | s2_temporal_deviation_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.497837 | 0.497550 | 0.000287 | 3 |
| S3 | s3_temporal_deviation_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.478716 | 0.477929 | 0.000787 | 1 |
| S3 | s3_temporal_deviation_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.477929 | 0.477480 | 0.000449 | 2 |
| S3 | s3_temporal_recovery_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.477480 | 0.477191 | 0.000289 | 3 |
| S4 | s4_temporal_recovery_proto | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.556678 | 0.555120 | 0.001558 | 1 |
| S4 | s4_temporal_recovery_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.555120 | 0.554366 | 0.000754 | 2 |
| S4 | s4_temporal_recovery_hgb | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.554366 | 0.553817 | 0.000549 | 3 |
| S4 | s4_temporal_recovery_hgb | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.553817 | 0.553593 | 0.000224 | 4 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.550558 | 0.591282 | 0.605005 | 0.588775 | 0.531237 | 0.502215 | 0.478716 | 0.556678 |
| conditional_latent_routing | 0.545176 | 0.584932 | 0.597978 | 0.580331 | 0.524657 | 0.497550 | 0.477191 | 0.553593 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.588775 | 0.583074 | 0.005701 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.588775 | 0.583255 | 0.005520 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.588775 | 0.583972 | 0.004803 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.588775 | 0.584412 | 0.004363 |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.591282 | 0.587336 | 0.003946 |
| Q3 | q3_temporal_deviation_logreg | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.588775 | 0.585128 | 0.003648 |
| Q3 | q3_temporal_deviation_logreg | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.588775 | 0.585221 | 0.003555 |
| Q3 | q3_temporal_deviation_logreg | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.588775 | 0.585310 | 0.003465 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.591282 | 0.587936 | 0.003346 |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.591282 | 0.587939 | 0.003343 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.591282 | 0.587941 | 0.003341 |
| S2 | s2_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.502215 | 0.498930 | 0.003286 |
| Q1 | q1_temporal_deviation_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.591282 | 0.588060 | 0.003223 |
| S2 | s2_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.502215 | 0.499012 | 0.003204 |
| Q1 | q1_temporal_deviation_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.591282 | 0.588154 | 0.003128 |
| S2 | s2_temporal_deviation_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.502215 | 0.499126 | 0.003089 |
| Q1 | q1_temporal_deviation_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.591282 | 0.588246 | 0.003037 |
| Q3 | q3_temporal_deviation_logreg | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.588775 | 0.585764 | 0.003011 |
| Q1 | q1_temporal_deviation_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.591282 | 0.588369 | 0.002913 |
| Q2 | q2_temporal_deviation_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.605005 | 0.602162 | 0.002844 |
