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

## Current Decision

가장 저비용으로 많은 가설을 가르는 실험은 E05 selector-only/pairwise-order falsification이었다. 결과는 "micro-refine을 더 많이 만들기보다 selector resolution 또는 large safe representation move가 필요하다"로 수렴한다.

E10 이후 결론은 더 좁아졌다. label-flow/block-rate는 "환상"은 아니지만, 현재 후보들이 a2c8/raw05 public-risk gate를 넘지 못하므로 제출 후보가 아니라 high-confidence gate/energy로만 써야 한다.

E11 이후 결론은 한 단계 더 좁아졌다. semantic label-flow를 dependency-energy/raw05 gate로 제한하면 conflict 없는 control/probe 후보는 만들 수 있지만, strict submit 후보는 여전히 0개다. 병목은 이제 "representation 존재 여부"보다 "selector noise를 넘는 크기의 안전한 probability translation"으로 이동했다.

E12-E14 이후에는 "안전한 probability translation"이 처음으로 구체화됐지만, E15-E19가 그 해석을 좁혔다. S4+Q3 gated atom 조합은 strict pairwise submit gate를 통과했지만 독립 hidden-subset selector에서는 survival 0개였고, pairwise 내부도 만장일치가 아니라 favorable scenario tail에 의존했다. E17은 기존 candidate universe 안에 이 방향을 독립적으로 지지하는 S4/Q3 anchor가 없음을 확인했다. E18-E19는 로컬 OOF archive도 그 anchor가 아님을 보였다. E20은 block/measurement archive도 missing large safe movement가 아님을 보였다. E21은 pair-only와 old-only support가 구조적으로 갈라지고 two-selector majority cell이 비어 있음을 확인했다. E22는 old-only 쪽이 이미 raw05 public observation에 의해 약화됐고, 당시 다음 public sensor를 쓴다면 pair-only S4/Q3가 가장 정보량 높다는 결론을 냈다. E23은 그 sensor를 축소해도 two-selector majority가 생기지 않는다는 것을 보였고, E24는 subject/date/block/energy localization도 conflict를 해결하지 못한다는 것을 보였다. E25는 별도의 큰 움직임 mixmin/direns/sparse branch도 pairwise/old strict gate를 통과하지 못한다는 것을 보였다. E26은 known public LB 역문제 자체도 후보 sign을 결정하지 못할 만큼 underidentified임을 보였고, E27은 train global prior와 subject-target prior를 추가해도 그 ambiguity가 사라지지 않음을 보였다. E28은 binary hidden-label 제약이 일부 anchor fit realism을 높이지만, 아직 current candidate sign을 안정적으로 결정하지 못함을 보였다. E29는 binary world pool이 pair-only S4/Q3보다 mixmin/inverse7을 더 지지할 가능성을 보였지만 frontier-scale world가 1개뿐이라 submit gate는 열지 않았다. E30은 frontier-box 안의 binary worlds가 다수 존재하고 non-candidate objectives에서는 mixmin/inverse7을 강하게 지지한다는 것을 보였지만, adverse candidate-objective worlds도 가능해서 strict gate는 여전히 닫혀 있다. E31은 그 adverse worlds가 train label geometry상 오히려 가장 plausible하다는 것을 보여, generic plausibility gate로는 mixmin을 검증할 수 없다고 결론냈다. E32는 같은 adverse worlds가 known-anchor loss attribution geometry에서는 high-energy라는 점을 보여 mixmin/inverse7 probe 근거를 다시 강화했고, E33은 그 geometry가 특정 anchor 하나에 의존하지 않음을 보였다. E34는 이 신호가 medium non-JEPA anchors와 broad loss/cancellation geometry에 의해 유지되고, exact target-axis semantics에는 덜 의존한다는 점을 밝혔다. E35는 이 신호가 normal-submit certification으로는 부족함을 분리해 냈다. E36은 raw observed structure까지 추가해 mixmin certification을 더 약화시켰다: mixmin은 raw pseudo-label support가 `5/10`이고 mean delta가 positive인 반면, inverse7은 `10/10` source에서 개선됐다. E37은 inverse7/mixmin scale-blend bridge도 strict gate를 만들지 못함을 보였다: raw gate는 14개, anchor gate는 22개였지만 two-selector majority와 bridge gate는 모두 0개였다. E38은 이 상태를 후보 제출 문제가 아니라 worldview sensor 선택 문제로 재정의했다. 10개 후보 중 normal submit은 `0`, public sensor는 `10`이며, 정보량 기준으로 mixmin이 top anchor-loss worldview sensor, inverse7/full-scale branch가 raw+anchor bridge sensor, S4/Q3 pair files가 selector-disambiguation sensor다. E39는 독립 selector calibration 후보였던 OOF archive도 normal ranker가 아님을 보였다: OOF sign은 known public과 맞지만 stage2/ordinal public 순서를 거꾸로 고른다. E40은 test movement fingerprint가 stage2/ordinal 순서를 맞히고 inverse7_s0p25를 가장 raw05-like한 sensor로 보는 단서를 줬지만, bad JEPA severity와 A2C8 leave-one-out best 조건을 놓쳐 strict selector는 0개였다. E41은 여기에 bad-axis geometry를 직접 추가해도 strict/loose selector가 0개임을 보였다. `axis_group`은 bad-anchor severity를 일부 복구하지만 A2C8 LOO를 심하게 실패하고, named-axis는 rank/ordering을 망가뜨린다. E42는 A2C8를 fixed zero anchor로 고정해도 usable gate가 0개임을 보여, A2C8 LOO harshness가 핵심 병목이 아니라 frontier-resolution collapse가 핵심 병목임을 확인했다. E43은 이 해상도 병목을 전 selector family로 확장해 검증했고, selector frontier-resolution gate와 error-margin-certified 후보가 모두 0개임을 보였다. E44는 기존 scored universe 안에 selector error를 넘는 큰 안전 후보도 없음을 보였다. E45는 public subset이 단순한 subject/order/date/raw-domain mask라면 selector target으로 쓸 수 있다는 가설도 반증했다. E46은 이 모든 결과를 block-state 관점에서 재정렬했다: 0.54 자체는 block-rate oracle `0.517878`로 가능하지만, subject identity는 oracle gap의 `0.291286`만 설명하고 Markov/endpoint/threshold/public-mask는 숨은 block-rate vector를 복원하지 못한다. E47은 현재 fold-safe block summary views도 직접 테스트했고, best row blend는 `-0.001505`였지만 block-rate loss는 temporal보다 `0.012440` 나빠졌다. 따라서 현재 후보는 개선 우선순위가 아니라 selector conflict 또는 selector 선택 자체를 설명하는 센서다. 정상 제출 후보는 아직 없다.

E48-E68 이후에는 기준점이 바뀌었다. Mixmin은 previous best를 `0.0011326805` 이겼고, E49는 그 움직임이 단순 global/subject/recent prior correction으로 설명되지 않으며 subject-calendar hidden test block과 더 잘 맞는다는 관찰을 남겼다. E50은 그 관찰을 바로 selector로 쓰는 시도를 반증했다: best subject-calendar selector도 mixmin을 public-best로 예측하지 못했다. E51은 anchor-loss/binary-world geometry를 결합해도 같은 selector 변환이 실패함을 보였다. E52는 방향을 바꿔 mixmin을 관측 constraint로 놓고 기존 후보들의 sign을 테스트했지만, 158개 후보 중 strict/loose better-than-mixmin은 `0`이었다. E53은 남은 calendar-flank block-rate/count branch의 가장 단순한 count-state posterior를 찔렀다. Local/same-subject donor는 pseudo-hidden에서 `-0.005266` 개선됐지만 strict donor는 `+0.001434` 나빠졌고, 실제 hidden alignment도 strict 기준 `-0.000179`로 약했다. E54는 raw overnight context를 추가하면 strict pseudo-hidden block-state recovery가 강하게 살아난다는 점을 보였다(`-0.007733`). 그러나 그 latent는 mixmin-public latent가 아니었다. Best raw strict method는 실제 hidden mixmin alignment를 `+0.000311`로 악화시켰고 S3도 pseudo-hidden에서 adverse였다. E55는 이 conflict가 단순 Q/S target-dependency projection으로 고쳐지는지 찔렀고, joint gate `0/225`로 반증했다. E56은 mixmin을 hard constraint로 넣은 새 binary-world family를 실제로 만들었고, world-LOO posterior gate `12`개를 열었다. 하지만 E57은 그 posterior를 직접 제출하는 가설을 반증했다: joint safety gate는 `0`, 가장 안전한 posterior도 actual-anchor에서 mixmin보다 `+0.000123` 나빴고, E56 selected candidate는 `+0.020381`로 크게 나빴다. E58은 단순 distillation을 시도했지만 submission margin gate는 `0`이었고, E61은 그 결론이 scoring-index artifact가 아님을 확인했다. E59는 within-block joint label-pattern representation을 찔렀고, joint 구조 자체는 강하게 살아났지만 row calibration과 hidden mixmin sign으로 번역되지 않았다. E60은 transition residual이 hidden sign 센서로는 더 강하지만 row calibration을 완전히 깨뜨린다는 점을 보였다. E62는 transition residual을 target이 아니라 E56 gate로만 써도 selector-scale margin이 생기지 않는다는 점을 보였다. E63은 독립 hidden-rate gradient consensus가 E56 방향 자체를 강하게 지지하지만, 그 방향도 아직 public-anchor margin으로 번역되지 않는다는 점을 보였다. E64는 그 방향을 더 크게 키우면 된다는 단순 amplitude 가설을 반증했다. E65는 near-zero targetwise pocket이 존재하지만 여전히 sub-margin임을 보였다. E66은 그 pocket이 Q2/S3 hidden-direction 오류 때문이라는 단순 해석을 반증했다. E67은 first-order anchor-tail gate가 matched `no_q2_s3`보다 낫다는 점을 보였지만, 최고 `-6.933e-6`로 여전히 margin을 넘지 못했다. E68은 그 tail-gated Q2/S3 cell이 known-anchor derivative 밖에서도 살아남는지 찔렀고, held-out combo construction plus hidden/world/block stress에서 independent/strict gate `155/540`을 확인했다. 그러므로 다음 질문은 "a2c8보다 조금 나은 micro-edge가 있나"도 아니고 "calendar/anchor features로 kNN ranker를 만들 수 있나"도 아니며, "기존 bridge 후보가 mixmin을 대체하나"도 아니고, "simple calendar-flank/raw/target-dependency posterior가 바로 후보인가"도 아니고, "mixmin-hard posterior를 그냥 평균내면 되나"도 아니고, "E56 posterior를 단순 gate로 잘라내면 되나"도 아니고, "joint pattern labels나 transition residual만 예측하면 되나"도 아니고, "transition residual을 E56 gate로 쓰면 되나"도 아니며, "hidden-rate gradient agreement나 scalar/near-zero line search만으로 제출 가능해지나"도 아니고, "E67이 단순 anchor-tail artifact인가"도 아니다. 질문은 "독립 검증된 Q2/S3 cell을 어떻게 tail/block calibration을 잃지 않고 margin-scale amplitude나 structural target으로 바꾸는가"다.
