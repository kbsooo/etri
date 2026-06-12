# 2026-06-11 Cross-Listener Transport 결과 해석

## Executive Summary

**핵심 판단:** Cross-listener transport는 listener posterior를 직접 action generator가 아니라 boundary prior로 쓰는 실험이었지만, public LB 0.5684860446으로 row-state frontier를 넘지 못했다.

**현재 public best:** `submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv` = `0.5677269444`

## 점수 근거

| score_rank | semantic_stage | file | public_lb_display | delta_display | family |
| --- | --- | --- | --- | --- | --- |
| 1 | frontier active-silence | submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv | 0.5677269444 | -0.0003965387 | HS-JEPA frontier active-silence |
| 2 | row-state vector frontier | submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | 0.5677475939 | +0.0000206495 | HS-JEPA row-state decoder |
| 3 | subjective route expansion | submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.5679048248 | +0.0001778804 | HS-JEPA target route stress |
| 3 | Q2 phase route | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.5679048248 | +0.0001778804 | HS-JEPA public equation |
| 5 | target-split XOR stress | submission_h144_targetxor_def80b88_uploadsafe.csv | 0.5679296410 | +0.0002026966 | HS-JEPA target assignment stress |
| 5 | Q3 repair-only stress | submission_h145_q3repair_2d818e46_uploadsafe.csv | 0.5679296410 | +0.0002026966 | HS-JEPA target assignment stress |
| 7 | public-equation jump | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.5681234831 | -0.0080354663 | HS-JEPA public equation |
| 8 | cross-listener transport | submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv | 0.5684860446 | +0.0007591002 | HS-JEPA cross-listener transport |

## 분석 결과

- 점수는 H088 0.5684942019와 거의 같은 손실대다. 즉 listener-calibrated shadow release는 broad Pareto/hard-world gate와 비슷한 public-toxic action 폭을 가진다.
- Direct listener-lift 0.5680255019보다는 나빠졌기 때문에, target-listener posterior를 안전한 release gate로 바꾸는 현재 transport 식은 충분하지 않다.
- 다만 0.570+로 붕괴하지 않았으므로 listener가 완전히 무의미한 것은 아니다. listener는 action 생성기나 최종 gate가 아니라, strict jury/core-health 후보의 diagnostic feature로 남기는 게 맞다.

## 데이터/실험 범위

- 원본 metric train: `450` rows.
- test/sample submission: `250` rows.
- raw lifelog parquet sources: `12` files.
- HITL decision files reviewed: `125`.

## 다음 행동

다음 big bet은 listener 추가가 아니라, row-state-positive action과 listener/toxicity가 충돌하는 cell을 명시적으로 금지하는 anti-listener toxicity field를 만든다.

## Caveat

이 문서는 repo 안에 기록된 public LB, README/lb log, decision/report 산출물만 사용한다. 실제 private LB나 미기록 제출 결과는 포함하지 않는다.
