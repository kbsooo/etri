# H021 Human-State Conditional Vector-Prior HS-JEPA

## Question

Can raw human-state context predict the hidden row-level 7-target vector and use that as a non-public regularizer for the H020 public-equation posterior?

## Train Public-Free Prior Validation

Global vector prior baseline marginal BCE: `0.664614445`
Global vector prior baseline vector NLL: `4.140676540`

| config_id | group | scope | k | date_decay | alpha | subject_boost | n_cols | marginal_bce | delta_marginal_bce_vs_global | vector_nll | delta_vector_nll_vs_global | vector_top1_acc | mean_entropy | mean_top_prob | mean_train_neighbor_ess | mean_test_neighbor_ess | mean_test_same_subject_share | config_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject_all_k10 | all | subject | 10 | 0.000000000 | 0.750000000 | 1.000000000 | 300 | 0.617584875 | -0.047029570 | 4.271432345 | 0.130755806 | 0.113333333 | 3.491555440 | 0.143815601 | 9.759208726 | 9.798676024 | 1.000000000 | -0.039524222 |
| hybrid_social_sleep_k36_boost4 | social_sleep | hybrid | 36 | 45.000000000 | 0.500000000 | 4.000000000 | 200 | 0.620037205 | -0.044577241 | 4.275629431 | 0.134952891 | 0.111111111 | 3.616844726 | 0.127344066 | 19.815053394 | 21.668532023 | 0.431777778 | -0.036813401 |
| hybrid_state_k36_boost4 | state | hybrid | 36 | 45.000000000 | 0.500000000 | 4.000000000 | 254 | 0.620014848 | -0.044599597 | 4.278425354 | 0.137748814 | 0.100000000 | 3.608573982 | 0.128969334 | 19.786947122 | 21.384529023 | 0.459000000 | -0.036634668 |
| subject_state_k10 | state | subject | 10 | 0.000000000 | 0.750000000 | 1.000000000 | 254 | 0.621033301 | -0.043581144 | 4.291739192 | 0.151062652 | 0.111111111 | 3.495059927 | 0.141658885 | 9.709912710 | 9.753076019 | 1.000000000 | -0.034850719 |
| subject_past_state_k10_d28 | state | subject_past | 10 | 28.000000000 | 0.750000000 | 1.000000000 | 254 | 0.625613916 | -0.039000529 | 4.334413056 | 0.193736516 | 0.100000000 | 3.390408958 | 0.187690773 | 7.416290226 | 7.726494581 | 1.000000000 | -0.027676338 |
| global_all_k32 | all | global | 32 | 0.000000000 | 0.500000000 | 1.000000000 | 300 | 0.636517591 | -0.028096854 | 4.287831858 | 0.147155318 | 0.093333333 | 3.767108531 | 0.091225377 | 31.256888097 | 31.355070070 | 0.492500000 | -0.019547535 |
| quality_global_k32 | quality | global | 32 | 0.000000000 | 0.500000000 | 1.000000000 | 30 | 0.637298776 | -0.027315669 | 4.378563161 | 0.237886621 | 0.088888889 | 3.692103729 | 0.111968346 | 29.017652729 | 29.316108916 | 0.501750000 | -0.013309139 |
| global_social_sleep_k32 | social_sleep | global | 32 | 0.000000000 | 0.500000000 | 1.000000000 | 200 | 0.641428088 | -0.023186357 | 4.321987703 | 0.181311164 | 0.088888889 | 3.766400440 | 0.091669701 | 31.329740720 | 31.419927727 | 0.453125000 | -0.012574354 |
| global_state_k32 | state | global | 32 | 0.000000000 | 0.500000000 | 1.000000000 | 254 | 0.641200205 | -0.023414240 | 4.345021538 | 0.204344998 | 0.104444444 | 3.763734476 | 0.093028777 | 31.094972482 | 31.192807134 | 0.484750000 | -0.011466873 |
| calendar_body_global_k32 | calendar_body | global | 32 | 0.000000000 | 0.500000000 | 1.000000000 | 134 | 0.652672354 | -0.011942091 | 4.463192747 | 0.322516207 | 0.086666667 | 3.738849372 | 0.096193113 | 30.936099289 | 31.141247547 | 0.286875000 | 0.007148881 |

## Selected Human-State Prior Ensemble

Top configs: `subject_all_k10, hybrid_social_sleep_k36_boost4, hybrid_state_k36_boost4, subject_state_k10`
Weights: `0.697, 0.137, 0.123, 0.042`

## Test Row Human-State State

| subject_id | sleep_date | lifelog_date | hs_top_vector_code | hs_top_vector | hs_top_vector_prob | hs_vector_entropy | hs_row_conf | hs_h020_agree_rate | h020_row_score | h020_row_weight | ensemble_configs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id06 | 2024-08-23 00:00:00 | 2024-08-22 00:00:00 | 63 | 0111111 | 0.377006394 | 3.032853462 | 0.656212078 | 0.428571429 | 0.656240000 | 0.004623910 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-10-07 00:00:00 | 2024-10-06 00:00:00 | 127 | 1111111 | 0.329415345 | 3.079770828 | 0.647293778 | 0.285714286 | 0.160160000 | 0.003054020 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-07-18 00:00:00 | 2024-07-17 00:00:00 | 63 | 0111111 | 0.319939125 | 3.106070666 | 0.642512570 | 0.428571429 | 0.789120000 | 0.004650599 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-10-12 00:00:00 | 2024-10-11 00:00:00 | 127 | 1111111 | 0.333482172 | 3.163121292 | 0.639645618 | 0.285714286 | 0.759680000 | 0.004367156 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-10-14 00:00:00 | 2024-10-13 00:00:00 | 127 | 1111111 | 0.313486232 | 3.155048757 | 0.635160678 | 0.428571429 | 0.238240000 | 0.003563101 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-07-09 00:00:00 | 2024-07-08 00:00:00 | 63 | 0111111 | 0.291587155 | 3.186167039 | 0.628033277 | 0.428571429 | 0.633200000 | 0.004360317 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-07-13 00:00:00 | 2024-07-12 00:00:00 | 63 | 0111111 | 0.288717717 | 3.215345468 | 0.622925767 | 0.714285714 | 0.599440000 | 0.003948620 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-09-08 00:00:00 | 2024-09-07 00:00:00 | 127 | 1111111 | 0.301030909 | 3.261596887 | 0.621282956 | 0.285714286 | 0.365200000 | 0.003747307 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-07-10 00:00:00 | 2024-07-09 00:00:00 | 63 | 0111111 | 0.270564647 | 3.221039005 | 0.613280379 | 0.714285714 | 0.385200000 | 0.003614429 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-07-07 00:00:00 | 2024-07-06 00:00:00 | 63 | 0111111 | 0.271721784 | 3.248366175 | 0.611982718 | 0.142857143 | 0.785520000 | 0.004355549 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-09-09 00:00:00 | 2024-09-08 00:00:00 | 127 | 1111111 | 0.281792673 | 3.281179319 | 0.610063197 | 0.142857143 | 0.420880000 | 0.003827004 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-08-15 00:00:00 | 2024-08-14 00:00:00 | 63 | 0111111 | 0.283923741 | 3.313325771 | 0.610019248 | 0.142857143 | 0.682160000 | 0.005074318 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-07-11 00:00:00 | 2024-07-10 00:00:00 | 63 | 0111111 | 0.255142567 | 3.222572885 | 0.605906506 | 0.571428571 | 0.557680000 | 0.003989681 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id06 | 2024-08-22 00:00:00 | 2024-08-21 00:00:00 | 63 | 0111111 | 0.259248961 | 3.272979882 | 0.603792641 | 0.142857143 | 0.744960000 | 0.004797521 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-09-01 00:00:00 | 2024-08-31 00:00:00 | 127 | 1111111 | 0.283443442 | 3.370345503 | 0.601755799 | 0.428571429 | 0.540160000 | 0.003858511 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-10-03 00:00:00 | 2024-10-02 00:00:00 | 127 | 1111111 | 0.245286851 | 3.241464105 | 0.600165099 | 0.428571429 | 0.554080000 | 0.003942983 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-08-26 00:00:00 | 2024-08-25 00:00:00 | 127 | 1111111 | 0.262511946 | 3.331101832 | 0.599004250 | 0.428571429 | 0.195520000 | 0.003517649 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-09-06 00:00:00 | 2024-09-05 00:00:00 | 127 | 1111111 | 0.247954957 | 3.288018787 | 0.596687912 | 0.428571429 | 0.812560000 | 0.004318741 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-09-29 00:00:00 | 2024-09-28 00:00:00 | 127 | 1111111 | 0.256524307 | 3.333291788 | 0.595156008 | 0.142857143 | 0.637280000 | 0.006291522 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |
| id02 | 2024-10-05 00:00:00 | 2024-10-04 00:00:00 | 127 | 1111111 | 0.244882813 | 3.280171539 | 0.592177433 | 0.285714286 | 0.459680000 | 0.004195932 | subject_all_k10,hybrid_social_sleep_k36_boost4,hybrid_state_k36_boost4,subject_state_k10 |

## Top Human-State Vectors

| hs_top_vector | count |
| --- | --- |
| 1111111 | 76 |
| 0111111 | 27 |
| 0100111 | 16 |
| 1111000 | 14 |
| 0000001 | 11 |
| 1001111 | 10 |
| 1101111 | 9 |
| 0001111 | 8 |
| 1111101 | 8 |
| 0001110 | 8 |
| 1011000 | 6 |
| 1110001 | 5 |

## Mean Prior Shift

| target | h012_mean | h020_mean | hs_mean |
| --- | --- | --- | --- |
| Q1 | 0.494667535 | 0.493493231 | 0.501237410 |
| Q2 | 0.548956037 | 0.548869257 | 0.557255920 |
| Q3 | 0.607849452 | 0.606245589 | 0.589887105 |
| S1 | 0.661251559 | 0.658125878 | 0.691090562 |
| S2 | 0.640413579 | 0.640787781 | 0.625002570 |
| S3 | 0.666531151 | 0.673689586 | 0.645759961 |
| S4 | 0.566948940 | 0.567532522 | 0.551534356 |

## Candidate Ranking

| candidate_id | mode | k | alpha | hs_mix | file | changed_cells | changed_rows | mean_abs_delta_vs_h012 | max_abs_delta_vs_h012 | agree_rate_changed | h020_delta_vs_h012 | hs_delta_vs_h012 | h020_gain_retained | survival_score | real_hs_delta_vs_h012 | null_hs_delta_mean | null_hs_delta_p10 | null_hs_delta_p50 | null_hs_delta_p90 | real_percentile_lower_is_better | real_agree_rate_changed | null_agree_rate_mean | null_hs_advantage | public_equation_survives | human_state_beats_null | action_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agree_h020_k1200_a1 | agree_h020 | 1200 | 1.000000000 | 0.000000000 | hitl/h021_human_state_vector_prior_jepa/submission_h021_agree_h020_k1200_a1_e1546ba9.csv | 1200 | 248 | 0.010015858 | 0.123283706 | 0.580833333 | -0.000684129 | 0.013058704 | 0.618866184 | 0.004158949 | 0.013058704 | 0.018609416 | 0.017000786 | 0.018608057 | 0.020281662 | 0.000000000 | 0.580833333 | 0.610226667 | 0.005549353 | True | True | primary_hs_action |
| agree_h020_k900_a1 | agree_h020 | 900 | 1.000000000 | 0.000000000 | hitl/h021_human_state_vector_prior_jepa/submission_h021_agree_h020_k900_a1_744fcd7f.csv | 900 | 244 | 0.007407976 | 0.123283706 | 0.774444444 | -0.000465002 | 0.003697485 | 0.420642631 | 0.000658613 | 0.003697485 | 0.001640904 | -0.000835912 | 0.001520887 | 0.004332655 | 0.844000000 | 0.774444444 | 0.811982222 | -0.002176598 | True | False | public_only_action |
| agree_joint_hs_k900_a1_m0.25 | agree_joint_hs | 900 | 1.000000000 | 0.250000000 | hitl/h021_human_state_vector_prior_jepa/submission_h021_agree_joint_hs_k900_a1_m0.25_f9c710d1.csv | 900 | 244 | 0.015992545 | 0.105102062 | 0.774444444 | 0.000735991 | -0.011537977 | -0.665780713 | -0.004542380 | -0.011537977 | -0.030748576 | -0.032176105 | -0.030713309 | -0.029492067 | 1.000000000 | 0.774444444 | 0.812475556 | -0.019175332 | False | False | diagnostic_only |
| agree_joint_hs_k1200_a1_m0.25 | agree_joint_hs | 1200 | 1.000000000 | 0.250000000 | hitl/h021_human_state_vector_prior_jepa/submission_h021_agree_joint_hs_k1200_a1_m0.25_4f9b00aa.csv | 1200 | 248 | 0.019151257 | 0.105102062 | 0.580833333 | 0.001159772 | -0.014089902 | -1.049135014 | -0.005014564 | -0.014089902 | -0.039888287 | -0.041617866 | -0.039927548 | -0.038151842 | 1.000000000 | 0.580833333 | 0.609973333 | -0.025837646 | False | False | diagnostic_only |
| hs_regularize_all_a0.9_m0.18 | hs_regularize_all | 1750 | 0.900000000 | 0.180000000 | hitl/h021_human_state_vector_prior_jepa/submission_h021_hs_regularize_all_a0.9_m0.18_e00b16b9.csv | 1750 | 250 | 0.017307219 | 0.079804120 | 0.398285714 | 0.000273235 | -0.004377235 | -0.247169299 | -0.006173663 | -0.004377235 | -0.023801881 | -0.025298559 | -0.023827001 | -0.022257968 | 1.000000000 | 0.398285714 | 0.417028571 | -0.019449766 | False | False | diagnostic_only |
| conflict_hs_override_k280_a0.35 | conflict_hs_override | 280 | 0.350000000 | 1.000000000 | hitl/h021_human_state_vector_prior_jepa/submission_h021_conflict_hs_override_k280_a0.35_5fe5b273.csv | 1750 | 250 | 0.016764555 | 0.161021909 | 0.000000000 | 0.001191888 | -0.001908696 | -1.078186959 | -0.007191888 | -0.001908696 | -0.003648373 | -0.009420833 | -0.003946019 | 0.002336569 | 0.628000000 | 0.000000000 | 0.000000000 | -0.002037323 | False | False | diagnostic_only |
| hs_regularize_all_a1_m0.25 | hs_regularize_all | 1750 | 1.000000000 | 0.250000000 | hitl/h021_human_state_vector_prior_jepa/submission_h021_hs_regularize_all_a1_m0.25_71df5586.csv | 1750 | 250 | 0.024984419 | 0.120107223 | 0.398285714 | 0.001985261 | -0.018820786 | -1.795875694 | -0.007885689 | -0.018820786 | -0.054036719 | -0.056445266 | -0.053962737 | -0.051720677 | 1.000000000 | 0.398285714 | 0.418013714 | -0.035141951 | False | False | diagnostic_only |

## Null Stress

The human-state prior rows are permuted across test rows. A real candidate should align with the unpermuted human-state vector prior better than this null.

| candidate_id | real_hs_delta_vs_h012 | null_hs_delta_mean | null_hs_delta_p10 | null_hs_delta_p50 | null_hs_delta_p90 | real_percentile_lower_is_better | real_agree_rate_changed | null_agree_rate_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agree_h020_k900_a1 | 0.003697485 | 0.001640904 | -0.000835912 | 0.001520887 | 0.004332655 | 0.844000000 | 0.774444444 | 0.811982222 |
| agree_h020_k1200_a1 | 0.013058704 | 0.018609416 | 0.017000786 | 0.018608057 | 0.020281662 | 0.000000000 | 0.580833333 | 0.610226667 |
| agree_joint_hs_k900_a1_m0.25 | -0.011537977 | -0.030748576 | -0.032176105 | -0.030713309 | -0.029492067 | 1.000000000 | 0.774444444 | 0.812475556 |
| agree_joint_hs_k1200_a1_m0.25 | -0.014089902 | -0.039888287 | -0.041617866 | -0.039927548 | -0.038151842 | 1.000000000 | 0.580833333 | 0.609973333 |
| hs_regularize_all_a0.9_m0.18 | -0.004377235 | -0.023801881 | -0.025298559 | -0.023827001 | -0.022257968 | 1.000000000 | 0.398285714 | 0.417028571 |
| hs_regularize_all_a1_m0.25 | -0.018820786 | -0.054036719 | -0.056445266 | -0.053962737 | -0.051720677 | 1.000000000 | 0.398285714 | 0.418013714 |
| conflict_hs_override_k280_a0.35 | -0.001908696 | -0.003648373 | -0.009420833 | -0.003946019 | 0.002336569 | 0.628000000 | 0.000000000 | 0.000000000 |

## Decision

Selected upload-safe candidate: `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv`
Validation: `{'path': '/Users/kbsoo/Downloads/cl2/submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv', 'shape': (250, 10), 'min_prob': 1.0000000000000008e-06, 'max_prob': 0.999999, 'duplicate_keys': 0}`

A public win would support the HS-JEPA claim that observed lifestyle context predicts a row-level Q/S hidden vector that can safely steer public-equation posterior actions.
A public loss means the human-state vector prior is locally learnable but not yet calibrated enough to translate into leaderboard action.

## Files

- `hitl/h021_human_state_vector_prior_jepa/h021_vector_prior_configs.csv`
- `hitl/h021_human_state_vector_prior_jepa/h021_test_human_state_vector_prior_rows.csv`
- `hitl/h021_human_state_vector_prior_jepa/h021_test_human_state_vector_prior_cells.csv`
- `hitl/h021_human_state_vector_prior_jepa/h021_candidates.csv`
- `hitl/h021_human_state_vector_prior_jepa/h021_hs_null_stress.csv`
- `hitl/h021_human_state_vector_prior_jepa/h021_report.md`
- `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv`
