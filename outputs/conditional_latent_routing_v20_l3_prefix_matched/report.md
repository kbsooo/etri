# Conditional latent routing

- Base OOF: `0.557955`
- Routed OOF: `0.557163`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_connectivity_context_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116.000000 | 120.000000 | 0.607223 | 0.605821 | 0.001402 | 1 |
| Q1 | q1_night_events_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100.000000 | 130.000000 | 0.605821 | 0.604281 | 0.001539 | 2 |
| Q2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| Q3 | q3_night_events_knn_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100.000000 | 130.000000 | 0.597617 | 0.597243 | 0.000374 | 1 |
| S1 | s1_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.050000 | 291.000000 | 57.000000 | 0.533467 | 0.533043 | 0.000423 | 1 |
| S1 | s1_sleep_missing_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.050000 | 291.000000 | 57.000000 | 0.533043 | 0.532737 | 0.000306 | 2 |
| S2 | s2_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.150000 | 159.000000 | 193.000000 | 0.511008 | 0.510285 | 0.000723 | 1 |
| S2 | s2_s2_broad_knn_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116.000000 | 120.000000 | 0.510285 | 0.509835 | 0.000450 | 2 |
| S3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S4 | s4_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.150000 | 159.000000 | 193.000000 | 0.565284 | 0.564959 | 0.000325 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.557955 | 0.607223 | 0.610811 | 0.597617 | 0.533467 | 0.511008 | 0.480275 | 0.565284 |
| conditional_latent_routing | 0.557163 | 0.604281 | 0.610811 | 0.597243 | 0.532737 | 0.509835 | 0.480275 | 0.564959 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_night_events_knn_resid | mid | 0.333000 | 0.666000 | 0.350000 | 100 | 130 | 0.607223 | 0.605683 | 0.001539 |
| Q1 | q1_connectivity_context_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.607223 | 0.605821 | 0.001402 |
| Q1 | q1_connectivity_context_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.607223 | 0.605825 | 0.001398 |
| Q1 | q1_connectivity_context_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.607223 | 0.605843 | 0.001380 |
| Q1 | q1_night_events_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.607223 | 0.605846 | 0.001377 |
| Q1 | q1_connectivity_context_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.607223 | 0.605868 | 0.001355 |
| Q1 | q1_connectivity_context_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.607223 | 0.605920 | 0.001303 |
| Q1 | q1_connectivity_context_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.607223 | 0.605956 | 0.001267 |
| Q1 | q1_night_events_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.607223 | 0.605997 | 0.001226 |
| Q1 | q1_connectivity_context_knn_resid | late | 0.666000 | 1.000001 | 0.350000 | 116 | 120 | 0.607223 | 0.606067 | 0.001155 |
| Q1 | q1_connectivity_context_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.607223 | 0.606068 | 0.001155 |
| Q1 | q1_connectivity_context_knn_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.607223 | 0.606154 | 0.001069 |
| Q1 | q1_night_events_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.607223 | 0.606182 | 0.001041 |
| Q1 | q1_night_events_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.607223 | 0.606201 | 0.001022 |
| Q1 | q1_night_events_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.607223 | 0.606239 | 0.000984 |
| Q1 | q1_night_events_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.607223 | 0.606256 | 0.000967 |
| Q1 | q1_connectivity_context_logreg | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.607223 | 0.606326 | 0.000897 |
| Q1 | q1_connectivity_context_logreg | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.607223 | 0.606330 | 0.000893 |
| Q1 | q1_connectivity_context_logreg | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.607223 | 0.606420 | 0.000802 |
| Q1 | q1_night_events_knn_logitresid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.607223 | 0.606430 | 0.000793 |
