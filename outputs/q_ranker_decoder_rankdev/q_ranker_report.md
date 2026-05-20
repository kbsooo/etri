# Q ranker decoder report

- Train rows: 450
- Test rows: 250
- Best single Q CV: 0.664448 (`blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_subject_50_a2`)
- Target-wise Q CV: 0.661768
- Full CV with baseline S: 0.610891

## Top Q candidates

| name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_subject_50_a2 | blend | 0.664448 | 0.644040 | 0.684895 | 0.664409 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_subject_50_a10 | blend | 0.664472 | 0.644396 | 0.684806 | 0.664216 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.03_b0.5_half_subject_50_a2 | blend | 0.664600 | 0.644033 | 0.685079 | 0.664689 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.03_b0.5_half_subject_50_a10 | blend | 0.664624 | 0.644385 | 0.684992 | 0.664496 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_subject_50_a50 | blend | 0.664659 | 0.645254 | 0.684772 | 0.663952 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_a50 | blend | 0.664786 | 0.645973 | 0.683650 | 0.664733 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_a2 | blend | 0.664786 | 0.645973 | 0.683650 | 0.664733 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_a10 | blend | 0.664786 | 0.645973 | 0.683650 | 0.664733 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.03_b0.5_half_subject_50_a50 | blend | 0.664812 | 0.645241 | 0.684964 | 0.664231 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.03_b0.5_half_a10 | blend | 0.664939 | 0.645964 | 0.683843 | 0.665010 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.03_b0.5_half_a50 | blend | 0.664939 | 0.645964 | 0.683843 | 0.665010 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.03_b0.5_half_a2 | blend | 0.664939 | 0.645964 | 0.683843 | 0.665010 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b1_half_subject_50_a2 | blend | 0.664954 | 0.641649 | 0.686372 | 0.666840 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b1_half_subject_50_a10 | blend | 0.665021 | 0.642079 | 0.686317 | 0.666668 |
| blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_subject_a50 | blend | 0.665070 | 0.644804 | 0.686421 | 0.663985 |

## Target-wise Q selection

| target | name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_baseline_w0.75_rankcal_all_rankdev_C0.03_b2_subject_a2 | blend | 0.669279 | 0.640188 | 0.694007 | 0.673641 |
| Q2 | blend_baseline_w0.75_rankcal_all_rankdev_C0.01_b0.5_half_a50 | blend | 0.664786 | 0.645973 | 0.683650 | 0.664733 |
| Q3 | blend_baseline_w0.75_rankcal_q_core_latent_C0.03_b0.5_half_subject_50_a50 | blend | 0.666035 | 0.650131 | 0.686511 | 0.661465 |

## Full score with baseline S

| avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.610891 | 0.640188 | 0.683650 | 0.661465 | 0.569479 | 0.557581 | 0.531625 | 0.632245 |

## Feature set sizes

- q_core: 236
- q_core_latent: 300
- all_rankdev: 1039
- all_rankdev_latent: 1039
