# Sleep Fragment Recovery postwake_digital Variant

## Purpose

Compact S-family probe view split from the broad sleep-fragment/recovery latent family.

- Output: `artifacts/domain_sleep_fragment_recovery_postwake_digital_v1.parquet`
- Rows: `700`
- Feature count: `132`

## Pattern Rules

`postwake1h_ev_phone_active`, `postwake1h_phone_still`, `postwake1h_screen`, `postwake1h_usage`, `postwake3h_ev_phone_active`, `postwake3h_phone_still`, `postwake3h_screen`, `postwake3h_usage`, `day_recovery_ev_phone_active`, `day_recovery_phone_still`, `day_recovery_screen`, `day_recovery_usage`

## Feature Coverage

| feature | mean | std |
| --- | --- | --- |
| z_sfr_day_recovery_ev_phone_active_longest_run | 8.957143 | 5.831040 |
| z_sfr_day_recovery_ev_phone_active_ratio | 0.718271 | 0.359677 |
| z_sfr_day_recovery_ev_phone_active_starts | 1.014286 | 1.109110 |
| z_sfr_day_recovery_ev_phone_active_transitions | 1.697143 | 2.002786 |
| z_sfr_day_recovery_phone_still_ratio | 0.258255 | 0.270455 |
| z_sfr_day_recovery_screen_mean_max | 0.674387 | 0.369407 |
| z_sfr_day_recovery_screen_mean_mean | 0.258191 | 0.199467 |
| z_sfr_day_recovery_screen_mean_slope | -0.002334 | 0.036180 |
| z_sfr_day_recovery_screen_mean_std | 0.215027 | 0.127746 |
| z_sfr_day_recovery_screen_mean_sum | 3.885767 | 3.064761 |
| z_sfr_day_recovery_usage_total_max | 837145.958095 | 503835.212812 |
| z_sfr_day_recovery_usage_total_mean | 316485.232106 | 203484.664868 |
| z_sfr_day_recovery_usage_total_slope | -3088.231537 | 30295.734562 |
| z_sfr_day_recovery_usage_total_std | 240476.874067 | 141447.585565 |
| z_sfr_day_recovery_usage_total_sum | 4808892.748095 | 3268279.803650 |
| z_sfr_postwake1h_ev_phone_active_longest_run | 1.434286 | 0.805895 |
| z_sfr_postwake1h_ev_phone_active_longest_run_subdev | -0.345714 | 0.640030 |
| z_sfr_postwake1h_ev_phone_active_longest_run_subpct | 0.507143 | 0.214614 |
| z_sfr_postwake1h_ev_phone_active_longest_run_subrz | -345714.285714 | 640029.888940 |
| z_sfr_postwake1h_ev_phone_active_ratio | 0.722143 | 0.403324 |
| z_sfr_postwake1h_ev_phone_active_ratio_subdev | -0.167857 | 0.318766 |
| z_sfr_postwake1h_ev_phone_active_ratio_subpct | 0.507143 | 0.211926 |
| z_sfr_postwake1h_ev_phone_active_ratio_subrz | -167857.142857 | 318766.366999 |
| z_sfr_postwake1h_ev_phone_active_starts | 0.237143 | 0.425635 |
| z_sfr_postwake1h_ev_phone_active_starts_subdev | 0.237143 | 0.425635 |
| z_sfr_postwake1h_ev_phone_active_starts_subpct | 0.507143 | 0.204571 |
| z_sfr_postwake1h_ev_phone_active_starts_subrz | 237142.857143 | 425634.737176 |
| z_sfr_postwake1h_ev_phone_active_transitions | 0.152857 | 0.360107 |
| z_sfr_postwake1h_ev_phone_active_transitions_subdev | 0.152857 | 0.360107 |
| z_sfr_postwake1h_ev_phone_active_transitions_subpct | 0.507143 | 0.176310 |
| z_sfr_postwake1h_ev_phone_active_transitions_subrz | 152857.142857 | 360107.053138 |
| z_sfr_postwake1h_phone_still_ratio | 0.325000 | 0.407920 |
| z_sfr_postwake1h_phone_still_ratio_subdev | 0.104286 | 0.396492 |
| z_sfr_postwake1h_phone_still_ratio_subpct | 0.507143 | 0.242104 |
| z_sfr_postwake1h_phone_still_ratio_subrz | 110714.272857 | 273193.493792 |
| z_sfr_postwake1h_screen_mean_max | 0.341501 | 0.334824 |
| z_sfr_postwake1h_screen_mean_max_subdev | 0.046189 | 0.302245 |
| z_sfr_postwake1h_screen_mean_max_subpct | 0.507143 | 0.270632 |
| z_sfr_postwake1h_screen_mean_max_subrz | 0.258961 | 1.401912 |
| z_sfr_postwake1h_screen_mean_mean | 0.243993 | 0.268261 |