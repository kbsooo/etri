# Fixed Deep Learning Golf Policy

## Result

- Best policy: `full_targetwise_upper_bound`
- Best OOF avg logloss: `0.623600`
- Drift vs v83: `0.068172`
- Best global source: `only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1`

## Policy Scores

| policy | avg_log_loss | macro_f1_at_0p5 | drift_vs_reference | fallback | n_overridden_targets | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_targetwise_upper_bound | 0.623600 | 0.709489 | 0.068172 | subject_prior | 7 | 0.670182 | 0.690139 | 0.672089 | 0.575339 | 0.578979 | 0.534719 | 0.643750 |
| nested_ge3_on_global | 0.624338 | 0.709841 | 0.066763 | only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 4 | 0.672390 | 0.690139 | 0.672089 | 0.575339 | 0.579893 | 0.534719 | 0.645794 |
| nested_ge3_on_prior | 0.624656 | 0.707727 | 0.064550 | subject_prior | 4 | 0.673179 | 0.690139 | 0.672089 | 0.575339 | 0.579856 | 0.534719 | 0.647272 |
| nested_ge4_on_global | 0.624790 | 0.708283 | 0.066469 | only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 3 | 0.672390 | 0.690139 | 0.675252 | 0.575339 | 0.579893 | 0.534719 | 0.645794 |
| nested_ge5_on_global | 0.625230 | 0.709144 | 0.067377 | only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 1 | 0.672390 | 0.690139 | 0.675252 | 0.576266 | 0.579893 | 0.536876 | 0.645794 |
| nested_ge4_on_prior | 0.625468 | 0.706170 | 0.063912 | subject_prior | 3 | 0.673179 | 0.690139 | 0.677770 | 0.575339 | 0.579856 | 0.534719 | 0.647272 |
| nested_ge5_on_prior | 0.625530 | 0.703385 | 0.062377 | subject_prior | 1 | 0.673179 | 0.690139 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| best_global | 0.626371 | 0.707657 | 0.067286 | only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0 | 0.672390 | 0.698126 | 0.675252 | 0.576266 | 0.579893 | 0.536876 | 0.645794 |

## Nested Count Maps

- ge5: `{'Q2': 'only_cross_modal__deviation__linear_k4_b0.2'}`
- ge4: `{'Q2': 'only_cross_modal__deviation__linear_k4_b0.2', 'S1': 'only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1', 'S3': 'only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1'}`
- ge3: `{'Q2': 'only_cross_modal__deviation__linear_k4_b0.2', 'Q3': 'only_rhythm__absolute_plus_deviation__mlp_h1_k1_wd0.1_b0.2', 'S1': 'only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1', 'S3': 'only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1'}`

## Best Policy Sources

| target | source |
| --- | --- |
| Q1 | only_rhythm__absolute__mlp_h1_k2_wd0.1_b0.2 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h1_k1_wd0.1_b0.2 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 |
| S3 | only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 |
| S4 | only_cross_modal__deviation__lowrank_r1_k4_wd0.1_b0.2 |

## Decision

This converts nested selection counts into fixed target rules. It is still an OOF policy comparison, but it avoids choosing each target source directly from full-train OOF losses.