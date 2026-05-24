# Phase 3C — Long-rest / vacation event study

## 핵심 요약

- long-rest proxy 후보: `s4x_cross_quiet_longest_h, s4x_cross_screenoff_longest_h, longest_screenoff_run_h, longest_quiet_run_h`.
- 12h+ long-rest는 system anomaly로 제거하기보다 subject-specific behavior event 후보로 보는 것이 안전하다.
- 특히 id06의 long-rest row는 Q2/Q3 event grammar와 연결될 가능성이 있어 별도 추적 대상이다.

## Long-rest event counts by subject

| subject_id   |   long_rest |   normal |   post_long_rest |   pre_long_rest |
|:-------------|------------:|---------:|-----------------:|----------------:|
| id01         |           7 |       22 |                6 |               6 |
| id02         |           8 |       27 |                6 |               7 |
| id03         |          11 |        9 |                5 |               8 |
| id04         |           2 |       53 |                1 |               1 |
| id05         |           9 |       21 |                7 |               7 |
| id06         |           6 |       33 |                4 |               5 |
| id07         |           5 |       36 |                3 |               5 |
| id08         |           6 |       38 |                6 |               6 |
| id09         |           9 |       19 |                6 |               7 |
| id10         |          11 |        9 |                6 |               7 |

## Event class label rates

| event_class    |   Q1_mean |   Q1_count |   Q2_mean |   Q2_count |   Q3_mean |   Q3_count |   S1_mean |   S1_count |   S2_mean |   S2_count |   S3_mean |   S3_count |   S4_mean |   S4_count |
|:---------------|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|
| long_rest      |    0.527  |         74 |    0.6216 |         74 |    0.5946 |         74 |    0.6622 |         74 |    0.5811 |         74 |    0.6216 |         74 |    0.5676 |         74 |
| normal         |    0.4906 |        267 |    0.5693 |        267 |    0.6142 |        267 |    0.7116 |        267 |    0.6854 |        267 |    0.6854 |        267 |    0.5543 |        267 |
| post_long_rest |    0.46   |         50 |    0.5    |         50 |    0.64   |         50 |    0.66   |         50 |    0.58   |         50 |    0.62   |         50 |    0.56   |         50 |
| pre_long_rest  |    0.5085 |         59 |    0.5085 |         59 |    0.5085 |         59 |    0.5932 |         59 |    0.6441 |         59 |    0.6441 |         59 |    0.5763 |         59 |

## Q2 transition x long-rest proxy

| Q2_transition   |     Q1 |   Q2 |     Q3 |     S1 |     S2 |     S3 |     S4 |   long_rest_proxy_h |   long_rest_event_12h |
|:----------------|-------:|-----:|-------:|-------:|-------:|-------:|-------:|--------------------:|----------------------:|
| 0_to_1          | 0.6184 |  1   | 0.75   | 0.7763 | 0.6447 | 0.6316 | 0.5132 |              7.8026 |                0.2237 |
| 1_to_0          | 0.4    |  0   | 0.4267 | 0.6    | 0.6    | 0.64   | 0.56   |              6.9733 |                0.12   |
| first/unknown   | 0.1    |  0.6 | 0.5    | 0.5    | 0.4    | 0.6    | 0.4    |              6.1    |                0.1    |
| stable_0        | 0.4576 |  0   | 0.4153 | 0.6949 | 0.6864 | 0.7203 | 0.5847 |              7.2373 |                0.1525 |
| stable_1        | 0.5322 |  1   | 0.7427 | 0.6784 | 0.6667 | 0.6491 | 0.5731 |              7.2749 |                0.1696 |

## id06 top long-rest rows

| subject_id   | lifelog_date        |   long_rest_proxy_h | event_class   |   Q1 |   Q2 |   Q3 |   S1 |   S2 |   S3 |   S4 |
|:-------------|:--------------------|--------------------:|:--------------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| id06         | 2024-06-16 00:00:00 |                  13 | long_rest     |    0 |    0 |    0 |    1 |    1 |    1 |    1 |
| id06         | 2024-08-15 00:00:00 |                  13 | long_rest     |    0 |    1 |    1 |    1 |    1 |    1 |    1 |
| id06         | 2024-06-21 00:00:00 |                  13 | long_rest     |    0 |    0 |    0 |    1 |    1 |    1 |    0 |
| id06         | 2024-07-21 00:00:00 |                  13 | long_rest     |    1 |    1 |    1 |    1 |    1 |    1 |    0 |
| id06         | 2024-08-05 00:00:00 |                  13 | long_rest     |    0 |    1 |    1 |    1 |    1 |    1 |    1 |
| id06         | 2024-06-14 00:00:00 |                  13 | long_rest     |    0 |    0 |    0 |    0 |    1 |    1 |    1 |
| id06         | 2024-08-03 00:00:00 |                  11 | normal        |    0 |    0 |    0 |    1 |    1 |    1 |    1 |
| id06         | 2024-07-28 00:00:00 |                   8 | normal        |    0 |    0 |    0 |    1 |    1 |    1 |    1 |
| id06         | 2024-07-05 00:00:00 |                   8 | normal        |    0 |    1 |    1 |    1 |    1 |    1 |    1 |
| id06         | 2024-06-28 00:00:00 |                   7 | normal        |    1 |    0 |    1 |    1 |    1 |    1 |    1 |
| id06         | 2024-08-01 00:00:00 |                   7 | normal        |    0 |    1 |    1 |    1 |    1 |    1 |    1 |
| id06         | 2024-07-01 00:00:00 |                   7 | normal        |    0 |    1 |    0 |    1 |    1 |    1 |    1 |

## 해석

- `long_rest`, `pre_long_rest`, `post_long_rest`를 분리했으므로, Q2가 피로 누적/회복/휴식 이벤트 중 어디에 반응하는지 다음 단계에서 더 볼 수 있다.
- row 수가 작기 때문에 CV 세 번째 자리식 판단보다 event direction과 subject 반복성을 우선한다.

## 산출물

- `analysis/phase3_long_rest_event_rows.csv`
- `analysis/phase3_long_rest_event_counts.csv`
- `analysis/phase3_long_rest_label_rates.csv`
- `analysis/phase3_long_rest_by_subject_rates.csv`
- `analysis/phase3_q2_transition_long_rest_table.csv`
- `analysis/figures/p3_C_long_rest_counts.png`
