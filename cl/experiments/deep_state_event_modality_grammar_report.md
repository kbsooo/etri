# Deeper State/Event/Modality/Grammar Diagnostics

## 1. State transition event-study

For each latent-state transition day, engineered features were z-scored and compared as `after - before`. This asks: when label grammar changes, what behavioral feature families move?

transition           family  n_events  n_feature_deltas  mean_delta_z  mean_abs_delta_z
      0->1              ssl         9              1700         0.003             1.025
      0->1      heart_light         9              1156         0.060             0.751
      0->1    sleep_episode         9                68         0.109             0.727
      0->1   activity_steps         9              1700        -0.085             0.707
      0->1     screen_phone         9              1700        -0.022             0.554
      0->1 location_context         9              1700         0.165             0.553
      0->1     routine_axes         9              1700        -0.024             0.504
      0->2      heart_light         9              1666         0.089             0.870
      0->2              ssl         9              2450         0.068             0.843
      0->2   activity_steps         9              2450         0.147             0.769
      0->2     screen_phone         9              2450         0.116             0.603
      0->2     routine_axes         9              2450         0.040             0.559
      0->2    sleep_episode         9                98         0.109             0.549
      0->2 location_context         9              2450        -0.126             0.393
      1->0    sleep_episode        10                66         0.037             0.911
      1->0              ssl        10              1650         0.024             0.880
      1->0      heart_light        10              1122        -0.196             0.857
      1->0   activity_steps        10              1650         0.020             0.820
      1->0 location_context        10              1650        -0.215             0.611
      1->0     screen_phone        10              1650        -0.106             0.582
      1->0     routine_axes        10              1650         0.003             0.484
      1->2              ssl         8              1850         0.043             0.785
      1->2      heart_light         8              1258         0.065             0.731
      1->2     screen_phone         8              1850         0.089             0.657
      1->2   activity_steps         8              1850         0.039             0.646
      1->2    sleep_episode         8                74        -0.003             0.635
      1->2     routine_axes         8              1850        -0.027             0.492
      1->2 location_context         8              1850        -0.092             0.420
      2->0              ssl        10              2450        -0.080             0.887
      2->0    sleep_episode        10                98        -0.007             0.712
      2->0   activity_steps        10              2450         0.023             0.702
      2->0     screen_phone        10              2450        -0.036             0.677
      2->0      heart_light        10              1666        -0.039             0.637
      2->0     routine_axes        10              2450         0.008             0.566
      2->0 location_context        10              2450         0.042             0.459
      2->1              ssl         9              1750         0.042             0.864
      2->1    sleep_episode         9                70         0.069             0.755
      2->1     screen_phone         9              1750        -0.108             0.686
      2->1      heart_light         9              1190        -0.039             0.679
      2->1   activity_steps         9              1750        -0.045             0.663
      2->1     routine_axes         9              1750         0.015             0.474
      2->1 location_context         9              1750        -0.039             0.430

## 2. Raw modality state separability

Daily raw modality aggregates were built directly from the original parquet files, then tested under masked splits. `normalized=True` means within-subject z-scoring, i.e. asking whether deviations from a person's own baseline matter more than raw level.

          scheme   modality  normalized  masks   acc  bal_acc  state_logloss  majority_acc
interleaved_rank   raw_wifi       False      3 0.448    0.452          1.065         0.348
interleaved_rank     raw_hr       False      3 0.428    0.410          1.075         0.348
interleaved_rank    raw_ble       False      3 0.395    0.381          1.077         0.348
interleaved_rank  raw_usage       False      3 0.403    0.377          1.090         0.348
interleaved_rank   raw_pedo       False      3 0.369    0.361          1.098         0.348
interleaved_rank raw_screen       False      3 0.371    0.354          1.088         0.348
interleaved_rank raw_mlight       False      3 0.368    0.339          1.121         0.348
interleaved_rank    raw_gps       False      3 0.351    0.338          1.113         0.348
interleaved_rank raw_wlight        True      3 0.360    0.338          1.114         0.348
interleaved_rank   raw_pedo        True      3 0.353    0.337          1.111         0.348
interleaved_rank    raw_ble        True      3 0.353    0.335          1.094         0.348
interleaved_rank    raw_gps        True      3 0.361    0.334          1.108         0.348
interleaved_rank  raw_usage        True      3 0.357    0.333          1.098         0.348
interleaved_rank    raw_amb        True      3 0.368    0.329          1.100         0.348
interleaved_rank   raw_wifi        True      3 0.348    0.329          1.114         0.348
interleaved_rank raw_wlight       False      3 0.351    0.326          1.110         0.348
interleaved_rank    raw_amb       False      3 0.364    0.325          1.102         0.348
interleaved_rank     raw_ac       False      3 0.356    0.325          1.115         0.348
interleaved_rank     raw_hr        True      3 0.347    0.323          1.108         0.348
interleaved_rank raw_screen        True      3 0.344    0.312          1.116         0.348
     testpattern   raw_wifi       False      4 0.422    0.427          1.080         0.373
     testpattern     raw_hr       False      4 0.395    0.384          1.095         0.373
     testpattern    raw_ble       False      4 0.383    0.371          1.084         0.373
     testpattern  raw_usage       False      4 0.378    0.358          1.111         0.373
     testpattern raw_screen       False      4 0.377    0.356          1.095         0.373
     testpattern   raw_pedo       False      4 0.360    0.350          1.109         0.373
     testpattern    raw_gps       False      4 0.359    0.344          1.113         0.373
     testpattern  raw_usage        True      4 0.362    0.342          1.108         0.373
     testpattern    raw_ble        True      4 0.353    0.342          1.102         0.373
     testpattern     raw_ac       False      4 0.363    0.338          1.113         0.373
     testpattern raw_mlight       False      4 0.360    0.335          1.132         0.373
     testpattern    raw_amb       False      4 0.361    0.334          1.111         0.373
     testpattern raw_wlight        True      4 0.350    0.332          1.115         0.373
     testpattern raw_wlight       False      4 0.352    0.329          1.114         0.373
     testpattern    raw_amb        True      4 0.343    0.322          1.109         0.373
     testpattern     raw_hr        True      4 0.334    0.321          1.121         0.373
     testpattern   raw_wifi        True      4 0.334    0.320          1.120         0.373
     testpattern raw_mlight        True      4 0.337    0.318          1.126         0.373
     testpattern   raw_pedo        True      4 0.328    0.313          1.122         0.373
     testpattern    raw_act        True      4 0.330    0.313          1.126         0.373

## 3. Raw modality target signal

AUC is easier to read here than tiny logloss differences. Values near 0.5 mean no useful rank signal.

          scheme target   modality  normalized  masks  mean_logloss  mean_auc
interleaved_rank     Q1   raw_wifi       False      3         0.686     0.598
interleaved_rank     Q1    raw_ble        True      3         0.692     0.568
interleaved_rank     Q1 raw_wlight       False      3         0.691     0.565
interleaved_rank     Q2     raw_ac        True      3         0.687     0.587
interleaved_rank     Q2     raw_ac       False      3         0.705     0.565
interleaved_rank     Q2 raw_mlight       False      3         0.699     0.556
interleaved_rank     Q3 raw_mlight       False      3         0.671     0.590
interleaved_rank     Q3 raw_mlight        True      3         0.669     0.584
interleaved_rank     Q3     raw_hr       False      3         0.666     0.579
interleaved_rank     S1 raw_screen       False      3         0.608     0.677
interleaved_rank     S1  raw_usage       False      3         0.619     0.610
interleaved_rank     S1    raw_ble       False      3         0.630     0.573
interleaved_rank     S2 raw_screen       False      3         0.639     0.630
interleaved_rank     S2   raw_wifi       False      3         0.640     0.610
interleaved_rank     S2     raw_hr       False      3         0.637     0.607
interleaved_rank     S3    raw_ble       False      3         0.637     0.577
interleaved_rank     S3    raw_amb        True      3         0.646     0.571
interleaved_rank     S3    raw_gps       False      3         0.637     0.562
interleaved_rank     S4  raw_usage       False      3         0.680     0.603
interleaved_rank     S4   raw_wifi       False      3         0.681     0.591
interleaved_rank     S4 raw_screen       False      3         0.685     0.565
     testpattern     Q1   raw_wifi       False      4         0.683     0.600
     testpattern     Q1  raw_usage       False      4         0.693     0.557
     testpattern     Q1    raw_ble        True      4         0.694     0.550
     testpattern     Q2     raw_ac       False      4         0.681     0.602
     testpattern     Q2     raw_ac        True      4         0.686     0.564
     testpattern     Q2 raw_screen        True      4         0.688     0.564
     testpattern     Q3 raw_mlight       False      4         0.671     0.582
     testpattern     Q3    raw_ble        True      4         0.671     0.568
     testpattern     Q3     raw_hr       False      4         0.670     0.567
     testpattern     S1 raw_screen       False      4         0.607     0.667
     testpattern     S1  raw_usage       False      4         0.622     0.598
     testpattern     S1     raw_hr       False      4         0.620     0.581
     testpattern     S2 raw_screen       False      4         0.645     0.633
     testpattern     S2    raw_ble       False      4         0.648     0.606
     testpattern     S2     raw_hr       False      4         0.646     0.598
     testpattern     S3    raw_ble       False      4         0.639     0.591
     testpattern     S3    raw_gps       False      4         0.639     0.580
     testpattern     S3     raw_hr       False      4         0.639     0.578
     testpattern     S4   raw_wifi       False      4         0.679     0.620
     testpattern     S4     raw_ac       False      4         0.688     0.579
     testpattern     S4    raw_ble       False      4         0.688     0.565

## 4. Q2/Q3 direction/gap grammar

target  direction   n  p_y1  p_other_t1  mean_prev_gap  mean_next_gap
    Q2   agree_00 107 0.234       0.467          1.897          1.533
    Q2   agree_11 161 0.739       0.658          1.540          1.646
    Q2 falling_10  80 0.600       0.613          1.812          1.562
    Q2  rising_01  82 0.585       0.634          1.244          1.866
    Q3   agree_00  78 0.244       0.410          1.487          1.551
    Q3   agree_11 166 0.777       0.627          1.602          1.530
    Q3 falling_10  91 0.582       0.571          1.824          1.934
    Q3  rising_01  95 0.589       0.547          1.579          1.642

### Conflict cases by gap bucket and other target

target  direction       gap_bucket  other_t  n  p_y1  mean_prev_gap  mean_next_gap
    Q2 falling_10 next_much_closer        0  2 0.000          7.500          2.500
    Q2 falling_10 next_much_closer        1  1 1.000         20.000          1.000
    Q2 falling_10      next_closer        0  2 1.000          8.000          5.000
    Q2 falling_10      next_closer        1  6 0.500          3.500          1.500
    Q2 falling_10         balanced        0 25 0.280          1.120          1.280
    Q2 falling_10         balanced        1 39 0.821          1.026          1.154
    Q2 falling_10      prev_closer        0  2 0.000          1.000          4.000
    Q2 falling_10      prev_closer        1  2 1.000          1.000          3.000
    Q2 falling_10 prev_much_closer        1  1 1.000          1.000          9.000
    Q2  rising_01 next_much_closer        1  1 1.000          7.000          3.000
    Q2  rising_01      next_closer        0  4 0.250          2.750          1.250
    Q2  rising_01      next_closer        1  5 0.400          2.400          1.000
    Q2  rising_01         balanced        0 25 0.480          1.000          1.080
    Q2  rising_01         balanced        1 38 0.684          1.000          1.211
    Q2  rising_01      prev_closer        0  1 0.000          1.000          3.000
    Q2  rising_01      prev_closer        1  4 0.750          1.000          3.750
    Q2  rising_01 prev_much_closer        1  4 0.750          1.000         12.250
    Q3 falling_10 next_much_closer        0  1 0.000         16.000          1.000
    Q3 falling_10 next_much_closer        1  2 1.000         13.500          1.500
    Q3 falling_10      next_closer        0  3 0.667          3.000          1.000
    Q3 falling_10      next_closer        1  6 0.500          5.167          2.833
    Q3 falling_10         balanced        0 34 0.412          1.059          1.176
    Q3 falling_10         balanced        1 40 0.700          1.025          1.150
    Q3 falling_10      prev_closer        1  1 1.000          2.000          6.000
    Q3 falling_10 prev_much_closer        0  1 0.000          1.000         17.000
    Q3 falling_10 prev_much_closer        1  3 1.000          1.000         14.333
    Q3  rising_01 next_much_closer        0  1 0.000          9.000          4.000
    Q3  rising_01 next_much_closer        1  1 1.000         25.000          2.000
    Q3  rising_01      next_closer        0  7 0.429          2.714          1.143
    Q3  rising_01      next_closer        1  6 0.667          2.167          1.000
    Q3  rising_01         balanced        0 33 0.485          1.121          1.212
    Q3  rising_01         balanced        1 41 0.659          1.000          1.220
    Q3  rising_01      prev_closer        0  1 0.000          1.000          3.000
    Q3  rising_01      prev_closer        1  2 1.000          1.000          3.000
    Q3  rising_01 prev_much_closer        0  1 1.000          1.000         10.000
    Q3  rising_01 prev_much_closer        1  2 1.000          1.000         13.500

## 5. Output files

- `experiments/deep_state_transition_feature_deltas_raw.csv`
- `experiments/deep_state_transition_family_event_study.csv`
- `experiments/deep_state_transition_top_features.csv`
- `features/deep_raw_modality_daily_features.parquet`
- `experiments/deep_raw_modality_state_separability_summary.csv`
- `experiments/deep_raw_modality_target_signal_summary.csv`
- `experiments/deep_q2q3_direction_summary.csv`
- `experiments/deep_q2q3_conflict_gap_other_summary.csv`
