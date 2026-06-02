# H072 Human-Social State Engine HS-JEPA

Question: can 1000 human-state stories become an action-grade
route prior, instead of a direct label rule?

Design:

- story text is compressed into human-state families;
- E268 human/social features produce row-level family scores;
- hypothesis routes plus manual priors map families to route templates;
- H071 row-route candidates are rescored by human-route support;
- subject-preserving row permutations test whether the support is a shortcut;
- final submissions only materialize via H071 row-target route actions toward H061 q061.

Family score summary:

| family | mean | p90 | top_rows |
| --- | --- | --- | --- |
| measurement_confidence | 0.500656000 | 0.732706496 | 25 |
| weekend_rhythm | 0.465200000 | 0.730046982 | 25 |
| routine_anchor | 0.502000000 | 0.684247040 | 25 |
| recovery_rest | 0.502000000 | 0.682949440 | 25 |
| nocturnal_awake | 0.502000000 | 0.679349600 | 25 |
| cashflow_stress | 0.502000000 | 0.671692992 | 25 |
| social_load | 0.502000000 | 0.660070720 | 25 |
| bedtime_arousal | 0.502000000 | 0.653775040 | 25 |
| routine_pressure | 0.502000000 | 0.653558080 | 25 |
| body_fatigue | 0.501360000 | 0.644820720 | 25 |
| isolation_cocoon | 0.502000000 | 0.642409520 | 25 |
| badnight_aftereffect | 0.502000000 | 0.633242720 | 25 |

Hypothesis-derived route priors:

| story_family | route_template | hypotheses | weighted_hypotheses | high_priority |
| --- | --- | --- | --- | --- |
| badnight_aftereffect | q3_s_stage | 90 | 207.000000000 | 45 |
| badnight_aftereffect | q_subjective | 20 | 36.000000000 | 5 |
| badnight_aftereffect | q1q3_subjective | 10 | 23.000000000 | 5 |
| badnight_aftereffect | q3_quality | 10 | 23.000000000 | 5 |
| bedtime_arousal | q3_s_stage | 180 | 371.000000000 | 70 |
| bedtime_arousal | q2_s3_tail | 10 | 23.000000000 | 5 |
| bedtime_arousal | s_stage | 10 | 23.000000000 | 5 |
| body_fatigue | q3_s_stage | 40 | 62.000000000 | 5 |
| body_fatigue | s_stage | 10 | 13.600000000 | 0 |
| cashflow_stress | q3_s_stage | 110 | 150.000000000 | 5 |
| cashflow_stress | no_direct | 10 | 23.000000000 | 5 |
| measurement_confidence | no_direct | 10 | 24.400000000 | 6 |
| measurement_confidence | s_stage | 10 | 24.400000000 | 6 |
| measurement_confidence | q3_s_stage | 10 | 23.000000000 | 5 |
| measurement_confidence | s14_edge | 10 | 23.000000000 | 5 |
| nocturnal_awake | q3_s_stage | 20 | 47.400000000 | 11 |
| recovery_rest | q3_s_stage | 100 | 210.000000000 | 40 |
| recovery_rest | recovery_route | 10 | 13.000000000 | 0 |
| routine_pressure | q3_s_stage | 110 | 213.000000000 | 35 |
| routine_pressure | s_stage | 20 | 46.000000000 | 10 |
| social_load | q3_s_stage | 140 | 216.600000000 | 20 |
| social_load | no_direct | 20 | 47.400000000 | 11 |
| social_load | s_stage | 10 | 23.000000000 | 5 |
| social_load | q_subjective | 10 | 13.000000000 | 0 |
| weekend_rhythm | q3_s_stage | 10 | 23.000000000 | 5 |
| weekend_rhythm | s_stage | 10 | 23.000000000 | 5 |

Family-to-latent diagnostics:

| family | mean_score | max_score | auc_h057_seed_row | auc_h068_selected_row | auc_h069_selected_row | auc_h070_selected_row | auc_h071_selected_row | spearman_public_score | spearman_latent_hsjepa | selected_h071_mean | not_selected_h071_mean | family_corr_abs_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| badnight_aftereffect | 0.502000000 | 0.768056000 | 0.485203252 | 0.697236919 | 0.495689655 | 0.458529874 | 0.426114474 | -0.031746172 | -0.107762492 | 0.491609939 | 0.519843800 |  |
| nocturnal_awake | 0.502000000 | 0.852952000 | 0.579945799 | 0.713109935 | 0.529794313 | 0.535704927 | 0.432649972 | -0.065170067 | 0.002215331 | 0.491552339 | 0.519942722 |  |
| bedtime_arousal | 0.502000000 | 0.840728800 | 0.551869919 | 0.719576720 | 0.545296431 | 0.524109015 | 0.480393506 | -0.033515672 | 0.000220036 | 0.498910810 | 0.507305348 |  |
| social_load | 0.502000000 | 0.908664000 | 0.504065041 | 0.587889477 | 0.543481549 | 0.548087002 | 0.524422124 | 0.039044600 | 0.062611062 | 0.503357934 | 0.499667896 |  |
| routine_pressure | 0.502000000 | 0.864208000 | 0.418536585 | 0.561434450 | 0.499924380 | 0.462722746 | 0.491400660 | 0.071304949 | -0.045015888 | 0.502496891 | 0.501146643 |  |
| recovery_rest | 0.502000000 | 0.872920000 | 0.506991870 | 0.420928865 | 0.490471869 | 0.559682914 | 0.513483764 | -0.055724284 | 0.030419815 | 0.502815466 | 0.500599526 |  |
| cashflow_stress | 0.502000000 | 0.863457920 | 0.543414634 | 0.715461493 | 0.555505142 | 0.448571803 | 0.448816731 | -0.004462535 | -0.087694331 | 0.493457722 | 0.516670435 |  |
| measurement_confidence | 0.500656000 | 0.850616320 | 0.418102981 | 0.567901235 | 0.469978826 | 0.379454927 | 0.418409466 | -0.033574809 | -0.164896462 | 0.481933854 | 0.532809251 |  |
| weekend_rhythm | 0.465200000 | 0.920471488 | 0.565962060 | 0.611992945 | 0.499546279 | 0.628341195 | 0.572303247 | -0.001150098 | 0.216938511 | 0.477913424 | 0.443366075 |  |
| body_fatigue | 0.501360000 | 0.773072800 | 0.454742547 | 0.524397413 | 0.497202057 | 0.389806080 | 0.430517336 | -0.033298325 | -0.134435559 | 0.493806172 | 0.514332878 |  |
| isolation_cocoon | 0.502000000 | 0.834050400 | 0.556639566 | 0.439153439 | 0.459618875 | 0.607376834 | 0.542927903 | -0.025697307 | 0.092798541 | 0.504685149 | 0.497388548 |  |
| routine_anchor | 0.502000000 | 0.873073600 | 0.497127371 | 0.510288066 | 0.494517544 | 0.565775681 | 0.515066043 | -0.044997081 | 0.040618642 | 0.502931286 | 0.500400617 |  |
| __geometry__ | 0.498768000 | 0.920471488 |  |  |  |  |  |  |  |  |  | 0.277015424 |

Subject-preserving null stress:

| metric | real | null_mean | null_std | null_p95 | z_vs_null | p_ge_real |
| --- | --- | --- | --- | --- | --- | --- |
| mean_h071_route_support | 0.776796092 | 0.783463390 | 0.005026145 | 0.791539638 | -1.326522796 | 0.903333333 |
| topk_h071_overlap | 0.069620253 | 0.068248945 | 0.007793781 | 0.082278481 | 0.175948978 | 0.653333333 |
| auc_h071_route | 0.769786971 | 0.777508182 | 0.003155003 | 0.782249460 | -2.447290056 | 0.986666667 |
| spearman_assignment | 0.508365568 | 0.510851605 | 0.006538859 | 0.521211521 | -0.380194232 | 0.636666667 |

Top candidates:

| candidate_id | family | max_cells | max_rows | q2_cap | max_per_subject | min_route_score | min_human_support | min_cell_score | novelty | alpha | mode | selected_routes | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | outside_h071_routes | outside_h070_cells | outside_h069_cells | h071_route_overlap | h070_overlap_cells | h069_overlap_cells | h068_overlap_cells | public_action_pred_delta_vs_h057 | posterior_delta_vs_h057 | responsibility_weighted_delta_vs_h057 | max_positive_bad_cosine | mean_h072_route_score | mean_human_route_support | mean_assignment_route_score | mean_cell_assignment_score | mean_public_score | mean_invariant_score | mean_shortcut_energy | h050_null_selected | selected_subjects | route_templates | human_family_templates | bad_cos_submission_h010_ob | bad_cos_submission_e216_ma | bad_cos_submission_e323_55 | bad_cos_submission_jepa_la | bad_cos_submission_lejepa_ | bad_cos_submission_ordinal | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | hash | h071_route_support_null_z | action_rank | posterior_rank | responsibility_rank | human_rank | route_rank | assignment_rank | shortcut_avoid_rank | bad_avoid_rank | outside_h069_ratio | outside_h071_route_ratio | q2_risk | route_diversity | human_family_diversity | bigbet_scale_score | h072_score | file | resolved_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h072_human_route_big_outside_h071_c760_r190_q272_d9986beb | human_route_big | 760 | 190 | 72 | 22 | 0.610000000 | 0.220000000 | 0.350000000 | outside_h071 | 1.000000000 | logit | 138 | 538 | 538 | 138 | 138 | 253 | 465 | 0 | 285 | 73 | 185 | -0.000621507 | -0.000510878 | -0.000577518 | 0.000000000 | 0.777355723 | 1.345150549 | 0.761130638 | 0.681782549 | 0.623791397 | 0.570511232 | 0.243442884 | 0 | 10 | full_state:12;nonq2_full:6;q3_s_stage:105;q_subjective:2;recovery_route:1;s_stage:12 | badnight_aftereffect:6;bedtime_arousal:8;body_fatigue:21;cashflow_stress:7;isolation_cocoon:5;measurement_confidence:9;nocturnal_awake:58;recovery_rest:1;routine_anchor:1;routine_pressure:3;social_load:11;weekend_rhythm:8 | -0.544839812 | -0.548445749 | -0.545708766 | -0.538258922 | -0.533570979 | -0.544174427 | 11 | 9 | 79 | 110 | 123 | 99 | 107 | d9986beb | -1.326522796 | 0.500000000 | 0.625000000 | 0.625000000 | 0.875000000 | 0.750000000 | 0.500000000 | 0.875000000 | 0.500000000 | 0.864312268 | 1.000000000 | 0.016728625 | 6 | 12 | 0.000000000 | 0.753820366 | submission_h072_human_route_big_outside_h071_c760_r190_q272_d9986beb.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_human_route_big_outside_h071_c760_r190_q272_d9986beb.csv |
| h072_human_route_big_outside_h069_c900_r205_q286_4a0705d1 | human_route_big | 900 | 205 | 86 | 25 | 0.580000000 | 0.200000000 | 0.330000000 | outside_h069 | 1.000000000 | logit | 150 | 600 | 600 | 150 | 120 | 297 | 522 | 30 | 303 | 78 | 205 | -0.000733187 | -0.000645721 | -0.000873316 | 0.000000000 | 0.770030215 | 1.333965870 | 0.752392769 | 0.664856300 | 0.612528695 | 0.563635576 | 0.256066762 | 0 | 10 | full_state:25;nonq2_full:10;q3_s_stage:113;s_stage:2 | badnight_aftereffect:7;bedtime_arousal:8;body_fatigue:21;cashflow_stress:8;isolation_cocoon:7;measurement_confidence:2;nocturnal_awake:61;recovery_rest:1;routine_anchor:1;routine_pressure:12;social_load:10;weekend_rhythm:12 | -0.551460337 | -0.555112193 | -0.552509451 | -0.545261717 | -0.540709538 | -0.551003709 | 22 | 23 | 92 | 116 | 126 | 107 | 114 | 4a0705d1 | -1.326522796 | 0.875000000 | 0.875000000 | 0.875000000 | 0.625000000 | 0.625000000 | 0.375000000 | 0.375000000 | 0.500000000 | 0.870000000 | 0.800000000 | 0.038333333 | 4 | 12 | 0.000000000 | 0.748128571 | submission_h072_human_route_big_outside_h069_c900_r205_q286_4a0705d1.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_human_route_big_outside_h069_c900_r205_q286_4a0705d1.csv |
| h072_anti_shortcut_human_big_anti_shortcut_c760_r205_q260_ffc9a916 | anti_shortcut_human_big | 760 | 205 | 60 | 24 | 0.560000000 | 0.200000000 | 0.330000000 | anti_shortcut | 1.000000000 | logit | 132 | 559 | 559 | 132 | 104 | 269 | 480 | 28 | 290 | 79 | 199 | -0.000649171 | -0.000478025 | -0.000403293 | 0.000000000 | 0.780479831 | 1.308037463 | 0.783514030 | 0.673232783 | 0.619328515 | 0.556952957 | 0.244360772 | 0 | 10 | full_state:6;nonq2_full:11;q2_s3_tail:3;q3_s_stage:99;q_subjective:3;recovery_route:5;s_stage:5 | badnight_aftereffect:6;bedtime_arousal:7;body_fatigue:20;cashflow_stress:9;isolation_cocoon:12;measurement_confidence:3;nocturnal_awake:56;recovery_rest:1;routine_anchor:3;routine_pressure:3;social_load:7;weekend_rhythm:5 | -0.508425435 | -0.512104335 | -0.509380017 | -0.503352055 | -0.497157096 | -0.505151523 | 24 | 11 | 83 | 112 | 118 | 104 | 107 | ffc9a916 | -1.326522796 | 0.625000000 | 0.500000000 | 0.375000000 | 0.500000000 | 0.875000000 | 0.875000000 | 0.750000000 | 0.500000000 | 0.858676208 | 0.787878788 | 0.019677996 | 7 | 12 | 0.000000000 | 0.699346032 | submission_h072_anti_shortcut_human_big_anti_shortcut_c760_r205_q260_ffc9a916.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_anti_shortcut_human_big_anti_shortcut_c760_r205_q260_ffc9a916.csv |
| h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae | fullvector_social_state | 980 | 220 | 90 | 25 | 0.530000000 | 0.180000000 | 0.300000000 | outside_h069 | 1.000000000 | logit | 148 | 704 | 704 | 148 | 97 | 383 | 613 | 51 | 321 | 91 | 245 | -0.000921626 | -0.000696049 | -0.000934844 | 0.000000000 | 0.727490880 | 0.885505991 | 0.748307904 | 0.633245938 | 0.597853068 | 0.563827143 | 0.282149107 | 0 | 10 | full_state:117;nonq2_full:3;q3_s_stage:25;q_subjective:2;s_stage:1 | badnight_aftereffect:8;bedtime_arousal:10;routine_pressure:66;social_load:19;weekend_rhythm:45 | -0.596109399 | -0.599408244 | -0.596531848 | -0.591152227 | -0.586945656 | -0.596141919 | 87 | 75 | 90 | 116 | 117 | 109 | 110 | bae1edae | -1.326522796 | 1.000000000 | 1.000000000 | 1.000000000 | 0.250000000 | 0.125000000 | 0.250000000 | 0.125000000 | 0.500000000 | 0.870738636 | 0.655405405 | 0.106534091 | 5 | 5 | 0.101355140 | 0.629855109 | submission_h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae.csv |
| h072_cashflow_routine_big_outside_h069_c640_r180_q286_fd6e1e4c | cashflow_routine_big | 640 | 180 | 86 | 22 | 0.520000000 | 0.200000000 | 0.320000000 | outside_h069 | 1.000000000 | logit | 115 | 615 | 615 | 115 | 62 | 308 | 533 | 53 | 307 | 82 | 210 | -0.000724444 | -0.000621406 | -0.000797116 | 0.000000000 | 0.759939240 | 0.809406159 | 0.805036311 | 0.654661273 | 0.614874267 | 0.588088037 | 0.273098072 | 0 | 10 | full_state:102;nonq2_full:5;q2_s3_tail:1;q3_s_stage:7 | cashflow_stress:14;routine_pressure:58;weekend_rhythm:43 | -0.523614524 | -0.528186602 | -0.525464242 | -0.519261653 | -0.514792885 | -0.524398513 | 82 | 64 | 83 | 98 | 105 | 90 | 93 | fd6e1e4c | -1.326522796 | 0.750000000 | 0.750000000 | 0.750000000 | 0.125000000 | 0.500000000 | 1.000000000 | 0.250000000 | 0.500000000 | 0.866666667 | 0.539130435 | 0.104065041 | 4 | 3 | 0.000000000 | 0.596623075 | submission_h072_cashflow_routine_big_outside_h069_c640_r180_q286_fd6e1e4c.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_cashflow_routine_big_outside_h069_c640_r180_q286_fd6e1e4c.csv |
| h072_measurement_stage_big_anti_shortcut_c660_r190_q20_af0baff3 | measurement_stage_big | 660 | 190 | 0 | 24 | 0.540000000 | 0.200000000 | 0.330000000 | anti_shortcut | 1.000000000 | logit | 110 | 452 | 452 | 110 | 96 | 225 | 386 | 14 | 227 | 66 | 161 | -0.000478053 | -0.000355844 | -0.000277518 | 0.000000000 | 0.784313376 | 1.341482128 | 0.783054389 | 0.676437187 | 0.615003578 | 0.553380904 | 0.238879298 | 0 | 10 | nonq2_full:1;q3_s_stage:83;s_stage:26 | body_fatigue:22;measurement_confidence:24;nocturnal_awake:64 | -0.453109819 | -0.455589361 | -0.452860478 | -0.445984123 | -0.440057202 | -0.449396031 | 1 | 0 | 62 | 101 | 104 | 89 | 95 | af0baff3 | -1.326522796 | 0.125000000 | 0.125000000 | 0.125000000 | 0.750000000 | 1.000000000 | 0.750000000 | 1.000000000 | 0.500000000 | 0.853982301 | 0.872727273 | 0.000000000 | 3 | 3 | 0.000000000 | 0.596265113 | submission_h072_measurement_stage_big_anti_shortcut_c660_r190_q20_af0baff3.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_measurement_stage_big_anti_shortcut_c660_r190_q20_af0baff3.csv |
| h072_bedtime_social_big_outside_h069_c720_r185_q274_6413be13 | bedtime_social_big | 720 | 185 | 74 | 24 | 0.550000000 | 0.210000000 | 0.330000000 | outside_h069 | 1.000000000 | logit | 123 | 455 | 455 | 123 | 111 | 226 | 389 | 12 | 229 | 66 | 166 | -0.000569292 | -0.000417144 | -0.000505280 | 0.000000000 | 0.756874140 | 1.438461114 | 0.728941561 | 0.668294744 | 0.614617771 | 0.573632571 | 0.255941601 | 0 | 10 | full_state:2;q3_s_stage:109;q_subjective:12 | badnight_aftereffect:8;bedtime_arousal:11;nocturnal_awake:82;social_load:22 | -0.478715055 | -0.480377630 | -0.478282140 | -0.474709398 | -0.471626662 | -0.479785806 | 9 | 10 | 78 | 92 | 97 | 83 | 86 | 6413be13 | -1.326522796 | 0.250000000 | 0.250000000 | 0.500000000 | 1.000000000 | 0.375000000 | 0.125000000 | 0.500000000 | 0.500000000 | 0.854945055 | 0.902439024 | 0.021978022 | 3 | 4 | 0.000000000 | 0.560633432 | submission_h072_bedtime_social_big_outside_h069_c720_r185_q274_6413be13.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_bedtime_social_big_outside_h069_c720_r185_q274_6413be13.csv |
| h072_recovery_objective_big_outside_h069_c760_r200_q224_b56d61ba | recovery_objective_big | 760 | 200 | 24 | 24 | 0.550000000 | 0.200000000 | 0.330000000 | outside_h069 | 1.000000000 | logit | 138 | 584 | 584 | 138 | 97 | 295 | 502 | 41 | 289 | 82 | 206 | -0.000573594 | -0.000468092 | -0.000368811 | 0.000000000 | 0.742139190 | 0.904349710 | 0.767767768 | 0.664227495 | 0.609937202 | 0.553962931 | 0.255567735 | 0 | 10 | nonq2_full:69;q3_s_stage:24;recovery_route:4;s_stage:41 | body_fatigue:25;isolation_cocoon:57;measurement_confidence:40;recovery_rest:4;routine_anchor:12 | -0.484398622 | -0.487340928 | -0.484468375 | -0.480856225 | -0.474861796 | -0.487222171 | 64 | 0 | 68 | 109 | 123 | 107 | 113 | b56d61ba | -1.326522796 | 0.375000000 | 0.375000000 | 0.250000000 | 0.375000000 | 0.250000000 | 0.625000000 | 0.625000000 | 0.500000000 | 0.859589041 | 0.702898551 | 0.000000000 | 4 | 5 | 0.000000000 | 0.481481678 | submission_h072_recovery_objective_big_outside_h069_c760_r200_q224_b56d61ba.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_recovery_objective_big_outside_h069_c760_r200_q224_b56d61ba.csv |

Decision:

| decision | selected_candidate_id | selected_file | selected_resolved_path | root_uploadsafe_path | worldview | candidate_id | family | max_cells | max_rows | q2_cap | max_per_subject | min_route_score | min_human_support | min_cell_score | novelty | alpha | mode | selected_routes | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | outside_h071_routes | outside_h070_cells | outside_h069_cells | h071_route_overlap | h070_overlap_cells | h069_overlap_cells | h068_overlap_cells | public_action_pred_delta_vs_h057 | posterior_delta_vs_h057 | responsibility_weighted_delta_vs_h057 | max_positive_bad_cosine | mean_h072_route_score | mean_human_route_support | mean_assignment_route_score | mean_cell_assignment_score | mean_public_score | mean_invariant_score | mean_shortcut_energy | h050_null_selected | selected_subjects | route_templates | human_family_templates | bad_cos_submission_h010_ob | bad_cos_submission_e216_ma | bad_cos_submission_e323_55 | bad_cos_submission_jepa_la | bad_cos_submission_lejepa_ | bad_cos_submission_ordinal | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | hash | h071_route_support_null_z | action_rank | posterior_rank | responsibility_rank | human_rank | route_rank | assignment_rank | shortcut_avoid_rank | bad_avoid_rank | outside_h069_ratio | outside_h071_route_ratio | q2_risk | route_diversity | human_family_diversity | bigbet_scale_score | h072_score | file | resolved_path | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_humansocial_route_sensor_null_failed | h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae | submission_h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae.csv | /Users/kbsoo/Downloads/cl2/submission_h072_humansocial_route_bae1edae_uploadsafe.csv | human-social route priors create a large action-health candidate, but null stress does not yet prove they recover H071-like hidden routes | h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae | fullvector_social_state | 980 | 220 | 90 | 25 | 0.530000000 | 0.180000000 | 0.300000000 | outside_h069 | 1.000000000 | logit | 148 | 704 | 704 | 148 | 97 | 383 | 613 | 51 | 321 | 91 | 245 | -0.000921626 | -0.000696049 | -0.000934844 | 0.000000000 | 0.727490880 | 0.885505991 | 0.748307904 | 0.633245938 | 0.597853068 | 0.563827143 | 0.282149107 | 0 | 10 | full_state:117;nonq2_full:3;q3_s_stage:25;q_subjective:2;s_stage:1 | badnight_aftereffect:8;bedtime_arousal:10;routine_pressure:66;social_load:19;weekend_rhythm:45 | -0.596109399 | -0.599408244 | -0.596531848 | -0.591152227 | -0.586945656 | -0.596141919 | 87 | 75 | 90 | 116 | 117 | 109 | 110 | bae1edae | -1.326522796 | 1.000000000 | 1.000000000 | 1.000000000 | 0.250000000 | 0.125000000 | 0.250000000 | 0.125000000 | 0.500000000 | 0.870738636 | 0.655405405 | 0.106534091 | 5 | 5 | 0.101355140 | 0.629855109 | submission_h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae.csv | /Users/kbsoo/Downloads/cl2/hitl/h072_human_social_state_engine_jepa/submission_h072_fullvector_social_state_outside_h069_c980_r220_q290_bae1edae.csv | /Users/kbsoo/Downloads/cl2/submission_h072_humansocial_route_bae1edae_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999999000 | 704 | True |

Interpretation rule:

- If H072 wins by >= 0.001, human-social stories are an action-grade HS-JEPA context view.
- If H072 loses mildly but H071 wins, story families are explanatory priors but not yet route selectors.
- If H072 loses badly, direct human story routing is too noisy and H073 should use anti-shortcut inversion.

Family columns: family_badnight_aftereffect, family_nocturnal_awake, family_bedtime_arousal, family_social_load, family_routine_pressure, family_recovery_rest, family_cashflow_stress, family_measurement_confidence, family_weekend_rhythm, family_body_fatigue, family_isolation_cocoon, family_routine_anchor
