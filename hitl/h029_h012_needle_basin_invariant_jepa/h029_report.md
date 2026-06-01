# H029 H012 Needle-Basin Invariant HS-JEPA

## Question

H012 beat the old frontier by a large margin, but H028 showed that local public-gradient continuation is unsafe. H029 asks which invariant makes H012 special: exact support, amplitude, target/subject block, same-subject memory agreement, or row identity.

## External Reference Integrated

The attached high-scoring document argues for same-subject temporal label memory conditioned by sleep-state and sensor-quality similarity. H029 uses that idea as a falsification view via H014 memory agreement/disagreement slices rather than replacing H012.

## Generated Variants

- generated variants: `102`
- best H024 decoder in this pool: `geometry` alpha `100.0`, MAE `0.000772855`, Spearman `0.969924812`, pairwise `0.947368421`

## Family Summary

| family | n | best_candidate_id | best_pred_public_median | best_margin_vs_h012 | best_margin_vs_duplicate | best_support_better_than_h012 | best_risk_width | median_pred_public |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target_rollback | 7 | rollback_target_S1 | 0.570494744 | 0.002371261 | -0.001154236 | 0.116666667 | 0.005961265 | 0.571925896 |
| posterior_topk | 27 | posterior_top_k1200_a0p7 | 0.570594161 | 0.002470677 | -0.001054820 | 0.166666667 | 0.016391840 | 0.573458980 |
| subject_rollback | 10 | rollback_subject_id03 | 0.570924706 | 0.002801223 | -0.000724274 | 0.083333333 | 0.005154202 | 0.571878690 |
| memory_rollback | 12 | rollback_private_safe_k250 | 0.572914561 | 0.004791078 | 0.001265581 | 0.033333333 | 0.005353538 | 0.574001575 |
| support_ray_scale | 10 | support_ray_scale_0p35 | 0.574090473 | 0.005966990 | 0.002441492 | 0.100000000 | 0.005850707 | 0.572687700 |
| memory_only | 12 | only_memory_agree_k500 | 0.574397528 | 0.006274045 | 0.002748548 | 0.016666667 | 0.005422146 | 0.574455941 |
| target_group_only | 2 | only_group_Q | 0.574948706 | 0.006825223 | 0.003299726 | 0.000000000 | 0.001929719 | 0.573657850 |
| target_group_rollback | 2 | rollback_group_S | 0.574948706 | 0.006825223 | 0.003299726 | 0.000000000 | 0.001929719 | 0.573657850 |
| target_only | 7 | only_target_S3 | 0.575182850 | 0.007059367 | 0.003533870 | 0.000000000 | 0.001706357 | 0.575352400 |
| outside_support_matched | 1 | outside_support_targetcount_matched_top | 0.576720646 | 0.008597163 | 0.005071666 | 0.000000000 | 0.001483838 | 0.576720646 |
| targetwise_rowperm | 12 | targetwise_rowperm_seed05 | 0.581149687 | 0.013026204 | 0.009500707 | 0.000000000 | 0.007740172 | 0.582127527 |

## Top Variants

| candidate_id | family | pred_public_median | pred_public_p10 | pred_public_p90 | margin_vs_h012_pred | margin_vs_h012_duplicate_pred | support_better_than_h012 | changed_cells_vs_h012 | max_abs_prob_vs_h012 | posterior_delta_vs_h012 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rollback_target_S1 | target_rollback | 0.570494744 | 0.567600462 | 0.573561727 | 0.002371261 | -0.001154236 | 0.116666667 | 194 | 0.151541620 | 0.001455183 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_target_S1_d403217e.csv |
| rollback_subject_id03 | subject_rollback | 0.570924706 | 0.569489427 | 0.574643630 | 0.002801223 | -0.000724274 | 0.083333333 | 116 | 0.189622758 | 0.000896144 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_subject_id03_5317b18e.csv |
| rollback_target_Q1 | target_rollback | 0.570588750 | 0.568545119 | 0.574756302 | 0.002465267 | -0.001060230 | 0.100000000 | 167 | 0.189622758 | 0.000980804 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_target_Q1_97cb1b14.csv |
| rollback_subject_id06 | subject_rollback | 0.569945731 | 0.563433497 | 0.571860194 | 0.001822248 | -0.001703249 | 0.183333333 | 148 | 0.132271428 | 0.001526360 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_subject_id06_7a3a0e84.csv |
| rollback_subject_id04 | subject_rollback | 0.570686075 | 0.568417263 | 0.574900452 | 0.002562592 | -0.000962905 | 0.100000000 | 115 | 0.226229643 | 0.000826610 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_subject_id04_0971487c.csv |
| rollback_subject_id02 | subject_rollback | 0.571587807 | 0.569554885 | 0.575716967 | 0.003464324 | -0.000061173 | 0.083333333 | 162 | 0.181008177 | 0.001133288 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_subject_id02_e64984d5.csv |
| rollback_target_S2 | target_rollback | 0.571977511 | 0.568800639 | 0.575831952 | 0.003854028 | 0.000328531 | 0.083333333 | 207 | 0.116332594 | 0.001561680 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_target_S2_ea8b6c0e.csv |
| rollback_private_safe_k250 | memory_rollback | 0.572914561 | 0.569115813 | 0.574469351 | 0.004791078 | 0.001265581 | 0.033333333 | 250 | 0.294110279 | 0.005067567 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_private_safe_k250_8899870f.csv |
| rollback_private_safe_k100 | memory_rollback | 0.571761535 | 0.564723288 | 0.573538741 | 0.003638052 | 0.000112554 | 0.283333333 | 100 | 0.294110279 | 0.003392175 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_private_safe_k100_cc13a85f.csv |
| rollback_memory_disagree_k100 | memory_rollback | 0.571612033 | 0.563833245 | 0.573518031 | 0.003488550 | -0.000036948 | 0.283333333 | 100 | 0.189622758 | 0.003087026 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_memory_disagree_k100_f80891bd.csv |
| rollback_private_safe_k500 | memory_rollback | 0.574268701 | 0.572108336 | 0.575345635 | 0.006145218 | 0.002619721 | 0.000000000 | 500 | 0.294110279 | 0.006257488 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_private_safe_k500_06273fe1.csv |
| rollback_memory_disagree_k250 | memory_rollback | 0.572838873 | 0.566972907 | 0.574465274 | 0.004715390 | 0.001189893 | 0.216666667 | 250 | 0.189622758 | 0.004358627 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_memory_disagree_k250_e5e518c8.csv |
| only_group_Q | target_group_only | 0.574948706 | 0.573938363 | 0.575868082 | 0.006825223 | 0.003299726 | 0.000000000 | 787 | 0.151541620 | 0.004809045 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_only_group_Q_d13929ef.csv |
| rollback_group_S | target_group_rollback | 0.574948706 | 0.573938363 | 0.575868082 | 0.006825223 | 0.003299726 | 0.000000000 | 787 | 0.151541620 | 0.004809045 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_group_S_d13929ef.csv |
| only_target_S3 | target_only | 0.575182850 | 0.573970081 | 0.575676438 | 0.007059367 | 0.003533870 | 0.000000000 | 1006 | 0.294110279 | 0.006313760 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_only_target_S3_dd923897.csv |
| rollback_memory_disagree_k500 | memory_rollback | 0.573931334 | 0.569490430 | 0.575218329 | 0.005807851 | 0.002282354 | 0.033333333 | 500 | 0.189622758 | 0.005007720 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_memory_disagree_k500_817b802f.csv |
| only_target_S4 | target_only | 0.575352400 | 0.574689962 | 0.576505886 | 0.007228917 | 0.003703420 | 0.000000000 | 1008 | 0.294110279 | 0.006220671 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_only_target_S4_dfc97a80.csv |
| rollback_private_safe_k750 | memory_rollback | 0.575242852 | 0.573515359 | 0.576061089 | 0.007119369 | 0.003593872 | 0.000000000 | 750 | 0.294110279 | 0.006806339 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_rollback_private_safe_k750_d3f9457c.csv |
| support_ray_scale_0p35 | support_ray_scale | 0.574090473 | 0.570993429 | 0.576844136 | 0.005966990 | 0.002441492 | 0.100000000 | 1200 | 0.191293379 | 0.002898894 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_support_ray_scale_0p35_1d644065.csv |
| support_ray_scale_0p5 | support_ray_scale | 0.573362769 | 0.568732336 | 0.576844136 | 0.005239286 | 0.001713789 | 0.100000000 | 1200 | 0.145845202 | 0.001938497 | hitl/h029_h012_needle_basin_invariant_jepa/submission_h029_support_ray_scale_0p5_25382853.csv |

## Selected Stress

- selected diagnostic: `rollback_target_S1`
- selected predicted margin vs H012: `0.002371261`
- selected predicted margin vs duplicated-H012 control: `-0.001154236`
- duplicated-H012 control predicted public median: `0.571648980`
- H024 public-score permutation p(lower margin): `0.858000000`
- H025 row-permutation p(higher top1200 gain): `0.613333333`
- real H025 top1200 gain: `-1.367449827`

## Decision

- decision: `diagnostic_only_h012_needle_invariant_not_action_safe`
- promoted path: `none`

## Interpretation

The strongest local invariant family under H024 is `target_rollback`. If its best member is still priced above H012, H012 should be treated as a narrow public-equation basin. If a non-control family is priced below H012 with stress support, that family becomes the next public-world hypothesis.
