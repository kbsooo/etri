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
python3 sleep_competition_adapter/failure_boundary_law_distillation.py
python3 sleep_competition_adapter/row_reset_episode_detector.py
python3 sleep_competition_adapter/episode_selective_assignment_decoder.py
python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py
python3 sleep_competition_adapter/episode_controller_stress_audit.py
python3 sleep_competition_adapter/subject_invariant_episode_controller.py
python3 sleep_competition_adapter/cross_subject_episode_prototype_transport.py
```

`spectral_public_tangent_solver.py`는 H057 이후 public에서 실패한 제출들을 독립 실패로 보지 않고 하나의 negative representation space로 본다. 실패 액션들의 첫 spectral mode가 지배적이면, 다음 제출은 bad tangent의 반대 방향을 타야 하는지 또는 그와 직교한 private-safe residual subspace만 믿어야 하는지를 가르는 센서가 된다.

`negative_tangent_invariant_projection_solver.py`는 spectral solver의 다음 단계다. public-bad tangent를 단순히 뒤집지 않고, train target covariance와 subject prior로 정의한 invariant manifold를 보존하는 row-target action만 release한다. 이 후보가 public에서 살아나면 HS-JEPA의 action decoder는 `negative representation + invariant projection`이라는 더 일반적인 논문 contribution으로 정리할 수 있다.

이 실험은 route/fusion/target-listener/anti-shortcut을 서로 다른 listener로 보고, 한 listener를 가려도 살아남는 row-target action만 건강한 action 후보로 본다. 생성되는 `dropout_fullfield_aggressive`와 `toxic_direction_inversion` 후보는 같은 hidden action field를 믿을지, public-negative direction을 뒤집을지를 가르는 A/B 센서다.

`raw_knn_override_safety_jury.py`는 public LB, 기존 submission probability, action teacher, frontier file 없이 OG train future split만 사용한다. raw lifelog KNN을 기본값으로 두고, HS-JEPA context가 raw KNN failure cell만 sparse override할 수 있는지 본다. 현재 결과는 raw KNN OOF `0.636997`에서 sharp boundary `0.632478`로 개선되지만, consensus/vote guard는 `0.635705`까지 약해진다. 즉 adapter 관점에서는 HS-JEPA를 broad replacement가 아니라 sharp failure-boundary detector로 쓰는 것이 더 강하고, consensus는 release 조건보다 toxicity stress diagnostic으로 쓰는 편이 맞다.

`contrastive_failure_atlas.py`는 같은 질문을 더 architecture-first로 바꾼 ablation이다. 성공 action과 toxic action을 HS-JEPA state 공간의 positive/negative prototype atlas로 만들고, prototype energy만으로 raw-KNN override를 시도한다. OOF는 `0.635425`로 raw KNN보다 조금 좋지만 matched-null p-value가 `0.53` 수준이라 release-grade 증거는 아니다. 이 결과는 HS-JEPA core alone이 action solver가 아니라, 별도 row-target assignment/release decoder가 필요하다는 결론을 강화한다.

`failure_boundary_law_distillation.py`는 sharp failure boundary를 해석 가능한 law로 증류한다. depth-2 tree가 `expert_prob_mean`과 `abs_vs_core` 두 feature만으로 raw KNN OOF `0.636997`을 `0.632902`까지 낮췄고, GBDT detector `0.632478`과 거의 같은 수준이다. test에서는 20개 row의 7개 target 전체를 `global_prior`로 reset하는 high-information sensor candidate를 만든다. 이 결과는 HS-JEPA core가 direct predictor가 아니라 raw memory와 action route가 core geometry에서 벗어나는 정도를 재는 prior-reset/toxicity law로 쓰일 수 있음을 보여준다.

`row_reset_episode_detector.py`는 failure-boundary law의 선택이 cell 단위라기보다 row 전체 episode처럼 보인다는 관찰에서 출발한다. public score ledger, 기존 submission probability, action teacher, frontier file 없이 OG train OOF만 사용해 `raw lifelog memory를 계속 믿을 row인가, 안전한 prior/core route로 row 전체를 reset해야 하는 episode인가`를 학습한다. clean OOF에서 raw KNN `0.636997`을 `0.634030`으로 낮췄고, top 6개 row reset의 row-null p-value는 `0.005833`이다. 이 결과는 HS-JEPA adapter가 단순 sparse cell editor가 아니라 hidden episode reset detector로 확장될 수 있음을 보여주지만, 최종 release에는 target/listener assignment decoder가 추가로 필요하다는 한계도 남긴다.

`episode_selective_assignment_decoder.py`는 row episode detector와 target/listener assignment를 결합한 ablation이다. 기대는 row-level hidden episode state가 cell-level release decision의 독성을 줄이는 것이었지만, clean OOF에서 episode-conditioned assignment `0.632902`는 no-episode route law `0.632902`와 같았다. 최종 model은 `row_episode_*` feature를 쓰지 않았고, 생성 후보도 failure-boundary law와 동일한 prediction이다. 따라서 이 실험은 positive release가 아니라 negative architecture evidence다. row episode는 diagnostic으로 살아 있지만, 단순 feature injection이 아니라 episode-conditioned action-space restriction 또는 listener responsibility reweighting이 필요하다.

`episode_action_space_restriction_decoder.py`는 그 다음 구조를 검증한다. row episode state를 gain model feature로 넣지 않고, action 후보 공간을 제한하는 controller로 사용한다. clean OOF에서 unrestricted route law `0.632902`를 episode-family restricted policy `0.629771`까지 낮췄고, target+family null p-value는 `0.000625`다. 즉 HS-JEPA row-state encoder는 feature injection보다 action responsibility controller로 쓸 때 더 강하게 작동한다. 후보 파일은 `submission_hsjepa_episode_action_space_restriction_decoder_816c3a6e_uploadsafe.csv`다.

`episode_controller_stress_audit.py`는 위 positive result를 subject-LOO policy selection으로 검증한다. 결과는 full OOF best `0.629771`와 달리 subject-LOO selected-policy `0.639997`, raw 대비 `+0.003000`으로 무너졌다. 따라서 episode action-space restriction은 정보량 높은 제출 센서이지만, 아직 subject-general controller라고 주장하기에는 약하다. 다음 adapter 방향은 full OOF best policy가 아니라 subject-invariant controller objective다.

`subject_invariant_episode_controller.py`는 full OOF 최저 정책 대신 subject-invariant objective로 episode controller를 고른다. 결과는 subject-LOO `0.636997`, raw와 사실상 동률이며, 판정은 `subject_invariant_selector_is_safe_but_inactive`다. 이 실패는 중요하다. 안전 목적함수를 걸면 controller가 held-out subject에서 action을 거의 하지 않으므로, 이전 positive result가 특정 subject action tail에 묶여 있음을 보여준다.

`cross_subject_episode_prototype_transport.py`는 그 실패를 해결하기 위한 큰 구조 변경이다. 같은 subject 안에서 action을 고르지 않고, 다른 subject에서 성공한 episode-action prototype을 비슷한 row-target-route로 전이한다. public LB, 기존 submission probability, action teacher, frontier file 없이 subject-held-out kNN transport를 사용하며, raw KNN OOF `0.636997`을 best `0.629211`, robust release `0.630158`까지 낮췄다. robust release는 active subject 7명, negative active subject 1명으로, 2명 tail에 집중된 episode action-space restriction보다 더 일반화된 HS-JEPA 증거다. 후보 파일은 `submission_hsjepa_cross_subject_episode_prototype_transport_b034ce3b_uploadsafe.csv`다.

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
- `sleep_competition_adapter/outputs/failure_boundary_law_distillation/FAILURE_BOUNDARY_LAW_DISTILLATION_KO.md`
- `sleep_competition_adapter/outputs/row_reset_episode_detector/ROW_RESET_EPISODE_DETECTOR_KO.md`
- `sleep_competition_adapter/outputs/episode_selective_assignment_decoder/EPISODE_SELECTIVE_ASSIGNMENT_DECODER_KO.md`
- `sleep_competition_adapter/outputs/episode_action_space_restriction_decoder/EPISODE_ACTION_SPACE_RESTRICTION_DECODER_KO.md`
- `sleep_competition_adapter/outputs/episode_controller_stress_audit/EPISODE_CONTROLLER_STRESS_AUDIT_KO.md`
- `sleep_competition_adapter/outputs/subject_invariant_episode_controller/SUBJECT_INVARIANT_EPISODE_CONTROLLER_KO.md`
- `sleep_competition_adapter/outputs/cross_subject_episode_prototype_transport/CROSS_SUBJECT_EPISODE_PROTOTYPE_TRANSPORT_KO.md`

## 경계

이 adapter는 LB score를 움직이는 대회 적용체다. 논문에서 일반 기술로 주장할 부분은 `hsjepa_core/`에 있어야 하고, 이 adapter는 case study로 말해야 한다.
