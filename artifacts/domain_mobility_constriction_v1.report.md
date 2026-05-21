# Mobility Constriction Latents

## Purpose

Encode home-stay deviation, location entropy, novelty, passive/active mobility balance, and constrained-day markers.

- Output: `artifacts/domain_mobility_constriction_v1.parquet`
- Rows: `700`
- Feature count: `213`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| weekday | 1.000000 | 3.001429 | 2.015320 |
| z_mc_active_mobility | 1.000000 | 155.122857 | 149.637604 |
| z_mc_ble_novelty_ratio_subdev | 1.000000 | 0.023756 | 0.217450 |
| z_mc_ble_novelty_ratio_subpct | 1.000000 | 0.507143 | 0.285698 |
| z_mc_ble_novelty_ratio_subrz | 1.000000 | 41144.339197 | 193288.141386 |
| z_mc_constriction_raw | 1.000000 | 0.290733 | 0.331309 |
| z_mc_day_gps_speed_max_subdev | 1.000000 | 0.385495 | 3.161159 |
| z_mc_day_gps_speed_max_subpct | 1.000000 | 0.507143 | 0.286497 |
| z_mc_day_gps_speed_max_subrz | 1.000000 | 164796.875884 | 839381.754580 |
| z_mc_day_gps_speed_mean_subdev | 1.000000 | 0.131786 | 0.680077 |
| z_mc_day_gps_speed_mean_subpct | 1.000000 | 0.507143 | 0.286497 |
| z_mc_day_gps_speed_mean_subrz | 1.000000 | 28251.726227 | 227360.925220 |
| z_mc_day_step_sum_past14_abs_delta | 1.000000 | 106.774402 | 87.541855 |
| z_mc_day_step_sum_past14_delta | 1.000000 | -11.809547 | 137.626286 |
| z_mc_day_step_sum_past14_volatility | 1.000000 | 122.225639 | 48.140235 |
| z_mc_day_step_sum_past28_abs_delta | 1.000000 | 105.292269 | 86.691203 |
| z_mc_day_step_sum_past28_delta | 1.000000 | -18.143193 | 135.233282 |
| z_mc_day_step_sum_past28_volatility | 1.000000 | 124.862833 | 46.162903 |
| z_mc_day_step_sum_past3_abs_delta | 1.000000 | 116.969357 | 99.659371 |
| z_mc_day_step_sum_past3_delta | 1.000000 | -4.204273 | 153.673982 |
| z_mc_day_step_sum_past3_volatility | 1.000000 | 108.531282 | 74.108855 |
| z_mc_day_step_sum_past7_abs_delta | 1.000000 | 107.093973 | 89.966796 |
| z_mc_day_step_sum_past7_delta | 1.000000 | -7.265286 | 139.737939 |
| z_mc_day_step_sum_past7_volatility | 1.000000 | 119.539560 | 55.059043 |
| z_mc_day_step_sum_subdev | 1.000000 | 10.086478 | 134.393017 |
| z_mc_day_step_sum_subpct | 1.000000 | 0.507143 | 0.287621 |
| z_mc_day_step_sum_subrz | 1.000000 | 0.135234 | 1.605133 |
| z_mc_elsewhere_share | 1.000000 | 0.168689 | 0.153321 |
| z_mc_evening_mobility_pressure | 1.000000 | 6.069557 | 16.983318 |
| z_mc_gps_elsewhere_ratio_subdev | 1.000000 | 0.024280 | 0.132381 |
| z_mc_gps_elsewhere_ratio_subpct | 1.000000 | 0.507143 | 0.285257 |
| z_mc_gps_elsewhere_ratio_subrz | 1.000000 | 4741.471248 | 42641.721576 |
| z_mc_gps_home_ratio_subdev | 1.000000 | 0.047198 | 0.224719 |
| z_mc_gps_home_ratio_subpct | 1.000000 | 0.507143 | 0.285710 |
| z_mc_gps_home_ratio_subrz | 1.000000 | 30666.782635 | 150484.438018 |
| z_mc_gps_stationary_min_subdev | 1.000000 | -6.531429 | 316.061046 |