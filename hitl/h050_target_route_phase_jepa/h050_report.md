# H050 Target-Route Phase Residual HS-JEPA

Question: after the H042 Q2 phase win, do non-Q2 target routes have their own public-relevant residual phase?

Design:

- base = H042 current public best;
- freeze Q2 exactly;
- generate Q1/Q3/S1-S4 target-phase actions from route/world/posterior sources;
- score with H042 action decoder after adding H042 public feedback, route-world equation, H024, and H025.

Decision:

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | root_uploadsafe_path | reason | expected_relation | source | target_group | k | alpha | agree_only | changed_cells_vs_h012 | changed_cells_vs_h042 | non_q2_changed_cells_vs_h042 | route_equation_delta_vs_h012 | route_delta_gain_vs_h042 | h036world_delta_vs_h012 | full_known_action_margin_vs_h012_median | full_known_action_support_better_than_h012 | pre_h012_action_margin_vs_h012_median | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | h050_target_route_score | h050_worldview_promotable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote | True | h050_target_phase_route_world_mid_Q_k96_a0.3_agree_b140216b | submission_h050_target_phase_route_world_mid_Q_k96_a0.3_agree_b140216b.csv | /Users/kbsoo/Downloads/cl2/hitl/h050_target_route_phase_jepa/submission_h050_target_phase_route_world_mid_Q_k96_a0.3_agree_b140216b.csv | /Users/kbsoo/Downloads/cl2/submission_h050_target_route_phase_b140216b_uploadsafe.csv | target-route residual gate passed | beats H042 only if non-Q2 target-route phase exists after Q2 is frozen | route_world_mid | Q | 96 | 0.300000000 | True | 141 | 96 | 96 | -0.000444205 | -0.000303538 | -0.000166506 | -0.000050859 | 0.583333333 | 0.000036495 | 0.001857507 | 0.250000000 | 0.377968233 | 1.034000000 | True |

Top decoder fits after adding H042 public feedback:

| feature_set | alpha | n_features | loo_mae | loo_rmse | loo_spearman | loo_pair_acc |
| --- | --- | --- | --- | --- | --- | --- |
| coords_plus_world | 0.010000000 | 47 | 0.000064714 | 0.000094941 | 0.998870695 | 0.995670996 |
| coords_plus_world | 0.100000000 | 47 | 0.000071062 | 0.000105010 | 0.995482778 | 0.987012987 |
| coords_plus_world | 1.000000000 | 47 | 0.000167034 | 0.000206406 | 0.994353473 | 0.982683983 |
| compact | 0.010000000 | 41 | 0.000203027 | 0.000341300 | 0.985319029 | 0.965367965 |
| compact | 1.000000000 | 41 | 0.000213091 | 0.000298138 | 0.964991530 | 0.939393939 |
| compact | 0.100000000 | 41 | 0.000254054 | 0.000414682 | 0.967250141 | 0.943722944 |
| coords_cos_compact | 1.000000000 | 115 | 0.000345944 | 0.000660439 | 0.966120836 | 0.943722944 |
| compact | 10.000000000 | 41 | 0.000383649 | 0.000514844 | 0.961603614 | 0.935064935 |

Top candidates:

| candidate_id | source | target_group | k | alpha | changed_cells_vs_h042 | route_delta_gain_vs_h042 | route_equation_delta_vs_h012 | full_known_action_margin_vs_h012_median | full_known_action_support_better_than_h012 | pre_h012_h024_margin_vs_h012_median | h025_score | h050_target_route_score | h050_worldview_promotable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h050_target_phase_route_world_mid_Q_k96_a0.3_agree_b140216b | route_world_mid | Q | 96 | 0.300000000 | 96 | -0.000303538 | -0.000444205 | -0.000050859 | 0.583333333 | 0.001857507 | 0.377968233 | 1.034000000 | True |
| h050_target_phase_route_world_mid_Q_k96_a0.19_free_92d30f84 | route_world_mid | Q | 96 | 0.190000000 | 96 | -0.000240842 | -0.000381510 | -0.000144805 | 0.583333333 | 0.001447063 | 0.180212447 | 1.040750000 | True |
| h050_target_phase_route_phase_S24_k220_a0.19_free_b9ef15c3 | route_phase | S24 | 220 | 0.190000000 | 220 | -0.000286834 | -0.000427502 | -0.000042186 | 0.583333333 | 0.001937366 | -3.635658712 | 1.060000000 | True |
| h050_target_phase_route_phase_S24_k220_a0.19_agree_219a9e83 | route_phase | S24 | 220 | 0.190000000 | 220 | -0.000259200 | -0.000399868 | -0.000041365 | 0.583333333 | 0.001909743 | -3.978483130 | 1.071333333 | True |
| h050_target_phase_route_world_mid_S24_k150_a0.19_free_e8680162 | route_world_mid | S24 | 150 | 0.190000000 | 150 | -0.000313524 | -0.000454192 | 0.000027118 | 0.500000000 | 0.002119776 | -4.518126464 | 1.080750000 | True |
| h050_target_phase_route_world_mid_S24_k220_a0.12_agree_5415fb9b | route_world_mid | S24 | 220 | 0.120000000 | 220 | -0.000212159 | -0.000352827 | -0.000135689 | 0.583333333 | 0.001338169 | -3.688258819 | 1.105916667 | True |
| h050_target_phase_route_phase_S24_k150_a0.19_free_aad8a7e2 | route_phase | S24 | 150 | 0.190000000 | 150 | -0.000248564 | -0.000389232 | -0.000025482 | 0.583333333 | 0.001903130 | -4.212009574 | 1.113000000 | True |
| h050_target_phase_route_phase_Q_k96_a0.3_agree_4b87a45d | route_phase | Q | 96 | 0.300000000 | 96 | -0.000245454 | -0.000386122 | -0.000073431 | 0.583333333 | 0.001803440 | 0.372889693 | 1.149333333 | True |
| h050_target_phase_route_world_mid_Q_k56_a0.3_agree_7e418f23 | route_world_mid | Q | 56 | 0.300000000 | 56 | -0.000249846 | -0.000390514 | -0.000061004 | 0.583333333 | 0.001814614 | -0.128551232 | 1.182833333 | True |
| h050_target_phase_route_world_mid_Q3S_k220_a0.075_free_d0795d39 | route_world_mid | Q3S | 220 | 0.075000000 | 220 | -0.000225487 | -0.000366154 | -0.000000824 | 0.500000000 | 0.001456256 | -4.876012802 | 1.191750000 | True |
| h050_target_phase_posterior_mid_S24_k220_a0.19_free_65b63677 | posterior_mid | S24 | 220 | 0.190000000 | 220 | -0.000221990 | -0.000362658 | -0.000073066 | 0.583333333 | 0.001773081 | -3.945612548 | 1.210500000 | True |
| h050_target_phase_world_phase_S24_k220_a0.19_free_670c89ed | world_phase | S24 | 220 | 0.190000000 | 220 | -0.000185752 | -0.000326420 | -0.000098584 | 0.583333333 | 0.001577206 | -4.031715073 | 1.216583333 | True |
| h050_target_phase_route_world_mid_Q_k96_a0.19_agree_14bfadd7 | route_world_mid | Q | 96 | 0.190000000 | 96 | -0.000206613 | -0.000347281 | -0.000136172 | 0.583333333 | 0.001429074 | 0.389913147 | 1.224500000 | True |
| h050_large_route_phase_route_world_mid_Q3S_k260_a0.075_agree_8b1003cf | route_world_mid | Q3S | 260 | 0.075000000 | 260 | -0.000240383 | -0.000381051 | 0.000000534 | 0.500000000 | 0.001473006 | -3.907357073 | 1.225750000 | True |
| h050_target_phase_posterior_mid_S24_k220_a0.19_agree_7c7b5f61 | posterior_mid | S24 | 220 | 0.190000000 | 220 | -0.000208248 | -0.000348916 | -0.000073750 | 0.583333333 | 0.001754005 | -4.210854996 | 1.227500000 | True |
| h050_target_phase_route_phase_S24_k150_a0.19_agree_aadaf51c | route_phase | S24 | 150 | 0.190000000 | 150 | -0.000237071 | -0.000377739 | -0.000023371 | 0.500000000 | 0.001910479 | -3.622146596 | 1.229000000 | True |
| h050_target_phase_route_world_mid_S24_k150_a0.12_agree_17b52fd2 | route_world_mid | S24 | 150 | 0.120000000 | 150 | -0.000194824 | -0.000335492 | -0.000123938 | 0.583333333 | 0.001381655 | -3.621831058 | 1.230083333 | True |
| h050_target_phase_route_phase_Q_k96_a0.19_free_a95a0a15 | route_phase | Q | 96 | 0.190000000 | 96 | -0.000186824 | -0.000327492 | -0.000167470 | 0.666666667 | 0.001304256 | 0.083322847 | 1.233583333 | True |
| h050_target_phase_world_phase_S24_k220_a0.19_agree_80f76dc6 | world_phase | S24 | 220 | 0.190000000 | 220 | -0.000172925 | -0.000313593 | -0.000095898 | 0.583333333 | 0.001572350 | -3.832299040 | 1.257833333 | True |
| h050_target_phase_route_world_mid_Q3S_k220_a0.075_agree_3edc4e77 | route_world_mid | Q3S | 220 | 0.075000000 | 220 | -0.000217622 | -0.000358290 | 0.000000671 | 0.500000000 | 0.001445404 | -4.473587753 | 1.284583333 | True |

Interpretation rule:

- If the promoted file improves public LB, HS-JEPA needs target-specific action routes beyond Q2.
- If it fails materially, H042 remains a Q2-local phase result and non-Q2 action should require an independent route signal.
