# E91 E72-Updated Selector Collapse Audit

## Observe

E72 is the first public-negative anchor after mixmin. It is close to mixmin in public score but close in movement geometry as well, so it is a direct test of whether movement-fingerprint proxies can now rank post-mixmin candidates.

## Wonder

Does adding E72 make the public proxy usable for choosing among E86, E90, E89, and E85, or does the proxy fail on the exact frontier/E72 distinction?

## Hypothesis

H86: an E72-updated movement-fingerprint selector can rank the next mixmin-relative candidates.

## Method

- Reuse the public-anchor movement features from `public_anchor_bottleneck_decomposition.py`.
- Include known public anchors from `public_probe_observations.csv`, now including mixmin and E72, plus manual A2C8.
- Run fixed LOOCV ridge proxy families and inspect their holdout errors on mixmin and E72.
- Score only the current post-mixmin decision set: E85, E86, E87 contrasts, E89, E90.

## Known Public Anchors

| file | public_lb | mean_abs_move_vs_a2c8 | mean_abs_move_vs_raw05 | bad_axis_abs_load | good_span_residual_ratio |
| --- | --- | --- | --- | --- | --- |
| submission_mixmin_0c916bb4.csv | 0.576307 | 0.0456142 | 0.0490298 | 0.213626 | 0.65571 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576408 | 0.0467284 | 0.0499428 | 0.206975 | 0.652438 |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.577439 | 0 | 0.00853087 | 0.0369058 | 8.85476e-10 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526 | 0.00853087 | 0 | 0.02479 | 1.08472e-09 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577945 | 0.0440096 | 0.0392914 | 0 | 0 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303 | 0.128555 | 0.129665 | 0.551693 | 0.941853 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427 | 0.175679 | 0.179981 | 0.468007 | 0.781545 |
| submission_jepa_latent_q2_w0p45.csv | 0.579801 | 0.0728516 | 0.0682492 | 1.5113 | 0.999954 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580247 | 0.127474 | 0.12565 | 1.27587 | 0.995345 |
| submission_jepa_latent_residual_probe.csv | 0.581227 | 0.110359 | 0.107275 | 1.78905 | 0.995229 |

## LOOCV Proxy Models

| model | mae | rmse | max_abs_error | pairwise_rank_accuracy | p90_abs_error |
| --- | --- | --- | --- | --- | --- |
| raw05_a2c8_compat | 0.000543412 | 0.000641783 | 0.00114272 | 0.8 | 0.00101023 |
| good_bad_axes | 0.00086514 | 0.000971823 | 0.00163718 | 0.733333 | 0.00154959 |
| constant_median | 0.00123811 | 0.00155499 | 0.00310316 |  | 0.0022207 |
| bad_axes_only | 0.00130364 | 0.00242485 | 0.00734806 | 0.733333 | 0.00178726 |
| target_move_core | 0.00132957 | 0.00155766 | 0.002837 | 0.755556 | 0.00218893 |
| compact_energy | 0.0057626 | 0.0147103 | 0.0463145 | 0.711111 | 0.00704842 |

## Critical Holdout Checks

- Best fixed proxy: `raw05_a2c8_compat` with MAE `0.000543412` and p90 abs error `0.001010234`.
- Mixmin is the actual frontier at `0.5763066405`, but best-proxy LOO predicts `0.5774493627`; error `+0.001142722`.
- E72 actual delta vs mixmin is `+0.0001011367`; best-proxy LOO predicted E72-minus-mixmin `-0.0000460726`.
- The proxy's p90 error is `0.001010234`, about `9.99x` the entire E72 public miss.

## Post-Mixmin Candidate Proxy Scores

| role | file | known_public_lb | proxy_pred_mean | proxy_delta_vs_mixmin_public | proxy_pred_spread | below_proxy_resolution | mean_abs_move_vs_a2c8 | mean_abs_move_vs_raw05 | bad_axis_abs_load | good_span_residual_ratio | candidate_risk_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| max_upside_consensus | submission_e86_e85_consensus_a3f7c96f.csv |  | 0.577003 | 0.000696389 | 7.09974e-05 | False | 0.041089 | 0.0444454 | 0.183446 | 0.629899 | 0.577115 |
| pareto_row_decontam | submission_e90_e72pareto_28925de5.csv |  | 0.577005 | 0.000698753 | 7.43525e-05 | False | 0.0411283 | 0.0444802 | 0.185318 | 0.630316 | 0.577119 |
| no_q2_contrast | submission_e87_noq2_source_consensus_a85c4e39.csv |  | 0.577014 | 0.000706861 | 7.06981e-05 | False | 0.0410318 | 0.0443654 | 0.189264 | 0.6316 | 0.577127 |
| no_overstep_contrast | submission_e87_q2_nooverstep_consensus_acd7add0.csv |  | 0.57701 | 0.0007032 | 8.90682e-05 | False | 0.0419225 | 0.0452804 | 0.189482 | 0.63371 | 0.57713 |
| min_contamination_decontam | submission_e89_e72decontam_00d7807f.csv |  | 0.577014 | 0.000707622 | 8.02871e-05 | False | 0.0411702 | 0.0445164 | 0.190934 | 0.631314 | 0.577131 |
| conservative_target_prune | submission_e85_inverse_conflict_pruned_58b23ed1.csv |  | 0.577018 | 0.000711426 | 8.46968e-05 | False | 0.0418181 | 0.0451547 | 0.193676 | 0.635491 | 0.577137 |
| frontier | submission_mixmin_0c916bb4.csv | 0.576307 | 0.577034 | 0.00072761 | 0.000153896 | False | 0.0456142 | 0.0490298 | 0.213626 | 0.65571 | 0.577183 |
| failed_public_anchor | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576408 | 0.577044 | 0.000737477 | 0.00013222 | False | 0.0467284 | 0.0499428 | 0.206975 | 0.652438 | 0.577184 |

## Falsification

H86 is rejected as a submission selector. The updated proxy cannot explain the frontier distinction with enough resolution: it overprices/underprices mixmin-scale anchors by more than the E72 public signal itself.

## Decision

No E91 submission is materialized. The correct action is to keep E86/E90/E89 as predeclared public sensors, not to rank them by a regression proxy trained on the known public anchors. If one slot is used, the choice should be the hypothesis being tested: E86 for max-upside structural consensus, E90 for row-coherent E72 repair, E89 for minimum contamination.
