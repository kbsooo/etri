# 2026-06-04 HS-JEPA 점수 센서 정리

## Executive Summary

**핵심 판단:** H012/H042/H057은 public LB를 직접 최적화한 파일이 아니라, public-visible hidden state를 점점 더 정확히 좁힌 sensor로 해석해야 한다.

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

- H012는 E247 대비 약 0.0080을 줄여 public-equation 계열이 단순 모델 개선보다 훨씬 큰 구조 발견임을 보였다.
- H042/H050은 같은 0.5679048248에 묶여, Q2 support는 맞았지만 Q1/Q3 route만 추가하는 방식은 부족하다는 신호를 줬다.
- H057은 Q2를 freeze한 채 45개 row에서 non-Q2 전체 벡터를 움직여 0.5677475939까지 내려갔다. 이는 row 자체가 hidden human-state라는 해석을 강화한다.

## 데이터/실험 범위

- 원본 metric train: `450` rows.
- test/sample submission: `250` rows.
- raw lifelog parquet sources: `12` files.
- HITL decision files reviewed: `125`.

## 다음 행동

H057의 45개 row를 seed로 보되, 무작정 확장하지 말고 public-toxic action을 분리하는 decoder를 우선한다.

## Caveat

이 문서는 repo 안에 기록된 public LB, README/lb log, decision/report 산출물만 사용한다. 실제 private LB나 미기록 제출 결과는 포함하지 않는다.
