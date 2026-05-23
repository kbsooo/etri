# DACON ETRI Lifelog/Sleep Multi-Label Prediction — Experiment Plan

> **For Hermes:** 데이터 가설/feature engineering이 1순위다. 모델 참신성은 큰 supervised model이 아니라 self-supervised latent representation + small calibrated head 방향으로 실험한다.

**Goal:** `Q1,Q2,Q3,S1,S2,S3,S4` 평균 logloss를 낮추기 위해, subject/day lifelog representation과 sleep/behavior latent features를 체계적으로 실험한다.

**Architecture:** raw parquet sensor streams를 subject/day 단위 feature table과 time-bin sequence tensor로 변환한다. 먼저 domain-driven features와 strong validation을 만든 뒤, masked/denoising/contrastive representation을 학습하고 small supervised head 및 calibration/blending을 적용한다.

**Tech Stack:** Python, duckdb/pyarrow/polars or pandas, numpy, scikit-learn, PyTorch, optional LightGBM/CatBoost for diagnostic baseline only.

---

## 0. Working Principles

1. **Feature/data 가설이 90%**다. 모델 구조보다 sensor proxy 설계가 먼저다.
2. **Tree-only에 머무르지 않는다.** Tree는 baseline/diagnostic/feature sanity check 용도다.
3. **큰 supervised Transformer는 피한다.** label 450개로는 overfit 위험이 너무 크다.
4. **self-supervised day representation을 우선한다.** label 없이 sensor structure를 학습한다.
5. **subject prior는 버리지 않는다.** test subject가 train subject와 같기 때문에 subject-level bias는 강력한 정보다.
6. **chronological validation만 신뢰한다.** random KFold는 날짜 leakage 가능성이 크다.
7. **logloss는 calibration 게임이다.** clipping, smoothing, blending을 반드시 한다.

---

## Stage 1. Data/Validation Foundation

### Experiment 1. Subject-wise Chronological CV

**Objective:** LB와 유사한 local validation을 만든다.

**Files:**
- Create: `src/validation.py`
- Create: `notebooks/01_validation_sanity.ipynb` or `scripts/01_validation_sanity.py`

**Plan:**
- 각 subject별 lifelog_date 기준 정렬.
- 각 subject 마지막 20%, 25%, 30%를 valid로 쓰는 fold 생성.
- label 분포, subject 분포, date range를 fold별로 저장.

**Expected output:**
- `outputs/validation/folds_20_25_30.json`
- fold별 target mean report.

**Why:**
- test는 같은 subject의 미래/다른 날짜다.
- random split은 sensor temporal autocorrelation 때문에 성능 과대평가 가능성이 높다.

---

### Experiment 2. Global/Subject Prior Baseline

**Objective:** 모든 모델이 이겨야 할 logloss 기준선을 만든다.

**Files:**
- Create: `src/baselines.py`
- Create: `scripts/02_subject_prior_baseline.py`

**Features/Models:**
- global target mean
- subject target mean
- smoothed subject prior:

```python
p = (subject_pos + alpha * global_mean) / (subject_count + alpha)
```

**Alpha candidates:**

```text
1, 3, 5, 10, 20, 50
```

**Validation:**
- chronological folds에서 alpha/target별 logloss 확인.

**Expected insight:**
- 어떤 target이 subject prior에 강하게 의존하는지 확인.
- 특히 `S3`, `S1`, 일부 subject-specific Q-label에서 강할 가능성.

---

## Stage 2. Domain Feature Table

### Experiment 3. Daily Aggregate Feature Table

**Objective:** 모든 parquet를 `subject_id + lifelog_date` 단위로 요약한 기본 feature table을 만든다.

**Files:**
- Create: `src/features/daily_aggregates.py`
- Create: `scripts/03_build_daily_features.py`
- Output: `features/daily_features.parquet`

**Sensors:**
- `mACStatus`
- `mActivity`
- `mAmbience`
- `mBle`
- `mGps`
- `mLight`
- `mScreenStatus`
- `mUsageStats`
- `mWifi`
- `wHr`
- `wLight`
- `wPedo`

**Aggregates:**
- numeric: mean, std, min, max, median, p10, p90, count, missingness
- list/struct: count, unique count, mean length, max length, entropy-like summaries
- timestamps: coverage minutes, first timestamp, last timestamp

**Why:**
- 이후 모든 모델/latent experiment의 shared base.

---

### Experiment 4. Time-Window Features

**Objective:** 수면/피로/스트레스와 관련된 시간대별 behavior를 분리한다.

**Files:**
- Modify: `src/features/daily_aggregates.py`
- Output: `features/window_features.parquet`

**Windows:**

```text
all_day:        00:00-24:00
morning:        06:00-12:00
afternoon:      12:00-18:00
evening:        18:00-24:00
late_evening:   21:00-24:00
night:          00:00-06:00
sleep_proxy:    21:00-03:00
post_midnight:  00:00-03:00
```

**High-value sensors by window:**
- screen: 21-03, 00-06
- light: evening/night/morning
- HR: night/day split
- pedo/GPS: evening/night movement
- app usage: late usage
- ambience: night speech/music/vehicle/outside

---

### Experiment 5. Subject-Normalized Features

**Objective:** 개인 평균 대비 deviation을 feature화한다.

**Files:**
- Create: `src/features/normalization.py`
- Output: `features/subject_normalized_features.parquet`

**Transforms:**

```text
x_raw
subject_mean(x)
subject_std(x)
x - subject_mean
(x - subject_mean) / subject_std
x / (subject_mean + eps)
rank within subject
percentile within subject
rolling_3d_mean, rolling_7d_mean
x - rolling_3d_mean
x - rolling_7d_mean
```

**Leakage variants:**
1. strict CV: train fold only statistics
2. transductive feature-only: train+test sensor feature statistics

**Why:**
- `Q1~Q3`는 개인 평균 대비 label이다.
- subject deviation이 raw absolute value보다 중요할 가능성이 높다.

---

## Stage 3. Sleep/Recovery Proxy Features

### Experiment 6. Sleep-Like Block Detection

**Objective:** 직접 sleep sensor 없이 lifelog에서 수면 구간 proxy를 추정한다.

**Files:**
- Create: `src/features/sleep_proxy.py`
- Output: `features/sleep_proxy_features.parquet`

**Signals:**
- screen off
- low activity
- low steps
- low movement/GPS
- low light
- resting HR
- charging status

**Features:**

```text
estimated_bedtime
estimated_wakeup
estimated_sleep_opportunity_minutes
longest_inactive_block_minutes
longest_screen_off_block_minutes
low_light_block_minutes
sleep_block_start_hour
sleep_block_end_hour
sleep_block_midpoint
night_interruptions_count
screen_on_during_sleep_block
light_spikes_during_sleep_block
steps_during_sleep_block
hr_spikes_during_sleep_block
fragmentation_index
```

**Target hypotheses:**
- `S1`: sleep block length
- `S2`: sleep block fragmentation / interruptions
- `S3`: late screen/light/activity before sleep block
- `S4`: interruptions inside sleep block
- `Q1`: overall sleep block quality

---

### Experiment 7. Daytime Load + Night Recovery Features

**Objective:** Q2/Q3 피로/스트레스 proxy를 구성한다.

**Files:**
- Create: `src/features/load_recovery.py`
- Output: `features/load_recovery_features.parquet`

**Load features:**
- total steps/distance/calories
- GPS movement/radius of gyration
- high HR duration
- app usage total/entropy/fragmentation
- screen pickup count
- BLE/WiFi density
- ambience speech/vehicle/outside

**Recovery features:**
- sleep-like block length
- resting HR proxy
- night light/screen interruptions
- darkness duration

**Interaction features:**

```text
day_load_score
night_recovery_score
load_minus_recovery
high_load_low_recovery_flag
```

---

## Stage 4. Semantic Sensor Features

### Experiment 8. App Usage Semantics

**Objective:** `mUsageStats`를 cognitive load/stress proxy로 변환한다.

**Files:**
- Create: `src/features/app_semantics.py`
- Output: `features/app_semantic_features.parquet`

**Features:**
- total app time
- number of apps
- app entropy
- top1 app share
- late app time
- category usage time

**Initial categories:**

```text
messenger/social
video/music
browser/search/news
game
health/fitness
study/work/productivity
religion/personal
finance/shopping
unknown
```

**Caution:**
- app name one-hot은 overfit 위험.
- category/time/entropy 위주로 시작한다.

---

### Experiment 9. Mobility and Location Regularity

**Objective:** GPS/WiFi/BLE에서 routine deviation과 social/environmental density를 추정한다.

**Files:**
- Create: `src/features/mobility.py`
- Output: `features/mobility_features.parquet`

**Features:**
- radius of gyration
- total movement distance
- stationary time ratio
- home cluster time ratio
- away-from-home hours
- late-night mobility flag
- unique WiFi/BLE counts
- new WiFi/BLE ratio
- near device count

**Hypotheses:**
- 평소보다 이동량/장소 변화가 크면 fatigue/stress에 영향.
- late-night mobility는 sleep labels에 악영향.

---

### Experiment 10. Ambience Semantics

**Objective:** ambient sound predictions를 stress/sleep disturbance proxy로 사용한다.

**Files:**
- Create: `src/features/ambience.py`
- Output: `features/ambience_features.parquet`

**Features:**
- speech/music/vehicle/outside/inside probability sums
- night noise proxy
- ambience entropy
- top-class transition count

**Hypotheses:**
- night speech/music/vehicle/outside는 sleep quality/efficiency 악화.
- daytime speech/outside/social density는 stress/fatigue와 관련 가능.

---

## Stage 5. Latent Representation Experiments

### Experiment 11. Time-Bin Sequence Tensor

**Objective:** latent model input용 sequence representation을 만든다.

**Files:**
- Create: `src/sequence/build_time_bins.py`
- Output: `features/timebin_1h.parquet` or `features/timebin_30m.parquet`
- Output: `features/day_sequence_tensor.npz`

**Resolution candidates:**

```text
1h = 24 tokens/day
30m = 48 tokens/day
```

**Token features:**
- screen
- steps/distance/speed
- light
- HR
- activity
- GPS movement
- app usage
- ambience grouped probabilities
- WiFi/BLE density
- charging
- missingness indicators

**Important:**
- missingness itself is a feature.
- features should be subject-normalized as an optional channel.

---

### Experiment 12. Masked Sensor Modeling Encoder

**Objective:** label 없이 sensor sequence structure를 학습한다.

**Files:**
- Create: `src/models/masked_sensor_encoder.py`
- Create: `scripts/12_train_masked_sensor_encoder.py`
- Output: `models/masked_sensor_encoder.pt`
- Output: `features/masked_encoder_embeddings.parquet`

**Architecture:**
- small Transformer encoder
- input: `[batch, time_bins, sensor_dim]`
- output: reconstructed masked values + day embedding

**Masking strategies:**
- random time-bin mask
- random sensor-channel mask
- contiguous time-block mask
- modality dropout

**Embedding extraction:**
- CLS token or mean pooling
- output `z_day` dimension candidates: 16, 32, 64

**Downstream:**
- logistic/ridge/MLP head on `z_day`
- combine with domain features

---

### Experiment 13. Denoising Autoencoder

**Objective:** diffusion-inspired forward/reverse idea를 lightweight하게 실험한다.

**Files:**
- Create: `src/models/denoising_autoencoder.py`
- Create: `scripts/13_train_denoising_autoencoder.py`
- Output: `models/denoising_autoencoder.pt`
- Output: `features/dae_embeddings.parquet`

**Corruptions:**
- Gaussian noise on continuous features
- random masking
- sensor modality dropout
- time-block dropout
- shuffled small windows, optional

**Loss:**
- MSE for continuous normalized features
- BCE/CE for binary/categorical-derived features
- missingness-aware loss masking

**Hypothesis:**
- Bottleneck latent captures daily rhythm/recovery state.

---

### Experiment 14. Contrastive Day Representation

**Objective:** same-subject nearby days and similar routine days를 latent space에서 가깝게 만든다.

**Files:**
- Create: `src/models/contrastive_day_encoder.py`
- Create: `scripts/14_train_contrastive_encoder.py`
- Output: `features/contrastive_embeddings.parquet`

**Positive pairs:**
- same subject adjacent days
- same subject same weekday-ish
- two augmented views of same day

**Negative pairs:**
- different subject days
- same subject distant/unlike days, optional

**Caution:**
- subject identity만 배우면 안 된다.
- 하지만 test subject가 같으므로 subject identity가 완전히 나쁜 정보는 아니다.

---

### Experiment 15. Unsupervised Behavioral State Clustering

**Objective:** time-bin을 latent behavioral state로 clustering하고 day-level state features를 만든다.

**Files:**
- Create: `src/features/behavioral_states.py`
- Output: `features/behavioral_state_features.parquet`

**Methods:**
- KMeans/GMM on time-bin features
- candidates K: 6, 8, 12, 16

**Day features:**
- state occupancy ratio
- state transition counts
- longest sleep-like state duration
- screen-heavy -> sleep-like transition time
- sleep-like state interruption count

**Why promising:**
- 참신하지만 안정적이다.
- sleep labels에 설명력 좋을 수 있다.
- neural overfit 위험이 낮다.

---

## Stage 6. Small Supervised Heads and Calibration

### Experiment 16. Linear/Ridge/MLP Probes

**Objective:** latent embeddings와 domain features를 작은 supervised model로 연결한다.

**Files:**
- Create: `src/models/probes.py`
- Create: `scripts/16_train_probes.py`

**Candidates:**
- logistic regression with L2
- ridge-like linear classifier
- tiny MLP with dropout
- multi-task shared MLP + 7 heads
- target-specific heads

**Inputs:**
- domain features only
- latent z only
- domain + z
- domain + z + subject prior

---

### Experiment 17. Target Relation / Stacking

**Objective:** target 간 correlation을 OOF prediction으로 활용한다.

**Observed correlations:**
- `Q2-Q3 ≈ 0.34`
- `Q1-S1 ≈ 0.36`
- `S2-S4 ≈ 0.48`
- `S2-S3 ≈ 0.39`

**Plan:**
- first-stage OOF predictions for all labels
- second-stage model uses original features + OOF target predictions
- test uses first-stage predictions as meta-features

**Caution:**
- leakage 방지 위해 반드시 OOF만 사용.
- 작은 데이터라 target pair-specific stacking부터 시도.

---

### Experiment 18. Calibration and Blending

**Objective:** logloss를 직접 낮춘다.

**Files:**
- Create: `src/calibration.py`
- Create: `scripts/18_calibrate_and_blend.py`

**Methods:**
- probability clipping: `[0.03,0.97]`, `[0.05,0.95]`, `[0.08,0.92]`
- subject prior blend:

```python
final = w * model_pred + (1 - w) * subject_prior
```

- target-specific `w`
- temperature scaling on logits
- Platt scaling, if enough validation stability

**Caution:**
- isotonic은 overfit 위험이 높다.

---

## Stage 7. Experiment Tracking

### Experiment 19. Result Ledger

**Objective:** 모든 실험 결과를 한 곳에 정리한다.

**Files:**
- Create: `experiments/results.md`
- Create: `experiments/runs.csv`

**Record fields:**

```text
run_id
date
features
model
validation_scheme
fold_logloss_mean
target_logloss
notes
submission_file
```

---

## Immediate Next Actions

1. `src/` 구조 만들기.
2. validation folds + subject prior baseline 구현.
3. daily/window feature builder 구현.
4. sleep proxy v0 구현.
5. time-bin tensor builder 구현.
6. latent model 중 가장 가벼운 것부터:
   - behavioral state clustering
   - denoising autoencoder
   - masked sensor encoder
7. calibration/blending layer 구현.

---

## Current Priority Ranking

High ROI / Low Risk:

1. subject prior + chronological CV
2. daily/window aggregates
3. subject-normalized deviation
4. sleep-like block detection
5. behavioral state clustering
6. calibration/blending

High Upside / Medium Risk:

1. denoising autoencoder
2. masked sensor modeling
3. contrastive day encoder
4. multi-task small MLP with latent z

Low Priority Initially:

1. full diffusion model
2. large supervised Transformer
3. raw app/WiFi/BLE one-hot
4. random KFold leaderboard chasing


---

## Implementation Status — 2026-05-22

Completed initial infrastructure and first artifacts.

### Done

```text
src/cl_common.py
scripts/01_make_folds.py
scripts/02_subject_prior_baseline.py
scripts/03_build_daily_window_features.py
scripts/04_build_timebin_features.py
scripts/05_build_sleep_proxy_v0.py
scripts/06_build_model_features_v0.py
scripts/07_behavioral_state_clustering.py
```

Generated:

```text
outputs/validation/folds_chrono.json
experiments/subject_prior_results.json
experiments/subject_prior_results.csv
experiments/results.md
features/daily_window_features.parquet
features/timebin_1h_features.parquet
features/sleep_proxy_v0.parquet
features/behavioral_state_features_k8.parquet
features/model_features_v0.parquet
```

Subject prior baseline currently gives best chrono fold result:

```text
chrono_last_25 / alpha=20 / mean logloss=0.6343930851520722
```

`model_features_v0.parquet` covers all train/test rows:

```text
train join: 450/450
test join: 250/250
rows: 700
cols: 258
```

### Next implementation target

1. non-tree probe evaluation over `model_features_v0.parquet`
2. app/WiFi/BLE/ambience semantic features
3. stronger sleep-block detection
4. denoising or masked time-bin encoder


---

## Update — No-anchor feature-only direction

Byungsoo does not want subject-prior anchoring/blending. The prior remains only a diagnostic baseline.

Current best feature-only non-tree result:

```text
semantic_only SelectK+Logistic
fold chrono_last_25
mean logloss 0.631418
average over chronological folds for semantic_only k=20 C=0.001: 0.633684
```

Actionable direction:

1. Do target-specific semantic/sleep feature selection.
2. Reduce noisy flattened hourly features to hypothesis-driven windows/bins.
3. Implement self-supervised latent features without large supervised models.
4. Keep documentation in `experiments/results.md`.


---

## Update — after failed 0.5x push with more aggregates

Additional routine/top-k/stacking/tree diagnostics did not reach 0.5x. Clean best is now target-specific feature-only logistic:

```text
average chronological CV: 0.622735
```

Main blockers:

```text
Q2 fatigue: 0.6903
S4 WASO:    0.6884
```

Next plan should stop adding generic columns and focus on two target-specific mechanisms:

1. `S4`: infer sleep episode + interruptions/WASO proxy from screen/steps/light/charging/HR.
2. `Q2`: daytime physiological/behavioral load and evening recovery imbalance.
3. Then add self-supervised hourly latent embedding, because aggregate features appear saturated.


## 2026-05-22 — Mechanism-first v2: cross-night correction + Q2 daytime flat

User asked to continue toward 0.5x. Key discovery: `ch2026_metrics_train.csv` has both `sleep_date` and `lifelog_date`; `sleep_date = lifelog_date + 1`. Previous sleep-block features used same-date 00-05 + 20-23, which mixes the morning **before** the lifelog day with that evening. For sleep outcomes, the plausible episode is evening of `lifelog_date` plus morning of `sleep_date`.

### New scripts

```text
scripts/23_build_mechanism_sleep_load_features.py
scripts/24_train_mechanism_target_ablation.py
scripts/25_train_target_specific_mechanism_v2.py
scripts/26_build_crossnight_day_flat_features.py
```

### New features

```text
features/mechanism_sleep_load_features_v2.parquet
features/crossnight_day_flat_features_v2.parquet
```

Feature groups:

- `s4x_*`: cross-night inferred sleep episode and interruption features.
  - evening `lifelog_date` 18-23 + morning `sleep_date` 00-12
  - longest quiet/screen-off runs
  - inferred onset/wake/midpoint
  - inside-block screen/step/light/HR spike interruptions
  - pre-sleep and post-wake activity
- `q2x_*`: daytime load/evening recovery aggregate features.
- `day_h*`: hour-preserving daytime/evening flat features for Q2.
- `cn_h*`: hour-preserving cross-night flat features.

### Hard-target ablation

Q2 improved materially when using hour-preserving daytime features:

```text
Q2 previous target-specific: ~0.6903
Q2 sleep_plus_s4x:          ~0.6539
Q2 day_flat best:           ~0.6341
```

S4 improved materially from the cross-night sleep episode correction:

```text
S4 previous target-specific: ~0.6884
S4 sleep_plus_s4x best:      ~0.6089
```

This confirms the earlier hypothesis: the main bottleneck was not generic model capacity; it was mechanism alignment and the night boundary.

### Current clean best

Updated target-specific clean chronological CV:

```text
script: experiments/probe_target_specific_mechanism_v2_results.csv

chrono_last_20: 0.592605
chrono_last_25: 0.601295
chrono_last_30: 0.612080
average:        0.601994
```

Target averages:

```text
Q1: 0.633735
Q2: 0.634128
Q3: 0.649689
S1: 0.539650
S2: 0.569550
S3: 0.578272
S4: 0.608930
```

Compared to previous best clean target-specific average:

```text
before: 0.622735
after:  0.601994
improvement: -0.020742 logloss
```

And compared to earlier feature-only best row around `0.6314`, the new clean multi-fold average is about `-0.0294` better.

### Important caveat

Average is still barely above 0.60, not safely in the 0.5x range. One fold is now 0.5926, but the 3-fold average is 0.6020.

Current bottleneck shifted:

- `Q2` and `S4` are no longer catastrophic; both moved from ~0.69 to ~0.63/~0.61.
- `Q3` is now the worst target at ~0.65.
- `Q1/Q2/Q3` subjective questionnaire labels remain harder than objective sleep targets.

### Failed/neutral follow-up

Clean Q3 meta with Q2 prediction did not help:

```text
Q3 base avg: 0.6497
Q3 meta with Q2 pred: 0.6585
```

So label-relation stacking remains overfit-prone.

### Next direction

The best next ROI is now Q3/Q1 subjective-state modeling, not more S4/Q2 engineering:

1. Build stress/arousal features for Q3:
   - late HR elevation relative to day/subject baseline
   - late screen/app + low movement + high HR pattern
   - ambience speech/music/vehicle/outside in late window
   - previous-night interruption carry-over
2. Build questionnaire-specific latent state features from hourly streams.
3. Consider self-supervised day embedding now that mechanism aggregates are near 0.60.


---

## Current Update — Q3/Q1 subjective-state feature branch

Implemented and evaluated:

```text
scripts/27_build_stress_arousal_q_features.py
scripts/28_tune_subjective_q_features.py
features/stress_arousal_q_features_v1.parquet
```

TimesFM review takeaway applied: use patch/window tokenization as the design lever. Built compact hourly patch summaries over `06-23 + 00-03`, with late-chunk normalization vs daytime chunk, plus Q3 stress/arousal and Q1 morning-recovery features.

Result: no clean CV improvement. Q1 still chooses `semantic_only`; Q3 still chooses `sleep_only`; average remains `0.601994`.

Next plan adjustment:

1. Stop expanding supervised Q3/Q1 aggregate features unless a sharply new signal source is found.
2. Move to latent sequence representation:
   - hourly token tensor from HR/screen/steps/light/activity/app/ambience/GPS/WiFi/BLE;
   - per-subject/day normalization;
   - masked/denoising reconstruction or behavioral-state contrastive objective;
   - small target-specific logistic heads.
3. Keep current mechanism features for Q2/S4 as the strongest clean baseline.
