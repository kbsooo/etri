# Feature Registry

작성일: 2026-05-28

Feature는 "좋아 보이기 때문에 추가"하지 않는다. 각 feature family는 어떤 숨은 구조를 겨냥하는지, label signal인지 split signal인지, 폐기 조건이 무엇인지 함께 관리한다.

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

## Current Feature Policy

- Direct feature addition is paused unless it maps to a hypothesis and stress test.
- Direct JEPA residual probability movement is banned at raw/full amplitude. Only tiny scaled steps that pass broadness, bad-axis geometry, negative controls, context-alignment diagnostics, safety-context decoupling, public-sensor framing, pre-registered feedback decoding, critical-cell prior audit, rollback-intervention survival, rollback-overcorrection stress, anti-post-hoc public-feedback decoding, component-level damping checks, locked post-feedback interpretation, and E178 plateau-law survival are allowed. E166 is the raw broad-escape sensor; E167 adds the caveat that context-real is not safety-certified; E168-E169 refine that caveat by producing a context-high/veto repaired tensor; E170 adds that even this repaired tensor remains public hard-label-resolution limited; E171 adds that the broad body is visible-prior favorable but top critical cells are adverse; E172 shows the adverse visible-positive-loss tail can be damped without killing the broad body; E174 shows a subset of that damping can be reopened without losing the visible-tail guard; E175 fixes how that sharper bet must be interpreted; E176 shows Q2 should be slightly damped inside that reopened subset; E177 locks the E176 feedback bands; E178 explains why this still sits at the plateau: broad signal exists, but current public resolution is a few hard labels and current selectors are too coarse. Prefer E176 for the next risk-adjusted broad expected-score submission, E174 for max-edge contrast, E172 for lower-risk tail repair, and E169 only when the explicit goal is to observe the unrolled body-vs-tail split.
- The most promising public-relevant diagnostic is now the anchor-loss/binary-world geometry that selected `submission_mixmin_0c916bb4.csv`; E48 validates it as a public-sign feature family, not just a sensor label. It is still not private-safe certification or target-axis JEPA semantics. The next useful feature is not another S4/Q3 weight variant, OOF-local Q3/S4 winner, existing block/measurement candidate rescore, naive merge of pair-only and old-only shortlists, old-only Q3/raw05-drift sensor, amplitude-only S4/Q3 rescale, simple row-mask localization, unqualified larger sparse/minimax movement, inverse-LB prior fitting, subject-prior inverse ranking, a single binary inverse incumbent, a small binary world-pool sign readout, generic train-label plausibility gate, OOF selector-rank gate, movement-fingerprint predicted LB used as a score forecast, movement+axis predicted LB used as a score forecast, fixed-zero anchor kNN forecast used to rank near-A2C8 candidates, existing-universe rescore without new evidence, simple structured public-subset mask recovery, or same-summary Ridge block-rate regression. E39-E45 remain negative screens for selector calibration, and E46-E47 still say the 0.54 path requires better held-out block-rate/count representation. Post-E48 feature work must be mixmin-relative: preserve the validated anchor-loss/cancellation direction, reduce private-risk energy, and test whether new block-state context/target designs recover hidden rates instead of only perturbing row probabilities.

E49 makes the next feature policy narrower: start from subject-calendar mask context, but treat it as JEPA context/energy, not as a raw row-order feature dump. E50 makes it narrower again: calendar movement is not enough to rank public candidates because it fails to predict mixmin as best. E51 narrows it further: anchor-loss world aggregates plus calendar fingerprints are still not a transferable selector. E52 narrows it again: conditioning existing binary worlds on mixmin does not reveal a current replacement candidate. E53 narrows the block-rate/count branch: a simple calendar-flank count posterior is useful energy but not a candidate generator because strict donor exclusion fails pseudo-hidden recovery. E54 widens the representation evidence but narrows the candidate gate: raw overnight context recovers strict pseudo-hidden block state, yet its actual hidden-rate world is adverse for mixmin and regresses S3. E55 then narrows the translation hypothesis: simple Q/S target-rate projection cannot reconcile raw pseudo-hidden recovery, S3, and mixmin sign. E56 reopens hidden-world generation by producing coherent mixmin-hard raw posterior energy, but E57 closes direct posterior submission because actual-anchor safety gates are `0`. E58 closes the first simple anchor-constrained distillation attempt because best safe anchor deltas are below `1e-5`. E59 closes the within-block joint-pattern-only target as a candidate source: the joint structure is real but target-mismatched. E60 closes aggressive transition-residual hidden-sign movement as a candidate source: the sign is real-looking but calibration collapses. E62 closes simple transition-gated E56 teacher movement as a candidate source: the gate is interpretable but weaker than E58. E63 opens a useful direction validator but closes gradient consensus as a submission gate because the best anchor gain remains sub-margin. E64 closes scalar amplification of that validator because larger moves are uniformly anchor-adverse. E65 opens only a sub-margin near-zero targetwise pocket and points directly at Q2/S3 as conflict targets. E66 refines that target-conflict: Q2/S3 can be hidden/mean-favorable, but they expand public-compatible tail risk. E67 shows a first-order tail-neutral translator improves over broad masks, but margin gates remain `0`. E68 then validates many tail-gated Q2/S3 cells outside same-anchor construction, so the missing object is no longer independent validation alone. E69 closes global alpha over those cells. E70 keeps the consensus branch alive but not submission-ready: strict rows exist, yet only under `gate=none` and heldout-specific aggregation. E71 shows this is not merely a heldout-specific arithmetic trick, because one unified strict row survives, but deployable sign/agreement gates remain `0`. E72 then narrows the failure: sparse-magnitude `top_abs50` and `s3_only` gates can be deployable, while Q2-only and soft/sign agreement remain weak. E74 adds that the selected sparse gate is cell-subset stable, while alpha24 failure warns against uncontrolled amplitude. E75 adds that the amplitude boundary is target-specific: S3-heavy/Q2-low rows dominate deployable support and Q2-only remains dead. E76 adds that this target-asymmetric direction is subset-stable but exact universal `8/28` deployability is only partial. E77 then closes the tempting shortcut: source-subset posterior averaging does not repair exact-amplitude instability because safe Q2/S3-only movement is sub-margin and full posterior movement breaks combo-set/tail consistency. E78 closes the next shortcut: E76 deployable/non-deployable source-subset reliability masks create many deployable rows but no row that beats E75, so simple sign/consensus/excess/veto localization is not the missing law. E79 closes the handcrafted row/block/flank shortcut. E80/E81 close direct sparse-gate follow-up: the submitted E73 file is public-adverse and all-target contaminated, while pure E73 Q2/S3 remains sub-margin and inverse sign fails. E82 closes the wider pure-graft rescue: even E72/E75/E76 source grafts pass non-margin stress but fail margin. E83 shows that Q2/S3 energy can mark safe rows but does not by itself make broad structural movement safe; broad margin rows worsen Q2/S3/world or fail combo-set coverage. E84 shows that adding non-Q2S3 structural margin and Q2/S3 safety solves hidden/world/block stress but leaves a single inverse-top combo-set conflict. E85 then proves the first cheaper separation: target-axis pruning, especially keeping `S1,S2,S3`, resolves inverse-top while preserving the other combo worlds. E86 adds the source-stability layer: consensus across many strict target-pruned rows and source files strengthens the local edge without breaking hidden/world/block stress. E87 splits that source-consensus risk into Q2 add-back, shrink overstep, and inverse-top-prior geometry. E88 adds the public-movement attribution layer. E89 then turns that risk into a concrete gate: top-E72 cells can fall back from E86 to E85, giving a lower-contamination strict candidate. E90 adds the Pareto-knee layer: row-coherent fallback can retain more E86 structure than the minimum-contamination file while still being cleaner than E85/no-Q2. E91 adds a negative selector flag: known-LB regression remains invalid even after E72. E92 adds another negative selector flag: hidden-block posterior CE is E72-tainted and cannot rank submissions directly. E93 adds a third negative selector flag: train target-manifold consistency is also E72-tainted and cannot serve as the counter-gate. E94 adds the required hard-label tail flag: soft health can look best on E86 while hard-label tail risk is lower for E89/E85. E95 turns that flag into a local fallback gate that beats E89 on hard-tail and margin, while also showing non-strict tail minimization is a rollback trap. E96 adds the public-miss budget scenario energy, E97 validates E95 as public-positive, E98 adds the E95-updated known-LB selector collapse flag, E99 adds the E95-conditioned tail-transfer energy, E100 adds the E89 Q2/S3 diffuse-tail counterfactual energy, E101 adds the E95-relative Q2/S3 rollback energy, E102 shows the rollback cells are weakly edge-local but not block/subject-local, E103 shows that direct edge-local masks do not dominate the full E101 amplitude rollback, E104 shows E101 alpha `0.25` is a Pareto cliff rather than a coarse-grid accident, E105 shows E101's public fate is mostly a subject/block-local S3 hard-label condition rather than a global prior correction, E106 rejects subject-prior gating as a pre-feedback candidate generator, E107 turns the pending E101 result into a conditional branch map, E108 materializes the E101-win amplitude branch without changing the pre-feedback submission order, E109 closes same-line rescue for E101 tie/loss, E110 rejects the automatic non-active E89/graft fallback after a negative E101 result, E111 reframes the current frontier as target-axis hard-tail surgery, E112 separates S subject/block-state from Q temporal-state, E113 rejects visible raw context as a broad Q temporal rescue, E114 rejects raw context as E101 active-cell pre-validation, E115 confirms E101 has the highest actionable public-sensor information after that raw-support failure, E116 locks the post-E101 feedback decoder before the score is known, E117 closes the old-universe shortcut by showing that lower-tail E95-like neighbors are only E101/E85/E108-family files, E118 adds visible flank-transition support while keeping E101 uncertified because expected delta remains positive, E119 rejects turning that support into a pre-feedback flank-gated replacement because no row dominates E101, E120 applies the real E101 public `small_loss` feedback, E121 converts that score into a one-cell-scale S3 hard-label boundary, E122 shows existing visible priors explain but cannot exploit that boundary, and E123 rejects cross-target transition motif as the missing independent S3-cell sensor. A useful feature must now treat target-axis contamination, source-consensus stability, post-E86 risk decomposition, frontier-movement attribution, E72-cell fallback, E72 row-coherent Pareto fallback, known-LB selector collapse, hidden-block posterior taint, target-manifold taint, hard-label tail exposure, hard-tail localized fallback, public-miss budget robustness, E95-updated proxy collapse, E95-conditioned transfer, Q2/S3 diffuse-tail concentration, E95-relative rollback separation, edge-local active-cell energy, E101 flank-transition support but non-certification, E101 flank-gate replacement failure, E101 public small-loss boundary energy, exact small-loss inverse-posterior energy, independent-sensor boundary failure, transition-motif collapse energy, E103 edge-amplitude dominance failure, E104 amplitude Pareto-cliff risk, E105 public-label break-even, E106 subject-prior gate failure, E107 feedback-conditioning tension, E108 conditional materialization, E109 tie/loss active-label retention, E110 non-active tail isolation failure, E111 target-axis surgery, E112 S/Q axis split, E113 raw-context collapse warning, E114 raw-support failure, E115 actionable sensor information, E116 feedback decoder guardrails, and E117 neighborhood scarcity as separate energies.
