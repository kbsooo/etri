# Public LB Observation Log

작성일: 2026-05-30

Public LB는 최적화 target이 아니라 hidden public subset과 calibration sensitivity를 관측하는 sensor로 취급한다.

현재 public best는 `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` = `0.5681234831`다. 아래 초기 표의 delta는 기존 E95 frontier anchor 기준이며, H012 이후 관측은 별도 섹션에 기록한다.

## Public-Free Post-H012 Observation

H034 is a public-free row-route observation. It tests whether the failed H032
siblings become actionable when the atomic unit is a row's full 7-target route
instead of an independent cell.

- Route training rows: `4262`.
- Best route model: `et_route`, all-OOF MAE `0.000388962`, Spearman
  `0.985479984`, pairwise `0.956022161`.
- Generated row-route actions: `349`.
- Selected diagnostic: `row_rollback_support_rollback_memory_conflict_changed_r1_a0.08`.
- H024 pre-state margin vs H012: `-0.003998719`.
- H034 route mean margin prediction: `+0.032224275`.
- Public-score permutation p(lower margin): `0.305333333`.
- H025 row-permutation p(higher top1200 gain): `0.940000000`.

Signal: route-level sibling failure is highly learnable, but H024 can
over-encourage a tiny single-row rollback that route/action-health stress
rejects. Unresolved: a nonlinear H012-vs-sibling classifier or combinatorial
solver may still recover an action, but direct row-route top-k editing should
not be submitted.

H033 is also not a public LB observation. It follows H032 by using the failed
phase siblings as contrastive supervision for a phase-lock decoder.

- Contrastive siblings: `4262`.
- Best all-OOF alpha: `100.0`, MAE `0.000814682`, Spearman `0.954416119`,
  pairwise `0.912785497`.
- Generated negative-cost actions: `83`.
- Selected diagnostic: `negative_add_add_k10_a0.1`.
- Selected pre-state margin versus H012 prediction: `+0.016275125`.
- Public-score permutation p(lower margin): `0.861333333`.
- H025 row-permutation p(higher top1200 gain): `0.710000000`.

Signal: H012's neighborhood has a learnable phase-lock structure. Unresolved:
the first-order independent-cell translation of that structure is action-bad,
so a future public candidate must use a nonlinear row-vector or route-level
translator rather than H033 cell coefficients directly.

H032 is not a submitted public LB observation, but it is the strongest
public-free sensor after H012. It withheld H012's public score from the decoder,
then ranked the real H012 anchor against `4263` generated phase siblings.

- Selected point: real `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`.
- Best pre-H012 decoder: `geometry` alpha `10.0`, LOO MAE `0.000295413`,
  Spearman `0.950877193`, pairwise `0.923976608`.
- Best non-anchor sibling: `identity_phase_score_all_k120_a0.7_uniform`,
  predicted `+0.009811799` worse than H012 by pre-state score.

Signal: H012 is not just an LB-fitted artifact; it is visible from pre-H012
state/action geometry. Unresolved: that geometry recovers H012 but does not yet
produce a better post-H012 action.

## Known Observations

| submission | public LB | delta vs E95 anchor | changed point | expected reaction | observed signal | unresolved |
|---|---:|---:|---|---|---|---|
| `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` | 0.5761589494 | -0.0001323804 | E247 feature-NN1 Q3 smoothing rollback: E224에서 Q3 `34` cells만 E154 방향으로 되돌림 | if E207/E246 feature-neighbor Q3 smoothing is public-real, should beat E95 despite E248 OOF-adverse analogue | new frontier. Beats E95 by `0.0001323804`, mixmin by `0.0001476911`, and the E95-over-mixmin edge by `8.646x`; validates test-side feature-neighbor public-tail geometry as action-grade | attribution between E224 body and E247 rollback is unresolved; next high-information family sensor is E256 `top50_amp_then_smooth25` |
| `submission_e95_hardtail_541e3973.csv` | 0.5762913298 | 0.0000000000 | E86 with E85 fallback on E72-adverse top-tail cells | if hard-tail localization is real, should improve over mixmin despite retaining E86 structure | new frontier. Beats mixmin by `0.0000153107` and recovers the E72 miss plus an extra `15.14%` of that miss scale | whether more E86 structure is safe; whether E85 conservative floor would beat E95 |
| `submission_e101_q2s3tail_177569bc.csv` | 0.5763003660 | +0.0000090362 | E95-relative rollback on `50` Q2/S3 active cells toward mixmin | if E95 over-amplified the Q2/S3/S3-heavy hard tail, should beat E95 or at least land in E116 win/tie bands | E116 `small_loss`: worse than E95 but still beats mixmin by `0.0000062745`. Gives back `59.02%` of E95's mixmin gain and preserves `40.98%`; E126 later shows E101-compatible scenario budget is only `1.1234%` E101-active | true public labels remain hidden; same-line Q2/S3 followups are closed unless a new independent sensor appears |
| `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` | 0.5772865088 | +0.0009951790 | E216 masked-family JEPA `s2_rank` graft on E154 at scale `0.75`; public observed `2026-05-30 16:14:15` | if E215's S2-only masked-family latent is public-safe, should hold near E95 or improve as a non-collinear S2 sensor | severe public miss. Worse than E95 by `0.0009951790`, mixmin by `0.0009798683`, E101 by `0.0009861428`, and E176 by `0.0009746778`; rejects E216 S2-only as public-safe | whether smaller scale or E95-anchor would lose less; remaining E216 siblings are demoted until the S2 tail failure is explained |
| `submission_mixmin_0c916bb4.csv` | 0.5763066405 | +0.0000153107 | high-risk mixmin public sensor selected from anchor-loss/binary-world evidence | if anchor-loss worldview is real, should beat a2c8 despite pair/old selector veto | previous frontier. Beats a2c8 by `0.0011326805`; validates mixmin as public-relevant, not merely diagnostic | private split safety; which targets/rows caused the large gain |
| `submission_e72_topabs50_q2s3_gate_4e48cba2.csv` | 0.5764077772 | +0.0001164474 | E72/E73 sparse-magnitude Q2/S3 gate candidate | if H69 sparse Q2/S3 consensus is public-real, should improve over mixmin or at least hold near-flat | worsened vs mixmin by `0.0001011367`. Public response reversed the local all-combo edge by `9.590x`; movement audit shows the submitted file moved `893` cells across all `7` targets, so this rejects the combined E72 base plus sparse-gate file rather than isolated Q2/S3 alone | whether pure mixmin-anchored Q2/S3 movement has any public value; whether broad non-Q2/S3 base movement caused most of the failure |
| `submission_frontier_cvjepa_refine_a2c8d2c8.csv` | 0.5774393210 | +0.0011479912 | previous frontier, raw05-compatible refined candidate | raw05보다 아주 작게 개선 | no longer best. Still important raw05-compatible anchor | why mixmin escapes the previous selector veto |
| `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv` | 0.5775263072 | +0.0012349774 | raw timeline JEPA rescue, strict scale 0.5 | raw05-like raw temporal signal 확인 | strong positive anchor, but mixmin/E95 are much better | raw05 manifold is insufficient by itself |
| `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` | 0.5779449757 | +0.0016536459 | strong local stage2 hybrid | local CV strength가 public에 일부 transfer | public에서는 mixmin/raw05/a2c8보다 약함 | CV-public mismatch magnitude |
| `submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` | 0.5783033652 | +0.0020120354 | ordinal Q constraints, nearest blend | Q count/order constraint가 도움 기대 | public 악화. hard ordinal/count correction 위험 | 일부 target에서만 유효했을 가능성 |
| `submission_hybrid_0p578_logit_after_subject_final9_strict.csv` | 0.5784273528 | +0.0021360230 | subject/logit after-correction | subject prior/logit correction 도움 기대 | broad correction은 frontier를 못 이김 | targetwise correction source |
| `submission_jepa_latent_q2_w0p45.csv` | 0.5798012862 | +0.0035099564 | Q2 JEPA latent direct move | Q2 latent correction 개선 기대 | bad public anchor. Q2 direct JEPA 위험 | Q2만 나쁜지 collateral인지 |
| `submission_lejepa_targetwise_strict_best_scale0p5.csv` | 0.5802468192 | +0.0039554894 | LeJEPA targetwise strict blend | geometry regularization이 public safety 개선 기대 | public 악화. LeJEPA 이름만으로 safety 없음 | latent geometry 어떤 축이 실패했는지 |
| `submission_jepa_latent_residual_probe.csv` | 0.5812273278 | +0.0049359980 | all-target latent residual probe | local OOF gain transfer 기대 | major bad anchor. local CV gain이 public shortcut일 수 있음 | bad-axis decomposition 필요 |

## Sensor Interpretation

1. `mixmin`이 previous best a2c8를 `0.0011326805` 이겼다. 이 edge는 raw05-a2c8 gap `0.0000869862`의 약 `13.02x`라서 noise-scale micro-edge가 아니다.
2. Pairwise/old selector veto를 hard gate로 사용하면 좋은 후보를 버린다는 강한 반례가 생겼다. E32-E38의 anchor-loss/binary-world sensor ranking은 public-relevant였고, E35의 "normal gate 0"은 너무 보수적이었다.
3. raw05가 강한 것은 여전히 public-positive raw timeline/measurement-process 신호지만, raw05 manifold 근처만 고집하는 전략은 부족하다. Mixmin처럼 anchor-loss/cancellation geometry가 맞으면 큰 이동도 public에서 살아남을 수 있다.
4. JEPA direct moves는 여전히 bad anchors가 많다. 이번 관측이 의미하는 것은 "모든 큰 latent move가 좋다"가 아니라, anchor-loss/binary-world geometry로 필터링된 특정 큰 이동이 public subset과 맞았다는 것이다.
5. E95 improves on mixmin by only `0.0000153107`, so the hard-tail gate is public-real but not a structural breakthrough to 0.54. It says the E72-adverse hard-label tail can be localized, not that the hidden block-rate state has been recovered.
6. public observations remain underidentified, but the mixmin and E95 anchors sharply update which hidden-world families deserve weight. Next work should recalibrate selectors around E95-as-frontier instead of continuing a2c8-centered micro-edge certification.
7. E101 resolves the pending Q2/S3 rollback question negatively against E95: public `0.5763003660` is `+0.0000090362` worse than E95, yet still `-0.0000062745` better than mixmin. The clean read is not "E101 was nonsense"; it is "E95's target-axis hard-tail surgery was right enough that the smaller Q2/S3 rollback cannot replace it." E108, E104 higher-alpha, E106 subject-prior masks, and E119 flank-gated variants are closed as automatic followups.
8. E124 adds a held-out model check: the E99 transfer world that explained E72/E95 predicted E101 too optimistically. Broad-plausible mean E101 delta was `-0.000031516` versus actual `-0.000006275`, and only `57/3452` broad worlds matched the E101 ordering. Public LB is saying the hard-tail axis is real, but the Q2/S3 boundary variable is missing.
9. E125 adds survivor anatomy: those `57` worlds are not q2s3 diffuse-tail worlds. `q2s3` has `0/368` survivors; `all`/`e72_top50_hard` have `43/57`; median alpha collapses from `3.310470` to `0.791985`; and E101 loses its tail advantage over E95. Public LB is pointing toward transfer shrinkage/tail allocation outside the active Q2/S3 line.
10. E144 was the first post-E101 transfer-branch sensor before the later E154 repair. It tightens the post-E101 transfer branch by finding a fine active/Q2S3 boundary row that beats E143 locally while preserving all E143 gates. Public feedback on E144 should be read as a test of boundary fineness, not as generic model quality.
11. E148 adds the pre-public responsibility decoder for E144. Global/subject/nearest-hard simulated win-rate masses are `0.745560` / `0.599760` / `0.635616`, but branch-or-worse masses are `0.204972` / `0.333832` / `0.284852`. A future E144 fine loss is not automatically a fine-tail failure; it may be inherited-body/Q3/S2, S3/Q3, or inherited-body/Q3/S3 depending on which prior geometry best matches the public observation.
12. E149 adds the anchor-geometry decoder for E144. E144 is almost orthogonal to E101/E72 public-negative axes (`-0.019625796` / `-0.024358970`) but highly aligned with E143/E142 branch axes (`0.991918719` / `0.952146833`). This keeps E144 as the conservative unrepaired contrast while lowering the interpretation from broad breakthrough to branch-pruned residual test.
13. E150 supersedes E145's loose post-loss action rule. After E144 public feedback, use `analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>`; fine-loss is only `conditional_alive`, and E143 is not automatic unless attribution points to fine-tail/S3 retention.
14. E151 turns the E95/E101/E144 observations into a plateau diagnosis: selector resolution is far coarser than frontier-scale edges, old-candidate search has no novel strict successor, and direct decoder families keep failing submit gates. This kept E144 alive while shifting local work away from old-file ranking and toward a non-collinear transfer-budget decoder.
15. E152 tests that non-collinear escape hatch and finds the stricter problem: non-collinear signal exists, but relaxed structural reward, E72 budget, post-E101 safety, and active-veto actionability have zero all-four intersection. This kept E144 as the standing conservative sensor and turned the next local target into gate-intersection diagnosis.
16. E154 updates the pending public-sensor order locally, not from public LB. E153's S3 active-boundary blocker is repairable: `10` all-four rows open after selected S3 rollback, and `submission_e154_s3repair_9f2e2e73.csv` beats E144 locally while remaining E144-collinear and E72/E101-negative-axis safe. Public LB should now be used to test whether that repaired all-four intersection is real.
17. E156 updates the repaired-branch control stack locally. E155's diagonal `25%` body is not the minimum coherent repair: `85` target-axis lattice rows sit below that body ratio while keeping all-four health. The selected `submission_e156_targetaxis_757546d2.csv` is nearly pure E144/E155 geometry with a tiny Q1/S2/S4 add-on, so it is a decomposition control rather than a first public sensor.
18. E157 warns against overreading E156's target-axis choice. The lattice is fully all-four, Q3 is the strongest local/post-E101 finite-difference axis, and three low-body rows including Q3 dominate E155 on local/post-E101/E72 stress. `submission_e157_lowbodypareto_bd67930d.csv` is therefore a tuned low-body Pareto control, not proof of a new target law.
19. E158 pre-registers the repaired-branch public decoder. E154 is not first because it is public-readably better than E155; E154-minus-E155 local gap is only `-0.000001795559`, below the `2e-6` guardrail. It is first because E154-minus-E144 is `-0.000002432120`, readable against the unrepaired branch and asks the full repaired all-four question. E155 is the amplitude-control after E154 feedback; E157/E156 are post-E155 target-axis controls.
20. E159 adds the missing attribution layer for E154. The exact additive decomposition has `479` segments over `294` unique moved cells and verifies direct E154-vs-E95 hard-label deltas to `<2e-16`. Public-free win mass remains high enough to justify E154 as the next sensor, but loss-side blame is dominated by inherited E144 body rather than E154's added body. Therefore E155 is a follow-up only when E154 feedback specifically implicates added-body overextension, not when the inherited branch fails.
21. E160 combines E158 and E159 into an executable post-feedback interpreter. After E154 public feedback, run `analysis_outputs/e160_e154_postfeedback_interpreter.py --score <PUBLIC_LB>`. The pre-feedback table marks E155 as `information_only` for tie/small_loss and `not_recommended` for branch_loss/hard_fail, while E157/E156 remain blocked before E155.
22. E164-E166 reopen the broad-latent branch that E163 demanded. E164 found `192` broad candidate-gate rows in the tracked submission universe, E165 rejected known public-bad broad controls while leaving `90` geometry-health survivors, and E166 materialized `submission_e166_broadsurv_s0p01_d8bfa94b.csv` as a `1%` E95-to-survivor logit step. This file has focus expected delta `-0.000332077`, cells-to-flip `74`, top1/expected `0.023369627`, mean/max abs logit move `0.002243986` / `0.013580886`, and no scaled known-bad control passes the same gate. It is the current broad-escape sensor, distinct from the narrow repaired E154 branch.
23. E167 says how to read any future E166 public score. The E166 focus cells are hidden-context-real, not target-count-random: edge-like rate is `0.689189` vs null `0.470842`, and between-train-runs is `0.797297` vs `0.624658`. But they are safety-atlas-divergent: all-veto-null is `0.297297` vs `0.574158`, safe-density `0.117097` vs `0.243966`, E101-plausible mass `0.238204` vs `0.533727`, and E72-active `0.837838` vs `0.670369`. Therefore an E166 win means the safety atlas was too conservative/branch-bound; an E166 loss means the E72-active/low-veto-null conflict is likely the missing public-negative axis.
24. E216 public feedback is a hard negative for the masked-family JEPA S2-only translator. The E215 latent can still be real, but `s2_rank` on E154 at `0.75` is not public-safe. This is not a frontier-scale tie: the miss is almost `0.001` worse than E95, so the local/geometry/frontier stress stack produced a false positive for S2. Remaining E216 siblings should be treated as negative controls, not automatic next submissions.
25. E219 explains the E216 miss as S2-tail fragility rather than E154-anchor bad luck. E154 body alone has adverse capacity `0.000924070`, below the observed E216-vs-E95 miss `0.0009951790`, while the pure S2 graft has adverse capacity `0.006048995`. Near-observed simulated worlds attribute about `0.000920169` to S2 graft and near-zero to E154 body. The missing gate signal is support probability: S2 graft focus support is only `0.473945` despite a slightly negative expected delta.
26. E220 tries the obvious repair and rejects it. Simple S2 support/tail thresholds cannot keep both negative expected movement and bounded adverse capacity. `focus_support_ge_0p7` is support-safe but expected-adverse (`+0.000018940`), while `focus_support_ge_0p6_expected_neg` is expected-helpful (`-0.000578857`) but still has adverse capacity `0.001402108`, above the E216 observed miss. This closes simple E216 threshold variants as public candidates.
27. E221 tries the trainable version of the same repair and also rejects it. S2 support is locally learnable (`AUC=0.748104` stratified, `0.713730` subject-LOO), but OOF-good gates and public-tail-safe test gates do not coincide. This updates the public interpretation of E216: the miss is not just a missing scalar threshold; it is a train/test-public support mismatch in the current masked-family S2 translator.
28. E226 converts the E216 miss plus E224 collinearity into a candidate-order sensor. Existing materialized files were scanned for non-collinearity to E224 and distance from known public-negative axes. The best existing independent counter-world is `submission_e166_broadsurv_s0p01_d8bfa94b.csv`, not an E209/E210/E211/E223 sibling. E154 remains the conservative repaired-branch counter-world. This does not create a new public observation, but it prevents wasting a slot on E224-neighbor amplitude variants after the E216 S2 failure.
29. E227 locks how a future E166 public score should be read. E166 is not an E224 replacement; it asks whether the safety atlas became too conservative for broad survivor edge/between-train-runs context. Public win below `0.576276019` strengthens broad survivor context. Mixmin-safe loss or worse routes away from broad survivor toward E154/search. E72-scale loss says E167's E72-active warning was probably causal.
30. E228 converts the E224/E166/E154 live set into a conflict atlas before any blending. E224/E166 are almost orthogonal (`cos=0.074348`, top50 overlap `1`, same-sign E166 covers `0.035638` of E224 mass). E166/E154 are also almost orthogonal (`cos=0.061662`, top50 overlap `0`). E224/E154 are related (`cos=0.316350`) because E154's active cells are fully inside E224 and `0.885621` of E154 mass is covered same-sign by E224. This is not a public LB observation, but it fixes how future public observations should be read: E224 and E166 are separate sensors; E154 is a conditional repaired-branch counter-world, not a blind third blend component.
31. E230 is another local sensor, not a public observation. It shows that E224's Q3 tail can be pruned with small expected-focus cost and better support/adverse geometry, creating conditional files such as `submission_e230_q3_swingtop25_drop_e0918606.csv` and `submission_e230_q3_risktop21_drop_7d95c14a.csv`. The public policy does not change: submit E224 first for a clean JEPA read, then use E230 only if E224 feedback implicates Q3 tail.
32. E231 is a local negative sensor. It asks whether E230's Q3 prune can be learned from train/OOF support labels. The answer is no for the current representation: best AUC is `0.588101`, no OOF/support-tail joint gate passes, and no submission is selected. This keeps E230 as conditional hand-prune evidence and blocks an E231 learned-gate submission.
33. E232 is a local negative sensor for shared JEPA support regularization. It asks whether E216 S2, E224 Q3, and E224 S4 support tails share one hidden row/block support latent. The answer is no under current tensors: max support-label correlation is `0.057278`, max benefit correlation is `0.090611`, and Q3/S2 test low-support top25 overlap is only `1` row. Movement-shape transfer is real (`AUC=0.745452`), but it is calibration-shape evidence rather than a common public-safe support row set. This blocks shared S2/Q3/S4 support-gated submissions.
34. E233 is a local negative sensor for the cheapest target-specific JEPA rescue. It asks whether target-specific support probabilities can be reused as soft energy/amplitude heads instead of hard gates. The answer is no: promoted policies `0`, best Q3/S2/S4 learned soft policies lose to the full target movements by `+0.001713160` / `+0.001600825` / `+0.000498506`, and Q3 low-amplitude top25 overlap with the E230 risk-top21 set is `0`. This blocks softened E221/E231-style support submissions and moves the next JEPA question to the target representation/loss itself.
35. E234 is a local positive sensor for changing the JEPA target/loss. High-impact tail targets produce `323` promoted policies and beat full target movement on S2, Q3, and S4. This means the current plateau is not proof that JEPA representations are dead; it says the all-row support head was the wrong target. Because Q3 public-tail alignment remains weak and S2 already failed publicly, E234 is a materialization generator rather than a submission.
36. E235 blocks immediate S2 public materialization of E234. The strongest E234 local branch scans `240` S2 materializations but gets `0` submission-gate passes and `0` joint passes. Support stays below `0.5`, and adverse capacity remains above the observed E216 miss. This keeps the E216/E235 S2 lane closed while leaving Q3/S4 tail-target materialization as the next JEPA question.
37. E216's public score is now explicitly a negative boundary for future JEPA translators. `0.5772865088` is not a small frontier miss; it is an E216-like collapse threshold. E238 uses that score as the upper fail band for E237: if a learned Q3 cell translator lands anywhere near E216, the conclusion is not "try a different top-k" but "the translator target itself collapsed."
38. E247 public feedback is the strongest positive JEPA-family observation so far. `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` scores `0.5761589494`, beating E95 by `0.0001323804` and mixmin by `0.0001476911`. This is `8.646x` the E95-over-mixmin edge, so it is not a frontier noise tie. E248 remains useful, but now as a mismatch diagnosis rather than a veto: train OOF says smoothing is adverse, while public rewards test-side feature-neighbor Q3 geometry. The next follow-up should separate broad feature-neighbor smoothness from high-amplitude smooth cells, not return to ordinary OOF ranking.

## Derived Local Sensor Updates

These are not public LB observations; they are local stress results that decide what would be worth using as the next public sensor.

| experiment | candidate or family | local sensor result | interpretation | next public use |
|---|---|---|---|---|
| E238 E237 public-feedback decoder | top E237 learned Q3 decisive-cell file | routebook fixed before public feedback; clean support `<=0.576276019`, tie through `0.576294330`, branch loss above `0.576306641`, E216-like collapse above `0.576591330`; E237-vs-E224 readable win requires delta `<= -0.000010` | E237 public feedback is identifiable only if decoded as learned Q3 cell-tail vs clean E224 body vs hand-pruned E230 contrast | after E237 score, run `python3 analysis_outputs/e238_e237_public_feedback_decoder.py --score <PUBLIC_LB>` and add `--e224-score <E224_LB>` if known |
| E235 S2 tail-contrastive materialization | E234 S2 risk/contrast policies applied to E216 S2 on E95 anchor | scanned `240`; joint/submission gate pass `0`; max support `0.497582`; best expected rows still exceed the observed E216 miss in adverse capacity | OOF tail target does not transfer to public-safe S2 support geometry | no submission; keep E216/E235 S2 closed |
| E234 tail-contrastive JEPA target | high-impact adverse/positive OOF tail targets for E216 S2 and E224-like Q3/S4 | promoted `323`; best loss vs full S2 `-0.002653627`, Q3 `-0.000870181`, S4 `-0.000833194`; Q3 best public-tail overlap remains weak | target/loss change restores local signal, but each target needs materialization stress | no direct submission; use for Q3/S4 or sharper cell-level target audits |
| E233 target-specific soft energy heads | E216 S2 / E224-like Q3 / E224-like S4 support probabilities as soft amplitudes | promoted policies `0`; best Q3/S2/S4 learned soft loss vs full `+0.001713160` / `+0.001600825` / `+0.000498506`; Q3 low-amplitude top25 overlap with E230 risk-top21 `0` | softening current support heads under-scales useful movement and misses Q3 public-free tail anatomy | no public submission; change the JEPA target representation or loss before reopening support-head submissions |
| E232 cross-target support invariance | E216 S2, E224-like Q3, and E224-like S4 support labels | max label corr `0.057278`; max benefit corr `0.090611`; best movement transfer AUC `0.745452`; best latent-context transfer AUC `0.707003`; Q3/S2 test top25 low-support overlap `1` | support-tail risk is target-specific. The transferable signal is movement-shape calibration, not one shared row/block support latent | no public submission; do not build shared S2/Q3/S4 gates. Build future JEPA support/energy heads target-specifically |
| E231 learned E224 Q3 support prune | E224-like Q3 support labels and E230-style rollback gates | support-label rate `0.502222`; full E224-like Q3 OOF delta `-0.004262113`; best AUC `0.588101`; no joint OOF/tail gate; no selected submission | Q3 tail risk is locally prunable but not currently an invariant learned support representation | no public submission; keep E224 first and E230 conditional after E224 attribution |
| E182 current-anchor binary-world refresh | regenerated current-anchor worlds; E176/E154/E144 explicit objectives | scenario max residuals `0.0000784319`/`0.0000513148`/`0.0000762925`; strict range incumbent rate `0.233`; pressure zero-crossing rates for E176/E154/E144 `1.000`/`1.000`/`1.000`; representative spans E176 `-0.000421216..+0.000254123`, E154 `-0.00109286..+0.000923535`, E144 `-0.000992245..+0.000838041` | current anchors, including E101 public `0.5763003660`, still underidentify live-branch signs. E181 remains a counterprior, but not a promotion certificate for E154/E144 | no new submission; choose E176 only for visible-body/Q2-underopen worldview, and E154/E144 only as repaired-branch worldview sensors with decoder |
| E181 E176 binary-world counterprior audit | inherited binary worlds reranked by current public anchors; E176/E154/E144 live branches | best-5 residual worlds: E176 mean `+0.000003920` vs E95, negative rate `0.400`; best-10: `+0.000007442`, negative rate `0.300`; E154/E144 best-5 means `-0.000051451`/`-0.000051445`, negative rate `1.000`; E176 best-5 top4 support `0.433633`, top16 `0.221275` | E176 is not representation-wide best. Visible priors support E176 as a body/Q2-underopen sensor, but binary hidden-label worlds point toward the repaired E154/E144 branch | no submission from E181; regenerate current-anchor binary-world stress before promoting E154/E144 or demoting E176 |
| E180 known-anchor decisive-cell visibility calibration | known public pairs plus pending E176 | E95-vs-mixmin public-positive top4 support `0.100896`; E101-vs-mixmin `0.100896`; mixmin-vs-a2c8 `0.310904`; E176 top4 `0.330699`; failed E72 observed-adverse support `0.793304` vs mixmin and `0.696441` vs E95; all-moved visible-prior sign accuracy `0.5` | E179 top-cell weakness is not a hard veto. Visible priors can explain large E72-style failures but cannot certify E95/E101/E176 frontier-scale decisive cells | keep E176 as hidden-tail sensor; do not rank or prune candidates by visible top-cell support alone |
| E179 E176 critical-cell visibility audit | `submission_e176_abl_q2_to0p75_91e49725.csv` | full body visible-mean delta `-0.000050824`, visible win `0.999080`; Q2 damping visible delta `-0.000000191`, support `0.690495`; top4 decisive-cell support `0.330699`; top33 support `0.245771` vs null `0.335713` (`p_low=0.014667`) | E176 is body-supported and Q2-damping-supported, but not decisive-cell-certified. E101 public `0.5763003660` remains the resolved small-loss reference for this interpretation | submit E176 only as a hidden-tail sensor and decode with E177/E179; do not create another Q2 keep-factor sibling before feedback |
| E167 broad survivor context alignment | `submission_e166_broadsurv_s0p01_d8bfa94b.csv` | `74` focus cells; edge-like `0.689189` vs null `0.470842`; between-train-runs `0.797297` vs `0.624658`; all-veto-null `0.297297` vs `0.574158`; safe-density `0.117097` vs `0.243966`; E72-active `0.837838` vs `0.670369` | E166 is hidden-context-real but safety-atlas divergent. It is a public sensor for whether the atlas is too conservative, not a safer expected-score file | submit only as the broad plateau-break question; do not scale/clone before public feedback |
| E10 label-flow direct submissions | 556 transductive/MP-count files | pair_submit 0, pair_probe 0, control 0, best p90 vs a2c8 `+0.000125668` | semantic latent exists but direct probability translation is public-risk negative | do not submit direct files |
| E11 gated label-flow scan | 7240 dependency/raw05-gated files | pair_submit 0, control 50, probe 3263, conflict 0 | gating repairs direction enough for clean sensors, not strong submit | first sensor: `analysis_outputs/submission_label_flow_gated_f1046674.csv`; second sensor: `analysis_outputs/submission_label_flow_gated_ff8df011.csv` |
| E12 targetwise label-flow scan | 9444 target-mask files | pair_submit 0, control 3024, best p90 vs a2c8 `-0.000005997` | S4 is the strongest safe atom, Q3/Q2-Q3 secondary | do not submit alone unless mapping scale curve |
| E13 combo label-flow scan | 11248 atom-combo files | pair_submit 0, control 8094, best p90 vs a2c8 `-0.000035162` | S4+Q3 atoms add constructively but just miss submit threshold | use as pre-submit sensor only |
| E14 focused S4+Q3 scan | 180 focused files | pair_submit 61, best p90 vs a2c8 `-0.000065217`, conflict 0 | first strict pairwise-gate candidate, later superseded by E15 | hold pending independent survival |
| E15 focused label-flow independent survival review | 163 reviewed files, including 61 E14 pair-submit files | independent survival 0, strict survival 0, best old-selector p90 vs a2c8 `+0.000569397`, corr(pair p90, old-selector p90) `-0.881` | E14 pairwise edge is selector-family conflict, not robust public evidence | do not submit focused S4+Q3 as improvement candidate; use only as diagnostic if needed |
| E16 selector conflict decomposition | pinned S4+Q3/E11 sensors | focused files old hidden-subset better_rate `0.285714`, pairwise full-fit better_rate `0.500000`; tiny E11 sensors pairwise `0.666667` but too small | pairwise support is mixed and relies on favorable scenario tail | find independent S4/Q3 anchor or larger safe movement before public submit |
| E17 S4/Q3 anchor gap audit | pairwise universe, focused family, old-positive rescore | pairwise universe: 21 Q3/S4-shaped but 0 with old-majority; focused family: 163 Q3/S4 pair-positive but old-majority 0; old-positive rescore: 97 old-majority but Q3/S4-shaped 0 | current artifacts have no independent S4/Q3 positive anchor | stop S4/Q3 weight rescans; search new validation source or larger safe representation move |
| E18/E19 OOF anchor audit | 5167 OOF arrays and top 399 local Q3/S4 OOF submissions | 1578 local-Q3/S4-strong OOF candidates; top 399 direct selector rescore has pair p90 negative 0, pair majority 0, old majority 0, submit/control/probe 0 | local OOF Q3/S4 strength is not the missing public anchor | do not submit OOF-local Q3/S4 winners; use them as validation-mismatch negatives |
| E20 block/measurement selector rescore | 3800 block/hidden-block/presleep/raw05-block candidates | pair p90 negative 0, pair majority 52, old-majority 3, two-selector majority 0, submit/control/probe 0/0/63; large-lowbad 2505 but large-lowbad two-selector 0 | existing block/measurement candidates contain movements but no selector-resolvable a2c8 improvement | do not submit existing block/measurement files; raw05-blockcount only as diagnostic sensor if needed |
| E21 selector support topology | merged scored universe | pair-only 465, old-only 97, pair-probe-not-majority 56, two-selector majority 0, strict candidate shape 0 | public-sensitive selectors disagree structurally: S4-heavy pair-only vs Q3/raw05-drift old-only | next public use should be explicit selector-disambiguation, not improvement claim |
| E22 selector disambiguation sensor design | pair-only S4/Q3 vs old-only Q3/raw05-drift sensors | pairwise selector pass 33/36 and raw05 direction correct 0.916667; old selector pass 0/7 and raw05 direction correct 0.0 | old-only support is already weakened by raw05 being public-worse than A2C8; pair-only S4/Q3 is the better diagnostic sensor | if using a public sensor, submit `analysis_outputs/submission_label_flow_focused_1bbfb735.csv`; do not treat it as an improvement claim |
| E23 label-flow sensor scale curve | 108 A2C8-to-S4/Q3 scaled sensor variants | pair p90 negative in every mask family, but two-selector majority 0; balanced 0.65 sensor pair p90 `-0.000034496`, old p90 `+0.000571958` | scaling lowers old p90 but does not make old selector agree; conflict is directional | use 0.65 scaled sensor only if lower-risk diagnostic is preferred over maximum contrast |
| E24 label-flow localized sensor audit | 960 subject/date/block/phase/energy/sign localized S4/Q3 variants | pair p90 negative 807, old-majority 0, two-selector majority 0; loose candidates only on tiny `id02_b02` block with pair p90 around `-2e-7` | simple localization does not turn pair-only S4/Q3 into a two-selector-supported public candidate | do not submit localized sensors; use as evidence against more handcrafted row-mask sweeps |
| E25 direction probe selector reconciliation | 22 mixmin/direns/sparseladder/targetabl/inverse7 probes | pair p90 negative 0, pair majority 0, old-majority 0, two-selector majority 0 | large score-oriented probes test a different selector worldview; they are not strict-survival candidates | `submission_mixmin_0c916bb4.csv` is only a high-risk score-probe if public slot is used for that question |
| E26 public LB inverse feasibility | 8 known public LBs, LP inverse models | exact fit under all-test soft labels and cell-mixture; all 8 unobserved candidate deltas cross zero even with train-prior bands | known LB observations are too underidentified to rank current candidates directly | use LB as a sensor for predeclared hypotheses only |
| E27 public LB structural-prior stress | global target and subject-target prior LP scenarios | all 7 scenarios fit known LBs with slack 0; unobserved candidate cells crossed zero `56/56`; one-sided improvement 0 | train/subject priors do not collapse the public-LB feasible worlds | do not use subject-prior inverse ranking for current submissions |
| E28 binary hidden-label inverse stress | binary all-test MILP incumbents | tight subject-prior incumbent max residual `0.000061242`; no one-sided improvement evidence; `6b9335b1` crosses zero under no-prior incumbents | binary exactness may be realistic but is not yet a ranker | do not submit from a single binary inverse world |
| E29 binary world-pool sign audit | 15 tight-prior binary MILP incumbents | 15 unique worlds, but only 1 frontier-scale world; all-world better_rate: mixmin `0.8667`, inverse7 `0.7333`, pair sensors `0.2667-0.3333`; frontier world favored mixmin/inverse7 and rejected pair S4/Q3 | binary-world hypothesis weakly prefers the high-risk score-probe lane, but sample size is too small for a gate | do not submit from E29; expand frontier-world pool first if this sensor is pursued |
| E30 binary frontier-box pool | 29 tight-prior binary MILP incumbents with each public-anchor residual <= raw05-a2c8 gap | 29 frontier-scale worlds, 28 unique; random-plus-fit worlds favor mixmin `19/19` and inverse7 `18/19`; candidate-max worlds still make both worse | binary-world hypothesis now strongly disfavors pair-only S4/Q3 and favors score-probe metadata, but still does not certify improvement | if public slot is used for this worldview, mixmin is the clearest probe; not a strict submission |
| E31 binary world plausibility geometry | train-only geometry score over E30 worlds | random+fit worlds favor mixmin `19/19`, but the two mixmin-adverse worlds are plausibility ranks 1 and 2 | train label dynamics cannot dismiss the adverse binary worlds | mixmin remains information-rich probe, not certified improvement |
| E32 binary anchor loss geometry | known public-anchor per-target loss decomposition over E30 worlds | low-anchor-energy half supports mixmin `15/15` and inverse7 `15/15`; low quarter supports both `7/7`; adverse mixmin worlds are high-energy ranks `26` and `28` | known-anchor loss attribution rejects the adverse worlds that generic train geometry could not reject | mixmin becomes the clearest high-risk binary/actual-anchor public probe; still diagnostic, not certified |
| E33 binary anchor loss LOO stability | leave-one-anchor-out recomputation of E32 energy | mixmin low-energy half/quarter better_rate stayed `1.0` in all 7 LOO runs; no adverse mixmin world entered any LOO low-energy half | E32 is not explained by one known-anchor artifact | strengthens mixmin as a public sensor; still needs new observation to validate |
| E34 binary anchor loss family/null audit | family holdout, component ablation, and target-axis permutation null | mixmin survives no-raw05/no-medium/no-bad and only-medium scenarios; only-bad-JEPA fails; target-axis permutation keeps mixmin one-sided in `500/500` permutations | signal is broad medium-anchor loss/cancellation geometry, not exact target-axis semantics | keep mixmin probe priority but lower JEPA-axis semantic claim |
| E35 public probe independent evidence audit | local/selector/anchor evidence tiers for current sensors | normal submit gates `0`; mixmin has honest-CV support but pair/old hard veto remains | strongest mixmin evidence is still anchor-derived or quasi-public | use mixmin only as high-risk public sensor |
| E36 raw-structure pseudo-label stress | 10 train-derived subject/date/raw-feature pseudo-label sources | inverse7 support `10/10`, mean delta `-0.000705727`; mixmin support `5/10`, mean delta `+0.000065107` | observed raw structure favors inverse7, not mixmin | inverse7 becomes raw-structure bridge sensor, not certified submission |
| E37 inverse7 raw-anchor bridge scale scan | 22 inverse7/mixmin scale-blend variants | raw gates `14`, anchor gates `22`, two-selector majority `0`, strict bridge gates `0` | raw+anchor support does not remove selector veto | do not submit inverse7 scale-blends as improvement claims |
| E38 worldview sensor discriminability audit | cross-source evidence join for 10 sensors | normal-submit `0`, public-sensor `10`; top information sensor mixmin score `3.355110` | current action is public-sensor selection, not improvement ranking | predeclare sensor lane if using public slot |
| E39 OOF selector calibration audit | 4172 OOF rows over label-free pseudo-public stresses | strict OOF gates `1311`, conservative `1115`; known-public sign match `1.0`, rank agreement `0.0` | OOF can screen local instability but reverses stage2/ordinal public rank | do not use OOF as public selector |
| E40 test-movement fingerprint selector | target/subject/order/raw-domain movement fingerprints vs A2C8 | strict views `0`, loose views `4`; stage2/ordinal order correct; combined rank accuracy `0.821429`, null p `0.004` | movement anatomy is informative but underpredicts bad JEPA severity and cannot certify A2C8 as best in LOO | use only as loose prior; favors `inv7_s0p25` as lower-risk diagnostic |
| E41 movement + bad-axis geometry selector | LOO-safe logit cosine/projection features against raw/medium/bad anchor axes | strict views `0`, loose views `0`; `axis_group` MAE `0.000854918`, rank `0.785714`, bad underprediction `0.000898399`, A2C8 LOO predicted `+0.001475508` worse | bad-axis geometry fixes part of E40 severity collapse but still does not identify public selector | do not use axis prior as a public LB forecast |
| E42 fixed-zero anchor selector calibration | A2C8 fixed at zero; nonbaseline LOO over compact/axis movement views | fixed gates `0`, usable gates `0`; best `axis_group` MAE `0.000766262`, rank `0.857143`, raw05 gap/MAE `0.113520`, best unobserved advantage/MAE `0.065408` | current-best anchoring improves coarse nonbaseline rank but still cannot resolve frontier-scale edges | do not use fixed-zero axis prior as a public LB forecast |
| E43 selector resolution boundary audit | current selector errors and candidate edges compared to raw05-A2C8 gap | frontier-resolution gates `0`; certified better-than-A2C8 `0`; certified better-than-raw05 `0`; best selector error `0.000218288` | selector error is larger than the public edge being optimized | no micro-edge normal submissions from current selectors |
| E44 large-edge low-risk census | 29 current score tables, 69,869 rows, 48,088 unique files | pair edge > raw05-A2C8 gap `0`; pair edge > selector error `0`; normal large-safe files `0`; best pair edge `0.000073768` | current universe has no selector-resolvable large safe movement; raw/anchor large edges remain worldview conflicts | do not submit existing scored candidates as improvement claims |
| E45 structured public-subset feasibility | 145 subject/order/date/raw-domain/random masks with train-prior soft-label LOO | selector-scale gates `0`; strict sub-gap gates `0`; best LOO MAE `0.000429528`; best MAE/raw05 gap `4.937886`; feasible ranges mean width about `0.04` | simple public-subset masks are not the missing selector target; ranges contain anchors because they are too wide | do not rank candidates from simple structured-mask inverse fits |
| E46 block-state bottleneck audit | oracle/Markov/threshold/hidden-block/topology/lag/mask evidence | block-rate oracle `0.517878`; temporal-to-oracle gap `0.106888`; subject identity explains `0.291286`; Markov `+0.002998`, nested threshold `+0.044275`, endpoint gain `0.003252`; two-flank blocks `26/36` | 0.54 is structurally possible only through hidden block-rate state inference; current row/context heuristics do not recover that state | next local work should be block-rate JEPA context-target modeling, not another submission candidate |
| E47 block-context JEPA target audit | fold-safe Ridge heads from label-context, sensor-value, missingness, and combined block summaries to held-out block-rate vectors | best 25% row blend `label_context_ridge = 0.623260`, delta `-0.001505`; oracle-gap recovery `0.014083`; block-rate loss `0.635888` vs temporal `0.623448`; sensor values row blend `+0.000660` | current block summaries do not recover hidden block-rate state; the small row gain is calibration-like | no submission; change block context/target construction before probability translation |
| E48 mixmin public LB observation | `analysis_outputs/submission_mixmin_0c916bb4.csv` public submission | public LB `0.5763066405`, improvement vs previous best a2c8 `-0.0011326805`, improvement vs raw05 `-0.0012196667` | maximum-information public sensor succeeded. Anchor-loss/binary actual-anchor worldview is public-relevant; pairwise/old selector veto is not a valid hard gate | promote mixmin to frontier; rebuild selector calibration and next candidates relative to mixmin |
| E49 post-mixmin observation audit | mixmin/a2c8/raw05 movement, simple prior CE stress, subject concentration, and calendar masks | train/test is subject-calendar hidden masking, not future-only; largest movements `Q3/Q1/S3`; `Q1/S1` are adverse under simple prior proxies; high-movement blocks often `gap_adjacent` or `between_train_runs` | mixmin is not ordinary prevalence correction; it likely approximates hidden block/state structure on selected subject-calendar holes | no submission; build mixmin-relative calendar-block selector and block-rate context target |
| E50 post-mixmin calendar selector | mixmin included as known anchor; target/prior, calendar, subject, and subject-calendar movement views | strict views `0`, loose views `0`; best `subject_calendar` MAE `0.000884106`, rank `0.833333`, Spearman `0.833333`; held-out mixmin predicted delta `0.00135162`, so `mixmin_predicted_best=False` | calendar movement is informative but not enough to explain the mixmin public-best anchor | no submission; next public sensor must combine calendar context with anchor-loss/binary-world or block-rate target evidence |
| E51 post-mixmin anchor-calendar selector | LOO-safe E32-style binary-world anchor-loss aggregates plus compact E50 calendar fingerprints | strict views `0`, loose views `0`; best `anchor_residual` MAE `0.000835516`, rank `0.750000`, Spearman `0.633333`; held-out mixmin predicted delta `0.00241739`, so `mixmin_predicted_best=False`; a2c8/raw05 order also failed | anchor-loss was public-relevant as a hidden-world sensor, but not as a smooth transferable kNN selector over submission files | no submission; move to calendar-flank block-rate/count targets or mixmin-constrained binary-world sign stress |
| E52 post-mixmin binary-world sign stress | E30/E32 worlds conditioned on actual mixmin delta; 158 candidates scored vs mixmin | strict better-than-mixmin `0`, loose `0`, near-tie `1`; near-tie `bridge_blend_m0p75_s1p25` had better_rate `0.2`, median `+0.000034`, max `+0.000048` in 1-gap band | existing candidate pool does not contain a binary-world-certified mixmin replacement | no submission; next public-relevant work is block-rate/count target or fresh mixmin-hard world generation |
| E53 calendar-flank count-state probe | pseudo-hidden and real hidden block count/rate posterior from labeled flanks and donor signatures | local pseudo-hidden delta `-0.005266`, strict subject-excluded delta `+0.001434`; strict hidden mixmin delta `-0.000179`, local `+0.000250`; strict target alignment S3/S2/Q2 favorable but Q1/Q3/S1/S4 adverse | mixmin is not explained by a simple private-safe flank count posterior; calendar signal is context/energy rather than a submission forecast | no submission; next public-relevant work needs richer raw context, target-dependency count manifolds, or fresh mixmin-hard worlds |
| E54 raw overnight block context probe | raw overnight feature-family PCA block embeddings plus flank context | best strict `night_phone_rawctx_strict_k8_a24` pseudo-hidden delta `-0.007733`; S3 pseudo-hidden delta `+0.007802`; same method hidden mixmin delta `+0.000311`; best hidden alignment still `calendar_count_strict` at `-0.000179` | raw context recovers real strict block state, but it is not the mixmin-public latent and should not be directly submitted | no submission; next public-relevant work must resolve raw-vs-mixmin sign conflict or use raw context only as a hard-world feasibility prior |
| E55 raw block target-dependency probe | E54 raw block rates projected through strict donor Q/S target-rate manifolds | `225` methods, joint gates `0`; S3 subject replacement raw delta `-0.001115` but hidden mixmin `+0.000319`; best hidden-sign Ridge `-0.000414` but pseudo-hidden LogLoss `0.727319` | simple target-rate projection cannot translate raw strict latent into mixmin-public latent | no submission; next public-relevant work should use mixmin-hard binary worlds with raw context as feasibility prior or a structural block target |
| E56 mixmin-hard raw world probe | mixmin included as a hard public observation; raw overnight hidden rates used as feasibility prior | `45` worlds, `44` unique; existing candidate strict gates `0`; posterior world-LOO strict gates `12`; diagnostic submission generated with mean abs logit move `0.381359` | hard-world family can create a coherent posterior, but this is only internal world evidence | require E57 safety stress before any public submission |
| E57 mixmin-hard posterior safety stress | E56 posterior variants tested with independent actual-anchor/public-shape proxy and movement guard | `15` variants, joint gates `0`; best posterior anchor delta `+0.000123`; E56 selected diagnostic anchor delta `+0.020381` | direct E56 posterior is public-anchor adverse despite internal coherence | no submission; use E56 posterior as energy/teacher only |
| E58/E61 mixmin-hard posterior distillation probe + score-index audit | E56 teacher gated by band/target/cell/row/cap/weight, then actual-anchor scored after world-support prefilter; E61 fixed stable `pred_index` identity through sorted prefilters | `104727` generated, `1200` scored; toward eligible gates `0`; corrected toward sign beats `126/900`; best toward anchor delta `-0.000004081`; best reverse `-0.0000000126` | simple E56 distillation remains non-adverse only below selector-scale margin; the E58 rejection is not a scoring-index artifact | no submission; next needs structural block target or independent non-anchor validation |
| E59 structural joint-pattern probe | 128-state within-block Q/S label-pattern distributions predicted from strict raw/calendar/subject contexts | structural methods `216`; pattern NLL beats raw `139`; row LogLoss beats raw `0`; joint gates `0`; best hidden sign `-0.000367` only with row collapse `+0.042230` | joint label structure is real but not a public-aligned probability translation | no submission; do not use pattern-derived rates as a public test |
| E60 transition-residual block-state probe | strict logit-rate residual prediction from endpoint/raw/subject baselines and topology/raw contexts | transition methods `432`; residual MSE beats raw `227`; hidden mixmin negative `217`; joint gates `0`; best hidden sign `-0.001569` only with row collapse `+1.519232` and S3 `+1.331880` | transition residual is a hidden-sign sensor but not a calibrated non-anchor validator | no submission; use only as teacher-risk diagnostic |
| E62 transition-gated posterior distillation probe | E60 transition residual views used only as gates for small E56 teacher movement | `363258` generated, `1300` scored; eligible gates `0`; best toward anchor delta `-0.000002716`; best reverse `-0.00000000547`; balanced transition view hidden mixmin `-0.000289` | transition residual gating does not rescue E56 distillation and is weaker than corrected E58 | no submission; transition residual remains risk diagnostic, not missing validator |
| E63 gradient-consensus posterior probe | subject/calendar/raw/transition hidden-rate views used as BCE-gradient guards for small E56 teacher movement | `404671` generated, `1300` scored; toward hidden guard `1000/1000`, reverse hidden guard `0/300`; toward anchor beats `932/1000`; eligible gates `0`; best toward anchor delta `-0.000003650` | E56 direction is independently supported by hidden-rate gradients, but still not public-anchor margin-safe | no submission; use gradient consensus as direction energy and solve amplitude/public-anchor translation next |
| E64 gradient-amplitude translation probe | larger scale/cap moves on the E63 gradient-consensus cells | `12096` generated, `1796` scored; toward hidden/world/movement guards `1346/1346`; toward anchor beats `0/1346`; best toward delta `+0.000003024`; reverse best `+0.000000154` | E63 is not merely under-scaled; larger validated E56 movement is public-anchor adverse | no submission; amplitude must be targetwise/rowwise or structural, not scalar |
| E65 near-zero amplitude response probe | small targetwise line search around E63 gradient-consensus cells | `27384` generated, `2400` scored; toward hidden/world/movement guards `2290/2290`; toward anchor beats `1753/2290`; best toward delta `-0.000005995`; margin gates `0`; best mask `no_q2_s3` | a local target-conflict pocket exists but remains below submission margin | no submission; next question is why excluding Q2/S3 is necessary |
| E66 Q2/S3 conflict translator probe | matched target-mask add-back and target contribution audit around E65/E63 cells | `3000` generated/scored; `no_q2_s3` best `-0.000005995`; `all` add-back robust-anchor adverse `432/432`; `all` mean-anchor improves `288/432`; `all` max-set tail worsens `432/432`; hidden core improves `432/432` | Q2/S3 conflict is public-anchor tail risk, not absence of hidden direction | no submission; next target is a tail-neutral Q2/S3 translator |
| E67 tail-neutral Q2/S3 translator probe | Q2/S3 added back by uniform weights or first-order anchor-scenario tail gates while non-Q2/S3 E65 move is preserved | `7632` generated/scored; best `tail_meanneg_m1.00` delta `-0.000006933`; best strict-tail `tail_p90_nonpos_m1.00` delta `-0.000006587`; matched base beats `4207/7200`; max-set-tail-neutral base beats `2241/7200`; margin gates `0` | first-order tail gates improve the Q2/S3 translator but remain sub-margin and anchor-derived | no submission; independently validate tail-gated cells before any file |
| E68 Q2/S3 tail-gate independence probe | selected E67 configs rebuilt while each combo set was held out from gate construction, then stressed on heldout combo plus hidden/world/block Q2/S3 checks | selected `180`; scored `762` unique predictions; matched pairs `540`; independent gates `155`; strict independent gates `155`; best strict `tail_p90_nonpos_m1.00` heldout delta `-0.000001261`; `tail_soft_max_m1.00` strict gates `44`; `tail_p90_nonpos_m1.00` strict gates `41` | E67 cells are not merely same-anchor derivative artifacts, but the validated edge is still `1e-6` scale | no submission; use strict cells as latent/amplitude gate source |
| E69 Q2/S3 strict-cell amplitude probe | E68 strict cells scaled by alpha over only Q2/S3 logit delta while non-Q2/S3 stayed at matched `no_q2_s3` base | strict pairs `155`; rows `2170`; unique predictions `2061`; strict amplitude gates `0`; full-combo margin gates `0`; best all delta `-0.000009178`; heldout tail-neutral falls from `155/155` at alpha `1` to `22/155` at alpha `24` | simple alpha amplification improves toward margin but plateaus below selector margin and erodes heldout/tail stability | no submission; need rowwise/cellwise amplitude or structural target |
| E70 Q2/S3 strict-cell consensus probe | E68 strict cells aggregated into pooled base and Q2/S3 consensus deltas, then combo-scored and hidden/world/block stressed | candidate rows `2688`; unique predictions `2576`; strict consensus gates `6`; loose gates `502`; best all delta `-0.0000102775`; all strict rows use `gate=none` and all `3/3` combo sets beat base/tail-neutral | consensus accumulation is a live local structure, but the rule is not unified or conservative enough for public submission | no submission; next test is unified-rule consensus or LeJEPA-style consensus energy |
| E71 unified Q2/S3 strict-cell consensus probe | E68 strict rows selected `104` unique cells, then each cell was rebuilt once with full combo tables before consensus scoring | candidate rows `3136`; unique predictions `2842`; strict unified gates `1`; deployable unified gates `0`; loose gates `475`; best all delta `-0.0000108217`; only strict row is `gate=none` | unified consensus is not pure heldout arithmetic, but conservative deployable geometry is still absent | no submission; use as consensus energy and repair the `gate=none` dependence |
| E72/E73 sparse Q2/S3 gate probe | E71 unified cells swept through sparse magnitude, soft agreement, and target-only gates; best deployable row materialized | E72 rows `4752`; strict `21`; deployable non-`none` `10`; `top_abs50` deployable `7`; `s3_only` deployable `3`; selected file `submission_e72_topabs50_q2s3_gate_4e48cba2.csv` with all delta `-0.0000105458`; later public LB `0.5764077772` | non-`none` gate geometry exists locally, but the submitted combined file is public-adverse and contaminated by broad all-target movement | do not resubmit; use only as diagnostic latent inside broader structural/block-state candidates |
| E74 sparse Q2/S3 gate stability probe | E73 full source pool stressed by jackknife, group/rank subsets, and deterministic bootstrap8 subsets; full-pool alpha20 materialized | rows `470`; variants `94`; strict/deployable `141`; jackknife alpha16 deployable `13/13`; bootstrap8 alpha16 deployable `48/60`; full-pool alpha20 file `submission_e74_fullpool_a20_q2s3_gate_55455b60.csv` with all delta `-0.0000107261`; alpha24 reference fails strict | E73 is not a single-cell artifact, but public now rejects the submitted combined sign sensor | hold E74 alpha20; only revisit after a pure sparse-gate public sign becomes positive |
| E75 target-specific Q2/S3 amplitude ridge | E74 full-pool sparse gate crossed with Q2/S3 target-specific alphas; best asymmetric row materialized | rows `120`; strict/deployable `37`; `s3_higher` deployable `23`; `s3_only` `6`; `q2_only` `0`; selected file `submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv` with all delta `-0.0000123676` | symmetric alpha20 is not the local optimum; S3-heavy/Q2-low amplitude is a live hidden-world hypothesis | use after E73 if testing target-asymmetric sparse-gate amplitude; keep E74 as symmetric control |
| E76 target-specific Q2/S3 amplitude stability | E75 alpha grid replayed across E74 source-subset variants | rows `1974`; variants `94`; strict/deployable `1138`; exact `asym8_28_e75` beats sym16/sym20 in `94/94`; exact deployable `49/94`; best deployable axis S3-heavy `94/94` | public-readable direction is likely target-asymmetric, but exact `q2=8/s3=28` is a sharper and less stable bet than E73 sign | E75 is second-sensor material only when testing target asymmetry; E74 is safer symmetric control; no new public file from E76 |
| E77 Q2/S3 amplitude posterior aggregation | E76 source-subset predictions aggregated as logit posterior movements from mixmin/E73/E74 | rows `6840`; strict/deployable `0`; loose `3099`; rows beating E75 local all-combo `62`; mixmin/q2s3 safe but best `-0.000008095`; mixmin/full can reach `-0.000012599` but breaks set/tail consistency | exact-amplitude instability is not solved by averaging source-subset predictions; the missing object is combo-set/tail-conditioned amplitude | no submission; use as negative sensor and move to localized amplitude |
| E78 Q2/S3 localized amplitude gate | E76 exact/deployable/S3-heavy/deployable-vs-failed source distributions converted into reliability masks over E75 sparse movement | rows `4452`; masks `36`; strict/deployable `1806`; loose `3934`; deployable rows beating E75 `0`; best all equals E75 `-0.0000123676`; consensus masks mostly identity; excess/veto sparse | source-subset reliability masks do not create a better amplitude law than E75 top_abs50 | no submission; next amplitude localization must use public-like row/block/tail state or public feedback |
| E79 public-like row/block Q2/S3 amplitude gate | subject-calendar topology, positive unit-energy, subject-prior, subject-id, nearest train-label flank, and target-specific flank masks applied over E75 sparse movement | rows `6516`; masks `61`; strict/deployable `1318`; loose `3403`; deployable rows beating E75 `0`; best all equals E75 `-0.0000123676`; E75 active movement covers `72/250` rows/cells | handcrafted row/block/flank masks do not improve E75; simple public-like row topology is not the missing amplitude selector | no submission; E80/E81 supersede the old E73-first public order |
| E80 E73 public observation assimilation | public LB `0.5764077772` for `submission_e72_topabs50_q2s3_gate_4e48cba2.csv` compared with mixmin | public delta `+0.0001011367`; local expected delta `-0.0000105458`; moved cells `893`; moved rows `249`; active targets `Q1,Q2,Q3,S1,S2,S3,S4`; isolated Q2/S3 cells only `79` | submitted E73 was a broad all-target movement, not a clean Q2/S3 public sign test. The combined file is rejected as public-aligned | pause E74/E75 direct follow-ups; split pure Q2/S3 from non-Q2/S3 movement before another sparse-gate submission |
| E81 pure E73 Q2/S3 graft split | mixmin anchor with only E73 Q2/S3, Q2-only, S3-only, non-Q2/S3-only, and inverse-sign variants | rows `8`; strict/deployable `0`; loose `3`; pure Q2/S3 all delta `-0.000005954`, `3/3` combo sets beat base/tail-neutral, hidden Q2/S3 `-0.000391043`, but margin gate false; inverse Q2/S3 all delta `+0.000014747` and all local guards fail | isolated Q2/S3 direction is locally real but sub-margin; broad non-Q2/S3 movement is also sub-margin and tail-adverse; public-sign inversion is not locally defensible | no immediate submission from E81; E82 later shows the wider pure source universe is also margin-limited |
| E82 pure Q2/S3 source-graft scan | E72/E75/E76 source predictions grafted onto mixmin using only Q2/S3/Q2/S3-only values or source-base deltas | rows `8402`; evaluated `700`; strict/deployable `0`; loose `700`; best evaluated all delta `-0.000007903`; non-margin guards pass `700/700`, all-margin pass `0/700` | pure Q2/S3 source universe is coherent but margin-limited; base contamination removal alone cannot create a submission-scale file | no public file; use Q2/S3 as latent energy inside a broader structural/block-state candidate |
| E83 Q2/S3-energy structural gate scan | E82 Q2/S3 row energy used as a gate over broad structural submission deltas | rows `3716`; evaluated `700`; strict/deployable `0`; loose `40`; structural-loose `189`; best evaluated all delta `-0.000035052`, but broad margin rows worsen Q2/S3 hidden/world and beat only `2/3` combo sets | broad structural margin exists but conflicts with Q2/S3 safety; E72-safe rows are still sub-margin | no public file; recombine non-Q2S3 structural movement with Q2/S3-only safety movement |
| E84 structural margin + Q2/S3 safety recombination | E83 non-Q2S3 structural deltas plus E72-derived Q2/S3-only safety deltas | rows `1728`; evaluated `700`; strict/deployable `0`; loose `700`; best evaluated all delta `-0.000032150`; all evaluated rows pass margin/hidden/world/block, but inverse-top combo set rejects `700/700` while raw05-compatible/all-sign accept `700/700` | remaining bottleneck is public-observation set identity rather than Q2/S3 direction or target-group additivity | diagnostic file `submission_e84_inverse_sensor_1c74da00.csv` created only to test whether public follows inverse-top or the raw05/all-sign worlds |
| E85 inverse-top target-prune | target subsets applied to E84 movement and rescored against inverse-top/raw05-compatible/all-sign plus hidden/world/block stress | rows `10135`; evaluated `700`; strict/deployable `535`; best `S1,S2,S3` file all delta `-0.000023876`, inverse-top `-0.000008167`, raw05-compatible `-0.000029555`, all-sign `-0.000033906` | E84 inverse-top conflict is target-axis contamination first; Q1/Q3/S4 movement is adverse while S1/S2/S3 structural movement survives | next public file: `submission_e85_inverse_conflict_pruned_58b23ed1.csv` |
| E86 E85 source-consensus robustness | source-diverse consensus over strict E85 target-pruned rows | rows `1485`; evaluated `700`; strict/deployable/loose `700/700`; selected `Q2,S1,S2,S3` mean top-40 shrink `1.25` file all delta `-0.000027706`, inverse-top `-0.00000691`, raw05-compatible `-0.000035339`, all-sign `-0.000040869`, hidden/world/block favorable | E85 target-prune law is not a single-source artifact; source consensus adds margin but increases overstep/Q2 add-back risk | highest-upside next public file: `submission_e86_e85_consensus_a3f7c96f.csv`; E85 remains conservative fallback |
| E87 E86 risk decomposition | no-Q2, no-overstep, and inverse-top-prior contrasts built from the same E86 consensus pool | rows `1485`; strict/deployable universe `700`; no-Q2 all delta `-0.000026946`; no-overstep all delta `-0.000024255`; inverse-top-prior inverse-top delta `-0.000020643` | E86 public failure can now be split into Q2 add-back, shrink overstep, or inverse-top-prior geometry | do not submit before E86 unless the goal is diagnostic contrast rather than highest-upside sensor |
| E88/E89 E72 contamination attribution and repair | E88 compared E86/E87 movement to the failed E72 movement; E89 scanned E86/no-Q2 blends, row/cell fallback, Q2 removal, and projection-away repairs | E86 contamination index `0.772379`; no-Q2 `0.730408`; E85 `0.734771`; E89 selected E86 with E85 fallback on top-20% E72 cells, all delta `-0.000025896`, contamination index `0.676361`, strict/deployable true | E86's public risk is now a measurable movement-manifold risk, and at least part of it is cell-local. The repair reduces E72 proximity but sacrifices E86 hidden/world/block edge | public use depends on question: E86 for max upside, E89 for E72-downside control |
| E90 E89 Pareto-knee selector | E90 rescored the E89 strict scan for balanced E72 decontamination and E86 structure retention | selected `submission_e90_e72pareto_28925de5.csv`, E86 with E85 fallback on top-10% E72 rows; all delta `-0.000026932`, contamination `0.715784`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block win `0.777778`, tail safe `1.0` | minimum E72 contamination and maximum structural retention are different objectives. E90 is the row-coherent middle point between E86 and E89 | public use: balanced sensor if the next question is whether row-level structural retention matters more than absolute E72-cell cleanup |
| E91 E72-updated selector collapse audit | known-public movement proxy rerun after adding E72, then scored only E85/E86/E87/E89/E90 | best LOOCV proxy MAE `0.000543412`, p90 error `0.001010234`; mixmin holdout error `+0.001142722`; E72 actual delta vs mixmin `+0.0001011367` but predicted E72-minus-mixmin `-0.0000460726` | public-LB regression remains too coarse. It cannot rank E86/E90/E89 because it cannot resolve the known mixmin/E72 pair | no E91 submission; use public slots as predeclared hypothesis sensors, not proxy-ranked optimizations |
| E92 hidden-block posterior alignment audit | E72/E85/E86/no-Q2/E90/E89 scored against hidden-block posterior and endpoint target representations | failed E72 is the alignment leader; posterior CE delta E72 `-0.000287300`, no-Q2 `-0.000257196`, E86 `-0.000255621`, E90 `-0.000250767`, E89 `-0.000235903`; E89 block-target R2 `0.356204` and E72 mass agreement `0.635838` | hidden-block posterior is E72-tainted as a public selector. Coherent block representation is not the same as public-safe translation | no E92 submission; keep posterior CE as representation-health diagnostic, not ranking rule |
| E93 target-manifold counter-energy audit | train-label conditional target models plus empirical label-pattern and correlation energies tested as E72 counter-filter | E72 target-manifold delta mean `-0.001468687`; live candidates favorable but smaller: E86 `-0.000921783`, E90 `-0.000877945`, E89 `-0.000806467`; public-bad final9 and bad-Q2 JEPA also favorable | E72 failure is not an obvious target-dependency violation. Target-manifold consistency is diagnostic, not a public-safe selector | no E93 submission; keep E86/E90/E89 ordering hypothesis-based |
| E94 soft-health hard-label tail audit | E72-adverse hard-label direction computed per cell, then candidate exposure measured against mixmin | E72 full adverse exposure `0.002330945`; observed miss is only `0.043389` of that scale; live exposure E85 `0.000739201`, E89 `0.000799109`, E90 `0.000934031`, E86 `0.001010242`; known-public Spearman: hard worst-tail `0.866667`, soft-health `0.081935` | soft JEPA-style health can hide the hard-label tail that LogLoss punishes. E86 remains max-upside, E89 becomes lower-downside hard-tail sensor, E90 stays row-coherent compromise | no E94 submission; future soft-health gates need hard-label tail checks |
| E95 hard-tail localized gate scan | E94 hard-tail exposure converted into controlled E86/E90 row/cell fallback gates | rows/evaluated/strict `178/178/112`; strict non-dominated `19`; selected `submission_e95_hardtail_541e3973.csv` starts from E86 and falls back to E85 on E72-adverse top-tail cells; all delta `-0.0000262074`, E72-adverse tail `0.000788914`, hidden Q2/S3 `-0.000251140`, world `-0.000132931`, block win `0.750000`, tail safe `0.972222`; public `0.5762913298` | hard-tail localization adds a candidate beyond E89/E90: E95 beats E89 on both local margin and hard-tail exposure, then beats mixmin on public | current frontier; use as the anchor for E95-relative retained-structure or conservative-floor tests |
| E96 public-miss budget tail scenarios | observed E72 miss fixed as total hard-tail budget and allocated over plausible E72-adverse cells | `3894/3894` complete-budget scenarios; E72 reconstructs `+0.0001011367`; live mean deltas E95 `0.000057874`, E85 `0.000058977`, E89 `0.000059964`, E90 `0.000069295`, E86 `0.000076162`; live p95 E85 `0.000115304`, E95 `0.000115644`, E89 `0.000117735`; E95 beats E89 `0.712378` and wins live set `0.527478` | E95 is the best mean/win-rate hard-tail sensor and broadly beats E89/E90/E86; E85 is still the pure conservative p95 tail floor | no new submission; keep E95 as top information-rich hard-tail sensor, use E85 only if the next public question is pure downside floor |
| E97 E95 public observation | `submission_e95_hardtail_541e3973.csv` submitted after E96 | public LB `0.5762913298`; delta vs mixmin `-0.0000153107`; delta vs failed E72 `-0.0001164474`; realized gain is `58.42%` of E95 local all-combo margin and `15.14%` of the E72 miss scale | hard-tail localization is public-positive. The realized public labels were not so tail-adverse that E95's retained E86 structure failed; however the small edge means the main block-rate/calibration bottleneck remains | promote E95 to frontier; next public sensor should test more retained structure (`E90`/`E86`) or the conservative floor (`E85`) |
| E98 E95-updated selector audit | E95 added to public observation table; fixed LOOCV movement proxy rerun over 11 known anchors | best proxy p90 `0.000816497`, `53.33x` E95 edge; E72-minus-mixmin sign still wrong; future proxy spread `0.000015142` is not interpretable | E95 improves the observation log but does not make known-LB regression a usable selector | no proxy-ranked submission; keep E90/E86/E85 ordering hypothesis-based |
| E99 E95-conditioned tail transfer audit | E72 miss and E95 gain jointly used as public sensors in a per-scenario `local_delta + E96_tail_delta` transfer solve | `3894/3894` scenarios solved; broad-plausible `3452`; broad best mean/best p95/winner mode all E95; beat-E95 rates: E89 `0.195829`, E85 `0.031866`, E90 `0.002607`, E86 `0.000290` | conditioning on E95 sharply weakens the immediate E90/E86 improvement story. The only unresolved nontrivial E95-beat counterfactual is E89's older cell-fallback geometry | no E99 file; keep E95 as current best. If exactly one diagnostic slot is used for E95-beat probability, E89 is sharper than E90; E90 remains a row-coherent structure sensor only |
| E100 E89 counterfactual anatomy | E99 broad-plausible E95-conditioned worlds decomposed by mask/order/family and tail surplus | broad-plausible `3452`; E89 beat-E95 `0.195829`; mean E89-minus-E95 `+0.000003833`; E89-beating cases `676`, top mask `q2s3`; `q2s3` slice beat rate `0.779891`, mean E89-minus-E95 `-0.000005030`; non-beating cases top mask `s1s2s3` | E89 is not a broad E95 replacement. Its live pocket is specifically Q2/S3 diffuse-tail allocation where older E72-cell fallback beats E95's localized hard-tail cells | no E100 file; submit E89 only if the public question is Q2/S3 diffuse-tail over-localization. If E89 fails, retire it as a near-term successor |
| E101 Q2/S3 tail graft probe | E100's Q2/S3 diffuse-tail pocket isolated as E95-relative rollback/graft candidates | rows/grafts/strict-like/pass `618/612/581/54`; selected `submission_e101_q2s3tail_177569bc.csv`; only `50` active cells vs E95; all delta `-0.0000253724`; E72-adverse exposure `0.000692235`; broad mean vs E95 `-0.0000162053`; beat-E95 `0.983488`; broad p95 vs E95 `-0.000001564`; Q2/S3-slice beat `1.0` | a smaller E95-relative Q2/S3 rollback tests the E100 hypothesis more cleanly than full E89. It keeps E95's structural law but reduces Q2/S3 tail amplitude | next public sensor should be E101 before E89 if the question is E95 Q2/S3 over-amplification |
| E102 E101 active-cell structure audit | E101's `50` active Q2/S3 cells converted into a row/cell atlas and tested with target-count-preserving permutation nulls | active cells/rows/blocks/subjects `50/48/26/10`; max cells per block `4`; edge-or-near-edge rate `0.620` vs null `0.471289`, p `0.016999`; mean edge distance `1.680` vs null `2.138444`, p `0.040848`; max cells per block p `0.997300`, subjects touched p `1.0` | E101 is mainly target-axis amplitude/edge-local calibration, not a hidden subject/block-local selector | no E102 submission; use E102 only to decide the branch after E101 public feedback |
| E103 edge-local Q2/S3 amplitude probe | E102 edge/active/interior/top-gap masks scanned as E95-to-mixmin rollback variants under E101's inherited stress frame | variants `180`; E103 pass `12`; E101-dominating rows `0`; best passing active-all alpha `0.375` mean/p95/beat vs E95 `-0.000023425`/`-0.000002159`/`0.980881`; E101 reference `-0.000016205`/`-0.000001564`/`0.983488`; materialized file `none` | edge proximity is a branch/risk diagnostic, not a replacement selector. Higher-amplitude active-all variants trade beat-rate for mean/p95, and edge-only masks fail p95/strict safety | no E103 public submission; keep E101 as the next public sensor |
| E104 E101 amplitude Pareto-cliff audit | E101/E103 active masks fine-scanned over alphas `0.000-0.500` by `0.005` under the same E95-conditioned transfer frame | variants `505`; E101-pass rows `228`; E101-dominating rows `0`; active-all first alpha above E101 with beat loss `0.255`; alpha `0.255` improves mean/p95 vs E101 by only `~3.02e-7`/`~2.6e-8` while beat gap is `-0.000289687`; materialized file `none` | E101 alpha `0.25` is a local Pareto point, not a coarse-grid accident. Higher rollback amplitude is an upside/downside tradeoff, not a clean successor | no E104 public submission; keep E101 as the next public sensor |
| E105 E101 public-label break-even anatomy | E101-vs-E95 hard-label deltas on the `50` active cells plus global/subject train-prior simulations | active Q2/S3 `11/39`; all-support/all-adverse deltas `-0.000096679`/`+0.000211677`; support cells needed to beat E95 `23/50`; support cells needed to match E95's mixmin edge `25/50`; S3 flip-benefit share `0.935862`; global-prior expected delta/beat probability `+0.000048971`/`0.016610`; subject-prior `+0.000007854`/`0.335360` | E101 public result is a sensor for subject/block-local S3-heavy hard labels, not global Q2/S3 prevalence | no E105 public submission; use this to interpret pending E101 LB |
| E106 E101 subject-prior gate audit | E105's subject/S3 label clue converted into subject-support, subject-expected, flip-benefit, S3-only, and prior-ranked E101 rollback gates | variants `268`; E101-pass `12`; prior-healthier `56`; interesting non-replacements `6`; replacement/dominating rows `0`; materialized file `none`; `active_s3_all` alpha `0.25` mean/p95/beat `-0.000015728`/`-0.000001195`/`0.973349` vs E101 `-0.000016205`/`-0.000001564`/`0.983488` | subject prior is useful to interpret E101's public result, but it is not strong enough to pre-mask E101 into a better file | no E106 public submission; keep E101 as the next public sensor |
| E107 E101 feedback decision map | E104/E106 follow-ups conditioned on hypothetical E101-vs-E95 public deltas inside E99 broad-plausible worlds | candidates `292`; outcomes `6`; summary rows `1752`; edge win/small win/tie within-tolerance, strong win/loss nearest/tension; edge/small wins point to E104 active-all amplitude-up; E106 masks do not outrank E104 | E101 public result should choose a branch: win -> amplitude-up E104; loss -> E99/E101 world-model tension rather than subject-prior rescue | no E107 public submission; use after E101 LB |
| E108 E101-win amplitude follow-up kit | E107 edge/small-win amplitude branch materialized into executable files | `submission_e108_if_e101win_amp050_079aab57.csv` alpha `0.500`, rank `1` vs E101 in edge/small-win worlds, not E101-pass; `submission_e108_if_e101win_strict_amp038_64514c53.csv` alpha `0.380`, E101-pass, edge/small rank `54/49` | E108 is a decision-hygiene layer, not a pre-feedback submission. It prevents post-hoc selection if E101 wins | use amp050 or amp038 only after E101 improves by edge/small-win scale |
| E109 E101 tie/loss hard-label world audit | E101 active-cell labels sampled under global/subject priors and bucketed by E101-vs-E95 active-cell outcome | subject-prior small/large loss mass `0.355350`/`0.244350`; top10 support rate falls from `0.916933` in edge wins to `0.805226`/`0.719218` in small/large losses; E108 amp050/amp038 subject small-loss active mean vs E101 `+0.000011723`/`+0.000006026`, beat-E101 rate `0` | E101 tie/loss is active-label rollback failure, not a reason to amplify the same line. Loss buckets favor E95/E90/E86 retention on active cells | if E101 ties/losses, do not submit E108/E104/E106 rescue before rebuilding the public-world model |
| E110 E101-negative non-active tail audit | Active-restored E89/E85 and E95-to-E89/E85/E90/E86 non-active grafts tested after E109's loss-side active-cell result | unique candidates `45`; active-loss-safe non-control rows `36`; diagnostic sensors `8`; strict candidates `0`; materialized file `none`; best non-control broad mean/p95 vs E95 `+0.000000714`/`+0.000002798` | E101 tie/loss does not automatically revive full E89 or non-active grafts. Restoring failed active cells helps the E109 bucket but broad E95-conditioned downside remains | if E101 ties/losses, keep E95 as standing best and rebuild before spending a slot on E89/non-active-graft fallback |
| E111 SAUNA frontier movement atlas | Submission geometry of mixmin/E72/E85/E86/E89/E90/E95/E101/E108 compared by target-axis movement and tail concentration | E72 failed with Q-share `0.450788`, S-share `0.549212`, active cells `893`, L1 `2.203482`, cosine with E95 direction `0.327033`; E95 improved with Q-share `0.019948`, S-share `0.980052`, active cells `550`, L1 `1.509562`; E101 vs E95 changes only `50` Q2/S3 cells | E95's gain is target-axis hard-tail surgery, not broad model improvement. Public-positive movement mostly removes Q/Q3/S4 contamination and keeps S-side movement plus a small Q2 component | no E111 submission; E101 remains the smallest public sensor for whether E95's Q2/S3/S3-heavy surgery is too tight |
| E112 SAUNA Q/S temporal-axis audit | Train labels and train/test calendar order checked for subject-prior, temporal persistence, and target-axis correlation asymmetry | S-target subject-LOO gain `0.068724` vs Q `0.020146`; strongest subject-prior targets `S3/S2/S1`; Q temporal persistence lift `0.135700` vs S `0.087255`; test rows bracketed by train within 3 days on both sides `0.080000`; within-S corr `0.260803`, within-Q `0.187934`, Q-S `0.030038` | S-heavy E95 surgery is plausible as subject/block-state translation. Q targets carry temporal signal, but sparse test adjacency makes direct Q/Q3 propagation unsafe | no E112 submission; keep E101 as Q2/S3 boundary sensor and avoid broad Q/Q3 temporal movement |
| E113 raw context visibility audit | Raw lifelog daily coverage/context tested as a replacement for missing Q temporal labels | raw feature count `114`; train/test raw coverage `1.000000`/`1.000000`; temporal raw+prior delta vs subject prior Q `+0.038804`, S `+0.058534`, E95-active `+0.059881`; only S3 temporal delta is favorable at `-0.004643`; Q2 random-only improvement conflicts with temporal degradation | visible raw context has ranking signal but fails calibrated temporal LogLoss after subject prior. This is a LeJEPA shortcut/collapse warning, not a submission branch | no E113 submission; raw context stays diagnostic energy and E101 remains next public sensor |
| E114 E101 raw-context support audit | Raw+subject-prior heads scored only the `50` E101 active cells by support-label probability | subject-prior beat probability `0.336655`; raw+prior `0.238325`; validation-gated raw `0.230710`; S3 flip-benefit share `0.935862`, raw S3 support `0.589463` vs subject `0.604450` | raw context cannot pre-validate the active-cell label world that would make E101 beat E95. E101 remains a public hard-label sensor, not raw-supported improvement | no E114 submission; if E101 wins, the support world was hidden from this raw-context head |
| E115 public sensor information audit | E101/E89/E85/E90/E86 compared as public sensors after E114 | E101 actionable score `1.613953`, entropy `1.728493`, beat-E95 `0.983488`; E89 actionable `0.233881`; E85/E90/E86 mostly loss-heavy | E101 remains next public slot because it is the most actionable sensor, not because raw supports it | no E115 submission; submit E101 if using one external sensor |
| E116 E101 public feedback decoder | E101 future LB mapped to pre-registered world-model bands | strong win `<=0.576261330`; edge win `(0.576261330,0.576280330]`; small win `(0.576280330,0.576288330]`; tie `(0.576288330,0.576294330]`; loss `>0.576294330` | prevents post-hoc interpretation after E101 public feedback | no E116 submission; consult decoder before any post-E101 file |
| E120 post-E101 public observation audit | actual E101 LB ingested into the pre-registered E116 decoder and loss-side audits | public `0.5763003660`; delta vs E95 `+0.0000090362`; delta vs mixmin `-0.0000062745`; E116 outcome `small_loss`; local E101 stress mean/p95/beat had been `-0.0000162053`/`-0.000001564`/`0.983488`, so actual public was `+0.0000252415` worse than local mean | E95 remains standing law. E101 was informative but negative versus frontier; the E99/E101 broad-plausible stress underestimated the loss-side public tail | no new submission; close E108/E104/E106/E119 and automatic E89/non-active graft followups, then rebuild a two-point E95/E101 public-world model |
| E124 E101-conditioned transfer audit | E99 local+tail transfer solved from E72/E95, then checked against held-out E101 public feedback | broad-plausible `3452`; broad mean predicted E101 `-0.000031516` vs actual `-0.000006275`; E101 order-match `57`; E101-plausible `57`; inside E101-plausible worlds E95 live win rate `0.929825`, E89 beat-E95 `0.052632`, E85 `0.017544`, E90/E86 `0` | E99 captures the hard-tail axis but misses the E101 Q2/S3 boundary variable; pre-E101 ranking should not select the next file | no submission; do not inherit E89/E85/E90/E86 order from E99 after E101 |
| E125 E101 survivor anatomy | E124 survivor worlds analyzed by mask/gamma/alpha/tail relation | E101 survivors `57/3452`; `q2s3` `0/368`; `all`/`e72_top50_hard` `43/57`; gamma0/deterministic `40/57`; median alpha `3.310470 -> 0.791985`; median `tail_e101-tail_e95` `-0.000012634 -> ~0` | post-E101 residual world is broad transfer-shrink/tail-neutral, not Q2/S3 diffuse-tail | no submission; lower priority of E89/Q2S3 same-line sensors |
| E126 E101 survivor cell-budget anatomy | E124/E125 survivor worlds expanded into selected E72-adverse cell budgets | E101-plausible q2s3 mass share `0.180513`; E101-active mass share `0.011234`; E95-fallback mass share `0.356179`; between-train-runs mass share `0.621562`; broad-q2s3 E101-active share `0.584840` | the E101 public sensor is not primarily charging the cells E101 changed; public-compatible residual is broad low-alpha transfer shrinkage | no submission; close E101/E89/Q2S3 same-line variants by default |
| E127 transfer-shrinkage predictability | E126 budget field compared with public-free proxy and metadata views | `broad_tail_equal` JS `0.038002`, cosine `0.945388`, top50 truth-mass `0.293969`; best metadata `target_context_tail_e72bin` CV JS `0.073253`; q2s3 JS `0.508660` | the residual field is visible as tail-neutral/low-alpha geometry, but metadata-only action is still weak | no submission; build a transfer-shrinkage representation before probability movement |
| E128 transfer-shrinkage energy audit | E127 transfer-shrinkage density converted into candidate-risk components and checked against known public anchors/live files | strong component Spearman: q2s3 rollback `0.958042`, tail-equal residual `0.888112`, E72 exposure `0.881119`, active rollback `0.874126`; composite risk only `0.440559`; live low-risk rank E85/E89/noQ2/E90/E86 | public LB sensors validate the components, not the compressed ranker. The energy explains E101 as close-but-worse but does not identify a new file | no submission; use as veto/decomposition only |
| E129 transfer-shrinkage Pareto universe audit | separated E128 veto components applied to full local/report-referenced submission universe | `116044` paths, `65865` unique tensors; strict veto `3`, strict actionable `2` = E85/E101, relaxed material adds E89, novel strict actionable `0` | the public-compatible low-veto region does not contain a hidden old successor. It is the same already-interpreted hardtail line | no submission; old-file rank search is a negative branch |
| E130 tail-density synthesis probe | E95-relative synthesis from E127 density masks and old donor directions | `1792` variants, `698` evaluated, local strict `25`, E129-veto-actionable `19`, local-strict plus veto-actionable `0`, submit gate `0` | density sees a real public-compatible field, but direct donor interpolation converts it into either local-upside/public-tail-adverse rows or safe but immaterial micro-moves | no submission; next public file needs a genuinely new movement direction, not density-only blending |
| E145 E144 public feedback decoder | future E144 public LB mapped to pre-registered branch decisions | bands: `<=0.576271330` breakthrough win, `<=0.576284330` clean win, `<=0.576289330` micro win, `<=0.576293330` tie, `<=0.576300366` fine-loss branch alive, `<=0.576306641` branch loss, `>0.576306641` hard fail | prevents post-hoc interpretation of E144's tiny E143-relative local edge | no submission; consult before any E143/E142 or boundary followup |
| E149 E144 anchor-geometry audit | E144 logit movement decomposed against hardtail, E72, E101, E142, and E143 axes | E144 changed `185` cells vs E95; cosine with E101 `-0.019625796`, E72 `-0.024358970`, E142 `0.952146833`, E143 `0.991918719`; residual ratio vs E143 `0.126874959`; Q2/S3 share `0.161603888` | E144 avoids known public-negative axes but is mostly a pruned E142/E143 residual branch, not a new broad representation direction | no submission; keep E144 as next sensor and interpret feedback as residual-branch validation/failure |
| E150 E144 post-feedback interpreter | E145 bands joined with E148 attribution and E149 geometry | `7` rows; fine-loss becomes `conditional_alive`; E143 allowed only if fine-tail/S3 attribution is the culprit; branch-loss/hard-fail block same-family rescue | scalar E144 LB is underidentified; post-public action must combine band, attribution, and geometry | no submission; run with `--score <PUBLIC_LB>` after E144 result |
| E151 plateau resolution bottleneck audit | E98/E120/E129-E150 evidence joined into a frontier-scale bottleneck table | selector p90 `0.0008164966` = `53.33x` E95 edge; E101 local optimism `0.0000252415`; E129 novel strict old candidates `0`; E130-E139 submit gates `0`; E142/E143/E144 counts `35/15/9`; E144/E143 cosine `0.991918719` | plateau is mainly selector-resolution plus decoder geometry, not missed old candidates or generic capacity | no submission; keep E144 as next sensor; next local work needs a non-collinear strict/E72/post101-safe decoder |
| E152 branch-orthogonal decoder audit | E137-E140 decoder moves projected away from E144 branch and rescored under current stress gates | source rows `4650`; projected rows `2880`; relaxed `349`; E72-budget `1208`; post-E101 `564`; actionable `122`; all-four intersection `0`; best local move `-0.0000455468` | non-collinear signal exists but current decoder gates are mutually incompatible | no submission; keep E144 as next sensor; next local target is gate-intersection failure |
| E153 gate-intersection failure atlas | E152 projected rows rebuilt and classified by missing all-four gate | projected rows `2880`; three-of-four near misses `103`; all-four `0`; `missing_actionable` `102`; `missing_relaxed` `1`; active/Q2S3 blocker `101/102`; raw/world blocker `1/1` on the lone relaxed miss; S3/S4/S2 positive target lift, Q2 absent | E152 failure is not scalar threshold looseness. The main blocker is S3 active-boundary actionability, and the only actionability-safe escape fails raw/world health | no submission; keep E144 as next sensor; next local repair must target S3 active-boundary or raw/world health explicitly |
| E154 S3 active-boundary repair probe | E153 missing-actionable rows repaired by selected S3 rollback toward E95 | source rows `102`; repair rows `7458`; all-four `10`; selected `submission_e154_s3repair_9f2e2e73.csv`; selected all-minus-E95 `-0.000012158050`; changed cells vs E95 `294`; contains all `185` E144 cells; cosine with E144 `0.983569299`, E72 `-0.031628728`, E101 `-0.005523655` | the S3 active-boundary blocker is repairable, but the repaired solution remains E144-branch geometry rather than a broad new latent | submit E154 first if using one current public slot; keep E144 as conservative contrast |
| E155 E154 branch-body ablation | E154's added E144->E154 body reduced, target-dropped, and replayed through the same health gates | rows `44`; variants `40`; all-four variants `34`; E155-submit variants `27`; reduced-body submit variants `22`; selected `submission_e155_bodytemp_d27e7965.csv`; alpha `0.25`; all-minus-E95 `-0.000010362491`; body ratio `0.25`; target-drop all-four `12/12` | E154 is not an isolated exact point; the repaired branch exists as a low-amplitude ridge, though full E154 has larger local edge | use E155 as conservative amplitude-control after E154; if E154 loses but E155 wins, blame full-body overextension |
| E156 E154 target-axis lattice | E154's Q1/Q3/S2/S3/S4 body decomposed by target-axis amplitudes and fully rescored | variants `3125`; all-four `3125`; strict `2984`; minbody below E155 `85`; selected `submission_e156_targetaxis_757546d2.csv`; axes Q1+S2+S4 with alphas `0.25/0.75/0.25`; body ratio `0.171266667`; all-minus-E95 `-0.000010004`; post-E101 p95 `-0.000003712`; E72 gap `-0.000002266`; cos E144/E155 `0.999515751`/`0.998991027` | the low-body repaired law does not need the diagonal body or extra Q3/S3 movement; it is E144 plus a tiny Q1/S2/S4 add-on | use as the third repaired-branch decomposition control after E154/E155, not as the first public sensor |
| E157 E156 axis response audit | E156 lattice finite-differenced by target axis and searched for E155-dominating low-body Pareto rows | all-four `3125/3125`; strict `2984`; Q3 local finite-diff `-0.000000383335`; Q3 post-E101 finite-diff `-0.000000132956`; S2 E72-gap finite-diff `-0.000000714955`; E155-dominating lowbody rows `3`; selected `submission_e157_lowbodypareto_bd67930d.csv`; axes Q1+Q3+S2+S4; body ratio `0.240336139`; all-minus-E95 `-0.000010404446`; post-E101 p95 `-0.000003807382`; E72 gap `-0.000001671496` | E156's Q1/S2/S4 minimum is a body-selection artifact; Q3 is favorable but expensive in body norm, and all-four gates are saturated | optional tuned low-body Pareto control after E154/E155; not a first sensor and not a new target law |
| E158 repaired branch public decoder | E154/E155/E157/E156/E144 converted into a pre-registered public-feedback decision table | E154-vs-E155 local gap `-0.000001795559`; E154-vs-E144 `-0.000002432120`; E157-vs-E155 `-0.000000041955`; E156-vs-E155 `+0.000000358921`; E155/E157/E156 cosines vs E144 `0.998962769`/`0.999041566`/`0.999515751`; score-band table written to `e158_repaired_branch_public_decoder_bands.csv` | sibling controls are below public-readable separation before feedback; E154 is first for interpretability against E144, not because it is score-distinguishable from E155 | use E154 result to choose whether E155 is justified; do not rescue hard-failed E154 with E157/E156 micro-controls |
| E159 E154 public outcome attribution | E154-vs-E95 decomposed into additive LogLoss segments and simulated through E158 bands under public-free priors | unique cells/segments `294/479`; rows/subjects `139/9`; component flip-benefit inherited E144 body `3.292000000`, E154 extra body `0.255975083`, E154 adjustment `0.203843941`; win mass global/subject/nearest-hard `0.728550`/`0.601575`/`0.666680`; branch-or-worse `0.222590`/`0.336125`/`0.259610`; direct hard-delta max error `<2e-16` | E154 is still the next sensor, but a non-win is underidentified without attribution. Loss-side blame is usually inherited-body, not added-body, so E155 is conditional rather than automatic | after E154 public feedback, combine E158 band and E159 attribution before choosing E155/E144/branch close |
| E160 E154 post-feedback interpreter | E158 score bands and E159 attribution converted into a score-to-action command | `7` decision rows; E155 gate `not_needed` for wins, `information_only` for tie/small_loss, `not_recommended` for branch_loss/hard_fail; score probes `0.5763003660 -> small_loss`, `0.5762880000 -> micro_win` | future E154 feedback now has an executable guardrail, preventing scalar band-only rescue logic | run `python3 analysis_outputs/e160_e154_postfeedback_interpreter.py --score <PUBLIC_LB>` after E154 result |
| E163 candidate edge breadth audit | known public transitions and live post-E95 candidates converted to hard-label swing breadth | mixmin-vs-a2c8 actual delta needs `25` top cells; E95-vs-mixmin needs `1`; E101-vs-E95 needs `1`; E72 miss needs `4-6`; live post-E95 files have `7/7` one-cell `2e-6` fragility | mixmin was broad, but E95-era refinements are hidden-label-resolution limited; E101's `0.5763003660` result is a narrow-cell boundary observation, not a broad Q2/S3 law | no new submission; keep E154 as the next sensor and require future candidates to beat top-cell fragility or recover another broad signal |
| E164 universe broad edge screen | tracked submission universe scanned for broad E95-relative hard-label edge | `2052` paths, `1977` unique tensors, `198` broad-edge rows, `192` conservative candidate-gate rows; top broad row focus expected delta `-0.025880912`, cells-to-flip `54` | an existing broad post-E95 branch exists, but broadness alone admits known public-bad rows | do not submit raw broad rows; pass through E165/E166 |
| E165 broad edge bad-axis geometry | E164 broad candidates checked against known public-bad axes | `205` rows scored, `192` candidate rows, `90` geometry-health survivors; known public-bad broad controls fail geometry health | broad branch is not fully explained by known bad/collapse axes, but raw amplitude remains unsafe | shrink survivor directions before any submission |
| E166 broad survivor scale probe | E95-to-E165-survivor tiny logit steps tested for broadness and geometry | `198` scaled rows, `112` sensor-gate rows, `51` material rows with scale `<=0.03`, negative-control gate `0`; selected `submission_e166_broadsurv_s0p01_d8bfa94b.csv` with expected delta `-0.000332077`, cells-to-flip `74`, top1/expected `0.023369627`, bad-span energy `0.450742441` | first post-E95 broad small-amplitude escape sensor. A win would strengthen the broad latent branch; a loss would expose missing bad-axis geometry | use as broad plateau-break public sensor; E154 remains conservative repaired-branch sensor |
| E167 broad survivor context alignment | E166 focus cells tested against hidden context and safety-atlas nulls | top-benefit focus cells are context-enriched: edge-like `0.689189` vs null `0.470842`, between-train-runs `0.797297` vs `0.624658`; but safety-divergent: veto-null `0.297297` vs `0.574158`, safe-density `0.117097` vs `0.243966`, E72-active `0.837838` vs `0.670369` | E166 is context-real but not safety-certified. Public E166 would be a safety-atlas falsification sensor, not a safer expected-score file | do not scale E166 before feedback; try context/safety separation first |
| E168 safety-context decoupling | E166 context signal and safety divergence tested for separability by local masks | decoupling-pass policies `2`; `context_high__veto` expected delta `-0.000120457`, cells-to-flip `32`, top1/expected `0.048415`, edge `0.610619`, between `0.819690`, veto `1.0`, safe-density `0.346150`, E72-active `0.268805`; high-density p50 near-tied | the strongest negative E167 interpretation is false: context signal and safety divergence are not fully inseparable | materialize context-high safety mask before treating raw E166 as the default broad sensor |
| E169 context/safety mask materializer | E168 masks converted to actual E95-relative submission tensors and rerun through breadth/bad-axis stress | materialized `submission_e169_ctx_veto_c5e806e3.csv` and `submission_e169_ctx_high_density_p50_51110c7e.csv`; ctx-veto expected delta `-0.000120457`, moved cells/rows `904/193`, bad-span energy `0.295326`, max bad cosine `0.222381`, mean/max logit `0.001096`/`0.010206` | balanced broad repair exists locally: less upside than raw E166, but lower amplitude and safer atlas geometry | next broad public sensor should be `submission_e169_ctx_veto_c5e806e3.csv`; raw E166 only if deliberately testing the atlas as overconservative |
| E170 E169 public feedback decoder | E169 public interpretation fixed before any E169 LB is known | bands written to `e170_e169_public_feedback_decoder_bands.csv`; E169-vs-E95 expected delta `-0.000120457`, cells-to-flip `32`, top1 swing `0.000005832`, cells for `2e-6` guard `1`, cells for E95 edge `4`; between-train-runs share `81.1%`, not-E72-active share `73.7%`; high-density sibling differs by only `10` cells | E169 is broad and safer than raw E166, but still public hard-label-resolution limited. Its LB must be decoded by pre-registered bands, not post-hoc tuned | after submitting E169, run `python3 analysis_outputs/e170_e169_public_feedback_decoder.py --score <PUBLIC_LB>`; do not submit high-density p50 before ctx-veto feedback |
| E171 E169 critical-cell prior audit | E170's public-decisive cells checked against global/subject/flank priors before E169 LB is known | full visible_mean body mean `-0.000022659`, win `0.868840`; subject win `0.853520`; flank_mean win `0.480740`; top1 support `0.098648`, top4 `0.330699`, top32 `0.247434`; top32 below target-matched null mean `0.353573`, `z=-2.703` | E169's broad body is visible-prior favorable, but the high-swing cells that can decide public are visible-prior adverse. This explains why E169 is high-information but not a stable expected-score claim | if E169 loses narrowly, diagnose critical-cell tail adversity before closing the broad branch; do not prune top cells without rerunning breadth/readability stress |
| E178 current plateau law audit | fixed E101 public `0.5763003660` joined with E95/mixmin anchors, E162 readability, E165 bad-axis geometry, E177 E176 contrast, and E98 selector error | E101 is `+0.0000090362` vs E95; E166 expected edge `-0.000332077` = `21.689x` E95 edge; E176 expected edge `-0.000123384` = `8.059x`; E176 needs `4` top cells and E101 `2` cells to cover the E95 edge; selector p90 is `53.33x` the edge | public plateau is broad-signal plus hard-label-resolution law: signal exists, but target-tail/public-cell realization and validation resolution dominate post-E95 ranking | no submission; keep E176 as the next single public sensor and decode with E177 before any same-family follow-up |
| E183 pressure-world branch anatomy | E182 favorable/adverse pressure worlds joined with train-derived visible/subject/flank priors on differing candidate moved cells | visible-mean favorable-branch preference E176/E154/E144 `0.000/0.000/0.000`; subject and flank also `0.000`; support-gap coefficient-weighted means E176 `0.797945`, E154 `0.973558`, E144 `0.888923`; E176 global prior alone favors the min branch in `1.000` scenarios | visible priors are public-free diagnostics but anti-selectors for current pressure branches; public LB will be needed as a sensor unless a new decisive-cell representation is built | no submission; do not rank E176/E154/E144 by visible-prior branch preference |
| E184 public-anchor motif selector | known public transition cells used as support-compatible/incompatible motif supervision, then scored on E183 pressure branches | best direct pair-LOO sign/AUC `0.333`/`0.425`; best direct family sign/AUC `0.600`/`0.178`; polarity-inverted pair can reach `1.000` but family best-polarity only `0.600`; live branch preference flips by feature set (`0.000` for core/swing, `1.000` for public-axis variants) | shallow metadata motifs over known public anchors are not stable hidden-world selectors; public-axis residue can flip decisions without held-out reliability | no submission; do not rank live files by E184 motif score |
| E191 boundary-aware E72 score | exact E95/E101 used as hard negatives in filename-free E72 contamination scoring | best clean pair-LOO row `shape_target_context_abs/plain_logit_c025`: AUC `0.978836`, AP `0.809524`, top-k recall `0.666667`, exact E95/E101 mean `0.057658`; support-containing clean rows `0`; support-rich exact E95/E101 probability remains `~0.766..0.839`; E176 contamination near zero | hard-negative weighting/prototypes do not rehabilitate support. Exact-boundary safety currently belongs to shape/target/context, not support | no submission; E176 remains shape/broad-Q2-underopen sensor; no support-gated variant |
| E206 E176 public observation | `submission_e176_abl_q2_to0p75_91e49725.csv` submitted as the E176 broad/Q2-underopen sensor and decoded with E205 | public LB `0.576311831`; delta vs E95 `+0.0000205012`; delta vs mixmin `+0.0000051905`; E205 outcome `branch_loss`; follow-up role `body_exit_counterworld`; selected follow-up file `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` | broad partial-reopen gives back the frontier edge; same-family expected-score followups E176/E174/E172/E169 are weakened. This is not Q2-only feedback because E176's expected body was mostly S-stage / between-train-runs | do not submit E174/Q2 sibling or E172 safety next. If spending an existing-file slot, E154 is the coherent counter-world; otherwise search non-collinear structure |
| E216 masked-family JEPA S2 public observation | `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` submitted as the masked-family JEPA S2-only survivor; observed `2026-05-30 16:14:15` | public LB `0.5772865088`; delta vs E95 `+0.0009951790`; above the E238 E216-like collapse threshold for E237 routebooks | the S2 masked-family JEPA representation was locally real but public-adverse when translated into probabilities. The failure is too large to treat as frontier noise or one-cell tie | close remaining E216 siblings as submissions; keep E216 only as a bad-axis/negative-control anchor and use its miss as a support-tail capacity bound |

## Next Public-Observation Experiments

1. E247 feature-NN1 Q3 smoothing frontier: keep `analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` as the current public anchor. Its `0.5761589494` score validates the combined E224-body plus Q3 feature-neighbor rollback branch and should replace E95 as the operational frontier.
2. E256 high-amplitude smoothing follow-up: `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` asks whether E247's broad top34 smoothness is necessary or whether high-amplitude smooth cells are enough. This is the first post-E247 score-plus-information candidate, not a sibling sweep.
3. E224 clean body attribution: `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv` asks whether E247's win mostly came from the E224 body. Use this if attribution is more valuable than immediate score pressure.
4. E95 hard-tail localized public frontier: resolved as previous public anchor. Keep `analysis_outputs/submission_e95_hardtail_541e3973.csv` for contrast, but no longer treat it as the current score frontier.
5. E176 risk-adjusted E174-family broad candidate: resolved. `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` public LB `0.576311831` lands in E205 `branch_loss`. It is worse than E95 by `+0.0000205012` and worse than mixmin by `+0.0000051905`, so same-family broad reopening is no longer an expected-score follow-up lane.
6. E174 rollback-overcorrection broad max-edge contrast: demoted after E206. Use only if deliberately asking the narrow Q2 full-reopening question, not as a rescue or expected-score follow-up.
7. E172 visible-positive-loss rollback broad contrast: demoted as immediate follow-up after E206. It was reserved for E176 tie/small-loss safety; the observed E176 branch-loss routes to E154/search instead.
5. E101 Q2/S3 tail rollback sensor: resolved. `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` public `0.5763003660` is E116 `small_loss`: worse than E95 by `0.0000090362` but still better than mixmin by `0.0000062745`. This closes the automatic E108/E104/E106/E119 follow-up path and says the next step is model rebuild, not same-family amplitude tuning.
6. E169 balanced broad repair sensor: `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv` asks the sharper body-vs-critical-tail question before rollback. After E172, it is no longer the first expected-score broad candidate, but remains useful if we deliberately want to observe whether the raw broad body beats visible-tail adversity. Interpret with `analysis_outputs/e170_e169_public_feedback_decoder.py --score <PUBLIC_LB>`.
7. E166 raw broad survivor sensor: `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv` asks whether E95 is missing a broad latent branch rather than only narrow hardtail repairs. It is a `1%` E95-to-broad-survivor logit step, not a raw JEPA submission. E167 makes the public read sharper: the file is context-real but safety-atlas divergent. Submit it after/over E176/E174/E172/E169 only when deliberately testing whether the safety atlas is overconservative.
8. E154 S3 active-boundary repaired sensor: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` asks whether E95 can be extended by the E144 residual branch after explicitly repairing the S3 active-boundary gate that killed E152. A win strengthens the repaired all-four worldview; a loss with later E144 win blames E154's added branch body or exact rollback; losses for both close the branch.
9. E155 lower-amplitude E154 ridge sensor: keep `analysis_outputs/submission_e155_bodytemp_d27e7965.csv` as the conservative amplitude-control contrast. It asks whether the repaired E154 law survives with only `25%` of the added body. If E154 loses but E155 wins, blame full-body overextension rather than S3 repair.
10. E157 tuned low-body Pareto control: keep `analysis_outputs/submission_e157_lowbodypareto_bd67930d.csv` as the target-axis-tuned low-body contrast. It asks whether a Q3-including low-body row that slightly dominates E155 locally transfers to public. Do not submit before E154/E155 unless the explicit question is tuned target-axis control rather than clean amplitude interpretation.
11. E156 minimum target-axis repaired control: keep `analysis_outputs/submission_e156_targetaxis_757546d2.csv` as the low-body decomposition contrast. It asks whether only a tiny Q1/S2/S4 add-on over E144 is public-real.
12. E144 fine active-boundary transferclip sensor: keep `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the conservative unrepaired same-branch contrast. It asks whether E95 can be extended by transfer-budget-neutral residual movement without E154/E155/E157/E156 repaired body detail. Interpret any E144 result with `analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>` before followup.
13. E143 active/Q2S3 repaired transferclip sensor: keep `analysis_outputs/submission_e143_activeq2s3repair_68ca656f.csv` as the stricter fallback. It asks the same residual-decoder question as E144, but with full rollback of top21 Q2/S3-weighted cells.
14. E142 transfer-budget clipped sensor: keep `analysis_outputs/submission_e142_transferclip_09a92236.csv` as the higher-upside fallback, not the first submission. It has slightly better local/post-E101 stress than E143/E144's conservative movement family, but fails the active/Q2S3 strict veto.
15. E89 E72-decontaminated public sensor: do not auto-submit after E101 loss. Use `analysis_outputs/submission_e89_e72decontam_00d7807f.csv` only as a deliberate diffuse-tail sensor if the explicit question is whether public prefers E89's broader E72-cell fallback law despite E110's negative non-active graft stress.
16. E85 conservative target-pruned structural fallback: submit `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv` only if the sharper question is lower-amplitude `S1,S2,S3` correction without E86's consensus overstep/Q2 add-back, or if pure downside floor is prioritized.
17. E90 E72 Pareto-knee public sensor: submit `analysis_outputs/submission_e90_e72pareto_28925de5.csv` only if the explicit question is row-coherent structural retention after removing the worst E72 rows. E99/E101 make it a weak expected-improvement bet over E95.
18. E86 source-consensus target-pruned public sensor: submit `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv` if using one public slot for maximum upside and willing to accept much higher hard-tail downside than E95. E99 makes its E95-beat probability negligible under the local+tail abstraction.
15. E98-E120 selector updates: adding E95 to known anchors still leaves movement regression too coarse, conditioning E96 tail worlds on E95 keeps E95 best, E89's remaining pocket is Q2/S3-specific, E101 shows a smaller Q2/S3 rollback can isolate that pocket, E102 rejects strong block/subject-local active-cell concentration while preserving a weak edge-local calibration signal, E103 rejects direct edge-only replacement, E104 rejects higher-alpha replacement before public feedback, E105 rejects the global-prior interpretation of E101, E106 rejects subject-prior gating as a pre-feedback replacement, E107 pre-registers the branch after E101 feedback, E108 materializes only the E101-win branch, E109 rejects same-line rescue after E101 tie/loss, E110 rejects automatic non-active E89/graft fallback after E101 tie/loss, E111 reframes E95 as target-axis hard-tail surgery, E112 explains the axis split as S subject-state versus Q temporal-state with weak test adjacency, E113 rejects visible raw context as a broad Q temporal rescue, E114 rejects raw context as E101 active-cell pre-validation, E115 keeps E101 as the highest-actionability sensor, E116 pre-registers the exact LB decoder, and E120 applies the actual E101 `small_loss` feedback. Choose the next file by the hidden-world question being tested, not by a proxy-predicted LB or post-hoc score interpretation.
16. E87 contrast sensors after E86 feedback: use exactly one of `analysis_outputs/submission_e87_noq2_source_consensus_a85c4e39.csv`, `analysis_outputs/submission_e87_q2_nooverstep_consensus_acd7add0.csv`, or `analysis_outputs/submission_e87_inverse_top_prior_consensus_5445ec28.csv` if E86 fails and the next question is which E86 risk axis survived.
17. Structural block target representation: raw overnight context can recover strict pseudo-hidden block state, but target-rate smoothing, raw posterior averaging, simple E56 distillation, within-block joint labels, transition residual hidden-sign moves, transition-gated E56 teacher movement, gradient-consensus gating, and scalar amplitude expansion cannot align it at selector-scale margin. The next JEPA-style target should encode block topology/transition/label-world constraints while preserving row calibration and S3.
18. Independent non-anchor E56 validation: E63 shows hidden-rate gradients validate E56 direction, E64 shows scalar amplitude is adverse, E65 says the best near-zero pocket is `no_q2_s3` but sub-margin, E66 says Q2/S3 add-back is hidden/mean-favorable yet worst-tail adverse, E67 says first-order tail gates improve but remain below margin, E68 validates many of those Q2/S3 cells outside same-anchor construction, E69 shows simple alpha amplification still fails, E70 shows consensus can barely clear local margin, E71 shows a unified reconstruction can preserve one strict row but no deployable sign gate, E72/E73 show sparse-magnitude `top_abs50` can create a deployable diagnostic file, E74 says that file is not single-cell fragile, E75 says the amplitude ridge is S3-heavy/Q2-low rather than symmetric, E76 says that S3-heavy direction is subset-stable while exact `8/28` deployability is partial, E77 says source-subset posterior averaging is not enough, E78 says source-subset reliability masks are not enough, and E79 says handcrafted row/block/flank masks are not enough either. E80 then shows the submitted E73 combined file is public-adverse, E81 shows the isolated E73 Q2/S3 graft is only loose/sub-margin while inverse-sign variants fail, and E82 shows the broader pure Q2/S3 source universe is still margin-limited. The next public observation should not be E74/E75 amplification or pure Q2/S3 grafting; it should test a broader structural/block-state candidate that uses Q2/S3 as energy.
19. Target sensitivity probe: mixmin delta를 target groups별로 분리해 which target movement explains the new public order를 추정한다.
20. Next candidate generation should be mixmin-relative, not a2c8-relative: preserve the anchor-loss/binary-world direction while reducing private risk and identifying whether inverse7/raw-structure or subject-calendar block context can be blended without losing the new public gain.
21. Lower-risk S4+Q3 probes such as `analysis_outputs/submission_label_flow_focused_1bbfb735.csv` are now secondary diagnostics, not the next default public test. They should be revisited only after mixmin-relative selector calibration.
22. Public LB inverse fitting and simple subject/order/date/raw-domain masks remain underidentified. E48 adds a strong new anchor, but it does not by itself make inverse-LB optimization safe.
23. Block-state oracle evidence still explains why 0.54 feels far despite this improvement: the hidden rate vector exists, but current observable proxies do not identify it. Public submissions should not be expected to jump unless they change block-state inference or explicitly test a newly calibrated sensor worldview.
24. Current block-summary Ridge context is not that change. E47 moves only `0.014083` of the oracle gap and worsens direct block-rate loss, so it should be treated as a negative local sensor rather than a candidate source.
25. E154/E155/E157/E156 turn the E153 S3 blocker into a concrete public sensor stack, and E158/E159/E160 fix how to read it: do not relax gates globally and do not act on scalar score band alone. Submit the repaired full-body file first if testing this branch because it is readable against E144. After feedback, run E160. Use E155 only if E160 allows it; use E157/E156 only as target-axis controls after E155. If E154 hard-fails above mixmin or blame is inherited E144 body, do not rescue with E157/E156.
26. E224 is now the preferred JEPA-family observation if spending one JEPA slot. It replaces E223 q3_scale `0.75` with q3_scale `0.625` on the same E211 S4 dependency-gated body. The selected file is `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`; local/geometry/support-tail metrics are local delta `-0.001098893`, geometry `-0.000505582`, expected focus `-0.000623352`, adverse `0.003400775`, support `0.465984`, Q3 top1/expected `0.875120`. If this wins, read it as support for "S4 body plus capped-Q3 residual"; if it loses materially, demote the current E211 probability translator and keep JEPA axes as diagnostics.
27. E225 locks that interpretation before public feedback. After an E224 score is known, run `python3 analysis_outputs/e225_e224_public_feedback_decoder.py --score <PUBLIC_LB>`. Clean win is `<=0.576276019`; tie is `0.576288330..0.576294330`; small loss is up to E101 `0.576300366`; mixmin-safe loss is up to `0.576306641`; worse than mixmin closes the current E211-family expected-score lane. E224 is highly collinear with E223/full E211 and almost orthogonal to E216 S2 miss, so it is a capped-amplitude translator test, not a new JEPA family.

28. E229 updates the machine-readable public anchor ledger after the E176 and E216 observations. `analysis_outputs/public_probe_observations.csv` now includes `submission_e176_abl_q2_to0p75_91e49725.csv` at `0.5763118310` and `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` at `0.5772865088`. Rerunning `analysis_outputs/public_anchor_bottleneck_decomposition.py` gives a 14-anchor proxy where the best model is still `raw05_a2c8_compat`, MAE `0.000496259`, p90 `0.000695363`. This is still too coarse to choose the next frontier file by expected score. The public-LB lesson is therefore procedural: use E224 if the next public observation is the JEPA question, use E166 if it is the independent broad-world question, and keep E154 conditional. Do not convert the 14-anchor proxy into prior tweaking or a blind tri-world blend.

29. E236 is a local negative sensor, not a public observation. It tests whether E234 Q3/S4 learned tail masks can become an E224 submission. The answer is no under public-free geometry: `0/92` graft rows pass and no file is materialized. This strengthens the read from E216/E221/E231/E235: JEPA latents can be real and locally useful while their probability materialization fails hard-label support geometry.

30. E237 is a local positive sensor after that negative. It tests a sharper JEPA target: row-target-cell decisive Q3/S4 risk rather than row-level support. The top local file is `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`; it passes OOF, graft-vs-E154, and actual-vs-E95 public-free stress, with expected loss vs E224 `-0.000005612`, adverse reduction `0.000576400`, actual-vs-E95 adverse reduction `0.000553281`, and Q3 top1/expected `0.747139811`. If submitted, read its public score as a test of whether the hidden public tail is a learned Q3 decisive-cell law. No public LB is known yet.

## Derived Local Sensor Updates After E186

| experiment | sensor | local observation | hidden-world read | next action |
|---|---|---|---|---|
| E237 cell-level decisive JEPA target | OOF decisive-cell risk over Q3/S4 cells applied to E224/E154 tensor | selected `7` files; top drops `25` Q3 cells and `0` S4 cells; expected loss vs E224 `-0.000005612`; adverse reduction `0.000576400`; actual-vs-E95 adverse reduction `0.000553281`; Q3 top1/expected `0.747139811`; E230 risk-top21 overlap `11` | E236 failed because row-level support was too coarse. The live learned JEPA object is Q3 cell-tail decisiveness, not S2/S4 row support | submit top E237 only if testing learned Q3-tail translation; use E224 for clean unpruned JEPA and E230 for hand-prune control |
| E236 Q3/S4 tail-contrastive materialization | E234 Q3/S4 high-impact masks applied to E224/E154 tensor | graft gate `0/92`; files `0`; best Q3 adverse reduction `0.000329753` but support `-0.004017252` and Q3 top1/expected `3.054720`; best S4 support gain `0.006519636` but expected loss `0.000166178` | learned Q3/S4 tail masks do not match the public-free E230/E224 tail geometry; local JEPA target success does not imply submission-safe translation | no submission; keep E224 as clean JEPA sensor and E230 as conditional hand-prune |
| E185 known-LB pair structural decoder | all known public LB pairs, including E95/E101/mixmin/E72 and bad JEPA controls | best file-LOO `shape_support_public_axis`: accuracy `0.811`, frontier `0.833`, E95-edge `0.714`; best pair-LOO E95-edge `0.786`; reciprocity MAE `0.081/0.146` on E95-edge | known public pairs contain signal, but unconstrained pair geometry collapses orientation and branch choice flips by feature set | no submission; require antisymmetric geometry before using this sensor |
| E186 antisymmetric pair decoder | antisymmetric z-feature pair decoder over the same known public anchors | best file-LOO `shape_support`: accuracy `0.795`, frontier `0.867`, micro `0.8125`, E95-edge `0.857`, reciprocity `0`; pair-LOO `shape_only` E95-edge `1.000`; E176 branch selected `3/3`, E144/E154 rejected `3/3` | E185's failure was partly representation geometry. E176 is now supported by a reciprocity-healthy known-LB sensor, but support models still miss the E95/E101 boundary | if using one slot, E176 is the highest-information sensor; decode with E177 and do not tune siblings from one scalar score |
| E187 E95/E101 boundary anatomy | exact E95/E101 public boundary using E101 public `0.5763003660` | shape-only gets E95/E101 correct; every support-containing ablation tested flips E95/E101, often with E95 probability near `0.002..0.050`; support adverse contribution is spread across flank/visible/subject/focus/nearest/global/all-prior families | support features are not a removable bug; they encode a conflicting shortcut that helps wider edge stress while failing the tight frontier boundary | keep support scores as sensors only; do not let them rank candidates without an exact-boundary veto |
| E188 shape/support logit blend | low-alpha blend of shape-only and support decoder outputs | action-grade rows `0`; for all support variants, best exact-boundary row is `alpha=0`; first E95/E101 failure at alpha `0.170..0.285`; edge accuracy does not improve before failure | support is not a weak prior that can be safely mixed into shape geometry; it is a conflicting latent view | no blend submission; next useful work is a new decisive-cell/structural representation |
| E189 shape/support disagreement atlas | row-level disagreement audit between shape-only and support antisymmetric file-LOO predictions | in primary E95-edge slice, support rescues `6` rows and shape-only wins `4`; support rescues are E72-frontier-neighbor at rate `1.000`, while shape-only wins are exact E95/E101 at rate `1.000`; file-identity gate reaches E95-edge `1.000` but is not deployable | support's useful known-LB gain is E72-contamination correction, not broad frontier selection; tight hardtail boundary remains shape-only | keep E176 only as broad/Q2-underopen plus shape-only-supported sensor; build a structural E72-contamination detector before reusing support as a gate |
| E190 E72 contamination detector | absolute z-feature detector for E72-neighbor contamination, excluding file names as inputs | best pair-LOO `shape_target_context_abs` AUC `0.978836`, AP `0.809524`, top-k recall `0.666667`; any-file LOO skips `6` E72-positive rows when E72 is fully held out; support views score exact E95/E101 as contamination at `~0.957..0.975`; live E176 contamination is near zero | movement-shape has E72 diagnostic signal, but support-containing detectors reproduce the tight-boundary shortcut; E176 is not E72-contaminated under this sensor | no submission; E190 weakens support-gated E176 and leaves E176 as a shape/broad-Q2-underopen sensor |
| E197 public support-mass inverse | known public pair deltas inverted into `delta = adverse_sum - q * swing_sum`, then known slippage applied to live candidates | E72 visible adverse slippage `-0.071348`/`-0.120707`; E176 visible/focus surplus-to-tie `0.061761`/`0.094836`; E176 visible stress clean `4/6`, win `4/6`, branch/hard fail `1/6`; E154/E144/E155 visible surplus only `0.010284`/`0.011545`/`0.011227` and branch/hard fail `4/6` | E176's live failure mode is now specific: it loses if public hidden labels behave like E72-like adverse slippage. Repaired-branch sensors are thinner-margin counter-worlds, not better first sensors | no submission; keep E176 as next public sensor, use E172 only as safer same-family contrast after tie/small-loss, and route severe loss to E154/search |
| E226 non-collinear post-E224 scan | documented/materialized submissions after E216 public miss and E224 routebook | evaluated `73` files; top actionable independent sensor `submission_e166_broadsurv_s0p01_d8bfa94b.csv` with score `1.686847`, cos(E224) `0.074348`, cos(E216) `0.055999`, cos(E72) `0.108706`, expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`; repaired branch cluster next, with E154 as conservative counter-world | after E216, do not route to masked-family S2 variants; after E224, do not route to same Q3/S4 JEPA siblings as independent evidence. E166 is the broad independent worldview sensor; E154 is the conservative repaired-branch worldview sensor | no new submission yet; if E224 fails or if one non-E224 worldview slot is needed, choose E166 for information-rich broad-survivor test or E154 for conservative repaired-branch test |
| E227 E166 public-feedback decoder | `submission_e166_broadsurv_s0p01_d8bfa94b.csv` | routebook created; E166 moves `1750` cells over `250` rows and all `7` targets; top-benefit context edge-like `0.689189`, between-train-runs `0.797297`, E72-active `0.837838`, all-veto-null `0.297297`; candidate roles split E224/JEPA, E166/broad, E154/repaired branch | E166 is a sensor for safety-atlas overconservatism versus E72-active hidden-tail danger. It is not a file to scale or clone before feedback | after E166 score, run `python3 analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>` |
| E240 E237 residual-rule ablation | deterministic E239 residual-energy Q3 rollback rules | all `9/9` non-control simple selectors pass E237-like stress; best `simple_pc10_top25` expected loss vs E224 `-0.000062119`, adverse reduction `0.000594489`, support gain `0.016747154`, actual adverse reduction `0.000573879`, overlap with E237 `14/25` | E237's local success is not uniquely learned. The public-observation question is now Q3 residual-energy cell-tail reality, not E237 classifier superiority | no submission from E240; validate residual PC10-like Q3 cells on train/OOF before materializing a simple-rule candidate |
| E241 residual PC10 OOF validation | E240 residual-energy scores checked against train OOF Q3 benefit | no full-train top-k score has negative selected-benefit delta; `score_pc10` top-10% is adverse (`+0.001867628`), split-stress top-10% is also adverse (`+0.002633171`, win rate `0.30`); test `score_pc10` still overlaps E237 `14/25` and E230 swing25 `18/25` | residual energy is a visible Q3 motif but not an OOF-valid harmful-row selector. The E240 simple-rule submission branch is closed; E237 remains the learned-cell sensor if that public question is worth asking | no submission from E241; do not submit simple residual-PC10 rules without a rebuilt OOF decisive-cell target |
| E242 E237 OOF-to-test transfer audit | E237 materialization rows ranked by OOF gain, OOF tail-AUC, and test stress | gate pass `7/120`; top E237 file ranks `71/120` by OOF gain but `1/120` by OOF tail-AUC, support gain, and Q3 top-cell safety; OOF gain gate AUC `0.426043`; OOF tail-AUC gate AUC `0.958913` | E237 is not a generic OOF-CV winner. Its meaningful local claim is high-impact Q3 tail discrimination plus public-free support/top-cell survival | no submission from E242; if E237 is submitted, read it as a high-impact tail sensor and do not pick siblings by OOF gain |

## Update After E259

`submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` remains the current public anchor at `0.5761589494`. E259 adds no new public LB, but it changes how the next public LB should be used.

- E256 score should be treated as the sensor for broad top34 smoothness versus high-amplitude constrained Q3 rollback.
- E224 score should be treated as the sensor for whether the E224 capped-Q3/S4 body carried E247.
- Routebook file: `analysis_outputs/e259_post_e247_observation_routebook_report.md`.

Pre-registered thresholds:

- E256 clean win: `<=0.576155949`.
- E256 near loss: `0.576161949..0.576188949`.
- E256 hard loss: `>=0.576291330`.
- E224 body tie/micro-win: `<=0.576161949`.
- E224 rollback-helped: `0.576161949..0.576291330`.
- E224 body-only loss: `>=0.576306641`.

Interpretation policy: do not use the next public score as a generic rank signal. Decode it as one of the routebook worlds, then choose the follow-up that falsifies the remaining branch.

## Update After E260

No new public LB was added. E260 refines how the next public observation should be interpreted.

- E256 expected penalty versus E247: `+0.000019101`.
- E224 expected penalty versus E247: `+0.000066519`.
- E256 is still the next score-plus-information file because its expected downside is smaller.
- The E256 downside is concentrated in `4` high-amplitude added Q3 cells, not in deletion of the `13` E247-only broad cells.
- E224's downside is mainly the removal of the `21` common rollback cells.

Public decoding addition: if E256 is worse than E247, do not immediately conclude that E247-only broad smoothness was the cause. First test whether the four E256-only high-amplitude cells were public-adverse. If E224 ties or beats E247, interpret that as evidence against the common rollback core and for body sufficiency.

## Public Observation: E256

- submission file: `submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`
- public LB: `0.5762805676`
- expected LB reaction: E256 was the score-plus-information follow-up for broad-vs-amplitude feature-NN1 Q3 smoothing.
- actual LB reaction: worse than E247 by `+0.0001216182`, but still better than E95 by `-0.0000107622`.
- E259 decoding: `same_family_loss`.
- interpretation: high-amplitude constrained smoothing loses the E247 edge. This strengthens E247 exact top34 / body-plus-rollback interaction and weakens E256-like high-amplitude sibling sweeps.
- unresolved: E256 loss does not prove the `13` E247-only broad cells alone caused E247's win; E260 still marks the `4` E256-only high-amplitude additions as the first suspect.
- next experiment: E224 only if body attribution is the explicit question; otherwise refresh non-collinear candidates with E247/E256 included as public anchors.

## Public Observation: E267

- submission file: `submission_e267_humansocial_tail_balanced_2936100f.csv`
- public LB: `0.5763294974`
- expected LB reaction: the file tested whether human/social lifestyle gates could safely choose a balanced E224/E154-style Q3/S4 tail rollback.
- actual LB reaction: worse than E247 by `+0.0001705480`, worse than E95 by `+0.0000381676`, and worse than mixmin by `+0.0000228569`.
- interpretation: public rejects this specific social-gated rollback materialization. The loss does not kill the broader social-state hypothesis because the file translated the story through an old E224/E154 branch rather than directly through the current E247 frontier.
- unresolved: we still do not know whether social/context features identify the public tail, only that the chosen rollback action was too blunt or pointed at the wrong probability body.
- next experiment: build a human/social hypothesis atlas that tests stories as falsifiable signals first; only materialize a direct E247 overlay if a story survives OOF, subject/block stress, train/test shift, and E267 movement-context checks.

## Public-Free Observation: E284

- submission files: `analysis_outputs/submission_e284_appentropy_decisive_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is being preserved; E284 failed the local E247-current matched row/subject/dateblock placebo governor.
- local observation:
  - E237 gate passes: `9`;
  - public-free ready files: `0`;
  - best E247-current p90: `+0.000025223`;
  - matched-placebo gate passes: `0/9`;
  - top selected Q3 overlap with E247: `11/25`, Jaccard `0.229167`.
- interpretation: app-entropy is useful as JEPA context, but the materialized E224/E154 rollback target is stale relative to the current public-best E247 smoothing body.
- next experiment: learn E247-relative preserve/undo/avoid cell labels and keep public LB unused until a candidate beats matched nulls locally.

## Public-Free Observation: E285

- submission files: `analysis_outputs/submission_e285_e247resid_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E285 failed the local E247-current matched row/subject/dateblock placebo governor.
- local observation:
  - candidates: `158`;
  - matched nulls: `3318`;
  - old strict-promote candidates: `0`;
  - matched-placebo gate passes: `0`;
  - public-free ready files: `0`;
  - best add p90: `-0.000003481`;
  - best undo p90: `-0.000000902`.
- interpretation: human/social/payday state explains E247/E256 boundary anatomy, including month-start shopping/money-rumination and app-state-by-amplitude signals, but the direct add/undo translator is not strong enough.
- next experiment: keep E247 as the protected body and learn a contrastive E247 preserve/avoid latent before any new public LB slot is used.

## Public-Free Observation: E286

- submission files: `analysis_outputs/submission_e286_e247contrast_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E286 failed the local E247-current matched row/subject/dateblock placebo governor.
- local observation:
  - latent rows: `128`;
  - selected latents: `12`;
  - candidates: `533`;
  - matched nulls: `11193`;
  - old strict-promote candidates: `0`;
  - matched-placebo gate passes: `0`;
  - public-free ready files: `0`;
  - best source-transfer AUC: `0.519231`;
  - best candidate p90 scale: about `-0.000004`.
- interpretation: learned E247 preserve/avoid identity mostly recovers E247 geometry, not a transferable human/social hidden state. Human/social context contains a small local sibling-boundary clue, but it is not strong enough to justify public LB.
- next experiment: ground the social/JEPA latent in train OOF residuals or row-alignment transfer before materializing another current-frontier tensor.

## Public-Free Observation: E287

- submission files: `analysis_outputs/submission_e287_rowalign_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E287 failed the local E247-current matched row/subject/dateblock null governor.
- local observation:
  - latent rows: `36`;
  - train-gated policies: `3`;
  - candidates: `3`;
  - matched nulls: `63`;
  - public-free ready files: `0`;
  - best transferred candidate: `submission_e287_rowalign_q3_only_subject_oof_lr_l1_tf70_5fc12bc2.csv`;
  - best actual mean: `-0.000051070`;
  - best actual p90: `-0.000034973`;
  - best final decision: `too_small_to_submit`.
- interpretation: train-supervised row-action benefit is a better hidden target than current-test pseudo-label identity, but it still does not transfer into a robust E247-current probability edit.
- next experiment: use train row-action benefit as an energy/context signal, or build a sharper train-to-test bridge, before spending another public LB slot.

## Public-Free Observation: E288

- submission files: none produced.
- public LB: not submitted.
- reason not submitted: E288 is a representation/stress audit and failed local label gates.
- local observation:
  - stories: `28`;
  - context views: `3`;
  - label stress rows: `12`;
  - label-gate rows: `0`;
  - best mean label delta: `+0.002092612`;
  - best reconstruction view: `family_jepa_context/dateblock5`, mean story R2 `0.385944`;
  - top reconstructable payday/cash-flow story: `paymonth_start_post3_late_shopping`, R2 `0.813342`.
- interpretation: social/cash-flow lifestyle states are real as hidden diary states, but the broad bundle is not a public-ready probability representation.
- next experiment: target-specific bundle slicing with per-target null governance, focusing on dateblock-stable S4/Q3/S2 improvements rather than shared 7-target bundle features.

## Public-Free Observation: E289

- submission files: `analysis_outputs/submission_e289_lifeslice_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E289 failed the local E247-current matched row/subject/dateblock null governor.
- local observation:
  - target-slice rows: `84`;
  - target-gate rows: `7`;
  - candidates: `28`;
  - matched nulls: `420`;
  - public-free ready files: `0`;
  - best Q3 target slice: `Q3_raw_human_context_subject5_pc`, train delta `-0.014465898`;
  - best S4 target slice: `S4_family_jepa_context_dateblock5_cluster6`, train delta `-0.011131`;
  - strongest candidate null strict rate: `1.000000`.
- interpretation: target-specific lifestyle state is real on train, especially Q3/S4, but direct E247-current materialization is not certified because matched shuffles reproduce the movement.
- next experiment: learn row/block placement from the Q3/S4 lifestyle energy rather than submitting a scalar target edit.

## Public-Free Observation: E290

- submission files: `analysis_outputs/submission_e290_lifeplace_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E290 failed the local E247-current matched row/subject/dateblock null governor.
- local observation:
  - placement rows: `420`;
  - train placement gates: `59`;
  - candidates: `48`;
  - matched nulls: `720`;
  - public-free ready files: `0`;
  - best train placement delta: `-0.024399167`;
  - best candidate actual mean: `-0.000495`;
  - best candidate actual p90: `-0.000308`;
  - strongest candidate null strict rate: `1.000000`.
- interpretation: train labels can teach where lifestyle corrections help, but the learned placement does not transfer into a test tensor that beats matched nulls.
- next experiment: search for an independent test-side placement invariant or move from rowwise placement to hidden block-state assignment.

## Public-Free Observation: E291

- submission files: `analysis_outputs/submission_e291_lifeblock_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E291 failed the local E247-current matched row/subject/dateblock null governor.
- local observation:
  - block policy rows: `560`;
  - train block gates: `39`;
  - candidates: `40`;
  - matched nulls: `600`;
  - public-free ready files: `0`;
  - best train block delta: `-0.017607`;
  - best candidate actual mean: `-0.000796`;
  - best candidate p90 scale: about `-0.000314`;
  - promote-scale candidates are blocked by matched nulls.
- interpretation: hidden lifestyle block state is real on train, but direct block-gated E247-current edits are not certified.
- next experiment: learn a contrastive true-vs-null placement representation before spending another public LB slot.

## Public-Free Observation: E292

- submission files: `analysis_outputs/submission_e292_contrastlife_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E292 did not produce a public-free ready candidate.
- local observation:
  - contrast rows: `98`;
  - train contrast gates: `34`;
  - candidates: `56`;
  - matched nulls: `840`;
  - public-free ready files: `0`;
  - best train contrast delta: `-0.014723076`;
  - best old-strict null strict rate: `0.133333`;
  - best low-null candidate p90: `-0.000053`;
  - best low-null candidate mean dominance: `0.466667`.
- interpretation: anti-null placement filtering partially works for S4, but not enough to justify public LB. Q3 contrast placement remains null-reproducible.
- next experiment: focus on candidate-level null-outcome modeling for S4 lifestyle-bin raw edits, or stop the lifestyle-placement branch until a stronger invariant appears.

## Public-Free Observation: E293

- submission files: `analysis_outputs/submission_e293_s4lownull_*.csv`
- public LB: not submitted.
- reason not submitted: public LB is scarce, and E293 failed the local public-free matched-null governor.
- local observation:
  - generated candidates: `840`;
  - old strict candidates: `554`;
  - null-evaluated candidates: `64`;
  - matched null evaluations: `1344`;
  - public-free ready files: `0`;
  - best null-safe candidates: null strict rate `0.000000`, final `too_small_to_submit`;
  - nearest old-strict 31-row pocket: null strict rate `0.476190` to `0.523810`;
  - strongest p90 candidates: null strict rate `1.000000`.
- interpretation: S4 lifestyle-bin low-null signal is a diagnostic pocket, not a submission-ready file. The failure mode is a discrete selector/invariant cliff.
- next experiment: do not spend public LB on another S4 scale variant. Either build a candidate-level null-outcome invariant or switch to a different hidden-state branch.

## Public-Free Observation: E294

- submission files: none generated.
- public LB: not submitted.
- reason not submitted: E294 was a diagnostic audit and produced `0` public-ready candidates.
- local observation:
  - source candidates: `64`;
  - matched null rows: `1344`;
  - best actual-vs-null AUC: `0.883498`;
  - S4-local-only AUC: `0.619617`;
  - realness vs null strict rate: positive;
  - public-free ready files: `0`.
- interpretation: E293 actual placement identity is learnable, but it is not the desired hidden state. It tracks broad output geometry and null-promotable movement.
- next experiment: avoid E293/S4 public submissions. Either train a direct null-outcome gate if enough positives can be created, or pivot to a different lifestyle state with cleaner target evidence.

## Public-Free Observation: E295

- submission files: none generated.
- public LB: not submitted.
- reason not submitted: E295 was a discovery atlas with light null stress, not a promotion governor.
- local observation:
  - episode states: `11`;
  - reconstruction rows: `66`;
  - broad bundle label gates: `0`;
  - target-specific gates: `51`;
  - best reconstruction view: `family_jepa_context/dateblock5`, mean R2 `0.438241`;
  - best target instance: `cashflow_stress/S1`, delta `-0.017243504`.
- interpretation: human/social/cash-flow episode states are real as target-specific representations, but not as a shared all-target feature block.
- next experiment: strict null audit on consensus and large single-view episode-target pairs.

## Public-Free Observation: E296

- submission files: none generated.
- public LB: not submitted.
- reason not submitted: E296 was a strict train-side null audit, not a current-submission materializer.
- local observation:
  - candidate instances: `33`;
  - strict gates: `19`;
  - robust gates: `5`;
  - pair gates: `2`;
  - strongest robust states: `bedtime_arousal/S3`, `routine_fragmentation/S1`, `routine_anchor_recovery/S2`, `routine_fragmentation/S3`, `bedtime_arousal/S1`;
  - pair-gated states: `bedtime_arousal/S1` and `bedtime_arousal/S3`.
- interpretation: presleep arousal and routine fragmentation are the current strongest human-state hypotheses. Cash-flow/payday is not dead, but it is not strict enough yet for scarce public testing.
- next experiment: materialize only robust episode-target states on E247 and apply the matched-null governor.

## Public-Free Observation: E297

- submission files: `analysis_outputs/submission_e297_epstate_*.csv`
- public LB: not submitted.
- reason not submitted: no E297 candidate passed the current public-free matched-null governor.
- local observation:
  - generated candidates: `150`;
  - old strict candidates: `25`;
  - null-evaluated candidates: `39`;
  - public-free ready files: `0`;
  - best actual p90: `-0.000565475`;
  - best null strict rate: `0.000000`, but only for `too_small_to_submit` rows;
  - old-strict bedtime/routine S1 rows are blocked by high matched-null strict rates.
- interpretation: the human episode states survived local label nulls, but the logistic materializer collapses into generic target movement when translated onto E247.
- next experiment: learn candidate outcome health directly: selector-visible and null-rare, with bedtime/routine states as priors.

## Public-Free Observation: E298

- submission files: none.
- public LB: not submitted.
- reason not submitted: E298 is an archive-level local governor audit; it found no public-free ready candidate.
- local observation:
  - governor files loaded: `11`;
  - governed candidates: `1044`;
  - ready-like candidates: `0`;
  - selector-visible candidates: `162`;
  - null-rare candidates: `867`;
  - selector-visible and null-rare candidates: `0`;
  - null-rare and edge-ok candidates: `0`;
  - selector-visible and null-common candidates: `160`.
- interpretation: the current archive does not contain a hidden safe submission. The action layer has a visibility/null-rarity cliff.
- next experiment: build a local-only translator target for `selector-visible + null-rare`; do not spend public LB on another amplitude or story-ranked variant.

## Public-Free Observation: E299

- submission files: `analysis_outputs/submission_e299_bridge_*.csv`.
- public LB: not submitted.
- reason not submitted: no E299 bridge candidate passed the public-free matched-null governor.
- local observation:
  - base near-miss rows: `14`;
  - generated candidates: `102`;
  - old strict prefilter candidates: `81`;
  - null-evaluated candidates: `71`;
  - public-free ready candidates: `0`;
  - closest file: `analysis_outputs/submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv`;
  - closest file metrics: p90 `-0.000050918`, null strict `0.095238`, p90 dominance `0.952381`, worst-mode `0.857143`, mean dominance `0.476190`.
- interpretation: scale bridging is insufficient. The live near-miss is S4 placement with subject/dateblock mean-dominance failure.
- next experiment: S4 sign/mask/within-subject placement rescue under the same matched-null governor.

## Public-Free Observation: E300-E301

- submission file: `analysis_outputs/submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv`.
- public LB: not submitted.
- reason not submitted: E301 large-null confirmation rejected the E300 small-governor ready result.
- local observation:
  - E300 generated candidates: `1305`;
  - E300 small-governor ready candidates: `1`;
  - E301 null submissions: `256`;
  - actual strict promote: true;
  - actual mean/p90: `-0.000161310` / `-0.000051307`;
  - null strict rate: `0.164062`;
  - p90 dominance: `0.937500`;
  - mean dominance: `0.691406`;
  - worst-mode mean dominance: `0.328125`;
  - row/subject/dateblock/sign null strict rates: `0.000000` / `0.250000` / `0.406250` / `0.000000`.
- interpretation: the S4 sign pattern is meaningful, but subject/dateblock placement is not certified. Public LB should be preserved.
- next experiment: learn or construct a subject/dateblock placement-health target; do not submit hand-probed S4 dateblock masks.

## Public-Free Observation: E302

- submission files: none.
- public LB: not submitted.
- reason not submitted: E302 is a placement-health decoder, not a probability submission generator.
- local observation:
  - placements: `257`;
  - null placements: `256`;
  - `human_all` leave-mode-out mean Spearman: `0.400962`;
  - `human_all_plus_topology` leave-mode-out mean Spearman: `0.325973`;
  - `human_all` p90 Spearman: `-0.090201`;
  - E300 actual mean predicted rank pct under `human_all_plus_topology`: `0.433594`;
  - E300 actual p90 predicted rank pct under `human_all_plus_topology`: `0.000000`.
- interpretation: human diary context weakly explains mean placement health, but it does not make E300 exceptional on the failing axis. The branch remains diagnostic.
- next experiment: build a constrained S4 mean-placement prior from the E302 decoder and rerun large-null confirmation, or abandon S4 mask surgery if that fails.

## Public-Free Observation: E303

- submission files: `analysis_outputs/submission_e303_s4meanprior_*.csv`.
- public LB: not submitted.
- reason not submitted: no E303 candidate passed the local large-null governor.
- local observation:
  - generated candidates: `260`;
  - old strict prefilter candidates: `183`;
  - null-evaluated candidates: `12`;
  - public-free ready files: `0`;
  - best null strict rate: `0.187500`;
  - best mean dominance: `0.695312`;
  - best actual p90: `-0.000074119`.
- interpretation: the E302 human placement prior creates attractive S4 movements, but public-free checks still see subject/dateblock placement as reproducible by null worlds.
- next experiment: do not spend public LB on E303. Either define a new hidden block-placement target or pivot away from S4 mask surgery.

## Public-Free Observation: E304

- submission files: none.
- public LB: not submitted.
- reason not submitted: E304 is a hidden block-state representation probe, not a probability materializer.
- local observation:
  - train blocks: `86`;
  - representation gates: `3`;
  - best view: `family_jepa/subject_holdout`;
  - mean Spearman: `0.143141`;
  - null dominance: `0.986111`;
  - S4 Spearman: `0.124633`;
  - E299 active-minus-inactive predicted S4: `-0.151507`;
  - `id07_b9` predicted S4 residual: `-0.415169`.
- interpretation: raw human diary/JEPA context can weakly recover hidden block target state, and it explains why previous S4 placements failed.
- next experiment: materialize the E304 block prior under matched-null governance before any public LB.

## Public-Free Observation: E305

- submission files: `analysis_outputs/submission_e305_blockprior_s4_*.csv`.
- public LB: not submitted.
- reason not submitted: no E305 candidate passed the local large-null governor.
- local observation:
  - generated candidates: `111`;
  - old strict candidates: `14`;
  - null-evaluated candidates: `14`;
  - public-free ready files: `0`;
  - best null strict rate: `0.648438`;
  - best mean dominance: `0.562500`;
  - best actual p90: `-0.000127522`.
- interpretation: E304's hidden block prior is real as a diagnostic, but direct S4 top-block materialization is null-common.
- next experiment: learn a contrastive action-health target, or pause S4 and use E304 block state as a broader Q/S world-model feature.

## Public-Free Observation: E306

- submission files: `analysis_outputs/submission_e306_withinblock_s4_*.csv`.
- public LB: not submitted.
- reason not submitted: no E306 candidate passed the local row/subject/dateblock/sign governor.
- local observation:
  - row-placement gates: `6`;
  - best row diagnostic: `family_jepa_dbdelta/row_stratified5`, within-dateblock AUC `0.585020`;
  - dateblock-held diagnostic: `family_jepa_dbdelta/dateblock_holdout`, within-dateblock AUC `0.574899`, null dominance `0.979167`;
  - generated candidates: `272`;
  - old strict candidates: `22`;
  - null-evaluated candidates: `20`;
  - public-free ready files: `0`;
  - best null strict rate: `0.625000`;
  - best dateblock p90 dominance: `0.875000`;
  - best mean dominance: `0.671875`.
- interpretation: hidden row-placement state exists in train, but direct S4 row mass still looks too much like null movement on the current public-free selector.
- next experiment: use row-placement as an action-health feature or censor, not as a direct additive S4 generator.

## Public-Free Observation: E307

- submission files: `analysis_outputs/submission_e307_s4latentcensor_*.csv`.
- public LB: not submitted.
- reason not submitted: no E307 candidate passed the local row/subject/dateblock/sign governor.
- local observation:
  - generated candidates: `765`;
  - old strict candidates: `106`;
  - null-evaluated candidates: `22`;
  - public-free ready files: `0`;
  - best null strict rate: `0.750000`;
  - best mean dominance: `0.546875`;
  - best dateblock p90 dominance: `0.656250`;
  - best actual p90: `-0.000197843`;
  - wrong-direction/sharpening controls were competitive.
- interpretation: S4 latent-current mismatch is useful as a diagnostic, but direct censoring is not public-free safe. The public-free selector can be triggered by generic S4 confidence movement.
- next experiment: stop hand-built S4 delta families unless a learned action-health model or a non-S4 interaction creates controls that clearly lose.

## Public-Free Observation: E308

- submission files: none.
- public LB: not submitted.
- reason not submitted: E308 is a governor audit, not a candidate generator.
- local observation:
  - governed candidate rows: `1304`;
  - experiments loaded: `18`;
  - selector-visible rows: `367`;
  - null-rare rows: `918`;
  - visible/null-rare rows: `2`;
  - strict-large-null ready raw: `1`;
  - certified public-free ready after E301 supersession: `0`;
  - post-E303 S4 rows: `68`, null-rare `0`.
- interpretation: public LB should not be used on the current archive. Most candidates either have no visible edge or have a visible edge that matched nulls can imitate.
- next experiment: generate a genuinely new action-health positive, or pivot away from hand-built S4 deltas to a target interaction where controls fail locally before any public submission.

## Public-Free Observation: E309

- submission files: none.
- public LB: not submitted.
- reason not submitted: E309 is a representation/null-stress probe, not a materialized candidate.
- local observation:
  - quick scanned rows: `426`;
  - strict rerun rows: `32`;
  - strict gates: `29`;
  - robust gates: `13`;
  - pair gates: `12`;
  - strongest pair: `cashflow_stress/Q1_S1`, best delta `-0.046023`;
  - strongest family: QS target dependency, strict `16/18`, robust `8/18`.
- interpretation: the human/social branch is not dead. Its live form is target dependency, especially cashflow or money-rumination effects on Q1-S1 and bedtime arousal effects on Q/S-stage pairs.
- next experiment: materialize coupled pair-delta candidates and reject them locally unless wrong-pair and shuffled-state controls lose.

## Public-Free Observation: E310

- submission files: `analysis_outputs/submission_e310_pair_*.csv`.
- public LB: not submitted.
- reason not submitted: no E310 candidate passed the local row/subject/dateblock/swap/wrong-pair/sign governor.
- local observation:
  - generated candidates: `455`;
  - old strict candidates: `77`;
  - null-evaluated candidates: `42`;
  - public-free ready files: `0`;
  - best actual p90: `-0.000379563`;
  - strongest visible stories: `cashflow_stress/Q1_S1`, `cashflow_stress/S1_S2`, `cashflow_stress/S1_S3`, `cashflow_stress/S1_S4`, `home_recovery/Q1_S3`;
  - old-strict visible candidates are mostly null-common;
  - null-rare candidates are below submission resolution.
- interpretation: public LB should not be used on E310. The pair-interaction representation is useful, but direct coupled logit deltas are not a certified action layer.
- next experiment: use pair state as action-health supervision or energy/gate, and keep wrong-pair plus shuffled-state controls as mandatory local blockers.

## Public-Free Observation: E311

- submission files: `analysis_outputs/submission_e311_pairmicro_*.csv`.
- public LB: not submitted.
- reason not submitted: no E311 candidate passed the local row/subject/dateblock/swap/wrong-pair/sign governor.
- local observation:
  - generated candidates: `512`;
  - old strict candidates: `489`;
  - null-evaluated candidates: `37`;
  - public-free ready files: `0`;
  - best actual p90: `-0.000807827`;
  - best null strict rate: `0.000000`, but only on too-small residualized rows;
  - visible microstacks are null-common, with best microstack null strict rate `0.611111`.
- interpretation: public LB should not be used on E311. The pair-action safety cliff survives stacking and mean-null residualization.
- next experiment: stop direct pair-delta materialization unless a learned action-health target or a new hidden-state objective changes the visible/null-rare tradeoff.

## Public-Free Observation: E312

- submission files: none.
- public LB: not submitted.
- reason not submitted: E312 is a local checker/governor model, not a probability tensor.
- local observation:
  - governed rows: `1383`;
  - experiments: `20`;
  - selector-visible rows: `418`;
  - null-rare rows: `930`;
  - visible/null-rare rows: `2`;
  - strict-health rows: `1`;
  - `geometry_only` null-common OOF AUC: `0.984890`;
  - `semantic_only` null-common OOF AUC: `0.713484`;
  - `full_safe` readiness-distance OOF Spearman: `0.102712`.
- interpretation: public LB should not be used to test E310/E311 descendants. The archive says their failure is predictable action geometry: many candidates are visible or safe, but almost none are both.
- next experiment: generate a new action class or train a richer row/block action-health objective. The governor may veto submissions, but it cannot certify a ready file by itself.

## Public-Free Observation: E313

- submission files: none.
- public LB: not submitted.
- reason not submitted: E313 is a human-diary action signature audit, not a probability tensor.
- local observation:
  - candidate files found: `1379/1383`;
  - human aggregate columns: `520`;
  - `human_signature` null-common AUC: `0.866674`;
  - `geometry_only` null-common AUC: `0.982733`;
  - `geometry_plus_shape` null-common AUC: `0.987170`;
  - `human_signature` readiness-distance Spearman: `0.700161`;
  - `geometry_only` readiness-distance Spearman: `0.031522`.
- interpretation: human/lifestyle row placement is real but not sufficient for public submission selection. It explains readiness distance and some selector-visible rare cases, while geometry remains the stronger global null-common checker.
- next experiment: use human-readiness energy to create a new materializer that starts from safe-but-too-small human-aligned rows and tries to become visible without entering the geometry null-common region.

## Public-Free Observation: E314

- submission files: `analysis_outputs/submission_e314_humanready_*.csv`.
- public LB: not submitted.
- reason not submitted: no E314 candidate passed the local row/subject/dateblock/target-permutation/QS-swap/sign governor.
- local observation:
  - safe human-ready seeds loaded: `180`;
  - generated candidates: `360`;
  - old strict candidates: `33`;
  - info candidates: `134`;
  - null-evaluated candidates: `40`;
  - public-free ready files: `0`;
  - best actual p90: `-0.000087616`;
  - best null strict rate: `0.000000`, but only below submission resolution;
  - old-strict lifted rows become null-common, with the top visible row null strict rate `0.346154`.
- interpretation: human-readiness energy identifies plausible seeds, but individual scalar lift is not a public-free action layer. It still falls into safe-but-invisible versus visible-but-null-common behavior.
- next experiment: do not public-test E314 files. Reserve a new local run for non-single consensus/orthogonal-stack materialization, or move to a target-level materializer that changes the action geometry rather than the amplitude.

## Public-Free Observation: E315

- submission files: `analysis_outputs/submission_e315_humancomp_*.csv`.
- public LB: not submitted.
- reason not submitted: no E315 candidate passed the local row/subject/dateblock/target-permutation/QS-swap/sign governor.
- local observation:
  - safe human-ready seeds loaded: `180`;
  - generated candidates: `660`;
  - old strict candidates: `229`;
  - info candidates: `297`;
  - null-evaluated candidates: `67`;
  - public-free ready files: `0`;
  - best actual p90: `-0.000523248`;
  - best null strict rate: `0.090909`, but on non-strict orthogonal story stacks with subject/dateblock weakness;
  - bedtime-arousal family consensus is selector-visible but null-common;
  - routine-fragmentation/S1 target consensus is a strong information sensor but fails row dominance.
- interpretation: public LB should not be spent. E315 says the human/social branch is still useful for world modeling, but existing probability-delta composition does not solve hidden placement.
- next experiment: train or construct a placement-health target from E315 near misses rather than stacking more human-ready deltas.

## Public-Free Observation: E316

- submission files: none.
- public LB: not submitted.
- reason not submitted: E316 is a local hidden-placement diagnostic and explicitly finds that placement identity is not enough for health.
- local observation:
  - placement rows: `1541`;
  - source candidates: `67`;
  - actual rows: `67`;
  - placement null rows: `1005`;
  - all null rows: `1474`;
  - `human_signature` actual-vs-placement-null AUC: `0.998856`;
  - `human_signature` AP: `0.992019`;
  - `human_signature` mean actual rank: `0.999005`;
  - `action_shape` actual-vs-placement-null AUC: `0.500000`;
  - `human_plus_shape` local p90 Spearman: `0.900789`;
  - identity rank vs worst-mode p90 dominance Spearman: `0.159448`;
  - identity rank vs null strict rate Spearman: `-0.206034`.
- interpretation: hidden human/social placement identity is real and locally measurable without public LB. But the health target is different from the identity target, so public LB should not be used until a candidate passes direct placement-health governance.
- next experiment: train an outcome-health target for row/subject/dateblock dominance using E315/E316 near misses, with actual-vs-null identity as only one input feature.

## Public-Free Observation: E317

- submission files: none.
- public LB: not submitted.
- reason not submitted: E317 is a local placement-outcome learner and does not produce a probability tensor.
- local observation:
  - placement rows: `1072`;
  - sources: `67`;
  - joint-health positive rate: `0.152052`;
  - source-held p90-rank Spearman: human `0.320748`, action shape `0.000000`, human+action `0.451921`, human+identity+action `0.459774`;
  - source top-mode accuracy: human `0.432836`, human+action `0.552239`, human+identity+action `0.582090`, action shape `0.029851`;
  - source-held joint-health AUC: human `0.731185`, action shape `0.683432`, shape+identity `0.794344`;
  - within-mode p90-rank mean Spearman: action shape `0.326136`, human `0.238693`;
  - null-mode holdout p90-rank mean Spearman: human `0.133354`, action shape `-0.358750`.
- interpretation: E317 should not spend public LB. Human diary context helps with source/mode placement health, but mode-internal health remains too action-geometry-dependent.
- next experiment: build a mode-specialized generator that uses human context to choose row/subject/dateblock regime and action geometry to place movement within that regime, then test matched nulls locally.

## Public-Free Observation: E318

- submission files: none.
- public LB: not submitted.
- reason not submitted: E318 selects among E315 actual/null placement controls and does not produce a fresh probability tensor. Public LB should not be used as the checker for these controls.
- local observation:
  - placement rows: `1072`;
  - sources: `67`;
  - policies: `10`;
  - best non-oracle policy: `human_identity_action_p90_rank`;
  - p90-rank health mean: `0.649254` versus actual baseline `0.620336`;
  - delta rank versus actual: `0.028918`;
  - joint-health rate: `0.313433` versus actual baseline `0.134328`;
  - oracle-mode accuracy: `0.582090`;
  - selected placement mix: actual `0.089552`, row `0.149254`, subject `0.552239`, dateblock `0.208955`.
- interpretation: E318 is a useful public-free sensor. It strengthens the belief that hidden placement regime matters and that human context helps select it, but it rejects direct public testing of E315 null placements.
- next experiment: build a fresh mode-specialized generator, then apply direct row/subject/dateblock/sign/target null governance before any public LB use.

## Public-Free Observation: E319

- submission files: `analysis_outputs/submission_e319_modespec_*.csv`.
- public LB: not submitted.
- reason not submitted: E319 generated fresh mode-specialized tensors, but none passed matched null governance. Public LB is not needed to reject this branch.
- local observation:
  - routes from E318 policies: `335`;
  - generated candidates: `540`;
  - old strict candidates: `403`;
  - info candidates: `103`;
  - null-evaluated candidates: `54`;
  - public-free ready candidates: `0`;
  - best actual p90: `-0.004283155`;
  - best null strict rate: `0.000000`, but not with all promotion gates satisfied;
  - non-oracle governed candidates: `47`;
  - non-oracle old-strict candidates inside governor: `30`.
- interpretation: E319 proves that E318 routes can make very visible tensors, but the visibility is not a healthy hidden-state signal. The candidates are locally attractive and still reproducible by row/subject/dateblock controls.
- next experiment: do not public-test E319 files. Build an adversarial mode-specific action-health learner before generating another tensor.

## Public-Free Observation: E320

- submission files: none.
- public LB: not submitted.
- reason not submitted: E320 is a failure-anatomy diagnostic for E319, not a probability tensor.
- local observation:
  - non-oracle governed candidates: `47`;
  - old-strict candidates inside governor: `30`;
  - public-free ready candidates: `0`;
  - target-permutation mean dominance: `1.000000`;
  - sign-flip mean dominance: `1.000000`;
  - Q/S-swap mean dominance: `0.978723`;
  - subject mean dominance: `0.611702`;
  - dateblock mean dominance: `0.702128`;
  - row mean dominance: `0.755319`;
  - killer modes: row `16`, subject `15`, dateblock `15`, Q/S swap `1`.
- interpretation: the E319 failure is not mainly wrong target, wrong sign, or Q/S confusion. The blocker is hidden placement ambiguity: the same movement can be imitated by row, subject, or dateblock alternatives.
- next experiment: make row/subject/dateblock placement health the explicit JEPA-style target and use public LB only after that local target survives.

## Public-Free Observation: E321

- submission files: none.
- public LB: not submitted.
- reason not submitted: E321 is a local action-health learner and produces no probability tensor.
- local observation:
  - pair rows: `564`;
  - candidates: `47`;
  - p90-win AUC with full-pair geometry: row `0.821035`, subject `0.930077`, dateblock `0.915720`;
  - candidate predicted worst-placement dominance Spearman: `0.614177`;
  - predicted null strict rate Spearman: `0.548433`;
  - predicted adversarial health Spearman: `0.508146`;
  - ready-like candidates: `0`.
- interpretation: placement health is locally learnable and should become a JEPA-style action target. The current E319 candidate pool still has no public candidate.
- next experiment: use E321 as a pre-materialization health model or a public-free preselector for additional null evaluation.

## Public-Free Observation: E322

- submission files: none.
- public LB: not submitted.
- reason not submitted: E322 selected unevaluated E319 candidates for fresh public-free null governance, and none passed. Public LB should not be used to override a ready count of `0`.
- local observation:
  - non-oracle E319 candidates scored: `450`;
  - old strict in universe: `357`;
  - previously null-evaluated: `47`;
  - selected for fresh null: `36`;
  - selected old strict: `36`;
  - fresh public-free ready: `0`;
  - best fresh p90: `-0.001452588`;
  - best null strict rate: `0.136364`;
  - best worst-mode p90 dominance: `1.000000`.
- interpretation: the E321 health target is useful as a checker but did not rescue a skipped candidate. The selected files are visible, but matched nulls still imitate them too often.
- next experiment: build a new generator that uses adversarial health before materialization; do not spend public LB on E319/E322-selected files.

## Public-Free Observation: E323/E324

- submission files:
  - priority: `analysis_outputs/submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv`;
  - alternate high-upside: `analysis_outputs/submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv`;
  - alternate middle: `analysis_outputs/submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv`.
- public LB: not submitted.
- local observation:
  - E323 generated `420` residual candidates;
  - E323 fresh ready `3`;
  - E324 high-rep ready `3/3`;
  - E324 null rows `774`;
  - priority high-rep p90 `-0.000053747`;
  - priority high-rep null strict `0.050388`;
  - priority worst-mode p90 dominance `0.859375`.
- interpretation: E323/E324 is the first local evidence that null-common residualization can extract a submission-grade hidden-placement component from human/social route near misses.
- expected public reaction:
  - improves versus E247: confirms the null-common residual world and makes residualization the next generator family;
  - flat/slightly worse: signal exists locally but is below public readability or public subset differs;
  - clearly worse: local matched nulls are missing a public/private calibration axis, and E323 should become a diagnostic rather than a generator.

## Public-Free Observation: E325

- submission files: none generated.
- public LB: not submitted.
- reason not submitted: E325 is a semantic attribution check on the already selected E324-ready files, not a new probability tensor.
- local observation:
  - tested E324 ready files: `3`;
  - semantic null modes: row, subject, dateblock;
  - reps per mode: `128`;
  - priority `5508f966` best signed semantic z `2.871546`;
  - priority best abs semantic z `2.316330`;
  - priority signed semantic z>=2 hits `9`;
  - strongest priority axes: Q1 night-out mobility, S1 phone-in-bed/bedtime arousal, S3 social-isolation/media.
- interpretation: the E324 priority file is lifestyle-interpretable but only moderately so. This supports its worldview without creating a stronger semantic-gated sibling.
- expected public reaction:
  - improves versus E247: E325 becomes explanatory evidence that the residual action found a real lifestyle-aware placement component;
  - worsens: semantic attribution alone is insufficient, and future public-free gates must add public/private calibration or subset diagnostics before another submission.

## Public-Free Observation: E326

- submission files: generated locally, but none promoted above the existing E324 priority.
- public LB: not submitted.
- reason not submitted: E326 found semantic-censored candidates that pass local readiness, but none beat the already selected E324 priority under the replacement gate.
- local observation:
  - generated candidates: `252`;
  - prefilter strict candidates: `141`;
  - null-evaluated candidates: `36`;
  - null rows: `6984`;
  - public-free ready: `2`;
  - beats E324 priority locally: `0`;
  - semantic selected ready: `2/24`;
  - anti-control selected ready: `0/12`.
- interpretation: semantic/social axes are useful enough to reject anti-semantic controls, but not enough to replace placement-null residualization as the main action law.
- expected public reaction:
  - do not spend a public slot on E326 before E324 priority;
  - if E324 later improves public, E326 can become a follow-up contrast for whether semantic pruning adds value;
  - if E324 worsens, E326 should be blocked because the issue would likely be public/private subset or calibration mismatch, not insufficient semantic pruning.

## Public-Free Observation: E327

- submission files: generated locally, but none promoted above the existing E324 priority.
- public LB: not submitted.
- reason not submitted: E327 produced public-free ready variants, but none dominated the current E324 priority under fresh null stress.
- local observation:
  - generated candidates: `540`;
  - prefilter strict candidates: `179`;
  - build null rows: `288`;
  - stress null rows: `7760`;
  - public-free ready: `2`;
  - beats E324 priority locally: `0`;
  - nullfail-censor selected ready: `2/33`;
  - anti-control selected ready: `0/7`.
- interpretation: competitive null placements contain useful diagnostic signal, but direct bad-null subtraction overfits and conservative damping is not stronger than the original residual candidate.
- expected public reaction:
  - do not spend a public slot on E327 before E324 priority;
  - if E324 improves, E327 can be used as a second-order diagnostic sibling;
  - if E324 worsens, E327 should also be blocked because it is built on the same local residual world and selector family.

## Submission-Format Observation: E323 Priority

- original file: `analysis_outputs/submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv`.
- observed platform reaction: submission-value error.
- local schema check:
  - shape equals sample: `250 x 10`;
  - columns equal sample: `subject_id,sleep_date,lifelog_date,Q1,Q2,Q3,S1,S2,S3,S4`;
  - key order equals sample: true;
  - NaN/Inf: none;
  - target values strictly inside `(0, 1)`: true;
  - min/max: `0.0683439958` / `0.9793394519`.
- mitigation file: `analysis_outputs/submission_e323_5508f966_uploadsafe.csv`.
- mitigation method: rebuild from `data/ch2026_submission_sample.csv`, copy original predictions into target columns, clip to `1e-7..1-1e-7`, and write fixed decimal formatting.
- max absolute prediction change from original: `< 5e-11`.
- interpretation: this is treated as a packaging/platform-parse issue, not model evidence. It should not update the E323 worldview until the upload-safe file receives an actual LB score.

## Public LB Observation: E323 Upload-Safe

- submission file: `analysis_outputs/submission_e323_5508f966_uploadsafe.csv`.
- actual public LB: `0.5770355016`.
- expected reaction before submission: if E324 worsens clearly, local matched nulls are missing a public/private calibration or subset axis and E323 should become diagnostic rather than generative.
- actual reaction:
  - vs E247 best `0.5761589494`: `+0.0008765522` worse;
  - vs E256 `0.5762805676`: `+0.0007549340` worse;
  - vs E95 `0.5762913298`: `+0.0007441718` worse;
  - vs mixmin `0.5763066405`: `+0.0007288611` worse.
- interpretation:
  - this is a hard negative, not a frontier-scale tie;
  - E323/E324 local null-common residualization learned a locally non-random residual, but not the public-evaluated hidden state;
  - E325 semantic alignment did not imply public correctness;
  - E326/E327 should not be used as rescue because both are same-family refinements that failed to dominate `5508f966` locally.
- next experiment consequence:
  - add an E323-negative stress slice to future promotion checks;
  - block direct siblings of E323/E324/E326/E327;
  - do not spend another public slot until the new candidate explains why the E323 movement should be avoided or orthogonalized.

## Public-Free Observation: E328 Own-Latent Lifestyle State

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: all E328 candidates are below selector resolution and the broad latent fails blocked label stress.
- local observation:
  - best teacher prediction view: `family_jepa_story/dateblock`, OOF R2 `0.972508`;
  - subject label delta `+0.035211637`;
  - dateblock label delta `+0.022631387`;
  - targets improved `0`;
  - strongest E247/E256 boundary signal `1.477419`;
  - strongest E323 top20 signal `0.545557`;
  - strict promoted candidates `0`.
- interpretation:
  - hidden lifestyle state is observable and human-interpretable;
  - broad lifestyle state does not transfer to labels or public-risk gating;
  - the next public candidate should not come from broad lifestyle PCA/KMeans, but from target-specific or action-health latent objectives.
- expected public reaction if submitted anyway:
  - likely flat/noisy or worse, because the local checker sees no label benefit and no strong E323-negative axis.

## Public-Free Observation: E330 Target-Residual Lifestyle Latent

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: target-residual representation survives local label/null stress, but materialized E247 edits are below selector resolution or rejected.
- local observation:
  - audited target/view/split rows: `84`;
  - gated residual-state rows: `16`;
  - generated candidates: `25`;
  - selector-promoted candidates: `0`;
  - E323-negative candidates by movement cosine: `25`.
- strongest residual states:
  - Q2 `jepa_resid/subject`, label delta `-0.030210616`;
  - Q1 `jepa_resid/dateblock`, label delta `-0.025842772`;
  - S2 `raw_day/subject`, label delta `-0.016452074`;
  - S2 `jepa_resid/dateblock`, label delta `-0.014211218`.
- interpretation:
  - hidden lifestyle-state signal exists after target residualization;
  - current full-target materializer is too diffuse;
  - next public-free experiment should localize the residual state to rows/blocks/cells before another submission candidate is considered.
- expected public reaction if submitted anyway:
  - likely low-information because the best local scores still have p90 crossing above zero and no strict promote gate.

## Public-Free Observation: E331 Residual-State Localization

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: localized residual-state gates are label-useful, but current E247 materializations are too small or not movement-null-safe enough.
- local observation:
  - localized gates: `39`;
  - generated candidates: `43`;
  - selector-promoted candidates: `0`;
  - selector+E323+movement-null-safe candidates: `0`.
- strongest localized states:
  - Q1 `jepa_resid/dateblock/pos_q80`, label delta `-0.029674864`, dominance `1.000000`, test rows `42`;
  - Q1 `jepa_resid/dateblock/pos_q90`, label delta `-0.022958364`, dominance `1.000000`, test rows `11`;
  - Q2 `jepa_resid/subject/pos_q80`, label delta `-0.017481597`, dominance `0.900000`, test rows `51`;
  - S2 `jepa_resid/dateblock/pos_q80`, label delta `-0.016882963`, dominance `1.000000`, test rows `54`.
- closest local candidate:
  - `submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p7_cf6801db.csv`;
  - selector mean `-0.000053263`, p90 `-0.000008279`, beats rate `0.972222`;
  - decision `too_small_to_submit`.
- interpretation:
  - localization confirms that hidden lifestyle residual state exists at episode-tail level;
  - public-grade movement has not been solved;
  - Q1 positive-tail residual state is now the most promising single object, but not yet a public candidate.
- expected public reaction if submitted anyway:
  - likely low-information or small-noise movement because the best p90 remains too close to zero.

## Public-Free Observation: E332 Q1 Tail Translator Stress

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: direct Q1-tail translators preserve local label/null signal but fail selector visibility and movement-null/p90 stress.
- local observation:
  - local translator gates: `33`;
  - generated candidates: `77`;
  - actual-direction selector-promoted candidates: `0`;
  - selector+E323+movement-null-safe candidates: `0`;
  - strongest local translator: Q1 `pos_q83/const`, delta `-0.015385658`, dominance `1.000000`;
  - signflip controls are rejected with beats rate `0.000000`;
  - E323 cosine is mostly negative or near zero, so E323 public-bad similarity is not the blocker.
- interpretation:
  - Q1 positive-tail hidden lifestyle state is a real directional latent;
  - direct scalar translation cannot make it public-visible without p90 risk;
  - the next public-worthy branch needs an action-health or placement-shape translator.
- expected public reaction if submitted anyway:
  - likely noisy or worse than E247 because the candidate family has no selector-promoted actual-direction file and the closest mean-positive edges still have positive p90.

## Public-Free Observation: E333 Q1 Contrastive Action Translator

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: contrastive Q1 background compensation improves local label/null stress but fails public-free selector stress.
- local observation:
  - local translator gates: `510`;
  - generated candidates: `84`;
  - selector-promoted candidates: `0`;
  - selector+E323+movement-null-safe candidates: `0`;
  - strongest local translator: Q1 `pos_q75/softplus + nontail_all/opp050`, delta `-0.020200`, dominance `1.000000`.
- public-free selector observation:
  - best-ish probe `submission_e333_q1contrast_pos_q75_softplus_low_q25_opp050_s0p25_911ccf1d.csv`;
  - mean `+0.000034`;
  - p90 `+0.000299`;
  - beats rate `0.583333`.
- interpretation:
  - local Q1 contrast is real but not public-safe;
  - broad background compensation worsens E247 action geometry;
  - Q1 branch needs action-health/placement supervision, not more local-Q1 compensation.
- expected public reaction if submitted anyway:
  - likely worse than E247 because selector mean and p90 are already adverse.

## Public-Free Observation: E334 Q1 Tail Row-Censor Action-Health

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: row-censored Q1-tail actions preserve local label/null gains but fail selector visibility and movement-null health.
- local observation:
  - row-censor variants: `532`;
  - local row-censor gates: `510`;
  - generated candidates: `72`;
  - selector-promoted candidates: `0`;
  - selector+E323-safe candidates: `0`;
  - selector+E323+movement-null-safe candidates: `0`.
- strongest local gate:
  - Q1 `pos_q78/const/latent_top80`, delta `-0.016399822`, dominance `1.000000`, test rows `34`.
- closest local probes:
  - `submission_e334_q1rowcensor_pos_q75_const_latent_top65_s0p25_1adff771.csv`, mean `-0.000112`, p90 `+0.000018`, beats `0.861111`;
  - `submission_e334_q1rowcensor_pos_q75_const_dateblock_drop_id05_b5_s0p25_159137ce.csv`, mean `-0.000236`, p90 `+0.000046`, beats `0.833333`.
- interpretation:
  - the Q1 hidden lifestyle-state latent remains real and row-local;
  - row censoring alone does not solve public-visible action health;
  - the next useful public-free experiment should learn an action-health latent directly.
- expected public reaction if submitted anyway:
  - likely low-information or worse than E247 because no file is selector-promoted and all visible-ish files retain positive p90 or weak movement-null dominance.

## Public-Free Observation: E335 Q1 Action-Health Latent Generator

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: action-health rank transfer is high, but every generated file remains below selector resolution.
- local observation:
  - archive rows: `233`;
  - movement-null-labelled rows: `58`;
  - leave-family trees Spearman `0.938198`, top20 overlap `0.891304`;
  - generated candidates: `55`;
  - selector-promoted candidates: `0`;
  - selector+E323+movement-null-safe candidates: `0`.
- closest local candidates:
  - `submission_e335_q1health_weightedavg_top2_badproj075_s0_45_d485b72f.csv`, mean `-0.000135`, p90 `-0.000012`, beats `0.930556`, movement-null p90 dominance `0.933333`;
  - `submission_e335_q1health_weightedavg_top2_s0_45_cab4254e.csv`, mean `-0.000135`, p90 `-0.000012`, beats `0.930556`, movement-null p90 dominance `0.933333`.
- interpretation:
  - action-health is a real latent/ranking target;
  - the current Q1 archive lacks a visible/null-rare positive region;
  - public testing a safe-invisible file would waste a sensor reading.
- expected public reaction if submitted anyway:
  - likely tiny/noisy movement around E247 rather than a breakthrough, because local selector promotion is exactly zero.

## Public-Free Observation: E336 Public-Negative Action Latent

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: direct inversion or orthogonalization of public-bad movement fails public-free selector and movement-null gates.
- local observation:
  - generated candidates: `162`;
  - selector-promoted candidates: `0`;
  - selector+public-bad-safe candidates: `0`;
  - selector+public-bad+movement-null-safe candidates: `0`.
- public-bad anatomy observation:
  - E323 bad axis is Q1/S1/S3-heavy, with shares Q1 `0.258564`, S1 `0.263325`, S3 `0.478111`;
  - E216 bad axis is S2-heavy, with S2 share `0.645902`;
  - old-frontier-good axes are not simply the negative of E323.
- closest local candidates:
  - `submission_e336_good_mixmin_topall_s0_14_3fb3ae73.csv`, mean `-0.000012951`, p90 `+0.000013885`, beats `0.750000`;
  - `submission_e336_good_mixmin_topall_s0_20_509bebff.csv`, mean `-0.000017725`, p90 `+0.000021884`, beats `0.750000`.
- interpretation:
  - public-bad movement anatomy is informative but not directly reversible;
  - E323/E216 axes should be used as risk sensors, not as action generators;
  - the hidden lifestyle-state latent must be discovered upstream of probability movement.
- expected public reaction if submitted anyway:
  - low-information for tiny good-mixmin continuations;
  - likely noisy or worse for away-from-bad vectors because no file is selector-promoted.

## Public-Free Observation: E337 Residual Lifestyle-Cluster State

- submission files: generated locally, but none promoted.
- public LB: not submitted.
- reason not submitted: cluster-level residual states are label-useful but their global E247 materialization fails selector visibility.
- local observation:
  - dateblock latent prediction:
    - `family/dateblock` R2 `0.169277`;
    - `jepa_resid/dateblock` R2 `0.107508`;
  - label/null gated cluster-target rows: `3`;
  - generated candidates: `64`;
  - selector-promoted candidates: `0`;
  - movement-null-safe promoted candidates: `0`.
- strongest local states:
  - `Q3/dateblock/k6`, delta `-0.003932`, dominance `0.833333`;
  - `Q2/dateblock/k8`, delta `-0.003512`, dominance `0.916667`;
  - `S3/subject/k4`, delta `-0.003509`, dominance `0.875000`.
- interpretation:
  - public-free evidence supports hidden residual lifestyle clusters;
  - global cluster-prior movement is too diffuse;
  - E323/E216 are better used as veto axes than action generators.
- expected public reaction if submitted anyway:
  - likely low-information or worse than E247 because selector-promoted count is zero and the movement is broad target-level calibration.

## Public-Free Observation: E338 Cluster-Local Episode Action

- submission files: generated locally, but none promoted for public testing.
- public LB: not submitted.
- reason not submitted: the best local episode action is clean but below selector resolution.
- local observation:
  - episode-gated rows: `10`;
  - generated candidates: `75`;
  - information-sensor candidates: `4`;
  - selector-promoted candidates: `0`;
  - movement-null-safe promoted candidates: `0`.
- closest local candidate:
  - `submission_e338_local_veto_centered_top2_s0_20_28122ea1.csv`;
  - mean `-0.000034`;
  - p90 `-0.00000036`;
  - beats `0.902778`;
  - movement-null mean/p90 dominance `1.000000/1.000000`;
  - decision `too_small_to_submit`.
- interpretation:
  - E337's hidden state becomes healthier when used locally;
  - the current action is a useful Q3 episode sensor, not a submission tensor;
  - the next public-free experiment should test constrained amplification or an E338-gated Q3 blend.
- expected public reaction if submitted anyway:
  - likely tiny/noisy public effect because the candidate is explicitly below selector resolution.

## Public-Free Observation: E339 Q3 Episode-Gated Amplifier

- submission files: generated locally, but none promoted for public testing.
- public LB: not submitted.
- reason not submitted: every amplified Q3 episode candidate remains below selector promotion despite clean local p90/null readings.
- local observation:
  - generated candidates: `5430`;
  - information-sensor candidates: `1492`;
  - selector-promoted candidates: `0`;
  - movement-null-safe promoted candidates: `0`.
- source-alignment observation:
  - E95/mixmin/E101 Q3 directions agree with E338 episode signs only `0.510204`;
  - E176 agreement is `0.489796`;
  - E267 agreement is `0.122449`;
  - E256 agreement is `0.020408`.
- closest local candidate:
  - `submission_e339_q3_top2_submission_e267_humansocial_tail_balanced_2936100f_src_inv_raw_s0_40_fe50f59e.csv`;
  - mean `-0.000019`;
  - p90 `-0.000005`;
  - beats `0.944444`;
  - movement-null mean/p90 dominance `1.000000/1.000000`;
  - decision `too_small_to_submit`.
- interpretation:
  - E338's episode gate is a real Q3 lifestyle-state sensor;
  - older stronger Q3 directions are not the missing hidden target representation;
  - the current public-free evidence does not justify a public LB sensor spend.
- expected public reaction if submitted anyway:
  - likely tiny/noisy effect around E247 because selector-promoted count is zero.

## Public-Free Observation: E340 Microstate Coalition Action-Health

- submission files: generated locally, but none promoted for public testing.
- public LB: not submitted.
- reason not submitted: Q1+Q3 hidden lifestyle micro-state coalitions remain below strict selector p90 resolution.
- local observation:
  - archive rows: `5560`;
  - safe-invisible source rows: `37`;
  - generated coalitions: `7400`;
  - selector-promoted candidates: `0`;
  - information-sensor candidates: `4248`;
  - movement-null-safe promoted candidates: `0`.
- latent observation:
  - action-health score is predictable, OOF Spearman `0.938224`;
  - visibility margin is predictable, OOF Spearman `0.921134`;
  - null-health is not predictable from this archive, OOF Spearman `0.004871`.
- closest local candidate:
  - `submission_e340_q1_E335_submission_e335_q1__q3_E339_submission_e339_q3__w1_25_1_00_bad_veto_38d229fd.csv`;
  - mean `-0.000168`;
  - p90 `-0.000028`;
  - beats `0.944444`;
  - movement-null mean/p90 dominance `1.000000/1.000000`;
  - decision `too_small_to_submit`.
- interpretation:
  - combining clean lifestyle micro-states improves mean and stability but still does not create public-visible p90;
  - the bottleneck is a missing visible/null-rare positive support axis, not merely too few small sensors.
- expected public reaction if submitted anyway:
  - likely small/noisy improvement at best, with insufficient evidence to justify spending a public slot.

## Public-Free Observation: E341 Sparse Residual Lifestyle Support Axis

- submission files: generated locally, but none promoted for public testing.
- public LB: not submitted.
- reason not submitted: E330 residual-state rare tails still fail strict selector visibility.
- local observation:
  - generated candidates: `864`;
  - selector-promoted candidates: `0`;
  - information-sensor candidates: `96`;
  - movement-null-safe promoted candidates: `0`.
- closest selector candidate:
  - `submission_e341_sparseresid_Q2_jepa_resid_subject_posdelta_top34_inv_s0_55_787b726b.csv`;
  - mean `-0.000151`;
  - p90 `-0.000017477`;
  - beats `0.902778`;
  - decision `too_small_to_submit`.
- closest null-dominant candidate:
  - `submission_e341_sparseresid_Q1_jepa_resid_dateblock_absdelta_top12_raw_s0_55_ddc802bf.csv`;
  - mean `-0.000033082`;
  - p90 `-0.000005843`;
  - movement-null mean/p90 dominance `1.000000/1.000000`;
  - null strict rate `0.000000`.
- interpretation:
  - sparse residual-tail placement is healthier than broad residual action;
  - local train residual sign does not transfer directly because the best sensor is Q2 inverse movement;
  - p90 remains too weak for a public slot.
- expected public reaction if submitted anyway:
  - likely too small/noisy to justify a submission; could provide information about Q2 inverse residual tails, but score upside is weak.

## Public-Free Observation: E342/E343 Sign-Transfer Lifestyle Latent

- submission files: generated locally, but none recommended for public testing.
- public LB: not submitted.
- reason not submitted:
  - E342 crosses p90 visibility but exceeds public-bad-axis cap;
  - E343 reduces bad-axis but loses p90 visibility.
- local observation:
  - E342 candidates: `1314`;
  - E342 selector-promoted candidates: `0`;
  - E342 information-sensor candidates: `1019`;
  - E343 candidates: `1512`;
  - E343 selector-promoted candidates: `0`;
  - E343 information-sensor candidates: `845`.
- closest E342 near-miss:
  - `submission_e342_signtransfer_q2_submission_e341_sp__micro_submission_e340_q1__w0_75_1_00_sum_bad_veto_07fbe22a.csv`;
  - mean `-0.000248`;
  - p90 `-0.000055`;
  - beats `0.986111`;
  - incremental bad-axis `0.017962`;
  - movement-null p90 dominance `0.964286`.
- closest E343 cleaned probe:
  - `submission_e343_badneutral_submission_e342_signtransfer_q2_submission_e34__q2resid_a0_20_proj_cellveto_ca0898be.csv`;
  - mean `-0.000237`;
  - p90 `-0.000046`;
  - beats `0.986111`;
  - incremental bad-axis `0.015414`.
- interpretation:
  - public-free local evidence says the sign-transfer hidden lifestyle state is real as a sensor;
  - the current action translator still borrows public-bad geometry;
  - spending a public slot now would mostly test bad-axis tolerance, not a clean score-improvement hypothesis.
- expected public reaction if submitted anyway:
  - uncertain and not worth a scarce slot for score-seeking;
  - if the public LB improved, it would imply the E272 bad-axis cap is too conservative for this branch;
  - if it worsened, it would confirm that E323-like bad-axis entanglement remains the active bottleneck.

## Public-Free Observation: E344 Counter-Axis Sign-Transfer

- submission file recommended for public test: `analysis_outputs/submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv`.
- public LB: pending.
- changed point: E344 keeps the E342 hidden lifestyle-state sign-transfer signal and adds a small E315-derived counter-axis (`w=0.10`, `cellveto`) to reduce bad-axis below the strict cap.
- expected LB reaction:
  - improve if E342's Q2/Q1/Q3 lifestyle-state signal is real and the counter-axis transfers to the public subset;
  - worsen if the E315 counter is only locally anti-bad or if the narrow bad-axis margin is still too risky.
- local evidence:
  - `3330` candidates;
  - `6` selector-promoted;
  - `6` movement-null-safe promoted;
  - top file mean `-0.000246354`, p90 `-0.000053606`, beats `0.972222`, bad-axis `0.014849687`, null strict rate `0.000000`.
- next experiment after public result:
  - if improved, build a learned counter-source selector around E315/E342 interaction;
  - if worse, audit why E315 local counter geometry fails public transfer before increasing weight or adding more counters.

## Public-Free Observation: E345 Counter-Axis Margin Refinement

- submission file available for public test: `analysis_outputs/submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv`.
- public LB: pending.
- changed point: E345 stays inside the E344 hidden lifestyle-state world model but refines the counter-axis margin with local sweeps over E315 counter weight, veto strength, and target scope.
- expected LB reaction:
  - improve if the E342+E315 basin transfers and the public subset prefers wider bad-axis margin;
  - underperform E344 if p90 margin is the dominant public sensor;
  - worsen if local movement-null safety still misses the public hidden subset.
- local evidence:
  - `6588` candidates;
  - `278` selector-promoted;
  - `40` movement-null-safe promoted;
  - selected file mean `-0.000246580`, p90 `-0.000051888`, beats `0.972222`, bad-axis `0.014655826`, null strict rate `0.000000`.
- interpretation before submission:
  - E345 strengthens the claim that E344 is a stable local basin, not a one-off;
  - E344 remains first because p90 is stronger;
  - E345 is the bad-axis-margin follow-up if public feedback suggests risk margin matters more.

## Public-Free Observation: E346 Counter-Axis Public-Analog Preflight

- submission file: none created.
- public LB: not submitted.
- changed point: E346 uses known public LB observations as fixed diagnostic axes, comparing E344/E345 movement to public-loss anatomies relative to E247.
- local observation:
  - E344 upload public-analog risk `0.051129078`, survival `0.452806122`;
  - E345 upload public-analog risk `0.051144175`, survival `0.461734694`;
  - both have direct positive E323/E216/E267/E256 alignment `0.000000000`;
  - certification-grade public-analog dominance is `False`.
- interpretation:
  - E346 provides no hard veto against E344/E345;
  - E346 also does not certify either candidate as public-transferable;
  - the known public-bad axes are not the obvious reason to avoid E344/E345, but the public subset/calibration uncertainty remains.
- next experiment after public result:
  - if E344 improves, treat public-analog hard-veto as sufficient and learn a counter-source selector;
  - if E344 worsens, search for a public subset/calibration state not represented by the E323/E216/E267/E256 axes.

## Public-Free Observation: E347 Lifestyle-State Candidate Re-Audit

- submission file recommended for public test: `analysis_outputs/submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv`.
- public LB: pending.
- changed point: E347 chooses the lower public-analog-risk E344 neighborhood row only after requiring hidden lifestyle-state alignment against E328/E337 teacher features.
- local observation:
  - E347 gate passes `3/16`;
  - selected local mean `-0.000249`;
  - selected p90 `-0.000050116`;
  - bad-axis `0.014671133`;
  - public-analog survival `0.528061224`;
  - public-analog risk `0.044818570`;
  - direct positive E323/E216/E267/E256 alignment `0`;
  - dominant state axis `rs01_Q1_jepa_resid_dateblock`;
  - state corr/enrichment dominance `1.000000/1.000000`.
- interpretation before submission:
  - E347 is the most evidence-balanced public sensor in the E342/E344 branch;
  - it sacrifices some E344 p90 margin for lower public-analog risk and better statefulness/risk explanation;
  - E344 remains the more aggressive p90 backup and E345 remains the margin backup.
- expected LB reaction:
  - improve if the public subset rewards the Q1 dateblock residual lifestyle-state plus lower public-analog risk;
  - underperform E344 if pure p90 margin matters more than public-analog/lifestyle-state balance;
  - worsen if the missing public state is outside E328/E337's hidden lifestyle teacher.

## Public-Free Observation: E348 Lifestyle-State Specificity Audit

- submission file: none new; canonical recommendation remains `analysis_outputs/submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv`.
- public LB: not submitted.
- changed point: E348 tests whether E347's lifestyle-state explanation survives controls instead of merely sounding plausible.
- local observation:
  - E348 gate passes `3/25`;
  - selected file remains E347;
  - selected Q1 state corr `0.432330`;
  - selected Q1 state enrichment `0.852584`;
  - Q1 specificity margin `0.297346`;
  - broader specificity margin `0.271772`;
  - calendar corr `0.053213`;
  - non-Q1 residual corr `0.160558`;
  - own-latent corr `0.137435`;
  - random p95 `0.134984`;
  - permuted-Q1 p95 `0.114145`;
  - E323/E216/E256 public-bad controls fail specificity.
- interpretation:
  - E348 strengthens E347 priority;
  - it does not create a new public test;
  - the next public observation should still be E347 unless the user wants the more aggressive E344 p90 sensor.

## Public-Free Observation: E349 Target/Cell Lifestyle-State Ablation

- submission file recommended for public test: `analysis_outputs/submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv`.
- public LB: pending.
- changed point: E349 converts E347 from a full movement into a compact Q1/Q2/Q3/S1 high-magnitude cell action, keeping the same hidden Q1 dateblock lifestyle-state view but removing weak/noisy cells.
- local observation:
  - `158` variants tested;
  - general gate passes `10`;
  - replacement gate passes `2`;
  - selected p90 `-0.000050035`;
  - selected bad-axis `0.014667610`;
  - public-analog survival `0.525510204`;
  - public-analog risk `0.044736209`;
  - direct E323/E216/E267/E256 positive alignment `0`;
  - Q1 state corr `0.440884`;
  - Q1 specificity margin `0.299145`;
  - changed cells vs E347 `347`.
- interpretation before submission:
  - improvement would support the compact Q1/Q2/Q3/S1 hidden lifestyle-state story;
  - deterioration while E347 remains strong would mean the removed low-magnitude/S3 cells were calibration support rather than noise;
  - a large deterioration would demote target/cell pruning and move the next question back to public-subset/calibration transfer.

## Public-Free Observation: E350 Compact Lifestyle-State Plateau

- submission file recommended for public test: `analysis_outputs/submission_e350_compactplateau_selected_compact_t45_s1_005_s3a1_00_ef54727b_uploadsafe.csv`.
- public LB: pending.
- changed point: E350 keeps the E349 compact lifestyle-state thesis but tests it as a local basin, restoring S3-tail movement and using a tiny `1.005` amplification.
- local observation:
  - `311` variants tested;
  - local gate passes `187`;
  - plateau gate passes `176`;
  - selected p90 `-0.000050233`;
  - selected bad-axis `0.014742869`;
  - public-analog survival `0.502551020`;
  - public-analog risk `0.044770778`;
  - direct E323/E216/E267/E256 positive alignment `0`;
  - Q1 specificity margin `0.317370`;
  - plateau support score `37`;
  - changed cells vs E349 `480`.
- interpretation before submission:
  - improvement would support a compact Q1/Q2/Q3/S1 plus calibrated S3-tail hidden lifestyle-state basin;
  - deterioration while E349 is better would mean S3-tail restoration or tiny amplification overstepped public calibration;
  - deterioration of both E349/E350 would demote compact target/cell editing and return priority to E347/E344 or a new public-subset calibration latent.

## Public-Free Observation: E351 Robust Plateau Selector

- submission file recommended for scarce public test: `analysis_outputs/submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv`.
- public LB: pending.
- changed point: E351 chooses a conservative representative from the E350 plateau instead of the original score-seeking rank winner.
- local observation:
  - E350 plateau candidates `176`;
  - E351 compatibility candidates `36`;
  - selected p90 `-0.000050191`;
  - p90 gain vs E349 `0.000000156`;
  - public-analog risk `0.044765398`;
  - risk delta vs E349 `0.000029189`;
  - bad-axis `0.014741236`;
  - Q1 specificity margin `0.324251`;
  - plateau support score `35`;
  - probability L1 delta vs E349 `0.006241`;
  - S3-tail alpha `0.25`.
- interpretation before submission:
  - improvement would support robust plateau selection and small S3-tail calibration;
  - underperforming E350 but beating E349 would mean stronger S3 restoration has upside but robust selection is safer;
  - underperforming E349 would mean even small S3-tail/micro-scale restoration is too aggressive and E349/E347 should regain priority.

## Public-Free Observation: E353 Public-Bad Tangent Neutralization

- submission file: none.
- public LB: not submitted.
- changed point: E353 tries to improve E351 by removing positive projection onto known public-bad movement axes.
- local observation:
  - candidates tested `52`;
  - generated neutralized candidates `48`;
  - E353 local gate passes `0`;
  - no generated risk-improver remains strict-promoted;
  - strong cleanup reduces public-analog risk but destroys p90 visibility.
- interpretation:
  - this rejects simple public-bad-axis projection as the next score route;
  - E351 remains the practical public sensor;
  - if E351 fails, the next hypothesis should be a new support/visibility latent rather than a cleaned E351 sibling.

## Public Observation: E368 Q2/S1 Row-Mask Cell-Action Latent

- submission file: `submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv`
- public LB: `0.576290429`
- current public best reference: E247 `0.5761589494`
- delta vs E247: `+0.0001314796` worse
- delta vs E95 `0.5762913298`: `-0.0000009008` better
- changed point:
  - E365-style backbone with only Q2/S1 target-cell movement;
  - learned Q2/S1 lifestyle row validity beat direct-public and null masks locally;
  - E369 public-free residual audit supported the same Q2/S1 state.
- expected LB reaction before feedback:
  - improvement would promote target-specific Q2 intervention validity plus S1 recovery validity as the live hidden law;
  - neutral/worse would mean the latent is real but not public-calibrated, especially around Q2.
- actual interpretation:
  - E368 is not catastrophic and almost ties E95, so the Q2/S1 hidden lifestyle-state signal is not pure noise;
  - it fails to beat E247 by a material margin, so it is not the current final-submission candidate;
  - the local jackknife/transfer evidence overestimated public value, likely because Q2 action health and Q2 public-risk anatomy are entangled.
- next experiment implication:
  - do not upload E370/E371/E372 derivatives as safer variants;
  - keep E247 as public-best default;
  - use E368 as a diagnostic anchor for Q2/S1 target-specific hidden lifestyle state, not as a frontier replacement.

## Public Observation: H010 Objective Mobility S1/S4 Route Jackpot

- submission file: `submission_h010_objective_s1s4_v2_uploadsafe.csv`
- public LB: `0.5781718175`
- current public best reference: E247 `0.5761589494`
- delta vs E247: `+0.0020128681` worse
- delta vs E95 `0.5762913298`: `+0.0018804877` worse
- delta vs E368 `0.576290429`: `+0.0018813885` worse
- changed point:
  - H010 preserved E247 marginals and changed only objective-stage route cells;
  - changed cells: `S1=213`, `S4=242`, all other targets unchanged;
  - local subject/dateblock route stress selected `S1↓/S4↑` as the only jackpot candidate.
- expected LB reaction before feedback:
  - improvement would support objective mobility-stage routing as a real public-hidden law;
  - worsening would mean S4 mobility latent exists locally but direct S1/S4 route reassignment is public-miscalibrated.
- actual interpretation:
  - this is a strong public falsification of H010 as a submission route;
  - the damage is much larger than E368's miss, so the public subset does not tolerate the S1/S4 rank/route reassignment;
  - H009/H010 local route stress is now known to be anti-transfer for public, despite clean reverse-control behavior locally.
- next experiment implication:
  - do not submit S1/S4 route-rank variants;
  - do not use local S4/S1 route logloss as a standalone selector;
  - if mobility latent is reused, it needs a public-calibrated action-health target or a much smaller model-integrated feature, not output-space rank reassignment.

## Public-Free Observation: H011 H010 Public-Inversion Action-Health

- submission file prepared: `submission_h011_public_inversion_rowtop_all_k50_a1_uploadsafe.csv`
- public LB: not submitted yet
- changed point:
  - treats H010's failed S1/S4 movement as a public-negative action-health teacher;
  - inverts only the top `50` H010-active rows on S1 and S4;
  - changed cells: `S1=50`, `S4=50`, all other targets unchanged.
- expected LB reaction:
  - improvement would mean H010 exposed a reversible public-negative action axis and HS-JEPA can use failed actions as target representations;
  - worsening would reject anti-H010 route inversion and imply H010 was not a reversible route law but a local rank/materialization artifact.
- local/public-free observation:
  - generated candidates: `63`;
  - selected H010-axis coefficient: `-0.545892`;
  - linear H010-axis public delta estimate: `-0.001098809`;
  - selector mean/p90 delta vs E247: `+0.000200937` / `+0.000573326`;
  - selector beats-current rate: `0.256250`.
- interpretation:
  - this is intentionally not a safe selector-promoted candidate;
  - it is a high-information public sensor for whether H010's failure can be inverted into action health.
- next experiment:
  - submit H011 only if spending a slot on a world-changing sensor is acceptable;
  - after feedback, either promote failed-action inversion as an HS-JEPA primitive or kill the anti-H010 branch.

## Public Observation: H012 Public-Equation HS-JEPA

- submission file: `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`
- public LB: `0.5681234831`
- previous public best reference: E247 `0.5761589494`
- delta vs E247: `-0.0080354663`
- delta vs E95 `0.5762913298`: `-0.0081678467`
- delta vs H010 `0.5781718175`: `-0.0100483344`
- changed point:
  - treats known public LB deltas as equations over hidden public labels/subset;
  - solves a continuous pseudo-public posterior `q`;
  - moves E247 toward the top `1200` posterior cells at logit alpha `0.7`.
- expected LB reaction:
  - improvement would mean public LB observations can be used as a same-level HS-JEPA target representation, not merely as after-the-fact scores;
  - a hard miss would mean the public-equation system is too underidentified or subset-specific for direct pseudo-label materialization.
- local/public-free observation:
  - known public observations: `20`;
  - equations vs E247: `19`;
  - best posterior config LOO MAE `0.000320737`;
  - best posterior config LOO Spearman `0.935088`;
  - generated candidates: `238`;
  - selected posterior mean/p90 delta vs E247: `-0.006446397` / `-0.004693170`;
  - changed cells: `1200`;
  - max probability delta: `0.294110`.
- actual interpretation:
  - this is a decisive public validation of the public-equation HS-JEPA branch;
  - the realized gain is larger than the posterior mean forecast by `0.0015890693`, so the model was not merely optimistic on paper;
  - the private-risk question remains open, but the public bottleneck is no longer "no usable latent"; H012 found a public-readable hidden-state posterior.
- next experiment:
  - promote public-equation latent reconstruction into the core HS-JEPA architecture;
  - decompose H012 by target, row, subject/dateblock, posterior scenario stability, and same-subject memory compatibility before another broad materialization.

## External Public Observation: Sleep-State Conditioned Same-Subject Memory

- source: attached text document from another high-scoring participant;
- reported submission file: `submission_v106_sleep_state_conditioned_memory.csv`;
- reported public LB: `0.5703952266`;
- delta vs H012: `+0.0022717435` worse;
- changed point:
  - extends same-subject temporal label memory;
  - weights past labels by date distance, sleep-state similarity, and sensor-quality similarity;
  - argues that GroupKFold is a cold-subject stress rather than a fair validation for same-subject memory.
- interpretation:
  - this independently supports the within-subject temporal continuity hypothesis;
  - it also warns that raw feature similarity is useful mainly when it conditions memory retrieval, not when it is materialized as a broad output edit;
  - because the actual prediction file is unavailable, it cannot be added as an equation anchor yet.
- next experiment:
  - use this as an H014 design prior: H012 posterior cells should be audited against subject/date proximity, sleep-state similarity, and sensor-quality similarity to separate stable human-state signal from public-equation overfit.

## Public-Free Observation: H013 Raw Human-State JEPA Gate

- submission file prepared: `submission_h013_raw_hs_jepa_health_top_route_r140_c260_a0.75_4a91266c_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - does not directly submit all of H012;
  - builds raw human-state context from app/screen/charging/activity/mobility/HR/light/calendar/payday features;
  - applies H012 posterior movement only on rows/cells where raw-state action-health and KNN target-route agreement support the move.
- expected LB reaction:
  - improvement would mean raw human-state context is a real HS-JEPA gate for public-equation action;
  - worsening would reject scalar row-gating and imply the missing target is row x target action-health or public/private subset calibration.
- local/public-free observation:
  - generated candidates: `1190`;
  - full jackpot-gated candidates: `0`;
  - high-risk candidates: `168`;
  - selected file changes `260` cells on `126` rows;
  - posterior delta `-0.001233534`;
  - selector mean/p90 delta `+0.000486533` / `+0.001506255`;
  - route agreement `1.000000`, consistency `0.991453`.
- interpretation:
  - raw human-state creates coherent H012 slices but does not pass public-free action-health;
  - H013 should not supersede H012 as the current highest-upside public sensor.
- next experiment:
  - learn action health at row x target level instead of applying a scalar row gate to H012.

## Public-Free Observation: H014 Sleep-State Memory Audit

- submission files prepared: `submission_h014_*_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - tests whether V106-style same-subject sleep-state/sensor-quality memory explains H012;
  - builds memory agreement and reliability for H012 changed cells;
  - generates memory-compatible keep-H012 candidates and memory-conflict revert candidates.
- expected LB reaction:
  - if memory-compatible cells kept most of H012's posterior gain, a memory-regularized H012 file could be a safer final;
  - if gain concentrated in memory-disagree cells, H012 is not reducible to same-subject memory and should not be pruned this way.
- local/public-free observation:
  - H012 changed cells audited: `1200`;
  - memory-agree rate: `0.405000`;
  - memory-agree gain share: `0.279671`;
  - high-alignment/high-reliability gain share: `0.101482`;
  - best kept-gain candidate: `0.358133`;
  - all H014 candidates: `diagnostic_only`.
- interpretation:
  - subject-time memory is real but insufficient as the H012 regularizer;
  - Q3 is the main memory-compatible target, while the larger S-target gain is mostly memory-disagree.
- next experiment:
  - use memory as a diagnostic/private-risk feature only;
  - test H012 self-feedback directly because H012 is driven by public-equation geometry more than subject-memory geometry.

## Public-Free Observation: H015 H012 Self-Feedback Public Equation

- submission file prepared: `submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - adds H012's actual public LB as the new strongest public-equation anchor;
  - re-solves hidden public-state posterior with H012 as the current prediction tensor;
  - moves H012 toward the new posterior on `1600` high-consistency cells.
- expected LB reaction:
  - improvement would mean H012 was under-amplified and public-equation HS-JEPA can recursively sharpen;
  - worsening would mean H012 is the practical fixed point and self-feedback should stop.
- local/public-free observation:
  - known public observations: `21`;
  - equations vs H012: `20`;
  - best LOO Spearman: `0.986466`;
  - best LOO MAE: `0.001312381`;
  - posterior mean/p90 delta vs H012: `-0.001586219` / `-0.001149849`;
  - posterior beats-H012 rate: `0.966667`;
  - max probability delta vs H012: `0.051642`.
- interpretation:
  - this is the current highest-information next submission sensor;
  - the main risk is public self-feedback overconfidence because selected configs are dominated by `h012_sharp`.
- next experiment:
  - if a single big public slot is available, submit H015;
  - after feedback, either promote recursive public-equation sharpening or freeze H012 as the public-equation fixed point.

## Public-Free Observation: H016 Public-Subset Weight HS-JEPA

- submission file prepared: `submission_h016_public_subset_gain_all_k1000_a0.75_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - keeps H012 as anchor;
  - treats known public LB deltas as evidence about public cell weights, not only hidden labels;
  - applies H015 movement only to `1000` inferred public-weight/gain-compatible cells.
- expected LB reaction:
  - improvement would mean H012/H015 should be interpreted through a diffuse public cell-weight field, and future public-equation actions should be gated at row x target level;
  - worsening would mean the weight field is useful for explaining old public submissions but not safe as a new action materializer.
- local/public-free observation:
  - best weight config LOO MAE `0.000013654`;
  - LOO p90 abs `0.000026381`;
  - LOO Spearman `0.990977444`;
  - uniform-weight MAE `0.000885430`;
  - effective weight count `1747.348299`;
  - permutation null median LOO MAE `0.004329919`;
  - permutation null max Spearman `0.660150`;
  - selected predicted subset-weight delta vs H012 `-0.000296297`;
  - full H015 predicted subset-weight delta vs H012 `+0.000164649`.
- interpretation:
  - this is the first strong evidence that public feedback contains a stable cell-weight/gain representation, not just a pseudo-label posterior;
  - it is not a tiny hard public subset: weights are diffuse over almost all cells;
  - H016 is lower-upside than H015 but is a cleaner test of whether broad recursive sharpening should be constrained by public-weighted action health.
- next experiment:
  - if the next public slot should test recursive amplification, use H015;
  - if it should test public cell-weight action selection, use H016;
  - use the result to decide whether HS-JEPA's public-equation branch should be label-posterior-first or weight/gate-first.

## Public-Free Observation: H017 Joint Label x Public-Weight HS-JEPA

- submission file prepared: `submission_h017_joint_label_weight_oracle_gain_all_k1650_a1_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - models public LB deltas as a joint hidden label and public cell-weight equation;
  - selected joint state is almost exactly `H012 public posterior + H016 mean public weights`;
  - moves H012 further toward the original H012 public posterior on `1650` high joint-gain cells.
- expected LB reaction:
  - improvement would mean H012 was an under-moved posterior step and H016 weights identify where posterior-completion is public-healthy;
  - worsening would mean the original H012 posterior explains old public deltas but is too aggressive as a new action target.
- local/public-free observation:
  - joint LOO MAE `0.000001044`;
  - joint LOO Spearman `1.000000`;
  - permutation-null median LOO MAE `0.001672425`;
  - permutation-null max Spearman `0.200902`;
  - q/w movement from priors is almost zero;
  - predicted joint delta vs H012 `-0.000574501`;
  - H015 under same joint sensor `+0.000164654`;
  - H016 under same joint sensor `-0.000296289`;
  - changed cells `1650`, max probability delta `0.107121`.
- interpretation:
  - H017 is not a newly discovered independent latent. It is a compatibility and posterior-completion test.
  - It is more aggressive than H016 and less dependent on post-H012 self-feedback than H015.
- next experiment:
  - public feedback on H017 would decide whether H012's public posterior should be treated as an action target or only as an explanatory latent;
  - if H017 fails, stop posterior-completion and look for a private/public risk sensor before moving further from H012.

## Public-Free Observation: H018 Hard-Label Public-World HS-JEPA

- submission file prepared: `submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - keeps H012 as anchor;
  - samples binary public label worlds from the H017 posterior instead of fitting only continuous pseudo-labels;
  - reweights sampled worlds by how well their weighted loss deltas explain known public LB deltas;
  - moves H012 toward the resulting hard-world posterior on all `1750` cells.
- expected LB reaction:
  - improvement would mean H017's public-equation posterior is not merely smooth calibration and survives binary hidden-label constraints;
  - worsening would mean hard-world conditioning is a good diagnostic but too aggressive as a submission action.
- local/public-free observation:
  - sampled hard worlds `90000`;
  - best posterior `soft_t0.00035_p1.5`;
  - posterior equation MAE `0.000005557`;
  - best sampled hard-world MAE `0.000167740`;
  - ESS `19756.395104`;
  - hard posterior shift from H017 prior `0.002394823`;
  - permutation-null stress beats all `300` public-delta permutations across best/top100/median/p01/p05 errors;
  - predicted hard-world delta vs H012 `-0.000603041`;
  - mean abs difference from H017 `0.002414278`.
- interpretation:
  - H018 is a binary-aware strengthening of H017, not a new independent direction;
  - it is the cleanest current test of whether posterior-completion should be interpreted as hidden hard-label-world inference.
- next experiment:
  - submit H018 only if the next public slot is meant to distinguish continuous posterior-completion from binary public-world posterior-completion;
  - if public slots are scarce and H017/H018 are redundant, prioritize the one whose failure mode is more informative for the paper story.

## Public-Free Observation: H019 Hard Public Row-Subset HS-JEPA

- submission file prepared: `submission_h019_row_subset_hardworld_gain_all_r240_a1_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - forces public-equation latent into sampled row-level public masks;
  - uses H018/H017 label proxies but removes the free cell-weight assumption;
  - materializes a row-exclusion variant of H018 by leaving the lowest posterior-inclusion rows unchanged.
- expected LB reaction:
  - improvement over H018/H012 would mean public row identity is actionable and HS-JEPA should infer public/private row masks;
  - worsening while H018 improves would mean row-subset structure is explanatory but row exclusion is not the right action.
- local/public-free observation:
  - best row-mask sampled config `h017_joint`, subset size `150`;
  - top100 mask MAE `0.000074821`;
  - best posterior `h018_hard_k125_soft_t4e-05_p2`;
  - posterior MAE `0.000027461`;
  - posterior Spearman `0.998496`;
  - inclusion range `0.370519-0.786440`;
  - all `300` public-delta permutations lose to real row masks;
  - primary H019 row-posterior delta vs H012 `-0.000611233`;
  - H018 under the same row posterior is slightly stronger at `-0.000615495`.
- interpretation:
  - public-equation latent is compatible with a realistic broad row-subset split;
  - H019 does not prove low-inclusion rows should be removed from H018.
- next experiment:
  - prioritize H018 if the goal is strongest posterior-completion action;
  - use H019 if the next public slot is meant to test row-level public/private subset actionability.

## Public-Free Observation: H020 Joint Target-Vector Hardworld HS-JEPA

- submission file prepared: `submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - keeps H012 as anchor;
  - replaces independent row-target hard labels with sampled row-level 7-bit target vectors;
  - uses H018 marginal probabilities plus optional train global/subject target-vector priors;
  - moves H012 toward the selected joint-vector posterior on all `1750` cells.
- expected LB reaction:
  - improvement would mean the public-equation posterior is closer to a coherent row-level hidden Q/S state than to independent cell marginals;
  - worsening would mean joint-vector consistency is explanatory under old public equations but too aggressive as a new action materializer.
- local/public-free observation:
  - sampled joint-vector worlds: `70000` per config;
  - best sampled config by config score: `global_b0.15`;
  - best sampled world MAE `0.000175369`;
  - top100 sampled world MAE `0.000260939`;
  - selected posterior: `none_b0_soft_t0.00012_p2`;
  - posterior MAE `0.000012623`;
  - posterior p90 abs `0.000023274`;
  - posterior Spearman `0.995488722`;
  - ESS `977.953487`;
  - mean/max shift vs H018 `0.010608997` / `0.044670350`;
  - all `300` public-delta permutation nulls are worse on tracked joint-vector world metrics;
  - selected rowweighted delta vs H012 `-0.001105455`;
  - H018 under the same report is `-0.000636475`, H019 is `-0.000631235`.
- interpretation:
  - row-level target-vector consistency is now the strongest high-risk posterior-completion worldview;
  - train target co-occurrence is not yet the action driver, because the selected posterior has `beta=0`;
  - the useful constraint is currently "one row should choose one coherent 7-label hidden state", not "copy train vector frequencies."
- next experiment:
  - if one public slot is reserved for the biggest worldview-changing posterior-completion test, H020 is more informative than another H018/H019 sibling;
  - if the goal is cleaner attribution and lower action novelty, H018 remains the baseline binary-world test.

## Public-Free Observation: H021 Human-State Conditional Vector-Prior Gate

- submission file prepared: `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv`
- public LB: not submitted
- changed point:
  - learns a row-level 7-bit target-vector prior from raw human-state context;
  - rejects direct q_hs replacement;
  - applies the H020 direction only to `1200` cells where the human-state vector prior and H020 direction agree strongly enough to beat a row-permuted human-prior null.
- expected LB reaction:
  - improvement would mean the human-state part of HS-JEPA can ground the public-equation row-vector posterior and reduce public-equation-only overfit;
  - worsening would mean q_hs is locally predictive but not public-action-calibrated, and H020/H012 should remain public-equation-first.
- local/public-free observation:
  - best human-state train prior `subject_all_k10` marginal BCE `0.617584875` versus global vector prior `0.664614445`;
  - selected candidate changes `1200` cells across `248` rows;
  - H020-equation delta vs H012 `-0.000684129`;
  - H020 gain retained `0.618866184`;
  - row-permuted q_hs null median is worse by `0.005549353`.
- interpretation:
  - q_hs is a valid human-state latent view;
  - its safe action is gating H020, not replacing H020 probabilities.
- next experiment:
  - submit H021 only if the next public slot should test the human-state bridge of HS-JEPA;
  - if public budget prioritizes the pure biggest posterior-completion test, H020 remains the more direct bet.

## Public-Free Observation: H022 Human-State Conditioned Vector-World Posterior

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - injects H021's `q_hs` into the H020 row-level target-vector world sampler/posterior;
  - tests whether human-state context should be the vector-world posterior prior instead of a post-hoc H020 gate.
- expected LB reaction:
  - if a beta-positive posterior had won and then improved public LB, HS-JEPA's human-state prior would become part of the final probability generator;
  - because no beta-positive posterior won, submitting H022 diagnostic files would mostly test public-equation posterior sharpening, not the human-state prior.
- local/public-free observation:
  - best config score is weak human prior `hs_b0.1`, with top100 world MAE `0.000260035`;
  - selected posterior is `none_b0_top250_t0.0005`, with MAE `0.000014073`, p90 abs `0.000026312`, Spearman `0.990977444`;
  - best positive human-state posterior is weaker: `hs_b0.1_top250_t0.00012`, MAE `0.000024950`, p90 abs `0.000043720`;
  - public-delta permutation null passes strongly for `hs_b0.1`;
  - q_hs row-permutation null is mixed: top100 world search benefits from real q_hs, but best/median world metrics do not.
- interpretation:
  - q_hs is useful as a proposal/search/gate latent, not as the final posterior density;
  - no H022 upload-safe candidate should be submitted by default.
- next experiment:
  - turn q_hs into a proposal/Pareto constraint or action-health feature before materialization;
  - do not force q_hs beta unless it wins posterior selection and row-permutation stress.

## Public-Free Observation: H023 Human-State Proposal/Pareto Vector-World Posterior

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - keeps H012 as the anchor and H020/H022 row-vector worlds as the target representation;
  - uses H021 `q_hs` only as proposal/Pareto energy after public-compatible worlds are sampled;
  - explicitly tests row-permuted `q_hs` controls before allowing any upload-safe file.
- expected LB reaction:
  - if an H023 candidate were promoted and improved, it would mean human-state geometry can choose a public/private-safe action posterior;
  - because no candidate passed the row-permutation public-fit stress, uploading H023 diagnostic files would mainly test an unproven materializer.
- local/public-free observation:
  - public-error top1000 worlds are human-state aligned: real energy `4.877889323` vs row-permutation null median `5.234522555`, p `0.012345679`;
  - selected Pareto posterior: `pareto_top1000_lam0.2_t0.00012`;
  - posterior MAE/p90/Spearman: `0.000031100` / `0.000059357` / `0.989473684`;
  - human-state KL survives row-permutation stress (`rowperm_hs_kl_p=0.016393443`);
  - public posterior fit fails row-permutation stress (`rowperm_public_p=0.754098361`);
  - root upload-safe H023 files: none.
- interpretation:
  - H023 is useful evidence that the public-equation vector-world manifold is coupled to human-state geometry;
  - it is not evidence that q_hs can safely choose the next submission.
- next experiment:
  - learn an action-health or public/private calibration target using H023 energy as one feature;
  - do not submit q_hs-Pareto candidates until public-fit row-permutation stress improves.

## Public-Free Observation: H024 Action-Health Decoder

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - treats known public LB results as fixed sensors for action health;
  - scores known/public and H015-H023 candidates by movement geometry, public-good/public-bad axes, and H012/H015/H021/H023 latent cell-state features;
  - promotes only if an unseen candidate beats H012 under aggregated decoder scenarios and public-score permutation stress.
- expected LB reaction:
  - if a candidate had passed and improved, it would validate action-health decoding as the missing HS-JEPA materializer;
  - because no candidate passed, submitting H024-selected diagnostics would only test an unstable ranker.
- local/public-free observation:
  - known sensors `20`, candidate rows `407`;
  - best LOO decoder MAE `0.000773`, Spearman `0.969925`, pairwise `0.947368`;
  - top unknown H015 `k100` candidate predicted median `0.570054`, p10/p90 `0.559653-0.580761`;
  - support better than H012 only `0.15`;
  - selected-vs-H012 permutation p `0.841`.
- interpretation:
  - public-score geometry is real on known anchors;
  - it is not enough to safely choose a new post-H012 action.
- next experiment:
  - create independent action-health supervision or a new hidden-state target;
  - do not spend public attempts on H015-H023 candidates selected only by this decoder.

## Public-Free Observation: H025 Train-Counterfactual Action-Health Decoder

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - creates independent action-health supervision from train labels by measuring counterfactual logloss gain for many subject/time/KNN/global proposal actions;
  - ranks known and unknown post-H012 candidates without using public LB as the direct training target;
  - promotes only if row/time transfer, known-public-bad anchor sanity, and row-permutation placement stress all pass.
- expected LB reaction:
  - if promoted and improved, it would validate train-counterfactual action health as the missing HS-JEPA materializer;
  - because no file passed, submitting the selected diagnostic would test a failed row-placement stress rather than a live public hypothesis.
- local/public-free observation:
  - row/time OOF Spearman `0.021090879`;
  - row/time top10 lift `0.004425758`;
  - selected unknown diagnostic `hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a1.2_a639be88.csv`;
  - selected row-permutation p `0.576666667`;
  - top ranked known files include public-bad Q2/residual probes.
- interpretation:
  - train-side action-health is a real but incomplete representation;
  - public-safe action health requires public/private calibration and shortcut veto.
- next experiment:
  - model train action-health and public-bad/domain-shift energy jointly;
  - reject any decoder that ranks known public-bad Q2/residual probes above H012-compatible candidates.

## Public-Free Observation: H026 Public/Private Calibration-Veto Decoder

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - combines H025 train-counterfactual action-health with H024 public decoder features;
  - adds explicit public-bad veto energy for known public-bad Q2/residual shortcut axes;
  - materializes only diagnostic post-H012 variants when both source and cell scores look favorable.
- expected LB reaction:
  - if a variant had passed and improved, it would validate scalar public/private shortcut veto as the missing HS-JEPA action-health bridge;
  - because no variant passed, submitting the selected diagnostic would mainly test a public-stress failure.
- local/public-free observation:
  - source sanity succeeds: H012 ranks first, while known public-bad JEPA/Q2/residual anchors are demoted;
  - generated variants `272`;
  - selected diagnostic file:
    `hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a0p35_v0p35_h015_direct_all_a0.1_35c68bc9.csv`;
  - selected H025 row-permutation p `0.000000`;
  - selected H024 predicted public median/p10/p90 `0.574388293` / `0.561070999` / `0.597525659`;
  - support below H012 `0.166667`;
  - H024 public-score permutation p `0.898000`.
- interpretation:
  - public-bad veto is real enough to fix known-anchor ranking;
  - it is not enough to create a public-safe post-H012 action.
- next experiment:
  - do not submit H026 variants;
  - define a richer public/private calibration target or generate candidates whose action geometry is public/private-aware before vetoing.

## Public-Free Observation: H027 Born Public/Private-Aware Generator

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - uses the external V106 memory idea as an independent view: same-subject temporal memory conditioned by sleep-state and sensor-quality similarity;
  - generates candidate cells only after combining H015/H020/H023 posterior targets, H021/H023 human-state agreement, H014 memory safety, H026 public-good/bad energy, and H025 train-action predicted gain;
  - tests whether public/private calibration must happen at birth rather than after generation.
- expected LB reaction:
  - if a variant had passed and improved, it would validate birth-time public/private action generation as the missing HS-JEPA materializer;
  - because no file passed, uploading H027 diagnostics would test a failed local stress result rather than a live public hypothesis.
- local/public-free observation:
  - generated variants `1648`;
  - selected diagnostic:
    `hitl/h027_public_private_aware_generator_jepa/submission_h027_h015_public_feedback_bad_axis_escape_S1S2S3_k80_a0p25.csv`;
  - H024 predicted public median/p10/p90 `0.569712461` / `0.560020747` / `0.583215022`;
  - support below H012 `0.150000`;
  - H025 row-permutation p `0.383333333`;
  - H024 public-score permutation p `0.822000000`.
- interpretation:
  - V106-style same-subject memory supports the repeated-subject world model, but it does not explain most of H012 and does not rescue H015/H020/H023 materialization;
  - public/private-aware generation over existing posterior cells is still not enough.
- next experiment:
  - stop adding scalar wrappers over H015/H020/H023;
  - define a new calibration target or a new generator whose proposals are not inherited from the same posterior-completion pool.

## Public-Free Observation: H028 Public/Private Action-Gradient JEPA

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - learns public response to whole-submission interventions from H012;
  - treats known public deltas as an action-gradient target rather than a cell posterior;
  - generates rollback/amplification/descent variants only as diagnostics.
- expected LB reaction:
  - if a variant had passed and improved, it would validate smooth public-gradient continuation from H012;
  - because no variant passed, uploading the diagnostic would mainly test a failed extrapolation.
- local/public-free observation:
  - selected public-gradient fit has LOO MAE `0.001204883`;
  - shuffled-public-delta null is beaten with p `0.000000`;
  - top generated file is priced by H024 at `0.576388429`;
  - support below H012 only `0.083333333`;
  - H025 row-permutation p `0.710000000`;
  - H024 public-score permutation p `0.918000000`.
- interpretation:
  - known public interventions contain real coarse response geometry;
  - around H012 that geometry says "the basin is isolated" more than "continue descending."
- next experiment:
  - model H012 as a needle basin/invariant, not as a smooth optimum.

## Public-Free Observation: H029 H012 Needle-Basin Invariant

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - tests whether H012 is explained by support, amplitude, target/subject block,
    same-subject memory agreement, or exact row-target placement;
  - creates support-ray, rollback, memory-only, outside-support, and target-wise
    row-permuted H012 variants.
- expected LB reaction:
  - if a variant had passed, H012 could be simplified into an interpretable
    invariant such as target rollback or memory-compatible support;
  - because no variant passed, uploading the diagnostic would test a known basin break.
- local/public-free observation:
  - generated variants `102`;
  - best diagnostic `rollback_target_S1`;
  - H024 predicted median `0.570494744`;
  - support below H012 `0.116666667`;
  - H024 public-score permutation p `0.858000000`;
  - H025 row-permutation p `0.613333333`;
  - target-wise row permutation collapses to best median about `0.581149687`.
- interpretation:
  - H012 is not target-level calibration, memory pruning, or smooth amplitude;
  - exact row-target placement is part of the hidden basin.
- next experiment:
  - infer row/subset identity directly inside the public-equation solver.

## Public-Free Observation: H030 Row-Target Identity Public Equation

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - gives each row-target cell an allowance prior from H012 support, H016 public
    weights, H019 row subset, H020 joint-vector state, and H014 memory;
  - tests whether row-target identity can anticipate H012 without directly
    seeing H012 as an equation.
- expected LB reaction:
  - if an action had passed, it would validate row-target identity priors as the
    missing public-equation translator;
  - because no action passed, H030 remains a latent discovery rather than a
    submission route.
- local/public-free observation:
  - independent held-out H012 prediction `-0.007550142` versus actual
    `-0.008035466`, error `0.000485324`;
  - generated candidates `756`;
  - best diagnostic H024 median `0.572160346`;
  - support below H012 `0.100000000`;
  - H024 public-score permutation p `0.923333333`;
  - H025 row-permutation p `0.670000000`.
- interpretation:
  - row-target identity is real enough to explain much of H012;
  - direct allowance-prior materialization does not preserve the H012 action basin.
- next experiment:
  - use external memory as a contrastive view of the H012 public core, then test
    whether that core is action-safe.

## Public-Free Observation: H031 Memory-Conflict Public-Core JEPA

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - reads the V106 same-subject sleep-state memory document as an independent
    contrastive world model;
  - tests whether H012 gain is concentrated in memory-agree or memory-disagree
    cells;
  - generates conflict-core amplification, conflict-core swap, memory-agree
    rollback, and core-reconstruction variants.
- expected LB reaction:
  - if a variant had passed and improved, it would mean memory-conflict cells are
    an amplifiable public core;
  - because no variant passed, the result says memory conflict is explanatory
    but not yet an action.
- local/public-free observation:
  - H012 changed cells audited `1200`;
  - memory-disagree cells `714`;
  - memory-disagree gain share `0.720328567`;
  - memory-agree gain share `0.279671433`;
  - generated candidates `482`;
  - best diagnostic H024 median/p10/p90
    `0.569809630` / `0.561924630` / `0.581936465`;
  - support below H012 `0.150000000`;
  - H024 public-score permutation p `0.800666667`;
  - H025 row-permutation p `0.183333333`.
- interpretation:
  - V106-style memory is real, but H012's public jump is mostly in cells that
    memory would not choose;
  - the live bottleneck is now the probability-action translator for an already
    partially identified row-target core.
- next experiment:
  - learn the amplitude/route/calibration law for memory-conflict public-core
    cells instead of amplifying them mechanically.

## Public-Free Observation: H035 Basin-Boundary Support-Swap JEPA

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - tests local support replacement around H012 instead of another posterior
    continuation;
  - swaps or softens H012 support cells under target/row/support-count
    constraints;
  - scores candidates with q-loss, route margin, H024 pre-state margin,
    public-score permutation, and H025 row-placement stress.
- expected LB reaction:
  - if a candidate had passed and improved, it would mean H012 is an editable
    row-target identity basin;
  - because no candidate passed, submitting H035 would mostly test a known
    action-health failure.
- local/public-free observation:
  - generated candidates `585`;
  - q-improving candidates `55`;
  - best q-loss delta `-0.000286222`;
  - route-safe count `0`;
  - pre-state-better count `0`;
  - strict gate count `0`;
  - selected diagnostic q-loss delta `+0.000512108`;
  - selected route/pre-state margins `+0.017292336` / `+0.012214437`;
  - public-score permutation p `0.660666667`;
  - H025 row-permutation p `0.610000000`.
- interpretation:
  - q posterior still suggests local moves, but route/pre-state action-health
    rejects all of them;
  - H012 is locally locked under support-swap operations.
- next experiment:
  - infer a global hidden public label/subset or private/public split, rather
    than editing H012 support locally.

## Public-Free Observation: H036 Global Public-World Solver JEPA

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - treats all known public LB scores as sensors for a sampled hidden public row
    subset and row/target binary label world;
  - uses H012/H015/H017/H018/H020 q priors, H019/H030/H035 row priors, and H013
    human-social/calendar row priors;
  - materializes top-world posterior actions only after world-null, H024, and
    H025 stress.
- expected LB reaction:
  - if a candidate had passed and improved, it would mean the global public
    world can be translated directly into a post-H012 action;
  - because no candidate passed, submitting H036 would mostly test a known
    translation failure.
- local/public-free observation:
  - sampled worlds `55488`;
  - best world MAE `0.000202825`;
  - best world RMSE/Spearman `0.000249943` / `0.969924812`;
  - permutation-null p `0.000000`;
  - null best-MAE mean/median `0.000957` / `0.000964`;
  - strongest internal candidate expected delta `-0.002238821`;
  - selected diagnostic `h036_target_Q2_k140_a1_c140_9ef667d6`;
  - selected expected delta `-0.000235201`;
  - selected H024 pre-H012 margin/support
    `+0.001430749` / `0.250000000`;
  - selected H025 row-permutation p `0.590000000`.
- interpretation:
  - global hidden public-world geometry is real and non-random;
  - direct posterior materialization is still not action-safe;
  - human-social row priors are useful as proposal context but not as final
    probability labels.
- next experiment:
  - train a world-to-action translator from H012/H030/H035/H036 positives and
    failures, or separate public-safe versus public-overfit components before
    moving probabilities.

## Public-Free Observation: H037 Fixed-Point Translator JEPA

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - keeps H012 support fixed and translates H036 world pressure only through the
    original E247-to-H012 ray;
  - tests aligned-support amplification, conflict damping, dual amplitude
    actions, target-wise ray scaling, row-public ray scaling, and support-only
    small q-pulls.
- expected LB reaction:
  - if a candidate had passed and improved, it would mean H012 is a reusable
    fixed-point action ray;
  - because no candidate passed, submitting H037 would mainly test a known
    H024/H036 disagreement.
- local/public-free observation:
  - H012 support `1200`;
  - H036-aligned support `903`, score sum `244.595425`;
  - H036-conflict support `297`, score sum `20.929529`;
  - generated candidates `253`;
  - world-cell gain candidates `44`;
  - negative-H024-margin candidates `4`;
  - candidates satisfying both `0`;
  - H024 support >= `0.6` candidates `0`;
  - selected diagnostic `h037_support_qpull_k180_a0.03_c176_6b9ae6d4`;
  - selected world row/cell deltas
    `-0.000042258` / `-0.000062846`;
  - selected H024 margin/support
    `+0.000479900` / `0.250000000`;
  - selected H025 row-permutation p `0.106666667`.
- interpretation:
  - H036 pressure is mostly inside H012 support, but scalar ray translation is
    not enough;
  - public-world gain and H024-safe movement are still not aligned under this
    action family.
- next experiment:
  - learn route/calibration/private-public transfer jointly, using H036 as
    teacher and H037 as negative support-preserving examples.

## Public-Free Observation: H038 Memory-Transition Translator JEPA

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - uses V106/H014 same-subject sleep-state memory as a contrastive context;
  - tests whether cells where H012 breaks subject memory are the missing
    world-to-action translator;
  - generates exception q-pulls, exception posterior pulls, memory-repair
    rollbacks, row-transition vector moves, and world-exception veto moves.
- expected LB reaction:
  - if a candidate had passed and improved, it would mean H012's post-best
    route is a memory-transition exception law;
  - because no candidate passed, submitting H038 would mostly test a known
    H024/H025 rejection.
- local/public-free observation:
  - H012 support `1200`;
  - memory-exception support `523`;
  - memory-exception posterior gain sum `8.133135268`;
  - memory-exception H036 cell-score sum `200.501588821`;
  - broad-world exception cells `245`, score sum `183.788898304`;
  - generated candidates `459`;
  - world-cell gain candidates `42`;
  - posterior-gain candidates `2`;
  - negative-H024-margin candidates `0`;
  - H024 support >= `0.55` candidates `0`;
  - selected diagnostic `h038_memory_repair_all_k140_a0.38_4edd633f`;
  - selected world/posterior deltas
    `+0.000443266` / `+0.000266868`;
  - selected H024 margin/support
    `+0.002193776` / `0.250000000`;
  - selected H025 row-permutation p `0.836666667`.
- interpretation:
  - memory-transition is a real explanation for H012's anatomy;
  - memory-transition is not a direct action route;
  - use memory conflict as a translator feature, not as a target to amplify.
- next experiment:
  - train or search a route/calibration/private-public translator with
    H036/H037/H038 candidates as positive/negative action examples.

## Public-Free Observation: H039 Failed-Translator Nullspace JEPA

- submission file prepared: none promoted
- public LB: not submitted
- changed point:
  - uses all materialized H036/H037/H038 failed candidate directions as
    negative action supervision;
  - removes all-bad or world-good/action-bad principal directions from H036
    world pressure;
  - optionally projects the residual through candidates least disliked by H024.
- expected LB reaction:
  - if a candidate had passed and improved, it would mean post-H012 translation
    is approximately a failed-direction nullspace law;
  - because no candidate passed, submitting H039 would mainly test a known
    low-gain residual failure.
- local/public-free observation:
  - source candidates `816`;
  - all-bad PC1 energy `0.651576382`;
  - all-bad PC8 cumulative energy `0.895838636`;
  - world-bad PC8 removal leaves raw world norm ratio `0.210274586`;
  - generated/scored candidates `520`;
  - world-cell gain candidates below threshold `0`;
  - posterior-gain candidates below threshold `0`;
  - negative-H024-margin candidates `0`;
  - H024 support >= `0.55` candidates `0`;
  - selected diagnostic
    `h039_transition_world_allow_cone_world_bad_pc8_exception_k238_cap0.022_583e2255`;
  - selected world/posterior deltas
    `-0.000018978` / `-0.000009471`;
  - selected H024 margin/support
    `+0.000238744` / `0.250000000`;
  - selected H025 row-permutation p `0.510000000`.
- interpretation:
  - failure directions are structured, but linear removal also removes most
    public-world signal;
  - post-H012 decoder is unlikely to be a local linear nullspace.
- next experiment:
  - move from local projection to discrete route/private-public assignment, or
    infer the public subset/label equations more directly.

## Public-Free Observation: H040 Discrete Route-Assignment JEPA

- submission file prepared: none promoted
- public LB: not submitted
- external reference:
  - attached V106 document reports
    `submission_v106_sleep_state_conditioned_memory.csv` public LB
    `0.5703952266`;
  - this supports same-subject human-state memory, but H012 remains better by
    `0.0022717435`.
- changed point:
  - treats public/private/memory/rollback as discrete row routes;
  - moves whole rows or row-supported cells toward H036 world, H012 posterior,
    H014/H038 memory, or E247 rollback;
  - uses H024/H025 stress before any public submission.
- expected LB reaction:
  - if a candidate had passed and improved, it would mean the post-H012
    bottleneck is a row-route decoder;
  - because no candidate passed, H040 files should not spend a public slot.
- local/public-free observation:
  - generated/scored candidates `328`;
  - selected diagnostic
    `h040_public_route_world_p140_world_high_a0.45_h012_v0_support_b0_all_0985acf7`;
  - selected world/posterior deltas
    `-0.001426068` / `-0.001708677`;
  - selected H024 margin/support
    `+0.007548586` / `0.250000000`;
  - selected H025 row-permutation p `0.280000000`;
  - candidates with `world_cell_delta < -0.0005`: `198`;
  - candidates with `h025_score < 0`: `181`;
  - candidates with negative H024 margin: `0`;
  - candidates with H024 support >= `0.55`: `0`.
- interpretation:
  - simple row-route assignment is a useful latent state but a bad direct
    action;
  - the hidden route should become a prior inside public-subset equation
    inference, not a post-H012 edit.
- next experiment:
  - infer public/private subset equations directly with route priors and
    H012-phase constraints.
