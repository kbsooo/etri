# Conditional latent routing

- Base OOF: `0.506657`
- Routed OOF: `0.504393`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.550023 | 0.547570 | 0.002453 | 1 |
| Q2 | q2_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.559150 | 0.554687 | 0.004463 | 1 |
| Q3 | q3_temporal_state_novelty_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.526272 | 0.524266 | 0.002005 | 1 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.524266 | 0.524033 | 0.000233 | 2 |
| S1 | s1_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.497013 | 0.494487 | 0.002526 | 1 |
| S2 | s2_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.478511 | 0.478356 | 0.000155 | 1 |
| S2 | s2_temporal_state_novelty_knn_label | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.478356 | 0.478194 | 0.000162 | 2 |
| S3 | s3_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.432507 | 0.431725 | 0.000782 | 1 |
| S4 | s4_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.503123 | 0.501179 | 0.001944 | 1 |
| S4 | s4_temporal_state_novelty_hgb | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.501179 | 0.500054 | 0.001125 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.506657 | 0.550023 | 0.559150 | 0.526272 | 0.497013 | 0.478511 | 0.432507 | 0.503123 |
| conditional_latent_routing | 0.504393 | 0.547570 | 0.554687 | 0.524033 | 0.494487 | 0.478194 | 0.431725 | 0.500054 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | q2_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.559150 | 0.554687 | 0.004463 |
| Q2 | q2_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.559150 | 0.555038 | 0.004112 |
| Q2 | q2_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.559150 | 0.555583 | 0.003568 |
| Q2 | q2_temporal_state_novelty_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.559150 | 0.556083 | 0.003067 |
| Q2 | q2_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.559150 | 0.556384 | 0.002767 |
| Q2 | q2_temporal_state_novelty_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.559150 | 0.556397 | 0.002754 |
| S1 | s1_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.497013 | 0.494473 | 0.002541 |
| S1 | s1_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.497013 | 0.494487 | 0.002526 |
| Q1 | q1_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.550023 | 0.547570 | 0.002453 |
| S1 | s1_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.497013 | 0.494667 | 0.002346 |
| Q2 | q2_temporal_state_novelty_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.559150 | 0.556820 | 0.002330 |
| Q1 | q1_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.550023 | 0.547698 | 0.002325 |
| Q2 | q2_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.559150 | 0.556908 | 0.002243 |
| Q1 | q1_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.550023 | 0.547831 | 0.002192 |
| Q3 | q3_temporal_state_novelty_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.526272 | 0.524266 | 0.002005 |
| Q3 | q3_temporal_state_novelty_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.526272 | 0.524268 | 0.002003 |
| S4 | s4_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.503123 | 0.501179 | 0.001944 |
| Q2 | q2_temporal_state_novelty_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.559150 | 0.557206 | 0.001944 |
| S1 | s1_temporal_state_novelty_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.497013 | 0.495077 | 0.001936 |
| Q1 | q1_temporal_state_novelty_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.550023 | 0.548139 | 0.001884 |
