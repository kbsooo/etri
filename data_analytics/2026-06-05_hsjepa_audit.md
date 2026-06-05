# 2026-06-05 HS-JEPA 병목 재정의

## Executive Summary

**핵심 판단:** H088과 H144/H145는 숨은 상태를 찾는 문제보다, 그 상태를 안전한 row-target action으로 번역하는 문제가 병목임을 보여준다.

**현재 public best:** `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` = `0.5677475939`

## 점수 근거

| score_rank | observed_stage | file | public_lb_display | delta_display | family |
| --- | --- | --- | --- | --- | --- |
| 1 | H057 | submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | 0.5677475939 | -0.0001572309 | HS-JEPA row-state decoder |
| 2 | H050 | submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.5679048248 | +0.0000000000 | HS-JEPA target route stress |
| 2 | H042 | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.5679048248 | -0.0002186583 | HS-JEPA public equation |
| 4 | H145 | submission_h145_q3repair_2d818e46_uploadsafe.csv | 0.5679296410 | +0.0001820471 | HS-JEPA target assignment stress |
| 4 | H144 | submission_h144_targetxor_def80b88_uploadsafe.csv | 0.5679296410 | +0.0001820471 | HS-JEPA target assignment stress |
| 6 | H012 | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.5681234831 | -0.0080354663 | HS-JEPA public equation |
| 7 | H088 | submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.5684942019 | +0.0007466080 | HS-JEPA action toxicity stress |
| 8 | E247 | submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.5761589494 | -0.0001323804 | Feature NN smoothing |

## 분석 결과

- H088은 로컬 dual-head Pareto gate가 좋아 보여도 public LB가 0.5684942019로 후퇴했다. hard-world head는 action head가 아니라 toxic/collapse stress로 써야 한다.
- H144/H145가 둘 다 0.567929641에 묶인 것은 target-level micro-branch보다 공통 action body가 문제였다는 뜻이다.
- V131C식 cohort-relative anomaly는 좋은 context view지만, 바로 Q2/Q3/S2를 보정하는 decoder가 아니라 HS-JEPA의 action-health 입력으로 들어가야 한다.

## 데이터/실험 범위

- 원본 metric train: `450` rows.
- test/sample submission: `250` rows.
- raw lifelog parquet sources: `12` files.
- HITL decision files reviewed: `125`.

## 다음 행동

Cohort-relative outlier, human-social route, source responsibility를 모두 action-health/assignment solver 입력으로 통합한다.

## Caveat

이 문서는 repo 안에 기록된 public LB, README/lb log, decision/report 산출물만 사용한다. 실제 private LB나 미기록 제출 결과는 포함하지 않는다.
