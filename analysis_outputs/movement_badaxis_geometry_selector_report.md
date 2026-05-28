# E41 Movement + Bad-Axis Geometry Selector

## Observe

E40 recovered the stage2/ordinal public order, but it missed A2C8-best and underpredicted bad JEPA anchor severity.

## Wonder

Does adding logit-space direction geometry against raw/good/bad anchor movements make movement anatomy a stricter public selector?

## Hypothesis

H40: if the missing E40 component is bad-axis geometry rather than general movement scale, then a LOO-safe movement+axis selector should reduce bad-anchor underprediction while preserving stage2/ordinal order and A2C8-best.

## Method

- Base is A2C8. Features are computed from candidate logit/probability/entropy movement relative to A2C8.
- Axis features use cosine and projection against known raw/medium/bad public anchor directions.
- During leave-one-anchor-out, the left-out anchor's own axis is removed before features are recomputed.
- Strict gate additionally requires mean bad-anchor underprediction <= 0.0010.

## Result

- strict selector views: `0`.
- loose selector views: `0`.

## View Summary

| view               | n_features | loocv_mae   | loocv_max_abs_error | pairwise_rank_accuracy | spearman | stage2_ordinal_order_correct | a2c8_predicted_best | raw05_near_best | bad_anchor_mean_underprediction | bad_anchor_max_underprediction | bad_anchor_predicted_delta_mean | null_rank_p_ge_actual | null_mae_p_le_actual | strict_selector_gate | loose_selector_gate |
| ------------------ | ---------- | ----------- | ------------------- | ---------------------- | -------- | ---------------------------- | ------------------- | --------------- | ------------------------------- | ------------------------------ | ------------------------------- | --------------------- | -------------------- | -------------------- | ------------------- |
| axis_named         | 50         | 0.000827696 | 0.00260381          | 0.571429               | 0.238095 | False                        | False               | True            | 0.00141257                      | 0.00260381                     | 0.00170389                      | 0.188                 | 0.02                 | False                | False               |
| axis_group         | 22         | 0.000854918 | 0.00147551          | 0.785714               | 0.738095 | True                         | False               | True            | 0.000898399                     | 0.00143025                     | 0.00224544                      | 0.014                 | 0.024                | False                | False               |
| compact_axis_named | 147        | 0.000935417 | 0.00246852          | 0.642857               | 0.52381  | True                         | False               | True            | 0.00129224                      | 0.00246852                     | 0.00169358                      | 0.094                 | 0.048                | False                | False               |
| compact_axis_group | 119        | 0.00097268  | 0.00249292          | 0.535714               | 0.428571 | True                         | False               | True            | 0.00125306                      | 0.00249292                     | 0.00173277                      | 0.214                 | 0.052                | False                | False               |
| compact            | 97         | 0.0010031   | 0.00252338          | 0.535714               | 0.428571 | True                         | False               | True            | 0.00128549                      | 0.00252338                     | 0.00170033                      | 0.222                 | 0.064                | False                | False               |

## Known Anchor LOOCV

| view               | name              | public_delta_vs_best | predicted_delta | abs_error   | underprediction | role                       |
| ------------------ | ----------------- | -------------------- | --------------- | ----------- | --------------- | -------------------------- |
| axis_group         | a2c8_best         | 0                    | 0.00147551      | 0.00147551  | 0               | current_best               |
| axis_group         | raw_timeline      | 8.69862e-05          | 0.000405847     | 0.000318861 | 0               | raw05_like_positive_anchor |
| axis_group         | stage2            | 0.000505655          | 0.00111311      | 0.000607459 | 0               | strong_local_stage2        |
| axis_group         | ordinal           | 0.000864044          | 0.00120692      | 0.000342873 | 0               | ordinal_constraint         |
| axis_group         | final9            | 0.000988032          | 0.00191342      | 0.000925385 | 0               | subject_logit_final9       |
| axis_group         | q2_jepa_bad       | 0.00236197           | 0.00283602      | 0.000474059 | 0               | bad_q2_jepa_anchor         |
| axis_group         | lejepa_bad        | 0.0028075            | 0.00154255      | 0.00126494  | 0.00126494      | bad_lejepa_anchor          |
| axis_group         | jepa_residual_bad | 0.00378801           | 0.00235775      | 0.00143025  | 0.00143025      | bad_all_target_jepa_anchor |
| axis_named         | a2c8_best         | 0                    | 0.000981451     | 0.000981451 | 0               | current_best               |
| axis_named         | raw_timeline      | 8.69862e-05          | 0.000456974     | 0.000369988 | 0               | raw05_like_positive_anchor |
| axis_named         | stage2            | 0.000505655          | 0.000589133     | 8.34779e-05 | 0               | strong_local_stage2        |
| axis_named         | ordinal           | 0.000864044          | 0.000430376     | 0.000433669 | 0.000433669     | ordinal_constraint         |
| axis_named         | final9            | 0.000988032          | 0.00111142      | 0.000123386 | 0               | subject_logit_final9       |
| axis_named         | q2_jepa_bad       | 0.00236197           | 0.00275386      | 0.000391894 | 0               | bad_q2_jepa_anchor         |
| axis_named         | lejepa_bad        | 0.0028075            | 0.000203687     | 0.00260381  | 0.00260381      | bad_lejepa_anchor          |
| axis_named         | jepa_residual_bad | 0.00378801           | 0.00215412      | 0.00163389  | 0.00163389      | bad_all_target_jepa_anchor |
| compact            | a2c8_best         | 0                    | 0.000880279     | 0.000880279 | 0               | current_best               |
| compact            | raw_timeline      | 8.69862e-05          | 0.000619106     | 0.00053212  | 0               | raw05_like_positive_anchor |
| compact            | stage2            | 0.000505655          | 0.000436946     | 6.87085e-05 | 6.87085e-05     | strong_local_stage2        |
| compact            | ordinal           | 0.000864044          | 0.00241207      | 0.00154803  | 0               | ordinal_constraint         |
| compact            | final9            | 0.000988032          | 0.00212724      | 0.00113921  | 0               | subject_logit_final9       |
| compact            | q2_jepa_bad       | 0.00236197           | 0.0019521       | 0.000409866 | 0.000409866     | bad_q2_jepa_anchor         |
| compact            | lejepa_bad        | 0.0028075            | 0.00188428      | 0.00092322  | 0.00092322      | bad_lejepa_anchor          |
| compact            | jepa_residual_bad | 0.00378801           | 0.00126462      | 0.00252338  | 0.00252338      | bad_all_target_jepa_anchor |
| compact_axis_group | a2c8_best         | 0                    | 0.000875975     | 0.000875975 | 0               | current_best               |
| compact_axis_group | raw_timeline      | 8.69862e-05          | 0.000625446     | 0.00053846  | 0               | raw05_like_positive_anchor |
| compact_axis_group | stage2            | 0.000505655          | 0.000472078     | 3.35766e-05 | 3.35766e-05     | strong_local_stage2        |
| compact_axis_group | ordinal           | 0.000864044          | 0.00232319      | 0.00145914  | 0               | ordinal_constraint         |
| compact_axis_group | final9            | 0.000988032          | 0.00210315      | 0.00111512  | 0               | subject_logit_final9       |
| compact_axis_group | q2_jepa_bad       | 0.00236197           | 0.00201845      | 0.000343514 | 0.000343514     | bad_q2_jepa_anchor         |
| compact_axis_group | lejepa_bad        | 0.0028075            | 0.00188476      | 0.000922735 | 0.000922735     | bad_lejepa_anchor          |
| compact_axis_group | jepa_residual_bad | 0.00378801           | 0.00129509      | 0.00249292  | 0.00249292      | bad_all_target_jepa_anchor |
| compact_axis_named | a2c8_best         | 0                    | 0.000855901     | 0.000855901 | 0               | current_best               |
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
| raw_timeline          | jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv                                | raw05_like_positive_anchor    | 0.577526   | 0.577526   | 0.577526 | 0.577526           | 0.577526           |
| pair_sensor_1bb_s0p65 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | S4/Q3 selector disambiguation | 0.577476   | 0.577472   | 0.577631 | 0.577619           | 0.577611           |
| pair_sensor_1bb       | analysis_outputs/submission_label_flow_focused_1bbfb735.csv                                 | S4/Q3 selector disambiguation | 0.577483   | 0.577477   | 0.577632 | 0.577621           | 0.577613           |
| blend_m0p50_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv             | raw-structure bridge          | 0.57757    | 0.577623   | 0.577611 | 0.577603           | 0.577614           |
| pair_sensor_6b        | analysis_outputs/submission_label_flow_focused_6b9335b1.csv                                 | S4/Q3 selector disambiguation | 0.577488   | 0.577481   | 0.577634 | 0.577623           | 0.577615           |
| blend_m0p25_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv             | raw-structure bridge          | 0.577581   | 0.577651   | 0.57759  | 0.577591           | 0.577624           |
| mixmin_0c916          | analysis_outputs/submission_mixmin_0c916bb4.csv                                             | anchor-loss worldview         | 0.577564   | 0.577631   | 0.577758 | 0.577666           | 0.577624           |
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

## Decision

Adding bad-axis geometry does not create a certified selector. The E40 failure is not solved by simple direction geometry.

## Outputs

- `analysis_outputs/movement_badaxis_geometry_selector_views.csv`
- `analysis_outputs/movement_badaxis_geometry_selector_loocv.csv`
- `analysis_outputs/movement_badaxis_geometry_selector_candidates.csv`