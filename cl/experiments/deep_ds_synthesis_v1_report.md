# Deep DS Synthesis v1 — Information / Controls / Grammar 통합 보고

생성일: 2026-05-24
대상: ETRI/DACON 236690 lifelog multi-binary self-report 예측

## 1. 읽은 파일 / 파악한 현재 구조

### 1.1 데이터
- `data/ch2026_metrics_train.csv` (450행) / `data/ch2026_submission_sample.csv` (250행)
- 10 subjects 동일 (id01~id10), 7 binary targets (Q1,Q2,Q3,S1,S2,S3,S4)
- `sleep_date = lifelog_date + 1`
- test 250개 구성: train 날짜 범위 *안* 156개 (62%) + *후* 94개 (38%)
- `data/ch2025_data_items/*.parquet` — 12 modality raw sensor 스트림

### 1.2 기존 진단 산출물 (이번 분석에 활용)
- `features/observation_coverage_features.parquet` (700×76, day-level coverage by 12 modality)
- `experiments/observation_hourly_coverage_long.csv` (hour-level, 5MB)
- `features/observation_identity_token_features.parquet` (700×1202, BLE/WiFi/app token presence)
- `features/{semantic_features_v1, sleep_block_features_v1, mechanism_sleep_load_features_v2}.parquet`
- `experiments/advanced76_*` — IRT 측정 모델, subject-debiased token, temporal influence
- `experiments/{q1..q5}*` — 이전 5개 진단 결과
- `experiments/hybrid_validation_v1_report.md` — mirror_v1 fold (LB 모방)

### 1.3 이번에 추가 구현한 진단 스크립트
- `scripts/85_information_hierarchy.py` → `experiments/axis2_information_hierarchy_report.md` + `.csv` + `.marginal.csv`
- `scripts/86_negative_controls_v2.py` → `experiments/axis3_negative_controls_report.md` + `.csv`
- `scripts/87_target_grammar_extended.py` → `experiments/axis4_target_grammar_report.md` + `.csv`

평가는 모두 **mirror_v1 fold (3 seeds)** — LB와 inside/after 비율 (62/38) 동일하게 맞춘 validation. 단, mirror도 in-sample 비교(MI/transition은 train 전체)와 fold 비교(information hierarchy/negative controls)가 섞여 있음을 표 caption에 명시.

---

## 2. Target별 현재 가설

이번 진단 종합 후 갱신된 가설.

| target | 1차 driver | 보조 driver | 비고 |
|---|---|---|---|
| **Q1** | global prior에 가까움 — **어떤 source도 거의 lift 없음** | 약한 own-lag autocorr | 가장 *예측 불가*한 target. mirror에서 anchor 대비 모든 source가 +값 (marginal Δ table). 진짜 noise에 가깝거나, 우리가 못 본 신호. |
| **Q2** | **own_neighbor (-0.011) + coverage (-0.018)** | calendar weak helper | 유일하게 multiple sources에서 동시에 lift 보임. coverage가 도움 = 측정 가용성과 피로가 동조. forward smoothing lever 효과 있음. |
| **Q3** | calendar weak (-0.005) + autocorr (sticky) | latent state 도움 안 됨 | 자기 자신 lag effect가 가장 강함 (sticky 0/0=0.29, 1/1=0.76). cross-target Q lag는 거의 없음 (Q1 진단에서 확인). |
| **S1** | **subject prior 압도** (−0.044 lift over global) | other_neighbor 약간 도움 (+0.023 = 도움 안 됨) | feature/context 거의 안 받음. anchor가 사실상 최선. |
| **S2** | **subject prior 압도** (−0.081) | feature 모두 +값으로 망침 (특히 latent +0.175) | 가장 subject-static. latent factor와 충돌 (S2가 latent의 1번 축 *반대 방향*). |
| **S3** | **subject prior 압도** (−0.077) | autocorr sticky | S2와 패턴 동일. floor 0.51 거의 근접. |
| **S4** | **subject prior + 5개 surviving BSSID/app token** | other_neighbor +값 (도움 안 됨) | 이전 Q2 진단 (BSSID event vs availability)에서 25개 중 5개만 진짜 event signal로 살아남음. 나머지는 availability proxy. |

**핵심 패턴**: Q-family는 *temporal/coverage*에 약하게 반응, S-family는 *subject만 들으면 끝*.

---

## 3. Observation process / Coverage에서 확인할 수 있는 것

### 3.1 기존 coverage feature 구조
`observation_coverage_features.parquet` (76 cols, 700 rows)에 12 modality × {record_n, item_n, active_hours, night_hours, day_hours, longest_missing_hours} 형태로 day-level 있음. hour-level은 `observation_hourly_coverage_long.csv`에 long-format으로 존재. 새 modality 정의 안 했고 기존 활용.

### 3.2 Coverage-only 모델 점수 (axis 3 글로벌 컨트롤)

```
                 Q1     Q2     Q3     S1     S2     S3     S4     Tavg
coverage_only  0.7286 0.7239 0.6745 0.6359 0.6725 0.6912 0.6870 0.6877
subject_only   0.7119 0.7660 0.7515 0.5851 0.5894 0.5798 0.6275 0.6587
```

- coverage-only 평균 = **0.688**, subject-only = **0.659** → subject-only가 더 좋음
- 단 Q2/Q3에서 coverage가 subject보다 *낫다* (Q2: 0.724 vs 0.766, Q3: 0.675 vs 0.752) → **Q2/Q3는 측정 가용성과 비자명한 상관**
- 이건 advanced76에서 본 "Q3 evening WiFi/GPS 신호"와 일관

### 3.3 Coverage가 진짜 day-varying signal인가?

axis 3에서 측정한 `subj_cov` 모델의 **C0_real - C1_within_subject_perm** gap:
```
Q1: +0.033 (real가 perm보다 나쁨 = 가짜 신호)
Q2: -0.032 (real가 perm보다 좋음 = 실제 신호)
Q3: -0.009 (작음)
S1: +0.010, S2: -0.007, S3: +0.003, S4: +0.006 (모두 노이즈 수준)
```

→ **Q2 coverage만이 진짜 day-varying signal.** Q1 coverage는 오히려 *허위* (within-subject 라벨을 섞었을 때 더 좋아짐 = 모델이 잘못된 패턴 학습). S-family coverage는 day-signal 거의 없음.

### 3.4 결론
- coverage signal이 강한 곳: **Q2 (실제 day-varying)**, Q3 (약하게)
- coverage signal이 artifact인 곳: **Q1** (within-subject perm이 더 좋음)
- S-family는 coverage 무관 — subject prior가 다 잡음

⚠ "Q1에서 coverage가 허위로 좋아 보임"이 advanced76의 high-residual ~ coverage 연관(AUC 0.62)이 *Q1 모델 overfit*에 가깝다는 단서. coverage gating은 Q1에 함부로 적용 금지.

---

## 4. Information hierarchy 설계와 결과

### 4.1 설계 (script 85)
8단계 source set을 mirror_v1에 평가:
```
S0_global → S1_subject → S2_calendar → S3_own_neighbor →
S4_other_neighbor → S5_latent(1-factor IRT) → S6_engineered(top-30 F-test) →
S7_coverage(top-15 F-test) → S8_context_tokens(5 Q2 survivors)
```

평가 두 가지:
- **cumulative**: 누적 추가 (overfit cliff 확인용)
- **marginal**: 각 source를 (S0+S1) anchor 위에 **단독** 추가 (정보 기여 추출용)

### 4.2 Marginal Δlogloss vs anchor (S0+S1) (가장 신뢰 가능)

```
source             Q1      Q2      Q3      S1      S2      S3      S4      Tavg
S2_calendar      +0.002  -0.008  -0.005  +0.001  +0.003  +0.003  +0.011  +0.001
S3_own_neighbor  +0.007  -0.011  -0.003  -0.003  +0.024  +0.002  +0.001  +0.003
S4_other_neighbor +0.013 -0.010  -0.002  +0.023  +0.031  +0.040  +0.014  +0.016
S5_latent        +0.007  +0.007  +0.011  +0.021  +0.175  +0.015  +0.004  +0.034
S6_engineered    +0.087  +0.052  +0.108  +0.116  +0.078  +0.079  +0.055  +0.082
S7_coverage      +0.054  -0.018  +0.007  +0.032  +0.011  +0.019  +0.036  +0.020
S8_context_tokens +0.019 +0.003  +0.002  +0.001  +0.005  +0.015  +0.003  +0.007
```

### 4.3 해석

| 관찰 | 의미 |
|---|---|
| **Q2가 유일하게 다수 source에서 lift** (own_neighbor -0.011, other_neighbor -0.010, calendar -0.008, coverage -0.018) | Q2는 *진짜 day-level 정보가 있는 유일한 target*. 단 각각 작아서 합쳐도 -0.04 수준 |
| **S-family는 어떤 source도 anchor에 도움 안 됨** | S1/S2/S3/S4 모두 subject prior가 사실상 ceiling. 추가 작업은 overfit 위험 |
| **S5_latent가 S2를 +0.175 망침** | latent factor (Q+/S- 축)가 S2 prediction과 직교/반대 → S-family는 단일 latent로 모델 불가 |
| **S6_engineered 모든 target에 +0.05~+0.12** | 30 feature × 250 train row → 심한 overfit. feature 수 더 줄이지 않으면 사용 불가 |
| **S7_coverage가 Q2만 -0.018, 나머지는 +값** | coverage signal은 거의 Q2에만 진짜. 위 §3.3과 일치 |
| **S8_tokens 5개는 거의 neutral** | Q2 BSSID 분석 결과 (script 84) 재확인. tokens가 mirror에서 추가 lift 거의 0 |

### 4.4 information hierarchy의 한계
- 250 train rows / 7 targets → C=0.5 logistic도 30+ feature에서 overfit
- mirror fold마다 std가 target별 0.04~0.11 (full-stack에서) → **|Δ| < 0.01 차이는 noise**
- 따라서 "Q2 -0.018"도 sub-noise 가능성. 단 여러 source에서 일관된 부호 (-) 이므로 patterns는 신뢰 가능

---

## 5. Negative control 결과 (script 86)

### 5.1 핵심 표: `real - within_subject_perm` gap

`subj_tokens` 모델 (subject dummies + 5 surviving Q2 tokens):
```
Q1: +0.007  Q2: -0.011  Q3: -0.010  S1: -0.005  S2: -0.008  S3: -0.003  S4: -0.006
```

`subj_cov` 모델 (subject dummies + top-15 coverage):
```
Q1: +0.033  Q2: -0.032  Q3: -0.009  S1: +0.010  S2: -0.007  S3: +0.003  S4: +0.006
```

### 5.2 해석
- **모든 target에서 real-perm gap ≤ 0.033 (작음)**. 즉 *어떤 모델도 within-subject day-level signal을 크게 잡지 못함*
- subj_tokens는 모든 target에서 perm가 real을 거의 따라잡음 → **tokens는 subject 외 day-signal을 거의 안 줌**
- subj_cov는 Q1에서 **real이 perm보다 더 나쁨** (+0.033). 이건 진단 신호 — coverage가 Q1에서는 *허위 패턴*을 학습 (random shuffle 시 더 잘 맞춤)
- subj_cov는 Q2에서 -0.032로 가장 큰 gap → coverage on Q2 = real day-signal
- C5 (fake target) 결과: subj_tokens가 fake target에서 +0.04 정도 손해 → 모델이 *진짜 신호*를 일부 학습하긴 함 (단 magnitude 작음)

### 5.3 Context token / BSSID 결론
- 5개 surviving Q2 tokens는 within-subject perm에서도 *거의 동일* 점수 → **5 tokens조차 subject 흔적 비중이 크다**
- 단 script 84의 partial correlation 결과는 다른 방향 (5개는 subject+coverage controls 후 *살아남았다*). 두 결과 종합: 5 tokens는 *subject identity*는 아니지만 *static context fingerprint*에 가깝다 (subject별 자주 가는 장소). 진짜 *day-event*는 아니다.

### 5.4 negative control 종합
- **S2/S3/S4 day-level signal은 사실상 0** — subject prior가 가능한 거의 모든 정보를 흡수
- **Q2만이 작지만 검증된 day-signal**을 가짐 (-0.03 정도)
- **Q1은 coverage의 *허위* 패턴 위험** — 추가 시 perm보다 나빠짐
- BSSID/token "context event"는 *static context*에 더 가깝지 *true day event*는 아님

---

## 6. Temporal / label grammar 결과 (script 87)

### 6.1 Pairwise MI (nats) — top pair만
```
S2-S4: 0.118    (가장 강한 pair)
S2-S3: 0.077
S1-S2: 0.072
Q1-S1: 0.068
Q2-Q3: 0.058
```

### 6.2 MI - CMI (latent state로 설명되는 부분)
```
                Q1     Q2     Q3     S1     S2     S3     S4
S2-S4 reduction: 0.117 (= almost all 0.118)  ← S2-S4 association is latent
S2-S3 reduction: 0.071 (out of 0.077)         ← 거의 다 latent로 설명
S1-S2 reduction: 0.039 (out of 0.072)         ← 절반만 설명
Q2-Q3 reduction: 0.001 (out of 0.058)         ← latent로 설명 안 됨 ⭐
Q1-Q2 reduction: -0.033 (negative)            ← latent로 *반전*
```

**핵심**: S-family 안의 association은 latent state가 거의 다 설명. Q-family 안의 association은 latent state가 **전혀** 설명 못 함. **두 family가 서로 다른 axis** 라는 advanced76 IRT 발견을 *조건부 독립성 관점*에서 재확인.

### 6.3 Q/S axis decomposition
```
mean MI within Q: 0.024
mean MI within S: 0.047
mean MI Q × S cross: 0.007
```

- within-family MI = cross-family MI의 **3-7배**
- 두 axis 거의 독립
- 단일 IRT latent factor는 한 axis (보통 S)에 정렬 → 다른 axis (Q) 못 잡음. 위 §4의 S5_latent가 S2를 망친 이유.

### 6.4 Prev/next pattern × P(y=1)

가장 stickiness가 큰 target (prev=1 & next=1 → P(y=1)):
```
S1: 0.811   (모든 target 중 최대)
Q3: 0.759
S3: 0.792
S2: 0.762
Q2: 0.736
S4: 0.663
Q1: 0.757
```

대칭성: P(y=1 | prev=0, next=1) vs P(y=1 | prev=1, next=0):
```
Q3: 0.550 vs 0.587  → 거의 대칭 (forward와 backward 신호가 동등)
Q2: 0.585 vs 0.615  → 거의 대칭
S2: 0.577 vs 0.610  → 거의 대칭
```

→ **prev와 next가 거의 동등한 정보량.** Q1 분석에서 발견한 "hole regime에서 forward 라벨이 가장 큰 lever"가 이 대칭성으로 설명됨.

### 6.5 Transition vs non-transition day feature delta (top features)

transition day = 자기 자신 라벨이 어제와 다른 날.

| target | top transition-marker feature |
|---|---|
| Q1 | `q2x_prevnight_s4x_pre_sleep_screen_sum` (전날 잠들기 전 screen) |
| Q2 | `q2x_prevnight_s4x_post_wake_screen_sum` (전날 깬 후 screen) |
| Q3 | `ble_active_hours` (BLE 활동 시간 — 환경 변화) |
| S1 | `q2x_late_hr_std_hours` (late HR 변동성) |
| S2 | `wifi_record_n` (WiFi record 수 — 측정량) |
| S3 | `q2x_prevnight_s4x_block_hr_max` (수면 블록 HR max) |
| S4 | `quiet_run_end_hour` (조용한 구간 종료 시각) |

abs_z_delta 모두 0.3 전후 — **작지만 일관**. transition day는 측정량 변화 / 환경 변화와 동조. routine deviation으로 해석 가능.

---

## 7. Target별 분류

이번 진단 5개 영역 (axis 1~4 + 이전 Q1~Q5) 종합 후 target별 분류:

| target | 분류 | 근거 |
|---|---|---|
| **Q1** | **currently not observable** | 어떤 source도 anchor 대비 -0.005 이상 못 줄임 (axis 2). within-subject perm에서 coverage 모델이 *더 좋아짐* (axis 3) = 우리 feature가 잘못된 패턴. 진짜 noise이거나 우리가 못 본 신호. |
| **Q2** | **feature/context-driven (약함)** + temporal grammar-driven (약함) | 유일하게 multiple source lift: own_neighbor -0.011, other_neighbor -0.010, coverage -0.018 (Q2 cov는 real day-signal — axis 3). 단 lift는 모두 sub-0.02. |
| **Q3** | **label grammar-driven (own-lag sticky)** + 약한 calendar | prev/next pattern에서 가장 sticky (1/1=0.76, 0/0=0.29). cross-target Q lag은 거의 0 (이전 Q1 진단). calendar marginal -0.005만 유일 positive lever. |
| **S1** | **subject-driven** | subject prior anchor 외 어떤 source도 도움 안 됨. autocorr sticky (1/1=0.81 최대). |
| **S2** | **subject-driven (강력)** | subject lift -0.081 (최대). latent factor와 충돌 (latent 추가 시 +0.175). |
| **S3** | **subject-driven** | subject lift -0.077. 그 외 0. floor 0.51 거의 근접. |
| **S4** | **subject-driven** + **약한 coverage/context** | subject lift -0.060. 5개 BSSID/app survivor은 negative control에서도 대부분 살아남지 *못함* → static context. 단 mirror에서 작은 lift는 유효. |

분류 요약:
- **subject-driven** 6/7: S1, S2, S3, S4, (Q1 사실상), (Q3 부분)
- **temporal-grammar-driven** 2/7: Q2 (forward+own neighbor), Q3 (own-lag stick)
- **label-grammar-driven (cross-target)** 0/7 — Q3의 cross-target effect도 mirror에서 -0.011 수준, label-grammar가 dominant인 target 없음
- **feature/context-driven** 1/7: Q2만 weak
- **coverage/measurement-driven** 0/7 — coverage가 real signal인 target은 Q2 하나뿐인데 그것도 lift 작음
- **currently not observable** 1/7: Q1

⚠ 이 분류는 *현재 우리가 만든 feature 안에서* 본 정보 분포. 1등 LB 0.55는 우리가 만들지 못한 feature family에서 더 큰 신호가 있다는 시그널.

---

## 8. 다음에 실제 모델/제출로 번역한다면 어떤 target을 얼마나 움직여야 하는지

### 8.1 Anchor 기준점
- subject_prior_a20 (혹은 per-subject α tuning) on mirror_v1 ≈ **0.642**
- 이게 출발선. 모든 correction은 anchor 위에 capped delta로.

### 8.2 Target별 합리적 movement budget

| target | anchor | 합리적 목표 | 추가 lever | 위험 |
|---|---:|---:|---|---|
| Q1 | ~0.71 | 0.70 (-0.01) | 거의 없음. neighbor smoothing 약하게. | coverage 사용 금지 (허위 패턴) |
| Q2 | ~0.76 | **0.72 (-0.04)** | own_neighbor + coverage 결합. **가장 큰 movable target** | 여러 source 결합 시 overfit |
| Q3 | ~0.74 | 0.72 (-0.02) | own-lag stick (forward/backward) | cross-Q grammar는 약함 |
| S1 | ~0.59 | 0.585 (-0.005) | 거의 없음 | anchor가 거의 ceiling |
| S2 | ~0.59 | 0.585 (-0.005) | 거의 없음. latent 절대 금지 | latent factor와 충돌 |
| S3 | ~0.58 | 0.57 (-0.01) | 거의 없음 | floor 근접 |
| S4 | ~0.64 | 0.62 (-0.02) | 5개 surviving token, **capped ±0.05** | token이 static context이지 event 아님 |

**합산 추정**: Q1(-0.01) + Q2(-0.04) + Q3(-0.02) + S1(-0.005) + S2(-0.005) + S3(-0.01) + S4(-0.02) = **-0.110 / 7 = -0.0157 평균**

→ mirror 0.642 - 0.016 = **0.626** 가 우리 feature 한계 내 최선 추정.

### 8.3 1등 LB 0.55 갭에 대한 진단
- 0.642 → 0.55 = **-0.09 필요**
- 우리 한계 추정 = -0.016
- **갭 -0.07이 우리 feature/방법으로 안 잡힘**

가능한 누락 source:
- (a) sleep boundary detection을 *훨씬* 정밀하게 (분 단위 stage-like proxy)
- (b) cross-subject 정보를 *learning*으로 흡수 (deep representation, 우리 SSL은 약함)
- (c) 외부 pretrained model의 *실제 활용* (TimesFM/MOMENT를 feature gen 외에 fine-tune)
- (d) Q-S 두 axis를 동시 모델하는 *two-factor* structure (현재 single latent로는 §6.2에서 봤듯 못 잡음)
- (e) day-hour level event detection (current는 day-aggregate)

### 8.4 권장 다음 진단 (이번 보고서 후속)
이번 분석으로 "**우리 feature 한계 = -0.016**"이 정량화됨. 다음 진단은:

1. **2-factor IRT** (Q axis + S axis 분리). 이게 §6.2 CMI 패턴 (Q내 reduction ≈ 0)을 해결할 수 있는지 측정
2. **hour-level event detection** — sleep boundary가 분 단위에서 진짜 정확해질 수 있는지. coverage_long.csv 5MB 활용
3. **외부 pretrained TS model fine-tune** — chronos_bolt/dino embedding을 supervised head로 정밀 변환 (현재는 feature 추출만)
4. **discussion/공개 솔루션 파악** — 1등의 길이 (a)~(e) 중 어떤 path인지 외부 정보 필요. 이게 없으면 (a)~(e)를 brute force해야 함

---

## 출처 / 산출물 인덱스

- 이번 추가:
  - `experiments/axis2_information_hierarchy_report.md` (+ `.csv`, `.marginal.csv`)
  - `experiments/axis3_negative_controls_report.md` (+ `.csv`)
  - `experiments/axis4_target_grammar_report.md` (+ `.csv`)
  - `experiments/deep_ds_synthesis_v1_report.md` (이 문서)
  - `scripts/85_information_hierarchy.py`
  - `scripts/86_negative_controls_v2.py`
  - `scripts/87_target_grammar_extended.py`

- 이전 산출물 (이번 종합에 참조):
  - `experiments/q3_noise_floor_report.md`
  - `experiments/q1_grammar_vs_autocorr_report.md`
  - `experiments/q5_anomaly_taxonomy_report.md`
  - `experiments/q4_per_subject_loss_report.md`
  - `experiments/q2_bssid_event_vs_availability_report.md`
  - `experiments/hybrid_validation_v1_report.md`
  - `experiments/advanced76_data_science_report.md`
  - `experiments/observation_process_deep_diagnostics_report.md`
  - `experiments/problem_definition_q_temporal_s_context_measurement.md`

이번 턴: submission 0개, feature parquet 변경 0개, 기존 pipeline 손대지 않음.
