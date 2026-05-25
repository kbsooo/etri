# CL Exhaustive Clue Hunt

## Claim

This run does not assume a new submission can be uploaded today. It exhaustively reuses current local evidence: submitted-file movement geometry, fold-local row predictions, and every numeric `cl/features` family.

## Known Public Axis

| file | known_public_lb | move_vs_anchor | dist_vs_sleep | dist_vs_raw | dist_vs_bad_import | good_axis_corr | bad_axis_corr | public_axis_score |
|---|---|---|---|---|---|---|---|---|
| submission_cl_catboost_state_proto_sleep_state_prob.csv | 0.614622 | 0.037350 | 0.000000 | 0.111987 | 0.139420 | 1.000000 | 0.358913 | 0.047677 |
| submission_v38_targetwise_catboost_proto_safe_prob.csv | 0.621864 | 0.024650 | 0.018065 | 0.122478 | 0.140603 | 0.908441 | 0.296100 | 0.029333 |
| submission_temporal_state_smoothing_wcap02_prob.csv | 0.631187 | 0.002913 | 0.036699 | 0.146368 | 0.144933 | 0.385472 | 0.506402 | -0.002884 |
| submission_temporal_state_smoothing_wcap01_prob.csv | 0.639420 | 0.012904 | 0.043153 | 0.150352 | 0.150527 | -0.208347 | -0.229732 | -0.005094 |
| submission_v39_imported_v81_conditional_latent_routing_raw_prob.csv | 0.661003 | 0.146233 | 0.139420 | 0.166517 | 0.000000 | 0.358913 | 1.000000 | -0.228475 |

Interpretation: the best known public move is still the CL sleep-state axis. The imported/raw axis is explicitly anti-public, so new clues must be either close to sleep-state or orthogonal to both sleep-state and imported raw.

## Existing Files Closest To The Good Axis

| file | public_axis_score | move_vs_anchor | dist_vs_sleep | dist_vs_bad_import | good_axis_corr | bad_axis_corr |
|---|---|---|---|---|---|---|
| submission_cl_catboost_public_axis_consensus_prob.csv | 0.043610 | 0.041286 | 0.003967 | 0.139438 | 0.995193 | 0.359324 |
| submission_cl_catboost_public_axis_rowgate_prob.csv | 0.042059 | 0.042830 | 0.005509 | 0.139487 | 0.991975 | 0.357152 |
| submission_cl_catboost_state_proto_target_focus_eventpatch_prob.csv | 0.037349 | 0.028820 | 0.009538 | 0.141756 | 0.893693 | 0.321264 |
| submission_cl_catboost_state_proto_target_focus_prob.csv | 0.035620 | 0.026920 | 0.011309 | 0.141802 | 0.893609 | 0.319692 |
| submission_cl_catboost_public_axis_step2_prob.csv | 0.032993 | 0.046528 | 0.013188 | 0.140670 | 0.883116 | 0.332420 |
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | 0.030821 | 0.031173 | 0.016566 | 0.141035 | 0.953616 | 0.347240 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | 0.030821 | 0.031173 | 0.016566 | 0.141035 | 0.953616 | 0.347240 |
| submission_cl_catboost_state_proto_confirmed_safe_prob.csv | 0.029333 | 0.024650 | 0.018065 | 0.140603 | 0.908441 | 0.296100 |
| submission_cl_catboost_public_axis_step3_prob.csv | 0.024155 | 0.055030 | 0.021560 | 0.141345 | 0.859268 | 0.340328 |
| submission_v38_targetwise_catboost_proto_publiclike_routed_prob.csv | 0.019790 | 0.018198 | 0.026537 | 0.141872 | 0.794687 | 0.251705 |
| submission_meta_anchor_s2dl20_s2sparse30_avg_prob.csv | 0.004548 | 0.001677 | 0.036932 | 0.146390 | 0.375290 | 0.131192 |
| submission_meta_anchor_s2sparse_replace_prob.csv | 0.004411 | 0.003954 | 0.036772 | 0.146288 | 0.254649 | 0.024141 |
| submission_meta_anchor_s2sparse_gate_top50_blend50_prob.csv | 0.004404 | 0.001566 | 0.036974 | 0.146282 | 0.231993 | -0.008378 |
| submission_meta_anchor_s2sparse_blend70_prob.csv | 0.004394 | 0.002768 | 0.036769 | 0.146214 | 0.254649 | 0.024141 |
| submission_meta_anchor_s2sparse_blend50_prob.csv | 0.004318 | 0.001977 | 0.036843 | 0.146201 | 0.254649 | 0.024141 |

## Row-Level Oracle From Fold-Local CatBoost

| target | mask | mean_delta | worst_delta | mean_weight | mean_move | families |
|---|---|---|---|---|---|---|
| S1 | gap_le3 | -0.049174 | -0.033447 | 0.816667 | 0.115662 | 3 |
| S1 | has_future | -0.034501 | -0.030415 | 0.725000 | 0.092190 | 2 |
| S1 | inside | -0.034501 | -0.030415 | 0.725000 | 0.092190 | 2 |
| S1 | all | -0.025883 | -0.023208 | 0.566667 | 0.080249 | 3 |
| Q1 | tail_after | -0.024622 | -0.013595 | 0.500000 | 0.089230 | 2 |
| Q3 | has_future | -0.022871 | -0.018026 | 0.525000 | 0.084280 | 2 |
| Q3 | inside | -0.022871 | -0.018026 | 0.525000 | 0.084280 | 2 |
| S2 | gap_le3 | -0.016414 | -0.007653 | 0.400000 | 0.067475 | 3 |
| S1 | tail_after | -0.015555 | -0.007902 | 0.375000 | 0.061066 | 2 |
| Q3 | all | -0.015383 | -0.013371 | 0.383333 | 0.060358 | 3 |
| Q3 | tail_after | -0.013872 | -0.013371 | 0.175000 | 0.037874 | 2 |
| S2 | tail_after | -0.012318 | -0.004088 | 0.200000 | 0.043648 | 2 |
| Q3 | gap_le3 | -0.012292 | -0.002378 | 0.316667 | 0.050389 | 3 |
| S3 | gap_le3 | -0.009902 | -0.001871 | 0.333333 | 0.050382 | 3 |
| S2 | has_future | -0.008714 | -0.005403 | 0.300000 | 0.050075 | 2 |
| S2 | inside | -0.008714 | -0.005403 | 0.300000 | 0.050075 | 2 |
| Q1 | gap_le3 | -0.007733 | -0.001063 | 0.233333 | 0.041980 | 3 |
| Q1 | all | -0.007503 | -0.003115 | 0.216667 | 0.036145 | 3 |
| S2 | all | -0.007348 | -0.004088 | 0.216667 | 0.042946 | 3 |
| Q2 | tail_after | -0.006180 | -0.004227 | 0.175000 | 0.031686 | 2 |

Interpretation: this is the upper-bound map for where the current CatBoost/prototype signal is real. Targets/masks absent here should not be pushed without a new feature family.

## New Feature-Family Clues

| feature_family | target | mirror_hole_delta | worst_delta | mean_delta | mean_abs_move | mean_features |
|---|---|---|---|---|---|---|
| prior_sleep_proxy_features_v1 | S1 | -0.039081 | -0.022932 | -0.033698 | 0.085845 | 80.333333 |
| prior_sleep_window_features_v1 | S1 | -0.037627 | -0.020285 | -0.041852 | 0.088828 | 81.000000 |
| goal4_sleep_boundary_rest_features_v1 | Q1 | -0.024232 | -0.015751 | -0.023969 | 0.076645 | 81.000000 |
| goal4_sleep_boundary_rest_features_v1 | S1 | -0.024175 | -0.024119 | -0.030041 | 0.087588 | 81.000000 |
| prior_sleep_window_features_v1 | S2 | -0.012118 | -0.009318 | -0.018564 | 0.062803 | 81.000000 |
| prior_sleep_window_features_v1 | Q1 | -0.010885 | -0.007355 | -0.012237 | 0.058435 | 81.000000 |
| goal4_sleep_boundary_rest_features_v1 | S2 | -0.010468 | -0.009957 | -0.011839 | 0.044523 | 81.000000 |
| goal4_sleep_boundary_rest_features_v1 | S4 | -0.010050 | -0.003073 | -0.010929 | 0.047803 | 81.000000 |
| prior_sleep_proxy_features_v1 | Q1 | -0.010041 | -0.004659 | -0.010547 | 0.043811 | 80.333333 |
| prior_sleep_window_features_v1 | S4 | -0.009008 | -0.002973 | -0.010196 | 0.048256 | 81.000000 |
| goal4_hour_transition_features_v1 | S2 | -0.008938 | -0.003455 | -0.007215 | 0.036137 | 81.000000 |
| prior_sleep_proxy_features_v1 | S4 | -0.008256 | -0.004331 | -0.011798 | 0.047653 | 80.333333 |
| goal4_sleep_boundary_rest_features_v1 | Q2 | -0.007895 | -0.003344 | -0.006378 | 0.028180 | 81.000000 |
| goal4_hour_transition_features_v1 | Q3 | -0.007414 | -0.005422 | -0.009091 | 0.042522 | 81.000000 |
| goal4_hour_transition_features_v1 | Q1 | -0.005183 | -0.004235 | -0.006132 | 0.032807 | 81.000000 |
| goal4_hour_transition_features_v1 | S4 | -0.004384 | -0.001740 | -0.004894 | 0.041885 | 81.000000 |
| prior_sleep_proxy_features_v1 | S3 | -0.003677 | -0.002558 | -0.004642 | 0.028077 | 80.333333 |
| prior_sleep_proxy_features_v1 | S2 | -0.003535 | -0.003512 | -0.005496 | 0.031959 | 80.333333 |

## Decision

- Feature families that passed strict gates are the only credible new-signal candidates. Use them target-wise, not as global model input.
- `prior_sleep_proxy_features_v1` on `S1`: mirror/hole -0.0391, worst -0.0229, move 0.0858.
- `prior_sleep_window_features_v1` on `S1`: mirror/hole -0.0376, worst -0.0203, move 0.0888.
- `goal4_sleep_boundary_rest_features_v1` on `Q1`: mirror/hole -0.0242, worst -0.0158, move 0.0766.
- `goal4_sleep_boundary_rest_features_v1` on `S1`: mirror/hole -0.0242, worst -0.0241, move 0.0876.
- `prior_sleep_window_features_v1` on `S2`: mirror/hole -0.0121, worst -0.0093, move 0.0628.
- `prior_sleep_window_features_v1` on `Q1`: mirror/hole -0.0109, worst -0.0074, move 0.0584.
- `goal4_sleep_boundary_rest_features_v1` on `S2`: mirror/hole -0.0105, worst -0.0100, move 0.0445.
- `goal4_sleep_boundary_rest_features_v1` on `S4`: mirror/hole -0.0101, worst -0.0031, move 0.0478.

## Next Experiment Queue

1. Build tomorrow's probes as target-isolated files: S1-only, Q3-only, S1+Q3, and S1+Q3 with S2 capped.
2. If a feature family appears above, train only that family for the listed target and only on inside/future or small-gap rows.
3. Do not extrapolate `public_axis_step2/step3`; validation already says it worsens S2/Q3 movement.