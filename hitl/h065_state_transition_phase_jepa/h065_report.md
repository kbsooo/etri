# H065 State-Transition Phase HS-JEPA

Question: are H057's neighboring same-subject rows copies of the seed state, or
pre/post transition phases that need different target routes?

Design:

- base: H057 public frontier;
- positive representation: H057's `45` full-vector state rows;
- context: H064 contrastive state graph plus H062/H063 expansion evidence;
- target representation: H061 post-H057 posterior `q061`;
- action: freeze Q2 and move only phase-specific non-Q2 target routes;
- route learning: derive separate pre/post target weights from near non-seed
  rows that both have expansion evidence and are close to H057 seeds.

Phase target weights:

| phase | target | mean_gain | phase_weight | rank | in_top3 | in_top4 | training_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| post | S4 | 0.002136261 | 1.000000000 | 1 | 1 | 1 | 24 |
| post | S2 | 0.001945513 | 0.910709433 | 2 | 1 | 1 | 24 |
| post | S3 | 0.001765123 | 0.826267716 | 3 | 1 | 1 | 24 |
| post | Q1 | 0.001622993 | 0.759735439 | 4 | 0 | 1 | 24 |
| post | S1 | 0.001266382 | 0.592803195 | 5 | 0 | 0 | 24 |
| post | Q3 | 0.000947389 | 0.443480144 | 6 | 0 | 0 | 24 |
| pre | Q3 | 0.001874735 | 1.000000000 | 1 | 1 | 1 | 15 |
| pre | S4 | 0.001725467 | 0.920379498 | 2 | 1 | 1 | 15 |
| pre | S2 | 0.001679454 | 0.895835428 | 3 | 1 | 1 | 15 |
| pre | S3 | 0.001389220 | 0.741022210 | 4 | 0 | 1 | 15 |
| pre | S1 | 0.000991786 | 0.529027231 | 5 | 0 | 0 | 15 |
| pre | Q1 | 0.000517023 | 0.275784911 | 6 | 0 | 0 | 15 |

Summary:

| h057_seed_rows | candidate_rows | near_transition_rows | pre_near_rows | post_near_rows | promoted_file | promoted_candidate | promoted_changed_cells | promoted_selected_rows | promoted_posterior_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 45 | 139 | 87 | 61 | 76 | submission_h065_state_transition_phase_75d5575d_uploadsafe.csv | h065_phase_h064_core_r24_phase_top4_a1p0_prob_75d5575d | 96 | 24 | -0.000111158 |

Decision:

| candidate_id | family | k_rows | alpha | mode | target_rule | max_per_subject | max_abs_seed_distance | selected_rows | selected_row_count | changed_cells_vs_h057 | changed_rows_vs_h057 | q2_changed_vs_h057 | posterior_delta_vs_h057 | mean_h065_row_score | mean_h064_row_score | mean_phase_route_gain | pre_rows | post_rows | phase_balance | episode_near_rate | selected_subjects | h050_null_rows_selected | h062_overlap_rows | h063_overlap_rows | h064_overlap_rows | mean_targets_per_row | target_specificity | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | file | resolved_path | posterior_rank | h065_rank | context_rank | overlap_strength | size_score | family_penalty | h065_score | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | q2_changed_vs_h057_validation | upload_safe | root_uploadsafe_path | decision | worldview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h065_phase_h064_core_r24_phase_top4_a1p0_prob_75d5575d | phase_h064_core | 24 | 1.000000000 | prob | phase_top4 | 8 | 3 | 138,205,236,99,195,147,132,71,214,140,133,53,244,145,54,162,75,222,2,62,142,154,124,159 | 24 | 96 | 24 | 0 | -0.000111158 | 0.985963333 | 0.662616702 | 0.008421465 | 10 | 14 | 0.416666667 | 1.000000000 | 10 | 0 | 14 | 21 | 24 | 4.000000000 | 1.000000000 | 14 | 0 | 10 | 0 | 24 | 24 | 24 | submission_h065_phase_h064_core_r24_phase_top4_a1p0_prob_75d5575d.csv | /Users/kbsoo/Downloads/cl2/hitl/h065_state_transition_phase_jepa/submission_h065_phase_h064_core_r24_phase_top4_a1p0_prob_75d5575d.csv | 0.277777778 | 0.835648148 | 0.835648148 | 0.819444444 | 0.600000000 | 0.000000000 | 0.708462963 | /Users/kbsoo/Downloads/cl2/submission_h065_state_transition_phase_75d5575d_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999999000 | 0 | True | /Users/kbsoo/Downloads/cl2/submission_h065_state_transition_phase_75d5575d_uploadsafe.csv | promote_state_transition_phase_sensor | H057 seed-neighbor rows are transition phases with phase-specific target routes, not copies of the seed full-vector state |

Top candidates:

| candidate_id | family | target_rule | selected_row_count | changed_cells_vs_h057 | posterior_delta_vs_h057 | phase_balance | mean_targets_per_row | h062_overlap_rows | h063_overlap_rows | h064_overlap_rows | h065_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h065_phase_h064_core_r24_phase_top4_a1p0_prob_75d5575d | phase_h064_core | phase_top4 | 24 | 96 | -0.000111158 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.708462963 |
| h065_phase_graph_near_r24_phase_top4_a1p0_prob_75d5575d | phase_graph_near | phase_top4 | 24 | 96 | -0.000111158 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.708462963 |
| h065_phase_near_union_r24_phase_top4_a1p0_prob_75d5575d | phase_near_union | phase_top4 | 24 | 96 | -0.000111158 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.708462963 |
| h065_phase_graph_near_r24_phase_top4_a1p0_logit_75d5575d | phase_graph_near | phase_top4 | 24 | 96 | -0.000111158 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.705407407 |
| h065_phase_near_union_r24_phase_top4_a1p0_logit_75d5575d | phase_near_union | phase_top4 | 24 | 96 | -0.000111158 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.705407407 |
| h065_phase_h064_core_r24_phase_top4_a1p0_logit_75d5575d | phase_h064_core | phase_top4 | 24 | 96 | -0.000111158 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.705407407 |
| h065_phase_h064_core_r24_phase_top4_a1p15_logit_bb9b80c9 | phase_h064_core | phase_top4 | 24 | 96 | -0.000108921 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.700314815 |
| h065_phase_near_union_r24_phase_top4_a1p15_logit_bb9b80c9 | phase_near_union | phase_top4 | 24 | 96 | -0.000108921 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.700314815 |
| h065_phase_graph_near_r24_phase_top4_a1p15_logit_bb9b80c9 | phase_graph_near | phase_top4 | 24 | 96 | -0.000108921 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.700314815 |
| h065_phase_graph_near_r36_phase_top4_a1p0_logit_d8468cfa | phase_graph_near | phase_top4 | 36 | 144 | -0.000154528 | 0.388888889 | 4.000000000 | 17 | 28 | 25 | 0.694870370 |
| h065_phase_near_union_r24_phase_top4_a1p15_prob_39719f18 | phase_near_union | phase_top4 | 24 | 96 | -0.000104921 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.694203704 |
| h065_phase_graph_near_r24_phase_top4_a1p15_prob_39719f18 | phase_graph_near | phase_top4 | 24 | 96 | -0.000104921 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.694203704 |
| h065_phase_h064_core_r24_phase_top4_a1p15_prob_39719f18 | phase_h064_core | phase_top4 | 24 | 96 | -0.000104921 | 0.416666667 | 4.000000000 | 14 | 21 | 24 | 0.694203704 |
| h065_phase_near_union_r24_phase_weighted_a1p15_logit_1f48d82a | phase_near_union | phase_weighted | 24 | 144 | -0.000136004 | 0.416666667 | 6.000000000 | 14 | 21 | 24 | 0.693990741 |
| h065_phase_near_union_r24_phase_weighted_gainpos_a1p15_logit_1f48d82a | phase_near_union | phase_weighted_gainpos | 24 | 144 | -0.000136004 | 0.416666667 | 6.000000000 | 14 | 21 | 24 | 0.693990741 |
| h065_phase_graph_near_r24_phase_weighted_a1p15_logit_1f48d82a | phase_graph_near | phase_weighted | 24 | 144 | -0.000136004 | 0.416666667 | 6.000000000 | 14 | 21 | 24 | 0.693990741 |
| h065_phase_h064_core_r24_phase_weighted_a1p15_logit_1f48d82a | phase_h064_core | phase_weighted | 24 | 144 | -0.000136004 | 0.416666667 | 6.000000000 | 14 | 21 | 24 | 0.693990741 |
| h065_phase_h064_core_r24_phase_weighted_gainpos_a1p15_logit_1f48d82a | phase_h064_core | phase_weighted_gainpos | 24 | 144 | -0.000136004 | 0.416666667 | 6.000000000 | 14 | 21 | 24 | 0.693990741 |
| h065_phase_graph_near_r24_phase_weighted_gainpos_a1p15_logit_1f48d82a | phase_graph_near | phase_weighted_gainpos | 24 | 144 | -0.000136004 | 0.416666667 | 6.000000000 | 14 | 21 | 24 | 0.693990741 |
| h065_phase_graph_near_r36_phase_top4_a1p0_prob_d8468cfa | phase_graph_near | phase_top4 | 36 | 144 | -0.000154528 | 0.388888889 | 4.000000000 | 17 | 28 | 25 | 0.693851852 |

Selected rows:

| row | subject_id | sleep_date | phase | signed_seed_offset | abs_seed_distance | h065_row_score | h064_row_score | phase_route_gain | h062_changed_row | h063_changed_row | h064_changed_row |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 138 | id06 | 2024-07-18 | pre | -1 | 1 | 1.133520000 | 0.725152264 | 0.014001820 | 1 | 1 | 1 |
| 205 | id09 | 2024-08-10 | post | 2 | 2 | 1.117760000 | 0.712049788 | 0.014598942 | 1 | 1 | 1 |
| 236 | id10 | 2024-08-19 | post | 1 | 1 | 1.099920000 | 0.747126216 | 0.007305033 | 1 | 1 | 1 |
| 99 | id04 | 2024-10-20 | post | 1 | 1 | 1.095840000 | 0.756306075 | 0.006743006 | 1 | 1 | 1 |
| 195 | id08 | 2024-09-10 | post | 1 | 1 | 1.090080000 | 0.731413869 | 0.012219463 | 1 | 1 | 1 |
| 147 | id06 | 2024-08-21 | post | 1 | 1 | 1.071360000 | 0.732480171 | 0.009801721 | 0 | 1 | 1 |
| 132 | id06 | 2024-07-11 | pre | -3 | 3 | 1.063520000 | 0.728938386 | 0.008131002 | 1 | 1 | 1 |
| 71 | id03 | 2024-09-17 | post | 1 | 1 | 1.039040000 | 0.694409107 | 0.008704810 | 1 | 1 | 1 |
| 214 | id09 | 2024-08-21 | pre | -2 | 2 | 1.036880000 | 0.698037461 | 0.007792216 | 1 | 1 | 1 |
| 140 | id06 | 2024-07-21 | post | 1 | 1 | 1.014240000 | 0.680440282 | 0.007034762 | 0 | 1 | 1 |
| 133 | id06 | 2024-07-12 | pre | -2 | 2 | 0.982640000 | 0.664249384 | 0.007030674 | 0 | 1 | 1 |
| 53 | id02 | 2024-10-10 | post | 3 | 3 | 0.982320000 | 0.660156073 | 0.006352448 | 0 | 1 | 1 |
| 244 | id10 | 2024-09-21 | post | 2 | 2 | 0.981920000 | 0.672559213 | 0.014964307 | 1 | 0 | 1 |
| 145 | id06 | 2024-08-15 | post | 1 | 1 | 0.966000000 | 0.660970365 | 0.005155678 | 0 | 1 | 1 |
| 54 | id02 | 2024-10-12 | pre | -2 | 2 | 0.960560000 | 0.614150814 | 0.014441147 | 1 | 1 | 1 |
| 162 | id07 | 2024-07-24 | pre | -1 | 1 | 0.939520000 | 0.640683633 | 0.011562733 | 1 | 1 | 1 |
| 75 | id03 | 2024-09-22 | pre | -3 | 3 | 0.913520000 | 0.584152345 | 0.004201313 | 0 | 1 | 1 |
| 222 | id09 | 2024-09-14 | pre | -3 | 3 | 0.913200000 | 0.647520634 | 0.003889052 | 0 | 1 | 1 |
| 2 | id01 | 2024-08-02 | pre | -1 | 1 | 0.899040000 | 0.582691742 | 0.007538801 | 0 | 1 | 1 |
| 62 | id03 | 2024-08-20 | post | 1 | 1 | 0.895760000 | 0.600264116 | 0.009026236 | 1 | 0 | 1 |
| 142 | id06 | 2024-08-12 | pre | -1 | 1 | 0.881920000 | 0.620691911 | 0.001732204 | 0 | 1 | 1 |
| 154 | id07 | 2024-07-16 | post | 2 | 2 | 0.878400000 | 0.599194299 | 0.007254157 | 1 | 1 | 1 |
| 124 | id05 | 2024-11-17 | post | 3 | 3 | 0.854640000 | 0.573279672 | 0.006991541 | 1 | 0 | 1 |
| 159 | id07 | 2024-07-21 | post | 1 | 1 | 0.851520000 | 0.575883034 | 0.005642093 | 0 | 1 | 1 |

Interpretation rule:

- If H065 improves over H057/H064, broad episode-copy was the wrong abstraction:
  HS-JEPA needs a transition-phase decoder around validated human-state seeds.
- If H065 fails while H062/H063/H064 improve, the phase-specific target route is
  too sparse or the learned pre/post route is wrong.
- If H065, H062, H063, and H064 all fail, H057 is likely a compact public-specific
  row-state and same-subject neighbor expansion should be demoted.
