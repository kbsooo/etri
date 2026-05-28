# E54 Raw Overnight Block Context Probe

## Observe

E53 kept calendar-flank state as energy only: local donors improved pseudo-hidden blocks, but strict subject-excluded donors failed. The next question is whether the observed raw overnight block context is the missing representation.

## Wonder

Can raw overnight context plus flanks predict hidden block target rates under strict subject exclusion, or does raw context collapse into subject/domain shortcut?

## Hypothesis

H54: if raw overnight context encodes the hidden sleep-state generator, raw/ctx block embeddings should beat subject mean and calendar-count strict on pseudo-hidden blocks without using same-subject donors, especially on S targets, and their real hidden rates should explain mixmin with broader target alignment.

## Method

- Pseudo-hidden blocks: `369`; actual hidden blocks: `36`.
- Context: `overnight_sensor_features_v2.parquet` feature families compressed to row PCA, aggregated to block mean/std/min/max/first/last/slope, optionally concatenated with labeled flank context.
- Prediction: kNN donor rate posterior with shrinkage to subject mean; strict mode excludes the target subject, local mode is retained only as shortcut diagnostic.
- Stress: pseudo-hidden weighted row LogLoss/count NLL, targetwise recovery, latent geometry, and expected hidden-block CE delta for mixmin/raw05 versus a2c8.

## Pseudo-Hidden Summary

| method | weighted_row_logloss | delta_weighted_row_logloss_vs_subject | weighted_count_nll_per_row | rate_mae_weighted | support_mean | dist_median |
| --- | --- | --- | --- | --- | --- | --- |
| night_phone_rawctx_local_k8_a24 | 0.601641 | -0.011361 | 0.279409 | 0.185411 | 8.000000 | 0.964152 |
| night_coverage_rawctx_local_k8_a24 | 0.601802 | -0.011200 | 0.279570 | 0.185454 | 8.000000 | 0.966533 |
| night_all_rawctx_local_k8_a24 | 0.602396 | -0.010606 | 0.280164 | 0.186078 | 8.000000 | 0.918822 |
| night_watch_rawctx_local_k8_a24 | 0.602448 | -0.010554 | 0.280216 | 0.186893 | 8.000000 | 0.943194 |
| night_context_rawctx_local_k8_a24 | 0.602675 | -0.010327 | 0.280443 | 0.186856 | 8.000000 | 0.907046 |
| night_mobility_rawctx_local_k8_a24 | 0.602767 | -0.010234 | 0.280535 | 0.186268 | 8.000000 | 0.923090 |
| night_usage_ambience_rawctx_local_k8_a24 | 0.603086 | -0.009915 | 0.280854 | 0.186553 | 8.000000 | 0.915763 |
| night_light_rawctx_local_k8_a24 | 0.603455 | -0.009547 | 0.281223 | 0.186470 | 8.000000 | 0.903855 |
| night_phone_rawctx_strict_k8_a24 | 0.605269 | -0.007733 | 0.283037 | 0.190842 | 8.000000 | 1.182683 |
| night_light_rawctx_strict_k8_a24 | 0.605873 | -0.007129 | 0.283640 | 0.190767 | 8.000000 | 1.042774 |
| night_watch_rawctx_strict_k8_a24 | 0.607025 | -0.005977 | 0.284793 | 0.192091 | 8.000000 | 1.073876 |
| night_coverage_rawctx_strict_k8_a24 | 0.607516 | -0.005486 | 0.285284 | 0.191898 | 8.000000 | 1.144479 |
| calendar_count_local | 0.607736 | -0.005266 | 0.285504 | 0.192483 |  |  |
| night_usage_ambience_rawctx_strict_k8_a24 | 0.607780 | -0.005222 | 0.285548 | 0.192908 | 8.000000 | 1.125502 |
| night_all_rawctx_strict_k8_a24 | 0.607966 | -0.005036 | 0.285734 | 0.193244 | 8.000000 | 1.183931 |
| night_context_rawctx_strict_k8_a24 | 0.608166 | -0.004835 | 0.285934 | 0.194195 | 8.000000 | 1.183574 |
| night_phone_rawctx_strict_k16_a24 | 0.608340 | -0.004662 | 0.286108 | 0.194108 | 16.000000 | 1.215917 |
| night_mobility_rawctx_strict_k8_a24 | 0.608937 | -0.004065 | 0.286705 | 0.193858 | 8.000000 | 1.227545 |

## View Geometry

| view | n_cols | row_dim | block_dim | anisotropy | effective_rank | hidden_nn_dist_median | hidden_nn_dist_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| night_mobility | 1180.000000 | 17.000000 | 124.000000 | 0.161822 | 31.652849 | 0.567842 | 1.372667 |
| night_context | 2692.000000 | 17.000000 | 124.000000 | 0.148202 | 31.358921 | 0.596802 | 0.921466 |
| night_light | 176.000000 | 17.000000 | 124.000000 | 0.144271 | 34.644463 | 0.606065 | 1.065230 |
| night_all | 3924.000000 | 17.000000 | 124.000000 | 0.155757 | 31.790338 | 0.639849 | 0.954587 |
| night_usage_ambience | 1512.000000 | 17.000000 | 124.000000 | 0.154152 | 33.139791 | 0.642842 | 0.905897 |
| night_coverage | 427.000000 | 9.000000 | 68.000000 | 0.183029 | 23.393361 | 0.659252 | 0.969815 |
| night_phone | 1231.000000 | 17.000000 | 124.000000 | 0.154143 | 34.727245 | 0.665462 | 0.939945 |
| night_watch | 873.000000 | 17.000000 | 124.000000 | 0.171476 | 35.124905 | 0.668528 | 0.873868 |

## Best Strict Target Detail

| target | target_row_logloss | delta_row_vs_subject | target_count_nll_per_row | delta_count_vs_subject |
| --- | --- | --- | --- | --- |
| Q1 | 0.638011 | -0.010726 | 0.300229 | -0.010726 |
| Q2 | 0.676538 | -0.017247 | 0.345263 | -0.017247 |
| Q3 | 0.653038 | -0.016308 | 0.311461 | -0.016308 |
| S1 | 0.567136 | -0.009910 | 0.251906 | -0.009910 |
| S2 | 0.560021 | -0.006878 | 0.260031 | -0.006878 |
| S3 | 0.510756 | 0.007802 | 0.228868 | 0.007802 |
| S4 | 0.631380 | -0.000865 | 0.283498 | -0.000865 |

## Hidden-Block Mixmin Alignment

| method | weighted_mixmin_delta_vs_a2c8 | mean_mixmin_delta_vs_a2c8 | mean_raw05_delta_vs_a2c8 | mixmin_better_block_rate | median_support | median_dist |
| --- | --- | --- | --- | --- | --- | --- |
| calendar_count_strict | -0.000179 | -0.000434 | 0.000841 | 0.527778 | 5.500000 |  |
| night_light_rawctx_strict_k8_a24 | 0.000153 | -0.000139 | 0.000768 | 0.500000 | 8.000000 | 1.008313 |
| night_coverage_rawctx_strict_k8_a24 | 0.000165 | -0.000129 | 0.000771 | 0.472222 | 8.000000 | 1.083946 |
| night_watch_rawctx_strict_k8_a24 | 0.000203 | -0.000181 | 0.000778 | 0.555556 | 8.000000 | 1.032081 |
| calendar_count_local | 0.000250 | -0.000095 | 0.000779 | 0.444444 | 6.000000 |  |
| night_light_rawctx_local_k8_a24 | 0.000259 | 0.000000 | 0.000742 | 0.472222 | 8.000000 | 0.888580 |
| night_phone_rawctx_local_k8_a24 | 0.000304 | 0.000049 | 0.000743 | 0.500000 | 8.000000 | 0.926834 |
| night_phone_rawctx_strict_k8_a24 | 0.000311 | 0.000034 | 0.000716 | 0.500000 | 8.000000 | 1.102409 |
| night_all_rawctx_local_k8_a24 | 0.000314 | 0.000015 | 0.000764 | 0.472222 | 8.000000 | 0.901272 |
| night_mobility_rawctx_local_k8_a24 | 0.000316 | 0.000073 | 0.000734 | 0.472222 | 8.000000 | 0.895865 |
| night_coverage_rawctx_local_k8_a24 | 0.000324 | 0.000012 | 0.000757 | 0.472222 | 8.000000 | 0.933820 |
| night_watch_rawctx_local_k8_a24 | 0.000327 | 0.000053 | 0.000743 | 0.472222 | 8.000000 | 0.887603 |
| night_usage_ambience_rawctx_local_k8_a24 | 0.000351 | 0.000071 | 0.000754 | 0.472222 | 8.000000 | 0.916811 |
| night_context_rawctx_local_k8_a24 | 0.000377 | 0.000135 | 0.000753 | 0.444444 | 8.000000 | 0.876900 |

## Decision

The best strict raw overnight method `night_phone_rawctx_strict_k8_a24` improves pseudo-hidden row LogLoss by `-0.007733`, so raw overnight context does recover a real held-out block-state signal.

But it fails the public/mixmin translation gate: its actual hidden-block weighted mixmin delta is `+0.000311`, while the strongest hidden alignment remains `calendar_count_strict` at `-0.000179`. Pseudo-hidden target regressions for the best strict method: `S3`.

This splits the world model: raw overnight context is a real strict representation, but it is not the same latent that produced mixmin's public edge. Treat it as a validation-mismatch/private-risk diagnostic, not as a submission source.

## Outputs

- `analysis_outputs/raw_overnight_block_context_probe_summary.csv`
- `analysis_outputs/raw_overnight_block_context_probe_target_detail.csv`
- `analysis_outputs/raw_overnight_block_context_probe_geometry.csv`
- `analysis_outputs/raw_overnight_block_context_probe_hidden_alignment.csv`
- `analysis_outputs/raw_overnight_block_context_probe_hidden_target_alignment.csv`
