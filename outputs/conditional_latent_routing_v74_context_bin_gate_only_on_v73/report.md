# Conditional latent routing

- Base OOF: `0.483097`
- Routed OOF: `0.483017`

## Selected Moves

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement | move_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159.000000 | 193.000000 | 0.526868 | 0.526613 | 0.000255 | 1 |
| Q2 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159.000000 | 193.000000 | 0.539350 | 0.539167 | 0.000183 | 1 |
| Q3 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S1 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S2 | base | all |  |  | 0.000000 |  |  |  |  | 0.000000 | 0 |
| S3 | joint_neural_context_bin_gate_hgb_resid | second_half | 0.500000 | 1.000001 | 0.050000 | 159.000000 | 193.000000 | 0.414280 | 0.414225 | 0.000055 | 1 |
| S4 | joint_neural_context_bin_gate_logreg_logitresid | second_half | 0.500000 | 1.000001 | 0.050000 | 159.000000 | 193.000000 | 0.470727 | 0.470664 | 0.000063 | 1 |

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.483097 | 0.526868 | 0.539350 | 0.502451 | 0.472410 | 0.455589 | 0.414280 | 0.470727 |
| conditional_latent_routing | 0.483017 | 0.526613 | 0.539167 | 0.502451 | 0.472410 | 0.455589 | 0.414225 | 0.470664 |

## Top Candidates

| target | source | bin | lo | hi | weight | train_rows | sample_rows | base_log_loss | log_loss | improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.526868 | 0.526613 | 0.000255 |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.526868 | 0.526613 | 0.000255 |
| Q2 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.539350 | 0.539122 | 0.000229 |
| Q2 | joint_neural_context_bin_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.539350 | 0.539122 | 0.000229 |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.526868 | 0.526669 | 0.000199 |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.526868 | 0.526669 | 0.000199 |
| Q1 | joint_neural_context_bin_gate_logreg_logitresid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.526868 | 0.526678 | 0.000189 |
| Q1 | joint_neural_context_bin_gate_logreg_logitresid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.526868 | 0.526678 | 0.000189 |
| Q1 | joint_neural_context_bin_gate_hgb_resid | second_half | 0.500000 | 1.000001 | 0.100000 | 159 | 193 | 0.526868 | 0.526680 | 0.000188 |
| Q1 | joint_neural_context_bin_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.100000 | 116 | 120 | 0.526868 | 0.526680 | 0.000188 |
| Q2 | joint_neural_context_bin_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.539350 | 0.539167 | 0.000183 |
| Q2 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.539350 | 0.539167 | 0.000183 |
| Q1 | joint_neural_context_bin_gate_logreg_logitresid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.526868 | 0.526689 | 0.000179 |
| Q1 | joint_neural_context_bin_gate_logreg_logitresid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.526868 | 0.526689 | 0.000179 |
| Q1 | joint_neural_context_bin_gate_hgb_resid | second_half | 0.500000 | 1.000001 | 0.075000 | 159 | 193 | 0.526868 | 0.526716 | 0.000151 |
| Q1 | joint_neural_context_bin_gate_hgb_resid | late | 0.666000 | 1.000001 | 0.075000 | 116 | 120 | 0.526868 | 0.526716 | 0.000151 |
| Q1 | joint_neural_context_bin_gate_logreg_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.526868 | 0.526724 | 0.000144 |
| Q1 | joint_neural_context_bin_gate_logreg_logitresid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.526868 | 0.526724 | 0.000144 |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | late | 0.666000 | 1.000001 | 0.050000 | 116 | 120 | 0.526868 | 0.526730 | 0.000138 |
| Q1 | joint_neural_context_bin_gate_hgb_logitresid | second_half | 0.500000 | 1.000001 | 0.050000 | 159 | 193 | 0.526868 | 0.526730 | 0.000138 |
