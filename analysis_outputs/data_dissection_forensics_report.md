# Data Dissection Forensics

## Dataset Health Check

- Train rows: 450, submission rows: 250, subjects: 10.
- Train date range: 2024-06-03 to 2024-11-14.
- Submission date range: 2024-07-06 to 2024-11-19.
- Timeline blocks: train=36, submission=36.
- Submission block length median=5.5, max=16; both-boundary fraction=0.722.
- Several subjects have a visible mask pattern rather than a plain future split. For example `id01/id02/id03/id09/id10` start with an approximate `2x train -> 1x hidden -> 1x train -> 1x hidden` pattern, while `id04/id05/id06/id08` are much more fragmented.

## Target/Supervision Quality Review

```
target  global_rate  subject_rate_std  train_block_rate_std  transition_rate_within_subject
    Q1     0.495556          0.175438              0.344099                        0.380797
    Q2     0.562222          0.146900              0.320770                        0.345471
    Q3     0.600000          0.123898              0.319807                        0.351344
    S1     0.682222          0.180240              0.338912                        0.355070
    S2     0.651111          0.218593              0.345230                        0.385376
    S3     0.662222          0.247490              0.359997                        0.354712
    S4     0.560000          0.194749              0.362993                        0.411966
```

Strong subject-level rate differences are real, but within-subject temporal copy is weak. This means the hidden block problem is closer to block-level count/rate inference than sequence smoothing.

Top target pair constraints:

```
 a  b     corr  p_b_given_a1  p_b_given_a0  both1_rate  xor_rate
S2 S4 0.478282      0.733788      0.235669    0.477778  0.255556
S2 S3 0.394023      0.798635      0.407643    0.520000  0.273333
S1 S2 0.381608      0.775244      0.384615    0.528889  0.275556
Q1 S1 0.361444      0.852018      0.515419    0.422222  0.333333
Q2 Q3 0.340129      0.747036      0.411168    0.420000  0.322222
Q1 Q2 0.122060      0.623318      0.502203    0.308889  0.440000
S1 S3 0.118045      0.700326      0.580420    0.477778  0.388889
S1 S4 0.106533      0.596091      0.482517    0.406667  0.428889
Q1 Q3 0.101612      0.650224      0.550661    0.322222  0.451111
S3 S4 0.086327      0.590604      0.500000    0.391111  0.440000
```

## Boundary Leakage Check

Simple boundary copying is actively bad under submission-like geometry:

```
       method  full_oof_loss  full_delta_vs_stage2  loss_Q1  loss_Q2  loss_Q3  loss_S1  loss_S2  loss_S3  loss_S4
subject_prior       0.612828              0.045297 0.647848 0.671781 0.663115 0.563019 0.578438 0.528417 0.637176
         both       0.685083              0.117552 0.729049 0.706518 0.752291 0.650412 0.640304 0.606068 0.710942
same_boundary       0.685083              0.117552 0.729049 0.706518 0.752291 0.650412 0.640304 0.606068 0.710942
         prev       0.688870              0.121339 0.736631 0.674783 0.765462 0.666565 0.660808 0.591251 0.726589
         next       0.713453              0.145922 0.744874 0.800385 0.790960 0.635203 0.655141 0.634662 0.732944
```

This kills the tempting hypothesis that bracket labels directly reveal hidden labels. The useful oracle is block-rate/count, not row-wise boundary propagation.

## Rank/Threshold Rule Check

I also scanned the top residual/label/shift features as direct subject-relative threshold rules under geometry CV. No single stump beat stage2:

```
target  best_delta_vs_stage2
Q1                  +0.052700
Q2                  +0.031513
Q3                  +0.017351
S1                  +0.063905
S2                  +0.072014
S3                  +0.101991
S4                  +0.059843
```

This does not mean these features are useless; it means the label is not a simple one-feature threshold. These signals should be used as weak latent count/rate priors or interaction features, not as direct row-level replacements.

## Lag/Periodicity Check

Best label-copy lags by target:

```
target  lag  copy_accuracy     corr   n
    Q1    1       0.618182 0.236578 440
    Q1    7       0.578947 0.158385 380
    Q1    3       0.566667 0.133568 420
    Q2    1       0.656818 0.303538 440
    Q2    2       0.623256 0.234465 430
    Q2    5       0.605000 0.198225 400
    Q3    1       0.652273 0.276312 440
    Q3    5       0.590000 0.142653 400
    Q3   15       0.583333 0.134741 300
    S1    7       0.660526 0.212661 380
    S1    6       0.653846 0.196653 390
    S1    1       0.652273 0.197105 440
    S2   13       0.665625 0.251264 320
    S2    8       0.664865 0.245310 370
    S2   14       0.664516 0.248122 310
    S3    6       0.684615 0.294499 390
    S3   13       0.684375 0.293795 320
    S3    8       0.683784 0.292110 370
    S4    7       0.605263 0.199090 380
    S4    6       0.605128 0.197091 390
    S4   14       0.600000 0.185850 310
```

## Feature/Measurement Clues

Top residual-correlated features after subject-centering:

```
                        feature_file                                         feature signal_type best_target  best_corr  abs_corr  train_mean  train_std  sub_mean  sub_train_z_shift  missing_delta_sub_minus_train
measurement_process_features.parquet      mp_wlight_core5h_positive_frac_next1_delta    residual          S1   0.202580  0.202580   -0.008143   0.220852  0.009263           0.078812                      -0.058222
     rhythm_regular_features.parquet    rr_hr_pre6h_hr_points_count_same_weekend_dev    residual          Q3  -0.198196  0.198196   20.384444  98.382792 14.480000          -0.060015                       0.000000
measurement_process_features.parquet       mp_hr_pre6h_minute_count_same_weekend_dev    residual          Q3  -0.198048  0.198048   20.250000  98.440797 14.306000          -0.060381                       0.000000
measurement_process_features.parquet          mp_hr_pre6h_row_count_same_weekend_dev    residual          Q3  -0.198048  0.198048   20.250000  98.440797 14.306000          -0.060381                       0.000000
measurement_process_features.parquet           mp_hr_pre6h_obs_frac_same_weekend_dev    residual          Q3  -0.198048  0.198048    0.056250   0.273447  0.039739          -0.060381                       0.000000
measurement_process_features.parquet    mp_watch_pre6h_obs_frac_min_same_weekend_dev    residual          Q3  -0.194848  0.194848    0.048404   0.261638  0.033150          -0.058303                       0.000000
     rhythm_regular_features.parquet     rr_mlight_core5h_m_light_min_zdev_subj_mean    residual          S1  -0.194031  0.194031   -0.075466   0.681823 -0.033682           0.061282                       0.048444
measurement_process_features.parquet  mp_usage_day12_18_gap60_count_same_weekend_dev    residual          Q2  -0.193536  0.193536    0.161111   0.656591  0.222000           0.092735                       0.000000
measurement_process_features.parquet           mp_hr_pre3h_span_min_same_weekend_dev    residual          Q3  -0.191180  0.191180   25.527778  61.827917 25.426000          -0.001646                       0.000000
measurement_process_features.parquet    mp_hr_all24h_median_gap_min_same_weekend_dev    residual          S4  -0.190979  0.190979   90.624444 348.630760 45.146000          -0.130449                       0.000000
measurement_process_features.parquet                     mp_hr_all24h_median_gap_min    residual          S4  -0.190979  0.190979   90.624444 348.630760 45.146000          -0.130449                       0.000000
measurement_process_features.parquet        mp_hr_all24h_median_gap_min_dev_subj_med    residual          S4  -0.190979  0.190979   90.624444 348.630760 45.146000          -0.130449                       0.000000
measurement_process_features.parquet       mp_hr_all24h_p90_gap_min_same_weekend_dev    residual          S4  -0.189908  0.189908   91.631111 348.884598 54.650000          -0.105998                       0.000000
measurement_process_features.parquet           mp_hr_all24h_p90_gap_min_dev_subj_med    residual          S4  -0.189612  0.189612   92.108889 349.416172 54.990000          -0.106231                       0.000000
measurement_process_features.parquet                        mp_hr_all24h_p90_gap_min    residual          S4  -0.189612  0.189612   92.291111 349.386610 55.206000          -0.106143                       0.000000
measurement_process_features.parquet    mp_hr_pre3_to_core_obs_drop_same_weekend_dev    residual          Q3  -0.189281  0.189281    0.105244   0.295925  0.098085          -0.024191                       0.000000
measurement_process_features.parquet mp_usage_day12_18_minute_count_same_weekend_dev    residual          Q2   0.188140  0.188140   -0.731111   5.987917 -0.348000           0.063981                       0.000000
measurement_process_features.parquet    mp_usage_day12_18_row_count_same_weekend_dev    residual          Q2   0.188140  0.188140   -0.731111   5.987917 -0.348000           0.063981                       0.000000
measurement_process_features.parquet     mp_usage_day12_18_obs_frac_same_weekend_dev    residual          Q2   0.188140  0.188140   -0.002031   0.016633 -0.000967           0.063981                       0.000000
measurement_process_features.parquet mp_usage_core5h_median_gap_min_same_weekend_dev    residual          Q1   0.186721  0.186721  -14.177222 128.260619 -2.293000           0.092657                       0.000000
```

Largest train/sub feature shifts:

```
                              feature_file                                               feature signal_type best_target  best_corr  abs_corr  train_mean   train_std    sub_mean  sub_train_z_shift  missing_delta_sub_minus_train  abs_shift
presleep_temporal_context_features.parquet              presleep_wlight_post2h_w_light_max_prev1       label          Q3   0.069185  0.069185   26.460000   73.722917  287.780000           3.544624                      -0.096000   3.544624
       pre_sleep_relative_features.parquet                    presleep_wlight_post2h_w_light_max       label          Q3  -0.104569  0.104569   26.782222   74.419845  288.624000           3.518440                      -0.103111   3.518440
presleep_temporal_context_features.parquet              presleep_wlight_post2h_w_light_max_next1       label          Q2  -0.076268  0.076268   27.600000   74.656302  287.088000           3.475768                      -0.012889   3.475768
presleep_temporal_context_features.parquet     presleep_wlight_post2h_w_light_max_neighbor_slope       label          Q3  -0.070667  0.070667    0.951111   91.631086  266.292000           2.895752                      -0.054222   2.895752
presleep_temporal_context_features.parquet       presleep_wlight_post2h_w_light_max_neighbor_dev       label          Q3  -0.110208  0.110208    0.791111   78.012175 -133.722000          -1.724258                      -0.104889   1.724258
presleep_temporal_context_features.parquet              presleep_wlight_post2h_w_light_std_prev1       label          S4   0.097140  0.097140    6.593257   19.894182   38.082908           1.582857                      -0.096000   1.582857
presleep_temporal_context_features.parquet           presleep_wlight_post2h_w_light_max_past2dev       label          Q3  -0.116919  0.116919    2.963333   81.556225  130.718000           1.566461                      -0.111111   1.566461
       pre_sleep_relative_features.parquet                    presleep_wlight_post2h_w_light_std       label          Q3  -0.111061  0.111061    6.738647   20.126118   37.928174           1.549704                      -0.103111   1.549704
presleep_temporal_context_features.parquet              presleep_wlight_post2h_w_light_std_next1       label          Q2  -0.041467  0.041467    7.086138   20.404011   37.285826           1.480086                      -0.012889   1.480086
presleep_temporal_context_features.parquet     presleep_wlight_post2h_w_light_std_neighbor_slope       label          S1   0.083776  0.083776    0.333257   24.642637   32.550939           1.307396                      -0.054222   1.307396
           rhythm_regular_features.parquet                                      rr_subject_phase       label          Q2   0.079232  0.079232    0.387703    0.272027    0.702135           1.155885                       0.000000   1.155885
           rhythm_regular_features.parquet                                  rr_subject_day_index       label          Q2   0.084160  0.084160   27.402222   19.760943   49.116000           1.098823                       0.000000   1.098823
presleep_temporal_context_features.parquet       presleep_wlight_post2h_w_light_std_neighbor_dev       label          Q3  -0.095455  0.095455    0.174310   22.235853  -16.362651          -0.743707                      -0.104889   0.743707
presleep_temporal_context_features.parquet           presleep_wlight_post2h_w_light_std_past2dev       label          Q3  -0.111827  0.111827    0.688376   22.695343   15.931445           0.671639                      -0.111111   0.671639
      measurement_process_features.parquet     mp_watch_to_phone_day12_18_obs_ratio_dev_subj_med       label          S4   0.077922  0.077922   -0.094305    0.387430    0.129213           0.576924                      -0.002667   0.576924
      measurement_process_features.parquet                  mp_watch_to_phone_day12_18_obs_ratio       label          S4   0.080417  0.080417    0.793962    0.415349    1.032065           0.573261                      -0.002667   0.573261
      measurement_process_features.parquet mp_watch_to_phone_day12_18_obs_ratio_same_weekend_dev       label          S2   0.071917  0.071917   -0.065447    0.382435    0.140048           0.537332                      -0.002667   0.537332
      measurement_process_features.parquet                      mp_wlight_day12_18_positive_frac       label          Q1  -0.087160  0.087160    0.899087    0.124928    0.836651          -0.499780                      -0.079111   0.499780
presleep_temporal_context_features.parquet              presleep_wlight_core5h_w_light_max_prev1       label          Q1  -0.096136  0.096136  330.053333 2088.657413 1371.608000           0.498672                      -0.095111   0.498672
      measurement_process_features.parquet     mp_wlight_day12_18_positive_frac_same_weekend_dev       label          Q1  -0.077977  0.077977   -0.023221    0.114818   -0.080064          -0.495069                      -0.079111   0.495069
```

## Top Insights

1. Submission rows are hidden blocks inside each subject timeline, but nearest visible labels are not reliable. Any 0.54 route needs hidden block count/rate recovery, not boundary smoothing.
2. Q2 has the largest block-rate oracle gap, followed by Q1/Q3. The subjective Q targets are still the highest-upside place to search for subject-rank/count rules.
3. The strongest residual signals are measurement-process/rhythm deviations, especially pre-sleep HR observation density, usage counts, light gaps, and sensor active counts. Missingness is behavior.
4. S2/S3 carry the cleanest JEPA block-rate signal, but public feedback shows aggressive latent residual moves are unsafe unless anchored to a public-positive raw-timeline direction.
5. There is no evidence that a bigger model alone solves the gap. The data bottleneck is an undiscovered labeling/threshold/count rule.

## Immediate Experiments

1. Subject-rank threshold miner: for each target, mine monotonic subject-relative thresholds over the top residual features, then solve hidden block counts with exact/near-exact count constraints.
2. Measurement-process generative model: model sensor coverage/gap patterns as a latent sleep regularity state, then use the state as the JEPA target rather than raw row residuals.
3. Public-safe count solver: combine raw-timeline public-positive movement with only Q-count/S2-S3 block-rate movements that have negative or near-zero harmful-axis projection.
