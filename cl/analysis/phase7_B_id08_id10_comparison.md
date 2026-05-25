# Phase 7B — id08 vs id10 night-phone regime 비교

둘 다 night-phone/short screen-off 계열이지만 Q2/Q3 라벨 구조가 다르다.

## base comparison

| subject_id | n_days | Q1_rate | Q2_rate | Q3_rate | S1_rate | S2_rate | S3_rate | S4_rate | night_screen_mean | screenoff_h | gps_radius | steps | app_total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id08 | 56 | 0.411 | 0.786 | 0.446 | 0.446 | 0.607 | 0.661 | 0.607 | 55.589 | 3.250 | 0.035 | 2303.914 | 29217721.500 |
| id10 | 33 | 0.485 | 0.545 | 0.636 | 0.485 | 0.364 | 0.485 | 0.667 | 103.152 | 2.273 | 0.028 | 3383.515 | 34797872.000 |

## Q2/Q3 class axis comparison

| subject_id | class | n_days | Q1_rate | low_activity | night_phone | phone_internal | rest_quiet | low_mobility_context | physio_light_low |
|---|---|---|---|---|---|---|---|---|---|
| id08 | Q2=0,Q3=0 | 12 | 0.500 | 0.199 | -0.388 | -0.126 | 0.233 | -0.039 | -0.331 |
| id08 | Q2=1,Q3=0 | 19 | 0.263 | -0.181 | -0.155 | 0.040 | 0.071 | 0.178 | 0.199 |
| id08 | Q2=1,Q3=1 | 25 | 0.480 | -0.096 | 0.304 | 0.030 | -0.166 | 0.266 | 0.378 |
| id10 | Q2=0,Q3=0 | 11 | 0.364 | 0.152 | -0.204 | -0.326 | 0.067 | 0.047 | 0.012 |
| id10 | Q2=0,Q3=1 | 4 | 0.500 | 0.113 | 0.510 | 0.958 | -0.202 | -0.405 | -0.282 |
| id10 | Q2=1,Q3=0 | 1 | 1.000 | -0.102 | 0.939 | 0.974 | -0.202 | 1.558 | 1.198 |
| id10 | Q2=1,Q3=1 | 17 | 0.529 | -0.119 | -0.043 | -0.071 | 0.016 | -0.027 | -0.012 |

## top apps

| subject_id | app | minutes |
|---|---|---|
| id08 | 시스템 ui | 9632.200 |
| id08 | one ui 홈 | 9140.800 |
| id08 | 클래시 로얄 | 3134.700 |
| id08 | youtube | 2775.800 |
| id08 | 카카오톡 | 2532.800 |
| id08 | 네이트 | 1246.900 |
| id08 | 메시지 | 1184.300 |
| id08 | 당근 | 826.200 |
| id08 | 클래시오브클랜 | 634.300 |
| id08 | withings | 566.800 |
| id08 | 삼성 인터넷 | 539.500 |
| id08 | 통화 | 490.900 |
| id10 | one ui 홈 | 8235.000 |
| id10 | 카카오톡 | 6043.600 |
| id10 | instagram | 3675.200 |
| id10 | threads | 3342.700 |
| id10 | naver | 1452.100 |
| id10 | x | 1333.200 |
| id10 | merge designer-decor & story | 1271.900 |
| id10 | youtube | 1090.300 |
| id10 | nonogram elf | 793.500 |
| id10 | 쿠팡 | 612.000 |
| id10 | screw puzzle | 538.000 |
| id10 | fantastic bricks | 537.500 |

## Q2 transition diaries

| subject_id | lifelog_date | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | top_axes | screen_use_00_06 | longest_screenoff_run_h | gps_radius_proxy | steps_sum | top_apps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id08 | 2024-06-28 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | night_phone:+1.33, phone_internal:+0.97, low_activity:-0.85 | 55.000 | 2.000 | 0.060 | 3882.000 | one ui 홈(262m), 시스템 ui(111m), 카카오톡(52m), youtube(42m) |
| id08 | 2024-07-09 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | low_activity:+1.40, rest_quiet:+1.08, night_phone:-0.91 | 27.000 | 4.000 | 0.060 | 969.000 | one ui 홈(171m), 클래시 로얄(104m), 시스템 ui(95m), 당근(33m) |
| id08 | 2024-07-27 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | low_activity:+1.81, phone_internal:-1.67, night_phone:-1.16 | 14.000 | 4.000 | nan | 40.000 | withings(18m), one ui 홈(18m), 시스템 ui(14m), 통화 설정(9m) |
| id08 | 2024-08-04 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | physio_light_low:+1.13, low_mobility_context:+1.04, phone_internal:-1.02 | 33.000 | 4.000 | nan | nan | 시스템 ui(32m), one ui 홈(21m), 클래시 로얄(21m), youtube(17m) |
| id08 | 2024-08-16 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | low_activity:-1.50, phone_internal:+1.34, low_mobility_context:+1.03 | 46.000 | 3.000 | nan | nan | one ui 홈(148m), 시스템 ui(126m), 카카오톡(72m), youtube(65m) |
| id08 | 2024-08-22 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | physio_light_low:-0.85, low_mobility_context:+0.51, night_phone:-0.28 | 76.000 | 3.000 | 0.010 | 2796.000 | 시스템 ui(232m), one ui 홈(123m), 클래시 로얄(58m), 카카오톡(38m) |
| id08 | 2024-08-28 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | night_phone:-1.19, low_mobility_context:+1.04, physio_light_low:+0.80 | 25.000 | 5.000 | 0.000 | 0.000 | 시스템 ui(72m), one ui 홈(69m), youtube(36m), 메시지(21m) |
| id10 | 2024-07-09 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | rest_quiet:+2.76, night_phone:-0.74, low_mobility_context:-0.48 | 0.000 | 6.000 | 0.040 | 5035.000 | 카카오톡(109m), one ui 홈(74m), nonogram elf(60m), instagram(53m) |
| id10 | 2024-07-15 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | low_mobility_context:-1.57, low_activity:-1.03, rest_quiet:-0.94 | 90.000 | 1.000 | 0.050 | 8248.000 | x(174m), one ui 홈(100m), nonogram elf(65m), 카카오톡(60m) |
| id10 | 2024-07-26 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | physio_light_low:-0.96, rest_quiet:+0.54, low_mobility_context:-0.53 | 1.000 | 3.000 | 0.040 | 3725.000 | one ui 홈(137m), 카카오톡(131m), merge designer-decor & story(96m), 쿠팡이츠(31m) |
| id10 | 2024-08-01 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | low_mobility_context:-0.78, physio_light_low:-0.59, rest_quiet:+0.54 | 51.000 | 3.000 | 0.040 | 4256.000 | one ui 홈(194m), 카카오톡(181m), instagram(136m), merge designer-decor & story(93m) |
| id10 | 2024-08-27 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | low_activity:+1.35, rest_quiet:-0.94, low_mobility_context:-0.39 | 253.000 | 1.000 | 0.040 | 3377.000 | one ui 홈(148m), 카카오톡(142m), instagram(96m), threads(63m) |
| id10 | 2024-08-30 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | rest_quiet:-0.94, low_mobility_context:-0.76, phone_internal:-0.74 | 128.000 | 1.000 | 0.040 | 3354.000 | 카카오톡(73m), hexa sort(65m), one ui 홈(65m), threads(32m) |
| id10 | 2024-09-07 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | low_mobility_context:+1.56, physio_light_low:+1.20, phone_internal:+0.97 | 172.000 | 2.000 | 0.000 | 62.000 | 카카오톡(256m), one ui 홈(256m), threads(98m), naver(90m) |

