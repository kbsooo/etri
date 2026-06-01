# H037 Fixed-Point Translator HS-JEPA

## Question

Can H036's hidden public-world pressure be translated through H012's successful E247-to-H012 ray, without opening new support cells or leaving the H012 action basin?

## Alignment summary

| region | cells | cell_score_sum | cell_score_mean | targets |
| --- | --- | --- | --- | --- |
| support | 1200 | 265.524954009 | 0.221270795 | {'Q1': 167, 'Q2': 105, 'Q3': 141, 'S1': 194, 'S2': 207, 'S3': 194, 'S4': 192} |
| aligned_support | 903 | 244.595425195 | 0.270869795 | {'Q1': 119, 'Q2': 79, 'Q3': 106, 'S1': 148, 'S2': 165, 'S3': 139, 'S4': 147} |
| conflict_support | 297 | 20.929528814 | 0.070469794 | {'Q1': 48, 'Q2': 26, 'Q3': 35, 'S1': 46, 'S2': 42, 'S3': 55, 'S4': 45} |
| outside_support_high_world | 0 | 0.000000000 | 0.000000000 | {'Q1': 0, 'Q2': 0, 'Q3': 0, 'S1': 0, 'S2': 0, 'S3': 0, 'S4': 0} |


## Gate counts

| candidates | world_cell_lt_-0.0002 | world_row_lt_-0.00008 | h024_margin_negative | h024_support_ge_0.6 | world_and_h024_negative |
| --- | --- | --- | --- | --- | --- |
| 253 | 44 | 68 | 4 | 0 | 0 |


## Candidate ranking

| candidate_id | family | changed_cells | world_row_delta_vs_h012 | world_cell_delta_vs_h012 | pre_h012_h024_pred_public_median | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | pred_gain_top1200_sum | h037_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h037_support_qpull_k180_a0.03_c176_6b9ae6d4 | support_qpull_k180 | 176 | -0.000042258 | -0.000062846 | 0.557015253 | 0.000479900 | 0.250000000 | -4.493624932 | 4.493624932 | 1.020454545 |
| h037_target_S2_ray_k207_g1.03_c207_d058a7a3 | target_S2_ray_k207_g1.03 | 207 | -0.000016465 | -0.000024212 | 0.555314739 | 0.000290645 | 0.416666667 | -7.409458233 | 7.409458233 | 1.078227931 |
| h037_support_qpull_k360_a0.03_c323_bd637ab9 | support_qpull_k360 | 323 | -0.000067001 | -0.000098184 | 0.559214371 | 0.000536886 | 0.250000000 | -3.636221340 | 3.636221340 | 1.087648221 |
| h037_support_qpull_k180_a0.06_c176_d1a861fd | support_qpull_k180 | 176 | -0.000083029 | -0.000123425 | 0.557109706 | 0.000959814 | 0.250000000 | -4.484910904 | 4.484910904 | 1.097924901 |
| h037_support_qpull_k360_a0.06_c323_f2e5fc19 | support_qpull_k360 | 323 | -0.000131754 | -0.000193014 | 0.559315249 | 0.001013161 | 0.250000000 | -3.611395500 | 3.611395500 | 1.149308300 |
| h037_support_qpull_k700_a0.03_c563_23911b94 | support_qpull_k700 | 563 | -0.000089038 | -0.000129423 | 0.561142794 | 0.000666510 | 0.250000000 | -1.868618298 | 1.868618298 | 1.154841897 |
| h037_support_qpull_k180_a0.16_c176_aad22d6a | support_qpull_k180 | 176 | -0.000208453 | -0.000309481 | 0.557422464 | 0.002555666 | 0.250000000 | -4.566824276 | 4.566838561 | 1.177766798 |
| h037_support_qpull_k180_a0.1_c176_9508dba2 | support_qpull_k180 | 176 | -0.000135113 | -0.000200741 | 0.557234835 | 0.001598231 | 0.250000000 | -4.474388410 | 4.474388410 | 1.181719368 |
| h037_support_qpull_k360_a0.16_c323_ccbdda88 | support_qpull_k360 | 323 | -0.000331634 | -0.000485407 | 0.559646978 | 0.002691761 | 0.250000000 | -3.708035309 | 3.708049595 | 1.185671937 |
| h037_support_qpull_k360_a0.1_c323_07399207 | support_qpull_k360 | 323 | -0.000214633 | -0.000314310 | 0.559448192 | 0.001684877 | 0.250000000 | -3.606380667 | 3.606380667 | 1.189624506 |
| h037_target_S2_ray_k120_g1.03_c120_6cd3bc22 | target_S2_ray_k120_g1.03 | 120 | -0.000015708 | -0.000023148 | 0.555236962 | 0.000296296 | 0.250000000 | -6.216125031 | 6.216125031 | 1.205039526 |
| h037_dual_a260_c120_ga1.03_gc0.84_c380_34000f9b | dual_a260_c120_ga1.03_gc0.84 | 380 | -0.000094045 | -0.000136382 | 0.560959295 | 0.001097281 | 0.250000000 | -4.029616934 | 4.029616934 | 1.221245059 |
| h037_dual_a260_c120_ga1.1_gc0.55_c380_f8809d9f | dual_a260_c120_ga1.1_gc0.55 | 380 | -0.000258866 | -0.000376759 | 0.560904976 | 0.003580761 | 0.250000000 | -4.085566773 | 4.085566773 | 1.221640316 |
| h037_align_amp_k220_g1.015_c220_6dff50a5 | align_amp_k220_g1.015 | 220 | -0.000026520 | -0.000039162 | 0.556029670 | 0.000486363 | 0.250000000 | -4.066691563 | 4.066691563 | 1.224802372 |
| h037_support_qpull_k700_a0.06_c563_3a4f8cc1 | support_qpull_k700 | 563 | -0.000175154 | -0.000254536 | 0.561250956 | 0.001083478 | 0.250000000 | -1.828451310 | 1.828451310 | 1.232312253 |
| h037_target_S2_ray_k207_g1.07_c207_e45a6756 | target_S2_ray_k207_g1.07 | 207 | -0.000036891 | -0.000054260 | 0.555643813 | 0.000749595 | 0.250000000 | -7.409894797 | 7.409894797 | 1.240612648 |
| h037_support_qpull_k700_a0.1_c563_59165d4f | support_qpull_k700 | 563 | -0.000285467 | -0.000414721 | 0.561393606 | 0.001785757 | 0.250000000 | -1.802855926 | 1.802855926 | 1.241007905 |
| h037_dual_a260_c120_ga1.06_gc0.72_c380_f3bbef72 | dual_a260_c120_ga1.06_gc0.72 | 380 | -0.000170038 | -0.000247068 | 0.560733932 | 0.002157686 | 0.250000000 | -4.060385398 | 4.060385398 | 1.258003953 |
| h037_support_qpull_k700_a0.16_c563_bce10207 | support_qpull_k700 | 563 | -0.000441371 | -0.000640964 | 0.561606949 | 0.002857846 | 0.250000000 | -1.920606745 | 1.920621031 | 1.272628458 |
| h037_align_amp_k220_g1.16_c220_b787d2ac | align_amp_k220_g1.16 | 220 | -0.000251491 | -0.000370962 | 0.557973157 | 0.005214143 | 0.250000000 | -4.215359682 | 4.215945396 | 1.276185771 |


## Row-permutation stress

- rowperm p(perm >= real): `0.106666667`

| perm | real_top1200_sum | perm_top1200_sum | real_minus_perm |
| --- | --- | --- | --- |
| 0 | 4.493624932 | 3.869892814 | 0.623732118 |
| 1 | 4.493624932 | 4.668753955 | -0.175129024 |
| 2 | 4.493624932 | 4.259956292 | 0.233668639 |
| 3 | 4.493624932 | 4.730559065 | -0.236934134 |
| 4 | 4.493624932 | 3.359576779 | 1.134048152 |
| 5 | 4.493624932 | 3.828177812 | 0.665447119 |
| 6 | 4.493624932 | 3.172621833 | 1.321003098 |
| 7 | 4.493624932 | 3.781731258 | 0.711893673 |


## Decision

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | world_row_delta_vs_h012 | world_cell_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | rowperm_real_top1200_sum | rowperm_p_perm_ge_real | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| do_not_promote | False | h037_support_qpull_k180_a0.03_c176_6b9ae6d4 | submission_h037_support_qpull_k180_a0.03_c176_6b9ae6d4.csv | /Users/kbsoo/Downloads/cl2/hitl/h037_fixed_point_translator_jepa/submission_h037_support_qpull_k180_a0.03_c176_6b9ae6d4.csv | -0.000042258 | -0.000062846 | 0.000479900 | 0.250000000 | 4.493624932 | 0.106666667 | world-cell gain too small; world-row gain too small; H024 pre-H012 margin not below H012; H024 support below 60% |


## Interpretation
- Passing would mean H012 is a reusable fixed-point ray, not a single locked file.
- Failing means the translator must model more than support-preserving amplitude: exact route, calibration, or private/public split remains missing.
