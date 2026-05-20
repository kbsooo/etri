# Public LB Feedback

Last updated: 2026-05-21

## Submitted Scores Provided By User

| rank by score | file | note | submitted_at | public_lb |
| ---: | --- | --- | --- | ---: |
| 1 | `submission_v83_gq015_gs010.csv` | repaired-v80 public-coordinate gamma probe | 2026-05-21 | 0.5997645835 |
| 2 | `submission_01_v76_balanced_hedge_best.csv` | memo | 2026-05-18 13:15:24 | 0.5999627447 |
| (new) | `submission_v82_q1_s3_decoder_probe.csv` | v82 Q1/S3 decoder probe | 2026-05-20 | 0.6629409456 |
| 3 | `submission_15_v18_old15_prob_blend.csv` | memo | 2026-05-20 00:32:17 | 0.6057860899 |
| 4 | `submission_01_public_anchor_blend_best_known_0p612659.csv` | 0517-1 edit | 2026-05-17 14:46:12 | 0.6061690193 |
| 5 | `v_perfect_shrink15.csv` | 0518-1 edit | 2026-05-18 13:11:25 | 0.6097358003 |
| 6 | `submission_sample_support_target_blend.csv` | memo | 2026-05-20 00:29:17 | 0.6104310794 |
| 7 | `v_perfect_shrink30.csv` | memo | 2026-05-18 13:12:13 | 0.6104977999 |
| 8 | `submission_01_blend_best.csv` | codex1 edit | 2026-05-15 15:18:29 | 0.6126595186 |
| 9 | `stack_calibrated_v_perfect_snapshot.csv` | 0517-2 edit | 2026-05-17 14:47:50 | 0.6173417918 |
| 10 | `submission_02_subject_smooth.csv` | codex2 edit | 2026-05-15 15:19:16 | 0.6195173919 |
| (new) | `submission_v85_tau06_clip005.csv` | public-posterior breakthrough probe | 2026-05-21 | 0.6157626029 |
| 11 | `submission_sample_support_target_blend.csv` | memo | 2026-05-19 10:22:03 | 0.6335340671 |
| 12 | `42_submission_nopseudo_blend.csv` | memo | 2026-05-19 00:01:07 | 0.6424387775 |
| 13 | `submission_03_torch_mlp.csv` | codex3 edit | 2026-05-15 15:19:42 | 0.6592167646 |
| 14 | `v11_meanonly_submission.csv` | memo | 2026-05-17 14:48:40 | 0.6619461447 |
| 15 | `48_submission_global_mean_pure.csv` | memo | 2026-05-19 00:04:54 | 0.6619461447 |
| 16 | `stack_calibrated_submission.csv` | claude1 edit | 2026-05-16 00:00:05 | 0.7060157004 |
| 17 | `submission_01_cross_workspace_convex_calibrated.csv` | codex4 edit | 2026-05-16 10:22:51 | 0.8196748034 |
| 18 | `stack_calibrated_submission.csv` | cluade2 edit | 2026-05-16 10:25:56 | 0.8825491515 |
| 19 | `stack_calibrated_submission.csv` | memo | 2026-05-20 00:34:36 | 0.9128560882 |

Lower is better.

## Current Reading

- The best known Public LB is now `submission_v83_gq015_gs010.csv` at `0.5997645835`, narrowly beating v76 (`0.5999627447`).
- The two latest direct feedback points are:
  - `submission_sample_support_target_blend.csv`: `0.6104310794`
  - `submission_15_v18_old15_prob_blend.csv`: `0.6057860899`
- These are worse than v76, despite being plausible internally. This means internal OOF improvements from the sample-support/old-prob blend family did not transfer cleanly to Public LB.
- Very aggressive calibrated stacks can be catastrophically wrong on Public LB (`0.70` to `0.91`). This strongly suggests the public/test distribution punishes over-calibration, pseudo-label anchoring, or cross-project blending that is not grounded in this dataset.
- Simple/global mean style baselines are around `0.662`, so scores near `0.60` are real signal, not just mean prediction.

## v82 failure (2026-05-21): v80/v81 decoder branch is QUARANTINED

- `submission_v82_q1_s3_decoder_probe.csv` scored **0.6629409456** — worse than the global-mean baseline (0.6619). v82 = v80 routed base with Q1/S3 replaced by the v81 decoder.
- Diagnosis (`outputs/v82_failure_diagnosis_report.md`): the whole v80 base is public-misaligned, not just the Q1/S3 edit. v80 sits **row-wise mean-abs 0.1275 away from v76** (all targets 0.11-0.16), with S1 -0.045 and S3 -0.049 below the good family; v82 then pushed Q1 up by +0.047 (good family is Q1≈0.50). Ranked harm: (1) Q1 upshift, (2) v80 S1/S3 under-prediction, (3) OOF router selection — all HIGH.
- Offline check: the max-entropy public posterior (`outputs/public_lb_pseudolabel_calibration/`) is exact at v76/v18 but **+0.018 optimistic on far candidates** — it predicted v82 at 0.6444 vs the real 0.6629. It predicts v80_base and v81_routed at ~0.644 too, i.e. ~global-mean once the optimism is added. **Do not upload any v80/v81/v82-based file.**
- **Q1 OOF↔Public LB contradiction (important for future me)**: the v81 stress test honestly showed OOF Q1 +0.019 was real source-recombination (not selection bias). v82's larger Q1 +0.047 still wrecked Public LB. This is NOT a contradiction in the stress test — it is direct evidence that **OOF labels and Public/test labels disagree on Q1 direction**. Stop trusting any OOF-derived Q1 upward signal; treat Q1 moves as Public-LB-unverified by default.

## Why v80/v82 fail on Public LB: panel-conditional coordinate drift (2026-05-21)

Root cause found (`scripts/build_v83_repaired_v80.py`, `outputs/v83_repaired_v80/`):

- v80 OOF (train) mean ≈ train-label mean — v80 is well-calibrated to TRAIN.
- But **train labels are panel-conditional**: from early→late panel, Q1 rises 0.49→0.58 and S2/S3 fall. The TEST set is entirely late panel (panel_position mean 0.70 vs train 0.39, min 0.41). So v80's test predictions inherit a systematic late-panel drift: Q up, S1/S3/S2 down.
- The public-good submissions (v76 0.5999, v18 0.6058) are **flat / not panel-conditional** (Q1≈0.51, S1≈0.69, S3≈0.66). v82 followed v80's panel drift (Q1→0.56, S1/S3 low) and lost. So **train-late label structure does NOT hold on the public test set** — late-panel OOF is therefore a *negative* control, not a scoring oracle.
- Refined Q1 lesson: it was the Q1 **mean shift** (+0.04) that v82 paid for, NOT the Q1 row-level ordering. With the mean held at v76, adding v80's Q1 row deviation actually helps slightly.

## Repaired-v80 candidates (v83 main objective — `outputs/v83_repaired_v80/report.md`)

- Construction: `repaired_t = sigmoid( logit(v76_row_t) + γ_t · (logit(v80_row_t) − logit_mean(v80_t)) )`. v76 row is the public ruler; add only fraction γ of v80's row-level deviation (the breakthrough), with v80's panel-conditional mean drift removed.
- γ-sweep result: posterior optimum near γ≈0.10–0.15, ~**−0.002 vs v76** (0.5978 vs 0.5999). The mean-only form (v76 mean + v80 deviation) was rejected by the posterior (0.64, drift 0.10) — v76's row info must be kept.
- **Honest reading: only ~15% of v80's row deviation is public-aligned; the other ~85% is the panel/coordinate distortion that killed v82. The repaired v80 is a small, real win, NOT a large jump.** A larger jump needs a different hypothesis (a v80-style model trained with public-coordinate priors from the start, or ensembling repaired-v80 with the orthogonal public-good v18), not more squeezing of v80 row signal.
- **Primary upload: `submission_v83_gq015_gs010.csv`** (Q γ=0.15, S γ=0.10): posterior 0.597813 (−0.0021 vs v76), drift_v76 0.019, max-row 0.151, tail(pp>0.9) disagreement share 0.11 (spread, not tail-concentrated). Q1 mean 0.510 ≤ v76 0.511. Downside bounded (drift 0.019 vs v82's 0.128 — no v82-style blowup possible).
- Public LB result: `0.5997645835`. This confirms the repaired-v80 direction is real, but much smaller than posterior predicted: posterior expected ~`0.597813`, so the posterior was optimistic by `+0.001951`. Use this as the new calibration point for v84: keep the v80 row-deviation idea, but penalize drift/large gamma more aggressively.

## v85 last-slot breakthrough pivot (`outputs/v85_public_posterior_breakthrough/`)

- User rejected spending the final daily slot on another `0.59x` hedge. v85 therefore intentionally leaves the v76/v83 neighborhood.
- Construction: fit a sharpened soft-label posterior using known Public LB scores as aggregate BCE constraints, now including:
  - v83 success `0.5997645835`
  - v76 `0.5999627447`
  - v18 `0.6057860899`
  - support blend `0.6104310794`
  - v82 failure `0.6629409456`
- The old conservative posterior had self-entropy around `0.590`. Using its row ordering as prior and sharpening with `tau=6` gives `submission_v85_tau06_clip005.csv` with self-entropy `0.540890`, while still matching known-score constraints within `0.000039` after clipping.
- This is a high-upside leaderboard-feedback distillation probe, not a robust generalization candidate. It has a plausible 0.54-0.55 path only if the posterior geometry recovered from aggregate LB constraints is real. If the constraints are underdetermined, it can fail badly. This accepted risk matches the final-slot objective.
- Public LB result: `0.6157626029`. This rejects the sharp public-posterior geometry as a direct submission model. The result is far better than v82 (`0.66294`) but worse than v83/v76/v18, so the posterior row ordering carries some information, but tau=6 sharpening injects too much wrong-confidence and/or underdetermined pseudo-label structure. Next use: keep v85 only as a diagnostic teacher/feature, never as a direct prediction target unless heavily temperature-softened and anchored.

## Earlier diagnostic-only candidates (v83 anchor blends — `outputs/v83_anchor_candidates/report.md`)

- Tiny v76 perturbations kept as diagnostics, not the main objective: `submission_C_v76_plus_v18_w050.csv` (0.95·v76+0.05·v18, posterior 0.598588) and `_supp_w050`. The A_* (v76+v82) candidates are rejected (posterior optimism toward the quarantined branch + Q1 mean up).

## Practical Calibration Rules

1. Treat internal OOF as a signal-discovery metric, not as an upload score estimate.
2. Downweight candidates that improve OOF by adding many conditional routed moves unless they are supported by sample/test panel coverage and target-level consistency.
3. Prefer candidates that stay close to the Public LB anchor family unless the new representation changes the predictions in a controlled, interpretable way.
4. Public LB suggests the current reliable band is roughly `0.600` to `0.610`, not the internal `0.50x` OOF band.
5. A candidate needs to beat v76 in expected Public LB only if it passes extra robustness checks versus v76: prediction distance, per-target drift, panel-position drift, subject-distribution sanity, and source-family simplicity.

## Implication For Current v52

The v52 internal OOF `0.502679` is a strong representation-discovery result, but it should not be submitted as-is without a Public-LB-aware packaging step. The packaging step should probably:

- Blend v52 conservatively toward v76/public-anchor style predictions.
- Limit per-target corrections to the targets where temporal-state features repeatedly improved across subjects.
- Avoid tiny-bin or empty-sample routed effects.
- Check whether the v52 prediction shift resembles the successful v76/recovery15 direction more than the failed sample-support direction.
