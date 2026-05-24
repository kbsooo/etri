# Phase 3E — Cluster-aware validation sketch

## 핵심 요약

- subject-level lifestyle profile을 KMeans(k=3)로 나눴다. 목적은 점수 개선이 아니라 feature 의미가 cluster마다 달라지는지 확인하는 것이다.
- cluster별 target prevalence가 다르면 단일 global residual보다 cluster-aware cap/calibration이 더 안전하다.
- 단, subject가 10명뿐이라 cluster별 별도 대형 모델은 과적합 위험이 크다.

## Subject cluster assignment

| subject_id   | cluster          |     Q1 |     Q2 |     Q3 |     S1 |     S2 |     S3 |     S4 |
|:-------------|:-----------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| id01         | C1_mobility_rank | 0.439  | 0.561  | 0.5854 | 0.6341 | 0.5854 | 0.8537 | 0.4878 |
| id02         | C2_mobility_rank | 0.5417 | 0.6667 | 0.7292 | 0.875  | 0.9167 | 0.8958 | 0.75   |
| id03         | C1_mobility_rank | 0.8485 | 0.8182 | 0.7273 | 0.8182 | 0.5152 | 0.4848 | 0.1515 |
| id04         | C0_mobility_rank | 0.5614 | 0.4912 | 0.7719 | 0.7544 | 0.7018 | 0.5439 | 0.5088 |
| id05         | C1_mobility_rank | 0.6136 | 0.4318 | 0.6818 | 0.4773 | 0.25   | 0.1364 | 0.4091 |
| id06         | C0_mobility_rank | 0.1458 | 0.3958 | 0.5    | 0.9375 | 0.9167 | 0.9583 | 0.8542 |
| id07         | C1_mobility_rank | 0.5102 | 0.5102 | 0.5102 | 0.7959 | 0.7143 | 0.7959 | 0.4694 |
| id08         | C0_mobility_rank | 0.4107 | 0.7857 | 0.4464 | 0.4464 | 0.6071 | 0.6607 | 0.6071 |
| id09         | C1_mobility_rank | 0.5122 | 0.439  | 0.439  | 0.561  | 0.7805 | 0.7073 | 0.5854 |
| id10         | C1_mobility_rank | 0.4848 | 0.5455 | 0.6364 | 0.4848 | 0.3636 | 0.4848 | 0.6667 |

## Cluster target rates

| cluster          |   Q1_mean |   Q1_count |   Q2_mean |   Q2_count |   Q3_mean |   Q3_count |   S1_mean |   S1_count |   S2_mean |   S2_count |   S3_mean |   S3_count |   S4_mean |   S4_count |
|:-----------------|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|
| C0_mobility_rank |    0.3851 |        161 |    0.5652 |        161 |    0.5776 |        161 |    0.7019 |        161 |    0.7329 |        161 |    0.7081 |        161 |    0.646  |        161 |
| C1_mobility_rank |    0.5602 |        241 |    0.5394 |        241 |    0.5892 |        241 |    0.6307 |        241 |    0.5436 |        241 |    0.5851 |        241 |    0.4647 |        241 |
| C2_mobility_rank |    0.5417 |         48 |    0.6667 |         48 |    0.7292 |         48 |    0.875  |         48 |    0.9167 |         48 |    0.8958 |         48 |    0.75   |         48 |

## 해석

- 권장 구조는 `global anchor + cluster-aware residual/cap`이다.
- id08 같은 outlier는 포함/제외 sensitivity를 별도 확인해야 한다.
- id10 nomad cluster는 home-based feature를 약화하고 mobility/stability feature 중심으로 해석해야 한다.

## 산출물

- `analysis/phase3_lifestyle_clusters.csv`
- `analysis/phase3_lifestyle_cluster_profiles.csv`
- `analysis/phase3_lifestyle_cluster_target_rates.csv`
- `analysis/phase3_subject_cluster_label_summary.csv`
- `analysis/figures/p3_E_cluster_target_prevalence.png`
