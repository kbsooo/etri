# Big-swing all-experiment report

Generated five structural candidate families: graph label propagation, joint label-state, subject-regime routing, cross-night episode, and SSL prototypes.

## Candidate movement summary
                                          file  mean_abs_vs_base  max_target_mean_abs_vs_base  mean_abs_vs_anchor  max_target_mean_abs_vs_anchor  mean_abs_vs_w03  max_target_mean_abs_vs_w03
        submission_big_graph_s_family_prob.csv          0.050913                     0.095368            0.043100                       0.074091         0.039039                    0.069296
      submission_big_graph_state_noq3_prob.csv          0.053110                     0.082500            0.038717                       0.060620         0.034516                    0.055864
    submission_big_crossnight_episode_prob.csv          0.040522                     0.081128            0.027092                       0.059327         0.025875                    0.054811
         submission_big_ssl_prototype_prob.csv          0.033657                     0.065728            0.024736                       0.056268         0.025315                    0.054822
  submission_big_subject_regime_graph_prob.csv          0.034808                     0.053317            0.019251                       0.028100         0.015825                    0.023660
submission_big_joint_label_state_noq3_prob.csv          0.020365                     0.030828            0.003834                       0.007760         0.009312                    0.015675

## Validation probe mean delta vs null
 family target  delta_vs_null
episode     Q1       0.001814
episode     Q2       0.077454
episode     Q3       0.074956
episode     S1       0.026331
episode     S2      -0.009007
episode     S3      -0.012787
episode     S4       0.054734
  graph     Q1      -0.012448
  graph     Q2      -0.014310
  graph     Q3      -0.014092
  graph     S1      -0.019567
  graph     S2      -0.025909
  graph     S3      -0.034726
  graph     S4      -0.028148
    ssl     Q1       0.021023
    ssl     Q2       0.033474
    ssl     Q3       0.004706
    ssl     S1       0.007844
    ssl     S2      -0.012125
    ssl     S3       0.020019
    ssl     S4       0.005178

## Notes
- These are high-variance candidates; movement size is intentional.
- Graph candidates are the cleanest structural state-completion test.
- Episode and SSL candidates are independent representation-family tests.
- Q3 is frozen in most files because prior diagnostics treated it as risky/unstable.