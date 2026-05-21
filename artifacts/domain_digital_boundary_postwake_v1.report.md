# Digital Boundary postwake Variant

## Purpose

Pruned digital-boundary representation to test whether narrower phone/sleep timing axes are more label-readable than the full 405-feature family.

- Output: `artifacts/domain_digital_boundary_postwake_v1.parquet`
- Rows: `700`
- Feature count: `92`

## Pattern Rules

`postwake1h_phone`, `postwake2h_phone`, `postwake1h_step`, `postwake2h_step`, `first_phone_after_wake`, `first_move_after_wake`, `wake_phone`, `morning_sluggish`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
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
| z_db_morning_sluggish_score | 2.944126 | 2.791503 |
| z_db_morning_sluggish_score_past14_delta | 0.134962 | 2.751687 |
| z_db_morning_sluggish_score_past14_ratio | 64160.957330 | 542771.937750 |
| z_db_morning_sluggish_score_past28_delta | 0.188607 | 2.724470 |
| z_db_morning_sluggish_score_past28_ratio | 64160.876529 | 542771.947313 |
| z_db_morning_sluggish_score_past3_delta | 0.059046 | 3.059855 |
| z_db_morning_sluggish_score_past3_ratio | 64150.270864 | 542773.274981 |
| z_db_morning_sluggish_score_past7_delta | 0.097867 | 2.798495 |
| z_db_morning_sluggish_score_past7_ratio | 64160.865473 | 542771.948624 |
| z_db_morning_sluggish_score_subdev | 0.240203 | 2.713531 |
| z_db_morning_sluggish_score_subpct | 0.507143 | 0.288296 |
| z_db_morning_sluggish_score_subrz | 0.141310 | 1.727422 |
| z_db_postwake1h_phone_longest_run | 1.434286 | 0.805895 |
| z_db_postwake1h_phone_longest_run_subdev | -0.458571 | 0.816320 |
| z_db_postwake1h_phone_longest_run_subpct | 0.507143 | 0.243604 |
| z_db_postwake1h_phone_longest_run_subrz | -465714.278571 | 754743.840915 |
| z_db_postwake1h_phone_move_ratio | 0.397143 | 0.423883 |
| z_db_postwake1h_phone_move_ratio_subdev | 0.150000 | 0.433322 |
| z_db_postwake1h_phone_move_ratio_subpct | 0.507143 | 0.259308 |
| z_db_postwake1h_phone_move_ratio_subrz | 146428.578571 | 315868.061509 |
| z_db_postwake1h_phone_ratio | 0.722143 | 0.403324 |
| z_db_postwake1h_phone_ratio_subdev | -0.224286 | 0.409625 |
| z_db_postwake1h_phone_ratio_subpct | 0.507143 | 0.241885 |
| z_db_postwake1h_phone_ratio_subrz | -229285.704286 | 377192.486365 |