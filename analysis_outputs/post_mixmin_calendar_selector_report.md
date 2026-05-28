# E50 Post-Mixmin Calendar Selector

## Observe

E49 showed that train/test is an interleaved subject-calendar mask and that mixmin is not a simple prevalence correction.

## Wonder

Can calendar-run movement fingerprints explain `mixmin` as the new public-best anchor without breaking raw05, stage2, ordinal, and bad-JEPA anchor order?

## Hypothesis

H48 predicts that labeled calendar flanks around hidden test runs contain selector information. If true, a calendar view should recover mixmin as best and keep known-anchor ordering under leave-one-anchor-out.

## Method

- Features are probability/logit/entropy movement relative to a2c8, aggregated by target, subject, calendar context, train-span zone, run-length bin, and flank signature.
- Prior stress features reuse train/global, subject, and recent7 proxy LogLoss deltas.
- Public LB is used only for known-anchor LOOCV; no submission is generated.
- Mixmin-a2c8 public edge scale: `0.001132680`.

## Result

- strict selector views: `0`.
- loose selector views: `0`.

## View Summary

| view              | n_features | loocv_mae   | mixmin_abs_error | pairwise_rank_accuracy | spearman | mixmin_predicted_best | a2c8_raw05_order_correct | stage2_ordinal_order_correct | bad_tail_correct | edge_scale_gate | null_rank_p_ge_actual | strict_selector_gate | loose_selector_gate |
| ----------------- | ---------- | ----------- | ---------------- | ---------------------- | -------- | --------------------- | ------------------------ | ---------------------------- | ---------------- | --------------- | --------------------- | -------------------- | ------------------- |
| subject_calendar  | 966        | 0.000884106 | 0.00135162       | 0.833333               | 0.833333 | False                 | True                     | True                         | True             | True            | 0                     | False                | False               |
| target_prior      | 92         | 0.000945706 | 0.0013362        | 0.75                   | 0.616667 | False                 | True                     | True                         | False            | True            | 0.01                  | False                | False               |
| calendar          | 506        | 0.000972197 | 0.00134567       | 0.75                   | 0.733333 | False                 | True                     | True                         | False            | True            | 0.01                  | False                | False               |
| subject           | 552        | 0.0010092   | 0.00134643       | 0.694444               | 0.533333 | False                 | True                     | True                         | False            | True            | 0.0233333             | False                | False               |
| calendar_no_prior | 460        | 0.00101297  | 0.00137761       | 0.722222               | 0.716667 | False                 | False                    | True                         | False            | True            | 0.0166667             | False                | False               |

## Best View

| view             | n_features | loocv_mae   | loocv_max_abs_error | mixmin_abs_error | pairwise_rank_accuracy | spearman | mixmin_predicted_best | a2c8_raw05_order_correct | stage2_ordinal_order_correct | bad_tail_correct | edge_scale_gate | mixmin_error_below_edge | null_rank_p_ge_actual | strict_selector_gate | loose_selector_gate |
| ---------------- | ---------- | ----------- | ------------------- | ---------------- | ---------------------- | -------- | --------------------- | ------------------------ | ---------------------------- | ---------------- | --------------- | ----------------------- | --------------------- | -------------------- | ------------------- |
| subject_calendar | 966        | 0.000884106 | 0.00250241          | 0.00135162       | 0.833333               | 0.833333 | False                 | True                     | True                         | True             | True            | False                   | 0                     | False                | False               |

## Known Anchor LOOCV

| view              | name              | public_delta_vs_mixmin | predicted_delta | abs_error   | role                       | neighbor_indices |
| ----------------- | ----------------- | ---------------------- | --------------- | ----------- | -------------------------- | ---------------- |
| calendar          | mixmin            | 0                      | 0.00134567      | 0.00134567  | active_frontier            | 2,1,0            |
| calendar          | a2c8              | 0.00113268             | 0.00100391      | 0.00012877  | previous_frontier          | 1,0,2            |
| calendar          | raw05             | 0.00121967             | 0.00106024      | 0.000159425 | raw05_positive_anchor      | 1,2,0            |
| calendar          | stage2            | 0.00163834             | 0.000782572     | 0.000855763 | stage2_local_cv_anchor     | 2,0,1            |
| calendar          | ordinal           | 0.00199672             | 0.00159742      | 0.000399309 | ordinal_constraint_anchor  | 0,3,5            |
| calendar          | final9            | 0.00212071             | 0.00299766      | 0.000876947 | subject_logit_anchor       | 4,6,5            |
| calendar          | q2_jepa_bad       | 0.00349465             | 0.00209488      | 0.00139977  | bad_q2_jepa_anchor         | 3,0,7            |
| calendar          | lejepa_bad        | 0.00394018             | 0.00286618      | 0.00107399  | bad_lejepa_anchor          | 7,3,4            |
| calendar          | jepa_residual_bad | 0.00492069             | 0.00241056      | 0.00251013  | bad_all_target_jepa_anchor | 6,3,4            |
| calendar_no_prior | mixmin            | 0                      | 0.00137761      | 0.00137761  | active_frontier            | 2,1,0            |
| calendar_no_prior | a2c8              | 0.00113268             | 0.0011863       | 5.3622e-05  | previous_frontier          | 1,2,0            |
| calendar_no_prior | raw05             | 0.00121967             | 0.00110564      | 0.000114025 | raw05_positive_anchor      | 1,2,0            |
| calendar_no_prior | stage2            | 0.00163834             | 0.00068501      | 0.000953325 | stage2_local_cv_anchor     | 0,2,1            |
| calendar_no_prior | ordinal           | 0.00199672             | 0.00158558      | 0.000411144 | ordinal_constraint_anchor  | 0,3,5            |
| calendar_no_prior | final9            | 0.00212071             | 0.00333799      | 0.00121728  | subject_logit_anchor       | 4,7,6            |
| calendar_no_prior | q2_jepa_bad       | 0.00349465             | 0.00209197      | 0.00140268  | bad_q2_jepa_anchor         | 0,3,7            |
| calendar_no_prior | lejepa_bad        | 0.00394018             | 0.00286722      | 0.00107296  | bad_lejepa_anchor          | 7,3,4            |
| calendar_no_prior | jepa_residual_bad | 0.00492069             | 0.00240663      | 0.00251405  | bad_all_target_jepa_anchor | 6,3,4            |
| subject           | mixmin            | 0                      | 0.00134643      | 0.00134643  | active_frontier            | 2,1,0            |
| subject           | a2c8              | 0.00113268             | 0.00102789      | 0.000104793 | previous_frontier          | 1,0,2            |
| subject           | raw05             | 0.00121967             | 0.00107208      | 0.000147591 | raw05_positive_anchor      | 1,2,0            |
| subject           | stage2            | 0.00163834             | 0.000801429     | 0.000836906 | stage2_local_cv_anchor     | 2,0,1            |
| subject           | ordinal           | 0.00199672             | 0.00157723      | 0.000419491 | ordinal_constraint_anchor  | 0,3,5            |
| subject           | final9            | 0.00212071             | 0.00195216      | 0.000168555 | subject_logit_anchor       | 4,0,6            |
| subject           | q2_jepa_bad       | 0.00349465             | 0.000987209     | 0.00250744  | bad_q2_jepa_anchor         | 3,0,2            |
| subject           | lejepa_bad        | 0.00394018             | 0.00288624      | 0.00105393  | bad_lejepa_anchor          | 3,5,7            |
| subject           | jepa_residual_bad | 0.00492069             | 0.00242298      | 0.00249771  | bad_all_target_jepa_anchor | 6,3,4            |
| subject_calendar  | mixmin            | 0                      | 0.00135162      | 0.00135162  | active_frontier            | 2,1,0            |
| subject_calendar  | a2c8              | 0.00113268             | 0.00106518      | 6.75025e-05 | previous_frontier          | 1,0,2            |
| subject_calendar  | raw05             | 0.00121967             | 0.00106642      | 0.000153246 | raw05_positive_anchor      | 1,2,0            |
| subject_calendar  | stage2            | 0.00163834             | 0.000762495     | 0.00087584  | stage2_local_cv_anchor     | 2,0,1            |
| subject_calendar  | ordinal           | 0.00199672             | 0.00158255      | 0.000414174 | ordinal_constraint_anchor  | 0,3,5            |
| subject_calendar  | final9            | 0.00212071             | 0.00196695      | 0.00015376  | subject_logit_anchor       | 4,0,6            |
| subject_calendar  | q2_jepa_bad       | 0.00349465             | 0.00209773      | 0.00139691  | bad_q2_jepa_anchor         | 3,0,7            |
| subject_calendar  | lejepa_bad        | 0.00394018             | 0.00289868      | 0.00104149  | bad_lejepa_anchor          | 7,3,5            |
| subject_calendar  | jepa_residual_bad | 0.00492069             | 0.00241828      | 0.00250241  | bad_all_target_jepa_anchor | 6,3,4            |
| target_prior      | mixmin            | 0                      | 0.0013362       | 0.0013362   | active_frontier            | 2,1,0            |
| target_prior      | a2c8              | 0.00113268             | 0.00089033      | 0.000242351 | previous_frontier          | 0,1,2            |
| target_prior      | raw05             | 0.00121967             | 0.00123838      | 1.87177e-05 | raw05_positive_anchor      | 2,1,0            |
| target_prior      | stage2            | 0.00163834             | 0.00150724      | 0.000131099 | stage2_local_cv_anchor     | 2,5,0            |
| target_prior      | ordinal           | 0.00199672             | 0.00163056      | 0.00036616  | ordinal_constraint_anchor  | 3,0,5            |
| target_prior      | final9            | 0.00212071             | 0.00252119      | 0.000400476 | subject_logit_anchor       | 4,6,3            |
| target_prior      | q2_jepa_bad       | 0.00349465             | 0.00106147      | 0.00243318  | bad_q2_jepa_anchor         | 3,2,0            |
| target_prior      | lejepa_bad        | 0.00394018             | 0.00287048      | 0.0010697   | bad_lejepa_anchor          | 4,7,3            |
| target_prior      | jepa_residual_bad | 0.00492069             | 0.00240722      | 0.00251347  | bad_all_target_jepa_anchor | 6,3,4            |

## Candidate Sensor Predictions

These are not submission forecasts unless a view passes the gate.

| name                  | file                                                                                        | role                          | calendar | calendar_no_prior | subject  | subject_calendar | target_prior |
| --------------------- | ------------------------------------------------------------------------------------------- | ----------------------------- | -------- | ----------------- | -------- | ---------------- | ------------ |
| mixmin                | analysis_outputs/submission_mixmin_0c916bb4.csv                                             | active_frontier               | 0.576307 | 0.576307          | 0.576307 | 0.576307         | 0.576307     |
| blend_m0p50_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv             | raw-structure bridge          | 0.577255 | 0.577404          | 0.577276 | 0.577317         | 0.577296     |
| a2c8                  | analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv                             | previous_frontier             | 0.577439 | 0.577439          | 0.577439 | 0.577439         | 0.577439     |
| inv7_s0p25            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv                    | raw-structure bridge          | 0.577548 | 0.577448          | 0.577541 | 0.57752          | 0.57766      |
| raw05                 | jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv                                | raw05_positive_anchor         | 0.577526 | 0.577526          | 0.577526 | 0.577526         | 0.577526     |
| inv7_s0p50            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p50.csv                    | raw-structure bridge          | 0.577555 | 0.577468          | 0.577549 | 0.577527         | 0.577664     |
| blend_m0p25_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv             | raw-structure bridge          | 0.577566 | 0.577487          | 0.57756  | 0.577537         | 0.577346     |
| inv7_s1p00            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p00.csv                    | raw-structure bridge          | 0.577577 | 0.577505          | 0.577572 | 0.57755          | 0.577673     |
| inverse7blend_1040    | analysis_outputs/submission_inverse7blend_1040423d.csv                                      | raw-structure bridge          | 0.577577 | 0.577505          | 0.577572 | 0.57755          | 0.577673     |
| pair_sensor_1bb_s0p65 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | S4/Q3 selector disambiguation | 0.577624 | 0.57752           | 0.577623 | 0.577616         | 0.578401     |
| pair_sensor_1bb       | analysis_outputs/submission_label_flow_focused_1bbfb735.csv                                 | S4/Q3 selector disambiguation | 0.577626 | 0.577561          | 0.577625 | 0.57762          | 0.578402     |
| pair_sensor_6b        | analysis_outputs/submission_label_flow_focused_6b9335b1.csv                                 | S4/Q3 selector disambiguation | 0.577627 | 0.577581          | 0.577626 | 0.577623         | 0.578402     |
| stage2                | analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv              | stage2_local_cv_anchor        | 0.577945 | 0.577945          | 0.577945 | 0.577945         | 0.577945     |
| ordinal               | analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv            | ordinal_constraint_anchor     | 0.578303 | 0.578303          | 0.578303 | 0.578303         | 0.578303     |
| final9                | analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv              | subject_logit_anchor          | 0.578427 | 0.578427          | 0.578427 | 0.578427         | 0.578427     |
| q2_jepa_bad           | jepa/submission_jepa_latent_q2_w0p45.csv                                                    | bad_q2_jepa_anchor            | 0.579801 | 0.579801          | 0.579801 | 0.579801         | 0.579801     |
| lejepa_bad            | jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv                                  | bad_lejepa_anchor             | 0.580247 | 0.580247          | 0.580247 | 0.580247         | 0.580247     |
| jepa_residual_bad     | jepa/submission_jepa_latent_residual_probe.csv                                              | bad_all_target_jepa_anchor    | 0.581227 | 0.581227          | 0.581227 | 0.581227         | 0.581227     |

## Decision

Calendar-mask movement is an important observation, but the tested selector does not yet explain mixmin strongly enough to rank new submissions.

## Outputs

- `analysis_outputs/post_mixmin_calendar_selector_views.csv`
- `analysis_outputs/post_mixmin_calendar_selector_loocv.csv`
- `analysis_outputs/post_mixmin_calendar_selector_candidates.csv`
- `analysis_outputs/post_mixmin_calendar_selector_anchor_features.csv`
