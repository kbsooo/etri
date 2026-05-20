# Conditional latent routing

- Base OOF: `0.504393`
- Routed OOF: `0.502679`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.547570 | 0.545197 | 0.002373 | 1 |
| Q1 | q1_temporal_state_novelty_recovery_proto | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.545197 | 0.544717 | 0.000480 | 2 |
| Q2 | q2_temporal_state_novelty_recovery_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.554687 | 0.553268 | 0.001419 | 1 |
| Q3 | q3_temporal_state_novelty_recovery_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.524033 | 0.522725 | 0.001307 | 1 |
| S1 | s1_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.494487 | 0.493611 | 0.000876 | 1 |
| S2 | s2_temporal_state_novelty_recovery_knn_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.478194 | 0.477968 | 0.000226 | 1 |
| S2 | s2_temporal_state_novelty_recovery_logreg | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.477968 | 0.477738 | 0.000230 | 2 |
| S3 | s3_temporal_state_novelty_recovery_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.431725 | 0.430836 | 0.000890 | 1 |
| S3 | s3_temporal_state_novelty_recovery_knn_resid | first_half | 0.000000 | 0.500000 | 0.050000 | 291 | 57 | 0.430836 | 0.430434 | 0.000401 | 2 |
| S4 | s4_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.500054 | 0.496433 | 0.003621 | 1 |
| S4 | s4_temporal_state_novelty_recovery_logreg | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.496433 | 0.496258 | 0.000175 | 2 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.504393 | 0.547570 | 0.554687 | 0.524033 | 0.494487 | 0.478194 | 0.431725 | 0.500054 |
| conditional_latent_routing | 0.502679 | 0.544717 | 0.553268 | 0.522725 | 0.493611 | 0.477738 | 0.430434 | 0.496258 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | s4_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.500054 | 0.496433 | 0.003621 |
| S4 | s4_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.500054 | 0.496937 | 0.003117 |
| S4 | s4_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.500054 | 0.497550 | 0.002504 |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.547570 | 0.545197 | 0.002373 |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.547570 | 0.545420 | 0.002150 |
| S4 | s4_temporal_state_novelty_recovery_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.500054 | 0.498179 | 0.001875 |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.547570 | 0.545741 | 0.001829 |
| S4 | s4_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.500054 | 0.498274 | 0.001780 |
| Q1 | q1_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.547570 | 0.545902 | 0.001668 |
| Q1 | q1_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.547570 | 0.545906 | 0.001664 |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.547570 | 0.545940 | 0.001630 |
| S4 | s4_temporal_state_novelty_recovery_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.500054 | 0.498473 | 0.001581 |
| Q1 | q1_temporal_state_novelty_recovery_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.200000 | 159 | 193 | 0.547570 | 0.546021 | 0.001549 |
| Q1 | q1_temporal_state_novelty_recovery_knn_logitresid | late | 0.666000 | 1.000001 | 0.150000 | 116 | 120 | 0.547570 | 0.546071 | 0.001499 |
| Q1 | q1_temporal_state_novelty_recovery_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.150000 | 159 | 193 | 0.547570 | 0.546082 | 0.001488 |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | late | 0.666000 | 1.000001 | 0.200000 | 116 | 120 | 0.547570 | 0.546136 | 0.001434 |
| Q2 | q2_temporal_state_novelty_recovery_knn_resid | late | 0.666000 | 1.000001 | 0.250000 | 116 | 120 | 0.554687 | 0.553268 | 0.001419 |
| Q1 | q1_temporal_state_novelty_recovery_knn_logitresid | second_half | 0.500000 | 1.000001 | 0.250000 | 159 | 193 | 0.547570 | 0.546171 | 0.001398 |
| Q1 | q1_temporal_state_novelty_recovery_knn_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.547570 | 0.546183 | 0.001387 |
| Q3 | q3_temporal_state_novelty_recovery_knn_resid | mid | 0.333000 | 0.666000 | 0.250000 | 100 | 130 | 0.524033 | 0.522650 | 0.001383 |
