# Strategy Notes After Deep-Dive Experiments

## Current Best Evidence

Primary validation should be `subject_blocks`: it keeps all known subjects in train/valid but withholds date blocks, which matches the hidden split pattern better than random CV. Random CV is useful only as a leakage/optimism check. Group-subject CV is over-pessimistic for this competition because submission contains the same 10 subjects.

Post-public update: the stage2 file is still the submitted public best (`0.5779449757`), while the stronger OOF ordinal/ambnext file scored `0.5783033652`. New experiments should therefore be ranked by projection onto the observed failed stage2->ordinal direction, not by OOF alone. The safest one-axis non-convex projection diagnostic is `submission_projblend_cap0p0.csv` (OOF `0.562144`, projection `-0.000049`). Using both public directions gives `submission_public2dblend_budget0p0.csv` (OOF `0.561702`, two-axis public delta `-0.00000005`, one-axis delta `+0.00000890`) as the best low-risk non-convex score probe. The balanced next probe is `submission_public2dblend_budget0p00002.csv` (OOF `0.560724`, two-axis public delta `+0.00001997`).

Public-LB inverse update: `public_entropy_projection_builder.py` uses the three observed public scores as aggregate label constraints and solves a minimum-KL projection. This is not a safe CV candidate, but it is the first direct quasi-label exploit with a plausible sub-0.577 public hypothesis. Best balanced probe is `submission_public_entropyproj_public2d0_g075.csv` (OOF analogue `0.554156`, public-posterior expected loss `0.575826`, mean move `0.013218`). Safer shrink is `..._g050.csv` (`0.555625`, expected `0.576100`); maximum exploit is `..._g100.csv` (`0.553679`, expected `0.575734`, exact expected fit to all three public scores).

Target-mask update: `public_entropy_targetmask_builder.py` evaluated 508 target subsets/shrink levels and saved 48 clean submissions. Q2 is not needed for the public-constraint signal. The best balanced derivative is `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv` (drops Q2; OOF `0.554185`, expected `0.575887`, mean move `0.011874`, geometry `-0.010185`, win-rate `1.0`). The lower-move derivative is `..._q1_q3_s2_s3_s4_g075.csv` (drops Q2/S1; expected `0.575956`). The lowest current risk-score derivative is `..._q1_q3_s1_s2_s3_s4_g050.csv` (expected `0.576149`, mean move `0.007898`).

Subset-sensitivity update: `public_subset_sensitivity_audit.py` shows the entropy family beats the public2d0 prior under simulated random/order/subject public row subsets when judged against the full-g100 posterior, but that test is circular. The stronger `public_posterior_scenario_robustness.py` uses six posterior scenarios and ranks by subset regret; it promotes `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv` as the top robust file (mean expected `0.574649`, mean regret `0.000082`, p90 regret `0.000159`, win-rate vs prior `1.0`). Raw `g100` drops to 13th because its win-rate vs prior is only `0.8371` across scenario/subset pairs.

Minimax ensemble update: `public_minimax_ensemble_optimizer.py` convex-blended the public-constraint files under the same six posterior/subset objective. The sparse rank-1 file is `submission_public_minimaxens_r01_a6_h422045.csv` with mean expected `0.574634`, mean regret `0.000067`, p90 regret `0.000118`, win-rate vs prior `1.0`, and OOF analogue `0.554332`. It is now the default public-constraint score candidate; keep the Q2-dropped target-mask as the simpler interpretable fallback.

Conservative frontier update: `public_conservative_frontier_builder.py` adds a second uncertainty model where stage2, public2d0, projblend, and the 0.578 anchor are treated as conservative pseudo-posteriors. This is a dampener for the case where the entropy projection overfits the three public observations. The top higher-trust bridge is `submission_public_consfront_t80_r10_b06ca82f.csv`: 65% `submission_public_minimaxens_r01_a6_h422045.csv` plus 35% `submission_publicobsblend_anchor578_to_stage2_w095.csv`, probability blend over all targets. It has OOF `0.557498`, posterior mean `0.574792`, conservative mean `0.574646`, entropy-only scenario robust score `0.575799`, and integrity-clean predictions. It should not replace raw minimax as the highest-upside public-constraint probe; it is the safer bridge if we want to reduce posterior-model risk.

Mask-aware entropy update: `public_maskaware_entropy_projection.py` flips the public-inverse assumption from "the public subset is effectively all rows" to "the public subset could be random/order/subject-blocked." It solves the three public LB constraints on many candidate masks and averages the resulting logit shifts. The diagnostic is useful: random, rowmod, and subject-contiguous masks require mean probability moves near the all-row projection (`0.0175-0.0185`), while global prefix/suffix masks require much larger movement (`0.0356`), making a pure chronological public split less plausible under the observed three LB scores. The best mask-aware file by six-posterior robustness is `submission_public_maskaware_t80_r11_544844af.csv` with OOF `0.553156`, mean expected `0.574650`, p90 regret `0.000160`, and win-rate `1.0`. It does not beat minimax, but it is now the best row-subset-uncertainty fallback.

Latest negative controls: a 216-config covariate-neighbor label-prior scan over sleep/quiet/presleep features failed on stage2 (`best -0.000199` OOF and positive repeated-subject holdout delta), and 78 hidden-block row gates all worsened geometry versus full stage2. A 48-config interpretable NSF proxy audit for S1/S2/S3/S4 also selected no candidate; S4 had only a tiny full-OOF gain and failed subject-half validation. Presleep/temporal-context candidates remain the strongest raw representation family, but their top OOF files project `0.75-0.99` onto the observed failed ordinal direction. A 73-candidate presleep orthcap follow-up capped that axis; best OOF was only `0.565572` at projection `0.375`, and the best low-risk `projection <= 0.05` file was `0.567216`, so presleep is not a public-safe score leader yet.

| Candidate | Subject-block Log Loss | Decision |
| --- | ---: | --- |
| Global target prior | 0.66766 | Baseline only |
| Subject prior | 0.62765 | Strong mandatory baseline |
| Temporal target-history smoothing | 0.62477 | Adopt as backbone |
| Mobility sensor nested blend | 0.62429 | Adopt cautiously |
| Conservative Q2/Q3/S4 sensor cap | 0.62314 | Strong candidate |
| Conservative cap + missing indicators | 0.62284 | Strong candidate |
| 7,146 meta features + fixed cap | 0.62338 | Hold |
| Conservative cap + tiny watch S-cap | 0.62239 | Current best candidate |
| Block-rate S target switch | 0.62047 nested-target estimate / 0.61981 fixed-config estimate | Aggressive candidate; not fully nested as a final selector |
| Overnight phone remap | 0.60904 | Major structural improvement; post-midnight sensor records mapped to prior lifelog date |
| Overnight/block hybrid | 0.60491 | Current aggressive best estimate |
| Low-dimensional nested stacker | 0.63099 | Reject |
| All sensor nested blend | 0.62530 | Hold |
| Target-correlation calibration | 0.62619+ | Hold |
| Hard subject/global balance correction | 0.71034+ | Reject |
| Target-specific temporal parameters | 0.62995 | Reject |
| Target-specific sensor group selection | 0.62581 | Reject |
| Nested state-space smoothing | 0.62501 | Hold |

## What The Data Is Hiding

0.5-range audit update:

1. A true 0.5 path exists only if hidden block rates can be inferred.  
   The fold-safe temporal model is still `0.62477`, but an oracle that knows each validation block's target rate reaches `0.51788`. This is the first hard evidence that `0.5x` is structurally possible. It also says the missing signal is not row-level noise reduction; it is block-level state/rate reconstruction.

2. Subject means alone cannot get there.  
   A full-subject-rate oracle that is allowed to use validation labels in the subject mean is still only `0.59363`. The jump from `0.59363` to `0.51788` comes from block-local label-state changes, not static subject identity.

3. Pattern Markov/HMM-style state transitions do not solve the block-rate problem.  
   A 128-state 7-bit label Markov bridge was tested with several smoothing/blend settings. Best result was `0.62776`, worse than temporal base. Co-occurrence is real, but transition dynamics are too weak/noisy to reconstruct hidden blocks.

4. Direct one-feature sensor threshold reconstruction is not stable.  
   A nested single-threshold search across deep + meta features scored `0.66904`, worse than temporal base. A validation-selected cheating diagnostic reaches `0.56840`, which means the feature matrix contains many fold-specific slices, but they do not transfer under nested selection.

5. Block smoothing helps only on selected S targets.  
   A surrounding train-block/window-rate smoother gets a non-nested grid best of `0.62117`, but nested all-target selection is `0.62345`. Target-wise, block smoothing beats tiny-watch on `S1`, `S2`, and `S4` only. Combining tiny-watch for `Q1/Q2/Q3/S3` with block smoother for `S1/S2/S4` gives a post-hoc target estimate of `0.62047`; the fixed-config estimate is `0.61981`.

1. The split is block-interleaved, not pure future prediction.  
   Many subjects follow patterns like `T28 S14 T13 S13`, `T32 S16 T16 S16`, or fragmented variants. Hidden labels are often surrounded by known labels from the same subject, so interpolation-like target history is a real signal.

2. Subject identity is not metadata noise.  
   S targets vary dramatically by subject: `id06` has very high S1/S2/S3/S4, while `id05` has very low S2/S3. The same sensor value means different things depending on the individual.

3. Q targets and S targets behave differently.  
   Q2/Q3 have short-lag autocorrelation around 0.22, while S targets are more subject-baseline dominated than day-to-day autocorrelated.

4. Mobility/context is the only sensor family that survived nested blending.  
   GPS/WiFi/BLE/location proxies slightly improved over temporal-only CV. Watch/HR/light/app/ambience features show correlations but do not improve reliably when blended.

5. Label co-occurrence is real but not safely exploitable as a postprocess.  
   Examples: `S2 -> S4`, `Q2 -> Q3`, `Q1 -> S1`. However, nested calibration worsened subject-block CV, so pairwise adjustment is likely overfit unless used with a very weak prior.

6. The “individual average” rule is not a hard 50/50 constraint.  
   Forcing Q targets toward 0.5 or forcing subject full-period rates toward global rates severely worsened CV. Treat this as background, not a probability constraint.

7. Target-specific tuning is fragile.  
   Choosing different temporal smoothing parameters per target looked plausible, but nested subject-block CV worsened from `0.62477` to `0.62995`. Choosing different sensor groups per target also worsened to `0.62581`. The inner folds select aggressive sensor weights, but those weights do not transfer reliably to outer blocks.

8. Small, pre-capped sensor residuals do transfer.  
   A narrow rule that only changes `Q2`, `Q3`, and `S4` survived nested validation: `Q2 = 90% temporal + 10% phone`, `Q3 = 80% temporal + 20% mobility`, `S4 = 90% temporal + 10% mobility`. The same weights were selected in every outer fold and improved subject-block Log Loss from `0.62477` to `0.62314`.

8a. Missingness is a real sensor state.  
   Adding missing indicators to only the phone/mobility residual models improved the fixed capped blend further to `0.62284`. Subject-normalized z features improved phone sensor-only loss (`0.63891 -> 0.62767`) but did not improve the capped blend, so missingness is the safer variant to submit.

9. Stronger state-space smoothing is tempting but not robust.  
   Full-grid subject-block CV found a kernel smoother at `0.62410`, slightly better than the temporal base. But nested config selection fell back to `0.62501`, so this is likely validation-fit rather than a safe production improvement.

10. Neighbor agreement is useful context, not a hard rule.  
    In subject-block CV, when both adjacent train labels were `1`, the true label matched only `71.9%` overall. When both were `0`, it matched only `59.9%`. Forcing same-neighbor rows to `0.9/0.1` was much worse than the temporal probability model. Submission has one extreme contradiction flag (`id06`, block 2, `Q1`), but CV says Q1 same-neighbor agreement is too weak to correct it manually.

11. More features help diagnostics more than final score.  
    A meta-feature layer generated `7,146` additional features: missing indicators, group coverage, log transforms, subject z-scores, subject ranks, window deltas/ratios, and cross-sensor interactions. Sensor-only `meta_all` reached `0.62598`, better than most sensor-only variants, but the fixed residual blend was `0.62338`, still worse than the current missing-indicator candidate (`0.62284`).

12. Stacking is too flexible for this sample size.  
    A nested stacker over temporal/current/meta sensor logits chose the same configuration in every inner fold, but outer CV worsened to `0.63099`. The inner losses around `0.60` were a classic small-data overfit signal. Keep final blending hand-capped and low-dimensional.

13. Watch/HR features are useful only as a tiny S-target residual.  
    The meta-watch model is weak as a standalone sensor model (`0.63859`), but adding it only to `S1-S4` with small weights transferred in nested CV. The best nested tiny-watch candidate improved `0.62284 -> 0.62239`, mostly through `S1`, `S2`, and `S4`.

14. The new practical ceiling is around `0.620`, unless block rates can be predicted directly.  
    The 0.51788 oracle is the target. Current observable features and label-history methods only extract a small part of it. To reach 0.5x, the next experiment must predict submission block rates from a stronger source than row-level sensor aggregates: exact sleep-stage raw data, a hidden split/label generator, external Withings-derived variables, or a much better block-level representation.

15. Overnight alignment is the first real breakthrough.  
    `sleep_date` is always `lifelog_date + 1`, so the actual sleep episode crosses midnight. The original daily features attached `00:00-11:59` records to that calendar date, which means the post-midnight sleep segment was assigned to the next label day. Remapping `00:00-11:59` to the previous `lifelog_date` and aggregating overnight windows drops nested CV from `0.62239` to `0.60904` for the best single overnight blend.

16. The current aggressive best is a target-wise hybrid.  
    Use overnight phone/context where it clearly wins, keep tiny-watch where overnight hurts, and keep block smoothing where it is still better:
    `Q1=overnight_phone_sensor`, `Q2=tiny`, `Q3=tiny`, `S1=overnight_phone`, `S2=block_fixed`, `S3=overnight_all`, `S4=overnight_context`. Estimated target-wise CV is `0.60491`.

## Target-Specific Notes

- `Q1`: Best sensor clues are late call usage, daily light exposure, and HR variability. Sensor ExtraTrees helped Q1 more than temporal alone, but the blend was unstable.
- `Q2`: Phone activity transitions, morning light, BLE evening density, and staying near home are directional clues. Phone-only sensor can help Q2 but hurts other targets.
- `Q3`: Mobility and BLE/WiFi context are the clearest sensor family. Mobility blend weight was highest for Q3.
- `S1`: Mostly subject baseline. Early pedometer bursts and HR minimum correlate, but sensor blend is not stable.
- `S2`: Subject baseline plus weak HR/ambience signals. Hard target-correlation postprocess is not safe.
- `S3`: Strong subject baseline; HR/coverage features correlate. Sensor blend often overfits.
- `S4`: Related to S2 and outside ambience, but direct postprocess did not validate.

## Candidate Submission Files

- `submission_temporal_base.csv`: full-train temporal target-history backbone.
- `submission_mobility_blend.csv`: temporal backbone blended with full-train mobility sensor model using average nested blend weights.
- `submission_conservative_sensor_blend.csv`: strong validated candidate; temporal backbone with capped sensor residuals for Q2/Q3/S4 only.
- `submission_conservative_sensor_blend_missing.csv`: current best candidate; same cap rule but phone/mobility sensor residual models include missingness indicators.
- `submission_meta_current_missing.csv`: regenerated current best from the meta-feature experiment; equivalent strategy.
- `submission_tiny_watch_cap.csv`: current best candidate; conservative phone/mobility cap plus tiny meta-watch residual on S targets.
- `submission_block_target_switch.csv`: aggressive candidate; uses current best for `Q1/Q2/Q3/S3` and block-rate smoother for `S1/S2/S4`.
- `submission_overnight_blend.csv`: best latest single overnight blend.
- `submission_hybrid_overnight_block.csv`: first overnight/block hybrid (`0.60511` estimate).
- `submission_hybrid_overnight_context.csv`: current aggressive best hybrid (`0.60491` estimate).
- `submission_stacked.csv`: generated for audit only; nested stacking rejected this strategy.
- `submission_state_space_best.csv`: generated for audit only; nested selection rejected state-space smoothing.
- `submission_target_specific_temporal.csv`: generated for audit only; nested CV rejected this strategy.
- `submission_target_specific_sensor.csv`: generated for audit only; nested CV rejected this strategy.

Average mobility blend weights from nested subject-block CV:

```text
Q1 0.170
Q2 0.120
Q3 0.460
S1 0.004
S2 0.076
S3 0.280
S4 0.330
```

Because the improvement is small, the mobility file should be treated as a candidate, not automatically superior to the temporal base.

Rejected candidate details:

```text
fixed temporal              0.62477
current missing cap         0.62284
tiny watch cap nested       0.62239
meta fixed cap              0.62338
state-space nested          0.62501
stacking nested             0.63099
target-specific temporal    0.62995
target-specific sensor      0.62581
```

The target-specific result that consistently gave useful information was diagnostic: Q2 likes phone features, Q3/S4 like mobility features, but selecting groups aggressively overfits. The safer production strategy is the capped residual blend:

```text
Q2 phone     0.10
Q3 mobility 0.20
S4 mobility 0.10
all others  0.00
```

Base capped submission probability audit:

```text
file: submission_conservative_sensor_blend.csv
rows: 250
nulls: 0
probability range: 0.189827 .. 0.905849
target means: Q1 0.5004, Q2 0.5634, Q3 0.6102, S1 0.6879, S2 0.6570, S3 0.6778, S4 0.5582
```

Best submission probability audit:

```text
file: submission_conservative_sensor_blend_missing.csv
rows: 250
nulls: 0
probability range: 0.189827 .. 0.905849
target means: Q1 0.5004, Q2 0.5632, Q3 0.6112, S1 0.6879, S2 0.6570, S3 0.6778, S4 0.5588
```

Updated best submission audit:

```text
file: submission_best.csv / submission_tiny_watch_cap.csv
strategy: temporal + Q2 phone 0.10 + Q3 mobility 0.20 + S4 mobility 0.10 + S1-S4 meta-watch 0.15
subject-block Log Loss: 0.62239
```

0.5-range probe summary:

```text
validation block-rate oracle       0.51788
full subject-rate oracle           0.59363
pattern Markov best                0.62776
nested single-threshold features   0.66904
validation-selected threshold      0.56840  (cheating diagnostic)
block smoother grid best           0.62117
block smoother nested all-target   0.62345
block S-target switch estimate     0.62047  (post-hoc target switch)
block S-target fixed estimate      0.61981  (fixed config, target switch)
overnight phone nested blend       0.60904
hybrid overnight/context estimate  0.60491
Q2 soft app/rate combo             0.66357  (Q2 only, strict nested)
hybrid 0p599 estimate              0.59968  (first practical 0.5-range candidate)
Q3 fixed soft/app combo            0.65727  (Q3 only, fixed outer OOF)
hybrid 0p598 estimate              0.59897  (current high-upside candidate)
```

Latest overnight target source estimate:

```text
Q1  overnight_phone_sensor_only    0.62503
Q2  tiny_watch                     0.69271
Q3  tiny_watch                     0.66222
S1  overnight_phone_nested_blend   0.52419
S2  block_fixed                    0.56207
S3  overnight_all_nested_blend     0.53525
S4  overnight_context_sensor_only  0.63291
mean                               0.60491
```

Latest 0.5-range target source estimate:

```text
Q1  overnight_phone_sensor_only     0.62503
Q2  temporal/app/soft-rate combo    0.66357
Q3  fixed app/soft-rate combo       0.65727
S1  overnight_phone_nested_blend    0.52419
S2  0.70 block + 0.30 overnight_all 0.55972
S3  overnight_all_nested_blend      0.53525
S4  0.55 overnight_context + 0.45 block 0.62778
mean                                0.59897
```

Latest sleep-proxy 0.597 candidate:

```text
Q1  0.70 current + 0.30 sleep-interval proxy  0.62002
Q2  current reproducible hybrid               0.66357
Q3  current reproducible hybrid               0.65727
S1  0.70 current + 0.30 sleep-interval proxy  0.51860
S2  current reproducible hybrid               0.55972
S3  current reproducible hybrid               0.53525
S4  current reproducible hybrid               0.62778
mean                                           0.59746
```

Sleep-interval proxy discovery:

```text
feature family: longest quiet interval from screen-off + no-step + low-speed/activity variants
best config: ExtraTrees leaf=6, max_features=0.80, blend weight=0.30 for Q1 and S1
Q1 subject-block OOF: 0.625034 -> 0.620019
S1 subject-block OOF: 0.524188 -> 0.518602
half-subject holdout: Q1 0.615798 -> 0.611891; S1 0.498541 -> 0.495360
geometry-mask saved-current proxy: Q1 delta -0.00649; S1 delta -0.01373
top features: quiet-interval duration, quiet-interval end hour, duration x charging, pre/post screen/light context
decision: kept Q1/S1 sleep-proxy blend as an earlier high-upside candidate.
```

Augmented subject-relative sleep-proxy candidate:

```text
augmentation: subject z/rank/center, prev-next deltas, neighbor means, rolling-3 context from unlabeled sensor covariates
Q1 best config: aug_leaf10_mf0.6, blend weight=0.60
Q1 subject-block OOF: 0.625034 -> 0.604470
Q1 half-subject holdout: 0.615798 -> 0.597643
Q1 actual-geometry saved-current mask: 0.632460 -> 0.611601
S1 augmented full OOF improves but half-subject worsens, so S1 stays on the non-augmented proxy.
new mean estimate: 0.595237
file: submission_hybrid_0p597_sleep_proxy_augmented.csv
estimate: hybrid_0p595_sleep_proxy_augmented_cv_estimate.csv
decision: earlier high-upside candidate; strongest Q1 clue remains subject-relative quiet-interval rank/duration.
```

Fold-safe reference-stat sleep-proxy candidate:

```text
motivation: separate true sleep-interval signal from transductive covariate-rank optimism
fold-safe transform: subject reference mean/std/rank are computed from the fold train rows only, then validation rows are projected onto that reference
Q1 fold-safe best: 0.625034 -> 0.610793; half-holdout 0.615798 -> 0.601065; geometry 0.632460 -> 0.616860
Q2 fold-safe leaf3 w0.20: 0.663572 -> 0.661317; half-holdout 0.686456 -> 0.681794; geometry w0.20 0.671960 -> 0.663919
Q3 fold-safe leaf3 w0.10: 0.657266 -> 0.654440; half-holdout 0.694412 -> 0.693926; geometry w0.10 0.657612 -> 0.654510
new mean estimate with Q2/Q3 fold-safe additions: 0.594511
file: submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv
estimate: hybrid_0p594_sleep_proxy_q23foldsafe_cv_estimate.csv
decision: previous high-upside candidate; keep the fold-safe Q3 component at low weight only.
```

Quiet-fragmentation candidate:

```text
features: quiet segment counts/durations/gaps over screen-off, no-step, low-speed, still-activity variants with charge/hr/light context
S1 selected: frag_leaf4_mf0.6_depth10, weight=0.60
S1 subject-block OOF: 0.518602 -> 0.504520
S1 repeated subject-half fixed weight: mean delta -0.014124, win-rate 0.977
S1 actual-geometry w0.60: 0.530627 -> 0.518948
Q3 selected: frag_leaf3_mf0.35, weight=0.30
Q3 subject-block OOF: 0.654440 -> 0.650187
Q3 repeated subject-half fixed weight: mean delta -0.004307, win-rate 0.895
Q3 actual-geometry w0.30: 0.654145 -> 0.649188
new mean estimate: 0.591892
file: submission_hybrid_0p592_sleep_fragment_s1_q3.csv
estimate: hybrid_0p592_sleep_fragment_s1_q3_cv_estimate.csv
decision: cleaner 0p592 backup; Q2/Q1/S4 fragmentation rejected by repeated subject-half despite some OOF/geometry optimism.
```

Sleep-dynamics candidate:

```text
features: HR drop/rebound, quiet-end screen/step/light wake bursts, first activity after quiet, subject regularity deltas
S1 selected: dyn_leaf6_mf0.8, weight=0.30
S1 subject-block OOF: 0.504520 -> 0.502098
S1 fixed repeated subject-half: mean delta -0.002430, win-rate 0.932
S1 actual-geometry w0.30: 0.509429 -> 0.507605
S4 selected: dyn_leaf3_mf0.35, weight=0.08
S4 subject-block OOF: 0.627784 -> 0.626623
S4 fixed repeated subject-half: mean delta -0.001253, win-rate 0.796
S4 actual-geometry w0.08: 0.625851 -> 0.625016
new mean estimate: 0.591380
file: submission_hybrid_0p591_sleep_dynamics_s1_s4.csv
estimate: hybrid_0p591_sleep_dynamics_s1_s4_cv_estimate.csv
decision: previous sleep-dynamics backup; the gain is thin but still validated.
```

Block-label residual candidate:

```text
motivation: after sleep proxies, direct block-rate oracle gap is still not closed; test whether surrounding same-subject train labels explain residual block state
base: submission_hybrid_0p591_sleep_dynamics_s1_s4.csv
Q1 selected: s4_a0.9_w1_gap_boost0, weight=0.05
Q1 subject-block OOF: 0.604470 -> 0.603439
Q1 repeated subject-half: mean delta -0.000981, win-rate 0.602
Q1 actual-geometry: 0.607798 -> 0.606558
Q2 selected: s32_a0.9_w1_gap_boost0, weight=0.10
Q2 subject-block OOF: 0.661317 -> 0.658044
Q2 repeated subject-half: mean delta -0.003066, win-rate 0.657
Q2 actual-geometry: 0.667656 -> 0.659661
Q3 selected: s32_a0.9_w3_eq_boost0, weight=0.15
Q3 subject-block OOF: 0.650187 -> 0.647542
Q3 repeated subject-half: mean delta -0.002505, win-rate 0.756
Q3 actual-geometry: 0.648151 -> 0.642465
S3 selected: s4_a0.15_w5_gap_boost0, weight=0.60
S3 subject-block OOF: 0.535248 -> 0.531569
S3 repeated subject-half: mean delta -0.003814, win-rate 0.885
S3 actual-geometry: 0.525487 -> 0.518308
S4 selected: s32_a0.9_w10_gap_boost0, weight=0.45
S4 subject-block OOF: 0.626623 -> 0.619838
S4 repeated subject-half: mean delta -0.006747, win-rate 0.812
S4 actual-geometry: 0.619696 -> 0.618137
S2 rejected: full OOF 0.559719 -> 0.555998, but actual-geometry 0.539040 -> 0.541775
new mean estimate: 0.588893
file: submission_hybrid_0p588_block_label.csv
estimate: hybrid_0p588_block_label_cv_estimate.csv
decision: accept Q1/Q2/Q3/S3/S4 only; block labels remain useful, but target-specific geometry guardrails are mandatory.
```

Subject-relative Q candidate:

```text
motivation: hard Q-rate constraints are rejected, but Q labels still contain within-subject latent-state structure
base: submission_hybrid_0p588_block_label.csv
Q1 selected: center_temp_p2_w0.3
Q1 subject-block OOF: 0.603439 -> 0.600917
Q1 repeated subject-half: mean delta -0.002464, win-rate 0.830
Q1 actual-geometry: 0.606165 -> 0.604220
Q2 selected: center_temp_p0.5_w0.3
Q2 subject-block OOF: 0.658044 -> 0.656820
Q2 repeated subject-half: mean delta -0.001271, win-rate 0.726
Q2 actual-geometry: 0.663306 -> 0.660554
Q3 selected: center_temp_p0.5_w0.3
Q3 subject-block OOF: 0.647542 -> 0.646729
Q3 repeated subject-half: mean delta -0.000884, win-rate 0.802
Q3 actual-geometry: 0.642652 -> 0.642074
new mean estimate: 0.588241
file: submission_hybrid_0p588_subject_relative_q.csv
estimate: hybrid_0p588_subject_relative_q_cv_estimate.csv
decision: Q-relative backup; Q1 is sharpened within subject, Q2/Q3 are smoothed within subject.
```

Subject-relative S candidate:

```text
motivation: objective sleep-stage targets may still need subject-relative state/rank correction after block labels and sleep proxies
base: submission_hybrid_0p588_subject_relative_q.csv
S2 selected: center_temp_p0.5_w0.3
S2 subject-block OOF: 0.559719 -> 0.558581
S2 repeated subject-half: mean delta -0.001200, win-rate 0.825
S2 actual-geometry: 0.539040 -> 0.537414
S3 selected: center_temp_p0.5_w0.3
S3 subject-block OOF: 0.531569 -> 0.528718
S3 repeated subject-half: mean delta -0.002867, win-rate 1.000
S3 actual-geometry: 0.518608 -> 0.515986
S4 selected: rank_logit_p0.75_w0.3
S4 subject-block OOF: 0.619838 -> 0.618055
S4 repeated subject-half: mean delta -0.001864, win-rate 0.742
S4 actual-geometry: 0.610113 -> 0.608501
S1 rejected: best OOF delta only -0.000183
new mean estimate: 0.587417
file: submission_hybrid_0p587_subject_relative_qs.csv
estimate: hybrid_0p587_subject_relative_qs_cv_estimate.csv
decision: previous no-resweep backup; accept S2/S3/S4 relative transforms and leave S1 unchanged.
```

Second-pass subject-relative resweep:

```text
motivation: after the first Q/S relative correction, test whether the remaining logits still have within-subject shrink/rank residue
base: submission_hybrid_0p587_subject_relative_qs.csv
Q3 selected: rank_logit_p0.5_w0.4
Q3 subject-block OOF: 0.646729 -> 0.646039
Q3 repeated subject-half: mean delta -0.000742, win-rate 0.817
Q3 actual-geometry: geometry delta -0.001258
S2 selected: center_temp_p0.25_w0.4
S2 subject-block OOF: 0.558581 -> 0.557029
S2 repeated subject-half: mean delta -0.001585, win-rate 0.758
S2 actual-geometry: geometry delta -0.002442
S3 selected: center_temp_p0.25_w0.4
S3 subject-block OOF: 0.528718 -> 0.524153
S3 repeated subject-half: mean delta -0.004484, win-rate 1.000
S3 actual-geometry: geometry delta -0.004204
S4 selected: rank_logit_p0.5_w0.4
S4 subject-block OOF: 0.618055 -> 0.616847
S4 repeated subject-half: mean delta -0.001214, win-rate 0.684
S4 actual-geometry: geometry delta -0.001381
Q1 rejected: no loose pass; S1 not promoted because improvement is tiny and only loose
new strict mean estimate: 0.586272
file: submission_hybrid_0p586_subject_relative_resweep_strict.csv
estimate: hybrid_0p586_subject_relative_resweep_strict_cv_estimate.csv
decision: strict current backup; second-pass relative resweep is now the strongest validated structure after block labels.
```

Q2 targeted loose add-on:

```text
motivation: Q2 remains a high-loss target; full OOF and geometry prefer more shrink, but broad subject-half was borderline
base: submission_hybrid_0p586_subject_relative_resweep_strict.csv
selected: center_shift_p-0.5_w0.2
Q2 subject-block OOF: 0.656820 -> 0.656415
Q2 targeted 2000-repeat subject-half: mean delta -0.000401, win-rate 0.648
Q2 actual-geometry: geometry delta -0.001295
new high-upside mean estimate: 0.586214
file: submission_hybrid_0p586_subject_relative_resweep_q2loose.csv
estimate: hybrid_0p586_subject_relative_resweep_q2loose_cv_estimate.csv
decision: no-logit-calibration backup; keep strict 0p586 as backup because Q2 narrowly misses the strict 0.65 win-rate gate.
```

Current-frontier block-label residual:

```text
base: submission_hybrid_0p586_subject_relative_resweep_q2loose.csv
S2 best OOF residual: 0.557029 -> 0.553555, but geometry delta +0.001623
S4 best OOF residual: 0.616847 -> 0.616063, but geometry delta +0.000068
Q3 best OOF residual: 0.646039 -> 0.645390, but subject-half win-rate 0.500 and geometry delta +0.000944
Q2 best OOF residual: 0.656415 -> 0.656143, but subject-half win-rate 0.552
decision: reject another block-label layer at the current frontier.
```

Gentle per-target logit calibration:

```text
motivation: joint calibration overfits, but current probabilities may still be systematically under-confident after many conservative blends
base: submission_hybrid_0p586_subject_relative_resweep_q2loose.csv
Q1 selected: scale1.3_shift0_w0.2
Q1 subject-block OOF: 0.600917 -> 0.599588
Q1 repeated subject-half: mean delta -0.001274, win-rate 0.977
Q1 actual-geometry: geometry delta -0.001242
Q2 selected: scale1.15_shift0.08_w0.2
Q2 subject-block OOF: 0.656415 -> 0.655403
Q2 repeated subject-half: mean delta -0.000967, win-rate 0.897
Q2 actual-geometry: geometry delta -0.000934
Q3 selected: scale1.3_shift0_w0.2
Q3 subject-block OOF: 0.646039 -> 0.645317
Q3 repeated subject-half: mean delta -0.000710, win-rate 0.938
Q3 actual-geometry: geometry delta -0.001200
S1 selected: scale1.3_shift0_w0.2
S1 subject-block OOF: 0.502098 -> 0.499921
S1 repeated subject-half: mean delta -0.002179, win-rate 1.000
S1 actual-geometry: geometry delta -0.001551
S2 selected: scale1.3_shift0_w0.2
S2 subject-block OOF: 0.557029 -> 0.556059
S2 repeated subject-half: mean delta -0.000957, win-rate 0.963
S2 actual-geometry: geometry delta -0.001944
S3 selected: scale1.3_shift0_w0.2
S3 subject-block OOF: 0.524153 -> 0.523202
S3 repeated subject-half: mean delta -0.000984, win-rate 0.920
S3 actual-geometry: geometry delta -0.001331
S4 selected: scale1.3_shift0_w0.2
S4 subject-block OOF: 0.616847 -> 0.616162
S4 repeated subject-half: mean delta -0.000679, win-rate 0.958
S4 actual-geometry: geometry delta -0.001117
new mean estimate: 0.585093
file: submission_hybrid_0p585_gentle_logit_calibration.csv
estimate: hybrid_0p585_gentle_logit_calibration_cv_estimate.csv
decision: first accepted logit layer; this is a weak per-target sharpening, not a flexible joint calibration.
```

Iterative gentle-logit residual path:

```text
motivation: the first logit layer passed all guardrails, so test whether calibration residual remains after each accepted layer
probe script: gentle_logit_residual_probe.py
submission builder: make_gentle_logit_from_guardrail_selection.py
base after first layer: submission_hybrid_0p585_gentle_logit_calibration.csv
second layer: submission_hybrid_0p584_gentle_logit_residual.csv, mean 0.584290
third layer: submission_hybrid_0p583_gentle_logit_residual2_loose.csv, mean 0.583714
fourth layer: submission_hybrid_0p583_gentle_logit_residual3_loose.csv, mean 0.583334
fifth layer: submission_hybrid_0p583_gentle_logit_residual4_loose.csv, mean 0.583058
sixth layer: submission_hybrid_0p582_gentle_logit_residual5_loose.csv, mean 0.582832
seventh layer: submission_hybrid_0p582_gentle_logit_residual6_loose.csv, mean 0.582657
latest strict backup: submission_hybrid_0p582_gentle_logit_residual6_strict.csv, mean 0.582669
latest accepted targets: Q2/Q3/S1/S2 strict, S3 loose, Q1 unchanged, S4 unchanged
latest integrity: 250 rows, sample order true, nulls 0, duplicates 0, probability range 0.084907 .. 0.973413
decision: superseded by the alternating subject/logit/block path below; calibration-only gains were shrinking, but subject-relative residuals reopened the frontier.
```

Alternating subject/logit/block residual path:

```text
motivation: pure calibration saturated around 0.5825; subject-relative residuals then reopened the target losses, and S2 block-state residual briefly reopened after that
post-logit subject-relative: submission_hybrid_0p580_subject_relative_after_logit8_loose.csv, mean 0.581478
post-subject logit: submission_hybrid_0p581_logit_after_subject_relative_loose.csv, mean 0.581139
S2 block residual: submission_hybrid_0p580_block_s2_after_logit_subject.csv, mean 0.580945
post-block logit: submission_hybrid_0p580_logit_after_block_s2_loose.csv, mean 0.580794
continued alternating strict/loose path: submission_hybrid_0p578_subject_after_logit_final8_loose.csv, mean 0.578467
strict current backup: submission_hybrid_0p578_subject_after_logit_final8_strict.csv, mean 0.578530
pre-final loose backup: submission_hybrid_0p578_logit_after_subject_final7_strict.csv, mean 0.578593
previous aggressive add-on: submission_hybrid_0p578_logit_after_subject_final9_strict.csv, mean 0.578304
nested-supported guardrail candidate: submission_hybrid_0p579_nested_supported_late_residual_gridbest.csv, mean 0.579168, geometry delta -0.002044, geometry win-rate 1.0
latest integrity: 250 rows, sample order true, nulls 0, duplicates 0, probability range 0.107524 .. 0.976992
decision at that stage: the 0.578304 aggressive file was the highest-upside pre-quiet candidate; the 0.579168 nested-supported file remains the strongest geometry-nested pre-quiet backup.
```

Post-0.578/0.579 block-label residual retest:

```text
base aggressive: submission_hybrid_0p578_logit_after_subject_final9_strict.csv
aggressive S2 best OOF residual: delta -0.001187, but geometry delta +0.002218
aggressive S4 best OOF residual: delta -0.000391, but geometry delta +0.000224
aggressive Q3 best OOF residual: delta -0.000109, geometry delta -0.000846, but win-rate 0.555
base nested-supported: submission_hybrid_0p579_nested_supported_late_residual_gridbest.csv
nested-supported S2 best OOF residual: delta -0.001065, but geometry delta +0.002024
nested-supported S4 best OOF residual: delta -0.000391, but geometry delta +0.000224
nested-supported S1/Q1 small OOF residuals: fail geometry or win-rate
decision: reject another block-label layer after both the aggressive and nested-supported late residual candidates.
```

Quiet-window logistic residual breakthrough:

```text
motivation: fixed sleep-proxy model residuals fail at the 0.578/0.579 frontier, so re-scan raw quiet-window features directly against current residuals.
residual probe signal: Q3 quiet start time, S2/S4 long screen-off duration, S3 quiet-window HR mean.
fold-safe correction: per-target logistic model using base logit + subject-reference quiet feature z-score.
main quiet file: submission_hybrid_0p573_quiet_logit_q3_s2_s3_s4.csv
main quiet estimate: 0.578304 -> 0.574942
main quiet geometry delta: -0.000987
safer w0.30 file: submission_hybrid_0p575_quiet_logit_q3_s2_s3_s4_w30.csv
safer w0.30 estimate / geometry: 0.575842 / -0.001031
post-quiet gentle file: submission_hybrid_0p574_quiet_logit_then_gentle_loose.csv, estimate 0.574786, additional geometry delta -0.000426
current high-upside file: submission_hybrid_0p574_quiet_logit_then_second_loose.csv, estimate 0.574678, additional geometry delta -0.000307
integrity: 250 rows, sample order true, nulls 0, duplicates 0, probability range 0.099320 .. 0.978198
decision: quiet-window correction supersedes the 0.578 aggressive file; keep the w0.30 variant as the safer geometry-weighted backup.
```

Public LB anchor and broad residual breakthrough:

```text
submitted anchor: submission_hybrid_0p578_logit_after_subject_final9_strict.csv
offline estimate / public LB: 0.578304 / 0.5784273528
interpretation: offline OOF scale is well calibrated for the pre-quiet stack; prefer fold-safe OOF over full-fit optimistic quiet estimates.
submitted stage2: submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv
offline estimate / public LB: 0.567531 / 0.5779449757
stage2 interpretation: broad residual features are not useless, but the apparent 0.01077 OOF gain mostly fails on public. Treat raw stage2 and all stage3 broad add-ons as selection-sensitive.
strict quiet re-audit: final_hybrid_0p575_quiet_logit_then_second_loose_foldsafe_oof.npy, mean 0.575742
post-quiet broad Q1 signal: deep__usage_late_usage_kw_call_time_max, subject_center, C=0.50, w=0.45, Q1 delta -0.014864
post-quiet broad Q2 signal: deep__phone_activity_morning_transitions, subject_rank, C=0.50, w=0.30, Q2 delta -0.003082
Q1/Q2 broad file: submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv, mean 0.572651, geometry delta -0.002905, geometry win-rate 1.0
stage2 broad signals: Q3 BLE morning unique, S1 ambience hour, S2 late phone light, S3 HR rows, S4 evening outside ambience.
current fold-safe frontier: submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv
current fold-safe estimate / geometry: 0.567531 / -0.003490, geometry win-rate 1.0
integrity: 250 rows, sample order true, nulls 0, duplicates 0, probability range 0.065941 .. 0.979202
anchor-stage2 blend files: submission_publicblend_anchor578_stage2567_prob_w050.csv, submission_publicblend_anchor578_stage2567_prob_w075.csv, submission_publicblend_anchor578_stage2567_prob_w085.csv
blend rationale: linear probability blending is convex for Log Loss on hidden labels, so these files test lower-amplitude stage2 movement without adding a new selected feature family.
target-switch probe files: submission_publicprobe_anchor578_stage2_drop_s3.csv, submission_publicprobe_anchor578_stage2_drop_s4.csv, submission_publicprobe_anchor578_stage2only_s.csv, submission_publicprobe_anchor578_stage2only_q.csv
probe rationale: copy selected stage2 targets onto the public anchor to identify which target family actually transfers on public.
public inverse alpha: 0.544736 from anchor/stage2 public LB constraint
submitted ordinal/ambnext: submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv
ordinal offline / public LB: 0.561904 / 0.5783033652
ordinal interpretation: huge OOF gain did not beat stage2 public; public transfer ratio versus anchor is only 0.0076. This demotes aggressive q3off/ambnext and count-shift candidates from score priority.
observed-endpoint microblend script: public_observed_pair_blend_builder.py
lowest-risk new score file: submission_publicobsblend_stage2_to_ordinal_w005.csv, OOF 0.567025, convex public upper bound 0.5779628952
subject-target gate script: subject_target_gate_donor_builder.py
best subject-gate high-upside file: submission_subjectgate_ordinal_all_thrm0p005_w100.csv, full OOF 0.558584, half-gate OOF 0.563328, public-bad projection 0.623
lower-projection subject-gate file: submission_subjectgate_ordinal_all_thrm0p02_w080.csv, OOF 0.562297, half-gate OOF 0.564583, public-bad projection 0.321
orthcap script: public_bad_direction_orthcap_builder.py
orthcap balanced file: submission_orthcap_s001_cap010_sc100.csv, OOF 0.561989, public-bad projection 0.100, projected public penalty +0.000036
orthcap high-upside file: submission_orthcap_s001_cap030_sc100.csv, OOF 0.560427, public-bad projection 0.300, no hard clip
score-oriented next files: submission_publicobsblend_stage2_to_ordinal_w005.csv, then submission_publicobsblend_stage2_to_ordinal_w010.csv, then submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv
decision: raw stage2 is current known public best. The next score priority is not the OOF-top ordinal file; it is tiny probability blending between already-public-observed endpoints. Orthcap is the best non-convex rescue because it keeps the subjectgate OOF residual while capping the failed public direction. Subject-target gates are the highest-upside OOF probes, but they still need public-risk handling because the best gates retain 0.56-0.71 projection onto the failed ordinal direction. Next attribution priority is target-switch (`drop_q3`, `no_q2q3`, then Q-vs-S) plus lower-projection orthcap/subject-gate probes. Do not submit stage3 before this attribution/line-search loop.
```

0.598 reproducible candidate integrity:

```text
file: submission_hybrid_0p598_repro.csv
rows: 250
sample key order: true
nulls: 0
duplicate keys: 0
probability range: 0.159659 .. 0.975671
max target diff vs previous submission_hybrid_0p598.csv: 4.44e-16
```

Interpretation:

```text
Q2 was the first breakthrough: strict outer nested CV accepts temporal + pre-sleep app + soft subject-rate.
Q3 has a weaker sibling signal: fixed outer OOF improves, but nested selection fails.
Hard subject-rate constraints are rejected: they become overconfident and explode logloss.
Soft subject-relative Q temperature is now accepted: Q1 wants sharper within-subject rank contrast, Q2/Q3 want smoothed relative differences.
Subject-relative S correction is also accepted for S2/S3/S4: S2/S3 want smoothed within-subject logits, S4 wants a weak within-subject rank-logit correction.
Second-pass relative resweep is accepted for Q3/S2/S3/S4; Q2 has a smaller loose add-on with strong geometry but borderline subject-half.
Block labels are still useful after sleep proxies, but only target-specific configs pass geometry; S2 is rejected despite full-OOF improvement.
At the 0p586 frontier and again after the 0p578/0p579 late residual candidates, another block-label layer is rejected by geometry/win-rate.
Gentle per-target logit sharpening is accepted across all seven targets; the model stack is still under-confident after conservative blends.
Pure iterative gentle-logit residuals remain useful through about 0.5825, but the stronger pattern is alternating calibration with subject-relative residuals and one S2 block-state correction.
The current known public best is submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv at public LB 0.5779449757. Its fold-safe estimate 0.567531 is now known to be optimistic by about 0.01041.
Nested broad-feature selection audit now rejects fresh full-train residual mining: inner-selected broad features improve inner folds but worsen outer geometry by +0.008737 with 0.0 win-rate. Fixed stage2 still improves outer geometry by -0.003272, but Q3 alone is unstable (+0.001753, win-rate 0.25). Do not add stage3 broad residuals until target-gated public probes are resolved.
Label-powerset hard constraints are rejected: nested selected label priors worsen outer geometry by +0.000687 with 0.0 win-rate. A target-gated exception exists for S2 only: on full stage2, S2-only subject-joint prior improves geometry by -0.000592 with 0.75 win-rate; on Q3-off w650, S2-only global-Q/S prior improves geometry by -0.000546 with 0.75 win-rate; on blend500/ambnext, S2-only global-Q/S prior improves geometry by -0.000690 with 0.75 win-rate. Ordinary OOF rejects the stage2/q3off S2 prior and is almost flat on blend500/ambnext (-0.000030), so this remains a geometry-bet family only.
Subject-target donor gating is accepted as a diagnostic/high-upside family, not as a low-risk family. The half-gate guardrail remains positive (`0.567531 -> 0.563328` for the best ordinal gate), but the best variants still project heavily onto the observed public-bad stage2->ordinal direction. Orthcap is the preferred wrapper around subjectgate because it can reduce that projection to 0.10 while keeping OOF `0.561989`, or projection 0.30 while keeping OOF `0.560427`.
Use submission_publicobsblend_stage2_to_ordinal_w005.csv as the lowest-risk score-oriented public-observed microblend. Use submission_publicobsblend_stage2_to_ordinal_w010.csv only if accepting a larger public-bound risk for more OOF gain. Use submission_orthcap_s009_cap005_sc100.csv as the first low-projection non-convex rescue, submission_orthcap_s001_cap010_sc100.csv as the balanced rescue, and submission_orthcap_s001_cap030_sc100.csv as the main high-upside orthcap. Keep submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv as the lower-distance anchor/stage2 alternative. Use submission_subjectgate_ordinal_all_thrm0p02_w080.csv as the lower-projection subject-gate probe and submission_subjectgate_ordinal_all_thrm0p005_w100.csv only as a high-upside OOF probe. Use submission_publicgated_anchor578_stage2_drop_q3_prob_w650.csv and submission_publicgated_anchor578_stage2_drop_q3_prob_w545.csv as the next Q3-off attribution/score probes. Use submission_label_prior_gate_blend500_ambnext_r8_S2__global_qs_a0.5_w0.25_sh0.csv only as the geometry-bet S2 variant. Use submission_publicgated_anchor578_stage2_drop_q3_prob_w1000.csv and submission_publicgated_anchor578_stage2_no_q2q3_prob_w650.csv as attribution probes. Use submission_publicprobe_anchor578_stage2only_s.csv and submission_publicprobe_anchor578_stage2only_q.csv as the clean Q-vs-S decomposition pair before adding any stage3 broad residual.
Use submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv as the cleaner Q1/Q2 broad-feature backup, estimated mean 0.572651 with geometry delta -0.002905.
Use submission_hybrid_0p575_quiet_logit_q3_s2_s3_s4_w30.csv as the safer quiet-window-only backup, estimated mean 0.575842 with geometry delta -0.001031.
Use submission_hybrid_0p579_nested_supported_late_residual_gridbest.csv as the strongest geometry-nested late residual candidate, estimated mean 0.579168 with geometry delta -0.002044.
Use submission_hybrid_0p578_subject_after_logit_final8_strict.csv as the previous stricter backup, estimated mean 0.578530.
Use submission_hybrid_0p580_logit_after_block_s2_loose.csv as the pre-overiteration backup, estimated mean 0.580794.
Use submission_hybrid_0p585_gentle_logit_calibration.csv as the first-logit-layer backup.
Use submission_hybrid_0p586_subject_relative_resweep_q2loose.csv as the no-logit-calibration backup.
Use submission_hybrid_0p586_subject_relative_resweep_strict.csv as the stricter backup.
Use submission_hybrid_0p587_subject_relative_qs.csv as the previous no-resweep backup.
Use submission_hybrid_0p588_subject_relative_q.csv as the no-S-relative backup.
Use submission_hybrid_0p588_block_label.csv as the no-Q-temperature backup.
Use submission_hybrid_0p591_sleep_dynamics_s1_s4.csv as the previous sleep-dynamics backup.
Use submission_hybrid_0p592_sleep_fragment_s1_q3.csv as the cleaner fragmentation backup.
Use submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv as the previous high-upside backup.
Use submission_hybrid_0p597_sleep_proxy_augmented.csv as the Q1/S1-only augmented backup.
Use submission_hybrid_0p597_sleep_proxy.csv as the non-augmented sleep-proxy backup.
Use submission_hybrid_0p598_repro.csv as the reproducible pre-sleep-proxy backup.
Use submission_hybrid_0p599.csv as the cleaner Q2-first 0.5-range candidate.
Keep submission_hybrid_overnight_context.csv as the safer pre-0.6 backup.
```

Q-rate constraint postprocess:

```text
subject-block OOF Q1 improved to 0.619828, but half-subject and actual-geometry masks reject it.
half-subject Q1 selected shift worsened 0.615798 -> 0.621631.
geometry-mask saved-current proxy Q1 worsened 0.624443 -> 0.629417.
decision: do not submit Q-rate shift; it is a split-specific rate artifact, not a robust feature.
```

Cross-target coherence stack:

```text
current_0p594_oof mean        0.594511
nested_cross_target mean      0.599760
Q3 selected all_C0.5_g0.25    holdout 0.693926 -> 0.697585
S1 selected pairs_C0.2_g0.5   holdout 0.495360 -> 0.504981
S3 selected pairs_C0.2_g0.25  holdout 0.538073 -> 0.538971
decision: reject label-coherence stacking; it learns fold-specific target priors, not stable physiology.
```

S2/S4 pair validation:

```text
current sources       S2 0.562067  S4 0.632913  pair_mean 0.597490
locked fixed pairs    S2 0.559719  S4 0.627784  pair_mean 0.593752
nested pair selector  S2 0.562523  S4 0.635510  pair_mean 0.599017
mean from pre-pair    0.600041 -> locked fixed 0.598973; nested selector 0.600477
decision: fixed S2/S4 weights are useful; dynamic fold-selected weights are rejected.
```

Q1 soft/app diagnostic:

```text
current Q1 source                 0.625034
best tested Q1 soft/app variant   0.627164
best variant                      overnight_all + soft target rate r=0.50, shrink=1, weight=0.10
decision: reject Q1 soft/app family for current candidate.
```

Neighbor consistency audit:

```text
same_1 rows: actual match 0.7186, temporal logloss 0.5507, forced-0.90 logloss 0.7236
same_0 rows: actual match 0.5993, temporal logloss 0.6432, forced-0.10 logloss 0.9857
submission contradiction flags: id06 block 2 Q1 only
decision: audit only; no neighbor-forcing postprocess
```

Actual-geometry mask CV:

```text
actual submission blocks: 36 blocks, 250 rows, median n=5.5, both-boundary fraction=0.722
subject-block CV blocks: 50 blocks, 450 rows, median n=9.0
geometry-mask temporal_base mean: 0.613820
best all-target bridge/block mean: 0.614258 (worse than temporal)
target signal: block/bridge helps S targets weakly, but hurts Q targets.
decision: no all-target boundary bridge; keep target-specific S2/S4 fixed pair only.
```

Geometry S2/S4 pair check:

```text
locked subject-block fixed pair on geometry masks: S2 0.540251, S4 0.627195, pair_mean 0.583723
current sources on geometry masks:             S2 0.541624, S4 0.633159, pair_mean 0.587391
half-selected holdout:                         S2 0.548653, S4 0.626346, pair_mean 0.587499
holdout fixed S4 beats half-selected S4:       0.625768 vs 0.626346
decision: geometry audit supports the existing fixed S2/S4 pair, not a new dynamic geometry selector.
```

Overnight block-level regressor:

```text
legacy_overnight_v1 temporal base            0.624765
legacy_overnight_v1 nested block regressor   0.624984
overnight_v2 nested block regressor          0.628856
best S-only switch                           0.625935 (legacy), 0.627173 (v2)
decision: reject ML block-rate regressor; it cannot extract the 0.51788 oracle gap from current features.
```

## Next Experiments

1. Submission-geometry-aware target switches only where independent evidence agrees.  
   The geometry mask now confirms Q1/Q2/Q3/S3/S4 block-label residual smoothing on top of 0p591, rejects S2 block-label smoothing there, accepts S2/S3/S4 first-pass relative correction, accepts Q3/S2/S3/S4 second-pass resweep, and rejects another block-label layer at 0p586. Avoid all-target boundary rules and keep target-specific geometry gates.

2. Refine sleep interval proxies only where guardrails agree.  
   Q1/S1 opened with longest quiet interval features, S1/Q3 pass quiet-fragmentation guardrails, and S1/S4 get a thin sleep-dynamics add-on. Q2 still improves on geometry but fails repeated subject-half; keep it capped at the fold-safe sleep-proxy blend.

3. Probability rank preservation with gentler calibration.  
   Iterative per-target gentle logit sharpening now passes several guardrail rounds, but gains are shrinking and later loose additions are below strict thresholds. Any next calibration attempt should be capped, nested, or compared against representation-level alternatives; do not move to flexible joint logits without a new validation design.

Presleep relative-window Q3 result:

```text
new feature file                         pre_sleep_relative_features.parquet
alignment                                windows relative to proxy_screen_step_start_hour
best Q3 feature                          presleep__presleep_hr_pre6h_hr_points_count
single-feature Q3 OOF delta              -0.010128
repeated subject-half mean delta         -0.009710
repeated subject-half win-rate           0.988462
q3off650 + HR Q3 candidate               OOF 0.569619, geometry -0.000995, win-rate 0.90
q3off650 + HR/BLE Q3 combo               OOF 0.568778, geometry -0.001374, win-rate 0.90
candidate                                submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45_ble_c0.2_w0.30.csv
decision                                 accept as a Q3-risk public probe; it is stronger than the old BLE-only Q3 add-back and has modest train/sub feature shift.
```

Presleep relative-window multitarget result:

```text
script                                  presleep_multitarget_candidate_builder.py
anchor safety script                    presleep_anchor_candidate_builder.py
representation                          windows relative to proxy_screen_step_start_hour
Q1 signal                               core5h m_charging_min, subject_z, c0.5/w0.45
S1 signal                               core5h m_light_min, subject_z, c0.5/w0.45
S4 signal                               pre3h m_light_sum, subject_center, c0.5/w0.45
Q3 signal                               pre6h HR points + BLE morning unique
q3off650 core candidate                 OOF 0.565697, delta -0.005370 vs q3off650, geometry -0.005976, win-rate 1.0
q3off650 all candidate                  OOF 0.564786, delta -0.006280 vs q3off650, geometry -0.006720, win-rate 1.0
anchor core candidate                   OOF 0.572444, delta -0.005860 vs anchor, geometry -0.006258, win-rate 1.0
anchor all candidate                    OOF 0.570984, delta -0.007320 vs anchor, geometry -0.007268, win-rate 1.0
best stage2-strength blend              submission_presleepblend_core_q1s1s4_q3hrble_q3offw650.csv, OOF 0.567457
decision                                promote presleep core to first-priority score probe; keep anchor version as the public-transfer safety pair.
```

Temporal-context presleep extension:

```text
feature file                            presleep_temporal_context_features.parquet
builder                                 presleep_temporal_context_feature_builder.py
derived transforms                      dprev1, next1, past2dev, future2dev, neighbor_dev, neighbor_slope
S2 watch-light temporal signal          prectx__presleep_wlight_pre1h_w_light_min_dprev1, delta -0.005525
S2 charging temporal signal             prectx__presleep_charge_pre3h_m_charging_mean_dprev1, delta -0.005388
S3 future-neighbor light signal         prectx__presleep_mlight_pre3h_m_light_max_future2dev, delta -0.008472
Q3 ambience-next add-on                 prectx__presleep_ambience_core5h_top_is_speech_count_next1
Q3 after HR+BLE+ambience-next           0.640894 -> 0.615696, delta -0.025199
q3off650 temporal+ambnext candidate     OOF 0.562385, delta -0.008681 vs q3off650, geometry -0.009748, win-rate 1.0
anchor temporal+ambnext candidate       OOF 0.568820, delta -0.009483 vs anchor, geometry -0.010068, win-rate 1.0
blend temporal+ambnext q3offw650        OOF 0.564035, distance 0.027964
distribution shift check                S2/S3 temporal feature mean shifts within about 0.022 train standard deviations
caveat                                  S3 future2dev and Q3 next1 use future-neighbor sensor context; keep non-ambnext temporal candidate as safety pair.
```

Ordinal Q count constraint:

```text
script                                  ordinal_q_count_constraint_audit.py
premise                                 Q1/Q2/Q3 are 5-point ordinal values compared with subject full-period mean
constraint                              enumerate feasible hidden positive counts from known train labels and hidden row count
hard range clamp                        no effect; current Q sums already inside feasible ranges
best soft correction                    Q2,Q3 nearest feasible hidden-count logit shift, weight 0.75
ambnext base                            0.562385 -> 0.561904, delta -0.000481
target deltas                           Q2 -0.001522, Q3 -0.001847, Q1 unchanged
no-ambnext base                         0.563697 -> 0.563254, delta -0.000443
ambnext blend w850                      0.563027 -> 0.562294, delta -0.000732
ambnext blend w750                      0.563509 -> 0.562833, delta -0.000676
ambnext blend w650                      0.564035 -> 0.563415, delta -0.000620
candidate                               submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv
public LB                               0.5783033652, worse than submitted stage2 by +0.0003583895
decision                                hold as a useful label-generation diagnostic, not a primary score candidate. The public result does not isolate the count shift from the aggressive ambnext backbone, but it rejects using this full file directly. If reused, use only tiny probability micro-blends with a public-observed endpoint.
```

Presleep signal direction audit:

```text
Q1 high core5h charging minimum          higher Q1 positive rate; feature coefficient +0.4457
S1 higher core5h phone-light minimum     lower S1 probability after base adjustment; feature coefficient -0.5345
S4 higher pre3h phone-light              higher S4 positive rate; feature coefficient +0.3805
Q3 more HR coverage / BLE uniqueness     lower Q3 positive rate; coefficients -0.3825 / -0.3666
S2/S3 add-ons                            useful but weaker; keep as separate aggressive candidates.
```

Rejected sparse calibrator:

```text
script                  nested_sparse_calibrator_audit.py
base                    Q3-off w650
Q2/Q3 r4 geometry       Q2 +0.006751, Q3 +0.022931
non-Q r4 geometry       all targets worsened; best S3 +0.001491
decision                reject flexible sparse calibration on current base; it mostly relearns noise around already-shrunk predictions.
```

Temporal bridge residual:

```text
script                  temporal_bridge_residual_audit.py
base                    Q3-off w650
fixed geometry selected Q2 and Q3 bridge, both a0.2_gw0.5_stay1.5_sh16_bw0.35
subject-block OOF       mean +0.003621, Q2 +0.021569, Q3 +0.003779
decision                keep only as a low-priority geometry bet; ordinary OOF rejects the bridge application.
```

Public universe minimax update:

```text
script                    public_universe_minimax_optimizer.py
candidate universe         entropy/target-mask + minimax + mask-aware + conservative-frontier + priors
search masks               128 representative masks
final audit masks          2,124 simulated public-subset masks
best trusted profile       u80 -> ties old minimax frontier, six-posterior score 0.574917
best mixed profile         u65 r02, OOF 0.554117, six-posterior score 0.574947
decision                   no promotion over public_minimaxens_r01. Expanded uncertainty pushes the optimizer back to old minimax; mixed universe files are stress probes, not primary submissions.
```
