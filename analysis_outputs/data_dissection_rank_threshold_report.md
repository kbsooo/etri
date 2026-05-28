# Rank/Threshold Miner

This scans top residual/label/shift features as possible subject-relative threshold rules. Each candidate is a one-level stump selected inside geometry folds.

## Best Overall

```
                                                                            feature           mode target  full_loss  full_base_loss  full_delta_vs_stage2  mean_fold_loss  mean_fold_delta  win_rate dominant_direction
presleep_temporal_context_features__presleep_screen_post2h_m_screen_use_count_next1      subject_z     Q3   0.659729        0.642378              0.017351        0.649236         0.015875      0.25               high
         measurement_process_features__mp_watch_pre6h_obs_frac_min_same_weekend_dev   subject_rank     Q3   0.661422        0.642378              0.019044        0.654090         0.020728      0.00               high
       presleep_temporal_context_features__presleep_wlight_post2h_w_light_sum_next1   subject_rank     Q3   0.661766        0.642378              0.019388        0.657833         0.024471      0.00                low
            quiet_window_residual_features__quiet_w23_33_screen_step_activity_start      subject_z     Q3   0.663707        0.642378              0.021329        0.657106         0.023745      0.00               high
         measurement_process_features__mp_watch_pre6h_obs_frac_min_same_weekend_dev            raw     Q3   0.664368        0.642378              0.021990        0.659617         0.026256      0.00               high
  measurement_process_features__mp_watch_evening18_24_obs_frac_min_same_weekend_dev subject_center     Q3   0.664573        0.642378              0.022195        0.657933         0.024571      0.00                low
         measurement_process_features__mp_hr_pre3_to_core_obs_drop_same_weekend_dev   subject_rank     Q3   0.664960        0.642378              0.022582        0.651633         0.018272      0.00               high
presleep_temporal_context_features__presleep_screen_post2h_m_screen_use_count_next1            raw     Q3   0.665271        0.642378              0.022893        0.657780         0.024419      0.25               high
         measurement_process_features__mp_usage_core5h_p90_gap_min_same_weekend_dev      subject_z     Q3   0.665758        0.642378              0.023380        0.659299         0.025938      0.00                low
             measurement_process_features__mp_usage_core5h_row_count_zdev_subj_mean      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
          measurement_process_features__mp_usage_core5h_minute_count_zdev_subj_mean      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
              measurement_process_features__mp_usage_core5h_obs_frac_zdev_subj_mean      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
               measurement_process_features__mp_usage_core5h_row_count_dev_subj_med      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
            measurement_process_features__mp_usage_core5h_minute_count_dev_subj_med      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
                            measurement_process_features__mp_usage_core5h_row_count      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
                         measurement_process_features__mp_usage_core5h_minute_count      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
                measurement_process_features__mp_usage_core5h_obs_frac_dev_subj_med      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
                             measurement_process_features__mp_usage_core5h_obs_frac      subject_z     Q3   0.665805        0.642378              0.023427        0.661138         0.027777      0.00               high
presleep_temporal_context_features__presleep_screen_post2h_m_screen_use_count_next1   subject_rank     Q3   0.666089        0.642378              0.023711        0.655401         0.022040      0.00                low
             measurement_process_features__mp_hr_pre3h_p90_gap_min_same_weekend_dev   subject_rank     Q3   0.666406        0.642378              0.024028        0.660943         0.027582      0.00                low
       presleep_temporal_context_features__presleep_wlight_post2h_w_light_sum_next1            raw     Q3   0.666662        0.642378              0.024284        0.664146         0.030785      0.00                low
      presleep_temporal_context_features__presleep_wlight_post2h_w_light_mean_next1            raw     Q3   0.666662        0.642378              0.024284        0.664146         0.030785      0.00                low
       presleep_temporal_context_features__presleep_wlight_post2h_w_light_std_next1            raw     Q3   0.667178        0.642378              0.024800        0.662351         0.028990      0.00                low
       presleep_temporal_context_features__presleep_wlight_post2h_w_light_max_next1            raw     Q3   0.667569        0.642378              0.025191        0.662056         0.028695      0.00                low
           measurement_process_features__mp_usage_core5h_p90_gap_min_zdev_subj_mean   subject_rank     Q3   0.668288        0.642378              0.025910        0.669297         0.035936      0.00                low
             measurement_process_features__mp_usage_core5h_p90_gap_min_dev_subj_med   subject_rank     Q3   0.668288        0.642378              0.025910        0.669297         0.035936      0.00                low
                          measurement_process_features__mp_usage_core5h_p90_gap_min   subject_rank     Q3   0.668288        0.642378              0.025910        0.669297         0.035936      0.00                low
            measurement_process_features__mp_hr_pre6h_minute_count_same_weekend_dev            raw     Q3   0.669015        0.642378              0.026638        0.657832         0.024471      0.00               high
               measurement_process_features__mp_hr_pre6h_row_count_same_weekend_dev            raw     Q3   0.669015        0.642378              0.026638        0.657832         0.024471      0.00               high
                measurement_process_features__mp_hr_pre6h_obs_frac_same_weekend_dev            raw     Q3   0.669015        0.642378              0.026638        0.657832         0.024471      0.00               high
```

## Best By Target

```
                                                                            feature           mode target  full_loss  full_base_loss  full_delta_vs_stage2  mean_fold_loss  mean_fold_delta  win_rate dominant_direction
           measurement_process_features__mp_usage_core5h_row_count_same_weekend_dev            raw     Q1   0.633217        0.580517              0.052700        0.631123         0.069704      0.00                low
        measurement_process_features__mp_usage_core5h_minute_count_same_weekend_dev            raw     Q1   0.633217        0.580517              0.052700        0.631123         0.069704      0.00                low
            measurement_process_features__mp_usage_core5h_obs_frac_same_weekend_dev            raw     Q1   0.633217        0.580517              0.052700        0.631123         0.069704      0.00                low
            measurement_process_features__mp_usage_core5h_span_min_same_weekend_dev subject_center     Q1   0.634297        0.580517              0.053779        0.640606         0.079187      0.00                low
               pre_sleep_relative_features__presleep_activity_core5h_m_activity_std      subject_z     Q1   0.639732        0.580517              0.059215        0.633547         0.072128      0.00                low
               pre_sleep_relative_features__presleep_activity_core5h_m_activity_std   subject_rank     Q1   0.639732        0.580517              0.059215        0.633547         0.072128      0.00                low
            measurement_process_features__mp_usage_core5h_span_min_same_weekend_dev            raw     Q1   0.640982        0.580517              0.060465        0.637212         0.075793      0.00                low
                             measurement_process_features__mp_usage_core5h_span_min subject_center     Q1   0.643953        0.580517              0.063435        0.647655         0.086237      0.00                low
       measurement_process_features__mp_usage_day12_18_gap60_count_same_weekend_dev   subject_rank     Q2   0.667837        0.636324              0.031513        0.685731         0.056750      0.00                low
       measurement_process_features__mp_usage_day12_18_gap60_count_same_weekend_dev      subject_z     Q2   0.669042        0.636324              0.032718        0.676935         0.047954      0.00                low
               pre_sleep_relative_features__presleep_pedo_core5h_step_frequency_max subject_center     Q2   0.669982        0.636324              0.033658        0.676300         0.047319      0.00                low
                         pre_sleep_relative_features__presleep_pedo_core5h_step_max subject_center     Q2   0.669982        0.636324              0.033658        0.676300         0.047319      0.00                low
                        pre_sleep_relative_features__presleep_pedo_core5h_speed_max subject_center     Q2   0.670914        0.636324              0.034590        0.677969         0.048988      0.00                low
   measurement_process_features__mp_usage_day12_18_longest_gap_min_same_weekend_dev            raw     Q2   0.671448        0.636324              0.035123        0.680407         0.051426      0.00               high
                   rhythm_regular_features__rr_wlight_pre1h_w_light_min_prev1_delta   subject_rank     Q2   0.675273        0.636324              0.038948        0.668029         0.039048      0.00                low
       presleep_temporal_context_features__presleep_wlight_pre1h_w_light_min_dprev1   subject_rank     Q2   0.675273        0.636324              0.038948        0.668029         0.039048      0.00                low
presleep_temporal_context_features__presleep_screen_post2h_m_screen_use_count_next1      subject_z     Q3   0.659729        0.642378              0.017351        0.649236         0.015875      0.25               high
         measurement_process_features__mp_watch_pre6h_obs_frac_min_same_weekend_dev   subject_rank     Q3   0.661422        0.642378              0.019044        0.654090         0.020728      0.00               high
       presleep_temporal_context_features__presleep_wlight_post2h_w_light_sum_next1   subject_rank     Q3   0.661766        0.642378              0.019388        0.657833         0.024471      0.00                low
            quiet_window_residual_features__quiet_w23_33_screen_step_activity_start      subject_z     Q3   0.663707        0.642378              0.021329        0.657106         0.023745      0.00               high
         measurement_process_features__mp_watch_pre6h_obs_frac_min_same_weekend_dev            raw     Q3   0.664368        0.642378              0.021990        0.659617         0.026256      0.00               high
  measurement_process_features__mp_watch_evening18_24_obs_frac_min_same_weekend_dev subject_center     Q3   0.664573        0.642378              0.022195        0.657933         0.024571      0.00                low
         measurement_process_features__mp_hr_pre3_to_core_obs_drop_same_weekend_dev   subject_rank     Q3   0.664960        0.642378              0.022582        0.651633         0.018272      0.00               high
presleep_temporal_context_features__presleep_screen_post2h_m_screen_use_count_next1            raw     Q3   0.665271        0.642378              0.022893        0.657780         0.024419      0.25               high
               pre_sleep_relative_features__presleep_activity_core5h_m_activity_std            raw     S1   0.552219        0.488314              0.063905        0.532453         0.078951      0.00               high
               pre_sleep_relative_features__presleep_activity_core5h_m_activity_std subject_center     S1   0.563338        0.488314              0.075024        0.541690         0.088189      0.00                low
               pre_sleep_relative_features__presleep_activity_core5h_m_activity_max            raw     S1   0.564018        0.488314              0.075704        0.545406         0.091904      0.00                low
    measurement_process_features__mp_activity_core5h_positive_frac_same_weekend_dev      subject_z     S1   0.567140        0.488314              0.078826        0.538181         0.084680      0.00                low
    measurement_process_features__mp_activity_core5h_positive_frac_same_weekend_dev   subject_rank     S1   0.567140        0.488314              0.078826        0.538181         0.084680      0.00                low
        measurement_process_features__mp_activity_core5h_positive_frac_dev_subj_med      subject_z     S1   0.567140        0.488314              0.078826        0.538181         0.084680      0.00                low
        measurement_process_features__mp_activity_core5h_positive_frac_dev_subj_med   subject_rank     S1   0.567140        0.488314              0.078826        0.538181         0.084680      0.00                low
                     measurement_process_features__mp_activity_core5h_positive_frac      subject_z     S1   0.567140        0.488314              0.078826        0.538181         0.084680      0.00                low
                   rhythm_regular_features__rr_wlight_pre1h_w_light_min_prev1_delta subject_center     S2   0.597163        0.525149              0.072014        0.592128         0.094208      0.00                low
                   rhythm_regular_features__rr_wlight_pre1h_w_light_min_prev1_delta      subject_z     S2   0.597163        0.525149              0.072014        0.592128         0.094208      0.00                low
       presleep_temporal_context_features__presleep_wlight_pre1h_w_light_min_dprev1 subject_center     S2   0.597163        0.525149              0.072014        0.592128         0.094208      0.00                low
       presleep_temporal_context_features__presleep_wlight_pre1h_w_light_min_dprev1      subject_z     S2   0.597163        0.525149              0.072014        0.592128         0.094208      0.00                low
               pre_sleep_relative_features__presleep_pedo_core5h_step_frequency_max      subject_z     S2   0.604101        0.525149              0.078952        0.573942         0.076023      0.00                low
                         pre_sleep_relative_features__presleep_pedo_core5h_step_max      subject_z     S2   0.604101        0.525149              0.078952        0.573942         0.076023      0.00                low
                        pre_sleep_relative_features__presleep_pedo_core5h_speed_max      subject_z     S2   0.604101        0.525149              0.078952        0.573942         0.076023      0.00                low
               pre_sleep_relative_features__presleep_pedo_core5h_step_frequency_max   subject_rank     S2   0.605449        0.525149              0.080301        0.574223         0.076303      0.00                low
                   rhythm_regular_features__rr_wlight_pre1h_w_light_min_prev1_delta subject_center     S3   0.577347        0.475357              0.101991        0.563023         0.106766      0.00               high
       presleep_temporal_context_features__presleep_wlight_pre1h_w_light_min_dprev1 subject_center     S3   0.577347        0.475357              0.101991        0.563023         0.106766      0.00               high
    measurement_process_features__mp_activity_core5h_positive_frac_same_weekend_dev      subject_z     S3   0.578330        0.475357              0.102973        0.556087         0.099830      0.00                low
    measurement_process_features__mp_activity_core5h_positive_frac_same_weekend_dev   subject_rank     S3   0.578330        0.475357              0.102973        0.556087         0.099830      0.00                low
        measurement_process_features__mp_activity_core5h_positive_frac_dev_subj_med      subject_z     S3   0.578330        0.475357              0.102973        0.556087         0.099830      0.00                low
        measurement_process_features__mp_activity_core5h_positive_frac_dev_subj_med   subject_rank     S3   0.578330        0.475357              0.102973        0.556087         0.099830      0.00                low
                     measurement_process_features__mp_activity_core5h_positive_frac      subject_z     S3   0.578330        0.475357              0.102973        0.556087         0.099830      0.00                low
                     measurement_process_features__mp_activity_core5h_positive_frac   subject_rank     S3   0.578330        0.475357              0.102973        0.556087         0.099830      0.00                low
         measurement_process_features__mp_hr_all24h_median_gap_min_same_weekend_dev subject_center     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
         measurement_process_features__mp_hr_all24h_median_gap_min_same_weekend_dev      subject_z     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
                          measurement_process_features__mp_hr_all24h_median_gap_min subject_center     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
                          measurement_process_features__mp_hr_all24h_median_gap_min      subject_z     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
             measurement_process_features__mp_hr_all24h_median_gap_min_dev_subj_med subject_center     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
             measurement_process_features__mp_hr_all24h_median_gap_min_dev_subj_med      subject_z     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
           measurement_process_features__mp_hr_all24h_median_gap_min_zdev_subj_mean subject_center     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
           measurement_process_features__mp_hr_all24h_median_gap_min_zdev_subj_mean      subject_z     S4   0.650470        0.590626              0.059843        0.657902         0.074254      0.00                low
```

## Interpretation

If these stumps beat stage2, the label likely has a recoverable threshold/rank component. If they lose but still show stable direction, use them as weak count priors rather than direct probability replacements.
