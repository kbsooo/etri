# H039 Failed-Translator Nullspace HS-JEPA

## Question

Can H036 hidden public-world pressure become action-safe if we remove the
principal directions learned from H036/H037/H038 failed translators and
optionally pass the residual through the H024 survivor cone?

## Source Pool

| source_experiment | candidates | materialized | world_good_action_bad | survivor_hint | mean_h024_margin | max_h024_support |
| --- | --- | --- | --- | --- | --- | --- |
| h036 | 104 | 104 | 98 | 0 | 0.005081479 | 0.250000000 |
| h037 | 253 | 253 | 107 | 87 | 0.001155092 | 0.583333333 |
| h038 | 459 | 459 | 283 | 35 | 0.001307225 | 0.250000000 |

## Basis Diagnostics

| pc | singular | energy | cum_energy | basis |
| --- | --- | --- | --- | --- |
| 1 | 16.299840542 | 0.651576382 | 0.651576382 | all_bad |
| 2 | 4.644162434 | 0.052894854 | 0.704471236 | all_bad |
| 3 | 4.125407530 | 0.041738067 | 0.746209304 | all_bad |
| 4 | 3.913165481 | 0.037553900 | 0.783763204 | all_bad |
| 5 | 3.575538025 | 0.031353168 | 0.815116372 | all_bad |
| 6 | 3.430334033 | 0.028858347 | 0.843974719 | all_bad |
| 7 | 3.313811774 | 0.026931113 | 0.870905831 | all_bad |
| 8 | 3.188498783 | 0.024932805 | 0.895838636 | all_bad |
| 9 | 2.859594248 | 0.020054297 | 0.915892933 | all_bad |
| 10 | 2.356513435 | 0.013618788 | 0.929511721 | all_bad |
| 11 | 2.204212709 | 0.011915318 | 0.941427039 | all_bad |
| 12 | 1.827745294 | 0.008192755 | 0.949619794 | all_bad |
| 13 | 1.505105054 | 0.005555616 | 0.955175410 | all_bad |
| 14 | 1.446542927 | 0.005131700 | 0.960307111 | all_bad |
| 15 | 1.389669400 | 0.004736108 | 0.965043219 | all_bad |
| 16 | 1.149845699 | 0.003242483 | 0.968285702 | all_bad |
| 17 | 1.140166450 | 0.003188124 | 0.971473826 | all_bad |
| 18 | 1.040222668 | 0.002653696 | 0.974127522 | all_bad |
| 19 | 1.006638935 | 0.002485113 | 0.976612635 | all_bad |
| 20 | 0.869724289 | 0.001855076 | 0.978467711 | all_bad |
| 21 | 0.851868907 | 0.001779689 | 0.980247400 | all_bad |
| 22 | 0.827803154 | 0.001680555 | 0.981927956 | all_bad |
| 23 | 0.730853024 | 0.001309962 | 0.983237918 | all_bad |
| 24 | 0.702242167 | 0.001209407 | 0.984447324 | all_bad |
| 25 | 0.675513897 | 0.001119096 | 0.985566420 | all_bad |
| 26 | 0.667468592 | 0.001092598 | 0.986659018 | all_bad |
| 27 | 0.599178174 | 0.000880462 | 0.987539480 | all_bad |
| 28 | 0.595385347 | 0.000869350 | 0.988408830 | all_bad |
| 29 | 0.579424141 | 0.000823364 | 0.989232194 | all_bad |
| 30 | 0.554767333 | 0.000754780 | 0.989986974 | all_bad |

## Projection Diagnostics

| source_vector | forbid_basis | forbid_pcs | removed_norm_ratio | cosine_removed_to_world | cosine_removed_to_ray |
| --- | --- | --- | --- | --- | --- |
| world | world_bad | 8 | 0.210274586 | 0.210274586 | -0.057028796 |
| world | world_bad | 24 | 0.068574652 | 0.068574652 | 0.009777572 |
| world | all_bad | 8 | 0.227501309 | 0.227501309 | -0.047692020 |
| world | all_bad | 24 | 0.090005574 | 0.090005574 | 0.025063360 |
| posterior_world_mix | world_bad | 8 | 0.134906830 | 0.197593873 | -0.011757091 |
| posterior_world_mix | world_bad | 24 | 0.057889053 | 0.062115614 | 0.029377145 |
| posterior_world_mix | all_bad | 8 | 0.149590701 | 0.215232796 | -0.002898648 |
| posterior_world_mix | all_bad | 24 | 0.076524555 | 0.084825215 | 0.041551316 |
| transition_world | world_bad | 8 | 0.150772473 | 0.200751341 | -0.078682475 |
| transition_world | world_bad | 24 | 0.042381457 | 0.061116152 | 0.014641854 |
| transition_world | all_bad | 8 | 0.169531477 | 0.218308505 | -0.064339624 |
| transition_world | all_bad | 24 | 0.052214802 | 0.082512957 | 0.026608758 |

## Gate Counts

| candidates | world_cell_lt_-0.00018 | posterior_lt_-0.00006 | h024_margin_negative | h024_margin_lt_-0.00010 | h024_support_ge_0.55 | world_and_h024_negative |
| --- | --- | --- | --- | --- | --- | --- |
| 520 | 0 | 0 | 0 | 0 | 0 | 0 |

## Top Candidates

| candidate_id | family | projection_mode | forbid_basis | forbid_pcs | route_mask | k | cap | changed_cells_vs_h012 | world_cell_delta_vs_h012 | posterior_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | forbidden_cosine | h039_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h039_transition_world_allow_cone_world_bad_pc8_exception_k238_cap0.022_583e2255 | transition_world_allow_cone | allow_cone | world_bad | 8 | exception | 238 | 0.022000000 | 237 | -0.000018978 | -0.000009471 | 0.000238744 | 0.250000000 | 1.643644207 | 0.786552145 | 0.621750000 |
| h039_transition_world_allow_cone_world_bad_pc8_transition_high_support_k250_cap0.022_02f713cf | transition_world_allow_cone | allow_cone | world_bad | 8 | transition_high_support | 250 | 0.022000000 | 249 | -0.000021942 | -0.000009673 | 0.000267539 | 0.250000000 | 1.762738752 | 0.761853404 | 0.690692308 |
| h039_transition_world_allow_cone_world_bad_pc8_world_high_support_k199_cap0.022_81b742be | transition_world_allow_cone | allow_cone | world_bad | 8 | world_high_support | 199 | 0.022000000 | 199 | -0.000019949 | -0.000007097 | 0.000209130 | 0.250000000 | 1.095598706 | 0.801634924 | 0.710788462 |
| h039_posterior_world_mix_allow_cone_world_bad_pc24_exception_k271_cap0.06_1edc40e6 | posterior_world_mix_allow_cone | allow_cone | world_bad | 24 | exception | 271 | 0.060000000 | 270 | -0.000024873 | -0.000013510 | 0.000385067 | 0.250000000 | 2.247927519 | 0.574972883 | 0.784576923 |
| h039_world_allow_cone_world_bad_pc8_transition_high_support_k249_cap0.022_2dfc2979 | world_allow_cone | allow_cone | world_bad | 8 | transition_high_support | 249 | 0.022000000 | 248 | -0.000021985 | -0.000010276 | 0.000250134 | 0.250000000 | 1.187146406 | 0.727089843 | 0.798961538 |
| h039_world_allow_cone_world_bad_pc8_world_high_support_k194_cap0.022_41a58373 | world_allow_cone | allow_cone | world_bad | 8 | world_high_support | 194 | 0.022000000 | 194 | -0.000019601 | -0.000006829 | 0.000189248 | 0.250000000 | 0.748520455 | 0.766887667 | 0.865884615 |
| h039_posterior_world_mix_allow_cone_world_bad_pc24_exception_k271_cap0.022_a3148fe8 | posterior_world_mix_allow_cone | allow_cone | world_bad | 24 | exception | 271 | 0.022000000 | 270 | -0.000011785 | -0.000007619 | 0.000147903 | 0.250000000 | 2.179016842 | 0.574972883 | 0.869576923 |
| h039_world_allow_cone_world_bad_pc8_exception_k255_cap0.022_d8ac5219 | world_allow_cone | allow_cone | world_bad | 8 | exception | 255 | 0.022000000 | 254 | -0.000021941 | -0.000010681 | 0.000242707 | 0.250000000 | 0.944852732 | 0.730683008 | 0.872653846 |
| h039_world_allow_cone_world_bad_pc24_support_k280_cap0.022_708ad922 | world_allow_cone | allow_cone | world_bad | 24 | support | 280 | 0.022000000 | 280 | -0.000024724 | -0.000004297 | 0.000205255 | 0.250000000 | 0.701758205 | 0.312818094 | 0.910673077 |
| h039_transition_world_allow_cone_world_bad_pc24_exception_k204_cap0.06_52a870f5 | transition_world_allow_cone | allow_cone | world_bad | 24 | exception | 204 | 0.060000000 | 203 | -0.000023726 | -0.000014267 | 0.000331602 | 0.250000000 | 1.003542145 | 0.659857233 | 0.920615385 |
| h039_transition_world_allow_cone_world_bad_pc24_exception_k204_cap0.022_6bbc7321 | transition_world_allow_cone | allow_cone | world_bad | 24 | exception | 204 | 0.022000000 | 203 | -0.000011077 | -0.000007609 | 0.000131417 | 0.250000000 | 1.321610908 | 0.659857233 | 0.934269231 |
| h039_posterior_world_mix_allow_cone_world_bad_pc24_transition_high_support_k239_cap0.022_e0165268 | posterior_world_mix_allow_cone | allow_cone | world_bad | 24 | transition_high_support | 239 | 0.022000000 | 238 | -0.000018721 | -0.000009290 | 0.000163537 | 0.250000000 | 2.119033239 | 0.698436020 | 1.001461538 |
| h039_posterior_world_mix_allow_cone_world_bad_pc24_support_k280_cap0.022_82e9a42c | posterior_world_mix_allow_cone | allow_cone | world_bad | 24 | support | 280 | 0.022000000 | 280 | -0.000023690 | -0.000008713 | 0.000193515 | 0.250000000 | 1.422637940 | 0.329931179 | 1.018750000 |
| h039_world_remove_only_world_bad_pc24_transition_high_support_k241_cap0.022_65e93765 | world_remove_only | remove_only | world_bad | 24 | transition_high_support | 241 | 0.022000000 | 241 | -0.000028012 | -0.000012871 | 0.000244816 | 0.250000000 | 1.235031238 | 0.475312126 | 1.029673077 |
| h039_world_allow_cone_world_bad_pc24_exception_k222_cap0.022_d4dcaa86 | world_allow_cone | allow_cone | world_bad | 24 | exception | 222 | 0.022000000 | 221 | -0.000010882 | -0.000007661 | 0.000139308 | 0.250000000 | 0.629437633 | 0.699559332 | 1.036932692 |
| h039_world_remove_only_world_bad_pc24_transition_high_support_k120_cap0.022_a4b0c893 | world_remove_only | remove_only | world_bad | 24 | transition_high_support | 120 | 0.022000000 | 120 | -0.000021810 | -0.000008112 | 0.000170679 | 0.250000000 | 1.407076422 | 0.316823689 | 1.065721154 |
| h039_posterior_world_mix_allow_cone_all_bad_pc24_exception_k230_cap0.022_7c01db75 | posterior_world_mix_allow_cone | allow_cone | all_bad | 24 | exception | 230 | 0.022000000 | 229 | -0.000013588 | -0.000009161 | 0.000139190 | 0.250000000 | 1.198560170 | 0.617675655 | 1.065721154 |
| h039_transition_world_allow_cone_world_bad_pc24_transition_high_support_k189_cap0.022_5f645925 | transition_world_allow_cone | allow_cone | world_bad | 24 | transition_high_support | 189 | 0.022000000 | 188 | -0.000013876 | -0.000009230 | 0.000123341 | 0.250000000 | 1.611487756 | 0.730689569 | 1.077750000 |
| h039_world_double_null_world_bad_pc24_transition_high_support_k242_cap0.022_8af16c42 | world_double_null | double_null | world_bad | 24 | transition_high_support | 242 | 0.022000000 | 242 | -0.000029063 | -0.000013325 | 0.000247393 | 0.250000000 | 1.212313188 | 0.470549352 | 1.079807692 |
| h039_world_allow_cone_all_bad_pc24_exception_k212_cap0.022_b17cc62f | world_allow_cone | allow_cone | all_bad | 24 | exception | 212 | 0.022000000 | 211 | -0.000011726 | -0.000007902 | 0.000128943 | 0.250000000 | 0.737023014 | 0.646452935 | 1.081288462 |
| h039_world_allow_cone_world_bad_pc24_transition_high_support_k195_cap0.022_38b8175f | world_allow_cone | allow_cone | world_bad | 24 | transition_high_support | 195 | 0.022000000 | 194 | -0.000012962 | -0.000007225 | 0.000131573 | 0.250000000 | 0.513677010 | 0.771044625 | 1.092134615 |
| h039_posterior_world_mix_remove_only_world_bad_pc24_transition_high_support_k240_cap0.022_8e7ef15d | posterior_world_mix_remove_only | remove_only | world_bad | 24 | transition_high_support | 240 | 0.022000000 | 240 | -0.000024023 | -0.000018068 | 0.000246790 | 0.250000000 | 1.208330136 | 0.429719627 | 1.103807692 |
| h039_world_allow_cone_all_bad_pc24_exception_k212_cap0.06_283b6a94 | world_allow_cone | allow_cone | all_bad | 24 | exception | 212 | 0.060000000 | 211 | -0.000025994 | -0.000015566 | 0.000347991 | 0.250000000 | 0.526805775 | 0.646452935 | 1.120961538 |
| h039_world_allow_cone_world_bad_pc24_support_k280_cap0.06_3e9eec15 | world_allow_cone | allow_cone | world_bad | 24 | support | 280 | 0.060000000 | 280 | -0.000057154 | -0.000001445 | 0.000469217 | 0.250000000 | 0.638811825 | 0.312818094 | 1.125000000 |

## Row-Permutation Stress

- rowperm p(perm >= real): `0.510000000`

| perm | real_top1200_sum | perm_top1200_sum | real_minus_perm |
| --- | --- | --- | --- |
| 0 | -1.643644207 | -0.947727544 | -0.695916663 |
| 1 | -1.643644207 | -1.267676614 | -0.375967593 |
| 2 | -1.643644207 | -1.262326834 | -0.381317374 |
| 3 | -1.643644207 | -0.042227398 | -1.601416809 |
| 4 | -1.643644207 | -1.472534896 | -0.171109311 |
| 5 | -1.643644207 | -2.138981767 | 0.495337560 |
| 6 | -1.643644207 | -1.649683052 | 0.006038845 |
| 7 | -1.643644207 | -1.300033338 | -0.343610870 |

## Decision

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | family | source_vector | projection_mode | forbid_basis | forbid_pcs | route_mask | world_cell_delta_vs_h012 | posterior_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | rowperm_real_top1200_sum | rowperm_p_perm_ge_real | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| do_not_promote | False | h039_transition_world_allow_cone_world_bad_pc8_exception_k238_cap0.022_583e2255 | submission_h039_transition_world_allow_cone_world_bad_pc8_exception_k238_cap0.022_583e2255.csv | /Users/kbsoo/Downloads/cl2/hitl/h039_failed_translator_nullspace_jepa/submission_h039_transition_world_allow_cone_world_bad_pc8_exception_k238_cap0.022_583e2255.csv | transition_world_allow_cone | transition_world | allow_cone | world_bad | 8 | exception | -0.000018978 | -0.000009471 | 0.000238744 | 0.250000000 | 1.643644207 | -1.643644207 | 0.510000000 | world-cell gain too small; posterior gain too small; H024 pre-H012 margin not below H012; H024 support below 55%; H025 row permutation stress weak |

## Interpretation

- Passing would mean the post-H012 action decoder is approximately a
  failed-direction nullspace or survivor-cone law.
- Failing means H036/H037/H038 failures are not linearly removable;
  the missing HS-JEPA decoder is likely discrete route/private-public
  structure rather than a linear projection around H012.
