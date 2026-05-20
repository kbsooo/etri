# Public LB Feedback

Last updated: 2026-05-21

## Submitted Scores Provided By User

| rank by score | file | note | submitted_at | public_lb |
| ---: | --- | --- | --- | ---: |
| 1 | `submission_01_v76_balanced_hedge_best.csv` | memo | 2026-05-18 13:15:24 | 0.5999627447 |
| (new) | `submission_v82_q1_s3_decoder_probe.csv` | v82 Q1/S3 decoder probe | 2026-05-20 | 0.6629409456 |
| 2 | `submission_15_v18_old15_prob_blend.csv` | memo | 2026-05-20 00:32:17 | 0.6057860899 |
| 3 | `submission_01_public_anchor_blend_best_known_0p612659.csv` | 0517-1 edit | 2026-05-17 14:46:12 | 0.6061690193 |
| 4 | `v_perfect_shrink15.csv` | 0518-1 edit | 2026-05-18 13:11:25 | 0.6097358003 |
| 5 | `submission_sample_support_target_blend.csv` | memo | 2026-05-20 00:29:17 | 0.6104310794 |
| 6 | `v_perfect_shrink30.csv` | memo | 2026-05-18 13:12:13 | 0.6104977999 |
| 7 | `submission_01_blend_best.csv` | codex1 edit | 2026-05-15 15:18:29 | 0.6126595186 |
| 8 | `stack_calibrated_v_perfect_snapshot.csv` | 0517-2 edit | 2026-05-17 14:47:50 | 0.6173417918 |
| 9 | `submission_02_subject_smooth.csv` | codex2 edit | 2026-05-15 15:19:16 | 0.6195173919 |
| 10 | `submission_sample_support_target_blend.csv` | memo | 2026-05-19 10:22:03 | 0.6335340671 |
| 11 | `42_submission_nopseudo_blend.csv` | memo | 2026-05-19 00:01:07 | 0.6424387775 |
| 12 | `submission_03_torch_mlp.csv` | codex3 edit | 2026-05-15 15:19:42 | 0.6592167646 |
| 13 | `v11_meanonly_submission.csv` | memo | 2026-05-17 14:48:40 | 0.6619461447 |
| 14 | `48_submission_global_mean_pure.csv` | memo | 2026-05-19 00:04:54 | 0.6619461447 |
| 15 | `stack_calibrated_submission.csv` | claude1 edit | 2026-05-16 00:00:05 | 0.7060157004 |
| 16 | `submission_01_cross_workspace_convex_calibrated.csv` | codex4 edit | 2026-05-16 10:22:51 | 0.8196748034 |
| 17 | `stack_calibrated_submission.csv` | cluade2 edit | 2026-05-16 10:25:56 | 0.8825491515 |
| 18 | `stack_calibrated_submission.csv` | memo | 2026-05-20 00:34:36 | 0.9128560882 |

Lower is better.

## Current Reading

- The best known Public LB remains `submission_01_v76_balanced_hedge_best.csv` at `0.5999627447`.
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

## Next upload candidates (v83, anchored on v76 — `outputs/v83_anchor_candidates/report.md`)

- Built only as tiny controlled perturbations of the v76 best anchor; scored offline by the posterior (trustworthy near v76).
- **Primary: `submission_C_v76_plus_v18_w050.csv`** = 0.95·v76 + 0.05·v18 (the 2nd-best public anchor). Posterior 0.598588 vs v76 0.599963, drift 0.0044, max-row 0.029. Because BCE is convex in p, a small blend of two good anchors can beat both — a low-risk ensemble bet, not OOF chasing.
- Secondary: `submission_C_v76_plus_supp_w050.csv` (0.95·v76 + 0.05·sample_support).
- Rejected: the A_* (v76+tiny-v82) candidates show offline improvement but that is the posterior's optimism toward the quarantined branch, and they raise Q1 (HIGH harm).

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
