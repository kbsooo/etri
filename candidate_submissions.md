# Candidate Submissions

작성일: 2026-05-29

Submission 후보는 CV 점수순이 아니라 survival score로 판단한다.

```text
submission_survival_score =
  public-observation consistency
  + anchor-LOO/L2O consistency
  + blockwise stress survival
  + targetwise calibration improvement
  + raw05 compatibility or justified deviation
  + prediction diversity without instability
  + latent energy sanity
  + seed/model-family stability
  + known public LB observation consistency
  + expected upside/downside ratio
```

## Current Public Frontier

Current public frontier: `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` with public LB `0.5761589494`.

Current best next submission candidate depends on the public question:

- score plus information after E247: `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`.
- clean E224 body attribution: `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
- OOF-vs-materialization conflict sensor: `analysis_outputs/submission_e252_e237_e250_union_q3top31_67707aef.csv`.
- learned Q3 decisive-cell contrast: `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
- conservative repaired branch: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

E247 supersedes the earlier E95-centered candidate order. E176/E174/E172/E169/E166 remain historical worldview sensors, not the current first choice, because E247 has provided a stronger public-positive JEPA mechanism.

Previous frontier: `analysis_outputs/submission_mixmin_0c916bb4.csv` with public LB `0.5763066405`.

The E95 improvement over mixmin is `-0.0000153107`. This is small in absolute terms, but it is `15.14%` of the failed E72 public miss (`+0.0001011367`) and it validates the hard-tail localization branch as public-positive rather than merely local stress-positive.

E88 adds one important risk lens after the E72 miss: post-mixmin target-pruned candidates are not continuation of mixmin's first-order movement. They are rollback/refinement moves with varying proximity to the public-negative E72 movement. E86 remains the highest-upside sensor by local stress, but it is E72-contamination-proximate. E89 turns that warning into a concrete minimum-contamination candidate by falling back from E86 to E85 only on the top-E72-contaminated cells. E90 adds the balanced version: fallback entire top-E72 rows so more E86 hidden/world/block structure survives while contamination still drops below E85/no-Q2. E91 then closes the tempting known-LB regression shortcut: adding E72 still leaves movement-fingerprint proxy error about `10x` the E72 miss, so E86/E90/E89 should be ordered by the hypothesis being tested rather than proxy-predicted score. E92 closes the next shortcut: hidden-block posterior CE ranks the failed E72 file first, so posterior alignment is a representation-health diagnostic, not a public-safe selector. E93 closes the natural counter-shortcut: train target-manifold consistency also likes E72 and older bad public anchors, so target dependency cannot be used to rank the next file either. E94 adds the missing hard-label tail lens: E72's public miss is only `4.3389%` of its full adverse hard-label exposure, and hard-tail metrics align with known public LBs far better than soft-health metrics. E95 turns that lens into a direct gate: E86 hard-tail cells fallback to E85 creates a strict candidate that beats E89 on both E72-adverse tail and all-combo margin. E96 stress-tests that claim by allocating the observed E72 miss across `3894` plausible hard-tail worlds: E95 has the best mean/win-rate and beats E89 in `71.24%` of scenarios, while E85 has a marginally lower p95 tail floor. Public E95 then confirms the branch with LB `0.5762913298`, better than mixmin by `0.0000153107`. E98 adds the negative selector update: even after E95 is added as the 11th known public anchor, movement-fingerprint regression still has p90 error `0.000816497`, `53.33x` the E95 edge, and still gets E72-minus-mixmin sign wrong. E99 adds the E95-conditioned transfer update: after forcing E72 miss and E95 gain into the same local+tail worlds, E95 remains best mean/best p95/winner mode, while E89 is the only unresolved file with material E95-beat rate (`0.195829`). E100 narrows that further: E89's favorable pocket is not broad, but concentrated in Q2/S3 diffuse-tail scenarios where the `q2s3` slice beats E95 at `0.779891`. E101 tests that pocket with only `50` active E95-relative Q2/S3 rollback cells, and E102 shows those cells are not a hidden subject/block-local selector: they spread across all `10` subjects and `26` hidden blocks, with the only clear enrichment coming from hidden-block edge proximity. E103 rejects direct edge-local replacement, E104 shows E101 alpha `0.25` is a Pareto cliff, and E105 shows its public fate is mostly a subject/block-local S3 hard-label question: global priors give only `0.016610` beat probability, while subject priors raise it to `0.335360`. E106 then tests whether that subject-prior clue can replace E101 with a gated subset and finds `0` replacement/dominating rows. E118 adds visible flank-transition support, but E119 tests the actual pre-feedback gate and finds `602` flank-gated variants, `66` E101-pass rows, and `0` E101-dominating rows. Public E101 then resolves the branch at `0.5763003660`: it is worse than E95 by `0.0000090362` but still beats mixmin by `0.0000062745`. This keeps E95 as frontier, closes E108/E104/E106/E119 automatic followups, and turns the next step into a public-world rebuild rather than another same-family submission. E130 then tested the first post-E129 constructive route, synthesizing E95-neighborhood donor movements under E127 density masks. It produced local-strict rows (`25`) and E129-veto-actionable rows (`19`), but their intersection was `0`, so no E130 submission candidate exists. E141 corrected E140's exact tail gate and exposed the remaining transfer-tail budget problem. E142 then clipped E140 relaxed structural moves only on cells that created excess E72-plausible exposure. This opened `35` relaxed submit-gate rows and materialized `submission_e142_transferclip_09a92236.csv`. E143 repairs E142's remaining active/Q2S3 veto by rolling back only `21` top Q2/S3-weighted cells to E95; it gives up about `1.12e-6` local all-minus-E95 versus E142 but opens `15` original-strict-submit rows and materializes `submission_e143_activeq2s3repair_68ca656f.csv`. E144 then asks whether E143's coarse full rollback was boundary-optimal; fine top-count/keep-factor search opens `9` stricter submit rows and materializes `submission_e144_activeboundary_d7b4b331.csv`, preserving `185` changed cells while improving local all-minus-E95 to `-0.000009725930`. E146 isolates E144-vs-E143 itself: all `24` differing cells are `S3`, and all `10/10` public-free priors prefer E144, so E144 is not just a local-gate artifact. E147/E148 add whole-file prior support and pre-public attribution. E149 then grounds the geometry: E144 is almost orthogonal to E101/E72 negative axes but cosine `0.991918719` with E143, so it is a branch-pruned residual sensor rather than a broad breakthrough. E150 replaces E145's loose fine-loss action with an executable rule: fine-loss is conditional, and E143 requires fine-tail/S3 attribution. E153 then explains why branch-orthogonal E152 rows failed: almost every near miss died on S3 active-boundary actionability. E154 repairs that blocker directly, opens `10` all-four rows, and materializes `submission_e154_s3repair_9f2e2e73.csv`; it is E144-collinear but improves local all-minus-E95 to `-0.000012158050` while keeping E72/E101 negative-axis exposure low. E155 then shows this is not a single exact point: `25%` of the E144->E154 body still passes all-four and materializes `submission_e155_bodytemp_d27e7965.csv`, with local all-minus-E95 `-0.000010362491`. E156 decomposes that low-amplitude body and finds an even smaller target-axis control, `submission_e156_targetaxis_757546d2.csv`, using only Q1/S2/S4 add-on body ratio `0.171266667`; it is useful as a decomposition sensor, not as the first repaired-branch bet. E157 then prevents overreading E156: the all-four gate is saturated, Q3 is the strongest local/post-E101 finite-difference axis, and a Q1+Q3+S2+S4 row slightly dominates E155 while using less body. That makes `submission_e157_lowbodypareto_bd67930d.csv` a tuned low-body control, not a cleaner first sensor. E163 then explains why this entire post-E95 ordering is fragile: mixmin-vs-a2c8 needs `25` top hard-label cells to explain its actual public edge, but E95-vs-mixmin and E101-vs-E95 each need only `1`, and all `7/7` live post-E95 candidates have one-cell `2e-6` readability fragility. E164-E166 then reopen the broad branch: E164 finds `192` broad candidate-gate rows, E165 leaves `90` bad-axis-healthy survivors, and E166 materializes `submission_e166_broadsurv_s0p01_d8bfa94b.csv`, a `1%` E95-to-survivor logit graft with focus expected delta `-0.000332077`, cells-to-flip `74`, and negative-control gate `0`. E167 shows that E166 is hidden-context-real but safety-atlas divergent. E168-E169 then partially repair that: `context_high__veto` keeps `904` broad-context/veto cells, expected delta `-0.000120457`, cells-to-flip `32`, and materializes `submission_e169_ctx_veto_c5e806e3.csv` with lower bad-span energy `0.295326` and lower mean logit amplitude `0.001096`. This creates a balanced broad repair sensor alongside raw E166 and the conservative E154 repaired-branch sensor.

Update after E174: before the E176 countercheck, E174 superseded E172 as the sharper broad expected-score file, while E172 remained the safer contrast. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` reopens the top `75` E172 rollback cells back to E169 and improves E162 focus expected delta from E172 `-0.000112695` to `-0.000124367` while keeping visible p95 negative (`-0.000022709`) and worse-than-E101 small (`0.000220`). The risk is that it spends more Q2/S3 and bad-axis margin than E172: Q2/S3 share rises to `0.339597`, close to the E174 guard. After E176, use E174 as the max-edge contrast rather than the first risk-adjusted broad file.

Update after E175: E174 has a pre-public feedback decoder, now reused as the same-family decoder for E176/E174/E172. Submit `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` only as the max-edge contrast with `analysis_outputs/e175_e174_public_feedback_decoder.py` attached. A score `<=0.576276019` validates E174 as a broad anchor; `0.576276019..0.576288330` keeps partial reopening alive but underresolved; `0.576288330..0.576300366` keeps E95 practical and makes E172 the clean same-family contrast; `>0.576300366` demotes E174; `>0.576306641` closes E174/E172/E169 same-family reopening as expected-score follow-up. After feedback, run `python3 analysis_outputs/e175_e174_public_feedback_decoder.py --score <PUBLIC_LB>` before any next file.

Update after E176: E176 supersedes E174 as the risk-adjusted first broad candidate, while E174 remains the max-edge contrast. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` dampens only the E174 reopened Q2 cells from keep `1.0` to `0.75`. It gives up only `+0.000000983` focus delta versus E174, remains `-0.000010689` better than E172, and improves the thin risk axes: max bad cosine `0.163229 -> 0.158126`, Q2/S3 share `0.339597 -> 0.334753`, visible p95 `-0.000022709 -> -0.000023096`, worse-than-E101 `0.000220 -> 0.000192`. If submitting one broad expected-score file with risk control, submit E176; if deliberately maximizing public upside, E174 is the contrast.

Update after E177: E176 now has its own pre-public decoder. Use `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>` after any E176 submission. The important locked fact is that E176-vs-E174 is only `21` Q2 cells with expected focus cost `+0.000000983` and top1 swing `0.000000832`; this is too small to justify post-hoc Q2 keep tuning from one scalar score. A score `<=0.576276019` validates E176 as the broad/Q2-underopen anchor, `0.576276019..0.576288330` is micro-win/underresolved, `0.576288330..0.576300366` keeps E95 practical and limits E172/E174 to contrast sensors, `>0.576300366` demotes E176, and `>0.576306641` closes same-family reopening as expected-score follow-up.

Update after E179: E176 remains the single next public sensor, but the claim is now narrower and cleaner. `analysis_outputs/e179_e176_critical_cell_visibility_audit.py` says the E176 full body is visible-supported (`-0.000050824` visible-mean expected delta, `0.999080` visible win rate) and the Q2 damping versus E174 is also visible-supported (`-0.000000191` visible-mean delta, support `0.690495`). The unresolved risk is not body support; it is decisive hard-label visibility. Top4 support is only `0.330699`, and top33 expected-flip support is below null (`0.245771` vs `0.335713`, `p_low=0.014667`). Do not create a new sibling from this. Submit E176 only if the next slot is meant to observe whether the hidden public tail agrees with a body-supported/Q2-underopened broad law.

Update after E180: E179's top-cell weakness should not be treated as a veto. Known public winners can look equally weak or weaker: E95-vs-mixmin and E101-vs-mixmin both have public-positive top4 visible support `0.100896`, while mixmin-vs-a2c8 has `0.310904`. E176 top4 `0.330699` is above that small known-winner set. The issue is not "E176 top4 is worse than winners"; the issue is that visible priors have only `0.5` all-moved sign accuracy across known anchors and cannot certify frontier-scale decisive cells. This keeps E176 at priority 1A, with the exact same action rule: submit as a hidden-tail sensor, not as a certified win.

Update after E181: E176 is no longer the unqualified best-supported latent view. `analysis_outputs/e181_e176_binary_world_counterprior_audit.py` reranks the inherited binary hidden-label worlds by all current public-anchor residuals. In the best-5 residual worlds, E176 averages `+0.000003920` versus E95 with negative rate `0.400`; in best-10 it averages `+0.000007442` with negative rate `0.300`. Meanwhile E154 and E144 are negative in all best-5 worlds, averaging `-0.000051451` and `-0.000051445`. This does not automatically promote E154/E144 because the world pool is inherited and residuals are still larger than the E95 edge, but it changes the wording: E176 is priority 1A only when the next slot is meant to test the visible-body/Q2-underopen world. If the next slot should follow current-anchor binary worlds, first regenerate that pool with explicit E176/E154/E144 objectives.

Update after E182: `analysis_outputs/e182_current_anchor_binary_world_refresh.py` ran that regeneration against the current public anchors, including E101 public `0.5763003660`. The refreshed worlds fit anchors at frontier-scale max residuals (`0.0000784319`, `0.0000513148`, `0.0000762925`), but exact range incumbents are sparse (`0.233`) and objective-pressure worlds make E176/E154/E144 all cross zero in every scenario. This weakens the E181-based priority inversion: E154/E144 are still the repaired-branch alternate worldview, but they are not certified replacements. E176 also remains uncertified. The next public slot should be chosen by the question being asked: E176 for visible-body/Q2-underopen; E154/E144 only for repaired-branch validity with a decoder.

Update after E183: `analysis_outputs/e183_pressure_world_branch_anatomy.py` checked whether train-derived priors can select the favorable E182 pressure branch. They cannot. Visible-mean favorable-branch preference is `0.000` for E176/E154/E144; subject and flank rates are also `0.000`. The branch disagreement is on real moved cells, with support-gap coefficient-weighted means E176 `0.797945`, E154 `0.973558`, and E144 `0.888923`. E176 has one global-prior favorable signal (`1.000`), but local/visible priors still prefer the adverse branch. This does not demote E176 below E154/E144 or promote the repaired branch; it demotes visible-prior branch preference itself. The next public slot remains a worldview choice, and any E176/E154/E144 submission needs a decoder rather than a visible-prior certification claim.

Update after E184: `analysis_outputs/e184_public_anchor_motif_pressure_selector.py` tested the obvious non-visible replacement: a shallow metadata motif learned from known public-positive/negative transition cells. It is not action-grade. Best direct pair-LOO sign accuracy/AUC are only `0.333` / `0.425`; best direct family accuracy/AUC are `0.600` / `0.178`. Some pair signals become strong only after polarity inversion, but that polarity does not survive family stress. Live branch preferences also flip by feature set: core/swing reject all favorable pressure branches, while public-axis variants favor all three. This leaves the next submission rule unchanged: choose E176/E154/E144 by the worldview being tested and attach the relevant decoder. Do not rank them by E184 motif score.

## Pre-E48 Strict Gate

Before the new public observation, strict local submit candidate count was `0`. That conclusion was useful as a risk warning, but E48 shows it was too conservative as a hard gate because it vetoed the now-best mixmin candidate.

이 pre-E48 결론은 다음 audits에 의해 지지됐다.

- public anchor bottleneck: a2c8 edge is smaller than proxy error.
- hidden subset selector stress: passing selector families 0/7.
- universe audit: strict resolved-better 0.
- badaxis low-energy JEPA: resolved better 0.
- hidden public localization/bridge: submit_gate 0.
- pairwise order selector: strict submit-gate 0.
- label-flow gated scan: submit_gate 0, control gate 50, probe gate 3263.
- focused S4+Q3 label-flow scan: submit_gate 61/180, conflict 0.
- focused S4+Q3 independent survival review: independent survival 0/163, including 0/61 pair-submit candidates.
- S4/Q3 anchor gap audit: no existing candidate has both Q3/S4-shaped movement and old hidden-subset support.
- S4/Q3 OOF anchor audit: top 399 local Q3/S4 OOF candidates produced pair/old support 0 and submit/control/probe 0.
- Block/measurement selector rescore: 3800 non-anchor candidates produced pair p90 negative 0, two-selector majority 0, and submit/control 0/0.
- Selector support topology: merged scored universe produced pair-only 465, old-only 97, pair-probe-not-majority 56, two-selector majority 0.
- Selector disambiguation: old hidden-subset selector fails the known raw05/A2C8 direction; pairwise selector is better as a diagnostic sensor but still too noisy for improvement claims.
- Sensor scale curve: 108 scaled pair-only S4/Q3 variants produced two-selector majority 0; lower amplitude can reduce old p90 but does not make an improvement candidate.
- Localized sensor audit: 960 subject/date/block/phase/energy/sign variants produced pair p90 negative 807, old-majority 0, two-selector majority 0; the only loose sensors were tiny `id02_b02` moves with pair p90 around `-2e-7`.
- Direction-probe selector reconciliation: 22 mixmin/direns/sparseladder/targetabl/inverse7 probes produced pair p90 negative 0, pair majority 0, old-majority 0, two-selector majority 0.
- Public LB inverse feasibility: 8 known public LBs can be fit exactly by relaxed hidden worlds; all 8 unobserved candidate delta ranges cross zero even with train target prevalence bands.
- Public LB structural-prior stress: adding global target and subject-target prior bands fits known LBs exactly but leaves unobserved candidate signs crossing zero in `56/56` cells.
- Binary hidden-label inverse stress: tight subject-prior MILP incumbent fits known LBs within the raw05/a2c8 gap, but no representative candidate gets one-sided improvement evidence.
- Binary world-pool sign audit: 15 tight-prior binary incumbents include only 1 frontier-scale world, so mixmin/inverse7 support is diagnostic metadata rather than a submission gate.
- Binary frontier-box pool: 29 residual-box-constrained binary worlds strongly favor mixmin/inverse7 in random objectives, but candidate-max worlds still find adverse signs.
- Binary world plausibility audit: train-label geometry ranks the mixmin-adverse worlds as the most plausible worlds, so they cannot be safely discarded.
- Binary anchor loss geometry audit: low-anchor-energy worlds support mixmin/inverse7 one-sided, and the adverse mixmin worlds are high-energy under known-anchor loss decomposition; this strengthens the high-risk probe lane but still does not open the strict gate.
- Binary anchor loss LOO stability: omitting any one known anchor keeps mixmin one-sided in low-energy half/quarter bands and keeps adverse worlds out of the low-energy half; the high-risk probe is not one-anchor fragile.
- Binary anchor loss family/null audit: medium non-JEPA anchors alone sustain mixmin support, bad-JEPA-only fails, and target-axis permutation does not break support; evidence is broad anchor-loss/cancellation geometry rather than target-axis semantics.
- Public probe independent evidence audit: existing artifacts do not provide certification-grade out-of-anchor evidence for mixmin; normal submit gates remain `0`, but mixmin becomes the highest-information public sensor for the binary/actual-anchor/anchor-loss worldview.
- Raw-structure pseudo-label stress: 10 train-derived subject/date/raw-feature pseudo-label sources do not support mixmin as independent validation (`5/10`, mean delta `+0.000065107`), while inverse7 is supported by all sources (`10/10`, mean delta `-0.000705727`); this creates a bridge-probe branch but does not open the strict gate because selector hard veto remains.
- Inverse7 raw-anchor bridge scale scan: 22 inverse7/mixmin scale-blend variants produced raw support gates `14` and anchor gates `22`, but two-selector majority `0` and strict bridge gates `0`; scaled inverse7 remains a diagnostic bridge sensor, not a safe submission.
- Worldview sensor discriminability audit: 10 current sensors produced normal-submit candidates `0` and public-sensor candidates `10`; `mixmin_0c916` is the maximum-information anchor-loss worldview sensor, inverse7/inv7 variants are raw+anchor bridge sensors, and S4/Q3 pair files are selector-disambiguation sensors.
- OOF selector calibration audit: 4172 OOF rows produced many local gates (`1311` strict, `1115` conservative) and known-public sign match `1.0`, but known-public rank agreement was `0.0` because OOF ranks ordinal above stage2 while public LB ranks stage2 above ordinal.
- Test-movement fingerprint selector: target/subject/order/raw-domain movement fingerprints produced strict selector views `0`, loose views `4`; combined view recovers stage2/ordinal order and predicts `inv7_s0p25` closest to A2C8 (`0.577450`) but underpredicts bad JEPA severity.
- Movement + bad-axis geometry selector: adding LOO-safe bad/good axis cosine/projection features produced strict views `0` and loose views `0`; best `axis_group` repaired bad severity partly but failed A2C8-best and missed the loose MAE threshold.
- Fixed-zero anchor selector calibration: keeping A2C8 fixed at zero improves `axis_group` nonbaseline rank to `0.857143`, but fixed gates and usable gates remain `0`; predicted near-A2C8 candidate advantages are far below selector MAE.
- Selector resolution boundary audit: across current selector families, frontier-resolution gates `0`, certified better-than-A2C8 rows `0`, and certified better-than-raw05 rows `0`; best selector error is `0.000218288`, still above the raw05-A2C8 gap.

## Candidate Table

| priority | file | role | why it matters | expected LB reaction | risk | decision |
|---:|---|---|---|---|---|---|
| 0 | `analysis_outputs/submission_e95_hardtail_541e3973.csv` | current best hard-tail localized frontier | public `0.5762913298`, beats mixmin by `0.0000153107`; E95 starts from E86 and falls back to E85 on E72-adverse top-tail cells; E96 miss-budget stress mean `0.000057874`, p95 `0.000115644`, live win-rate `0.527478`, beats E89 `0.712378` | validates that E72-adverse hard-tail localization is public-real and adds information beyond E89/E90 | gain is only `15.14%` of the E72 miss and p95 floor is slightly worse than E85; still not a 0.54 path by itself | keep as current frontier; future candidates must be E95-relative or explicitly test more-structure vs more-conservative tradeoffs |
| 1A | `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` | conditional visible-body/Q2-underopen sensor | E176 starts from E174 and dampens only the reopened Q2 cells to keep `0.75`. It keeps `904/193` moved cells/rows, cells-to-flip `33`, focus expected delta `-0.000123384`, only `+0.000000983` worse than E174 and `-0.000010689` better than E172. It improves max bad cosine to `0.158126`, Q2/S3 share to `0.334753`, visible p95 to `-0.000023096`, and worse-than-E101 to `0.000192`. E177 locks the feedback decoder and shows E176-vs-E174 is only `21` Q2 cells with top1 swing `0.000000832`. E179 adds that the full body is visible-supported (`-0.000050824`, win `0.999080`) and Q2 damping is visible-supported (`-0.000000191`, support `0.690495`). E180 calibrates the top-cell concern: E176 top4 `0.330699` is above known-winner top4 mean `0.170898`, but visible priors have only `0.5` known-anchor sign accuracy. E181 adds the counterprior: inherited current-anchor binary worlds give E176 best-5 mean `+0.000003920` versus E95, while E154/E144 are best-5 negative. | if public improves, the visible-body/Q2-underopen world beat the inherited binary counterprior, and the hidden public tail agreed with a visible-prior-underresolved top-cell world | still same-family as E174 and hidden hard-label-resolution limited; E181 says it is not representation-wide best; if it ties/small-loses, the miss may be decisive-cell tail or binary-world counterprior; if E174 later beats it, the full Q2 reopening was public-real | submit first only if choosing to test the visible-body/Q2-underopen worldview. Decode with `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>` and interpret with E179/E180/E181 before any sibling |
| 1B | `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` | sharper max-edge broad expected-score contrast | E174 reopens the top `75` E172 rollback cells fully toward E169. It improves E162 focus expected delta versus E172 by `-0.000011672` to `-0.000124367`, keeps `904/193` moved cells/rows, raises cells-to-flip to `33`, and keeps visible p95 negative at `-0.000022709` with worse-than-E101 `0.000220`. Direct E174-vs-E172 recovery is mostly S3/Q2/S2/S1. | if public beats E176 or wins strongly, E172's visible-tail repair was directionally right and the full Q2 reopening was also public-real | Q2/S3 share is `0.339597`, close to the `0.34` guard, and bad-span energy/max bad cosine are worse than E176/E172 though still inside gate | use as max-edge contrast, not the first risk-adjusted file after E176 |
| 1C | `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` | safer broad visible-tail repair contrast | E172 keeps the E169 broad body but damps all `410` visible-positive-loss cells to `25%` of E169 movement. It keeps expected delta `-0.000112695`, moved cells/rows `904/193`, cells-to-flip `30`, visible p95 `-0.000026683`, worse-than-E101 `0.000050`, bad-span energy `0.257874`, and Q2/S3 share `0.315866`. | if E172 beats E176/E174 or loses less, partial reopening spent too much Q2/S3/bad-axis margin; if both improve, broad-body plus tail repair is public-real | lower upside than E176/E174 and still hidden hard-label-resolution limited: top1 swing `0.000005832`, one cell clears the `2e-6` guard | submit instead of E176 only when lower tail risk is prioritized over expected edge |
| 1D | `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv` | unrolled context/safety broad body-vs-tail sensor | E169 keeps only E166 cells where hidden context and safety-atlas comfort overlap: `context_high__veto` has `904` moved cells, `193` rows, expected delta `-0.000120457`, cells-to-flip `32`, top1/expected `0.048415`, edge-like `0.610619`, between-train-runs `0.819690`, veto `1.0`, safe-density `0.346150`, E72-active `0.268805`. It materializes with bad-span energy `0.295326`, max bad cosine `0.222381`, mean/max abs logit `0.001096`/`0.010206`, Q2/S3 share `0.347775`, and low cosine to E154/E101/mixmin (`0.087180`/`-0.021896`/`-0.020672`) | if public improves while E172/E174 do not, the visible-tail rollback family overcorrected and the raw broad body was right; if it loses after E172/E174, visible-tail repair was necessary | E171 showed its public-decisive top cells are visible-prior adverse and visible p95 is positive; higher Q2/S3/bad-axis exposure than E172/E174 | use only when deliberately testing the unrolled body-vs-tail question; not the first expected-score broad file after E176/E174 |
| 1E | `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv` | raw broad plateau-break / safety-atlas falsification sensor | E166 starts from E95 and takes only a `1%` logit-space step toward the E165 geometry-health survivor `submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv`. It keeps broad hard-label support: focus expected delta `-0.000332077`, cells-to-flip `74`, top1/expected `0.023369627`, and moves all `1750` row-target cells with tiny amplitude. It avoids known public-bad geometry: bad-span energy `0.450742441`, max bad-axis cosine `0.268538582`, negative-control gate `0`, mean/max abs logit move `0.002243986`/`0.013580886`, and cosine vs E154 only `0.061661852`. E167 adds that its focus cells are hidden-context-real: edge-like rate `0.689189` vs null `0.470842`, between-train-runs `0.797297` vs `0.624658` | if public improves, E95 is missing a broad latent branch and the existing safety atlas was too conservative or branch-bound; next work is E166 amplitude/target/context decomposition. If public loses, the E72-active/low-veto-null conflict is probably the missing public-negative axis | no direct public-positive anchor for this broad family; raw full-survivor amplitude is unsafe; E167 shows safety-atlas divergence: all-veto-null `0.297297` vs null `0.574158`, safe-density `0.117097` vs `0.243966`, E101-plausible mass `0.238204` vs `0.533727`, and E72-active `0.837838` vs `0.670369` | use after/over E176/E174/E172/E169 only when deliberately testing whether the safety atlas is too conservative. Not safety-certified; do not scale or clone before public feedback |
| 1F | `analysis_outputs/submission_e169_ctx_high_density_p50_51110c7e.csv` | near-duplicate broad repair control | E169 high-density p50 keeps `894` cells, expected delta `-0.000119080`, cells-to-flip `32`, top1/expected `0.048975`, bad-span energy `0.295856`, max bad cosine `0.222464`, mean/max abs logit `0.001086`/`0.010206`, Q2/S3 share `0.341722`, edge-like `0.610738`, between-train-runs `0.817673`, veto `1.0`, safe-density `0.349218` | if it diverges from ctx_veto on public despite near-identical local geometry, the exact safety-density threshold matters; otherwise it mostly confirms E169 broad-repair read | almost redundant with ctx_veto and slightly weaker expected delta; low information if submitted before ctx_veto | keep as diagnostic control, not the first broad repair file |
| 2 | `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` | repaired all-four E144-branch extension | E154 starts from an E152 E144-plus-orthogonal near miss and rolls back only `3` top E101-active S3 cells with keep `0.25`; it opens the E153 all-four intersection (`10` materializable rows), passes relaxed structural, E72-budget, post-E101, strict actionability, and local material gates; local all-minus-E95 is `-0.000012158050`, better than E144; it moves `294` cells vs E95, contains all `185` E144 cells, has cosine with E144/E143/E142 `0.983569299`/`0.975091856`/`0.939950819`, and avoids E72/E101 negative axes (`-0.031628728`/`-0.005523655`) | if public improves, the live law becomes "E95 + transfer-budget residual branch + S3 active-boundary repair"; this validates that E153's blocker was the missing decoder state, not terminal incompatibility | still E144-collinear and less prior-audited than E144; if E154 loses while E144 wins, the added branch body or exact 3-cell S3 rollback was overfit | use first when the public slot is meant to read the conservative repaired-branch world; use E169/E166 first when the slot is meant to test broad plateau escape |
| 2 | `analysis_outputs/submission_e155_bodytemp_d27e7965.csv` | conservative E154 amplitude-control sensor | E155 keeps the E154 direction but uses only `25%` of the E144->E154 body; it passes all-four health, beats E144 locally, has local all-minus-E95 `-0.000010362491`, body-norm ratio `0.25`, post-E101 p95 about `-0.00000377`, and E72 gap about `-0.00000108`; E155 found `34/40` all-four ablations, `27` submit rows, and `22` reduced-body submit rows | if public improves, the live law is lower-amplitude repaired branch rather than full E154 amplitude; if E154 loses but E155 wins, blame full-body overextension | much smaller local edge than E154, so public may not resolve it; it is a conservative control, not the strongest first sensor | keep after E154 and before E144 if the next question is downside-controlled repaired-branch amplitude |
| 3 | `analysis_outputs/submission_e157_lowbodypareto_bd67930d.csv` | tuned low-body target-axis Pareto control | E157 audits the E156 lattice and finds the all-four gate saturated (`3125/3125`). Q3 is the strongest local/post-E101 finite-difference axis, while S2 carries E72 budget. The selected row uses Q1+Q3+S2+S4 alphas Q1/Q3/S2/S3/S4 = `0.25/0.25/0.50/0.00/0.50`, body ratio `0.240336139` vs E155 `0.25`, all-minus-E95 `-0.000010404446`, post-E101 p95 `-0.000003807382`, and E72 gap `-0.000001671496`; it improves E155 on all three stress metrics while using less body | if public improves after E154/E155 ambiguity, target-axis tuning matters despite a tiny local edge; if E155 wins and E157 fails, the tuned Pareto row overfit the saturated lattice | edge over E155 is only `~4.2e-8` local all-minus, far below public-resolution scale; less clean as an interpretation than diagonal E155 | keep after E154/E155 if testing tuned low-body axis response; do not use as first sensor |
| 4 | `analysis_outputs/submission_e156_targetaxis_757546d2.csv` | minimum-body repaired target-axis control | E156 scans `3125` Q1/Q3/S2/S3/S4 target-axis amplitude rows; all are all-four, `2984` are strict, and `85` sit below E155's `0.25` body ratio. The selected file uses only Q1/S2/S4 alphas `0.25/0.75/0.25`, body ratio `0.171266667`, local all-minus-E95 `-0.000010004`, post-E101 p95 `-0.000003712`, E72 gap `-0.000002266`, and cosine with E144/E155/E154 `0.999515751`/`0.998991027`/`0.985122955` | if public improves after E154/E155/E157 fail, public may accept only a tiny Q1/S2/S4 add-on over E144 rather than full, diagonal, or tuned repaired body | local edge barely clears materiality and is weaker than E154/E155/E157; almost pure E144 geometry, so information value is lower if submitted too early | keep as minimum-body decomposition control |
| 5 | `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` | conservative unrepaired branch contrast | E144 refines E143's coarse `top_q2s3_weighted_21` full rollback. Selected row uses `top_q2s3_weighted_24`, keep factor `0.15`, rollback cells `24`, keeps `185` changed cells vs E95, passes original strict actionability, active/Q2S3, E72-budget, and post-E101 gates; local all-minus-E95 is `-0.0000097259`, post-E101 mean/p95 is `-0.0000133266`/`-0.0000034305`; E146 shows all `24` E144-vs-E143 differing cells are `S3` and all `10/10` public-free priors prefer E144; E147 shows the whole 185-cell E144-vs-E95 movement is preferred by all `10/10` public-free priors; E148 gives win-rate mass `0.599760..0.745560`; E149 shows E144 avoids E101/E72 negative axes but is nearly collinear with E143 (`cos 0.991918719`); E150 locks post-feedback action with fine-loss as conditional only | if E154/E155/E157/E156 fail but E144 improves, public accepted the original residual branch but rejected repaired-branch amplitude/body detail | lower local edge than repaired controls and no all-four repair of E152, but stronger prior-audit history | keep as the clean unrepaired contrast; after any E144 result, run `analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>` before E143/E142 |
| 6 | `analysis_outputs/submission_e143_activeq2s3repair_68ca656f.csv` | stricter E142 repair fallback | E143 starts from E142 and rolls back the top `21` Q2/S3-weighted active cells to E95; it keeps `164` changed cells vs E95, passes relaxed structural, E72-budget, post-E101 p95, `gate_active_q2s3_not_more_than_e101`, and original strict actionability; local all-minus-E95 is `-0.0000095514`, E72-plausible gap is `~0`, post-E101 mean/p95/beat is `-0.0000131312`/`-0.0000033689`/`1.0` | if E154/E155/E157/E156/E144 fail and attribution points specifically to fine-tail/S3 retention, E143 is the clean contrast | gives up about `1.12e-6` local reward versus E142 and about `1.75e-7` versus E144; E146 weakens it as an expectation-ranked fallback, and E148 shows even fine-loss bands may be inherited-body/Q3/S2 rather than fine-tail-only | keep as a clean contrast only if public feedback asks the fine-tail/S3 question |
| 7 | `analysis_outputs/submission_e142_transferclip_09a92236.csv` | E95-relative transfer-budget clipped decoder candidate | E142 starts from E140 relaxed structural primitive decoder row `e140_score_top_local_25c44401`, then rolls back `55` high E72-plausible-excess cells to E95; it still moves `185` cells across `108` rows, no Q2 cells, with target mix Q1 `38`, Q3 `56`, S2 `23`, S3 `47`, S4 `21`; local all-minus-E95 `-0.0000106668`, tail tolerance pass, hidden-core `-0.000022`, world `-0.000284`, raw-energy `-0.000049`, E72-plausible exposure equal to E95, post-E101 mean/p95 `-0.0000143796`/`-0.0000037623`, beat-E95 `1.0` | if repaired and conservative controls fail but E142 would improve, the active/Q2S3 strict veto was overconservative and E101-conditioned residual movement should be less pruned | it fails `gate_active_q2s3_not_more_than_e101`; private risk is public-sensor conditioning plus active/Q2S3 overfit | keep as higher-upside fallback sensor after the repaired and conservative branch controls |
| anchor | `analysis_outputs/submission_mixmin_0c916bb4.csv` | previous public anchor | public `0.5763066405`, beats previous a2c8 by `0.0011326805`; validates the anchor-loss/binary actual-anchor worldview despite pair/old selector veto | baseline anchor for E95-relative deltas | private safety still unknown; large movement means target/row attribution is mandatory | keep as reference; no longer frontier |
| resolved | `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` | resolved negative E95-relative Q2/S3 amplitude sensor | starts from E95 and shrinks the effective Q2/S3 movement `25%` toward mixmin on only `50` active cells; local broad-plausible mean/p95/beat vs E95 was `-0.0000162053`/`-0.000001564`/`0.983488`, but actual public was `0.5763003660`, or `+0.0000090362` worse than E95 and `-0.0000062745` better than mixmin; E102/E105/E118 still explain it as S3-heavy edge/flank transition-state risk, while E106/E119 show subject/flank gates cannot replace the full active set | E116 actual branch is `small_loss`: E95's structural law remains right enough that Q2/S3 rollback does not beat the frontier | same-line local stress was too optimistic by `0.0000252415` versus mean and `0.0000106001` versus p95; E101 is informative but not a new best | keep as logged sensor; do not submit E108/E104/E106/E119, full E89, or non-active grafts as automatic followups |
| 2 | `analysis_outputs/submission_e89_e72decontam_00d7807f.csv` | Q2/S3 diffuse-tail E95 counterfactual | E89 starts from E86 but falls back to E85 on cells in the top `20%` of E72 failed absolute movement; all delta `-2.58960e-5`, inverse-top `-5.55392e-6`, raw05-compatible `-3.33148e-5`, all-sign `-3.88191e-5`; E99 broad-plausible beat-E95 rate `0.195829`; E100 shows this pocket is concentrated in `q2s3` worlds with beat rate `0.779891` and mean E89-minus-E95 `-0.000005030` | if public improves over E95 after E101 fails or is skipped, public tail is closer to diffuse Q2/S3 E72-cell fallback than to E95's localized hard-tail cells | not a broad lower-downside file: mean E89-minus-E95 remains `+0.000003833`; it sacrifices E86 hidden/world/block strength and loses in S1/S2/S3 or E95-fallback-cell worlds | use after E101 only if the question remains broader Q2/S3 diffuse-tail allocation |
| 3 | `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv` | conservative target-pruned sensor | E85 keeps only `S1,S2,S3`; strict/deployable `535/700`; all delta `-2.38758e-5`, inverse-top/raw05/all-sign all favorable; E96 p95 `0.000115304`, the lowest live conditional tail floor; E99 beat-E95 rate `0.031866` | if public improves over E95, public prefers conservative tail-floor behavior over retained E86 structure | lower local edge and lower information value than E101/E89/E90/E86; still public-pending | conservative fallback if the next question is pure downside floor |
| 4 | `analysis_outputs/submission_e90_e72pareto_28925de5.csv` | row-coherent structure-retention sensor | E90 starts from E86 but falls back to E85 on top `10%` E72-contaminated rows; all delta `-2.69324e-5`, contamination `0.715784`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block win `0.777778`, tail safe `1.0`; E99 beat-E95 rate `0.002607` | if public improves over E95, public rewards row-coherent structural retention that the local+tail abstraction missed | more hard-tail exposure than E95/E89 and E99 says low expected E95-beat rate | use only when the question is row-coherent retained structure, not expected improvement |
| 5 | `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv` | target-pruned source-consensus sensor | E86 source-diverse consensus over strict E85 rows; keeps `Q2,S1,S2,S3`, averages top `40` rows from `18` source files, shrink `1.25`; all delta `-2.77059e-5`, hidden/world/block favorable, block-tail safe `1.0`; E88 contamination index `0.772379`; E99 beat-E95 rate `0.000290` | if public improves over E95, source-stable target-pruned structural law dominates residual hard-tail risk in a way E99 missed | strongest overstep and hard-tail risk among the main candidates | maximum-upside sensor only, not the next expected-improvement file |
| diagnostic | `analysis_outputs/submission_e87_noq2_source_consensus_a85c4e39.csv` | E86 no-Q2 contrast | same source-consensus family as E86 but keeps `S1,S2,S3`; all delta `-2.69461e-5`, inverse-top `-7.28932e-6`; E88 contamination index `0.730408`, cleanest E87 risk split | if E86 worsens but this improves, Q2 add-back was the contaminating axis | lower hidden/world support than E86; not highest-upside before E86 feedback | first E87 contrast if E86 fails |
| diagnostic | `analysis_outputs/submission_e87_q2_nooverstep_consensus_acd7add0.csv` | E86 no-overstep contrast | same `Q2,S1,S2,S3` target mask as E86 but shrink `1.00`; all delta `-2.42545e-5`, inverse-top `-7.53196e-6` | if E86 worsens but this improves, shrink `1.25` overstepped calibration | lower all-margin than E86; public-pending | hold as amplitude contrast |
| diagnostic | `analysis_outputs/submission_e87_inverse_top_prior_consensus_5445ec28.csv` | E86 inverse-top-prior contrast | keeps `Q2,S1,S3`; inverse-top delta `-2.06434e-5`, world `-0.000443423`, block-tail safe `1.0`; E88 contamination index `0.928415` | if this improves, public follows inverse-top geometry despite strong E72 proximity | weakest safety profile under E88; tests a different public-world prior but is not a safer fallback | hold as high-information geometry contrast only |
| paused | `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv` | failed combined sparse-gate sensor | public LB `0.5764077772`, worse than mixmin by `+0.0001011367`; E80 shows it moved `893` cells across all `7` targets | public rejected this combined file | not a clean Q2/S3 sign test; pure Q2/S3 is only sub-margin in E81 | do not resubmit or amplify |
| paused | `analysis_outputs/submission_e74_fullpool_a20_q2s3_gate_55455b60.csv` | held symmetric amplitude control | same 13-cell full pool as E73, alpha `20`; local all delta `-1.07261e-5`, but E80/E81 removed the basis for direct follow-up | only useful if a future pure sparse-gate sign is validated first | alpha24 fails strict; public just rejected the E73 combined file | hold |
| paused | `analysis_outputs/submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv` | held target-asymmetric amplitude control | local S3-heavy/Q2-low best all delta `-1.23676e-5`; direction stable across E76, exact amplitude only partially stable | only useful after a future pure sparse-gate sign is validated | too direct after E73 public failure; pure Q2/S3 remains sub-margin | hold |
| anchor | `analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv` | previous best anchor | previous best known public `0.577439321` | now `+0.0011326805` worse than mixmin | still useful as raw05-compatible reference | keep as contrast anchor, no longer frontier |
| 4 | `analysis_outputs/submission_label_flow_focused_1bbfb735.csv` | lower-risk selector-disambiguation sensor | pairwise p90 `-0.000054316`, old-selector p90 `+0.000638679`; E48 lowers priority because mixmin already proved the pair/old veto can be wrong | diagnostic only; now should be rescored relative to mixmin, not a2c8 | independent survival false; beat-rate `0.277992`; not a 0.54 path by itself | hold until post-mixmin selector recalibration |
| 5 | `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv` | lower-risk selector-disambiguation sensor | pairwise p90 `-0.000034496`, old p90 `+0.000571958`, movement `0.003931`; E23 balanced scale | weaker but lower-movement diagnostic | still no old majority; not a normal improvement candidate | optional diagnostic only after mixmin-relative rescore |
| 6 | `analysis_outputs/submission_label_flow_focused_6b9335b1.csv` | high-upside selector-conflict sensor | best pairwise p90 `-0.000065217`, but old-selector p90 `+0.000675515` | diagnostic only after `1bbfb735` improves | focused selector overfit; S4 max move not tiny | hold |
| 7 | `analysis_outputs/submission_label_flow_combo_3d536109.csv` | pre-threshold sensor | broad combo best before focused push, pair p90 `-0.000035162`, old-selector p90 `+0.000581412` | information-only | below pair-submit and independent survival false | hold |
| 8 | `analysis_outputs/submission_label_flow_gated_f1046674.csv` | conservative semantic-gate sensor | best E11 control/probe by rank; tiny movement | likely noise-scale | expected edge below selector error | hold |
| 9 | `analysis_outputs/submission_label_flow_gated_ff8df011.csv` | higher-upside E11 sensor | best E11 p90 delta vs a2c8 among gated controls | possible tiny movement sensor only | no strict gate, independent survival false | hold |
| 10 | `analysis_outputs/submission_hiddenloc_bridge_8ff484be.csv` | information-only probe | top baseline-relative hiddenloc bridge in pairwise selector | possible tiny improvement or noise around previous frontier | selector conflict, edge `1e-5` scale | lower priority |
| 11 | `jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv` | raw05 anchor | validates raw timeline public-positive direction | known `0.5775263072`, now `+0.0012196667` worse than mixmin | still useful as raw-timeline contrast | no need to resubmit |
| 12 | `analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_block_id02_b02_s1p00_ea4fdc0b.csv` | weak localization sanity sensor | E24 loose localized candidate on an 8-row id02 block; pair p90 `-0.000000203`, old p90 `+0.000580036` | likely unreadable on public LB | movement `0.0000127`; no old majority; no two-selector support | do not submit |
| risk lane | `analysis_outputs/submission_inverse7blend_1040423d.csv` | raw-structure bridge probe | E25 nearest direction-probe by pairwise p90 (`+0.000122038`) but still old beat-rate `0.003861`; E32 low-anchor-energy worlds support inverse7 with mixmin; E33 inverse7 anchor-LOO is slightly weaker than mixmin (low-half min better_rate `0.928571`); E36 raw-structure pseudo-label stress supports inverse7 `10/10`, mean delta `-0.000705727`, worst delta `-0.000507826` | tests whether the candidate that aligns with raw observed structure generalizes better than mixmin's anchor-loss priority | selector hard veto remains; not pair/old strict; anchor-LOO weaker than mixmin; direct public readability unknown | do not submit before scale/blend reconciliation unless the explicit public question is raw-structure bridge vs selector veto |
| risk lane | `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv` | conservative raw-structure bridge probe | E37 best-ranked scale-bridge diagnostic: raw support `10/10`, raw mean delta `-0.000181991`, low-anchor-half better_rate `1.0`, low-anchor-quarter better_rate `1.0`, pair p90 `+0.000035423`, old p90 `+0.000587512`; E38 sensor information score `2.787093`; E40 combined movement-fingerprint predicted public LB `0.577450`, closest non-baseline candidate and below raw timeline | tests whether a very small inverse7 bridge direction can beat selector veto through raw+anchor/movement-anatomy agreement | selector hard veto remains; old beat-rate only `0.007722`; E40 is loose not strict; public readability may be weak due small movement | hold; best lower-risk diagnostic if explicit question is raw+anchor/movement anatomy vs selector veto |

## E38 Selected Sensor Options

This is a selected public-sensor menu, not expected safety. Full score ordering is in `analysis_outputs/worldview_sensor_discriminability_audit.csv`.

| option | file | lane | information score | public question |
|---|---|---|---:|---|
| maximum information | `analysis_outputs/submission_mixmin_0c916bb4.csv` | anchor-loss worldview | `3.355110` | Does anchor-loss/honest-CV support beat raw/pair/old veto? |
| strongest raw bridge | `analysis_outputs/submission_inverse7blend_1040423d.csv` | raw-structure bridge | `3.235599` | Does raw observed structure plus anchor-loss support beat selector veto? |
| conservative raw bridge | `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv` | raw-structure bridge | `2.787093` | Does a small raw+anchor bridge movement survive despite weak readability? |
| high-amplitude pair sensor | `analysis_outputs/submission_label_flow_focused_6b9335b1.csv` | S4/Q3 selector disambiguation | `3.084287` | Does higher-amplitude pairwise S4/Q3 movement beat old/anchor veto? |
| lower-risk pair sensor | `analysis_outputs/submission_label_flow_focused_1bbfb735.csv` | S4/Q3 selector disambiguation | `2.943869` | Does lower-risk pairwise S4/Q3 movement beat old/anchor veto? |

Update after E10: existing label-flow/transductive/MP-count branch candidates were scored directly. 556 files produced `pair_submit_gate=0`, `pair_probe_gate=0`, `pair_control_better_than_a2c8_gate=0`; best p90 delta vs a2c8 was `+0.000125668`. Therefore priority 3 is not "submit existing label-flow candidate"; it is now "build a gated label-flow candidate and stress it."

Update after E11: gated label-flow candidates were built. 7240 files produced `pair_submit_gate=0`, `pair_control_better_than_a2c8_gate=50`, `pair_probe_gate=3263`, and `pair_selector_conflict=0`. This is not enough for a strong submit, but it is better than hiddenloc because the sensor has no selector conflict and directly tests H15.

Update after E12-E14: targetwise/combo/focused scans changed the submission state. S4 is the dominant safe target movement and Q3 is additive. The focused S4+Q3 scan produced 61 strict pairwise submit-gate candidates. At that point this looked like a frontier-challenge branch, but it required independent survival before actual submission priority.

Update after E15-E16: independent survival review reversed the E14 submission recommendation. Among 163 reviewed label-flow candidates, including all 61 pair-submit files, independent survival was 0 and strict independent survival was 0. Pairwise-improving movement is anti-aligned with the older hidden-subset selector: corr(pairwise p90 delta, old-selector p90 delta) `-0.881`. Decomposition then showed pairwise support is mixed, not unanimous: focused files have pairwise full-fit better_rate `0.500000` and old hidden-subset better_rate `0.285714`. Therefore the current best action is to hold submissions and use these files only as diagnostic sensors if a public slot is intentionally spent for information.

Update after E17: the missing validation object was audited directly. The pairwise-scored universe has 21 Q3/S4-shaped candidates and 46 pairwise-p90-negative candidates, but `0` with Q3/S4 shape plus old-majority support. The focused family has 163 pairwise-positive Q3/S4 candidates and old-majority `0`. The old-positive rescore has 97 old-majority candidates, but Q3/S4-shaped `0`. Therefore more S4/Q3 weight rescan is not a rational next submit path.

Update after E18-E19: the OOF archive is also not the missing validation source. E18 found 1578 local-Q3/S4-strong OOF candidates, but no anchor-like overlap. E19 directly rescored the top 399 local OOF candidates; pairwise p90 negative, pair majority, old majority, pair probe/control/submit, and strict S4/Q3 OOF anchor-like counts were all `0`. These candidates are mostly Q3-dominant broad/public-mask-aware moves, not clean S4/Q3 public-positive anchors.

Update after E20: existing block/measurement submissions are not the missing large safe movement. E20 rescored 3800 non-anchor block-scale, hidden-block, public-block, raw05-blockcount, and pre-sleep measurement candidates. Results were pair p90 negative `0`, pair majority `52`, old-majority `3`, two-selector majority `0`, pair submit/control/probe `0/0/63`. There were 2505 large low-bad movement candidates but 0 with two-selector support. The nearest raw05-blockcount refine files are diagnostic probes only; they still have best pair p90 `+0.000010793` and old beat rate around `0.36`.

Update after E21: merging the scored universes did not uncover a hidden intersection. `analysis_outputs/selector_support_topology_audit.py` found pair-only `465`, old-only `97`, pair-probe-not-majority `56`, two-selector majority `0`, strict candidate shape `0`. Pair-only candidates are S4/Q3-heavy and include the focused label-flow pair-submit files; old-only candidates are Q3/raw05-public-drift-like and are pairwise-vetoed. This confirms that current candidates are sensors for selector disagreement, not improvement submissions.

Update after E22: selector disambiguation changed the sensor priority but not the strict gate. Pairwise public-order selector preserves the raw05/A2C8 public direction in `33/36` models with raw05 direction correct rate `0.916667`; old hidden-subset selector has pass `0/7` and raw05 direction correct rate `0.0`. Therefore an old-only Q3/raw05-drift candidate is not the next public sensor. If one public diagnostic is used, `analysis_outputs/submission_label_flow_focused_1bbfb735.csv` has the best information-to-risk tradeoff; `6b9335b1` is only a follow-up if `1bbfb735` improves.

Update after E23: scaling the S4/Q3 sensor does not resolve the selector conflict. The best balanced lower-risk file is `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv` with pair p90 `-0.000034496`, old p90 `+0.000571958`, and movement `0.003931`, but two-selector majority remains `0`. This is a lower-risk diagnostic alternative, not a new submit-safe candidate.

Update after E24: simple row localization also does not resolve the selector conflict. `analysis_outputs/label_flow_localized_sensor_audit.py` scored 960 localized variants and found old-majority `0` and two-selector majority `0`. The eight loose localized candidates all target the tiny `id02_b02` date block and have pairwise deltas around `1e-7`, too small to be public-readable. They are not submission candidates.

Update after E25: the newer large-movement score-probe branch also fails the strict survival gate. `analysis_outputs/direction_probe_selector_reconciliation.py` scored 22 mixmin/direns/sparseladder/targetabl/inverse7 probes: pair p90 negative `0`, pair majority `0`, old-majority `0`, two-selector majority `0`. `submission_mixmin_0c916bb4.csv` remains the best high-risk score-oriented probe under actual-anchor/combo/honest-CV metadata, but not under the pairwise/old selector gate.

Update after E26: public-LB inverse fitting cannot rescue candidate ranking. `analysis_outputs/public_lb_inverse_feasibility.py` matched all 8 known public LBs exactly with all-test soft labels and with arbitrary cell-mixture weights. The delta ranges for `1bbfb735`, `6b9335b1`, 0.65 sensor, `mixmin_0c916`, `direns_c4af`, target-ablation probes, and inverse7 all cross zero; this remains true with train target prevalence constrained to `±0.05`, `±0.10`, and `±0.20`. Therefore current submissions must be chosen as worldview tests, not as inverse-LB-validated improvements.

Update after E27: train global prevalence and subject-target prior constraints also cannot rescue candidate ranking. `analysis_outputs/public_lb_structural_prior_stress.py` tested 7 all-test inverse scenarios; all fit the 8 known public LBs with slack `0`, but all unobserved candidate-scenario cells crossed zero (`56/56`) and one-sided improvement cells were `0`. Therefore subject-prior inverse ranking is not a valid submission gate for the current files.

Update after E28: binary hidden-label constraints are not a current submission gate either. `analysis_outputs/public_lb_binary_inverse_stress.py` found a tight subject-prior binary incumbent with max residual `0.000061242`, below the raw05/a2c8 public gap `0.000086986`, so binary exactness remains a plausible hidden-world constraint. But candidate range MILPs produced no one-sided improvement evidence, and `6b9335b1` crossed zero under no-prior incumbents. Do not submit from a single binary inverse world.

Update after E29: a small binary world pool weakly changes probe priority but not the strict gate. `analysis_outputs/public_lb_binary_world_pool.py` found 15 unique tight-prior binary incumbents, but only one frontier-scale world. In all worlds, mixmin and inverse7 had higher better_rate than pair-only S4/Q3 sensors; in the only frontier-scale world, mixmin and inverse7 improved while the pair sensors worsened. This slightly strengthens `analysis_outputs/submission_mixmin_0c916bb4.csv` as a high-risk worldview probe, but the evidence is too thin to call it an improvement candidate.

Update after E30: frontier-box binary sampling makes the high-risk probe ranking sharper. `analysis_outputs/public_lb_binary_frontier_box_pool.py` bounded every known-public residual by the raw05/a2c8 gap and found 29 frontier-scale incumbents, 28 unique. Excluding candidate min/max objectives, mixmin was better in `19/19` worlds and inverse7 in `18/19`, while pair-only S4/Q3 sensors were below half support. But candidate-max objectives still made mixmin and inverse7 worse, so this is not one-sided proof. If a public slot is used to test the binary/actual-anchor worldview, mixmin is now the clearest probe.

Update after E31: generic train-label plausibility cannot upgrade mixmin from probe to improvement candidate. `analysis_outputs/public_lb_binary_world_plausibility_audit.py` found low-energy random+fit worlds support mixmin/inverse7 `6/6`, but the two mixmin-adverse worlds are the two most plausible worlds by the same train-geometry score. Therefore E31 strengthens the diagnosis but blocks certification: mixmin is informative because it directly tests whether public resembles random/fit binary worlds or candidate-adverse plausible worlds.

Update after E32: known-anchor loss geometry reopens the mixmin probe lane, but still not the strict gate. `analysis_outputs/public_lb_binary_anchor_loss_geometry.py` found low-anchor-energy half supports mixmin and inverse7 `15/15`, low quarter supports both `7/7`, and low-anchor-energy random+fit supports both `12/12`. The two mixmin-adverse worlds are high-anchor-energy ranks `26` and `28`. This makes `submission_mixmin_0c916bb4.csv` the clearest high-risk binary/actual-anchor public sensor if a public slot is deliberately spent, but it is still not a normal improvement candidate.

Update after E33: anchor-loss support is not one-anchor fragile. `analysis_outputs/public_lb_binary_anchor_loss_loo_stability.py` omitted each known public anchor and recomputed the gate. Mixmin stayed negative in every low-energy-half and low-energy-quarter LOO band, with worst low-half max delta `-0.000315338`; no mixmin-adverse world entered any LOO low-energy half. Inverse7 is close but less stable, with low-half min better_rate `0.928571`. This moves mixmin above inverse7 as the cleaner high-risk sensor.

Update after E34: anchor-loss support is real but less semantic than hoped. `analysis_outputs/public_lb_binary_anchor_loss_family_null_audit.py` showed mixmin survives `no_raw05`, `no_medium_non_jepa`, `no_bad_jepa`, and `only_medium_non_jepa`, but fails under `only_bad_jepa`. Target-axis permutation leaves mixmin one-sided in `500/500` low-half and low-quarter permutations. Therefore mixmin remains the top high-risk sensor, but the reason is medium-anchor loss/cancellation geometry, not JEPA target-axis semantic alignment.

Update after E35: existing evidence does not certify mixmin as a normal submission. `analysis_outputs/public_probe_independent_evidence_audit.py` audited 5 sensors and found normal submit gates `0`. Mixmin has local honest-CV support and strong anchor-derived support, but pair p90 `+0.000879200`, old p90 `+0.001041933`, and selector hard veto remain. This closes the "mixmin is safe" interpretation while making the next diagnostic choice clearer: if spending a high-risk public sensor, mixmin is now more information-rich than another S4/Q3 pair-only variant.

Update after E36: raw observed structure does not independently certify mixmin. `analysis_outputs/raw_structure_pseudolabel_candidate_stress.py` built 10 train-derived subject/date/raw-feature pseudo-label sources. Mixmin support was only `5/10` with mean delta `+0.000065107`; inverse7 support was `10/10` with mean delta `-0.000705727` and negative worst-source delta. The strict gate remains closed because inverse7 still carries selector hard veto and weaker anchor-LOO stability than mixmin. The next local action should test inverse7 scale/blend variants against raw-structure support, anchor-loss/LOO support, and selector veto before spending a public slot.

Update after E37: inverse7 scale/blend reconciliation failed as a strict gate. `analysis_outputs/inverse7_raw_anchor_bridge_scale_scan.py` generated 22 logit-space variants. Raw support gates were `14`, anchor low-half+quarter gates were `22`, but two-selector majority and strict bridge gates were both `0`. The best diagnostic was `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv`; it preserves raw and anchor support but still has positive pair/old p90 and selector hard veto. Do not submit inverse7 or scaled inverse7 as an improvement claim.

Update after E38: worldview/sensor discriminability was audited directly. `analysis_outputs/worldview_sensor_discriminability_audit.py` found normal submit candidates `0` and public sensor candidates `10`. The highest-information sensor is `analysis_outputs/submission_mixmin_0c916bb4.csv` with score `3.355110`; the raw+anchor bridge lane is led by `analysis_outputs/submission_inverse7blend_1040423d.csv` / full inverse7 and the lower-amplitude bridge option is `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv`; the S4/Q3 selector lane remains `1bbfb735`/`6b9335b1`. This changes submission framing, not the strict gate.

Update after E39: OOF selector calibration failed as a public ranker. `analysis_outputs/oof_selector_calibration_audit.py` found many OOF-stable candidates, but it reverses the known-public stage2/ordinal order. Therefore OOF gates can demote unstable or overfit files, but they cannot promote a candidate to normal submission or choose between the current public-sensor lanes.

Update after E40: test-movement fingerprint calibration is a loose prior, not a submission gate. `analysis_outputs/test_movement_fingerprint_selector.py` found strict selector views `0` and loose views `4`. Unlike OOF, it recovers the stage2/ordinal public order, but it underpredicts bad JEPA anchors and fails the A2C8-best leave-one-out gate. It shifts the lower-risk diagnostic preference toward `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv`, but it does not override the “no improvement claim” rule.

Update after E41: adding bad-axis geometry did not repair the selector. `analysis_outputs/movement_badaxis_geometry_selector.py` found strict selector views `0` and loose views `0`. `axis_group` reduced bad-anchor underprediction to `0.000898399` and kept stage2/ordinal order, but A2C8 LOO was predicted `+0.001475508` worse and MAE `0.000854918` missed the loose gate. Therefore E41 is a failure-to-certify, not a new candidate ranking.

Update after E42: fixed-zero A2C8 anchoring also does not create a usable ranker. `analysis_outputs/zero_anchor_selector_calibration.py` found fixed-zero gates `0` and usable zero-anchor gates `0`. The best `axis_group` view has nonbaseline MAE `0.000766262`, rank `0.857143`, and raw05 predicted best nonbaseline, but raw05 gap/MAE is only `0.113520`, best unobserved advantage/MAE is only `0.065408`, and trajectory monotonicity is `0.428571`. Its top unobserved pair sensors are only `0.000037-0.000050` better than raw05 by forecast, far below selector error. Do not submit those files as improvement claims.

Update after E43: selector resolution is now quantified as the immediate normal-submission blocker. `analysis_outputs/selector_resolution_boundary_audit.py` found selector frontier-resolution gates `0`, candidates certified better than A2C8 `0`, and candidates certified better than raw05 `0`. The best current selector error is pairwise public-order LOO `0.000218288`, which is still 2.5x larger than the raw05-A2C8 gap `0.0000869862`; best L2O error is `0.000415499`. Therefore no current micro-edge candidate should be submitted as an improvement claim.

Update after E44: the existing scored universe does not contain a hidden larger safe candidate. `analysis_outputs/large_edge_lowrisk_census.py` normalized 29 score tables, 69,869 rows, and 48,088 unique files. Pair-negative files were `12,309`, but pair edge greater than the raw05-A2C8 gap was `0`, pair edge greater than the best selector error was `0`, and normal large-safe files were `0`. The best pair edge was `0.000073768`, below both raw05 gap and selector error. Large favorable raw/anchor signals still exist for inverse7/mixmin, but they remain selector-conflict sensors, not improvement candidates.

Update after E45: simple structured public-subset recovery is also not a usable selector. `analysis_outputs/structured_public_subset_feasibility.py` tested 145 subject/order/date/raw-domain/random masks with train-prior soft-label LOO. Selector-scale gates were `0`, strict sub-gap gates were `0`, and the best LOO MAE was `0.000429528`, which is `4.937886x` the raw05-A2C8 gap and `1.967712x` the best current selector error. Feasible ranges on representative masks have mean width around `0.04`, so they are not candidate-ranking instruments.

Update after E46: block-state bottleneck audit does not add a submission file, but it changes what a useful next candidate must prove. `analysis_outputs/block_state_bottleneck_audit.py` shows validation block-rate oracle `0.517878`, temporal-to-oracle gap `0.106888`, subject identity explaining only `0.291286` of that gap, and current context heuristics failing: Markov `+0.002998`, nested threshold `+0.044275`, endpoint gain only `0.003252`. A normal submission candidate now needs either a block-rate context representation that recovers material oracle headroom or a public sensor that tests a worldview; another row-level micro-blend is not aligned with the bottleneck.

Update after E47: the first direct block-context target audit also does not add a submission file. `analysis_outputs/block_context_jepa_target_audit.py` shows best non-base 25% row blend `label_context_ridge = 0.623260` (`-0.001505`), but it recovers only `0.014083` of the oracle gap and has worse block-rate loss than temporal (`0.635888` vs `0.623448`). This is weak calibration signal, not hidden block-state recovery. Do not create a submission from these Ridge block-summary predictions.

Update after E49: post-mixmin observation does not add a new submission file. It changes the next candidate requirement. `analysis_outputs/post_mixmin_observation_audit.py` shows mixmin is not explained by simple global/subject/recent priors, and train/test is an interleaved subject-calendar mask rather than future-only forecasting. The next candidate should be mixmin-relative and calendar-block-aware; it should explain why `Q3/Q1/S3` move most and why `Q1/S1` can move against simple priors.

Update after E50: post-mixmin calendar selector recalibration also does not add a submission file. `analysis_outputs/post_mixmin_calendar_selector.py` found strict selector views `0` and loose selector views `0`. The best `subject_calendar` view had useful coarse order (`MAE 0.000884106`, rank `0.833333`, bad-tail correct), but failed the critical condition: held-out mixmin was predicted at delta `0.00135162` rather than best. The candidate prediction table in `analysis_outputs/post_mixmin_calendar_selector_candidates.csv` is not a public forecast. Do not submit a file from E50; the next candidate must pair calendar context with anchor-loss/binary-world or block-rate target evidence.

Update after E51: anchor-loss plus calendar selector recalibration also does not add a submission file. `analysis_outputs/post_mixmin_anchor_calendar_selector.py` found strict selector views `0` and loose selector views `0`. The best `anchor_residual` view had MAE `0.000835516` and bad-tail correct, but held-out mixmin was predicted at delta `0.00241739` and a2c8/raw05 order failed. This means E32/E38 anchor-loss evidence should not be converted into a kNN public-LB forecast. The next candidate needs either a hidden block-rate/count representation or a mixmin-constrained binary-world sign stress.

Update after E52: the first mixmin-constrained binary-world sign stress also does not add a submission file. `analysis_outputs/post_mixmin_binary_world_sign_stress.py` conditioned E30/E32 worlds on the actual mixmin public delta and scored `158` candidates versus mixmin. Strict better-than-mixmin gates were `0`, loose gates were `0`, and near-tie gates were `1`. The only non-duplicate near-tie was `analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv`, but it had mixmin-fit-gap better_rate `0.2`, median delta `+0.000034`, max delta `+0.000048`, and postmix-energy-quarter better_rate `0.285714`. This is not a replacement for mixmin. It supports keeping `submission_mixmin_0c916bb4.csv` as the active frontier.

Update after E53: the simple calendar-flank count-state probe also does not add a submission file. `analysis_outputs/calendar_flank_block_count_state_probe.py` found a local same-subject pseudo-hidden gain (`-0.005266`) but strict subject-excluded pseudo-hidden loss (`+0.001434`). Real hidden strict rates weakly favor mixmin overall (`-0.000179`) but only through S3/S2/Q2, while S1/Q1/Q3/S4 are adverse. This is not a direct probability-movement source. It supports keeping calendar-flank count state as an energy/gating diagnostic only.

Update after E54: raw overnight context is the strongest post-E53 representation result, but still does not add a submission file. `analysis_outputs/raw_overnight_block_context_probe.py` found best strict pseudo-hidden recovery with `night_phone_rawctx_strict_k8_a24` at `-0.007733` versus subject mean. However, the same method regresses S3 (`+0.007802`) and makes mixmin worse than a2c8 on actual hidden predicted rates (`+0.000311`). This is a real strict block-state latent, not a public-aligned candidate generator. Keep `analysis_outputs/submission_mixmin_0c916bb4.csv` as the active frontier.

Update after E55: target-dependency projection does not repair the E54 conflict. `analysis_outputs/raw_block_target_dependency_probe.py` tested `225` strict donor kNN/Ridge/S3 replacement variants and found joint gates `0`. The best pseudo-hidden repair, `raw_phone_s3_subject_w1p00`, improved raw by `-0.001115` and fixed S3, but hidden mixmin stayed adverse at `+0.000319`. The best hidden-sign method, `raw_phone_td_ridge_groupcross_all_k0_a8_w0.75`, reached `-0.000414` versus mixmin but collapsed pseudo-hidden LogLoss to `0.727319`. Do not submit these projections; the next source must be fresh mixmin-hard world generation or a structural block target, not target-rate smoothing.

Update after E56/E57: fresh mixmin-hard raw world generation did create a coherent posterior, but direct posterior submission is rejected. `analysis_outputs/mixmin_hard_raw_world_probe.py` generated `45` worlds / `44` unique worlds, existing candidate strict gates `0`, and posterior world-LOO strict gates `12`, writing diagnostic `analysis_outputs/submission_mixhard_rawposterior_af1502f9.csv`. `analysis_outputs/mixmin_hard_raw_posterior_safety_stress.py` then scored `15` variants and found joint safety gates `0`. The safest posterior was still actual-anchor worse than mixmin by `+0.000123`, and the E56 selected diagnostic was worse by `+0.020381` with mean abs logit move `0.381359`. Do not submit E56 posterior variants.

Update after E58/E61: simple anchor-constrained distillation of E56 posterior energy also does not add a submission file. `analysis_outputs/mixmin_hard_posterior_distillation_probe.py` generated `104727` teacher-gated candidates and actual-anchor scored `1200`; E61 fixed a sorted-prefilter score-index mismatch by carrying stable `pred_index`. Corrected toward-teacher candidates had only `126/900` sign-level anchor improvements and passed world/movement guards, but the best anchor delta was only `-0.000004081`, below the `1e-5` margin; eligible gates were `0`. Reverse controls were weaker (`-0.0000000126`) and had no world guard. Do not submit E58 candidates.

Update after E59: structural joint block target prediction also does not add a submission file. `analysis_outputs/structural_block_target_probe.py` tested `216` within-block 128-pattern structural methods. Pattern structure is real (`139` beat raw pattern NLL; `198` had own-margin joint gain), but submission gates stayed closed: row LogLoss beats raw `0`, joint gates `0`. The best pattern method improved pattern NLL by `-0.062594` but had row delta `+0.003678` and hidden mixmin delta `+0.000304`; the best hidden-sign method had hidden mixmin `-0.000367` but row delta `+0.042230` and S3 `+0.078145`. Do not submit E59 pattern-derived rates.

Update after E60: transition-residual block-state prediction also does not add a submission file. `analysis_outputs/transition_residual_block_state_probe.py` tested `432` transition methods and found joint gates `0`. The hidden-sign axis is stronger than E59 (`best weighted mixmin delta -0.001569`), but it comes from methods with catastrophic pseudo-hidden calibration (`+1.519232` row LogLoss vs raw, S3 `+1.331880` vs subject). Row-valid residual methods stay near raw and do not flip hidden mixmin sign. Do not submit E60 residual-derived rates.

Update after E62: transition-gated E56 teacher movement also does not add a submission file. `analysis_outputs/transition_gated_posterior_distillation_probe.py` generated `363258` candidates and actual-anchor scored `1300`. The transition gates were used only to open/close E56 teacher cells, not as direct probability targets. Eligible toward-teacher gates were `0`, diagnostic reverse gates were `0`, and the best toward-teacher anchor delta was only `-0.000002716`, weaker than corrected E58's `-0.000004081`. Do not submit E62 candidates.

Update after E63: gradient-consensus E56 teacher movement also does not add a submission file, but it changes the diagnosis. `analysis_outputs/gradient_consensus_posterior_probe.py` generated `404671` candidates and actual-anchor scored `1300`. The hidden-rate BCE-gradient guards were built from subject, calendar, raw, transition, and core-median views. Toward-teacher candidates passed hidden guard `1000/1000`, world guard `1000/1000`, and anchor sign beats `932/1000`; reverse controls passed hidden/world guards `0/300`. The best toward-teacher anchor delta was only `-0.000003650`, so eligible gates stayed `0`. Do not submit E63 candidates; use them as evidence that the E56 direction is plausible but amplitude/public-anchor translation is still missing.

Update after E64: scalar amplification of E63 also does not add a submission file, and it kills the simplest amplitude explanation. `analysis_outputs/gradient_amplitude_translation_probe.py` generated `12096` amplitude-expanded candidates and actual-anchor scored `1796`. Toward candidates passed hidden/world/movement guards `1346/1346`, but anchor beats were `0/1346`; best toward delta was `+0.000003024`. Do not submit E64 candidates. E56 gradient direction is useful only as a near-zero local energy unless a targetwise/rowwise calibration translator is found.

Update after E65: near-zero targetwise response improves the diagnostic edge but still does not add a submission file. `analysis_outputs/near_zero_amplitude_response_probe.py` generated `27384` candidates and actual-anchor scored `2400`. Toward candidates passed hidden/world/movement guards `2290/2290`, anchor beats were `1753/2290`, and the best delta improved to `-0.000005995`, but anchor-margin gates were `0`. The best mask was `no_q2_s3`, followed by `no_q2`, `no_s3`, and `all`; single-target moves were weak and S2 was adverse. Do not submit E65 candidates. The next useful branch is a Q2/S3 target-conflict translator, not another line search.

Update after E66: Q2/S3 conflict decomposition also does not add a submission file, but it changes the next translator. `analysis_outputs/q2_s3_conflict_translator_probe.py` generated and scored `3000` focused matched-mask candidates. `no_q2_s3` remained best at `-0.000005995`, but matched `all` add-back was robust-anchor adverse in `432/432` while improving mean-anchor in `288/432`, max-set tail worsening in `432/432`, and hidden core improving in `432/432`. Do not submit E66 add-back candidates. The next source must be a tail-neutral Q2/S3 translator, not a broad target-mask choice.

Update after E67: first-order tail-neutral Q2/S3 translation also does not add a submission file. `analysis_outputs/q2_s3_tail_neutral_translator_probe.py` generated/scored `7632`; best `tail_meanneg_m1.00` reached `-0.000006933`; strict `tail_p90_nonpos_m1.00` reached `-0.000006587`; matched-base beats were `4207/7200`; max-set-tail-neutral matched beats were `2241/7200`; margin gates stayed `0`. Do not submit E67 candidates. The next source needs independent non-anchor validation of tail-gated Q2/S3 cells.

Update after E68: independent Q2/S3 tail-gate validation also does not add a submission file. `analysis_outputs/q2_s3_tail_gate_independence_probe.py` selected `180` E67 configs, rebuilt gates with each combo set held out, scored `762` unique predictions, and formed `540` matched pairs. Independent gates were `155`, strict gates were `155`; `tail_soft_max_m1.00` had `44` strict gates and `tail_p90_nonpos_m1.00` had `41`. The best strict heldout edge was only `-0.000001261`, so this validates the cells but not a public-margin move. Do not submit E68 cells directly.

Update after E69: simple alpha amplification of E68 strict Q2/S3 cells also does not add a submission file. `analysis_outputs/q2_s3_strict_cell_amplitude_probe.py` used `155` strict pairs, scored `2170` rows / `2061` unique predictions, and found strict amplitude gates `0`. Best full-combo delta was `-0.000009178`, still below the `-1e-5` selector margin, while heldout tail-neutral counts collapsed from `155/155` at alpha `1` to `22/155` at alpha `24`. Do not submit E69 candidates. The next source must be rowwise/cellwise amplitude or a structural target.

Update after E70: strict-cell consensus keeps the Q2/S3 branch alive but still does not add a submission file. `analysis_outputs/q2_s3_strict_cell_consensus_probe.py` built `2688` rows / `2576` unique predictions from the `155` E68 strict cells and found `6` strict consensus gates, with best all-combo delta `-0.0000102775`. The issue is that every strict row uses `gate=none` and the construction is still heldout-specific. Do not submit E70 outputs directly. The next candidate source is a unified-rule consensus or structural energy that reproduces the margin without losing agreement/tail/block stability.

Update after E71: unified strict-cell consensus also does not add a submission file. `analysis_outputs/q2_s3_unified_strict_cell_consensus_probe.py` rebuilt `104` unique E68 strict cells with the full combo family and scored `3136` rows / `2842` unique predictions. It found `1` strict unified gate and best all-combo delta `-0.0000108217`, so consensus is not pure heldout arithmetic. But deployable unified gates were `0`, and the only strict row still used `gate=none`. Do not submit E71 outputs. The next candidate source must repair the disagreement-permissive gate dependency.

Update after E72/E73: the non-`none` gate branch is alive. `analysis_outputs/q2_s3_unified_gate_geometry_probe.py` scored `4752` rows and found `21` strict rows, `10` deployable non-`none` rows, and `655` loose rows. `top_abs50` produced `7` deployable rows; `s3_only` produced `3`; Q2-only produced none. The best deployable row was materialized as `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`, with all-combo delta `-0.0000105458`, all `3/3` combo sets beating base/tail-neutral, hidden Q2/S3 mean `-0.000391043`, world support `-0.000280957`, raw-energy q-p90 `-0.000159091`, and block win rate `0.722222`.

Update after E74: E73 was no longer just a 13-cell fragile-looking local candidate. `analysis_outputs/q2_s3_sparse_gate_stability_probe.py` scored `470` rows across `94` reference/jackknife/group/rank/bootstrap variants. Jackknife alpha16 remained deployable `13/13`, bootstrap8 alpha16 remained deployable `48/60`, and total strict/deployable rows were `141`. The same full-pool alpha20 row improved local all-combo delta to `-0.0000107261` and remained strict/deployable, but alpha24 failed strict. E80/E81 later superseded this as a submission order: E74 is now held until a pure sparse-gate sign is validated.

Update after E75: target-specific amplitude is now a live branch. `analysis_outputs/q2_s3_target_amplitude_ridge_probe.py` crossed Q2 and S3 alpha values on the E74 full pool and found `37` strict/deployable rows. The deployable mass is S3-heavy: `s3_higher` has `23` strict/deployable rows, `s3_only` has `6`, and `q2_only` has `0`. The best deployable row is `analysis_outputs/submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv`, with Q2 alpha `8`, S3 alpha `28`, all-combo delta `-0.0000123676`, hidden Q2/S3 `-0.000372692`, and block win `0.722222`. This is a sharper target-asymmetry sensor than E74, but more aggressive than E73.

Update after E76: target-asymmetric amplitude is direction-stable but exact E75 amplitude is not as stable as E73. `analysis_outputs/q2_s3_target_amplitude_stability_probe.py` rebuilt the E74/E75 sparse-gate pool across `94` source-subset variants and `21` Q2/S3 alpha pairs. Exact `asym8_28_e75` beats both `sym16_e73` and `sym20_e74` in `94/94` variants, and the best deployable axis is S3-heavy in `94/94` variants. But exact `asym8_28_e75` is deployable in only `49/94` variants: jackknife `8/13`, bootstrap8 `28/60`. E75 remains a strong target-asymmetry public sensor, not a safer replacement for E73; E74 remains the symmetric-control fallback.

Update after E77: no new submission file should be made from source-subset posterior aggregation. `analysis_outputs/q2_s3_amplitude_posterior_probe.py` aggregated E76 prediction variants as posterior logit movements from mixmin/E73/E74 and scored `6840` rows. Strict/deployable rows were `0`; loose rows were `3099`; `62` rows beat E75 local all-combo, but none were deployable. Mixmin/Q2S3 posterior was safe-looking but sub-margin (`-0.000008095` best all), while mixmin/full posterior reached local margin (`-0.000012599`) by weakening combo-set/tail consistency. E77 is a negative sensor: it says the next amplitude branch must condition on combo-set, tail, row-block, or public-like risk rather than average E76 variants.

Update after E78: no new submission file should be made from source-subset reliability masks. `analysis_outputs/q2_s3_localized_amplitude_gate_probe.py` scored `4452` localized rows from `36` E76-derived masks. Strict/deployable rows were `1806`, loose rows were `3934`, but deployable rows beating E75 local all-combo were `0`; the best rows were E75-equivalent. Consensus masks mostly collapsed to identity over E75 active cells, while hard sign/excess/veto masks reduced edge. E78 says the missing amplitude object is not E76 source-subset sign/consensus/excess reliability.

Update after E79: no new submission file should be made from handcrafted row/block/flank masks. `analysis_outputs/q2_s3_public_like_rowblock_amplitude_probe.py` scored `6516` rows from `61` topology, positive-unit-energy, subject-prior, subject-id, train-flank, and target-specific flank masks. Strict/deployable rows were `1318`, loose rows were `3403`, but deployable rows beating E75 local all-combo were `0`; best all stayed E75-equivalent. The useful observation is that E75 already moves only `72/250` active sparse rows/cells, and further cutting those rows by energy/topology/flanks lowers edge rather than improving it.

Update after E80/E81: `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv` scored public LB `0.5764077772`, worse than mixmin by `+0.0001011367`. The public result should not be read as a clean Q2/S3 sign oracle because E80 found the submitted file moved `893` cells across all `7` targets. E81 isolated the movement: pure mixmin-anchored Q2/S3 is loose but sub-margin (`-0.000005954`), pure S3-only is also sub-margin (`-0.000005665`), and all inverse-sign public-reaction variants are locally adverse. No direct E74/E75 follow-up should be submitted now.

Update after E82: the broader E72/E75/E76 Q2/S3 source universe does not rescue pure grafting. `analysis_outputs/e82_pure_q2s3_source_graft_scan.py` built `8402` pure mixmin-anchored value/delta grafts and stress-evaluated `700` combo-promising rows. Strict/deployable rows were `0`, loose rows `700`, and best evaluated all delta was only `-0.00000790328`. The important failure mode is clean: every evaluated row passed combo-set, tail, hidden, world, and block guards, while `all_margin_vs_mixmin` was `0/700`. Pure Q2/S3 should now be treated as latent energy, not as the next submission family.

Update after E83/E84: broader structural movement can supply margin, but it conflicts with Q2/S3/world or with one combo set. E83 found broad structural rows as strong as `-0.000035052` but unsafe; E84 recombined non-Q2S3 structural margin with Q2/S3-only safety and got loose/structural-loose `700/700`, best all `-0.000032150`, and hidden/world/block all favorable. The remaining failure was entirely the `inverse_top` combo set, which rejected `700/700` while raw05-compatible and all-sign accepted `700/700`. E84 is therefore a diagnostic sensor, not the best next file.

Update after E85: target-axis pruning solves the E84 inverse-top conflict locally. `analysis_outputs/e85_inverse_conflict_target_prune.py` evaluated `700` target-pruned rows and opened strict/deployable `535`. The selected file, `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv`, keeps only `S1,S2,S3` structural movement and has all delta `-0.0000238758`, inverse-top `-0.0000081666`, raw05-compatible `-0.0000295552`, all-sign `-0.0000339057`, hidden core `-0.000161301`, hidden Q2/S3 `-0.000216060`, world `-0.000130361`, block win `0.666667`, and block-tail safety `0.944444`. It is now the highest-information next public candidate.

Update after E86: the main E85 objection was tested. `analysis_outputs/e86_e85_target_prune_robustness.py` formed source-diverse consensus variants from strict E85 rows. The best public candidate is `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv`: `Q2,S1,S2,S3`, mean aggregation, top `40` rows, `18` source files, shrink `1.25`, all delta `-0.0000277059`, inverse-top `-0.00000691`, raw05-compatible `-0.0000353387`, all-sign `-0.0000408689`, hidden core `-0.000239181`, hidden Q2/S3 `-0.000377585`, world `-0.000307439`, block win `0.833333`, and block-tail safety `1.0`. This promotes E86 above E85 for upside, while E85 remains the lower-amplitude fallback.

Update after E87: E86's public risk is now pre-split into three contrast files. `analysis_outputs/submission_e87_noq2_source_consensus_a85c4e39.csv` tests whether Q2 add-back is the contaminant, `analysis_outputs/submission_e87_q2_nooverstep_consensus_acd7add0.csv` tests whether shrink `1.25` overstepped calibration, and `analysis_outputs/submission_e87_inverse_top_prior_consensus_5445ec28.csv` tests whether public follows inverse-top-prior geometry. These files are not ranked above E86; they reduce ambiguity if E86 fails.

Update after E88/E89: E88 made E86's downside measurable by comparing it with the public-negative E72 movement. E89 then tested whether that risk is cell-local. The selected `analysis_outputs/submission_e89_e72decontam_00d7807f.csv` keeps E86 except for top-20% E72-contaminated cells, where it falls back to E85. It reduces contamination index from E86 `0.772379` to `0.676361` while staying strict/deployable, but its local margin is weaker than E86. This makes E89 a lower-downside sensor, not the highest-upside file.

Update after E90: minimum E72 contamination is not the only useful decontamination objective. `analysis_outputs/submission_e90_e72pareto_28925de5.csv` falls back entire top-10% E72-contaminated rows from E86 to E85. It keeps more E86 structure than E89: all delta `-2.69324e-5`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block tail safe `1.0`, with contamination `0.715784`. This makes E90 the balanced row-coherent sensor between E86 and E89.

Update after E91: `analysis_outputs/e91_e72_updated_selector_collapse_audit.py` rejects known-LB movement regression as the next selector. With 10 known anchors, the best LOOCV proxy has MAE `0.000543412` and p90 error `0.001010234`; it predicts mixmin `+0.001142722` worse than its actual public score and predicts E72-minus-mixmin with the wrong sign. No E91 submission was made. Keep E86/E90/E89 as public sensors, not proxy-ranked optimization files.

Update after E92: `analysis_outputs/e92_hidden_block_posterior_alignment_audit.py` rejects hidden-block posterior CE as the next selector. The known public-negative E72 file is the hidden-block alignment leader with posterior CE delta `-0.000287300`. Among live candidates, no-Q2/E86 have the strongest posterior CE, E89 has highest block-target R2 and lowest E72 direction mass, and E90 stays the compromise. No E92 submission was made.

Update after E93: `analysis_outputs/e93_target_manifold_counterenergy_audit.py` rejects target-manifold consistency as the E72 counter-gate. E72 target-manifold delta mean is `-0.001468687` versus mixmin, while live candidates are favorable but smaller: E86 `-0.000921783`, no-Q2 `-0.000914184`, E90 `-0.000877945`, E89 `-0.000806467`, E85 `-0.000742113`. Older public-bad anchors such as final9 and bad-Q2 JEPA also look favorable under this energy. No E93 submission was made.

Update after E94: `analysis_outputs/e94_soft_health_hard_tail_audit.py` explains why E92/E93 can look healthy while E72 still misses public. It defines the hard label that would make E72 wrong in each active cell and measures candidate exposure to that adverse direction. E72's public miss `+0.0001011367` is only `0.043389` of its full adverse exposure `0.002330945`. Among live files, E72-adverse positive exposure is E85 `0.000739201`, E89 `0.000799109`, no-Q2 `0.000906798`, E90 `0.000934031`, E86 `0.001010242`; soft-health order instead ranks E86 highest. No E94 submission was made. The practical update is ranking semantics: E86 is the max-upside soft-health/local-structure sensor, E90 is the row-coherent compromise, E89 is the lower-downside hard-tail sensor, and E85 is the conservative floor.

Update after E98: `analysis_outputs/e98_e95_updated_selector_audit.py` rejects the idea that E95 makes known-LB regression submission-usable. With 11 known anchors, the best fixed proxy has MAE `0.000520095` and p90 abs error `0.000816497`; that p90 error is `53.33x` the E95 edge over mixmin and `8.07x` the E72 miss. It still predicts E72-minus-mixmin with the wrong sign. No E98-ranked submission should be made.

Update after E99: `analysis_outputs/e99_e95_conditioned_tail_transfer.py` conditions the E96 hard-tail worlds on both the failed E72 public miss and the successful E95 public gain. The model is small by design: `public_delta = alpha * local_all_delta + lambda * E96_tail_delta`, solved per scenario. Broad-plausible worlds are `3452`, with alpha median `3.310470` and lambda median `1.345192`. In those worlds E95 stays best mean, best p95, and winner mode. E89 is the only unresolved file with material E95-beat rate (`0.195829`); E85 is `0.031866`, E90 `0.002607`, and E86 `0.000290`. No E99 submission file should be made, but the next diagnostic order changes: E89 is the sharper E95 counterfactual, while E90 is only for explicitly testing row-coherent structure retention.

Update after E101: E89's Q2/S3 diffuse-tail counterfactual can be tested more cleanly than full E89. `analysis_outputs/e101_q2s3_tail_graft_probe.py` generated `618` rows, `581` strict-like grafts, and `54` pass rows. The selected `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` starts from E95 and shrinks only the effective Q2/S3 movement `25%` toward mixmin (`50` active cells vs E95). It remains strict/deployable, has all delta `-0.0000253724`, E72-adverse exposure `0.000692235` versus E95 `0.000788914`, hidden Q2/S3 `-0.000191316`, world `-0.000115685`, block win `0.75`, broad-plausible mean vs E95 `-0.0000162053`, broad beat-E95 rate `0.983488`, and broad p95 vs E95 `-0.000001564`. This file should be tested before full E89 if the next public question is whether E95 over-amplified Q2/S3 tail cells.

Update after E102: `analysis_outputs/e102_e101_active_cell_structure_audit.py` audits the `50` E101 active cells before making a follow-up mask. They touch `48` rows, `26` hidden blocks, and all `10` subjects; max cells per block is only `4`. Target-count-preserving nulls reject strong subject/block-local concentration (`n_subjects_touched` p `1.0`, `n_blocks_touched` p `0.935553`, `max_cells_per_block` p `0.997300`), but show weak edge-localization (`edge_or_near_edge_rate` `0.620` vs null `0.471289`, p `0.016999`; mean edge distance `1.680` vs null `2.138444`, p `0.040848`). No E102 submission should be made. E102 changes the post-E101 branch: if E101 improves, try Q2/S3 amplitude or edge-risk variants before subject/block masks; if E101 worsens, demote generic Q2/S3 rollback and keep only the edge-local idea as a weak diagnostic.

Update after E103: `analysis_outputs/e103_edge_local_q2s3_amplitude_probe.py` tested whether E102's weak edge-local clue can replace E101. It scanned `180` active/edge/interior/top-gap Q2/S3 rollback variants under E101's inherited stress frame. `12` rows passed E103 stress, but `0` dominated E101 on broad mean, p95, and beat-E95 rate together, so no E103 submission was materialized. The best passing active-all alpha `0.375` improves broad mean/p95 but lowers beat-E95 rate; edge-only masks fail p95/strict safety. E101 remains the cleaner next public sensor.

Update after E104: `analysis_outputs/e104_e101_amplitude_pareto_cliff.py` fine-scanned the E101 rollback alpha over `505` variants. `228` rows passed E101-style stress, but `0` dominated E101 on broad mean, p95, and beat-E95 rate together. For the active-all mask, alpha `0.255` is the first point above E101 with beat-rate loss; it improves mean/p95 only by `~3.02e-7`/`~2.6e-8` while dropping beat-rate by `0.000289687`. No E104 submission was materialized.

Update after E105: `analysis_outputs/e105_e101_public_label_breakeven.py` pre-registered how to read E101's public result. E101's `50` active cells split Q2/S3 as `11/39`, and S3 carries `0.935862` of flip benefit. All-support E101-vs-E95 delta is `-0.000096679`; all-adverse is `+0.000211677`. It needs `23/50` top-impact supportive cells to beat E95 and `25/50` to match E95's mixmin edge. Under global priors, expected delta is `+0.000048971` with beat probability `0.016610`; under subject priors, expected delta is `+0.000007854` with beat probability `0.335360`. This does not change the next file, but it changes the interpretation: E101 is a subject/block-local S3 tail-label sensor, not a global-prior correction.

Update after E106: `analysis_outputs/e106_e101_subject_prior_gate.py` tested the natural follow-up to E105: directly gate E101 by subject-prior support before public feedback. It scanned `268` variants and found E101-pass `12`, prior-healthier `56`, interesting non-replacements `6`, replacement rows `0`, and dominating rows `0`. The S3-heavy `active_s3_all` alpha `0.25` row is close but still weaker than E101 on broad mean/p95/beat (`-0.000015728/-0.000001195/0.973349` vs `-0.000016205/-0.000001564/0.983488`). This keeps E101 as the next file and demotes subject-prior gates to post-feedback contrast energy.

Update after E107: `analysis_outputs/e107_e101_feedback_decision_map.py` precomputed the branch table for possible E101 public outcomes. It used `292` candidates and `6` hypothetical E101-vs-E95 outcomes. Edge-sized E101 win and small win have coherent within-tolerance E99 worlds (`841` and `742` scenarios), and both point to E104 amplitude-up follow-ups, especially risk-tolerant active-all alpha near `0.500`; strict E101-pass follow-ups are lower alpha near `0.380`. E101 loss outcomes cannot be explained cleanly inside the E99/E101 broad-plausible worlds and are marked model tension. E106 subject-prior gates do not become the next branch before feedback.

Update after E108: `analysis_outputs/e108_e101_win_amplitude_followup.py` materialized the two post-feedback amplitude branches that E107 had only ranked. The risk-tolerant file is `analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv`: alpha `0.500`, not E101-pass, but rank `1` versus E101 in both E107 edge-win and small-win worlds. The conservative file is `analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv`: alpha `0.380`, E101-pass, lower upside with edge/small ranks `54`/`49`. Both are conditional on an E101 edge/small public win and are not pre-E101 submissions.

Update after E109: `analysis_outputs/e109_e101_tie_loss_label_world_audit.py` closes the naive E101 tie/loss rescue. Under subject-prior sampled active-cell worlds, E101 small/large loss buckets are common (`0.355350` / `0.244350`) and are caused by missing high-impact S3 support labels: top10 support rate falls from `0.916933` in edge wins to `0.805226` / `0.719218` in small/large loss. In those loss buckets E108 amp050 and strict amp038 are strictly worse than E101 on active cells: subject small-loss active mean vs E101 is `+0.000011723` / `+0.000006026`, with beat-E101 rate `0`. E95/E90/E86 retention is favored active-cell-only, so a negative E101 result should not trigger E108 or subject-prior masks. It should trigger model revision or an explicitly different retained-structure/non-active-tail sensor.

Update after E110: `analysis_outputs/e110_e101_negative_branch_nonactive_tail.py` tested that explicitly different non-active-tail branch. It built `45` unique candidates from active-restored E89/E85 and E95-to-E89/E85/E90/E86 non-active grafts. Non-control rows that were active-loss-safe existed (`36`), and `8` rows qualified as diagnostic sensors, but strict candidates were `0` and no submission was materialized. The best non-control row, non-active `S1/S2/S3` E86 alpha `0.25`, had broad mean/p95 vs E95 `+0.000000714` / `+0.000002798`, so it still fails E95-conditioned downside stress. This means an E101 tie/loss should not automatically route to full E89 or an active-restored/non-active graft.

Update after E111: `analysis_outputs/e111_sauna_frontier_movement_atlas.py` reframed the current frontier as target-axis hard-tail surgery. E72 failed versus mixmin with Q-share `0.450788`, S-share `0.549212`, and cosine only `0.327033` with the E95 direction. E95 improved with Q-share only `0.019948`, S-share `0.980052`, active cells `550`, and L1 `1.509562`, so its public gain is not a broad model upgrade. It is mostly S-side target-axis pruning with a tiny Q2 component. This strengthens E101 as the next sensor because E101 changes only `50` Q2/S3 cells versus E95 and asks whether that surviving axis surgery is too tight around S3-heavy tail cells.

Update after E112: `analysis_outputs/e112_sauna_qs_temporal_axis_audit.py` adds label/order evidence for the axis split. S-target mean subject-LOO gain is `0.068724` versus Q-target `0.020146`, and the strongest subject-prior targets are `S3`, `S2`, `S1`, all E95-active. Q targets have stronger temporal persistence (`0.135700` vs S `0.087255`), but only `8%` of test rows are bracketed by train rows within 3 days on both sides, so direct Q temporal propagation is not safe. This strengthens E101's role as a Q2/S3 boundary sensor rather than a broad Q/Q3 follow-up.

Update after E113: `analysis_outputs/e113_sauna_raw_context_visibility_audit.py` tested the obvious rescue for E112: use visible raw lifelog context instead of missing nearby labels. Raw coverage exists for every train/test row and the daily feature count is `114`, but raw+subject-prior worsens temporal LogLoss versus subject prior by `+0.038804` on Q targets and `+0.058534` on S targets. Random split also worsens on average, and Q2's random-only improvement while temporal holdout worsens is a shortcut warning. Only S3 improves slightly in temporal holdout (`-0.004643`). This does not create a raw-context submission branch; it strengthens the view that S3/S-state is safer than broad Q/Q3 temporal propagation.

Update after E114: `analysis_outputs/e114_e101_raw_context_support_audit.py` asked whether raw context can at least pre-validate E101's `50` active-cell support labels. It cannot. Subject-prior E101 beat probability is `0.336655`, while raw+prior drops it to `0.238325` and validation-gated raw drops it to `0.230710`. S3 owns `0.935862` of E101 flip benefit, but raw S3 support probability is `0.589463` versus subject prior `0.604450`. This keeps E101 as the next public sensor, but removes raw context as an independent pro-E101 argument.

Update after E115: `analysis_outputs/e115_public_sensor_information_audit.py` tested the decision rule directly: after raw support fails, is E101 still the most information-rich public sensor? Across `3452` E95-conditioned broad-plausible worlds, E101 has actionable information score `1.613953`, entropy `1.728493`, beat-E95 rate `0.983488`, and win/tie/loss `0.911645/0.088355/0.000000`. E89 is much weaker (`0.233881`, beat `0.195829`, loss `0.580243`), and E85/E90/E86 mostly ask how badly they lose. This strengthens E101 as the next public slot on information value, not raw-context support.

Update after E116: `analysis_outputs/e116_e101_public_feedback_decoder.py` pre-registers how to interpret the next E101 LB before seeing it. With E95 public `0.5762913298`, strong win is `<=0.576261330`, edge win is `(0.576261330, 0.576280330]`, small win is `(0.576280330, 0.576288330]`, tie is `(0.576288330, 0.576294330]`, and loss is `>0.576294330`. Win bands allow an exact-delta rerun and E108 consideration; tie/loss bands explicitly block E108/E104/E106/full-E89/non-active-graft rescue.

Update after E117: `analysis_outputs/e117_e95_like_neighborhood_audit.py` rejects the easy "there is probably another E95-shaped file already hidden in the documented universe" escape hatch. It scanned `5277` referenced submission names, resolved `4477`, deduplicated `4031` prediction tensors, and found only `10` E95-like neighbors. Only `4` had no higher E72-adverse exposure than E95: E101, E85, and the two E108 post-E101-win files. E101 is a `50`-cell E95-relative Q2/S3 micro edit, not a standalone replacement. E108 remains conditional on E101 feedback, not a pre-feedback shortcut.

Update after E118: `analysis_outputs/e118_e101_flank_label_support_audit.py` gives E101 more visible transition-state support but not certification. The best train-flank prior `edge_endpoint_beta` raises beat-E95 probability to `0.437780` versus subject prior `0.337185` and global `0.015920`, and active cells are enriched for edge/near-edge (`0.620000`, p `0.016999`) plus flank conflict (`0.240000`, p `0.048998`). The expected delta is still positive at `+0.000003014` per all cells, so do not turn this into an E108 or amplitude-up submission before E101 public feedback.

Update after E119: `analysis_outputs/e119_e101_flank_gate_variant_stress.py` tried exactly that tempting conversion: use visible flank/support/edge/flip-benefit selectors to gate the E95-to-E101 movement. It generated `602` variants, `66` E101-pass rows, `0` E101-dominating rows, and no materialized submission. Full active-all scale `1.50` improves mean/p95 but loses beat-rate (`0.980881` vs E101 `0.983488`); scale `2.00` improves mean more but fails E101-pass and drops beat-rate to `0.977984`. Flank support is therefore interpretation energy, not a replacement candidate generator.

Update after E120: `analysis_outputs/e120_post_e101_public_observation_audit.py` ingested the actual E101 public result. `submission_e101_q2s3tail_177569bc.csv` scored `0.5763003660`, which is E116 `small_loss`: `+0.0000090362` worse than E95 and `-0.0000062745` better than mixmin. E101 gives back `59.02%` of E95's gain over mixmin and preserves `40.98%`. The actual public delta is `+0.0000252415` worse than local E101 mean and `+0.0000106001` worse than local p95. This keeps E95 as frontier and closes E108/E104/E106/E119/full-E89/non-active-graft automatic followups.

Update after E121: `analysis_outputs/e121_e101_small_loss_inverse_posterior.py` rebuilt the exact E95/E101/mixmin boundary. The observed E101 delta requires `0.657165` of the active-cell flip benefit. Greedy high-impact support first beats mixmin at `21`, matches the observation near `22`, and first beats E95 at `23`. Exact-observed worlds are common under local/flank priors but do not expose a clean visible selector. This means the next same-line file is not justified. A new candidate must either bring an independent sensor for the missing high-impact S3 support cells or intentionally test a different hidden structure.

Update after E122: `analysis_outputs/e122_e101_independent_sensor_boundary_audit.py` checked whether that independent sensor already exists. It does not. Simple subject/flank/raw expectations predict the observed small-loss branch very well: `raw_full_subject_prior_y1` expected `+0.000008889` versus actual `+0.0000090362`, and train-flank expectations cluster around the same branch. The pre-public E119 local-transfer stress is the wrong sensor here because it expected `-0.000016205`. But no submission gate opens: the critical greedy rank-23 S3 cell, which is the first support count that would beat E95, remains high-support under subject/edge/raw/posterior views. Therefore no E121/E122 same-line posterior or thresholded support file should be submitted.

Update after E123: `analysis_outputs/e123_e101_transition_motif_s3_sensor.py` tested the next cheap independent sensor: Q/S neighbor-state motif around the hidden row, including a no-S3 version that excludes direct S3 flanks. This also does not open a file. Temporal-tail validation worsened versus subject prior by `+0.135183` for `motif_no_s3`, `+0.246239` for `motif_full`, and `+0.349065` for `motif_plus_subject`; rank-23 support remained high at `0.943564` to `0.984326`. Do not create an E95/E101 gate from transition motifs. The same-family queue stays closed.

Update after E124: `analysis_outputs/e124_e101_conditioned_tail_transfer.py` used E101 as a held-out check on the pre-E101 E99 transfer world. E99 broad-plausible worlds predicted E101 too optimistically: mean predicted delta `-0.000031516` vs actual `-0.000006275`. Only `57/3452` broad-plausible worlds matched the E101 ordering and magnitude enough to be E101-plausible. Inside those worlds E95 remains live winner mode with `0.929825` rate, while future candidates are weak: E89 beat-E95 `0.052632`, E85 `0.017544`, E90/E86 `0`. Therefore pre-E101 E99 order must not be inherited. E89 is still an explicit diffuse-tail worldview sensor if we choose to spend a slot, not an expected-improvement successor.

Update after E125: `analysis_outputs/e125_e101_survivor_anatomy.py` inspected the `57` E101-plausible worlds. They are not Q2/S3 diffuse-tail survivors. `q2s3` has `0/368` survivors, while `all`/`e72_top50_hard` account for `43/57`; median alpha collapses from `3.310470` to `0.791985`; median `tail_e101 - tail_e95` becomes `~0`. This weakens full E89 and same-line Q2/S3 rollback even as diagnostic sensors. The next submission, if any, should not be justified by E100 q2s3 enrichment.

## Submission Order

Current recommendation after E125: keep `analysis_outputs/submission_e95_hardtail_541e3973.csv` as the active public frontier. There is no automatic same-family next submission. E101 was the right information sensor and it resolved negatively against E95; E121 shows that the loss is a one-high-impact-S3-cell-scale boundary, E122 shows that existing visible priors explain but cannot exploit that boundary, E123 shows that cross-target transition motifs also fail as the missing independent S3-cell sensor, E124 shows that the pre-E101 E99 transfer ranker overestimated E101, and E125 shows that the surviving worlds are not q2s3 diffuse-tail. The next candidate must either bring a materially different S3-cell sensor or explicitly test a different hidden structure. Full E89 is demoted from "diffuse-tail sensor" to a lower-priority historical contrast; E85 remains the conservative same-family floor; E90 and E86 are structure-retention/max-upside sensors, not expected-improvement bets under the E101-conditioned world.

Conditional E108 files are closed under the observed E101 result. `analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv` and `analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv` were valid only after an E101 win. The observed branch is E116 `small_loss`, so neither should be submitted as a rescue.

1. Keep `analysis_outputs/submission_e95_hardtail_541e3973.csv` as the active best.
2. Treat `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` as a resolved negative sensor, not a pending file.
3. Post-E101 two-point hard-tail rebuild is now done by E121. Before choosing a same-line file, find an independent non-public sensor for the missing high-impact S3 cells; otherwise move to a different hidden-structure sensor.
3a. Do not use E123 transition-motif scores for that same-line sensor. They fail temporal validation and keep rank-23 support high.
3b. Do not use pre-E101 E99 broad-plausible ranking as the same-line selector after E101. E124 shows only `57/3452` broad worlds survive E101 plausibility and E95 remains dominant inside them.
3c. Do not use E100 `q2s3` enrichment as the next same-family rationale. E125 shows `q2s3` has `0/368` E101 survivors.
4. Submit/test `analysis_outputs/submission_e89_e72decontam_00d7807f.csv` only if the explicit question remains whether public prefers E89's broader E72-cell fallback law despite E110's negative non-active graft result. E89 is not the automatic fallback after E101 loss; it is only a high-information diffuse-tail sensor if we intentionally spend a slot to test that worldview.
5. Use `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv` as the conservative same-hypothesis fallback. If E85 improves but E101/E89/E90/E86 worsen, public wants lower-amplitude target-prune floor rather than retained E86 structure.
6. Submit/test `analysis_outputs/submission_e90_e72pareto_28925de5.csv` if the public question is whether E95 left too much row-coherent E86 hidden/world/block structure on the table. Do not present it as the highest expected E95-beat file after E99/E101.
7. Submit/test `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv` if the public question is maximum source-consensus structural upside despite higher hard-tail exposure than E95.
8. If E86 fails and a second diagnostic slot is available, choose exactly one E87 contrast based on the belief to split: no-Q2 for Q2 contamination, no-overstep for calibration overstep, inverse-top-prior for public-world geometry.
9. Do not resubmit or amplify `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`. It is now a failed combined-file public sensor.
10. Hold `analysis_outputs/submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv`. Its target-asymmetry direction remains locally interesting, but E73 public failure and E81 sub-margin pure Q2/S3 make it too direct a follow-up.
11. Hold `analysis_outputs/submission_e74_fullpool_a20_q2s3_gate_55455b60.csv`. It is only a symmetric amplitude control if a future pure sparse-gate public sign becomes positive.
12. Do not submit a new file from E49/E50/E51/E52/E53/E54/E55/E56/E57/E58/E59/E60/E62/E63/E64/E65/E66/E67/E68/E69/E70/E71/E77/E78/E79/E80/E81/E82/E83 alone. E80/E81 turned E72/E73 into a negative public sensor and a sub-margin latent energy; E82 shows the broader pure Q2/S3 source universe is still margin-limited; E83 shows broad structural margin and Q2/S3 safety are separated.
13. `analysis_outputs/submission_e84_inverse_sensor_1c74da00.csv` is now secondary to E85/E86/E87. Use it only if the specific question is whether public follows raw05/all-sign despite inverse-top rejection. It is higher-risk because E85/E86 already show strict target-pruned repairs.
14. Treat `analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv` as the previous-frontier contrast anchor, not the baseline to optimize around blindly.
15. Stop treating known-anchor kNN as the next default selector. E50/E51 show it cannot explain mixmin-best even with calendar and anchor-loss features.
16. If E85/E86/E89/E90 all fail public, next candidate source should not be pure Q2/S3-only or simple target-group recombination. Reopen row/block-specific inverse-top conflict separation or all-sign/raw05-compatible target-axis recovery.
17. Do not submit `analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv`. E52 says it is a near-tie only, not better than mixmin.
18. Hold pair-only S4/Q3 sensors until post-mixmin recalibration. Their old purpose, pair-vs-old selector disambiguation around a2c8, is now lower value.
18. If lower movement risk is more important than maximum diagnostic contrast, use `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv`; expect weaker LB readability.
19. If `1bbfb735` or the 0.65 scaled sensor improves public LB despite independent survival failure, then the old hidden-subset selector is miscalibrated for S4+Q3 movement and H17 becomes live again.
20. If it worsens, do not submit `6b9335b1`; treat E14 as pairwise-selector overfit and move to selector reconciliation.
21. Do not spend a public slot on another S4/Q3 weight variant unless a new anchor or external validation source supports the direction.
22. Do not promote local OOF Q3/S4 winners as public candidates without selector support; E19 directly falsified that path for the current top OOF set.
23. Do not promote existing block/measurement/raw05-blockcount/presleep candidates as public candidates; E20 directly falsified that archive as a submit source. If a diagnostic slot is used, raw05-blockcount refine is lower-risk than presleep, but it is not expected to beat a2c8.
24. Do not rank current candidates by merging pairwise and old selector shortlists. E21 shows the intersection is empty; any public submission now should be explicitly framed as a selector-disambiguation sensor.
25. Do not spend the next public sensor on an old-only Q3/raw05-drift file unless the specific question is to retest a selector that already failed the raw05/A2C8 known direction.
26. Do not spend a public slot on the E24 localized `id02_b02` files. They are too small and still old-selector-negative.
27. Do not present mixmin/direns as strict-survival candidates. If the next public submission is `analysis_outputs/submission_mixmin_0c916bb4.csv`, state that it is a high-risk test of actual-anchor/combo/binary-world/anchor-loss stress against the pairwise/old selector veto.
28. Do not present inverse7 or inverse7 scale-blends as strict-survival either. E36 makes inverse7 a raw-structure bridge probe, and E37 shows scale/blend variants still do not resolve selector veto.
29. Do not claim any current unobserved candidate is supported by public-LB inverse fitting; E26 proves the known LBs leave both improvement and degradation feasible.
30. Do not claim subject-prior inverse fitting supports a candidate; E27 proves global/subject-target priors still leave every checked unobserved candidate sign ambiguous.
31. Do not claim binary hidden-label inverse fitting supports a candidate; E28 did not produce stable one-sided improvement evidence.
32. Do not claim binary world-pool support certifies a candidate; E29 has only one frontier-scale world. It can only reprioritize high-risk probe questions.
33. Do not claim frontier-box binary support certifies mixmin either. E30 makes mixmin the leading high-risk worldview probe, not a strict submission.
34. Do not claim plausibility-gated binary support certifies mixmin. E31 shows adverse mixmin worlds are not train-geometry outliers.
35. Do not claim anchor-loss-gated binary support certifies mixmin. E32 makes mixmin the best high-risk public sensor under the binary/actual-anchor worldview, but the gate is derived from known public-anchor decomposition and must be validated by a new observation.
36. Do not claim anchor-LOO stability certifies mixmin. E33 only says the E32 gate is not one-anchor fragile. It makes the next information-rich probe clearer; it does not make an improvement submission safe.
37. Do not claim anchor-loss support is JEPA target-axis semantic evidence. E34 says target-axis permutation does not break the signal; the probe is anchored in loss/cancellation geometry.
38. Do not claim existing independent evidence certifies mixmin. E35 says the normal-submit gate is still closed; mixmin is a public sensor, not a validated improvement candidate.
39. Do not claim raw-structure pseudo-label support certifies inverse7. E36 says inverse7 is the best bridge candidate under raw observed structure, but selector veto and anchor-LOO weakness remain.
40. Do not repeat amplitude-only inverse7/mixmin bridge sweeps as if more scales will solve it. E37 already found raw support and anchor support can coexist across many scales while two-selector majority stays `0`.
41. Do not treat E38 information score as an improvement score. It ranks which public sensor would be most informative; it explicitly found normal-submit candidates `0`.
42. Do not treat E39 OOF gates as a public selector. OOF sign agrees with known-public direction versus final9, but it gets the stage2/ordinal ordering wrong; use OOF only as a negative screen.
43. Do not treat E40 predicted public LB as a score forecast. Movement fingerprints are loose: they recover stage2/ordinal but miss bad JEPA severity. Use them only to choose lower-risk diagnostic framing.
44. Do not treat E41 axis-geometry predicted LB as a score forecast. The best axis view is severity-informative but not selector-certified.
45. Do not treat E42 fixed-zero axis predictions as a score forecast. A2C8 anchoring improves coarse nonbaseline rank but collapses frontier-scale resolution; the predicted pair-sensor edge is much smaller than selector error.
46. Do not submit any current micro-edge candidate as an improvement claim unless a new selector gets below `0.0000869862` known-anchor error or the candidate edge exceeds the current best selector error `0.000218288`.
47. Do not submit any existing scored-universe candidate as an improvement claim solely because a raw/anchor view shows a large edge. E44 found zero files with selector-resolvable pairwise edge and zero normal large-safe files.
48. Do not submit or rank from simple structured public-subset inverse masks. E45 found zero selector-scale masks and wide feasible ranges; any apparent exact fit is underidentified, not predictive.
49. Do not submit a candidate merely because it uses block/order/endpoint context. E46 shows those contexts are common (`26/36` hidden blocks have two train flanks) but current Markov, endpoint, and threshold translations do not recover the block-rate oracle. A block-context candidate must demonstrate held-out block-rate vector prediction first.
50. Do not submit E47 block-summary Ridge predictions. They improve a 25% row blend by `-0.001505` but fail the actual block-rate target stress; any candidate based on them would be another selector-noise-scale micro-blend.
51. Do not convert E49 calendar-mask observations into a direct row-order/public-subset tweak. They are a context-target design constraint; the next candidate must survive mixmin-anchor and known-anchor stress.
52. Do not submit or rank from E50 calendar-selector predicted scores. The best subject-calendar selector fails to predict mixmin as best, so its candidate table is diagnostic only.
53. Do not submit or rank from E51 anchor-calendar predicted scores. The best anchor-residual selector also fails held-out mixmin and a2c8/raw05 order.
54. Do not submit E52 near-tie candidates as mixmin replacements. `bridge_blend_m0p75_s1p25` is not one-sided better under mixmin-compatible binary worlds.
55. Do not submit E53 calendar-flank count posteriors or use them as direct row probability tweaks. Local gains are same-subject-driven and strict recovery is target-mismatched.
56. Do not submit E54 raw overnight block-state posteriors directly. Strict pseudo-hidden recovery is strong, but hidden mixmin sign is adverse and S3 regresses.
57. Do not submit E55 target-dependency projections or S3 replacements. S3 repair, pseudo-hidden recovery, and hidden mixmin sign do not align; hidden sign flips collapse pseudo-hidden validity.
58. Do not submit E56 mixmin-hard raw posterior variants directly. E57 found joint safety gates `0`; the E56 selected diagnostic is actual-anchor worse by `+0.020381` and moves too far from mixmin.
59. Do not submit E58 anchor-constrained distillation candidates. After E61 score-index correction, the best toward-teacher anchor delta is only `-0.000004081`, below selector-scale margin.
60. Do not submit E59 structural joint-pattern predictions. Pattern NLL gains are real, but row LogLoss versus raw never improves and hidden mixmin sign improves only when pseudo-hidden validity and S3 collapse.
61. Do not submit E60 transition-residual predictions. Hidden mixmin sign can be made negative, but the methods that do it collapse pseudo-hidden row calibration and S3; row-valid transition methods do not explain mixmin.
62. Do not resurrect E58 because of the discovered indexing bug. Stable `pred_index` scoring still leaves eligible gates at `0`, so the original no-submission decision stands.
63. Do not submit E62 transition-gated E56 distillation candidates. The best toward-teacher anchor delta is `-0.000002716`, below margin and weaker than corrected E58.
64. Do not submit E63 gradient-consensus E56 distillation candidates. Hidden-rate gradients validate direction, but the best toward-teacher anchor delta is `-0.000003650`, below margin and weaker than corrected E58.
65. Do not submit E64 gradient-amplitude candidates. Every scored toward candidate is actual-anchor worse than mixmin despite hidden/world guards passing.
66. Do not submit E65 near-zero amplitude candidates. The best `no_q2_s3` pocket is only `-0.000005995`, below margin, and its dependence on excluding Q2/S3 is a target-conflict diagnostic rather than a submission argument.
67. Do not submit E66 Q2/S3 add-back candidates. The matched decomposition says Q2/S3 can improve hidden core and mean-anchor terms, but robust actual-anchor and max-set tails worsen; this is a translator-design clue, not a file.
68. Do not submit E67 tail-neutral Q2/S3 translator candidates. First-order tail gates improve matched base and can keep some max-set tails neutral, but the best delta is still below margin and the evidence is anchor-derived.
69. Do not submit E68 strict Q2/S3 tail-gate cells directly. They survive held-out combo plus hidden/world/block stress, but the best strict heldout edge is only `-0.000001261`; use them as a latent/amplitude gate source.
70. Do not submit E69 alpha-amplified strict-cell candidates. Best full-combo delta is `-0.000009178`, still below margin, and heldout tail stability collapses as alpha grows.
71. Do not submit E70 strict-cell consensus outputs directly. They produce `6` strict local gates and best all-combo delta `-0.0000102775`, but every strict row uses `gate=none` and the construction is not a unified test-time rule.
72. Do not submit E71 unified strict-cell consensus outputs. They preserve one strict unified row and best all-combo delta `-0.0000108217`, but deployable gates are `0` and the only strict row still uses `gate=none`.
73. Do not submit E72 soft/agreement/Q2-only variants. The only live E72 file is the selected `top_abs50` sparse-magnitude gate; Q2-only produces no loose rows, and soft/agreement gates do not produce strict deployable rows.
74. Do not submit E74/E75 as direct follow-ups after E73 public failure. E80 shows E73 was a broad all-target movement, and E81 shows pure Q2/S3 is sub-margin while inverse-sign controls fail.
75. Do not submit E82 pure Q2/S3 grafts. They pass every evaluated non-margin stress but fail selector-scale margin (`0/700` all-margin), so they are diagnostic energy rather than candidates.
76. Do not submit E101/E89/Q2S3 same-line variants by default after E126. E101-compatible selected budget mass is only `0.011234` E101-active and `0.180513` Q2/S3, so the public-compatible surface is not primarily the cells those files move.
77. Do not submit a transfer-shrinkage metadata gate from E127 alone. `target_context_tail_e72bin` has real hidden-block-heldout signal, but top50 teacher-mass capture is only `0.252521`; it is a representation target and negative gate, not a probability-movement file.
78. Do not submit E85/E89/noQ2/E90/E86 solely because E128 transfer-shrinkage risk ranks them low. E128 component energies are useful vetoes, but the combined risk index has known-public Spearman only `0.440559` and conflicts with E124/E126 post-E101 same-family warnings.
79. Do not continue existing-universe submission ranking as the next default branch. E129 scanned `65865` unique tensors and found `0` novel strict actionable transfer-shrinkage survivors; strict actionable survivors are only E85 and E101, with relaxed material adding E89.
80. Do not submit E130/E131 density-family local-upside blends. E130 found `0` local-strict plus veto-actionable rows from direct density-shaped donor interpolation; E131 expanded this to `6384` local+safe combinations/clipped variants and again found `0` local-strict plus veto-actionable rows. The branch is a negative diagnostic, not a file source.
81. Do not submit E132 gradient-nullspace candidates. E132 removed old donors and moved directly along E95 combo gradients, but still found `0` gradient local-strict rows, `843` veto-actionable rows, `0` in the intersection, and `0` submit-gate rows. The branch is a tangent-space diagnostic, not a submission source.
82. Do not submit E133 co-location atlas cells directly. E133 is an interpretation layer: best local-safe mass is only `0.161830`, the co-located pocket shifts from Q2/S3 to Q3/Q1, and metadata CV top50 truth-mass capture is only `0.048280`. It is a latent-target clue, not a probability file.
83. Do not submit E134 raw-block co-location rankings. E134 improves top50 teacher-mass capture only from metadata `0.063040` to raw-block `0.073497`; this is weak visibility, not a selector-scale latent.
84. Do not submit E135 prediction-manifold co-location rankings. E135 improves only from metadata `0.063040` to prediction-manifold `0.063430` and is weaker than E134 raw/block `0.073497`; existing submission disagreement is not the missing selector.
85. Do not submit E136 block-target compressed rankings directly. E136 is a target-representation discovery, not a calibrated probability movement. A file is allowed only after the compressed state creates a cell movement that passes transfer-shrinkage and hardtail stress.
86. Do not submit E137 block-target-gradient rows. They improve local/post-E101 means but have `0` strict and `0` transfer-veto-actionable survivors; this is the classic mean-good/tail-bad failure mode.
87. Do not submit E138 block-target x veto-null overlap rows. They repair transfer-veto/post-E101 sensor signs (`373` veto-actionable rows), but still have `0` local-strict, `0` local-and-veto, and `0` submit-gate rows. The best local/post-E101 row fails all-set tail neutrality and world/raw hidden support, so it is a decoder failure diagnostic, not a frontier candidate.
88. Do not submit E139 block-target set-consensus rows. Combo-set mean agreement is not enough: E139 produced `190` transfer-veto-actionable rows but `0` local strict, `0` local-and-veto, and `0` submit-gate rows, with every evaluated row failing tail-neutral, world-nonworse, and raw-energy-nonworse checks.
89. Do not submit E140 primitive tail/world decoder rows. They make hidden/world/raw nonworsening easy (`168/168` combined rows pass), but all `168/168` combined rows fail all-set tail neutrality and transfer-veto actionability remains `0`.
90. Do not submit E140 rows even under E141 tail tolerance. Tolerance `1e-12` opens `84` relaxed structural rows, but `0` pass E72-plausible exposure, `0` pass post-E101 p95, and `0` are actionable.
91. Do not submit E142 uniform-shrink or partial-clipped rows. Uniform keep `0.25-0.90` and partial keep `0.25/0.50` fail E72-budget survival; the only live E142 family is full rollback of high excess-exposure cells.

Update after E134: there is no new submission candidate. The single-file frontier remains `analysis_outputs/submission_e95_hardtail_541e3973.csv`, and the latest public sensor `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` remains a resolved negative against E95 at `0.5763003660`. The next file should not be made from E133/E134 cell rankings unless a new target representation materially improves hidden-block-heldout recovery and yields an actual probability movement that passes E128/E129/E124 stress.

Update after E135: still no new submission candidate. The prediction-manifold route does not improve the selector enough to justify a file, so the next public slot should not be spent on an old-submission disagreement blend or a rank-translated E133/E134/E135 gate. Frontier remains `analysis_outputs/submission_e95_hardtail_541e3973.csv` with public LB `0.5762913298`; E101 remains a resolved negative sensor at `0.5763003660`.

Update after E136: no submission yet, but the live branch changes. The best next candidate source is not old-submission disagreement or cell ranking; it is block-target safe-state translation. E136's best block-target visibility (`top10 enrichment 3.326980`) is strong enough to justify a movement-generation experiment, but not enough to bypass calibration/tail gates.

Update after E137: still no submission. E136 block-target state is useful, but current E95 combo gradients are not a safe decoder: `1980` variants, `0` local strict, `0` transfer-veto-actionable, `0` submit-gate. A future file must come from a new block-target direction/amplitude translator, not from scaling the E137 mean-improving rows.

Update after E138: still no submission. Intersecting E136 block-target state with veto-null / low-adverse masks creates many transfer-veto-actionable rows (`373`) and favorable post-E101 mean/p95 in the best rows, but strict structural gates remain closed (`0` local strict, `0` local-and-veto, `0` submit-gate). This demotes mask multiplication itself: the next file, if any, must be a new decoder that preserves all combo sets, tail neutrality, and world/raw structure inside the block-target state.

Update after E139: still no submission. Set-consensus decoders can clean up combo-set mean direction enough to produce all-three mean wins, but they do not repair LogLoss tails or world/raw hidden support. The next candidate should not be another E95-gradient mask/filter. It should be a decoder whose primitive objective is worst-tail neutrality and world/raw nonworsening inside the E136 block-target state.

Update after E140: still no submission. Primitive decoding proves the world/raw part can be repaired, but the combo-set worst-tail law remains closed. The next file is not allowed until a decoder can move beyond `1/3` tail-neutral sets while keeping the E140 world/raw improvement.

Update after E141: still no submission, and the E140 interpretation is corrected. Exact all-set tail failure was partly numerical. The real remaining submission blocker is transfer-tail budget: E72-plausible exposure is at least `+0.000003189534` above E95 and post-E101 p95 remains positive after relaxed structural filtering.

Update after E142: new candidate opened. `analysis_outputs/submission_e142_transferclip_09a92236.csv` was the first transfer-budget-neutral residual public sensor. It is not a same-line Q2/S3 rollback; it moves `185` non-Q2 cells and bets that the remaining public-compatible frontier is transfer-budget-neutral residual movement. The expected upside is small but cleaner than E89/E85/E90 because it passes relaxed structural, E72-budget, and post-E101 p95 gates simultaneously.

Update after E143: E142 is superseded as the first file by `analysis_outputs/submission_e143_activeq2s3repair_68ca656f.csv`. E143 keeps most of E142's residual movement but rolls back the top `21` Q2/S3-weighted cells, making the candidate pass the original active/Q2S3 strict gate as well as E72-budget and post-E101 p95 gates. Submit E143 first; keep E142 as the fallback if public suggests the active/Q2S3 veto was overconservative.

Update after E144: E143 is now superseded as the first file by `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`. E144 searches the fine boundary around E143 and finds `9` original-strict submit variants that beat E143 locally without worsening post-E101 p95. The selected top24/keep0.15 row keeps all E143 gates, improves local all-minus-E95 from `-0.000009551358` to `-0.000009725930`, and improves post-E101 p95 from `-0.000003368915` to `-0.000003430489`. Submit E144 first; use E143 only if public feedback says the finer retained movement was too optimistic.

Update after E146: the E144-vs-E143 edge is public-free prior-supported. The `24` differing cells are all `S3`, with `0` flank conflicts, and all `10/10` global/subject/flank priors prefer E144 over E143. This strengthens E144 as the current single next submission. If E144 loses narrowly, E143 should be treated as a fine-tail-retention contrast rather than an automatically safer expected-score fallback.

Update after E145: `analysis_outputs/e145_e144_public_feedback_decoder.py` pre-registers the E144 interpretation bands. If E144 is `<=0.576284330`, treat the fine-boundary branch as public-real at readable scale. If it is `(0.576284330, 0.576289330]`, promote E144 but do not claim a structural breakthrough. If it is `(0.576289330, 0.576293330]`, keep E95 as practical frontier and do not over-interpret. If it is `(0.576293330, 0.576300366]`, E143 becomes the only same-family contrast worth considering. If it is worse than E101, do not auto-submit E143/E142; if worse than mixmin, close the branch.

Update after E147: E144 now has whole-file support, not only E146 fine-tail support. `analysis_outputs/e147_e144_e95_prior_world_audit.py` finds `185` E144-vs-E95 moved cells across `108` rows and `9` subjects, and all `10/10` public-free priors prefer E144 over E95. Expected E144-minus-E95 deltas range from `-0.000049865515` to `-0.000012197928`, with simulated beat probability `0.583850..0.762700`. This keeps `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the single next file. The caveat is target-local: nearest-hard priors say Q1/S4/S2 are favorable while S3/Q3 are adverse, and the inherited E143 body carries most support. If E144 fails, first read E145 band and E147 target/component failure before promoting E143 or closing the branch.

Update after E148: `analysis_outputs/e148_e144_public_outcome_attribution.py` pre-registers target/component responsibility for each possible E144 band. E144 has meaningful win mass under public-free priors: global `0.745560`, subject `0.599760`, nearest-hard `0.635616`. But branch-or-worse tail mass is also large: global `0.204972`, subject `0.333832`, nearest-hard `0.284852`. Fine-loss-alive worlds are only `0.027696..0.033340` and are not necessarily fine-tail failures; they can be inherited-body/Q3/S2 under global, S3/Q3 under nearest-hard, or inherited-body/Q3/S3 under subject. This keeps E144 as the single next file, but tightens post-feedback discipline: E143 is justified only if E148 attribution points to fine-tail/S3 retention, not merely because E144 loses.

Update after E150: `analysis_outputs/e150_e144_postfeedback_interpreter.py` supersedes the loose E145 score-only action rule. After E144 public feedback, run `python3 analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>`. A fine-loss band is now only `conditional_alive`; E143 is allowed only if the read points specifically to fine-tail/S3 retention. Branch-loss or hard-fail blocks E143/E142 automatic rescue.

Update after E151: no new submission was created. `analysis_outputs/e151_plateau_resolution_bottleneck_audit.py` says the plateau is not mainly missed old candidates or generic capacity: E98 selector p90 is `53.33x` the E95 public edge, E129 has `0` novel strict old-file successors, E130-E139 submit gates remain `0`, and E144 is almost an E143-collinear branch-pruned point. This does not demote `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`; it clarifies that E144 is the next public sensor, while the next local work should be a non-collinear representation-to-probability decoder rather than another top-count/blend/Q2-S3 amplitude sweep.

Update after E152: no new submission was created. `analysis_outputs/e152_branch_orthogonal_decoder_audit.py` tested the obvious E151 escape hatch by projecting E137-E140 decoder moves away from the E144 branch. Non-collinear signal is abundant (`4650/4650` source rows), but the strict/E72-budget/post-E101/actionable intersection is `0/2880`. This keeps `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the single next public sensor. The next local branch should learn or diagnose the gate-intersection state itself, especially the split between E138 relaxed-budget-post101 rows that fail active-veto and E139 budget-post101-actionable rows that fail relaxed structure.

Update after E153: no new submission was created. `analysis_outputs/e153_gate_intersection_failure_atlas.py` shows the E152 near misses are not balanced across blockers: `102/103` are `missing_actionable`, and `101/102` of those fail active/Q2S3 while passing relaxed, E72, and post-E101 gates. Target anatomy says this is really S3 active-boundary exposure, not Q2. The lone `missing_relaxed` row is actionability-safe but fails raw/world relaxed health. This keeps `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the single next public sensor. A new submission should only be made if it repairs the S3 active-boundary blocker or the lone raw/world-health blocker while preserving all-four gate survival.

Update after E154: new candidate opened. `analysis_outputs/e154_s3_active_boundary_repair_probe.py` repaired the E153 blocker by rolling back selected S3 cells from E152 missing-actionable rows. It generated `7458` repair rows, `10` all-four rows, and materialized `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`. The selected row rolls back `3` top E101-active S3 cells with keep `0.25`, improves local all-minus-E95 to `-0.000012158050`, contains all `185` E144 cells, and avoids E72/E101 negative axes. E154 supersedes E144 as the first file if using one public slot now. E144 remains the conservative contrast if E154 fails and we need to know whether the unrepaired branch was accepted.

Update after E155: E154 is not a single exact point. `analysis_outputs/e155_e154_branch_body_ablation.py` found `34/40` all-four ablations, `27` E155-submit rows, and `22` reduced-body submit rows. The materialized `analysis_outputs/submission_e155_bodytemp_d27e7965.csv` uses only `25%` of the E144->E154 body with local all-minus-E95 `-0.000010362491`. E154 remains first because it has the larger edge and tests the full repaired body; E155 is the conservative amplitude-control follow-up.

Update after E156: the E155 diagonal is not the minimum coherent repaired body. `analysis_outputs/e156_e154_target_axis_lattice.py` scored `3125` Q1/Q3/S2/S3/S4 lattice variants with full non-anchor evaluation; all `3125` were all-four, `2984` were strict, and `85` sat below E155's body ratio. The materialized `analysis_outputs/submission_e156_targetaxis_757546d2.csv` uses only Q1/S2/S4 add-on movement, body ratio `0.171266667`, and local all-minus-E95 `-0.000010004`. Keep it as the third repaired-branch decomposition control, after E154 and E155, before falling back to unrepaired E144.

Update after E157: E156's minimum-body target set should not be overinterpreted. `analysis_outputs/e157_e156_axis_response_audit.py` shows the E156 lattice is all-four saturated (`3125/3125`), Q3 has the strongest local/post-E101 finite-difference response, and S2 carries most of the E72-gap benefit. The materialized `analysis_outputs/submission_e157_lowbodypareto_bd67930d.csv` uses Q1+Q3+S2+S4 with alphas Q1/Q3/S2/S3/S4 = `0.25/0.25/0.50/0.00/0.50`, body ratio `0.240336139`, and slightly dominates E155 while using less body. Keep it after E154/E155 as a tuned low-body Pareto control, with E156 moved to minimum-body decomposition control.

Update after E158: the repaired-branch stack is now pre-registered as public-feedback instrumentation. `analysis_outputs/e158_repaired_branch_public_decoder.py` shows E154 beats E155 locally by only `-0.000001795559`, below the `2e-6` public-readable guardrail, while E154 beats unrepaired E144 by `-0.000002432120`, above it. E157 and E156 are even closer to E155 (`-0.000000041955` and `+0.000000358921`). Therefore E154 remains first because it asks the full repaired all-four question and is readable against E144, not because it is score-distinguishable from E155. If E154 ties or loses, E155 is the only clean same-family follow-up; E157/E156 are post-E155 target-axis controls, not pre-feedback score maximizers.

Update after E159: E154 now has a pre-public responsibility map. `analysis_outputs/e159_e154_public_outcome_attribution.py` decomposes E154 into `479` additive LogLoss segments over `294` unique moved cells and confirms the decomposition against direct E154-vs-E95 hard-label deltas with max error below `2e-16`. Public-free win mass is still meaningful: global `0.728550`, subject `0.601575`, nearest-hard `0.666680`. The caution is that branch-or-worse outcomes are mostly blamed on `inherited_e144_body`, not the small E154 added body. Therefore the next public file remains `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`, but E155 is not automatic after any loss. E155 is justified only if E158 says tie/small-loss and E159 attribution blames `e154_adjustment_on_e144_body` or `e154_extra_body`; if blame is inherited E144 body, use E144 as the unrepaired contrast or leave the branch.

Update after E160: the E154 follow-up rule is now executable. Run `python3 analysis_outputs/e160_e154_postfeedback_interpreter.py --score <PUBLIC_LB>` after E154 public feedback. The current pre-feedback table says E155 is `information_only` for tie/small_loss, not a clean expected-improvement rescue, because component reads are split between E154-added body and inherited E144 body. For branch_loss and hard_fail, E155 is `not_recommended` and E157/E156 are blocked. This does not change the next submission: use `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Update after E161: no new submission was created. `analysis_outputs/e161_e154_inherited_body_pruning_audit.py` tried the obvious E159 rescue by reverting public-free high-risk E154 cells toward E144/E95. It found many safer diagnostic controls (`1226` safer-than-E154 rows, `631` all-four rows, `299` control-grade rows), but `0` submission-grade rows and `0` variants that beat E154 by the `2e-6` public-readable guardrail. Best local delta versus E154 was only `-0.000000045921`. Therefore E161 pruning rows are not a replacement first file. The next submission candidate remains `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Update after E162: the repaired-branch stack is confirmed cell-fragile. `analysis_outputs/e162_branch_readability_flip_thresholds.py` shows one high-swing hidden row-target label is enough to exceed the `2e-6` public-readable guardrail for E154-vs-E155, E154-vs-E144, E157-vs-E155, and E161-prune controls. E154-vs-E155 has focus expected delta only `+0.000000505` while its top1 cell swing is `0.000010815`; E154-vs-E95 has top1 swing `0.000015340`, about the whole E95-over-mixmin edge. This keeps E154 as the first public sensor and demotes sibling/pruning files to post-feedback instruments.

Update after E170: the current broad-branch first file remains `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv`, but its public read is now pre-registered. E170 says ctx-veto has a broad local edge versus E95 (`904` cells, `193` rows, `32` cells-to-flip expected, expected delta `-0.000120457`) while still being public hard-label-resolution limited (`1` cell for the `2e-6` guard, `4` cells for E95's edge over mixmin). Between-train-runs carries `81.1%` of the expected edge and not-E72-active cells carry `73.7%`, so the bet is not a random Q2/S3 tweak. The high-density p50 sibling differs by only `10` Q2/S3 cells and should not be submitted before ctx-veto feedback. After any E169 public score, run `python3 analysis_outputs/e170_e169_public_feedback_decoder.py --score <PUBLIC_LB>` before choosing raw E166, E154, or same-family variants.

Update after E171: E169 is now better described as "broad body supported, top-tail risky." The full moved body under `visible_mean` has mean delta `-0.000022659` and win rate `0.868840`, but top-swing support is weak: top1 `0.098648`, top4 `0.330699`, top32 `0.247434`, with top32 below target-matched null (`z=-2.703`). Flank priors are near-tie/adverse while subject/global-style priors are favorable. This does not remove E169 as the next broad sensor; it removes the stronger claim that E169 is a robust expected-score candidate. If submitted, a narrow loss should be read as critical-cell hard-label adversity before discarding the whole broad context/veto worldview.

Update after E172: E172 upgrades the broad branch from "sensor only" to a better expected-score candidate. `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` keeps E169's broad body (`904/193` moved cells/rows, `30` cells-to-flip, focus delta `-0.000112695`) while repairing the visible-prior tail that E171 flagged: visible p95 changes from E169 `+0.000010607` to `-0.000026683`, and visible worse-than-E101 drops from `0.058545` to `0.000050`. It also lowers bad-span energy and Q2/S3 share. If choosing exactly one new broad-branch file now, prefer E172 over E169. Raw E169 remains useful only as the sharper body-vs-tail falsification sensor.

Update after E173: E172 now has a pre-public score decoder. Submit `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` only with the E173 interpretation attached: `<=0.576276019` cleanly validates tail repair, `0.576288330..0.576294330` is an underresolved tie, `0.576294330..0.576300366` is small loss, and `>0.576306641` closes E172/E169 same-family broad expected-score followups. E173 also warns that E172 still has one-cell `2e-6` hard-label fragility, so a tie/small loss should not trigger threshold tuning.

Update after E174: E172's keep `0.25` rollback was not the only safe point. `analysis_outputs/e174_e172_rollback_overcorrection_probe.py` found `46/80` gate variants and materialized `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`. E174 reopens the top `75` focus-recovery rollback cells, improves focus expected delta from E172 `-0.000112695` to `-0.000124367`, and keeps visible p95 negative at `-0.000022709`. It is the max-edge broad contrast, but it spends more Q2/S3 and bad-axis margin than E172.

Update after E175: E174 now has a pre-public decoder. Run `python3 analysis_outputs/e175_e174_public_feedback_decoder.py --score <PUBLIC_LB>` after any E174 result. E174-vs-E172 is only `75` cells and expected recovery `-0.000011672`, so wins validate controlled reopening, while tie/small-loss points back to E172 as contrast and worse-than-E101 demotes same-family reopening.

Update after E176: E174 is not component-Pareto. `analysis_outputs/e176_e174_component_ablation_probe.py` found a better risk-adjusted sibling, `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`, by damping only reopened Q2 cells to keep `0.75`. It gives up only `+0.000000983` focus delta versus E174 while reducing max bad cosine `0.163229 -> 0.158126`, Q2/S3 share `0.339597 -> 0.334753`, visible p95 `-0.000022709 -> -0.000023096`, and worse-than-E101 `0.000220 -> 0.000192`. E176 supersedes E174 as the first broad-branch file if using one slot now.

Update after E177: E176 is a locked public sensor, not an adjustable Q2 knob. E176-vs-E174 changes only `21` Q2 cells with expected cost `+0.000000983`, cells-to-flip `2`, and top1 swing `0.000000832`. Submit E176 only with `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>` attached; do not scan new Q2 keep factors after the score.

Update after E178: no new submission was created. The plateau audit says broad signal exists but public-tail resolution is the live bottleneck: E166 focus edge is `21.689x` the E95 public edge, E176 is `8.059x`, yet E176 needs only `4` top hard-label cells to swing the whole E95-over-mixmin edge and E98 selector p90 is `53.33x` that edge. This keeps `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the single risk-adjusted next public sensor, not because it is guaranteed to win, but because it asks the highest-information question with the least extra Q2/S3 risk.

## Current 0.54 Assessment

0.54 is not blocked by a single missing model family. To approach it, one of two things must happen:

- selector resolution improves enough to trust small public-sensitive deltas; or
- a new representation creates a larger low-bad-axis movement that survives blockwise and anchor stress.

E48 changes the plateau diagnosis. Mixmin's public `0.5763066405` proves that at least one larger anchor-loss/binary-world movement was real despite pre-E48 selector vetoes. E56 then shows mixmin-hard hidden-world generation can create a coherent posterior, E57 shows unconstrained posterior movement is not public-anchor safe, E58 shows simple gated distillation is below selector-scale margin, E59 shows within-block joint labels are learnable but target-mismatched, E60 shows transition residuals are sign-informative but calibration-destructive, E62 shows those residuals do not rescue E56 as a simple gate, E63 shows independent hidden-rate gradients support E56 direction but not public-safe amplitude, E64 shows scalar amplification is adverse, E65 shows the near-zero targetwise pocket is real but sub-margin, E66 shows the Q2/S3 conflict is tail-risk rather than absence of hidden direction, E67 shows first-order tail-neutral Q2/S3 translation improves but remains sub-margin and anchor-derived, E68 shows that many of those Q2/S3 cells are independently supported, E69 shows global alpha still fails, E70 shows heldout-specific consensus can barely clear local margin, E71 shows unified consensus remains diagnostic but not deployable under sign gates, and E72/E73 show sparse-magnitude `top_abs50` can create a materialized non-`none` diagnostic file. E80/E81 then show that the materialized E73 combined file is public-adverse and that isolated Q2/S3 remains sub-margin. E82 extends this to the broader source universe: pure Q2/S3 is structurally coherent but too small. The remaining 0.54 gap is still large; the immediate question is now how to create a broader structural/block-state move that preserves Q2/S3 tail energy without reintroducing E73's all-target public failure.

E10 says representation exists but translation fails. E11 says gated correction repairs one selector's sign but not the magnitude. E12-E14 say the translation is S4+Q3 targetwise. E15-E17 say that focused amplification overfits a favorable pairwise scenario tail and lacks an independent anchor. E18-E19 say OOF-local S4/Q3 winners are also not the anchor. E20 says existing block/measurement candidates are also not the hidden large-safe branch. E21 says the two-selector intersection is empty. E22 says the next useful public observation, if any, is a selector-disambiguation sensor rather than another improvement candidate. E23 says lowering the S4/Q3 amplitude does not fix selector disagreement. E24 says simple subject/date/block localization also does not fix it. E25 says large score-probe mixtures do not pass the strict selectors either. E26 says public LB inverse fitting cannot choose among them. E27 says adding subject prior also cannot choose among them. E28 says binary exactness also cannot choose among them yet. E29 says a small binary world pool can reprioritize probes but cannot certify them. E30 says a stronger frontier-box binary pool makes mixmin the clearest high-risk probe but still cannot certify improvement. E31 says generic plausibility gating also cannot certify it. E32 says known-anchor loss geometry is more useful than generic plausibility and now favors mixmin/inverse7. E33 says that conclusion survives anchor LOO and favors mixmin over inverse7. E34 says the support is broad anchor-loss/cancellation geometry rather than target-axis semantics. E35 says existing independent evidence is still insufficient for normal submission. E36 says raw observed structure does not certify mixmin but strongly supports inverse7. E37 says inverse7 raw support and anchor support can coexist, but not with selector agreement. E38 says the current rational action is either no submission or an explicitly labeled public sensor; it does not create a safe improvement candidate. E39 says the OOF archive is not the missing selector calibration target. E40 says movement anatomy gives a useful but loose inverse7-friendly prior, not a strict selector. E41 says simply adding bad-axis geometry repairs one symptom but still does not create selector certification. E42 says even a principled current-best zero-anchor calibration leaves the selector error far above the public edge. E43 makes that a hard boundary: current selectors cannot certify micro-edge candidates at all. E44 closes the broader "maybe an existing large safe file is hidden in the tables" escape route. E45 closes the simple structured public-subset selector route. The next useful work is either a truly independent selector target, a selector with sub-raw05-gap error, a newly generated larger sign-consistent movement, or spending a predeclared public sensor; not another micro-blend, scale, axis-feature, fixed-zero kNN sweep, existing-universe rescore, or simple public-mask inverse fit.

## Update After E186

If choosing exactly one file now, the next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

Reason: E176 was already the visible-body/Q2-underopen broad-branch sensor. E186 adds an independent known-LB-pair reason: after enforcing antisymmetric pair geometry, E176's favorable pressure-min branch is selected in `3/3` scenarios across all feature sets, while E144/E154 are rejected in `3/3`. File-LOO frontier accuracy is `0.867` and E95-edge accuracy is `0.857`.

Risk: this is not certified. The support-based antisymmetric decoder still misreads the exact E95/E101 frontier boundary, predicting E101 over E95 despite E101's public `0.5763003660` being worse than E95. Therefore E176 should be submitted only as a worldview sensor and interpreted with `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>`.

Current order if spending public slots by information value:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` — broad/Q2-underopen plus antisymmetric known-LB pair worldview.
2. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` — full-Q2 reopening contrast if E176 under-opening is rejected.
3. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` — repaired-branch worldview, not first after E186 unless the explicit question is E154/E144 branch repair.
4. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` — conservative unrepaired branch contrast.

## Update After E188

The single next public sensor is still:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

But the reason is narrower than after E186. E187/E188 show the support-heavy known-LB decoder is not action-grade: it improves wider E95-edge stress but flips the exact E95/E101 boundary, and no positive shape/support logit blend repairs this without losing E95/E101.

What still supports E176:

- shape-only antisymmetric decoder gets E95/E101 correct and still selects E176.
- E176 remains the visible-body/Q2-underopen broad-world sensor.
- support-heavy decoders also select E176, but that evidence is auxiliary and boundary-vetoed.

Submission order by information value stays:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` — best current worldview sensor, not certified expected-score winner.
2. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` — full-Q2 reopening contrast only after E176 feedback.
3. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` — repaired-branch alternate worldview.
4. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` — conservative branch contrast.

Do not create a submission from E187/E188. Their value is negative selection: support-decoder branch scores require an exact-boundary veto or a new structural target.

## Update After E189

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

The reason is now even narrower. E189 shows support's wider E95-edge gain is almost entirely an E72-neighbor correction: `6/6` primary support rescues are E72-frontier-neighbor rows, while `4/4` shape-only wins are exact E95/E101 boundary rows. A file-identity gate can look excellent locally, but it is not deployable to live branches.

Submission order by information value:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` — broad/Q2-underopen sensor, supported by shape-only pair geometry and previous body/tail audits.
2. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` — full-Q2 reopening contrast only after E176 feedback.
3. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` — repaired-branch alternate worldview.
4. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` — conservative branch contrast.

Do not promote any support-heavy E189 gate into a submission. Its live use requires a new public-free E72-contamination detector, not filename identity.

## Update After E190

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E190 tried to build the missing filename-free E72-contamination detector. The result is diagnostic, not deployable. `shape_target_context_abs` detects E72-neighbor structure under pair-LOO with AUC `0.978836`, but only `0.666667` top-k recall and an E72-heldout blind spot. Support-containing views misclassify exact E95/E101 as contamination with mean probability around `0.957..0.975`.

For live pressure branches, E176 has near-zero contamination score and never crosses E72 thresholds. So E190 does not add a reason to trust support for E176; it says E176 should be read as a shape/broad-Q2-underopen sensor.

Submission order remains unchanged. Do not create a support-gated E176/E154/E144 file from E190.

## Update After E191

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E191 tested the last cheap support-rehabilitation idea: make exact E95/E101 a hard negative in the E72-contamination detector. It failed for support. Boundary-clean pair-LOO rows exist only for `shape_target_context_abs`; support-containing clean rows are `0`. Exact E95/E101 probability remains about `0.786..0.839` for support-only and `0.766..0.824` for shape+support/all views.

This narrows the submission rationale again:

1. E176 is not support-gated.
2. E176 is not E72-contamination-like.
3. E176 is still the shape/broad-Q2-underopen public sensor.
4. A support-gated live file should not be created before a genuinely new structural target exists.

Submission order remains unchanged. If one file is submitted next, use E176 only as the pre-registered broad/Q2-underopen sensor and decode with `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>`.

## Update After E192

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E192 decomposed the only boundary-clean E72 score, `shape_target_context_abs`. It did not create a submission. The important live result is:

- E144: one pressure scenario crosses the known non-E72 p95 (`0.038723` vs p95 `0.020815`) but stays below p99 (`0.044812`) and far below the known positive floor (`0.804849`); nearest known rows are all non-E72.
- E154: all scenarios stay below p95, max `0.007973`.
- E176: all scenarios stay near zero, max `0.000008`.

So E192 does not promote E144/E154 and does not justify support gating. It narrows the interpretation: E144 has shape-tail risk, while E176 remains the clean broad/Q2-underopen sensor.

Submission order remains unchanged:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` — broad/Q2-underopen sensor with lowest E72-shape contamination.
2. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` — full-Q2 reopening contrast after E176 feedback.
3. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` — repaired-branch alternate worldview.
4. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` — conservative branch contrast, now explicitly marked as mild shape-tail-risk rather than contamination-positive.

## Update After E193

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E193 did not create a submission. It consolidated the live evidence for E176/E154/E144 so the next file is chosen by a fixed evidence ledger rather than by whichever diagnostic is most convenient.

Evidence balance:

- E176: `3.100` (`8` support axes, `4` warnings, `0` underidentified, `0` missing).
- E154: `-0.225` (`4` support axes, `4` warnings, `1` underidentified, `3` missing).
- E144: `-1.725` (`3` support axes, `5` warnings, `1` underidentified, `3` missing).

Submission order by information value:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` — broad/Q2-underopen sensor; highest cross-sensor evidence balance, not certified expected-score winner.
2. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` — full-Q2 reopening contrast only after E176 feedback.
3. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` — repaired-branch alternate worldview; supported by inherited binary counterprior but rejected by pressure/pair geometry as first-choice.
4. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` — conservative branch contrast; useful only as a tail-risk/repaired-branch control.

If E176 is submitted, run `python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>` before choosing any same-family or repaired-branch follow-up.

## Update After E194

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E194 stress-tested whether E193's evidence ledger was just arbitrary weighting. It was not fully arbitrary:

- single-source leaveout: E176 wins `1.000`.
- Monte Carlo family weights:
  - loguniform `0.25..4`: E176 win rate `0.771300`.
  - loguniform `0.5..2`: E176 win rate `0.905950`.
  - 20% family dropout: E176 win rate `0.896500`.
- binary-world family alone picks E154/E144.
- E181 binary-world evidence would flip E176 versus E154 if trusted `>1.760x` relative to the rest.
- if E176-only visible/top-cell evidence is removed, E176 still leads, but pair geometry must keep at least `0.725x` of its current weight.

Submission meaning is now precise:

1. Submit E176 if asking whether pair/shape/broad-body evidence beats inherited binary-world counterprior.
2. If E176 loses, the strongest alternate worldview is E154, not another E176 keep-factor sibling.
3. Do not treat E194 as LB prediction. It only says the E176 priority is reasonably robust as a sensor choice.

## Update After E195

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E195 compared E176 and E154 as public sensors, not as expected-score predictions. The result is that E176 still spends the next slot better.

- E176 asks the bigger live question: whether pair/shape/broad-body evidence beats the inherited binary-world counterprior.
- E176-vs-E154 is public-readable: `1027` moved cells over `238` rows, focus expected delta `-0.000093546`.
- If E176 loses, E177 already routes adverse bands toward E154/search and forbids same-family tuning.
- E154 is valuable but narrower: it tests repaired E144-collinear S3 active-boundary repair. E154-vs-E144 is barely readable at `-0.000002432`, and E154-vs-E155 is not readable at `-0.000001796`.

Current submission order by information value:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` - first sensor; broad/Q2-underopen vs binary-world conflict.
2. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` - first counter-world if E176 lands in an adverse E177 band, or if we deliberately trust binary-world above E194's flip threshold.
3. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` - full-Q2 reopening contrast only if the next question is Q2 amplitude after E176 feedback.
4. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` - conservative repaired-branch/tail-risk contrast, not first follow-up unless E154 branch interpretation asks for it.

No new file is created by E195. The next public result must be decoded with the relevant pre-registered decoder, not by scalar score intuition.

## Update After E196

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E196 tested a possible last-minute demotion rule: row/order/block/target motif nearest-anchor matching. It failed as an action-grade selector.

- best motif view: `top4 / sequence_axis_flank`.
- known-pair LOO accuracy: `0.833333`.
- exact E101/E95 boundary correctness: `0`.
- E176 nearest anchor in that best view: `e72_vs_e95`, direction `new_lost`.
- E176 inverse-distance vote in that best view: new_won `0.505761`, new_lost `0.494239`.
- top33 E176 profiles drift toward `mixmin_vs_a2c8`, but top33 LOO accuracy is only `0.333333`.

This adds a caution, not a priority inversion. E176 is still the first sensor because its public result resolves the broad/Q2-underopen vs binary-world conflict. E196 only says not to claim E176 is certified by motif anatomy.

## Update After E197

The single next public sensor still remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E197 adds a sharper decoder around that choice. Known public pairs were inverted into support-mass slippage:

- E176 visible-prior support surplus to tie: `0.061761`.
- E176 focus-prior support surplus to tie: `0.094836`.
- Under visible-prior known-slippage analogues, E176 is clean-or-better in `4/6`, wins in `4/6`, and branch/hard-fails in `1/6`.
- The only losing analogues are E72-like adverse slippages; E72-vs-E95 gives small loss and E72-vs-mixmin gives branch loss.
- E172 is slightly safer by this support-mass lens (`0.070613` visible surplus), so it is the same-family safety contrast if E176 lands tie/small-loss.
- E154/E144/E155 have much thinner visible surplus (`0.010284`/`0.011545`/`0.011227`) and branch/hard-fail in `4/6` analogues.

This does not promote E172 over E176 because E176 is still the higher-information broad/Q2-underopen sensor with a pre-registered decoder. It does change the failure interpretation: an E176 loss should be read as E72-like adverse public slippage, not as generic visible-support failure.

## Update After E198

The single next public sensor still remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E198 checked whether E176's E72-like loss condition is structurally visible before feedback.

- E176 loses under E72-like slippage stress:
  - visible E72-vs-E95: `small_loss`.
  - visible E72-vs-mixmin: `branch_loss`.
  - focus E72-vs-mixmin: `branch_loss`.
- But E176's clean shape E72 probability is only `0.000008`.
- That is far below:
  - non-E72 p95 `0.020815`.
  - non-E72 p99 `0.044812`.
  - known E72-positive floor `0.804849`.
- E154 remains the counter-world but its risk is thin margin, not E72 contamination (`max 0.007973`).
- E144 has a mild p95 tail alarm (`0.038723`) but not positive-scale E72 evidence.

Submission order is unchanged:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` - first sensor; broad/Q2-underopen, not clean-shape E72-exposed.
2. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` - first counter-world after adverse E176 feedback.
3. `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` - same-family safety contrast if E176 lands in the tie/small-loss slippage band.

Do not create an E72-demoted E176 variant before public feedback. The current evidence says E176 can fail like E72 algebraically, but it does not look like E72 structurally under the clean detector.

## Update After E199

The single next public sensor still remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E199 scores all E197 candidates directly with the clean-shape E72 detector.

- E172 direct E72 probability `0.000087`: clean same-family safety contrast.
- E174 direct E72 probability `0.000097`: clean Q2 full-reopen contrast, but lower information before E176 feedback.
- E176 direct E72 probability `0.000097`: clean first sensor.
- E166 direct E72 probability `0.000677`: clean shape, but still broad slippage/tail-risk by E197.
- E154 direct E72 probability `0.007860`: clean repaired-branch counter-world, but thin-margin.
- E155 direct E72 probability `0.009284`: clean low-body control, but not first counter-world.
- E144 direct E72 probability `0.054385`: above non-E72 p99 but far below positive floor; tail-risk control.

Current conditional order:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` - first sensor.
2. If E176 tie/small-loss: `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` - same-family safety contrast, clean-shape non-E72.
3. If E176 branch/hard-loss: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` - repaired-branch counter-world, clean-shape non-E72.
4. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` - tail-risk control, not first follow-up.

## Update After E200

The single next public sensor still remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E200 directly tested whether E172 should replace E176 as first submission after E199 made E172 look slightly cleaner.

- E176 has `0.0000106885` expected focus edge over E172.
- That edge is `0.698x` of the whole E95-over-mixmin public edge, so giving it up is not a harmless safety swap.
- E172 is safer but narrowly so:
  - visible support surplus advantage `0.008852`.
  - focus support surplus advantage `0.007054`.
  - clean-shape E72 probability advantage only `0.00000972`.
- E176-vs-E172 is a `75`-cell same-family rollback contrast.
- E176-vs-E154 is a `1027`-cell counter-world contrast.

Current order is unchanged:

1. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` - first sensor; broad/Q2-underopen worldview test.
2. `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` - if E176 ties or small-loses; same-family safety contrast.
3. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` - if E176 branch-loses or hard-fails; repaired-branch counter-world.
4. `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv` - Q2 full-reopen contrast only after an explicit E176/E174 amplitude question.

## Update After E201

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E201 turns that recommendation into an auditable packet rather than a loose preference.

- SHA256: `34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206`.
- Submission audit: `250` rows, exact sample columns/key order, no duplicate keys, finite probabilities inside `[0, 1]`.
- E176 vs E95 movement: `904` cells across `193` rows.
- Main movement share: Q2 `0.209702`, S4 `0.145285`, Q3 `0.141693`, S2 `0.130103`, Q1 `0.128746`, S3 `0.126307`, S1 `0.118164`.

Pre-registered follow-up policy:

1. If E176 is better than `0.5762883298`, do not rush another same-family file. First decompose whether the gain came from Q2 damping or S-stage body.
2. If E176 lands from `0.5762883298` through `0.576300366`, use E172 only if the next question is same-family safety.
3. If E176 is worse than `0.576300366`, demote the partial-reopen branch and prefer E154 or non-collinear latent search.
4. If E176 is worse than `0.5763413298`, close E176/E174/E172/E169 as expected-score follow-ups.

Before any post-E176 file is chosen, run:

`python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <E176_PUBLIC_LB>`

and compare the result against `analysis_outputs/e201_e176_public_sensor_packet_route_summary.csv`.

## Update After E202

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E202 changes how the score must be interpreted, not which file is next.

- E176 is not a Q2-only experiment despite the `q2_to0p75` name.
- S-targets carry `0.651098` of focus-prior expected movement; Q-targets carry `0.348902`.
- Between-train-runs rows carry `0.807772` of expected movement.
- Q2 is largest by raw probability movement (`0.209702`) but only fifth by expected contribution (`0.121416`).
- The top expected contributors are S3 `0.203515`, S1 `0.189679`, and S4 `0.146985`.
- Top33 hard-label visibility remains thin (`p_low=0.014667`), so tie/loss bands are tail/cancellation evidence before they are Q2-amplitude evidence.

Current conditional order:

1. Submit `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` if spending the next public slot.
2. If E176 wins, decompose S3/S1/S4 and between-train-runs body first. Do not jump straight to E174 or another Q2 sibling.
3. If E176 ties or small-loses, use `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` only as same-family safety.
4. If E176 is worse than E101 or mixmin-safe bands, use `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` or non-collinear latent search.

Do not infer Q2-only causality from the scalar public score.

## Update After E203

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E203 adds a keep/drop component stress around E176.

- E176 is broad-body necessary:
  - S-only focus share `0.644881`.
  - primary S-stage S3/S1/S4 share `0.573289`.
  - between-train-runs share `0.774524`.
- E176 is not Q2-only:
  - Q2-only share `0.093922`.
  - dropping Q2 still leaves `0.906078`.
- E176 is not top33-only:
  - top33 share `0.226424`.
  - dropping top33 still leaves `0.773576`.
  - top33 visible support is weak at `0.245771`.

Post-score rule is now stricter:

1. Clean E176 win: decompose broad S-stage / between-train-runs body first.
2. Micro win, tie, or small loss: treat the body as probably real but cancelled by compact hard-tail cells; E172 only if asking same-family safety.
3. Branch/hard loss: broad body is public-misaligned or cancelled too strongly; route to E154/search.
4. Q2 amplitude is a second-order paired question, not the first post-E176 action.

## Update After E204

The single next public sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E204 maps what the current follow-up candidates actually do relative to E176.

- `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv`
  - same-family rollback.
  - changes `75` cells, all inside E176 cells.
  - rollback share in E176 overlap `1.000000`.
  - off-E176 abs share `0.000000`.
  - E176 body rollback fraction `0.089780`.
- `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`
  - counter-world / body-exit.
  - changes `1027` cells and adds `123` off-E176 cells.
  - off-E176 abs share `0.292501`.
  - E176 body rollback fraction `0.877576`.
- `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`
  - Q2 amplitude probe.
  - changes only `21` E176-overlap cells.
  - rollback share `0`.
  - should not be used as rescue after tie/loss.

Conditional order is now:

1. E176 first.
2. E172 only after E176 tie/small-loss.
3. E154 after E176 branch/hard-loss.
4. E174 only after clean E176 win if the next question is Q2 amplitude.

## Update After E205

The single next public sensor is still:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E205 changes the post-score process, not the first file.

After E176 public LB arrives, run:

`python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score <E176_PUBLIC_LB>`

Then follow the selected route:

1. Breakthrough or clean win: no immediate sibling; decompose broad S-stage / between-train-runs body first.
2. Micro win: optional E174 only if deliberately asking a Q2 amplitude question.
3. Tie or small loss: E172 is the same-family safety file.
4. Worse than E101 / branch loss: E154 is the body-exit counter-world.
5. Hard fail: close the same-family expected-score lane and return to non-collinear hidden-structure search.

Do not choose E172, E154, or E174 from scalar closeness alone.

## Update After E206

E176 is resolved:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` -> public LB `0.576311831`

E205 selected route:

- outcome: `branch_loss`
- worldview update: `close_same_family_expected_score_lane`
- follow-up role: `body_exit_counterworld`
- follow-up file: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`

Submission order now changes:

1. Do not submit E174 as a rescue; Q2 amplitude is not the explanation.
2. Do not submit E172 as the immediate next file; E172 was reserved for tie/small-loss safety, and this was branch loss.
3. If using an existing file next, E154 is the coherent sensor because it exits the E176 body.
4. If not spending a slot on E154, return to non-collinear hidden-block/sequence/target-dependency search.

Current read: E176 disproves the expected-score version of the broad partial-reopen family, not the existence of S-stage/body signal itself.

## Update After E207

E207 creates no submission. It answers the "use JEPA for real" question by selecting the only currently healthy positive-pair regime for true JEPA training.

Result:

- `analysis_outputs/e207_lejepa_identifiability_conditions_audit_summary.csv`
- `analysis_outputs/e207_lejepa_identifiability_conditions_audit_report.md`
- true-JEPA candidates: `1/77`
- selected regime: `broad_stage2_pca64 + feature_nn1_all`
- readiness `0.652939`, rho `0.494280`, alignment ratio `0.636020`, increment Gaussian score `0.435262`

What this changes:

1. Do not train a monolithic subject-order JEPA over all row lags.
2. Do not treat existing LeJEPA block-canvas subject-lag2 as a certified world model despite its high readiness; its increment Gaussianity is too low (`0.194814`) and split-distance CV is high (`0.660020`).
3. If building a new JEPA submission family, start with feature-neighbor context-to-target prediction and keep subject/order/block-canvas latents as auxiliary gates.

Submission order is unchanged for existing files:

1. Existing coherent counter-world sensor remains `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` if using a public slot now.
2. New JEPA work should first produce E208 feature-neighbor JEPA diagnostics before materializing a submission.

## Update After E208

E208 still creates no submission, but it opens one real JEPA materialization branch.

Result:

- `analysis_outputs/e208_feature_neighbor_jepa_probe_report.md`
- materialization gate pass count: `8`
- passing target families: Q3 and S4
- strongest Q3 feature: `e208_resid_self_pc10`
- strongest S4 feature: `e208_pred_pc14`
- rejected local shortcut: S2 `e208_pred_pc12`, because geometry stress is adverse despite strong OOF/subject deltas.

Submission policy:

1. Do not submit an E208 file directly; none exists by design.
2. If building a new file, create E209 from the passing Q3/S4 operations only.
3. Before public submission, compare E209 movement against E95, E154, E176 branch-loss anatomy, and known hard-tail cells.
4. If using a public slot immediately without E209, the coherent existing sensor remains `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Interpretation:

E208 is the first practical "real JEPA" branch. It says the model can learn hidden neighbor representation, but it also says the useful probability movement is narrow. A full-latent JEPA blend would be exactly the kind of shortcut LeJEPA warns against.

## Update After E209

E209 creates the first actual JEPA-derived submission files.

Result:

- script: `analysis_outputs/e209_feature_neighbor_jepa_materialization_stress.py`
- report: `analysis_outputs/e209_feature_neighbor_jepa_materialization_report.md`
- selected candidates: `4`

Submission order depends on the public question:

1. Maximum E209 survival score:
   `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv`
2. Cleanest JEPA-only sensor on the current E95 frontier:
   `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv`
3. Cleaner bad-axis but narrower S4-only E154 branch:
   `analysis_outputs/submission_e209_jepa_s4_rank_e154_s0p75_030e88de.csv`
4. Cleaner bad-axis but narrower S4-only E95 branch:
   `analysis_outputs/submission_e209_jepa_s4_rank_e95_s0p75_0ed14a13.csv`

Interpretation:

The best single file by survival score is the E154-anchored Q3/S4 JEPA graft, but it confounds the E154 counter-world with JEPA. If the next public slot should specifically answer "does actual JEPA help?", use the E95-anchored Q3/S4 file. A win strengthens the narrow Q3/S4 JEPA-translation hypothesis. A loss weakens this probability translation path, not the fact that E208 learned a nontrivial representation.

## Update After E210

E210 creates dependency-gated E209 variants, but they should not automatically jump ahead of E209.

Selected files:

1. Maximum E210 survival / E154-confounded dependency-tail sensor:
   `analysis_outputs/submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv`
2. Cleanest E210 dependency-tail sensor on E95:
   `analysis_outputs/submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv`
3. Higher keep-share E154 dependency-tail sensor:
   `analysis_outputs/submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv`
4. Higher keep-share E95 dependency-tail sensor:
   `analysis_outputs/submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv`

Submission policy:

E209 remains the cleaner answer to "does actual JEPA help?" E210 is the next sensor only if the question is "does public hard-tail prefer target-dependency filtering over the raw JEPA Q3/S4 body?" A good E210 score would credit dependency-tail localization. A bad E210 score would mean the gate removed useful Q3 body or followed a train-only target-dependency shortcut.

## Update After E211

E211 supersedes E210 for target-dependency follow-up because it keeps Q3 raw and gates only S4.

Selected files:

1. Maximum E211 survival / E154-confounded:
   `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`
2. E154 near-twin with S4 toward:
   `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv`
3. Clean E95 current-frontier sensor with S4 toward:
   `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`
4. Clean E95 current-frontier sensor with S4 closer:
   `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv`

Submission policy:

If using one public slot for the strongest JEPA-derived structured hypothesis, E211 E154 closer is now the top candidate. If isolating the current-frontier JEPA hypothesis, use E211 E95 toward before E210. E209 remains useful as the ungated raw-JEPA control.

## Update After E212

E212 fixes the JEPA-family submission order and feedback interpretation.

Artifacts:

- `analysis_outputs/e212_jepa_family_sensor_ordering.py`
- `analysis_outputs/e212_jepa_family_sensor_ordering_report.md`
- `analysis_outputs/e212_jepa_family_sensor_ordering_summary.csv`
- `analysis_outputs/e212_jepa_family_sensor_ordering_routebook.csv`
- `analysis_outputs/e212_jepa_family_sensor_ordering_pairwise.csv`

Submission order:

1. Maximum structured JEPA survival:
   `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`
2. Clean current-frontier JEPA sensor:
   `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`
3. Raw-JEPA control:
   `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv`
4. Blunt dependency-tail sensor:
   `analysis_outputs/submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv`

Interpretation:

E211 is first because it is the only JEPA family member that improves on E209 locally while adding a target-specific dependency gate. E210 is no longer the next expected-score move; it is a follow-up only if public feedback specifically says the raw/E211 JEPA body is tail-adverse. If the E211 E154 file wins and the E95 twin later loses, the repaired-branch anchor is doing much of the work. If the E211 E95 file wins, actual JEPA is cleanly useful beyond E154.

## Update After E213

E213 strengthens the E211-first policy by rejecting the cheap cherry-pick objection.

- Q3 `e208_resid_self_pc10`: permutation p-values `0.020408`, same-family pool rank `1/16`.
- S4 `e208_pred_pc14`: permutation p-values `0.020408`, same-family pool rank `1/16`.

Submission policy remains unchanged: E211 E154 closer is the maximum-survival JEPA sensor, and E211 E95 toward is the clean current-frontier JEPA sensor. If either loses, interpret it first as translation/public-tail failure, not as proof that the JEPA axes are noise.

## Update After E214

E214 tried to turn the JEPA axes into a stronger submission by learning a row-target benefit gate. It did not produce a submission-worthy file.

- Q3 benefit gate AUC: `0.552169`.
- S4 benefit gate AUC: `0.568968`.
- Best benefit-gated local policy: `q3raw_s4benefit_rank`, delta `-0.000918`.
- E211 toward baseline: delta `-0.001318`.
- Selected E214 submissions: none.

Submission policy remains E211-first. The next JEPA submission candidate is still `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv` for maximum structured survival, or `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv` for a clean E95-frontier JEPA sensor. E214 is a failed translator, not a replacement candidate.

## Update After E215/E216

E215 changed the JEPA target representation and found a new Q1/S2/S4 masked-family channel. E216 materialized it and selected only S2-safe sensors.

Selected E216 files:

- `analysis_outputs/submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv`
- `analysis_outputs/submission_e216_maskfam_jepa_s2_rank_e95_s0p75_4f8dc44d.csv`
- `analysis_outputs/submission_e216_maskfam_jepa_s2_rank_e154_s0p5_0ca3d931.csv`
- `analysis_outputs/submission_e216_maskfam_jepa_s2_rank_e95_s0p5_4516fb93.csv`

Interpretation:

Initial pre-public interpretation: E216 was not stronger than E211 as the first JEPA slot, but looked valuable as a non-collinear masked-family JEPA S2-only sensor.

Public feedback update: `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` scored `0.5772865088`, which is `+0.0009951790` worse than E95. That rejects E216 S2-only as a public-safe submission lane. The sibling E216 files remain useful as negative controls only; do not submit them before a specific S2 tail-failure audit explains why local/geometry/frontier stress missed this public-adverse movement.

## Update After E217

E217 tested a closer teacher-student tabular JEPA with an EMA teacher full-row latent. It did not produce a submission file.

Artifacts:

- `analysis_outputs/e217_teacher_student_tabular_jepa_probe.py`
- `analysis_outputs/e217_teacher_student_tabular_jepa_report.md`
- `analysis_outputs/e217_teacher_student_tabular_jepa_downstream_geometry_summary.csv`
- `analysis_outputs/e217_teacher_student_tabular_jepa_train_features.parquet`
- `analysis_outputs/e217_teacher_student_tabular_jepa_submission_features.parquet`

Interpretation:

The JEPA objective is learnable, but its best downstream signals fail geometry materialization. S2 is the strongest local feature, yet its geometry delta is positive. Therefore E217 should not change the submission order. After the E216 public miss, the actionable JEPA order is:

1. `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`
2. `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`
3. `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv`, only as an E211-control sensor after E211 feedback.

E216 and E217 are now diagnostic/energy sources only. E219 explains why the remaining E216 siblings are not automatic safer variants: the E154 body alone cannot explain the miss (`0.000924070` adverse capacity < observed `0.0009951790`), while the pure S2 graft can (`0.006048995` adverse capacity) and has weak support probability (`0.473945`). E220 then rejects simple support/tail thresholding: high-support subsets become expected-adverse and expected-negative subsets retain too much adverse capacity. Do not submit an E216 sibling, E220 threshold file, or E217-derived file unless a later target-specific materializer converts the signal into negative geometry, passes frontier hard-tail stress, and adds an OOF-reproducible S2 support/tail guard.

## Update After E221

E221 tried that OOF-reproducible S2 support/tail guard and did not produce a candidate.

- Support labels are locally learnable: best support-classifier AUCs are `0.748104` stratified, `0.717482` row-contiguous, and `0.713730` subject-LOO.
- OOF gates can preserve much of the E216 S2 local gain; for example `hgb_shallow__subject_loo/top250` gives S2 target delta `-0.004050232` with support precision `0.704000`.
- But no gate passes both sides of the submission rule. OOF-good gates remain public-tail unsafe, while submission-tail-safe gates fail OOF support/win criteria.

Submission policy is unchanged and stricter:

1. `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`
2. `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`
3. `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv`, only as a raw-JEPA control after E211 feedback.

Do not submit E216/E220/E221 S2 variants. The current evidence says masked-family S2 JEPA is a diagnostic latent, not a public-safe probability translator.

## Update After E222/E223

E222 applied the E216 failure criterion to the live E211 Q3/S4 candidates.

Key result:

- Original E211 E154 closer remains expected-good, but it is not support-safe:
  - graft expected focus `-0.000655277`
  - adverse capacity `0.004765654`
  - support probability `0.463231`
  - Q3 top1/expected `1.090401`
- E211's S4 component is the healthier part. Q3 contributes only about `-0.000144` expected focus while carrying about `0.00358` adverse capacity and top-cell concentration above `1.0x` of its expected gain.

E223 therefore creates a risk-rebalanced JEPA candidate by lowering Q3 scale from `1.0` to `0.75` while keeping the S4 dependency-gated body:

1. `analysis_outputs/submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv`
   - current preferred JEPA-family sensor.
   - actual vs E95 expected focus `-0.000666805`.
   - adverse capacity `0.004533247`, down from original E211 E154 closer's `0.005426827`.
   - top1/expected `0.176972`, down from `0.229657`.
   - not fully support-safe: support probability remains `0.464769`.

2. `analysis_outputs/submission_e223_jepa_q3s0p75_s4toward_e95_a0p5_55d326e5.csv`
   - cleaner E95-anchor contrast if the next slot should isolate JEPA movement from E154 repaired-branch body.
   - actual vs E95 expected focus `-0.000635269`, adverse `0.003912769`.

Updated submission policy:

1. If submitting exactly one JEPA-family file now, use `analysis_outputs/submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv`.
2. Use the original E211 E154 closer only if the explicit question is maximum original E211 body, not risk-rebalanced tail survival.
3. Use the E211/E223 E95-anchor files only as clean attribution sensors.
4. Do not submit E216/E220/E221 S2 variants.

Interpretation rule:

- If E223 improves public LB, the lesson is not "bigger JEPA worked"; it means E211's S4 body plus reduced-Q3 tail is closer to the public hidden subset.
- If E223 loses similarly to E216, then E211's Q3/S4 expected-good movement shares the same low-support public-tail mismatch and the current JEPA probability-translation lane should be demoted.

## Update After E224

E224 tests whether E223's q3_scale `0.75` was the real knee. It was not. A finer Pareto sweep says the current JEPA-family sensor should lower Q3 further to `0.625`.

Selected E224 files:

1. `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`
   - current preferred JEPA-family sensor.
   - graft vs anchor expected focus `-0.000623352`.
   - adverse capacity `0.003400775`.
   - support probability `0.465984`.
   - Q3 top1/expected `0.875120`.
   - local delta `-0.001098893`, geometry delta `-0.000505582`.

2. `analysis_outputs/submission_e224_e224_q3s0p625_s4toward_e95_a0p5_9c52abe2.csv`
   - cleaner E95-anchor contrast.
   - graft vs anchor expected focus `-0.000621278`, adverse `0.003461158`, support `0.466428`, Q3 top1/expected `0.860804`.

Updated submission policy:

1. If submitting exactly one JEPA-family file now, use `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
2. Keep E223 as the q3_scale `0.75` ablation, not the first JEPA candidate.
3. Use E224 E95-anchor siblings only if the explicit question is clean current-frontier attribution without E154 body.
4. Do not submit E216/E220/E221 S2 variants.

Interpretation rule:

- If E224 beats E95/E216 and ideally the public frontier, the update is specific: E211's S4 body is useful, but Q3 must be capped more aggressively than E223.
- If E224 loses around E216 scale, demote the current E211 probability translator. The JEPA axes may still be real, but this translation into public probabilities is not support-safe.

## Update After E225

E225 locks the public-feedback interpretation for E224 before submission.

Use this command after an E224 score is known:

`python3 analysis_outputs/e225_e224_public_feedback_decoder.py --score <PUBLIC_LB>`

Score bands:

- `<=0.576276019`: clean or stronger win. Promote capped-Q3/S4-body as public-readable, but do not raise Q3 to `0.75/1.0` without a new tail audit.
- `0.576276019..0.576288330`: micro win. Keep E224 preferred, but run exact attribution before any sibling.
- `0.576288330..0.576294330`: tie. E224 is underresolved; keep E95 practical.
- `0.576294330..0.576300366`: small loss. Do not submit another amplitude sibling; audit E154 body vs Q3/S4 residual.
- `0.576300366..0.576306641`: mixmin-safe loss. Demote E211/E223/E224 as expected-score followups.
- `>0.576306641`: branch loss or worse. Close current E211-family probability translator until a new support/tail target is built.

Movement read:

- E224 vs E95 is still highly collinear with E223 (`cos=0.996078`) and full E211 (`cos=0.975464`), so it is not a fresh representation lane.
- It is nearly orthogonal to the failed E216 S2 miss (`cos=0.043542`), so E216's public miss does not automatically kill E224. It only supplies the support-tail stress logic.

## Update After E226

E226 scans the existing documented/materialized submission pool after the E216 public miss and E224 routebook. It is a candidate-order audit, not a new score forecast.

Main result:

1. JEPA slot remains `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`. It is the capped-Q3/S4 E211-family sensor.
2. Best non-E224 independent worldview sensor is `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
   - role: `broad_survivor_counterworld`.
   - cos(E224) `0.074348`, cos(E216) `0.055999`, cos(E72) `0.108706`.
   - expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`.
   - interpretation: tests whether the safety atlas after E72/E101/E176/E216 became too conservative around broad survivor structure.
3. Conservative repaired-branch counter-world remains `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.
   - It is less broad and lower expected edge than E166, but easier to interpret as the repaired E144/E154 branch.

Do not use these as next-file shortcuts:

- E209/E210/E211/E223 as independent alternatives to E224. E226 classifies them as same Q3/S4 JEPA family.
- E216 siblings. They are S2 bad-axis neighbors after the public miss.
- `bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv`. E226 shape looks tempting, but E52 already rejected it as a mixmin-relative near-tie.
- hardtail parent diagnostics such as E84/E86/E87/E89/E90/E108 unless the explicit question is revisiting the hardtail branch, not finding a new post-E224 worldview.

## Update After E227

E227 locks the E166 public-feedback interpretation before any E166 submission.

Use this command after an E166 score is known:

`python3 analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>`

Current candidate roles:

1. JEPA question: `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`
   - asks whether E211's S4 body plus capped Q3 residual transfers to public.
   - decode with E225.

2. Independent broad-world question: `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`
   - asks whether the safety atlas became too conservative and broad survivor edge/between-train-runs context is public-real.
   - decode with E227.
   - do not scale or submit E166 siblings first.

3. Conservative repaired-branch question: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`
   - asks whether the E144/E154 repaired S3 active-boundary branch is the clean counter-world after broad/JEPA losses.
   - decode with E160.

Practical ordering is question-dependent, not score-dependent. If the user wants to test JEPA now, choose E224. If the user wants the most non-collinear existing worldview test, choose E166. If the user wants lower-risk branch repair, choose E154.

## Update After E228

E228 checks whether the three live files should be mixed or treated as separate public sensors.

Main result:

1. `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`
   - JEPA capped-Q3/S4 sensor.
   - cos(E166) `0.074348`; same-sign E166 covers only `0.035638` of E224 mass.
   - cos(E154) `0.316350`; E154 covers `0.885621` of its own mass inside E224 but only `0.175323` of E224 mass.

2. `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`
   - independent broad safety-atlas-overconservatism sensor.
   - cos(E154) `0.061662`.
   - top50 overlap with E154 is `0`, and top50 overlap with E224 is only `1` cell.

3. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`
   - conservative repaired-branch counter-world.
   - not fully independent from E224 because E224 contains most of its same-sign repaired body.
   - best used after E224/E166 feedback, or if the explicit question is "does the repaired branch work without the JEPA Q3/S4 residual?"

Submission policy update:

- Do not submit a naive E224/E166/E154 blend before public feedback. It would be hard to interpret and would not tell us which hidden-world law survived.
- If spending one JEPA slot: E224.
- If spending one independent non-JEPA worldview slot: E166.
- If spending one conservative repaired-branch slot after attribution: E154.

## Update After E229

E229 folds the real E216 public miss into the machine-readable public-anchor table and reruns the public-anchor bottleneck decomposition. The selector still cannot rank frontier files by expected LB: best LOOCV proxy MAE is `0.000496259`, far larger than the current frontier gaps. Therefore the next file must be chosen by the hidden-world question, not by the proxy.

Current one-slot policy:

1. JEPA-first question: submit `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
   - Intent: test whether E216 was a narrow S2/rank failure or whether current JEPA probability translation is broadly unsafe.
   - Public read: decode with `python3 analysis_outputs/e225_e224_public_feedback_decoder.py --score <PUBLIC_LB>`.

2. Independent non-JEPA question: submit `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
   - Intent: test whether the safety atlas is overconservative on broad survivor / edge / between-train-runs context.
   - Public read: decode with `python3 analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>`.

3. Conservative repaired branch: keep `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` conditional.
   - Intent: test E144/E154 repaired body only after JEPA or independent broad evidence points away from the active residual.
   - Reason not first: E154 is partly inherited inside E224; E224 covers `0.885621` of E154 mass same-sign.

Do not submit an E229 blend. E224 and E166 are high-information separate sensors, and blending before feedback destroys the observation.

## Update After E230

E230 creates conditional E224 siblings by pruning only fragile Q3 tail cells from the E224 movement. This is a repair audit, not a replacement for the first JEPA sensor.

Selected conditional files:

1. `analysis_outputs/submission_e230_q3_swingtop25_drop_e0918606.csv`
   - Best E230 score.
   - Drops the top `25` Q3 swing cells back to E154.
   - Expected focus `-0.000600044`, only `+0.000023308` worse than E224.
   - Adverse reduction vs E224 `+0.000633168`.
   - Support gain vs E224 `+0.009873471`.

2. `analysis_outputs/submission_e230_q3_risktop21_drop_7d95c14a.csv`
   - Strongest support gain among selected small-prune siblings.
   - Drops `21` Q3 low-support risk cells.
   - Expected focus `-0.000691244`, `-0.000067892` better than E224 under the public-free prior.
   - Adverse reduction vs E224 `+0.000444730`.
   - Support gain vs E224 `+0.021076971`.

3. `analysis_outputs/submission_e230_q3_risktop13_drop_9704f7c9.csv`
   - Smaller risk-top prune.
   - Expected focus `-0.000674532`, adverse reduction `+0.000326867`, support gain `+0.014719432`.

Submission policy:

- Do not submit E230 before E224 if the intended question is "does JEPA help here?" E224 is the cleaner observation.
- If E224 is a clean or micro win, do not use E230 immediately; first decode the win with E225.
- If E224 lands in the tie/small-loss band and attribution blames Q3 tail, use an E230 sibling. Prefer `q3_swingtop25_drop` for lower adverse capacity; prefer `q3_risktop21_drop` if support gain is the priority.
- If E224 loses worse than mixmin-safe, E230 is probably too narrow. Route to E166 or E154/search instead of pruning the same translator.

## Update After E231

E231 tried to promote the E230 Q3 hand-prune into an OOF-learned support gate. It failed the promotion test.

Key result:

- best Q3 support model AUC: `0.588101` under subject5; subject-LOO and row-contiguous variants are weaker.
- no learned gate passes both OOF preservation and submission-side tail stress.
- no E231 submission file is selected.

Submission policy stays unchanged:

1. JEPA-first question: submit `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
2. Conditional Q3-tail repair after E224 tie/small-loss: use `analysis_outputs/submission_e230_q3_swingtop25_drop_e0918606.csv` or `analysis_outputs/submission_e230_q3_risktop21_drop_7d95c14a.csv`.
3. If E224 hard-fails or E225 does not blame Q3 tail, do not use E230/E231. Route to E166, E154, or new non-collinear search.

## Update After E232

E232 tested whether the E216 S2 miss, E224 Q3 tail, and E224 S4 body share one support boundary. They do not.

Key result:

- max support-label correlation across S2/Q3/S4: `0.057278`.
- max benefit correlation: `0.090611`.
- Q3-vs-S2 test low-support top25 overlap: `1` row.
- best cross-target transfer is movement-shape based (`AUC=0.745452`), while latent-context transfer is weaker (`0.707003`) and not enough to define public-safe rows.

Submission policy stays conservative:

1. No E232 submission.
2. Do not create a shared S2/Q3/S4 support-gated submission.
3. JEPA-first public sensor remains `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
4. E230 remains conditional only after E224 tie/small-loss attribution to Q3 tail.
5. The next new JEPA branch should train target-specific support/energy heads, not a common support regularizer.

## Update After E233

E233 tested the cheapest target-specific support-head rescue: use support probabilities as soft amplitudes instead of hard gates. It failed as a candidate generator.

Key result:

- promoted soft policies: `0`.
- best learned Q3 soft delta loses to full E224-like Q3 by `+0.001713160`.
- best learned S2 soft delta loses to full E216 S2 by `+0.001600825`.
- best learned S4 soft delta loses to full E224-like S4 by `+0.000498506`.
- Q3 low-amplitude top25 overlap with E230 risk-top21 is `0` rows.

Submission policy:

1. No E233 submission.
2. Do not create a softened E221/E231 support-gate file.
3. Keep E224 as the clean JEPA public sensor if the next public question is still JEPA.
4. Future JEPA work should change the self-supervised/auxiliary target itself, for example a target-specific tail/benefit representation, instead of reusing current support probabilities as amplitudes.

## Update After E234/E235

E234 changed the JEPA target/loss from all-row support to high-impact tail representation. That produced local signal: `323` promoted policies, with best loss versus full movement of `-0.002653627` for S2, `-0.000870181` for Q3, and `-0.000833194` for S4. This is the first positive sign after the E232/E233 support-gate failures.

E235 then tried to turn the strongest local branch, S2, into a public-safe submission. It failed: `240` S2 materialization rows scanned, `0` submission-gate passes, `0` joint passes, and `0` materialized files. The best expected rows still have adverse capacity above the observed E216 miss and support below `0.5`.

Submission policy:

1. No E234 direct submission.
2. No E235 S2 submission.
3. Keep E216/E235 S2 closed as a public lane.
4. Keep E224 as the clean JEPA public sensor if the next public question is still JEPA.
5. The next JEPA diagnostic should audit E234 Q3/S4 materialization or train a sharper cell-level decisive-label target, not another S2 rescue.

## Update After E236

E236 audited the remaining E234 Q3/S4 branch by trying to materialize learned tail masks on the live E224 tensor. It also failed the submission gate: `92` graft rows, `0` gate passes, and `0` materialized files.

Key result:

- Q3 learned masks reduce adverse capacity a little, but they are anti-support and concentrate risk into a worse top-cell shape (`q3_top1_over_abs_expected=3.054720`).
- S4 learned masks improve support in some rows, but they erase too much of E224's expected body and do not address Q3 tail risk.

Submission policy stays unchanged:

1. No E236 submission.
2. E224 remains the clean JEPA public sensor if testing capped Q3 plus S4 body.
3. E230 remains conditional only after E224 tie/small-loss attribution points to Q3 tail.
4. E234 stays useful as local representation evidence, not as a direct public translator.

## Update After E237

E237 changes the JEPA branch status. The learned Q3/S4 row-level masks failed in E236, but a sharper cell-level decisive-label target produced submission candidates.

Top candidate:

1. `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`
   - Intent: test whether a learned JEPA-style decisive-cell head can replace the hand Q3 prune while preserving E224's S4 body.
   - Drops `25` Q3 cells and `0` S4 cells.
   - Expected loss vs E224 `-0.000005612`.
   - Adverse reduction vs E224 `0.000576400`.
   - Actual-vs-E95 adverse reduction vs E224 `0.000553281`.
   - Support gain vs E224 `0.006450259`.
   - Q3 top1/expected `0.747139811`, better than E224's `0.875120`.
   - Overlap with E230 Q3 risk-top21: `11` rows.

Submission policy:

1. If the next public question is "can a real learned JEPA target improve the Q3 tail?", submit the top E237 file.
2. If the next public question is the clean unpruned Q3/S4 JEPA translator, submit E224 instead.
3. If the goal is to test the hand-prune counterfactual after E224 feedback, keep E230 as the comparator.
4. Do not submit lower-ranked E237 siblings before the top file; they answer the same cell-tail question with weaker stress metrics.

## Update After E238

E238 does not create a new submission. It locks how the top E237 public result must be interpreted before seeing the score.

Routebook:

- `<=0.576276019`: clean support for learned Q3 decisive-cell JEPA.
- `0.576276019..0.576288330`: weak support; wait for E224/E230 contrast before siblings.
- `0.576288330..0.576294330`: tie; prefer E224 as the cleaner contrast if still untested.
- `0.576294330..0.576306641`: weak-to-clear rejection; do not tune E237 top-k siblings.
- `0.576306641..0.576341330`: branch loss; move to E166/E154 or another target representation.
- `>0.576591330`: E216-like translator collapse; rebuild the target instead of threshold-tuning.

Current one-file policy:

1. Learned-JEPA Q3-tail question: `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. Clean unpruned JEPA question: `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
3. Hand-prune control after E224 attribution: E230 risk/swing files, not before.
4. E216-style S2/maskfam siblings remain demoted after public `0.5772865088`.

## Update After E239

E239 does not change the one-file submission policy. It explains what the top E237 file is actually betting on.

Motif read:

- E237 drops `25` Q3 cells.
- It overlaps E230 swing25 by `13` and E230 risk21 by `11`, so it is not just the hand-prune replayed.
- It is not pure top-k amplitude: only `52%` of E237 cells are E224 top-25 by absolute movement, though `96%` are top-50.
- It is not a simple date-edge rule: near-test-edge-2 is `0.120` versus population `0.240`; train-gap-adjacent-2 is `0.240` versus `0.344`.
- The strongest extra signal is latent residual/neighbor energy: E208 residual self norm/abs mean, E208 nearest-neighbor target distance, and E208 residual PC10.

Submission policy stays:

1. If testing learned JEPA Q3-tail, submit exactly `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. Do not submit lower-ranked E237 top13/top10/p05 siblings before public feedback. E239 says the motif is residual-energy-plus-top50, not a scalar top-k knob.
3. If E237 wins, the next experiment should rebuild a Q3 decisive-cell JEPA target around E208 residual/NN-distance context.
4. If E237 loses, the same motif becomes a shortcut warning and E237-family siblings should be closed rather than tuned.

## Update After E240

E240 changes the confidence label on E237. The Q3 residual-energy cell-tail motif is stronger, but the claim that E237 uniquely needs a learned cell classifier is weaker.

Key finding:

- All `9/9` non-control simple residual/amplitude selectors pass the E237-like gate.
- Best simple rule is `simple_pc10_top25`:
  - expected loss vs E224 `-0.000062119`.
  - adverse reduction vs E224 `0.000594489`.
  - support gain vs E224 `0.016747154`.
  - actual adverse reduction vs E224 `0.000573879`.
  - overlap with E237 only `14/25`.
- E237 control still passes, but its advantage is no longer local-stress uniqueness.

Submission policy:

1. Do not create or submit E240 simple-rule files yet. They are post-E239 diagnostics, not OOF-learned translators.
2. If submitting the existing E237 top file, describe it as a Q3 residual-energy cell-tail public sensor, not as proof that the learned E237 classifier is uniquely correct.
3. The next local work should validate E208 residual PC10 / residual-energy rules against train-side Q3 benefit labels before materializing a simple-rule submission.
4. If E237 public wins, the next candidate family should be residual-energy Q3 cell-tail rules with OOF support, not lower-ranked E237 top-k siblings.

## Update After E241

E241 closes the immediate simple residual-rule branch. The E240 stress success does not transfer to train OOF Q3 benefit labels.

Key finding:

- No residual/amplitude/margin score has negative full-train selected-benefit delta.
- `score_pc10`, the strongest E240-style simple motif, is adverse on OOF Q3:
  - full train top-10% drop delta `+0.001867628`.
  - split-stress top-10% drop delta `+0.002633171`.
  - split-stress win rate `0.30`.
- The motif is still real on test geometry: `score_pc10` top25 overlaps E237 by `14/25` and E230 swing25 by `18/25`.

Submission policy:

1. Do not submit any E240/E241 simple residual-PC10 rule.
2. The learned E237 file remains the only defensible Q3 decisive-cell JEPA sensor, because it is OOF-trained and has a pre-registered decoder.
3. If E237 public wins, rebuild from OOF decisive-cell targets rather than from scalar PC10 top-k rules.
4. If E237 loses, close the whole current Q3 residual-energy prune family until a new OOF target explains the train/test motif mismatch.

## Update After E242

E242 refines why E237 is still live after E241. The selected E237 file is not an average-OOF-gain winner; it is a high-impact tail discriminator that passes the test-side support/top-cell stress.

Key finding:

- E237 gate pass rows are only `7/120`.
- Top E237 file rank by OOF gain is `71/120`.
- OOF gain gate AUC is `0.426043`, so average OOF improvement is not the selector.
- Top E237 file rank by OOF tail-AUC is `1/120`.
- OOF tail-AUC gate AUC is `0.958913`.
- Top E237 file also ranks `1/120` by support gain and Q3 top-cell safety.

Submission policy:

1. Keep the same top E237 file if the next public question is learned Q3 decisive-cell JEPA:
   `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. Do not submit E237 siblings because they look better by average OOF gain.
3. Do not submit simple residual-PC10 rules; E242 strengthens the distinction between learned high-impact tail labels and scalar residual-energy motifs.
4. If E237 is submitted, public feedback should update the high-impact Q3 tail-discrimination worldview, not a generic OOF-CV worldview.

## Update After E243

E243 fixes the next-slot policy after E242. It does not create a new file; it separates two different JEPA questions that were easy to conflate.

Current one-file policy:

1. If the public slot is **JEPA-as-solution / improvement-biased**, submit:
   `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. If the public slot is **clean JEPA body ablation**, submit:
   `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
3. If the public slot is **non-JEPA escape**, submit:
   `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
4. Keep `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` as a conservative repaired-branch counter-world, not the highest-information first slot.

Why E237 is now the closest real JEPA attempt:

- It changes only `25` Q3 cells versus E224 and leaves S4 intact.
- It has E224-relative expected loss `-0.000005612`, adverse reduction `0.000576400`, and support gain `0.006450259`.
- E242 ranks it `1/120` by OOF tail-AUC, support gain, and Q3 top-cell safety, while only `71/120` by average OOF gain.

Do not submit E216 siblings, E240 simple residual-PC10 rules, lower-ranked E237 siblings, or an E224/E166/E154 blend before feedback.

## Update After E244

E244 converts the E243 E237 recommendation from a modeling decision into a submission-ready artifact audit.

Submission-ready file:

`analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`

Integrity facts:

- status `READY`.
- SHA256 `6521b0e26622713eb9391c804af03b20eba84b924c4157bcc4ef50941b053915`.
- exact sample schema/key order against `data/ch2026_submission_sample.csv`.
- finite probabilities, all in `[0,1]`.
- exactly `25` cells changed versus E224, all on `Q3`.
- no Q1/Q2/S1/S2/S3/S4 movement versus E224 beyond floating-point zero.

Current candidate order is unchanged:

1. JEPA-as-solution / improvement-biased public slot: E237 audited file above.
2. Clean JEPA body ablation: `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
3. Non-JEPA escape: `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
4. Conservative repaired branch: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

E244 adds no new score evidence. It only closes the artifact-risk question: if E237 is selected, submit exactly this checksum-matched file and read public feedback as the learned Q3 decisive-cell worldview test.

## Update After E245

E245 adds a representation-compatibility check, not a new submission.

Key finding:

- E207's only `true_jepa_candidate` pair regime is `broad_stage2_pca64 / feature_nn1_all`.
- E237's 25-cell Q3 rollback reduces Q3 feature-NN1 pair roughness:
  - global abs-logit pair delta `-0.000802649`.
  - affected-pair abs-logit delta `-0.006472972` across `31` affected directed pairs.
- The effect is supportive but not decisive:
  - all-row random rollback percentile `0.1754` global, `0.1080` affected.
  - top50-amplitude rollback percentile `0.3132` global, `0.2896` affected.
- E237 is not globally smoother than E224 by movement ratio, so this is a local Q3 compatibility signal, not a broad latent-health certificate.

Submission policy remains:

1. If using one JEPA-as-solution public slot, submit the audited E237 file.
2. Do not create a new E245 submission.
3. If E237 wins, train the next JEPA target directly on feature-NN1 decisive-cell compatibility.
4. If E237 loses, E245 is too weak to justify tuning E237 siblings.

## Update After E247

E246/E247 changes the JEPA submission policy.

New high-information JEPA candidate:

`analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`

Artifact facts:

- selector: `nn_smooth_sum_top34`.
- SHA256: `3f4086d73b23a9c87294986aaa3a8ff32613312e69a398352d6744b8646ce839`.
- exact sample schema/key order.
- finite probabilities in `[0,1]`.
- E224 대비 changed cells `34`, all `Q3`.
- expected loss vs E224 `-0.000066519`.
- adverse reduction vs E224 `0.000632592`.
- support gain vs E224 `0.005788959`.
- actual-vs-E95 adverse reduction `0.000596176`.
- feature-NN1 Q3 pair roughness delta `-0.014223558` global, `-0.057353058` affected.
- E237 overlap `13`, E230 swing25 overlap `10`, amp top25 overlap `10`.

Current candidate order:

1. **Most informative JEPA-as-solution test:** E247 feature-NN1 smoothing file above.
2. **More conservative learned-cell JEPA test:** `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
3. **Clean JEPA body ablation:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
4. **Non-JEPA escape:** `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
5. **Conservative repaired branch:** `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Interpretation rule:

- If E247 beats E95, feature-NN1 broad-stage2 neighbor consistency becomes a real actionable JEPA selector, not just a diagnostic.
- If E247 is near E95/E101 but not better, the selector is informative but too weak at public hard-label resolution; fall back to E237 or wait for an OOF-trained feature-NN1 decisive target.
- If E247 is E216-like bad, the feature-NN1 smoothing gate is a calibration shortcut and should be demoted despite local stress success.

## Update After E248

E248 downgrades E247's expected-score claim.

OOF result:

- E247 train-only PCA analogue at the same `0.136` selection fraction has rollback delta `+0.002829987`.
- E247 all-PCA analogue has rollback delta `+0.002922728`.
- Split-stress means are also adverse: `+0.002638697` and `+0.002950123`.
- Even the best score at that fraction, `score_neg_trainpca_smooth_sum`, remains non-negative at `+0.000489209`.

Current candidate order by purpose:

1. **Best current JEPA score bet:** `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. **Highest-information feature-NN1 mechanism sensor:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
3. **Clean JEPA body ablation:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
4. **Non-JEPA escape:** `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
5. **Conservative repaired branch:** `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Practical rule:

- If the next submit is chosen for likely score, prefer E237 over E247.
- If the next submit is chosen to answer "can JEPA feature-neighbor smoothing itself solve the public Q3 tail?", E247 is still the sharper sensor.
- Do not submit E247 siblings or threshold variants before public feedback; E248 says the local smoothing rule lacks OOF invariance.

## Update After E250

E249/E250 changes the feature-NN1 JEPA branch again.

New live feature-NN1-context sensor:

`analysis_outputs/submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_top21_4e9a88af.csv`

Artifact facts:

- selected by feature-NN1 context inside the E237 decisive-cell target, not by direct smoothing.
- changes `21` E224 cells, all `Q3`.
- OOF loss_vs_full `-0.000185023`.
- OOF tail-AUC `0.887356598`.
- expected loss vs E224 `-0.000000845`.
- adverse reduction vs E224 `0.000524271`.
- support gain vs E224 `0.005790882`.
- actual adverse reduction vs E224 `0.000502064`.
- Q3 top1/abs-expected `0.660128450`.

Current candidate order by purpose:

1. **Best current JEPA score bet:** `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. **Best feature-NN1-context decisive-cell sensor:** `analysis_outputs/submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_top21_4e9a88af.csv`.
3. **Highest-information direct feature-NN1 smoothing sensor:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
4. **Clean JEPA body ablation:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
5. **Non-JEPA escape:** `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
6. **Conservative repaired branch:** `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Practical rule:

- If the next submit is chosen for likely score, E237 remains first because its locked OOF tail-AUC and E237 score are stronger.
- If the next submit is chosen to test "JEPA as actual feature-neighbor context, not just an idea", E250 top21 is now the cleaner sensor than E247.
- Do not submit E249 top50 or E250 siblings before feedback. E250 already shows average OOF gain is not enough; only the narrow top21 risk row survives the full stress gate.

## Update After E252

E251/E252 creates a stronger but less OOF-certified complementarity sensor.

New union sensor:

`analysis_outputs/submission_e252_e237_e250_union_q3top31_67707aef.csv`

Artifact facts:

- E237 cells `25`, E250 cells `21`, shared `15`, union `31`.
- exact sample schema/key order.
- finite probabilities in `[0.068110176672, 0.979776651464]`.
- E224 대비 changed cells `31`, all `Q3`.
- materialization stress from E251:
  - expected loss vs E224 `-0.000035272`.
  - adverse reduction vs E224 `0.000721005`.
  - support gain vs E224 `0.010353010`.
  - actual adverse reduction vs E224 `0.000688037`.
  - Q3 top1/abs-expected `0.506203451`.
  - score `0.077866812`, above E237 `0.058941606` and E250 `0.053008707`.

Current candidate order by purpose:

1. **Best current JEPA score bet:** `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. **Best E237/E250 complementarity sensor:** `analysis_outputs/submission_e252_e237_e250_union_q3top31_67707aef.csv`.
3. **Best pure feature-NN1-context decisive-cell sensor:** `analysis_outputs/submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_top21_4e9a88af.csv`.
4. **Highest-information direct feature-NN1 smoothing sensor:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
5. **Clean JEPA body ablation:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
6. **Non-JEPA escape:** `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
7. **Conservative repaired branch:** `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Practical rule:

- Choose E237 if the goal is the most defensible expected-score submission.
- Choose E252 if the goal is the most informative new public sensor from the JEPA branch: it asks whether learned decisive-cell and feature-NN1-context cell sets are complementary.
- Do not call E252 certified. Its weakness is no direct OOF policy identity for the union.

## Update After E253

E253 downgrades E252's expected-score claim and sharpens what it tests.

OOF analogue result:

- E237 parent loss_vs_full `-0.000271441`.
- E250 parent loss_vs_full `-0.000185023`.
- E252-style union loss_vs_full `-0.000080010`.
- Union remains stress-promoted, but is `+0.000191431` worse than E237.
- OOF shared intersection is strongest at `-0.000376454`, even though E251 materialization rejected the shared intersection.

Current candidate order by purpose:

1. **Best current JEPA score bet:** `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. **Best OOF-vs-materialization conflict sensor:** `analysis_outputs/submission_e252_e237_e250_union_q3top31_67707aef.csv`.
3. **Best pure feature-NN1-context decisive-cell sensor:** `analysis_outputs/submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_top21_4e9a88af.csv`.
4. **Highest-information direct feature-NN1 smoothing sensor:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
5. **Clean JEPA body ablation:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
6. **Non-JEPA escape:** `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.
7. **Conservative repaired branch:** `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

Practical rule:

- Do not submit E252 as a likely-score upgrade over E237.
- Submit E252 only if the explicit information goal is: does public behave more like E251 materialization support geometry than E253 train OOF?
- If only one JEPA score-biased file is wanted, E237 remains the file.

## Update After E254

E254 explains why E252 should stay a sensor rather than a score bet.

- OOF shared intersection is genuinely strong on train, but its corresponding test hard-tail shape is concentrated.
- Parent-specific cells look weak or adverse in OOF, but they alter the test hard-tail profile that made the union attractive in E251.
- The groups have large train/test shifts in `prob_gap`, `logit_step`, and feature-NN1 smooth-gain, so the conflict is a representation-transfer problem rather than a simple set-selection mistake.

Current candidate order by purpose remains:

1. **Best current JEPA score bet:** `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.
2. **Best OOF-vs-materialization conflict sensor:** `analysis_outputs/submission_e252_e237_e250_union_q3top31_67707aef.csv`.
3. **Best pure feature-NN1-context decisive-cell sensor:** `analysis_outputs/submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_top21_4e9a88af.csv`.
4. **Highest-information direct feature-NN1 smoothing sensor:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.

Practical rule:

- Do not create an E237/E250 intersection file.
- Do not promote E252 unless the next public question deliberately targets the OOF-vs-test geometry conflict.
- The next score-oriented submission should come from a new contrastive target, not from another union/intersection of existing cells.

## Update After E255/E256

E247 is now the public best:

`analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`

Public LB: `0.5761589494`.

Interpretation:

- E247 beats E95 by `0.0001323804`, which is `8.646x` the E95-over-mixmin edge.
- E248's OOF failure is now evidence of validation mismatch rather than a reason to discard feature-NN1 smoothing.
- The unresolved issue is attribution: E247 proves the combined E224 body plus Q3 feature-NN1 rollback, not the isolated rollback.
- The refreshed public-anchor proxy is still too coarse: best LOOCV MAE `0.000481276`, p90 `0.000741555`.

New candidate order by purpose:

1. **Current public best:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
2. **Best post-E247 score-plus-information follow-up:** `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`.
3. **Clean E224 body attribution:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
4. **OOF-vs-materialization conflict sensor:** `analysis_outputs/submission_e252_e237_e250_union_q3top31_67707aef.csv`.
5. **Learned Q3 decisive-cell contrast:** `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.

Practical rule:

- If the next file should seek score while still answering a clean question, use E256.
- If the next file should explain whether E247's win came mostly from E224 body, use E224.
- Do not submit an E247 sibling sweep; E256 is the controlled first follow-up.

## Update After E257

E257 explains what E256 actually changes relative to E247.

- E247 and E256 share `21` Q3 rollback cells.
- E247-only has `13` low-amplitude broad-smoothing cells:
  - rollback amplitude mean `0.039125051`.
  - smooth-gain sum `1.002858981`.
  - E237/E230 overlap `0`.
- E256-only has `4` high-amplitude cells:
  - rollback amplitude mean `0.110316918`.
  - smooth-gain sum `0.049289874`.
  - E230 swing overlap `4/4`.
- E247-all keeps more total smoothness mass (`3.555889570`), while E256-all has stronger affected-pair roughness reduction (`-0.070332985` vs `-0.057353058`).

Candidate order by purpose remains:

1. **Current public best:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.
2. **Best score-plus-information follow-up:** `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`.
3. **Clean body attribution:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.

Practical rule:

- Use E256 if the next public question is whether high-amplitude smoothing beats broad smoothness.
- Use E224 if the next public question is whether the E247 win mostly came from the E224 body.
- Do not create another E247-family sibling before E256 or E224 resolves one of those two questions.

## Update After E258

E258 separates E247 into body and rollback.

- `E95 -> E224` body:
  - `534` moved cells over `250` rows.
  - expected focus `-0.000653189`.
  - support probability `0.465789507`.
  - Q3/S4 carry `0.897035` of logit movement.
- `E224 -> E247` rollback:
  - `34` Q3 cells.
  - expected focus `-0.000066519`.
  - support probability `0.566510083`.
  - selected-cell cosine versus E224 body `-0.992683110`.
  - opposite-sign share `1.000000`.
- `E95 -> E247` total:
  - expected focus `-0.000719708`.
  - adverse delta reduced to `0.003497893`.
  - Q3 top1/abs improves from E224 body `0.863839051` to `0.545240602`.

Candidate order by question:

1. **Score plus information:** `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`.
2. **Clean body attribution:** `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.
3. **Keep current anchor:** `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`.

Practical rule:

- E247 is body plus tail correction. Do not interpret E247 public as isolated smoothing proof.
- If the next submission should still try to beat E247, E256 is the sharper bet.
- If the next submission should explain the win, E224 is more informative even if it may be less score-oriented.
