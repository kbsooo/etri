# E152 Branch-Orthogonal Decoder Audit

## Question

If E151 is right, the problem is not absence of signal but failure to decode non-collinear signal into public-tail-safe probabilities. This audit projects E137-E140 decoder moves away from the E144 branch and asks whether the remaining component survives the current gates.

## Source Geometry

| family | rows | candidate_interest | noncollinear_source | local_material_1e5 | post101_p95_ok | local_and_noncollinear | post101_and_noncollinear | best_all_minus_base | best_post101_p95 | max_resid_ratio_e144 | median_abs_cos_e144 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e137 | 1980 | 1646 | 1980 | 566 | 0 | 566 | 0 | -0.000047452 | 0.000000028 | 0.999931059 | 0.229053916 |
| e138 | 1314 | 1314 | 1314 | 884 | 698 | 884 | 698 | -0.000030467 | -0.000015691 | 0.980032784 | 0.336688230 |
| e139 | 1188 | 955 | 1188 | 474 | 699 | 474 | 699 | -0.000023771 | -0.000010520 | 0.989431065 | 0.308137622 |
| e140 | 168 | 38 | 168 | 4 | 0 | 4 | 0 | -0.000017556 | 0.000000141 | 0.999597041 | 0.106987585 |

## Projection Summary

| projection_mode | source_family | rows | noncollinear | relaxed_structural | budget_ok | post101_ok | gate_strict_actionable | strict_e72_post101 | e152_submit | best_all_minus_base | best_post101_p95 | best_e72_gap | max_candidate_resid_ratio_e144 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e144_plus_orth_full | e137 | 120 | 120 | 18 | 0 | 18 | 0 | 0 | 0 | -0.000045547 | -0.000003582 | 0.000099251 | 0.963022221 |
| e144_plus_orth_top100 | e137 | 120 | 120 | 26 | 0 | 26 | 0 | 0 | 0 | -0.000037588 | -0.000003911 | 0.000041133 | 0.951111331 |
| e95_plus_orth_full | e137 | 120 | 120 | 0 | 0 | 0 | 0 | 0 | 0 | -0.000035838 |  | 0.000112405 | 1.000000000 |
| e144_plus_orth_full | e138 | 120 | 120 | 4 | 120 | 40 | 0 | 0 | 0 | -0.000029216 | -0.000010035 | -0.000026284 | 0.912420773 |
| e144_plus_orth_top100 | e138 | 120 | 120 | 15 | 120 | 41 | 0 | 0 | 0 | -0.000028951 | -0.000009514 | -0.000026284 | 0.873848976 |
| e144_plus_orth_top50 | e137 | 120 | 120 | 27 | 0 | 27 | 0 | 0 | 0 | -0.000028788 | -0.000004243 | 0.000029411 | 0.936120871 |
| e95_plus_orth_top100 | e137 | 120 | 120 | 0 | 0 | 0 | 0 | 0 | 0 | -0.000027175 |  | 0.000041855 | 0.999882472 |
| e144_plus_orth_top100 | e139 | 120 | 120 | 18 | 120 | 83 | 0 | 0 | 0 | -0.000026113 | -0.000012274 | -0.000017171 | 0.833217198 |
| e144_plus_orth_top50 | e138 | 120 | 120 | 24 | 120 | 54 | 0 | 0 | 0 | -0.000025402 | -0.000006470 | -0.000025023 | 0.857788852 |
| e144_plus_orth_top50 | e139 | 120 | 120 | 23 | 120 | 92 | 0 | 0 | 0 | -0.000025153 | -0.000010367 | 0.000000000 | 0.847849106 |
| e144_plus_orth_full | e139 | 120 | 120 | 18 | 120 | 73 | 0 | 0 | 0 | -0.000024121 | -0.000009893 | -0.000017171 | 0.893579820 |
| e95_plus_orth_top100 | e138 | 120 | 120 | 0 | 120 | 0 | 28 | 0 | 0 | -0.000021557 |  | -0.000026284 | 0.999694115 |
| e95_plus_orth_full | e138 | 120 | 120 | 0 | 8 | 0 | 8 | 0 | 0 | -0.000019993 |  | -0.000002717 | 1.000000000 |
| e95_plus_orth_top50 | e137 | 120 | 120 | 0 | 0 | 0 | 0 | 0 | 0 | -0.000019009 |  | 0.000030165 | 0.999950792 |
| e95_plus_orth_top100 | e139 | 120 | 120 | 0 | 120 | 30 | 29 | 0 | 0 | -0.000018602 | -0.000007416 | -0.000017171 | 0.992819189 |
| e95_plus_orth_top50 | e139 | 120 | 120 | 0 | 120 | 22 | 36 | 0 | 0 | -0.000016141 | -0.000003413 | 0.000000000 | 0.998855580 |
| e95_plus_orth_top50 | e138 | 120 | 120 | 0 | 120 | 0 | 21 | 0 | 0 | -0.000015668 |  | -0.000025023 | 0.999999844 |
| e144_plus_orth_top100 | e140 | 120 | 120 | 65 | 0 | 21 | 0 | 0 | 0 | -0.000015070 | -0.000002066 | 0.000011385 | 0.887226948 |
| e144_plus_orth_full | e140 | 120 | 120 | 51 | 0 | 10 | 0 | 0 | 0 | -0.000014873 | -0.000000659 | 0.000011385 | 0.836382488 |
| e95_plus_orth_full | e139 | 120 | 120 | 0 | 0 | 18 | 0 | 0 | 0 | -0.000014051 | -0.000003730 | 0.000001355 | 1.000000000 |
| e144_plus_orth_top50 | e140 | 120 | 120 | 60 | 0 | 9 | 0 | 0 | 0 | -0.000013560 | -0.000001195 | 0.000011385 | 0.743766856 |
| e95_plus_orth_top100 | e140 | 120 | 120 | 0 | 0 | 0 | 0 | 0 | 0 | -0.000006636 |  | 0.000011385 | 0.999698584 |
| e95_plus_orth_full | e140 | 120 | 120 | 0 | 0 | 0 | 0 | 0 | 0 | -0.000005430 |  | 0.000012064 | 1.000000000 |
| e95_plus_orth_top50 | e140 | 120 | 120 | 0 | 0 | 0 | 0 | 0 | 0 | -0.000004246 |  | 0.000011385 | 1.000000000 |

## Gate Intersection Blockers

| intersection | count | best_projection_mode | best_source_family | best_all_minus_base | best_post101_p95 | best_e72_gap | best_candidate_resid_ratio_e144 | best_gate_strict_actionable | best_relaxed | best_budget_ok | best_post101_ok | best_tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| relaxed_and_budget | 102 | e144_plus_orth_top100 | e138 | -0.000012803 | -0.000005662 | 0.000000000 | 0.188475721 | False | True | True | True | e152_14f03eec |
| relaxed_and_post101 | 213 | e144_plus_orth_full | e137 | -0.000019280 | -0.000002164 | 0.000298308 | 0.404221050 | False | True | False | True | e152_2bcf7225 |
| budget_and_post101 | 435 | e144_plus_orth_top100 | e139 | -0.000025920 | -0.000010974 | -0.000000483 | 0.765494112 | False | False | True | True | e152_7de8cbc1 |
| budget_post101_actionable | 1 | e95_plus_orth_top50 | e139 | -0.000010614 | -0.000002244 | 0.000000000 | 0.992775072 | True | False | True | True | e152_db8dfc39 |
| relaxed_budget_post101 | 102 | e144_plus_orth_top100 | e138 | -0.000012803 | -0.000005662 | 0.000000000 | 0.188475721 | False | True | True | True | e152_14f03eec |
| relaxed_budget_actionable | 0 |  |  |  |  |  |  |  |  |  |  |  |
| relaxed_post101_actionable | 0 |  |  |  |  |  |  |  |  |  |  |  |
| all_four | 0 |  |  |  |  |  |  |  |  |  |  |  |
| beats_e144_and_all_four | 0 |  |  |  |  |  |  |  |  |  |  |  |

## Frontier Rows

| projection_mode | source_family | source_tag | alpha | top_k | all_minus_base | beats_e144_local | relaxed_structural_tol1e12 | budget_ok | post101_ok | gate_strict_actionable | strict_e72_post101 | candidate_noncollinear | candidate_resid_ratio_e144 | source_resid_ratio_e144 | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_a1091554 | 0.750000000 | 0 | -0.000045547 | True | False | False | False | False | False | True | 0.934728474 | 0.873366795 |  | 0.001924402 | e152_484650a0 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_ab3286f1 | 0.750000000 | 0 | -0.000045476 | True | False | False | False | False | False | True | 0.932922942 | 0.872947962 |  | 0.001775778 | e152_cfddbb6c |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_2aff1d4e | 0.750000000 | 0 | -0.000045022 | True | False | False | False | False | False | True | 0.935672573 | 0.875592152 |  | 0.001942511 | e152_73b2d888 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_e4f25510 | 0.750000000 | 0 | -0.000044978 | True | False | False | False | False | False | True | 0.933855299 | 0.875247081 |  | 0.001801945 | e152_e0029947 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_ab3286f1 | 1.000000000 | 0 | -0.000044876 | True | False | False | False | False | False | True | 0.960564149 | 0.872947962 |  | 0.002439523 | e152_d6d896a5 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_a1091554 | 1.000000000 | 0 | -0.000044640 | True | False | False | False | False | False | True | 0.961671437 | 0.873366795 |  | 0.002638939 | e152_e2f78181 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_e4f25510 | 1.000000000 | 0 | -0.000044136 | True | False | False | False | False | False | True | 0.961136264 | 0.875247081 |  | 0.002472789 | e152_d2fc9c69 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_2aff1d4e | 1.000000000 | 0 | -0.000043873 | True | False | False | False | False | False | True | 0.962249396 | 0.875592152 |  | 0.002661432 | e152_7644084e |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_91cf677a | 1.000000000 | 0 | -0.000043867 | True | False | False | False | False | False | True | 0.927480359 | 0.933083944 |  | 0.001208898 | e152_d77f9abd |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_781e9219 | 1.000000000 | 0 | -0.000043738 | True | False | False | False | False | False | True | 0.925082574 | 0.933053068 |  | 0.001140113 | e152_c421bc0e |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_a196bad9 | 1.000000000 | 0 | -0.000043079 | True | False | False | False | False | False | True | 0.930895885 | 0.937120621 |  | 0.001244591 | e152_aac1376f |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_acd1a0eb | 1.000000000 | 0 | -0.000042954 | True | False | False | False | False | False | True | 0.928545980 | 0.937101091 |  | 0.001182159 | e152_6bd8fe80 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_7535c2c8 | 0.750000000 | 0 | -0.000042891 | True | False | False | False | False | False | True | 0.935975413 | 0.890949145 |  | 0.001993737 | e152_e7fe974f |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_7db35255 | 0.750000000 | 0 | -0.000042860 | True | False | False | False | False | False | True | 0.934375760 | 0.890414970 |  | 0.001840399 | e152_b0d511fd |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_305f2736 | 0.750000000 | 0 | -0.000042438 | True | False | False | False | False | False | True | 0.936936795 | 0.893474384 |  | 0.001991875 | e152_e9fc7be6 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_46cb033c | 0.750000000 | 0 | -0.000042402 | True | False | False | False | False | False | True | 0.935319973 | 0.893036512 |  | 0.001847027 | e152_8bcc5ccc |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_8800018e | 1.000000000 | 0 | -0.000042323 | True | False | False | False | False | False | True | 0.925133990 | 0.939628632 |  | 0.001213081 | e152_d9b81743 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_b3bfad90 | 1.000000000 | 0 | -0.000042170 | True | False | False | False | False | False | True | 0.922855770 | 0.939583233 |  | 0.001139047 | e152_596b86e4 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_91fadaee | 0.750000000 | 0 | -0.000041855 | True | False | False | False | False | False | True | 0.928781926 | 0.905428562 |  | 0.001754608 | e152_a589cfb3 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_b7bc6f2d | 1.000000000 | 0 | -0.000041664 | True | False | False | False | False | False | True | 0.928822475 | 0.944012186 |  | 0.001209975 | e152_80ad75d0 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_23458139 | 1.000000000 | 0 | -0.000041585 | True | False | False | False | False | False | True | 0.926565176 | 0.943983853 |  | 0.001143515 | e152_a52d72d2 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_7db35255 | 1.000000000 | 0 | -0.000041569 | True | False | False | False | False | False | True | 0.961455330 | 0.890414970 |  | 0.002533795 | e152_6e239350 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_8bd72ce9 | 0.750000000 | 0 | -0.000041553 | True | False | False | False | False | False | True | 0.929583692 | 0.906513102 |  | 0.001769080 | e152_a90308fb |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_7535c2c8 | 1.000000000 | 0 | -0.000041301 | True | False | False | False | False | False | True | 0.962434640 | 0.890949145 |  | 0.002738865 | e152_7a71c363 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_46cb033c | 1.000000000 | 0 | -0.000040936 | True | False | False | False | False | False | True | 0.962033624 | 0.893036512 |  | 0.002542641 | e152_b63c6d78 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_91cf677a | 0.750000000 | 0 | -0.000040749 | True | False | False | False | False | False | True | 0.880834239 | 0.933083944 |  | 0.000897213 | e152_391a1d47 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_305f2736 | 1.000000000 | 0 | -0.000040681 | True | False | False | False | False | False | True | 0.963022221 | 0.893474384 |  | 0.002736344 | e152_79a74194 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_91fadaee | 1.000000000 | 0 | -0.000040562 | True | False | False | False | False | False | True | 0.958014745 | 0.905428562 |  | 0.002399690 | e152_034d752b |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_781e9219 | 0.750000000 | 0 | -0.000040498 | True | False | False | False | False | False | True | 0.877191383 | 0.933053068 |  | 0.000846117 | e152_0a270cd4 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_a196bad9 | 0.750000000 | 0 | -0.000040322 | True | False | False | False | False | False | True | 0.886052861 | 0.937120621 |  | 0.000925862 | e152_2c23a2c7 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_a1091554 | 0.500000000 | 0 | -0.000040314 | True | False | False | False | False | False | True | 0.868677743 | 0.873366795 |  | 0.001236256 | e152_b26732b2 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_81880485 | 1.000000000 | 0 | -0.000040314 | True | False | False | False | False | False | True | 0.868677743 | 0.873366795 |  | 0.001236256 | e152_b26732b2 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_2aff1d4e | 0.500000000 | 0 | -0.000040129 | True | False | False | False | False | False | True | 0.870385165 | 0.875592152 |  | 0.001250254 | e152_c6b3c36a |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_4176ff6b | 1.000000000 | 0 | -0.000040129 | True | False | False | False | False | False | True | 0.870385165 | 0.875592152 |  | 0.001250254 | e152_c6b3c36a |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_ab3286f1 | 0.500000000 | 0 | -0.000040080 | True | False | False | False | False | False | True | 0.865425947 | 0.872947962 |  | 0.001138198 | e152_0601e042 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_3a1aebab | 1.000000000 | 0 | -0.000040080 | True | False | False | False | False | False | True | 0.865425947 | 0.872947962 |  | 0.001138198 | e152_0601e042 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_acd1a0eb | 0.750000000 | 0 | -0.000040041 | True | False | False | False | False | False | True | 0.882458668 | 0.937101091 |  | 0.000879624 | e152_bf17ced3 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_8bd72ce9 | 1.000000000 | 0 | -0.000039993 | True | False | False | False | False | False | True | 0.958509420 | 0.906513102 |  | 0.002419348 | e152_db50aa35 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_e4f25510 | 0.500000000 | 0 | -0.000039890 | True | False | False | False | False | False | True | 0.867102926 | 0.875247081 |  | 0.001157684 | e152_628e17ec |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_42dd1975 | 1.000000000 | 0 | -0.000039890 | True | False | False | False | False | False | True | 0.867102926 | 0.875247081 |  | 0.001157684 | e152_628e17ec |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_cffabd2d | 0.750000000 | 0 | -0.000039640 | True | False | False | False | False | False | True | 0.929756283 | 0.920708718 |  | 0.001795099 | e152_f782023e |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_814405d0 | 0.750000000 | 0 | -0.000039296 | True | False | False | False | False | False | True | 0.930563472 | 0.922060207 |  | 0.001791179 | e152_a62a5c18 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_8800018e | 0.750000000 | 0 | -0.000039262 | True | False | False | False | False | False | True | 0.877269319 | 0.939628632 |  | 0.000879839 | e152_72374568 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_b3bfad90 | 0.750000000 | 0 | -0.000039000 | True | False | False | False | False | False | True | 0.873823441 | 0.939583233 |  | 0.000824533 | e152_f603d5e7 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_b7bc6f2d | 0.750000000 | 0 | -0.000038904 | True | False | False | False | False | False | True | 0.882880710 | 0.944012186 |  | 0.000877610 | e152_370958fb |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_7535c2c8 | 0.500000000 | 0 | -0.000038727 | True | False | False | False | False | False | True | 0.870933895 | 0.890949145 |  | 0.001257585 | e152_80512cf7 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_23458139 | 0.750000000 | 0 | -0.000038676 | True | False | False | False | False | False | True | 0.879441832 | 0.943983853 |  | 0.000827871 | e152_35c1cd68 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_305f2736 | 0.500000000 | 0 | -0.000038610 | True | False | False | False | False | False | True | 0.872679219 | 0.893474384 |  | 0.001257722 | e152_6fbbc256 |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_7db35255 | 0.500000000 | 0 | -0.000038554 | True | False | False | False | False | False | True | 0.868041104 | 0.890414970 |  | 0.001155883 | e152_57da5fdc |
| e144_plus_orth_full | e137 | e137_blocktarget_gradient_46cb033c | 0.500000000 | 0 | -0.000038418 | True | False | False | False | False | False | True | 0.869746909 | 0.893036512 |  | 0.001161656 | e152_9c1c4578 |

## Decision

No branch-orthogonal projection passes strict/E72/post101 plus active-veto gates. This strengthens the E151 world model: the visible decoder signal outside E142/E143/E144 is not currently translatable into a safe probability movement.
