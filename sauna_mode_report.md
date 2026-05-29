# Sauna Mode Report

## 내가 발견한 가장 이상한 점

현재 frontier `submission_e95_hardtail_541e3973.csv`의 public LB `0.5762913298`은 broad model improvement처럼 보이지 않는다. E72는 넓게 움직였고 public에서 죽었지만, E95는 훨씬 target-pruned하게 움직이고 아주 작게 살아남았다.

## 그 이상함을 설명하는 현재 최강 세계관

이 대회의 현재 병목은 모델 capacity가 아니라 hidden block/state 신호를 row-level probability로 번역할 때 생기는 target-axis hard-tail calibration 실패다.

압축 문장:

> 0.576대 plateau는 숨은 구조가 없어서가 아니라, broad latent/structure movement가 Q/Q3/S4와 hard-label tail을 함께 건드리면서 LogLoss를 잃기 때문에 생긴다.

## 그 세계관이 맞다면 관측되어야 할 것

- public-positive E95는 broad movement가 아니라 target-axis surgery여야 한다.
- public-negative E72는 Q/Q3/S4 contamination 또는 낮은 E95-direction alignment를 보여야 한다.
- E101은 full E89보다 더 작은 kill-test여야 한다. 즉 E95의 남은 Q2/S3/S3-heavy ambiguity만 건드려야 한다.
- E101이 tie/loss이면 E108/E104/E106뿐 아니라 full E89/non-active graft 자동 fallback도 닫혀야 한다.

## 그 세계관을 죽일 수 있는 가장 작은 실험

`analysis_outputs/e111_sauna_frontier_movement_atlas.py`

submission geometry만 사용해 mixmin/E72/E85/E86/E89/E90/E95/E101/E108의 active cells, target-axis share, E95-confident movement share, E95-direction cosine을 비교했다.

## 실험 결과

- E72 vs mixmin: public delta `+0.0001011367`, active cells `893`, L1 `2.203482`, Q-share `0.450788`, S-share `0.549212`, cosine with E95 direction `0.327033`.
- E95 vs mixmin: public delta `-0.0000153107`, active cells `550`, L1 `1.509562`, Q-share `0.019948`, S-share `0.980052`.
- E101 vs E95: active cells `50`, active rows `48`, Q2/S3 share `1.0`, S-target share `0.905306`.
- E89 vs E95: active cells `158`, L1 `0.107468`, Q2/S3 share `0.299376`.

## 생각이 어떻게 바뀌었는지

E95를 단순 hardtail fallback으로만 보던 해석을 더 좁혔다. 지금 더 정확한 해석은 target-axis surgery다. E95는 실패한 E72류 movement에서 Q/Q3/S4 broad contamination을 거의 제거하고 S1/S2/S3 중심으로 남긴다.

## 추가 관찰: 왜 S축인가

`analysis_outputs/e112_sauna_qs_temporal_axis_audit.py`로 train label/order만 봤다.

- S-target subject-LOO logloss gain: `0.068724`, Q-target `0.020146`.
- strongest subject-prior targets: `S3`, `S2`, `S1`, 전부 E95-active.
- Q-target temporal persistence lift: `0.135700`, S-target `0.087255`.
- 하지만 test rows가 양쪽 train row로 3일 내 bracket되는 비율은 `0.080000`뿐이다.
- pairwise corr는 within-S `0.260803`, within-Q `0.187934`, Q-S `0.030038`.

따라서 E95가 S-heavy인 이유는 S축이 subject/block state를 더 잘 담기 때문으로 보인다. Q축도 temporal signal은 강하지만, test에 직접 전파할 train adjacency가 부족해서 broad Q/Q3 movement는 위험하다.

## 추가 관찰: raw context는 Q temporal state를 구하지 못함

`analysis_outputs/e113_sauna_raw_context_visibility_audit.py`로 visible raw lifelog context가 sparse Q temporal labels를 대체할 수 있는지 봤다.

- raw daily feature count: `114`.
- train/test raw coverage: `1.000000` / `1.000000`.
- temporal holdout에서 raw+subject-prior는 subject prior보다 Q targets `+0.038804`, S targets `+0.058534` 나빠졌다.
- random split에서도 평균적으로 Q `+0.007833`, S `+0.016497` 나빠졌다.
- 유일한 temporal gain은 S3 `-0.004643`뿐이다.
- Q2의 random-only 개선과 temporal degradation은 shortcut/collapse 경고다.

이 결과는 raw context rescue를 약화한다. Q temporal signal은 존재하지만 현재 보이는 raw coverage/head로는 submission-safe calibration으로 번역되지 않는다. S3만 약하게 살아남는 점은 오히려 E95의 S-subject-state 세계관과 맞는다.

## 추가 관찰: raw context는 E101도 미리 지지하지 못함

`analysis_outputs/e114_e101_raw_context_support_audit.py`로 E101의 `50` active cells만 봤다.

- subject prior 기준 E101 beat probability: `0.336655`.
- raw+prior 기준 E101 beat probability: `0.238325`.
- validation-gated raw 기준: `0.230710`.
- S3는 flip benefit의 `0.935862`를 차지하지만, raw S3 support probability는 `0.589463`으로 subject prior `0.604450`보다 낮다.

즉 raw context는 broad Q temporal rescue도 아니고, E101 active-cell label world를 미리 확인해주는 센서도 아니다. E101이 이기면 raw context가 보지 못한 public/local S3 hard-label world가 있었다는 뜻이고, 지면 raw context도 이미 그 방향을 약하게 반대한 셈이다.

## 추가 관찰: 그래도 E101이 다음 센서인 이유

`analysis_outputs/e115_public_sensor_information_audit.py`로 E101/E89/E85/E90/E86를 public sensor로 비교했다.

- E95-conditioned broad-plausible worlds: `3452`.
- E101 actionable information score: `1.613953`.
- E101 outcome entropy: `1.728493`.
- E101 beat-E95 rate: `0.983488`.
- E101 win/tie/loss: `0.911645` / `0.088355` / `0.000000`.
- E89 actionable information score: `0.233881`, beat-E95 `0.195829`, loss `0.580243`.
- E85/E90/E86 actionable scores: `0.025735`, `0.011719`, `0.002573`.

이 결과는 E101을 "raw가 지지하는 파일"로 되살리지 않는다. 대신 더 정확하게 만든다. E101은 현재 남은 세계관을 가장 많이 가르는 public sensor다. E89는 diffuse-tail 질문으로는 살아 있지만 다음 slot에서 E101보다 정보량이 낮고, E85/E90/E86는 대부분 "얼마나 지는가"를 묻는 파일에 가깝다.

## 다음으로 가장 정보량이 큰 행동

`analysis_outputs/submission_e101_q2s3tail_177569bc.csv` 제출.

이 파일은 E95의 구조를 유지하면서 남은 Q2/S3/S3-heavy ambiguity만 찌른다. E114 이후에도 raw-context support는 없지만, E115 기준으로 가장 actionability가 높은 public kill-test다. 즉 “raw가 맞다고 해서 제출”이 아니라 “남은 세계관을 가장 날카롭게 가르기 때문에 제출”이다.

## 제출 후보

파일: `analysis_outputs/submission_e101_q2s3tail_177569bc.csv`

의도: E95의 target-axis hard-tail surgery가 Q2/S3/S3-heavy cells에서 너무 tight한지 검증한다.

기대 public 반응:

- E101 improves over E95: E95의 큰 세계관은 맞지만 Q2/S3 tail localization이 과했다. E108/E104 amplitude-up branch가 열린다.
- E101 ties or loses: E95의 현재 axis/tail surgery가 standing law다. E108/E104/E106와 full E89/non-active graft fallback은 닫고 public-world model을 다시 짠다.
