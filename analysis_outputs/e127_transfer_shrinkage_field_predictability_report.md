# E127 Transfer-shrinkage field predictability

## Question

E126 showed that E101-compatible public-loss budget is mostly outside the
cells E101 changed. E127 asks whether that post-feedback budget field was
visible before another probability move.

## Proxy Distribution Stress

| proxy_view | cosine | spearman | tv_distance | js_divergence | top50_overlap | truth_mass_in_pred_top50 | proxy_mass_on_e101_active | proxy_mass_on_q2s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| broad_tail_equal | 0.945388 | 0.902053 | 0.173650 | 0.038002 | 0.760000 | 0.293969 | 0.000000 | 0.169618 |
| broad_low_alpha | 0.780801 | 0.847148 | 0.329692 | 0.103608 | 0.540000 | 0.228487 | 0.120421 | 0.250406 |
| broad_all_or_top50 | 0.501985 | 0.836780 | 0.366029 | 0.144327 | 0.460000 | 0.194649 | 0.247347 | 0.374844 |
| broad | 0.410643 | 0.841784 | 0.443053 | 0.198225 | 0.480000 | 0.191863 | 0.354978 | 0.521544 |
| broad_q2s3 | 0.323754 | 0.108504 | 0.819487 | 0.508660 | 0.360000 | 0.170905 | 0.584840 | 1.000000 |

## Structural Metadata Predictability

| view | features | n_all_data_bins | cv_cosine | cv_spearman | cv_tv_distance | cv_js_divergence | cv_top50_overlap | cv_truth_mass_in_pred_top50 | all_js_divergence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target_context_tail_e72bin | target,context_type,e95_fallback_cell,e95_moved_vs_mixmin,e72_pos_bin | 95 | 0.818819 | 0.877137 | 0.270961 | 0.073253 | 0.560000 | 0.252521 | 0.058162 |
| target_tail | target,e95_fallback_cell,e95_moved_vs_mixmin | 13 | 0.687435 | 0.457974 | 0.496866 | 0.213619 | 0.420000 | 0.209990 | 0.207572 |
| target_context_tail | target,context_type,e95_fallback_cell,e95_moved_vs_mixmin | 26 | 0.670384 | 0.446737 | 0.506166 | 0.220395 | 0.440000 | 0.212335 | 0.206682 |
| subject_target | subject_id,target | 70 | 0.432920 | 0.343937 | 0.607028 | 0.301099 | 0.040000 | 0.041933 | 0.265795 |
| target | target | 7 | 0.425300 | 0.256766 | 0.641914 | 0.316796 | 0.000000 | 0.037897 | 0.310201 |
| target_context | target,context_type | 14 | 0.410126 | 0.227360 | 0.647762 | 0.322138 | 0.040000 | 0.042658 | 0.309268 |
| target_position | target,pos_bin | 35 | 0.407751 | 0.235157 | 0.650345 | 0.322216 | 0.040000 | 0.025564 | 0.303177 |
| target_context_position | target,context_type,pos_bin | 63 | 0.377974 | 0.215740 | 0.661810 | 0.332605 | 0.020000 | 0.021259 | 0.300057 |
| subject_context_target | subject_id,context_type,target | 140 | 0.400521 | 0.092551 | 0.662749 | 0.336646 | 0.100000 | 0.042751 | 0.248426 |
| blocklen_context_target | block_len_bin,context_type,target | 56 | 0.360628 | 0.194189 | 0.670326 | 0.340956 | 0.020000 | 0.015236 | 0.300511 |
| constant | constant | 1 | 0.394217 | -0.053337 | 0.680333 | 0.347749 | 0.080000 | 0.030754 | 0.345991 |

## Top E101-compatible Budget Cells

| cell_idx | target | subject_id | hidden_block_id | context_type | pos_bin | e101_plausible_share | broad_tail_equal_share | broad_low_alpha_share | target_is_q2s3 | e101_active | e95_fallback_cell | e72_pos_bin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 449 | Q2 | id03 | id03_b2 | between_train_runs | interior | 0.020442 | 0.018931 | 0.009998 | True | False | True | p05_high |
| 1618 | Q2 | id10 | id10_b2 | between_train_runs | interior | 0.010177 | 0.010452 | 0.006109 | True | False | True | p05_high |
| 1212 | Q2 | id07 | id07_b4 | after_train_run | interior | 0.009706 | 0.012817 | 0.005509 | True | False | True | p05_high |
| 1695 | Q2 | id10 | id10_b4 | after_train_run | interior | 0.008827 | 0.006799 | 0.004721 | True | False | True | p05_high |
| 1730 | Q2 | id10 | id10_b4 | after_train_run | interior | 0.008787 | 0.005801 | 0.004138 | True | False | True | p05_high |
| 967 | Q2 | id06 | id06_b4 | between_train_runs | interior | 0.008262 | 0.008486 | 0.003781 | True | False | True | p05_high |
| 1513 | Q2 | id09 | id09_b4 | after_train_run | near_edge | 0.008020 | 0.006177 | 0.004390 | True | False | True | p05_high |
| 1310 | Q2 | id08 | id08_b4 | between_train_runs | interior | 0.007900 | 0.012170 | 0.007683 | True | False | True | p05_high |
| 1226 | Q2 | id07 | id07_b4 | after_train_run | interior | 0.007652 | 0.009788 | 0.005438 | True | False | True | p05_high |
| 1303 | Q2 | id08 | id08_b4 | between_train_runs | interior | 0.007414 | 0.011352 | 0.006332 | True | False | True | p05_high |
| 1639 | Q2 | id10 | id10_b2 | between_train_runs | interior | 0.007038 | 0.003614 | 0.005157 | True | False | True | p05_high |
| 911 | Q2 | id06 | id06_b2 | between_train_runs | interior | 0.006731 | 0.006926 | 0.004040 | True | False | True | p05_high |
| 1242 | S1 | id07 | id07_b4 | after_train_run | interior | 0.006694 | 0.007734 | 0.002813 | False | False | True | p05_high |
| 1191 | Q2 | id07 | id07_b4 | after_train_run | interior | 0.006648 | 0.008194 | 0.004676 | True | False | True | p05_high |
| 731 | S1 | id04 | id04_b14 | after_train_run | left_edge | 0.006627 | 0.005105 | 0.003553 | False | False | True | p05_high |
| 627 | S2 | id04 | id04_b6 | between_train_runs | interior | 0.006570 | 0.005783 | 0.003729 | False | False | True | p05_high |
| 1158 | S1 | id07 | id07_b2 | between_train_runs | near_edge | 0.006569 | 0.007229 | 0.002438 | False | False | False | p05_high |
| 1117 | S2 | id07 | id07_b2 | between_train_runs | interior | 0.006408 | 0.005641 | 0.003918 | False | False | False | p05_high |
| 1002 | Q2 | id06 | id06_b8 | between_train_runs | near_edge | 0.006296 | 0.004850 | 0.004816 | True | False | True | p05_high |
| 1131 | S2 | id07 | id07_b2 | between_train_runs | interior | 0.006260 | 0.005511 | 0.004241 | False | False | True | p05_high |

## Interpretation

- Best public-free scenario proxy: `broad_tail_equal` with JS `0.038002`, TV `0.173650`, and top50 truth-mass capture `0.293969`.
- The rejected q2s3 proxy has JS `0.508660` and top50 truth-mass capture `0.170905`.
- Best hidden-block-heldout metadata view: `target_context_tail_e72bin` with CV JS `0.073253` and top50 truth-mass capture `0.252521`.
- Target-only heldout view has CV JS `0.316796`.

The transfer-shrinkage field is not arbitrary: scenario-level tail-neutral /
low-alpha proxies see it better than q2s3. But structural metadata alone is only
a weak action sensor under hidden-block holdout. This supports the E126 world
model as an explanation and a negative gate, while rejecting a direct metadata
gate as the next submission generator.

## Decision

No submission. The next useful branch should build a public-free
tail-neutral/low-alpha transfer-shrinkage representation, then test whether it
creates probability movement larger than selector noise without reintroducing
E72/E101 active-cell tail risk.
