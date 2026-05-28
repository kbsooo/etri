# E42 Fixed-Zero Anchor Selector Calibration

## Observe

E41 fails the full LOO gate mainly because A2C8 is not recovered as the zero-loss current-best point when it is held out.

## Wonder

Is that failure just an overly harsh LOO design, or does keeping A2C8 fixed create a near-zero movement prior whose apparent candidate improvements are below selector resolution?

## Hypothesis

H41: if A2C8 should be treated as a known fixed zero anchor, then nonbaseline leave-one-out should recover public ordering and the selector should still have enough resolution to rank candidates beyond the raw05-A2C8 gap.

## Method

- A2C8 is kept in every training fold with delta 0.
- Each nonbaseline public anchor is held out in turn.
- Axis views still remove the held-out anchor's own axis before prediction.
- A frontier-resolution gate compares nonbaseline MAE against the raw05-A2C8 public gap.
- A zero-neighborhood collapse check counts unobserved candidates predicted better than raw05 by less than selector error.

## Result

- fixed-zero nonbaseline gates: `0`.
- usable zero-anchor gates after frontier-resolution/collapse stress: `0`.

## View Summary

| view               | n_features | nonbaseline_loocv_mae | nonbaseline_loocv_max_abs_error | pairwise_rank_accuracy | spearman | stage2_ordinal_order_correct | raw05_predicted_best_nonbaseline | raw05_abs_error | bad_anchor_mean_underprediction | bad_anchor_max_underprediction | raw05_gap_to_mae_ratio | null_rank_p_ge_actual | null_mae_p_le_actual | n_unobserved_candidates | n_unobserved_better_than_raw05 | best_unobserved_predicted_delta | best_unobserved_advantage_vs_raw05 | best_unobserved_advantage_to_mae_ratio | trajectory_monotonic_rate | bad_half_predicted_delta_mean | good_half_predicted_delta_mean | bad_half_above_good_half | fixed_zero_nonbaseline_gate | frontier_resolution_gate | zero_anchor_collapse_warning | usable_zero_anchor_gate |
| ------------------ | ---------- | --------------------- | ------------------------------- | ---------------------- | -------- | ---------------------------- | -------------------------------- | --------------- | ------------------------------- | ------------------------------ | ---------------------- | --------------------- | -------------------- | ----------------------- | ------------------------------ | ------------------------------- | ---------------------------------- | -------------------------------------- | ------------------------- | ----------------------------- | ------------------------------ | ------------------------ | --------------------------- | ------------------------ | ---------------------------- | ----------------------- |
| axis_group         | 22         | 0.000766262           | 0.00143025                      | 0.857143               | 0.821429 | True                         | True                             | 0.000318861     | 0.000898399                     | 0.00143025                     | 0.11352                | 0.006                 | 0.016                | 10                      | 3                              | 3.68669e-05                     | 5.01193e-05                        | 0.0654075                              | 0.428571                  | 0.00287343                    | 0.000432387                    | True                     | False                       | False                    | True                         | False                   |
| axis_named         | 50         | 0.000805731           | 0.00260381                      | 0.619048               | 0.285714 | False                        | False                            | 0.000369988     | 0.00141257                      | 0.00260381                     | 0.107959               | 0.152                 | 0.018                | 10                      | 3                              | 3.28843e-05                     | 5.41019e-05                        | 0.0671463                              | 0.428571                  | 0.00279256                    | 0.000555197                    | True                     | False                       | False                    | True                         | False                   |
| compact_axis_named | 147        | 0.000946776           | 0.00246852                      | 0.619048               | 0.392857 | True                         | False                            | 0.000531894     | 0.00129224                      | 0.00246852                     | 0.0918762              | 0.114                 | 0.062                | 10                      | 0                              | 0.000171633                     | -8.46464e-05                       | -0.0894049                             | 0.714286                  | 0.00167323                    | 0.000471727                    | True                     | False                       | False                    | False                        | False                   |
| compact_axis_group | 119        | 0.000986495           | 0.00249292                      | 0.47619                | 0.25     | True                         | False                            | 0.00053846      | 0.00125306                      | 0.00249292                     | 0.088177               | 0.334                 | 0.09                 | 10                      | 0                              | 0.000147014                     | -6.00275e-05                       | -0.0608493                             | 0.714286                  | 0.00158429                    | 0.000430121                    | True                     | False                       | False                    | False                        | False                   |
| compact            | 97         | 0.00102065            | 0.00252338                      | 0.47619                | 0.25     | True                         | False                            | 0.00053212      | 0.00128549                      | 0.00252338                     | 0.0852265              | 0.336                 | 0.11                 | 10                      | 0                              | 0.000143585                     | -5.65986e-05                       | -0.0554536                             | 0.571429                  | 0.00113093                    | 0.000547498                    | True                     | False                       | False                    | False                        | False                   |

## Best View

| view       | n_features | nonbaseline_loocv_mae | nonbaseline_loocv_max_abs_error | pairwise_rank_accuracy | spearman | stage2_ordinal_order_correct | raw05_predicted_best_nonbaseline | raw05_abs_error | bad_anchor_mean_underprediction | bad_anchor_max_underprediction | raw05_gap_to_mae_ratio | null_rank_p_ge_actual | null_mae_p_le_actual | n_unobserved_candidates | n_unobserved_better_than_raw05 | best_unobserved_predicted_delta | best_unobserved_advantage_vs_raw05 | best_unobserved_advantage_to_mae_ratio | trajectory_monotonic_rate | bad_half_predicted_delta_mean | good_half_predicted_delta_mean | bad_half_above_good_half | fixed_zero_nonbaseline_gate | frontier_resolution_gate | zero_anchor_collapse_warning | usable_zero_anchor_gate |
| ---------- | ---------- | --------------------- | ------------------------------- | ---------------------- | -------- | ---------------------------- | -------------------------------- | --------------- | ------------------------------- | ------------------------------ | ---------------------- | --------------------- | -------------------- | ----------------------- | ------------------------------ | ------------------------------- | ---------------------------------- | -------------------------------------- | ------------------------- | ----------------------------- | ------------------------------ | ------------------------ | --------------------------- | ------------------------ | ---------------------------- | ----------------------- |
| axis_group | 22         | 0.000766262           | 0.00143025                      | 0.857143               | 0.821429 | True                         | True                             | 0.000318861     | 0.000898399                     | 0.00143025                     | 0.11352                | 0.006                 | 0.016                | 10                      | 3                              | 3.68669e-05                     | 5.01193e-05                        | 0.0654075                              | 0.428571                  | 0.00287343                    | 0.000432387                    | True                     | False                       | False                    | True                         | False                   |

## Nonbaseline LOOCV

| view               | name              | public_delta_vs_best | predicted_delta | abs_error   | underprediction | role                       |
| ------------------ | ----------------- | -------------------- | --------------- | ----------- | --------------- | -------------------------- |
| axis_group         | raw_timeline      | 8.69862e-05          | 0.000405847     | 0.000318861 | 0               | raw05_like_positive_anchor |
| axis_group         | stage2            | 0.000505655          | 0.00111311      | 0.000607459 | 0               | strong_local_stage2        |
| axis_group         | ordinal           | 0.000864044          | 0.00120692      | 0.000342873 | 0               | ordinal_constraint         |
| axis_group         | final9            | 0.000988032          | 0.00191342      | 0.000925385 | 0               | subject_logit_final9       |
| axis_group         | q2_jepa_bad       | 0.00236197           | 0.00283602      | 0.000474059 | 0               | bad_q2_jepa_anchor         |
| axis_group         | lejepa_bad        | 0.0028075            | 0.00154255      | 0.00126494  | 0.00126494      | bad_lejepa_anchor          |
| axis_group         | jepa_residual_bad | 0.00378801           | 0.00235775      | 0.00143025  | 0.00143025      | bad_all_target_jepa_anchor |
| axis_named         | raw_timeline      | 8.69862e-05          | 0.000456974     | 0.000369988 | 0               | raw05_like_positive_anchor |
| axis_named         | stage2            | 0.000505655          | 0.000589133     | 8.34779e-05 | 0               | strong_local_stage2        |
| axis_named         | ordinal           | 0.000864044          | 0.000430376     | 0.000433669 | 0.000433669     | ordinal_constraint         |
| axis_named         | final9            | 0.000988032          | 0.00111142      | 0.000123386 | 0               | subject_logit_final9       |
| axis_named         | q2_jepa_bad       | 0.00236197           | 0.00275386      | 0.000391894 | 0               | bad_q2_jepa_anchor         |
| axis_named         | lejepa_bad        | 0.0028075            | 0.000203687     | 0.00260381  | 0.00260381      | bad_lejepa_anchor          |
| axis_named         | jepa_residual_bad | 0.00378801           | 0.00215412      | 0.00163389  | 0.00163389      | bad_all_target_jepa_anchor |
| compact            | raw_timeline      | 8.69862e-05          | 0.000619106     | 0.00053212  | 0               | raw05_like_positive_anchor |
| compact            | stage2            | 0.000505655          | 0.000436946     | 6.87085e-05 | 6.87085e-05     | strong_local_stage2        |
| compact            | ordinal           | 0.000864044          | 0.00241207      | 0.00154803  | 0               | ordinal_constraint         |
| compact            | final9            | 0.000988032          | 0.00212724      | 0.00113921  | 0               | subject_logit_final9       |
| compact            | q2_jepa_bad       | 0.00236197           | 0.0019521       | 0.000409866 | 0.000409866     | bad_q2_jepa_anchor         |
| compact            | lejepa_bad        | 0.0028075            | 0.00188428      | 0.00092322  | 0.00092322      | bad_lejepa_anchor          |
| compact            | jepa_residual_bad | 0.00378801           | 0.00126462      | 0.00252338  | 0.00252338      | bad_all_target_jepa_anchor |
| compact_axis_group | raw_timeline      | 8.69862e-05          | 0.000625446     | 0.00053846  | 0               | raw05_like_positive_anchor |
| compact_axis_group | stage2            | 0.000505655          | 0.000472078     | 3.35766e-05 | 3.35766e-05     | strong_local_stage2        |
| compact_axis_group | ordinal           | 0.000864044          | 0.00232319      | 0.00145914  | 0               | ordinal_constraint         |
| compact_axis_group | final9            | 0.000988032          | 0.00210315      | 0.00111512  | 0               | subject_logit_final9       |
| compact_axis_group | q2_jepa_bad       | 0.00236197           | 0.00201845      | 0.000343514 | 0.000343514     | bad_q2_jepa_anchor         |
| compact_axis_group | lejepa_bad        | 0.0028075            | 0.00188476      | 0.000922735 | 0.000922735     | bad_lejepa_anchor          |
| compact_axis_group | jepa_residual_bad | 0.00378801           | 0.00129509      | 0.00249292  | 0.00249292      | bad_all_target_jepa_anchor |
| compact_axis_named | raw_timeline      | 8.69862e-05          | 0.00061888      | 0.000531894 | 0               | raw05_like_positive_anchor |
| compact_axis_named | stage2            | 0.000505655          | 0.000511836     | 6.18097e-06 | 0               | strong_local_stage2        |
| compact_axis_named | ordinal           | 0.000864044          | 0.00225999      | 0.00139594  | 0               | ordinal_constraint         |
| compact_axis_named | final9            | 0.000988032          | 0.00180472      | 0.000816687 | 0               | subject_logit_final9       |
| compact_axis_named | q2_jepa_bad       | 0.00236197           | 0.00186869      | 0.000493271 | 0.000493271     | bad_q2_jepa_anchor         |
| compact_axis_named | lejepa_bad        | 0.0028075            | 0.00189256      | 0.000914937 | 0.000914937     | bad_lejepa_anchor          |
| compact_axis_named | jepa_residual_bad | 0.00378801           | 0.00131948      | 0.00246852  | 0.00246852      | bad_all_target_jepa_anchor |

## Candidate Sensor Predictions

| name                  | file                                                                                        | role                          | axis_group | axis_named | compact  | compact_axis_group | compact_axis_named |
| --------------------- | ------------------------------------------------------------------------------------------- | ----------------------------- | ---------- | ---------- | -------- | ------------------ | ------------------ |
| a2c8_best             | analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv                             | current_best                  | 0.577439   | 0.577439   | 0.577439 | 0.577439           | 0.577439           |
| pair_sensor_1bb_s0p65 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | S4/Q3 selector disambiguation | 0.577476   | 0.577472   | 0.577631 | 0.577619           | 0.577611           |
| pair_sensor_1bb       | analysis_outputs/submission_label_flow_focused_1bbfb735.csv                                 | S4/Q3 selector disambiguation | 0.577483   | 0.577477   | 0.577632 | 0.577621           | 0.577613           |
| pair_sensor_6b        | analysis_outputs/submission_label_flow_focused_6b9335b1.csv                                 | S4/Q3 selector disambiguation | 0.577488   | 0.577481   | 0.577634 | 0.577623           | 0.577615           |
| raw_timeline          | jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv                                | raw05_like_positive_anchor    | 0.577526   | 0.577526   | 0.577526 | 0.577526           | 0.577526           |
| mixmin_0c916          | analysis_outputs/submission_mixmin_0c916bb4.csv                                             | anchor-loss worldview         | 0.577564   | 0.577631   | 0.577758 | 0.577666           | 0.577624           |
| blend_m0p50_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv             | raw-structure bridge          | 0.57757    | 0.577623   | 0.577611 | 0.577603           | 0.577614           |
| blend_m0p25_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv             | raw-structure bridge          | 0.577581   | 0.577651   | 0.57759  | 0.577591           | 0.577624           |
| inv7_s0p25            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv                    | raw-structure bridge          | 0.577591   | 0.577611   | 0.577583 | 0.577586           | 0.577634           |
| inv7_s0p50            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p50.csv                    | raw-structure bridge          | 0.577593   | 0.577614   | 0.577589 | 0.577591           | 0.57764            |
| inv7_s1p00            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p00.csv                    | raw-structure bridge          | 0.577598   | 0.577619   | 0.577614 | 0.577608           | 0.577652           |
| inverse7blend_1040    | analysis_outputs/submission_inverse7blend_1040423d.csv                                      | raw-structure bridge          | 0.577598   | 0.577619   | 0.577614 | 0.577608           | 0.577652           |
| stage2                | analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv              | strong_local_stage2           | 0.577945   | 0.577945   | 0.577945 | 0.577945           | 0.577945           |
| ordinal               | analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv            | ordinal_constraint            | 0.578303   | 0.578303   | 0.578303 | 0.578303           | 0.578303           |
| final9                | analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv              | subject_logit_final9          | 0.578427   | 0.578427   | 0.578427 | 0.578427           | 0.578427           |
| q2_jepa_bad           | jepa/submission_jepa_latent_q2_w0p45.csv                                                    | bad_q2_jepa_anchor            | 0.579801   | 0.579801   | 0.579801 | 0.579801           | 0.579801           |
| lejepa_bad            | jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv                                  | bad_lejepa_anchor             | 0.580247   | 0.580247   | 0.580247 | 0.580247           | 0.580247           |
| jepa_residual_bad     | jepa/submission_jepa_latent_residual_probe.csv                                              | bad_all_target_jepa_anchor    | 0.581227   | 0.581227   | 0.581227 | 0.581227           | 0.581227           |

## Trajectory Sample

| view       | anchor            | scale | linear_delta_reference | predicted_delta | role                       |
| ---------- | ----------------- | ----- | ---------------------- | --------------- | -------------------------- |
| axis_group | final9            | 0.05  | 4.94016e-05            | 0.000125388     | subject_logit_final9       |
| axis_group | final9            | 0.1   | 9.88032e-05            | 0.000130573     | subject_logit_final9       |
| axis_group | final9            | 0.25  | 0.000247008            | 0.00027695      | subject_logit_final9       |
| axis_group | final9            | 0.5   | 0.000494016            | 0.000682697     | subject_logit_final9       |
| axis_group | final9            | 0.75  | 0.000741024            | 0.000890587     | subject_logit_final9       |
| axis_group | final9            | 1     | 0.000988032            | 0.000988032     | subject_logit_final9       |
| axis_group | jepa_residual_bad | 0.05  | 0.0001894              | 0.00291301      | bad_all_target_jepa_anchor |
| axis_group | jepa_residual_bad | 0.1   | 0.000378801            | 0.0029098       | bad_all_target_jepa_anchor |
| axis_group | jepa_residual_bad | 0.25  | 0.000947002            | 0.00289866      | bad_all_target_jepa_anchor |
| axis_group | jepa_residual_bad | 0.5   | 0.001894               | 0.00287785      | bad_all_target_jepa_anchor |
| axis_group | jepa_residual_bad | 0.75  | 0.00284101             | 0.00295842      | bad_all_target_jepa_anchor |
| axis_group | jepa_residual_bad | 1     | 0.00378801             | 0.00378801      | bad_all_target_jepa_anchor |
| axis_group | lejepa_bad        | 0.05  | 0.000140375            | 0.00180272      | bad_lejepa_anchor          |
| axis_group | lejepa_bad        | 0.1   | 0.00028075             | 0.00185817      | bad_lejepa_anchor          |
| axis_group | lejepa_bad        | 0.25  | 0.000701875            | 0.00290628      | bad_lejepa_anchor          |
| axis_group | lejepa_bad        | 0.5   | 0.00140375             | 0.00290664      | bad_lejepa_anchor          |
| axis_group | lejepa_bad        | 0.75  | 0.00210562             | 0.00292629      | bad_lejepa_anchor          |
| axis_group | lejepa_bad        | 1     | 0.0028075              | 0.0028075       | bad_lejepa_anchor          |
| axis_group | ordinal           | 0.05  | 4.32022e-05            | 0.000162885     | ordinal_constraint         |
| axis_group | ordinal           | 0.1   | 8.64044e-05            | 0.000226628     | ordinal_constraint         |
| axis_group | ordinal           | 0.25  | 0.000216011            | 0.000297479     | ordinal_constraint         |
| axis_group | ordinal           | 0.5   | 0.000432022            | 0.000491707     | ordinal_constraint         |
| axis_group | ordinal           | 0.75  | 0.000648033            | 0.000846637     | ordinal_constraint         |
| axis_group | ordinal           | 1     | 0.000864044            | 0.000864044     | ordinal_constraint         |
| axis_group | q2_jepa_bad       | 0.05  | 0.000118098            | 0.00179868      | bad_q2_jepa_anchor         |
| axis_group | q2_jepa_bad       | 0.1   | 0.000236197            | 0.00184727      | bad_q2_jepa_anchor         |
| axis_group | q2_jepa_bad       | 0.25  | 0.000590491            | 0.00288851      | bad_q2_jepa_anchor         |
| axis_group | q2_jepa_bad       | 0.5   | 0.00118098             | 0.00283581      | bad_q2_jepa_anchor         |
| axis_group | q2_jepa_bad       | 0.75  | 0.00177147             | 0.00268502      | bad_q2_jepa_anchor         |
| axis_group | q2_jepa_bad       | 1     | 0.00236197             | 0.00236197      | bad_q2_jepa_anchor         |
| axis_group | raw_timeline      | 0.05  | 4.34931e-06            | 9.20921e-05     | raw05_like_positive_anchor |
| axis_group | raw_timeline      | 0.1   | 8.69862e-06            | 9.16127e-05     | raw05_like_positive_anchor |
| axis_group | raw_timeline      | 0.25  | 2.17466e-05            | 9.029e-05       | raw05_like_positive_anchor |
| axis_group | raw_timeline      | 0.5   | 4.34931e-05            | 8.85207e-05     | raw05_like_positive_anchor |
| axis_group | raw_timeline      | 0.75  | 6.52397e-05            | 8.73858e-05     | raw05_like_positive_anchor |
| axis_group | raw_timeline      | 1     | 8.69862e-05            | 8.69862e-05     | raw05_like_positive_anchor |
| axis_group | stage2            | 0.05  | 2.52827e-05            | 0.000392096     | strong_local_stage2        |
| axis_group | stage2            | 0.1   | 5.05655e-05            | 0.000399693     | strong_local_stage2        |
| axis_group | stage2            | 0.25  | 0.000126414            | 0.000424479     | strong_local_stage2        |
| axis_group | stage2            | 0.5   | 0.000252827            | 0.000466622     | strong_local_stage2        |
| axis_group | stage2            | 0.75  | 0.000379241            | 0.000496507     | strong_local_stage2        |
| axis_group | stage2            | 1     | 0.000505655            | 0.000505655     | strong_local_stage2        |
| axis_named | final9            | 0.05  | 4.94016e-05            | 0.000259253     | subject_logit_final9       |
| axis_named | final9            | 0.1   | 9.88032e-05            | 0.000276245     | subject_logit_final9       |
| axis_named | final9            | 0.25  | 0.000247008            | 0.000610979     | subject_logit_final9       |
| axis_named | final9            | 0.5   | 0.000494016            | 0.000777231     | subject_logit_final9       |
| axis_named | final9            | 0.75  | 0.000741024            | 0.000944034     | subject_logit_final9       |
| axis_named | final9            | 1     | 0.000988032            | 0.000988032     | subject_logit_final9       |
| axis_named | jepa_residual_bad | 0.05  | 0.0001894              | 0.000962576     | bad_all_target_jepa_anchor |
| axis_named | jepa_residual_bad | 0.1   | 0.000378801            | 0.00199882      | bad_all_target_jepa_anchor |
| axis_named | jepa_residual_bad | 0.25  | 0.000947002            | 0.00225319      | bad_all_target_jepa_anchor |
| axis_named | jepa_residual_bad | 0.5   | 0.001894               | 0.00306463      | bad_all_target_jepa_anchor |
| axis_named | jepa_residual_bad | 0.75  | 0.00284101             | 0.00336141      | bad_all_target_jepa_anchor |
| axis_named | jepa_residual_bad | 1     | 0.00378801             | 0.00378801      | bad_all_target_jepa_anchor |
| axis_named | lejepa_bad        | 0.05  | 0.000140375            | 0.000997962     | bad_lejepa_anchor          |
| axis_named | lejepa_bad        | 0.1   | 0.00028075             | 0.0010697       | bad_lejepa_anchor          |
| axis_named | lejepa_bad        | 0.25  | 0.000701875            | 0.0013443       | bad_lejepa_anchor          |
| axis_named | lejepa_bad        | 0.5   | 0.00140375             | 0.0028918       | bad_lejepa_anchor          |
| axis_named | lejepa_bad        | 0.75  | 0.00210562             | 0.0028418       | bad_lejepa_anchor          |
| axis_named | lejepa_bad        | 1     | 0.0028075              | 0.0028075       | bad_lejepa_anchor          |
| axis_named | ordinal           | 0.05  | 4.32022e-05            | 0.000303916     | ordinal_constraint         |
| axis_named | ordinal           | 0.1   | 8.64044e-05            | 0.000324542     | ordinal_constraint         |
| axis_named | ordinal           | 0.25  | 0.000216011            | 0.0005424       | ordinal_constraint         |
| axis_named | ordinal           | 0.5   | 0.000432022            | 0.000822688     | ordinal_constraint         |
| axis_named | ordinal           | 0.75  | 0.000648033            | 0.000855287     | ordinal_constraint         |
| axis_named | ordinal           | 1     | 0.000864044            | 0.000864044     | ordinal_constraint         |
| axis_named | q2_jepa_bad       | 0.05  | 0.000118098            | 0.000985954     | bad_q2_jepa_anchor         |
| axis_named | q2_jepa_bad       | 0.1   | 0.000236197            | 0.00103119      | bad_q2_jepa_anchor         |
| axis_named | q2_jepa_bad       | 0.25  | 0.000590491            | 0.00224078      | bad_q2_jepa_anchor         |
| axis_named | q2_jepa_bad       | 0.5   | 0.00118098             | 0.00242126      | bad_q2_jepa_anchor         |
| axis_named | q2_jepa_bad       | 0.75  | 0.00177147             | 0.00248076      | bad_q2_jepa_anchor         |
| axis_named | q2_jepa_bad       | 1     | 0.00236197             | 0.00236197      | bad_q2_jepa_anchor         |
| axis_named | raw_timeline      | 0.05  | 4.34931e-06            | 9.13572e-05     | raw05_like_positive_anchor |
| axis_named | raw_timeline      | 0.1   | 8.69862e-06            | 9.09515e-05     | raw05_like_positive_anchor |
| axis_named | raw_timeline      | 0.25  | 2.17466e-05            | 8.98277e-05     | raw05_like_positive_anchor |
| axis_named | raw_timeline      | 0.5   | 4.34931e-05            | 8.83132e-05     | raw05_like_positive_anchor |
| axis_named | raw_timeline      | 0.75  | 6.52397e-05            | 8.73335e-05     | raw05_like_positive_anchor |
| axis_named | raw_timeline      | 1     | 8.69862e-05            | 8.69862e-05     | raw05_like_positive_anchor |
| axis_named | stage2            | 0.05  | 2.52827e-05            | 0.000288475     | strong_local_stage2        |
| axis_named | stage2            | 0.1   | 5.05655e-05            | 0.000299742     | strong_local_stage2        |

## Decision

Even with A2C8 fixed, the selector does not pass the nonbaseline calibration gate. Fixed-zero anchoring does not repair the bottleneck.

## Outputs

- `analysis_outputs/zero_anchor_selector_calibration_views.csv`
- `analysis_outputs/zero_anchor_selector_calibration_loocv.csv`
- `analysis_outputs/zero_anchor_selector_calibration_candidates.csv`
- `analysis_outputs/zero_anchor_selector_calibration_trajectories.csv`