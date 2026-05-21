# Event Rhythm Latents

## Purpose

Encode burstiness, active-run structure, circadian phase, and cross-modal rhythm gaps from the 30-minute token grid.

- Input: `artifacts/multires_30min_event_hybrid_grid.parquet`
- Output: `artifacts/domain_event_rhythm_v1.parquet`
- Rows: `700`
- Feature count: `96`

## Feature Coverage

| feature | non_null_rate | mean | std |
| --- | --- | --- | --- |
| z_er_phone_sum | 1.000000 | 23.058690 | 4.172993 |
| z_er_phone_mean | 1.000000 | 0.480389 | 0.086937 |
| z_er_phone_std | 1.000000 | 0.385840 | 0.044711 |
| z_er_phone_max | 1.000000 | 1.246311 | 0.212446 |
| z_er_phone_active_ratio | 1.000000 | 0.293512 | 0.074466 |
| z_er_phone_run_count | 1.000000 | 6.472857 | 1.718570 |
| z_er_phone_longest_run | 1.000000 | 4.897143 | 2.630457 |
| z_er_phone_mean_run | 1.000000 | 2.408101 | 1.589474 |
| z_er_phone_burstiness | 1.000000 | -0.020469 | 0.171692 |
| z_er_phone_phase_entropy | 1.000000 | 1.224935 | 0.127856 |
| z_er_phone_phase_peak | 1.000000 | 2.075714 | 0.679758 |
| z_er_phone_phase_strength | 1.000000 | 0.320427 | 0.126856 |
| z_er_phone_phase_sin | 1.000000 | -0.206196 | 0.137318 |
| z_er_phone_phase_cos | 1.000000 | -0.165326 | 0.173514 |
| z_er_phone_phase_hour | 1.000000 | 15.373547 | 2.603482 |
| z_er_phone_night_ratio | 1.000000 | 0.099321 | 0.084074 |
| z_er_phone_morning_ratio | 1.000000 | 0.263762 | 0.096380 |
| z_er_phone_afternoon_ratio | 1.000000 | 0.341633 | 0.078811 |
| z_er_phone_evening_ratio | 1.000000 | 0.295283 | 0.091102 |
| z_er_mobility_sum | 1.000000 | 19.129657 | 4.841729 |
| z_er_mobility_mean | 1.000000 | 0.398535 | 0.100869 |
| z_er_mobility_std | 1.000000 | 0.534801 | 0.158168 |
| z_er_mobility_max | 1.000000 | 2.363309 | 0.798769 |
| z_er_mobility_active_ratio | 1.000000 | 0.262738 | 0.096426 |