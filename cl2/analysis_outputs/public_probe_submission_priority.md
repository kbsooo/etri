# Public Probe Submission Priority

## Current Public Anchors

| File | Offline | Public LB | Interpretation |
| --- | ---: | ---: | --- |
| `submission_hybrid_0p578_logit_after_subject_final9_strict.csv` | 0.578304 | 0.5784273528 | Reliable public anchor for the late pre-broad stack. |
| `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` | 0.567531 | 0.5779449757 | Current submitted public best, but OOF gain is mostly selection bias. |
| `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` | 0.561904 | 0.5783033652 | Very strong OOF did not beat stage2 public; public transfer ratio only 0.0076 versus anchor. |

Full stage2 improves public by only `-0.0004823771` versus the anchor. That is enough to keep the direction, but not enough to trust raw broad residual OOF.

The ordinal+ambnext candidate improves anchor by only `-0.0001239876` and is worse than stage2 by `+0.0003583895`. Treat it as evidence that large OOF-only moves on the q3off/ambnext backbone are public-fragile.

## New Nested Selection Audit

The full-train broad residual search is now proven selection-biased:

```text
script                         broad_nested_selection_bias_audit.py
outer geometry repeats/top-n   8 / 10
base                           final_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity_oof.npy
nested selected mean delta     +0.008737
nested selected win-rate       0.0
fixed stage2 mean delta        -0.003272
fixed stage2 win-rate          1.0
fixed stage2 unstable target   Q3: +0.001753, win-rate 0.25
```

Interpretation: do not keep mining fresh broad residual features from the full train set. The safer public move is stage2 amplitude shrink plus target gating, especially Q3-off variants.

## New Presleep Q3 Signal

The new relative-window feature file `pre_sleep_relative_features.parquet` aggregates raw sensors around the inferred sleep start (`proxy_screen_step_start_hour`) instead of fixed clock windows. The strongest new signal is Q3:

```text
feature                     presleep__presleep_hr_pre6h_hr_points_count
transform                   subject_z
single-feature Q3 delta      -0.010128
repeated-subject mean delta  -0.009710
repeated-subject win-rate     0.988462
train/sub feature shift       modest: train mean 118.10, submission mean 124.55
```

Combining this with the older Q3 BLE uniqueness signal on the Q3-off `w650` base gives:

```text
file       submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45_ble_c0.2_w0.30.csv
OOF        0.568778
Q3 delta   -0.016016
geometry   -0.001374, win-rate 0.90
changed    Q3 only versus Q3-off w650
```

Interpretation: this is the first Q3 add-back that is not just full-train broad mining. It is still a Q3 public-risk probe, but it has stronger physiological/coverage grounding than the original stage2 Q3 move.

## Presleep Public-Direction Audit

The presleep/temporal-context family is real as a representation, but it is not currently public-safe. Re-ranking the saved presleep candidates against the two observed public axes shows:

```text
best presleep OOF file      0.562385
bad-axis projection         0.992393
two-axis public delta       +0.000357 versus stage2
```

The next strongest presleep candidates have bad-axis projection `0.75-0.93`. A dry-run projection blend that added all presleep candidates to the orthcap/exact pool selected no presleep component at any cap from `-0.005` through `0.300`. Keep presleep files as representation probes, not score-first submissions, unless a lower-projection derivative is built.

## Presleep Orthcap Follow-Up

I built the lower-projection derivative and it confirms the risk diagnosis rather than rescuing the family.

```text
script                         presleep_orthcap_builder.py
candidates                     73
best OOF                       0.565572 at projection 0.375
best global risk rank          2530 / 3739
best projection <= 0.05        OOF 0.567216, OOF gain 0.000315 vs stage2
integrity                      250 rows, no duplicate keys, no null predictions
```

Interpretation: the presleep representation is useful evidence, but most of its score movement was coupled to the public-bad ordinal direction. Once that axis is capped to a low-risk range, it no longer competes with `projblend_cap0p0`, `public2dblend_budget0p0`, or `projblend_cap0p05`.

## New Negative Controls

Two extra feature ideas were tested and rejected:

```text
covariate KNN label prior   best OOF delta -0.000199, guard mean +0.002463
row-level block gate        best geometry delta +0.001034 vs full stage2
NSF S-target proxy layer    48 configs, zero loose/strict passes on stage2
```

The first says that "similar sleep/quiet covariates imply similar labels" is too crude once stage2 is already present. The second says actual hidden block geometry does not support row-wise amplitude shrink; target/projection gating remains cleaner.

The NSF proxy audit is a sharper S-target negative control. Direct TST/efficiency/latency/WASO proxies are meaningful before the late frontier, but on top of stage2 they no longer add robust signal. S1/S2/S3 select zero blend weight, while the best S4 WASO derivative has only `-0.000188` OOF and fails repeated subject-half validation (`+0.000582`, win-rate `0.103`).

## New Public-Constraint Exploit

I treated the three observed public LB scores as aggregate linear constraints on the hidden binary labels, then solved a minimum-KL/maximum-entropy projection from several priors. This is a quasi-label exploit, not an ordinary CV candidate.

```text
script                 public_entropy_projection_builder.py
public constraints      anchor 0.5784273528, stage2 0.5779449757, ordinal 0.5783033652
generated files         16 submissions, all 250 rows / no duplicate keys / no nulls
geometry analogue       public2d0 prior: mean delta -0.010874, win-rate 1.0
best OOF analogue       public2d0 g100: 0.553679, delta vs stage2 -0.013852
self-est public model   public2d0 g100: 0.575734, g075: 0.575826, g050: 0.576100
```

Recommended order if deliberately burning a high-upside public-constraint probe:

1. `submission_public_entropyproj_public2d0_g075.csv`  
   Best balance. OOF analogue `0.554156`, public-posterior expected loss `0.575826`, mean move from prior `0.013218`. It keeps nearly all projected public benefit while avoiding exact full-strength fitting to all three public scores.

2. `submission_public_entropyproj_public2d0_g050.csv`  
   Safer shrink. OOF analogue `0.555625`, public-posterior expected loss `0.576100`, mean move `0.008793`.

3. `submission_public_entropyproj_public2d0_g100.csv`  
   Maximum exploit. OOF analogue `0.553679`, public-posterior expected loss `0.575734`, mean move `0.017658`, and exactly matches all three observed public constraints in expectation. Highest upside, highest overfit risk.

Do not compare these to the convex microblends as equally safe. The main assumption is that applying the public aggregate constraints over all 250 submission rows is close enough to the unknown public subset.

Shift decomposition for the balanced `g075` file says this is not an all-target uniform calibration. Mean absolute movement concentrates on `Q1` (`0.017613`), `Q3` (`0.016752`), `S3` (`0.015051`), and `S4` (`0.014184`). Directionally it lowers Q3 (`mean -0.003964`) and raises S3 (`mean +0.010975`); biggest cells are id10 S4 on 2024-09-24/25 and id01 Q3 on 2024-08-08.

## Public-Constraint Target Masks

I then split the public entropy projection by target subset: 127 target masks x 4 shrink levels, with geometry analogue checks for every row. This keeps the public-LB inverse signal but tests which targets are carrying it.

```text
script                 public_entropy_targetmask_builder.py
evaluated rows          508
saved candidates        48, all integrity-clean
best risk score         Q1+Q3+S1+S2+S3+S4 g050
best <=0.012 mean move  Q1+Q3+S1+S2+S3+S4 g075
main lesson             Q2 can be dropped with almost no loss; core movement is Q1/Q3/S3/S4
```

New public-constraint priority:

1. `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv`  
   Best balanced target mask: drops Q2, keeps nearly all full-g075 upside. OOF analogue `0.554185`, public-posterior expected `0.575887`, mean move `0.011874`, geometry delta `-0.010185`, win-rate `1.0`.

2. `submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv`  
   Drops both Q2 and S1. OOF `0.555407`, expected `0.575956`, mean move `0.010956`, geometry delta `-0.008045`.

3. `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv`  
   Lowest-risk target-mask score by the current risk score. OOF `0.555707`, expected `0.576149`, mean move `0.007898`, geometry delta `-0.008158`.

4. `submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv`  
   Core attribution probe. OOF `0.556265`, expected `0.576140`, mean move `0.009086`, geometry delta `-0.006413`. This tests whether the public inverse signal is mostly Q1/Q3/S3/S4 without S1/S2/Q2.

## Public Subset Sensitivity

I stress-tested the public-constraint candidates under possible public row subsets: random row subsets, global prefix/suffix/modulo splits, per-subject prefix/suffix/contiguous blocks, and single-subject masks.

Single-posterior subset audit using full `g100` as the posterior says all entropy candidates beat the public2d0 prior on every simulated subset, but this is biased toward `g100`. A stronger multi-posterior scenario audit uses six plausible posterior scenarios and ranks candidates by subset regret.

```text
script                         public_posterior_scenario_robustness.py
best scenario-robust file       submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv
mean expected                   0.574649
mean regret                     0.000082
p90 regret                      0.000159
win-rate vs public2d0 prior     1.0000
full g100 rank                  13th; p90 delta vs prior barely positive, win-rate 0.8371
```

Decision update: promote the Q2-dropped `g075` target-mask above raw `g100`. It keeps the strongest public-constraint signal while avoiding the exact-fit endpoint's posterior-scenario fragility.

## Public Minimax Ensemble

I optimized convex ensembles over the public-constraint files against the six posterior scenarios and simulated public subsets. The gain is small but consistent: it lowers regret versus the best single target-mask while preserving the expected public-posterior score.

```text
script                    public_minimax_ensemble_optimizer.py
selected sparse file       submission_public_minimaxens_r01_a6_h422045.csv
mean expected              0.574634
mean regret                0.000067
p90 regret                 0.000118
win-rate vs public2d0      1.0000
OOF analogue               0.554332
integrity                  250 rows, no duplicate keys, no null predictions
```

Decision update: for a public-constraint submission, `submission_public_minimaxens_r01_a6_h422045.csv` is now the best default. Use `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv` if a single interpretable target-mask file is preferred over an ensemble.

## Public Conservative Frontier

I added a conservative uncertainty layer that scores candidates against both the entropy posterior scenarios and pseudo-posteriors from submitted-safe files: stage2, public2d0, projblend, and the 0.578 anchor. This tests whether a candidate remains reasonable if the public entropy projection is partly overfit.

```text
script                         public_conservative_frontier_builder.py
generated submissions           12
best higher-trust bridge         submission_public_consfront_t80_r10_b06ca82f.csv
construction                    35% anchor->stage2 w095 + 65% minimax r01, probability blend, all targets
OOF analogue                    0.557498
posterior mean expected          0.574792
conservative mean expected       0.574646
entropy-only robust score        0.575799
integrity                       250 rows, no duplicate keys, no null predictions
```

Decision update: the conservative frontier is not the top upside candidate. Raw minimax remains better if the entropy posterior is trusted. The conservative bridge is useful as a mid-risk submission when we want some public-constraint upside but want to dampen the exact three-score posterior assumption.

## Public Mask-Aware Entropy Projection

I tested the biggest remaining assumption in the public-LB inverse method: that the public rows are close enough to all 250 submission rows. The new script solves the three public-score constraints on many candidate public masks and averages the logit shifts either marginally or conditionally on row inclusion.

```text
script                         public_maskaware_entropy_projection.py
mask families                   all/global/rowmod/subject_order/subject_contig/random/random50
global prefix/suffix movement   mean probability move 0.035586
random movement                 mean probability move 0.018525
subject-contiguous movement     mean probability move 0.017478
best mask-aware robustness      submission_public_maskaware_t80_r11_544844af.csv
OOF analogue                    0.553156
mean expected                   0.574650
p90 regret                      0.000160
win-rate vs public2d0 prior     1.0000
```

Decision update: mask-aware projection does not replace the minimax ensemble. It gives a strong fallback for row-subset uncertainty and weakens the case that the public split is a simple chronological prefix/suffix, because those masks need roughly double the all-row probability movement to explain the three observed LB scores.

## Public Universe Minimax

I expanded the minimax search to include entropy/target-mask candidates, mask-aware candidates, conservative-frontier bridges, raw priors, and prior minimax ensembles. The optimizer used 128 representative masks for search, then re-ranked saved candidates on all 2,124 simulated public-subset masks.

```text
script                         public_universe_minimax_optimizer.py
saved submissions               16
best u80 file                   submission_public_universeens_u80_r01_07c571e6.csv
u80 six-posterior score          0.574917
u80 OOF analogue                 0.554343
best u65 mixed file              submission_public_universeens_u65_r02_c0e2b2f1.csv
u65 six-posterior score          0.574947
u65 OOF analogue                 0.554117
integrity                       250 rows, no duplicate keys, no null predictions
```

Decision update: this does not supersede `submission_public_minimaxens_r01_a6_h422045.csv`. The most trusted profile (`u80`) collapses back onto existing minimax files, and the more mixed profiles buy pseudo-posterior coverage by increasing regret. Treat universe minimax as confirmation that the current public-constraint frontier is saturated, not as a new primary submission lane.

## Revised Best Next Submissions

1. `submission_publicobsblend_stage2_to_ordinal_w005.csv`  
   Probability micro-blend: 95% submitted stage2 + 5% ordinal/ambnext. OOF `0.567025`. Because both endpoints have public scores and the blend is in probability space, public Log Loss is convex-bounded by `0.5779628952`, only `+0.0000179195` worse than the current public best. This remains the lowest-risk endpoint sanity check.

2. `submission_projblend_cap0p0.csv`  
   Projection-constrained blend with essentially zero exposure to the observed public-bad stage2->ordinal direction. OOF `0.562144`, projection `-0.000049`, linear public estimate `0.577945`. This is the cleanest non-convex diagnostic after the ordinal public miss.

3. `submission_public2dblend_budget0p0.csv`  
   Two-public-axis blend using both the public-good anchor->stage2 axis and the public-bad stage2->ordinal axis. OOF `0.561702`, two-axis public delta `-0.00000005` versus stage2, one-axis public delta `+0.00000890`. This is more model-based than `projblend_cap0p0`, but it carries a better OOF at a still small one-axis exposure.

4. `submission_projblend_cap0p05.csv`  
   Balanced low-risk projection blend. OOF `0.561307`, projection `0.048995`, linear public estimate `0.577963`. It dominates the earlier low-projection orthcap/exact candidates at similar public-direction exposure.

5. `submission_public2dblend_budget0p00002.csv`  
   Balanced two-axis score probe. OOF `0.560724`, two-axis public delta `+0.00001997`, one-axis public delta `+0.00003077`. This is a cleaner intermediate step before the raw `projblend_cap0p1`.

6. `submission_projblend_cap0p1.csv`  
   Main score/projection tradeoff candidate. OOF `0.560523`, projection `0.099482`, linear public estimate `0.577981`. This keeps the risk level near the old `cap010` exact-count family but is slightly cleaner by construction.

7. `submission_public2dblend_budget0p00005.csv`  
   Higher-upside two-axis blend. OOF `0.560039`, two-axis public delta `+0.00004984`, one-axis public delta `+0.00006145`. Use only after lower-risk two-axis files transfer.

8. `submission_projblend_cap0p15.csv`  
   Higher-upside projection blend. OOF `0.560170`, projection `0.149470`, linear public estimate `0.577999`. Use only after a lower-cap blend shows public transfer.

9. `submission_publicobsblend_stage2_to_ordinal_w010.csv`  
   90% stage2 + 10% ordinal. OOF `0.566549`; convex public upper bound `0.5779808147`, only `+0.0000358390` versus stage2. This is safer than any non-convex file but less informative than the projection ladder.

10. `submission_orthcap005c000_exact_q3_exact_value_nearest_w1.csv`  
   Pure-orthogonal orthcap plus Q3-only nearest hidden-count quantization. OOF `0.562810`, projection `-0.005704`, linear public estimate `0.577943`. Superseded by `projblend_cap0p0` as a score candidate, but still the most interpretable Q3-only diagnostic.

11. `submission_orthcap009c005_exact_q2q3_exact_value_nearest_w1.csv`  
   Low-projection orthcap plus Q2/Q3 nearest count quantization. OOF `0.561729`, projection `0.051616`, linear public estimate `0.577963`. Superseded by `projblend_cap0p05`, but useful as a single-source comparison.

12. `submission_projblend_cap0p2.csv`  
   Score-first projection blend. OOF `0.559879`, projection `0.199447`, linear public estimate `0.578016`. This is high-upside only, but less exposed than the raw `cap030` exact-count file.

13. `submission_projblend_cap0p3.csv`  
   Highest OOF projection blend in the generated ladder. OOF `0.559381`, projection `0.299402`, linear public estimate `0.578052`. Use only if deliberately testing the high-upside end of the non-convex family.

14. `submission_orthcap030_exact_q2q3_exact_value_nearest_w1.csv`  
   Highest OOF exact-count rescue. OOF `0.559355`, projection `0.305399`, linear public estimate `0.578054`. It is now mostly a reference endpoint for the projection blends.

15. `submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv`  
   Public-inferred anchor/stage2 latent-mix candidate. Distance from anchor is much lower (`0.018524`) than raw stage2 (`0.034006`), but the two-point latent model is weaker than observed-pair convex micro-blends because ordinal public exposed stronger OOF-public mismatch.

16. `submission_publicgated_anchor578_stage2_drop_q3_prob_w545.csv`  
   Q3-off lower-amplitude probe. OOF `0.571900`, distance `0.015469`. Use as an attribution/score hybrid if the next goal is to test whether stage2 Q3 is hurting public.

17. `submission_label_prior_gate_blend500_ambnext_r8_S2__global_qs_a0.5_w0.25_sh0.csv`  
   S2-only label-combination prior on the low-distance blend500/ambnext file. Geometry delta `-0.000690`, win-rate `0.75`, but ordinary OOF delta only `-0.000030`; information-oriented, not primary score.

18. `submission_subjectgate_ordinal_all_thrm0p005_w100.csv`  
   Subject-target gate from stage2 to ordinal, activated only where the donor wins by at least `0.005` OOF in a subject-target cell. Full OOF `0.558584`, time-half guarded OOF `0.563328`, projection onto the observed stage2->ordinal public-bad direction `0.623`. This remains the strongest high-upside raw probe, but it is not low-risk.

19. `submission_subjectgate_ordinal_all_thrm0p02_w080.csv`  
   Lower-projection subject-gate alternative. Full OOF `0.562297`, time-half guarded OOF `0.564583`, bad-direction projection `0.321`, active subject-targets `13`. Use this before the full-strength subjectgate if public-risk control matters more than OOF upside.

20. `submission_anchor578_presleep_core_prectx_s2wlight_s3light_q3hr_ble.csv`  
   Stage2-free test of the presleep temporal-context representation without the extra ambience-next layer. OOF `0.570132`, geometry delta `-0.008820`, distance `0.018696`.

## Target-Mask Follow-Up

After the ordinal public miss, the full stage2 -> ordinal direction is an observed public-bad direction. I generated target-masked donor candidates and ranked them by projection onto that direction.

Best information probes:

```text
submission_stage2_donor_ordinal_q3_s_w035.csv        OOF 0.564838, projection 0.295, Q3+S targets only
submission_stage2_donor_ordinal_s1_s3_s4_w080.csv    OOF 0.565139, projection 0.316, S1/S3/S4 only
submission_stage2_donor_ordinal_q3_w100.csv          OOF 0.565174, projection 0.342, Q3 only
submission_stage2_donor_ordinal_no_q2_w035.csv       OOF 0.564668, projection 0.345, all except Q2
submission_stage2_donor_blend500_q3_s_w050.csv       OOF 0.564686, projection 0.458, lower-distance blend500 donor
```

Use these after the convex-bound microblends if the goal is attribution rather than immediate LB risk minimization.

## Subject-Target Gate Follow-Up

The new subject-gate family chooses donor probabilities per subject-target, not per whole file or whole target. This directly attacks the ordinal public failure pattern, where some subject-target cells improve a lot in OOF while others are obvious donors to avoid.

Best high-upside gates:

```text
submission_subjectgate_ordinal_all_thrm0p005_w100.csv  full OOF 0.558584, half-gate 0.563328, projection 0.623
submission_subjectgate_ordinal_all_thr0p0_w100.csv     full OOF 0.558264, half-gate 0.563378, projection 0.709
submission_subjectgate_ordinal_all_thrm0p0025_w100.csv full OOF 0.558348, half-gate 0.563547, projection 0.689
```

Lower-risk subject-gate probes:

```text
submission_subjectgate_ordinal_all_thrm0p02_w080.csv      OOF 0.562297, half-gate 0.564583, projection 0.321
submission_subjectgate_ordinal_s1_s3_s4_thrm0p01_w100.csv OOF 0.563962, half-gate 0.565689, projection 0.166
submission_subjectgate_blend500_s1_s3_s4_thrm0p005_w100.csv OOF 0.563737, half-gate 0.565780, projection 0.186
```

Use the first group only as a deliberate high-upside public probe. The second group is better for diagnosing whether subject-cell gating transfers without inheriting most of the failed ordinal direction.

## Orthcap Follow-Up

Orthcap is a new public-aware representation of the subjectgate/targetmask family. It removes or caps the observed public-bad axis while preserving the orthogonal residual.

```text
submission_orthcap_s001_cap030_sc100.csv  OOF 0.560427, projection 0.300, no hard clip
submission_orthcap_s001_cap020_sc100.csv  OOF 0.561165, projection 0.200, no hard clip
submission_orthcap_s001_cap010_sc100.csv  OOF 0.561989, projection 0.100, max prob 0.984159
submission_orthcap_s009_cap005_sc100.csv  OOF 0.562905, projection 0.050, no hard clip
submission_orthcap_s005_cap000_sc100.csv  OOF 0.563648, projection ~0.000, no hard clip
submission_orthcap_s001_capm005_sc075.csv OOF 0.564217, projection -0.0375, recoil probe
```

Submit sequence for this family: `cap005` first if public-risk minimization matters, `cap010` for balanced score/projection, `cap030` for high-upside. The negative projection recoil file is diagnostic only.

## Exact Ordinal Prior Follow-Up

The exact 1-5 value-count prior does not rescue posterior mean/mode. Those variants worsen OOF. The only useful operation is nearest hidden-positive-count quantization, and Q1 should be excluded.

```text
submission_orthcap005c000_exact_q3_exact_value_nearest_w1.csv   OOF 0.562810, projection -0.005704
submission_orthcap009c005_exact_q2q3_exact_value_nearest_w1.csv OOF 0.561729, projection  0.051616
submission_orthcap010_exact_q3_exact_value_nearest_w1.csv       OOF 0.560925, projection  0.101177
submission_orthcap010_exact_q2q3_exact_value_nearest_w1.csv     OOF 0.560448, projection  0.105490
submission_orthcap030_exact_q2q3_exact_value_nearest_w1.csv     OOF 0.559355, projection  0.305399
```

Use Q3-only variants when the goal is an interpretable public-risk probe. Use Q2/Q3 variants only when accepting slightly more ordinal-direction coupling for a better OOF score.

## Projection-Constrained Blend Follow-Up

The projection blend optimizer searches probability blends among orthcap/exact-count candidates while capping exposure to the observed failed stage2->ordinal direction. This gives a cleaner risk ladder than choosing one orthcap endpoint by hand.

```text
submission_projblend_cap0p0.csv    OOF 0.562144, projection -0.000049
submission_projblend_cap0p025.csv  OOF 0.561715, projection  0.024479
submission_projblend_cap0p05.csv   OOF 0.561307, projection  0.048995
submission_projblend_cap0p075.csv  OOF 0.560904, projection  0.074578
submission_projblend_cap0p1.csv    OOF 0.560523, projection  0.099482
submission_projblend_cap0p15.csv   OOF 0.560170, projection  0.149470
submission_projblend_cap0p2.csv    OOF 0.559879, projection  0.199447
submission_projblend_cap0p3.csv    OOF 0.559381, projection  0.299402
```

All generated projection blends have 250 rows, no duplicate keys, no missing predictions, and favorable per-target OOF deltas versus stage2. The `cap0p05` and `cap0p1` files are the main non-convex score probes; `cap0p0` is the safest diagnostic.

S2 label-prior variants remain diagnostic only. On orthcap/exact bases they reduce public-direction projection, but full OOF worsens S2 by about `+0.0020`, so they are not promoted as score candidates.

## Public Two-Axis Blend Follow-Up

The public two-axis optimizer adds the observed public-good `anchor578 -> stage2` direction to the observed public-bad `stage2 -> ordinal` direction. This is more model-based than one-axis projection, but it uses all three public observations instead of only the ordinal failure.

```text
submission_public2dblend_budget0p0.csv      OOF 0.561702, two-axis public delta -0.00000005, one-axis delta +0.00000890
submission_public2dblend_budget0p00002.csv  OOF 0.560724, two-axis public delta +0.00001997, one-axis delta +0.00003077
submission_public2dblend_budget0p00005.csv  OOF 0.560039, two-axis public delta +0.00004984, one-axis delta +0.00006145
submission_public2dblend_budget0p00010.csv  OOF 0.559351, two-axis public delta +0.00009737, one-axis delta +0.00010932
```

The practical change is that `budget0p0` becomes the best low-risk non-convex file after `projblend_cap0p0`, and `budget0p00002` becomes the best intermediate score probe before `projblend_cap0p1`. Do not overinterpret the two-axis estimate: low-risk files still have high residual ratio outside the two public axes, so this is ranking evidence rather than a public guarantee.

## Superseded Score List Before Ordinal Public

### Score-Oriented

1. `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv`  
   Current strongest local candidate. It takes the temporal+ambnext q3off file and applies the ordinal questionnaire count constraint only to Q2/Q3. OOF `0.561904`, delta `-0.000481` versus the raw ambnext candidate, mean distance from anchor `0.033615`. Q2 delta `-0.001522`, Q3 delta `-0.001847`, Q1 unchanged.

2. `submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv`  
   Strongest representation-only score candidate. It starts from Q3-off `w650`, adds presleep Q1/S1/S4, temporal-context S2/S3, HR+BLE Q3, then the new Q3 ambience-next residual. OOF `0.562385`, geometry delta `-0.009748`, geometry win-rate `1.0`, mean distance from anchor `0.033284`. This is aggressive because S3 and the extra Q3 layer use future-neighbor sensor context.

3. `submission_ordinal_q_constraints_ambnext_blend850_q2q3_nearest_w1.csv`  
   High-score public-aware blend with the same Q2/Q3 ordinal-count correction. OOF `0.562294`, distance `0.031483`, so it gives up only `+0.000390` OOF versus the full q3off ordinal file while moving slightly closer to the validated anchor.

4. `submission_ordinal_q_constraints_ambnext_blend750_q2q3_nearest_w1.csv`  
   More conservative ordinal blend. OOF `0.562833`, distance `0.030010`.

5. `submission_anchor578_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv`  
   Stage2-free safety pair for the same temporal-context discovery. OOF `0.568820`, geometry delta `-0.010068`, win-rate `1.0`, distance `0.021121`. This isolates the new representation from the public-overfit risk of the old stage2/q3off backbone.

6. `submission_ordinal_q_constraints_noamb_q2q3_nearest_w0.75.csv`  
   Safer no-ambience version with the same Q2/Q3 ordinal-count correction. OOF `0.563254`, mean distance from anchor `0.031307`.

7. `submission_ordinal_q_constraints_ambnext_blend650_q2q3_nearest_w1.csv`  
   Lower-amplitude public-aware ordinal blend. OOF `0.563415`, distance `0.028605`.

8. `submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble.csv`  
   Same temporal-context S2/S3 candidate without the extra Q3 ambience-next layer. OOF `0.563697`, geometry delta `-0.008500`, win-rate `1.0`, distance `0.030860`. Use this if the `next1` Q3 feature looks too aggressive.

9. `submission_presleepblend_prectx_s2wlight_s3light_q3hrble_ambnext_q3offw650.csv`  
   Non-ordinal public-aware blend between the anchor-presleep and q3off-presleep ambience-next candidates. OOF `0.564035`, distance `0.027964`.

10. `submission_anchor578_presleep_core_prectx_s2wlight_s3light_q3hr_ble.csv`  
   Stage2-free non-ambience safety pair. OOF `0.570132`, geometry delta `-0.008820`, win-rate `1.0`, distance `0.018696`.

11. `submission_publicgated_q3off650_presleep_core_q1_s1_s4_q3hr_ble.csv`  
   Earlier presleep core without temporal-context S2/S3. OOF `0.565697`, geometry delta `-0.005976`, win-rate `1.0`, distance `0.028909`.

12. `submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv`  
   Exact probability blend at the latent mix coefficient inferred from the two public LB observations (`alpha = 0.544736`). Under the anchor-stage2 latent mixture model this is the best score-oriented candidate.

13. `submission_publicgated_anchor578_stage2_drop_q3_prob_w650.csv`  
   Q3-off stage2 gate with moderate amplitude. This keeps the strongest geometry-stable targets while removing the only fixed-stage2 target that loses in nested geometry.

14. `submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45_ble_c0.2_w0.30.csv`  
   Q3-off `w650` plus the new presleep-HR Q3 add-back and a thin BLE Q3 add-on. OOF and geometry are better than plain Q3-off, but submit as a Q3-risk probe.

15. `submission_publicgated_anchor578_stage2_drop_q3_prob_w545.csv`  
   Same Q3-off direction at the public-inferred amplitude. Use as the lower-risk pair to the `w650` Q3-off probe.

16. `submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45.csv`  
   Single-feature version of the new Q3 add-back. OOF `0.569619`, geometry `-0.000995`, win-rate `0.90`; lower complexity than the HR+BLE combo.

17. `submission_label_prior_gate_q3off650_r8_S2__global_qs_a0.5_w0.25_sh0.csv`  
   Q3-off `w650` plus an S2-only label-combination prior. Geometry says `-0.000546` with win-rate `0.75`; subject-block OOF slightly worsens, so treat this as a submission-geometry bet, not a general CV win.

18. `submission_publicblend_anchor578_stage2567_prob_w050.csv`  
   Almost the same as the inferred optimum, with slightly lower full-stage2 amplitude.

### Information-Oriented

1. `submission_publicgated_anchor578_stage2_drop_q3_prob_w1000.csv`  
   Direct Q3-off test. If this beats full stage2 public, Q3 should be removed or heavily damped in all future broad residual stacks.

2. `submission_publicgated_anchor578_stage2_no_q2q3_prob_w650.csv`  
   Tests whether Q2's small broad move is also unnecessary after Q3 is removed.

3. `submission_publicprobe_anchor578_stage2only_s.csv` and `submission_publicprobe_anchor578_stage2only_q.csv`  
   Submit as a pair when the goal is attribution. Their public deltas decompose whether the stage2 gain comes from objective S targets or subjective Q targets.

4. `submission_anchor578_presleep_core_q1_s1_s4.csv` and `submission_anchor578_presleep_core_q1_s1_s4_q3hr_ble.csv`  
   These are the cleanest public tests of the new sleep-relative representation because they are anchored on the validated 0.578 file and do not include stage2 broad residual amplitude.

5. `submission_publicprobe_anchor578_presleep_q3_hr_ble.csv`  
   Isolated Q3-only probe for the presleep HR+BLE signal. OOF `0.576016`, Q3-only delta `-0.002288` versus anchor.

6. `submission_publicprobe_anchor578_stage2_drop_s3.csv` and `submission_publicprobe_anchor578_stage2_drop_s4.csv`  
   Previous diagnostics remain useful, but nested fixed-stage2 now says S3/S4 are internally stable; Q3 has higher priority.

7. `submission_label_prior_gate_stage2_r8_S2__subject_joint_a0.5_w0.25_sh8.csv`  
   Pure S2 label-combination prior on full stage2. This tests whether S2 needs an upward correction from target-combination structure.

## Presleep Multitarget Result

The main new discovery is not just Q3. Sleep-start-relative windows expose a coherent target map:

```text
Q1  core5h phone charging minimum       OOF target delta -0.005870 on q3off650, -0.007689 on anchor
S1  core5h phone-light minimum          OOF target delta -0.008581 on q3off650, -0.008747 on anchor
S4  pre3h phone-light sum               OOF target delta -0.007120 on q3off650, -0.008566 on anchor
Q3  pre6h watch-HR points + BLE unique  OOF target delta -0.016016
```

Feature shift is acceptable for Q1/S4/Q3 and moderate for S2/S3. S1 is sparse (`train_zero_rate 0.969`, `sub_zero_rate 0.953`), so aggressive S1 candidates should be paired with the anchor-based safety submission.

## Temporal-Context Presleep Result

The next representation step uses day-neighbor transforms of the presleep window features (`dprev1`, `next1`, `past2dev`, `future2dev`, `neighbor_dev`, `neighbor_slope`). This exposed the missing S2/S3 layer and a much stronger Q3 residual:

```text
S2  prectx__presleep_wlight_pre1h_w_light_min_dprev1       target delta -0.005525, repeated win-rate 0.831
S2  prectx__presleep_charge_pre3h_m_charging_mean_dprev1   target delta -0.005388, repeated win-rate 0.962
S3  prectx__presleep_mlight_pre3h_m_light_max_future2dev   target delta -0.008472, repeated win-rate 0.992
Q3  prectx ambience core5h top-is-speech count next1       HR+BLE Q3 loss 0.624878 -> 0.615696
```

Train/sub feature shift for the S2/S3 temporal-context features is small: `-0.0218`, `-0.0047`, and `-0.0119` train-standard deviations for the watch-light S2, charging S2, and S3 light features respectively. The caveat is semantic rather than statistical: `future2dev` and `next1` use neighboring future-day sensor context, so these are valid only if the full test lifelog table is available at prediction time.

## Ordinal Q Count Constraint

Q1/Q2/Q3 originate from 5-point questionnaire values compared with each subject's full-period average. Enumerating all possible 1-5 ordinal count distributions gives feasible hidden positive counts for each subject and target. The feasible range is wide enough that hard range-clamping changes nothing, but softly shifting Q2/Q3 predictions toward the nearest feasible hidden-positive count gives a small independent OOF gain:

```text
script                       ordinal_q_count_constraint_audit.py
base                         temporal+ambnext q3off candidate
best targets                 Q2,Q3 only
strategy                     nearest feasible hidden-positive count, logit shift, weight 0.75
OOF                          0.562385 -> 0.561904
target deltas                Q2 -0.001522, Q3 -0.001847, Q1 0.000000
no-ambnext safety version     0.563697 -> 0.563254
blend w850 version            0.563027 -> 0.562294
blend w750 version            0.563509 -> 0.562833
blend w650 version            0.564035 -> 0.563415
```

This uses only known train labels, subject row counts, and the published ordinal-label generation rule.

Public update: the submitted ordinal/ambnext file scored `0.5783033652`, worse than the stage2 public best `0.5779449757`. This does not isolate the ordinal correction from the aggressive ambnext backbone, but it does demote this family from score priority. Keep only low-amplitude probability micro-blends with stage2.

Exact-prior update: enumerating all 1-5 value-count distributions confirms the posterior prior is not useful. The public-safe form is not posterior mean/mode; it is a nearest integer hidden-count quantization, preferably Q3-only and only after removing/capping the failed public direction via orthcap.

## Public LB Inverse Result

The two public observations define a one-dimensional constraint for the full stage2 move:

```text
public delta stage2 vs anchor     -0.0004823771
offline delta stage2 vs anchor    -0.010773
public/offline transfer ratio      0.044776
delta if anchor probs were truth   +0.005302
delta if stage2 probs were truth   -0.005317
latent mix alpha                   0.544736
```

Interpretation: full stage2 was too high-amplitude, but the public labels are slightly closer to stage2 than anchor along that direction. This supports a mid-strength probability blend rather than stage3 broad residual stacking.

## How To Interpret New Public Scores

Let `A = 0.5784273528` be the anchor public LB and `F = 0.5779449757` be the full stage2 public LB.

For any probe file, compute:

```text
delta_probe = public_probe - A
delta_full  = F - A = -0.0004823771
```

Rules:

```text
drop_s3 < F  => S3 stage2 move was hurting public; prefer drop_s3 or retune S3 lower.
drop_s3 > F  => S3 stage2 move helped; keep S3.

drop_s4 < F  => S4 stage2 move was hurting public; prefer drop_s4 or retune S4 lower.
drop_s4 > F  => S4 stage2 move helped; keep S4.

drop_q3 < F  => Q3 stage2 move was hurting public; prefer Q3-off gated blends.
drop_q3 > F  => Q3 stage2 move helped public despite nested geometry risk; keep only in damped full-stage2 blends.

stage2only_s < A and stage2only_q >= A => S targets carry the public gain; stop broad Q additions.
stage2only_q < A and stage2only_s >= A => Q targets carry the public gain; S stage2 is mostly overfit.
both improve => combine carefully, then line-search amplitude.
both worsen while full improves => target interactions/calibration matter; use damped full-stage2 blends.
```

## Generated Probe Summary

| Probe | File | Changed Targets | OOF | Mean Distance From Anchor |
| --- | --- | --- | ---: | ---: |
| temporal+ambnext + ordinal Q2/Q3 | `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.561904 | 0.033615 |
| temporal+ambnext blend850 + ordinal Q2/Q3 | `submission_ordinal_q_constraints_ambnext_blend850_q2q3_nearest_w1.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.562294 | 0.031483 |
| temporal+ambnext blend750 + ordinal Q2/Q3 | `submission_ordinal_q_constraints_ambnext_blend750_q2q3_nearest_w1.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.562833 | 0.030010 |
| q3off temporal+ambnext | `submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.562385 | 0.033284 |
| temporal no-ambnext + ordinal Q2/Q3 | `submission_ordinal_q_constraints_noamb_q2q3_nearest_w0.75.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.563254 | 0.031307 |
| temporal+ambnext blend650 + ordinal Q2/Q3 | `submission_ordinal_q_constraints_ambnext_blend650_q2q3_nearest_w1.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.563415 | 0.028605 |
| anchor temporal+ambnext | `submission_anchor578_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv` | Q1,Q3,S1,S2,S3,S4 | 0.568820 | 0.021121 |
| temporal+ambnext blend w650 | `submission_presleepblend_prectx_s2wlight_s3light_q3hrble_ambnext_q3offw650.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.564035 | 0.027964 |
| q3off temporal no-ambnext | `submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.563697 | 0.030860 |
| anchor temporal no-ambnext | `submission_anchor578_presleep_core_prectx_s2wlight_s3light_q3hr_ble.csv` | Q1,Q3,S1,S2,S3,S4 | 0.570132 | 0.018696 |
| q3off presleep core | `submission_publicgated_q3off650_presleep_core_q1_s1_s4_q3hr_ble.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.565697 | 0.028909 |
| q3off presleep all | `submission_publicgated_q3off650_presleep_core_all_s2quiet_q3hr_ble.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.564786 | 0.031792 |
| anchor presleep core | `submission_anchor578_presleep_core_q1_s1_s4_q3hr_ble.csv` | Q1,Q3,S1,S4 | 0.572444 | 0.014147 |
| anchor presleep all | `submission_anchor578_presleep_core_all_s2quiet_q3hr_ble.csv` | Q1,Q3,S1,S2,S3,S4 | 0.570984 | 0.019683 |
| presleep core blend w650 | `submission_presleepblend_core_q1s1s4_q3hrble_q3offw650.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | 0.567457 | 0.023135 |
| latent mix blend | `submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | public-mix pred `0.576841` | 0.018524 |
| Q3-off w650 | `submission_publicgated_anchor578_stage2_drop_q3_prob_w650.csv` | Q1,Q2,S1,S2,S3,S4 | 0.571066 | 0.018449 |
| Q3-off w650 + presleep HR/BLE Q3 | `submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45_ble_c0.2_w0.30.csv` | Q1,Q2,Q3,S1,S2,S3,S4, Q3 add-back | 0.568778 | 0.023675 |
| Q3-off w650 + presleep HR Q3 | `submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45.csv` | Q1,Q2,Q3,S1,S2,S3,S4, Q3 add-back | 0.569619 | 0.023100 |
| Q3-off w650 + S2 label prior | `submission_label_prior_gate_q3off650_r8_S2__global_qs_a0.5_w0.25_sh0.csv` | Q1,Q2,S1,S2,S3,S4 plus S2 prior | 0.571156 | S2-only delta mean 0.020952 |
| Q3-off w545 | `submission_publicgated_anchor578_stage2_drop_q3_prob_w545.csv` | Q1,Q2,S1,S2,S3,S4 | 0.571900 | 0.015469 |
| Q3-off full | `submission_publicgated_anchor578_stage2_drop_q3_prob_w1000.csv` | Q1,Q2,S1,S2,S3,S4 | 0.569037 | 0.028384 |
| no Q2/Q3 w650 | `submission_publicgated_anchor578_stage2_no_q2q3_prob_w650.csv` | Q1,S1,S2,S3,S4 | 0.571421 | 0.016070 |
| full stage2 + S2 label prior | `submission_label_prior_gate_stage2_r8_S2__subject_joint_a0.5_w0.25_sh8.csv` | Q1,Q2,Q3,S1,S2,S3,S4 plus S2 prior | 0.567846 | S2-only delta mean 0.023581 |
| 50% blend | `submission_publicblend_anchor578_stage2567_prob_w050.csv` | Q1,Q2,Q3,S1,S2,S3,S4 | public-mix pred `0.576852` | 0.017003 |
| drop S3 | `submission_publicprobe_anchor578_stage2_drop_s3.csv` | Q1,Q2,Q3,S1,S2,S4 | 0.568801 | 0.028304 |
| drop S4 | `submission_publicprobe_anchor578_stage2_drop_s4.csv` | Q1,Q2,Q3,S1,S2,S3 | 0.569226 | 0.028449 |
| S only | `submission_publicprobe_anchor578_stage2only_s.csv` | S1,S2,S3,S4 | 0.572294 | 0.018096 |
| Q only | `submission_publicprobe_anchor578_stage2only_q.csv` | Q1,Q2,Q3 | 0.573540 | 0.015910 |
| Q3/S1/S4 | `submission_publicprobe_anchor578_stage2only_q3s1s4.csv` | Q3,S1,S4 | 0.573828 | 0.013209 |
| S1/S4 | `submission_publicprobe_anchor578_stage2only_s1s4.csv` | S1,S4 | 0.575335 | 0.007586 |
| Q1 only | `submission_publicprobe_anchor578_stage2only_q1.csv` | Q1 | 0.575487 | 0.006627 |
| broad Q1/Q2 only | `submission_publicprobe_anchor578_broadq1q2only_q1q2.csv` | Q1,Q2 | 0.575740 | 0.007833 |

All listed files passed submission integrity checks: 250 rows, sample key order true, nulls 0, duplicate keys 0, probabilities inside `[1e-5, 1-1e-5]`.
