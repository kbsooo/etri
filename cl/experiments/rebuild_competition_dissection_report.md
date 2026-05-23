# Rebuild competition dissection report

## 1. Split forensics

{
  "n_train": 450,
  "n_test": 250,
  "n_subjects_train": 10,
  "n_subjects_test": 10,
  "test_rows_with_prev_train_share": 1.0,
  "test_rows_with_next_train_share": 0.624,
  "test_rows_with_both_neighbors_share": 0.624,
  "test_rows_beyond_train_max_share": 0.376,
  "median_test_frac": 0.6024868705591597,
  "median_nearest_train_gap_d": 4.0,
  "p90_nearest_train_gap_d": 12.0,
  "median_prev_gap_d": 5.0,
  "median_next_gap_d": 5.0,
  "weekday_dist": {
    "0": 0.132,
    "1": 0.148,
    "2": 0.156,
    "3": 0.148,
    "4": 0.132,
    "5": 0.144,
    "6": 0.14
  }
}

### Subject split summary top/bottom

subject_id  test_rows  median_frac  min_frac  max_frac  median_nearest_gap  share_has_both_neighbors  share_beyond_tail
      id05         21     0.578125  0.406250       1.0                 2.0                  0.761905           0.238095
      id08         19     0.594595  0.432432       1.0                 1.0                  0.894737           0.105263
      id06         24     0.598592  0.422535       1.0                 2.0                  0.750000           0.250000
      id04         27     0.602410  0.409639       1.0                 2.0                  0.888889           0.111111
      id03         21     0.603774  0.415094       1.0                 5.0                  0.523810           0.476190
      id01         27     0.611940  0.417910       1.0                 6.0                  0.518519           0.481481
      id09         27     0.611940  0.417910       1.0                 6.0                  0.518519           0.481481
      id02         32     0.702532  0.405063       1.0                 6.0                  0.500000           0.500000
      id10         22     0.703704  0.407407       1.0                 6.5                  0.500000           0.500000
      id07         30     0.711538  0.423077       1.0                 6.0                  0.500000           0.500000

subject_id  test_rows  median_frac  min_frac  max_frac  median_nearest_gap  share_has_both_neighbors  share_beyond_tail
      id05         21     0.578125  0.406250       1.0                 2.0                  0.761905           0.238095
      id08         19     0.594595  0.432432       1.0                 1.0                  0.894737           0.105263
      id06         24     0.598592  0.422535       1.0                 2.0                  0.750000           0.250000
      id04         27     0.602410  0.409639       1.0                 2.0                  0.888889           0.111111
      id03         21     0.603774  0.415094       1.0                 5.0                  0.523810           0.476190
      id01         27     0.611940  0.417910       1.0                 6.0                  0.518519           0.481481
      id09         27     0.611940  0.417910       1.0                 6.0                  0.518519           0.481481
      id02         32     0.702532  0.405063       1.0                 6.0                  0.500000           0.500000
      id10         22     0.703704  0.407407       1.0                 6.5                  0.500000           0.500000
      id07         30     0.711538  0.423077       1.0                 6.0                  0.500000           0.500000

## 2. Label semantics

target  global_prev  subject_prev_std  mean_flip_rate  mean_lag1_autocorr  median_run_len  p90_run_len  weekday_prev_std  month_prev_std
    Q1       0.4956            0.1664          0.3808              0.1379          2.0000       5.0000            0.0810          0.1528
    Q2       0.5622            0.1394          0.3455              0.2252          2.0000       7.0000            0.0551          0.1002
    Q3       0.6000            0.1175          0.3513              0.2187          2.0000       5.0000            0.0847          0.1555
    S1       0.6822            0.1710          0.3551              0.0360          2.0000       5.0000            0.0713          0.1404
    S2       0.6511            0.2074          0.3854              0.0023          1.0000       5.0000            0.0552          0.2350
    S3       0.6622            0.2348          0.3547             -0.0287          1.0000       6.0000            0.0554          0.2522
    S4       0.5600            0.1848          0.4120              0.0145          2.0000       5.0000            0.0835          0.1889

### Target family heuristic

{
  "Q1": "state_temporal_candidate",
  "Q2": "state_temporal_candidate",
  "Q3": "freeze/noisy_candidate",
  "S1": "state_temporal_candidate",
  "S2": "state_temporal_candidate",
  "S3": "state_temporal_candidate",
  "S4": "state_temporal_candidate"
}

### Label correlation

       Q1     Q2     Q3    S1    S2     S3     S4
Q1  1.000  0.122  0.102 0.361 0.073 -0.119  0.019
Q2  0.122  1.000  0.340 0.052 0.003 -0.052 -0.024
Q3  0.102  0.340  1.000 0.066 0.002 -0.027  0.007
S1  0.361  0.052  0.066 1.000 0.382  0.118  0.107
S2  0.073  0.003  0.002 0.382 1.000  0.394  0.478
S3 -0.119 -0.052 -0.027 0.118 0.394  1.000  0.086
S4  0.019 -0.024  0.007 0.107 0.478  0.086  1.000

## 3. Validation scheme credibility by type

          scheme  masks  public_match_mean  w02_minus_w01_mean  w03_minus_w02_mean  graph_minus_w02_mean  block_minus_w02_mean
interleaved_rank      4           2.000000           -0.009481           -0.001803             -0.007458             -0.006064
     testpattern      9           1.444444           -0.009366            0.001177              0.000057             -0.001846
         weekday      3           1.000000           -0.010636            0.001749             -0.011185             -0.010441
            tail      3           1.000000           -0.005300            0.000594              0.002373             -0.003521

## 4. Top validation masks

          scheme              mask   n     base      w01      w02  w03_noq3_q2w02  raw_graph_noq3  validated_block  w02_minus_w01  w03_minus_w02  graph_minus_w02  block_minus_w02  public_match_score
     testpattern      testpattern4 250 0.694551 0.673978 0.660526        0.659559        0.650612         0.647182      -0.013452      -0.000968        -0.009914        -0.013345                   2
interleaved_rank interleaved_rank1 250 0.687139 0.676490 0.667380        0.666765        0.655534         0.657660      -0.009110      -0.000615        -0.011846        -0.009720                   2
interleaved_rank interleaved_rank3 250 0.688896 0.672321 0.661246        0.659281        0.652411         0.652354      -0.011075      -0.001965        -0.008835        -0.008892                   2
     testpattern      testpattern0 250 0.669530 0.660861 0.653234        0.650891        0.644752         0.644549      -0.007626      -0.002343        -0.008482        -0.008685                   2
interleaved_rank interleaved_rank0 250 0.679060 0.665885 0.656118        0.652785        0.649465         0.650000      -0.009767      -0.003333        -0.006653        -0.006117                   2
interleaved_rank interleaved_rank2 250 0.679543 0.670104 0.662132        0.660832        0.659632         0.662604      -0.007972      -0.001300        -0.002500         0.000472                   2
     testpattern      testpattern3 250 0.670699 0.661753 0.654003        0.651287        0.652644         0.654815      -0.007750      -0.002716        -0.001359         0.000812                   2
     testpattern      testpattern1 250 0.671266 0.662446 0.654739        0.652929        0.661688         0.661405      -0.007707      -0.001810         0.006949         0.006666                   2
         weekday          weekday2 250 0.681303 0.663411 0.651434        0.652731        0.632498         0.633184      -0.011977       0.001297        -0.018936        -0.018250                   1
         weekday          weekday0 250 0.676838 0.665130 0.655625        0.657477        0.644781         0.643909      -0.009505       0.001853        -0.010844        -0.011716                   1
            tail          tail0.45 203 0.677795 0.669986 0.663265        0.664103        0.660466         0.657632      -0.006721       0.000838        -0.002798        -0.005633                   1
            tail          tail0.25 111 0.656414 0.651205 0.646846        0.647601        0.653865         0.643176      -0.004360       0.000755         0.007019        -0.003670                   1
     testpattern      testpattern6 250 0.682326 0.667136 0.656130        0.664010        0.656506         0.653212      -0.011006       0.007880         0.000375        -0.002918                   1
     testpattern      testpattern5 250 0.689559 0.671714 0.659276        0.662556        0.660432         0.656468      -0.012437       0.003280         0.001156        -0.002808                   1
         weekday          weekday1 250 0.679337 0.667181 0.656755        0.658853        0.652979         0.655398      -0.010425       0.002098        -0.003776        -0.001357                   1
            tail          tail0.36 163 0.667535 0.661861 0.657042        0.657231        0.659941         0.655783      -0.004819       0.000188         0.002898        -0.001259                   1
     testpattern              tail 163 0.667535 0.661861 0.657042        0.657231        0.659941         0.655783      -0.004819       0.000188         0.002898        -0.001259                   1
     testpattern      testpattern2 250 0.684155 0.671312 0.660901        0.665516        0.660267         0.659924      -0.010410       0.004615        -0.000635        -0.000978                   1
     testpattern      testpattern7 250 0.674824 0.663105 0.654015        0.656479        0.663538         0.659920      -0.009089       0.002463         0.009523         0.005905                   1

## 5. Targetwise score on most public-like masks

candidate     base  raw_graph_noq3  validated_block      w01      w02  w03_noq3_q2w02
target                                                                               
Q1        0.689114        0.686562         0.689114 0.683809 0.680114        0.677467
Q2        0.722995        0.678058         0.678058 0.713684 0.705526        0.705526
Q3        0.722854        0.722854         0.722854 0.709578 0.698798        0.722854
S1        0.651934        0.605022         0.605022 0.636617 0.624312        0.614186
S2        0.670215        0.623359         0.623359 0.645269 0.629722        0.618119
S3        0.641164        0.596020         0.596020 0.627850 0.615975        0.605448
S4        0.662322        0.661523         0.662322 0.659051 0.656260        0.653937

## 6. Initial conclusions

- Test rows are evaluated through the split forensic summary above; inspect neighbor shares and tail share before trusting graph.
- A validation scheme is credible only if it reproduces public fact w02 < w01.
- Component choice must be targetwise: graph/block should not be applied uniformly to every target.
- New submissions should be built from the targets where graph/block wins under public-like schemes, not from global blend search.