# Conditional latent routing

- Base OOF: `0.483657`
- Routed OOF: `0.483645`

## Selected Moves

| target | source | bin | weight | improvement | move_index | lo | hi | train_rows | sample_rows | base_log_loss | log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| Q3 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S1 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S2 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.050000 | 0.000082 | 1 | 0.333000 | 0.666000 | 100.000000 | 130.000000 | 0.414965 | 0.414884 |
| S4 | base | all | 0.000000 | 0.000000 | 0 |  |  |  |  |  |  |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.483657 | 0.527420 | 0.539802 | 0.503916 | 0.472622 | 0.455641 | 0.414965 | 0.471233 |
| conditional_latent_routing | 0.483645 | 0.527420 | 0.539802 | 0.503916 | 0.472622 | 0.455641 | 0.414884 | 0.471233 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.100000 | 100 | 130 | 0.414965 | 0.414836 | 0.000129 |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.075000 | 100 | 130 | 0.414965 | 0.414856 | 0.000110 |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.050000 | 100 | 130 | 0.414965 | 0.414884 | 0.000082 |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.025000 | 100 | 130 | 0.414965 | 0.414921 | 0.000045 |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.015000 | 100 | 130 | 0.414965 | 0.414937 | 0.000028 |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.414965 | 0.414946 | 0.000019 |
| S3 | joint_neural_context_gate_hgb_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.414965 | 0.414956 | 0.000010 |
| S3 | joint_neural_context_gate_hgb_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.414965 | 0.414984 | -0.000019 |
| S3 | joint_neural_context_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.414965 | 0.414985 | -0.000020 |
| S3 | joint_neural_context_gate_logreg_logitresid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.414965 | 0.414987 | -0.000021 |
| S3 | joint_neural_context_gate_logreg_logitresid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.414965 | 0.414990 | -0.000024 |
| S3 | joint_neural_context_gate_hgb_resid | first_half | 0.000000 | 0.500000 | 0.005000 | 291 | 57 | 0.414965 | 0.414991 | -0.000025 |
| S3 | joint_neural_context_gate_logreg_resid | mid | 0.333000 | 0.666000 | 0.005000 | 100 | 130 | 0.414965 | 0.414991 | -0.000026 |
| Q2 | joint_neural_context_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.539802 | 0.539831 | -0.000028 |
| S3 | joint_neural_context_gate_hgb_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.414965 | 0.414995 | -0.000030 |
| S1 | joint_neural_context_gate_hgb_resid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.472622 | 0.472656 | -0.000034 |
| S2 | joint_neural_context_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.005000 | 116 | 120 | 0.455641 | 0.455678 | -0.000037 |
| S3 | joint_neural_context_gate_hgb_logitresid | mid | 0.333000 | 0.666000 | 0.010000 | 100 | 130 | 0.414965 | 0.415003 | -0.000038 |
| S3 | joint_neural_context_gate_logreg_logitresid | second_half | 0.500000 | 1.000001 | 0.005000 | 159 | 193 | 0.414965 | 0.415004 | -0.000039 |
| S3 | joint_neural_context_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.414965 | 0.415005 | -0.000040 |
