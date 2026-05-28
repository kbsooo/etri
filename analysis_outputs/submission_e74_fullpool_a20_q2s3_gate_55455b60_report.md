# E74 Submission Candidate: Full-Pool Alpha20 Sparse Q2/S3 Gate

## Candidate

- File: `analysis_outputs/submission_e74_fullpool_a20_q2s3_gate_55455b60.csv`
- Source scan: `analysis_outputs/q2_s3_sparse_gate_stability_probe_scan.csv`
- Selection rule: the E74 reference/full_pool row at alpha20. This keeps the exact E73 13-cell source pool and changes only amplitude from 16 to 20.

## Local Evidence

| tag | variant_kind | variant_name | pool | pool_size | pool_support_mean | pool_support2_count | base_agg | delta_agg | gate | alpha | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | hidden_q2_minus_base | hidden_s3_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | mean_abs_q2s3_logit_delta_vs_e73 | q2s3_topabs_jaccard_vs_e73 | gate_active_q2s3 | gate_weight_q2s3_mean | strict_gate | deployable_gate | loose_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e74_full_pool_20.00_55455b60 | reference | full_pool | translator_tail_soft_p90_m0.50 | 13 | 1.46154 | 6 | mean | signed_p75 | top_abs50 | 20 | -1.07261e-05 | -5.96055e-06 | 1.10367e-05 | 3 | 3 | -0.000484506 | -0.000604704 | -0.000364309 | -0.000351115 | -0.000197636 | 0.722222 | 1 | 0.00702733 | 0.00600445 | 0.00120089 | 1 | 0.158 | 0.158 | True | True | True |

## Hidden-World Hypothesis

This file bets that E73's sparse-magnitude Q2/S3 gate was directionally right but conservative: the same full-pool latent movement has a shallow amplitude ridge around alpha20 before alpha24 breaks strict consensus.

## Public LB Interpretation

- If public LB improves over E73: sparse Q2/S3 structure is public-aligned and the bottleneck is under-amplitude rather than gate selection.
- If public LB worsens while E73 improves or holds: the gate shape is real but the amplitude ridge is a local-stress illusion; keep E73 and require stronger public-like amplitude calibration.
- If both E73 and this file worsen: E74 stability is local-only, and sparse Q2/S3 movements should be demoted behind a different hidden-world branch.

## Submission Order

Secondary diagnostic after E73. It is higher-upside but higher-risk because alpha24 already fails strict consensus.
