# Block OOF diagnostics

- Baseline: `v13b`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prior_min3 | 0.576223 | -0.000358 | 0.000153 | 0.000153 | -0.000074 | 0.000372 | 0.000896 | -0.000406 | -0.000068 | -0.000886 | -0.000473 | False |
| prior_min4 | 0.576341 | -0.000186 | 0.000034 | -0.000131 | 0.000161 | 0.000077 | 0.000116 | -0.000287 | -0.000330 | -0.000181 | 0.000000 | False |
| v13b | 0.576376 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v13b | all | 450 | 0.576376 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | mid_third | 147 | 0.569211 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | late_third | 152 | 0.579279 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | tail_20pct | 95 | 0.581343 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prior_min4 | all | 450 | 0.576341 | 0.000034 | -0.000186 | 0.000034 | 0.000244 |
| prior_min4 | early_third | 151 | 0.580560 | -0.000131 | -0.000583 | -0.000131 | 0.000289 |
| prior_min4 | mid_third | 147 | 0.569050 | 0.000161 | -0.000145 | 0.000161 | 0.000458 |
| prior_min4 | late_third | 152 | 0.579202 | 0.000077 | -0.000287 | 0.000077 | 0.000431 |
| prior_min4 | tail_20pct | 95 | 0.581227 | 0.000116 | -0.000330 | 0.000116 | 0.000545 |
| prior_min3 | all | 450 | 0.576223 | 0.000153 | -0.000358 | 0.000153 | 0.000647 |
| prior_min3 | early_third | 151 | 0.580276 | 0.000153 | -0.000762 | 0.000153 | 0.001009 |
| prior_min3 | mid_third | 147 | 0.569285 | -0.000074 | -0.000975 | -0.000074 | 0.000819 |
| prior_min3 | late_third | 152 | 0.578907 | 0.000372 | -0.000406 | 0.000372 | 0.001171 |
| prior_min3 | tail_20pct | 95 | 0.580447 | 0.000896 | -0.000068 | 0.000896 | 0.001808 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v13b | Q1 | 0.651047 | 0.000000 |
| v13b | Q2 | 0.625465 | 0.000000 |
| v13b | Q3 | 0.559878 | 0.000000 |
| v13b | S1 | 0.549735 | 0.000000 |
| v13b | S2 | 0.553949 | 0.000000 |
| v13b | S3 | 0.525282 | 0.000000 |
| v13b | S4 | 0.589595 | 0.000000 |
| prior_min4 | Q1 | 0.651047 | 0.000000 |
| prior_min4 | Q2 | 0.625465 | 0.000000 |
| prior_min4 | Q3 | 0.559878 | 0.000000 |
| prior_min4 | S1 | 0.549735 | 0.000000 |
| prior_min4 | S2 | 0.553411 | 0.000537 |
| prior_min4 | S3 | 0.525282 | 0.000000 |
| prior_min4 | S4 | 0.589595 | 0.000000 |
| prior_min3 | Q1 | 0.651047 | 0.000000 |
| prior_min3 | Q2 | 0.625020 | 0.000445 |
| prior_min3 | Q3 | 0.559878 | 0.000000 |
| prior_min3 | S1 | 0.548552 | 0.001184 |
| prior_min3 | S2 | 0.553411 | 0.000537 |
| prior_min3 | S3 | 0.525755 | -0.000473 |
| prior_min3 | S4 | 0.588684 | 0.000911 |
