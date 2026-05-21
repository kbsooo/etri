# Chronotype Sleep Debt Latents

## Purpose

Build sleep-to-sleep, social-jetlag, chronotype drift, sleep debt ledger, and post-wake recovery features for S1/S3 discovery.

- Output: `artifacts/domain_chronotype_sleep_debt_v1.parquet`
- Rows: `700`
- Feature count: `183`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| z_cs_sleep_window_min | 1.000000 | 549.607143 | 347.121531 |
| z_cs_sleep_to_sleep_wake_interval_min | 1.000000 | 1717.465714 | 1627.557848 |
| z_cs_sleep_to_sleep_onset_interval_min | 1.000000 | 1719.368571 | 1528.118110 |
| z_cs_postwake3h_tok_n | 1.000000 | 4.942857 | 2.215085 |
| z_cs_postwake3h_step_sum_sum | 1.000000 | 551.691429 | 796.027801 |
| z_cs_postwake3h_step_sum_mean | 1.000000 | 92.148238 | 132.767246 |
| z_cs_postwake3h_step_sum_max | 1.000000 | 277.981429 | 412.270580 |
| z_cs_postwake3h_cal_sum_sum | 1.000000 | 22.365078 | 34.329481 |
| z_cs_postwake3h_cal_sum_mean | 1.000000 | 3.735790 | 5.723247 |
| z_cs_postwake3h_cal_sum_max | 1.000000 | 12.152544 | 21.903184 |
| z_cs_postwake3h_body_activity_sum | 1.000000 | 11.097030 | 11.380286 |
| z_cs_postwake3h_body_activity_mean | 1.000000 | 1.860624 | 1.898609 |
| z_cs_postwake3h_body_activity_max | 1.000000 | 3.357160 | 2.911016 |
| z_cs_postwake3h_phone_activity_sum | 1.000000 | 53.411291 | 30.072201 |
| z_cs_postwake3h_phone_activity_mean | 1.000000 | 9.151042 | 4.971816 |
| z_cs_postwake3h_phone_activity_max | 1.000000 | 11.390683 | 5.436040 |
| z_cs_postwake3h_mobility_activity_sum | 1.000000 | 5.043973 | 10.692864 |
| z_cs_postwake3h_mobility_activity_mean | 1.000000 | 0.845420 | 1.786905 |
| z_cs_postwake3h_mobility_activity_max | 1.000000 | 2.546002 | 5.976618 |
| z_cs_postwake3h_screen_mean_sum | 1.000000 | 1.493348 | 1.305478 |
| z_cs_postwake3h_screen_mean_mean | 1.000000 | 0.256622 | 0.225267 |
| z_cs_postwake3h_screen_mean_max | 1.000000 | 0.535367 | 0.360432 |
| z_cs_postwake3h_usage_total_sum | 1.000000 | 1849510.208095 | 1328496.197144 |
| z_cs_postwake3h_usage_total_mean | 1.000000 | 315701.212754 | 222349.338788 |
| z_cs_postwake3h_usage_total_max | 1.000000 | 654551.618095 | 435445.977131 |
| z_cs_postwake3h_ev_phone_active_sum | 1.000000 | 4.227143 | 2.274724 |
| z_cs_postwake3h_ev_phone_active_mean | 1.000000 | 0.724548 | 0.375101 |
| z_cs_postwake3h_ev_phone_active_max | 1.000000 | 0.828571 | 0.377153 |
| z_cs_postwake3h_ev_moving_sum | 1.000000 | 2.885714 | 2.324485 |
| z_cs_postwake3h_ev_moving_mean | 1.000000 | 0.484595 | 0.388413 |
| z_cs_postwake3h_ev_moving_max | 1.000000 | 0.702857 | 0.457327 |
| z_cs_postwake3h_ev_no_wear_sum | 1.000000 | 0.048571 | 0.378893 |
| z_cs_postwake3h_ev_no_wear_mean | 1.000000 | 0.009048 | 0.072409 |
| z_cs_postwake3h_ev_no_wear_max | 1.000000 | 0.020000 | 0.140100 |
| z_cs_postwake3h_sensor_coverage_n_sum | 1.000000 | 65.724286 | 33.116558 |
| z_cs_postwake3h_sensor_coverage_n_mean | 1.000000 | 11.255262 | 5.388366 |
| z_cs_postwake3h_sensor_coverage_n_max | 1.000000 | 12.415714 | 5.730728 |
| z_cs_postwake3h_phone_still_ratio | 1.000000 | 0.292048 | 0.327777 |
| z_cs_postwake6h_tok_n | 1.000000 | 9.662857 | 4.568104 |
| z_cs_postwake6h_step_sum_sum | 1.000000 | 1205.002857 | 1389.251049 |