# E129 Transfer-shrinkage Pareto universe audit

## Question

E128 says transfer-shrinkage should remain disentangled into veto components.
E129 asks whether those components leave a novel, material, existing candidate
in the documented/local submission universe.

## Scan Scale

- candidate paths collected: `116044`
- unique prediction tensors loaded: `65865`
- duplicate tensors skipped: `50178`
- load/key mismatch skipped: `1`

## Gate Summary

| gate | count | known_public_count | same_family_count | novel_count | max_mean_abs_logit_vs_e95 | min_e72_exposure_e101_plausible |
| --- | --- | --- | --- | --- | --- | --- |
| gate_cos95_resid025 | 7 | 2.000000 | 7.000000 | 0.000000 | 0.000819 | 0.001496 |
| gate_active_q2s3_not_more_than_e101 | 7 | 2.000000 | 6.000000 | 1.000000 | 0.005992 | 0.001496 |
| gate_e72_not_more_than_e95 | 55 | 2.000000 | 5.000000 | 50.000000 | 0.013285 | 0.000000 |
| gate_strict_veto | 3 | 2.000000 | 3.000000 | 0.000000 | 0.000819 | 0.001496 |
| gate_relaxed_veto | 4 | 2.000000 | 4.000000 | 0.000000 | 0.000819 | 0.001496 |
| gate_material_vs_e95 | 65864 | 8.000000 | 1048.000000 | 64816.000000 | 0.541542 | 0.000000 |
| gate_strict_actionable | 2 | 1.000000 | 2.000000 | 0.000000 | 0.000819 | 0.001496 |
| gate_strict_novel_actionable | 0 | 0.000000 | 0.000000 | 0.000000 |  |  |
| raw_path_count | 116044 |  |  |  |  |  |
| loaded_unique | 65865 |  |  |  |  |  |
| skipped_load | 1 |  |  |  |  |  |
| duplicate_tensor | 50178 |  |  |  |  |  |

## Known Public Anchors

| file | public_delta_vs_e95 | tail_equal_law_cosine | tail_equal_law_resid_ratio | e101_active_delta95_l1 | q2s3_delta95_l1 | e72_adverse_exposure_e101_plausible | gate_strict_veto |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv | 0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.001557 | True |
| submission_e101_q2s3tail_177569bc.csv | 0.000009 | 1.000000 | 0.000000 | 0.010792 | 0.001079 | 0.001543 | True |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.000116 | 0.024468 | 1.946178 | 0.015921 | 0.003286 | 0.007634 | False |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.001148 | 0.684978 | 4.359945 | 0.036700 | 0.040400 | 0.010517 | False |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.002012 | 0.113117 | 18.274722 | 0.112066 | 0.080763 | 0.025203 | False |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.002136 | -0.128465 | 18.290761 | 0.175425 | 0.138603 | 0.046004 | False |
| submission_jepa_latent_q2_w0p45.csv | 0.003510 | 0.277091 | 13.056796 | 0.111541 | 0.149321 | 0.024872 | False |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.003955 | 0.296974 | 16.943922 | 0.077873 | 0.099436 | 0.021460 | False |
| submission_jepa_latent_residual_probe.csv | 0.004936 | 0.489869 | 16.052800 | 0.134525 | 0.145880 | 0.028773 | False |

## Strict Actionable Survivors

| file | same_family_name | tail_equal_law_cosine | tail_equal_law_resid_ratio | e101_active_delta95_l1 | q2s3_delta95_l1 | e72_adverse_exposure_e101_plausible | mean_abs_logit_move_vs_e95 | changed_cells_vs_e95 | gate_strict_actionable | gate_strict_novel_actionable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e85_inverse_conflict_pruned_58b23ed1.csv | True | 0.994651 | 0.157206 | 0.003562 | 0.000356 | 0.001496 | 0.000819 | 445 | True | False |
| submission_e101_q2s3tail_177569bc.csv | True | 1.000000 | 0.000000 | 0.010792 | 0.001079 | 0.001543 | 0.000308 | 50 | True | False |

## Relaxed Material Survivors

| file | same_family_name | tail_equal_law_cosine | tail_equal_law_resid_ratio | e101_active_delta95_l1 | q2s3_delta95_l1 | e72_adverse_exposure_e101_plausible | mean_abs_logit_move_vs_e95 | changed_cells_vs_e95 | gate_strict_actionable | gate_strict_novel_actionable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e85_inverse_conflict_pruned_58b23ed1.csv | True | 0.994651 | 0.157206 | 0.003562 | 0.000356 | 0.001496 | 0.000819 | 445 | True | False |
| submission_e101_q2s3tail_177569bc.csv | True | 1.000000 | 0.000000 | 0.010792 | 0.001079 | 0.001543 | 0.000308 | 50 | True | False |
| submission_e89_e72decontam_00d7807f.csv | True | 0.988304 | 0.154073 | 0.003562 | 0.000356 | 0.001686 | 0.000353 | 158 | False | False |

## Interpretation

- Strict veto means: tail-equal E95-law cosine >= `0.95`, residual <= `0.25`,
  active/Q2S3 rollback no larger than E101, and E101-compatible E72 exposure
  no larger than E95.
- Material means: at least E101-scale mean absolute logit movement vs E95.
- Novel means the filename is outside the current E85/E86/E87/E89/E90/E95/E101/E108
  same-family hardtail line.

Novel strict actionable survivors: `0`.

If this count is zero, the separated vetoes do not reveal a hidden old file.
They only recover already-known same-family conservative edits, so the next
step is new representation/movement rather than another existing-universe rank.

## Decision

No submission is generated by E129. Use this as a universe-level falsification
of "E128 vetoes already imply an existing next file."

## Outputs

- `e129_transfer_shrinkage_pareto_universe_full.csv` (local ignored full scan table)
- `e129_transfer_shrinkage_pareto_universe_gate_summary.csv`
- `e129_transfer_shrinkage_pareto_universe_shortlist_summary.csv`
