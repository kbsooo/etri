# E98 E95-Updated Selector Audit

## Observe

E95 is the first public-positive post-mixmin movement. This gives the known-LB proxy one more near-frontier anchor: mixmin, failed E72, and successful E95 now bracket the hard-tail branch.

## Wonder

Does adding E95 make movement-fingerprint public regression sharp enough to choose E90/E86/E85, or does it still fail at the exact scale of the new frontier?

## Hypothesis

H92: E95 as a known public anchor makes the current movement proxy useful for E95-relative candidate ranking.

## Method

- Add `submission_e95_hardtail_541e3973.csv` public `0.5762913298` to `public_probe_observations.csv`.
- Reuse fixed LOOCV ridge proxy families from `public_anchor_bottleneck_decomposition.py`.
- Audit critical holdout deltas among E95, mixmin, and E72.
- Score the unresolved post-E95 queue: E90, E86, E85, E89, and E87 contrasts.

## Known Public Anchors

| file | public_lb | mean_abs_move_vs_a2c8 | mean_abs_move_vs_raw05 | bad_axis_abs_load | good_span_residual_ratio |
| --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv | 0.576291 | 0.0411316 | 0.044481 | 0.187187 | 0.630994 |
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
| raw05_a2c8_compat | 0.000520095 | 0.000577565 | 0.000858236 | 0.909091 | 0.000816497 |
| good_bad_axes | 0.000856084 | 0.000983942 | 0.00184123 | 0.672727 | 0.00162788 |
| constant_median | 0.00127589 | 0.00159807 | 0.00328235 |  | 0.00230184 |
| target_move_core | 0.00136797 | 0.00153274 | 0.00291647 | 0.745455 | 0.00224814 |
| bad_axes_only | 0.00141674 | 0.0026341 | 0.00835121 | 0.690909 | 0.00125254 |
| compact_energy | 0.00551281 | 0.0145303 | 0.0479786 | 0.745455 | 0.00274878 |

## Critical Near-Frontier Holdouts

| pair | newer_file | older_file | actual_older_minus_newer | pred_older_minus_newer | correct_sign | abs_error | newer_loo_error | older_loo_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_minus_e95 | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | 1.53107e-05 | 7.72344e-05 | True | 6.19237e-05 | 0.000754573 | 0.000816497 |
| e72_minus_mixmin | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.000101137 | -3.05135e-05 | False | 0.00013165 | 0.000816497 | 0.000684846 |
| e72_minus_e95 | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.000116447 | 4.6721e-05 | True | 6.97264e-05 | 0.000754573 | 0.000684846 |

## Candidate Proxy Scores

| role | file | known_public_lb | proxy_pred_mean | proxy_delta_vs_e95_public | edge_to_proxy_mae_e95 | proxy_pred_spread | below_proxy_resolution | mean_abs_move_vs_a2c8 | mean_abs_move_vs_raw05 | bad_axis_abs_load | good_span_residual_ratio | candidate_risk_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| max_upside_consensus | submission_e86_e85_consensus_a3f7c96f.csv |  | 0.57684 | 0.000548288 | -1.05421 | 1.75658e-05 | False | 0.041089 | 0.0444454 | 0.183446 | 0.629899 | 0.576933 |
| pareto_row_decontam | submission_e90_e72pareto_28925de5.csv |  | 0.576842 | 0.000550678 | -1.0588 | 2.13142e-05 | False | 0.0411283 | 0.0444802 | 0.185318 | 0.630316 | 0.576937 |
| current_frontier | submission_e95_hardtail_541e3973.csv | 0.576291 | 0.576845 | 0.000553488 | -1.0642 | 2.25067e-05 | False | 0.0411316 | 0.044481 | 0.187187 | 0.630994 | 0.576941 |
| no_q2_contrast | submission_e87_noq2_source_consensus_a85c4e39.csv |  | 0.57685 | 0.00055909 | -1.07498 | 1.71135e-05 | False | 0.0410318 | 0.0443654 | 0.189264 | 0.6316 | 0.576945 |
| no_overstep_contrast | submission_e87_q2_nooverstep_consensus_acd7add0.csv |  | 0.576846 | 0.000554962 | -1.06704 | 3.79143e-05 | False | 0.0419225 | 0.0452804 | 0.189482 | 0.63371 | 0.576948 |
| min_contamination_decontam | submission_e89_e72decontam_00d7807f.csv |  | 0.576851 | 0.000559808 | -1.07636 | 2.80011e-05 | False | 0.0411702 | 0.0445164 | 0.190934 | 0.631314 | 0.57695 |
| conservative_floor | submission_e85_inverse_conflict_pruned_58b23ed1.csv |  | 0.576855 | 0.000563431 | -1.08332 | 3.28227e-05 | False | 0.0418181 | 0.0451547 | 0.193676 | 0.635491 | 0.576956 |
| inverse_top_contrast | submission_e87_inverse_top_prior_consensus_5445ec28.csv |  | 0.576854 | 0.000562738 | -1.08199 | 4.08884e-05 | False | 0.0431943 | 0.0465799 | 0.194867 | 0.643415 | 0.576959 |
| previous_frontier | submission_mixmin_0c916bb4.csv | 0.576307 | 0.576869 | 0.000577896 | -1.11114 | 0.000110179 | False | 0.0456142 | 0.0490298 | 0.213626 | 0.65571 | 0.577003 |
| failed_public_anchor | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576408 | 0.576882 | 0.000590219 | -1.13483 | 8.70705e-05 | False | 0.0467284 | 0.0499428 | 0.206975 | 0.652438 | 0.577006 |

## Falsification

- Best fixed proxy: `raw05_a2c8_compat`, MAE `0.000520095`, p90 abs error `0.000816497`.
- New E95 edge over mixmin: `0.0000153107`. The best proxy p90 error is `53.33x` this edge.
- E72 miss over mixmin: `0.0001011367`. The best proxy p90 error is `8.07x` this miss.
- Best future candidate by this proxy is `max_upside_consensus` / `submission_e86_e85_consensus_a3f7c96f.csv` with proxy delta vs E95 `+0.000548288`.
- Future proxy spread is `0.000015142`, still not interpretable unless the proxy can hold out the near-frontier anchors.

Verdict: `rejected` for H92.

## Decision

Do not use E98 proxy scores as the next submission order. E95 adds a valuable public anchor, but the current known-LB regression remains too coarse at the `1e-5` to `1e-4` frontier scale. The next public file should remain a hypothesis sensor:

1. `E90` if the question is whether preserving more row-coherent E86 structure beats E95's cell-local hard-tail cleanup.
2. `E86` if the question is maximum source-consensus structural upside despite higher hard-tail exposure.
3. `E85` if the question is whether the conservative p95 tail floor beats retained E86 structure.

## Files

- `e98_e95_updated_selector_known_loo.csv`
- `e98_e95_updated_selector_model_scores.csv`
- `e98_e95_updated_selector_candidates.csv`
