# E185 Known-LB Pair Structural Decoder

## Question

E184 showed that a shallow cell-level public-anchor motif is not a reliable
pressure-branch selector. E185 asks whether a broader pair-level movement
representation, trained on all known public-LB submission pairs, can generalize
to an unseen submission and especially to frontier-scale pairs.

## Result In One Sentence

The best leave-one-file decoder is `shape_support_public_axis` with overall
accuracy `0.811`, frontier accuracy
`0.833`, and E95-edge-band accuracy
`0.714`, but its E95-edge reciprocity MAE
is `0.081`. The best
leave-one-pair decoder is `shape_support_public_axis` with E95-edge-band
accuracy `0.786` and reciprocity MAE
`0.146`. Treat pressure-branch
scores below as diagnostic unless file-LOO, edge-band stress, and reciprocal
orientation sanity are all strong.

## Known Public Files

| file | public_lb | note |
| --- | --- | --- |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | Current public frontier; validates E72-adverse hard-tail localization with E86-to-E85 fallback. |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | Resolved E95-relative Q2/S3 rollback sensor; small_loss versus E95 (+0.0000090362) but still beats mixmin (-0.0000062745); closes E108 and same-line automatic followups. |
| submission_mixmin_0c916bb4.csv | 0.576306641 | Previous public frontier; validates anchor-loss/binary-world mixmin sensor despite old selector veto. |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | E72/E73 sparse Q2/S3 gate sensor worsened versus mixmin; later audits show broad all-target contamination and sub-margin pure Q2/S3. |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.577439321 | Current public best supplied by user; missing from older observation table. |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | Raw timeline JEPA rescue current public control/best anchor. |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | Stage2 broad residual OOF gain mostly did not transfer to public; still slightly better than 0.578 anchor. |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | Ordinal Q2/Q3 nearest feasible-count correction improved OOF but missed public-best; strong CV-public overfit signal for this count shift. |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | Public anchor validated late fold-safe scale. |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | Direct JEPA latent Q2 movement failed public; bad-axis anchor. |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | LeJEPA target-wise strict scale0.5 improved OOF/geometry but failed public; new bad-axis anchor. |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | Direct latent residual probe failed public strongly; collapse/risk anchor. |

## Decoder Stress Summary

| feature_set | group_col | n_rows | n_groups | accuracy | auc | logloss | frontier_n | frontier_accuracy | frontier_auc | micro_n | micro_accuracy | e95_edge_n | e95_edge_accuracy | reciprocity_mae | frontier_reciprocity_mae | micro_reciprocity_mae | e95_edge_reciprocity_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_support_public_axis | file | 264 | 12 | 0.810606061 | 0.839015152 | 0.745759923 | 60 | 0.833333333 | 0.861111111 | 32 | 0.687500000 | 28 | 0.714285714 | 0.057468056 | 0.061205814 | 0.071345550 | 0.081044942 |
| shape_support | file | 264 | 12 | 0.803030303 | 0.835743802 | 0.740156120 | 60 | 0.800000000 | 0.828888889 | 32 | 0.656250000 | 28 | 0.678571429 | 0.050291643 | 0.043076534 | 0.045492954 | 0.051119716 |
| shape_only | file | 264 | 12 | 0.738636364 | 0.798611111 | 0.973656336 | 60 | 0.766666667 | 0.775555556 | 32 | 0.531250000 | 28 | 0.571428571 | 0.123096966 | 0.221658625 | 0.269749202 | 0.286172942 |
| shape_support_public_axis | pair | 132 | 66 | 0.931818182 | 0.965794307 | 0.257035698 | 30 | 0.866666667 | 0.915555556 | 16 | 0.687500000 | 14 | 0.785714286 | 0.051909462 | 0.079627763 | 0.147132126 | 0.146044396 |
| shape_only | pair | 132 | 66 | 0.924242424 | 0.957874197 | 0.495223438 | 30 | 0.866666667 | 0.908888889 | 16 | 0.687500000 | 14 | 0.785714286 | 0.104576434 | 0.171275822 | 0.274757269 | 0.286505022 |
| shape_support | pair | 132 | 66 | 0.909090909 | 0.960514233 | 0.240578669 | 30 | 0.800000000 | 0.862222222 | 16 | 0.625000000 | 14 | 0.714285714 | 0.038328627 | 0.017738221 | 0.040311547 | 0.022210471 |

## E95-Edge-Band File-LOO Predictions

| feature_set | heldout | new_file | base_file | actual_delta | prob_new_better | correct | frontier_pair | micro_pair | e95_edge_pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.641458999 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.365483915 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.338596250 | False | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.396923477 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 1.000000000 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 1.000000000 | False | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 1.000000000 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 1.000000000 | False | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.646949997 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.285216386 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.380847417 | False | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.404209640 | True | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.227935640 | False | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.039898627 | True | True | True | True |
| shape_only | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.453381725 | False | True | True | True |
| shape_only | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.323292936 | True | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.168378495 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.561176729 | False | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.594275162 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.220272216 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.740457503 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.278203390 | True | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.093796566 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.918174568 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.100313052 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.908879122 | False | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.757627070 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.241364166 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.920892482 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.086200257 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.881790121 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.192592467 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.001119509 | False | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.959319109 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.001357248 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.986593215 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.926684648 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.073433871 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.923143493 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.145943063 | True | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.172134049 | False | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.585118574 | False | True | True | True |
| shape_support | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.112040488 | False | True | True | True |
| shape_support | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.924142417 | False | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.785389680 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.189028221 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.924650124 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.078966893 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.949831393 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.049911920 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.582103084 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.523296069 | False | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.600390212 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.498096203 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.939833670 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.059053284 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.922477431 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.087604498 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.885768933 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.201162242 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.236217076 | False | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.999847933 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.243967822 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.999944087 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.925933411 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.072995913 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.924713684 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.150973746 | True | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.174029633 | False | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.590916991 | False | True | True | True |
| shape_support_public_axis | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.119750522 | False | True | True | True |
| shape_support_public_axis | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.929985627 | False | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.719694168 | True | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.139740506 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.899445469 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.058025006 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.949714659 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.050225583 | True | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.529300665 | True | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.467197363 | True | True | True | True |

## E95-Edge-Band Pair-LOO Predictions

| feature_set | heldout | new_file | base_file | actual_delta | prob_new_better | correct | frontier_pair | micro_pair | e95_edge_pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.674830816 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.323729597 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 1.000000000 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 1.000000000 | False | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.691142991 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.261423034 | True | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.407086069 | False | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.102779126 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.292650545 | False | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.264858090 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.753344664 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.265791186 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.771895613 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.223204817 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.940407332 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.067514400 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.002081041 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.984017998 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.967919238 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.032915518 | True | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.209886035 | False | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.690631017 | False | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.865390837 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.104572622 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.946350043 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.056912962 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.953711947 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.046254700 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.942045298 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.068270746 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.808007675 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.999991871 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.967956413 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.032281328 | True | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.213223137 | False | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.695334024 | False | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.816585949 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.074289825 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.946270494 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.056516364 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.953517598 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.046078888 | True | True | True | True |

## Pressure-Branch Scores

| feature_set | candidate | scenario_count | prefers_favorable_min_rate | prob_mean | prob_min | prob_max |
| --- | --- | --- | --- | --- | --- | --- |
| shape_only | e144 | 3 | 1.000000000 | 0.995942533 | 0.989584057 | 0.999203247 |
| shape_only | e154 | 3 | 1.000000000 | 0.998719216 | 0.998609334 | 0.998873698 |
| shape_only | e176 | 3 | 0.000000000 | 0.016896877 | 0.015316486 | 0.018046603 |
| shape_support | e144 | 3 | 0.333333333 | 0.407495117 | 0.243629612 | 0.546413412 |
| shape_support | e154 | 3 | 0.000000000 | 0.237556717 | 0.145649611 | 0.402250517 |
| shape_support | e176 | 3 | 1.000000000 | 0.977878062 | 0.969201628 | 0.986640902 |
| shape_support_public_axis | e144 | 3 | 0.666666667 | 0.534836925 | 0.357099397 | 0.671270640 |
| shape_support_public_axis | e154 | 3 | 0.333333333 | 0.366960555 | 0.251033610 | 0.570465979 |
| shape_support_public_axis | e176 | 3 | 1.000000000 | 0.961898485 | 0.947437197 | 0.976717040 |

## Pressure-Branch Detail

| feature_set | candidate | scenario | prob_pressure_min_public_better | prefers_favorable_min | n_diff_cells | top_targets | between_rate | e72_active_rate | e101_active_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | e144 | global_t010 | 0.999203247 | True | 185 | S2,Q1,Q3,Q1 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_only | e144 | global_t010_subject_t010 | 0.989584057 | True | 185 | Q1,Q1,Q1,Q3 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_only | e144 | global_t010_subject_t020 | 0.999040294 | True | 185 | S2,Q1,Q1,Q3 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_only | e154 | global_t010 | 0.998609334 | True | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_only | e154 | global_t010_subject_t010 | 0.998873698 | True | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_only | e154 | global_t010_subject_t020 | 0.998674616 | True | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_only | e176 | global_t010 | 0.015316486 | False | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_only | e176 | global_t010_subject_t010 | 0.017327542 | False | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_only | e176 | global_t010_subject_t020 | 0.018046603 | False | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_support | e144 | global_t010 | 0.546413412 | True | 185 | S2,Q1,Q3,Q1 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_support | e144 | global_t010_subject_t010 | 0.432442329 | False | 185 | Q1,Q1,Q1,Q3 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_support | e144 | global_t010_subject_t020 | 0.243629612 | False | 185 | S2,Q1,Q1,Q3 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_support | e154 | global_t010 | 0.145649611 | False | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_support | e154 | global_t010_subject_t010 | 0.402250517 | False | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_support | e154 | global_t010_subject_t020 | 0.164770023 | False | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_support | e176 | global_t010 | 0.977791656 | True | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_support | e176 | global_t010_subject_t010 | 0.986640902 | True | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_support | e176 | global_t010_subject_t020 | 0.969201628 | True | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_support_public_axis | e144 | global_t010 | 0.671270640 | True | 185 | S2,Q1,Q3,Q1 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_support_public_axis | e144 | global_t010_subject_t010 | 0.576140737 | True | 185 | Q1,Q1,Q1,Q3 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_support_public_axis | e144 | global_t010_subject_t020 | 0.357099397 | False | 185 | S2,Q1,Q1,Q3 | 0.497297297 | 0.237837838 | 0.021621622 |
| shape_support_public_axis | e154 | global_t010 | 0.251033610 | False | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_support_public_axis | e154 | global_t010_subject_t010 | 0.570465979 | True | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_support_public_axis | e154 | global_t010_subject_t020 | 0.279382075 | False | 294 | Q3,Q3,Q3,Q3 | 0.472789116 | 0.316326531 | 0.017006803 |
| shape_support_public_axis | e176 | global_t010 | 0.961541219 | True | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_support_public_axis | e176 | global_t010_subject_t010 | 0.976717040 | True | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |
| shape_support_public_axis | e176 | global_t010_subject_t020 | 0.947437197 | True | 904 | S1,Q3,Q3,Q3 | 0.819690265 | 0.268805310 | 0.011061947 |

## Interpretation

- Leave-one-file is the meaningful stress: a decoder that merely memorizes known
  file quality does not solve the next-submission problem.
- Frontier and E95-edge-band rows are the plateau regime. A model can look good
  on broad bad-vs-good public pairs and still be useless for E95/E101/mixmin
  branch choice.
- Reciprocal sanity matters: for one unordered pair, `P(A beats B) + P(B beats
  A)` should be close to `1`. Large errors are representation collapse, even
  when threshold accuracy looks acceptable.
- If branch preferences flip across feature sets, that is LeJEPA-style
  shortcut/collapse evidence, not a submission ranking signal.

## Decision

No submission is created. Use this audit to decide whether pair-level structural
movement is a real selector or only a coarse public-quality classifier.
