# Routine Regularity Latents

## Purpose

Encode personal routine residuals, weekday-specific routine distance, circadian phase shift, sleep regularity break, and multi-scale volatility.

- Output: `artifacts/domain_routine_regularity_v1.parquet`
- Rows: `700`
- Feature count: `252`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| z_rr_profile_corr_to_subject | 1.000000 | 0.578169 | 0.168298 |
| z_rr_profile_cosine_dist_to_subject | 1.000000 | 0.158871 | 0.086759 |
| z_rr_profile_abs_gap_to_subject | 1.000000 | 0.172264 | 0.050272 |
| z_rr_best_shift_corr_to_subject | 1.000000 | 0.573331 | 0.198573 |
| z_rr_best_shift_lag_to_subject | 1.000000 | -0.474286 | 1.968470 |
| z_rr_profile_corr_to_subject_weekday | 1.000000 | 0.650332 | 0.165782 |
| z_rr_profile_abs_gap_to_subject_weekday | 1.000000 | 0.148635 | 0.052070 |
| z_rr_weekday_gap_minus_global_gap | 1.000000 | -0.023629 | 0.030408 |
| z_rr_phone_phase_shift_from_subject | 1.000000 | 0.085343 | 2.310784 |
| z_rr_phone_phase_abs_shift_from_subject | 1.000000 | 1.531275 | 1.731722 |
| z_rr_mobility_phase_shift_from_subject | 1.000000 | 0.568294 | 3.118667 |
| z_rr_mobility_phase_abs_shift_from_subject | 1.000000 | 2.183503 | 2.296737 |
| z_rr_body_phase_shift_from_subject | 1.000000 | 0.689807 | 3.604697 |
| z_rr_body_phase_abs_shift_from_subject | 1.000000 | 2.461526 | 2.720767 |
| z_rr_coverage_phase_shift_from_subject | 1.000000 | 0.359445 | 3.046644 |
| z_rr_coverage_phase_abs_shift_from_subject | 1.000000 | 2.091897 | 2.242573 |
| z_rr_weekday_subject_dev | 1.000000 | 0.001429 | 2.015320 |
| z_rr_weekday_subject_z | 1.000000 | 0.000714 | 1.007659 |
| z_rr_phone_sum_subject_dev | 1.000000 | -0.483366 | 4.432331 |
| z_rr_phone_sum_subject_z | 1.000000 | -0.218224 | 1.768013 |
| z_rr_phone_std_subject_dev | 1.000000 | -0.002392 | 0.039907 |
| z_rr_phone_std_subject_z | 1.000000 | -0.166781 | 2.237964 |
| z_rr_phone_entropy_subject_dev | 1.000000 | -0.050109 | 0.253036 |
| z_rr_phone_entropy_subject_z | 1.000000 | -0.485330 | 2.411857 |
| z_rr_phone_phase_hour_subject_shift | 1.000000 | 0.142332 | 2.311055 |
| z_rr_phone_phase_hour_subject_abs_shift | 1.000000 | 1.529075 | 1.737770 |
| z_rr_phone_phase_strength_subject_dev | 1.000000 | 0.008642 | 0.120617 |
| z_rr_phone_phase_strength_subject_z | 1.000000 | 0.135528 | 1.836867 |
| z_rr_phone_active_start_hour_subject_shift | 1.000000 | 0.077143 | 3.859632 |
| z_rr_phone_active_start_hour_subject_abs_shift | 1.000000 | 2.691429 | 2.765604 |
| z_rr_phone_active_end_hour_subject_shift | 1.000000 | -0.346429 | 1.658740 |
| z_rr_phone_active_end_hour_subject_abs_shift | 1.000000 | 1.140714 | 1.252402 |