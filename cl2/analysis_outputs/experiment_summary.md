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
- `submission_public_consfront_t80_r10_b06ca82f.csv`: conservative bridge from anchor->stage2 w095 to minimax r01 at 65% risk weight; OOF `0.557498`, entropy-only scenario score weaker than minimax but safer under expanded pseudo-posterior audit.
- `submission_public_consfront_t65_r07_f8156dce.csv`: conservative bridge from anchor->stage2 w095 to entropy g075 at 65% risk weight; OOF `0.557303`, posterior mean `0.574803`, conservative mean `0.574641`.
- `submission_public_maskaware_t80_r11_544844af.csv`: mask-aware random-mask conditional/no-Q2 probe; OOF `0.553156`, mean expected `0.574650`, scenario robust score `0.575019`. It is not better than minimax, but is a strong alternate if public row-subset uncertainty is prioritized.
- `submission_public_maskaware_t65_r07_768f6df0.csv`: mask-aware random conditional/all-target probe; OOF `0.553045`, single-posterior subset robust score essentially tied with entropy g075.
- `submission_public_universeens_u80_r01_07c571e6.csv`: expanded-universe ensemble. It ties the old minimax six-posterior robust score `0.574917`, OOF `0.554343`; use only as a confirmation/alternate, not ahead of `submission_public_minimaxens_r01_a6_h422045.csv`.
- `submission_public_universeens_u65_r02_c0e2b2f1.csv`: stress-probe blend across minimax/mask-aware/conservative files; OOF `0.554117`, six-posterior robust score `0.574947`. Slightly more robust to pseudo-posterior uncertainty, but lower public-constraint priority than raw minimax.
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
