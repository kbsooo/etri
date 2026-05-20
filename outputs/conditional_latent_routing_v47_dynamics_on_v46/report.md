# Conditional latent routing

- Base OOF: `0.512673`
- Routed OOF: `0.511600`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.552688 | 0.552305 | 0.000382 | 1 |
| Q1 | q1_temporal_synchrony_logreg | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.552305 | 0.552061 | 0.000245 | 2 |
| Q2 | q2_temporal_motif_knn_logitresid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.566755 | 0.566290 | 0.000465 | 1 |
| Q2 | q2_temporal_motif_logreg | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.566290 | 0.565758 | 0.000532 | 2 |
| Q3 | q3_temporal_motif_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.538393 | 0.537153 | 0.001240 | 1 |
| Q3 | q3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.537153 | 0.536765 | 0.000388 | 2 |
| S1 | s1_temporal_motif_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.499528 | 0.499111 | 0.000418 | 1 |
| S1 | s1_temporal_synchrony_knn_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.499111 | 0.499009 | 0.000102 | 2 |
| S2 | s2_temporal_motif_knn_label | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.483456 | 0.482068 | 0.001388 | 1 |
| S2 | s2_temporal_motif_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.482068 | 0.481224 | 0.000844 | 2 |
| S3 | s3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.438515 | 0.437181 | 0.001334 | 1 |
| S4 | s4_temporal_motif_knn_resid | second_half | 0.500000 | 1.000001 | 0.025000 | 159 | 193 | 0.509373 | 0.509200 | 0.000172 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.512673 | 0.552688 | 0.566755 | 0.538393 | 0.499528 | 0.483456 | 0.438515 | 0.509373 |
| conditional_latent_routing | 0.511600 | 0.552061 | 0.565758 | 0.536765 | 0.499009 | 0.481224 | 0.437181 | 0.509200 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | s2_temporal_motif_knn_label | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.483456 | 0.482068 | 0.001388 |
| S3 | s3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.438515 | 0.437178 | 0.001338 |
| S3 | s3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.438515 | 0.437181 | 0.001334 |
| S3 | s3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.438515 | 0.437181 | 0.001334 |
| Q3 | q3_temporal_motif_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.538393 | 0.537059 | 0.001334 |
| S2 | s2_temporal_motif_knn_label | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.483456 | 0.482151 | 0.001305 |
| S3 | s3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.438515 | 0.437247 | 0.001268 |
| Q3 | q3_temporal_motif_knn_resid | mid | 0.333000 | 0.666000 | 0.200000 | 100 | 130 | 0.538393 | 0.537153 | 0.001240 |
| S2 | s2_temporal_motif_knn_label | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.483456 | 0.482240 | 0.001216 |
| S3 | s3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.438515 | 0.437318 | 0.001198 |
| S3 | s3_sleep_retrieval_meta | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.438515 | 0.437415 | 0.001100 |
| Q3 | q3_temporal_motif_knn_resid | mid | 0.333000 | 0.666000 | 0.150000 | 100 | 130 | 0.538393 | 0.537309 | 0.001084 |
| S2 | s2_temporal_motif_knn_label | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.483456 | 0.482430 | 0.001026 |
| S2 | s2_temporal_motif_knn_label | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.483456 | 0.482472 | 0.000984 |
| S3 | s3_sleep_retrieval_meta | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.438515 | 0.437587 | 0.000929 |
| S2 | s2_temporal_motif_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.483456 | 0.482568 | 0.000887 |
| S2 | s2_temporal_motif_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.483456 | 0.482570 | 0.000886 |
| Q3 | q3_temporal_motif_knn_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.538393 | 0.537546 | 0.000846 |
| S2 | s2_temporal_motif_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.483456 | 0.482610 | 0.000846 |
| S2 | s2_temporal_motif_knn_resid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.483456 | 0.482612 | 0.000844 |
