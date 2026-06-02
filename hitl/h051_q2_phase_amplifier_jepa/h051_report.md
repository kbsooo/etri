# H051 Q2 Phase Amplifier HS-JEPA

Question: after H042's Q2-only public win and H050's non-Q2 neutral result, is the H042 Q2 direction under-amplified?

Design:

- base = H042 current public best;
- freeze every target except Q2;
- keep exactly H042's 45-cell Q2 support;
- move those cells farther in the same logit direction;
- selected public sensor = factor `2.0`, because H042's promoted file was the `s=0.5` phase and this tests the full-step interpretation.

Decision:

| decision | selected_candidate_id | selected_file | selected_resolved_path | root_uploadsafe_path | reason | public_anchor | public_anchor_lb | h050_public_lb | expected_relation | candidate_id | family | parameter | effective_h042_factor | changed_cells_vs_h042 | q2_changed_cells_vs_h042 | support_overlap_cells | same_direction_rate | mean_abs_prob_move_vs_h042 | max_abs_prob_move_vs_h042 | max_abs_extra_logit | curvature_risk | edge_rate | linear_expected_lb | linear_expected_gain_vs_h042 | h050_neutral_guard | h051_sensor_priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote | h051_fullsupport_logitline_f2p0_5ab4e605 | submission_h051_fullsupport_logitline_f2p0_5ab4e605.csv | /Users/kbsoo/Downloads/cl2/hitl/h051_q2_phase_amplifier_jepa/submission_h051_fullsupport_logitline_f2p0_5ab4e605.csv | /Users/kbsoo/Downloads/cl2/submission_h051_q2_phase_amp_f2p0_5ab4e605_uploadsafe.csv | H042 exact-support Q2 phase full-step amplifier | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.567904825 | beats H042 if H042 was an under-amplified hidden Q2 label phase; fails if H042 was only a local support-specific correction | h051_fullsupport_logitline_f2p0_5ab4e605 | fullsupport_logitline | f2p0 | 2.000000000 | 45 | 45 | 45 | 1.000000000 | 0.018088685 | 0.033284941 | 0.223839854 | 0.008272287 | 0.000000000 | 0.567686167 | -0.000218658 | 0.000000000 | 0.000193841 |

Support summary:

- H012 public LB: `0.5681234831`
- H042 public LB: `0.5679048248`
- H050 public LB treated as: `0.5679048248`
- H042 improvement vs H012: `-0.0002186583`
- H050 delta vs H042: `0.0000000000`
- H042 Q2 support cells: `45`
- H042 support positive/negative directions: `23` / `22`

Top candidates:

| candidate_id | family | parameter | effective_h042_factor | changed_cells_vs_h042 | same_direction_rate | mean_abs_prob_move_vs_h042 | max_abs_prob_move_vs_h042 | edge_rate | linear_expected_lb | linear_expected_gain_vs_h042 | curvature_risk | h051_sensor_priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h051_fullsupport_logitline_f2p0_5ab4e605 | fullsupport_logitline | f2p0 | 2.000000000 | 45 | 1.000000000 | 0.018088685 | 0.033284941 | 0.000000000 | 0.567686167 | -0.000218658 | 0.008272287 | 0.000193841 |
| h051_fullsupport_logitline_f2p25_d930c677 | fullsupport_logitline | f2p25 | 2.250000000 | 45 | 1.000000000 | 0.022563641 | 0.041519884 | 0.000000000 | 0.567631502 | -0.000273323 | 0.012925449 | 0.000184547 |
| h051_fullsupport_logitline_f2p5_6920d0fc | fullsupport_logitline | f2p5 | 2.500000000 | 45 | 1.000000000 | 0.027017970 | 0.049711464 | 0.000000000 | 0.567576837 | -0.000327987 | 0.018612646 | 0.000172150 |
| h051_top35_logitline_f2p5_9266643a | top35_logitline | f2p5 | 1.944444444 | 35 | 1.000000000 | 0.024451374 | 0.049711464 | 0.000000000 | 0.567698314 | -0.000206511 | 0.017811629 | 0.000141965 |
| h051_fullsupport_logitline_f3p0_d7d1d9d6 | fullsupport_logitline | f3p0 | 3.000000000 | 45 | 1.000000000 | 0.035861480 | 0.065947571 | 0.000000000 | 0.567467508 | -0.000437317 | 0.033089149 | 0.000138049 |
| h051_top35_logitline_f3p0_6abf01a5 | top35_logitline | f3p0 | 2.333333333 | 35 | 1.000000000 | 0.032437896 | 0.065947571 | 0.000000000 | 0.567613280 | -0.000291544 | 0.031665118 | 0.000129882 |
| h051_fullsupport_logitline_f1p75_0051acdf | fullsupport_logitline | f1p75 | 1.750000000 | 45 | 1.000000000 | 0.013593953 | 0.025010996 | 0.000000000 | 0.567740831 | -0.000163994 | 0.004653162 | 0.000100034 |
| h051_fullsupport_logitline_f3p5_1e468420 | fullsupport_logitline | f3p5 | 3.500000000 | 45 | 1.000000000 | 0.044612938 | 0.081960415 | 0.000000000 | 0.567358179 | -0.000546646 | 0.051701795 | 0.000091540 |
| h051_fullsupport_logitline_f4p0_d8a9587d | fullsupport_logitline | f4p0 | 4.000000000 | 45 | 1.000000000 | 0.053266472 | 0.097719041 | 0.022222222 | 0.567248850 | -0.000655975 | 0.074450585 | 0.000010401 |
| h051_top35_logitline_f2p0_33952d5f | top35_logitline | f2p0 | 1.555555556 | 35 | 1.000000000 | 0.016378418 | 0.033284941 | 0.000000000 | 0.567783348 | -0.000121477 | 0.007916280 | 0.000008839 |
| h051_fullsupport_logitline_f1p5_6deee3e8 | fullsupport_logitline | f1p5 | 1.500000000 | 45 | 1.000000000 | 0.009080321 | 0.016951214 | 0.000000000 | 0.567795496 | -0.000109329 | 0.002068072 | 0.000003125 |
| h051_top25_logitline_f3p0_3cb04031 | top25_logitline | f3p0 | 1.666666667 | 25 | 1.000000000 | 0.026440663 | 0.065947571 | 0.000000000 | 0.567759053 | -0.000145772 | 0.027959493 | -0.000004773 |
| h051_top25_logitline_f2p5_a6932b86 | top25_logitline | f2p5 | 1.388888889 | 25 | 1.000000000 | 0.019933201 | 0.049711464 | 0.000000000 | 0.567819791 | -0.000085034 | 0.015727215 | -0.000084370 |
| h051_fullsupport_logitline_f1p25_14f957ae | fullsupport_logitline | f1p25 | 1.250000000 | 45 | 1.000000000 | 0.004548693 | 0.008624461 | 0.000000000 | 0.567850160 | -0.000054665 | 0.000517018 | -0.000096886 |
| h051_top25_logitline_f2p0_b9697f81 | top25_logitline | f2p0 | 1.111111111 | 25 | 1.000000000 | 0.013353090 | 0.033284941 | 0.000000000 | 0.567880529 | -0.000024295 | 0.006989873 | -0.000174452 |
| h051_top15_logitline_f3p0_ed72f7aa | top15_logitline | f3p0 | 1.000000000 | 15 | 1.000000000 | 0.017970490 | 0.065947571 | 0.000000000 | 0.567904825 | 0.000000000 | 0.021756901 | -0.000265271 |
| h051_top15_logitline_f2p5_6ec61e1c | top15_logitline | f2p5 | 0.833333333 | 15 | 1.000000000 | 0.013581853 | 0.049711464 | 0.000000000 | 0.567941268 | 0.000036443 | 0.012238257 | -0.000306491 |
| h051_top15_logitline_f2p0_48d2d45c | top15_logitline | f2p0 | 0.666666667 | 15 | 1.000000000 | 0.009120652 | 0.033284941 | 0.000000000 | 0.567977711 | 0.000072886 | 0.005439225 | -0.000355870 |
| h051_fullsupport_edgepush_edge0p82_mix0p35_0fca88cf | fullsupport_edgepush | edge0p82_mix0p35 | 4.805234980 | 45 | 1.000000000 | 0.096009891 | 0.210928732 | 0.000000000 | 0.567072779 | -0.000832046 | 0.228067523 | -0.000413203 |
| h051_fullsupport_edgepush_edge0p88_mix0p35_582a0694 | fullsupport_edgepush | edge0p88_mix0p35 | 5.825830500 | 45 | 1.000000000 | 0.116709818 | 0.231928732 | 0.000000000 | 0.566849617 | -0.001055208 | 0.313536593 | -0.000650568 |

Interpretation rule:

- If H051 improves materially, HS-JEPA should treat Q2 phase as a recoverable hidden label route and search stronger exact-support / label-edge solutions.
- If H051 is worse, H042 is not an under-amplified direction; it is a shallow local correction, and future Q2 work should focus on support identity or public-subset assignment rather than amplitude.
