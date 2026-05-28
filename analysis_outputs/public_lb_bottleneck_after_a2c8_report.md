# Public LB Bottleneck After A2C8

## Bottom Line

- New best public LB: `submission_frontier_cvjepa_refine_a2c8d2c8.csv` = `0.577439321`.
- Improvement vs raw05: `-0.0000869862`.
- Remaining distance to `0.540000000`: `0.037439321`.
- The last improvement covers only `0.2323%` of the remaining 0.54 gap; the same-size gain would need about `430.4x` more.

## Validation Bottleneck

- Best 7-anchor leave-one-public-anchor proxy: `loocv_ridge_signed_axes_a1` MAE/RMSE `0.0002979250` / `0.0003593046`.
- For `a2c8`, the raw05-relative proxy predicted `0.5775229594`, missing public by `0.0000836384`.
- But the leave-one-anchor signed-axis model predicted `0.5778666938`, missing by `0.0004273728`. This marks `a2c8` as out-of-family for the old six public anchors.

## Movement Bottleneck

- `a2c8` mean absolute move vs raw05 is only `0.0016463907` per cell.
- Even if every moved probability pointed toward the hidden truth, the best-case average logloss gain is `0.0050731896`, only `13.55%` of the 0.54 gap.

## Known Public Anchors With A2C8

| file                                                            | known_public | actual_anchor_score_final | posterior_expected_public_vs_anchor | delta_vs_raw05_rawaxis | bad_residual_axis_ratio | mean_abs_move_vs_raw05 |
| --------------------------------------------------------------- | ------------ | ------------------------- | ----------------------------------- | ---------------------- | ----------------------- | ---------------------- |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv         | 0.5775263072 | 0.5779059944              | 0.5775263072                        | 0.0000000000           | 0.0048441395            | 0.0000000000           |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv   | 0.5779449757 | 0.5779449757              | 0.5779449757                        | 0.0004186685           | 0.0000000000            | 0.0000000000           |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.5783033652 | 0.5799865296              | 0.5783033652                        | 0.0038030797           | -0.0035798689           | 0.0000000000           |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv   | 0.5784273528 | 0.5813157907              | 0.5784273528                        | 0.0055868627           | -0.0476969461           | 0.0000000000           |
| submission_jepa_latent_q2_w0p45.csv                             | 0.5798012862 | 0.5801455759              | 0.5798012862                        | 0.0021365395           | 0.5726249631            | 0.0000000000           |
| submission_jepa_latent_residual_probe.csv                       | 0.5812273278 | 0.5802891189              | 0.5812273278                        | 0.0024925752           | 1.0000000000            | 0.0000000000           |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv                  | 0.5774393210 | 0.5778270682              | 0.5768966986                        | 0.0000000725           | 0.0001202771            | 0.0016463907           |

## 7-Anchor Proxy Scores

| model                          | mae          | rmse         | max_abs_error | bias_mean_pred_minus_public | pairwise_rank_accuracy |
| ------------------------------ | ------------ | ------------ | ------------- | --------------------------- | ---------------------- |
| loocv_ridge_signed_axes_a1     | 0.0002979250 | 0.0003593046 | 0.0006166222  | 0.0001050947                | 0.9523809524           |
| loocv_ridge_abs_axes_a1        | 0.0003254873 | 0.0003873977 | 0.0006054533  | 0.0001187168                | 0.9047619048           |
| loocv_ridge_anchor_abs_axes_a1 | 0.0003512950 | 0.0004167666 | 0.0006601056  | 0.0001063437                | 0.9047619048           |
| loocv_ridge_public_shape_a1    | 0.0003512950 | 0.0004167666 | 0.0006601056  | 0.0001063437                | 0.9047619048           |
| loocv_ridge_mean_a1            | 0.0010660987 | 0.0014010794 | 0.0025057685  | 0.0000934350                | 0.6666666667           |
| loocv_ridge_actual_a1          | 0.0011161864 | 0.0014249271 | 0.0026205804  | 0.0001106355                | 0.6666666667           |
| loocv_ridge_anchor_gap_a1      | 0.0012225642 | 0.0014433698 | 0.0026717877  | 0.0001906527                | 0.7142857143           |

## A2C8 Movement Bounds

| file                                                    | mean_abs_move_vs_raw05 | max_abs_move_vs_raw05 | active_cell_rate_gt_1e-4 | best_case_logloss_gain_if_all_moves_correct | best_case_gap_fraction_to_0p54 |
| ------------------------------------------------------- | ---------------------- | --------------------- | ------------------------ | ------------------------------------------- | ------------------------------ |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv          | 0.0016463907           | 0.0239652862          | 0.9062857143             | 0.0050731896                                | 0.1355043175                   |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.0000000000           | 0.0000000000          | 0.0000000000             | 0.0000000000                                | 0.0000000000                   |

## Local JEPA Signal vs Public Transfer

Cross-view JEPA surprise features improve local OOF strongly, but the public-safe graft only converts a tiny part of that signal:

| combo                            | base_loss    | candidate_loss | delta         | subject_half_delta | subject_half_win_rate | geometry_delta | geometry_win_rate |
| -------------------------------- | ------------ | -------------- | ------------- | ------------------ | --------------------- | -------------- | ----------------- |
| cvjepa_surprise_full_nonq2       | 0.5675309247 | 0.5646068482   | -0.0029240765 | -0.0029323116      | 0.9423076923          | -0.0034774605  | 0.8750000000      |
| cvjepa_surprise_full_nonq2_w030  | 0.5675309247 | 0.5651136900   | -0.0024172346 | -0.0024236040      | 0.9846153846          | -0.0027401668  | 1.0000000000      |
| cvjepa_surprise_core_q1_q3_s2_s4 | 0.5675309247 | 0.5651957335   | -0.0023351912 | -0.0022590688      | 0.9115384615          | -0.0028821278  | 0.8750000000      |
| cvjepa_surprise_s_targets        | 0.5675309247 | 0.5655769948   | -0.0019539299 | -0.0020376131      | 0.8615384615          | -0.0021378571  | 0.8750000000      |
| cvjepa_surprise_full_nonq2_w020  | 0.5675309247 | 0.5657135547   | -0.0018173700 | -0.0018219395      | 1.0000000000          | -0.0020147718  | 1.0000000000      |
| cvjepa_surprise_q1_s2            | 0.5675309247 | 0.5660898414   | -0.0014410833 | -0.0013572346      | 0.9615384615          | -0.0021182518  | 0.8750000000      |
| cvjepa_surprise_q_targets        | 0.5675309247 | 0.5665607781   | -0.0009701466 | -0.0008946985      | 0.9846153846          | -0.0013396034  | 0.8750000000      |

Raw timeline JEPA rescue also shows that bigger local moves looked better OOF, while the submitted safe scale was only a public-safe compromise:

| candidate                                                | scale        | oof_loss     | oof_delta_vs_stage2 | bad_axis_projection_ratio | good_axis_projection_ratio | jepa_bad_axis_ratio |
| -------------------------------------------------------- | ------------ | ------------ | ------------------- | ------------------------- | -------------------------- | ------------------- |
| submission_raw_timeline_jepa_rescue_strict_scale0p25.csv | 0.2500000000 | 0.5664468718 | -0.0010840529       | 0.0109058700              | -0.0022871053              | 0.0051327421        |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv  | 0.5000000000 | 0.5656089320 | -0.0019219927       | 0.0192885043              | -0.0058717103              | 0.0073660908        |
| submission_raw_timeline_jepa_rescue_strict_scale0p75.csv | 0.7500000000 | 0.5650166127 | -0.0025143120       | 0.0249656470              | -0.0116513639              | 0.0066620276        |
| submission_raw_timeline_jepa_rescue_strict_scale1p0.csv  | 1.0000000000 | 0.5646719644 | -0.0028589603       | 0.0277778894              | -0.0204021951              | 0.0028454882        |

## Frontier Focus

| file                                           | is_submitted_a2c8 | label                                                                                       | available_raw05_relative_delta_vs_raw05_public | available_raw05_relative_model_spread | actual_anchor_score_final | posterior_expected_public_vs_anchor | mean_abs_move_vs_raw05 |
| ---------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------- | ------------------------- | ----------------------------------- | ---------------------- |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | True              | e40:full_nonq2_w030\|q3_s2_s4\|ones\|agree_raw_q65\|dir+1\|w0.22\|c0.024                    | -0.0000033478                                  | 0.0000720155                          | 0.5778270682              | 0.5768966986                        | 0.0016463907           |
| submission_frontier_cvjepa_refine_e725a22f.csv | False             | lowbad_edge:full_nonq2_w020\|q1_s2\|surprise_top70\|agree_raw_q65\|dir-1\|w0.14\|c0.014     | -0.0000041086                                  | 0.0000703382                          | 0.5778277704              | 0.5769058973                        | 0.0015925399           |
| submission_frontier_cvjepa_refine_298aaf05.csv | False             | lowbad_bal:full_nonq2_w030\|q1_s2\|surprise_top70\|agree_raw_q65\|dir-1\|w0.34\|c0.006      | -0.0000041050                                  | 0.0000703282                          | 0.5778277924              | 0.5769057990                        | 0.0015925126           |
| submission_frontier_cvjepa_refine_cc1a74e3.csv | False             | lowbad_edge:full_nonq2_w020\|s_targets\|surprise_top50\|agree_raw_q65\|dir-1\|w0.14\|c0.006 | -0.0000040999                                  | 0.0000704393                          | 0.5778277629              | 0.5769055703                        | 0.0015936030           |
| submission_frontier_cvjepa_refine_4e2759ea.csv | False             | e40:full_nonq2_w030\|s_targets\|surprise_top70\|agree_raw_q65\|dir-1\|w0.14\|c0.006         | -0.0000040701                                  | 0.0000704963                          | 0.5778277905              | 0.5769046324                        | 0.0015957627           |
| submission_frontier_cvjepa_refine_1d850e9b.csv | False             | e40:full_nonq2_w020\|s_targets\|surprise_top70\|agree_raw_q65\|dir-1\|w0.14\|c0.006         | -0.0000040697                                  | 0.0000704986                          | 0.5778277905              | 0.5769046040                        | 0.0015958024           |
| submission_frontier_cvjepa_refine_e8dc6e07.csv | False             | lowbad_bal:full_nonq2_w030\|s2_only\|surprise_top50\|agree_raw_q65\|dir-1\|w0.08\|c0.024    | -0.0000040661                                  | 0.0000703275                          | 0.5778278725              | 0.5769043695                        | 0.0015945379           |
| submission_frontier_cvjepa_refine_e392642d.csv | False             | lowbad_bal:full_nonq2_w020\|s2_only\|ones\|agree_raw_q65\|dir-1\|w0.22\|c0.006              | -0.0000040652                                  | 0.0000704830                          | 0.5778277792              | 0.5769043674                        | 0.0015963362           |
| submission_frontier_cvjepa_refine_b1d38df6.csv | False             | lowbad_bal:full_nonq2_w030\|no_q2\|surprise_top70\|all\|dir+1\|w0.04\|c0.014                | -0.0000040617                                  | 0.0000704120                          | 0.5778275958              | 0.5769038478                        | 0.0015981440           |
| submission_frontier_cvjepa_refine_54984ae1.csv | False             | lowbad_bal:full_nonq2_w020\|no_q2\|surprise_top70\|all\|dir+1\|w0.04\|c0.014                | -0.0000040614                                  | 0.0000704047                          | 0.5778275940              | 0.5769038586                        | 0.0015980615           |
| submission_frontier_cvjepa_refine_a13ba578.csv | False             | lowbad_bal:full_nonq2_w030\|no_q2\|surprise_top70\|all\|dir+1\|w0.08\|c0.006                | -0.0000040557                                  | 0.0000704066                          | 0.5778276277              | 0.5769039111                        | 0.0015980860           |
| submission_frontier_cvjepa_refine_3351fd05.csv | False             | lowbad_bal:full_nonq2_w020\|no_q2\|surprise_top70\|all\|dir+1\|w0.08\|c0.006                | -0.0000040554                                  | 0.0000704057                          | 0.5778276296              | 0.5769038910                        | 0.0015980923           |

## Interpretation

1. The current search is mostly optimizing a very thin public-compatible tangent around raw05. That can produce 1e-4 gains but cannot plausibly produce a 0.037 logloss drop.
2. The local OOF signal is real, but public transfer is bottlenecked by hidden-block distribution shift and by sparse public feedback. Six to seven public anchors are not enough to calibrate new candidate families.
3. To attack 0.54, the next branch must either identify hidden test labels/subsets much more directly, or train a substantially stronger row-level representation whose larger moves survive public-axis validation. Micro-refines around raw05 are now a measurement tool, not the main path.
