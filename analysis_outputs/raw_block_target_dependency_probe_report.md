# E55 Raw Block Target-Dependency Probe

## Observe

E54 showed a split world: raw overnight context is a real strict block-state representation, but its best strict method regresses S3 and produces an adverse actual hidden mixmin sign.

## Wonder

If S3 and mixmin sign are target-manifold failures rather than raw-context failures, can other predicted target rates project each block back onto a train block-rate dependency manifold and repair both?

## Hypothesis

H55: a strict target-dependency/count projection should keep the raw overnight block-state gain, fix the S3 pseudo-hidden regression, and make actual hidden-block rates prefer mixmin rather than a2c8.

## Method

- Pseudo-hidden blocks: `369`; actual hidden blocks: `36`.
- Base: `night_phone_rawctx_strict_k8_a24` from E54.
- Context for projection: other target rates only, using strict subject-excluded donor blocks. Donor contexts use true donor block rates; query contexts use raw predicted block rates.
- Estimators: kNN target-rate manifold and Ridge logit-rate projection.
- Masks: S3 only, S2/S3, S-stage group, and all targets.
- Stress: pseudo-hidden row/count LogLoss, S3 target recovery, train-rate manifold energy, and actual hidden-block expected mixmin delta versus a2c8.

## Baseline Raw State

| method | weighted_row_logloss | delta_weighted_row_logloss_vs_subject | delta_weighted_row_logloss_vs_raw | s3_delta_vs_subject | weighted_mixmin_delta_vs_a2c8 | joint_gate |
| --- | --- | --- | --- | --- | --- | --- |
| raw_phone_base | 0.605269 | -0.007733 | 0.000000 | 0.007802 | 0.000311 | 0.000000 |
| subject_mean | 0.613002 | 0.000000 | 0.007733 | 0.000000 | 0.000445 | 0.000000 |
| calendar_count_strict | 0.614436 | 0.001434 | 0.009167 | 0.034293 | -0.000179 | 0.000000 |

## Top Pseudo-Hidden Methods

| method | weighted_row_logloss | delta_weighted_row_logloss_vs_raw | s3_delta_vs_subject | s3_delta_vs_raw | weighted_mixmin_delta_vs_a2c8 | energy_delta_vs_raw | joint_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| raw_phone_s3_subject_w1p00 | 0.604154 | -0.001115 | 0.000000 | -0.007802 | 0.000319 | 0.141534 | 0.000000 |
| raw_phone_s3_subject_w0p50 | 0.604203 | -0.001065 | 0.000345 | -0.007457 | 0.000315 | 0.061998 | 0.000000 |
| raw_phone_td_knn_groupcross_stage_k8_a24_w0.25 | 0.605150 | -0.000118 | 0.007219 | -0.000583 | 0.000317 | 0.011250 | 0.000000 |
| raw_phone_td_knn_groupcross_s3_k8_a24_w0.25 | 0.605185 | -0.000083 | 0.007219 | -0.000583 | 0.000299 | -0.001077 | 0.000000 |
| raw_phone_td_knn_groupcross_s3_k8_a24_w0.50 | 0.605189 | -0.000080 | 0.007245 | -0.000558 | 0.000287 | 0.000240 | 0.000000 |
| raw_phone_td_knn_groupcross_s2s3_k8_a24_w0.25 | 0.605203 | -0.000066 | 0.007219 | -0.000583 | 0.000315 | 0.001964 | 0.000000 |
| raw_phone_td_knn_pair_s3_k8_a24_w0.25 | 0.605233 | -0.000036 | 0.007553 | -0.000249 | 0.000315 | -0.002484 | 0.000000 |
| raw_phone_td_knn_pair_stage_k8_a24_w0.25 | 0.605242 | -0.000026 | 0.007553 | -0.000249 | 0.000316 | 0.004617 | 0.000000 |
| raw_phone_td_knn_pair_s2s3_k8_a24_w0.25 | 0.605251 | -0.000018 | 0.007553 | -0.000249 | 0.000331 | 0.000593 | 0.000000 |
| raw_phone_base | 0.605269 | 0.000000 | 0.007802 | 0.000000 | 0.000311 | 0.000000 | 0.000000 |
| raw_phone_td_knn_groupcross_s2s3_k8_a24_w0.50 | 0.605275 | 0.000007 | 0.007245 | -0.000558 | 0.000320 | 0.007751 | 0.000000 |
| raw_phone_td_knn_pair_s3_k8_a24_w0.50 | 0.605278 | 0.000009 | 0.007867 | 0.000064 | 0.000319 | -0.003282 | 0.000000 |
| raw_phone_td_knn_allcross_s3_k8_a24_w0.25 | 0.605281 | 0.000012 | 0.007886 | 0.000084 | 0.000297 | -0.003521 | 0.000000 |
| raw_phone_td_knn_allcross_s2s3_k8_a24_w0.25 | 0.605282 | 0.000014 | 0.007886 | 0.000084 | 0.000306 | -0.001156 | 0.000000 |
| raw_phone_td_knn_groupcross_s3_k8_a24_w0.75 | 0.605284 | 0.000015 | 0.007908 | 0.000106 | 0.000275 | 0.003950 | 0.000000 |
| raw_phone_td_knn_groupcross_stage_k8_a24_w0.50 | 0.605301 | 0.000033 | 0.007245 | -0.000558 | 0.000323 | 0.029360 | 0.000000 |

## S3-Fixed Methods

| method | weighted_row_logloss | delta_weighted_row_logloss_vs_raw | s3_delta_vs_subject | weighted_mixmin_delta_vs_a2c8 | joint_gate |
| --- | --- | --- | --- | --- | --- |
| raw_phone_s3_subject_w1p00 | 0.604154 | -0.001115 | 0.000000 | 0.000319 | 0.000000 |
| subject_mean | 0.613002 | 0.007733 | 0.000000 | 0.000445 | 0.000000 |

## Best Hidden Mixmin Alignment

| method | weighted_row_logloss | delta_weighted_row_logloss_vs_raw | s3_delta_vs_subject | weighted_mixmin_delta_vs_a2c8 | mixmin_better_block_rate | joint_gate |
| --- | --- | --- | --- | --- | --- | --- |
| raw_phone_td_ridge_groupcross_all_k0_a8_w0.75 | 0.727319 | 0.122051 | 0.207892 | -0.000414 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_groupcross_all_k0_a2_w0.75 | 0.726606 | 0.121337 | 0.205821 | -0.000407 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_pair_all_k0_a8_w0.75 | 0.737054 | 0.131785 | 0.201414 | -0.000363 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_pair_all_k0_a2_w0.75 | 0.736452 | 0.131184 | 0.199174 | -0.000350 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_groupcross_s2s3_k0_a8_w0.75 | 0.638214 | 0.032945 | 0.207892 | -0.000247 | 0.527778 | 0.000000 |
| raw_phone_td_ridge_groupcross_s2s3_k0_a2_w0.75 | 0.637606 | 0.032338 | 0.205821 | -0.000240 | 0.555556 | 0.000000 |
| raw_phone_td_ridge_pair_s2s3_k0_a8_w0.75 | 0.637288 | 0.032020 | 0.201414 | -0.000200 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_pair_s2s3_k0_a2_w0.75 | 0.636657 | 0.031388 | 0.199174 | -0.000187 | 0.500000 | 0.000000 |
| calendar_count_strict | 0.614436 | 0.009167 | 0.034293 | -0.000179 | 0.527778 | 0.000000 |
| raw_phone_td_ridge_groupcross_all_k0_a8_w0.50 | 0.662182 | 0.056913 | 0.113545 | -0.000173 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_groupcross_all_k0_a2_w0.50 | 0.661863 | 0.056594 | 0.112683 | -0.000168 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_pair_all_k0_a8_w0.50 | 0.666312 | 0.061043 | 0.110194 | -0.000139 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_pair_all_k0_a2_w0.50 | 0.666036 | 0.060767 | 0.109215 | -0.000130 | 0.500000 | 0.000000 |
| raw_phone_td_ridge_groupcross_stage_k0_a8_w0.75 | 0.662546 | 0.057278 | 0.207892 | -0.000093 | 0.527778 | 0.000000 |
| raw_phone_td_ridge_groupcross_stage_k0_a2_w0.75 | 0.661721 | 0.056453 | 0.205821 | -0.000086 | 0.527778 | 0.000000 |
| raw_phone_td_ridge_groupcross_s2s3_k0_a8_w0.50 | 0.622408 | 0.017139 | 0.113545 | -0.000061 | 0.500000 | 0.000000 |

## Decision

No target-dependency projection passed the joint gate. The projection can improve one axis at a time, but not all three requirements together: preserve raw pseudo-hidden recovery, fix S3, and make hidden mixmin sign negative.

Raw base pseudo-hidden delta vs subject is `-0.007733`, S3 delta is `+0.007802`, and hidden mixmin delta is `+0.000311`.
The best pseudo-hidden method is `raw_phone_s3_subject_w1p00` with raw delta `-0.001115` and hidden mixmin delta `+0.000319`.
The best hidden mixmin alignment is `raw_phone_td_ridge_groupcross_all_k0_a8_w0.75` at `-0.000414`.

This weakens the idea that a simple target-dependency count manifold can translate the raw overnight latent into the mixmin-public latent. The remaining branch is a hard mixmin-constrained world model or a more structural target representation, not a post-hoc target projection.

## Outputs

- `analysis_outputs/raw_block_target_dependency_probe_summary.csv`
- `analysis_outputs/raw_block_target_dependency_probe_target_detail.csv`
- `analysis_outputs/raw_block_target_dependency_probe_hidden_alignment.csv`
- `analysis_outputs/raw_block_target_dependency_probe_hidden_target_alignment.csv`
- `analysis_outputs/raw_block_target_dependency_probe_method_detail.csv`
