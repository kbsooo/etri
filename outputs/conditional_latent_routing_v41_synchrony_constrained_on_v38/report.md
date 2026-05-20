# Conditional latent routing

- Base OOF: `0.521168`
- Routed OOF: `0.517632`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291.000000 | 57.000000 | 0.558669 | 0.557468 | 0.001202 | 1 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116.000000 | 120.000000 | 0.575663 | 0.574581 | 0.001081 | 1 |
| Q3 | q3_temporal_synchrony_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100.000000 | 130.000000 | 0.545006 | 0.542737 | 0.002269 | 1 |
| S1 | s1_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.150000 | 450.000000 | 250.000000 | 0.505435 | 0.502749 | 0.002686 | 1 |
| S2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S3 | s3_temporal_synchrony_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116.000000 | 120.000000 | 0.447148 | 0.445936 | 0.001212 | 1 |
| S3 | s3_temporal_synchrony_logreg | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.445936 | 0.444784 | 0.001151 | 2 |
| S4 | s4_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.250000 | 291.000000 | 57.000000 | 0.526575 | 0.516405 | 0.010170 | 1 |
| S4 | s4_temporal_synchrony_knn_resid | late | 0.666000 | 1.000001 | 0.350000 | 116.000000 | 120.000000 | 0.516405 | 0.512521 | 0.003884 | 2 |
| S4 | s4_temporal_synchrony_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100.000000 | 130.000000 | 0.512521 | 0.511425 | 0.001096 | 3 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.521168 | 0.558669 | 0.575663 | 0.545006 | 0.505435 | 0.489683 | 0.447148 | 0.526575 |
| conditional_latent_routing | 0.517632 | 0.557468 | 0.574581 | 0.542737 | 0.502749 | 0.489683 | 0.444784 | 0.511425 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | s4_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.526575 | 0.515428 | 0.011147 |
| S4 | s4_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.526575 | 0.516118 | 0.010458 |
| S4 | s4_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.526575 | 0.516405 | 0.010170 |
| S4 | s4_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.526575 | 0.516544 | 0.010031 |
| S4 | s4_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.526575 | 0.516864 | 0.009711 |
| S4 | s4_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.526575 | 0.517536 | 0.009039 |
| S4 | s4_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.526575 | 0.518270 | 0.008306 |
| S4 | s4_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.526575 | 0.519110 | 0.007465 |
| S4 | s4_temporal_synchrony_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.526575 | 0.519299 | 0.007276 |
| S4 | s4_temporal_synchrony_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.526575 | 0.519389 | 0.007186 |
| S4 | s4_temporal_synchrony_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.526575 | 0.519955 | 0.006621 |
| S4 | s4_temporal_synchrony_knn_resid | all | 0.000000 | 1.000001 | 0.350000 | 450 | 250 | 0.526575 | 0.520139 | 0.006436 |
| S4 | s4_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.526575 | 0.520349 | 0.006227 |
| S4 | s4_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.526575 | 0.521136 | 0.005440 |
| S4 | s4_temporal_synchrony_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.526575 | 0.521163 | 0.005413 |
| S4 | s4_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.526575 | 0.521853 | 0.004723 |
| S4 | s4_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.526575 | 0.521936 | 0.004639 |
| S4 | s4_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.526575 | 0.522319 | 0.004256 |
| S4 | s4_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.526575 | 0.522325 | 0.004250 |
| S4 | s4_temporal_synchrony_knn_resid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.526575 | 0.522691 | 0.003884 |
