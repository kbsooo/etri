# Sleep Fragment Recovery sleep_sensor Variant

## Purpose

Compact S-family probe view split from the broad sleep-fragment/recovery latent family.

- Output: `artifacts/domain_sleep_fragment_recovery_sleep_sensor_v1.parquet`
- Rows: `700`
- Feature count: `75`

## Pattern Rules

`sleep_ev_`, `sleep_hr_`, `sleep_screen`, `sleep_usage`, `sleep_mlight`, `sleep_wlight`, `sleep_sensor`, `sleep_late_minus`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_sfr_sleep_ev_charging_on_longest_run | 6.192857 | 6.716938 |
| z_sfr_sleep_ev_charging_on_ratio | 0.321477 | 0.332037 |
| z_sfr_sleep_ev_charging_on_starts | 0.994286 | 1.006401 |
| z_sfr_sleep_ev_charging_on_transitions | 1.551429 | 1.600764 |
| z_sfr_sleep_ev_low_coverage_longest_run | 0.084286 | 0.828694 |
| z_sfr_sleep_ev_low_coverage_ratio | 0.003034 | 0.029342 |
| z_sfr_sleep_ev_low_coverage_starts | 0.021429 | 0.154469 |
| z_sfr_sleep_ev_low_coverage_transitions | 0.042857 | 0.308938 |
| z_sfr_sleep_ev_moving_longest_run | 2.464286 | 3.587872 |
| z_sfr_sleep_ev_moving_ratio | 0.162405 | 0.212691 |
| z_sfr_sleep_ev_moving_starts | 1.067143 | 1.274738 |
| z_sfr_sleep_ev_moving_transitions | 1.855714 | 2.263231 |
| z_sfr_sleep_ev_no_wear_longest_run | 0.030000 | 0.326182 |
| z_sfr_sleep_ev_no_wear_ratio | 0.001163 | 0.013791 |
| z_sfr_sleep_ev_no_wear_starts | 0.012857 | 0.124785 |
| z_sfr_sleep_ev_no_wear_transitions | 0.025714 | 0.249569 |
| z_sfr_sleep_ev_phone_active_longest_run | 4.641429 | 4.034720 |
| z_sfr_sleep_ev_phone_active_ratio | 0.387538 | 0.250842 |
| z_sfr_sleep_ev_phone_active_starts | 2.541429 | 1.926325 |
| z_sfr_sleep_ev_phone_active_transitions | 4.428571 | 3.402731 |
| z_sfr_sleep_hr_mean_max | 60.596991 | 52.094623 |
| z_sfr_sleep_hr_mean_mean | 21.177797 | 27.842055 |
| z_sfr_sleep_hr_mean_slope | 0.026802 | 4.808447 |
| z_sfr_sleep_hr_mean_std | 18.924838 | 18.965788 |
| z_sfr_sleep_hr_mean_sum | 407.323823 | 564.940014 |
| z_sfr_sleep_hr_rmssd_max | 1.495487 | 2.551665 |
| z_sfr_sleep_hr_rmssd_mean | 0.348316 | 0.631605 |
| z_sfr_sleep_hr_rmssd_slope | 0.010163 | 0.188488 |
| z_sfr_sleep_hr_rmssd_std | 0.401360 | 0.688551 |
| z_sfr_sleep_hr_rmssd_sum | 6.764136 | 11.511205 |
| z_sfr_sleep_hr_std_max | 2.574995 | 2.673247 |
| z_sfr_sleep_hr_std_mean | 0.753624 | 1.042235 |
| z_sfr_sleep_hr_std_slope | 0.008279 | 0.210342 |
| z_sfr_sleep_hr_std_std | 0.769656 | 0.834330 |
| z_sfr_sleep_hr_std_sum | 14.816859 | 21.412415 |
| z_sfr_sleep_late_minus_early_moving | 0.063320 | 0.382522 |
| z_sfr_sleep_late_minus_early_phone | -0.017048 | 0.444674 |
| z_sfr_sleep_mlight_mean_max | 455.735098 | 1612.932676 |
| z_sfr_sleep_mlight_mean_mean | 63.245299 | 127.922132 |
| z_sfr_sleep_mlight_mean_slope | 2.538106 | 19.125676 |