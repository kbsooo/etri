# E274 Target-Specific Diary Energy Audit

## Question

After E273 rejected broad diary-state modeling, can target-specific diary energy axes create a public-free-promotable candidate?

## Local Axis Scan

- scanned axis-target rows: `581`
- action-gate axes: `44`
- diagnostic-gate axes: `6`
- selected axes for materialization: `24`

### Top Axes

| target | feature | action_gate | diagnostic_gate | local_axis_score | abs_label_lift | dateblock_delta | subject_delta | boundary_signal | train_test_mean_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | jepa_prednorm_dateblock_mobility_context | True | False | 0.029439497 | 0.256637168 | -0.013697360 | -0.035301799 | 0.927376658 | 0.071493822 |
| Q3 | jepa_prednorm_subject_mobility_context | True | False | 0.029055316 | 0.327433628 | -0.012267053 | -0.036501166 | 0.937272413 | 0.132502555 |
| Q3 | jepa_prednorm_subject_routine_calendar | True | False | 0.027476442 | 0.185840708 | -0.018569811 | -0.019935336 | 0.318927560 | 0.165380166 |
| Q3 | jepa_resid_subject_bedtime_phone | True | False | 0.026605531 | 0.203539823 | -0.018941832 | -0.014521025 | 0.612946779 | 0.044669959 |
| Q3 | mobility_context_energy | True | False | 0.026042339 | 0.256637168 | -0.013127964 | -0.027952733 | 0.671365775 | 0.071212835 |
| Q2 | media_game_pc2 | True | False | 0.022828890 | 0.194690265 | -0.015133742 | -0.016873665 | 0.000000000 | 0.105025145 |
| Q3 | diary_state_energy | True | False | 0.022800618 | 0.185840708 | -0.012069679 | -0.025094629 | 0.605910262 | 0.344332149 |
| Q3 | jepa_prednorm_subject_cognitive_money | True | False | 0.022787828 | 0.176991150 | -0.015051731 | -0.015188610 | 0.698291832 | 0.032080020 |
| S4 | jepa_prednorm_subject_physiology_activity | True | False | 0.019438862 | 0.141592920 | -0.015549956 | -0.009655225 | 0.003664385 | 0.606677195 |
| S4 | physiology_activity_energy | True | False | 0.018568755 | 0.159292035 | -0.015909649 | -0.005692457 | 0.020933926 | 0.631406059 |
| S4 | jepa_prednorm_dateblock_physiology_activity | True | False | 0.017410157 | 0.141592920 | -0.013951399 | -0.008231510 | 0.152318022 | 0.660344922 |
| S1 | jepa_resid_dateblock_cognitive_money | True | False | 0.015520574 | 0.221238938 | -0.009047279 | -0.009000092 | 1.199199993 | 0.058884132 |
| Q3 | social_comm_energy | True | False | 0.015223527 | 0.132743363 | -0.006555757 | -0.020886868 | 0.344603533 | 0.209781144 |
| S1 | jepa_resid_subject_cognitive_money | True | False | 0.014352492 | 0.203539823 | -0.007763140 | -0.010825533 | 0.778953838 | 0.009290709 |
| Q3 | diary_state_pc1 | True | False | 0.013915673 | 0.176991150 | -0.007072569 | -0.015429184 | 0.189893569 | 0.344610309 |
| S4 | mobility_context_pc2 | True | False | 0.012819398 | 0.150442478 | -0.011853794 | 0.001254839 | 0.000000000 | 0.066418330 |
| Q2 | diary_state_pc10 | True | False | 0.010879351 | 0.185840708 | -0.004355192 | -0.011372249 | 0.789844035 | 0.069586208 |
| S3 | physiology_activity_pc4 | True | False | 0.010441450 | 0.185840708 | -0.007826261 | -0.002488273 | 0.000000000 | 0.076075969 |
| S3 | diary_state_pc10 | True | False | 0.010312848 | 0.176991150 | -0.002589215 | -0.015052161 | 0.789844035 | 0.069586208 |
| S1 | cognitive_money_energy | True | False | 0.009211379 | 0.168141593 | -0.005505624 | -0.003717308 | 0.820255285 | 0.064649712 |
| Q1 | jepa_prednorm_subject_mobility_context | True | False | 0.009081410 | 0.203539823 | -0.002045565 | -0.012176938 | 0.937272413 | 0.132502555 |
| Q3 | jepa_prednorm_subject_bedtime_phone | True | False | 0.008231664 | 0.203539823 | -0.004547592 | -0.006256942 | 0.042607663 | 0.389242600 |
| Q3 | jepa_resid_subject_mobility_context | True | False | 0.007551659 | 0.159292035 | -0.006177993 | 0.002437835 | 0.644266922 | 0.006852263 |
| S2 | mobility_context_pc2 | True | False | 0.007319039 | 0.115044248 | -0.004451708 | -0.005190044 | 0.000000000 | 0.066418330 |

## Public-Free Promotion Audit

- selected E272-style selector models: `1`
- strict promote count: `0`
- best local candidate: `submission_e274_q_sleep_subjective_top12_8e391007.csv` -> `too_small_to_submit`
- best mean/p90 delta vs E247: `-0.000098347` / `-0.000048780`

### Candidate Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e274_q_sleep_subjective_top12_8e391007.csv | too_small_to_submit | -0.000098347 | -0.000177534 | -0.000048780 | 0.970588235 | -0.002504864 |
| submission_e274_q3_boundary_energy_top8_e5e4b0f4.csv | too_small_to_submit | -0.000050650 | -0.000066153 | -0.000026449 | 1.000000000 | -0.004736223 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | below_selector_resolution | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e274_action_only_top12_soft_efd9e3a7.csv | below_selector_resolution | 0.000015602 | -0.000014688 | 0.000039877 | 0.205882353 | 0.001162376 |
| submission_e274_s_objective_energy_top12_0e83fa92.csv | below_selector_resolution | 0.000006602 | -0.000043828 | 0.000053228 | 0.411764706 | -0.000070009 |
| submission_e274_energy_top18_balanced_238aa96b.csv | below_selector_resolution | 0.000048165 | 0.000000264 | 0.000083199 | 0.117647059 | 0.001363740 |

### Movement Anatomy

| basename | changed_cells_vs_current | changed_rows_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current |
| --- | --- | --- | --- | --- |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0 | 0 | 0.000000000 | 0.000000000 |
| submission_e274_action_only_top12_soft_efd9e3a7.csv | 129 | 110 | 2.902212437 | 0.008679674 |
| submission_e274_s_objective_energy_top12_0e83fa92.csv | 149 | 104 | 3.582138267 | 0.011164325 |
| submission_e274_q3_boundary_energy_top8_e5e4b0f4.csv | 140 | 140 | 5.009349198 | 0.014989903 |
| submission_e274_q_sleep_subjective_top12_8e391007.csv | 185 | 143 | 6.219838803 | 0.013741727 |
| submission_e274_energy_top18_balanced_238aa96b.csv | 241 | 174 | 7.193244290 | 0.012493321 |

## Decision

No E274 candidate clears the strict public-free promotion gate. The target-specific diary energy is locally informative but not yet submission-grade.

Interpretation: a broad human diary latent failed in E273; E274 asks whether the surviving axes can be translated into target-specific probability movement. If the score table says `too_small_to_submit`, the axis is a real story but below public-free resolution. If it says `block_or_reject`, the axis likely repeats a known bad movement geometry.

## Files

- `e274_target_specific_diary_energy_scan.csv`
- `e274_target_specific_diary_energy_selected_axes.csv`
- `e274_target_specific_diary_energy_candidate_scores.csv`
- `e274_target_specific_diary_energy_candidate_anatomy.csv`
- `e274_target_specific_diary_energy_selected_cells.csv`
