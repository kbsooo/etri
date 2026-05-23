# Prior-competition sleep-window experiment report

Date: 2026-05-22

## Goal

Reproduce the highest-signal ideas found from prior ETRI Lifelog competitions:

1. Row-level sleep-window feature alignment rather than plain calendar-day aggregation.
2. Hand-crafted sleep metric proxy features/prior for S targets.
3. Conservative target-wise routing/blending from the previous best anchor.

## Files created

### Feature builders

- `scripts/43_build_prior_sleep_window_features.py`
  - Output: `features/prior_sleep_window_features_v1.parquet`
  - Shape: 700 rows x 208 cols.
  - Windows:
    - `sw_evening`: lifelog_date 18:00-24:00
    - `sw_presleep`: lifelog_date 21:00 - next day 03:00
    - `sw_overnight`: next day 00:00-08:00
    - `sw_morning`: next day 06:00-12:00
    - `sw_fullctx`: lifelog_date 18:00 - next day 12:00
  - Sensors:
    - wPedo, mScreenStatus, mActivity, mACStatus, mLight, wLight, wHr.

- `scripts/44_build_prior_sleep_proxy_features.py`
  - Output: `features/prior_sleep_proxy_features_v1.parquet`
  - Shape: 700 rows x 89 cols.
  - Adds cross-window contrasts and proxy scores:
    - `pswp_rest_duration`
    - `pswp_sleep_efficiency`
    - `pswp_sleep_latency_bad`
    - `pswp_waso_bad`
    - `pswp_sleep_quality`
    - `pswp_fatigue_stress`

### Evaluation/training

- `scripts/45_eval_prior_sleep_window.py`
  - Output:
    - `experiments/probe_prior_sleep_window_results.csv`
    - `experiments/probe_prior_sleep_targetwise_best_results.csv`
    - `experiments/probe_prior_sleep_targetwise_best_config.json`
    - OOF prediction files for base/proxy/oracle.

- `scripts/46_train_prior_sleep_submissions.py`
  - Output submissions:
    - `outputs/submission_base_v4_replicate_prob.csv`
    - `outputs/submission_prior_sleep_targetwise_cv0593_prob.csv`
    - `outputs/submission_prior_sleep_conservative_q1q2s4_prob.csv`

## CV results

Baseline replicate:

| model | mean | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base_v4_replicate | 0.601643 | 0.633735 | 0.634128 | 0.647234 | 0.539650 | 0.569550 | 0.578272 | 0.608930 |

Simple feature addition was not good:

| model | mean | note |
|---|---:|---|
| best psw-only | ~0.651 | sleep-window features alone are weak |
| base + psw_all ks1 cm1 | 0.608166 | worse than baseline |
| base + psw_sleep ks1 cm1 | 0.609601 | worse than baseline |
| base + pswp_proxy ks1 cm1 | 0.625322 | worse than baseline |
| rankbin proxy weak blend w0.02 | 0.603449 | close but still worse than baseline |

Target-wise sweep result:

| model | mean | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| prior_sleep_targetwise_best_from_sweep | 0.593248 | 0.609323 | 0.613769 | 0.647234 | 0.539650 | 0.569550 | 0.578065 | 0.595146 |
| prior_sleep_conservative_q1q2s4 | 0.593278 | 0.609323 | 0.613769 | 0.647234 | 0.539650 | 0.569550 | 0.578272 | 0.595146 |

The conservative version only replaces Q1/Q2/S4 with the sweep-selected prior sleep-window variants and leaves Q3/S1/S2/S3 as baseline.

## Selected configs

Target-wise best config from sweep:

```json
{
  "Q1": ["semantic_only+psw_all", 100, 0.009],
  "Q2": ["day_flat+psw_sleep", 40, 0.003],
  "Q3": ["dino_k4_cluster", 10, 0.3],
  "S1": ["no_flat_hourly", 20, 0.1],
  "S2": ["no_flat_hourly", 20, 0.001],
  "S3": ["semantic_only+psw_sleep", 20, 0.01],
  "S4": ["sleep_plus_s4x+psw_all", 200, 0.009]
}
```

Conservative submit candidate:

```json
{
  "Q1": ["semantic_only+psw_all", 100, 0.009],
  "Q2": ["day_flat+psw_sleep", 40, 0.003],
  "Q3": ["dino_k4_cluster", 10, 0.3],
  "S1": ["no_flat_hourly", 20, 0.1],
  "S2": ["no_flat_hourly", 20, 0.001],
  "S3": ["semantic_only", 20, 0.01],
  "S4": ["sleep_plus_s4x+psw_all", 200, 0.009]
}
```

## Interpretation

- Prior-competition idea is real: sleep-window features are not strong standalone features, but target-wise they substantially improve Q1, Q2, and S4 under the current chronological CV.
- CV mean improved from 0.601643 to about 0.59325, much larger than the generic external-data/model experiments.
- However, this is a target-wise sweep over many candidates, so selection bias exists. The safer output is `submission_prior_sleep_conservative_q1q2s4_prob.csv`.
- The rank-bin proxy prior did not help enough in this local CV. It moved Q1/S1 a little in the right direction but damaged S2/S4 enough to lose overall.

## Submission candidates

Validated shape/null/probability range OK for all three files:

1. Baseline safety:
   - `outputs/submission_base_v4_replicate_prob.csv`
2. Best CV target-wise candidate:
   - `outputs/submission_prior_sleep_targetwise_cv0593_prob.csv`
3. Recommended cautious candidate:
   - `outputs/submission_prior_sleep_conservative_q1q2s4_prob.csv`

Recommendation: submit candidate 3 first if submission slots are limited. Candidate 2 is slightly better in CV but differs only by S3 and is more sweep-biased.
