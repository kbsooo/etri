# Axis 4 — Target / label grammar extended


## A. Pairwise mutual information MI(Y_i, Y_j) (nats)

|  | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|
| Q1 | 0.6931 | 0.0075 | 0.0052 | 0.0680 | 0.0027 | 0.0071 | 0.0002 |
| Q2 | 0.0075 | 0.6854 | 0.0585 | 0.0013 | 0.0000 | 0.0014 | 0.0003 |
| Q3 | 0.0052 | 0.0585 | 0.6730 | 0.0022 | 0.0000 | 0.0004 | 0.0000 |
| S1 | 0.0680 | 0.0013 | 0.0022 | 0.6252 | 0.0715 | 0.0069 | 0.0057 |
| S2 | 0.0027 | 0.0000 | 0.0000 | 0.0715 | 0.6468 | 0.0767 | 0.1181 |
| S3 | 0.0071 | 0.0014 | 0.0004 | 0.0069 | 0.0767 | 0.6396 | 0.0037 |
| S4 | 0.0002 | 0.0003 | 0.0000 | 0.0057 | 0.1181 | 0.0037 | 0.6859 |


## B. Conditional MI given 4-bin latent state

|  | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|
| Q1 | 0.0000 | 0.0409 | 0.0392 | 0.0386 | 0.0401 | 0.0531 | 0.0319 |
| Q2 | 0.0409 | 0.0000 | 0.0571 | 0.0011 | 0.0130 | 0.0116 | 0.0098 |
| Q3 | 0.0392 | 0.0571 | 0.0000 | 0.0299 | 0.0160 | 0.0242 | 0.0102 |
| S1 | 0.0386 | 0.0011 | 0.0299 | 0.0000 | 0.0326 | 0.0214 | 0.0711 |
| S2 | 0.0401 | 0.0130 | 0.0160 | 0.0326 | 0.0000 | 0.0058 | 0.0008 |
| S3 | 0.0531 | 0.0116 | 0.0242 | 0.0214 | 0.0058 | 0.0000 | 0.0517 |
| S4 | 0.0319 | 0.0098 | 0.0102 | 0.0711 | 0.0008 | 0.0517 | 0.0000 |


## B.2. MI − CMI: how much pair association is *explained* by latent state

Large values = latent state captures the i-j relationship; pair is conditionally near-independent given state.


|  | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|
| Q1 | 0.6931 | -0.0334 | -0.0340 | 0.0294 | -0.0374 | -0.0460 | -0.0317 |
| Q2 | -0.0334 | 0.6854 | 0.0014 | 0.0002 | -0.0130 | -0.0102 | -0.0095 |
| Q3 | -0.0340 | 0.0014 | 0.6730 | -0.0277 | -0.0160 | -0.0238 | -0.0102 |
| S1 | 0.0294 | 0.0002 | -0.0277 | 0.6252 | 0.0389 | -0.0145 | -0.0654 |
| S2 | -0.0374 | -0.0130 | -0.0160 | 0.0389 | 0.6468 | 0.0709 | 0.1173 |
| S3 | -0.0460 | -0.0102 | -0.0238 | -0.0145 | 0.0709 | 0.6396 | -0.0480 |
| S4 | -0.0317 | -0.0095 | -0.0102 | -0.0654 | 0.1173 | -0.0480 | 0.6859 |


## C. Prev/next pattern × P(y=1) per target

prev/next: -1 = missing, 0 = label 0, 1 = label 1. Sample size in `n`.


next            -1      0      1
target prev                     
Q1     -1    0.588  0.273  0.581
        0    0.357  0.268  0.493
        1    0.611  0.508  0.757
Q2     -1    0.647  0.321  0.639
        0    0.485  0.233  0.585
        1    0.710  0.615  0.736
Q3     -1    0.559  0.385  0.711
        0    0.559  0.286  0.550
        1    0.767  0.587  0.759
S1     -1    0.706  0.481  0.730
        0    0.542  0.393  0.621
        1    0.700  0.648  0.811
S2     -1    0.559  0.467  0.676
        0    0.583  0.568  0.577
        1    0.700  0.610  0.762
S3     -1    0.618  0.519  0.676
        0    0.577  0.372  0.615
        1    0.816  0.591  0.792
S4     -1    0.559  0.471  0.500
        0    0.429  0.379  0.606
        1    0.722  0.552  0.663


## D. Top-5 features with largest |z-delta| on transition days, per target


### Q1

| feature | abs_z_delta |
|---|---|
| q2x_prevnight_s4x_pre_sleep_screen_sum | 0.4400 |
| q2x_day_hr_mean | 0.2910 |
| q2x_day_distance_maxh | 0.2790 |
| s4x_block_hr_max | 0.2690 |
| q2x_prevnight_s4x_block_hr_mean | 0.2690 |

### Q2

| feature | abs_z_delta |
|---|---|
| q2x_prevnight_s4x_post_wake_screen_sum | 0.4460 |
| quiet_run_start_hour | 0.2940 |
| quiet_run_end_hour | 0.2770 |
| q2x_late_hr_max | 0.2320 |
| gps_item_n | 0.2310 |

### Q3

| feature | abs_z_delta |
|---|---|
| ble_active_hours | 0.3000 |
| quiet_run_start_hour | 0.2910 |
| ble_day_hours | 0.2770 |
| quiet_run_end_hour | 0.2670 |
| ble_item_n | 0.2400 |

### S1

| feature | abs_z_delta |
|---|---|
| q2x_late_hr_std_hours | 0.4760 |
| sleep_block_fragmentation | 0.3740 |
| q2x_prevnight_s4x_pre_sleep_steps_sum | 0.3620 |
| quiet_run_end_hour | 0.3510 |
| longest_quiet_run_h | 0.3390 |

### S2

| feature | abs_z_delta |
|---|---|
| wifi_record_n | 0.3810 |
| wifi_item_n | 0.3810 |
| quiet_run_end_hour | 0.3720 |
| wifi_night_hours | 0.3510 |
| gps_item_n | 0.3280 |

### S3

| feature | abs_z_delta |
|---|---|
| q2x_prevnight_s4x_block_hr_max | 0.3680 |
| q2x_prevnight_s4x_block_hr_mean | 0.3460 |
| usage_night_hours | 0.3420 |
| longest_screenoff_run_h | 0.3070 |
| quiet_run_start_hour | 0.2880 |

### S4

| feature | abs_z_delta |
|---|---|
| quiet_run_end_hour | 0.3000 |
| quiet_run_start_hour | 0.2940 |
| q2x_prevnight_s4x_block_screen_sum | 0.2800 |
| q2x_prevnight_s4x_block_light_max | 0.2300 |
| usage_longest_missing_hours | 0.2250 |


## E. Q/S axis decomposition
- mean MI within Q-family (Q1↔Q2↔Q3): **0.0237**
- mean MI within S-family (S1↔S2↔S3↔S4): **0.0471**
- mean MI Q×S cross: **0.0070**

If within-family >> cross-family → Q and S live on separate latent axes; a single latent factor cannot model both simultaneously.
