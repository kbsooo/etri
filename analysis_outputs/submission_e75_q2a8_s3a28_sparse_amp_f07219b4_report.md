# E75 Submission Candidate: Q2-Low/S3-High Sparse Amplitude Ridge

## Candidate

- File: `analysis_outputs/submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv`
- Source scan: `analysis_outputs/q2_s3_target_amplitude_ridge_probe_scan.csv`
- Selection rule: best E75 deployable row by all-combo delta, then worst-set delta and distance from E74.

## Local Evidence

| tag | dominant_axis | pool | pool_size | pool_support_mean | pool_support2_count | base_agg | delta_agg | gate | alpha_q2 | alpha_s3 | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | hidden_q2_minus_base | hidden_s3_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | mean_abs_q2s3_logit_delta_vs_e73 | mean_abs_q2s3_logit_delta_vs_e74 | strict_gate | deployable_gate | loose_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e75_q2a8.0_s3a28.0_f07219b4 | s3_higher | translator_tail_soft_p90_m0.50 | 13 | 1.46154 | 6 | mean | signed_p75 | top_abs50 | 8 | 28 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000247148 | -0.000498235 | -0.000200351 | -0.000122508 | 0.722222 | 1 | 0.00694104 | 0.00570243 | 0.00306191 | 0.00294254 | True | True | True |

## Hidden-World Hypothesis

This file bets that E73/E74 found the right sparse Q2/S3 gate but used the wrong target amplitude: Q2 should be shrunk while S3 should be expanded. The public-sensitive component is S3-heavy, while Q2 contributes more hidden/world support than public-combo edge.

## Public LB Interpretation

- If public LB improves over E73/E74: the sparse gate is real and public amplitude is target-asymmetric, with S3 carrying the readable public signal.
- If E73 improves but this worsens: sparse-gate sign is real but S3-high/Q2-low amplitude is local combo overfit.
- If this improves while E73/E74 do not: target-specific amplitude was the missing object, and future gates should separate Q2 hidden/world support from S3 public-combo support.

## Submission Order

High-information follow-up after E73. It may outrank E74 as a second sensor because it tests a sharper target-asymmetry hypothesis, but it is more aggressive than E73.
