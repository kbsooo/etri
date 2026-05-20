# Conditional latent routing

- Base OOF: `0.533214`
- Routed OOF: `0.531332`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_persistence_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159.000000 | 193.000000 | 0.573486 | 0.571898 | 0.001588 | 1 |
| Q1 | q1_temporal_regime_hgb | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.571898 | 0.570889 | 0.001008 | 2 |
| Q1 | q1_temporal_regime_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291.000000 | 57.000000 | 0.570889 | 0.570086 | 0.000804 | 3 |
| Q2 | q2_temporal_regime_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159.000000 | 193.000000 | 0.585996 | 0.584256 | 0.001740 | 1 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116.000000 | 120.000000 | 0.584256 | 0.583377 | 0.000879 | 2 |
| Q3 | q3_temporal_persistence_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291.000000 | 57.000000 | 0.558924 | 0.558079 | 0.000845 | 1 |
| S1 | s1_temporal_persistence_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116.000000 | 120.000000 | 0.519394 | 0.517858 | 0.001536 | 1 |
| S1 | s1_temporal_regime_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100.000000 | 130.000000 | 0.517858 | 0.516213 | 0.001644 | 2 |
| S1 | s1_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.150000 | 291.000000 | 57.000000 | 0.516213 | 0.515457 | 0.000757 | 3 |
| S2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S3 | s3_temporal_regime_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116.000000 | 120.000000 | 0.464365 | 0.463570 | 0.000795 | 1 |
| S4 | s4_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100.000000 | 130.000000 | 0.539153 | 0.538351 | 0.000802 | 1 |
| S4 | s4_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.250000 | 291.000000 | 57.000000 | 0.538351 | 0.537576 | 0.000775 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.533214 | 0.573486 | 0.585996 | 0.558924 | 0.519394 | 0.491178 | 0.464365 | 0.539153 |
| conditional_latent_routing | 0.531332 | 0.570086 | 0.583377 | 0.558079 | 0.515457 | 0.491178 | 0.463570 | 0.537576 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | s1_temporal_regime_logreg | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.519394 | 0.517160 | 0.002233 |
| S1 | s1_temporal_regime_logreg | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.519394 | 0.517274 | 0.002120 |
| S1 | s1_temporal_regime_logreg | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.519394 | 0.517320 | 0.002074 |
| Q2 | q2_temporal_regime_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.585996 | 0.583941 | 0.002055 |
| Q2 | q2_temporal_regime_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.585996 | 0.584058 | 0.001939 |
| S1 | s1_temporal_persistence_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.519394 | 0.517530 | 0.001863 |
| S1 | s1_temporal_persistence_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.519394 | 0.517627 | 0.001767 |
| Q2 | q2_temporal_regime_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.585996 | 0.584256 | 0.001740 |
| S1 | s1_temporal_persistence_knn_logitresid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.519394 | 0.517723 | 0.001670 |
| S1 | s1_temporal_regime_logreg | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.519394 | 0.517749 | 0.001644 |
| Q1 | q1_temporal_persistence_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.573486 | 0.571898 | 0.001588 |
| Q1 | q1_temporal_persistence_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.573486 | 0.571938 | 0.001548 |
| S1 | s1_temporal_persistence_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.519394 | 0.517858 | 0.001536 |
| Q1 | q1_temporal_persistence_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.573486 | 0.571977 | 0.001508 |
| Q2 | q2_temporal_regime_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.585996 | 0.584548 | 0.001448 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.585996 | 0.584601 | 0.001395 |
| S1 | s1_temporal_persistence_knn_resid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.519394 | 0.518037 | 0.001357 |
| Q1 | q1_temporal_regime_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.573486 | 0.572134 | 0.001352 |
| Q1 | q1_temporal_persistence_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.573486 | 0.572170 | 0.001316 |
| Q1 | q1_temporal_regime_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.573486 | 0.572197 | 0.001289 |
