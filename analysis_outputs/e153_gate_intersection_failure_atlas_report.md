# E153 Gate-Intersection Failure Atlas

## Question

E152 found non-collinear decoder signal but zero all-four gate intersections. This audit asks which gate actually kills the near misses and whether the blockers look localized or structural.

## Gate-Class Summary

| gate_class | rows | best_all_minus_base | best_post101_p95 | best_e72_gap | median_q_share | median_s_share | median_q2s3_share | median_share_Q3 | median_share_S3 | median_tail_equal_cosine | median_tail_equal_resid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| missing_actionable | 102 | -0.000012803 | -0.000005662 | -0.000010715 | 0.578622974 | 0.421377026 | 0.158655271 | 0.348422309 | 0.158655271 | 0.970403428 | 0.249947863 |
| missing_relaxed | 1 | -0.000010614 | -0.000002244 | 0.000000000 | 0.639893447 | 0.360106553 | 0.120133912 | 0.293398600 | 0.120133912 | 0.972920899 | 0.240279389 |
| other | 2777 | -0.000045547 | -0.000012274 | -0.000026284 | 0.613270808 | 0.386729192 | 0.146458534 | 0.363943826 | 0.146246162 | 0.944107248 | 0.351901616 |

## Near-Miss Family/Mode Summary

| gate_class | source_family | projection_mode | rows | best_all_minus_base | median_q2s3_share | median_share_Q3 | median_share_S3 | median_tail_equal_resid | fail_action_cos_rate | fail_relaxed_tail_rate | fail_relaxed_raw_rate | fail_relaxed_world_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| missing_actionable | e138 | e144_plus_orth_top50 | 24 | -0.000012154 | 0.157314556 | 0.349652071 | 0.157314556 | 0.249635566 | 0.333333333 | 0.000000000 | 0.000000000 | 0.000000000 |
| missing_actionable | e139 | e144_plus_orth_top50 | 23 | -0.000012133 | 0.158661199 | 0.346534255 | 0.158661199 | 0.248365286 | 0.173913043 | 0.000000000 | 0.000000000 | 0.000000000 |
| missing_actionable | e139 | e144_plus_orth_top100 | 18 | -0.000012415 | 0.159854581 | 0.342367038 | 0.159854581 | 0.256859293 | 1.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| missing_actionable | e139 | e144_plus_orth_full | 18 | -0.000012287 | 0.159850493 | 0.340500255 | 0.159850493 | 0.248679535 | 0.500000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| missing_actionable | e138 | e144_plus_orth_top100 | 15 | -0.000012803 | 0.158936841 | 0.351841908 | 0.158936841 | 0.251902109 | 0.733333333 | 0.000000000 | 0.000000000 | 0.000000000 |
| missing_actionable | e138 | e144_plus_orth_full | 4 | -0.000012258 | 0.160532017 | 0.351328999 | 0.160532017 | 0.240630222 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| missing_relaxed | e139 | e95_plus_orth_top50 | 1 | -0.000010614 | 0.120133912 | 0.293398600 | 0.120133912 | 0.240279389 | 0.000000000 | 0.000000000 | 1.000000000 | 1.000000000 |

## Component Blockers

| gate_class | component | fail_rate | fail_count | rows |
| --- | --- | --- | --- | --- |
| missing_actionable | fail_action_active_q2s3 | 0.990196078 | 101 | 102 |
| missing_actionable | fail_action_cos | 0.490196078 | 50 | 102 |
| missing_actionable | fail_action_e72 | 0.000000000 | 0 | 102 |
| missing_actionable | fail_action_material | 0.000000000 | 0 | 102 |
| missing_actionable | fail_relaxed_margin | 0.000000000 | 0 | 102 |
| missing_actionable | fail_relaxed_all_beats | 0.000000000 | 0 | 102 |
| missing_actionable | fail_relaxed_set_mean | 0.000000000 | 0 | 102 |
| missing_actionable | fail_relaxed_tail | 0.000000000 | 0 | 102 |
| missing_actionable | fail_relaxed_hidden | 0.000000000 | 0 | 102 |
| missing_actionable | fail_relaxed_world | 0.000000000 | 0 | 102 |
| missing_actionable | fail_relaxed_raw | 0.000000000 | 0 | 102 |
| missing_relaxed | fail_relaxed_world | 1.000000000 | 1 | 1 |
| missing_relaxed | fail_relaxed_raw | 1.000000000 | 1 | 1 |
| missing_relaxed | fail_action_cos | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_action_active_q2s3 | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_action_e72 | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_action_material | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_relaxed_margin | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_relaxed_all_beats | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_relaxed_set_mean | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_relaxed_tail | 0.000000000 | 0 | 1 |
| missing_relaxed | fail_relaxed_hidden | 0.000000000 | 0 | 1 |

## Target Contrasts

| gate_class | target | rows | mean_share | median_share | mean_lift_vs_rest | top_target_rate |
| --- | --- | --- | --- | --- | --- | --- |
| missing_actionable | S3 | 102 | 0.158377349 | 0.158655271 | 0.022774096 | 0.000000000 |
| missing_actionable | S4 | 102 | 0.125150466 | 0.124319612 | 0.020949251 | 0.000000000 |
| missing_actionable | S2 | 102 | 0.138709484 | 0.138608175 | 0.018799901 | 0.000000000 |
| missing_actionable | S1 | 102 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| missing_actionable | Q2 | 102 | 0.000000000 | 0.000000000 | -0.002486649 | 0.000000000 |
| missing_actionable | Q3 | 102 | 0.344440178 | 0.348422309 | -0.029801288 | 1.000000000 |
| missing_actionable | Q1 | 102 | 0.233322523 | 0.232590982 | -0.030235311 | 0.000000000 |
| missing_relaxed | Q1 | 1 | 0.346494847 | 0.346494847 | 0.084037027 | 1.000000000 |
| missing_relaxed | S2 | 1 | 0.137676340 | 0.137676340 | 0.017106866 | 0.000000000 |
| missing_relaxed | S1 | 1 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000000000 |
| missing_relaxed | Q2 | 1 | 0.000000000 | 0.000000000 | -0.002399414 | 0.000000000 |
| missing_relaxed | S4 | 1 | 0.102296301 | 0.102296301 | -0.002647786 | 0.000000000 |
| missing_relaxed | S3 | 1 | 0.120133912 | 0.120133912 | -0.016281576 | 0.000000000 |
| missing_relaxed | Q3 | 1 | 0.293398600 | 0.293398600 | -0.079815117 | 0.000000000 |

## Frontier Near Misses

| gate_class | passed_gate_count | projection_mode | source_family | source_tag | alpha | top_k | all_minus_base | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | tail_equal_law_cosine | tail_equal_law_resid_ratio | q2s3_share | share_Q3 | share_S3 | cos_e144 | cos_e72 | fail_action_cos | fail_action_active_q2s3 | fail_relaxed_tail | fail_relaxed_world | fail_relaxed_raw | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_44d71d03 | 0.100000000 | 100 | -0.000012803 | -0.000005662 | 0.000000000 | 0.969068433 | 0.256281889 | 0.157024651 | 0.353326916 | 0.157024651 | 0.982077850 | -0.040726331 | True | True | False | False | False | e152_14f03eec |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_46382460 | 0.100000000 | 100 | -0.000012794 | -0.000005654 | 0.000000000 | 0.969086833 | 0.256198387 | 0.157035092 | 0.353304439 | 0.157035092 | 0.982191992 | -0.040672441 | True | True | False | False | False | e152_c7c68547 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_a1b50678 | 0.100000000 | 100 | -0.000012761 | -0.000005604 | 0.000000000 | 0.969214142 | 0.255619774 | 0.157884566 | 0.353154963 | 0.157884566 | 0.983053018 | -0.039954216 | True | True | False | False | False | e152_4acbdc73 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_1fa9b255 | 0.100000000 | 100 | -0.000012756 | -0.000005599 | 0.000000000 | 0.969223252 | 0.255578314 | 0.157890332 | 0.353137341 | 0.157890332 | 0.983110496 | -0.039928019 | True | True | False | False | False | e152_2ac8771f |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_02d30c7d | 0.100000000 | 100 | -0.000012537 | -0.000005240 | 0.000000000 | 0.969761612 | 0.253113087 | 0.159504687 | 0.351875032 | 0.159504687 | 0.986920186 | -0.037002653 | True | True | False | False | False | e152_f1bf70c9 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_4df5582b | 0.100000000 | 100 | -0.000012524 | -0.000005020 | 0.000000000 | 0.969867195 | 0.252641148 | 0.159532714 | 0.351841908 | 0.159532714 | 0.987191075 | -0.036598072 | True | True | False | False | False | e152_9d5d8200 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_36b09f34 | 0.100000000 | 100 | -0.000012509 | -0.000004726 | 0.000000000 | 0.969981103 | 0.252196698 | 0.161012359 | 0.348859008 | 0.161012359 | 0.987373052 | -0.036400295 | True | True | False | False | False | e152_0a49b46b |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_0aee7116 | 0.100000000 | 100 | -0.000012497 | -0.000004624 | 0.000000000 | 0.970050630 | 0.251417944 | 0.161710247 | 0.348805831 | 0.161710247 | 0.987981335 | -0.035838515 | True | True | False | False | False | e152_3cc21d18 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_c04699c9 | 0.100000000 | 100 | -0.000012488 | -0.000004594 | 0.000000000 | 0.969936246 | 0.251902109 | 0.159613496 | 0.351037646 | 0.159613496 | 0.987810212 | -0.035931754 | True | True | False | False | False | e152_63dfca26 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_6327a967 | 0.100000000 | 100 | -0.000012479 | -0.000004617 | 0.000000000 | 0.970091292 | 0.251238371 | 0.161738050 | 0.348850475 | 0.161738050 | 0.988082684 | -0.035528896 | True | True | False | False | False | e152_cacfe566 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_659fb9e1 | 0.100000000 | 100 | -0.000012470 | -0.000004588 | 0.000000000 | 0.969979280 | 0.251712562 | 0.159642962 | 0.351077440 | 0.159642962 | 0.987909696 | -0.035611943 | True | True | False | False | False | e152_c0838df9 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_f69d87df | 0.100000000 | 100 | -0.000012415 | -0.000004708 | 0.000000000 | 0.967346693 | 0.263221918 | 0.149986194 | 0.351872994 | 0.149986194 | 0.984546731 | -0.036743676 | True | True | False | False | False | e152_c6ed9e78 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_b1db95cd | 0.100000000 | 100 | -0.000012340 | -0.000005016 | -0.000000483 | 0.967974698 | 0.261043383 | 0.159994274 | 0.330881047 | 0.159994274 | 0.987778267 | -0.036582885 | True | True | False | False | False | e152_33f3d6b8 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_f6547fe2 | 0.100000000 | 100 | -0.000012328 | -0.000004516 | -0.000000628 | 0.969552032 | 0.253559841 | 0.158306509 | 0.349648080 | 0.158306509 | 0.984162792 | -0.033247046 | True | True | False | False | False | e152_2086a57e |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_bc02c721 | 0.100000000 | 100 | -0.000012323 | -0.000005009 | -0.000000483 | 0.967916030 | 0.261347407 | 0.160629917 | 0.329628757 | 0.160629917 | 0.987874108 | -0.036837396 | True | True | False | False | False | e152_aa7c894c |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_f3f54666 | 0.100000000 | 100 | -0.000012307 | -0.000004508 | -0.000000627 | 0.969580813 | 0.253430787 | 0.158331688 | 0.349576077 | 0.158331688 | 0.984414446 | -0.033179783 | True | True | False | False | False | e152_9c3eeec8 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_f8461d4e | 0.100000000 | 100 | -0.000012297 | -0.000004998 | -0.000000483 | 0.968067977 | 0.260624869 | 0.160018792 | 0.331023279 | 0.160018792 | 0.988168336 | -0.036392154 | True | True | False | False | False | e152_c88a1519 |
| missing_actionable | 3 | e144_plus_orth_full | e139 | e138_blocktarget_set_consensus_decoder_f6547fe2 | 0.100000000 | 0 | -0.000012287 | -0.000004699 | -0.000001868 | 0.971196071 | 0.246377730 | 0.157654888 | 0.348092153 | 0.157654888 | 0.982570570 | -0.034113533 | False | True | False | False | False | e152_2266b73b |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_8024ba79 | 0.100000000 | 100 | -0.000012286 | -0.000004994 | -0.000000483 | 0.968091138 | 0.260520854 | 0.160024935 | 0.331058917 | 0.160024935 | 0.988264993 | -0.036344375 | True | True | False | False | False | e152_cac01164 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_49c5e734 | 0.100000000 | 100 | -0.000012280 | -0.000004992 | -0.000000483 | 0.968012051 | 0.260916436 | 0.160644753 | 0.329790062 | 0.160644753 | 0.988261309 | -0.036642453 | True | True | False | False | False | e152_4b620d72 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_169e0bff | 0.100000000 | 100 | -0.000012270 | -0.000004987 | -0.000000483 | 0.968035888 | 0.260809343 | 0.160648470 | 0.329830478 | 0.160648470 | 0.988357253 | -0.036593619 | True | True | False | False | False | e152_02c30b53 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_107ff795 | 0.100000000 | 100 | -0.000012267 | -0.000004491 | -0.000000624 | 0.969636642 | 0.253180252 | 0.158381094 | 0.349434793 | 0.158381094 | 0.984902024 | -0.033047716 | True | True | False | False | False | e152_51e6ba85 |
| missing_actionable | 3 | e144_plus_orth_full | e139 | e138_blocktarget_set_consensus_decoder_f3f54666 | 0.100000000 | 0 | -0.000012266 | -0.000004685 | -0.000001857 | 0.971211841 | 0.246303215 | 0.157538423 | 0.348091941 | 0.157538423 | 0.982855738 | -0.034134663 | False | True | False | False | False | e152_3e1d7dcd |
| missing_actionable | 3 | e144_plus_orth_full | e138 | e138_blocktarget_vetonull_overlap_7f70f22f | 0.100000000 | 0 | -0.000012258 | -0.000004688 | -0.000002860 | 0.972400185 | 0.240817737 | 0.159672018 | 0.353183917 | 0.159672018 | 0.987297288 | -0.033937681 | False | True | False | False | False | e152_efe33e46 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_8e6b6523 | 0.100000000 | 100 | -0.000012253 | -0.000004485 | -0.000000623 | 0.969656666 | 0.253090327 | 0.158399000 | 0.349383586 | 0.158399000 | 0.985076709 | -0.032999822 | True | True | False | False | False | e152_053d27b5 |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_dccaf6c0 | 0.100000000 | 100 | -0.000012249 | -0.000004979 | -0.000000483 | 0.968171698 | 0.260158745 | 0.160046479 | 0.331183898 | 0.160046479 | 0.988600563 | -0.036176845 | True | True | False | False | False | e152_de27948e |
| missing_actionable | 3 | e144_plus_orth_full | e138 | e138_blocktarget_vetonull_overlap_c975a0f9 | 0.100000000 | 0 | -0.000012243 | -0.000004681 | -0.000002846 | 0.972391683 | 0.240854524 | 0.159564370 | 0.353239327 | 0.159564370 | 0.987436795 | -0.033987649 | False | True | False | False | False | e152_50b3194b |
| missing_actionable | 3 | e144_plus_orth_full | e138 | e138_blocktarget_vetonull_overlap_fa60a8ba | 0.100000000 | 0 | -0.000012232 | -0.000004685 | -0.000003068 | 0.972502260 | 0.240400587 | 0.161514972 | 0.349394760 | 0.161514972 | 0.987981558 | -0.033882444 | False | True | False | False | False | e152_75b0527f |
| missing_actionable | 3 | e144_plus_orth_top100 | e139 | e138_blocktarget_set_consensus_decoder_00282dc0 | 0.100000000 | 100 | -0.000012232 | -0.000004972 | -0.000000483 | 0.968118787 | 0.260436568 | 0.160661506 | 0.329972219 | 0.160661506 | 0.988690345 | -0.036422397 | True | True | False | False | False | e152_31231d6f |
| missing_actionable | 3 | e144_plus_orth_full | e139 | e138_blocktarget_set_consensus_decoder_f69d87df | 0.100000000 | 0 | -0.000012227 | -0.000004525 | 0.000000000 | 0.969664917 | 0.253212757 | 0.147076117 | 0.353174775 | 0.147076117 | 0.981117218 | -0.037963508 | True | False | False | False | False | e152_f631badf |
| missing_actionable | 3 | e144_plus_orth_full | e139 | e138_blocktarget_set_consensus_decoder_107ff795 | 0.100000000 | 0 | -0.000012226 | -0.000004659 | -0.000001834 | 0.971242156 | 0.246159787 | 0.157745450 | 0.347911592 | 0.157745450 | 0.983399609 | -0.033890768 | False | True | False | False | False | e152_f4216ea5 |
| missing_actionable | 3 | e144_plus_orth_full | e138 | e138_blocktarget_vetonull_overlap_c65b97ae | 0.100000000 | 0 | -0.000012218 | -0.000004678 | -0.000003053 | 0.972492548 | 0.240442707 | 0.161392015 | 0.349474082 | 0.161392015 | 0.988111714 | -0.033937452 | False | True | False | False | False | e152_f35b6b55 |
| missing_actionable | 3 | e144_plus_orth_full | e139 | e138_blocktarget_set_consensus_decoder_8e6b6523 | 0.100000000 | 0 | -0.000012211 | -0.000004649 | -0.000001826 | 0.971252938 | 0.246108711 | 0.157623221 | 0.347927721 | 0.157623221 | 0.983598054 | -0.033931494 | False | True | False | False | False | e152_83890456 |
| missing_actionable | 3 | e144_plus_orth_top50 | e138 | e138_blocktarget_vetonull_overlap_44d71d03 | 0.100000000 | 50 | -0.000012154 | -0.000004627 | 0.000000000 | 0.969816118 | 0.252503089 | 0.155639827 | 0.351612629 | 0.155639827 | 0.986419515 | -0.036183825 | True | True | False | False | False | e152_d3b3dea6 |
| missing_actionable | 3 | e144_plus_orth_top50 | e138 | e138_blocktarget_vetonull_overlap_46382460 | 0.100000000 | 50 | -0.000012147 | -0.000004622 | 0.000000000 | 0.969829166 | 0.252444186 | 0.155655948 | 0.351587813 | 0.155655948 | 0.986510529 | -0.036145146 | True | True | False | False | False | e152_82ef3cf4 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_7f70f22f | 0.100000000 | 100 | -0.000012145 | -0.000004408 | 0.000000000 | 0.970785676 | 0.248023677 | 0.157432882 | 0.353965940 | 0.157432882 | 0.988831447 | -0.032499067 | False | True | False | False | False | e152_aff6876f |
| missing_actionable | 3 | e144_plus_orth_top50 | e139 | e138_blocktarget_set_consensus_decoder_f69d87df | 0.100000000 | 50 | -0.000012133 | -0.000004653 | 0.000000000 | 0.970155680 | 0.251099617 | 0.152970112 | 0.350309112 | 0.152970112 | 0.985933367 | -0.034387721 | True | True | False | False | False | e152_bc961b22 |
| missing_actionable | 3 | e144_plus_orth_top100 | e138 | e138_blocktarget_vetonull_overlap_c975a0f9 | 0.100000000 | 100 | -0.000012132 | -0.000004403 | 0.000000000 | 0.970796221 | 0.247975118 | 0.157454068 | 0.353895001 | 0.157454068 | 0.988954925 | -0.032453679 | False | True | False | False | False | e152_46f1ca00 |
| missing_actionable | 3 | e144_plus_orth_full | e139 | e138_blocktarget_set_consensus_decoder_b1db95cd | 0.100000000 | 0 | -0.000012129 | -0.000004930 | -0.000000483 | 0.970151504 | 0.251560905 | 0.160508950 | 0.328296192 | 0.160508950 | 0.984670930 | -0.039296844 | True | True | False | False | False | e152_10bf283d |
| missing_actionable | 3 | e144_plus_orth_top50 | e138 | e138_blocktarget_vetonull_overlap_8eca8d2c | 0.100000000 | 50 | -0.000012127 | -0.000004646 | 0.000000000 | 0.970025671 | 0.251601515 | 0.157308881 | 0.348909296 | 0.157308881 | 0.986851713 | -0.035763021 | True | True | False | False | False | e152_103107f6 |

## Decision

No submission. The near misses split into `102` missing-actionable rows and `1` missing-relaxed rows. This supports the E152 interpretation: the decoder failure is not a single scalar threshold that can be tuned; it is a mismatch between tail-equal/actionability geometry and relaxed structural health.
