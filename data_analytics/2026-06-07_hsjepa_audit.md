# 2026-06-07 현재 상태와 재현성 점검

## Executive Summary

**핵심 판단:** 오늘 기준으로 가장 강한 산출물은 최고점 제출을 재현하는 end-to-end HS-JEPA 코드와, 이후 실험들이 왜 row-state vector frontier를 크게 넘지 못했는지 설명하는 negative sensor ledger다.

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

- hs_jepa_end_to_end.py는 row-state vector frontier hash 7cde1a77을 재현하고, 45 hidden row와 270 row-target action을 cell-level로 설명한다.
- Gemini embedding 실험은 narrative latent 가능성을 보였지만, 오픈소스 재현성 때문에 논문/팀 공유용 핵심 경로에서는 제외해야 한다.
- 다음 breakthrough는 더 큰 blend가 아니라 safe assignment field다. row-state seed를 유지하면서 cohort outlier나 social latent가 어느 target action에 안전한지 판별해야 한다.

## 데이터/실험 범위

- 원본 metric train: `450` rows.
- test/sample submission: `250` rows.
- raw lifelog parquet sources: `12` files.
- HITL decision files reviewed: `125`.

## 다음 행동

오픈소스 semantic/cohort encoder를 HS-JEPA context view로 만들고, public-toxic 방향과 H057-positive 방향을 동시에 보는 row-target solver를 설계한다.

## Caveat

이 문서는 repo 안에 기록된 public LB, README/lb log, decision/report 산출물만 사용한다. 실제 private LB나 미기록 제출 결과는 포함하지 않는다.
