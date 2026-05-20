# GPS Probe

## Verdict
GPS is usable, but should be treated as anonymized relative mobility data, not real map coordinates.

## Table Structure
- rows: 800611 minute-level rows
- raw points inside list column: 8546932
- subjects: 10
- time range: 2024-06-03 12:57:00 to 2024-11-19 23:59:00
- point count per minute row median: 11

## Coverage On Target Days
| split | days | available | availability | median_minute_rows | median_points | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| test | 250 | 235 | 0.94 | 1387 | 1.429e+04 | 24 |
| train | 450 | 425 | 0.9444 | 1387 | 1.272e+04 | 24 |

## Coverage By Subject
| subject_id | split | days | available | median_minute_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- |
| id01 | test | 27 | 27 | 1431 | 24 |
| id01 | train | 41 | 41 | 1436 | 24 |
| id02 | test | 32 | 32 | 1416 | 24 |
| id02 | train | 48 | 48 | 1422 | 24 |
| id03 | test | 21 | 21 | 1277 | 23 |
| id03 | train | 33 | 33 | 1318 | 24 |
| id04 | test | 27 | 27 | 1440 | 24 |
| id04 | train | 57 | 57 | 1440 | 24 |
| id05 | test | 21 | 21 | 1369 | 24 |
| id05 | train | 44 | 44 | 1348 | 24 |
| id06 | test | 24 | 24 | 1386 | 24 |
| id06 | train | 48 | 48 | 1408 | 24 |
| id07 | test | 30 | 30 | 773.5 | 22 |
| id07 | train | 49 | 49 | 806 | 22 |
| id08 | test | 19 | 4 | 707.5 | 14 |
| id08 | train | 56 | 31 | 1211 | 22 |
| id09 | test | 27 | 27 | 1433 | 24 |
| id09 | train | 41 | 41 | 1432 | 24 |
| id10 | test | 22 | 22 | 1132 | 24 |
| id10 | train | 33 | 33 | 1001 | 24 |

## Point Numeric Stats
| stat | lat | lon | alt | speed |
| --- | --- | --- | --- | --- |
| count | 8.547e+06 | 8.547e+06 | 8.547e+06 | 8.547e+06 |
| mean | 0.5876 | 0.4701 | 99.34 | 0.8493 |
| std | 0.5428 | 0.3166 | 36.26 | 3.938 |
| min | 0 | 0 | -627.2 | 0 |
| 0.1% | 0.002439 | 0.007097 | -53.7 | 0 |
| 1% | 0.02491 | 0.01167 | 33.1 | 0 |
| 5% | 0.02557 | 0.0684 | 58.8 | 0 |
| 50% | 0.476 | 0.4931 | 99.8 | 0.064 |
| 95% | 1.418 | 1.032 | 149.9 | 2.96 |
| 99% | 2.417 | 1.119 | 177.7 | 19.68 |
| 99.9% | 2.636 | 2.223 | 446.3 | 62.75 |
| max | 2.749 | 2.47 | 1249 | 246.7 |

## Speed Outlier Rates
| threshold | rate |
| --- | --- |
| 0 | 0.801 |
| 0.5 | 0.153 |
| 1 | 0.1011 |
| 2 | 0.0603 |
| 5 | 0.03851 |
| 10 | 0.02415 |
| 20 | 0.009718 |
| 50 | 0.001286 |
| 100 | 3.51e-07 |

## Subject Coordinate And Speed Ranges
| subject_id | points | lat_min | lat_max | lon_min | lon_max | lat_std | lon_std | speed_median | speed_p95 | speed_p99 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id01 | 778064 | 0 | 1.705 | 0 | 1.806 | 0.1291 | 0.1436 | 0.0509 | 1.999 | 14.93 |
| id02 | 1156464 | 0 | 2.749 | 0 | 2.47 | 0.4523 | 0.3468 | 0.0905 | 14.49 | 36.55 |
| id03 | 627880 | 0 | 0.612 | 0 | 0.9162 | 0.06072 | 0.06274 | 0.0549 | 2.491 | 14.21 |
| id04 | 1346026 | 0 | 1.37 | 0 | 1.003 | 0.06773 | 0.04173 | 0.009 | 1.239 | 17.42 |
| id05 | 881329 | 0.02551 | 2.382 | 0.1268 | 1.952 | 0.3273 | 0.1245 | 0.1213 | 5.107 | 25.45 |
| id06 | 889363 | 0 | 0.982 | 0.03751 | 1.485 | 0.06207 | 0.1668 | 0.1566 | 3.641 | 20.33 |
| id07 | 731705 | 0.3999 | 0.5907 | 0.02009 | 0.1801 | 0.01393 | 0.03613 | 0.2617 | 4.011 | 10.18 |
| id08 | 259521 | 0 | 0.09086 | 0 | 0.1279 | 0.009153 | 0.04661 | 0.0382 | 1.165 | 14.81 |
| id09 | 1317272 | 0 | 1.268 | 0 | 0.6142 | 0.08287 | 0.03371 | 0.0013 | 0.646 | 7.299 |
| id10 | 559308 | 0 | 0.0573 | 0 | 0.1102 | 0.01109 | 0.03175 | 0.0436 | 0.7746 | 7.936 |

## Day Feature Stats
| stat | raw_points | speed_mean | speed_p95 | speed_max | stationary_rate | moving_rate | lat_std | lon_std | alt_std | active_hours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| count | 660 | 660 | 660 | 660 | 660 | 660 | 660 | 660 | 660 | 660 |
| mean | 1.295e+04 | 0.8535 | 4.421 | 27.17 | 0.8339 | 0.07656 | 0.04934 | 0.03768 | 18.79 | 22.53 |
| std | 4181 | 0.985 | 6.394 | 19.23 | 0.1368 | 0.08321 | 0.1233 | 0.09323 | 21.98 | 3.505 |
| min | 2 | 0.01871 | 0.0069 | 0.2358 | 0 | 0 | 2.462e-06 | 4.098e-06 | 0 | 1 |
| 5% | 6203 | 0.07323 | 0.2343 | 5.88 | 0.5331 | 0.002689 | 5.71e-05 | 6.215e-05 | 1.245 | 15.95 |
| 50% | 1.312e+04 | 0.5453 | 1.492 | 24.93 | 0.8731 | 0.05 | 0.009891 | 0.0149 | 11.78 | 24 |
| 95% | 2.029e+04 | 2.999 | 19.21 | 75.08 | 0.9799 | 0.2813 | 0.4568 | 0.1522 | 51.22 | 24 |
| max | 2.272e+04 | 6.565 | 60.47 | 246.7 | 1 | 0.6 | 0.7749 | 0.9711 | 219.6 | 24 |

## Timestamp Continuity
| subject_id | minute_rows | median_gap_min | p95_gap_min | gaps_over_10m_rate |
| --- | --- | --- | --- | --- |
| id01 | 84634 | 1 | 1 | 0.003391 |
| id02 | 110860 | 1 | 1 | 0.0006585 |
| id03 | 67407 | 1 | 1 | 0.001884 |
| id04 | 119508 | 1 | 1 | 0.0001339 |
| id05 | 78434 | 1 | 1 | 0.001696 |
| id06 | 95325 | 1 | 1 | 0.001081 |
| id07 | 61866 | 1 | 1 | 0.01694 |
| id08 | 33027 | 1 | 1 | 0.00215 |
| id09 | 91247 | 1 | 1 | 0.0005918 |
| id10 | 58303 | 1 | 1 | 0.01117 |

## Recommended Use
- Use daily mobility features: active hours, point count, stationary/moving rate, speed quantiles, coordinate spread, altitude variation.
- Use within-subject deviations: today's mobility compared to that subject's usual mobility.
- Use robust clipping for speed/altitude outliers before feeding neural models.
- Do not use absolute geographic meaning; coordinates look transformed/anonymized and should not be mapped to real places.
