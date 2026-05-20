# Conditional latent routing

- Base OOF: `0.529944`
- Routed OOF: `0.526931`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_burden_hgb | mid | 0.333000 | 0.666000 | 0.200000 | 100.000000 | 130.000000 | 0.568535 | 0.567489 | 0.001046 | 1 |
| Q2 | q2_temporal_burden_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116.000000 | 120.000000 | 0.581046 | 0.579956 | 0.001090 | 1 |
| Q3 | q3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.350000 | 291.000000 | 57.000000 | 0.557756 | 0.551672 | 0.006084 | 1 |
| Q3 | q3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291.000000 | 57.000000 | 0.551672 | 0.550642 | 0.001030 | 2 |
| S1 | s1_temporal_burden_logreg | late | 0.666000 | 1.000001 | 0.050000 | 116.000000 | 120.000000 | 0.513798 | 0.512092 | 0.001706 | 1 |
| S2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S3 | s3_temporal_burden_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100.000000 | 130.000000 | 0.461741 | 0.459404 | 0.002337 | 1 |
| S3 | s3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291.000000 | 57.000000 | 0.459404 | 0.457150 | 0.002254 | 2 |
| S3 | s3_temporal_burden_proto | first_half | 0.000000 | 0.500000 | 0.100000 | 291.000000 | 57.000000 | 0.457150 | 0.454949 | 0.002201 | 3 |
| S4 | s4_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.350000 | 291.000000 | 57.000000 | 0.536553 | 0.533210 | 0.003343 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.529944 | 0.568535 | 0.581046 | 0.557756 | 0.513798 | 0.490182 | 0.461741 | 0.536553 |
| conditional_latent_routing | 0.526931 | 0.567489 | 0.579956 | 0.550642 | 0.512092 | 0.490182 | 0.454949 | 0.533210 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | q3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.557756 | 0.551672 | 0.006084 |
| Q3 | q3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.557756 | 0.552835 | 0.004921 |
| Q3 | q3_temporal_burden_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.557756 | 0.552934 | 0.004822 |
| Q3 | q3_temporal_burden_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.557756 | 0.553193 | 0.004563 |
| Q3 | q3_temporal_burden_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.557756 | 0.553255 | 0.004501 |
| Q3 | q3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.557756 | 0.553556 | 0.004200 |
| Q3 | q3_temporal_burden_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.557756 | 0.553889 | 0.003867 |
| Q3 | q3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.557756 | 0.554386 | 0.003370 |
| S4 | s4_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.536553 | 0.533210 | 0.003343 |
| S3 | s3_temporal_burden_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.461741 | 0.458707 | 0.003033 |
| S3 | s3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.461741 | 0.458710 | 0.003031 |
| S3 | s3_temporal_burden_knn_resid | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.461741 | 0.458769 | 0.002972 |
| Q3 | q3_temporal_burden_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.557756 | 0.554845 | 0.002911 |
| S3 | s3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.461741 | 0.458860 | 0.002881 |
| S3 | s3_temporal_burden_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.461741 | 0.458867 | 0.002874 |
| S4 | s4_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.536553 | 0.533840 | 0.002713 |
| S3 | s3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.461741 | 0.459072 | 0.002669 |
| S3 | s3_temporal_burden_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.461741 | 0.459191 | 0.002550 |
| Q3 | q3_temporal_burden_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.557756 | 0.555343 | 0.002413 |
| S3 | s3_temporal_burden_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.461741 | 0.459404 | 0.002337 |
