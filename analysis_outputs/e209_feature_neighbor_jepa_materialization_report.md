# E209 Feature-Neighbor JEPA Materialization Stress

## Purpose

Materialize only the E208 Q3/S4 operations and test whether the learned JEPA movement remains sane when grafted onto frontier tensors.

## Stage2 OOF/Subject/Geometry Summary

| combo | n_ops | targets | delta | subject_half_delta | subject_half_win_rate | geometry_delta | geometry_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3_center_s4_rank | 2 | Q3,S4 | -0.001370190 | -0.001394602 | 0.919230769 | -0.000978984 | 0.750000000 |
| q3_z_s4_rank | 2 | Q3,S4 | -0.001277709 | -0.001315720 | 0.900000000 | -0.001210888 | 0.875000000 |
| q3_center_c010_s4_rank | 2 | Q3,S4 | -0.001272724 | -0.001297106 | 0.900000000 | -0.000794598 | 0.750000000 |
| q3_rank_s4_rank | 2 | Q3,S4 | -0.001271878 | -0.001312582 | 0.896153846 | -0.001299943 | 1.000000000 |
| q3_center | 1 | Q3 | -0.000922510 | -0.000917580 | 0.930769231 | -0.000339009 | 0.750000000 |
| q3_z | 1 | Q3 | -0.000830029 | -0.000838698 | 0.911538462 | -0.000570913 | 0.875000000 |
| q3_center_c010 | 1 | Q3 | -0.000825045 | -0.000820084 | 0.930769231 | -0.000154623 | 0.500000000 |
| q3_rank | 1 | Q3 | -0.000824199 | -0.000835560 | 0.915384615 | -0.000659968 | 1.000000000 |
| s4_rank | 1 | S4 | -0.000447679 | -0.000477022 | 0.800000000 | -0.000639975 | 0.875000000 |

## Frontier Stress

| combo | anchor | scale | e209_frontier_gate | survival_score | vs_e95_expected_delta_focus_mean | vs_e95_cells_for_2e6_guard | vs_e95_top1_over_abs_expected | bad_span_energy | max_bad_axis | max_bad_cos | mean_abs_logit_step_vs_anchor | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_center_c010_s4_rank | e154 | 0.250000000 | True | 0.013853189 | -0.000217865 | 1 | 0.361098020 | 0.313520152 | ordinal | 0.202004727 | 0.007873679 | submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv |
| s4_rank | e154 | 0.750000000 | True | 0.012660227 | -0.000218027 | 1 | 0.637509996 | 0.115301389 | ordinal | 0.090785337 | 0.011354327 | submission_e209_jepa_s4_rank_e154_s0p75_030e88de.csv |
| q3_center_c010_s4_rank | e95 | 0.250000000 | True | 0.012445288 | -0.000189667 | 1 | 0.414782960 | 0.292165174 | ordinal | 0.155737509 | 0.007873679 | submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv |
| s4_rank | e95 | 0.750000000 | True | 0.011175112 | -0.000188668 | 1 | 0.671883799 | 0.097401574 | ordinal | 0.060514995 | 0.011354327 | submission_e209_jepa_s4_rank_e95_s0p75_0ed14a13.csv |
| s4_rank | e154 | 0.500000000 | True | 0.011058887 | -0.000184858 | 1 | 0.523319535 | 0.129633202 | ordinal | 0.104497596 | 0.007569551 |  |
| s4_rank | e95 | 0.500000000 | True | 0.009571873 | -0.000155326 | 1 | 0.544075500 | 0.097401574 | ordinal | 0.060514995 | 0.007569551 |  |
| s4_rank | e154 | 0.250000000 | True | 0.007931351 | -0.000122074 | 1 | 0.446330569 | 0.175932649 | ordinal | 0.138110361 | 0.003784776 |  |
| q3_center_c010 | e154 | 0.250000000 | True | 0.007430138 | -0.000125629 | 1 | 0.626217209 | 0.365615375 | ordinal | 0.206858038 | 0.004088903 |  |
| s4_rank | e95 | 0.250000000 | True | 0.006446731 | -0.000092382 | 1 | 0.457388020 | 0.097401574 | ordinal | 0.060514995 | 0.003784776 |  |
| q3_center_c010 | e95 | 0.250000000 | True | 0.005944227 | -0.000097285 | 1 | 0.808660290 | 0.349986270 | ordinal | 0.151805209 | 0.004088903 |  |
| q3_center_c010_s4_rank | e154 | 0.750000000 | False | 0.021039865 | -0.000363060 | 1 | 0.650065196 | 0.299792654 | ordinal | 0.173716753 | 0.023621037 |  |
| q3_center_c010_s4_rank | e95 | 0.750000000 | False | 0.019773207 | -0.000338204 | 1 | 0.697839989 | 0.292165174 | ordinal | 0.155737509 | 0.023621037 |  |
| q3_center_c010_s4_rank | e154 | 0.500000000 | False | 0.019419689 | -0.000329155 | 1 | 0.478016143 | 0.303490158 | ordinal | 0.181787950 | 0.015747358 |  |
| q3_center_c010_s4_rank | e154 | 1.000000000 | False | 0.018671918 | -0.000319063 | 1 | 0.986273740 | 0.297903494 | ordinal | 0.169442818 | 0.031494716 |  |
| q3_center_c010_s4_rank | e95 | 0.500000000 | False | 0.018082849 | -0.000302618 | 1 | 0.519934774 | 0.292165174 | ordinal | 0.155737509 | 0.015747358 |  |
| q3_center_c010_s4_rank | e95 | 1.000000000 | False | 0.017475750 | -0.000295911 | 1 | 1.063438573 | 0.292165174 | ordinal | 0.155737509 | 0.031494716 |  |
| s4_rank | e154 | 1.000000000 | False | 0.012740174 | -0.000221436 | 1 | 0.818515545 | 0.109111948 | ordinal | 0.083527447 | 0.015139102 |  |
| q3_center_c010_s4_rank | mixmin | 0.750000000 | False | 0.012285652 | -0.000193661 | 1 | 1.218685140 | 0.334045362 | e72 | 0.181184903 | 0.023621037 |  |
| s4_rank | e95 | 1.000000000 | False | 0.011251393 | -0.000192266 | 1 | 0.879082386 | 0.097401574 | ordinal | 0.060514995 | 0.015139102 |  |
| q3_center_c010_s4_rank | mixmin | 0.500000000 | False | 0.010548272 | -0.000158075 | 1 | 0.995358623 | 0.372468303 | e72 | 0.247264070 | 0.015747358 |  |
| q3_center_c010_s4_rank | mixmin | 1.000000000 | False | 0.009740875 | -0.000151368 | 1 | 2.078923299 | 0.317889720 | ordinal | 0.153005037 | 0.031494716 |  |
| q3_center_c010 | e154 | 0.500000000 | False | 0.009728816 | -0.000174135 | 1 | 0.903563063 | 0.360421751 | ordinal | 0.184188429 | 0.008177807 |  |
| q3_center_c010 | e154 | 0.750000000 | False | 0.009545451 | -0.000174870 | 1 | 1.349644210 | 0.357520482 | ordinal | 0.174437593 | 0.012266710 |  |
| q3_center_c010 | e95 | 0.500000000 | False | 0.008314792 | -0.000147292 | 1 | 1.068226753 | 0.349986270 | ordinal | 0.151805209 | 0.008177807 |  |

## Selected Submissions

| combo | anchor | scale | e209_frontier_gate | survival_score | vs_e95_expected_delta_focus_mean | vs_e95_cells_for_2e6_guard | vs_e95_top1_over_abs_expected | bad_span_energy | max_bad_axis | max_bad_cos | mean_abs_logit_step_vs_anchor | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_center_c010_s4_rank | e154 | 0.250000000 | True | 0.013853189 | -0.000217865 | 1 | 0.361098020 | 0.313520152 | ordinal | 0.202004727 | 0.007873679 | submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv |
| s4_rank | e154 | 0.750000000 | True | 0.012660227 | -0.000218027 | 1 | 0.637509996 | 0.115301389 | ordinal | 0.090785337 | 0.011354327 | submission_e209_jepa_s4_rank_e154_s0p75_030e88de.csv |
| q3_center_c010_s4_rank | e95 | 0.250000000 | True | 0.012445288 | -0.000189667 | 1 | 0.414782960 | 0.292165174 | ordinal | 0.155737509 | 0.007873679 | submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv |
| s4_rank | e95 | 0.750000000 | True | 0.011175112 | -0.000188668 | 1 | 0.671883799 | 0.097401574 | ordinal | 0.060514995 | 0.011354327 | submission_e209_jepa_s4_rank_e95_s0p75_0ed14a13.csv |

## Decision

- Best materialized candidate: `submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv`. It tests whether the E208 Q3/S4 JEPA residual can improve the `e154` frontier tensor at scale `0.25`.
- This remains a hypothesis submission, not proof of a 0.54 path. Public feedback should be read as a Q3/S4 JEPA-translation sensor.
