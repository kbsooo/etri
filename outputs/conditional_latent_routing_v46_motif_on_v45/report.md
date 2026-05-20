# Conditional latent routing

- Base OOF: `0.514658`
- Routed OOF: `0.512673`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | q2_temporal_motif_knn_resid | all | 0.250000 | 0.004094 | 1 | 0.000000 | 1.000001 | 450.000000 | 250.000000 | 0.570849 | 0.566755 |
| Q3 | q3_sleep_retrieval_meta | first_half | 0.250000 | 0.002710 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.541882 | 0.539172 |
| Q3 | q3_temporal_motif_knn_resid | second_half | 0.150000 | 0.000780 | 2 | 0.500000 | 1.000001 | 159.000000 | 193.000000 | 0.539172 | 0.538393 |
| S1 | s1_temporal_motif_knn_resid | all | 0.050000 | 0.000927 | 1 | 0.000000 | 1.000001 | 450.000000 | 250.000000 | 0.500456 | 0.499528 |
| S2 | s2_temporal_motif_knn_resid | second_half | 0.250000 | 0.003020 | 1 | 0.500000 | 1.000001 | 159.000000 | 193.000000 | 0.486476 | 0.483456 |
| S3 | s3_temporal_motif_logreg | first_half | 0.050000 | 0.001180 | 1 | 0.000000 | 0.500000 | 291.000000 | 57.000000 | 0.440488 | 0.439308 |
| S3 | s3_temporal_motif_knn_logitresid | late | 0.150000 | 0.000792 | 2 | 0.666000 | 1.000001 | 116.000000 | 120.000000 | 0.439308 | 0.438515 |
| S4 | s4_temporal_motif_knn_resid | second_half | 0.050000 | 0.000395 | 1 | 0.500000 | 1.000001 | 159.000000 | 193.000000 | 0.509768 | 0.509373 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.514658 | 0.552688 | 0.570849 | 0.541882 | 0.500456 | 0.486476 | 0.440488 | 0.509768 |
| conditional_latent_routing | 0.512673 | 0.552688 | 0.566755 | 0.538393 | 0.499528 | 0.483456 | 0.438515 | 0.509373 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | q2_temporal_motif_knn_resid | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.570849 | 0.566755 | 0.004094 |
| Q2 | q2_temporal_motif_knn_resid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.570849 | 0.567020 | 0.003829 |
| Q2 | q2_temporal_motif_knn_resid | all | 0.000000 | 1.000001 | 0.200000 | 450 | 250 | 0.570849 | 0.567068 | 0.003781 |
| Q2 | q2_temporal_motif_knn_resid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.570849 | 0.567510 | 0.003339 |
| Q2 | q2_temporal_motif_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.570849 | 0.567525 | 0.003324 |
| Q2 | q2_temporal_motif_knn_resid | all | 0.000000 | 1.000001 | 0.150000 | 450 | 250 | 0.570849 | 0.567596 | 0.003253 |
| Q2 | q2_temporal_motif_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.570849 | 0.567656 | 0.003193 |
| Q2 | q2_temporal_motif_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.570849 | 0.567773 | 0.003076 |
| S2 | s2_temporal_motif_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.486476 | 0.483456 | 0.003020 |
| Q2 | q2_temporal_motif_knn_resid | first_half | 0.000000 | 0.500000 | 0.150000 | 291 | 57 | 0.570849 | 0.568121 | 0.002728 |
| S2 | s2_temporal_motif_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.486476 | 0.483757 | 0.002718 |
| Q3 | q3_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.250000 | 291 | 57 | 0.541882 | 0.539172 | 0.002710 |
| S2 | s2_temporal_motif_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.486476 | 0.483804 | 0.002671 |
| Q2 | q2_temporal_motif_knn_resid | all | 0.000000 | 1.000001 | 0.100000 | 450 | 250 | 0.570849 | 0.568370 | 0.002479 |
| Q2 | q2_temporal_motif_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.100000 | 291 | 57 | 0.570849 | 0.568407 | 0.002442 |
| S2 | s2_temporal_motif_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.486476 | 0.484063 | 0.002412 |
| Q3 | q3_sleep_retrieval_meta | first_half | 0.000000 | 0.500000 | 0.200000 | 291 | 57 | 0.541882 | 0.539506 | 0.002377 |
| S2 | s2_temporal_motif_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.486476 | 0.484175 | 0.002300 |
| Q3 | q3_sleep_retrieval_meta | all | 0.000000 | 1.000001 | 0.250000 | 450 | 250 | 0.541882 | 0.539807 | 0.002075 |
| S2 | s2_temporal_motif_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.486476 | 0.484427 | 0.002049 |
