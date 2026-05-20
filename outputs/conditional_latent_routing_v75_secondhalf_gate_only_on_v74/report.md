# Conditional latent routing

- Base OOF: `0.482206`
- Routed OOF: `0.482181`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.075000 | 116.000000 | 120.000000 | 0.526613 | 0.526495 | 0.000118 | 1 |
| Q2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| Q3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S1 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S3 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116.000000 | 120.000000 | 0.412963 | 0.412907 | 0.000056 | 1 |
| S4 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.482206 | 0.526613 | 0.539167 | 0.501873 | 0.470550 | 0.453825 | 0.412963 | 0.470452 |
| conditional_latent_routing | 0.482181 | 0.526495 | 0.539167 | 0.501873 | 0.470550 | 0.453825 | 0.412907 | 0.470452 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.526613 | 0.526469 | 0.000145 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.526613 | 0.526495 | 0.000118 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.526613 | 0.526503 | 0.000110 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.526613 | 0.526524 | 0.000089 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.526613 | 0.526528 | 0.000085 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.526613 | 0.526549 | 0.000064 |
| S3 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.412963 | 0.412907 | 0.000056 |
| S3 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.412963 | 0.412917 | 0.000046 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.526613 | 0.526568 | 0.000045 |
| S3 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.412963 | 0.412923 | 0.000040 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.526613 | 0.526579 | 0.000034 |
| S3 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.412963 | 0.412929 | 0.000034 |
| S3 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.412963 | 0.412930 | 0.000033 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.015000 | 116 | 120 | 0.526613 | 0.526585 | 0.000028 |
| S3 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.412963 | 0.412937 | 0.000026 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.015000 | 116 | 120 | 0.526613 | 0.526592 | 0.000021 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.526613 | 0.526594 | 0.000019 |
| S3 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.412963 | 0.412945 | 0.000018 |
| S3 | joint_neural_context_secondhalf_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.025000 | 116 | 120 | 0.412963 | 0.412948 | 0.000014 |
| Q1 | joint_neural_context_secondhalf_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.010000 | 116 | 120 | 0.526613 | 0.526599 | 0.000014 |
