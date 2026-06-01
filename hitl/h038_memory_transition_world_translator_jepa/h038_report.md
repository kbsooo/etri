# H038 Memory-Transition World Translator HS-JEPA

## Question

Did H012 win by detecting within-person state transitions where same-subject memory is misleading, and can H036 public-world pressure be translated only through those transition cells/rows?

## Transition Regions

| region | cells | posterior_gain_sum | cell_world_score_sum | mean_transition_exception_score | targets |
| --- | --- | --- | --- | --- | --- |
| support | 1200 | 12.535786068 | 265.524954009 | 0.536685924 | {'Q1': 167, 'Q2': 105, 'Q3': 141, 'S1': 194, 'S2': 207, 'S3': 194, 'S4': 192} |
| memory_exception | 523 | 8.133135268 | 200.501588821 | 0.730220104 | {'Q1': 62, 'Q2': 48, 'Q3': 46, 'S1': 100, 'S2': 98, 'S3': 75, 'S4': 94} |
| underfit_exception | 523 | 8.133135268 | 200.501588821 | 0.730220104 | {'Q1': 62, 'Q2': 48, 'Q3': 46, 'S1': 100, 'S2': 98, 'S3': 75, 'S4': 94} |
| memory_repair | 106 | 0.430182806 | 6.625747231 | 0.365267493 | {'Q1': 18, 'Q2': 10, 'Q3': 18, 'S1': 13, 'S2': 20, 'S3': 19, 'S4': 8} |
| broad_world_exception | 245 | 6.735904010 | 183.788898304 | 0.839248910 | {'Q1': 24, 'Q2': 11, 'Q3': 16, 'S1': 58, 'S2': 54, 'S3': 35, 'S4': 47} |

## Gate Counts

| candidates | world_cell_lt_-0.0002 | posterior_lt_-0.0001 | h024_margin_negative | h024_support_ge_0.55 | world_and_h024_negative |
| --- | --- | --- | --- | --- | --- |
| 459 | 42 | 2 | 0 | 0 | 0 |

## Top Candidates

| candidate_id | family | target_group | k | alpha | changed_cells_vs_h012 | world_cell_delta_vs_h012 | posterior_delta_vs_h012 | memory_delta_vs_h012 | pre_h012_h024_pred_public_median | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | h038_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h038_memory_repair_all_k140_a0.38_4edd633f | memory_repair | all | 106 | 0.380000000 | 106 | 0.000443266 | 0.000266868 | -0.002958880 | 0.593935533 | 0.002193776 | 0.250000000 | 1.012945827 | 0.175599129 |
| h038_memory_repair_all_k80_a0.38_1b43b52b | memory_repair | all | 80 | 0.380000000 | 80 | 0.000379429 | 0.000219113 | -0.002673459 | 0.593772767 | 0.001958657 | 0.250000000 | 0.729012951 | 0.212745098 |
| h038_memory_repair_S124_k40_a0.38_cb445f73 | memory_repair | S124 | 40 | 0.380000000 | 40 | 0.000184956 | 0.000114979 | -0.001214567 | 0.597679529 | 0.001722837 | 0.166666667 | 0.464639120 | 0.389869281 |
| h038_memory_repair_S124_k80_a0.38_90b4cfee | memory_repair | S124 | 41 | 0.380000000 | 41 | 0.000184948 | 0.000115100 | -0.001214592 | 0.597680663 | 0.001718592 | 0.166666667 | 0.449769196 | 0.399564270 |
| h038_memory_repair_Q2S124_k80_a0.38_e31aef36 | memory_repair | Q2S124 | 51 | 0.380000000 | 51 | 0.000208619 | 0.000123912 | -0.001299463 | 0.597249345 | 0.001720869 | 0.166666667 | 0.259288972 | 0.405337691 |
| h038_memory_repair_all_k40_a0.38_8042f26c | memory_repair | all | 40 | 0.380000000 | 40 | 0.000258558 | 0.000133743 | -0.001644886 | 0.592347322 | 0.001410932 | 0.250000000 | 0.463852656 | 0.433551198 |
| h038_memory_repair_all_k140_a0.24_96419ec4 | memory_repair | all | 106 | 0.240000000 | 106 | 0.000205985 | 0.000072536 | -0.001991920 | 0.593938939 | 0.001368380 | 0.250000000 | 0.989993888 | 0.434858388 |
| h038_memory_repair_S1S2_k40_a0.38_18babcb2 | memory_repair | S1S2 | 33 | 0.380000000 | 33 | 0.000181318 | 0.000114157 | -0.001192847 | 0.598185714 | 0.001681097 | 0.166666667 | 0.141381081 | 0.450326797 |
| h038_memory_repair_all_k80_a0.24_3ae1142c | memory_repair | all | 80 | 0.240000000 | 80 | 0.000177811 | 0.000061018 | -0.001798440 | 0.593775492 | 0.001220998 | 0.250000000 | 0.706188879 | 0.476361656 |
| h038_memory_repair_Q2S124_k40_a0.38_a844db15 | memory_repair | Q2S124 | 40 | 0.380000000 | 40 | 0.000180815 | 0.000098465 | -0.001142892 | 0.595878685 | 0.001503983 | 0.166666667 | 0.282102475 | 0.512962963 |
| h038_memory_repair_S124_k40_a0.24_a107a6f8 | memory_repair | S124 | 40 | 0.240000000 | 40 | 0.000085253 | 0.000030417 | -0.000818889 | 0.597597971 | 0.001054532 | 0.166666667 | 0.415229711 | 0.673856209 |
| h038_memory_repair_S124_k80_a0.24_7f42a6c3 | memory_repair | S124 | 41 | 0.240000000 | 41 | 0.000085247 | 0.000030491 | -0.000818907 | 0.597599157 | 0.001050210 | 0.166666667 | 0.399402121 | 0.681372549 |
| h038_memory_repair_Q2S124_k80_a0.24_42c4c130 | memory_repair | Q2S124 | 51 | 0.240000000 | 51 | 0.000097652 | 0.000032768 | -0.000876965 | 0.597168151 | 0.001050730 | 0.166666667 | 0.204021625 | 0.682897603 |
| h038_memory_repair_all_k40_a0.24_30a5dc12 | memory_repair | all | 40 | 0.240000000 | 40 | 0.000125247 | 0.000039924 | -0.001108360 | 0.592348861 | 0.000881310 | 0.250000000 | 0.428929373 | 0.688017429 |
| h038_memory_repair_all_k140_a0.14_244d3cf0 | memory_repair | all | 106 | 0.140000000 | 106 | 0.000091333 | 0.000004867 | -0.001209858 | 0.593941427 | 0.000787339 | 0.250000000 | 0.979872363 | 0.713943355 |
| h038_memory_repair_S1S2_k40_a0.24_6ec7ab55 | memory_repair | S1S2 | 33 | 0.240000000 | 33 | 0.000083555 | 0.000030686 | -0.000804004 | 0.598105583 | 0.001025274 | 0.166666667 | 0.093723386 | 0.721568627 |
| h038_exception_postpull_all_k40_a0.22_0839df17 | exception_postpull | all | 40 | 0.220000000 | 40 | -0.000031279 | -0.000009077 | 0.004504957 | 0.553912924 | 0.002300752 | 0.250000000 | -2.570709232 | 0.733877996 |
| h038_memory_repair_all_k80_a0.14_1ceea71a | memory_repair | all | 80 | 0.140000000 | 80 | 0.000079714 | 0.000005539 | -0.001091758 | 0.593777474 | 0.000701160 | 0.250000000 | 0.694608319 | 0.760893246 |
| h038_memory_repair_Q2S124_k40_a0.24_d5b6bbc3 | memory_repair | Q2S124 | 40 | 0.240000000 | 40 | 0.000086237 | 0.000026127 | -0.000771604 | 0.595810242 | 0.000922688 | 0.166666667 | 0.251221908 | 0.775708061 |
| h038_exception_postpull_all_k40_a0.14_cbc3af93 | exception_postpull | all | 40 | 0.140000000 | 40 | -0.000020844 | -0.000006108 | 0.002866354 | 0.553614967 | 0.001462133 | 0.250000000 | -2.557893807 | 0.779847495 |
| h038_exception_postpull_S12_k40_a0.22_321b645b | exception_postpull | S12 | 40 | 0.220000000 | 40 | -0.000032098 | -0.000007890 | 0.004232260 | 0.553515056 | 0.002336759 | 0.250000000 | -3.165800588 | 0.796405229 |
| h038_row_transition_S124_r12_aq0.18_am0.08_ef194811 | row_transition | S124 | 24 | 0.180000000 | 24 | -0.000028434 | -0.000005035 | 0.001573571 | 0.553089679 | 0.001421104 | 0.250000000 | -1.223042541 | 0.801525054 |
| h038_exception_postpull_S12_k40_a0.14_074780a4 | exception_postpull | S12 | 40 | 0.140000000 | 40 | -0.000021321 | -0.000005313 | 0.002692902 | 0.553210422 | 0.001480632 | 0.250000000 | -3.152503115 | 0.850000000 |
| h038_row_transition_Q2S124_r12_aq0.18_am0.08_89765518 | row_transition | Q2S124 | 30 | 0.180000000 | 30 | -0.000031392 | -0.000006222 | 0.001581842 | 0.553437491 | 0.001427347 | 0.250000000 | -1.246653213 | 0.852069717 |
| h038_exception_postpull_all_k40_a0.08_4b3b70f2 | exception_postpull | all | 40 | 0.080000000 | 40 | -0.000012332 | -0.000003637 | 0.001637723 | 0.553391359 | 0.000833092 | 0.250000000 | -2.513481217 | 0.867647059 |

## Row-Permutation Stress

- rowperm p(perm >= real): `0.836666667`

| perm | real_top1200_sum | perm_top1200_sum | real_minus_perm |
| --- | --- | --- | --- |
| 0 | -1.012945827 | -0.754716744 | -0.258229083 |
| 1 | -1.012945827 | -0.802623866 | -0.210321962 |
| 2 | -1.012945827 | -0.490312310 | -0.522633517 |
| 3 | -1.012945827 | -0.631702206 | -0.381243622 |
| 4 | -1.012945827 | -0.536859838 | -0.476085990 |
| 5 | -1.012945827 | -0.545290832 | -0.467654995 |
| 6 | -1.012945827 | -1.015708761 | 0.002762934 |
| 7 | -1.012945827 | -0.920677135 | -0.092268693 |

## Decision

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | family | target_group | world_cell_delta_vs_h012 | posterior_delta_vs_h012 | memory_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | rowperm_real_top1200_sum | rowperm_p_perm_ge_real | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| do_not_promote | False | h038_memory_repair_all_k140_a0.38_4edd633f | submission_h038_memory_repair_all_k140_a0.38_4edd633f.csv | /Users/kbsoo/Downloads/cl2/hitl/h038_memory_transition_world_translator_jepa/submission_h038_memory_repair_all_k140_a0.38_4edd633f.csv | memory_repair | all | 0.000443266 | 0.000266868 | -0.002958880 | 0.002193776 | 0.250000000 | -1.012945827 | 0.836666667 | world-cell gain too small; H012-posterior gain too small; H024 pre-H012 margin not below H012; H024 support below 55%; H025 row permutation stress weak |

## Interpretation

- Passing would mean the post-H012 translator is not H012-ray amplitude, but a memory-transition/public-world route gate.
- Failing means subject-state memory remains a strong contrastive diagnosis of H012, but still not an action translator.
