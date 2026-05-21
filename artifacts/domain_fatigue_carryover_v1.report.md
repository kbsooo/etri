# Fatigue Carryover Latents

## Purpose

Encode wake-anchored recovery, late-day fatigue accumulation, sleep debt, screen fatigue, and weekend transition carry-over.

- Output: `artifacts/domain_fatigue_carryover_v1.parquet`
- Rows: `700`
- Feature count: `380`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| is_after_weekend | 1.000000 | 0.287143 | 0.452752 |
| is_monday | 1.000000 | 0.145714 | 0.353072 |
| weekday | 1.000000 | 3.001429 | 2.015320 |
| z_fc_awake_interval_min | 1.000000 | -549.607143 | 347.121531 |
| z_fc_fatigue_late_activity_max | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_activity_mean | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_activity_slope | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_activity_std | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_activity_sum | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_body_max | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_body_mean | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_body_slope | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_body_std | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_body_sum | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_coverage_max | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_coverage_mean | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_coverage_slope | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_coverage_std | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_coverage_sum | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_light_max | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_light_mean | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_light_slope | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_light_std | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_light_sum | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_phone_max | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_phone_mean | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_phone_slope | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_phone_std | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_phone_sum | 1.000000 | 0.000000 | 0.000000 |
| z_fc_fatigue_late_tok_n | 1.000000 | 0.000000 | 0.000000 |
| z_fc_late_minus_recovery_activity | 1.000000 | -0.377205 | 0.340117 |
| z_fc_late_minus_recovery_phone | 1.000000 | -0.515571 | 0.282111 |
| z_fc_longest_block_min | 1.000000 | 239.477143 | 151.184038 |
| z_fc_n_awakenings | 1.000000 | 6.045714 | 6.790397 |
| z_fc_onset_hour | 1.000000 | 15.825167 | 8.368529 |
| z_fc_postwake10h_activity_max | 1.000000 | 1.264800 | 0.934223 |