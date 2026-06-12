# Anchor-Free State Transport

## 한 문장 요약

Anchor-Free State Transport는 current best를 기준점으로 조금 움직이는 방식이 아니라, 여러 listener world가 말하는 hidden row-target field를 합성해 fresh action tensor를 만드는 HS-JEPA decoder다.

## 왜 필요한가

frontier active-silence positive-path는 public LB `0.5677269444`로 새 best를 만들었다.

하지만 이 결과는 개선 폭이 작다. 즉 active silence는 유효하지만, current best 주변을 계속 미는 방식만으로는 0.53급 breakthrough나 논문 contribution을 만들기 어렵다.

따라서 질문을 바꾼다.

```text
current best 주변에서 어디를 더 움직일까?
```

가 아니라,

```text
여러 listener가 본 hidden human-state field를 합성하면,
current best 없이도 row-target action field를 재구성할 수 있는가?
```

## HS-JEPA 안에서의 위치

```text
human context
  -> hidden human-state representation
  -> listener worlds
       - pre-HS feature frontier
       - public-equation jump
       - Q2 phase route
       - row-state vector frontier
       - frontier active-silence
       - negative/toxic listener branches
  -> anchor-free state transport
  -> action-health / invariant check
  -> submission tensor
```

여기서 current best는 base anchor가 아니다. 여러 listener 중 하나일 뿐이다.

## Positive listener worlds

| listener | 의미 |
| --- | --- |
| pre-HS feature frontier | HS-JEPA 이전 feature/model plateau |
| public-equation jump | public scalar feedback이 hidden public-state equation으로 바뀐 큰 점프 |
| Q2 phase route | Q2-support row가 hidden state marker라는 신호 |
| row-state vector frontier | Q2-support row가 전체 Q/S vector로 확장된 frontier |
| frontier active-silence | release/abstain trajectory가 실제 public에서 작게 이긴 신호 |

## Negative listener worlds

| listener | 의미 |
| --- | --- |
| dual-head toxicity stress | local Pareto action이 public-toxic할 수 있음 |
| cross-listener transport stress | listener-confirmed shadow release가 action-grade가 아님 |
| objective S1/S4 toxic route | objective route를 직접 밀면 public이 벌줄 수 있음 |
| mask-family JEPA S2 toxic route | direct JEPA latent를 label action으로 바로 번역하면 무너짐 |
| null-common residual toxic route | local residual branch가 public miss를 만들 수 있음 |

## 구현

```bash
python3 sleep_competition_adapter/anchor_free_state_transport_solver.py
```

생성 산출물:

```text
sleep_competition_adapter/outputs/anchor_free_state_transport_solver/anchor_free_state_transport_readout_ko.md
sleep_competition_adapter/outputs/anchor_free_state_transport_solver/anchor_free_state_transport_cells.csv
sleep_competition_adapter/outputs/anchor_free_state_transport_solver/anchor_free_state_transport_selected_cells.csv
```

## 생성된 big-bet 후보

| 후보 | 변경 규모 | 해석 |
| --- | ---: | --- |
| `full_field_public_private_reset` | 1725 cells / 250 rows | 완전한 fresh tensor reset. 맞으면 HS-JEPA가 anchor 없이 listener field를 재구성한 것. 틀리면 dense tensor 합성은 아직 action-valid하지 않음. |
| `nonlocal_transport_release` | 322 cells / 188 rows | positive consensus, negative repulsion, route validity, source support가 모두 맞는 cell만 release. 가장 논문적으로 해석 가능한 big bet. |
| `listener_shock_reset` | 765 cells / 245 rows | current frontier가 과하게 보수적이라는 가설에 대한 강한 shock test. |
| `cohort_ready_private_safe_reset` | 113 cells / 89 rows | cohort-relative human-state view를 붙이기 쉬운 private-safe reset. |

## 현재 추천 센서

제출 슬롯을 정보량 기준으로 하나만 쓴다면:

```text
submission_hsjepa_anchorfree_state_transport_nonlocal_transport_release_6b3b402c_uploadsafe.csv
```

이 후보가 좋은 이유:

- 322 cells를 바꾸므로 current best 주변 미세조정이 아니다.
- selected cells의 mean route energy delta가 `-0.00515`로 내려간다.
- negative listener distance rank가 `0.7739`로 높다.
- random null 대비 cell score z가 `33.37`, route energy z가 `-14.00`이다.

즉 이 후보는 “많이 바꿨지만 아무렇게나 바꾼 것”이 아니라, HS-JEPA listener/invariant 조건을 통과한 nonlocal release다.

## public LB 해석

좋아지면:

```text
HS-JEPA는 current best를 anchor로 삼지 않고도,
listener worlds를 transport해 row-target action field를 만들 수 있다.
```

나빠지면:

```text
public-equation, row-state, active-silence world는 개별적으로 real이지만,
fresh tensor 합성에는 아직 private/toxicity/invariant가 부족하다.
```

둘 다 논문적으로 의미가 있다. 핵심은 이 실험이 점수 미세조정이 아니라 HS-JEPA의 일반화 가능성을 직접 찌른다는 점이다.
