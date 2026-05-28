# E40 Test-Movement Fingerprint Selector

## Observe

E39 showed that OOF stability matches known-public signs but reverses stage2/ordinal rank. The next non-OOF local target is the label-free test movement fingerprint itself.

## Wonder

Can target, subject, row-order, and raw-domain movement anatomy recover known public LB deltas under leave-one-anchor-out strongly enough to rank new sensors?

## Hypothesis

H39: if the hidden public subset is encoded in test movement/raw-domain structure, then a kNN selector over label-free movement fingerprints should recover known anchor order, especially stage2 < ordinal, and pass a permutation-null stress.

## Method

- Fingerprints are computed from submission probability/logit/entropy movement relative to A2C8.
- Views: target-only, subject, row-order, raw-domain, and combined.
- Raw-domain masks use train/test domain score, train-nearest-neighbor density, missingness, and raw-feature clusters.
- Train/test domain AUC from raw features: `1.000000`.
- Public LB is used only for known-anchor leave-one-out evaluation, not for direct candidate tuning.

## Result

- strict selector views: `0`.
- loose selector views: `4`.

## View Summary

| view       | n_features | loocv_mae   | pairwise_rank_accuracy | spearman | stage2_ordinal_order_correct | a2c8_predicted_best | null_rank_p_ge_actual | strict_selector_gate | loose_selector_gate |
| ---------- | ---------- | ----------- | ---------------------- | -------- | ---------------------------- | ------------------- | --------------------- | -------------------- | ------------------- |
| combined   | 1292       | 0.000781461 | 0.821429               | 0.809524 | True                         | False               | 0.004                 | False                | True                |
| order      | 380        | 0.000802019 | 0.821429               | 0.809524 | True                         | False               | 0.004                 | False                | True                |
| target     | 38         | 0.00081491  | 0.785714               | 0.785714 | True                         | False               | 0.01                  | False                | True                |
| raw_domain | 570        | 0.00082387  | 0.821429               | 0.809524 | True                         | False               | 0.008                 | False                | True                |
| subject    | 418        | 0.00086646  | 0.821429               | 0.809524 | True                         | False               | 0.002                 | False                | False               |

## Best View

| view     | n_features | loocv_mae   | loocv_max_abs_error | pairwise_rank_accuracy | spearman | stage2_ordinal_order_correct | a2c8_predicted_best | raw05_near_best | null_rank_p_ge_actual | null_mae_p_le_actual | strict_selector_gate | loose_selector_gate |
| -------- | ---------- | ----------- | ------------------- | ---------------------- | -------- | ---------------------------- | ------------------- | --------------- | --------------------- | -------------------- | -------------------- | ------------------- |
| combined | 1292       | 0.000781461 | 0.0025148           | 0.821429               | 0.809524 | True                         | False               | True            | 0.004                 | 0                    | False                | True                |

## Known Anchor LOOCV

| view       | name              | public_delta_vs_best | predicted_delta | abs_error   | role                       |
| ---------- | ----------------- | -------------------- | --------------- | ----------- | -------------------------- |
| combined   | a2c8_best         | 0                    | 0.000146436     | 0.000146436 | current_best               |
| combined   | raw_timeline      | 8.69862e-05          | 7.85748e-05     | 8.41141e-06 | raw05_like_positive_anchor |
| combined   | stage2            | 0.000505655          | 0.000437528     | 6.81269e-05 | strong_local_stage2        |
| combined   | ordinal           | 0.000864044          | 0.000996444     | 0.0001324   | ordinal_constraint         |
| combined   | final9            | 0.000988032          | 0.00120447      | 0.000216441 | subject_logit_final9       |
| combined   | q2_jepa_bad       | 0.00236197           | 0.000222627     | 0.00213934  | bad_q2_jepa_anchor         |
| combined   | lejepa_bad        | 0.0028075            | 0.00178176      | 0.00102573  | bad_lejepa_anchor          |
| combined   | jepa_residual_bad | 0.00378801           | 0.0012732       | 0.0025148   | bad_all_target_jepa_anchor |
| order      | a2c8_best         | 0                    | 0.000149336     | 0.000149336 | current_best               |
| order      | raw_timeline      | 8.69862e-05          | 8.40018e-05     | 2.98442e-06 | raw05_like_positive_anchor |
| order      | stage2            | 0.000505655          | 0.000403853     | 0.000101802 | strong_local_stage2        |
| order      | ordinal           | 0.000864044          | 0.00101214      | 0.000148096 | ordinal_constraint         |
| order      | final9            | 0.000988032          | 0.00119531      | 0.000207273 | subject_logit_final9       |
| order      | q2_jepa_bad       | 0.00236197           | 0.000220351     | 0.00214161  | bad_q2_jepa_anchor         |
| order      | lejepa_bad        | 0.0028075            | 0.0016511       | 0.00115639  | bad_lejepa_anchor          |
| order      | jepa_residual_bad | 0.00378801           | 0.00127935      | 0.00250866  | bad_all_target_jepa_anchor |
| raw_domain | a2c8_best         | 0                    | 0.000146443     | 0.000146443 | current_best               |
| raw_domain | raw_timeline      | 8.69862e-05          | 7.91532e-05     | 7.83305e-06 | raw05_like_positive_anchor |
| raw_domain | stage2            | 0.000505655          | 0.000401933     | 0.000103722 | strong_local_stage2        |
| raw_domain | ordinal           | 0.000864044          | 0.00100353      | 0.000139486 | ordinal_constraint         |
| raw_domain | final9            | 0.000988032          | 0.00121384      | 0.000225812 | subject_logit_final9       |
| raw_domain | q2_jepa_bad       | 0.00236197           | 0.000221777     | 0.00214019  | bad_q2_jepa_anchor         |
| raw_domain | lejepa_bad        | 0.0028075            | 0.00150342      | 0.00130408  | bad_lejepa_anchor          |
| raw_domain | jepa_residual_bad | 0.00378801           | 0.00126461      | 0.0025234   | bad_all_target_jepa_anchor |
| subject    | a2c8_best         | 0                    | 0.000143505     | 0.000143505 | current_best               |
| subject    | raw_timeline      | 8.69862e-05          | 7.3109e-05      | 1.38772e-05 | raw05_like_positive_anchor |
| subject    | stage2            | 0.000505655          | 0.000501194     | 4.46076e-06 | strong_local_stage2        |
| subject    | ordinal           | 0.000864044          | 0.00125292      | 0.000388881 | ordinal_constraint         |
| subject    | final9            | 0.000988032          | 0.00119639      | 0.000208358 | subject_logit_final9       |
| subject    | q2_jepa_bad       | 0.00236197           | 0.000224853     | 0.00213711  | bad_q2_jepa_anchor         |
| subject    | lejepa_bad        | 0.0028075            | 0.00127469      | 0.00153281  | bad_lejepa_anchor          |
| subject    | jepa_residual_bad | 0.00378801           | 0.00128532      | 0.00250268  | bad_all_target_jepa_anchor |
| target     | a2c8_best         | 0                    | 0.000143311     | 0.000143311 | current_best               |
| target     | raw_timeline      | 8.69862e-05          | 7.62661e-05     | 1.07201e-05 | raw05_like_positive_anchor |
| target     | stage2            | 0.000505655          | 0.000334744     | 0.000170911 | strong_local_stage2        |
| target     | ordinal           | 0.000864044          | 0.00122665      | 0.000362601 | ordinal_constraint         |
| target     | final9            | 0.000988032          | 0.00121068      | 0.000222644 | subject_logit_final9       |
| target     | q2_jepa_bad       | 0.00236197           | 0.00021716      | 0.00214481  | bad_q2_jepa_anchor         |
| target     | lejepa_bad        | 0.0028075            | 0.00188397      | 0.000923532 | bad_lejepa_anchor          |
| target     | jepa_residual_bad | 0.00378801           | 0.00124725      | 0.00254076  | bad_all_target_jepa_anchor |

## Candidate Sensor Predictions

| name                  | file                                                                                        | role                          | combined | order    | raw_domain | subject  | target   |
| --------------------- | ------------------------------------------------------------------------------------------- | ----------------------------- | -------- | -------- | ---------- | -------- | -------- |
| a2c8_best             | analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv                             | current_best                  | 0.577439 | 0.577439 | 0.577439   | 0.577439 | 0.577439 |
| inv7_s0p25            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv                    | raw-structure bridge          | 0.57745  | 0.57745  | 0.577449   | 0.577452 | 0.57745  |
| inv7_s0p50            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p50.csv                    | raw-structure bridge          | 0.577473 | 0.577472 | 0.577471   | 0.577476 | 0.577474 |
| blend_m0p25_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv             | raw-structure bridge          | 0.577494 | 0.577494 | 0.577493   | 0.577496 | 0.577496 |
| inv7_s1p00            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p00.csv                    | raw-structure bridge          | 0.57751  | 0.577512 | 0.577508   | 0.577512 | 0.577515 |
| inverse7blend_1040    | analysis_outputs/submission_inverse7blend_1040423d.csv                                      | raw-structure bridge          | 0.57751  | 0.577512 | 0.577508   | 0.577512 | 0.577515 |
| blend_m0p50_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv             | raw-structure bridge          | 0.577516 | 0.577518 | 0.577515   | 0.577516 | 0.57752  |
| pair_sensor_1bb_s0p65 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | S4/Q3 selector disambiguation | 0.577522 | 0.577514 | 0.577521   | 0.577526 | 0.577503 |
| raw_timeline          | jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv                                | raw05_like_positive_anchor    | 0.577526 | 0.577526 | 0.577526   | 0.577526 | 0.577526 |
| pair_sensor_1bb       | analysis_outputs/submission_label_flow_focused_1bbfb735.csv                                 | S4/Q3 selector disambiguation | 0.57756  | 0.57755  | 0.577558   | 0.577567 | 0.577533 |
| pair_sensor_6b        | analysis_outputs/submission_label_flow_focused_6b9335b1.csv                                 | S4/Q3 selector disambiguation | 0.577578 | 0.577567 | 0.577574   | 0.577586 | 0.577548 |
| mixmin_0c916          | analysis_outputs/submission_mixmin_0c916bb4.csv                                             | anchor-loss worldview         | 0.577664 | 0.57769  | 0.577657   | 0.577659 | 0.577694 |
| stage2                | analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv              | strong_local_stage2           | 0.577945 | 0.577945 | 0.577945   | 0.577945 | 0.577945 |
| ordinal               | analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv            | ordinal_constraint            | 0.578303 | 0.578303 | 0.578303   | 0.578303 | 0.578303 |
| final9                | analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv              | subject_logit_final9          | 0.578427 | 0.578427 | 0.578427   | 0.578427 | 0.578427 |
| q2_jepa_bad           | jepa/submission_jepa_latent_q2_w0p45.csv                                                    | bad_q2_jepa_anchor            | 0.579801 | 0.579801 | 0.579801   | 0.579801 | 0.579801 |
| lejepa_bad            | jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv                                  | bad_lejepa_anchor             | 0.580247 | 0.580247 | 0.580247   | 0.580247 | 0.580247 |
| jepa_residual_bad     | jepa/submission_jepa_latent_residual_probe.csv                                              | bad_all_target_jepa_anchor    | 0.581227 | 0.581227 | 0.581227   | 0.581227 | 0.581227 |

## Decision

No movement-fingerprint view is a certified public selector. Treat this as another negative selector-calibration result, not as a candidate ranker.

## Outputs

- `analysis_outputs/test_movement_fingerprint_selector_views.csv`
- `analysis_outputs/test_movement_fingerprint_selector_loocv.csv`
- `analysis_outputs/test_movement_fingerprint_selector_candidates.csv`
