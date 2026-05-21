# Digital Boundary sleep_phone Variant

## Purpose

Pruned digital-boundary representation to test whether narrower phone/sleep timing axes are more label-readable than the full 405-feature family.

- Output: `artifacts/domain_digital_boundary_sleep_phone_v1.parquet`
- Rows: `700`
- Feature count: `44`

## Pattern Rules

`sleep_phone`, `sleep_usage`, `sleep_screen`, `sleep_charging`, `sleep_lowcov`, `sleep_without_charging`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_db_sleep_charging_ratio | 0.321477 | 0.332037 |
| z_db_sleep_lowcov_or_nowear_ratio | 0.003073 | 0.029356 |
| z_db_sleep_phone_bout_count | 2.752857 | 1.848421 |
| z_db_sleep_phone_bout_count_past14_delta | 0.014280 | 1.783265 |
| z_db_sleep_phone_bout_count_past14_ratio | 61429.589572 | 397341.818283 |
| z_db_sleep_phone_bout_count_past28_delta | 0.007747 | 1.761338 |
| z_db_sleep_phone_bout_count_past28_ratio | 61429.576094 | 397341.820369 |
| z_db_sleep_phone_bout_count_past3_delta | -0.003571 | 1.954260 |
| z_db_sleep_phone_bout_count_past3_ratio | 61429.772852 | 397341.789909 |
| z_db_sleep_phone_bout_count_past7_delta | 0.010680 | 1.828999 |
| z_db_sleep_phone_bout_count_past7_ratio | 61429.626744 | 397341.812528 |
| z_db_sleep_phone_bout_count_subdev | -0.151429 | 1.728309 |
| z_db_sleep_phone_bout_count_subpct | 0.507143 | 0.283327 |
| z_db_sleep_phone_bout_count_subrz | -0.107857 | 1.420714 |
| z_db_sleep_phone_longest_run | 4.641429 | 4.034720 |
| z_db_sleep_phone_longest_run_subdev | 0.728571 | 3.961985 |
| z_db_sleep_phone_longest_run_subpct | 0.507143 | 0.286028 |
| z_db_sleep_phone_longest_run_subrz | 0.383764 | 1.769190 |
| z_db_sleep_phone_move_ratio | 0.118549 | 0.162225 |
| z_db_sleep_phone_move_ratio_subdev | 0.040899 | 0.150956 |
| z_db_sleep_phone_move_ratio_subpct | 0.507143 | 0.268959 |
| z_db_sleep_phone_move_ratio_subrz | 22339.860865 | 69799.141820 |
| z_db_sleep_phone_ratio | 0.387538 | 0.250842 |
| z_db_sleep_phone_ratio_subdev | -0.019199 | 0.234932 |
| z_db_sleep_phone_ratio_subpct | 0.507143 | 0.287648 |
| z_db_sleep_phone_ratio_subrz | -0.143345 | 1.607904 |
| z_db_sleep_phone_starts | 2.752857 | 1.848421 |
| z_db_sleep_phone_starts_subdev | -0.151429 | 1.728309 |
| z_db_sleep_phone_starts_subpct | 0.507143 | 0.283327 |
| z_db_sleep_phone_starts_subrz | -0.107857 | 1.420714 |
| z_db_sleep_phone_still_ratio | 0.268989 | 0.211846 |
| z_db_sleep_phone_still_ratio_subdev | 0.019806 | 0.207105 |
| z_db_sleep_phone_still_ratio_subpct | 0.507143 | 0.287377 |
| z_db_sleep_phone_still_ratio_subrz | 0.151087 | 1.687653 |
| z_db_sleep_phone_while_charging_ratio | 0.096767 | 0.125474 |
| z_db_sleep_phone_while_charging_ratio_subdev | 0.018321 | 0.110581 |
| z_db_sleep_phone_while_charging_ratio_subpct | 0.507143 | 0.275441 |
| z_db_sleep_phone_while_charging_ratio_subrz | 7347.387904 | 51038.429885 |
| z_db_sleep_phone_without_charging_ratio | 0.290771 | 0.240157 |
| z_db_sleep_phone_without_charging_ratio_subdev | 0.007418 | 0.222173 |