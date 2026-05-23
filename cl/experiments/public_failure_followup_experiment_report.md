# Public failure follow-up experiments

Date: 2026-05-22

## Context

Bad submitted file: `outputs/submission_prior_sleep_conservative_q1q2s4_prob.csv`

Public LB: `0.6421303776`

The file changed only Q1/Q2/S4 versus `outputs/submission_base_v4_replicate_prob.csv` and therefore the follow-up goal was to test mechanism-specific replacements without repeating the broad targetwise `psw_*` sweep failure.

## Implemented scripts

- `scripts/47_run_public_failure_followups.py`
  - Builds new feature artifact: `features/public_failure_followup_features_v1.parquet`
  - Runs Q1/Q2/S4 target sweeps.
  - Runs conservative stability selection.
  - Outputs candidate: `outputs/submission_followup_stability_selected_prob.csv`
- `scripts/48_followup_alt_robustness.py`
  - Compares base, bad public config, and follow-up S4-only config under extra diagnostics.
  - Outputs: `experiments/followup_alt_robustness_results.csv`

## New feature families tested

### Q1 compact sleep-quality index

Prefix: `q1qual_*`

Features include inferred sleep episode length, onset/wake/midpoint, interruption rate, screen/step/light/HR interruptions, HR drop/recovery, darkness/charging consistency, morning recovery proxies, missingness, and episode confidence.

### Q2 load/recovery features

Prefix: `q2lr_*`

Features include cumulative daytime load by cutoff, HR-load proxies, app/screen/social burden, GPS/context movement, evening/late recovery, activity drop, late screen after high-load day, and load/recovery scores.

### S4 event-level WASO proxies

Prefix: `s4evt_*`

Features include inferred episode interruption counts, screen/step/activity/light/HR burst proxies, first/second-half interruptions, interruption clusters, longest uninterrupted segment, and episode confidence.

### Prototype features

Prefixes:

- `cnproto_*`: cross-night 18:00→12:00 prototype clusters.
- `q2proto_*`: daytime 06:00→24:00 load prototype clusters.

## Main target sweep results

### Q1

Best remained the original baseline:

| rank | subset | mean CV |
|---:|---|---:|
| 1 | `semantic_only` | **0.633735** |
| 2 | `q1qual+semantic` | 0.635595 |
| 3 | `q1qual+semantic+cnproto` | 0.642644 |
| standalone | `q1qual` | 0.705599+ |

Conclusion: the compact Q1 sleep-quality index did not improve Q1. It is safer than broad `psw_all` in concept, but current implementation is not predictive enough.

### Q2

Best remained the original baseline:

| rank | subset | mean CV |
|---:|---|---:|
| 1 | `day_flat` | **0.634128** |
| 2 | `q2lr+day_flat` | 0.683491 |
| standalone | `q2lr` | 0.688865+ |

Conclusion: the new daytime load/recovery features are currently too noisy or incorrectly scaled. They do not justify replacing Q2.

### S4

Tiny improvement from S4 event/prototype fusion:

| rank | subset | mean CV |
|---:|---|---:|
| 1 | `s4evt+sleep+cnproto` | **0.608617** |
| 2 | `sleep_plus_s4x` baseline | 0.608930 |
| 3 | `s4evt+sleep` | 0.609185 |
| standalone | `s4evt` | 0.702900+ |

Fold deltas for selected S4 candidate versus base:

- chrono_last_20: `-0.000871`
- chrono_last_25: `+0.001190`
- chrono_last_30: `-0.001259`

Conclusion: S4 improvement exists but is extremely small and not enough for a confident submission.

## Stability-selected candidate

File:

`outputs/submission_followup_stability_selected_prob.csv`

Config:

- Q1/Q2/Q3/S1/S2/S3: unchanged from base.
- S4: `s4evt+sleep+cnproto`, `k=200`, `C=0.003`.

CV:

| model | mean CV |
|---|---:|
| base recheck | 0.601643 |
| stability selected | 0.601598 |

Change versus base submission:

| target | changed rows | mean abs delta | max abs delta | corr vs base |
|---|---:|---:|---:|---:|
| S4 | 239 | 0.005216 | 0.036791 | 0.9994 |
| all others | 0 | 0 | 0 | 1.0 |

This is much safer than the failed public submission, but it is only a tiny perturbation and does not create 0.5x confidence.

## Alternate robustness diagnostics

Output: `experiments/followup_alt_robustness_results.csv`

Across existing chrono folds, tail-14/tail-21 folds, and LOSO diagnostics:

| model | diagnostic mean | std | min | max |
|---|---:|---:|---:|---:|
| bad_public_cfg | 0.679994 | 0.083876 | 0.550161 | 0.851891 |
| base | 0.687904 | 0.081396 | 0.580691 | 0.849979 |
| followup_s4_only | 0.687534 | 0.081155 | 0.580004 | 0.847931 |

Important: these alternate diagnostics still do not explain the public failure of `bad_public_cfg`, because that config looks good in many local diagnostics. Therefore local validation is still not public-LB-faithful enough.

## Honest conclusion

All proposed follow-up families were implemented/tested at a first-pass level. None produced a candidate that deserves “0.5대 확신”.

The best new file is:

`outputs/submission_followup_stability_selected_prob.csv`

But it is only `0.601643 → 0.601598` local CV and changes S4 by a very small amount. It is safer than the failed submission but not a confident breakthrough.

Recommended next direction if continuing:

1. Do not submit current follow-up unless using it as a very low-risk diagnostic.
2. The real bottleneck remains Q1/Q2. Current sensor-derived Q1/Q2 features are not strong enough.
3. Need either:
   - a public-LB-calibrated validation discovery if more submissions can be spent, or
   - a genuinely different data source/label insight for Q1/Q2, not more aggregate/prototype variants.
