# Contrastive Failure Atlas

## 한 줄 요약

raw KNN이 실패한 action과 raw KNN보다 더 나빠진 toxic action을 HS-JEPA human-state 공간의 prototype atlas로 만들고, test row-target action을 이 atlas에 투영했다.

## 목적

직전 safety jury는 sharp boundary를 찾았지만 supervised gain regressor 성격이 강했다. 이번 실험은 더 JEPA답게 `성공한 action representation`과 `실패한 action representation` 사이의 contrastive energy만으로 release할 cell을 고른다.

## 핵심 결과

- raw KNN OOF logloss: `0.636997`
- best atlas policy: `atlas_target_family_score_all_topfrac_0.080`
- best atlas OOF logloss: `0.635425`
- delta vs raw KNN: `-0.001572`
- OOF switched cells: `59`
- target matched-null p(gain >= observed): `0.529250`
- target+family matched-null p(gain >= observed): `0.534500`
- generated candidate: `submission_hsjepa_contrastive_failure_atlas_7a28f76d_uploadsafe.csv`
- submission priority: `low_negative_evidence_not_primary_submission`

## Best policy target counts

| target | count |
| --- | --- |
| Q1 | 53 |
| Q2 | 2 |
| Q3 | 0 |
| S1 | 0 |
| S2 | 0 |
| S3 | 2 |
| S4 | 2 |

## Best policy expert-family counts

| expert_family | count |
| --- | --- |
| prior | 53 |
| core_action_health | 3 |
| raw_action_core_health | 3 |

## Top policies

| policy_name | logloss | switched_cells | mean_realized_gain_all_cells | positive_true_gain_rate | target_null_p_ge_observed | target_family_null_p_ge_observed |
| --- | --- | --- | --- | --- | --- | --- |
| atlas_target_family_score_all_topfrac_0.080 | 0.635425 | 59 | 0.001572 | 0.542373 | 0.529250 | 0.534500 |
| atlas_target_family_score_core_or_prior_topfrac_0.080 | 0.635425 | 59 | 0.001572 | 0.542373 | 0.542250 | 0.529000 |
| atlas_target_score_all_topfrac_0.150 | 0.635495 | 110 | 0.001502 | 0.572727 | 0.066500 | 0.190250 |
| atlas_target_score_core_or_prior_topfrac_0.150 | 0.635495 | 110 | 0.001502 | 0.572727 | 0.063750 | 0.190500 |
| atlas_global_score_core_only_topfrac_0.150 | 0.635685 | 110 | 0.001312 | 0.618182 | 0.068000 | 0.207250 |
| atlas_target_family_score_all_topfrac_0.040 | 0.636050 | 29 | 0.000947 | 0.517241 | 0.561000 | 0.573250 |
| atlas_target_family_score_core_or_prior_topfrac_0.040 | 0.636050 | 29 | 0.000947 | 0.517241 | 0.556500 | 0.572250 |
| atlas_target_score_all_topfrac_0.100 | 0.636227 | 74 | 0.000771 | 0.608108 | 0.152000 | 0.356250 |
| atlas_target_score_core_or_prior_topfrac_0.100 | 0.636227 | 74 | 0.000771 | 0.608108 | 0.139750 | 0.355500 |
| atlas_contrastive_score_all_topfrac_0.020 | 0.636273 | 15 | 0.000724 | 0.600000 | 0.173750 | 0.317000 |
| atlas_contrastive_score_core_or_prior_topfrac_0.020 | 0.636273 | 15 | 0.000724 | 0.600000 | 0.181000 | 0.322000 |
| atlas_contrastive_score_all_topfrac_0.010 | 0.636372 | 7 | 0.000625 | 0.714286 | 0.148500 | 0.346000 |
| atlas_contrastive_score_core_or_prior_topfrac_0.010 | 0.636372 | 7 | 0.000625 | 0.714286 | 0.163750 | 0.333000 |
| atlas_target_family_score_all_topfrac_0.010 | 0.636419 | 7 | 0.000579 | 0.714286 | 0.276000 | 0.302250 |

## 논문용 해석

OOF 평균은 raw KNN보다 좋아졌지만, matched-null p-value가 `0.53` 수준이므로 이 결과는 `좋은 action manifold`가 안정적으로 분리됐다는 증거가 아니다.

오히려 직전 sharp boundary는 prototype geometry만으로는 잡히지 않는 얇은 non-linear boundary였다는 해석이 강해졌다. 따라서 HS-JEPA core는 인간 상태 representation으로 남고, release-grade row-target assignment에는 별도 decoder가 필요하다.

이 후보는 제출 1순위가 아니라 negative architectural evidence다. 논문에서는 `core representation alone is not a release-grade action solver`를 보여주는 ablation으로 쓰는 편이 맞다.