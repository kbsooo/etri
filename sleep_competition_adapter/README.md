# Sleep Competition Adapter

이 디렉토리는 범용 `hsjepa_core/`를 수면 기반 생활습관 로그 대회에 꽂는 adapter다.

Core는 `listener`, `invariant`, `action-health` 같은 일반 개념만 알고, adapter가 다음을 제공한다.

- Q1/Q2/Q3/S1/S2/S3/S4 listener schema
- sleep-stage/Q-S route invariant
- public LB sensor boundary
- row-target sparse submission format
- upload-safe submission packaging

## 생성

```bash
python3 sleep_competition_adapter/build_sleep_competition_adapter_report.py
```

큰 thesis 검증 실험:

```bash
python3 sleep_competition_adapter/spectral_public_tangent_solver.py
python3 sleep_competition_adapter/negative_tangent_invariant_projection_solver.py
python3 sleep_competition_adapter/counterfactual_listener_dropout_solver.py
python3 sleep_competition_adapter/raw_knn_override_safety_jury.py
python3 sleep_competition_adapter/contrastive_failure_atlas.py
```

`spectral_public_tangent_solver.py`는 H057 이후 public에서 실패한 제출들을 독립 실패로 보지 않고 하나의 negative representation space로 본다. 실패 액션들의 첫 spectral mode가 지배적이면, 다음 제출은 bad tangent의 반대 방향을 타야 하는지 또는 그와 직교한 private-safe residual subspace만 믿어야 하는지를 가르는 센서가 된다.

`negative_tangent_invariant_projection_solver.py`는 spectral solver의 다음 단계다. public-bad tangent를 단순히 뒤집지 않고, train target covariance와 subject prior로 정의한 invariant manifold를 보존하는 row-target action만 release한다. 이 후보가 public에서 살아나면 HS-JEPA의 action decoder는 `negative representation + invariant projection`이라는 더 일반적인 논문 contribution으로 정리할 수 있다.

이 실험은 route/fusion/target-listener/anti-shortcut을 서로 다른 listener로 보고, 한 listener를 가려도 살아남는 row-target action만 건강한 action 후보로 본다. 생성되는 `dropout_fullfield_aggressive`와 `toxic_direction_inversion` 후보는 같은 hidden action field를 믿을지, public-negative direction을 뒤집을지를 가르는 A/B 센서다.

`raw_knn_override_safety_jury.py`는 public LB, 기존 submission probability, action teacher, frontier file 없이 OG train future split만 사용한다. raw lifelog KNN을 기본값으로 두고, HS-JEPA context가 raw KNN failure cell만 sparse override할 수 있는지 본다. 현재 결과는 raw KNN OOF `0.636997`에서 sharp boundary `0.632478`로 개선되지만, consensus/vote guard는 `0.635705`까지 약해진다. 즉 adapter 관점에서는 HS-JEPA를 broad replacement가 아니라 sharp failure-boundary detector로 쓰는 것이 더 강하고, consensus는 release 조건보다 toxicity stress diagnostic으로 쓰는 편이 맞다.

`contrastive_failure_atlas.py`는 같은 질문을 더 architecture-first로 바꾼 ablation이다. 성공 action과 toxic action을 HS-JEPA state 공간의 positive/negative prototype atlas로 만들고, prototype energy만으로 raw-KNN override를 시도한다. OOF는 `0.635425`로 raw KNN보다 조금 좋지만 matched-null p-value가 `0.53` 수준이라 release-grade 증거는 아니다. 이 결과는 HS-JEPA core alone이 action solver가 아니라, 별도 row-target assignment/release decoder가 필요하다는 결론을 강화한다.

## 산출물

- `sleep_competition_adapter/outputs/sleep_competition_adapter_report.json`
- `sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md`
- `sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json`
- `sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md`
- `sleep_competition_adapter/outputs/spectral_public_tangent_solver/spectral_public_tangent_readout_ko.md`
- `sleep_competition_adapter/outputs/negative_tangent_invariant_projection_solver/negative_tangent_invariant_projection_readout.md`
- `sleep_competition_adapter/outputs/counterfactual_listener_dropout_solver/counterfactual_listener_dropout_readout_ko.md`
- `sleep_competition_adapter/outputs/raw_knn_override_safety_jury/RAW_KNN_OVERRIDE_SAFETY_JURY_KO.md`
- `sleep_competition_adapter/outputs/contrastive_failure_atlas/CONTRASTIVE_FAILURE_ATLAS_KO.md`

## 경계

이 adapter는 LB score를 움직이는 대회 적용체다. 논문에서 일반 기술로 주장할 부분은 `hsjepa_core/`에 있어야 하고, 이 adapter는 case study로 말해야 한다.
