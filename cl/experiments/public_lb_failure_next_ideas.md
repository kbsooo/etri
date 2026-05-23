# Public LB failure diagnosis and next improvement ideas

Context: `submission_prior_sleep_conservative_q1q2s4_prob.csv` scored public LB `0.6421303776` despite local CV `~0.5933`. It changed only Q1/Q2/S4 vs `submission_base_v4_replicate_prob.csv`.

## Diagnosis

The bad submission is not a file-format problem. It is likely targetwise-sweep overfit.

Changed targets vs base:

| target | mean abs delta | max abs delta | corr vs base | interpretation |
|---|---:|---:|---:|---|
| Q1 | 0.1221 | 0.4939 | 0.717 | too large / unstable |
| Q2 | 0.0772 | 0.6243 | 0.725 | too large / unstable |
| S4 | 0.0528 | 0.2724 | 0.964 | closer to base, more plausible |

With only one public LB scalar, we cannot know which target caused the damage. If unknown base public LB was around 0.59–0.60, the average public damage on changed Q1/Q2/S4 was roughly +0.10 to +0.12 per changed target, which is severe.

## Immediate submission rule

Do not submit any more broad Q1/Q2/S4 replacement unless it passes a stronger robustness gate. The previous 3-fold chrono targetwise sweep is insufficient.

## High-leverage experiments

### 1. Robustness gate before any submission

Create `scripts/47_validate_targetwise_robustness.py`.

Evaluate base vs candidates under:
- existing chrono_last_20/25/30;
- last-month / leave-calendar-block validation;
- leave-one-subject diagnostic;
- bootstrap over subject-days;
- train/test feature drift and prediction-shift checks.

Reject if:
- any target worsens base by >0.01 on a chrono fold;
- Q1 test mean abs shift vs base >0.06;
- Q2 test mean abs shift vs base >0.05;
- S4 test mean abs shift vs base >0.04;
- selected features are dominated by unstable broad `psw_*` family.

### 2. Q1 compact sleep-quality index, not broad psw_all

Create:
- `scripts/48_build_sleep_quality_index_features.py`
- `scripts/49_eval_q1_sleep_quality_index.py`

Features should be compact/interpretable:
- inferred sleep duration;
- sleep midpoint;
- onset/wake lateness;
- interruption count/rate;
- screen/light/step interruptions;
- HR evening-to-sleep drop;
- HR sleep-to-morning recovery;
- darkness/charging consistency;
- morning recovery score;
- episode confidence/missingness.

Use logistic with `k <= 15` or single-index calibration. Must beat Q1 base on all chrono folds and shift much less than the failed Q1 candidate.

### 3. Q2 daytime load and evening recovery curve

Create:
- `scripts/50_build_q2_load_recovery_features.py`
- `scripts/51_eval_q2_load_recovery.py`

Q2 is physical fatigue before sleep. Avoid sleep-window rescue. Build:
- cumulative steps/distance/calories by cutoff 06–12/15/18/21;
- HR load above subject median, p90/p95, high-HR minutes;
- GPS movement/commute-like proxies;
- app/screen/social burden;
- WiFi/BLE environment changes;
- evening HR recovery slope;
- activity drop afternoon→evening;
- late screen persistence after high-load day;
- evening charging/rest opportunity.

Evaluate subsets: `q2_load_only`, `q2_recovery_only`, `q2_load_recovery`, `q2_load_recovery+day_flat_top20`.

### 4. S4 event-level WASO detector

Create:
- `scripts/52_build_s4_event_waso_features.py`
- `scripts/53_eval_s4_event_waso.py`

Use timestamp-level data, not just hourly aggregates. Infer sleep episode boundaries, then count interruption events inside the episode:
- screen-on bursts;
- step bursts;
- light spikes;
- HR spikes relative to sleep HR;
- charging changes;
- activity transitions;
- clustered interruption minutes;
- first-half vs second-half interruptions;
- episode confidence/missingness.

This is the most mechanism-plausible path for S4 and should replace broad `psw_all`.

### 5. Cross-night prototype clusters for Q1/S4

Create:
- `scripts/54_train_crossnight_sleep_prototypes.py`
- `scripts/55_eval_q1_s4_crossnight_prototypes.py`

Build 18:00 lifelog_date → 12:00 sleep_date sequences with screen/steps/activity/light/charging/HR/missingness. Train compact unsupervised prototypes with KMeans `k=3..10`. Use cluster one-hot, distances, entropy, confidence as features. Evaluate Q1/S4 only. This mirrors the DiNO cluster lesson: compact prototypes are safer than high-dimensional supervised heads.

### 6. Q2 daytime prototype clusters

Create:
- `scripts/56_train_q2_dayload_prototypes.py`
- `scripts/57_eval_q2_dayload_prototypes.py`

Use 06:00–24:00 lifelog_date sequences for physical/social load and recovery. Cluster day types and use prototype distances instead of fragile raw `day_h*` expansion.

### 7. Family-stability targetwise selection

Create `scripts/58_targetwise_family_stability_selection.py`.

Score candidate families by:

`robust_score = mean_logloss + λ1*fold_std + λ2*feature_instability + λ3*train_test_shift + λ4*prediction_shift_vs_base`

This should replace the old oracle-style targetwise sweep for choosing submission configs.

## Current recommendation

No current new file deserves “확신” for public 0.5x. The most rational candidate generated so far is `outputs/submission_lbshot_revert_q1q2_keep_s4_prob.csv`, but it is still not certainty. The next work should be feature generation + robustness gate, not another blind submission.
