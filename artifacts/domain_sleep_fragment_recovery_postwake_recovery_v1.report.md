# Sleep Fragment Recovery postwake_recovery Variant

## Purpose

Compact S-family probe view split from the broad sleep-fragment/recovery latent family.

- Output: `artifacts/domain_sleep_fragment_recovery_postwake_recovery_v1.parquet`
- Rows: `700`
- Feature count: `548`

## Pattern Rules

`postwake`, `day_recovery`, `wake_activity`, `wake_phone`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_sfr_day_recovery_arousal_transition_load | 4.352857 | 3.520194 |
| z_sfr_day_recovery_ev_charging_on_longest_run | 1.781429 | 2.200130 |
| z_sfr_day_recovery_ev_charging_on_ratio | 0.156737 | 0.190761 |
| z_sfr_day_recovery_ev_charging_on_starts | 0.920000 | 0.935334 |
| z_sfr_day_recovery_ev_charging_on_transitions | 1.702857 | 1.739137 |
| z_sfr_day_recovery_ev_low_coverage_longest_run | 0.260000 | 1.377668 |
| z_sfr_day_recovery_ev_low_coverage_ratio | 0.018125 | 0.095445 |
| z_sfr_day_recovery_ev_low_coverage_starts | 0.061429 | 0.246168 |
| z_sfr_day_recovery_ev_low_coverage_transitions | 0.085714 | 0.368380 |
| z_sfr_day_recovery_ev_moving_longest_run | 6.114286 | 5.171294 |
| z_sfr_day_recovery_ev_moving_ratio | 0.523025 | 0.350975 |
| z_sfr_day_recovery_ev_moving_starts | 1.490000 | 1.276468 |
| z_sfr_day_recovery_ev_moving_transitions | 2.570000 | 2.427068 |
| z_sfr_day_recovery_ev_no_wear_longest_run | 0.067143 | 0.555689 |
| z_sfr_day_recovery_ev_no_wear_ratio | 0.005446 | 0.051014 |
| z_sfr_day_recovery_ev_no_wear_starts | 0.027143 | 0.171187 |
| z_sfr_day_recovery_ev_no_wear_transitions | 0.035714 | 0.239537 |
| z_sfr_day_recovery_ev_phone_active_longest_run | 8.957143 | 5.831040 |
| z_sfr_day_recovery_ev_phone_active_ratio | 0.718271 | 0.359677 |
| z_sfr_day_recovery_ev_phone_active_starts | 1.014286 | 1.109110 |
| z_sfr_day_recovery_ev_phone_active_transitions | 1.697143 | 2.002786 |
| z_sfr_day_recovery_hr_mean_max | 73.051427 | 47.480930 |
| z_sfr_day_recovery_hr_mean_mean | 50.932905 | 37.625613 |
| z_sfr_day_recovery_hr_mean_slope | 0.199272 | 4.683985 |
| z_sfr_day_recovery_hr_mean_std | 16.863570 | 16.619639 |
| z_sfr_day_recovery_hr_mean_sum | 792.135817 | 606.278262 |
| z_sfr_day_recovery_hr_rmssd_max | 1.894037 | 2.391402 |
| z_sfr_day_recovery_hr_rmssd_mean | 0.869639 | 0.948419 |
| z_sfr_day_recovery_hr_rmssd_slope | -0.005765 | 0.122941 |
| z_sfr_day_recovery_hr_rmssd_std | 0.458248 | 0.598967 |
| z_sfr_day_recovery_hr_rmssd_sum | 13.650837 | 15.262661 |
| z_sfr_day_recovery_hr_std_max | 3.419057 | 2.444307 |
| z_sfr_day_recovery_hr_std_mean | 2.076349 | 1.623737 |
| z_sfr_day_recovery_hr_std_slope | 0.003107 | 0.208054 |
| z_sfr_day_recovery_hr_std_std | 0.835295 | 0.723251 |
| z_sfr_day_recovery_hr_std_sum | 32.471269 | 26.158340 |
| z_sfr_day_recovery_light_burst_n | 3.121429 | 1.572601 |
| z_sfr_day_recovery_mlight_mean_max | 1502.690224 | 6402.178825 |
| z_sfr_day_recovery_mlight_mean_mean | 254.219620 | 511.237107 |
| z_sfr_day_recovery_mlight_mean_slope | 2.717967 | 91.186237 |