# E90 E89 Pareto-Knee Selector

## Observe

E89 minimized E72 contamination, but its selected cell fallback sacrifices part of E86's hidden/world/block edge.

## Wonder

Is there a strict row that remains cleaner than both E85 and no-Q2 while preserving more of E86's local structural strength than the minimum-contamination E89 file?

## Method

- Reuse the E89 strict/deployable scan.
- Keep only rows cleaner than both E85 and no-Q2 by E72 contamination index.
- Score a Pareto knee over margin retention, E72 decontamination, hidden/world retention, block/tail safety, and a small row-coherence bonus.
- Penalize projection-away rows because FH79 showed global projection is not the clean repair.

## Selected Row

| strategy | source | fallback | row_quantile | cell_quantile | pareto_score | margin_retention_vs_e86_e85 | decontam_gain_vs_e86_to_min | world_retention_vs_e86_e85 | hidden_retention_vs_e86_e85 | all_delta_vs_mixmin | e72_failed_contamination_index | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| row_e72_fallback | e86 | e85 | 0.9 |  | 0.749619 | 0.798048 | 0.589422 | 0.681272 | 0.518671 | -2.69324e-05 | 0.715784 | -0.000250999 | -0.000299838 | 0.777778 | 1 | e89_row_e72_fallback_28925de5 |

## Top Eligible Rows

| strategy | source | fallback | row_quantile | cell_quantile | pareto_score | margin_retention_vs_e86_e85 | decontam_gain_vs_e86_to_min | world_retention_vs_e86_e85 | hidden_retention_vs_e86_e85 | all_delta_vs_mixmin | e72_failed_contamination_index | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| row_e72_fallback | e86 | e85 | 0.9 |  | 0.749619 | 0.798048 | 0.589422 | 0.681272 | 0.518671 | -2.69324e-05 | 0.715784 | -0.000250999 | -0.000299838 | 0.777778 | 1 | e89_row_e72_fallback_28925de5 |
| row_e72_fallback | e86 | e85 | 0.8 |  | 0.697675 | 0.687317 | 0.84672 | 0.428855 | 0.205507 | -2.65083e-05 | 0.691079 | -0.000206302 | -0.000249254 | 0.722222 | 0.944444 | e89_row_e72_fallback_e6493417 |
| row_e72_q2_remove | e86 | q2_zero | 0.8 |  | 0.64151 | 0.851582 | 0.494735 | 0.408975 | 0.278712 | -2.71374e-05 | 0.724876 | -0.000202781 | -0.000261079 | 0.722222 | 0.944444 | e89_row_e72_q2_remove_6b4585f5 |
| row_e72_fallback | e86 | e85 | 0.7 |  | 0.616517 | 0.571255 | 0.8406 | 0.274501 | 0.0886391 | -2.60638e-05 | 0.691667 | -0.000178969 | -0.000230377 | 0.638889 | 0.944444 | e89_row_e72_fallback_7c2e4987 |
| row_e72_q2_remove | e86 | q2_zero | 0.7 |  | 0.612946 | 0.805303 | 0.553896 | 0.327297 | 0.171324 | -2.69602e-05 | 0.719195 | -0.000188318 | -0.000243733 | 0.638889 | 0.944444 | e89_row_e72_q2_remove_85f7ef06 |
| cell_e72_fallback | e86 | e85 |  | 0.9 | 0.60264 | 0.686205 | 0.842438 | 0.169803 | 0 | -2.6504e-05 | 0.69149 | -0.000160429 | -0.00021606 | 0.638889 | 0.944444 | e89_cell_e72_fallback_8e24187e |
| row_e72_q2_remove | e86 | q2_zero | 0.6 |  | 0.593826 | 0.781552 | 0.605445 | 0.197815 | 0.128605 | -2.68692e-05 | 0.714246 | -0.00016539 | -0.000236833 | 0.638889 | 0.944444 | e89_row_e72_q2_remove_ad12b148 |
| cell_e72_fallback | e86 | e85 |  | 0.8 | 0.589542 | 0.527442 | 1 | 0.056989 | 0 | -2.5896e-05 | 0.676361 | -0.000140452 | -0.00021606 | 0.638889 | 0.944444 | e89_cell_e72_fallback_00d7807f |
| row_e72_fallback | e86 | e85 | 0.6 |  | 0.560326 | 0.433062 | 0.906148 | 0.143555 | 0.0429523 | -2.55345e-05 | 0.685373 | -0.000155781 | -0.000222998 | 0.638889 | 0.944444 | e89_row_e72_fallback_3a92956a |
| cell_e72_fallback | e86 | e85 |  | 0.7 | 0.504493 | 0.412514 | 0.934895 | -0.0124588 | 0 | -2.54558e-05 | 0.682613 | -0.000128155 | -0.00021606 | 0.638889 | 0.944444 | e89_cell_e72_fallback_f0e327cd |
| project_away_e72 | e86 |  |  |  | 0.504 | 0.771254 | 0.458744 | 0.115023 | 0.432327 | -2.68298e-05 | 0.728332 | -0.000150729 | -0.000285892 | 0.777778 | 1 | e89_project_away_e72_3a962fb0 |
| project_away_e72 | e86 |  |  |  | 0.456781 | 0.555141 | 0.779611 | -0.444223 | 0.0869021 | -2.6002e-05 | 0.697523 | -5.16985e-05 | -0.000230097 | 0.777778 | 1 | e89_project_away_e72_3e43e09e |
| cell_e72_fallback | e86 | e85 |  | 0.6 | 0.439529 | 0.292961 | 0.842416 | -0.1145 | 0 | -2.49979e-05 | 0.691492 | -0.000110085 | -0.00021606 | 0.638889 | 0.944444 | e89_cell_e72_fallback_01dc4bf6 |

## Decision

Materialized Pareto-knee candidate: `submission_e90_e72pareto_28925de5.csv`.

This is not safer than E89 on contamination alone. It is a balanced public sensor: it tests whether public rewards preserving E86 row-level structural strength after removing the worst E72-contaminated rows.
