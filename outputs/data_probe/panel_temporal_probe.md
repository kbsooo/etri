# Panel and temporal probe

## Split timing
| subject_id | n_days | n_train | n_test | date_min | date_max | train_after_first_test | pattern_head | pattern_tail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id01 | 68 | 41 | 27 | 2024-06-26 | 2024-09-14 | 13 | TTTTTTTTTTTTTTTTTTTTTTTTTTTTPPPPPPPPPPPPPPTTTTTTTT | TTTTTTTTTTPPPPPPPPPPPPPPTTTTTTTTTTTTTPPPPPPPPPPPPP |
| id02 | 80 | 48 | 32 | 2024-07-17 | 2024-10-15 | 16 | TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTPPPPPPPPPPPPPPPPTT | TTPPPPPPPPPPPPPPPPTTTTTTTTTTTTTTTTPPPPPPPPPPPPPPPP |
| id03 | 54 | 33 | 21 | 2024-07-17 | 2024-10-09 | 11 | TTTTTTTTTTTTTTTTTTTTTTPPPPPPPPPPPTTTTTTTTTTTPPPPPP | TTTTTTTTTTTTTTTTTTPPPPPPPPPPPTTTTTTTTTTTPPPPPPPPPP |
| id04 | 84 | 57 | 27 | 2024-07-31 | 2024-10-29 | 23 | TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTPTPPPPPTTPPPPPPP | PTPPPPPTTPPPPPPPPTTTTTTTTTTTTTTTTTPPPPPPTPTPPPTPPP |
| id05 | 65 | 44 | 21 | 2024-08-28 | 2024-11-19 | 18 | TTTTTTTTTTTTTTTTTTTTTTTTTTPPPPPPPTPPPPPTTTTTTTTTTT | TTTTTTTTTTTPPPPPPPTPPPPPTTTTTTTTTTTTTPPTTTPPTPPPPP |
| id06 | 72 | 48 | 24 | 2024-06-03 | 2024-08-24 | 18 | TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTPPPPPPPPTPPPPPTTTTTT | TTTTTTTTPPPPPPPPTPPPPPTTTTTTTTTTTTTTPTPPPPTTPPPPPP |
| id07 | 79 | 49 | 30 | 2024-06-09 | 2024-09-01 | 16 | TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTPPPPPPPPPPPPPPPTT | TTTTPPPPPPPPPPPPPPPTTTTTTTTTTTTTTTTPPPPPPPPPPPPPPP |
| id08 | 75 | 56 | 19 | 2024-06-25 | 2024-09-19 | 24 | TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTPPTTPPPPPPTPPTTTTT | TTTTTTTPPTTPPPPPPTPPTTTTTTTTTTTTTTTTTPTPPPPTPPTTPP |
| id09 | 68 | 41 | 27 | 2024-07-01 | 2024-09-21 | 13 | TTTTTTTTTTTTTTTTTTTTTTTTTTTTPPPPPPPPPPPPPPTTTTTTTT | TTTTTTTTTTPPPPPPPPPPPPPPTTTTTTTTTTTTTPPPPPPPPPPPPP |
| id10 | 55 | 33 | 22 | 2024-07-06 | 2024-09-26 | 11 | TTTTTTTTTTTTTTTTTTTTTTPPPPPPPPPPPTTTTTTTTTTTPPPPPP | TTTTTTTTTTTTTTTTTPPPPPPPPPPPTTTTTTTTTTTPPPPPPPPPPP |

## Test rows near labeled rows of same subject
| count | median_gap | p90_gap | max_gap | within_1d | within_2d | within_3d | within_5d | within_7d | within_14d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 250 | 4 | 12 | 27 | 0.2 | 0.344 | 0.488 | 0.656 | 0.768 | 0.936 |

## Adjacent labeled-day persistence
| target | adjacent_same_rate | marginal_same_baseline | lift_vs_marginal |
| --- | --- | --- | --- |
| Q1 | 0.6208 | 0.5044 | 0.1163 |
| Q2 | 0.6594 | 0.5622 | 0.0972 |
| Q3 | 0.6546 | 0.6 | 0.05459 |
| S4 | 0.5894 | 0.56 | 0.02937 |
| S3 | 0.6522 | 0.6622 | -0.01005 |
| S1 | 0.6522 | 0.6822 | -0.03005 |
| S2 | 0.6184 | 0.6511 | -0.03275 |

## Subject target-rate ranges
| target | min | max | range | std |
| --- | --- | --- | --- | --- |
| S3 | 0.1364 | 0.9583 | 0.822 | 0.2475 |
| Q1 | 0.1458 | 0.8485 | 0.7027 | 0.1754 |
| S4 | 0.1515 | 0.8542 | 0.7027 | 0.1947 |
| S2 | 0.25 | 0.9167 | 0.6667 | 0.2186 |
| S1 | 0.4464 | 0.9375 | 0.4911 | 0.1802 |
| Q2 | 0.3958 | 0.8182 | 0.4223 | 0.1469 |
| Q3 | 0.439 | 0.7719 | 0.3329 | 0.1239 |

## Top association feature families
| family | count | mean | max |
| --- | --- | --- | --- |
| subject | 5 | 0.07269 | 0.1108 |
| mScreen | 3 | 0.06398 | 0.07572 |
| mWifi | 9 | 0.06239 | 0.07568 |
| mBle | 8 | 0.06204 | 0.07712 |
| wLight | 3 | 0.06151 | 0.06479 |
| wPedo | 9 | 0.05853 | 0.07183 |
| mUsage | 3 | 0.05824 | 0.06737 |
| mGps | 10 | 0.05723 | 0.07424 |
| mUsage_app_vocab | 19 | 0.05598 | 0.0734 |
| mAC | 2 | 0.05507 | 0.05532 |
| hr | 10 | 0.05484 | 0.08781 |
| mLight | 2 | 0.05277 | 0.05541 |
| mAmbience | 1 | 0.04888 | 0.04888 |

## Sensor-nearest-neighbor label smoothness
| k | target | neighbor_same_rate |
| --- | --- | --- |
| 1 | Q1 | 0.56 |
| 1 | Q2 | 0.5667 |
| 1 | Q3 | 0.5956 |
| 1 | S1 | 0.6444 |
| 1 | S2 | 0.6156 |
| 1 | S3 | 0.64 |
| 1 | S4 | 0.5867 |
| 3 | Q1 | 0.5481 |
| 3 | Q2 | 0.5667 |
| 3 | Q3 | 0.5881 |
| 3 | S1 | 0.6222 |
| 3 | S2 | 0.5993 |
| 3 | S3 | 0.6422 |
| 3 | S4 | 0.5726 |
| 7 | Q1 | 0.5384 |
| 7 | Q2 | 0.5463 |
| 7 | Q3 | 0.5663 |
| 7 | S1 | 0.6073 |
| 7 | S2 | 0.6175 |
| 7 | S3 | 0.6343 |
| 7 | S4 | 0.5714 |

## Raw table budget for self-supervised/pretext learning
| file | rows | subjects | time_min | time_max |
| --- | --- | --- | --- | --- |
| ch2025_mACStatus.parquet | 939896 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 |
| ch2025_mActivity.parquet | 961062 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 |
| ch2025_mAmbience.parquet | 476577 | 10 | 2024-06-03 13:00:10 | 2024-11-19 23:58:10 |
| ch2025_mBle.parquet | 21830 | 10 | 2024-06-03 13:07:00 | 2024-11-19 21:27:00 |
| ch2025_mGps.parquet | 800611 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 |
| ch2025_mLight.parquet | 96258 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:57:00 |
| ch2025_mScreenStatus.parquet | 939653 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 |
| ch2025_mUsageStats.parquet | 45197 | 10 | 2024-06-09 11:00:00 | 2024-11-19 22:10:00 |
| ch2025_mWifi.parquet | 76336 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:57:00 |
| ch2025_wHr.parquet | 382918 | 10 | 2024-06-03 14:28:00 | 2024-11-19 15:37:00 |
| ch2025_wLight.parquet | 633741 | 10 | 2024-06-03 14:28:00 | 2024-11-19 23:59:00 |
| ch2025_wPedo.parquet | 748100 | 10 | 2024-06-03 14:15:00 | 2024-11-19 23:59:00 |
