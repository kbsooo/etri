# H004 HS-JEPA Sparse Routes

## Question

Can HS-JEPA become useful when the human-state latent is translated only through sparse episode-to-target routes, instead of the broad H003 all-target translator?

## H003 Constraint

- H003 semantic tiny public LB: `0.5763763885`.
- E247 public best anchor: `0.5761589494`.
- Observed delta: `+0.0002174391`, so broad all-target HS-JEPA materialization is rejected.
- H004 therefore limits each candidate to at most two active targets and at most 80 changed cells.

## H003 Route Evidence Used

| split | episode | target | delta_logloss | dominance | route_gate |
| --- | --- | --- | --- | --- | --- |
| subject5 | home_recovery | S3 | -0.013044173 | 1.000000000 | True |
| subject5 | bedtime_arousal | S3 | -0.010444948 | 1.000000000 | True |
| subject5 | social_overload | S3 | -0.009121835 | 0.888888889 | True |
| dateblock5 | routine_anchor_recovery | S2 | -0.005921853 | 0.888888889 | True |
| dateblock5 | home_recovery | S4 | -0.004999434 | 1.000000000 | True |
| dateblock5 | cashflow_stress | S3 | -0.004837016 | 1.000000000 | True |
| dateblock5 | home_recovery | S3 | -0.004706756 | 0.888888889 | True |
| subject5 | badnight_aftereffect | Q3 | -0.004585621 | 1.000000000 | True |
| dateblock5 | routine_fragmentation | S3 | -0.004425964 | 1.000000000 | True |
| subject5 | routine_anchor_recovery | Q2 | -0.003137053 | 0.888888889 | True |
| dateblock5 | routine_anchor_recovery | S3 | -0.002876823 | 0.888888889 | True |
| subject5 | physiology_strain | Q1 | -0.002834207 | 0.888888889 | True |
| subject5 | badnight_aftereffect | S2 | -0.002788849 | 0.888888889 | True |
| subject5 | routine_anchor_recovery | S3 | -0.002697847 | 1.000000000 | True |
| subject5 | routine_fragmentation | S1 | -0.002656371 | 1.000000000 | True |
| dateblock5 | commute_pressure | S4 | -0.002650042 | 0.888888889 | True |
| dateblock5 | home_recovery | Q2 | -0.002583347 | 0.888888889 | True |
| subject5 | bedtime_arousal | S1 | -0.002537004 | 1.000000000 | True |
| subject5 | routine_anchor_recovery | S1 | -0.002335291 | 0.888888889 | True |
| dateblock5 | physiology_strain | Q1 | -0.002017433 | 1.000000000 | True |
| subject5 | cashflow_stress | S3 | -0.003868382 | 0.666666667 | False |
| dateblock5 | commute_pressure | Q2 | -0.003861539 | 0.777777778 | False |
| dateblock5 | social_overload | Q2 | -0.002954707 | 0.777777778 | False |
| subject5 | routine_fragmentation | Q2 | -0.002792573 | 0.666666667 | False |
| dateblock5 | commute_pressure | Q3 | -0.002377026 | 0.666666667 | False |

## Bundle Stress

| bundle | target | episodes | split | delta_logloss | null_median | dominance | bundle_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3_badnight | Q3 | badnight_aftereffect | subject5 | -0.011851961 | -0.009006736 | 0.933333333 | True |
| s3_core | S3 | home_recovery,bedtime_arousal,social_overload | subject5 | -0.003676805 | 0.016915430 | 1.000000000 | True |
| q3_badnight | Q3 | badnight_aftereffect | dateblock5 | -0.002214142 | -0.002610448 | 0.466666667 | False |
| s3_core_plus | S3 | home_recovery,bedtime_arousal,social_overload,cashflow_stress,routine_fragmentation | subject5 | 0.000530310 | 0.020101767 | 0.933333333 | False |
| s1_fragment_arousal | S1 | routine_fragmentation,bedtime_arousal,routine_anchor_recovery | dateblock5 | 0.002987859 | 0.002180256 | 0.400000000 | False |
| s2_anchor_badnight | S2 | routine_anchor_recovery,badnight_aftereffect | dateblock5 | 0.006409593 | 0.020168076 | 1.000000000 | False |
| q2_anchor_home | Q2 | routine_anchor_recovery,home_recovery | dateblock5 | 0.006638792 | 0.007891032 | 0.533333333 | False |
| s1_fragment_arousal | S1 | routine_fragmentation,bedtime_arousal,routine_anchor_recovery | subject5 | 0.008350123 | 0.011052138 | 0.733333333 | False |
| q2_anchor_home | Q2 | routine_anchor_recovery,home_recovery | subject5 | 0.008651733 | 0.011923331 | 0.866666667 | False |
| s4_home_commute | S4 | home_recovery,commute_pressure | dateblock5 | 0.010474515 | 0.019596486 | 1.000000000 | False |
| s3_core_plus | S3 | home_recovery,bedtime_arousal,social_overload,cashflow_stress,routine_fragmentation | dateblock5 | 0.012206826 | 0.023505974 | 1.000000000 | False |
| s4_home_commute | S4 | home_recovery,commute_pressure | subject5 | 0.014028555 | 0.010041466 | 0.066666667 | False |
| s3_core | S3 | home_recovery,bedtime_arousal,social_overload | dateblock5 | 0.014147052 | 0.020301936 | 0.933333333 | False |
| s2_anchor_badnight | S2 | routine_anchor_recovery,badnight_aftereffect | subject5 | 0.018389917 | 0.030962404 | 1.000000000 | False |

## Route Translator Meta

| bundle | target | episodes | train_rate | oof_subject5_loss | test_pred_mean | test_pred_std |
| --- | --- | --- | --- | --- | --- | --- |
| s3_core | S3 | home_recovery,bedtime_arousal,social_overload | 0.662222222 | 0.659180537 | 0.649182975 | 0.212836391 |
| s3_core_plus | S3 | home_recovery,bedtime_arousal,social_overload,cashflow_stress,routine_fragmentation | 0.662222222 | 0.663520894 | 0.648436489 | 0.211616118 |
| q2_anchor_home | Q2 | routine_anchor_recovery,home_recovery | 0.562222222 | 0.704977110 | 0.587875384 | 0.131141478 |
| q3_badnight | Q3 | badnight_aftereffect | 0.600000000 | 0.672988038 | 0.670278439 | 0.122434406 |
| s2_anchor_badnight | S2 | routine_anchor_recovery,badnight_aftereffect | 0.651111111 | 0.685182082 | 0.601458159 | 0.202367747 |
| s4_home_commute | S4 | home_recovery,commute_pressure | 0.560000000 | 0.714023207 | 0.517539452 | 0.188150492 |
| s1_fragment_arousal | S1 | routine_fragmentation,bedtime_arousal,routine_anchor_recovery | 0.682222222 | 0.652719111 | 0.685735645 | 0.170260929 |

## Candidate Materialization

| candidate_id | basename | active_targets | changed_cells | changed_rows | mean_abs_logit_move | max_abs_logit_move | max_abs_prob_delta | best_bundle_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s3_core_top35 | submission_h004_s3_core_top35_9b076c27.csv | S3 | 35 | 35 | 0.000300464 | 0.018000000 | 0.004323703 | -0.003676805 |
| s3_core_top50 | submission_h004_s3_core_top50_15455f9d.csv | S3 | 50 | 50 | 0.000367323 | 0.016000000 | 0.003879836 | -0.003676805 |
| s3_coreplus_top35 | submission_h004_s3_coreplus_top35_53020041.csv | S3 | 35 | 35 | 0.000278086 | 0.016000000 | 0.003999941 | 0.000530310 |
| s3_core_tail25 | submission_h004_s3_core_tail25_14432619.csv | S3 | 25 | 25 | 0.000247591 | 0.018000000 | 0.004196151 | -0.003676805 |
| q2_anchor_top30 | submission_h004_q2_anchor_top30_2bd535d2.csv | Q2 | 30 | 30 | 0.000231950 | 0.014000000 | 0.003444906 | 0.006638792 |
| q3_badnight_top25 | submission_h004_q3_badnight_top25_34c80262.csv | Q3 | 25 | 25 | 0.000200000 | 0.014000000 | 0.003499803 | -0.011851961 |
| s2_anchor_top30 | submission_h004_s2_anchor_top30_3b720084.csv | S2 | 30 | 30 | 0.000227470 | 0.014000000 | 0.003438166 | 0.006409593 |
| s4_home_top30 | submission_h004_s4_home_top30_412d1a55.csv | S4 | 30 | 30 | 0.000238565 | 0.014000000 | 0.003472704 | 0.010474515 |
| s3_q2_micro | submission_h004_s3_q2_micro_eec39264.csv | Q2,S3 | 48 | 46 | 0.000328571 | 0.015000000 | 0.003733852 | -0.003676805 |
| s3_q3_micro | submission_h004_s3_q3_micro_e221f794.csv | Q3,S3 | 48 | 44 | 0.000330576 | 0.015000000 | 0.003733852 | -0.011851961 |

## Public-Free Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h004_s3_q3_micro_e221f794.csv | too_small_to_submit | -0.000019589 | -0.000041971 | -0.000002924 | 0.958333333 | -0.000097713 |
| submission_h004_s2_anchor_top30_3b720084.csv | too_small_to_submit | -0.000024576 | -0.000064471 | -0.000000541 | 0.916666667 | -0.000357067 |
| submission_h004_q3_badnight_top25_34c80262.csv | too_small_to_submit | -0.000031673 | -0.000081814 | 0.000002445 | 0.680555556 | -0.001079600 |
| submission_h004_s4_home_top30_412d1a55.csv | too_small_to_submit | -0.000001644 | -0.000013295 | 0.000018733 | 0.722222222 | -0.000604994 |
| submission_h004_s3_core_tail25_14432619.csv | below_selector_resolution | 0.000003830 | -0.000006605 | 0.000020377 | 0.555555556 | -0.000331211 |
| submission_h004_s3_coreplus_top35_53020041.csv | below_selector_resolution | 0.000004435 | -0.000008181 | 0.000025705 | 0.597222222 | 0.000708637 |
| submission_h004_s3_q2_micro_eec39264.csv | below_selector_resolution | 0.000011874 | -0.000006346 | 0.000025867 | 0.111111111 | -0.000410419 |
| submission_h004_s3_core_top50_15455f9d.csv | below_selector_resolution | 0.000003620 | -0.000012827 | 0.000029397 | 0.597222222 | 0.000927159 |
| submission_h004_s3_core_top35_9b076c27.csv | below_selector_resolution | 0.000004563 | -0.000012322 | 0.000029475 | 0.597222222 | 0.000967510 |
| submission_h004_q2_anchor_top30_2bd535d2.csv | below_selector_resolution | 0.000025119 | 0.000007603 | 0.000036126 | 0.041666667 | -0.002500104 |

## Anatomy

| basename | changed_rows | changed_cells | h003_alltarget_l1_ratio | h003_alltarget_cos | max_abs_prob_delta |
| --- | --- | --- | --- | --- | --- |
| submission_h004_q3_badnight_top25_34c80262.csv | 25 | 25 | 0.025846970 | 0.197186867 | 0.003499803 |
| submission_h004_s3_core_tail25_14432619.csv | 25 | 25 | 0.031997423 | 0.158337617 | 0.004196151 |
| submission_h004_q2_anchor_top30_2bd535d2.csv | 30 | 30 | 0.029975975 | 0.210158228 | 0.003444906 |
| submission_h004_s2_anchor_top30_3b720084.csv | 30 | 30 | 0.029397016 | 0.202203784 | 0.003438166 |
| submission_h004_s4_home_top30_412d1a55.csv | 30 | 30 | 0.030830858 | 0.209721327 | 0.003472704 |
| submission_h004_s3_core_top35_9b076c27.csv | 35 | 35 | 0.038830405 | 0.185711429 | 0.004323703 |
| submission_h004_s3_coreplus_top35_53020041.csv | 35 | 35 | 0.035938434 | 0.187717226 | 0.003999941 |
| submission_h004_s3_q2_micro_eec39264.csv | 46 | 48 | 0.042462774 | 0.232173031 | 0.003733852 |
| submission_h004_s3_q3_micro_e221f794.csv | 44 | 48 | 0.042721970 | 0.235567467 | 0.003733852 |
| submission_h004_s3_core_top50_15455f9d.csv | 50 | 50 | 0.047470874 | 0.206911399 | 0.003879836 |

## Selection

| decision | selected_uploadsafe_file | selected_basename | reason | strict_promote_count | info_sensor_count |
| --- | --- | --- | --- | --- | --- |
| information_sensor_only | none | submission_h004_s3_q3_micro_e221f794.csv | candidate is sparse and mean-favorable, but not strict enough for scarce public LB | 0 | 4 |

## Decision

H004 produced an information-sensor candidate, but it is not strict enough to call a score candidate.

## Files

- `hitl/h004_hsjepa_sparse_routes/h004_bundle_stress.csv`
- `hitl/h004_hsjepa_sparse_routes/h004_bundle_nulls.csv`
- `hitl/h004_hsjepa_sparse_routes/h004_candidates.csv`
- `hitl/h004_hsjepa_sparse_routes/h004_route_translator_meta.csv`
- `hitl/h004_hsjepa_sparse_routes/h004_selector_scores.csv`
- `hitl/h004_hsjepa_sparse_routes/h004_candidate_anatomy.csv`
- `hitl/h004_hsjepa_sparse_routes/h004_gate_scores.csv`
- `hitl/h004_hsjepa_sparse_routes/h004_selection.csv`
