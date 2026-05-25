# Goal5 — 0.55 breakthrough clue hunt

목표는 평균 CV를 조금 올리는 후보가 아니라, test 250 rows 중 일부를 크게 맞힐 수 있는 고상한 단서를 찾는 것이다.


## 1. Best subset-moving candidates

| family | target | candidate | mode | mean_delta | std_delta | mean_coverage | mean_move |
|---|---|---|---|---|---|---|---|
| hole_v1 | S3 | nn_hour_transition | top50_w050 | -0.0164 | 0.0090 | 0.5045 | 0.0709 |
| hole_v1 | S3 | nn_hour_transition | top20_w075 | -0.0159 | 0.0130 | 0.2072 | 0.1489 |
| hole_v1 | S3 | nn_hour_transition | top30_w060 | -0.0139 | 0.0092 | 0.3063 | 0.1052 |
| hole_v1 | Q1 | near_date_peer_w7 | top30_w060 | -0.0108 | 0.0111 | 0.3063 | 0.0923 |
| hole_v1 | S3 | nn_hour_transition | top10_w090 | -0.0102 | 0.0179 | 0.1081 | 0.2408 |
| hole_v1 | Q1 | near_date_peer_w7 | top10_w090 | -0.0094 | 0.0207 | 0.1081 | 0.2227 |
| hole_v1 | Q2 | nn_identity_token | top50_w050 | -0.0091 | 0.0103 | 0.5045 | 0.0723 |
| hole_v1 | Q1 | near_date_peer_w7 | top50_w050 | -0.0090 | 0.0112 | 0.5045 | 0.0655 |
| hole_v1 | Q1 | near_date_peer_w7 | top20_w075 | -0.0067 | 0.0189 | 0.2072 | 0.1394 |
| hole_v1 | Q2 | nn_identity_token | top30_w060 | -0.0060 | 0.0094 | 0.3063 | 0.1116 |
| mirror_v1 | S3 | near_date_peer_w7 | top30_w060 | -0.0047 | 0.0187 | 0.3012 | 0.1697 |
| mirror_v1 | Q2 | nn_rest_boundary | top50_w050 | -0.0042 | 0.0014 | 0.5025 | 0.0873 |
| mirror_v1 | Q3 | nn_hour_transition | top50_w050 | -0.0040 | 0.0098 | 0.5025 | 0.1093 |
| hole_v1 | Q3 | nn_identity_token | top50_w050 | -0.0033 | 0.0137 | 0.5045 | 0.0832 |
| hole_v1 | Q2 | nn_hour_transition | top50_w050 | -0.0025 | 0.0323 | 0.5045 | 0.1083 |
| hole_v1 | Q1 | nn_identity_token | top50_w050 | -0.0024 | 0.0180 | 0.5045 | 0.0790 |
| hole_v1 | Q2 | nn_rest_boundary | top50_w050 | -0.0022 | 0.0061 | 0.5045 | 0.0971 |
| mirror_v1 | Q3 | near_date_peer_w7 | top50_w050 | -0.0015 | 0.0110 | 0.5042 | 0.0919 |
| hole_v1 | Q2 | nn_identity_token | top10_w090 | -0.0014 | 0.0079 | 0.1081 | 0.2066 |
| hole_v1 | Q1 | nn_rest_boundary | top50_w050 | -0.0012 | 0.0262 | 0.5045 | 0.1192 |
| hole_v1 | S3 | nn_rest_boundary | top10_w090 | -0.0011 | 0.0102 | 0.1081 | 0.0988 |
| hole_v1 | Q1 | nn_identity_token | top20_w075 | -0.0008 | 0.0329 | 0.2072 | 0.1621 |
| mirror_v1 | S2 | nn_semantic_app | top20_w075 | -0.0006 | 0.0130 | 0.2030 | 0.1140 |
| hole_v1 | Q3 | nn_identity_token | top30_w060 | 0.0004 | 0.0179 | 0.3063 | 0.0962 |
| mirror_v1 | S3 | near_date_peer_w3 | top30_w060 | 0.0005 | 0.0067 | 0.3147 | 0.1605 |
| hole_v1 | S1 | nn_rest_boundary | top50_w050 | 0.0007 | 0.0075 | 0.5045 | 0.0830 |
| hole_v1 | Q3 | nn_identity_token | top20_w075 | 0.0009 | 0.0199 | 0.2072 | 0.1249 |
| hole_v1 | Q2 | nn_rest_boundary | top20_w075 | 0.0010 | 0.0064 | 0.2072 | 0.1737 |
| mirror_v1 | S3 | near_date_peer_w7 | top50_w050 | 0.0011 | 0.0092 | 0.5110 | 0.1281 |
| mirror_v1 | S2 | nn_semantic_app | top30_w060 | 0.0014 | 0.0128 | 0.2995 | 0.0858 |
| hole_v1 | Q2 | nn_identity_token | top20_w075 | 0.0014 | 0.0138 | 0.2072 | 0.1508 |
| hole_v1 | Q3 | nn_hour_transition | top10_w090 | 0.0016 | 0.0131 | 0.1081 | 0.2088 |
| mirror_v1 | S4 | nn_hour_transition | top30_w060 | 0.0018 | 0.0175 | 0.2995 | 0.1362 |
| mirror_v1 | S1 | nn_rest_boundary | top50_w050 | 0.0020 | 0.0028 | 0.5025 | 0.0789 |
| mirror_v1 | Q3 | nn_hour_transition | top30_w060 | 0.0022 | 0.0067 | 0.2995 | 0.1325 |
| hole_v1 | S1 | nn_identity_token | top10_w090 | 0.0024 | 0.0080 | 0.1231 | 0.1123 |
| mirror_v1 | Q3 | nn_rest_boundary | top50_w050 | 0.0027 | 0.0143 | 0.5025 | 0.0829 |
| hole_v1 | S3 | nn_semantic_app | top50_w050 | 0.0027 | 0.0209 | 0.5045 | 0.0754 |
| mirror_v1 | Q2 | nn_rest_boundary | top30_w060 | 0.0029 | 0.0024 | 0.2995 | 0.1144 |
| hole_v1 | Q1 | nn_identity_token | top30_w060 | 0.0032 | 0.0253 | 0.3183 | 0.1142 |

## 2. Overall candidate ranking

| family | target | candidate | mode | mean_delta | std_delta | mean_coverage | mean_move |
|---|---|---|---|---|---|---|---|
| chrono_tail | Q1 | nn_rest_boundary | top20_w075 | -0.0415 | 0.0054 | 0.2058 | 0.1766 |
| chrono_tail | Q1 | nn_rest_boundary | top30_w060 | -0.0397 | 0.0046 | 0.3042 | 0.1290 |
| chrono_tail | S4 | nn_identity_token | top50_w050 | -0.0349 | 0.0104 | 0.5420 | 0.1013 |
| chrono_tail | Q1 | nn_rest_boundary | top50_w050 | -0.0319 | 0.0074 | 0.5033 | 0.0922 |
| chrono_tail | Q1 | nn_rest_boundary | top10_w090 | -0.0302 | 0.0078 | 0.1075 | 0.2363 |
| chrono_tail | Q1 | nn_semantic_app | top30_w060 | -0.0298 | 0.0033 | 0.3042 | 0.1385 |
| chrono_tail | Q1 | nn_semantic_app | top10_w090 | -0.0296 | 0.0075 | 0.1075 | 0.2692 |
| chrono_tail | Q1 | nn_semantic_app | top20_w075 | -0.0281 | 0.0077 | 0.2058 | 0.1904 |
| chrono_tail | Q1 | near_date_peer_w7 | top10_w090 | -0.0255 | 0.0079 | 0.1245 | 0.2958 |
| chrono_tail | S4 | nn_identity_token | top30_w060 | -0.0248 | 0.0153 | 0.3091 | 0.1414 |
| chrono_tail | Q2 | near_date_peer_w3 | top50_w050 | -0.0222 | 0.0141 | 0.5033 | 0.1310 |
| chrono_tail | Q1 | nn_semantic_app | top50_w050 | -0.0220 | 0.0041 | 0.5033 | 0.0974 |
| chrono_tail | S4 | nn_identity_token | top10_w090 | -0.0216 | 0.0127 | 0.1771 | 0.2498 |
| chrono_tail | S4 | nn_identity_token | top20_w075 | -0.0214 | 0.0184 | 0.2468 | 0.1807 |
| chrono_tail | S1 | nn_rest_boundary | top50_w050 | -0.0209 | 0.0033 | 0.5033 | 0.0805 |
| chrono_tail | S4 | nn_identity_token | blend_all_w025 | -0.0207 | 0.0046 | 1.0000 | 0.0401 |
| chrono_tail | Q1 | nn_rest_boundary | blend_all_w025 | -0.0200 | 0.0041 | 1.0000 | 0.0337 |
| chrono_tail | S1 | nn_semantic_app | top30_w060 | -0.0192 | 0.0031 | 0.3042 | 0.1024 |
| chrono_tail | Q1 | near_date_peer_w7 | top20_w075 | -0.0188 | 0.0022 | 0.2108 | 0.2428 |
| chrono_tail | S1 | nn_rest_boundary | top30_w060 | -0.0188 | 0.0040 | 0.3042 | 0.0924 |
| chrono_tail | Q2 | near_date_peer_w3 | blend_all_w025 | -0.0173 | 0.0081 | 1.0000 | 0.0427 |
| hole_v1 | S3 | nn_hour_transition | top50_w050 | -0.0164 | 0.0090 | 0.5045 | 0.0709 |
| hole_v1 | S3 | nn_hour_transition | top20_w075 | -0.0159 | 0.0130 | 0.2072 | 0.1489 |
| chrono_tail | Q1 | nn_hour_transition | top30_w060 | -0.0156 | 0.0123 | 0.3042 | 0.1463 |
| chrono_tail | Q1 | nn_hour_transition | top50_w050 | -0.0151 | 0.0131 | 0.5033 | 0.1067 |
| chrono_tail | S2 | nn_identity_token | blend_all_w025 | -0.0148 | 0.0135 | 1.0000 | 0.0352 |
| hole_v1 | Q3 | nn_identity_token | blend_all_w025 | -0.0148 | 0.0070 | 1.0000 | 0.0345 |
| chrono_tail | Q1 | nn_identity_token | blend_all_w025 | -0.0143 | 0.0011 | 1.0000 | 0.0326 |
| hole_v1 | S3 | nn_hour_transition | top30_w060 | -0.0139 | 0.0092 | 0.3063 | 0.1052 |
| chrono_tail | Q1 | nn_identity_token | top50_w050 | -0.0133 | 0.0027 | 0.5088 | 0.0890 |
| chrono_tail | S1 | nn_semantic_app | top20_w075 | -0.0126 | 0.0061 | 0.2058 | 0.1428 |
| chrono_tail | S1 | nn_rest_boundary | top20_w075 | -0.0122 | 0.0081 | 0.2058 | 0.1190 |
| mirror_v1 | Q3 | nn_hour_transition | blend_all_w025 | -0.0120 | 0.0008 | 1.0000 | 0.0430 |
| hole_v1 | Q1 | near_date_peer_w7 | top30_w060 | -0.0108 | 0.0111 | 0.3063 | 0.0923 |
| mirror_v1 | Q2 | nn_rest_boundary | blend_all_w025 | -0.0105 | 0.0030 | 1.0000 | 0.0349 |
| chrono_tail | S1 | nn_rest_boundary | blend_all_w025 | -0.0105 | 0.0028 | 1.0000 | 0.0373 |
| chrono_tail | S4 | near_date_peer_w7 | top30_w060 | -0.0102 | 0.0080 | 0.3116 | 0.1442 |
| hole_v1 | S3 | nn_hour_transition | top10_w090 | -0.0102 | 0.0179 | 0.1081 | 0.2408 |
| hole_v1 | Q1 | near_date_peer_w7 | top10_w090 | -0.0094 | 0.0207 | 0.1081 | 0.2227 |
| chrono_tail | Q1 | nn_hour_transition | blend_all_w025 | -0.0093 | 0.0070 | 1.0000 | 0.0394 |
| hole_v1 | Q2 | nn_identity_token | top50_w050 | -0.0091 | 0.0103 | 0.5045 | 0.0723 |
| hole_v1 | Q1 | near_date_peer_w7 | top50_w050 | -0.0090 | 0.0112 | 0.5045 | 0.0655 |
| hole_v1 | Q2 | nn_identity_token | blend_all_w025 | -0.0089 | 0.0014 | 1.0000 | 0.0294 |
| chrono_tail | Q2 | near_date_peer_w7 | blend_all_w025 | -0.0086 | 0.0057 | 1.0000 | 0.0380 |
| chrono_tail | Q3 | nn_identity_token | top50_w050 | -0.0084 | 0.0011 | 0.5033 | 0.0913 |
| chrono_tail | Q3 | nn_identity_token | blend_all_w025 | -0.0083 | 0.0035 | 1.0000 | 0.0388 |
| chrono_tail | S3 | near_date_peer_w7 | blend_all_w025 | -0.0082 | 0.0043 | 1.0000 | 0.0739 |
| chrono_tail | Q2 | same_date_peer_w0 | blend_all_w025 | -0.0080 | 0.0057 | 1.0000 | 0.0609 |
| chrono_tail | S1 | nn_semantic_app | top50_w050 | -0.0079 | 0.0049 | 0.5033 | 0.0756 |
| chrono_tail | Q1 | nn_semantic_app | blend_all_w025 | -0.0077 | 0.0034 | 1.0000 | 0.0372 |

## 3. Test coverage for top NN candidates

| candidate | target | test_n | test_conf_top10_threshold | test_top10_rows | test_top20_rows | test_mean_conf | test_mean_abs_move_from_subject_prior |
|---|---|---|---|---|---|---|---|
| nn_hour_transition | S3 | 250 | 0.1082 | 25 | 50 | 0.0615 | 0.1388 |
| nn_hour_transition | S3 | 250 | 0.1082 | 25 | 50 | 0.0615 | 0.1388 |
| nn_hour_transition | S3 | 250 | 0.1082 | 25 | 50 | 0.0615 | 0.1388 |
| nn_hour_transition | S3 | 250 | 0.1082 | 25 | 50 | 0.0615 | 0.1388 |
| nn_identity_token | Q2 | 250 | 0.2997 | 26 | 50 | 0.1458 | 0.1270 |
| nn_identity_token | Q2 | 250 | 0.2997 | 26 | 50 | 0.1458 | 0.1270 |
| nn_rest_boundary | Q2 | 250 | 0.0880 | 25 | 50 | 0.0439 | 0.1409 |
| nn_hour_transition | Q3 | 250 | 0.1042 | 25 | 50 | 0.0506 | 0.1510 |
| nn_identity_token | Q3 | 250 | 0.2715 | 25 | 50 | 0.1238 | 0.1517 |
| nn_hour_transition | Q2 | 250 | 0.0803 | 25 | 50 | 0.0404 | 0.1574 |
| nn_identity_token | Q1 | 250 | 0.4620 | 25 | 50 | 0.1793 | 0.1210 |
| nn_rest_boundary | Q2 | 250 | 0.0880 | 25 | 50 | 0.0439 | 0.1409 |
| nn_identity_token | Q2 | 250 | 0.2997 | 26 | 50 | 0.1458 | 0.1270 |
| nn_rest_boundary | Q1 | 250 | 0.1065 | 25 | 50 | 0.0514 | 0.1721 |

## 4. Top test rows for row-action inspection

| candidate | target | subject_id | lifelog_date | subject_prior | nn_pred | move_from_subject_prior | confidence | conf_rank |
|---|---|---|---|---|---|---|---|---|
| nn_hour_transition | S3 | id04 | 2024-09-24 | 0.5746 | 0.0300 | -0.5446 | 0.2281 | 1 |
| nn_hour_transition | S3 | id05 | 2024-09-28 | 0.3007 | 0.1032 | -0.1975 | 0.1752 | 2 |
| nn_hour_transition | S3 | id05 | 2024-11-16 | 0.3007 | 0.1111 | -0.1896 | 0.1615 | 3 |
| nn_hour_transition | S3 | id04 | 2024-10-25 | 0.5746 | 0.2136 | -0.3610 | 0.1540 | 4 |
| nn_hour_transition | S3 | id05 | 2024-10-01 | 0.3007 | 0.1057 | -0.1950 | 0.1477 | 5 |
| nn_hour_transition | S3 | id05 | 2024-10-06 | 0.3007 | 0.1050 | -0.1957 | 0.1452 | 6 |
| nn_hour_transition | S3 | id05 | 2024-10-17 | 0.3007 | 0.1103 | -0.1904 | 0.1395 | 7 |
| nn_hour_transition | S3 | id05 | 2024-11-15 | 0.3007 | 0.1062 | -0.1945 | 0.1360 | 8 |
| nn_hour_transition | S3 | id04 | 2024-10-27 | 0.5746 | 0.7714 | 0.1968 | 0.1343 | 9 |
| nn_hour_transition | S3 | id04 | 2024-10-15 | 0.5746 | 0.1881 | -0.3865 | 0.1328 | 10 |
| nn_hour_transition | S3 | id07 | 2024-08-22 | 0.7572 | 0.9700 | 0.2128 | 0.1315 | 11 |
| nn_hour_transition | S3 | id07 | 2024-08-19 | 0.7572 | 0.9700 | 0.2128 | 0.1282 | 12 |
| nn_hour_transition | S3 | id08 | 2024-09-17 | 0.6611 | 0.8906 | 0.2295 | 0.1280 | 13 |
| nn_hour_transition | S3 | id03 | 2024-08-24 | 0.5518 | 0.0300 | -0.5218 | 0.1277 | 14 |
| nn_hour_transition | S3 | id08 | 2024-08-07 | 0.6611 | 0.8992 | 0.2381 | 0.1272 | 15 |
| nn_hour_transition | S3 | id08 | 2024-09-14 | 0.6611 | 0.9700 | 0.3089 | 0.1272 | 16 |
| nn_hour_transition | S3 | id08 | 2024-08-05 | 0.6611 | 0.8960 | 0.2349 | 0.1217 | 17 |
| nn_hour_transition | S3 | id01 | 2024-07-31 | 0.7909 | 0.9700 | 0.1791 | 0.1204 | 18 |
| nn_hour_transition | S3 | id02 | 2024-08-26 | 0.8271 | 0.9700 | 0.1429 | 0.1203 | 19 |
| nn_hour_transition | S3 | id04 | 2024-10-17 | 0.5746 | 0.2280 | -0.3467 | 0.1183 | 20 |
| nn_hour_transition | S3 | id03 | 2024-08-20 | 0.5518 | 0.8946 | 0.3428 | 0.1173 | 21 |
| nn_hour_transition | S3 | id04 | 2024-09-14 | 0.5746 | 0.7614 | 0.1868 | 0.1165 | 22 |
| nn_hour_transition | S3 | id05 | 2024-11-19 | 0.3007 | 0.2187 | -0.0820 | 0.1163 | 23 |
| nn_hour_transition | S3 | id05 | 2024-11-17 | 0.3007 | 0.2297 | -0.0710 | 0.1125 | 24 |
| nn_hour_transition | S3 | id02 | 2024-09-02 | 0.8271 | 0.9700 | 0.1429 | 0.1121 | 25 |
| nn_identity_token | Q2 | id05 | 2024-10-01 | 0.4726 | 0.2160 | -0.2565 | 0.5003 | 1 |
| nn_identity_token | Q2 | id01 | 2024-09-10 | 0.5614 | 0.7747 | 0.2133 | 0.4797 | 2 |
| nn_identity_token | Q2 | id08 | 2024-08-07 | 0.7269 | 0.9700 | 0.2431 | 0.4765 | 3 |
| nn_identity_token | Q2 | id05 | 2024-10-04 | 0.4726 | 0.2145 | -0.2581 | 0.4730 | 4 |
| nn_identity_token | Q2 | id01 | 2024-09-12 | 0.5614 | 0.7751 | 0.2137 | 0.4722 | 5 |
| nn_identity_token | Q2 | id04 | 2024-10-18 | 0.5097 | 0.2132 | -0.2965 | 0.4717 | 6 |
| nn_identity_token | Q2 | id05 | 2024-11-15 | 0.4726 | 0.2147 | -0.2579 | 0.4632 | 7 |
| nn_identity_token | Q2 | id01 | 2024-09-11 | 0.5614 | 0.7642 | 0.2028 | 0.4604 | 8 |
| nn_identity_token | Q2 | id01 | 2024-09-06 | 0.5614 | 0.7752 | 0.2138 | 0.4553 | 9 |
| nn_identity_token | Q2 | id08 | 2024-08-02 | 0.7269 | 0.9700 | 0.2431 | 0.4463 | 10 |
| nn_identity_token | Q2 | id08 | 2024-09-06 | 0.7269 | 0.9700 | 0.2431 | 0.4365 | 11 |
| nn_identity_token | Q2 | id09 | 2024-08-14 | 0.4794 | 0.1228 | -0.3566 | 0.4046 | 12 |
| nn_identity_token | Q2 | id08 | 2024-09-10 | 0.7269 | 0.9700 | 0.2431 | 0.3927 | 13 |
| nn_identity_token | Q2 | id08 | 2024-08-10 | 0.7269 | 0.8990 | 0.1721 | 0.3704 | 14 |
| nn_identity_token | Q2 | id02 | 2024-10-06 | 0.6359 | 0.9700 | 0.3341 | 0.3681 | 15 |

## 5. Repeated selected features

| group | target | feature | selected_count |
|---|---|---|---|
| semantic_app | Q1 | sem__topapp_all_시스템_ui_time | 9 |
| hour_transition | S2 | h4__g4_sleep_00_06_wlight_max_h_rz_maxabs | 9 |
| hour_transition | S2 | h4__g4_evening_18_23_activity_mean_h_rz_maxabs__prev_abs_delta | 9 |
| hour_transition | S2 | h4__g4_morning_06_10_activity_mean_h_rz_maxabs | 9 |
| hour_transition | S2 | h4__g4_day_10_18_activity_mean_h_rz_maxabs__prev_abs_delta | 9 |
| hour_transition | S2 | h4__g4_h05_activity_mean_h_rz | 9 |
| hour_transition | S2 | h4__g4_h00_mlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_h06_mlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_day_10_18_mlight_max_h_rz_maxabs | 9 |
| hour_transition | S2 | h4__g4_h03_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_h04_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_h02_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_h01_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_day_10_18_wlight_max_h_rz_mean__prev_abs_delta | 9 |
| hour_transition | S2 | h4__g4_morning_06_10_wlight_max_h_rz_maxabs | 9 |
| hour_transition | S2 | h4__g4_late_21_02_wlight_max_h_rz_maxabs | 9 |
| hour_transition | S2 | h4__g4_h12_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_h00_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_sleep_00_06_wlight_max_h_rz_mean | 9 |
| hour_transition | S2 | h4__g4_h06_screen_use_sum_h_rz | 9 |
| hour_transition | S2 | h4__g4_h16_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_sleep_00_06_mlight_max_h_rz_mean__prev_delta | 9 |
| hour_transition | S2 | h4__g4_h13_wlight_max_h_rz | 9 |
| hour_transition | S2 | h4__g4_day_10_18_mlight_max_h_rz_mean__prev_abs_delta | 9 |
| hour_transition | S2 | h4__g4_hourly_max_abs_deviation | 9 |
| identity_token | S2 | tok__wifi_bssid:08:5d:dd:de:5f:fb | 9 |
| identity_token | S2 | tok__wifi_bssid:3a:5d:dd:de:5f:fb | 9 |
| identity_token | S2 | tok__wifi_bssid:00:23:aa:e3:b6:43 | 9 |
| identity_token | S2 | tok__wifi_bssid:3a:5d:dd:d8:9e:52 | 9 |
| identity_token | S2 | tok__wifi_bssid:00:23:aa:e3:b6:42 | 9 |
| identity_token | S2 | tok__wifi_bssid:0a:5d:dd:d8:9e:53 | 9 |
| identity_token | S2 | tok__wifi_bssid:08:5d:dd:d1:35:66 | 9 |
| identity_token | S2 | tok__wifi_bssid:3a:5d:dd:70:c5:30 | 9 |
| identity_token | S2 | tok__wifi_bssid:08:5d:dd:70:c5:30 | 9 |
| identity_token | S2 | tok__wifi_bssid:12:23:aa:e3:b6:42 | 9 |
| identity_token | S2 | tok__wifi_bssid:42:23:aa:dc:6f:96 | 9 |
| identity_token | S2 | tok__wifi_bssid:0a:5d:dd:d1:35:67 | 9 |
| identity_token | S2 | tok__wifi_bssid:00:23:aa:dc:6f:96 | 9 |
| identity_token | S2 | tok__wifi_bssid:3a:5d:dd:d1:35:66 | 9 |
| identity_token | S2 | tok__wifi_bssid:12:23:aa:dc:6f:96 | 9 |
| identity_token | S2 | tok__wifi_bssid:0a:5d:dd:70:c5:30 | 9 |
| identity_token | S2 | tok__wifi_bssid:3a:5d:dd:73:32:68 | 9 |
| identity_token | S2 | tok__wifi_bssid:08:5d:dd:73:32:68 | 9 |
| identity_token | S2 | tok__wifi_bssid:e8:54:84:35:87:37 | 9 |
| identity_token | S2 | tok__wifi_bssid:42:23:aa:e3:b6:43 | 9 |
| identity_token | S2 | tok__wifi_bssid:e8:54:84:35:87:35 | 9 |
| identity_token | S2 | tok__wifi_bssid:0a:5d:dd:73:32:68 | 9 |
| identity_token | S2 | tok__usage_app_name:캐시워크 | 9 |
| identity_token | S2 | tok__wifi_bssid:22:23:aa:e3:b6:43 | 9 |
| hour_transition | S2 | h4__g4_day_10_18_wlight_max_h_rz_mean | 9 |
| hour_transition | S2 | h4__g4_morning_06_10_screen_use_sum_h_rz_mean | 9 |
| identity_token | S2 | tok__wifi_bssid:08:5d:dd:d1:35:67 | 9 |
| semantic_app | S3 | sem__topapp_evening_성경일독q_time | 9 |
| rest_boundary | S2 | r4__g4_rest_high_run_end_rel_h__prev_abs_delta | 9 |
| rest_boundary | S2 | r4__g4_rest_screen_interrupt_h__subj_z | 9 |
| rest_boundary | S2 | r4__g4_rest_activity_interrupt_h__prev_delta | 9 |
| rest_boundary | S2 | r4__g4_rest_light_interrupt_h__prev_delta | 9 |
| rest_boundary | S2 | r4__g4_post_rest_active_h__subj_z | 9 |
| rest_boundary | S2 | r4__g4_post_rest_active_h__prev_delta | 9 |
| rest_boundary | S2 | r4__g4_pre_rest_screen_sum__subj_z | 9 |

## 6. Decision

- If a candidate shows `mean_delta <= -0.02` on both `hole_v1` and `mirror_v1` with 10-30% coverage, it is a real 0.55-style clue candidate.

- If gains are concentrated in one fold family or one target only, use it as a row-action diagnostic, not as a global submission rule.

- Top rows above should be inspected manually before any submission movement.
