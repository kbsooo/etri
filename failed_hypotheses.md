# Failed Hypotheses

작성일: 2026-05-28

실패한 실험은 폐기물이 아니라 hidden structure를 좁히는 증거로 남긴다.

## FH01. Boundary copy solves hidden rows

- Failed hypothesis: nearby train labels can be copied/smoothed into hidden rows.
- Observed result: prev/next/both boundary copy was worse than subject prior under submission-like geometry.
- Why discard: it behaves like leakage-shaped overfit, not stable DGP signal.
- Implementation issue possible: low. Multiple boundary variants failed.
- Bottleneck implication: row-order exists, but not as direct label propagation.
- Do not repeat: simple boundary copy/smooth submit.

## FH02. Single feature thresholds reveal target rules

- Failed hypothesis: strong raw/MP feature stumps can directly predict targets.
- Observed result: single threshold stumps were worse than stage2 across targets.
- Why discard: residual correlations are weak priors, not direct deterministic rules.
- Implementation issue possible: medium but not worth direct submit.
- Bottleneck implication: feature signal must be aggregated into latent/calibration risk.
- Do not repeat: stump-like hand rules.

## FH03. Ordinal Q hard constraints improve public

- Failed hypothesis: Q1/Q2/Q3 ordinal/count structure can be enforced directly.
- Observed result: `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` public `0.5783033652`, worse than best by `0.000864044`.
- Why discard: hard target constraints likely miscalibrate hidden public subset.
- Implementation issue possible: possible target-specific tuning issue, but public signal is negative.
- Bottleneck implication: target dependency should be soft energy, not hard correction.
- Do not repeat: hard ordinal prior without anchor stress.

## FH04. Q2 JEPA direct latent correction is public-positive

- Failed hypothesis: Q2 JEPA latent can directly correct Q2 probabilities.
- Observed result: `submission_jepa_latent_q2_w0p45.csv` public `0.5798012862`.
- Why discard: direct movement loads bad public axis.
- Implementation issue possible: possible, but public gap is too large to treat as noise.
- Bottleneck implication: target-specific JEPA local gain is not enough.
- Do not repeat: Q2-only latent push without geometry gate.

## FH05. All-target JEPA latent residual OOF gain transfers

- Failed hypothesis: strong all-target OOF improvement means public-safe representation.
- Observed result: latent residual OOF around `0.560757`, but public residual probe `0.5812273278`.
- Why discard: local CV objective was misaligned with public hidden subset.
- Implementation issue possible: low to medium; nested guardrail also failed.
- Bottleneck implication: latent must be semantic/stress-stable, not just predictive.
- Do not repeat: direct residual graft from local CV.

## FH06. LeJEPA targetwise strict scale solves geometry

- Failed hypothesis: adding LeJEPA-style geometry regularization makes targetwise latent public-safe.
- Observed result: `submission_lejepa_targetwise_strict_best_scale0p5.csv` public `0.5802468192`.
- Why discard: implemented geometry did not align with public subset or target semantics.
- Implementation issue possible: yes, because LeJEPA idea may be under-translated. But this concrete branch is bad anchor.
- Bottleneck implication: geometry diagnostic must be measured, not assumed.
- Do not repeat: JEPA-branded direct blend without explicit latent health checks.

## FH07. Bad-axis projection alone unlocks frontier

- Failed hypothesis: remove known bad JEPA axes and large candidate pool will contain strict winner.
- Observed result: badaxis_lowenergy_jepa generated many candidates but strict resolved-better 0.
- Why discard: low bad-axis is necessary but not sufficient.
- Implementation issue possible: low. Universe audit agrees.
- Bottleneck implication: need positive direction, not only negative-axis avoidance.
- Do not repeat: low-bad-axis-only ranking.

## FH08. Hidden public localization can be directly bridged

- Failed hypothesis: inverse-local public subset direction can create submit-safe bridge.
- Observed result: hiddenloc bridge generated 1530 candidates, stress-scored 580, submit_gate 0.
- Why discard: local improvement conflicts with selector/bad-axis stress.
- Implementation issue possible: medium; inverse masks underidentified.
- Bottleneck implication: public localization exists but cannot yet be selected reliably.
- Do not repeat: high-localization candidates without selector agreement.

## FH09. More candidate generation is enough

- Failed hypothesis: enough blends/submissions will contain a reliable winner.
- Observed result: full universe audit over 15871 valid submissions found strict resolved-better 0.
- Why discard: candidate selection resolution is below candidate edge.
- Implementation issue possible: low for current candidate families; possible for new representation family.
- Bottleneck implication: selection and representation quality, not pool size.
- Do not repeat: brute-force micro-blend expansion.

## FH10. Current public proxy can rank tiny a2c8-scale deltas

- Failed hypothesis: public proxy can decide deltas around `0.0001`.
- Observed result: raw05-a2c8 public gap `0.000086986`, while best fixed LOOCV proxy MAE around `0.000546739`.
- Why discard: decision scale is below measurement error.
- Implementation issue possible: no; this is statistical underidentification.
- Bottleneck implication: submit confidence is impossible without stronger selector or larger safe movement.
- Do not repeat: treating proxy delta smaller than MAE as submit evidence.

## FH11. Existing label-flow/MP-count candidates are submit-safe as-is

- Failed hypothesis: transductive episode count and MP-count conditioning candidates already translate label-flow/block-rate semantic signal into public-safe submissions.
- Observed result: E10 scored 556 related submission files with public pairwise stress. `pair_submit_gate=0`, `pair_probe_gate=0`, `pair_control_better_than_a2c8_gate=0`; best p90 delta vs a2c8 was `+0.000125668`.
- Why discard: semantic latent exists, but the current probability translation moves in a direction pairwise public-risk models rate as worse than a2c8.
- Implementation issue possible: medium. The latent branch may still be useful, but not with the existing direct/blended submission files.
- Bottleneck implication: representation is not the only issue; translation/gating from representation to probability is the bottleneck.
- Do not repeat: submitting existing transductive/MP-count CSVs without a new gate.

## FH12. Gated label-flow currently produces a strict submit candidate

- Failed hypothesis: dependency-energy/raw05-gated label-flow movement is enough to create a strict submit-safe candidate above `a2c8`.
- Observed result: E11 generated and scored 7240 gated candidates. `pair_submit_gate=0`, `pair_control_better_than_a2c8_gate=50`, `pair_probe_gate=3263`, `pair_selector_conflict=0`; best p90 delta vs a2c8 was only `-0.000000687`.
- Why discard: the gate fixes the direction enough to create clean probes, but the expected edge remains far below selector/proxy uncertainty.
- Implementation issue possible: medium. The gate is deliberately conservative; larger targetwise movement or better row localization may still work.
- Bottleneck implication: translation is improving, but the current probability movement is not large enough to be decisionable.
- Do not repeat: treating `f1046674` or `ff8df011` as confident improvement submissions. They are public sensors unless a stronger stress gate is added.

## FH13. All-target label-flow amplification is the right translation

- Failed hypothesis: once label-flow gate is useful, amplifying all targets or broad target groups is the right way to create a submit candidate.
- Observed result: E12 targetwise scan showed S4 was the strongest safe atom and Q3/Q2-Q3 were secondary. Broad/all-target masks were weaker than S4/Q3-specific movement. E13 broad combos reached p90 `-0.000035162` but not strict submit.
- Why discard: useful correction is target-local, not all-target.
- Implementation issue possible: low for current donors. The targetwise contrast was clear.
- Bottleneck implication: hidden label-flow structure does not map uniformly to all seven targets; S4 objective signal and Q3 subjective/objective bridge carry the usable public-positive direction.
- Do not repeat: all-target label-flow amplification without targetwise stress.

## FH14. Pairwise-strict S4+Q3 label-flow candidates are submit-safe

- Failed hypothesis: the E14 focused S4+Q3 candidates that pass strict pairwise submit gate are robust enough to treat as frontier-challenge submissions.
- Observed result: E15 reviewed 163 label-flow candidates, including all 61 E14 pair-submit files. Independent survival was 0 and strict independent survival was 0. `6b9335b1` had pairwise p90 `-0.000065217` but old-selector p90 `+0.000675515`; `1bbfb735` had pairwise p90 `-0.000054316` but old-selector p90 `+0.000638679`. E16 then showed focused files have only pairwise full-fit better_rate `0.500000` and old hidden-subset better_rate `0.285714`. E17 audited the anchor gap: pairwise universe had 21 Q3/S4-shaped candidates but 0 with old-majority support; focused family had 163 pairwise-positive Q3/S4 candidates with old-majority 0; old-positive rescore had 97 old-majority candidates but Q3/S4-shaped 0.
- Why discard: the focused scan optimized the same pairwise selector used as its gate. The pairwise-improving direction is anti-aligned with older hidden-subset geometry: corr(pairwise p90 delta, old-selector p90 delta) `-0.881`. The support is not unanimous even within pairwise models.
- Implementation issue possible: medium. The old selector is also underidentified and conservative, so a public diagnostic could still falsify it. But local evidence is not strong enough to spend an improvement-oriented submission slot.
- Bottleneck implication: candidate selection/validation mismatch is the immediate bottleneck, not lack of S4/Q3 candidate generation.
- Do not repeat: promoting pairwise-focused candidates to submit priority without independent survival, an independent S4/Q3 anchor, or explicit public-sensor intent.

## FH15. Local OOF Q3/S4 winners can serve as the missing public anchor

- Failed hypothesis: the OOF archive contains an independent S4/Q3 validation source that can resolve the pairwise-vs-old selector conflict.
- Observed result: E18 scanned 5167 OOF files and found 1578 local-Q3/S4-strong candidates, but OOF anchor-like candidates were 0. E19 directly rescored the top 399 local Q3/S4 OOF candidates: pair p90 negative 0, pair majority 0, old majority 0, pair probe/control/submit 0, q3s4_shape70 0.
- Why discard: local Q3/S4 logloss gains are not aligned with public-sensitive selector geometry and are mostly broad Q3-dominant/public-mask-aware moves.
- Implementation issue possible: low for this question. The top local candidates were resolved to CSVs and directly scored by both selector families.
- Bottleneck implication: validation mismatch is stronger than expected. The missing anchor is not in existing OOF validation either.
- Do not repeat: selecting public submissions from OOF-local Q3/S4 improvement without pairwise and old selector agreement.

## FH16. Existing block/measurement candidates contain the missing large safe branch

- Failed hypothesis: block-scale JEPA, hidden-block sequence/rateprobe, raw05-blockcount, public-block, or pre-sleep measurement candidates already contain a larger low-bad-axis movement that can beat a2c8 once rescored correctly.
- Observed result: E20 rescored 3800 non-anchor candidates. pair p90 negative `0`, pair majority `52`, old-majority `3`, two-selector majority `0`, pair submit/control/probe `0/0/63`. There were 2505 large low-bad movement candidates, but large-lowbad two-selector support was `0`.
- Why discard: movement scale and low bad-axis are not enough. The candidates do not cross the sign boundary versus a2c8 under pairwise p90, and the few old-majority files have weak pairwise support.
- Implementation issue possible: low for existing CSVs; medium for future representation design. The audit covered the main generated block/hidden-block/presleep/raw05-block families, but a new representation could still work.
- Bottleneck implication: the plateau is not caused by failing to retrieve an old block/measurement candidate. It is still selector-resolvable movement or public-subset underidentification.
- Do not repeat: promoting old block/measurement/presleep files based on low bad-axis, local OOF/CV, or raw05 proximity without two-selector support.

## FH17. Merging current selector shortlists will reveal a robust candidate

- Failed hypothesis: the current pairwise-positive, old-positive, OOF-local, and block/measurement rescored universes contain a rare but valid intersection candidate if merged and deduplicated.
- Observed result: E21 merged scored candidates from broad pairwise universe, focused label-flow review, old-positive rescore, OOF-top rescore, and block/measurement rescore. The result was pair-only `465`, old-only `97`, pair-probe-not-majority `56`, two-selector majority `0`, strict candidate shape `0`.
- Why discard: pairwise and old hidden-subset support are not two noisy views around the same candidate cluster. They favor different movement manifolds: S4/Q3-heavy pair-only versus Q3/raw05-drift old-only.
- Implementation issue possible: low for the merge question. The source score files were already generated by direct selector scoring and the audit only classifies their overlap.
- Bottleneck implication: current candidate ranking is not recoverable by a better survival-score formula over existing rows. The selector disagreement itself must be explained or measured.
- Do not repeat: weighted averaging of pairwise and old selector ranks, or promoting a candidate because it is near the top of one selector and merely tolerable under the other.

## FH18. Old-only Q3/raw05-drift should be the next public sensor

- Failed hypothesis: because old hidden-subset stress vetoed focused S4/Q3 candidates, an old-only Q3/raw05-drift candidate should be the next public diagnostic.
- Observed result: E22 compared selector reliability on known public anchors. Pairwise public-order selector passed `33/36` models and got the raw05 direction correct at rate `0.916667`. Old hidden-subset selector passed `0/7` models and got the raw05 direction correct at rate `0.0`, over-endorsing raw05-like geometry even though raw05 public `0.5775263072` is worse than A2C8 `0.5774393210`.
- Why discard: old-only support is partly redundant with a known public-negative raw05 direction. It can remain a veto/caution signal, but it should not choose the next sensor when the question is maximum information per public slot.
- Implementation issue possible: medium. The old hidden-subset selector may still capture some private-like or alternate subset geometry, but it is not reliable enough to dominate next-sensor priority.
- Bottleneck implication: the immediate bottleneck is selector calibration, not simply choosing the stricter selector. Known-anchor reliability must be part of the gate.
- Do not repeat: submitting an old-only Q3/raw05-drift candidate before testing the conservative pair-only S4/Q3 diagnostic, unless the explicit experiment is to retest old hidden-subset geometry despite known raw05 weakness.

## FH19. Scaling down S4/Q3 movement resolves selector disagreement

- Failed hypothesis: the pairwise-vs-old conflict for S4/Q3 label-flow candidates is mainly caused by movement amplitude, so smaller logit-space movement should preserve pairwise signal and recover old hidden-subset support.
- Observed result: E23 generated 108 A2C8-to-`1bbfb735`/`6b9335b1` scale/mask variants. Pair p90 was negative across all mask families, but two-selector majority was `0` everywhere. The best balanced lower-risk sensor had pair p90 `-0.000034496`, old p90 `+0.000571958`, old scenario beat rate `0.277992`, and movement `0.003931`.
- Why discard: scaling reduces old p90 but does not change old majority support. The selectors disagree on direction/world, not just on amplitude.
- Implementation issue possible: low for the interpolation question. The generated files are deterministic logit-space blends from A2C8 to the two focused sensors and were scored by both existing selector families.
- Bottleneck implication: candidate selection cannot be fixed by gentle shrinkage of the same pair-only direction. Need a new anchor, new selector, or a representation that lands in a different sign-consistent direction.
- Do not repeat: more fine-grained scales around the same S4/Q3 direction unless a public sensor result changes the selector calibration picture.

## FH20. Simple row localization resolves S4/Q3 selector disagreement

- Failed hypothesis: pairwise S4/Q3 label-flow movement is public-positive only on a hidden subject/date/block/phase/energy subset, and old hidden-subset stress vetoes it because the movement is applied too broadly.
- Observed result: E24 generated 960 localized A2C8-to-`1bbfb735`/`6b9335b1` variants across subject, subject complement, global date bin, subject phase, date block, date block complement, delta-energy, S4 sign, calendar, and subject-energy masks. Pair p90 was negative for 807 candidates, but old-majority was `0` and two-selector majority was `0`. The only loose localized candidates were eight `id02_b02` date-block files with pair p90 around `-0.0000002`, old p90 around `+0.000580`, old beat rate `0.413127`, and movement around `1e-5`.
- Why discard: localization can preserve pairwise support, but it does not move the old selector across the majority boundary. The tiny `id02_b02` signal is below public readability and still old-negative.
- Implementation issue possible: medium. The tested masks are simple handcrafted DGP candidates; a learned row gate might still exist, but it needs a new anchor or validation target. More handcrafted sweeps around the same direction are low value.
- Bottleneck implication: the S4/Q3 conflict is not explained by applying the right target movement to the wrong simple row subset. The current bottleneck remains selector-resolvable direction or a new latent/anchor source.
- Do not repeat: subject/date/block/phase/energy/sign sweeps around `1bbfb735` or `6b9335b1` unless a public sensor result or new representation changes the selector calibration picture.

## FH21. Newer large direction probes pass the strict pairwise/old gate

- Failed hypothesis: the current mixmin/direns/sparseladder/target-ablation probes are large enough and locally robust enough to produce a selector-resolvable improvement over a2c8 under the same strict stress used for S4/Q3 label-flow candidates.
- Observed result: E25 scored 22 priority direction probes. Pair p90 negative `0`, pair majority `0`, old-majority `0`, two-selector majority `0`, submit-shape `0`. The nearest inverse7blend file still had pair p90 `+0.000122038` and old beat rate `0.003861`; mixmin/direns/sparseladder files had pair p90 roughly `+0.000835` to `+0.000960`.
- Why discard: honest-CV, actual-anchor, and combo-stress evidence does not survive the pairwise/old hidden-public selector gate. This does not prove the public LB will reject them, but it does prove they are not strict-survival candidates.
- Implementation issue possible: medium. The pairwise/old selectors are themselves underidentified; E25 is a reconciliation test, not a public LB measurement. A public score-probe can still be informative if explicitly framed as testing actual-anchor/combo stress against selector veto.
- Bottleneck implication: the 0.54 bottleneck is not solved by simply increasing movement scale through sparse/minimax mixture. Selector choice and hidden-public subset identification remain central.
- Do not repeat: promoting mixmin/direns files as stable submissions without saying which selector worldview is being tested.

## FH22. Known public LB inverse fitting can rank current candidates

- Failed hypothesis: the eight known public LB observations constrain the hidden public labels/subset strongly enough to determine whether current unobserved candidates beat a2c8.
- Observed result: E26 matched all known public LBs exactly under an all-test soft-label LP and under an arbitrary cell-mixture LP. All-test target prior ranges were nearly full `[0, 1]`; cell-mixture subject mass was `[0, 1]` for every subject. Delta ranges for eight unobserved candidates crossed zero under all-test soft labels, cell-mixture, and train target prevalence bands `±0.05`, `±0.10`, `±0.20`.
- Why discard: the inverse problem is massively underdetermined. The known LBs are compatible with hidden worlds where the same candidate improves and worlds where it worsens.
- Implementation issue possible: low for the underidentification claim, medium for realism. The LP uses relaxed labels and cell weights, so it does not model the exact binary public set; however, adding train-prior bands still leaves signs open. The result is a lower-bound proof of ambiguity, not a public-set reconstruction.
- Bottleneck implication: public LB cannot be used as a standalone optimizer or prior-tweaker. It can only adjudicate a predeclared structural hypothesis through a new public observation.
- Do not repeat: inverse-LB ranking of candidates without a new structural constraint or additional public observations.

## FH23. Train global and subject-target priors collapse inverse-LB ambiguity

- Failed hypothesis: E26 is underidentified mainly because it ignores hidden subject/user identity; adding train global prevalence and subject-target prior bands should make current candidate signs identifiable.
- Observed result: E27 tested seven all-test inverse scenarios with global target bands and subject-target bands. Every scenario matched the 8 known public LB anchors with minimum slack `0`, but all unobserved candidate-scenario cells still crossed zero (`56/56`). One-sided improvement cells were `0`. Even the tight `global_t010_subject_t010` prior left `1bbfb735` at `[-0.003706960, +0.002332888]`, 0.65 sensor at `[-0.002441019, +0.001484882]`, and mixmin at `[-0.010891932, +0.009106607]`.
- Why discard: plausible subject priors do not remove enough feasible hidden-public worlds to rank submissions. The ambiguity is not just missing subject identity in the inverse model.
- Implementation issue possible: medium. These are relaxed soft-label LPs and subject priors are broad bands from train; exact binary public subset constraints could behave differently. But as a low-cost structural-prior test, this directly falsifies using subject prior as the next ranking gate.
- Bottleneck implication: validation/public-subset mismatch and candidate selection remain stronger than target prior mismatch. A useful next constraint must come from a new public observation, a binary/exact public-set assumption, or a learned latent-world gate with independent evidence.
- Do not repeat: using train subject-target prior bands as a standalone public-LB inverse ranker for current candidates.

## FH24. Binary all-test inverse stress can rank current candidates

- Failed hypothesis: forcing all hidden test labels to be binary will remove the relaxed-LP ambiguity and make current candidate signs submission-rankable.
- Observed result: E28 solved binary-label MILP stresses with 1750 binary variables. All fit solves hit time limits, but incumbents were informative. A tight subject-prior binary world fit known LBs with max residual `0.000061242`, below the raw05-a2c8 gap `0.000086986`, while no-prior/global-only worlds were less precise. Candidate range MILPs did not produce one-sided improvement evidence. Under no-prior, `6b9335b1` had both improvement and degradation feasible from incumbents; tight subject-prior range MILPs produced no candidate incumbents within the short range time limit.
- Why discard: binary exactness improves realism but not current decision quality. The optimization is brittle, time-limited, and gives no validated one-sided improvement for representative candidates.
- Implementation issue possible: high. A better MILP search, saved incumbent pool, exact public subset cardinality, or binary row-subset model could change the picture. E28 is not a proof that binary constraints are useless; it is a proof that the current binary inverse stress is not ready as a submission gate.
- Bottleneck implication: public-subset identification remains open, but the immediate bottleneck is still selector/candidate ranking. Exact-label constraints alone do not create a usable 0.54 path.
- Do not repeat: using a single binary inverse incumbent, or a time-limited MILP range without independent validation, to justify a public submission.

## FH25. Small binary world pool can rank submissions

- Failed hypothesis: sampling a small pool of binary hidden-label worlds under tight subject priors is enough to identify the next submission family.
- Observed result: E29 solved 15 slack/candidate/random MILP objectives and found 15 unique binary incumbents. Only one incumbent was frontier-scale by max residual <= raw05-a2c8 public gap. Across all incumbents, mixmin had better_rate `0.866667` and inverse7 `0.733333`, while pair-only S4/Q3 sensors were `0.266667-0.333333`. In the only frontier-scale world, mixmin and inverse7 were better than a2c8, while the S4/Q3 pair sensors were worse.
- Why discard: the directional clue is too sample-dependent. One frontier-scale binary world cannot establish a stable hidden-public distribution, especially with all MILPs ending by time limit.
- Implementation issue possible: high. A larger frontier-filtered incumbent pool, slack-first random objectives, exact public subset/cardinality constraints, or a learned latent-world gate may make this line useful.
- Bottleneck implication: binary exactness may help choose between selector worldviews, but the current pool still shows candidate-selection uncertainty rather than resolving it.
- Do not repeat: treating E29's mixmin/inverse7 sign as a strict submission gate. Use it only as a high-risk public-probe prior or as motivation for a larger frontier-world audit.

## FH26. Frontier-box binary world pool certifies mixmin/inverse7

- Failed hypothesis: once every known-public residual is forced below the raw05-a2c8 gap, binary hidden-label worlds will make the correct candidate family one-sided.
- Observed result: E30 found 29 frontier-scale incumbents and 28 unique worlds under tight subject priors and per-anchor slack upper bounds. Non-candidate objectives strongly favored mixmin (`19/19`) and inverse7 (`18/19`), while pair-only S4/Q3 sensors were below half support. However candidate-max objectives still found frontier-compatible worlds where mixmin was worse by `+0.008774` and inverse7 by `+0.002782`.
- Why discard: the frontier-box constraint is strong enough to generate many realistic exact-label worlds, but not strong enough to identify a unique public world or one-sided candidate sign.
- Implementation issue possible: medium. Candidate-max worlds may be adversarial and less likely than random worlds, but there is no current external evidence to downweight them safely.
- Bottleneck implication: the binary-world hypothesis now helps prioritize public probes, but still does not close the validation/public-subset mismatch.
- Do not repeat: calling mixmin/inverse7 validated because random frontier-box worlds favor them. They remain high-risk worldview probes until a new public observation or independent latent-world gate downweights the adverse worlds.

## FH27. Generic train-label geometry can downweight adverse binary worlds

- Failed hypothesis: the frontier-box worlds where mixmin/inverse7 lose are adversarial artifacts that can be rejected by train-only target, subject, dependency, and temporal geometry.
- Observed result: E31 scored all E30 worlds with target-prior, subject-target, pairwise co-occurrence, correlation, row-cardinality, flip-rate, run-length, and edge-continuity features. Random+fit worlds supported mixmin `19/19`, but the two mixmin-adverse worlds were plausibility ranks `1` and `2`.
- Why discard: the adverse worlds are not geometry outliers under the available train-label dynamics. They are actually the closest worlds under this generic plausibility score.
- Implementation issue possible: medium. The energy is generic and train-only; a more specific hidden-public subset model could still reject these worlds.
- Bottleneck implication: the missing constraint is not broad label plausibility. It is public subset identity, a new public observation, or a sharper latent-world gate.
- Do not repeat: certifying mixmin by saying the adverse binary worlds are unrealistic under ordinary train label dynamics.

## FH28. Known-anchor loss geometry certifies mixmin

- Failed hypothesis: once known-public anchor per-target loss decomposition assigns adverse binary worlds high energy, mixmin can be promoted from high-risk probe to strict improvement candidate.
- Observed result: E32 scored 29 E30 frontier-box worlds. Low-anchor-energy bands strongly supported mixmin and inverse7: half `15/15`, quarter `7/7`, and low-anchor-energy random+fit `12/12`. The two mixmin-adverse worlds were high-anchor-energy ranks `26` and `28`. E33 then omitted each known public anchor in turn; mixmin stayed negative in every low-energy-half and low-energy-quarter LOO band, and no adverse world entered any LOO low-energy half.
- Why discard: this is strong diagnostic evidence, but not certification. The gate is derived from known public anchor decompositions, so LOO stability proves it is not one-anchor fragile but cannot prove that the next public/private subset follows the same loss geometry.
- Implementation issue possible: medium. The E32/E33 implementations directly use saved E30 worlds and known-anchor losses, but still lack an out-of-anchor validation set. A new public observation or independent anchor is needed to test whether `anchor_energy` generalizes.
- Bottleneck implication: candidate selection is improving but remains unresolved. E32 makes mixmin the most information-rich high-risk public sensor under the binary/actual-anchor worldview; it does not produce a strict 0.54-path submission.
- Do not repeat: describing `submission_mixmin_0c916bb4.csv` as validated or safe. If it is submitted, label it as a predeclared high-risk test of anchor-loss/binary-world geometry.
- E48 update: the public test succeeded. `submission_mixmin_0c916bb4.csv` scored `0.5763066405`, beating previous best by `0.0011326805`. Therefore this failed hypothesis should now be read narrowly: E32/E33 did not certify private safety or a 0.54 path, but it did identify a public-relevant candidate family.

## FH29. Anchor-loss support proves target-axis semantic alignment

- Failed hypothesis: E32/E33 support for mixmin means the candidate is aligned with the moved target axes of known public anchors in a JEPA-style semantic sense.
- Observed result: E34 permuted moved-target weights within each anchor row 500 times while preserving per-target losses and cancellation. Mixmin remained one-sided in `500/500` low-half and low-quarter permutations. Component ablations also kept mixmin support. Family isolation showed medium non-JEPA anchors alone are sufficient, while bad-JEPA anchors alone fail.
- Why discard: the signal does not depend on exact target-axis movement alignment. It is better explained as broad known-anchor loss/cancellation geometry, especially from medium non-JEPA anchors.
- Implementation issue possible: low for this falsification. The permutation explicitly breaks target-axis weight semantics while preserving the loss surface; support remaining intact directly weakens the target-axis interpretation.
- Bottleneck implication: JEPA-style target representation has not yet produced a certified semantic axis for submission. The current mixmin probe is a public-anchor geometry test, not a semantic latent proof.
- Do not repeat: claiming that E32/E33 validate a JEPA target-axis semantic representation without a stronger target-axis-sensitive stress.

## FH30. Existing independent evidence certifies mixmin as a normal submission

- Failed hypothesis: E32-E34 anchor-loss support for `analysis_outputs/submission_mixmin_0c916bb4.csv` is backed by enough out-of-anchor evidence to promote it from high-risk public sensor to normal improvement candidate.
- Observed result: E35 audited 5 candidate sensors and found normal submit gates passing `0`. Mixmin has honest CV mean/worst `-0.000951963` / `-0.000695966`, low-half anchor-loss better_rate `1.0`, low-half max delta `-0.000537096`, and LOO worst max delta `-0.000315338`. But pairwise p90 is `+0.000879200`, old-selector p90 is `+0.001041933`, and selector hard veto remains.
- Why discard: the strongest mixmin evidence is still known-public/anchor-derived or quasi-public. Honest CV is supportive but not enough to override the public-selector veto. There is no current independent validation source that proves the anchor-loss/binary-world gate generalizes to the next public/private subset.
- Implementation issue possible: medium. E35 is an evidence audit over existing artifacts, not a new public observation. A new public sensor or genuinely independent anchor could still validate mixmin later.
- Bottleneck implication: candidate selection remains unresolved. E35 changes sensor priority, not submission safety: mixmin is now the most information-rich high-risk worldview probe, while `1bbfb735` is a lower-risk selector-disambiguation sensor.
- Do not repeat: calling mixmin safe, validated, or normal-submit-ready without either a new public observation, a new independent anchor, or a local gate that makes pair/old selector conflict disappear.
- E48 update: the missing public observation arrived and validated mixmin on public LB. The old statement remains valid only for pre-public certification and unknown private safety; it is no longer valid as a reason to demote mixmin below a2c8.

## FH31. Raw observed structure independently certifies mixmin

- Failed hypothesis: if mixmin is the right binary/actual-anchor worldview probe, train-derived subject/date/raw-feature neighborhoods should independently support its movement versus A2C8.
- Observed result: E36 built 10 pseudo-label sources from raw observed structure: subject mean, same-subject temporal KNN k3/k7, all-sensor KNN k5/k15, cross-subject KNN k15, count/coverage KNN, sensor-stat KNN, and KMeans raw-feature cluster priors k12/k24. Mixmin improved only `5/10` sources, with mean soft LogLoss delta `+0.000065107` and worst delta `+0.000498574`. Inverse7 improved `10/10` sources, with mean delta `-0.000705727` and worst delta `-0.000507826`.
- Why discard: the first non-public raw-structure stress does not support mixmin as an independent validation source. Mixmin's strongest evidence remains anchor-loss/binary-world geometry, not observed raw neighborhood geometry.
- Implementation issue possible: medium. Pseudo-labels are imperfect and may favor smoother train-like structure rather than the public subset. But the source diversity and negative inverse7 result across all sources are strong enough to reject "raw structure certifies mixmin" for the current candidate file.
- Bottleneck implication: the bottleneck is not solved by adding a raw-structure confirmation stamp to mixmin. There are at least two still-conflicting latent probes: mixmin for anchor-loss worldview, inverse7 for raw-structure bridge. Candidate selection remains unresolved.
- Do not repeat: citing raw observed structure as evidence for submitting mixmin. Use raw-structure pseudo-label support to design inverse7/mixmin scale-blend reconciliation, and keep inverse7 as a bridge hypothesis rather than a certified submission.

## FH32. Inverse7 scale/blend resolves selector veto

- Failed hypothesis: because inverse7 has full raw-structure pseudo-label support and is also supported by low-anchor-energy binary worlds, a smaller inverse7 movement or inverse7/mixmin blend should preserve raw+anchor support while reducing pairwise/old selector veto.
- Observed result: E37 generated 22 logit-space scale/blend variants from A2C8 toward inverse7, mixmin, and inverse7/mixmin directions. Raw support gates were `14`, and anchor low-half+quarter gates were `22`, but two-selector majority was `0` and strict bridge gates were `0`. Best-ranked `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv` had raw support_rate `1.0`, raw mean delta `-0.000181991`, low-anchor-half better_rate `1.0`, but pair p90 `+0.000035423`, old p90 `+0.000587512`, old beat-rate `0.007722`, and selector hard veto `True`.
- Why discard: the failure is not an amplitude-only problem. Raw pseudo-label and anchor-loss support can be made to agree across many scales, but the same candidates remain outside the selector-supported public-risk manifold.
- Implementation issue possible: low to medium. The scan is deterministic and reuses the same E36/E32/E25 selector machinery. It does not prove that no nonlinear learned gate can reconcile inverse7, but it falsifies simple logit scaling and linear mixmin blending.
- Bottleneck implication: candidate selection/public subset identity is still the bottleneck. The next step should not be more inverse7 scale sweeps; it should be selector/worldview calibration, a genuinely new independent validation target, or a predeclared public sensor.
- Do not repeat: spending time on finer inverse7/mixmin amplitude grids unless a new public observation or a new selector target changes the conflict.

## FH33. Worldview discriminability reveals a normal submission

- Failed hypothesis: once all current evidence sources are joined, one candidate will emerge as both high-information and normal-submit-safe.
- Observed result: E38 audited 10 candidates across raw-structure, anchor-loss, pairwise selector, old selector, and honest-CV views. normal-submit candidates were `0`; public-sensor candidates were `10`. The top information sensor was `mixmin_0c916` with score `3.355110`, but its raw/pair/old verdicts remain adverse. Inverse7 bridge variants preserve raw+anchor support but remain selector-vetoed, and S4/Q3 pair sensors remain anchor/old-vetoed.
- Why discard: information value is not safety. E38 can rank diagnostic public questions, but every lane still contains an unresolved veto from at least one stress family.
- Implementation issue possible: low. E38 is a deterministic evidence join and does not create new models; it may miss a not-yet-generated candidate, but it correctly rejects the existing candidate set as normal-submit-safe.
- Bottleneck implication: candidate selection is still the bottleneck, not candidate-table organization. The next work needs a new independent selector target, a new public observation, or a representation that makes a larger sign-consistent movement.
- Do not repeat: treating sensor information score as survival score or claiming `mixmin_0c916` is safe because it is the most informative diagnostic.
- E48 update: the information score correctly selected the most valuable public sensor. It was not a full survival score, but it did identify the new public frontier. Future failed-hypothesis wording should distinguish "not private-certified" from "not worth public testing."

## FH34. OOF archive calibrates public selector identity

- Failed hypothesis: the broad train OOF archive can serve as an independent local selector target for ranking current public-sensor candidates.
- Observed result: E39 scored `4172` OOF rows (`4171` unique prediction hashes) against final9 OOF across label-free future-tail, train/test-domain-like, density, missingness, subject, date, and random subsets. It found many locally stable files: strict OOF selector gates `1311` and conservative gates `1115`. Known-public sign versus final9 matched for stage2 and ordinal (`1.0`), but known-public pairwise rank agreement was `0.0`: OOF ranked ordinal better (`full_delta -0.016400`, stress p90 `-0.010581`) than stage2 (`full_delta -0.010773`, stress p90 `-0.005761`), while public LB ranks stage2 better (`0.5779449757` vs `0.5783033652`).
- Why discard: sign agreement is too weak for submission selection. The actual decision is ranking among public-positive candidates, and OOF reverses that ordering on the two known nonbaseline public observations with matched OOF files.
- Implementation issue possible: medium. The baseline is final9 OOF rather than A2C8 OOF, and OOF folds may not match the competition public split. But that is exactly the point: the available OOF archive is not a trustworthy public-world selector.
- Bottleneck implication: validation mismatch is a primary plateau component. Local OOF stability can demote unstable candidates, but it does not resolve the hidden-public selector/worldview conflict.
- Do not repeat: promoting candidates because they pass OOF stress gates, or treating OOF-local rank as a substitute for public-observation consistency.

## FH35. Test movement fingerprint certifies public selector identity

- Failed hypothesis: label-free test movement anatomy relative to A2C8 is sufficient to rank public candidates safely.
- Observed result: E40 built target, subject, row-order, raw-domain, and combined probability/logit/entropy movement fingerprints. Four views passed a loose selector gate and correctly recovered stage2 < ordinal. The combined view had LOOCV MAE `0.000781461`, pairwise rank accuracy `0.821429`, and permutation-null rank p-value `0.004`. But strict selector views were `0`: A2C8 was not predicted best under leave-one-anchor-out, and bad JEPA anchor severity was heavily underpredicted (`q2_jepa_bad` predicted around `+0.00022` vs actual `+0.00236`; all-target JEPA residual around `+0.00127` vs actual `+0.00379`).
- Why discard: movement anatomy captures some public-order geometry but misses label/loss risk. A selector that cannot price known bad JEPA failures cannot certify an unobserved candidate, even if it ranks stage2/ordinal correctly.
- Implementation issue possible: medium. The kNN selector is intentionally simple and uses only eight known anchors; a richer model could overfit easily. The failure is still informative because the missing signal is exactly the bad-axis/loss geometry that has repeatedly caused public failures.
- Bottleneck implication: a pure movement-fingerprint selector is not the missing validation target. The useful next selector must combine movement anatomy with anchor-loss/bad-axis geometry, or be validated by a new public observation.
- Do not repeat: using E40 predicted public LB values as leaderboard forecasts. They are loose diagnostic priors only.

## FH36. Movement plus bad-axis geometry certifies public selector identity

- Failed hypothesis: E40 failed mainly because it omitted bad-axis direction geometry; adding logit-space cosine/projection against known raw, medium, and bad public-anchor movements should turn movement anatomy into a usable selector.
- Observed result: E41 built compact movement, axis-group, axis-named, and combined views with LOO-safe axis removal for the held-out anchor. Strict selector views were `0` and loose selector views were `0`. `axis_group` partially repaired bad-anchor severity with mean underprediction `0.000898399`, pairwise rank accuracy `0.785714`, null rank p `0.014`, and correct stage2/ordinal order, but LOOCV MAE was `0.000854918` and A2C8 was predicted as `+0.001475508` worse in leave-one-out. `axis_named` had MAE `0.000827696` but failed rank accuracy `0.571429`, stage2/ordinal order, and bad-anchor underprediction `0.001412567`.
- Why discard: bad-axis geometry fixes only one symptom. It does not recover the current-best zero anchor or stable public ranking, and named axes behave like anchor-identity overfit rather than a transferable selector.
- Implementation issue possible: medium. The kNN selector has only eight public anchors and LOO is harsh for the A2C8 zero point. But this is exactly why E41 cannot be promoted: if the result depends on treating A2C8 as an in-sample known point, it is not out-of-anchor selector certification.
- Bottleneck implication: the missing object is not another movement/cosine feature. It is either an independent selector calibration target, a principled current-best anchor model, or an actual public sensor observation.
- Do not repeat: using movement+bad-axis predicted public LB values as forecasts, or doing another small axis-feature tweak without a new validation target.

## FH37. Fixed-zero A2C8 calibration certifies movement-axis selector

- Failed hypothesis: E41's A2C8 failure was mainly a harsh LOO artifact; if A2C8 is kept as a known zero anchor, the movement+bad-axis selector should become usable for ranking near-frontier candidates.
- Observed result: E42 kept A2C8 fixed at zero and held out each nonbaseline anchor. Fixed-zero gates were `0` and usable zero-anchor gates were `0`. The best `axis_group` view had improved nonbaseline ordering with MAE `0.000766262`, rank accuracy `0.857143`, Spearman `0.821429`, stage2/ordinal order correct, raw05 predicted best nonbaseline, and null rank p `0.006`. But raw05 gap/MAE was only `0.113520`, best unobserved advantage/MAE was only `0.065408`, trajectory monotonicity was `0.428571`, and zero-neighborhood collapse warning was true.
- Why discard: fixing A2C8 turns the selector into a coarse nonbaseline ranker, not a frontier-resolution tool. It can separate bad anchors from medium/good anchors, but its error is far larger than the `0.0000869862` raw05-A2C8 gap and far larger than the predicted `0.000037-0.000050` edge of the pair sensors it ranks above raw05.
- Implementation issue possible: medium. The anchor count is still tiny, and kNN may be underpowered. But that is exactly the current reality: without a new independent selector target or a public observation, fixed-zero calibration cannot justify a normal submission.
- Bottleneck implication: the plateau is not explained by an overly harsh A2C8 LOO condition alone. The immediate blocker is selector resolution: current local selectors cannot read candidate movements at the scale needed to beat `0.577439` reliably.
- Do not repeat: submitting `pair_sensor_1bb_s0p65`, `1bb`, or `6b` because a fixed-zero axis view predicts them slightly better than raw05. Those advantages are smaller than selector error by more than an order of magnitude.

## FH38. Current selectors can certify near-frontier micro-edges

- Failed hypothesis: among pairwise public-order selectors, old hidden-subset stress, movement fingerprints, bad-axis geometry, and fixed-zero calibration, at least one selector should have enough resolution to certify a normal near-frontier submission.
- Observed result: E43 compared selector errors and candidate edges to the raw05-A2C8 public gap `0.0000869862`. Selector frontier-resolution gates were `0`, candidates certified better than A2C8 were `0`, and candidates certified better than raw05 were `0`. The best selector was pairwise public-order with best LOO error `0.000218288`, raw05-gap/error ratio `0.398493`, and best L2O error `0.000415499`. E40/E41/E42 best raw05-gap/error ratios were only `0.111312`, `0.105094`, and `0.113520`.
- Why discard: even the strongest current selector is too noisy for the public edge being optimized. Favorable candidate rows are smaller than the selector's demonstrated error on known public anchors, so they cannot be promoted from sensor to improvement candidate.
- Implementation issue possible: low to medium. E43 is an audit of existing selector outputs, so it cannot discover a new selector. But it correctly bounds the current selector stack and makes the error-margin requirement explicit.
- Bottleneck implication: candidate selection and public subset/worldview uncertainty dominate the 0.577439 plateau. To move toward 0.54, the next useful branch needs either sub-gap selector resolution, a larger sign-consistent movement, or a deliberate public sensor observation.
- Do not repeat: submitting micro-edge candidates because their mean or p90 selector delta is slightly negative. Error-margin certification is now a hard normal-submission requirement.

## FH39. Existing scored universe hides a larger low-risk candidate

- Failed hypothesis: even if near-frontier micro-edges are below selector resolution, the existing scored candidate universe may contain a larger pairwise-public edge that survives low-bad-axis, raw05-compatibility, and two-selector stress.
- Observed result: E44 normalized 29 score tables into 69,869 rows and 48,088 unique files. Pair-negative files were `12,309`, but files with pair edge greater than raw05-A2C8 gap were `0`, files with pair edge greater than the E43 best selector error `0.000218288` were `0`, large-pair low-bad files were `0`, and normal large-safe files were `0`. The best pair edge was `0.000073768`, only `0.337941` of selector error and `0.848048` of raw05 gap. The 21 any-edge-above-selector files were raw/anchor conflict rows such as inverse7/mixmin, not pairwise-supported safe candidates.
- Why discard: the current universe has many favorable rows, but not at a magnitude that current selectors can read. Larger favorable signals are exactly the previously diagnosed worldview conflict: raw-structure or anchor-loss support against pair/old selector veto.
- Implementation issue possible: low to medium. E44 is a census of existing score tables, so it cannot discover a candidate absent from those tables or a new selector. But it is strong evidence against spending more time re-ranking/rescoring the current files as if a hidden safe submission is already present.
- Bottleneck implication: the normal-submit bottleneck is not just poor ranking of existing candidates. It is either selector resolution, missing independent public-world target, or failure to generate a larger sign-consistent movement.
- Do not repeat: another broad existing-CSV rescore without a new evidence source. Future work must introduce a new independent selector target, a new representation family, or explicitly frame the next public file as a sensor.

## FH40. Simple structured public subset is the missing selector target

- Failed hypothesis: the public LB subset is dominated by a simple subject/order/date/raw-domain mask, and that mask can be recovered locally well enough to become an independent selector target.
- Observed result: E45 tested 145 predeclared masks across subject, subject complement/group, key-order prefix/suffix/window/mod, per-subject head/mid/tail, calendar/date/dow/month, raw-domain logistic/density/missingness/cluster, and random controls. Selector-scale gates were `0`; strict sub-gap gates were `0`. The best mask was `global_key_order/suffix_frac0.20` with LOO MAE `0.000429528`, max abs `0.00129817`, MAE/raw05-gap ratio `4.937886`, and MAE/selector-error ratio `1.967712`. Feasible ranges had mean widths around `0.04`, so they contained known anchors only because they were too wide to rank candidates.
- Why discard: exact public-LB inverse fits are easy, but held-out-anchor resolution is not. Simple masks may describe some public-order signal, but not at the precision needed to beat the current best or rank unobserved candidates.
- Implementation issue possible: medium. The mask family is broad but not exhaustive, and the minimum-deviation prior may not be the true public world. The failure is still actionable because the tested route was the cheap, recoverable version of the public-subset hypothesis.
- Bottleneck implication: public subset mismatch remains plausible, but it is not recoverable as an obvious subject/order/date/raw-domain mask. The missing object is still a sharper selector/worldview target, a larger sign-consistent movement, or a deliberate public sensor.
- Do not repeat: using simple structured-mask inverse fits as public LB forecasts or candidate rankers without a new anchor/target that reduces LOO error below the raw05-A2C8 gap.

## FH41. Existing row/context heuristics can close the block-rate oracle gap

- Failed hypothesis: because the train/test split is block-interleaved and most hidden blocks have nearby train context, row-order Markov transitions, endpoint flanks, one-feature thresholds, or simple public masks should recover enough hidden block-rate state to approach the `0.517878` oracle.
- Observed result: E46 consolidated the relevant evidence. The validation block-rate oracle is `0.517878` and the temporal-to-oracle gap is `0.106888`, but full subject identity explains only `0.291286` of that gap. Best Markov is worse than temporal by `+0.002998`, nested single-feature threshold is worse by `+0.044275`, endpoint pseudo-hidden reconstruction gains only `0.003252` over subject mean, and the best simple structured public mask LOO MAE is `0.000429528`.
- Why discard: context is present but not interpreted. `26/36` submission blocks have two train flanks, yet endpoint propagation and row-state transitions do not recover the hidden block-rate vector. The useful latent target is block-rate/count representation, not direct row labels.
- Implementation issue possible: medium. E46 is a synthesis over existing experiments, not a new neural block-context model. A stronger context model may still work, but it must be evaluated as held-out block-rate vector prediction rather than another heuristic smoother.
- Bottleneck implication: 0.54 is structurally possible but blocked by hidden block-state identification. Current submission candidates are sensors, not improvement claims, until a representation recovers material oracle headroom or a public observation resolves the worldview.
- Do not repeat: simple Markov/HMM label transitions, endpoint copy/smoothing, one-feature threshold searches, or structured public-mask inverse fitting as if they were enough. The next attempt must build a fold-safe JEPA-style context-to-block-rate target and stress its residual/energy.

## FH42. Current block-summary Ridge context recovers the hidden block-rate state

- Failed hypothesis: if the missing state is block-level, the existing fold-safe block summaries should already contain enough signal for a Ridge context-to-rate head to recover useful oracle headroom.
- Observed result: E47 trained fixed Ridge heads from label-context, sensor-value, missingness, and combined block summaries to held-out block-rate vectors. The best 25% row blend was `label_context_ridge = 0.623260`, a `-0.001505` row-level delta, but it recovered only `0.014083` of the temporal-to-oracle gap and had direct block weighted LogLoss `0.635888`, worse than temporal block context `0.623448`. `sensor_values_ridge` was worse by row blend (`+0.000660`) and block-rate loss (`0.657811`).
- Why discard: the test was designed around the JEPA target representation itself. A model that worsens block-rate loss while slightly improving a row blend is not learning the hidden block state; it is applying a weak calibration/shrinkage perturbation.
- Implementation issue possible: medium. Ridge plus block summaries may be too simple, and raw overnight sequence tokens or discrete count targets may still work. But repeating the same summary/Ridge family is unlikely to change the conclusion because the direct target loss failed.
- Bottleneck implication: the hidden block-state path is still live, but the current observable summary representation is insufficient. The problem is not just needing a target head on existing block features; it needs a different context/target construction or a sharper selector/worldview anchor.
- Do not repeat: same-summary block-rate Ridge regressors or row-blend promotion from them. Future attempts must beat temporal block weighted LogLoss and recover material oracle headroom before becoming submission candidates.

## FH43. Calendar-mask movement alone certifies the mixmin-relative selector

- Failed hypothesis: once mixmin is added as a known public anchor, target/subject/calendar-run movement features should explain why mixmin is public-best and become the next selector gate.
- Observed result: E50 ran `analysis_outputs/post_mixmin_calendar_selector.py` over target/prior, calendar, subject, and subject-calendar views. Strict selector views were `0` and loose selector views were `0`. The best `subject_calendar` view had LOOCV MAE `0.000884106`, pairwise rank accuracy `0.833333`, Spearman `0.833333`, and bad-tail order correct, but it predicted held-out mixmin delta `0.00135162` instead of `0`; `mixmin_predicted_best` and `mixmin_error_below_edge` were both false for every tested view.
- Why discard: the view captures coarse public-order structure but prices mixmin like a raw05/a2c8-like neighbor. It does not explain the actual public frontier edge, and its held-out mixmin error is larger than the mixmin-a2c8 public edge.
- Implementation issue possible: medium. The selector is deliberately simple kNN with few known anchors, and richer models could overfit the same small anchor set. The failure is still actionable because the tested claim was the cheap, falsifiable version: calendar movement alone should be enough if H48 immediately solved the selector problem.
- Bottleneck implication: subject-calendar topology is real context, not sufficient selector identity. The missing object is probably the interaction between calendar holes and anchor-loss/binary-world geometry, or an actual held-out block-rate/count target representation.
- Do not repeat: using E50 predicted public scores as LB forecasts, submitting calendar-position tweaks, or treating calendar masks as a standalone public-subset prior. Use them only as context/energy until they pass block-rate or anchor-loss stress.

## FH44. Anchor-loss world geometry plus calendar context certifies the mixmin-relative selector

- Failed hypothesis: the E32/E38 anchor-loss/binary-world signal that selected mixmin should become a transferable known-anchor selector once it is combined with E49/E50 calendar context.
- Observed result: E51 ran `analysis_outputs/post_mixmin_anchor_calendar_selector.py` with LOO-safe world-energy scoring. Strict selector views were `0` and loose selector views were `0`. Best view `anchor_residual` had LOOCV MAE `0.000835516`, pairwise rank accuracy `0.750000`, Spearman `0.633333`, and bad-tail order correct, but it predicted held-out mixmin delta `0.00241739` instead of `0`. It also failed a2c8/raw05 order. Adding calendar context did not rescue it; `contextall_anchor_residual` had MAE `0.000889706` and still failed mixmin-best.
- Why discard: E32/E38 worked as a worldview sensor over candidate signs inside binary worlds, not as a smooth metric for kNN over submission files. When mixmin is held out, its anchor-world features look closer to worse anchors than to the public-best state.
- Implementation issue possible: medium. The kNN selector and aggregate world features are simple, and the binary worlds were generated before mixmin was a known constraint. But this is exactly the falsified claim: the existing anchor-loss geometry plus calendar context is not enough to certify a post-mixmin selector.
- Bottleneck implication: the immediate blocker is translation of public-relevant hidden-world evidence into a reusable local selector. The next branch should either build a real calendar-flank block-rate/count target or regenerate binary worlds with mixmin as a constraint and evaluate candidate signs under that updated world family.
- Do not repeat: another small kNN/feature concatenation over known submission anchors. If anchor-loss is used next, it should be a constrained hidden-world feasibility stress, not a predicted-public-LB regressor.

## FH45. Existing candidates beat mixmin once binary worlds are conditioned on mixmin

- Failed hypothesis: after mixmin becomes an observed public anchor, the existing inverse7/raw-bridge/pair/JEPA-bridge candidate pool should contain at least one file that is one-sided better than mixmin under mixmin-compatible E30/E32 binary worlds.
- Observed result: E52 ran `analysis_outputs/post_mixmin_binary_world_sign_stress.py`. It conditioned the E30/E32 world family on actual mixmin delta `-0.0011326805` using raw05-a2c8 gap units, then scored `158` curated candidates versus mixmin. Strict better-than-mixmin gates were `0`; loose gates were `0`; near-tie gates were `1`. The only non-duplicate near-tie, `analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv`, had mixmin-fit-gap better_rate `0.2`, median delta `+0.000034`, max delta `+0.000048`, and postmix-energy-quarter better_rate `0.285714`, median delta `+0.000009`.
- Why discard: the sign is not one-sided and not even median-improving. It is close enough to mixmin to be a diagnostic equivalent, but the adverse max delta is positive and the better_rate is far below any reasonable submission gate.
- Implementation issue possible: medium. E52 reuses the pre-mixmin E30 world pool rather than regenerating MILP worlds with mixmin as a hard constraint, so a fresh constrained world family could differ. But the tested claim was narrower and actionable: no existing candidate should be submitted merely because it looks mixmin-adjacent under the current binary-world pool.
- Bottleneck implication: the next obstacle is not ranking the existing candidate table after adding mixmin. The current frontier is a local optimum for the tested world family. A real next candidate needs new hidden-state information or new world generation, not another bridge rescore.
- Do not repeat: submitting `bridge_blend_m0p75_s1p25`, inverse7 scale variants, pair sensors, or selected JEPA bridge files as mixmin replacements based only on existing E30/E32 world signs. They need either fresh mixmin-hard MILP support or block-rate/count target evidence.

## FH46. Simple calendar-flank count posterior is a submit-safe mixmin explanation

- Failed hypothesis: labeled calendar flanks plus block length and donor count signatures should recover hidden block target count/rate state well enough to generate a mixmin-relative submission or directly explain mixmin's public edge.
- Observed result: E53 ran `analysis_outputs/calendar_flank_block_count_state_probe.py`. On `369` pseudo-hidden train blocks, `calendar_count_local` improved weighted row LogLoss by `-0.005266` versus subject mean, but the strict subject-excluded version worsened it by `+0.001434`. Strict improved Q1 `-0.011907`, Q2 `-0.029170`, and Q3 `-0.011743`, but worsened S1 `+0.001126`, S2 `+0.024074`, S3 `+0.034293`, and S4 `+0.003363`. On `36` real hidden blocks, strict predicted rates gave only a weak expected mixmin advantage over a2c8, weighted delta `-0.000179`; the local version was adverse at `+0.000250`.
- Why discard: the pseudo-hidden improvement is mostly the local same-subject path, not the strict transferable path. The actual hidden alignment is too small and target-mismatched: it supports S3/S2/Q2 but hurts S1/Q1/Q3/S4. That is not a coherent enough latent to move probabilities safely.
- Implementation issue possible: medium. The posterior is intentionally simple and does not yet use raw overnight sensor context, richer sequence motifs, or Q/S target-dependency manifolds. But the rejected claim is specifically the simple calendar-flank count posterior as the next submission source.
- Bottleneck implication: subject-calendar block topology is real, but its directly recoverable count-state signal is below candidate-generation quality. The branch now needs either richer raw context, a better target-dependency representation, or a newly generated mixmin-hard binary world family.
- Do not repeat: converting `calendar_count_local` or `calendar_count_strict` hidden rates into row-level submission tweaks. Use them as energy/gating diagnostics only until a strict fold-safe representation recovers pseudo-hidden block state and target alignment simultaneously.

## FH47. Raw overnight strict block-state posterior is a direct mixmin submission source

- Failed hypothesis: adding raw overnight context to the calendar-flank count-state posterior should both recover pseudo-hidden block state and explain mixmin's actual hidden-block advantage, making it a direct source for the next probability movement.
- Observed result: E54 found strong strict pseudo-hidden recovery: `night_phone_rawctx_strict_k8_a24` improved weighted row LogLoss by `-0.007733` versus subject mean, with broad gains on Q1/Q2/Q3/S1/S2/S4. But the same method regressed S3 by `+0.007802` in pseudo-hidden target stress and made mixmin worse than a2c8 under actual hidden-block predicted rates (`+0.000311`). The strongest actual hidden mixmin alignment remained the weaker `calendar_count_strict` signal at `-0.000179`.
- Why discard: representation existence and public-aligned translation are different claims. E54 proves a real strict raw overnight block-state latent exists, but it fails the mixmin-sign gate and has a target-specific S3 conflict. Direct row movement from this posterior would bet against the current public frontier's observed hidden-world direction.
- Implementation issue possible: medium. The kNN posterior and PCA block aggregation are intentionally simple, and raw context may still help after target-dependency/S3 correction or in a hard-constrained binary-world generator. The discarded claim is only the direct submission-source version.
- Bottleneck implication: the bottleneck is not pure representation/capacity absence. It is alignment: strict pseudo-hidden block-state recovery can improve while the public/mixmin hidden-world sign worsens.
- Do not repeat: submitting raw overnight block-rate posterior movement, or treating strict pseudo-hidden improvement alone as enough. Future use should be as `raw_overnight_block_state_energy`, S3 conflict diagnostic, or feasibility prior inside a mixmin-hard world model.

## FH48. Simple target-rate dependency projection repairs raw overnight block state

- Failed hypothesis: the E54 raw overnight latent is structurally right, but its S3/mixmin failure is just a simple target-rate manifold violation that can be repaired by projecting each target from the other Q/S target rates.
- Observed result: E55 tested `225` kNN/Ridge target-dependency projections and simple S3 replacements. Joint gates were `0`. The best pseudo-hidden method, `raw_phone_s3_subject_w1p00`, improved raw by `-0.001115` and fixed S3 versus subject mean, but hidden mixmin delta stayed adverse at `+0.000319`. The best hidden-sign method, `raw_phone_td_ridge_groupcross_all_k0_a8_w0.75`, produced hidden mixmin delta `-0.000414` but destroyed pseudo-hidden validity: LogLoss `0.727319`, raw delta `+0.122051`, S3 delta `+0.207892`.
- Why discard: the tested target-dependency projections split the objectives instead of reconciling them. S3 repair does not imply mixmin-public alignment, and hidden sign flips can be achieved only by projections that fail the validation world.
- Implementation issue possible: medium. The projection uses true donor block-rate contexts and raw predicted query contexts, so a richer learned representation could still work. But the rejected claim is specifically the simple Q/S rate-manifold translator.
- Bottleneck implication: raw representation and public alignment are separated at a deeper level than pairwise target dependencies. The next branch needs mixmin-hard hidden-world constraints or a structural block target, not another post-hoc target smoothing pass.
- Do not repeat: S3-only subject/calendar replacement, kNN target-rate projection, or Ridge target-rate projection as a submission source unless a new stress shows simultaneous pseudo-hidden validity and hidden mixmin sign.

## FH49. Mixmin-hard raw posterior is directly submit-safe

- Failed hypothesis: because E56 regenerated binary worlds with mixmin as a hard observed constraint and produced posterior world-LOO strict gates, the resulting posterior can be submitted directly as the next frontier candidate.
- Observed result: E57 scored `15` posterior/reference variants and found joint safety gates `0`. Mixmin actual-anchor score was `0.577734`. The safest posterior, `posterior_all_w0.05`, still scored worse than mixmin by `+0.000123`. The E56 selected diagnostic `posterior_raw_energy_quarter_w0.28` / `submission_mixhard_rawposterior_af1502f9.csv` scored worse by `+0.020381` and moved mean abs logit `0.381359` away from mixmin.
- Why discard: E56 world coherence is not the same as independent public-anchor calibration. The internally best posterior appears to overfit the generated world family or move along a public-anchor-adverse direction.
- Implementation issue possible: medium. The generated worlds and posterior may still be valuable as a teacher or energy, and the actual-anchor proxy is not the true public LB. The discarded claim is specifically direct posterior submission without anchor-constrained distillation.
- Bottleneck implication: the bottleneck is probability translation and public-anchor geometry, not hidden-world generation alone. A world model can be coherent yet unsafe when converted to row probabilities.
- Do not repeat: submitting E56 posterior variants or any mixmin-hard world average unless it first beats mixmin under independent anchor stress and stays within a small movement guard.

## FH50. Simple anchor-constrained E56 posterior distillation is submit-safe

- Failed hypothesis: E56 posterior is too large as a full average, but a simple distillation over confident cells, target masks, row gates, caps, and small weights should produce a mixmin-relative submission candidate.
- Observed result: E58 generated `104727` latent-gated candidates and actual-anchor scored `1200`; E61 then fixed a sorted-prefilter score-index mismatch with stable `pred_index` and reran the probe. Corrected toward-teacher candidates had `126/900` sign-level anchor improvements and all `900` passed world/movement guards, but eligible submission gates were `0` after requiring anchor margin `< -1e-5`. Best toward-teacher delta was only `-0.000004081`. Reverse controls had no world guards and best anchor delta `-0.0000000126`.
- Why discard: the apparent safe direction is below selector/public-sensor resolution. It is not large enough to distinguish signal from anchor-proxy noise or justify a public slot.
- Implementation issue possible: medium. The candidate grid is simple and may miss nonlinear structural target representations. The discarded claim is only that simple gated distillation is enough.
- Bottleneck implication: E56 energy can be made non-adverse near mixmin, but not useful at frontier scale. The next path needs a structural block target or an independent non-anchor validation signal, not finer slicing of the same teacher grid.
- Do not repeat: using sub-`1e-5` actual-anchor improvements as submission evidence, or treating sign-level anchor improvements as sufficient without a margin.

## FH51. Within-block joint label-pattern target is a submit-safe structural representation

- Failed hypothesis: seven marginal target rates are the wrong target, and predicting a 128-state within-block Q/S label-pattern distribution will expose the public-aligned hidden block representation.
- Observed result: E59 tested `216` structural kNN methods plus baselines. Joint structure was clearly learnable: `139/216` structural methods improved pattern NLL versus raw independent marginals, and `198/216` had own-margin joint gain. But row LogLoss improvements versus raw were `0`, and joint gates were `0`. The best structural method, `struct_raw_calendar_subject_fbsubject_k16_a12_w0.35`, improved pattern NLL by `-0.062594` but worsened row LogLoss by `+0.003678`, S3 versus subject by `+0.002727`, and hidden mixmin sign by `+0.000304`. The best hidden-sign method, `struct_raw_subject_fbraw_k8_a4_w1.00`, had hidden mixmin delta `-0.000367` but worsened row LogLoss by `+0.042230` and S3 by `+0.078145`.
- Why discard: the structural target recovered joint co-occurrence but not submission-relevant marginal calibration. The target can be geometrically meaningful while still being the wrong latent for LogLoss and mixmin-relative public movement.
- Implementation issue possible: medium. The representation was a strict kNN pattern posterior with independent fallback, not a learned transition model. The discarded claim is only within-block joint labels as the next direct candidate source.
- Bottleneck implication: "more structural than marginal rates" is necessary but insufficient. The missing structure likely involves block transitions, calendar topology, hidden-run identity, or E56 public-world energy, not just within-block co-occurrence.
- Do not repeat: building a submission from E59 pattern-derived marginal rates, or treating pattern NLL gains as proof of public-aligned improvement. Future structural targets need row LogLoss, S3, and hidden mixmin sign gates from the start.

## FH52. Transition-residual block state is a submit-safe non-anchor validator

- Failed hypothesis: after within-block joint labels failed, the missing structural target could be the transition residual from labeled flanks/raw/subject baseline into the hidden run, and this residual would independently validate mixmin/E56-like hidden directions without relying on public anchors.
- Observed result: E60 ran `analysis_outputs/transition_residual_block_state_probe.py` over `438` methods. Joint gates were `0`. Residual MSE improved over raw in `227` methods and hidden mixmin sign was negative in `217`, but these were not the calibrated methods. The best row-valid transition method, `transition_raw_residual_baseraw_k4_a24_w0.35`, was close to raw (`+0.000186` row LogLoss), improved residual MSE (`-0.017074`), but hidden mixmin stayed adverse (`+0.000230`) and S3 remained adverse. The best hidden-sign method, `transition_raw_residual_baseedge_mid_k4_a4_w1.00`, had strong hidden mixmin sign (`-0.001569`) but pseudo-hidden row LogLoss collapsed by `+1.519232` versus raw and S3 by `+1.331880` versus subject.
- Why discard: the residual target splits exactly where it needed to unify. Conservative raw-based residuals preserve calibration but do not explain mixmin; edge-based hidden-sign residuals explain mixmin-like direction only by making impossible row-level moves.
- Implementation issue possible: medium. The model is kNN residual prediction and may be too crude, but the failure mode is large and diagnostic: the hidden-sign axis is not calibration-preserving. A future model may use transition residual as one energy, not as the target by itself.
- Bottleneck implication: independent non-anchor validation for E56 cannot be "hidden-sign residual looks good" alone. It must also preserve pseudo-hidden row calibration, S3, and residual MSE.
- Do not repeat: generating submissions from transition-residual hidden-sign rates, especially endpoint-mid aggressive residuals. Use E60 only as a risk diagnostic or as a constrained feature in a broader target that keeps row calibration explicit.

## FH53. E58 rejection was only a score-index artifact

- Failed hypothesis: the E58 no-submission decision might be caused by candidate metadata becoming detached from the corresponding prediction array after sorted prefilters, so corrected scoring could open an eligible distillation gate.
- Observed result: E61 added stable `pred_index` at generation time and used it in `attach_anchor_scores`. The rerun kept `104727` generated candidates and `1200` scored candidates. Eligible gates stayed `0`; diagnostic reverse gates stayed `0`; best toward-teacher delta was `-0.000004081`; best reverse-control delta was `-0.0000000126`; corrected toward sign-level anchor improvements were `126/900`.
- Why discard: the implementation bug existed, but fixing it did not create a selector-scale candidate or change the no-submission conclusion. It weakened the previous apparent sign-level support rather than strengthening it.
- Implementation issue possible: low for this specific claim. The remaining limitation is the E58 candidate family itself, not the scoring identity wiring.
- Bottleneck implication: E58 failed because simple E56 teacher slicing is too weak, not because the scorer mislabeled the best candidates.
- Do not repeat: any scored candidate table that is sorted, reset, or prefiltered without carrying a stable prediction id. Future grid scorers must preserve candidate-to-probability identity explicitly.

## FH54. Transition residual is the missing gate for E56 teacher cells

- Failed hypothesis: E60 transition residuals fail as direct probability targets, but they can still validate E56 teacher movement if used only as sign/block/target gates.
- Observed result: E62 generated `363258` transition-gated E56 candidates and actual-anchor scored `1300`. Eligible toward-teacher gates were `0`; diagnostic reverse gates were `0`. Best toward-teacher anchor delta was `-0.000002716`, from `toward_teacher|low_slack_half|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080`, which is weaker than corrected E58's `-0.000004081`. Best reverse delta was only `-0.00000000547`.
- Why discard: the gate makes the candidate more interpretable but not more useful. Balanced transition sign plus raw agreement isolates a plausible subset, yet the movement remains below selector/public-sensor margin and does not improve on the simpler E58 gate.
- Implementation issue possible: medium. The gate family is still hand-built and does not learn a joint representation. The discarded claim is only the simple use of transition residuals as E56 cell gates.
- Bottleneck implication: transition residual information is not the missing independent non-anchor validator by itself. The bottleneck remains calibration-preserving probability translation from hidden-world energy.
- Do not repeat: using E60 transition sign as a simple post-hoc mask for E56 teacher movement. Future use must embed transition residual inside a richer target with row calibration, S3, and public-disagreement constraints.

## FH55. Hidden-rate gradient consensus is enough to make E56 teacher submit-safe

- Failed hypothesis: if independent subject/calendar/raw/transition hidden-rate views agree that E56 teacher cells move down the BCE gradient at mixmin, then the resulting gradient-gated E56 movement should clear selector-scale public-anchor margin.
- Observed result: E63 generated `404671` gradient-gated E56 candidates and actual-anchor scored `1300`. Direction validation was strong: toward-teacher candidates passed hidden guard `1000/1000`, E56 world guard `1000/1000`, movement guard `1000/1000`, and anchor sign beats `932/1000`; reverse controls passed hidden guard `0/300` and world guard `0/300`. But eligible gates were still `0`. Best toward-teacher anchor delta was only `-0.000003650`, from `toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|w0.070|c0.080`, and best reverse delta was `-0.00000000894`.
- Why discard: gradient consensus solves a different problem than submission safety. It shows the E56 teacher direction is not arbitrary, but it does not estimate how far to move probabilities without losing public-anchor calibration. The best anchor gain is below the `1e-5` margin and weaker than corrected E58's `-0.000004081`.
- Implementation issue possible: medium. The gradient views are hand-built and amplitude is still a capped grid, so a learned or analytic amplitude translator may improve. The discarded claim is only direction-consensus-as-submit-gate, not gradient consensus as energy.
- Bottleneck implication: the bottleneck has moved from "is there a hidden direction?" to "how do we translate a validated hidden direction into selector-scale calibrated probability movement?" This strengthens E56 as a teacher but weakens any plan that keeps adding direction gates without amplitude modeling.
- Do not repeat: submitting gradient-gated E56 files or treating hidden-rate agreement alone as public evidence. Future work should target amplitude, calibration risk, and targetwise S3/Q2/Q3 movement size for cells already validated by gradient consensus.

## FH56. E63 gradient-consensus direction is just under-amplified

- Failed hypothesis: E63's hidden-rate consensus direction is correct and only too small; increasing scale/cap on the same validated cells should create a selector-scale public-anchor improvement.
- Observed result: E64 generated `12096` amplitude-expanded candidates and actual-anchor scored `1796`. Toward-teacher candidates passed hidden guard `1346/1346`, E56 world guard `1346/1346`, and movement guard `1346/1346`, but anchor beats were `0/1346`. Best toward-teacher anchor delta was `+0.000003024`; median toward delta was `+0.000757074`. Reverse controls also had no improvement, with best delta `+0.000000154`.
- Why discard: scalar amplitude separates hidden-world validity from public-anchor LogLoss. The direction remains hidden-valid, but larger moves make actual-anchor worse. This is exactly the failure mode LeJEPA-style diagnostics were meant to catch: a representation can be geometrically coherent while its probability translation is wrong.
- Implementation issue possible: medium. The tested grid is focused rather than exhaustive, and actual-anchor is still a proxy. But the result is broad within the focused family: every scored toward candidate loses to mixmin, despite all hidden/world guards passing.
- Bottleneck implication: the next bottleneck is not direction or scalar scale. It is targetwise/rowwise calibration: which validated cells should move almost zero, which can move, and how Q2/S3/Q3 interact with LogLoss.
- Do not repeat: larger global scale/cap sweeps on E63/E56 gradient cells. Future amplitude work must be conditional by target, row risk, or structural block state, not a single scalar.

## FH57. Near-zero targetwise E56 amplitude clears submission margin

- Failed hypothesis: E64 failed only because the moves were too large; a very small targetwise line search around E63 gradient-consensus cells should find a submission-margin pocket.
- Observed result: E65 generated `27384` candidates and actual-anchor scored `2400`. Toward-teacher candidates passed hidden/world/movement guards `2290/2290`, and `1753/2290` beat mixmin sign-level. But anchor-margin gates were `0`. The best toward-teacher delta was only `-0.000005995`, from `toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120`. Reverse controls had no diagnostic gate.
- Why discard: the near-zero pocket is real but not submission-scale. The best response depends on excluding Q2/S3, single-target moves are weak, and S2 is adverse. This is a target-conflict clue, not a candidate.
- Implementation issue possible: medium. The grid is focused, not exhaustive, and actual-anchor remains a proxy. But it specifically tested the most plausible next branch after E63/E64: small scales, target masks, row gates, caps, and flat/core-gain shapes. The margin gate stayed closed.
- Bottleneck implication: the bottleneck is not line-search resolution. The missing object is a Q2/S3-aware calibration translator or a structural representation that explains why broad target movement saturates before becoming public-anchor safe.
- Do not repeat: more near-zero scalar/target-mask sweeps on the same E63 cells unless a new target-conflict model changes the cell set or amplitude rule.

## FH58. Q2/S3 conflict means hidden direction is wrong

- Failed hypothesis: E65's `no_q2_s3` pocket works because Q2 and S3 teacher movement is simply wrong under hidden-rate structure; excluding them is therefore the semantic solution.
- Observed result: E66 generated and scored `3000` focused matched-mask candidates. `no_q2_s3` remained the best robust actual-anchor mask at `-0.000005995`, but Q2/S3 add-back was not hidden-direction adverse. `all` add-back worsened robust actual-anchor in `432/432` matched configurations while improving mean-anchor in `288/432`, min-set tail in `432/432`, and hidden core in `432/432`; max-set tail worsened in `432/432`. Q2/S3-only masks had hidden-core gains but `q2` and `q2_s3` had `0` anchor beats.
- Why discard: hidden/mean evidence and robust public-anchor evidence split. Q2/S3 can point in a plausible hidden direction while increasing the worst public-compatible tail enough to dominate LogLoss. Masking them is a diagnostic, not a semantic explanation.
- Implementation issue possible: medium. E66 uses focused E65/E63 cell families and actual-anchor proxy rather than true public labels. But the matched decomposition is internally strong: the same configurations show hidden and tail effects moving in opposite directions.
- Bottleneck implication: the next bottleneck is tail-risk calibration, not target-direction discovery. A valid translator must allow or shrink Q2/S3 based on scenario stability and max-set risk, not by broad inclusion/exclusion.
- Do not repeat: Q2/S3 add-back or exclusion sweeps that do not measure mean-versus-tail decomposition. Future Q2/S3 work needs tail-neutral gating or variance-aware amplitude.

## FH59. First-order Q2/S3 tail-neutral translator clears submission margin

- Failed hypothesis: E66's Q2/S3 tail-risk can be solved directly by first-order scenario-tail gates, making a Q2/S3-inclusive E56 translator submission-ready.
- Observed result: E67 generated and scored `7632` tail-neutral translator candidates. The best translator, `tail_meanneg_m1.00`, improved the actual-anchor proxy to `-0.000006933` versus mixmin and beat matched `no_q2_s3` in `387/432` anchor scenarios. The strict `tail_p90_nonpos_m1.00` variant beat matched base in `432/432` and stayed max-set-tail-neutral in `360/432`. Across pair comparisons, `4207/7200` beat matched base and `2241/7200` also stayed max-set-tail-neutral. However, all anchor-margin gates remained `0`.
- Why discard: the tail gate is directionally useful but still sub-margin and derived from known-anchor scenario derivatives. It does not yet prove the gated Q2/S3 cells are real hidden structure rather than local anchor-tail arithmetic.
- Implementation issue possible: medium. First-order BCE derivatives are approximate and use the current anchor scenario/mask family. A scenario-holdout or hidden/block/row-calibration validation could still rescue the idea, but E67 alone is not enough.
- Bottleneck implication: the bottleneck moved from "which targets?" to "which Q2/S3 cells have independent support?" The next translator must validate tail-gated cells outside the anchor-tail objective.
- Do not repeat: first-order anchor-tail gate sweeps as submission candidates without independent validation or selector-scale margin.

## FH60. E67 tail-gated Q2/S3 cells are only same-anchor derivative artifacts

- Failed hypothesis: E67's Q2/S3 tail-gated cells improve only because the same known-anchor combo family was used to define first-order gates and score the response.
- Observed result: E68 selected `180` promising E67 matched configs, rebuilt gates while holding each combo set out, scored `762` unique predictions, and formed `540` matched comparisons. Independent gates were `155/540`, and strict independent gates were also `155/540`. `tail_soft_max_m1.00` had `44` strict gates; `tail_p90_nonpos_m1.00` had `41` strict gates and best strict heldout delta `-1.260816e-6`. The strongest heldout score, `tail_max_nonpos_m1.00` at `-1.629588e-6`, failed because block-majority wins were `0`.
- Why discard: held-out combo construction, hidden Q2/S3 improvement, world support, and hidden-block Q2/S3 stress all survive for many selected cells. The artifact-only explanation is too strong.
- Implementation issue possible: medium. E68 still starts from selected E67 configs and uses proxy combo families, not true public labels. But the heldout reconstruction plus non-anchor diagnostics directly remove the simplest same-anchor arithmetic explanation.
- Bottleneck implication: the bottleneck is no longer Q2/S3 cell validity. It is amplitude and translation: the validated cells are real-looking but their held-out gains are `1e-6` scale.
- Do not repeat: dismissing E67 as pure anchor-tail artifact without heldout/non-anchor stress. Also do not submit E68 cells directly; the effect is below selector-scale margin.

## FH61. E68 strict Q2/S3 cells only need global alpha amplification

- Failed hypothesis: independently validated Q2/S3 cells are useful but under-scaled; a single alpha over their Q2/S3 logit delta should convert the E68 micro-edge into selector-scale movement.
- Observed result: E69 used `155` E68 strict pairs, scaled only the Q2/S3 logit delta over alpha `0` to `24`, and scored `2170` rows / `2061` unique predictions. Strict amplitude gates were `0`, and full-combo margin gates were `0`. Best full-combo delta vs mixmin was `-9.1779e-6`, below the `-1e-5` margin. Heldout tail-neutral counts fell from `155/155` at alpha `1` to `69/155` at alpha `8`, `49/155` at alpha `12`, and `22/155` at alpha `24`; median heldout response turned adverse after alpha `10`.
- Why discard: the full-combo proxy gets closer to the margin, but not enough, and the stability curve worsens as alpha increases. The missing object is not one global multiplier.
- Implementation issue possible: low to medium. E69 uses heldout-specific E68 gates rather than a unified submission rule, so it is a stress test rather than a candidate. But this makes the negative result stronger for simple alpha: even with heldout-specific strict cells, no margin gate opens.
- Bottleneck implication: the bottleneck is rowwise/cellwise amplitude selection or structural target design, not validated-cell direction or scalar scale.
- Do not repeat: global alpha sweeps over E68 strict cells. Future amplitude work must condition on row/block/tail energy and prove margin plus tail safety together.

## FH62. E70 strict-cell consensus is immediately submit-safe

- Failed hypothesis: because multiple E68 strict Q2/S3 cells can be aggregated, the resulting consensus movement should be safe enough to submit directly once it clears the local full-combo margin.
- Observed result: E70 built `2688` candidate rows / `2576` unique predictions and found `6` strict consensus gates, with best all-combo delta `-1.027751e-5`. However, every strict row used `gate=none`; sign-agreement gates did not produce strict rows. The construction also pools heldout-specific E68 strict cells and therefore is a stress result, not a unified test-time rule.
- Why discard: the local signal is real enough to keep H67 alive, but direct submission would confuse a heldout-specific diagnostic with a deployable probability rule. The margin is tiny and depends on consensus averaging before conservative agreement geometry is proven.
- Implementation issue possible: medium. E70 intentionally scored combo first and hidden/world/block stress only for the top `700` rows to keep the probe tractable. A unified-rule implementation could still rescue the idea, but E70 itself is not that rule.
- Bottleneck implication: consensus structure may be the missing accumulation mechanism, but it still needs rowwise/cellwise amplitude or unified structural gating. The bottleneck is now "how to make consensus reproducible and conservative", not "whether any strict-cell consensus can move the proxy".
- Do not repeat: submitting heldout-specific consensus rows or treating `gate=none` consensus as safe. Future work must test a unified non-heldout rule, agreement/energy diagnostics, and tail/block stability before producing a file.

## FH63. E71 unified strict-cell consensus is deployable

- Failed hypothesis: if E70's heldout-specific reconstruction was the main blocker, rebuilding each unique E68 strict cell once with the full combo family should produce a deployable consensus row under a conservative non-`none` gate.
- Observed result: E71 used `155` strict rows to derive `104` unique cells and built `3136` candidate rows / `2842` unique predictions. It found `1` strict unified gate and best all-combo delta `-1.082166e-5`, but deployable unified gates were `0`. The only strict row used `top75_heldout_mean`, mean base, `signed_p75` delta, `gate=none`, and alpha `8`.
- Why discard: unified reconstruction preserves the diagnostic signal but still fails the conservative submission condition. The branch remains disagreement-permissive; a public file would be betting on unregularized consensus rather than a stable representation.
- Implementation issue possible: low to medium. E71 intentionally uses E68 strict rows as evidence for cell selection, so it is still a diagnostic, but it removes the strongest heldout-specific reconstruction objection. The lack of non-`none` gates is therefore a meaningful negative.
- Bottleneck implication: the bottleneck is not only heldout-specific construction. It is the absence of a stable agreement/energy geometry that can choose when Q2/S3 consensus is safe.
- Do not repeat: treating unified `gate=none` consensus as submit-safe. Future work must either make non-`none` gates survive margin, learn rowwise/cellwise amplitude, or change the target to a structural block representation.

## FH64. E71 means no non-none Q2/S3 gate can be deployable

- Failed hypothesis: because E71 found `0` deployable non-`none` unified gates, the Q2/S3 consensus branch cannot produce a conservative test-time rule and should be abandoned unless a structural block target is rebuilt from scratch.
- Observed result: E72 swept sparse magnitude, soft agreement, sign agreement, target-only, and target-agreement gates over the same unified-cell source. It generated `4752` rows and found `21` strict rows, `10` deployable non-`none` rows, and `655` loose rows. The deployable rows came from `top_abs50` (`7`) and `s3_only` (`3`), not from Q2-only or soft/sign agreement. E73 materialized the best deployable row as `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`.
- Why discard: E71 falsified sign/agreement gating, not all non-`none` gating. Sparse magnitude is a different geometry: it accepts that only the largest Q2/S3 consensus cells are reliable and treats sign disagreement as noise/risk rather than a hard veto.
- Implementation issue possible: medium. E72 is still a local combo/hidden/world stress, and public LB is unobserved. But the narrow claim "no deployable non-`none` gate exists" is directly false under the same margin/stress machinery.
- Bottleneck implication: the bottleneck is now public sign, not mere deployability. We have a materialized sparse-gate sensor; if public rejects it, the failure is local stress overfit or public-subset mismatch, not absence of gate geometry.
- Do not repeat: abandoning Q2/S3 consensus solely because sign/agreement gates fail. Also do not submit untested soft/agreement/Q2-only variants; the only live E72 file is the selected sparse-magnitude diagnostic.

## FH65. E73 sparse Q2/S3 gate is a single-cell artifact

- Failed hypothesis: the E73 top_abs50 file might only pass because one or two of the `13` source cells dominate the local combo proxy, so deleting cells or sampling subsets would collapse strict/deployable support.
- Observed result: E74 ran `analysis_outputs/q2_s3_sparse_gate_stability_probe.py` over reference, leave-one-cell-out jackknife, group-keep, rank-keep, and `60` deterministic bootstrap8 variants. It scored `470` rows over `94` variants and found strict/deployable rows `141`. Jackknife alpha16 stayed deployable `13/13`; bootstrap8 alpha16 stayed deployable `48/60`; all jackknife alpha16 rows were loose and deployable. The reference full-pool alpha20 row remained strict/deployable and improved local all delta to `-1.07261e-5`.
- Why discard: broad jackknife and bootstrap support directly contradicts the single-cell-artifact explanation. The E73 source pool behaves like a stable sparse consensus family under this stress.
- Implementation issue possible: low to medium. E74 still uses local combo/hidden/world/block stress rather than public labels, and bootstrap subsets are not independent public evidence. But the discarded claim is only cell fragility, not public alignment.
- Bottleneck implication: the remaining blocker is not source-cell fragility. It is public sign and amplitude calibration: alpha20 looks better locally but alpha24 fails strict, so the branch needs public observation or a stronger public-like amplitude selector.
- Do not repeat: rejecting E73 because it has only `13` source cells. Also do not submit the best bootstrap subset solely because it has slightly better local delta; use the full-pool E74 alpha20 row if testing amplitude.

## FH66. Sparse Q2/S3 safe amplitude is one symmetric scalar

- Failed hypothesis: once the E73 sparse gate is fixed and cell-stability is established, Q2 and S3 can share a single safe alpha. Under this view E74 alpha20 is the natural amplitude ridge and target-specific amplitude should not materially improve the deployable frontier.
- Observed result: E75 crossed Q2 and S3 alpha values on the E74 full pool. It scored `120` rows, with strict/deployable `37` and loose `109`. `s3_higher` produced `23` strict/deployable rows, `s3_only` produced `6`, `q2_higher` produced `5`, `equal` produced `3`, and `q2_only` produced `0`. The best deployable row was not symmetric: `alpha_q2=8`, `alpha_s3=28`, tag `e75_q2a8.0_s3a28.0_f07219b4`, all delta `-1.23676e-5`, hidden Q2/S3 `-0.000372692`, and block win `0.722222`.
- Why discard: the local deployable frontier is clearly target-asymmetric. Symmetric alpha20 remains useful as a control, but it is not the best local sparse-gate amplitude under the current stress set. Q2-only being dead while S3-heavy dominates means a single scalar is hiding the actual amplitude boundary.
- Implementation issue possible: medium. E75 still depends on combo proxies and the true public sign is unknown. But the discarded claim is only local symmetric-amplitude optimality, not public alignment.
- Bottleneck implication: the remaining blocker is now public sign and target-specific amplitude calibration. If E73 public sign is positive, the next information-rich question is whether public prefers conservative symmetric movement or S3-heavy target-asymmetric movement.
- Do not repeat: treating E74 alpha20 as the only second sparse-gate sensor. Keep it as symmetric control, and use E75 when the experiment is specifically target-asymmetric amplitude.

## FH67. Exact E75 `q2=8/s3=28` amplitude is as subset-stable as E73 sparse sign

- Failed hypothesis: after E75, the exact target-specific amplitude pair `alpha_q2=8`, `alpha_s3=28` can be promoted as broadly stable in the same sense as E73's alpha16 sparse-gate sign.
- Observed result: E76 replayed `21` Q2/S3 alpha pairs over `94` reference/jackknife/group/rank/bootstrap source-subset variants. Exact `asym8_28_e75` beat `sym16_e73` and `sym20_e74` in `94/94` variants, so the direction survived. But exact `asym8_28_e75` was deployable in only `49/94` variants: jackknife `8/13`, group_keep `7/10`, rank_keep `5/10`, bootstrap8 `28/60`. E74's earlier E73 alpha16 stress was broader: jackknife `13/13`, bootstrap8 `48/60`.
- Why discard: E76 separates direction from exact amplitude. S3-heavy/Q2-low is a stable local law, but universal `8/28` is not stable enough to outrank E73 as the first public sparse-gate sensor on robustness grounds.
- Implementation issue possible: low to medium. E76 uses the same local combo/hidden/world/block stress as E74/E75, so public sign is still unknown. The discarded claim is only exact-amplitude subset stability, not target asymmetry itself.
- Bottleneck implication: the next amplitude problem is row/cell-conditioned calibration, not another universal target-alpha pair. Public could still reward E75, but that would mean public subset matches the sharp asymmetric ridge despite partial subset stability.
- Do not repeat: calling E75 safer than E73 because it has better local all-combo delta. Use E75 for target-asymmetry information value, not for robustness; keep E74 as the symmetric control.

## FH68. E76 source-subset posterior averaging repairs exact-amplitude instability

- Failed hypothesis: because E76 showed S3-heavy/Q2-low direction is stable but exact `8/28` deployability is partial, aggregating source-subset predictions as a posterior should recover a safer amplitude without requiring a hand-picked universal pair.
- Observed result: E77 generated `6840` posterior rows from `19` selector groups, bases mixmin/E73/E74, aggregators mean/median/signed quantiles, scopes Q2S3/S3-only/full, and shrink values up to `2.5`. Strict/deployable rows were `0`, loose rows were `3099`, and deployable rows beating E75 local all-combo were `0`. `62` rows beat E75 locally, but all failed strict/deployable gates. Mixmin/Q2S3 was the safest branch (`688/760` loose; best all `-0.000008095`; hidden/world/block favorable) but below margin. Mixmin/full reached `-0.000012599`, yet best rows only beat `1/3` combo sets and kept `1/3` tail-neutral sets.
- Why discard: posterior averaging merges incompatible stress worlds. The safe target-limited posterior does not reach selector margin, while the margin-clearing full posterior buys score by losing combo-set/tail consistency. That is not a repair of exact-amplitude instability; it is a new instability with a better-looking mean.
- Implementation issue possible: low to medium. E77 uses E76's local stress universe and robust aggregators, not a learned posterior. A learned localizer could still work. The discarded claim is only generic source-subset posterior averaging as a direct candidate generator.
- Bottleneck implication: the missing object is localization, not averaging. Target-asymmetric direction is real-looking, but safe amplitude depends on combo-set, tail, row-block, or public-like energy.
- Do not repeat: materializing E77 posterior aggregate submissions or treating full-scope posterior margin as safe without tail/set support. Future amplitude work must condition movement before aggregation or learn a row/cell-local gate.

## FH69. Source-subset reliability masks repair E75 exact-amplitude risk

- Failed hypothesis: E76 deployable/non-deployable distributions can localize E75 movement into a better deployable row.
- Observed result: E78 scored `4452` localized rows from `36` reliability masks, with strict/deployable `1806`, loose `3934`, deployable rows beating E75 `0`, and best all equal to E75 `-1.23676e-5`.
- Why discard: masks either collapse to identity over E75 active cells or shrink the edge below E75. Strong sign masks can remain deployable but weaker; excess/veto masks are too sparse.
- Implementation issue possible: low to medium. E78 uses E76 source-subset distributions and the same local stress universe, not a learned public-like localizer. A richer row/block/tail-conditioned localizer could still work. The discarded claim is only source-subset reliability masks as direct amplitude repair.
- Bottleneck implication: exact amplitude risk is not solved by row/target reliability from the same E76 source-subset universe.
- Do not repeat: sign-stability, consensus, excess, or veto masks over E76 source variants as direct candidates. Future amplitude localization needs public-like row/block/tail state or public feedback from E73/E75/E74.

## FH70. Handcrafted row/block/flank masks repair E75 exact-amplitude risk

- Failed hypothesis: E75's sparse Q2/S3 amplitude is correct only on a public-like subset identifiable by subject-calendar topology, flanking train labels, subject priors, or positive sparse-unit energy.
- Observed result: E79 scored `6516` localized rows from `61` masks. Strict/deployable rows were `1318`, loose rows were `3403`, deployable rows beating E75 were `0`, and best all stayed E75-equivalent at `-1.23676e-5`. Positive sparse-unit energy masks cut the active E75 rows from `72/250` to `22` or `36`, but did not improve edge. Best non-identity masks such as flank `s3_high`, topology `block_inner`, `block_first_half`, `subject_late_half`, and subject-prior/flank target masks stayed deployable but weaker than E75.
- Why discard: the masks are real context descriptors, but as direct multiplicative gates over E75 movement they only shrink or reshape an already sparse active set. They do not reveal a better row subset.
- Implementation issue possible: low to medium. E79 uses handcrafted masks and local stress, not a learned structural target or public labels. A learned combo-set/tail/structural localizer could still work. The discarded claim is only direct row/block/flank mask repair over E75.
- Bottleneck implication: exact amplitude risk is not solved by simple row topology or nearest train-label context. The remaining amplitude problem is combo-set/tail calibration or a learned structural representation, not another handcrafted row-mask sweep.
- Do not repeat: subject id, block position, train-gap, flank-label, subject-prior, or energy-quantile masks over the same E75 unit delta as direct candidates. Use these variables only as features/energies inside a stronger structural target or public-tested sparse-gate interpretation.

## FH71. Submitted E73 combined sparse-gate file is public-aligned

- Failed hypothesis: `submission_e72_topabs50_q2s3_gate_4e48cba2.csv` would improve public LB if the E72 sparse-magnitude Q2/S3 consensus was public-real.
- Observed result: public LB was `0.5764077772`, worse than mixmin `0.5763066405` by `+0.0001011367`. E80 measured a sign reversal versus local expected delta `-0.0000105458`, a `9.590x` public/local edge ratio, and `893` moved cells across all `7` targets.
- Why discard: the submitted file is not a clean Q2/S3 sign test. It combines Q2/S3 sparse movement with `814` non-Q2/S3 moved cells. Therefore the broad submitted-file public-alignment claim is dead, while isolated Q2/S3 remains separately tested by E81.
- Implementation issue possible: low for the public observation and movement audit; medium for attributing the public miss to any target group because public labels are not known.
- Bottleneck implication: public LB is punishing either broad all-target base movement, Q2/S3 movement, or their interaction. Direct E74/E75 amplification is not a justified next step.
- Do not repeat: treating E73 as a validated public sign sensor or submitting E74/E75 as direct amplitude follow-ups.

## FH72. Public E73 failure justifies direct Q2/S3 sign inversion

- Failed hypothesis: because E73 worsened public LB, the opposite Q2/S3 movement should be a useful next public sensor.
- Observed result: E81 inverse Q2/S3 had local all delta `+0.000014747`, `0/3` combo sets beating base, `0/3` tail-neutral, hidden Q2/S3 `+0.000418366`, world `+0.000311296`, and block win rate `0.083333`. Inverse Q2-only and inverse S3-only also failed local guards.
- Why discard: one public miss was underidentified by broad-base contamination, and the inverse direction is locally adverse across combo, hidden, world, and block diagnostics.
- Implementation issue possible: low. The inverse controls are direct algebraic sign reversals around the mixmin anchor and use the same stress machinery.
- Bottleneck implication: the useful object is not public-LB reaction sign flipping. It is calibration-safe translation of a sub-margin Q2/S3 latent.
- Do not repeat: building inverse sparse-gate submissions from E73 public failure without an independent structural gate.

## FH73. Removing broad base contamination makes pure Q2/S3 source grafts submission-scale

- Failed hypothesis: E73 public failure was mainly caused by non-Q2/S3 base contamination, so the wider E72/E75/E76 Q2/S3 source universe should produce a strict/deployable candidate when only Q2/S3 value or source-base delta movement is grafted onto mixmin.
- Observed result: E82 generated `8402` pure mixmin-anchored source graft rows and non-anchor evaluated `700` combo-promising rows. Strict/deployable rows were `0`, loose rows were `700`, and best evaluated all delta was `-0.00000790328`, below the `-1e-5` selector margin.
- Why discard: the failure is not hidden/world/block/tail inconsistency. Every evaluated row passed all non-margin guards (`700/700` all beats base, all sets beat base, all tails neutral, hidden Q2/S3 improves, world nonworse, block majority beats, block tail safe), but `all_margin_vs_mixmin` was `0/700`. Pure Q2/S3 is coherent but too small.
- Implementation issue possible: low to medium. E82 uses source rows from existing local stress families and combo-promising preselection, so it could miss a bad-combo row with surprising public value. But the discarded claim is local strict/deployable submission scale, and that is directly false under the current gate.
- Bottleneck implication: the missing movement is no longer "cleaner Q2/S3 isolation." It is a broader calibrated structural move that can clear margin while using Q2/S3 as energy/tail guard.
- Do not repeat: materializing pure Q2/S3 grafts from E72/E75/E76 solely because they are loose and tail-safe. Use them as latent energy or constraints inside a larger block-state candidate.

## FH74. Q2/S3 energy alone can select safe broad structural movement

- Failed hypothesis: E82's coherent Q2/S3 latent energy should be enough to gate older JEPA/block/raw structural deltas into a deployable mixmin-relative candidate.
- Observed result: E83 generated `3716` structural-gated rows and non-anchor evaluated `700`. Strict/deployable rows were `0`, loose rows `40`, structural-loose rows `189`, and the best broad all-delta reached `-0.0000350517`. The high-margin broad rows beat only `2/3` combo sets and worsened Q2/S3 hidden/world (`hidden_q2s3` about `+0.000443`, world about `+0.000252`). The E72-derived Q2/S3-safe rows kept `3/3` set/tail support and hidden/world improvements, but stayed sub-margin around `-0.000008935`.
- Why discard: Q2/S3 energy separates useful regimes but does not itself solve the compatibility problem. The structural rows have enough edge and fail Q2/S3/world/set safety; the Q2/S3-safe rows have safety and fail margin.
- Implementation issue possible: medium. E83 reuses existing structural submission deltas, so a newly trained structural representation could behave differently. The discarded claim is only that row-energy gating over the available broad deltas is sufficient.
- Bottleneck implication: the bottleneck is not lack of any structural movement. It is coupling structural non-Q2S3 margin with Q2/S3 safety without breaking a public-observation combo set.
- Do not repeat: another blind E82-energy gate sweep over old structural files. Future work should either recombine target groups explicitly or learn a row/block gate for the remaining combo-world conflict.

## FH75. Target-group recombination of non-Q2S3 structural margin and Q2/S3 safety is deployable

- Failed hypothesis: E83's two pieces can be added in disjoint target groups: structural movement outside Q2/S3 supplies margin, and E72-derived Q2/S3 movement supplies the missing safety, yielding a deployable file.
- Observed result: E84 generated `1728` recombination rows and non-anchor evaluated `700`. Strict/deployable rows were `0`; loose and structural-loose were `700/700`. Best evaluated all delta was `-0.0000321500`, and every evaluated row passed margin, hidden Q2/S3, world, block-majority, and block-tail guards. But every row beat only `2/3` combo sets and kept `2/3` tails neutral. The rejecting set was `inverse_top`: `0/700` wins, mean inverse-top minus-base `+0.0000859`; raw05-compatible and all-sign sets accepted `700/700`.
- Why discard: additive target-group separation fixes the Q2/S3 safety and hidden/world/block issues, but not the public-observation set identity conflict. A file that fails one combo world in all `700` evaluated rows is not a safe candidate.
- Implementation issue possible: low to medium. The combo-set definitions are local proxies, not public labels. That is why `submission_e84_inverse_sensor_1c74da00.csv` is retained as a diagnostic sensor, not discarded as useless.
- Bottleneck implication: the current live bottleneck is row/block-specific public-world separation, especially whether public behaves like `inverse_top` or like raw05-compatible/all-sign worlds.
- Do not repeat: presenting E84 recombination as deployable-safe because it has a large local mean edge. Use it only to test public-world identity or to train a gate that explicitly separates the inverse-top conflict.

## FH76. E84 inverse-top conflict must be row/block-specific before target-axis pruning can help

- Failed hypothesis: because E84 passed hidden/world/block stress but failed only the inverse-top combo set, the next useful repair must learn a row/block-specific inverse-top gate; target-axis pruning alone should not open a deployable candidate.
- Observed result: E85 generated `10135` target-pruned variants from E84 movement and non-anchor evaluated `700`. Strict/deployable rows opened to `535`, and the best `S1,S2,S3` candidate improved every relevant combo view: all delta `-0.0000238758`, inverse-top `-0.0000081666`, raw05-compatible `-0.0000295552`, all-sign `-0.0000339057`. Hidden core, hidden Q2/S3, world, raw-energy, block win, and block-tail diagnostics also stayed favorable.
- Why discard: the strongest immediate failure mode was target-axis contamination. E84's Q1/Q3/S4 movement was adverse under inverse-top, while S1/S2/S3 preserved enough structural signal to pass strict/deployable stress.
- Implementation issue possible: medium. Combo worlds are still local sensors, not true public labels, and public may prefer the removed Q1/Q3/S4 movement. But the discarded claim was "target-axis pruning cannot solve the E84 conflict locally"; E85 directly falsifies that.
- Bottleneck implication: the current bottleneck is now public-world choice among target axes, not only row/block localization. Row/block gates remain useful only if E85 fails public or if a later target-pruned candidate needs more upside.
- Do not repeat: jumping straight to complex inverse-top row/block gates before testing the simpler S1/S2/S3 target-pruned structural candidate.

## FH77. E85 target-prune edge is a single-source artifact

- Failed hypothesis: E85's selected S1/S2/S3 target-pruned file is an accidental row/source artifact; averaging strict E85 movements across source files should wash out the edge or break inverse-top stress.
- Observed result: E86 rebuilt E85 predictions, grouped strict rows by target mask, and generated `1485` source-diverse consensus variants. The evaluated `700` rows were all strict/deployable/loose. The selected `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv` keeps `Q2,S1,S2,S3`, averages top `40` rows from `18` source files across `gate,rawcorr_micro,rawcorr_refine`, uses mean aggregation and shrink `1.25`, and improves all delta to `-0.0000277059` while preserving inverse-top, raw05-compatible, all-sign, hidden/world/block, and block-tail stress.
- Why discard: source diversity did not wash out the target-prune law. It strengthened the local edge and improved block-tail safety from E85's `0.944444` to `1.0`.
- Implementation issue possible: medium. The source-consensus stress is still local and public-pending. Public may punish the consensus overstep or Q2 add-back even if the single-source-artifact objection is locally false.
- Bottleneck implication: the live question is no longer "is E85 just one row?" It is whether public accepts target-pruned structural movement at E86 amplitude, or only the lower-amplitude E85 version.
- Do not repeat: dismissing E85 solely because it came from one selected row. The next falsification must be public LB or a genuinely independent target-pruned world, not another single-source objection.

## FH78. E87 inverse-top-prior is the safest E86 fallback

- Failed hypothesis: because inverse-top was the rejecting combo world in E84 and E85 fixed that conflict, the E87 inverse-top-prior contrast should be the safest fallback if E86 is risky.
- Observed result: E88 measured the inverse-top-prior contrast against the known public-negative E72 movement and found the highest E72 proximity among E85/E86/E87 variants: high-E72 cell mass `0.602577`, E72 overlap ratio `1.113262`, E72 contamination index `0.928415`, and E72 row correlation `0.743567`.
- Why discard: inverse-top-prior is good for testing public-world geometry, but it is not safer under the actual post-E72 public observation. It moves fewer cells and has a strong inverse-top local edge, yet its movement mass concentrates more on the failed E72 manifold than E86 or no-Q2.
- Implementation issue possible: medium. E88 is label-free movement attribution, not public-label scoring. But the discarded claim is about safety ranking, not whether inverse-top can be informative.
- Bottleneck implication: public-risk decomposition must include observed movement-manifold proximity, not just local combo-world scores. After an E86 miss, no-Q2 is the cleaner first contrast unless the explicit question is inverse-top public-world identity.
- Do not repeat: promoting inverse-top-prior as the conservative fallback solely because it wins the inverse-top proxy. Treat it as diagnostic only.

## FH79. Direct projection away from E72 is the clean decontamination repair

- Failed hypothesis: once E88 identifies E72 contamination, the cleanest E86 repair should be to project the E86 movement away from the E72 failed movement vector.
- Observed result: E89 projection-away variants could lower E72 proximity, but aggressive projection often broke inverse-top/world/block stress or strict/deployable status. The selected strict repair was not projection. It was a simpler cell-local fallback: keep E86, but replace top-20% E72 failed cells with E85 movement, yielding contamination index `0.676361`, all delta `-0.000025896`, inverse-top `-0.000005554`, world `-0.000140452`, and block-tail safe `0.944444`.
- Why discard: projection treats E72 contamination as one global vector, but the stress failures show the bad axis is not orthogonal to useful E86 structure. Cell-local fallback preserves the target-pruned law better.
- Implementation issue possible: medium. Projection scopes and beta grid were limited, so a more constrained projection could still be useful. The discarded claim is that direct projection is the obvious/safe first repair.
- Bottleneck implication: the remaining public-risk geometry is local and cell/target-dependent, not a single linear contamination axis. Decontamination should use local fallback or learned gates before global vector surgery.
- Do not repeat: promoting projection-away rows merely because their contamination index is lower. Require strict/deployable, inverse-top/world/block, and margin survival at the same time.

## FH80. Minimum E72 contamination is automatically the best decontaminated successor

- Failed hypothesis: after E89, the decontamination decision can be ranked primarily by the lowest E72 contamination index among strict rows.
- Observed result: E90 rescored the same strict E89 scan and found a row-coherent Pareto knee: `analysis_outputs/submission_e90_e72pareto_28925de5.csv`, E86 with E85 fallback on top `10%` E72-contaminated rows. It has higher contamination than E89 (`0.715784` vs `0.676361`) but preserves much more E86 structure: all delta `-0.000026932`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block win `0.777778`, and block-tail safe `1.0`.
- Why discard: minimum contamination and healthy latent geometry are different objectives. The min-contamination cell fallback may be safest if public directly punishes failed E72 cells, but it can underprice row-level hidden-state coherence and E86's source-consensus structural edge.
- Implementation issue possible: low to medium. E90's scoring weights are a design choice, and public LB is pending. But the discarded claim is only "minimum contamination is the unique local ranking rule"; the strict scan itself shows a non-dominated row-coherent alternative.
- Bottleneck implication: post-E72 risk has at least two axes: contamination removal and structural retention. The next public observation should identify which axis public rewards rather than treating them as one scalar.
- Do not repeat: ranking E86 repairs solely by E72 contamination index. Keep E86 for maximum upside, E90 for balanced row-coherent decontamination, and E89 for minimum-contamination downside control.

## FH81. E72-updated movement-fingerprint proxy can rank post-mixmin candidates

- Failed hypothesis: adding E72 as a public-negative anchor to the known-LB movement-fingerprint proxy should make it good enough to choose among E86, E90, E89, and E85.
- Observed result: E91 used `10` known public anchors and found best fixed LOOCV proxy `raw05_a2c8_compat` with MAE `0.000543412` and p90 error `0.001010234`. The same proxy holds out mixmin at `0.5774493627` even though actual mixmin is `0.5763066405`, an error of `+0.001142722`. E72's actual delta vs mixmin is `+0.0001011367`, but the proxy predicts E72-minus-mixmin as `-0.0000460726`.
- Why discard: the proxy error is roughly `10x` the E72 public miss and even gets the E72-vs-mixmin sign wrong under leave-one-out. A selector that cannot resolve the known frontier and first post-frontier miss cannot rank unobserved E86/E90/E89 candidates.
- Implementation issue possible: low to medium. The model class is intentionally simple and uses existing movement features. A different selector target might work, but the discarded claim is specifically that the current known-LB movement regression can rank the next post-mixmin files.
- Bottleneck implication: public LB observations remain sensors, not enough training labels for a submission ranker. The next file must be chosen by hypothesis value and local stress, not proxy-predicted LB.
- Do not repeat: building an E91-style proxy-ranked submission or using `proxy_pred_mean` from known-public regression to order E86/E90/E89. Use E86 for max-upside, E90 for row-coherent decontamination, and E89 for minimum-contamination if those are the questions being tested.

## FH82. Hidden-block posterior alignment can rank post-mixmin candidates

- Failed hypothesis: the current hidden-block posterior representation should be public-safe enough to choose among E86, E90, E89, and E85.
- Observed result: E92 ranked the known public-negative E72 file first by hidden-block alignment and posterior CE. E72 had posterior CE delta `-0.000287300` versus mixmin, ahead of no-Q2 `-0.000257196`, E86 `-0.000255621`, E90 `-0.000250767`, E89 `-0.000235903`, and E85 `-0.000207023`.
- Why discard: a representation that most rewards the failed E72 movement is not public-safe as a selector, even if it is coherent as a hidden-block target. This is exactly the LeJEPA failure mode: a latent can have healthy-looking block geometry while encoding a shortcut or target that does not match the public metric.
- Implementation issue possible: medium. The posterior was built from prior hidden-block work and may still be useful as an energy feature. The discarded claim is narrower: posterior CE alone can rank the next public submission.
- Bottleneck implication: representation/capacity exists, but public-aligned translation is still missing. Hidden-block posterior, E72 contamination, local combo stress, and public LB anchors must remain separate energies.
- Do not repeat: using `hidden_block_posterior_alignment_score` or posterior CE delta as a direct submission ranker. Treat E92 as a representation-health warning and keep E86/E90/E89 as hypothesis sensors.

## FH83. Target-manifold consistency can counter-filter E72-tainted representations

- Failed hypothesis: because E92 hidden-block posterior alignment rewards the public-negative E72 file, the train Q/S target dependency manifold should provide a counter-energy that rejects E72 while preserving E86/E90/E89.
- Observed result: E93 found the opposite. E72 improved target-manifold delta mean versus mixmin by `-0.001468687`. Live candidates were favorable but smaller: E86 `-0.000921783`, no-Q2 `-0.000914184`, E90 `-0.000877945`, E89 `-0.000806467`, E85 `-0.000742113`. Older known public-bad anchors also looked target-manifold-consistent (`final9` `-0.020801364`, `bad_q2_jepa` `-0.002958703`).
- Why discard: target co-occurrence consistency is not the public-safe missing geometry. A movement can look healthier under train conditional labels, empirical label patterns, and pair correlations while still worsening public LB. This is another LeJEPA warning: representation geometry can be real but aligned to the wrong evaluation world.
- Implementation issue possible: medium. E93 uses simple logistic target conditionals and empirical pattern/correlation energies, not a richer subject/block-conditioned target manifold. The discarded claim is only that current train target-manifold consistency can rank or counter-filter post-mixmin submissions.
- Bottleneck implication: E72 failure is not explained by obvious target dependency violation. The bottleneck is hidden public subset/calibration/world identity after a movement that both block posterior and target co-occurrence can like.
- Do not repeat: ranking E86/E90/E89 by `target_manifold_delta_mean`, conditional residual RMS, pattern NLL, or pair-correlation gap. Use these as diagnostics only, not submission selectors.

## FH84. Soft representation health is sufficient for post-E72 candidate safety

- Failed hypothesis: if a candidate improves hidden-block posterior CE and target-manifold consistency, it is healthy enough to rank above lower-health candidates despite the E72 miss.
- Observed result: E94 found that the public-negative E72 file itself has strong soft-health signals, while its observed public miss requires only a small realized hard-label tail. E72 full adverse exposure is `0.002330945`, and the public miss `+0.0001011367` is only `4.3389%` of that scale. Among live candidates, soft-health ranks E86 highest, but E72-adverse positive exposure ranks E85/E89 as lower-tail than E90/E86.
- Why discard: LogLoss punishes the hard labels that oppose a move, not only the average geometry of a latent. A representation can be coherent and still put probability mass in a direction that is expensive on a small public-label subset.
- Implementation issue possible: low to medium. E94 uses the E72-adverse direction as a public-negative anchor, not true public labels for unobserved files. The discarded claim is only that soft-health metrics are sufficient without a hard-tail check.
- Bottleneck implication: the current candidate choice has separate axes: E86 maximum soft-health/upside, E90 row-coherent compromise, E89 lower hard-tail/downside, and E85 conservative floor.
- Do not repeat: using posterior CE, target-manifold consistency, or aggregate soft-health gain as a standalone submission ranker. Pair every soft representation metric with hard-label tail exposure against known public-negative anchors.

## FH85. Lowest hard-tail exposure alone is a submission-safe objective

- Failed hypothesis: after E94, the next candidate can be selected by minimizing E72-adverse hard-label tail exposure directly.
- Observed result: E95 found a raw non-control best tail of `0.000146152`, but those extreme low-tail rows failed strict structural stress because they were broad rollback/mixmin-like moves. The submission-worthy row was not the lowest-tail row. It was the best strict non-dominated candidate, `analysis_outputs/submission_e95_hardtail_541e3973.csv`, with E72-adverse tail `0.000788914`, all delta `-0.0000262074`, hidden Q2/S3 `-0.000251140`, world `-0.000132931`, block win `0.750000`, and block-tail safe `0.972222`.
- Why discard: hard-tail minimization can erase useful E86 structure. Tail exposure is a gate and risk energy, not a scalar objective to optimize without hidden/world/block and local-margin survival.
- Implementation issue possible: low. E95 explicitly separated raw best-tail from strict best-tail, deduped predictions, and used positive-tail masks to avoid zero-tail quantile artifacts.
- Bottleneck implication: the bottleneck is a three-way tradeoff: hard-label tail risk, structural retention, and local margin. E95 creates a lower-downside candidate, but E86/E90 remain meaningful because they test different points on that frontier.
- Do not repeat: promoting mixmin-like or low-movement rows because their hard-tail exposure is tiny. Require strict structural survival and non-trivial movement before considering a hard-tail-gated submission.

## FH86. E72-derived hard-tail gates are only local diagnostics

- Failed hypothesis: because E72 public labels are unobserved and E95 was built from an E72-adverse proxy, the hard-tail localized gate should be treated as a local diagnostic with no expected public edge.
- Observed result: `submission_e95_hardtail_541e3973.csv` scored public LB `0.5762913298`, improving over mixmin by `0.0000153107` and over failed E72 by `0.0001164474`. The public gain is `58.42%` of E95's local all-combo margin and `15.14%` of the E72 miss scale.
- Why discard: E95 converts the E72-derived hard-tail proxy into a real public improvement. The proxy is imperfect and small-scale, but it is not merely post-hoc local stress.
- Implementation issue possible: low. The public result is direct. The remaining uncertainty is not whether E95 was public-positive, but whether the next candidate should preserve more E86 structure (`E90`/`E86`) or lower tail floor further (`E85`).
- Bottleneck implication: hard-tail localization is a live feature family and should be part of future LeJEPA-style health checks. It still does not explain the 0.54 gap, because the gain is a localized tail repair rather than hidden block-rate recovery.
- Do not repeat: dismissing E72-derived gates solely because public labels are hidden. Require conditional-budget stress and structural survival, then treat public observations as sensors for the retained-structure versus conservative-floor tradeoff.

## FH87. E95 public anchor makes known-LB movement regression submission-usable

- Failed hypothesis: after E95 becomes a public-positive frontier anchor, adding it to the known public table should make movement-fingerprint regression sharp enough to rank E90/E86/E85.
- Observed result: E98 added E95 as the 11th known anchor and reran fixed LOOCV movement proxies. The best proxy was still `raw05_a2c8_compat` with MAE `0.000520095` and p90 abs error `0.000816497`. That p90 error is `53.33x` the E95 edge over mixmin and `8.07x` the E72 miss over mixmin. It still predicted E72-minus-mixmin with the wrong sign (`-0.0000305135` predicted vs `+0.0001011367` actual).
- Why discard: the proxy error is much larger than the frontier-scale differences and it fails one of the critical known pair signs. Its candidate spread over the post-E95 queue is only `0.000015142`, which is not interpretable under this error.
- Implementation issue possible: low to medium. The proxy families are intentionally fixed and simple to avoid overfitting the small public table. A different future selector may work, but this specific known-LB regression cannot be used as the next submission order.
- Bottleneck implication: adding public observations helps the hypothesis graph, not a supervised LB ranker. The next public file remains a sensor for retained structure versus conservative tail floor, not a proxy-optimized candidate.
- Do not repeat: using E98 `proxy_pred_mean`, `candidate_risk_score`, or any direct known-LB movement-regression ranking to choose E90/E86/E85. Require a selector that can hold out E95/mixmin/E72 before using predicted LB.

## FH88. E95-conditioned tail worlds promote E90/E86 as the next expected-improvement bet

- Failed hypothesis: after E95 improves public, the best next file should be the candidate that preserves more E86 structure, especially E90 or E86, because E95 may have sacrificed too much hidden/world/block signal.
- Observed result: E99 forced each complete E96 tail scenario to explain both E72's public miss and E95's public gain using `public_delta = alpha * local_all_delta + lambda * E96_tail_delta`. All `3894` scenarios solved, `3452` were broad-plausible, and E95 remained best mean, best p95, and winner mode. Broad-plausible beat-E95 rates were E90 `0.002607` and E86 `0.000290`, while E89 was `0.195829`.
- Why discard: once E95 is conditioned in, the local+tail abstraction says the current frontier is already the best compromise. E90/E86 are still valuable structural sensors, but not strong expected-improvement bets over E95 under this model.
- Implementation issue possible: medium. The transfer model is deliberately simple and only has two terms, so it could miss a row-coherent structural-retention effect. The discarded claim is not "E90/E86 can never win"; it is "E95-conditioned local+tail evidence makes E90/E86 the most likely next improvement."
- Bottleneck implication: the immediate plateau is not solved by simply retaining more E86 structure. The remaining plausible E95 counterfactual is whether E95 over-localized hard-tail cells and E89's broader cell fallback matches public better.
- Do not repeat: presenting E90 or E86 as the default next expected-improvement file after E95 without new evidence. Use E90 only for the explicit row-coherent structure question and E86 only for maximum-upside risk testing.

## FH89. E89 counterfactual is a broad lower-downside replacement for E95

- Failed hypothesis: because E89 has the only material E95-beat rate after E99, it should be treated as a generally safer or broadly better E95 successor.
- Observed result: E100 decomposed the `3452` E99 broad-plausible worlds. E89 beat-E95 rate was `0.195829`, but mean E89-minus-E95 remained `+0.000003833`. E89-beating cases were `676` scenarios with top mask `q2s3` and mean tail surplus `+0.000002916`; the `q2s3` slice had beat rate `0.779891`. E89-not-beating cases had top mask `s1s2s3` and mean tail surplus `-0.000004272`.
- Why discard: E89's survival is concentrated in Q2/S3 diffuse-tail allocations. It is not a broad low-risk file and does not dominate E95 outside that pocket.
- Implementation issue possible: low to medium. The decomposition inherits E99's two-term transfer abstraction, so row-coherent effects could still be missed. The rejected claim is only the broad-lower-downside interpretation of E89.
- Bottleneck implication: the next public slot should be framed as a sharp Q2/S3 tail-world sensor, not as a generic improvement attempt. This keeps candidate selection tied to hidden-world falsification rather than aggregate beat-rate optimism.
- Do not repeat: promoting E89 because its aggregate E95-beat rate is nonzero without stating the Q2/S3 diffuse-tail condition and the loss condition if public rejects it.

## FH90. E101 active cells are a hidden subject/block-local selector

- Failed hypothesis: the `50` active Q2/S3 cells in E101 identify a small hidden subject or block subset, so the next improvement should be a handcrafted subject/block-local rollback mask.
- Observed result: E102 found the active cells spread across `48` rows, `26` hidden blocks, and all `10` subjects. Target-count-preserving permutation nulls did not support subject/block concentration: max cells per block p `0.997300`, blocks touched p `0.935553`, subjects touched p `1.0`.
- Why discard: the active set is too distributed to justify a block- or subject-local selector. The only clear structure is edge-locality: edge-or-near-edge rate `0.620` vs null `0.471289`, p `0.016999`; mean edge distance `1.680` vs null `2.138444`, p `0.040848`.
- Implementation issue possible: low to medium. The hidden block reconstruction is derived from existing audits, so a richer block definition could alter details. But the current E101 active-cell atlas is incompatible with a narrow subject/block mask.
- Bottleneck implication: E101 is an amplitude/calibration-risk sensor, not a shortcut to hidden subject identity. The remaining bottleneck is target-axis Q2/S3 tail calibration near block boundaries, not obvious block membership selection.
- Do not repeat: building a subject/block-specific follow-up from E101 before public feedback. If E101 improves, test amplitude/edge-risk variants first; if it worsens, demote generic Q2/S3 rollback and keep edge-local rollback only as a weak diagnostic.

## FH91. E101 edge-locality is enough to create a stronger edge-only submission

- Failed hypothesis: because E102 found E101 cells are weakly hidden-block-edge-local, an edge-only or edge-enriched Q2/S3 rollback should dominate the full E101 active-cell rollback and become the next submission.
- Observed result: E103 scanned `180` active/edge/interior/top-gap rollback variants under the inherited E101 stress frame. `12` rows passed E103 stress, but `0` dominated E101 on broad mean, p95, and beat-E95 rate together. No E103 file was materialized. The best passing active-all alpha `0.375` improved broad mean/p95 but reduced beat-E95 rate to `0.980881` versus E101 `0.983488`; edge-only masks had positive p95 or failed strict safety.
- Why discard: the edge signal is not strong enough as a standalone selector. The stable branch remains the broader active-all Q2/S3 amplitude rollback, with edge proximity as a diagnostic risk feature.
- Implementation issue possible: low to medium. E103 reuses E101's transfer frame, so a future public-positive E101 result could justify a richer edge-energy model. The rejected claim is only that direct edge masks are already better than E101 now.
- Bottleneck implication: boundary geometry may still explain where Q2/S3 calibration risk lives, but selector strength is insufficient. The bottleneck remains amplitude/world calibration, not identifying a simple edge subset.
- Do not repeat: submitting edge-only, edge-topgap, or handcrafted active-cell edge masks before E101 public feedback or without a new independent stress source.

## FH92. A nearby higher E101 rollback alpha dominates the submitted E101 candidate

- Failed hypothesis: E101's alpha `0.25` is a coarse-grid accident, and a fine-grid alpha slightly above it should improve broad mean/p95 without losing E101's E95-conditioned scenario support.
- Observed result: E104 scanned `505` variants over alphas `0.000-0.500` by `0.005`. `228` rows passed E101-style stress, but `0` dominated E101 on broad mean, p95, and beat-rate together. In the active-all mask, the first alpha above E101 with beat-rate loss is `0.255`; it improves mean/p95 by only about `3.02e-7`/`2.6e-8` while dropping beat-rate by `0.000289687`. The best passing alpha `0.380` improves mean/p95 more but lowers beat-rate to `0.980881`.
- Why discard: higher alpha is not a free improvement. It changes the risk preference by trading scenario support for average transfer. That is useful after public feedback, but not enough to replace E101 before observing its public result.
- Implementation issue possible: low. E104 reuses the E101/E103 scoring frame and validates the exact E101 alpha as the control row. The caveat is that the frame is still E95-conditioned local+tail transfer, not public labels.
- Bottleneck implication: the immediate bottleneck is not grid resolution. It is deciding which side of the Q2/S3 amplitude risk frontier public actually occupies.
- Do not repeat: replacing E101 with a higher-alpha active-all rollback based only on better mean/p95 before E101 public feedback. Require either public-positive E101 feedback or a new independent stress source that can justify sacrificing beat-rate.

## FH93. E101 is a global-prior Q2/S3 correction

- Failed hypothesis: E101 should be interpreted as a broad target-prior correction, so global train prevalence should already make its `50` active Q2/S3 cells favorable versus E95.
- Observed result: E105 computed hard-label E101-minus-E95 deltas for every active cell. Under global train priors, expected E101-vs-E95 delta is `+0.000048971` and Monte Carlo beat probability is only `0.016610`. Under subject priors, expected delta is much closer to neutral at `+0.000007854` with beat probability `0.335360`. S3 owns `0.935862` of total flip benefit.
- Why discard: E101 only becomes plausible when active cells are interpreted through subject/block-local label tendencies, especially S3. It is not supported by global prevalence alone.
- Implementation issue possible: low. The calculation is deterministic conditional on E95/E101 probabilities; the Monte Carlo only samples null label worlds from train priors. The remaining uncertainty is whether public labels follow a still-richer local process.
- Bottleneck implication: the next public feedback is about hidden local label realization, not global calibration. If E101 wins, it identifies a local S3-heavy tail world; if it loses, the rollback-favorable local world did not materialize.
- Do not repeat: describing E101 as a generic Q2/S3 prior correction or using global prevalence to justify higher-alpha rollback.

## FH94. Subject-prior support can replace E101 before public feedback

- Failed hypothesis: because E105 makes E101 much less adverse under subject priors than global priors, subject-supported or S3-only active-cell masks should create a cleaner pre-feedback E101 replacement.
- Observed result: E106 scanned `268` subject-prior gate variants over E101 active cells. It found E101-pass `12`, prior-healthier `56`, interesting non-replacements `6`, but replacement rows `0` and E101-dominating rows `0`. The best interpretable S3-heavy masks at alpha `0.25` reduce prior risk but lose E101's broad support; `active_s3_all` has mean/p95/beat `-0.000015728/-0.000001195/0.973349` versus E101 `-0.000016205/-0.000001564/0.983488`.
- Why discard: subject-prior support is useful to interpret the hidden label world, but as a selector it removes too much of the amplitude rollback that makes E101 survive E95-conditioned stress.
- Implementation issue possible: low-medium. The first E106 run exposed a strict-flag bookkeeping bug for the new strategy name, but the rerun recomputed graft flags and restored `12` E101-pass rows. The remaining caveat is that all tests are still local stress and prior-null simulations, not public labels.
- Bottleneck implication: the bottleneck is not simply finding the most subject-supported S3 subset. It is whether public realizes the whole E101 active-cell label world.
- Do not repeat: replacing E101 with subject-prior-gated, S3-only, or high-support masks before E101 public feedback. Use those masks only as post-feedback contrasts if E101 improves.

## FH95. E101 loss can be locally explained by subject-prior or amplitude masks

- Failed hypothesis: if E101 loses public versus E95, the same E99/E101 world family should still identify a smaller subject-prior mask or nearby amplitude variant as the next coherent follow-up.
- Observed result: E107 conditioned E99 broad-plausible worlds on hypothetical E101 losses of `+0.000010` and `+0.000040` versus E95. Both outcomes required nearest-scenario selection and were marked model tension. The nearest scenarios still had E101 mean around `-0.000000821`, not a real positive loss. The top follow-ups in those strained subsets had positive p95 risk and did not promote E106 subject-prior gates.
- Why discard: a loss would not be an ordinary in-model branch choice. It would say the E99/E101 local+tail abstraction failed to represent the realized public world for E101. Rescuing the same branch with masks would overfit a model that the public result just falsified.
- Implementation issue possible: medium. E107 is a conditional decision map and inherits E99's two-term transfer abstraction. A richer future public-world model might explain an E101 loss, but the current E104/E106 universe does not.
- Bottleneck implication: E101 is a true sensor, not a file family to keep adjusting regardless of feedback. If it loses, return to full E89 or broader structural/block-state questions rather than narrowing E101.
- Do not repeat: after a negative E101 result, do not submit subject-prior-gated E106 rows or higher-alpha E104 rows as if they are conservative repairs. First rebuild the public-world model.

## FH96. E101 tie/loss can be rescued by stronger same-line rollback

- Failed hypothesis: if E101 ties or loses, the next coherent repair should still stay on the same active Q2/S3 rollback line, either by submitting E108 amp050/amp038 or by shrinking/masking the same cells.
- Observed result: E109 sampled `200000` active-cell hidden-label worlds under global and subject priors. Under subject priors, E101 small-loss and large-loss buckets have mass `0.355350` and `0.244350`. Those buckets are driven by missing high-impact S3 support: top10 support rate drops from `0.916933` in edge wins to `0.805226` in small losses and `0.719218` in large losses. In subject small-loss worlds, E108 amp050/amp038 active mean versus E101 is `+0.000011723` / `+0.000006026`, with beat-E101 rate `0`; large-loss worlds are worse again.
- Why discard: negative E101 feedback would mean the active rollback direction failed on the hard labels that matter most. More rollback on the same cells amplifies that failure; the active-cell-only ranking instead favors retaining E95/E90/E86 behavior.
- Implementation issue possible: medium. E109 is active-cell-only and does not forecast the full public LB for non-active E89/E90/E86 movements. It is strong enough to reject same-line E108 rescue after tie/loss, not strong enough to automatically choose the next full-file branch.
- Bottleneck implication: E101 tie/loss should be treated as active-label world mismatch, not as an amplitude tuning problem. The remaining live questions become retained structure, active-cell restoration, or a different non-active diffuse-tail hypothesis.
- Do not repeat: after an E101 tie/loss, do not submit E108, E104 high-alpha, or E106 subject-prior masks as the next default. Rebuild the public-world model or test a genuinely different retained-structure/non-active-tail question.
