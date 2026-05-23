# S2 sparse-head public-LB-informed meta diagnostics

Diagnostic candidate files were written, but no automatic submission recommendation is made.

## Anchor
`outputs/submission_meta_anchor_w02_noq3_prob.csv`

## Component
S2 sparse head: `existing_no_flat` + SelectK=32 + Logistic C=0.003 trained on all train rows.

## Candidate S2 shift summary
                                                 file                                                                                        description  S2_changed_rows  S2_mean_abs_delta_vs_anchor  S2_p95_abs_delta_vs_anchor  S2_max_abs_delta_vs_anchor  S2_corr_vs_anchor  S2_candidate_mean_prob  S2_anchor_mean_prob  S2_mean_prob_shift
     submission_meta_anchor_s2sparse_blend30_prob.csv                                               Anchor S2 interpolated 30% toward sparse raw32 head.              250                     0.008303                    0.020143                    0.022520           0.998529                0.595674             0.596454           -0.000781
     submission_meta_anchor_s2sparse_blend50_prob.csv                                               Anchor S2 interpolated 50% toward sparse raw32 head.              250                     0.013838                    0.033572                    0.037533           0.996011                0.595153             0.596454           -0.001301
     submission_meta_anchor_s2sparse_blend70_prob.csv                                               Anchor S2 interpolated 70% toward sparse raw32 head.              250                     0.019374                    0.047000                    0.052547           0.992380                0.594633             0.596454           -0.001822
submission_meta_anchor_plus_s2sparse_resid30_prob.csv                                         Anchor plus 30% of sparse raw32 minus base residual on S2.              250                     0.011970                    0.027370                    0.029429           0.996865                0.599494             0.596454            0.003040
submission_meta_anchor_plus_s2sparse_resid50_prob.csv                                         Anchor plus 50% of sparse raw32 minus base residual on S2.              250                     0.019950                    0.045617                    0.049049           0.991565                0.601520             0.596454            0.005066
     submission_meta_anchor_s2sparse_replace_prob.csv Full S2 replacement with sparse raw32 head. Diagnostic/highest shift; not first submission choice.              250                     0.027677                    0.067144                    0.075067           0.985074                0.593852             0.596454           -0.002602
submission_meta_anchor_s2dl20_s2sparse30_avg_prob.csv                Average previous S2-DL20 residual with a mild 30% sparse-S2 interpolation residual.              250                     0.011740                    0.022341                    0.023888           0.997953                0.588853             0.596454           -0.007601

## Selected sparse S2 features
                              feature
                  screen_n__subj_mean
           screen_use_mean__subj_mean
            screen_use_sum__subj_mean
          screen_use_21_03__subj_mean
          screen_use_18_24__subj_mean
                wlight_max__subj_mean
                      ac_n__subj_mean
       sleepwin_screen_sum__subj_mean
pre_sleep_screen_sum_21_03__subj_mean
           gps_speed_21_03__subj_mean
          app_unique_count__subj_mean
            app_total_time__subj_mean
            app_time_21_03__subj_mean
           app_social_time__subj_mean
       app_study_work_time__subj_mean
              wifi_records__subj_mean
                        wifi_rssi_max
             wifi_rssi_max__subj_mean
                   wifi_records_21_03
        wifi_records_21_03__subj_mean
              ble_rssi_max__subj_mean
  screenoff_run_start_hour__subj_mean
                       dow__subj_mean
                                month
                     month__subj_mean
         gap_from_prev_day__subj_mean
           gap_to_next_day__subj_mean
       app_hourly_time_max__subj_mean
       app_hourly_time_std__subj_mean
     app_hourly_unique_max__subj_mean
ble_deviceclass_1344_count__subj_mean
 ble_deviceclass_524_count__subj_mean

## Interpretation
Use the interpolation candidates first if public probing is allowed. Residual and replacement variants are higher-shift diagnostics.
The safest new S2-only files by shift are the 30/50% anchor-to-sparse blends; the replacement file is intentionally not first-choice.