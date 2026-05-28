# E60 Transition-Residual Block-State Probe

Question: does the hidden block state live in the transition residual from labeled flanks to the hidden run, rather than in within-block marginal or joint labels?

Decision gates:

- row LogLoss improves over E54 raw phone base;
- transition-residual MSE improves over raw phone base;
- S3 does not regress versus subject mean;
- real hidden-block expected mixmin delta versus a2c8 is negative.

Joint gates opened: `0`.

Best by row/raw stress:

| method | weighted_row_logloss | delta_weighted_row_logloss_vs_raw | delta_transition_residual_mse_vs_raw | s3_delta_vs_subject | weighted_mixmin_delta_vs_a2c8 | joint_gate |
| --- | --- | --- | --- | --- | --- | --- |
| raw_phone_base | 0.605269 | 0.000000 | 0.000000 | 0.007802 | 0.000311 | 0.000000 |
| transition_raw_residual_baseraw_k4_a24_w0.35 | 0.605455 | 0.000186 | -0.017074 | 0.007783 | 0.000230 | 0.000000 |
| transition_raw_residual_baseraw_k8_a24_w0.35 | 0.606542 | 0.001273 | -0.013787 | 0.007714 | 0.000243 | 0.000000 |
| transition_topology_baseraw_k4_a24_w0.35 | 0.607328 | 0.002059 | -0.104952 | 0.015478 | 0.000203 | 0.000000 |
| transition_raw_residual_baseraw_k4_a12_w0.35 | 0.607329 | 0.002060 | -0.012614 | 0.009107 | 0.000164 | 0.000000 |
| transition_raw_residual_baseraw_k16_a24_w0.35 | 0.607538 | 0.002269 | -0.112994 | 0.008407 | 0.000372 | 0.000000 |
| transition_raw_residual_baseraw_k4_a24_w0.65 | 0.607715 | 0.002447 | -0.010769 | 0.009390 | 0.000155 | 0.000000 |
| transition_full_transition_baseraw_k4_a24_w0.35 | 0.608108 | 0.002839 | 0.024872 | 0.014091 | 0.000265 | 0.000000 |
| transition_raw_topology_baseraw_k4_a24_w0.35 | 0.608868 | 0.003600 | -0.000440 | 0.013858 | 0.000247 | 0.000000 |
| transition_raw_residual_baseraw_k8_a12_w0.35 | 0.609598 | 0.004329 | 0.000996 | 0.009758 | 0.000206 | 0.000000 |
| transition_topology_baseraw_k8_a24_w0.35 | 0.610325 | 0.005057 | -0.120146 | 0.021743 | 0.000218 | 0.000000 |
| transition_raw_residual_baseraw_k16_a12_w0.35 | 0.610751 | 0.005483 | -0.138771 | 0.011195 | 0.000401 | 0.000000 |
| transition_full_transition_baseraw_k8_a24_w0.35 | 0.611009 | 0.005741 | 0.040370 | 0.017090 | 0.000334 | 0.000000 |
| transition_raw_residual_baseraw_k8_a24_w0.65 | 0.611417 | 0.006148 | 0.012626 | 0.011108 | 0.000192 | 0.000000 |

Best hidden mixmin alignment:

| method | weighted_mixmin_delta_vs_a2c8 | mean_mixmin_delta_vs_a2c8 | mixmin_better_block_rate |
| --- | --- | --- | --- |
| transition_raw_residual_baseedge_mid_k4_a4_w1.00 | -0.001569 | -0.002150 | 0.638889 |
| transition_raw_residual_baseedge_mid_k4_a4_w0.65 | -0.001503 | -0.002046 | 0.666667 |
| transition_raw_residual_baseedge_mid_k4_a12_w1.00 | -0.001445 | -0.001974 | 0.638889 |
| transition_full_transition_baseedge_mid_k16_a4_w1.00 | -0.001399 | -0.002162 | 0.611111 |
| transition_full_transition_baseedge_mid_k16_a12_w1.00 | -0.001381 | -0.002034 | 0.527778 |
| transition_raw_residual_baseedge_mid_k4_a4_w0.35 | -0.001378 | -0.001893 | 0.611111 |
| transition_full_transition_baseedge_mid_k16_a4_w0.65 | -0.001373 | -0.002008 | 0.527778 |
| transition_raw_residual_baseedge_mid_k4_a12_w0.65 | -0.001366 | -0.001879 | 0.611111 |
| transition_raw_topology_baseedge_mid_k16_a4_w1.00 | -0.001365 | -0.001813 | 0.555556 |
| transition_raw_topology_baseedge_mid_k16_a12_w1.00 | -0.001356 | -0.001797 | 0.555556 |
| transition_raw_topology_baseedge_mid_k16_a4_w0.65 | -0.001353 | -0.001794 | 0.555556 |
| transition_full_transition_baseedge_mid_k16_a24_w1.00 | -0.001351 | -0.001943 | 0.527778 |

Target stress for the best row/raw method:

| target | target_row_logloss | delta_row_vs_subject | delta_row_vs_raw |
| --- | --- | --- | --- |
| Q1 | 0.638011 | -0.010726 | 0.000000 |
| Q2 | 0.676538 | -0.017247 | 0.000000 |
| Q3 | 0.653038 | -0.016308 | 0.000000 |
| S1 | 0.567136 | -0.009910 | 0.000000 |
| S2 | 0.560021 | -0.006878 | 0.000000 |
| S3 | 0.510756 | 0.007802 | 0.000000 |
| S4 | 0.631380 | -0.000865 | 0.000000 |

Interpretation:

No transition-residual method survived the full gate. If row/raw recovery improves without hidden mixmin sign, transition structure is real but not enough to explain the current frontier.

Most informative rows:

- best row/raw method: `raw_phone_base`
- best hidden-sign method: `transition_raw_residual_baseedge_mid_k4_a4_w1.00`

Next action:

If no gate opens, use transition-residual features as non-anchor diagnostics for E56 teacher reliability rather than as direct probability movement.
