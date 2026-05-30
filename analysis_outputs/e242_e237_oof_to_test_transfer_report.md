# E242 E237 OOF-to-Test Transfer Audit

## Question

Does E237's OOF learned cell policy transfer to test-side materialization geometry, or is the selected file mostly determined by public-free graft/actual stress?

## Key Numbers

- Graft-side materialization rows audited: `120`.
- E237 gate pass rows: `7` (`0.058333`).
- OOF gain vs E237 score Spearman: `0.108953`.
- OOF gain gate AUC: `0.426043`.
- OOF tail-AUC gate AUC: `0.958913`.
- Top E237 file rank by OOF gain: `71/120`.
- Top E237 file rank by E237 score: `2/120`.

## Rank Audit

| rank_by | best_is_gate | best_value | first_selected_rank | top_e237_rank | top_e237_value |
| --- | --- | --- | --- | --- | --- |
| e237_score | False | 0.088602771 | 2 | 2 | 0.058941606 |
| oof_gain_vs_full | False | 0.000594241 | 17 | 71 | 0.000271441 |
| oof_gain_active | False | 0.004440366 | 17 | 71 | 0.004117566 |
| oof_tail_auc | True | 0.901873158 | 1 | 1 | 0.901873158 |
| oof_subject_win_rate | True | 0.800000000 | 1 | 14 | 0.700000000 |
| test_expected_gain_vs_e224 | True | 0.000009860 | 1 | 3 | 0.000005612 |
| adverse_reduction_vs_e224 | False | 0.001076431 | 6 | 6 | 0.000576400 |
| support_gain_vs_e224 | True | 0.006450259 | 1 | 1 | 0.006450259 |
| test_actual_gain_vs_e224 | True | 0.000009860 | 1 | 3 | 0.000005612 |
| actual_adverse_reduction_vs_e224 | False | 0.001041761 | 6 | 6 | 0.000553281 |
| q3_top1_over_abs_expected | True | 0.747139811 | 1 | 1 | 0.747139811 |

## Gate Summary

| group | n | oof_gain_vs_full_mean | oof_gain_vs_full_median | oof_gain_active_mean | oof_gain_active_median | oof_tail_auc_mean | oof_tail_auc_median | oof_subject_win_rate_mean | oof_subject_win_rate_median | test_expected_gain_vs_e224_mean | test_expected_gain_vs_e224_median | adverse_reduction_vs_e224_mean | adverse_reduction_vs_e224_median | support_gain_vs_e224_mean | support_gain_vs_e224_median | test_actual_gain_vs_e224_mean | test_actual_gain_vs_e224_median | actual_adverse_reduction_vs_e224_mean | actual_adverse_reduction_vs_e224_median | actual_support_gain_vs_e224_mean | actual_support_gain_vs_e224_median | q3_top1_over_abs_expected_mean | q3_top1_over_abs_expected_median | e230_q3_risk_top21_overlap_mean | e230_q3_risk_top21_overlap_median | e230_q3_swing_top25_overlap_mean | e230_q3_swing_top25_overlap_median | q3_dropped_cells_mean | q3_dropped_cells_median | s4_dropped_cells_mean | s4_dropped_cells_median | e237_score_mean | e237_score_median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_false | 113 | 0.000307832 | 0.000286624 | 0.004153956 | 0.004132749 | 0.610519088 | 0.589374494 | 0.695575221 | 0.700000000 | -0.000063066 | -0.000028252 | 0.000255415 | 0.000229778 | -0.002181456 | -0.001174833 | -0.000063066 | -0.000028252 | 0.000240326 | 0.000200734 | -0.001721649 | -0.000957086 | 1.318402983 | 1.001852644 | 1.398230088 | 1.000000000 | 2.203539823 | 1.000000000 | 18.433628319 | 13.000000000 | 17.035398230 | 13.000000000 | -0.001336529 | 0.003026040 |
| gate_true | 7 | 0.000281377 | 0.000271441 | 0.004127502 | 0.004117566 | 0.892739538 | 0.900643856 | 0.714285714 | 0.700000000 | 0.000003161 | 0.000005414 | 0.000318622 | 0.000264407 | 0.005278926 | 0.005859231 | 0.000003161 | 0.000005414 | 0.000314407 | 0.000262811 | 0.004415546 | 0.004893109 | 0.801466292 | 0.804528302 | 7.000000000 | 7.000000000 | 8.857142857 | 9.000000000 | 12.857142857 | 10.000000000 | 0.000000000 | 0.000000000 | 0.032727060 | 0.028117517 |

## OOF/Test Correlation Highlights

| oof_signal | test_signal | spearman |
| --- | --- | --- |
| e230_q3_expected_positive_overlap | adverse_reduction_vs_e224 | 0.842845334 |
| q3_dropped_cells | adverse_reduction_vs_e224 | 0.776699234 |
| e230_q3_swing_top25_overlap | adverse_reduction_vs_e224 | 0.479969945 |
| e230_q3_risk_top21_overlap | adverse_reduction_vs_e224 | 0.449307046 |
| q3_drop_purity | adverse_reduction_vs_e224 | 0.371927758 |
| oof_tail_auc | adverse_reduction_vs_e224 | 0.087180624 |
| oof_subject_win_rate | adverse_reduction_vs_e224 | 0.077663527 |
| oof_gain_vs_full | adverse_reduction_vs_e224 | 0.070336418 |
| oof_gain_active | adverse_reduction_vs_e224 | 0.070336418 |
| s4_dropped_cells | adverse_reduction_vs_e224 | 0.032283351 |
| oof_tail_auc | e237_score | 0.337261419 |
| e230_q3_risk_top21_overlap | e237_score | 0.191065224 |
| e230_q3_expected_positive_overlap | e237_score | 0.148859528 |
| oof_subject_win_rate | e237_score | 0.126180313 |
| oof_gain_vs_full | e237_score | 0.108953376 |
| oof_gain_active | e237_score | 0.108953376 |
| e230_q3_swing_top25_overlap | e237_score | 0.100440193 |
| s4_dropped_cells | e237_score | 0.100367320 |
| q3_dropped_cells | e237_score | -0.020880943 |
| q3_drop_purity | e237_score | -0.054195593 |
| e230_q3_risk_top21_overlap | gate_auc | 0.960176991 |
| oof_tail_auc | gate_auc | 0.958912769 |
| e230_q3_swing_top25_overlap | gate_auc | 0.937420986 |
| q3_drop_purity | gate_auc | 0.867256637 |
| e230_q3_expected_positive_overlap | gate_auc | 0.623893805 |
| oof_subject_win_rate | gate_auc | 0.582806574 |
| oof_gain_vs_full | gate_auc | 0.426042984 |
| oof_gain_active | gate_auc | 0.426042984 |
| q3_dropped_cells | gate_auc | 0.402654867 |
| s4_dropped_cells | gate_auc | 0.132743363 |
| oof_tail_auc | test_expected_gain_vs_e224 | 0.241185241 |
| oof_subject_win_rate | test_expected_gain_vs_e224 | 0.130025904 |
| oof_gain_vs_full | test_expected_gain_vs_e224 | 0.091924961 |
| oof_gain_active | test_expected_gain_vs_e224 | 0.091924961 |
| q3_drop_purity | test_expected_gain_vs_e224 | 0.032488285 |
| e230_q3_risk_top21_overlap | test_expected_gain_vs_e224 | -0.050676448 |
| e230_q3_swing_top25_overlap | test_expected_gain_vs_e224 | -0.115916087 |
| s4_dropped_cells | test_expected_gain_vs_e224 | -0.171749828 |
| e230_q3_expected_positive_overlap | test_expected_gain_vs_e224 | -0.197231460 |
| q3_dropped_cells | test_expected_gain_vs_e224 | -0.305633117 |

## Conflict Examples

| conflict_type | candidate_id | e237_gate | q3_dropped_cells | s4_dropped_cells | oof_gain_vs_full | oof_tail_auc | test_expected_gain_vs_e224 | support_gain_vs_e224 | e237_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oof_strong | q3s4_movement_hgb_shallow_row5_risk_q0p20_drop_q3_top25 | False | 25 | 0 | 0.000594241 | 0.866479925 | -0.000079291 | -0.002062972 | -0.054821822 |
| oof_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p10_drop_q3_p20 | False | 50 | 0 | 0.000562500 | 0.592561285 | -0.000002990 | -0.004872843 | 0.041224723 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p10_drop_q3_p20 | False | 50 | 0 | 0.000562500 | 0.591595218 | -0.000002990 | -0.004872843 | 0.041224723 |
| oof_strong | q3s4_movement_hgb_shallow_row5_risk_q0p20_drop_q3_top21 | False | 21 | 0 | 0.000527674 | 0.866479925 | -0.000076318 | -0.002835596 | -0.049625668 |
| oof_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_top40 | False | 22 | 18 | 0.000504853 | 0.592561285 | -0.000023407 | -0.002908644 | 0.016267429 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_top40 | False | 22 | 18 | 0.000504853 | 0.591595218 | -0.000023407 | -0.002908644 | 0.016267429 |
| oof_strong | q3s4_movement_hgb_shallow_row5_risk_q0p20_drop_q3_p05 | False | 12 | 0 | 0.000504768 | 0.866479925 | -0.000076799 | -0.005384776 | -0.063976288 |
| oof_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_top50 | False | 28 | 22 | 0.000485778 | 0.592561285 | -0.000007851 | -0.003049408 | 0.028481770 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_top50 | False | 28 | 22 | 0.000485778 | 0.591595218 | -0.000007851 | -0.003049408 | 0.028481770 |
| oof_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p10_drop_each_top25 | False | 25 | 25 | 0.000485778 | 0.592561285 | -0.000013180 | -0.003062996 | 0.028158301 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p10_drop_each_top25 | False | 25 | 25 | 0.000485778 | 0.591595218 | -0.000013180 | -0.003062996 | 0.028158301 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p20_drop_q3_top25 | False | 25 | 0 | 0.000425601 | 0.528801739 | -0.000043322 | -0.001172407 | -0.000796073 |
| oof_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_p20 | False | 48 | 52 | 0.000415475 | 0.592561285 | -0.000041306 | -0.007161781 | 0.039261564 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_p20 | False | 48 | 52 | 0.000415475 | 0.591595218 | -0.000041306 | -0.007161781 | 0.039261564 |
| oof_strong | all3_movement_hgb_shallow_row5_contrast_q0p10_drop_s4_p20 | False | 0 | 50 | 0.000401681 | 0.588507342 | -0.000068741 | -0.003541542 | 0.011033534 |
| oof_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p20_drop_q3_top40 | False | 40 | 0 | 0.000400994 | 0.527216738 | -0.000054436 | -0.000892183 | 0.003794061 |
| oof_strong | all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top13 | True | 13 | 0 | 0.000398977 | 0.900643856 | 0.000002012 | 0.006005051 | 0.032782975 |
| oof_strong | all3_movement_hgb_shallow_row5_contrast_q0p10_drop_global_p15 | False | 46 | 29 | 0.000393879 | 0.588507342 | -0.000125173 | -0.011434899 | -0.027459335 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p20_drop_q3_p05 | False | 12 | 0 | 0.000391717 | 0.528801739 | -0.000023954 | -0.002578066 | 0.000501375 |
| oof_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p20_drop_each_top21 | False | 21 | 21 | 0.000382824 | 0.528801739 | -0.000197452 | 0.000347030 | -0.003062918 |
| test_gate_strong | all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_each_top25 | False | 25 | 25 | 0.000350486 | 0.901873158 | -0.000138549 | 0.004457075 | 0.088602771 |
| test_gate_strong | all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25 | True | 25 | 0 | 0.000271441 | 0.901873158 | 0.000005612 | 0.006450259 | 0.058941606 |
| test_gate_strong | all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top21 | False | 21 | 0 | 0.000260686 | 0.901873158 | -0.000013872 | 0.004145347 | 0.047562741 |
| test_gate_strong | all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p10_drop_each_top13 | False | 13 | 13 | 0.000294104 | 0.900643856 | -0.000084583 | 0.002643105 | 0.047411715 |
| test_gate_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p10_drop_q3_p20 | False | 50 | 0 | 0.000562500 | 0.592561285 | -0.000002990 | -0.004872843 | 0.041224723 |
| test_gate_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p10_drop_q3_p20 | False | 50 | 0 | 0.000562500 | 0.591595218 | -0.000002990 | -0.004872843 | 0.041224723 |
| test_gate_strong | all3_latent_with_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_p20 | False | 48 | 52 | 0.000415475 | 0.592561285 | -0.000041306 | -0.007161781 | 0.039261564 |
| test_gate_strong | all3_latent_no_targetid_hgb_shallow_subject5_contrast_q0p10_drop_global_p20 | False | 48 | 52 | 0.000415475 | 0.591595218 | -0.000041306 | -0.007161781 | 0.039261564 |
| test_gate_strong | all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_global_p05 | False | 15 | 10 | 0.000289247 | 0.901873158 | -0.000104610 | 0.000981066 | 0.035118820 |
| test_gate_strong | all3_latent_with_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top13 | True | 13 | 0 | 0.000398977 | 0.900643856 | 0.000002012 | 0.006005051 | 0.032782975 |

## E237 vs E240/E241

| item | source | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_adverse_reduction_vs_e224 | overlap_e237 | overlap_e230_swing25 | oof_or_train_delta | oof_or_train_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E237 top learned selector | all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25 | -0.000005612 | 0.000576400 | 0.006450259 | 0.000553281 | 25.000000000 | 13.000000000 | -0.000271441 | E237 OOF loss_vs_full |
| E240 best simple selector | simple_pc10_top25 | -0.000062119 | 0.000594489 | 0.016747154 | 0.000573879 | 14.000000000 | 18.000000000 | 0.001867628 | E241 score_pc10 train top10 drop_delta |

## Decision

- Average OOF loss gain is not a reliable selector, but OOF tail-AUC is strongly aligned with the E237 gate. The transferable object is high-impact Q3 risk-tail discrimination, not mean OOF policy improvement.
- No submission is created. Do not choose E237 siblings by OOF rank alone; use the pre-registered E237 top file only if the next public question is the learned Q3 decisive-cell world.
