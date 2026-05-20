# Q ranker decoder report

- Train rows: 450
- Test rows: 250
- Best single Q CV: 0.632094 (`baseline_q`)
- Target-wise Q CV: 0.631738
- Full CV with baseline S: 0.581440

## Top Q candidates

| name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- |
| baseline_q | baseline | 0.632094 | 0.635456 | 0.639543 | 0.621282 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b1_half_subject_50_a0.5 | blend | 0.634500 | 0.635106 | 0.643075 | 0.625319 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b1_half_subject_50_a20 | blend | 0.634551 | 0.635490 | 0.643058 | 0.625105 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b1_half_subject_50_a100 | blend | 0.634634 | 0.635900 | 0.643085 | 0.624917 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.01_b1_half_subject_50_a0.5 | blend | 0.634645 | 0.635103 | 0.643300 | 0.625532 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.01_b1_half_subject_50_a20 | blend | 0.634699 | 0.635481 | 0.643293 | 0.625323 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b1_half_a20 | blend | 0.634708 | 0.636020 | 0.642932 | 0.625170 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b1_half_a100 | blend | 0.634708 | 0.636020 | 0.642932 | 0.625170 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b1_half_a0.5 | blend | 0.634708 | 0.636020 | 0.642932 | 0.625170 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.05_b1_half_subject_50_a0.5 | blend | 0.634736 | 0.635045 | 0.643465 | 0.625697 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_subject_50_a0.5 | blend | 0.634749 | 0.634561 | 0.643366 | 0.626320 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.01_b1_half_subject_50_a100 | blend | 0.634788 | 0.635892 | 0.643331 | 0.625140 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.05_b1_half_subject_50_a20 | blend | 0.634791 | 0.635415 | 0.643471 | 0.625488 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_subject_50_a20 | blend | 0.634822 | 0.635029 | 0.643339 | 0.626099 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.01_b1_half_a100 | blend | 0.634861 | 0.636018 | 0.643176 | 0.625390 |

## Target-wise Q selection

| target | name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_baseline_w0.9_rankcal_all_rankdev_C0.05_b2_half_subject_50_a0.5 | blend | 0.635099 | 0.634388 | 0.644144 | 0.626764 |
| Q2 | baseline_q | baseline | 0.632094 | 0.635456 | 0.639543 | 0.621282 |
| Q3 | baseline_q | baseline | 0.632094 | 0.635456 | 0.639543 | 0.621282 |

## Full score with baseline S

| avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.581440 | 0.634388 | 0.639543 | 0.621282 | 0.553868 | 0.529019 | 0.498396 | 0.593582 |

## Feature set sizes

- q_core: 236
- q_core_latent: 332
- all_rankdev: 1071
- all_rankdev_latent: 1071
