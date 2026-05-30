# E311 Pair Micro-Action Combiner

Public LB는 사용하지 않았다. E310의 visibility/null-rarity cliff를 두 방식으로 찔렀다: null-rare micro pair actions를 stack하고, old-strict pair actions에서 matched-null 평균 움직임을 빼서 residual action을 만든다.

## E310 Cliff Input

| final_decision | n | best_p90 | best_null_strict |
| --- | --- | --- | --- |
| blocked_by_pair_nulls | 23 | -0.000379563 | 0.555555556 |
| too_small_to_submit | 19 | -0.000049995 | 0.000000000 |

## Prefilter

- generated candidates: `512`
- old strict candidates: `489`
- info candidates: `23`
- null-evaluated candidates: `37`

| recipe | generated | old_strict | info | best_p90 | best_mean | median_move |
| --- | --- | --- | --- | --- | --- | --- |
| residualized_visible | 413 | 390 | 23 | -0.000507576 | -0.000747008 | 0.003606495 |
| microstack | 45 | 45 | 0 | -0.000807827 | -0.001178279 | 0.006385203 |
| microdiverse | 30 | 30 | 0 | -0.000440547 | -0.000629463 | 0.004582375 |
| microcash | 24 | 24 | 0 | -0.000423537 | -0.000625522 | 0.004469151 |

## Matched Null Governor

- public-free ready candidates: `0`

| recipe | evaluated | old_strict | ready | best_actual_p90 | best_null_strict | best_worst_mode |
| --- | --- | --- | --- | --- | --- | --- |
| residualized_visible | 20 | 11 | 0 | -0.000507576 | 0.000000000 | 0.750000000 |
| microstack | 9 | 9 | 0 | -0.000807827 | 0.611111111 | 0.750000000 |
| microdiverse | 5 | 5 | 0 | -0.000440547 | 0.722222222 | 1.000000000 |
| microcash | 3 | 3 | 0 | -0.000423537 | 0.722222222 | 0.750000000 |

| basename | recipe | n_parts | pairs | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | wrong_pair_p90_dominance | swap_targets_p90_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l0_50_kall_w1_50_2613cdc7.csv | residualized_visible | 1 | Q1_S1 | -0.000628328 | -0.000456292 | 0.500000000 | 0.833333333 | 0.861111111 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l0_50_k96_w1_50_2613cdc7.csv | residualized_visible | 1 | Q1_S1 | -0.000628328 | -0.000456292 | 0.555555556 | 0.833333333 | 0.777777778 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top8_w2_00_e0041a98.csv | microstack | 8 | Q1_S1,Q1_S3,S1_S2,S3_S4 | -0.001178279 | -0.000807827 | 0.611111111 | 0.888888889 | 0.944444444 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top8_w1_50_8ab8e42a.csv | microstack | 8 | Q1_S1,Q1_S3,S1_S2,S3_S4 | -0.000852075 | -0.000606110 | 0.666666667 | 0.888888889 | 0.888888889 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__all_controls_l0_50_kall_w1_50_7bf13c82.csv | residualized_visible | 1 | Q1_S1 | -0.000673921 | -0.000451151 | 0.666666667 | 0.666666667 | 0.611111111 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_50_k96_w1_50_e79791bf.csv | residualized_visible | 1 | Q1_S1 | -0.000710159 | -0.000504676 | 0.722222222 | 0.666666667 | 0.666666667 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top8_w1_25_30a3004a.csv | microstack | 8 | Q1_S1,Q1_S3,S1_S2,S3_S4 | -0.000692616 | -0.000497169 | 0.722222222 | 0.944444444 | 1.000000000 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__all_controls_l0_50_kall_w1_50_3163f496.csv | residualized_visible | 1 | Q1_S1 | -0.000743296 | -0.000473690 | 0.722222222 | 0.555555556 | 0.833333333 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_75_k96_w1_50_c0fdff07.csv | residualized_visible | 1 | Q1_S1 | -0.000661200 | -0.000460194 | 0.722222222 | 0.555555556 | 0.666666667 | 1.000000000 | 1.000000000 | 0.000000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microdiverse_top4_w2_00_e671661d.csv | microdiverse | 4 | Q1_S1,Q1_S3,S1_S2,S3_S4 | -0.000629463 | -0.000440547 | 0.722222222 | 1.000000000 | 0.944444444 | 1.000000000 | 1.000000000 | 1.000000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microcash_top2_w1_25_1b8e5784.csv | microcash | 2 | Q1_S1 | -0.000197290 | -0.000134932 | 0.722222222 | 0.888888889 | 0.888888889 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top6_w2_00_b173f856.csv | microstack | 6 | Q1_S1,Q1_S3,S1_S2 | -0.000908766 | -0.000615904 | 0.777777778 | 0.833333333 | 0.722222222 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l0_50_kall_w1_50_7da75d01.csv | residualized_visible | 1 | Q1_S1 | -0.000745684 | -0.000507576 | 0.777777778 | 0.944444444 | 0.944444444 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__all_controls_l0_50_k96_w1_50_897fc1d9.csv | residualized_visible | 1 | Q1_S1 | -0.000688287 | -0.000498196 | 0.777777778 | 0.777777778 | 0.666666667 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_50_k96_w1_50_e3fc9e5e.csv | residualized_visible | 1 | Q1_S1 | -0.000691453 | -0.000474615 | 0.777777778 | 0.833333333 | 0.777777778 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__all_controls_l0_50_k96_w1_50_f773eab2.csv | residualized_visible | 1 | Q1_S1 | -0.000663585 | -0.000470747 | 0.777777778 | 0.611111111 | 0.555555556 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_50_kall_w1_50_29a31bcb.csv | residualized_visible | 1 | Q1_S1 | -0.000747008 | -0.000459738 | 0.777777778 | 0.666666667 | 0.611111111 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top5_w2_00_3aa12fc7.csv | microstack | 5 | Q1_S1,Q1_S3,S1_S2 | -0.000665716 | -0.000438960 | 0.777777778 | 0.944444444 | 0.888888889 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top3_w2_00_a2e32ab2.csv | microstack | 3 | Q1_S1,S1_S2 | -0.000653380 | -0.000422804 | 0.777777778 | 0.944444444 | 0.833333333 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top3_w1_50_3c66bbec.csv | microstack | 3 | Q1_S1,S1_S2 | -0.000450053 | -0.000293604 | 0.777777778 | 0.888888889 | 0.833333333 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top2_w2_00_29a8926a.csv | microstack | 2 | Q1_S1 | -0.000370271 | -0.000247628 | 0.777777778 | 0.944444444 | 0.833333333 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microdiverse_top3_w1_50_a7b87c67.csv | microdiverse | 3 | Q1_S1,Q1_S3,S1_S2 | -0.000313989 | -0.000197570 | 0.777777778 | 0.944444444 | 1.000000000 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microdiverse_top2_w1_50_31820b9f.csv | microdiverse | 2 | Q1_S1,S1_S2 | -0.000310199 | -0.000193109 | 0.777777778 | 0.888888889 | 0.888888889 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microstack_top2_w1_50_5fa8971d.csv | microstack | 2 | Q1_S1 | -0.000252156 | -0.000170946 | 0.777777778 | 0.944444444 | 0.833333333 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microcash_top2_w1_50_5fa8971d.csv | microcash | 2 | Q1_S1 | -0.000252156 | -0.000170946 | 0.777777778 | 0.888888889 | 0.888888889 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microcash_top4_w1_50_a8f230fb.csv | microcash | 4 | Q1_S1,S1_S2 | -0.000625522 | -0.000423537 | 0.833333333 | 0.833333333 | 0.777777778 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microdiverse_top3_w2_00_fadb2d44.csv | microdiverse | 3 | Q1_S1,Q1_S3,S1_S2 | -0.000465203 | -0.000291509 | 0.833333333 | 1.000000000 | 0.944444444 | 1.000000000 | 1.000000000 | 1.000000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_microdiverse_top2_w2_00_aca1ecf6.csv | microdiverse | 2 | Q1_S1,S1_S2 | -0.000459862 | -0.000285090 | 0.833333333 | 1.000000000 | 0.944444444 | 1.000000000 | 1.000000000 | 1.000000000 | blocked_by_pair_micro_nulls |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__all_controls_l1_00_k32_w0_75_915cc5fb.csv | residualized_visible | 1 | Q1_S1 | -0.000100350 | -0.000030381 | 0.000000000 | 0.666666667 | 0.500000000 | 0.750000000 | 1.000000000 | 0.250000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l1_25_k96_w0_75_c650998d.csv | residualized_visible | 1 | Q1_S1 | -0.000089343 | -0.000049386 | 0.055555556 | 0.944444444 | 0.944444444 | 1.000000000 | 1.000000000 | 0.750000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_75_k32_w0_75_afa649b8.csv | residualized_visible | 1 | Q1_S1 | -0.000097678 | -0.000037572 | 0.055555556 | 0.833333333 | 0.666666667 | 0.750000000 | 1.000000000 | 0.750000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l1_25_k32_w0_75_3e369651.csv | residualized_visible | 1 | Q1_S1 | -0.000096053 | -0.000044030 | 0.111111111 | 0.833333333 | 0.833333333 | 1.000000000 | 1.000000000 | 0.500000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l1_25_kall_w0_75_c650998d.csv | residualized_visible | 1 | Q1_S1 | -0.000089343 | -0.000049386 | 0.138888889 | 0.861111111 | 0.861111111 | 1.000000000 | 1.000000000 | 0.250000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l1_25_k96_w0_75_47bfc7d9.csv | residualized_visible | 1 | Q1_S1 | -0.000081606 | -0.000037597 | 0.166666667 | 0.777777778 | 0.722222222 | 1.000000000 | 1.000000000 | 0.500000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l1_00_k32_w0_75_8ee0d609.csv | residualized_visible | 1 | Q1_S1 | -0.000109045 | -0.000033949 | 0.166666667 | 0.666666667 | 0.722222222 | 0.750000000 | 1.000000000 | 0.250000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_75_k32_w0_75_5d89ae36.csv | residualized_visible | 1 | Q1_S1 | -0.000112977 | -0.000046934 | 0.277777778 | 0.666666667 | 0.777777778 | 0.750000000 | 1.000000000 | 0.500000000 | too_small_to_submit |
| submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l1_25_k64_w0_75_151e6697.csv | residualized_visible | 1 | Q1_S1 | -0.000129095 | -0.000045052 | 0.277777778 | 0.666666667 | 0.611111111 | 0.750000000 | 1.000000000 | 0.250000000 | too_small_to_submit |

## Decision

- No E311 micro-combo or null-residualized pair action is public-free ready.
- If micro stacks remain too small or become null-common when visible, the visibility/null-rarity cliff is structural for the current pair translator.
- If residualized visible actions are still null-common, matched-null subtraction is not enough; a learned action-health target is needed.

## Outputs

- `analysis_outputs/e311_pair_micro_candidates.csv`
- `analysis_outputs/e311_pair_micro_selected.csv`
- `analysis_outputs/e311_pair_micro_governor.csv`
- `analysis_outputs/e311_pair_micro_scores.csv`
- `analysis_outputs/e311_pair_micro_null_map.csv`
- `analysis_outputs/e311_pair_micro_report.md`
