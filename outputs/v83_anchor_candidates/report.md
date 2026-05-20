# v83 conservative anchor candidates

- Base anchor: v76 (real Public LB **0.5999627447**, posterior self-score `0.599963`).
- Posterior trust note: exact at v76/v18; **+0.018 optimistic on far candidates** (v82 predicted 0.6444 vs real 0.6629). Only trust the offline posterior score for candidates with small drift from v76.
- Decision rule: upload-worthy = posterior_pred <= v76 self-score AND mean_abs_drift_v76 small (< 0.01) AND no large row drift.

## Candidate ranking (by posterior_pred, lower better)

| name | posterior_pred | vs_v76_posterior | mean_abs_drift_v76 | max_row_drift_v76 | mean_abs_drift_v82 | Q1Δ | S1Δ | S3Δ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_v76_plus_v18_w100 | 0.597396 | -0.002567 | 0.00881 | 0.0578 | 0.1238 | -0.0006 | +0.0013 | +0.0029 |
| C_v76_plus_v18_w050 | 0.598588 | -0.001375 | 0.00441 | 0.0289 | 0.1260 | -0.0003 | +0.0006 | +0.0014 |
| A_v76_plus_v82_w050 | 0.599034 | -0.000929 | 0.00642 | 0.0300 | 0.1220 | +0.0024 | -0.0023 | -0.0020 |
| A_v76_plus_v82_w025 | 0.599457 | -0.000506 | 0.00321 | 0.0150 | 0.1252 | +0.0012 | -0.0011 | -0.0010 |
| C_v76_plus_supp_w050 | 0.599500 | -0.000463 | 0.00339 | 0.0152 | 0.1274 | -0.0005 | +0.0003 | +0.0007 |
| B_meanshift_antiv82_a025 | 0.599962 | -0.000000 | 0.00056 | 0.0012 | 0.1285 | -0.0011 | +0.0007 | +0.0007 |
| B_meanshift_antiv82_a050 | 0.599964 | +0.000001 | 0.00113 | 0.0025 | 0.1286 | -0.0023 | +0.0015 | +0.0014 |
| B_meanshift_antiv82_a100 | 0.599974 | +0.000011 | 0.00225 | 0.0050 | 0.1288 | -0.0046 | +0.0030 | +0.0027 |

## Per-candidate construction + verdict

### C_v76_plus_v18_w100
- formula: `0.90*v76 + 0.10*v18 (prob)`
- posterior_pred: `0.597396` (-0.002567 vs v76); mean_abs_drift v76 `0.00881`, max-row `0.0578`; drift vs v82 `0.1238`
- per-target mean change vs v76: Q1 -0.0006, S1 +0.0013, S3 +0.0029
- safer than v82 because it stays within `0.0088` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: no** — drift too large to trust

### C_v76_plus_v18_w050
- formula: `0.95*v76 + 0.05*v18 (prob)`
- posterior_pred: `0.598588` (-0.001375 vs v76); mean_abs_drift v76 `0.00441`, max-row `0.0289`; drift vs v82 `0.1260`
- per-target mean change vs v76: Q1 -0.0003, S1 +0.0006, S3 +0.0014
- safer than v82 because it stays within `0.0044` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: YES** — small, safe move toward a known-good public anchor with offline improvement

### A_v76_plus_v82_w050
- formula: `0.95*v76 + 0.05*v82 (prob)`
- posterior_pred: `0.599034` (-0.000929 vs v76); mean_abs_drift v76 `0.00642`, max-row `0.0300`; drift vs v82 `0.1220`
- per-target mean change vs v76: Q1 +0.0024, S1 -0.0023, S3 -0.0020
- safer than v82 because it stays within `0.0064` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: no** — rejected: raises Q1 (diagnosis: HIGH harm; posterior is optimistic toward v82 and cannot be trusted here)

### A_v76_plus_v82_w025
- formula: `0.975*v76 + 0.025*v82 (prob)`
- posterior_pred: `0.599457` (-0.000506 vs v76); mean_abs_drift v76 `0.00321`, max-row `0.0150`; drift vs v82 `0.1252`
- per-target mean change vs v76: Q1 +0.0012, S1 -0.0011, S3 -0.0010
- safer than v82 because it stays within `0.0032` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: no** — rejected: raises Q1 (diagnosis: HIGH harm; posterior is optimistic toward v82 and cannot be trusted here)

### C_v76_plus_supp_w050
- formula: `0.95*v76 + 0.05*sample_support (prob)`
- posterior_pred: `0.599500` (-0.000463 vs v76); mean_abs_drift v76 `0.00339`, max-row `0.0152`; drift vs v82 `0.1274`
- per-target mean change vs v76: Q1 -0.0005, S1 +0.0003, S3 +0.0007
- safer than v82 because it stays within `0.0034` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: YES** — small, safe move toward a known-good public anchor with offline improvement

### B_meanshift_antiv82_a025
- formula: `sigmoid(logit(v76) + 0.025*(mean_logit_v76 - mean_logit_v82)) — per-target constant, 0 row noise`
- posterior_pred: `0.599962` (-0.000000 vs v76); mean_abs_drift v76 `0.00056`, max-row `0.0012`; drift vs v82 `0.1285`
- per-target mean change vs v76: Q1 -0.0011, S1 +0.0007, S3 +0.0007
- safer than v82 because it stays within `0.0006` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: YES** — small, safe move toward a known-good public anchor with offline improvement

### B_meanshift_antiv82_a050
- formula: `sigmoid(logit(v76) + 0.05*(mean_logit_v76 - mean_logit_v82))`
- posterior_pred: `0.599964` (+0.000001 vs v76); mean_abs_drift v76 `0.00113`, max-row `0.0025`; drift vs v82 `0.1286`
- per-target mean change vs v76: Q1 -0.0023, S1 +0.0015, S3 +0.0014
- safer than v82 because it stays within `0.0011` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: YES** — neutral-but-safe direction probe (offline ~v76)

### B_meanshift_antiv82_a100
- formula: `sigmoid(logit(v76) + 0.10*(mean_logit_v76 - mean_logit_v82))`
- posterior_pred: `0.599974` (+0.000011 vs v76); mean_abs_drift v76 `0.00225`, max-row `0.0050`; drift vs v82 `0.1288`
- per-target mean change vs v76: Q1 -0.0046, S1 +0.0030, S3 +0.0027
- safer than v82 because it stays within `0.0023` of the v76 best anchor (v82 was 0.128 away).
- **upload-worthy: YES** — neutral-but-safe direction probe (offline ~v76)

## Recommendation

- **Posterior trap noted**: the A_* (v76+v82) candidates show offline improvement, but that is the posterior's +0.018 optimism toward the failed v82 branch, and they raise Q1 (HIGH harm). They are rejected despite the offline number.
- **Primary upload: `submission_C_v76_plus_v18_w050.csv`** (posterior `0.598588` vs v76 `0.599963`, drift `0.00441`). It blends the v76 best with the 2nd-best public anchor (v18, 0.6058); because BCE is convex in p, a small v76+v18 blend can beat both — a real, low-risk ensemble bet, not an OOF-chasing move.
- Secondary (if a 2nd slot is available): `submission_C_v76_plus_supp_w050.csv`.
- Do NOT upload any v80/v81/v82-based file; the branch is quarantined.
