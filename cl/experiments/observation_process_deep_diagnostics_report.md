# Observation-process deep diagnostics

This is a no-submission data-science audit. It asks whether the labels are driven by behavior, sensor observability, temporal alignment, raw identity/context, or subject-specific label language.

## Files produced

- `features/observation_coverage_features.parquet`
- `experiments/observation_hourly_coverage_long.csv`
- `experiments/observation_coverage_label_association.csv`
- `experiments/observation_coverage_state_association.csv`
- `experiments/observation_coverage_train_test_shift.csv`
- `experiments/observation_negative_control_coverage_results.csv`
- `experiments/observation_hourly_signature_by_target.csv`
- `experiments/observation_window_signal_ranking.csv`
- `features/observation_identity_token_features.parquet`
- `experiments/observation_identity_token_association.csv`
- `experiments/observation_subject_label_language.csv`
- `experiments/observation_singleton_label_anomalies.csv`

## 1. Sensor coverage / missingness

Top univariate coverage-label associations by direction-free AUC:

```
         analysis target                       feature  auc_raw  auc_absdir    mean_pos    mean_neg  diff_pos_minus_neg   n  pos_rate
coverage_vs_label     S2                   wifi_item_n 0.601835    0.601835  112.382253  101.535032           10.847221 450  0.651111
coverage_vs_label     S2                 wifi_record_n 0.601835    0.601835  112.382253  101.535032           10.847221 450  0.651111
coverage_vs_label     S3      hr_longest_missing_hours 0.399373    0.600627    6.895973    7.914474           -1.018501 450  0.662222
coverage_vs_label     S1     ble_longest_missing_hours 0.600567    0.600567    6.218241    5.496503            0.721738 450  0.682222
coverage_vs_label     S3 w_light_longest_missing_hours 0.407983    0.592017    2.151007    3.690789           -1.539783 450  0.662222
coverage_vs_label     S3                 pedo_record_n 0.591123    0.591123 1053.922819  955.256579           98.666240 450  0.662222
coverage_vs_label     S3                   pedo_item_n 0.591123    0.591123 1053.922819  955.256579           98.666240 450  0.662222
coverage_vs_label     S1                    gps_item_n 0.589018    0.589018 1187.850163 1038.846154          149.004009 450  0.682222
coverage_vs_label     S1                  gps_record_n 0.589018    0.589018 1187.850163 1038.846154          149.004009 450  0.682222
coverage_vs_label     Q2              wifi_night_hours 0.412803    0.587197    6.079051    6.786802           -0.707751 450  0.562222
coverage_vs_label     S1              gps_active_hours 0.586205    0.586205   21.905537   19.671329            2.234209 450  0.682222
coverage_vs_label     Q3     ble_longest_missing_hours 0.585504    0.585504    6.277778    5.555556            0.722222 450  0.600000
```

Top train/test coverage shifts:

```
                 analysis  target                  feature  auc_raw  auc_absdir  mean_pos    mean_neg  diff_pos_minus_neg   n  pos_rate
coverage_train_test_shift is_test      w_light_night_hours 0.575204    0.575204     6.780    5.924444            0.855556 700  0.357143
coverage_train_test_shift is_test           pedo_day_hours 0.574738    0.574738    14.460   12.913333            1.546667 700  0.357143
coverage_train_test_shift is_test              pedo_item_n 0.573560    0.573560  1155.328 1020.595556          134.732444 700  0.357143
coverage_train_test_shift is_test            pedo_record_n 0.573560    0.573560  1155.328 1020.595556          134.732444 700  0.357143
coverage_train_test_shift is_test     w_light_active_hours 0.568653    0.568653    21.488   19.180000            2.308000 700  0.357143
coverage_train_test_shift is_test        pedo_active_hours 0.564707    0.564707    20.792   18.446667            2.345333 700  0.357143
coverage_train_test_shift is_test         pedo_night_hours 0.561689    0.561689     6.332    5.533333            0.798667 700  0.357143
coverage_train_test_shift is_test        w_light_day_hours 0.556907    0.556907    14.708   13.255556            1.452444 700  0.357143
coverage_train_test_shift is_test  any_sensor_active_hours 0.555653    0.555653    11.840   11.508889            0.331111 700  0.357143
coverage_train_test_shift is_test           hr_night_hours 0.553493    0.553493     1.644    1.324444            0.319556 700  0.357143
coverage_train_test_shift is_test          hr_active_hours 0.552876    0.552876    12.388   11.113333            1.274667 700  0.357143
coverage_train_test_shift is_test hr_longest_missing_hours 0.552702    0.552702     8.236    7.240000            0.996000 700  0.357143
```

## 2. Coverage-only negative controls

If shuffled/shifted/subject-augmented controls stay strong, the signal is not clean day-level behavior.

```
target   n  pos_rate      auc  logloss  base_logloss  logloss_improvement                    control
    S4 450  0.560000 0.659051 0.656322      0.685930             0.029607      coverage_plus_subject
    Q1 450  0.495556 0.627467 0.665421      0.693108             0.027687 feature_shift_plus_subject
    S4 450  0.560000 0.646605 0.664333      0.685930             0.021597 feature_shift_plus_subject
    S3 450  0.662222 0.710151 0.618202      0.639550             0.021348      coverage_plus_subject
    S3 450  0.662222 0.716487 0.620397      0.639550             0.019154      subject_label_shuffle
    Q1 450  0.495556 0.603564 0.674242      0.693108             0.018866      coverage_plus_subject
    Q2 450  0.562222 0.622459 0.668671      0.685384             0.016713      coverage_plus_subject
    S3 450  0.662222 0.701232 0.628252      0.639550             0.011298 feature_shift_plus_subject
    S4 450  0.560000 0.629670 0.676902      0.685930             0.009027              coverage_only
    Q2 450  0.562222 0.598483 0.676367      0.685384             0.009017 feature_shift_plus_subject
    Q1 450  0.495556 0.571225 0.689689      0.693108             0.003419              coverage_only
    Q2 450  0.562222 0.595474 0.682184      0.685384             0.003200              coverage_only
    Q1 450  0.495556 0.573280 0.694229      0.693108            -0.001121      subject_label_shuffle
    S2 450  0.651111 0.671659 0.649103      0.646756            -0.002346      coverage_plus_subject
    S2 450  0.651111 0.677572 0.649161      0.646756            -0.002405      subject_label_shuffle
    S2 450  0.651111 0.671290 0.651908      0.646756            -0.005152 feature_shift_plus_subject
    S4 450  0.560000 0.579345 0.699123      0.685930            -0.013193      subject_label_shuffle
    S1 450  0.682222 0.688185 0.638383      0.625183            -0.013199      subject_label_shuffle
    Q3 450  0.600000 0.619362 0.687621      0.673012            -0.014609              coverage_only
    Q3 450  0.600000 0.620329 0.692835      0.673012            -0.019823 feature_shift_plus_subject
```

## 3. Time-window / alignment signatures

Best target-window-modality signals:

```
target modality  offset_day       window  mean_auc_absdir  max_auc_absdir  mean_abs_diff
    S1    usage           1   night00_05         0.574489        0.622901       0.462475
    S4     wifi          -1 morning06_11         0.537464        0.622360       0.339517
    S4     wifi          -1   night00_05         0.597356        0.616343       0.934030
    Q3     wifi           1    late22_23         0.593215        0.611957       0.794481
    S4    usage          -1     day12_17         0.563889        0.610550       0.413126
    Q3    usage          -1     day12_17         0.587646        0.608935       0.619204
    Q3      gps           1    late22_23         0.606547        0.608420       8.422182
    S4     wifi           0 morning06_11         0.542048        0.607138       0.349657
    S3     pedo           0   night00_05         0.570203        0.605729       6.942478
    Q3     wifi           0    late22_23         0.601160        0.605626       0.841078
    Q3      gps           0    late22_23         0.599027        0.604643       7.866384
    S4     wifi           1   night00_05         0.574881        0.604042       0.714318
    S3      ble          -1     day12_17         0.545613        0.602530       0.276185
    S1      gps          -1   night00_05         0.582016        0.601353       8.481073
    Q1       hr           1 evening18_21         0.587547        0.600937       7.973428
    Q1    usage          -1 morning06_11         0.562794        0.600272       0.467837
    S2     wifi           0 morning06_11         0.554874        0.599467       0.444373
    Q3     wifi           1 evening18_21         0.585481        0.599204       0.780490
    S1      gps          -1 evening18_21         0.584987        0.598906       6.949310
    Q1  w_light           0 evening18_21         0.577419        0.598487       5.903597
```

## 4. Raw identity/context tokens

Strongest token-label/state associations:

```
target                         token score_type     score      p_value  presence_days  rate_present  rate_absent  lift_present_minus_absent
    S3  wifi_bssid:16:7f:67:44:38:34       chi2 51.276013 8.025024e-13             39      0.128205     0.712895                  -0.584690
    S3  wifi_bssid:0c:96:cd:dc:d1:61       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:80:ca:4b:cb:e3:d6       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:a6:36:c7:fc:21:eb       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:a6:36:c7:ff:b7:58       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:e8:54:84:35:39:73       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:e8:54:84:35:71:2f       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:e8:54:84:35:87:35       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:30:16:9d:05:4b:ce       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3  wifi_bssid:e8:54:84:35:87:37       chi2 48.501542 3.300293e-12             40      0.150000     0.712195                  -0.562195
    S3 ble_address:D2:78:52:C4:46:4A       chi2 44.874845 2.100389e-11             36      0.138889     0.707729                  -0.568841
    S3 ble_address:4C:5B:B3:AE:46:40       chi2 43.454448 4.339442e-11             33      0.121212     0.705036                  -0.583824
    S3  wifi_bssid:a6:36:c7:fc:01:30       chi2 42.209257 8.201091e-11             37      0.162162     0.707022                  -0.544860
    S3  wifi_bssid:80:ca:4b:25:e4:66       chi2 41.349921 1.272766e-10             32      0.125000     0.703349                  -0.578349
    S3           usage_app_name:엘포인트       chi2 40.801752 1.684819e-10             45      0.222222     0.711111                  -0.488889
    S3  wifi_bssid:e8:54:84:35:91:0f       chi2 40.692211 1.781961e-10             34      0.147059     0.704327                  -0.557268
    S2  wifi_bssid:16:7f:67:44:38:34       chi2 30.949522 2.648273e-08             39      0.230769     0.690998                  -0.460228
    S2  wifi_bssid:0c:96:cd:dc:d1:61       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
    S2  wifi_bssid:e8:54:84:35:39:73       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
    S2  wifi_bssid:e8:54:84:35:87:37       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
    S2  wifi_bssid:e8:54:84:35:87:35       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
    S2  wifi_bssid:e8:54:84:35:71:2f       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
    S2  wifi_bssid:a6:36:c7:ff:b7:58       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
    S2  wifi_bssid:a6:36:c7:fc:21:eb       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
    S2  wifi_bssid:80:ca:4b:cb:e3:d6       chi2 28.961442 7.383340e-08             40      0.250000     0.690244                  -0.440244
```

## 5. Subject-specific label language

Subject-level prevalence, pair-correlation, persistence, and contradiction rates are in `observation_subject_label_language.csv`; singleton temporal anomalies are in `observation_singleton_label_anomalies.csv`.

## Interpretation checklist

- Coverage/missingness with AUC > ~0.65 means the target/state partly reflects sensor availability or device wearing/phone availability, not only behavior values.
- Train/test coverage AUC > ~0.65 means hidden rows are not a purely random hole under the observed sensor process.
- Shifted-feature or subject-shuffled controls close to real performance indicate static subject/context artifacts.
- Offset/window asymmetry indicates which calendar date actually matches the self-report label; weak asymmetry means the signal is broad subject routine rather than precise sleep-night behavior.
- Identity tokens with large lift are context fingerprints; useful for interpretation, but dangerous for public/private generalization if they mostly encode subject/place.
