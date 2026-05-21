# Digital Boundary core Variant

## Purpose

Pruned digital-boundary representation to test whether narrower phone/sleep timing axes are more label-readable than the full 405-feature family.

- Output: `artifacts/domain_digital_boundary_core_v1.parquet`
- Rows: `700`
- Feature count: `65`

## Pattern Rules

`boundary_disruption_score`, `morning_sluggish_score`, `last_phone_before_onset_min`, `first_phone_after_wake_min`, `first_move_after_wake_min`, `wake_phone_before_move_min`, `phone_before_sleep_recency`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_db_boundary_disruption_score | 0.797500 | 0.478445 |
| z_db_boundary_disruption_score_past14_delta | -0.004249 | 0.466555 |
| z_db_boundary_disruption_score_past14_ratio | 25876.420052 | 167390.513890 |
| z_db_boundary_disruption_score_past28_delta | -0.005956 | 0.463419 |
| z_db_boundary_disruption_score_past28_ratio | 25876.408353 | 167390.515701 |
| z_db_boundary_disruption_score_past3_delta | -0.007613 | 0.512098 |
| z_db_boundary_disruption_score_past3_ratio | 25876.532376 | 167390.496504 |
| z_db_boundary_disruption_score_past7_delta | -0.007595 | 0.476130 |
| z_db_boundary_disruption_score_past7_ratio | 25876.443866 | 167390.510204 |
| z_db_boundary_disruption_score_subdev | -0.019842 | 0.460973 |
| z_db_boundary_disruption_score_subpct | 0.507143 | 0.288397 |
| z_db_boundary_disruption_score_subrz | -0.076355 | 1.530877 |
| z_db_first_move_after_wake_min | 170.680000 | 328.745864 |
| z_db_first_move_after_wake_min_subdev | 137.218571 | 327.645212 |
| z_db_first_move_after_wake_min_subpct | 0.507143 | 0.287626 |
| z_db_first_move_after_wake_min_subrz | 5.818722 | 16.776895 |
| z_db_first_phone_after_wake_min | 75.318571 | 231.636876 |
| z_db_first_phone_after_wake_min_past14_delta | 8.656214 | 236.164778 |
| z_db_first_phone_after_wake_min_past14_ratio | 638574.013785 | 5345509.561815 |
| z_db_first_phone_after_wake_min_past28_delta | 8.831272 | 235.175189 |
| z_db_first_phone_after_wake_min_past28_ratio | 638573.530188 | 5345509.619664 |
| z_db_first_phone_after_wake_min_past3_delta | 7.195476 | 264.340085 |
| z_db_first_phone_after_wake_min_past3_ratio | 2095725.177612 | 38117853.446302 |
| z_db_first_phone_after_wake_min_past7_delta | 8.510561 | 246.136272 |
| z_db_first_phone_after_wake_min_past7_ratio | 638575.343654 | 5345509.402736 |
| z_db_first_phone_after_wake_min_subdev | 60.281429 | 231.854363 |
| z_db_first_phone_after_wake_min_subpct | 0.507143 | 0.287430 |
| z_db_first_phone_after_wake_min_subrz | 5.788107 | 23.356272 |
| z_db_last_phone_before_onset_min | 23.977143 | 57.763090 |
| z_db_last_phone_before_onset_min_past14_delta | -0.664988 | 59.852658 |
| z_db_last_phone_before_onset_min_past14_ratio | 920001.185620 | 7714831.457964 |
| z_db_last_phone_before_onset_min_past28_delta | -0.887307 | 58.938875 |
| z_db_last_phone_before_onset_min_past28_ratio | 920001.118810 | 7714831.465942 |
| z_db_last_phone_before_onset_min_past3_delta | -0.194286 | 65.959396 |
| z_db_last_phone_before_onset_min_past3_ratio | 920001.595178 | 7714831.409054 |
| z_db_last_phone_before_onset_min_past7_delta | -0.366939 | 61.516049 |
| z_db_last_phone_before_onset_min_past7_ratio | 920001.285941 | 7714831.445983 |
| z_db_last_phone_before_onset_min_subdev | 6.887143 | 57.812800 |
| z_db_last_phone_before_onset_min_subpct | 0.507143 | 0.288107 |
| z_db_last_phone_before_onset_min_subrz | 0.659506 | 5.844772 |