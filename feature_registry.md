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
- Adopt if: the E73 file improves public LB or a later public-independent selector predicts its sign while preserving the same hidden/world/block support.
- Drop if: public LB worsens, or if the only positive rows are local-combo artifacts with no public-subset-independent confirmation.
- Current evidence: E72 generated `4752` rows / `4752` unique predictions and found strict rows `21`, deployable non-`none` rows `10`, and loose rows `655`. `top_abs50` produced `7` deployable rows with best all delta `-1.05458e-5`; `s3_only` produced `3`; Q2-only produced none. E73 materialized the best `top_abs50` row as `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`, with hidden Q2/S3 mean improvement `-0.000391043`, world support `-0.000280957`, raw-energy q-p90 `-0.000159091`, and block win rate `0.722222`.
- Policy: add `q2_s3_sparse_gate_energy`. This is now the priority diagnostic submission branch after mixmin, not yet a confirmed feature family for production blending. The public observation must decide whether sparse magnitude is a real hidden-world gate or a local stress artifact.

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

## Current Feature Policy

- Direct feature addition is paused unless it maps to a hypothesis and stress test.
- Direct JEPA residual probability movement is banned until latent geometry passes.
- The most promising public-relevant diagnostic is now the anchor-loss/binary-world geometry that selected `submission_mixmin_0c916bb4.csv`; E48 validates it as a public-sign feature family, not just a sensor label. It is still not private-safe certification or target-axis JEPA semantics. The next useful feature is not another S4/Q3 weight variant, OOF-local Q3/S4 winner, existing block/measurement candidate rescore, naive merge of pair-only and old-only shortlists, old-only Q3/raw05-drift sensor, amplitude-only S4/Q3 rescale, simple row-mask localization, unqualified larger sparse/minimax movement, inverse-LB prior fitting, subject-prior inverse ranking, a single binary inverse incumbent, a small binary world-pool sign readout, generic train-label plausibility gate, OOF selector-rank gate, movement-fingerprint predicted LB used as a score forecast, movement+axis predicted LB used as a score forecast, fixed-zero anchor kNN forecast used to rank near-A2C8 candidates, existing-universe rescore without new evidence, simple structured public-subset mask recovery, or same-summary Ridge block-rate regression. E39-E45 remain negative screens for selector calibration, and E46-E47 still say the 0.54 path requires better held-out block-rate/count representation. Post-E48 feature work must be mixmin-relative: preserve the validated anchor-loss/cancellation direction, reduce private-risk energy, and test whether new block-state context/target designs recover hidden rates instead of only perturbing row probabilities.

E49 makes the next feature policy narrower: start from subject-calendar mask context, but treat it as JEPA context/energy, not as a raw row-order feature dump. E50 makes it narrower again: calendar movement is not enough to rank public candidates because it fails to predict mixmin as best. E51 narrows it further: anchor-loss world aggregates plus calendar fingerprints are still not a transferable selector. E52 narrows it again: conditioning existing binary worlds on mixmin does not reveal a current replacement candidate. E53 narrows the block-rate/count branch: a simple calendar-flank count posterior is useful energy but not a candidate generator because strict donor exclusion fails pseudo-hidden recovery. E54 widens the representation evidence but narrows the candidate gate: raw overnight context recovers strict pseudo-hidden block state, yet its actual hidden-rate world is adverse for mixmin and regresses S3. E55 then narrows the translation hypothesis: simple Q/S target-rate projection cannot reconcile raw pseudo-hidden recovery, S3, and mixmin sign. E56 reopens hidden-world generation by producing coherent mixmin-hard raw posterior energy, but E57 closes direct posterior submission because actual-anchor safety gates are `0`. E58 closes the first simple anchor-constrained distillation attempt because best safe anchor deltas are below `1e-5`. E59 closes the within-block joint-pattern-only target as a candidate source: the joint structure is real but target-mismatched. E60 closes aggressive transition-residual hidden-sign movement as a candidate source: the sign is real-looking but calibration collapses. E62 closes simple transition-gated E56 teacher movement as a candidate source: the gate is interpretable but weaker than E58. E63 opens a useful direction validator but closes gradient consensus as a submission gate because the best anchor gain remains sub-margin. E64 closes scalar amplification of that validator because larger moves are uniformly anchor-adverse. E65 opens only a sub-margin near-zero targetwise pocket and points directly at Q2/S3 as conflict targets. E66 refines that target-conflict: Q2/S3 can be hidden/mean-favorable, but they expand public-compatible tail risk. E67 shows a first-order tail-neutral translator improves over broad masks, but margin gates remain `0`. E68 then validates many tail-gated Q2/S3 cells outside same-anchor construction, so the missing object is no longer independent validation alone. E69 closes global alpha over those cells. E70 keeps the consensus branch alive but not submission-ready: strict rows exist, yet only under `gate=none` and heldout-specific aggregation. E71 shows this is not merely a heldout-specific arithmetic trick, because one unified strict row survives, but deployable sign/agreement gates remain `0`. E72 then narrows the failure: sparse-magnitude `top_abs50` and `s3_only` gates can be deployable, while Q2-only and soft/sign agreement remain weak. E74 adds that the selected sparse gate is cell-subset stable, while alpha24 failure warns against uncontrolled amplitude. E75 adds that the amplitude boundary is target-specific: S3-heavy/Q2-low rows dominate deployable support and Q2-only remains dead. E76 adds that this target-asymmetric direction is subset-stable but exact universal `8/28` deployability is only partial. E77 then closes the tempting shortcut: source-subset posterior averaging does not repair exact-amplitude instability because safe Q2/S3-only movement is sub-margin and full posterior movement breaks combo-set/tail consistency. E78 closes the next shortcut: E76 deployable/non-deployable source-subset reliability masks create many deployable rows but no row that beats E75, so simple sign/consensus/excess/veto localization is not the missing law. A useful feature must now come from public-tested sparse-magnitude consensus, unified rowwise/cellwise calibration-preserving target-specific amplitude over E68/E70/E71/E72/E74/E75/E76 strict cells, public-like combo-set/tail/row-block-localized amplitude, or transition/topology/public-disagreement structural targets that explicitly preserve row calibration, S3, consensus geometry, amplitude boundary, target asymmetry, exact-amplitude stability, and tail stability; not from target-rate smoothing, raw posterior averaging, source-subset posterior averaging, source-subset reliability masks, sub-margin teacher slicing, joint-pattern kNN rates, endpoint-residual hidden-sign rates, transition residual used as a simple post-hoc mask, gradient direction agreement alone, global scale increases, another tiny line search, target masks without tail-risk accounting, first-order anchor-tail gates alone, independently validated micro-cells without margin, global alpha over validated cells, heldout-specific consensus averaging, unified `gate=none` consensus, sign-agreement-only consensus gates, symmetric-only amplitude, universal target-asymmetric amplitude without energy conditioning, full-scope posterior movement with weak tail/set coverage, or bootstrap-best sparse subsets chosen only by local score.
