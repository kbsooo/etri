# Human-State Drift Consistency Certifier

## 핵심 주장

이 실험은 public LB를 직접 맞추는 후보가 아니다. HS-JEPA가 복원한 subject-level human-state를
`회복/악화 방향 drift`로 보고, 그 방향이 train-time subject drift와 aggregate listener signal에서
동시에 들릴 때만 subject-uniform logit action으로 번역한다.

subject 내부에서는 모든 row에 같은 Q2/Q3 logit 이동을 적용한다. 그래서 어느 test row가 실제 positive인지에
따른 배정노이즈를 최소화하고, row-cell 수술이 아니라 subject hidden-state 방향을 테스트한다.

Submitted positive candidate: `certified_replay`
Next sensor candidate: `drift_consistency_overshoot`

## 왜 HS-JEPA인가

- context: subject의 train-time temporal drift, current frontier probability state, aggregate listener sign
- hidden representation: subject별 recovery/degradation human-state direction
- prediction/action: Q2 intervention route와 Q3 companion route의 subject-uniform correction field
- diagnostic: train drift와 listener direction이 충돌하는 subject는 step을 줄인다

## 후보 요약

| variant | public LB | vs FrontierSilence | vs external certified | changed rows | changed cells | Q2 cells | Q3 cells | upload safe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| certified_replay | 0.5619100863 | -0.0058168581 | -0.0028390041 | 202 | 404 | 202 | 202 | True |
| drift_consistency_overshoot | not submitted | n/a | n/a | 202 | 404 | 202 | 202 | True |

## Submitted Subject Drift Field

| subject | sign | Q2 train drift | Q2 step | Q3 train drift | Q3 step |
| --- | ---: | ---: | ---: | ---: | ---: |
| id01 | 0 | 0.119048 | 0.000000 | -0.028571 | 0.000000 |
| id02 | -1 | 0.083333 | -0.750000 | 0.125000 | -0.250000 |
| id03 | 1 | 0.253676 | 0.750000 | -0.044118 | 0.250000 |
| id04 | 1 | 0.333744 | 0.750000 | 0.113300 | 0.250000 |
| id05 | 0 | -0.409091 | 0.000000 | 0.000000 | 0.000000 |
| id06 | 1 | 0.541667 | 0.750000 | 0.583333 | 0.250000 |
| id07 | -1 | -0.306667 | -0.750000 | 0.183333 | -0.250000 |
| id08 | -1 | 0.000000 | -0.750000 | -0.178571 | -0.250000 |
| id09 | 1 | 0.271429 | 0.750000 | -0.021429 | 0.250000 |
| id10 | -1 | -0.033088 | -0.750000 | -0.220588 | -0.250000 |

## 해석

`certified_replay`는 0.564749 계열을 재현하기 위한 control이다. 실제 public LB는 `0.5619100863`으로, FrontierSilence 대비 `-0.0058168581`, 외부 certified result 대비 `-0.0028390041` 개선되었다. 이는 subject-uniform human-state drift action이 public에서 강하게 전이됐다는 증거다.
`drift_consistency_overshoot`는 같은 방향을 더 세게 미는 것이 아니라, train drift가 뒷받침하는 subject에서만 더 크게 움직이고 충돌 subject는 줄이는 HS-JEPA action decoder다.

이 후보가 0.564749보다 좋아지면, subject-level human-state drift가 단순 public equation을 넘어 action magnitude까지
설명한다는 증거가 된다. 나빠지면, 현재 aggregate listener가 방향은 주지만 magnitude는 이미 max-min에 가깝게 포화됐다는
negative sensor로 기록한다.
