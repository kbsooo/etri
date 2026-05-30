# E306 Within-Block S4 Row Placement

Public LB는 사용하지 않았다. E304 block prior를 직접 평균 이동으로 쓰지 않고, dateblock 내부 row-placement가 실제로 존재하는지 먼저 검증했다.

## Question

E305의 실패가 block prior 자체의 실패인가, 아니면 block 안 row identity를 못 맞힌 실패인가? E306은 context=human/JEPA row diary, target=같은 dateblock 안 S4-positive row rank로 둔 JEPA-style row-placement 실험이다.

## Summary

| row_views | row_gate_count | best_view | best_split | best_within_auc | generated_candidates | old_strict | null_evaluated | ready_32rep | best_null_strict_rate | best_dateblock_p90_dominance | best_mean_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 6 | family_jepa_dbdelta | row_stratified5 | 0.585020243 | 272 | 22 | 20 | 0 | 0.625000000 | 0.875000000 | 0.671875000 |

## Row-Placement Diagnostic

| view_id | split | global_auc | global_logloss | within_auc_weighted | within_auc_unweighted | mixed_blocks | pairs | null_median | null_p90 | null_dominance | row_placement_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_jepa_dbdelta | row_stratified5 | 0.517396184 | 0.805055964 | 0.585020243 | 0.560000000 | 60 | 494 | 0.497975709 | 0.548582996 | 0.979166667 | True |
| family_jepa_dbdelta | dateblock_holdout | 0.533609909 | 0.811003396 | 0.574898785 | 0.564259259 | 60 | 494 | 0.503036437 | 0.550607287 | 0.979166667 | True |
| calendar | subject_holdout | 0.464606381 | 0.726893573 | 0.554655870 | 0.561851852 | 60 | 494 | 0.494939271 | 0.532388664 | 0.937500000 | True |
| family_jepa_dbdelta | subject_holdout | 0.520522687 | 0.831586151 | 0.550607287 | 0.545092593 | 60 | 494 | 0.496963563 | 0.544534413 | 0.937500000 | True |
| calendar | dateblock_holdout | 0.510221260 | 0.713284042 | 0.540485830 | 0.558240741 | 60 | 494 | 0.494939271 | 0.539473684 | 0.895833333 | True |
| family_jepa | dateblock_holdout | 0.534030784 | 0.804506527 | 0.534412955 | 0.555648148 | 60 | 494 | 0.503036437 | 0.543522267 | 0.822916667 | True |
| story_episode_dbdelta | subject_holdout | 0.520001603 | 0.729485667 | 0.516194332 | 0.549814815 | 60 | 494 | 0.493927126 | 0.538461538 | 0.729166667 | False |
| story_episode | row_stratified5 | 0.513528139 | 0.733544316 | 0.512145749 | 0.525555556 | 60 | 494 | 0.492914980 | 0.543522267 | 0.666666667 | False |
| calendar | row_stratified5 | 0.558231121 | 0.695841505 | 0.512145749 | 0.524722222 | 60 | 494 | 0.507085020 | 0.547570850 | 0.562500000 | False |
| story_episode_dbdelta | row_stratified5 | 0.482824274 | 0.743759946 | 0.508097166 | 0.518055556 | 60 | 494 | 0.497975709 | 0.543522267 | 0.562500000 | False |
| story_episode_dbdelta | dateblock_holdout | 0.508658009 | 0.734115877 | 0.502024291 | 0.531851852 | 60 | 494 | 0.500000000 | 0.544534413 | 0.520833333 | False |
| story_episode | subject_holdout | 0.509339426 | 0.740096823 | 0.506072874 | 0.498425926 | 60 | 494 | 0.503036437 | 0.546558704 | 0.510416667 | False |
| family_jepa | subject_holdout | 0.466871092 | 0.987429263 | 0.493927126 | 0.466018519 | 60 | 494 | 0.505060729 | 0.553643725 | 0.395833333 | False |
| story_episode | dateblock_holdout | 0.490800866 | 0.751045317 | 0.483805668 | 0.494722222 | 60 | 494 | 0.497975709 | 0.539473684 | 0.333333333 | False |
| family_jepa | row_stratified5 | 0.579525413 | 0.761630168 | 0.475708502 | 0.449351852 | 60 | 494 | 0.496963563 | 0.536437247 | 0.260416667 | False |

## Best Prefilter Candidates

| basename | family | nonzero_rows | active_minus_inactive_block_S4 | active_minus_inactive_row_center | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | strict_promote_gate | pred_beats_current_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e306_withinblock_s4_global_rowcenter_top50_up_a0_0520_bc3ecd23.csv | global_rowcenter_top | 50 | -0.012748270 | 0.306673014 | -0.000411072 | -0.000114916 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_combined_top50_up_a0_0520_5ef87bc9.csv | global_combined_top | 50 | 0.387761104 | 0.218872814 | -0.000385233 | -0.000106255 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_rowcenter_top40_up_a0_0520_be28fd49.csv | global_rowcenter_top | 40 | 0.049420994 | 0.313167561 | -0.000317097 | -0.000090885 | True | 0.941176471 |
| submission_e306_withinblock_s4_control_topblock16_rowbottom3_up_a0_0520_cba453fb.csv | control_wrong_row | 41 | 0.473307399 | -0.116451368 | -0.000305647 | -0.000084320 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_rowcenter_top50_up_a0_0388_c1f59879.csv | global_rowcenter_top | 50 | -0.012748270 | 0.306673014 | -0.000313163 | -0.000082500 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_combined_top40_up_a0_0520_f95e29eb.csv | global_combined_top | 40 | 0.428618366 | 0.216019864 | -0.000299870 | -0.000082380 | True | 0.941176471 |
| submission_e306_withinblock_s4_topblock16_rowtop3_up_a0_0520_d7db2a81.csv | topblock_rowtop | 41 | 0.473307399 | 0.117665449 | -0.000317299 | -0.000081368 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_combined_top50_up_a0_0388_f0c686fe.csv | global_combined_top | 50 | 0.387761104 | 0.218872814 | -0.000293088 | -0.000076503 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_rowcenter_top32_up_a0_0520_320532a9.csv | global_rowcenter_top | 32 | 0.056601747 | 0.320828648 | -0.000244772 | -0.000074467 | True | 0.911764706 |
| submission_e306_withinblock_s4_global_combined_top32_up_a0_0520_caa05321.csv | global_combined_top | 32 | 0.464403416 | 0.211168381 | -0.000238753 | -0.000067716 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_rowcenter_top40_up_a0_0388_4d10a008.csv | global_rowcenter_top | 40 | 0.049420994 | 0.313167561 | -0.000241640 | -0.000065268 | True | 0.941176471 |
| submission_e306_withinblock_s4_control_topblock16_rowbottom2_up_a0_0520_58e0e274.csv | control_wrong_row | 31 | 0.460840539 | -0.144487058 | -0.000232752 | -0.000064229 | True | 0.941176471 |
| submission_e306_withinblock_s4_topblock16_rowtop2_up_a0_0520_187cbb7c.csv | topblock_rowtop | 31 | 0.460840539 | 0.135170123 | -0.000235630 | -0.000063641 | True | 0.941176471 |
| submission_e306_withinblock_s4_control_topblock12_rowbottom3_up_a0_0520_5b77d62a.csv | control_wrong_row | 29 | 0.540388522 | -0.095022497 | -0.000206163 | -0.000061302 | True | 0.911764706 |
| submission_e306_withinblock_s4_control_topblock16_rowbottom3_up_a0_0388_43d41203.csv | control_wrong_row | 41 | 0.473307399 | -0.116451368 | -0.000233459 | -0.000060206 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_combined_top40_up_a0_0388_eb828eb9.csv | global_combined_top | 40 | 0.428618366 | 0.216019864 | -0.000228863 | -0.000058963 | True | 0.941176471 |
| submission_e306_withinblock_s4_topblock12_rowtop3_up_a0_0520_d6d85574.csv | topblock_rowtop | 29 | 0.540388522 | 0.092047814 | -0.000218709 | -0.000057221 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_rowcenter_top24_up_a0_0520_437cd014.csv | global_rowcenter_top | 24 | 0.032752432 | 0.333379518 | -0.000181571 | -0.000057031 | True | 0.911764706 |
| submission_e306_withinblock_s4_control_topblock10_rowbottom3_up_a0_0520_2a0df251.csv | control_wrong_row | 26 | 0.562374286 | -0.104567167 | -0.000186407 | -0.000056325 | True | 0.911764706 |
| submission_e306_withinblock_s4_topblock16_rowtop3_up_a0_0388_3462bfb6.csv | topblock_rowtop | 41 | 0.473307399 | 0.117665449 | -0.000240838 | -0.000055892 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_rowcenter_top32_up_a0_0388_fd4de6a0.csv | global_rowcenter_top | 32 | 0.056601747 | 0.320828648 | -0.000185600 | -0.000054100 | True | 0.941176471 |
| submission_e306_withinblock_s4_topblock10_rowtop3_up_a0_0520_bc16577b.csv | topblock_rowtop | 26 | 0.562374286 | 0.101293688 | -0.000198953 | -0.000052245 | True | 0.941176471 |
| submission_e306_withinblock_s4_global_rowcenter_top50_up_a0_0250_40089d2c.csv | global_rowcenter_top | 50 | -0.012748270 | 0.306673014 | -0.000206129 | -0.000049273 | False | 0.941176471 |
| submission_e306_withinblock_s4_global_combined_top32_up_a0_0388_f671ac48.csv | global_combined_top | 32 | 0.464403416 | 0.211168381 | -0.000182115 | -0.000048577 | False | 0.941176471 |
| submission_e306_withinblock_s4_control_topblock12_rowbottom2_up_a0_0520_4f53de0b.csv | control_wrong_row | 23 | 0.523596829 | -0.109457997 | -0.000167248 | -0.000047869 | False | 0.941176471 |

## Governor Rows

| basename | family | nonzero_rows | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | dateblock_p90_dominance | dateblock_mean_dominance | public_free_ready | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e306_withinblock_s4_global_rowcenter_top24_up_a0_0520_437cd014.csv | global_rowcenter_top | 24 | -0.000181571 | -0.000057031 | 0.625000000 | 0.804687500 | 0.312500000 | 0.812500000 | 0.062500000 | False | do_not_submit |
| submission_e306_withinblock_s4_topblock10_rowtop3_up_a0_0520_bc16577b.csv | topblock_rowtop | 26 | -0.000198953 | -0.000052245 | 0.632812500 | 0.437500000 | 0.601562500 | 0.281250000 | 0.750000000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_combined_top40_up_a0_0388_eb828eb9.csv | global_combined_top | 40 | -0.000228863 | -0.000058963 | 0.671875000 | 0.539062500 | 0.515625000 | 0.593750000 | 0.375000000 | False | do_not_submit |
| submission_e306_withinblock_s4_topblock16_rowtop3_up_a0_0388_3462bfb6.csv | topblock_rowtop | 41 | -0.000240838 | -0.000055892 | 0.671875000 | 0.453125000 | 0.671875000 | 0.375000000 | 0.687500000 | False | do_not_submit |
| submission_e306_withinblock_s4_control_topblock16_rowbottom3_up_a0_0388_43d41203.csv | control_wrong_row | 41 | -0.000233459 | -0.000060206 | 0.695312500 | 0.640625000 | 0.414062500 | 0.875000000 | 0.062500000 | False | do_not_submit |
| submission_e306_withinblock_s4_control_topblock12_rowbottom3_up_a0_0520_5b77d62a.csv | control_wrong_row | 29 | -0.000206163 | -0.000061302 | 0.718750000 | 0.734375000 | 0.312500000 | 0.750000000 | 0.156250000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_combined_top32_up_a0_0520_caa05321.csv | global_combined_top | 32 | -0.000238753 | -0.000067716 | 0.718750000 | 0.679687500 | 0.453125000 | 0.687500000 | 0.343750000 | False | do_not_submit |
| submission_e306_withinblock_s4_topblock12_rowtop3_up_a0_0520_d6d85574.csv | topblock_rowtop | 29 | -0.000218709 | -0.000057221 | 0.726562500 | 0.492187500 | 0.609375000 | 0.343750000 | 0.906250000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_rowcenter_top40_up_a0_0388_4d10a008.csv | global_rowcenter_top | 40 | -0.000241640 | -0.000065268 | 0.726562500 | 0.546875000 | 0.578125000 | 0.218750000 | 0.531250000 | False | do_not_submit |
| submission_e306_withinblock_s4_control_topblock16_rowbottom2_up_a0_0520_58e0e274.csv | control_wrong_row | 31 | -0.000232752 | -0.000064229 | 0.734375000 | 0.601562500 | 0.476562500 | 0.593750000 | 0.437500000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_rowcenter_top32_up_a0_0520_320532a9.csv | global_rowcenter_top | 32 | -0.000244772 | -0.000074467 | 0.742187500 | 0.812500000 | 0.304687500 | 0.781250000 | 0.093750000 | False | do_not_submit |
| submission_e306_withinblock_s4_topblock16_rowtop2_up_a0_0520_187cbb7c.csv | topblock_rowtop | 31 | -0.000235630 | -0.000063641 | 0.742187500 | 0.617187500 | 0.515625000 | 0.687500000 | 0.406250000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_combined_top50_up_a0_0388_f0c686fe.csv | global_combined_top | 50 | -0.000293088 | -0.000076503 | 0.750000000 | 0.609375000 | 0.390625000 | 0.843750000 | 0.062500000 | False | do_not_submit |
| submission_e306_withinblock_s4_control_topblock16_rowbottom3_up_a0_0520_cba453fb.csv | control_wrong_row | 41 | -0.000305647 | -0.000084320 | 0.750000000 | 0.585937500 | 0.390625000 | 0.687500000 | 0.125000000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_combined_top50_up_a0_0520_5ef87bc9.csv | global_combined_top | 50 | -0.000385233 | -0.000106255 | 0.750000000 | 0.570312500 | 0.453125000 | 0.625000000 | 0.281250000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_rowcenter_top40_up_a0_0520_be28fd49.csv | global_rowcenter_top | 40 | -0.000317097 | -0.000090885 | 0.750000000 | 0.679687500 | 0.484375000 | 0.593750000 | 0.281250000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_rowcenter_top50_up_a0_0520_bc3ecd23.csv | global_rowcenter_top | 50 | -0.000411072 | -0.000114916 | 0.750000000 | 0.648437500 | 0.539062500 | 0.562500000 | 0.437500000 | False | do_not_submit |
| submission_e306_withinblock_s4_topblock16_rowtop3_up_a0_0520_d7db2a81.csv | topblock_rowtop | 41 | -0.000317299 | -0.000081368 | 0.750000000 | 0.476562500 | 0.632812500 | 0.437500000 | 0.718750000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_combined_top40_up_a0_0520_f95e29eb.csv | global_combined_top | 40 | -0.000299870 | -0.000082380 | 0.750000000 | 0.484375000 | 0.500000000 | 0.375000000 | 0.312500000 | False | do_not_submit |
| submission_e306_withinblock_s4_global_rowcenter_top50_up_a0_0388_c1f59879.csv | global_rowcenter_top | 50 | -0.000313163 | -0.000082500 | 0.750000000 | 0.585937500 | 0.554687500 | 0.343750000 | 0.437500000 | False | do_not_submit |

## Decision

- Row-placement signal exists locally, but no materialized candidate survived the stricter dateblock null governor.
- The block-state hypothesis remains diagnostic; translating it into S4 probability mass still needs a different action model.

## Outputs

- `analysis_outputs/e306_within_block_s4_row_cv.csv`
- `analysis_outputs/e306_within_block_s4_row_nulls.csv`
- `analysis_outputs/e306_within_block_s4_test_rows.csv`
- `analysis_outputs/e306_within_block_s4_candidates.csv`
- `analysis_outputs/e306_within_block_s4_prefilter.csv`
- `analysis_outputs/e306_within_block_s4_governor.csv`
- `analysis_outputs/e306_within_block_s4_summary.csv`
- `analysis_outputs/e306_within_block_s4_report.md`
