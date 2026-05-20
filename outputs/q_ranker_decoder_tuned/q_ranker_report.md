# Q ranker decoder report

- Train rows: 450
- Test rows: 250
- Best single Q CV: 0.663294 (`blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a100`)
- Target-wise Q CV: 0.661051
- Full CV with baseline S: 0.610583

## Top Q candidates

| name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a100 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a2 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a1 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a50 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a20 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a5 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a10 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b2_half_a0.5 | blend | 0.663294 | 0.642747 | 0.684403 | 0.662733 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b3_half_a20 | blend | 0.663323 | 0.642409 | 0.684578 | 0.662983 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b3_half_a5 | blend | 0.663323 | 0.642409 | 0.684578 | 0.662983 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b3_half_a100 | blend | 0.663323 | 0.642409 | 0.684578 | 0.662983 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b3_half_a10 | blend | 0.663323 | 0.642409 | 0.684578 | 0.662983 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b3_half_a50 | blend | 0.663323 | 0.642409 | 0.684578 | 0.662983 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b3_half_a1 | blend | 0.663323 | 0.642409 | 0.684578 | 0.662983 |
| blend_baseline_w0.9_rankcal_all_rankdev_C0.003_b3_half_a2 | blend | 0.663323 | 0.642409 | 0.684578 | 0.662983 |

## Target-wise Q selection

| target | name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_baseline_w0.8_rankcal_all_rankdev_C0.05_b2_half_subject_75_a0.5 | blend | 0.666206 | 0.639599 | 0.689830 | 0.669191 |
| Q2 | blend_baseline_w0.6_rankcal_all_rankdev_C0.003_b0.25_half_a5 | blend | 0.667132 | 0.651187 | 0.683163 | 0.667047 |
| Q3 | blend_baseline_w0.9_rankcal_q_core_latent_C0.05_b2_half_subject_50_a50 | blend | 0.665870 | 0.649475 | 0.687745 | 0.660390 |

## Full score with baseline S

| avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.610583 | 0.639599 | 0.683163 | 0.660390 | 0.569479 | 0.557581 | 0.531625 | 0.632245 |

## Feature set sizes

- q_core: 236
- q_core_latent: 300
- all_rankdev: 1039
- all_rankdev_latent: 1039
