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

## FH97. E101 tie/loss can be rescued by full E89 or non-active tail graft

- Failed hypothesis: if E101 ties or loses because its active cells failed, full E89 or a non-active E89/E85/E90/E86 graft should still recover the useful diffuse-tail structure outside the failed active cells.
- Observed result: E110 built `45` unique candidates from controls, active-restored E89/E85 variants, and E95-to-E89/E85/E90/E86 non-active grafts. Active-loss-safe non-control rows existed (`36`) and `8` rows qualified as diagnostic sensors, but strict candidates were `0` and no submission was materialized. The best non-control row, non-active `S1/S2/S3` E86 alpha `0.25`, still had broad mean/p95 vs E95 `+0.000000714` / `+0.000002798`; active-restored E89/E85 variants also failed broad E95-conditioned stress.
- Why discard: restoring active cells handles the E109 loss bucket locally, but the residual diffuse movement remains broad-risk-positive under E95-conditioned worlds. That is not a strict expected-improvement branch.
- Implementation issue possible: medium. E110 inherits E99's local+tail abstraction and E109's simulated active-loss worlds. It is strong enough to reject automatic E89/non-active fallback after E101 loss, not strong enough to prove that all future non-active-tail hypotheses are dead.
- Bottleneck implication: an E101 tie/loss would leave E95 as the standing best and require a rebuilt public-world model. The easy route from active-cell failure to broader E89 tail is not supported.
- Do not repeat: after a negative E101 result, do not automatically submit full E89, active-restored E89/E85, or E95-to-source non-active grafts. Use E89 only as a deliberate high-information diffuse-tail sensor, not as a rescue.

## FH98. Visible raw lifelog context can rescue Q temporal prediction directly

- Failed hypothesis: because E112 showed stronger temporal persistence in Q targets, daily raw lifelog context should replace missing nearby labels and make broad Q/Q3 temporal movement submission-safe.
- Observed result: E113 aggregated `114` raw daily coverage/context features and found complete train/test raw coverage (`1.000000`/`1.000000`). Despite that, raw+subject-prior worsened temporal holdout LogLoss versus subject prior on Q targets by `+0.038804`, S targets by `+0.058534`, and E95-active axes by `+0.059881`. Random within-subject also worsened on average, and Q2's random-only gain contradicted its temporal degradation. Only S3 improved in temporal holdout by `-0.004643`.
- Why discard: raw context contains some ranking signal, but it does not translate into calibrated temporal LogLoss after subject prior. The random/temporal divergence is a LeJEPA-style shortcut warning, not evidence of a healthy latent.
- Implementation issue possible: medium. E113 uses a logistic diagnostic head over coverage-style raw aggregates, not a rich representation learner. The discarded claim is narrower: visible raw context in this form should not be promoted into a broad Q/Q3 probability movement or used to replace E101.
- Bottleneck implication: Q temporal state likely exists but is still mostly unobservable in a submission-safe way. S3 remains the only raw-context temporal survivor, which fits the S subject/block-state explanation for E95.
- Do not repeat: building broad Q/Q3 raw-context submissions from daily raw coverage, AUC, or random-split gains. Require temporal holdout calibration improvement after subject prior first.

## FH99. Raw context can pre-validate E101 active-cell support labels

- Failed hypothesis: even if E113 rejected broad raw-context prediction, raw context might still serve as a narrow energy for the `50` E101 active Q2/S3 cells by assigning higher probability to the hard labels that would make E101 beat E95.
- Observed result: E114 compared global prior, subject prior, raw+prior, and validation-gated raw support over the active cells. Subject prior gives expected E101-vs-E95 delta `+0.000003926` with beat probability `0.336655` and mean support `0.587686`; raw+prior worsens that to `+0.000007010`, beat probability `0.238325`, and mean support `0.579426`; validation-gated raw is still worse at `+0.000007229`, `0.230710`, and `0.575835`.
- Why discard: the active-cell world is S3-dominated (`0.935862` of flip benefit), and raw lowers S3 support from `0.604450` under subject prior to `0.589463`. Q2 raw support rises slightly, but Q2 is only `0.064138` of the active-cell benefit and its raw temporal delta was invalid in E113.
- Implementation issue possible: medium. E114 uses E113's raw diagnostic probabilities, so a richer raw representation could change the support estimate. The discarded claim is narrower: the current visible raw context cannot be used as independent evidence that E101's active hard-label world is public-likely.
- Bottleneck implication: raw context is now demoted twice. It cannot rescue broad temporal Q/Q3 calibration, and it cannot pre-certify the S3-heavy E101 active-cell branch. E101 remains a public sensor about hidden local S3 labels, not an internally raw-validated expected-improvement file.
- Do not repeat: promoting raw-supported E101 masks, raw-gated active-cell rollback, or Q2 raw exceptions before a new raw latent shows both temporal calibration gain and active-cell support gain, especially on S3.

## FH100. Existing documented submissions hide an untested E95-like replacement

- Failed hypothesis: because E95 improved public by only `0.0000153107`, the documented submission universe should already contain another E95-shaped hard-tail candidate that is lower-risk than E95 and can be promoted without waiting for E101 feedback.
- Observed result: E117 parsed documented submission references, resolved `4477` files, deduplicated them to `4031` unique prediction tensors, and found only `10` E95-like neighbors. Only `4` had no higher E72-adverse exposure than E95: E101, E85, and two E108 post-E101-win variants. The closest non-E95 neighbor E89 had slightly higher E72-adverse exposure (`0.000799109`) than E95 (`0.000788914`), while E101 was only a `50`-cell Q2/S3 micro edit vs E95.
- Why discard: the E95 neighborhood is sparse and already interpreted. There is no hidden old-file family that cleanly lowers the tail while preserving E95's public-positive geometry.
- Implementation issue possible: low-medium. E117 only searches files referenced by existing reports and markdown, so an unreferenced local CSV could still exist. But for the documented experiment universe, the negative result is direct and deduplicated at prediction-tensor level.
- Bottleneck implication: the frontier is a narrow target-axis hard-tail compromise, not a candidate-indexing failure. Further progress likely requires E101 public feedback or a genuinely new structural/block-state movement, not another rescore of old submissions.
- Do not repeat: old-submission universe search as the next default path, or unconditional E108 promotion before E101 feedback. Use E117 only as a negative scarcity gate.

## FH101. Train-label flanks certify E101 before public feedback

- Failed hypothesis: visible train flanks around hidden blocks make E101 locally expected-positive enough to treat it as certified before public feedback.
- Observed result: E118 found that the best flank prior `edge_endpoint_beta` improves beat-E95 probability from subject prior `0.337185` to `0.437780`, but expected delta remains positive at `+0.000003014` per all cells and match-edge probability is only `0.120745`.
- Why discard: flanks are useful support but not enough. Active cells are also enriched for flank conflict, which means transition uncertainty rather than deterministic support.
- Implementation issue possible: low to medium. The flank model is deliberately simple and uses reconstructed block context, but it directly tests the low-cost visible-context certification claim.
- Bottleneck implication: E101 is a transition-state public sensor, not a guaranteed improvement. The hidden public labels still decide whether the visible flank clue is strong enough.
- Do not repeat: using flank support to submit E108, increase E101 amplitude, or build same-line masks before actual E101 feedback.

## FH102. Flank-gated E101 variants can replace full E101 before feedback

- Failed hypothesis: the E118 flank/edge support signal can be converted into a safer pre-feedback submission by applying the E95-to-E101 move only on flank-supported active cells.
- Observed result: E119 generated `602` flank/support/edge/flip-benefit gated variants and found `66` E101-pass rows but `0` E101-dominating rows. No submission was materialized. Active-all scale `1.50` improved broad mean/p95 versus E101 but dropped beat-rate from `0.983488` to `0.980881`; active-all scale `2.00` improved mean further but failed E101-pass and dropped beat-rate to `0.977984`.
- Why discard: the visible flank signal is distributed and interpretive. Hard-gating by flanks, edge rank, support probability, or flip benefit removes E101's scenario support faster than it removes risk.
- Implementation issue possible: medium. The selector family is handcrafted and the stress model is still E99/E101-conditioned rather than public labels. But it directly tests the low-cost replacement claim and no selector came close to dominance.
- Bottleneck implication: the next public information is still the full E101 active-set law, not a visible-flank subset. Flank support can explain a future E101 win, but cannot certify or replace it.
- Do not repeat: pre-feedback E119-style flank/support subset gates over E101 unless E101 public feedback changes the branch.

## FH103. E101 win unlocks same-line amplitude followups

- Failed hypothesis: E101 would beat E95, or at least land close enough to the E116 tie/win bands that E108/E104 amplitude-up, E106 subject-prior masks, or E119 flank gates should become the next same-family submission.
- Observed result: actual E101 public LB is `0.5763003660`, which is `+0.0000090362` worse than E95 and therefore E116 `small_loss`. It still beats mixmin by `0.0000062745`, but that only preserves `40.98%` of E95's mixmin gain. The actual public delta is `+0.0000252415` worse than the local E101 stress mean and `+0.0000106001` worse than local p95.
- Why discard: the observed public branch is exactly the pre-registered loss-side model-tension branch. Same-line amplification would be post-hoc rationalization of a direction that failed to beat the frontier.
- Implementation issue possible: low. The public LB is external feedback. The only caveat is that it gives aggregate LogLoss, not per-target labels, so it closes automatic same-line followups but does not identify the failed cells directly.
- Bottleneck implication: the bottleneck is now the E95/E101 boundary itself. E95 is right enough to remain best; E101 is right enough to beat mixmin but wrong enough to lose the frontier. The local stress model missed that tail.
- Do not repeat: submitting E108 amp050/amp038, E104 higher-alpha, E106 subject/S3 masks, E119 flank-gated variants, full E89, or non-active grafts as automatic post-E101 repairs.

## FH104. Exact E101 public score can directly identify the next same-line gate

- Failed hypothesis: once E101's exact small-loss score is known, the active-cell inverse posterior should identify a stable subset/gate that can be submitted as the next E95-to-E101 repair.
- Observed result: E121 found that the exact observation requires `0.657165` of active-cell flip benefit. Greedy high-impact support first beats mixmin at `21`, matches the observed boundary near `22`, and first beats E95 at `23`. Exact-observed worlds are common under local/flank priors (`~0.044-0.047`) but the posterior is prior-dependent and does not expose a clean visible selector; global prior makes the exact world rare (`0.007963`).
- Why discard: the exact public score narrows the hidden label budget, but it does not reveal which high-impact S3 cells are support/adverse without using the leaderboard as labels. A submission chosen from this exact posterior would be public-score fitting unless backed by an independent sensor.
- Implementation issue possible: low-medium. The active-cell LogLoss map is deterministic, and the simulations are stable at `300000` worlds per prior. The caveat is public subset normalization; this affects absolute rates but not the qualitative knife-edge result.
- Bottleneck implication: the same-line frontier is underidentified at one or two high-impact S3 cells. Progress requires a non-public sensor for those cells or a move to a different hidden-structure hypothesis.
- Do not repeat: creating E101 variants by fitting the exact E101 public delta, or treating posterior cell support from E121 as target labels.

## FH105. E119 local transfer or existing visible priors can certify the post-E101 boundary

- Failed hypothesis: the pre-public E119 local-transfer stress, or the existing subject/flank/raw support priors, should identify a same-line E101 repair after the exact E101 small-loss result is known.
- Observed result: E122 found that E119 local transfer expected active-all E101 to improve versus E95 by `-0.000016205`, while actual public was `+0.0000090362`; it missed the sign and E116 branch. Simple visible priors explained the aggregate branch much better: `raw_full_subject_prior_y1` expected `+0.000008889`, `flank_conflict_flat` `+0.000009521`, and `flank_both_distance_beta` `+0.000009532`. But the critical rank-23 S3 cell, whose support would be the first greedy count that beats E95, remains high-support under subject, edge, raw, and posterior views (`0.958333`, `0.972222`, `0.864418`, `0.940119`).
- Why discard: E119 is over-optimistic for this boundary, while the simple priors are explanation sensors, not action sensors. They match the aggregate small-loss branch but do not supply a non-public rule for which high-impact S3 cell to withhold.
- Implementation issue possible: low-medium. E122 reuses E114/E118/E121 tables, and the script now regenerates ignored E118/E121 intermediate cells if absent. A richer future S3-cell sensor could still exist, but these existing sensors do not certify it.
- Bottleneck implication: same-line post-E101 progress is blocked by cell-level underidentification, not by lack of aggregate branch explanation. The public boundary is visible in simple priors at the score level but not resolvable into a safe probability edit.
- Do not repeat: using E119 local-transfer optimism, E121 inverse posterior, or E122 best aggregate-prior match to submit another E95-to-E101 gate. Require a genuinely new non-public S3-cell signal or switch to a different hidden-structure test.

## FH106. Cross-target transition motifs can certify the missing E101 S3 cell

- Failed hypothesis: because the decisive E95/E101 boundary is S3-heavy and near train-label flanks, previous/next Q/S target-state motifs excluding S3 should provide an independent signal for whether the rank-23 S3 cell is support or adverse.
- Observed result: E123's train-only `motif_no_s3` head failed temporal-tail validation by `+0.135183` logloss versus subject prior; `motif_full` and `motif_plus_subject` failed by `+0.246239` and `+0.349065`. Interleaved validation was also worse for every motif head. Rank-23 support remained high: `0.943564` under no-S3 motif and `0.984326` under motif+subject.
- Why discard: the feature can create an apparently useful aggregate branch and can make rank 22 look adverse, but its validation geometry is unhealthy and the decisive rank-23 cell remains support-like. This is a shortcut/collapse warning, not a public-independent gate.
- Implementation issue possible: medium. E123 uses a simple logistic head over neighbor target-state features rather than a deep sequence model. The discarded claim is narrower: the visible cross-target neighbor motif, in this calibrated train-only form, cannot justify a same-line E101 repair.
- Bottleneck implication: the E95/E101 plateau is not explained by a missed full-target transition-state feature. The blocker remains one-cell-scale S3 underidentification, and the remaining viable path is a materially different hidden structure or a much stronger S3-specific non-public sensor.
- Do not repeat: building E101/E95 gates from Q/S neighbor-state motif scores, motif aggregate public-delta matches, or rank-22-only improvements unless the motif first improves temporal validation and reverses rank-23 support without using public LB.

## FH107. Pre-E101 E99 local+tail transfer can rank the next file after E101

- Failed hypothesis: the E99 two-term transfer model, calibrated on E72 failure and E95 success, should remain a reliable candidate ranker once E101 public feedback is known.
- Observed result: E124 found that broad-plausible E99 worlds predicted mean E101 delta `-0.000031516` versus actual `-0.000006275`, an over-optimism of about `0.000025241`. Only `57/3452` broad-plausible worlds matched the E101 ordering, and the E101-plausible subset kept E95 as live winner mode with `0.929825` rate. Future candidates were weak: E89 beat-E95 `0.052632`, E85 `0.017544`, E90/E86 `0`.
- Why discard: E99 captures a real hard-tail axis, but E101 reveals an additional boundary variable at the Q2/S3/S3-heavy active-cell edge. Reusing E99 broad order after E101 would inherit a model that already missed the held-out sensor by larger than the E95 edge.
- Implementation issue possible: low-medium. E124 reuses E96 scenario construction and E99 local deltas, so its conclusion is about this two-term abstraction, not every possible public-world model.
- Bottleneck implication: the next same-family file is not hidden inside E99's pre-E101 ranking. The bottleneck is boundary resolution, not lack of another broad local+tail rescore.
- Do not repeat: promoting E89/E85/E90/E86 by pre-E101 E99 broad mean, p95, or beat-rate without conditioning on the observed E101 small-loss branch.

## FH108. The remaining E101-compatible world is Q2/S3 diffuse-tail allocation

- Failed hypothesis: after E101, the surviving public-world subset should still be dominated by the `q2s3` mask that made E89 interesting in E100.
- Observed result: E125 found `0/368` E101-plausible scenarios under the `q2s3` mask. The survivors are dominated by `all` and `e72_top50_hard` masks (`43/57`), low-gamma/deterministic allocation (`40/57`), median alpha collapse from `3.310470` to `0.791985`, and E101-vs-E95 tail neutrality (`tail_e101 - tail_e95` median `~0`).
- Why discard: q2s3 worlds make E101 too favorable versus E95 (`pred_vs_e95_e101` mean `-0.000028957`), exactly the error the public result rejected. The surviving worlds explain E101 by compressing local transfer and removing E101's tail advantage, not by selecting better Q2/S3 cells.
- Implementation issue possible: low. E125 is a deterministic anatomy of E124 scenarios. It does not claim every possible q2s3 model is false, only that the E99/E96 q2s3 diffuse-tail survivor story is false after E101.
- Bottleneck implication: same-line Q2/S3 rollback is no longer merely underidentified; the E101-compatible residual world points away from it.
- Do not repeat: using E100 q2s3 enrichment, E89's diffuse-tail pocket, or q2s3-only E96 masks as the next default public rationale.

## FH109. E101-compatible broad survivors secretly charge the E101-active cells

- Failed hypothesis: although `q2s3` masks have no E101 survivors, the broad/all survivors might still spend most of their selected public-miss budget on the `50` E101-active Q2/S3 cells, leaving a narrower same-line gate alive.
- Observed result: E126 reconstructed selected cell budgets and found that E101-plausible worlds allocate only `0.180513` of budget mass to Q2/S3 and only `0.011234` to E101-active cells. Broad-q2s3 worlds, by contrast, allocate `1.000000` to Q2/S3 and `0.584840` to E101-active cells. E101-plausible worlds are also low-alpha (`0.791985` median), less E95-fallback-heavy (`0.356179`), and more between-train-runs-heavy (`0.621562`).
- Why discard: the public-compatible loss surface is not merely a broad scenario family hiding the same E101 cell budget. It is mostly outside the cells E101 changed.
- Implementation issue possible: low-medium. E126 reconstructs E96/E124 scenario weights deterministically and joins existing hidden-row metadata. The caveat is that the public labels remain unobserved; this is still a scenario-world anatomy, not direct labels.
- Bottleneck implication: the same-family E101/E89/Q2S3 line is now closed by scenario family, tail relation, and selected-cell budget. The remaining bottleneck is transfer-shrinkage or a different hidden structure, not a missing Q2/S3 amplitude/gate tweak.
- Do not repeat: E101-active-cell masks, Q2/S3 diffuse-tail variants, active-cell alpha sweeps, or E89-style Q2/S3 fallback as the default next public candidate unless a new independent non-public sensor overturns E126.

## FH110. Simple metadata alone is enough to submit a transfer-shrinkage gate

- Failed hypothesis: after E126 identifies broad transfer-shrinkage, target/context/position/fallback metadata should directly identify the E101-compatible budget cells strongly enough to generate the next submission.
- Observed result: E127 found real but insufficient metadata signal. The best hidden-block-heldout metadata view `target_context_tail_e72bin` reached CV JS `0.073253` and top50 truth-mass capture `0.252521`, while target-only was weak at JS `0.316796` and top50 mass `0.037897`. The much stronger view was not metadata alone but scenario-level `broad_tail_equal`, with JS `0.038002` and top50 mass `0.293969`.
- Why discard: metadata can diagnose and weakly rank cells, but it does not yet provide a selector-scale action gate. The missing object is a tail-neutral/low-alpha representation, not a few categorical feature rules.
- Implementation issue possible: medium. E127 uses category-mean prediction rather than a richer model; a future representation learner could improve it. The discarded claim is only the direct simple-metadata submission path.
- Bottleneck implication: the field is partly visible but not translated. Progress requires building a representation from the tail-neutral proxy and then proving margin-scale probability movement.
- Do not repeat: submitting a file from target/context/fallback/E72-bin metadata ranking alone, or treating E127 metadata CV as a public score forecast.

## FH111. Transfer-shrinkage composite ranker can choose the next submission

- Failed hypothesis: E127's tail-neutral/low-alpha field can be compressed into one candidate-risk score that ranks live E85/E86/E89/E90/noQ2 submissions well enough to choose the next file.
- Observed result: E128 found strong component metrics against known public deltas: `q2s3_delta95_l1` Spearman `0.958042`, `tail_equal_law_resid_ratio` `0.888112`, `e72_adverse_exposure_e101_plausible` `0.881119`, and `e101_active_delta95_l1` `0.874126`. But the combined `transfer_shrinkage_risk_index` only reached Spearman `0.440559` and would rank live candidates E85/E89/noQ2/E90/E86 despite E124/E126 showing that same-family successors have weak E95-beat support after E101.
- Why discard: the components measure real risks, but a single scalar loses the separation between active-cell rollback, Q2/S3 rollback, E72 exposure, and tail-equal law residual. That compression would over-promote conservative old files without independent upside.
- Implementation issue possible: medium. E128 uses a deliberately simple composite. A learned ranker could improve, but the discarded claim is narrower: the current composite is not a safe submit selector.
- Bottleneck implication: transfer-shrinkage is now a veto/decomposition layer, not the candidate-selection answer. The next improvement still needs selector-scale probability movement or a new public-free representation.
- Do not repeat: submitting E85/E89/noQ2 solely because transfer-shrinkage risk is low, or replacing E124/E126 public-world stress with one combined energy scalar.

## FH112. Existing universe contains a novel transfer-shrinkage-safe successor

- Failed hypothesis: once E128 veto components are kept separate, the existing local/documented submission universe should contain at least one novel material candidate that passes those vetoes and can become the next submission.
- Observed result: E129 collected `116044` candidate paths and loaded `65865` unique prediction tensors. Strict veto left only `3` tensors, all same-family; strict actionable left only E85 and E101; relaxed material survivors add only E89. `gate_strict_novel_actionable` was `0`.
- Why discard: the only survivors are already interpreted files from the E85/E89/E101 hardtail line, and that line is weakened by E124/E126 after the E101 small-loss public observation. No hidden old file solves the plateau.
- Implementation issue possible: low-medium. E129 depends on filename-based same-family tagging and local/report-referenced file availability. But the scan is broad enough that the discarded claim is strong for the current workspace universe.
- Bottleneck implication: candidate selection over existing files is not the immediate path. The missing object is a new representation/movement that satisfies the vetoes, not another old-file rank.
- Do not repeat: full local submission rescans, E85/E89/noQ2 promotion by low veto energy, or "maybe an old CSV is hiding the answer" unless a new representation family has actually produced new files.

## FH113. Tail-neutral density can be directly translated into an E95 successor

- Failed hypothesis: the E127 tail-neutral/low-alpha density field should be enough to synthesize a new E95-neighborhood file by moving selected cells toward existing donors such as E86/E90/E89/E85/noQ2/mixmin.
- Observed result: E130 generated `1792` density-shaped variants and evaluated `698`. It found `25` E95-relative local-strict variants and `19` E129-veto-actionable variants, but `0` variants in the intersection and `0` final submit-gate variants. The strongest local strict rows came mostly from E86/E90 low-alpha masks, but they increased post-E101 sensor exposure; the safest rows were only micro-moves and failed strict/material gates.
- Why discard: density identifies where the post-E101 budget may live, not the direction/amplitude that improves probabilities there. Direct movement toward old donors recreates the same conflict E129 exposed: local margin lives in an exposure-adverse region, while veto-safe movement is too small.
- Implementation issue possible: medium. E130 only tests donor interpolation around E95, not a learned representation or new model family. The discarded claim is specifically the simple direct density-shaped synthesis rule.
- Bottleneck implication: the plateau is not solved by "move on better cells." The next representation must learn a movement direction that is simultaneously local-upside and transfer-veto-safe.
- Do not repeat: submitting E86/E90 low-alpha density rows, tail-equal micro-moves, or density-only E95 blends unless they pass both local strict E95 improvement and post-E101/E129 separated veto gates.

## FH114. Local-upside density atoms can be rescued by safe correction atoms

- Failed hypothesis: E130 failed only because local-upside and veto-safe atoms were tested independently; adding a safe mixmin/E85 correction or clipping high-risk cells should create an overlap.
- Observed result: E131 generated `6384` local+safe atom combinations and risk-clipped local variants. It found `651` local-strict candidates and `208` veto-actionable candidates, but `0` local-strict plus veto-actionable candidates and `0` submit-gate candidates. No evaluated candidate had negative post-E101 sensor mean.
- Why discard: the local-upside direction itself carries the post-E101/E72 exposure that the veto rejects. Safe atoms can make a candidate safe only by giving up the E95-relative local improvement, not by cancelling a small removable component.
- Implementation issue possible: medium. E131 tests linear logit-space combinations and hard-tail clipping over the E130 atom family, not all possible nonlinear representations. The discarded claim is the cheap blend/correction rescue path.
- Bottleneck implication: the next movement must be learned or constructed as safe from the start. Transfer-shrinkage density is still a health target, but it is not a corrective layer over old local-upside donors.
- Do not repeat: local+safe donor blending, E86/E90 low-alpha plus mixmin/E85 correction, or hard-tail clipping of the same E130 local atoms unless a new independent representation changes the base movement direction.

## FH115. Donor-free E95 combo gradients contain a safe successor tangent

- Failed hypothesis: the post-E131 failure was caused by old donor contamination, and a direct E95 combo-set gradient would reveal a local-upside direction that can be masked into the transfer-veto nullspace.
- Observed result: E132 generated `4590` gradient-nullspace candidates and evaluated `698`. It found `843` veto-actionable gradient rows but `0` gradient local-strict rows, `0` local-strict plus veto-actionable rows, and `0` submit-gate rows. The best local row improved local stress by `-0.000112772` but failed strict hidden/block/Q2S3/world support and carried positive post-E101 p95 exposure. The best post-E101 sensor rows were locally non-strict.
- Why discard: removing donors did not make local gradient reward and transfer-safe geometry overlap. Current combo gradients can produce attractive local loss reductions, but those reductions are not structurally healthy under the hidden/block and post-E101 tests.
- Implementation issue possible: medium. E132 tests first-order BCE-style combo gradients and sparse masks around E95, not a learned nonlinear latent. The discarded claim is specifically that the current E95 tangent field contains a cheap safe successor.
- Bottleneck implication: the plateau is not a blend-weight or donor-source problem. It is a latent tangent-space mismatch: the visible local gradient and the public-safe tail geometry do not agree in the same cells/targets.
- Do not repeat: E95-neighborhood gradient/nullspace mask sweeps, top-gradient cell pruning, or LOO-combo gradient rescaling as a submission source unless the target representation itself changes and passes strict local support before veto checks.

## FH116. Simple metadata can recover the local-safety co-location field

- Failed hypothesis: after E132, the next latent target could be built directly from visible target/subject/context/block metadata because those metadata should predict where local gradient reward and tail safety co-locate.
- Observed result: E133 found that even the best context `all_sign` places only `0.161830` of local reward mass in veto-null+density70. The best hidden-block-CV category view, `subject_target`, has JS `0.240700` and top50 truth-mass capture `0.048280`. Local top50 cells in `all_sign` are `44%` Q2/S3 and `42%` S3, but co-located top50 cells are only `2%` Q2/S3 and instead mostly Q3/Q1.
- Why discard: metadata weakly describes the target-family shift but does not recover top co-located cells at selector scale. It also removes the old Q2/S3 explanation rather than repairing it.
- Implementation issue possible: medium. E133 uses categorical mean predictors, not raw sequence models or learned block embeddings. The discarded claim is only the simple metadata target path.
- Bottleneck implication: the next latent cannot be a target/context/fallback/E72-bin table. It needs a richer representation, likely raw/run/block-context based, and should be judged by whether it predicts the Q3/Q1-heavy safe remainder without reviving Q2/S3 tail risk.
- Do not repeat: metadata-only co-location gates, Q2/S3 rollback resurrections based on local top cells, or direct movement on E133 co-located cells without a stronger raw/run/block predictor.

## FH117. Raw overnight block context directly recovers the safe remainder

- Failed hypothesis: the Q3/Q1-heavy E133 safe remainder is visible enough in raw overnight/run/block context to become the next JEPA-style target or direct selector.
- Observed result: E134 used hidden-block holdout over `1750` cells and `36` hidden blocks. The best raw/block predictor was `night_all_blockknn` / `target_knn8` with top50 truth-mass capture `0.073497`, cosine `0.498528`, JS `0.260922`, and predicted top50 mix `Q1:37,Q3:4,S4:9`. The best metadata-only baseline already captured `0.063040`.
- Why discard: raw context is only slightly better than metadata and far below selector-scale recovery. It does preserve Q2/S3 suppression, but it does not identify enough of the safe remainder to justify probability movement.
- Implementation issue possible: medium. E134 tests PCA block aggregates, ridge, and target-wise kNN; it does not rule out richer sequence models or a different representation target. It rejects the cheap raw-block visibility path.
- Bottleneck implication: the E133 safe remainder is not simply hidden in raw overnight block geometry. The current wall is not just "use raw context as JEPA context"; the target or movement direction itself must change.
- Do not repeat: direct raw-block kNN/ridge co-location gates or raw-view ranking of E133 cells as a submission source unless a new target or substantially stronger heldout recovery appears.

## FH118. Existing prediction disagreement reveals the safe remainder

- Failed hypothesis: the Q3/Q1-heavy E133 safe remainder is already present in the manifold of old submissions, so prediction disagreement, row prediction PCA, uncertainty, or per-cell old-submission scalars can recover it better than raw/block context.
- Observed result: E135 used `12` known submission tensors and hidden-block holdout over `1750` cells. The best predictor, `row_prediction_pca_meta` / `ridge`, captured top50 truth-mass `0.063430`, barely above metadata-only `0.063040` and below E134 raw/block `0.073497`. The predicted top50 stayed Q2/S3-suppressed but did not recover selector-scale mass.
- Why discard: old prediction geometry is mostly restating target/metadata priors for this teacher. It is not a hidden selector for the safe remainder and does not justify another old-submission blend/rank.
- Implementation issue possible: medium. E135 tests PCA/scalar/manifold summaries of existing submissions, not every possible nonlinear meta-model. The discarded claim is the cheap old-prediction-manifold visibility path.
- Bottleneck implication: the plateau is not caused by failing to rank the old CSV manifold. The safe target itself is weak under both raw/block and old-prediction contexts, so progress requires a different target representation or independent supervision.
- Do not repeat: old-submission disagreement gates, prediction-PCA ranking, uncertainty-only blending, or direct probability movement from E133/E134/E135 cell ranks unless a new latent target materially improves hidden-block-heldout recovery.

## FH119. E136 block-target state makes current E95 gradients safe

- Failed hypothesis: E132's donor-free gradient failed because the cell masks were weak; replacing them with E136 predicted block-target safe-state masks should make local upside and transfer safety overlap.
- Observed result: E137 generated `1980` block-target-gated gradient variants and evaluated `698`. It found `0` local strict variants, `0` transfer-veto-actionable variants, `0` local-strict plus veto-actionable variants, and `0` submit-gate variants. The best local delta versus E95 was `-0.000043592`, and the best post-E101 mean was `-0.000040388`, but post-E101 p95 stayed positive and transfer-veto components failed.
- Why discard: the visible block-target state helps locate mean-improving regions, but the current combo-gradient decoder still carries unsafe tail/e72 exposure and poor tail-equal law alignment. The problem is not only support selection; direction and amplitude are wrong.
- Implementation issue possible: medium. E137 tests donor-free first-order gradients, not a learned nonlinear block-target decoder. The discarded claim is specifically "E136 state mask times current E95 gradient is enough."
- Bottleneck implication: the live representation branch remains block-target state, but movement must be learned or defined differently. The plateau is now a decoder problem, not merely a context visibility problem.
- Do not repeat: E95 combo-gradient masks over E136 state, larger scale sweeps over the same masks, or submitting mean-improving block-target-gradient rows without strict/veto/post-E101 p95 survival.

## FH120. E136 state plus transfer-safe overlap is enough to create a safe movement

- Failed hypothesis: E137 failed only because it did not explicitly intersect the visible block-target state with E132/E128 transfer-safe veto-null and low-adverse masks.
- Observed result: E138 generated `1314` block-target x veto-null overlap variants and evaluated `698`. It found `373` transfer-veto-actionable variants, but still `0` local strict variants, `0` local-strict plus veto-actionable variants, and `0` submit-gate variants. The best evaluated row improved local all stress by `-0.000030467` and post-E101 mean/p95 by `-0.000055772` / `-0.000015691`, but failed strict actionability with only `2/3` combo-set wins, `1/3` tail-neutral sets, hidden Q2/S3 `+0.000084793`, and world support `+0.001092051`.
- Why discard: state-veto co-location fixes one side of the problem but not the structural decoder. The overlap can be transfer-safe while still violating the all-set tail and world/raw laws that distinguish E95 from E101-style local optimism.
- Implementation issue possible: medium. E138 still uses current E95 combo gradients and mask intersections, not a learned decoder. The discarded claim is narrower: co-location of E136 state and E132/E128 safety masks is not sufficient.
- Bottleneck implication: the current wall is now specifically direction/amplitude decoding inside a visible block-target state. Visibility and safety-region overlap exist; calibrated all-set/world-preserving movement does not.
- Do not repeat: more state-veto mask multiplication, top-fraction sweeps, or scale-only variants on the same gradient. Future work should first define a decoder target that rewards all-set tail neutrality and world/raw hidden support before materializing probabilities.

## FH121. Combo-set sign consensus is enough to decode block-target state

- Failed hypothesis: E138's failure came from conflicting gradient signs across combo-set views, and filtering to cells where `inverse_top`, `raw05_compatible`, and `all_sign` agree would make the block-target movement strict.
- Observed result: E139 generated `1188` set-consensus variants and evaluated `698`. It found `190` transfer-veto-actionable variants, but `0` local strict variants, `0` local-strict plus veto-actionable variants, and `0` submit-gate variants. Every evaluated row passed all-margin and all-beats-base, but all `698` failed tail-neutral, world-nonworse, and raw-energy-nonworse gates. The best all-three consensus rows got `3/3` combo-set mean wins but only `1/3` tail-neutral sets.
- Why discard: combo-set mean agreement is a weaker condition than LogLoss tail health. It can align average local directions while still pushing probability mass into hidden world/raw and worst-tail regions that the frontier cannot afford.
- Implementation issue possible: medium. E139 still works inside E95 first-order gradient geometry and tests min/mean sign-consensus decoders, not a learned constrained decoder. The discarded claim is specifically that consensus filtering is the missing constraint.
- Bottleneck implication: the plateau is not caused by sign disagreement alone. The missing object is a decoder objective that directly models tail-neutral/world/raw nonworsening inside the visible block-target state.
- Do not repeat: all-three/pairwise gradient consensus filters, agreement-cell top-k sweeps, or combo-set mean-win promotions unless a new decoder first proves worst-tail and world/raw health.

## FH122. Tail/world-aware primitives are enough to decode the block-target state

- Failed hypothesis: if the decoder starts from single-cell directions that already satisfy local reward, worst-tail neutrality, world nonworsening, and raw-energy nonworsening, those primitives should accumulate into a safe E95 successor.
- Observed result: E140 evaluated `942` micro moves over `471` support cells. It found `119` tail/world/local primitives and only `3` tolerance-level strict primitives, all with negligible local reward. The `168` combined variants produced `0` local strict, `0` transfer-veto-actionable, and `0` submit-gate rows. All combined variants passed hidden-core, world, and raw checks, but all failed all-set tail neutrality; max tail-neutral count remained `1/3`.
- Why discard: primitive world/raw health can be made additive, but combo-set worst-tail health does not accumulate under this construction. The bottleneck is no longer generic world/raw support; it is exact worst-tail balancing across combo sets.
- Implementation issue possible: medium. E140 uses micro finite differences and top-k additive combinations, not a learned constrained optimizer. The discarded claim is specifically that primitive tail/world filters alone are sufficient.
- Bottleneck implication: the next decoder must identify and balance the specific failing combo-set tail axes. Broad primitive selection, sign consensus, and world/raw-safe top-k accumulation are not enough.
- Do not repeat: primitive top-k accumulation, tolerance-level strict-cell promotion, or world/raw-safe cell pools unless the candidate explicitly improves all-set tail-neutral count beyond `1/3`.

## FH123. E140 is blocked mainly by real combo-set tail failure

- Failed hypothesis: E140's all combined rows failing exact all-set tail neutrality means the main remaining decoder task is combo-set tail-axis balancing.
- Observed result: E141 applied small tolerances to E140's worst-tail deltas. At tolerance `1e-12`, tail pass became `129` and relaxed structural pass became `84`; at `1e-6`, relaxed structural pass became `91`. But relaxed plus E72 exposure pass stayed `0`, relaxed plus post-E101 p95 pass stayed `0`, and actionable stayed `0`. The best relaxed E72 gap was `+0.000003189534`, and best relaxed post-E101 p95 was `+0.000000141478`.
- Why discard: the exact tail gate counted numerical-zero raw05/all-sign deltas as failures. Once that artifact is removed, structural rows exist, but the transfer-tail budget still blocks them.
- Implementation issue possible: low for the audit; it reads existing E140 scored rows and recomputes boolean gates. Medium for generalization because it does not generate new predictions.
- Bottleneck implication: the next decoder should not spend cycles only improving tail-neutral count. It must lower E72-plausible exposure below the E95 threshold and make post-E101 p95 nonpositive while preserving local reward.
- Do not repeat: pure tail-axis balancing, exact-zero tail-gate conclusions, or relaxed-tail candidate promotion without E72/post-E101 transfer survival.

## FH124. Uniform shrinkage is enough to fix E140 transfer-tail budget

- Failed hypothesis: E140 relaxed structural rows only need smaller amplitude; shrinking the whole movement should reduce E72-plausible exposure and post-E101 p95 while preserving local reward.
- Observed result: E142 tested uniform keep factors `0.25`, `0.50`, `0.75`, and `0.90` over relaxed material parents. Uniform rows kept some local reward, but budget survivors remained `0` at every keep factor. Partial cell clipping with keep `0.25` or `0.50` also produced `0` budget survivors.
- Why discard: transfer-tail exposure is localized and threshold-like, not a smooth global amplitude problem. It only opened when high excess-exposure cells were fully rolled back to E95.
- Implementation issue possible: low for this family; the same script produced viable full cell-rollback rows under the same scoring pipeline.
- Bottleneck implication: the live decoder is not "smaller E140." It is "E140 minus specific transfer-budget-spending cells."
- Do not repeat: uniform shrink, global scale, or partial clipping sweeps over E140 relaxed rows as the main next submission path.

## FH125. E142's active/Q2S3 veto failure is irreparable

- Failed hypothesis: E142's failure of the older active/Q2S3 strict gate means the transfer-budget clipped residual branch cannot be made stricter without collapsing local reward.
- Observed result: E143 generated `80` E142 repair variants by rolling back E101-active/Q2S3/S3 cells. All `80` remained relaxed-submit, and `15` passed original strict-submit. The selected `submission_e143_activeq2s3repair_68ca656f.csv` rolls back `21` top Q2/S3-weighted cells, keeps local all-minus-E95 `-0.000009551358`, has E72 gap `~0`, post-E101 p95 `-0.000003368915`, and passes active/Q2S3 plus strict actionability.
- Why discard: the active/Q2S3 risk was localized. It can be cut at small local cost instead of invalidating the whole E142 residual decoder.
- Implementation issue possible: low for this repair family; the control E142 row was scored in the same run and correctly failed the active/Q2S3 gate.
- Bottleneck implication: the current frontier question is no longer "can transfer-budget residual movement survive the E101 lesson?" It can locally. The question is whether the E101-informed pruning generalizes to public labels.
- Do not repeat: treating E142's active/Q2S3 veto failure as a hard branch killer. Use E143 as the stricter public sensor, and keep E142 only as a higher-upside fallback if the veto proves overconservative.

## FH126. E143's coarse top21 full rollback is boundary-optimal

- Failed hypothesis: after E143 opened the strict branch, the best active/Q2S3 repair was exactly the coarse `top_q2s3_weighted_21` full rollback; any attempt to retain more movement would either fail strict gates or worsen post-E101 p95.
- Observed result: E144 generated `206` fine-boundary variants, with `32` original-strict rows and `9` rows that beat E143 locally while not worsening post-E101 p95. The selected `submission_e144_activeboundary_d7b4b331.csv` uses `top_q2s3_weighted_24`, keep factor `0.15`, keeps `185` changed cells, improves local all-minus-E95 from E143's `-0.000009551358` to `-0.000009725930`, and improves post-E101 p95 from `-0.000003368915` to `-0.000003430489`.
- Why discard: E143's full rollback was a coarse safe point, not the local boundary optimum. The active/Q2S3 cliff is finer and still allows a small amount of retained movement.
- Implementation issue possible: low for the tested grid; E144 re-scores E142 and E143 controls in the same pipeline and keeps E143 strict. It does not prove that the absolute optimum is found outside the scanned masks.
- Bottleneck implication: the live branch is extremely narrow. We can still extract a tiny amount of reward from the residual decoder, but the edge size is `1e-7` local scale, so this is a next-sensor refinement rather than a 0.54-path discovery.
- Do not repeat: assuming E143's coarse mask is optimal. Use E144 first; keep E143 as the conservative fallback if public rejects the fine retained tail.

## FH127. E144 is supported only by the tiny E144-over-E143 fine-tail edge

- Failed hypothesis: E146's support might be too narrow to matter; E144 could still be globally unhealthy versus E95 because public scores all `185` moved cells, not just the `24` cells that differ from E143.
- Observed result: E147 finds all `10/10` public-free priors prefer E144 over E95 on the full moved-cell set. Expected E144-minus-E95 deltas range from `-0.000049865515` to `-0.000012197928`, and simulated beat probability ranges from `0.583850` to `0.762700`. The inherited E143 body, not only the E144 fine-tail delta, carries the main favorable signal.
- Why discard: the visible-prior evidence is whole-file positive. E144 is not merely a 24-cell local-gate artifact.
- Implementation issue possible: medium. E147 is still a prior-world audit, not public labels. It can say the whole-file movement is coherent under train-derived priors, but public can still have a different hidden S3/Q3 mix.
- Bottleneck implication: the live risk is no longer "E144 has no broad support." It is target/component mismatch: nearest-hard priors oppose S3/Q3 even while Q1/S4/S2 and the inherited body are favorable.
- Do not repeat: dismissing E144 as only an E143 micro-tweak. If E144 fails, inspect S3/Q3 and fine-tail/body decomposition before assuming E143 was the expectation-safer file.

## FH128. Any E144 fine loss automatically points to E143 as the next file

- Failed hypothesis: if E144 loses to E95 but stays no worse than E101, the retained `keep0.15` fine tail is the natural culprit and E143 should be submitted as the clean contrast.
- Observed result: E148 conditions simulated E144 outcomes on E145 bands. Fine-loss-alive worlds have rate only `0.027696..0.033340`, and their responsibility is not consistently the E144-only fine tail. Global prior fine-loss blame is inherited-body/Q3/S2; nearest-hard blame is S3/Q3; subject blame is inherited-body/Q3/S3. In some fine-loss worlds the fine-tail component is still favorable or only weakly adverse.
- Why discard: the same numeric fine-loss band can be caused by inherited-body or broader target-body shortfall, not just retained S3 fine-tail movement.
- Implementation issue possible: medium. E148 is simulated from visible priors and does not reveal public labels. The discarded claim is not "E143 can never be useful"; it is "fine-loss alone is sufficient evidence for E143."
- Bottleneck implication: post-public branch decisions need target/component attribution, not only scalar LB bands. The plateau is partly an interpretation-resolution problem.
- Do not repeat: auto-submit E143 after any E144 fine loss. Use E145 banding plus E148 attribution first; E143 is justified only if failure is compatible with fine-tail/S3 retention.

## FH129. E144 is a new broad representation breakthrough

- Failed hypothesis: because E144 is supported by E146/E147/E148 prior-world audits, it might represent a new broad successor law beyond the E142/E143 residual branch.
- Observed result: E149 measures E144 in logit-space against known anchors. E144 cosine with E143 branch axis is `0.991918719`, with E142 branch axis `0.952146833`, and residual ratio versus E143 is only `0.126874959`. It is almost orthogonal to E101 and E72 public-negative axes (`-0.019625796` and `-0.024358970`), but that is avoidance of known bad axes, not a new independent direction.
- Why discard: E144's geometry is inherited branch geometry plus a small fine-boundary correction. Its value is as a branch-pruned sensor, not as evidence that a new broad latent family has been found.
- Implementation issue possible: low for geometry measurement; medium for public interpretation because hidden labels are still unknown. The discarded claim is only the broad-breakthrough framing, not E144's submission value.
- Bottleneck implication: the plateau is still a transfer-budget/calibration/branch-selection bottleneck. E144 may beat E95, but even a win would not by itself explain the route to 0.54.
- Do not repeat: describing E144 as a JEPA-style broad representation breakthrough. Submit and interpret it as a precise test of the E142/E143 residual branch and fine active-boundary pruning.

## FH130. E145 score band alone is enough for post-E144 action

- Failed hypothesis: the pre-registered E145 bands are sufficient to choose the next file, especially E143 after `fine_loss_branch_alive`.
- Observed result: E150 combines E145 with E148 and E149 and changes the fine-loss action. Fine loss is now `conditional_alive`, and E143 is allowed only if attribution points to fine-tail/S3 retention. E148 shows global fine-loss blame can be S2/Q3/inherited-body, subject blame can be inherited-body/Q3/S3, and nearest-hard blame can be S3/Q3/fine-tail. E149 shows the whole candidate is mostly E143 branch geometry.
- Why discard: a scalar score band cannot identify which component failed. Acting on E145 alone would turn public LB into a tuning target.
- Implementation issue possible: low for the decision table; medium for actual public interpretation because the future score is not known yet.
- Bottleneck implication: candidate selection is now an interpretation-resolution problem as much as a modeling problem. The next action must preserve attribution discipline.
- Do not repeat: auto-submit E143 after E144 fine loss, or close/rescue the branch from a scalar band without E148/E149 context.

## FH131. The current plateau is mainly missed old candidates or generic model capacity

- Failed hypothesis: the `0.5762913298` frontier exists because a better old submission, blend, top-count sweep, or ordinary model-capacity variant has not been selected yet.
- Observed result: E151 aggregates E98/E120/E129-E150 and finds the opposite pattern. E98's best known-LB selector p90 error is `0.0008164966`, `53.33x` the E95 edge; E101 was locally optimistic by `0.0000252415`; E129 found `0` novel strict actionable old-file successors; E130/E131/E132/E137/E138/E139 all have `submit_gate=0`; and the only live path is the narrow E142/E143/E144 branch with counts `35/15/9` and E144/E143 cosine `0.991918719`.
- Why discard: old-file search and direct decoder families repeatedly expose the same split: local reward exists, public-tail safety exists, but their intersection is tiny and mostly hand-pruned. This is not what a simple candidate-selection or capacity bottleneck should look like.
- Implementation issue possible: low for the audit because it only joins previously materialized reports and verifies control counts. Medium for the global claim because an untested genuinely new decoder could still exist.
- Bottleneck implication: the frontier is a selector-resolution and representation-to-probability decoder problem. The useful next branch must create a non-collinear movement that survives strict/E72/post101 p95 gates above `1e-5`, not rescore old CSVs.
- Do not repeat: old submission universe ranking, same-family blend/top-count sweeps, Q2/S3 amplitude tuning, or broad capacity experiments unless E144 public feedback specifically reopens that branch.
- Remaining question: can a new latent target encode transfer-tail budget and worst-tail geometry directly enough to produce a non-collinear, public-tail-safe probability movement?

## FH132. Branch-orthogonal projection is enough to escape E144 collinearity

- Failed hypothesis: E151's plateau may be solved by taking existing E137-E140 decoder rows, projecting away the E144 branch, and keeping the remaining non-collinear component.
- Observed result: E152 finds non-collinear signal everywhere (`4650/4650` source rows), but `0/2880` projected rows pass relaxed structural, E72-budget, post-E101, and active-veto/actionability together. The best local projected move is `-0.0000455468` but fails E72/structural/actionable gates. `relaxed_budget_post101` has `102` rows but actionability is false; `budget_post101_actionable` has `1` row but relaxed structural is false.
- Why discard: orthogonality is not the missing condition. Projection can preserve or enlarge local reward, but it does not make the decoder satisfy the public-tail and active-boundary constraints simultaneously.
- Implementation issue possible: medium. The audit reuses existing E137-E140 scored families and a finite projection grid, so a genuinely new decoder could still work. Low for this specific shortcut because controls and blocker intersections are explicit.
- Bottleneck implication: the live bottleneck is gate compatibility, not lack of non-collinear movement. The next model should predict why gates fail together, not search more top-k/alpha projections.
- Do not repeat: branch-orthogonal full/top50/top100 alpha sweeps over E137-E140 as the next default. Treat E152 outputs as training/diagnostic material for a gate-intersection latent instead.

## FH133. E152 all-four failure is a single scalar threshold problem

- Failed hypothesis: the zero all-four intersection in E152 is mainly caused by a threshold that is slightly too strict; relaxing one scalar gate should reveal a submit-safe projection.
- Observed result: E153 classifies `103` three-of-four near misses and finds an asymmetric blocker split. `102/103` are `missing_actionable`, and `101/102` of those fail active/Q2S3 while passing relaxed, E72, and post-E101 gates. The lone `missing_relaxed` row passes actionability but fails raw/world structural health. Target anatomy shows the dominant missing-actionable exposure is S3/S4/S2, not Q2.
- Why discard: the blockers are not distributed like a scalar tolerance miss. They represent two different state requirements: S3 active-boundary actionability for the main mass and raw/world health for the lone actionable escape.
- Implementation issue possible: low to medium. E153 initially exposed a candidate-row identity issue and fixed it with `variant_pos`; after the fix, rows match E152's `2880` projected count. The conclusion is still bounded to E152's projection family.
- Bottleneck implication: the next useful decoder must make S3 active-boundary safety and raw/world health co-occur. Global threshold relaxation would likely create public-tail exposure rather than a healthy candidate.
- Do not repeat: relaxing active/Q2S3, action-cos, relaxed, E72, or post-E101 gates globally as the next default. Use E153 blocker classes as the repair target instead.

## FH134. The E153 S3 active-boundary blocker is terminal

- Failed hypothesis: because `102/103` E152 near misses failed actionability and `101/102` failed active/Q2S3, the E152 branch-orthogonal family was fundamentally incompatible with the strict/E72/post-E101/actionability intersection.
- Observed result: E154 repaired the dominant blocker directly. S3-only rollback over the `102` missing-actionable sources generated `7458` rows, `10` all-four repairs, and `10` materializable rows. The selected `submission_e154_s3repair_9f2e2e73.csv` rolls back only `3` top E101-active S3 cells with keep `0.25`, keeps all-four gates open, and improves local all-minus-E95 to `-0.000012158050`.
- Why discard: the blocker was localized to a few S3 active-boundary cells in the right source rows. It did not require relaxing global gates or abandoning the branch-orthogonal family.
- Implementation issue possible: medium. The scan is finite and still E144-branch-collinear; it proves repairability inside this local grid, not a broad new representation. The scoring pipeline reuses E83/E130/E142 controls and materializes only rows that beat E144 locally.
- Bottleneck implication: the live bottleneck shifts from "no all-four intersection exists" to "does the repaired all-four E144-plus-orthogonal branch survive public labels?" E154 is now the highest-information sensor, while E144 is the conservative contrast.
- Do not repeat: treating active/Q2S3 failure as a branch killer. Repair S3 active-boundary first, then test public feedback. If E154 fails but E144 wins, the issue is likely added branch body or exact rollback selection, not the entire S3 repair concept.

## FH135. E154 requires the exact full branch body

- Failed hypothesis: E154's all-four health is an isolated tuned point; reducing its E144->E154 body or removing target pieces should kill all-four health or lose the E144 local edge.
- Observed result: E155 finds the opposite. Among `40` ablation variants, `34` remain all-four, `27` pass the E155 submit rule, and `22` reduced-body variants still beat E144. The selected lower-body file `submission_e155_bodytemp_d27e7965.csv` uses only `25%` of the E154 body and still has all-minus-E95 `-0.000010362491`. All `12/12` target-drop rows remain all-four.
- Why discard: the repaired direction is an amplitude ridge, not a single exact point. Full E154 amplitude may still be the higher-information public sensor, but it is not required for local gate health.
- Implementation issue possible: low for the ridge existence because it uses the same scoring stack and direct interpolation controls. Medium for public interpretation because lower amplitude may be too small to move public LB even if locally healthy.
- Bottleneck implication: the branch is less brittle than E154 alone implied. The next risk is amplitude/public-signal resolution, not only gate compatibility.
- Do not repeat: arguing that an E154 loss automatically rejects S3 active-boundary repair. First separate full-body overextension from the lower-amplitude E155 ridge.

## FH136. E155 is the minimal coherent repaired body

- Failed hypothesis: E155's `25%` diagonal E144->E154 body is the smallest coherent repaired branch; going below it or dropping diagonal target pieces should fail all-four health or lose the E144 edge.
- Observed result: E156 scans the Q1/Q3/S2/S3/S4 body lattice and finds `3125/3125` all-four variants, `2984` strict candidates, and `85` rows below E155's body ratio. The selected `submission_e156_targetaxis_757546d2.csv` uses only Q1/S2/S4 axes, body ratio `0.171266667`, all-minus-E95 `-0.000010004`, post-E101 p95 `-0.000003712`, and E72 gap `-0.000002266`.
- Why discard: the repaired branch does not require a diagonal low-amplitude body. Its minimum local survivor is nearly E144 plus a tiny Q1/S2/S4 add-on, with no extra Q3/S3 movement.
- Implementation issue possible: low for the tested lattice after full non-anchor evaluation was forced; earlier truncated evaluation was corrected by raising `MAX_NONANCHOR_ROWS` above the lattice size. Medium for public interpretation because the local edge is barely above the materiality threshold.
- Bottleneck implication: the branch is even less brittle than E155 implied, but also more collinear and smaller. The bottleneck is not finding any local all-four low-body point; it is knowing which tiny target-axis add-on, if any, public labels actually reward.
- Do not repeat: treating E155 as the minimum repaired amplitude. Use E156 only as a low-body decomposition control, not as evidence of a new broad latent.

## FH137. E156's Q1/S2/S4 minimum-body row is a unique target-axis law

- Failed hypothesis: because E156 selected Q1/S2/S4 as the minimum-body all-four row, Q3/S3 extra movement is unhealthy or unnecessary in a target-semantic sense.
- Observed result: E157 finds the opposite. Finite-difference response over the E156 lattice shows Q3 is the strongest local all-minus axis (`-0.000000383335`) and strongest post-E101 p95 axis (`-0.000000132956`). S2, not Q1/S2/S4 as a group, carries almost all E72 budget improvement. Three low-body rows including Q3 dominate E155 across local all-minus, post-E101 p95, and E72 gap.
- Why discard: E156's selected Q1/S2/S4 row was selected by minimum body among barely material rows, not by unique target-axis health. The lattice is gate-saturated (`3125/3125` all-four), so target semantics cannot be inferred from that minimum alone.
- Implementation issue possible: low for the finite-difference audit because it reuses the completed E156 full-evaluation scan. Medium for public interpretation because E157's improvement over E155 is only `~4.2e-8` local all-minus.
- Bottleneck implication: the repaired branch has smooth low-body controls, but target-axis selection remains below public-resolution scale. The bottleneck is candidate-selection resolution and public-tail validation, not absence of target-axis alternatives.
- Do not repeat: claiming Q3/S3 are rejected by E156. Use E157 to describe the branch as a gate-saturated ridge with tiny target-axis controls.

## FH138. E154 is public-readably better than E155 and target-axis controls before feedback

- Failed hypothesis: after E154/E155/E157/E156 are generated, their local ordering can be treated as an expected-score ranking before public feedback.
- Observed result: E158 shows the repaired controls are too close for that. E154 beats E155 locally by `-0.000001795559`, below the `2e-6` public-readable guardrail. E157 beats E155 by only `-0.000000041955`, and E156 is `+0.000000358921` worse than E155. The only readable local separation inside the immediate stack is E154 versus unrepaired E144 at `-0.000002432120`.
- Why discard: the sibling controls are highly E144-collinear and below public-resolution scale. Ranking them as if they were independent score candidates would turn a sensor stack into leaderboard-chasing noise.
- Implementation issue possible: low for the computed geometry and local gaps because E158 reads the actual submission files and selected stress rows. Medium for the `2e-6` guardrail because public feedback could still reveal a hidden target-axis effect not visible locally.
- Bottleneck implication: E154 is first for interpretability against E144 and the full repaired all-four question, not because it has a public-readable edge over E155. E155/E157/E156 are post-feedback controls.
- Do not repeat: using E155/E157/E156 before E154 feedback as score-maximizing micro-variants. Use them only to distinguish full-body overextension, target-axis tuning, and minimum-body decomposition after the branch result is known.

## FH139. E154 scalar public band alone can choose the next repaired-branch file

- Failed hypothesis: once E154 public LB is known, E158's score band alone is enough to decide whether to submit E155, E157, E156, E144, or close the branch.
- Observed result: E159 decomposes E154 into `479` additive LogLoss segments over `294` unique row-target cells and shows the loss-side responsibility is not scalar. The direct decomposition is numerically exact (`<2e-16` hard-delta error), and branch/hard-fail blame is dominated by `inherited_e144_body` under global, subject, and nearest-hard priors. The E154-specific added body is much smaller: flip-benefit `0.255975083` for extra body and `0.203843941` for adjustment, versus `3.292000000` for inherited E144 body.
- Why discard: E155 only reduces the E144->E154 added body. It cannot logically rescue a failure whose dominant blame is inherited E144 body. A score band without responsibility attribution would confuse component failure with amplitude overextension.
- Implementation issue possible: low for additive accounting because direct hard-label deltas were verified; medium for realized public attribution because true public labels remain hidden and E159 uses prior-world simulations.
- Bottleneck implication: candidate selection is now attribution-resolution limited. The next public feedback must be read as a hidden-label world observation, not as a scalar leaderboard ranking.
- Do not repeat: auto-submit E155 after any E154 tie/small-loss, or auto-close the branch after any E154 non-win without checking whether blame falls on added body, inherited body, or target-local axes.

## FH140. E154 high-risk cell pruning creates a new first submission

- Failed hypothesis: because E159 identifies inherited/added cells that can dominate E154 loss-side attribution, pruning the highest-risk cells toward E144 or E95 before public feedback should create a safer successor to E154.
- Observed result: E161 generated `1608` pruning variants from E159 cell-level risk. Many rows were diagnostically real: `1226` were safer than E154 under focus expected risk, `631` preserved all-four health, and `299` were control-grade. But `0` were submission-grade and `0` beat E154 by the `2e-6` public-readable guardrail. The best local delta versus E154 was only `-0.000000045921`.
- Why discard: pruning can reduce prior-risk, but the improvement does not translate into an independently readable probability movement. The strongest risk reductions give up too much local health/edge, while healthy pruning rows remain E154-collinear micro-controls.
- Implementation issue possible: medium. The scan is finite and uses public-free priors; a different learned risk model could rank cells differently. Low for this specific shortcut because the search covered component scopes, target scopes, top counts, and both E144/E95 reversion modes with the same E154 stress stack.
- Bottleneck implication: the frontier is not blocked merely by knowing which E154 cells are risky. The missing object is a decoder that turns risk reduction into a larger public-tail-safe movement, not a local branch prune.
- Do not repeat: pre-feedback E154 risk-prune submissions or more top-risk revert sweeps unless actual E154 feedback specifically points to a narrow component overextension and E160 permits diagnostic controls.

## FH141. Repaired-branch sibling local ranking is stable enough for pre-feedback submission order

- Failed hypothesis: E154/E155/E157/E156/E161 pruning rows can be ordered by local edge or public-free prior before E154 feedback because their average deltas encode stable structure.
- Observed result: E162 shows the branch is hidden-label resolution limited. E154-vs-E155 has focus expected delta only `+0.000000505`, while one top-swing cell can move `0.000010815`. E154-vs-E144 has top1 swing `0.000014420`, and E157-vs-E155 has top1 swing `0.000002185`. Every live sibling/control pair needs only `1` top-swing cell to exceed the `2e-6` public-readable guardrail.
- Why discard: the public-readable signal is not distributed broadly enough to rank sibling controls safely. One high-swing hidden row-target label can dominate the intended file-to-file edge.
- Implementation issue possible: low for the pairwise hard-label arithmetic because it directly uses submission probabilities; medium for realized public subset because labels are hidden and E159 priors supply only expected-world context.
- Bottleneck implication: this is a resolution/calibration-tail bottleneck, not a normal model-ranking problem. E154 is valuable as a public sensor, while siblings are post-feedback instruments.
- Do not repeat: pre-feedback submission order changes among E155/E157/E156/E161 based on `1e-6` local/prior differences. Wait for E154 or build a candidate with a much larger low-tail-safe edge.

## FH142. E162's hidden-label fragility is only an E154 sibling artifact

- Failed hypothesis: the one-cell readability issue found in E162 is local to the repaired E154 sibling stack, so broader known-public transitions and live post-E95 candidates can still be ranked by ordinary expected delta or CV-style local edge.
- Observed result: E163 extends the audit to `22` candidate pairs. Known public transitions are also narrow after mixmin: E95-vs-mixmin actual delta `-0.0000153107` needs `1` top cell, E101-vs-E95 `+0.0000090362` needs `1`, E101-vs-mixmin needs `1`, and the failed E72 move needs only `4-6` top cells depending on base. In contrast, mixmin-vs-a2c8 needs `25` top cells for the actual `-0.0011326805` public delta. All `7/7` live post-E95 candidates need only one top cell to exceed the `2e-6` readability guardrail.
- Why discard: post-E95 ranking is not just locally close; it is underresolved by the hidden public hard-label realization. The one-cell problem is a plateau property after the broad mixmin move, not an E154-only measurement artifact.
- Implementation issue possible: low for hard-label arithmetic and known-public deltas; medium for actual hidden-label attribution because true public labels remain hidden and focus-prior expected deltas are only public-free proxies.
- Bottleneck implication: after E95, the main blocker is candidate-selection resolution/calibration-tail risk. To break out, a candidate must either recover another broad mixmin-scale signal or make a low-tail-safe move whose edge is larger than top-cell swing fragility.
- Do not repeat: treating a `1e-6` to `3e-5` local edge among post-E95 candidates as a stable expected-public ranking unless it survives explicit hard-label breadth stress.

## FH143. The existing candidate universe has no broad post-E95 escape branch

- Failed hypothesis: because E129 found no novel strict old-file successor and E163 showed live post-E95 branch files are one-cell fragile, the already generated submission universe contains no broad E95-relative direction worth testing.
- Observed result: E164 scanned `2052` tracked submission paths and `1977` unique tensors, finding `198` broad-edge rows and `192` conservative candidate-gate rows. E165 then rejected known public-bad broad controls but left `90` geometry-health survivors. E166 showed those survivors can be shrunk into small E95-relative movements while preserving breadth: `112` scaled sensor-gate rows and `51` material rows at scale `<=0.03`.
- Why discard: the universe does contain a broad latent branch; it was hidden behind unsafe raw amplitude and known-bad JEPA controls. The correct statement is not "no broad branch exists" but "raw broad branch submissions are unsafe without geometry and scale control."
- Implementation issue possible: medium. The broad branch is dominated by JEPA-family files and has no direct public-positive observation yet. E165's bad-axis basis may be undercomplete, so E166 public feedback is required.
- Bottleneck implication: the plateau has two separate lanes now. The repaired E154 lane is narrow and hidden-label-resolution limited. The E166 lane is broad and small-amplitude, with real upside but higher worldview risk.
- Do not repeat: old-file ranking that ignores broadness, or raw JEPA submission that ignores bad-axis and scale control. Future broad candidates must pass both E165-style geometry and E166-style small-amplitude breadth.

## FH144. E166 focus cells are target-count-random broad noise

- Failed hypothesis: E166's broad survivor focus cells pass E164-E166 only because many cells are moved slightly; after matching target counts, their top-benefit/top-swing cells should look like random row-target subsets with no hidden calendar/block signature.
- Observed result: E167 rejects this. E166 top-benefit cells have edge-like rate `0.689189` versus target-count null `0.470842` (`z=3.902`, `p_high=0.000333`), between-train-runs rate `0.797297` versus `0.624658` (`z=3.293`, `p_high=0.001333`), and top-subject share `0.243243` versus `0.164563` (`z=3.498`). The top-swing set repeats the same direction with between-train-runs `0.824324` and edge-like `0.594595`.
- Why discard: the E166 broad branch is not merely submission-space noise. It touches real hidden row/block context, especially edge-like and between-train-runs regions.
- Implementation issue possible: medium. The context atlas is inferred from prior experiments, and the public labels are still hidden. Low for the target-count-null result because the permutation test preserves target composition and uses `3000` nulls.
- Bottleneck implication: the broad lane remains alive as a hidden-world sensor. A public E166 loss should not be interpreted as "there was no context signal"; it should be interpreted against safety-atlas and public-negative axis mismatch.
- Do not repeat: dismissing broad E95-relative candidates solely because they are JEPA-family or old-universe files. First test context enrichment and safety divergence separately.

## FH145. E166 inherits the same safety-atlas law as the repaired branch

- Failed hypothesis: if E166's broad focus cells are real, they should also be enriched for the existing transfer-shrinkage/veto-null safety atlas that made E154/E95-style repaired branches plausible.
- Observed result: E167 finds the opposite. E166 top-benefit cells have all-veto-null rate `0.297297` versus null `0.574158` (`z=-5.127`), all-safe-density mean `0.117097` versus `0.243966` (`z=-5.239`), broad-low-alpha mass `1.321365` versus `3.199735` (`z=-3.387`), and E101-plausible mass `0.238204` versus `0.533727` (`z=-3.100`). E72-active rate is high: `0.837838` versus `0.670369` (`z=3.310`).
- Why discard: E166 is structurally real but safety-atlas divergent. The existing atlas does not certify it; in fact, the strongest E166 focus cells sit in regions the atlas would treat as risky or under-supported.
- Implementation issue possible: medium. The atlas is a public-free proxy, and it may be too conservative or branch-bound. But the direction and significance are strong enough to block any claim that E166 is a safer expected-score file.
- Bottleneck implication: the plateau is not solved by "broad plus tiny scale" alone. The missing ingredient is a safety axis that distinguishes true broad hidden-context signal from E72-active public-negative exposure.
- Do not repeat: scaling E166, creating E166 amplitude variants, or ranking E166 above repaired-branch files as a safer expected-score candidate before public feedback. Use it only as a broad-escape sensor.

## FH146. E166 context-real signal cannot be separated from safety divergence by simple masks

- Failed hypothesis: E167's context enrichment and safety-atlas divergence are fully coupled, so any simple safety repair will either destroy the hidden-context signal or leave the broad branch too top-cell fragile.
- Observed result: E168 finds `2` decoupling-pass policies. `context_high__veto` keeps `904` cells over `193` rows, expected delta `-0.000120457`, cells-to-flip `32`, top1/expected `0.048415`, edge-like `0.610619`, between-train-runs `0.819690`, veto `1.0`, safe-density `0.346150`, and E72-active `0.268805`. `context_high__high_density_p50` is almost tied with expected delta `-0.000119080`.
- Why discard: context-high plus veto/density comfort preserves material breadth and improves the exact safety metrics E167 flagged. The failure is not separability; the failure is that strict context-only purity is too small and top-cell fragile.
- Implementation issue possible: medium. The masks are built on E167's inferred atlas and still need public feedback. Low for this exact falsification because the E168 criteria were pre-public and require both breadth and safety improvements.
- Bottleneck implication: E166 is not a binary choice between raw broad JEPA movement and total rejection. A repaired broad lane exists locally, but it gives up expected edge for lower risk.
- Do not repeat: treating E167 safety divergence as a proof that all broad-context E166 variants are dead. First test context-high safety intersections.

## FH147. E168 context-high safety masks collapse when materialized as prediction tensors

- Failed hypothesis: E168's cell-mask rows only look healthy in diagnostic space; once converted to full submissions, they will lose breadth, align with known bad axes, or become another narrow E154/E101-style micro-control.
- Observed result: E169 materializes `2` stress-gate files. `submission_e169_ctx_veto_c5e806e3.csv` has expected delta `-0.000120457`, moved cells/rows `904/193`, cells-to-flip `32`, top1/expected `0.048415`, bad-span energy `0.295326`, max bad cosine `0.222381`, mean/max abs logit `0.001096`/`0.010206`, and low cosine to E154/E101/mixmin (`0.087180`/`-0.021896`/`-0.020672`). `submission_e169_ctx_high_density_p50_51110c7e.csv` is a near-duplicate stress-pass control.
- Why discard: materialization preserves the intended broad/small-amplitude geometry while lowering bad-span energy versus raw E166. The candidate remains public-unproven, but it is not a diagnostic-only artifact.
- Implementation issue possible: medium. The broad branch still lacks a public-positive anchor and `q2_bad` remains the max bad axis. Low for the tensor-materialization check because actual submission files were written and rescored.
- Bottleneck implication: the live broad branch now has three distinguishable public sensors: repaired E169 for balanced risk, raw E166 for safety-atlas falsification, and E154 for conservative repaired-branch contrast.
- Do not repeat: demoting E168 masks without materialized stress. If one broad candidate is submitted before feedback, use `submission_e169_ctx_veto_c5e806e3.csv` unless the explicit goal is to challenge the safety atlas with raw E166.

## FH148. E169 fully solves the post-E95 hard-label readability bottleneck

- Failed hypothesis: because E169 restores broadness and safety geometry versus E166, its public outcome should be robust enough that local expected delta can be read as a stable score-ranking claim.
- Observed result: E170 shows E169-vs-E95 is broad in expectation but still public hard-label-resolution limited. It moves `904` cells and has `32` cells-to-flip expected, but the top1 swing is `0.000005832`, `1` cell clears the `2e-6` guard, and only `4` cells cover E95's full public edge over mixmin. The high-density p50 sibling differs by only `10` Q2/S3 cells and `-0.000001377` expected delta.
- Why discard: E169 is a better sensor, not a solved selector. A few high-swing hidden labels can still decide whether the public LB is win/tie/small-loss even though the local expected edge is broad.
- Implementation issue possible: low for pairwise hard-label arithmetic and group attribution; medium for public realization because public labels are hidden.
- Bottleneck implication: E169 addresses the broad-lane safety problem but not the frontier-scale public-label resolution problem. The plateau remains partly a calibration-tail/hidden-label sensor problem.
- Do not repeat: ranking E169 near-duplicates by sub-`2e-6` local edge, submitting high-density p50 before ctx-veto feedback, or interpreting a tie/small-loss as proof that the broad branch is dead.

## FH149. E169's public-decisive top cells are independently visible-prior supported

- Failed hypothesis: E169's top hard-label cells should be at least as well supported by visible global/subject/flank priors as the rest of the moved body, making the E170 hard-label fragility less concerning.
- Observed result: E171 shows the opposite. The full moved body is favorable under `visible_mean` with mean delta `-0.000022659` and win rate `0.868840`, but the top critical cells are weak: top1 support `0.098648`, top4 swing-weighted support `0.330699`, top16 `0.266074`, top32 `0.247434`. The top32 support is significantly below target-matched null mean `0.353573` (`z=-2.703`, `p_low=0.001667`). Flank-only priors are also weak/adverse: `nearest_beta` mean `+0.000005364`, `edge_endpoint_beta` mean `+0.000005106`, `flank_mean` mean `+0.000000790`.
- Why discard: visible priors support the broad E169 body more than the public-decisive tail. E169 is not a resolved selector; it is a broad-body hypothesis with critical-cell tail risk.
- Implementation issue possible: medium. The priors are train-derived and public-free, not true public labels. Low for the contrast itself because top sets, priors, and target-matched nulls are fixed pre-public.
- Bottleneck implication: the 0.576 plateau remains a two-layer problem: broad latent body selection and high-swing hard-label tail realization can disagree.
- Do not repeat: claiming E169 is stable because its full-body visible prior is favorable, or pruning top critical cells solely because E171 says they are adverse without rerunning breadth/readability stress.

## FH150. E171's critical-tail warning is only diagnostic and cannot be repaired locally

- Failed hypothesis: the E169 visible-prior adverse top-tail is inseparable from the broad context/veto body, so any rollback that fixes visible p95 should destroy breadth, focus expected edge, or bad-axis geometry.
- Observed result: E172 finds `7` stress-gate rollback variants. The selected `visible_positive_all_keep0p25` row keeps `904` moved cells, `193` moved rows, `30` cells-to-flip, focus expected delta `-0.000112695`, top1/expected `0.051750`, and improves visible p95 from `+0.000010607` to `-0.000026683`. Bad-span energy improves from `0.295326` to `0.257874`, and max bad-axis cosine improves from `0.222381` to `0.142927`.
- Why discard: the adverse tail is at least locally separable. The repair is not a blind top-cell deletion; it damps the full visible-prior-positive-loss subset while preserving the broad body.
- Implementation issue possible: medium. Visible priors are public-free proxies, not hidden public labels. Low for the separability test because the materialized tensor was rescored with independent breadth and geometry checks.
- Bottleneck implication: broad body selection and visible-tail calibration are distinct bottlenecks. E169 is a sensor for the split; E172 is the first broad-body-preserving tail repair.
- Do not repeat: treating E171 as a reason to abandon the broad branch without testing intervention survival, or submitting unrolled E169 as the safer expected-score file when the question is score improvement rather than body-vs-tail falsification.

## FH151. E172 keep `0.25` is the only safe visible-tail rollback amplitude

- Failed hypothesis: after E172, any meaningful reopening of the visible-positive-loss rollback cells toward E169 will reopen visible-tail risk, increase E101-like downside, or cross bad-axis/Q2-S3 geometry guards.
- Observed result: E174 scores `80` reopening policies and finds `46` E174-gate survivors. The materialized `submission_e174_ro_fc_top75_to1p0_95638e73.csv` reopens the top `75` focus-recovery cells fully toward E169, improving focus expected delta versus E172 by `-0.000011672` while keeping visible p95 `-0.000022709`, worse-than-E101 `0.000220`, bad-span energy `0.263996`, max bad cosine `0.163229`, and Q2/S3 share `0.339597`.
- Why discard: keep `0.25` was a safe rollback, not a unique Pareto point. A structured subset of rollback cells carries recoverable broad-body signal that local stress can reopen without losing the main visible-tail repair.
- Implementation issue possible: medium. The gate is public-free and E174 sits close to the Q2/S3 guard, so public feedback could still reject the reopened subset. Low for the falsification itself because E174 used actual materialized tensors, not only cell summaries.
- Bottleneck implication: the broad-lane bottleneck is now three-layered: broad body, visible-tail damping, and rollback-cell amplitude selection. E174 improves the third layer but still does not solve hidden hard-label resolution.
- Do not repeat: freezing E172's keep factor as a constant or creating same-family keep siblings without explicit visible-tail, bad-axis, and public-readability stress.

## FH152. E174 top-75 full reopening is component-Pareto

- Failed hypothesis: E174's selected top-75 reopening is already the best risk-adjusted component point, so any simple target/context/risk damping must either give up too much focus edge or fail to improve the thin risk axes.
- Observed result: E176 scans `162` target, group, context, E72-active, support, top-swing, and top-focus component ablations. `12` variants pass the component gate. The selected `submission_e176_abl_q2_to0p75_91e49725.csv` dampens only reopened Q2 cells from keep `1.0` to `0.75`, gives up only `+0.000000983` focus delta versus E174, remains `-0.000010689` better than E172, and improves bad-span energy `0.263996 -> 0.261687`, max bad cosine `0.163229 -> 0.158126`, Q2/S3 share `0.339597 -> 0.334753`, visible p95 `-0.000022709 -> -0.000023096`, and worse-than-E101 `0.000220 -> 0.000192`.
- Why discard: E174 is the max-edge reopening, not the risk-adjusted Pareto point. Q2 contributes real broad-body recovery, but full Q2 reopening spends too much of the same q2_bad/Q2-S3 margin that E101 already exposed as fragile.
- Implementation issue possible: medium. E176 is still public-free and same-family with E174/E172, so it can be rejected by the hidden public realization. Low for the component-Pareto falsification because the scan compares actual materialized tensors under the same E174 stress stack before any E174/E176 public score is known.
- Bottleneck implication: the current broad-lane bottleneck is not only "which cells reopen"; it is target-specific amplitude law inside those cells. S3/S2/S1 can stay fully reopened while Q2 should be under-opened unless public feedback proves the full Q2 movement is real.
- Do not repeat: treating top-N full reopening as fixed, or tuning Q2 amplitude after public feedback. Component damping must be pre-public and interpreted as a Q/S-asymmetric calibration hypothesis.
- Remaining question: is Q2 under-opening enough to make the partial-reopen family public-positive, or is the entire E169/E172/E174/E176 broad lane still hidden hard-label-resolution limited?

## FH153. E176 can be interpreted with ordinary score ranking or E175 alone

- Failed hypothesis: because E176 is only a small E174 sibling, its public score can be interpreted by ordinary leaderboard ordering or by reusing E175 without a Q2-amplitude-specific decoder.
- Observed result: E177 shows E176-vs-E174 is a tiny Q2-only contrast: `21` cells over `21` rows, expected focus cost `+0.000000983`, cells-to-flip `2`, top1 swing `0.000000832`, and swing-weighted support `0.495994`. Meanwhile E176-vs-E95 remains broad (`904/193`, expected focus `-0.000123384`, cells-to-flip `33`, cells for E95-over-mixmin edge `4`). The public score must therefore be read as a banded observation about Q/S-asymmetric partial reopening, not as a continuous Q2 keep-factor signal.
- Why discard: a single scalar E176 score cannot resolve full-Q2 versus damped-Q2 amplitude at sub-`1e-6` expected edge scale. Without a locked decoder, any next E174/E172/E154 choice would become post-hoc tuning.
- Implementation issue possible: low for the decoder arithmetic because it uses fixed tensors and pairwise hard-label deltas. Medium for public interpretation because E176 feedback is still unknown.
- Bottleneck implication: the plateau is still hidden-hard-label-resolution limited. E176 is submit-worthy as a risk-adjusted sensor, but its score must be used to kill or preserve worldviews, not to estimate a new Q2 keep factor.
- Do not repeat: treating E176 feedback as permission to scan Q2 keep `0.5/0.65/0.85/1.0` after the fact. Use `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>` first.

## FH154. The current plateau is mainly lack of model capacity or absence of hidden signal

- Failed hypothesis: the reason public stays around E95 is that there is no useful post-E95 structure left, or that ordinary stronger modeling would be the main missing ingredient.
- Observed result: E178 shows broad hidden signal is still present. E166 has focus-prior edge `-0.000332077`, `21.689x` the E95 public edge; E169/E172/E174/E176 remain material with expected deltas around `-0.000112695` to `-0.000124367`. But the frontier edge is tiny: E176 needs only `4` top cells, E101 only `2`, and E98 selector p90 is `53.33x` the E95-over-mixmin public edge.
- Why discard: the problem is not signal absence. The problem is that public-real improvements are filtered through target-tail calibration and high-swing hard-label cells that the current validation stack cannot rank at frontier scale.
- Implementation issue possible: low for hard-label/readability arithmetic and public-anchor ratios; medium for generalizing to private because E176 feedback is still pending.
- Bottleneck implication: improving model capacity alone is unlikely to jump toward 0.54 unless it also supplies a new hard-label/public-subset sensor or a much larger low-bad-axis movement.
- Do not repeat: broad model/feature sweeps that produce slightly better CV without proving cell-resolution survival. Future candidates must either beat same-family hard-label fragility or arrive with a new public-free resolution test.

## FH155. E176 is locally certified at public-decisive hard-label resolution

- Failed hypothesis: because E176 passed broadness, visible-tail, bad-axis, and Q2-damping checks, its top public-decisive cells should also be train-prior visible enough to treat E176 as a certified expected-score improvement.
- Observed result: E179 supports the full body but rejects decisive-cell certification. Full E176-vs-E95 visible-mean expected delta is `-0.000050824`, and visible-mean simulated win rate is `0.999080`. E176-vs-E174 Q2 damping is also visible-prior favorable with expected delta `-0.000000191`, support `0.690495`, and hard support rate `0.904762`. But the top4 E95-edge cells have support only `0.330699`; top33 expected-flip support is `0.245771` versus target-matched null mean `0.335713` (`p_low=0.014667`).
- Why discard: visible priors support E176 as a body and support Q2 damping, but they do not resolve the high-swing cells that can decide public LB. E176 is a good sensor, not a certified improvement.
- Implementation issue possible: medium. The target-matched null and priors are train-derived, not true public labels. Low for the falsification of certification because the same fixed E176/E95/E174 cells were audited before feedback.
- Bottleneck implication: the plateau remains a hard-label visibility problem. The missing object is not another E176-family amplitude variant; it is a public-free way to identify the decisive cells below the current public-edge scale.
- Do not repeat: calling E176 "safe" from full-body support alone, or creating another Q2 keep-factor sibling because E179 says Q2 damping is favorable. Wait for E176 public feedback and decode with E177/E179.

## FH156. E179's weak top-cell support is a hard veto against E176

- Failed hypothesis: E176 top4 visible support `0.330699` is low enough by itself to demote E176 below other candidates.
- Observed result: E180 shows known public winners can be as weak or weaker at the top-cell layer. E95-vs-mixmin public-positive top4 support is only `0.100896`; E101-vs-mixmin is also `0.100896`; mixmin-vs-a2c8 is `0.310904`. E176 top4 `0.330699` is above the known-winner mean `0.170898` and max `0.310904` in this anchor set. Visible-prior all-moved sign accuracy over known anchors is only `0.5`.
- Why discard: weak visible top-cell support is not a hard veto because successful anchors can have weak top-cell support. The failure is the selector, not necessarily the candidate.
- Implementation issue possible: medium. Known anchors are few and public labels remain aggregate. Low for the narrow falsification because the same E179 machinery was applied to fixed known-public pairs.
- Bottleneck implication: the decisive-cell problem survives, but it shifts from "E176 top cells look bad" to "visible priors cannot certify frontier top cells." This keeps E176 alive while demanding a better representation target for future work.
- Do not repeat: demoting E176 solely because top4 support is below 0.5, or using visible-prior top-cell support as a standalone submission ranker.

## FH157. E176 is the best-supported live candidate across all latent representations

- Failed hypothesis: after E179/E180, E176 can be described as the best-supported next candidate in a representation-wide sense.
- Observed result: E181 finds a direct counterprior from the inherited binary hidden-label world pool after reranking worlds by all current public anchors. In best-5 current-anchor residual worlds, E176 has mean delta `+0.000003920` versus E95 and negative rate `0.400`; in best-10 it has mean delta `+0.000007442` and negative rate `0.300`. E154 and E144 are negative in all best-5 worlds, with means `-0.000051451` and `-0.000051445`.
- Why discard: E176 is supported by visible/body/Q2-damping evidence, not by every latent representation. The binary-world view points to a different branch, so the stronger "E176 is globally most supported" wording is false.
- Implementation issue possible: medium. The world pool is inherited and was not regenerated with explicit current-anchor E176/E154/E144 objectives; current-anchor residuals are also larger than the E95 public edge. The narrow failure remains valid because E181 only rejects the representation-wide claim, not E176 as a public sensor.
- Bottleneck implication: the plateau is now a latent-view conflict, not just a top-cell visibility conflict. We need a refreshed current-anchor binary-world stress or public feedback to decide whether visible-body E176 or repaired-branch E154/E144 is closer to the hidden public world.
- Do not repeat: presenting E176 as certified or universally supported. Present it as a conditional visible-body/Q2-underopen sensor until binary-world conflict is resolved.

## FH158. E181 inherited binary counterprior is sufficient to promote E154/E144 over E176

- Failed hypothesis: because E181's best inherited current-anchor residual worlds favor E154/E144 and are mixed/adverse for E176, the next public priority should be inverted from E176 to the repaired E154/E144 branch without another stress layer.
- Observed result: E182 regenerates current-anchor binary worlds and explicitly pressures E176/E154/E144 objectives. Scenario fits remain frontier-scale (`0.0000784319`, `0.0000513148`, `0.0000762925` max residuals), but strict range incumbents appear in only `0.233` of rows, and pressure worlds make E176/E154/E144 cross zero in `1.000` / `1.000` / `1.000` of scenarios. E176 spans about `-0.000421216..+0.000254123`; E154 spans about `-0.00109286..+0.000923535`; E144 spans about `-0.000992245..+0.000838041`.
- Why discard: the refreshed current-anchor inverse problem does not identify a one-sided branch. It can construct hidden-label worlds where E176 wins and worlds where E176 loses; the same is true for E154 and E144. E181 remains a warning against universal E176 support, but it is not an action-grade selector.
- Implementation issue possible: medium. Exact range MILPs are incumbent-sparse under the time limit, so E182 uses pressure worlds as a diagnostic. Low for the narrow failure because the pressure worlds all have incumbents and all three branches cross zero across scenarios.
- Bottleneck implication: current public anchors and train structural priors still underidentify frontier-scale live-candidate signs. The bottleneck is hidden-label/cell-resolution and latent-view conflict, not a simple choice between E176 and E154/E144.
- Do not repeat: promoting E154/E144 solely because inherited binary worlds favor them. Before changing priority, either obtain public feedback, build a stronger non-public selector, or attach a pre-registered decoder to the repaired-branch submission.

## FH159. Visible/subject/flank priors can select the favorable E182 pressure branch

- Failed hypothesis: once E182 exposes favorable and adverse pressure worlds, train-derived visible, subject, or flank priors should prefer the favorable branch on the differing moved cells for at least one live candidate.
- Observed result: E183 finds favorable-branch preference rates of `0.000` for E176/E154/E144 under visible-mean priors. Subject and flank priors also have `0.000` favorable preference for all three candidates. The disagreement is not small-cell noise: support-gap coefficient-weighted means are E176 `0.797945`, E154 `0.973558`, and E144 `0.888923`.
- Why discard: the pressure branches that make candidates look good require labels that current train-derived visible/local priors systematically dislike. Visible priors can still describe bodies and risk, but they are not branch selectors at the current hidden-label resolution.
- Implementation issue possible: medium. E183 depends on E182 pressure-world solutions and train-derived priors, not true public labels. Low for the narrow failure because the same prior machinery rejects the favorable branch across all candidates and scenarios.
- Bottleneck implication: the current plateau is not solved by reusing visible priors as a gate. The missing object is a different decisive-cell representation or public feedback that identifies the pressure branch.
- Do not repeat: ranking E176/E154/E144 by visible-prior branch preference, or claiming a candidate is certified because its full body has favorable visible-prior expectation.

## FH160. A shallow known-public metadata motif can select live pressure branches

- Failed hypothesis: known public transition cells contain enough target/context/public-axis metadata to learn a public-compatible support-direction motif, and that motif can choose the favorable E182 pressure branch.
- Observed result: E184's best direct pair-LOO model has sign accuracy `0.333` and AUC `0.425`; best direct family accuracy/AUC are `0.600` / `0.178`. Polarity inversion can make some pair-level results look strong, but family best-polarity accuracy is only `0.600`. Live branch preference is unstable: `meta_core` and `meta_public_axis_plus_swing` reject all favorable branches, while `meta_public_axis` and `meta_public_axis_plus_support_label` favor all three.
- Why discard: a selector whose polarity must be chosen after seeing held-out results and whose live decision flips by feature set is not a usable hidden-world representation. It is public-anchor residue, not a stable branch law.
- Implementation issue possible: medium. Cell-level labels are aggregate pair labels and are noisy by construction. Low for the failure of this exact approach because both pair and family stress were run before using live branch scores.
- Bottleneck implication: the missing decisive-cell representation is not a shallow metadata classifier over known public anchors. It likely needs a structural target or new public feedback.
- Do not repeat: using known-public metadata motif scores, inverted motif scores, or public-axis cell flags as a direct E176/E154/E144 ranking rule.

## FH161. An unconstrained known-LB pair decoder is action-grade if its accuracy is high enough

- Failed hypothesis: broader pair-level known-LB movement features can be used directly as a selector once leave-one-file or leave-one-pair accuracy is materially above chance.
- Observed result: E185's best leave-one-file model reaches accuracy `0.811`, frontier accuracy `0.833`, and E95-edge accuracy `0.714`, but reciprocal orientation is unhealthy: E95-edge reciprocity MAE is `0.081` in file-LOO and `0.146` in pair-LOO for the best public-axis model. Live E176/E154/E144 branch preference also flips by feature set.
- Why discard: public pair ordering is antisymmetric. A decoder that can rate both directions of one pair as favorable is not a hidden-world law, even if threshold accuracy looks acceptable.
- Implementation issue possible: medium. Pair labels are sparse and public anchors are few. Low for the narrow failure because the reciprocal sanity check is a mathematical requirement of the task.
- Bottleneck implication: the plateau is partly representation geometry, not only lack of signal. Known-LB pair structure is useful only after orientation constraints.
- Do not repeat: using unconstrained pair probabilities, post-hoc feature-set choice, or reciprocal-inconsistent scores to rank live submissions.

## FH162. Support-heavy antisymmetric pair features are a repairable weak prior

- Failed hypothesis: E186 support-heavy features miss exact E95/E101 only because one support family is over-weighted, so ablation or a low-alpha blend can keep E95/E101 correct while improving edge-band stress.
- Observed result: E187 shows shape-only gets exact E95/E101 correct, but every support-containing ablation tested flips the boundary. The adverse logit contribution is distributed across support flank, visible, subject, focus, nearest, global, and all-prior families. E188 then tests logit blends and finds `0` action-grade rows; for every support variant, the best exact-boundary row is `alpha=0.0`, and exact E95/E101 fails at alpha `0.170..0.285` before edge-band accuracy improves.
- Why discard: support is not a weak local correction on top of shape geometry. It is a different public-quality shortcut that can help wider edge stress while violating the tight frontier boundary.
- Implementation issue possible: low for the exact-boundary falsification because E101 public `0.5763003660` is known and file/pair LOO predictions are fixed. Medium for generalizing to future branches because known public anchors remain few.
- Bottleneck implication: the next bottleneck is not support-weight tuning. We need a new decisive-cell or structural target representation that resolves tight public boundaries without borrowing a support shortcut.
- Do not repeat: creating a submission from support-heavy pair-decoder branch scores, or tuning shape/support blend alpha, unless an independent exact-boundary veto or new public-free cell-resolution sensor is added first.

## FH163. Support-heavy edge gain is a broad deployable selector

- Failed hypothesis: even if support cannot be blended smoothly, its wider E95-edge gains reflect a broad conditional frontier law that can be used to rank live submissions after adding an exact-boundary veto.
- Observed result: E189 finds that in the primary E95-edge file-LOO slice, support rescues exactly `6` rows and all `6/6` are E72-frontier-neighbor orientations. Shape-only wins exactly `4` rows and all `4/4` are the exact E95/E101 boundary. A support-only-on-E72-neighbor gate reaches E95-edge accuracy `1.000`, but this uses known file identity and does not transfer to unlabeled live candidate branches.
- Why discard: the broad-selector claim is false. Support is useful in a specific known-anchor contamination context, not as a general frontier law. The apparent gate is a diagnostic of E72 adjacency, not a deployable candidate selector.
- Implementation issue possible: medium. Known public anchors are few, and a future structural detector might recover E72 contamination without filenames. Low for the narrow falsification because the current support wins and shape wins are exactly concentrated in opposing known slices.
- Bottleneck implication: the current pair-decoder bottleneck is not "add support with a veto"; it is to define a new target representation that separates E72-contamination from tight hardtail boundary movement.
- Do not repeat: using support-heavy E186/E187/E189 branch probabilities to certify E176, E154, or E144. Use support only as auxiliary evidence or as a target for a future E72-contamination detector.

## FH164. Current E72 contamination detector makes support deployable

- Failed hypothesis: after E189, a filename-free structural detector can identify E72-contaminated cases well enough to turn support back into a live gate for E176/E154/E144.
- Observed result: E190 finds real E72-neighbor signal, but not an action-grade gate. `shape_target_context_abs` reaches pair-LOO AUC `0.978836` and AP `0.809524`, but top-k recall is only `0.666667`, and any-file LOO skips `6` positive rows when E72 itself is held out. Support-rich views keep high E72 detection metrics while assigning exact E95/E101 contamination probability around `0.957..0.975`. Live E176 contamination is near zero and never crosses non-E72 p95 or min-positive thresholds.
- Why discard: the detector is useful as a diagnostic, but it does not solve the exact-boundary false-positive problem or the E72-heldout one-class problem. It also gives no support-gate reason for E176.
- Implementation issue possible: medium. The label set is tiny, and E72-neighbor positives are all derived from one known failed submission. Low for the narrow failure because the exact E95/E101 false-positive check directly repeats the boundary that killed support.
- Bottleneck implication: support's E72 signal is real but not yet invariant. The missing object is a contamination representation that can be trained or calibrated without relying on E72 identity and that preserves the E95/E101 hardtail boundary.
- Do not repeat: treating high E72-neighbor AUC from support features as permission to support-gate E176. Require low exact-boundary false positives and a stronger E72-heldout/one-class stress first.

## FH165. Exact E95/E101 hard-negative weighting can make support deployable

- Failed hypothesis: support-rich E72 detectors fail mainly because exact E95/E101 is not explicitly penalized; adding exact E95/E101 as a hard negative should lower support false positives while preserving E72-neighbor recall.
- Observed result: E191 finds boundary-clean pair-LOO rows only for `shape_target_context_abs`. The best clean shape row has AUC `0.978836`, AP `0.809524`, top-k recall `0.666667`, and exact E95/E101 mean probability `0.057658`. Support-containing clean rows are `0`; support-only exact E95/E101 probability stays around `0.785758..0.839112`, and shape+support/all stays around `0.766102..0.824223`.
- Why discard: hard-negative weighting changes calibration of the clean shape view but does not alter the support conflict. Support remains entangled with the exact frontier boundary even when that boundary is explicitly named as negative supervision.
- Implementation issue possible: medium. The positive E72 set is tiny and all positives still depend on one failed anchor, so this does not prove no future one-class/contrastive target can work. Low for rejecting this exact weighting/prototype repair.
- Bottleneck implication: the support problem is representation-level, not sample-weight level. The next useful target must separate E72 contamination and tight hardtail boundary structurally, probably with additional non-public context or a different contrastive target.
- Do not repeat: reweighting exact E95/E101 harder, using prototype distance to E72 vs E95/E101, or calling support clean because E72-neighbor AUC is high while exact E95/E101 remains high.

## FH166. Mild clean-shape E72 pressure is enough to rerank live branches

- Failed hypothesis: because the boundary-clean shape-only E72 score partially flags E144, that score can be used as a live contamination selector to promote or demote E144/E154/E176.
- Observed result: E192 decomposes the clean `shape_target_context_abs` score. E144 crosses known non-E72 p95 in only `1/3` scenarios (`0.038723` vs p95 `0.020815`), remains below non-E72 p99 (`0.044812`), and is far below the known positive floor (`0.804849`). Its nearest known top-3 rows are all non-E72. E154 and E176 never cross p95, with maxima `0.007973` and `0.000008`.
- Why discard: the E144 signal is tail-risk evidence, not E72-like contamination evidence. It does not support a new submission or a support-gated branch change.
- Implementation issue possible: medium. E192 full-data AUC/AP are anatomy-only and optimistic; E191 pair-LOO is the real stress layer. Low for the narrow discard because nearest-neighbor and threshold comparisons all reject live E72-positive resemblance.
- Bottleneck implication: the remaining E72 score is useful as an energy diagnostic, but not a selector. The plateau is still caused by unresolved target/shape hard-tail calibration and hidden public critical cells, not by a missed E72-contamination gate for E176.
- Do not repeat: treating E144's p95 crossing as positive contamination proof, or replacing E176 with E144/E154 based only on clean-shape E72 score.

## FH167. Evidence balance certifies E176 as an expected-score winner

- Failed hypothesis: once E179/E180/E186/E192 evidence is consolidated, E176 should be certifiable as the likely public winner rather than merely selected as the next information sensor.
- Observed result: E193 gives E176 the only positive evidence balance (`3.100`) and keeps it first, but the warnings are still material. E181 inherited binary worlds are adverse/mixed for E176, and E183 local subject/flank/visible priors reject the favorable pressure branch for all candidates. The ledger therefore supports sensor priority, not expected-score certainty.
- Why discard: a positive cross-sensor balance is not the same as a hidden-label certificate. The unresolved counter-evidence is exactly in the public-sensitive cell-resolution layer that has produced the 0.57629 plateau.
- Implementation issue possible: medium. Evidence weights in E193 are bookkeeping weights, not learned public-LB weights. Low for the narrow failure because the script explicitly preserves the adverse binary and local-prior signals instead of optimizing them away.
- Bottleneck implication: the current bottleneck is still latent-view conflict and hidden public critical-cell sign ambiguity. E176 is the best next question, not the solved answer.
- Do not repeat: describing E176 as guaranteed or locally certified. Describe it as the broad/Q2-underopen public sensor, and decode feedback with E177 before any follow-up.

## FH168. E193 chooses E176 only because of arbitrary evidence weights

- Failed hypothesis: the E193 E176-first decision is so weight-sensitive that a modest change in evidence weights or removal of one source would promote E154/E144, making E176 priority a bookkeeping artifact.
- Observed result: E194 finds E176 wins every single-source leaveout. It also wins `0.905950` of moderate loguniform `0.5..2` family-weight draws and `0.896500` under 20% family dropout. Missing-evidence penalties only strengthen E176 because E154/E144 have more missing comparable axes.
- Why discard: ordinary robustness stress does not flip the decision. E176 priority is not just arbitrary E193 weighting.
- Implementation issue possible: medium. E194 still uses interpretive source families and does not learn weights from public LB. Low for rejecting the narrow artifact claim because source leaveout and randomized weights directly stress the bookkeeping.
- Bottleneck implication: the real uncertainty is not arbitrary ledger scoring. It is which latent view deserves trust: pair/shape/broad-body evidence or inherited binary-world counterprior.
- Do not repeat: dismissing E176 solely because the ledger is weighted. The coherent E176 objection is more specific: trust E181 binary-world evidence above `1.760x`, or discount pair geometry below `0.725x` after removing non-comparable visible/top-cell evidence.

## FH169. E154 should be submitted first because it is the strongest counter-world

- Failed hypothesis: after E194 identified E154 as the explicit counter-world to E176, the next public slot should be E154 rather than E176.
- Observed result: E195 shows E154 is a good counter-world but a narrower first measurement. E176-vs-E154 moves `1027` cells over `238` rows with focus expected delta `-0.000093546`, while E154-vs-E144 is barely readable at `-0.000002432` and E154-vs-E155 is not readable at `-0.000001796`. E176 has adverse decoder bands that route to E154/search; E154 feedback does not directly resolve whether E176's broad/Q2-underopen worldview is public-real.
- Why discard: first-sensor choice should maximize worldview resolution, not simply submit the best alternate branch. E154 first mainly asks whether repaired E144-collinear S3 active-boundary repair is real; it does not kill or validate the current E176 broad branch.
- Implementation issue possible: low. The script only joins existing pre-registered decoder and pairwise files; it does not create new labels or tune thresholds. Medium for the broader ranking because actual public feedback could still surprise either decoder.
- Bottleneck implication: the bottleneck remains hidden-label/worldview underidentification. The next public slot should be used to distinguish pair/shape/broad-body vs binary-world, then route to E154 if E176 loses.
- Do not repeat: promoting E154 ahead of E176 merely because it is the explicit counter-world. Promote E154 first only under an intentional high-binary/low-pair prior, or after adverse E176 feedback.

## FH170. Row/order/block motif nearest anchors can certify E176 before public feedback

- Failed hypothesis: E176's decisive cells can be certified or rejected before public feedback by comparing their row/order/block/target motif profile to known public-winning and public-losing transitions.
- Observed result: E196 finds `0/9` action-grade motif views. The best view, `top4 / sequence_axis_flank`, reaches known-pair LOO accuracy `0.833333` but fails the exact E101/E95 boundary. In that best view E176 is nearest to the known losing `e72_vs_e95` transition, with only a near-tie inverse-distance new_won vote `0.505761`. Top33 shifts nearest to `mixmin_vs_a2c8`, but top33 LOO accuracy collapses to `0.333333`.
- Why discard: motif structure exists, but it is not invariant across the exact frontier boundary that matters most. A selector that misses E101/E95 cannot safely override the E177/E195 public-sensor plan.
- Implementation issue possible: medium. Known public anchors are few and nearest-neighbor geometry is coarse. Low for rejecting this exact shortcut because every view fails the explicit action-grade gate.
- Bottleneck implication: row/order/sequence motif is not enough by itself. The missing representation must resolve hard-label critical cells at frontier-boundary scale, not merely cluster them by block anatomy.
- Do not repeat: motif-only nearest-anchor certification, motif-gated E176 variants, or using E176's E72-like top4 motif as a standalone demotion rule.

## FH171. Public support-mass inversion can directly select the next submission

- Failed hypothesis: inverting known public LB pairs into observed support mass is enough to choose the next file by stress score.
- Observed result: E197 produces a useful slippage decoder but not a clean selector. E172 has slightly higher visible support surplus than E176 (`0.070613` vs `0.061761`), while E176 remains the more informative broad/Q2-underopen sensor. E166 has strong focus stress but hard-fails under E72-vs-mixmin slippage. E154/E144/E155 are thin-margin branch sensors.
- Why discard: the support-mass score mixes two quantities: expected-score safety and information value. A safer same-family contrast can score better without asking the live broad/Q2-underopen question. A broad safety-atlas falsification sensor can score well but carry too much E72-like tail.
- Implementation issue possible: low for rejecting selector use; the algebra is direct. Medium for absolute slippage values because public subset composition is still hidden.
- Bottleneck implication: public LB observations can define failure modes, but they do not remove hidden-world underidentification. We still need public sensor feedback or a stronger decisive-cell representation.
- Do not repeat: ranking candidates solely by support surplus, clean-or-better rate, or slippage stress score.

## FH172. E176 should be demoted because its only losing stress is E72-like

- Failed hypothesis: since E197 shows E176 loses under E72-like adverse slippage, E176 should be treated as structurally E72-like and demoted before public feedback.
- Observed result: E198 joins the E197 slippage law with E192 clean-shape E72 anatomy. E176 branch-loses under E72-vs-mixmin stress, but its max clean E72 probability is only `0.000008`, far below non-E72 p95 `0.020815`, non-E72 p99 `0.044812`, and the known-positive floor `0.804849`.
- Why discard: "can lose under an E72-like aggregate slippage" is not the same as "has an E72-like movement shape." The clean structural detector sees E176 as non-E72. The proper use is failure attribution after public feedback, not pre-feedback demotion.
- Implementation issue possible: medium. The clean detector has top-k recall `0.666667` and all E72 positives still come from one anchor family, so absence of clean-shape exposure is not a proof of safety. Low for rejecting this narrow demotion shortcut.
- Bottleneck implication: the active bottleneck is hidden public-label realization at critical-cell scale. We can describe an E72-like failure scenario, but the available structural diagnostics do not identify it before feedback.
- Do not repeat: creating E72-demoted E176 siblings or dropping E176 solely because E197 includes E72-like failure analogues. Use E177/E197 decoding after public feedback instead.

## FH173. Unscored E176 follow-up candidates hide direct E72-shape exposure

- Failed hypothesis: E198 was incomplete because E172/E174/E166/E155 were not pressure-branch-scored; one of those direct candidate movements may be E72-shaped and unsafe as a follow-up route.
- Observed result: E199 scores direct candidate-vs-E95 movement for all E197 candidates. E172 `0.000087`, E174 `0.000097`, E176 `0.000097`, E166 `0.000677`, E154 `0.007860`, and E155 `0.009284` all stay below non-E72 p95 `0.020815`. Only E144 crosses p99 at `0.054385`, still far below the positive floor `0.804849`.
- Why discard: the missing candidates do not hide clean-shape E72 exposure. The post-E176 route can be chosen by information role and margin fragility rather than by fear of unscored E72 shape.
- Implementation issue possible: medium. Direct candidate-vs-E95 scoring is not identical to pressure-branch scoring, and the clean detector remains imperfect. Low for rejecting the narrow missing-score concern because direct scoring is the exact movement that would be submitted.
- Bottleneck implication: follow-up uncertainty is not E72-shape contamination for E172/E154. It remains hidden-label slippage, repaired-branch margin fragility, and public hard-label critical-cell realization.
- Do not repeat: blocking E172/E154 follow-up solely because they lacked E192 pressure-branch scores. Use E199 direct scores for that caveat.

## FH174. E172 should replace E176 as the first sensor because it is safer

- Failed hypothesis: after E199, E172's cleaner shape and larger support-mass surplus are enough to submit E172 before E176.
- Observed result: E200 shows E172 is safer but lower-information. E176 has `0.0000106885` focus expected edge over E172, equal to `0.698x` of the E95-over-mixmin public edge. E172's visible/focus surplus advantages are `0.008852`/`0.007054`, and its clean-shape E72 probability advantage is only `0.00000972`. E176-vs-E172 is a `75`-cell rollback contrast, while E176-vs-E154 is a `1027`-cell counter-world contrast.
- Why discard: the first public slot should resolve the largest live worldview conflict, not merely choose the safest same-family rollback. E172's safety gain is real but does not replace E176's broader Q2-underopen sensor role.
- Implementation issue possible: low. E200 uses locked E177/E197/E199 artifacts and derives E172-vs-E95 algebraically from pairwise rows rather than fitting a new selector.
- Bottleneck implication: safety and information value are different axes. The current bottleneck remains hidden-world underidentification, so the first sensor should maximize resolution; safety fallback comes after the relevant band.
- Do not repeat: promoting E172 ahead of E176 solely from support surplus or clean-shape E72 probability. Use E172 only after an E176 tie/small-loss or under an explicit private-risk-minimization objective.

## FH175. E176 public feedback can be interpreted after seeing the scalar score

- Failed hypothesis: because E177 already has score bands, it is acceptable to wait for E176 public LB and then reason informally about what the number means.
- Observed result: E201 shows this is too loose. The exact E176 file is now fixed by SHA256 `34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206`, and every public-score regime has a pre-registered route. Better than `0.5762883298` means E176 is useful but does not justify an immediate sibling; `0.5762883298..0.576300366` activates only E172 as same-family safety; worse than `0.576300366` demotes partial-reopen toward E154/search; worse than `0.5763413298` closes the same-family expected-score lane.
- Why discard: scalar post-hoc interpretation is exactly the mechanism that creates redundant keep-factor siblings and ambiguous branch decisions. It does not respect the fact that E176-vs-E172 is only `75` cells while E176-vs-E154 is the broader `1027`-cell worldview conflict.
- Implementation issue possible: low. E201 is file/schema/router governance, not a fitted selector. The only possible issue would be submitting a different file than the audited hash.
- Bottleneck implication: the bottleneck is not only model signal; it is also feedback-resolution discipline. Public LB can help only if each observation kills or preserves a specific worldview.
- Do not repeat: making another E176/Q2 sibling directly from the public scalar. Decode with E177/E201 first.

## FH176. E176 public feedback can be read as Q2-only amplitude feedback

- Failed hypothesis: because the next file is named `q2_to0p75`, E176's public score can be interpreted mainly as evidence for or against Q2 keep-factor amplitude.
- Observed result: E202 shows the file name is misleading at component level. S-targets carry `0.651098` of focus-prior expected movement versus `0.348902` for Q-targets, and between-train-runs rows carry `0.807772`. Q2 is the largest raw movement target (`0.209702`) but only `0.121416` of expected contribution, behind S3/S1/S4/Q1. Top33 hard-label visibility is weak (`p_low=0.014667`).
- Why discard: raw probability movement is not the same as expected public-relevant responsibility. A scalar Q2 read would over-credit the most moved target and under-credit the S-stage/body structure that actually carries the expected edge.
- Implementation issue possible: low for the narrow rejection because the decomposition uses the locked E176 tensor and existing E177/E179/E201 artifacts. Medium for final causality because the actual E176 public score is still pending.
- Bottleneck implication: the plateau is still a component/tail-resolution problem, not a one-dimensional Q2 amplitude problem. The useful signal lives in how broad S-stage body, Q2 guard, and hard-label tail cancel.
- Do not repeat: Q2 keep-factor sibling sweeps directly after E176 public feedback. Use E201 score route plus E202 component responsibility first.

## FH177. E176 is mainly a compact top33 critical-cell bet

- Failed hypothesis: E176's useful edge is mostly concentrated in top33/top8 swing cells, so public feedback should be interpreted primarily as a compact critical-cell selector result.
- Observed result: E203 shows top33 cells carry only `0.226424` of the E179 focus body and top8 only `0.068714`. Dropping top33 still leaves `0.773576` of the focus body. The broad components are much larger: S-only `0.644881`, primary S3/S1/S4 `0.573289`, and between-train-runs `0.774524`.
- Why discard: top33 is public-fragile and weakly visible, but not sufficient to explain the whole E176 movement. Treating E176 as top33-only would erase the broad body that makes it an information-rich sensor.
- Implementation issue possible: low for the narrow rejection because the knockout uses the exact E179 moved-cell table. Medium for final public attribution because public labels are still unobserved.
- Bottleneck implication: the current bottleneck is broad-body versus compact-tail cancellation, not a pure critical-cell selector. A loss can still mean body-tail cancellation rather than absence of body.
- Do not repeat: replacing E176 with a top33-only variant or reading E176 feedback as only a top-cell selector before checking the score band and component route.

## FH178. E172, E154, and E174 are interchangeable post-E176 rescues

- Failed hypothesis: after E176 feedback, E172/E154/E174 can be treated as nearby rescue candidates on one scalar axis.
- Observed result: E204 separates their geometry. E172 is a same-family rollback: `75` changed cells, all inside E176, rollback share `1.000000`, off-body share `0.000000`, and body rollback fraction `0.089780`. E154 is a body-exit counter-world: `1027` changed cells, `123` off-E176 cells, off-body abs share `0.292501`, and body rollback fraction `0.877576`. E174 is a Q2 amplitude probe: `21` changed cells, rollback `0`.
- Why discard: these files answer different hidden-world questions. Choosing among them by scalar closeness would produce an uninformative public observation.
- Implementation issue possible: low. The comparison uses locked submission tensors and direct cell-level movement overlap. Medium for final public causality because E176 public feedback is pending.
- Bottleneck implication: candidate selection remains a worldview-routing problem, not a local rescue ranking problem.
- Do not repeat: swapping E172/E154/E174 after E176 feedback without first matching the E201/E202/E203/E204 route condition.

## FH179. E176 score routing can be safely reconstructed from notes by hand

- Failed hypothesis: because E201-E204 are documented, the eventual E176 public score can be interpreted manually from those notes without an executable route.
- Observed result: E205 converts the notes into one deterministic decoder. Example `0.576291` maps to `tie` / E172 same-family safety, while example `0.576303` maps to `e101_worse_mixmin_safe` / E154 body-exit counter-world. Clean win bands explicitly route to no immediate sibling.
- Why discard: manual interpretation reintroduces the exact post-hoc scalar freedom that E201 tried to remove. The score band, component attribution, body/tail constants, and follow-up geometry must be read together, not reconstructed from memory.
- Implementation issue possible: low. E205 is a join over locked CSV artifacts and creates no submission. The main operational risk is submitting a follow-up without running it with the real score.
- Bottleneck implication: one plateau bottleneck is feedback-resolution discipline. Public LB is useful only if each observed scalar kills or preserves a specific worldview.
- Do not repeat: choosing E172, E154, E174, or a Q2 sibling from scalar intuition after E176. Run `python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score <E176_PUBLIC_LB>` first.

## FH180. E176 broad partial-reopen is an expected-score improvement over E95

- Failed hypothesis: E176's broad S-stage / between-train-runs body with Q2 under-opening is not just a useful public sensor, but a likely expected-score improvement over E95.
- Observed result: E176 public LB is `0.576311831`, worse than E95 by `+0.0000205012` and worse than mixmin by `+0.0000051905`. E205 decodes the score as `branch_loss`, not tie/small-loss.
- Why discard: the broad body may be real locally, but public frontier LogLoss is decided by hard-label tail realization at a scale where this body gives back the E95 edge. The scalar score also does not justify Q2-only tuning because E202/E203 showed Q2-only is a small expected-share component.
- Implementation issue possible: low for the public outcome and decoder route. Medium for global private inference because public subset may not equal private, but this candidate's expected-score public route is closed.
- Bottleneck implication: the plateau is not solved by broad partial-reopen amplitude. The missing object is a representation that can identify public-favorable high-swing cells or a genuinely non-collinear latent branch.
- Do not repeat: E174/Q2 sibling, E172 immediate safety, or E169/E166 broad expected-score follow-up after this branch-loss result. Use E154 only as body-exit counter-world, or search outside the same-family lane.

## FH181. Any subject-order JEPA transition is healthy enough for true JEPA training

- Failed hypothesis: because this dataset has strong subject/date structure, a true JEPA should train directly on same-subject adjacent or lagged rows, especially with the existing LeJEPA block-canvas latent.
- Observed result: E207 shows the strongest existing LeJEPA subject-lag2 regime has high readiness (`0.668530`) but poor increment Gaussianity (`0.194814`) and high split distance CV (`0.660020`), so it is demoted to `energy_or_auxiliary`. Subject-lag1 block-canvas regimes are also auxiliary, not certified. The only `true_jepa_candidate` is `broad_stage2_pca64 + feature_nn1_all`.
- Why discard: subject/order autocorrelation alone is not enough. Under the new LeJEPA reading, the transition must also have Gaussian-ish increments, stable stationarity, and a nontrivial alignment gap. Subject lag structure is visible but not identifiable enough as the main JEPA world-model target.
- Implementation issue possible: medium. The audit uses PCA summaries and proxy Gaussianity tests, so a more specialized latent could pass later. The narrow claim being discarded is only "use any subject-order JEPA transition directly."
- Bottleneck implication: the bottleneck is not lack of JEPA branding or network capacity. It is choosing a positive-pair regime whose transition is actually identifiable and public-relevant.
- Do not repeat: training one large JEPA over all subject lags or averaging every positive-pair regime. Start with feature-neighbor JEPA, and keep subject/order/block-canvas latents as gates until they pass increment/stationarity diagnostics.

## FH182. A trained JEPA predicted latent can be submitted wholesale

- Failed hypothesis: once E208 shows the feature-neighbor JEPA task is learnable, the full predicted latent or every locally helpful JEPA feature should be blended into a submission.
- Observed result: E208 training is real, but geometry and downstream stress are selective. `pred_mean` has rank fraction `0.287411` and covariance condition `1365.92`, while the healthier `hidden_mean` still does not translate broadly. S2 has strong local/subject deltas but fails geometry with positive geometry delta. Q1/Q2/S1/S3 provide no stable materialization path. Only Q3 residual-self pc10 and S4 predicted pc14 pass the E208 gate.
- Why discard: learnability is not submission health. A compressed predicted representation can encode shortcuts, and local OOF gains can be fold-specific. LeJEPA discipline requires geometry and stress to decide which pieces survive.
- Implementation issue possible: medium. E208 is CPU MLP/PCA based and could improve with stronger architecture, different masks, or target representation. Low for rejecting the current wholesale-submission shortcut because the generated diagnostics directly show anisotropy and target selectivity.
- Bottleneck implication: JEPA can expose hidden structure, but the bottleneck is probability translation and target-specific calibration risk. The useful branch is narrow Q3/S4 residual movement, not global capacity.
- Do not repeat: all-feature E208 blend, S2 local shortcut materialization, or "JEPA succeeded therefore submit the latent" reasoning. Run E209 Q3/S4-only materialization and hard-tail/frontier geometry first.

## FH183. E209 proves that JEPA should be applied broadly or at high scale

- Failed hypothesis: after E208/E209, the correct next move is to trust the learned JEPA signal broadly, add S2 back because it was locally strong, or increase Q3/S4 scale because expected local deltas improve.
- Observed result: E209 opens only low-scale Q3/S4 candidates. `q3_center_c010_s4_rank` survives OOF, subject-half, and geometry stress, but high-scale Q3/S4 grafts fail the frontier gate. S2 remains excluded from materialization because E208 geometry was adverse. The selected candidates still need only `1` hard-label cell for the `2e-6` guard, so public hard-tail brittleness remains.
- Why discard: JEPA learnability does not remove LogLoss tail risk. The low-scale gate is not a conservative habit; it is the stress result. Pushing scale or target coverage would restore the same collapse/shortcut failure modes that LeJEPA warned about.
- Implementation issue possible: medium. A stronger architecture or a different context-target definition may produce a healthier latent later. Low for rejecting the current E209 broad/high-scale shortcut because the generated frontier-stress table directly marks those rows as non-gated.
- Bottleneck implication: the bottleneck is not whether JEPA can learn anything. It can. The bottleneck is translating a learned representation into public-stable calibrated probability movement.
- Do not repeat: high-scale E209 Q3/S4 submissions, S2 comeback from local OOF alone, or full-latent JEPA blending without new geometry evidence.

## FH184. Target-dependency gating is a strict E209 replacement

- Failed hypothesis: because E210 dependency-gated candidates improve public-prior hard-tail anatomy, they should replace E209 as the next generic JEPA submission.
- Observed result: the selected E210 closer files are much worse than ungated E209 on local validation. The top selected e154 closer file has OOF `-0.000482` versus ungated E209 `-0.001273`, and geometry `-0.000096` versus ungated geometry `-0.000939`. Cell anatomy also splits by target: S4 dependency alignment is useful, while Q3 non-aligned cells often carry the larger local improvement.
- Why discard: the gate may be a good public-tail sensor, but it cuts away a large part of the locally validated JEPA body. That is not a strict dominance relationship.
- Implementation issue possible: medium. A better conditional target model or Q3/S4-specific gate could preserve more body. Low for rejecting the current strict-replacement claim because the OOF/geometry deltas are direct.
- Bottleneck implication: the bottleneck is target-specific translation. S4 can use dependency alignment; Q3 needs a different gate or public-tail sensor.
- Do not repeat: promoting E210 ahead of E209 without an explicit hard-tail localization question or public feedback from E209.

## FH185. A single Q3/S4 dependency gate is the right JEPA translator

- Failed hypothesis: Q3 and S4 should use the same dependency gate because both are E209 JEPA-derived targets.
- Observed result: E211 shows the better policy is split. Q3 raw movement carries the main local body, while S4 benefits from dependency-toward/closer gating. Q3 raw + S4 toward improves OOF to `-0.001318`, better than ungated E209's `-0.001273`, whereas E210's shared closer gate fell to `-0.000482`.
- Why discard: target grouping by "Q3/S4 both JEPA" hides different noise geometry. Q3 is residual-body dominated; S4 is dependency-consistency dominated.
- Implementation issue possible: low for this rejection because E211 directly compares raw/gated/zero/anti S4 controls while holding Q3 policy explicit. Medium for public inference until LB feedback arrives.
- Bottleneck implication: the remaining JEPA bottleneck is not simply "gate or do not gate"; it is per-target translation.
- Do not repeat: applying one dependency gate across Q3 and S4 without a target-specific justification.

## FH186. E210 should be the next JEPA submission because its hard-tail survival score is highest

- Failed hypothesis: E210's stronger public-prior hard-tail anatomy should make it the next JEPA public slot ahead of E211 and E209.
- Observed result: E212 ranks E210 behind E211 and the raw E209 Q3/S4 control once parent integrity and geometry are included. E210's survival scores are high, but the selected closer files lose most of the E209 local body: local delta around `-0.000482..-0.000550` versus E209 `-0.001273`, and geometry delta around `-0.000096..-0.000026` versus E209 `-0.000795`.
- Why discard: hard-tail survival alone is not a healthy JEPA criterion. It can be achieved by cutting away useful Q3 body. E211 preserves Q3 raw movement while applying the dependency signal only to S4, so it asks the sharper hypothesis first.
- Implementation issue possible: medium. If public feedback later strongly favors E210 after E211/E209 fail, the current parent-integrity penalty was too strong. Low for the current ordering decision because E212 uses locked selected artifacts and no new model fit.
- Bottleneck implication: the JEPA bottleneck is feedback ordering and probability translation, not just hard-tail minimization.
- Do not repeat: promoting a dependency-gated JEPA candidate solely because its public-prior survival score is larger. Require parent-integrity and target-specific evidence.

## FH187. E211's live Q3/S4 axes are probably random JEPA coordinate cherry-picks

- Failed hypothesis: the Q3 `e208_resid_self_pc10` and S4 `e208_pred_pc14` axes survived only because many JEPA coordinates were scanned.
- Observed result: E213 tests both axes against global permutations, within-subject permutations, and same-family PC pools. Both axes hit the minimum empirical permutation p-value available with 48 reps (`0.020408`) for global and subject nulls. Both are rank `1/16` in their same-family coordinate pool. Q3's pool runner-up is much weaker (`-0.002200` versus `-0.005775`), and S4's pool runner-up is adverse (`+0.001377` versus `-0.003134`).
- Why discard: the selected axes are not easily reproduced by shuffled values or neighboring PCs under the same OOF correction path.
- Implementation issue possible: medium. A larger permutation budget or independent JEPA training seeds could refine p-values, but the current effect sizes are wide enough to reject the cheap cherry-pick explanation.
- Bottleneck implication: if E211 fails publicly, the likely failure is public-tail probability translation, anchor confounding, or calibration risk, not absence of a real JEPA axis.
- Do not repeat: dismissing the current JEPA branch as random axis selection without a stronger null or independent retraining audit.

## FH188. A small supervised benefit classifier is enough to gate JEPA translation

- Failed hypothesis: E211's remaining translation risk can be fixed by training a small public-free classifier to predict whether each Q3/S4 raw JEPA cell improves OOF log loss.
- Observed result: E214's benefit gates have only weak sorting power: Q3 AUC `0.552169`, S4 AUC `0.568968`. Probability, rank-normalized, margin, and dependency-composed gate variants all lose too much local signal. The best benefit-gated local policy (`q3raw_s4benefit_rank`) reaches only `-0.000918`, while raw JEPA is `-0.001273` and E211 toward is `-0.001318`.
- Why discard: a good gate must preserve the Q3/S4 body and reduce public-tail risk. E214 improves geometry for one variant (`-0.000987`) but sacrifices enough OOF/local signal that no policy passes frontier selection.
- Implementation issue possible: medium. The gate probability calibration is weak and could be improved, but rank-normalization was also tested and still failed to close the gap.
- Bottleneck implication: the translation problem is not solved by cell-wise benefit classification. It likely needs a different JEPA target representation, a narrower public-tail rule, or public-feedback-guided routebook interpretation after E211.
- Do not repeat: training a generic benefit gate over the same E209/E211 Q3/S4 step unless a new feature family gives materially higher benefit AUC.

## FH189. The strongest E215 local masked-family JEPA combo should be submitted directly

- Failed hypothesis: because `q1_s2_s4_rank` has the best E216 local/geometry profile, it should be the natural masked-family JEPA submission.
- Observed result: `q1_s2_s4_rank` has strong local evidence (`delta=-0.001807`, subject-half win `1.000`, geometry `-0.001628`) but fails frontier stress. At useful E95/E154 scales, its expected public-sensitive movement becomes positive, while S2-only remains negative and low bad-axis energy.
- Why discard: local strength is not sufficient when public-tail stress says the broad move points the wrong way. This repeats the plateau law: public-safe narrow movement beats broad local improvement.
- Implementation issue possible: medium. The public-tail stress is a proxy, not the leaderboard. But the contrast is large enough to avoid direct broad-combo submission before a specific audit.
- Bottleneck implication: masked-family JEPA is useful, but public-safe translation is target-selective. S2 was the clean local survivor, but later public feedback rejected it; Q1/S4/S2 all need separate public-tail explanation before another E215/E216 submission.
- Do not repeat: promoting the locally largest multi-target JEPA combo without checking frontier stress and target-specific public-tail direction.

## FH190. A more faithful teacher-student JEPA is itself enough to create the next submission

- Failed hypothesis: replacing fixed PCA targets with a closer EMA teacher-student tabular JEPA should unlock a healthier latent and therefore a direct candidate.
- Observed result: E217 training is clearly nontrivial: validation loss is about `7%` of mean-teacher baseline and `4.5%` of shuffled-teacher baseline. But downstream materialization fails. Best S2 `e217_teacher_pc07` has local delta `-0.002853` and subject-half win `0.757692`, but geometry delta is `+0.000410`; Q3 residual rows are closer to neutral but below the pass thresholds. E217 selects no submission.
- Why discard: better JEPA mechanics did not remove the plateau bottleneck. The learned full-row latent behaves like a fold-sensitive calibration energy, not a public-safe probability translator.
- Implementation issue possible: medium. The objective is small CPU tabular JEPA and could change with teacher target, mask schedule, or a target-specific materializer. Low for rejecting direct E217 submission because the current geometry table directly fails the gate.
- Bottleneck implication: the limiting factor is still translation/public-tail geometry, not merely whether JEPA is implemented faithfully. JEPA helps only when target-specific sensors survive public-tail translation; after E216 feedback, E211 Q3/S4 is the only live example.
- Do not repeat: "make JEPA more real, then submit its strongest local feature" without target-specific geometry and frontier stress.

## FH191. E216 S2-only masked-family JEPA is a public-safe non-collinear sensor

- Failed hypothesis: after E216 rejected the broad Q1/S2/S4 masked-family move, its S2-only `s2_rank` survivor should be public-safe enough to test as the next non-collinear JEPA lane.
- Observed result: `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` scored public `0.5772865088`, which is `+0.0009951790` worse than E95, `+0.0009798683` worse than mixmin, and `+0.0009861428` worse than E101.
- Why discard: the miss is too large to treat as frontier noise. Local OOF, subject-half, geometry, bad-axis, and hard-tail stress all failed to detect a public-adverse S2 tail for this anchor/scale.
- E219 root cause: E154 body alone cannot explain the miss under the current 250x7 public-cell normalization (`all_adverse_delta=0.000924070`), but the pure S2 graft can (`all_adverse_delta=0.006048995`). Near-observed focus-prior worlds attribute mean `0.000920169` to the S2 graft and `-0.000004004` to E154 body.
- Implementation issue possible: medium. Smaller scale may lose less, but E219 shows E95-anchor and lower-scale siblings are not automatically safe because the pure S2 graft has enough adverse capacity. Low for keeping E216 as a next submission lane because the first public sensor directly rejects its selection logic.
- Bottleneck implication: JEPA can expose local latent signal, but S2 translation is especially public-tail brittle. The missing stress dimension is support probability: focus swing-weighted support for the S2 graft is only `0.473945`, below `0.5`, despite slightly favorable expected delta.
- Do not repeat: submitting remaining E216 siblings as automatic followups. First explain why S2-only failed despite passing the stress stack, or rebuild the translator with a target-specific public-tail audit.

## FH192. A simple S2 support/tail threshold can rescue E216

- Failed hypothesis: E219's support-probability diagnosis can be turned into a simple threshold or top-risk-cell drop that preserves E216's favorable S2 expected movement while bounding public-tail loss.
- Observed result: E220 scans focus/subject/nearest support thresholds, expected-negative filters, and E219 posterior-risk drops. No gate passes. High-support gates are expected-adverse (`focus_support_ge_0p7` expected `+0.000018940`), while expected-negative gates remain worst-case unsafe (`focus_support_ge_0p6_expected_neg` adverse `0.001402108`; `expected_neg_only` adverse `0.002118163`, both above the observed E216 miss `0.0009951790`).
- Why discard: the support-safe cells and expected-helpful cells are not the same simple subset. A scalar support threshold just trades one failure mode for another.
- Implementation issue possible: medium. A richer trainable gate may still work, but the current public-tail threshold/drop rules are not enough and should not create a submission.
- Bottleneck implication: S2 needs a real translator, not a post-hoc public-tail threshold. This strengthens the view that 0.576x is a calibration/hidden-subset tail bottleneck rather than an encoder-capacity bottleneck.
- Do not repeat: submitting an E220 thresholded S2 file without an OOF-reproducible support model.

## FH193. A trainable OOF S2 support classifier can rescue E216

- Failed hypothesis: E216's S2 failure can be fixed by training a row-level classifier to predict whether the E216 S2 movement helps in OOF, then applying that support gate to test.
- Observed result: E221 shows support is locally learnable but not submission-stable. Best classifier AUCs are `0.748104` on stratified folds, `0.717482` on row-contiguous folds, and `0.713730` under subject-LOO. Many OOF gates keep strong S2 gains, but none also pass submission-side expected/adverse/support stress. The best OOF-safe gates either have positive expected focus movement on test or adverse capacity above the observed E216 miss; the submission-tail-safe gates fail OOF support/win criteria.
- Why discard: the local support boundary and the public-facing test-tail boundary are not the same object under the current E215/E216 representation. A row support classifier learns local label compatibility, not the hidden public subset support geometry.
- Implementation issue possible: medium. The classifier family is intentionally small and tabular. But the failure is not weak local modeling: AUC is high enough locally, and the joint failure occurs after test-tail stress. That is the relevant rejection for a submission candidate.
- Bottleneck implication: S2 JEPA is not blocked by encoder capacity alone. It is blocked by train/test-public support mismatch and LogLoss tail exposure. Reopening S2 requires changing the target representation or adding support/tail structure to the JEPA objective itself.
- Do not repeat: ordinary benefit/support classifiers on E215 S2 features as submission gates. Use them only as diagnostics unless a new representation target changes the test-tail behavior.

## FH194. Original full-Q3 E211 is support-safe after the E216 lesson

- Failed hypothesis: because E211 Q3/S4 passed local, subject-half, geometry, bad-axis, and focus-expected stress, it should also pass the E216-derived support/tail criterion.
- Observed result: E222 shows the live E211 grafts are expected-good but low-support. E211 E154 closer graft has expected focus `-0.000655277`, adverse `0.004765654`, and support probability `0.463231`; E211 E95 toward has expected `-0.000654330`, adverse `0.004824911`, and support `0.463587`.
- Why discard: support probability remains below `0.5`, and the target breakdown shows Q3 is fragile: expected focus only about `-0.000144..-0.000147` while Q3 top1/expected exceeds `1.0`. This is too similar to the E216 failure pattern to call original full-Q3 E211 safe.
- Implementation issue possible: medium. E222 uses public-free priors, not true public labels, and known winners can also have weak visible support. But E216 public feedback made this exact failure mode actionable enough to update the candidate order.
- Bottleneck implication: E211's JEPA axes are real, but target-level probability translation remains the bottleneck. The hidden law is not "use the whole JEPA move"; it is "preserve S4 body and control Q3 tail."
- Do not repeat: submitting original full-Q3 E211 as the default JEPA file without acknowledging that public feedback will be a support-tail sensor. Prefer E223 q3-scale `0.75` if testing this lane now.

## FH195. E223 q3_scale 0.75 is the best E211 tail knee

- Failed hypothesis: after E222, reducing Q3 from `1.0` to `0.75` is enough, and lower Q3 scales mainly throw away useful JEPA signal.
- Observed result: E224's Pareto sweep selects q3_scale `0.625`, not `0.75`. Best selected row `e224_q3s0p625_s4closer_e154_a0p5` has expected focus `-0.000623352`, adverse `0.003400775`, support `0.465984`, Q3 top1/expected `0.875120`, and geometry `-0.000505582`. The `0.75` rows keep more local/expected body but fail the stricter E224 tail gate because Q3 top1/expected remains above `0.92..0.94` and adverse capacity is higher.
- Why discard: E223 was a useful first correction, but the sharper stress says Q3 is still too concentrated at `0.75`. The best current hidden-world question is not "does reduced Q3 work?" but "does S4 body plus Q3 capped near `0.625` transfer to public?"
- Implementation issue possible: medium. The E224 gate is still a public-free stress proxy and support remains below `0.5`. Low for replacing E223 in submission order because the sweep is locked before public feedback and uses the same E222 failure criterion derived from E216.
- Bottleneck implication: the JEPA bottleneck is amplitude-specific target translation. Stronger local Q3 improvement can be the wrong public question if it raises top-cell hard-label exposure.
- Do not repeat: treating q3_scale `0.75` as an optimal constant. Re-evaluate target-specific scales under adverse capacity, support probability, and top-cell concentration whenever a JEPA movement is materialized.

## FH196. E209/E210/E211/E223 are independent alternatives to E224

- Failed hypothesis: if E224 is uncertain, nearby JEPA files such as E209/E210/E211/E223 can be used as independent fallback sensors.
- Observed result: E226 marks them as the same Q3/S4 JEPA family. E224 is collinear with E223 (`0.996078`) and full E211 (`0.975464`); E209/E210 variants also sit on the same family line even when their scalar scores differ.
- Why discard: another same-family file would mostly retest Q3/S4 amplitude/anchor details, not a new hidden-world law. E225 already provides the correct E224 feedback routebook.
- Implementation issue possible: low. The movement vectors are deterministic submission deltas, not model-estimated features.
- Bottleneck implication: the post-E224 question is not "which sibling has the prettiest local metric"; it is whether capped-Q3/S4 translation transfers at all. If it fails, search non-collinear structure.
- Do not repeat: submitting E209/E210/E211/E223 as if they were a fresh JEPA lane after E224 feedback.

## FH197. The E52 bridge near-tie can be revived by E226 shape

- Failed hypothesis: because `bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv` has decent non-E224 shape, it should be revived as a post-E224 candidate.
- Observed result: E226 classifies it as `local_rejected_neartie`, not a live candidate. E52 already conditioned binary worlds on mixmin and found no strict/loose better-than-mixmin replacement; this bridge was only a near-tie with positive median/max risk.
- Why discard: movement shape alone cannot override a prior experiment that directly tested the mixmin-relative replacement claim.
- Implementation issue possible: low for routing. The file can remain a diagnostic contrast, but not a submission candidate without new evidence.
- Bottleneck implication: old near-ties are not the hidden 0.54 route. We need new structure, not re-ranking stale bridge files after a bad JEPA result.
- Do not repeat: resurrecting bridge blends from cosmetic non-collinearity without a new falsifiable hypothesis.

## FH198. E224/E166/E154 should be blindly blended before public feedback

- Failed hypothesis: because E224, E166, and E154 are the live post-E216 files, a weighted blend across all three should be a safer next candidate than choosing one worldview.
- Observed result: E228 shows the three-way geometry is not a single blendable family. E224/E166 cosine is only `0.074348`, with top50 overlap `1` and same-sign E166 covering only `0.035638` of E224 mass. E166/E154 cosine is `0.061662` with top50 overlap `0`. E224/E154 are related because E154 is mostly inherited inside E224: `0.885621` of E154 mass is same-sign covered by E224.
- Why discard: a tri-blend would destroy public-feedback identifiability. If it wins, we cannot tell whether JEPA Q3/S4, broad safety-atlas structure, or cancellation helped; if it loses, we cannot isolate the failed branch.
- Implementation issue possible: low. The rejection is deterministic movement geometry, not a stochastic model result. A future blend may become valid only after one component receives public feedback and attribution.
- Bottleneck implication: candidate selection is now an observation-design problem. The next useful public slot should isolate a hidden-world law instead of averaging mutually underidentified laws.
- Do not repeat: building a blended submission from live sensors just because each has some local or routebook support.

## FH199. The updated public-anchor proxy can choose the next frontier file

- Failed hypothesis: after adding E176 and E216 to the public observation ledger, the known-anchor proxy should be good enough to pick the next post-E95 file by predicted LB or expected edge.
- Observed result: rerunning `analysis_outputs/public_anchor_bottleneck_decomposition.py` with 14 anchors keeps `raw05_a2c8_compat` as the best proxy, but its MAE is still `0.000496259` and p90 error is `0.000695363`. That is far larger than the gaps separating E95, E101, mixmin, and E176.
- Why discard: the proxy is useful for coarse geometry and known-bad JEPA-axis separation, but its resolution is too low for frontier ordering. Using it as a selector would turn public LB into post-hoc prior tweaking.
- Implementation issue possible: medium. More anchors or a better inverse subset model could reduce error later. Low for rejecting current use because the error floor is directly measured by leave-one-anchor validation.
- Bottleneck implication: candidate selection remains an observation-design problem, not a score-regression problem. The next submission should be chosen by which hidden-world belief it can kill: E224 for JEPA, E166 for independent broad-world, E154 for repaired branch.
- Do not repeat: ranking E224/E166/E154 by scalar proxy forecast, or creating a new blend because the proxy cannot separate them.

## FH200. E230 Q3-tail prune should replace E224 before any E224 feedback

- Failed hypothesis: because E230 improves E224's Q3 support-tail geometry, an E230 sibling should supersede E224 as the first JEPA-family public file.
- Observed result: E230 does improve the public-free tail audit, but only as an intervention on an already selected E224 movement. `q3_swingtop25_drop` reduces adverse capacity by `0.000633168` at a small expected-focus cost, and `q3_risktop21_drop` improves expected focus under the prior, but the prune criterion is not OOF-learned and is chosen from E224's own movement anatomy.
- Why discard: submitting E230 first would confound the main question. We would no longer know whether the capped-Q3/S4 JEPA translator works, only whether a hand-pruned Q3 tail variant happened to fit public.
- Implementation issue possible: medium. A future OOF-trained Q3 tail model could promote this from conditional repair to first-class translator. Low for rejecting current first-slot replacement because the current prune is deliberately an audit, not a learned gate.
- Bottleneck implication: E224 likely has a prunable Q3 tail, but the bottleneck remains public-tail translation and observation design.
- Do not repeat: using E230-style prunes as automatic pre-feedback replacements. First submit E224 if testing JEPA; use E230 only after E224 tie/small-loss attribution points to Q3 tail.

## FH201. A learned E224 Q3 support gate can promote E230 into a first-class translator

- Failed hypothesis: E230's hand-pruned Q3 tail can be learned from train/OOF support labels strongly enough to create a submission-safe gate.
- Observed result: E231 rebuilds E224-like Q3 OOF movement and trains small support models under stratified, row-contiguous, subject-kfold, and subject-LOO stress. Best AUC is only `0.588101`; OOF-helpful gates do not jointly pass subject stability and submission-side tail stress. No E231 submission file is selected.
- Why discard: the support boundary that improves OOF Q3 is not the same as the public-facing tail boundary. Current features can sort a little, but not enough to make a stable learned translator.
- Implementation issue possible: medium. The classifier family is intentionally small. But this was the right falsification for replacing E224 now: if even weak invariant signal existed, at least one small gate should have passed the strict joint stress.
- Bottleneck implication: E224's Q3 problem is not just "missing a small classifier." It is a target-tail translation problem where public-safe support is not currently identifiable from the available OOF row context.
- Do not repeat: submitting learned Q3 support-prune files before E224 public feedback. Use E231 only as a diagnostic unless a new JEPA target representation changes the support label geometry.

## FH202. A single shared S2/Q3/S4 support latent can drive the next JEPA gate

- Failed hypothesis: E216 S2, E224 Q3, and E224 S4 support-tail risks are expressions of one hidden row/block support state, so one shared JEPA support/energy gate should transfer across targets.
- Observed result: E232 shows almost no shared row support. Max support-label correlation is `0.057278`, max benefit correlation is `0.090611`, and subject support-rate correlations are mixed or negative. Test-side low-support overlap is also weak: Q3/S2 top25 overlap `1`, Q3/S4 top25 `2`, S2/S4 top25 `4`.
- Why discard: cross-target prediction survives mainly through movement-shape features, not through row identity or JEPA latent context. Best movement-only held-out transfer AUC is `0.745452`, while best latent-context transfer is `0.707003`, and overlap of the actual risky test rows is too small to justify a common gate.
- Implementation issue possible: medium. E232 uses the current E216/E224 translators, so a new JEPA objective could change support geometry. Low for rejecting a shared gate on the current tensors because the direct overlap and transfer diagnostics are consistent.
- Bottleneck implication: support-tail failure is target-specific. The 0.576x plateau is not fixed by one larger latent regularizer; it needs target-specific translation and calibration heads.
- Do not repeat: building one S2/Q3/S4 support-gated submission or claiming S4 support is a proxy for Q3/S2 support. Use target-specific heads and treat movement-shape support as an auxiliary calibration diagnostic.

## FH203. Softening the target-specific support gates is enough

- Failed hypothesis: E221/E231 failed partly because hard keep/drop gates are too discontinuous; using the same target-specific support probabilities as continuous amplitudes should preserve useful JEPA movement while reducing tail risk.
- Observed result: E233 finds `0` promoted soft policies. Best learned Q3 soft delta is `-0.002548953` versus full `-0.004262113`; best learned S2 is `-0.002769599` versus full `-0.004370425`; best learned S4 is `-0.002931629` versus full `-0.003430136`. For Q3, learned low-amplitude top25 rows overlap E230 risk-top21 by `0`.
- Why discard: the soft heads under-scale useful movement instead of isolating harmful rows, and they do not rediscover the independent Q3 public-free tail anatomy. This is not a threshold artifact.
- Implementation issue possible: medium. E233 uses simple probability-to-amplitude transforms and small models, but the negative is broad across all three target tasks and includes the independent E230 Q3 alignment check.
- Bottleneck implication: current support probabilities are diagnostics, not deployable amplitude heads. The JEPA bottleneck is in the target representation/loss, not just in the post-hoc gate function.
- Do not repeat: softened E221/E231 submissions or more scalar transforms of the same support probabilities. Build a new target-specific JEPA target before reopening this lane.

## FH204. E234 S2 tail-risk drops can be materialized as a public-safe E216 rescue

- Failed hypothesis: because E234's S2 high-impact tail target beats full E216 S2 OOF movement by as much as `-0.002653627`, applying those drops to the E216 S2 submission tensor should rescue the public-failed S2 lane.
- Observed result: E235 scans `240` S2 materialization rows across E234 promoted policies and scales `0.35`, `0.50`, and `0.75`. Submission gate pass is `0`, joint gate pass is `0`, and no submission file is materialized. Best expected-focus rows still have adverse capacity about `1.878x..4.068x` the observed E216 miss, and support remains below `0.5`.
- Why discard: the OOF tail-risk boundary and the public-facing S2 hard-label support boundary are not the same object under the current E216 translator.
- Implementation issue possible: medium. E235 intentionally tests only S2 and only the current E216/E95 materialization geometry. It does not kill E234 Q3/S4 or future cell-level tail targets. Low for rejecting immediate S2 submission because the exact post-E216 capacity gate has zero passes.
- Bottleneck implication: JEPA target/loss changes can find local structure, but S2 translation is still blocked by public subset/support mismatch. The bottleneck is not just representation learning; it is target-specific probability materialization.
- Do not repeat: smaller-scale E216 S2 siblings, E95-anchor S2 variants, or E234-S2-derived files unless a new target definition passes the same submission-side support/adverse stress.

## FH205. E234 Q3/S4 learned tail masks are a submission-safe replacement for E230

- Failed hypothesis: E234's locally promoted Q3/S4 tail-contrastive policies should learn the same public-facing Q3/S4 tail law that E230 hand-pruned from E224.
- Observed result: E236 scans `92` graft-side materializations and selects `0` files. Best Q3 masks reduce adverse capacity by `0.000329753`, but support drops by `-0.004017252` and Q3 top1/expected rises to `3.054720`. Best S4 masks can improve support by `0.006519636`, but lose `0.000166178` expected focus and leave Q3 risk unchanged.
- Why discard: the learned tail masks do not preserve the joint E224 geometry. Q3 learned drops are not aligned with public-free support; S4 learned drops are mostly healthy-body removal.
- Implementation issue possible: medium. E236 only tests the current E234 policy family on the current E224/E154 tensor. It does not kill future cell-level decisive-label targets or new JEPA objectives. Low for rejecting this exact submission branch because every public-free gate is zero.
- Bottleneck implication: E234 proves that changing JEPA targets can expose local tail structure, but target-specific public materialization is still the bottleneck. The Q3 public tail remains visible as an intervention energy, not as a learned invariant gate.
- Do not repeat: submitting E234-derived Q3/S4 learned-mask files, or replacing E230 with a learned Q3/S4 gate, unless a new target definition passes E224 expected-focus, support, adverse, and top-cell concentration stress.

## FH206. E237's local stress success proves learned-selector uniqueness

- Failed hypothesis: because E237 is OOF-trained and passes graft-vs-E154 plus actual-vs-E95 stress, the selected Q3 cells should be treated as a uniquely learned cell-level JEPA target rather than a residual-energy heuristic.
- Observed result: E240 tests deterministic rules from the E239 residual-energy motif. All `9/9` non-control simple selectors pass the same E237-like gate. `simple_pc10_top25` beats E237 control on expected loss vs E224 (`-0.000062119` vs `-0.000005612`), support gain (`0.016747154` vs `0.006450259`), actual adverse reduction (`0.000573879` vs `0.000553281`), and Q3 top1/expected (`0.485061` vs `0.747140`), while overlapping E237 only `14/25`.
- Why discard: the public-free gate is not discriminative enough to separate learned-cell representation from simple residual-energy sorting. E237 can still be a useful sensor, but its win would validate the broader residual-energy Q3-tail world, not the uniqueness of the learned classifier.
- Implementation issue possible: medium. E240 rules are post-hoc test-side diagnostics and should not replace E237 without train/OOF validation. Low for rejecting the uniqueness claim because the same local gates directly pass for many simple rules.
- Bottleneck implication: the next bottleneck is not "train a sharper E237 sibling"; it is proving whether residual PC10-like Q3 cells are supported by train/OOF benefit and public-like stress.
- Do not repeat: claiming E237 is a JEPA breakthrough solely because it passes E237/E230 stress, or submitting lower-ranked E237 siblings before separating learned target value from residual-energy heuristic value.

## FH207. E240 simple residual-energy rules are OOF-valid Q3 rollback candidates

- Failed hypothesis: because E240 residual-energy rules pass E237/E230 public-free stress, residual PC10 or related scores should identify train OOF rows where E224-like Q3 movement is harmful and could become a simple submission rule.
- Observed result: E241 finds no full-train top-k score with negative selected-benefit delta. `score_pc10` top-10% has drop delta `+0.001867628`; split-stress top-10% mean is `+0.002633171` with win rate `0.30`. The best split-stress score, `score_nn_dist`, is still non-negative at `+0.000270542` and win rate `0.50`.
- Why discard: the rule is a test-side motif that overlaps E237/E230 cells, not an invariant harmful-row selector under current OOF labels.
- Implementation issue possible: medium. The OOF target is E224-like Q3 benefit and may not perfectly match hidden public cells. Low for rejecting immediate submission because every direct validation metric is adverse or non-negative.
- Bottleneck implication: the Q3 residual-energy motif is not enough. The plateau remains a translation problem: visible latent energy can mark interesting cells, but probability movement needs OOF cell-target supervision or public-feedback routing.
- Do not repeat: materializing `simple_pc10_top25`, `top50_amp_then_resid_combo25`, or similar residual-energy top-k rules without a new OOF target or public contrast.

## FH208. E237 siblings should be ranked by average OOF gain

- Failed hypothesis: because E237 is learned from OOF decisive-cell labels, candidates with stronger average OOF loss improvement should be the best E237 submission siblings.
- Observed result: E242 audits `120` graft-side materialization rows. The top E237 file ranks only `71/120` by OOF gain; OOF gain has gate AUC `0.426043` and Spearman `0.108953` with E237 score. By contrast, OOF tail-AUC has gate AUC `0.958913`, and the top E237 file ranks `1/120` by OOF tail-AUC.
- Why discard: average OOF gain mixes useful high-impact tail discrimination with broad body/support tradeoffs that do not transfer to the public-free materialization gate.
- Implementation issue possible: low for the ranking claim because it is a direct audit over all existing E237 materialization rows. Medium for public truth because the real hidden labels are unknown.
- Bottleneck implication: the live E237 object is high-impact Q3 tail identity, not generic OOF-CV improvement. This helps explain why many high-OOF policies fail support/top-cell stress.
- Do not repeat: submitting E237 siblings because they improve OOF more than the locked top file, or calling E237 a broad learned translator.

## FH209. E237 should universally replace E224 as the next JEPA file

- Failed hypothesis: because E237 improves E224's Q3 tail geometry and is the closest learned JEPA cell-tail translator, it should supersede E224 for every JEPA-related public slot.
- Observed result: E243 separates the question roles. E237 is ranked first for an improvement-biased JEPA-tail public test, but E224 remains first for the clean unpruned capped-Q3/S4 JEPA body test. E237 changes only `25` Q3 cells, so a public result from E237 would confound body validity with Q3 pre-pruning unless interpreted through E238 and ideally contrasted with E224.
- Why discard: universal replacement would destroy feedback identifiability. If E237 wins, we would not know whether the clean E224 body also works; if it loses, we would not know whether the pre-pruned Q3 tail or the E224 body failed.
- Implementation issue possible: low. This is a deterministic decision-geometry issue, not a stochastic training result.
- Bottleneck implication: the bottleneck is still public-tail translation plus observation design. The next file must be chosen by the question: E237 for JEPA-as-solution, E224 for clean JEPA ablation, E166 for non-JEPA escape.
- Do not repeat: saying "submit E237" without specifying that it is a learned Q3-tail bet, or demoting E224 without acknowledging that E224 answers a different clean-body question.

## FH210. Feature-NN1 smoothing is an OOF-certified harmful-Q3-row selector

- Failed hypothesis: because E246/E247 directly reduce Q3 roughness on the E207 feature-NN1 manifold, high smoothing-gain rows should also be train/OOF rows where E224-like Q3 movement is harmful and rollback improves LogLoss.
- Observed result: E248 shows the opposite for the E247 analogue. At the `34/250 = 0.136` selection fraction, train-only PCA `score_trainpca_smooth_sum` has rollback delta `+0.002829987`, all-PCA `score_allpca_smooth_sum` has `+0.002922728`, and split-stress means are positive (`+0.002638697` and `+0.002950123`). The best full-train score is the negative-control smoothness direction, and even that is non-negative at `+0.000489209`.
- Why discard: the smoothing rule is a real geometric intervention, but not an invariant label-support selector under current OOF Q3 benefit. It tends to remove helpful movement rather than isolate harmful movement.
- Implementation issue possible: medium. OOF `q3_e224` benefit may not equal hidden public labels, and train-only neighbor geometry is not exactly the test feature-NN1 graph. Low for downgrading E247 as an expected-score candidate because the exact missing claim was OOF invariance.
- Bottleneck implication: the plateau is not solved by making predictions smoother on a plausible JEPA manifold. The hard part is still target-specific probability materialization: which cells should move, not whether a manifold exists.
- Do not repeat: creating E247 sibling sweeps or smoothness-threshold variants before public feedback or before training a true OOF feature-NN1 decisive-cell target.

## FH211. E249 top OOF feature-NN1 policy is submission-safe because average OOF gain is large

- Failed hypothesis: E249's best feature-NN1 OOF row, `drop_q3_top50`, should be safe to materialize because its loss_vs_full is very strong at `-0.000706695`.
- Observed result: E250 materialization rejects that family. The top50/broad contrast rows keep attractive OOF loss but fail the E237 gate because support gain turns negative and Q3 top1/abs-expected is high. The selected rows are narrower risk-target policies, led by `drop_q3_top21` with OOF loss_vs_full only `-0.000185023` but tail-AUC `0.887357` and positive support/adverse stress.
- Why discard: average OOF gain is again the wrong selection variable. The public-facing object is high-impact Q3 tail identity plus materialized support geometry, not broad loss improvement.
- Implementation issue possible: low for rejecting the top50 submission claim, because the same materialization code selects four narrower rows while rejecting the broad top50 row. Medium for public truth because hidden labels are unknown.
- Bottleneck implication: this reinforces the E242 lesson. JEPA context can help, but only when the target and gate are tail-specific. Broad OOF-winning policies are likely calibration/support traps.
- Do not repeat: submitting E249 `drop_q3_top50`, broad global top-k policies, or E250 siblings ranked by OOF loss before public feedback.

## FH212. E237/E250 shared consensus cells are the safest standalone Q3 law

- Failed hypothesis: if two JEPA context views agree on `15` Q3 rollback cells, that intersection should be the safest high-confidence tail set.
- Observed result: E251 shows the shared intersection fails materialization: expected loss vs E224 is positive at `+0.000028815`, and Q3 top1/abs-expected is `1.054975`. The best anatomy is the union, not the consensus core.
- Why discard: agreement creates concentration, not safety. The useful public-free signal is distributed across parent-specific cells.
- Implementation issue possible: low for rejecting intersection-only materialization; medium for public truth because the union still lacks OOF provenance.
- Bottleneck implication: multi-view JEPA health is not simple consensus voting. The next representation should model complementary cell sets, not only cells selected by multiple views.
- Do not repeat: materializing intersection-only E237/E250 files or using overlap count as a hard confidence score.

## FH213. E250-only cells are independently deployable

- Failed hypothesis: feature-NN1 context's `6` cells outside E237 should be enough to create an independent E250-only public-safe correction.
- Observed result: E251 E250-only has favorable expected movement (`-0.000029661`) and support gain (`0.003048691`) but fails the materialization gate because adverse reduction is only `0.000144605` and actual adverse reduction `0.000134756`, both below the gate.
- Why discard: E250-only cells are useful as complements to E237-only cells, not as an independent public-safe branch.
- Implementation issue possible: low for this exact cell set; the gate miss is small but deterministic.
- Bottleneck implication: feature-NN1 context currently adds marginal tail cells that need a learned-cell backbone. It is not yet a standalone selector.
- Do not repeat: submitting E250-only or promoting feature-NN1-only differences without the E237 backbone.

## FH214. E252 union is OOF-certified as better than both parents

- Failed hypothesis: because E251's E237/E250 union has the best submission-side materialization anatomy, the same union should beat both parent policies on train OOF.
- Observed result: E253 shows union loss_vs_full `-0.000080010`, worse than E237 parent `-0.000271441` and E250 parent `-0.000185023`. The union remains stress-promoted, but parent-specific cells are OOF-adverse and dilute the shared signal.
- Why discard: materialization support/adverse geometry and train OOF benefit are not aligned for these Q3 cells. E252 cannot be called OOF-certified.
- Implementation issue possible: medium. The union is reconstructed from two different OOF split regimes (`subject5` and `row5`), which is exactly the point of the stress. Low for rejecting the "better than both parents" claim because parent and union metrics are in the same script.
- Bottleneck implication: candidate ranking is constrained by validation mismatch, not lack of Q3 tail candidates. A public E252 result would be a sensor for which geometry public follows.
- Do not repeat: promoting E252 as likely-score first without public feedback, or unioning parent-specific cells from two views and treating materialization score as validation.

## FH215. OOF consensus implies submission-side public safety

- Failed hypothesis: cells selected by both E237 and E250 should be safest because they are consensus across two context views.
- Observed result: E253 says the OOF shared intersection is strongest with loss_vs_full `-0.000376454`, but E251 says the corresponding materialized shared intersection fails with expected loss `+0.000028815` and Q3 top1/abs-expected `1.054975`.
- Why discard: consensus is OOF-good but public-free materialization-bad. It is not a safe public law under current stress.
- Implementation issue possible: medium because train and test row sets differ, but the conflict is the core discovery rather than an error.
- Bottleneck implication: the hidden public subset likely weights a different Q3 hard-label tail than random/subject OOF. This strengthens validation mismatch and public-tail translation as the current bottleneck.
- Do not repeat: using overlap/intersection as a confidence gate without materialization stress.

## FH216. The E237/E250 conflict is only a set arithmetic artifact

- Failed hypothesis: the E253 contradiction can be resolved by choosing the right set operation, such as intersection for OOF or union for materialization, without changing the representation target.
- Observed result: E254 shows the conflict has visible geometry. Selected groups shift strongly from train to test in `prob_gap` and `logit_step`; feature-NN1 smooth-gain also flips sign for shared and E250-only cells. Train shared cells have benefit mean `-0.028234084`, while test shared cells have favorable expected focus but extreme concentration (`top1/abs=3.412733926`). Union is OOF-diluted but changes the test hard-tail anatomy.
- Why discard: the issue is not only which rows are selected. The selected rows live in different train/test regimes, so union/intersection cannot be certified by set logic alone.
- Implementation issue possible: medium. The atlas compares OOF benefit and public-free priors, not hidden public labels. Low for rejecting simple set arithmetic because the feature shifts are directly observable.
- Bottleneck implication: the plateau is a validation-geometry transfer problem. A useful next model must learn a contrastive representation of tail regime, not just reweight E237/E250 cells.
- Do not repeat: creating new E237/E250 set-operation files before training or auditing a contrastive head that explains the train/test geometry shift.

## FH217. E248 OOF smoothing rejection should veto E247

- Failed hypothesis: because E247's train OOF analogue is adverse under E248, E247 should be ranked below OOF-certified learned Q3-tail candidates for expected public score.
- Observed result: E247 public LB is `0.5761589494`, beating E95 by `0.0001323804` and mixmin by `0.0001476911`.
- Why discard: the exact reason E248 was useful is now inverted. It did not prove smoothing was false; it proved the ordinary OOF smoothing target is not the public invariant. Public follows the test-side feature-neighbor geometry in this branch.
- Implementation issue possible: low for rejecting the veto, because public LB directly contradicts it. Medium for attributing the gain solely to smoothing because E224 body is still unobserved.
- Bottleneck implication: validation mismatch is now stronger than model-capacity bottleneck for the live JEPA branch. The next representation should be public-contrastive, not another average OOF benefit head.
- Do not repeat: using adverse OOF smoothing analogues as a hard pre-public veto for E247-family candidates. Use them as mismatch diagnostics and require controlled public sensors like E256.

## FH218. E247 public win proves standalone feature-NN1 smoothing

- Failed hypothesis: because E247 won public, the feature-NN1 smoothing rollback itself can be treated as an independent replacement law and freely tuned/blended.
- Observed result: E258 shows E247 rollback is an opposite-sign trim of the E224 body, not an independent same-sign movement. On selected cells, rollback-vs-body cosine is `-0.992683110`, opposite-sign share is `1.000000`, and rollback abs over selected body abs is `0.984581403`. E247 total movement keeps the E224 body and improves Q3 tail concentration.
- Why discard: E247 public LB validates the composition of E224 body plus Q3 feature-NN1 rollback. It does not tell us whether E224 alone, E247 rollback, or their interaction carried the public gain.
- Implementation issue possible: low for the decomposition; it is deterministic logit arithmetic over the submitted tensors. Medium for public attribution because E224 is still unobserved.
- Bottleneck implication: the immediate bottleneck is attribution and controlled observation, not another threshold sweep. The next useful public files are E256 for rollback refinement or E224 for body attribution.
- Do not repeat: treating E247 siblings, E247/E256 blends, or arbitrary smoothing threshold variants as justified before E256/E224 feedback.

## FH219. A post-E247 scalar score can be interpreted without a routebook

- Failed hypothesis: after E247, the next E247-family public score can be interpreted by scalar rank alone.
- Observed result: E257 and E258 show the family is underidentified. E256 and E224 ask different questions, and the same delta size has different meaning depending on which file produced it.
- Why discard: scalar rank cannot distinguish body sufficiency, rollback necessity, broad smoothness, amplitude smoothing, or exact top34 interaction. E259 pre-registers separate score bands and actions for E256 and E224.
- Implementation issue possible: low for the governance conclusion; the ambiguity is structural. Medium for exact thresholds because they are pragmatic public-resolution bands, not hidden labels.
- Bottleneck implication: the bottleneck is no longer only candidate generation. It is feedback identifiability. A public slot should kill a branch, not just produce another number.
- Do not repeat: interpreting E256/E224/E247-family scores post-hoc, or creating a blend before one clean axis has public feedback.

## FH220. E256's main risk is deleting E247-only broad smoothness

- Failed hypothesis: if E256 loses to E247, the natural first explanation should be that the `13` E247-only low-amplitude broad-smoothness cells were public-real and should be restored.
- Observed result: E260 separates E256-vs-E247 by E257 cell group. The `13` E247-only deletion cells are slightly favorable under the focus prior (`-0.000001767`), while the `4` E256-only high-amplitude additions are adverse (`+0.000020868`). Total E256-vs-E247 expected focus is `+0.000019101`.
- Why discard: the candidate-level E256 penalty is driven by the added high-amplitude cells, not by the removed broad cells. A scalar E256 loss would be underidentified without this decomposition.
- Implementation issue possible: medium. The decomposition uses current hard-label priors, not hidden public labels. Low for rejecting the prior-based explanation, because group attribution is deterministic over the submitted tensors.
- Bottleneck implication: the next bottleneck is cell-level public label resolution, not broad-vs-amplitude story alone. The public may still reward broad smoothness, but E260 says that is not the current public-free risk explanation.
- Do not repeat: making an E247/E256 blend or E247-only restoration variant immediately after an E256 loss without first isolating the four E256-only cells.

## FH221. High-amplitude constrained smoothing beats broad top34 smoothing

- Failed hypothesis: E256's amplitude-constrained top25 smoothing should beat E247's broad top34 smoothing because it keeps the shared E247 core and swaps low-amplitude broad cells for high-amplitude/E230-aligned cells.
- Observed result: E256 public LB is `0.5762805676`, worse than E247 by `+0.0001216182`. E259 decodes this as `same_family_loss`.
- Why discard: public directly rejects E256 as the next score route. It remains above E95, so the failure is not feature-NN1 smoothing collapse; it is the specific high-amplitude refinement losing the E247 edge.
- Implementation issue possible: low for the public score interpretation. Medium for exact cell causality because E256 simultaneously removes `13` E247-only cells and adds `4` high-amplitude cells.
- Bottleneck implication: the live bottleneck is not "find a sharper threshold inside E246." It is attribution/non-collinearity: E247 exact top34, E224 body interaction, or a different hidden-world branch.
- Do not repeat: submitting more E246/E256 scalar-threshold siblings or blending E247/E256 before an attribution/non-collinear observation.

## FH222. E264 strict lifestyle gate certifies a submission

- Failed hypothesis: if human/social lifestyle features produce many strict OOF gates under subject/date-block stress, a broad lifestyle-conditioned rollback can be treated as submission-ready.
- Observed result: E264 did produce strong gates, but E265 random cell noise also passed strict gates at rate `0.290909` and reached loss_vs_full `-0.000723735`. The best human_late row is stronger at `-0.001689622`, but the gate itself is too easy.
- Why discard: policy-level broad rollback improvement is not a sufficiently sharp latent health criterion. It can be triggered by random cell ordering often enough that it cannot certify public-facing Q3/S4 tail geometry.
- Implementation issue possible: low for rejecting the broad gate; E265 uses the same policy machinery. Medium for the exact random rate because only `5` seeds and representative policies were used for speed, but the failure is large enough to block immediate submission.
- Bottleneck implication: the human/social representation is alive, but the missing object is sharper target translation: cell-tail ranking, top-cell overlap, and materialization-side support/adverse stress.
- Do not repeat: broad `drop_global_pXX` lifestyle rollback submissions without E224/E154 materialization stress and random-control margin.

## FH223. E266 highest E237 score is automatically the first lifestyle submission

- Failed hypothesis: once E266 selected files, the highest E237-score row should be the next public file.
- Observed result: the top E237-score `c1e018aa` has strong adverse/support numbers, but it drops `75` Q3/S4 cells and has positive expected_loss_vs_e224 `+0.000010956`. E267's survival routebook penalizes exactly this broad expected-positive pattern and ranks balanced `2936100f` first.
- Why discard: E265 already showed broad gates can look good too easily. A top-score row that wins mainly by support/adverse mass but increases expected loss and broadness is not the clean first public sensor.
- Implementation issue possible: low for the ranking decision; all metrics come from the same E266 materialization table. Medium for true public outcome because hidden labels may still reward the broad support sensor.
- Bottleneck implication: candidate selection is now part of the bottleneck. The branch can produce files, but picking by one scalar stress score can reintroduce the broad-gate failure.
- Do not repeat: submitting the broadest/highest-support lifestyle tensor before the balanced routebook candidate has public feedback.
