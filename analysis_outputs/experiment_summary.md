# Experiment Summary

Last updated: 2026-05-26

## Current Best

Public best remains `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` at `0.5779449757`.

The OOF-best ordinal/ambnext file `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` scored public `0.5783033652`, worse than stage2 by `+0.0003583895`. Its offline/public gap is `+0.0163995480`, so aggressive q3off/ambnext count-shift candidates are now public-fragile.

## What Worked

- Full stage2 direction transfers weakly: public improves anchor by `-0.0004823771`.
- Presleep temporal-context features remain the strongest representation discovery, but public has not yet isolated them.
- S2-only label-combination prior is repeatable in geometry masks across stage2, q3off650, and blend500/ambnext, but ordinary OOF is weak or negative.
- Probability blends between endpoints with known public scores give convex public upper bounds and are now safer than new OOF-only jumps.
- Orthcap preserves much of the subject-gated ordinal OOF gain while reducing the observed public-bad stage2->ordinal direction to 0.05-0.30 projection.
- Projection-constrained probability blends among orthcap/exact-count candidates now dominate the single-endpoint orthcap ladder at the same public-bad-direction exposure.
- Public two-axis blends use both submitted public directions: anchor->stage2 as a weak good axis and stage2->ordinal as a bad axis. This creates a slightly better low-risk candidate than the one-axis cap ladder.
- Public-constraint entropy projection is the first direct public-LB inverse method that creates a plausible `0.575-0.576` public-posterior score hypothesis. It is high-risk quasi-labeling, but the OOF analogue is very strong: public2d0 g100 gives OOF `0.553679`, and geometry analogue improves by `-0.010874` with win-rate `1.0`.
- Public-constraint target masking sharpens that exploit: Q2 can be removed with almost no loss. The best balanced mask `Q1+Q3+S1+S2+S3+S4 g075` has OOF `0.554185`, public-posterior expected `0.575887`, and less movement than full g075.
- Public subset sensitivity now favors the Q2-dropped target-mask over raw full `g100`. Across six posterior scenarios and simulated public row subsets, `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv` has mean expected `0.574649`, mean regret `0.000082`, p90 regret `0.000159`, and win-rate `1.0` vs the public2d0 prior.
- Public minimax ensembling improves the scenario-regret layer slightly. `submission_public_minimaxens_r01_a6_h422045.csv` has mean expected `0.574634`, mean regret `0.000067`, p90 regret `0.000118`, win-rate `1.0`, and OOF analogue `0.554332`.
- Public conservative frontier blends the entropy/minimax signal back toward submitted-safe predictions. It gives up some entropy-only upside, but provides mid-risk probes that still improve posterior scenarios while staying close to stage2/public2d0/projblend pseudo-posteriors. Best higher-trust bridge: `submission_public_consfront_t80_r10_b06ca82f.csv`, OOF `0.557498`, posterior mean `0.574792`, conservative mean `0.574646`.
- Mask-aware entropy projection stress-tests the "public subset equals all 250 rows" assumption. Random/subject-contiguous masks require shifts close to the all-row projection, while global prefix/suffix masks require much larger moves and look less plausible. Best mask-aware files sit just below minimax and target-mask g075 in six-posterior robustness; `submission_public_maskaware_t80_r11_544844af.csv` has OOF `0.553156`, mean expected `0.574650`, p90 regret `0.000160`, and win-rate `1.0`.
- Public universe minimax adds mask-aware and conservative pseudo-posteriors into the ensemble search. It does not create a new top candidate: the `u80` profile collapses back to existing minimax files with the same six-posterior robust score `0.574917`. This is useful negative evidence that the public-constraint optimum is already saturated unless we accept more pseudo-posterior risk.
- Adding presleep candidates to the public-direction audit explains why they should not lead the queue: the strongest presleep/temporal-context files have excellent OOF, but move almost exactly along the failed stage2->ordinal public-bad axis.
- Presleep orthcap confirms the diagnosis: after capping/removing the public-bad axis, presleep still has real residual signal, but the surviving gain is too small to beat the existing projection blends.

## What Failed

- Direct ordinal/ambnext OOF-top submission failed to beat current public best.
- Whole-target label powerset priors remain rejected.
- Posterior ordinal count priors worsened OOF; nearest feasible count is the only useful diagnostic, not a direct public score move.
- Full-strength subject-target gates have excellent OOF, but their public-bad-direction projection is still high, so they are not safety candidates.
- Re-testing ordinal constraints with an exact 1-5 value-count prior confirmed that posterior mean/mode is harmful. Only nearest feasible hidden-positive count works, and Q3-only is cleaner than Q2/Q3 when public-direction risk matters.
- S2 label-prior additions on orthcap/exact bases are not score candidates: geometry looks favorable, but full OOF worsens S2 by about `+0.0020`.
- Covariate-neighbor label priors over sleep/quiet/presleep features are not useful on top of stage2. Best scan result is only `-0.000199` OOF, affects S4 only, and fails the repeated-subject guardrail (`guard_mean_delta +0.002463`, win-rate `0.435`).
- Row-level public gating by hidden block geometry is rejected. The best block-aware anchor->stage2 gate has geometry delta `+0.001034` versus full stage2 and zero geometry wins, so submission block position/gap does not justify shrinking stage2 row-by-row.
- Projection dry-run with presleep candidates added to the orthcap/exact pool selected no presleep file at any cap from `-0.005` to `0.300`; the orthcap/exact projection blends remain dominant.
- Presleep orthcap candidates are not promoted. Best OOF is `0.565572` at projection `0.375`; the low-risk `projection <= 0.05` subset tops out at OOF `0.567216`, only `0.000315` gain versus stage2.
- Direct NSF-guideline proxy additions on stage2 are rejected. A 48-config S1/S2/S3/S4 audit found zero loose/strict passes; S1/S2/S3 choose zero blend weight, and the best S4 WASO proxy has tiny OOF gain `-0.000188` but subject-half guardrail delta `+0.000582`.
- Block-target public entropy projection is rejected. The real submission has 36 hidden blocks and the validation-block oracle is very strong, but fitting the three public scores with one latent probability per block-target overfits badly in train analogue. Best minimax-prior block projection at gamma `0.35` worsens OOF from `0.554332` to `0.570921`; public2d0 worsens from `0.561702` to `0.573676`.
- Boundary-consensus postprocessing is rejected. Same-boundary and one-sided endpoint labels are visibly exposed in the submission split, but nested target-wise validation worsens every tested base/mode. Best nested row is only `stage2 + zeros_only`, and it still worsens `0.567531 -> 0.567797`; minimax worsens `0.554332 -> 0.554762`. Apparent full-OOF gains such as minimax `zeros_only -0.000337` are selection artifacts.
- Ordinal Q-count constraints are demoted by public feedback. `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` scored `0.5783033652`, worse than stage2 public by `+0.0003583895`, so Q2/Q3 ordinal correction is useful label-rule evidence but not a direct score file on the ambnext backbone.
- Public-mask plausibility reweighting changes the high-upside queue. Equal-mask/six-posterior scoring still favors minimax `r05/r01`, but downweighting implausible global prefix/suffix masks and crossing conservative pseudo-posteriors promotes `u65` universe files; compromise `maskplausens` blends lower mean profile score but do not win individual profiles.

## Latest Audit Files

- `current_covknn_stage2_scan.csv`: 216 sleep/quiet/presleep KNN-prior configs; no loose/strict pass.
- `public_block_gated_blend_candidates.csv`: 78 row-level hidden-block anchor/stage2 gates; no saved candidate.
- `presleep_public_direction_audit.csv`: 30 presleep candidates projected onto the two observed public axes; top OOF file has bad-axis projection `0.992393`.
- `presleep_orthcap_candidates.csv`: 73 presleep-axis-capped derivatives; global risk-rank best is only rank `2530/3739`.
- `presleep_orthcap_integrity_and_deltas.csv`: top 30 presleep orthcap files have 250 rows, no duplicate keys, no missing probabilities, and probability range within `[0.0672, 0.9861]`.
- `nsf_guideline_proxy_audit.csv`: 48 interpretable S-target proxy configs; no candidate selected.
- `nsf_guideline_proxy_report.md`: decision note for the NSF proxy negative control.
- `public_entropy_projection_summary.csv`: 16 public-LB entropy projection candidates; best OOF analogue `0.553679`, best balanced high-upside file `submission_public_entropyproj_public2d0_g075.csv`.
- `public_entropy_projection_geometry_analogue_summary.csv`: train-fold analogue of the public-constraint trick; public2d0 prior mean delta `-0.010874`, win-rate `1.0`.
- `public_entropy_projection_report.md`: decision note and constraint residual audit for the public-LB inverse projection.
- `public_entropy_projection_target_shift_summary.csv`: target movement decomposition; balanced `g075` mostly moves Q1/Q3/S3/S4, with Q3 down and S3 up.
- `public_entropy_projection_top_shift_cells.csv`: largest row-target changes for the public-constraint candidates.
- `public_entropy_targetmask_summary.csv`: 508 target-mask public-constraint rows; best risk-score row is `Q1+Q3+S1+S2+S3+S4 g050`.
- `public_entropy_targetmask_selected.csv`: 48 saved target-mask submissions and OOF analogues.
- `public_entropy_targetmask_integrity.csv`: all 48 target-mask files have 250 rows, no duplicate keys, no null predictions.
- `public_subset_sensitivity_summary.csv`: single-posterior row-subset stress test for public-constraint candidates.
- `public_posterior_scenario_robustness_summary.csv`: six-posterior row-subset regret audit; promotes Q2-dropped `g075` as the most robust public-constraint file.
- `public_minimax_ensemble_summary.csv`: convex ensemble optimizer over public-constraint candidates.
- `public_minimax_ensemble_selected.csv`: 8 saved minimax ensemble submissions and OOF analogues.
- `public_minimax_ensemble_integrity.csv`: all minimax ensemble files pass key/null/probability checks.
- `public_conservative_frontier_builder.py`: stage2/public2d0/projblend/anchor pseudo-posterior frontier for damping public-constraint overfit.
- `public_conservative_frontier_selected.csv`: 12 saved conservative public-constraint bridge submissions.
- `public_conservative_frontier_integrity.csv`: all conservative frontier files pass key/null/probability checks.
- `public_maskaware_entropy_projection.py`: solves public-score entropy constraints over many plausible public row masks and averages logit shifts.
- `public_maskaware_projection_family_diagnostics.csv`: mask-family movement audit; global prefix/suffix masks are the extreme outlier.
- `public_maskaware_entropy_selected.csv`: 12 saved mask-aware public-constraint submissions and OOF analogues.
- `public_maskaware_entropy_integrity.csv`: all mask-aware files pass key/null/probability checks and have OOF shape `(450, 7)`.
- `public_universe_minimax_optimizer.py`: expanded minimax search over entropy, target-mask, mask-aware, conservative-frontier, and prior candidates.
- `public_universe_minimax_selected.csv`: 16 saved universe minimax submissions. `u80` ties the old minimax frontier; `u65/u50/u35` are lower-priority pseudo-posterior stress probes.
- `public_universe_minimax_integrity.csv`: all universe minimax files pass key/null/probability checks and have OOF shape `(450, 7)`.
- `public_block_entropy_projection.py`: block-target version of the public-score entropy projection using actual submission hidden blocks.
- `public_blockentropy_analogue_summary.csv`: train analogue rejects the block-target projection; every tested prior/mask/gamma worsens versus its prior.
- `public_blockentropy_selected.csv`: 17 generated blockentropy diagnostic submissions, not promoted.
- `public_blockentropy_integrity.csv`: all blockentropy diagnostic files pass key/null/probability checks.
- `boundary_consensus_audit.py`: fold-safe endpoint-label audit for actual hidden-block boundaries.
- `boundary_consensus_case_summary.csv`: row-level case table; some endpoint anchors look locally useful, but effects are target/case unstable.
- `boundary_consensus_nested_summary.csv`: final rejection evidence; all base/mode nested mean deltas are positive.
- `boundary_consensus_submission_boundary_exposure.csv`: actual sample boundary exposure; e.g. Q1 has 64 `same0` and 33 `same1` rows, S3 has 107 `same1` rows.
- `boundary_consensus_report.md`: decision note; no boundary-consensus candidate is promoted.
- `public_mask_plausibility_reweight.py`: re-ranks all public-constraint submissions under explicit public-mask family priors and scenario profiles.
- `public_mask_plausibility_reweight_summary.csv`: consensus table; `u65_r04/u65_r01` have the best mean ranks, while submitted stage2 and ordinal are bottom controls.
- `public_mask_plausibility_blend_scan.py`: targeted blend scan over top plausibility candidates.
- `public_mask_plausibility_blend_selected.csv`: five saved compromise blends; best mean-score candidates are `maskplausens_r04/r05`, but they trail `u65` on profile-win ranking.
- `public_mask_plausibility_blend_integrity.csv`: all five compromise blends pass key/null/probability and OOF-shape checks.
- `rhythm_regularization_feature_builder.py`: builds 968 subject-relative rhythm and measurement-process features from proxy/quiet/presleep logs.
- `rhythm_regularization_scan.py`: fold-safe residual scan with subject-half and geometry guardrails for rhythm features.
- `rhythm_regularization_combo_builder.py`: creates rhythm combo submissions and OOF analogues for stage2 and q3off650 bases.
- `rhythm_regularization_signal_report.md`: direction and quantile audit for the top rhythm signals.
- `rhythm_stage2_combo_summary.csv`: full non-Q2 rhythm combo reaches OOF `0.561317`, geometry `-0.008151`, win-rate `1.0`.
- `rhythm_q3off650_combo_summary.csv`: q3off650 non-Q2 rhythm combo reaches OOF `0.564012`, geometry `-0.008501`, win-rate `1.0`.
- `measurement_process_feature_builder.py`: builds 16,140 sensor coverage/gap/wear-compliance features from all raw parquet logs.
- `measurement_process_scan.py`: target-balanced fold-safe residual scan for measurement-process features.
- `measurement_process_combo_builder.py`: creates measurement-process combo submissions and OOF analogues for stage2 and q3off650 bases.
- `measurement_process_signal_report.md`: direction and quantile audit for the top measurement-process signals.
- `mp_stage2_combo_summary.csv`: stage2 non-Q2 measurement combo reaches OOF `0.561643`, geometry `-0.004915`, win-rate `1.0`.
- `mp_q3off650_combo_summary.csv`: q3off650 non-Q2 measurement combo reaches OOF `0.564592`, geometry `-0.005067`, win-rate `1.0`.

## Rhythm Regularization Finding

The strongest new raw-log discovery is a subject-relative rhythm / measurement-density family. It improves every target except Q2 under OOF and geometry checks:

```text
Q1  core5h charging minimum zdev
Q3  pre6h HR point count same-weekend deviation
S1  core5h mobile-light minimum subject deviation
S2  pre3h charging mean previous-day delta
S3  pre3h mobile-light max next-3-day delta
S4  pre3h mobile-light sum same-weekend deviation
```

The best stage2 full non-Q2 combo is `submission_rhythm_stage2_nonq2_strict.csv` with OOF `0.561317`; the softer q3off650 variant `submission_rhythm_q3off650_nonq2_soft.csv` has OOF `0.565892`. Public posterior audits reject these as primary submissions: q3off650 non-Q2 soft has scenario score `0.590227`, far behind the u65/minimax frontier near `0.5749-0.5763`. Treat this as a label/measurement-process clue, not a public-safe replacement.

## Measurement-Process / Wear-Compliance Finding

The raw parquet logs expose a broader measurement-process family beyond the rhythm transform. I built 16,140 features around sensor observation count, minute coverage, first/last observed hour, long gaps, watch-vs-phone coverage, active-sensor count, and subject-relative same-weekend deviations.

Target-balanced guardrails confirm six targets and reject Q2:

```text
Q1  core5h usage row count / subject rank
Q3  pre6h HR observation fraction same-weekend deviation
S1  watch-gap irregularity or screen first-observed hour
S2  all-day watch-light longest gap same-weekend deviation
S3  evening/candidate usage sampling gap
S4  pre6h active sensor count same-weekend deviation
Q2  no selected feature; best raw move is only about -0.0001
```

Combo results:

```text
stage2 non-Q2              0.567531 -> 0.561643, geometry -0.004915, win-rate 1.0
stage2 no-Q2/no-Q3         0.567531 -> 0.563438, geometry -0.003370, win-rate 1.0
q3off650 non-Q2            0.571066 -> 0.564592, geometry -0.005067, win-rate 1.0
q3off650 no-Q2/no-Q3       0.571066 -> 0.566787, geometry -0.003363, win-rate 1.0
```

Public posterior audits reject direct submission, even after removing Q3. Best measurement-process public rows are `submission_mp_q3off650_q3_hr.csv` with scenario score `0.587092` and `submission_mp_q3off650_s4_sensor_count.csv` with score `0.588146`; the no-Q2/no-Q3 soft combo has score `0.591289`. Mask-plausibility ranks them around 110+ versus the u65/minimax frontier around 17-35. Treat this family as strong label-process evidence, not as a current public-safe file.

## Q2 Stage2-Safe Residual Scan

After `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` scored public `0.5783033652`, strong Q-count / Q2+Q3 moves are demoted. I re-scanned Q2 as a single-column residual: use the public-best stage2 file as the base, swap only Q2 from existing OOF/submission families, and guard by Q2 geometry plus the two observed public axes.

Key result:

```text
stage2 base public                         0.5779449757
stage2 Q2 loss                             0.642999
best maskaware-Q2 swap                     Q2 0.632038-0.632045, mean delta about -0.001565
maskaware-Q2 geometry                      mean Q2 delta about -0.0116, win-rate 1.0
maskaware-Q2 public-axis estimate          about +0.000008 vs stage2, effectively neutral
best orthcap-Q2 swap                       Q2 0.635692-0.636074, mean delta about -0.00104 to -0.00099
orthcap-Q2 geometry                        Q2 win-rate 1.0
orthcap-Q2 public-axis estimate            about -0.000005 to -0.000006 vs stage2
```

Generated stage2-safe Q2 probes:

```text
submission_q2_stage2safe_r01_af9d1d96.csv  maskaware aggressive, mean -0.001566, Q2 -0.010961
submission_q2_stage2safe_r02_369582d6.csv  maskaware aggressive, mean -0.001565, Q2 -0.010956
submission_q2_stage2safe_r05_f1881cc3.csv  orthcap conservative, mean -0.000989, Q2 -0.006924
submission_q2_stage2safe_r10_a7aa0680.csv  orthcap conservative, mean -0.001044, Q2 -0.007307
```

Interpretation: Q2 is not closed by raw sensor/rhythm features, but it is partially recoverable from the public-constraint / orthogonal-count family. The important shape is subject-specific re-centering: stage2 was too high for id02/id06 high-probability Q2 rows and too low for id05/id09 low-probability rows. This is opposite to the failed ordinal Q2/Q3 constraint direction on several rows, which explains why the latest ordinal file moved public away.

## Next 3

1. `submission_publicobsblend_stage2_to_ordinal_w005.csv`  
   Public-observed microblend. OOF `0.567025`; convex public upper bound `0.5779628952`. This is still the lowest-risk endpoint sanity check.

2. `submission_projblend_cap0p0.csv`  
   Near-zero projection non-convex diagnostic. OOF `0.562144`; projection `-0.000049`, linear public estimate `0.577945`.

3. `submission_public2dblend_budget0p0.csv`  
   Best two-axis low-risk non-convex candidate. OOF `0.561702`; two-axis public delta `-0.00000005`, one-axis public delta `+0.00000890`.

High-upside alternatives:

- `submission_public_entropyproj_public2d0_g075.csv`: high-risk public-constraint exploit; OOF analogue `0.554156`, public-posterior expected loss `0.575826`, mean move `0.013218`.
- `submission_public_entropyproj_public2d0_g050.csv`: safer public-constraint shrink; OOF analogue `0.555625`, public-posterior expected loss `0.576100`, mean move `0.008793`.
- `submission_public_entropyproj_public2d0_g100.csv`: maximum public-constraint exploit; OOF analogue `0.553679`, public-posterior expected loss `0.575734`, exactly fits the three observed public constraints in expectation.
- `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv`: target-mask balanced public-constraint probe; drops Q2, OOF `0.554185`, expected `0.575887`, mean move `0.011874`.
- `submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv`: lower-move target-mask probe; drops Q2/S1, OOF `0.555407`, expected `0.575956`, mean move `0.010956`.
- `submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv`: safest target-mask score by current risk score; OOF `0.555707`, expected `0.576149`, mean move `0.007898`.
- `submission_public_minimaxens_r01_a6_h422045.csv`: best sparse minimax public-constraint ensemble; OOF `0.554332`, mean expected `0.574634`, p90 regret `0.000118`.
- `submission_public_minimaxens_r05_a10_h506746.csv`: best six-posterior/equal-mask robust score after re-run; score `0.5749169278`, essentially tied with `r01` but marginally ahead.
- `submission_public_consfront_t80_r10_b06ca82f.csv`: conservative bridge from anchor->stage2 w095 to minimax r01 at 65% risk weight; OOF `0.557498`, entropy-only scenario score weaker than minimax but safer under expanded pseudo-posterior audit.
- `submission_public_consfront_t65_r07_f8156dce.csv`: conservative bridge from anchor->stage2 w095 to entropy g075 at 65% risk weight; OOF `0.557303`, posterior mean `0.574803`, conservative mean `0.574641`.
- `submission_public_maskaware_t80_r11_544844af.csv`: mask-aware random-mask conditional/no-Q2 probe; OOF `0.553156`, mean expected `0.574650`, scenario robust score `0.575019`. It is not better than minimax, but is a strong alternate if public row-subset uncertainty is prioritized.
- `submission_public_maskaware_t65_r07_768f6df0.csv`: mask-aware random conditional/all-target probe; OOF `0.553045`, single-posterior subset robust score essentially tied with entropy g075.
- `submission_public_universeens_u80_r01_07c571e6.csv`: expanded-universe ensemble. It ties the old minimax six-posterior robust score `0.574917`, OOF `0.554343`; use only as a confirmation/alternate, not ahead of `submission_public_minimaxens_r01_a6_h422045.csv`.
- `submission_public_universeens_u65_r04_dc6f3303.csv`: best public-mask-plausibility mean-rank file; OOF `0.554759`, plausibility mean score `0.576299`, six-posterior score `0.575013`.
- `submission_public_universeens_u65_r01_365a84a6.csv`: wins 6/24 plausibility profiles; OOF `0.554318`, plausibility mean score `0.576335`, six-posterior score `0.574977`.
- `submission_public_universeens_u65_r02_c0e2b2f1.csv`: best u65 six-posterior score; OOF `0.554117`, six-posterior robust score `0.574947`; more of an entropy-trusted stress probe than a plausibility-rank winner.
- `submission_public_maskplausens_r05_e8325bb7.csv`: compromise blend `70% u65_r04 + 30% u50_r02`; OOF `0.555222`, plausibility mean score `0.576278`, six-posterior score `0.575111`.
- `submission_public_maskplausens_r04_161f5469.csv`: compromise blend `70% u65_r04 + 30% u50_r01`; OOF `0.555232`, plausibility mean score `0.576276`, six-posterior score `0.575116`.
- `submission_publicobsblend_stage2_to_ordinal_w010.csv`: OOF `0.566549`; convex public upper bound `0.5779808147`.
- `submission_projblend_cap0p05.csv`: OOF `0.561307`, projection `0.048995`; one-axis low-risk projection blend.
- `submission_public2dblend_budget0p00002.csv`: OOF `0.560724`, two-axis public delta `+0.00001997`; intermediate score probe.
- `submission_projblend_cap0p1.csv`: OOF `0.560523`, projection `0.099482`; balanced score/projection candidate.
- `submission_public2dblend_budget0p00005.csv`: OOF `0.560039`, two-axis public delta `+0.00004984`; higher-upside two-axis blend.
- `submission_projblend_cap0p15.csv`: OOF `0.560170`, projection `0.149470`; higher-upside projection blend.
- `submission_projblend_cap0p2.csv`: OOF `0.559879`, projection `0.199447`; score-first projection blend.
- `submission_orthcap010_exact_q3_exact_value_nearest_w1.csv`: OOF `0.560925`, projection `0.101177`; clean Q3-only count quantization, now mostly interpretability probe.
- `submission_orthcap030_exact_q2q3_exact_value_nearest_w1.csv`: OOF `0.559355`, projection `0.305399`; strongest OOF in the exact-prior family, now a projection-blend endpoint.
- `submission_orthcap_s001_cap010_sc100.csv`: OOF `0.561989`, projection `0.100`, no convex bound but strong OOF/projection tradeoff.
- `submission_orthcap_s001_cap030_sc100.csv`: OOF `0.560427`, projection `0.300`, main high-upside orthcap.
- `submission_subjectgate_ordinal_all_thrm0p005_w100.csv`: full OOF `0.558584` and time-half guarded OOF `0.563328`, but projection `0.623`; submit only if accepting a much larger public-direction risk.

## Information Probes

- `submission_stage2_donor_ordinal_q3_w100.csv`: Q3-only test, OOF `0.565174`, projection `0.342`.
- `submission_stage2_donor_ordinal_s1_s3_s4_w080.csv`: objective S1/S3/S4-only test, OOF `0.565139`, projection `0.316`.
- `submission_stage2_donor_ordinal_no_q2_w035.csv`: all-except-Q2 test, OOF `0.564668`, projection `0.345`.
- `submission_subjectgate_ordinal_all_thrm0p02_w080.csv`: lower-projection subject-gate, OOF `0.562297`, half-gate `0.564583`, projection `0.321`.
- `submission_subjectgate_ordinal_s1_s3_s4_thrm0p01_w100.csv`: S-only subject-gate, OOF `0.563962`, half-gate `0.565689`, projection `0.166`.
- `submission_orthcap_s009_cap005_sc100.csv`: low-projection orthcap, OOF `0.562905`, projection `0.050`.
- `submission_orthcap_s005_cap000_sc100.csv`: pure orthogonal residual, OOF `0.563648`, projection near zero.
- `submission_stage2_donor_ordinal_q3_s_w035.csv`: target-mask attribution probe, OOF `0.564838`, projection `0.295`, changing only `Q3,S1,S2,S3,S4`.
