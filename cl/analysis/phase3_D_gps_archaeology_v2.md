# Phase 3D — GPS archaeology v2

## 핵심 요약

- GPS dominant-cell share를 rounding precision 2~5로 다시 계산했다.
- id09와 id10은 같은 “low home”처럼 보여도 다르게 처리해야 한다. id09는 좌표 precision/noise 문제일 가능성, id10은 실제 nomad regime 가능성이 핵심이다.
- precision 변화에 따라 dominant-cell share가 회복되면 noise-splitting, precision을 낮춰도 낮으면 nomad/multi-place 생활로 해석한다.

## id09/id10 precision summary

| subject_id   |   precision | home_cell       |   home_share_all_records |   unique_cells |   records |
|:-------------|------------:|:----------------|-------------------------:|---------------:|----------:|
| id09         |           2 | 0.03,0.49       |                   0.6341 |            175 |     91247 |
| id09         |           3 | 0.026,0.493     |                   0.5699 |            827 |     91247 |
| id09         |           4 | 0.0256,0.4931   |                   0.2598 |           3543 |     91247 |
| id09         |           5 | 0.04739,0.4594  |                   0.0293 |          10346 |     91247 |
| id10         |           2 | 0.05,0.1        |                   0.5513 |             49 |     58303 |
| id10         |           3 | 0.05,0.096      |                   0.5306 |            581 |     58303 |
| id10         |           4 | 0.05,0.096      |                   0.403  |           2929 |     58303 |
| id10         |           5 | 0.05003,0.09603 |                   0.0613 |           5325 |     58303 |

## GPS home share와 target link

|   precision | label   |   corr_home_share |   corr_unique_cells |
|------------:|:--------|------------------:|--------------------:|
|           3 | Q1      |           -0.0052 |              0.1085 |
|           4 | Q1      |            0.0262 |              0.081  |
|           3 | Q2      |            0.1017 |             -0.0647 |
|           4 | Q2      |            0.1856 |             -0.1099 |
|           3 | Q3      |            0.1304 |              0.1029 |
|           4 | Q3      |            0.1379 |              0.057  |
|           3 | S1      |            0.1461 |              0.0441 |
|           4 | S1      |           -0.0272 |              0.0507 |
|           3 | S2      |            0.0767 |              0.0049 |
|           4 | S2      |           -0.1121 |              0.008  |
|           3 | S3      |            0.0101 |              0.0472 |
|           4 | S3      |           -0.1538 |              0.064  |
|           3 | S4      |            0.0082 |              0.0329 |
|           4 | S4      |           -0.0922 |             -0.0015 |

## 해석

- id09는 corrected home-stay / location entropy feature를 재계산할 후보이다.
- id10은 home-stay ratio보다 mobility radius, dominant-place stability, sleep-location consistency 같은 nomad-aware feature가 더 적절하다.
- sparse GPS/context는 subject fingerprint 위험이 있으므로 subject-debiased 또는 within-subject 검증을 통과해야 한다.

## 산출물

- `analysis/phase3_gps_precision_home_summary.csv`
- `analysis/phase3_gps_daily_home_precision.csv`
- `analysis/phase3_gps_home_label_link.csv`
- `analysis/figures/p3_D_gps_home_recovery.png`
