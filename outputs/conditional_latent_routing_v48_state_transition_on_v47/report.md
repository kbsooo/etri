# Conditional latent routing

- Base OOF: `0.511600`
- Routed OOF: `0.509456`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_state_transition_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.552061 | 0.551278 | 0.000783 | 1 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.565758 | 0.562225 | 0.003533 | 1 |
| Q3 | q3_temporal_state_transition_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.536765 | 0.533484 | 0.003281 | 1 |
| Q3 | q3_temporal_state_transition_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.533484 | 0.532111 | 0.001373 | 2 |
| S1 | s1_sleep_retrieval_meta | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.499009 | 0.498716 | 0.000293 | 1 |
| S1 | s1_temporal_state_transition_knn_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.498716 | 0.498505 | 0.000211 | 2 |
| S2 | s2_temporal_state_transition_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.481224 | 0.479303 | 0.001921 | 1 |
| S2 | s2_temporal_state_transition_logreg | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.479303 | 0.479181 | 0.000122 | 2 |
| S3 | s3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.437181 | 0.435637 | 0.001544 | 1 |
| S3 | s3_temporal_state_transition_knn_resid | first_half | 0.000000 | 0.500000 | 0.075000 | 291 | 57 | 0.435637 | 0.435259 | 0.000378 | 2 |
| S4 | s4_temporal_state_transition_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.509200 | 0.508360 | 0.000840 | 1 |
| S4 | s4_temporal_state_transition_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.508360 | 0.507634 | 0.000726 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.511600 | 0.552061 | 0.565758 | 0.536765 | 0.499009 | 0.481224 | 0.437181 | 0.509200 |
| conditional_latent_routing | 0.509456 | 0.551278 | 0.562225 | 0.532111 | 0.498505 | 0.479181 | 0.435259 | 0.507634 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.565758 | 0.562225 | 0.003533 |
| Q3 | q3_temporal_state_transition_knn_logitresid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.536765 | 0.533484 | 0.003281 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.565758 | 0.562742 | 0.003016 |
| Q3 | q3_temporal_state_transition_knn_logitresid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.536765 | 0.533972 | 0.002793 |
| Q3 | q3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.536765 | 0.534108 | 0.002657 |
| Q2 | q2_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.565758 | 0.563354 | 0.002404 |
| Q3 | q3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.536765 | 0.534403 | 0.002362 |
| Q2 | q2_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.565758 | 0.563452 | 0.002306 |
| Q3 | q3_temporal_state_transition_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.536765 | 0.534506 | 0.002259 |
| Q3 | q3_temporal_state_transition_knn_logitresid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.536765 | 0.534544 | 0.002221 |
| Q3 | q3_temporal_state_transition_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.536765 | 0.534569 | 0.002196 |
| Q3 | q3_temporal_state_transition_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.536765 | 0.534578 | 0.002187 |
| Q3 | q3_temporal_state_transition_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.536765 | 0.534606 | 0.002159 |
| Q3 | q3_temporal_state_transition_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.536765 | 0.534673 | 0.002092 |
| Q3 | q3_temporal_state_transition_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.536765 | 0.534780 | 0.001985 |
| Q3 | q3_temporal_state_transition_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.536765 | 0.534789 | 0.001976 |
| Q2 | q2_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.565758 | 0.563809 | 0.001949 |
| S2 | s2_temporal_state_transition_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.481224 | 0.479303 | 0.001921 |
| Q3 | q3_temporal_state_transition_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.536765 | 0.534919 | 0.001846 |
| Q3 | q3_temporal_state_transition_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.536765 | 0.534932 | 0.001833 |
