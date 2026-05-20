# Block OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_p025guard | 0.583456 | 0.000024 | 0.001008 | 0.001128 | 0.001245 | 0.000659 | 0.001874 | -0.001149 | -0.000464 | -0.003331 | -0.003457 | True |
| master_resid_min3_w05 | 0.583496 | 0.000025 | 0.000967 | 0.001095 | 0.001175 | 0.000638 | 0.001800 | -0.001087 | -0.000466 | -0.003148 | -0.003457 | True |
| master_resid_min3_w03 | 0.583798 | 0.000099 | 0.000665 | 0.000739 | 0.000792 | 0.000470 | 0.001180 | -0.000570 | -0.000190 | -0.001820 | -0.001971 | True |
| temporal_label_min3_blend | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_min3_blend | all | 450 | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | early_third | 151 | 0.584703 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | mid_third | 147 | 0.575046 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | late_third | 152 | 0.593332 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | tail_20pct | 95 | 0.601707 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| master_resid_min3_w03 | all | 450 | 0.583798 | 0.000665 | 0.000099 | 0.000665 | 0.001244 |
| master_resid_min3_w03 | early_third | 151 | 0.583964 | 0.000739 | -0.000190 | 0.000739 | 0.001696 |
| master_resid_min3_w03 | mid_third | 147 | 0.574254 | 0.000792 | -0.000227 | 0.000792 | 0.001812 |
| master_resid_min3_w03 | late_third | 152 | 0.592862 | 0.000470 | -0.000570 | 0.000470 | 0.001545 |
| master_resid_min3_w03 | tail_20pct | 95 | 0.600527 | 0.001180 | -0.000190 | 0.001180 | 0.002608 |
| master_resid_min3_w05 | all | 450 | 0.583496 | 0.000967 | 0.000025 | 0.000967 | 0.001924 |
| master_resid_min3_w05 | early_third | 151 | 0.583608 | 0.001095 | -0.000447 | 0.001095 | 0.002680 |
| master_resid_min3_w05 | mid_third | 147 | 0.573871 | 0.001175 | -0.000517 | 0.001175 | 0.002856 |
| master_resid_min3_w05 | late_third | 152 | 0.592694 | 0.000638 | -0.001087 | 0.000638 | 0.002414 |
| master_resid_min3_w05 | tail_20pct | 95 | 0.599907 | 0.001800 | -0.000466 | 0.001800 | 0.004161 |
| targetwise_p025guard | all | 450 | 0.583456 | 0.001008 | 0.000024 | 0.001008 | 0.002005 |
| targetwise_p025guard | early_third | 151 | 0.583576 | 0.001128 | -0.000506 | 0.001128 | 0.002806 |
| targetwise_p025guard | mid_third | 147 | 0.573801 | 0.001245 | -0.000548 | 0.001245 | 0.003023 |
| targetwise_p025guard | late_third | 152 | 0.592673 | 0.000659 | -0.001149 | 0.000659 | 0.002494 |
| targetwise_p025guard | tail_20pct | 95 | 0.599833 | 0.001874 | -0.000464 | 0.001874 | 0.004283 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| temporal_label_min3_blend | Q1 | 0.655428 | 0.000000 |
| temporal_label_min3_blend | Q2 | 0.645800 | 0.000000 |
| temporal_label_min3_blend | Q3 | 0.611704 | 0.000000 |
| temporal_label_min3_blend | S1 | 0.548427 | 0.000000 |
| temporal_label_min3_blend | S2 | 0.565627 | 0.000000 |
| temporal_label_min3_blend | S3 | 0.528912 | 0.000000 |
| temporal_label_min3_blend | S4 | 0.597426 | 0.000000 |
| master_resid_min3_w03 | Q1 | 0.654786 | 0.000641 |
| master_resid_min3_w03 | Q2 | 0.645800 | 0.000000 |
| master_resid_min3_w03 | Q3 | 0.607185 | 0.004519 |
| master_resid_min3_w03 | S1 | 0.550398 | -0.001971 |
| master_resid_min3_w03 | S2 | 0.565627 | 0.000000 |
| master_resid_min3_w03 | S3 | 0.528912 | 0.000000 |
| master_resid_min3_w03 | S4 | 0.597326 | 0.000100 |
| master_resid_min3_w05 | Q1 | 0.654498 | 0.000930 |
| master_resid_min3_w05 | Q2 | 0.645800 | 0.000000 |
| master_resid_min3_w05 | Q3 | 0.604833 | 0.006871 |
| master_resid_min3_w05 | S1 | 0.551885 | -0.003457 |
| master_resid_min3_w05 | S2 | 0.565627 | 0.000000 |
| master_resid_min3_w05 | S3 | 0.528912 | 0.000000 |
| master_resid_min3_w05 | S4 | 0.597304 | 0.000122 |
| targetwise_p025guard | Q1 | 0.654353 | 0.001074 |
| targetwise_p025guard | Q2 | 0.645800 | 0.000000 |
| targetwise_p025guard | Q3 | 0.604833 | 0.006871 |
| targetwise_p025guard | S1 | 0.551885 | -0.003457 |
| targetwise_p025guard | S2 | 0.565627 | 0.000000 |
| targetwise_p025guard | S3 | 0.528912 | 0.000000 |
| targetwise_p025guard | S4 | 0.597304 | 0.000122 |
