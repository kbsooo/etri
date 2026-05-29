# Experiment Log

작성일: 2026-05-28

실험은 `Observe -> Wonder -> Hypothesize -> Falsify -> Build -> Stress -> Decide` 형식으로 기록한다. public LB는 최적화 대상이 아니라 hidden-DGP sensor로 사용한다.

## E00. File and Artifact Inventory

- Observe: train target table은 450 rows, submission sample은 250 rows, subject는 10명이다. raw log parquet는 phone/watch sensor별로 분리되어 있고, JEPA/analysis outputs에 다수의 submission과 report가 있다.
- Wonder: 이미 생성된 submission universe와 JEPA reports가 plateau 원인을 설명하는가?
- Hypothesis: plateau는 feature 부족보다 기존 artifacts에 남은 validation/public selector mismatch로 설명될 수 있다.
- Method: root, `analysis_outputs`, `jepa`, `data`의 submission/report/CV/public-fit artifacts를 인벤토리했다.
- Result: 요구된 root 산출물 8개는 없었다. 기존 핵심 보고서는 analysis_outputs와 jepa에 흩어져 있었다.
- Decision: 새 root-level 문서를 source of truth로 만든다.

## E01. Data Dissection Forensics

- Observe: train/submission은 단순 future split이 아니고, subject별 target prior가 매우 크다.
- Wonder: row order/boundary가 target을 직접 누출하는가?
- Hypothesis: hidden subject/session block 구조는 있지만 label copy는 위험하다.
- Method: subject/block prior, boundary copy, lag/periodicity, feature stump 분석.
- Result: subject target rate std가 Q/S 대부분에서 크다. boundary copy는 submission-like geometry에서 subject prior보다 나쁘다. single feature stump도 stage2보다 나쁘다.
- Interpretation: hidden structure는 row label copy가 아니라 block-rate/measurement-process 쪽이다.
- Next: block-level target representation과 calibration risk로 변환한다.

## E02. Hidden Block Sequence Motif

- Observe: hidden rows가 block 단위로 나타나며, train flanks/endpoint/date phase가 있다.
- Wonder: train label context가 hidden block rate를 예측하는가?
- Hypothesis: row-level prediction보다 block-level count/rate latent가 더 안정적이다.
- Method: label flanks, endpoint motif, weekday, hidden block length 기반 pseudo-hidden block rate prediction.
- Result: best motif `motif_same_r1_k16_tau1p0_s8p0` weighted logloss `0.597394`, subject mean 대비 `-0.015607`, weighted R2 `0.3672`.
- Interpretation: semantic target representation은 존재한다. 하지만 direct submission blend는 raw05/a2c8보다 안전하지 않았다.
- Next: label-flow semantic JEPA target으로 재설계.

## E03. Hidden Block Rate Reconstruction

- Observe: strict subject split에서 simple endpoint/local priors는 약하다.
- Wonder: block-rate reconstruction이 subject prior를 충분히 이기는가?
- Hypothesis: endpoint/motif block latent는 weak but real signal이다.
- Method: endpoint local non-overlap, Markov, strict subject variants.
- Result: best pseudo-hidden method `endpoint_local_nonoverlap` weighted logloss `0.609749`, subject mean 대비 `-0.003252`, weighted R2 `0.3028`.
- Interpretation: 직접 row probabilities를 크게 밀 만큼 강하지 않다.
- Next: block-rate latent를 gate/energy로 쓴다.

## E04. JEPA Latent Residual and Public Failure

- Observe: JEPA latent residual은 local OOF를 크게 개선하는 듯 보였지만 public에서 악화했다.
- Wonder: JEPA가 semantic latent를 배운 것인가, public-bad shortcut을 배운 것인가?
- Hypothesis: aggressive JEPA latent는 bad public axes를 탄다.
- Method: raw timeline I-JEPA, latent residual discovery, targetwise LeJEPA, nested guardrail.
- Result: all-target latent residual OOF `0.560757`였지만 nested guardrail 실패. `submission_jepa_latent_q2_w0p45.csv` public `0.5798012862`, LeJEPA targetwise strict public `0.5802468192`, residual probe public `0.5812273278`.
- Interpretation: prediction loss만 좋은 latent는 제출 안전성을 보장하지 않는다.
- Next: latent geometry/isotropy/energy diagnostic을 submission gate로 사용한다.

## E05. Public Anchor Bottleneck and Pairwise Order Selector

- Observe: current best `a2c8` public `0.577439321`, raw05 public `0.5775263072`; gap은 `0.000086986`뿐이다.
- Wonder: 이 작은 edge를 selector가 안정적으로 구분할 수 있는가?
- Hypothesis: current plateau는 candidate 부족이 아니라 selector resolution 부족이다.
- Method: public anchor LOOCV/L2O proxy, inverse selector, hidden subset stress, pairwise order selector.
- Result:
  - best fixed LOOCV proxy MAE는 약 `0.000546739`, raw05-a2c8 gap은 이의 `0.159x`.
  - hidden subset selector stress passing families `0/7`.
  - universe/JEPA/hiddenloc audits에서 strict resolved-better 또는 submit-gate candidate `0`.
  - pairwise order selector는 33개 model이 key order를 보존했지만 strict submit-gate candidate는 `0`.
  - baseline-relative better-than-a2c8 candidates는 46개였으나 모두 `hiddenloc_bridge`이고 selector conflict가 있었다.
  - formal hard selector criterion `LOO/L2O MAE <= 0.00040`, rank accuracy `> 0.90`, key order preservation을 동시에 만족한 모델은 `0/36`이었다. 가장 가까운 passing-order near miss도 max(LOO,L2O) MAE `0.000444` 이상이었다.
- Interpretation: public subset signal은 있으나 현재 selector가 a2c8보다 작은 delta를 reliable하게 rank하지 못한다.
- Decision: micro-refine 제출은 정보량이 낮다. 다음은 selector-only falsification 또는 large low-bad-axis representation branch다.

## E06. Measurement Process Signal

- Observe: raw value보다 observation process가 residual과 상관을 가진다.
- Wonder: missingness는 sensor artifact인가, behavior proxy인가?
- Hypothesis: missingness/rhythm은 behavioral signal이지만 direct rule은 위험하다.
- Method: measurement-process feature residual correlation, subject/weekend deviation.
- Result: 예시로 Q3 `mp_hr_pre6h_obs_frac_same_weekend_dev` residual corr `-0.206`, S4 `mp_sensor_active_count_pre6h_same_weekend_dev` residual corr `+0.184`.
- Interpretation: feature family는 유효하나 train/test shift와 calibration stress가 필수다.
- Next: calibration risk/latent energy feature로 사용.

## E07. Cross-View JEPA Surprise

- Observe: view-to-view prediction residuals가 local CV를 개선한다.
- Wonder: cross-view residual은 hidden behavior인가, split shortcut인가?
- Hypothesis: cross-view surprise는 local signal이지만 public safety는 geometry에 달려 있다.
- Method: raw-log views 간 masked latent prediction, residual PCs, guarded repeated-subject scan.
- Result: base OOF `0.5675309247`; targetwise best deltas Q1 `-0.00442`, Q3 `-0.00237`, S1 `-0.00201`, S2 `-0.00566`, S3 `-0.00211`, S4 `-0.00389`. 32 strict repeated-subject passes.
- Interpretation: signal은 real. 하지만 direct submission-safe 여부는 미검증.
- Next: latent geometry diagnostic과 energy gate.

## E08. Universe and Bad-Axis Audits

- Observe: 후보는 충분히 많지만 strict winner가 없다.
- Wonder: bad-axis projection만으로 frontier를 넘을 수 있는가?
- Hypothesis: bad-axis removal은 필요조건일 수 있지만 충분조건은 아니다.
- Method: full submission universe audit, badaxis_lowenergy_jepa ensemble.
- Result: full valid submission universe 15871에서 strict resolved better 0. low-bad-axis JEPA ensemble도 resolved better 0.
- Interpretation: candidate generation보다 candidate selection/hidden subset localization이 병목이다.
- Next: target dependency energy와 label-flow block latent로 larger safe movement 탐색.

## E09. Hidden Public Localization and Bridge

- Observe: inverse/local solutions가 특정 target/sample deltas를 제안한다.
- Wonder: local public improvement direction을 stress-safe하게 bridge할 수 있는가?
- Hypothesis: hidden-public localization can guide a small correction if it avoids bad axes.
- Method: hidden_public_localization_selector, hidden_public_local_bridge, stress scoring.
- Result: localization selected inverse solutions but submit_gate `0`; bridge generated 1530 candidates, stress-scored 580, submit_gate `0`, probe_gate 399.
- Interpretation: local direction은 존재하나 stress-safe selector와 충돌한다.
- Next: only information-probe if submission slot is used deliberately; not a strong candidate.

## E10. Label-Flow Block-Rate JEPA Stress

- Observe: 기존 `two_level_proto_jepa`, semantic prototype, transductive episode count, MP-count conditioning branch가 label-flow/block-rate representation을 이미 일부 만들었다.
- Wonder: 이 representation은 숨은 block target-rate manifold를 잡은 semantic latent인가, 아니면 또 local CV shortcut인가?
- Hypothesis: hidden blocks live on a low-dimensional label-rate manifold; useful JEPA target should preserve block target rates, be predictable from strict context, improve downstream OOF under geometry/subject-chunk stress, and avoid public pairwise bad-axis gates.
- Method: `analysis_outputs/label_flow_blockrate_jepa_stress.py`로 기존 semantic fold outputs와 556개 transductive/MP-count submission 후보를 stress했다.
- Result:
  - semantic configs summarized: 60.
  - semantic stress-pass configs: 1.
  - best oracle_rate_r2: 0.347118.
  - best pred_rate_r2: 0.092778 overall, but the only strict semantic pass was `two_level_proto / past_label / label_rate K=10 / raw_mean K=8 / context_plus_true_coarse_train` with pred_rate_r2 0.026047 and fold-min -0.077889.
  - downstream best geometry delta vs stage2: -0.003334; best subject_chunk delta: -0.000537.
  - 556 candidate files scored by public pairwise gate: pair_submit_gate 0, pair_probe_gate 0, pair_control_better_than_a2c8_gate 0. Best p90 delta vs a2c8 was +0.000125668.
- Interpretation: label-flow/block-rate latent is real enough to keep as semantic energy, but the current probability translations are not submit-safe.
- Decision: H03/H15 strengthen as representation hypotheses; direct label-flow/MP-count submission branch fails public-risk stress. Next action is a gated correction, not direct replacement.

## E11. Label-Flow Gated Candidate Scan

- Observe: E10 showed semantic label-flow/block-rate signal but all direct probability translations failed public pairwise gates.
- Wonder: can the semantic signal be used only where it lowers target-dependency energy and stays raw05/a2c8-compatible?
- Hypothesis: gated label-flow movement can produce a safer candidate than direct transductive/MP-count submissions if movement is restricted to rows with improved Q/S dependency energy and small raw05 distance drift.
- Method: `analysis_outputs/label_flow_gated_candidate_scan.py` started from `a2c8`, used top E10 donor directions, and applied clipped donor-base deltas only on rows passing dependency-energy and raw05-distance gates. It scanned 7240 candidates over alpha, energy threshold, raw margin, max step, and donor choice, then scored all candidates with the pairwise public-order selector.
- Result:
  - generated candidates: 7240.
  - `pair_submit_gate`: 0.
  - `pair_control_better_than_a2c8_gate`: 50.
  - `pair_probe_gate`: 3263.
  - `pair_selector_conflict`: 0.
  - best conservative control/probe: `analysis_outputs/submission_label_flow_gated_f1046674.csv`, alpha 0.15, gate_frac 0.020, mean_abs_move_vs_a2c8 0.000063, pair_delta_vs_a2c8_p90 `-0.000000029`, pair_beats_a2c8_rate 0.908, raw05 p90 delta `+0.000022`, bad_axis_abs_load 0.0361.
  - best p90/upside control/probe: `analysis_outputs/submission_label_flow_gated_ff8df011.csv`, alpha 0.70, gate_frac 0.024, mean_abs_move_vs_a2c8 0.000370, pair_delta_vs_a2c8_p90 `-0.000000687`, pair_beats_a2c8_rate 0.919, raw05 p90 delta `+0.000002`, bad_axis_abs_load 0.0323.
- Interpretation: gating fixes the E10 direct-translation failure enough to create clean control/probe candidates, but the edge is still far below selector error and below a strict submit threshold.
- Decision: no strong submit candidate yet. If a submission slot is used, `f1046674` is the conservative information sensor and `ff8df011` is the higher-upside semantic-gate sensor. Neither should be sold as a reliable 0.577439 beater.

## E12. Targetwise Amplified Label-Flow Gate

- Observe: E11 repaired sign but not magnitude. The movement was row-gated but not target-specialized.
- Wonder: is the useful label-flow direction concentrated in a target subset?
- Hypothesis: if target-dependency gate is real, targetwise masks should reveal which Q/S component can be safely enlarged before raw05/bad-axis stress breaks.
- Method: `analysis_outputs/label_flow_targetwise_amplified_gate_scan.py` scanned 9444 candidates using target masks, larger alpha/max_step, dependency-energy row gate, raw05 row compatibility, and the same pairwise public-order stress.
- Result:
  - pair_submit_gate 0, control 3024, probe 6780, conflict 0.
  - best p90 vs a2c8 `-0.000005997`, best mean vs a2c8 `-0.000084359`.
  - strongest target mask: S4. Best S4 candidate `analysis_outputs/submission_label_flow_twampl_b8c66b64.csv` moved 70/250 rows, only S4, with pair_delta_vs_raw05_p90 `+0.000000769` and bad_axis_abs_load `0.03608`.
- Interpretation: targetwise gate confirms the actionable direction is mostly S4, with a smaller Q3/Q2-Q3 component. Still below strict submit threshold.
- Decision: combine S4 and Q-side atoms instead of pushing all targets.

## E13. Label-Flow Combo Gate

- Observe: E12 S4 and Q3/Q2-Q3 atoms were individually public-risk clean but too small.
- Wonder: do targetwise gated atoms add constructively, or does stress break when S4 and Q-side moves are combined?
- Hypothesis: if S4 and Q3 label-flow corrections are orthogonal pieces of the same hidden block-rate latent, their pairwise edge should add while bad-axis load stays low.
- Method: `analysis_outputs/label_flow_combo_gate_scan.py` combined selected S4/Q3/Q2-Q3/E11 atoms with weight grids and scored 11248 candidates.
- Result:
  - pair_submit_gate 0, control 8094, probe 11245, conflict 0.
  - best p90 vs a2c8 `-0.000035162`, best mean vs a2c8 `-0.000380143`.
  - best combo before focused push: `analysis_outputs/submission_label_flow_combo_3d536109.csv`, S4+Q3 atoms, bad_axis_abs_load `0.01530`, pair_delta_vs_raw05_p90 `-0.000081`.
- Interpretation: S4 and Q3 atoms are additive and lower bad-axis/raw05 risk, but broad combo grid still falls short of strict submit p90 threshold `-0.00005`.
- Decision: run a focused threshold scan only around the best S4+Q3 atom family.

## E14. Focused S4+Q3 Submit-Threshold Scan

- Observe: E13 was close to strict gate and showed no selector conflict.
- Wonder: can the best S4+Q3 atom family cross the strict pairwise submit threshold without raw05/bad-axis failure?
- Hypothesis: controlled amplification of the best S4 atom plus Q3 atoms can turn the semantic gate from a sensor into a frontier-challenge candidate.
- Method: `analysis_outputs/label_flow_combo_focused_submit_scan.py` scanned 180 focused weight combinations over atoms `a00=S4`, `a01=Q3 strong`, `a03=Q3 conservative`.
- Result:
  - pair_submit_gate 61, control 180, probe 180, conflict 0.
  - best p90 vs a2c8 `-0.000065217`, best mean vs a2c8 `-0.000303563`.
  - high-upside submit-gate candidate: `analysis_outputs/submission_label_flow_focused_6b9335b1.csv`, weights `9.0|0.75|4.0`, pair_delta_vs_a2c8_p90 `-0.000065217`, pair_delta_vs_raw05_p90 `-0.000131438`, bad_axis_abs_load `0.01725`.
  - conservative submit-gate candidate: `analysis_outputs/submission_label_flow_focused_1bbfb735.csv`, weights `7.5|0.75|1.0`, pair_delta_vs_a2c8_p90 about `-0.000054`, pair_delta_vs_raw05_p90 about `-0.000118`, bad_axis_abs_load `0.02067`.
- Interpretation: the immediate plateau can be pierced locally by a hidden block-rate/label-flow gate concentrated on S4 plus Q3. This is the first strict-gate candidate, but it is still a 0.00005-scale move, not evidence of a path to 0.54.
- Decision at the time: promote `6b9335b1` and `1bbfb735` to candidate submissions with explicit selector-overfit/private-risk warning. Superseded by E15 below.

## E15. Focused Label-Flow Independent Survival Review

- Observe: E14 candidates were selected by the same pairwise public-order selector used as their submit gate, so they may be selector-family artifacts rather than robust hidden-public moves.
- Wonder: do S4+Q3 focused candidates still look public-positive under the older hidden-subset ridge selector and anchor scenario stress?
- Hypothesis: if H17 is a real hidden-public correction rather than pairwise-selector overfit, at least some E14 pair-submit candidates should beat a2c8 in a majority of old-selector scenarios while keeping low bad-axis and Q3+S4-focused movement.
- Method: `analysis_outputs/focused_label_flow_survival_review.py` rescored 163 label-flow candidates, including all 61 E14 pair-submit candidates plus E11-E13 sensors, through `hidden_subset_selector_stress.candidate_stress_scores`.
- Result:
  - pair-submit candidates inside review set: 61.
  - independent survival candidates: 0.
  - strict independent survival candidates: 0.
  - best old-selector p90 delta vs a2c8 among reviewed candidates: `+0.000569397`.
  - `6b9335b1`: pair p90 `-0.000065217`, old-selector p90 `+0.000675515`, scenario beat rate `0.277992`.
  - `1bbfb735`: pair p90 `-0.000054316`, old-selector p90 `+0.000638679`, scenario beat rate `0.277992`.
  - corr(pairwise p90 delta, old-selector p90 delta) `-0.881`; pairwise-improving movement is anti-aligned with old hidden-subset geometry.
- Interpretation: E14 did not pierce the plateau robustly. It found a target-local pairwise-selector direction, but the independent anchor geometry prices that direction as worse than a2c8. H17 remains a useful diagnostic about S4/Q3 label-flow, not a submit-safe strategy.
- Decision: demote `6b9335b1` and `1bbfb735` from frontier-challenge submissions to information-only sensors. The next action is not public submission; it is resolving the selector conflict or finding a larger low-bad-axis movement that both selectors agree on.

## E16. Selector Conflict Decomposition

- Observe: E15 showed pairwise p90 and old hidden-subset p90 are anti-aligned for the focused label-flow family.
- Wonder: is the conflict caused by one obvious bad feature, or by underidentified selector geometry?
- Hypothesis: if E14 is overfit, the pairwise selector should not be unanimously positive; it should rely on a favorable scenario tail and target-local features, while old selector remains scenario-majority negative because no known anchor validates the S4+Q3 direction.
- Method: `analysis_outputs/selector_conflict_decomposition.py` decomposed pairwise-order and old hidden-subset ridge predictions for pinned label-flow candidates into per-feature contributions relative to a2c8.
- Result:
  - `1bbfb735`: old hidden-subset better_rate `0.285714`, pairwise full-fit better_rate `0.500000`.
  - `6b9335b1`: old hidden-subset better_rate `0.285714`, pairwise full-fit better_rate `0.500000`.
  - E11 tiny gated sensors reached pairwise full-fit better_rate `0.666667`, but movement is far below decision scale.
  - pairwise contributions are mixed: S4 target-local and max-move terms often help, while residual-span/projection terms hurt.
  - old hidden-subset contributions are also mixed, but never provide scenario-majority endorsement for S4+Q3 focused movement.
- Interpretation: this is underidentification, not a clean feature-level bug. Current known public anchors do not contain a positive example for this exact S4+Q3 correction, so the selectors cannot agree whether it is true signal or surrogate artifact.
- Decision: next candidate work must either add an independent anchor-like validation source for S4/Q3 direction or find a larger safe movement that does not depend on the favorable pairwise tail.

## E17. S4/Q3 Independent Anchor Gap Audit

- Observe: E15-E16 imply the focused S4+Q3 direction may be underidentified because neither selector has an independent positive anchor for that exact movement.
- Wonder: do any existing candidate families already contain a S4/Q3-shaped candidate that both public-sensitive selectors support?
- Hypothesis: if S4/Q3 label-flow is robust public signal, at least one existing family should provide a Q3/S4-shaped candidate with old hidden-subset majority support and non-positive pairwise p90 risk.
- Method: `analysis_outputs/old_positive_anchor_pairwise_rescore.py` rescored old-selector-positive candidates with the pairwise selector. `analysis_outputs/s4q3_anchor_gap_audit.py` then triangulated three sources: the pairwise-scored universe, the focused S4/Q3 family, and the old-positive rescore.
- Result:
  - pairwise-scored universe: 1893 candidates, 21 with Q3/S4 move share >= 0.70, 46 with pairwise p90 below a2c8, 3 old-majority candidates, but `0` candidates satisfying Q3/S4 shape plus old-majority support.
  - focused S4/Q3 family: 163/163 Q3/S4-shaped and pairwise-positive candidates, but old-majority support `0`.
  - old-positive rescore: 212 candidates, 97 old-majority candidates, but Q3/S4-shaped candidates `0` and pairwise-p90-negative candidates `0`.
  - two-selector agreement candidates for S4/Q3 anchor: `0`.
- Interpretation: current artifacts do not contain an independent S4/Q3 positive anchor. The missing object is not another focused S4/Q3 weight sweep; it is a new validation signal for this direction or a larger safe movement that both selectors can price consistently.
- Decision: keep the submission gate closed for focused S4/Q3. Next work should move away from weight rescan and toward selector reconciliation, anchor discovery, or a new representation branch that creates a larger low-bad-axis signal.

## E18. S4/Q3 OOF Anchor Audit

- Observe: E17 showed the existing public-stress artifact universe lacks a S4/Q3 positive anchor. The remaining cheap source is the large OOF archive.
- Wonder: can existing OOF validation act as the missing independent S4/Q3 anchor?
- Hypothesis: if local validation contains the missing anchor, OOF candidates with strong stable Q3/S4 gains should overlap with pairwise or old hidden-subset public support.
- Method: `analysis_outputs/s4q3_oof_anchor_audit.py` scanned 5167 OOF arrays against the stage2 OOF baseline, computed Q3/S4 logloss deltas plus subject/rowblock/month scenario stability, and joined any existing pairwise/old selector scores.
- Result:
  - OOF files scanned: 5167.
  - matched submissions: 5155.
  - local Q3/S4 strong candidates: 1578.
  - already matched pairwise selector rows: 9.
  - already matched old selector rows: 2.
  - OOF anchor-like candidates: 0.
  - strict S4/Q3 OOF anchor-like candidates: 0.
- Interpretation: OOF archive contains many locally strong Q3/S4 candidates, but existing selector overlap is too small and gives no anchor. OOF is a validation view, not yet a resolution.
- Decision: directly rescore the top local OOF candidates through both selectors.

## E19. S4/Q3 Top OOF Selector Rescore

- Observe: E18 found many stable local Q3/S4 OOF improvements but too little selector overlap.
- Wonder: if we score the strongest local OOF candidates directly, do any survive pairwise and old hidden-subset public stress?
- Hypothesis: a true independent OOF anchor should be local-Q3/S4 strong, pairwise-positive, old-majority, and preferably Q3/S4-shaped in test movement.
- Method: `analysis_outputs/s4q3_oof_top_selector_rescore.py` selected the top 400 local Q3/S4 OOF candidates, resolved 399 to submission CSVs, computed public-anchor features, ran `candidate_stress_scores`, and then applied the pairwise selector.
- Result:
  - top OOF candidates scored: 399.
  - pairwise p90 negative: 0.
  - pairwise majority: 0.
  - old-majority: 0.
  - pair probe/control/submit gates: 0/0/0.
  - selector conflict: 0 because selector support is simply absent, not mixed.
  - q3s4_shape70: 0; strongest OOF candidates are broad Q3-dominant/public-mask-aware moves, not clean S4/Q3 movement.
  - strict S4/Q3 OOF anchor-like candidates: 0.
- Interpretation: local OOF strength is not the missing anchor. It is mostly another local/public-mask-aware validation shortcut and is strongly priced as worse by both public-sensitive selectors.
- Decision: do not use local OOF Q3/S4 gains as submission evidence. This strengthens the conclusion that the bottleneck is validation/public-subset mismatch and selector-resolvable movement, not lack of local S4/Q3 candidate generation.

## E20. Block / Measurement Selector Rescore

- Observe: E17-E19 ruled out the existing S4/Q3 artifact universe and OOF archive as the missing independent anchor. The next cheap possibility is that older block, hidden-block, pre-sleep measurement, raw05-block, or public-block candidates already contain a larger low-bad-axis movement that was not rescored through both selectors.
- Wonder: is the plateau caused by ignoring a non-S4/Q3 block/measurement candidate family, or do these branches also fail to produce selector-resolvable public-positive movement?
- Hypothesis: if existing block/measurement JEPA candidates contain the missing large safe movement, at least one candidate should show pairwise p90 below a2c8, pairwise majority support, old hidden-subset majority support, and low bad-axis energy.
- Method: `analysis_outputs/block_measurement_selector_rescore.py` collected and deduplicated 3808 files from block-scale, block-public, hidden-block, JEPA block-count/raw-corrector, pre-sleep measurement, public-presleep, and raw05-blockcount sources; 3800 non-anchor candidates were feature-scored, old hidden-subset stressed, and pairwise-order stressed.
- Result:
  - pairwise p90 negative: `0/3800`.
  - pairwise majority: `52/3800`.
  - old hidden-subset majority: `3/3800`.
  - two-selector majority: `0/3800`.
  - pair submit/control/probe gates: `0/0/63`.
  - large low-bad movement candidates: `2505`, but large-lowbad plus two-selector support: `0`.
  - raw05 blockcount refine was the nearest clean probe family: best pairwise p90 `+0.000010793`, old p90 around `+0.000574`, old beat rate around `0.36`.
  - pre-sleep measurement candidates were broad and risky: best pairwise p90 around `+0.000509`, best old p90 around `+0.001025`.
- Interpretation: the existing block/measurement universe contains many real movements and many low-bad-axis files, but none cross the sign boundary needed to challenge a2c8. Measurement-process direct translation is especially unsafe. The nearest raw05-blockcount files are useful sensors, not submissions.
- Decision: no new public submission from existing block/measurement candidates. The bottleneck is not missed candidate retrieval; it is still selector-resolvable movement or a new representation/selector source.

## E21. Selector Support Topology Audit

- Observe: E15-E20 repeatedly show either pairwise support without old hidden-subset support, or old support without pairwise support. We need to know whether the intersection is merely rare, target-specific, or empty across the already scored universe.
- Wonder: are we missing a small intersection cell between pairwise-public and old hidden-subset selectors, or do the two selectors genuinely favor different movement manifolds?
- Hypothesis: if the current candidate universe contains a robust public-positive direction, some candidate should land in two-selector majority support. If not, pair-only and old-only zones should have different target/movement shapes.
- Method: `analysis_outputs/selector_support_topology_audit.py` merged deduplicated scored candidates from broad pairwise universe, focused label-flow review, old-positive rescore, OOF-top rescore, and block/measurement rescore. It classified support zones by pairwise p90/majority and old hidden-subset scenario majority.
- Result:
  - two-selector majority: `0`.
  - pair-only: `465` candidates; pair-strict p90 `209`, pair-submit `61`, median old beat rate `0.266`, median Q3/S4 share `0.639`.
  - old-only: `97` candidates; pair-strict p90 `0`, median pair beat rate `0.146`, median Q3/S4 share `0.396`.
  - pair-probe-not-majority: `56` candidates, mostly raw05-blockcount-like probes; median old beat rate `0.297`.
  - by dominant target, S4 owns most pairwise submit/probe support (`61` submit, median pair rate `0.962`) but has old majority only `2`; Q3 owns most old-majority support (`88`) but has no two-selector support.
- Interpretation: the missing cell is structural, not just a bad shortlist. Pairwise support is S4/Q3-heavy and target-local; old support is Q3/raw05-public-drift-like and pairwise-vetoed. More candidate retrieval from existing families is low value.
- Decision: next useful work is selector reconciliation or a public-sensor submission deliberately designed to decide which selector is miscalibrated. Without that, no candidate should be promoted as an improvement submission.

## E22. Selector Disambiguation Sensor Design

- Observe: E21 left two incompatible support zones: pair-only S4/Q3 candidates and old-only Q3/raw05-drift candidates. We need to decide which sensor, if any, gives the most information per public submission.
- Wonder: do known public anchors already tell us which selector is less reliable, and can that guide a diagnostic submission order?
- Hypothesis: if old hidden-subset support is largely raw05-like, the known raw05 public result should already weaken it. If pairwise support better preserves known anchor order, a diagnostic public sensor should test pair-only S4/Q3 rather than old-only raw05-drift.
- Method: `analysis_outputs/selector_disambiguation_sensor_design.py` compared selector reliability on known anchors and selected one high-contrast, one conservative pair-only sensor plus two hold-only alternatives.
- Result:
  - A2C8 public is `0.5774393210`; raw05 public is `0.5775263072`; A2C8 beats raw05 by `0.000086986`.
  - Pairwise public-order selector: `33/36` models preserve key order; raw05 direction correct rate `0.916667`; best LOO MAE `0.000218`, best L2O MAE `0.000444`.
  - Old hidden-subset selector: `0/7` models pass gate; raw05 direction correct rate `0.0`; it endorses raw05-like geometry even though raw05 is public-worse than A2C8.
  - Best single diagnostic sensor: `analysis_outputs/submission_label_flow_focused_1bbfb735.csv`, pair p90 `-0.000054316`, old p90 `+0.000638679`.
  - High-contrast diagnostic sensor: `analysis_outputs/submission_label_flow_focused_6b9335b1.csv`, pair p90 `-0.000065217`, old p90 `+0.000675515`.
  - Raw05-blockcount and old-only sensors are hold: raw05-blockcount best pair p90 is positive, and old-only is redundant with the known raw05 public observation.
- Interpretation: old hidden-subset stress remains useful as a cautionary veto, but it should not dominate submission choice when it contradicts known raw05/A2C8 public order. If a public slot is used, it should be explicitly diagnostic and pair-only S4/Q3 should be tested first.
- Decision: do not claim an improvement candidate. If the user wants one information-rich public sensor, submit `1bbfb735`; if it improves, reopen H17 and downweight old hidden-subset for S4/Q3 movement. If it worsens, close focused S4/Q3 amplification and do not submit `6b9335b1`.

## E23. Label-Flow Sensor Scale Curve

- Observe: E22 selected `1bbfb735` as the best information-rich public diagnostic, but full-strength movement still has old-selector p90 around `+0.000639`. Before spending a public slot, test whether lower amplitude or target masks preserve pairwise signal while reducing old-selector risk.
- Wonder: is the S4/Q3 selector conflict merely amplitude-driven, or is it directional?
- Hypothesis: if the conflict is amplitude-driven, a smaller A2C8-to-S4/Q3 movement should keep pairwise support and flip old hidden-subset scenario majority or at least create a two-selector-majority candidate.
- Method: `analysis_outputs/label_flow_sensor_scale_curve.py` generated logit-space blends from A2C8 toward `1bbfb735` and `6b9335b1` across masks `full`, `q3_s4`, `s4`, `q3`, `q2_q3_s4`, `s3_s4` and scales `0.05` to `1.00`; scored all variants with pairwise public-order and old hidden-subset stress.
- Result:
  - 108 generated scale/mask variants were scored.
  - Every mask family had pairwise p90 negative at all 9 scales, but two-selector majority was `0` for every family.
  - Best balanced lower-risk sensor: `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv`, pair p90 `-0.000034496`, old p90 `+0.000571958`, movement `0.003931`.
  - Lowest-old-risk pairwise-negative sensor: `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s3_s4_s0p35_1a1ac81b.csv`, pair p90 `-0.000016726`, old p90 `+0.000550965`, movement `0.001875`.
  - Maximum pairwise contrast remains a full `6b9335b1`-direction variant with pair p90 `-0.000065217`, but old p90 `+0.000675515`.
- Interpretation: scaling can reduce old p90, but it does not change old scenario beat rate enough to create majority support. The conflict is directional, not just amplitude-driven. Lower-scale files are risk-controlled sensors, not safer improvement candidates.
- Decision: E23 does not reopen submission gate. If the purpose is maximum information, keep E22 `1bbfb735`. If the purpose is lower-risk public diagnostic, use `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv`. Do not treat either as a 0.54 path.

## E24. Label-Flow Localized Sensor Audit

- Observe: E23 showed that amplitude scaling does not reconcile pairwise S4/Q3 support with old hidden-subset veto. The remaining cheap question is whether the conflict is caused by applying the movement on the wrong row subset rather than by target direction.
- Wonder: can subject/date/block/phase/energy/sign localization make the S4/Q3 label-flow direction selector-consistent?
- Hypothesis: if public-sensitive S4/Q3 movement is localized to a hidden DGP block, then some row mask should preserve pairwise p90 improvement and raise old hidden-subset support to majority, creating at least one two-selector-majority candidate.
- Method: `analysis_outputs/label_flow_localized_sensor_audit.py` generated 960 logit-space localized variants from A2C8 toward `1bbfb735` and `6b9335b1`. Row masks included subject, subject complement, global date bins, within-subject phase bins, contiguous date blocks and complements, delta-energy quantiles, S4 delta sign, weekday/weekend, and subject-energy groups. Target masks were `q3_s4` and `s4`; scales were `1.0` and `0.65`. Each file was scored with the pairwise public-order selector and old hidden-subset stress.
- Result:
  - candidates scored: `960`.
  - pair p90 negative: `807`.
  - old-majority: `0`.
  - two-selector majority: `0`.
  - localized sensor candidates under the loose diagnostic rule: `8`, all from the tiny `id02_b02` date block.
  - `id02_b02` is subject `id02`, sleep dates `2024-10-03` to `2024-10-10`, `8/250` rows.
  - best loose localized candidate: `analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_block_id02_b02_s1p00_ea4fdc0b.csv`, pair p90 `-0.000000203`, old p90 `+0.000580036`, old beat rate `0.413127`, movement `0.0000127`.
  - best broad pairwise localization remained old-negative: `not_subject_id07` full-scale variants had pair p90 around `-0.000074` but old p90 around `+0.000660` and old beat rate `0.277992`.
- Interpretation: simple localization does not resolve the selector conflict. The only loose candidates are too small to matter and do not reach old majority. This is a directional/world disagreement, not merely an amplitude or row-mask problem.
- Decision: no public submission from localized sensors. Use E24 as negative evidence against more S4/Q3 localization sweeps. The next useful branch needs either a new selector/anchor source or a representation that creates a larger sign-consistent movement, not another subject/date/block mask around the same pair-only direction.

## E25. Direction Probe Selector Reconciliation

- Observe: current worktree also contains newer score-oriented probes from target-ablation, sparse ladder, blockwise bad-axis repair, direction ensembles, and minimax mixtures. These were not yet reconciled with the same pairwise-vs-old selector gate used to reject focused S4/Q3 label-flow sensors.
- Wonder: do the larger mixmin/direns/sparseladder candidates finally create a selector-resolvable movement that the S4/Q3 branch lacks?
- Hypothesis: if the score-oriented sparse/JEPA/direct-label direction is the missing 0.54 path, at least one of the current priority probes should show pairwise p90 below a2c8, old hidden-subset majority, and acceptable bad-axis load.
- Method: `analysis_outputs/direction_probe_selector_reconciliation.py` scored 22 priority probes: mixmin, direns, sparseladder, blockorth, targetabl, inverse7blend, and inv7gate files. It joined available actual-anchor/combo/honest-CV metadata, then ran `candidate_stress_scores` and pairwise public-order `score_candidates`.
- Result:
  - probes scored: `22`.
  - pair p90 negative: `0`.
  - pair majority: `0`.
  - old majority: `0`.
  - two-selector majority: `0`.
  - submit-shape candidates: `0`.
  - closest by pairwise p90 was `analysis_outputs/submission_inverse7blend_1040423d.csv`, pair p90 `+0.000122038`, old p90 `+0.000617292`, old beat rate `0.003861`.
  - best target-ablation row by this gate was `analysis_outputs/submission_targetabl_1049b8e7.csv`, pair p90 `+0.000293056`, old p90 `+0.000801965`, old beat rate `0.011583`.
  - mixmin/direns/sparseladder files had pair p90 around `+0.000835` to `+0.000960` and old p90 around `+0.00096` to `+0.00111`, despite strong honest CV and combo-stress metadata.
- Interpretation: the newer large-movement score-probe branch is not strict-survival validated. It may still be a public experiment under a different belief system, because actual-anchor/combo/honest-CV evidence is not the same selector as E25, but it does not solve the current hidden-public selector bottleneck.
- Decision: keep strict submission gate closed. If a public slot is spent on mixmin/direns, label it as a high-risk score-oriented probe that explicitly tests whether actual-anchor/combo stress is more trustworthy than the pairwise/old selector pair. Do not merge it with the conservative S4/Q3 selector-disambiguation lane.

## E26. Public LB Inverse Feasibility

- Observe: E21-E25 repeatedly say selector worldviews disagree, but we still need to know whether known public LB observations themselves are strong enough to identify candidate signs if modeled directly.
- Wonder: do the eight known public LB anchors constrain target prior, public subset, or candidate deltas enough to rank `1bbfb735`, mixmin/direns, target-ablation, and inverse7 probes?
- Hypothesis: if public LB observations are sufficiently informative, then feasible hidden-label/public-subset worlds compatible with the known scores should give one-sided candidate delta ranges for important probes.
- Method: `analysis_outputs/public_lb_inverse_feasibility.py` formulated two LP inverse models:
  - all-test soft-label model: fixed 250 test rows x 7 targets, unknown fractional labels `q in [0,1]`, equal cell weight.
  - cell-mixture model: arbitrary public cell/label mass over positive and negative outcomes, representing an unknown pseudo-public subset/weighting.
  - It also repeated candidate-delta ranges with train target prevalence constrained to `±0.05`, `±0.10`, and `±0.20`.
- Result:
  - known public observations used: `8`.
  - all-test soft-label minimum total slack: `0`; max absolute residual `~1e-15`.
  - cell-mixture minimum total slack: `0`; max absolute residual `~1e-16`.
  - all-test target prior ranges are almost fully open: Q1/Q3/S2/S3/S4 can range `0` to `1`; Q2 is `0.0337` to `0.9253`; S1 is `0.00057` to `1`.
  - cell-mixture subject mass range is `0` to `1` for every subject.
  - all checked unobserved candidates cross zero under all-test soft-label ranges: `1bbfb735`, `6b9335b1`, 0.65 sensor, `mixmin_0c916`, `direns_c4af`, `targetabl_b19056bb`, `targetabl_1049b8e7`, `inverse7blend_1040`.
  - train-prior bands do not fix sign: with `±0.05`, `±0.10`, and `±0.20`, cross-zero count remains `8/9`; only raw05 is one-sided because it is itself a known public observation.
- Interpretation: public LB anchors are mathematically underidentified. Even after assuming all test rows are public and constraining target prevalence close to train, the known LBs cannot decide the sign of current important candidates. Public LB can calibrate a declared selector worldview, but cannot by itself select among the competing worlds.
- Decision: stop treating public-LB inverse fitting as a direct optimizer. A new submission should be framed as choosing a worldview to test: conservative pair-only S4/Q3 diagnostic, or high-risk actual-anchor/combo score probe. The missing object is not another inverse LP; it is an external anchor or structural assumption strong enough to collapse these feasible worlds.

## E27. Public LB Structural Prior Stress

- Observe: E26 proved that unconstrained/public-prior-banded inverse worlds are underidentified. The next cheapest question is whether a plausible hidden subject prior collapses candidate signs.
- Wonder: is the remaining ambiguity merely because E26 ignored subject/user identity, or does sign ambiguity survive even after using train-derived subject-target priors?
- Hypothesis: if train target prevalence plus subject identity is the missing structural assumption, then all-test soft-label worlds matching the known public LBs and constrained by global/subject-target priors should make at least one important unobserved candidate one-sided negative versus a2c8.
- Method: `analysis_outputs/public_lb_structural_prior_stress.py` reused the E26 all-test soft-label LP and added seven scenarios: no prior, global target prevalence `±0.05`, and global prevalence plus subject-target priors with bands `±0.20`, `±0.15`, and `±0.10`. It then recomputed candidate delta ranges for `1bbfb735`, 0.65 sensor, `6b9335b1`, mixmin/direns, target-ablation probes, inverse7, and raw05.
- Result:
  - scenarios tested: `7`.
  - all scenarios fit the 8 known public LB anchors with minimum slack `0`.
  - all unobserved candidate-scenario cells crossed zero: `56/56`.
  - one-sided improvement cells: `0`.
  - raw05 was one-sided positive in all 7 scenarios, as expected from its known worse public LB.
  - even the tight `global_t010_subject_t010` scenario left `1bbfb735` at `[-0.003706960, +0.002332888]`, 0.65 sensor at `[-0.002441019, +0.001484882]`, and mixmin at `[-0.010891932, +0.009106607]`.
- Interpretation: weak/moderate subject identity priors are not enough to collapse the public-LB feasible worlds. This directly weakens the hypothesis that the plateau is caused by simply missing subject priors in the inverse selector.
- Decision: do not submit or rank current candidates from a subject-prior inverse worldview. The next useful structural assumption must be stronger and externally justified: exact public subset/binary-label constraints, a new public sensor, or a learned latent gate that predicts selector-world assignment from non-LB evidence.

## E28. Binary Hidden-Label Inverse Stress

- Observe: E26-E27 used relaxed soft labels. A fair objection is that public labels are binary, so the relaxation may be creating fake ambiguity.
- Wonder: if all 250 test rows x 7 targets are forced to binary labels, do known public LB anchors become precise enough to rank current candidates?
- Hypothesis: if relaxed-label ambiguity is the main issue, then a binary all-test inverse model should fit known public LBs within frontier resolution and produce one-sided candidate deltas for representative files.
- Method: `analysis_outputs/public_lb_binary_inverse_stress.py` solved MILPs with 1750 binary label variables plus 8 slack variables. Scenarios were `binary_no_prior`, `binary_global_t005`, and `binary_global_t010_subject_t010`. Candidate range MILPs were attempted for representative pair sensors, mixmin, inverse7, and raw05 under residual budgets from the fit incumbents.
- Result:
  - all fit MILPs hit the time limit, so this is an incumbent stress, not a proven optimum.
  - `binary_no_prior`: sum abs residual `0.000526704`, max residual `0.000145053`, which is `1.67x` the raw05-a2c8 public gap.
  - `binary_global_t005`: max residual `0.000202364`, worse than no-prior at the max-residual scale.
  - `binary_global_t010_subject_t010`: sum abs residual `0.000149950`, max residual `0.000061242`, which is `0.704x` the raw05-a2c8 gap. So a tight subject-prior binary all-test world can fit known anchors at frontier-scale precision as an incumbent.
  - candidate range optimization was much harder. Under `binary_no_prior`, `6b9335b1` had both signs feasible from incumbents: `[-0.004415762, +0.002817743]`. `1bbfb735` and the 0.65 sensor only produced max-side positive incumbents within the short range time limit. Tight subject-prior range MILPs produced no candidate incumbents within 4 seconds.
  - one-sided improvement evidence: `0`.
- Interpretation: binary labels do not simply erase the underidentification. They can make a plausible all-test public world fit anchors more realistically, but the resulting inverse problem is computationally brittle and still does not produce a submission-rankable sign for current candidates. The best reading is "binary exactness is a possible constraint family, but not yet an operational selector."
- Decision: do not promote any candidate from E28. The next version, if pursued, should not be another blind MILP range sweep; it should add a structured candidate-specific search, save incumbent binary worlds, or use a public sensor/new latent gate to decide which binary world is plausible.

## E29. Binary World Pool Candidate Sign Audit

- Observe: E28 found one tight binary subject-prior incumbent that fits known anchors within the raw05-a2c8 public gap, but a single binary world is not enough to choose a candidate.
- Wonder: if we sample multiple binary hidden-label worlds under the tight subject-prior constraint, do candidate signs become stable?
- Hypothesis: if binary exactness is the missing public-world model, frontier-scale binary incumbents should agree on which candidate family improves: pair-only S4/Q3 sensors, mixmin, or inverse7.
- Method: `analysis_outputs/public_lb_binary_world_pool.py` solved 15 MILP objectives under `global_band=0.10` and `subject_target_band=0.10`: slack fit, min/max objectives for pair sensors, mixmin, inverse7, and four random world objectives. Each incumbent was evaluated for known-LB residual, target priors, and candidate deltas.
- Result:
  - objectives attempted: `15`.
  - incumbents found: `15`.
  - unique binary worlds: `15`.
  - frontier-scale worlds by max residual <= raw05-a2c8 gap: `1`.
  - across all worlds, better rates were mixmin `0.8667`, inverse7 `0.7333`, 0.65 sensor `0.3333`, `1bbfb735` `0.2667`, `6b9335b1` `0.2667`.
  - the only frontier-scale world was `random_world_3` with max residual `0.000084491`, just inside the raw05-a2c8 gap. In that world, mixmin delta was `-0.00107366`, inverse7 delta `-0.000277011`, while 0.65 sensor, `1bbfb735`, and `6b9335b1` were positive (`+0.000313073`, `+0.000530105`, `+0.000615230`).
- Interpretation: binary-world sampling does not validate a submission because only one frontier-scale world was found and all solves are time-limited incumbents. But it gives a useful directional clue: the plausible binary world sampled here supports the high-risk score-probe lane more than the pair-only S4/Q3 sensor lane.
- Decision: do not submit from E29. Promote the next binary-world work, if any, to frontier-pool expansion with more slack-dominant random objectives and stricter residual filters. In candidate triage, E29 slightly strengthens `submission_mixmin_0c916bb4.csv` as a high-risk worldview probe, not as a strict survival candidate.

## E30. Binary Frontier-Box Pool

- Observe: E29's main weakness was that only one sampled world was frontier-scale. That might mean binary exactness is unusable, or it might mean the objective did not force the solver into the frontier residual box.
- Wonder: if every known-public residual slack is constrained to be no larger than the raw05-a2c8 public gap, do exact-label worlds still exist, and do they agree on candidate signs?
- Hypothesis: if the binary exact-label public world is a useful selector, a frontier-box-constrained pool should produce multiple diverse worlds and stable one-sided candidate improvement for the correct family.
- Method: `analysis_outputs/public_lb_binary_frontier_box_pool.py` reused the tight `global_band=0.10`, `subject_target_band=0.10` binary MILP, but changed slack bounds so every known-public LB residual must be `<= 0.000086986`. It solved 29 objectives: slack fit, candidate min/max for pair sensors/mixmin/inverse7, and 18 random row/subject/target textured objectives.
- Result:
  - objectives attempted: `29`.
  - incumbent worlds: `29`.
  - unique worlds: `28`.
  - frontier-scale worlds: `29` by construction and verification.
  - all-world better rates: mixmin `0.931034`, inverse7 `0.896552`, 0.65 sensor `0.413793`, `1bbfb735` `0.413793`, `6b9335b1` `0.379310`.
  - random-plus-fit worlds, excluding candidate min/max objectives, favored mixmin `19/19` and inverse7 `18/19`, while pair sensors were only `7-8/19`.
  - no candidate was certified one-sided: candidate-max objectives still produced positive deltas for mixmin (`+0.008774`) and inverse7 (`+0.002782`).
- Interpretation: frontier-scale binary worlds are not rare; E29's one-world result was partly an objective-design artifact. Within non-candidate-objective frontier worlds, the high-risk score-probe lane dominates pair-only S4/Q3. But the existence of frontier-scale adverse candidate-objective worlds means exact-label constraints still do not prove public improvement.
- Decision: strict submit gate remains closed. E30 materially raises `submission_mixmin_0c916bb4.csv` above pair-only S4/Q3 as the more coherent binary-world public probe, but only if the next public slot is deliberately used to test the binary/actual-anchor worldview against the pairwise/old veto. It is not a 0.54-certifying candidate.

## E31. Binary World Plausibility Geometry Audit

- Observe: E30 found frontier-box binary worlds that strongly support mixmin/inverse7 under random+fit objectives, but adverse candidate-max worlds still exist.
- Wonder: are those adverse worlds structurally implausible under train label dynamics, so a LeJEPA-style geometry gate can safely downweight them?
- Hypothesis: if adverse mixmin/inverse7 worlds are artifacts of adversarial objectives, then train-only label geometry should assign them high plausibility energy compared with random/fit worlds.
- Method: `analysis_outputs/public_lb_binary_world_plausibility_audit.py` scored each E30 world without using test labels. Features were target prior MAE, subject-target MAE, pairwise joint MAE, target-correlation MAE, row-cardinality L1, global/subject temporal flip-rate MAE, run-length MAE, and train/test edge flip rate. Lower `plausibility_energy` means closer to train label geometry.
- Result:
  - worlds scored: `29`.
  - mixmin adverse worlds: `2`.
  - inverse7 adverse worlds: `3`.
  - random+fit worlds: mixmin better_rate `1.000000`, inverse7 `0.947368`, pair sensors `0.368421-0.421053`.
  - low-energy random+fit worlds: mixmin `6/6`, inverse7 `6/6`.
  - but the two mixmin-adverse worlds are the two most plausible worlds by this train-geometry score: ranks `1` and `2`, with mixmin deltas `+0.004332` and `+0.008774`.
- Interpretation: train label geometry cannot discard the adverse binary worlds. This is the strongest reason not to promote mixmin from high-risk probe to strict submission: the worlds where mixmin fails are not obviously unrealistic under priors, co-occurrence, cardinality, or temporal dynamics.
- Decision: keep mixmin as the leading information-rich public probe under the binary/actual-anchor worldview, but do not call it a validated improvement. The missing constraint must come from a public observation, an independent anchor, or a more specific hidden-public subset model; generic train-label plausibility is insufficient.

## E32. Binary Anchor Loss Geometry Audit

- Observe: E31 left mixmin/inverse7 stuck: adverse frontier-box binary worlds looked plausible under generic train-label geometry. But those worlds may still be implausible in a different sense: they might explain the already-known public LB anchors only through large target-level cancellation or movement/loss misalignment.
- Wonder: do known-public anchor loss decompositions reject the E30 adverse mixmin/inverse7 worlds even when generic train-label geometry does not?
- Hypothesis: if the random/fit frontier-box binary worlds are closer to the actual public sensor than candidate-adverse worlds, then known public-worse anchors should have per-target loss deltas aligned with their moved target axes, with less cancellation. Adverse mixmin worlds should require higher `anchor_energy`.
- Method: `analysis_outputs/public_lb_binary_anchor_loss_geometry.py` scored all 29 E30 binary worlds. For every known public anchor, it computed per-target logloss deltas versus A2C8, measured whether moved target axes explain the public worsening, and penalized target-level cancellation. Lower `anchor_energy` means less cancellation and better movement/loss alignment.
- Result:
  - worlds scored: `29`.
  - mixmin adverse worlds: `2`.
  - all-world better rates: mixmin `0.931034`, inverse7 `0.896552`, pair sensors `0.379310-0.413793`.
  - `low_anchor_energy_half`: mixmin `15/15`, inverse7 `15/15`; pair sensors only `0.333333-0.400000`.
  - `low_anchor_energy_quarter`: mixmin `7/7`, inverse7 `7/7`.
  - `low_anchor_energy_random_plus_fit`: mixmin `12/12`, inverse7 `12/12`.
  - the two adverse mixmin worlds are high-anchor-energy, not low-energy: `mixmin_0c916_max` has rank `26`, delta `+0.008774`; `inverse7blend_1040_max` has rank `28`, mixmin delta `+0.004332`, inverse7 delta `+0.002782`.
- Interpretation: this is the first stress after E31 that actually downweights the adverse binary worlds. Generic train-label dynamics could not reject them, but known-anchor loss geometry says they explain public observations in a more strained way. This strengthens mixmin/inverse7 as the leading binary/actual-anchor worldview probe.
- Decision: still no strict improvement claim. `anchor_energy` uses known public anchor decompositions, so it is a diagnostic gate, not a leaderboard optimizer. But if one high-risk public probe is chosen, E32 moves `analysis_outputs/submission_mixmin_0c916bb4.csv` ahead of pair-only S4/Q3 sensors and ahead of inverse7 as the clearest information-rich test.

## E33. Binary Anchor Loss LOO Stability Audit

- Observe: E32 is promising but uses the known public anchors directly. It could be driven by one anomalous anchor such as raw05, final9, or a bad JEPA file.
- Wonder: if one known public anchor is removed, does the anchor-loss gate still reject mixmin-adverse worlds and favor mixmin/inverse7?
- Hypothesis: if E32 captures a stable public-anchor geometry rather than one-anchor overfit, then leave-one-anchor-out `anchor_energy` should preserve mixmin support in low-energy bands and keep adverse mixmin worlds out of the low-energy half.
- Method: `analysis_outputs/public_lb_binary_anchor_loss_loo_stability.py` recomputed `anchor_energy` seven times, omitting one non-A2C8 known public anchor each time. It rescored the 29 E30 frontier-box worlds and summarized low-energy half, low-energy quarter, and low-energy random+fit bands.
- Result:
  - leave-one-anchor runs: `7`.
  - mixmin low-energy-half better_rate min/median/max: `1.000000 / 1.000000 / 1.000000`; worst max delta `-0.000315338`.
  - mixmin low-energy-quarter better_rate min/median/max: `1.000000 / 1.000000 / 1.000000`; worst max delta `-0.000537096`.
  - inverse7 low-energy-half better_rate min/median/max: `0.928571 / 1.000000 / 1.000000`; worst max delta `+0.000060149`.
  - no mixmin-adverse world entered any LOO low-energy-half band; adverse rank ranges stayed high, with worst minimum rank `21/29`.
  - pair sensors remained weak: low-energy-half better_rate max was `0.428571` for `1bb` and `0.357143` for `6b`.
- Interpretation: E32 is not just one-anchor overfit. Anchor-loss geometry remains one-sided for mixmin under LOO, while inverse7 is slightly less stable and pair-only S4/Q3 sensors remain unsupported.
- Decision: update the high-risk probe priority: `submission_mixmin_0c916bb4.csv` is now the best information-rich public sensor under the binary/actual-anchor/anchor-loss worldview. The strict improvement gate remains closed because the stress is still anchor-derived, not a new independent public observation.

## E34. Binary Anchor Loss Family/Null Audit

- Observe: E32/E33 made mixmin the leading high-risk public sensor, but the gate may still be an artifact of one anchor family or an overinterpreted target-axis alignment story.
- Wonder: does the anchor-loss gate survive raw05/medium/bad-JEPA family holdouts, and does it actually rely on moved-target axis semantics?
- Hypothesis: if the gate is a robust public-anchor geometry, it should survive removal of raw05 and bad-JEPA anchors. If it is genuinely target-axis semantic, permuting moved-target weights should weaken the signal.
- Method: `analysis_outputs/public_lb_binary_anchor_loss_family_null_audit.py` recomputed E32-style energy under family scenarios: `no_raw05`, `no_medium_non_jepa`, `no_bad_jepa`, `only_medium_non_jepa`, `only_bad_jepa`, `raw05_plus_medium`, and `raw05_plus_bad_jepa`. It also ablated energy components and ran 500 target-axis permutations of anchor movement weights.
- Result:
  - mixmin survives main family holdouts: `no_raw05`, `no_medium_non_jepa`, and `no_bad_jepa` all keep low-half better_rate `1.0`.
  - `only_medium_non_jepa` is sufficient: mixmin low-half better_rate `1.0`, max delta `-0.000537096`, adverse in band `0`.
  - `only_bad_jepa` fails: mixmin low-half better_rate drops to `0.857143`, max delta `+0.008774`, and both adverse worlds enter the low-energy half.
  - component ablations still keep mixmin low-half support at `1.0`.
  - target-axis permutation null also keeps mixmin one-sided in `500/500` low-half and low-quarter permutations; median low-half max delta remains `-0.000315338`.
- Interpretation: E32/E33 are not raw05-only or bad-JEPA-only artifacts. The useful anchor signal is mostly carried by medium non-JEPA anchors plus broad loss/cancellation geometry. However, the target-axis semantic interpretation is weakened: permuting target movement weights does not break the signal.
- Decision: keep `submission_mixmin_0c916bb4.csv` as the leading high-risk public sensor, but describe the evidence as anchor-loss/cancellation geometry rather than JEPA-style target-axis alignment. This still does not certify a normal improvement submission.

## E35. Public Probe Independent Evidence Audit

- Observe: E32-E34 made `analysis_outputs/submission_mixmin_0c916bb4.csv` the leading high-risk binary/actual-anchor/anchor-loss probe, but all strongest evidence is still entangled with known public anchors. The unresolved question is whether any existing non-public, out-of-anchor source is strong enough to promote mixmin to a normal improvement submission.
- Wonder: does mixmin have certification-grade independent evidence, or is it only the most information-rich public sensor for a specific worldview?
- Hypothesis: if mixmin is a normal submit candidate, at least one local/representation source should support it, the pairwise/old selector veto should not be hard, and anchor-loss geometry should be corroborative rather than the primary evidence.
- Method: `analysis_outputs/public_probe_independent_evidence_audit.py` joined direction-probe metadata, focused label-flow pairwise scores, focused survival review, scale-curve scores, actual-anchor/combo summaries, E32 anchor-loss bands, E33 LOO summary, and E34 family/null summary. It tagged evidence tiers as local-independent-ish, local/representation, quasi-public, known-public-derived, anchor-derived, or anchor-derived robustness.
- Result:
  - candidates audited: `5`.
  - normal submit gates passing: `0`.
  - mixmin local direction support: yes, honest CV mean/worst `-0.000951963` / `-0.000695966`.
  - mixmin selector hard veto: yes, pair p90 `+0.000879200`, old p90 `+0.001041933`.
  - mixmin anchor-loss support: yes, low-half better_rate `1.0`, low-half max_delta `-0.000537096`.
  - mixmin LOO support: yes, LOO low-half min better_rate `1.0`, worst max_delta `-0.000315338`.
  - pair-only S4/Q3 sensors have local dependency/pairwise support but fail old/independent survival and are weak under binary/anchor-loss geometry.
- Interpretation: H34 is rejected as a normal-submit claim. Mixmin is not independently certified; its strongest evidence remains known-public/anchor-derived. However, E35 also confirms it is the highest-information public sensor if the next experiment is to test whether anchor-loss/binary-world geometry beats the selector veto.
- Decision: strict submit candidate count remains `0`. If a public diagnostic slot is deliberately spent, `analysis_outputs/submission_mixmin_0c916bb4.csv` is now more information-rich than another S4/Q3 pair-only variant for testing the binary/actual-anchor/anchor-loss worldview. `1bbfb735` remains a lower-risk selector-disambiguation sensor, not the top information sensor after E35.

## E36. Raw-Structure Pseudo-Label Candidate Stress

- Observe: E35 could not find certification-grade out-of-anchor support for mixmin. The next independent-ish check should use observed data structure rather than public-anchor decomposition: same-subject temporal neighbors, raw-feature KNN, coverage/missingness KNN, behavior KNN, and raw-feature clusters derived from `analysis_outputs/all_keys_deep_features.parquet`.
- Wonder: do raw subject/date/feature neighborhoods support the candidate movement, and does that support agree with the anchor-loss worldview?
- Hypothesis: if raw observed structure independently supports mixmin, mixmin should improve soft LogLoss versus A2C8 across train-derived pseudo-label sources without using public LB or known public-anchor losses.
- Method: `analysis_outputs/raw_structure_pseudolabel_candidate_stress.py` built 10 pseudo-label sources: subject mean, same-subject temporal KNN k3/k7, all-sensor KNN k5/k15, cross-subject KNN k15, count/coverage KNN, sensor-stat KNN, and KMeans raw-feature cluster priors k12/k24. It scored mixmin, inverse7, and pair-only S4/Q3 sensors against A2C8 by soft LogLoss delta, movement alignment, and row movement anatomy. It also measured train/test adversarial AUC from raw sensor features.
- Result:
  - pseudo-label sources: `10`.
  - raw sensor train/test adversarial AUC: `0.607876`.
  - raw-structure gates passing after selector-veto check: `0`.
  - `inverse7blend_1040`: support `10/10`, mean delta `-0.000705727`, worst delta `-0.000507826`, mean toward-rate `0.606601`.
  - `mixmin_0c916`: support `5/10`, mean delta `+0.000065107`, worst delta `+0.000498574`, mean toward-rate `0.526255`.
  - pair sensors: support `7/10`, mean deltas around `-0.00012` to `-0.00014`, but positive worst deltas and selector hard veto remain.
- Interpretation: E36 does not independently support mixmin; it strengthens the reading that mixmin is mainly an anchor-loss/binary-world public sensor. The surprising new signal is inverse7: it is the only candidate supported by every raw-structure pseudo-label source. That makes inverse7 a possible bridge between observed raw structure and anchor-loss geometry, but E35 still flags selector hard veto and E33 shows inverse7 anchor-LOO is weaker than mixmin.
- Decision: strict submit candidate count remains `0`. Next useful local experiment is no longer "certify mixmin"; it is "can inverse7 or a mixmin/inverse7 blend reduce selector veto while preserving raw-structure and anchor-loss support?"

## E37. Inverse7 Raw-Anchor Bridge Scale Scan

- Observe: E36 split the probe family. Mixmin is strongest as anchor-loss/binary-world public sensor; inverse7 is strongest under train-derived raw observed structure. The cheap next test is whether scaling or blending these directions can reconcile that split.
- Wonder: can a scaled inverse7 or inverse7/mixmin blend preserve raw-structure support and anchor-loss support while reducing the pairwise/old selector veto?
- Hypothesis: if inverse7 is a true bridge direction, at least one scale/blend variant should keep E36 raw pseudo-label support, keep E32 low-anchor-energy binary-world support, and weaken the E35 selector veto enough to create two-selector majority or a strict bridge gate.
- Method: `analysis_outputs/inverse7_raw_anchor_bridge_scale_scan.py` generated 22 logit-space variants from A2C8 toward inverse7, mixmin, and inverse7/mixmin blended directions. It scored each variant with the same 10 E36 raw-structure pseudo-label sources, E32 binary anchor-loss bands, the old hidden-subset selector, and the pairwise public-order selector.
- Result:
  - variants scanned: `22`.
  - raw support gates: `14`.
  - anchor low-half+quarter gates: `22`.
  - two-selector majority variants: `0`.
  - strict bridge gates: `0`.
  - best-ranked diagnostic: `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv`, support_rate `1.0`, raw mean delta `-0.000181991`, low-anchor-half better_rate `1.0`, pair p90 `+0.000035423`, old p90 `+0.000587512`, selector hard veto `True`.
- Interpretation: scaling inverse7 preserves raw and anchor support, but it does not fix selector conflict. Adding mixmin weight improves anchor-band margins but worsens selector p90/bad-axis and eventually weakens raw support. The bridge failure is not amplitude-only.
- Decision: strict submit candidate count remains `0`. E37 rejects the easy bridge strategy. The next useful question is either a new selector/worldview calibration public sensor, or a non-public gate that explains why raw+anchor-supported inverse7 still has near-zero pairwise support and old beat rates around `0.004-0.008`.

## E38. Worldview Sensor Discriminability Audit

- Observe: E37 showed raw and anchor support can coexist while selector veto remains. The next useful decision is not which candidate is "safe", but which candidate best separates the hidden-public worldviews if a diagnostic public slot is spent.
- Wonder: among anchor-loss binary worlds, raw observed structure, pairwise public-order selector, old hidden-subset selector, and local honest-CV/combo evidence, which candidate has the clearest predeclared interpretation if public LB improves or worsens?
- Hypothesis: if no normal submit candidate exists, the next public slot should be allocated to the candidate with the highest worldview discriminability: large sign conflict, clear lane identity, and no claim of safety.
- Method: `analysis_outputs/worldview_sensor_discriminability_audit.py` joined E32/E33 anchor-loss bands, E35 independent-evidence audit, E36 raw-structure pseudo-label stress, and E37 bridge scale scan. It converted each source into raw/anchor/pair/old/honest-CV verdicts, then ranked candidates by sign entropy and conflict span relative to the raw05/A2C8 public gap.
- Result:
  - candidates audited: `10`.
  - normal submit candidates: `0`.
  - public sensor candidates: `10`.
  - top information sensor: `analysis_outputs/submission_mixmin_0c916bb4.csv`, sensor information score `3.355110`.
  - next lanes: `analysis_outputs/submission_inverse7blend_1040423d.csv` / full inverse7 as raw+anchor bridge sensors, and `analysis_outputs/submission_label_flow_focused_6b9335b1.csv` / `1bbfb735` as S4/Q3 pair-vs-anchor selector sensors.
- Interpretation: E38 formalizes the current state as sensor selection, not improvement selection. Mixmin is the highest-information anchor-loss worldview sensor because it sets anchor/honest-CV support against raw/pair/old veto. Inverse7 is the raw+anchor-vs-selector bridge sensor. Pair-only S4/Q3 files are selector-disambiguation sensors, but no lane crosses the normal-submit gate.
- Decision: strict submit candidate count remains `0`. If a public diagnostic is intentionally used, `mixmin_0c916` is the maximum-information sensor; `inv7_s0p25` is the cleaner raw+anchor bridge sensor; `1bbfb735` is the lower-risk S4/Q3 selector sensor. None should be described as safe or as a 0.54 path.

## E39. OOF Selector Calibration Audit

- Observe: E38 ranked public sensors but could not certify any candidate. The next cheap independent check is whether the train OOF archive can act as a selector/worldview calibration target without using unknown public labels.
- Wonder: do label-free OOF stresses over future-tail rows, train/test-domain-like rows, raw density, missingness, subject blocks, date blocks, and random blocks select candidates whose signs and known-public ordering agree with public LB?
- Hypothesis: if selector identity can be calibrated locally, OOF improvements should be stable across label-free pseudo-public subsets, and known public OOF analogues should preserve both sign and rank relative to the final9 baseline.
- Method: `analysis_outputs/oof_selector_calibration_audit.py` scored `4172` OOF rows (`4171` unique prediction hashes) versus `final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy`. It built label-free subsets from raw features, subject/date order, missingness, density, and train/test domain score. Known public scores were used only for the sanity table.
- Result:
  - train/test domain AUC from raw features was `1.000000`, so the feature archive contains strong split/domain signal.
  - strict OOF selector gates: `1311`; conservative OOF gates: `1115`.
  - known-public nonbaseline sign match rate: `1.000000`.
  - known-public nonbaseline pairwise rank agreement: `0.000000`.
  - Stage2 is public-better than ordinal (`0.5779449757` vs `0.5783033652`), but OOF ranks ordinal much better than stage2 (`full_delta -0.016400` vs `-0.010773`; stress p90 `-0.010581` vs `-0.005761`).
  - Top OOF-stable files are `publicblend` OOF variants with very large local improvements, which reinforces the danger of treating local OOF stability as public transfer.
- Interpretation: E39 separates sign from selector ranking. OOF stress can reject unstable candidates and expose local overfit, but it cannot choose the public worldview because it reverses the known-public order among stage2 and ordinal despite matching both signs versus final9.
- Decision: strict submit candidate count remains `0`. Do not use OOF selector gates as a normal submission ranker. Keep them only as a negative calibration/overfit screen and as evidence that validation mismatch remains a primary bottleneck.

## E40. Test-Movement Fingerprint Selector

- Observe: E39 rejected OOF as a public-rank selector. A different non-OOF selector target is the test prediction movement fingerprint itself: where each candidate moves A2C8 by target, subject, row-order, raw-domain score, density, missingness, and raw-feature cluster.
- Wonder: can label-free movement anatomy recover known public LB ordering under leave-one-anchor-out, especially the stage2 < ordinal order that OOF got wrong?
- Hypothesis: if hidden public subset identity is encoded in test movement/raw-domain structure, a kNN selector over movement fingerprints should recover known-anchor order, pass permutation-null rank stress, and then provide a cautious prior for current public sensors.
- Method: `analysis_outputs/test_movement_fingerprint_selector.py` built probability/logit/entropy movement fingerprints relative to A2C8. Views were target-only, subject, row-order, raw-domain, and combined. Raw-domain masks used train/test domain score, train-NN density, missingness, and raw-feature clusters. Known public LB was used only for leave-one-anchor-out evaluation.
- Result:
  - train/test domain AUC from raw features: `1.000000`.
  - strict selector views: `0`.
  - loose selector views: `4` (`combined`, `order`, `target`, `raw_domain`).
  - combined LOOCV MAE: `0.000781461`; pairwise rank accuracy: `0.821429`; permutation-null rank p-value: `0.004`.
  - stage2/ordinal order is correctly recovered by every view, unlike E39 OOF.
  - strict gate fails because A2C8 is not predicted best under leave-one-out and bad JEPA anchor severity is strongly underpredicted (`q2_jepa_bad` predicted around `+0.00022` vs actual `+0.00236`; all-target JEPA residual predicted around `+0.00127` vs actual `+0.00379`).
  - Combined-view candidate prior: `inv7_s0p25` predicted `0.577450`, raw timeline `0.577526`, `1bb_s0p65` `0.577522`, full `1bb` `0.577560`, mixmin `0.577664`.
- Interpretation: E40 is better than OOF at the fine stage2/ordinal ordering, but still fails as a certified selector because it compresses known bad JEPA failures and cannot prove A2C8 as best in leave-one-out. It gives a useful local prior: conservative inverse7/raw-bridge movement is most public-like by test movement anatomy, while mixmin is less raw05-like.
- Decision: strict submit candidate count remains `0`. Do not use E40 to claim an improvement submission. Use it as a loose sensor-prior that strengthens `inv7_s0p25` as the conservative raw+anchor bridge diagnostic if the explicit public question is low-risk movement anatomy, while E38 still makes mixmin the maximum-information worldview sensor.

## E41. Movement + Bad-Axis Geometry Selector

- Observe: E40's specific failure was not only general selector noise. It recovered stage2/ordinal but compressed known bad JEPA failures, so the natural next falsification is to add bad-axis direction geometry directly.
- Wonder: does logit-space cosine/projection against raw, medium, and bad public-anchor movement directions repair the missing severity signal without turning into an in-sample anchor lookup?
- Hypothesis: if E40 was missing only bad-axis geometry, a LOO-safe movement+axis selector should reduce bad-anchor underprediction, preserve stage2 < ordinal, and either pass loose/strict gates or at least explain which candidate lane is safest.
- Method: `analysis_outputs/movement_badaxis_geometry_selector.py` built compact movement features and axis features versus A2C8. Axis features use group and named cosine/projection against raw_timeline, stage2, ordinal, final9, q2_jepa_bad, lejepa_bad, and jepa_residual_bad. During leave-one-anchor-out, the left-out anchor's own axis is removed before features are recomputed.
- Result:
  - strict selector views: `0`.
  - loose selector views: `0`.
  - best severity view `axis_group`: LOOCV MAE `0.000854918`, pairwise rank accuracy `0.785714`, permutation-null rank p `0.014`, stage2/ordinal order correct, bad-anchor mean underprediction `0.000898399`.
  - `axis_group` still fails because MAE is just above the loose threshold and A2C8 is predicted much worse in LOO (`+0.001475508` delta).
  - `axis_named` gets lower MAE `0.000827696` but fails rank (`0.571429`), stage2/ordinal order, and bad-anchor underprediction (`0.001412567`).
  - In-sample candidate priors from ungated axis views rank some S4/Q3 pair sensors near raw05, but this is not actionable because all views fail gates.
- Interpretation: E41 partially validates the diagnosis that E40 missed bad-axis severity: group bad-axis geometry reduces bad-anchor underprediction from E40-scale collapse to below `0.001`. But it also shows that severity geometry alone does not identify the public selector. A2C8-as-best is still not recoverable under LOO, and named axes overfit anchor identity while degrading rank.
- Decision: strict submit candidate count remains `0`. Do not use movement+bad-axis predicted LB values as forecasts. The next local work should not be another axis/cosine feature tweak; it should either introduce an independent out-of-anchor selector target, model A2C8/current-best as an explicit known anchor without pretending it is LOO certification, or spend a predeclared public sensor.

## E42. Fixed-Zero Anchor Selector Calibration

- Observe: E41's largest strict failure was A2C8 LOO. Since A2C8 is already a known current-best public anchor, the next falsification is whether treating it as a fixed zero anchor repairs selector calibration without pretending that full LOO is the only valid stress.
- Wonder: if A2C8 is fixed in every fold, does the movement+axis selector become usable, or does the fixed zero simply create a near-zero prior whose candidate advantages are below selector resolution?
- Hypothesis: if A2C8 should be modeled as a known fixed zero anchor, nonbaseline leave-one-out should preserve known public ordering and still have enough resolution to separate unobserved candidates beyond the raw05-A2C8 public gap.
- Method: `analysis_outputs/zero_anchor_selector_calibration.py` kept A2C8 fixed with delta `0` in every nonbaseline LOO fold, removed the held-out anchor's own axis for axis views, scored `compact`, `axis_group`, `axis_named`, and combined views, then stress-tested synthetic A2C8-to-anchor trajectories at scales `0.05` through `1.00`. The frontier-resolution gate compared selector MAE with the raw05-A2C8 gap `0.0000869862`.
- Result:
  - fixed-zero nonbaseline gates: `0`.
  - usable zero-anchor gates: `0`.
  - best view `axis_group`: nonbaseline MAE `0.000766262`, rank accuracy `0.857143`, Spearman `0.821429`, stage2/ordinal order correct, raw05 predicted best among nonbaseline anchors, null rank p `0.006`.
  - `axis_group` still fails because raw05 gap to MAE ratio is only `0.113520`, best unobserved advantage-to-MAE ratio is only `0.065408`, trajectory monotonic rate is `0.428571`, and zero-neighborhood collapse warning is true.
  - ungated `axis_group` predicts three pair sensors slightly better than raw05 (`1bb_s0p65`, `1bb`, `6b`), but their forecast edge over raw05 is only `0.000037-0.000050` while selector MAE is `0.000766`.
- Interpretation: A2C8 LOO was harsh, but it was not the main blocker. Fixing A2C8 improves nonbaseline rank and bad/good separation, yet it collapses frontier-scale resolution. The selector can distinguish very bad movement from medium/good movement, but it cannot certify tiny near-A2C8 improvements.
- Decision: strict submit candidate count remains `0`. Do not submit fixed-zero `axis_group` ranked pair sensors as improvement candidates. The next local work should stop trying to repair movement+axis kNN and instead target a selector whose error is below the raw05-A2C8 edge, or use a predeclared public sensor to identify the hidden public worldview.

## E43. Selector Resolution Boundary Audit

- Observe: E42 converted the problem from "A2C8 LOO is too harsh" to "near-frontier candidate edges are below selector error." The next falsification is to measure that boundary across all current selector families.
- Wonder: is the 0.577439 plateau mainly because the candidate universe lacks any good candidate, or because current selectors cannot read improvements at the `raw05-A2C8` scale?
- Hypothesis: if a local selector can justify a normal near-frontier submission, its known-anchor error must be below the raw05-A2C8 public gap and at least one unobserved candidate's predicted edge must exceed that error margin.
- Method: `analysis_outputs/selector_resolution_boundary_audit.py` collected pairwise public-order selector reliability, old hidden-subset reliability, E40 movement fingerprints, E41 movement+axis geometry, and E42 fixed-zero axis calibration. It used raw05-A2C8 gap `0.0000869862` as the resolution target and checked candidate rows by `predicted_delta + selector_error < 0` for A2C8 improvement and `< raw05_gap` for raw05 improvement.
- Result:
  - selector frontier-resolution gates: `0`.
  - candidates certified better than A2C8 by error margin: `0`.
  - candidates certified better than raw05 by error margin: `0`.
  - best selector by error: pairwise public-order models, best LOO error `0.000218288`, raw05-gap/error ratio `0.398493`, best L2O error `0.000415499`, raw05-gap/L2O ratio `0.209353`.
  - E40/E41/E42 best error ratios are only `0.111312`, `0.105094`, and `0.113520` respectively.
  - top pairwise-p90 candidate edges are hiddenloc rows around `1e-6`, only `0.005-0.007` of the best selector error.
- Interpretation: this is the sharpest plateau diagnosis so far. The currently audited selector stack cannot read the leaderboard edge being optimized. Adding more micro-blends is almost guaranteed to produce unverifiable candidates unless a new selector has sub-gap error or the candidate movement is much larger while still low-risk.
- Decision: strict submit candidate count remains `0`. Do not rank near-A2C8 candidates as improvement submissions from current selectors. The next work should either generate an independent selector target with error below `0.0000869862`, create a larger sign-consistent movement, or spend a public sensor with a predeclared worldview question.

## E44. Large-Edge Low-Risk Census

- Observe: E43 left one plausible escape route: perhaps the existing scored universe already contains a larger movement whose edge is big enough to dominate selector error, even though the visible top micro-edges do not.
- Wonder: among all current selector/candidate score tables, is there any low-bad-axis, raw05-compatible, two-selector-supported candidate with pairwise p90 edge greater than the best selector error `0.000218288`?
- Hypothesis: if the plateau is mainly candidate-selection failure rather than representation/selector-resolution failure, at least one existing scored candidate should have selector-error-scale pairwise edge and pass low-risk gates.
- Method: `analysis_outputs/large_edge_lowrisk_census.py` normalized 29 candidate/selector tables into 69,869 score rows and 48,088 unique files. It compared pairwise p90 edge against the raw05-A2C8 gap `0.0000869862` and the E43 best selector error `0.000218288`, then required low bad-axis, raw05 compatibility, no hard veto, and two-selector or submit-like support for a normal large-safe gate.
- Result:
  - pair-negative rows/files: `12855` / `12309`.
  - pair edge greater than raw05-A2C8 gap: rows `0`, files `0`.
  - pair edge greater than selector error: rows `0`, files `0`.
  - large-pair low-bad rows/files: `0` / `0`.
  - normal large-safe rows/files: `0` / `0`.
  - best pair edge: `0.000073768`, only `0.337941` of selector error and `0.848048` of the raw05-A2C8 gap.
  - any-edge-above-selector rows/files: `25` / `21`, but these come from raw/anchor conflict views such as inverse7 and mixmin, not pairwise public-order support.
- Interpretation: the "maybe we already have a large safe candidate" escape route is closed for the current scored universe. Large favorable signals exist, but only in raw-structure or anchor-loss views while pair/old selectors veto them. This reinforces that the next useful move is not another candidate rescore; it is a new selector target, a genuinely larger sign-consistent representation move, or an explicitly labeled public sensor.
- Decision: strict submit candidate count remains `0`. The current candidates are still sensors, not improvement submissions.

## E45. Structured Public-Subset Feasibility

- Observe: E43-E44 closed the obvious "selector can read micro-edges" and "existing universe hides a larger safe edge" routes. The next cheap falsification is whether public LB is mostly a simple structured test subset that can be recovered from subject/date/order/raw-domain masks.
- Wonder: can a predeclared mask family plus train-derived target priors predict held-out known public anchors at selector-scale error, or do inverse public worlds remain too underdetermined?
- Hypothesis: if public LB is dominated by a simple structured subset, at least one mask should produce known-anchor LOO MAE below the E43 selector error `0.000218288`, preferably below the raw05-A2C8 gap `0.0000869862`, and feasible ranges should be narrow enough to rank candidates.
- Method: `analysis_outputs/structured_public_subset_feasibility.py` tested 145 masks across subject, subject-complement/group, key-order prefix/suffix/window/mod, per-subject head/mid/tail, calendar/date/dow/month, raw-domain logistic/density/missingness/cluster, and random controls. For each mask and held-out anchor it fit soft hidden labels on the remaining 7 anchors under train global +/-0.10 and subject-target +/-0.20 constraints, then selected the minimum-deviation solution from shrunk subject train priors. It also computed feasible ranges for the best and representative masks.
- Result:
  - selector-scale gates: `0`.
  - strict sub-gap gates: `0`.
  - best LOO MAE: `0.000429528` from `global_key_order/suffix_frac0.20`.
  - best LOO MAE / raw05-A2C8 gap: `4.937886`.
  - best LOO MAE / selector error: `1.967712`.
  - best mask max absolute LOO error: `0.00129817`.
  - feasible ranges remain very wide: best-mask range mean width `0.0427582`, all-row mean width `0.0455258`; actual anchors sit inside the ranges only because the ranges are too broad.
- Interpretation: simple public-subset structure is not the missing selector target. A few masks recover A2C8-best and raw05 direction, but their error is still far above the public edge being optimized, and feasible intervals are orders of magnitude too wide. Public subset mismatch remains real, but it is not locally recoverable as an obvious subject/order/date/raw-domain mask under these priors.
- Decision: strict submit candidate count remains `0`. Do not spend more work on simple structured-mask public subset recovery unless a new public observation supplies a real mask anchor or the mask model gains a new independent target.

## E46. Block-State Bottleneck Audit

- Observe: earlier oracle results showed a validation block-rate oracle at `0.517878`, but that evidence was scattered across oracle, Markov, threshold, hidden-block reconstruction, lag, topology, and E45 public-mask reports.
- Wonder: is the 0.54 barrier mostly row-level signal scarcity, or failure to infer hidden block-level target-rate states?
- Hypothesis: if hidden block-rate state is the true bottleneck, then (1) block-rate oracle headroom should be large enough for 0.5x, (2) static subject identity should explain only a fraction of that headroom, and (3) Markov transitions, endpoint flanks, nested one-feature thresholds, and simple public masks should fail to recover the missing state.
- Method: `analysis_outputs/block_state_bottleneck_audit.py` joined `breakthrough_oracle_bounds.csv`, `breakthrough_markov_results.csv`, `breakthrough_threshold_results.csv`, `breakthrough_split_blocks.csv`, `data_dissection_label_lag_autocorr.csv`, `hidden_block_rate_reconstruction_*`, and E45 structured mask outputs. It wrote `block_state_bottleneck_summary.csv`, `block_state_bottleneck_target_detail.csv`, `block_state_bottleneck_topology.csv`, `block_state_bottleneck_subject_patterns.csv`, and `block_state_bottleneck_report.md`.
- Result:
  - validation block-rate oracle mean LogLoss: `0.517878`.
  - temporal-to-block-rate oracle gap: `0.106888`.
  - full subject identity explains only `0.291286` of that gap.
  - remaining gap after full subject oracle: `0.075753`.
  - best Markov transition model is worse than temporal by `+0.002998`.
  - nested single-feature threshold is worse than temporal by `+0.044275`, while validation-selected cheating threshold improves by `0.056364`.
  - endpoint pseudo-hidden block reconstruction gains only `0.003252` over subject mean, about `0.030429` of the temporal-to-block oracle gap.
  - `26/36` submission blocks have two train flanks, so context often exists but is not being interpreted correctly.
  - mean lag1 target correlation is only `0.226420`, and E45 best simple public mask LOO MAE remains `0.000429528`.
- Interpretation: 0.54 is structurally possible only if hidden block rates can be identified. Current context heuristics see pieces of the structure but do not reconstruct the block-state vector. This is stronger evidence for a block-rate JEPA target than for another row classifier, Markov smoother, endpoint propagation, or public-mask inverse fit.
- Decision: strengthen H03 and add H45. The next JEPA experiment should predict held-out block-rate vectors from sparse subject/train-block/overnight/measurement-process context and use the residual as energy; do not build a submission from the current audit alone.

## E47. Block-Context JEPA Target Audit

- Observe: E46 made the target representation explicit. A useful JEPA-style branch should predict held-out block-rate vectors from available context, not just improve row predictions through another shrinkage layer.
- Wonder: do same-subject label context, sensor block summaries, and missingness/measurement-process signatures contain the hidden block-state vector, or only weak calibration perturbations?
- Hypothesis: if the current block summaries contain the missing state, a fold-safe context-to-block-rate model should beat temporal block context on block-rate loss and recover a meaningful share of the `0.106888` temporal-to-oracle gap.
- Method: `analysis_outputs/block_context_jepa_target_audit.py` reused the fold-safe pseudo-hidden block generator from `block_level_regressor_experiments.py`. It trained fixed Ridge heads from four context views (`label_context`, `sensor_values`, `missingness`, `combined`) to held-out block-rate vectors, then evaluated direct block-rate loss, 25%/50% row blends, targetwise deltas, and LeJEPA-style geometry/energy.
- Result:
  - temporal row LogLoss `0.624765`; block-rate oracle `0.517878`; available gap `0.106888`.
  - best non-base 25% row blend: `label_context_ridge` at `0.623260`, delta `-0.001505`, only `0.014083` of oracle gap recovered.
  - temporal block weighted LogLoss `0.623448`; `label_context_ridge` block weighted LogLoss `0.635888`, worse by `0.012440`.
  - `sensor_values_ridge` worsens row blend by `+0.000660` and has block-rate loss `0.657811`.
  - geometry is non-collapsed but not predictive enough: `label_context_ridge` anisotropy `0.466748`, effective rank `3.547232`, top20 block energy share `0.235049`.
  - apparent targetwise row-blend gains are small and selection-fragile: Q3 sensor values `-0.004395`, S3 label context `-0.003986`, Q1 combined `-0.003491`, Q2 missingness `-0.003010`.
- Interpretation: current context views do not reconstruct hidden block-rate state. The best row blend improves while block-rate target loss is worse than temporal, so the gain is better read as weak calibration perturbation than JEPA-style target representation learning.
- Decision: add H46/F34/FH42. Keep submission gate closed. Do not repeat Ridge block-rate regressors on the same block summary views. The next block-state experiment must change the context/target construction, for example discrete count/posterior targets, contrastive subject-block retrieval, raw overnight sequence tokenization, or a public/anchor-conditioned energy target.

## E48. Mixmin Public Sensor Observation

- Observe: after E38, the maximum-information public sensor was `analysis_outputs/submission_mixmin_0c916bb4.csv`, but it was explicitly labeled high-risk because pairwise/old selectors vetoed it and normal submit gates were `0`.
- Wonder: was the anchor-loss/binary actual-anchor worldview a real public signal, or only an overfit to known public-anchor decompositions?
- Hypothesis: if the anchor-loss/binary actual-anchor worldview is closer to the true public hidden world than pairwise/old selectors, mixmin should beat the previous frontier despite selector veto. If it fails, E32-E38 anchor-loss support is not public-generalizing.
- Public observation: `submission_mixmin_0c916bb4.csv` scored `0.5763066405`.
- Result:
  - Previous best `submission_frontier_cvjepa_refine_a2c8d2c8.csv`: `0.5774393210`.
  - Improvement vs previous best: `-0.0011326805`.
  - Improvement vs raw05 `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv`: `-0.0012196667`.
  - The improvement is about `13.02x` the previous raw05-a2c8 gap `0.0000869862`.
- Interpretation: the public sensor succeeded. The old conclusion "mixmin is not safe" remains valid as a pre-public risk warning, but the stronger conclusion "pairwise/old selector veto should block this branch" is now falsified. Anchor-loss/cancellation geometry and binary actual-anchor worlds were public-relevant.
- Decision: promote mixmin to the active public frontier. Next work should stop optimizing around a2c8 micro-edges and instead explain why mixmin worked, decompose its target/row movement, recalibrate selectors with mixmin as a known anchor, and design mixmin-relative candidates. E46/E47 remain relevant for 0.54 because mixmin improves the frontier but does not yet solve hidden block-rate state inference.

## E49. Post-Mixmin Observation Audit

- Observe: E48 gave a strong public observation, but score alone does not say whether mixmin won by ordinary prevalence correction, hidden public subset luck, or a real block/state move.
- Wonder: does mixmin's movement look like train/global, subject, or recent-target prior correction, or does it concentrate on subject-calendar holes that require a richer hidden-world explanation?
- Hypothesis: if mixmin is ordinary prior correction, its target movement should be supported by global/subject/recent priors and should not depend on calendar mask topology. If it is hidden-block/state movement, simple priors should give mixed or contradictory support and the movement should concentrate by subject, target, and train/test calendar runs.
- Method: `analysis_outputs/post_mixmin_observation_audit.py` compared mixmin, previous a2c8, and raw05 predictions; computed target/subject/row movement; evaluated CE deltas under train/global, subject, and recent7 target priors; and reconstructed per-subject train/test calendar masks.
- Result:
  - Train/test rows are `450/250`, with `10/10` subjects. Test dates are not a future-only holdout; they are hidden calendar blocks inside each subject timeline, often before the subject's train max date and flanked by train runs.
  - Largest mean absolute mixmin movements are `Q3 = 0.011540`, `Q1 = 0.010345`, and `S3 = 0.009688`.
  - Simple prior stress is contradictory: `Q1` and `S1` are worse under train/global, subject, and recent7 priors, while `S2/S3` are helped mostly by global priors and `Q3/S4` need recent7-like priors.
  - Subject movement is concentrated in `id05`, `id09`, `id08`, `id03`, and `id01`, with dominant targets changing by subject.
  - Top calendar-mask movement blocks are often `gap_adjacent` or `between_train_runs`; the natural JEPA context is labeled train flanks around hidden test blocks, and the target should be a block label-rate/count representation rather than a row probability.
- Interpretation: mixmin is not explained by ordinary prevalence correction. E49 strengthens the view that the task is subject-calendar hidden-block restoration. The active mystery is now which hidden blocks have the target-rate state that mixmin approximates, and whether that state can be inferred without public-anchor overfit.
- Decision: add H48/F35 and use E49 as the next selector-design constraint. The next useful experiment is mixmin-anchor selector recalibration with calendar-block movement features, not another model family or a2c8-centered micro-blend.

## E50. Post-Mixmin Calendar Selector Audit

- Observe: E49 made the calendar-mask structure visible, but observation is not yet a selector. The next cheap falsification was whether subject/calendar movement fingerprints can explain the new mixmin frontier when mixmin is added as a known public anchor.
- Wonder: can calendar-run movement fingerprints recover `mixmin` as public-best while preserving raw05/a2c8, stage2/ordinal, and bad-JEPA anchor order?
- Hypothesis: if H48 has immediate selector utility, a mixmin-relative calendar view should pass known-anchor LOOCV by predicting mixmin as best, keeping known order constraints, and keeping selector error below the mixmin-a2c8 public edge scale `0.0011326805`.
- Method: `analysis_outputs/post_mixmin_calendar_selector.py` built target/prior, calendar, subject, and subject-calendar movement features relative to a2c8. Features aggregate probability/logit/entropy movement by target, subject, calendar context, train-span zone, run-length bin, flank signature, and simple train/global, subject, recent7 proxy LogLoss deltas. It then ran kNN known-anchor LOOCV over mixmin, a2c8, raw05, stage2, ordinal, final9, and bad JEPA anchors.
- Result:
  - strict selector views: `0`.
  - loose selector views: `0`.
  - best view `subject_calendar`: LOOCV MAE `0.000884106`, pairwise rank accuracy `0.833333`, Spearman `0.833333`, and bad-tail order correct.
  - But the same best view predicted held-out mixmin delta `0.00135162` instead of `0`, so `mixmin_predicted_best = False` and `mixmin_error_below_edge = False`.
  - All tested views failed to predict mixmin as best. `calendar_no_prior` also failed a2c8/raw05 order.
- Interpretation: calendar topology is real but not sufficient as a standalone public selector. It prices mixmin as a raw05/a2c8-like neighbor rather than the public-best anchor. The missing signal is likely anchor-loss/binary-world geometry, hidden block-rate target information, or their interaction with calendar flanks.
- Decision: add FH43 and revise H48 from "predictive utility untested" to "calendar-only selector falsified, context-target hypothesis still live." No new submission should be made from E50 candidate predictions; they are diagnostic non-forecasts.

## E51. Anchor-Loss x Calendar Selector Audit

- Observe: E50 showed calendar-only selector failure, while E32-E38 plus E48 showed anchor-loss/binary-world geometry was public-relevant enough to select mixmin as a sensor.
- Wonder: does LOO-safe anchor-loss world geometry rescue the calendar selector, or was E32 useful only as a candidate-family sensor rather than a transferable selector metric?
- Hypothesis: if the post-mixmin worldview can be converted into a selector, anchor-loss world aggregates should predict held-out mixmin as best, and adding compact calendar context should improve or at least not degrade known-anchor order.
- Method: `analysis_outputs/post_mixmin_anchor_calendar_selector.py` reused the E30 binary frontier-box worlds. For each known anchor or candidate, it computed per-world target LogLoss deltas versus a2c8. It scored worlds in two LOO-safe modes: `shape` reproduces E32-style cancellation/sign/correlation energy, while `residual` also includes known-anchor residual fit. For each held-out public anchor, that anchor was omitted from world-energy scoring before prediction. Views then combined anchor-world aggregates with target/prior, context-all, or moved-target calendar fingerprints.
- Result:
  - strict selector views: `0`.
  - loose selector views: `0`.
  - best view `anchor_residual`: LOOCV MAE `0.000835516`, rank accuracy `0.750000`, Spearman `0.633333`, and bad-tail order correct.
  - Critical failures: held-out mixmin predicted delta `0.00241739` instead of `0`; `mixmin_predicted_best = False`, `mixmin_error_below_edge = False`, and a2c8/raw05 order was false.
  - Adding calendar context did not rescue the failure: best context view `contextall_anchor_residual` had MAE `0.000889706` and also failed mixmin-best.
- Interpretation: E32/E38 succeeded as a worldview sensor, not as a smooth transferable selector. Binary anchor-loss geometry can say "mixmin is an information-rich public probe" but the tested kNN selector maps held-out mixmin toward worse anchors. The missing object is not calendar features alone or anchor-loss features alone; it is either a new hidden block-rate/count target or a different post-mixmin world construction that treats mixmin as a constraint and tests new candidates out-of-world.
- Decision: add FH44. Keep mixmin as active frontier, but do not generate a submission from E51 candidate predictions. The next high-value local work should stop trying to make kNN over known submission files and instead build a calendar-flank block-rate/count target or a mixmin-constrained binary-world stress for candidate deltas.

## E52. Post-Mixmin Binary-World Sign Stress

- Observe: E51 closed the kNN selector conversion, but it left one sharper question: if mixmin is treated as an observed public anchor rather than a candidate to be predicted, do the E30/E32 binary worlds certify any replacement candidate as one-sided better than mixmin?
- Wonder: is mixmin just the first member of a better post-mixmin family, or is it a local frontier inside the current binary-world family?
- Hypothesis: if a next candidate is already present in the current candidate/bridge pool, then after conditioning worlds on the actual mixmin delta `-0.0011326805`, at least one candidate should have negative max delta versus mixmin across mixmin-compatible and low-energy world bands. If no candidate survives, the binary-world family says "do not replace mixmin yet."
- Method: `analysis_outputs/post_mixmin_binary_world_sign_stress.py` reused the E30 frontier-box binary worlds and E32 anchor energies. It defined post-mixmin feasible bands by whether each world reproduces mixmin's observed public delta within `1x`, `2x`, or `5x` the raw05-a2c8 gap `0.0000869862`, plus a LeJEPA-style `postmix_world_energy` combining old anchor energy and mixmin residual. It scored 158 curated candidates from E51, E37 bridge variants, E38 worldview sensors, and selected bridge families by LogLoss delta versus mixmin on every world.
- Result:
  - mixmin-compatible 1-gap worlds: `5`, all random/fit worlds, median mixmin error `0.326053` raw05-gap units.
  - postmix energy quarter worlds: `7`, median mixmin error `0.342926` raw05-gap units.
  - candidates scored: `158`.
  - strict better-than-mixmin gates: `0`.
  - loose better-than-mixmin gates: `0`.
  - near-tie gates: `1`, led by `analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv`.
  - Best near-tie still failed one-sidedness: mixmin-fit-gap better rate `0.2`, median delta `+0.000034`, max delta `+0.000048`; postmix-energy-quarter better rate `0.285714`, median delta `+0.000009`.
- Interpretation: existing post-mixmin bridge candidates do not beat mixmin under the binary-world family once mixmin's actual public delta is imposed. The only non-duplicate survivor is a near-tie that is slightly worse on median and positive on max. This converts the E32/E48 lesson from "mixmin was a good public sensor" into a stricter local rule: the current binary-world family does not justify replacing mixmin with inverse7, pair sensors, or bridge blends.
- Decision: add FH45 and F37. Keep `submission_mixmin_0c916bb4.csv` as the active frontier and do not submit the E52 near-tie. The next high-value branch is no longer another existing-candidate sign rescore; it is either a true calendar-flank block-rate/count target or a regenerated binary-world pool that includes mixmin in the MILP constraints and searches for new movements, not just rescoring existing files.

## E53. Calendar-Flank Block Count-State Probe

- Observe: E52 closed the current replacement pool, so the next cheap falsification was whether mixmin is approximating a hidden block count/rate state that can be recovered from labeled calendar flanks rather than from submission-file neighbors.
- Wonder: do previous/next labeled blocks, subject identity, hidden block length, and donor block count signatures predict pseudo-hidden target count state; and if they do, does that state independently prefer mixmin over a2c8 on real hidden blocks?
- Hypothesis: if calendar-flank count state is the missing JEPA target, a fold-safe posterior should beat subject mean on pseudo-hidden train blocks, survive strict donor exclusion, and assign actual hidden blocks rates under which mixmin has negative expected LogLoss delta versus a2c8.
- Method: `analysis_outputs/calendar_flank_block_count_state_probe.py` built `369` pseudo-hidden train blocks using the real test hidden-block length distribution and `36` real hidden submission blocks. It compared `subject_mean`, two edge-shrink baselines, `calendar_count_local` donors, and `calendar_count_strict` donors that exclude the same subject. Stress checks were pseudo-hidden weighted row LogLoss/count NLL, targetwise deltas, and expected hidden-block CE delta for mixmin/raw05 against a2c8.
- Result:
  - `calendar_count_local` was best pseudo-hidden: weighted row LogLoss `0.607736`, delta vs subject mean `-0.005266`.
  - `calendar_count_strict` failed the private-safe version: weighted row LogLoss `0.614436`, delta `+0.001434`.
  - Strict target deltas improved only Q targets: Q1 `-0.011907`, Q2 `-0.029170`, Q3 `-0.011743`; S1 `+0.001126`, S2 `+0.024074`, S3 `+0.034293`, S4 `+0.003363` worsened.
  - Local target deltas improved Q1/Q2/Q3/S1 but worsened S2/S3/S4.
  - On real hidden blocks, strict predicted rates weakly favored mixmin overall: weighted expected mixmin delta vs a2c8 `-0.000179`, better-block rate `0.527778`; local was adverse overall at `+0.000250`.
  - Strict hidden target alignment favored S3 `-0.003537`, S2 `-0.002363`, and Q2 `-0.000820`, but hurt S1 `+0.003665`, S4 `+0.000821`, Q1 `+0.000649`, and Q3 `+0.000333`.
- Interpretation: calendar-flank count state is a real context signal, but the part that improves pseudo-hidden blocks is mainly local/same-subject and does not transfer cleanly under strict donor exclusion. The actual hidden-block alignment partially explains why mixmin may help S2/S3/Q2, but it does not explain Q1/Q3 and over-penalizes S1. This is a LeJEPA-style geometry warning: the representation has useful energy but the safe latent is not coherent enough to generate a submission.
- Decision: add H50, FH46, and F38. No submission should be made from this posterior or a direct mixmin tweak based on it. Keep it as a calendar-flank count-state energy and move next to richer raw overnight context, target-dependency count manifolds, or fresh mixmin-hard world generation.

## E54. Raw Overnight Block Context Probe

- Observe: E53 left a clean split. Calendar flanks contained local block-state signal, but strict subject-excluded recovery failed. Overnight raw sensor context was the smallest remaining way to ask whether the hidden block-state latent exists outside same-subject donor shortcuts.
- Wonder: can raw overnight context plus labeled flanks predict pseudo-hidden block count/rate state under strict subject exclusion, and does that same latent explain the public-validated mixmin edge?
- Hypothesis: if raw overnight context encodes the hidden sleep-state generator, raw/ctx block embeddings should beat subject mean and simple calendar-count strict posteriors on pseudo-hidden blocks without same-subject donors, especially on S targets. If it is the mixmin-public latent, the same predicted hidden rates should make mixmin better than a2c8 on actual hidden blocks.
- Method: `analysis_outputs/raw_overnight_block_context_probe.py` compressed `overnight_sensor_features_v2.parquet` feature families into row PCA views, aggregated them to block-level mean/std/min/max/first/last/slope vectors, optionally concatenated E53 labeled-flank context, and used kNN donor rate posteriors with shrinkage `alpha=24`. Strict mode excluded the target subject; local mode was retained as shortcut diagnostic.
- Result:
  - pseudo-hidden blocks `369`; actual hidden blocks `36`.
  - best strict method: `night_phone_rawctx_strict_k8_a24`, weighted row LogLoss `0.605269`, delta vs subject mean `-0.007733`.
  - local shortcut diagnostics were stronger, led by `night_phone_rawctx_local_k8_a24` delta `-0.011361`, but the important result is that strict recovery also improved materially.
  - best strict target deltas: Q1 `-0.010726`, Q2 `-0.017247`, Q3 `-0.016308`, S1 `-0.009910`, S2 `-0.006878`, S3 `+0.007802`, S4 `-0.000865`.
  - geometry did not show obvious collapse: effective rank ranged from `23.393361` to `35.124905`, anisotropy from `0.144271` to `0.183029`.
  - actual hidden-block mixmin translation failed for the best strict raw method: `night_phone_rawctx_strict_k8_a24` weighted mixmin delta vs a2c8 was `+0.000311`.
  - the strongest actual hidden alignment remained `calendar_count_strict` at only `-0.000179`.
- Interpretation: raw overnight context is a real strict block-state representation. That is a meaningful positive result for the JEPA hidden-state branch. But it is not the same latent that produced mixmin's public edge: it regresses S3 in pseudo-hidden stress and makes mixmin worse under its actual hidden-rate world. The bottleneck is no longer "no representation"; it is "which representation is public-aligned and how to translate it without target-sign conflict."
- Decision: add H51, FH47, and F39. No submission should be made from direct raw overnight block-rate movement. Keep it as `raw_overnight_block_state_energy`, a validation-mismatch/private-risk diagnostic, and a constraint for the next branch: either target-dependency/S3 correction on the strict raw latent or fresh mixmin-hard world generation using raw context as a feasibility prior rather than a probability move.

## E55. Raw Block Target-Dependency Probe

- Observe: E54 produced the strongest strict representation result so far, but with a split-world failure: raw context improved pseudo-hidden block-state recovery, while S3 and actual hidden mixmin alignment moved the wrong way.
- Wonder: is this failure just a target-manifold translation error? If other predicted target rates imply the hidden S3 or stage count state, a strict target-dependency projection might keep the raw context gain while fixing S3 and flipping the mixmin sign.
- Hypothesis: if Q/S count geometry is the missing translator, then a strict donor projection from other target rates should satisfy three conditions at once: preserve or improve raw pseudo-hidden LogLoss, make S3 non-adverse versus subject mean, and assign actual hidden blocks rates under which mixmin beats a2c8.
- Method: `analysis_outputs/raw_block_target_dependency_probe.py` used E54 `night_phone_rawctx_strict_k8_a24` as base. For each pseudo-hidden block, it projected target rates from strict subject-excluded donor block-rate manifolds using only other target rates as context. It tested kNN and Ridge projections, pair/group/all-cross target contexts, masks over S3, S2/S3, S-stage, and all targets, plus simple S3 replacement baselines.
- Result:
  - methods tested: `225`; joint gates: `0`.
  - raw base: pseudo-hidden weighted row LogLoss `0.605269`, delta vs subject `-0.007733`, S3 delta vs subject `+0.007802`, hidden mixmin delta `+0.000311`.
  - best pseudo-hidden method: `raw_phone_s3_subject_w1p00`, LogLoss `0.604154`, raw delta `-0.001115`, S3 delta `0.000000`, but hidden mixmin delta remained adverse at `+0.000319`.
  - best kNN projection near the raw manifold, `raw_phone_td_knn_groupcross_stage_k8_a24_w0.25`, gave only raw delta `-0.000118`, S3 stayed adverse `+0.007219`, and hidden mixmin stayed adverse `+0.000317`.
  - methods that made hidden mixmin negative were Ridge projections that destroyed pseudo-hidden validity: best hidden `raw_phone_td_ridge_groupcross_all_k0_a8_w0.75` had hidden mixmin delta `-0.000414`, but pseudo-hidden LogLoss `0.727319`, raw delta `+0.122051`, and S3 delta `+0.207892`.
  - `calendar_count_strict` remained a weak hidden-sign comparator at `-0.000179`, but its pseudo-hidden raw delta was `+0.009167` and S3 was `+0.034293`.
- Interpretation: target-dependency projection can improve one axis at a time, but not the joint condition. Replacing S3 with subject mean improves pseudo-hidden loss, but it does not move the actual hidden world toward mixmin. Forcing hidden mixmin sign with Ridge collapses pseudo-hidden validity and creates a large S3 error. The raw overnight latent and mixmin-public latent are not connected by a simple Q/S count manifold projection.
- Decision: add H52, FH48, and F40. No submission. The next live branch should stop post-hoc target projection and either generate a fresh mixmin-hard binary world with raw context as a feasibility prior, or define a more structural target representation beyond simple target-rate manifold projection.

## E56. Mixmin-Hard Raw World Probe

- Observe: E55 closed the simple target-rate translation route. The remaining cheap branch was to stop treating mixmin as a candidate and regenerate hidden binary worlds with mixmin itself as an observed public constraint, while using the E54 raw overnight block-state posterior only as a feasibility/energy prior.
- Wonder: if the world generator is forced to respect the actual mixmin public edge, does raw block-state feasibility produce a coherent posterior movement that is not already present in existing candidates?
- Hypothesis: if mixmin-hard raw worlds capture the next hidden structure, existing candidates may still fail, but posterior averaging over those worlds should create internally stable mixmin-relative movements. If this is just self-consistent world fitting, the movement should be large and require an independent anchor safety gate before submission.
- Method: `analysis_outputs/mixmin_hard_raw_world_probe.py` built `45` world objectives across mixmin-compatible scenarios, included `9` known public anchors with mixmin as a hard observation, and added E54 `night_phone_rawctx_strict_k8_a24` raw hidden block rates as raw CE/count feasibility energy. It scored existing candidates and fold-style posterior variants over held-out world groups.
- Result:
  - worlds generated: `45`; unique binary worlds: `44`.
  - existing candidate strict gates: `0`.
  - posterior world-LOO strict gates: `12`.
  - best internal posterior: `posterior_raw_energy_quarter_w0.28`, held worlds `11`, better_rate `1.0`, median delta `-0.154291`, p90 `-0.069887`, max delta `-0.069103`.
  - generated diagnostic submission: `analysis_outputs/submission_mixhard_rawposterior_af1502f9.csv`.
  - movement versus mixmin was large: mean abs probability move `0.078656`, mean abs logit move `0.381359`, max abs logit move `1.215720`; all target mean deltas were positive.
- Interpretation: mixmin-hard raw worlds are a coherent hidden-world generator, and they create a posterior that is internally decisive. But that does not yet mean public-safe probability movement; the selected posterior may be optimizing the generated world family rather than the independent public-anchor geometry.
- Decision: add H53 and F41. Do not submit the diagnostic file until E57 or an equivalent independent public-anchor stress accepts it.

## E57. Mixmin-Hard Raw Posterior Safety Stress

- Observe: E56 created a strong internal posterior, but the probability movement was much larger than mixmin and had no independent public-anchor safety proof.
- Wonder: does any E56 posterior variant survive actual-anchor/public-shape stress against mixmin, or is the posterior only useful as a teacher/energy?
- Hypothesis: if the E56 posterior is a public-safe candidate, at least one variant should pass three gates together: E56 world-LOO strict pass, actual-anchor score better than mixmin, and mean abs logit movement versus mixmin no larger than `0.08`.
- Method: `analysis_outputs/mixmin_hard_raw_posterior_safety_stress.py` reconstructed E56 posterior variants from the generated worlds, scored them with the independent `actual_anchor_score` proxy, and compared them against mixmin, raw05, and a2c8.
- Result:
  - variants scored: `15`; joint safety gates: `0`.
  - mixmin actual-anchor score: `0.577734`.
  - best posterior by actual-anchor stress: `posterior_all_w0.05`, score `0.577857`, delta versus mixmin `+0.000123`; it passed world-LOO and movement guard but still did not beat mixmin.
  - E56 selected diagnostic `posterior_raw_energy_quarter_w0.28` / `submission_mixhard_rawposterior_af1502f9.csv` had actual-anchor score `0.598116`, delta versus mixmin `+0.020381`, and mean abs logit movement `0.381359`; movement guard failed.
- Interpretation: the E56 world family exposes useful hidden posterior energy, but direct posterior movement is public-anchor adverse. This is the cleanest current separation between "world-model coherence" and "submission-safe translation."
- Decision: add H54 and FH49. No submission from E56 posterior files. The next live branch is anchor-constrained distillation of the E56 posterior or a more structural block target, not direct posterior averaging.

## E58. Mixmin-Hard Posterior Distillation Probe

- Observe: E57 rejected direct E56 posterior averaging, but did not test whether the E56 teacher has a small anchor-compatible subdirection near mixmin.
- Wonder: can the E56 posterior be distilled only on confident cells, target groups, and row gates so that it keeps world-model support while staying inside actual-anchor geometry?
- Hypothesis: if E56 posterior contains a submission-safe subdirection, a toward-teacher gated candidate should satisfy world guard, movement guard, and actual-anchor improvement margin `< -1e-5` versus mixmin. If only tiny sub-margin anchor changes appear, E56 is energy/teacher but not a candidate generator yet.
- Method: `analysis_outputs/mixmin_hard_posterior_distillation_probe.py` generated `104727` candidates from E56 posterior bands, target masks, raw-agreement/support/entropy cell gates, row gates, caps, and small weights. It prefiltered by movement and generated-world support, then actual-anchor scored `1200` candidates including `900` toward-teacher and `300` reverse-control candidates.
- Result:
  - eligible toward-teacher submission gates: `0`.
  - diagnostic reverse-control gates: `0`.
  - best toward-teacher actual-anchor delta after E61 index correction: `-0.000004081`, from `toward_teacher|low_slack_half|no_q2|raw_agree|all|w0.070|c0.120`.
  - best reverse-control actual-anchor delta after E61 index correction: `-0.0000000126`.
  - all top toward-teacher candidates had world guard and small movement, but none cleared the `1e-5` anchor margin.
- Interpretation: E56 posterior contains a very small mixmin-neighborhood direction that is not obviously anchor-adverse after gating, but the effect is below selector/public-sensor resolution. Reverse controls do not reveal a stronger opposite direction. This keeps E56 as a teacher/energy axis but closes the first simple distillation route as a submission source.
- Decision: add H55, FH50, and F42. No submission. The next branch should either make the structural block target richer, or add an independent non-anchor validation signal before trusting any sub-`1e-5` distillation movement.

## E59. Structural Block Target Representation Probe

- Observe: E55 closed the seven-marginal-rate target-dependency route, and E58 showed E56 posterior distillation is below margin. The remaining structural question was whether the target itself is wrong: maybe hidden blocks live on a joint Q/S label-pattern manifold that marginal rates erase.
- Wonder: if a JEPA target is a 128-state joint label-pattern distribution per block, can raw/calendar/subject context predict it under strict donor exclusion, and does that structural target align with the mixmin public frontier?
- Hypothesis: if joint block target structure is the missing public-aligned latent, then structural kNN should improve pseudo-hidden pattern NLL and row LogLoss versus raw independent marginals, carry joint information beyond its own marginals, avoid S3 regression, and give negative hidden mixmin delta.
- Method: `analysis_outputs/structural_block_target_probe.py` reused E55 `build_base_state()`, built 128 joint label-pattern count distributions for pseudo-hidden train blocks, predicted them with strict subject-excluded kNN over raw/calendar/subject context variants and raw/subject independent fallbacks, and stressed each method with pattern NLL, own-margin joint gain, row LogLoss, S3 target stress, and actual hidden-block mixmin alignment.
- Result:
  - methods scored: `219`; structural methods: `216`; joint gates: `0`.
  - `139/216` structural methods improved pattern NLL versus raw independent baseline.
  - `198/216` structural methods carried joint information beyond their own marginal rates.
  - row LogLoss gates were `0`: every structural method worsened row LogLoss versus raw.
  - best structural method `struct_raw_calendar_subject_fbsubject_k16_a12_w0.35`: pattern NLL delta vs raw `-0.062594`, own-margin joint gain `-0.088340`, row LogLoss delta vs raw `+0.003678`, S3 delta vs subject `+0.002727`, hidden mixmin delta `+0.000304`.
  - best hidden-sign method `struct_raw_subject_fbraw_k8_a4_w1.00`: hidden mixmin delta `-0.000367`, but row LogLoss delta vs raw `+0.042230`, pattern NLL delta vs raw `+0.300872`, and S3 delta vs subject `+0.078145`.
- Interpretation: the data does contain nontrivial block-level joint target structure, and strict context can predict some of it. But this structure is not the public-aligned probability movement. Pattern NLL gains trade off against marginal row calibration, S3 health, and hidden mixmin sign. This is a LeJEPA-style warning: representation quality under one target geometry can be real while still being the wrong latent for the submission frontier.
- Decision: add H56, FH51, and F43. No submission. Do not repeat simple joint-pattern kNN translation. Next useful branch is independent non-anchor validation for E56 energy, or a structural target that includes transition/topology/mixmin-disagreement energy rather than within-block joint labels alone.

## E60. Transition-Residual Block-State Probe

- Observe: E59 proved joint pattern structure is real but target-mismatched. The next sharper question was whether the missing JEPA target is a transition state: the residual movement from labeled flanks/raw/subject baseline into the hidden run.
- Wonder: can strict subject-excluded context predict the hidden block's logit-rate residual from endpoints/raw/subject state, and does that residual independently validate the mixmin-hard posterior direction?
- Hypothesis: if transition residual is the missing public-aligned block state, a method should simultaneously beat E54 raw phone base on pseudo-hidden row LogLoss, reduce transition-residual MSE, avoid S3 regression versus subject mean, and make mixmin better than a2c8 under actual hidden-block predicted rates.
- Method: `analysis_outputs/transition_residual_block_state_probe.py` reused E55 `build_base_state()`. It tested endpoint, subject, and raw bases; topology, raw-residual, raw-topology, and full-transition contexts; strict subject-excluded kNN residual prediction in logit-rate space; pseudo-hidden row/residual stress; and real hidden-block mixmin alignment.
- Result:
  - methods scored: `438`; transition methods: `432`; joint gates: `0`.
  - row-beats-raw methods: `1`, and that method was the raw baseline itself.
  - transition-residual MSE beats raw: `227`; hidden mixmin negative: `217`; S3 fixed versus subject: `5`.
  - best row-valid transition `transition_raw_residual_baseraw_k4_a24_w0.35`: row delta vs raw `+0.000186`, residual MSE delta `-0.017074`, S3 delta vs subject `+0.007783`, hidden mixmin delta `+0.000230`.
  - best hidden-sign method `transition_raw_residual_baseedge_mid_k4_a4_w1.00`: hidden mixmin delta `-0.001569`, but row delta vs raw `+1.519232`, residual MSE delta `+25.448213`, and S3 delta vs subject `+1.331880`.
  - target hidden alignment for the best hidden-sign method favored Q1 `-0.001456`, Q2 `-0.001469`, Q3 `-0.001997`, S2 `-0.001371`, and S3 `-0.008884`, but hurt S1 `+0.004075` and S4 `+0.000120`.
- Interpretation: transition residual is a real hidden-direction sensor but not a valid probability translator. The sign that likes mixmin is obtained by aggressive endpoint-residual moves that destroy pseudo-hidden calibration. Conservative raw-based transition residuals preserve row validity but do not explain mixmin.
- Decision: add H57, FH52, and F44. No submission. Use transition residual only as a diagnostic energy for teacher reliability; do not generate public files from hidden-sign residual methods.

## E61. E58 Score-Index Integrity Audit

- Observe: while designing a transition-gated E56 teacher experiment, E58's scoring path showed a possible mismatch. `score_prefilter()` sorted and reset candidate rows, but `attach_anchor_scores()` selected probability arrays by the post-sort DataFrame index rather than a stable candidate prediction index.
- Wonder: was the E58 no-submission conclusion an artifact of scoring the wrong probability arrays against candidate names?
- Hypothesis: if E58 rejection was an index artifact, corrected scoring could change the best anchor deltas, open an eligible candidate, or make reverse controls stronger than toward-teacher movement.
- Method: patch `analysis_outputs/mixmin_hard_posterior_distillation_probe.py` to store `pred_index` at candidate generation and use it during actual-anchor scoring; rerun E58 end to end.
- Result:
  - generated candidates: `104727`; actual-anchor scored: `1200`.
  - eligible toward-teacher gates: `0`; diagnostic reverse gates: `0`.
  - corrected toward-teacher sign-level anchor improvements: `126/900`, not the previous mismatched `631/900`.
  - corrected best toward-teacher anchor delta: `-0.000004081`, from `toward_teacher|low_slack_half|no_q2|raw_agree|all|w0.070|c0.120`.
  - corrected best reverse-control anchor delta: `-0.0000000126`, with world guard `0`.
- Interpretation: the implementation bug was real, but it did not hide a candidate. It actually weakens the "many safe sign-level improvements" phrasing while preserving the core conclusion: E56 distillation remains below selector-scale margin.
- Decision: add H58/FH53. Keep E58 rejected as a submission source. Future scoring scripts must carry stable prediction indices through sorted prefilters.

## E62. Transition-Gated Posterior Distillation Probe

- Observe: E56 posterior energy is coherent internally, corrected E58 simple slicing is below margin, and E60 transition residuals sense hidden mixmin sign only when direct residual predictions collapse row calibration.
- Wonder: can transition residuals be used only as gates for small E56 teacher movements, without using transition predictions as probability targets?
- Hypothesis: if transition residual is the missing independent validator for E56 teacher cells, transition-gated candidates should improve over E58's corrected best anchor delta and open at least one toward-teacher gate with `anchor_delta_vs_mixmin < -1e-5`, while preserving world and movement guards.
- Method: `analysis_outputs/transition_gated_posterior_distillation_probe.py` selected E60 row-safe, balanced hidden-sign, and aggressive hidden-sign residual views; converted them into sign/block/target gates; generated capped logit moves from mixmin toward E56 teacher; prefiltered by E56-world support; and actual-anchor scored `1300` candidates.
- Result:
  - generated candidates: `363258`; actual-anchor scored: `1300`.
  - eligible toward-teacher gates: `0`; diagnostic reverse gates: `0`.
  - best toward-teacher anchor delta: `-0.000002716`, from `toward_teacher|low_slack_half|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080`.
  - best reverse-control anchor delta: `-0.00000000547`.
  - aggregate transition views were coherent as diagnostics: row-safe hidden mixmin delta `+0.000261`, balanced hidden-sign `-0.000289`, aggressive hidden-sign `-0.001483`, but this did not translate into a submission-scale gate.
- Interpretation: transition residual gates make the best candidate more interpretable (`balanced hidden-sign + raw agreement`, excluding S3), but not stronger. The local margin is smaller than corrected E58, so transition residual is not the missing non-anchor validator for E56 energy in this form.
- Decision: add H59/FH54/F45. No submission. Future E56 validation must use a different target or a richer structural model that includes transition residual without letting it dominate calibration.

## E63. Gradient-Consensus Posterior Probe

- Observe: E62 closed transition residual as a simple E56 gate, but it did not answer whether the E56 teacher direction itself is supported by independent hidden-rate views. The remaining ambiguity was direction versus translation: maybe E56 points the right way but every tested gate has too little selector-scale amplitude.
- Wonder: if subject/calendar/raw/transition hidden-rate views define an independent BCE-gradient field at mixmin, do E56 teacher cells move down that field, and does that agreement make an actual-anchor-safe candidate?
- Hypothesis: if gradient-consensus is the missing validator, toward-teacher candidates should pass hidden-rate guards across independent views, reverse controls should fail, and at least one toward candidate should clear actual-anchor margin `< -1e-5` while preserving E56 world and movement guards.
- Method: `analysis_outputs/gradient_consensus_posterior_probe.py` built hidden-rate views from subject mean, strict calendar counts, raw phone base, row-safe transition, balanced/aggressive transition hidden signs, and a core median of calendar/raw/balanced transition logits. It scored whether E56 teacher deltas move down the BCE gradient implied by those rates, generated capped logit moves from mixmin toward E56 teacher, prefiltered by hidden/world/movement guards, and actual-anchor scored `1300` candidates.
- Result:
  - generated candidates: `404671`; actual-anchor scored: `1300`.
  - toward-teacher candidates: hidden guard `1000/1000`, world guard `1000/1000`, movement guard `1000/1000`, anchor beats `932/1000`, eligible gates `0`.
  - reverse controls: hidden guard `0/300`, world guard `0/300`, movement guard `300/300`, anchor beats `260/300`, diagnostic gates `0`.
  - best toward-teacher anchor delta: `-0.000003650`, from `toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|w0.070|c0.080`.
  - best toward hidden-core mean delta: `-0.000368596`.
  - best reverse anchor delta: `-0.00000000894`.
- Interpretation: this is the first post-E58 validator that cleanly separates direction from reverse control across independent hidden-rate views. E56 is not merely random teacher noise. But the same validator still fails the public-anchor margin, and its best anchor delta is smaller than corrected E58's `-0.000004081`. The bottleneck is now sharper: E56 has a real-looking hidden direction, but the current logit cap/gate family cannot translate it into selector-scale public movement.
- Decision: add H60/FH55/F46. No submission. Use gradient-consensus as direction/energy evidence only; the next experiment should learn or derive amplitude/public-anchor translation from the cells where hidden gradient, E56 world support, and mixmin public movement all agree.

## E64. Gradient-Amplitude Translation Probe

- Observe: E63 validated E56 direction but used very small capped logit moves. The immediate falsifiable question was whether E63 is simply under-amplified.
- Wonder: if we keep the E63 gradient-consensus cells and scale them up with broader caps and gain-shaped amplitudes, does actual-anchor improvement become selector-scale, or does public-anchor geometry reject larger movement?
- Hypothesis: if scalar amplitude is the missing translator, larger toward-teacher moves should keep hidden/world guards and produce at least one `anchor_delta_vs_mixmin < -1e-5` candidate, while reverse controls stay adverse.
- Method: `analysis_outputs/gradient_amplitude_translation_probe.py` focused on the strongest E63 gate families, generated flat and core-gain shaped moves with larger scales/caps, prefiltered by E56 world support, hidden-rate guard, and movement guard, then actual-anchor scored `1796` candidates.
- Result:
  - generated candidates: `12096`; actual-anchor scored: `1796`.
  - toward-teacher candidates: hidden guard `1346/1346`, world guard `1346/1346`, movement guard `1346/1346`, anchor beats `0/1346`, eligible gates `0`.
  - reverse controls: hidden guard `0/450`, world guard `0/450`, movement guard `450/450`, anchor beats `0/450`, diagnostic gates `0`.
  - best toward-teacher anchor delta: `+0.000003024`, from `toward_teacher|all|no_s3|raw_agree|grad_core_top50|all|core_gain|s0.50|c0.080`.
  - best reverse-control anchor delta: `+0.000000154`.
- Interpretation: this is a strong negative result. Direction validation survives because every scored toward candidate passes hidden/world guards, but larger amplitude reverses actual-anchor sign. The useful E56 direction appears confined to a tiny neighborhood around mixmin; beyond that, public-anchor LogLoss penalizes the move.
- Decision: add H61/FH56/F47. No submission. Stop treating E56 gradient consensus as a scalar scale problem; the next branch needs targetwise amplitude/calibration modeling or a structural target that changes which cells move, not merely how far all validated cells move.

## E65. Near-Zero Amplitude Response Probe

- Observe: E63 had a tiny favorable edge and E64 rejected larger scalar movement. The remaining possibility was a narrow targetwise near-zero pocket, not global scaling.
- Wonder: can small target-specific E56 gradient movement, especially masks that exclude Q2/S3 conflict targets, clear the actual-anchor margin while preserving hidden/world guards?
- Hypothesis: if a near-zero targetwise amplitude pocket exists at submission scale, a line search over small scales and target masks should produce `anchor_delta_vs_mixmin < -1e-5` with hidden/world/movement guards intact.
- Method: `analysis_outputs/near_zero_amplitude_response_probe.py` generated `27384` small-amplitude candidates over E63 gradient gates, target masks, row gates, caps, and flat/core-gain shapes; selected world/hidden-valid candidates; and actual-anchor scored `2400`.
- Result:
  - toward-teacher candidates: hidden guard `2290/2290`, world guard `2290/2290`, movement guard `2290/2290`, anchor beats `1753/2290`, anchor-margin gates `0`.
  - reverse controls: hidden/world guard `0/110`, anchor beats `106/110`, but best delta only `-0.0000000121`.
  - best toward delta: `-0.000005995`, from `toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120`.
  - target response: `no_q2_s3` best `-5.995e-6`, `no_q2` `-5.090e-6`, `no_s3` `-4.726e-6`, `all` `-4.193e-6`; single-target Q1/S4/Q3 were much weaker and S2 was adverse.
- Interpretation: a real local response pocket exists and is target-conflict shaped, but it remains below public/submission margin. Excluding both Q2 and S3 is consistently best, which echoes earlier S3 conflict and Q2/S-stage instability, but the effect is still not enough to justify a file.
- Decision: add H62/FH57/F48. No submission. The next branch should model Q2/S3 conflict and targetwise calibration, not extend scalar/near-zero line search.

## E66. Q2/S3 Conflict Translator Probe

- Observe: E65's best local pocket excluded Q2 and S3. That exclusion could mean Q2/S3 teacher direction is wrong, or it could mean those targets increase public-anchor tail risk while still being hidden/mean-favorable.
- Wonder: when the same E56 gradient-consensus cell set is held fixed, what exactly happens when Q2 and/or S3 are added back to the `no_q2_s3` pocket?
- Hypothesis: if Q2/S3 are directionally wrong, add-back should worsen hidden-core BCE and mean-anchor contribution. If they are tail-risk targets, add-back may improve hidden/mean terms while worsening robust actual-anchor score.
- Method: `analysis_outputs/q2_s3_conflict_translator_probe.py` generated and scored `3000` focused matched-mask candidates over `all`, `no_q2`, `no_s3`, `no_q2_s3`, `q2`, `s3`, and `q2_s3`. It computed actual-anchor score, targetwise anchor mean contribution, hidden core/all target BCE deltas, and paired same-configuration add-back decompositions versus `no_q2_s3`.
- Result:
  - `no_q2_s3` remained the best robust mask: `432` candidates, `328` anchor beats, best anchor delta `-5.994944e-6`, median `-2.282449e-6`.
  - `no_q2`, `no_s3`, and `all` were weaker but still sometimes favorable: best deltas `-5.090378e-6`, `-4.726393e-6`, and `-4.193235e-6`.
  - Q2/S3-only movement was not robust-anchor useful: `q2` and `q2_s3` had `0` anchor beats, while `s3` had only `2/432`.
  - Matched `all` add-back was robust-anchor adverse in `432/432` configurations, but mean-anchor improved in `288/432`, min-set tail improved in `432/432`, max-set tail worsened in `432/432`, and hidden core improved in `432/432`.
  - Adding only S3 (`no_q2` vs `no_q2_s3`) was adverse in `429/432`; adding only Q2 (`no_s3` vs `no_q2_s3`) was adverse in `432/432`.
- Interpretation: Q2/S3 are not simply wrong hidden targets. They often carry hidden/mean signal, but their add-back expands the public-compatible worst-tail enough to dominate the robust actual-anchor score. Q2 is more directly mean-adverse; S3 can be mean-good but tail-risky.
- Decision: add H63/F49/FH58. No submission. The next branch should build a tail-neutral Q2/S3 translator or variance-aware gate, not keep choosing target masks by scalar line search.

## E67. Tail-Neutral Q2/S3 Translator Probe

- Observe: E66 split Q2/S3 into hidden/mean signal and robust-anchor tail risk. A target mask alone cannot decide that conflict.
- Wonder: can Q2/S3 be added back only where first-order public-anchor scenario tails are neutral, beating the `no_q2_s3` pocket without expanding max-set tail?
- Hypothesis: if Q2/S3 tail risk is locally identifiable, first-order anchor-scenario derivative gates should beat matched `no_q2_s3`, preserve hidden guards, and ideally clear `anchor_delta_vs_mixmin < -1e-5`.
- Method: `analysis_outputs/q2_s3_tail_neutral_translator_probe.py` generated `7632` candidates. Non-Q2/S3 targets kept the E65 move; Q2/S3 used either uniform partial add-back or tail gates (`meanneg`, `p90_nonpos`, `max_nonpos`, soft p90/max) computed from first-order BCE derivative `(mixmin - scenario) * teacher_delta` over the existing anchor scenario/mask family.
- Result:
  - best translator: `tail_meanneg_m1.00`, best anchor delta `-6.93314e-6`, improving E65 `no_q2_s3` best `-5.99494e-6` but still below margin.
  - `tail_p90_nonpos_m1.00`: best `-6.58701e-6`, matched-base beats `432/432`, max-set-tail-neutral matched beats `360/432`.
  - total translators beating matched `no_q2_s3`: `4207/7200`; beating matched base with max-set tail neutral: `2241/7200`.
  - uniform small Q2/S3 add-back mostly failed; full `uniform_q21.00_s31.00` reproduced E66's weaker all-target behavior (`-4.19324e-6` best).
  - anchor-margin gates remained `0`.
- Interpretation: tail-aware Q2/S3 add-back is real and more informative than target masks. But the best edge is still sub-margin and partly derived from the same anchor scenario family used for scoring, so it is not a public submission argument.
- Decision: add H64/F50/FH59. No submission. The next branch should independently validate the tail-gated Q2/S3 cells with hidden/block/row-calibration stress before any candidate file.

## E68. Q2/S3 Tail-Gate Independence Probe

- Observe: E67 improved Q2/S3 add-back, but its gates were constructed from the same known-anchor combo family used for scoring and remained below public-margin scale.
- Wonder: if each combo set is held out from gate construction, do the selected Q2/S3 cells still beat matched `no_q2_s3` and survive non-anchor hidden/world/block stress?
- Hypothesis: if E67 was only same-anchor arithmetic, held-out combo-set wins should disappear and hidden/world/block Q2/S3 diagnostics should not improve. If the cells are real, held-out wins, tail neutrality, hidden Q2/S3 gain, world support, and block-majority Q2/S3 gain should survive together.
- Method: `analysis_outputs/q2_s3_tail_gate_independence_probe.py` selected `180` promising E67 matched configurations, rebuilt Q2/S3 tail gates excluding each held-out combo set, scored `762` unique non-anchor predictions, and formed `540` matched held-out comparisons.
- Result:
  - independent gates: `155/540`; strict independent gates: `155/540`.
  - `tail_soft_max_m1.00`: `44` strict gates, best block win rate `0.944444`, best held-out minus matched base `-6.646495e-7`.
  - `tail_p90_nonpos_m1.00`: `41` strict gates, best strict held-out comparison `-1.260816e-6`, hidden Q2/S3 mean minus base `-0.000109229`, world support minus base `-9.34742e-5`.
  - `tail_max_nonpos_m1.00` had the strongest held-out score (`-1.629588e-6`) but `0` block-majority wins, so it failed the independent gate despite held-out score improvement.
- Interpretation: E67 is not purely a same-anchor derivative artifact. The same Q2/S3 tail-gated cells survive held-out combo construction and independent hidden/world/block checks. But the surviving effect is still `1e-6` scale, so it validates a direction, not a submission.
- Decision: add H65/F51/FH60. No submission. The next branch should either amplify E68 strict cells rowwise while preserving block/tail support, or use them as a latent target/energy in a structural block experiment.

## E69. Q2/S3 Strict-Cell Amplitude Probe

- Observe: E68 strict cells are independently supported, but their held-out deltas are only `1e-6` scale.
- Wonder: can those exact Q2/S3 cells be scaled up into selector-margin movement, or does amplitude expansion recreate E64-style tail/calibration failure?
- Hypothesis: if E68 is merely under-amplified, alpha-scaling the Q2/S3 logit delta from matched `no_q2_s3` base to strict E68 candidate should create full-combo `all_delta_vs_mixmin < -1e-5` while preserving heldout/train/all wins and hidden/world/block support.
- Method: `analysis_outputs/q2_s3_strict_cell_amplitude_probe.py` used `155` E68 strict pairs. Non-Q2/S3 targets stayed fixed at the matched `no_q2_s3` base; only Q2/S3 logit delta was scaled by alpha `[0.0, 0.5, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 24.0]`. It scored heldout combo, train combo, all-combo, hidden, world, and block Q2/S3 stress.
- Result:
  - rows scored: `2170`; unique predictions: `2061`.
  - strict amplitude gates: `0`; full-combo margin gates: `0`.
  - best full-combo delta vs mixmin: `-9.1779e-6` at alpha `24`, still below the `-1e-5` margin.
  - all-beats-base remained broad through alpha `4` (`155/155`) but fell to `137/155` at alpha `8`, `113/155` at alpha `12`, and `51/155` at alpha `24`.
  - heldout tail-neutral counts fell from `155/155` at alpha `1` to `69/155` at alpha `8`, `49/155` at alpha `12`, and `22/155` at alpha `24`; median heldout response turned adverse after alpha `10`.
- Interpretation: E68 strict cells are directionally useful, but simple global alpha is not the missing object. Full-combo improves toward the margin, yet the response plateaus under `1e-5` and tail/heldout stability collapses with larger alpha.
- Decision: add H66/F52/FH61. No submission. Stop global alpha sweeps; next branch must learn rowwise/cellwise amplitude or turn E68 strict cells into a structural target/energy.

## E70. Q2/S3 Strict-Cell Consensus Probe

- Observe: E69 rejected one-pair/global-alpha amplification, but left open a JEPA-style possibility: the individually validated E68 cells may share a common Q2/S3 row/target representation that only appears when cells are aggregated.
- Wonder: do multiple E68 strict cells accumulate into a safer consensus movement that clears selector-scale margin while preserving hidden/world/block/tail diagnostics?
- Hypothesis: if the consensus representation is real, pooled bases and aggregated Q2/S3 deltas should create strict rows with all-combo margin, all combo sets beating base, all set tails non-worse, and non-anchor hidden/world/block support.
- Method: `analysis_outputs/q2_s3_strict_cell_consensus_probe.py` rebuilt the `155` E68 strict cells, aggregated matched `no_q2_s3` bases and Q2/S3 logit deltas across all/heldout/translator/top-ranked pools, tested mean/median/weighted/signed-p75 delta aggregators, agreement gates, and alpha response, then scored combo proxy first and hidden/world/block stress on the `700` most promising rows.
- Result:
  - candidate rows: `2688`; unique predictions: `2576`; summary rows: `384`.
  - strict consensus gates: `6`; loose consensus gates: `502`.
  - best all-combo delta vs mixmin: `-0.0000102775`.
  - all strict rows used `gate=none`; none of the sign-agreement gates produced strict margin rows.
  - strict rows came from `translator_tail_soft_max_m1.00`, `top100_heldout`, `translator_tail_soft_p90_m1.00`, and the full `all` pool.
  - strict rows had `3/3` combo sets beating base and tail-neutral, hidden Q2/S3 mean improvements around `-0.000411` to `-0.000542`, world support improvements around `-0.000403` to `-0.000490`, block win rates `0.888889-0.916667`, and raw-energy non-worsening.
- Interpretation: consensus accumulation is a real local structural signal, not a dead branch. But it is not yet a submission rule: the margin is tiny, all strict rows are disagreement-permissive (`gate=none`), and the construction still depends on heldout-specific E68 strict cells.
- Decision: add H67/F53/FH62. No submission. Next work should convert E70 into a unified non-heldout rule or LeJEPA-style consensus energy before producing a file.

## E71. Unified Q2/S3 Strict-Cell Consensus Probe

- Observe: E70 crossed local margin, but the result could still be heldout-specific because E68 strict cells were reconstructed per heldout family and all strict rows used `gate=none`.
- Wonder: does the consensus survive if each unique strict cell is rebuilt exactly once with the full combo family, and can any conservative non-`none` gate reproduce the margin?
- Hypothesis: if E70 captured a deployable representation, unified-cell reconstruction should keep margin while opening at least one `deployable_unified_gate = strict_unified_gate & gate != none`.
- Method: `analysis_outputs/q2_s3_unified_strict_cell_consensus_probe.py` used E68 strict rows only to select unique cells (`155` strict rows, `104` unique cells, `51` support-2 cells), rebuilt those cells with full combo tables, aggregated pooled base/delta views, and scored the same tail/hidden/world/block requirements as E70. It wrote scan, summary, and report files but no submission.
- Result:
  - candidate rows: `3136`; unique predictions: `2842`; summary rows: `448`.
  - strict unified gates: `1`; deployable unified gates: `0`; loose unified gates: `475`.
  - best all-combo delta vs mixmin: `-0.0000108217`.
  - the only strict row used `top75_heldout_mean`, mean base, `signed_p75` delta, `gate=none`, and alpha `8`.
  - that strict row kept `3/3` combo sets beating base and tail-neutral, hidden Q2/S3 mean improvement `-0.000477907`, world support improvement `-0.000413602`, and block win rate `0.833333`.
- Interpretation: unified consensus is not purely heldout-specific arithmetic, because one strict row and many loose rows survive full reconstruction. But it is still not a submission rule: deployable gates are `0`, margin rows remain disagreement-permissive, and conservative agreement geometry has not learned the latent.
- Decision: add H68/F54/FH63. No submission. Treat unified consensus as diagnostic energy; the next branch must explain or repair the `gate=none` dependence with rowwise/cellwise amplitude, non-`none` agreement, or a structural block target.

## E72. Unified Q2/S3 Gate Geometry Probe

- Observe: E71's only strict unified row still used `gate=none`, but the tested non-`none` gates were mostly hard sign-agreement gates.
- Wonder: is the failure really absence of deployable gate geometry, or just the wrong gate family?
- Hypothesis: if sparse magnitude or target-specific consensus is the missing geometry, `top_abs50` or target-only gates should produce strict deployable rows. If not, every non-`none` gate should remain sub-margin or fail tail/hidden/world/block stress.
- Method: `analysis_outputs/q2_s3_unified_gate_geometry_probe.py` rebuilt the E71 unified cells, restricted to the most relevant pools, and swept `11` gate modes over alpha `[2,4,8,12,16,24]`: `none`, `top_abs50`, `top_abs30`, `agree55`, soft signed/agreement gates, `q2_only`, `s3_only`, and target agreement gates. It scored combo proxy, then hidden/world/block stress for the selected rows.
- Result:
  - candidate rows: `4752`; unique predictions: `4752`.
  - strict gates: `21`; deployable non-`none` gates: `10`; loose gates: `655`.
  - `top_abs50` produced `7` deployable rows and best deployable all-combo delta `-1.05458e-5`.
  - `s3_only` produced `3` deployable rows, while `q2_only` and `q2_agree55` produced `0` loose rows.
  - soft/agree55 gates produced loose rows but no strict deployable rows.
- Interpretation: E71's "no deployable gate" conclusion was too broad. The missing object is not generic sign agreement; it is sparse-magnitude consensus, plus a secondary S3-only path. Q2-only remains dead. The best candidate is small-margin but now has a real non-`none` gate.
- Decision: add H69/F55/FH64. Materialize the best deployable `top_abs50` row as a diagnostic submission candidate, not as a confirmed replacement.

## E73. E72 TopAbs50 Candidate Materialization

- Observe: E72 opened `10` deployable rows but did not write a submission.
- Wonder: which single file is the highest-information public sensor?
- Method: `analysis_outputs/q2_s3_unified_gate_candidate.py` selected the best E72 deployable row by all-combo delta, worst-set delta, and movement size, regenerated the exact prediction from the unified cells, and wrote `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`.
- Result:
  - selected tag: `e72_translator_tail_soft_p90_m0.50_top_abs50_16.00_4e48cba2`.
  - local all-combo delta vs mixmin: `-1.05458e-5`; all-minus-base `-5.78026e-6`.
  - all `3/3` combo sets beat base and were tail-neutral.
  - hidden Q2/S3 mean minus base `-0.000391043`, world support minus base `-0.000280957`, raw-energy q-p90 minus base `-0.000159091`, block win rate `0.722222`, block tail-safe `1.0`.
  - submission file shape matches mixmin (`250 x 10`), no NaNs, probability range `0.069003-0.979520`.
- Interpretation: this is the first post-mixmin Q2/S3 consensus candidate with a non-`none` deployable gate. It is still a diagnostic because worst-set delta vs mixmin is positive and the edge is around the selector margin.
- Decision: candidate priority 1 if one public observation is used next. If it improves LB, sparse-magnitude Q2/S3 consensus becomes public-relevant. If it worsens, E72 remains a local stress artifact and future work must require stronger public-subset or structural block-state evidence.

## E74. Sparse Q2/S3 Gate Stability Probe And Alpha20 Materialization

- Observe: E73's candidate came from only `13` source cells, so it could still be a few-cell artifact even though it passed the non-`none` deployable gate.
- Wonder: is sparse-magnitude Q2/S3 consensus a stable latent cell family, or did E73 win because a small number of cells happened to match the local combo proxy?
- Method: `analysis_outputs/q2_s3_sparse_gate_stability_probe.py` rebuilt the E73 full-pool candidate, then stressed it with leave-one-cell-out jackknife, group-keep subsets, rank-keep subsets, and `60` deterministic bootstrap `8/13` subsets across alpha `[8, 12, 16, 20, 24]`. It wrote `analysis_outputs/q2_s3_sparse_gate_stability_probe_scan.csv`, summary, and report. `analysis_outputs/q2_s3_sparse_gate_stability_candidate.py` then materialized the clean reference/full-pool alpha20 row as `analysis_outputs/submission_e74_fullpool_a20_q2s3_gate_55455b60.csv`.
- Result:
  - total rows `470`, variants `94`, strict/deployable `141`, loose `470`.
  - reference alpha16 reproduces E73: tag `e74_full_pool_16.00_4e48cba2`, all delta `-1.05458e-5`.
  - reference alpha20 remains strict/deployable and improves the local all-combo delta to `-1.07261e-5`, hidden Q2/S3 mean to `-0.000484506`, and world support to `-0.000351115`.
  - jackknife alpha16 deployable `13/13`; jackknife best all delta `-1.07697e-5`.
  - bootstrap8 alpha16 deployable `48/60`; bootstrap8 best all delta `-1.08084e-5`.
  - alpha24 fails strict on the reference row, so alpha20 is an amplitude-risk ridge, not an unlimited scale signal.
- Interpretation: the E73 sparse gate is not single-cell fragile. The local structure survives cell deletion and random subset stress, which strengthens H69. The new E74 alpha20 file is a cleaner amplitude diagnostic than bootstrap variants because it keeps the exact full 13-cell source pool and changes only alpha from `16` to `20`.
- Decision: at the time, keep E73 as the first public sensor if only one slot is used and treat `submission_e74_fullpool_a20_q2s3_gate_55455b60.csv` as a secondary amplitude sensor. This ordering was later superseded by E80/E81 after E73 public LB worsened and pure Q2/S3 split proved sub-margin.

## E75. Q2/S3 Target-Specific Amplitude Ridge Probe And Q2-Low/S3-High Candidate

- Observe: E74 showed the sparse gate is cell-subset stable, but the symmetric amplitude story was ambiguous: alpha20 improved locally, alpha24 failed strict consensus, and E72 had already hinted that `s3_only` survives while Q2-only does not.
- Wonder: is the safe amplitude ridge symmetric across Q2 and S3, or is public-readable movement S3-heavy while Q2 should be shrunk?
- Method: `analysis_outputs/q2_s3_target_amplitude_ridge_probe.py` fixed the E74 pool (`translator_tail_soft_p90_m0.50`), base/delta aggregation (`mean` / `signed_p75`), and gate (`top_abs50`), then crossed target-specific `alpha_q2` and `alpha_s3` over `[0, 8, 12, 16, 18, 20, 22, 24, 26, 28, 32]`. `analysis_outputs/q2_s3_target_amplitude_ridge_candidate.py` materialized the best deployable row.
- Result:
  - scan rows `120`; strict/deployable `37`; loose `109`.
  - reference E73-equivalent `alpha16/16`: all delta `-1.05458e-5`, hidden Q2/S3 `-0.000391043`, world `-0.000280957`.
  - reference E74-equivalent `alpha20/20`: all delta `-1.07261e-5`, hidden Q2/S3 `-0.000484506`, world `-0.000351115`.
  - axis summary: `s3_higher` has `23` strict/deployable rows and best all delta `-1.23676e-5`; `s3_only` has `6`; `q2_higher` has `5`; `equal` has `3`; `q2_only` has `0`.
  - best deployable row: `e75_q2a8.0_s3a28.0_f07219b4`, all delta `-1.23676e-5`, all-minus-base `-7.60210e-6`, hidden Q2/S3 `-0.000372692`, hidden Q2 `-0.000247148`, hidden S3 `-0.000498235`, world `-0.000200351`, block win `0.722222`, strict/deployable true.
  - materialized file: `analysis_outputs/submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv`.
- Interpretation: target-specific amplitude is live. Symmetric alpha20 is not locally optimal under the current public-combo proxy. The ridge is asymmetric: Q2-only is dead, while S3-heavy amplitudes dominate the deployable frontier. The tradeoff is that E75 is a sharper and more aggressive public sensor than E73, with weaker hidden/world support than E74 on Q2 but stronger public-combo edge.
- Decision: add H71/F57/FH66. Keep E73 as the first sparse-gate public sensor because it tests the sign with lower amplitude risk. Promote E75 above E74 as the sharper second sensor if the next slot is meant to test target-asymmetric amplitude; keep E74 as the symmetric amplitude control.

## E76. Q2/S3 Target-Amplitude Stability Probe

- Observe: E75 found a better local full-pool row by shrinking Q2 to alpha `8` and amplifying S3 to alpha `28`, but that could still be a full-pool/local-combo artifact rather than a stable target-asymmetric law.
- Wonder: does the S3-heavy/Q2-low amplitude direction survive the same source-cell deletion and subset stress that made E73 credible, or should E75 be treated as a sharp but fragile local row?
- Method: `analysis_outputs/q2_s3_target_amplitude_stability_probe.py` reused the E74/E75 source pool (`translator_tail_soft_p90_m0.50`, `13` cells), `top_abs50` gate, `mean` base, and `signed_p75` delta. It rebuilt `94` variants across reference, jackknife, group-keep, rank-keep, and deterministic bootstrap8 subsets, then scored `21` target-alpha pairs including E73 `16/16`, E74 `20/20`, E75 `8/28`, S3-heavy rows, and S3-only rows. It wrote scan, summary, pair-comparison, and report files; no submission was materialized.
- Result:
  - total rows `1974`, variants `94`, strict/deployable `1138`, loose `1894`.
  - exact `asym8_28_e75` beats both `sym16_e73` and `sym20_e74` on all-combo delta in `94/94` variants.
  - exact `asym8_28_e75` is deployable in only `49/94` variants: reference `1/1`, jackknife `8/13`, group_keep `7/10`, rank_keep `5/10`, bootstrap8 `28/60`.
  - best deployable axis is S3-heavy in `94/94` variants; equal and S3-only are never the best deployable axis in the summary.
  - bootstrap8 median `asym8_28` all delta is `-1.21716e-5`, worst is `-1.13436e-5`, and best deployable all delta is `-1.26757e-5`.
  - jackknife `asym8_28` beats symmetric controls in `13/13`, but exact deployability is `8/13`, while E74 previously showed E73 alpha16 jackknife deployability `13/13`.
- Interpretation: target asymmetry is much more stable than the exact E75 amplitude. The direction "S3 should carry more amplitude than Q2" survives every subset variant, but the exact `q2=8/s3=28` row is not as broad as E73's alpha16 sparse-gate sign. This strengthens H71 as a direction, weakens any claim that E75 is lower-risk than E73, and makes E74 a useful symmetric control rather than the preferred second sensor by default.
- Decision: add H72/F58/FH67. Keep E73 as the first sparse-gate public sign sensor. E75 remains the sharper second public sensor only if the explicit question is target-asymmetric amplitude; E74 remains the safer symmetric amplitude control if exact-amplitude stability matters more than upside. The next non-public experiment should condition target-specific amplitude on row/cell energy instead of treating `8/28` as universal.

## E77. Q2/S3 Amplitude Posterior Aggregation Probe

- Observe: E76 says S3-heavy direction survives subset stress, but exact `8/28` deployability is partial. A natural JEPA-style next question is whether the source-subset prediction distribution itself can act as an amplitude posterior.
- Wonder: can aggregating E76 subset predictions reduce exact-alpha fragility while preserving local margin, tail neutrality, hidden Q2/S3 support, world support, and block stress?
- Method: `analysis_outputs/q2_s3_amplitude_posterior_probe.py` rebuilt E76 predictions, formed `19` selector groups from exact asym rows, best deployable rows per variant, all S3-heavy deployable rows, and dynamically stable alpha pairs. It generated logit-space posterior movements from `mixmin`, E73, and E74 using aggregators `mean`, `median`, `signed_p60`, `signed_p75`, `signed_p90`, scopes `q2s3`, `s3_only`, `full`, and shrink values `[0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5]`.
- Result:
  - candidate rows `6840`; strict/deployable `0`; loose `3099`; deployable rows beating E75 local all-combo `0`; all rows beating E75 local all-combo `62`.
  - best all-combo row: `exact_asym_all + e74 + signed_p90 + q2s3 + shrink 0.75`, all delta `-1.26541e-5`, but hidden Q2/S3 `+3.95652e-5`, world `+0.000107171`, and block win `0.555556`, so it is not even loose.
  - best mixmin/q2s3 posterior: all delta only `-8.09547e-6`, but it is broad and safe-looking: loose `688/760`, best worst-set `-2.16163e-6`, hidden Q2/S3 `-0.001203`, world `-0.000779`, block win `0.833333`.
  - increasing mixmin/q2s3 shrink does not open margin: best all delta stalls near `-8e-6`, while worst-set turns positive after shrink `1.50`.
  - mixmin/full posterior can beat E75 local all-combo, with best `-1.25991e-5`, hidden `-0.001203`, world `-0.004756`, and block `0.833333`, but the best rows beat only `1/3` combo sets and keep only `1/3` tail-neutral sets.
- Interpretation: posterior aggregation is not the missing amplitude fix. It cleanly separates two incompatible objects: Q2/S3-only posterior movement is calibrated and stress-friendly but sub-margin, while full posterior movement creates local margin but breaks combo-set/tail consistency. The bottleneck is now set-specific/tail-aware amplitude localization, not universal source-subset posterior averaging.
- Decision: add H73/F59/FH68. Do not materialize an E77 submission. Future amplitude work should condition on combo-set/tail risk or row/block topology, not just average E76 variants.

## E78. Q2/S3 Localized Amplitude Gate Probe

- Observe: E77 rejected generic posterior averaging. The next sharper hypothesis was whether E76 deployable/non-deployable source-subset distributions can become row/target reliability gates over E75's sparse unit movement.
- Wonder: can we shrink Q2 or unstable cells while preserving S3-heavy signal and beat E75 without breaking combo-tail/hidden/world/block stress?
- Method: `analysis_outputs/q2_s3_localized_amplitude_gate_probe.py` used E75 full-pool `translator_tail_soft_p90_m0.50` / `top_abs50` unit delta, built 36 reliability masks from E76 exact/all/deployable/S3-heavy/deployable-vs-failed source stacks, localized both/Q2-only/S3-only, crossed Q2 alphas `[0, 4, 8, 12, 16, 20]` with S3 alphas `[16, 20, 24, 28, 32, 36, 40]`, and scored `4452` rows with the same E76 stress gate.
- Result:
  - rows `4452`; strict/deployable `1806`; loose `3934`; deployable rows beating E75 local all-combo `0`; best all `-1.23676e-5`.
  - best rows are E75-equivalent `q2=8/s3=28`; consensus masks from exact/deployable/S3-heavy/all-deployable mostly collapse to identity over E75 active cells.
  - strong sign masks keep deployability but lower edge, e.g. `s3_deployable hard_sign_0.90 s3_local_q2_full` strict/deployable `21`, best `-1.16605e-5`.
  - deployable-vs-failed excess/veto masks are sparse and shrink movement too much.
- Interpretation: source-subset reliability gating does not reveal a better row/cell law than E75 `top_abs50`. Exact E75 remains the local best; localization can create safer-looking variants but not more informative submission candidates.
- Decision: add H74/F60/FH69. No E78 submission. At the time, keep E73 as first public sign sensor, E75 as target-asymmetry sensor, and E74 as symmetric control; this direct order was later superseded by E80-E82. Next amplitude localization needs richer public-like row/block/tail structure or public feedback.

## E79. Public-Like Row/Block Q2/S3 Amplitude Probe

- Observe: E78 killed E76 source-subset reliability masks, but the data are not iid rows. Submission rows occur inside subject-calendar runs bracketed by train rows, so row position, flanking train labels, subject priors, and sparse-unit energy remain plausible JEPA context for public-like amplitude.
- Wonder: is E75's `q2=8/s3=28` amplitude valid only on a public-like row/block/flank subset rather than all sparse active cells?
- Method: `analysis_outputs/q2_s3_public_like_rowblock_amplitude_probe.py` reused the E75 full-pool `translator_tail_soft_p90_m0.50` / `top_abs50` unit delta, built `61` masks from topology, topology x positive unit-energy, subject priors, subject ids, nearest train-label flanks, and target-specific Q2/S3 flank gates, then crossed Q2 alphas `[0, 4, 8, 12, 16, 20]` with S3 alphas `[16, 20, 24, 28, 32, 36]`.
- Result:
  - rows `6516`; masks `61`; strict/deployable `1318`; loose `3403`.
  - deployable rows beating E75 local all-combo: `0`; best all equals E75 at `-1.23676e-5`.
  - E75 sparse movement is active on only `72/250` submission rows/cells; positive-energy `top30` cuts this to `22` active rows and `top50` to `36`, but neither improves the deployable frontier.
  - best non-identity row/block/flank masks (`s3_high`, `block_inner`, `block_first_half`, `subject_late_half`, subject-prior/flank target masks) stay deployable but all lose edge versus E75.
- Interpretation: row/block/flank topology is real observation context, but it does not repair E75 amplitude under current stress. The local optimum is still the full active sparse `top_abs50` cell set with asymmetric amplitude, not a simple public-like row subset.
- Decision: add H75/F61/FH70. No E79 submission. At the time the public test order stayed E73 first, E75 target-asymmetry second, and E74 symmetric control; E80/E81 later superseded that order and paused all direct E74/E75 follow-ups. Future localization must use combo-set/tail calibration or a learned structural target, not handcrafted row/block/flank masks alone.

## E80. E73 Public Observation Assimilation

- Observe: `submission_e72_topabs50_q2s3_gate_4e48cba2.csv` was submitted and scored public LB `0.5764077772`, worse than mixmin `0.5763066405`.
- Wonder: did public reject the sparse Q2/S3 latent itself, or did the submitted file contain another movement that contaminated the sensor?
- Method: `analysis_outputs/e73_public_observation_assimilation.py` compared E73 against mixmin, decomposed moved cells by target group, and translated the public delta into loss-support constraints.
- Result:
  - public delta vs mixmin: `+0.0001011367`.
  - local all-combo expected delta: `-0.0000105458`; public/local edge ratio `9.590x` with opposite sign.
  - E73 moved `893` cells on `249` rows across `Q1,Q2,Q3,S1,S2,S3,S4`.
  - isolated Q2/S3 movement accounts for only `79` moved cells; non-Q2/S3 movement accounts for `814`.
- Interpretation: the submitted file was not a pure Q2/S3 sign test. The public result rejects the combined E72 base plus sparse Q2/S3 file, not isolated Q2/S3 by itself.
- Decision: demote E73 as a public-aligned candidate and pause E74/E75 direct follow-ups until the Q2/S3 movement is separated from the broad base movement.

## E81. Pure E73 Q2/S3 Graft Split

- Observe: E80 made E73's public failure underidentified because the file moved all target families.
- Wonder: if only E73's Q2/S3 cells are grafted onto mixmin, does the local stress still justify a public sensor? Conversely, does public failure justify sign inversion?
- Method: `analysis_outputs/e73_pure_q2s3_graft_probe.py` scored eight mixmin-anchored variants: E73 full, pure Q2/S3, Q2-only, S3-only, non-Q2/S3-only, and inverse Q2/S3/Q2/S3 public-sensor controls.
- Result:
  - strict/deployable rows: `0`; loose rows: `3`.
  - E73 full remains loose with local all delta `-0.0000105458`, but it is not deployable because only `1/3` combo sets beat base and only `1/3` tails are neutral.
  - pure Q2/S3 graft is loose but sub-margin: all delta `-0.000005954`, `3/3` combo sets beat base, `3/3` tails neutral, hidden Q2/S3 `-0.000391043`, world `-0.000281016`.
  - pure S3-only is similarly loose/sub-margin at `-0.000005665`; Q2-only is too small at `-0.000000439`.
  - inverse Q2/S3 is locally adverse: all delta `+0.000014747`, combo-set wins `0`, hidden/world/block all worsen.
- Interpretation: isolated Q2/S3 direction is not dead, but it is not submission-scale. Public-sign inversion is rejected as a reaction to one LB miss. The useful signal is now a sub-margin latent energy, not a next file.
- Decision: add H76/F62/FH71/FH72. No E81 submission. The next submission should require a new combo-set/tail-calibrated or structural block target gate rather than E74/E75 amplification.

## E82. Pure Q2/S3 Source-Graft Scan

- Observe: E81 only tested the submitted E73 final-file Q2/S3 values. The broader E72/E75/E76 source universe still contained target-specific and subset-stable Q2/S3 movements that might become cleaner after removing non-Q2/S3 base movement.
- Wonder: if every E72/E75/E76 source row is grafted onto mixmin using only Q2/S3, Q2-only, or S3-only value/delta movement, does any row become margin-scale while preserving combo-set, tail, hidden, world, and block stress?
- Method: `analysis_outputs/e82_pure_q2s3_source_graft_scan.py` reconstructed E72 adaptive rows, E75 target-ridge rows, and E76 subset-stability rows; built value-graft and source-base delta-graft variants anchored to mixmin; combo-scored `8402` rows; and ran non-anchor stress on the `700` combo-promising rows.
- Result:
  - rows `8402`; non-anchor evaluated `700`; strict/deployable `0`; loose `700`.
  - best evaluated all delta `-0.00000790328`, below the `-1e-5` margin gate.
  - every evaluated row passed the non-margin pieces: all beats base `700/700`, all combo sets beat base `700/700`, all tails neutral `700/700`, hidden Q2/S3 improves `700/700`, world nonworse `700/700`, block majority beats `700/700`, block tail safe `700/700`.
  - best rows came from E76 bootstrap/jackknife `asym8_28_e75` and `q2a12_s3a28` Q2/S3 grafts; Q2-only and S3-only did not enter non-anchor stress.
- Interpretation: E82 is a clean margin bottleneck. Removing broad base contamination preserves the Q2/S3 direction and tail safety, but it also caps the edge below submission scale. The missing object is not another pure Q2/S3 gate; it is either a broader structural target that uses Q2/S3 as energy, or a new block-state representation that creates larger calibrated movement without E73's all-target contamination.
- Decision: add H77/F63/FH73. No E82 submission. Pure Q2/S3 source grafts should now be demoted from candidate-generator to latent energy unless public feedback later proves a sub-margin pure move valuable.

## E83. Q2/S3-Energy Structural Gate Scan

- Observe: E82 made Q2/S3 a coherent but sub-margin latent. Older broad JEPA/block/raw submissions still contain larger movement, but direct broad movement has been unsafe.
- Wonder: can E82 Q2/S3 row energy select rows where those broader structural movements become safe relative to mixmin?
- Method: `analysis_outputs/e83_q2s3_energy_structural_gate_scan.py` built E82 top-20 Q2/S3 energy, loaded compact-selected broad structural submissions, and applied their logit deltas to mixmin across row gates, target scopes, and scales.
- Result:
  - rows `3716`; non-anchor evaluated `700`; strict/deployable `0`; loose `40`; structural-loose `189`.
  - best evaluated all delta `-0.0000350517`, but the best broad rows beat only `2/3` combo sets and worsened Q2/S3 hidden/world (`hidden_q2s3` about `+0.000443`, world about `+0.000252`).
  - E72-derived Q2/S3-safe rows passed E70 loose with `3/3` sets and tails, but stayed sub-margin around `-0.00000894`.
  - non-Q2/S3 structural rows reached margin-scale deltas around `-0.0000253` and improved hidden-core/world, but by construction carried no Q2/S3 safety signal and beat only `2/3` combo sets.
- Interpretation: E83 splits the plateau into two separable-looking pieces: structural margin exists outside Q2/S3, and Q2/S3 safety exists inside E72, but no single E83 row carries both plus all combo-set coverage.
- Decision: add H78/F64/FH74. No deployable E83 submission. Recombine non-Q2/S3 structural margin with Q2/S3 safety before trying another learned representation.

## E84. Structural Margin + Q2/S3 Safety Recombination

- Observe: E83's strongest failure was not absence of signal; it was target-group conflict. The natural falsification is to add structural non-Q2/S3 movement and Q2/S3-only safety movement in the same candidate.
- Wonder: is the conflict additive by target group, or does one public-observation combo set reject the whole structural direction?
- Method: `analysis_outputs/e84_structural_margin_q2s3_safety_recombination.py` selected E83 structural-loose `non_q2s3` rows and E72-derived Q2/S3-safe rows, combined structural deltas outside Q2/S3 with only the Q2/S3 components from the safety rows, and swept conservative weights.
- Result:
  - rows `1728`; non-anchor evaluated `700`; strict/deployable `0`; loose `700`; structural-loose `700`.
  - best evaluated all delta `-0.0000321500`.
  - all evaluated rows passed margin, all-beats-base, hidden Q2/S3, world, block-majority, and block-tail guards; `672/700` also passed raw-energy.
  - strict failed only because every evaluated row beat `2/3` combo sets and kept `2/3` tails neutral. The rejecting set is `inverse_top`: `0/700` wins, with mean inverse-top minus-base `+0.0000859`; raw05-compatible and all-sign sets were `700/700` favorable.
- Interpretation: additive target-group recombination solves Q2/S3 safety but not the public-observation split. The current bottleneck is now a specific combo-set/anchor-world conflict, not model capacity or missing Q2/S3 direction.
- Decision: add H79/F65/FH75. No deployable E84 submission. Materialized only a diagnostic sensor, `analysis_outputs/submission_e84_inverse_sensor_1c74da00.csv`, to test whether public behaves like the inverse-top set that rejects every otherwise healthy E84 candidate.

## E85. Inverse-Top Conflict Target-Prune

- Observe: E84 localized the remaining failure to the `inverse_top` combo set, but not whether the rejection was row/block-specific or target-axis-specific.
- Wonder: can the inverse-top conflict be solved by pruning harmful target axes from the same E84 movement before learning a row/block gate?
- Method: `analysis_outputs/e85_inverse_conflict_target_prune.py` took the top E84 loose/structural rows, applied every non-empty target subset of their mixmin-relative logit movement, and rescored the resulting predictions with the same all-combo, inverse-top, raw05-compatible, all-sign, hidden/world/block, tail, and movement diagnostics.
- Result:
  - scan rows `10135`; non-anchor evaluated `700`; strict `535`; deployable `535`; loose `588`.
  - E84 target contribution under inverse-top was adverse on `Q3` (`+6.36482e-05`), `Q1` (`+2.14071e-05`), `S4` (`+1.44236e-05`), and `S2` (`+1.21695e-05`), while favorable on `S3` (`-1.93327e-05`) and nearly neutral on `S1`/`Q2`.
  - Strong target masks were `S1,S2,S3` and `Q2,S1,S2,S3`; both produced `80/80` evaluated strict/deployable rows. Q2 is effectively unchanged, so the material movement is `S1,S2,S3`.
  - best materialized file: `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv`, keeping `S1,S2,S3` and removing `Q1,Q2,Q3,S4` movement.
  - best file stress: all delta `-2.38758e-05`; inverse-top delta `-8.16658e-06`; raw05-compatible delta `-2.95552e-05`; all-sign delta `-3.39057e-05`; hidden core `-0.000161301`; hidden Q2/S3 `-0.000216060`; world `-0.000130361`; raw energy `-3.52006e-05`; block win `0.666667`; block tail safe `0.944444`.
- Interpretation: the first-order conflict is target-axis contamination, not necessarily row/block conflict. E84's Q1/Q3/S4 movement was public-world-adverse under inverse-top; the surviving structural movement lives mainly on S1/S2/S3.
- Decision: add H80/F66/FH76. Promote `analysis_outputs/submission_e85_inverse_conflict_pruned_58b23ed1.csv` as the highest-information next public candidate. If public improves, inverse-top pruning is a real public-world correction. If public worsens, public is closer to the raw05/all-sign target movement and inverse-top was over-conservative.

## E86. E85 Target-Prune Source-Consensus Robustness

- Observe: E85 produced a strong strict/deployable file, but the remaining public risk was whether the chosen row was one source/seed artifact.
- Wonder: does the S1/S2/S3 target-prune law survive source-diverse logit consensus and small shrink/overstep stress?
- Method: `analysis_outputs/e86_e85_target_prune_robustness.py` rebuilt E85 predictions, selected strict E85 rows by target mask, and generated logit-delta consensus variants using top rows, distinct source-file rows, and distinct seed-rank rows. Aggregators were mean/median/trimmed mean, with shrink values `0.75, 0.90, 1.00, 1.10, 1.25`.
- Result:
  - E85 source stability: `S1,S2,S3`, `Q2,S1,S2,S3`, `Q2,S1,S3,S4`, `S1,S3,S4`, `Q2,S1,S3`, and `S1,S3` each had `80/80` strict rows across `18` unique source files and `80` seed ranks. Source families were `gate`, `rawcorr_micro`, and `rawcorr_refine`.
  - E86 consensus rows: `1485`; non-anchor evaluated `700`; strict `700`; deployable `700`; loose `700`.
  - best evaluated all delta `-2.77059e-5`, stronger than E85's `-2.38758e-5`.
  - materialized file: `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv`.
  - selected row keeps `Q2,S1,S2,S3`, averages top `40` strict E85 rows from `18` source files, uses mean aggregation and shrink `1.25`.
  - selected row stress: all delta `-2.77059e-5`; inverse-top `-6.91e-6`; raw05-compatible `-3.53387e-5`; all-sign `-4.08689e-5`; hidden core `-0.000239181`; hidden Q2/S3 `-0.000377585`; world `-0.000307439`; raw-energy `-0.000172786`; block win `0.833333`; block-tail safe `1.0`.
- Interpretation: the target-pruned structural law is source-stable, not a one-row accident. E86 also shows mild overstep can improve local margin without breaking inverse-top or block/tail stress. The new risk is different: E86 is a stronger consensus/overstep bet than E85, so public could prefer E85's lower-amplitude S1/S2/S3-only correction.
- Decision: add H81/F67. Promote `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv` as the highest-upside next public candidate. Keep E85 as the conservative same-hypothesis sensor.

## E87. E86 Risk Decomposition Contrast Sensors

- Observe: E86 is locally stronger than E85, but it entangles three public risks: Q2 add-back, shrink `1.25` overstep, and choice of all-delta geometry over inverse-top-prior geometry.
- Wonder: if E86 misses public, which belief should die first: Q2 add-back, overstep amplitude, or the inverse-top target-prune worldview itself?
- Method: `analysis_outputs/e87_e86_risk_decomposition.py` rebuilt the deterministic E86 consensus pool and selected three contrast submissions under the same strict/deployable E86 stress: no-Q2 source-diverse consensus, Q2 with no overstep, and inverse-top-prior consensus.
- Result:
  - scan rows `1485`; strict/deployable candidate universe `700`.
  - E86 reference: `analysis_outputs/submission_e86_e85_consensus_a3f7c96f.csv`, `Q2,S1,S2,S3`, shrink `1.25`, all delta `-2.77059e-5`, inverse-top delta `-6.91e-6`, hidden Q2/S3 `-0.000377585`, world `-0.000307439`.
  - no-Q2 contrast: `analysis_outputs/submission_e87_noq2_source_consensus_a85c4e39.csv`, `S1,S2,S3`, shrink `1.25`, all delta `-2.69461e-5`, inverse-top `-7.28932e-6`, hidden Q2/S3 `-0.000254206`, world `-0.000171638`.
  - no-overstep contrast: `analysis_outputs/submission_e87_q2_nooverstep_consensus_acd7add0.csv`, `Q2,S1,S2,S3`, shrink `1.00`, all delta `-2.42545e-5`, inverse-top `-7.53196e-6`, hidden Q2/S3 `-0.000305292`, world `-0.000248837`.
  - inverse-top-prior contrast: `analysis_outputs/submission_e87_inverse_top_prior_consensus_5445ec28.csv`, `Q2,S1,S3`, shrink `1.25`, all delta `-1.88862e-5`, inverse-top `-2.06434e-5`, hidden Q2/S3 `-0.000376122`, world `-0.000443423`.
- Interpretation: E87 does not supersede E86. It creates a public-response decision tree. If E86 fails but no-Q2 improves, Q2 add-back was the contaminant. If no-overstep improves, shrink `1.25` was the overfit. If inverse-top-prior improves, public is closer to inverse-top geometry than all-delta geometry.
- Decision: add H82/F68 and track E87 as contrast sensors only. Do not rank E87 above E86 before public feedback.

## E88. Frontier Movement Attribution After E72 Public Miss

- Observe: E72 public LB was `0.5764077772`, worse than mixmin by `+0.0001011367`. E86/E87 are locally healthy, but the open question is whether their movement is a clean target-prune correction or whether it lies near the same failed E72 movement manifold.
- Wonder: do E85/E86/E87 move the same hidden cells/rows as the public-positive mixmin jump, or do they mostly rollback mixmin along an E72-contaminated axis?
- Method: `analysis_outputs/e88_frontier_movement_attribution.py` compared mixmin-vs-a2c8, E72-vs-mixmin, E85/E86/E87-vs-mixmin in logit space. It measured high-mixmin cell mass, high-E72 cell mass, signed cell correlations, row-move correlations, subject-prior CE proxies, raw-domain/order/calendar context concentrations, and two derived energies: `e72_failed_contamination_index` and `mixmin_reversal_index`.
- Result:
  - E86 has mean abs logit move `0.006064`, high-E72 failed cell mass `0.443457`, E72 overlap ratio `0.819288`, E72 contamination index `0.772379`, and row correlation with the E72 failed row move `0.725471`.
  - E86 has signed cell correlation `-0.758417` with the original mixmin-vs-a2c8 movement, so it is a second-order rollback/refinement of mixmin rather than continuation of mixmin's first-order public-positive movement.
  - no-Q2 E87 is the cleanest contrast by this lens: contamination index `0.730408` versus E86 `0.772379`, with all-delta still near E86 (`-2.69461e-5` local stress from E87).
  - no-overstep E87 lowers amplitude but has the same moved-cell geometry as E86, so it tests scale, not contamination.
  - inverse-top-prior E87 has the worst E72 proximity: contamination index `0.928415` and high-E72 cell mass `0.602577`, so it is a high-information diagnostic, not a safety fallback.
- Interpretation: E86 remains the highest-upside public sensor because E86 local stress is strongest, but E88 makes its public downside more explicit. The candidate is not simply a safe continuation of mixmin; it is a target-pruned rollback that overlaps the known failed E72 manifold. If E86 misses public, the first contrast to read is no-Q2, not inverse-top-prior.
- Decision: add H83/F69/FH78. Keep E86 as the next information-rich sensor if not yet submitted, but annotate it as E72-contamination-proximate. Demote inverse-top-prior from "possibly safer" to "diagnostic only."

## E89. E86/E72 Decontamination Scan

- Observe: E88 did not kill E86, but it made the hidden risk precise: E86's local edge is strong while its E72-contamination index is `0.772379`.
- Wonder: can we remove only the E72-contaminated part of E86, keep the E86 source-consensus law, and preserve strict/deployable stress?
- Method: `analysis_outputs/e89_e86_e72_decontamination_scan.py` generated controlled mixmin-relative logit movements: E86/E85/no-Q2/no-overstep/inverse-top controls, global E86-noQ2 blends, high-E72 row/cell fallback to noQ2/E85/mixmin, rowwise Q2 removal, and projection away from E72 failed delta. It scored all rows with the same combo, hidden/world/block, raw-energy, and tail stress as E86, then added E88-style movement attribution metrics.
- Result:
  - rows `52`; evaluated `52`; strict/deployable `37/37`; best local all delta remains E86 at `-2.77059e-5`.
  - the selected risk-adjusted candidate is `analysis_outputs/submission_e89_e72decontam_00d7807f.csv`.
  - selected rule: start from E86, but for cells in the top `20%` of E72 failed absolute movement, fallback to E85.
  - selected stress: all delta `-2.58960e-5`, inverse-top `-5.55392e-6`, raw05-compatible `-3.33148e-5`, all-sign `-3.88191e-5`, hidden Q2/S3 `-0.000216060`, world `-0.000140452`, block win `0.638889`, block-tail safe `0.944444`.
  - selected E72 contamination index `0.676361`, down from E86 `0.772379`, no-Q2 `0.730408`, and E85 `0.734771`.
  - aggressive projection-away variants lower E72 proximity but often break inverse-top/world/block stress; projection is not the safe repair. E85 fallback on high-E72 cells is the live repair.
- Interpretation: E89 creates a genuine risk-adjusted submission candidate, but it is not a free improvement. It sacrifices part of E86's hidden/world/block strength to buy much lower E72 proximity. It should be submitted only if the next public question is "does public punish E72-contamination more than it rewards E86's extra local margin?"
- Decision: add H84/F70. Do not rank E89 above E86 on upside; rank it above inverse-top-prior as a safety/diagnostic fallback. If E86 has not been submitted, E86 remains the sharper upside sensor. If the goal is lower downside after E72's public miss, E89 is the better single file than no-Q2 or inverse-top-prior.

## E90. E89 Pareto-Knee Selector

- Observe: E89 minimized E72 contamination, but its selected cell fallback weakened E86's hidden/world/block edge more than some other strict repairs.
- Wonder: is the useful next sensor the absolute minimum-contamination repair, or a Pareto knee that stays cleaner than E85/no-Q2 while preserving more E86 row-level structure?
- Method: `analysis_outputs/e90_e89_pareto_knee.py` reused the E89 strict/deployable scan, kept only rows cleaner than both E85 and no-Q2, penalized projection-away rows, and scored margin retention, E72 decontamination, hidden/world retention, block/tail safety, and row-coherence.
- Result:
  - eligible strict rows: `13/37`.
  - selected file: `analysis_outputs/submission_e90_e72pareto_28925de5.csv`.
  - selected rule: E86 with E85 fallback on top `10%` E72-contaminated rows.
  - selected stress: all delta `-2.69324e-5`, contamination `0.715784`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block win `0.777778`, block-tail safe `1.0`.
  - retention versus the E86/E85 span: margin `0.798048`, world `0.681272`, hidden `0.518671`; decontamination gain `0.589422`.
- Interpretation: E90 is not lower-risk than E89 by E72 contamination alone. It is a balanced public sensor for the competing belief that public may reward row-coherent structural retention after only the worst E72 rows are removed.
- Decision: add H85/F71/FH80. Use E90 between E86 and E89 when a single slot should balance upside and E72 downside. If E90 beats E89/E86, row-coherent decontamination is public-real; if E89 beats E90, public punishes E72-contaminated cells more directly; if E86 beats both, the contamination lens is over-penalizing useful structure.

## E91. E72-Updated Selector Collapse Audit

- Observe: E72 is now a real public-negative anchor after mixmin, but its public miss is small: `+0.0001011367` vs mixmin.
- Wonder: does adding E72 make the movement-fingerprint public proxy good enough to rank E86/E90/E89/E85, or does it fail on the exact frontier distinction we need?
- Method: `analysis_outputs/e91_e72_updated_selector_collapse_audit.py` reused the public-anchor movement features from `public_anchor_bottleneck_decomposition.py`, included known public anchors from `public_probe_observations.csv` plus manual A2C8, ran fixed LOOCV ridge proxy families, and scored only the post-mixmin decision set.
- Result:
  - known anchors: `10`.
  - best fixed proxy: `raw05_a2c8_compat`, MAE `0.000543412`, p90 abs error `0.001010234`.
  - mixmin actual public is `0.5763066405`, but best-proxy LOO predicts `0.5774493627`; error `+0.001142722`.
  - E72 actual delta vs mixmin is `+0.0001011367`, but best-proxy LOO predicts E72-minus-mixmin `-0.0000460726`.
  - proxy p90 error is `9.99x` the entire E72 miss.
  - the proxy ranks E86/E90/E89 as worse than mixmin, but it also ranks the known mixmin frontier itself as worse by much more than the public signal scale.
- Interpretation: H86 is rejected as a submission selector. The E72-updated movement proxy is diagnostic only; it cannot be used to choose among E86/E90/E89.
- Decision: no E91 submission. Keep E86/E90/E89 as predeclared public sensors: E86 tests maximum-upside source-consensus target pruning, E90 tests row-coherent decontamination, and E89 tests minimum E72 contamination.

## E92. Hidden-Block Posterior Alignment Audit

- Observe: after E91, the tempting known-LB selector is dead. The remaining E86/E90/E89 choice needs a non-public hidden-structure check. E90's claim is specifically row-coherent hidden-state preservation, so the cheapest independent stress is hidden-block posterior alignment.
- Wonder: does `hidden_block_posterior_block_summary.csv` act as a public-safe target representation for ranking E86/E90/E89, or does it reward the same public-negative E72 direction?
- Method: `analysis_outputs/e92_hidden_block_posterior_alignment_audit.py` compared mixmin-relative movement for E72, E85, E86, no-Q2, E90, and E89 against row-repeated hidden-block posterior rates and endpoint rates. Metrics included posterior CE delta, endpoint CE delta, posterior direction mass agreement, block-target R2, high-posterior-shift block concentration, and E72 failed-direction mass agreement. No public-LB regression was fit.
- Result:
  - hidden-block alignment leader: `failed_e72`.
  - best posterior CE: `failed_e72`, posterior CE delta `-0.000287300`.
  - unobserved post-mixmin posterior CE order: no-Q2 `-0.000257196`, E86 `-0.000255621`, E90 `-0.000250767`, E89 `-0.000235903`, E85 `-0.000207023`.
  - highest block-target R2: E89 `0.356204`.
  - E72 failed-direction mass agreement: E86 `0.668166`, E90 `0.657990`, E89 `0.635838`.
- Interpretation: H87 is rejected as a public-safe selector. Hidden-block posterior alignment is E72-tainted because it ranks the known public-negative E72 file first. This is a LeJEPA-style representation-health failure: a latent can be geometrically coherent and still public-misaligned.
- Decision: no E92 submission. Keep the candidate ordering hypothesis-based. E86 remains maximum-upside/local-margin, E90 remains balanced row-coherent decontamination, and E89 remains minimum E72-contamination/block-R2 fallback. Do not rank submissions by hidden-block posterior CE alone.

## E93. Target-Manifold Counter-Energy Audit

- Observe: E92 killed hidden-block posterior CE as a selector because it liked the failed E72 file. The cheapest counter-hypothesis is that E72 is block-coherent but violates the target dependency manifold.
- Wonder: can train Q/S co-occurrence and conditional target geometry reject E72 while keeping E86/E90/E89 alive?
- Method: `analysis_outputs/e93_target_manifold_counterenergy_audit.py` fitted seven logistic target-conditional models `target_j ~ other targets` on train labels, then scored known public anchors and live candidates by conditional logit residual, empirical label-pattern mixture NLL, nearest-pattern NLL, and pair-correlation gap to train. Public LB was used only as a sanity readout, not a fitted target.
- Result:
  - E72 target-manifold delta mean vs mixmin: `-0.001468687`, so the failed public file looks more target-manifold-consistent than mixmin.
  - Live target-manifold delta order: E86 `-0.000921783`, no-Q2 `-0.000914184`, E90 `-0.000877945`, E89 `-0.000806467`, E85 `-0.000742113`.
  - Known public-bad anchors can score very well: `final9` `-0.020801364`, `bad_q2_jepa` `-0.002958703`.
  - Public-LB sanity correlations were weak: target-manifold delta mean Spearman `0.260606`, conditional residual Spearman `-0.163636`, pair-corr gap Spearman `0.503030`.
  - E72 target-level self-consistency improved on all seven targets, strongest by logit-residual delta on S1 `-0.006393236`, Q3 `-0.004905500`, S3 `-0.004410437`.
- Interpretation: H88 is rejected as a public-safe selector. Target dependency/manifold energy is also E72-tainted in the relevant sense: it rewards a public-negative movement and even rewards some older bad public anchors.
- Decision: no E93 submission. Do not use target-manifold consistency to rank E86/E90/E89. The remaining public question is not target-dependency violation; it is hidden public subset/calibration/world identity after a movement that can look healthy under both block posterior and train target co-occurrence.

## E94. Soft-Health / Hard-Label Tail Audit

- Observe: E92 and E93 both rewarded the public-negative E72 file, yet E72's public miss versus mixmin was small (`+0.0001011367`). This means the failure could be caused by a small public-label tail rather than by broad representation collapse.
- Wonder: can a candidate look healthy under soft hidden-block/target-manifold geometry while carrying hard-label LogLoss tail risk in the same direction that made E72 fail?
- Method: `analysis_outputs/e94_soft_health_hard_tail_audit.py` computed candidate-minus-mixmin hard-label LogLoss deltas for each cell under labels `0` and `1`. For E72-active cells it defined the adverse hard label as the label that makes E72's move wrong, then measured each candidate's positive exposure to that same adverse direction. E92 posterior CE and E93 target-manifold scores were merged only as context, not as a fitted selector.
- Result:
  - E72 moved `893/1750` cells. If every active moved cell had the E72-adverse hard label, full positive exposure would be `0.002330945`.
  - The observed E72 public miss is only `0.043389` of that full-exposure scale, so a small realized tail is enough to explain the miss.
  - Live E72-adverse positive exposure: E85 `0.000739201`, E89 `0.000799109`, no-Q2 `0.000906798`, E90 `0.000934031`, E86 `0.001010242`.
  - Live soft-health order is different: E86 `0.001177404`, no-Q2 `0.001171380`, E90 `0.001128712`, E89 `0.001042370`, E85 `0.000949136`.
  - Known-public sanity correlations favor hard-tail metrics over soft health: hard worst-tail mean Spearman `0.866667`, KL-if-mixmin-calibrated `0.866667`, E72-adverse positive exposure `0.793939`, soft-health gain only `0.081935`.
- Interpretation: H89 is supported as a bottleneck explanation. E72 failure is compatible with a representation that looks coherent under posterior and target-manifold energies, because LogLoss is sensitive to the small subset of hard labels aligned against the move. This is a LeJEPA-style health failure: soft geometry alone is not enough unless it is paired with hard-label tail exclusion.
- Decision: no E94 submission. Use hard-label tail exposure as a mandatory gate beside JEPA-style soft health. E86 remains max-upside because it has the strongest soft-health/local structure, E90 remains balanced, E89 becomes the lower-downside main sensor by hard-tail exposure, and E85 is the conservative floor.

## E95. Hard-Tail Gate Scan

- Observe: E94 made hard-label tail exposure useful as a risk lens, but it did not answer whether the tail can localize a new candidate or only restate the E89/E90/E86 tradeoff.
- Wonder: can the E72-adverse hard-tail cells choose a fallback gate that keeps E86's structural margin while beating E89 on both hard-tail exposure and local all-combo margin?
- Method: `analysis_outputs/e95_hard_tail_gate_scan.py` used mixmin as base and E72 as the known public-negative hard-tail direction. It generated controlled E86/E90 row/cell fallback candidates to E89, E85, or mixmin, plus scalar E86/E89 and E90/E89 blends. Candidates were scored with the same combo, hidden/world/block, raw-energy, and strict gates used by E89/E90. A file was materialized only if a non-control row was strict and non-dominated on hard-tail exposure plus local margin versus E89/E90/E85. The scan also separates raw best-tail from strict best-tail because broad fallback to mixmin can look tail-perfect while failing structural stress.
- Result:
  - rows/evaluated/strict: `178/178/112`.
  - strict non-dominated rows: `19`.
  - best raw non-control tail: `0.000146152`, but this is non-strict rollback-like and not submission evidence.
  - best strict non-control tail: `0.000788914`.
  - selected file: `analysis_outputs/submission_e95_hardtail_541e3973.csv`.
  - selected rule: start from E86, replace E72-adverse top-tail cells with E85 fallback over all targets.
  - selected stress: all delta `-0.0000262074`, E72-adverse exposure `0.000788914`, world `-0.000132931`, hidden Q2/S3 `-0.000251140`, block win `0.750000`, block-tail safe `0.972222`.
  - selected movement: active targets `Q2,S1,S2,S3`, moved cells `550`, mean abs logit move vs mixmin `0.00554828`.
- Interpretation: H90 is partially supported. E95 creates a real new same-law candidate, not a trivial mixmin rollback: it beats E89 on both hard-tail exposure (`0.000788914 < 0.000799109`) and all-combo margin (`-2.62074e-5 < -2.58960e-5`) while keeping more structure than E85. It does not dominate E86 on upside or E90 on row-coherent structural retention, so it is a lower-downside hard-tail bet rather than the universal best.
- Decision: add `submission_e95_hardtail_541e3973.csv` as the highest lower-downside post-E72 public sensor. If the next slot should test hard-tail public sensitivity directly, submit E95 before E89. If the next slot should test maximum upside, submit E86. If it should test row-coherent structural retention, submit E90.

## E96. Public-Miss Budget Tail Scenarios

- Observe: E95 beat E89 on scalar hard-tail exposure and local margin, but that still does not prove the E72 public miss would have occurred on the cells E95 protects. The observed E72 miss is a total budget, not a label map.
- Wonder: if E72's public miss `+0.0001011367` is allocated over many plausible E72-adverse hard-label tail worlds, does E95 remain robust versus E89/E90/E86, or only in a narrow scenario?
- Method: `analysis_outputs/e96_public_miss_budget_tail_scenarios.py` fixed the observed E72-minus-mixmin public miss as a LogLoss budget over `1750` test-target cells. It generated deterministic and random weighted scenarios over target masks, E72 hard-tail masks, E95 fallback cells, and candidate movement masks. Each scenario selected fractional E72-adverse hard-label cells until failed E72 exactly reconstructed the observed public miss, then scored live candidates on the same hard labels. No public labels were fit.
- Result:
  - scenarios: `3894/3894` complete-budget.
  - failed E72 reconstructs `0.0001011367` in every complete scenario; mixmin is exactly `0`.
  - live mean conditional deltas: E95 `0.000057874`, E85 `0.000058977`, E89 `0.000059964`, E90 `0.000069295`, no-Q2 `0.000071237`, E86 `0.000076162`.
  - live p95 conditional deltas: E85 `0.000115304`, E95 `0.000115644`, E89 `0.000117735`, E90 `0.000129152`, E86 `0.000138751`, no-Q2 `0.000138876`.
  - E95 wins the live set in `0.527478` of scenarios, beats E89 in `0.712378`, E90 in `0.999486`, and E86 in `0.998973`.
  - E95 loses most to E89 in diffuse/low-amplitude Q2 or Q2/S3-bottom scenarios, especially `q2s3 bottom`, where E95 is `+0.000028431` worse than E89 while still slightly better than E90.
- Interpretation: H90 is strengthened against E89/E90/E86 but not as a universal conservative claim. E95 is the best mean/win-rate hard-tail sensor and broadly dominates E89, while E85 remains the slightly lower p95 tail floor. The new distinction is: E95 is the active lower-downside hard-tail submission candidate; E85 is the conservative tail-floor fallback if we decide E95 is too structured/E72-derived.
- Decision: no new submission file. Keep `submission_e95_hardtail_541e3973.csv` as the top information-rich hard-tail public sensor. If the next slot is pure downside minimization rather than information gain, E85 deserves explicit consideration because its p95 is marginally lower. E96 is recorded as conditional scenario stress, not public-LB optimization.

## E97. E95 Public Observation Assimilation

- Observe: `submission_e95_hardtail_541e3973.csv` was submitted and scored public LB `0.5762913298`.
- Wonder: did the E95 hard-tail localized fallback act as a real public improvement, or was E96 only a local/scenario artifact with no leaderboard edge?
- Method: compare E95 against the two relevant public anchors: mixmin (`0.5763066405`) and failed E72 (`0.5764077772`). Read the result as a sensor for H90/H91, not as proof of the exact public labels.
- Result:
  - E95 vs mixmin: `-0.0000153107`.
  - E95 vs failed E72: `-0.0001164474`.
  - E95 recovers the E72 miss and adds another `15.14%` of the E72 miss scale beyond mixmin.
  - E95's public gain is `58.42%` of its local all-combo margin (`0.0000153107 / 0.0000262074`).
- Interpretation: H90 is now public-supported. The E72-adverse hard-label tail was not just a post-hoc diagnostic; localized fallback to E85 on the E86 hard-tail cells produced a real, if small, public improvement. H91 also gains support as a stress-ranking tool because the candidate it promoted by mean/win-rate was the one that improved public. The small edge is the constraint: E95 did not unlock the 0.54 path, it only shaved a localized LogLoss tail while preserving enough E86 structure.
- Decision: promote E95 to current public frontier. Do not rescore everything by E96 alone. The next public question should be one of three explicit hypotheses: E90 if testing whether more row-coherent E86 structure can beat E95, E86 if testing maximum structural upside despite tail risk, or E85 if testing whether the conservative p95 tail floor beats retained structure.

## E98. E95-Updated Selector Audit

- Observe: E95 gives the known-public table one more near-frontier anchor, bracketing mixmin and failed E72 with a public-positive hard-tail file.
- Wonder: does adding E95 make movement-fingerprint public regression sharp enough to choose E90/E86/E85, or does it still fail at the exact scale of the new frontier?
- Method: `analysis_outputs/e98_e95_updated_selector_audit.py` added E95 to `public_probe_observations.csv`, reused the fixed LOOCV ridge proxy families from `public_anchor_bottleneck_decomposition.py`, audited critical holdout deltas among E95/mixmin/E72, and scored the unresolved post-E95 queue.
- Result:
  - known public anchors: `11`.
  - best fixed proxy: `raw05_a2c8_compat`, MAE `0.000520095`, p90 abs error `0.000816497`.
  - E95 edge over mixmin: `0.0000153107`; the best proxy p90 error is `53.33x` this edge.
  - E72 miss over mixmin: `0.0001011367`; the best proxy p90 error is `8.07x` this miss.
  - critical holdouts: mixmin-minus-E95 sign correct but abs error `0.0000619237`; E72-minus-mixmin sign wrong, predicted `-0.0000305135` vs actual `+0.0001011367`; E72-minus-E95 sign correct but abs error `0.0000697264`.
  - future proxy spread is only `0.000015142`, still below a trustworthy resolution because the proxy cannot hold out the near-frontier anchors.
- Interpretation: H92 is rejected. E95 is a useful public observation, but adding it does not turn known-LB movement regression into a candidate selector. The regression can produce a numeric ranking, yet it is still less informative than the predeclared hard-tail/structure hypotheses at the scale that matters.
- Decision: no E98-ranked submission. Keep E90/E86/E85 as hypothesis sensors: E90 for row-coherent retained structure, E86 for max source-consensus upside, and E85 for conservative p95 tail floor.

## E99. E95-Conditioned Tail Transfer Audit

- Observe: E96 used E72's public miss as a hard-tail budget, but it did not condition on the new E95 public gain. A tail world that explains E72 but makes E95 impossible is now outdated.
- Wonder: after forcing every E96 tail world to explain both the failed E72 miss and the successful E95 gain, do E90/E86/E85 still look like worthwhile next improvement bets?
- Method: `analysis_outputs/e99_e95_conditioned_tail_transfer.py` solved a two-term model per complete E96 scenario: `public_delta = alpha * local_all_delta + lambda * E96_tail_delta`. The two equations were the observed E72 delta versus mixmin (`+0.0001011367`) and E95 delta versus mixmin (`-0.0000153107`). Candidate scores were then computed for E85/E86/no-Q2/E90/E89/E95 without fitting any public labels.
- Result:
  - complete solved scenarios: `3894/3894`.
  - positive-transfer scenarios: `3849`; broad-plausible scenarios (`0 < alpha <= 8`, `0 < lambda <= 4`): `3452`.
  - broad-plausible transfer geometry: alpha median `3.310470`, p10/p90 `0.948551/6.794704`; lambda median `1.345192`, p10/p90 `1.098908/1.708502`.
  - broad-plausible winner mode/best mean/best p95: all `E95`.
  - broad-plausible mean deltas: E95 `-0.000015311`, E89 `-0.000011477`, E85 `-0.000005652`, E90 `-0.000001938`, no-Q2 `-0.000000021`, E86 `+0.000005034`.
  - broad-plausible beat-E95 rates: E89 `0.195829`, E85 `0.031866`, no-Q2 `0.023175`, E90 `0.002607`, E86 `0.000290`.
- Interpretation: H93 is supported as a negative ranking update. E95-conditioned worlds do not promote E90/E86 as likely improvements; they mostly say the current E95 frontier already sits at the best local+tail compromise. The only unresolved file with nontrivial E95-beat probability is E89, which means the remaining plausible counterfactual is not "more row-coherent E86 structure" but "E95 overfit the hard-tail cells and the true public tail is closer to the older E89 cell-fallback geometry."
- Decision: no E99 submission file. Update the next-public queue: keep E95 as active best; if forced to spend exactly one diagnostic slot for expected E95-beat probability, E89 is now the sharper counterfactual than E90. Use E90 only if the explicit question is row-coherent structural retention, not expected improvement over E95.

## E100. E89 Counterfactual Anatomy

- Observe: E99 made E89 the only material unresolved E95 counterfactual, but that aggregate `0.195829` beat-E95 rate did not say whether E89 was a broad lower-downside candidate or a narrow public-tail hypothesis.
- Wonder: in the E95-conditioned worlds where E89 beats E95, what hidden tail geometry is being selected?
- Method: `analysis_outputs/e100_e89_counterfactual_anatomy.py` decomposed the E99 broad-plausible scenarios by mask/order/family, then compared E89-minus-E95 local disadvantage, E96-tail advantage, required tail advantage, and tail surplus.
- Result:
  - broad-plausible scenarios: `3452`.
  - E89 beat-E95 rate: `0.195829`; E89 live win-rate `0.188876`; E95 live win-rate `0.800406`.
  - mean E89-minus-E95 public delta: `+0.000003833`, so E89 is still worse on average.
  - E89-beats-E95 cases: `676`, mean E89-minus-E95 `-0.000004251`, mean tail surplus `+0.000002916`, top mask `q2s3`.
  - E89-not-beats-E95 cases: `2776`, mean E89-minus-E95 `+0.000005802`, mean tail surplus `-0.000004272`, top mask `s1s2s3`.
  - dominant favorable slice: `mask_name=q2s3`, `n=368`, E89 beat rate `0.779891`, mean E89-minus-E95 `-0.000005030`, mean tail surplus `+0.000003262`.
  - negative slices: `s1s2s3` and `e95_fallback_cells` have no material E89-beat support under this decomposition.
- Interpretation: H94 is supported. E89 is not a general lower-risk successor to E95. It is specifically a Q2/S3 diffuse-tail counterfactual: E89 wins only when the realized public tail is spread through Q2/S3-like E72 cells rather than the cells E95 localized as hard-tail fallback.
- Decision: no E100 submission file. Keep `analysis_outputs/submission_e89_e72decontam_00d7807f.csv` as the single highest-information next public sensor only if the question is "did E95 over-localize Q2/S3 tail risk?" If E89 improves, update the world model toward diffuse Q2/S3 tail allocation. If E89 worsens, close the E89 branch and keep E95's localized hard-tail gate as the better current explanation.

## E101. Q2/S3 Tail Graft Probe

- Observe: E100 left one live counterfactual, but full E89 changes more than the favorable Q2/S3 tail pocket. If the pocket is real, a smaller E95-relative graft should test the same world with less non-Q2/S3 movement.
- Wonder: can the Q2/S3 diffuse-tail advantage be separated from E89 as a strict/deployable E95 graft, or does separation break combo/hidden/world/block stress?
- Method: `analysis_outputs/e101_q2s3_tail_graft_probe.py` used E95 as base and grafted E89/E85/mixmin values onto Q2/S3 scopes selected by E72-positive tail, E89-vs-E95 tail advantage, E95 fallback cells, or logit difference. It then rescored candidates with E83 combo/hidden/world/block stress and E96/E99 E95-conditioned transfer scenarios. Pass required strict gate, lower E72-adverse exposure than E95, broad-plausible mean better than E95, broad p95 non-positive, broad beat-E95 rate above `0.75`, and Q2/S3-slice improvement.
- Result:
  - rows/grafts/strict-like/pass: `618/612/581/54`.
  - materialized file: `analysis_outputs/submission_e101_q2s3tail_177569bc.csv`.
  - selected rule: start from E95 and shrink Q2/S3 movement `25%` toward mixmin. The recorded selector is `q2s3_all`, but effective active cells vs E95 are only `50` because most Q2/S3 cells already equal mixmin.
  - selected local stress: all delta `-0.0000253724`, E72-adverse exposure `0.000692235` versus E95 `0.000788914`, hidden Q2/S3 `-0.000191316`, world `-0.000115685`, block win `0.750000`, block-tail safe `0.972222`, inverse-top `-0.000001974`, raw05-compatible `-0.000033936`, all-sign `-0.000040207`, strict/deployable `true`.
  - E95-conditioned transfer: broad-plausible mean vs E95 `-0.0000162053`, beat-E95 rate `0.983488`, p95 vs E95 `-0.000001564`; Q2/S3-slice mean vs E95 `-0.0000289568`, beat rate `1.0`, p95 `-0.0000150661`.
- Interpretation: H95 is supported locally. The live branch is sharper than "submit E89": public may prefer E95's structural hard-tail gate except that E95 still over-moves a small Q2/S3 tail subset. This is a rollback of only E95's Q2/S3 correction cells, not a broad E89 decontamination file.
- Decision: promote `submission_e101_q2s3tail_177569bc.csv` as the next highest-information public sensor ahead of full E89. If it improves public, the world model shifts to "E95 was right structurally but Q2/S3 tail amplitude was too high." If it worsens, retire the E101 rollback branch and test full E89 only if the question remains diffuse Q2/S3 tail rather than amplitude.

## E102. E101 Active-Cell Structure Audit

- Observe: E101's selected file changes only `50` Q2/S3 cells versus E95. Before building another rollback, we need to know whether those cells form a hidden block/subject subset or are simply the Q2/S3 cells where E95 differs from mixmin.
- Wonder: if E101 improves public, should the next experiment be a block/subject-local mask, a broader Q2/S3 amplitude line, or a return to block-state representation work?
- Method: `analysis_outputs/e102_e101_active_cell_structure_audit.py` built a 500-cell Q2/S3 atlas over all submission rows, attached hidden submission block metadata, measured active-cell enrichment by target/subject/block/context/position, and ran a target-count-preserving permutation null with `20000` permutations.
- Result:
  - active cells/rows/blocks/subjects: `50/48/26/10`.
  - target split: Q2 `11`, S3 `39`; every active cell is exactly `25%` rollback toward mixmin.
  - largest active hidden block has only `4` active cells; active cells touch all subjects and most blocks, so this is not a narrow subject/block mask.
  - strongest enrichment is target S3 (`39/50`, z `3.959798`), followed by weak subject/block enrichments such as id06 rows and id04 cells.
  - permutation null: edge-or-near-edge rate `0.620` vs null mean `0.471289`, p `0.016999`; mean edge distance `1.680` vs null `2.138444`, p `0.040848`; block/subject concentration metrics are not significant (`max_cells_per_block` p `0.997300`, `n_blocks_touched` p `0.935553`, `n_subjects_touched` p `1.0`).
- Interpretation: H96 is supported only in the weak edge-local sense. E101 is primarily a target-axis amplitude rollback, not a hidden subject/block-local selector. The one non-random structure is proximity to hidden block edges, which fits the broader calibration/tail story: boundary rows may be where E95's Q2/S3 correction over-moves.
- Decision: keep E101 as the next public sensor. If it improves, the next local branch should be an E101-centered Q2/S3 amplitude or edge-risk gate, not a handcrafted subject/block mask. If it worsens, the failure should mostly kill generic Q2/S3 rollback; only the edge-local variant remains weakly alive.

## E103. Edge-Local Q2/S3 Amplitude Probe

- Observe: E102 left edge proximity as the only non-random structure in E101's active cells, but it did not prove that edge-local cells are better submission cells than the full E101 amplitude rollback.
- Wonder: is the edge-local signal strong enough to replace E101 with a sharper Q2/S3 rollback, or is it only a diagnostic geometry to use after public feedback?
- Method: `analysis_outputs/e103_edge_local_q2s3_amplitude_probe.py` reused E101's E95-conditioned scoring frame. It built `180` E95-to-mixmin rollback variants from E102 cell masks: active all, active edge/interior, S3/Q2 splits, edge-only masks, and top logit-gap masks over alphas `0.125-1.0`. A row could materialize only if it passed the strict E101-style stress and dominated E101 on broad-plausible mean, p95, and beat-E95 rate together.
- Result:
  - variant rows: `180`; E103 pass rows: `12`; E101-dominating rows: `0`.
  - no E103 submission file was materialized.
  - E101 reference broad mean/p95/beat vs E95: `-0.000016205` / `-0.000001564` / `0.983488`.
  - best passing non-duplicate stress row by mean was `active_all` alpha `0.375`, broad mean `-0.000023425`, p95 `-0.000002159`, beat `0.980881`; it improves mean/p95 but loses beat-rate versus E101, so it is a higher-amplitude risk variant rather than a clean successor.
  - edge-only rows reached broad mean around `-0.000022843` at alpha `1.0`, but p95 was positive (`+0.000007795`) and strict gate failed.
- Interpretation: H97 is only partially supported. Edge proximity is a real diagnostic clue, but the direct edge-local selector fails as an E101 replacement. The surviving rows are mostly the same active-all/S3-heavy amplitude line, not a new block-edge mask. This reinforces the view that E101 is an amplitude public sensor, while edge energy should be used for post-E101 branching or risk scoring.
- Decision: no E103 submission. Keep `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` as the next highest-information public sensor. If E101 improves, test amplitude schedule variants with edge energy as a stress dimension; do not jump directly to handcrafted edge-only masks. If E101 worsens, edge-only rollback remains too weak to rescue the generic Q2/S3 rollback branch without new evidence.

## E104. E101 Amplitude Pareto-Cliff Audit

- Observe: E103's best passing active-all alpha `0.375` improved E95-conditioned mean/p95 versus E101 but lost beat-rate. That could mean E101's alpha `0.25` is just a coarse-grid artifact, or it could be a local Pareto cliff.
- Wonder: if we fine-scan rollback amplitude around E101, can a slightly higher alpha dominate E101 on broad mean, p95, and beat-rate, or does scenario support drop immediately?
- Method: `analysis_outputs/e104_e101_amplitude_pareto_cliff.py` fine-scanned alphas `0.000-0.500` by `0.005` over active-all, active-S3, top-gap, edge, and interior masks, using the same E95-conditioned transfer frame as E101/E103. A submission could materialize only if it passed E101-style stress and dominated E101 on broad mean, p95, and beat-rate together.
- Result:
  - fine-grid variant rows: `505`; E101-pass rows: `228`; E101-dominating rows: `0`.
  - no E104 submission file was materialized.
  - active-all alpha `0.250` reproduces E101 broad mean/p95/beat vs E95: `-0.000016205` / `-0.000001564` / `0.983488`.
  - first active-all alpha above E101 with beat-rate loss: `0.255`.
  - alpha `0.255` improves mean/p95 versus E101 by about `3.02e-7` / `2.6e-8`, but lowers beat-rate by `0.000289687`.
  - best passing active-all alpha `0.380` improves broad mean/p95 to `-0.000023695` / `-0.000002181`, but lowers beat-rate to `0.980881`.
  - edge and interior masks have `0` pass rows.
- Interpretation: H98 is supported locally. E101 is not just a coarse grid accident. More rollback along the same active-all Q2/S3 line buys average transfer and p95 at the cost of E101's scenario support almost immediately. This is a classic amplitude Pareto cliff: it marks risk preference, not a stronger hidden-world law.
- Decision: no E104 submission. Keep `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` as the next public sensor because it is the last point before beat-rate starts to fall. Higher-alpha rows are useful as post-E101 follow-up only if public confirms that Q2/S3 rollback is directionally right and the next question becomes upside/risk tradeoff.

## E105. E101 Public-Label Break-Even Anatomy

- Observe: E101 is the next sensor, but without public labels its future LB result would be underinterpreted unless we know which hard-label world it tests. It changes only `50` active Q2/S3 cells versus E95.
- Wonder: if E101 improves or worsens public, does that imply a global target-prior shift, a subject-prior shift, or a local S3/Q2 tail event concentrated in the active cells?
- Method: `analysis_outputs/e105_e101_public_label_breakeven.py` computed E101-minus-E95 LogLoss deltas for each active cell under hard labels `0` and `1`. It marked the label that supports E101, computed all-support/all-adverse bounds, found the minimum high-impact cells needed to beat E95, and ran `200000` Monte Carlo samples under global and subject train priors.
- Result:
  - active cells: `50`, split Q2 `11`, S3 `39`.
  - E101-support labels are balanced by count: `25` label-0 support and `25` label-1 support.
  - all-support E101-vs-E95 delta: `-0.000096679`; all-adverse delta: `+0.000211677`.
  - to beat E95, the top-impact supportive labels need only `23/50` cells; to match E95's edge over mixmin, `25/50` cells.
  - S3 owns `0.935862` of active-cell flip benefit, so the public signal is mostly S3, not Q2.
  - global train prior simulation: expected E101-vs-E95 delta `+0.000048971`, beat probability `0.016610`.
  - subject prior simulation: expected delta `+0.000007854`, beat probability `0.335360`.
- Interpretation: H99 is supported as a framing claim. E101 is not a generic prevalence/prior correction; under global priors it should lose. It becomes live only when the active cells follow subject/block-local label tendencies or deviate further in the E101-favorable direction, especially on S3. This makes the pending public LB highly diagnostic: a win would imply local S3-heavy tail labels, not just "Q2/S3 rollback is broadly good."
- Decision: no new submission. Keep E101 as the next public sensor, but pre-register the interpretation. If E101 improves, follow-up should condition on subject/block-local S3 tail labels and then revisit amplitude. If E101 worsens, do not amplify E101 or E104 higher-alpha variants; the realized public hard-label world did not occupy the rollback-favorable side.

## E106. E101 Subject-Prior Gate Audit

- Observe: E105 made E101 live only under subject-local priors, so the immediate temptation is to gate E101 cells by subject support before public feedback.
- Wonder: can subject-prior support select a smaller E101-style rollback that is healthier than full E101, or is it only a public-result interpretation energy?
- Method: `analysis_outputs/e106_e101_subject_prior_gate.py` built E95-to-mixmin rollback variants on E105 active cells using subject expected delta, subject-support quantiles, S3-only masks, flip-benefit ranking, and global/subject expected rankings over alphas `0.25/0.50/0.75/1.00`. It reused E101 local+E95-conditioned transfer stress and required any materialized file to beat E101 on prior health plus broad mean/p95/beat.
- Result:
  - variant rows: `268`.
  - E101-pass variants: `12`.
  - prior-healthier variants: `56`.
  - interesting non-replacements: `6`.
  - replacement rows: `0`; dominating rows: `0`.
  - materialized submission: `none`.
  - the best interpretable rows are S3-heavy `35-45` cell alpha `0.25` gates, but all spend E101's broad scenario support. `active_s3_all` alpha `0.25` has mean/p95/beat `-0.000015728` / `-0.000001195` / `0.973349` versus E101 `-0.000016205` / `-0.000001564` / `0.983488`.
- Interpretation: H100 is rejected as a pre-feedback candidate generator. Subject-prior support is real as label-world energy, but it filters too hard when used as a selector before public feedback.
- Decision: no E106 submission. Keep E101 as the next public sensor. If E101 improves, E106 rows like `active_s3_all` or `flip_benefit_best_top40` can become post-feedback contrast variants. If E101 worsens, do not rescue the branch with subject-prior masks.

## E107. E101 Feedback Decision Map

- Observe: E101 is still pending, but the useful next action depends on whether its public delta can be explained inside the E99/E101 E95-conditioned tail worlds.
- Wonder: if E101 wins by the E95 edge, wins weakly, ties, or loses, which hidden-world branch should survive: E104 amplitude, E106 subject-prior masks, older controls, or model falsification?
- Method: `analysis_outputs/e107_e101_feedback_decision_map.py` rebuilt E104 amplitude and E106 subject-gate candidates, recomputed E96/E99 per-scenario tail predictions, and conditioned broad-plausible E99 scenarios on six hypothetical E101-vs-E95 public deltas. It ranked controls plus E104/E106 follow-ups by conditional mean/p95/beat versus E95 and versus E101. No public labels or new submission were used.
- Result:
  - candidate universe: `292`; scenario outcomes: `6`; summary rows: `1752`.
  - E101 edge-sized win (`-0.0000153107`) has `841` within-tolerance scenarios, tension `False`; small win (`-0.000005`) has `742`, tension `False`; tie has `305`, tension `False`.
  - strong win target `-0.000050`, small loss `+0.000010`, and large loss `+0.000040` require nearest-scenario matching, tension `True`.
  - in edge-win and small-win worlds the top follow-ups are E104 risk-tolerant high-amplitude `active_all` rows around alpha `0.500`; strict E101-pass follow-ups are lower alpha around `0.380`.
  - E106 subject-prior gates do not outrank E104 in the matched outcome subsets.
- Interpretation: H101 is supported as a pre-feedback decision map. If E101 improves, the next branch is deliberate amplitude-up E104, not E106 subject-prior gating. If E101 loses, the E99/E101 world model is strained and we should not rescue the branch with subject masks or higher alpha.
- Decision: no E107 submission. E101 remains the next public sensor. E107 is the conditional branch table to use after E101 public feedback.

## E108. E101-Win Amplitude Follow-Up Kit

- Observe: E107 identified the post-E101-win branch, but it was still a ranking table rather than executable submission files. That creates a decision-risk: after the E101 public result arrives, the next file could be chosen ad hoc instead of from the pre-registered branch.
- Wonder: can we materialize the two useful E101-win amplitude follow-ups now, while keeping them explicitly conditional and not replacing E101 as the next public sensor?
- Method: `analysis_outputs/e108_e101_win_amplitude_followup.py` rebuilt the E104 active-all amplitude scan through the E101/E104 stress path, selected the E107 edge/small-win top risk row and the best conservative strict E101-pass row, materialized both CSVs, and joined them back to E107 conditioned outcomes.
- Result:
  - materialized risk-tolerant file: `analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv`.
  - materialized strict file: `analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv`.
  - risk amp `0.500` is not E101-pass unconditionally, but ranks `1` versus E101 in both edge-win and small-win E107 worlds; edge/small mean vs E101 `-0.000012556` / `-0.000004165`, p95 vs E101 `-0.000009546` / `-0.000001459`.
  - strict amp `0.380` is E101-pass, but ranks only `54` / `49` versus E101 in edge/small worlds; edge/small mean vs E101 `-0.000006864` / `-0.000002316`, p95 vs E101 `-0.000005293` / `-0.000000954`.
  - tie worlds have positive p95 versus E101 for both files, and loss/strong-win worlds are model-tension buckets in E107.
- Interpretation: H102 is supported as a decision hygiene layer, not as a new immediate submission. If E101 wins by edge/small scale, amp050 is the highest-upside next sensor and amp038 is the conservative same-branch sensor. If E101 ties or loses, E108 should not be used as a rescue.
- Decision: no immediate E108 submission before E101 feedback. Keep E101 as the next public sensor. Use the two E108 files only after the pre-registered E101-win condition is observed.

## E109. E101 Tie/Loss Hard-Label World Audit

- Observe: E108 only fixes the E101-win branch. If E101 ties or loses, E107 says the current E99/E101 tail-transfer model is strained, but it does not explain what hidden labels would have caused the failure.
- Wonder: in E101 tie/loss worlds, is the active-cell label realization saying "use a smaller or larger E101-style rollback", or is it saying "the active Q2/S3 rollback direction itself failed"?
- Method: `analysis_outputs/e109_e101_tie_loss_label_world_audit.py` sampled `200000` hidden hard-label worlds for the `50` E101 active cells under global and subject train priors. It bucketed worlds by E101-vs-E95 active-cell delta and measured active-cell-only behavior for E95, E101, E108 amp050/amp038, E89, E85, E90, E86, and mixmin.
- Result:
  - Under subject priors, E101 outcome mass is edge-or-stronger win `0.142385`, small win `0.132400`, tie `0.125515`, small loss `0.355350`, large loss `0.244350`.
  - Tie/loss is mostly missing high-impact S3 support: subject-prior top10 support rate drops from `0.916933` in edge wins to `0.849349` in ties, `0.805226` in small losses, and `0.719218` in large losses; support flip-share drops from `0.749273` to `0.686248` / `0.650286` / `0.585604`.
  - In subject-prior small-loss worlds, E108 amp050 has active mean vs E101 `+0.000011723` and p95 `+0.000019546`; strict amp038 has `+0.000006026` and p95 `+0.000010093`. Both have active beat-E101 rate `0`.
  - In subject-prior large-loss worlds, E108 amp050 has active mean vs E101 `+0.000031668`, strict amp038 `+0.000016397`, again with beat-E101 rate `0`.
  - Active-cell-only loss buckets favor retaining or restoring E95/E86/E90 behavior, not moving farther toward mixmin/E101: in subject small-loss worlds E86/E90/E95 rank `1/2/3` versus E101, while E101/E108/mixmin rank below them.
- Interpretation: H103 is supported. If E101 ties or loses, the hidden-label world did not merely ask for a different subject-prior mask or larger amplitude. It says the active Q2/S3 rollback labels failed, especially high-impact S3 support labels. That closes same-line E108 rescue and weakens full-E89 as an automatic fallback unless the next question is explicitly outside the `50` active cells.
- Decision: no E109 submission. Keep E101 as the next public sensor. If E101 wins, use E108. If E101 ties/losses, avoid E108 and rebuild around active-cell retention/E90-E86 structure or a different non-active diffuse-tail question.

## E110. E101-Negative Non-Active Tail Audit

- Observe: E109 closed same-line E101 rescue, but it left a second ambiguity: if E101 ties or loses because the `50` active cells fail, can the old E89 diffuse-tail hypothesis still survive outside those active cells?
- Wonder: can we create a submit-safe non-active tail graft or active-restored E89/E85 variant, or does a negative E101 result simply leave E95 as the only justified action until the public-world model is rebuilt?
- Method: `analysis_outputs/e110_e101_negative_branch_nonactive_tail.py` built `45` unique candidates: controls, E89/E85 variants with the E101-active cells restored to E95/E90/E86, and E95-to-E89/E85/E90/E86 non-active grafts over `q2`, `s3`, `q2s3`, `s1s2s3`, and all changed cells. It reused E101 structural stress, E99 E95-conditioned tail transfer, and E109 subject-prior active hard-label loss buckets.
- Result:
  - total unique candidates: `45`.
  - active-loss-safe non-control rows: `36`.
  - sensor candidates: `8`.
  - strict candidates: `0`.
  - materialized submission: `none`.
  - the best non-control rows are non-active `S1/S2/S3` grafts from E86/E90; they are active-loss-safe and beat the Q2/S3 slice, but broad E95-conditioned mean/p95 versus E95 remain positive. Best broad mean vs E95 is `+0.000000714` and p95 `+0.000002798`.
  - full active-restored E89/E85 variants also fail the broad E95-conditioned stress: restoring active cells helps the E109 loss bucket but leaves broad mean/p95 versus E95 positive.
- Interpretation: H104 rejects the immediate "E101 loss -> full E89 or non-active graft" shortcut. E101-negative feedback can separate the active-cell failure, but the remaining diffuse-tail movement is still not submit-safe under E95-conditioned downside stress.
- Decision: no E110 submission. If E101 ties or loses, do not automatically submit E89, active-restored E89/E85, or non-active E89/E90/E86 grafts. Treat E95 as the standing best and rebuild the public-world model, or use E90/E86 only as explicit retained-structure sensors rather than expected-improvement files.

## E111. Sauna Frontier Movement Atlas

- Observe: SAUNA MODE asks why E95's `0.5762913298` plateau is natural. The uncomfortable fact is that public-positive E95 is not a broad model upgrade, while public-negative E72 looked locally interesting before submission.
- Wonder: is E95 a general structural improvement, or is it target-axis surgery that removes the all-target contamination that killed E72?
- Method: `analysis_outputs/e111_sauna_frontier_movement_atlas.py` compared submission geometry only: mixmin, E72, E85/E86/E89/E90, E95, E101, and E108 conditional files. It computed active cells, target shares, entropy shifts, E95-confident movement share, and cosine versus the E95-from-mixmin direction.
- Result:
  - E72 failed versus mixmin with public delta `+0.0001011367`, active cells `893`, L1 prob `2.203482`, Q-share `0.450788`, S-share `0.549212`, Q2/S3 share `0.198389`, E95-confident share `0.222567`, and cosine with E95 direction `0.327033`.
  - E95 improved versus mixmin by `-0.0000153107`, active cells `550`, L1 prob `1.509562`, Q-share only `0.019948`, S-share `0.980052`, Q2/S3 share `0.209993`, and E95-confident share `0.386257`.
  - E101 versus E95 changes only `50` cells across `48` rows, Q2/S3 share `1.0`, S-target share `0.905306`, and entropy delta `-0.0000243763`.
  - Full E89 versus E95 is larger and more diffuse: `158` active cells, L1 `0.107468`, Q2/S3 share `0.299376`.
- Interpretation: H105 is the compressed SAUNA explanation. E95 survives because it is target-axis surgery: it removes broad Q/Q3/S4 contamination and keeps mostly S-side movement plus a tiny Q2 component. The 0.576 plateau is created by hidden structure that can be sensed, but ordinary broad translation touches too many target axes and pays LogLoss tail.
- Decision: no E111 submission. Keep E101 as the next kill-test because it is the smallest public sensor for whether the surviving E95 Q2/S3/S3-heavy cells should roll back toward older mixmin geometry.

## Current Decision

가장 저비용으로 많은 가설을 가르는 실험은 E05 selector-only/pairwise-order falsification이었다. 결과는 "micro-refine을 더 많이 만들기보다 selector resolution 또는 large safe representation move가 필요하다"로 수렴한다.

E10 이후 결론은 더 좁아졌다. label-flow/block-rate는 "환상"은 아니지만, 현재 후보들이 a2c8/raw05 public-risk gate를 넘지 못하므로 제출 후보가 아니라 high-confidence gate/energy로만 써야 한다.

E11 이후 결론은 한 단계 더 좁아졌다. semantic label-flow를 dependency-energy/raw05 gate로 제한하면 conflict 없는 control/probe 후보는 만들 수 있지만, strict submit 후보는 여전히 0개다. 병목은 이제 "representation 존재 여부"보다 "selector noise를 넘는 크기의 안전한 probability translation"으로 이동했다.

E12-E14 이후에는 "안전한 probability translation"이 처음으로 구체화됐지만, E15-E19가 그 해석을 좁혔다. S4+Q3 gated atom 조합은 strict pairwise submit gate를 통과했지만 독립 hidden-subset selector에서는 survival 0개였고, pairwise 내부도 만장일치가 아니라 favorable scenario tail에 의존했다. E17은 기존 candidate universe 안에 이 방향을 독립적으로 지지하는 S4/Q3 anchor가 없음을 확인했다. E18-E19는 로컬 OOF archive도 그 anchor가 아님을 보였다. E20은 block/measurement archive도 missing large safe movement가 아님을 보였다. E21은 pair-only와 old-only support가 구조적으로 갈라지고 two-selector majority cell이 비어 있음을 확인했다. E22는 old-only 쪽이 이미 raw05 public observation에 의해 약화됐고, 당시 다음 public sensor를 쓴다면 pair-only S4/Q3가 가장 정보량 높다는 결론을 냈다. E23은 그 sensor를 축소해도 two-selector majority가 생기지 않는다는 것을 보였고, E24는 subject/date/block/energy localization도 conflict를 해결하지 못한다는 것을 보였다. E25는 별도의 큰 움직임 mixmin/direns/sparse branch도 pairwise/old strict gate를 통과하지 못한다는 것을 보였다. E26은 known public LB 역문제 자체도 후보 sign을 결정하지 못할 만큼 underidentified임을 보였고, E27은 train global prior와 subject-target prior를 추가해도 그 ambiguity가 사라지지 않음을 보였다. E28은 binary hidden-label 제약이 일부 anchor fit realism을 높이지만, 아직 current candidate sign을 안정적으로 결정하지 못함을 보였다. E29는 binary world pool이 pair-only S4/Q3보다 mixmin/inverse7을 더 지지할 가능성을 보였지만 frontier-scale world가 1개뿐이라 submit gate는 열지 않았다. E30은 frontier-box 안의 binary worlds가 다수 존재하고 non-candidate objectives에서는 mixmin/inverse7을 강하게 지지한다는 것을 보였지만, adverse candidate-objective worlds도 가능해서 strict gate는 여전히 닫혀 있다. E31은 그 adverse worlds가 train label geometry상 오히려 가장 plausible하다는 것을 보여, generic plausibility gate로는 mixmin을 검증할 수 없다고 결론냈다. E32는 같은 adverse worlds가 known-anchor loss attribution geometry에서는 high-energy라는 점을 보여 mixmin/inverse7 probe 근거를 다시 강화했고, E33은 그 geometry가 특정 anchor 하나에 의존하지 않음을 보였다. E34는 이 신호가 medium non-JEPA anchors와 broad loss/cancellation geometry에 의해 유지되고, exact target-axis semantics에는 덜 의존한다는 점을 밝혔다. E35는 이 신호가 normal-submit certification으로는 부족함을 분리해 냈다. E36은 raw observed structure까지 추가해 mixmin certification을 더 약화시켰다: mixmin은 raw pseudo-label support가 `5/10`이고 mean delta가 positive인 반면, inverse7은 `10/10` source에서 개선됐다. E37은 inverse7/mixmin scale-blend bridge도 strict gate를 만들지 못함을 보였다: raw gate는 14개, anchor gate는 22개였지만 two-selector majority와 bridge gate는 모두 0개였다. E38은 이 상태를 후보 제출 문제가 아니라 worldview sensor 선택 문제로 재정의했다. 10개 후보 중 normal submit은 `0`, public sensor는 `10`이며, 정보량 기준으로 mixmin이 top anchor-loss worldview sensor, inverse7/full-scale branch가 raw+anchor bridge sensor, S4/Q3 pair files가 selector-disambiguation sensor다. E39는 독립 selector calibration 후보였던 OOF archive도 normal ranker가 아님을 보였다: OOF sign은 known public과 맞지만 stage2/ordinal public 순서를 거꾸로 고른다. E40은 test movement fingerprint가 stage2/ordinal 순서를 맞히고 inverse7_s0p25를 가장 raw05-like한 sensor로 보는 단서를 줬지만, bad JEPA severity와 A2C8 leave-one-out best 조건을 놓쳐 strict selector는 0개였다. E41은 여기에 bad-axis geometry를 직접 추가해도 strict/loose selector가 0개임을 보였다. `axis_group`은 bad-anchor severity를 일부 복구하지만 A2C8 LOO를 심하게 실패하고, named-axis는 rank/ordering을 망가뜨린다. E42는 A2C8를 fixed zero anchor로 고정해도 usable gate가 0개임을 보여, A2C8 LOO harshness가 핵심 병목이 아니라 frontier-resolution collapse가 핵심 병목임을 확인했다. E43은 이 해상도 병목을 전 selector family로 확장해 검증했고, selector frontier-resolution gate와 error-margin-certified 후보가 모두 0개임을 보였다. E44는 기존 scored universe 안에 selector error를 넘는 큰 안전 후보도 없음을 보였다. E45는 public subset이 단순한 subject/order/date/raw-domain mask라면 selector target으로 쓸 수 있다는 가설도 반증했다. E46은 이 모든 결과를 block-state 관점에서 재정렬했다: 0.54 자체는 block-rate oracle `0.517878`로 가능하지만, subject identity는 oracle gap의 `0.291286`만 설명하고 Markov/endpoint/threshold/public-mask는 숨은 block-rate vector를 복원하지 못한다. E47은 현재 fold-safe block summary views도 직접 테스트했고, best row blend는 `-0.001505`였지만 block-rate loss는 temporal보다 `0.012440` 나빠졌다. 따라서 현재 후보는 개선 우선순위가 아니라 selector conflict 또는 selector 선택 자체를 설명하는 센서다. 정상 제출 후보는 아직 없다.

E48-E100 이후에는 기준점이 다시 좁아졌다. Mixmin은 previous best를 `0.0011326805` 이겼고, E49-E79는 mixmin 이후의 block-state, raw context, mixmin-hard world, Q2/S3 tail-risk, sparse consensus, amplitude, posterior averaging, reliability mask, row/block/flank mask 가설을 차례로 좁혔다. E80-E82는 direct sparse-gate branch를 닫았다: submitted E73은 public `0.5764077772`로 mixmin보다 `+0.0001011367` 나빴고, pure Q2/S3는 loose지만 sub-margin이었다. E83-E84는 broad structural movement와 Q2/S3 safety를 분리했고, target-group recombination이 hidden/world/block은 통과하지만 `inverse_top` 하나에 막힌다는 것을 보였다. E85는 그 충돌을 row/block gate보다 먼저 target-axis prune으로 찔렀고, `S1,S2,S3`만 남기면 strict/deployable `535/700`이 열린다는 것을 확인했다. E86은 이 법칙이 single-source accident가 아님을 보였다: source-diverse consensus variants가 evaluated `700/700` strict/deployable이고, `Q2,S1,S2,S3` mean consensus shrink `1.25`는 all delta `-2.771e-5`까지 내려가면서 inverse-top/raw05/all-sign/hidden/world/block을 모두 통과했다. E87은 이 public risk를 세 조각으로 분리했다. E88은 그 위험을 E72 public miss 기준으로 다시 읽었다. E89는 첫 cheap repair를 만들었다: E86의 E72-top20% cells만 E85로 fallback하면 strict/deployable을 유지하면서 contamination index를 `0.772 → 0.676`으로 낮춘다. E90은 그 다음 질문을 분리했다: 최소 contamination이 항상 최선은 아니며, E86 row-level 구조를 더 많이 보존하는 top-10% row fallback Pareto-knee가 존재한다. E91은 쉬운 ranking escape route를 닫았다: E72를 known anchor로 추가해도 movement-fingerprint proxy는 mixmin과 E72를 public-scale로 구분하지 못한다. E92는 또 다른 쉬운 escape route를 닫았다: hidden-block posterior CE는 실패한 E72를 1등으로 두므로 public-safe selector가 아니다. E93은 그 반대편 escape route도 닫았다: train target-manifold consistency 역시 실패한 E72와 일부 older bad anchors를 좋게 보므로 public-safe counter-gate가 아니다. E94는 왜 이 soft-health 실패가 가능했는지 hard-label LogLoss tail로 설명했다: E72의 public miss는 full adverse exposure의 `4.3389%`만 실현돼도 나오고, hard-tail metrics는 known public LB와 soft-health보다 훨씬 잘 맞는다. E95는 이 tail-risk를 실제 gate로 바꿨다: E86의 hard-tail cells를 E85로 fallback한 `submission_e95_hardtail_541e3973.csv`가 E89보다 tail과 margin을 동시에 개선하면서 strict stress를 통과했다. E96은 이 결론을 E72 public miss budget scenario로 다시 찔렀고, E95가 평균/승률 기준으로 E89/E90/E86보다 강하지만 p95 tail floor는 E85가 근소하게 더 낮다는 점을 밝혔다. E97에서 E95는 public `0.5762913298`로 mixmin을 `0.0000153107` 이겼다. E98은 E95를 known anchor로 추가해도 public-LB movement regression이 E95/mixmin/E72 근방을 충분히 해상하지 못한다는 것을 보였다. E99는 E72 miss와 E95 gain을 동시에 만족하는 local+tail transfer world를 만들었고, broad-plausible 세계 `3452`개 안에서도 E95가 best mean/best p95/winner mode를 모두 유지했다. E100은 그 안에서 E89가 이기는 세계가 거의 Q2/S3 diffuse-tail allocation에 몰려 있음을 보였다: `q2s3` mask의 E89 beat rate는 `0.779891`이지만, 전체 평균에서는 E89가 E95보다 `+0.000003833` 나쁘다. 따라서 hard-tail localization은 public-real이지만 효과 크기는 여전히 작고, E95보다 더 공격적인 E90/E86 구조-retention이 바로 개선될 가능성은 약하다. 다음 public 질문은 이제 "E95가 과하게 Q2/S3 hard-tail 특정 셀에 맞춰졌고 E89의 더 diffuse한 Q2/S3 cell-fallback geometry가 public에 맞는가"가 가장 정보량 높다. E90은 expected-improvement 후보가 아니라 row-coherent structural-retention sensor로만 남긴다.

E101-E111는 그 질문을 더 좁혔다. E101은 full E89 대신 E95의 Q2/S3 effective cells `50`개만 `25%` mixmin 쪽으로 되돌린 파일을 만들었고, broad-plausible E95-conditioned stress에서 mean/p95/beat `-0.0000162053/-0.000001564/0.983488`로 살아남았다. E102는 그 `50`개가 subject/block-local shortcut이 아니라 `48` rows, `26` hidden blocks, `10` subjects에 퍼진 target-axis amplitude rollback이며, 약한 edge-local 신호만 있다는 것을 보였다. E103은 그 edge clue를 직접 제출 후보로 바꾸려 했지만 `180` variants 중 E101-dominating row가 `0`이라 제출 파일을 만들지 않았다. E104는 fine-grid amplitude scan에서도 `505` variants 중 E101-dominating row가 `0`이고, active-all alpha `0.255`부터 beat-rate가 바로 떨어진다는 것을 보였다. E105는 pending public feedback의 해석 조건을 만들었다: E101은 global train prior 아래서는 beat probability `0.016610`으로 불리하지만, subject prior 아래서는 `0.335360`까지 살아나며 active-cell flip benefit의 `93.5862%`가 S3에 있다. E106은 그 subject-prior 단서를 직접 gate로 바꿔 `268` variants를 만들었지만 E101 대체/dominating row는 `0`개였고, S3-heavy subject-gated alpha `0.25` 후보들도 E101보다 broad scenario support가 약했다. E107은 E101 결과별 조건부 분기표를 만들었다: edge-sized win과 small win은 E104 amplitude-up branch를 살리고, E101 loss는 현재 E99/E101 world model이 설명하지 못하는 tension signal이다. E108은 그 분기를 실제 파일 두 개로 고정했다: risk amp050 `submission_e108_if_e101win_amp050_079aab57.csv`와 strict amp038 `submission_e108_if_e101win_strict_amp038_64514c53.csv`. E109는 반대쪽을 닫았다: tie/loss bucket에서는 E108 amp line이 E101보다 더 나빠지고, active-cell-only signal은 E95/E90/E86 retention 쪽이다. E110은 남은 쉬운 escape hatch도 닫았다: active-restored E89/E85와 non-active E89/E90/E86 graft `45`개 중 strict 후보가 `0`이라, E101 tie/loss가 full E89나 non-active graft 자동 fallback을 뜻하지 않는다. E111은 이 전체를 SAUNA 관찰로 압축했다: E72 실패는 Q-share `0.450788`의 broad all-target movement였고, E95 성공은 S-share `0.980052`의 target-axis surgery다. 따라서 현재 다음 public sensor는 여전히 `submission_e101_q2s3tail_177569bc.csv`이고, E108은 E101이 edge/small scale로 이긴 뒤에만 쓰는 조건부 후속이며, E101 tie/loss면 같은 line amplify도, 단순 non-active tail fallback도 하지 않는다.
