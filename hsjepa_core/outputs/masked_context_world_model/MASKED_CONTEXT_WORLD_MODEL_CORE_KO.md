# Masked Context World Model Core

## 한 줄 요약

HS-JEPA core를 더 직접적인 JEPA 형태로 만든 실험이다.

```text
visible lifelog views
  -> predict masked target-view representation
  -> predicted state + residual surprise energy
  -> label/action structure probe
```

이 실험은 competition adapter가 아니라 core representation probe다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## 왜 이것이 HS-JEPA core인가

이전 adapter 실험들은 `hidden state -> row-target action` 번역에 가까웠다.
이번 실험은 그보다 앞단을 본다.

```text
보이는 생활 context 일부만 보고,
보이지 않는 target-view representation을 예측할 수 있는가?
```

여기서 target은 Q/S label이 아니라 phone, body, app, mobility 같은 semantic lifelog view의 PCA representation이다.
즉 raw value reconstruction이 아니라 view-level latent prediction이다.

## Masked View Prediction 결과

- best target view: `app_social_context`
- best component corr lift vs null: `0.248882`
- best R2 lift vs null: `0.215739`

| target_view | context_feature_count | target_feature_count | components | oof_r2 | null_oof_r2 | r2_lift_vs_null | oof_component_corr | component_corr_lift_vs_null |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| app_social_context | 81 | 18 | 4 | -0.132434 | -0.348173 | 0.215739 | 0.156728 | 0.248882 |
| mobility_environment | 81 | 18 | 4 | -336.893778 | -949.237713 | 612.343935 | -0.053134 | 0.059870 |
| phone_behavior | 59 | 40 | 4 | -150.628833 | -570.943627 | 420.314794 | 0.105008 | 0.031207 |
| calendar_rhythm | 94 | 5 | 4 | -453.763173 | -1048.350472 | 594.587299 | 0.004705 | 0.000430 |
| body_activity_sleep | 81 | 18 | 4 | -1481.296505 | -5432.537774 | 3951.241269 | -0.048899 | -0.073456 |

## Grouped Label Probe

이 평가는 label을 학습하지만, representation 자체는 label 없이 만든다.
같은 subject가 train/valid 양쪽에 동시에 들어가지 않도록 GroupKFold로 검증했다.

| feature_set | logloss | auc |
| --- | --- | --- |
| prior_only | 0.677858 | 0.382414 |
| masked_world_surprise_energy | 1.062562 | 0.433075 |
| masked_world_full_state | 1.122751 | 0.455430 |
| masked_world_predicted_state | 1.173277 | 0.450871 |

요약:

- prior mean logloss: `0.677858`
- masked world full-state mean logloss: `1.122751`
- delta vs prior: `0.444894`
- world-model KNN OOF logloss: `0.715135`

이 결과는 중요한 negative evidence다. Masked world-model representation은 label-free hidden state로는 의미가 있지만,
그 자체를 direct label predictor로 쓰면 prior보다 나쁘다. 따라서 HS-JEPA core를 classifier로 포장하면 안 된다.

## Nearest-Neighbor Label Consistency

좋은 hidden state라면 가까운 row의 target vector가 random row보다 더 비슷해야 한다.

| representation | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| masked_world_predicted_state | 0.562095 | 0.530794 | 0.031302 |
| masked_world_full_state | 0.558857 | 0.528127 | 0.030730 |

## Action-Health Diagnostic

이 부분은 core-only가 아니라 adapter diagnostic이다.
cross-subject prototype transport가 만든 OOF action field를 외부 평가 대상으로 두고,
world-model residual energy가 toxic action을 분리하는지 본다.

| target | selected_score_col | selected_mode | selected_cells | selected_gain_sum | all_gain_sum | removed_gain_sum | selected_positive_gain_rate | all_positive_gain_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | wm_energy_app_social_context | low_energy_listener | 7 | 1.487267 | 0.945472 | -0.541795 | 0.857143 | 0.615385 |
| S4 | wm_energy_calendar_rhythm | high_energy_listener | 2 | 0.099617 | -0.425003 | -0.524620 | 0.500000 | 0.400000 |
| Q3 | wm_energy_mean | low_energy_listener | 5 | 1.176419 | 1.168314 | -0.008105 | 0.800000 | 0.666667 |
| Q2 | wm_energy_calendar_rhythm | low_energy_listener | 6 | 1.882835 | 1.976824 | 0.093989 | 1.000000 | 0.750000 |
| S2 | wm_energy_calendar_rhythm | low_energy_listener | 3 | 0.898557 | 1.361437 | 0.462880 | 1.000000 | 1.000000 |

## Anchor-Free Candidate

world-model state만으로 train nearest-neighbor target probability를 만든 diagnostic submission을 생성했다.

- candidate: `submission_hsjepa_masked_context_world_model_core_ff673c9a_uploadsafe.csv`

이 후보는 public LB를 맞추기 위한 파일이 아니라, core representation만으로 어디까지 갈 수 있는지 확인하는 anchor-free sensor다.

## 해석

강한 성공 조건은 다음이다.

```text
masked target-view prediction이 null보다 낫고,
그 predicted/residual state가 label consistency와 action toxicity를 동시에 설명한다.
```

실패한다면 HS-JEPA core는 human-state representation으로는 의미가 있지만,
row-target action release에는 별도의 adapter와 diagnostic이 필수라는 결론이 강화된다.
