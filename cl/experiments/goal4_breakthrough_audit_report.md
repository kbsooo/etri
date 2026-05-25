# Goal4 breakthrough audit

목표 네 가지를 같은 산출물에서 검증했다. 이 리포트는 submission 생성 없이 train/fold/test 구조만 사용한다.


## 1. Sleep boundary / rest-event features

음수는 subject_prior anchor보다 logloss가 좋아진 것이다.

| family | target | anchor | new_boundary_rest | old_plus_new_sleep | old_sleep |
|---|---|---|---|---|---|
| chrono_tail | Q1 | 0.0000 | 0.0094 | 0.0346 | 0.0345 |
| chrono_tail | Q2 | 0.0000 | 0.1015 | 0.0840 | 0.0135 |
| chrono_tail | Q3 | 0.0000 | 0.0996 | 0.1206 | 0.0444 |
| chrono_tail | S1 | 0.0000 | 0.0187 | 0.0165 | 0.0064 |
| chrono_tail | S2 | 0.0000 | 0.0215 | 0.0260 | 0.0055 |
| chrono_tail | S3 | 0.0000 | 0.0261 | 0.0397 | 0.0149 |
| chrono_tail | S4 | 0.0000 | 0.0077 | 0.0043 | -0.0160 |
| hole_v1 | Q1 | 0.0000 | 0.0155 | 0.0176 | 0.0191 |
| hole_v1 | Q2 | 0.0000 | 0.0481 | 0.0431 | 0.0035 |
| hole_v1 | Q3 | 0.0000 | 0.0605 | 0.0672 | 0.0081 |
| hole_v1 | S1 | 0.0000 | 0.0095 | 0.0140 | -0.0062 |
| hole_v1 | S2 | 0.0000 | 0.0183 | 0.0195 | -0.0064 |
| hole_v1 | S3 | 0.0000 | 0.0347 | 0.0430 | -0.0160 |
| hole_v1 | S4 | 0.0000 | 0.0354 | 0.0353 | -0.0090 |
| mirror_v1 | Q1 | 0.0000 | 0.0253 | 0.0512 | 0.0489 |
| mirror_v1 | Q2 | 0.0000 | 0.0922 | 0.0774 | 0.0425 |
| mirror_v1 | Q3 | 0.0000 | 0.0976 | 0.1118 | 0.0585 |
| mirror_v1 | S1 | 0.0000 | 0.0015 | 0.0004 | -0.0042 |
| mirror_v1 | S2 | 0.0000 | 0.0368 | 0.0468 | -0.0045 |
| mirror_v1 | S3 | 0.0000 | 0.0492 | 0.0498 | -0.0004 |
| mirror_v1 | S4 | 0.0000 | 0.0270 | 0.0253 | -0.0318 |


핵심 판정: `new_boundary_rest`가 모든 target에 좋은 feature라는 증거는 아니며, target/fold별 선택 feature로 다뤄야 한다. 특히 Q/S 전체 평균 개선보다 Q2/Q3 transition 관련 top feature가 더 중요하다.


## 2. Q/S two-factor measurement model

| family | target | anchor | one_factor_blend | one_factor_neighbor | two_factor_qs_blend | two_factor_qs_neighbor |
|---|---|---|---|---|---|---|
| chrono_tail | Q1 | 0.0000 | 0.0000 | 0.1005 | 0.0000 | 0.1183 |
| chrono_tail | Q2 | 0.0000 | 0.0000 | 0.0320 | 0.0000 | 0.1980 |
| chrono_tail | Q3 | 0.0000 | 0.0000 | 0.1263 | 0.0000 | 0.3271 |
| chrono_tail | S1 | 0.0000 | 0.0000 | 0.1011 | 0.0000 | 0.0918 |
| chrono_tail | S2 | 0.0000 | 0.0000 | 0.0549 | 0.0000 | 0.0817 |
| chrono_tail | S3 | 0.0000 | 0.0000 | 0.1289 | 0.0000 | 0.1610 |
| chrono_tail | S4 | 0.0000 | 0.0000 | 0.0284 | 0.0000 | 0.0307 |
| hole_v1 | Q1 | 0.0000 | -0.0002 | 0.0286 | -0.0134 | 0.0161 |
| hole_v1 | Q2 | 0.0000 | -0.0241 | -0.0138 | -0.0255 | 0.0015 |
| hole_v1 | Q3 | 0.0000 | -0.0012 | 0.0205 | -0.0071 | 0.0438 |
| hole_v1 | S1 | 0.0000 | -0.0133 | -0.0162 | -0.0108 | -0.0071 |
| hole_v1 | S2 | 0.0000 | 0.0135 | 0.0130 | 0.0035 | 0.0197 |
| hole_v1 | S3 | 0.0000 | 0.0266 | -0.0102 | 0.0167 | -0.0025 |
| hole_v1 | S4 | 0.0000 | 0.0198 | 0.0318 | 0.0211 | 0.0662 |
| mirror_v1 | Q1 | 0.0000 | 0.0041 | 0.0516 | -0.0018 | 0.0598 |
| mirror_v1 | Q2 | 0.0000 | -0.0226 | 0.1146 | -0.0173 | 0.1995 |
| mirror_v1 | Q3 | 0.0000 | -0.0037 | 0.0578 | -0.0063 | 0.1497 |
| mirror_v1 | S1 | 0.0000 | -0.0026 | -0.0063 | -0.0024 | 0.0019 |
| mirror_v1 | S2 | 0.0000 | 0.0096 | 0.0290 | 0.0020 | 0.0223 |
| mirror_v1 | S3 | 0.0000 | 0.0127 | 0.0102 | 0.0050 | 0.0257 |
| mirror_v1 | S4 | 0.0000 | 0.0040 | -0.0126 | 0.0034 | 0.0068 |


Two-factor가 one-factor보다 더 나은지 직접 비교:

| family | target | two_minus_one_delta |
|---|---|---|
| chrono_tail | Q1 | 0.0179 |
| chrono_tail | Q2 | 0.1660 |
| chrono_tail | Q3 | 0.2008 |
| chrono_tail | S1 | -0.0093 |
| chrono_tail | S2 | 0.0268 |
| chrono_tail | S3 | 0.0320 |
| chrono_tail | S4 | 0.0023 |
| hole_v1 | Q1 | -0.0125 |
| hole_v1 | Q2 | 0.0153 |
| hole_v1 | Q3 | 0.0232 |
| hole_v1 | S1 | 0.0091 |
| hole_v1 | S2 | 0.0067 |
| hole_v1 | S3 | 0.0077 |
| hole_v1 | S4 | 0.0343 |
| mirror_v1 | Q1 | 0.0082 |
| mirror_v1 | Q2 | 0.0849 |
| mirror_v1 | Q3 | 0.0919 |
| mirror_v1 | S1 | 0.0082 |
| mirror_v1 | S2 | -0.0068 |
| mirror_v1 | S3 | 0.0155 |
| mirror_v1 | S4 | 0.0194 |


Fold-safe blend model 비교(inside-hole에서만 이동, tail은 anchor 고정):

| family | target | one_factor_blend | two_factor_qs_blend | two_blend_minus_one_blend |
|---|---|---|---|---|
| chrono_tail | Q1 | 0.0000 | 0.0000 | 0.0000 |
| chrono_tail | Q2 | 0.0000 | 0.0000 | 0.0000 |
| chrono_tail | Q3 | 0.0000 | 0.0000 | 0.0000 |
| chrono_tail | S1 | 0.0000 | 0.0000 | 0.0000 |
| chrono_tail | S2 | 0.0000 | 0.0000 | 0.0000 |
| chrono_tail | S3 | 0.0000 | 0.0000 | 0.0000 |
| chrono_tail | S4 | 0.0000 | 0.0000 | 0.0000 |
| hole_v1 | Q1 | -0.0002 | -0.0134 | -0.0133 |
| hole_v1 | Q2 | -0.0241 | -0.0255 | -0.0014 |
| hole_v1 | Q3 | -0.0012 | -0.0071 | -0.0059 |
| hole_v1 | S1 | -0.0133 | -0.0108 | 0.0025 |
| hole_v1 | S2 | 0.0135 | 0.0035 | -0.0100 |
| hole_v1 | S3 | 0.0266 | 0.0167 | -0.0099 |
| hole_v1 | S4 | 0.0198 | 0.0211 | 0.0013 |
| mirror_v1 | Q1 | 0.0041 | -0.0018 | -0.0060 |
| mirror_v1 | Q2 | -0.0226 | -0.0173 | 0.0053 |
| mirror_v1 | Q3 | -0.0037 | -0.0063 | -0.0026 |
| mirror_v1 | S1 | -0.0026 | -0.0024 | 0.0002 |
| mirror_v1 | S2 | 0.0096 | 0.0020 | -0.0076 |
| mirror_v1 | S3 | 0.0127 | 0.0050 | -0.0077 |
| mirror_v1 | S4 | 0.0040 | 0.0034 | -0.0006 |


Measurement loadings:

| target | factor1_loading | factor2_loading |
|---|---|---|
| Q1 | 0.5006 | -0.0381 |
| Q2 | 0.2683 | 0.6490 |
| Q3 | 0.2612 | 0.6136 |
| S1 | 0.4570 | -0.0973 |
| S2 | 0.4654 | -0.3013 |
| S3 | 0.0810 | -0.1434 |
| S4 | 0.4209 | -0.2828 |
| explained_variance_ratio | 0.2619 | 0.2102 |

## 3. Raw hour-level transition events

AUC는 방향을 뒤집어도 같은 신호면 높은 값으로 계산했다(`auc_abs`).

| event | feature | auc_abs | mean_event | mean_stable | delta_event_minus_stable | n_event |
|---|---|---|---|---|---|---|
| Q2_down | g4_morning_06_10_screen_use_sum_h_rz_mean__prev_delta | 0.6098 | 0.1385 | -0.0362 | 0.1747 | 75 |
| Q2_down | g4_morning_06_10_wlight_max_h_rz_mean__prev_delta | 0.6087 | 0.2085 | -0.0639 | 0.2724 | 75 |
| Q2_down | g4_h09_mlight_max_h_rz | 0.5965 | 0.3693 | 0.1432 | 0.2260 | 75 |
| Q2_down | g4_rest_block_score_mean | 0.5964 | 0.7273 | 0.6984 | 0.0289 | 75 |
| Q2_down | g4_morning_06_10_wlight_max_h_rz_mean | 0.5956 | 0.0357 | -0.1038 | 0.1395 | 75 |
| Q2_down | g4_rest_block_score_min | 0.5944 | 0.6896 | 0.6572 | 0.0324 | 75 |
| Q2_down | g4_h08_mlight_max_h_rz | 0.5926 | 0.3626 | 0.0532 | 0.3094 | 75 |
| Q2_down | g4_morning_06_10_mlight_max_h_rz_mean | 0.5919 | -0.0306 | -0.2234 | 0.1928 | 75 |
| Q2_flip | g4_h02_screen_use_sum_h_rz | 0.5990 | -0.7225 | -0.5255 | -0.1970 | 151 |
| Q2_flip | g4_sleep_00_06_screen_use_sum_h_rz_maxabs | 0.5943 | 1.0617 | 0.9344 | 0.1273 | 151 |
| Q2_flip | g4_sleep_00_06_screen_use_sum_h_rz_mean | 0.5928 | -0.7144 | -0.5643 | -0.1501 | 151 |
| Q2_flip | g4_h03_screen_use_sum_h_rz | 0.5869 | -0.8494 | -0.6757 | -0.1737 | 151 |
| Q2_flip | g4_evening_18_23_screen_use_sum_h_rz_maxabs | 0.5835 | 1.0407 | 0.9510 | 0.0897 | 151 |
| Q2_flip | g4_late_21_02_screen_use_sum_h_rz_maxabs | 0.5829 | 1.0698 | 0.9739 | 0.0959 | 151 |
| Q2_flip | g4_morning_06_10_screen_use_sum_h_rz_maxabs | 0.5789 | 1.0339 | 0.9397 | 0.0941 | 151 |
| Q2_flip | g4_h05_screen_use_sum_h_rz | 0.5788 | -0.8651 | -0.7195 | -0.1456 | 151 |
| Q2_up | g4_rest_fragmentation__prev_delta | 0.6042 | -0.7763 | 0.1456 | -0.9219 | 76 |
| Q2_up | g4_h06_screen_use_sum_h_rz | 0.5953 | -0.8045 | -0.5959 | -0.2086 | 76 |
| Q2_up | g4_h00_mlight_max_h_rz | 0.5953 | -1.3781 | -0.9299 | -0.4482 | 76 |
| Q2_up | g4_h02_screen_use_sum_h_rz | 0.5920 | -0.7457 | -0.5603 | -0.1854 | 76 |
| Q2_up | g4_sleep_00_06_screen_use_sum_h_rz_mean | 0.5900 | -0.7360 | -0.5901 | -0.1459 | 76 |
| Q2_up | g4_rest_block_score_mean__prev_delta | 0.5894 | -0.0332 | 0.0057 | -0.0389 | 76 |
| Q2_up | g4_h00_wlight_max_h_rz | 0.5889 | -0.6725 | -0.4773 | -0.1952 | 76 |
| Q2_up | g4_crossnight_screen_on_h__subj_z | 0.5816 | -0.1766 | 0.0973 | -0.2740 | 76 |
| Q3_down | g4_rest_block_score_mean__subj_z | 0.6293 | 0.2962 | -0.0260 | 0.3222 | 75 |
| Q3_down | g4_rest_block_score_min__subj_z | 0.6265 | 0.3377 | -0.0172 | 0.3549 | 75 |
| Q3_down | g4_rest_block_score_min | 0.6126 | 0.6982 | 0.6555 | 0.0427 | 75 |
| Q3_down | g4_rest_screen_interrupt_h__prev_delta | 0.6059 | -0.5467 | 0.1397 | -0.6864 | 75 |
| Q3_down | g4_rest_screen_interrupt_h | 0.6033 | 0.3867 | 0.8640 | -0.4773 | 75 |
| Q3_down | g4_rest_screen_interrupt_h__subj_z | 0.6001 | -0.3110 | 0.0251 | -0.3361 | 75 |
| Q3_down | g4_rest_boundary_confidence__subj_z | 0.5996 | 0.2925 | -0.0124 | 0.3050 | 75 |
| Q3_down | g4_rest_block_score_mean | 0.5962 | 0.7279 | 0.6983 | 0.0296 | 75 |
| Q3_flip | g4_h01_screen_use_sum_h_rz | 0.5762 | -0.5873 | -0.3988 | -0.1885 | 153 |
| Q3_flip | g4_sleep_00_06_wlight_max_h_rz_mean__prev_abs_delta | 0.5719 | 0.2512 | 0.1564 | 0.0948 | 153 |
| Q3_flip | g4_sleep_00_06_screen_use_sum_h_rz_maxabs | 0.5646 | 1.0268 | 0.9515 | 0.0753 | 153 |
| Q3_flip | g4_evening_18_23_mlight_max_h_rz_mean__prev_abs_delta | 0.5634 | 0.4766 | 0.4104 | 0.0662 | 153 |
| Q3_flip | g4_rest_block_score_min | 0.5615 | 0.6760 | 0.6557 | 0.0204 | 153 |
| Q3_flip | g4_h02_screen_use_sum_h_rz | 0.5609 | -0.6603 | -0.5563 | -0.1040 | 153 |
| Q3_flip | g4_rest_screen_interrupt_h | 0.5590 | 0.6667 | 0.8451 | -0.1785 | 153 |
| Q3_flip | g4_rest_activity_interrupt_h | 0.5581 | 5.2222 | 5.6801 | -0.4579 | 153 |
| Q3_up | g4_h00_mlight_max_h_rz | 0.6154 | -1.4434 | -0.9138 | -0.5296 | 78 |
| Q3_up | g4_rest_block_score_mean__prev_delta | 0.6128 | -0.0301 | 0.0053 | -0.0354 | 78 |
| Q3_up | g4_rest_boundary_confidence__prev_delta | 0.5973 | -0.0482 | 0.0093 | -0.0574 | 78 |
| Q3_up | g4_rest_block_score_min__prev_delta | 0.5890 | -0.0340 | 0.0055 | -0.0395 | 78 |
| Q3_up | g4_evening_18_23_wlight_max_h_rz_mean__prev_delta | 0.5856 | -0.1206 | 0.0091 | -0.1297 | 78 |
| Q3_up | g4_evening_18_23_screen_use_sum_h_rz_maxabs__prev_delta | 0.5720 | -0.0855 | 0.0198 | -0.1052 | 78 |
| Q3_up | g4_h00_screen_use_sum_h_rz | 0.5690 | -0.4718 | -0.2751 | -0.1967 | 78 |
| Q3_up | g4_day_10_18_screen_use_sum_h_rz_maxabs | 0.5676 | 0.9357 | 0.9766 | -0.0409 | 78 |

## 4. Public/private hidden split rules

정답 없는 test split의 정확한 public/private membership은 로컬 파일만으로 식별 불가능하다. 대신 test row geometry와 known-label neighbor 구조로 후보 rule을 랭킹했다.

| rule | n_rows | subject_coverage | inside_ratio | after_ratio | has_future_ratio | mean_prev_dist | mean_next_dist | date_min | date_max | plausibility_score | public_failure_risk_score |
|---|---|---|---|---|---|---|---|---|---|---|---|
| per_subject_first_half | 128 | 10 | 1.0000 | 0.0000 | 1.0000 | 6.8594 | 7.5859 | 2024-07-06 | 2024-10-16 | 0.6228 | 0.5640 |
| inside_only | 156 | 10 | 1.0000 | 0.0000 | 1.0000 | 6.1474 | 6.6346 | 2024-07-06 | 2024-11-13 | 0.6116 | 0.5640 |
| date_first_50pct | 125 | 8 | 0.8160 | 0.1840 | 0.8160 | 6.9760 | 8.1569 | 2024-07-06 | 2024-09-02 | 0.7780 | 0.2880 |
| sample_order_first_50pct | 125 | 5 | 0.6480 | 0.3520 | 0.6480 | 7.1520 | 6.3457 | 2024-07-30 | 2024-11-16 | 0.9010 | 0.0360 |
| alternating_even_rows | 125 | 10 | 0.6320 | 0.3680 | 0.6320 | 6.8480 | 6.6835 | 2024-07-06 | 2024-11-18 | 0.9920 | 0.0120 |
| full_test | 250 | 10 | 0.6240 | 0.3760 | 0.6240 | 6.9160 | 6.6346 | 2024-07-06 | 2024-11-19 | 0.9500 | 0.0000 |
| sample_order_first_40pct | 100 | 4 | 0.6100 | 0.3900 | 0.6100 | 8.1200 | 7.0492 | 2024-07-30 | 2024-10-19 | 0.8860 | -0.0210 |
| date_last_50pct | 125 | 8 | 0.4320 | 0.5680 | 0.4320 | 6.8560 | 3.7593 | 2024-09-03 | 2024-11-19 | 0.7780 | -0.2880 |
| per_subject_second_half | 122 | 10 | 0.2295 | 0.7705 | 0.2295 | 6.9754 | 2.2857 | 2024-07-20 | 2024-11-19 | 0.6043 | -0.5917 |
| tail_after_only | 94 | 10 | 0.0000 | 1.0000 | 0.0000 | 8.1915 | nan | 2024-08-14 | 2024-11-19 | 0.3636 | -0.9360 |

## Decision summary

- Q2/Q3 two-factor blend mean delta by family: {'chrono_tail': 0.0, 'hole_v1': -0.0163, 'mirror_v1': -0.0118}

- Q2/Q3 one-factor blend mean delta by family: {'chrono_tail': 0.0, 'hole_v1': -0.0127, 'mirror_v1': -0.0132}

- Q2/Q3 new sleep-boundary mean delta by family: {'chrono_tail': 0.1005, 'hole_v1': 0.0543, 'mirror_v1': 0.0949}

- Strongest transition event features: [{'event': 'Q3_down', 'feature': 'g4_rest_block_score_mean__subj_z', 'auc_abs': 0.6292622222222223}, {'event': 'Q3_down', 'feature': 'g4_rest_block_score_min__subj_z', 'auc_abs': 0.6265244444444443}, {'event': 'Q3_up', 'feature': 'g4_h00_mlight_max_h_rz', 'auc_abs': 0.615401847256686}, {'event': 'Q3_up', 'feature': 'g4_rest_block_score_mean__prev_delta', 'auc_abs': 0.6128342983181693}, {'event': 'Q3_down', 'feature': 'g4_rest_block_score_min', 'auc_abs': 0.6126044444444444}]

- Adopt: two-factor blend for Q2/Q3 only in inside-hole rows; hold raw logistic Q/S factor and new sleep-boundary logistic features.

- Hidden split: `inside_only`/future-neighbor-heavy subsets are the highest public-failure-risk candidates; exact split discovery needs multiple submissions with public scores or organizer disclosure.
