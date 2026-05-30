# E300 S4 Mean-Dominance Rescue

Public LB는 사용하지 않았다. E299 closest S4 후보의 row/sign/mask placement를 바꿔 mean dominance 실패를 구조적으로 고칠 수 있는지 검사했다.

## Counts

- row probes: `50`
- generated candidates: `1305`
- old strict prefilter candidates: `199`
- null-evaluated candidates: `120`
- public-free ready candidates: `1`

## Best Row Probes

| row_idx | subject_id | sleep_date | s4_delta | sign | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | row_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 154 | id07 | 2024-07-16 | 0.038800000 | pos | -0.000009712 | -0.000002638 | 0.911764706 | -0.000007939 |
| 2 | id01 | 2024-08-02 | 0.038800000 | pos | -0.000009668 | -0.000002638 | 0.911764706 | -0.000007894 |
| 16 | id01 | 2024-09-04 | 0.038800000 | pos | -0.000009341 | -0.000002633 | 0.911764706 | -0.000007562 |
| 17 | id01 | 2024-09-05 | 0.038800000 | pos | -0.000009200 | -0.000002623 | 0.911764706 | -0.000007411 |
| 173 | id07 | 2024-08-23 | 0.038800000 | pos | -0.000008372 | -0.000001280 | 0.941176471 | -0.000006711 |
| 15 | id01 | 2024-09-03 | 0.038800000 | pos | -0.000007582 | -0.000002016 | 0.941176471 | -0.000006657 |
| 14 | id01 | 2024-09-02 | 0.038800000 | pos | -0.000007266 | -0.000002163 | 0.911764706 | -0.000005018 |
| 172 | id07 | 2024-08-21 | 0.038800000 | pos | -0.000006842 | -0.000002124 | 0.911764706 | -0.000004554 |
| 155 | id07 | 2024-07-17 | 0.038800000 | pos | -0.000006837 | -0.000002122 | 0.911764706 | -0.000004547 |
| 178 | id07 | 2024-08-29 | 0.038800000 | pos | -0.000006830 | -0.000002118 | 0.911764706 | -0.000004536 |
| 13 | id01 | 2024-08-17 | 0.038800000 | pos | -0.000006809 | -0.000002107 | 0.911764706 | -0.000004504 |
| 179 | id07 | 2024-08-30 | 0.038800000 | pos | -0.000006805 | -0.000002106 | 0.911764706 | -0.000004499 |
| 58 | id02 | 2024-10-16 | 0.038800000 | pos | -0.000006153 | -0.000001186 | 0.941176471 | -0.000004398 |
| 169 | id07 | 2024-08-17 | 0.038800000 | pos | -0.000006728 | -0.000002066 | 0.911764706 | -0.000004383 |
| 171 | id07 | 2024-08-20 | 0.038800000 | pos | -0.000006722 | -0.000002063 | 0.911764706 | -0.000004373 |
| 177 | id07 | 2024-08-28 | 0.038800000 | pos | -0.000006674 | -0.000002039 | 0.911764706 | -0.000004301 |
| 176 | id07 | 2024-08-27 | 0.038800000 | pos | -0.000006649 | -0.000002026 | 0.911764706 | -0.000004263 |
| 3 | id01 | 2024-08-03 | 0.038800000 | pos | -0.000006628 | -0.000002016 | 0.911764706 | -0.000004232 |
| 181 | id07 | 2024-09-02 | 0.038800000 | pos | -0.000006625 | -0.000002014 | 0.911764706 | -0.000004227 |
| 18 | id01 | 2024-09-07 | 0.038800000 | pos | -0.000006363 | -0.000001880 | 0.911764706 | -0.000003831 |

## Family Summary

| mask_name | transform | n | ready | old_strict | min_null | best_mean_dom | best_p90 | best_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| drop_dateblock_id07_b9 | raw | 2 | 1 | 1 | 0.000000000 | 0.714285714 | -0.000051307 | -0.000161310 |
| drop_subject_id01_neg | abs_pos | 4 | 0 | 4 | 0.952380952 | 0.476190476 | -0.000094393 | -0.000319831 |
| all | abs_pos | 4 | 0 | 4 | 1.000000000 | 0.428571429 | -0.000094964 | -0.000321449 |
| drop_dateblock_id07_b6 | abs_pos | 4 | 0 | 4 | 1.000000000 | 0.428571429 | -0.000094278 | -0.000313153 |
| drop_dateblock_id03_b3 | abs_pos | 4 | 0 | 4 | 1.000000000 | 0.333333333 | -0.000093798 | -0.000313004 |
| drop_subject_id07_neg | abs_pos | 4 | 0 | 4 | 1.000000000 | 0.285714286 | -0.000094746 | -0.000318842 |
| drop_dateblock_id08_b5 | abs_pos | 3 | 0 | 3 | 0.952380952 | 0.285714286 | -0.000090511 | -0.000303902 |
| drop_dateblock_id03_b4 | abs_pos | 3 | 0 | 3 | 1.000000000 | 0.619047619 | -0.000088157 | -0.000305843 |
| drop_dateblock_id02_b10 | abs_pos | 3 | 0 | 3 | 1.000000000 | 0.523809524 | -0.000090579 | -0.000311789 |
| drop_dateblock_id01_b4 | abs_pos | 3 | 0 | 3 | 1.000000000 | 0.428571429 | -0.000088080 | -0.000293976 |
| drop_dateblock_id03_b7 | abs_pos | 3 | 0 | 3 | 1.000000000 | 0.380952381 | -0.000089033 | -0.000307028 |
| drop_subject_id08 | abs_pos | 3 | 0 | 3 | 1.000000000 | 0.333333333 | -0.000087807 | -0.000296460 |
| drop_dateblock_id01_b8 | abs_pos | 3 | 0 | 3 | 1.000000000 | 0.190476190 | -0.000087903 | -0.000284348 |
| drop_subject_id03_neg | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.571428571 | -0.000082283 | -0.000287111 |
| drop_dateblock_id02_b5 | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.428571429 | -0.000087463 | -0.000302249 |
| drop_dateblock_id07_b9 | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.428571429 | -0.000086612 | -0.000297904 |
| drop_subject_id03_pos | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.428571429 | -0.000084745 | -0.000292992 |
| drop_subject_id02 | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.428571429 | -0.000082928 | -0.000285463 |
| drop_dateblock_id07_b10 | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.380952381 | -0.000081886 | -0.000280720 |
| drop_dateblock_id03_b6 | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.333333333 | -0.000085968 | -0.000297125 |
| drop_dateblock_id07_b5 | abs_pos | 2 | 0 | 2 | 1.000000000 | 0.238095238 | -0.000086248 | -0.000284842 |
| drop_dateblock_id01_b4 | raw | 3 | 0 | 1 | 0.000000000 | 0.666666667 | -0.000051611 | -0.000160618 |
| drop_dateblock_id08_b5 | raw | 2 | 0 | 1 | 0.000000000 | 0.619047619 | -0.000063374 | -0.000203812 |
| drop_dateblock_id03_b3 | raw | 2 | 0 | 1 | 0.000000000 | 0.619047619 | -0.000059400 | -0.000185257 |
| abs_top35 | raw | 3 | 0 | 1 | 0.000000000 | 0.619047619 | -0.000054171 | -0.000168823 |
| drop_dateblock_id02_b5 | raw | 2 | 0 | 1 | 0.000000000 | 0.619047619 | -0.000052159 | -0.000165655 |
| drop_subject_id08 | raw | 2 | 0 | 1 | 0.000000000 | 0.571428571 | -0.000064233 | -0.000214552 |
| drop_dateblock_id02_b10 | raw | 3 | 0 | 1 | 0.000000000 | 0.571428571 | -0.000055274 | -0.000175195 |
| drop_subject_id03_neg | raw | 2 | 0 | 1 | 0.000000000 | 0.523809524 | -0.000068975 | -0.000223979 |
| all | raw | 2 | 0 | 1 | 0.000000000 | 0.523809524 | -0.000059273 | -0.000184855 |

## Best Governor Rows

| mask_name | transform | multiplier | nonzero_rows | pos_rows | neg_rows | old_strict_promote | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | worst_mode_mean_dominance | public_free_submission_ready | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| drop_dateblock_id07_b9 | raw | 1.160000000 | 47 | 33 | 14 | True | -0.000161310 | -0.000051307 | 0.095238095 | 0.904761905 | 0.714285714 | 0.857142857 | 0.571428571 | True | submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv |
| abs_top35 | raw | 1.160000000 | 35 | 28 | 7 | True | -0.000168823 | -0.000054171 | 0.190476190 | 1.000000000 | 0.428571429 | 1.000000000 | 0.142857143 | False | submission_e300_s4mean_abs_top35_raw_m1p16_76734941.csv |
| drop_dateblock_id02_b5 | raw | 1.160000000 | 47 | 33 | 14 | True | -0.000165655 | -0.000052159 | 0.285714286 | 0.857142857 | 0.523809524 | 0.571428571 | 0.285714286 | False | submission_e300_s4mean_drop_dateblock_id02_b5_raw_m1p16_7cdd0efe.csv |
| drop_dateblock_id01_b4 | raw | 1.160000000 | 46 | 33 | 13 | True | -0.000160618 | -0.000051611 | 0.380952381 | 0.857142857 | 0.666666667 | 0.714285714 | 0.285714286 | False | submission_e300_s4mean_drop_dateblock_id01_b4_raw_m1p16_67acd4d3.csv |
| drop_dateblock_id03_b6 | raw | 1.160000000 | 45 | 32 | 13 | True | -0.000175520 | -0.000051942 | 0.428571429 | 0.619047619 | 0.761904762 | 0.142857143 | 0.428571429 | False | submission_e300_s4mean_drop_dateblock_id03_b6_raw_m1p16_e2496604.csv |
| drop_dateblock_id02_b10 | raw | 1.160000000 | 48 | 34 | 14 | True | -0.000175195 | -0.000055274 | 0.428571429 | 0.857142857 | 0.476190476 | 0.571428571 | 0.000000000 | False | submission_e300_s4mean_drop_dateblock_id02_b10_raw_m1p16_04e140b6.csv |
| drop_subject_id01_neg | raw | 1.160000000 | 49 | 36 | 13 | True | -0.000186473 | -0.000059795 | 0.666666667 | 0.904761905 | 0.571428571 | 0.857142857 | 0.142857143 | False | submission_e300_s4mean_drop_subject_id01_neg_raw_m1p16_2cdc3630.csv |
| drop_dateblock_id07_b6 | raw | 1.160000000 | 47 | 35 | 12 | True | -0.000181770 | -0.000058323 | 0.714285714 | 0.809523810 | 0.476190476 | 0.428571429 | 0.142857143 | False | submission_e300_s4mean_drop_dateblock_id07_b6_raw_m1p16_92d1699f.csv |
| drop_dateblock_id03_b3 | raw | 1.160000000 | 48 | 35 | 13 | True | -0.000185257 | -0.000059400 | 0.714285714 | 0.904761905 | 0.428571429 | 0.714285714 | 0.000000000 | False | submission_e300_s4mean_drop_dateblock_id03_b3_raw_m1p16_5bf344bc.csv |
| all | raw | 1.160000000 | 50 | 36 | 14 | True | -0.000184855 | -0.000059273 | 0.714285714 | 0.952380952 | 0.428571429 | 0.857142857 | 0.142857143 | False | submission_e300_s4mean_all_raw_m1p16_d2582178.csv |
| probe_top6_per_subject | abs_pos | 1.160000000 | 27 | 27 | 0 | True | -0.000198852 | -0.000054302 | 0.761904762 | 0.523809524 | 0.809523810 | 0.285714286 | 0.714285714 | False | submission_e300_s4mean_probe_top6_per_subject_abs_pos_m1p16_7650bdf9.csv |
| drop_subject_id03 | raw | 1.160000000 | 36 | 30 | 6 | True | -0.000195522 | -0.000058756 | 0.761904762 | 0.857142857 | 0.619047619 | 0.571428571 | 0.285714286 | False | submission_e300_s4mean_drop_subject_id03_raw_m1p16_7bfc81c8.csv |
| drop_subject_id07_neg | raw | 1.160000000 | 48 | 36 | 12 | True | -0.000187459 | -0.000059877 | 0.761904762 | 0.809523810 | 0.571428571 | 0.571428571 | 0.285714286 | False | submission_e300_s4mean_drop_subject_id07_neg_raw_m1p16_6a041b50.csv |
| probe_top28 | raw | 1.160000000 | 28 | 28 | 0 | True | -0.000220881 | -0.000061760 | 0.761904762 | 0.857142857 | 0.523809524 | 0.714285714 | 0.285714286 | False | submission_e300_s4mean_probe_top28_raw_m1p16_e171fcef.csv |
| drop_dateblock_id03_b7 | raw | 1.160000000 | 47 | 35 | 12 | True | -0.000187429 | -0.000060114 | 0.761904762 | 0.904761905 | 0.428571429 | 0.714285714 | 0.142857143 | False | submission_e300_s4mean_drop_dateblock_id03_b7_raw_m1p16_10bf7233.csv |
| drop_dateblock_id08_b5 | raw | 1.160000000 | 48 | 36 | 12 | True | -0.000203812 | -0.000063374 | 0.809523810 | 0.952380952 | 0.428571429 | 0.857142857 | 0.142857143 | False | submission_e300_s4mean_drop_dateblock_id08_b5_raw_m1p16_70415ba6.csv |
| probe_mix_pos16_neg16 | abs_pos | 1.160000000 | 30 | 30 | 0 | True | -0.000203444 | -0.000053981 | 0.857142857 | 0.428571429 | 0.761904762 | 0.285714286 | 0.571428571 | False | submission_e300_s4mean_probe_mix_pos16_neg16_abs_pos_m1p16_d3136eba.csv |
| probe_top28 | abs_pos | 1.160000000 | 28 | 28 | 0 | True | -0.000220881 | -0.000061760 | 0.904761905 | 0.809523810 | 0.619047619 | 0.571428571 | 0.285714286 | False | submission_e300_s4mean_probe_top28_abs_pos_m1p16_e171fcef.csv |
| probe_mix_pos20_neg20 | abs_pos | 1.160000000 | 34 | 34 | 0 | True | -0.000233890 | -0.000064932 | 0.904761905 | 0.666666667 | 0.476190476 | 0.571428571 | 0.428571429 | False | submission_e300_s4mean_probe_mix_pos20_neg20_abs_pos_m1p16_ba51cc1d.csv |
| drop_subject_id08 | raw | 1.160000000 | 47 | 36 | 11 | True | -0.000214552 | -0.000064233 | 0.904761905 | 0.857142857 | 0.476190476 | 0.714285714 | 0.142857143 | False | submission_e300_s4mean_drop_subject_id08_raw_m1p16_091b6182.csv |
| drop_subject_id03_neg | raw | 1.160000000 | 42 | 36 | 6 | True | -0.000223979 | -0.000068975 | 0.952380952 | 0.857142857 | 0.523809524 | 0.714285714 | 0.428571429 | False | submission_e300_s4mean_drop_subject_id03_neg_raw_m1p16_85c37cc7.csv |
| drop_subject_id01_neg | abs_pos | 1.080000000 | 49 | 49 | 0 | True | -0.000298756 | -0.000087337 | 0.952380952 | 0.809523810 | 0.476190476 | 0.428571429 | 0.285714286 | False | submission_e300_s4mean_drop_subject_id01_neg_abs_pos_m1p08_74409132.csv |
| pos_only | raw | 1.160000000 | 36 | 36 | 0 | True | -0.000257898 | -0.000074337 | 0.952380952 | 0.952380952 | 0.476190476 | 0.857142857 | 0.285714286 | False | submission_e300_s4mean_pos_only_raw_m1p16_5ce5c347.csv |
| drop_dateblock_id03_b4 | raw | 1.160000000 | 46 | 36 | 10 | True | -0.000201880 | -0.000064739 | 0.952380952 | 1.000000000 | 0.380952381 | 1.000000000 | 0.000000000 | False | submission_e300_s4mean_drop_dateblock_id03_b4_raw_m1p16_a44c0c1d.csv |
| drop_subject_id01 | abs_pos | 1.160000000 | 40 | 40 | 0 | True | -0.000240625 | -0.000075677 | 0.952380952 | 0.809523810 | 0.333333333 | 0.428571429 | 0.000000000 | False | submission_e300_s4mean_drop_subject_id01_abs_pos_m1p16_4ba4ef69.csv |
| drop_dateblock_id08_b5 | abs_pos | 1.080000000 | 48 | 48 | 0 | True | -0.000283785 | -0.000083797 | 0.952380952 | 1.000000000 | 0.238095238 | 1.000000000 | 0.142857143 | False | submission_e300_s4mean_drop_dateblock_id08_b5_abs_pos_m1p08_6928f9cd.csv |
| drop_subject_id07_pos | abs_pos | 1.160000000 | 35 | 35 | 0 | True | -0.000207199 | -0.000061598 | 0.952380952 | 0.714285714 | 0.190476190 | 0.571428571 | 0.000000000 | False | submission_e300_s4mean_drop_subject_id07_pos_abs_pos_m1p16_e970b546.csv |
| drop_subject_id07 | abs_pos | 1.160000000 | 33 | 33 | 0 | True | -0.000204593 | -0.000061380 | 0.952380952 | 0.857142857 | 0.190476190 | 0.857142857 | 0.000000000 | False | submission_e300_s4mean_drop_subject_id07_abs_pos_m1p16_d8252d9d.csv |
| abs_top35 | abs_pos | 1.160000000 | 35 | 35 | 0 | True | -0.000260264 | -0.000076992 | 1.000000000 | 0.952380952 | 0.619047619 | 0.857142857 | 0.428571429 | False | submission_e300_s4mean_abs_top35_abs_pos_m1p16_397634f3.csv |
| drop_dateblock_id03_b4 | abs_pos | 1.000000000 | 46 | 46 | 0 | True | -0.000265267 | -0.000075125 | 1.000000000 | 0.952380952 | 0.619047619 | 0.857142857 | 0.285714286 | False | submission_e300_s4mean_drop_dateblock_id03_b4_abs_pos_m1p00_ee919b1f.csv |

## Interpretation

- A public-free ready S4 mean-dominance rescue exists. Inspect duplicate risk and movement anatomy before any public submission.

## Outputs

- `analysis_outputs/e300_s4_mean_dominance_row_probes.csv`
- `analysis_outputs/e300_s4_mean_dominance_candidates.csv`
- `analysis_outputs/e300_s4_mean_dominance_prefilter.csv`
- `analysis_outputs/e300_s4_mean_dominance_governor.csv`
- `analysis_outputs/e300_s4_mean_dominance_report.md`
