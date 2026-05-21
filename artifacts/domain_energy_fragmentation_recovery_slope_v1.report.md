# Energy Fragmentation recovery_slope Variant

## Purpose

Compact subfamily split from broad energy/fragmentation features.

- Output: `artifacts/domain_energy_fragmentation_recovery_slope_v1.parquet`
- Rows: `700`
- Feature count: `104`

## Pattern Rules

`morning`, `prev_load`, `low_morning`, `workday`, `energy_sum_past`, `energy_mean_past`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_ef_commute_morning_mean | 0.286793 | 0.362096 |
| z_ef_commute_morning_mean_subdev | 0.031906 | 0.298824 |
| z_ef_commute_morning_mean_subrz | 0.594628 | 3.747552 |
| z_ef_commute_morning_ratio | 0.195547 | 0.141212 |
| z_ef_commute_morning_ratio_subdev | 0.010552 | 0.134962 |
| z_ef_commute_morning_ratio_subrz | 0.192511 | 1.785486 |
| z_ef_commute_morning_sum | 2.294343 | 2.896766 |
| z_ef_commute_morning_sum_subdev | 0.255248 | 2.390591 |
| z_ef_commute_morning_sum_subrz | 0.594648 | 3.747675 |
| z_ef_commute_workday_mean | 0.289045 | 0.258471 |
| z_ef_commute_workday_mean_subdev | 0.043373 | 0.233805 |
| z_ef_commute_workday_mean_subrz | 0.450617 | 2.475213 |
| z_ef_commute_workday_ratio | 0.421686 | 0.192952 |
| z_ef_commute_workday_ratio_subdev | 0.005156 | 0.172854 |
| z_ef_commute_workday_ratio_subrz | 0.038175 | 1.572241 |
| z_ef_commute_workday_sum | 4.624725 | 4.135539 |
| z_ef_commute_workday_sum_subdev | 0.693971 | 3.740877 |
| z_ef_commute_workday_sum_subrz | 0.450622 | 2.475248 |
| z_ef_digital_morning_mean | 0.349034 | 0.191772 |
| z_ef_digital_morning_mean_subdev | -0.021262 | 0.165616 |
| z_ef_digital_morning_mean_subrz | -0.202637 | 1.571807 |
| z_ef_digital_morning_ratio | 0.152029 | 0.081876 |
| z_ef_digital_morning_ratio_subdev | -0.005767 | 0.074139 |
| z_ef_digital_morning_ratio_subrz | -0.147251 | 1.728752 |
| z_ef_digital_morning_sum | 2.792271 | 1.534174 |
| z_ef_digital_morning_sum_subdev | -0.170098 | 1.324925 |
| z_ef_digital_morning_sum_subrz | -0.202639 | 1.571823 |
| z_ef_digital_workday_mean | 0.522669 | 0.168897 |
| z_ef_digital_workday_mean_subdev | -0.013360 | 0.149535 |
| z_ef_digital_workday_mean_subrz | -0.140151 | 1.672295 |
| z_ef_digital_workday_ratio | 0.456871 | 0.101222 |
| z_ef_digital_workday_ratio_subdev | -0.005110 | 0.096445 |
| z_ef_digital_workday_ratio_subrz | -0.101601 | 1.795436 |
| z_ef_digital_workday_sum | 8.362710 | 2.702351 |
| z_ef_digital_workday_sum_subdev | -0.213756 | 2.392566 |
| z_ef_digital_workday_sum_subrz | -0.140153 | 1.672314 |
| z_ef_energy_mean_past14_abs_delta | 0.114618 | 0.089725 |
| z_ef_energy_mean_past14_delta | -0.007697 | 0.145421 |
| z_ef_energy_mean_past14_volatility | 0.131788 | 0.044399 |
| z_ef_energy_mean_past28_abs_delta | 0.113071 | 0.088177 |