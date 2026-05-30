# E207 LeJEPA Identifiability Conditions Audit

Purpose: turn the `When Does LeJEPA Learn a World Model?` reading into a precondition audit before training a larger JEPA. The audit scores whether a proposed positive-pair regime has the rough ingredients required for identifiable LeJEPA-style learning: intermediate autocorrelation, Gaussian-ish increments, non-collapsed rank, useful alignment gap, and some compatibility with known frontier movements.

This is not a submission generator. It is a regime selector for any future true-JEPA run.

## Decision Counts

```json
{'diagnostic_only': 56, 'energy_or_auxiliary': 20, 'true_jepa_candidate': 1}
```

## Best Regime/Latent Combinations

| latent | pair_regime | lejepa_readiness | decision | rho_abs_mean | alignment_ratio | increment_gauss_score | rank_fraction | frontier_smoothness | train_label_consistency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lejepa_l0p2_d32_pca48 | subject_lag2_all | 0.66853 | energy_or_auxiliary | 0.553658 | 0.476353 | 0.194814 | 1 | 0.450252 | 0.609233 |
| broad_stage2_pca64 | feature_nn1_all | 0.652939 | true_jepa_candidate | 0.49428 | 0.63602 | 0.435262 | 1 | 0.422099 | 0.594036 |
| lejepa_l0p05_d32_pca48 | subject_lag2_all | 0.651369 | energy_or_auxiliary | 0.53472 | 0.488817 | 0.182446 | 1 | 0.450252 | 0.609233 |
| block_canvas_pca48 | subject_lag1_train | 0.640868 | energy_or_auxiliary | 0.488816 | 0.677013 | 0.402125 | 1 | nan | 0.636039 |
| block_canvas_pca48 | subject_lag1_submission | 0.62746 | energy_or_auxiliary | 0.44903 | 0.672016 | 0.446385 | 1 | 0.447748 | nan |
| block_canvas_pca48 | subject_lag1_all | 0.621422 | energy_or_auxiliary | 0.465861 | 0.700623 | 0.404343 | 1 | 0.452199 | 0.635956 |
| broad_stage2_pca64 | feature_nn3_all | 0.607592 | energy_or_auxiliary | 0.388052 | 0.695021 | 0.496512 | 1 | 0.430905 | 0.573858 |
| neural_jepa_pca48 | feature_nn1_all | 0.585475 | energy_or_auxiliary | 0.259272 | 0.818313 | 0.717566 | 1 | 0.422099 | 0.594036 |
| jepa_group_pca48 | feature_nn1_all | 0.580372 | energy_or_auxiliary | 0.392409 | 0.717001 | 0.455639 | 1 | 0.422099 | 0.594036 |
| block_canvas_pca48 | subject_lag2_all | 0.556736 | energy_or_auxiliary | 0.361463 | 0.764008 | 0.43023 | 1 | 0.450252 | 0.609233 |
| rawijepa_pca48 | feature_nn1_all | 0.555438 | energy_or_auxiliary | 0.189843 | 0.857606 | 0.755895 | 1 | 0.422099 | 0.594036 |
| neural_jepa_pca48 | feature_nn3_all | 0.543716 | energy_or_auxiliary | 0.1907 | 0.850156 | 0.720541 | 1 | 0.430905 | 0.573858 |
| rawijepa_pca48 | feature_nn3_all | 0.541264 | energy_or_auxiliary | 0.13861 | 0.888042 | 0.796835 | 1 | 0.430905 | 0.573858 |
| jepa_group_pca48 | feature_nn3_all | 0.540581 | energy_or_auxiliary | 0.298041 | 0.758484 | 0.520947 | 1 | 0.430905 | 0.573858 |
| lejepa_l0p2_d32_pca48 | subject_lag4_all | 0.536654 | energy_or_auxiliary | 0.345548 | 0.696531 | 0.319215 | 1 | 0.449778 | 0.588938 |
| rawijepa_pca48 | train_target_manifold_neighbor | 0.533964 | energy_or_auxiliary | 0.164287 | 0.839744 | 0.64424 | 1 | nan | 0.991429 |
| rawijepa_pca48 | subject_lag1_submission | 0.530843 | energy_or_auxiliary | 0.145449 | 0.920839 | 0.776351 | 1 | 0.447748 | nan |
| block_canvas_pca48 | subject_lag4_all | 0.530069 | energy_or_auxiliary | 0.292434 | 0.811945 | 0.518971 | 1 | 0.449778 | 0.588938 |

## Best Latent Per Pair Regime

| latent | pair_regime | lejepa_readiness | decision | rho_abs_mean | alignment_ratio | increment_gauss_score | rank_fraction | frontier_smoothness | train_label_consistency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lejepa_l0p2_d32_pca48 | subject_lag2_all | 0.66853 | energy_or_auxiliary | 0.553658 | 0.476353 | 0.194814 | 1 | 0.450252 | 0.609233 |
| broad_stage2_pca64 | feature_nn1_all | 0.652939 | true_jepa_candidate | 0.49428 | 0.63602 | 0.435262 | 1 | 0.422099 | 0.594036 |
| block_canvas_pca48 | subject_lag1_train | 0.640868 | energy_or_auxiliary | 0.488816 | 0.677013 | 0.402125 | 1 | nan | 0.636039 |
| block_canvas_pca48 | subject_lag1_submission | 0.62746 | energy_or_auxiliary | 0.44903 | 0.672016 | 0.446385 | 1 | 0.447748 | nan |
| block_canvas_pca48 | subject_lag1_all | 0.621422 | energy_or_auxiliary | 0.465861 | 0.700623 | 0.404343 | 1 | 0.452199 | 0.635956 |
| broad_stage2_pca64 | feature_nn3_all | 0.607592 | energy_or_auxiliary | 0.388052 | 0.695021 | 0.496512 | 1 | 0.430905 | 0.573858 |
| lejepa_l0p2_d32_pca48 | subject_lag4_all | 0.536654 | energy_or_auxiliary | 0.345548 | 0.696531 | 0.319215 | 1 | 0.449778 | 0.588938 |
| rawijepa_pca48 | train_target_manifold_neighbor | 0.533964 | energy_or_auxiliary | 0.164287 | 0.839744 | 0.64424 | 1 | nan | 0.991429 |
| rawijepa_pca48 | subject_lag8_all | 0.509599 | diagnostic_only | 0.0890709 | 0.955144 | 0.784583 | 1 | 0.43438 | 0.58879 |
| rawijepa_pca48 | calendar_same_day_cross_subject | 0.501418 | diagnostic_only | 0.0413701 | 1.00188 | 0.804102 | 1 | 0.438144 | 0.550661 |
| rawijepa_pca48 | train_submission_subject_boundary | 0.498559 | diagnostic_only | 0.159178 | 0.90723 | 0.659375 | 1 | nan | nan |

## Interpretation

- `true_jepa_candidate` means the pair regime is plausible enough for a real context-to-target JEPA training attempt.
- `energy_or_auxiliary` means the structure is visible but should first be used as an energy/gate or diagnostic feature.
- `diagnostic_only` means a bigger JEPA would probably learn shortcuts, collapse, or a non-identifiable smooth feature under this regime.

Immediate rule: do not train a single JEPA over all pair types. Choose the top one or two regimes only, and treat same-family high-CV latents that fail this audit as gates rather than frontier submissions.
