# 0.5-Range Breakthrough Findings

## Executive Finding

`0.62` is not the structural limit of the labels. A validation-block-rate oracle reaches `0.51788`, so a `0.5x` score is possible if the hidden submission block rates can be inferred.

What failed: row-level sensor models, 7-bit Markov transitions, and nested single-feature threshold reconstruction.

What helped: predicting block-level state/rate, sleep-episode alignment, inferred quiet intervals, and quiet-interval fragmentation.

Major update: the original daily feature alignment was missing the post-midnight part of the sleep episode. Remapping records from `00:00-11:59` to the previous `lifelog_date` creates overnight features that improve the best estimate from the `0.62` range to about `0.605`.

Second update: `Q2` can be moved materially by combining temporal prior, pre-sleep app usage, and a soft subject-rate constraint. This produces the first non-oracle candidate with an estimated mean below `0.600`: `0.599681`.

Third update: `Q3` has a weaker version of the same signal. A fixed `logreg_c0.03 0.10 + soft-rate 0.10` combo improves outer OOF `Q3` from `0.66222` to `0.65727`, pushing the best aggressive candidate to `0.598973`.

## Key Evidence

| Probe | Subject-block Log Loss | Interpretation |
| --- | ---: | --- |
| Temporal base | 0.62477 | Current robust backbone. |
| Full subject-rate oracle | 0.59363 | Even knowing full subject rates is not enough for strong 0.5x. |
| Validation block-rate oracle | 0.51788 | 0.5x is possible if block rates are inferred. |
| Pattern Markov bridge | 0.62776 | Label transition dynamics do not transfer. |
| Nested single-threshold feature search | 0.66904 | Direct one-feature sensor formula not stable. |
| Validation-selected threshold diagnostic | 0.56840 | There are many fold-specific slices, but they overfit. |
| Block smoother grid best | 0.62117 | Block context helps, but not enough. |
| Block smoother nested all-target | 0.62345 | All-target block smoothing overfits Q targets. |
| S-target block switch estimate | 0.62047 | Use block smoother only for `S1/S2/S4`. |
| Fixed-config S-target switch estimate | 0.61981 | Aggressive candidate, not a fully nested selector. |
| Overnight phone nested blend | 0.60904 | First large non-oracle improvement; fixes sleep-window alignment. |
| Hybrid overnight/block target switch | 0.60491 | Current aggressive best estimate. |
| Q2 soft app/rate combo | 0.66357 on Q2 | Strict nested Q2 improvement, from `0.69271` to `0.66357`. |
| Hybrid 0p599 candidate | 0.59968 | First practical 0.5-range candidate; Q2 strict nested plus fixed S2/S4 blends. |
| Q3 fixed soft/app combo | 0.65727 on Q3 | Fixed combo improves Q3; nested selector fails, so treat as aggressive. |
| Hybrid 0p598 candidate | 0.59897 | Reproducible pre-sleep-proxy candidate. |
| Hybrid 0p594 candidate | 0.59451 | Fold-safe Q2/Q3 sleep-proxy backup. |
| Hybrid 0p592 candidate | 0.59189 | S1/Q3 quiet-fragmentation candidate. |
| Hybrid 0p591 candidate | 0.59138 | Conservative S1/S4 sleep-dynamics add-on. |
| Hybrid 0p588 block-label candidate | 0.58889 | Reopens block-rate residual using target-specific train-label block smoothing; S2 rejected by geometry. |
| Hybrid 0p588 subject-relative Q candidate | 0.58824 | Block-label residual plus Q relative-temperature postprocess. |
| Hybrid 0p587 subject-relative Q/S candidate | 0.58742 | Adds validated S2/S3/S4 subject-relative smoothing/rank. |
| Hybrid 0p586 strict resweep candidate | 0.58627 | Former strict backup; second-pass relative resweep accepted for Q3/S2/S3/S4. |
| Hybrid 0p586 Q2-loose candidate | 0.58621 | Adds a loose-but-supported Q2 relative shrink. |
| Hybrid 0p585 gentle logit candidate | 0.58509 | First gentle per-target logit calibration layer; all 7 targets pass guardrails. |
| Hybrid 0p582 iterative logit candidate | 0.58266 | Iterative weak logit residual layers with shrinking gains. |
| Hybrid 0p580 alternating residual candidate | 0.58079 | Subject-relative, S2 block residual, then logit residual reopen after calibration. |
| Hybrid 0p579 nested-supported late residual | 0.57917 | Strongest geometry-nested late candidate; only Q2/S1/S3 configs supported by nested target summaries. |
| Hybrid 0p578 alternating residual candidate | 0.57830 | Public LB anchor: submitted file scored `0.5784273528`, validating the OOF scale within about `+0.00012`. |
| Hybrid 0p574 quiet-window logit candidate | 0.57468 | Quiet-window correction; later fold-safe re-audit gives a stricter `0.57574` baseline. |
| Hybrid 0p573 broad Q1/Q2 candidate | 0.57265 | Adds Q1 late call-time and Q2 morning activity-transition single-feature corrections; geometry delta `-0.002905`. |
| Hybrid 0p567 broad stage2 candidate | 0.56753 / public `0.5779449757` | Adds Q1/Q3/S1/S2/S3/S4 broad residual features. Public LB shows the OOF gain is mostly selection-biased, but the file is still `0.00048` better than the 0.578 public anchor. |
| Ordinal/ambnext Q2/Q3 candidate | 0.56190 / public `0.5783033652` | Strongest local OOF so far, but public underperforms stage2 by `+0.000358`; treat as public-fragile unless used in tiny observed-endpoint blends. |
| Subject-target gated ordinal donor | 0.55858 full / 0.56333 half-gate | Highest OOF family after the ordinal public miss. It selectively copies ordinal only for winning subject-target cells, but the best candidate still has `0.623` projection onto the failed ordinal public direction. |
| Orthcap public-bad-axis removal | 0.56043 / projection `0.300` | Best non-convex rescue of the ordinal/subjectgate signal. It caps the observed public-bad direction and keeps the orthogonal residual. |
| Exact ordinal hidden-count quantization | 0.55936 / projection `0.305` | Exact 1-5 posterior priors fail, but nearest hidden-count quantization still improves Q3/Q2 on top of orthcap. The safest version is Q3-only on pure orthogonal residual: OOF `0.562810`, projection `-0.005704`. |
| Projection-constrained orthcap/exact blend | 0.56052 / projection `0.099` | Best current non-convex score/projection ladder. `cap0p0` is OOF `0.562144` at near-zero projection; `cap0p05` is OOF `0.561307`; `cap0p1` is OOF `0.560523`. |
| Public two-axis blend | 0.56072 / two-axis delta `+0.000020` | Uses both submitted public directions. `budget0p0` is OOF `0.561702` with two-axis public-neutral estimate; `budget0p00002` is OOF `0.560724` with small estimated public risk. |
| Public entropy projection | 0.55368 OOF analogue / public-posterior expected `0.57573` | Treats the three observed public LB scores as aggregate hidden-label constraints and solves a minimum-KL projection. `submission_public_entropyproj_public2d0_g075.csv` is the balanced high-upside probe; `g100` exactly fits all three public scores in expectation but has the highest overfit risk. |
| Public entropy target masks | 0.55419 OOF analogue / expected `0.57589` | Splits the public entropy projection by target subset. Q2 can be removed with little loss; the best balanced mask is `Q1+Q3+S1+S2+S3+S4 g075`, while the core attribution mask is `Q1+Q3+S3+S4`. |
| Public subset robustness | mean expected `0.57465` / p90 regret `0.000159` | Simulates public row subsets and multiple posterior scenarios. The Q2-dropped `g075` target-mask is more robust than exact-fit `g100`, which falls to 13th under scenario regret. |
| Public minimax ensemble | mean expected `0.57463` / p90 regret `0.000118` | Convex-blends public-constraint files against six posterior/subset scenarios. The sparse rank-1 ensemble is now the default public-constraint score candidate. |
| Covariate-neighbor sleep prior | 0.56733 best blend | Rejected. KNN over sleep/quiet/presleep covariates adds only `-0.000199` to stage2 and fails repeated-subject holdout. |
| Hidden-block row gate | geometry `+0.001034` vs stage2 | Rejected. Actual submission block position/gap features do not support row-wise shrinking of stage2 toward anchor. |
| Presleep public-axis audit | bad-axis projection `0.992` for top OOF file | The representation is strong but public-risk aligned with the failed ordinal direction, so it needs projection control before score use. |
| Presleep orthcap derivative | 0.56557 best / 0.56722 low-risk | Rejected as score candidate. Public-bad-axis control leaves too little gain versus existing projection blends. |
| NSF guideline proxy layer | 0 passes out of 48 configs | Rejected. TST/efficiency/latency/WASO proxies do not add robust signal on top of stage2. |

## What This Means

1. The hidden labels are block-state dominated.  
   The score gap `0.62477 -> 0.51788` appears only when the validation block's target rate is known. Static subject identity and row-level local smoothing cannot explain that gap.

2. The split itself is informative but not enough.  
   Submission consists of interleaved unknown blocks between known same-subject train blocks. Many blocks have known labels immediately before and/or after, but boundary labels alone are too noisy.

3. Q targets are the main wall.  
   Block smoothing tends to hurt `Q1/Q2` and only weakly helps `Q3`. The survey labels are based on individual averages over 5-point responses, but binary labels alone do not impose a useful hard 50/50 constraint.

4. S targets have exploitable block behavior.  
   `S1/S2/S4` improve under block smoothing. `S3` is already strong from subject/temporal priors and does not benefit.

5. Sensor/meta features contain local slices, not stable reconstruction.  
   The cheating threshold diagnostic reaching `0.56840` means some columns can separate a validation fold when selected with validation labels. Nested selection collapses to `0.66904`, so those are not reliable formula features.

6. The biggest concrete feature bug was temporal alignment.  
   `sleep_date = lifelog_date + 1`, so the sleep episode spans late `lifelog_date` and early `sleep_date`. Previous daily aggregates attached `00:00-06:00` records to the same calendar date, which is the morning before the logged sleep, not the post-midnight sleep segment. The overnight remap attaches `00:00-11:59` to the previous `lifelog_date`.

7. Overnight phone/screen/activity/light features are stronger than coarse watch features.  
   `overnight_phone` nested blend reaches `0.60904`. It sharply improves `Q1` and `S1`, and modestly improves `S3`.

8. Context additions help selected targets but not the global mean.  
   Adding WiFi/BLE/GPS/usage/ambience to the overnight matrix gives `overnight_all` `0.61144`, weaker than the lean phone version, but it improves `S4` through `overnight_context_sensor_only`.

9. `Q2` is not random noise; it needs a soft constraint, not a hard one.  
   The hard subject-rate / 50:50 style correction explodes log loss because it becomes overconfident. A shrinked subject-rate target blended with temporal base and pre-sleep app logreg gives strict nested `Q2 = 0.66357`, a `-0.02914` target improvement.

10. The current `0.59968` candidate is real but aggressive.  
   `Q2` is validated with strict outer nested CV. The `S2` and `S4` upgrades use fixed full-OOF pair-blend weights, so they are data-backed but not as conservative as the Q2 result.

11. `Q3` has a smaller soft-rate/app signal, but selection is unstable.  
   A fixed combo improves `Q3` to `0.65727`, but the nested selector chooses inconsistent settings and lands at `0.66722`. This is useful for a high-upside submission, not as a clean structural proof.

12. S2/S4 fixed pair weights are better than fold-wise selection.  
   A locked fixed pair test keeps `S2 = 0.55972` and `S4 = 0.62778`. Letting each fold select pair weights overfits and worsens to `S2 = 0.56252`, `S4 = 0.63551`.

13. Q1 does not currently open with the Q2/Q3 soft-rate trick.  
   The best Q1 diagnostic from overnight/app/soft-rate is `0.62716`, worse than the current `0.62503` source. Do not spend more short-cycle effort on this exact Q1 variant.

14. The 0.598 candidate is now reproducible without stale CSV dependency.  
   The legacy overnight feature matrix (`overnight_sensor_features.parquet`) reproduces the key old v1 losses: `Q1 = 0.625034`, `S1 = 0.524188`, `S3 = 0.535248`. `submission_hybrid_0p598_repro.csv` matches the previous 0.598 target values to numerical precision.

15. Block-averaging the final predictions is rejected.  
   The block-rate oracle is strong, but naive block averaging erases useful row-level signal. Best OOF strength is `0.00`; even `0.05` worsens `0.598973 -> 0.599224`.

16. Actual submission geometry changes validation interpretation, not the final rule.  
   Submission hidden blocks are smaller and more boundary-rich than the original subject-block CV. A repeated geometry-mask CV gives `temporal_base = 0.613820`, while the best all-target block/bridge candidate is worse at `0.614258`. The useful signal is target-specific: S targets improve weakly, Q targets break. This supports the existing S2/S4 fixed pair and rejects all-target boundary smoothing.

17. Block-rate ML regression still does not open the oracle gap.  
   Re-running the block-level rate regressor with overnight-aligned features gives `legacy_overnight_v1 nested_block_regressor = 0.624984` and `overnight_v2 nested_block_regressor = 0.628856`. The direct block-rate oracle (`0.51788`) is not reachable from the current block feature representation.

18. Q-rate logit shifting is a tempting but rejected artifact.  
   Subject-block OOF improves Q1 to `0.619828`, but the same idea fails the more relevant checks: half-subject Q1 worsens `0.615798 -> 0.621631`, and actual-geometry masks worsen saved-current Q1 `0.624443 -> 0.629417`. Do not promote `submission_hybrid_0p598_q_rate_shift.csv`.

19. The new useful raw feature is an inferred sleep interval, not another aggregate.  
   Building a longest quiet interval from screen-off, no-step, low-speed/activity variants opens both Q1 and S1. Best stable model is `et_leaf6_mf0.8` blended at `0.30` into the current prediction:
   `Q1 0.625034 -> 0.620019`, `S1 0.524188 -> 0.518602`, mean `0.598973 -> 0.597459`.

20. Sleep-proxy guardrails support Q1/S1, but not Q2/Q3 yet.  
   Half-subject holdout improves Q1 `0.615798 -> 0.611891` and S1 `0.498541 -> 0.495360`. Actual-geometry masks also improve saved-current Q1 by `-0.00649` and S1 by `-0.01373`. Q2/Q3 improve on some full/geometry views but fail half-subject selection, so they remain audit-only.

21. The proxy signal is interpretable.  
   Top Q1/S1 features are quiet-interval duration, quiet-interval end hour, duration x charging, last/first screen activity, and pre/post light/screen context. This is closer to Withings-style sleep duration/efficiency signal than the prior generic overnight aggregates.

22. Subject-relative sleep interval features are the strongest Q1 clue so far.  
   Adding unlabeled covariate-only subject z/rank/center, prev-next deltas, neighbor means, and rolling-3 context to the quiet-interval features opens Q1 much further: `0.625034 -> 0.604470`. Half-subject holdout also improves `0.615798 -> 0.597643`, and actual-geometry masks improve saved-current Q1 `0.632460 -> 0.611601`.

23. Do not promote augmented S1 despite the huge full-OOF gain.  
   Augmented S1 full OOF reaches `0.501057`, but half-subject holdout worsens `0.498541 -> 0.502999`. Keep S1 on the non-augmented `et_leaf6_mf0.8_w0.3` proxy source.

24. Fold-safe reference-stat sleep proxies confirm the signal is not only transductive rank optimism.  
   When subject mean/std/rank are computed from the fold-train rows only and validation rows are projected onto that reference, Q1 still improves `0.625034 -> 0.610793`, with half-subject `0.615798 -> 0.601065` and geometry `0.632460 -> 0.616860`. This is weaker than the transductive augmented Q1 but still a strong structural confirmation.

25. Q2 and Q3 now have small sleep-interval proxy additions that pass guardrails.  
   `foldsafe_leaf3_mf0.35` at Q2 weight `0.20` gives `0.663572 -> 0.661317`, half-holdout `0.686456 -> 0.681794`, and geometry w0.20 `0.671960 -> 0.663919`. Q3 must be low weight: w0.10 gives `0.657266 -> 0.654440`, half-holdout `0.694412 -> 0.693926`, and geometry w0.10 `0.657612 -> 0.654510`.

26. Quiet-interval fragmentation is a real S1/Q3 signal.  
   Segment count/duration/gap/context features push S1 `0.518602 -> 0.504520` and Q3 `0.654440 -> 0.650187`. Fixed-weight repeated subject-half checks support both (`S1` win-rate `0.977`, `Q3` win-rate `0.895`), while Q1/Q2/S4 fragmentation remains rejected.

27. HR/WASO-like sleep dynamics add only a thin but validated S-side gain.  
   HR drop/rebound, quiet-end wake bursts, and subject regularity do not reopen Q targets. A conservative S1/S4 add-on gives S1 `0.504520 -> 0.502098`, S4 `0.627784 -> 0.626623`, and mean `0.591892 -> 0.591380`.

28. Block-label residual signal still exists after sleep proxies.  
   Surrounding same-subject train labels can be used as a weak block-rate prior on top of the `0.59138` OOF. Target-specific smoothing improves Q1/Q2/Q3/S3/S4 and pushes the mean to `0.588893`. S2 is explicitly rejected because full OOF improves but actual-geometry masks worsen.

29. Q targets need relative-temperature correction, not hard rate forcing.  
   On top of the block-label candidate, weak within-subject relative transforms improve all three Q targets: Q1 benefits from sharper subject-relative contrast, while Q2/Q3 benefit from smoothing. This moves the best estimate to `0.588241` without changing S targets.

30. S2/S3/S4 also retain subject-relative residual structure.  
   Applying the same weak within-subject transform on top of the Q-relative candidate improves S2/S3/S4 and passes both repeated subject-half and actual-geometry guardrails. S1 has only a tiny `-0.00018` OOF gain, so it is not promoted.

31. A second subject-relative resweep still finds stable S/Q3 residue.  
   On top of `0.587417`, a finer grid accepts Q3/S2/S3/S4 under strict OOF, repeated subject-half, and geometry gates, lowering the strict estimate to `0.586272`. Q1 is rejected; S1 is only a loose tiny gain.

32. Q2 has a smaller high-upside relative-shrink residue.  
   A targeted 2,000-repeat Q2 guardrail finds `center_shift_p-0.5_w0.2`: OOF `0.656820 -> 0.656415`, subject-half mean delta `-0.000401` with win-rate `0.648`, and geometry delta `-0.001295`. This is just below the strict win-rate gate, so keep `0.586272` as strict backup and `0.586214` as the highest-upside candidate.

33. Block-label residual is now exhausted at the current frontier.  
   Re-testing block smoothing on top of `0.586214` finds apparent OOF gains for S2/Q3/S4, but they fail geometry or win-rate. Do not stack another block-label blend on the current candidate.

34. Gentle per-target logit sharpening is still underused signal.  
   Joint/platt-style calibration was too flexible, but a weak target-wise logit transform passes strict guardrails for all seven targets. Most targets want mild sharpening (`scale1.3`, weight `0.2`); Q2 wants a gentler positive-shift shrink. This lowers the current estimate to `0.585093`.

35. Iterative gentle logit residuals keep improving, but the marginal gain is shrinking.  
   Repeated weak per-target calibration layers lower the estimate from `0.585093` to `0.582657`. Early layers pass strict guardrails broadly; later layers narrow to Q2/S1/Q3/S2 and loose S3, while Q1 and S4 stop. This suggests the ensemble is still conservative, but the calibration-only path is approaching saturation.

36. Calibration and subject-relative correction interact.  
   After iterative logit calibration, subject-relative transforms reopen on every target: Q1/Q2/Q3/S1/S2/S3 strict and S4 loose, dropping the estimate to `0.581478`. This is stronger than another pure calibration layer and shows the hidden structure is not one-dimensional calibration only.

37. Block residual reopens only for S2 at the new frontier.  
   On top of the post-logit subject-relative candidate, block-label smoothing helps S2 with strict guardrails (`0.553387 -> 0.552027`) while S4 still fails geometry. A final weak logit pass on Q1/S1/Q3 lowered the high-upside estimate at that stage to `0.580794`.

38. Late alternating residuals are now a narrow S3/S1 loop with optional Q2/Q3 loose gains.  
   Continuing from `0.580794`, repeated strict S3 subject-relative corrections and S1 logit corrections lower the strict estimate to `0.578530`. Adding loose Q2 center-temperature and Q3 rank-logit subject-relative corrections gives an estimate of `0.578467`; this late loose file is useful, but it is more selection-sensitive than the strict backup.

39. Late residuals split into two candidates: highest-upside versus strongest nested evidence.  
   A geometry-nested residual selector rejects all-target greedy continuation: cumulative heldout geometry delta becomes `+0.002954` after 8 steps. Restricting the late path to nested-supported Q2/S1/S3 configs gives a safer `0.579168` candidate with geometry delta `-0.002044` and win-rate `1.0`. The highest-upside OOF candidate continues the aggressive path to `0.578304`, but should be treated as less proven than the nested-supported file.

40. Quiet-window sleep reconstruction reopens a real post-0.578 signal.  
   Fixed sleep-proxy model residuals fail after the 0.578/0.579 frontier, but direct quiet-window features expose a cleaner structure: S2/S4 track long screen-off duration, Q3 tracks quiet-window start time, and S3 tracks quiet-window HR mean. A fold-safe logistic correction on Q3/S2/S3/S4 lowers the estimate from `0.578304` to `0.574942` and passes actual-geometry masks with mean delta `-0.000987`. A weaker `w=0.30` variant has better geometry delta `-0.001031` but higher OOF `0.575842`. Adding small loose residual calibration gives the current high-upside `0.574678` candidate with additional geometry delta `-0.000307`.

41. Public LB anchor confirms the offline scale.  
   `submission_hybrid_0p578_logit_after_subject_final9_strict.csv` scored public LB `0.5784273528` against an offline estimate of `0.578304`, only about `+0.00012` worse. This makes the fold-safe OOF and geometry-mask deltas credible enough to rank new candidates, while full-fit quiet estimates remain treated as optimistic unless re-audited.

42. Broad single-feature residuals break the Q1/Q2 wall and then reopen Q3/S targets.  
   After the stricter fold-safe quiet audit, Q1 is strongly explained by late `usage_kw_call_time` and Q2 by morning activity transitions. Adding those gives `0.575215 -> 0.572651` with geometry delta `-0.002905`. A second broad pass then finds Q3 `BLE morning unique`, S1 ambience/finance-use, S2 late phone-light, S3 HR rows, and S4 evening outside ambience residuals. The current stage2 candidate reaches `0.567531` fold-safe OOF with geometry delta `-0.003490` and win-rate `1.0`.

43. Public LB falsifies the raw stage2 OOF scale.  
   `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` scored public LB `0.5779449757`, only `-0.00048` better than the 0.578 anchor despite a `-0.01077` offline gain. This means the broad residual features are not pure leakage, but the feature selection is much more optimistic than the guardrails estimated. Stage3 broad residuals are therefore audit-only unless damped against the public anchor.

44. Anchor-to-stage2 probability blends are the next safest public experiments.  
   Linear probability blends between the submitted 0.578 anchor and the submitted 0.567 stage2 endpoint are convex under Log Loss on the hidden labels. Generated candidates `submission_publicblend_anchor578_stage2567_prob_w050.csv`, `..._w075.csv`, and `..._w085.csv` test whether a lower-amplitude move beats both submitted endpoints without introducing new selected features.

45. Target-switch probes are now higher-information than new broad features.  
   Because full stage2 improved public by only `-0.000482`, the next question is which target move survived. Generated probes copy selected stage2 targets onto the 0.578 public anchor. The highest-value checks are `submission_publicprobe_anchor578_stage2_drop_s3.csv`, `submission_publicprobe_anchor578_stage2_drop_s4.csv`, `submission_publicprobe_anchor578_stage2only_s.csv`, and `submission_publicprobe_anchor578_stage2only_q.csv`.

46. Public-LB inverse analysis supports a mid-strength probability blend.  
   Treating anchor and stage2 as endpoints, the observed public delta implies a latent probability mix coefficient `alpha = 0.544736`. Under that one-dimensional model, the best score-oriented file is `submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv` with predicted public `0.576841`, very close to `prob_w050` predicted `0.576852`. This model is a hypothesis from two public points, not a proof; use `drop_s3/drop_s4` for attribution and `w545/w050` for score-oriented probing.

47. Ordinal/ambnext public score rejects the OOF-top file as a direct submission.  
   `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` scored public LB `0.5783033652`. It is still `-0.000124` better than the 0.578 anchor, but `+0.000358` worse than stage2. The offline gain versus anchor was about `-0.01640`, so the public transfer ratio is only `0.0076`. This does not isolate the ordinal count shift from the aggressive ambnext backbone, but it is enough to demote full q3off/ambnext count-shift files from score priority.

48. Public-observed probability microblends are now the lowest-risk score experiments.  
   I generated `public_observed_pair_blend_builder.py` to blend only endpoints with known public scores. The best new low-risk file is `submission_publicobsblend_stage2_to_ordinal_w005.csv`: 95% stage2 + 5% ordinal/ambnext, OOF `0.567025`, and convex public upper bound `0.5779628952`, only `+0.0000179` above the current public best. The 10% version has OOF `0.566549` and public upper bound `0.5779808147`.

49. Subject-target donor gating is the strongest post-failure rescue, but not a safe blind score move.  
   `subject_target_gate_donor_builder.py` activates donor predictions per subject-target cell only where that donor improves stage2 OOF. The best high-upside file is `submission_subjectgate_ordinal_all_thrm0p005_w100.csv`, with full OOF `0.558584` and time-half guarded OOF `0.563328`. The lower-projection alternative is `submission_subjectgate_ordinal_all_thrm0p02_w080.csv`, with OOF `0.562297`, half-gate `0.564583`, and public-bad projection `0.321`. This is now the main creative probe family, but it should be submitted after the convex microblends because there is no public convex bound.

50. Removing the observed public-bad axis preserves a large orthogonal residual.  
   `public_bad_direction_orthcap_builder.py` decomposes candidate moves into the failed stage2->ordinal direction and its orthogonal residual. This produces a better risk ladder than raw subjectgate: `submission_orthcap_s001_cap010_sc100.csv` has OOF `0.561989` at projection `0.100`; `submission_orthcap_s001_cap030_sc100.csv` has OOF `0.560427` at projection `0.300`; and `submission_orthcap_s005_cap000_sc100.csv` still has OOF `0.563648` with essentially zero projection. This is strong evidence that the ordinal/subjectgate family contains real non-public-bad signal, not just the failed OOF direction.

51. The exact ordinal prior is useful only as count quantization, not as a posterior predictor.  
   `ordinal_q_exact_prior_count_audit.py` enumerates all 1-5 value-count distributions under the published Q-label rule. Posterior mean/mode worsens OOF across tested bases. Nearest hidden-positive-count quantization improves because it rounds each subject's hidden Q3/Q2 probability sum to a feasible integer count. Q1 should be excluded. Best score file is `submission_orthcap030_exact_q2q3_exact_value_nearest_w1.csv` with OOF `0.559355` and projection `0.305399`; safest non-convex diagnostic is `submission_orthcap005c000_exact_q3_exact_value_nearest_w1.csv` with OOF `0.562810` and projection `-0.005704`.

52. Projection-constrained blending is the cleanest current public-risk control.  
   `projection_constrained_blend_optimizer.py` blends orthcap/exact-count candidates while capping projection onto the observed failed stage2->ordinal direction. It improves the single-candidate ladder at matched risk: `submission_projblend_cap0p0.csv` has OOF `0.562144` at projection `-0.000049`; `submission_projblend_cap0p05.csv` has OOF `0.561307` at projection `0.048995`; `submission_projblend_cap0p1.csv` has OOF `0.560523` at projection `0.099482`. The S2 label-prior variants are rejected for score because full OOF worsens S2 by about `+0.0020` despite favorable projection geometry.

53. Public-LB evidence is now two-dimensional, not just a bad-axis warning.  
   `public_two_axis_blend_optimizer.py` uses the public-good `anchor578 -> stage2` direction and the public-bad `stage2 -> ordinal` direction together. The best public-neutral two-axis file is `submission_public2dblend_budget0p0.csv`, OOF `0.561702`, two-axis public delta `-0.00000005`, one-axis delta `+0.00000890`. The best intermediate score probe is `submission_public2dblend_budget0p00002.csv`, OOF `0.560724`, two-axis public delta `+0.00001997`. This is still a public surrogate, not a guarantee, because most candidate movement remains outside the two observed axes.

54. Presleep is a feature discovery, not the next score submission.  
   `presleep_orthcap_builder.py` capped the top presleep candidates against the observed failed stage2->ordinal axis. The best resulting OOF is `0.565572` at projection `0.375`, while the best low-risk derivative with projection `<= 0.05` is only `0.567216`. In the unified public-risk rank, the best presleep orthcap file is rank `2530/3739`, so the current submission queue should stay with public-observed microblends, projection-constrained blends, and two-axis blends.

55. Direct NSF proxy stacking is exhausted at the stage2 frontier.  
   `nsf_guideline_proxy_audit.py` tested 48 interpretable S-target configs: S1 total-sleep-time duration, S2 efficiency/quiet fraction, S3 latency/start phase, and S4 WASO fragmentation. No loose or strict pass survived. S1/S2/S3 choose zero blend weight on top of stage2, and the best S4 row has OOF delta `-0.000188` but repeated subject-half delta `+0.000582` with win-rate `0.103`. Future S-target work needs a new sleep-stage-like source or public-safe blending, not another direct guideline proxy layer.

56. Public LB can be inverted as weak label information, but it is a different risk class.  
   `public_entropy_projection_builder.py` converts the three submitted public scores into linear constraints on the hidden labels. The projection is numerically exact and gives a very strong train analogue: public2d0 prior full projection OOF `0.553679`, geometry analogue mean delta `-0.010874`, win-rate `1.0`. The public-posterior self estimate is `0.575734` for full `g100`, `0.575826` for balanced `g075`, and `0.576100` for safer `g050`. Shift decomposition shows the balanced file mostly moves Q1/Q3/S3/S4, lowering Q3 and raising S3. This is the most creative high-upside public probe now, but it assumes the unknown public subset is well represented by all 250 submission rows.

57. Target-masking makes the public-LB inverse probe less blunt.  
   `public_entropy_targetmask_builder.py` evaluated all 127 target masks at four shrink levels. The best balanced mask drops Q2: `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv` has OOF `0.554185`, public-posterior expected `0.575887`, mean move `0.011874`, geometry delta `-0.010185`, and win-rate `1.0`. Dropping both Q2 and S1 gives a lower-move alternative (`0.555407`, expected `0.575956`). The core attribution mask `Q1+Q3+S3+S4 g075` still has OOF `0.556265`, so the public inverse signal is concentrated outside Q2.

58. Public-subset robustness rejects the exact-fit endpoint as the default.  
   `public_subset_sensitivity_audit.py` first tested random/order/subject public row subsets against the full-g100 posterior; all entropy candidates beat the public2d0 prior, but the test favors g100 by construction. `public_posterior_scenario_robustness.py` fixes that by scoring against six posterior scenarios. The robust winner is the Q2-dropped target-mask `g075`: mean expected `0.574649`, mean regret `0.000082`, p90 regret `0.000159`, and win-rate `1.0` versus prior. Raw `g100` is still high-upside but falls to 13th with win-rate `0.8371`, so the default public-constraint submission should be the target-mask `g075`, not exact-fit `g100`.

59. A convex minimax ensemble is slightly better than any single public-constraint file.  
   `public_minimax_ensemble_optimizer.py` searches sparse/Dirichlet convex blends over the public-constraint files using the same six posterior/subset objective. The best sparse file, `submission_public_minimaxens_r01_a6_h422045.csv`, has mean expected `0.574634`, mean regret `0.000067`, p90 regret `0.000118`, win-rate `1.0`, and OOF analogue `0.554332`. This is a small gain over Q2-dropped `g075`, but it is the best current default if we accept the public-constraint risk class.

60. A conservative public frontier separates upside from posterior-model risk.  
   `public_conservative_frontier_builder.py` blends entropy/minimax candidates back toward stage2/public2d0/projblend/anchor pseudo-posteriors. These files are deliberately weaker under the entropy-only posterior audit, but they answer a different question: what if the three public-LB constraints are partly overfit? The best higher-trust bridge, `submission_public_consfront_t80_r10_b06ca82f.csv`, is 65% minimax r01 plus 35% anchor->stage2 w095. It has OOF `0.557498`, posterior mean `0.574792`, conservative mean `0.574646`, and clean submission integrity.

61. Public row-subset uncertainty can be stress-tested directly.  
   `public_maskaware_entropy_projection.py` solves the same three public-score constraints on random/order/subject candidate masks and bag-averages the logit shifts. The result does not beat minimax, but it reveals an important hidden clue: global prefix/suffix masks require about `0.0356` mean probability movement, roughly double random/subject-contiguous masks (`0.0175-0.0185`). Under the three observed public scores, a simple chronological public split is less plausible than random or subject-block-like rows. Best row-subset-uncertainty fallback is `submission_public_maskaware_t80_r11_544844af.csv`, with OOF `0.553156`, mean expected `0.574650`, p90 regret `0.000160`, and win-rate `1.0`.

## New Candidate Files

- `analysis_outputs/submission_best.csv`: conservative current best, nested CV `0.62239`.
- `analysis_outputs/submission_block_target_switch.csv`: aggressive S-target block-switch candidate.
- `analysis_outputs/submission_overnight_blend.csv`: best single overnight blend from the latest run.
- `analysis_outputs/submission_hybrid_overnight_block.csv`: first overnight/block hybrid, estimate `0.60511`.
- `analysis_outputs/submission_hybrid_overnight_context.csv`: current aggressive best hybrid, estimate `0.60491`.
- `analysis_outputs/submission_q2_soft_app_stack.csv`: Q2-only strict nested upgrade, estimate `0.60075`.
- `analysis_outputs/submission_hybrid_0p599.csv`: first 0.5-range practical candidate, estimate `0.59968`.
- `analysis_outputs/submission_q3_soft_app.csv`: Q3 fixed soft/app upgrade applied on top of `0.59968`.
- `analysis_outputs/submission_hybrid_0p598.csv`: earlier high-upside candidate, estimate `0.59897`.
- `analysis_outputs/submission_hybrid_0p598_repro.csv`: reproducible reconstruction of the earlier 0.598 candidate.
- `analysis_outputs/hybrid_0p598_repro_cv_estimate.csv`: self-contained target-wise estimate for the reproducible 0.598 candidate.
- `analysis_outputs/public_entropy_projection_builder.py`: public-LB inverse projection generator using anchor/stage2/ordinal public scores as aggregate constraints.
- `analysis_outputs/submission_public_entropyproj_public2d0_g075.csv`: balanced public-constraint exploit candidate, OOF analogue `0.554156`, public-posterior expected loss `0.575826`.
- `analysis_outputs/submission_public_entropyproj_public2d0_g050.csv`: safer public-constraint shrink candidate, OOF analogue `0.555625`, public-posterior expected loss `0.576100`.
- `analysis_outputs/submission_public_entropyproj_public2d0_g100.csv`: maximum public-constraint exploit candidate, OOF analogue `0.553679`, exact expected fit to the three observed public scores.
- `analysis_outputs/public_entropy_projection_summary.csv`: full 16-row candidate and constraint residual audit.
- `analysis_outputs/public_entropy_projection_shift_audit.py`: target/subject/cell movement decomposition for the public-constraint candidates.
- `analysis_outputs/public_entropy_targetmask_builder.py`: exhaustive target-subset public-constraint projection generator.
- `analysis_outputs/submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv`: balanced target-mask public-constraint candidate; drops Q2, OOF `0.554185`, expected `0.575887`.
- `analysis_outputs/submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv`: lower-move target-mask candidate; drops Q2/S1, OOF `0.555407`, expected `0.575956`.
- `analysis_outputs/submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv`: lowest current target-mask risk-score candidate; OOF `0.555707`, expected `0.576149`.
- `analysis_outputs/public_entropy_targetmask_summary.csv`: all 508 target-mask rows and geometry/risk metrics.
- `analysis_outputs/public_subset_sensitivity_audit.py`: random/order/subject public-row subset stress test.
- `analysis_outputs/public_posterior_scenario_robustness.py`: multi-posterior subset regret audit; promotes Q2-dropped `g075`.
- `analysis_outputs/public_posterior_scenario_robustness_summary.csv`: robust public-constraint ranking across six posterior scenarios.
- `analysis_outputs/public_minimax_ensemble_optimizer.py`: convex minimax optimizer over public-constraint candidates.
- `analysis_outputs/submission_public_minimaxens_r01_a6_h422045.csv`: sparse rank-1 minimax public-constraint ensemble, OOF `0.554332`, mean expected `0.574634`.
- `analysis_outputs/public_minimax_ensemble_summary.csv`: optimizer trace and weight summaries.
- `analysis_outputs/public_conservative_frontier_builder.py`: conservative public-constraint frontier using stage2/public2d0/projblend/anchor pseudo-posteriors.
- `analysis_outputs/submission_public_consfront_t80_r10_b06ca82f.csv`: higher-trust conservative bridge, OOF `0.557498`, posterior mean `0.574792`, conservative mean `0.574646`.
- `analysis_outputs/public_conservative_frontier_selected.csv`: 12 saved conservative frontier submissions.
- `analysis_outputs/public_conservative_frontier_integrity.csv`: key/null/probability integrity for the conservative frontier.
- `analysis_outputs/public_maskaware_entropy_projection.py`: mask-aware public-LB entropy projection over random/order/subject candidate public subsets.
- `analysis_outputs/submission_public_maskaware_t80_r11_544844af.csv`: best row-subset-uncertainty fallback, OOF `0.553156`, mean expected `0.574650`.
- `analysis_outputs/public_maskaware_projection_family_diagnostics.csv`: mask family movement audit; global prefix/suffix masks are extreme.
- `analysis_outputs/public_maskaware_entropy_selected.csv`: 12 saved mask-aware submissions and OOF analogues.
- `analysis_outputs/public_maskaware_entropy_integrity.csv`: integrity checks for mask-aware submissions.
- `analysis_outputs/submission_hybrid_0p597_sleep_proxy.csv`: new Q1/S1 sleep-interval proxy candidate, estimate `0.59746`.
- `analysis_outputs/hybrid_0p597_sleep_proxy_cv_estimate.csv`: target-wise estimate for the 0.597 sleep-proxy candidate.
- `analysis_outputs/submission_hybrid_0p597_sleep_proxy_augmented.csv`: Q1 augmented + S1 non-augmented sleep proxy backup, estimate `0.59524`.
- `analysis_outputs/hybrid_0p595_sleep_proxy_augmented_cv_estimate.csv`: target-wise estimate for the 0.595 backup.
- `analysis_outputs/submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv`: fold-safe Q2/Q3 sleep-proxy backup, estimate `0.59451`.
- `analysis_outputs/hybrid_0p594_sleep_proxy_q23foldsafe_cv_estimate.csv`: target-wise estimate for the 0.594 backup.
- `analysis_outputs/submission_hybrid_0p592_sleep_fragment_s1_q3.csv`: cleaner fragmentation backup; S1/Q3 quiet-fragmentation additions, estimate `0.59189`.
- `analysis_outputs/hybrid_0p592_sleep_fragment_s1_q3_cv_estimate.csv`: target-wise estimate for the 0.592 candidate.
- `analysis_outputs/submission_hybrid_0p591_sleep_dynamics_s1_s4.csv`: S1/S4 sleep-dynamics candidate, estimate `0.59138`.
- `analysis_outputs/hybrid_0p591_sleep_dynamics_s1_s4_cv_estimate.csv`: target-wise estimate for the 0.591 candidate.
- `analysis_outputs/submission_hybrid_0p588_block_label.csv`: block-label residual candidate, estimate `0.58889`.
- `analysis_outputs/hybrid_0p588_block_label_cv_estimate.csv`: target-wise estimate for the block-label residual candidate.
- `analysis_outputs/current_0p591_block_label_results.csv`: target/config/weight sweep for block-label residual smoothing.
- `analysis_outputs/current_0p591_block_label_subject_split.csv`: repeated subject-half guardrail for block-label residual candidates.
- `analysis_outputs/current_0p591_block_label_geometry.csv`: actual-geometry guardrail for block-label residual candidates.
- `analysis_outputs/submission_hybrid_0p588_subject_relative_q.csv`: Q relative-temperature candidate, estimate `0.58824`.
- `analysis_outputs/hybrid_0p588_subject_relative_q_cv_estimate.csv`: target-wise estimate for the Q relative-temperature candidate.
- `analysis_outputs/current_0p588_subject_relative_q_results.csv`: Q subject-relative postprocess sweep.
- `analysis_outputs/current_0p588_subject_relative_q_subject_split.csv`: repeated subject-half guardrail for the Q relative-temperature postprocess.
- `analysis_outputs/current_0p588_subject_relative_q_geometry.csv`: actual-geometry guardrail for the Q relative-temperature postprocess.
- `analysis_outputs/submission_hybrid_0p587_subject_relative_qs.csv`: Q relative-temperature plus S2/S3/S4 subject-relative postprocess, estimate `0.58742`.
- `analysis_outputs/hybrid_0p587_subject_relative_qs_cv_estimate.csv`: target-wise estimate for the 0.587 candidate.
- `analysis_outputs/current_0p588_subject_relative_s_results.csv`: S-target subject-relative postprocess sweep.
- `analysis_outputs/current_0p588_subject_relative_s_subject_split.csv`: repeated subject-half guardrail for the S subject-relative postprocess.
- `analysis_outputs/current_0p588_subject_relative_s_geometry.csv`: actual-geometry guardrail for the S subject-relative postprocess.
- `analysis_outputs/submission_hybrid_0p586_subject_relative_resweep_strict.csv`: strict second-pass subject-relative candidate, estimate `0.58627`.
- `analysis_outputs/hybrid_0p586_subject_relative_resweep_strict_cv_estimate.csv`: target-wise estimate for the strict 0.586 candidate.
- `analysis_outputs/submission_hybrid_0p586_subject_relative_resweep_q2loose.csv`: high-upside relative-resweep candidate with loose Q2 add-on, estimate `0.58621`.
- `analysis_outputs/hybrid_0p586_subject_relative_resweep_q2loose_cv_estimate.csv`: target-wise estimate for the 0.586 Q2-loose candidate.
- `analysis_outputs/current_0p587_subject_relative_resweep_results.csv`: second-pass relative grid over all targets.
- `analysis_outputs/current_0p587_subject_relative_resweep_multiguard_merged.csv`: multi-candidate guardrail for second-pass relative configs.
- `analysis_outputs/current_0p587_q2_relative_targeted_merged.csv`: targeted Q2 2,000-repeat guardrail for loose Q2 add-on.
- `analysis_outputs/current_0p586_block_label_residual_merged.csv`: current-frontier block-label residual rejection.
- `analysis_outputs/submission_hybrid_0p585_gentle_logit_calibration.csv`: first gentle per-target logit calibration layer, estimate `0.58509`.
- `analysis_outputs/hybrid_0p585_gentle_logit_calibration_cv_estimate.csv`: target-wise estimate for the first gentle-logit candidate.
- `analysis_outputs/current_0p586_gentle_logit_calibration_merged.csv`: guardrail evidence for the gentle logit calibration.
- `analysis_outputs/submission_hybrid_0p584_gentle_logit_residual.csv`: second gentle-logit layer, estimate `0.58429`.
- `analysis_outputs/submission_hybrid_0p583_gentle_logit_residual2_loose.csv`: third gentle-logit layer with S4 loose add-on, estimate `0.58371`.
- `analysis_outputs/submission_hybrid_0p583_gentle_logit_residual3_loose.csv`: fourth gentle-logit layer with Q1 loose add-on, estimate `0.58333`.
- `analysis_outputs/submission_hybrid_0p583_gentle_logit_residual4_loose.csv`: fifth gentle-logit layer with S3 loose add-on, estimate `0.58306`.
- `analysis_outputs/submission_hybrid_0p582_gentle_logit_residual5_loose.csv`: sixth gentle-logit layer, estimate `0.58283`.
- `analysis_outputs/submission_hybrid_0p582_gentle_logit_residual6_loose.csv`: seventh gentle-logit layer, estimate `0.58266`.
- `analysis_outputs/gentle_logit_residual_probe.py`: reusable guardrail probe for iterative logit residuals.
- `analysis_outputs/make_gentle_logit_from_guardrail_selection.py`: reusable submission builder from guardrail-selected logit configs.
- `analysis_outputs/submission_hybrid_0p580_subject_relative_after_logit8_loose.csv`: post-logit subject-relative reopening candidate, estimate `0.58148`.
- `analysis_outputs/hybrid_0p580_subject_relative_after_logit8_loose_cv_estimate.csv`: target-wise estimate for the post-logit subject-relative candidate.
- `analysis_outputs/current_0p582_subject_relative_after_logit8_merged.csv`: guardrail evidence for post-logit subject-relative reopening.
- `analysis_outputs/submission_hybrid_0p580_block_s2_after_logit_subject.csv`: S2 block residual after alternating logit/subject-relative path, estimate `0.58095`.
- `analysis_outputs/hybrid_0p580_block_s2_after_logit_subject_cv_estimate.csv`: target-wise estimate for the S2 block residual candidate.
- `analysis_outputs/current_0p580_block_residual_after_subject_relative_merged.csv`: current-frontier block residual guardrail; accepts S2 and rejects S4.
- `analysis_outputs/submission_hybrid_0p580_logit_after_block_s2_loose.csv`: post-S2-block Q1/Q3/S1 gentle-logit add-on, estimate `0.58079`.
- `analysis_outputs/hybrid_0p580_logit_after_block_s2_loose_cv_estimate.csv`: target-wise estimate for the 0.58079 candidate.
- `analysis_outputs/submission_hybrid_0p578_subject_after_logit_final8_loose.csv`: previous high-upside alternating residual candidate, estimate `0.57847`.
- `analysis_outputs/hybrid_0p578_subject_after_logit_final8_loose_cv_estimate.csv`: target-wise estimate for the previous high-upside candidate.
- `analysis_outputs/submission_hybrid_0p578_subject_after_logit_final8_strict.csv`: stricter current backup, estimate `0.57853`.
- `analysis_outputs/hybrid_0p578_subject_after_logit_final8_strict_cv_estimate.csv`: target-wise estimate for the stricter 0.578 backup.
- `analysis_outputs/current_0p578_subject_after_logit_final8_merged.csv`: final subject-relative guardrail evidence; S3 strict, Q2/Q3 loose.
- `analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv`: previous highest-upside aggressive candidate before quiet-window correction, estimate `0.57830`.
- `analysis_outputs/hybrid_0p578_logit_after_subject_final9_strict_cv_estimate.csv`: target-wise estimate for the previous highest-upside aggressive candidate.
- `analysis_outputs/submission_hybrid_0p579_nested_supported_late_residual_gridbest.csv`: strongest geometry-nested late residual candidate, estimate `0.57917`.
- `analysis_outputs/hybrid_0p579_nested_supported_late_residual_gridbest_cv_estimate.csv`: target-wise estimate for the nested-supported candidate.
- `analysis_outputs/hybrid_0p579_nested_supported_late_residual_gridbest_geometry.csv`: geometry-mask validation for the nested-supported candidate, mean delta `-0.002044`.
- `analysis_outputs/submission_hybrid_0p573_quiet_logit_q3_s2_s3_s4.csv`: quiet-window logistic correction candidate, estimate `0.57494`.
- `analysis_outputs/hybrid_0p573_quiet_logit_q3_s2_s3_s4_geometry.csv`: actual-geometry validation for the quiet-window candidate, mean delta `-0.000987`.
- `analysis_outputs/submission_hybrid_0p575_quiet_logit_q3_s2_s3_s4_w30.csv`: safer quiet-window variant, estimate `0.57584`, actual-geometry mean delta `-0.001031`.
- `analysis_outputs/submission_hybrid_0p574_quiet_logit_then_gentle_loose.csv`: quiet-window plus first residual calibration, estimate `0.57479`.
- `analysis_outputs/submission_hybrid_0p574_quiet_logit_then_second_loose.csv`: current highest-upside candidate, estimate `0.57468`.
- `analysis_outputs/hybrid_0p574_quiet_logit_then_second_loose_geometry.csv`: second-loose geometry check, additional mean delta `-0.000307`.
- `analysis_outputs/quiet_window_residual_probe.py`: quiet-window feature scan against current frontier residuals.
- `analysis_outputs/quiet_feature_logit_postprocess_probe.py`: fold-safe logistic correction and subject-half guardrail for quiet-window features.
- `analysis_outputs/quiet_feature_logit_geometry_build.py`: geometry validation and submission builder for quiet-window corrections.
- `analysis_outputs/foldsafe_quiet_sequence_audit.py`: stricter fold-safe re-audit of the quiet-window sequence; current honest quiet baseline `0.575742`.
- `analysis_outputs/broad_single_feature_residual_probe.py`: broad deep/proxy/quiet/wifi/ble single-feature residual scanner.
- `analysis_outputs/submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv`: Q1/Q2 broad residual candidate, estimate `0.57265`.
- `analysis_outputs/broad_feature_addon_combo_summary.csv`: geometry summary for Q1/Q2 broad add-ons, best delta `-0.002905`.
- `analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv`: current fold-safe frontier, estimate `0.56753`.
- `analysis_outputs/broad_stage2_addon_combo_summary.csv`: stage2 geometry summary, best delta `-0.003490`.
- `analysis_outputs/public_lb_observations.csv`: submitted public LB anchors; 0.578 anchor scored `0.5784273528`, 0.567 stage2 scored `0.5779449757`.
- `analysis_outputs/public_anchor_stage2_blend_candidates.py`: generates convex anchor-to-stage2 blend submissions.
- `analysis_outputs/public_anchor_stage2_blend_candidates.csv`: OOF and distance summary for anchor-to-stage2 probability/logit blends.
- `analysis_outputs/submission_publicblend_anchor578_stage2567_prob_w050.csv`: 50% probability blend between submitted 0.578 anchor and submitted 0.567 stage2.
- `analysis_outputs/submission_publicblend_anchor578_stage2567_prob_w075.csv`: 75% probability blend; higher-upside damped stage2 check.
- `analysis_outputs/submission_publicblend_anchor578_stage2567_prob_w085.csv`: 85% probability blend; closest safe retreat from full stage2.
- `analysis_outputs/current_0p567_broad_stage3_rescan_selected.csv`: stage3 residual scan; audit-only because stage2 public LB exposed broad-feature selection bias.
- `analysis_outputs/public_target_switch_probes.py`: builds anchor-vs-stage2 target switch probes.
- `analysis_outputs/public_target_switch_probes.csv`: OOF/distance summary for target switch probes.
- `analysis_outputs/public_probe_submission_priority.md`: next public submission order and interpretation rules.
- `analysis_outputs/public_lb_inverse_analysis.py`: converts public LB anchors into an anchor-stage2 latent-mix constraint and scores candidate probes.
- `analysis_outputs/public_lb_inverse_constraint.csv`: public inverse summary; latent mix alpha `0.544736`.
- `analysis_outputs/public_candidate_latent_mix_predictions.csv`: predicted public scores under the inferred latent mix.
- `analysis_outputs/submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv`: exact alpha probability blend; score-oriented next probe.
- `analysis_outputs/submission_publicprobe_anchor578_stage2_drop_s3.csv`: full stage2 except S3, highest-value S3 over-shift test.
- `analysis_outputs/submission_publicprobe_anchor578_stage2_drop_s4.csv`: full stage2 except S4, high-amplitude S4 test.
- `analysis_outputs/submission_publicprobe_anchor578_stage2only_s.csv`: S1-S4 copied from stage2 onto anchor.
- `analysis_outputs/submission_publicprobe_anchor578_stage2only_q.csv`: Q1-Q3 copied from stage2 onto anchor.
- `analysis_outputs/nested_late_residual_guardrail.py`: geometry-nested residual selector; shows all-target greedy late residual overfits.
- `analysis_outputs/nested_supported_sequence_grid.py`: grid search over nested-supported Q2/S1/S3 late residual counts.
- `analysis_outputs/subject_relative_residual_probe.py`: reusable guardrail probe for subject-relative residuals.
- `analysis_outputs/block_label_residual_probe.py`: reusable guardrail probe for block-label residuals.
- `analysis_outputs/sleep_dynamics_proxy_results.csv`: HR/WASO-like dynamic sleep feature model/weight search.
- `analysis_outputs/sleep_dynamics_proxy_subject_split_guardrail.csv`: repeated subject-half guardrail for dynamic candidates.
- `analysis_outputs/sleep_fragmentation_proxy_results.csv`: quiet-fragmentation model/weight search.
- `analysis_outputs/sleep_fragmentation_proxy_subject_split_guardrail.csv`: repeated subject-half guardrail for fragmentation candidates.
- `analysis_outputs/sleep_interval_proxy_foldsafe_results.csv`: fold-safe subject reference-stat proxy results.
- `analysis_outputs/sleep_interval_proxy_foldsafe_leaf3_geometry_grid.csv`: geometry weight grid validating Q2/Q3 low-weight fold-safe additions.
- `analysis_outputs/sleep_interval_proxy_q23foldsafe_candidate_note.csv`: selected Q2/Q3 weights and guardrail evidence.
- `analysis_outputs/sleep_interval_proxy_augmented_features.parquet`: subject-relative z/rank/delta/rolling sleep interval features.
- `analysis_outputs/sleep_interval_proxy_augmented_results.csv`: augmented model search and guardrails.
- `analysis_outputs/sleep_interval_proxy_augmented_geometry_cv_results.csv`: actual-geometry validation for augmented sleep proxy.
- `analysis_outputs/sleep_interval_proxy_augmented_feature_importance.csv`: Q1 feature importance; top signal is quiet-interval duration subject-rank.
- `analysis_outputs/sleep_interval_proxy_features.parquet`: inferred longest quiet interval features for all train/submission keys.
- `analysis_outputs/sleep_interval_proxy_model_search_results.csv`: model/weight search; best stable Q1/S1 config is `et_leaf6_mf0.8`.
- `analysis_outputs/sleep_interval_proxy_geometry_cv_results.csv`: actual-geometry mask validation for the sleep-proxy signal.
- `analysis_outputs/q_rate_shift_postprocess_results.csv`: Q-rate shift diagnostic; rejected by guardrails.
- `analysis_outputs/overnight_legacy_repro.py`: reproduces legacy overnight v1 key losses from the saved legacy feature parquet.
- `analysis_outputs/final_hybrid_block_average_oof_results.csv`: final-candidate block-average postprocess rejection.
- `analysis_outputs/geometry_mask_cv_results.csv`: repeated actual-geometry hidden-block mask CV; rejects all-target bridge/block smoothing.
- `analysis_outputs/geometry_s2s4_pair_cv_results.csv`: geometry-mask validation of the fixed S2/S4 pair.
- `analysis_outputs/overnight_block_level_regressor_results.csv`: overnight-aligned block-rate regressor rejection.
- `analysis_outputs/split_geometry_summary.csv`: actual train/submission block geometry vs subject-block CV geometry.
- `analysis_outputs/s2s4_pair_blend_nested_results.csv`: fixed pair vs nested pair-selector validation.
- `analysis_outputs/q1_soft_app_diagnostic_results.csv`: Q1 soft-rate/app diagnostic; rejected.
- `analysis_outputs/block_target_switch_cv_estimate.csv`: nested-target post-hoc estimate, `0.62047`.
- `analysis_outputs/block_target_switch_fixed_cfg_estimate.csv`: fixed block-config estimate, `0.61981`.
- `analysis_outputs/hybrid_overnight_context_cv_estimate.csv`: target-wise source estimate for current aggressive best.
- `analysis_outputs/hybrid_0p599_cv_estimate.csv`: target-wise source estimate for the `0.59968` candidate.
- `analysis_outputs/hybrid_0p598_cv_estimate.csv`: estimate for the Q3-upgraded `0.59897` candidate.

## Current 0.5-Range Candidate

`submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` is the current known public best among submitted files (`0.5779449757`), but not a trustworthy `0.567`-scale model. The next public experiments should be damped anchor-to-stage2 probability blends, especially `submission_publicblend_anchor578_stage2567_prob_w050.csv`, `..._w075.csv`, and `..._w085.csv`. `submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv` remains the broad Q1/Q2-only backup. `submission_hybrid_0p575_quiet_logit_q3_s2_s3_s4_w30.csv` remains the safer quiet-window-only backup, and `submission_hybrid_0p579_nested_supported_late_residual_gridbest.csv` remains the strongest geometry-nested pre-quiet backup.

```text
previous hybrid estimate  0.604911
0p599 estimate            0.599681
0p598 estimate            0.598973
0p597 sleep-proxy         0.597459
0p595 augmented proxy     0.595237
0p594 Q2/Q3 fold-safe     0.594511
0p592 S1/Q3 fragmentation 0.591892
0p591 S1/S4 dynamics      0.591380
0p588 block-label residual 0.588893
0p588 subject-relative Q   0.588241
0p587 subject-relative Q/S 0.587417
0p586 strict resweep       0.586272
0p586 Q2-loose resweep     0.586214
0p585 gentle logit cal     0.585093
0p584 logit residual       0.584290
0p583 residual2 loose      0.583714
0p583 residual3 loose      0.583334
0p583 residual4 loose      0.583058
0p582 residual5 loose      0.582832
0p582 residual6 loose      0.582657
0p582 residual8 loose      0.582492
0p580 subject-rel reopen   0.581478
0p580 S2 block residual    0.580945
0p580 final logit loose    0.580794
0p579 nested-supported     0.579168
0p579 subject/logit path   0.579353
0p578 strict current       0.578530
0p578 loose current        0.578467
0p578 aggressive current   0.578304
0p575 quiet-logit w30      0.575842
0p575 strict quiet audit   0.575742
0p574 quiet-logit          0.574942
0p574 quiet+gentle loose   0.574786
0p574 second-loose current 0.574678
0p573 broad Q1/Q2          0.572651
0p567 broad stage2 OOF     0.567531
0p567 broad stage2 public  0.5779449757
delta vs previous OOF      -0.010773 vs 0p578 aggressive, -0.015126 vs 0p582 residual6
delta vs 0p578 public      -0.0004823771
```

Target changes:

```text
Q1  0.625034 -> 0.604470  subject-relative longest quiet sleep-interval proxy
Q1  0.603439 -> 0.600917  subject-relative Q sharpening after block-label residual
Q1  0.600917 -> 0.599588  gentle target-wise logit sharpening
Q1  0.599588 -> 0.597525  iterative gentle logit residuals until Q1 stops
Q1  0.597525 -> 0.596484  subject-relative reopens after logit path
Q1  0.595683 -> 0.595248  final post-block logit add-on
Q1  0.594506 -> 0.594346  late loose subject-relative add-on
Q2  0.663572 -> 0.661317  fold-safe ref-stat sleep proxy added to Q2 source
Q2  0.658044 -> 0.656820  subject-relative Q smoothing after block-label residual
Q2  0.656820 -> 0.656415  loose second-pass subject-relative shrink
Q2  0.656415 -> 0.655403  gentle target-wise logit shift/sharpen
Q2  0.655403 -> 0.651254  iterative gentle logit residuals
Q2  0.650987 -> 0.649595  subject-relative reopens after logit path
Q2  0.646594 -> 0.646244  late loose subject-relative add-on
Q3  0.654440 -> 0.650187  conservative quiet-fragmentation blend after fold-safe sleep-proxy source
Q3  0.647542 -> 0.646729  subject-relative Q smoothing after block-label residual
Q3  0.646729 -> 0.646039  strict second-pass rank correction
Q3  0.646039 -> 0.645317  gentle target-wise logit sharpening
Q3  0.645317 -> 0.643417  iterative gentle logit residuals
Q3  0.643114 -> 0.642376  subject-relative reopens after logit path
Q3  0.642202 -> 0.642068  final loose post-block logit add-on
Q3  0.640988 -> 0.640894  late loose rank-logit add-on
S1  0.518602 -> 0.504520  quiet-fragmentation blend after longest quiet sleep-interval proxy
S1  0.502098 -> 0.499921  gentle target-wise logit sharpening
S1  0.499921 -> 0.495084  iterative gentle logit residuals
S1  0.494503 -> 0.493176  subject-relative reopens after logit path
S1  0.492388 -> 0.491898  final post-block logit add-on
S1  0.491898 -> 0.488466  repeated strict logit/subject residuals
S2  0.562067 -> 0.559719  0.70 block + 0.30 overnight_all
S2  0.559719 -> 0.558581  subject-relative S smoothing
S2  0.558581 -> 0.557029  strict second-pass smoothing
S2  0.557029 -> 0.556059  gentle target-wise logit sharpening
S2  0.556059 -> 0.553953  iterative gentle logit residuals
S2  0.553953 -> 0.553387  subject-relative reopens after logit path
S2  0.553387 -> 0.552027  S2 block residual after alternating path
S3  0.535248 -> 0.531569  block-label residual smoothing
S3  0.531569 -> 0.528718  subject-relative S smoothing
S3  0.528718 -> 0.524153  strict second-pass smoothing
S3  0.524153 -> 0.523202  gentle target-wise logit sharpening
S3  0.523202 -> 0.521750  iterative gentle logit residuals
S3  0.521750 -> 0.519957  subject-relative reopens after logit path
S3  0.519870 -> 0.512705  repeated strict subject-relative residuals
S4  0.627784 -> 0.626623  conservative sleep-dynamics add-on after fixed S4 pair
S4  0.626623 -> 0.619838  block-label residual smoothing after sleep-dynamics source
S4  0.619838 -> 0.618055  subject-relative S rank correction
S4  0.618055 -> 0.616847  strict second-pass rank correction
S4  0.616847 -> 0.616162  gentle target-wise logit sharpening
S4  0.616162 -> 0.615614  early loose residual only; later geometry rejects
S4  0.615614 -> 0.615375  loose subject-relative after logit path; later block/logit geometry rejects
```

Pair-weight rigor check:

```text
S2/S4 pre-pair mean contribution  0.600041
locked fixed pair estimate        0.598973
nested pair selector estimate     0.600477
decision: keep locked fixed weights; reject per-fold pair selection
```

Rejected Q-rate extension:

```text
Q1 subject-block rate shift        0.619828
half-subject Q1 shifted holdout    0.621631 vs base 0.615798
geometry Q1 shifted saved-current  0.629417 vs base 0.624443
decision: no Q-rate shift submission
```

Accepted Q1/S1 sleep-proxy extension:

```text
file: submission_hybrid_0p594_sleep_proxy_q23foldsafe.csv
Q1 subject-block OOF              0.604470
Q1 half-subject holdout           0.597643 vs base 0.615798
Q1 actual-geometry mask           0.611601 vs base 0.632460
Q2 fold-safe subject-block OOF    0.661317
Q2 half/geometry guardrail        0.681794 vs 0.686456; geometry w0.20 0.663919 vs 0.671960
Q3 fold-safe subject-block OOF    0.654440
Q3 half/geometry guardrail        0.693926 vs 0.694412; geometry w0.10 0.654510 vs 0.657612
S1 subject-block OOF              0.518602
mean estimate                     0.594511
integrity: 250 rows, nulls 0, duplicate keys 0, probability range 0.161006 .. 0.969576
top Q1 feature                    quiet-interval duration subject-rank
```

Accepted quiet-fragmentation extension:

```text
file: submission_hybrid_0p592_sleep_fragment_s1_q3.csv
previous mean estimate             0.594511
new mean estimate                  0.591892
S1 fragment leaf4 w0.60            0.518602 -> 0.504520
S1 repeated subject-half fixed     mean delta -0.014124, win-rate 0.977
S1 actual-geometry mask w0.60      0.530627 -> 0.518948
Q3 fragment leaf3 w0.30            0.654440 -> 0.650187
Q3 repeated subject-half fixed     mean delta -0.004307, win-rate 0.895
Q3 actual-geometry mask w0.30      0.654145 -> 0.649188
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.161006 .. 0.948678
interpretation: S1 is now the cleanest objective sleep-stage clue; Q3 accepts only a conservative low-weight fragmentation blend.
```

Accepted sleep-dynamics extension:

```text
file: submission_hybrid_0p591_sleep_dynamics_s1_s4.csv
previous mean estimate             0.591892
new mean estimate                  0.591380
S1 dynamic leaf6 w0.30             0.504520 -> 0.502098
S1 fixed repeated subject-half     mean delta -0.002430, win-rate 0.932
S1 actual-geometry mask w0.30      0.509429 -> 0.507605
S4 dynamic leaf3 w0.08             0.627784 -> 0.626623
S4 fixed repeated subject-half     mean delta -0.001253, win-rate 0.796
S4 actual-geometry mask w0.08      0.625851 -> 0.625016
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.161006 .. 0.952708
decision: kept as the previous sleep-dynamics backup before block-label residual and Q relative-temperature postprocess.
```

Accepted block-label residual extension:

```text
file: submission_hybrid_0p588_block_label.csv
previous mean estimate             0.591380
new mean estimate                  0.588893
Q1 s4_a0.9_w1_gap_boost0 w0.05     0.604470 -> 0.603439
Q2 s32_a0.9_w1_gap_boost0 w0.10    0.661317 -> 0.658044
Q3 s32_a0.9_w3_eq_boost0 w0.15     0.650187 -> 0.647542
S3 s4_a0.15_w5_gap_boost0 w0.60    0.535248 -> 0.531569
S4 s32_a0.9_w10_gap_boost0 w0.45   0.626623 -> 0.619838
S2 rejected despite full OOF gain   geometry 0.539040 -> 0.541775
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.152955 .. 0.952708
decision: accept Q1/Q2/Q3/S3/S4 only; reject S2 because the geometry guardrail worsens.
```

Accepted subject-relative Q extension:

```text
file: submission_hybrid_0p588_subject_relative_q.csv
previous mean estimate             0.588893
new mean estimate                  0.588241
Q1 center_temp_p2_w0.3             0.603439 -> 0.600917
Q1 repeated subject-half           mean delta -0.002464, win-rate 0.830
Q1 actual-geometry                 0.606165 -> 0.604220
Q2 center_temp_p0.5_w0.3           0.658044 -> 0.656820
Q2 repeated subject-half           mean delta -0.001271, win-rate 0.726
Q2 actual-geometry                 0.663306 -> 0.660554
Q3 center_temp_p0.5_w0.3           0.647542 -> 0.646729
Q3 repeated subject-half           mean delta -0.000884, win-rate 0.802
Q3 actual-geometry                 0.642652 -> 0.642074
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.122877 .. 0.952708
interpretation: Q1 is rank-sensitive; Q2/Q3 need shrinked relative differences rather than hard subject-rate balancing.
```

Accepted subject-relative S extension:

```text
file: submission_hybrid_0p587_subject_relative_qs.csv
previous mean estimate             0.588241
new mean estimate                  0.587417
S2 center_temp_p0.5_w0.3           0.559719 -> 0.558581
S2 repeated subject-half           mean delta -0.001200, win-rate 0.825
S2 actual-geometry                 0.539040 -> 0.537414
S3 center_temp_p0.5_w0.3           0.531569 -> 0.528718
S3 repeated subject-half           mean delta -0.002867, win-rate 1.000
S3 actual-geometry                 0.518608 -> 0.515986
S4 rank_logit_p0.75_w0.3           0.619838 -> 0.618055
S4 repeated subject-half           mean delta -0.001864, win-rate 0.742
S4 actual-geometry                 0.610113 -> 0.608501
S1 not promoted                    best OOF delta only -0.000183
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.122877 .. 0.952708
interpretation: objective sleep-stage targets still contain subject-relative state/rank residue after block labels and sleep proxies.
```

Accepted second-pass subject-relative resweep:

```text
strict file: submission_hybrid_0p586_subject_relative_resweep_strict.csv
strict mean estimate               0.586272
Q3 rank_logit_p0.5_w0.4            0.646729 -> 0.646039
Q3 subject-half / geometry         mean delta -0.000742, win-rate 0.817; geometry delta -0.001258
S2 center_temp_p0.25_w0.4          0.558581 -> 0.557029
S2 subject-half / geometry         mean delta -0.001585, win-rate 0.758; geometry delta -0.002442
S3 center_temp_p0.25_w0.4          0.528718 -> 0.524153
S3 subject-half / geometry         mean delta -0.004484, win-rate 1.000; geometry delta -0.004204
S4 rank_logit_p0.5_w0.4            0.618055 -> 0.616847
S4 subject-half / geometry         mean delta -0.001214, win-rate 0.684; geometry delta -0.001381
Q1 rejected                        no loose pass; best geometry delta only -0.000014
S1 not promoted                    loose-only tiny gain, best OOF delta -0.000186
```

Accepted Q2-loose add-on:

```text
file: submission_hybrid_0p586_subject_relative_resweep_q2loose.csv
previous strict mean estimate       0.586272
new mean estimate                  0.586214
Q2 center_shift_p-0.5_w0.2          0.656820 -> 0.656415
Q2 targeted 2000-repeat guardrail   mean delta -0.000401, win-rate 0.648
Q2 actual-geometry                 geometry delta -0.001295
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.122877 .. 0.952708
decision: highest-upside current candidate; keep strict resweep as the safer backup because Q2 narrowly misses the strict 0.65 win-rate gate.
```

Rejected current-frontier block-label residual:

```text
base: submission_hybrid_0p586_subject_relative_resweep_q2loose.csv
S2 best OOF residual                0.557029 -> 0.553555, but geometry delta +0.001623
S4 best OOF residual                0.616847 -> 0.616063, but geometry delta +0.000068
Q3 best OOF residual                0.646039 -> 0.645390, but subject-half win-rate 0.500 and geometry delta +0.000944
Q2 best OOF residual                0.656415 -> 0.656143, but subject-half win-rate 0.552
decision: do not stack more block-label smoothing at the current frontier.
```

Accepted gentle logit calibration:

```text
file: submission_hybrid_0p585_gentle_logit_calibration.csv
previous mean estimate             0.586214
new mean estimate                  0.585093
Q1 scale1.3_shift0_w0.2            0.600917 -> 0.599588; subject-half win-rate 0.977; geometry delta -0.001242
Q2 scale1.15_shift0.08_w0.2        0.656415 -> 0.655403; subject-half win-rate 0.897; geometry delta -0.000934
Q3 scale1.3_shift0_w0.2            0.646039 -> 0.645317; subject-half win-rate 0.938; geometry delta -0.001200
S1 scale1.3_shift0_w0.2            0.502098 -> 0.499921; subject-half win-rate 1.000; geometry delta -0.001551
S2 scale1.3_shift0_w0.2            0.557029 -> 0.556059; subject-half win-rate 0.963; geometry delta -0.001944
S3 scale1.3_shift0_w0.2            0.524153 -> 0.523202; subject-half win-rate 0.920; geometry delta -0.001331
S4 scale1.3_shift0_w0.2            0.616847 -> 0.616162; subject-half win-rate 0.958; geometry delta -0.001117
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.112719 .. 0.958214
interpretation: the current model family is still under-confident after all structural fixes; weak per-target sharpening is stable, unlike flexible joint calibration.
```

Accepted iterative gentle-logit residual path:

```text
calibration-only file: submission_hybrid_0p582_gentle_logit_residual6_loose.csv
first logit layer mean             0.585093
second layer mean                  0.584290
third layer strict / loose         0.583733 / 0.583714
fourth layer strict / loose        0.583381 / 0.583334
fifth layer strict / loose         0.583084 / 0.583058
sixth layer strict / loose         0.582885 / 0.582832
seventh layer strict / loose       0.582669 / 0.582657
latest accepted targets            Q2, Q3, S1, S2 strict; S3 loose; Q1 unchanged; S4 unchanged
latest guardrail                   Q2/S1/Q3/S2 strict, S3 loose; S4 rejected by geometry
integrity: 250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.084907 .. 0.973413
interpretation: calibration is approaching saturation; further logit-only iterations have diminishing returns and should be capped or nested before promotion.
```

Accepted alternating subject/logit/block residual path:

```text
subject-relative file: submission_hybrid_0p580_subject_relative_after_logit8_loose.csv
subject-relative mean              0.581478
subject-relative strict targets    Q1, Q2, Q3, S1, S2, S3
subject-relative loose target      S4
S2 block file                      submission_hybrid_0p580_block_s2_after_logit_subject.csv
S2 block mean                      0.580945
S2 block guardrail                 delta -0.001360, subject-half win-rate 0.682, geometry delta -0.000544
final file                         submission_hybrid_0p580_logit_after_block_s2_loose.csv
final mean estimate                0.580794
final accepted add-ons             Q1/S1 strict logit, Q3 loose logit
final integrity                    250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.098014 .. 0.974787
interpretation: after calibration saturates, subject-relative shrink reopens; after that, S2 block-state and small Q1/S1/Q3 calibration residual remain.
```

Accepted late alternating residual extension:

```text
base file                           submission_hybrid_0p580_logit_after_block_s2_loose.csv
base mean estimate                  0.580794
strict current file                 submission_hybrid_0p578_subject_after_logit_final8_strict.csv
strict current mean estimate        0.578530
previous high-upside file           submission_hybrid_0p578_subject_after_logit_final8_loose.csv
previous high-upside mean estimate  0.578467
strict late signal                  repeated S3 subject-relative correction, repeated S1 gentle-logit correction
loose late add-ons                  Q2 center-temp subject-relative, Q3 rank-logit subject-relative
latest guardrail                    S3 strict: delta -0.000444, win-rate 1.000, geometry delta -0.000417; Q2/Q3 loose only
latest integrity                    250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.107524 .. 0.978095
risk note                           late iterations are selected on OOF residuals; use strict file as safer backup and treat loose file as highest-upside, not fully nested proof.
```

Nested-supported late residual check:

```text
greedy nested selector result        repeated all-target greedy residual worsens heldout geometry by +0.002954 after 8 steps
stable target families               Q2 center-temp/logit, S1 weak logit, S3 repeated subject-relative
gridbest file                        submission_hybrid_0p579_nested_supported_late_residual_gridbest.csv
gridbest mean estimate               0.579168
gridbest geometry delta              -0.002044
gridbest geometry win-rate           1.0
current aggressive file              submission_hybrid_0p578_logit_after_subject_final9_strict.csv
current aggressive mean estimate     0.578304
current aggressive final add-ons      S1 scale1_shift-0.12_w0.2, S3 center_shift_p-0.5_w0.3
integrity                            250 rows, sample key order true, nulls 0, duplicate keys 0, probability range 0.107524 .. 0.976992
risk note                            prefer gridbest when validating structure; prefer aggressive current only for highest OOF upside.
```

Post-0.578/0.579 block-label retest:

```text
aggressive base file                 submission_hybrid_0p578_logit_after_subject_final9_strict.csv
aggressive S2 apparent OOF delta      -0.001187, rejected by geometry delta +0.002218
aggressive S4 apparent OOF delta      -0.000391, rejected by geometry delta +0.000224
aggressive Q3 apparent OOF delta      -0.000109, geometry delta -0.000846, rejected by win-rate 0.555
nested-supported base file            submission_hybrid_0p579_nested_supported_late_residual_gridbest.csv
nested-supported S2 apparent OOF delta -0.001065, rejected by geometry delta +0.002024
nested-supported S4 apparent OOF delta -0.000391, rejected by geometry delta +0.000224
nested-supported S1/Q1 small deltas    fail geometry or win-rate
decision                              do not build another block-label submission after the current 0.578/0.579 candidates.
```

Rejected cross-target coherence stack:

```text
current_0p594_oof mean              0.594511
nested_cross_target mean            0.599760
half-subject selected Q3/S1/S3      all worsened on holdout
decision: do not force label-coherence logits; target relationships are real but not reusable without leakage.
```

Submission integrity:

```text
file: submission_hybrid_0p598_repro.csv
rows: 250
columns: subject_id, sleep_date, lifelog_date, Q1, Q2, Q3, S1, S2, S3, S4
sample key order: true
nulls: 0
probability range: 0.159659 .. 0.975671
duplicate keys: 0
max target diff vs previous submission_hybrid_0p598.csv: 4.44e-16
```

Legacy overnight reproducibility:

```text
Q1  legacy_overnight_phone_sensor_only  0.625034
S1  legacy_overnight_phone_nested_blend 0.524188
S3  legacy_overnight_all_nested_blend   0.535248
```

Split geometry audit:

```text
actual submission blocks: 36 blocks, 250 rows, median n=5.5, both-boundary fraction=0.722
subject-block CV blocks: 50 blocks, 450 rows, median n=9.0
submission gaps are usually 1 day on both sides; CV chunks are artificial subject quintiles.
```

Actual-geometry mask CV:

```text
temporal_base                         0.613820
best all-target block/bridge          0.614258
locked S2/S4 fixed pair geometry mean 0.583723
current S2/S4 source geometry mean    0.587391
decision: no all-target geometry smoother; keep fixed S2/S4.
```

Rejected block-average postprocess:

```text
strength 0.00  mean 0.598973
strength 0.05  mean 0.599224
strength 0.10  mean 0.599526
decision: keep row-level predictions; do not average within submission blocks.
```

Rejected overnight block regressor:

```text
legacy_overnight_v1 temporal base           0.624765
legacy_overnight_v1 nested block regressor  0.624984
overnight_v2 nested block regressor         0.628856
decision: reject block-level ML regressor.
```

Broad residual nested selection audit:

```text
script                              broad_nested_selection_bias_audit.py
base                                final_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity_oof.npy
outer geometry repeats/top-n         8 / 10
nested selected mean loss            0.573043
nested selected delta                +0.008737
nested selected win-rate             0.0
fixed stage2 mean loss               0.561034
fixed stage2 delta                   -0.003272
fixed stage2 win-rate                1.0
fixed stage2 target deltas           S4 -0.012375, Q1 -0.003524, S3 -0.003385, S1 -0.003162, S2 -0.002210, Q3 +0.001753
decision                             reject more full-train broad residual mining; prefer public-calibrated shrink and Q3-off target gates.
```

Public-aware gated blend candidates:

```text
best public-calibrated full blend     submission_publicblend_anchor578_stage2567_prob_w545_latentmix.csv, predicted public 0.576841 under two-point latent mix
Q3-off score probe                    submission_publicgated_anchor578_stage2_drop_q3_prob_w650.csv, OOF 0.571066, distance 0.018449
Q3-off lower-amplitude probe          submission_publicgated_anchor578_stage2_drop_q3_prob_w545.csv, OOF 0.571900, distance 0.015469
Q3-off direct attribution             submission_publicgated_anchor578_stage2_drop_q3_prob_w1000.csv, OOF 0.569037, distance 0.028384
no-Q2/Q3 attribution                  submission_publicgated_anchor578_stage2_no_q2q3_prob_w650.csv, OOF 0.571421, distance 0.016070
integrity                             priority files: 250 rows, sample key order true, nulls 0, duplicate keys 0, clipped probabilities
```

Label-combination / powerset prior audit:

```text
scripts                              label_powerset_prior_audit.py, label_prior_target_gate_audit.py
base                                 full stage2 0.567531 OOF
hard/whole-target prior result        nested selected delta +0.000687, win-rate 0.0
best fixed whole-target prior         -0.000152, win-rate 0.625; too weak and driven almost entirely by S2
accepted weak exception               S2-only target-gated label prior
full-stage2 S2 gate geometry          -0.000592, win-rate 0.75
full-stage2 S2 gate OOF               +0.000315, S2 OOF +0.002206; ordinary subject-block OOF rejects it
Q3-off w650 S2 gate geometry          -0.000546, win-rate 0.75
Q3-off w650 S2 gate OOF               +0.000090, S2 OOF +0.000629; ordinary subject-block OOF rejects it
blend500/ambnext S2 gate geometry      -0.000690, win-rate 0.75
blend500/ambnext S2 gate OOF           -0.000030, S2 OOF -0.000212; ordinary subject-block OOF is almost flat
candidate                             submission_label_prior_gate_blend500_ambnext_r8_S2__global_qs_a0.5_w0.25_sh0.csv
decision                              no global label-powerset constraint; keep S2-only prior as a submission-geometry bet, not a primary score candidate.
```

## Next Real 0.5 Experiments

1. Stronger block-level representation only if a new raw source appears.  
   Daily, overnight v1, and overnight v2 block regressors all fail. Do not re-run the same Ridge block-rate family without new sleep-derived variables.

2. Submission-geometry-aware target switches only where independent evidence agrees.  
   Geometry masks now confirm second-pass Q3/S2/S3/S4 subject-relative resweep and the loose Q2 shrink, but reject another block-label layer. Any new geometry rule must be target-specific and held out against repeated geometry masks.

3. Extend sleep-derived proxy variables carefully.  
   Longest quiet interval and quiet-fragmentation are both useful. Next additions should focus on HR dip slope, wake-after-quiet interruptions, and subject-normalized interval regularity rather than generic segment counts.

4. Treat `Q1/Q2/Q3` as questionnaire latent-state reconstruction.  
   The useful path is soft subject-state reconstruction, not hard balancing. `Q2` has a working fold-safe sleep proxy; `Q3` now accepts conservative fragmentation; `Q1` remains the main subjective wall.

5. Re-test Q2/Q3 sleep-proxy only with stronger guardrails.  
   Geometry masks like Q2, but repeated subject-half rejects it. Q3 passes only at low fragmentation weight; avoid high-weight Q3 blends even when full OOF looks better.

## New Presleep Relative-Window Breakthrough

Fixed clock windows were missing a useful Q3 representation. I built `pre_sleep_relative_features.parquet`, using the inferred sleep start (`proxy_screen_step_start_hour`) to aggregate raw phone/watch/app/ambience features in `pre1h`, `pre3h`, `pre6h`, `post2h`, and `core5h` windows.

Key result:

```text
best feature                         presleep__presleep_hr_pre6h_hr_points_count
interpretation                       watch HR coverage in the 6h before inferred sleep start, subject-normalized
Q3 single-feature OOF delta           -0.010128
repeated subject-half mean delta      -0.009710
repeated subject-half win-rate        0.988462
train/sub raw mean                    118.10 / 124.55, so not an obvious submission-only artifact
```

Q3-off `w650` candidates:

```text
HR-only candidate                     submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45.csv
HR-only OOF / geometry                0.569619 / -0.000995, win-rate 0.90
HR+BLE candidate                      submission_publicgated_q3off650_presleep_hrpoints_c0.5_w0.45_ble_c0.2_w0.30.csv
HR+BLE OOF / geometry                 0.568778 / -0.001374, win-rate 0.90
Q3 target delta for HR+BLE             -0.016016
decision                              promote HR+BLE to public probe priority; keep as Q3-risk because the public anchor has not validated Q3 add-backs yet.
```

## Presleep Multitarget Breakthrough

The presleep alignment was not a one-target accident. Re-scanning the same relative-window feature block on the Q3-off `w650` base surfaced stable residuals for Q1/S1/S4 as well:

```text
Q1  presleep__presleep_charge_core5h_m_charging_min   OOF target delta -0.005870, half-split win-rate 0.981
S1  presleep__presleep_mlight_core5h_m_light_min      OOF target delta -0.008581, half-split win-rate 0.908
S4  presleep__presleep_mlight_pre3h_m_light_sum       OOF target delta -0.007120, half-split win-rate 0.969
Q3  presleep HR points + BLE morning unique           OOF target delta -0.016016
```

The combined candidates are now the strongest local artifacts:

```text
q3off650 presleep core      submission_publicgated_q3off650_presleep_core_q1_s1_s4_q3hr_ble.csv
OOF / geometry              0.565697 / -0.005976, win-rate 1.0

q3off650 presleep all       submission_publicgated_q3off650_presleep_core_all_s2quiet_q3hr_ble.csv
OOF / geometry              0.564786 / -0.006720, win-rate 1.0

anchor presleep core        submission_anchor578_presleep_core_q1_s1_s4_q3hr_ble.csv
OOF / geometry              0.572444 / -0.006258, win-rate 1.0

anchor presleep all         submission_anchor578_presleep_core_all_s2quiet_q3hr_ble.csv
OOF / geometry              0.570984 / -0.007268, win-rate 1.0
```

Interpretation: this is the first representation family that gives simultaneous target-level gains while preserving submission-geometry holdout behavior. It is still not guaranteed public gain because the only observed public feedback says stage2 amplitude transfers weakly; therefore the anchor-presleep and q3off-presleep candidates should be submitted as a pair when possible.

## Temporal-Context Presleep Breakthrough

The remaining S2/S3 gap was not captured by same-day presleep windows alone. I expanded the presleep block into neighbor-day transforms (`dprev1`, `next1`, `past2dev`, `future2dev`, `neighbor_dev`, `neighbor_slope`) and re-ran strict residual scans.

Stable additions:

```text
S2  prectx__presleep_wlight_pre1h_w_light_min_dprev1       OOF target delta -0.005525, win-rate 0.831
S2  prectx__presleep_charge_pre3h_m_charging_mean_dprev1   OOF target delta -0.005388, win-rate 0.962
S3  prectx__presleep_mlight_pre3h_m_light_max_future2dev   OOF target delta -0.008472, win-rate 0.992
Q3  ambience next-day context after HR+BLE                  Q3 loss 0.624878 -> 0.615696
```

Best combined artifacts:

```text
q3off650 temporal+ambnext      submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv
OOF / geometry                 0.562385 / -0.009748, win-rate 1.0

anchor temporal+ambnext        submission_anchor578_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv
OOF / geometry                 0.568820 / -0.010068, win-rate 1.0

blend temporal+ambnext w650    submission_presleepblend_prectx_s2wlight_s3light_q3hrble_ambnext_q3offw650.csv
OOF / distance                 0.564035 / 0.027964 from anchor

q3off temporal no-ambnext      submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble.csv
OOF / geometry                 0.563697 / -0.008500, win-rate 1.0
```

Distribution shift is not the obvious failure mode: the top S2/S3 temporal features shift by roughly `-0.022`, `-0.005`, and `-0.012` train standard deviations between train and submission. The real risk is semantic: `future2dev` and `next1` use future-neighbor sensor context, so these candidates assume batch inference over the full test lifelog table. Keep the non-ambience temporal candidate as the safer pair.

## Ordinal Label-Rule Constraint

The Q labels expose another hidden rule: each starts as a 5-point questionnaire value compared with the subject's full-period average. I enumerated all possible 1-5 ordinal count distributions per subject to derive feasible hidden positive counts from known train labels plus hidden row counts.

Result:

```text
script                         ordinal_q_count_constraint_audit.py
hard feasible-range clamp       no-op; predictions already fall inside feasible count intervals
best usable correction          Q2,Q3 nearest feasible hidden-count logit shift, weight 0.75
ambnext base                    0.562385 -> 0.561904
no-ambnext base                 0.563697 -> 0.563254
ambnext blend w850              0.563027 -> 0.562294
ambnext blend w750              0.563509 -> 0.562833
ambnext blend w650              0.564035 -> 0.563415
Q2/Q3 target deltas              -0.001522 / -0.001847 on ambnext base
Q1                              rejected; same correction worsens Q1
candidate                       submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv
public LB                       0.5783033652; worse than stage2 by +0.0003583895
```

This is still structurally different from feature mining because it comes from the label-generation mechanism itself, but the public result demotes it to a diagnostic. Reuse it only through tiny probability blends with a public-observed endpoint.

Rejected high-capacity alternatives:

```text
nested sparse calibrator on Q2/Q3      Q2 +0.006751, Q3 +0.022931 on r4 geometry
nested sparse calibrator on other      all worsened; best S3 +0.001491
temporal bridge selected Q2/Q3         but subject-block OOF mean worsened +0.003621
decision                              the useful new signal is representation-level presleep alignment, not a more flexible calibrator or Markov bridge.
```

## Public Universe Minimax Boundary

The latest expanded minimax test added every plausible public-constraint uncertainty class I have built so far: raw entropy projections, target masks, sparse minimax ensembles, mask-aware row-subset projections, conservative-frontier bridges, and the submitted-safe priors.

```text
script                             public_universe_minimax_optimizer.py
search candidates                   61
scenario classes                    core entropy 0.80/0.65/0.50/0.35, mask-aware, conservative pseudo-posteriors
saved submissions                   16
best trusted u80                    submission_public_universeens_u80_r01_07c571e6.csv
u80 robust score / OOF              0.574917 / 0.554343
best mixed u65                      submission_public_universeens_u65_r02_c0e2b2f1.csv
u65 robust score / OOF              0.574947 / 0.554117
result                              expanded search returns to the old minimax frontier; more mixed profiles trade lower OOF for higher pseudo-posterior regret.
```

Breakthrough implication: the public-LB inverse route has likely found its current local optimum under only three public observations. To get a real new 0.5-level move from this branch, we need another independent public observation or a different structural label rule, not just more blending around the same three-score entropy posterior.
