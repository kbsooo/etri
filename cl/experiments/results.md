# Experiment Results Ledger

## 2026-05-22 — Project bootstrap / validation / baseline / feature v0

### Environment

```bash
cd /Users/kbsoo/Downloads/cl
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### Implemented files

```text
requirements.txt
src/__init__.py
src/cl_common.py
scripts/01_make_folds.py
scripts/02_subject_prior_baseline.py
scripts/03_build_daily_window_features.py
scripts/04_build_timebin_features.py
scripts/05_build_sleep_proxy_v0.py
scripts/06_build_model_features_v0.py
scripts/07_behavioral_state_clustering.py
```

### Generated artifacts

```text
outputs/validation/folds_chrono.json
experiments/subject_prior_results.json
experiments/subject_prior_results.csv
features/daily_window_features.parquet
features/timebin_1h_features.parquet
features/sleep_proxy_v0.parquet
features/behavioral_state_features_k8.parquet
features/model_features_v0.parquet
```

### Validation folds

Subject-wise chronological folds:

```text
chrono_last_20: train 359 / valid 91
chrono_last_25: train 339 / valid 111
chrono_last_30: train 316 / valid 134
```

### Subject prior baseline

Best among alpha/clipping grid:

```text
fold: chrono_last_25
alpha: 20
clip: 0.0
mean logloss: 0.6343930851520722
```

Target logloss:

```text
Q1: 0.683018521875428
Q2: 0.6667606216495826
Q3: 0.6810905400204265
S1: 0.546791006111851
S2: 0.6207001800723062
S3: 0.5834536716477198
S4: 0.6589370546871907
```

Interpretation:

- Subject prior alone is already non-trivial.
- `S1`, `S3`, `S2` benefit relatively strongly from subject-specific priors.
- Any feature/latent model should beat ~0.634 average logloss under chrono validation, or be used only as a blended component.

### Feature artifacts sanity check

```text
features/daily_window_features.parquet: rows=700, cols=40
features/timebin_1h_features.parquet: rows=16579, cols=18
features/sleep_proxy_v0.parquet: rows=700, cols=15
features/behavioral_state_features_k8.parquet: rows=700, cols=15
features/model_features_v0.parquet: rows=700, cols=258
```

Coverage:

```text
train join rows: 450 / 450
test join rows: 250 / 250
subjects: 10
date range: 2024-06-03 ~ 2024-11-19
```

### Feature v0 contents

`daily_window_features.parquet` currently includes robust high-signal sensor aggregates:

- screen status: all-day, 21-03, 00-06, 18-24
- pedometer: steps/distance/calories/speed + windowed steps
- mobile/wearable light: mean/max + morning/evening/night windows
- activity: mean + night sum
- charging: mean/any/night mean

`sleep_proxy_v0.parquet` includes lightweight sleep proxy features:

- sleep window screen sum
- sleep window steps sum
- sleep window light mean/max
- quiet hours where screen=0 and steps=0
- sleep window active hours
- pre-sleep 21-03 screen/steps
- morning/evening light means

`behavioral_state_features_k8.parquet` includes unsupervised time-bin clustering features:

- 8 behavioral state occupancy ratios
- state entropy
- transition count
- dominant state
- night entropy
- night transition count

`model_features_v0.parquet` combines the above and adds subject-level normalization:

- raw numeric feature
- subject mean
- subject delta
- subject z-score

### Next experiments

1. Add semantic features for app/WiFi/BLE/ambience.
2. Improve sleep proxy from simple window sums to true longest inactive/screen-off block detection.
3. Train small non-tree probes:
   - subject prior only
   - features v0 logistic/ridge
   - behavioral state only
   - features + behavioral state
4. Add denoising autoencoder or masked sensor encoder over `timebin_1h_features.parquet`.
5. Implement calibration/blending script using subject prior + model predictions.


### Logistic probe v0

Implemented:

```text
scripts/08_train_logistic_probe_v0.py
experiments/probe_logistic_l2_results.csv
experiments/probe_logistic_l2_best.json
experiments/probe_predictions/*.csv
```

Best result over C grid:

```text
model: logistic_l2_features_v0
C: 0.01
fold: chrono_last_25
mean logloss: 0.6511481669415247
```

Target logloss:

```text
Q1: 0.6714569182270461
Q2: 0.7170165785013957
Q3: 0.7023527924592118
S1: 0.590053215323838
S2: 0.6075616785034861
S3: 0.6298478977147675
S4: 0.6397480878609277
```

Interpretation:

- Raw feature v0 logistic probe is worse than smoothed subject prior baseline.
- This does **not** mean features are useless; it means current feature set/head needs either:
  1. subject-prior blending,
  2. better semantic/sleep-block features,
  3. stronger representation learning,
  4. target-specific feature selection/regularization.
- Current best pure baseline remains subject prior: `0.63439`.
- Interesting sign: feature probe improves/competes on `Q1`, `S2`, `S4` compared to some prior targets, but hurts `Q2/Q3/S3`; target-specific blending is likely necessary.


## 2026-05-22 — Feature-only / no-anchor continuation

User feedback: do **not** use subject prior as an anchor/blend. Treat prior only as a diagnostic baseline; continue with feature-only, non-tree experiments.

### New feature artifacts

Implemented additional data/feature scripts:

```text
scripts/09_build_semantic_features_v1.py
scripts/10_build_sleep_block_features_v1.py
scripts/11_train_selectk_logistic_probe.py
scripts/12_train_pca_mlp_probes.py
scripts/13_build_timebin_flat_features.py
scripts/14_train_feature_subset_probes.py
```

Generated:

```text
features/semantic_features_v1.parquet          # rows=700, cols=59
features/sleep_block_features_v1.parquet       # rows=699, cols=15
features/timebin_1h_flat_features.parquet      # rows=700, cols=266
features/model_features_v0.parquet             # rows=700, cols=1594 after joins + subject-normalized variants
```

### Semantic feature v1

Added feature families from richer modalities:

- wearable heart rate: mean/std/min/max and sleep/evening/morning windows
- GPS: speed/distance proxies and night/evening movement summaries
- app usage: use count, unique app count, usage entropy, night/evening usage, app-category proxies
- WiFi/BLE: density/unique-count/social-context proxies
- ambience: probability summaries and night/evening acoustic-context proxies

### Improved sleep-block features

Added simple hourly sequence-derived sleep proxies:

- longest quiet run over 20:00-05:00
- longest screen-off run
- quiet/screen-off start/end hour
- fragmentation count
- late screen/activity last hour
- dark-hour count and bright interruption hours

### Non-tree feature-only probes

No subject-prior anchoring/blending was used.

#### SelectK + Logistic, all features

After adding semantic/sleep/flat hourly features, naive all-feature SelectK logistic got worse than the previous no-flat version:

```text
best all-feature row:
fold=chrono_last_25
k=50
C=0.003
mean logloss=0.639602
```

This suggests the flattened hourly expansion adds noise/overfit unless carefully subsetted.

#### PCA/MLP probes

PCA logistic and small MLPs were worse:

```text
best PCA/MLP row:
model=pca16_logistic
fold=chrono_last_25
mean logloss=0.667529
```

MLPs are currently not promising under this validation/data size.

#### Feature subset SelectK + Logistic

Best feature-only, non-tree result so far:

```text
model=feature_subset_selectk_logistic
subset=semantic_only
n_features=228
k=20
C=0.003
fold=chrono_last_25
mean logloss=0.631418

Q1=0.663616
Q2=0.697934
Q3=0.693202
S1=0.557155
S2=0.561828
S3=0.594304
S4=0.651891
```

Across the three chronological folds, the most stable configs were also semantic-only:

```text
semantic_only, k=20, C=0.001 -> avg fold logloss 0.633684
semantic_only, k=20, C=0.003 -> avg fold logloss 0.633865
semantic_only, k=20, C=0.010 -> avg fold logloss 0.635771
```

### Interpretation

Important: this is not using subject-prior anchoring. The best row `0.6314` is feature-only and slightly below the earlier prior diagnostic `0.6344`.

The main signal currently appears to come from semantic modalities, not from naive dense hourly flattening:

```text
HR + GPS + app + WiFi/BLE + ambience > all features with hourly flattening
```

This supports the original hypothesis that data/feature interpretation matters more than generic model capacity.

### Next hypotheses

1. Refine semantic features further instead of increasing model size.
2. Split target families:
   - Q targets may prefer app/GPS/ambience/HR daytime features.
   - S targets may prefer HR + light + screen + quiet-block features.
3. Build target-specific feature subsets rather than one shared feature set.
4. Add low-risk self-supervised latent features from time-bin tensors, but keep heads small.
5. Treat flat hourly features cautiously; use selected night/evening bins instead of all 24×channels.


## 2026-05-22 — Pushing below 0.63: additional data hypotheses

User feedback: `0.63` is still too high; target should be at least `0.5x`. Continued with data-hypothesis experiments rather than subject-prior anchoring.

### Diagnostic: metric definitions

Extracted `ch2026_metrics_description.pdf`.

Key label semantics:

- `Q1`: subjective sleep quality above/below individual average after waking.
- `Q2`: physical fatigue before sleep; `1` means lower fatigue than individual average.
- `Q3`: stress before sleep; `1` means lower stress than individual average.
- `S1`: total sleep time guideline.
- `S2`: sleep efficiency guideline.
- `S3`: sleep onset latency guideline.
- `S4`: wakefulness after sleep onset guideline.

Implication: Q labels are not absolute; they are individual-relative latent questionnaire labels. This explains why subject-normalized deviations matter, but it also means lifelog features may have a ceiling without the actual questionnaire/sleep-sensor streams.

### Label diagnostics

Train label means:

```text
Q1 0.496
Q2 0.562
Q3 0.600
S1 0.682
S2 0.651
S3 0.662
S4 0.560
```

Notable label correlations:

```text
Q2-Q3: 0.340
Q1-S1: 0.361
S1-S2: 0.382
S2-S3: 0.394
S2-S4: 0.478
```

### New feature hypotheses tried

Implemented:

```text
scripts/15_build_routine_deviation_features.py
scripts/16_train_classifier_chains.py
scripts/17_split_diagnostic.py
scripts/18_tree_diagnostic.py
scripts/19_build_semantic_topk_features.py
scripts/20_train_topk_semantic_probe.py
scripts/21_train_target_specific_probe.py
scripts/22_nested_label_stacking.py
```

Generated:

```text
features/routine_deviation_features_v1.parquet
features/semantic_topk_features_v2.parquet
```

Feature ideas:

1. Calendar/time-position features: weekday, weekend, month, subject-time fraction.
2. Routine deviations: previous-day deltas, rolling 3/7-day deviations, weekday-vs-subject deviations.
3. Exact top app usage features: top app time by day/night/evening windows.
4. Exact ambience class features: top AudioSet-like classes by day/night/evening windows.
5. BLE device-class composition.
6. Target-specific feature subsets and hyperparameters.
7. Label-relation/classifier-chain/stacking diagnostics.
8. Tree diagnostic only as a sanity check, not as preferred modeling direction.

### Results

#### Routine deviation features

Routine/rolling deviation features did **not** improve clean CV. They added many noisy columns and worsened generic SelectK logistic.

Best after routine join in generic subset search:

```text
mean logloss ≈ 0.6398
```

Conclusion: rolling/weekday deviations are not currently high-ROI unless feature count is aggressively controlled or target-specific.

#### Exact top app / ambience features

Top app/ambience features also did **not** improve. Best top-k semantic run:

```text
best row ≈ 0.6526
best avg config ≈ 0.6578
```

Conclusion: exact high-cardinality app/ambience columns are noisier than coarse semantic aggregates under current CV.

#### Tree diagnostic

RandomForest/ExtraTrees diagnostic did not break through either:

```text
best row ≈ 0.6302
best avg ≈ 0.6336
```

Conclusion: the issue is not simply “linear model too weak.” Tree models are not revealing a hidden easy signal.

#### Split diagnostic

Random KFold diagnostic with no-flat features:

```text
best random-kfold mean ≈ 0.6183
```

Even random folds do not enter the 0.5x range, which suggests either:

1. Current features still miss the actual questionnaire/sleep-sensor signal, or
2. The labels are intrinsically noisy from phone/wearable proxy data, or
3. We need a different representation layer, not just more aggregates.

#### Target-specific feature-only probe — best clean direction so far

Implemented target-specific feature subsets/hyperparameters without subject-prior anchor:

```text
scripts/21_train_target_specific_probe.py
experiments/probe_target_specific_results.csv
```

Clean chronological CV:

```text
chrono_last_20: 0.621499
chrono_last_25: 0.625088
chrono_last_30: 0.621619
average:        0.622735
```

Target-level average OOF logloss:

```text
Q1: 0.6355
Q2: 0.6903  # weak
Q3: 0.6297
S1: 0.5427  # strongest
S2: 0.5788
S3: 0.5938
S4: 0.6884  # weak/noisy under current proxies
```

This is better than the previous clean `0.6314`, but still far from 0.5x.

#### Label stacking / classifier chain

Naive classifier chains were worse. Proper nested stacking was also worse:

```text
base avg:  0.6227
stack avg: 0.6427
```

A non-clean OOF stacking diagnostic could reach ~0.599, which means label relations have potential, but the clean nested version overfits.

### Current honest diagnosis

The bottleneck is now target-specific:

- `S1`, `S2`, `S3` have real signal and are approaching useful range.
- `Q2` and `S4` are dragging the mean heavily.
- `Q2` is pre-sleep fatigue relative to personal average; phone/wearable features may need much better daytime load/recovery features.
- `S4` is WASO; current phone/wearable proxy does not capture actual wakefulness after sleep onset well enough.

### Next high-ROI hypotheses

1. Build a better sleep episode detector, not just hourly quiet runs:
   - infer sleep onset/wake time from joint screen-off + low steps + darkness + charging + HR drop
   - compute interruptions inside inferred sleep episode
   - derive WASO proxy specifically for `S4`

2. Build daytime load/recovery features for `Q2`:
   - cumulative steps/activity/GPS movement until evening
   - HR load relative to subject baseline
   - late-day fatigue proxies: evening low activity + high HR + screen/app patterns

3. Use sequence/latent route now:
   - current aggregate expansion saturates around 0.62
   - next serious attempt should learn a day embedding from hourly tokens with denoising/masked reconstruction
   - keep small target-specific heads

4. Avoid more high-cardinality top-k expansion unless controlled by target-specific selection; it worsened CV.


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


## 2026-05-22 — Q3/Q1 subjective-state feature attempt with TimesFM-inspired patch summaries

User supplied a TimesFM review. Practical takeaway applied here: treat time-series tokenization/windowing as the core design choice. Instead of a large supervised Transformer on only 450 labels, built compact hourly patch/channel summaries and direct window features:

```text
scripts/27_build_stress_arousal_q_features.py
scripts/28_tune_subjective_q_features.py
features/stress_arousal_q_features_v1.parquet  # rows=700, cols=242
```

Feature ideas implemented:

- Q3 stress/arousal windows: day 06-17, evening 18-20, late 21-24, late cross-midnight 21-04.
- Late HR elevation vs daytime/subject baseline.
- Late screen + low movement + high HR score.
- Social/media/browser app arousal score.
- Ambience speech/music/vehicle/outside score.
- Screen-in-dark and daytime-overstimulation-to-late-arousal proxies.
- TimesFM-style compact hourly patch summaries: 06-23 + 00-03 channels, normalized late chunk vs daytime chunk, vector distance/slope/transition features.
- Q1 morning recovery proxies: morning HR/screen/activity, morning HR vs late HR, recovery-failure score.
- Previous subjective-state carry-over for compact engineered columns.

Important implementation fix:

- Adding `q3x_/q1x_/qpatch_/qcarry_` introduced names containing `late_`, `hr_`, etc. Existing broad subset selectors accidentally pulled these into old `sleep_only`/`semantic_only` subsets and corrupted the baseline.
- Patched `scripts/25_train_target_specific_mechanism_v2.py` and `scripts/28_tune_subjective_q_features.py` so old subsets explicitly exclude the new Q-state prefixes.

### Tuning result

The new Q-state features did **not** improve clean chronological CV.

Best Q1 remained old semantic-only:

```text
Q1 best: subset=semantic_only, k=50, C=0.03
Q1 avg logloss: 0.633735
```

Best Q3 remained old sleep-only:

```text
Q3 best: subset=sleep_only, k=20, C=0.03
Q3 avg logloss: 0.649689
```

Final v3 result equals the previous clean best, not an improvement:

```text
script: experiments/probe_target_specific_subjective_q_v3_results.csv

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

Interpretation:

- The TimesFM review was useful conceptually: patch/window interface matters more than architecture scale.
- But hand-built stress/arousal patch summaries did not expose Q3 signal; they mostly added noisy proxies.
- Q1 also still prefers coarse semantic features, not explicit morning-recovery features.
- Current bottleneck remains Q3 subjective stress. Next serious route should be a self-supervised/unsupervised day embedding over hourly tokens, not more supervised SelectK feature expansion.


## 2026-05-22 — Hourly SSL representation experiments: masked AE + DiNO-inspired temporal SSL

User requested moving from supervised Q1/Q3 feature expansion to SSL over hourly token tensors, and also testing DiNO-inspired ideas.

### Implemented files

```text
scripts/29_train_ssl_hourly_representations.py
scripts/30_eval_ssl_feature_fusion_q.py
features/ssl_hourly_masked_ae_embeddings.parquet
features/ssl_hourly_dino_temporal_embeddings.parquet
experiments/probe_ssl_hourly_q_results.csv
experiments/probe_ssl_hourly_masked_ae_q_results.csv
experiments/probe_ssl_hourly_dino_temporal_q_results.csv
experiments/probe_ssl_feature_fusion_q_results.csv
```

### Setup note

The project `.venv` uses Python 3.13, where `torch` wheels were unavailable. Created `.venv312` with Python 3.12 for the SSL script and installed `torch`, `pyarrow`, `numpy<2`, and the existing requirements. Classical sklearn fusion evaluation still runs on `.venv`.

### SSL inputs

```text
input tensor: 700 subject-days x 24 hourly tokens x 22 channels
base channels: 11 hourly sensor aggregate channels
extra channels: corresponding observed/missingness masks
flat dim: 528
embedding dim: 48
```

### Methods

1. `masked_ae`: denoising/masked autoencoder over flattened 24h token tensor.
2. `dino_temporal`: DiNO-inspired EMA teacher/student where teacher sees full-day global view and student sees temporal crops + modality dropout.

Both produce day embeddings, then Q1/Q3 are evaluated with small target-specific logistic heads under existing subject-wise chronological folds. This is unlabeled transductive SSL over available train+sample-day sensor tensors; no validation labels are used in SSL.

### Latent-only Q1/Q3 probe results

```text
masked_ae avg:
  Q1 logloss: 0.694441
  Q3 logloss: 0.677222
  mean Q logloss: 0.685831

dino_temporal avg:
  Q1 logloss: 0.695665
  Q3 logloss: 0.673753
  mean Q logloss: 0.684709
```

Interpretation:

- Current SSL embeddings alone are weak for Q1/Q3.
- DiNO-inspired temporal SSL is slightly better than masked AE on Q3, but still far behind supervised feature baselines.
- Masked AE has better Q3 AUC than DiNO in this run, but its logloss is worse; calibration/linear separability remains poor.

### Feature + SSL fusion check

`probe_ssl_feature_fusion_q_results.csv` tests SSL embeddings alone and fused with semantic/qstate feature subsets. Best observed rows:

```text
Q1 best remains semantic_only:
  subset=semantic_only, k=50, C=0.03, avg_logloss=0.633735

Q3 best in this reduced fusion grid:
  subset=ssl_dino_temporal_only, k=20, C=0.10, avg_logloss=0.669431
```

Important: the fusion grid did not include the earlier `sleep_only` subset, whose clean best was `Q3=0.649689`, so DiNO is **not** better than the current best Q3 baseline. It only beats other SSL-only variants in this reduced SSL fusion check.

### Conclusion

- We successfully ran both requested SSL directions: masked/denoising hourly encoder and DiNO-inspired temporal local/global SSL.
- The current implementation is a useful plumbing/proof-of-concept, not yet a score improvement.
- The bottleneck is probably representation objective/view design, not just adding SSL machinery. Next improvements should be:
  1. fold-local SSL evaluation vs transductive SSL sanity check,
  2. sequence encoder with real hourly attention/TCN instead of flat MLP,
  3. cross-night 21:00-06:00 episode tensor rather than calendar-day-only tensor,
  4. auxiliary masked reconstruction + teacher/student consistency together,
  5. subject-normalized token values before SSL, and
  6. calibration/tiny head tuning using Q1/Q3-specific windows rather than whole-day latent only.


## 2026-05-22 — SSL semantic cluster discovery

Follow-up to the DiNO-inspired idea list: explicitly tested “semantic cluster” discovery over the new SSL day embeddings.

### Implemented files

```text
scripts/31_ssl_semantic_cluster_probe.py
features/ssl_semantic_cluster_features.parquet
experiments/probe_ssl_semantic_cluster_q_results.csv
```

### Method

- Clustered SSL day embeddings with KMeans for `k ∈ {4,6,8,12}`.
- Embedding sources: `masked_ae`, `dino_temporal`, and concatenated `both`.
- Cluster-derived features: cluster one-hot, distances to centroids, min-distance, entropy-like soft-assignment proxy.
- Evaluated Q1/Q3 with small logistic probes under existing subject-wise chronological folds.

### Best results

```text
Q1 best cluster result:
  method=masked_ae, k=12, avg_logloss=0.684061
  -> not useful vs current Q1 semantic baseline 0.633735

Q3 best cluster result:
  method=dino_temporal, k=4, avg_logloss=0.648236
  folds: 0.647973 / 0.640924 / 0.655810
  avg_auc=0.597786
```

### Interpretation

- Semantic clustering is the first DiNO-inspired component that gives a small clean Q3 improvement over the previous Q3 clean best (`0.649689` sleep-only).
- The improvement is tiny (`~0.00145` logloss), so treat it as promising but fragile until rerun/ablation confirms it.
- Q1 does not benefit; Q1 remains a semantic-feature problem in current experiments.
- The fact that `dino_temporal k=4` works best for Q3 supports the hypothesis that broad behavioral-state clusters may capture stress/arousal state better than raw latent logistic probes.


## 2026-05-22 — Q3 DiNO-cluster fusion and cluster profiling

Follow-up from the DiNO idea checklist: tested whether the best SSL semantic cluster (`dino_temporal`, `k=4`) fuses with existing Q features and profiled the cluster states.

### Implemented files

```text
scripts/32_eval_q_ssl_cluster_fusion.py
scripts/33_profile_ssl_dino_clusters.py
experiments/probe_q_ssl_cluster_fusion_results.csv
experiments/ssl_dino_k4_cluster_profile.csv
experiments/ssl_dino_k4_cluster_profile_compact.csv
```

### Fusion results

Best Q1 remains essentially unchanged:

```text
Q1 semantic_plus_dino_k4: 0.633725
Q1 semantic_only:          0.633735
```

This is a negligible `~0.00001` gain, so Q1 should still be treated as semantic-feature driven.

Best Q3 improved with the cluster feature alone:

```text
Q3 dino_k4_cluster, k=10, C=0.30:
  avg_logloss: 0.647234
  folds: 0.647028 / 0.640463 / 0.654209
  avg_auc: 0.606039

Previous clean Q3 sleep_only best:
  avg_logloss: 0.649689
```

So the DiNO-inspired semantic cluster feature improves Q3 by about `0.00246` logloss vs previous clean best.

Adding the cluster to `sleep_only` did not help in the current SelectK setup; the selected top features remained effectively the sleep-only set. This suggests the cluster is an alternative compact Q3 signal rather than a naive additive feature under univariate selection.

### Cluster profile summary

`ssl_dino_k4_cluster_profile_compact.csv` shows broad behavior-state differences. Train label rates:

```text
cluster 0: days=221, train_days=146, Q3_rate=0.555, Q1_rate=0.459
cluster 1: days=168, train_days=115, Q3_rate=0.591, Q1_rate=0.522
cluster 2: days=252, train_days=152, Q3_rate=0.671, Q1_rate=0.539
cluster 3: days= 59, train_days= 37, Q3_rate=0.514, Q1_rate=0.378
```

Interpretation hypothesis:

- Cluster 2 is the high-Q3/stress cluster: low late screen, low night steps, low late light, low morning steps. This may be a low-signal/low-activity or poor-recovery state rather than obvious phone-arousal.
- Cluster 3 is low-Q3 despite high night/evening steps and higher late screen/light; possibly active/outside/mobile days, not necessarily subjective stress.
- Cluster 0 has high late screen but lower Q3 than cluster 2, which weakens a simplistic “late phone use = stress” hypothesis.
- Cluster 1 is broadly active/bright with medium Q3.

### Takeaway

The best DiNO-derived idea so far is not raw embedding logistic probing, but **prototype/semantic cluster features**. For Q3, `dino_temporal k=4` is now the clean best among tested feature-only/non-anchor variants, though the margin is small and should be treated as fragile until confirmed by reruns and ablations.


## 2026-05-22 — Q3 DiNO cluster sweep, subject diagnostic, and v4 target config

Follow-up requested after the initial DiNO cluster result.

### Implemented files

```text
scripts/34_q3_dino_cluster_sweep_fixed_fusion.py
scripts/35_train_target_specific_v4_dino_q3_cluster.py
features/ssl_dino_cluster_sweep_features.parquet
experiments/probe_q3_dino_cluster_sweep_fusion.csv
experiments/probe_q3_dino_cluster_subject_diagnostic.csv
experiments/probe_target_specific_subjective_q_v4_dino_q3_cluster_results.csv
experiments/probe_target_specific_subjective_q_v4_dino_q3_cluster_oof.csv
experiments/probe_target_specific_subjective_q_v4_dino_q3_cluster_config.json
```

### Q3 cluster sweep and fixed fusion

Swept `dino_temporal` cluster counts `k=3..10` and compared cluster-only vs sleep+cluster fixed-all logistic.

Best cluster-only configs:

```text
dino_k4_cluster_only: avg_logloss=0.647312, avg_auc=0.611920
dino_k3_cluster_only: avg_logloss=0.647903, avg_auc=0.617884
dino_k5_cluster_only: avg_logloss=0.650773
```

The earlier `k=4` result remains the best. `k=3` is close, but `k>=5` degrades.

Fixed-all `sleep_plus_dino_k*` logistic overfits badly (`~0.714` avg logloss), so simple high-dimensional fixed fusion is not useful. The cluster should be used as a compact alternative Q3 feature/prototype, not naively concatenated with all sleep features.

### Subject identity diagnostic

Balanced accuracy for predicting `subject_id` from cluster features only:

```text
k=3:  0.255
k=4:  0.223
k=5:  0.207
k=6:  0.220
k=7:  0.210
k=8:  0.248
k=9:  0.257
k=10: 0.265
```

Random across 10 subjects would be about `0.10`, so clusters contain some subject/routine identity. However, they are not pure subject identifiers. This is acceptable as a feature-only diagnostic under seen-subject chronological validation, but should be watched if the goal is subject-invariant representation.

### Target-specific v4 config

Replaced only Q3 in the previous v3 target-specific config with `dino_k4_cluster`.

```text
Q1: semantic_only, k=50, C=0.03
Q2: day_flat, k=20, C=0.01
Q3: dino_k4_cluster, k=10, C=0.30
S1: no_flat_hourly, k=20, C=0.10
S2: no_flat_hourly, k=20, C=0.001
S3: semantic_only, k=20, C=0.01
S4: sleep_plus_s4x, k=200, C=0.003
```

Results:

```text
chrono_last_20: 0.590152
chrono_last_25: 0.598388
chrono_last_30: 0.616388
average:        0.601643
```

Target averages:

```text
Q1: 0.633735
Q2: 0.634128
Q3: 0.647234
S1: 0.539650
S2: 0.569550
S3: 0.578272
S4: 0.608930
```

Compared with v3 average `0.601994`, v4 improves slightly to `0.601643` entirely from Q3 (`0.649689 -> 0.647234`). The margin is small but directionally consistent with the DiNO prototype hypothesis.

### Interpretation

This work is not primarily “model architecture design.” The supervised model is still deliberately small. The main contribution is **representation/data design**: constructing hourly token views, SSL embeddings, semantic/prototype cluster states, and choosing which compact representation should feed target-specific heads.
