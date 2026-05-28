# E51 Post-Mixmin Anchor-Calendar Selector

## Observe

E50 falsified calendar-only selection: calendar topology is real, but it did not predict held-out mixmin as best.

## Wonder

Does subject-calendar context become selector-useful when combined with the binary-world anchor-loss geometry that selected mixmin before the public LB observation?

## Hypothesis

If the post-mixmin worldview is right, LOO-safe anchor-loss world aggregates should rescue mixmin-best prediction, and calendar context should improve or at least not degrade that anchor-loss selector.

## Method

- Reuse the E30 binary frontier-box worlds and compute every anchor/candidate's per-world LogLoss delta versus a2c8.
- Score worlds by known-anchor energy in two LOO-safe modes: `shape` reproduces E32-style cancellation/sign/correlation energy, while `residual` also includes known-anchor residual fit.
- For each held-out public anchor, omit that anchor from world-energy scoring before predicting it.
- Concatenate low-energy world aggregate features with compact calendar fingerprints from E50.

## Result

- strict selector views: `0`.
- loose selector views: `0`.

## View Summary

| view                         | n_features | loocv_mae   | loocv_max_abs_error | mixmin_abs_error | pairwise_rank_accuracy | spearman | mixmin_predicted_best | a2c8_raw05_order_correct | stage2_ordinal_order_correct | bad_tail_correct | edge_scale_gate | mixmin_error_below_edge | null_rank_p_ge_actual | strict_selector_gate | loose_selector_gate |
| ---------------------------- | ---------- | ----------- | ------------------- | ---------------- | ---------------------- | -------- | --------------------- | ------------------------ | ---------------------------- | ---------------- | --------------- | ----------------------- | --------------------- | -------------------- | ------------------- |
| anchor_residual              | 132        | 0.000835516 | 0.00241739          | 0.00241739       | 0.75                   | 0.633333 | False                 | False                    | True                         | True             | True            | False                   |                       | False                | False               |
| anchor_shape                 | 132        | 0.000852957 | 0.0025358           | 0.0025358        | 0.75                   | 0.633333 | False                 | False                    | True                         | True             | True            | False                   |                       | False                | False               |
| contextall_anchor_residual   | 348        | 0.000889706 | 0.00241796          | 0.00241796       | 0.75                   | 0.683333 | False                 | False                    | True                         | False            | True            | False                   |                       | False                | False               |
| targetprior_anchor_shape     | 224        | 0.00091328  | 0.00253613          | 0.00253613       | 0.777778               | 0.683333 | False                 | False                    | True                         | True             | True            | False                   |                       | False                | False               |
| targetprior_anchor_residual  | 224        | 0.000922784 | 0.00241748          | 0.00241748       | 0.75                   | 0.683333 | False                 | False                    | True                         | True             | True            | False                   |                       | False                | False               |
| contextall_anchor_shape      | 348        | 0.00099711  | 0.00237642          | 0.00237642       | 0.694444               | 0.633333 | False                 | False                    | True                         | False            | True            | False                   |                       | False                | False               |
| movedtargets_anchor_shape    | 1092       | 0.00108743  | 0.00249949          | 0.002378         | 0.583333               | 0.333333 | False                 | False                    | False                        | False            | True            | False                   |                       | False                | False               |
| movedtargets_anchor_residual | 1092       | 0.00108915  | 0.00250018          | 0.0023791        | 0.583333               | 0.333333 | False                 | False                    | False                        | False            | True            | False                   |                       | False                | False               |

## Best View

| view            | n_features | loocv_mae   | loocv_max_abs_error | mixmin_abs_error | pairwise_rank_accuracy | spearman | mixmin_predicted_best | a2c8_raw05_order_correct | stage2_ordinal_order_correct | bad_tail_correct | edge_scale_gate | mixmin_error_below_edge | null_rank_p_ge_actual | strict_selector_gate | loose_selector_gate |
| --------------- | ---------- | ----------- | ------------------- | ---------------- | ---------------------- | -------- | --------------------- | ------------------------ | ---------------------------- | ---------------- | --------------- | ----------------------- | --------------------- | -------------------- | ------------------- |
| anchor_residual | 132        | 0.000835516 | 0.00241739          | 0.00241739       | 0.75                   | 0.633333 | False                 | False                    | True                         | True             | True            | False                   |                       | False                | False               |

## Known Anchor LOOCV

| view                         | name              | public_delta_vs_mixmin | predicted_delta | abs_error   | role                       | neighbor_indices |
| ---------------------------- | ----------------- | ---------------------- | --------------- | ----------- | -------------------------- | ---------------- |
| anchor_residual              | mixmin            | 0                      | 0.00241739      | 0.00241739  | active_frontier            | 4,5,2            |
| anchor_residual              | a2c8              | 0.00113268             | 0.0021407       | 0.00100802  | previous_frontier          | 5,2,1            |
| anchor_residual              | raw05             | 0.00121967             | 0.00157942      | 0.000359756 | raw05_positive_anchor      | 2,1,3            |
| anchor_residual              | stage2            | 0.00163834             | 0.00130099      | 0.000337347 | stage2_local_cv_anchor     | 2,1,3            |
| anchor_residual              | ordinal           | 0.00199672             | 0.00175898      | 0.000237741 | ordinal_constraint_anchor  | 4,3,2            |
| anchor_residual              | final9            | 0.00212071             | 0.00238643      | 0.000265713 | subject_logit_anchor       | 4,3,6            |
| anchor_residual              | q2_jepa_bad       | 0.00349465             | 0.00274763      | 0.000747019 | bad_q2_jepa_anchor         | 7,3,2            |
| anchor_residual              | lejepa_bad        | 0.00394018             | 0.00329732      | 0.000642863 | bad_lejepa_anchor          | 7,4,5            |
| anchor_residual              | jepa_residual_bad | 0.00492069             | 0.00341689      | 0.00150379  | bad_all_target_jepa_anchor | 7,6,5            |
| anchor_shape                 | mixmin            | 0                      | 0.0025358       | 0.0025358   | active_frontier            | 4,3,5            |
| anchor_shape                 | a2c8              | 0.00113268             | 0.00212964      | 0.00099696  | previous_frontier          | 2,5,1            |
| anchor_shape                 | raw05             | 0.00121967             | 0.00158222      | 0.00036255  | raw05_positive_anchor      | 2,1,3            |
| anchor_shape                 | stage2            | 0.00163834             | 0.00129822      | 0.000340111 | stage2_local_cv_anchor     | 2,1,3            |
| anchor_shape                 | ordinal           | 0.00199672             | 0.00170511      | 0.000291616 | ordinal_constraint_anchor  | 4,3,2            |
| anchor_shape                 | final9            | 0.00212071             | 0.00236547      | 0.000244753 | subject_logit_anchor       | 4,3,6            |
| anchor_shape                 | q2_jepa_bad       | 0.00349465             | 0.00276362      | 0.00073103  | bad_q2_jepa_anchor         | 7,3,2            |
| anchor_shape                 | lejepa_bad        | 0.00394018             | 0.00331527      | 0.000624907 | bad_lejepa_anchor          | 7,4,5            |
| anchor_shape                 | jepa_residual_bad | 0.00492069             | 0.00337181      | 0.00154888  | bad_all_target_jepa_anchor | 7,6,4            |
| contextall_anchor_residual   | mixmin            | 0                      | 0.00241796      | 0.00241796  | active_frontier            | 2,5,4            |
| contextall_anchor_residual   | a2c8              | 0.00113268             | 0.00202066      | 0.00088798  | previous_frontier          | 1,2,5            |
| contextall_anchor_residual   | raw05             | 0.00121967             | 0.00125457      | 3.49004e-05 | raw05_positive_anchor      | 2,1,0            |
| contextall_anchor_residual   | stage2            | 0.00163834             | 0.001637        | 1.33493e-06 | stage2_local_cv_anchor     | 2,1,5            |
| contextall_anchor_residual   | ordinal           | 0.00199672             | 0.00174429      | 0.000252438 | ordinal_constraint_anchor  | 3,5,0            |
| contextall_anchor_residual   | final9            | 0.00212071             | 0.00310669      | 0.00098598  | subject_logit_anchor       | 4,6,5            |
| contextall_anchor_residual   | q2_jepa_bad       | 0.00349465             | 0.00264902      | 0.000845627 | bad_q2_jepa_anchor         | 3,7,2            |
| contextall_anchor_residual   | lejepa_bad        | 0.00394018             | 0.00307189      | 0.00086829  | bad_lejepa_anchor          | 7,5,4            |
| contextall_anchor_residual   | jepa_residual_bad | 0.00492069             | 0.00320784      | 0.00171285  | bad_all_target_jepa_anchor | 6,7,4            |
| contextall_anchor_shape      | mixmin            | 0                      | 0.00237642      | 0.00237642  | active_frontier            | 3,5,2            |
| contextall_anchor_shape      | a2c8              | 0.00113268             | 0.00202075      | 0.000888068 | previous_frontier          | 1,2,5            |
| contextall_anchor_shape      | raw05             | 0.00121967             | 0.00125489      | 3.52227e-05 | raw05_positive_anchor      | 2,1,0            |
| contextall_anchor_shape      | stage2            | 0.00163834             | 0.00163316      | 5.17523e-06 | stage2_local_cv_anchor     | 2,1,5            |
| contextall_anchor_shape      | ordinal           | 0.00199672             | 0.00326212      | 0.0012654   | ordinal_constraint_anchor  | 3,5,7            |
| contextall_anchor_shape      | final9            | 0.00212071             | 0.00309785      | 0.000977139 | subject_logit_anchor       | 4,6,5            |
| contextall_anchor_shape      | q2_jepa_bad       | 0.00349465             | 0.00265785      | 0.000836798 | bad_q2_jepa_anchor         | 3,7,2            |
| contextall_anchor_shape      | lejepa_bad        | 0.00394018             | 0.00306805      | 0.000872133 | bad_lejepa_anchor          | 7,5,4            |
| contextall_anchor_shape      | jepa_residual_bad | 0.00492069             | 0.00320304      | 0.00171764  | bad_all_target_jepa_anchor | 6,7,4            |
| movedtargets_anchor_residual | mixmin            | 0                      | 0.0023791       | 0.0023791   | active_frontier            | 2,5,3            |
| movedtargets_anchor_residual | a2c8              | 0.00113268             | 0.00195061      | 0.000817932 | previous_frontier          | 1,2,5            |
| movedtargets_anchor_residual | raw05             | 0.00121967             | 0.00109681      | 0.000122855 | raw05_positive_anchor      | 1,2,0            |
| movedtargets_anchor_residual | stage2            | 0.00163834             | 0.00191025      | 0.000271911 | stage2_local_cv_anchor     | 5,2,0            |
| movedtargets_anchor_residual | ordinal           | 0.00199672             | 0.00168678      | 0.000309948 | ordinal_constraint_anchor  | 0,3,5            |
| movedtargets_anchor_residual | final9            | 0.00212071             | 0.00200904      | 0.00011167  | subject_logit_anchor       | 4,6,0            |
| movedtargets_anchor_residual | q2_jepa_bad       | 0.00349465             | 0.00110908      | 0.00238556  | bad_q2_jepa_anchor         | 3,2,0            |
| movedtargets_anchor_residual | lejepa_bad        | 0.00394018             | 0.00303696      | 0.000903219 | bad_lejepa_anchor          | 7,5,4            |
| movedtargets_anchor_residual | jepa_residual_bad | 0.00492069             | 0.00242051      | 0.00250018  | bad_all_target_jepa_anchor | 6,3,4            |
| movedtargets_anchor_shape    | mixmin            | 0                      | 0.002378        | 0.002378    | active_frontier            | 5,2,3            |
| movedtargets_anchor_shape    | a2c8              | 0.00113268             | 0.00195495      | 0.000822267 | previous_frontier          | 1,2,5            |
| movedtargets_anchor_shape    | raw05             | 0.00121967             | 0.00109606      | 0.000123607 | raw05_positive_anchor      | 1,2,0            |
| movedtargets_anchor_shape    | stage2            | 0.00163834             | 0.00188936      | 0.000251027 | stage2_local_cv_anchor     | 5,2,0            |
| movedtargets_anchor_shape    | ordinal           | 0.00199672             | 0.00169551      | 0.000301219 | ordinal_constraint_anchor  | 3,0,5            |
| movedtargets_anchor_shape    | final9            | 0.00212071             | 0.0020059       | 0.000114813 | subject_logit_anchor       | 4,6,0            |
| movedtargets_anchor_shape    | q2_jepa_bad       | 0.00349465             | 0.0011019       | 0.00239275  | bad_q2_jepa_anchor         | 3,2,0            |
| movedtargets_anchor_shape    | lejepa_bad        | 0.00394018             | 0.00303644      | 0.000903738 | bad_lejepa_anchor          | 7,5,4            |
| movedtargets_anchor_shape    | jepa_residual_bad | 0.00492069             | 0.00242119      | 0.00249949  | bad_all_target_jepa_anchor | 6,3,4            |
| targetprior_anchor_residual  | mixmin            | 0                      | 0.00241748      | 0.00241748  | active_frontier            | 4,5,2            |
| targetprior_anchor_residual  | a2c8              | 0.00113268             | 0.00208706      | 0.000954381 | previous_frontier          | 2,1,5            |
| targetprior_anchor_residual  | raw05             | 0.00121967             | 0.00175751      | 0.000537844 | raw05_positive_anchor      | 2,1,5            |
| targetprior_anchor_residual  | stage2            | 0.00163834             | 0.00153564      | 0.000102696 | stage2_local_cv_anchor     | 2,1,5            |
| targetprior_anchor_residual  | ordinal           | 0.00199672             | 0.00163907      | 0.000357657 | ordinal_constraint_anchor  | 3,2,4            |
| targetprior_anchor_residual  | final9            | 0.00212071             | 0.00249333      | 0.000372619 | subject_logit_anchor       | 4,3,6            |
| targetprior_anchor_residual  | q2_jepa_bad       | 0.00349465             | 0.00263061      | 0.000864031 | bad_q2_jepa_anchor         | 3,7,2            |
| targetprior_anchor_residual  | lejepa_bad        | 0.00394018             | 0.00294732      | 0.000992858 | bad_lejepa_anchor          | 7,4,3            |
| targetprior_anchor_residual  | jepa_residual_bad | 0.00492069             | 0.0032152       | 0.00170549  | bad_all_target_jepa_anchor | 7,6,4            |
| targetprior_anchor_shape     | mixmin            | 0                      | 0.00253613      | 0.00253613  | active_frontier            | 4,3,5            |
| targetprior_anchor_shape     | a2c8              | 0.00113268             | 0.00208239      | 0.000949711 | previous_frontier          | 2,1,5            |
| targetprior_anchor_shape     | raw05             | 0.00121967             | 0.00175669      | 0.000537027 | raw05_positive_anchor      | 2,1,5            |
| targetprior_anchor_shape     | stage2            | 0.00163834             | 0.00153065      | 0.00010769  | stage2_local_cv_anchor     | 2,1,5            |
| targetprior_anchor_shape     | ordinal           | 0.00199672             | 0.00216154      | 0.000164812 | ordinal_constraint_anchor  | 3,2,6            |
| targetprior_anchor_shape     | final9            | 0.00212071             | 0.00248665      | 0.000365935 | subject_logit_anchor       | 4,3,6            |
| targetprior_anchor_shape     | q2_jepa_bad       | 0.00349465             | 0.00264042      | 0.000854228 | bad_q2_jepa_anchor         | 3,7,2            |
| targetprior_anchor_shape     | lejepa_bad        | 0.00394018             | 0.00294865      | 0.000991526 | bad_lejepa_anchor          | 7,4,3            |
| targetprior_anchor_shape     | jepa_residual_bad | 0.00492069             | 0.00320822      | 0.00171247  | bad_all_target_jepa_anchor | 7,6,4            |

## Candidate Sensor Predictions

These are not public forecasts unless a view passes the gate.

| name                  | file                                                                                        | role                          | anchor_residual | anchor_shape | contextall_anchor_residual | contextall_anchor_shape | movedtargets_anchor_residual | movedtargets_anchor_shape | targetprior_anchor_residual | targetprior_anchor_shape |
| --------------------- | ------------------------------------------------------------------------------------------- | ----------------------------- | --------------- | ------------ | -------------------------- | ----------------------- | ---------------------------- | ------------------------- | --------------------------- | ------------------------ |
| mixmin                | analysis_outputs/submission_mixmin_0c916bb4.csv                                             | active_frontier               | 0.576307        | 0.576307     | 0.576307                   | 0.576307                | 0.576307                     | 0.576307                  | 0.576307                    | 0.576307                 |
| blend_m0p50_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv             | raw-structure bridge          | 0.57719         | 0.577166     | 0.57726                    | 0.57725                 | 0.577213                     | 0.57721                   | 0.577229                    | 0.577215                 |
| inv7_s1p00            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p00.csv                    | raw-structure bridge          | 0.577233        | 0.577257     | 0.577318                   | 0.577332                | 0.577594                     | 0.577592                  | 0.5773                      | 0.577315                 |
| inverse7blend_1040    | analysis_outputs/submission_inverse7blend_1040423d.csv                                      | raw-structure bridge          | 0.577233        | 0.577257     | 0.577318                   | 0.577332                | 0.577594                     | 0.577592                  | 0.5773                      | 0.577315                 |
| pair_sensor_6b        | analysis_outputs/submission_label_flow_focused_6b9335b1.csv                                 | S4/Q3 selector disambiguation | 0.577288        | 0.577275     | 0.577635                   | 0.577636                | 0.57762                      | 0.577621                  | 0.577637                    | 0.577638                 |
| blend_m0p25_s0p50     | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv             | raw-structure bridge          | 0.577299        | 0.577278     | 0.577333                   | 0.577323                | 0.577575                     | 0.577575                  | 0.577315                    | 0.577301                 |
| inv7_s0p50            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p50.csv                    | raw-structure bridge          | 0.577365        | 0.577367     | 0.577637                   | 0.577635                | 0.57757                      | 0.577569                  | 0.577659                    | 0.57738                  |
| a2c8                  | analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv                             | previous_frontier             | 0.577439        | 0.577439     | 0.577439                   | 0.577439                | 0.577439                     | 0.577439                  | 0.577439                    | 0.577439                 |
| raw05                 | jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv                                | raw05_positive_anchor         | 0.577526        | 0.577526     | 0.577526                   | 0.577526                | 0.577526                     | 0.577526                  | 0.577526                    | 0.577526                 |
| pair_sensor_1bb       | analysis_outputs/submission_label_flow_focused_1bbfb735.csv                                 | S4/Q3 selector disambiguation | 0.577648        | 0.577286     | 0.577633                   | 0.577635                | 0.577617                     | 0.577619                  | 0.577635                    | 0.577637                 |
| pair_sensor_1bb_s0p65 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | S4/Q3 selector disambiguation | 0.57765         | 0.577657     | 0.577631                   | 0.577632                | 0.577614                     | 0.577615                  | 0.577634                    | 0.577635                 |
| inv7_s0p25            | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv                    | raw-structure bridge          | 0.577652        | 0.577649     | 0.577631                   | 0.577629                | 0.577562                     | 0.577561                  | 0.577656                    | 0.577655                 |
| stage2                | analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv              | stage2_local_cv_anchor        | 0.577945        | 0.577945     | 0.577945                   | 0.577945                | 0.577945                     | 0.577945                  | 0.577945                    | 0.577945                 |
| ordinal               | analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv            | ordinal_constraint_anchor     | 0.578303        | 0.578303     | 0.578303                   | 0.578303                | 0.578303                     | 0.578303                  | 0.578303                    | 0.578303                 |
| final9                | analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv              | subject_logit_anchor          | 0.578427        | 0.578427     | 0.578427                   | 0.578427                | 0.578427                     | 0.578427                  | 0.578427                    | 0.578427                 |
| q2_jepa_bad           | jepa/submission_jepa_latent_q2_w0p45.csv                                                    | bad_q2_jepa_anchor            | 0.579801        | 0.579801     | 0.579801                   | 0.579801                | 0.579801                     | 0.579801                  | 0.579801                    | 0.579801                 |
| lejepa_bad            | jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv                                  | bad_lejepa_anchor             | 0.580247        | 0.580247     | 0.580247                   | 0.580247                | 0.580247                     | 0.580247                  | 0.580247                    | 0.580247                 |
| jepa_residual_bad     | jepa/submission_jepa_latent_residual_probe.csv                                              | bad_all_target_jepa_anchor    | 0.581227        | 0.581227     | 0.581227                   | 0.581227                | 0.581227                     | 0.581227                  | 0.581227                    | 0.581227                 |

## Decision

The anchor-calendar combination still does not certify a selector. The missing object is likely a stronger block-rate/count target or a different anchor-world construction.

## Outputs

- `analysis_outputs/post_mixmin_anchor_calendar_selector_views.csv`
- `analysis_outputs/post_mixmin_anchor_calendar_selector_loocv.csv`
- `analysis_outputs/post_mixmin_anchor_calendar_selector_candidates.csv`
- `analysis_outputs/post_mixmin_anchor_calendar_selector_anchor_features.csv`
- `analysis_outputs/post_mixmin_anchor_calendar_selector_world_energy.csv`
