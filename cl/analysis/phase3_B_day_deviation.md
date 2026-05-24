# Phase 3B — Day deviation model

## 핵심 요약

- raw value보다 `__subj_z` 기반의 subject-normalized deviation을 사용했다.
- Q2에서 high-deviation day와 low-deviation day의 label-rate 차이가 가장 해석 가능한 후보를 만든다.
- Q1은 personal anchor가 강하므로 deviation signal이 보여도 negative-control 없이 크게 쓰면 안 된다.

## Q2 deviation family signal 상위

| label   | deviation_family   |    corr |   high70_rate |   low30_rate |   high_minus_low |   n_high |   n_low |
|:--------|:-------------------|--------:|--------------:|-------------:|-----------------:|---------:|--------:|
| Q2      | gps/context        | -0.0033 |        0.5556 |       0.5185 |           0.037  |      135 |     135 |
| Q2      | routine/regularity |  0.0243 |        0.5852 |       0.5481 |           0.037  |      135 |     135 |
| Q2      | phone/app/screen   |  0.0308 |        0.5778 |       0.5556 |           0.0222 |      135 |     135 |
| Q2      | activity/step      | -0.028  |        0.5481 |       0.5778 |          -0.0296 |      135 |     135 |
| Q2      | sleep/long-rest    | -0.0271 |        0.5556 |       0.5852 |          -0.0296 |      135 |     135 |
| Q2      | other              | -0.0543 |        0.5556 |       0.5926 |          -0.037  |      135 |     135 |
| Q2      | overall            | -0.0473 |        0.5185 |       0.6    |          -0.0815 |      135 |     135 |
| Q2      | sensor/coverage    | -0.1308 |        0.4741 |       0.6593 |          -0.1852 |      135 |     135 |

## Q3 deviation family signal 상위

| label   | deviation_family   |    corr |   high70_rate |   low30_rate |   high_minus_low |   n_high |   n_low |
|:--------|:-------------------|--------:|--------------:|-------------:|-----------------:|---------:|--------:|
| Q3      | routine/regularity |  0.042  |        0.6296 |       0.5407 |           0.0889 |      135 |     135 |
| Q3      | gps/context        |  0.0242 |        0.6222 |       0.563  |           0.0593 |      135 |     135 |
| Q3      | phone/app/screen   |  0.0589 |        0.6222 |       0.563  |           0.0593 |      135 |     135 |
| Q3      | other              | -0.0029 |        0.6    |       0.6074 |          -0.0074 |      135 |     135 |
| Q3      | overall            | -0.0125 |        0.5852 |       0.5926 |          -0.0074 |      135 |     135 |

## Q1 deviation family signal 상위 — anchor/허위 signal 가능성 주의

| label   | deviation_family   |    corr |   high70_rate |   low30_rate |   high_minus_low |   n_high |   n_low |
|:--------|:-------------------|--------:|--------------:|-------------:|-----------------:|---------:|--------:|
| Q1      | routine/regularity |  0.0548 |        0.563  |       0.4519 |           0.1111 |      135 |     135 |
| Q1      | gps/context        |  0.0392 |        0.5407 |       0.4667 |           0.0741 |      135 |     135 |
| Q1      | sleep/long-rest    | -0.0045 |        0.5333 |       0.4815 |           0.0519 |      135 |     135 |
| Q1      | overall            | -0.0393 |        0.4889 |       0.4667 |           0.0222 |      135 |     135 |
| Q1      | other              | -0.0313 |        0.4741 |       0.4889 |          -0.0148 |      135 |     135 |

## 가장 unusual한 subject-days

| subject_id   | lifelog_date        |   dev_overall |   dev_activity/step |   dev_gps/context |   dev_other |   dev_phone/app/screen |   dev_routine/regularity |
|:-------------|:--------------------|--------------:|--------------------:|------------------:|------------:|-----------------------:|-------------------------:|
| id01         | 2024-06-26 00:00:00 |        1.1664 |              1.3677 |            0.787  |      1.0217 |                 1.1519 |                   1.408  |
| id01         | 2024-08-23 00:00:00 |        1.1553 |              0.8302 |            1.938  |      1.0109 |                 0.8352 |                   1.0975 |
| id05         | 2024-11-09 00:00:00 |        1.1293 |              1.1056 |            1.4254 |      1.0006 |                 1.3509 |                   1.3467 |
| id06         | 2024-06-16 00:00:00 |        1.1093 |              0.9072 |            1.7515 |      0.9753 |                 0.7311 |                   1.5682 |
| id04         | 2024-07-31 00:00:00 |        1.0708 |              1.0159 |            0.6424 |      1.0739 |                 1.0345 |                   1.0967 |
| id03         | 2024-07-19 00:00:00 |        1.0132 |              1.3395 |            1.0599 |      0.8932 |                 0.7702 |                   1.062  |
| id08         | 2024-06-26 00:00:00 |        1.0082 |              1.3233 |            0.8286 |      1.017  |                 0.8679 |                   1.0647 |
| id07         | 2024-08-12 00:00:00 |        1.0074 |              0.9068 |            1.3072 |      0.737  |                 0.7027 |                   1.1989 |
| id06         | 2024-08-04 00:00:00 |        1.0038 |              0.9225 |            0.995  |      1.013  |                 1.1352 |                   0.9764 |
| id06         | 2024-06-23 00:00:00 |        0.9991 |              0.8944 |            0.9445 |      1.0404 |                 0.7804 |                   1.0387 |
| id08         | 2024-06-25 00:00:00 |        0.9576 |              0.8078 |            0.8681 |      1.0781 |                 0.6989 |                   0.7887 |
| id09         | 2024-07-13 00:00:00 |        0.9426 |              0.8654 |            1.3108 |      0.7589 |                 1.1244 |                   0.8011 |

## 해석

- 이 분석은 “그 사람답지 않은 날”이 target과 연결되는지를 보기 위한 것이다.
- 향후 모델 번역 시 Q2는 event/deviation residual 후보, Q1은 subject anchor 이후 매우 작은 residual, S-family는 freeze/작은 cap이 기본이다.

## 산출물

- `analysis/phase3_day_deviation_scores.csv`
- `analysis/phase3_day_deviation_target_signal.csv`
- `analysis/phase3_top_deviation_features_by_target.csv`
- `analysis/phase3_unusual_days_top.csv`
- `analysis/figures/p3_B_deviation_signal_heatmap.png`
