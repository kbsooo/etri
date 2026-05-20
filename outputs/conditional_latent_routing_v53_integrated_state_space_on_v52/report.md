# Conditional latent routing

- Base OOF: `0.502679`
- Routed OOF: `0.500979`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.544717 | 0.543645 | 0.001072 | 1 |
| Q1 | q1_temporal_state_transition_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.543645 | 0.543391 | 0.000254 | 2 |
| Q2 | q2_temporal_state_novelty_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.553268 | 0.551039 | 0.002229 | 1 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.522725 | 0.520554 | 0.002171 | 1 |
| Q3 | q3_temporal_state_novelty_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.520554 | 0.519391 | 0.001163 | 2 |
| S1 | s1_temporal_state_novelty_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.493611 | 0.492508 | 0.001103 | 1 |
| S1 | s1_temporal_state_novelty_recovery_hgb | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.492508 | 0.492404 | 0.000105 | 2 |
| S2 | s2_temporal_state_novelty_logreg | first_half | 0.000000 | 0.500000 | 0.025000 | 291 | 57 | 0.477738 | 0.477270 | 0.000469 | 1 |
| S3 | s3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.430434 | 0.429902 | 0.000532 | 1 |
| S3 | s3_temporal_state_novelty_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.429902 | 0.429792 | 0.000110 | 2 |
| S4 | s4_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.496258 | 0.493568 | 0.002690 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.502679 | 0.544717 | 0.553268 | 0.522725 | 0.493611 | 0.477738 | 0.430434 | 0.496258 |
| conditional_latent_routing | 0.500979 | 0.543391 | 0.551039 | 0.519391 | 0.492404 | 0.477270 | 0.429792 | 0.493568 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | s4_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.496258 | 0.493553 | 0.002705 |
| S4 | s4_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.496258 | 0.493568 | 0.002690 |
| S4 | s4_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.496258 | 0.493823 | 0.002434 |
| S4 | s4_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.496258 | 0.493943 | 0.002315 |
| Q2 | q2_temporal_state_novelty_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.553268 | 0.550955 | 0.002313 |
| Q2 | q2_temporal_state_novelty_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.553268 | 0.550967 | 0.002301 |
| Q2 | q2_temporal_state_novelty_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.553268 | 0.551039 | 0.002229 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.522725 | 0.520533 | 0.002193 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.522725 | 0.520554 | 0.002171 |
| Q2 | q2_temporal_state_novelty_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.553268 | 0.551146 | 0.002122 |
| Q2 | q2_temporal_state_novelty_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.553268 | 0.551303 | 0.001965 |
| S4 | s4_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.075000 | 450 | 250 | 0.496258 | 0.494298 | 0.001960 |
| S4 | s4_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.496258 | 0.494370 | 0.001888 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.522725 | 0.520845 | 0.001881 |
| S4 | s4_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.496258 | 0.494380 | 0.001878 |
| Q3 | q3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.522725 | 0.520853 | 0.001873 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.522725 | 0.520855 | 0.001870 |
| S4 | s4_temporal_state_novelty_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.496258 | 0.494391 | 0.001867 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.522725 | 0.520861 | 0.001864 |
| Q3 | q3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.522725 | 0.520890 | 0.001835 |
