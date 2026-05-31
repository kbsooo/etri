# E341 Sparse Residual Lifestyle Support Axis

## Question

Can E330's locally useful target-residual lifestyle states become public-visible if moved only on rare test tails?

## Source Residual States

| target | view_id | split | context_cols | teacher_resid_std | student_oof_r2 | student_spearman | base_loss | aug_loss | actual_delta | null_best | null_median | null_q20 | dominance | placebo_adjusted_vs_median | gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | jepa_resid | subject | 32 | 0.529534051 | -0.195539000 | -0.234482211 | 0.765899724 | 0.735689108 | -0.030210616 | -0.021406624 | 0.002898194 | -0.002572115 | 1.000000000 | -0.033108810 | True |
| Q1 | jepa_resid | dateblock | 32 | 0.490883367 | -0.166429177 | -0.221202146 | 0.678969360 | 0.653126588 | -0.025842772 | -0.026037033 | -0.000121684 | -0.008620067 | 0.958333333 | -0.025721088 | True |
| S2 | raw_day | subject | 160 | 0.498724340 | -0.296321149 | 0.206834602 | 0.698689330 | 0.682237256 | -0.016452074 | -0.017433356 | 0.000306265 | -0.009405310 | 0.958333333 | -0.016758339 | True |
| S2 | jepa_resid | dateblock | 32 | 0.444832946 | -0.122333143 | -0.165973165 | 0.590404664 | 0.576193446 | -0.014211218 | -0.005020530 | 0.002018470 | -0.000212523 | 1.000000000 | -0.016229688 | True |
| S1 | family_jepa_story | subject | 280 | 0.477844007 | -0.633356974 | 0.172189624 | 0.656678990 | 0.647551344 | -0.009127646 | -0.005946190 | 0.001337255 | -0.001349278 | 1.000000000 | -0.010464902 | True |
| S2 | family | dateblock | 40 | 0.444832946 | -0.147824396 | -0.127379658 | 0.590404664 | 0.582853040 | -0.007551624 | -0.006944294 | 0.000681265 | -0.001390855 | 1.000000000 | -0.008232889 | True |

## Generated Candidates

- generated candidates: `864`
- selector-promoted candidates: `0`
- information-sensor candidates: `96`
- movement-null-safe promoted candidates: `0`

### Best Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_s0_55_787b726b.csv | too_small_to_submit | -0.000150576 | -0.000443052 | -0.000017477 | 0.902777778 | 0.008568346 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_bad_veto_s0_55_836c3ab3.csv | too_small_to_submit | -0.000140976 | -0.000414917 | -0.000015473 | 0.902777778 | 0.008406965 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_bad_veto_s0_55_1b03343e.csv | too_small_to_submit | -0.000093885 | -0.000257153 | -0.000006556 | 0.902777778 | 0.008860784 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_s0_55_2bbb8ef5.csv | too_small_to_submit | -0.000097266 | -0.000269873 | -0.000006079 | 0.902777778 | 0.009123864 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_raw_s0_55_ddc802bf.csv | too_small_to_submit | -0.000033082 | -0.000085621 | -0.000005843 | 0.972222222 | 0.002801571 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_bad_veto_s0_55_ddc802bf.csv | too_small_to_submit | -0.000033082 | -0.000085621 | -0.000005843 | 0.972222222 | 0.002801571 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_s1_00_3f2647c3.csv | too_small_to_submit | -0.000028879 | -0.000062075 | -0.000004909 | 0.916666667 | 0.003301984 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_bad_veto_s1_60_560a5360.csv | too_small_to_submit | -0.000044486 | -0.000086238 | -0.000004789 | 0.916666667 | 0.004788865 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_bad_veto_s1_00_c0176424.csv | too_small_to_submit | -0.000029026 | -0.000060457 | -0.000004611 | 0.916666667 | 0.002993041 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_s0_55_d5faab46.csv | too_small_to_submit | -0.000018700 | -0.000040495 | -0.000003924 | 0.930555556 | 0.001816091 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_s1_60_6c50c20f.csv | too_small_to_submit | -0.000043752 | -0.000092523 | -0.000003387 | 0.902777778 | 0.005283175 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_bad_veto_s0_55_a9e90a57.csv | too_small_to_submit | -0.000018346 | -0.000039681 | -0.000003196 | 0.930555556 | 0.001646172 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top12_inv_bad_veto_s0_55_c67ab238.csv | too_small_to_submit | -0.000048271 | -0.000146039 | -0.000002816 | 0.930555556 | 0.001810956 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_bad_veto_s1_00_45215631.csv | too_small_to_submit | -0.000260819 | -0.000821019 | -0.000002779 | 0.902777778 | 0.015285391 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top12_inv_s0_55_73660ebe.csv | too_small_to_submit | -0.000051652 | -0.000158759 | -0.000002608 | 0.930555556 | 0.002074035 |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top34_bad_veto_s0_55_8fce451b.csv | too_small_to_submit | -0.000008797 | -0.000018224 | -0.000002141 | 0.972222222 | 0.000361356 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_raw_s1_00_952495d9.csv | too_small_to_submit | -0.000044877 | -0.000137965 | -0.000001628 | 0.916666667 | 0.005093765 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_bad_veto_s1_00_952495d9.csv | too_small_to_submit | -0.000044877 | -0.000137965 | -0.000001628 | 0.916666667 | 0.005093765 |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top12_bad_veto_s0_55_1ac8617c.csv | too_small_to_submit | -0.000008710 | -0.000017483 | -0.000001319 | 0.916666667 | -0.000055161 |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top34_raw_s0_55_5df86c04.csv | too_small_to_submit | -0.000011334 | -0.000017472 | -0.000001303 | 0.902777778 | 0.000695441 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_inv_bad_veto_s0_55_077ea15e.csv | too_small_to_submit | -0.000020123 | -0.000046530 | -0.000001132 | 0.902777778 | 0.002076612 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top20_inv_bad_veto_s0_55_23a18330.csv | too_small_to_submit | -0.000034880 | -0.000089173 | -0.000000477 | 0.916666667 | 0.001032467 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top34_inv_s0_55_31ec424f.csv | too_small_to_submit | -0.000026218 | -0.000072430 | 0.000000133 | 0.875000000 | 0.001378726 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top20_raw_s0_55_3d0a872b.csv | too_small_to_submit | -0.000042733 | -0.000137535 | 0.000000410 | 0.875000000 | 0.004680087 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top20_bad_veto_s0_55_3d0a872b.csv | too_small_to_submit | -0.000042733 | -0.000137535 | 0.000000410 | 0.875000000 | 0.004680087 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_inv_s0_55_61f41bda.csv | too_small_to_submit | -0.000021671 | -0.000053607 | 0.000000996 | 0.847222222 | 0.002108998 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top20_inv_bad_veto_s0_55_411fd4f0.csv | too_small_to_submit | -0.000017179 | -0.000041098 | 0.000001247 | 0.888888889 | 0.000359969 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top34_inv_bad_veto_s0_55_7323f72d.csv | too_small_to_submit | -0.000019875 | -0.000052669 | 0.000001299 | 0.833333333 | 0.001017600 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top12_inv_bad_veto_s0_55_18a34f41.csv | too_small_to_submit | -0.000013563 | -0.000032871 | 0.000001617 | 0.805555556 | 0.000991246 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_s1_00_70dd0db5.csv | too_small_to_submit | -0.000278028 | -0.000883045 | 0.000001713 | 0.875000000 | 0.015578811 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_state_abs_x_delta_top12_inv_s0_55_5b8d2106.csv | too_small_to_submit | -0.000024246 | -0.000071734 | 0.000001755 | 0.888888889 | -0.002079330 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_state_abs_x_delta_top12_inv_bad_veto_s0_55_5b8d2106.csv | too_small_to_submit | -0.000024246 | -0.000071734 | 0.000001755 | 0.888888889 | -0.002079330 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top20_inv_s0_55_07ff63be.csv | too_small_to_submit | -0.000019679 | -0.000050825 | 0.000001975 | 0.888888889 | 0.000444270 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_bad_veto_s1_00_58e9ece3.csv | too_small_to_submit | -0.000173166 | -0.000512633 | 0.000002292 | 0.888888889 | 0.016110516 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top20_inv_s0_55_ce2f5ecb.csv | too_small_to_submit | -0.000043831 | -0.000115796 | 0.000002549 | 0.805555556 | 0.000953275 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top12_inv_s0_55_b7aa10c6.csv | too_small_to_submit | -0.000013594 | -0.000034413 | 0.000002910 | 0.652777778 | 0.000885372 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top20_inv_bad_veto_s1_00_e826517c.csv | too_small_to_submit | -0.000055626 | -0.000147318 | 0.000003214 | 0.847222222 | 0.001877213 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_s1_00_eb769cf2.csv | too_small_to_submit | -0.000179717 | -0.000535889 | 0.000003414 | 0.888888889 | 0.016588843 |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top20_bad_veto_s0_55_08488be5.csv | too_small_to_submit | -0.000007121 | -0.000017198 | 0.000003418 | 0.847222222 | -0.000248759 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_inv_bad_veto_s0_55_3a2af9e9.csv | too_small_to_submit | -0.000037247 | -0.000099419 | 0.000003756 | 0.847222222 | 0.002255433 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_absdelta_top34_inv_bad_veto_s0_55_328fc5ba.csv | too_small_to_submit | -0.000130896 | -0.000369407 | 0.000004755 | 0.861111111 | 0.018433759 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_absdelta_top12_inv_bad_veto_s0_55_f9cb90eb.csv | too_small_to_submit | -0.000060553 | -0.000151507 | 0.000005180 | 0.888888889 | 0.011702852 |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top12_bad_veto_s1_00_5889fdb7.csv | too_small_to_submit | -0.000003097 | -0.000010418 | 0.000005405 | 0.583333333 | -0.000100292 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_inv_s0_55_54c20239.csv | too_small_to_submit | -0.000036246 | -0.000096055 | 0.000005426 | 0.861111111 | 0.002151899 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_absdelta_top12_inv_s0_55_b4b66f62.csv | too_small_to_submit | -0.000065947 | -0.000165412 | 0.000005593 | 0.888888889 | 0.012798176 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_state_abs_x_delta_top12_inv_s1_00_e5780aca.csv | too_small_to_submit | -0.000037208 | -0.000120731 | 0.000006211 | 0.861111111 | -0.003780600 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_state_abs_x_delta_top12_inv_bad_veto_s1_00_e5780aca.csv | too_small_to_submit | -0.000037208 | -0.000120731 | 0.000006211 | 0.861111111 | -0.003780600 |
| submission_e341_sparseresid_Q2_jepa_resid_subject_absdelta_top20_inv_bad_veto_s0_55_7f384d70.csv | too_small_to_submit | -0.000094322 | -0.000241855 | 0.000006355 | 0.888888889 | 0.017249801 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top12_inv_bad_veto_s0_55_7812bb90.csv | too_small_to_submit | -0.000011456 | -0.000033399 | 0.000006588 | 0.847222222 | -0.000375861 |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top20_inv_bad_veto_s1_60_ddd9ab96.csv | too_small_to_submit | -0.000083584 | -0.000222275 | 0.000006598 | 0.791666667 | 0.003003541 |

### Best Candidate Anatomy

| basename | target | view_id | split | tail_mask | topk | variant | scale | source_actual_delta | changed_rows | mean_abs_logit_delta | cos_with_e323_bad | cos_with_e216_bad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top34_bad_veto_s1_60_04d2de2f.csv | Q1 | jepa_resid | dateblock | posdelta | 34 | bad_veto | 1.600000000 | -0.025842772 | 34 | 0.002194286 | -0.079137699 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top34_bad_veto_s1_00_d7164eb0.csv | Q1 | jepa_resid | dateblock | posdelta | 34 | bad_veto | 1.000000000 | -0.025842772 | 34 | 0.001371429 | -0.079137699 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top34_bad_veto_s0_55_a9eb2cf6.csv | Q1 | jepa_resid | dateblock | posdelta | 34 | bad_veto | 0.550000000 | -0.025842772 | 34 | 0.000754286 | -0.079137699 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_bad_veto_s1_60_17ce3a81.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 34 | bad_veto | 1.600000000 | -0.009127646 | 34 | 0.002194286 | -0.075308857 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_bad_veto_s1_00_10a2b76b.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 34 | bad_veto | 1.000000000 | -0.009127646 | 34 | 0.001371429 | -0.075308857 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_bad_veto_s0_55_5c4b04a7.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 34 | bad_veto | 0.550000000 | -0.009127646 | 34 | 0.000754286 | -0.075308857 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_bad_veto_s1_60_69b3b991.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 20 | bad_veto | 1.600000000 | -0.009127646 | 20 | 0.001287314 | -0.064343950 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_bad_veto_s1_00_f5c9e15d.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 20 | bad_veto | 1.000000000 | -0.009127646 | 20 | 0.000804571 | -0.064343950 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_bad_veto_s0_55_7ba31d5f.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 20 | bad_veto | 0.550000000 | -0.009127646 | 20 | 0.000442514 | -0.064343950 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top34_bad_veto_s1_60_5c12d20a.csv | Q1 | jepa_resid | dateblock | negdelta | 34 | bad_veto | 1.600000000 | -0.025842772 | 34 | 0.002252800 | -0.063374056 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top34_bad_veto_s1_00_6f29d29b.csv | Q1 | jepa_resid | dateblock | negdelta | 34 | bad_veto | 1.000000000 | -0.025842772 | 34 | 0.001408000 | -0.063374056 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top34_bad_veto_s0_55_e5ab1006.csv | Q1 | jepa_resid | dateblock | negdelta | 34 | bad_veto | 0.550000000 | -0.025842772 | 34 | 0.000774400 | -0.063374056 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top20_bad_veto_s1_60_e7fe3da6.csv | Q1 | jepa_resid | dateblock | posdelta | 20 | bad_veto | 1.600000000 | -0.025842772 | 20 | 0.001287314 | -0.059206016 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top20_bad_veto_s1_00_67a5b42d.csv | Q1 | jepa_resid | dateblock | posdelta | 20 | bad_veto | 1.000000000 | -0.025842772 | 20 | 0.000804571 | -0.059206016 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top20_bad_veto_s0_55_52fd98dc.csv | Q1 | jepa_resid | dateblock | posdelta | 20 | bad_veto | 0.550000000 | -0.025842772 | 20 | 0.000442514 | -0.059206016 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top12_inv_bad_veto_s1_60_022f0e15.csv | Q1 | jepa_resid | dateblock | posdelta | 12 | inv_bad_veto | 1.600000000 | -0.025842772 | 12 | 0.000760686 | -0.050852220 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top12_inv_bad_veto_s1_00_9131e7a3.csv | Q1 | jepa_resid | dateblock | posdelta | 12 | inv_bad_veto | 1.000000000 | -0.025842772 | 12 | 0.000475429 | -0.050852220 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top12_inv_bad_veto_s0_55_7b8f90b0.csv | Q1 | jepa_resid | dateblock | posdelta | 12 | inv_bad_veto | 0.550000000 | -0.025842772 | 12 | 0.000261486 | -0.050852220 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_raw_s1_60_606b711b.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 34 | raw | 1.600000000 | -0.009127646 | 34 | 0.002486857 | -0.050591494 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_raw_s1_00_a73e899c.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 34 | raw | 1.000000000 | -0.009127646 | 34 | 0.001554286 | -0.050591494 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top34_raw_s0_55_1a6f7775.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 34 | raw | 0.550000000 | -0.009127646 | 34 | 0.000854857 | -0.050591494 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top34_raw_s1_60_f5c956c0.csv | Q1 | jepa_resid | dateblock | negdelta | 34 | raw | 1.600000000 | -0.025842772 | 34 | 0.002486857 | -0.045488315 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top34_raw_s1_00_de1f6276.csv | Q1 | jepa_resid | dateblock | negdelta | 34 | raw | 1.000000000 | -0.025842772 | 34 | 0.001554286 | -0.045488315 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top34_raw_s0_55_7b6ce189.csv | Q1 | jepa_resid | dateblock | negdelta | 34 | raw | 0.550000000 | -0.025842772 | 34 | 0.000854857 | -0.045488315 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top34_raw_s1_60_77bc27f1.csv | Q1 | jepa_resid | dateblock | posdelta | 34 | raw | 1.600000000 | -0.025842772 | 34 | 0.002486857 | -0.045052113 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top34_raw_s1_00_ce426344.csv | Q1 | jepa_resid | dateblock | posdelta | 34 | raw | 1.000000000 | -0.025842772 | 34 | 0.001554286 | -0.045052113 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top34_raw_s0_55_5c885497.csv | Q1 | jepa_resid | dateblock | posdelta | 34 | raw | 0.550000000 | -0.025842772 | 34 | 0.000854857 | -0.045052113 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_raw_s1_60_2c2c7647.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 20 | raw | 1.600000000 | -0.009127646 | 20 | 0.001462857 | -0.043895132 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_raw_s1_00_42f0ee8d.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 20 | raw | 1.000000000 | -0.009127646 | 20 | 0.000914286 | -0.043895132 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_raw_s0_55_24f9a7bf.csv | S1 | family_jepa_story | subject | state_abs_x_delta | 20 | raw | 0.550000000 | -0.009127646 | 20 | 0.000502857 | -0.043895132 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top20_inv_bad_veto_s1_60_4c4c4b63.csv | Q1 | jepa_resid | dateblock | negdelta | 20 | inv_bad_veto | 1.600000000 | -0.025842772 | 20 | 0.001345829 | -0.032360915 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top20_inv_bad_veto_s1_00_61aa7294.csv | Q1 | jepa_resid | dateblock | negdelta | 20 | inv_bad_veto | 1.000000000 | -0.025842772 | 20 | 0.000841143 | -0.032360915 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top20_inv_bad_veto_s0_55_f0e4603d.csv | Q1 | jepa_resid | dateblock | negdelta | 20 | inv_bad_veto | 0.550000000 | -0.025842772 | 20 | 0.000462629 | -0.032360915 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top20_inv_bad_veto_s1_60_f4612b66.csv | Q1 | jepa_resid | dateblock | posdelta | 20 | inv_bad_veto | 1.600000000 | -0.025842772 | 20 | 0.001111771 | -0.031877954 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top20_inv_bad_veto_s1_00_5e776abb.csv | Q1 | jepa_resid | dateblock | posdelta | 20 | inv_bad_veto | 1.000000000 | -0.025842772 | 20 | 0.000694857 | -0.031877954 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top20_inv_bad_veto_s0_55_027a9926.csv | Q1 | jepa_resid | dateblock | posdelta | 20 | inv_bad_veto | 0.550000000 | -0.025842772 | 20 | 0.000382171 | -0.031877954 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_posdelta_top12_inv_bad_veto_s1_60_2a5ee76b.csv | S1 | family_jepa_story | subject | posdelta | 12 | inv_bad_veto | 1.600000000 | -0.009127646 | 12 | 0.000702171 | -0.031390268 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_posdelta_top12_inv_bad_veto_s1_00_3d84dccb.csv | S1 | family_jepa_story | subject | posdelta | 12 | inv_bad_veto | 1.000000000 | -0.009127646 | 12 | 0.000438857 | -0.031390268 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_posdelta_top12_inv_bad_veto_s0_55_2c2598db.csv | S1 | family_jepa_story | subject | posdelta | 12 | inv_bad_veto | 0.550000000 | -0.009127646 | 12 | 0.000241371 | -0.031390268 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_negdelta_top34_bad_veto_s1_60_00f5cbcc.csv | S1 | family_jepa_story | subject | negdelta | 34 | bad_veto | 1.600000000 | -0.009127646 | 34 | 0.002369829 | -0.030495996 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_negdelta_top34_bad_veto_s1_00_74094c37.csv | S1 | family_jepa_story | subject | negdelta | 34 | bad_veto | 1.000000000 | -0.009127646 | 34 | 0.001481143 | -0.030495996 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_negdelta_top34_bad_veto_s0_55_fb8f75b2.csv | S1 | family_jepa_story | subject | negdelta | 34 | bad_veto | 0.550000000 | -0.009127646 | 34 | 0.000814629 | -0.030495996 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top12_inv_bad_veto_s1_60_5f1f021c.csv | Q1 | jepa_resid | dateblock | negdelta | 12 | inv_bad_veto | 1.600000000 | -0.025842772 | 12 | 0.000760686 | -0.029084322 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top12_inv_bad_veto_s1_00_376943ba.csv | Q1 | jepa_resid | dateblock | negdelta | 12 | inv_bad_veto | 1.000000000 | -0.025842772 | 12 | 0.000475429 | -0.029084322 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_negdelta_top12_inv_bad_veto_s0_55_3b4a7346.csv | Q1 | jepa_resid | dateblock | negdelta | 12 | inv_bad_veto | 0.550000000 | -0.025842772 | 12 | 0.000261486 | -0.029084322 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_posdelta_top20_inv_bad_veto_s1_60_be79d017.csv | S1 | family_jepa_story | subject | posdelta | 20 | inv_bad_veto | 1.600000000 | -0.009127646 | 20 | 0.001287314 | -0.026686257 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_posdelta_top20_inv_bad_veto_s1_00_aca852d3.csv | S1 | family_jepa_story | subject | posdelta | 20 | inv_bad_veto | 1.000000000 | -0.009127646 | 20 | 0.000804571 | -0.026686257 | 0.000000000 |
| submission_e341_sparseresid_S1_family_jepa_story_subject_posdelta_top20_inv_bad_veto_s0_55_8e919d06.csv | S1 | family_jepa_story | subject | posdelta | 20 | inv_bad_veto | 0.550000000 | -0.009127646 | 20 | 0.000442514 | -0.026686257 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top12_inv_s1_60_83c479a7.csv | Q1 | jepa_resid | dateblock | posdelta | 12 | inv | 1.600000000 | -0.025842772 | 12 | 0.000877714 | -0.025786463 | 0.000000000 |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_posdelta_top12_inv_s1_00_580541e4.csv | Q1 | jepa_resid | dateblock | posdelta | 12 | inv | 1.000000000 | -0.025842772 | 12 | 0.000548571 | -0.025786463 | 0.000000000 |

## Movement-Null Stress

| basename | null_count | actual_mean | actual_p90 | actual_beats_rate | actual_strict_promote | null_mean_best | null_mean_median | null_p90_best | null_p90_median | actual_mean_dominance | actual_p90_dominance | null_strict_promote_rate | mode_count | strict_null_modes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_raw_s0_55_ddc802bf.csv | 28 | -0.000033082 | -0.000005843 | 0.972222222 | False | -0.000032050 | -0.000002910 | -0.000005826 | 0.000015007 | 1.000000000 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_bad_veto_s1_00_952495d9.csv | 28 | -0.000044877 | -0.000001628 | 0.916666667 | False | -0.000048670 | -0.000006928 | 0.000000442 | 0.000026385 | 0.964285714 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top20_bad_veto_s0_55_3d0a872b.csv | 28 | -0.000042733 | 0.000000410 | 0.875000000 | False | -0.000051720 | -0.000004886 | 0.000001097 | 0.000026944 | 0.964285714 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_s1_00_3f2647c3.csv | 28 | -0.000028879 | -0.000004909 | 0.916666667 | False | -0.000079883 | -0.000006900 | -0.000003805 | 0.000034468 | 0.821428571 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top34_raw_s0_55_5df86c04.csv | 28 | -0.000011334 | -0.000001303 | 0.902777778 | False | -0.000022302 | 0.000011964 | -0.000000495 | 0.000030726 | 0.821428571 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_bad_veto_s1_00_c0176424.csv | 28 | -0.000029026 | -0.000004611 | 0.916666667 | False | -0.000079355 | -0.000012686 | -0.000003267 | 0.000033061 | 0.750000000 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_bad_veto_s1_60_560a5360.csv | 28 | -0.000044486 | -0.000004789 | 0.916666667 | False | -0.000133594 | -0.000028092 | -0.000000943 | 0.000028932 | 0.714285714 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_s0_55_d5faab46.csv | 28 | -0.000018700 | -0.000003924 | 0.930555556 | False | -0.000040690 | -0.000008528 | -0.000002190 | 0.000015160 | 0.714285714 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top34_inv_s0_55_31ec424f.csv | 28 | -0.000026218 | 0.000000133 | 0.875000000 | False | -0.000047666 | -0.000018674 | 0.000002027 | 0.000025458 | 0.571428571 | 1.000000000 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top20_raw_s0_55_3d0a872b.csv | 28 | -0.000042733 | 0.000000410 | 0.875000000 | False | -0.000042733 | -0.000018588 | -0.000000042 | 0.000015454 | 1.000000000 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_bad_veto_s0_55_836c3ab3.csv | 28 | -0.000140976 | -0.000015473 | 0.902777778 | False | -0.000141445 | -0.000026599 | -0.000017541 | 0.000026310 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_bad_veto_s0_55_ddc802bf.csv | 28 | -0.000033082 | -0.000005843 | 0.972222222 | False | -0.000033082 | -0.000010779 | -0.000005843 | 0.000015349 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_raw_s1_00_952495d9.csv | 28 | -0.000044877 | -0.000001628 | 0.916666667 | False | -0.000044877 | 0.000000097 | -0.000001628 | 0.000036904 | 0.964285714 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_s1_60_6c50c20f.csv | 28 | -0.000043752 | -0.000003387 | 0.902777778 | False | -0.000104747 | -0.000022883 | -0.000003387 | 0.000048305 | 0.750000000 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top12_inv_bad_veto_s0_55_c67ab238.csv | 28 | -0.000048271 | -0.000002816 | 0.930555556 | False | -0.000056360 | -0.000019713 | -0.000003269 | 0.000009039 | 0.642857143 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top34_inv_bad_veto_s0_55_7323f72d.csv | 28 | -0.000019875 | 0.000001299 | 0.833333333 | False | -0.000044352 | -0.000018986 | -0.000007139 | 0.000023387 | 0.571428571 | 0.964285714 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_bad_veto_s0_55_1b03343e.csv | 28 | -0.000093885 | -0.000006556 | 0.902777778 | False | -0.000093946 | -0.000017762 | -0.000009102 | 0.000013409 | 0.964285714 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top34_bad_veto_s0_55_8fce451b.csv | 28 | -0.000008797 | -0.000002141 | 0.972222222 | False | -0.000022062 | 0.000014975 | -0.000003515 | 0.000034433 | 0.821428571 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top20_inv_bad_veto_s0_55_23a18330.csv | 28 | -0.000034880 | -0.000000477 | 0.916666667 | False | -0.000078543 | -0.000020631 | -0.000001047 | 0.000019850 | 0.821428571 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_absdelta_top12_inv_bad_veto_s0_55_a9e90a57.csv | 28 | -0.000018346 | -0.000003196 | 0.930555556 | False | -0.000050999 | -0.000011093 | -0.000005281 | 0.000012634 | 0.785714286 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top12_inv_s0_55_73660ebe.csv | 28 | -0.000051652 | -0.000002608 | 0.930555556 | False | -0.000055532 | -0.000019356 | -0.000002785 | 0.000011489 | 0.750000000 | 0.928571429 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_inv_bad_veto_s0_55_077ea15e.csv | 42 | -0.000020123 | -0.000001132 | 0.902777778 | False | -0.000032144 | -0.000001834 | -0.000001772 | 0.000019093 | 0.880952381 | 0.904761905 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top20_inv_s0_55_2bbb8ef5.csv | 28 | -0.000097266 | -0.000006079 | 0.902777778 | False | -0.000098201 | -0.000021780 | -0.000006809 | 0.000014250 | 0.928571429 | 0.892857143 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_bad_veto_s1_00_45215631.csv | 28 | -0.000260819 | -0.000002779 | 0.902777778 | False | -0.000274726 | -0.000093991 | -0.000013311 | 0.000045152 | 0.821428571 | 0.857142857 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S2_raw_day_subject_state_abs_x_delta_top12_bad_veto_s0_55_1ac8617c.csv | 28 | -0.000008710 | -0.000001319 | 0.916666667 | False | -0.000017762 | 0.000005649 | -0.000002422 | 0.000015653 | 0.821428571 | 0.857142857 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_s0_55_787b726b.csv | 28 | -0.000150576 | -0.000017477 | 0.902777778 | False | -0.000161836 | -0.000101171 | -0.000017932 | 0.000020620 | 0.750000000 | 0.857142857 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S1_family_jepa_story_subject_absdelta_top20_inv_bad_veto_s0_55_411fd4f0.csv | 28 | -0.000017179 | 0.000001247 | 0.888888889 | False | -0.000032494 | -0.000011860 | -0.000012948 | 0.000018453 | 0.678571429 | 0.857142857 | 0.000000000 | 7 |  |
| submission_e341_sparseresid_S1_family_jepa_story_subject_state_abs_x_delta_top20_inv_s0_55_61f41bda.csv | 28 | -0.000021671 | 0.000000996 | 0.847222222 | False | -0.000041923 | -0.000015487 | -0.000003732 | 0.000013101 | 0.642857143 | 0.857142857 | 0.000000000 | 7 |  |

## Decision

Sparse residual tails remain information sensors only. Best p90 is `-0.000017477`, below submission standard but useful as support-axis evidence.

## Files

- `e341_sparse_residual_support_sources.csv`
- `e341_sparse_residual_support_candidates.csv`
- `e341_sparse_residual_support_scores.csv`
- `e341_sparse_residual_support_anatomy.csv`
- `e341_sparse_residual_support_movement_nulls.csv`
