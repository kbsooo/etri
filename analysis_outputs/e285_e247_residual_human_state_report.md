# E285 E247-Residual Human-State Audit

## Question

Can human/social diary state produce an E247-relative preserve/undo/avoid rule, instead of using stale E224/E154 rollback targets?

## Human Boundary Features

| feature | mean_e247_only | mean_e256_only | mean_neither | e247_vs_e256_d | e247_vs_neither_d | e256_vs_neither_d | abs_boundary_signal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| amp_z | 0.103083437 | 2.295608278 | -0.198576937 | -2.192524841 | 0.301660374 | 2.494185215 | 2.192524841 |
| state_amp_z | 0.033043050 | 1.680842446 | -0.055823271 | -1.647799396 | 0.088866320 | 1.736665717 | 1.647799396 |
| z_paymonth_start_post3_late_shopping_subj_z | 1.086912704 | -0.358596195 | -0.031529994 | 1.445508898 | 1.118442697 | -0.327066201 | 1.445508898 |
| z_paymonth_start_near3_money_rumination_subj_z | 1.088196432 | -0.071351893 | -0.033861373 | 1.159548325 | 1.122057805 | -0.037490520 | 1.159548325 |
| z_diary_state_pc8 | 0.195939165 | -0.915905363 | -0.018905162 | 1.111844528 | 0.214844327 | -0.897000200 | 1.111844528 |
| z_diary_state_pc6 | -0.446233907 | 0.652173120 | 0.021350126 | -1.098407028 | -0.467584033 | 0.630822995 | 1.098407028 |
| z_diary_state_k8_5 | -0.243561150 | 0.843765413 | 0.002625996 | -1.087326563 | -0.246187146 | 0.841139417 | 1.087326563 |
| z_diary_state_k10_4 | -0.243561150 | 0.843765413 | 0.002625996 | -1.087326563 | -0.246187146 | 0.841139417 | 1.087326563 |
| z_jepa_resid_dateblock_cognitive_money | 0.506603578 | -0.550993630 | 0.010893152 | 1.057597208 | 0.495710426 | -0.561886782 | 1.057597208 |
| z_diary_state_k6_3 | -0.261488180 | 0.759950024 | 0.008325685 | -1.021438204 | -0.269813865 | 0.751624339 | 1.021438204 |
| smooth_z | 1.210617003 | 0.248751850 | -0.264156066 | 0.961865153 | 1.474773069 | 0.512907916 | 0.961865153 |
| z_pay15_post3_late_shopping_subj_z | -0.204434897 | 0.754300264 | -0.006569134 | -0.958735161 | -0.197865763 | 0.760869398 | 0.958735161 |
| z_jepa_prednorm_subject_social_comm | -0.629928193 | 0.324992809 | 0.015543466 | -0.954921002 | -0.645471658 | 0.309449344 | 0.954921002 |
| z_jepa_prednorm_dateblock_bedtime_phone | 0.281024262 | -0.552059739 | -0.020253557 | 0.833084001 | 0.301277819 | -0.531806182 | 0.833084001 |
| z_jepa_prednorm_dateblock_mobility_context | -0.379804153 | 0.403931210 | -0.000753594 | -0.783735362 | -0.379050559 | 0.404684803 | 0.783735362 |
| z_cognitive_money_energy | 0.379916909 | -0.376887254 | 0.013159156 | 0.756804163 | 0.366757753 | -0.390046410 | 0.756804163 |
| z_bright_light_late_subj_z | 0.033665291 | 0.782216992 | -0.025956228 | -0.748551701 | 0.059621519 | 0.808173220 | 0.748551701 |
| z_jepa_resid_subject_cognitive_money | 0.324141316 | -0.378250303 | 0.012773776 | 0.702391618 | 0.311367540 | -0.391024078 | 0.702391618 |
| z_weekend_social_jetlag_subj_z | -0.040482693 | -0.730754507 | 0.020599695 | 0.690271814 | -0.061082388 | -0.751354202 | 0.690271814 |
| z_jepa_prednorm_subject_mobility_context | -0.484484396 | 0.174658014 | 0.013832040 | -0.659142410 | -0.498316436 | 0.160825974 | 0.659142410 |
| z_diary_state_pc5 | -0.034199495 | 0.614621777 | -0.006818692 | -0.648821272 | -0.027380803 | 0.621440469 | 0.648821272 |
| z_diary_state_k8_0 | -0.481172623 | 0.158684589 | 0.001738480 | -0.639857212 | -0.482911103 | 0.156946109 | 0.639857212 |
| z_mobility_context_energy | -0.446000056 | 0.185833934 | 0.015631777 | -0.631833990 | -0.461631832 | 0.170202158 | 0.631833990 |
| z_phone_in_bed_subj_z | 0.476692700 | -0.150352413 | -0.000086045 | 0.627045113 | 0.476778744 | -0.150266368 | 0.627045113 |

## Cell Group Anatomy

| group | n_rows | e237_overlap | e230_swing_overlap | e230_risk_overlap | single_row_smooth_gain_sum_mean | single_row_smooth_gain_sum_median | rollback_amp_abs_mean | rollback_amp_abs_median | app_state_avg_z_mean | app_state_avg_z_median | app_story_score_mean | app_story_score_median | state_amp_z_mean | state_amp_z_median | e284_select_count_mean | e284_select_count_median | e284_score_max_mean | e284_score_max_median | nn_dist_mean | nn_dist_median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e247_common | 21 | 13 | 10 | 7 | 0.121572885 | 0.087624411 | 0.084600496 | 0.076433549 | 0.099883025 | 0.112987941 | -0.130371231 | -0.557958040 | 0.222933521 | 0.042027708 | 2.380952381 | 1.000000000 | 0.032832544 | 0.043501146 | 10.602562428 | 8.400505751 |
| e247_only | 13 | 0 | 0 | 0 | 0.077142999 | 0.077662709 | 0.039125051 | 0.038831354 | 0.235262155 | 0.266751516 | 0.570663416 | 0.752707008 | 0.033043050 | 0.012466512 | 0.538461538 | 0.000000000 | 0.013501909 | 0.000000000 | 6.118931537 | 5.832526616 |
| e256_only | 4 | 1 | 4 | 0 | 0.012322468 | 0.009735247 | 0.110316918 | 0.108228172 | 0.719623888 | 0.732049311 | 1.142024398 | 0.961202852 | 1.680842446 | 1.466271544 | 0.250000000 | 0.000000000 | 0.007883023 | 0.000000000 | 7.230545594 | 7.126368780 |
| e284_extra | 50 | 10 | 10 | 8 | -0.040740737 | -0.037035163 | 0.050281271 | 0.044367328 | 0.182224499 | 0.317369327 | 0.116720077 | 0.225712356 | 0.089064940 | -0.007683500 | 2.520000000 | 2.500000000 | 0.045883649 | 0.043501146 | 7.560341769 | 7.587594230 |
| neither | 212 | 11 | 11 | 14 | -0.022242629 | -0.008011203 | 0.029330058 | 0.022533769 | 0.058279146 | 0.157312483 | 0.001254692 | 0.145547465 | -0.055823271 | -0.068301684 | 0.589622642 | 0.000000000 | 0.010672879 | 0.000000000 | 7.221184574 | 6.967129993 |

## Candidate Tensor Families

- materialized candidates: `158`
- current-anchor selected models: `1`
- old strict-promote candidates: `0`
- matched-placebo gate passes: `0`
- public-free ready candidates: `0`

### Candidate Anatomy

| candidate_id | action | fraction | rule_family | row_count | e247_overlap | e256_overlap | e284_overlap | sum_smooth_gain | mean_amp | mean_app_state | mean_app_story | mean_state_amp_z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| undo_high_amp_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | 3 | 3 | 2 | 0.553107112 | 0.140772075 | 0.587944845 | 0.077875374 | 1.796120081 |
| undo_high_amp_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | 3 | 3 | 2 | 0.553107112 | 0.140772075 | 0.587944845 | 0.077875374 | 1.796120081 |
| undo_high_amp_top5_f0p25 | undo | 0.250000000 | e247_undo_rank | 5 | 5 | 5 | 4 | 0.765986506 | 0.127039124 | 0.620080067 | 0.265801751 | 1.856084984 |
| undo_high_amp_top5_f0p5 | undo | 0.500000000 | e247_undo_rank | 5 | 5 | 5 | 4 | 0.765986506 | 0.127039124 | 0.620080067 | 0.265801751 | 1.856084984 |
| undo_high_amp_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | 8 | 8 | 5 | 1.110391241 | 0.111657174 | 0.313997890 | 0.161373315 | 0.932444516 |
| undo_high_amp_top8_f0p5 | undo | 0.500000000 | e247_undo_rank | 8 | 8 | 8 | 5 | 1.110391241 | 0.111657174 | 0.313997890 | 0.161373315 | 0.932444516 |
| undo_high_e284_oldlaw_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | 3 | 3 | 3 | 0.271176971 | 0.064914474 | 0.857179354 | 0.520439801 | 0.565454915 |
| undo_high_e284_oldlaw_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | 3 | 3 | 3 | 0.271176971 | 0.064914474 | 0.857179354 | 0.520439801 | 0.565454915 |
| undo_high_e284_oldlaw_top5_f0p25 | undo | 0.250000000 | e247_undo_rank | 5 | 5 | 4 | 5 | 0.454051165 | 0.064519888 | 0.726826755 | 0.674159015 | 0.520944630 |
| undo_high_e284_oldlaw_top5_f0p5 | undo | 0.500000000 | e247_undo_rank | 5 | 5 | 4 | 5 | 0.454051165 | 0.064519888 | 0.726826755 | 0.674159015 | 0.520944630 |
| undo_high_e284_oldlaw_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | 8 | 7 | 8 | 0.785154955 | 0.081712904 | 0.340107493 | 0.100935021 | 0.027595069 |
| undo_high_e284_oldlaw_top8_f0p5 | undo | 0.500000000 | e247_undo_rank | 8 | 8 | 7 | 8 | 0.785154955 | 0.081712904 | 0.340107493 | 0.100935021 | 0.027595069 |
| undo_high_state_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | 3 | 3 | 3 | 0.243564856 | 0.081188285 | 1.374942433 | 1.070965073 | 2.078719774 |
| undo_high_state_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | 3 | 3 | 3 | 0.243564856 | 0.081188285 | 1.374942433 | 1.070965073 | 2.078719774 |
| undo_high_state_top5_f0p25 | undo | 0.250000000 | e247_undo_rank | 5 | 5 | 4 | 3 | 0.558691048 | 0.080225590 | 1.265934611 | 1.105167059 | 1.885394823 |
| undo_high_state_top5_f0p5 | undo | 0.500000000 | e247_undo_rank | 5 | 5 | 4 | 3 | 0.558691048 | 0.080225590 | 1.265934611 | 1.105167059 | 1.885394823 |
| undo_high_state_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | 8 | 5 | 4 | 0.811229543 | 0.071214631 | 1.079201802 | 1.322053494 | 1.388944412 |
| undo_high_state_top8_f0p5 | undo | 0.500000000 | e247_undo_rank | 8 | 8 | 5 | 4 | 0.811229543 | 0.071214631 | 1.079201802 | 1.322053494 | 1.388944412 |
| undo_high_stateamp_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | 3 | 3 | 2 | 0.513806864 | 0.127671993 | 0.955429029 | 0.973264656 | 3.039968929 |
| undo_high_stateamp_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | 3 | 3 | 2 | 0.513806864 | 0.127671993 | 0.955429029 | 0.973264656 | 3.039968929 |
| undo_high_stateamp_top5_f0p25 | undo | 0.250000000 | e247_undo_rank | 5 | 5 | 5 | 3 | 0.657522546 | 0.105346332 | 1.053240025 | 1.147326935 | 2.373797195 |
| undo_high_stateamp_top5_f0p5 | undo | 0.500000000 | e247_undo_rank | 5 | 5 | 5 | 3 | 0.657522546 | 0.105346332 | 1.053240025 | 1.147326935 | 2.373797195 |
| undo_high_stateamp_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | 8 | 8 | 6 | 0.869063731 | 0.092284106 | 0.955693244 | 1.080455833 | 1.770625232 |
| undo_high_stateamp_top8_f0p5 | undo | 0.500000000 | e247_undo_rank | 8 | 8 | 8 | 6 | 0.869063731 | 0.092284106 | 0.955693244 | 1.080455833 | 1.770625232 |
| undo_high_story_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | 3 | 1 | 1 | 0.252538495 | 0.056196367 | 0.767980455 | 1.683530885 | 0.561527059 |
| undo_high_story_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | 3 | 1 | 1 | 0.252538495 | 0.056196367 | 0.767980455 | 1.683530885 | 0.561527059 |
| undo_high_story_top5_f0p25 | undo | 0.250000000 | e247_undo_rank | 5 | 5 | 3 | 3 | 0.384610234 | 0.060132168 | 0.857284612 | 1.511125713 | 0.697883214 |
| undo_high_story_top5_f0p5 | undo | 0.500000000 | e247_undo_rank | 5 | 5 | 3 | 3 | 0.384610234 | 0.060132168 | 0.857284612 | 1.511125713 | 0.697883214 |
| undo_high_story_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | 8 | 5 | 4 | 0.758812403 | 0.064662489 | 0.995789468 | 1.372048373 | 0.985920719 |
| undo_high_story_top8_f0p5 | undo | 0.500000000 | e247_undo_rank | 8 | 8 | 5 | 4 | 0.758812403 | 0.064662489 | 0.995789468 | 1.372048373 | 0.985920719 |
| undo_low_smooth_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | 3 | 0 | 1 | 0.156661408 | 0.034821210 | 0.507731990 | 0.559020722 | -0.065474161 |
| undo_low_smooth_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | 3 | 0 | 1 | 0.156661408 | 0.034821210 | 0.507731990 | 0.559020722 | -0.065474161 |
| undo_low_smooth_top5_f0p25 | undo | 0.250000000 | e247_undo_rank | 5 | 5 | 1 | 3 | 0.273160544 | 0.038450237 | 0.751904303 | 0.909263168 | 0.158031390 |
| undo_low_smooth_top5_f0p5 | undo | 0.500000000 | e247_undo_rank | 5 | 5 | 1 | 3 | 0.273160544 | 0.038450237 | 0.751904303 | 0.909263168 | 0.158031390 |
| undo_low_smooth_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | 8 | 3 | 5 | 0.452825116 | 0.042692401 | 0.501396031 | 0.561636538 | 0.291535960 |
| undo_low_smooth_top8_f0p5 | undo | 0.500000000 | e247_undo_rank | 8 | 8 | 3 | 5 | 0.452825116 | 0.042692401 | 0.501396031 | 0.561636538 | 0.291535960 |
| undo_low_state_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | 3 | 2 | 1 | 0.214991017 | 0.061538157 | -1.384188036 | -1.194829240 | -1.483202512 |
| undo_low_state_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | 3 | 2 | 1 | 0.214991017 | 0.061538157 | -1.384188036 | -1.194829240 | -1.483202512 |
| undo_low_state_top5_f0p25 | undo | 0.250000000 | e247_undo_rank | 5 | 5 | 4 | 1 | 0.516675815 | 0.060921526 | -1.198311368 | -1.096794741 | -1.274363048 |
| undo_low_state_top5_f0p5 | undo | 0.500000000 | e247_undo_rank | 5 | 5 | 4 | 1 | 0.516675815 | 0.060921526 | -1.198311368 | -1.096794741 | -1.274363048 |
| undo_low_state_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | 8 | 7 | 2 | 0.906339307 | 0.067024679 | -0.885519799 | -1.090954237 | -1.068058946 |
| undo_low_state_top8_f0p5 | undo | 0.500000000 | e247_undo_rank | 8 | 8 | 7 | 2 | 0.906339307 | 0.067024679 | -0.885519799 | -1.090954237 | -1.068058946 |
| add_e247like_amp_z_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | 0 | 0 | 0 | 0.082802822 | 0.004465434 | -1.057078403 | -1.288974729 | 1.299450861 |
| add_e247like_amp_z_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | 0 | 0 | 0 | 0.130272531 | 0.005843908 | -0.518536018 | -0.592063158 | 0.688091339 |
| add_e247like_state_amp_z_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | 0 | 0 | 1 | -0.144851837 | 0.048283946 | 1.183348673 | 1.277997352 | -3.582163976 |
| add_e247like_state_amp_z_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | 0 | 0 | 1 | -0.153550851 | 0.030705970 | 1.321389709 | 1.291122475 | -2.855459757 |
| add_e247like_z_diary_state_k8_5_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | 0 | 0 | 2 | 0.144111638 | 0.038588588 | 0.534076324 | 0.563904561 | 0.099677097 |
| add_e247like_z_diary_state_k8_5_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | 0 | 0 | 3 | 0.236647126 | 0.041660250 | 0.589716312 | 0.556470827 | 0.140370071 |
| add_e247like_z_diary_state_pc6_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | 0 | 0 | 1 | 0.009543440 | 0.043626026 | -0.297644012 | -0.541615761 | -0.151663145 |
| add_e247like_z_diary_state_pc6_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | 0 | 0 | 1 | 0.013521425 | 0.037013887 | -0.007106100 | -0.815397362 | -0.152289556 |

### Current-Anchor Governor

| basename | candidate_id | action | fraction | rule_family | row_count | final_decision | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | matched_placebo_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e285_e247resid_add_e247like_z_diary_state_pc6_top5_f0p25_6f3cde41.csv | add_e247like_z_diary_state_pc6_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | too_small_to_submit | too_small_to_submit | -0.000005761 | -0.000003481 | 0.000000000 | 0.952380952 | 0.857142857 | False |
| submission_e285_e247resid_add_e247like_z_diary_state_pc6_top3_f0p25_ce425c66.csv | add_e247like_z_diary_state_pc6_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | too_small_to_submit | too_small_to_submit | -0.000005783 | -0.000003441 | 0.000000000 | 0.952380952 | 0.857142857 | False |
| submission_e285_e247resid_add_e247like_z_paymonth_start_near3_money_ruminat_top3_f0p25_4b8ece82.csv | add_e247like_z_paymonth_start_near3_money_ruminat_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | too_small_to_submit | too_small_to_submit | -0.000003007 | -0.000002061 | 0.000000000 | 0.476190476 | 0.142857143 | False |
| submission_e285_e247resid_add_e247like_z_paymonth_start_near3_money_ruminat_top5_f0p25_cbd476c5.csv | add_e247like_z_paymonth_start_near3_money_ruminat_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | too_small_to_submit | too_small_to_submit | -0.000002915 | -0.000001973 | 0.000000000 | 0.285714286 | 0.142857143 | False |
| submission_e285_e247resid_add_e247like_z_diary_state_pc8_top3_f0p25_dd573e4b.csv | add_e247like_z_diary_state_pc8_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | too_small_to_submit | too_small_to_submit | -0.000002779 | -0.000001933 | 0.000000000 | 0.523809524 | 0.428571429 | False |
| submission_e285_e247resid_add_e247like_z_jepa_resid_dateblock_cognitive_mon_top5_f0p25_4e51fe88.csv | add_e247like_z_jepa_resid_dateblock_cognitive_mon_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | too_small_to_submit | too_small_to_submit | -0.000002696 | -0.000001837 | 0.000000000 | 0.142857143 | 0.000000000 | False |
| submission_e285_e247resid_add_e247like_state_amp_z_top5_f0p25_b9b18348.csv | add_e247like_state_amp_z_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | too_small_to_submit | too_small_to_submit | -0.000002505 | -0.000000969 | 0.000000000 | 0.238095238 | 0.142857143 | False |
| submission_e285_e247resid_add_e247like_z_paymonth_start_post3_late_shopping_top3_f0p25_74c45584.csv | add_e247like_z_paymonth_start_post3_late_shopping_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | too_small_to_submit | too_small_to_submit | -0.000001356 | -0.000000942 | 0.000000000 | 0.476190476 | 0.428571429 | False |
| submission_e285_e247resid_undo_e247like_ctrl_amp_z_top5_f0p5_d58bb5f7.csv | undo_e247like_ctrl_amp_z_top5_f0p5 | undo | 0.500000000 | human_boundary_control | 5 | too_small_to_submit | too_small_to_submit | -0.000002007 | -0.000000902 | 0.000000000 | 0.666666667 | 0.571428571 | False |
| submission_e285_e247resid_add_e247like_state_amp_z_top3_f0p25_327a71a9.csv | add_e247like_state_amp_z_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | too_small_to_submit | too_small_to_submit | -0.000002289 | -0.000000824 | 0.000000000 | 0.285714286 | 0.285714286 | False |
| submission_e285_e247resid_undo_e247like_ctrl_amp_z_top3_f0p5_e14e7b45.csv | undo_e247like_ctrl_amp_z_top3_f0p5 | undo | 0.500000000 | human_boundary_control | 3 | too_small_to_submit | too_small_to_submit | -0.000001691 | -0.000000703 | 0.000000000 | 0.666666667 | 0.285714286 | False |
| submission_e285_e247resid_add_e247like_z_jepa_prednorm_dateblock_bedtime_ph_top5_f0p25_3fa2fad3.csv | add_e247like_z_jepa_prednorm_dateblock_bedtime_ph_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | too_small_to_submit | too_small_to_submit | -0.000000945 | -0.000000650 | 0.000000000 | 0.190476190 | 0.000000000 | False |
| submission_e285_e247resid_undo_e247like_ctrl_amp_z_top5_f0p25_b16a2cee.csv | undo_e247like_ctrl_amp_z_top5_f0p25 | undo | 0.250000000 | human_boundary_control | 5 | too_small_to_submit | too_small_to_submit | -0.000001010 | -0.000000456 | 0.000000000 | 0.523809524 | 0.428571429 | False |
| submission_e285_e247resid_add_e247like_z_jepa_resid_dateblock_cognitive_mon_top3_f0p25_adf0c040.csv | add_e247like_z_jepa_resid_dateblock_cognitive_mon_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | too_small_to_submit | too_small_to_submit | -0.000000757 | -0.000000354 | 0.000000000 | 0.142857143 | 0.000000000 | False |
| submission_e285_e247resid_undo_e247like_ctrl_amp_z_top3_f0p25_1a236769.csv | undo_e247like_ctrl_amp_z_top3_f0p25 | undo | 0.250000000 | human_boundary_control | 3 | too_small_to_submit | too_small_to_submit | -0.000000849 | -0.000000354 | 0.000000000 | 0.809523810 | 0.428571429 | False |
| submission_e285_e247resid_add_e247like_z_paymonth_start_post3_late_shopping_top5_f0p25_56165483.csv | add_e247like_z_paymonth_start_post3_late_shopping_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | too_small_to_submit | too_small_to_submit | -0.000001028 | -0.000000342 | 0.000000000 | 0.095238095 | 0.000000000 | False |
| submission_e285_e247resid_add_e247like_z_diary_state_pc8_top5_f0p25_19a52f10.csv | add_e247like_z_diary_state_pc8_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | below_selector_resolution | below_selector_resolution | -0.000000061 | 0.000000286 | 0.000000000 | 0.142857143 | 0.000000000 | False |
| submission_e285_e247resid_add_e247like_amp_z_top3_f0p25_aa6c6b32.csv | add_e247like_amp_z_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | below_selector_resolution | below_selector_resolution | 0.000000273 | 0.000000365 | 0.000000000 | 0.952380952 | 0.857142857 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_paymonth_start_post3_late_sh_top3_f0p25_7396655f.csv | undo_e247like_ctrl_z_paymonth_start_post3_late_sh_top3_f0p25 | undo | 0.250000000 | human_boundary_control | 3 | too_small_to_submit | too_small_to_submit | -0.000000359 | 0.000000458 | 0.000000000 | 0.285714286 | 0.000000000 | False |
| submission_e285_e247resid_add_e247like_amp_z_top5_f0p25_8cc563b4.csv | add_e247like_amp_z_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | below_selector_resolution | below_selector_resolution | 0.000000491 | 0.000000608 | 0.000000000 | 0.619047619 | 0.428571429 | False |
| submission_e285_e247resid_add_e247like_z_jepa_prednorm_dateblock_bedtime_ph_top3_f0p25_923b3c1b.csv | add_e247like_z_jepa_prednorm_dateblock_bedtime_ph_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | below_selector_resolution | below_selector_resolution | 0.000000475 | 0.000000883 | 0.000000000 | 0.047619048 | 0.000000000 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_paymonth_start_post3_late_sh_top3_f0p5_ae4564c4.csv | undo_e247like_ctrl_z_paymonth_start_post3_late_sh_top3_f0p5 | undo | 0.500000000 | human_boundary_control | 3 | too_small_to_submit | too_small_to_submit | -0.000000706 | 0.000000926 | 0.000000000 | 0.190476190 | 0.000000000 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_paymonth_start_near3_money_r_top5_f0p25_59022654.csv | undo_e247like_ctrl_z_paymonth_start_near3_money_r_top5_f0p25 | undo | 0.250000000 | human_boundary_control | 5 | below_selector_resolution | below_selector_resolution | 0.000000114 | 0.000000947 | 0.000000000 | 0.095238095 | 0.000000000 | False |
| submission_e285_e247resid_add_e247like_z_jepa_prednorm_subject_social_comm_top3_f0p25_a6b1e2d3.csv | add_e247like_z_jepa_prednorm_subject_social_comm_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | below_selector_resolution | below_selector_resolution | 0.000000642 | 0.000001111 | 0.000000000 | 0.190476190 | 0.000000000 | False |
| submission_e285_e247resid_add_e247like_z_diary_state_k8_5_top3_f0p25_6a5b80da.csv | add_e247like_z_diary_state_k8_5_top3_f0p25 | add | 0.250000000 | human_boundary_add | 3 | below_selector_resolution | below_selector_resolution | 0.000000615 | 0.000001216 | 0.000000000 | 0.095238095 | 0.000000000 | False |
| submission_e285_e247resid_undo_low_smooth_top3_f0p25_5ce11742.csv | undo_low_smooth_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | below_selector_resolution | below_selector_resolution | 0.000000672 | 0.000001373 | 0.000000000 | 0.904761905 | 0.714285714 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_jepa_prednorm_subject_social_top3_f0p25_37621a4b.csv | undo_e247like_ctrl_z_jepa_prednorm_subject_social_top3_f0p25 | undo | 0.250000000 | human_boundary_control | 3 | below_selector_resolution | below_selector_resolution | 0.000001023 | 0.000001389 | 0.000000000 | 0.714285714 | 0.571428571 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_paymonth_start_near3_money_r_top5_f0p5_b7797908.csv | undo_e247like_ctrl_z_paymonth_start_near3_money_r_top5_f0p5 | undo | 0.500000000 | human_boundary_control | 5 | too_small_to_submit | too_small_to_submit | -0.000000858 | 0.000001960 | 0.000000000 | 0.190476190 | 0.000000000 | False |
| submission_e285_e247resid_undo_high_e284_oldlaw_top3_f0p25_16fd395c.csv | undo_high_e284_oldlaw_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | below_selector_resolution | below_selector_resolution | 0.000001029 | 0.000002079 | 0.000000000 | 0.714285714 | 0.571428571 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_diary_state_pc6_top3_f0p25_bc3ffc88.csv | undo_e247like_ctrl_z_diary_state_pc6_top3_f0p25 | undo | 0.250000000 | human_boundary_control | 3 | below_selector_resolution | below_selector_resolution | 0.000001596 | 0.000002271 | 0.000000000 | 0.238095238 | 0.142857143 | False |
| submission_e285_e247resid_add_e247like_z_jepa_prednorm_subject_social_comm_top5_f0p25_50fee853.csv | add_e247like_z_jepa_prednorm_subject_social_comm_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | below_selector_resolution | below_selector_resolution | 0.000001340 | 0.000002367 | 0.000000000 | 0.095238095 | 0.000000000 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_jepa_prednorm_subject_social_top3_f0p5_f13dadd3.csv | undo_e247like_ctrl_z_jepa_prednorm_subject_social_top3_f0p5 | undo | 0.500000000 | human_boundary_control | 3 | below_selector_resolution | below_selector_resolution | 0.000000948 | 0.000002560 | 0.000000000 | 0.666666667 | 0.571428571 | False |
| submission_e285_e247resid_undo_low_smooth_top3_f0p5_781451e1.csv | undo_low_smooth_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | below_selector_resolution | below_selector_resolution | 0.000001357 | 0.000002756 | 0.000000000 | 0.857142857 | 0.714285714 | False |
| submission_e285_e247resid_undo_e256like_z_paymonth_start_post3_late_shoppi_top3_f0p25_149092e6.csv | undo_e256like_z_paymonth_start_post3_late_shoppi_top3_f0p25 | undo | 0.250000000 | human_boundary_undo | 3 | below_selector_resolution | below_selector_resolution | 0.000000828 | 0.000002765 | 0.000000000 | 0.809523810 | 0.714285714 | False |
| submission_e285_e247resid_undo_low_smooth_top8_f0p25_d02262b4.csv | undo_low_smooth_top8_f0p25 | undo | 0.250000000 | e247_undo_rank | 8 | below_selector_resolution | below_selector_resolution | 0.000001382 | 0.000002960 | 0.000000000 | 0.476190476 | 0.142857143 | False |
| submission_e285_e247resid_undo_e256like_z_pay15_post3_late_shopping_subj_z_top5_f0p25_6f63d7b7.csv | undo_e256like_z_pay15_post3_late_shopping_subj_z_top5_f0p25 | undo | 0.250000000 | human_boundary_undo | 5 | too_small_to_submit | too_small_to_submit | -0.000000462 | 0.000002960 | 0.000000000 | 0.761904762 | 0.714285714 | False |
| submission_e285_e247resid_undo_e256like_z_pay15_post3_late_shopping_subj_z_top3_f0p25_6314f6be.csv | undo_e256like_z_pay15_post3_late_shopping_subj_z_top3_f0p25 | undo | 0.250000000 | human_boundary_undo | 3 | too_small_to_submit | too_small_to_submit | -0.000000578 | 0.000003046 | 0.000000000 | 0.857142857 | 0.714285714 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_diary_state_k8_5_top3_f0p25_897600e9.csv | undo_e247like_ctrl_z_diary_state_k8_5_top3_f0p25 | undo | 0.250000000 | human_boundary_control | 3 | below_selector_resolution | below_selector_resolution | 0.000002149 | 0.000003185 | 0.000000000 | 0.714285714 | 0.285714286 | False |
| submission_e285_e247resid_add_e247like_z_diary_state_k8_5_top5_f0p25_551f4548.csv | add_e247like_z_diary_state_k8_5_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | below_selector_resolution | below_selector_resolution | 0.000002022 | 0.000003577 | 0.000000000 | 0.000000000 | 0.000000000 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_pay15_post3_late_shopping_su_top3_f0p25_2ec67f92.csv | undo_e247like_ctrl_z_pay15_post3_late_shopping_su_top3_f0p25 | undo | 0.250000000 | human_boundary_control | 3 | below_selector_resolution | below_selector_resolution | 0.000002392 | 0.000003611 | 0.000000000 | 0.714285714 | 0.428571429 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_jepa_resid_dateblock_cogniti_top5_f0p25_d8f69c53.csv | undo_e247like_ctrl_z_jepa_resid_dateblock_cogniti_top5_f0p25 | undo | 0.250000000 | human_boundary_control | 5 | below_selector_resolution | below_selector_resolution | 0.000001083 | 0.000003660 | 0.000000000 | 0.476190476 | 0.285714286 | False |
| submission_e285_e247resid_undo_high_state_top3_f0p25_eb1d06a4.csv | undo_high_state_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | below_selector_resolution | below_selector_resolution | 0.000002068 | 0.000003677 | 0.000000000 | 0.476190476 | 0.000000000 | False |
| submission_e285_e247resid_add_e247like_z_pay15_post3_late_shopping_subj_z_top5_f0p25_a5b78a74.csv | add_e247like_z_pay15_post3_late_shopping_subj_z_top5_f0p25 | add | 0.250000000 | human_boundary_add | 5 | below_selector_resolution | below_selector_resolution | 0.000002395 | 0.000003963 | 0.000000000 | 0.095238095 | 0.000000000 | False |
| submission_e285_e247resid_undo_high_e284_oldlaw_top3_f0p5_d782dddc.csv | undo_high_e284_oldlaw_top3_f0p5 | undo | 0.500000000 | e247_undo_rank | 3 | below_selector_resolution | below_selector_resolution | 0.000002088 | 0.000004179 | 0.000000000 | 0.809523810 | 0.571428571 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_diary_state_pc6_top3_f0p5_c226db92.csv | undo_e247like_ctrl_z_diary_state_pc6_top3_f0p5 | undo | 0.500000000 | human_boundary_control | 3 | below_selector_resolution | below_selector_resolution | 0.000001564 | 0.000004224 | 0.000000000 | 0.619047619 | 0.285714286 | False |
| submission_e285_e247resid_undo_e256like_z_paymonth_start_post3_late_shoppi_top5_f0p25_bfe1796c.csv | undo_e256like_z_paymonth_start_post3_late_shoppi_top5_f0p25 | undo | 0.250000000 | human_boundary_undo | 5 | below_selector_resolution | below_selector_resolution | 0.000002820 | 0.000004432 | 0.000000000 | 0.904761905 | 0.857142857 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_paymonth_start_post3_late_sh_top5_f0p25_7fc96419.csv | undo_e247like_ctrl_z_paymonth_start_post3_late_sh_top5_f0p25 | undo | 0.250000000 | human_boundary_control | 5 | below_selector_resolution | below_selector_resolution | 0.000003012 | 0.000004610 | 0.000000000 | 0.380952381 | 0.285714286 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_jepa_prednorm_subject_social_top5_f0p25_875a43c2.csv | undo_e247like_ctrl_z_jepa_prednorm_subject_social_top5_f0p25 | undo | 0.250000000 | human_boundary_control | 5 | below_selector_resolution | below_selector_resolution | 0.000002975 | 0.000004690 | 0.000000000 | 0.809523810 | 0.714285714 | False |
| submission_e285_e247resid_undo_e247like_ctrl_z_jepa_resid_dateblock_cogniti_top3_f0p25_59e353e0.csv | undo_e247like_ctrl_z_jepa_resid_dateblock_cogniti_top3_f0p25 | undo | 0.250000000 | human_boundary_control | 3 | below_selector_resolution | below_selector_resolution | 0.000003496 | 0.000004736 | 0.000000000 | 0.285714286 | 0.000000000 | False |
| submission_e285_e247resid_undo_low_state_top3_f0p25_8968209c.csv | undo_low_state_top3_f0p25 | undo | 0.250000000 | e247_undo_rank | 3 | below_selector_resolution | below_selector_resolution | 0.000003856 | 0.000004822 | 0.000000000 | 0.190476190 | 0.000000000 | False |

## Preserve / Undo Read

- best undo actual p90: `-0.000000902`
- undo old strict-promote count: `0`
- undo matched-placebo pass count: `0`
- best add actual p90: `-0.000003481`
- add old strict-promote count: `0`
- add matched-placebo pass count: `0`

## Decision

No E247-relative human-state residual candidate is submission-ready. This supports preserving the current E247 Q3 smoothing body until a stronger E247-specific target is learned.

## Interpretation

The experiment deliberately avoided public LB. If undo candidates fail, that means current local sensors do not find a safe subset of E247 cells to remove. If add candidates fail, it means E247's public-positive body should not be extended with social/story-like cells by handcrafted rules.

## Files

- `e285_e247_residual_human_state_boundary_summary.csv`
- `e285_e247_residual_human_state_cell_summary.csv`
- `e285_e247_residual_human_state_candidate_summary.csv`
- `e285_e247_residual_human_state_governor_summary.csv`
- `e285_e247_residual_human_state_scores.csv`
