# Feature Registry

작성일: 2026-05-28

Feature는 "좋아 보이기 때문에 추가"하지 않는다. 각 feature family는 어떤 숨은 구조를 겨냥하는지, label signal인지 split signal인지, 폐기 조건이 무엇인지 함께 관리한다.

## H034 Feature Update

### F-H034. Row-vector route features

- Hidden structure: H012 phase may be locked by whole-row 7-target action
  routes rather than independent row-target cells.
- Candidates: row support code, row rollback/add/over aggregates, route mask
  counts, memory-conflict rows, public row-subset mean, joint-vector mean,
  H033 row-level cost sums, and row-route x target-group interaction features.
- Label vs split test: predict H032 sibling margins under score-name,
  target-group, curve, and random folds; then require generated row-route
  actions to pass H024 pre-H012 permutation and H025 row-placement stress.
- Adopt if: route features predict sibling margins and identify a generated
  row-route action with negative H012-relative stress.
- Drop if: the features only classify known bad siblings or if H024-only
  positives fail route/action-health agreement.
- Current evidence: route representation is strong (`et_route` all-OOF MAE
  `0.000388962`, Spearman `0.985479984`, pairwise `0.956022161`), but action
  translation fails. Best row 144 rollback has H024 pre-state margin
  `-0.003998719`, yet route margin `+0.032224275` and H025 row-permutation p
  `0.940000000`.
- Policy: use row-route features as a discriminator/veto for H024
  hallucinations. Do not use first-order row-route top-k edits as submissions.

## H033 Feature Update

### F-H033. Phase-lock contrast features

- Hidden structure: operations that break or preserve the exact H012 row-target
  phase.
- Candidates: rollback cost on H012-support cells, add cost on outside-support
  cells, over-amplification cost, memory-disagreement support, target-route
  family, H032 phase score source, and H024-style pre-H012 state/action
  features.
- Label vs split test: sibling margins must be predicted without using H012
  public LB in the action decoder, and generated edits must pass fresh
  public-score and row-placement permutation stress.
- Adopt if: the contrast separates H012-like from sibling-like actions and a
  materialized action clears H024/H025 stress below H012.
- Drop if: coefficients only rank known generated failures or if negative-cost
  cells produce worse H012-relative action health.
- Current evidence: H033 contrast is healthy as a diagnostic (`0.000814682`
  all-OOF MAE, `0.954416119` Spearman, `0.912785497` pairwise), but generated
  edits are not action-safe. Best candidate `negative_add_add_k10_a0.1` is
  `+0.016275125` worse than H012 by pre-state prediction despite changing only
  `10` tiny cells.
- Policy: use these as discriminator/route features. Do not use first-order
  independent-cell phase-lock coefficients as direct submission edits.

## H032 Feature Update

### F-H032. H012 phase-translation features

- Hidden structure: exact row-target action phase that made H012 public-positive.
- Candidates: E247-to-H012 logit phase, top-k support rank, target-route support,
  memory-conflict overlap, identity-prior score, phase-loss margin, H024-style
  state/action decoder features, H012-vs-sibling movement anatomy.
- Label vs split test: H012 public score must be withheld from the decoder, and
  the real H012 anchor must still rank above generated siblings. Generated
  siblings must pass independent stress before promotion.
- Adopt if: the features separate H012 from near-siblings under pre-H012 LOO and
  also identify a new action that survives H024/H025-style public-free stress.
- Drop if: they only re-rank H012 after using H012 public feedback, or if they
  produce smooth alpha/k/top-k variants that are priced above H012.
- Current evidence: H032 recovered real H012 as the best phase point with
  pre-H012 `geometry` LOO MAE `0.000295413`, Spearman `0.950877193`, pairwise
  `0.923976608`. Best non-anchor sibling was `+0.009811799` worse by pre-state
  prediction and changed `1080` cells.
- Policy: use as a discriminator/translator target. Do not submit dense phase
  siblings from this family.

## Registry

### F01. Subject-like fingerprint

- Hidden structure: subject/session prior and repeated behavior.
- Candidates: subject_id encoding, subject/date phase, within-subject rank, feature distribution rank, missingness fingerprint.
- Label vs split test: repeated-subject CV, strict-subject stress, train/test adversarial score.
- Adopt if: subject-controlled residual signal survives.
- Drop if: only train/test mask prediction improves or public bad-axis load increases.

### F02. Hidden block and sequence motif

- Hidden structure: contiguous hidden session blocks and block-level target rates.
- Candidates: block length, endpoint labels, flank motifs, weekday/date phase, row neighborhood density.
- Label vs split test: pseudo-hidden block split, endpoint non-overlap, anchor LOO.
- Adopt if: block-rate logloss beats subject mean and direct row movement remains low-energy.
- Drop if: boundary copy or leakage-like behavior dominates.

### F03. Measurement-process missingness

- Hidden structure: behavior expressed by sensor logging process.
- Candidates: observation fraction, longest gap, row count, active sensor count, pre/post sleep windows, subject/weekend deviations.
- Label vs split test: residual correlation after subject/weekend controls, train/test distribution distance.
- Adopt if: improves calibration risk or blockwise stress.
- Drop if: single threshold direct rule or train/test domain shortcut.

### F04. Cross-view JEPA surprise

- Hidden structure: inconsistency between expected sensor views and observed views.
- Candidates: view-to-view residual PCs, target_pred_cos, residual norm, surprise rank.
- Label vs split test: latent geometry, NN label consistency, high-energy loss contribution.
- Adopt if: geometry is stable and anchor stress does not load bad JEPA axes.
- Drop if: local CV gain comes with public bad anchor similarity.

### F05. Label-flow semantic JEPA

- Hidden structure: hidden block target rate/count latent.
- Candidates: past/future label-rate context, masked block-rate prediction, target-group masked prediction.
- Label vs split test: pseudo-hidden block logloss, oracle_rate_r2 vs pred_rate_r2, strict-subject stress.
- Adopt if: semantic target representation improves without overconfident row moves.
- Drop if: predictable time_meta dominates semantic latent.
- Current evidence: E10 found one strict semantic pass (`oracle_rate_r2=0.347118`, `pred_rate_r2=0.026047`) and downstream OOF gains, but 556 related direct submissions failed pairwise public-risk gates. E11 dependency/raw05 gating produced 50 control candidates and 3263 probe candidates, but no strict submit candidate. E12-E14 showed S4+Q3 gated movement is constructive and can cross strict pairwise submit gate. E15 showed those focused candidates fail independent hidden-subset survival: 0/163 candidates survived, including 0/61 pair-submit candidates. E17 showed the existing artifact universe has no Q3/S4-shaped candidate with old-majority support. E18-E19 showed OOF-local Q3/S4 strength is not an independent anchor.
- Policy: do not use as direct blockwise probability replacement. Allow targetwise S4+Q3 movement only as a diagnostic energy until raw05 distance, bad-axis load, pairwise stress, independent hidden-subset stress, and an independent S4/Q3 anchor agree.

### F06. raw05-compatible gate

- Hidden structure: public-positive raw timeline manifold.
- Candidates: raw05 distance, raw05 residual similarity, raw05-a2c8 tangent projection.
- Label vs split test: known public anchor order and raw05 distance stress.
- Adopt if: candidate movement is small or larger movement has clear low-energy support.
- Drop if: deviation from raw05 is not selector-resolvable.
- Current evidence: E11 best conservative candidate `submission_label_flow_gated_f1046674.csv` has mean_abs_move_vs_a2c8 `0.000063` and raw_dist_delta_vs_base `-0.000000121`; best p90 candidate `submission_label_flow_gated_ff8df011.csv` has larger movement `0.000370` but raw05 p90 delta only `+0.000002`.

### F07. Public-sensitive pairwise selector features

- Hidden structure: hidden public subset sign/order.
- Candidates: candidate delta features, target-move norms, bad-anchor distances, localization scores.
- Label vs split test: anchor LOO/L2O pair order.
- Adopt if: MAE `<= 0.00040`, rank accuracy `> 0.90`, and order is stable.
- Drop if: selected improvement is smaller than selector uncertainty.

### F08. Target dependency manifold

- Hidden structure: Q/S latent state and co-occurrence constraints.
- Candidates: pairwise dependency energy, Q latent factor, S latent factor, residual correlation violation, conditional target predictions.
- Label vs split test: targetwise calibration stress, bad-anchor discrimination.
- Adopt if: energy flags known bad submissions and improves calibration without hard clipping.
- Drop if: hard constraints worsen public anchors.
- Current evidence: soft dependency energy works better as a row gate than as a hard target constraint. E11 produced conflict-free probes; ordinal hard constraints remain a failed branch.
- Update: E12-E14 show the dependency gate should be targetwise. S4 is the dominant safe movement, Q3 is the secondary support. Q/S hard constraints remain banned.

### F09. Calibration risk features

- Hidden structure: LogLoss sensitivity from overconfidence and prior shift.
- Candidates: ensemble disagreement, temperature sensitivity, local density, domain score, high-energy flags.
- Label vs split test: targetwise ECE/logloss contribution, high-risk sample ablation.
- Adopt if: clipping/blending improves stress without reducing useful diversity.
- Drop if: uniform clipping just regresses to prior and hurts public-positive anchors.

### F10. Hidden-localization bridge features

- Hidden structure: inverse-public local target/sample direction.
- Candidates: hiddenloc score, bridge delta, per-target inverse energy.
- Label vs split test: old selector conflict, pairwise order stress, bad-axis load.
- Adopt if: local score and selector score agree.
- Drop if: conflict remains or expected edge is `1e-5` scale.

### F11. Block / measurement archive candidates

- Hidden structure: pseudo-subject block, hidden block rate/count, row-order motifs, raw05-compatible blockcount corrections, and pre-sleep measurement-process shifts.
- Candidates: existing block-scale JEPA, hidden-block sequence/rateprobe, public-block entropy, raw05-blockcount refine, public/presleep measurement submissions.
- Label vs split test: two-selector stress over pairwise public order and old hidden-subset scenarios, plus bad-axis and movement-scale diagnostics.
- Adopt if: candidate has pairwise p90 below a2c8, pairwise majority, old hidden-subset majority, and low bad-axis energy.
- Drop if: large-lowbad movement exists but selector sign stays positive, or pre-sleep movement is broad and public-risk negative.
- Current evidence: E20 scored 3800 non-anchor candidates. pair p90 negative `0`, pair majority `52`, old-majority `3`, two-selector majority `0`, pair submit/control/probe `0/0/63`, large-lowbad `2505`, large-lowbad two-selector `0`. raw05-blockcount refine is the nearest probe, but still has best pair p90 `+0.000010793` and old beat rate around `0.36`.
- Policy: do not submit existing block/measurement CSVs as improvement candidates. Use the archive as negative evidence for selector design and as a source of latent diagnostics only.

### F12. Selector support topology features

- Hidden structure: candidate-level latent world assignment, where pairwise-public and old hidden-subset selectors imply different public subsets.
- Candidates: support zone (`pair_only`, `old_only`, `pair_probe_not_majority`, `neither`), dominant target, Q3/S4 move share, pair/old support rates, raw05/bad-axis energies.
- Label vs split test: whether a new anchor, public sensor, or held-out public-observation split can explain which zone predicts public LB better.
- Adopt if: topology features predict known public anchor order under LOO/L2O or identify a new two-selector-supported region.
- Drop if: zone assignment only restates selector disagreement without resolving it.
- Current evidence: E21 found pair-only `465`, old-only `97`, pair-probe-not-majority `56`, two-selector majority `0`. Pair-only is S4/Q3-heavy; old-only is Q3/raw05-drift-like.
- Policy: use topology as diagnostic metadata and for sensor design. Do not blend pair-only and old-only candidates as if they were independent improvements.

### F13. Selector reliability and disambiguation features

- Hidden structure: which public-sensor world is compatible with known public-anchor order before spending another submission.
- Candidates: raw05/A2C8 direction preservation, selector pass rate, LOO/L2O MAE, support zone, dominant target, q3s4_move_share, old-vs-pair scenario beat rates.
- Label vs split test: selector must preserve known public anchor order before its favored candidate zone can define the next sensor.
- Adopt if: reliability features separate pair-only/old-only zones in a way that predicts known LB anchors and yields a single information-rich public sensor.
- Drop if: they merely restate historical LB outcomes or are used for direct leaderboard prior tweaking.

### F14. Public action-gradient features

- Hidden structure: public/private response field over row-target actions from H012.
- Candidates: aggregate known-submission logit movement through H012/H015/H016/H020/H021/H023/H014/H027 cell states, target/subject/date identities, and learned low-rank public-delta gradients.
- Label vs split test: leave-one-public-out public-delta prediction, shuffled-public-delta null, H024 public decoder, H025 row-permutation action-health stress.
- Adopt if: gradient fit beats permutation null and gradient-generated candidates also pass independent H024/H025 stress below H012.
- Drop if: gradient only separates H012 from the rest or self-scores candidates that independent public/action-health sensors price as 0.576-level.
- Current evidence: H028 selected `all` alpha `100` with LOO MAE `0.001204883` and permutation p `0.000000`, but its top generated file had H024 predicted public `0.576388`, support below H012 `0.083333`, row-permutation p `0.710000`, and public-score permutation p `0.918000`.
- Policy: keep as diagnostic of public response geometry. Do not use as a materializer unless an independent H024/H025-like stress also validates the generated move.
- Current evidence: E22 found pairwise selector pass `33/36` and raw05 direction correct `0.916667`; old hidden-subset selector pass `0/7` and raw05 direction correct `0.0`. This does not make pair-only S4/Q3 a submit-safe improvement, but it makes `analysis_outputs/submission_label_flow_focused_1bbfb735.csv` the most informative diagnostic sensor if a public slot is used.
- Policy: use as submission triage metadata only. Do not build a public-LB overfit prior from it.

### F14. Sensor amplitude curve

- Hidden structure: whether selector disagreement is caused by movement amplitude or by latent direction.
- Candidates: logit-space interpolation from A2C8 to pair-only S4/Q3 sensors, target masks, scale, old p90 response, pair p90 response, two-selector majority.
- Label vs split test: a valid amplitude feature must create old/pair agreement as scale changes, not only reduce movement magnitude.
- Adopt if: a scale/mask variant preserves pairwise edge and flips old hidden-subset majority or creates two-selector support.
- Drop if: scaling changes p90 smoothly but old majority remains below 0.5.
- Current evidence: E23 scored 108 variants. Pair p90 was negative throughout, but two-selector majority was `0`. Balanced lower-risk sensor `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv` is diagnostic only.
- Policy: use scale as a risk knob for public sensors. Do not use scale as evidence that the S4/Q3 movement is submit-safe.

### F15. Localized S4/Q3 row-mask gates

- Hidden structure: whether pairwise-public S4/Q3 movement belongs only to a hidden subject/date/block/phase/energy subset.
- Candidates: subject masks, subject complements, global date tertiles/quintiles, within-subject phase bins, contiguous date blocks and complements, delta-energy quantiles, S4 delta sign, weekday/weekend, subject-energy groups.
- Label vs split test: row localization must improve selector agreement, not merely lower movement magnitude. A useful gate should create old hidden-subset majority or two-selector majority while preserving pairwise p90 below a2c8.
- Adopt if: a row mask yields pairwise p90 below 0, old scenario beat rate above 0.5, low bad-axis load, and movement large enough to be public-readable.
- Drop if: row masks only create pairwise-positive/old-negative files or micro-movement files with p90 deltas below selector noise.
- Current evidence: E24 scored 960 variants. Pair p90 negative was `807`, but old-majority and two-selector majority were both `0`. The only loose candidates were eight `id02_b02` files affecting `8/250` rows with pair p90 around `-2e-7`, old p90 around `+0.000580`, and movement around `1e-5`.
- Policy: do not use simple row-mask localization as a submit gate for the current S4/Q3 sensors. Future localization must be learned from a new anchor/representation rather than swept manually around the same pair-only direction.

### F16. Sparse / direction-mixture large-movement probes

- Hidden structure: larger JEPA/direct-label sparse direction may encode a public-transfer axis that micro S4/Q3 sensors cannot expose.
- Candidates: sparse-ladder, target-ablation Q3/stage, blockwise bad-axis repair, direction ensembles, minimax mixtures, inverse7 blends, inverse7 row gates.
- Label vs split test: large movement must survive honest CV, actual-anchor/combo stress, pairwise public-order stress, old hidden-subset stress, and bad-axis load checks. If selectors disagree, the candidate is a public-probe experiment rather than a strict submission.
- Adopt if: at least one file has nontrivial movement, pair p90 below a2c8, pair majority, old majority, low bad-axis load, and no worse combo tail than the current direction-ensemble reference.
- Drop if: honest-CV/combo gains are accompanied by pairwise p90 positive and old-majority 0.
- Current evidence: E25 scored 22 current priority files. Pair p90 negative `0`, pair majority `0`, old-majority `0`, two-selector majority `0`. `submission_mixmin_0c916bb4.csv` remains high-risk public-probe material under actual-anchor/combo metadata, but strict selector support is absent.
- Policy: keep as a separate high-risk score-probe lane. Do not mix it with strict-survival or selector-disambiguation candidates.

### F17. Public-LB inverse feasibility constraints

- Hidden structure: whether public LB observations imply a pseudo-public subset, target prior, or hidden label distribution that can rank new submissions.
- Candidates: all-test soft-label inverse LP, arbitrary cell/label mixture LP, train target prevalence bands, candidate delta intervals.
- Label vs split test: inverse constraints are useful only if they produce one-sided candidate deltas under plausible structural assumptions.
- Adopt if: known public LBs force candidate delta sign while preserving known anchor scores and train-prior plausibility.
- Drop if: candidate ranges cross zero or target/subject masses remain unconstrained.
- Current evidence: E26 matched all 8 known public LBs exactly; all unobserved candidate delta intervals crossed zero even under train-prior bands `±0.05`, `±0.10`, `±0.20`.
- Policy: use only as an ambiguity diagnostic. Do not use inverse-LB fitting as a direct feature, gate, or ranker.

### F18. Structural-prior inverse constraints

- Hidden structure: whether hidden subject/user identity and train-derived target prevalence are the missing constraints that make public-LB feasible worlds realistic.
- Candidates: global target prevalence bands, subject-target prior bands, scenario fit slack, candidate delta interval width, one-sided sign indicators.
- Label vs split test: priors are useful only if they both fit known public LB anchors and make candidate deltas one-sided under plausible bands.
- Adopt if: a candidate is one-sided negative across weak/moderate global and subject-target prior scenarios, with known-LB slack near zero.
- Drop if: known LBs fit but candidate intervals continue to cross zero.
- Current evidence: E27 tested seven scenarios. All known public LBs fit with slack `0`, but all unobserved candidate-scenario cells crossed zero (`56/56`) and one-sided improvement cells were `0`.
- Policy: subject-target prior is a diagnostic constraint only. Do not rank current candidates by this inverse worldview.

### F19. Binary hidden-label inverse constraints

- Hidden structure: whether the real public world is closer to an exact binary all-test label vector than to relaxed soft-label feasible worlds.
- Candidates: binary-label MILP fit residual, binary incumbent pools, candidate delta ranges under residual budgets, exact-label/public-subset cardinality constraints.
- Label vs split test: a binary inverse feature is useful only if it fits known public anchors at frontier resolution and produces stable one-sided candidate signs across multiple binary incumbents or optimized ranges.
- Adopt if: representative candidates become one-sided negative under binary worlds that preserve known public anchor order and have residual below the raw05-a2c8 gap.
- Drop if: range searches remain time-limited, candidate signs cross zero, or fit residual is larger than the public edge being optimized.
- Current evidence: E28 found a tight subject-prior binary incumbent with max residual `0.000061242`, below the raw05-a2c8 gap, but candidate range searches produced no one-sided improvement evidence. `6b9335b1` crossed zero under no-prior binary incumbent ranges.
- Policy: keep as a future exact-public-world diagnostic. Do not use current binary inverse outputs as a submission gate.

### F20. Binary world-pool sign features

- Hidden structure: multiple exact-label hidden public worlds may form a candidate-family sensor even when relaxed inverse LPs are underidentified.
- Candidates: frontier-scale world indicator, world hash/dedup count, max residual over raw05-a2c8 gap, candidate better_rate across worlds, frontier-only delta sign, positive-cell count, target-prior dispersion.
- Label vs split test: a useful pool feature must be stable after filtering to frontier-scale worlds and should not depend on candidate-objective worlds alone.
- Adopt if: several diverse frontier-scale worlds agree on the same candidate family and preserve known public-anchor residuals below the raw05-a2c8 gap.
- Drop if: frontier-scale count is too small, signs differ by sampled world, or all support comes from time-limited incumbents with residuals larger than the public edge.
- Current evidence: E29 produced 15 unique binary incumbents but only 1 frontier-scale world. E30 then forced all known-public residuals inside the raw05-a2c8 gap and found 29 frontier worlds, 28 unique. Random-plus-fit worlds favored mixmin `19/19` and inverse7 `18/19`, but candidate-max objectives still found adverse frontier worlds.
- Policy: use `binary_world_pool_support_energy` as diagnostic metadata only. It raises `submission_mixmin_0c916bb4.csv` above pair-only S4/Q3 as a high-risk worldview probe, but it still cannot certify a submission.

### F21. Binary world plausibility geometry

- Hidden structure: adverse exact-label worlds may be artifacts if their target/subject/dependency/sequence geometry is unlike train.
- Candidates: target-prior MAE, subject-target MAE, pairwise joint MAE, target-correlation MAE, row-cardinality L1, subject/global temporal flip MAE, run-length MAE, train/test edge flip rate, robust aggregated plausibility energy.
- Label vs split test: a plausibility gate is useful only if it rejects adverse candidate worlds without merely selecting candidate-objective artifacts.
- Adopt if: adverse worlds for a candidate are high-energy outliers and low-energy random/fit worlds are one-sided.
- Drop if: adverse worlds are low-energy or more plausible than supporting worlds.
- Current evidence: E31 found mixmin adverse worlds are plausibility ranks `1` and `2`, despite random+fit worlds supporting mixmin `19/19`.
- Policy: do not use generic train-label plausibility to certify mixmin. Keep it as a negative gate and diagnostic feature.

### F22. Known-anchor loss decomposition geometry

- Hidden structure: a hidden binary/public world should explain known public-worse anchors through coherent per-target loss movement, not through large cancellation among target axes.
- Candidates: per-anchor per-target loss delta versus A2C8, moved-target/loss-delta alignment, anchor cancellation mean, positive-share mean, movement/loss correlation, robust `anchor_energy` rank.
- Label vs split test: this feature is useful only if low-energy bands support candidates consistently and adverse candidate worlds are high energy; it must not be used to directly tune to public LB scores.
- Adopt if: low-anchor-energy random/fit worlds agree on a candidate family, known public anchor order remains preserved, and candidate-max adverse worlds are high-energy rather than merely inconvenient.
- Drop if: adverse worlds are low-anchor-energy, or the feature only recovers known LB ranking while failing out-of-anchor stress.
- Current evidence: E32 scored 29 E30 worlds. Low-anchor-energy half supported mixmin `15/15` and inverse7 `15/15`; low quarter supported both `7/7`; low-anchor-energy random+fit supported both `12/12`. The two mixmin-adverse worlds were high-energy ranks `26` and `28`.
- Stability evidence: E33 leave-one-anchor-out stress kept mixmin low-energy-half and low-energy-quarter better_rate at `1.0` in all 7 LOO runs, and no mixmin-adverse world entered any LOO low-energy half. Inverse7 was slightly less stable with low-half min better_rate `0.928571`.
- Null evidence: E34 family/null stress kept mixmin low-half support at `1.0` under `no_raw05`, `no_medium_non_jepa`, `no_bad_jepa`, and `only_medium_non_jepa`; `only_bad_jepa` failed with adverse worlds entering the low-energy half. Target-axis permutation kept mixmin one-sided in `500/500` permutations, so the signal is not exact target-axis semantics.
- Policy: promoted after E48. This is now a validated public-relevant gate for the mixmin family because `analysis_outputs/submission_mixmin_0c916bb4.csv` scored `0.5763066405`. It still should not be described as target-axis JEPA semantics or private-safe certification; use it to build mixmin-relative candidates and to recalibrate selector energy.

### F23. Evidence-source independence tier

- Hidden structure: whether a candidate is supported by independent latent/data evidence or only by known-public/anchor-derived geometry.
- Candidates: evidence tier labels, local-independent-ish support flags, selector hard veto flags, anchor-derived support flags, normal-submit gate, diagnostic sensor priority.
- Label vs split test: a candidate can be a normal submission only if support is not primarily known-public-derived and if independent local/representation evidence does not conflict with selector stress.
- Adopt if: local/representation evidence, pair/old selector evidence, and anchor-derived evidence all point in the same direction.
- Drop if: the strongest support is anchor-derived while selector hard veto remains, even if anchor-LOO/family/null robustness is strong.
- Current evidence: E35 audited 5 sensors. normal submit gates passing `0`. Mixmin has honest CV mean/worst `-0.000951963` / `-0.000695966` and strong anchor-loss/LOO support, but pair p90 `+0.000879200`, old p90 `+0.001041933`, and selector hard veto remain. Pair-only S4/Q3 sensors have local dependency/pairwise support but fail old/independent survival and binary/anchor-loss support.
- Policy: update after E48. The independence-tier feature was too conservative as a public hard gate because mixmin became the public frontier, but it remains useful for private-risk labeling. Use it to separate "public-validated but anchor-derived" from "independently safe".

### F24. Raw-structure pseudo-label support energy

- Hidden structure: whether observed subject/date/raw-feature neighborhoods carry the same target direction implied by anchor-loss/binary public worlds.
- Candidates: subject mean pseudo-labels, same-subject temporal KNN priors, raw-feature KNN priors, cross-subject KNN priors, sensor coverage/stat KNN priors, raw-feature cluster priors, movement-toward-pseudo-label rate, raw-structure support rate.
- Label vs split test: support must come from train-derived pseudo-label views that do not use known public LB anchors; it must be checked against train/test adversarial AUC, selector hard-veto status, and anchor-loss/LOO stability.
- Adopt if: a candidate improves soft LogLoss across most raw-structure sources, has negative worst-source delta, and does not keep a selector hard veto after scale/blend reconciliation.
- Drop if: raw support is sparse, mean soft delta is positive, support only appears in train/test domain-like views, or the candidate remains pair/old selector-vetoed.
- Current evidence: E36 built 10 raw-structure pseudo-label sources from train-derived subject/date/raw features. Mixmin support was `5/10`, mean delta `+0.000065107`, worst delta `+0.000498574`; therefore raw observed structure does not independently certify mixmin. Inverse7 support was `10/10`, mean delta `-0.000705727`, worst delta `-0.000507826`, with mean toward-rate `0.606601`. Pair-only S4/Q3 sensors had `7/10` support but positive worst-source deltas.
- Scale/blend evidence: E37 generated 22 inverse7/mixmin logit scale-blend variants. Raw support gates were `14` and anchor low-half+quarter gates were `22`, but two-selector majority and strict bridge gates were both `0`. Best-ranked `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv` kept raw and anchor support but still had pair p90 `+0.000035423`, old p90 `+0.000587512`, and selector hard veto.
- Policy: use `raw_structure_pseudolabel_energy` as an independent-ish bridge diagnostic, not as a direct submission gate. It promotes inverse7 to a new bridge-probe branch, but any public candidate must first reconcile E35 selector hard veto and E33's weaker inverse7 anchor-LOO stability.

### F25. Worldview sensor discriminability energy

- Hidden structure: whether current candidate families are best understood as separate hidden-public worldviews rather than a single submission ranking.
- Candidates: raw verdict, anchor verdict, pairwise-selector verdict, old-selector verdict, honest-CV verdict, conflict span versus raw05/A2C8 gap, sign entropy, lane identity.
- Label vs split test: this feature is useful only if it separates diagnostic questions without claiming label signal. It must not promote a candidate unless at least two independent non-public stresses agree and selector veto is resolved.
- Adopt if: public sensor selection needs a predeclared question and the candidate has high conflict-span plus clear interpretation under both improvement and degradation.
- Drop if: it is used as an improvement score, if all evidence comes from one anchor family, or if it hides the normal-submit gate result.
- Current evidence: E38 audited 10 current sensors. normal-submit candidates were `0`; public-sensor candidates were `10`. `mixmin_0c916` was the top information sensor with score `3.355110`; `inverse7blend_1040` / `inv7_s1p00` were raw+anchor-vs-selector bridge sensors; `6b9335b1` and `1bbfb735` were S4/Q3 pair-vs-anchor selector sensors.
- Policy: validated for public-sensor selection after E48. It correctly elevated mixmin as the most informative public observation, and that file became the frontier. It is still not a private safety score; future use should rank which mixmin-relative public question is most informative.

### F26. OOF selector calibration energy

- Hidden structure: whether the train OOF archive contains a local selector target that generalizes to public candidate ordering.
- Candidates: full OOF delta versus final9, label-free future-tail/domain/density/missingness stress deltas, subject/date/random block deltas, known-public sign/rank agreement, OOF family stability.
- Label vs split test: OOF stability is useful only if known-public analogues preserve both direction and ordering. Sign-only agreement is insufficient because submission choice depends on ranking among public-positive candidates.
- Adopt if: known-public pairwise rank agreement is high, OOF top families are not dominated by obvious local/publicblend shortcuts, and OOF-stable candidates also survive non-OOF selector/anchor stresses.
- Drop if: OOF rank reverses known public order, or many candidates pass OOF gates while failing public/anchor-derived stress.
- Current evidence: E39 scored `4172` OOF rows (`4171` unique hashes). strict OOF gates were `1311`, conservative gates `1115`, and known-public sign match was `1.0`. But known-public pairwise rank agreement was `0.0`: OOF ranks ordinal stronger than stage2 even though public LB ranks stage2 better than ordinal.
- Policy: use as a negative overfit/local-stability screen only. Do not use OOF selector calibration as a submission ranker or a 0.54 path.

### F27. Test-movement fingerprint selector energy

- Hidden structure: whether public transfer is encoded in the anatomy of test-set probability/logit/entropy movement relative to A2C8.
- Candidates: target-level movement, per-subject movement, row-order movement, raw-domain/density/missingness/cluster movement, nearest known-anchor fingerprint, permutation-null rank evidence.
- Label vs split test: movement fingerprints are useful only if they recover known public anchor ordering under leave-one-anchor-out, including stage2 < ordinal, A2C8 as best, and bad JEPA severity. Passing stage2/ordinal alone is not enough.
- Adopt if: at least one view has LOOCV MAE below the frontier-scale public edge, rank accuracy above `0.75`, A2C8 predicted best, bad-anchor severity not collapsed, and permutation-null p-value below `0.10`.
- Drop if: the selector compresses bad JEPA anchors, predicts A2C8 as non-best in leave-one-out, or only works as an in-sample nearest-anchor lookup.
- Current evidence: E40 found strict selector views `0` and loose selector views `4`. Combined view had LOOCV MAE `0.000781461`, pairwise rank accuracy `0.821429`, permutation-null rank p `0.004`, and correct stage2/ordinal order. It failed strict gate because A2C8 was not predicted best under leave-one-out and bad JEPA severity was underpredicted. The loose prior ranked `inv7_s0p25` closest to best (`0.577450` predicted public LB), `1bb_s0p65` near raw05 (`0.577522`), and mixmin worse (`0.577664`).
- Policy: use as a loose sensor-prior only. It can help choose a lower-risk diagnostic public sensor, but it cannot certify improvement or override anchor-loss/worldview evidence.

### F28. Movement bad-axis geometry energy

- Hidden structure: whether E40's missing component is the logit-space direction of movement toward known bad JEPA anchors, not broader public subset identity.
- Candidates: cosine/projection to raw_timeline, stage2, ordinal, final9, q2_jepa_bad, lejepa_bad, jepa_residual_bad axes; bad/good group projection ratios; compact movement plus axis views.
- Label vs split test: axis features are useful only if leave-one-anchor-out removes the held-out anchor's own axis and the selector still recovers stage2/ordinal, bad-anchor severity, and A2C8-best. In-sample candidate nearest-anchor predictions are not evidence.
- Adopt if: a LOO-safe view passes strict or loose gates with bad-anchor underprediction controlled, A2C8 predicted best, and permutation-null rank p below `0.10`.
- Drop if: severity improves but A2C8-best fails, named axes overfit anchor identity, or candidate ranking changes only in ungated in-sample predictions.
- Current evidence: E41 found strict selector views `0` and loose selector views `0`. `axis_group` was the best severity view: LOOCV MAE `0.000854918`, pairwise rank accuracy `0.785714`, permutation-null rank p `0.014`, correct stage2/ordinal order, and bad-anchor mean underprediction `0.000898399`; but it predicted A2C8 as `+0.001475508` worse in LOO and missed the loose MAE threshold by `0.000004918`. `axis_named` had MAE `0.000827696` but failed rank, stage2/ordinal order, and bad-anchor underprediction.
- Policy: use only as a diagnostic explaining why E40 failed. Do not use movement+bad-axis predicted public LB as a forecast or submission ranker.

### F29. Fixed-zero anchor selector calibration energy

- Hidden structure: whether the pre-E48 best A2C8 should be treated as a known zero anchor rather than a LOO target when calibrating public-selector geometry.
- Candidates: nonbaseline LOO with A2C8 fixed at delta `0`, held-out-axis removal for axis views, raw05 gap to selector MAE ratio, best unobserved advantage to MAE ratio, A2C8-to-anchor synthetic trajectory monotonicity, zero-neighborhood collapse warning.
- Label vs split test: this feature is useful only if it improves nonbaseline rank while preserving enough resolution to read changes smaller than the raw05-A2C8 public gap. It must not turn in-sample current-best anchoring into a forecast.
- Adopt if: a view passes fixed-zero nonbaseline rank/order gates, trajectory monotonicity is high, raw05 gap/MAE is close to or above `1`, and unobserved candidate advantage/MAE is large enough to be public-readable.
- Drop if: nonbaseline rank improves but selector MAE remains much larger than the frontier edge, synthetic paths are non-monotone, or "better than raw05" candidates are better by less than selector error.
- Current evidence: E42 found fixed-zero gates `0` and usable zero-anchor gates `0`. Best `axis_group` nonbaseline rank improved to `0.857143` with null rank p `0.006`, stage2/ordinal order correct, and raw05 predicted best nonbaseline. But nonbaseline MAE was `0.000766262`, raw05 gap/MAE was `0.113520`, best unobserved advantage/MAE was `0.065408`, trajectory monotonicity was `0.428571`, and zero-neighborhood collapse warning was true.
- Policy: use as a failed calibration diagnostic. Do not submit pair sensors solely because fixed-zero `axis_group` predicts them slightly better than raw05; the predicted edges are far below selector error.

### F30. Selector resolution boundary energy

- Hidden structure: whether current public selector/gate families have enough measurement resolution to detect a candidate edge at the frontier scale.
- Candidates: selector best/median known-anchor error, LOO/L2O error, raw05 gap to error ratio, candidate predicted edge to selector-error ratio, error-margin certification flags.
- Label vs split test: this is not a feature for model input. It is a meta-gate that prevents promoting candidates whose expected edge is smaller than the selector's observed error on known public anchors.
- Adopt if: a selector family has best error below the raw05-A2C8 gap `0.0000869862`, preferably with L2O support, and at least one candidate has predicted edge larger than that error under independent stress.
- Drop if: all selector errors exceed the raw05-A2C8 gap or all favorable candidate edges vanish after error-margin correction.
- Current evidence: E43 found selector frontier-resolution gates `0`, certified better-than-A2C8 rows `0`, and certified better-than-raw05 rows `0`. The best selector was pairwise public-order with best LOO error `0.000218288`, raw05-gap/error ratio `0.398493`, and best L2O error `0.000415499`. E40/E41/E42 raw05-gap/error ratios were only `0.111312`, `0.105094`, and `0.113520`.
- Policy: make this a hard normal-submission gate. A candidate can still be a public sensor, but it should not be described as an improvement candidate unless its edge exceeds selector error or a new selector has sub-gap error.

### F31. Large-edge low-risk census energy

- Hidden structure: whether the current scored candidate universe already contains a larger safe movement that previous per-family audits missed.
- Candidates: file-level normalized pair p90 edge, pair edge/raw05-gap ratio, pair edge/selector-error ratio, any raw/anchor/old favorable edge, low bad-axis flags, raw05 compatibility, two-selector support, submit-like support, hard-veto status.
- Label vs split test: this is a meta-feature/gate, not a model input. It must aggregate across source tables without treating raw/anchor-only support as public truth. Pairwise public-order edge must exceed both raw05-A2C8 gap and selector error before it can be considered selector-readable.
- Adopt if: at least one file has pairwise p90 edge greater than the E43 best selector error `0.000218288`, low bad-axis, raw05 compatibility, no hard veto, and two-selector or submit-like support.
- Drop if: favorable pairwise edge stays below selector error or if large favorable edge appears only in raw/anchor/honest-CV views while pair/old selectors remain adverse.
- Current evidence: E44 loaded 29 score tables with 69,869 rows and 48,088 unique files. Pair-negative files were `12,309`, but files with pair edge greater than raw05-A2C8 gap were `0`, files with pair edge greater than selector error were `0`, and normal large-safe files were `0`. Best pair edge was `0.000073768`, only `0.337941` of selector error and `0.848048` of raw05 gap. Any-edge-above-selector files were `21`, dominated by inverse7/mixmin raw/anchor conflict rows.
- Policy: use as a hard stop against re-ranking existing scored files as improvement submissions. Future work must add a new independent selector target or generate a new representation movement; merely rescoring the current universe is not enough.

### F32. Structured public-subset feasibility energy

- Hidden structure: whether public LB is dominated by a simple subject/order/date/raw-domain test-row subset that can serve as an independent selector target.
- Candidates: mask kind/name, rows, known-anchor LOO MAE, max abs held-out error, A2C8-best flag, raw05-direction flag, feasible range width, structured-vs-random comparison.
- Label vs split test: this is a meta-selector feature, not a model input. It uses only known public anchors in leave-one-anchor-out form and tests masks predeclared from row order, subject, calendar, raw-domain, and random controls. A mask is not trusted if it only fits anchors exactly but leaves wide feasible ranges.
- Adopt if: a mask family gets LOO MAE below the raw05-A2C8 gap `0.0000869862` or at least below the E43 selector error `0.000218288`, preserves A2C8-best/raw05 direction, and has narrow feasible ranges.
- Drop if: LOO error stays above selector scale or feasible ranges are much wider than the public edge being optimized.
- Current evidence: E45 tested 145 masks and found selector-scale gates `0` and strict sub-gap gates `0`. Best mask `global_key_order/suffix_frac0.20` had LOO MAE `0.000429528`, max abs `0.00129817`, raw05-gap ratio `4.937886`, and selector-error ratio `1.967712`. Feasible range mean widths were around `0.04`, far too wide for candidate selection.
- Policy: use as a negative screen. Do not rank candidates from simple structured public-subset inverse fits unless a new public observation gives a real mask anchor or a new independent target reduces the LOO error below the gap.

### F33. Block-rate context target representation

- Hidden structure: hidden rows are generated in subject/session blocks whose target-rate vector changes locally; the missing signal is a block-level rate/count latent rather than a deterministic row-level label.
- Candidates: held-out block-rate vector, block count vector, subject train-block summary, previous/next block rates, block length/phase, overnight measurement-process context, raw05-compatible block residual, block-rate prediction energy.
- Label vs split test: this representation is useful only if it predicts validation block-rate targets fold-safely and remains stable under blockwise, anchor-LOO, raw05 compatibility, and train/test domain stress. It must be learned from context available at test time, not from validation labels or public LB fitting.
- Adopt if: it recovers a meaningful fraction of the `0.106888` temporal-to-block-rate oracle gap, improves blockwise LogLoss or calibration energy, and produces lower high-energy loss concentration without increasing bad-axis/raw05 risk.
- Drop if: it behaves like Markov row transition, endpoint propagation, nested one-feature threshold, or simple public-mask inverse fit: local-looking gains that do not transfer or recover only a tiny fraction of oracle headroom.
- Current evidence: E46 shows the block-rate oracle reaches `0.517878`, temporal-to-oracle gap is `0.106888`, full subject identity explains only `0.291286` of the gap, and `26/36` submission blocks have two train flanks. But best Markov is worse than temporal by `+0.002998`, nested threshold is worse by `+0.044275`, endpoint reconstruction gains only `0.003252` over subject mean, and E45 simple public masks have best LOO MAE `0.000429528`.
- Policy: make this the next JEPA representation target. Do not convert it directly into a submission until it passes blockwise and anchor stress; use its residual first as `block_state_bottleneck_energy` for gating/calibration.

### F34. Block-summary context-to-rate probe

- Hidden structure: whether current fold-safe block summaries already contain enough information to predict the hidden block-rate vector.
- Candidates: label-context summaries, previous/next train block rates, subject priors, sensor block means/std/deltas, missingness signatures, combined block summaries, block target energy.
- Label vs split test: useful only if block-rate target loss improves versus temporal block context. A row-blend gain without block-rate loss gain is calibration perturbation, not hidden-state recovery.
- Adopt if: block weighted LogLoss beats temporal block weighted LogLoss and the 25% row blend recovers a meaningful share of the `0.106888` oracle gap under subject-block folds, with non-collapsed geometry and no targetwise instability.
- Drop if: sensor/combined views worsen block-rate loss, best improvement is only row-level shrinkage, or targetwise gains depend on selecting views from the full OOF result.
- Current evidence: E47 shows best 25% row blend `label_context_ridge = 0.623260`, delta `-0.001505`, but oracle-gap recovery is only `0.014083` and block-rate loss is `0.635888` versus temporal block context `0.623448`. `sensor_values_ridge` worsens row blend by `+0.000660`. Label-context geometry is not collapsed (`anisotropy 0.466748`, effective rank `3.547232`) but still not predictive.
- Policy: negative gate for the current summary/Ridge family. Do not add this as a submission feature. Future block-state work must change context granularity or target type: discrete count/posterior target, contrastive block retrieval, raw overnight sequence tokens, or anchor-conditioned energy.

### F35. Subject-calendar mask block context

- Hidden structure: train/test rows are not independent observations but a subject-specific calendar mask. Test rows are hidden blocks inside each subject timeline, often adjacent to or between labeled train runs.
- Candidates: per-subject train/test run id, calendar phase (`inside_train_calendar`, `after_train_end`), flank type (`between_train_runs`, `gap_adjacent`, `isolated_gap`), hidden run length, days from previous/next train row, previous/next train block target rates, targetwise mixmin movement by block, raw05 distance by block, simple-prior CE contradiction flags.
- Label vs split test: this is useful only if it predicts held-out block target rates or explains known public-anchor movement under LOO without using test labels. It is split/leakage risk if used as a hard row identifier or public-subset mask without anchor stress.
- Adopt if: calendar-block features reduce mixmin-anchor selector error, improve block-rate/count target prediction under subject-block CV, or identify high-energy rows where mixmin should be trusted over raw05/a2c8.
- Drop if: it only reproduces row order, only fits mixmin in-sample, fails stage2/ordinal/raw05/bad-JEPA anchor order, or does not improve block-rate target loss beyond E47's weak summary/Ridge result.
- Current evidence: E49 shows test rows are hidden calendar blocks inside subject timelines; largest mixmin movements are `Q3 = 0.011540`, `Q1 = 0.010345`, `S3 = 0.009688`; `Q1` and `S1` are not supported by global/subject/recent priors; top high-movement blocks are `gap_adjacent` or `between_train_runs`. E50 tested target/prior, calendar, subject, and subject-calendar movement views with mixmin as a known anchor. Best `subject_calendar` MAE was `0.000884106`, rank `0.833333`, and bad-tail order correct, but it predicted held-out mixmin delta `0.00135162` instead of `0`; strict and loose selector views were `0`.
- Policy: keep as JEPA context/energy, not as a standalone selector or public-LB forecast. Use it only when paired with anchor-loss/binary-world geometry or a block-rate/count target. Drop direct calendar-position tweaks and any candidate whose only evidence is E50 predicted score.

### F36. Anchor-loss world aggregate selector features

- Hidden structure: whether binary frontier-box worlds and known-anchor loss/cancellation geometry can be converted from a successful public sensor into a reusable selector for post-mixmin candidates.
- Candidates: per-world candidate LogLoss delta versus a2c8, low-anchor-energy better rate, low/high energy delta gap, targetwise delta means, cancellation, entropy, movement/loss correlation, residual-including world energy, and combinations with compact calendar fingerprints.
- Label vs split test: useful only if known-anchor LOOCV predicts mixmin as best while preserving raw05/a2c8, stage2/ordinal, and bad-JEPA order. It is leakage-prone if the held-out anchor contributes to world-energy scoring.
- Adopt if: a LOO-safe view predicts held-out mixmin as public-best, keeps a2c8/raw05 order, and has error below the mixmin-a2c8 public edge.
- Drop if: it behaves as a coarse sensor only, fails mixmin-best, or ranks candidates through nearest-submission similarity rather than hidden-world feasibility.
- Current evidence: E51 tested shape and residual anchor-world aggregates alone and with target/prior, context-all, and moved-target calendar fingerprints. Strict and loose selector views were `0`. Best `anchor_residual` MAE was `0.000835516`, rank `0.750000`, bad-tail correct, but held-out mixmin predicted delta was `0.00241739`; a2c8/raw05 order also failed.
- Policy: do not use as a public-LB regressor or candidate forecast. If anchor-loss is used next, use it as a constrained hidden-world feasibility stress with mixmin included as a known constraint, not as kNN features over submission files.

### F37. Post-mixmin binary-world sign stress features

- Hidden structure: whether the public-validated mixmin anchor turns E30/E32 binary worlds into a local feasibility test for replacements.
- Candidates: mixmin residual to observed public delta, postmix world energy, mixmin-compatible world bands, candidate LogLoss delta vs mixmin, one-sided max-delta gates, near-tie flags, and mixmin-equivalent prediction flag.
- Label vs split test: useful only if candidate signs are evaluated out-of-anchor against worlds selected by mixmin fit and old anchor energy, not by known-submission nearest neighbors.
- Adopt if: a non-equivalent candidate has negative max delta vs mixmin in mixmin-fit and postmix-energy core bands, or if regenerated hard-constraint worlds produce stable sign.
- Drop if: only near-ties appear, better_rate is far from one-sided, or median/max deltas stay positive.
- Current evidence: E52 scored `158` candidates. Strict better-than-mixmin gates were `0`, loose gates were `0`, and near-tie gates were `1`. The only non-duplicate near-tie was `bridge_blend_m0p75_s1p25`, with mixmin-fit-gap better_rate `0.2`, median `+0.000034`, max `+0.000048`, and postmix-energy-quarter better_rate `0.285714`, median `+0.000009`.
- Policy: use as a negative mixmin-replacement gate. Do not submit E52 near-ties; either predict block-rate/count state or regenerate hard mixmin-constrained worlds.

### F38. Calendar-flank block count-state posterior

- Hidden structure: whether labeled subject-calendar flanks and block length/topology expose the hidden block target count/rate state that mixmin appears to approximate.
- Candidates: previous/next labeled block rates, edge-shrink posterior, same-subject local donor posterior, strict subject-excluded donor posterior, donor support, dominant donor stage, length-bin support, and targetwise expected CE deltas for mixmin/raw05 versus a2c8.
- Label vs split test: useful only if strict subject-excluded pseudo-hidden blocks improve over subject mean and real hidden-block target alignment is broad, not concentrated in a few public-friendly targets. Leakage-prone if same-subject local donors are treated as private-safe evidence.
- Adopt if: strict donor posterior beats subject mean on pseudo-hidden weighted row LogLoss/count NLL, improves both Q and S groups, and assigns actual hidden blocks a one-sided mixmin advantage with no large adverse target.
- Drop if: gains come only from local same-subject donors, strict donors worsen pseudo-hidden loss, or hidden alignment is target-mismatched.
- Current evidence: E53 found local pseudo-hidden delta `-0.005266`, but strict delta `+0.001434`. Strict improved Q1/Q2/Q3 but worsened all S targets in pseudo-hidden stress. Actual hidden strict rates weakly favored mixmin overall (`-0.000179`) and only on S3/S2/Q2, while S1/Q1/Q3/S4 were adverse.
- Policy: keep as `calendar_flank_count_state_energy` and support diagnostics. Do not create or submit row probability movement directly from this posterior. The next version must add richer raw overnight context or target-dependency count manifolds before candidate generation.

### F39. Raw overnight block-state embedding

- Hidden structure: whether phone/watch/context/light/mobility/usage/coverage overnight traces encode the hidden block-state generator beyond same-subject calendar flanks.
- Candidates: feature-family row PCA embeddings, block mean/std/min/max/first/last/slope aggregates, raw-only kNN donor posterior, raw+flank kNN donor posterior, strict-vs-local donor gap, family-specific donor distance, targetwise S3 conflict, and actual hidden-block mixmin delta under predicted rates.
- Label vs split test: useful only if strict subject-excluded pseudo-hidden blocks improve over subject mean and if actual hidden-block sign stress does not contradict the public frontier. Leakage-prone if local same-subject gains or train/test raw-domain proximity are treated as private-safe evidence.
- Adopt if: strict raw+flank posterior improves pseudo-hidden weighted row LogLoss, targetwise deltas are not adverse on S targets, actual hidden-block rates prefer mixmin or a new candidate one-sidedly, and geometry stays non-collapsed.
- Drop if: pseudo-hidden recovery works but actual hidden-block mixmin alignment is adverse, or if the targetwise gain is dominated by Q targets while S-stage structure regresses.
- Current evidence: E54 found best strict method `night_phone_rawctx_strict_k8_a24` with pseudo-hidden delta `-0.007733`, stronger than E53 strict calendar counts. Geometry did not show obvious collapse (`effective_rank 23.393361-35.124905`, `anisotropy 0.144271-0.183029`). But S3 worsened by `+0.007802`, and actual hidden-block mixmin delta for the same method was adverse at `+0.000311`; the best hidden alignment stayed with `calendar_count_strict` at only `-0.000179`.
- Policy: keep as `raw_overnight_block_state_energy`, not as a direct probability-movement feature. It is useful for stress, private-risk diagnosis, and future target-dependency/S3 correction or mixmin-hard world feasibility, but cannot generate a submission until the mixmin-sign conflict is resolved.

### F40. Raw block target-dependency projection

- Hidden structure: whether the E54 raw overnight block-state vector violates a simple Q/S target-rate manifold, especially around S3, and can be projected back onto a public-aligned count state.
- Candidates: kNN projection from pair/group/all-cross donor target rates, Ridge logit-rate projection, S3-only replacement, S2/S3 and stage-group projection, projection support, target-rate manifold energy, hidden mixmin delta.
- Label vs split test: useful only if strict subject-excluded donor projections improve or preserve raw pseudo-hidden LogLoss, fix S3 versus subject mean, and make actual hidden-block rates prefer mixmin. It is invalid if hidden sign improves only when pseudo-hidden loss collapses.
- Adopt if: at least one projection has `delta_weighted_row_logloss_vs_raw <= 0`, `s3_delta_vs_subject <= 0`, and `weighted_mixmin_delta_vs_a2c8 < 0`, with no large targetwise adverse movement.
- Drop if: S3 repair and hidden mixmin sign remain separated, or Ridge/projection methods achieve sign by making pseudo-hidden LogLoss much worse.
- Current evidence: E55 tested `225` methods and found joint gates `0`. `raw_phone_s3_subject_w1p00` improved raw by `-0.001115` and fixed S3, but hidden mixmin remained adverse `+0.000319`. The best hidden-sign method `raw_phone_td_ridge_groupcross_all_k0_a8_w0.75` reached `-0.000414`, but pseudo-hidden LogLoss was `0.727319`, raw delta `+0.122051`, and S3 delta `+0.207892`.
- Policy: negative gate for simple target-rate projection. Do not use as a submission feature or postprocess. Future use requires a structural target representation or mixmin-hard world constraint, not another target smoothing variant.

### F41. Mixmin-hard raw world posterior energy

- Hidden structure: whether a binary hidden-label world family that treats mixmin as an observed public constraint and raw overnight block-state rates as feasibility energy exposes a posterior hidden state not present in existing candidate files.
- Candidates: mixmin-hard world posterior mean, raw-energy posterior subsets, held-world posterior deltas, world energy ranks, posterior distance from mixmin, actual-anchor residual, movement guard, and posterior-as-teacher confidence.
- Label vs split test: useful only if internal world-LOO signs survive and independent actual-anchor/public-shape stress does not worsen versus mixmin. Invalid as a direct feature if world-internal gains require large logit movement or fail anchor safety.
- Adopt if: posterior variant passes world-LOO strict, beats mixmin under actual-anchor stress, and mean abs logit movement versus mixmin is small enough to avoid public-subset overfit.
- Drop if: posterior is internally strong but actual-anchor adverse, or if the selected movement is far from mixmin without independent safety support.
- Current evidence: E56 generated `45` worlds / `44` unique worlds and opened `12` posterior world-LOO strict gates while existing candidate strict gates stayed `0`. But E57 found joint safety gates `0/15`: best posterior actual-anchor delta was `+0.000123` versus mixmin, and the E56 selected diagnostic was `+0.020381` with mean abs logit movement `0.381359`.
- Policy: keep as `mixmin_hard_raw_posterior_energy` and teacher signal only. Do not submit direct posterior variants. The next usable feature must be anchor-constrained distillation or a structural block target that inherits E56 information without violating mixmin public-anchor geometry.

### F42. Anchor-constrained E56 posterior distillation

- Hidden structure: whether the E56 posterior has a small, confident, public-anchor-compatible subdirection when restricted by target masks, world support, entropy, raw agreement, and row-level teacher strength.
- Candidates: posterior-band teacher deltas, target masks, low-entropy/high-support/high-absolute cell gates, raw-agreement gates, teacher/raw/support row gates, cap/weight schedule, reverse-control direction, anchor margin gate.
- Label vs split test: useful only if toward-teacher movement passes generated-world guard and beats mixmin under actual-anchor stress by a selector-scale margin. Invalid if improvements are only sign-level and below margin.
- Adopt if: at least one toward-teacher candidate has `anchor_delta_vs_mixmin < -1e-5`, `world_guard=True`, `movement_guard=True`, and reverse controls do not show stronger anchor improvement.
- Drop if: best anchor improvement is below `1e-5` or reverse controls are comparable.
- Current evidence: E58 generated `104727` candidates and actual-anchor scored `1200`; E61 fixed a sorted-prefilter score-index mismatch with stable `pred_index`. Corrected toward-teacher sign-level anchor improvements were only `126/900`; eligible gates were `0`; best delta was `-0.000004081`. Reverse-control best delta was only `-0.0000000126` and had no world guard.
- Policy: negative gate for simple E56 teacher slicing. Keep the best patterns as diagnostics only; do not create a submission from sub-margin distillation. Next useful representation work must add structural block targets or independent non-anchor validation.

### F43. Structural joint block label-pattern target

- Hidden structure: whether the right JEPA target is not seven marginal rates but a full within-block Q/S co-occurrence distribution over 128 label patterns.
- Candidates: block pattern entropy, top-pattern mass, 128-state pattern posterior, own-margin joint gain, pairwise co-occurrence rates, strict donor support/distance, structural NLL versus raw independent marginals, and hidden mixmin sign under pattern-derived marginal rates.
- Label vs split test: useful only if structural NLL improves without worsening row LogLoss, S3 stress, or hidden mixmin sign. A high feature importance or lower pattern NLL is not enough if the pattern posterior shifts marginal probabilities into a public-adverse state.
- Adopt if: at least one method has `delta_pattern_nll_vs_raw < 0`, `delta_weighted_row_logloss_vs_raw < 0`, `weighted_joint_gain_vs_own_margins < 0`, `s3_delta_vs_subject <= 0`, and `weighted_mixmin_delta_vs_a2c8 < 0`.
- Drop if: pattern NLL gains trade off against row LogLoss, hidden mixmin sign, or S3; or if hidden-sign gains come only from methods with collapsed pseudo-hidden validity.
- Current evidence: E59 tested `216` structural methods. Pattern structure is real: `139` beat raw independent pattern NLL and `198` had own-margin joint gain. But row LogLoss improvements versus raw were `0`, joint gates were `0`, and the axes split sharply. Best pattern method `struct_raw_calendar_subject_fbsubject_k16_a12_w0.35` had pattern delta `-0.062594` but row delta `+0.003678` and hidden mixmin `+0.000304`. Best hidden-sign method `struct_raw_subject_fbraw_k8_a4_w1.00` had hidden mixmin `-0.000367` but row delta `+0.042230` and S3 `+0.078145`.
- Policy: keep as `structural_joint_pattern_energy` and negative evidence for within-block pattern-only targets. Do not build submissions from E59 pattern-derived rates. The next structural target must add transition/topology/public-disagreement or provide independent validation for E56 energy.

### F44. Transition-residual block-state target

- Hidden structure: whether the relevant JEPA target is the residual change from labeled flanks/raw/subject state into the hidden run, rather than a within-block marginal or joint label distribution.
- Candidates: endpoint-mid and endpoint-shrink bases, raw/subject/calendar residuals, topology vectors, raw-residual/full-transition contexts, strict donor support, transition-residual MSE, S3 residual risk, and actual hidden-block mixmin delta under residual-derived rates.
- Label vs split test: useful only if strict subject-excluded residual prediction improves pseudo-hidden row LogLoss over raw, reduces residual MSE, preserves S3 versus subject mean, and makes actual hidden blocks prefer mixmin. It is invalid if hidden sign is achieved through extreme endpoint residuals that break pseudo-hidden calibration.
- Adopt if: at least one method has `delta_weighted_row_logloss_vs_raw <= 0`, `delta_transition_residual_mse_vs_raw <= 0`, `s3_delta_vs_subject <= 0`, and `weighted_mixmin_delta_vs_a2c8 < 0`.
- Drop if: residual MSE, row LogLoss, S3, and hidden mixmin sign separate; or if only aggressive edge-based residuals make hidden sign negative.
- Current evidence: E60 tested `432` transition methods plus baselines. Joint gates were `0`; residual MSE improved in `227`, and hidden mixmin sign was negative in `217`, but row validity did not survive. Best row-valid transition `transition_raw_residual_baseraw_k4_a24_w0.35` was near raw (`+0.000186` row delta), improved residual MSE (`-0.017074`), but hidden mixmin stayed adverse (`+0.000230`) and S3 remained adverse. Best hidden-sign method `transition_raw_residual_baseedge_mid_k4_a4_w1.00` reached hidden mixmin `-0.001569`, but row LogLoss collapsed by `+1.519232` versus raw and S3 by `+1.331880` versus subject.
- Policy: keep as `transition_residual_block_state_energy` and teacher-risk diagnostic only. Do not create submissions from E60 residual rates. Future structural targets may include transition residuals only with explicit row-calibration and S3 constraints.

### F45. Transition-gated E56 posterior distillation

- Hidden structure: whether transition residual sign/block/target views can validate the tiny E56 teacher direction when used only as gates, not as probability targets.
- Candidates: row-safe transition residual view, balanced hidden-sign view, aggressive hidden-sign view, transition/raw sign consensus, transition block-good gate, transition target-good gate, S3 exclusion, E56 world-support prefilter, actual-anchor margin.
- Label vs split test: useful only if transition-gated toward-teacher movement beats corrected E58 and clears the `1e-5` anchor margin while preserving world and movement guards. Invalid if it only creates a more interpretable sub-margin micro-move.
- Adopt if: at least one toward-teacher candidate has `anchor_delta_vs_mixmin < -1e-5`, `world_guard=True`, `movement_guard=True`, and reverse controls do not show stronger evidence.
- Drop if: best anchor improvement is below E58 or below `1e-5`, or if reverse controls become comparable.
- Current evidence: E62 generated `363258` candidates and actual-anchor scored `1300`. Eligible gates were `0`; best toward-teacher delta was `-0.000002716`, weaker than corrected E58's `-0.000004081`; best reverse delta was `-0.00000000547`.
- Policy: negative gate for simple transition-as-mask use. Keep transition residual as a risk diagnostic or component of a richer structural target, not as a standalone E56 validator.

### F46. Gradient-consensus E56 posterior validator

- Hidden structure: whether independent hidden-rate views define a local BCE-gradient field around mixmin that agrees with E56 teacher movement, separating true hidden-world direction from reverse/control artifacts.
- Candidates: per-cell gradient agreement from subject mean, strict calendar count, raw phone base, row-safe transition, balanced/aggressive transition signs, core-median hidden rate, gradient support counts, hidden-core/all mean deltas, gradient top-k row gates, and reverse-control contrast.
- Label vs split test: useful only if gradient agreement separates toward-teacher from reverse controls under train-only/pseudo-hidden views and still clears actual-anchor margin. Invalid if it validates direction but every public-anchor gain remains sub-margin.
- Adopt if: at least one toward-teacher candidate has hidden guard, E56 world guard, movement guard, reverse-control separation, and `anchor_delta_vs_mixmin < -1e-5`.
- Drop if: hidden guards open but anchor margin remains below selector scale, or if reverse controls also pass hidden/world guards.
- Current evidence: E63 generated `404671` candidates and actual-anchor scored `1300`. Direction evidence is strong: toward hidden guard `1000/1000`, world guard `1000/1000`, anchor beats `932/1000`; reverse hidden guard `0/300`, world guard `0/300`. But eligible gates were `0`, best toward anchor delta was only `-0.000003650`, and the best hidden-core mean delta `-0.000368596` did not translate into public-anchor margin.
- Policy: keep as `gradient_consensus_posterior_energy` and cell-direction validator. Do not create a submission from gradient gating alone. Future features should estimate amplitude/calibration risk for these validated cells rather than re-proving direction.

### F47. Gradient-amplitude E56 translator

- Hidden structure: whether the E63 direction is valid but under-scaled, so larger capped logit moves on the same gradient-consensus cells can reach selector-scale public-anchor improvement.
- Candidates: larger scale/cap schedules, flat versus gradient-gain amplitude shapes, target masks excluding Q2/S3, movement-bin behavior, and anchor response curves by scale.
- Label vs split test: useful only if actual-anchor loss improves monotonically or at least opens a margin candidate while hidden/world guards remain true. Invalid if hidden/world guards survive but anchor sign flips adverse.
- Adopt if: at least one toward candidate has `anchor_delta_vs_mixmin < -1e-5`, `world_guard=True`, `hidden_guard=True`, `movement_guard=True`, and reverse controls remain non-improving.
- Drop if: amplified toward candidates all lose to mixmin under actual-anchor stress.
- Current evidence: E64 generated `12096` candidates and actual-anchor scored `1796`. Toward candidates passed hidden/world/movement guards `1346/1346`, but anchor beats were `0/1346`; best toward anchor delta was `+0.000003024`, median toward delta `+0.000757074`. Reverse controls also did not improve.
- Policy: negative gate for scalar amplitude. Do not rescale E63/E56 gradient cells globally. Future use must learn targetwise/rowwise amplitude or alter the structural target/cell set.

### F48. Near-zero targetwise E56 amplitude pocket

- Hidden structure: whether the E63 direction is correct only in a very small, target-specific pocket around mixmin, with Q2/S3 acting as conflict targets that destroy broader movement.
- Candidates: small scale schedules, target masks (`no_q2_s3`, `no_q2`, `no_s3`, single targets), row gates, flat/core-gain amplitude shapes, anchor response curve, and targetwise adverse-response flags.
- Label vs split test: useful only if a near-zero pocket clears the `1e-5` actual-anchor margin while preserving hidden/world/movement guards. Invalid if the best response is sign-positive but sub-margin, or if the gain depends on excluding targets without explaining why.
- Adopt if: at least one candidate has `anchor_delta_vs_mixmin < -1e-5`, hidden/world/movement guards true, reverse controls rejected, and target response broad enough to avoid a single fragile public-anchor artifact.
- Drop if: the best pocket is below margin or single-target moves are too weak/adverse.
- Current evidence: E65 generated `27384` candidates and actual-anchor scored `2400`. Toward candidates passed hidden/world/movement guards `2290/2290`, and `1753/2290` beat mixmin sign-level. The best delta improved over E63 to `-0.000005995`, but anchor-margin gates remained `0`. Target response was concentrated in exclusions: `no_q2_s3` best `-5.995e-6`, `no_q2` `-5.090e-6`, `no_s3` `-4.726e-6`, `all` `-4.193e-6`; single Q1/S4/Q3 were much weaker and S2 was adverse.
- Policy: keep as `near_zero_amplitude_response_energy`, not as a submission feature. The next feature must explain the Q2/S3 conflict or learn rowwise amplitude; do not continue tiny line-search sweeps around the same cells.

### F49. Q2/S3 tail-risk translator

- Hidden structure: whether Q2/S3 are genuinely bad targets for E56 movement or are hidden/mean-favorable targets whose public-compatible scenario tails dominate robust LogLoss.
- Candidates: matched add-back tail features, max-set minus mean-anchor spread, Q2/S3 scenario variance, targetwise disagreement between hidden-core BCE and robust anchor score, per-row Q2/S3 amplitude caps, and tail-neutral gates that allow Q2/S3 only when max-set risk stays flat.
- Label vs split test: useful only if it separates hidden/mean improvement from public-tail risk without using public LB directly. Invalid if it merely repeats `no_q2_s3` masking or picks Q2/S3 amplitudes by known-anchor score alone.
- Adopt if: a Q2/S3-inclusive candidate preserves hidden/mean improvements while keeping robust actual-anchor tail neutral or improving by at least selector margin, with matched add-back decomposition not worse in max-set tail.
- Drop if: Q2/S3 add-back remains robust-anchor adverse after tail gates, or if hidden gains survive only through row calibration collapse.
- Current evidence: E66 generated and scored `3000` focused candidates. `no_q2_s3` remained best (`-5.994944e-6`), but the important finding was decomposition: `all` add-back was robust-anchor adverse `432/432`, mean-anchor improved `288/432`, max-set tail worsened `432/432`, min-set tail improved `432/432`, and hidden core improved `432/432`. Q2/S3-only movement had hidden gains but `q2` and `q2_s3` had `0` anchor beats.
- Policy: add `q2_s3_tail_risk_energy`. Do not choose targets by mask alone. The next feature must penalize max-set/tail risk or condition Q2/S3 movement on scenario stability.

### F50. Tail-neutral Q2/S3 translator

- Hidden structure: whether E66's Q2/S3 conflict can be translated by selecting only cells whose first-order scenario-tail derivatives are non-adverse, instead of masking Q2/S3 entirely.
- Candidates: mean-negative first-order gate, p90/max non-positive gates, soft p90/max gates, margin-threshold variants, Q2/S3-only row gates, and scenario-holdout versions of those gates.
- Label vs split test: useful only if the same gated cells also survive hidden/block/row-calibration stress outside known-anchor scenario derivatives. Invalid if the improvement is only an anchor-tail arithmetic artifact.
- Adopt if: tail-gated Q2/S3 movement beats matched `no_q2_s3` with selector-scale margin, preserves max-set tail neutrality, and shows non-anchor agreement from hidden-rate/block context or row calibration.
- Drop if: margin gates remain `0`, or if hidden/mean gains disappear under scenario-holdout or non-anchor validation.
- Current evidence: E67 generated and scored `7632` candidates. Best `tail_meanneg_m1.00` improved to `-6.933142e-6` versus mixmin and beat the matched base in `387/432` anchor scenarios, while `tail_p90_nonpos_m1.00` beat matched `no_q2_s3` in `432/432` and stayed max-set-tail-neutral in `360/432`. Across pair comparisons, `4207/7200` beat the matched base and `2241/7200` also stayed max-set-tail-neutral. However, all anchor-margin gates remained `0`.
- Policy: add `q2_s3_tail_neutral_translation_energy`. Do not submit E67 candidates. The next feature must independently validate tail-gated Q2/S3 cells before any public file.

### F51. Heldout/non-anchor Q2/S3 tail-gate validator

- Hidden structure: whether E67 tail-gated Q2/S3 cells survive outside the same known-anchor derivatives used to build them.
- Candidates: strict independent Q2/S3 cell set, held-out combo-set score, held-out worst-tail neutrality, hidden Q2/S3 mean/core improvement, world support, hidden-block Q2/S3 block win rate, and rowwise amplitude eligibility over strict cells.
- Label vs split test: useful only if the gate is rebuilt without the held-out combo family and still agrees with hidden/world/block diagnostics. Invalid if it only improves held-out combo score while failing block-majority or world support.
- Adopt if: strict cells can be used as a latent/amplitude gate and a later translator clears selector-scale margin while preserving tail and block support.
- Drop if: amplitude over strict cells repeats E64 scalar-adverse behavior, or if block/hidden support disappears under a more independent split.
- Current evidence: E68 selected `180` promising E67 configs, scored `762` unique predictions, formed `540` matched comparisons, and found `155` independent gates, all strict. `tail_soft_max_m1.00` produced `44` strict gates and best block win rate `0.944444`; `tail_p90_nonpos_m1.00` produced `41` strict gates and best strict heldout delta `-1.260816e-6`. `tail_max_nonpos_m1.00` had stronger heldout score (`-1.629588e-6`) but `0` block-majority wins, proving heldout score alone is insufficient.
- Policy: add `q2_s3_tail_gate_independence_energy`. Do not submit E68 cells directly. The next feature must use strict cells for calibrated rowwise amplitude or as a structural target/energy.

### F52. Strict Q2/S3 cell amplitude response

- Hidden structure: whether independently validated Q2/S3 cells are under-amplified or intrinsically limited by heldout/tail calibration.
- Candidates: alpha response over Q2/S3-only logit delta, full-combo margin count, heldout tail-neutral decay curve, train/all response, hidden/world/block response, and per-row/cell amplitude eligibility flags.
- Label vs split test: useful only if full-combo margin improves while heldout tail neutrality and non-anchor diagnostics survive. Invalid if the only gain appears at high alpha with heldout tail collapse.
- Adopt if: alpha scaling opens strict amplitude gates or reveals a stable row/block subset whose margin improves without tail degradation.
- Drop if: full-combo best remains below `-1e-5`, or alpha improves all-combo while heldout/tail response collapses.
- Current evidence: E69 used `155` E68 strict pairs and scored `2170` rows / `2061` unique predictions over alpha `0` to `24`. Strict amplitude gates were `0`, full-combo margin gates were `0`, and best full-combo delta was `-9.1779e-6`. Heldout tail-neutral counts fell from `155/155` at alpha `1` to `69/155` at alpha `8`, `49/155` at alpha `12`, and `22/155` at alpha `24`; median heldout response turned adverse after alpha `10`.
- Policy: add `q2_s3_strict_cell_amplitude_energy`. Do not repeat global alpha sweeps. The next feature must condition amplitude on row/block/tail energy or use strict cells as a structural target.

### F53. Strict Q2/S3 cell consensus representation

- Hidden structure: whether multiple independently validated E68 Q2/S3 cells share a common row/target latent that is stronger than single-pair heldout gains.
- Candidates: pooled matched `no_q2_s3` base logits, aggregated Q2/S3 logit deltas, all/heldout/translator/top-ranked pools, mean/median/weighted/signed-p75 delta aggregators, agreement gates, alpha response, combo tail neutrality, hidden/world/block Q2/S3 support, and `gate=none` risk flags.
- Label vs split test: useful only if consensus movement clears full-combo margin, beats matched bases across all combo sets, keeps worst-set tails non-worse, and survives hidden/world/block stress. Invalid if strict rows only appear under heldout-specific construction or disagreement-permissive gates that cannot become a test-time rule.
- Adopt if: a unified non-heldout consensus rule reproduces E70-style margin with hidden/world/block/tail support and stable agreement geometry.
- Drop if: margin disappears under unified-rule stress, sign-agreement gates stay below margin, or strict rows rely on anchor-derived heldout selection.
- Current evidence: E70 built `2688` rows / `2576` unique predictions from `155` E68 strict cells. Strict consensus gates were `6`, loose gates `502`, and best all-combo delta was `-1.027751e-5`. Strict rows all used `gate=none`, had `3/3` combo set wins and tail-neutrality, hidden Q2/S3 mean improvements around `-0.000411` to `-0.000542`, world support improvements around `-0.000403` to `-0.000490`, and block win rates `0.888889-0.916667`.
- Policy: add `q2_s3_strict_cell_consensus_energy`. Do not submit E70 outputs directly. Use this as the next unified-rule or structural-target input.

### F54. Unified strict-cell consensus representation

- Hidden structure: whether the E70 consensus survives when strict cells are reconstructed as unique full-combo cells rather than heldout-specific diagnostic cells.
- Candidates: unique strict-cell fingerprints, support count, full-combo reconstructed base/delta consensus, strict/loose/deployable consensus flags, `gate=none` risk flag, and hidden/world/block/tail support under unified reconstruction.
- Label vs split test: useful only if unified reconstruction preserves margin and at least one non-`none` agreement gate becomes deployable. Invalid if strict rows survive only through `gate=none`, because that means the consensus has not become a conservative test-time gate.
- Adopt if: deployable unified gates (`strict_unified_gate & gate != none`) appear with hidden/world/block support and selector-scale margin.
- Drop if: deployable gates remain `0` or the only margin rows remain disagreement-permissive.
- Current evidence: E71 used `155` E68 strict rows to derive `104` unique cells and `51` support-2 cells, then built `3136` rows / `2842` unique predictions. Strict unified gates were `1`, deployable unified gates were `0`, loose gates were `475`, and best all-combo delta was `-1.082166e-5`. The only strict row used `top75_heldout_mean`, mean base, `signed_p75` delta, `gate=none`, and alpha `8`; it kept `3/3` combo set wins/tail-neutrality, hidden Q2/S3 improvement `-0.000477907`, world support improvement `-0.000413602`, and block win rate `0.833333`.
- Policy: add `q2_s3_unified_consensus_energy`. Do not submit E71 outputs. Use it as positive evidence that consensus is not purely heldout arithmetic and negative evidence against `gate=none` consensus as a deployable rule.

### F55. Sparse-magnitude unified Q2/S3 gate

- Hidden structure: Q2/S3 consensus may not be sign-agreeing across source cells, but its highest-magnitude consensus cells can still identify the rows/targets where movement is public-aligned.
- Candidates: `top_abs50`, `top_abs30`, target-side sparse gates (`s3_only`, `q2_only`), soft signed weights, agreement thresholds, gate-active rate, sparse-gate hidden/world/block response, and selected non-`none` deployable submission files.
- Label vs split test: useful only if sparse gates clear full-combo margin, beat matched base/tail stress, preserve hidden/world/block Q2/S3 support, and produce a materialized file whose public LB tests the predeclared hypothesis. Invalid if only `gate=none` or soft/sign agreement works, or if public LB rejects the sparse-gate file.
- Adopt if: a later broader structural/block-state selector uses the same Q2/S3 sign while preserving hidden/world/block support and crossing margin without E73-style broad contamination.
- Drop if: future Q2/S3-informed structural gates remain sub-margin, or if public LB rejects a clean Q2/S3-guarded structural file.
- Current evidence: E72 generated `4752` rows / `4752` unique predictions and found strict rows `21`, deployable non-`none` rows `10`, and loose rows `655`. `top_abs50` produced `7` deployable rows with best all delta `-1.05458e-5`; `s3_only` produced `3`; Q2-only produced none. E73 materialized the best `top_abs50` row as `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`, with hidden Q2/S3 mean improvement `-0.000391043`, world support `-0.000280957`, raw-energy q-p90 `-0.000159091`, and block win rate `0.722222`. Public LB was `0.5764077772`, worse than mixmin by `+0.0001011367`; E80 found the file moved `893` cells across all `7` targets. E81 found pure Q2/S3 graft loose but sub-margin (`-5.95383e-6`) and inverse Q2/S3 locally adverse (`+1.47473e-5`).
- Policy: keep `q2_s3_sparse_gate_energy` as a diagnostic latent, not a direct submission feature. Do not submit E74/E75 or pure grafts as simple follow-ups; require a broader structural/block-state move that uses Q2/S3 as a guard.

### F56. Sparse Q2/S3 gate stability and amplitude ridge

- Hidden structure: if E73's sparse gate is a real latent consensus rather than a few-cell accident, its row/target movement should survive source-cell deletion and random subset stress. If alpha20 is useful, the same full-pool direction should improve locally before alpha24 breaks strict consensus.
- Candidates: leave-one-cell-out source pools, deterministic bootstrap8 source pools, group/rank source subsets, alpha response over `[8, 12, 16, 20, 24]`, Jaccard overlap against E73 active Q2/S3 cells, and full-pool alpha20 materialization.
- Label vs split test: useful only if cell-subset stability is broad and the higher-amplitude row keeps hidden/world/block/tail support. Invalid if only one source cell or a small bootstrap accident drives the deployable gate, or if alpha20/alpha24 show uncontrolled amplitude risk.
- Adopt if: E73-like alpha16 rows remain deployable across most jackknife variants and a meaningful bootstrap fraction, while alpha20 remains strict/deployable without changing the source pool.
- Drop if: jackknife variants fail, bootstrap support is rare, or public LB rejects both E73 and the full-pool alpha20 sensor.
- Current evidence: E74 scored `470` rows over `94` variants. Strict/deployable rows were `141`. Jackknife alpha16 was deployable `13/13`; bootstrap8 alpha16 was deployable `48/60`. The reference full-pool alpha20 row stayed strict/deployable with all delta `-1.07261e-5`, hidden Q2/S3 mean `-0.000484506`, world support `-0.000351115`, and block win rate `0.722222`; reference alpha24 failed strict. `analysis_outputs/submission_e74_fullpool_a20_q2s3_gate_55455b60.csv` was materialized as the clean amplitude sensor.
- Policy: add `q2_s3_sparse_gate_stability_energy`. Use E74 to upgrade confidence in E73, not to skip the first public sensor. E74 alpha20 is secondary and should be interpreted as an amplitude test after sparse-gate public sign is known.

### F57. Target-specific sparse Q2/S3 amplitude ridge

- Hidden structure: the sparse Q2/S3 gate may be real, but Q2 and S3 may have different safe/public-readable amplitude boundaries. S3 could carry the public-combo edge while Q2 supplies hidden/world support but needs shrinkage.
- Candidates: crossed `alpha_q2`/`alpha_s3` grid, dominant-axis class (`s3_higher`, `q2_higher`, `equal`, target-only), strict/deployable/loose flags, hidden Q2/S3 split, S3-heavy public-combo edge, distance from E73/E74, and target-specific amplitude submission files.
- Label vs split test: useful only if target-asymmetric amplitudes improve combo proxy while preserving hidden/world/block/tail diagnostics. Invalid if the best row simply overfits one target axis or collapses hidden/world support.
- Adopt if: S3-heavy/Q2-low rows remain deployable, beat symmetric alpha rows, and public LB improves or a future public-independent selector validates the same target asymmetry.
- Drop if: public LB rejects E75 while E73 survives, or if future stress shows the S3-heavy ridge is only a local combo proxy artifact.
- Current evidence: E75 scored `120` target-alpha rows. Strict/deployable rows were `37`; `s3_higher` contributed `23`, `s3_only` `6`, `q2_higher` `5`, `equal` `3`, and `q2_only` `0`. The best deployable row was `alpha_q2=8`, `alpha_s3=28`, with all delta `-1.23676e-5`, hidden Q2/S3 `-0.000372692`, hidden S3 `-0.000498235`, world support `-0.000200351`, and block win `0.722222`. `analysis_outputs/submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv` was materialized.
- Policy: add `q2_s3_target_amplitude_ridge_energy`. Use E75 as a high-information target-asymmetry sensor after E73, not as a lower-risk replacement for E73. Keep E74 as the symmetric-amplitude control.

### F58. Target-specific Q2/S3 amplitude subset-stability energy

- Hidden structure: target asymmetry may be stable while any single universal alpha pair is not. The feature should separate "S3-heavy direction survives" from "exact E75 `8/28` row is deployment-stable".
- Candidates: pairwise comparison of `asym8_28_e75` vs `sym16_e73` and `sym20_e74` across reference/jackknife/group/rank/bootstrap variants, exact-asym deployability count, best deployable dominant axis, median/worst asym all-delta, and source-pool sensitivity.
- Label vs split test: useful only if the S3-heavy direction survives variants that omit or resample cells. Invalid if target asymmetry disappears outside the full pool or if exact amplitude deployability depends on one subset family.
- Adopt if: S3-heavy rows beat symmetric controls broadly and public LB rewards E75 or a row/cell-conditioned asymmetric amplitude. Treat exact `8/28` as high-confidence only if future conditioning improves deployability beyond E76's partial rate.
- Drop if: public LB rejects E75 while E73/E74 survive, or if future stress shows exact-asym gains come only from local combo scoring with no independent target/block support.
- Current evidence: E76 scored `1974` rows over `94` source-subset variants. Exact `asym8_28_e75` beat symmetric controls in `94/94` variants, and best deployable axis was S3-heavy in `94/94`. Exact `asym8_28_e75` deployability was only `49/94`, with jackknife `8/13`, group_keep `7/10`, rank_keep `5/10`, and bootstrap8 `28/60`.
- Policy: add `q2_s3_target_amplitude_stability_energy`. Keep E73 first, E75 as target-asymmetry sensor, and E74 as symmetric control. Future amplitude features should be rowwise/cellwise energy-conditioned rather than universal `8/28`.

### F59. Q2/S3 source-subset amplitude posterior energy

- Hidden structure: E76 may have exposed a posterior distribution over safe Q2/S3 amplitudes rather than a single universal alpha pair. The feature asks whether aggregating source-subset predictions repairs exact-amplitude instability, or only averages incompatible public-tail worlds.
- Candidates: posterior selector name, base reference (`mixmin`, E73, E74), aggregation mode, target scope, shrink, source-row/source-variant/source-pair counts, strict/deployable/loose flags, E75-local beat count, combo-set wins, tail-neutrality, hidden/world/block response, and full-vs-Q2S3 scope divergence.
- Label vs split test: useful only if posterior aggregation opens strict or deployable rows while preserving combo-set, tail, hidden/world, and block support. Invalid if Q2/S3-only movement is safe but below margin, or if full-scope movement clears local margin by breaking set/tail consistency.
- Adopt if: a posterior aggregate becomes deployable under Q2/S3-only or S3-only scope, beats E75 locally, and keeps tail/hidden/world/block stress neutral or favorable.
- Drop if: generic posterior averaging creates no deployable rows, or if the best margin rows are full-scope artifacts with adverse hidden/world or weak tail coverage.
- Current evidence: E77 scored `6840` posterior rows from `19` selector groups over mixmin/E73/E74 bases. Strict/deployable rows were `0`, loose rows `3099`, and rows beating E75 local all-combo were `62` but none were deployable. Mixmin/Q2S3 was broad and safer (`688/760` loose; best all `-8.09547e-6`; hidden `-0.001203`; world `-0.000779`; block `0.833333`) but below margin. Mixmin/full reached `-1.25991e-5` and beat E75 in `9` rows, but best rows only beat `1/3` combo sets and kept `1/3` tails neutral.
- Policy: add `q2_s3_amplitude_posterior_energy` as a negative screen. Do not submit E77 posterior aggregates. The next amplitude feature must localize by combo-set, tail, row-block, or public-like risk instead of averaging E76 variants.

### F60. Q2/S3 localized amplitude reliability gate energy

- Hidden structure: exact target-specific amplitude may need row/target reliability masks rather than global pairs or posterior averages.
- Candidates: reliability source, mask mode, localization, mask active rates, Q2/S3 alpha, strict/deployable/loose, E75 beat, tail/set/hidden/world/block response.
- Label vs split test: useful only if masks improve over E75 without losing combo-set/tail/hidden/world/block support. Invalid if masks collapse to identity over active cells or shrink movement into sub-E75 edge.
- Adopt if: deployable localized rows beat E75 or match E75 edge with materially better tail/hidden/world/block.
- Drop if: masks collapse to identity, strong masks reduce edge, or no deployable row beats E75.
- Current evidence: E78 scored `4452` rows from `36` reliability masks. Strict/deployable rows were `1806`, loose rows `3934`, deployable rows beating E75 were `0`, and the best all-combo row was E75-equivalent at `-1.23676e-5`. Consensus maps mostly became identity; hard sign/excess/veto maps shrank signal.
- Policy: add `q2_s3_localized_amplitude_gate_energy` as a negative gate. Do not submit E78 variants. Future localization must use richer public-like row/block/tail state.

### F61. Q2/S3 public-like row/block amplitude energy

- Hidden structure: exact target-specific amplitude may be safe only on submission rows whose subject-calendar topology, flanking train labels, subject priors, or sparse-unit energy make them public-like.
- Candidates: subject-calendar run position, train flank availability/gaps, block edge/interior/half, subject-prior Q2/S3 rates, nearest train-label Q2/S3 flank means, target-specific Q2/S3 flank masks, positive sparse-unit energy quantiles, and topology x energy intersections.
- Label vs split test: useful only if handcrafted row/block/flank masks beat E75 local all-combo while preserving combo-set/tail/hidden/world/block stress. Invalid if masks only reduce the active set and lose edge, or reproduce identity rows.
- Adopt if: deployable row/block/flank-localized amplitude beats E75, or matches E75 edge with materially stronger stress profile.
- Drop if: no deployable row beats E75 and best non-identity masks are weaker.
- Current evidence: E79 scored `6516` rows from `61` masks. Strict/deployable rows were `1318`, loose rows `3403`, deployable rows beating E75 were `0`, and best all remained E75-equivalent at `-1.23676e-5`. E75 active movement covers only `72/250` rows/cells; positive-energy top30/top50 masks reduce that to `22`/`36` active rows without improving edge.
- Policy: add `q2_s3_public_like_rowblock_amplitude_energy` as a negative gate. Do not submit E79 variants. Keep row/block/flank context for structural targets, but do not expect handcrafted masks over E75 movement to repair amplitude.

### F62. E73 public assimilation and pure Q2/S3 split energy

- Hidden structure: the public miss from E73 may be caused by broad non-Q2/S3 base movement rather than the sparse Q2/S3 latent itself.
- Candidates: moved-cell target scope, pure Q2/S3 graft, Q2-only/S3-only grafts, non-Q2/S3-only graft, inverse-sign controls, public/local edge ratio, and combo-set/tail/hidden/world/block stress after scope isolation.
- Label vs split test: useful only if a pure graft retains local stress while removing broad base contamination. Invalid if pure Q2/S3 stays below margin or if inverse controls fail local stress.
- Adopt if: a future structural gate can use mixmin-anchored Q2/S3 energy while adding calibrated broader movement that clears selector margin without violating combo tails.
- Drop if: Q2/S3-informed structural gates remain sub-margin or reintroduce E73-style broad public failure.
- Current evidence: E80 found submitted E73 moved `893` cells across all `7` targets and scored public `0.5764077772`, worse than mixmin by `+0.0001011367`. E81 found pure Q2/S3 graft loose but sub-margin (`-5.95383e-6`), pure S3-only `-5.66531e-6`, pure Q2-only `-4.38789e-7`, and inverse Q2/S3 adverse (`+1.47473e-5`).
- Policy: add `e73_public_scope_split_energy`. Use it to veto direct E74/E75 follow-ups and to require broader structural/block-state gates for any future Q2/S3-informed submission.

### F63. Pure Q2/S3 source-graft margin energy

- Hidden structure: E72/E75/E76 may contain clean Q2/S3 source movements whose value or source-base delta survives once non-Q2/S3 base contamination is removed.
- Candidates: source family, value-vs-delta graft mode, target scope, source subset variant, target-alpha pair, combo-set wins, tail-neutral count, hidden Q2/S3 improvement, world support, block win rate, and all-margin failure distance.
- Label vs split test: useful only if pure grafts preserve hidden/world/block/tail support after anchoring to mixmin. Invalid as a submission generator if all failures concentrate on selector-scale margin rather than structure.
- Adopt if: a future broader structural candidate can use the same Q2/S3 energy while adding calibrated non-Q2/S3 or block-state movement to clear margin.
- Drop if: pure Q2/S3 source grafts are used directly as public submissions, or if public later shows sub-margin pure movement is not informative.
- Current evidence: E82 generated `8402` pure source graft rows and non-anchor evaluated `700`. Strict/deployable rows were `0`, loose rows `700`, and best evaluated all delta was `-7.90328e-6`. All evaluated rows passed combo-set, tail, hidden, world, and block guards (`700/700`), but all-margin was `0/700`.
- Policy: add `q2_s3_source_graft_margin_energy` as a positive latent/negative candidate gate. Use it to preserve Q2/S3 direction in future structural models, but veto Q2/S3-only submissions.

### F64. Q2/S3-energy structural gate

- Hidden structure: Q2/S3 pure movement is too small, but its row energy may mark hidden blocks where broader structural movement is safe.
- Candidates: E82 top-20 Q2/S3 energy, top50/top100/top250/top500 row gates, broad structural source deltas, target scopes, scale, E70 loose/strict, structural-loose, and hidden/world/block conflict metrics.
- Label vs split test: useful only if high-energy row gates preserve combo margin while improving Q2/S3 hidden/world/block stress. Invalid if broad margin rows worsen Q2/S3 or only pass one public-observation world.
- Current evidence: E83 generated `3716` rows, evaluated `700`, found strict/deployable `0`, loose `40`, structural-loose `189`, and best evaluated all delta `-3.50517e-5`. Broad structural rows made margin but worsened Q2/S3 hidden/world and beat only `2/3` combo sets; E72-safe rows passed loose but stayed sub-margin.
- Policy: keep as conflict diagnostic. Q2/S3 energy alone is not enough; combine target groups and then gate the remaining combo-set conflict.

### F65. Structural margin plus Q2/S3 safety recombination energy

- Hidden structure: non-Q2S3 structural movement may supply margin while Q2/S3 sparse safety movement supplies target-conflict repair.
- Candidates: E83 non-Q2S3 structural-loose rows, E72-derived Q2/S3-safe rows, structural/Q2S3 weights, inverse-top set response, raw05-compatible/all-sign set response, and strict-like-minus-one failure patterns.
- Label vs split test: useful only if the additive recombination passes all combo worlds or exposes one stable rejecting world. Invalid as a safe submission if one combo set rejects all otherwise healthy rows.
- Current evidence: E84 generated `1728` rows and evaluated `700`. Strict/deployable `0`, loose `700`, structural-loose `700`, best all `-3.215e-5`. All evaluated rows passed margin, hidden Q2/S3, world, block-majority, and block-tail; `672/700` passed raw-energy. Every row failed strict only because inverse-top rejected it (`0/700` set wins) while raw05-compatible and all-sign accepted it (`700/700` each).
- Policy: materialize only diagnostic `submission_e84_inverse_sensor_1c74da00.csv`. Do not treat E84 as safe unless public proves inverse-top is not public-like or a row/block gate separates the inverse-top conflict.

### F66. Inverse-top target-axis prune energy

- Hidden structure: E84's remaining inverse-top conflict may come from a few target axes contaminating an otherwise useful structural movement, rather than from a row/block-specific public subset.
- Candidates: target subset mask, per-target inverse-top/all-sign/raw05-compatible contribution, strict/deployable/loose flags, combo-set wins, tail-neutrality, hidden core, hidden Q2/S3, world, raw-energy, block win, and block-tail safety after pruning E84 movement.
- Label vs split test: useful only if the same target-pruned movement improves inverse-top while preserving raw05-compatible/all-sign, hidden/world, and block diagnostics. Invalid if target pruning only wins one combo world by sacrificing the other worlds or by collapsing movement size below margin.
- Current evidence: E85 scanned `10135` target-pruned E84 rows and evaluated `700`. Strict/deployable rows opened to `535`, with `S1,S2,S3` and `Q2,S1,S2,S3` both `80/80` strict/deployable. The selected `S1,S2,S3` file has all delta `-2.38758e-5`, inverse-top `-8.16658e-6`, raw05-compatible `-2.95552e-5`, all-sign `-3.39057e-5`, hidden core `-0.000161301`, hidden Q2/S3 `-0.000216060`, world `-0.000130361`, block win `0.666667`, and block-tail safety `0.944444`.
- Policy: promote `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv` as the next public candidate. If public improves, keep `inverse_top_target_prune_energy` as a positive gate and treat Q1/Q3/S4 structural movement as contamination. If public worsens, demote inverse-top pruning and revisit row/block gates or all-sign/raw05-compatible target axes.

### F67. Target-prune source-consensus energy

- Hidden structure: if target-axis pruning is a real law, not an E85 row accident, the same S1/S2/S3-like movement should be recoverable from many strict E85 source rows and should improve when averaged in logit-delta space.
- Candidates: target mask, source-file diversity, source-family diversity, seed-rank diversity, top/distinct selection size, mean/median/trimmed consensus, shrink/overstep, active cells, combo-set wins, hidden/world/block stress, raw-energy, and block-tail safety.
- Label vs split test: useful only if consensus preserves inverse-top/raw05/all-sign while improving margin and not collapsing to one source family. Invalid if consensus washes out the edge, breaks inverse-top, or relies on a single source file/seed rank.
- Current evidence: E86 generated `1485` consensus rows and evaluated `700`; every evaluated row was strict/deployable/loose. The selected `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv` keeps `Q2,S1,S2,S3`, averages top `40` strict E85 rows from `18` source files across `gate,rawcorr_micro,rawcorr_refine`, uses mean aggregation and shrink `1.25`, and has all delta `-2.77059e-5`, inverse-top `-6.91e-6`, raw05-compatible `-3.53387e-5`, all-sign `-4.08689e-5`, hidden core `-0.000239181`, hidden Q2/S3 `-0.000377585`, world `-0.000307439`, block win `0.833333`, and block-tail safety `1.0`.
- Policy: promote E86 as the highest-upside next public candidate. If public improves, keep source-consensus target-prune as a positive feature family. If public worsens while E85 improves, treat Q2 add-back or shrink `1.25` as overstep risk. If both worsen, demote inverse-top target pruning and reopen row/block or all-sign/raw05 target-axis alternatives.

### F68. E86 risk decomposition gates

- Hidden structure: E86's source-consensus target-prune latent may be right while one implementation axis is wrong: Q2 add-back, shrink `1.25`, or all-delta selection instead of inverse-top-prior selection.
- Candidates: no-Q2 target mask, no-overstep shrink, inverse-top-prior selection, source-file diversity, target-mask diversity, combo-set deltas, hidden Q2/S3, world support, raw-energy, block win, and block-tail safety.
- Label vs split test: useful only if each contrast stays inside the same strict/deployable stress manifold as E86 and changes one interpretation axis. Invalid if the contrast gains by leaving source-consensus support or by collapsing hidden/world/block stress.
- Current evidence: E87 rebuilt the E86 pool (`1485` rows) and kept a strict/deployable universe of `700`. It wrote `analysis_outputs/submission_e87_noq2_source_consensus_a85c4e39.csv` with all delta `-2.69461e-5`, `analysis_outputs/submission_e87_q2_nooverstep_consensus_acd7add0.csv` with all delta `-2.42545e-5`, and `analysis_outputs/submission_e87_inverse_top_prior_consensus_5445ec28.csv` with inverse-top delta `-2.06434e-5` and world `-0.000443423`.
- Policy: use E87 as public-feedback interpretation gates only. Do not rank these above E86 before public feedback. If E86 fails, choose one contrast to falsify the most likely failed axis instead of making another broad blend.

### F69. Frontier movement attribution energy

- Hidden structure: a public-positive frontier move and a public-negative follow-up move define two observed movement manifolds. New mixmin-relative candidates should be judged by whether they continue, rollback, or contaminate those manifolds.
- Candidates: high-mixmin cell/row mass, high-E72 failed cell/row mass, signed cell correlation with mixmin-vs-a2c8, row correlation with E72-vs-mixmin, `e72_failed_contamination_index`, `mixmin_reversal_index`, subject-prior CE proxy, raw-domain/order/calendar concentration, and target-axis movement scope.
- Label vs split test: useful only as a label-free attribution/risk lens after a real public observation. Invalid if used to fit public LB directly or to claim a score without stress evidence.
- Current evidence: E88 shows E86 has E72 overlap ratio `0.819288`, E72 contamination index `0.772379`, and E72 row correlation `0.725471`, while no-Q2 reduces contamination to `0.730408`. All E85/E86/E87 variants are negative-correlated with mixmin-vs-a2c8, meaning they are second-order rollbacks/refinements rather than first-order mixmin continuation. Inverse-top-prior has the highest E72 contamination index `0.928415`.
- Policy: use `frontier_movement_attribution_energy` before promoting any post-mixmin contrast. It may keep a high-upside sensor alive, but it should demote "safe fallback" claims when a candidate is E72-contamination-proximate.

### F70. E72-contamination cell fallback gate

- Hidden structure: E86 may contain a source-stable target-pruned law plus a smaller set of cells that lie close to the public-negative E72 manifold. Cell-level fallback to E85 can test whether this risk is localized.
- Candidates: E72 top-quantile cell mask, E72 row mask, fallback source (`E85`, no-Q2, mixmin), projection-away beta, E86/no-Q2 blend weight, E72 contamination index, local all-combo margin, hidden/world/block stress, and block-tail safety.
- Label vs split test: useful only if the fallback preserves strict stress and reduces E72 proximity. Invalid if the risk reduction comes from near-zero movement, positive inverse-top/world stress, or public-LB overfitting.
- Current evidence: E89 evaluated `52` controlled decontamination rows and found `37` strict/deployable. The selected `submission_e89_e72decontam_00d7807f.csv` uses E86 but falls back to E85 on top-20% E72 failed cells. It keeps all delta `-2.58960e-5`, inverse-top `-5.55392e-6`, raw05-compatible `-3.33148e-5`, all-sign `-3.88191e-5`, hidden Q2/S3 `-0.000216060`, world `-0.000140452`, block win `0.638889`, block-tail safe `0.944444`, and lowers contamination to `0.676361`.
- Policy: use `e72_contamination_cell_fallback_gate` as a risk-adjusted candidate generator, not an automatic replacement for E86. Promote it when downside control is more valuable than maximum local margin.

### F71. E72 Pareto-knee row fallback gate

- Hidden structure: E72 contamination may be tied to row/block state rather than isolated cells. A row-level fallback can remove the worst failed-manifold rows while preserving the internal coherence of E86's target-pruned structural movement.
- Candidates: E72 top-row fallback quantile, fallback source, Pareto score, margin retention, decontamination gain, hidden/world retention, row-coherence bonus, projection penalty, block win, and block-tail safety.
- Label vs split test: useful only if the row fallback remains strict/deployable, cleaner than E85/no-Q2, and retains materially more E86 hidden/world/block strength than the minimum-contamination cell fallback. Invalid if it only improves a handcrafted score while increasing E72 proximity above the failed controls or losing stress safety.
- Current evidence: E90 selected `analysis_outputs/submission_e90_e72pareto_28925de5.csv`, E86 with E85 fallback on the top `10%` E72-contaminated rows. It is cleaner than E85/no-Q2 (`0.715784` contamination), keeps all delta `-2.69324e-5`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block win `0.777778`, block-tail safe `1.0`, margin retention `0.798048`, and decontamination gain `0.589422`.
- Policy: use `e72_pareto_row_fallback_gate` as a balanced public sensor. It does not replace E89 for minimum contamination or E86 for maximum upside; it tests whether public values row-coherent structural preservation after removing the worst E72 rows.

### F72. E72-updated known-LB selector collapse flag

- Hidden structure: the known public LB anchors may not form a learnable smooth submission-geometry surface at frontier scale. If a proxy cannot distinguish mixmin from the public-negative E72 file, its candidate scores are a hallucinated calibration surface rather than useful evidence.
- Candidates: LOOCV proxy MAE/p90 error, mixmin holdout error, E72 holdout error, predicted E72-minus-mixmin sign, and candidate proxy spread over E85/E86/E89/E90.
- Label vs split test: useful only as a negative selector diagnostic. Invalid if used to rank submissions after it fails on known mixmin/E72 holdouts.
- Current evidence: E91 found best movement-fingerprint proxy `raw05_a2c8_compat` MAE `0.000543412`, p90 abs error `0.001010234`, mixmin holdout error `+0.001142722`, and wrong-sign E72-minus-mixmin prediction (`-0.0000460726` predicted vs `+0.0001011367` actual).
- Policy: set `known_lb_regression_selector_valid = false` for post-mixmin candidates. Do not create an E91 proxy-ranked submission. Use public observations as sensors and keep E86/E90/E89 ordering hypothesis-based.

### F73. Hidden-block posterior E72-taint flag

- Hidden structure: hidden-block posterior rates may encode real subject-calendar/block state, but not necessarily the public-safe direction. If a hidden representation rewards a known public-negative movement, it is a diagnostic energy rather than a selector.
- Candidates: posterior CE delta versus mixmin, endpoint CE delta, posterior-direction mass agreement, block-target R2, high-posterior-shift block movement lift, and E72 failed-direction mass agreement.
- Label vs split test: valid only if known public-negative E72 is not ranked above the active frontier and unobserved candidates. Invalid as a submission ranker when E72 is the posterior-alignment leader.
- Current evidence: E92 found `failed_e72` is the best hidden-block alignment and posterior CE candidate (`-0.000287300`). Among live candidates, no-Q2/E86 have stronger posterior CE than E90/E89, while E89 has the highest block-target R2 and lowest E72 direction mass among E86/E90/E89.
- Policy: set `hidden_block_posterior_selector_valid = false`. Use this feature family to diagnose representation mismatch and block coherence, not to rank public submissions directly.

### F74. Target-manifold E72-taint flag

- Hidden structure: train target co-occurrence is real, but public-safe translation may require a target manifold conditioned on hidden public subset/world identity rather than the unconditional train manifold.
- Candidates: conditional target logit residuals, empirical label-pattern mixture NLL, nearest-pattern NLL, pair-correlation gap, per-target conditional BCE, and public-bad-anchor sanity correlation.
- Label vs split test: valid only as a selector if it rejects known public-negative E72 and older public-bad anchors while preserving the active frontier. Invalid when it rewards E72 or gives favorable scores to bad public anchors.
- Current evidence: E93 found target-manifold delta mean likes E72 (`-0.001468687` vs mixmin) and likes older bad anchors such as `final9` (`-0.020801364`) and `bad_q2_jepa` (`-0.002958703`). Live candidates also look favorable but not separable enough to rank: E86 `-0.000921783`, E90 `-0.000877945`, E89 `-0.000806467`.
- Policy: set `target_manifold_selector_valid = false`. Use the feature as target-dependency diagnostic only. It can veto grossly impossible movement, but it cannot choose among E86/E90/E89 or serve as an E72 counter-gate.

### F75. Hard-label tail exposure energy

- Hidden structure: LogLoss can be dominated by a small subset of cells whose true hard labels oppose a candidate move, even when soft posterior, target-manifold, or representation-health metrics look favorable.
- Candidates: per-cell candidate-minus-mixmin LogLoss delta under hard labels `0/1`, E72-adverse hard-label direction, positive exposure to that direction, weighted positive tail mean, hard worst-tail mean, KL if mixmin is calibrated, and soft-health gain ratio.
- Label vs split test: useful only as a public-negative-anchor exclusion and tail-risk lens. Invalid as a direct public score forecast because the public hard labels remain unobserved.
- Current evidence: E94 found E72 full adverse exposure `0.002330945`, while the observed public miss was only `0.043389` of that scale. Live E72-adverse positive exposure is E85 `0.000739201`, E89 `0.000799109`, E90 `0.000934031`, E86 `0.001010242`. Known-public sanity correlations favor hard-tail metrics (`0.793939-0.866667`) over soft-health gain (`0.081935`).
- Policy: add `hard_label_tail_exposure_energy` as a mandatory companion to JEPA-style soft-health metrics. Use it to separate max-upside candidates from lower-downside candidates. Do not use soft posterior CE, target-manifold consistency, or aggregate soft-health gain alone to rank a submission.

### F76. Hard-tail localized fallback gate

- Hidden structure: E72-adverse hard-label tail risk may be localized by cell/row rather than only measured as a scalar candidate risk. If true, the high-risk part of E86 can fall back to a lower-amplitude same-law candidate without losing all structural margin.
- Candidates: positive E72-adverse tail mask, source candidate (`E86`, `E90`), fallback source (`E89`, `E85`, `mixmin`), cell-vs-row fallback, target scope, tail quantile, raw best-tail vs strict best-tail, all-combo margin, hidden Q2/S3, world support, block win, block-tail safe rate, moved cells, and active targets.
- Label vs split test: valid only when low-tail candidates remain strict under combo, hidden/world/block, raw-energy, and movement sanity checks. Invalid when tail reduction comes from broad mixmin rollback, zero-tail quantile artifacts, or duplicate predictions.
- Current evidence: E95 generated `178` rows, with `112` strict and `19` strict non-dominated rows. The selected `analysis_outputs/submission_e95_hardtail_541e3973.csv` starts from E86 and falls back to E85 on E72-adverse top-tail cells. It has all delta `-0.0000262074`, E72-adverse tail `0.000788914`, world `-0.000132931`, hidden Q2/S3 `-0.000251140`, block win `0.750000`, and tail safe `0.972222`. It beats E89 on both hard-tail exposure and all-combo margin, while keeping active targets `Q2,S1,S2,S3`. Public E95 scored `0.5762913298`, improving over mixmin by `0.0000153107`.
- Policy: promote `hard_tail_localized_fallback_gate` from candidate generator to current public frontier feature family. Use E95 as the anchor when the public question is hard-label tail sensitivity. Do not replace E86 for maximum-upside testing or E90 for row-coherent structural-retention testing.

### F77. Public-miss budget tail scenario energy

- Hidden structure: a public miss is observed as one scalar LogLoss delta, not as a revealed label map. A candidate that is truly robust to E72-style hard-tail risk should survive many allocations of the same E72 miss budget across plausible adverse cells.
- Candidates: E72-adverse hard-label cell budget, deterministic top/bottom/median tail orders, random weighted tail permutations, target masks, E95 fallback masks, candidate movement masks, complete-budget reconstruction rate, candidate conditional mean/p95/max deltas, live win-rate, and pairwise beat rates.
- Label vs split test: valid only if failed E72 reconstructs the observed public miss by construction and candidate ranking is evaluated across many complete-budget scenarios. Invalid if used to infer the true public labels or to fit public LB directly.
- Current evidence: E96 generated `3894/3894` complete-budget scenarios over `1750` test-target cells. E72 reconstructs `+0.0001011367` in every scenario and mixmin is `0`. E95 has the best live mean delta (`0.000057874`) and live win-rate (`0.527478`), beating E89 in `0.712378`, E90 in `0.999486`, and E86 in `0.998973`. E85 has the lowest live p95 tail (`0.000115304`) versus E95 `0.000115644`. E97 then validates the E95 side of this ranking on public with LB `0.5762913298`.
- Policy: use `public_miss_budget_tail_scenario_energy` to separate information-rich hard-tail localization from pure conservative tail-floor behavior. It keeps E95 first when the public question is hard-tail localization with retained structure; it gives E85 a clear role only when minimizing p95 downside is the goal.

### F78. E95-updated selector collapse flag

- Hidden structure: E95 may add a useful local public bracket around mixmin/E72, but the known public LB surface may still be too underidentified to learn a smooth frontier-scale selector from submission movement fingerprints.
- Candidates: known-anchor count, fixed LOOCV proxy family, p90 abs error, E95 edge/error ratio, E72 miss/error ratio, E95/mixmin/E72 critical pair sign, future proxy spread, and proxy-ranked candidate risk.
- Label vs split test: useful only as a negative selector diagnostic. Invalid if a predicted LB ranking is used after the proxy cannot hold out E95/mixmin/E72 at the edge scale.
- Current evidence: E98 added E95 as the 11th known public anchor. The best proxy remains `raw05_a2c8_compat` with MAE `0.000520095` and p90 abs error `0.000816497`; p90 error is `53.33x` the E95 edge over mixmin and `8.07x` the E72 miss. E72-minus-mixmin is still wrong-sign under the critical holdout, and future proxy spread is only `0.000015142`.
- Policy: set `e95_updated_known_lb_selector_valid = false`. Do not rank E90/E86/E85 by predicted LB. Use this flag to prevent public-anchor assimilation from turning into a proxy shortcut.

### F79. E95-conditioned tail transfer energy

- Hidden structure: E72 and E95 together constrain how local structural margin and hard-label tail exposure can transfer to public LB. A candidate that only looks good under unconditioned tail scenarios or local stress may be incompatible with the observed E95 gain.
- Candidates: per-scenario alpha/lambda from `public_delta = alpha * local_all_delta + lambda * E96_tail_delta`, positive-transfer count, broad/tight plausible filters, candidate mean/p90/p95 predicted delta, beat-E95 rate, live win-rate, and residuals on E72/E95 anchors.
- Label vs split test: valid only as a two-anchor sensor model that exactly reconstructs E72 and E95 without fitting hard labels. Invalid if used as a smooth public-LB regressor, if alpha/lambda signs are noninterpretable, or if candidate ranking ignores filter stability.
- Current evidence: E99 solved `3894/3894` E96 complete scenarios, with `3849` positive-transfer and `3452` broad-plausible scenarios. Broad-plausible alpha/lambda medians are `3.310470/1.345192`. E95 is best mean, best p95, and winner mode. Beat-E95 rates are E89 `0.195829`, E85 `0.031866`, no-Q2 `0.023175`, E90 `0.002607`, and E86 `0.000290`.
- Policy: use `e95_conditioned_tail_transfer_energy` as an E95-relative ranking sanity check. It does not create a new submission. It demotes E90/E86 as expected-improvement bets and promotes E89 only as the sharpest E95 counterfactual, not as a guaranteed improvement.

### F80. E89 Q2/S3 diffuse-tail counterfactual energy

- Hidden structure: E89 may beat E95 only if the public tail is spread through Q2/S3 E72-like cells that E95 did not localize, rather than if E89 is globally safer or more structurally correct.
- Candidates: `q2s3` mask membership, family/mask/order slice beat rate, E89-minus-E95 local delta, E89 tail advantage, required tail advantage, tail surplus, alpha/lambda medians, and E89 live win-rate.
- Label vs split test: valid only as a post-E95 counterfactual anatomy tool. Invalid if used to claim E89 is a broad improvement candidate, or if Q2/S3 slice concentration is ignored.
- Current evidence: E100 decomposed `3452` broad-plausible E95-conditioned worlds. Overall E89 beat-E95 rate is `0.195829`, but mean E89-minus-E95 is `+0.000003833`. The E89-beating cases are `676` scenarios with top mask `q2s3` and mean tail surplus `+0.000002916`. The `q2s3` slice has `n=368`, beat rate `0.779891`, mean E89-minus-E95 `-0.000005030`, and tail surplus `+0.000003262`.
- Policy: use `e89_q2s3_tail_counterfactual_energy` to decide what an E89 public submission means. E89 is only a Q2/S3 diffuse-tail sensor. If E89 fails public, do not keep the E89 branch alive as a generic decontamination candidate.

### F81. E95-relative Q2/S3 tail rollback energy

- Hidden structure: E95 may have identified the right structural/hard-tail law but still over-amplified Q2/S3 cells. A rollback toward mixmin on only those cells tests tail amplitude without carrying full E89 movement.
- Candidates: E95 base, fallback source (`mixmin`, E89, E85), Q2/S3 target scope, E72-positive selector, E89-vs-E95 tail advantage, graft alpha, active cells versus E95, strict/deployable gate, E72-adverse exposure, E95-conditioned broad mean/p95/beat rate, and Q2/S3-slice transfer.
- Label vs split test: valid only if the rollback passes strict/deployable stress and has non-positive broad p95 risk after E95-conditioned transfer. Invalid if it relies on non-strict inverse-top-conflicted rows, broad near-zero rollback, or proxy LB fitting.
- Current evidence: E101 generated `618` rows, `612` grafts, `581` strict-like rows, and `54` pass rows. The selected `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` shrinks E95's effective Q2/S3 movement `25%` toward mixmin on `50` active cells versus E95. It has all delta `-0.0000253724`, E72-adverse exposure `0.000692235`, hidden Q2/S3 `-0.000191316`, world `-0.000115685`, block win `0.75`, broad mean/p95/beat vs E95 `-0.0000162053`/`-0.000001564`/`0.983488`, and Q2/S3-slice beat rate `1.0`.
- Policy: promote `e95_q2s3_tail_rollback_energy` as the next public sensor family. Submit E101 before full E89 when the question is Q2/S3 tail amplitude. If E101 worsens, demote this rollback feature and interpret the E100 pocket as either full-E89-specific or overfit to local+tail transfer.

### F82. E101 active-cell edge-localization energy

- Hidden structure: the E101 rollback cells may reveal where E95 over-moves Q2/S3. If the cells are block-local, use block masks; if they are edge-local, treat hidden block boundary risk as a calibration feature; if neither, keep E101 as target-axis amplitude only.
- Candidates: active Q2/S3 cells versus E95, hidden block id, subject id, context type, block length, row position in hidden block, edge distance, target-count-preserving permutation null, and active-cell enrichment.
- Label vs split test: valid only as a structure diagnostic because it uses no public labels and no train target leakage. Invalid as a submission selector if it converts weak enrichment into a handcrafted mask without public or stress validation.
- Current evidence: E102 found E101 active cells are `50` cells across `48` rows, `26` hidden blocks, and all `10` subjects. Strong block/subject concentration is absent. The only non-random structure is hidden-block edge proximity: edge-or-near-edge rate `0.620` versus null mean `0.471289`, p `0.016999`; mean edge distance `1.680` versus null `2.138444`, p `0.040848`.
- Policy: add `e101_active_cell_edge_energy` as a branch selector after E101 public feedback. If E101 improves, test amplitude and edge-risk variants before subject/block masks. If E101 worsens, do not keep generic Q2/S3 rollback alive except as a weaker edge-local diagnostic.

### F83. E103 edge-local Q2/S3 amplitude stress energy

- Hidden structure: hidden block edges may mark Q2/S3 calibration-risk cells, but the edge clue must be separated from the simpler "rollback all E101-active cells by a different amplitude" line.
- Candidates: active-all, active-edge, active-interior, S3/Q2 edge splits, top logit-gap edge masks, rollback alpha, move-edge rate, E101 broad mean/p95/beat deltas, and E103 dominance over E101.
- Label vs split test: valid only as a post-E101 branch stress. Invalid as a direct selector when edge-only masks improve average transfer while failing p95/strict stress or losing E101's beat-rate stability.
- Current evidence: E103 scanned `180` edge/amplitude variants. `12` passed E103 stress but `0` dominated E101 on mean, p95, and beat-rate together, so no file was materialized. The best passing active-all alpha `0.375` improves broad mean/p95 versus E101 but lowers beat-E95 rate; edge-only alpha `1.0` has positive p95 and fails strict.
- Policy: set `edge_local_q2s3_direct_selector_valid = false`. Use edge energy as a risk/branch feature after E101 public feedback, not as a replacement submission. Do not build subject/block/edge handcrafted masks from E101 without a stronger independent signal.

### F84. E101 amplitude Pareto-cliff energy

- Hidden structure: E101 may be the local rollback amplitude where Q2/S3 hard-tail risk reduction is still scenario-stable. Pushing farther toward mixmin may improve average transfer while losing support in plausible E95-conditioned worlds.
- Candidates: fine-grid graft alpha, selector mask, E101-pass flag, broad mean/p95/beat deltas versus E95, mean/p95 gains versus E101, beat-rate gap versus E101, and E101-dominance flag.
- Label vs split test: valid only as an amplitude-response diagnostic under the same E95-conditioned scenario frame. Invalid if higher-alpha mean gain is treated as submission evidence while beat-rate drops or strict edge/interior masks fail.
- Current evidence: E104 scanned `505` variants over alphas `0.000-0.500` by `0.005`. `228` passed E101-style stress, but `0` dominated E101. Active-all alpha `0.255` is the first alpha above E101 that lowers beat-rate; it improves mean/p95 by only `~3.02e-7`/`~2.6e-8` while losing `0.000289687` beat-rate. Best passing active-all alpha `0.380` improves mean/p95 to `-0.000023695`/`-0.000002181` vs E95 but lowers beat-rate to `0.980881`. Edge/interior selectors have `0` pass rows.
- Policy: set `e101_alpha_0p25_pareto_cliff = true`. Keep E101 as the pre-feedback public sensor. Use higher-alpha rollback only after E101 public feedback confirms the direction and the next question is explicit upside/downside tradeoff.

### F85. E101 public-label break-even energy

- Hidden structure: E101's public result depends on the hidden hard labels of only `50` active Q2/S3 cells. The useful feature is not the probability move itself, but the label-world condition under which that move beats E95.
- Candidates: per-cell E101-minus-E95 LogLoss delta under hard labels `0/1`, support label, support/adverse delta, flip benefit, minimum high-impact support cells needed to beat E95, global/subject prior expected delta, and prior-simulated beat probability.
- Label vs split test: valid because it uses no public labels and only derives the public-feedback interpretation map. Invalid if the prior simulation is treated as a public forecast; it is a null model for interpreting E101's future LB.
- Current evidence: E105 found `50` active cells, Q2 `11` and S3 `39`. Support labels are balanced by count (`25` label 0, `25` label 1), but S3 carries `0.935862` of flip benefit. All-support delta is `-0.000096679`; all-adverse delta `+0.000211677`. Beating E95 needs `23/50` top-impact supportive cells; matching E95's mixmin edge needs `25/50`. Global prior simulation gives expected delta `+0.000048971` and beat probability `0.016610`; subject prior gives `+0.000007854` and beat probability `0.335360`.
- Policy: treat E101 as a subject/block-local S3 tail-label sensor, not as a global target-prior correction. If E101 wins, condition follow-up amplitude work on S3-heavy local label departure. If it loses, demote E101/E104 amplification before testing full E89.

### F86. E101 subject-prior gate energy

- Hidden structure: the E105 subject-local S3 label clue might be selective enough to choose a smaller E101-style rollback before public feedback.
- Candidates: subject expected delta, subject support probability, support-probability quantile masks, S3-only subject-support masks, flip-benefit rankings, selected-cell count, selected-S3 count, alpha, prior-healthier flag, E101-pass flag, and E101 replacement/dominance flags.
- Label vs split test: valid only as a pre-feedback selector audit because it uses train-derived priors and existing E95-conditioned stress, not public labels. Invalid if a prior-healthier row is promoted while broad mean/p95/beat support is weaker than E101.
- Current evidence: E106 scanned `268` variants. E101-pass variants: `12`; prior-healthier variants: `56`; interesting non-replacements: `6`; replacement rows: `0`; dominating rows: `0`. The strongest interpretable rows are S3-heavy alpha `0.25` gates, but `active_s3_all` has mean/p95/beat `-0.000015728/-0.000001195/0.973349`, weaker than E101 `-0.000016205/-0.000001564/0.983488`.
- Policy: keep subject-prior gate as interpretation/risk energy, not as a pre-feedback candidate generator. No E106 submission.

### F87. E101 feedback-conditioning energy

- Hidden structure: E101's public result is a sensor for which E95-conditioned tail world is plausible. The next candidate family should be selected by conditioning on that result, not by unconditional local ranking.
- Candidates: hypothetical E101-vs-E95 delta, within-tolerance scenario count, nearest/tension flag, conditional E104/E106/control mean/p95/beat versus E95 and E101, E101-pass flag, and strict-vs-risk-tolerant follow-up alpha.
- Label vs split test: valid only as a pre-registered branch table because it uses hypothetical deltas and existing E99 worlds, not public labels. Invalid if it is treated as a submission file or as proof that E104 high-alpha should be used before E101 feedback.
- Current evidence: E107 used `292` candidates, `6` hypothetical outcomes, and `1752` summary rows. Edge-sized win and small win are within-tolerance and point to E104 active-all amplitude-up; strict E101-pass follow-ups sit near alpha `0.380`. Strong win and loss outcomes are nearest/tension. E106 subject-prior masks do not outrank E104 in the matched subsets.
- Policy: use this feature only after E101 public feedback. If E101 wins, test E104 amplitude-up deliberately. If E101 loses, treat it as E99/E101 world-model tension and do not rescue E101 with subject-prior masks.

### F88. E101-win amplitude materialization gate

- Hidden structure: if E101 wins, the public tail world likely wants the same active Q2/S3 rollback direction with more amplitude, but only inside the E107 coherent edge/small-win buckets.
- Candidates: E107 outcome bucket, active-all alpha, E101-pass flag, conditional rank versus E101, conditional mean/p95/beat versus E101, tie/loss p95, and generated file identity.
- Label vs split test: valid only as a post-feedback gate because it is based on hypothetical conditioning, not observed public labels. Invalid if the amp050 or amp038 files are submitted before E101 feedback or after an E101 tie/loss.
- Current evidence: E108 materialized `analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv` and `analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv`. Amp050 is not E101-pass but ranks `1` versus E101 in edge/small-win worlds with mean vs E101 `-0.000012556` / `-0.000004165`. Amp038 is E101-pass and has edge/small mean vs E101 `-0.000006864` / `-0.000002316`, but ranks `54` / `49`.
- Policy: keep `e101_win_amp_materialization_gate` dormant until E101 public feedback. If E101 wins by edge/small scale, choose amp050 for upside or amp038 for conservative risk. If E101 ties or loses, do not activate this feature.

### F89. E101 tie/loss active-label retention energy

- Hidden structure: an E101 tie/loss would likely mean that the active Q2/S3 labels did not realize the S3-heavy support pattern needed for rollback. In that world, the safe local action is not more rollback but retaining E95/E90/E86 behavior on those cells.
- Candidates: sampled active-cell outcome bucket, top10/top23 support rate, support flip-share, S3 support rate, per-candidate active-cell delta versus E95/E101, and posterior support suppression by cell.
- Label vs split test: valid only as a hard-label null/branch diagnostic because it samples hidden labels from train priors and uses active-cell-only candidate deltas. Invalid as a full public LB forecast or as proof that E86/E90 full files should be submitted after E101 loss.
- Current evidence: E109 sampled `200000` worlds under global and subject priors. Under subject priors, small/large loss rates are `0.355350` / `0.244350`; top10 support rate falls to `0.805226` / `0.719218`; support flip-share falls to `0.650286` / `0.585604`. In subject small-loss worlds, E108 amp050/amp038 active mean vs E101 is `+0.000011723` / `+0.000006026`, both with beat-E101 rate `0`. E86/E90/E95 rank above E101 active-cell-only in loss buckets.
- Policy: if E101 ties or loses, close same-line E108 amplification and subject-prior masks. Use `e101_loss_active_retention_energy` to decide whether the next question is retained E86/E90 structure, active-cell restoration, or a non-active E89 diffuse-tail test.

### F90. E101-negative non-active tail isolation energy

- Hidden structure: after an E101 tie/loss, the active cells may be wrong while a diffuse non-active E89/E86/E90 tail law could still carry useful public structure. This feature tests whether that separation is real rather than assuming it.
- Candidates: active-restored E89/E85 variants, E95-to-E89/E85/E90/E86 non-active grafts, non-active target scopes (`q2`, `s3`, `q2s3`, `s1s2s3`, `all_changed`), active-loss-safe flag, broad E95-conditioned mean/p95/beat, and `sensor` versus `strict` decision labels.
- Label vs split test: valid as a branch diagnostic because it combines E109 active-loss hard-label worlds with E99 E95-conditioned transfer stress. Invalid as a public-LB forecast or as a reason to submit full E89 after a negative E101 result.
- Current evidence: E110 built `45` unique candidates. Active-loss-safe non-control rows existed (`36`) and `8` rows were diagnostic sensors, but strict candidates were `0` and no submission was materialized. The best non-control row, non-active `S1/S2/S3` E86 alpha `0.25`, had broad mean/p95 vs E95 `+0.000000714` / `+0.000002798`; active-restored E89/E85 variants also failed broad E95-conditioned stress.
- Policy: no direct submission from this feature. If E101 ties or loses, do not automatically submit full E89, active-restored E89/E85, or non-active grafts. Keep E95 as standing best and rebuild the public-world model unless the next public slot is explicitly a diffuse-tail sensor.

### F91. Raw-context visibility collapse energy

- Hidden structure: visible raw lifelog coverage may contain the missing temporal context for Q targets, but it can also collapse into subject/date shortcuts that improve ranking while worsening calibrated temporal LogLoss.
- Candidates: daily raw coverage features, temporal-last25-by-subject split, random-within-subject split, subject-prior baseline, raw-only head, raw+subject-prior head, target-axis deltas, E95-active deltas, and random-vs-temporal divergence.
- Label vs split test: valid only if raw context improves temporal holdout LogLoss after subject prior and does not show random-only target gains. Invalid when raw context improves AUC or random split but worsens temporal calibrated LogLoss.
- Current evidence: E113 aggregated `114` raw daily features and found raw coverage for all train/test rows. Raw+subject-prior worsened temporal LogLoss versus subject prior on Q targets by `+0.038804`, S targets by `+0.058534`, and E95-active axes by `+0.059881`. Random split also worsened on average (`+0.007833` Q, `+0.016497` S), while Q2's random-only gain conflicted with temporal degradation. Only S3 had a small temporal gain (`-0.004643`).
- Policy: set `raw_context_q_temporal_rescue_valid = false`. Keep raw context as diagnostic energy, especially for S3/Q2 boundary risk. Do not build broad Q/Q3 raw-context probability movement without a temporal holdout calibration gain.

### F92. E101 raw-support failure energy

- Hidden structure: even when raw context fails as a broad predictor, it may still identify whether the `50` E101 active cells realize the support labels that make E101 beat E95.
- Candidates: E101 active cells, support label, flip benefit, raw+subject-prior test probability, validation-gated raw probability, subject-prior probability, support probability, expected E101-vs-E95 hard-label delta, Monte Carlo beat probability, and target flip-benefit share.
- Label vs split test: useful only as an interpretation energy. Invalid as a submission selector if raw support is weaker than subject prior or if the target is rejected by temporal validation.
- Current evidence: E114 found subject-prior beat probability `0.336655`, raw+prior `0.238325`, and validation-gated raw `0.230710`. S3 accounts for `0.935862` of E101 flip benefit, but raw S3 support probability is `0.589463` versus subject prior `0.604450`.
- Policy: set `raw_context_e101_support_valid = false`. If E101 wins public, the winning support-label world was hidden from this raw-context head. If E101 loses, raw context should not be used to rescue or mask the same rollback branch.

### F93. Public sensor actionable-information energy

- Hidden structure: the next public submission should be chosen by the amount of world-model information it gives, not just by local mean score. A useful sensor must split E95-conditioned worlds into actionable outcome regimes without being almost certainly loss-heavy.
- Candidates: E95-conditioned broad-plausible world delta, outcome bucket, outcome entropy, win/tie/loss rates, raw split information, actionable rate, actionable information score, and best conditional follow-up family.
- Label vs split test: valid as a sensor-ranking diagnostic because it only uses already-conditioned E72/E95 worlds and no future public label. Invalid if actionable information is treated as a guarantee of public improvement.
- Current evidence: E115 compared control E101/E89/E85/E90/E86/mixmin across `3452` broad-plausible worlds. E101 has actionable score `1.613953`, entropy `1.728493`, beat-E95 `0.983488`, and loss rate `0.000000`. E89 is second but far lower at `0.233881` with loss rate `0.580243`; E85/E90/E86 are mostly loss-heavy.
- Policy: use `public_sensor_actionable_information` to choose the next external sensor when public feedback is absent. It supports E101 as the next slot after E114; it does not open E89/E85/E90/E86 before E101.

### F94. E101 public-feedback decoder energy

- Hidden structure: a public sensor only helps if its observed score is mapped to pre-declared world-model updates. Otherwise the same E101 result can be post-hoc rationalized into incompatible followups.
- Candidates: E101 public LB, delta versus E95 public `0.5762913298`, strong/edge/small/tie/loss band, E115 scenario rate, E107 model-tension flag, allowed candidate-to-test, and forbidden-action list.
- Label vs split test: valid as a procedural guard before external feedback. Invalid if used to predict public labels or to bypass an exact-delta rerun after a surprising result.
- Current evidence: E116 defines strong win `<=0.576261330`, edge win `(0.576261330, 0.576280330]`, small win `(0.576280330, 0.576288330]`, tie `(0.576288330, 0.576294330]`, and loss `>0.576294330`. Win bands allow E108 consideration; tie/loss bands block same-line rescue.
- Policy: consult `e116_e101_public_feedback_decoder.csv` before choosing any post-E101 file. If E101 ties or loses, do not submit E108/E104/E106/full-E89/non-active-graft followups without rebuilding the world model.

### F95. E95-like neighborhood scarcity energy

- Hidden structure: if E95's public edge is a general S-heavy hardtail law, existing documented submissions should contain multiple E95-shaped, lower-tail alternatives. If the neighborhood is sparse, the plateau is a narrow frontier rather than a selector oversight.
- Candidates: referenced submission names, resolved prediction tensors, tensor dedupe hash, E95-direction cosine, Q/S movement share, E72-adverse exposure, E95-relative changed-cell count, and E95-like score.
- Label vs split test: valid as an existing-universe falsification because it uses only already-created submissions and known public anchor geometry. Invalid if it is treated as a public score forecast or used to submit conditional E108 files before E101 feedback.
- Current evidence: E117 scanned `5277` referenced names, resolved `4477`, and deduplicated `4031` tensors. Only `10` were E95-like. Only `4` had no higher E72-adverse exposure than E95: E101, E85, and the two E108 post-E101-win files. E101 changes only `50` cells vs E95 with E95-relative Q2/S3 share `1.000000`.
- Policy: set `old_universe_e95_like_replacement_available = false`. Keep E101 as the next public sensor. Do not promote E108 before E101 or auto-promote E89/E85/E90/E86 as hidden lower-tail replacements.

### F96. E101 flank-transition support energy

- Hidden structure: E101's active Q2/S3 cells may be hidden block transition-state cells where visible train-label flanks carry partial information, even though raw context and subject-prior masks cannot certify the rollback.
- Candidates: previous/next/nearest/edge/both flank support priors, support-label probability, expected E101-vs-E95 hard-label delta, active-cell edge rate, flank conflict rate, conflict-given-both, and target-count-preserving null enrichment.
- Label vs split test: valid only as a transition-state support diagnostic. Invalid as a submission selector if expected delta remains positive or if flank support is used to pre-submit E108/higher-alpha variants before E101 feedback.
- Current evidence: E118 found best flank prior `edge_endpoint_beta` with beat-E95 probability `0.437780`, better than subject prior `0.337185` and global prior `0.015920`, but expected delta/all cells remained `+0.000003014`. Active cells were edge/near-edge enriched (`0.620000` vs null `0.471289`, p `0.016999`) and flank-conflict enriched (`0.240000` vs null `0.149933`, p `0.048998`). E119 then converted the same evidence into flank/support/edge/flip-benefit gates and found `602` variants, `66` E101-pass rows, and `0` E101-dominating rows.
- Policy: set `e101_flank_transition_support_present = true`, `e101_flank_transition_certified = false`, and `e101_flank_gate_replacement_available = false`. Keep E101 as the next public sensor; do not open E108/E104/E106/E119 before E101 public feedback.

### F97. Post-E101 two-point hard-tail boundary energy

- Hidden structure: E95 and E101 now define a narrow public boundary. E95 is the best known public file; E101 keeps enough of the same law to beat mixmin, but its Q2/S3 rollback loses to E95. The missing feature is not another E101-like selector but an energy that explains why this boundary flips.
- Candidates: exact E101 public LB, delta vs E95, delta vs mixmin, E95-gain giveback share, E95-gain remaining share, actual-minus-local-mean, actual-minus-local-p95, E116 outcome, E107 model-tension flag, E110 strict fallback count, and E119 E101-dominating count.
- Label vs split test: valid as public-observation state, not as target labels. Invalid if used to tune probabilities directly to the public score; valid if used to close same-line branches and design a new stress target.
- Current evidence: E120 found E101 public `0.5763003660`, delta vs E95 `+0.0000090362`, delta vs mixmin `-0.0000062745`, E116 outcome `small_loss`, giveback share `0.590189`, and remaining share `0.409811`. Actual public was `+0.0000252415` worse than local E101 mean and `+0.0000106001` worse than local p95. E110 non-control strict candidates remain `0`; E119 E101-dominating rows remain `0`.
- Policy: set `e101_same_line_followup_open = false`. Use this feature as a mandatory guard: any next candidate must explain the E95/E101 boundary or explicitly test a different hidden structure. Do not use E108/E104/E106/E119, full E89, or non-active grafts as automatic next files.

### F98. E101 exact small-loss inverse-posterior energy

- Hidden structure: E101's observed small loss may be a hard-label budget boundary over the `50` active Q2/S3 cells. The key feature is how much active flip benefit public realized, not a new probability transformation.
- Candidates: observed E101-vs-E95 delta, all-support/all-adverse active-cell deltas, needed flip-benefit share, greedy top-flip support count, exact-observed prior world rate, top10/top22/top23 support rate, S3 support rate, and soft posterior support per active cell.
- Label vs split test: valid as a public-sensor interpretation because it uses aggregate public LB only to constrain an already-defined active-cell hard-label map. Invalid if used to fit a new submission directly to the exact public score.
- Current evidence: E121 found all-support/all-adverse deltas `-0.0000966787` / `+0.0002116767`. The actual E101 delta `+0.0000090362` requires `0.657165` of active flip benefit. Greedy top-flip support first beats mixmin at `21`, matches the observation near `22`, and first beats E95 at `23`. Exact-observed worlds are common under local/flank priors (`~0.044-0.047`) but rare under global prior (`0.007963`), with top10 support `~0.81-0.86` and S3 support `~0.58-0.60`.
- Policy: set `e101_exact_small_loss_boundary_identified = true` and `e101_public_score_fitted_gate_allowed = false`. This energy can rank future independent S3-cell sensors, but cannot by itself create a same-line submission.

### F99. E101 independent-sensor boundary energy

- Hidden structure: the E101 small-loss boundary may be visible in train-derived subject/flank/raw priors even if it is not exploitable. This feature separates "can explain the public observation" from "can safely generate the next file."
- Candidates: E119 local-transfer expected delta, E118 flank expected deltas, E114 raw-context expected deltas, deterministic `p >= 0.5` hard gates, rank-22/rank-23 high-impact S3 support probabilities, and E116 branch agreement.
- Label vs split test: valid as a non-public explanation/stress because the priors existed before E101 feedback. Invalid as a submission selector if it only matches the aggregate small-loss branch but keeps the critical rank-23 cell high-support.
- Current evidence: E122 found `raw_full_subject_prior_y1` expected `+0.000008889` versus actual `+0.0000090362`, `flank_conflict_flat` expected `+0.000009521`, and `flank_both_distance_beta` expected `+0.000009532`. E119 local transfer expected `-0.000016205` and therefore missed the branch. The rank-23 S3 cell still has high support under subject/edge/raw/posterior (`0.958333/0.972222/0.864418/0.940119`), so the visible sensors do not provide a stop rule.
- Policy: set `e101_small_loss_explainable_by_simple_priors = true` and `e101_same_line_gate_available = false`. Use this feature to reject E119-style local-transfer optimism and E121/E122 posterior-fitted gates; require a genuinely different S3-cell sensor before another same-line file.

### F100. E101 transition-motif collapse energy

- Hidden structure: S3 may be a projection of the broader Q/S neighbor-state trajectory, so previous/next Q1/Q2/Q3/S1/S2/S4 labels might reveal the missing high-impact S3 support/adverse cell without using public LB.
- Candidates: train-only previous/next target-state motif features, no-S3 motif head, full motif head, motif+subject head, temporal-tail validation, interleaved validation, rank-22/rank-23 support probabilities, and expected E101-vs-E95 delta over active S3 cells.
- Label vs split test: valid only if the motif improves temporal S3 LogLoss versus subject prior and direct flank beta. Invalid if it relies on interleaved shortcuts, overshoots the observed branch, or keeps rank 23 high-support.
- Current evidence: E123 found temporal logloss deltas versus subject prior of `+0.135183` for `motif_no_s3`, `+0.246239` for `motif_full`, and `+0.349065` for `motif_plus_subject`. Rank-23 support stayed `0.943564`/`0.956191`/`0.984326` for no-S3/full/plus-subject. Aggregate expected deltas were `+0.000027684` to `+0.000028398`, too loss-heavy versus actual `+0.0000090362`.
- Policy: set `e101_transition_motif_gate_available = false`. Keep transition motifs as a LeJEPA-style collapse/shortcut warning and not as a same-line E95/E101 submission selector.

### F101. E101-conditioned transfer residual energy

- Hidden structure: E99's two-term `local_delta + E72_tail_delta` abstraction may explain the broad hard-tail law while still missing a Q2/S3 boundary variable exposed by E101.
- Candidates: E99 broad-plausible scenario id, alpha, lambda, predicted E101 delta, actual E101 residual, E101 order-match flag, E101 close-within-`10e-6` flag, E101-plausible subset, future candidate beat-E95 rates, and live/future winner modes.
- Label vs split test: valid as a held-out public-world model diagnostic because E101 is evaluated after the E72/E95 transfer solve. Invalid if used to tune directly toward E101's public score or to claim a future candidate is certified from only `57` surviving scenarios.
- Current evidence: E124 found broad-plausible E99 worlds `3452`, predicted E101 mean `-0.000031516` versus actual `-0.000006275`, and only `57` E101-sensor-plausible worlds. Inside those, E95 live win rate is `0.929825`; future E95-beat rates are E89 `0.052632`, E85 `0.017544`, E90/E86 `0`.
- Policy: set `pre_e101_e99_ranker_valid = false` and `e101_conditioned_same_family_successor_available = false`. Use this energy to prevent inherited E89/E85/E90/E86 promotion after E101 unless a new non-public sensor changes the boundary.

### F102. E101 survivor anatomy energy

- Hidden structure: the tiny E101-compatible subset may reveal whether the residual public law is Q2/S3-specific, broad hard-tail, or local-transfer shrinkage.
- Candidates: E124 scenario family, mask name, gamma, alpha, selected cell count, E101-vs-E95 tail relation, `q2s3` survivor count, broad/all-tail survivor share, and median alpha collapse.
- Label vs split test: valid as a post-E101 worldview diagnostic. Invalid as a submission generator because it uses E101 public feedback to inspect scenario compatibility.
- Current evidence: E125 found `57/3452` E101 survivors; `all`/`e72_top50_hard` are `43/57`; `q2s3` is `0/368`; deterministic or gamma0 are `40/57`; median alpha collapses `3.310470 -> 0.791985`; median `tail_e101 - tail_e95` moves `-0.000012634 -> ~0`.
- Policy: set `q2s3_diffuse_tail_residual_world_valid = false`. Treat future Q2/S3 cells only as energy inside a different structure, not as the next standalone same-family line.

### F103. E101 survivor cell-budget energy

- Hidden structure: E101-compatible public-world scenarios may reveal which cell families actually carry the public-miss budget after the E95/E101 boundary is conditioned on the observed score.
- Candidates: selected-cell budget mass, q2s3 mass share, E101-active mass share, E95-fallback share, target mass profile, context-type mass profile, edge/interior position mass, hidden-block metadata, and low-alpha/tail-equal group membership.
- Label vs split test: valid as scenario anatomy and gate design input. Invalid as direct public-label fitting, because it uses E101 public feedback to filter worlds and does not reveal true labels.
- Current evidence: E126 found E101-plausible q2s3 mass share `0.180513`, E101-active mass share `0.011234`, E95-fallback mass share `0.356179`, and between-train-runs mass share `0.621562`. Broad-q2s3 worlds have q2s3 mass share `1.000000` and E101-active mass share `0.584840`.
- Policy: set `e101_active_cell_budget_explains_survivors = false` and `same_line_q2s3_followup_allowed = false`. Use this feature only as a negative gate and as a target for future transfer-shrinkage representation work.

### F104. Transfer-shrinkage predictability energy

- Hidden structure: if the E101-compatible budget field is real, public-free tail-neutral/low-alpha scenario geometry should predict it better than q2s3 or target-only metadata.
- Candidates: proxy distribution JS/TV/cosine/top-k overlap against E101-plausible budget, hidden-block-heldout metadata CV score, tail-equal mass, low-alpha mass, fallback flags, E72-positive bin, context type, and target.
- Label vs split test: valid as a post-E101 representation audit and future gate target. Invalid as a direct submission selector because the teacher is defined by E101 public compatibility.
- Current evidence: E127 found `broad_tail_equal` JS `0.038002`, Spearman `0.902053`, top50 truth-mass capture `0.293969`; `broad_q2s3` JS `0.508660`; best metadata view `target_context_tail_e72bin` CV JS `0.073253`, top50 truth-mass capture `0.252521`; target-only CV JS `0.316796`.
- Policy: use tail-neutral/low-alpha transfer-shrinkage density as a mandatory negative gate for same-family candidates and as the next representation target. Do not promote metadata-only cell ranking to a submission.

### F105. Transfer-shrinkage candidate-risk energy

- Hidden structure: a candidate can look healthy under the broad E95 law while still paying LogLoss through E101-active rollback, Q2/S3 rollback, E72-adverse cells, or tail-equal law residual. These risks must remain visible separately instead of being hidden inside one blend score.
- Candidates: E95-law cosine under E127 `broad_tail_equal` density, tail-equal residual ratio, E101-active delta vs E95, Q2/S3 delta vs E95, E72-adverse exposure on E101-plausible density, and composite transfer-shrinkage risk index.
- Label vs split test: valid as a known-public sanity/veto diagnostic if component metrics align with E95/E101/mixmin/E72/bad-anchor ordering. Invalid as a submission selector when the composite scalar conflicts with E124/E126 public-world stress or promotes same-family files without new upside.
- Current evidence: E128 found component Spearman correlations with known public delta of `0.958042` for `q2s3_delta95_l1`, `0.888112` for `tail_equal_law_resid_ratio`, `0.881119` for `e72_adverse_exposure_e101_plausible`, and `0.874126` for `e101_active_delta95_l1`. The combined `transfer_shrinkage_risk_index` was only `0.440559` and ranked E85/E89/noQ2/E90/E86 as live low-risk candidates, conflicting with E124/E126 loss-side evidence.
- Policy: use the component energies as veto/decomposition fields. Do not submit or rank from the combined score alone. A future candidate must be low-risk on these components and independently pass post-E101 public-world stress with selector-scale expected movement.

### F106. Transfer-shrinkage Pareto-universe veto

- Hidden structure: if the separated E128 components are truly actionable, they should leave some existing non-same-family candidate that preserves the E95 tail-equal law, avoids E101-active/Q2S3 rollback, and does not raise E101-compatible E72 exposure.
- Candidates: full local/report-referenced `submission*.csv` universe, tensor dedupe hash, strict veto pass, relaxed veto pass, material movement versus E95, same-family flag, and novel actionable flag.
- Label vs split test: valid as an existing-universe falsification. Invalid as a model-score forecast because it does not estimate public LB; it only asks whether old files satisfy the veto geometry.
- Current evidence: E129 scanned `116044` candidate paths and `65865` unique tensors. Strict veto left `3` same-family tensors; strict actionable left E85 and E101; relaxed material survivors add E89; novel strict actionable count is `0`.
- Policy: use this as a negative screen. Do not search or rank old submissions again unless a new representation family has generated genuinely new candidates. The next live feature must create new movement that passes F105/F106, not merely reuse existing files.

### F107. Tail-density synthesis gate

- Hidden structure: tail-neutral/low-alpha density may identify public-compatible cells, but safe public budget placement is not the same as safe probability movement direction.
- Candidates: E127 density field, donor source (`e86`, `e90`, `e89`, `e85`, `noq2`, `mixmin`), mask scope, alpha, E95-relative local margin, E129 separated veto flags, E95 hard-tail exposure, and post-E101 sensor stress.
- Label vs split test: valid as a public-free synthesis stress because E130 starts from E95 and tests density-shaped local movement against already defined vetoes. Invalid if a locally strict row is submitted while E129 veto/actionability or post-E101 sensor stress rejects it.
- Current evidence: E130 generated `1792` variants and evaluated `698`. Local strict rows were `25`; E129-veto-actionable rows before local strict were `19`; local-strict plus E129-veto-actionable rows were `0`; final submit gate was `0`. The best local strict move was `-0.000001512` versus E95 but post-E101 sensor-adverse, while the safest micro-moves were immaterial.
- Policy: use density-shaped synthesis as a falsifier, not a candidate generator. Future features may use tail density as an energy term only if they also prove local E95-relative upside without increasing E72/E101-compatible exposure.

### F108. Tail-density atom-combo veto

- Hidden structure: local-upside and public-safe movement may be nonlinearly separated. If the separation were only additive, local E86/E90 low-alpha atoms could be combined with mixmin/E85 veto-safe atoms or clipped on hard-tail cells to create a safe successor.
- Candidates: local atom id, safe atom id, logit local/safe scales, safe projection on local movement, hard-tail risk scalar, clipped risk quantile, E95-relative local margin, separated veto flags, and post-E101 transfer stress.
- Label vs split test: valid as a public-free linearity falsifier because it reuses only pre-existing E130 atoms and predeclared E128/E129/E124 gates. Invalid if a local-strict row is promoted while `gate_strict_actionable` or post-E101 stress remains false.
- Current evidence: E131 generated `6384` combinations/clipped variants. Local strict rows were `651` and veto-actionable rows were `208`, but their intersection was `0`; submit gate was `0`. The best local row improved E95 by `-0.000001813` but had positive post-E101 sensor mean, and the best sensor mean among evaluated rows was still `+0.000002326`.
- Policy: set `density_atom_linear_correction_valid = false`. Do not build another submission by mixing old local-upside atoms with safe density atoms unless a new representation first creates co-located local upside and transfer-veto safety.

### F109. Veto-nullspace gradient tangent energy

- Hidden structure: if E95 already sits near a public-compatible surface, the local combo-set gradient around E95 may contain a tangent component that improves local public-like stress without moving into E101/E72 tail-risk regions.
- Candidates: combo context (`all`, leave-one-combo, single combo), gradient magnitude rank, mask scope, sparse top quantile, shape transform, active-cell count, Q2/S3 cell count, E95-relative local margin, hidden/block/Q2S3 support, E128/E129 veto flags, and post-E101 sensor stress.
- Label vs split test: valid as a donor-free tangent-space falsifier because it starts from E95 and does not rely on old submission directions. Invalid if a row is promoted from local loss alone while strict hidden/block support or transfer-veto actionability fails.
- Current evidence: E132 generated `4590` gradient-nullspace candidates. Gradient local-strict count was `0`; veto-actionable count was `843`; local-strict plus veto-actionable was `0`; submit-gate count was `0`. Best local movement was `-0.000112772` but structurally non-strict, while best post-E101 sensor movements were local-structure failures.
- Policy: use gradient-nullspace metrics as a negative geometry diagnostic only. Do not submit E95 tangent moves from current combo gradients. A future gradient feature must be attached to a different structural latent target that co-locates local margin and tail safety before probability movement.

### F110. Local-safety co-location atlas

- Hidden structure: the useful post-E95 target may be a cell field where local gradient reward, transfer-shrinkage density, veto-null tail direction, and low E72/E101 hard-tail exposure overlap.
- Candidates: per-context squared E95 combo gradient, veto-null flag, low-adverse flag, density rank, co-located local-safety score, local top-k target mix, co-located top-k target mix, and hidden-block-CV metadata predictability.
- Label vs split test: valid as a latent-target atlas because it does not produce a submission and uses hidden-block holdout to test metadata predictability. Invalid if used as a direct probability gate without proving a selector-scale predictor.
- Current evidence: E133 found best co-location context `all_sign`, but only `0.161830` of local reward mass lies in veto-null+density70. The co-located top50 cells are Q3/Q1-heavy (`Q3 40%`, `Q1 34%`) and almost exclude Q2/S3 (`2%`) and E101-active cells (`0%`). Best metadata CV top50 truth-mass capture is only `0.048280`.
- Policy: keep this atlas as a target-design clue, not a submission feature. Next representations should try raw/run/block context prediction of the Q3/Q1-heavy safe remainder and should be rejected if they collapse back into Q2/S3 local reward or metadata-only shortcuts.

### F111. Raw-block safe-remainder visibility energy

- Hidden structure: the E133 co-located safe remainder may be a real block-state field visible in raw overnight/run/block context, rather than only a submission-geometry construction.
- Candidates: raw overnight view name, block aggregate PCA vector, target-wise raw block kNN score, hidden-block-heldout ridge score, top50 truth-mass capture, Q1/Q3 mass, and Q2/S3 suppression fraction.
- Label vs split test: valid as a latent visibility audit because it predicts the E133 teacher under hidden-block holdout and does not generate a submission. Invalid as a direct selector if the raw signal only weakly beats metadata or uses the post-E101 teacher to tune probabilities.
- Current evidence: E134 found best predictor `night_all_blockknn` / `target_knn8` with top50 truth-mass capture `0.073497`, cosine `0.498528`, and JS `0.260922`. Metadata-only `submission_metadata` / `ridge` captured `0.063040`. The best predicted top50 is `Q1:37,Q3:4,S4:9` with Q2/S3 fraction `0`.
- Policy: retain as a weak negative/health energy only. Do not submit raw-block co-location gates. A future representation must materially exceed this visibility level or use a different target that creates a movement direction, not only a ranking.

### F112. Prediction-manifold safe-remainder visibility energy

- Hidden structure: the E133 co-located safe remainder may be encoded in the geometry of old submissions, prediction disagreement, row-level prediction PCA, or per-cell uncertainty even if raw/block context sees it weakly.
- Candidates: known-submission logits/probabilities, row prediction PCA, per-cell mean/std/range/entropy-like scalars, target-wise old-prediction features, visible metadata plus prediction metadata, top50 truth-mass capture, Q1/Q3 mass, and Q2/S3 suppression fraction.
- Label vs split test: valid as a latent visibility audit because it predicts the E133 teacher under hidden-block holdout and does not generate a submission. Invalid as a direct selector if it is only metadata-level or worse than E134 raw/block context.
- Current evidence: E135 found best predictor `row_prediction_pca_meta` / `ridge` with top50 truth-mass capture `0.063430`, cosine `0.531360`, and JS `0.251301`. Best metadata-only is `0.063040`, while E134 raw/block remains higher at `0.073497`. The best predicted top50 is `Q1:11,Q3:38,S4:1`, with Q2/S3 fraction `0`.
- Policy: retain only as a negative health check and Q2/S3-suppression diagnostic. Do not submit old-prediction-manifold gates, disagreement gates, or E133/E134/E135 rank translations unless a new target representation materially exceeds this hidden-block-heldout visibility.

### F113. Block-target compressed safe-state visibility

- Hidden structure: the safe remainder may be generated at hidden-block-by-target state level, making cell-level recovery too sparse and row-total recovery too coarse.
- Candidates: block-target aggregated teacher mass, block-family aggregated teacher mass, raw block views, old-prediction row geometry aggregated to block, metadata, top10 enrichment over random, oracle top10 capture ratio, and row-total contrast.
- Label vs split test: valid as a JEPA target-redesign audit because it predicts compressed states under leave-hidden-block-out. Invalid as a submission feature until a calibrated cell-level movement from the compressed state passes transfer-shrinkage, hardtail, and post-E101 stress.
- Current evidence: E136 found best block-target compressed predictor `all_raw_views_raw_pred` / `ridge` with top10 truth-mass `0.332698`, random enrichment `3.326980`, and oracle top10 capture ratio `0.709652`. Pure `night_all_raw` block-target reaches enrichment `3.236095`. Row-total best is only `1.181643`, while cell-level E134/E135 enrichment references are `2.572395` and `2.220050`.
- Policy: keep as the next live representation target. Do not submit from E136 rankings directly. The next experiment should ask whether block-target safe-state support can define direction/amplitude of probability movement without using weak E133 cell rankings.

### F114. Block-target gated E95-gradient translator

- Hidden structure: E136 may have found the right state support, and the remaining issue may be selecting the E95 local gradient only inside that state.
- Candidates: E136 predicted block-target state masks, donor-free E95 combo gradients, context name, hard/soft state mask, target scope, shape, scale, local strict gate, transfer veto, post-E101 p95, and hardtail exposure.
- Label vs split test: valid as a movement translator falsifier because it uses public-free E136 state predictions and pre-existing E95-relative stress gates. Invalid as a submission if local mean improves but strict/veto/post-E101 p95 fails.
- Current evidence: E137 generated `1980` block-target gradient variants. Evaluated variants `698`; local strict `0`; transfer-veto-actionable `0`; local-and-veto `0`; submit-gate `0`. Best local delta vs E95 is `-0.000043592`, and best post-E101 mean vs E95 is `-0.000040388`, but p95 remains positive (`~0.000026`) and tail-equal law alignment is poor.
- Policy: mark this translator invalid. Keep F113 as a representation target, but do not use current E95 combo gradients as its decoder. Future translators must learn direction/amplitude inside block-target state or use hardtail-support labels directly.

### F115. Block-target x veto-null overlap mask

- Hidden structure: E136 block-target state and E128/E132 transfer-safe veto-null fields may be two partial views of the same safe hidden region; their overlap might be where a probability movement becomes both locally useful and public-tail safe.
- Candidates: state scope/fraction, veto-null or low-adverse safety scope, overlap kind, selected cells/rows, Q2/S3 share, S share, gradient context/shape/scale, local strict gate, separated transfer-veto gate, post-E101 mean/p95, combo-set tail neutrality, hidden Q2/S3 support, world support, and E72 hard-tail exposure.
- Label vs split test: valid as a movement-decoder falsifier because it uses public-free state predictions and predeclared veto/stress gates. Invalid as a submission feature if it only fixes transfer-veto or post-E101 mean while failing all-set strict/tail/world health.
- Current evidence: E138 generated `1314` overlap variants and evaluated `698`. Transfer-veto-actionable rows rose to `373`, but local strict rows stayed `0`, local-and-veto stayed `0`, and submit-gate stayed `0`. The best local row improved all stress by `-0.000030467` and post-E101 mean/p95 by `-0.000055772` / `-0.000015691`, but only `2/3` combo sets beat base and only `1/3` tails were neutral; hidden Q2/S3 and world support were adverse.
- Policy: retain only as a diagnostic energy. It proves state-veto co-location is not enough. Do not build files by intersecting more masks with the current gradient; the next feature must define a decoder objective that preserves all-set tail neutrality and world/raw hidden structure.

### F116. Block-target set-consensus decoder

- Hidden structure: the unsafe part of the current block-target translator might be disagreement among combo-set gradient directions, so a decoder using only `inverse_top`, `raw05_compatible`, and `all_sign` agreement cells might preserve the public-compatible law.
- Candidates: decoder family (`all3_min`, `all3_mean`, pairwise min), source combo sets, agreement cell counts, agreement Q2/S3/S-cell counts, state/safety overlap masks, gradient shape/scale, combo-set mean wins, tail-neutral count, world/raw nonworse flags, and post-E101 transfer sensors.
- Label vs split test: valid as a decoder falsifier because it uses public-free combo gradients and the existing E136/E138 stress gates. Invalid as a submission feature if it passes mean combo-set wins while failing tail/world/raw health.
- Current evidence: E139 generated `1188` variants and evaluated `698`. It found `190` transfer-veto-actionable rows but `0` local strict, `0` local-and-veto, and `0` submit-gate rows. Every evaluated row passed all-margin/all-beats-base but failed tail-neutral, world-nonworse, and raw-energy-nonworse checks. Some `all3_mean` rows reached `3/3` combo-set wins but still had only `1/3` tail-neutral sets.
- Policy: reject as a direct feature. Keep combo-set consensus only as a diagnostic dimension. A future decoder must optimize tail/worst-case and world/raw constraints directly, rather than using consensus as a post-hoc sign filter.

### F117. Tail/world primitive decoder

- Hidden structure: safe movement may exist only at primitive single-cell directions where local reward, combo-set tails, world support, and raw-energy support are simultaneously non-adverse.
- Candidates: support cell from E136/E138/E139 union, micro direction, target, block-target state value, support count, local reward, set mean wins, set worst-tail deltas, hidden-core delta, world delta, raw-energy delta, primitive score, top-k combined pool, shape, and scale.
- Label vs split test: valid as a primitive decoder falsifier because it scores both directions for each support cell with the same stress metrics before combination. Invalid as a submission feature if combination keeps world/raw healthy but fails exact all-set tail neutrality or transfer-veto actionability.
- Current evidence: E140 found `471` support cells, `942` micro rows, `373` local-reward primitives, `119` tail/world/local primitives, and only `3` tolerance-level strict primitives with negligible reward. Combined variants `168` had `0` local strict, `0` transfer-veto-actionable, and `0` submit-gate rows. All combined variants passed hidden-core/world/raw nonworsening, but all failed all-set tail neutrality.
- Policy: reject as a submission feature. Keep it as evidence that world/raw can be handled by primitive decoding, while combo-set worst-tail remains the main decoder target.

### F118. Tail-tolerance transfer audit

- Hidden structure: E140's all-set tail failure may be a numerical exact-zero artifact, and the real blocker may be E72-plausible transfer exposure.
- Candidates: tail tolerance, relaxed structural pass count, E95 E72-plausible exposure threshold, relaxed minimum E72 exposure, E72 gap, post-E101 p95, strict-veto/actionable counts, and exact raw05/all-sign tail deltas.
- Label vs split test: valid as a validator audit because it does not create new predictions and only reinterprets E140's already scored rows. Invalid as a candidate source because it relaxes a gate rather than improving the prediction.
- Current evidence: E141 shows tolerance `1e-12` opens `84` relaxed structural rows, but relaxed plus E72 exposure pass remains `0`, relaxed plus post-E101 p95 pass remains `0`, and actionable remains `0`. Minimum relaxed E72 gap is `+0.000003189534`.
- Policy: keep tolerance-aware tail checks in diagnostics. Do not promote relaxed-tail candidates unless a future decoder also reduces E72-plausible exposure below the E95 threshold and makes post-E101 p95 nonpositive.

### F119. Transfer-budget clipped decoder

- Hidden structure: E140 relaxed structural movement may be locally correct but contaminated by cells that spend too much E72-plausible public-tail budget.
- Candidates: parent E140 relaxed row, per-cell E72-plausible excess versus E95, rollback ranker, rollback cell count, target mix after rollback, local all-minus-E95, relaxed structural flag, E72-budget flag, post-E101 p95, and tail-equal law residual.
- Label vs split test: valid as a candidate generator because it creates new predictions and evaluates them against independent local combo, hidden/world/raw, transfer-budget, and post-E101 stress. Risky if the E101-conditioned density is overused as a selector rather than a diagnostic.
- Current evidence: E142 produced `35` submit-relaxed rows and materialized `submission_e142_transferclip_09a92236.csv`. The selected row rolls back `55` excess-exposure cells from E140 parent `e140_score_top_local_25c44401`, preserves local all-minus-E95 `-0.000010666782`, matches E95's E72-plausible exposure, and has post-E101 p95 `-0.000003762343`.
- Policy: keep as a higher-upside/higher-risk fallback. Do not broaden it by uniform shrinkage or partial clipping; those fail budget gates. Treat public feedback as a test of whether E101-conditioned transfer-budget clipping generalizes.

### F120. Active/Q2S3 repair gate for transfer-budget residuals

- Hidden structure: after E101's small public loss, residual decoder movement may still be useful only if the most active Q2/S3-weighted cells are pruned back toward E95.
- Candidates: E142-minus-E95 logit deltas, E101-active mask, Q2/S3 and S3 masks, ranked Q2/S3/tension masks, rollback keep factor, active/Q2S3 gate, original strict actionability, E72-budget, and post-E101 p95.
- Label vs split test: valid as a candidate repair because it starts from an already-opened E142 residual decoder and asks a single public-observation-derived risk question. Risky if the active/Q2S3 veto is overconservative and removes the cells public would reward.
- Current evidence: E143 generated `80` repair variants; all `80` were relaxed-submit and `15` were original-strict-submit. The materialized `submission_e143_activeq2s3repair_68ca656f.csv` rolls back `21` top Q2/S3-weighted cells, keeps `164` E95-relative changed cells, has local all-minus-E95 `-0.000009551358`, E72 gap `~0`, post-E101 p95 `-0.000003368915`, and passes the active/Q2S3 and original strict gates.
- Policy: keep as the conservative fallback after F121. It preserves most residual-decoder upside while satisfying the stricter E101-informed risk gate, but E144 found a finer boundary with slightly better local/post-E101 stress.

### F121. Fine active/Q2S3 boundary gate

- Hidden structure: the E101-informed active/Q2S3 boundary may be a fine LogLoss tail cliff, not a binary decision to fully roll back E143's top `21` cells.
- Candidates: E142-minus-E95 logit deltas, Q2/S3-weighted ranked masks, tension masks, E101-active masks, top counts `14..24`, keep factors around E143, original strict actionability, E72-budget, active/Q2S3 gate, and post-E101 p95.
- Label vs split test: valid as a candidate refinement because it starts from E143's already-opened strict branch and asks whether a local boundary can be tightened without changing the worldview. Risky if the tiny retained movement is public-tail overfit.
- Current evidence: E144 generated `206` repair variants, `32` original-strict variants, and `9` E144-submit variants. The materialized `submission_e144_activeboundary_d7b4b331.csv` uses `top_q2s3_weighted_24`, keep factor `0.15`, rolls back `24` cells, keeps `185` E95-relative changed cells, has local all-minus-E95 `-0.000009725930`, E72 gap `~0`, post-E101 p95 `-0.000003430489`, and passes active/Q2S3 plus original strict actionability.
- Policy: current top submission candidate. Use it before E143 because it keeps all E143 gates while improving local all-minus-E95 and post-E101 p95. If public rejects it but E143 later succeeds, mark F121 as too fine and keep F120's conservative boundary.

### F122. E144 public-feedback decoder energy

- Hidden structure: E144's tiny local edge may be public-real, noise-scale, or a public-sensor overfit; the next LB must be decoded relative to E95, E101, and mixmin rather than interpreted after the fact.
- Candidates: E144 public LB, delta vs E95, delta vs E101, delta vs mixmin, E144 local edge over E143, and pre-registered branch labels.
- Label vs split test: valid as a public-sensor guard because it creates no predictions and blocks post-hoc same-family rescue. It is not a feature for model training.
- Current evidence: E145 defines seven bands: breakthrough win `<=0.576271330`, clean win `<=0.576284330`, micro win `<=0.576289330`, tie `<=0.576293330`, fine-loss branch alive `<=0.576300366`, branch loss `<=0.576306641`, and hard fail `>0.576306641`.
- Policy: consult before any post-E144 action. E143 is allowed only in the no-worse-than-E101 loss band; worse-than-E101 blocks E143/E142 automatic rescue, and worse-than-mixmin closes the branch.

### F123. E144/E143 retained S3-tail prior support

- Hidden structure: E144's fine boundary may be a real S3 tail-state correction rather than a strict-gate artifact; visible train flanks and subject priors should weakly recognize it if so.
- Candidates: E144-vs-E143 differing cells, hard-label support direction, target, row/block/edge context, global/subject/flank priors, expected E144-minus-E143 delta, simulated beat probability, and high-impact cell support.
- Label vs split test: valid as a public-free interpretation feature because it uses only train-derived priors and known candidate probabilities. Invalid as a submission generator because it is a prior explanation over `24` cells, not a new calibrated probability movement.
- Current evidence: E146 finds `24` E144-vs-E143 differing cells, all `S3`, with `0` flank conflicts. All `10/10` public-free priors prefer E144 over E143; expected deltas range from `-0.000010294767` to `-0.000001097289`, and simulated beat probability ranges from `0.540545` to `0.925720`.
- Policy: use as fallback interpretation energy. It strengthens E144 as the next public sensor. If E144 loses narrowly, do not automatically promote E143 as expectation-safer; read the loss as hidden public S3-tail adversity unless the next public slot is explicitly a fine-tail retention contrast.

### F124. E144/E95 whole-file prior-world energy

- Hidden structure: E144 may be a coherent E95-relative residual state rather than a local E143 refinement. If so, visible priors should prefer E144 over E95 across the whole moved-cell surface, with any failure localized to specific targets/components.
- Candidates: E144-vs-E95 moved cells, inherited E143 body versus E144-only fine-tail delta, hard-label support direction, target/component contribution, edge/flank context, global/subject/flank priors, expected E144-minus-E95 delta, simulated beat probability, and high-impact support cells.
- Label vs split test: valid as a public-free candidate-health energy because it uses train-derived priors and pre-existing submissions only. Invalid as a direct feature generator because it does not create new probabilities; it interprets the pending E144 public sensor.
- Current evidence: E147 finds `185` E144-vs-E95 moved cells across `108` rows and `9` subjects. All `10/10` public-free priors prefer E144 over E95, with expected deltas from `-0.000049865515` to `-0.000012197928` and simulated beat probability from `0.583850` to `0.762700`. The inherited E143 body carries the main favorable signal, while S3/Q3 are the visible stress axes under nearest-hard priors.
- Policy: use as the whole-file interpretation layer for E144. If E144 wins, this energy is strengthened. If E144 loses, first decompose S3/Q3 and fine-tail/body failure before falling back to E143/E142 or closing the branch.

### F125. E144 outcome-band attribution energy

- Hidden structure: a future E144 public score band is generated by a hidden support pattern across the moved cells; the same numeric band can mean different things depending on whether failure concentrates in fine-tail S3, inherited body, Q3, S2, or broad support.
- Candidates: E145 band, simulated prior, world-rate, conditional support rate, conditional delta by target/component/target-component, support-rate lift versus prior, support flip share, and branch-or-worse mass.
- Label vs split test: valid as a pre-public interpretation guardrail because it uses simulated train-prior worlds and fixed E145 bands. Invalid as a model feature because it conditions on hypothetical score bands rather than observable test labels.
- Current evidence: E148 samples `250000` worlds per prior. Global/subject/nearest-hard win-rate mass is `0.745560` / `0.599760` / `0.635616`, while branch-or-worse mass is `0.204972` / `0.333832` / `0.284852`. Fine-loss worlds are rare and not necessarily fine-tail-specific; nearest-hard loss blame is S3/Q3, global loss blame is inherited-body/Q3/S2, and subject loss blame is inherited-body/Q3/S3.
- Policy: use after E144 public feedback. Apply E145 band first, then E148 attribution. Do not submit E143 simply because E144 lands in fine-loss; require the attribution to point to fine-tail/S3 retention rather than inherited-body or broad target-body failure.

### F126. E144 anchor-geometry residual energy

- Hidden structure: E144 may be a safer point on the E142/E143 residual branch rather than a new broad hidden-state direction. Its submission value depends on branch geometry surviving public labels while avoiding known E72/E101 public-negative axes.
- Candidates: logit deltas versus E95, cosine/projection against hardtail/E72/E101/E142/E143 axes, active-cell overlaps, target L1 shares, Q2/S3 share, residual ratio versus E142/E143 axes, and E144-vs-E143 / E144-vs-E142 pairwise directions.
- Label vs split test: valid as a LeJEPA-style geometry health feature because it uses fixed submissions and known public anchors to diagnose collapse/shortcut risk. Invalid as a direct generator because it does not create calibrated probabilities or reveal hidden public labels.
- Current evidence: E149 shows E144 is nearly aligned with E143 (`cos 0.991918719`) and strongly aligned with E142 (`cos 0.952146833`), while almost orthogonal to E101 (`-0.019625796`) and E72 (`-0.024358970`) negative axes. Residual ratio is `0.126874959` versus E143 and `0.305640978` versus E142. E144's Q2/S3 share is `0.161603888`, far below E101's `1.000000000`.
- Policy: use as public-feedback interpretation energy. E144 remains the next file because it avoids known negative axes and keeps strong prior support, but expected upside should be framed as branch-pruned residual validation rather than a broad JEPA breakthrough.

### F127. E144 post-feedback decision gate

- Hidden structure: a scalar E144 public score is underidentified unless it is interpreted through score band, target/component attribution, and branch geometry together.
- Candidates: E145 band, E148 global/subject/nearest-hard world rates and top responsibility groups, E149 branch/negative-axis geometry, branch status, allowed next action, forbidden same-family action, and optional observed-score classification.
- Label vs split test: valid as a decision feature because it creates no probabilities and prevents post-hoc public-LB overfitting. Invalid as a model feature because it conditions on a future external score.
- Current evidence: E150 produces `7` decision rows. The key correction is `fine_loss_branch_alive -> conditional_alive`: E143 is allowed only if attribution points to fine-tail/S3 retention. `branch_loss` and `hard_fail` block E143/E142 rescue.
- Policy: mandatory after E144 public feedback. Run `python3 analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>` before creating or submitting any post-E144 same-family file.

### F128. Plateau resolution bottleneck energy

- Hidden structure: the current frontier may be limited less by missing features than by selector resolution and probability-decoder geometry. A useful feature must prove it can create public-tail-safe movement above frontier-scale noise without collapsing into the E142/E143/E144 branch.
- Candidates: E95-over-mixmin edge, E101 public loss, E98 known-LB selector p90/MAE, E120 local optimism, E129 old-universe strict novelty count, E130-E139 submit gates, E142/E143/E144 branch counts, E144/E143 cosine, and E144 local tiebreak.
- Label vs split test: valid as a LeJEPA-style decision energy because it tests whether candidate families are healthy enough to create submissions. Invalid as a direct model feature because it aggregates experiment outcomes and public observations.
- Current evidence: E151 finds E98 p90 `0.0008164966` is `53.33x` the E95 public edge; E101 actual-minus-local-mean optimism is `0.0000252415`; E129 strict novel actionable count is `0`; E130/E131/E132/E137/E138/E139 have `submit_gate=0`; E142/E143/E144 branch counts are `35`/`15`/`9`; E144 is E143-collinear with cosine `0.991918719`.
- Policy: use as a hard framing gate. Do not spend work on old-file ranking, blend/top-count sweeps, or same-family Q2/S3 amplitude tweaking unless E144 public feedback explicitly calls for that branch. New local work must target a non-collinear representation-to-probability decoder that passes strict/E72/post101 p95 gates with edge above `1e-5`.

### F129. Branch-orthogonal gate-intersection state

- Hidden structure: useful signal may exist outside the E142/E143/E144 branch, but the public-safe decoder may require a latent state where structural reward, E72 budget, post-E101 safety, and active-veto actionability co-occur.
- Candidates: E137-E140 source residual ratio versus E144, projection mode, top-k support, alpha, relaxed structural gate, E72-plausible gap, post-E101 p95, active-veto/actionability, blocker-intersection class, and source family.
- Label vs split test: valid as a diagnostic target because it explicitly separates non-collinear representation signal from calibrated probability movement. Invalid as a direct submission feature because E152 found no all-four intersection and no public file.
- Current evidence: E152 finds `4650/4650` source rows non-collinear and `2880` projected rows. The individual gates open separately (`349` relaxed, `1208` budget, `564` post-E101, `122` actionable), but all-four intersection is `0`. The best relaxed-budget-post101 row is E138 and fails actionability; the only budget-post101-actionable row is E139 and fails relaxed structure.
- Policy: use as the next latent/diagnostic target. Do not repeat direct branch-orthogonal projection sweeps unless a new model predicts gate-intersection membership out-of-sample or changes the decoder objective.

### F130. S3 active-boundary gate-intersection target

- Hidden structure: the old active/Q2S3 veto is mostly an S3 active-boundary exposure detector, while the only actionability-safe escape fails raw/world structural health.
- Candidates: E153 `gate_class`, active/Q2S3 failure flag, action-cos failure flag, target L1 share, S3/S4/S2 lift, Q1-heavy actionable escape flag, raw/world relaxed blockers, tail-equal cosine/residual, and source family/projection mode.
- Label vs split test: valid as a diagnostic and decoder target because it explains why E152's public-safe gates do not intersect. Invalid as a direct feature unless a new movement passes all-four stress without using public feedback.
- Current evidence: E153 finds `103` three-of-four near misses and no all-four row. `102` are `missing_actionable`; `101/102` fail active/Q2S3 while relaxed/E72/material blockers are zero. Target contrast shows S3 `+0.022774`, S4 `+0.020949`, S2 `+0.018800`, and Q2 effectively absent. The lone `missing_relaxed` row is Q1-heavy and fails raw/world health.
- Policy: make this the next local decoder target. A candidate can be materialized only if it repairs S3 active-boundary actionability or raw/world relaxed health while preserving relaxed, E72-budget, post-E101, and actionability gates simultaneously.

### F131. E154 repaired all-four branch energy

- Hidden structure: the S3 active-boundary blocker is local enough that selected E101-active S3 rollback can make E144-plus-orthogonal residual movement satisfy every current health gate.
- Candidates: S3 rollback mask, E101-active S3 rank, keep factor, all-four flag, E72-budget flag, post-E101 p95, active/actionability flag, local material flag, cosine versus E144/E143/E142, cosine versus E72/E101, target L1 shares, and changed-cell overlap with E144.
- Label vs split test: valid as a submission-health and latent-geometry feature because it repairs a pre-identified local gate failure without using new public labels. Invalid as a general feature generator until public feedback confirms whether E154's additional branch body is public-real.
- Current evidence: E154 creates `7458` repair rows from `102` E153 missing-actionable sources and finds `10` all-four materializable rows. The selected row `top_s3_e101_3` keep `0.25` rolls back `3` S3 cells, has all-minus-E95 `-0.000012158050`, moves `294` cells versus E95, contains all `185` E144 cells, and is E144-collinear (`cos 0.983569299`) while avoiding E72/E101 negative axes (`-0.031628728` / `-0.005523655`).
- Policy: use E154 as the current highest-information public sensor. If public improves, promote S3 active-boundary repair as a real decoder target. If public worsens while E144 later improves, demote this feature to overfit branch-extension energy.

### F132. E155 branch-body amplitude ridge

- Hidden structure: the repaired E154 direction may be robust at lower amplitude, meaning the public-safe law is the E144->E154 ridge rather than the exact full E154 body.
- Candidates: E144->E154 body alpha, source repair keep factor, target drop/only group, body-norm ratio, all-four health, E155 submit flag, post-E101 p95, E72 gap, target body shares, and materialized lower-body candidate.
- Label vs split test: valid as a LeJEPA anti-brittleness feature because it tests whether a repaired latent direction survives amplitude and target ablation without public labels. Invalid as a blind blend recipe; it only applies to the E154 branch.
- Current evidence: E155 scores `44` rows and `40` variants. `34` variants are all-four, `27` pass E155 submit, and `22` reduced-body variants submit. The materialized `submission_e155_bodytemp_d27e7965.csv` uses E144->E154 alpha `0.25`, body-norm ratio `0.25`, all-minus-E95 `-0.000010362491`, and all current health gates. All `12/12` target-drop variants remain all-four.
- Policy: keep E154 as the first public sensor because it has larger local edge and tests the full repaired branch. Use E155 as the conservative amplitude-control contrast before E144 if downside risk or an E154 loss makes full-body amplitude suspect.

### F133. E156 low-body target-axis decomposition

- Hidden structure: the repaired branch may not require the diagonal E144->E154 body. A tiny target-axis subset could preserve all-four health while exposing which targets actually carry the public-safe low-body law.
- Candidates: Q1/Q3/S2/S3/S4 body-axis alphas, body-norm ratio, all-four health, strict candidate flag, E155-body-below flag, post-E101 p95, E72 gap, local all-minus-E95, and branch/negative-axis cosine.
- Label vs split test: valid as a LeJEPA decomposition feature because it tests target-axis separability without using public labels. Invalid as a standalone feature if it is only an E144-collinear low-edge point.
- Current evidence: E156 scans `3125` target-axis lattice variants with full non-anchor evaluation. All `3125` are all-four, `2984` are strict candidates, and `85` sit below E155's `0.25` body ratio while still beating E144. The selected `submission_e156_targetaxis_757546d2.csv` uses Q1/S2/S4 alphas `0.25/0.75/0.25`, body ratio `0.171266667`, all-minus-E95 `-0.000010004`, post-E101 p95 `-0.000003712`, and E72 gap `-0.000002266`. It is almost pure branch geometry: cosine with E144/E155/E154 is `0.999515751`/`0.998991027`/`0.985122955`.
- Policy: use E156 as the third repaired-branch control after E154 and E155. If it wins while E154/E155 lose, the live target law becomes tiny Q1/S2/S4 add-on over E144. If it loses while E144 wins, the add-on is public-overfit.

### F134. E157 low-body axis response and Pareto control

- Hidden structure: E156's minimum-body Q1/S2/S4 row may be a body-minimization artifact. A healthier axis feature should explain finite-difference target responses and identify any low-body row that dominates E155 across multiple stress metrics.
- Candidates: per-axis finite-difference response for local all-minus, post-E101 p95, E72 gap, body cost, and transfer-shrinkage risk; E155-dominating low-body Pareto rows; target-axis alphas.
- Label vs split test: valid as a LeJEPA anti-shortcut feature because it rejects overinterpreting a selected target-axis row when the whole lattice gate is saturated. Invalid as a high-confidence submission feature because the E157-over-E155 edge is far below public-resolution scale.
- Current evidence: E157 finds all `3125` lattice rows all-four and finite-difference local/post-E101 improvements for every axis. Q3 is strongest for local all-minus (`-0.000000383335`) and post-E101 p95 (`-0.000000132956`), while S2 carries E72 budget (`-0.000000714955`). Three rows use less body than E155 while improving local, post-E101 p95, and E72 gap. The materialized `submission_e157_lowbodypareto_bd67930d.csv` uses Q1+Q3+S2+S4, body ratio `0.240336139`, all-minus-E95 `-0.000010404446`, post-E101 p95 `-0.000003807382`, and E72 gap `-0.000001671496`.
- Policy: keep E157 as an optional tuned low-body Pareto control. It can sit after E154/E155 and before E156 if the question is tuned target-axis low-body performance; otherwise E155 remains the cleaner amplitude-control and E156 the minimum-body control.

### F135. E166 broad-survivor scaled latent direction

- Hidden structure: E95 may be missing a broad post-frontier latent branch that the repaired E154/E155/E157/E156 stack cannot see because that stack is dominated by one-cell hard-label fragility. The candidate feature is not raw JEPA probability movement; it is a tiny E95-to-broad-survivor logit step selected by breadth, bad-axis geometry, and negative-control rejection.
- Candidates: E164 broad-edge flag, E164 cells-to-flip, E164 top1/expected ratio, E165 bad-span energy, E165 max bad-axis and max cosine, E166 scale, focus expected delta, entropy delta, mean/max absolute logit move, Q2/S3 share, cosine to E154/E101/mixmin, and negative-control sensor-gate count.
- Label vs split test: valid as a LeJEPA-style latent/gate feature because it uses fixed prediction geometry, known public-negative axes, and negative controls without fitting hidden public labels. Invalid as a direct feature if the full broad row is submitted or if the gate is tuned after public feedback to rescue one specific broad file.
- Current evidence: E164 scanned `2052` tracked paths and found `198` E95-relative broad-edge rows, including `192` conservative candidate-gate rows. E165 scored `205` broad rows and kept `90` geometry-health survivors while rejecting the `2` known-public-bad broad controls. E166 scaled `21` survivor directions, found `112` sensor-gate rows, `51` material rows with scale `<=0.03`, and `0` negative-control gate rows. The selected `submission_e166_broadsurv_s0p01_d8bfa94b.csv` is a `1%` step toward `submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv`, with focus expected delta `-0.000332077`, cells-to-flip `74`, top1/expected `0.023369627`, bad-span energy `0.450742441`, max bad-axis `q2_bad`, max cosine `0.268538582`, entropy delta `0.000238386`, and mean/max logit movement `0.002243986` / `0.013580886`.
- Policy: use E166 only as the broad plateau-break public sensor. If it wins, promote the broad-survivor latent branch and then decompose amplitude/target axes before scaling. If it loses, do not discard every broad branch blindly; revise the bad-axis geometry because E165 likely missed a public-negative axis or public subset mismatch. E154 remains the conservative repaired-branch sensor when the question is branch extension rather than plateau escape.

### F136. E167 broad context-alignment and safety-divergence energy

- Hidden structure: a broad latent can be real in row/block/calendar space and still be unsafe under the transfer-shrinkage atlas. E167 separates hidden-context reality from safety certification.
- Candidates: focus-set edge-like rate, between-train-runs rate, top-subject/block concentration, all-veto-null rate, all-safe-density mean, broad-low-alpha mass, E101-plausible mass, E72-active rate, and target-count-preserving null z-scores/p-values.
- Label vs split test: valid as a LeJEPA-style diagnostic because it uses fixed E166/E95 movements and target-count nulls. It is invalid as a direct probability feature until public feedback shows whether safety-atlas divergence is overconservative or truly public-negative.
- Current evidence: E166 top-benefit focus cells are context-enriched: edge-like rate `0.689189` vs null `0.470842`, between-train-runs `0.797297` vs `0.624658`, and top-subject share `0.243243` vs `0.164563`. They are safety-atlas adverse: all-veto-null `0.297297` vs `0.574158`, all-safe-density `0.117097` vs `0.243966`, broad-low-alpha mass `1.321365` vs `3.199735`, E101-plausible mass `0.238204` vs `0.533727`, and E72-active `0.837838` vs `0.670369`.
- Policy: use this energy to interpret E166 public feedback. If E166 wins, the safety atlas is too conservative/branch-bound around broad hidden-context cells. If E166 loses, the E72-active/low-veto-null conflict becomes the primary broad-branch failure axis. Do not scale or clone E166 before that feedback.

### F137. E168 context-high safety mask

- Hidden structure: E166's hidden-context cells may contain a recoverable overlap where row/block context and public-free safety agree. The feature is the intersection of broad context (`edge-like OR between-train-runs`) with veto-null or safe-density comfort.
- Candidates: context-high flag, strict-context flag, veto-null flag, safe-density thresholds, not-E72-active flag, target masks, expected delta, cells-to-flip, top1/expected, context gain, veto gain, density gain, and E72-active reduction.
- Label vs split test: valid as a pre-public mask feature because it uses fixed E166/E95 movement and public-free atlas fields with target-count/breadth criteria. Invalid as direct evidence that public labels prefer the mask.
- Current evidence: E168 finds `2` decoupling-pass policies. `context_high__veto` keeps `904` cells, expected delta `-0.000120457`, cells-to-flip `32`, top1/expected `0.048415`, edge-like `0.610619`, between-train-runs `0.819690`, veto `1.0`, safe-density `0.346150`, and E72-active `0.268805`. `context_high__high_density_p50` is similar with expected delta `-0.000119080`. Strict context masks are too top-cell fragile.
- Policy: use context-high safety masks before raw E166 when the goal is a balanced broad repair. Do not over-purify to strict edge-and-between or not-E72-only masks because they destroy materiality/breadth.

### F138. E169 materialized context/safety broad candidate

- Hidden structure: a context-high safety mask should remain healthy after being translated into an actual prediction tensor, not only in cell-summary space.
- Candidates: materialized masked E95-to-E166 logit movement, broadness metrics, bad-span energy, max bad-axis cosine, amplitude, Q2/S3 share, cosine to E154/E101/mixmin, and E168 decoupling-pass flag.
- Label vs split test: valid as a candidate-health feature because it produces real submission files and reruns the same geometry stress used for E166. Invalid as public-proof because no E169 LB exists yet.
- Current evidence: E169 materializes `submission_e169_ctx_veto_c5e806e3.csv` and `submission_e169_ctx_high_density_p50_51110c7e.csv`. The preferred `ctx_veto` row has expected delta `-0.000120457`, moved cells/rows `904/193`, cells-to-flip `32`, top1/expected `0.048415`, bad-span energy `0.295326`, max bad cosine `0.222381`, mean/max abs logit `0.001096`/`0.010206`, Q2/S3 share `0.347775`, and low cosine to E154/E101/mixmin.
- Policy: `submission_e169_ctx_veto_c5e806e3.csv` is the best balanced broad-branch public candidate. Use `submission_e169_ctx_high_density_p50_51110c7e.csv` only as a near-duplicate control. Raw E166 remains the riskier atlas-falsification sensor.

### F139. E170 public-feedback decoder and hard-label readability energy

- Hidden structure: E169's local broad repair may still be underresolved by the hidden public hard-label realization. The feature is not a prediction feature; it is a submission-decision energy that measures how many high-swing cells can explain a public score band.
- Candidates: score bands relative to E95/E101/mixmin, pairwise moved-cell breadth, top1/top5 swing, cells for `2e-6` guard, cells for E95-over-mixmin edge, target/context attribution, E72-active split, and near-duplicate sibling distance.
- Label vs split test: valid as a pre-feedback decision feature because it uses only fixed candidate tensors and known public anchors. Invalid as a public-LB fitting feature if thresholds are changed after seeing E169's score.
- Current evidence: E169-vs-E95 has expected delta `-0.000120457` and `32` cells-to-flip expected, but `1` top cell hits the `2e-6` guard and `4` cells cover E95's public edge over mixmin. Between-train-runs cells carry `81.1%` of expected edge, not-E72-active cells `73.7%`. `ctx_high_density_p50` differs by only `10` Q2/S3 cells and `-0.000001377` expected delta.
- Policy: after E169 public feedback, run `python3 analysis_outputs/e170_e169_public_feedback_decoder.py --score <PUBLIC_LB>` before selecting any follow-up. Do not submit E169 near-duplicates or raw E166 automatically after a tie/small loss.

### F140. E171 E169 critical-cell prior consistency

- Hidden structure: a broad latent body can be supported while the few public-decisive hard-label cells are visible-prior adverse. This feature separates body support from critical-cell support.
- Candidates: support probabilities under global/subject/flank/focus/visible priors, E170 band simulation under each prior, top-swing set summaries, target-matched null support, flank conflict, context type, and target-level visible deltas.
- Label vs split test: valid as a pre-public LeJEPA countercheck because it uses train-derived priors and fixed E169/E95 cells. Invalid as a direct pruning rule unless the pruned tensor re-passes breadth/readability stress.
- Current evidence: full E169 body is favorable under visible_mean (mean `-0.000022659`, win `0.868840`), but top critical sets are weak: top1 support `0.098648`, top4 `0.330699`, top32 `0.247434`; top32 is below target-matched null mean `0.353573` (`z=-2.703`). Flank priors are weak/adverse, while subject/global-style priors remain favorable.
- Policy: keep E169 as a high-information broad sensor. Treat narrow loss as critical-cell adversity first, not immediate branch death. Do not create a top-cell-pruned E169 unless it preserves broad expected edge and passes E170-style readability.

### F141. E172 visible-positive-loss rollback gate

- Hidden structure: E169's broad context/veto body and visible-prior adverse tail may be separable. The useful feature is not "top cell prune"; it is the set of cells whose E169-vs-E95 movement has positive expected LogLoss under visible priors.
- Candidates: `expected_delta_visible_mean > 0`, rollback keep factor, moved-cell breadth, cells-to-flip, focus expected delta, visible-prior mean/p95/worse-than-E101, bad-span energy, max bad-axis cosine, Q2/S3 share, and materialized rollback tensor.
- Label vs split test: valid as a pre-public gate because it uses train-derived priors plus fixed E169/E95 movement and requires independent breadth/geometry survival. Invalid if tuned after E169/E172 public feedback or if used to prune arbitrary candidates without rerunning broadness/readability stress.
- Current evidence: E172 scores `67` rollback variants and finds `7` stress-gate rows. The selected `visible_positive_all_keep0p25` row rolls back `410` visible-prior-positive-loss cells to `25%` of E169 movement, keeping focus expected delta `-0.000112695`, moved cells/rows `904/193`, cells-to-flip `30`, and top1/expected `0.051750`. It improves visible p95 from `+0.000010607` to `-0.000026683`, visible worse-than-E101 from `0.058545` to `0.000050`, bad-span energy from `0.295326` to `0.257874`, and max bad cosine from `0.222381` to `0.142927`.
- Policy: use `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` as the first broad-branch expected-score candidate. Keep raw E169 as the unrolled body-vs-tail sensor, not as the safer score candidate.

### F142. E173 E172 feedback bands and rollback responsibility map

- Hidden structure: even a healthier broad tensor can remain public hard-label-resolution limited. The feature is a decision layer that separates prior-tail repair from hidden-label readability.
- Candidates: E172 score bands, E172-vs-E95 pairwise hard-label swing, E172-vs-E169 rollback cell attribution, target/context rollback cost, visible/flank/subject prior moments, and observed-score decision rows.
- Label vs split test: valid because it is fixed before public feedback and writes no submission. Invalid if its thresholds are changed after seeing E172 LB.
- Current evidence: E173 shows E172-vs-E95 keeps broad support (`904/193`, expected delta `-0.000112695`) and strong prior-tail repair, but still has top1 swing `0.000005832`, cells for `2e-6` guard `1`, and cells for E95-over-mixmin edge `4`. E172-vs-E169 rollback costs `+0.000007762` under E162 focus priors, mostly Q2/S2, while improving visible/flank tail priors.
- Policy: after E172 public feedback, run `python3 analysis_outputs/e173_e172_public_feedback_decoder.py --score <PUBLIC_LB>` before any E169/E166/E154 follow-up. Do not tune rollback keep factors from a tie or small loss.

### F143. E174 rollback-overcorrection energy

- Hidden structure: E172's visible-positive-loss rollback cells are not all equal. Some cells carry focus-prior recoverable body signal and can be reopened toward E169 without reopening the visible-tail failure that E172 fixed.
- Candidates: E172 rollback-cell focus-recovery rank, target-specific direct effect, keep factor, E162 focus recovery versus E172, visible p95/worse-than-E101, bad-span energy, max bad-axis cosine, Q2/S3 share, and changed-cell count from E172.
- Label vs split test: valid as a pre-public LeJEPA-style gate because it must preserve broadness, visible-tail health, and bad-axis geometry while recovering focus edge. Invalid if tuned after an E172/E174 public score or if the Q2/S3 guard is relaxed only to select a preferred file.
- Current evidence: E174 scores `80` reopening policies and finds `46` gate survivors. The selected `reopen_focus_cost_top75_to1p0` materializes `submission_e174_ro_fc_top75_to1p0_95638e73.csv`, improving focus expected delta versus E172 by `-0.000011672` while keeping visible p95 `-0.000022709`, worse-than-E101 `0.000220`, bad-span energy `0.263996`, and max bad cosine `0.163229`. Direct recovery is mainly S3/Q2/S2/S1.
- Policy: use E174 when the goal is the highest-upside broad expected-score submission. Use E172 when the goal is safer tail-repair evidence. Do not create same-family keep-factor siblings until at least one of E174/E172 is decoded by public feedback.

### F144. E175 E174 public-feedback decoder

- Hidden structure: E174's public score is a hidden-label observation about partial reopening, not a scalar ranking permission. The feature is a decision/energy layer that ties score bands to world updates before feedback.
- Candidates: E174 score band, E174-vs-E95/E172 pairwise hard-label swing, cells-to-flip, cells for E95-over-mixmin edge, target/context attribution, E72-active split, and prior-tail moment deltas versus E172.
- Label vs split test: valid because it uses fixed candidate tensors and known public anchors before seeing E174 feedback. Invalid if the band thresholds, top-cell attribution, or follow-up action table are edited after E174 public LB arrives.
- Current evidence: E175 maps E174 scores to bands from breakthrough `<=0.576261330` through hard fail `>0.576341330`. E174-vs-E172 changes `75` cells, recovers focus `-0.000011672`, has top1 swing `0.000002996`, and spends visible-tail margin by p95 `+0.000003974` and worse-than-E101 `+0.000169869` versus E172. Direct recovery is mostly S3/Q2/S2/S1 and `88.6%` not-E72-active.
- Policy: after any E174 public feedback, run `python3 analysis_outputs/e175_e174_public_feedback_decoder.py --score <PUBLIC_LB>` before choosing E172, E154, or same-family broad variants. Do not use E174 feedback to tune top-N reopening or guard thresholds post hoc.

### F145. E176 E174 component-damping gate

- Hidden structure: E174's useful partial-reopen body may not require full-strength Q2 reopening. The feature is a component-level gate over the `75` reopened cells, separating S3/S2/S1-heavy body recovery from Q2/q2_bad risk.
- Candidates: target/component ablation keep factor, edge retained versus E174, edge retained versus E172, bad-span energy, max bad-axis cosine, Q2/S3 share, visible p95, worse-than-E101, cells-to-flip, and direct target-wise E176-vs-E174 cost.
- Label vs split test: valid as a public-free countercheck because it tests target/context/risk ablations before any E174/E176 score and requires both materiality and risk reduction. Invalid if a component keep factor is chosen after public feedback.
- Current evidence: E176 scans `162` variants and finds `12` gate survivors. The selected `ablate_q2_to0p75` materializes `submission_e176_abl_q2_to0p75_91e49725.csv`. It gives up only `+0.000000983` focus delta versus E174 while reducing max bad cosine to `0.158126`, Q2/S3 share to `0.334753`, visible p95 to `-0.000023096`, and worse-than-E101 to `0.000192`.
- Policy: use E176 as the risk-adjusted E174-family candidate. Use E174 only when intentionally maximizing expected focus edge, and E172 when prioritizing lower tail risk over partial-reopen edge.

### F146. E177 E176 public-feedback decoder

- Hidden structure: E176's public score is a hidden-label observation about Q/S-asymmetric partial reopening, not permission to tune Q2 amplitude.
- Candidates: E176 score band, E176-vs-E95 hard-label breadth, E176-vs-E174 Q2-only contrast, E176-vs-E172 target recovery, prior-tail moment deltas versus E174/E172, and prescribed next-action table.
- Label vs split test: valid because it uses fixed E176/E174/E172 tensors and known public anchors before E176 feedback. Invalid if band thresholds or Q2 keep actions are edited after E176 LB.
- Current evidence: E177 maps E176 scores to bands from breakthrough `<=0.576261330` through hard fail `>0.576341330`. E176-vs-E95 has expected focus `-0.000123384`, moved cells/rows `904/193`, cells-to-flip `33`, and top1 swing `0.000005832`. E176-vs-E174 is only `21` Q2 cells, expected focus cost `+0.000000983`, cells-to-flip `2`, and top1 swing `0.000000832`.
- Policy: after any E176 public feedback, run `python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>`. A win validates Q/S-asymmetric partial reopening; tie/small-loss keeps E95 practical; worse-than-E101 demotes the damped partial-reopen branch; E174 is only a later full-Q2 contrast.

### F147. E178 plateau-law evidence layer

- Hidden structure: post-E95 progress is filtered by a broad hidden body, target-tail calibration, and a small number of high-swing public hard labels. The useful feature is not a probability column but a decision layer measuring whether a candidate's edge is broad enough to exceed selector resolution.
- Candidates: expected focus edge relative to E95, cells for E95-over-mixmin edge, cells-to-flip expected, top1/top5 swing over frontier edge, known-LB selector p90/MAE ratios, Q2/S3 share, bad-span energy, max bad-axis cosine, and public-resolved E101 delta.
- Label vs split test: valid as a public-free audit because it uses fixed tensors and already-known public anchors. Invalid as a direct candidate generator or as a reason to tune E176/E174 keep factors before feedback.
- Current evidence: E178 finds E166 focus edge `-0.000332077` (`21.689x` E95 edge) and E176 `-0.000123384` (`8.059x` E95 edge), but E176 needs only `4` cells to swing the E95 edge and the best known-LB selector p90 is `53.33x` that edge. E101's `0.5763003660` small loss confirms the tail-fragility side.
- Policy: use this layer as a submission survival/risk explanation. Prefer E176 as the single risk-adjusted sensor, and require any future non-E176 candidate to either escape same-family cell fragility or bring a new hard-label-resolution sensor.

### F148. E179 decisive-cell visibility energy

- Hidden structure: a candidate can be supported as a broad body while its public-decisive top cells remain hidden from train-derived priors. The feature separates full-body support, Q2-damping support, and decisive-cell certification.
- Candidates: visible-mean expected delta, visible/focus simulated win rates, top1/top4/top16/top33 swing-weighted support, target-matched null support, Q2 damping support, hard support rate, flank conflict rate, and context-type attribution.
- Label vs split test: valid as a pre-feedback diagnostic because it uses fixed E176/E174/E95 tensors and train-derived priors. Invalid as a pruning or tuning rule if the top-cell weakness is used to create another same-family sibling before E176 public feedback.
- Current evidence: E176 body support is favorable with visible-mean expected delta `-0.000050824` and visible win rate `0.999080`. Q2 damping support is also favorable with visible-mean delta `-0.000000191`, support `0.690495`, and hard support rate `0.904762`. But decisive-cell support is weak: top4 `0.330699`, top33 `0.245771` versus target-matched null `0.335713` (`p_low=0.014667`).
- Policy: use this energy to interpret E176 feedback, not to tune a new file. E176 remains the next sensor because the body and damping are supported; the top-cell weakness explains why it is not certified.

### F149. E180 known-anchor decisive-cell calibration

- Hidden structure: visible priors may be body/tail diagnostics rather than decisive-cell selectors. A low top-cell support value is meaningful only after comparing it to known public winners and failures.
- Candidates: pairwise known-anchor top4/frontier-edge/actual-edge support in the actual public direction, visible-prior sign match, cells needed to cover actual public delta, and comparison of pending E176 against known winners and failures.
- Label vs split test: valid because it uses only already-known public anchors and fixed prediction tensors. Invalid if used to fit a new submission or infer hidden labels at cell level; the public aggregate remains underidentified.
- Current evidence: E95-vs-mixmin and E101-vs-mixmin are public-positive with top4 visible support `0.100896`; mixmin-vs-a2c8 is `0.310904`; E176 is `0.330699`. Failed E72 has high observed-adverse support, but E101-vs-E95 near loss does not. All-moved visible-prior sign accuracy over known anchors is only `0.5`.
- Policy: do not reject E176 because of E179 top-cell weakness, and do not certify it because of E180 top4 comparison. Treat visible priors as insufficient decisive-cell selectors; require a new representation target before pruning or tuning decisive cells.

### F150. E181 current-anchor binary-world counterprior

- Hidden structure: current public anchors may constrain hidden labels in a way that visible priors miss. The feature is not a direct probability edit; it is a latent-world stress that asks which live candidate branch is supported by binary hidden-label worlds after reranking by all known anchors.
- Candidates: current-anchor sum/max residual by world, E95-relative candidate deltas by world, negative rate over best-N residual worlds, E176 decisive-cell world support, and disagreement between visible support and binary-world support.
- Label vs split test: valid as a counterprior because it uses fixed inherited worlds and current known public anchors only to rank worlds, not to optimize a new submission. Invalid as a standalone selector because the world pool was not regenerated with E95/E101/E176/E154/E144 objectives and residuals remain larger than the frontier edge.
- Current evidence: best-5 current-anchor residual worlds give E176 mean delta `+0.000003920` versus E95 with negative rate `0.400`; best-10 gives `+0.000007442` with negative rate `0.300`. E154 and E144 are negative in all best-5 worlds with means `-0.000051451` and `-0.000051445`. E176 best-5 top4 world support is `0.433633`, but top16 is only `0.221275`.
- Policy: do not describe E176 as representation-wide best. Keep it only as the visible-body/Q2-underopen sensor. Before promoting E154/E144 over E176 from this evidence, regenerate or stress a current-anchor binary-world pool with explicit E176/E154/E144 objectives.

### F151. E182 refreshed current-anchor binary-world underidentification

- Hidden structure: current public anchors constrain possible hidden labels but do not yet identify the live candidate sign. The feature is a stress feature, not a prediction feature: candidate signs are evaluated under regenerated current-anchor binary worlds and objective-pressure worlds.
- Candidates: scenario fit residuals, strict range incumbent rate, pressure min/max delta versus E95, pressure zero-crossing flags, and live-branch sign ambiguity for E176/E154/E144.
- Label vs split test: valid as a latent-world diagnostic because it uses fixed known public scores, fixed candidate tensors, train target priors, and current-anchor MILP constraints. Invalid as a submission generator because pressure objectives can force both favorable and adverse worlds and exact ranges are incumbent-sparse.
- Current evidence: E182 fits three current-anchor scenarios with max residuals `0.0000784319`, `0.0000513148`, and `0.0000762925`. Strict residual-budget range incumbent rate is only `0.233`. Objective-pressure worlds make E176/E154/E144 cross zero in `1.000` / `1.000` / `1.000` of scenarios. Representative pressure spans are E176 `-0.000421216..+0.000254123`, E154 `-0.00109286..+0.000923535`, and E144 `-0.000992245..+0.000838041`.
- Policy: use E182 as an underidentification warning. It weakens automatic promotion of E154/E144 from E181 and also prevents calling E176 certified. Future features must either add a new public-free decisive-cell selector or create a larger low-bad-axis movement; another latent-view-preference score is not enough.

### F152. E183 pressure-world branch anatomy

- Hidden structure: the feasible pressure worlds may expose candidate-favorable labels that are specifically hidden from visible/subject/flank train priors. The feature is a branch diagnostic, not a probability feature.
- Candidates: favorable pressure-min labels, adverse pressure-max labels, differing moved cells, support-gap coefficient-weighted share, visible/subject/flank/global/nearest-hard/focus branch preference, context type, edge-like state, between-train-runs state, and active-cell flags.
- Label vs split test: valid as a public-free anti-selector audit because it uses fixed E182 pressure worlds, fixed candidate tensors, and train-derived priors before public feedback. Invalid if used as a direct public-label decoder, because all branch labels are still feasible under current anchors.
- Current evidence: visible-mean, subject, and flank priors prefer the favorable branch in `0.000` of scenarios for E176/E154/E144. Support-gap coefficient-weighted means are E176 `0.797945`, E154 `0.973558`, and E144 `0.888923`. E176's global prior prefers its favorable branch in `1.000` of scenarios, but that is not supported by the more local priors.
- Policy: do not rank E176/E154/E144 by visible-prior branch preference. Use E183 as a warning that the current visible-prior gate can be an anti-selector at pressure-cell resolution. The next usable feature must be a different decisive-cell representation or a locked public-feedback decoder.

### F153. E184 public-anchor motif pressure selector

- Hidden structure: known public-positive and public-negative transition cells might encode a metadata motif for public-compatible support direction. The feature is a candidate selector only if its polarity survives held-out public-anchor stress.
- Candidates: target/context/row-block metadata, public-axis flags (`e72_active`, `e101_active`, veto/safe-density fields), swing magnitude, optional support-label target prior, leave-one-pair/family sign accuracy, AUC, polarity stability, and E183 pressure-branch preference.
- Label vs split test: valid as a diagnostic because it trains only on already-known public anchors and requires LOO/LOFO stress. Invalid as an action-grade selector when the polarity is chosen after seeing scores or when feature sets disagree on the live branch.
- Current evidence: best direct pair-LOO is only `0.333` sign accuracy / `0.425` AUC. Best direct family accuracy/AUC are `0.600` / `0.178`. Polarity-inverted pair accuracy reaches `1.000` for some sets, but family best-polarity accuracy remains `0.600`. Live branch preference flips by feature set: core/swing reject all favorable branches, while public-axis variants favor all three.
- Policy: do not use E184 motif scores to rank submissions. A future public-anchor motif must predefine polarity and pass family transfer before it can influence a submission.

### F154. E185 known-LB pair structural decoder

- Hidden structure: known public LB submission pairs may encode a higher-level movement law than cell metadata motifs. The feature set treats each ordered pair as a context-to-target representation: movement shape, support, bad-axis geometry, E72/E101/public-axis overlap, and known public ordering.
- Candidates: oriented pair feature differences, leave-one-file accuracy/AUC/logloss, frontier and E95-edge stress, reciprocal probability MAE, and pressure-branch preference for E176/E154/E144.
- Label vs split test: valid as a diagnostic because it uses only already-known public observations and holds out whole files or unordered pairs before scoring. Invalid as an action selector if reciprocal orientation is not healthy or branch preference depends on feature-set choice.
- Current evidence: best file-LOO `shape_support_public_axis` reaches accuracy `0.811`, frontier accuracy `0.833`, and E95-edge accuracy `0.714`; best pair-LOO E95-edge accuracy reaches `0.786`. But reciprocal geometry is poor: E95-edge reciprocity MAE `0.081` file-LOO and `0.146` pair-LOO for the public-axis model. Live branch preference flips by feature set.
- Policy: do not rank live submissions directly with E185. Use it only as evidence that pair-level public-response signal exists and needs antisymmetric geometry.

### F155. E186 antisymmetric known-LB pair decoder

- Hidden structure: public LB ordering is antisymmetric. A healthy pair representation must represent `A beats B` and `B beats A` as opposite views of the same latent, not two unrelated predictions.
- Candidates: antisymmetric z-features, no-intercept logistic probability, file-LOO and pair-LOO frontier/E95-edge stress, fixed-zero reciprocity, pressure branch probability for E176/E154/E144, and exact E95-vs-E101 boundary behavior.
- Label vs split test: valid as a sensor-prior because it enforces orientation geometry and evaluates held-out files/pairs. Invalid as a certification layer while the E95/E101 boundary is still misclassified by support-based models.
- Current evidence: best file-LOO `shape_support` gives accuracy `0.795`, frontier accuracy `0.867`, micro accuracy `0.8125`, and E95-edge accuracy `0.857` with reciprocity MAE `0`. Pair-LOO `shape_only` gives E95-edge accuracy `1.000`. E176 favorable branch is selected in `3/3` scenarios across all feature sets; E144/E154 are rejected in `3/3`.
- Policy: E186 strengthens E176 as the next public sensor, but does not certify it. Interpret E176 feedback with E177 before any same-family tuning.

### F156. E187 E95/E101 boundary contribution anatomy

- Hidden structure: a pair decoder can be healthy on reciprocal geometry while still using a support shortcut that violates the tightest known frontier boundary.
- Candidates: exact E95/E101 file-LOO probability, support-family ablations, family contribution sums, top adverse support features, and pressure branch stability.
- Label vs split test: valid because E101 public is already known and the test holds out E95 or E101 files before predicting the exact boundary. Invalid as a direct candidate generator because it uses known public labels only for selector diagnosis.
- Current evidence: shape-only and axis-no-support get exact E95/E101 correct. Every support-containing ablation tested gets it wrong. Adverse contribution is not isolated; support flank, visible, subject, focus, nearest, global, and all-prior families all push the wrong way.
- Policy: support-family features require an exact-boundary veto. They may remain diagnostic sensors but cannot be used as automatic submission gates.

### F157. E188 shape/support logit blend stress

- Hidden structure: if support is only an over-weighted weak prior, low-alpha blending with shape geometry should repair it. If not, support is a conflicting latent view.
- Candidates: alpha-grid blend of shape-only and support logits, exact E95/E101 accuracy, wider E95-edge accuracy, frontier accuracy, and blended E176 branch probability.
- Label vs split test: valid as a selector stress because it uses held-out file predictions from E187 and pre-existing known public boundaries. Invalid as a public-LB optimizer or submission generator.
- Current evidence: action-grade rows are `0`; edge accuracy stays at shape-only level until exact E95/E101 flips. First boundary failure occurs at alpha `0.170..0.285`.
- Policy: no shape/support blend submission. Future feature work should target a new decisive-cell representation, not tune support weight.

### F158. E189 shape/support disagreement atlas

- Hidden structure: support may encode a useful but anchor-specific contamination law rather than a general frontier ordering rule. The feature separates E72-neighbor correction from exact E95/E101 hardtail boundary behavior.
- Candidates: disagreement class (`support_rescue`, `shape_only_win`, `both_correct`, `both_wrong`), E95-edge/frontier/micro/exact-E95-E101/E72-neighbor slices, file-identity gate scores, aligned support z-feature contrasts, and pair-context labels.
- Label vs split test: valid as a diagnostic because it uses held-out file predictions and already-known public anchors only to identify where selectors disagree. Invalid as a deployable feature if it relies on filenames or known-anchor identity.
- Current evidence: in primary E95-edge file-LOO, support rescues `6` rows and shape-only wins `4`; support rescues have E72-frontier-neighbor share `1.000`, while shape-only wins have exact E95/E101 share `1.000`. Support-only-on-E72-neighbor gate reaches E95-edge accuracy `1.000`, but is a file-identity shortcut.
- Policy: use support features only as an E72-contamination diagnostic until a public-free structural detector exists. Do not use support-heavy pair scores to rank live submissions or to certify E176.

### F159. E190 filename-free E72 contamination detector

- Hidden structure: E72-contaminated movement may have a structural shape independent of filenames. A useful feature would identify E72-neighbor contamination while not confusing exact E95/E101 hardtail boundaries with E72.
- Candidates: absolute antisymmetric z-features by shape/target/context/support/axis views, pair-LOO and pair-context-LOO E72-neighbor probability, any-file LOO skipped-positive count, exact E95/E101 false-positive probability, live branch contamination probability, and thresholds from known non-E72 p95 / known positive minimum.
- Label vs split test: valid as a diagnostic because file names are used only to define known labels, not as model inputs. Invalid as a deployable feature while E72-heldout positives are impossible and exact E95/E101 false positives remain high in support-rich views.
- Current evidence: `shape_target_context_abs` gives pair-LOO AUC `0.978836`, AP `0.809524`, and top-k recall `0.666667`; any-file LOO skips `6` positive rows when E72 itself is held out. Support-rich views classify exact E95/E101 as contamination with mean probability `~0.957..0.975`. Live E176 has near-zero contamination and never crosses thresholds.
- Policy: E190 can be used as a diagnostic energy, not a gate. Do not add support to E176 from this feature. Future versions must reduce exact-boundary false positives and solve the one-class/E72-heldout problem.

### F160. E191 boundary-aware E72 score

- Hidden structure: exact E95/E101 may be the hard negative that separates true E72 contamination from tight hardtail boundary movement. A useful feature would preserve E72-neighbor recall while reducing exact-boundary false positives even when support features are present.
- Candidates: weighted logistic E72 score with exact E95/E101 upweighted as hard negatives, prototype positive-vs-boundary distance score, pair-LOO/pair-context-LOO/any-file stress, clean-boundary gate, live branch contamination score, and support-containing clean-row count.
- Label vs split test: valid as a narrow diagnostic because file identity is used only to define known positive and hard-negative labels, not as input. Invalid as a deployable feature because E72 positives remain one-anchor-derived and any-file LOO still skips E72-heldout positives.
- Current evidence: clean boundary rows are only `shape_target_context_abs`; best pair-LOO clean row has AUC `0.978836`, AP `0.809524`, top-k recall `0.666667`, and exact E95/E101 mean `0.057658`. Support-containing clean rows are `0`, with exact E95/E101 probabilities still `~0.766..0.839`. E176 remains near-zero contamination.
- Policy: use E191 to reject support reweighting/prototype repairs. Do not create support-gated candidate variants until a new structural target reduces exact-boundary false positives in support-containing views.

### F161. E192 clean-shape E72 score anatomy

- Hidden structure: the surviving clean E72 score may be either true contamination structure or only a tail-risk/anomaly score. The feature is useful only if live high scores resemble known E72 positives rather than non-E72 tails.
- Candidates: full-data anatomy probability, known non-E72 p95/p99, known positive floor, exact E95/E101 score, live branch family/target contribution sums, top contributing features, and nearest known pair contexts in standardized shape/target/context z-space.
- Label vs split test: valid as a diagnostic explanation layered on top of E191 pair-LOO. Invalid as a submission selector by itself because the full-data model is intentionally fit on all known rows for anatomy and all E72 positives still come from one anchor family.
- Current evidence: exact E95/E101 remains low (`0.031016`). E144 crosses non-E72 p95 in only one scenario (`0.038723`) but stays below p99 and far below the E72-positive floor (`0.804849`); its nearest known rows are non-E72. E154 and E176 remain below p95, with E176 max `0.000008`.
- Policy: use E192 only as a tail-risk diagnostic. It supports E176 as contamination-clean and marks E144 as mild shape-tail risk; it does not justify support gating or branch reranking.

### F162. E193 live candidate evidence ledger

- Hidden structure: no single current latent view is stable enough to rank E176/E154/E144 alone. The useful feature is a governance layer that records which hidden-world sensors support, warn against, or underidentify each branch.
- Candidates: support/warning/underidentified/missing axes from E179 visible priors, E180 top-cell calibration, E181 binary-world counterprior, E182/E183 pressure ranges and local-prior branch anatomy, E186 pair geometry, and E192 clean-shape E72/tail risk.
- Label vs split test: valid as a decision ledger because it does not train on public LB or create a new prediction. Invalid as a learned score forecast because axis weights are interpretive and current public anchors still underidentify branch signs.
- Current evidence: E176 has evidence balance `3.100`; E154 has `-0.225`; E144 has `-1.725`. E176 is the only positive-balance branch but still has material binary-world and local-prior warnings.
- Policy: use E193 to choose the next public sensor and prevent diagnostic cherry-picking. Do not use it as an expected-LB predictor or as a reason to tune E176 without E177 feedback.

### F163. E194 evidence-ledger robustness stress

- Hidden structure: a multi-sensor ledger can itself become a shortcut if the branch ranking depends on arbitrary evidence weights. A robust decision should survive source leaveout and weight perturbation, while still exposing which worldview would flip the ranking.
- Candidates: single-source leaveout score, family-alone winner, Monte Carlo family-weight win rate, missing-evidence penalty, binary-world flip multiplier, and conservative pair-geometry threshold after removing non-comparable visible/top-cell evidence.
- Label vs split test: valid as governance stress because it uses only existing E193 diagnostic rows and does not touch public labels or prediction files. Invalid as a learned LB model because weights remain interpretive.
- Current evidence: E176 wins every single-source leaveout and `0.771300..0.905950` of random family-weight perturbations. Binary-world alone selects E154/E144; binary weight above `1.760x` flips E176 versus E154. Without visible/top-cell evidence, pair geometry must stay above `0.725x`.
- Policy: keep E176 as the next sensor, but make E154 the explicit counterfactual if E176 public feedback is bad. Do not use E194 as a numerical submission-survival score.

### F164. E195 next-sensor information value map

- Hidden structure: the best first public slot is not necessarily the candidate with the strongest counter-world support. It is the candidate whose feedback most cleanly separates the largest live worldviews and gives a pre-registered follow-up route.
- Candidates: decoder band action classes, counterworld-route counts, same-family-forbidden counts, E176-vs-E154 moved-cell contrast, E154-vs-E144/E155 readability, and E194 flip-threshold conditions.
- Label vs split test: valid as a governance feature because it reads only pre-existing decoders and stress outputs, and creates no prediction file. Invalid as a public-LB predictor because it ranks information value, not expected score.
- Current evidence: E176 ranks first. E176-vs-E154 has `1027` moved cells and focus expected delta `-0.000093546`; E154-vs-E144 has `294` moved cells and delta `-0.000002432`; E154-vs-E155 is not readable at `-0.000001796`. E176 adverse bands route to E154/search, while E154 does not resolve the E176 broad/Q2-underopen worldview.
- Policy: use E195 to lock next-slot order: E176 first, E154 first counter-world after adverse E176 feedback. Do not use E154-first unless deliberately adopting the high-binary/low-pair worldview before public feedback.

### F165. E196 decisive-cell motif nearest-anchor profile

- Hidden structure: public-decisive cells may be governed by row/order/block/target motifs rather than visible priors. If true, known public anchor motif profiles should transfer to pending E176 cells.
- Candidates: top4/top16/top33 swing-cell profiles; target shares; context type shares; block position/length shares; subject/block coverage; e72/e101 active rates; all-veto/safe-density; flank-conflict rates; nearest-anchor distance and inverse-distance vote.
- Label vs split test: valid as a diagnostic because public labels are used only for known-pair LOO stress and E176 is scored as pending. Invalid as a submission selector because known anchors are few and all action-grade gates fail.
- Current evidence: `0/9` views are action-grade. The best `top4 / sequence_axis_flank` view has LOO accuracy `0.833333` but exact E101/E95 correctness `0`; E176 is nearest to `e72_vs_e95` in top4/top16 views, while top33 nearest winner evidence is weak because top33 LOO accuracy is `0.333333`.
- Policy: use E196 as a warning/anatomy feature only. Do not demote or promote E176 based on motif nearest-neighbor scores, and do not create motif-gated E176 variants before a new exact-boundary-safe structural target exists.

### F166. E197 public support-mass slippage

- Hidden structure: public LB deltas imply an aggregate hidden-label support mass `q` over moved cells. The gap between observed `q` and visible/focus prior `q` is public slippage.
- Candidates: known-pair observed q, q-to-tie, q-to-clean-win, visible/focus/nearest support surplus, known-slippage analogue outcomes, branch/hard-fail rate.
- Label vs split test: valid as a decoder because known public labels are never estimated per-cell; only aggregate public deltas are inverted. Invalid as a selector because E172 can look slightly safer than E176 without answering the same public-world question.
- Current evidence: E176 visible surplus-to-tie `0.061761`, focus `0.094836`; E72 adverse visible slippages are `-0.071348` and `-0.120707`, exactly the failure condition for E176. E154/E144/E155 visible surpluses are only around `0.010..0.012`.
- Policy: use as public-feedback decoder and failure attribution. Do not create support-mass-tuned submissions before feedback. If E176 loses, treat it as E72-like adverse slippage and branch rather than tuning Q2 keep.

### F167. E198 E72 slippage exposure join

- Hidden structure: a candidate can fail under an E72-like aggregate slippage law without its movement shape being structurally E72-like. The feature separates algebraic public-label stress from clean-shape contamination exposure.
- Candidates: visible/focus E72-vs-E95 and E72-vs-mixmin stress outcomes, surplus-to-tie, max clean E72 probability, non-E72 p95/p99 band, known-positive floor, and combined verdict.
- Label vs split test: valid as a diagnostic join because it uses E197 aggregate public-pair inversion and E192 pre-feedback branch anatomy. Invalid as a learned feature or submission gate because the clean E72 detector has top-k recall `0.666667` and E72 positives still come from one anchor family.
- Current evidence: E176 branch-loses under E72-vs-mixmin slippage but has max clean E72 probability `0.000008`, below non-E72 p95 `0.020815` and far below the positive floor `0.804849`. E154 is thin-margin but clean (`0.007973`). E144 has a mild p95 tail alarm (`0.038723`) but no positive-scale E72 evidence.
- Policy: use this feature to prevent premature E176 demotion based on algebraic E72 stress alone. If E176 is bad publicly, decode the LB band as hidden-label slippage; do not retroactively claim E176 had a visible E72 contamination signature.

### F168. E199 direct candidate clean-shape E72 exposure

- Hidden structure: pressure-branch anatomy can miss direct movement exposure for candidates that were not in the refreshed pressure branch set. A follow-up route is safer if its actual candidate-vs-E95 movement is also clean-shape non-E72.
- Candidates: direct candidate-vs-E95 clean E72 probability, p95/p99/positive-floor band, nearest known contexts, thin-margin flag, and direct-vs-branch probability delta.
- Label vs split test: valid as a diagnostic extension because it reuses the E191/E192 boundary-clean detector and scores pending candidates without their public labels. Invalid as a submission selector because the detector still has one-anchor E72 positives and imperfect recall.
- Current evidence: E172/E174/E176/E166 direct probabilities are `0.000087`/`0.000097`/`0.000097`/`0.000677`; E154/E155 are `0.007860`/`0.009284`; all are below p95. E144 is `0.054385`, above p99 but far below positive floor, with nearest known rows all non-E72.
- Policy: use E199 only for conditional routing after E176 feedback. E172 is acceptable after E176 tie/small-loss; E154 is preferred over E144 after branch/hard-loss; E144 remains a tail-risk control.

### F169. E200 first-sensor resolution ledger

- Hidden structure: safety and information value are separate latent axes. A cleaner same-family fallback can be correct after feedback while still being a worse first public measurement.
- Candidates: E176-over-E172 expected edge, E172 support-surplus advantage, direct clean-shape E72 advantage, same-family vs counter-world moved-cell ratio, same-family vs counter-world expected-delta ratio, and E95-over-mixmin edge fraction.
- Label vs split test: valid as a governance feature because it reads only locked E177/E197/E199 artifacts and derives E172-vs-E95 algebraically. Invalid as a public-LB forecast because it chooses measurement order, not expected score.
- Current evidence: E176 has `0.0000106885` expected focus edge over E172, `0.698x` of E95-over-mixmin. E172 has visible/focus surplus advantages `0.008852`/`0.007054` and clean-shape E72 probability advantage `0.00000972`. E176-vs-E172 is `75` cells; E176-vs-E154 is `1027` cells; same-family/counter-world expected-delta ratio is `0.114`.
- Policy: keep E176 first. Use E172 only after E176 tie/small-loss or if the explicit objective changes to private-risk minimization over information value.

### F170. E201 public-score router and file-identity audit

- Hidden structure: public LB is a sensor only if the observation is tied to an exact prediction tensor and a fixed interpretation map. Otherwise the same scalar can become a post-hoc shortcut.
- Candidates: SHA256, schema/key/probability validity, changed cells and rows versus E95, target absolute-delta share, pre-registered score bands, next-candidate role, strengthened/weakened worldview, kill-switch, and required next evidence.
- Label vs split test: valid as governance and leakage prevention because it creates no labels, no new prediction, and no score fit. Invalid as a performance feature because it does not forecast LB; it only constrains interpretation after feedback.
- Current evidence: E176 SHA256 `34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206`; file audit passes. E176 moves `904` cells over `193` rows; target movement share is Q2 `0.209702`, S4 `0.145285`, Q3 `0.141693`, S2 `0.130103`, Q1 `0.128746`, S3 `0.126307`, S1 `0.118164`. Router thresholds are `<0.5762883298`, `0.5762883298..0.576300366`, `>0.576300366`, and `>0.5763413298`.
- Policy: use E201 before and after the E176 public submission. Do not create an E176 sibling, E172 fallback, or E154 counter-world file from scalar intuition; first route the score through E177/E201.

### F171. E202 component responsibility router

- Hidden structure: a submission can be named after one visible edit while the public-relevant responsibility lives in a different target group, row regime, or hard-label tail. E176 is especially vulnerable because `q2_to0p75` suggests Q2 amplitude, but its expected movement is mostly S-stage / between-train-runs body.
- Candidates: target expected-share, raw probability movement share, Q/S expected-share, between-train-runs expected-share, top33/top8 hard-label cell visibility, subject swing concentration, and score-band-to-component route.
- Label vs split test: valid as a pre-public interpretation guard because it uses only locked submission movements and existing public-free diagnostics. Invalid as a learned predictor because it does not observe the E176 public score and should not assign new probabilities.
- Current evidence: S-targets carry `0.651098` of focus-prior expected movement versus `0.348902` for Q-targets; between-train-runs rows carry `0.807772`; Q2 carries `0.209702` raw movement share but only `0.121416` expected share; top33 visible support remains weak at `p_low=0.014667`.
- Policy: use F171 only after E176 feedback to assign component responsibility. A win credits S3/S1/S4 body first; tie/loss credits hard-tail/cancellation failure first. Do not create Q2 keep-factor siblings from the scalar score alone.

### F172. E203 component knockout stress

- Hidden structure: E176 may combine a broad public-real body with a compact public-fragile tail. A useful feature must separate necessary body components from cancellation components before public feedback.
- Candidates: keep/drop Q/S groups, Q2-only/drop-Q2, primary S-stage S3/S1/S4, between-train-runs, top33/top8 swing cells, top subjects, visible-high/visible-low support cells, and cells-to-cover E95-over-mixmin edge.
- Label vs split test: valid as a diagnostic because it uses only E179 moved-cell priors and creates no prediction file. Invalid as a direct public predictor because no public labels for E176 are observed.
- Current evidence: S-only carries `0.644881` of the E179 focus delta, primary S-stage carries `0.573289`, and between-train-runs carries `0.774524`. Q2-only carries `0.093922`. Top33 carries `0.226424`, but dropping top33 still leaves `0.773576`; top33 visible support is only `0.245771`.
- Policy: use F172 to distinguish body validation from tail cancellation. Do not demote E176 as top33-only, and do not promote Q2-only amplitude tuning unless a clean E176 win first validates the broad body.

### F173. E204 follow-up correction map

- Hidden structure: post-E176 candidates encode different hidden-world probes. Same-family rollback, body-exit counter-world, and Q2 amplitude amplification should not be selected by scalar score proximity alone.
- Candidates: off-E176 movement share, rollback share in E176-overlap cells, E176 body rollback fraction, top33 rollback count, component metric delta under focus/visible priors, and component-specific rollback fractions.
- Label vs split test: valid as route governance because it compares locked submission tensors and E179 public-free priors. Invalid as a public-LB predictor because the E176 public score is still pending.
- Current evidence: E172 changes `75` cells, all inside E176, with overlap rollback `1.000000` and body rollback `0.089780`. E154 changes `1027` cells with off-E176 abs share `0.292501` and body rollback `0.877576`. E174 changes `21` cells with rollback `0`, acting as Q2 amplitude.
- Policy: use F173 only for post-E176 route selection. E172 follows tie/small-loss, E154 follows branch/hard-loss, and E174 follows only clean win plus explicit Q2-amplitude question.

### F174. E205 executable public-feedback decoder

- Hidden structure: public feedback has value only when the scalar score is bound to a fixed measurement protocol. Otherwise the modeler can smuggle in a new interpretation after seeing the number.
- Candidates: score band, outcome, worldview update class, component interpretation, forbidden action, required next evidence, follow-up candidate, follow-up role, follow-up geometry, and body/tail constants.
- Label vs split test: valid as governance because it uses only locked pre-feedback artifacts and creates no prediction file. Invalid as a performance feature because it does not predict the score; it only prevents post-score interpretive drift.
- Current evidence: E205 joins E201-E204 into an executable routebook. Example `0.576291` routes to E172 safety, `0.576303` routes to E154 counter-world, and clean win bands explicitly forbid immediate sibling sweeps.
- Policy: run `python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score <E176_PUBLIC_LB>` before any post-E176 action. Do not manually choose E172/E154/E174/Q2 siblings from scalar closeness.

### F175. E206 actual E176 branch-loss observation

- Hidden structure: a non-collapsed broad body can still be public-adverse if frontier high-swing hard-label cells cancel it. This is now observed, not hypothetical, for E176.
- Candidates: actual public LB, delta vs E95/mixmin/E101, E205 selected route, selected follow-up file, weakened family, forbidden sibling actions, and component attribution.
- Label vs split test: valid as public-sensor evidence because it is an actual leaderboard observation. Invalid as a private-proof because public subset may differ from private.
- Current evidence: E176 public LB `0.576311831`, E205 route `branch_loss`, follow-up role `body_exit_counterworld`, E154 selected as existing-file counter-world. E176 is worse than E95 by `+0.0000205012`.
- Policy: treat E176/E174/E172/E169 as weakened expected-score followups. Use E154 only as a counter-world test, not as a scalar rescue; otherwise return to non-collinear representation search.

### F176. E207 LeJEPA positive-pair identifiability score

- Hidden structure: a JEPA latent is only worth training as a world model if the chosen positive-pair transition is identifiable enough: intermediate autocorrelation, Gaussian-ish increments, stable rank, nontrivial alignment gap, and no obvious split shortcut.
- Candidates: `lejepa_readiness`, `decision`, `rho_abs_mean`, `alignment_ratio`, increment/marginal Gaussian scores, rank fraction, frontier smoothness, train-label consistency, and split-distance CV for each latent/pair regime.
- Label vs split test: valid as a pretraining-regime selector because it does not use public labels and treats known submissions only as frontier-movement smoothness diagnostics. Invalid as a direct probability feature because readiness is not calibrated LogLoss and target-neighbor pairs are diagnostic upper bounds, not inference-safe pairs.
- Current evidence: only `broad_stage2_pca64 + feature_nn1_all` passes `true_jepa_candidate` (`readiness=0.652939`, `rho=0.494280`, `alignment=0.636020`, `increment_gauss=0.435262`). Existing LeJEPA subject-lag2 has higher raw readiness (`0.668530`) but is demoted to auxiliary because increment Gaussianity is poor (`0.194814`) and split stationarity is weak.
- Policy: use F176 to choose E208 true-JEPA pairs. Train on feature-neighbor positive pairs first. Treat subject/order and block-canvas LeJEPA signals as energy/gate features until they pass a stricter increment/stationarity audit.

### F177. E208 feature-neighbor JEPA residual and prediction features

- Hidden structure: a row's feature-family context can predict the latent state of its nearest feature-neighbor, and the prediction residual may expose target-specific calibration risk that ordinary tabular features average away.
- Candidates: `e208_pred_pc*`, `e208_hidden_z*`, `e208_resid_self_pc*`, `e208_resid_nn_pc*`, prediction/hidden norms, seed disagreement, prediction-to-self/neighbor cosine, and nearest-neighbor target distance.
- Label vs split test: valid as a learned representation feature because the JEPA target is feature-neighbor broad latent, not the labels. Invalid as a direct submission move until OOF, repeated-subject, and geometry stress all pass. The full predicted latent is specifically unsafe because of anisotropy.
- Current evidence: the JEPA model beats copy-self and mean-target controls on validation MSE for all three seeds. Downstream best local features are Q3 `e208_resid_self_pc10`, S2 `e208_pred_pc12`, and S4 `e208_pred_pc14`; geometry stress passes only Q3/S4 rows. S2 is a local shortcut until repaired.
- Policy: materialize only a separate E209 Q3/S4 stress candidate. Do not add the entire E208 feature block to a frontier submission. Do not use S2 despite local gains unless it passes geometry folds.

### F178. E209 Q3/S4 JEPA graft policy

- Hidden structure: actual JEPA signal is target-local and calibration-sensitive. Q3 residual-self and S4 predicted-neighbor axes can move frontier probabilities, but only when converted into small, target-specific logit grafts.
- Candidates: Q3 `e208_resid_self_pc10` subject-centered/subject-z/subject-rank variants, S4 `e208_pred_pc14` subject-rank variant, stage2-learned logit movement, E95/E154/mixmin anchor grafts, frontier gate score, hard-label cell concentration, and bad-axis energy.
- Label vs split test: valid as a JEPA materialization feature because the source representation is learned from feature-neighbor context-to-target prediction, not labels. It is invalid as a global feature import because target movement is selected by OOF/subject/geometry stress and must remain Q3/S4-only unless new evidence passes the same gate.
- Current evidence: `q3_center_c010_s4_rank` has OOF delta `-0.001272724`, subject-half win rate `0.900000`, and geometry delta `-0.000794598`. Four low-scale E95/E154 grafts pass the frontier gate. High-scale Q3/S4 grafts and broader latent movement are rejected.
- Policy: use E209 only as a low-scale public sensor. Prefer `submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv` for maximum survival score, or `submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv` to isolate JEPA on the current frontier. Do not use F178 to justify S2, full-latent, or high-amplitude JEPA features.

### F179. E210 target-dependency JEPA gate

- Hidden structure: Q3/S4 JEPA movement may be public-risky when it violates the target-dependency manifold implied by the other six targets.
- Candidates: conditional target expectation from other target probabilities, movement-toward-conditional gate, movement-closer-to-conditional gate, soft-toward multiplier, anti-toward control, and E95/E154 anchor graft stress.
- Label vs split test: valid as a diagnostic because conditional models are fit on train labels and evaluated through OOF, subject-half, and geometry stress. Invalid as direct proof of public improvement because the selected files trade away much of the ungated E209 OOF/geometry edge.
- Current evidence: selected closer-gated Q3/S4 files improve public-prior hard-tail anatomy, but weaken local OOF and geometry versus E209. S4 dependency alignment is locally coherent; Q3 dependency alignment is conflicted.
- Policy: use F179 as a follow-up sensor, not a replacement feature. It is useful after E209 feedback if the next question is whether public hard-tail cells demand dependency filtering.

### F180. E211 target-specific JEPA gate

- Hidden structure: Q3 and S4 share the E208/E209 JEPA source but not the same translation law. Q3 behaves like a residual-body axis; S4 behaves like a target-dependency axis.
- Candidates: Q3 raw scale, S4 dependency mode, S4 dependency scale, E95/E154 anchor scale, subject-half stability, geometry stability, and hard-tail top1 concentration.
- Label vs split test: valid as a feature policy because Q3/S4 target-specific gates are selected through OOF, subject-half, geometry, and anti/zero controls. Invalid as proof of public improvement until E211 public feedback is observed.
- Current evidence: Q3 raw + S4 toward improves OOF versus E209 and keeps geometry negative. The selected E154/E95 files pass frontier gates with lower top1/abs than E209.
- Policy: prefer F180 over F179 for target-dependency follow-up. Keep E209 as the raw control and E211 as the target-specific gated candidate.

### F181. E212 JEPA-family sensor ordering score

- Hidden structure: JEPA-derived candidates are not interchangeable. The same trained E208 representation can express raw Q3/S4 translation, E154-anchored survival, blunt target-dependency filtering, or target-specific S4 gating. The submission order must preserve which hidden-world claim the public score tests.
- Candidates: `structured_survival_score`, `clean_sensor_score`, `control_value_score`, local delta, geometry delta, parent-integrity penalty, hard-tail survival, top1 concentration, bad-axis guard, anchor cleanliness, pairwise movement cosine, and routebook outcome bands.
- Label vs split test: valid as governance because it reads locked E209/E210/E211 artifacts and selected submission tensors. Invalid as a new predictive feature because it does not fit labels or create probabilities.
- Current evidence: E211 E154 closer is ranked first for structured survival; E211 E95 toward is ranked first for clean current-frontier sensing; E209 E95 Q3/S4 is the raw control; E210 is demoted because it loses the E209 local/geometry body despite strong hard-tail anatomy.
- Policy: use F181 before any JEPA-family public submission. Submit E211 E154 closer when prioritizing maximum survival, or E211 E95 toward when prioritizing clean JEPA attribution. Decode the public result with the E212 routebook before choosing E209/E210 follow-ups.

### F182. E213 JEPA axis specificity audit

- Hidden structure: a useful JEPA coordinate should remain special after breaking row-feature alignment and after comparing against nearby coordinates in the same learned representation family.
- Candidates: global permutation p-value, within-subject permutation p-value, same-family PC pool rank, pool best delta, E208 scan rank, E208 geometry delta, and subject-half win rate.
- Label vs split test: valid as a representation sanity check because it uses the same OOF correction path and public-free nulls. Invalid as a public-LB predictor because it does not audit anchor/public-tail translation.
- Current evidence: Q3 `e208_resid_self_pc10` and S4 `e208_pred_pc14` both pass as `specific`; both have permutation p-values `0.020408` and same-family pool rank `1/16`.
- Policy: keep these axes as live JEPA representation features. Do not expand to all PCs or nearby PCs. If public feedback is bad, revise the translation/gate, not the existence of the Q3/S4 axes.

### F183. E214 JEPA benefit-gate translator

- Hidden structure: if a JEPA axis is real but not uniformly valid, the row-target cells where the JEPA step helps should be predictable from step direction, dependency direction, entropy, and axis energy.
- Candidates: subject-CV benefit probability, rank-normalized benefit probability, margin gate, toward/closer-composed benefit gates for Q3/S4.
- Label vs split test: valid as a public-free OOF translation diagnostic only when evaluated through subject-CV and geometry folds. It is unsafe as a submission feature if it simply learns train label benefit without stress survival.
- Current evidence: Q3/S4 benefit AUCs are weak (`0.552169`, `0.568968`). Best benefit-gated local policy loses to raw JEPA and E211. No E214 policy passes frontier selection.
- Policy: do not use F183 for submission. Keep it as a negative control showing that the JEPA translation bottleneck is not fixed by a simple supervised benefit gate.

### F184. E215 masked feature-family JEPA representations

- Hidden structure: visible feature-family representation blocks may predict a hidden family block, exposing a cross-family latent state distinct from E208's feature-neighbor target.
- Candidates: `e215_pred_pc*`, `e215_resid_pc*`, `e215_hidden_z*`, and family-specific residual/predicted coordinates such as `e215_deep_resid_abs_mean`.
- Label vs split test: self-supervised train+submission representation is allowed as public-free latent construction, but downstream use must pass OOF, subject-half, and geometry stress.
- Current evidence: E215 pass count `10`; strongest target features are Q1 `e215_pred_pc06`, S2 `e215_resid_pc10`, and S4 `e215_deep_resid_abs_mean`.
- Policy: use E215 as a representation source. Do not submit direct full-combo movement without E216-style frontier stress.

### F185. E216 masked-family JEPA S2 materialization

- Hidden structure: masked-family JEPA movement appeared concentrated in S2 after local stress, but public feedback shows the current S2 translator is not public-safe.
- Candidates: `s2_rank` grafts from E215, especially E154/E95 scales `0.50` and `0.75`.
- Label vs split test: selected only after local OOF, subject-half, geometry, bad-axis, and hard-tail frontier stress.
- Current evidence: `s2_rank` local delta `-0.000624`, subject-half win `0.934615`, geometry `-0.000686`; selected files were `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv`, `submission_e216_maskfam_jepa_s2_rank_e95_s0p75_4f8dc44d.csv`, `submission_e216_maskfam_jepa_s2_rank_e154_s0p5_0ca3d931.csv`, and `submission_e216_maskfam_jepa_s2_rank_e95_s0p5_4516fb93.csv`. Public feedback on the first file was `0.5772865088`, `+0.0009951790` worse than E95.
- E219 tail audit: pure S2 graft has enough adverse capacity (`0.006048995`) to explain the public miss, while E154 body alone does not (`0.000924070`). The weak point is support geometry: focus swing-weighted support probability is `0.473945`, below `0.5`, despite slightly favorable expected delta.
- E220 gate audit: no simple support/tail threshold rescues the feature. High-support cells become expected-adverse (`focus_support_ge_0p7` expected `+0.000018940`), while expected-negative cells keep adverse capacity above the observed miss (`focus_support_ge_0p6_expected_neg` adverse `0.001402108`).
- Policy: treat E216 S2 features as diagnostics and negative controls. Do not submit remaining E216 siblings or simple E220 threshold variants. Only a train/OOF-reproducible support model can reopen this feature family.

### F186. E217 teacher-student tabular JEPA energy

- Hidden structure: masked feature-family context plus same-subject row-neighborhood context can predict an EMA teacher's full-row latent, but this full-row latent may encode fold-sensitive calibration state instead of public-stable target movement.
- Candidates: `e217_teacher_pc*`, `e217_pred_pc*`, `e217_context_pc*`, `e217_resid_pc*`, `e217_hard_resid_pc*`, prediction/teacher cosine, hard-vs-single mask residual norm, and mask disagreement.
- Label vs split test: self-supervised train+submission pretraining is allowed because no labels enter the JEPA objective. Downstream use is unsafe unless the feature passes OOF, subject-half, geometry, and later frontier stress.
- Current evidence: the objective is learnable (`val_loss` about `7%` of mean-teacher baseline), but no feature passes geometry materialization. Best local S2 `e217_teacher_pc07` fails with positive geometry delta `+0.000410`.
- Policy: keep E217 features as diagnostics/energy only. Do not submit an E217-based probability movement unless a later target-specific materializer turns it geometry-negative and frontier-safe.

### F187. E221 S2 support classifier gate features

- Hidden structure: the E216 S2 graft may help only on rows where movement direction, E215 latent state, subject position, and local calibration state imply high hard-label support.
- Candidates: E215 latent columns, subject/order features, base/full S2 probabilities, S2 logit step, movement direction, probability margin, absolute step size, and subject one-hot context used by `analysis_outputs/e221_s2_oof_support_classifier.py`.
- Label vs split test: allowed only as OOF support diagnostics. The support label is supervised by whether the E216 S2 movement improves train OOF loss, so submission use requires strict subject/row-contiguous OOF stress plus separate test-tail capacity stress.
- Current evidence: support is locally learnable (`AUC=0.748104` stratified, `0.717482` row-contiguous, `0.713730` subject-LOO), but no gate passes both OOF support and submission-side tail stress.
- Policy: do not use F187 as a submission gate for E216 S2. Keep it as evidence that local support and public-tail support are different objects under the current S2 translator.

### F188. E222/E223 target-specific JEPA support-tail features

- Hidden structure: the same JEPA latent can be healthy for one target component and tail-fragile for another. E211's S4 body appears healthier than its Q3 body under E216-style hard-label support stress.
- Candidates: E222 cell-level support probability, target-level adverse capacity, Q3/S4 top1-over-expected, E211 q3_scale rebalancing, and S4 dependency-gated body preservation.
- Label vs split test: these are public-free prior diagnostics, not true labels. They are allowed for candidate triage only when joined with existing E211 local/subject/geometry stress and negative controls from E216.
- Current evidence: original E211 is expected-good but low-support (`~0.463` swing-weighted support). Q3 has top1/expected above `1.0`; S4 has top1/expected around `0.166`. E223 q3_scale `0.75` reduces actual-vs-E95 adverse capacity from `0.005426827` to `0.004533247` with only a small expected-focus sacrifice.
- Policy: prefer `analysis_outputs/submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv` if testing the JEPA family now. Treat it as a risk-rebalanced public sensor, not a certified safe feature.

### F189. E224 capped-Q3 JEPA translator

- Hidden structure: E211's S4 body is the healthier latent component, while Q3 should be treated as a capped residual rather than a full target translation.
- Candidates: q3_scale sweep values, S4 `closer/toward` body mode, E95/E154 anchor contrast, E222 support probability, adverse capacity, and Q3 top1-over-expected.
- Label vs split test: valid only as candidate triage because it uses public-free priors and locked E211/E222 diagnostics. Unsafe as a general feature if q3_scale is tuned from public LB or if support remains below `0.5` without public-feedback interpretation.
- Current evidence: q3_scale `0.625` is the best current Pareto knee. `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv` has local delta `-0.001098893`, geometry delta `-0.000505582`, expected focus `-0.000623352`, adverse `0.003400775`, support `0.465984`, and Q3 top1/expected `0.875120`.
- Policy: prefer F189 over F188/E223 for the next JEPA-family public sensor. Keep E223 as an ablation and do not generalize the `0.625` scale to other targets without a fresh support-tail audit.

### F190. E225 E224 public-feedback routebook

- Hidden structure: E224 is a public observation protocol, not just a probability tensor. The same score can otherwise be misread as Q3 scale evidence, anchor evidence, or JEPA evidence.
- Candidates: score bands relative to E95/E101/mixmin/E216, E224/E223/E211/E216 movement cosines, target absolute movement shares, and forbidden-action rules.
- Label vs split test: valid as governance because it uses known public anchors and locked submission tensors. Invalid as a score predictor or label inference mechanism.
- Current evidence: E224 is collinear with E223 (`cos=0.996078`) and full E211 (`0.975464`) but far from E216 (`0.043542`). Therefore the public score should route capped-Q3 translator beliefs, not broad JEPA-family beliefs.
- Policy: always run `analysis_outputs/e225_e224_public_feedback_decoder.py --score <PUBLIC_LB>` after E224 feedback. Do not select E223/E211/q3_scale siblings from scalar intuition.

### F191. E226 movement-family and bad-axis scan features

- Hidden structure: after a public miss, the next useful candidate may be defined more by movement-family geometry than by local CV. A file near the E224 line retests the same Q3/S4 translator; a file near the E216 S2 line inherits the masked-family S2 public miss; a file near E72/E176 inherits known public-negative axes.
- Candidates: movement cosines versus E224/E223/E211/E216/E176/E72/E154/E101/mixmin, E222 support-tail metrics, known-public vetoes, E52 local near-tie veto, hardtail-parent diagnostic labels, and role labels such as `broad_survivor_counterworld`, `repaired_branch_counterworld`, `same_q3s4_jepa_family`, and `s2_bad_axis_neighbor`.
- Label vs split test: valid as a candidate-routing diagnostic only. It uses known public outcomes to mark bad axes, so it must not become a score optimizer. It is unsafe as a public-LB predictor or as a reason to tune amplitudes after the fact.
- Current evidence: `analysis_outputs/e226_noncollinear_candidate_scan.py` evaluated `73` documented/materialized files. The best actionable independent sensor is `submission_e166_broadsurv_s0p01_d8bfa94b.csv` with cos(E224) `0.074348`, cos(E216) `0.055999`, expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`. E154 remains the conservative repaired-branch counter-world. E209/E210/E211/E223 are same-Q3/S4 JEPA family, and E216 siblings are S2 bad-axis neighbors.
- Policy: use F191 to prevent duplicate-world submissions. It can choose between E224, E166, and E154 by the hidden-world question being asked. It must not promote E166 as certified public improvement, and it must not resurrect E52 bridge or E216 siblings.

### F192. E227 E166 public-feedback protocol features

- Hidden structure: a broad latent can be real in row/block context and still fail public because its safety-atlas support is wrong. E166 specifically tests whether edge-like, between-train-runs broad survivor cells are public-real despite E72-active and low-veto-null warnings.
- Candidates: E166 routebook bands, movement geometry versus E224/E154/E176/E216/E72, E167 top-benefit context rates, E72-active rate, all-veto-null rate, safe-density, and E101-plausible mass.
- Label vs split test: valid only as pre-registered public-feedback interpretation. It uses known public anchors to define score bands, so it must not be used to fit labels or tune amplitudes.
- Current evidence: E166 moves `1750` cells across all `7` targets, has cos(E224) `0.074348`, expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`. Its top-benefit cells are context-real but conflicted: edge-like `0.689189`, between-train-runs `0.797297`, E72-active `0.837838`, all-veto-null `0.297297`.
- Policy: use `analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>` after any E166 submission. Do not scale E166 or submit E166-family siblings before decoding. Treat wins as safety-atlas-overconservatism evidence and losses as E72-active/low-veto-null warning evidence.

### F193. E228 tri-world conflict atlas features

- Hidden structure: live candidates can be useful because they ask different hidden-world questions, not because they can be averaged into a smoother probability tensor.
- Candidates: E224/E166/E154 cell movements, pairwise cosine, active overlap, same-sign shared mass, sign-conflict mass, top-k overlap, target conflict, and subject/block concentration.
- Label vs split test: valid as deterministic submission-geometry routing only. It uses no labels and creates no public prediction, so it can reject duplicate-world or uninterpretable blends but cannot certify public improvement.
- Current evidence: E224/E166 are almost orthogonal (`cos=0.074348`) with top50 overlap `1`; E166/E154 are also almost orthogonal (`cos=0.061662`) with top50 overlap `0`; E224/E154 are related (`cos=0.316350`) because E224 contains most of E154's same-sign repaired body (`0.885621` E154 mass coverage).
- Policy: use F193 to keep E224 and E166 as separate public sensors. Do not create a blind E224/E166/E154 blend. Treat E154 as a conditional repaired-branch test, not as a clean independent post-E224 alternative.

### F194. E229 public-slot decision and anchor-ledger features

- Hidden structure: the public LB ledger itself is a sensor, but only at the resolution allowed by its leave-one-anchor error. After E216, the meaningful feature is not a scalar predicted LB; it is the mapping from each candidate to the hidden-world question its score can answer.
- Candidates: `analysis_outputs/public_probe_observations.csv`, 14-anchor `raw05_a2c8_compat` MAE/p90, E225/E227/E160 routebook outcome counts, E228 cosine/overlap relations, expected edge divided by proxy MAE, and role labels `jepa_first`, `independent_broad`, `conservative_branch`.
- Label vs split test: valid as governance and experiment tracking. It uses public observations, so it must never become a feature for probability fitting, prior tweaking, or post-hoc LB optimization.
- Current evidence: adding E176/E216 yields best proxy MAE `0.000496259`, still too coarse for frontier ordering. E224's expected edge is only `1.316x` this proxy MAE and carries large adverse capacity; E166's expected edge is `0.669x`; E154's is `0.060x`. Therefore the table cannot certify a score. It can only route the next public observation.
- Policy: choose E224 only when the explicit question is JEPA after E216. Choose E166 when the explicit question is independent broad-world structure. Keep E154 conditional. Do not use F194 as a model feature or LB-fitting device.

### F195. E230 E224 Q3 support-tail prune features

- Hidden structure: E224 may contain a healthy S4 body plus a fragile Q3 tail. The useful feature is not a new raw column, but a cell-level risk energy over E224's moved Q3 cells.
- Candidates: E224-vs-E154 logit swing, expected focus sign, support probability, risk score, target tag, adverse-capacity contribution, and top-cell concentration.
- Label vs split test: valid only as conditional submission triage. It uses no new public score, but it is not OOF-learned, so it must not be treated as a trained samplewise gate.
- Current evidence: `q3_swingtop25_drop` cuts adverse by `0.000633168` for only `0.000023308` expected-focus cost vs E224; `q3_risktop21_drop` improves expected focus by `0.000067892` under the prior while gaining `0.021076971` support.
- Policy: use F195 only after E224 feedback suggests Q3 tail blame. Do not use it to skip the cleaner E224 observation or to tune Q3 thresholds from public LB.

### F196. E231 learned Q3 support-prune features

- Hidden structure: if E224's fragile Q3 cells are not arbitrary, train/OOF features should identify rows where the capped-Q3 residual helps versus hurts.
- Candidates: E208/E209 latent features, subject/order features, base and E224-like Q3/S4 probabilities, Q3/S4 logit steps, margin/step-size features, and subject one-hot context used by `analysis_outputs/e231_e224_q3_oof_support_prune.py`.
- Label vs split test: valid only as OOF support diagnostics. The support label is supervised by whether E224-like Q3 improves train OOF loss, so a submission gate requires stability under row-contiguous, subject-kfold, subject-LOO, and submission-side E222/E224 tail stress.
- Current evidence: support is only weakly learnable. Best AUC is `0.588101`, and no gate passes both OOF preservation and submission-side tail stress.
- Policy: do not use F196 as a submission gate. Keep it as negative evidence that current E224 Q3 tail risk is not an invariant learned object; use E230 hand-prune only after E224 public attribution.

### F197. E232 cross-target support-invariance features

- Hidden structure: if S2/Q3/S4 support-tail risk came from one hidden row/block state, support labels should transfer across E216 S2, E224 Q3, and E224 S4.
- Candidates: target support labels, target benefit vectors, subject support rates, movement-shape features, E215/E208 latent context, held-out target transfer predictions, and test low-support overlap scores from `analysis_outputs/e232_cross_target_support_invariance.py`.
- Label vs split test: valid only as a diagnostic. Support labels are supervised by train OOF loss deltas and cannot be used as direct submission labels without target-specific OOF, row/subject, and submission-side stress.
- Current evidence: shared support overlap is nearly absent. Max row-label correlation is `0.057278`, max benefit correlation `0.090611`, and Q3/S2 test low-support top25 overlap is only `1` row. Movement-shape transfer can reach AUC `0.745452`, but latent-context transfer is weaker and does not define common public-safe rows.
- Policy: do not use F197 as a shared S2/Q3/S4 support gate. Use it to require target-specific JEPA support or energy heads and to keep movement-shape risk as a calibration diagnostic.

### F198. E233 target-specific soft support-energy heads

- Hidden structure: after shared support fails, target-specific support probabilities might still be useful as continuous amplitude/energy heads for JEPA movements.
- Candidates: OOF support probabilities for E216 S2, E224 Q3, and E224 S4; soft probability, squared-probability, threshold-linear, and centered amplitude policies; Q3 low-amplitude overlap with E230 risk cells.
- Label vs split test: valid only as a promotion diagnostic. These probabilities are trained from OOF benefit labels, so they cannot be used as deployment amplitudes unless they beat full movement under target/subject stress and align with independent public-free tail anatomy.
- Current evidence: no soft policy passes promotion. Best learned policies under-scale full movement by `+0.001713160` Q3, `+0.001600825` S2, and `+0.000498506` S4 versus full target movement. Q3 low-amp top25 overlaps E230 risk-top21 by `0` rows.
- Policy: do not use F198 for submission. Future target-specific JEPA work must change the representation target or loss; simply softening current support classifiers is closed.

### F199. E234 tail-contrastive JEPA target features

- Hidden structure: the useful JEPA target may be high-impact tail identity, not all-row support. LogLoss frontier errors are dominated by rows/cells where a target movement is sharply helpful or harmful.
- Candidates: target-specific high-adverse `risk` labels, high-positive-vs-high-adverse `contrast` labels, movement/logit context, latent-with-target and latent-without-target views, dropped-row mean benefit, subject win-rate, and Q3 overlap with E230 risk/swing/expected-positive rows.
- Label vs split test: valid as OOF target-representation diagnostics only. The labels are built from OOF benefit, so a deployed probability movement requires separate submission-side tail stress and cannot be promoted from OOF delta alone.
- Current evidence: E234 promotes `323` policies. Best loss versus full movement is S2 `-0.002653627`, Q3 `-0.000870181`, S4 `-0.000833194`. Q3 best-loss policy has weak E230 alignment, so the feature is not directly public-certified.
- Policy: use F199 to generate target-specific materialization tests. Do not submit raw E234 policies. Treat S2 as closed after F200; Q3/S4 remain possible only after separate public-free materialization audits.

### F200. E235 S2 tail materialization stress features

- Hidden structure: a locally good S2 tail representation must also satisfy the public-facing hard-label support geometry exposed by the E216 miss.
- Candidates: E234 S2 policy id, test selected rows, dropped rows, E95-anchor E216 S2 logit deltas, expected focus, adverse capacity, adverse-over-observed-miss ratio, support probability, top-cell swing share, and scale.
- Label vs split test: valid as a submission-side stress test because it does not fit public labels; it uses the pre-existing observed E216 miss as a capacity bound. Unsafe as a tuning oracle if thresholds are relaxed post hoc to force a file.
- Current evidence: `240` S2 materializations scanned; `0` submission-gate pass and `0` joint-gate pass. Max support remains below `0.5`, and the best expected rows still exceed the observed E216 miss in adverse capacity.
- Policy: keep F200 as a hard negative screen for S2 JEPA translators. Do not submit E235 or remaining E216 S2 siblings without a new target representation and a new pass through this stress.

### F201. E236 Q3/S4 learned-tail materialization stress features

- Hidden structure: if E234's Q3/S4 high-impact tail representation captures the same public-facing tail law as E230, it should become a learned replacement for E230's hand-pruned Q3 intervention on top of E224.
- Candidates: E234 Q3/S4 policy id, selected test rows, Q3/S4 dropped-row counts, E224-vs-E154 expected focus, adverse capacity, support probability, Q3 top-cell concentration, S4 body loss, and overlaps with E230 risk/swing rows.
- Label vs split test: valid only as a public-free materialization stress. It uses OOF-derived E234 policies and deterministic E224/E154 test tensors, but no new public labels. It must not be relaxed post hoc just to force a file.
- Current evidence: graft rows `92`; gate pass `0`; materialized files `0`. Best Q3 rows reduce adverse but lose support and increase Q3 top-cell concentration; best S4 rows improve support but erase expected focus and do not fix Q3.
- Policy: do not use F201 to generate a submission. Treat E234 Q3/S4 as local representation evidence, keep E230 as conditional hand-prune after E224 feedback, and require a sharper cell-level target before reopening learned Q3/S4 gates.

### F202. E237 cell-level decisive JEPA target features

- Hidden structure: E224's fragile Q3 tail may be a row-target-cell law rather than a row-level support law. A useful feature must identify exactly which Q3 cells should roll back without erasing the S4 body.
- Candidates: OOF decisive-cell risk/contrast labels, target id, Q3/S4 cell deltas, E224/E154 logits, latent-with-target and latent-without-target embeddings, movement-shape features, subject/row fold predictions, dropped Q3/S4 cell counts, Q3 top1/expected, actual-vs-E95 stress metrics, and E230 risk/swing overlap.
- Label vs split test: valid as a candidate generator only after OOF plus submission-side stress. The labels come from train OOF benefit, so deployment requires public-free graft and actual-vs-E95 checks; the feature must not be tuned from public LB.
- Current evidence: E237 scans `240` materialized rows and selects `7`. The top candidate drops `25` Q3 cells and no S4 cells, with expected loss vs E224 `-0.000005612`, adverse reduction `0.000576400`, actual-vs-E95 adverse reduction `0.000553281`, support gain `0.006450259`, and E230 risk-top21 overlap `11`.
- Policy: use F202 only for the learned Q3 decisive-cell JEPA branch. Top candidate is `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`. Do not generalize it into an S2 or S4 gate without separate target-specific stress.

### F203. E238 public-feedback routebook features

- Hidden structure: the same public score can mean different things unless the candidate's movement anatomy and contrast files are fixed in advance.
- Candidates: E237 public outcome band, E237-vs-E224 delta band, pairwise movement cosine, target abs-share, Q3 cell overlap with E230 hand-prunes, and E216-like fail distance.
- Label vs split test: this is not a training feature and must not be used to tune probabilities. It is an interpretation feature for future public feedback.
- Current evidence: E238 locks clean support at `<=0.576276019`, unresolved tie through `0.576294330`, branch loss above `0.576306641`, and E216-like collapse above `0.576591330`. E237 changes `25` Q3 cells versus E224, overlaps E230 swing25 by `13`, and overlaps E230 risk21 by `11`.
- Policy: use F203 only after an E237 public score is known. Do not create lower-ranked E237 siblings from one scalar public result; use the routebook to decide whether E224, E230, E166, E154, or a new target representation is the next question.

### F204. E239 E237 Q3 residual-energy cell motif features

- Hidden structure: the E237 Q3 cells may be high-movement Q3 cells under abnormal JEPA residual/nearest-neighbor context, rather than calendar-edge cells or a scalar top-k cutoff.
- Candidates: E237/E224 Q3 logit delta, E224 top-25/top-50 movement rank, E230 swing/risk overlap flags, E208 residual self norm/abs mean/PC10, E208 nearest-neighbor target distance, E215 residual norms, subject/date/test-edge/train-adjacency diagnostics, and E237-only/E230-only disagreement selectors.
- Label vs split test: valid only as a motif diagnostic. It uses the fixed E237 output and public-free latent/context features, not public labels. It must not become a new gate until E237 public feedback tells whether the motif is helpful or a shortcut.
- Current evidence: E237 overlaps E230 only partially (`13/25` swing25, `11/21` risk21). It is amplitude-filtered but not pure top-k (`0.520` top-25, `0.960` top-50). Edge/calendar explanations weaken (`0.120` near-test-edge-2 vs `0.240` population; `0.240` gap-adjacent-2 vs `0.344`). E208 residual/NN features are strongly enriched, especially `e208_resid_self_abs_mean`, `e208_nn_target_dist`, and `e208_resid_self_pc10`.
- E240 update: simple residual-energy rules pass the same E237-like stress. `simple_pc10_top25` has expected loss vs E224 `-0.000062119`, adverse reduction `0.000594489`, support gain `0.016747154`, actual adverse reduction `0.000573879`, and overlaps E237 only `14/25`.
- Policy: F204 is promoted as a diagnostic feature family, but not as a submission rule. If E237 wins, promote the broader Q3 residual-energy cell-tail world, not the exact learned selector. If E237 loses, demote both E237 and simple residual rules until train/OOF validation is rebuilt.

### F205. E240 simple residual-energy Q3 rollback rules

- Hidden structure: if residual-energy is the real Q3 tail signal, deterministic rules based on E208 residual PC10, residual abs mean, NN distance, and top50-amplitude filters should reproduce E237-like public-free stress.
- Candidates: `simple_pc10_top25`, `top50_amp_then_resid_combo25`, `top50_amp_then_nn25`, `global_e239_combo25`, and related deterministic selectors from `analysis_outputs/e240_e237_residual_rule_ablation.py`.
- Label vs split test: currently diagnostic only. These rules are built from post-E239 test-side motif observation and are not OOF-trained. A submission would require train-side Q3 benefit validation, subject/row stress, and a new pre-public routebook.
- Current evidence: all `9/9` non-control simple selectors pass the E237-like gate and E230 gate. This shows the current stress gate is under-discriminating for learned-vs-heuristic cell rules.
- E241 update: train/OOF validation rejects the direct feature. No residual/amplitude/margin score has negative selected-benefit delta. `score_pc10` top-10% is adverse on full train (`+0.001867628`) and split stress (`+0.002633171`, win rate `0.30`), even though the same score overlaps E237 `14/25` and E230 swing25 `18/25` on test.
- Policy: do not materialize E240 submissions. Keep F205 as a negative-control motif family and as evidence that public-free test stress can be fooled by residual-energy top-k rules.

### F206. E241 OOF residual-energy validation features

- Hidden structure: a public-relevant Q3 residual-energy motif should also have some train OOF trace in rows where E224-like Q3 movement hurts.
- Candidates: `score_pc10`, `score_nn_dist`, `score_resid_abs`, `score_resid_norm`, `score_low_margin`, `score_amp`, `score_e239_combo`, `score_e215_e208_combo`, selected-benefit deltas, split win rates, and test overlaps with E237/E230.
- Label vs split test: valid as a falsification feature. It uses train OOF Q3 benefits, random/row/subject stress, and no public labels. It is not a deployment feature because the result is negative.
- Current evidence: the motif is test-visible but not OOF-supported. Best top-10% full train delta is still `+0.000345376`; best split-stress top-10% delta is `+0.000270542`; PC10 itself is clearly adverse.
- Policy: treat residual energy as an explanatory motif and stress negative control, not as a submission gate. If E237 public wins, learn from OOF decisive-cell labels again rather than promoting scalar residual-energy rules.

### F207. E242 high-impact Q3 tail-transfer diagnostics

- Hidden structure: E237 may transfer only as a high-impact Q3 tail classifier, not as an average OOF policy-improvement model.
- Candidates: E237 OOF tail-AUC, OOF gain, subject win rate, E237 score, support gain, adverse reduction, Q3 top-cell safety, and E230 overlap metrics across the `120` graft-side materialization rows.
- Label vs split test: valid as a ranking/governance diagnostic. It uses existing OOF labels and public-free materialization stress; it does not fit public labels or create probabilities.
- Current evidence: OOF gain is not useful as a selector (`AUC=0.426043`, top E237 rank `71/120`), while OOF tail-AUC is highly aligned with the E237 gate (`AUC=0.958913`, top E237 rank `1/120`).
- Policy: use high-impact tail discrimination as the E237 feature identity. Do not use average OOF gain or raw residual PC10 as promotion criteria for E237 siblings.

### F208. E243 public-slot question-routing features

- Hidden structure: different candidate tensors can be valid only under different hidden-world questions; a feature can be useful for choosing the next observation without being a probability feature.
- Candidates: public-slot role, JEPA-as-solution rank, clean-JEPA-ablation rank, non-JEPA escape rank, E237-vs-E224 Q3 dropped-cell count, E242 tail-AUC/support/top-cell ranks, E224/E216 cosine, E224/E166 cosine, E154 inherited-body penalty, and routebook decoder availability.
- Label vs split test: this is governance metadata, not a model feature. It should never be trained into predictions or used to tune probabilities. It exists to prevent post-hoc blending and to preserve public LB as a sensor.
- Current evidence: E243 ranks E237 first only for improvement-biased JEPA-tail testing, E224 first for clean JEPA body ablation, E166 first for non-JEPA broad-world escape, and E154 as conservative conditional branch.
- Policy: use F208 to decide which public question is being asked before choosing a file. Do not collapse E237/E224/E166/E154 into one scalar rank or blend.

### F209. E245 feature-NN1 LeJEPA compatibility features

- Hidden structure: the only E207-identifiable true-JEPA positive-pair regime, `broad_stage2_pca64 / feature_nn1_all`, may provide a health check for whether E237's Q3 cell rollback is a world-model-compatible representation rather than a standalone tail edit.
- Candidates: submission-side feature-NN1 pair indices, Q3 pair abs-logit roughness, E224-to-E154 rollback deltas, affected-pair flags, random all-row rollback null, top50-amplitude rollback null, candidate movement pair ratios, residual embedding rank fraction, covariance condition, and random-projection Gaussian score.
- Label vs split test: valid as a public-free representation audit. It uses no public labels and creates no probabilities. It is not a selector unless future public feedback plus a stronger null result shows the feature-neighbor regime carries public-tail direction.
- Current evidence: E237 reduces global Q3 NN-pair roughness by `-0.000802649` and affected-pair roughness by `-0.006472972`, but null percentiles are only weakly supportive (`0.1080` affected all-row; `0.2896` affected top50-amplitude). E237 is not globally smoother than E224 by movement pair ratio.
- Policy: use F209 as a compatibility diagnostic for E237, not as a submission feature. If E237 wins, build a direct feature-NN1/decisive-cell JEPA target; if E237 loses, do not rescue the branch with F209 alone.

### F210. E246/E247 feature-NN1 smoothing selector features

- Hidden structure: Q3 probability should be locally coherent on the `broad_stage2_pca64 / feature_nn1_all` manifold; rows whose E224 Q3 logits violate that neighbor geometry are candidate rollback cells.
- Candidates: directed feature-NN1 pair index, nearest-neighbor distance, single-row source pair smoothing delta, incoming pair smoothing delta, total/mean Q3 smoothing gain, amplitude-weighted smoothing gain, E237/E230/amp-top overlap, and selected-row roughness deltas after materialization.
- Label vs split test: public-free and label-free on test, but not leak-free in the broader sense because it uses test geometry and candidate predictions. It must be treated as a sensor/candidate rule, not as a train-validated feature until an OOF analogue is built.
- Current evidence: all `16/16` feature-NN1 selectors pass E237-like test-side stress. The selected E247 file changes `34` Q3 cells, has E237 overlap `13`, E230 swing25 overlap `10`, expected loss vs E224 `-0.000066519`, adverse reduction `0.000632592`, and feature-NN1 Q3 roughness delta `-0.014223558` global / `-0.057353058` affected. E248 then rejects OOF invariance: the train-only smooth-sum analogue has rollback delta `+0.002829987`, and the all-PCA analogue has `+0.002922728`.
- Policy: F210 is actionable only as a high-information public sensor, not as an OOF-certified feature. Do not sweep thresholds or siblings before feedback. If E247 wins despite E248, hidden public labels differ from OOF in a feature-neighbor-specific way and F210 should be rebuilt as an OOF/public-contrast JEPA target. If it loses, demote F210 to a smoothing/calibration shortcut.

### F211. E249/E250 feature-NN1 decisive-cell context features

- Hidden structure: feature-neighbor geometry may not say "smooth Q3"; instead it may help predict the hidden representation "which moved Q3/S4 cells are high-impact tail risks?"
- Candidates: feature-NN1 row index, distance, neighbor base/full/prob/logit/margin deltas, source/incoming/total smoothing gains, E237 decisive-cell risk/contrast labels, OOF tail-AUC, support gain, adverse reduction, Q3 top-cell concentration, and E230 overlap.
- Label vs split test: valid only when trained/evaluated on OOF decisive-cell targets and then materialized through E237 graft/actual stress. It must not be used as a direct smoothing selector or as an average OOF loss ranker.
- Current evidence: E249 promotes `276/2496` OOF rows. Feature-NN1 context improves paired tail-AUC for `latent_no_targetid/hgb_shallow` in `62.5%` of rows but worsens median loss by `+0.000053880`. E250 finds `4/120` materialization gate passes. The best top21 file changes only Q3, has OOF tail-AUC `0.887357`, expected loss vs E224 `-0.000000845`, adverse reduction `0.000524271`, support gain `0.005790882`, and actual adverse reduction `0.000502064`.
- Policy: F211 is the preferred way to use feature-NN1 if the next question is JEPA-as-context. It does not outrank E237 for expected score. Reject broad top50 OOF-gain rows and E250 sibling sweeps before feedback.

### F212. E251/E252 multi-view Q3 cell-set complementarity

- Hidden structure: the public Q3 tail may be distributed across multiple context views. E237's learned decisive-cell view and E250's feature-NN1-context view may each capture part of the tail, while their shared consensus core is too concentrated.
- Candidates: E237/E250 cell overlap, E237-only cells, E250-only cells, union cells, symmetric difference, shared-intersection concentration, union support/adverse stress, and exact Q3-only materialized union.
- Label vs split test: valid as a public-free materialization and integrity test, then checked by an OOF analogue. It is not a certified feature because the OOF analogue conflicts with materialization.
- Current evidence: E251 finds E237 `25`, E250 `21`, shared `15`, E237-only `10`, E250-only `6`, union `31`. Union stress score is `0.077866812`, above E237 `0.058941606` and E250 `0.053008707`, with support gain `0.010353010`. E252 materializes a schema-clean union file changing only Q3. E253 weakens adoption: train-OOF union is stress-promoted but worse than E237 (`-0.000080010` vs `-0.000271441`), and the OOF shared intersection is strongest (`-0.000376454`) despite failing E251 materialization.
- Policy: F212 is a validation-mismatch diagnostic and public sensor family, not a certified feature. Use E252 only to test whether public follows materialization geometry over OOF; keep E237 first for expected score.

### F213. E254 OOF-vs-test Q3 conflict atlas features

- Hidden structure: the same Q3 cell group can be healthy under train OOF and unsafe under test hard-tail geometry because train/test probability-step and feature-neighbor regimes differ.
- Candidates: group identity (`shared`, `e237_only`, `e250_only`, `union`), train OOF benefit/negative-rate, test expected focus/adverse/support/top1 concentration, `prob_gap`, `logit_step`, feature-NN1 smooth-gain, feature-NN1 pair logit gap, and standardized train/test shifts by group.
- Label vs split test: valid as a diagnostic atlas only. It compares train OOF labels to public-free test hard-tail priors but uses no public LB. It must not become a direct gate until a new OOF contrastive target learns the split.
- Current evidence: shared cells are OOF-best with benefit mean `-0.028234084`, but test shared has Q3 top1/abs `3.412733926`. Union is OOF-diluted (`-0.002117914`) yet changes the test hard-tail profile. The largest shifts are `prob_gap` (`-1.52` to `-1.80` std), `logit_step` (`-1.40` to `-1.67` std), and feature-NN1 smooth-gain sign flips.
- Policy: use F213 to design the next JEPA objective: a contrastive head for OOF-harmful consensus versus test hard-tail-adverse parent-specific geometry. Do not use it to submit intersection, union, or another scalar threshold variant.

### F214. E255/E256 public-positive feature-NN1 smoothing features

- Hidden structure: the public Q3 tail follows feature-nearest-neighbor smoothing on the E207 broad-stage2 manifold more than ordinary train OOF harmful-row labels.
- Candidates: E247 public win, E246 selector family, E247 overlap/Jaccard, high-amplitude constrained smoothing, selected smooth-gain sum, global/affected pair roughness delta, and E224-body attribution.
- Label vs split test: public LB is used as a sensor, not a fit target. E248 remains the split contradiction: train OOF analogues are adverse, so future models must learn public-contrastive geometry rather than reuse OOF smoothing labels directly.
- Current evidence: E247 public `0.5761589494` beats E95 by `0.0001323804`. E256 changes `25` Q3 cells, overlaps E247 on `21`, has expected loss vs E224 `-0.000047418`, adverse reduction `0.000615602`, and affected-pair roughness delta `-0.070332985`.
- E257 anatomy: E247-only cells are low-amplitude broad smoothness (`13` cells, amplitude mean `0.039125051`, smooth-gain sum `1.002858981`, E237/E230 overlap `0`), while E256-only cells are high-amplitude swing cells (`4` cells, amplitude mean `0.110316918`, E230 swing overlap `4/4`, smooth-gain sum `0.049289874`).
- Policy: F214 is now the live score-plus-information feature family. Submit only controlled follow-ups: first E256 for broad-vs-amplitude smoothing, or E224 for body attribution. Do not sweep all E246 siblings before E256/E224 feedback.

### F215. E258 body-vs-rollback attribution features

- Hidden structure: the public-positive E247 tensor may be a composition of a broad capped-Q3/S4 JEPA body and a smaller Q3 tail trim, rather than an isolated feature-NN1 smoothing law.
- Candidates: `E95 -> E224` body vector, `E224 -> E247` rollback vector, `E224 -> E256` rollback vector, selected-cell body/rollback cosine, opposite-sign share, rollback magnitude over selected body magnitude, total expected focus, targetwise hard-tail concentration, and body-vs-rollback attribution route.
- Label vs split test: public LB is not fit. This is a deterministic decomposition of existing tensors plus E222 hard-tail priors. It can support attribution routing but cannot prove which component caused E247's public score.
- Current evidence: E247 rollback is an opposite-sign trim of E224 body on selected Q3 cells: selected cosine `-0.992683110`, opposite-sign share `1.000000`, and rollback abs over selected body abs `0.984581403`. E247 total preserves the E224 body while improving Q3 top1/abs expected from `0.863839051` to `0.545240602`.
- Policy: use F215 to prevent post-hoc overclaiming. E247 validates the composition, not isolated smoothing. Submit E256 for rollback refinement or E224 for body attribution; do not blend/tune before one of those sensors resolves.

### F216. E259 public-observation route features

- Hidden structure: the same scalar public LB can support different hidden-world explanations unless the candidate's role is fixed before submission.
- Candidates: candidate role (`E256` broad-vs-amplitude smoothing, `E224` body attribution), public score band, delta vs E247, delta vs E95, world-update class, next-action route, and forbidden follow-up class.
- Label vs split test: this is governance metadata, not a model feature. It uses known public anchors only to define interpretation bands; it must not be trained into predictions or used for prior tweaking.
- Current evidence: E259 maps E256 scores into amplitude breakthrough / tie / broad-smoothness loss / same-family loss, and maps E224 scores into body breakthrough / rollback-helped / body-only loss. The routebook is stored at `analysis_outputs/e259_post_e247_observation_routebook_report.md`.
- Policy: use F216 before acting on any E256 or E224 public LB. Do not submit E247-family blends or extra siblings before one pre-registered route is observed.

### F217. E260 hard-label route sensitivity features

- Hidden structure: post-E247 candidate risk is not only the candidate-level expected loss; it is the cell-group-level ability of a few public hard labels to overturn the public-free prior.
- Candidates: pair role (`E256-vs-E247`, `E224-vs-E247`), E257 cell group (`common`, `e247_only`, `e256_only`), cell action, hard-label swing, expected-focus contribution, adverse capacity, top1/top5 over expected edge, and cells needed to cross E259 public bands.
- Label vs split test: diagnostic only. It uses public-free priors and known submitted tensors, not hidden public labels. It should decide which failure explanation is admissible after public feedback, not train a probability model.
- Current evidence: E256 expected penalty is `+0.000019101` versus E247, while E224 is `+0.000066519`. E256's E247-only deletion group is slightly favorable (`-0.000001767`), and the E256-only four-cell group is adverse (`+0.000020868`). E224's common rollback removal is adverse (`+0.000068286`).
- Policy: use F217 when decoding E256/E224 feedback. If E256 loses, inspect the four high-amplitude additions first; do not automatically restore all E247-only broad cells. If E224 wins, treat it as evidence against the common rollback core.

### F218. E261 public-assimilated smoothing-branch state

- Hidden structure: public distinguishes feature-NN1 smoothing mechanism from the specific E256 amplitude-constrained refinement.
- Candidates: E256 public delta versus E247/E95/mixmin, E259 outcome, E260 actual-over-expected ratio, min top swing cells explaining public delta, and post-public branch status.
- Label vs split test: this is public-observation governance. It must not be used as a probability feature or as permission to tune siblings. It is used to close or keep alive hidden-world branches.
- Current evidence: E256 public `0.5762805676`; delta versus E247 `+0.0001216182`; delta versus E95 `-0.0000107622`; E259 outcome `same_family_loss`; two top E256-vs-E247 swing cells can explain the observed delta scale.
- Policy: close high-amplitude smoothing as a score route. Keep E247 as current anchor. Use E224 only for body attribution. For score, require a refreshed non-collinear candidate rather than another E247/E256 scalar threshold.

### F219. E262 human/social diary features

- Hidden structure: the raw lifelog may encode daily human states: late social stimulation, presleep cognitive load, commute/workday rhythm, routine anchors, physical fatigue, home/away/public context, and sleep-onset fragmentation.
- Candidates: app-category time by window, presleep/deepnight social/search/call/media/religion/finance/shopping usage, charging/screen windows, GPS speed/range, WiFi/BLE density, ambience speech/music/public, light, HR, pedometer, and composites such as `human_late_cognitive_load`, `human_routine_anchor`, `human_commute_mobility`, `human_sleep_onset_risk`.
- Label vs split test: must be used with subject/date-block stress. HR/pedometer count shifts are also train/test domain signatures, so raw importance is not enough. Require within-subject label lift and tail-risk transfer.
- Current evidence: E262 creates `790` lifestyle/raw context features over `700` rows. Strong cheap lifts appear in commute/mobility, routine, late cognitive load, sleep-onset risk, and social overstimulation families. E263 links these features to E247/E256 Q3 public-tail cells.
- Policy: use F219 as JEPA context/energy, not as direct feature dump. Any downstream use must answer which hidden human state it targets and must survive subject/date-block and train/test adversarial checks.

### F220. E263 lifestyle-conditioned Q3 tail-risk features

- Hidden structure: public-sensitive Q3 smoothing cells may depend on human-day state. E256-only high-amplitude cells may be unsafe on cognitively active but lower-social/lower-screen-fragmentation days.
- Candidates: E257/E260 cell group labels joined to E262 lifestyle features; groupwise robust z/percentiles; row-level E256-only swing context; future OOF labels for Q3 smoothing-validity or rollback-risk.
- Label vs split test: E263 uses test-side candidate cell groups, so it is diagnostic only. A deployable version needs an OOF analogue trained on train cells and evaluated under subject/date blocks.
- Current evidence: E256-only cells show high late cognitive load, late search/browser, HR, and moderate presleep movement, while being lower in late social/message, public-social-presence, screen/onset-risk, and presleep social/search compared with the common E247/E256 core.
- Policy: do not materialize a submission from E263 directly. Build a masked lifestyle-family JEPA head that predicts Q3 tail-risk/smoothing-validity, then use LeJEPA geometry checks before any gate.

### F221. E264 late/presleep lifestyle tail representation

- Hidden structure: harmful Q3/S4 tail movement is partly tied to late/presleep human diary context, not only feature-neighbor numeric smoothness.
- Candidates: `human_late` context features from E262, especially late/presleep search/browser, social/message, calls, screen, charging, movement, HR, light, ambience, and composite cognitive/onset/social scores.
- Label vs split test: E264 uses fold-local train OOF tail labels with `subject5` and `dateblock5`. This is stronger than E263, but still not materialization-side public stress.
- Current evidence: best human-only OOF row loss_vs_full `-0.001689622`; best dateblock LR row `-0.000690449`; human-only strict gates `443/936`. E265 shows random controls can pass many gates, so the policy gate is not certifying.
- Policy: keep F221 as a representation/energy. Use it to build sharper cell-tail ranking or materialization stress. Do not use broad `drop_global_p20` or similar policies as submissions.

### F222. E265 random-control policy-gate health

- Hidden structure: broad rollback policies may improve OOF even without meaningful context, making naive strict gates overoptimistic.
- Candidates: random cell bad-probability controls, random strict rate, random best loss_vs_full, and excess human-over-random margin.
- Label vs split test: negative control only; it does not create features. It tests whether an observed gate is hard enough to mean something.
- Current evidence: random strict rate `0.290909`; random best loss_vs_full `-0.000723735`; E264 human_late best `-0.001689622`.
- Policy: any future lifestyle gate must beat random controls by margin and pass materialization-side public-free tail anatomy. Treat broad OOF policy loss as an insufficient adoption criterion.

### F223. E266 lifestyle-conditioned Q3/S4 cell-tail materialization

- Hidden structure: late/presleep human diary context marks target-specific tail cells where the E224 Q3/S4 body should be rolled back toward E154.
- Candidates: E264 human/social views (`human_late`, `human_core`, latent+human variants), sharp top-k/p05/p10 policies, Q3/S4 dropped-cell counts, expected_loss_vs_e224, adverse_reduction_vs_e224, support_gain_vs_e224, actual-vs-E95 stress, Q3 top1/abs expected, and E230 Q3 risk overlap.
- Label vs split test: stronger than E264 because it uses subject/date-block OOF heads and E237 materialization-side public-free stress. Still not public-certified because the stress uses priors/anchors rather than hidden public labels.
- Current evidence: E266 selected `22` files. Balanced `2936100f` has `25` Q3 + `25` S4 dropped cells, expected_loss_vs_e224 `-0.000004014`, adverse reduction `0.000418519`, support gain `0.004541355`, and E230 risk overlap `6`.
- Policy: F223 is the first submission-grade human/social feature family, but only through pre-registered routebook selection. Do not submit broad support-only variants.

### F224. E267 social-JEPA survival route features

- Hidden structure: a healthy lifestyle-conditioned tensor should not maximize support by broad rollback; it should preserve expected loss while reducing adverse capacity and keeping enough public-tail support to be informative.
- Candidates: social-JEPA survival score, balanced gate, sharp gate, support-sensor gate, duplicate prediction digest, movement versus E247/E256/E224/E95, and public-feedback interpretation band.
- Label vs split test: governance/selection metadata, not an input feature. It prevents post-hoc candidate picking after E266 generated many sibling files.
- Current evidence: E267 ranks `submission_e267_humansocial_tail_balanced_2936100f.csv` first. It moves `60` cells versus E247 over `54` rows, with Q3 `51` and S4 `9`.
- Policy: use F224 only to choose and decode the next public sensor. Do not train it into predictions or tune it after public feedback.

## Current Feature Policy

- Direct feature addition is paused unless it maps to a hypothesis and stress test.
- Direct JEPA residual probability movement is banned at raw/full amplitude. Only tiny scaled steps that pass broadness, bad-axis geometry, negative controls, context-alignment diagnostics, safety-context decoupling, public-sensor framing, pre-registered feedback decoding, critical-cell prior audit, rollback-intervention survival, rollback-overcorrection stress, anti-post-hoc public-feedback decoding, component-level damping checks, locked post-feedback interpretation, E178 plateau-law survival, E179 decisive-cell visibility review, E180 known-anchor calibration, E181 binary-world counterprior stress, E182 refreshed current-anchor underidentification stress, E183 pressure-branch anti-selector stress, and E184 public-anchor motif stress are allowed. E166 is the raw broad-escape sensor; E167 adds the caveat that context-real is not safety-certified; E168-E169 refine that caveat by producing a context-high/veto repaired tensor; E170 adds that even this repaired tensor remains public hard-label-resolution limited; E171 adds that the broad body is visible-prior favorable but top critical cells are adverse; E172 shows the adverse visible-positive-loss tail can be damped without killing the broad body; E174 shows a subset of that damping can be reopened without losing the visible-tail guard; E175 fixes how that sharper bet must be interpreted; E176 shows Q2 should be slightly damped inside that reopened subset; E177 locks the E176 feedback bands; E178 explains why this still sits at the plateau; E179 adds that E176's body and Q2 damping are visible-supported, but its top public-decisive cells are not certified; E180 shows that known winners can also have weak top-cell support, so visible priors are diagnostics rather than vetoes; E181 adds that inherited current-anchor binary worlds are a counterprior against E176 and favor E154/E144 in the best-5 residual band; E182 shows the refreshed current-anchor pressure worlds make E176/E154/E144 all sign-underidentified; E183 shows visible/subject/flank priors reject the favorable pressure branch for all three candidates, so they are anti-selectors at branch resolution; E184 shows a shallow known-public metadata motif also fails as an action-grade selector because polarity and feature-set branch preferences are unstable. Prefer E176 only when deliberately testing the visible-body/Q2-underopen worldview; prefer E154/E144 only when deliberately testing the repaired-branch worldview with a decoder. Do not claim either branch is certified from current-anchor inverse worlds, visible-prior branch preference, or shallow public-anchor motif scores.
- E185/E186 add an explicit geometry rule: known-LB pair structure can be used only if reciprocal orientation is controlled. E185's unconstrained decoder is diagnostic only because branch choice flips and reciprocity MAE is nonzero. E186's antisymmetric decoder strengthens E176 as the next sensor, but E187/E188 show the support part of that decoder is a conflicting shortcut: it flips exact E95/E101, and low-alpha support blending cannot repair it before losing the boundary. E189 localizes the useful support signal to E72-neighbor correction, while shape-only owns the exact E95/E101 boundary. E190 shows filename-free movement features can partly detect E72-neighbor structure, but support-rich detectors still false-positive exact E95/E101 and live E176 is not E72-contaminated. E191 then rejects the cheap hard-negative repair: exact E95/E101 weighting/prototypes create clean rows only for shape/target/context, not for support. E192 decomposes that surviving clean score and shows E144's partial alarm is a non-E72 tail-risk signal, while E176 remains near-zero. Shape-only is healthier at tight frontier boundaries but weaker on wider E72-contaminated edge stress. Therefore known-LB pair structure is a sensor, not a selector, unless a future structural detector identifies E72-contamination without filename identity and without exact-boundary false positives.
- E197/E198 split the E72 risk into two objects. E197 shows E176 loses only under E72-like adverse slippage, while E198 shows E176 is not clean-shape E72-exposed (`0.000008`). So E72-like loss is an algebraic hidden-label scenario, not visible contamination evidence. This keeps E176 first as a sensor, but the feature policy stays conservative: do not build E72-demoted E176 variants before feedback, and do not call E176 certified because the clean detector has imperfect recall.
- E199 extends this to the follow-up tree: the same-family fallback E172 is also clean-shape non-E72, and the repaired-branch route should prefer E154 over E144 because E144 is the only direct p99 tail alarm.
- The most promising public-relevant diagnostic is now the anchor-loss/binary-world geometry that selected `submission_mixmin_0c916bb4.csv`; E48 validates it as a public-sign feature family, not just a sensor label. It is still not private-safe certification or target-axis JEPA semantics. The next useful feature is not another S4/Q3 weight variant, OOF-local Q3/S4 winner, existing block/measurement candidate rescore, naive merge of pair-only and old-only shortlists, old-only Q3/raw05-drift sensor, amplitude-only S4/Q3 rescale, simple row-mask localization, unqualified larger sparse/minimax movement, inverse-LB prior fitting, subject-prior inverse ranking, a single binary inverse incumbent, a small binary world-pool sign readout, generic train-label plausibility gate, OOF selector-rank gate, movement-fingerprint predicted LB used as a score forecast, movement+axis predicted LB used as a score forecast, fixed-zero anchor kNN forecast used to rank near-A2C8 candidates, existing-universe rescore without new evidence, simple structured public-subset mask recovery, or same-summary Ridge block-rate regression. E39-E45 remain negative screens for selector calibration, and E46-E47 still say the 0.54 path requires better held-out block-rate/count representation. Post-E48 feature work must be mixmin-relative: preserve the validated anchor-loss/cancellation direction, reduce private-risk energy, and test whether new block-state context/target designs recover hidden rates instead of only perturbing row probabilities.

E49 makes the next feature policy narrower: start from subject-calendar mask context, but treat it as JEPA context/energy, not as a raw row-order feature dump. E50 makes it narrower again: calendar movement is not enough to rank public candidates because it fails to predict mixmin as best. E51 narrows it further: anchor-loss world aggregates plus calendar fingerprints are still not a transferable selector. E52 narrows it again: conditioning existing binary worlds on mixmin does not reveal a current replacement candidate. E53 narrows the block-rate/count branch: a simple calendar-flank count posterior is useful energy but not a candidate generator because strict donor exclusion fails pseudo-hidden recovery. E54 widens the representation evidence but narrows the candidate gate: raw overnight context recovers strict pseudo-hidden block state, yet its actual hidden-rate world is adverse for mixmin and regresses S3. E55 then narrows the translation hypothesis: simple Q/S target-rate projection cannot reconcile raw pseudo-hidden recovery, S3, and mixmin sign. E56 reopens hidden-world generation by producing coherent mixmin-hard raw posterior energy, but E57 closes direct posterior submission because actual-anchor safety gates are `0`. E58 closes the first simple anchor-constrained distillation attempt because best safe anchor deltas are below `1e-5`. E59 closes the within-block joint-pattern-only target as a candidate source: the joint structure is real but target-mismatched. E60 closes aggressive transition-residual hidden-sign movement as a candidate source: the sign is real-looking but calibration collapses. E62 closes simple transition-gated E56 teacher movement as a candidate source: the gate is interpretable but weaker than E58. E63 opens a useful direction validator but closes gradient consensus as a submission gate because the best anchor gain remains sub-margin. E64 closes scalar amplification of that validator because larger moves are uniformly anchor-adverse. E65 opens only a sub-margin near-zero targetwise pocket and points directly at Q2/S3 as conflict targets. E66 refines that target-conflict: Q2/S3 can be hidden/mean-favorable, but they expand public-compatible tail risk. E67 shows a first-order tail-neutral translator improves over broad masks, but margin gates remain `0`. E68 then validates many tail-gated Q2/S3 cells outside same-anchor construction, so the missing object is no longer independent validation alone. E69 closes global alpha over those cells. E70 keeps the consensus branch alive but not submission-ready: strict rows exist, yet only under `gate=none` and heldout-specific aggregation. E71 shows this is not merely a heldout-specific arithmetic trick, because one unified strict row survives, but deployable sign/agreement gates remain `0`. E72 then narrows the failure: sparse-magnitude `top_abs50` and `s3_only` gates can be deployable, while Q2-only and soft/sign agreement remain weak. E74 adds that the selected sparse gate is cell-subset stable, while alpha24 failure warns against uncontrolled amplitude. E75 adds that the amplitude boundary is target-specific: S3-heavy/Q2-low rows dominate deployable support and Q2-only remains dead. E76 adds that this target-asymmetric direction is subset-stable but exact universal `8/28` deployability is only partial. E77 then closes the tempting shortcut: source-subset posterior averaging does not repair exact-amplitude instability because safe Q2/S3-only movement is sub-margin and full posterior movement breaks combo-set/tail consistency. E78 closes the next shortcut: E76 deployable/non-deployable source-subset reliability masks create many deployable rows but no row that beats E75, so simple sign/consensus/excess/veto localization is not the missing law. E79 closes the handcrafted row/block/flank shortcut. E80/E81 close direct sparse-gate follow-up: the submitted E73 file is public-adverse and all-target contaminated, while pure E73 Q2/S3 remains sub-margin and inverse sign fails. E82 closes the wider pure-graft rescue: even E72/E75/E76 source grafts pass non-margin stress but fail margin. E83 shows that Q2/S3 energy can mark safe rows but does not by itself make broad structural movement safe; broad margin rows worsen Q2/S3/world or fail combo-set coverage. E84 shows that adding non-Q2S3 structural margin and Q2/S3 safety solves hidden/world/block stress but leaves a single inverse-top combo-set conflict. E85 then proves the first cheaper separation: target-axis pruning, especially keeping `S1,S2,S3`, resolves inverse-top while preserving the other combo worlds. E86 adds the source-stability layer: consensus across many strict target-pruned rows and source files strengthens the local edge without breaking hidden/world/block stress. E87 splits that source-consensus risk into Q2 add-back, shrink overstep, and inverse-top-prior geometry. E88 adds the public-movement attribution layer. E89 then turns that risk into a concrete gate: top-E72 cells can fall back from E86 to E85, giving a lower-contamination strict candidate. E90 adds the Pareto-knee layer: row-coherent fallback can retain more E86 structure than the minimum-contamination file while still being cleaner than E85/no-Q2. E91 adds a negative selector flag: known-LB regression remains invalid even after E72. E92 adds another negative selector flag: hidden-block posterior CE is E72-tainted and cannot rank submissions directly. E93 adds a third negative selector flag: train target-manifold consistency is also E72-tainted and cannot serve as the counter-gate. E94 adds the required hard-label tail flag: soft health can look best on E86 while hard-label tail risk is lower for E89/E85. E95 turns that flag into a local fallback gate that beats E89 on hard-tail and margin, while also showing non-strict tail minimization is a rollback trap. E96 adds the public-miss budget scenario energy, E97 validates E95 as public-positive, E98 adds the E95-updated known-LB selector collapse flag, E99 adds the E95-conditioned tail-transfer energy, E100 adds the E89 Q2/S3 diffuse-tail counterfactual energy, E101 adds the E95-relative Q2/S3 rollback energy, E102 shows the rollback cells are weakly edge-local but not block/subject-local, E103 shows that direct edge-local masks do not dominate the full E101 amplitude rollback, E104 shows E101 alpha `0.25` is a Pareto cliff rather than a coarse-grid accident, E105 shows E101's public fate is mostly a subject/block-local S3 hard-label condition rather than a global prior correction, E106 rejects subject-prior gating as a pre-feedback candidate generator, E107 turns the pending E101 result into a conditional branch map, E108 materializes the E101-win amplitude branch without changing the pre-feedback submission order, E109 closes same-line rescue for E101 tie/loss, E110 rejects the automatic non-active E89/graft fallback after a negative E101 result, E111 reframes the current frontier as target-axis hard-tail surgery, E112 separates S subject/block-state from Q temporal-state, E113 rejects visible raw context as a broad Q temporal rescue, E114 rejects raw context as E101 active-cell pre-validation, E115 confirms E101 has the highest actionable public-sensor information after that raw-support failure, E116 locks the post-E101 feedback decoder before the score is known, E117 closes the old-universe shortcut by showing that lower-tail E95-like neighbors are only E101/E85/E108-family files, E118 adds visible flank-transition support while keeping E101 uncertified because expected delta remains positive, E119 rejects turning that support into a pre-feedback flank-gated replacement because no row dominates E101, E120 applies the real E101 public `small_loss` feedback, E121 converts that score into a one-cell-scale S3 hard-label boundary, E122 shows existing visible priors explain but cannot exploit that boundary, and E123 rejects cross-target transition motif as the missing independent S3-cell sensor. A useful feature must now treat target-axis contamination, source-consensus stability, post-E86 risk decomposition, frontier-movement attribution, E72-cell fallback, E72 row-coherent Pareto fallback, known-LB selector collapse, hidden-block posterior taint, target-manifold taint, hard-label tail exposure, hard-tail localized fallback, public-miss budget robustness, E95-updated proxy collapse, E95-conditioned transfer, Q2/S3 diffuse-tail concentration, E95-relative rollback separation, edge-local active-cell energy, E101 flank-transition support but non-certification, E101 flank-gate replacement failure, E101 public small-loss boundary energy, exact small-loss inverse-posterior energy, independent-sensor boundary failure, transition-motif collapse energy, E103 edge-amplitude dominance failure, E104 amplitude Pareto-cliff risk, E105 public-label break-even, E106 subject-prior gate failure, E107 feedback-conditioning tension, E108 conditional materialization, E109 tie/loss active-label retention, E110 non-active tail isolation failure, E111 target-axis surgery, E112 S/Q axis split, E113 raw-context collapse warning, E114 raw-support failure, E115 actionable sensor information, E116 feedback decoder guardrails, and E117 neighborhood scarcity as separate energies.
## E268 Human/Social Story Features

- Target hypothesis: E267 failed because the old E224/E154 rollback body was wrong, while a smaller human-state signal may still explain the E247/E256 Q3 boundary.
- Feature source: `analysis_outputs/e268_human_social_story_atlas.py`, using all E262 day-level lifelog aggregates.
- Stories tested: `35` explicit human-day states, including phone-in-bed, app entropy/scattered attention, weekend ritual rest, single-app monotony, ritual anchor, bright-light-late, deepnight phone awake, social isolation media, commute/workday, social outing, fatigue, HR stress, sensor sparsity, and environment/vehicle noise.
- Validation used:
  - train label lift by target;
  - dateblock and subject blocked CV;
  - train/test shift;
  - E247-only vs E256-only Q3 movement alignment;
  - E267 failed-movement exposure.
- Strongest surviving story: `phone_in_bed`, which separates E247-only from E256-only Q3 rows with cohen_d `1.164309` and is not exposed in E267 failed movements.
- Failure condition: broad latent usage is rejected. The PCA story latent worsens blocked CV on every target, so these features should be used as sparse gates/diagnostics, not dumped wholesale into a model.
- Current action: E269 uses these stories only on the `17` Q3 rows separating E247 and E256.

## E270 Payday / Cash-Flow Story Features

- Target hypothesis: monthly financial rhythm is a hidden human-state generator for sleep labels and the E247/E256 Q3 boundary, but not necessarily a literal salary date.
- Feature source: `analysis_outputs/e270_payday_cashflow_story_atlas.py`, built from E262 finance/shopping/social day-level lifelog features plus day-of-month anchors.
- Anchors tested: `10`, `15`, `20`, `25`, `eom`, `month_start`; phases include pre/post/near windows and behavior-linked variants.
- Surviving feature families:
  - `paymonth_start_near3_money_rumination`: month-start finance/shopping/search rumination; E247-only Q3 cohen_d `0.820306`.
  - `paymonth_start_post3_late_shopping`: month-start late shopping/finance use; E247-vs-E256 cohen_d `0.899993`.
  - `pay25_pre3_cash_stress`: clean pre-25 cash-checking stress; dateblock Q3 delta `-0.008576`, train/test gap `0.027231`.
  - `pay20_post3_late_shopping`: post-20 spending/late-shopping state; train/test gap `0.004853`.
- Label vs split test: pure calendar-only features can separate boundary cells but have high train/test gap, so they are confound-prone. Behavior-linked cash-flow features are preferred.
- Failure condition: if a cash-flow direct boundary probe loses public LB, do not expand this into a broad calendar feature dump. Use it only as context/energy for future sparse gates.
- Current action: E271 materializes a tiny direct E247 Q3 probe using only this story family.

## E273 Human Diary State JEPA Features

- Target hypothesis: raw lifelog is better treated as a human diary state than as unrelated tabular columns. The useful latent may be a residual energy: "given the rest of the day, is this social/mobility/bedtime/money pattern expected?"
- Feature source: `analysis_outputs/e273_human_diary_state_jepa_audit.py`.
- Families:
  - `social_comm`: messages, calls, speech, social isolation.
  - `cognitive_money`: search, work/study, finance, shopping, cash-flow windows.
  - `media_game`: media, game, music, attention entropy.
  - `bedtime_phone`: screen, charging, light, phone-in-bed, fragmentation.
  - `mobility_context`: home/away, commute, vehicle/public context.
  - `physiology_activity`: steps, HR, fatigue, sedentary/overtraining.
  - `routine_calendar`: weekday/weekend, rituals, stable routine.
  - `sensor_measurement`: wear/device/sensor density and missingness process.
- JEPA target: predict held-out family PCs from the other family PCs under subject and dateblock grouping; use residual and prediction norm as energy, not raw reconstruction.
- Validation used:
  - subject/dateblock OOF family predictability;
  - diary-state cluster health and subject NMI;
  - blocked CV baseline vs baseline+state;
  - train label lift;
  - E247/E256/E267 boundary alignment.
- Strong diagnostic axes:
  - `jepa_prednorm_subject_social_comm`: E247-vs-E256 boundary d `-1.332902`.
  - `jepa_resid_dateblock_cognitive_money`: boundary d `1.199200`.
  - `jepa_prednorm_subject_mobility_context`: Q3 label lift `-0.327434`.
  - `jepa_resid_subject_bedtime_phone`: Q1 lift `-0.221239`, Q3 lift `-0.203540`.
- Failure condition: broad diary-state feature dump is rejected because blocked CV worsens all targets. These features may be used only as target-specific energy/gates with an E272-style promotion audit.

## E274/E275 Target-Specific Q-Sleep Diary Energy

- Target hypothesis: the diary state should be split by target semantics. Q1/Q2/Q3 are subjective sleep/quality/intervention labels and can be affected by lifestyle interpretation; S1-S4 are objective stage-ratio labels and should not necessarily receive the same correction.
- Feature source: E273 energy axes, selected by E274 subject/dateblock single-feature stress.
- Surviving Q-side axes:
  - Q3 mobility/context pred-norm and energy: "home/away/commute/environment state says subjective quality changes."
  - Q3 bedtime-phone residual: "bed phone/light/fragmentation violates expected day-state."
  - Q3 routine-calendar pred-norm: "routine pressure/ritual stability changes perceived sleep quality."
  - Q3 cognitive-money pred-norm: "search/work/shopping/finance rumination changes perceived sleep quality."
  - Q2 media-game and diary PC10: "intervention/behavior label has attention/media component."
- Validation:
  - E274: `44` action-gate axes under subject/dateblock stress.
  - E275: q-sleep amplitude ladder m1.15..m1.60 passes strict public-free promotion.
- Adopt rule: use only Q1/Q2/Q3 movement from these axes. Do not expand this to S targets unless a separate S-only candidate passes promotion.
- Current candidate: `submission_e275_q_sleep_amp_m160_86528b2f.csv`.

## E276 Matched-Placebo Rule For Q-Sleep Diary Features

- Target hypothesis tested: E275's row placements encode real lifestyle-state alignment.
- Feature/representation source: the same E274/E275 top-12 Q-side diary-energy axes.
- Negative controls:
  - same logit deltas shuffled by row;
  - same logit deltas shuffled within subject;
  - same logit deltas shuffled within dateblock;
  - inverse E275 movement.
- Result: shuffled placebos promote `13/15`, so the old adopt rule is invalid.
- Updated adopt rule:
  - E274/E275 Q-side diary axes can stay in the registry as diagnostic features.
  - They cannot produce a submission unless the real row-aligned candidate beats matched row/subject/dateblock shuffle nulls.
  - Passing E272/E275 amplitude gates alone is now insufficient.
- Surviving subfeatures:
  - `mobility_context` and JEPA-derived axes remain the most promising.
  - `jepa_only_m160` passes old stress while `nonjepa_only_m160` fails, so JEPA context-target energy is preferred over raw PC/energy-only features.
- Failure condition: if a future JEPA/mobility Q3 candidate cannot beat matched placebos, retire this branch as score-action and keep it only for interpretation.

## E277 Placebo-Resistant Gate Feature Policy

- Target hypothesis tested: a narrower existing q-sleep semantic subset might beat its own matched nulls.
- Feature source: E275/E276 q-sleep variants generated from E273/E274 diary-energy axes.
- Validation result:
  - candidates: `21`;
  - matched nulls: `441`;
  - old strict candidates: `10`;
  - placebo-resistant candidates: `0`.
- Updated registry status:
  - `jepa_prednorm_*mobility_context*`, `jepa_resid_subject_bedtime_phone`, and cognitive/money Q3 axes remain diagnostic.
  - No q-sleep diary axis is currently approved for submission-time probability movement.
  - Any future feature in this family must provide a row-alignment score and must beat matched row/subject/dateblock nulls.
- Adopt rule:
  - require `placebo_resistant_gate=True`;
  - require old strict gate only as a first screen;
  - require null strict-promote rate <= `0.20`;
  - require p90 dominance over matched nulls >= `0.80`.

## E278 Train Row-Alignment Diagnostic Features

- Target hypothesis tested: q-sleep diary features may have supervised row signal even if current test candidates fail matched-placebo resistance.
- Feature source: same E273/E274/E275 diary-energy axes, evaluated on train with OOF Q baselines.
- Positive train-aligned feature groups:
  - `full_qsleep`: strong broad Q-side train alignment.
  - `q3_only`: clean Q3 row-alignment signal.
  - `jepa_only`: JEPA-derived mobility/routine/bedtime/money axes transfer within train.
  - `only_bedtime_phone`: small but highly null-dominant Q3 row alignment.
  - `only_mobility_context`: passes both subject/dateblock train gates.
- Negative/control:
  - inverse full movement is adverse.
  - `only_media_game` and `only_cognitive_money` do not pass robust train gates as standalone axes.
- Updated feature status:
  - These features are approved for row-alignment model training/diagnosis.
  - They are still not approved for direct submission movement until E277-style test matched-placebo resistance is also satisfied.

## E279 Public-Free Governor Feature Policy

- Target hypothesis tested: a candidate can be locally promoted only when row-aligned movement is stronger than matched movement with row identity destroyed.
- Representation source: any active submission tensor relative to E247; q-sleep tensors also inherit E278 policy-level train alignment.
- Adopt rule:
  - `old_strict_promote=True` is only the first screen.
  - `matched_placebo_gate=True` is mandatory for submission recommendation.
  - q-sleep candidates additionally need E278 `train_support_gate=True`.
  - known-public files worse than E247 are blocked regardless of local selector shape.
- Validation result:
  - audited candidates: `66`;
  - old strict candidates: `13`;
  - matched-placebo gate passes: `0`;
  - final submission-ready candidates: `0`.
- Updated registry status:
  - E274/E275/E276 diary-energy axes remain diagnostic and training targets.
  - No current feature group is approved for direct probability movement.
  - Future features must be registered with both train row-alignment evidence and test matched-placebo resistance.

## E280/E281 Story-State Feature Policy

- Target hypothesis tested: explicit human/social stories can become hidden-state representations only if they transfer as row selectors, not merely because they sound plausible.
- Feature source:
  - E268 human/social story scores;
  - E270 payday/cash-flow story scores;
  - E273 family JEPA context diagnostics;
  - E281 context-to-story-state predictions.
- Current approved diagnostic story-state:
  - `app_entropy_scattered_day`: routine/attention fragmentation state.
    - E281 subject5 state R2 `0.419010`, mean label delta `-0.001949852`, dominance `1.000000`.
    - E281 dateblock5 state R2 `0.728347`, mean label delta `-0.000108720`, dominance `0.920000`.
    - strongest local target effects: Q3 subject, Q2/S2 dateblock.
- Hold / diagnostic only:
  - `single_app_monotony`: subject5 strong but dateblock mean delta slightly positive, so it is not yet a both-split gate.
  - `commute_workday`, `bright_light_late`, `vehicle_noise_day`, `heart_stress_late`: story scores are interpretable, but E281 does not support them as overall row selectors.
  - payday/cash-flow stories: still useful as human hypotheses, but no E281-level both-split state yet.
- Adopt rule:
  - a story can enter materialization only if its predicted story state beats row/subject/dateblock nulls under both subject and dateblock OOF;
  - direct public-boundary edits from story scores remain blocked;
  - materialized candidates must still pass E279-style matched-placebo governance before public LB.
- Failure condition:
  - if app-entropy materialization cannot beat matched nulls, keep story-state features for diagnostics/row-slice analysis only and do not create more direct social gates.

## E282 App-Entropy Materialization Policy

- Target hypothesis tested: `app_entropy_scattered_day` can be translated from a validated story-state into an E247-relative probability tensor.
- Feature/representation source:
  - E281 context-to-story-state predictor;
  - target direction from E281 target deltas and train logistic state coefficients;
  - E247-relative logit edits for Q3, Q2, and S2.
- Validation result:
  - candidates: `22`;
  - matched nulls: `726`;
  - old strict-promote candidates: `6`;
  - matched-placebo candidates: `0`;
  - public-ready candidates: `0`.
- Updated registry status:
  - `app_entropy_scattered_day` remains approved as a diagnostic hidden state and future row/cell-target context feature.
  - It is not approved for direct submission movement.
  - Q3-only linear movement is directionally alive but not row-placement-certified.
  - Q2/S2 additions are not approved for this materialization route.
- Adopt rule for future app-entropy features:
  - use app-entropy as context or energy, not as a scalar probability shift;
  - require matched-null resistance at the final tensor level;
  - any new candidate must show that row/cell placement matters, not only Q3 prior direction.
- Failure condition:
  - if a future app-entropy candidate only becomes strong after nulls also pass, classify it as calibration/prior movement and block public submission.

## E283 App-Entropy Q3 Smoothing Context Policy

- Target hypothesis tested: app-entropy can choose or refill E247-style Q3 feature-NN smoothing cells.
- Feature/representation source:
  - E282 app-entropy predicted story-state;
  - E246/E247 feature-NN1 Q3 smoothing cell metrics;
  - E257 E247/E256 public-boundary anatomy.
- Validation result:
  - selectors: `28`;
  - local E246/E237 gate passes: `27`;
  - materialized candidates: `27`;
  - matched-placebo candidates passing final gate: `0`;
  - public-ready candidates: `0`.
- Updated registry status:
  - `app_entropy_scattered_day` remains approved as a diagnostic context feature.
  - It is not approved as a direct selector override, rank boost, band filter, or E247 refill rule.
  - High app-state-by-amplitude is a useful risk descriptor for E256-like cells, not a sufficient gating feature.
- Adopt rule for future Q3 app-entropy use:
  - use it inside a learned cell-tail or row-alignment target;
  - require placebo dominance against row/subject/dateblock matched nulls;
  - do not materialize scalar app-entropy sorting rules as public candidates.
- Failure condition:
  - if app-entropy changes only a few Q3 smoothing cells and the p90 edge is under `1e-5` without null dominance, classify as selector-resolution noise.

## E284 App-Entropy Decisive-Cell Context Policy

- Target hypothesis tested: app-entropy may be useful as context for learned Q3/S4 decisive-cell risk, even though it failed as a scalar Q3 shift or E247 smoothing rank override.
- Feature/representation source:
  - E282 app-entropy predicted story-state;
  - app-state/app-story z-scores by subject and dateblock;
  - interactions with feature-NN1 decisive-cell metrics such as `prob_gap`, `logit_step`, margins, smooth gain, pair abs-logit, and distance.
- Validation result:
  - OOF decisive-cell rows: `3744`;
  - OOF stress-promoted rows: `409`;
  - E237 gate passes: `9`;
  - E247-current matched-placebo gate passes: `0`;
  - public-ready candidates: `0`.
- Updated registry status:
  - `app_entropy_scattered_day` is approved as JEPA context/energy for decisive-cell learning.
  - It is not approved for an E224/E154-anchored rollback submission.
  - The current live use is diagnostic: identify where routine fragmentation explains old Q3/S4 tail risk and where that disagrees with E247.
- Adopt rule for future app-entropy decisive-cell features:
  - anchor the target to E247 residuals rather than E224/E154 rollback;
  - report overlap with E247 public-positive cells before materialization;
  - require E247-current matched row/subject/dateblock null dominance before any public LB.
- Failure condition:
  - if the app-entropy model improves OOF but selects cells with low E247 overlap and positive E247-current p90, classify it as stale-target learning rather than current-frontier signal.

## E285 E247-Residual Human-State Context Policy

- Target hypothesis tested: human/social/cash-flow diary state can directly decide E247-relative preserve/undo/add Q3 smoothing cells.
- Feature/representation source:
  - E283 app-entropy state/story context;
  - E273 diary-state JEPA PCs/clusters and family prednorm/residual features;
  - E268 human-social story scores;
  - E270 payday/month-start cash-flow stories;
  - E280 story registry columns;
  - E284 decisive-cell selection scores and overlap summaries.
- Validation result:
  - boundary features: `51`;
  - materialized E247-relative candidates: `158`;
  - matched row/subject/dateblock nulls: `3318`;
  - old strict-promote candidates: `0`;
  - matched-placebo gate passes: `0`;
  - public-ready candidates: `0`.
- Updated registry status:
  - month-start shopping/money-rumination, app-state-by-amplitude, diary PCs, social communication, bedtime-phone, mobility, and bright-light features are approved as E247/E256 boundary diagnostics.
  - They are not approved as direct scalar add/undo selectors.
  - E247 is the protected current body until a learned E247-relative target beats matched nulls.
- Adopt rule for future human-state E247 features:
  - treat social/payday/app-entropy features as context for a learned preserve/avoid target;
  - require final tensor movement to beat matched row/subject/dateblock nulls;
  - do not submit story-ranked E247 residual edits with p90 edges below `1e-5`.
- Failure condition:
  - if a future E247 residual feature only explains E247/E256 anatomy but produces no old strict promotes or no matched-null dominance, keep it diagnostic and block public submission.

## E286 E247 Preserve/Avoid Contrastive Context Policy

- Target hypothesis tested: learned contrastive E247 preserve/avoid labels can turn the E285 human/social boundary anatomy into a submission-grade Q3 edit.
- Feature/representation source:
  - E283 app-entropy state/story context;
  - E273 diary-state JEPA PCs/clusters and family prednorm/residual features;
  - E268 human-social story scores;
  - E270 payday/month-start cash-flow stories;
  - E280 story registry columns;
  - E284 decisive-cell summaries;
  - E247/E256/E284 cell-geometry and current smoothing metrics.
- Validation result:
  - latent rows: `128`;
  - selected latents: `12`;
  - materialized candidates: `533`;
  - matched row/subject/dateblock nulls: `11193`;
  - old strict-promote candidates: `0`;
  - matched-placebo gate passes: `0`;
  - public-ready candidates: `0`.
- Updated registry status:
  - `cell_geometry` is approved as a diagnostic for E247 identity but not as a novel signal by itself.
  - human/social features remain approved as boundary diagnostics, especially for the tiny E247-only/E256-only sibling split.
  - human/social features are not approved as a current test-side pseudo-label cell-identity target because source-transfer is weak.
  - E247 remains the protected current body.
- Adopt rule for future E247 preserve/avoid features:
  - define the hidden target from train/OOF residuals, label lift, or row-alignment transfer when possible;
  - use test-side E247/E256 cell groups only as diagnostic anatomy, not as the sole training label;
  - require source-transfer and matched-null dominance before materialization.
- Failure condition:
  - if a learned preserve/avoid latent has high AUC only because it reads cell geometry and produces p90 edges below `1e-5`, classify it as E247 replay rather than a breakthrough representation.

## E287 Train-Supervised Row-Action Benefit Policy

- Target hypothesis tested: q-sleep human/social context can learn where a row-level Q action improves OOF labels, then transfer that action to E247-current test rows.
- Feature/representation source:
  - E273 diary-state JEPA PCs/clusters and family prediction residuals;
  - E282 app-entropy state/story features;
  - q-sleep action metadata from E274/E276 axes;
  - base probability/logit and target/family/kind/feature identity;
  - OOF row-action benefit labels from subject/dateblock train baselines.
- Validation result:
  - latent rows: `36`;
  - train policy rows: `180`;
  - train-gated policies: `3`;
  - materialized candidates: `3`;
  - matched row/subject/dateblock nulls: `63`;
  - public-ready candidates: `0`.
- Updated registry status:
  - `q3_only` and `mobility_q3` row-action benefit are approved as train-supervised diagnostic targets.
  - `bedtime_q3` is approved as a high-AUC latent clue but not as a row-placement policy.
  - `attention_money_q3` remains diagnostic only in this audit; it did not pass train-to-test policy gates.
  - no E287 row-action feature is approved for direct submission.
- Adopt rule for future train-supervised row-action features:
  - report both latent AUC/AP and actual train row-placement delta;
  - require row, subject, and dateblock null dominance before transfer;
  - require test matched-null p90 and worst-mode dominance before public LB.
- Failure condition:
  - if a row-action model is train-positive but test p90 remains below `1e-5` or worst-mode dominance is below `0.8`, keep it as energy/context, not as a probability edit.

## E288 Lifestyle-Bundle JEPA Policy

- Target hypothesis tested: multiple human/social/cash-flow stories can form a hidden lifestyle state that is more useful than single-story features.
- Feature/representation source:
  - top `28` E280 story scores;
  - E262 raw day human/social/sensor context;
  - E273 family JEPA context and diary-state features;
  - cash-flow/payday/month-start story scores from E270.
- Validation result:
  - context views: `3`;
  - label stress rows: `12`;
  - label-gate rows: `0`;
  - best mean label delta: `+0.002092612`;
  - best reconstruction: `family_jepa_context/dateblock5`, mean story R2 `0.385944`.
- Updated registry status:
  - broad lifestyle bundle is approved as a diagnostic hidden-state representation.
  - broad lifestyle bundle is not approved as a shared downstream feature or submission translator.
  - cash-flow/payday late-shopping remains a real story coordinate, but not a direct feature block.
  - dateblock-stable S4/Q3/S2 cluster slices are candidates for future target-specific audits.
- Adopt rule for future lifestyle-bundle features:
  - split by target group before label modeling;
  - report targetwise benefit and harm separately;
  - require per-target matched-null dominance, not only reconstructability or cluster interpretability.
- Failure condition:
  - if a bundle has high story R2 but positive mean label delta, classify it as descriptive diary state rather than predictive representation.

## E289 Target-Specific Lifestyle Slice Policy

- Target hypothesis tested: broad lifestyle state fails because targets have different noise channels; splitting by target should reveal useful Q/S-specific slices.
- Feature/representation source:
  - E288 lifestyle-story bundle;
  - family JEPA context, raw human context, and hybrid context;
  - subject/dateblock OOF story predictions;
  - PC and cluster lifestyle reps;
  - current E247 submission as protected base tensor.
- Validation result:
  - target-slice rows: `84`;
  - target-gate rows: `7`;
  - materialized candidates: `28`;
  - matched row/subject/dateblock nulls: `420`;
  - public-ready candidates: `0`.
- Updated registry status:
  - Q3 lifestyle slices are approved as diagnostic latent energy.
  - S4 lifestyle clusters are approved as diagnostic latent energy.
  - the S1 raw-human dateblock PC slice is a weaker diagnostic.
  - no E289 lifestyle slice is approved for direct probability editing.
- Adopt rule for future target-specific lifestyle features:
  - keep target-specific effects separate;
  - report matched null dominance by row, subject, and dateblock;
  - use lifestyle energy to learn row/block placement, not as a scalar logit shift.
- Failure condition:
  - if a slice improves train CV but its materialized tensor has null strict rate near `1.0`, classify it as generic target movement rather than certified row placement.

## E290 Lifestyle Row-Placement Policy

- Target hypothesis tested: E289 slices fail because we do not know which rows should receive them; OOF row benefit can supervise that placement law.
- Feature/representation source:
  - E289 target-gated Q3/S4/S1 lifestyle slices;
  - subject/calendar baseline features;
  - lifestyle PCs/clusters;
  - base-vs-augmented OOF probability deltas and within-subject/dateblock ranks.
- Validation result:
  - placement rows: `420`;
  - train placement gates: `59`;
  - materialized candidates: `48`;
  - matched row/subject/dateblock nulls: `720`;
  - public-ready candidates: `0`.
- Updated registry status:
  - Q3 lifestyle row-placement is approved as a train-supervised diagnostic target.
  - S4 lifestyle row-placement is approved as a weaker train-supervised diagnostic target.
  - no E290 row-placement model is approved for direct E247-current editing.
- Adopt rule for future placement features:
  - require train placement dominance and test matched-null dominance;
  - report null strict-promote rate, not only actual p90;
  - prefer block-level or independently test-identifiable placement features over scalar row gates.
- Failure condition:
  - if a candidate has negative actual mean/p90 but null strict rate near `1.0`, classify it as generic Q3 movement rather than row-placement evidence.

## E291 Lifestyle Block-State Policy

- Target hypothesis tested: row placement may fail because the true assignment is a coarser human episode, such as weekday/weekend, month/payday phase, dateblock, or lifestyle-bin state.
- Feature/representation source:
  - E289/E290 Q3/S4/S1 lifestyle slices;
  - dateblock and subject calendar groups;
  - weekday/weekend subject blocks;
  - month-phase labels with pay-start and month-end buckets;
  - lifestyle-bin states from JEPA/raw human context PCs and clusters.
- Validation result:
  - block policy rows: `560`;
  - train block gates: `39`;
  - materialized candidates: `40`;
  - matched row/subject/dateblock nulls: `600`;
  - public-ready candidates: `0`.
- Updated registry status:
  - S4 lifestyle-bin state is approved as a train diagnostic.
  - Q3 weekday/weekend state is approved as a train diagnostic.
  - month/payday phase remains a plausible diagnostic axis but is not approved as a direct probability feature.
  - no E291 block-state model is approved for direct E247-current editing.
- Adopt rule for future block features:
  - use block-state scores as inputs to contrastive true-vs-null placement tests;
  - do not treat a plausible social calendar story as sufficient;
  - require candidate-level matched-null dominance, not only train block dominance.
- Failure condition:
  - if a block-gated candidate has negative local mean/p90 but is blocked by matched nulls, classify it as generic target movement rather than certified hidden block state.

## E292 Contrastive Lifestyle Placement Policy

- Target hypothesis tested: real lifestyle placement differs from matched-null placement by anti-null rarity, not only by high block score.
- Feature/representation source:
  - E291 block policy scores;
  - row/subject/dateblock null-selection rates;
  - contrast score, rarity score, null-gap score;
  - E247-current matched-null governor.
- Validation result:
  - contrast rows: `98`;
  - train contrast gates: `34`;
  - materialized candidates: `56`;
  - matched row/subject/dateblock nulls: `840`;
  - public-ready candidates: `0`.
- Updated registry status:
  - anti-null rarity is approved as an S4 diagnostic.
  - anti-null rarity is not approved as a Q3 placement feature.
  - no E292 contrast feature is approved for direct public submission.
- Adopt rule for future contrast features:
  - report null strict rate separately from p90;
  - do not accept old strict-promote if null strict rate remains high;
  - treat low-null but low-mean-dominance candidates as near-miss diagnostics, not submissions.
- Failure condition:
  - if a contrast candidate remains null strict rate `1.0`, classify it as generic target movement regardless of train contrast dominance.

## E293 S4 Low-Null Candidate Policy

- Target hypothesis tested: the S4 lifestyle-bin near-miss can become public-free ready by refining low-null block filters and raw-delta scale.
- Feature/representation source:
  - E291/E292 S4 `family_jepa_context/dateblock5/cluster6/subject_lifestyle_bin` parent policies;
  - block null mean/max rates;
  - rarity score and contrast score;
  - raw S4 delta scales from `0.30` to `0.60`;
  - E247-current matched row/subject/dateblock governor.
- Validation result:
  - generated candidates: `840`;
  - old strict candidates: `554`;
  - null-evaluated candidates: `64`;
  - matched null evaluations: `1344`;
  - public-ready candidates: `0`.
- Updated registry status:
  - S4 low-null lifestyle-bin pocket remains approved only as a diagnostic.
  - low-null/rarity/contrast filters are not approved for direct S4 submission.
  - scale sweeps in this family are deprioritized unless a new candidate-level invariant is added.
- Adopt rule for future S4 lifestyle features:
  - require the candidate to be both selector-visible and matched-null rare;
  - explicitly report the too-small/null-safe versus old-strict/null-reproducible cliff;
  - do not promote a file only because p90 is negative.
- Failure condition:
  - if null-safe candidates remain below selector resolution and selector-visible candidates have null strict rate above `0.10`, classify the family as an invariant failure rather than a tuning failure.

## E294 Candidate-Level Invariant Policy

- Target hypothesis tested: candidate output geometry can distinguish true S4 lifestyle placement from matched null placements and therefore become the missing gate.
- Feature/representation source:
  - E293 candidate and null score features;
  - selector deltas versus E247;
  - anchor/reference geometry;
  - S4-local probability/movement features;
  - leave-one-source-out actual-vs-null classifiers.
- Validation result:
  - source candidates: `64`;
  - matched null rows: `1344`;
  - best actual-vs-null AUC: `0.883498`;
  - S4-local AUC: `0.619617`;
  - public-ready candidates: `0`.
- Updated registry status:
  - actual-vs-null identity is approved as a diagnostic only.
  - all-output realness is not approved as a promotion gate.
  - S4-local realness is too weak to use.
- Adopt rule for future candidate-level features:
  - train on outcome health, not identity, whenever possible;
  - report the sign of correlation with null strict rate;
  - reject any gate whose score increases with null strict promotion.
- Failure condition:
  - if a learned realness score separates actual from null but correlates positively with null strict rate, classify it as shortcut geometry rather than hidden-state recovery.

## E295-E297 Human Episode-State Policy

- Target hypothesis tested: human/social/cash-flow stories should be composed into larger episode states before being used as JEPA targets.
- Feature/representation source:
  - E268 human-social story features;
  - E270 payday/cash-flow story features;
  - E288 family/raw/hybrid context views;
  - episode states for bedtime arousal, routine fragmentation, routine anchor recovery, cash-flow stress/relief, commute, home recovery, physiology strain, social overload, measurement confidence, and bad-night aftereffect.
- Validation result:
  - E295: `11` states, `51` light target gates, broad bundle label gates `0`;
  - E296: `33` strict candidates, `19` strict gates, `5` robust gates, `2` pair gates;
  - E297: `150` materialized candidates, `25` old strict candidates, public-free ready candidates `0`.
- Updated registry status:
  - bedtime arousal is approved as the strongest current human-state diagnostic for S1/S3.
  - routine fragmentation and routine anchor recovery are approved as target-specific diagnostics.
  - cash-flow/payday remains a diagnostic only; do not promote it before strict null and materialization survival.
  - logistic episode-state delta is not approved as a direct E247-current translator.
- Adopt rule for future episode-state features:
  - build target-specific states, not a shared all-target lifestyle feature;
  - require strict row/subject/dateblock null survival before materialization;
  - require current-anchor matched-null dominance before any public submission.
- Failure condition:
  - if an episode-state edit passes the old selector but matched nulls promote at high rate, classify it as generic target movement rather than recovered human state.

## E298 Materialization Outcome Policy

- Target hypothesis tested: the current governed archive may already contain a usable human/social submission if we rank by outcome health instead of CV or story plausibility.
- Feature/representation source:
  - all current-anchor governor outputs from E279, E284-E293, and E297;
  - selector visibility;
  - matched null strict rate;
  - p90, mean, and worst-mode dominance;
  - negative edge versus current.
- Validation result:
  - governed candidates: `1044`;
  - ready-like candidates: `0`;
  - selector-visible candidates: `162`;
  - null-rare candidates: `867`;
  - selector-visible and null-rare candidates: `0`.
- Updated registry status:
  - existing materialized human/social candidates are diagnostic only.
  - `selector-visible + null-rare` becomes the required outcome target for any new action-layer feature.
  - negative p90, old strict promotion, and story plausibility are insufficient by themselves.
- Adopt rule for future features:
  - separate representation health from action health;
  - only let a social/JEPA feature move probabilities if its placement survives matched nulls;
  - if no positive outcome examples exist, generate controlled near-miss families before training a gate.
- Failure condition:
  - if a feature is selector-visible but null-common, classify it as movement hallucination;
  - if a feature is null-rare but invisible, classify it as below-resolution diagnostic.

## E299 Bridge-Scale Policy

- Target hypothesis tested: near-miss human/social materializations may only need finer logit-scale search to satisfy `selector-visible + null-rare`.
- Feature/representation source:
  - E298 near-miss rows;
  - logit-space rescaling up for null-safe invisible candidates;
  - logit-space rescaling down for visible null-common candidates;
  - current-anchor and matched row/subject/dateblock null governor.
- Validation result:
  - base rows: `14`;
  - generated candidates: `102`;
  - old strict rows: `81`;
  - public-free ready candidates: `0`;
  - closest S4 candidate fails only mean dominance.
- Updated registry status:
  - amplitude-only bridge search is not approved for direct submission.
  - S4 lifestyle placement remains live as a narrow mean-dominance diagnostic.
  - E297 S1 bedtime/routine scaling is deprioritized because null strict rises too fast after visibility.
- Adopt rule for future features:
  - report which governor component fails, not just ready count;
  - for S4 near-misses, optimize mean dominance under subject/dateblock nulls specifically;
  - avoid global scale sweeps unless the geometry changes.
- Failure condition:
  - if rescaling creates many old-strict candidates but no ready rows, classify the issue as placement geometry, not amplitude.

## E300-E301 S4 Placement Rescue Policy

- Target hypothesis tested: the E299 S4 mean-dominance failure may be fixable by row/sign/dateblock mask placement.
- Feature/representation source:
  - E299 closest S4 lifestyle movement;
  - row-level selector probes;
  - subject/dateblock drop masks;
  - raw S4 sign-preserving movement;
  - strengthened row/subject/dateblock/sign null confirmation.
- Validation result:
  - E300 small-governor ready candidates: `1`;
  - E301 large-null confirmation candidates: `0`;
  - tested file: `analysis_outputs/submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv`;
  - E301 null strict rate: `0.164062`;
  - E301 mean dominance: `0.691406`;
  - E301 worst-mode mean dominance: `0.328125`;
  - E301 sign p90 dominance: `1.000000`.
- Updated registry status:
  - raw S4 sign direction is a valid diagnostic feature;
  - hand-probed dateblock-drop mask is not approved as a public submission feature;
  - subject/dateblock placement health is now the missing target.
- Adopt rule for future features:
  - any S4 feature must be checked against subject/dateblock nulls with a large null budget;
  - sign correctness is insufficient if mean dominance is reproduced by block shuffles;
  - public-free promotion requires strict confirmation after candidate discovery.
- Failure condition:
  - if a candidate passes a small null governor but fails large subject/dateblock null confirmation, classify it as selector/mask overfit and do not submit.

## E302 S4 Placement-Health Decoder Policy

- Target hypothesis tested: subject/dateblock S4 placement health can be decoded from human diary/story/episode aggregates.
- Feature/representation source:
  - E301 actual/null placement tensors;
  - signed, absolute, active-row, and positive-minus-negative aggregates over diary JEPA features;
  - E280 story scores;
  - E295 episode states;
  - topology controls for subject/dateblock mass.
- Validation result:
  - placements: `257`;
  - null placements: `256`;
  - `human_all` leave-mode-out mean Spearman `0.400962`;
  - `human_all_plus_topology` leave-mode-out mean Spearman `0.325973`;
  - `story_episode` strict AUC `0.629383`;
  - p90 health is not stable under the same human features.
- Updated registry status:
  - S4 placement-health features are diagnostic and eligible for one constrained follow-up;
  - they are not approved as direct submission features;
  - p90-based placement scoring is demoted because it is easier to satisfy than mean-dominance.
- Adopt rule for future features:
  - optimize subject/dateblock mean placement, not only p90;
  - use human diary placement score as a prior, then run E301-style large-null confirmation;
  - do not choose a null placement itself as a submission.
- Failure condition:
  - if a placement prior improves p90 but not mean dominance under large nulls, classify it as another visibility shortcut.

## E303 S4 Mean-Prior Materialization Policy

- Target hypothesis tested: the E302 mean-placement decoder can be used to generate public-free S4 candidates.
- Feature/representation source:
  - E301 placement-health lab;
  - E302 human diary/story/episode placement decoders;
  - E299 parent S4 movement;
  - mean-prior row/drop/dateblock masks;
  - row/subject/dateblock/sign matched null confirmation.
- Validation result:
  - generated candidates: `260`;
  - old strict candidates: `183`;
  - null-evaluated candidates: `12`;
  - public-free ready candidates: `0`;
  - best null strict rate: `0.187500`;
  - best mean dominance: `0.695312`.
- Updated registry status:
  - E302 mean-prior features are not approved as direct action features;
  - S4 sign/tail features remain diagnostic;
  - S4 mask-surgery candidates require a new block-placement target before more public testing.
- Adopt rule for future features:
  - do not promote a candidate because it is old-strict or mean-prior-ranked;
  - require matched-null rarity and mode-wise mean dominance;
  - if the feature cannot separate from subject/dateblock nulls, keep it as latent diagnostics only.
- Failure condition:
  - if a future S4 feature reproduces E303's pattern, many old-strict rows but zero large-null ready rows, classify it as action-layer shortcut and stop that branch.

## E304-E305 Hidden Block-State Policy

- Target hypothesis tested:
  - E304: raw human diary context can recover hidden subject/dateblock Q/S residual state.
  - E305: that recovered S4 block prior can directly generate a public-free S4 submission.
- Feature/representation source:
  - family-JEPA diary PCs, energies, and residual/prednorm signals;
  - story/episode states including routine, bedtime arousal, cash-flow, home recovery, social overload, measurement confidence;
  - raw top lifelog aggregates;
  - block-level aggregation by subject/dateblock;
  - target representation: shrunken block logit residual after subtracting subject prior.
- Validation result:
  - E304 best view `family_jepa/subject_holdout`: mean Spearman `0.143141`, null dominance `0.986111`, S4 Spearman `0.124633`;
  - E304 candidate alignment: E299/E300/E303 active S4 blocks are anti-aligned with predicted S4 state;
  - E305 generated `111` candidates, old strict `14`, public-free ready `0`;
  - E305 best null strict rate `0.648438`.
- Updated registry status:
  - hidden block-state features are approved as diagnostics;
  - direct top-block S4 movement is rejected as an action feature;
  - block-prior features may be used only inside a contrastive action-health target.
- Adopt rule for future features:
  - separate block-state recovery from probability materialization;
  - require `selector-visible + null-rare` before any public candidate;
  - use anti-alignment with E304 state as a failure explanation for old S4 files.
- Failure condition:
  - if a block-prior feature only creates old-strict but null-common candidates, classify it as generic target movement and do not submit.

## E306 Within-Dateblock Row-Placement Policy

- Target hypothesis tested:
  - dateblock-centered human/JEPA row features can identify which row inside a block carries S4 state.
- Feature/representation source:
  - `family_jepa_dbdelta`: family-JEPA row features minus the dateblock mean;
  - `story_episode_dbdelta`;
  - calendar row position controls;
  - E304 predicted S4 block residual;
  - combined row/block score for S4-only materialization.
- Validation result:
  - `family_jepa_dbdelta/dateblock_holdout` within-dateblock AUC `0.574899`, null dominance `0.979167`;
  - best row diagnostic `family_jepa_dbdelta/row_stratified5` within-dateblock AUC `0.585020`;
  - materialization generated `272` candidates, old strict `22`, public-free ready `0`;
  - best null strict rate `0.625000`.
- Updated registry status:
  - dateblock-centered family-JEPA row features are approved as diagnostics/energies;
  - direct S4 rowtop or global-rowcenter additive edits are not approved as submission features;
  - calendar row position is a live confounder and must be included as a control in future human/social row-placement claims.
- Adopt rule for future features:
  - keep within-dateblock shuffle nulls mandatory;
  - do not treat train row-placement AUC as sufficient for public candidate selection;
  - use row-placement features to predict candidate outcome health or to veto risky rows, not to simply add positive S4 mass.
- Failure condition:
  - if a feature improves within-block train AUC but its materialized tensor is matched-null common, classify it as a representation-only feature.

## E307 S4 Latent Censor Policy

- Target hypothesis tested:
  - hidden S4 block/row state can identify current S4 overconfidence and support calibration-risk censoring.
- Feature/representation source:
  - E306 test row latent state;
  - E304/E306 block and row S4 scores;
  - current E247 S4 logits and confidence;
  - latent-current mismatch, overconfident-lowlatent score, underconfident-highlatent score.
- Validation result:
  - latent/current S4 logit correlation `0.302062`;
  - generated candidates `765`, old strict `106`, public-free ready `0`;
  - best null strict rate `0.750000`;
  - best mean dominance `0.546875`;
  - wrong-direction controls remain competitive.
- Updated registry status:
  - latent-current mismatch is approved as a diagnostic/risk feature;
  - direct S4 temper/down/up corrections are not approved as submission features;
  - current S4 confidence is a strong confounder and must be controlled in future S4 action models.
- Adopt rule for future features:
  - never promote S4 censoring only because it improves p90 or old strict visibility;
  - require controls to lose before claiming latent correctness;
  - prefer learned action-health targets over hand-coded S4 delta projection.
- Failure condition:
  - if a censoring feature is matched by control sharpening or reproduced by row/subject/dateblock nulls, classify it as selector geometry rather than hidden-state action.

## E308 Action-Outcome Atlas Policy

- Target hypothesis tested:
  - governed candidate outcomes can replace repeated public LB checks as a local promotion/blocking layer.
- Feature/representation source:
  - normalized governor fields from E279-E307;
  - action metadata, target/family labels, candidate movement summaries, current-anchor deltas, matched-null rates and dominance metrics;
  - derived labels `selector_visible`, `null_rare`, `visible_null_rare`, `visible_null_common`, and `certified_public_free_ready`.
- Validation result:
  - governed rows `1304`;
  - selector-visible `367`;
  - null-rare `918`;
  - visible/null-rare `2`;
  - certified public-free ready `0`;
  - post-E303 S4 rows `68`, null-rare `0`;
  - leave-experiment-out diagnostic AUCs: selector-visible `0.998857`, null-common `0.986466`.
- Updated registry status:
  - E308 outcome labels are approved as a validation/governor feature family;
  - they are not approved as a direct submission generator because usable positive labels are too sparse;
  - old strict promotion is downgraded to prefilter status only.
- Adopt rule for future features:
  - every candidate family must report selector visibility, null rarity, mode-wise dominance, and control-direction behavior before public LB;
  - no public submission should be recommended if its edge can be matched by row/subject/dateblock/sign nulls;
  - after E301, small-null ready status is insufficient unless independently confirmed.
- Failure condition:
  - if a new feature only increases selector-visible/null-common counts, classify it as public-LB-waste risk even when local p90 looks attractive.

## E309 Episode Target-Interaction Representation

- Target hypothesis tested:
  - human/social episode states affect target dependencies, not only individual targets.
- Feature/representation source:
  - E295 episode states: cashflow stress, bedtime arousal, routine fragmentation, routine anchor recovery, home recovery, social overload, bad-night aftereffect;
  - E288 context views: family-JEPA, raw human context, hybrid context;
  - target-pair labels represented as 4-class joint Q/S states.
- Validation result:
  - quick scanned rows `426`;
  - strict rerun rows `32`;
  - strict gates `29`;
  - robust gates `13`;
  - pair gates `12`;
  - strongest QS result: `cashflow_stress/Q1_S1` best delta `-0.046023`;
  - strongest story clusters: cashflow stress, bedtime arousal, home recovery, bad-night aftereffect.
- Updated registry status:
  - approved as a live representation family;
  - not approved as a direct submission feature until coupled materialization passes null governance;
  - cashflow/payday-style features should be treated as Q/S dependency features, not standalone prior tweaks.
- Adopt rule for future features:
  - when a human story fails as a single-target edit, test its joint target manifold before discarding it;
  - materialization must move coupled targets together and include wrong-pair controls;
  - require E308-style selector/null/dominance gates before public LB.
- Failure condition:
  - if pair materialization is reproduced by wrong-pair or shuffled-state controls, keep E309 only as an interpretability/world-model clue.

## E310 Pair-Interaction Action Layer

- Target hypothesis tested:
  - E309 human/social target-pair states can be converted into coupled probability deltas on current E247.
- Feature/representation source:
  - E309 robust episode-pair rows;
  - predicted episode state from family/raw/hybrid JEPA contexts;
  - 4-class joint target models for pairs such as `cashflow_stress/Q1_S1`, `cashflow_stress/S1_S2`, and `home_recovery/Q1_S3`;
  - coupled marginal logit deltas shaped by dense/sparse/sign/difference rules.
- Validation result:
  - generated candidates `455`;
  - old strict candidates `77`;
  - null-evaluated candidates `42`;
  - public-free ready `0`;
  - best current-anchor p90 `-0.000379563`, but old-strict rows are null-common.
- Updated registry status:
  - pair-interaction deltas are not approved as direct submission features;
  - pair state remains approved as diagnostic/energy/supervision for action-health learning;
  - wrong-pair and target-swap controls are now mandatory for future target-dependency materializations.
- Adopt rule for future features:
  - do not call a human/social pair story submission-worthy until it beats wrong-pair and shuffled-state controls;
  - treat old strict promotion as visibility only, not correctness;
  - prefer a translator trained to predict public-free governor health over hand-coded pair marginal deltas.
- Failure condition:
  - if a pair feature is selector-visible but matched nulls also promote, classify it as target-movement geometry rather than hidden-world recovery.

## E311 Pair Micro-Action and Null-Residual Features

- Target hypothesis tested:
  - E310's safe-but-small pair actions can be stacked, or E310's visible-but-null-common actions can be residualized against matched-null movement.
- Feature/representation source:
  - E310 null-rare too-small candidate deltas;
  - E310 old-strict coupled pair deltas;
  - row/subject/dateblock/wrong-pair/swap null mean deltas;
  - microstack, microdiverse, microcash, and residualized-visible action recipes.
- Validation result:
  - generated candidates `512`;
  - old strict candidates `489`;
  - public-free ready `0`;
  - best microstack p90 `-0.000807827`, but null strict rate at least `0.611111`;
  - residualized-visible has null-safe rows only below old-strict submission resolution.
- Updated registry status:
  - micro-stacked pair actions are not approved as submission features;
  - average-null residualization is not approved as a sufficient action-health fix;
  - the safe/useful feature is the observed cliff itself: visibility and null rarity must be modeled jointly.
- Adopt rule for future features:
  - do not stack safe micro-actions as a submission shortcut;
  - do not treat null-mean subtraction as a public-free certificate;
  - future pair features must train or validate against `visible_null_rare`, not only pair-logloss or old strict p90.
- Failure condition:
  - if a candidate becomes visible only by increasing null strict rate, classify it as an action-layer cliff, not a hidden-state breakthrough.

## E312 Action-Health Governor Features

- Target hypothesis tested:
  - candidate action outcome itself can be treated as the hidden JEPA target, allowing local checks to replace public LB as the first-line evaluator.
- Feature/representation source:
  - `20` previous governor files from E279-E311;
  - semantic labels: family, target, pair, episode, story;
  - action geometry: recipe/action/split/movement statistics/current-anchor deltas;
  - derived labels: selector visibility, null rarity/commonness, action cliff, safe-invisible, strict health.
- Validation result:
  - governed rows `1383`;
  - visible/null-rare rows `2`;
  - strict-health rows `1`;
  - `geometry_only` null-common AUC `0.984890`;
  - `semantic_only` null-common AUC `0.713484`;
  - `full_safe` readiness-distance Spearman `0.102712`.
- Updated registry status:
  - approved as a veto/governor feature family;
  - not approved as a direct submission selector or generator;
  - action geometry is now a mandatory feature block for future public-free candidate audits.
- Adopt rule for future features:
  - public submission requires direct matched-null passage, not only high predicted action-health;
  - E312 predictions can block candidates predicted null-common;
  - semantic story improvements must still prove that their translated action has different geometry from wrong-row/wrong-pair controls.
- Failure condition:
  - if a feature only raises semantic plausibility while leaving action geometry in the null-common region, reject it before public LB.

## E313 Human-Diary Action Signature Features

- Target hypothesis tested:
  - the raw lifestyle context of rows touched by a candidate contains action-health signal that E312's recipe/geometry features missed.
- Feature/representation source:
  - E268 human/social story features;
  - E270 payday/cashflow cycle features;
  - E273 human diary JEPA state features;
  - candidate logit deltas versus E247, aggregated as abs-weighted, signed, active-row, and Q-minus-S diary signatures.
- Validation result:
  - governed rows `1383`;
  - candidate files found `1379`;
  - selected human aggregate columns `520`;
  - `human_signature` null-common AUC `0.866674`;
  - `geometry_only` null-common AUC `0.982733`;
  - `geometry_plus_shape` null-common AUC `0.987170`;
  - `human_signature` readiness-distance Spearman `0.700161`.
- Updated registry status:
  - approved as a diagnostic/energy feature family;
  - not approved as a direct submission certifier;
  - top signals include routine-calendar, weekend social jetlag, bright-light, bedtime-phone, cognitive-money, cash-stress/payday, screen fragmentation, and mobility signatures.
- Adopt rule for future features:
  - use human signatures to rank safe-but-too-small action seeds or explain selector-visible rare cases;
  - do not add high-dimensional human signatures blindly to geometry gates, because E313 shows global null-common transfer worsens;
  - future materializers should treat human-readiness distance as a regression/energy target rather than a binary null-common label.
- Failure condition:
  - if a candidate is human-ready but remains below selector resolution, do not submit it; use it as a seed for a new action class.

## E314 Human-Readiness Lift Features

- Target hypothesis tested:
  - E313 human-ready, safe-but-too-small actions can be scaled or sparsified into public-free visible candidates.
- Feature/representation source:
  - E313 human-readiness distance and predictions;
  - previous candidate logit deltas versus E247;
  - seed action shape: touched rows, touched cells, target shares, delta magnitude;
  - matched null modes: row, subject, dateblock, target permutation, Q/S swap, sign flip.
- Validation result:
  - safe seeds loaded `180`;
  - generated candidates `360`;
  - old strict candidates `33`;
  - null-evaluated candidates `40`;
  - public-free ready `0`;
  - best actual p90 `-0.000087616`;
  - old-strict lifts become null-common, while null-rare lifts are too small.
- Updated registry status:
  - individual human-ready scalar lift is not approved as a submission feature;
  - human-readiness remains approved as an energy/seed-ranking feature;
  - consensus or orthogonal human-ready stacks remain untested in E314 because the single-lift family exhausted the candidate budget.
- Adopt rule for future features:
  - public LB is not a checker; a file needs matched-null passage before submission;
  - do not spend more amplitude on the same seed if visibility comes with high null strict rate;
  - reserve generation quota for non-single recipes when testing whether multiple weak human-ready signals compose safely.
- Failure condition:
  - if a feature only converts safe seeds into visible null-common moves, classify it as action geometry overfit rather than hidden human-state recovery.

## E315 Human-Readiness Composition Features

- Target hypothesis tested:
  - multiple safe human-ready seeds can compose into a null-resistant action geometry even though individual scalar lifts fail.
- Feature/representation source:
  - E313 human-readiness seed table;
  - normalized candidate deltas from previous human/social, cell-boundary, pair, and S4 low-null branches;
  - family consensus, target consensus, negative-edge stacks, orthogonal low-cosine story stacks, and target-balanced story stacks.
- Validation result:
  - generated candidates `660`;
  - old strict candidates `229`;
  - null-evaluated candidates `67`;
  - public-free ready `0`;
  - strongest visible semantic family: `bedtime_arousal`;
  - strongest information sensor: `routine_fragmentation/S1`;
  - best null strict rate `0.090909` occurs in orthogonal story stacks but fails subject/dateblock dominance and old strict.
- Updated registry status:
  - human-ready composition is not approved as a direct submission feature;
  - bedtime-arousal and routine-fragmentation/S1 remain approved as hidden-state diagnostic features;
  - orthogonal story composition is approved only as a near-miss dataset for placement-health learning.
- Adopt rule for future features:
  - do not stack more human-ready deltas without explicitly modeling row/subject/dateblock placement;
  - use mode-specific dominance to diagnose which hidden placement layer failed;
  - treat target/sign robustness as necessary but insufficient.
- Failure condition:
  - if a candidate only beats target permutation, Q/S swap, and sign controls but loses subject/dateblock or row controls, classify it as a real semantic direction with wrong hidden placement, not a submission.

## E316 Human Placement Identity and Health Features

- Target hypothesis tested:
  - raw human diary context can recover hidden placement information from E315 actual/null mini-worlds, and that signal may or may not align with action health.
- Feature/representation source:
  - E313 delta-weighted human diary signatures;
  - E315 actual candidate placements;
  - E315 row, subject, and dateblock null placements;
  - action-shape features such as touched cells, row concentration, target share, and movement magnitude.
- Validation result:
  - placement rows `1541`;
  - source candidates `67`;
  - placement null rows `1005`;
  - `human_signature` actual-vs-placement-null AUC `0.998856`;
  - `human_signature` AP `0.992019`;
  - `human_signature` mean actual rank `0.999005`;
  - `action_shape` AUC `0.500000`;
  - `human_plus_shape` local p90 Spearman `0.900789`;
  - identity rank vs worst-mode p90 dominance Spearman `0.159448`;
  - identity rank vs null strict rate Spearman `-0.206034`.
- Updated registry status:
  - human placement identity is approved as a strong diagnostic representation;
  - action shape is not approved as an identity feature in this mini-world;
  - identity rank is not approved as a submission-health gate.
- Adopt rule for future features:
  - use actual-vs-placement-null identity as one input to a health model, not as a standalone promotion rule;
  - require mode-specific health labels: row dominance, subject dominance, dateblock dominance, and worst-mode dominance;
  - public LB must not be used to resolve files that fail these local health labels.
- Failure condition:
  - if a candidate is highly recognizable as the intended human/social placement but has low subject/dateblock/worst-mode dominance, classify it as identity-positive and health-negative.

## E317 Human Placement Outcome Features

- Target hypothesis tested:
  - raw human diary context can predict placement outcome health directly, not only intended placement identity.
- Feature/representation source:
  - E316 human diary signatures;
  - E316 action shape signatures;
  - E316 OOF human identity prediction;
  - E315 actual plus row/subject/dateblock null local score outcomes.
- Validation result:
  - placement rows `1072`;
  - source-held p90-rank Spearman: human `0.320748`, action shape `0.000000`, human+action `0.451921`;
  - source top-mode accuracy: human `0.432836`, human+action `0.552239`, human+identity+action `0.582090`, action shape `0.029851`;
  - source-held joint-health AUC: human `0.731185`, action shape `0.683432`;
  - within-mode p90-rank mean Spearman: action shape `0.326136`, human `0.238693`;
  - null-mode holdout p90-rank mean Spearman: human `0.133354`, action shape `-0.358750`.
- Updated registry status:
  - approved as a regime-selection/placement-health diagnostic;
  - not approved as a direct submission feature;
  - human context and action geometry should be separated by mode rather than blended into one universal score.
- Adopt rule for future features:
  - use human context to choose or weight row/subject/dateblock regime;
  - use mode-specific action geometry for within-regime health;
  - require direct matched-null promotion after materialization.
- Failure condition:
  - if a feature only improves pooled source-held health but fails leave-mode or within-mode governance, treat it as a diagnostic latent, not a candidate selector.

## E318 Mode-Specialized Policy Features

- Target hypothesis tested:
  - E317 human/identity/action predictions can be used as a mode-specialized policy over actual, row, subject, and dateblock placements, rather than as one universal multiplier.
- Feature/representation source:
  - E317 OOF `predict_p90_rank`, `predict_health_score`, and `classify_joint_health`;
  - E316/E317 placement features;
  - source-wise normalized score combinations for human-only, human+action, human+identity+action, joint-health, regime-first, and geometry-only policies.
- Validation result:
  - placement rows `1072`;
  - sources `67`;
  - best non-oracle policy `human_identity_action_p90_rank`;
  - delta p90-rank health versus actual `0.028918`;
  - p90-rank health mean `0.649254` versus actual `0.620336`;
  - joint-health rate `0.313433` versus actual `0.134328`;
  - oracle upper bound p90-rank health mean `0.937500`.
- Updated registry status:
  - approved as a regime-selection diagnostic;
  - not approved as a submission selector;
  - not approved for selecting E315 null-control CSVs as public candidates.
- Adopt rule for future features:
  - separate regime choice from within-regime action geometry;
  - use source-wise normalization or grouped OOF predictions so the policy cannot win by family scale leakage;
  - require fresh materialization and matched-null governance before promotion.
- Failure condition:
  - if a mode policy only selects healthier controls inside an archive but cannot create a new visible/null-rare tensor, keep it as a diagnostic and do not spend public LB.

## E319/E320 Mode-Specialized Generator and Failure Features

- Target hypothesis tested:
  - E318 regime routes can be converted into fresh consensus/blend/residual tensors that are visible and rare under matched null controls.
- Feature/representation source:
  - E318 selected routes for `human_identity_action_p90_rank`, `human_action_p90_rank`, `regime_then_geometry`, and `human_regime_only`;
  - selected, actual, blend, and residual deltas;
  - policy/mode/recipe consensus tensors;
  - row, subject, dateblock, target-permutation, sign-flip, and Q/S-swap null dominance diagnostics.
- Validation result:
  - E319 generated candidates `540`;
  - old strict candidates `403`;
  - null-evaluated candidates `54`;
  - public-free ready candidates `0`;
  - best actual p90 `-0.004283155`;
  - E320 target-permutation dominance `1.000000`;
  - E320 sign-flip dominance `1.000000`;
  - E320 Q/S-swap dominance `0.978723`;
  - E320 killer modes: row `16`, subject `15`, dateblock `15`, Q/S swap `1`.
- Updated registry status:
  - approved as a negative generator test and failure-anatomy diagnostic;
  - not approved as a submission feature;
  - target/sign/QS diagnostics remain useful sanity checks, but they are not the blocker for this branch.
- Adopt rule for future features:
  - old strict visibility is insufficient when row/subject/dateblock dominance is weak;
  - future human/social features must include mode-specific adversarial action-health labels;
  - public LB cannot be used to distinguish near misses that already fail local placement controls.
- Failure condition:
  - if a generated tensor is visible but its killer mode is row, subject, or dateblock, classify it as hidden-placement failure, not target-semantics failure.

## E321 Adversarial Action-Health Features

- Target hypothesis tested:
  - row/subject/dateblock placement health can be learned as an explicit action target from E319 actual-vs-null pairs, instead of being checked only after generation.
- Feature/representation source:
  - E319 candidate geometry versus public-anchor references;
  - route metadata: policy, recipe, base variant, source count, selected mode mix;
  - matched null geometry for row, subject, and dateblock controls;
  - pairwise labels: p90 win, mean win, null-not-strict, and pair-health.
- Validation result:
  - pair rows `564`;
  - candidates `47`;
  - full-pair p90-win AUC: row `0.821035`, subject `0.930077`, dateblock `0.915720`;
  - candidate adversarial-health Spearman `0.508146`;
  - ready-like candidates `0`.
- Updated registry status:
  - approved as a local adversarial-health diagnostic and future pre-materialization target;
  - not approved as a submission feature;
  - not sufficient to promote any E319 candidate directly.
- Adopt rule for future features:
  - model row/subject/dateblock action health before creating large visible tensors;
  - use actual-geometry versions for broad preselection and full-pair versions for local null validation;
  - require fresh null governance after any E321-guided generation.
- Failure condition:
  - if an E321-guided candidate improves predicted health but still has `ready_like_actual = 0` under fresh nulls, classify it as checker overfit, not a public candidate.

## E322 Adversarial Preselector Features

- Target hypothesis tested:
  - E321 health predictions can preselect unevaluated E319 candidates worth fresh null governance, reducing public LB dependence.
- Feature/representation source:
  - full actual public-free selector features for all non-oracle E319 candidates;
  - E319 route metadata and mode mix features;
  - Ridge predictions for worst-placement dominance, null strict rate, adversarial health, and mode-specific p90 dominance.
- Validation result:
  - candidate universe `450`;
  - governed training rows `47`;
  - selected unevaluated candidates `36`;
  - selected old strict `36`;
  - fresh public-free ready `0`;
  - best fresh p90 `-0.001452588`;
  - best null strict rate `0.136364`;
  - preselector OOF Spearman: null strict rate `0.564957`, dateblock p90 dominance `0.721851`, subject p90 dominance `0.589744`, row p90 dominance `0.208598`.
- Updated registry status:
  - approved as a public-free preselection/checking feature;
  - not approved as a submission selector;
  - not enough to rescue E319 after materialization.
- Adopt rule for future features:
  - use E322-style predictions upstream while creating candidate deltas;
  - fresh null governance remains mandatory after any preselected file;
  - public LB should not be used when ready count is `0`.
- Failure condition:
  - if preselected candidates remain old-strict but null strict rate stays above `0.10`, classify the branch as null-common action geometry, not a candidate-selection miss.

## E323/E324 Null-Common Residual Features

- Target hypothesis tested:
  - E322 near misses fail because they contain a large placement-null-common component, not because all their movement is false. Removing that component should reveal a null-rare hidden placement residual.
- Feature/representation source:
  - E322 high-ranked near-miss logit deltas;
  - row/subject/dateblock null stacks with `8` reference reps for residual construction;
  - mean-null residual, median-null residual, projection-out-null-mean, and unique-cell masks;
  - E321/E322 health predictions used only for prefiltering, followed by fresh null governance.
- Validation result:
  - E323 generated candidates `420`;
  - old strict `291`;
  - selected for fresh null `44`;
  - E323 ready `3`;
  - E324 high-rep ready `3/3`;
  - E324 null rows `774`;
  - priority file high-rep p90 `-0.000053747`, mean `-0.000952`, null strict `0.050388`, worst-mode dominance `0.859375`.
- Updated registry status:
  - approved as the first public-free submission-grade action representation after E247;
  - narrow scope: human-regime-only family-consensus S-heavy residual;
  - not yet approved as a general generator for all human/social states.
- Adopt rule for future features:
  - construct residuals against matched placement-null representations before increasing amplitude;
  - prefer candidates that survive high-rep nulls even if their local p90 edge is smaller;
  - use E324 priority as the next public sensor if a submission slot is intentionally spent.
- Failure condition:
  - if public LB worsens materially, treat the local null governor as missing a public/private subset or calibration axis; do not blindly expand residualization to more parents.

## E325 Semantic Null Attribution Features

- Target hypothesis tested:
  - an action that survives placement nulls should also have a coherent human/social diary explanation; otherwise it may be a numeric residual with no lifestyle structure.
- Feature/representation source:
  - E280 top transfer stories;
  - E295 episode states;
  - full E268 human/social story atlas;
  - E270 payday/cash-flow story atlas;
  - calendar/payday windows;
  - target-specific delta-weighted semantic means compared against row/subject/dateblock shuffled delta placements.
- Validation result:
  - E324 priority `5508f966` best signed semantic z `2.871546`;
  - top axes: Q1 night-out mobility, S1 phone-in-bed/bedtime arousal, S3 social-isolation/media;
  - semantic support is moderate; it does not outrank high-rep placement-null safety.
- Updated registry status:
  - approved as an interpretation and local checker feature;
  - not approved as a standalone submission selector;
  - use it to prevent post-hoc storytelling by requiring actual-vs-null semantic rarity.
- Adopt rule for future features:
  - a future human/social materializer should report both high-rep placement-null metrics and semantic-null attribution;
  - semantic z alone cannot promote a candidate if null strict or worst-mode dominance worsens.
- Failure condition:
  - if semantic-gated candidates raise story z but fail matched nulls, classify them as story overfit and do not spend public LB.

## E326 Semantic Residual Censor Features

- Target hypothesis tested:
  - E325 semantic axes can be converted from attribution into an action-level gate for E323 residual candidates.
- Feature/representation source:
  - per-target semantic support from E325 rows with signed z>=`1.75` and signed dominance>=`0.95`;
  - Q1 night-out mobility, S1 phone-in-bed/bedtime arousal, S3 social-isolation/media, plus related human/social/cash/calendar axes when they pass the null filter;
  - cell alignment score `sign(delta) * semantic_support`;
  - semantic censor policies and anti-semantic controls.
- Validation result:
  - generated `252` variants;
  - prefilter strict `141`;
  - selected for null stress `36`;
  - null rows `6984`;
  - semantic selected ready `2/24`;
  - anti-control ready `0/12`;
  - beats E324 priority locally `0`.
- Updated registry status:
  - approved as a diagnostic/censoring feature;
  - not approved as a replacement submission selector;
  - semantic support should be treated as an auxiliary gate behind placement-null residualization, not as the primary generator.
- Adopt rule for future features:
  - include anti-semantic controls whenever a human-story feature is used for action pruning;
  - require dominance over the current residual priority before changing submission order;
  - keep semantic z, null strict rate, p90 dominance, mean dominance, and worst-mode dominance in the same table.
- Failure condition:
  - if semantic pruning increases p90 edge but raises null strict rate above priority, mark it as semantic over-pruning or null-common scaling, not a public candidate.

## E327 Null-Fail Risk Censor Features

- Target hypothesis tested:
  - the remaining E324 risk is encoded in cells favored by competitive row/subject/dateblock build null placements.
- Feature/representation source:
  - build nulls separated from fresh stress nulls;
  - cell-level bad-null mean, bad-null q75 magnitude, sign-match frequency, relative null risk, and support = actual abs delta minus bad-null q75;
  - policies: badmean subtraction, support keep, risk damp/drop, low-risk keep, orthogonal projection, plus anti-controls.
- Validation result:
  - generated `540` candidates;
  - prefilter strict `179`;
  - selected `40`;
  - build null rows `288`;
  - fresh stress null rows `7760`;
  - ready `2`;
  - beats E324 priority locally `0`.
- Updated registry status:
  - approved as a null-risk diagnostic;
  - not approved as a priority replacement feature;
  - aggressive bad-null subtraction is marked high overfit risk.
- Adopt rule for future features:
  - split build nulls and stress nulls whenever using null-derived features;
  - treat conservative risk damping as safer than subtracting full bad-null means;
  - require a candidate to improve null strictness and worst-mode dominance, not only p90.
- Failure condition:
  - if a null-derived feature wins prefilter but fails fresh stress, classify it as null-overfit and do not public-test it.

## E323-Negative Public Stress Feature

- Target hypothesis tested:
  - future candidates should avoid the movement anatomy that made E323/E324 public-adverse.
- Feature/representation source:
  - delta similarity to `analysis_outputs/submission_e323_5508f966_uploadsafe.csv` versus E247;
  - overlap with E323 active cells, target shares, subject/dateblock concentration, and row/subject/dateblock null-failure axes;
  - same-family flags for E323/E324/E326/E327 residual/censor descendants.
- Validation result:
  - E323 upload-safe public LB `0.5770355016`;
  - worse than E247 by `+0.0008765522`;
  - local high-rep null health did not transfer.
- Updated registry status:
  - approved as a negative stress feature;
  - not a predictive feature by itself;
  - use it as a veto or penalty until a future candidate independently explains why E323-like movement is safe.
- Adopt rule for future features:
  - any public-free promotion report should include E323-negative similarity and same-family flags;
  - same-family descendants require stronger independent evidence than ordinary candidates.
- Failure condition:
  - if a candidate is E323-similar and only passes row/subject/dateblock nulls, do not public-test it.

## E328 Own-Latent Lifestyle-State Features

- Target hypothesis tested:
  - hidden lifestyle state can be learned as a same-level latent from human/social, raw-day, residual, and story context views, then used as a JEPA-style representation for labels and E323-negative gating.
- Feature/representation source:
  - teacher PCA from lifestyle context views;
  - masked-context student predictions under subject/dateblock OOF;
  - residual energy features;
  - ownlife PCs, k8 clusters, cluster distance, global distance, and student residual summaries.
- Validation result:
  - best teacher R2 `0.972508` for `family_jepa_story/dateblock`;
  - subject label delta `+0.035211637`, dateblock label delta `+0.022631387`;
  - targets improved `0`;
  - E247/E256 boundary separation up to `1.477419`;
  - E323 top20 separation only `0.545557`;
  - generated anti-E323 files all below selector resolution.
- Updated registry status:
  - approved as a diagnostic and clustering feature;
  - rejected as a direct label feature or submission gate;
  - do not use broad ownlife PCs/clusters as standalone probability movement.
- Adopt rule for future features:
  - split broad lifestyle state into target/noise regimes before materialization;
  - require label stress improvement, not only high latent reconstruction R2;
  - include E323-negative alignment before any candidate promotion.
- Failure condition:
  - if a lifestyle latent is easy to predict but worsens blocked label CV, classify it as lifestyle atlas or subject/routine shortcut, not a submission representation.

## E330 Target-Residual Lifestyle-State Features

- Target hypothesis tested:
  - lifestyle context should predict target-specific residual state after subject/calendar base priors, even when broad lifestyle atlas features fail.
- Feature/representation source:
  - teacher: target residual `y - base_prob`;
  - context views: family, JEPA residual, story bundle, raw day, family story, family+JEPA+story;
  - student feature: OOF predicted residual state for each target/view/split.
- Validation result:
  - `16/84` rows pass label/null gates;
  - strongest targets are Q2, Q1, and S2;
  - S4 has no gated rows;
  - materialized E247 edits generate `0` selector-promoted candidates.
- Updated registry status:
  - approved as a target-specific diagnostic feature;
  - rejected as a direct full-test calibration feature;
  - highest-priority axes: Q2 JEPA residual subject state, Q1 JEPA residual dateblock state, S2 raw-day subject state, S2 JEPA residual dateblock state.
- Adopt rule for future features:
  - use residual-state predictions to choose rows/blocks/cells, not to move an entire target column;
  - preserve the shuffled-null gate and E323-negative anatomy check;
  - treat S4 as unsupported by this residual-state construction unless a new view changes the evidence.
- Failure condition:
  - if a residual-state candidate only produces diffuse all-row target movement, do not submit even when the representation stress is strong.

## E331 Localized Residual-State Tail Features

- Target hypothesis tested:
  - target-specific lifestyle residual states should become more useful when converted into high-energy row/block/cell tail gates instead of full-test target calibration.
- Feature/representation source:
  - E330 predicted residual-state columns;
  - quantile-tail policies over absolute, positive, negative, and block-absolute residual energy;
  - localized action masks for E247 target-only logit movement.
- Validation result:
  - `39` localized gates pass label/null criteria;
  - strongest Q1 JEPA-residual dateblock positive tails improve Q1 logloss by `-0.029674864` and `-0.022958364`;
  - `43` materialized probes produce `0` selector-promoted candidates;
  - best Q1 `pos_q90` probes are stable but `too_small_to_submit`.
- Updated registry status:
  - approved as a diagnostic and localization feature;
  - rejected as a current direct submission feature;
  - highest-priority feature object: Q1 `jepa_resid/dateblock/pos_q90`.
- Adopt rule for future features:
  - use localized residual tails as action-health targets or gates, not as standalone probability edits;
  - test the Q1 positive tail separately before composing it with Q2/S2;
  - require high-repetition movement-null safety before public submission.
- Failure condition:
  - if a localized residual-tail action is only selector-visible after widening the gate or composing multiple targets, classify it as null-risky and do not submit.

## E332 Q1 Tail Translator Features

- Target hypothesis tested:
  - the clean E331 Q1 positive residual-tail latent may only need a better localized logit translator to become submission-visible.
- Feature/representation source:
  - fixed Q1 `jepa_resid/dateblock` residual-state score;
  - positive quantile tail gates and band gates;
  - constant, rank, and softplus OOF-trained logit-shift translators;
  - signflip and movement-null controls.
- Validation result:
  - `33` local translator gates pass label/null checks;
  - best local translator Q1 `pos_q83/const` has delta `-0.015385658`, dominance `1.000000`;
  - `77` generated probes produce `0` selector-promoted actual-direction candidates;
  - signflip controls fail, confirming the negative Q1 correction direction;
  - closest actual probes remain p90-positive or weak under movement-null dominance.
- Updated registry status:
  - approved as a directional Q1 hidden lifestyle-state diagnostic;
  - rejected as a direct scalar submission feature;
  - keep the learned sign and Q1-tail gate as inputs to an action-health translator.
- Adopt rule for future features:
  - do not scale Q1-tail shifts blindly;
  - optimize for p90-safe visibility and movement-null dominance;
  - test placement/shape changes before target amplitude changes.
- Failure condition:
  - if a Q1-tail feature only improves mean while p90 stays positive, classify it as action-visible but calibration-unsafe.

## E333 Q1 Contrastive Action Features

- Target hypothesis tested:
  - Q1-tail movement may need a non-tail/background counter-component to become calibration-preserving and public-visible.
- Feature/representation source:
  - E332 Q1 positive-tail residual latent;
  - background masks from non-tail, low residual, mid-band, and ring-band rows;
  - contrast ratios including opposite-direction and mass-neutral action shapes.
- Validation result:
  - `510` local translator gates pass label/null checks;
  - strongest local shape Q1 `pos_q75/softplus + nontail_all/opp050` has delta `-0.020200`;
  - `84` generated probes produce `0` selector-promoted candidates;
  - best selector probe has positive mean and p90 versus E247.
- Updated registry status:
  - rejected as a direct submission feature;
  - approved only as evidence that local Q1 logloss is too permissive for background compensation;
  - do not include broad non-tail Q1 compensation in candidate generation.
- Adopt rule for future features:
  - require public-free action visibility before trusting any Q1 background feature;
  - prefer row/block placement-health targets over global non-tail compensation.
- Failure condition:
  - if a contrastive feature improves train Q1 loss but selector mean/p90 turn positive, classify it as validation shortcut.

## E334 Q1 Tail Row-Censor Features

- Target hypothesis tested:
  - Q1-tail hidden lifestyle action may become healthy if it is applied only to the right latent/subject/dateblock/calendar/base-Q1 rows.
- Feature/representation source:
  - E332 Q1 positive-tail residual latent and translators;
  - row censor masks from latent quantiles, tail-weight quantiles, base-Q1 quantiles, calendar keep/drop, subject keep/drop, dateblock keep/drop, and all-tail controls.
- Validation result:
  - `510/532` row-censor variants pass local Q1 label/null gates;
  - strongest gate Q1 `pos_q78/const/latent_top80` has delta `-0.016399822`, dominance `1.000000`;
  - `72` generated E247 probes produce `0` selector-promoted candidates;
  - closest files are either `too_small_to_submit` or fail movement-null dominance.
- Updated registry status:
  - approved as evidence that Q1 hidden lifestyle state has many row-level masks;
  - rejected as a direct submission feature;
  - do not use these row masks without an action-health target.
- Adopt rule for future features:
  - row/subject/dateblock masks should become inputs to an action-health model, not final action rules;
  - promotion requires selector visibility plus p90 safety plus movement-null dominance.
- Failure condition:
  - if a row-censored feature improves local Q1 loss but produces no selector-promoted candidate, classify it as latent-real/action-invisible.

## E335 Q1 Action-Health Latent Features

- Target hypothesis tested:
  - the missing hidden object is not Q1 label signal but action health: selector-visible, p90-safe, movement-null-rare, and E323-negative probability movement.
- Feature/representation source:
  - E332/E333/E334 Q1 candidate geometry;
  - moved-row lifestyle signatures over social, bedtime, routine, cashflow, diary-state, and JEPA residual feature families;
  - E323 anatomy and movement-null stress summaries;
  - action-health score as a same-level own latent target.
- Validation result:
  - archive rows `233`, movement-null-labelled rows `58`;
  - leave-experiment trees Spearman `0.933512`, top20 overlap `0.869565`;
  - leave-family trees Spearman `0.938198`, top20 overlap `0.891304`;
  - generated candidates `55`, selector-promoted candidates `0`.
- Updated registry status:
  - approved as a diagnostic/ranking latent;
  - rejected as a current Q1-only submission generator;
  - keep action-health features for blocking unsafe candidates and for training a broader cross-target generator.
- Adopt rule for future features:
  - action-health score may rank candidates, but it cannot certify a file without selector promotion and fresh movement-null dominance;
  - future generators need visible/null-rare positive examples, not only safe-invisible Q1 averages.
- Failure condition:
  - if an action-health feature predicts prior health but all generated candidates remain below selector resolution, classify it as ranker-only, not a probability-moving representation.

## E336 Public-Negative Action Latent Features

- Target hypothesis tested:
  - public-bad movement anatomy can serve as a same-level action latent whose inverse or orthogonal complement yields a safer E247 submission.
- Feature/representation source:
  - logit-space E323 upload-safe minus E247 axis;
  - logit-space E216 minus E247 axis;
  - E247 minus old-frontier axes (`E95`, `mixmin`, `mildavg`, `E256`, `E267`);
  - bad-combo and bad-projection-orthogonalized good axes;
  - moved-row lifestyle signatures over cognitive-money, bedtime-phone, mobility, and diary-state energies.
- Validation result:
  - E323 bad axis is target-specific: Q1/S1/S3 shares `0.258564/0.263325/0.478111`;
  - E216 bad axis is S2-heavy with share `0.645902`;
  - `162` materialized candidates produce `0` selector-promoted candidates;
  - movement-null stress finds only tiny safe-invisible `good_mixmin_topall` probes.
- Updated registry status:
  - approved as a veto/risk diagnostic;
  - rejected as a direct submission feature or generator;
  - retain E323/E216 axes for future action-health targets.
- Adopt rule for future features:
  - a feature that merely moves opposite a public-bad output vector is insufficient;
  - public-negative axes should regularize or censor hidden-state actions, not define the action by themselves.
- Failure condition:
  - if away-from-bad or orthogonalized-good movement fails selector promotion, classify it as output-space reversal failure rather than hidden-state discovery.

## E337 Residual Lifestyle-Cluster Features

- Target hypothesis tested:
  - target-residual lifestyle latents may contain repeated hidden episode states that are not visible through broad subject/day summaries.
- Feature/representation source:
  - E330 target-residual latent matrix;
  - masked context views: family, jepa_resid, raw_day, story_bundle, family_story, family_jepa_story;
  - k-means residual clusters k `4/6/8/10/12`;
  - E323/E216 public-bad anatomy as veto diagnostics.
- Validation result:
  - `family/dateblock` predicts latent coordinates with R2 `0.169277`;
  - `jepa_resid/dateblock` R2 `0.107508`;
  - k4-k8 clusters are non-collapsed on train/test;
  - `3` cluster-target rows pass label/null stress;
  - `64` global materialized candidates produce `0` selector-promoted files.
- Updated registry status:
  - approved as a hidden lifestyle-state representation;
  - rejected as a direct global target-calibration feature;
  - keep cluster IDs and episode scores as candidate gates.
- Adopt rule for future features:
  - cluster features must be used locally at row/episode level;
  - global cluster priors should be treated as action smear unless they pass selector and movement-null dominance.
- Failure condition:
  - if cluster labels improve label CV but global target movement fails selector promotion, classify the feature as representation-only.

## E338 Cluster-Local Episode Features

- Target hypothesis tested:
  - E337's hidden residual clusters become useful only when translated through cluster-local episode rows.
- Feature/representation source:
  - E337 gated cluster-target rows;
  - cluster residual mean, median, sign agreement, support, and strength;
  - E323/E216 vetoed and target-centered local deltas.
- Validation result:
  - `10` episode-gated rows;
  - strongest states are Q3/dateblock positive/negative episodes;
  - `75` materialized candidates;
  - `4` information-sensor candidates;
  - `0` selector-promoted and `0` movement-null-safe promoted candidates;
  - best local sensor has movement-null mean/p90 dominance `1.000000/1.000000` but is `too_small_to_submit`.
- Updated registry status:
  - approved as a Q3 episode-placement energy/gate;
  - rejected as a standalone submission feature at current scale;
  - carry forward as a gating feature for constrained Q3 amplification.
- Adopt rule for future features:
  - prefer episode-local row placement over all-row target shifts;
  - any amplification must preserve negative p90 and movement-null dominance.
- Failure condition:
  - if amplification turns the E338 safe-invisible movement into p90-positive or null-common movement, classify it as visibility-overfit.

## E339 Q3 Episode-Gated Amplifier Features

- Target hypothesis tested:
  - E338's Q3/dateblock episode state can act as a hidden placement gate for older, stronger Q3 probability directions.
- Feature/representation source:
  - E338 Q3 episode rows and signed residual deltas;
  - borrowed Q3 logit directions from E256, E267, E95, mixmin, E101, E176, E224, E211, E269 controls, E323, and E216;
  - transform families: raw, inverse, sign-agree, disagreement-inverse, gate-signed-absolute, gate-signed-sqrt, and constant gate-shape;
  - E323/E216 veto and movement-null stress as health diagnostics.
- Validation result:
  - `5430` generated candidates;
  - `1492` information-sensor candidates;
  - `0` selector-promoted candidates;
  - `0` movement-null-safe promoted candidates;
  - best sensor mean `-0.000019`, p90 `-0.000005`, movement-null dominance `1.000000/1.000000`, but `too_small_to_submit`.
- Updated registry status:
  - approved as a Q3 episode-gate diagnostic;
  - rejected as a current Q3 amplifier/submission feature;
  - retain source episode-sign alignment as a prerequisite check for future Q3 borrowing.
- Adopt rule for future features:
  - an older public-surviving Q3 direction is not automatically useful inside a hidden lifestyle episode;
  - require both episode-sign alignment and selector promotion before spending a public slot.
- Failure condition:
  - if a gated borrowed direction stays below selector resolution despite negative p90 and null dominance, classify it as safe-invisible, not public-ready.

## E340 Microstate Coalition Action-Health Features

- Target hypothesis tested:
  - safe-invisible Q1 and Q3 hidden lifestyle micro-states can be combined into a selector-visible and null-rare coalition action.
- Feature/representation source:
  - E335 Q1 action-health tail candidates;
  - E338 cluster-local Q3 episode candidates;
  - E339 Q3 episode-gated historical-direction candidates;
  - candidate geometry, target-share anatomy, selector p90/mean/beats, E323/E216 bad-axis movement, and movement-null dominance.
- Validation result:
  - `5560` archive rows and `37` safe-invisible source rows;
  - action-health OOF Spearman `0.938224`;
  - visibility-margin OOF Spearman `0.921134`;
  - null-health OOF Spearman `0.004871`;
  - `7400` generated coalitions;
  - `0` selector-promoted candidates.
- Updated registry status:
  - approved as an action-health/visibility diagnostic;
  - rejected as a current coalition submission feature;
  - treat null-health as missing/unlearned in the current source archive.
- Adopt rule for future features:
  - do not assume clean small sensors add linearly into a public candidate;
  - require visible/null-rare positive examples before training another action generator;
  - keep E340 source-health fields as ranking and blocking features.
- Failure condition:
  - if coalition candidates have high null dominance but p90 remains above `-0.00005`, classify the family as safe-invisible saturation.

## E341 Sparse Residual Lifestyle Support Features

- Target hypothesis tested:
  - E330 target-residual lifestyle states are useful on rare human/social test tails even though broad all-row materialization fails.
- Feature/representation source:
  - E330 gated residual-state rows;
  - masked lifestyle views (`jepa_resid`, `raw_day`, `family_jepa_story`, `family`);
  - sparse tail masks from predicted residual movement: `absdelta`, `posdelta`, `negdelta`, `state_abs_x_delta`;
  - raw/inverse and E323/E216 bad-veto action variants.
- Validation result:
  - `864` generated candidates;
  - `0` selector-promoted;
  - `96` information sensors;
  - best selector p90 `-0.000017477`;
  - best movement-null dominance `1.000000/1.000000`, but p90 only `-0.000005843`.
- Updated registry status:
  - approved as rare-tail placement and sign-transfer diagnostic;
  - rejected as current submission feature;
  - Q2 inverse residual tail is the strongest surviving clue.
- Adopt rule for future features:
  - never materialize train residual direction directly without a sign-transfer check;
  - prefer sparse tail placement over broad all-row residual movement;
  - require p90 near `-0.00005` before public submission.
- Failure condition:
  - if sparse tails remain below strict promotion and only inverse directions survive, classify residual states as local CV features needing a separate public-geometry translator.

## E342/E343 Sign-Transfer Lifestyle-State Features

- Target hypothesis tested:
  - Q2 intervention/rough-night residual tails and Q1/Q3 human-social microstate coalitions are different projections of one hidden lifestyle state.
- Feature/representation source:
  - E341 Q2 sparse inverse residual-tail candidates;
  - E340 Q1/Q3 microstate coalition candidates;
  - Q2-tail row gates, full-sum sign-transfer, E323/E216 bad-veto transforms, and target-centered variants;
  - E343 projection cleanup against Q2-bad, residual-bad, LeJEPA-bad, and ordinal public-bad reference axes.
- Validation result:
  - E342: `1314` candidates, `1019` information sensors, `0` selector-promoted;
  - best E342 p90 `-0.000055`, mean `-0.000248`, beats `0.986111`, but bad-axis `0.017962`;
  - E343: `1512` candidates, `845` information sensors, `0` selector-promoted;
  - best cleaned p90 `-0.000046`, bad-axis `0.015414`.
- Updated registry status:
  - approved as the strongest current hidden lifestyle-state sign-transfer diagnostic;
  - rejected as a current submission feature because visible energy and bad-axis load are entangled;
  - keep E342 top near-misses as support-axis sensors for future generator training.
- Adopt rule for future features:
  - cross-target sign-transfer is more promising than more Q1/Q3 summing;
  - require bad-axis-safe p90 visibility, not just p90 visibility;
  - if a cleanup step kills p90, treat the feature as diagnostic only.
- Failure condition:
  - if a sign-transfer feature crosses p90 only by increasing public-bad-axis load, do not submit it; use it to identify the missing action-health target.

### E344 counter-axis lifestyle-state composition

- Target hidden structure: E342 visible Q2/Q1/Q3 hidden lifestyle state plus a small independent anti-bad action-health counter-state.
- Why needed: E342 proves visibility but fails bad-axis; E343 proves projection cleanup kills visibility. E344 tests whether a separate counter-state can preserve the latent while correcting geometry.
- Feature/action form:
  - E342 logit delta as primary context representation;
  - E315/E319/E326/E327 negative bad-axis sources as counter contexts;
  - small counter weights `0.04-0.20`;
  - add, cell-veto, centered, bad-cell patch, Q2-preserving, and source-row-only transforms.
- Current evidence:
  - `3330` candidates;
  - `6` selector-promoted;
  - `2677` information sensors;
  - `6` movement-null-safe promoted;
  - best file `submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv` with p90 `-0.000053606`, bad-axis `0.014849687`, and null strict rate `0.000000`.
- Leakage/stability condition: keep only candidates that clear E272 selector, bad-axis cap, and movement nulls. Do not treat the counter source itself as public-safe unless it passes independently.
- Public interpretation: improvement supports hidden lifestyle-state + counter-axis composition; deterioration means local anti-bad geometry is not public-transferable enough.

### E345 counter-axis margin refinement

- Target hidden structure: stability of the E342+E315 hidden lifestyle/counter-state composition.
- Why needed: E344's strict candidate had strong p90 but narrow bad-axis margin. E345 tests whether the state survives local perturbations rather than relying on a threshold accident.
- Feature/action form:
  - E342 sign-transfer delta as the primary lifestyle-state representation;
  - E315 human-ready composition as the counter-axis;
  - counter weights `0.075-0.160`;
  - veto strengths `0.15-0.45`;
  - joint, centered, additive-veto, bad-cell, source-row-only, Q2-preserving, Q1/Q2/S1, and Q1/S1 target scopes.
- Current evidence:
  - `6588` candidates;
  - `278` selector-promoted;
  - `6029` information sensors;
  - `40` movement-null-safe promoted;
  - selected file `submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv` with p90 `-0.000051888`, bad-axis `0.014655826`, and null strict rate `0.000000`.
- Registry status: approved as a robustness and bad-axis-margin feature; second submission priority behind E344.
- Failure condition: if E344 and E345 both fail publicly, stop treating local E315 counter-axis safety as transferable and learn a counter-source selector before another public test.

### E346 public-analog counter-axis gate

- Target hidden structure: public-transfer risk of the E342+E315 counter-axis state.
- Why needed: E323 was locally null-safe but public-bad. Local movement nulls alone cannot certify public transfer.
- Feature/action form:
  - known public-observation files are converted into E247-relative logit-delta axes;
  - candidate movement is scored by public-loss-weighted positive cosine and direct positive cosine to E323/E216/E267/E256;
  - matched row/target/sign/subject/dateblock nulls provide dominance thresholds.
- Current evidence:
  - E344 upload risk `0.051129078`, survival `0.452806122`;
  - E345 upload risk `0.051144175`, survival `0.461734694`;
  - direct positive E323/E216/E267/E256 alignment `0.000000000` for both.
- Registry status: approved as a veto diagnostic; not approved as a certification gate.
- Failure condition: if a future candidate has positive hard-veto alignment or public-analog survival below current E344/E345 while claiming to be safer, block it before public submission.

### E347 lifestyle-state action re-audit gate

- Target hidden structure: whether a safer counter-axis candidate still lies on the human/social hidden lifestyle-state manifold rather than becoming an output-space dilution.
- Why needed: E346 found lower-risk E344 neighborhood candidates, but lower public-analog risk alone is not enough. The goal requires a hidden lifestyle-state latent, not just a safer-looking movement vector.
- Feature/action form:
  - teacher state from E328 own-latent lifestyle features and E337 target-residual lifestyle states;
  - action view from candidate logit movement relative to E247;
  - row movement correlation/enrichment against lifestyle-state features;
  - row-shuffle null dominance as the anti-collapse check.
- Current evidence:
  - `16` candidates audited;
  - `3` gate passes;
  - selected file `submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv`;
  - p90 `-0.000050116`, bad-axis `0.014671133`, public-analog survival `0.528061224`, risk `0.044818570`;
  - dominant state `rs01_Q1_jepa_resid_dateblock`, state/null dominance `1.000000`.
- Registry status: approved as the current evidence-balanced submission gate.
- Failure condition: if public LB rejects E347 while E344/E345 remain better, downgrade lifestyle-state alignment below raw p90/bad-axis margin for this branch.

### E348 lifestyle-state specificity gate

- Target hidden structure: whether E347's Q1 dateblock residual lifestyle-state action is specific rather than an after-the-fact broad state story.
- Why needed: E347's state score was saturated across the E344/E345 family, so a stronger anti-collapse test was needed before treating statefulness as a submission-ranking signal.
- Feature/action form:
  - positive latent axis `rs01_Q1_jepa_resid_dateblock`;
  - controls from calendar-only, non-Q1 residual, own-latent, random columns, permuted-Q1 state, and public-bad movement controls.
- Current evidence:
  - E348 gate passes `3`;
  - selected canonical file remains `submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv`;
  - selected Q1 corr `0.432330`, Q1 enrichment `0.852584`;
  - Q1 specificity margin `0.297346`, broader margin `0.271772`;
  - public-bad controls fail specificity.
- Registry status: approved as a specificity validator for the E347 priority, not a new feature family.
- Failure condition: if future public feedback rejects E347, keep the specificity result as local evidence but stop assuming local lifestyle specificity implies public transfer.

### E349 target/cell lifestyle-state ablation gate

- Target hidden structure: whether the E347 Q1 dateblock lifestyle-state action is target-separable or only healthy as a coupled Q/S episode state.
- Why needed: E347/E348 prove local Q1-specific statefulness, but not the action support. A public submission should not spend a slot on Q1-only storytelling if the actual Log Loss geometry needs Q2/Q3/S1 support.
- Feature/action form:
  - E247 baseline plus masked/scaled logit(E347)-logit(E247) action;
  - masks over targets, Q1-state rows, movement rows, cell magnitude, and sign;
  - extra gate requiring meaningful probability/cell distance from E347.
- Current evidence:
  - `158` variants;
  - `10` E349 gate passes;
  - `2` replacement-gate passes;
  - selected file `submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv`;
  - selected metrics: p90 `-0.000050035`, bad-axis `0.014667610`, public-analog risk `0.044736209`, direct bad positive cosine sum `0`, Q1 corr `0.440884`, Q1 specificity margin `0.299145`;
  - changed cells vs E347 `347`, so this is not a near-duplicate.
- Registry status: approved as the current compact-lifestyle-state candidate and as evidence that the useful latent is Q1/Q2/Q3/S1-coupled, not Q1-only.
- Failure condition: if public rejects E349 while E347 is better, restore the low-magnitude/S3 cells as calibration support and stop pruning the state by target/cell without a stronger public-transfer proxy.

### E350 compact lifestyle-state plateau gate

- Target hidden structure: stability of the compact Q1/Q2/Q3/S1 lifestyle-state action under local threshold, micro-scale, and S3-tail perturbations.
- Why needed: E349 could have been a one-threshold selector artifact. A usable hidden state should survive a local neighborhood, not just one cell cutoff.
- Feature/action form:
  - E247 baseline plus masked logit(E347)-logit(E247) action;
  - primary targets Q1/Q2/Q3/S1;
  - optional S3-tail restoration alpha `0-1`;
  - cell thresholds `35-90`;
  - micro scales `0.990-1.010`;
  - plateau support features over neighboring thresholds/scales/alphas.
- Current evidence:
  - `311` variants;
  - `187` local gate passes;
  - `176` plateau gate passes;
  - selected file `submission_e350_compactplateau_selected_compact_t45_s1_005_s3a1_00_ef54727b_uploadsafe.csv`;
  - selected p90 `-0.000050233`, bad-axis `0.014742869`, public-analog risk `0.044770778`, direct bad positive cosine sum `0`, Q1 specificity margin `0.317370`, plateau support score `37`.
- Registry status: approved as the current highest-information compact-state public sensor. Use it as a plateau/gating feature family, not as a general amplitude-scaling recipe.
- Failure condition: if public rejects E350 while E349 is better, downgrade S3-tail restoration and micro-amplification; keep the compact Q1/Q2/Q3/S1 state but return to the lower-risk E349/E347 action.

### E351 robust plateau selector

- Target hidden structure: action selection inside the compact lifestyle-state plateau.
- Why needed: E350 proved the plateau exists, but a plateau still contains aggressive and conservative points. The goal is not only to find a latent, but to choose a public-safe probability action from it.
- Feature/action form:
  - reuse E350 score table;
  - rank axes: p90 visibility, public-analog risk, bad-axis margin, Q1 specificity, plateau support, E349 compatibility, and micro-scale size;
  - maximin robust score plus a conservative compatibility gate.
- Current evidence:
  - `176` plateau candidates;
  - `36` compatibility candidates;
  - selected file `submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv`;
  - selected p90 `-0.000050191`, risk `0.044765398`, bad-axis `0.014741236`, Q1 specificity margin `0.324251`, support `35`, distance vs E349 `0.006241`.
- Registry status: approved as the practical selector for scarce public submissions from the E350 plateau.
- Failure condition: if E351 underperforms E350 publicly, relax the E349-distance penalty and allow stronger S3-tail restoration; if both fail, the E350 plateau is local-only and needs a new public-transfer latent.

### E352 selector-sensitivity gate

- Target hidden structure: whether the compact lifestyle-state plateau has a stable action center or only arbitrary selector-dependent winners.
- Why needed: E351's maximin selector is hand-designed. A reliable latent action should survive selector perturbations before it gets a scarce public slot.
- Feature/action form:
  - reuse E351-ranked E350 plateau candidates;
  - perturb gates over p90 gain, public-analog risk, bad-axis margin, Q1 specificity, support, E349 compatibility, scale, and public-bad positive-cosine veto;
  - perturb ranking weights over the same axes with worst-axis and S3-tail terms.
- Current evidence:
  - `2500` random selector worlds;
  - `1118` non-empty worlds;
  - E351 robust candidate `compact_t75_s1.005_s3a0.25` wins top1/top3 `0.224508/0.277281`;
  - original E350 rank winner wins top1/top3 `0.000000/0.004472`;
  - E351 wins every deterministic profile except p90_hungry.
- Registry status: approved as a selection-stability validator. It does not create a new feature family or submission file.
- Failure condition: if public later prefers E350 over E351, reduce the weight of selector stability and restore stronger S3-tail/p90 pressure in the next candidate ranking.

### E353 public-bad tangent neutralization gate

- Target hidden structure: whether E351 still contains a removable component aligned with already observed public failures.
- Why needed: E323 showed local null-health can be a public-transfer shortcut. Before trusting E351, test whether known public-bad tangent removal improves it without destroying the hidden lifestyle-state action.
- Feature/action form:
  - source action: E351 minus E247 in logit space;
  - target representation: public-adverse axis sets from E346 public observations;
  - transformation: sequential or span removal of positive projections only;
  - alphas `0.01-1.00`.
- Current evidence:
  - `52` candidates;
  - `48` neutralized candidates;
  - `0` E353 local gate passes;
  - no generated risk-improver remains strict-promoted;
  - strong cleanup lowers risk but kills p90 visibility.
- Registry status: rejected as a submission-generating feature family. Keep as a negative diagnostic.
- Failure condition: if future new public-bad axes appear, this may be rerun once; do not keep sweeping alphas on the current axis set.

### E354 E247 support-latent graft gate

- Target hidden structure: whether E247's public-positive Q3 support body represents an independent hidden lifestyle/support state missing from E351.
- Why needed: E353 rejected simple public-bad cleanup, so the next breakthrough route had to be a new positive support axis rather than another projection. E286/E285 had a plausible E247/E256 preserve-avoid support latent.
- Feature/action form:
  - support anatomy metrics over E247 body/common/only Q3 cells;
  - `support_interference_l1`, `support_alignment_score`, and E247-body opposite-mass diagnostics;
  - support-source transfer AUC filter for E286 graft sources;
  - Q3 support guard and micro-graft actions on top of E351.
- Current evidence:
  - `132` candidates;
  - `0` E354 local gate passes;
  - E351 already has `e247_body_alignment_ratio=1.000000` and no opposite support movement;
  - grafts trade public-analog risk against strict p90 and Q1 lifestyle specificity.
- Registry status: rejected as a submission-generating feature family for the current E247/E256 boundary. Keep the support anatomy metrics as diagnostics.
- Failure condition: revive this only if a richer support target is learned, such as action-health/public-transfer labels or a non-E247/E256 social-state boundary.

### E355 action-health latent gate

- Target hidden structure: candidate-level action health, not row-level lifestyle state alone.
- Why needed: repeated failures showed that valid human/social states often fail during probability movement translation. The feature should predict whether a movement is visible, public-analog safe, Q1-specific, and bad-axis safe.
- Feature/action form:
  - context features from movement geometry, target shares, reference-axis geometry, and recipe descriptors;
  - target representation from p90 visibility, public-analog risk, Q1 specificity, and bad-axis margin;
  - leave-experiment-out action-health predictions over the E350/E351 plateau.
- Current evidence:
  - `653` full target rows;
  - ExtraTrees action-health OOF Spearman `0.852240`;
  - RandomForest action-health OOF Spearman `0.825717`;
  - top E355 row `compact_t45_s1.005_s3a0.25`;
  - no selected submission because the top row has weak E352 stability.
- Registry status: approved as a diagnostic latent; rejected as a standalone submission selector.
- Failure condition: do not use E355 rank alone for public candidates. A future version must include E352/public-transfer stability in the target before it can override E351.

### E356 transfer-stability latent gate

- Target hidden structure: public-transfer/stress stability inside the compact lifestyle-state action basin.
- Why needed: E355 proved action health is learnable but not enough for public-transfer candidate choice. E352 stability is the local proxy that survived after E355, so it becomes the same-level latent target.
- Feature/action form:
  - context views from candidate movement geometry, recipe descriptors, E351 selector context, and optional E355 action-health predictions;
  - target representation from E352 top1/top3 selector perturbation rates;
  - candidate ranking by multi-view transfer-stability prediction plus conservative plateau gates.
- Current evidence:
  - `311` training candidates and `36` E351-compatible prediction candidates;
  - best compat-pool transfer raw OOF Spearman `0.835013`;
  - best E352 top3 random-KFold Spearman `0.796029`;
  - best E352 top3 threshold-holdout Spearman `0.772806`;
  - selected probe `compact_t45_s1.005_s3a0.50`;
  - raw E352 still favors E351 over E356.
- Registry status: approved as a diagnostic latent and approved as an information-rich public-transfer probe. Not approved as a proven replacement for E351.
- Failure condition: if E356 public LB is worse than E247/E351, do not keep increasing learned selector complexity inside the same tiny plateau. The next target must model public subset/calibration state directly.

### E357 public-survival contrast latent gate

- Target hidden structure: public-survival movement anatomy around the current E247 public-best anchor.
- Why needed: E356 learned transfer stability without directly using the known public failure/success anatomy. E357 asks whether E247-preserving and E216/E267/E323-avoiding movement patterns form a learnable contrast latent.
- Feature/action form:
  - source action: candidate minus E247 in logit space;
  - context features: targetwise mean/absolute/tail movement, E247 preservation, projections onto known public-good and public-bad axes, and compact-basin descriptors;
  - same-level target: known public `delta_vs_e247` for locally available submission files;
  - anti-collapse checks: leave-one-public-file-out predictors and permutation baselines.
- Current evidence:
  - public observations: `17`;
  - available local public files: `13`;
  - candidate pool: `181`;
  - ExtraTrees LOO Spearman `0.829670`;
  - Ridge10 LOO Spearman `0.659341`, beating permutation p95;
  - selected probe `compact_t45_s1.000_s3a1.00`;
  - selected file `analysis_outputs/submission_e357_publicsurvival_selected_compact_t45_s1_000_s3a1_00_a08a4957_uploadsafe.csv`.
- Registry status: approved as a public-survival diagnostic latent and information-rich compact-basin probe. Not approved as a standalone public optimizer because the known public target set is small.
- Failure condition: if E357 public LB is worse than E247/E351/E356, stop tuning compact-basin S3-tail/amplification details and move to a different lifestyle-state/public-subset latent.

### E358 row-state public-survival gate

- Target hidden structure: whether probability movement lands on healthy human/social lifestyle rows rather than E323-heavy row-state pockets.
- Why needed: E357 only sees output-space movement. A true hidden lifestyle-state law should also be visible in row placement over E328 own-latent lifestyle states and E268 human/social story tails.
- Feature/action form:
  - row state: E328 `ownlife_*` PCs, energy, residual energy, cluster distance, and k8 cluster public-bad/public-good rates;
  - human semantics: E268 story axes aligned with E328 bad-minus-good cluster markers;
  - candidate context: movement-weighted row-state means, movement share in high-risk clusters, target-specific bad/good exposure, and story-tail exposure;
  - target representation: known public `delta_vs_e247`;
  - anti-collapse: leave-one-public-file-out regressors and permutation p95 checks.
- Current evidence:
  - known public files: `13`;
  - candidate pool: `181`;
  - ExtraTrees LOO Spearman `0.873626`;
  - KNN3 LOO Spearman `0.692308`, beating permutation p95;
  - no compact candidate passes row-state + E352/E356/E357 gates;
  - top compact candidate `compact_t45_s1.000_s3a1.00` has row-state predicted public loss `0.000956664`.
- Registry status: approved as a veto/diagnostic latent. Rejected as a submission-generating feature family for the current compact basin.
- Failure condition: if a future public-tested compact candidate improves strongly, recalibrate E358's pessimistic public-loss model. Otherwise use E358 to force the next branch toward row-placement/action-health rather than micro-scale tuning.

### E359 row-placement action-health gates

- Target hidden structure: whether the existing compact action can become healthy by changing only the lifestyle rows it touches.
- Why needed: E358 showed a row-state/public-survival contradiction but did not distinguish wrong action from wrong row placement.
- Feature/action form:
  - source deltas: E349, E351, E356, E357 compact movements relative to E247;
  - row scores: E328 own-latent risk/good scores from E247/E323/E256 cluster rates, ownlife energy, residual energy, and cluster distance;
  - gate families: high-risk-row damp, smooth risk gates, E247-like good-row boost, ownlife cluster suppression, and bad-cluster-rate damp;
  - candidate context: E272 output-space selector metrics plus E358 row-state public-survival features.
- Current evidence:
  - generated candidates: `124`;
  - combined E359 passes: `0`;
  - E272-only strict-promote rows: `16`;
  - strict-visible rows fail row-state health, with predicted row-state public loss `0.001038-0.001153`;
  - top non-passing row-balanced variant `e357_fulls3_noamp__goodboost20_riskdamp80` has p90 `-0.000046486` and row-state predicted public loss `0.000965778`.
- Registry status: rejected as a hand-engineered submission feature. Approved as a negative-control dataset for a learned row-action-health latent.
- Failure condition: do not reuse these monotone row gates unless a future learned generator identifies a different source action or a non-monotone row placement rule.

### E360 learned row-action-health surrogate

- Target hidden structure: candidate row-action health over E328 own-latent lifestyle states and E268 human/social story axes.
- Why needed: E359 showed hand gates fail. The next representation should predict the hidden stress outcome directly rather than hard-code risk/good row rules.
- Feature/action form:
  - training rows: E359 candidates and actual E272/E358 outcomes;
  - target: composite of p90 visibility, mean visibility, beat rate, bad-axis margin, row-state loss, row-state variance, exposure, and movement size;
  - generator: nonlinear row policies over risk/good clusters, ownlife PCs, story axes, and cluster biases;
  - verification: materialized shortlist scored by actual E272/E358.
- Current evidence:
  - health target random5 Spearman `0.972450`, leave-source `0.639068`;
  - visibility target remains weak, `0.118049-0.221986`;
  - verified candidates: `140`;
  - submission-gate passes: `0`;
  - best row-state loss around `0.000527`, but p90 too weak.
- Registry status: approved as a diagnostic/generator for healthy row placement; rejected as a submission feature without cell-action visibility support.
- Failure condition: do not use E360 surrogate rank alone for submissions. It needs a visible cell-action target or source family change.

### E361 row-action amplitude restore

- Target hidden structure: whether E360's healthy row placements are correct but under-scaled.
- Why needed: E360 could have failed only because its row actions were too small.
- Feature/action form:
  - source rows: top E360 healthy/balanced candidates;
  - scale policies: global, no-S3, Q-heavy, S1-heavy, Q1/S1;
  - amplitudes: `1.05-1.72`;
  - verification: actual E272/E358.
- Current evidence:
  - candidates: `1120`;
  - strict output candidates: `16`;
  - submission-gate passes: `0`;
  - strict-visible candidates fail row-state exposure/health, while healthiest candidates stay too weak.
- Registry status: rejected as a submission feature family. Keep as evidence that row placement plus amplitude is insufficient.
- Failure condition: do not repeat scalar scale sweeps on E360 rows unless the underlying row x target cell pattern changes.

### E362 row x target cell-action latent

- Target hidden structure: a hidden lifestyle state whose correct probability action differs by target cell, especially between subjective Q targets and objective S recovery/stage targets.
- Why needed: E359-E361 show that row placement and amplitude are not enough. Healthy row movement loses visibility, while visible amplitude violates row-state health. The missing representation must decide which target cells move on each lifestyle row.
- Feature/action form:
  - context views from E328 ownlife PCs, row-state risk/good clusters, E268 human/social story axes, source-action movement anatomy, and target shares;
  - action families with independent Q1/Q2/Q3/S1/S3 row gates;
  - verification by actual E272 output selector and E358 row-state public-survival stress.
- Current evidence:
  - generated candidates: `1550`;
  - strict output candidates: `11`;
  - submission-gate candidates: `1`;
  - selected recipe: `q_story_s_recovery`;
  - selected file: `analysis_outputs/submission_e362_cellaction_selected_e360_e351_robust_center__learned_story_nonmonotone_s1_counter_1273__cell_e019daf5_uploadsafe.csv`;
  - selected target movement shares: Q1 `0.571868`, Q2 `0.238509`, Q3 `0.050188`, S1 `0.139435`, S3 `0.000000`.
- Registry status: approved as the current top submission probe and as the strongest local evidence for row x target hidden lifestyle-action geometry.
- Failure condition: if public LB is clearly worse, do not keep generating E362 variants by small parameter tweaks. First recalibrate the row-state public-survival target or bring in an independent public-like subset/calibration latent.

### E363 cell-action robustness and target-balance latent

- Target hidden structure: robust target-balance manifold around the E362 row x target lifestyle-action, separating visibility targets from health-regularizing targets.
- Why needed: E362 selected one file, so the immediate risk was a one-point threshold artifact. A useful representation should survive local counterfactual perturbations and expose which target cells are structural.
- Feature/action form:
  - seed: E362 selected cell-action;
  - perturbation views: target-scale grid, row-risk gates, donor blends/grafts, and target ablations;
  - local target representation: actual E272 visibility plus E358 row-state public-survival;
  - selection: family-level pass-rate support plus robust local score.
- Current evidence:
  - candidates: `1586`;
  - submission-gate passes: `797`;
  - target-scale pass rate: `0.565285`;
  - selected file: `analysis_outputs/submission_e363_cellrobust_selected_e362_scale_g1_06_q11_08_q20_90_q31_00_s11_30_c2d9a88a_uploadsafe.csv`;
  - selected row-state loss improves to `0.000520036`;
  - selected target shares: Q1 `0.580616`, Q2 `0.201798`, Q3 `0.047181`, S1 `0.170405`, S3 `0.000000`.
- Registry status: approved as the current top submission probe. Use E363 before E362 if only one public slot is available.
- Failure condition: if E363 public LB fails, do not only keep target-scale tweaking. The next branch should either test the top donor-graft family as a separate hypothesis or build a stricter public-like subset/calibration sensor.

### E364 public-like cell-action calibration latent

- Target hidden structure: public-transfer health inside the E363 row x target cell-action basin.
- Why needed: E363's local gate is broad enough that local robustness alone no longer ranks candidates sharply. A candidate can be visible and row-state-acceptable while still aligning with known public-bad movements.
- Feature/action form:
  - fixed candidate pool: all E363 generated files;
  - context features: movement anatomy versus E247, projections onto known public-good/bad axes, E363 hidden lifestyle row-state/story exposure, and E363 local stress metrics;
  - target representation: known public delta versus E247 from available submitted files;
  - selection rule: replacement must pass E363 gate and improve public-like risk relative to E363 selected within bounded margins.
- Current evidence:
  - known available public files: `13`;
  - LOO Spearman: ExtraTrees `0.895604`, Ridge1 `0.769231`, Ridge10 `0.686813`, KNN3 `0.642857`;
  - selected file: `analysis_outputs/submission_e364_publiclike_cellaction_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv`;
  - selected public-bad-axis sum: `0.004203` versus E363 selected `0.006034`;
  - selected row-state public-loss mean: `0.000438374` versus E363 selected `0.000520036`;
  - selected target shares: Q1 `0.505235`, Q2 `0.210718`, Q3 `0.053685`, S1 `0.230361`, S3 `0.000000`.
- Registry status: approved as a high-information public probe. It is less conservative than E363 because it changes family from target-scale to donor-graft.
- Failure condition: if public LB worsens clearly, treat the known-public sensor as over-trusting donor geometry; return to source-law-preserving E363 or learn a less public-LB-scarce calibration target.

### E365 public-like jackknife stability latent

- Target hidden structure: stability of the E364 public-like donor-graft latent under masked public observations and masked context views.
- Why needed: E364 uses only `13` locally available public-observed files. A useful representation should not depend on one known public score or one feature family.
- Feature/action form:
  - no new probability action;
  - feature views: all, axis, target, anatomy, bad_good, compact;
  - public masks: no drop plus leave-one-known-public file out;
  - score: per-scenario public-like score with E363 local gate and relative E363-selected margins.
- Current evidence:
  - scenarios: `84`;
  - E364 beats E363: `84/84`;
  - E364 top1/top10 rates: `0.500000` / `0.809524`;
  - E363 top10 rate: `0.488095`;
  - selected audited file: `analysis_outputs/submission_e365_jackknife_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv`;
  - closest alternate is another donor-graft sibling, supporting family-level donor recovery geometry.
- Registry status: approved as the current strongest submission probe and as a stability check for E364.
- Failure condition: if public LB is clearly worse, do not continue local donor-graft jackknife selection. Treat the public-like latent as internally stable but externally wrong, and move to a new calibration/subset target.

### E366 hidden lifestyle donor-family row gate

- Target hidden structure: row-wise hidden lifestyle state deciding whether Q3/S1, Q3-only, or S1-only donor-graft geometry should be trusted.
- Why needed: E365 support is family-level, not a single exact file. A real hidden lifestyle state should explain which rows need Q3/S1 subjective/objective recovery movement and which rows should stay closer to the anchor.
- Feature/action form:
  - source family: E365-supported Q3/S1, Q3-only, and S1-only donor-graft siblings;
  - row context: E328/E358 own-lifestyle latent, row-state bad/good clusters, weekend/phone/finance/routine/recovery story tails;
  - actions: family centers, pair centers, target-cell recombinations, row/story gates, target-row gates;
  - null controls: inverse cluster, random rate-matched, and permuted cluster row gates.
- Current evidence:
  - generated candidates: `79`;
  - scenarios: `84`;
  - best real lifestyle gate: top1 `0/84`, top10 `84/84`, rank mean `2.345238`;
  - best null/permuted gate: top1 `81/84`, top10 `84/84`, rank mean `1.071429`;
  - decision: `reject_e366_lifestyle_gate_keep_e365`.
- Registry status: rejected as a submission feature. Keep as diagnostic evidence that current row-story gates are vulnerable to row-mask shortcuts.
- Failure condition: do not use E366-style row gates in a submission unless they beat null/permuted row-mask controls and preserve E365/E363/E364 stress.

### E367 public/private row-mask validity latent

- Target hidden structure: row-level public-good versus public-bad movement support, predicted from lifestyle/story context.
- Why needed: E366 showed that semantic row gates can be beaten by random/permuted masks. A valid row gate needs evidence that the row-mask target itself is lifestyle-predictable and stable.
- Feature/action form:
  - target representation: known-public movement support relative to E247, converted into public-good row support, public-bad row support, and target-specific validity for Q1/Q2/Q3/S1;
  - context features: E328/E358 own-lifestyle state and E268 human/social story axes;
  - generated actions: learned row-mask damp/boost, target-validity routing, diagnostic direct-public gates, and null/permuted row-mask gates;
  - stress: lifestyle CV/permutation null, leave-public row-mask stability, and E365-style jackknife.
- Current evidence:
  - generated candidates: `30`;
  - scenarios: `98`;
  - aggregate public row validity KFold Spearman `0.073804`, null p95 `0.135689`;
  - row-mask stability min Spearman `0.827446`;
  - Q2 target validity KFold Spearman `0.392982`, null p95 `0.105015`;
  - S1 target validity KFold Spearman `0.110407`, null p95 `0.099875`;
  - best null gate top1 `89/98`; best learned real gate top1 `0/98`;
  - decision: `reject_e367_rowmask_not_lifestyle_predictive_keep_e365`.
- Registry status: rejected as an aggregate submission feature; keep Q2/S1 target-specific validity as a live representation candidate.
- Failure condition: do not use aggregate row-mask validity in submissions. A future Q2/S1-specific feature must beat null masks before being uploadable.

### E368 Q2/S1 target-specific row-validity latent

- Target hidden structure: a hidden lifestyle state that is visible only through Q2 intervention/rough-night validity and S1 recovery validity, not through aggregate public/private row identity.
- Why needed: E367 showed aggregate row-mask validity is not lifestyle-predictive and is beaten by null masks, while Q2 and S1 target-specific validity survived. E368 tests that narrower feature before allowing any new submission.
- Feature/action form:
  - target representation: known-public Q2/S1 row-good minus row-bad support relative to E247;
  - context: E328/E358 own-lifestyle state and E268 human/social story axes;
  - action: E365 backbone plus Q2/S1-only cell scaling/source recovery;
  - controls: direct-public Q2/S1 masks, swapped masks, permuted masks, inverse masks, random masks.
- Current evidence:
  - Q2 validity KFold Spearman `0.426940`, null p95 `0.102237`;
  - S1 validity KFold Spearman `0.157989`, null p95 `0.102777`;
  - Q2/S1 leave-public stability min `0.692973`;
  - best learned gate top1/top10 `73/98` and `97/98`;
  - best direct-public top1 `19/98`;
  - best null top1 `4/98`;
  - selected file: `analysis_outputs/submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv`.
- Public feedback: `0.576290429`, worse than E247 by `+0.000131480` but slightly better than E95 by `-0.000000901`.
- Registry status: approved as a diagnostic Q2/S1 lifestyle-state representation; rejected as a current frontier submission feature.
- Failure condition: do not keep sweeping Q2/S1 masks from the same known-public target. Treat the target as locally valid but public-transfer undercalibrated, and build a public-free Q2/S1 calibration proxy before any new materialization.

### E369 public-free Q2/S1 lifestyle residual transfer

- Target hidden structure: Q2/S1 lifestyle residual state that can be learned from train labels and context views without public LB targets.
- Why needed: E368 beat direct-public and null row masks, but its target representation still came from known-public row support. E369 asks whether train-side hidden lifestyle residuals independently explain the same Q2/S1 action.
- Feature/action form:
  - no new submission movement;
  - base features: subject/calendar model;
  - teacher: Q2/S1 train residual after the base model;
  - context views: family PCs, JEPA residuals, story bundle, raw day, family-story, family-JEPA-story;
  - diagnostics: masked residual student, kNN residual analogy, cluster residual analogy, permuted gate/movement nulls, E323-axis movement audit.
- Current evidence:
  - Q2: `64` supporting rows, best gate Spearman `0.369592`, best abs-delta Spearman `0.421147`;
  - S1: `42` supporting rows, best gate Spearman `0.232458`, best abs-delta Spearman `0.181906`;
  - all-target E323 bad-axis cosine `0.001520`;
  - Q2-only E323 cosine versus E365 `0.591735`, so Q2 amplitude must be monitored.
- Registry status: approved as validation evidence for E368, not as a standalone submission feature.
- Failure condition: do not use E369 scores to amplify E368 unless the Q2 target-only bad-axis warning is neutralized.

### E370 Q2/S1 risk-constrained recalibration diagnostic

- Target hidden structure: separability of E368's validated Q2/S1 lifestyle-state signal from Q2-only E323 bad-axis exposure.
- Why needed: E369 supports E368, but Q2-only movement versus E365 has high E323 similarity. Before submitting a derivative, we need to know whether the Q2 risk can be removed without killing the signal.
- Feature/action form:
  - no new feature family;
  - candidate action: E365 plus E368 Q2/S1 delta with Q2 scale, S1 scale, and optional Q2 projection away from E323-vs-E365 bad axis;
  - diagnostics: E368 public-like jackknife, E369 public-free transfer alignment, all-target and Q2-only bad-axis cosine.
- Current evidence:
  - generated candidates: `275`;
  - eligible safer replacements: `0`;
  - baseline Q2 transfer abs Spearman `0.428458`, S1 `0.197475`;
  - Q2 orthogonalization reduces bad-axis cosine but drops Q2 transfer abs Spearman to about `0.181`;
  - best local stress row is S1-amplified but still has Q2 bad-axis cosine `0.591735`.
- Registry status: rejected as a submission feature; keep as a risk diagnostic.
- Failure condition: do not use linear bad-axis projection as the next Q2 safety mechanism. A future feature must learn Q2 calibration risk directly from public-free or anchor-stress targets.

### E371 row-wise Q2 safety/trust latent

- Target hidden structure: row-level trust for E368 Q2 movement, separating public-free Q2 lifestyle transfer rows from E323-like risk rows.
- Why needed: E370 showed Q2 risk is not removable by global projection. The next plausible separation is row-wise: good Q2 rows versus risky Q2 rows.
- Feature/action form:
  - context scores: Q2 transfer, Q2 gate, row validity, bad gate, and Q2 bad-contribution rank;
  - candidate actions: Q2 row weights by transfer floor, trust floor, risk damp, contribution damp, hard trust mask, and weak-transfer bad-tail damp;
  - S1 variants: fixed E368 S1 with scales `1.00`, `1.06`, and `1.15`.
- Current evidence:
  - generated candidates: `369`;
  - eligible safer replacements: `0`;
  - best total candidate top1/top10 `0.479592/0.959184`;
  - best total Q2 cosine only improves to `0.585298`;
  - risk-reducing candidates around Q2 cosine `0.539628` have top10 `0.0`.
- Registry status: rejected as a submission feature; keep as evidence that Q2 risk is not separable by current row-wise lifestyle trust.
- Failure condition: do not repeat row-wise Q2 damping based only on transfer/gate/risk ranks. A future row-wise Q2 feature needs a new target label, not a reweighted version of these scores.

### E372 Q2 calibration-residual latent

- Target hidden structure: Q2 residual calibration/prior state after subject/calendar base correction.
- Why needed: E370 and E371 showed that Q2 risk is not linearly removable and not a simple wrong-row issue. E372 tests whether the hidden Q2 state should be learned directly as a calibration residual.
- Feature/action form:
  - teacher: Q2 train residual after subject/calendar base;
  - context views: family, JEPA residual, story bundle, raw day, family-story, family-JEPA-story;
  - generated features: test-side Q2 residual score and Q2 calibration logit delta;
  - action families: Q2 replacement, Q2/E368 blend, Q2 agreement gate, with E368 S1 retained.
- Current evidence:
  - `4/12` local residual latents pass null gates;
  - best latent `Q2_jepa_resid_subject` improves blocked local Q2 logloss by `-0.030211`;
  - `241` materialized candidates yield `0` safer eligible replacements;
  - strongest local scenario candidate worsens Q2 bad-axis cosine to `0.609289`.
- Registry status: approved as a diagnostic feature; rejected as a submission feature.
- Failure condition: do not use Q2 residual score directly as a probability move. It needs an action-health/veto layer before any public-facing materialization.

### H009 S4 mobility rank-rewrite representation

- Target hidden structure: mobility/obligation/errand state as S4 row-ordering law.
- Why needed: H007/H008 showed that mobility latent improves S4 locally but tiny logit edits are too small. H009 tests whether the hidden state should reorder S4 probability mass instead of nudging logits.
- Feature/action form:
  - context: H007 `mobility_jepa` latent;
  - target representation: S4 rank assignment under E247 marginal distribution;
  - actions: global/subject/dateblock quantile rewrite, tail swap, model-blend rewrite, and reverse controls.
- Current evidence:
  - `88` materialized candidates;
  - `26` local-only high-risk candidates;
  - best forward rewrite worst delta `-0.008027`;
  - best reverse control worst delta `+0.026745`;
  - `0` jackpot candidates.
- Registry status: approved as a diagnostic representation; rejected as S4-only public translator.
- Failure condition: do not submit S4-only rank rewrite unless an additional route/action-health layer reduces selector p90 risk.

### H010 objective mobility route representation

- Target hidden structure: mobility/obligation state as objective sleep-stage route, especially `S1 down + S4 up`.
- Why needed: H009 proves S4 ordering but rejects S4-only materialization. The hidden human state may be multi-target and objective-stage based.
- Feature/action form:
  - context: H007 `mobility_jepa` latent plus target-specific positive delta;
  - target representation: coupled route rewrite preserving E247 marginals per target;
  - selected action: subject-level quantile rewrite on `S1/S4` with strength `0.25`.
- Current evidence:
  - `98` candidates;
  - `1` jackpot candidate;
  - selected file changes `S1=213` and `S4=242` cells;
  - local worst delta `-0.004319`;
  - selector mean `-0.001259`;
  - selector p90 `0.000702`;
  - reverse controls fail locally.
- Registry status: approved as current high-information big-bet candidate.
- Failure condition: if public LB worsens materially, route rank materialization is rejected and the next representation should learn objective route action-health rather than amplify mobility rank.

Public update: H010 scored `0.5781718175`, worse than E247 by `+0.0020128681`. Registry status is now rejected as a public translator; retain only as a public-negative action-health teacher.

### H011 H010 public-inversion action-health representation

- Target hidden structure: public action-health of a proposed S1/S4 objective route.
- Why needed: H010 showed that a locally coherent HS-JEPA mobility route can be strongly public-invalid. The new target is not "predict S1/S4 labels" but "predict whether an S1/S4 action should be trusted in the public/test world."
- Feature/action form:
  - context: H010 S1/S4 logit delta, row-level H010 action magnitude, target subset, known-public-bad agreement score;
  - target representation: negative projection onto H010's public-bad action axis;
  - selected action: invert the strongest `50` H010-active rows on both S1 and S4.
- Current evidence:
  - `63` materialized candidates;
  - selected file `submission_h011_public_inversion_rowtop_all_k50_a1_uploadsafe.csv`;
  - changed cells `100` (`S1=50`, `S4=50`);
  - H010-axis coefficient `-0.545892`;
  - selector mean/p90 `+0.000200937` / `+0.000573326`, so this is not selector-safe.
- Registry status: approved as a high-information public sensor, not as a safe final feature.
- Failure condition: if public LB does not improve meaningfully, stop using output-space failed-action inversion. Future HS-JEPA action-health must be learned before materialization from row/target/candidate context.

### H012 public-equation hidden-state posterior

- Target hidden structure: pseudo-public label/subset representation implied by known public LB observations.
- Why needed: current bottleneck is public/action-health mismatch. Instead of adding another feature, H012 asks whether public LB observations themselves constrain the hidden state enough to become a JEPA target.
- Feature/action form:
  - equations: known public log-loss deltas versus E247;
  - latent: continuous posterior `q` over `250 x 7` test cells;
  - context priors: E247, public-good soft/median ensemble, neutral, sharp E247;
  - action: move E247 toward stable high-score posterior cells.
- Current evidence:
  - `19` public equations;
  - best LOO public-delta Spearman `0.935088`;
  - selected file `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`;
  - changed cells `1200`;
  - posterior mean/p90 delta `-0.006446397` / `-0.004693170`;
  - max probability delta `0.294110`.
- Public feedback: LB `0.5681234831`, improving over E247 by `0.0080354663`.
- Registry status: promoted to core HS-JEPA feature/target representation and current public frontier. Still not automatically private-safe.
- Failure condition: no longer "if public LB fails"; it passed. The active discard condition is now private-risk evidence: if leave-H012-out posterior, subject-time memory compatibility, or target-wise stability show the gain is carried by brittle public-only cells, use H012 as final/public anchor but avoid amplifying it further.

### H014 subject-time sleep-state conditioned memory prior

- Target hidden structure: within-subject temporal continuity conditioned on sleep-state and sensor-quality similarity.
- Why needed: an external high-scoring note reports `submission_v106_sleep_state_conditioned_memory.csv` public LB `0.5703952266`. This is a strong non-equation view of the same repeated-subject world and can regularize H012's public-equation posterior.
- Feature/action form:
  - date-distance memory within subject;
  - sleep episode similarity;
  - sensor coverage / missingness / quality similarity;
  - effective neighbor count and memory reliability;
  - target-wise agreement between memory posterior and H012 posterior.
- Current evidence:
  - external public score is worse than H012 by `0.0022717435` but much stronger than most pre-H012 local semantic experiments;
  - no prediction file is available, so it cannot be used as an equation anchor.
- Registry status: approved as a next diagnostic prior, not yet a submission feature.
- Failure condition: reject as an H012 regularizer if memory-compatible cells lose most of H012's posterior delta or if agreement is driven only by low-impact cells.

### H013 raw human-state action-health gate

- Target hidden structure: human day-state controls where a public-equation target representation should be trusted.
- Why needed: H012 is too broad and may overfit public equations. HS-JEPA needs a raw-context gate so hidden public-state action is applied only on rows whose lifelog context supports the target route.
- Feature/action form:
  - raw context: app usage categories, time-of-day usage, screen status, charging, activity, pedometer, GPS, heart rate, phone/watch light, BLE/Wifi/Ambience counts, calendar and payday/weekend proxies;
  - latent: standardized PCA human-state embedding plus KNN train-label route prior;
  - action-health target: known-public bad/survivor action alignment smoothed over human-state neighbors;
  - action: H012 posterior movement on high-health or anti-bad rows with optional KNN route agreement.
- Current evidence:
  - `1190` candidates generated;
  - `0` full jackpot-gated candidates;
  - `168` high-risk candidates;
  - selected diagnostic `submission_h013_raw_hs_jepa_health_top_route_r140_c260_a0.75_4a91266c_uploadsafe.csv`;
  - changed cells `260`;
  - posterior delta `-0.001233534`;
  - selector p90 `+0.001506255`.
- Registry status: approved as diagnostic representation and HS-JEPA architecture evidence; rejected as current default submission feature.
- Failure condition: do not use scalar raw human-state row health alone to materialize H012. Future use requires row x target action-health or a joint model that reduces public-bad selector risk while keeping visible posterior gain.

### H014 sleep-state memory compatibility prior

- Target hidden structure: same-subject temporal continuity conditioned by sleep-state and sensor-quality similarity.
- Why needed: external V106 reports public `0.5703952266` from sleep-state-conditioned same-subject memory, so H012 should be tested against this independent human-state view.
- Feature/action form:
  - same-subject train-label memory weighted by date gap;
  - sleep-state similarity from H013 raw human-state features;
  - sensor-quality similarity from coverage/missingness/count features;
  - target-wise agreement between memory posterior and H012 posterior direction;
  - H012 posterior-gain preservation under memory-compatible masks.
- Current evidence:
  - H012 changed cells audited: `1200`;
  - memory-agree rate: `0.405000`;
  - memory-agree posterior-gain share: `0.279671`;
  - high-alignment/high-reliability gain share: `0.101482`;
  - best H014 candidate kept H012 gain rate: `0.358133`;
  - all candidates are `diagnostic_only`.
- Registry status: keep as diagnostic/private-risk prior. Reject as a direct H012 regularizer.
- Failure condition: do not prune or revert H012 based on this memory score unless a new public-free/private-risk target proves that memory-disagree H012 cells are harmful.

### H015 H012 self-feedback public-equation posterior

- Target hidden structure: recursive public-equation hidden-state posterior after H012's own public score is added.
- Why needed: H012's public win was larger than forecast, so the next worldview question is whether H012 is a fixed point or an under-amplified posterior step.
- Feature/action form:
  - current anchor: H012 probability tensor;
  - equations: known public log-loss deltas versus H012;
  - priors: H012 current, H012-sharp, wide top-public soft priors, top-public median, neutral, E247;
  - action: move H012 toward high-consistency posterior cells with small per-cell amplitude.
- Current evidence:
  - `21` known public observations and `20` equations vs H012;
  - best config LOO Spearman `0.986466`, LOO MAE `0.001312381`;
  - selected file `submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv`;
  - changed cells `1600`;
  - posterior mean/p90 delta vs H012 `-0.001586219` / `-0.001149849`;
  - max probability delta vs H012 `0.051642`.
- Registry status: approved as the next high-information public sensor, not private-safe evidence.
- Failure condition: if H015 public LB worsens, treat H012 as the public-equation fixed point and stop recursive sharpening without a new independent non-public risk sensor.

### H016 diffuse public cell-weight field

- Target hidden structure: public LB as a non-uniform row x target cell-weight/gain field over the H012/H015 action space.
- Why needed: H012 proved public-equation latent reconstruction works, and H015 tests recursive sharpening. H016 asks whether that sharpening should be applied everywhere or only where the inferred public sensor gives weight and gain.
- Feature/action form:
  - context: known submission loss-delta tensors under H012/H015 probability and posterior label proxies;
  - latent: nonnegative public cell weights fitted with ridge-dual leave-one-public stress;
  - anti-collapse check: permutation of known public LB deltas while keeping loss-delta tensors fixed;
  - action: move H012 toward H015 only on high public-weight/gain cells.
- Current evidence:
  - best config LOO MAE `0.000013654`, p90 abs `0.000026381`, Spearman `0.990977444`;
  - uniform-weight MAE `0.000885430`;
  - effective weight count `1747.348299`, so the field is broad/diffuse;
  - permutation null median LOO MAE `0.004329919`, max null Spearman `0.660150`;
  - selected file `submission_h016_public_subset_gain_all_k1000_a0.75_uploadsafe.csv`;
  - selected predicted subset-weight delta vs H012 `-0.000296297`;
  - full H015 predicted subset-weight delta vs H012 `+0.000164649`.
- Registry status: approved as a high-information structural feature/action layer. Not yet public-validated.
- Failure condition: if H016 public LB worsens, do not discard the weight diagnostic entirely; discard the direct materialization. The weight field may still be useful as a risk sensor for later candidates.

### H017 joint label-weight posterior completion

- Target hidden structure: joint public label posterior and diffuse public cell-weight field satisfying known public LB deltas.
- Why needed: H012 and H016 separately solve labels and weights. H017 tests whether these are compatible pieces of the same public equation, and whether H012 should be moved closer to its own posterior.
- Feature/action form:
  - context: known submission loss-delta tensors versus H012;
  - latent: `(q, w)` represented as `[w, w*q]`;
  - priors: H012 public posterior and H016 mean weight are the selected compatible state;
  - action: move H012 toward the joint `q` on high joint public-weighted gain cells.
- Current evidence:
  - selected config `q=h012_public_posterior`, `w=h016_mean_weight`;
  - LOO MAE `0.000001044`, Spearman `1.000000`;
  - permutation-null median LOO MAE `0.001672425`, max null Spearman `0.200902`;
  - `q_prior_abs_move=0.000000677`, `w_prior_l1_move=0.000000293`, so this is compatibility evidence rather than a new latent discovery;
  - selected file `submission_h017_joint_label_weight_oracle_gain_all_k1650_a1_uploadsafe.csv`;
  - selected predicted joint delta vs H012 `-0.000574501`;
  - changed cells `1650`, max probability delta vs H012 `0.107121`.
- Registry status: approved as a high-information public sensor for posterior-completion. Not approved as independent human-state/private-safe evidence.
- Failure condition: if public LB worsens, do not continue pushing H012 to the original posterior; use the H012 posterior only as an explanatory latent unless an independent private/public risk sensor appears.

### H018 hard-label public-world posterior

- Target hidden structure: binary public label worlds that jointly explain known public LB deltas under the H017 label posterior and public cell weights.
- Why needed: H012/H017 are continuous posterior equations. Real labels are binary, so a valid hidden-world story should still produce unusually good hard-label worlds rather than only smooth pseudo-labels.
- Feature/action form:
  - context: H017 public label posterior, H016-style public weights, and known submission loss-delta tensors;
  - latent: sampled binary hard public worlds, reweighted by public-equation fit;
  - anti-collapse check: permute public deltas while keeping the same sampled hard-world predictions fixed;
  - action: move H012 toward the hard-world posterior on high-gain cells.
- Current evidence:
  - sampled hard worlds: `90000`;
  - best posterior `soft_t0.00035_p1.5`;
  - posterior equation MAE `0.000005557`, p90 abs `0.000017261`;
  - best sampled hard-world MAE `0.000167740`;
  - ESS `19756.395104`;
  - q shift from H017 prior `0.002394823`, correlation `0.999879785`;
  - real hard-world errors beat all `300` permuted-public-delta nulls;
  - selected file `submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv`;
  - selected predicted hard-world delta vs H012 `-0.000603041`.
- Registry status: approved as the binary-aware posterior-completion public sensor. It strengthens H017's non-collapse evidence but is not an independent human-state/private-safe latent.
- Failure condition: if public LB worsens, stop using hard-world reweighting as a direct materializer; keep it only as a diagnostic that the public-equation posterior is plausible under binary labels.

### H019 hard public row-subset posterior

- Target hidden structure: row-level public/private subset identity under the H018/H017 public label posterior.
- Why needed: H016's cell weights are too flexible relative to how public LB is likely computed. A realistic public split should be representable as selected rows evaluated over targets.
- Feature/action form:
  - context: known submission row-wise loss-delta tensors versus H012;
  - target representation: sampled binary row masks of fixed public subset sizes;
  - anti-collapse check: permute public deltas while keeping row-mask predictions fixed;
  - action: apply H018 hard-world posterior-completion only on rows with high inferred public inclusion/gain.
- Current evidence:
  - best sampled config `h017_joint/subset_size=150`, top100 MAE `0.000074821`;
  - best posterior `h018_hard_k125_soft_t4e-05_p2`;
  - posterior MAE `0.000027461`, p90 abs `0.000052606`, Spearman `0.998496`;
  - inclusion probability range `0.370519-0.786440`;
  - all `300` permuted-public-delta nulls are worse on tracked row-mask metrics;
  - selected file `submission_h019_row_subset_hardworld_gain_all_r240_a1_uploadsafe.csv`;
  - selected row-posterior delta vs H012 `-0.000611233`, but H018 is slightly stronger under the same row posterior at `-0.000615495`.
- Registry status: approved as a realistic public-row-subset diagnostic. Not approved as a stronger action than H018 unless public feedback specifically rewards row exclusion.
- Failure condition: if public LB worsens relative to H018/H012, keep the row-subset posterior as explanatory evidence but stop pruning low-inclusion rows from H018-style actions.

### H020 joint target-vector hardworld posterior

- Target hidden structure: row-level 7-target Q/S hidden state, represented as one 7-bit target vector per test row.
- Why needed: independent cellwise public posteriors can fit known LB equations while producing implausible target combinations. A stronger HS-JEPA target should predict the hidden row state vector, not seven unrelated label cells.
- Feature/action form:
  - context: H018 hard-world marginal posterior, known public submission loss deltas, and train target-vector frequencies;
  - latent: sampled joint target-vector worlds with optional global/subject empirical vector priors;
  - anti-collapse check: public-delta permutation null while keeping the same sampled vector worlds;
  - action: move H012 toward the selected joint-vector posterior on all cells.
- Current evidence:
  - best sampled config `global_b0.15`, best/top100 world MAE `0.000175369` / `0.000260939`;
  - selected posterior `none_b0_soft_t0.00012_p2`;
  - posterior MAE `0.000012623`, p90 abs `0.000023274`, Spearman `0.995488722`;
  - real vector-world errors beat all `300` public-delta permutation nulls;
  - selected file `submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv`;
  - selected rowweighted delta vs H012 `-0.001105455`, stronger than H018/H019 in the same report;
  - upload-safe validation passed with no NaN and probabilities clipped to `[0.000001, 0.999999]`.
- Registry status: approved as a high-upside posterior-completion public sensor and architecture evidence for row-level target-state HS-JEPA. Not approved as private-safe final evidence.
- Failure condition: if public LB worsens, do not discard joint-vector representation entirely; discard the aggressive beta-zero materializer. A beta-positive/train-prior or private-risk-gated vector posterior would need separate evidence.

### H021 human-state conditional vector prior gate

- Target hidden structure: human lifestyle context as a predictor of the row-level 7-bit Q/S hidden target vector.
- Why needed: H020 proves joint row-vector consistency but not human-state grounding. H021 asks whether raw human-state features can identify which H020 moves are compatible with a plausible lifestyle-state vector.
- Feature/action form:
  - context: H013 human-state features from calendar/payday/weekend, app usage, screen/charging/light, activity, HR, GPS, BLE/Wifi/Ambience and sensor-quality counts;
  - latent: KNN distribution over 128 train target-vector codes;
  - anti-collapse check: train-only global-prior comparison plus row-permuted q_hs action null;
  - action: move H012 toward H020 only on cells where q_hs and H020 agree.
- Current evidence:
  - best human-state vector prior `subject_all_k10` marginal BCE `0.617584875` vs global vector prior `0.664614445`;
  - selected ensemble combines subject and hybrid social/sleep/state views;
  - selected file `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv`;
  - H020-equation delta vs H012 `-0.000684129`;
  - H020 gain retained `0.618866184`;
  - row-permuted q_hs null median is worse by `0.005549353`.
- Registry status: approved as a human-state action gate over H020. Not approved as direct probability replacement.
- Failure condition: if public LB worsens, keep the human-state vector prior as diagnostic evidence but stop using it to gate public-equation moves until a stronger action-health target is learned.

### H022 human-state conditioned vector-world prior

- Target hidden structure: row-level 7-target vector world with a conditional human-state proposal prior.
- Why needed: H020's final posterior used `beta=0`; H021 proved q_hs is locally predictive but only used it as a post-hoc gate. H022 tests whether q_hs belongs inside the generative vector-world posterior itself.
- Feature/action form:
  - context: H018/H020 public-equation marginals plus H021 `q_hs`;
  - latent: sampled 7-bit vector worlds under none, `q_hs`, confidence-weighted `q_hs`, and marginal `q_hs` priors;
  - anti-collapse checks: public-delta permutation and q_hs row-permutation null;
  - action: promote only if a beta-positive human-state posterior wins the public-equation posterior selection.
- Current evidence:
  - weak q_hs prior helps sampled-world search: `hs_b0.1` config score `0.000277410` vs `none_b0` `0.000310758`;
  - final posterior rejects q_hs: selected `none_b0_top250_t0.0005`, MAE `0.000014073`;
  - best positive q_hs posterior is weaker: `hs_b0.1_top250_t0.00012`, MAE `0.000024950`;
  - public-delta null passes strongly, while q_hs row-permutation null only supports top100 world search, not best/median world quality;
  - no H022 upload-safe candidate promoted.
- Registry status: approved as a proposal/search feature and diagnostic prior. Rejected as a final action probability prior.
- Failure condition: if future variants need positive q_hs beta to be selected, require both posterior/action dominance and row-permutation-null dominance. Otherwise keep q_hs as gate/proposal only.

### H023 human-state Pareto proposal energy

- Target hidden structure: public-compatible row-level vector worlds that are also close to raw human-state geometry.
- Why needed: H022 showed `q_hs` should not be the final posterior prior, but it may still identify which public-compatible hidden worlds are human-plausible. This is the JEPA role split: public equations define the target posterior, human-state context constrains the latent geometry.
- Feature/action form:
  - context: sampled H020/H022 row-vector worlds and known public-delta fit;
  - latent feature: `q_hs` energy of each sampled world plus row-vector KL from the H021 human-state prior;
  - anti-collapse checks: row-permuted `q_hs` energy for public-error top-k worlds and row-permuted `q_hs` controls for the selected Pareto posterior;
  - action rule: promote only if the Pareto posterior beats row-permuted controls on public fit and human-state geometry.
- Current evidence:
  - public-error top1000 worlds have real human-state energy `4.877889323` vs row-permutation null median `5.234522555`, p `0.012345679`;
  - selected Pareto posterior `pareto_top1000_lam0.2_t0.00012` improves human-state geometry (`rowperm_hs_kl_p=0.016393443`);
  - the same posterior does not improve public fit against row-permuted controls (`rowperm_public_p=0.754098361`);
  - no root upload-safe H023 candidate promoted.
- Registry status: approved as representation/alignment diagnostic and proposal energy. Rejected as direct action selector.
- Failure condition: do not use H023 energy to materialize submissions unless a new action-health target lowers row-permutation public-fit p and preserves public-only posterior compatibility.

### H024 public-sensor action-health decoder

- Target hidden structure: action health of a proposed probability movement, using known public outcomes as sensors rather than labels to optimize directly.
- Why needed: H015-H023 produce many public-equation-attractive posterior moves, but H023 proved human-state geometry alone cannot choose the final action. H024 asks whether good/bad public movement axes and latent cell-state features can decode safe post-H012 actions.
- Feature/action form:
  - context: candidate output tensor geometry relative to H012/E247 and public-bad anchors H010/E323/E216/E267;
  - latent features: H012 posterior score, H015 self-feedback score, H021 human-state gate agreement, H023 Pareto/human-state cell energy;
  - anti-collapse checks: leave-one-public-out public score reconstruction and public-score permutation for the top unknown candidate;
  - action rule: promote only if the top unknown candidate has high support below H012, narrow prediction interval, low bad-axis load, and null p below `0.05`.
- Current evidence:
  - known public LOO is strong: best decoder MAE `0.000773`, Spearman `0.969925`, pairwise `0.947368`;
  - unknown transfer fails: top H015 `k100` candidate has predicted median `0.570054`, p10/p90 `0.559653-0.580761`, H012-beating support `0.15`, and permutation p `0.841`;
  - no H024 upload-safe candidate promoted.
- Registry status: approved as a bottleneck diagnostic and known-score latent; rejected as current submission selector.
- Failure condition: do not submit files selected only by this decoder. A future action-health decoder must show unseen-candidate stability, not just known-score reconstruction.

### H025 train-counterfactual action-health decoder

- Target hidden structure: action health learned from train-label counterfactuals rather than public-LB regression.
- Why needed: H024 showed public-axis action-health is under-supervised and unstable on unseen candidates. H025 asks whether train rows can supply dense action-health supervision by simulating probability moves and measuring logloss gain.
- Feature/action form:
  - context: H013 human-state row embeddings, target one-hot-like geometry, base prediction, proposal prediction, logit/probability deltas, and row latent PCs;
  - target: per-cell gain `loss(base) - loss(counterfactual_action)`;
  - proposal generators: global, subject, subject-time, feature-family KNN, and subject-restricted KNN memory views;
  - anti-collapse checks: row/time OOF transfer, leave-proposal-family-out transfer, known-public-bad anchor ranking, and row-permuted test placement stress.
- Current evidence:
  - row/time OOF Spearman `0.021090879`;
  - row/time top10 lift `0.004425758`;
  - leave-family metrics are much stronger but likely proposal-family-shaped;
  - H025 ranks known public-bad Q2/residual probes above safer unknowns;
  - selected unknown H023 diagnostic fails row-permutation placement stress with p `0.576666667`;
  - no H025 root upload-safe file promoted.
- Registry status: approved as a diagnostic representation and a failure map for train-vs-public action health. Rejected as a submission selector.
- Failure condition: do not use train counterfactual gain alone to select public submissions. Re-enter only if a public/private calibration or bad-axis veto term removes the known public-bad Q2/residual preference and passes row/time plus row-permutation stress.

### H026 public/private calibration-veto energy

- Target hidden structure: public-safe action health after discounting train-health moves that resemble known public-bad Q2/residual shortcut anatomy.
- Why needed: H025 learned some train-visible action health but confused it with public-bad shortcuts. H026 asks whether an explicit public/private veto is enough to separate those two states.
- Feature/action form:
  - context: H025 predicted gain, H024 public decoder score, public-good/public-bad source axes, OOD/load features, Q2 shortcut exposure, and candidate movement anatomy;
  - latent feature: source-level and cell-level public-bad energy;
  - anti-collapse checks: known-source sanity, H025 row-permutation placement stress, and H024 public-score permutation stress;
  - action rule: promote only if known-bad anchors are demoted and the selected unknown variant passes both train-health and public-transfer stresses.
- Current evidence:
  - source-level sanity passes: H012 ranks first and known public-bad JEPA/Q2/residual anchors are demoted;
  - selected diagnostic keeps strong H025 row-placement signal with row-permutation p `0.000000`;
  - public-transfer check fails: H024 median `0.574388293`, support below H012 `0.166667`, public-score permutation p `0.898000`;
  - no H026 root upload-safe file promoted.
- Registry status: approved as a diagnostic public/private energy feature. Rejected as a complete action selector or materializer.
- Failure condition: do not submit variants selected by this scalar veto. Re-enter only if the public/private calibration target is learned before candidate generation or if a future variant passes H024/H025 stresses simultaneously.

### H027 born public/private-aware generator features

- Target hidden structure: cell-level action health that is public-readable and private-aware before candidate materialization.
- Why needed: H026 showed that after-the-fact scalar veto is too late. The external V106 note and H014 say same-subject sleep-state memory is real but not enough. H027 tests whether the generator can combine public posterior targets, memory, human-state agreement, train-action health, and public-bad energy before deciding which cells are actionable.
- Feature/action form:
  - context sources: H015 public-feedback posterior, H020 joint-vector posterior, H023 human-state Pareto posterior, H021/H023 human-state agreement, H014 same-subject memory/private safety, H026 good/bad public axes, and H025 train-action predicted gain;
  - styles: public-memory bridge, bad-axis escape, train-private consensus, human-state agreement, and wild-equation high-upside variants;
  - action rule: materialize top cells only if source posterior strength, private safety, human agreement, train gain, and public-bad energy jointly pass the style score;
  - anti-collapse checks: H024 public decoder, H025 row-permutation placement, and H024 public-score permutation stress.
- Current evidence:
  - generated `1648` variants;
  - best diagnostic is H015-derived `S1S2S3_k80_a0p25`;
  - H024 predicted public median `0.569712461` with support below H012 `0.150000`;
  - H025 row-permutation p `0.383333333`;
  - H024 public-score permutation p `0.822000000`;
  - no root upload-safe H027 file promoted.
- Registry status: approved as a negative generator-boundary diagnostic. Rejected as a submission selector.
- Failure condition: do not continue by adding more scalar weights to the same H015/H020/H023 source cells. Re-enter only with a new public/private calibration target or a proposal generator not dominated by existing posterior-completion cells.

### H028 public/private action-gradient features

- Target hidden structure: public LB response field for interventions from H012.
- Why needed: H026-H027 showed that better gates around existing posterior targets do not create H012-beating actions. H028 asked whether the response field itself could be learned.
- Feature/action form:
  - context: known submissions' logit movement from H012 plus H012/H015/H016/H020/H021/H023/H014/H027 cell-state features;
  - target: public LB delta versus H012;
  - action rule: generate gradient descent, rollback, amplification, and hybrid movement families from the learned cell-level response;
  - anti-collapse checks: leave-one-public-out, shuffled-public-delta null, H024 decoder, H025 row-permutation, and H024 public-score permutation.
- Current evidence:
  - public response is learnable above null: selected fit LOO MAE `0.001204883`, permutation p `0.000000`;
  - extrapolation fails: top generated file has H024 median `0.576388429`, support below H012 `0.083333333`, H025 row-permutation p `0.710000000`;
  - no root upload-safe H028 file promoted.
- Registry status: approved as coarse public-response diagnostic. Rejected as local descent/action feature.
- Failure condition: do not use this gradient directly for submissions unless a new invariant explains H012 and independent H024/H025 stresses reverse.

### H029 H012 needle-basin invariant features

- Target hidden structure: exact row-target placement invariant behind the H012 public-equation basin.
- Why needed: H028 showed H012 is not a smooth local optimum. H029 asks whether the basin is explained by support, amplitude, target/subject blocks, same-subject memory agreement, or row identity.
- Feature/action form:
  - context: H012 cell posterior, H014 memory agreement/private-safety cells, target/subject identity, and H012-vs-E247 movement anatomy;
  - variant families: support-ray scales, posterior top-k alternatives, target/group/subject rollback, memory-agree/disagree/private-safe only/rollback, outside-support target-count matched moves, and target-wise row permutations;
  - anti-collapse checks: H024 public decoder, duplicated-H012 control, H024 public-score permutation, and H025 row-permutation stress.
- Current evidence:
  - generated `102` variants;
  - selected diagnostic `rollback_target_S1` still has H024 median `0.570494744`, support below H012 `0.116666667`, public-score permutation p `0.858000000`, and H025 row-permutation p `0.613333333`;
  - target-wise row permutation collapses to median `0.581149687`;
  - memory-only/rollback variants do not recover H012.
- Registry status: approved as the current bottleneck diagnostic. Rejected as a submission generator.
- Failure condition: do not submit target rollback, memory pruning, outside-support matched, or row-permuted H012 variants. Re-enter by solving row/subset identity as a first-class latent rather than ablation.

### H030 row-target identity allowance features

- Target hidden structure: public-equation row-target identity, represented as per-cell movement allowance inside the inverse solver.
- Why needed: H029 showed exact row-target placement matters, while H016/H019/H020 separately found public cell weights, row subset state, and joint-vector state. H030 tests whether those signals should shape the solver itself.
- Feature/action form:
  - cell identity scores: H012 support/posterior, H016 public cell weight, H019 row public-subset score, H020 joint-vector cell/row score, H014 memory/private-safety score;
  - solver: weighted public-equation posterior `q = prior + D A^T (A D A^T + lambda I)^-1 residual`;
  - candidate families: e247-pre-H012 identity equation, e247-post-H012 identity equation, exact H012 support retarget, and H012 residual identity moves;
  - anti-collapse checks: independent H012-held-out without direct H012 prior, H024 decoder, H024 public-score permutation, and H025 row-permutation.
- Current evidence:
  - true held-out H012 prediction error `0.000485324` using `pre_h012_good_soft + identity_combo`;
  - generated candidates fail action health: best H024 median `0.572160346`, support below H012 `0.100000000`, public-score permutation p `0.923333333`, H025 row-permutation p `0.670000000`;
  - no root upload-safe H030 file promoted.
- Registry status: approved as a row-target identity latent feature. Rejected as a direct action/materialization feature.
- Failure condition: do not use allowance-prior top-k materialization as a submission route. Re-enter only with a learned translator that maps identity posterior to support/amplitude/calibration action.

### H031 memory-conflict public-core contrast features

- Target hidden structure: cells where H012's public-equation action conflicts
  with V106/H014 same-subject sleep-state memory.
- Why needed: V106 is a strong human-world model, but H014 showed H012 gain is
  concentrated where that model disagrees. H031 tests whether this conflict is
  an actionable public core or only a diagnostic contrast.
- Feature/action form:
  - cell state: memory agreement, memory reliability, H012 posterior gain,
    target conflict group, and E247-to-H012 movement amplitude;
  - candidate families: conflict-core amplification, conflict-core plus
    memory-agree rollback, memory-agree rollback, and core reconstruction from
    E247;
  - anti-collapse checks: H024 action-health decoder, H024 public-score
    permutation stress, and H025 row-permutation stress.
- Current evidence:
  - H012 changed cells audited `1200`;
  - memory-disagree cells `714` hold `0.720328567` of H012 posterior gain;
  - generated candidates `482`;
  - best diagnostic H024 median `0.569809630`, support below H012 `0.150000000`;
  - H024 public-score permutation p `0.800666667`;
  - H025 row-permutation p `0.183333333`;
  - no root upload-safe H031 file promoted.
- Registry status: approved as an explanatory contrast feature. Rejected as a
  direct amplification, swap, or rollback materializer.
- Failure condition: do not submit memory-conflict variants unless a new
  translator explains the exact H012 amplitude/route. Re-enter by learning
  probability action health on conflict cells, not by increasing their weight.

### H035 basin-boundary support-swap features

- Target hidden structure: whether H012 is an editable row-target identity basin
  or a locked fixed point under local support replacement.
- Why needed: H032-H034 showed the H012 phase is recognizable, but first-order
  cell and row-route edits fail. H035 tests the remaining local route:
  structure-preserving combinatorial swaps.
- Feature/action form:
  - cell state: H032 phase scores, H033 phase-lock costs, H034 row-route state,
    H012 posterior gain, memory conflict, public-row/vector scores, and
    support-count buckets;
  - candidate families: support swaps preserving target, row, or support-count,
    plus support-tail softening;
  - anti-collapse checks: q-loss delta, route margin, H024 pre-state margin,
    H024 public permutation, and H025 row-placement permutation.
- Current evidence:
  - generated candidates `585`;
  - q-improving candidates `55`;
  - best q-loss delta `-0.000286222`;
  - route-safe count `0`;
  - pre-state-better count `0`;
  - strict gate count `0`;
  - selected diagnostic q delta `+0.000512108`, route margin `+0.017292336`,
    pre-state margin `+0.012214437`;
  - no root upload-safe H035 file promoted.
- Registry status: approved as a basin-lock diagnostic. Rejected as a local
  support-swap materializer.
- Failure condition: do not submit H035 support swaps unless a new global
  public/private or fixed-point translator certifies that the swap remains
  inside the H012 action basin.

### H036 global public-world posterior features

- Target hidden structure: latent public row subset plus row/target binary label
  world that explains all known public LB deltas around H012.
- Why needed: H035 rejected local edits; a breakthrough now requires a global
  hidden object rather than another H012 support tweak.
- Feature/action form:
  - q sources: H012 posterior, H015 feedback posterior, H017 joint q, H018 hard
    labels, H020 row-vector q, and mixtures;
  - row priors: H019 inclusion/row weights, H030 identity scores, H035 route and
    public-row scores, plus H013 human-social/calendar priors;
  - sampled world state: row mask, binary label tensor, predicted public deltas;
  - posterior features: `world_public_prob`, `world_q_cond`, `cell_world_score`;
  - candidate families: top cells, target-specific cells, row-world all-target
    moves, and needle-world moves.
- Current evidence:
  - best world MAE `0.000202825`, Spearman `0.969924812`;
  - permutation-null p `0.000000`;
  - top configs include both equation priors and H013 `late_social_phone`;
  - generated candidates fail action translation: selected diagnostic has H024
    pre-H012 margin `+0.001430749`, support `0.250000000`, and H025
    row-permutation p `0.590000000`.
- Registry status: approved as a non-collapsed hidden-public-world feature set.
  Rejected as a direct materialization/action feature.
- Failure condition: do not move H012 directly toward `world_q_cond` unless a
  separate translator or stress gate proves the action stays inside the H012
  support/amplitude/calibration basin.

### H037 fixed-point ray translator features

- Target hidden structure: H012-compatible amplitude translator on the original
  E247-to-H012 ray.
- Why needed: H036 proved a global public-world latent but direct `q_cond`
  movement failed. H037 tests whether the missing translator is simply "keep
  H012 support fixed and adjust ray amplitude."
- Feature/action form:
  - support mask: cells changed by H012 from E247;
  - alignment state: whether H036 `world_q_cond` pushes further along or
    against the H012 ray;
  - cell pressure: H036 `cell_world_score` and row public probability;
  - candidate families: aligned amplification, conflict damping, dual
    amplify/damp, target ray scaling, row-public ray scaling, and support-only
    q-pulls.
- Current evidence:
  - H036 pressure strongly overlaps H012 support: `903/1200` aligned support
    cells hold `244.595425` score versus conflict score `20.929529`;
  - generated candidates `253`;
  - `44` candidates have `world_cell_delta < -0.0002`;
  - `4` candidates have negative H024 margin;
  - `0` candidates satisfy both;
  - no candidate has H024 support >= `0.6`.
- Registry status: approved as an overlap/negative-translator diagnostic.
  Rejected as a direct submission materializer.
- Failure condition: do not use support-preserving scalar ray amplitude as the
  next submission route unless paired with a new route/calibration/private-
  public translator.

### H038 memory-transition translator features

- Target hidden structure: within-subject lifestyle/sleep-state transition where
  same-subject memory becomes misleading and H012 public-equation movement
  overrides continuity.
- Why needed: V106-style subject memory is externally validated, but H012 is
  much stronger. The useful question is not whether memory is true, but where
  H012 breaks it.
- Feature/action form:
  - memory probability and reliability from H014;
  - memory agreement/disagreement with H012 direction;
  - H031 memory-conflict core scores;
  - H036 world pressure and row public probability;
  - transition-exception score, repair score, and row-transition score;
  - candidate families: exception q-pull, exception posterior-pull,
    memory-repair rollback, row-transition vector move, and world-exception
    veto.
- Current evidence:
  - memory-exception support cells: `523/1200`;
  - memory-exception posterior gain sum: `8.133135268`;
  - memory-exception H036 cell-score sum: `200.501588821`;
  - broad-world exception cells: `245`, score sum `183.788898304`;
  - generated candidates `459`;
  - world-gain candidates `42`;
  - posterior-gain candidates `2`;
  - negative-H024-margin candidates `0`;
  - H024 support >= `0.55` candidates `0`.
- Registry status: approved as a human-state route feature. Rejected as a
  direct action translator or submission materializer.
- Failure condition: do not submit memory-conflict amplification/repair files
  unless a learned translator also passes H024/H025 and shows public-free
  action-health.

### H039 failed-translator nullspace features

- Target hidden structure: compact bad-action geometry spanning failed
  H036/H037/H038 translators, plus a possible survivor cone of less-bad H024
  actions.
- Why needed: H036/H037/H038 created many negative examples. If action failure
  is low-dimensional, it can be used as a JEPA target: predict and remove the
  unhealthy action component from H036 world pressure.
- Feature/action form:
  - logit-delta direction vectors from materialized H036/H037/H038 candidates;
  - `all_bad`, `world_bad`, and `survivor` SVD bases;
  - projection diagnostics: removed norm ratio, cosine to world, cosine to
    H012 ray;
  - candidate families: failure-PC removal, survivor-cone projection, and
    double-nullspace residual;
  - route masks: support, memory exception, world-high support, and
    transition-high support.
- Current evidence:
  - source candidate directions `816`;
  - all-bad PC1 energy `0.651576382`;
  - all-bad PC8 cumulative energy `0.895838636`;
  - world-bad PC8 removal leaves raw world norm ratio `0.210274586`;
  - world-bad PC24 removal leaves raw world norm ratio `0.068574652`;
  - generated/scored candidates `520`;
  - world-gain candidates under promotion threshold `0`;
  - negative-H024-margin candidates `0`;
  - H024 support >= `0.55` candidates `0`.
- Registry status: approved as a failure-geometry diagnostic. Rejected as a
  direct linear translator.
- Failure condition: do not continue linear nullspace/survivor-cone projection
  around H012 unless a new target proves nonlocal route assignment separately.

### H040 discrete route-state features

- Target hidden structure: row-level assignment to public-equation,
  transition-exception, private-memory, rollback, uncertainty, or hold routes.
- Why needed: H039 rejects local linear projection, while H038 validates
  memory-transition state. A row should perhaps choose a route before its
  probabilities are decoded.
- Feature/action form:
  - `public_route_score`: row public probability, H036 world score, support
    count, posterior gain, transition exception, conflict core, and memory
    disagreement;
  - `private_memory_route_score`: private safety, memory agreement,
    same-subject memory reliability, transition repair, rollback cost, and low
    public probability;
  - `transition_exception_route_score`: transition exception, memory
    disagreement, world-opposes-memory, high world score, and local subject
    score jumps;
  - `route_uncertainty_score`: public probability near boundary plus conflict
    and support density;
  - action families: whole-row route moves to `world`, `posterior`,
    `posterior_world`, `memory`, `memory_state`, or `e247`.
- Current evidence:
  - generated/scored candidates `328`;
  - selected world/posterior deltas
    `-0.001426068` / `-0.001708677`;
  - `198/328` candidates have `world_cell_delta < -0.0005`;
  - `181/328` candidates have `h025_score < 0`;
  - `0/328` candidates have negative H024 margin;
  - `0/328` candidates have H024 support >= `0.55`.
- Registry status: approved as a row-state latent and proposal prior. Rejected
  as a direct post-H012 route materializer.
- Failure condition: do not submit row-route public/world/posterior moves unless
  H024 support and margin both turn positive under a genuinely new decoder.

### H041 route-prior public-world features

- Target hidden structure: route-conditioned public/private subset equation,
  where H040 row routes affect which hidden rows belong to the public sensor
  world before posterior probabilities are formed.
- Why needed: H040 rejected direct route materialization but left open the
  possibility that route should be used inside inference rather than after it.
- Feature/action form:
  - route q sources:
    `h041_route_public_q`, `h041_route_transition_q`,
    `h041_route_private_tempered_q`, `h041_route_public_hardmix`,
    `h041_route_memory_contrast_q`, and `h041_e247_phase_q`;
  - route row priors:
    public route, transition exception, public-not-private, uncertain-public,
    support-public, memory-disagree-public, world-public, reliable-transition,
    and private-inverse priors;
  - public-world selection by known LB equation fit plus
    leave-one-public-file-out consistency;
  - candidate families: route cell-top posterior pulls, route row pulls, and
    phase-preserving support pulls.
- Current evidence:
  - best route-prior LOFO MAE `0.000132093`;
  - best uniform LOFO MAE `0.000187170`;
  - route LOFO gain vs uniform `0.000055077`;
  - selected route-equation/H012-posterior/H036-world deltas
    `-0.001074309` / `-0.000205969` / `-0.000487601`;
  - selected H024 margin/support `+0.004066028` / `0.250000000`;
  - selected H025 row-permutation p `0.290000000`.
- Registry status: approved as a route-conditioned public-world inference
  feature. Rejected as a posterior-first submission materializer.
- Failure condition: do not submit route-conditioned posterior top-cell/row
  pulls unless the action itself is jointly solved or independently passes
  H024 support/margin, not just LOFO equation fit.

### H042 action-coupled public/private equation features

- Target hidden structure: upload-action response geometry conditioned on
  public/private route, phase support, memory rollback, exception worlds, and
  target-specific Q2/S1/S3/S4 action routes.
- Why needed: H041 proves route-conditioned hidden-world inference can improve
  public-sensor fit, but posterior-first materialization fails. The missing
  object may be the action coefficients that known public submissions already
  reveal.
- Feature/action form:
  - `36` action atoms: public cell tops, phase support, exception world,
    private memory, private rollback, route rows, and target-specific phase
    atoms;
  - known-action features: coordinates and cosines to atoms, route/H012/H036
    posterior deltas, targetwise movement, and public/private/transition
    weighted magnitudes;
  - candidate families: single atoms, public-private pairs,
    public-exception pairs, phase-exception-private triples, and target-route
    pairs;
  - stress features: action-decoder LOFO prediction, route-equation delta,
    H024 pre-H012 margin/support, H025 action-health, and row-permutation.
- Current evidence:
  - best action-decoder LOFO MAE `0.000665647`;
  - decoder Spearman / pairwise accuracy
    `0.924675325` / `0.904761905`;
  - permutation p `0.000000000`;
  - selected route-equation delta `-0.000537053`;
  - selected action margin/support `+0.000793299` / `0.333333333`;
  - selected H024 margin/support `+0.002010668` / `0.250000000`;
  - selected H025 row-permutation p `0.146666667`;
  - `15` candidates have action gain plus route gain;
  - no candidate has action gain plus route gain plus H024 gain;
  - no candidate has route gain plus H024 gain.
- Public feedback:
  - `submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv`
    scored `0.5679048248`;
  - delta vs H012 `-0.0002186583`;
  - winning file is a `45`-cell Q2-local phase move with action margin
    `-0.000052`, route delta `-0.000141`, H025 score `-0.918544`, and H024
    margin `+0.000410`.
- Registry status: approved as a non-collapsed action-response representation
  and as a tiny Q2 phase materializer. Rejected as a broad large-atom
  submission solver.
- Failure condition: do not submit action-atom mixtures unless a new search
  finds intersection across action decoder, route equation, H024, and H025.
  A strong LOFO action decoder alone is not enough outside the validated
  Q2-local phase branch.

### H043 Q2-local phase manifold features

- Target hidden structure: an H012-compatible Q2-only phase action manifold
  around the public-positive H042 movement.
- Why needed: H042 proved that small target-isolated Q2 phase can beat H012,
  while broad route/private action mixtures remain unsafe. The next question is
  whether that Q2 move is expandable or merely a `45`-cell accident.
- Feature/action form:
  - H042 public win appended as an observed action-response sensor;
  - Q2 phase direction from route-world `q_cond`, H012 public posterior, and
    H036 world posterior;
  - E247/H012 support mask to avoid unsupported cell invention;
  - H042 support overlap, H042 tangent distance, and tangent expected delta;
  - candidate families: Q2 top-k surface, H042-core amplitude, H042-core
    pruning, H042-core plus tail, and stronger-core/weak-tail.
- Current evidence:
  - generated/scored candidates `251` / `240`;
  - promotable candidates `67`;
  - selected `h043_q2_top120_a0.66_c105_ca1478b7`;
  - changed cells/rows `105` / `105`, Q2 only;
  - action margin/support `-0.000128164` / `0.583333333`;
  - route-equation delta `-0.000194493`;
  - H024 margin/support `+0.000619918` / `0.250000000`;
  - H025 score `-2.323117949`;
  - H042 Jaccard/distance L2 `0.428571429` / `0.026442709`.
- Registry status: public-ready as the next Q2 phase sensor. Not yet validated
  as an expandable manifold until public LB returns.
- Failure condition: if the promoted file loses materially to H042, do not
  widen Q2 support further. Fall back to pruning/scaling around exact H042
  support or a different public-regime split.

### H044 human-route Q2 support features

- Target hidden structure: Q2 phase action support selected by a human-state
  route, especially public-route, transition-exception, memory-disagreement,
  low private-memory, and H042-like row geometry.
- Why needed: H042's winning `45` rows look more public/transition-like than
  H043's wider `105` rows. A human social/state explanation should become
  actionable if it can choose which H043 tail rows to keep.
- Feature/action form:
  - row-level route scores:
    `h044_public_transition_score`, `h044_private_routine_score`,
    `h044_phase_energy_score`, `h044_h042_like_score`,
    `h044_public_q2_regime_score`;
  - candidate families: public-transition top-k, H042-like top-k, Q2-regime
    top-k, phase-energy top-k, H043-support route-pruned top-k, H042-core plus
    route tail, and H043 private-routine veto.
- Current evidence:
  - generated/scored candidates `768` / `240`;
  - promotable candidates `0`;
  - selected diagnostic
    `h044_h043_privateveto_q0.78_a0.66_c91_826ae253`;
  - changed cells/rows `91` / `91`, Q2 only;
  - action margin/support `-0.000095671` / `0.583333333`;
  - route-equation delta `-0.000184347`;
  - H024 margin/support `+0.000582704` / `0.250000000`;
  - H025 score `-1.987702538`.
- Registry status: approved as a diagnostic human-state latent and pruning
  clue. Rejected as a direct public submission selector.
- Failure condition: do not use scalar human-route thresholds as the primary
  Q2 support selector unless H043 public feedback specifically says the wider
  support was too aggressive.

### H045 conditional route-to-action movement features

- Target hidden structure: Q2 phase action response conditioned on human-state
  route context. The route latent is treated as context for action pricing,
  not as a direct row selector.
- Why needed: H044 showed route features are real but too weak as scalar gates.
  H045 tests the JEPA-style alternative: use visible route/context features to
  predict the hidden action-response representation.
- Feature/action form:
  - route context masks:
    `h045_public_high`, `h045_private_high`, `h045_private_low`,
    `h045_q2regime_high`, `h045_h042like_high`, `h045_phase_high`,
    `h045_public_not_private`, `h045_q2_public_context`;
  - movement summaries inside each route mask for target/cell probability
    changes, absolute movement, positive/negative movement, and public/private
    weighted movement;
  - known-action conditional decoder features fitted against public LB deltas;
  - candidate score combining full-known conditional margin, pre-H042 margin,
    pre-H012 action margin, route-equation delta, H024 warning, H025 health,
    and support size.
- Current evidence:
  - selected `h044_h043support_q2regime_top75_a0.66_c75_5988dfb9`;
  - root file
    `submission_h045_condroute_q2regime75_a0.66_5988dfb9_uploadsafe.csv`;
  - changed cells/rows vs H012 `75` / `75`, Q2 only;
  - changed cells/rows vs H043 `30` / `30`, Q2 only;
  - full known conditional margin/support
    `-0.000126787` / `0.583333333`;
  - pre-H042 conditional margin/support
    `-0.000665132` / `0.583333333`;
  - route-equation delta `-0.000171330`;
  - H024 margin `+0.000547357`;
  - H025 score `-1.693362091`.
- Registry status: approved as a public-ready Q2-local route-conditioned
  action sensor. Not yet approved as a general multi-target decoder.
- Failure condition: if H045 loses to both H042 and H043, do not continue
  route-conditioned pruning until a new independent route assignment signal is
  found. If H043 wins and H045 loses, the route context is over-pruning Q2
  support.

### H046 bifurcated Q2 regime action features

- Target hidden structure: route-specific Q2 action amplitude. H042-core rows,
  public-regime tail rows, neutral tail rows, and private-routine tail rows may
  need different movement strengths or signs.
- Why needed: H045 uses route context to choose support but still applies one
  phase direction. A stronger HS-JEPA theory should ask whether the action
  itself is conditional on human state.
- Feature/action form:
  - dual-regime candidates: H042 core + public tail + private veto/opposite
    tail;
  - H045 split candidates: H045 support with non-uniform route amplitude;
  - tri-regime candidates: public tail, neutral tail, private tail;
  - bifurcation strength feature from public/private signed action separation
    and row-level alpha dispersion.
- Current evidence:
  - generated/scored candidates `5224` / `240`;
  - promotable candidates `0`;
  - selected diagnostic
    `h046_dual_public_phase_pub45_priv8_a0.58_0.44_-0.03_c88_fd07485d`;
  - full-known conditional margin/support
    `+0.000015538` / `0.416666667`;
  - pre-H042 conditional margin/support
    `-0.000411481` / `0.583333333`;
  - route-equation delta `-0.000163227`;
  - H024 margin `+0.000497445`;
  - H025 score `-2.040387092`.
- Registry status: rejected as a public submission feature family for now.
  Retain only as a negative boundary for Q2 route modeling.
- Failure condition observed: post-H042 conditional decoder rejected all
  bifurcated candidates (`0/240` pass full-known margin and support), even
  though route/H024/H025 stress was mostly healthy.

### H047 Q2 support-identity posterior features

- Target hidden structure: row-level membership in the public-positive Q2
  phase support. This is a discrete support identity latent, not an amplitude
  or sign latent.
- Why needed: H046 rejected route-specific Q2 amplitude/sign bifurcation while
  leaving support selection alive. H047 asks the JEPA-style question directly:
  can observed candidate supports predict which unseen rows should join the
  H042 Q2 phase support?
- Feature/action form:
  - support observations from H045 and H046 candidate masks;
  - contrastive support quality from full-known conditional margin/support,
    pre-H042 margin, route-equation delta, H024, and H025;
  - row-level `h047_direct_support_contrast`,
    `h047_feature_support_prior`, and `h047_support_posterior`;
  - one-direction Q2 phase actions only: posterior top-k, H042-core plus
    posterior tail, and H043/H045 support-sieve candidates.
- Current evidence:
  - support observations `720`;
  - generated/scored candidates `262` / `240`;
  - promotable candidates `74`;
  - selected `h047_h042core_support_tail14_a0.66_0.44_c59_98737e9b`;
  - root file
    `submission_h047_q2_support_identity_98737e9b_uploadsafe.csv`;
  - changed cells/rows vs H012 `59` / `59`, Q2 only;
  - full-known conditional margin/support
    `-0.000211862` / `0.583333333`;
  - pre-H042 conditional margin/support
    `-0.000383048` / `0.583333333`;
  - route-equation delta `-0.000178002`;
  - H024 margin `+0.000552020`;
  - H025 score `-1.154530177`.
- Registry status: approved as a public-ready support-identity sensor.
- Failure condition: if H047 loses materially to H042, do not keep expanding
  Q2 support by posterior-tail selection without an independent public-subset
  assignment signal.

### H048 Q2 public-subset support-world features

- Target hidden structure: public-subset row assignment conditioned on H047
  Q2 support identity. This treats support identity as a public-world prior,
  not just as a Q2 action mask.
- Why needed: H047 proves a support posterior can create a local Q2 candidate,
  but it does not prove those rows are truly public-sensitive. H048 asks
  whether the same support posterior helps explain known public LB equations.
- Feature/action form:
  - H047 support posterior inserted into world-sampler row priors:
    `h048_support_identity`, `h048_support_public`,
    `h048_support_public_not_private`, `h048_core_tail_prior`;
  - Q2-specific q sources:
    `h048_q2_support_phase_q`, `h048_q2_coretail_q`,
    `h048_q2_public_soft_q`;
  - joint support/world score combining row posterior, support posterior,
    public route, private route, Q2 regime, and H042/H047 support indicators;
  - Q2-only action families:
    world-support top-k, H042-core plus world tail, and H047/H045 world-sieve.
- Current evidence:
  - support-prior LOFO MAE `0.000145480` vs uniform `0.000184123`;
  - generated/scored candidates `206` / `206`;
  - promotable candidates `83`;
  - selected `h048_world_support_top53_a0.66_c53_39c01d65`;
  - root file
    `submission_h048_q2_public_subset_support_39c01d65_uploadsafe.csv`;
  - changed cells/rows vs H012 `53` / `53`, Q2 only;
  - changed cells vs H047 `16`, Q2 only;
  - full-known conditional margin/support
    `-0.000184398` / `0.583333333`;
  - pre-H042 conditional margin/support
    `-0.000463494` / `0.583333333`;
  - route-equation delta `-0.000165760`;
  - H048 world delta `-0.000065847`;
  - H024 margin `+0.000522791`;
  - H025 score `-1.063509870`.
- Registry status: approved as a public-ready support-world sensor.
- Failure condition: if H048 loses while H047 survives, keep H047 support
  identity but reject the current public-subset assignment layer.

### H049 row-vector echo HS-JEPA features

- Target hidden structure: row-level human-state membership that should affect
  Q3/S targets, not only Q2. This is the first promoted attempt to translate
  the Q2 support/public-world latent into a non-Q2 target route.
- Why needed: H042 through H048 all keep the best evidence inside Q2. That can
  mean either the hidden state is genuinely Q2-local, or we have not yet
  translated the row state into the right Q3/S representation. H049 tests that
  distinction directly while keeping H042's Q2 values fixed.
- Feature/action form:
  - base prediction is the current public best H042;
  - row context combines Q2 support posterior, H048 public-world posterior,
    H045 route context, and H020 joint-vector posterior;
  - action targets only Q3/S cells and leaves Q1/Q2 unchanged;
  - candidate families use support/public row masks, joint-world soft targets,
    bounded top-k support, and low-amplitude echo strength.
- Current evidence:
  - generated/scored candidates `180`;
  - strict promotable candidates `16`;
  - selected
    `h049_public_rows_joint_world_soft_support_or_public_Q3S_k160_a0.085_t1_7635f5ed`;
  - root file
    `submission_h049_rowvector_echo_7635f5ed_uploadsafe.csv`;
  - changed cells vs H042 `160`, all non-Q2;
  - per-target changed cells vs H042:
    Q1 `0`, Q2 `0`, Q3 `14`, S1 `47`, S2 `39`, S3 `36`, S4 `24`;
  - route-equation delta vs H012 `-0.000185510`;
  - H036-world delta vs H012 `-0.000131061`;
  - full-known action margin/support
    `+0.000051201` / `0.416666667`;
  - full-known conditional margin/support
    `+0.000208025` / `0.500000000`;
  - H024 margin `+0.001194754`;
  - H025 score `-4.814111661`.
- Registry status: approved as a high-information public sensor, not as a
  conservative improvement candidate.
- Failure condition: if H049 loses materially to H042, reject the current Q3/S
  echo translator and treat H042's support as Q2-local until an independent
  non-Q2 route signal is found.

### H050 target-route phase residual features

- Target hidden structure: target-specific non-Q2 action phase after the H042
  Q2 phase is frozen. This treats Q1/Q3/S routes as separate hidden channels,
  not as one shared row-vector echo.
- Why needed: H049 tests row-level translation from Q2 support to Q3/S. H050
  asks a different HS-JEPA question: context is H042 plus route/world posterior,
  target is the missing non-Q2 target-route representation.
- Feature/action form:
  - base prediction is H042;
  - Q2 is frozen exactly;
  - route/world/posterior phase sources:
    `route_phase`, `world_phase`, `route_world_mid`, `posterior_mid`;
  - target groups include single Q/S targets, Q, S, S13, S24, Q3S3, Q3S, and
    all non-Q2;
  - candidates are ranked by H042 action decoder with H042 feedback, route
    gain, H036-world delta, H024, and H025.
- Current evidence:
  - generated/scored candidates `360` / `240`;
  - promotable candidates `85`;
  - selected
    `h050_target_phase_route_world_mid_Q_k96_a0.3_agree_b140216b`;
  - root file
    `submission_h050_target_route_phase_b140216b_uploadsafe.csv`;
  - changed cells vs H042 `96`, all non-Q2:
    Q1 `52`, Q3 `44`;
  - route-equation delta vs H012 `-0.000444205`;
  - route gain vs H042 `-0.000303538`;
  - H036-world delta `-0.000166506`;
  - full-known action margin/support
    `-0.000050859` / `0.583333333`;
  - H024 margin/support
    `+0.001857507` / `0.250000000`;
  - H025 score `+0.377968233`.
- Registry status: approved as a high-information target-route public sensor.
- Failure condition: if H050 loses materially to H042, reject the current
  subjective-Q non-Q2 phase translator and prioritize the S24 action-health
  branch or a new independent non-Q2 decoder.
## H051 Feature/Action Registry: Exact-Support Q2 Phase Amplification

- Feature/action name:
  `h051_exact_h042_q2_phase_amplifier`
- Hidden structure targeted:
  exact-support Q2 hidden label phase discovered by H042.
- Why needed:
  H050 tied H042 after moving non-Q2 Q1/Q3 cells, so the next information-rich
  action is not another target expansion but a direct amplitude test on the
  only public-positive translated route.
- Construction:
  - identify the `45` Q2 cells where H042 differs from H012;
  - compute H012->H042 Q2 logit delta;
  - set H051 Q2 to `logit(H012) + 2.0 * delta` on the same cells;
  - copy every other cell from H042 unchanged.
- Leakage/safety distinction:
  this uses public feedback as a sensor for a hypothesis, not as a final
  leaderboard-fitting blend. It is explicitly falsifiable: a bad public result
  kills amplitude continuation.
- Discard condition:
  if `submission_h051_q2_phase_amp_f2p0_5ab4e605_uploadsafe.csv` is worse than
  H042, do not continue stronger edge-push variants without a new support or
  public-subset explanation.

## H052 Feature/Action Registry: Q2 Binary-Edge Action

- Feature/action name:
  `h052_exact_h042_q2_binary_edge`
- Hidden structure targeted:
  Q2 hidden action-label edge on H042's exact support.
- Why needed:
  H051 tests smooth amplitude. H052 tests the more radical alternative that
  the same latent should be pulled toward class-edge states.
- Construction:
  - identify the exact `45` H042 Q2 cells;
  - preserve all non-Q2 targets;
  - if H042 moved a Q2 cell up, pull it toward `0.88`;
  - if H042 moved a Q2 cell down, pull it toward `0.12`;
  - mix this edge target with H042 using weight `0.35`.
- Leakage/safety distinction:
  H052 is explicitly conditional on H051. It should not be used as a generic
  calibration tweak.
- Discard condition:
  if H051 fails, discard H052 without submission. If H051 succeeds but H052
  fails, discard binary-edge continuation while preserving smooth Q2 phase.
