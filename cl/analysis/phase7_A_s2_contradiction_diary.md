# Phase 7A — S2 contradiction diary

S2가 S1/S3/S4 majority와 충돌하는 row를 따로 봤다.

## subject별 contradiction rate

| subject_id | S2_only_high | S2_only_low | aligned | contradiction_rate |
|---|---|---|---|---|
| id01 | 4 | 7 | 30 | 0.268 |
| id02 | 1 | 2 | 45 | 0.062 |
| id03 | 8 | 4 | 21 | 0.364 |
| id04 | 6 | 1 | 50 | 0.123 |
| id05 | 4 | 5 | 35 | 0.205 |
| id06 | 0 | 4 | 44 | 0.083 |
| id07 | 2 | 4 | 43 | 0.122 |
| id08 | 5 | 6 | 45 | 0.196 |
| id09 | 4 | 2 | 35 | 0.146 |
| id10 | 1 | 7 | 25 | 0.242 |

## S2 contradiction profile

| s2_case | n_days | Q1_rate | Q2_rate | Q3_rate | S1_rate | S2_rate | S3_rate | S4_rate | low_activity | night_phone | phone_internal | rest_quiet | low_mobility_context | physio_light_low |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S2_only_high | 35 | 0.486 | 0.686 | 0.629 | 0.514 | 1.000 | 0.286 | 0.200 | -0.171 | -0.058 | 0.021 | 0.029 | 0.011 | 0.075 |
| S2_only_low | 42 | 0.548 | 0.595 | 0.548 | 0.976 | 0.000 | 0.714 | 0.333 | 0.038 | -0.169 | -0.171 | 0.187 | -0.027 | 0.096 |

## high-intensity contradiction diaries

| subject_id | lifelog_date | s2_case | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | top_axes | steps_sum | screen_use_00_06 | longest_screenoff_run_h | gps_radius_proxy | wifi_unique_bssid | hr_mean | top_apps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| id08 | 2024-07-26 | S2_only_low | 1 | 0 | 0 | 1 | 0 | 1 | 0 | rest_quiet:+1.97, low_activity:+1.28, night_phone:-1.26 | 991.000 | 12.000 | 4.000 | nan | nan | 98.530 | 시스템 ui(57m), one ui 홈(44m), 카카오톡(35m), 클래시 로얄(13m) |
| id06 | 2024-06-03 | S2_only_low | 0 | 0 | 0 | 1 | 0 | 0 | 1 | low_activity:+2.23, rest_quiet:-1.36, physio_light_low:-0.84 | 2457.000 | 0.000 | 1.000 | 0.020 | 221.000 | 89.400 |  |
| id07 | 2024-06-09 | S2_only_high | 0 | 1 | 1 | 1 | 1 | 0 | 0 | rest_quiet:-1.77, low_activity:+1.60, low_mobility_context:+1.46 | 2191.000 | 0.000 | 0.000 | 0.000 | 57.000 | 85.370 | one ui 홈(74m), instagram(35m), 타임스프레드(31m), facebook(26m) |
| id03 | 2024-08-29 | S2_only_low | 1 | 1 | 0 | 1 | 0 | 1 | 0 | rest_quiet:+2.59, low_activity:+1.27, night_phone:-0.92 | 4322.000 | 0.000 | 7.000 | 0.020 | 716.000 | 88.790 | 시스템 ui(203m), 카카오톡(191m), one ui 홈(109m), samsung wallet(20m) |
| id01 | 2024-07-13 | S2_only_low | 0 | 1 | 1 | 1 | 0 | 1 | 0 | phone_internal:-1.46, physio_light_low:+1.39, low_mobility_context:+0.91 | 0.000 | 0.000 | 7.000 | 0.010 | 154.000 | 85.000 | one ui 홈(109m), ✝️성경일독q(108m), royal match(53m), naver(45m) |
| id01 | 2024-08-25 | S2_only_low | 1 | 1 | 1 | 1 | 0 | 1 | 1 | low_mobility_context:+1.45, phone_internal:-1.06, physio_light_low:+1.03 | nan | 0.000 | 7.000 | 0.020 | 117.000 | nan | ✝️성경일독q(146m), one ui 홈(119m), 카카오톡(57m), 캐시워크(53m) |
| id08 | 2024-08-16 | S2_only_low | 0 | 1 | 0 | 1 | 0 | 1 | 0 | low_activity:-1.50, phone_internal:+1.34, low_mobility_context:+1.03 | nan | 46.000 | 3.000 | nan | 17.000 | nan | one ui 홈(148m), 시스템 ui(126m), 카카오톡(72m), youtube(65m) |
| id08 | 2024-09-16 | S2_only_low | 1 | 0 | 0 | 1 | 0 | 1 | 0 | low_activity:+1.14, low_mobility_context:+1.05, night_phone:-0.81 | nan | 16.000 | 2.000 | nan | 11.000 | nan | 시스템 ui(85m), one ui 홈(67m), youtube(33m), 클래시 로얄(29m) |
| id01 | 2024-08-23 | S2_only_low | 1 | 0 | 0 | 1 | 0 | 1 | 0 | low_mobility_context:-1.96, rest_quiet:+0.89, physio_light_low:-0.72 | 0.000 | 0.000 | 7.000 | 1.220 | 630.000 | 96.230 | one ui 홈(151m), ✝️성경일독q(147m), meitu(75m), youtube(63m) |
| id10 | 2024-07-06 | S2_only_low | 1 | 1 | 1 | 1 | 0 | 1 | 0 | physio_light_low:+1.38, low_mobility_context:+1.33, phone_internal:-0.85 | 568.000 | 171.000 | 2.000 | 0.000 | 85.000 | 88.410 | nonogram elf(119m), x(104m), one ui 홈(87m), 배달의민족(50m) |
| id08 | 2024-06-28 | S2_only_low | 1 | 1 | 1 | 1 | 0 | 0 | 1 | night_phone:+1.33, phone_internal:+0.97, low_activity:-0.85 | 3882.000 | 55.000 | 2.000 | 0.060 | 183.000 | 95.980 | one ui 홈(262m), 시스템 ui(111m), 카카오톡(52m), youtube(42m) |
| id09 | 2024-07-05 | S2_only_low | 1 | 0 | 1 | 1 | 0 | 1 | 0 | low_mobility_context:+1.19, night_phone:+0.93, phone_internal:-0.91 | 1541.000 | 114.000 | 2.000 | 0.000 | 142.000 | 73.050 | tiktok(87m), microsoft launcher(77m), 카카오톡(32m), 계산기(25m) |
| id08 | 2024-08-11 | S2_only_high | 0 | 1 | 1 | 0 | 1 | 1 | 0 | low_activity:-1.50, physio_light_low:+1.29, low_mobility_context:+1.06 | nan | 13.000 | 3.000 | nan | 8.000 | nan | one ui 홈(105m), 시스템 ui(82m), google play 스토어(44m), 클래시 로얄(30m) |
| id10 | 2024-07-09 | S2_only_low | 0 | 1 | 1 | 1 | 0 | 1 | 0 | rest_quiet:+2.76, night_phone:-0.74, low_mobility_context:-0.48 | 5035.000 | 0.000 | 6.000 | 0.040 | 481.000 | 94.020 | 카카오톡(109m), one ui 홈(74m), nonogram elf(60m), instagram(53m) |
| id03 | 2024-08-11 | S2_only_low | 1 | 1 | 1 | 1 | 0 | 1 | 0 | phone_internal:+1.26, night_phone:+0.84, low_mobility_context:+0.81 | 3748.000 | 0.000 | 6.000 | 0.010 | 135.000 | 78.700 | one ui 홈(142m), instagram(116m), 시스템 ui(110m), 카카오톡(96m) |
| id10 | 2024-09-14 | S2_only_low | 1 | 0 | 0 | 1 | 0 | 0 | 1 | physio_light_low:+1.20, rest_quiet:-0.94, night_phone:+0.81 | 941.000 | 143.000 | 1.000 | 0.030 | 211.000 | 87.260 | 카카오톡(183m), threads(159m), one ui 홈(156m), instagram(110m) |
| id07 | 2024-07-31 | S2_only_low | 0 | 0 | 0 | 1 | 0 | 1 | 0 | rest_quiet:+2.11, low_activity:+0.85, phone_internal:-0.75 | 3453.000 | 23.000 | 5.000 | 0.050 | 301.000 | 86.610 | number match(127m), one ui 홈(38m), 타임스프레드(34m), naver(17m) |
| id02 | 2024-08-22 | S2_only_high | 0 | 1 | 0 | 0 | 1 | 1 | 0 | phone_internal:+1.46, night_phone:+1.45, low_mobility_context:-1.03 | 6291.000 | 1.000 | 5.000 | 0.610 | 1176.000 | 76.020 | 시스템 ui(275m), 카카오톡(161m), naver(118m), one ui 홈(99m) |
| id08 | 2024-07-28 | S2_only_high | 0 | 1 | 1 | 0 | 1 | 0 | 1 | night_phone:-1.04, low_mobility_context:+1.03, phone_internal:-0.91 | nan | 5.000 | 4.000 | nan | 20.000 | nan | one ui 홈(88m), 시스템 ui(44m), google play 스토어(36m), 카카오톡(31m) |
| id03 | 2024-07-21 | S2_only_high | 1 | 1 | 1 | 1 | 1 | 0 | 0 | low_mobility_context:-1.32, physio_light_low:-1.21, rest_quiet:-0.70 | 5312.000 | 54.000 | 2.000 | 0.240 | 249.000 | 87.360 | one ui 홈(105m), 시스템 ui(86m), instagram(55m), 카카오톡(45m) |
| id09 | 2024-08-23 | S2_only_high | 0 | 0 | 0 | 0 | 1 | 0 | 1 | low_mobility_context:+1.08, physio_light_low:+1.02, phone_internal:-0.85 | 755.000 | 95.000 | 2.000 | 0.000 | 111.000 | 73.220 | microsoft launcher(74m), tiktok(61m), 배달의민족(20m), 카카오톡(14m) |
| id05 | 2024-09-07 | S2_only_low | 0 | 1 | 0 | 1 | 0 | 0 | 1 | rest_quiet:+1.75, night_phone:-0.89, phone_internal:-0.67 | 11277.000 | 0.000 | 10.000 | 0.040 | 862.000 | 102.410 | 캐시워크(142m), one ui 홈(74m), 시스템 ui(64m), 카카오톡(23m) |
| id08 | 2024-07-15 | S2_only_high | 1 | 1 | 1 | 0 | 1 | 0 | 1 | low_activity:-0.95, physio_light_low:-0.82, low_mobility_context:-0.79 | 3953.000 | 55.000 | 4.000 | 0.060 | 385.000 | 99.020 | 시스템 ui(212m), one ui 홈(185m), 카카오톡(67m), 당근(65m) |
| id10 | 2024-07-13 | S2_only_high | 0 | 1 | 1 | 0 | 1 | 0 | 1 | low_activity:-1.19, physio_light_low:-0.95, night_phone:+0.82 | 4321.000 | 117.000 | 2.000 | 0.040 | 480.000 | 103.890 | 카카오톡(227m), one ui 홈(211m), instagram(116m), nonogram elf(57m) |
| id10 | 2024-08-27 | S2_only_low | 1 | 1 | 1 | 1 | 0 | 1 | 0 | low_activity:+1.35, rest_quiet:-0.94, low_mobility_context:-0.39 | 3377.000 | 253.000 | 1.000 | 0.040 | 410.000 | 93.130 | one ui 홈(148m), 카카오톡(142m), instagram(96m), threads(63m) |
| id05 | 2024-09-04 | S2_only_low | 0 | 0 | 1 | 1 | 0 | 0 | 1 | physio_light_low:-0.94, low_mobility_context:-0.84, low_activity:-0.78 | 4902.000 | 0.000 | 8.000 | 0.400 | 521.000 | 94.530 | 캐시워크(110m), one ui 홈(83m), 시스템 ui(61m), naver(47m) |
| id07 | 2024-07-02 | S2_only_high | 0 | 1 | 0 | 1 | 1 | 0 | 0 | phone_internal:+1.43, low_mobility_context:-0.91, rest_quiet:+0.50 | 5082.000 | 0.000 | 7.000 | 0.060 | 766.000 | 91.540 | one ui 홈(154m), naver(65m), 타임스프레드(61m), 카카오톡(42m) |
| id08 | 2024-07-18 | S2_only_low | 1 | 1 | 1 | 1 | 0 | 0 | 1 | night_phone:+1.63, low_mobility_context:-0.78, phone_internal:+0.48 | 3250.000 | 99.000 | 3.000 | 0.060 | 342.000 | 94.340 | 시스템 ui(155m), one ui 홈(145m), youtube(85m), 클래시 로얄(42m) |
| id09 | 2024-07-27 | S2_only_high | 1 | 1 | 0 | 1 | 1 | 0 | 0 | physio_light_low:+1.22, low_mobility_context:+1.13, phone_internal:-0.52 | 352.000 | 36.000 | 3.000 | 0.000 | 92.000 | 72.800 | microsoft launcher(75m), whiteout survival(50m), 배달의민족(44m), tiktok(35m) |
| id10 | 2024-09-05 | S2_only_low | 1 | 0 | 0 | 1 | 0 | 1 | 0 | low_mobility_context:-0.93, night_phone:-0.65, physio_light_low:-0.62 | 5609.000 | 25.000 | 3.000 | 0.040 | 709.000 | 98.190 | one ui 홈(84m), 카카오톡(73m), threads(50m), instagram(42m) |
| id03 | 2024-09-01 | S2_only_high | 1 | 1 | 1 | 1 | 1 | 0 | 0 | night_phone:-0.85, rest_quiet:+0.71, phone_internal:-0.67 | 1080.000 | 0.000 | 7.000 | 0.010 | 199.000 | 84.410 | 시스템 ui(110m), one ui 홈(91m), 카카오톡(78m), instagram(65m) |
| id04 | 2024-09-06 | S2_only_high | 0 | 1 | 1 | 0 | 1 | 1 | 0 | phone_internal:-1.01, night_phone:-0.99, low_activity:-0.57 | 6019.000 | 0.000 | 6.000 | 0.020 | 298.000 | 95.500 | one ui 홈(102m), 시스템 ui(47m), 당근(40m), 카카오톡(29m) |
| id03 | 2024-07-29 | S2_only_high | 1 | 0 | 0 | 0 | 1 | 1 | 0 | night_phone:+1.32, phone_internal:+0.95, low_activity:-0.55 | 8793.000 | 49.000 | 4.000 | 0.020 | 253.000 | 102.040 | 카카오톡(238m), one ui 홈(217m), 시스템 ui(213m), instagram(89m) |
| id08 | 2024-08-30 | S2_only_low | 1 | 1 | 1 | 1 | 0 | 1 | 0 | low_mobility_context:+1.03, physio_light_low:+0.89, night_phone:+0.84 | nan | 74.000 | 3.000 | nan | 19.000 | nan | one ui 홈(166m), 시스템 ui(92m), 클래시 로얄(77m), youtube(53m) |
| id03 | 2024-09-04 | S2_only_low | 1 | 1 | 0 | 1 | 0 | 1 | 0 | physio_light_low:-1.32, rest_quiet:-0.70, phone_internal:+0.57 | 4446.000 | 20.000 | 2.000 | 0.010 | 445.000 | 104.380 | one ui 홈(153m), 시스템 ui(149m), 카카오톡(124m), instagram(120m) |
| id03 | 2024-09-02 | S2_only_high | 1 | 1 | 1 | 1 | 1 | 0 | 0 | night_phone:-1.07, phone_internal:+0.80, rest_quiet:+0.43 | 7861.000 | 1.000 | 6.000 | 0.020 | 493.000 | 87.930 | 카카오톡(265m), one ui 홈(161m), 시스템 ui(150m), naver(57m) |
| id05 | 2024-10-26 | S2_only_high | 1 | 0 | 1 | 1 | 1 | 0 | 0 | low_activity:-1.00, phone_internal:-0.81, night_phone:-0.52 | 11833.000 | 0.000 | 6.000 | 0.000 | 319.000 | 107.550 | 캐시워크(111m), one ui 홈(56m), 카카오톡(36m), 시스템 ui(33m) |
| id05 | 2024-09-15 | S2_only_low | 1 | 0 | 1 | 1 | 0 | 0 | 1 | phone_internal:-1.31, night_phone:-0.83, physio_light_low:+0.36 | 4795.000 | 12.000 | 5.000 | 0.030 | 416.000 | 88.920 | 캐시워크(108m), 시스템 ui(40m), one ui 홈(23m), youtube(21m) |
| id03 | 2024-08-14 | S2_only_high | 1 | 1 | 1 | 1 | 1 | 0 | 0 | phone_internal:-1.21, low_activity:+0.75, night_phone:-0.44 | 10349.000 | 109.000 | 4.000 | 0.010 | 223.000 | 95.040 | 시스템 ui(121m), 카카오톡(90m), one ui 홈(39m), 시계(20m) |
| id05 | 2024-10-24 | S2_only_high | 1 | 0 | 1 | 1 | 1 | 0 | 0 | physio_light_low:+0.82, low_mobility_context:+0.79, phone_internal:-0.46 | nan | 2.000 | 5.000 | 0.040 | 146.000 | nan | 캐시워크(63m), one ui 홈(50m), youtube(49m), 시스템 ui(46m) |

