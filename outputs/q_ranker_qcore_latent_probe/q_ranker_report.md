# Q ranker decoder report

- Train rows: 450
- Test rows: 250
- Best single Q CV: 0.632094 (`baseline_q`)
- Target-wise Q CV: 0.632094
- Full CV with baseline S: 0.581592

## Top Q candidates

| name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- |
| baseline_q | baseline | 0.632094 | 0.635456 | 0.639543 | 0.621282 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_subject_50_a0.5 | blend | 0.634894 | 0.636436 | 0.642991 | 0.625255 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_subject_50_a2 | blend | 0.634899 | 0.636475 | 0.642992 | 0.625229 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_subject_50_a20 | blend | 0.634936 | 0.636764 | 0.643006 | 0.625038 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_subject_50_a50 | blend | 0.634968 | 0.636961 | 0.643030 | 0.624914 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_a2 | blend | 0.635081 | 0.637146 | 0.642994 | 0.625104 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_a0.5 | blend | 0.635081 | 0.637146 | 0.642994 | 0.625104 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_a20 | blend | 0.635081 | 0.637146 | 0.642994 | 0.625104 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b1_half_a50 | blend | 0.635081 | 0.637146 | 0.642994 | 0.625104 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.01_b1_half_subject_50_a0.5 | blend | 0.635170 | 0.637458 | 0.643636 | 0.624415 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.01_b1_half_subject_50_a2 | blend | 0.635176 | 0.637497 | 0.643642 | 0.624390 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.01_b1_half_subject_50_a20 | blend | 0.635231 | 0.637791 | 0.643692 | 0.624209 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.01_b1_half_subject_50_a50 | blend | 0.635277 | 0.637997 | 0.643737 | 0.624096 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.003_b2_half_subject_50_a0.5 | blend | 0.635414 | 0.637014 | 0.643323 | 0.625907 |
| blend_baseline_w0.9_rankcal_q_core_latent_C0.01_b1_half_a50 | blend | 0.635418 | 0.638213 | 0.643734 | 0.624307 |

## Target-wise Q selection

| target | name | kind | q_avg_log_loss | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | baseline_q | baseline | 0.632094 | 0.635456 | 0.639543 | 0.621282 |
| Q2 | baseline_q | baseline | 0.632094 | 0.635456 | 0.639543 | 0.621282 |
| Q3 | baseline_q | baseline | 0.632094 | 0.635456 | 0.639543 | 0.621282 |

## Full score with baseline S

| avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.581592 | 0.635456 | 0.639543 | 0.621282 | 0.553868 | 0.529019 | 0.498396 | 0.593582 |

## Feature set sizes

- q_core: 236
- q_core_latent: 332
- all_rankdev: 1071
- all_rankdev_latent: 1071
