# Block OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| master_resid_min3_w05 | 0.583496 | 0.000025 | 0.000967 | 0.001095 | 0.001175 | 0.000638 | 0.001800 | -0.001087 | -0.000466 | -0.003148 | -0.003457 | True |
| master_resid_min3_w03 | 0.583798 | 0.000099 | 0.000665 | 0.000739 | 0.000792 | 0.000470 | 0.001180 | -0.000570 | -0.000190 | -0.001820 | -0.001971 | True |
| master_resid_min3_w025 | 0.583891 | 0.000099 | 0.000573 | 0.000633 | 0.000679 | 0.000410 | 0.001004 | -0.000458 | -0.000139 | -0.001502 | -0.001621 | True |
| master_resid_min3_raw | 0.583224 | -0.000636 | 0.001239 | 0.001525 | 0.001642 | 0.000564 | 0.002801 | -0.002855 | -0.001645 | -0.006882 | -0.007777 | False |
| master_resid_min4 | 0.584107 | -0.000467 | 0.000356 | 0.000163 | 0.000745 | 0.000171 | 0.000595 | -0.001137 | -0.001005 | -0.001945 | 0.000000 | False |
| temporal_label_min3_blend | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_min3_blend | all | 450 | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | early_third | 151 | 0.584703 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | mid_third | 147 | 0.575046 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | late_third | 152 | 0.593332 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | tail_20pct | 95 | 0.601707 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| master_resid_min4 | all | 450 | 0.584107 | 0.000356 | -0.000467 | 0.000356 | 0.001179 |
| master_resid_min4 | early_third | 151 | 0.584540 | 0.000163 | -0.001241 | 0.000163 | 0.001705 |
| master_resid_min4 | mid_third | 147 | 0.574301 | 0.000745 | -0.000744 | 0.000745 | 0.002276 |
| master_resid_min4 | late_third | 152 | 0.593161 | 0.000171 | -0.001137 | 0.000171 | 0.001492 |
| master_resid_min4 | tail_20pct | 95 | 0.601112 | 0.000595 | -0.001005 | 0.000595 | 0.002300 |
| master_resid_min3_raw | all | 450 | 0.583224 | 0.001239 | -0.000636 | 0.001239 | 0.003124 |
| master_resid_min3_raw | early_third | 151 | 0.583178 | 0.001525 | -0.001549 | 0.001525 | 0.004631 |
| master_resid_min3_raw | mid_third | 147 | 0.573404 | 0.001642 | -0.001696 | 0.001642 | 0.004940 |
| master_resid_min3_raw | late_third | 152 | 0.592768 | 0.000564 | -0.002855 | 0.000564 | 0.004054 |
| master_resid_min3_raw | tail_20pct | 95 | 0.598906 | 0.002801 | -0.001645 | 0.002801 | 0.007389 |
| master_resid_min3_w025 | all | 450 | 0.583891 | 0.000573 | 0.000099 | 0.000573 | 0.001055 |
| master_resid_min3_w025 | early_third | 151 | 0.584070 | 0.000633 | -0.000142 | 0.000633 | 0.001434 |
| master_resid_min3_w025 | mid_third | 147 | 0.574368 | 0.000679 | -0.000173 | 0.000679 | 0.001529 |
| master_resid_min3_w025 | late_third | 152 | 0.592922 | 0.000410 | -0.000458 | 0.000410 | 0.001308 |
| master_resid_min3_w025 | tail_20pct | 95 | 0.600703 | 0.001004 | -0.000139 | 0.001004 | 0.002198 |
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
| master_resid_min4 | Q1 | 0.654250 | 0.001177 |
| master_resid_min4 | Q2 | 0.645800 | 0.000000 |
| master_resid_min4 | Q3 | 0.611704 | 0.000000 |
| master_resid_min4 | S1 | 0.548427 | 0.000000 |
| master_resid_min4 | S2 | 0.565627 | 0.000000 |
| master_resid_min4 | S3 | 0.528912 | 0.000000 |
| master_resid_min4 | S4 | 0.597405 | 0.000021 |
| master_resid_min3_raw | Q1 | 0.654250 | 0.001177 |
| master_resid_min3_raw | Q2 | 0.645800 | 0.000000 |
| master_resid_min3_raw | Q3 | 0.601175 | 0.010529 |
| master_resid_min3_raw | S1 | 0.556205 | -0.007777 |
| master_resid_min3_raw | S2 | 0.565627 | 0.000000 |
| master_resid_min3_raw | S3 | 0.528912 | 0.000000 |
| master_resid_min3_raw | S4 | 0.597405 | 0.000021 |
| master_resid_min3_w025 | Q1 | 0.654876 | 0.000552 |
| master_resid_min3_w025 | Q2 | 0.645800 | 0.000000 |
| master_resid_min3_w025 | Q3 | 0.607854 | 0.003850 |
| master_resid_min3_w025 | S1 | 0.550048 | -0.001621 |
| master_resid_min3_w025 | S2 | 0.565627 | 0.000000 |
| master_resid_min3_w025 | S3 | 0.528912 | 0.000000 |
| master_resid_min3_w025 | S4 | 0.597337 | 0.000089 |
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
