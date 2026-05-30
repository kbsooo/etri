# E183 Pressure-World Branch Anatomy

## Question

E182 says E176, E154, and E144 can each be favorable or adverse under refreshed
current-anchor pressure worlds. This audit asks whether the favorable branch is
visible from train-derived priors and row/block context, or whether the sign
ambiguity is still a hidden-label/cell-resolution problem.

No submission is created.

## Result In One Sentence

Visible priors do not resolve the E182 sign ambiguity: favorable pressure worlds are preferred by visible_mean in E176/E154/E144 rates `0.000` / `0.000` / `0.000` across scenarios.

## Candidate-Level Summary

| candidate | scenario_count | range_width_mean | differing_moved_cells_mean | support_gap_coeff_weighted_mean | visible_mean_prefers_min_rate | visible_mean_ce_gap_mean | visible_mean_min_prob_mean | visible_mean_max_prob_mean | subject_prefers_min_rate | flank_mean_prefers_min_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e154 | 3 | 0.001964297 | 282.666666667 | 0.973558461 | 0.000000000 | 22.360364827 | 0.468387143 | 0.531612857 | 0.000000000 | 0.000000000 |
| e144 | 3 | 0.001672190 | 164.000000000 | 0.888922641 | 0.000000000 | 23.108376002 | 0.469643248 | 0.530356752 | 0.000000000 | 0.000000000 |
| e176 | 3 | 0.000656641 | 601.666666667 | 0.797945435 | 0.000000000 | 80.620140513 | 0.411040364 | 0.588959636 | 0.000000000 | 0.000000000 |

## Scenario-Level Summary

| scenario | candidate | pressure_min_delta_vs_e95 | pressure_max_delta_vs_e95 | pressure_range_width | differing_moved_cells | differing_range_share | support_gap_coeff_weighted | top_diff_target_share | diff_between_train_runs_rate | diff_e72_active_rate | visible_mean_prefers_min | visible_mean_ce_min_minus_max_diff_cells | subject_prefers_min | flank_mean_prefers_min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_t010 | e144 | -0.000645959 | 0.000741469 | 0.001387429 | 143 | 0.786148238 | 0.737545565 | Q3,Q1,S3,S2 | 0.489510490 | 0.237762238 | False | 20.255341892 | False | False |
| global_t010_subject_t010 | e144 | -0.000972245 | 0.000826612 | 0.001798857 | 171 | 0.956257594 | 0.956257594 | Q3,Q1,S3,S2 | 0.508771930 | 0.245614035 | False | 20.105340195 | False | False |
| global_t010_subject_t020 | e144 | -0.000992245 | 0.000838041 | 0.001830286 | 178 | 0.972964763 | 0.972964763 | Q3,Q1,S3,S2 | 0.494382022 | 0.230337079 | False | 28.964445920 | False | False |
| global_t010 | e154 | -0.001092857 | 0.000923535 | 0.002016392 | 292 | 0.999378067 | 0.999378068 | Q3,Q1,S3,S2 | 0.472602740 | 0.311643836 | False | 30.394457811 | False | False |
| global_t010_subject_t010 | e154 | -0.001031925 | 0.000887734 | 0.001919658 | 271 | 0.951434229 | 0.951434229 | Q3,Q1,S3,S4 | 0.487084871 | 0.309963100 | False | 13.370327358 | False | False |
| global_t010_subject_t020 | e154 | -0.001066685 | 0.000890156 | 0.001956841 | 285 | 0.969863087 | 0.969863088 | Q3,Q1,S3,S2 | 0.470175439 | 0.312280702 | False | 23.316309312 | False | False |
| global_t010 | e176 | -0.000421216 | 0.000254123 | 0.000675339 | 605 | 0.820667165 | 0.820667166 | Q2,S1,S3,S4 | 0.826446281 | 0.272727273 | False | 90.393883503 | False | False |
| global_t010_subject_t010 | e176 | -0.000382384 | 0.000244934 | 0.000627318 | 587 | 0.771284017 | 0.762312483 | Q2,S2,S4,S1 | 0.822827939 | 0.286201022 | False | 67.800220623 | False | False |
| global_t010_subject_t020 | e176 | -0.000416038 | 0.000251227 | 0.000667266 | 613 | 0.811544642 | 0.810856655 | Q2,S1,S4,Q3 | 0.831973899 | 0.285481240 | False | 83.666317412 | False | False |

## Largest Differing Moved Cells

| scenario | candidate | sub_idx | target | coeff | coeff_abs | min_label | max_label | support_label | p_y1_visible_mean | min_label_prob_visible_mean | max_label_prob_visible_mean | context_type | pos_bin | edge_like | between_train_runs | e72_active | e101_active | flank_conflict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_t010 | e144 | 47 | S2 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.878974359 | 0.878974359 | 0.121025641 | after_train_run | interior | False | False | False | False | False |
| global_t010 | e144 | 59 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.827864358 | 0.172135642 | 0.827864358 | between_train_runs | left_edge | True | True | False | False | False |
| global_t010 | e144 | 55 | Q3 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.756266001 | 0.243733999 | 0.756266001 | after_train_run | interior | False | False | False | False | False |
| global_t010 | e144 | 69 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.827864358 | 0.172135642 | 0.827864358 | between_train_runs | right_edge | True | True | False | False | False |
| global_t010 | e144 | 168 | Q1 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.378908325 | 0.378908325 | 0.621091675 | after_train_run | near_edge | True | False | True | False | False |
| global_t010 | e144 | 225 | Q1 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.608756907 | 0.608756907 | 0.391243093 | after_train_run | interior | False | False | True | False | False |
| global_t010 | e144 | 248 | S2 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.335035448 | 0.664964552 | 0.335035448 | after_train_run | near_edge | True | False | False | False | False |
| global_t010 | e144 | 160 | S4 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.604322123 | 0.604322123 | 0.395677877 | between_train_runs | interior | False | True | True | False | False |
| global_t010_subject_t010 | e144 | 59 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.827864358 | 0.172135642 | 0.827864358 | between_train_runs | left_edge | True | True | False | False | False |
| global_t010_subject_t010 | e144 | 66 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.818540349 | 0.181459651 | 0.818540349 | between_train_runs | interior | False | True | True | False | False |
| global_t010_subject_t010 | e144 | 55 | Q3 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.756266001 | 0.243733999 | 0.756266001 | after_train_run | interior | False | False | False | False | False |
| global_t010_subject_t010 | e144 | 69 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.827864358 | 0.172135642 | 0.827864358 | between_train_runs | right_edge | True | True | False | False | False |
| global_t010_subject_t010 | e144 | 168 | Q1 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.378908325 | 0.378908325 | 0.621091675 | after_train_run | near_edge | True | False | True | False | False |
| global_t010_subject_t010 | e144 | 225 | Q1 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.608756907 | 0.608756907 | 0.391243093 | after_train_run | interior | False | False | True | False | False |
| global_t010_subject_t010 | e144 | 248 | S2 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.335035448 | 0.664964552 | 0.335035448 | after_train_run | near_edge | True | False | False | False | False |
| global_t010_subject_t010 | e144 | 160 | S4 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.604322123 | 0.604322123 | 0.395677877 | between_train_runs | interior | False | True | True | False | False |
| global_t010_subject_t020 | e144 | 47 | S2 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.878974359 | 0.878974359 | 0.121025641 | after_train_run | interior | False | False | False | False | False |
| global_t010_subject_t020 | e144 | 59 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.827864358 | 0.172135642 | 0.827864358 | between_train_runs | left_edge | True | True | False | False | False |
| global_t010_subject_t020 | e144 | 66 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.818540349 | 0.181459651 | 0.818540349 | between_train_runs | interior | False | True | True | False | False |
| global_t010_subject_t020 | e144 | 55 | Q3 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.756266001 | 0.243733999 | 0.756266001 | after_train_run | interior | False | False | False | False | False |
| global_t010_subject_t020 | e144 | 69 | Q1 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.827864358 | 0.172135642 | 0.827864358 | between_train_runs | right_edge | True | True | False | False | False |
| global_t010_subject_t020 | e144 | 168 | Q1 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.378908325 | 0.378908325 | 0.621091675 | after_train_run | near_edge | True | False | True | False | False |
| global_t010_subject_t020 | e144 | 225 | Q1 | -0.000011429 | 0.000011429 | 1 | 0 | 1 | 0.608756907 | 0.608756907 | 0.391243093 | after_train_run | interior | False | False | True | False | False |
| global_t010_subject_t020 | e144 | 248 | S2 | 0.000011429 | 0.000011429 | 0 | 1 | 0 | 0.335035448 | 0.664964552 | 0.335035448 | after_train_run | near_edge | True | False | False | False | False |
| global_t010 | e154 | 66 | Q3 | -0.000015340 | 0.000015340 | 1 | 0 | 1 | 0.517773893 | 0.517773893 | 0.482226107 | between_train_runs | interior | False | True | False | False | True |
| global_t010 | e154 | 7 | Q3 | 0.000014420 | 0.000014420 | 0 | 1 | 0 | 0.675618813 | 0.324381187 | 0.675618813 | between_train_runs | interior | False | True | False | False | False |
| global_t010 | e154 | 180 | Q3 | 0.000013868 | 0.000013868 | 0 | 1 | 0 | 0.622003782 | 0.377996218 | 0.622003782 | after_train_run | near_edge | True | False | False | False | False |
| global_t010 | e154 | 212 | Q3 | 0.000013428 | 0.000013428 | 0 | 1 | 0 | 0.363354867 | 0.636645133 | 0.363354867 | between_train_runs | interior | False | True | False | False | False |
| global_t010 | e154 | 14 | Q1 | -0.000013405 | 0.000013405 | 1 | 0 | 1 | 0.612663569 | 0.612663569 | 0.387336431 | after_train_run | left_edge | True | False | False | False | False |
| global_t010 | e154 | 211 | Q3 | 0.000013283 | 0.000013283 | 0 | 1 | 0 | 0.364608423 | 0.635391577 | 0.364608423 | between_train_runs | interior | False | True | False | False | False |
| global_t010 | e154 | 18 | Q3 | -0.000013256 | 0.000013256 | 1 | 0 | 1 | 0.673863129 | 0.673863129 | 0.326136871 | after_train_run | interior | False | False | False | False | False |
| global_t010 | e154 | 3 | Q3 | 0.000013142 | 0.000013142 | 0 | 1 | 0 | 0.678687573 | 0.321312427 | 0.678687573 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t010 | e154 | 66 | Q3 | -0.000015340 | 0.000015340 | 1 | 0 | 1 | 0.517773893 | 0.517773893 | 0.482226107 | between_train_runs | interior | False | True | False | False | True |
| global_t010_subject_t010 | e154 | 7 | Q3 | 0.000014420 | 0.000014420 | 0 | 1 | 0 | 0.675618813 | 0.324381187 | 0.675618813 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t010 | e154 | 180 | Q3 | 0.000013868 | 0.000013868 | 0 | 1 | 0 | 0.622003782 | 0.377996218 | 0.622003782 | after_train_run | near_edge | True | False | False | False | False |
| global_t010_subject_t010 | e154 | 212 | Q3 | 0.000013428 | 0.000013428 | 0 | 1 | 0 | 0.363354867 | 0.636645133 | 0.363354867 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t010 | e154 | 14 | Q1 | -0.000013405 | 0.000013405 | 1 | 0 | 1 | 0.612663569 | 0.612663569 | 0.387336431 | after_train_run | left_edge | True | False | False | False | False |
| global_t010_subject_t010 | e154 | 211 | Q3 | 0.000013283 | 0.000013283 | 0 | 1 | 0 | 0.364608423 | 0.635391577 | 0.364608423 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t010 | e154 | 18 | Q3 | -0.000013256 | 0.000013256 | 1 | 0 | 1 | 0.673863129 | 0.673863129 | 0.326136871 | after_train_run | interior | False | False | False | False | False |
| global_t010_subject_t010 | e154 | 3 | Q3 | 0.000013142 | 0.000013142 | 0 | 1 | 0 | 0.678687573 | 0.321312427 | 0.678687573 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t020 | e154 | 66 | Q3 | -0.000015340 | 0.000015340 | 1 | 0 | 1 | 0.517773893 | 0.517773893 | 0.482226107 | between_train_runs | interior | False | True | False | False | True |
| global_t010_subject_t020 | e154 | 7 | Q3 | 0.000014420 | 0.000014420 | 0 | 1 | 0 | 0.675618813 | 0.324381187 | 0.675618813 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t020 | e154 | 180 | Q3 | 0.000013868 | 0.000013868 | 0 | 1 | 0 | 0.622003782 | 0.377996218 | 0.622003782 | after_train_run | near_edge | True | False | False | False | False |
| global_t010_subject_t020 | e154 | 212 | Q3 | 0.000013428 | 0.000013428 | 0 | 1 | 0 | 0.363354867 | 0.636645133 | 0.363354867 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t020 | e154 | 14 | Q1 | -0.000013405 | 0.000013405 | 1 | 0 | 1 | 0.612663569 | 0.612663569 | 0.387336431 | after_train_run | left_edge | True | False | False | False | False |
| global_t010_subject_t020 | e154 | 211 | Q3 | 0.000013283 | 0.000013283 | 0 | 1 | 0 | 0.364608423 | 0.635391577 | 0.364608423 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t020 | e154 | 18 | Q3 | -0.000013256 | 0.000013256 | 1 | 0 | 1 | 0.673863129 | 0.673863129 | 0.326136871 | after_train_run | interior | False | False | False | False | False |
| global_t010_subject_t020 | e154 | 3 | Q3 | 0.000013142 | 0.000013142 | 0 | 1 | 0 | 0.678687573 | 0.321312427 | 0.678687573 | between_train_runs | interior | False | True | False | False | False |
| global_t010 | e176 | 141 | S1 | 0.000005832 | 0.000005832 | 0 | 1 | 0 | 0.901352259 | 0.098647741 | 0.901352259 | between_train_runs | single | True | True | False | False | False |
| global_t010 | e176 | 196 | Q3 | -0.000004562 | 0.000004562 | 1 | 0 | 1 | 0.335671769 | 0.335671769 | 0.664328231 | between_train_runs | right_edge | True | True | True | False | False |
| global_t010 | e176 | 190 | Q3 | -0.000004531 | 0.000004531 | 1 | 0 | 1 | 0.603741497 | 0.603741497 | 0.396258503 | between_train_runs | left_edge | True | True | True | False | True |
| global_t010 | e176 | 194 | Q3 | -0.000004466 | 0.000004466 | 1 | 0 | 1 | 0.351615646 | 0.351615646 | 0.648384354 | between_train_runs | near_edge | True | True | True | False | False |
| global_t010 | e176 | 67 | S4 | -0.000004432 | 0.000004432 | 1 | 0 | 1 | 0.187647908 | 0.187647908 | 0.812352092 | between_train_runs | interior | False | True | False | False | False |
| global_t010 | e176 | 135 | S1 | 0.000004082 | 0.000004082 | 0 | 1 | 0 | 0.900912698 | 0.099087302 | 0.900912698 | between_train_runs | right_edge | True | True | True | False | False |
| global_t010 | e176 | 182 | Q3 | -0.000004015 | 0.000004015 | 1 | 0 | 1 | 0.332482993 | 0.332482993 | 0.667517007 | between_train_runs | left_edge | True | True | True | False | False |
| global_t010 | e176 | 205 | S2 | 0.000003995 | 0.000003995 | 0 | 1 | 0 | 0.800624154 | 0.199375846 | 0.800624154 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t010 | e176 | 141 | S1 | 0.000005832 | 0.000005832 | 0 | 1 | 0 | 0.901352259 | 0.098647741 | 0.901352259 | between_train_runs | single | True | True | False | False | False |
| global_t010_subject_t010 | e176 | 196 | Q3 | -0.000004562 | 0.000004562 | 1 | 0 | 1 | 0.335671769 | 0.335671769 | 0.664328231 | between_train_runs | right_edge | True | True | True | False | False |
| global_t010_subject_t010 | e176 | 190 | Q3 | -0.000004531 | 0.000004531 | 1 | 0 | 1 | 0.603741497 | 0.603741497 | 0.396258503 | between_train_runs | left_edge | True | True | True | False | True |
| global_t010_subject_t010 | e176 | 194 | Q3 | -0.000004466 | 0.000004466 | 1 | 0 | 1 | 0.351615646 | 0.351615646 | 0.648384354 | between_train_runs | near_edge | True | True | True | False | False |
| global_t010_subject_t010 | e176 | 67 | S4 | -0.000004432 | 0.000004432 | 1 | 0 | 1 | 0.187647908 | 0.187647908 | 0.812352092 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t010 | e176 | 135 | S1 | 0.000004082 | 0.000004082 | 0 | 1 | 0 | 0.900912698 | 0.099087302 | 0.900912698 | between_train_runs | right_edge | True | True | True | False | False |
| global_t010_subject_t010 | e176 | 182 | Q3 | -0.000004015 | 0.000004015 | 1 | 0 | 1 | 0.332482993 | 0.332482993 | 0.667517007 | between_train_runs | left_edge | True | True | True | False | False |
| global_t010_subject_t010 | e176 | 205 | S2 | 0.000003995 | 0.000003995 | 0 | 1 | 0 | 0.800624154 | 0.199375846 | 0.800624154 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t020 | e176 | 141 | S1 | 0.000005832 | 0.000005832 | 0 | 1 | 0 | 0.901352259 | 0.098647741 | 0.901352259 | between_train_runs | single | True | True | False | False | False |
| global_t010_subject_t020 | e176 | 196 | Q3 | -0.000004562 | 0.000004562 | 1 | 0 | 1 | 0.335671769 | 0.335671769 | 0.664328231 | between_train_runs | right_edge | True | True | True | False | False |
| global_t010_subject_t020 | e176 | 190 | Q3 | -0.000004531 | 0.000004531 | 1 | 0 | 1 | 0.603741497 | 0.603741497 | 0.396258503 | between_train_runs | left_edge | True | True | True | False | True |
| global_t010_subject_t020 | e176 | 194 | Q3 | -0.000004466 | 0.000004466 | 1 | 0 | 1 | 0.351615646 | 0.351615646 | 0.648384354 | between_train_runs | near_edge | True | True | True | False | False |
| global_t010_subject_t020 | e176 | 67 | S4 | -0.000004432 | 0.000004432 | 1 | 0 | 1 | 0.187647908 | 0.187647908 | 0.812352092 | between_train_runs | interior | False | True | False | False | False |
| global_t010_subject_t020 | e176 | 135 | S1 | 0.000004082 | 0.000004082 | 0 | 1 | 0 | 0.900912698 | 0.099087302 | 0.900912698 | between_train_runs | right_edge | True | True | True | False | False |
| global_t010_subject_t020 | e176 | 143 | S1 | 0.000004017 | 0.000004017 | 0 | 1 | 0 | 0.899736228 | 0.100263772 | 0.899736228 | between_train_runs | near_edge | True | True | False | False | False |
| global_t010_subject_t020 | e176 | 182 | Q3 | -0.000004015 | 0.000004015 | 1 | 0 | 1 | 0.332482993 | 0.332482993 | 0.667517007 | between_train_runs | left_edge | True | True | True | False | False |

## Interpretation

- The min pressure world is the favorable candidate world by construction, and
  the max pressure world is the adverse world. If visible/block priors were a
  usable branch selector, they should prefer the min labels on the differing
  moved cells consistently.
- A high support gap between min and max worlds confirms that E182 is not
  numerical noise: the pressure objectives are flipping exactly the candidate's
  high-impact moved labels.
- If visible_mean, subject, and flank priors do not consistently prefer the min
  world, then current public-free context cannot choose the branch. That keeps
  E176/E154/E144 as public sensors rather than expected-score certificates.

## Decision

No submission. Use this as the next underidentification layer after E182. A
future candidate needs either a new decisive-cell representation that separates
these pressure branches, or a pre-registered public feedback decoder for the
worldview being tested.
