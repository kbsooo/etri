# ETRI Lifelog 2026 — 데이터 가공 보고서

> DACON 236690 (제5회 ETRI 휴먼이해 AI 논문경진대회)
> 라이프로그 **6.12M 행**에서 의미를 추출하는 데이터 가공 작업 정리
> 작성: 2026-05-18

---

## 0. TL;DR — 한 페이지 요약

### 데이터 비대칭

| | 행 수 | 비고 |
|---|---|---|
| 라벨 (train) | 450 행 | 10 subject × 평균 45일 |
| 제출 (test) | 250 행 | 같은 10 subject, 후기 날짜 |
| **라이프로그 raw** | **6,122,179 행** | 12 모달리티, ~8,746 event/day/subject |
| 라이프로그 ÷ 라벨 | **약 13,605 배** | 정보의 99.99%를 daily aggregation으로 버려 옴 |

### 결정적 발견 6가지

1. **라벨 없는 날짜는 0개** — 라이프로그가 정확히 train 450 + test 250 = **700 subject-day**에만 존재. "추가 unlabeled 날짜로 SSL"은 불가능. 진짜 활용해야 할 자원은 **하루 안의 ~8,746 event** (시간 슬롯 차원) + **test 250일의 lifelog** (pseudo-labeling).

2. **S1~S4의 ground truth 센서가 데이터에 없다** — PDF는 S1~S4가 *Withings Sleep Analyzer* (매트리스 아래 BCG 센서) 측정값이라고 명시. 우리가 가진 건 phone+wrist 12종뿐. 어떤 모델이든 sleep reconstruction은 *proxy*이고 ceiling이 존재.

3. **Q1~Q3는 "개인 평균 대비" 라벨** — 각 subject별 mean이 ≈ 0.5로 강제됨 (정의에 의해). subject ID 자체나 subject-constant feature는 Q에 대해 zero information. **반드시 within-subject deviation feature**가 필요.

4. **wHr는 밤에 절반 죽는다** — 22-06h 가용률 wHr 46.8% vs mActivity/mScreen 98.9%. 워치 안 차고 자는 사람이 많음. 수면 신호의 backbone은 mActivity+mScreen, wHr는 보조.

5. **두 기존 워크스페이스(claude/, codex/)가 stuck인 이유 진단됨** — codex 최고 public LB 0.6062 ≈ per-subject mean baseline 0.5940. 둘 다 daily aggregation으로 collapse해서 진짜 정보(시간 슬롯 deviation, place identity, outing count, prebed app mix, phone-watch coherence)를 못 짜냄.

6. **익명화 좌표에서 home/work 자동 발견 가능** — GPS 좌표가 익명화돼도 *클러스터 자체는 유효*. 10명 중 7명에서 명확한 home + work_or_school 패턴이 자동으로 추출됨.

### 핵심 산출물

| 산출물 | 의미 |
|---|---|
| `artifacts/10_master_daily.parquet` | 700 row × 232 col, 모든 derived data 통합 |
| `artifacts/06_*.parquet` (5개) | 위치/장소/wireless fingerprint |
| `artifacts/07_*.parquet` (5개) | 매일 sleep onset/wake + HRV 시계열 |
| `artifacts/08_*.parquet` (6개) | 13 bucket soundscape + 광 노출 |
| `artifacts/09_*.parquet` (5개) | 19 app category + 5 mobility mode + phone-watch coherence |
| `artifacts/03_hourly_grid.parquet` | 16,580 hourly cell × 30 feature (subject × date × hour) |
| `artifacts/04_features_deviation_daily.parquet` | 63 deviation feature (per-subject hourly z-score) |

---

## 1. 대회 개요

- **이름**: 제5회 ETRI 휴먼이해 인공지능 논문경진대회
- **목표**: 라이프로그 데이터로 (subject, sleep_date) 별 7개 이진 라벨 예측
- **평가 metric**: 평균 binary log loss (7 target 평균, 낮을수록 좋음)
- **기간**: 2026-04-20 ~ 2026-06-26 (리더보드 + ICTC 논문 동시 마감)
- **상금**: 530만원 + Private 상위 60팀 Claude API 크레딧
- **필수 절차**: ① 리더보드 ② ICTC 2026 논문 ③ 채택 시 코드/설명서

### 7개 라벨 정의 (PDF Table 1 정리)

| 라벨 | 의미 | 1의 정의 |
|---|---|---|
| **Q1** | 취침 후 수면질 | 개인 평균보다 좋음 |
| **Q2** | 취침 전 피로 | 개인 평균보다 적음 |
| **Q3** | 취침 전 스트레스 | 개인 평균보다 적음 |
| **S1** | 총 수면시간 (TST) | NSF 권고 충족 |
| **S2** | 수면 효율 (SE) | NSF 권고 충족 |
| **S3** | 입면 잠복기 (SOL) | NSF 권고 충족 |
| **S4** | 입면 후 각성 (WASO) | NSF 권고 충족 |

⚠️ **S1~S4는 Withings Sleep Analyzer 매트리스 BCG 측정값** (PDF 참조 [2]). 데이터셋에는 그 센서가 포함되어 있지 않음.

---

## 2. 데이터 구조

### 모달리티 12종 (`data/ch2025_data_items/`)

| 모달리티 | 행 수 | 측정 단위 | 가치 |
|---|---|---|---|
| **mActivity** | 961,062 | 1분 | Google Awareness 코드 (still=3 dominant 82%) |
| **mACStatus** | 939,896 | 1분 | 충전 여부 |
| **mScreenStatus** | 939,653 | 1분 | 화면 ON/OFF |
| **mGps** | 800,611 | 1분 (각 행 list, 평균 10점) | 익명화 위경도 + 속도 |
| **wPedo** | 748,100 | 1분 | step, calorie, speed |
| **wLight** | 633,741 | 1분 | 손목 광량 |
| **mAmbience** | 476,577 | ~2분 (각 행 top-10 class list) | 환경 사운드 |
| **wHr** | 382,918 | 1분 (각 행 ~60 BPM list) | 분당 60개 instantaneous BPM |
| **mLight** | 96,258 | 비정기 | 휴대폰 광량 |
| **mWifi** | 76,336 | 10분 (각 행 list) | WiFi BSSID/RSSI |
| **mUsageStats** | 45,197 | 10분 (각 행 list) | 앱별 사용 시간 |
| **mBle** | 21,830 | 10분 (각 행 list) | BLE 장치 주소/클래스 |

### 라벨

`data/ch2026_metrics_train.csv` (450 행), `data/ch2026_submission_sample.csv` (250 행)

| Subject | Train 일 | TST 평균 | Sleep eff |
|---|---|---|---|
| id04 | 57 | **580분** (9.7h) | 0.89 |
| id06 | 48 | 555 | 0.83 |
| id02 | 48 | 545 | 0.81 |
| id07 | 49 | 501 | 0.75 |
| id09 | 41 | 473 | 0.76 |
| id01 | 41 | 424 | 0.84 |
| id05 | 44 | 407 | 0.74 |
| id03 | 33 | 405 | 0.78 |
| id10 | 33 | 324 | 0.73 |
| **id08** | 56 | **312분** (5.2h) | **0.63** |

→ subject별 sleep 패턴 차이가 극단적 (5.2h ~ 9.7h, 거의 2배). subject prior가 압도적.

---

## 3. Phase 0 — 데이터 커버리지

**노트북**: `notebooks/01_data_coverage.py`
**산출물**: `01_coverage_heatmap.png`, `01_label_correlation.png`, `01_coverage_table.parquet`

### 핵심 발견

- 라이프로그 6.12M 행 = train 450일 + test 250일 = **700 subject-day**에 정확히 정렬
- 단 하루의 unlabeled day도 없음 → "라벨 없는 날짜로 SSL pretraining" 전략은 적용 불가
- 라벨일 중 88건은 12개 모달리티 중 일부가 죽음 (6~11개만 살아있음). subject prior로만 처리 가능.

### 라벨 상관 매트릭스 (Pearson)

```
      Q1    Q2    Q3    S1    S2    S3    S4
Q1  1.00  0.12  0.10  0.36  0.07 -0.12  0.02
Q2  0.12  1.00  0.34  0.05  0.00 -0.05 -0.02
Q3  0.10  0.34  1.00  0.07  0.00 -0.03  0.01
S1  0.36  0.05  0.07  1.00  0.38  0.12  0.11
S2  0.07  0.00  0.00  0.38  1.00  0.39  0.48
S3 -0.12 -0.05 -0.03  0.12  0.39  1.00  0.09
S4  0.02 -0.02  0.01  0.11  0.48  0.09  1.00
```

**구조 해독:**
- **S2 ↔ S4 = +0.48** (Sleep Efficiency ↔ WASO): 같은 측정에서 파생되니 자연스러움
- **S1 ↔ S2 = +0.38**: TST가 길수록 효율 ↑
- **Q1 ↔ S1 = +0.36**: 주관 수면질 ↔ 객관 TST — 의미 있는 신호
- **Q2 ↔ Q3 = +0.34**: 피로 ↔ 스트레스 — 자연스러운 정신상태 상관
- **Q ↔ S 사이는 대부분 ≈ 0** (예외: Q1↔S1) → **Q-family와 S-family는 거의 독립**

→ Multi-task 묶을 때 Q와 S를 분리해야 효율적. S 예측 → Q 예측의 feature로 cascade도 가능.

### 24시간 시간대별 신호 가용성

| 모달리티 | 22h~06h 가용률 |
|---|---|
| mActivity | **98.9%** |
| mScreenStatus | **98.9%** (off=수면 신호) |
| wPedo | 79.8% |
| **wHr** | **46.8%** |

→ Sleep window 추정은 mActivity+mScreen 주축. wHr만 의지하면 절반 실패.

---

## 4. Phase 0.5 — TST Proxy AUC 게이트

**노트북**: `notebooks/02_label_structure.py`
**산출물**: `02_tst_proxy_vs_S.png`, `02_proxy_persubj_auc.csv`, `02_logloss_baselines.csv`

### 단순 TST proxy 정의
- 18:00 (prev day) ~ 12:00 (curr day) 윈도우
- `STILL_CODES = {0, 3, 4}` AND `screen=0` 인 minute의 가장 긴 연속 구간

### Per-subject AUC (정직한 측정)

| target | tst_proxy | se_proxy | -gap_count |
|---|---|---|---|
| S1 | 0.616 | **0.646** | 0.638 |
| S2 | 0.579 | 0.600 | 0.577 |
| **S3** | 0.488 | 0.477 | 0.492 ← random |
| S4 | 0.593 | 0.608 | 0.569 |
| Q1 | 0.616 | 0.630 | 0.568 |
| **Q2** | 0.485 | 0.505 | 0.508 ← random |
| **Q3** | 0.508 | 0.507 | 0.523 ← random |

**결론**: 모든 AUC ≤ 0.65. Sleep window reconstruction은 메인 라인 불가능 (Withings 부재 ceiling 확정).

### Subject-mean baseline log loss (참고값)

```
uniform 0.5     : 0.6931
global mean     : 0.6641
per-subject mean: 0.5940  ← 모델 없이 단순 subject 평균만
codex public LB : 0.6062  ← 두 기존 워크스페이스는 여기에 머무름
public 0.54 목표 : -0.054 더 깎아야 함
```

⚠️ **두 기존 워크스페이스(claude/, codex/)는 단순 subject-mean baseline보다 약간 나쁜 수준에서 stuck.** 정보가 분명히 있는데(라이프로그 6.12M 행) 활용하지 못하고 있다는 정황.

---

## 5. Phase 1a — Intra-day Hourly Grid

**노트북**: `notebooks/03_intraday_signature.py`
**산출물**: `03_hourly_grid.parquet` (16,580 row × 30 col), `03_hod_signatures.png`, `03_still_variability.png`

### 무엇을 했나
- 12개 모달리티 raw 행을 (subject, date, hour-of-day) 셀로 압축
- 각 셀에 모달리티별 summary stats (still_ratio, screen_on_ratio, step_sum, hr_mean, gps_speed_mean, mlight_mean, charging_ratio 등)
- **이게 모든 후속 작업의 기반**

### 결과
- 700일 × 24 hod = 16,800 expected → 실제 16,580 (220개는 모든 신호 결측)
- 30 feature column, 모든 (subject, date) 키로 lookup 가능
- 시간대별 modality 신호의 풍부함이 정량화됨

---

## 6. Phase 1b — Routine Deviation Engine

**노트북**: `notebooks/04_routine_deviation.py`
**산출물**: `04_features_deviation_daily.parquet` (700 row × 63 col), `04_baseline_med_mad.parquet`, `04_auc_compare_*.csv`

### 핵심 가설
> Q 라벨은 "개인 평균 대비" 정의이므로, **per-subject hourly baseline에서의 deviation**이 직격타가 되어야 한다.

### 구현
1. 각 `(subject_id, hour-of-day)`의 **median + MAD** baseline 추정 (700일 전체 사용)
2. 각 hourly cell의 robust z-score = `(x - median) / (1.4826 * MAD + ε)`
3. Daily summary: 7개 시간 슬롯 (night/earlyAM/AM/noon/PM/evening/lateNight) × 8개 핵심 feature 의 signed z-score mean
4. 추가로 `z_abs_mean`, `z_abs_max`, per-slot `z_abs_*`

### Top-3 rank-sum AUC (per-subject 평균; raw daily vs deviation)

| target | raw daily | deviation | lift |
|---|---|---|---|
| Q1 | 0.630 | 0.646 | +0.016 |
| Q2 | 0.628 | 0.651 | +0.023 |
| **Q3** | 0.654 | **0.728** | **+0.074** |
| S1 | 0.659 | 0.659 | +0.001 |
| S2 | 0.677 | 0.657 | -0.020 |
| **S3** | 0.668 | **0.746** | **+0.077** |
| **S4** | 0.596 | **0.678** | **+0.082** |

평균 lift **+0.036**, 6/7 타깃에서 개선. **routine deviation이 raw daily aggregation보다 정보를 더 짜냄을 정량 확인.**

### 가장 강력한 단일 deviation feature

7개 타깃의 best dev feature 중 **6개가 night/lateNight (22-06h) 시간대**:

| target | best deviation feature | per-subj AUC |
|---|---|---|
| Q1 | z_lateNight_hr_mean | 0.608 |
| Q2 | z_earlyAM_step_sum | 0.592 |
| Q3 | z_night_hr_mean | 0.600 |
| S1 | z_night_step_sum | 0.598 |
| S2 | z_night_gps_speed_mean | 0.605 |
| **S3** | z_night_hr_mean | **0.633** (02에서 random 0.49 → 0.63) |
| **S4** | z_lateNight_hr_mean | **0.643** |

→ **진짜 sleep proxy는 단순 TST 지속이 아니라 "평소 수면시간대 HR/움직임이 평소와 다른가"**. wHr 밤 커버리지 47%인데도 작동하는 것은 deviation 신호이기 때문 (HR이 있는 밤만 사용).

⚠️ **주의** (advisor 지적): 위 AUC는 direction picking with labels을 포함하므로 절대값은 inflated. **lift는 fair**하지만 0.728은 "진짜 0.728"이 아님. log loss 검증에서는 이 lift가 강하게 transfer되지 않는다는 것이 Phase 1c에서 드러남 (모든 모델이 reference subject-mean baseline 0.629를 못 깎음). 이는 single deviation feature가 prior에 추가하는 정보가 약하다는 뜻이지, deviation이 무가치하다는 뜻이 아님.

---

## 7. Phase A — Places & Wireless Fingerprints

**노트북**: `notebooks/06_places_and_fingerprints.py`
**산출물 5개**: `06_places.parquet`, `06_daily_place_durations.parquet`, `06_wifi_core_fingerprint.parquet`, `06_ble_core_fingerprint.parquet`, `06_daily_novelty.parquet`

### GPS 장소 자동 발견

**전처리**: mGps list-of-dict explode → 8,546,932 long points → speed < 0.5 m/s 정지 점만 7.24M (84.7%) → 좌표 4자리 round → grid_id

**Subject별 정지 grid cell 수:**
```
id01 4,014 | id02 9,211 | id03 3,482 | id04 4,828 | id05 6,895
id06 4,520 | id07 2,523 | id08 1,259 | id09 3,196 | id10 2,666
```

**Place type 분류 (Hour-of-day 패턴 기반):**

| type | rule | count |
|---|---|---|
| home | share_night ≥ 0.5 | 168 |
| work_or_school | share_day ≥ 0.55 AND share_night < 0.3 | 782 |
| other | else | 542 |
| transient | n_minutes < 30 | 41,102 |

### Top-5 places per subject (자동 발견!)

| subject | 패턴 |
|---|---|
| **id01** | home 41,677분 (0.61 night) + 2 work grids (0.79/0.70 day) |
| **id02** | 4 home grid (좌표 정밀도가 한 집을 4개로 쪼갬, 0.64/0.54/0.72/0.80 night) |
| **id03** | home 2 grid + work 0.99 day dominance |
| **id04** | home 1 + work 2 (0.84/0.81 day) |
| **id05** | home 1 + work 2 (0.97/0.90 day) + other "다른 집" 추정 |
| **id06** | home 2 grid + work 1 (0.95 day) |
| **id07** | **home 2 + work 3 (모두 0.94+ day)** — 매우 안정한 출퇴근 직장인 |
| **id08** | home 2 + work 3 (0.97+ day) — 출장 잦음? 일별 work 다양 |
| **id09** | home 2 + work 1 (0.98 day) — id09는 "other"가 home보다 1순위 |
| **id10** | **home 0개, 모두 "other"** — 야간 분산형 outlier |

**핵심 발견**: 익명화 좌표인데도 **각 subject의 home/work 정체성이 자동으로 드러남**. 단순 daily aggregation으로는 절대 못 얻는 정보.

### Daily place durations (id01 sample)

```
date         home  work   other  elsewhere  moving
2024-06-26   148   183    114    243        264   ← 외출 많음
2024-06-29   1210   0     44     161        679   ← 집에서 보낸 날 (work=0)
2024-07-03   630   375    143    255        533
```

→ `gps_home_ratio`, `gps_elsewhere_ratio`, `outings` (stationary↔moving 전환 수) 등 derived feature가 자연스럽게 추출됨.

### WiFi fingerprint
- 1.27M WiFi long row → subject별 core BSSID (day-presence ≥ 30%)
- Core BSSID 1,199개 (subject별 51~187개)
- **매일 80%+ novel BSSID** — 일상 무선 환경이 매우 다양 (출퇴근 거리/카페/지하철 등)
- 살아남는 신호: `wifi_core_hit` (오늘 본 익숙한 BSSID 수) ← 익숙한 환경에 머물수록 ↑

### BLE
- 437K long row → core 105개 (subject별 5~25개)
- BLE novelty ratio 99%+ (대부분 1회성)
- 살아남는 신호: `ble_core_hit` (가족/동료처럼 항상 옆에 있는 사람의 phone)

---

## 8. Phase B — Sleep Schedule & HRV

**노트북**: `notebooks/07_sleep_schedule_and_hrv.py`
**산출물 5개**: `07_sleep_events.parquet`, `07_sleep_summary.parquet`, `07_hrv_hourly.parquet`, `07_hrv_daily.parquet`, `07_night_hrv.parquet`

### Sleep Episode Detection 알고리즘

```
입력: mActivity (still=3 only) + mScreenStatus (off=0)
윈도우: 전날 18:00 ~ 당일 14:00 (20시간)
규칙:
  1. sleep_cand = still AND screen_off
  2. 60분 이상 연속 sleep_cand 블록만 유효 sleep run
  3. 30분 미만 awakening gap은 sleep envelope에 합쳐짐
  4. Sleep envelope = 첫 valid sleep run ~ 마지막 valid sleep run
출력: onset, wake_time, TST, sleep_eff, n_awakenings (long), SOL_proxy
```

### 결과 (700 nights)

| 지표 | 평균 | std |
|---|---|---|
| TST | **460.56 분 (7.67h)** | 278 |
| sleep_eff | 0.78 | 0.30 |
| longest_block_min | (전체) | |
| n_awakenings | 0.74 (1h+ awakening 일평균) | 1.01 |
| sol_proxy_min | 59.15 | 134 |

→ Phase 02의 단순 proxy 275분 → 460분으로 크게 개선. 실제 수면 시간에 근접.

### HRV from wHr (1-minute granularity)

- 유효 row 375K (97.5% 데이터)
- 1분 단위 BPM list → IBI(ms) = 60000/BPM → RMSSD, SDNN, pNN50
- Daily 평균: HR 88, RMSSD 13.3, SDNN 30.5

### Night HRV (sleep envelope 내)
- 623 nights에 데이터 — 700 - 623 = 77개는 sleep envelope 없거나 wHr 미측정
- ⚠️ `night_hr_mean ≈ 88` (낮 평균과 거의 같음) — PPG 워치 측정 한계 또는 envelope이 "조용히 깨어있는 시간"을 포함하는 한계. 진짜 sleep 중 HR은 일반적으로 60대.

---

## 9. Phase C — Ambience & Light Context

**노트북**: `notebooks/08_ambience_and_light.py`
**산출물 6개**: `08_ambience_hourly_buckets.parquet`, `08_ambience_daily.parquet`, `08_ambience_subject_signature.parquet`, `08_light_daily.parquet`, `08_light_night.parquet`, `08_ambience_class_freq.parquet`

### Ambience 전처리
- 4,765,770 ambience tag (476K row × top-10 class)
- **517 unique classes**
- 13개 의미 bucket으로 매핑: speech / music / vehicle / outdoor / indoor / tv_radio / domestic / alarm_phone / white_noise / silence / footsteps / laughter_cry / other

### Top 클래스 (의외의 분포)

```
Inside, small room       419,651   ← 작은 방 안 시간이 가장 많음
Speech                   396,387
Silence                  354,232  (mean prob 0.93 — silence는 특정 시간엔 거의 완전)
Music                    352,983
Narration, monologue     335,203
Child speech             332,317
Conversation             331,389
Animal                    69,431  ← 의외 (모델 false positive 가능성)
Outside, rural           58,371
Vehicle                   48,099
```

### Per-subject soundscape signature (vehicle 비중만)

| subject | vehicle 비중 | 해석 |
|---|---|---|
| **id05** | **0.003** | 집순이 (이동 거의 없음) |
| id08 | 0.006 | 집순이 |
| id01 | 0.011 | 적당 |
| id06 | 0.023 | 보통 |
| id07 | 0.036 | 이동 많음 |
| id10 | 0.034 | 이동 많음 |
| **id09** | **0.044** | 가장 이동 많음 |

⚠️ **id05 모순 관찰**: GPS에서는 일관된 work_or_school grid(0.97 day)가 보이는데 ambience vehicle 비중은 0.003. → 도보 출퇴근 또는 매우 짧은 거리 출퇴근 가설.

### Light exposure
- wLight (wrist) 634K row vs mLight (phone) 96K row — **워치가 6배 많이 측정**
- 일별 dark hours (lux<10) / bright hours (lux>1000) 카운트 가능
- max lux 91,584 (어떤 날 wrist 직사광선 = 야외 활동 정황)

### Night light exposure (chronobiology risk)
- 21:00 ~ 06:00 시간대를 다음날 sleep_date에 attribute
- 805 (subject, sleep_date) row
- `mlight_night_h_bright`: 잠자기 전 휴대폰 100 lux 초과 시간 — Q1과 **-0.187** 상관 (수면질 ↓)

---

## 10. Phase D — Apps, Mobility, Cross-modal Coherence

**노트북**: `notebooks/09_apps_mobility_coherence.py`
**산출물 5개**: `09_app_categories_daily.parquet`, `09_app_prebed_categories.parquet`, `09_mobility_daily.parquet`, `09_coherence_hourly.parquet`, `09_coherence_daily.parquet`

### 앱 19 카테고리 분류 (한글 키워드 기반)

```
other          6.88B sec   (시스템 UI, 캐시워크, 당근 — refine 가능)
os_launcher    5.27B sec
messenger      2.50B sec
news           1.44B sec
sns            955M sec
video          905M sec
religion       787M sec    ← id01의 "성경일독Q" 비중 매우 큼
call           679M sec
finance        387M sec
camera         351M sec
shopping       278M sec
...
```

### Pre-bedtime (21:00 ~ 02:00) app mix
- 753 (subject, sleep_date) row × 19 카테고리
- → `prebed_video_sec`, `prebed_sns_sec` 등 잠자기 전 디지털 행동 시그니처

### Mobility 5 modes (GPS speed bin)

```
stationary    (<0.3 m/s)   6,745,662
walk          (0.3-1.5)    1,199,857
bike_or_jog   (1.5-4.0)      232,611
vehicle       (4.0-15.0)     238,440
transit_hispeed (>15.0)     130,362
```

→ 매일 (subject, date) 별 각 mode 분 + **outings** (stationary → motion 전환 횟수)

### Cross-modal Coherence (가장 흥미로운 발견)

mActivity ↔ wPedo 같은 분에서 motion 동의/불일치 비율:

| subject | agree_rate | only_act | only_ped | 해석 |
|---|---|---|---|---|
| **id10** | **0.877** | 0.080 | 0.043 | phone+watch 항상 같이 다님 |
| id09 | 0.867 | 0.094 | 0.039 | |
| id06 | 0.843 | 0.108 | 0.050 | |
| id01 | 0.841 | 0.122 | 0.037 | |
| id07 | 0.809 | 0.127 | 0.064 | |
| id04 | 0.798 | 0.111 | 0.091 | watch 자주 벗고 운동 |
| id08 | 0.790 | 0.177 | 0.032 | |
| id02 | 0.762 | 0.184 | 0.054 | |
| id05 | 0.743 | 0.213 | 0.043 | watch 자주 벗음 |
| **id03** | **0.689** | 0.179 | **0.132** | **phone과 watch 가장 따로 다님** |

**인사이트:**
- **id03 outlier** — phone과 watch가 따로 노는 사람. 모델링 시 큰 노이즈 원인.
- 모든 subject에서 `only_act > only_ped` — phone이 watch보다 motion 잘 감지 (주머니/가방 진동, watch는 손목 위라 정지 많음).
- `only_act` 높음 = "watch 손목에 있는데 정지인 시간이 많음" = 책상 위 phone + watch 운동 또는 phone 흔들리는 동안 watch 정지

---

## 11. Phase E — Master Daily Table

**노트북**: `notebooks/10_master_daily_table.py`
**산출물**: `10_master_daily.parquet` (700 row × **232 col**), `10_master_columns.csv`, `10_master_corr_highlights.csv`

### 통합 결과
- **700 row × 232 column** 단일 분석 base
- 모든 derived parquet을 `(subject_id, lifelog_date)` 또는 `(subject_id, sleep_date)` 키로 join
- 모델링/시각화/탐색의 base table

### Missingness summary

| group | mean % missing |
|---|---|
| night_hrv | 41.3% |
| label (test rows) | 35.7% |
| hrv_daily | 11.0% |
| deviation | 8.9% |
| light_night | 7.5% |
| coherence | 6.9% |
| 기타 | < 6% |

### 라벨과 가장 강한 상관 (|r| ≥ 0.10, n=450)

#### Q1 (수면질)

| feature | r |
|---|---|
| **mlight_night_h_bright** | **-0.187** |
| longest_block_min | +0.148 |
| agree_rate | -0.144 |
| only_ped_rate | +0.134 |
| ble_novelty_ratio | -0.115 |
| tst_min | +0.109 |
| amb_night_silence | +0.108 |
| mlight_night_max | +0.104 |
| only_act_rate | +0.102 |

→ **밤에 phone 스크린이 밝은 시간이 길수록 다음날 주관적 수면질이 안 좋음** (-0.187, 가장 강력한 단일 신호). longest_block_min, tst_min 같은 객관적 sleep duration도 + 상관.

#### Q2 (피로 ↓=좋음)

| feature | r |
|---|---|
| **mlight_mean** | **-0.147** |
| night_hr_mean | +0.134 |
| gps_home_ratio | +0.121 |
| sleep_eff | -0.122 |
| wifi_novelty_ratio | -0.110 |
| outings | -0.109 |
| tst_min | -0.108 |
| longest_block_min | -0.103 |

→ 외부 활동 많은 날(mlight, wifi novelty, outings)이 더 피로. 의외로 `night_hr_mean` 높을수록 피로 적음 (저녁에 운동/활동 → 다음날 피로 낮음 가설).

#### Q3 (스트레스 ↓=좋음)

| feature | r |
|---|---|
| **mlight_night_max** | **+0.158** |
| mlight_mean | -0.136 |
| gps_home_ratio | +0.131 |
| night_sdnn | +0.105 |
| amb_vehicle | -0.083 |

→ 집에 있는 비율 높을수록 스트레스 적음 (자연스러움). 밤 밝은 빛은 +0.158 — 의외 (실내 조명에서 안정?).

#### S1 (TST 권고 충족)

| feature | r |
|---|---|
| **outings** | **+0.175** |
| **gps_home_ratio** | **+0.170** |
| only_ped_rate | +0.140 |
| longest_block_min | +0.138 |
| tst_min | +0.134 (proxy 검증 양의 신호) |
| sol_proxy_min | -0.131 |
| gps_elsewhere_ratio | (negative side) |

#### S2 (Sleep Efficiency)

| feature | r |
|---|---|
| **outings** | **+0.196** |
| sns_sec | -0.131 |
| night_sdnn | +0.120 |
| z_abs_mean | +0.118 |
| prebed_sns_sec | -0.138 |

→ SNS 사용이 sleep efficiency에 negative. 잠자기 전 SNS는 특히 강함.

#### S3 (SOL — 입면 잠복기)

| feature | r |
|---|---|
| **outings** | **+0.254** ← 마스터 corr 중 가장 강함 |
| agree_rate | +0.147 |
| ble_novelty_ratio | +0.147 |
| mlight_night_h_bright | +0.132 |
| only_act_rate | -0.113 |
| only_ped_rate | -0.111 |
| night_hr_mean | -0.128 |

→ **활동적인 날 → 빨리 잠** (outings, ble_novelty). night_hr_mean -0.128 (밤 HR 낮을수록 SOL 충족 — 부교감 활성).

#### S4 (WASO)

| feature | r |
|---|---|
| **mlight_night_h_bright** | **+0.135** |
| prebed_video_sec | +0.117 |
| n_awakenings | +0.121 |
| night_rmssd | -0.120 |

→ 잠자기 전 비디오, 밤 밝은 화면 → WASO 권고는 충족 (얕은 수면이지만 짧은 awakening?). RMSSD ↓ (부교감 약함) → WASO 충족 ↑.

---

## 12. 핵심 인사이트 — 두 기존 워크스페이스가 못 본 것

### A. Outings — 단일 가장 강한 sleep 신호

`outings`는 **하루 stationary → motion 전환 횟수**. mGps 8M point를 minute-level mode로 분류한 후 그래프 transition count로 추출됨. raw daily aggregation으로는 절대 못 얻는다.

- S3 (입면 잠복기 충족)과 +0.254 — 모든 feature 중 가장 강한 단일 상관
- S2 +0.196, S1 +0.175 — sleep family 전반에 강력
- 신호의 본질: **활동량이 아니라 활동 패턴의 "다이내믹"** (외출/귀가 횟수)

### B. mlight_night_h_bright — 잠자기 전 화면 노출 시간

`mlight_night_h_bright`은 21h~06h 사이 휴대폰 광량 > 100 lux인 분 수. 즉 **잠자기 전 phone screen을 밝게 켜고 있는 시간**.

- Q1 (수면질) -0.187 ← 가장 강력
- S4 (WASO 충족) +0.135 (얕은 수면이지만 awakening 짧음)
- Q3 -0.095 (스트레스 영향 약함)

**bedside phone use가 sleep 영역에 명확한 흔적을 남김.**

### C. Phone-Watch Coherence Rate

`agree_rate`, `only_act_rate`, `only_ped_rate` — phone과 watch의 motion 동의 패턴.

- Q1 -0.144 (불일치할수록 수면질 ↑ → "운동" 가설)
- S3 +0.147 (일치율 높을수록 SOL 권고 충족 → 규칙적 생활?)
- id03 outlier (0.689) — phone과 watch가 따로 다님 → 데이터 노이즈 원인 identifier

### D. Place identity from 익명화 좌표

GPS 좌표가 익명화돼도 클러스터 자체는 valid. 10명 중 7명에서 명확한 home + work 패턴 자동 추출. id05 vs id07 vs id10의 *lifestyle archetype* 분리가 자동.

### E. App category × 잠자기 전 사용

`prebed_sns_sec`, `prebed_video_sec` — 잠자기 전 1~5시간 (21h~02h) 카테고리별 사용 시간.

- prebed_sns_sec — S2 (SE) -0.138 (SNS가 수면효율 ↓)
- prebed_video_sec — S4 +0.117 (비디오는 짧은 awakening 패턴)

이건 daily app totals보다 더 강한 신호.

### F. Per-subject Deviation Engine

(Subject, hour-of-day) baseline 위에서 z-score는 *raw daily*보다 평균 +0.036 AUC를 짜낸다. 6/7 타깃에서 부호 +. 다만 단일 feature 단독 효과는 약함 (multivariate fusion 필요).

### G. id별 lifestyle archetype 자동 분리

| subject | archetype |
|---|---|
| **id04** | "롱슬리퍼" — 9.7h TST, sleep_eff 0.89 |
| **id07** | "표준 직장인" — 명확한 출퇴근, coherence 0.81 |
| **id06** | "안정 가정형" — 2 home grid + ample sleep |
| **id05** | "집순이" — vehicle 비중 0.003, 짧은 TST |
| **id03** | "phone-watch 따로 노는 사람" — coherence 0.69, 데이터 노이즈 출처 |
| **id10** | "야간 분산 outlier" — home grid 0개, 짧은 TST 324분 |
| **id08** | "토막잠" — TST 312분, sleep_eff 0.63 |

이 archetype 정보가 사람별 prediction에 prior로 사용 가능.

---

## 13. 데이터 가공 산출물 인덱스 (`artifacts/`)

### 가장 중요한 것
- **`10_master_daily.parquet`** — 700 row × 232 col 분석 base
- **`10_master_corr_highlights.csv`** — 핵심 feature × label Pearson 상관

### Phase A — 위치/장소 (5)
- `06_places.parquet` — 42,594 places (home/work/other/transient 라벨링)
- `06_daily_place_durations.parquet` — 700 row, 매일 home/work/elsewhere 분
- `06_wifi_core_fingerprint.parquet` — 1,199 core BSSID
- `06_ble_core_fingerprint.parquet` — 105 core BLE device
- `06_daily_novelty.parquet` — 매일 wifi/ble/gps novelty score

### Phase B — 수면/생체 (5)
- `07_sleep_events.parquet` — 4,855 events (envelope + awakenings)
- `07_sleep_summary.parquet` — 700 nights summary (TST, eff, awakenings, onset, wake)
- `07_hrv_hourly.parquet` — 7,986 시간별 HRV
- `07_hrv_daily.parquet` — 623 일별 HRV
- `07_night_hrv.parquet` — 623 sleep-envelope 내 HRV

### Phase C — 환경 (6)
- `08_ambience_hourly_buckets.parquet` — 16,040 hourly × 13 bucket
- `08_ambience_daily.parquet` — 700 일별 sound bucket
- `08_ambience_subject_signature.parquet` — 10 subject signature
- `08_light_daily.parquet` — 700 일별 광 노출 (mLight + wLight)
- `08_light_night.parquet` — 805 (subject, sleep_date) 야간 광 노출
- `08_ambience_class_freq.parquet` — 517 class freq

### Phase D — 앱/이동성/일관성 (5)
- `09_app_categories_daily.parquet` — 690 row × 19 카테고리
- `09_app_prebed_categories.parquet` — 753 (subject, sleep_date) prebed mix
- `09_mobility_daily.parquet` — 700 일별 5 mode + outings
- `09_coherence_hourly.parquet` — 시간별 phone-watch agreement
- `09_coherence_daily.parquet` — 일별 agreement_rate + only_act/only_ped

### 기반 — Hourly Grid + Deviation (5)
- `01_coverage_table.parquet` — 700 (subject, date) coverage
- `03_hourly_grid.parquet` — 16,580 × 30
- `03_hod_variability.parquet` — (subject, hod) std per feature
- `04_features_raw_daily.parquet` — 700 row × 19 raw daily mean (baseline 비교용)
- `04_features_deviation_daily.parquet` — 700 row × 63 deviation feature
- `04_baseline_med_mad.parquet` — 240 (10 subj × 24 hod) median + MAD

### 시각화 (PNG)
- `01_coverage_heatmap.png` — (subject × date) 활성 modality 카운트
- `01_label_correlation.png` — 7×7 라벨 상관 매트릭스
- `02_tst_proxy_vs_S.png` — TST proxy vs S1~S4 산점도
- `03_hod_signatures.png` — 시간대별 modality 신호 per subject
- `03_still_variability.png` — (subject × hod) still_ratio 변동성

---

## 14. 한계와 honest caveats

1. **S1~S4 ground truth (Withings BCG)가 없음** — 어떤 모델도 proxy reconstruction. AUC 0.65 정도가 sleep family의 천장.

2. **wHr 밤 커버리지 47%** — 절반의 nights는 wrist HR 없음. `night_hr_mean` 분석은 부분적.

3. **night_hr_mean ≈ 88 (낮 평균과 같음)** — PPG 워치의 한계 + sleep envelope이 "조용한 깨어있는 시간"을 일부 포함. 진짜 sleep 시 HR 일반적으로 60대인데 우리 데이터에선 88.

4. **AUC ≠ log loss** — Phase 1c에서 +0.036 AUC lift가 log loss로 transfer되지 않음을 확인. 단일 deviation feature가 subject-mean prior 위에 추가하는 정보는 약함. multivariate fusion + calibration이 필요.

5. **GPS 좌표 익명화** — round(4)가 너무 strict해서 id02의 같은 집이 4개 grid로 쪼개짐. round(3)로 재처리 필요 시 옵션.

6. **mAmbience 노이즈** — "Snake" 42K, "Wild animals" 41K 같은 false positive 다수. bucket 매핑으로 일부 완화했지만 잔여 노이즈 존재.

7. **앱 카테고리화 키워드 기반** — "other" 6.88B sec (전체의 30%) 다수 남음. 추가 룰 refine 가능 (당근=shopping, 캐시워크=health 등).

8. **id03 phone-watch coherence 0.69** — 데이터 노이즈 source. 모델링 시 별도 처리 필요할 수 있음.

---

## 15. 추천 다음 단계 (데이터 가공 기준)

### 즉시 가능한 작업

**F. 시각화** — 핵심 발견 plot:
- 매일 sleep timeline (10 subjects × 시간축)
- per-subject home/work/other duration calendar heatmap
- prebed app category trend
- 라벨일 / 라이프로그 align 시각화

**G. Second-order feature engineering**:
- 강한 신호의 routine deviation (outings의 z-score by subject)
- Lag features (어제 outings, 이틀 전 mlight_night_h_bright)
- Interaction terms (outings × home_ratio, prebed_video × n_awakenings)

**H. Subject clustering / archetype label**:
- 10명을 행동 패턴 5~6 그룹으로 자동 군집 → 라벨 imbalance 진단
- "type" feature 추가 (집순이 / 직장인 / 야행성 / 토막잠형 / 표준)

**I. Test set 250일 lifelog 분석**:
- 같은 10명이지만 후기 날짜
- train 분포와 비교 (drift?)
- 잠재적 semi-supervised target

### 모델링 단계는 별도 (필요 시)
- Per-subject 작은 모델 (advisor 권장)
- Cascade: S 예측 → Q feature로
- Multi-task LightGBM with stronger regularization

---

## 16. 메모리에 박힌 핵심 사실

(memory: `~/.claude/projects/-Users-kbsoo-Downloads-dacon/memory/etri_lifelog_2026_data_truth.md`)

1. S1~S4 ground truth는 Withings Sleep Analyzer (BCG) — 데이터셋에 없음. 어떤 model도 proxy.
2. Q1~Q3는 per-subject relative. subject mean = 0.5 by construction.
3. Train+test는 같은 10 subject의 서로 다른 700일을 정확히 분할.
4. wHr 밤 커버리지 47% — sleep 신호는 mActivity+mScreen 주축, wHr 보조.

---

*문서 종료. 라이프로그 6.12M 행이 22개 derived parquet + 1개 master table로 압축되었음.*
