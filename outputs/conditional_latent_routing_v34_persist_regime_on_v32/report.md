# Conditional latent routing

- Base OOF: `0.533214`
- Routed OOF: `0.529944`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_persistence_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.573486 | 0.571898 | 0.001588 | 1 |
| Q1 | q1_temporal_regime_hgb | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.571898 | 0.570411 | 0.001486 | 2 |
| Q1 | q1_temporal_regime_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.570411 | 0.569059 | 0.001352 | 3 |
| Q1 | q1_temporal_persistence_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.569059 | 0.568725 | 0.000335 | 4 |
| Q1 | q1_temporal_persistence_logreg | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.568725 | 0.568586 | 0.000138 | 5 |
| Q1 | q1_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.568586 | 0.568535 | 0.000051 | 6 |
| Q2 | q2_temporal_regime_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.585996 | 0.583941 | 0.002055 | 1 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.583941 | 0.582415 | 0.001526 | 2 |
| Q2 | q2_temporal_persistence_knn_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.582415 | 0.581928 | 0.000487 | 3 |
| Q2 | q2_temporal_regime_logreg | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.581928 | 0.581519 | 0.000409 | 4 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.581519 | 0.581250 | 0.000268 | 5 |
| Q2 | q2_temporal_persistence_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.581250 | 0.581046 | 0.000205 | 6 |
| Q3 | q3_temporal_persistence_knn_resid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.558924 | 0.558079 | 0.000845 | 1 |
| Q3 | q3_temporal_regime_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.558079 | 0.557882 | 0.000197 | 2 |
| Q3 | q3_temporal_regime_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.557882 | 0.557756 | 0.000126 | 3 |
| S1 | s1_temporal_regime_logreg | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.519394 | 0.517160 | 0.002233 | 1 |
| S1 | s1_temporal_persistence_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.517160 | 0.515297 | 0.001863 | 2 |
| S1 | s1_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.515297 | 0.514483 | 0.000814 | 3 |
| S1 | s1_temporal_regime_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.514483 | 0.514064 | 0.000419 | 4 |
| S1 | s1_temporal_persistence_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.514064 | 0.513867 | 0.000197 | 5 |
| S1 | s1_temporal_persistence_knn_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.513867 | 0.513798 | 0.000069 | 6 |
| S2 | s2_temporal_persistence_proto | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.491178 | 0.490527 | 0.000650 | 1 |
| S2 | s2_temporal_persistence_logreg | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.490527 | 0.490264 | 0.000263 | 2 |
| S2 | s2_temporal_regime_proto | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.490264 | 0.490182 | 0.000083 | 3 |
| S3 | s3_temporal_regime_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.464365 | 0.463371 | 0.000994 | 1 |
| S3 | s3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.463371 | 0.462766 | 0.000605 | 2 |
| S3 | s3_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.462766 | 0.462520 | 0.000246 | 3 |
| S3 | s3_temporal_regime_knn_logitresid | all | 0.000000 | 1.000001 | 0.050000 | 450 | 250 | 0.462520 | 0.462185 | 0.000335 | 4 |
| S3 | s3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.462185 | 0.461938 | 0.000247 | 5 |
| S3 | s3_temporal_persistence_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.461938 | 0.461741 | 0.000197 | 6 |
| S4 | s4_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.539153 | 0.538037 | 0.001116 | 1 |
| S4 | s4_temporal_regime_logreg | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.538037 | 0.537356 | 0.000681 | 2 |
| S4 | s4_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.537356 | 0.536859 | 0.000497 | 3 |
| S4 | s4_temporal_regime_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.536859 | 0.536657 | 0.000202 | 4 |
| S4 | s4_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.536657 | 0.536604 | 0.000054 | 5 |
| S4 | s4_temporal_persistence_hgb | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.536604 | 0.536553 | 0.000051 | 6 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.533214 | 0.573486 | 0.585996 | 0.558924 | 0.519394 | 0.491178 | 0.464365 | 0.539153 |
| conditional_latent_routing | 0.529944 | 0.568535 | 0.581046 | 0.557756 | 0.513798 | 0.490182 | 0.461741 | 0.536553 |

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
| S1 | s1_temporal_regime_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.519394 | 0.518063 | 0.001330 |
| Q1 | q1_temporal_persistence_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.573486 | 0.572170 | 0.001316 |
