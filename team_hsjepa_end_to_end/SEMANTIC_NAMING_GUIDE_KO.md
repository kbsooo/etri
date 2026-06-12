# HS-JEPA Semantic Naming Guide

이 문서는 팀원이 과거 내부 실험 번호를 몰라도 HS-JEPA 실험 흐름을 이해할 수 있게 하기 위한 이름 규칙이다.

## 원칙

내부 버전 번호는 재현용 파일명 안에만 둔다. 문서와 발표에서는 메커니즘 이름을 쓴다.

```text
나쁜 설명: H057이 H042 row를 쓰고 H088은 실패했다.
좋은 설명: row-state vector frontier는 Q2-support row를 hidden state로 해석했고, dual-head toxicity stress는 broad action field가 public-toxic임을 보여줬다.
```

## 핵심 역할 이름

| 역할 이름 | 의미 | 대표 파일 |
| --- | --- | --- |
| pre-HS feature frontier | HS-JEPA 이전 feature/model 기반 public plateau | `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` |
| public-equation jump | scalar public feedback을 hidden public-state equation으로 읽어 큰 점프를 만든 실험 | `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` |
| Q2 phase route | Q2-support row가 public-visible hidden state marker라는 가설 | `submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv` |
| subjective route expansion | Q1/Q3 subjective route를 추가했지만 Q2 phase route와 동률이었던 stress | `submission_h050_target_route_phase_b140216b_uploadsafe.csv` |
| row-state vector frontier | Q2-support row를 전체 Q/S hidden-state vector로 확장한 frontier | `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` |
| dual-head toxicity stress | locally coherent dual-head/Pareto action이 public에서는 toxic할 수 있음을 보인 negative sensor | `submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv` |
| target-assignment stress | target split 또는 Q3 repair 같은 micro branch가 decisive하지 않음을 보인 stress | `submission_h144_targetxor_def80b88_uploadsafe.csv`, `submission_h145_q3repair_2d818e46_uploadsafe.csv` |
| cross-listener transport | listener posterior를 release gate로 쓰는 방식이 아직 action-grade가 아님을 보인 stress | `submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv` |
| frontier active-silence | 성공한 frontier trajectory에서 release보다 abstention/silence를 action으로 본 실험 | `submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv` |
| lifelog core state evidence | public LB 없이 OG lifelog-derived context만으로 HS-JEPA core-state geometry가 무엇을 설명하는지 검증한 논문용 evidence run | `hsjepa_core/run_lifelog_core_state_evidence.py` |
| action-health separation | public LB 없이 계산한 HS-JEPA health score가 기존 positive/stress action field를 구분하는지 본 probe | `sleep_competition_adapter/action_health_separation_probe.py` |
| teacher-free core support | 기존 성공 action teacher 없이 HS-JEPA core geometry만으로 row-state frontier 일부를 재발견할 수 있는지 본 probe | `sleep_competition_adapter/teacher_free_core_support_release.py` |
| target listener route selector | OG train future split에서 target마다 어떤 representation을 들어야 하는지 고르는 HS-JEPA route benchmark | `sleep_competition_adapter/core_oof_action_health_benchmark.py` |
| contextual listener route selector | target route를 row-target별 contextual routing으로 확장할 수 있는지 검증한 boundary probe | `sleep_competition_adapter/contextual_listener_route_selector.py` |
| raw-KNN failure detector | raw lifelog KNN을 기본값으로 두고 HS-JEPA route-risk가 실패 가능성이 큰 cell만 sparse override하는 실험 | `sleep_competition_adapter/raw_knn_failure_detector.py` |

## 현재 public best 해석

현재 관측 최고점은 `frontier active-silence positive-path`다.

```text
submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv
public LB 0.5677269444
```

이 결과는 HS-JEPA의 active-silence 개념이 일부 맞다는 양성 센서다. 하지만 개선 폭은 작다. 따라서 논문/대회 관점에서의 해석은 다음이 더 정확하다.

```text
frontier active-silence는 row-state vector frontier 근처의 남은 local action을 찾았다.
0.53급 breakthrough는 이 방향의 미세 continuation이 아니라,
row-state frontier를 하나의 listener로만 취급하는 anchor-free state transport에서 찾아야 한다.
```

## 발표에서 쓰는 문장

```text
HS-JEPA는 public-equation jump에서 hidden public-state를 발견했고,
row-state vector frontier에서 그 hidden state가 특정 row-target vector로 표현됨을 보였다.
이후 negative sensors는 좋은 latent가 곧 좋은 action이 아님을 보여줬고,
frontier active-silence는 abstention 자체도 action-health의 일부임을 검증했다.
lifelog core state evidence는 HS-JEPA core가 direct label classifier가 아니라
row-action support를 복원하는 hidden human-state geometry임을 보여준다.
action-health separation은 그 geometry가 release 전에 toxic action field를 낮게 평가할 수 있음을 보여준다.
teacher-free core support는 public score와 action teacher 없이도 row-state frontier 일부를 회수해,
core가 단순 대회용 조정값이 아니라 downstream listener가 사용할 support geometry임을 보여준다.
target listener route selector는 HS-JEPA가 단일 latent classifier가 아니라,
target/listener별로 core geometry, raw lifelog proximity, safe prior, action-health release 중 무엇을 들을지 고르는 구조임을 보여준다.
contextual listener route selector는 sample-level router가 fixed target route는 이기지만 raw KNN은 못 넘어,
다음 과제가 full router가 아니라 raw-KNN failure detector임을 보여준다.
raw-KNN failure detector는 그 다음 질문에서 OOF 개선을 만들며,
HS-JEPA를 broad predictor가 아니라 failure-aware listener override로 정립한다.
```

## 앞으로 금지할 표현

- "H012가 좋았다"
- "H057을 anchor로 조금 움직인다"
- "H088은 실패했다"

## 앞으로 쓸 표현

- "public-equation jump가 plateau를 깨뜨렸다"
- "row-state vector frontier가 hidden state를 action field로 번역했다"
- "dual-head toxicity stress는 broad latent release가 public-toxic임을 보여줬다"
- "frontier active-silence는 release하지 않는 decision도 action-health임을 보여줬다"
