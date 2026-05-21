# Sleep Fragment Recovery sleep_digital Variant

## Purpose

Compact S-family probe view split from the broad sleep-fragment/recovery latent family.

- Output: `artifacts/domain_sleep_fragment_recovery_sleep_digital_v1.parquet`
- Rows: `700`
- Feature count: `27`

## Pattern Rules

`sleep_screen`, `sleep_usage`, `sleep_ev_phone_active`, `wake_phone`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_sfr_sleep_ev_phone_active_longest_run | 4.641429 | 4.034720 |
| z_sfr_sleep_ev_phone_active_ratio | 0.387538 | 0.250842 |
| z_sfr_sleep_ev_phone_active_starts | 2.541429 | 1.926325 |
| z_sfr_sleep_ev_phone_active_transitions | 4.428571 | 3.402731 |
| z_sfr_sleep_screen_mean_max | 0.490357 | 0.375068 |
| z_sfr_sleep_screen_mean_mean | 0.078280 | 0.081717 |
| z_sfr_sleep_screen_mean_slope | 0.004957 | 0.035403 |
| z_sfr_sleep_screen_mean_std | 0.142239 | 0.116824 |
| z_sfr_sleep_screen_mean_sum | 1.896698 | 2.427863 |
| z_sfr_sleep_usage_total_max | 627867.185714 | 446017.597754 |
| z_sfr_sleep_usage_total_mean | 114829.232725 | 92768.300436 |
| z_sfr_sleep_usage_total_slope | -1039.474620 | 38881.063045 |
| z_sfr_sleep_usage_total_std | 180746.644795 | 123803.667356 |
| z_sfr_sleep_usage_total_sum | 2562634.653571 | 2524939.942332 |
| z_sfr_wake_phone_still_load | 315701.504802 | 222349.451839 |
| z_sfr_wake_phone_still_load_past14_abs_delta | 136848.498863 | 129410.849620 |
| z_sfr_wake_phone_still_load_past14_delta | -3632.026455 | 188383.282205 |
| z_sfr_wake_phone_still_load_past14_volatility | 175148.170590 | 62324.603372 |
| z_sfr_wake_phone_still_load_past28_abs_delta | 135570.240296 | 128484.236665 |
| z_sfr_wake_phone_still_load_past28_delta | -2780.354284 | 186831.585625 |
| z_sfr_wake_phone_still_load_past28_volatility | 177090.634988 | 57724.013763 |
| z_sfr_wake_phone_still_load_past3_abs_delta | 143119.156842 | 143627.905410 |
| z_sfr_wake_phone_still_load_past3_delta | -3933.130720 | 202795.167701 |
| z_sfr_wake_phone_still_load_past3_volatility | 142495.179705 | 101721.101606 |
| z_sfr_wake_phone_still_load_past7_abs_delta | 141670.561120 | 133993.043240 |
| z_sfr_wake_phone_still_load_past7_delta | -3597.876037 | 195039.569124 |
| z_sfr_wake_phone_still_load_past7_volatility | 168510.777228 | 73057.775624 |