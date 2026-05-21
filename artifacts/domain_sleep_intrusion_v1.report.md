# Sleep Intrusion Latents

## Purpose

Build sleep-window, prebed, postwake, phone-intrusion, no-wear, low-coverage, and sleep-debt features.

- Output: `artifacts/domain_sleep_intrusion_v1.parquet`
- Rows: `700`
- Feature count: `251`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| z_si_tst_min | 1.000000 | 460.562857 | 278.077665 |
| z_si_sleep_eff | 1.000000 | 0.777984 | 0.299390 |
| z_si_sol_proxy_min | 1.000000 | 52.641429 | 127.688031 |
| z_si_n_awakenings | 1.000000 | 6.045714 | 6.790397 |
| z_si_onset_hour | 0.890000 | 17.781086 | 6.623261 |
| z_si_wake_hour | 0.890000 | 11.392777 | 5.396033 |
| z_si_sleep_window_min | 0.890000 | 617.536116 | 305.603833 |
| z_si_sleep_midpoint_hour | 0.890000 | 6.974398 | 7.212146 |
| z_si_prebed2h_tok_n | 0.890000 | 4.000000 | 0.000000 |
| z_si_prebed2h_ev_phone_active_sum | 0.890000 | 3.537721 | 0.855156 |
| z_si_prebed2h_ev_phone_active_mean | 0.890000 | 0.884430 | 0.213789 |
| z_si_prebed2h_ev_phone_active_max | 0.890000 | 0.985554 | 0.119417 |
| z_si_prebed2h_ev_moving_sum | 0.890000 | 1.738363 | 1.555177 |
| z_si_prebed2h_ev_moving_mean | 0.890000 | 0.434591 | 0.388794 |
| z_si_prebed2h_ev_moving_max | 0.890000 | 0.654896 | 0.475784 |
| z_si_prebed2h_ev_no_wear_sum | 0.890000 | 0.006421 | 0.126633 |
| z_si_prebed2h_ev_no_wear_mean | 0.890000 | 0.001605 | 0.031658 |
| z_si_prebed2h_ev_no_wear_max | 0.890000 | 0.003210 | 0.056614 |
| z_si_prebed2h_ev_low_coverage_sum | 0.890000 | 0.009631 | 0.138563 |
| z_si_prebed2h_ev_low_coverage_mean | 0.890000 | 0.002408 | 0.034641 |
| z_si_prebed2h_ev_low_coverage_max | 0.890000 | 0.006421 | 0.079935 |
| z_si_prebed2h_ev_charging_on_sum | 0.890000 | 0.918138 | 1.152953 |
| z_si_prebed2h_ev_charging_on_mean | 0.890000 | 0.229535 | 0.288238 |
| z_si_prebed2h_ev_charging_on_max | 0.890000 | 0.495987 | 0.500386 |
| z_si_prebed2h_screen_mean_sum | 0.890000 | 1.330630 | 0.950807 |
| z_si_prebed2h_screen_mean_mean | 0.890000 | 0.333110 | 0.237354 |
| z_si_prebed2h_screen_mean_max | 0.890000 | 0.608670 | 0.319507 |
| z_si_prebed2h_usage_total_sum | 0.890000 | 1512240.637239 | 829825.255382 |
| z_si_prebed2h_usage_total_mean | 0.890000 | 427046.184658 | 213251.181009 |
| z_si_prebed2h_usage_total_max | 0.890000 | 700433.669074 | 344319.784376 |