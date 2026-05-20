# Conditional latent routing

- Base OOF: `0.521168`
- Routed OOF: `0.516460`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.558669 | 0.557468 | 0.001202 | 1 |
| Q1 | q1_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.557468 | 0.556852 | 0.000616 | 2 |
| Q1 | q1_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.556852 | 0.556313 | 0.000539 | 3 |
| Q1 | q1_temporal_synchrony_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.556313 | 0.555840 | 0.000473 | 4 |
| Q1 | q1_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.555840 | 0.555584 | 0.000256 | 5 |
| Q1 | q1_temporal_synchrony_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.555584 | 0.555379 | 0.000206 | 6 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.575663 | 0.574304 | 0.001359 | 1 |
| Q2 | q2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.574304 | 0.574033 | 0.000271 | 2 |
| Q2 | q2_temporal_synchrony_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.574033 | 0.573849 | 0.000184 | 3 |
| Q3 | q3_temporal_synchrony_knn_logitresid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.545006 | 0.542503 | 0.002502 | 1 |
| Q3 | q3_temporal_synchrony_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.542503 | 0.542172 | 0.000331 | 2 |
| Q3 | q3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.542172 | 0.542039 | 0.000133 | 3 |
| S1 | s1_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.505435 | 0.502749 | 0.002686 | 1 |
| S1 | s1_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.502749 | 0.502395 | 0.000354 | 2 |
| S1 | s1_temporal_synchrony_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.502395 | 0.502133 | 0.000261 | 3 |
| S2 | s2_temporal_synchrony_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.489683 | 0.489013 | 0.000670 | 1 |
| S2 | s2_temporal_synchrony_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.489013 | 0.488631 | 0.000382 | 2 |
| S2 | s2_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.488631 | 0.488554 | 0.000077 | 3 |
| S3 | s3_temporal_synchrony_knn_resid | second_half | 0.500000 | 1.000001 | 0.350000 | 159 | 193 | 0.447148 | 0.445488 | 0.001660 | 1 |
| S3 | s3_temporal_synchrony_logreg | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.445488 | 0.444298 | 0.001189 | 2 |
| S3 | s3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.444298 | 0.443553 | 0.000745 | 3 |
| S3 | s3_temporal_synchrony_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.443553 | 0.443285 | 0.000269 | 4 |
| S3 | s3_temporal_synchrony_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.443285 | 0.443163 | 0.000122 | 5 |
| S3 | s3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.443163 | 0.443108 | 0.000055 | 6 |
| S4 | s4_temporal_synchrony_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.350000 | 291 | 57 | 0.526575 | 0.515428 | 0.011147 | 1 |
| S4 | s4_temporal_synchrony_knn_resid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.515428 | 0.511544 | 0.003884 | 2 |
| S4 | s4_temporal_synchrony_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.511544 | 0.510948 | 0.000596 | 3 |
| S4 | s4_temporal_synchrony_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.510948 | 0.510522 | 0.000426 | 4 |
| S4 | s4_temporal_synchrony_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.510522 | 0.510161 | 0.000361 | 5 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.521168 | 0.558669 | 0.575663 | 0.545006 | 0.505435 | 0.489683 | 0.447148 | 0.526575 |
| conditional_latent_routing | 0.516460 | 0.555379 | 0.573849 | 0.542039 | 0.502133 | 0.488554 | 0.443108 | 0.510161 |

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
| S4 | s4_temporal_synchrony_knn_logitresid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.526575 | 0.521645 | 0.004931 |
| S4 | s4_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.526575 | 0.521853 | 0.004723 |
| S4 | s4_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.526575 | 0.521936 | 0.004639 |
| S4 | s4_temporal_synchrony_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.526575 | 0.522080 | 0.004495 |
| S4 | s4_temporal_synchrony_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.526575 | 0.522319 | 0.004256 |
