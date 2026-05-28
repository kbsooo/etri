# E73 Submission Candidate: E72 TopAbs50 Q2/S3 Gate

## Candidate

- File: `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`
- Source scan: `analysis_outputs/q2_s3_unified_gate_geometry_probe_scan.csv`
- Selection rule: best E72 deployable row sorted by all-combo delta, worst-set delta, and movement size.

## Local Evidence

| tag | pool | pool_size | pool_support_mean | base_agg | delta_agg | gate | alpha | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | hidden_q2_minus_base | hidden_s3_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | gate_active_q2s3 | gate_weight_q2s3_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e72_translator_tail_soft_p90_m0.50_top_abs50_16.00_4e48cba2 | translator_tail_soft_p90_m0.50 | 13 | 1.46154 | mean | signed_p75 | top_abs50 | 16 | -1.05458e-05 | -5.78026e-06 | 1.00163e-05 | 3 | 3 | -0.000391043 | -0.000487278 | -0.000294809 | -0.000280957 | -0.000159091 | 0.722222 | 1 | 0.00668422 | 0.00480356 | 0.158 | 0.158 |

## Hidden-World Hypothesis

This file bets that the deployable part of the Q2/S3 consensus is sparse-magnitude rather than sign-agreement based: `top_abs50` keeps only the strongest half of the unified Q2/S3 consensus movement and clears all strict local gates.

## Public LB Interpretation

- If public LB improves: E71's `gate=none` failure was mostly a gate-shape problem, and sparse top-magnitude Q2/S3 consensus is public-aligned.
- If public LB worsens: E72 is still overfitting local combo/hidden/world stress, and the next branch should require a stronger independent public-subset or structural block target before submission.

## Submission Order

Priority 1 diagnostic candidate after `submission_mixmin_0c916bb4.csv`; not a replacement until public observation confirms it.
