# H052 Q2 Binary-Edge HS-JEPA

Question: if H051's linear Q2 amplification is right, is the next state a stronger binary edge on the same hidden Q2 support?

Design:

- base = H042 current public best;
- Q1/Q3/S targets are frozen;
- selected branch keeps H042's exact `45` Q2 support;
- each selected Q2 cell is pulled toward `0.88` if H042 moved it upward and toward `0.12` if H042 moved it downward;
- mix is `0.35`, so this is a binary-edge sensor rather than a full saturation file.

Decision:

| decision | selected_candidate_id | selected_file | selected_resolved_path | root_uploadsafe_path | reason | public_anchor | public_anchor_lb | h050_public_lb | h051_dependency | expected_relation | candidate_id | support_name | edge | mix | changed_cells_vs_h042 | q2_changed_cells_vs_h042 | selected_support_cells | same_direction_rate | extra_direction_rate | mean_support_posterior | min_support_posterior | mean_abs_prob_move_vs_h042 | max_abs_prob_move_vs_h042 | curvature_risk | edge_rate | effective_h042_factor | linear_expected_lb | linear_expected_gain_vs_h042 | h052_binary_edge_priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conditional_promote_after_h051_positive | h052_exact45_edge0p88_mix0p35_582a0694 | submission_h052_exact45_edge0p88_mix0p35_582a0694.csv | /Users/kbsoo/Downloads/cl2/hitl/h052_q2_binary_edge_jepa/submission_h052_exact45_edge0p88_mix0p35_582a0694.csv | /Users/kbsoo/Downloads/cl2/submission_h052_q2_binary_edge_0p88m35_582a0694_uploadsafe.csv | Q2 exact-support binary-edge branch | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.567904825 | submission_h051_q2_phase_amp_f2p0_5ab4e605_uploadsafe.csv | submit after H051 only if H051 improves; beats H042 if Q2 phase is a binary hidden-label edge rather than a smooth calibration vector | h052_exact45_edge0p88_mix0p35_582a0694 | exact45 | 0.880000000 | 0.350000000 | 45 | 45 | 45 | 1.000000000 | 1.000000000 | 0.688528000 | 0.374920000 | 0.116709818 | 0.231928732 | 0.313536593 | 0.000000000 | 5.825830500 | 0.566849617 | -0.001055208 | 0.000732019 |

Public-anchor context:

- H012 public LB: `0.5681234831`
- H042 public LB: `0.5679048248`
- H050 public LB: `0.5679048248`
- H050 max Q2 delta vs H042: `0.000000000000` (Q2 was frozen)
- H051 extra Q2 mean/max abs move vs H042: `0.018088685` / `0.033284941`

Top candidates:

| candidate_id | support_name | edge | mix | selected_support_cells | mean_support_posterior | min_support_posterior | same_direction_rate | extra_direction_rate | mean_abs_prob_move_vs_h042 | max_abs_prob_move_vs_h042 | curvature_risk | edge_rate | effective_h042_factor | linear_expected_lb | linear_expected_gain_vs_h042 | h052_binary_edge_priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h052_post_high060_edge0p93_mix0p35_272a4f4c | post_high060 | 0.930000000 | 0.350000000 | 31 | 0.760015484 | 0.602320000 | 1.000000000 | 1.000000000 | 0.136718948 | 0.249428732 | 0.421153415 | 0.000000000 | 6.706411827 | 0.566657070 | -0.001247754 | 0.000806028 |
| h052_exact45_edge0p93_mix0p35_aa04c835 | exact45 | 0.930000000 | 0.350000000 | 45 | 0.688528000 | 0.374920000 | 1.000000000 | 1.000000000 | 0.134209818 | 0.249428732 | 0.403487807 | 0.000000000 | 6.713233248 | 0.566655579 | -0.001249246 | 0.000791130 |
| h052_post_top35_edge0p93_mix0p35_a95e3b34 | post_top35 | 0.930000000 | 0.350000000 | 35 | 0.722844571 | 0.487960000 | 1.000000000 | 1.000000000 | 0.128460314 | 0.249428732 | 0.384071986 | 0.000000000 | 6.397083739 | 0.566724708 | -0.001180117 | 0.000782312 |
| h052_post_high060_edge0p93_mix0p25_59dc33f7 | post_high060 | 0.930000000 | 0.250000000 | 31 | 0.760015484 | 0.602320000 | 1.000000000 | 1.000000000 | 0.097656391 | 0.178163380 | 0.216189256 | 0.000000000 | 5.036051389 | 0.567022309 | -0.000882516 | 0.000748236 |
| h052_post_high060_edge0p88_mix0p35_1ee1eb34 | post_high060 | 0.880000000 | 0.350000000 | 31 | 0.760015484 | 0.602320000 | 1.000000000 | 1.000000000 | 0.119218948 | 0.231928732 | 0.330006737 | 0.000000000 | 5.808452829 | 0.566853417 | -0.001051408 | 0.000746402 |
| h052_exact45_edge0p88_mix0p35_582a0694 | exact45 | 0.880000000 | 0.350000000 | 45 | 0.688528000 | 0.374920000 | 1.000000000 | 1.000000000 | 0.116709818 | 0.231928732 | 0.313536593 | 0.000000000 | 5.825830500 | 0.566849617 | -0.001055208 | 0.000732019 |
| h052_post_top35_edge0p88_mix0p35_1f1ba482 | post_top35 | 0.880000000 | 0.350000000 | 35 | 0.722844571 | 0.487960000 | 1.000000000 | 1.000000000 | 0.110960314 | 0.231928732 | 0.295692045 | 0.000000000 | 5.527003693 | 0.566914958 | -0.000989867 | 0.000724632 |
| h052_exact45_edge0p93_mix0p25_83f56bc2 | exact45 | 0.930000000 | 0.250000000 | 45 | 0.688528000 | 0.374920000 | 1.000000000 | 1.000000000 | 0.095864156 | 0.178163380 | 0.206132553 | 0.000000000 | 5.037505969 | 0.567021991 | -0.000882834 | 0.000720751 |
| h052_post_top35_edge0p93_mix0p25_eeee7216 | post_top35 | 0.930000000 | 0.250000000 | 35 | 0.722844571 | 0.487960000 | 1.000000000 | 1.000000000 | 0.091757367 | 0.178163380 | 0.196059084 | 0.000000000 | 4.813705058 | 0.567070927 | -0.000833898 | 0.000718113 |
| h052_exact45_edge0p88_mix0p5_05dcc99d | exact45 | 0.880000000 | 0.500000000 | 45 | 0.688528000 | 0.374920000 | 1.000000000 | 1.000000000 | 0.166728312 | 0.331326760 | 0.647098833 | 0.000000000 | 8.018759268 | 0.566370115 | -0.001534710 | 0.000711178 |
| h052_post_top35_edge0p88_mix0p5_31c6a81a | post_top35 | 0.880000000 | 0.500000000 | 35 | 0.722844571 | 0.487960000 | 1.000000000 | 1.000000000 | 0.158514734 | 0.331326760 | 0.610233419 | 0.000000000 | 7.581744594 | 0.566465672 | -0.001439153 | 0.000702106 |
| h052_post_high060_edge0p88_mix0p5_6da22e61 | post_high060 | 0.880000000 | 0.500000000 | 31 | 0.760015484 | 0.602320000 | 1.000000000 | 1.000000000 | 0.170312783 | 0.331326760 | 0.677508456 | 0.000000000 | 7.985241694 | 0.566377444 | -0.001527381 | 0.000701122 |
| h052_exact45_edge0p93_mix0p5_d57cf38a | exact45 | 0.930000000 | 0.500000000 | 45 | 0.688528000 | 0.374920000 | 1.000000000 | 1.000000000 | 0.191728312 | 0.356326760 | 0.850886991 | 0.022222222 | 9.406208842 | 0.566066737 | -0.001838087 | 0.000701095 |
| h052_post_top25_edge0p93_mix0p35_d5add60e | post_top25 | 0.930000000 | 0.350000000 | 25 | 0.773257600 | 0.487960000 | 1.000000000 | 1.000000000 | 0.139736047 | 0.249428732 | 0.419472839 | 0.000000000 | 6.172932324 | 0.566773720 | -0.001131105 | 0.000692802 |
| h052_post_top35_edge0p93_mix0p5_5d90bf36 | post_top35 | 0.930000000 | 0.500000000 | 35 | 0.722844571 | 0.487960000 | 1.000000000 | 1.000000000 | 0.183514734 | 0.356326760 | 0.810766951 | 0.028571429 | 8.941856450 | 0.566168272 | -0.001736553 | 0.000688706 |
| h052_post_high060_edge0p93_mix0p5_49af73db | post_high060 | 0.930000000 | 0.500000000 | 31 | 0.760015484 | 0.602320000 | 1.000000000 | 1.000000000 | 0.195312783 | 0.356326760 | 0.883107088 | 0.032258065 | 9.387589211 | 0.566070809 | -0.001834016 | 0.000688069 |
| h052_post_high060_edge0p88_mix0p25_b536c27e | post_high060 | 0.880000000 | 0.250000000 | 31 | 0.760015484 | 0.602320000 | 1.000000000 | 1.000000000 | 0.085156391 | 0.165663380 | 0.171148567 | 0.000000000 | 4.420936639 | 0.567156809 | -0.000748016 | 0.000681297 |
| h052_post_top25_edge0p93_mix0p25_93d75690 | post_top25 | 0.930000000 | 0.250000000 | 25 | 0.773257600 | 0.487960000 | 1.000000000 | 1.000000000 | 0.099811462 | 0.178163380 | 0.214281457 | 0.000000000 | 4.655368139 | 0.567105548 | -0.000799277 | 0.000668761 |
| h052_post_top25_edge0p88_mix0p35_bbd84abf | post_top25 | 0.880000000 | 0.350000000 | 25 | 0.773257600 | 0.487960000 | 1.000000000 | 1.000000000 | 0.122236047 | 0.231928732 | 0.328168288 | 0.000000000 | 5.390917433 | 0.566944714 | -0.000960111 | 0.000658765 |
| h052_exact45_edge0p88_mix0p25_360dc752 | exact45 | 0.880000000 | 0.250000000 | 45 | 0.688528000 | 0.374920000 | 1.000000000 | 1.000000000 | 0.083364156 | 0.165663380 | 0.161874664 | 0.000000000 | 4.429969564 | 0.567154833 | -0.000749991 | 0.000654295 |

Interpretation rule:

- If H051 improves and H052 also improves, HS-JEPA should model Q2 as a hidden binary action-label edge, not as ordinary calibration.
- If H051 improves but H052 fails, Q2 is amplitude-linear but not label-edge.
- If H051 fails, do not submit H052; the entire amplitude/edge branch is killed and support/public-subset assignment should take priority.
