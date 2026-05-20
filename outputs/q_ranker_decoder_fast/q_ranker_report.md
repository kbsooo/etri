# Q ranker decoder report

- Train rows: 450
- Test rows: 250
- Best single Q CV: 0.665787 (`baseline_q`)
- Target-wise Q CV: 0.663744
- Full CV with baseline S: 0.611738

## Top Q candidates

| name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- |
| baseline_q | baseline | 0.665787 | 0.647424 | 0.687135 | 0.662802 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0.5_half_subject_50_a2 | blend | 0.665829 | 0.649752 | 0.686764 | 0.660969 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0.5_half_subject_50_a10 | blend | 0.665858 | 0.650090 | 0.686714 | 0.660769 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0.5_half_subject_50_a50 | blend | 0.666041 | 0.650897 | 0.686728 | 0.660497 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0.5_half_a10 | blend | 0.666194 | 0.651557 | 0.685663 | 0.661362 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0.5_half_a2 | blend | 0.666194 | 0.651557 | 0.685663 | 0.661362 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0.5_half_a50 | blend | 0.666194 | 0.651557 | 0.685663 | 0.661362 |
| blend_baseline_w0.75_rankcal_q_core_C0.1_b0.5_half_subject_50_a2 | blend | 0.666316 | 0.651364 | 0.687532 | 0.660052 |
| blend_baseline_w0.75_rankcal_q_core_C0.1_b0.5_half_subject_50_a10 | blend | 0.666346 | 0.651704 | 0.687492 | 0.659843 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0.5_subject_a50 | blend | 0.666450 | 0.650496 | 0.688224 | 0.660629 |
| blend_baseline_w0.75_rankcal_q_core_C0.1_b0.5_half_subject_50_a50 | blend | 0.666530 | 0.652513 | 0.687520 | 0.659557 |
| blend_baseline_w0.75_rankcal_q_core_C0.1_b0_half_subject_50_a2 | blend | 0.666615 | 0.649476 | 0.686087 | 0.664281 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0_half_subject_50_a2 | blend | 0.666615 | 0.649476 | 0.686087 | 0.664281 |
| blend_baseline_w0.75_rankcal_q_core_C0.03_b0_half_subject_50_a10 | blend | 0.666619 | 0.649788 | 0.685993 | 0.664075 |
| blend_baseline_w0.75_rankcal_q_core_C0.1_b0_half_subject_50_a10 | blend | 0.666619 | 0.649788 | 0.685993 | 0.664075 |

## Target-wise Q selection

| target | name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | baseline_q | baseline | 0.665787 | 0.647424 | 0.687135 | 0.662802 |
| Q2 | blend_baseline_w0.75_rankcal_q_core_C0.1_b0_half_a2 | blend | 0.666852 | 0.651161 | 0.684798 | 0.664599 |
| Q3 | blend_baseline_w0.75_rankcal_q_core_C0.1_b1_subject_a50 | blend | 0.669330 | 0.656285 | 0.692696 | 0.659010 |

## Full score with baseline S

| avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.611738 | 0.647424 | 0.684798 | 0.659010 | 0.569479 | 0.557581 | 0.531625 | 0.632245 |

## Feature set sizes

- q_core: 236
- q_core_latent: 300
- all_rankdev: 1039
- all_rankdev_latent: 1039
