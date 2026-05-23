# Prior ETRI Lifelog competition research

Date: 2026-05-22

## What was searched

Queries included:

- `ch2026_metrics_train lifelog Q1 Q2 Q3 S1 S2 S3 S4`
- `ch2025_mUsageStats lifelog dacon sleep stress`
- `DACON ETRI lifelog sleep stress Q1 Q2 Q3 S1 S2 S3 S4`
- `ETRI 휴먼이해 인공지능 논문경진대회 라이프로그 수면 스트레스 후기`
- `데이콘 라이프로그 수면 스트레스 ETRI 후기 코드공유`

## Relevant sources found

### 2026 / current-like repositories

1. `dragonzzuny/ETRI_2026`
   - Mentions current task as ETRI 2026, 7 binary targets, average log-loss.
   - Claims sensor parquet files are byte-identical to the 2025 package; Q1/Q2/Q3/S2/S3 unchanged; S1 relabeled from 3-class to binary; S4 added.
   - Reported ideas: DALN image model, MAE pretraining on train+test sensor images, subject/time embeddings, per-group heads, TabPFN/LGB stacking, drift removal, LOSO sanity checking.
   - Important caveat: repo looks like another participant's active/current solution notes; scores/claims should be treated as unverified until reproduced.

2. `JAYUN-KIM/dacon-ETRI_lifelog`
   - Current 2026 repository with detailed experiment log.
   - Reported best public LB: 0.5877431660.
   - Main gains: conservative probability shrink, target-wise Q/S routing, 3-seed ensemble, subject-date prior, adaptive date confidence, sleep-window alignment, weak S-only sleep metric proxy.
   - Their own retrospective says heavy feature expansion and recent/change features often degraded; stable anchors + thin priors worked best.

3. `youngjune0507/-etri-lifelog-2026`
   - Current 2026 repository.
   - Reported best LB 0.5946.
   - Uses date-level feature engineering over 11 sensors, sleep-period features, lag/rolling/EMA/pct_change, target encoding, LGB/XGB/Cat ensemble with per-target blend.
   - Notes OOF != LB, subject-hole CV inappropriate because train/test share subjects; fewer top features improved OOF but hurt LB.

### 2025 / previous DACON repository

4. `csm3310/ETRI_lifelog-project`
   - 2025 DACON/ETRI lifelog sleep prediction, reportedly 1st place and ICTC 2025 paper.
   - Method summary: explainable time-series feature engineering, daily/subject aggregation, IQR/MAD/diff/EMA/expanding/zero-crossing/date features, LightGBM + CatBoost ensemble with CatBoost-heavy blend.
   - Reported public leaderboard macro-F1 about 0.62555.

5. `meanmaxx/Sleep-Quality-and-Condition-Prediction-using-Lifelog-Data`
   - 2025/term-project style repo with ch2025 files and multiple experiments.
   - Methods include GRU sequence model, DWT preprocessing, XGB/RF/logistic/stacking/TabPFN tests, per-target model selection.

### 2024 / earlier winner

6. Blog: `sjkoding.tistory.com/95`, “제3회 ETRI 휴먼이해 인공지능 논문경진대회 대상 리뷰”
   - Team PixleepFlow / paper `arXiv:2502.17469`.
   - Key idea: convert synchronized lifelog sensor streams into daily composite images; also test raw 1D-CNN and spectrogram variants.
   - Details from blog/paper: resample to 1Hz, synchronize each day to 86,400 points, linear interpolation except leading/trailing missing zones, then form composite image/spectrogram/raw inputs.
   - Models: timm SEResNeXt/ResNeXt, ensemble.
   - Important data insight from that year: distribution/domain mismatch made the officially named validation split closer to test than older train; using the mismatched train hurt.
   - XAI insights: acceleration Y/Z, heart rate, time in bed, and subtle phone-use/movement during sleep were important.

7. Dataset paper: `arXiv:2508.03698`, ETRI Lifelog Dataset 2024
   - Confirms 700 days, 450 train / 250 evaluation for 2024 dataset.
   - Baseline features: wPedo, wHr, wLight, mLight, mUsageStats, demographics + day-of-week.
   - App usage categorized into System/Social/Hobby daily minutes.
   - LightGBM default baseline; day-of-week/demographics materially change performance.

## Extracted method patterns

### Strongly repeated useful patterns

1. Subject/date prior is central.
   - Public repos emphasize personal baselines and close-date status flow.
   - This matches our current observation that subject prior is hard to beat.

2. Sleep target windows should cross midnight.
   - Prior solutions explicitly use evening/pre-sleep/overnight/morning/full-sleep-context windows such as 18-24, 21-03, 00-08, 06-12, 18-12.
   - Our current `03_build_daily_window_features.py` has some 21-03/00-06 daily buckets but not full row-specific `lifelog_date + hour` windowing with `sleep_date` alignment across all key sensors.

3. S targets benefit from hand-crafted sleep metric proxies.
   - Rest duration, sleep efficiency, sleep latency badness, WASO badness from overnight screen/activity/steps/light/HR variation.
   - Prior best used these only as a weak S-only nudge, not a full replacement model.

4. Target-wise routing/blending matters.
   - Q and S targets prefer different feature/model/prior mixtures.
   - CatBoost-heavy or XGB-heavy blends appear common; current project uses mostly logistic probes, so stronger tree anchors may still be worth testing if not already done.

5. Heavy feature expansion often overfits.
   - Multiple repos warn that local OOF improvements can hurt public LB.
   - Probability shrink / clipping is important under log-loss.

6. Image/patch representation is a plausible orthogonal branch.
   - PixleepFlow winner used synchronized sensor images and SEResNeXt/ResNeXt.
   - Current project already has DINO/SSL-style hourly representations, but not exactly the 1Hz/86,400-composite-image recipe.

## Highest-value experiments for current `cl`

Priority 1 — Reproduce prior-style sleep-window features:
- Build row-level windows keyed by `(subject_id, lifelog_date, sleep_date)` for 18-24, 21-03, 00-08, 06-12, 18-12.
- Sensors: mActivity, mLight, mScreenStatus, mACStatus, wHr, wLight, wPedo first.
- Add contrasts: overnight/evening, pre_sleep/evening, morning/overnight.
- Evaluate only by target-wise small additions, especially Q1/S1/S2/S3/S4.

Priority 2 — S-only sleep metric proxy prior:
- Create proxy_rest_duration, proxy_sleep_efficiency, proxy_sleep_latency_bad, proxy_wake_after_sleep_bad.
- Calibrate proxy to train labels by rank bins with heavy smoothing.
- Blend weakly into current best only for S targets; grid small weights like 0.02-0.12.

Priority 3 — Subject-date interpolation prior:
- For each subject/target, interpolate or nearest-neighbor smooth train label probabilities by date/order.
- Confidence should decay with distance from train dates; target/subject reliability scaling.
- Blend weakly with current anchor. This is high-LB-risk but prior repos say it produced largest gains.

Priority 4 — Current-year label/data reuse sanity:
- If old 2025 labels are available externally/locally, verify Q1/Q2/Q3/S2/S3 identity and S1 mapping. Do not assume blindly.
- If identical, use prior-year code insights but avoid data leakage beyond allowed competition package.

Priority 5 — Lightweight PixleepFlow branch:
- Avoid full 1Hz 86,400 image first; create 24h x sensor-channel low-res images/hourly patches from already built hourly features.
- Train small CNN/linear over embeddings or use self-supervised DINO/MAE only as auxiliary OOF/test features.
- Use as orthogonal blend, not primary model, unless CV/LB proves stable.

## Practical conclusion

The most actionable missing direction is not more generic external data/modeling. Prior competitors mostly won with:

- subject-specific temporal priors,
- sleep-window alignment,
- S-metric proxy nudges,
- conservative target-wise blending/calibration,
- and occasionally image-form sensor representation.

For the current project, implement `sleep-window + proxy-prior + weak targetwise blend` before spending more time on external foundation models.
