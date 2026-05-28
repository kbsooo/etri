# JEPA Direction Ensemble Combo Stress Audit

This scores the new direction-ensemble candidates on every inverse public scenario/mask combo instead of trusting only the averaged actual-anchor score.

## Overall Pairwise Summary

```
       candidate                                                    file  weighted_mean_score  weighted_delta_vs_b01_ladder  weighted_win_rate_vs_b01_ladder  p50_delta_vs_b01_ladder  p90_delta_vs_b01_ladder  worst_delta_vs_b01_ladder  weighted_delta_vs_898_ladder  weighted_win_rate_vs_898_ladder  weighted_delta_vs_a2c8
     direns_c4af                          submission_direns_c4af1fd8.csv             0.577602                     -0.000011                         0.634403                -0.000021                 0.000007                   0.000035                     -0.000009                         0.542311               -0.000182
     direns_c0fd                          submission_direns_c0fdb76b.csv             0.577603                     -0.000010                         0.573273                -0.000029                 0.000022                   0.000059                     -0.000008                         0.538448               -0.000181
     direns_24a9                          submission_direns_24a92ca1.csv             0.577604                     -0.000010                         0.579504                -0.000027                 0.000023                   0.000071                     -0.000008                         0.538448               -0.000180
     direns_1e0f                          submission_direns_1e0f159d.csv             0.577604                     -0.000009                         0.546409                -0.000035                 0.000031                   0.000070                     -0.000008                         0.538448               -0.000180
     direns_81cc                          submission_direns_81cca594.csv             0.577604                     -0.000009                         0.542311                -0.000034                 0.000029                   0.000061                     -0.000007                         0.542311               -0.000180
     direns_2a96                          submission_direns_2a96ae73.csv             0.577605                     -0.000009                         0.562397                -0.000043                 0.000044                   0.000101                     -0.000007                         0.534752               -0.000179
      898_ladder                    submission_sparseladder_89817541.csv             0.577612                     -0.000002                         0.461552                 0.000037                 0.000048                   0.000056                      0.000000                         0.000000               -0.000172
      b01_ladder                    submission_sparseladder_b01acaa1.csv             0.577614                      0.000000                         0.000000                 0.000000                 0.000000                   0.000000                      0.000002                         0.538448               -0.000171
  blockorth_3a28                       submission_blockorth_3a28f87f.csv             0.577619                      0.000006                         0.544404                -0.000011                 0.000039                   0.000103                      0.000007                         0.538614               -0.000165
     direns_652c                          submission_direns_652cd2ca.csv             0.577619                      0.000006                         0.413882                 0.000022                 0.000030                   0.000067                      0.000008                         0.546207               -0.000165
       f1ee_noq2                    submission_sparseladder_f1ee16b0.csv             0.577623                      0.000009                         0.154137                 0.000010                 0.000020                   0.000097                      0.000011                         0.550665               -0.000162
  target_q3stage                       submission_targetabl_b19056bb.csv             0.577638                      0.000024                         0.534752                -0.000181                 0.000320                   0.000513                      0.000026                         0.534752               -0.000146
direns_b096_orth                          submission_direns_b0962ff8.csv             0.577651                      0.000038                         0.534752                -0.000037                 0.000154                   0.000301                      0.000040                         0.534752               -0.000133
            a2c8          submission_frontier_cvjepa_refine_a2c8d2c8.csv             0.577784                      0.000171                         0.534752                -0.000292                 0.000819                   0.001108                      0.000172                         0.534752                0.000000
           raw05 submission_raw_timeline_jepa_rescue_strict_scale0p5.csv             0.577850                      0.000237                         0.534752                -0.000303                 0.000981                   0.001345                      0.000238                         0.534752                0.000066
```

## Per-Combo-Set Pairwise Summary

```
     candidate        combo_set  weighted_delta_vs_b01_ladder  weighted_win_rate_vs_b01_ladder  worst_delta_vs_b01_ladder  weighted_delta_vs_898_ladder
    898_ladder         all_sign                      0.000042                         0.019797               5.564690e-05                      0.000000
    898_ladder      inverse_top                     -0.000061                         1.000000              -2.505070e-05                      0.000000
    898_ladder raw05_compatible                      0.000013                         0.364858               5.564690e-05                      0.000000
    b01_ladder         all_sign                      0.000000                         0.000000               0.000000e+00                     -0.000042
    b01_ladder      inverse_top                      0.000000                         0.000000               0.000000e+00                      0.000061
    b01_ladder raw05_compatible                      0.000000                         0.000000               0.000000e+00                     -0.000013
blockorth_3a28         all_sign                     -0.000016                         0.973990               5.760920e-05                     -0.000058
blockorth_3a28      inverse_top                      0.000029                         0.006366               1.029013e-04                      0.000090
blockorth_3a28 raw05_compatible                      0.000003                         0.652857               7.880600e-05                     -0.000009
   direns_1e0f         all_sign                     -0.000039                         0.980203               4.813900e-06                     -0.000082
   direns_1e0f      inverse_top                      0.000028                         0.000000               4.778940e-05                      0.000089
   direns_1e0f raw05_compatible                     -0.000017                         0.659024               6.961450e-05                     -0.000029
   direns_24a9         all_sign                     -0.000033                         1.000000              -1.458460e-05                     -0.000076
   direns_24a9      inverse_top                      0.000020                         0.013659               3.241150e-05                      0.000081
   direns_24a9 raw05_compatible                     -0.000016                         0.724854               7.125530e-05                     -0.000029
   direns_2a96         all_sign                     -0.000048                         1.000000              -5.267000e-07                     -0.000090
   direns_2a96      inverse_top                      0.000039                         0.007204               6.924530e-05                      0.000100
   direns_2a96 raw05_compatible                     -0.000018                         0.679986               1.013082e-04                     -0.000031
   direns_652c         all_sign                      0.000025                         0.019797               4.018990e-05                     -0.000017
   direns_652c      inverse_top                     -0.000022                         0.993260               9.808000e-07                      0.000039
   direns_652c raw05_compatible                      0.000014                         0.228590               6.690030e-05                      0.000002
   direns_81cc         all_sign                     -0.000037                         0.980203               5.788600e-06                     -0.000080
   direns_81cc      inverse_top                      0.000026                         0.000000               4.177030e-05                      0.000087
   direns_81cc raw05_compatible                     -0.000016                         0.646730               6.105990e-05                     -0.000029
   direns_c0fd         all_sign                     -0.000034                         1.000000              -8.261500e-06                     -0.000076
   direns_c0fd      inverse_top                      0.000020                         0.007204               2.737150e-05                      0.000080
   direns_c0fd raw05_compatible                     -0.000017                         0.712613               5.851620e-05                     -0.000030
   direns_c4af         all_sign                     -0.000024                         1.000000              -1.274040e-05                     -0.000066
   direns_c4af      inverse_top                      0.000005                         0.045460               1.239660e-05                      0.000066
   direns_c4af raw05_compatible                     -0.000015                         0.857751               3.486450e-05                     -0.000027
```

## Interpretation

- A robust replacement for `b01_ladder` should have negative weighted delta, high weighted win rate, and non-positive or small p90/worst deltas versus `b01_ladder`.
- If a candidate improves only the weighted mean but loses many combo rows, it is likely another inverse-scenario averaging artifact.
- `898_ladder` remains the scale-stress reference; candidates that beat `b01_ladder` but lose badly to `898_ladder` are safer but lower-upside probes.
