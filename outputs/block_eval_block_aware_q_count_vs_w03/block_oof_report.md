# Block OOF diagnostics

- Baseline: `primary_w03`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | 0.581851 | 0.000451 | 0.001947 | 0.002950 | 0.002423 | 0.000489 | 0.001976 | -0.002139 | -0.001364 | -0.005833 | -0.000812 | True |
| qcount_w065 | 0.581881 | 0.000455 | 0.001917 | 0.002925 | 0.002382 | 0.000467 | 0.001800 | -0.002091 | -0.001435 | -0.005638 | -0.000812 | True |
| primary_w03 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_w03 | all | 450 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | early_third | 151 | 0.583964 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | mid_third | 147 | 0.574254 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | late_third | 152 | 0.592862 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | tail_20pct | 95 | 0.600527 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | all | 450 | 0.581851 | 0.001947 | 0.000451 | 0.001947 | 0.003449 |
| block_aware_qcount | early_third | 151 | 0.581015 | 0.002950 | 0.000434 | 0.002950 | 0.005479 |
| block_aware_qcount | mid_third | 147 | 0.571831 | 0.002423 | -0.000291 | 0.002423 | 0.005266 |
| block_aware_qcount | late_third | 152 | 0.592373 | 0.000489 | -0.002139 | 0.000489 | 0.003256 |
| block_aware_qcount | tail_20pct | 95 | 0.598552 | 0.001976 | -0.001364 | 0.001976 | 0.005419 |
| qcount_w065 | all | 450 | 0.581881 | 0.001917 | 0.000455 | 0.001917 | 0.003388 |
| qcount_w065 | early_third | 151 | 0.581039 | 0.002925 | 0.000464 | 0.002925 | 0.005389 |
| qcount_w065 | mid_third | 147 | 0.571873 | 0.002382 | -0.000277 | 0.002382 | 0.005141 |
| qcount_w065 | late_third | 152 | 0.592395 | 0.000467 | -0.002091 | 0.000467 | 0.003169 |
| qcount_w065 | tail_20pct | 95 | 0.598728 | 0.001800 | -0.001435 | 0.001800 | 0.005175 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| primary_w03 | Q1 | 0.654786 | 0.000000 |
| primary_w03 | Q2 | 0.645800 | 0.000000 |
| primary_w03 | Q3 | 0.607185 | 0.000000 |
| primary_w03 | S1 | 0.550398 | 0.000000 |
| primary_w03 | S2 | 0.565627 | 0.000000 |
| primary_w03 | S3 | 0.528912 | 0.000000 |
| primary_w03 | S4 | 0.597326 | 0.000000 |
| block_aware_qcount | Q1 | 0.655598 | -0.000812 |
| block_aware_qcount | Q2 | 0.642916 | 0.002884 |
| block_aware_qcount | Q3 | 0.605835 | 0.001350 |
| block_aware_qcount | S1 | 0.550398 | 0.000000 |
| block_aware_qcount | S2 | 0.565627 | 0.000000 |
| block_aware_qcount | S3 | 0.528912 | 0.000000 |
| block_aware_qcount | S4 | 0.597326 | 0.000000 |
| qcount_w065 | Q1 | 0.655598 | -0.000812 |
| qcount_w065 | Q2 | 0.642916 | 0.002884 |
| qcount_w065 | Q3 | 0.605991 | 0.001194 |
| qcount_w065 | S1 | 0.550398 | 0.000000 |
| qcount_w065 | S2 | 0.565627 | 0.000000 |
| qcount_w065 | S3 | 0.528912 | 0.000000 |
| qcount_w065 | S4 | 0.597326 | 0.000000 |
