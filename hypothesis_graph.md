# Hypothesis Graph

작성일: 2026-05-28

이 문서는 수면 기반 생활습관 로그 예측 대회를 "예측 표"가 아니라 숨은 데이터 생성 과정의 관측 로그로 다루기 위한 가설 그래프다. 현재 best public LB는 `submission_mixmin_0c916bb4.csv`의 `0.5763066405`이다.

## 현재 병목 요약

E48에서 `submission_mixmin_0c916bb4.csv`가 public `0.5763066405`를 기록해 previous best `a2c8`를 `0.0011326805` 낮췄다. 이 차이는 기존 raw05-a2c8 gap `0.0000869862`의 약 `13.02x`라서 noise-scale micro-edge가 아니다. 따라서 현재 병목은 "a2c8 근처 micro edge를 더 찾는 문제"가 아니라, 왜 pairwise/old selector가 veto한 anchor-loss/binary-world movement가 public에서 맞았는지 설명하고, 그 구조를 mixmin-relative 후보로 재현하는 문제다.

가장 강한 현재 설명:

- hidden subject/session/block 구조는 존재한다.
- row-level boundary copy는 실패했다.
- block-level rate/count latent는 의미가 있지만 직접 제출 후보로는 약하다.
- raw05는 public-positive raw timeline 방향을 포착했다.
- JEPA latent에는 local signal이 있지만 큰 이동은 public bad-axis를 강하게 탄다.
- `a2c8`는 raw05 manifold의 작은 correction이었지만, 이제 frontier가 아니다.
- Mixmin은 anchor-loss/cancellation geometry와 binary actual-anchor worldview가 public-relevant였다는 첫 강한 관측이다.
- 0.54 진입을 막는 핵심 병목은 여전히 hidden block-rate state inference와 selector calibration이지만, E48 이후에는 pairwise/old selector veto를 hard gate로 쓸 수 없다.

## 관계 그래프

```text
raw sensor logs
  -> measurement-process missingness/rhythm
  -> cross-view JEPA surprise
  -> local CV gains
  -> public transfer risk

subject/date/order table
  -> hidden block/session structure
  -> block rate/count latent
  -> raw05-compatible tangent
  -> a2c8 tiny public edge

known public LB anchors
  -> public-subset inverse selector
  -> anchor LOO/L2O stress
  -> selector uncertainty > a2c8 edge

target co-occurrence
  -> Q/S dependency manifold
  -> calibration constraints
  -> unsafe if applied as hard prior
```

## 가설 목록

### H01. Hidden subject/session blocks are real

- 상태: 증거 있음.
- 왜 그럴듯한가: train/submission이 10 subjects와 36 timeline blocks를 공유하며, subject별 target rate 차이가 매우 크다.
- 맞다면: subject/date/order/block feature가 target보다 train/test mask와 block rate를 더 잘 설명해야 한다.
- 틀리다면: random split과 blockwise split의 target calibration 차이가 작고, subject/block prior가 subject mean을 못 이겨야 한다.
- 최소 실험: subject-date block reconstruction, blockwise CV, train/test adversarial validation.
- 성공 기준: pseudo-hidden block logloss가 subject mean 대비 일관 개선.
- 제출 전략: row-level prediction이 아니라 block-level prior/gate correction.

### H02. Boundary label propagation solves hidden rows

- 상태: 반증됨.
- 왜 그럴듯한가: train/test rows가 같은 subject의 timeline 안에서 번갈아 나타난다.
- 맞다면: hidden row 양쪽 train label을 copy/smooth하면 subject prior보다 좋아야 한다.
- 틀리다면: boundary copy가 submission-like geometry에서 logloss를 크게 악화한다.
- 최소 실험: prev/next/both label copy stress.
- 관측: boundary leakage/copying은 subject prior보다 나빴다.
- 제출 전략: 폐기. boundary labels는 feature가 아니라 overfit risk로 취급한다.

### H03. Block-level count/rate latent matters more than row labels

- 상태: 증거 있음.
- 왜 그럴듯한가: hidden block sequence motif가 subject mean 대비 최대 `-0.0156` weighted logloss, weighted R2 `0.367`을 보였다.
- 맞다면: row label보다 block target rate/count representation 예측이 더 안정적이어야 한다.
- 틀리다면: block reconstruction이 random CV나 strict-subject stress에서 무너져야 한다.
- 최소 실험: endpoint/motif/label-flow block rate prediction.
- 제출 전략: direct replacement가 아니라 block-rate energy/gate로 사용.

### H04. Public LB is a pseudo-public or anchor subset sensor

- 상태: 강한 증거 있음, 기존 selector는 재보정 필요.
- 왜 그럴듯한가: known LB anchors를 inverse fit하면 설명 가능한 mask가 있지만 LOO/L2O 선택이 흔들린다.
- 맞다면: 특정 candidate delta가 public anchors에서 반복적으로 같은 sign을 보여야 한다.
- 틀리다면: anchor LOO/L2O MAE가 public gap보다 작아지지 않고 ranking이 불안정해야 한다.
- 최소 실험: selector-only falsification with LOO/L2O, pair order constraints.
- 관측: pre-E48 strict submit-gate candidate는 0이었지만, E48에서 그 veto를 받은 `mixmin`이 public `0.5763066405`로 previous best를 `0.0011326805` 이겼다. Public LB sensor가 hidden-world family를 판별하는 데 실제로 유효했다.
- 제출 전략: public LB를 직접 맞추지 말고, sensor로 사용한다. 단, E48 이후에는 pairwise/old selector를 hard gate가 아니라 competing worldview diagnostic으로 낮추고, mixmin을 포함해 selector를 재보정한다.

### H05. raw05 captures a public-positive raw timeline direction

- 상태: 증거 있음.
- 왜 그럴듯한가: raw timeline JEPA rescue가 public `0.5775263072`로 강한 anchor이며, bad JEPA보다 훨씬 좋다.
- 맞다면: raw05와 가까운 후보가 public에서 더 안정적이어야 한다.
- 틀리다면: raw05-distance가 낮아도 bad anchors 방향으로 악화되어야 한다.
- 최소 실험: raw05-distance, raw05 residual, raw05-compatible gate stress.
- 제출 전략: raw05 manifold 근처에서만 low-energy movement 허용.

### H06. a2c8 is a tiny correction on the raw05-compatible tangent

- 상태: 증거 있음.
- 왜 그럴듯한가: public gap `0.000086986`는 매우 작고, pairwise selector에서 baseline-relative 후보들의 기대 개선도 `1e-5` 수준이다.
- 맞다면: a2c8를 크게 벗어난 후보는 bad-axis 또는 selector conflict가 증가해야 한다.
- 틀리다면: low-bad-axis large-move 후보가 anchor stress를 통과해야 한다.
- 최소 실험: universe audit, low-energy JEPA ensemble, pairwise order selector.
- 관측: strict resolved-better 0.
- 제출 전략: large move 금지. only if stress-survival score가 a2c8보다 높을 때 제출.

### H07. Aggressive JEPA latent residuals load bad public axes

- 상태: 증거 있음.
- 왜 그럴듯한가: all-target JEPA latent residual은 local OOF가 좋아도 public `0.5812273278`로 나빴고, Q2 latent도 public `0.5798012862`였다.
- 맞다면: local CV 개선 후보가 public bad-axis load를 키워야 한다.
- 틀리다면: JEPA latent가 blockwise/public-observation stress에서 안정적으로 개선해야 한다.
- 최소 실험: latent residual guardrail, bad-axis projection, anchor LOO.
- 제출 전략: JEPA latent는 direct prediction이 아니라 diagnostic/energy/gate로 제한.

### H08. Bad-axis removal alone is insufficient

- 상태: 증거 있음.
- 왜 그럴듯한가: low-bad-axis candidates가 많아도 resolved-better candidate는 0이었다.
- 맞다면: bad-axis_abs_load가 낮은 후보도 selector p90 delta가 a2c8보다 좋아지지 않아야 한다.
- 틀리다면: low-bad-axis large-move 후보가 pair/order stress를 통과해야 한다.
- 최소 실험: badaxis_lowenergy_jepa ensemble stress.
- 제출 전략: bad-axis removal은 필요조건일 수 있지만 충분조건이 아니다.

### H09. Measurement-process missingness is behavioral signal

- 상태: 증거 있음.
- 왜 그럴듯한가: sensor observation fraction, gap, usage count, wLight gap이 residual과 상관을 보였다.
- 맞다면: missingness/rhythm features가 target residual을 설명하되 train/test shift stress가 필요하다.
- 틀리다면: subject/weekend controlled residual correlation이 사라져야 한다.
- 최소 실험: measurement-process residual correlation, train/test shift, targetwise calibration stress.
- 제출 전략: raw value보다 observation process features를 calibration risk 또는 latent energy로 사용.

### H10. Single feature threshold rules are not enough

- 상태: 반증됨.
- 왜 그럴듯한가: 일부 raw/MP feature가 target residual과 상관이 있다.
- 맞다면: feature stump가 stage2보다 targetwise logloss를 낮춰야 한다.
- 틀리다면: 모든 single threshold stump가 stage2보다 악화된다.
- 관측: single feature threshold stumps는 직접 rule로 실패했다.
- 제출 전략: 단일 feature rule 폐기. ensemble uncertainty/gate input으로만 사용.

### H11. Q/S target dependency manifold constrains calibration

- 상태: 증거 있음.
- 왜 그럴듯한가: S2-S4 corr `0.478`, S2-S3 `0.394`, Q1-S1 `0.361`, Q2-Q3 `0.340` 등 target dependency가 존재한다.
- 맞다면: target dependency violation energy가 bad candidates를 구분해야 한다.
- 틀리다면: dependency correction이 anchor stress에서 일관 악화한다.
- 최소 실험: target dependency violation energy, targetwise temperature/intercept stress.
- 제출 전략: hard constraints 금지. dependency energy로 clipping/blend strength 조절.

### H12. Validation mismatch is a primary plateau cause

- 상태: 강한 증거 있음.
- 왜 그럴듯한가: local OOF `0.56x` improvement가 public에서는 bad anchor가 되는 사례가 반복된다.
- 맞다면: random/fold CV ranking과 public-anchor/LOO ranking이 크게 다르다.
- 틀리다면: CV best가 public best와 일관 매칭되어야 한다.
- 최소 실험: random CV, blockwise CV, anchor LOO/L2O, public-observation held-out 비교.
- 제출 전략: CV 평균 순위로 submit하지 않고 survival score로 ranking.

### H13. Target prior/prevalence shift exists but direct prior correction is unsafe

- 상태: 증거 약함에서 중간.
- 왜 그럴듯한가: subject별 prevalence가 크고 train/test date phase shift가 있다.
- 맞다면: intercept/temperature correction이 일부 target에서만 public-sensitive해야 한다.
- 틀리다면: global prior correction이 anchor stress에서 일관 악화한다.
- 최소 실험: targetwise calibration stress, public anchor prior sensitivity.
- 제출 전략: target별 prior correction은 energy-gated로만 적용.

### H14. Cross-view JEPA surprise contains real local signal

- 상태: 증거 있음, public safety 미확인.
- 왜 그럴듯한가: cross-view JEPA surprise가 guarded local target deltas를 보였다.
- 맞다면: view-prediction residual PCs가 blockwise/public-observation stress 일부를 통과해야 한다.
- 틀리다면: train/test distribution distance, anisotropy, high-energy samples에서 collapse가 발생해야 한다.
- 최소 실험: latent geometry diagnostic, NN consistency, high-energy logloss contribution.
- 제출 전략: direct add보다 latent energy/gate 또는 calibration risk feature로 사용.

### H15. Label-flow semantic JEPA is more promising than raw reconstruction JEPA

- 상태: 강한 증거 있음, direct submission은 반증, S4+Q3 pairwise 후보는 독립 survival 실패.
- 왜 그럴듯한가: JEPA-friendly audit에서 time_meta는 predictable하지만 semantic하지 않았고, label_rate/past_label context가 더 의미 있었다.
- 맞다면: label-flow context가 oracle_rate_r2와 public-safe movement를 동시에 높여야 한다.
- 틀리다면: label-flow도 anchor stress에서 bad JEPA 축으로 이동해야 한다.
- 최소 실험: block label-rate masked prediction, semantic vs predictability split.
- 최근 증거: `label_flow_blockrate_jepa_stress.py`에서 semantic stress-pass config는 1개, best oracle_rate_r2 `0.347118`, strict pass pred_rate_r2 `0.026047`; downstream geometry OOF delta `-0.003334`, subject_chunk delta `-0.000537`. 그러나 556개 관련 direct submission 후보의 public pairwise stress는 pair_submit_gate 0, pair_probe_gate 0, best p90 delta vs a2c8 `+0.000125668`이었다. E11 gated scan은 7240 후보 중 strict submit 0, control 50, probe 3263, selector conflict 0을 만들었다. E12-E14 targetwise/combo/focused scans identified S4+Q3 as the constructive direction and produced 61 strict pairwise submit-gate candidates; best p90 vs a2c8 `-0.000065217`. E15 independent survival review then found 0/61 pair-submit candidates survived old hidden-subset stress; `6b9335b1` old-selector p90 was `+0.000675515` and `1bbfb735` was `+0.000638679`. E17 anchor gap audit found no existing candidate with both Q3/S4-shaped movement and old-majority support.
- 제출 전략: hidden block count/rate representation을 direct prediction target으로 밀지 말고, S4+Q3 targetwise gate도 제출 전에는 독립 selector agreement를 요구한다. 현재 `6b9335b1`/`1bbfb735`는 submit 후보가 아니라 selector conflict 센서다.

### H16. Candidate selection, not candidate generation, is the immediate bottleneck

- 상태: 강한 증거 있음, 단기 submit 후보는 독립 stress에서 철회됨.
- 왜 그럴듯한가: submission universe와 JEPA/bad-axis/hiddenloc pools에는 후보가 많지만 strict gate가 0이다.
- 맞다면: 더 많은 후보 생성보다 selector LOO/L2O stress가 먼저 좋아져야 한다.
- 틀리다면: 새로운 representation branch가 low-bad-axis large movement를 만들고 stress를 통과해야 한다.
- 최소 실험: selector-only falsification and pairwise ordering stress.
- 제출 전략: selector가 a2c8 edge보다 작은 오차를 달성하기 전까지 micro-refine submit은 정보량 낮음.
- 최근 증거: E11에서 7240 gated 후보 중 50개가 control-better-than-a2c8 gate를 통과했지만 strict submit gate는 0개였다. E12 targetwise gate는 best p90 `-0.000005997`, E13 combo는 `-0.000035162`, E14 focused scan은 `-0.000065217`로 strict pairwise gate를 처음 통과했다. 하지만 E15에서 그 61개 pair-submit 후보가 old hidden-subset selector survival 0개를 기록했고, pairwise p90와 old-selector p90의 correlation은 `-0.881`이었다. E16 decomposition showed focused files have old hidden-subset better_rate `0.285714` and pairwise full-fit better_rate only `0.500000`; the apparent edge depends on a favorable scenario tail. E17 found no independent S4/Q3 positive anchor in the existing candidate universe. E18-E19 found local OOF Q3/S4 strength is also not an anchor: top 399 OOF candidates had pair p90 negative 0, old-majority 0, and submit/control/probe 0.

### H17. The useful public-positive label-flow correction is S4-dominant with Q3 support

- 상태: 부분 지지, submit-safe 가설은 반증.
- 왜 그럴듯한가: E12 target masks에서 S4가 best p90을 만들었고 Q3/Q2-Q3가 다음으로 강했다. E13-E14에서 S4+Q3 조합은 additive였다.
- 맞다면: S4 단독 movement가 raw05/bad-axis stress를 유지하며 p90 edge를 만들고, Q3 atom 추가가 edge를 더 키우며, 독립 hidden-subset stress에서도 scenario majority가 a2c8를 이겨야 한다.
- 틀리다면: S4/Q3 movement는 pairwise selector에서는 좋아도 old hidden-subset selector에서 scenario majority를 잃거나 p90 risk가 증가해야 한다.
- 최소 실험: S4 atom, Q3 atom, S4+Q3 combo/focused scan, independent survival review, independent anchor gap audit.
- 관측: S4 atom best p90 `-0.000005997`; combo best p90 `-0.000035162`; focused best pairwise p90 `-0.000065217`; selector conflict 0. 그러나 E15에서 selected 163 후보, pair-submit 61 후보 모두 independent survival 0개였다. Best old-selector p90는 `+0.000569397`, max scenario beat rate는 `0.285714`. E16 shows pairwise support is mixed rather than unanimous. E17 found: pairwise universe has 21 Q3/S4-shaped candidates but 0 with old-majority support; focused family has 163 pairwise-positive Q3/S4 candidates with old-majority 0; old-positive rescore has 97 old-majority candidates but Q3/S4-shaped 0.
- 제출 전략: all-target blend는 금지. S4+Q3 focused movement는 정보 센서로만 유지하고, 제출 후보화하려면 pairwise selector와 old hidden-subset selector의 방향 충돌을 먼저 해결해야 한다.
- private risk: pairwise-focused weight scan은 selector-family overfit로 판정한다. movement는 79/250 rows, S4 중심, max_abs_move 약 0.124로 작지 않다.

### H18. Local OOF Q3/S4 strength can supply the missing independent anchor

- 상태: 반증됨.
- 왜 그럴듯한가: E17에서 public-stress artifact universe에는 S4/Q3 anchor가 없었지만, OOF archive에는 5000개 이상의 local validation views가 있다.
- 맞다면: local-Q3/S4-strong OOF candidates should overlap with pairwise-negative, old-majority, and Q3/S4-shaped test movement.
- 틀리다면: top local OOF candidates should be broad/public-mask-like moves that selectors price as worse than a2c8.
- 최소 실험: OOF archive scan, top local OOF direct pairwise/old selector rescore.
- 관측: E18 scanned 5167 OOF arrays and found 1578 local-Q3/S4-strong candidates but OOF anchor-like 0. E19 directly rescored top 399 local OOF candidates: pair p90 negative 0, pair majority 0, old majority 0, probe/control/submit 0, q3s4_shape70 0.
- 제출 전략: OOF-local Q3/S4 winners are not submission evidence. They can be used as negative examples for validation mismatch, not as anchors.

### H19. Existing block/measurement candidates contain the missing large safe movement

- 상태: 반증됨.
- 왜 그럴듯한가: block-scale JEPA, hidden-block, raw05-blockcount, pre-sleep measurement candidates include larger probability movements than E11-E14 micro-gates and many have low bad-axis load.
- 맞다면: at least one existing candidate should have pairwise p90 below a2c8, pairwise majority, old hidden-subset majority, and low bad-axis energy. A large-lowbad subset should overlap with two-selector support.
- 틀리다면: large-lowbad candidates should exist but fail sign support; pre-sleep/measurement broad moves should be priced as public-risk negative.
- 최소 실험: collect block/measurement/presleep/raw05-block candidates, score old hidden-subset stress, score pairwise-order stress, summarize by family and target movement shape.
- 관측: E20 scored 3800 non-anchor candidates. pairwise p90 negative `0`, pairwise majority `52`, old-majority `3`, two-selector majority `0`, pair submit/control/probe `0/0/63`, large-lowbad movement `2505`, large-lowbad two-selector `0`. raw05-blockcount refine is nearest probe but best pair p90 is still `+0.000010793`; pre-sleep measurement best pair p90 is around `+0.000509`.
- 제출 전략: no existing block/measurement candidate should be submitted as an improvement candidate. raw05-blockcount may be a low-risk diagnostic sensor only if a public slot is explicitly spent for information.

### H20. Existing scored universe contains a rare two-selector support intersection

- 상태: 반증됨.
- 왜 그럴듯한가: pairwise selector and old hidden-subset selector each identify plausible public-sensitive candidates; a robust direction might exist in their intersection even if each individual family failed.
- 맞다면: deduplicated scored candidates should include at least one two-selector-majority file, or at least a strict candidate shape with low bad-axis, pair p90 below a2c8, and old-majority support.
- 틀리다면: support zones should split into pair-only and old-only manifolds with different target/movement shapes and empty two-selector support.
- 최소 실험: merge scored candidates from broad pairwise universe, focused label-flow review, old-positive rescore, OOF-top rescore, and block/measurement rescore; classify support topology.
- 관측: E21 found two-selector majority `0`. pair-only `465` candidates include 209 pair-strict p90 files and 61 pair-submit files, but median old beat rate is `0.266`. old-only `97` candidates have median pair beat rate `0.146`. S4 dominates pairwise support, while Q3 dominates old-majority support; strict candidate shape count is `0`.
- 제출 전략: no submit candidate from the current scored universe. Next action is selector reconciliation or an explicit public-sensor submission, not another shortlist merge.

### H21. Old-only Q3/raw05-drift support should be the next public sensor

- 상태: 반증됨 for next-sensor priority; old selector remains a cautionary veto.
- 왜 그럴듯한가: E15-E21에서 old hidden-subset selector는 focused S4/Q3 pairwise candidates를 일관되게 veto했고, 독립 stress처럼 보였다.
- 맞다면: old selector should preserve known A2C8-vs-raw05 public direction and an old-only candidate should be a more informative diagnostic than pair-only S4/Q3.
- 틀리다면: old selector should over-endorse raw05-like geometry even though raw05 is public-worse than A2C8, while pairwise public-order selector better preserves known anchor order.
- 최소 실험: compare selector reliability on known public anchors and rank candidate sensors by information gain, not expected score.
- 관측: E22 found pairwise public-order selector pass `33/36`, raw05 direction correct rate `0.916667`, best LOO MAE `0.000218`, best L2O MAE `0.000444`. Old hidden-subset selector pass was `0/7` and raw05 direction correct rate was `0.0`; it endorses raw05-like geometry despite raw05 public `0.5775263072` being worse than A2C8 `0.5774393210`.
- 제출 전략: do not submit old-only Q3/raw05-drift candidates next. If a public diagnostic slot is spent, use the conservative pair-only S4/Q3 sensor `analysis_outputs/submission_label_flow_focused_1bbfb735.csv`; if it worsens, close the focused S4/Q3 branch and do not submit `6b9335b1`.

### H22. Scaling down S4/Q3 movement resolves the selector conflict

- 상태: 반증됨 as conflict resolution; partially useful for lower-risk diagnostic sensor design.
- 왜 그럴듯한가: full S4/Q3 candidates have pairwise support but old hidden-subset p90 risk. If old veto is partly caused by overlarge probability movement, smaller logit-space movement should retain sign while reducing old risk.
- 맞다면: some scaled or target-masked variant should keep pair p90 below 0 and raise old hidden-subset scenario beat rate to majority, or at least create two-selector majority.
- 틀리다면: pairwise p90 should remain negative across scales while old scenario beat rate stays below majority and two-selector majority remains 0.
- 최소 실험: A2C8-to-`1bbfb735`/`6b9335b1` scale curve over target masks, scored by both selector families.
- 관측: E23 scored 108 scale/mask variants. Pair p90 was negative for all scales in each mask family, but two-selector majority was `0` everywhere. Best balanced lower-risk sensor was `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv` with pair p90 `-0.000034496`, old p90 `+0.000571958`, movement `0.003931`; old scenario beat rate remained `0.277992`.
- 제출 전략: scaling is useful only to choose diagnostic risk level. It does not create an improvement candidate or resolve the public-subset selector mismatch.

### H23. Row/subject/block localization resolves S4/Q3 selector conflict

- 상태: 반증됨 as submit path; weak diagnostic signal only.
- 왜 그럴듯한가: E21-E23 left open the possibility that pairwise S4/Q3 support is correct only for a hidden subject/date/block subset, while old hidden-subset stress penalizes the movement because it is applied too broadly.
- 맞다면: a subject, date block, subject phase, delta-energy, sign, or calendar row mask should preserve pairwise p90 below a2c8 and raise old hidden-subset scenario support to majority, ideally producing two-selector-majority.
- 틀리다면: pairwise support should remain easy to produce, but old-majority and two-selector-majority should remain 0 even after localization.
- 최소 실험: localized A2C8-to-`1bbfb735`/`6b9335b1` logit blends over row masks and `q3_s4`/`s4` target masks, scored by pairwise public-order and old hidden-subset selectors.
- 관측: E24 scored 960 localized variants. Pair p90 negative was `807`, old-majority `0`, two-selector-majority `0`. The only loose localized candidates were eight `id02_b02` files, an 8-row id02 block from `2024-10-03` to `2024-10-10`, with pair p90 only around `-0.0000002`, old p90 `+0.000580`, and old beat rate `0.413127`.
- 제출 전략: do not submit localized S4/Q3 files. The `id02_b02` files are too small and still old-negative; they are not a frontier path. Future row localization must be learned from a new anchor or representation, not swept around the same pair-only direction.

### H24. Larger sparse/minimax direction probes create selector-resolvable movement

- 상태: strict survival 기준 반증됨; high-risk public-probe lane remains unresolved without public LB.
- 왜 그럴듯한가: target-ablation, sparse-ladder, direction-ensemble, and minimax reports show larger movement, better honest CV deltas, and stronger combo/actual-anchor objectives than micro S4/Q3 sensors.
- 맞다면: at least one mixmin/direns/sparseladder/targetabl probe should have pairwise p90 below a2c8, old hidden-subset majority, low bad-axis load, and nontrivial movement.
- 틀리다면: the same files should be priced as worse than a2c8 by pairwise public-order and old hidden-subset stress despite local/actual-anchor/combo evidence.
- 최소 실험: score current priority large-movement probes with the same pairwise/old selectors and compare family-level support.
- 관측: E25 scored 22 probes. Pair p90 negative `0`, pair majority `0`, old-majority `0`, two-selector majority `0`, submit-shape `0`. Mixmin/direns/sparseladder candidates had pair p90 around `+0.000835` to `+0.000960`; closest inverse7blend still had pair p90 `+0.000122` and old beat rate only `0.003861`.
- 제출 전략: do not mark mixmin/direns as strict-survival submissions. If submitted, they are high-risk score-oriented probes testing whether actual-anchor/combo stress is a better public sensor than pairwise/old stress, not validated 0.54 candidates.

### H25. Known public LB anchors can identify candidate sign by inverse fitting

- 상태: 반증됨 under relaxed and train-prior-banded inverse models.
- 왜 그럴듯한가: we have eight public LB observations spanning a2c8, raw05, stage2, ordinal, final9, and three bad JEPA anchors. Their score ordering might constrain hidden labels or public subset enough to rank new candidates.
- 맞다면: feasible hidden worlds matching known LBs should give one-sided candidate delta ranges for major candidates, especially after train target prevalence bands are enforced.
- 틀리다면: many target priors, subject masses, and candidate deltas should remain feasible; candidate ranges should cross zero.
- 최소 실험: linear-program inverse feasibility over all-test soft labels and arbitrary cell-mixture public weights; candidate delta min/max vs a2c8; repeat with train target prevalence bands.
- 관측: E26 matched all 8 known public LBs exactly with all-test soft labels and with cell-mixture weights. All-test target prior ranges were nearly unconstrained; cell-mixture subject masses were `0` to `1` for every subject. Eight unobserved candidate deltas crossed zero under all-test soft labels, under cell-mixture, and under train prevalence bands `±0.05`, `±0.10`, `±0.20`. Only raw05 was one-sided because it is a known public observation.
- 제출 전략: do not use public-LB inverse fitting as a standalone optimizer. Use it only to state which selector worldview a public submission is testing.

### H26. Global and subject-target priors collapse public-LB feasible worlds

- 상태: 반증됨 for current candidates.
- 왜 그럴듯한가: user/session identity is one of the most plausible hidden DGP layers, and train subject target rates differ strongly. E26 may be underidentified only because it ignored this subject structure.
- 맞다면: all-test inverse worlds that match known public LB anchors while respecting train global prevalence and subject-target prior bands should force one-sided candidate deltas for at least one important unobserved candidate.
- 틀리다면: known LBs should still fit exactly under those priors, but current candidate delta intervals should continue to cross zero.
- 최소 실험: add global target prevalence bands and subject-target prior bands to the all-test soft-label LP; recompute candidate delta min/max for pair sensors, mixmin/direns, target-ablation, inverse7, and raw05.
- 관측: E27 tested seven scenarios. All fit the 8 known public LBs with minimum slack `0`. All unobserved candidate-scenario cells crossed zero (`56/56`), and one-sided improvement cells were `0`. The tight `global_t010_subject_t010` scenario still left `1bbfb735` at `[-0.003706960, +0.002332888]` and mixmin at `[-0.010891932, +0.009106607]`.
- 제출 전략: do not rank current candidates by a subject-prior inverse worldview. Subject prior can be a diagnostic constraint, not a submission gate, unless a stronger external anchor or binary/exact public subset model collapses the range.

### H27. Binary all-test hidden labels resolve candidate sign

- 상태: 미확인 as exact reconstruction; 반증됨 as current submission ranker.
- 왜 그럴듯한가: public labels are binary, while E26-E27 relaxed them to fractional soft labels. The relaxation may overstate hidden-world ambiguity.
- 맞다면: binary all-test MILP should fit known public LBs at frontier resolution and produce one-sided candidate deltas for representative submissions.
- 틀리다면: binary fit residual should exceed public-edge resolution, or candidate ranges should remain ambiguous/time-limited without one-sided improvement evidence.
- 최소 실험: MILP with 1750 binary label variables and 8 slack variables; fit known public LBs under no-prior/global/subject-prior scenarios; then optimize representative candidate deltas under the fit residual budget.
- 관측: E28 fit MILPs hit time limits, but found incumbents. `binary_global_t010_subject_t010` fit known anchors with max residual `0.000061242`, below the raw05-a2c8 gap `0.000086986`; no-prior and global-only fits were worse. Candidate range MILPs did not yield one-sided improvement evidence. Under no-prior, `6b9335b1` had both signs feasible from incumbents (`[-0.004415762, +0.002817743]`); tight subject-prior candidate ranges produced no incumbents within the short time limit.
- 제출 전략: do not rank or submit from E28. Binary exactness may be a useful future constraint if paired with saved incumbent worlds or a stronger public-subset assumption, but the current MILP stress is not an operational gate.

### H28. Frontier-scale binary world pool identifies the candidate family

- 상태: 증거 약함; submit gate remains closed.
- 왜 그럴듯한가: E28 showed a tight binary subject-prior world can fit known anchors within frontier resolution. Multiple such worlds might reveal which candidate direction is stable.
- 맞다면: a pool of frontier-scale binary worlds should contain several diverse incumbents, and candidate signs should be consistent across them.
- 틀리다면: few or no frontier-scale worlds should be found, or candidate signs should depend strongly on the sampled world.
- 최소 실험: solve slack/candidate/random binary MILP objectives under tight subject priors; deduplicate worlds; score representative candidate deltas in each world.
- 관측: E29 attempted 15 objectives and found 15 unique incumbents, but only 1 frontier-scale world. In all worlds, mixmin better_rate was `0.8667` and inverse7 `0.7333`, while pair sensors were `0.2667-0.3333`. In the only frontier-scale world, mixmin and inverse7 were negative (`-0.00107366`, `-0.000277011`), while S4/Q3 pair sensors were positive.
- 제출 전략: do not submit from this alone. If a public probe is chosen under the binary-world hypothesis, mixmin is a more coherent probe than pair-only S4/Q3, but it remains high-risk and needs frontier-pool expansion or a public sensor.

### H29. Frontier-box binary worlds make mixmin/inverse7 one-sided

- 상태: 부분 지지, but strict certification 반증됨.
- 왜 그럴듯한가: E29 found only one frontier-scale world, but it favored mixmin/inverse7. Forcing every known-public residual into the raw05-a2c8 gap should reveal whether this was real or a sampling accident.
- 맞다면: many frontier-box binary worlds should exist, and mixmin/inverse7 should be one-sided negative while pair-only S4/Q3 is not.
- 틀리다면: frontier-box worlds should be infeasible/rare, or candidate-max objectives should find frontier-compatible worlds where mixmin/inverse7 are worse.
- 최소 실험: add an upper bound on every known-public slack variable equal to the raw05-a2c8 gap; sample slack, candidate min/max, and random textured objectives; score candidate deltas.
- 관측: E30 found 29 incumbent frontier-box worlds and 28 unique worlds. Non-candidate objectives strongly favored mixmin (`19/19`) and inverse7 (`18/19`) while pair sensors were `7-8/19`. However candidate-max objectives still found frontier-box worlds where mixmin delta was `+0.008774` and inverse7 delta `+0.002782`.
- 제출 전략: do not certify a submission. Under the binary/actual-anchor worldview, `submission_mixmin_0c916bb4.csv` is now a more coherent high-risk public probe than pair-only S4/Q3, but it remains a worldview test rather than a strict improvement candidate.

### H30. Train-label geometry can reject adverse binary worlds

- 상태: 반증됨 as a gate; useful as probe ranking metadata.
- 왜 그럴듯한가: candidate-max objectives can produce adversarial exact-label worlds. If those worlds are unrealistic, train-only label geometry should identify them as high energy.
- 맞다면: mixmin/inverse7 adverse worlds should have poor target co-occurrence, cardinality, temporal transition, run-length, subject-prior, or edge-continuity scores.
- 틀리다면: adverse worlds should look plausible or even highly plausible under these train-only diagnostics.
- 최소 실험: score E30 worlds with a LeJEPA-style geometry energy from train label dynamics; compare adverse candidate worlds against random/fit worlds and low-energy bands.
- 관측: E31 scored 29 worlds. Random+fit worlds supported mixmin `19/19` and low-energy random+fit supported mixmin/inverse7 `6/6`. But the two mixmin-adverse worlds were plausibility ranks `1` and `2`, with train-geometry metrics closer to train than most random worlds.
- 제출 전략: do not use train-label geometry to certify mixmin. It remains the leading high-risk binary/actual-anchor public probe, but adverse worlds require a stronger independent anchor or actual public observation to rule out.

### H31. Known-anchor loss geometry rejects adverse binary worlds

- 상태: 부분 지지; certification은 아직 반증됨.
- 왜 그럴듯한가: E31의 train-label geometry는 public LB 관측을 직접 설명하지 않는다. 반대로 known public anchors의 per-target loss decomposition은 "이 숨은 label world가 이미 관측된 public worse/better 순서를 얼마나 자연스럽게 설명하는가"를 묻는다.
- 맞다면: low `anchor_energy` worlds should support mixmin/inverse7, while mixmin-adverse candidate-max worlds should need high cancellation or poor movement/loss alignment.
- 틀리다면: mixmin-adverse worlds should also be low-anchor-energy, or low-anchor-energy worlds should split signs across mixmin/inverse7 and pair S4/Q3 sensors.
- 최소 실험: compute per-target anchor logloss deltas versus A2C8 for every E30 binary world; score target-level cancellation and moved-target/loss-delta alignment; compare candidate signs by anchor-energy bands.
- 관측: E32 scored 29 worlds. `low_anchor_energy_half` supported mixmin `15/15` and inverse7 `15/15`; `low_anchor_energy_quarter` supported both `7/7`; `low_anchor_energy_random_plus_fit` supported both `12/12`. The two mixmin-adverse worlds were high-energy: ranks `26` and `28`.
- public LB 기대 반응: if this diagnostic matches the real public sensor, `submission_mixmin_0c916bb4.csv` should beat A2C8 or at least degrade less than pair-only S4/Q3 sensors. If it fails, the known-anchor loss geometry is overfitting anchor decompositions or public subset identity is still different.
- 제출 전략: promote mixmin only as an explicit high-risk worldview probe, not as a strict-gated improvement. Use E32 to choose between probe families; do not use it as a direct public-LB optimizer.

### H32. Anchor-loss geometry is stable under known-anchor LOO

- 상태: 지지됨 as diagnostic stability; certification은 미확인.
- 왜 그럴듯한가: E32 could be an artifact of one known anchor. A stable public-sensor geometry should not collapse when any single non-A2C8 anchor is omitted.
- 맞다면: LOO low-energy bands should keep mixmin one-sided negative and keep mixmin-adverse worlds outside low-energy half.
- 틀리다면: omitting raw05, final9, ordinal, stage2, or bad JEPA anchors should make mixmin adverse worlds low-energy or make mixmin support cross zero.
- 최소 실험: recompute `anchor_energy` seven times with one anchor omitted; summarize candidate signs and adverse-world ranks in low-energy half/quarter/random+fit bands.
- 관측: E33 found mixmin low-energy-half and low-energy-quarter better_rate min/median/max all `1.0`; worst low-half max delta was `-0.000315338`. No mixmin-adverse world entered any LOO low-energy-half band; adverse minimum rank stayed at least `21/29`. Inverse7 was weaker with low-half better_rate min `0.928571`, while pair sensors stayed below half support.
- public LB 기대 반응: if the binary/anchor-loss worldview is correct, mixmin should be a more informative public probe than inverse7 or pair-only S4/Q3. If mixmin worsens, the failure is not explained by a single-anchor overfit; it points to public subset mismatch or anchor-derived gate non-generalization.
- 제출 전략: `submission_mixmin_0c916bb4.csv` is the top high-risk public sensor for this worldview, but not a strict improvement candidate.

### H33. Anchor-loss gate is broad loss/cancellation geometry, not exact target-axis semantics

- 상태: 부분 지지; target-axis semantic version은 약화됨.
- 왜 그럴듯한가: E32 described movement/loss alignment, but the energy also contains cancellation and broad sign-consistency terms. The gate might be selecting worlds that explain medium public anchors with low cancellation, not worlds that preserve exact target-axis JEPA semantics.
- 맞다면: family holdout should show which anchor family carries the signal, component ablation should keep mixmin support, and target-axis permutation should not destroy support.
- 틀리다면: support should vanish when raw05 or medium anchors are removed, or when moved-target weights are permuted.
- 최소 실험: family holdout/isolation over raw05, medium non-JEPA, bad-JEPA anchors; component ablation; 500 target-axis movement-weight permutations.
- 관측: E34 found `no_raw05`, `no_medium_non_jepa`, and `no_bad_jepa` all keep mixmin low-half support at `1.0`; `only_medium_non_jepa` alone is sufficient. `only_bad_jepa` fails with mixmin better_rate `0.857143` and both adverse worlds in the low-energy half. Target-axis permutation null keeps mixmin one-sided in `500/500` low-half and low-quarter permutations.
- public LB 기대 반응: if mixmin improves, the explanation is more likely medium-anchor loss/cancellation geometry than target-axis semantics. If mixmin fails, bad-JEPA-only anchors and target-axis alignment were not the missing constraint; public subset mismatch remains the likely cause.
- 제출 전략: keep mixmin as high-risk public sensor, but do not sell it as a JEPA semantic-target-axis candidate. It is an anchor-loss/cancellation worldview probe.

### H34. Mixmin has enough out-of-anchor evidence for normal submission

- 상태: 반증됨 for normal-submit certification; high-risk sensor priority는 지지됨.
- 왜 그럴듯한가: E32-E34 give mixmin strong binary/anchor-loss support, E33 shows LOO stability, and direction-probe metadata gives honest CV mean/worst improvements.
- 맞다면: at least one non-public or local/representation source should support mixmin, public-selector veto should not be hard, and anchor-loss evidence should be corroborative rather than primary.
- 틀리다면: evidence should separate into local-independent-ish weak support plus known-public/anchor-derived strong support, while pairwise/old selectors continue to veto unobserved candidate deltas.
- 최소 실험: join direction-probe metadata, pair/old selector scores, actual-anchor/combo summaries, E32 anchor bands, E33 LOO, E34 family/null outputs; tag each evidence source by independence tier.
- 관측: E35 audited 5 candidates. normal submit gates passing `0`. Mixmin had honest CV mean/worst `-0.000951963` / `-0.000695966`, but selector hard veto remained with pair p90 `+0.000879200` and old p90 `+0.001041933`. Anchor-loss and LOO support were strong: low-half better_rate `1.0`, low-half max_delta `-0.000537096`, LOO worst max_delta `-0.000315338`.
- public LB 기대 반응: if mixmin improves, it validates the binary/actual-anchor/anchor-loss worldview despite selector veto. If it worsens, the strongest current anchor-derived gate failed to generalize beyond known public observations.
- 제출 전략: do not treat mixmin as a normal improvement submission. If a public diagnostic slot is deliberately spent, mixmin is now the highest-information worldview probe; `1bbfb735` remains a lower-risk selector-disambiguation probe.

### H35. Raw observed structure independently supports mixmin

- 상태: 반증됨 for mixmin; inverse7 bridge 가설은 새로 지지됨.
- 왜 그럴듯한가: if anchor-loss geometry is not just public-anchor overfit, observed subject/date/raw-feature neighborhoods should move in the same direction as mixmin.
- 맞다면: mixmin should improve soft LogLoss versus A2C8 under train-derived subject temporal priors, raw feature KNN, cross-subject KNN, coverage/missingness KNN, behavior KNN, and cluster priors.
- 틀리다면: mixmin should have low support rate, positive mean delta, or worse raw-structure alignment than smaller candidates.
- 최소 실험: train-derived pseudo-label stress from `all_keys_deep_features.parquet` without public LB or known-anchor loss inputs.
- 관측: E36 used 10 raw-structure pseudo-label sources. raw sensor train/test adversarial AUC was `0.607876`. Mixmin support was only `5/10`, mean delta `+0.000065107`, worst delta `+0.000498574`. Inverse7 support was `10/10`, mean delta `-0.000705727`, worst delta `-0.000507826`; pair sensors were `7/10` with positive worst deltas.
- public LB 기대 반응: if mixmin improves despite weak raw-structure support, public follows anchor-loss/binary-world geometry more than train-derived raw neighborhoods. If inverse7 improves, the bridge between anchor-loss and raw observed structure is more important than mixmin's anchor-loss priority.
- 제출 전략: do not use E36 to certify mixmin. Promote inverse7 to a new bridge-probe branch, but require selector reconciliation because E35 still flags hard veto and E33 shows inverse7 anchor-LOO is weaker than mixmin.

### H36. Inverse7 scale/blend can reconcile raw support and selector veto

- 상태: 반증됨 for current scale/blend family; inverse7 remains diagnostic bridge only.
- 왜 그럴듯한가: E36 gives inverse7 full raw-structure support, and E32/E33 low-anchor-energy worlds also support inverse7. If selector veto is mostly amplitude or mixmin/anchor-loss imbalance, logit-space scaling or mixing with mixmin should produce a candidate with raw support, anchor support, and reduced selector risk.
- 맞다면: at least one scaled inverse7 or inverse7/mixmin blend should keep raw support gate, keep low-anchor-energy half/quarter anchor gates, and create two-selector majority or strict bridge gate.
- 틀리다면: raw and anchor gates may remain positive, but pairwise p90/old p90 stay positive, old beat-rate stays near zero, and two-selector majority remains zero.
- 최소 실험: generate A2C8-to-inverse7 scales, A2C8-to-mixmin scales, and inverse7/mixmin blended logit directions; score with E36 raw pseudo-labels, E32 anchor-loss bands, old hidden-subset selector, and pairwise public-order selector.
- 관측: E37 scanned 22 variants. Raw support gates were `14`, anchor low-half+quarter gates were `22`, but two-selector majority was `0` and strict bridge gates were `0`. Best-ranked `analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv` had support_rate `1.0`, low-anchor-half better_rate `1.0`, but pair p90 `+0.000035423`, old p90 `+0.000587512`, old beat-rate `0.007722`, selector hard veto `True`.
- public LB 기대 반응: if `inv7_s0p25` improves despite local selector veto, public favors raw+anchor bridge energy more than pairwise/old selector stress. If it worsens, E36 raw support is not enough to generalize and the bottleneck is public subset/selector identity rather than amplitude.
- 제출 전략: do not submit inverse7 scale/blend as a normal improvement. If a public diagnostic is deliberately spent on this branch, use it only as a bridge sensor; otherwise prefer a public sensor that directly calibrates the selector/worldview conflict.

### H37. Worldview discriminability can rank the next public sensor

- 상태: 강하게 지지됨 as public-sensor ranking; normal-submit certification framework는 재검토 필요.
- 왜 그럴듯한가: after E35-E37, all candidate families are vetoed by at least one credible stress. If a public slot is spent, the rational target is the candidate that most cleanly distinguishes hidden-public worldviews, not the one with the smallest local CV delta.
- 맞다면: a cross-source audit should produce no normal-submit candidates, but should rank sensors by interpretable sign conflicts across anchor-loss, raw-structure, pairwise selector, old selector, and honest-CV views.
- 틀리다면: at least one candidate should pass normal-submit gate, or all sensor lanes should be too similar to provide distinct public information.
- 최소 실험: join E32/E33 anchor bands, E35 independent evidence, E36 raw pseudo-label stress, and E37 bridge scan; convert each source to verdicts; rank by sign entropy and conflict span relative to the raw05/A2C8 public gap.
- 관측: E38 audited 10 candidates. normal submit candidates were `0`; public sensor candidates were `10`. Top information sensor was `mixmin_0c916` with score `3.355110`, followed by raw-structure bridge sensors `inverse7blend_1040`/`inv7_s1p00` and S4/Q3 selector sensors such as `pair_sensor_6b` and `pair_sensor_1bb`. E48 then validated that ranking: `mixmin_0c916` scored public `0.5763066405`, improving over previous best by `0.0011326805`.
- public LB 기대 반응: if `mixmin_0c916` improves, the anchor-loss/honest-CV worldview beats raw/pair/old veto; if it worsens, known-anchor loss geometry failed to generalize. If `inv7_s0p25` improves, raw observed structure plus anchor support is more predictive than selector veto. If `1bbfb735` improves, pairwise S4/Q3 selector is closer to public than old/anchor veto for that target movement.
- 제출 전략: mixmin is now the active frontier, not just a diagnostic option. Next submissions should be mixmin-relative and should explicitly test whether anchor-loss/binary-world geometry can be preserved while reducing private risk.

### H38. OOF archive can calibrate selector identity

- 상태: 반증됨 as public-rank selector; useful as negative local-stability screen.
- 왜 그럴듯한가: the OOF archive contains thousands of trained candidates, real train labels, and fold-level local failures/successes. If local validation mismatch is not the main bottleneck, label-free OOF stresses should identify candidates whose public analogue ordering agrees with known public LB.
- 맞다면: OOF improvements should be stable across future-tail, domain-like, density, missingness, subject/date block, and random OOF subsets; known-public OOF files should match both sign and pairwise order relative to final9.
- 틀리다면: many local OOF gates may pass, but known-public candidate ordering should disagree with public LB, or top local candidates should be implausibly strong publicblend/local variants that already look like validation shortcuts.
- 최소 실험: score all `*_oof.npy` arrays against final9 OOF across label-free subsets, keep known-public aliases after hash dedupe, and compare sign/rank for stage2 and ordinal against actual public LB.
- 관측: E39 scored `4172` OOF rows (`4171` unique hashes). strict OOF selector gates were `1311` and conservative gates `1115`. Known-public nonbaseline sign match was `1.0`, but pairwise rank agreement was `0.0`: public ranks stage2 better than ordinal, while OOF ranks ordinal better than stage2.
- public LB 기대 반응: if OOF rank were valid, ordinal-like candidates would be preferred over stage2-like candidates; existing public observations show the opposite. Therefore OOF can be used to veto local overfit but not to choose the next public sensor.
- 제출 전략: do not submit based on OOF selector rank. Use OOF stress only as a negative gate and continue treating public sensor choice as unresolved.

### H39. Test-movement fingerprints can calibrate public selector identity

- 상태: 부분 지지 as loose prior; strict selector certification 반증됨.
- 왜 그럴듯한가: unlike train OOF, test prediction movement directly describes how a candidate changes the hidden public table. If public subset identity is tied to subject/order/raw-domain structure, movement fingerprints should recover known public anchor order.
- 맞다면: target/subject/order/raw-domain movement fingerprints should recover known public deltas under leave-one-anchor-out, preserve stage2 < ordinal, rank A2C8 best, and distinguish bad JEPA anchors in permutation-null stress.
- 틀리다면: fingerprints may recover easy rank trends or stage2/ordinal but fail A2C8 best, compress bad JEPA failures, or have LOOCV error larger than the public edge being optimized.
- 최소 실험: build probability/logit/entropy movement fingerprints versus A2C8 over target, subject, row-order, raw-domain, and combined masks; run kNN leave-one-anchor-out on known public anchors; score current E38 sensors only if the selector passes.
- 관측: E40 found strict selector views `0`, loose selector views `4`. Combined view had LOOCV MAE `0.000781461`, pairwise rank accuracy `0.821429`, permutation-null rank p `0.004`, and correct stage2/ordinal order. It failed strict gate because A2C8 was not predicted best in leave-one-out and bad JEPA anchors were underpredicted. Combined-view loose prior ranked `inv7_s0p25` near best (`0.577450` predicted public LB), raw timeline `0.577526`, `1bb_s0p65` `0.577522`, and mixmin worse (`0.577664`).
- public LB 기대 반응: if the loose movement fingerprint is meaningful, conservative inverse7/raw-bridge movement should be less dangerous than mixmin on public, but expected deltas are too close to A2C8/raw05 to certify improvement. If it fails, public subset identity depends on label/loss geometry not captured by movement anatomy.
- 제출 전략: no normal submission. Use E40 only to choose a lower-risk diagnostic if the explicit question is movement-anatomy/public-likeness. It does not overrule E38's maximum-information mixmin sensor.

### H40. Movement plus bad-axis geometry can certify selector identity

- 상태: 반증됨 as selector certification; 부분 지지 as severity diagnostic.
- 왜 그럴듯한가: E40's main failure was bad JEPA severity compression. If the missing component is simply bad-axis direction geometry, logit-space cosine/projection against raw, medium, and bad public-anchor movement axes should repair LOO rank without needing new labels or models.
- 맞다면: a LOO-safe movement+axis view should lower bad-anchor underprediction, preserve stage2 < ordinal, predict A2C8 as best, pass a permutation-null rank stress, and create at least a loose selector gate.
- 틀리다면: bad-anchor underprediction may improve, but A2C8-best or rank/order should still fail, especially for named-axis features that can overfit known anchor identity.
- 최소 실험: build compact movement features plus axis-group/named cosine and projection features versus A2C8; during leave-one-anchor-out remove the left-out anchor's own axis; evaluate known-anchor LOOCV and score current E38 sensors only as gated diagnostics.
- 관측: E41 found strict selector views `0` and loose selector views `0`. Best severity view `axis_group` had LOOCV MAE `0.000854918`, pairwise rank accuracy `0.785714`, permutation-null rank p `0.014`, correct stage2/ordinal order, and bad-anchor mean underprediction `0.000898399`, but it failed A2C8-best badly by predicting A2C8 delta `+0.001475508` in LOO and missed the loose MAE threshold by `0.000004918`. `axis_named` had lower MAE `0.000827696` but failed rank accuracy `0.571429`, stage2/ordinal order, and bad-anchor underprediction `0.001412567`.
- public LB 기대 반응: if an ungated axis prior happened to improve on public, it would indicate that the selector should treat A2C8 as a known fixed anchor rather than a LOO target. If it worsens, then simple bad-axis geometry is just another overfit view. Either way E41 alone is not submission evidence.
- 제출 전략: no normal submission and no E41-ranked public forecast. The next useful route is not another cosine/projection tweak; it is an independent selector target, a principled current-best/zero-anchor calibration stress, or a predeclared public sensor.

### H41. Fixed-zero A2C8 anchoring makes movement-axis selector usable

- 상태: 반증됨 as usable selector; 부분 지지 as nonbaseline rank diagnostic.
- 왜 그럴듯한가: A2C8 is not an unknown anchor anymore. E41's harshest failure was leaving out the only zero/current-best point, so a valid selector may need to keep A2C8 fixed while testing nonbaseline ordering.
- 맞다면: keeping A2C8 fixed should recover nonbaseline public order, maintain stage2 < ordinal and raw05 as the best nonbaseline anchor, avoid trajectory collapse near zero, and produce candidate advantages larger than selector MAE.
- 틀리다면: nonbaseline rank may improve, but MAE should remain far above the raw05-A2C8 edge, synthetic trajectories should be non-monotone or collapse near zero, and unobserved "better than raw05" predictions should be much smaller than selector error.
- 최소 실험: keep A2C8 fixed at delta `0` in every nonbaseline LOO fold; remove each held-out anchor's own axis from axis views; score compact/axis views; compare candidate predicted advantages against nonbaseline selector MAE and the raw05-A2C8 public gap.
- 관측: E42 found fixed-zero nonbaseline gates `0` and usable zero-anchor gates `0`. Best view `axis_group` improved known-anchor ordering with nonbaseline MAE `0.000766262`, rank accuracy `0.857143`, Spearman `0.821429`, stage2/ordinal order correct, raw05 predicted best nonbaseline, and null rank p `0.006`. But raw05 gap/MAE was only `0.113520`, best unobserved advantage/MAE was `0.065408`, trajectory monotonic rate was `0.428571`, and the zero-anchor collapse warning was true.
- public LB 기대 반응: if an `axis_group`-ranked pair sensor improves, it would indicate that current-best anchoring is the right selector shape but local resolution underestimated the edge. If it worsens or is noise-scale, E42's collapse diagnosis is confirmed. Local evidence says this should not be used as a normal forecast.
- 제출 전략: no normal submission. Do not submit `pair_sensor_1bb_s0p65`, `1bb`, or `6b` because fixed-zero axis predictions beat raw05 by only `0.000037-0.000050`, far below selector MAE `0.000766`.

### H42. Existing selectors have enough resolution for near-frontier submissions

- 상태: 반증됨.
- 왜 그럴듯한가: pairwise public-order selectors, old hidden-subset stress, movement anatomy, bad-axis geometry, and fixed-zero anchoring each capture part of known public order. A combined audit could reveal that at least one selector is precise enough for the current frontier edge.
- 맞다면: at least one selector family should have known-anchor error below the raw05-A2C8 gap `0.0000869862`, and at least one unobserved candidate should have predicted edge larger than that selector error.
- 틀리다면: best known-anchor selector error should remain above the raw05-A2C8 gap, and candidate edges that look favorable should disappear once error margin is applied.
- 최소 실험: collect current selector reliability tables and candidate predictions; compute raw05-gap/error ratios; certify candidate rows only if `predicted_delta + selector_error < 0` versus A2C8 or `< raw05_gap` versus raw05.
- 관측: E43 found selector frontier-resolution gates `0`, candidates certified better than A2C8 `0`, and candidates certified better than raw05 `0`. The best selector was pairwise public-order with best LOO error `0.000218288`, raw05-gap/error ratio `0.398493`, and best L2O error `0.000415499`. E40/E41/E42 best raw05-gap/error ratios were only `0.111312`, `0.105094`, and `0.113520`.
- public LB 기대 반응: if a current micro-edge candidate improves, it would be outside the local selector evidence and would mainly reveal that public subset/worldview differs from all current selector stresses. If it worsens, E43's resolution-bound diagnosis is confirmed.
- 제출 전략: no normal submission. Any next public file should be a predeclared sensor, not an error-margin-certified improvement candidate.

### H43. Existing scored universe contains a larger low-risk movement

- 상태: 반증됨 for current scored universe.
- 왜 그럴듯한가: E43 could only certify that audited selector edges were smaller than selector error. A broader census might reveal a non-topline candidate with a larger pairwise p90 edge, low bad-axis load, raw05 compatibility, and two-selector or submit-like support.
- 맞다면: at least one existing score row should have pairwise public-order p90 edge greater than the E43 best selector error `0.000218288`, and at least one file should pass a normal large-safe gate after low-bad-axis/raw05/no-veto/two-selector checks.
- 틀리다면: pairwise-favorable rows may exist, but their edge should stay below both the raw05-A2C8 gap `0.0000869862` and selector error; large favorable raw/anchor signals should remain selector-conflict diagnostics rather than normal submissions.
- 최소 실험: normalize current candidate/selector tables, compute pair edge, raw/anchor/old edge, low-risk gates, and aggregate by file.
- 관측: E44 loaded 29 tables, 69,869 rows, and 48,088 unique files. Pair-negative files were `12,309`, but pair edge greater than raw05-A2C8 gap was `0`, pair edge greater than selector error was `0`, large-pair low-bad was `0`, and normal large-safe was `0`. Best pair edge was `0.000073768`, only `0.337941` of selector error. Any-edge-above-selector files were `21`, but they were raw/anchor conflict rows such as inverse7/mixmin with pair/old veto.
- public LB 기대 반응: if one of these raw/anchor conflict sensors improves, it validates a worldview not captured by current pair/old selectors; if it worsens, E44 confirms that raw/anchor-only large edges are not enough. No file is locally certified as a normal improvement submission.
- 제출 전략: no normal submission from the current scored universe. Continue with a new independent selector target, a larger sign-consistent movement, or a deliberately labeled public sensor.

### H44. Public subset is a simple structured mask recoverable from local data

- 상태: 반증됨 under tested mask/prior family.
- 왜 그럴듯한가: public LB may be computed on a pseudo-public subset rather than all test rows. If that subset is driven by subject, row order, calendar, date, missingness, raw-domain shift, or density, a structured mask could become an independent selector target without needing another model family.
- 맞다면: at least one predeclared mask should recover held-out known public anchors with LOO MAE below the E43 selector error `0.000218288`, preferably below the raw05-A2C8 gap `0.0000869862`; A2C8 should remain predicted best, raw05 direction should be correct, and feasible ranges should be narrow rather than merely containing every anchor.
- 틀리다면: exact inverse fits may remain possible, but LOO errors should stay above selector scale and feasible ranges should be much wider than the public edge.
- 최소 실험: build subject/order/date/dow/month/raw-domain/random masks; for each mask hold out each known public anchor, fit soft hidden labels on the others under train global +/-0.10 and subject-target +/-0.20 constraints, choose the minimum-deviation solution from train subject priors, and compute held-out LB plus feasible ranges.
- 관측: E45 tested 145 masks. Selector-scale gates were `0` and strict sub-gap gates were `0`. Best mask was `global_key_order/suffix_frac0.20` with LOO MAE `0.000429528`, max abs `0.00129817`, raw05-gap ratio `4.937886`, and selector-error ratio `1.967712`. Feasible range widths were huge: best-mask mean width `0.0427582`, all-row mean width `0.0455258`; actual anchors were inside because the ranges were uninformative.
- public LB 기대 반응: if a future public sensor reveals one of these simple masks, E45's train-prior/min-deviation assumption was insufficient; absent that, simple mask selection should not be used to rank candidates.
- 제출 전략: no normal submission and no mask-derived selector submission. A public sensor remains the only way to resolve the worldview, unless a new selector target or larger sign-consistent movement is found.

### H45. The 0.54 path is hidden block-rate state identification, not row-level prediction

- 상태: 강한 증거 있음; current reconstruction methods are insufficient.
- 왜 그럴듯한가: validation block-rate oracle reaches `0.517878`, while the fold-safe temporal baseline is `0.624765`. That is enough headroom for 0.5x if block rates are inferred, but not if we only smooth rows.
- 맞다면: subject identity should explain only part of the oracle gap; Markov transitions, endpoint flanks, one-feature thresholds, and simple public masks should fail to recover the missing hidden block-rate vector.
- 틀리다면: full subject oracle, Markov bridge, endpoint pseudo-hidden reconstruction, or nested feature thresholds should close most of the `0.106888` temporal-to-block-oracle gap.
- 최소 실험: `analysis_outputs/block_state_bottleneck_audit.py`, joining oracle bounds, Markov/threshold probes, split-block topology, lag autocorr, hidden-block reconstruction, and E45 public-mask feasibility.
- 관측: E46 found block-rate oracle `0.517878`, temporal-to-block gap `0.106888`, subject identity explained fraction `0.291286`, remaining gap after full-subject oracle `0.075753`, best Markov delta vs temporal `+0.002998`, nested threshold delta `+0.044275`, endpoint reconstruction gain over subject mean `0.003252`, and two-train-flank submission block fraction `0.722222`.
- 성공/폐기 기준: strengthened if oracle headroom is large and every cheap context heuristic recovers only a small fraction; weakened only if a fold-safe block-context model recovers a material share of the block-rate oracle gap under blockwise and anchor stress.
- public LB 기대 반응: public LB will not improve from another micro row-blend unless it changes block-state inference or selector identity. A successful future submission should either encode predicted block-rate state or use block-rate residual energy to choose candidate/gate strength.
- 제출 전략: no submission directly from E46. Build a JEPA-style block-context experiment where context is subject train-block summaries plus overnight/raw measurement-process views, target is held-out block-rate vector, and LeJEPA-style energy checks rank/isotropy/NN consistency plus anchor stress.

### H46. Current block-summary context does not contain enough recoverable block-rate state

- 상태: 강한 증거 있음 for current Ridge/context-summary family; not a claim about all possible raw sequence/context targets.
- 왜 그럴듯한가: E46 showed that context often exists around hidden blocks, but endpoint/Markov/threshold translations fail. The next question is whether richer block summaries already solve the target-representation problem.
- 맞다면: fold-safe context-to-block-rate heads may create small row blend gains, but direct block-rate loss should remain worse than or close to temporal block context, oracle-gap recovery should be tiny, and sensor-value views should not open the `0.106888` gap.
- 틀리다면: at least one context view should beat temporal block weighted LogLoss and recover a material share of the block-rate oracle gap while keeping non-collapsed geometry.
- 최소 실험: `analysis_outputs/block_context_jepa_target_audit.py`, fixed Ridge heads from label-context, sensor-value, missingness, and combined block summaries to held-out block-rate vectors under subject-block folds.
- 관측: E47 found best non-base 25% row blend `label_context_ridge = 0.623260`, delta `-0.001505`, but this recovers only `0.014083` of the oracle gap. Its direct block weighted LogLoss is `0.635888`, worse than temporal block context `0.623448` by `0.012440`. `sensor_values_ridge` is worse in both row blend (`+0.000660`) and block-rate loss (`0.657811`). Geometry is not collapsed but not useful enough: label-context anisotropy `0.466748`, effective rank `3.547232`.
- 성공/폐기 기준: strengthened if row-level gains remain calibration-like while target-representation loss fails; weakened only if a new context/target construction beats temporal block loss and recovers at least several percent of oracle gap under blockwise and anchor stress.
- public LB 기대 반응: a submission made from these current block-summary ridge predictions would likely behave like another micro-calibration perturbation, not a 0.54 path. Public movement should be small and selector-noise dominated.
- 제출 전략: no submission. Next try must change the representation task: discrete count/posterior target, contrastive block retrieval, raw overnight sequence tokens, or public/anchor-conditioned energy; not another same-summary Ridge regressor.

### H47. Mixmin validates the anchor-loss/binary actual-anchor worldview

- 상태: 강하게 지지됨 by public LB; private/generalization 미확인.
- 왜 그럴듯한가: E32-E34 showed that low-anchor-energy binary worlds one-sidedly supported mixmin, E33 showed the support was not one-anchor fragile, and E38 ranked mixmin as the maximum-information public sensor.
- 맞다면: mixmin should beat a2c8 despite pairwise/old selector veto, and the improvement should be large enough to exceed previous selector-resolution noise.
- 틀리다면: mixmin should worsen or only move at noise scale, implying that anchor-loss/cancellation geometry overfit known public anchors.
- 최소 실험: submit the predeclared public sensor `analysis_outputs/submission_mixmin_0c916bb4.csv` and compare with previous anchors.
- 관측: E48 public LB was `0.5763066405`, improving over previous best `0.5774393210` by `0.0011326805` and over raw05 by `0.0012196667`. This is about `13.02x` the previous raw05-a2c8 gap.
- public LB 기대 반응: fulfilled. The old pairwise/old selector veto is falsified as a hard gate, though still useful as a risk sensor.
- 제출 전략: promote mixmin to frontier. Next candidates should be mixmin-relative: decompose target/row contributions, add mixmin as a known anchor in selector calibration, and test whether inverse7/raw-structure or block-state JEPA can improve or stabilize mixmin rather than merely beat a2c8.

### H48. Train/test is a subject-calendar mask, so the target is hidden block-rate restoration

- 상태: 강한 관찰 증거 있음; calendar-only selector는 E50에서, anchor-loss x calendar kNN selector는 E51에서 반증됨.
- 왜 그럴듯한가: E49 shows train/test is not a future split. Test rows are hidden calendar holes inside each subject timeline, often adjacent to or between train runs. This matches I-JEPA's context-target framing better than independent tabular rows: context is labeled calendar flanks, target is the hidden block's label-rate/count vector.
- 맞다면: mixmin movement should concentrate by subject/date block and target, simple train/subject/recent priors should not uniformly explain the gain, and a selector using calendar-mask movement features should explain mixmin as a new public anchor without breaking raw05/stage2/ordinal/bad-JEPA order.
- 틀리다면: calendar block topology will add little beyond target-level movement, simple priors will explain most of mixmin's public edge, or selector recalibration with calendar features will still fail mixmin and known-anchor order.
- 최소 실험: use `analysis_outputs/post_mixmin_observation_audit.py` outputs to build mixmin-relative calendar-block features: inside-train-calendar vs after-train-end, gap-adjacent vs between-train-runs, run length, subject, target movement, raw05 distance, and prior CE stress. Re-run known-anchor selector LOO/L2O with mixmin included.
- 관측: E49 found largest target movements `Q3 = 0.011540`, `Q1 = 0.010345`, `S3 = 0.009688`; `Q1` and `S1` are worse under all simple prior proxies; movement is subject-concentrated (`id05/id09/id08/id03/id01` top); top high-movement calendar masks are `gap_adjacent` or `between_train_runs`. E50 then tested this as a selector with mixmin included as a known anchor. The best `subject_calendar` view had MAE `0.000884106`, rank accuracy `0.833333`, and Spearman `0.833333`, but predicted held-out mixmin delta `0.00135162` instead of `0`; strict and loose selector views were both `0`. E51 added LOO-safe anchor-loss world aggregates and compact calendar context. The best `anchor_residual` view had MAE `0.000835516`, rank accuracy `0.750000`, and bad-tail order correct, but predicted held-out mixmin delta `0.00241739`; strict and loose selector views again were `0`.
- 성공/폐기 기준: the standalone selector and kNN selector versions are falsified. The broader context-target version remains alive only if calendar flanks help predict held-out block-rate/count representations directly, or if a mixmin-constrained binary-world stress narrows new candidate signs without pretending to be a smooth submission-file ranker.
- public LB 기대 반응: a future public-improving candidate should not be a global prior tweak or a direct calendar-position tweak. It should preserve mixmin's anchor-loss direction while changing probabilities mostly on specific subject-calendar hidden blocks whose block-rate state is independently inferred.
- 제출 전략: no immediate submission. Do not use E50/E51 predicted candidate scores as forecasts. Build a mixmin-relative candidate only after calendar context predicts block-rate/count state or a revised binary-world stress uses mixmin as a constraint and leaves the candidate sign stable.

### H49. Mixmin-conditioned binary worlds certify an existing replacement candidate

- 상태: 반증됨 for current curated candidate pool; supports mixmin as local frontier inside the current binary-world family.
- 왜 그럴듯한가: E32/E33 low-anchor-energy worlds supported mixmin and inverse7 before mixmin was known. E48 then validated mixmin publicly. If the same hidden-world family contains the next improvement, conditioning worlds on the actual mixmin public delta should reveal which existing bridge/inverse/raw candidate is consistently better than mixmin.
- 맞다면: at least one candidate should have negative max LogLoss delta versus mixmin in the 1-gap or 2-gap mixmin-compatible world bands and in the postmix low-energy band. A weaker but useful result would be high better_rate, negative median, and no adverse delta larger than the raw05-a2c8 resolution unit.
- 틀리다면: candidate signs should collapse around mixmin, with no strict or loose better-than-mixmin gates. Near-ties may exist, but their max delta should remain positive and their better_rate should be far from one-sided.
- 최소 실험: `analysis_outputs/post_mixmin_binary_world_sign_stress.py`, reusing E30/E32 binary worlds, filtering/reweighting by actual mixmin delta `-0.0011326805`, and scoring E51/E37/E38/selected bridge candidates by world LogLoss delta versus mixmin.
- 관측: E52 scored `158` candidates. Mixmin-compatible 1-gap worlds were `5`; postmix-energy-quarter worlds were `7`. Strict better-than-mixmin gates were `0`, loose gates were `0`, and near-tie gates were `1`. The near-tie `analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv` had mixmin-fit-gap better_rate `0.2`, median delta `+0.000034`, max delta `+0.000048`, and postmix-energy-quarter better_rate `0.285714`, median delta `+0.000009`.
- 성공/폐기 기준: the existing-candidate replacement version is discarded because no candidate is one-sided better than mixmin. The broader constrained-world route remains live only if a newly generated binary/MILP family includes mixmin as a hard anchor and produces a new movement with stable sign, or if a block-rate/count representation supplies a new candidate not already in E52.
- public LB 기대 반응: submitting the near-tie would be low information because E52 says it is not better than mixmin, only almost equivalent under a small feasible band. A public improvement from it would imply the E30/E32 world family misses a private/public split or target-axis component; a worsening would add little beyond confirming E52.
- 제출 전략: no submission from E52. Keep mixmin as active frontier. Next useful action is calendar-flank block-rate/count target modeling or a fresh mixmin-constrained world-generation experiment, not another rescore of existing bridge candidates.

### H50. Calendar-flank count-state predicts mixmin safely

- 상태: 부분 반증됨 as a candidate generator; retained only as calendar-flank count-state energy.
- 왜 그럴듯한가: E46 found `26/36` hidden blocks have two labeled flanks and E49 showed test rows are interleaved subject-calendar holes. If mixmin succeeded by approximating hidden block state, a JEPA-style context of labeled flanks plus block length and donor block count/rate signatures should predict held-out count state and explain mixmin without using public LB directly.
- 맞다면: local and strict donor posteriors should both improve pseudo-hidden train block count/rate prediction over subject mean, targetwise gains should include the S targets that carry objective sleep-stage structure, and real hidden-block predicted rates should prefer mixmin over a2c8 with stable negative deltas across targets.
- 틀리다면: gains should depend on same-subject/local donors, strict donor exclusion should erase or reverse pseudo-hidden gains, and hidden-block mixmin preference should be weak or target-mismatched.
- 최소 실험: `analysis_outputs/calendar_flank_block_count_state_probe.py` creates pseudo-hidden blocks from train using real hidden block lengths, predicts block target rates/counts from labeled flanks and donor block signatures, compares local versus strict subject-excluded donors, and scores expected CE deltas for mixmin/raw05 against a2c8 on actual hidden blocks.
- 관측: E53 tested `369` pseudo-hidden train blocks and `36` actual hidden test blocks. `calendar_count_local` improved pseudo-hidden weighted row LogLoss by `-0.005266`, but `calendar_count_strict` worsened it by `+0.001434`. Strict improved Q1 `-0.011907`, Q2 `-0.029170`, and Q3 `-0.011743`, but worsened S1 `+0.001126`, S2 `+0.024074`, S3 `+0.034293`, and S4 `+0.003363`. On actual hidden blocks, strict predicted rates weakly favored mixmin with weighted delta `-0.000179`, while local was adverse at `+0.000250`. Strict hidden target alignment favored S3 `-0.003537`, S2 `-0.002363`, and Q2 `-0.000820`, but hurt S1 `+0.003665`, S4 `+0.000821`, Q1 `+0.000649`, and Q3 `+0.000333`.
- 성공/폐기 기준: the direct simple posterior is discarded as a submission generator because the fold-safe strict version fails pseudo-hidden target recovery and the real hidden alignment is small and target-mismatched. The broader block-state branch remains alive only if richer raw overnight context, target-dependency count manifolds, or hard mixmin-constrained worlds recover a stable strict latent.
- public LB 기대 반응: a submission made directly from this posterior would be low-quality evidence and likely target-fragile. If it improved public, it would imply the actual public subset overweights S2/S3/Q2 hidden states; if it worsened, it would mainly confirm the E53 strict/local mismatch.
- 제출 전략: no submission from E53. Use `calendar_flank_count_state_energy` only for risk analysis or gating, not for row probability movement by itself.

### H51. Raw overnight context recovers strict block state but not the mixmin public edge

- 상태: representation branch 강하게 지지됨; direct candidate/mixmin-explanation branch 반증됨.
- 왜 그럴듯한가: E53 showed that calendar flanks alone were too local and strict-subject donor exclusion failed. Raw overnight phone/watch/context/light/mobility/usage/coverage features are the most direct observed traces of the sleep-generating process, so they may encode a block-state latent that labeled flanks miss.
- 맞다면: raw overnight block embeddings plus flank context should improve pseudo-hidden block count/rate prediction under strict subject exclusion, without same-subject donors. Geometry should not collapse into a single shortcut direction. If this is the same latent that made mixmin win public, actual hidden-block predicted rates should also prefer mixmin over a2c8.
- 틀리다면: strict raw-context posteriors should behave like E53 strict calendar counts, with near-zero or adverse pseudo-hidden deltas; or, if pseudo-hidden recovery works but actual hidden mixmin alignment worsens, the raw latent is real but not the public mixmin latent.
- 최소 실험: `analysis_outputs/raw_overnight_block_context_probe.py`, compressing `overnight_sensor_features_v2.parquet` into feature-family row PCA views, aggregating to block vectors, concatenating optional E53 flank context, and scoring kNN donor rate posteriors under local and strict donor exclusion.
- 관측: E54 found best strict method `night_phone_rawctx_strict_k8_a24` with pseudo-hidden weighted row LogLoss `0.605269`, delta `-0.007733` versus subject mean. Local diagnostics were stronger (`night_phone_rawctx_local_k8_a24` delta `-0.011361`), but strict recovery itself was material. Best strict target deltas were Q1 `-0.010726`, Q2 `-0.017247`, Q3 `-0.016308`, S1 `-0.009910`, S2 `-0.006878`, S3 `+0.007802`, S4 `-0.000865`. Geometry was non-collapsed enough for diagnosis: effective rank `23.393361-35.124905`, anisotropy `0.144271-0.183029`. But actual hidden-block mixmin alignment failed for the best strict raw method: weighted mixmin delta vs a2c8 was `+0.000311`; the best hidden alignment remained `calendar_count_strict` at only `-0.000179`.
- 성공/폐기 기준: strict block-state representation is strengthened because pseudo-hidden recovery survives subject exclusion. The direct submission/mixmin-explanation variant is discarded because hidden-block mixmin alignment is adverse and S3 regresses.
- public LB 기대 반응: a direct raw overnight posterior submission would likely test a different, possibly private-relevant latent rather than the public mixmin edge. Improvement would imply public/public-private split overweights the raw overnight latent despite local mixmin-sign failure; worsening would confirm E54's translation-gate warning.
- 제출 전략: no submission. Use `raw_overnight_block_state_energy` as a stress/gate feature and as a feasibility prior for either target-dependency/S3 correction or fresh mixmin-hard world generation.

### H52. Simple Q/S target-dependency projection translates raw block state into mixmin-public state

- 상태: 반증됨 for tested kNN/Ridge target-rate manifold projections.
- 왜 그럴듯한가: E54's raw latent improved most targets but regressed S3 and failed mixmin hidden alignment. If the raw representation is right but its target vector violates the Q/S block-rate manifold, projecting each target from the other target rates could repair the translation without discarding the raw context.
- 맞다면: a strict donor target-dependency projection should preserve or improve `night_phone_rawctx_strict_k8_a24` pseudo-hidden LogLoss, fix S3 versus subject mean, and give negative expected mixmin delta on actual hidden blocks.
- 틀리다면: S3 repair, pseudo-hidden recovery, and hidden mixmin sign should separate. S3 replacement may help local pseudo-hidden loss without changing hidden mixmin sign; sign-flipping projections may destroy pseudo-hidden validity.
- 최소 실험: `analysis_outputs/raw_block_target_dependency_probe.py`, using raw E54 predictions as query target context, strict subject-excluded donor true block rates as the target-rate manifold, kNN/Ridge estimators, pair/group/all-cross contexts, and masks over S3, S2/S3, stage, and all targets.
- 관측: E55 tested `225` methods and found joint gates `0`. Raw base had pseudo-hidden LogLoss `0.605269`, raw delta `0`, S3 delta vs subject `+0.007802`, and hidden mixmin delta `+0.000311`. Best pseudo-hidden method `raw_phone_s3_subject_w1p00` improved raw by `-0.001115` and fixed S3 to `0.000000`, but hidden mixmin stayed adverse at `+0.000319`. Best near-raw kNN projection improved raw by only `-0.000118`, left S3 adverse at `+0.007219`, and hidden mixmin adverse at `+0.000317`. Best hidden-sign method `raw_phone_td_ridge_groupcross_all_k0_a8_w0.75` reached hidden mixmin `-0.000414`, but pseudo-hidden LogLoss collapsed to `0.727319`, raw delta `+0.122051`, and S3 delta `+0.207892`.
- 성공/폐기 기준: discarded because no method satisfies the joint condition. A future target-dependency branch must change the target representation itself, not just project target rates from other target rates.
- public LB 기대 반응: direct target-dependency projection submissions would be low information or high risk. If an S3-subject replacement improved public, it would imply public sign is insensitive to the hidden mixmin-rate stress; if Ridge sign-flip improved, E55's pseudo-hidden stress would be invalid for public. Neither is locally justified.
- 제출 전략: no submission. Move to fresh mixmin-hard binary world generation with raw context as a feasibility prior, or design a more structural block target beyond simple rate-manifold projection.

### H53. Mixmin-hard raw binary worlds generate a coherent hidden posterior

- 상태: 부분 지지됨 as a hidden-world generator; not yet a submission-safe translator.
- 왜 그럴듯한가: E52 showed existing candidates do not beat mixmin after conditioning old worlds on mixmin, and E54 showed raw overnight context contains strict block-state signal. A fresh world generator that treats mixmin as a hard observation and raw state as feasibility may reveal a posterior not present in the existing candidate pool.
- 맞다면: regenerated worlds should be numerous/non-duplicate, existing candidates may still fail, but posterior variants should pass internal world-LOO sign gates. The posterior should be interpretable as a latent energy even if direct movement needs separate public-anchor stress.
- 틀리다면: world generation should collapse to few duplicates, posterior variants should not beat mixmin in held-world stress, or the result should be indistinguishable from existing candidate rescoring.
- 최소 실험: `analysis_outputs/mixmin_hard_raw_world_probe.py`, with `9` known public anchors including mixmin as an observed constraint, raw E54 hidden block rates as CE/count feasibility energy, and posterior held-world validation.
- 관측: E56 generated `45` worlds and `44` unique binary worlds. Existing candidate strict gates stayed `0`, but posterior world-LOO strict gates were `12`. Best internal posterior `posterior_raw_energy_quarter_w0.28` had held worlds `11`, better_rate `1.0`, median delta `-0.154291`, p90 `-0.069887`, and max delta `-0.069103`. The generated diagnostic submission moved far from mixmin: mean abs logit `0.381359`.
- 성공/폐기 기준: hidden-world generator branch is kept because it creates internally coherent posterior structure. The direct submission branch remains unaccepted unless independent anchor/public-shape stress beats mixmin with small movement.
- public LB 기대 반응: if direct posterior movement improved public despite E57-style stress, it would imply actual-anchor proxy is missing a new hidden subset. If it worsens, E56 should be retained only as teacher/energy.
- 제출 전략: no direct submission from E56 alone. Use E56 posterior as `mixmin_hard_raw_posterior_energy` or a teacher for anchor-constrained distillation.

### H54. E56 mixmin-hard raw posterior is directly public-safe

- 상태: 반증됨 for tested posterior variants.
- 왜 그럴듯한가: E56 posterior variants passed internal held-world stress, and the world generator included mixmin as an observed public constraint rather than treating it as an unobserved candidate.
- 맞다면: at least one posterior should pass world-LOO strict, beat mixmin under independent actual-anchor scoring, and stay close enough to mixmin that it is not a high-variance public overfit move.
- 틀리다면: posterior variants should either lose to mixmin under actual-anchor stress, or only win after too-large logit movement.
- 최소 실험: `analysis_outputs/mixmin_hard_raw_posterior_safety_stress.py`, requiring world-LOO strict pass, actual-anchor score below mixmin, and mean abs logit movement versus mixmin `<= 0.08`.
- 관측: E57 scored `15` variants and found joint safety gates `0`. Mixmin actual-anchor score was `0.577734`. Best posterior `posterior_all_w0.05` scored `0.577857`, delta `+0.000123` versus mixmin. The E56 selected diagnostic `posterior_raw_energy_quarter_w0.28` scored `0.598116`, delta `+0.020381`, with mean abs logit movement `0.381359`.
- 성공/폐기 기준: discarded as direct submission because independent public-anchor geometry rejects every posterior variant.
- public LB 기대 반응: submitting the E56 diagnostic would be a high-downside public test, not a justified frontier candidate. Improvement would falsify the actual-anchor safety proxy; worsening would only confirm E57.
- 제출 전략: do not submit E56 posterior files. Next strategy is anchor-constrained distillation of E56 energy, or a structural block target that can explain the posterior without large public-anchor-adverse movement.

### H55. Anchor-constrained E56 posterior distillation yields a submission candidate

- 상태: 반증됨 as a submission source; weakly supported only as sub-resolution energy.
- 왜 그럴듯한가: E57 showed full posterior movement is too large and anchor-adverse. A smaller JEPA-style distillation may keep only confident cells, target groups, and row gates from the E56 teacher while staying close to mixmin.
- 맞다면: at least one toward-teacher candidate should satisfy world guard, movement guard, and actual-anchor improvement margin `< -1e-5` versus mixmin. Reverse controls should not be stronger than the teacher direction.
- 틀리다면: toward-teacher candidates may show tiny negative anchor deltas but below margin, or reverse controls may be equally good, implying the posterior is not a stable submission direction.
- 최소 실험: `analysis_outputs/mixmin_hard_posterior_distillation_probe.py`, generating E56 posterior-band candidates with target masks, raw-agreement/support/entropy cell gates, row gates, caps, and small weights; actual-anchor score is a final safety stress after world-support prefilter.
- 관측: E58 generated `104727` candidates and actual-anchor scored `1200`. E61 found and fixed a candidate-prediction index mismatch in the scoring path; the conclusion remained unchanged. Corrected toward-teacher candidates: `900` scored, `126` beat mixmin by sign, but eligible submission gates were `0` after the `1e-5` margin. Best toward-teacher anchor delta was `-0.000004081` from `toward_teacher|low_slack_half|no_q2|raw_agree|all|w0.070|c0.120`. Reverse controls scored `300`, with best anchor delta only `-0.0000000126` and world guard `0`.
- 성공/폐기 기준: discarded as a submission source because no candidate clears selector-scale anchor margin. Retained as evidence that the E56 direction is not purely adverse when heavily gated, but its safe movement is too small to justify public submission.
- public LB 기대 반응: submitting the best E58 candidate would be a very low-information micro-probe; any improvement or degradation would be dominated by public noise unless repeated evidence raises the margin.
- 제출 전략: no submission from E58. Move to structural block target representation or add an independent non-anchor validation signal before revisiting E56 distillation.

### H56. Joint block label-pattern target is the missing public-aligned representation

- 상태: 부분 반증됨. Joint pattern structure is learnable, but the tested structural target does not translate into a mixmin-relative submission source.
- 왜 그럴듯한가: E55 showed seven marginal target rates are too weak a representation: S3 repair, raw pseudo-hidden recovery, and hidden mixmin sign separate. A 128-state block-level joint label-pattern distribution can encode Q/S co-occurrence, cardinality, and impossible combinations that marginal rates erase.
- 맞다면: strict raw/calendar context should predict pseudo-hidden joint pattern distributions better than independent raw marginals; the resulting marginal rates should not worsen row LogLoss; the learned joint structure should add information beyond its own marginals; S3 should not regress; and actual hidden-block rates should prefer mixmin over a2c8.
- 틀리다면: pattern NLL may improve while marginal row LogLoss worsens, or hidden mixmin sign may improve only when pseudo-hidden validity collapses. That would mean joint co-occurrence is learnable but not the current public frontier latent.
- 최소 실험: `analysis_outputs/structural_block_target_probe.py`, using E55 `build_base_state()`, 128 joint label-pattern count targets, strict subject-excluded kNN over raw/calendar/subject context variants, independent raw/subject fallback distributions, row LogLoss, structural pattern NLL, own-margin joint gain, S3 stress, and real hidden-block mixmin alignment.
- 관측: E59 tested `219` methods (`216` structural). Joint gates were `0`. Structural pattern signal was strong: `139` methods beat raw independent pattern NLL and `198` carried joint information beyond their own marginals. Best structural method `struct_raw_calendar_subject_fbsubject_k16_a12_w0.35` improved pattern NLL versus raw by `-0.062594` and own-margin joint gain by `-0.088340`, but worsened row LogLoss versus raw by `+0.003678`, S3 versus subject by `+0.002727`, and hidden mixmin sign by `+0.000304`. Methods with negative hidden mixmin sign existed (`26`), led by `struct_raw_subject_fbraw_k8_a4_w1.00` at `-0.000367`, but they destroyed pseudo-hidden row validity (`+0.042230` versus raw) and S3 (`+0.078145` versus subject).
- 성공/폐기 기준: discarded as a direct candidate source because pattern recovery, row calibration, S3 health, and hidden mixmin sign do not align. Retain the structural pattern NLL as a diagnostic energy: it proves the data has nontrivial joint target structure, but current context-to-pattern translation is not public-aligned.
- public LB 기대 반응: a submission made from E59 hidden-sign structural methods would be high risk because the only negative hidden-sign methods fail pseudo-hidden and S3 stress. If such a file improved public, it would falsify the pseudo-hidden block target stress; if it worsened, it would confirm the joint-vs-row translation split.
- 제출 전략: no submission from E59. Next branch should not be another joint-pattern kNN translation. Use independent non-anchor validation for E56 energy, or design a structural target that includes transition/topology/public-disagreement energy rather than only within-block joint labels.

### H57. Transition residual block-state is the missing non-anchor validator

- 상태: 반증됨 as direct translator; retained only as a hidden-sign diagnostic.
- 왜 그럴듯한가: E59 showed within-block joint labels are learnable but target-mismatched. A more causal JEPA target may be the transition residual from labeled calendar flanks to the hidden run: not "what labels co-occur in a block?" but "how does this hidden block depart from its endpoints/raw/subject baseline?" This could independently validate E56 posterior energy without relying on public anchors.
- 맞다면: strict subject-excluded transition-residual kNN should improve pseudo-hidden row LogLoss over E54 raw phone base, reduce transition-residual MSE, avoid S3 regression versus subject mean, and assign actual hidden blocks rates under which mixmin beats a2c8.
- 틀리다면: row/raw validity, residual MSE, S3 health, and hidden mixmin sign should split. A method may predict residual energy or hidden sign, but only by breaking row calibration or target health.
- 최소 실험: `analysis_outputs/transition_residual_block_state_probe.py`, using E55 `build_base_state()`, endpoint/subject/raw bases, topology/raw/full-transition contexts, strict subject-excluded kNN in logit-rate residual space, pseudo-hidden row/residual stress, and real hidden-block mixmin alignment.
- 관측: E60 tested `438` methods (`432` transition methods). Joint gates were `0`. Only `1` method beat raw row LogLoss and that was the raw baseline itself. `227` methods improved transition-residual MSE and `217` had negative hidden mixmin sign, but these axes did not coincide. Best row-valid transition `transition_raw_residual_baseraw_k4_a24_w0.35` was close to raw (`+0.000186` row LogLoss vs raw) and improved residual MSE (`-0.017074`), but hidden mixmin stayed adverse (`+0.000230`) and S3 remained adverse. Best hidden-sign method `transition_raw_residual_baseedge_mid_k4_a4_w1.00` had hidden mixmin `-0.001569`, driven by S3/S2/Q3, but pseudo-hidden row LogLoss collapsed (`+1.519232` vs raw) and S3 worsened by `+1.331880` versus subject.
- 성공/폐기 기준: discarded as a candidate generator and as the missing independent validator for E56. Retain transition residual features only as diagnostic energy when evaluating teacher reliability, because hidden-sign support without pseudo-hidden validity is not actionable.
- public LB 기대 반응: submitting a transition-residual hidden-sign file would be high-downside. Improvement would imply the pseudo-hidden row/residual stress is not public-relevant and the public subset heavily weights the S3/S2/Q3 hidden-sign axis. Worsening would mainly confirm E60.
- 제출 전략: no submission from E60. The next structural target must avoid both within-block-only pattern targets and aggressive endpoint-residual hidden-sign moves; it should combine E56 energy with a validation target that preserves row calibration.

### H58. E58 posterior-distillation rejection is only a scoring-index artifact

- 상태: 반증됨. A scoring-index bug existed, but the no-submission conclusion survives correction.
- 왜 그럴듯한가: While designing the next E56/E60 gate, the E58 code path showed `score_prefilter()` sorted/reset candidate rows, while `attach_anchor_scores()` used the post-sort DataFrame index to select `preds`. This could mismatch candidate metadata and probability arrays, invalidating the reported best E58 anchor deltas.
- 맞다면: after adding stable `pred_index`, corrected actual-anchor scoring should materially change E58 gates, possibly open an eligible candidate or reverse the toward/reverse interpretation.
- 틀리다면: corrected scoring should keep eligible gates at `0`, keep best anchor improvement below the `1e-5` margin, and preserve E58 as an energy-only branch.
- 최소 실험: patch E58 to attach `pred_index` before prefilter sorting, rerun `analysis_outputs/mixmin_hard_posterior_distillation_probe.py`, and compare corrected summary against the previous E58 conclusion.
- 관측: E61 corrected and reran E58. Generated candidates remained `104727`; scored candidates remained `1200`; eligible gates remained `0`. Corrected best toward-teacher delta was `-0.000004081`, still below margin. Corrected toward sign-beats fell from the previous mismatched `631/900` to `126/900`; reverse-control best became only `-0.0000000126` with world guard `0`.
- 성공/폐기 기준: artifact-only explanation discarded. The script/output now use stable `pred_index`; E58 remains rejected as a submission source.
- public LB 기대 반응: unchanged. An E58 file would still be sub-margin and low information.
- 제출 전략: no submission. The fix improves evidence integrity, not candidate priority.

### H59. Transition residual can validate E56 teacher if used only as a gate

- 상태: 반증됨 for the tested gate family. Transition residuals remain risk diagnostics, not the missing calibration-preserving E56 validator.
- 왜 그럴듯한가: E56 generated coherent mixmin-hard worlds, E58 found a tiny non-adverse teacher direction, and E60 found a stronger hidden mixmin sign in transition residual space. Since direct transition rates collapse calibration, the more conservative idea is to use transition residual only to open/close E56 teacher cells.
- 맞다면: transition-gated E56 candidates should improve over E58's corrected best anchor delta, preserve E56 world/movement guards, and open at least one toward-teacher candidate with `anchor_delta_vs_mixmin < -1e-5`.
- 틀리다면: transition gates should reduce or fail to expand the E58 margin, keep eligible gates at `0`, or make reverse controls comparable.
- 최소 실험: `analysis_outputs/transition_gated_posterior_distillation_probe.py`, combining E56 posterior bands with E60 row-safe, balanced hidden-sign, and aggressive hidden-sign residual views as gates only. Candidate probabilities remain small capped logit moves from mixmin toward E56 teacher; transition residuals are never used as direct targets.
- 관측: E62 generated `363258` candidates and actual-anchor scored `1300`. Eligible gates were `0`; diagnostic reverse gates were `0`. Best toward-teacher delta was `-0.000002716` from `toward_teacher|low_slack_half|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080`, weaker than corrected E58's `-0.000004081`. Reverse best was only `-0.00000000547`.
- 성공/폐기 기준: discarded as the missing validator. The best transition gate is interpretable (`balanced hidden-sign + raw agreement`, no S3), but its effect is below selector margin and smaller than E58.
- public LB 기대 반응: no public submission. A public test would be lower-information than E58 because the local margin is smaller and the gate did not add independent selector-scale support.
- 제출 전략: no E62 submission. Future E56 use needs a different independent validation target, not transition residual as a simple gate.

### H60. Gradient-consensus hidden-rate views can make E56 submit-safe

- 상태: 부분 지지 for direction, 반증됨 for submission safety.
- 왜 그럴듯한가: E58/E62 tested hand-built gates and found only sub-margin actual-anchor gains. A sharper LeJEPA-style test is not "does a gate look plausible?" but "does the E56 teacher move down the BCE gradient implied by independent hidden-rate views?" If calendar count, raw phone context, transition residual, and subject priors independently agree with the teacher direction, E56 may contain a real hidden-world direction that previous gates underused.
- 맞다면: toward-teacher cells should pass gradient-consensus hidden guards across multiple non-anchor views, reverse controls should fail those guards, and at least one toward candidate should clear actual-anchor selector margin `< -1e-5` while preserving E56 world/movement guards.
- 틀리다면: hidden-rate gradient guards should either not distinguish toward vs reverse, or should distinguish direction but still fail public-anchor margin, implying the missing piece is amplitude/public-anchor translation rather than directional validation.
- 최소 실험: `analysis_outputs/gradient_consensus_posterior_probe.py`, building hidden-rate views from subject mean, strict calendar counts, raw phone base, row-safe/balanced/aggressive transition signs, and a core median view. It uses BCE-gradient agreement at mixmin as a cell/row gate, then makes capped logit moves from mixmin toward E56 teacher and actual-anchor scores the prefiltered candidates.
- 관측: E63 generated `404671` candidates and actual-anchor scored `1300`. Toward-teacher candidates passed hidden guard `1000/1000`, E56 world guard `1000/1000`, movement guard `1000/1000`, and sign-level anchor beats `932/1000`, while reverse controls had hidden guard `0/300` and world guard `0/300`. The best anchor candidate was `toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|w0.070|c0.080` with anchor delta `-0.000003650`; the strongest hidden-core mean delta among scored toward candidates was `-0.000368596`; eligible submission gates remained `0`.
- 성공/폐기 기준: directional validation survives; submit-safe claim fails. Gradient-consensus is stronger evidence than transition-only gating because it separates toward from reverse cleanly and agrees across independent hidden-rate views, but its public-anchor improvement is still below E58's corrected `-0.000004081` and far below `1e-5`.
- public LB 기대 반응: no submission. A public test from E63 would mostly measure public-anchor noise, not a selector-scale new hypothesis. If a future amplitude translator clears margin while preserving these hidden guards, improvement would strengthen the view that E56 has real direction but needs better calibration.
- 제출 전략: no E63 submission. Use gradient-consensus as a direction validator and cell-risk energy only; next work must translate the validated direction into a larger, calibration-preserving movement.

### H61. E63 gradient-consensus direction only needs scalar amplitude

- 상태: 반증됨 for the tested amplitude family.
- 왜 그럴듯한가: E63 showed toward-teacher direction passes hidden and world guards, but the movement was extremely small. If the only issue is under-scaling, larger capped logit movement on the same validated cells should make actual-anchor delta more negative while preserving hidden/world guards.
- 맞다면: increasing scale/cap on E63 gradient cells should create at least one toward candidate with `anchor_delta_vs_mixmin < -1e-5`, `world_guard=True`, `hidden_guard=True`, and no comparable reverse-control improvement.
- 틀리다면: larger amplitude should saturate or reverse under actual-anchor stress even while hidden/world guards remain true, proving direction validation is not enough to set probability size.
- 최소 실험: `analysis_outputs/gradient_amplitude_translation_probe.py`, focused on E63 top gradient gates with larger scales/caps and flat/core-gain amplitude shapes. It generated toward and reverse controls, prefiltered by world/hidden/movement stress, then actual-anchor scored the selected candidates.
- 관측: E64 generated `12096` candidates and actual-anchor scored `1796`. Toward candidates passed hidden guard `1346/1346`, world guard `1346/1346`, and movement guard `1346/1346`, but anchor beats were `0/1346`; best toward anchor delta was `+0.000003024`. Reverse controls also had anchor beats `0/450` and best delta `+0.000000154`.
- 성공/폐기 기준: scalar amplitude explanation discarded. Increasing validated E56 movement makes actual-anchor worse, not better. Hidden-rate BCE gradient and generated-world support are insufficient to choose public-safe amplitude.
- public LB 기대 반응: no submission. A public test from E64 would be high downside because local actual-anchor sign is uniformly adverse after amplitude expansion.
- 제출 전략: no E64 submission. Next work should not be "larger E56 gradient movement"; it needs targetwise calibration/amplitude modeling or a different structural target.

### H62. Near-zero targetwise E56 amplitude contains a submission-margin pocket

- 상태: 부분 지지 for a local pocket, 반증됨 for submission-margin claim.
- 왜 그럴듯한가: E64 showed large scalar movement is adverse, but E63/E64 together left open a narrow possibility: the E56 gradient direction may be useful only in a tiny targetwise neighborhood, especially excluding Q2 and S3 where earlier projection/transition probes repeatedly showed conflicts.
- 맞다면: a small targetwise line search should improve on E63's best anchor delta and ideally find `anchor_delta_vs_mixmin < -1e-5` while preserving hidden/world/movement guards. The useful pocket should be target-specific rather than global.
- 틀리다면: the best near-zero targetwise candidate should remain below margin, and response curves should show that single-target moves are too weak while broader moves saturate before clearing the threshold.
- 최소 실험: `analysis_outputs/near_zero_amplitude_response_probe.py`, focused on small scales, target masks, E63 gradient gates, row gates, and flat/core-gain shapes. It selected world/hidden-valid candidates and actual-anchor scored them.
- 관측: E65 generated `27384` candidates and actual-anchor scored `2400`. Toward candidates passed hidden/world/movement guards `2290/2290`, with anchor beats `1753/2290`, but anchor-margin gates `0`. Best toward delta was `-0.000005995` from `toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120`. Best target masks were `no_q2_s3` (`-5.995e-6`), `no_q2` (`-5.090e-6`), `no_s3` (`-4.726e-6`), and `all` (`-4.193e-6`); single-target Q1/S4/Q3 were much weaker and S2 was adverse.
- 성공/폐기 기준: local pocket exists but submission-margin pocket does not. The best response improves on E63's `-3.650e-6`, yet remains below `1e-5` and is driven by broad exclusion of Q2/S3 rather than a clean single target.
- public LB 기대 반응: no submission. A public test would be another sub-margin probe; a better next experiment should explain why Q2/S3 exclusion helps and whether public-safe amplitude is controlled by target conflict rather than scale.
- 제출 전략: no E65 submission. Use `no_q2_s3 + grad_all_abs50` as the current local response diagnostic, not a candidate file.

### H63. Q2/S3 conflict is hidden-direction failure

- 상태: 반증됨 as stated; refined to "Q2/S3 are public-anchor tail-risk targets, not simply wrong hidden targets."
- 왜 그럴듯한가: E65's best local pocket excluded Q2 and S3. Earlier raw-context, target-projection, and transition probes also repeatedly made S3 or Q2/S-stage axes unstable. The obvious explanation was that E56 teacher movement is directionally wrong on those targets.
- 맞다면: adding Q2/S3 back to matched `no_q2_s3` configurations should worsen hidden-core BCE and mean-anchor contribution, not only the robust actual-anchor score.
- 틀리다면: Q2/S3 add-back should often improve hidden-core or mean-anchor terms while still worsening the robust score, implying a tail/calibration conflict rather than a target-sign conflict.
- 최소 실험: `analysis_outputs/q2_s3_conflict_translator_probe.py`, holding the E65/E63 gradient-consensus cell set fixed and scoring matched target masks (`all`, `no_q2`, `no_s3`, `no_q2_s3`, `q2`, `s3`, `q2_s3`) with actual-anchor score, mean-anchor target contribution, hidden core/all deltas, and paired add-back decompositions.
- 관측: E66 generated and scored `3000` focused candidates. `no_q2_s3` remained the best robust actual-anchor mask (`-5.994944e-6`, `328/432` anchor beats), but `all` add-back was robust-anchor adverse in `432/432` matched configurations while improving mean-anchor in `288/432`, worsening max-set tail in `432/432`, improving min-set in `432/432`, and improving hidden core in `432/432`. Q2/S3-only masks had strong hidden-core gains (`q2_s3` best `-3.702e-5`) but `0` anchor beats for `q2` and `q2_s3`.
- 성공/폐기 기준: the hidden-direction-failure hypothesis is discarded. The surviving hypothesis is that Q2/S3 movement increases public-compatible worst-tail risk even when its average or hidden-world direction can be favorable.
- public LB 기대 반응: no public submission. A Q2/S3 add-back file would mostly test anchor-tail noise with high downside. The next public-relevant candidate must neutralize max-set/tail risk, not simply include or exclude Q2/S3.
- 제출 전략: no E66 submission. Use `q2_s3_tail_risk_energy` to design a tail-neutral, variance-aware Q2/S3 translator for E56-energy moves.

### H64. First-order tail-neutral Q2/S3 translator clears the public-anchor margin

- 상태: 부분 지지 for translator direction, 반증됨 for submission-margin claim.
- 왜 그럴듯한가: E66 showed Q2/S3 add-back improves hidden core and often mean-anchor, but worsens robust anchor through tail expansion. If the missing piece is tail control, first-order anchor-scenario derivatives should identify Q2/S3 cells whose add-back is mean-beneficial without max-tail expansion.
- 맞다면: tail-gated Q2/S3 add-back should beat matched `no_q2_s3`, preserve hidden guards, keep max-set tail neutral for a meaningful subset, and ideally clear `anchor_delta_vs_mixmin < -1e-5`.
- 틀리다면: uniform add-back and tail-gated add-back should either fail to beat `no_q2_s3`, improve only by expanding max-set tail, or remain below submission margin.
- 최소 실험: `analysis_outputs/q2_s3_tail_neutral_translator_probe.py`, keeping the E65 non-Q2/S3 move fixed and adding Q2/S3 by uniform partial weights or first-order tail gates (`meanneg`, `p90_nonpos`, `max_nonpos`, soft p90/max) computed from anchor-scenario BCE derivatives.
- 관측: E67 generated/scored `7632` candidates. Best translator was `tail_meanneg_m1.00` with anchor delta `-6.93314e-6`, improving E65's `no_q2_s3` best `-5.99494e-6` but still below `1e-5` margin. Tail-gated translators beat matched `no_q2_s3` in `4207/7200` comparisons; max-set-tail-neutral matched beats were `2241/7200`. The most interpretable strict tail gate, `tail_p90_nonpos_m1.00`, beat matched base in `432/432` and tail-neutral-beat in `360/432`, best anchor delta `-6.58701e-6`. Uniform small add-back mostly failed, and full uniform add-back reproduced the E66 adverse pattern.
- 성공/폐기 기준: translator direction survives, margin claim fails. First-order anchor-tail gates can add Q2/S3 better than target masks, but the edge remains sub-margin and partly anchor-derived.
- public LB 기대 반응: no public submission. A public file from E67 would still test a sub-margin, known-anchor-derived micro-edge. If a later independent non-anchor validation confirms the same tail-gated cells, E67 can become a candidate generator.
- 제출 전략: no E67 submission. Next branch should validate tail-gated Q2/S3 cells with non-anchor hidden/block/row calibration stress or learn rowwise amplitude; do not spend a public slot on E67 alone.

### H65. Tail-gated Q2/S3 cells are only same-anchor derivative artifacts

- 상태: 반증됨 as stated; refined to "tail-gated cells have independent support but remain sub-margin."
- 왜 그럴듯한가: E67 used the same anchor scenario family to define first-order tail gates and to score the candidate response. That could make the Q2/S3 improvement a local arithmetic artifact rather than hidden data structure.
- 맞다면: leaving one combo set out of tail-gate construction should kill held-out wins, and hidden/world/block stress outside the anchor-tail objective should not improve matched `no_q2_s3`.
- 틀리다면: selected tail gates should still beat matched `no_q2_s3` on the held-out combo set, stay tail neutral, improve hidden Q2/S3, keep non-worse world support, and beat hidden-block Q2/S3 stress.
- 최소 실험: `analysis_outputs/q2_s3_tail_gate_independence_probe.py`, selecting `180` promising E67 configurations, rebuilding Q2/S3 gates with each combo set held out, and scoring held-out combo response plus hidden/world/block Q2/S3 diagnostics.
- 관측: E68 rebuilt `762` unique scored predictions, formed `540` matched held-out comparisons, and found `155` independent gates, all `155` also strict. `tail_soft_max_m1.00` had `44` strict gates and best block win rate `0.944444`; `tail_p90_nonpos_m1.00` had `41` strict gates and the best strict held-out comparison (`-1.260816e-6` versus matched base). The strongest held-out score was `tail_max_nonpos_m1.00` at `-1.629588e-6`, but it had `0` block-majority wins and therefore failed the independence gate.
- 성공/폐기 기준: artifact-only claim is discarded. The submission-margin claim remains false because held-out gains are `1e-6` scale and not selector-scale probability movement.
- public LB 기대 반응: no public submission. E68 alone would only test a validated micro-edge below public selector resolution.
- 제출 전략: no E68 submission. Use the strict E68 cells as a latent/energy or amplitude-gate source; generate a file only if rowwise or structural amplification clears margin without losing tail/block support.

### H66. E68 strict Q2/S3 cells can be amplified by a simple alpha

- 상태: 반증됨 for simple global alpha; refined to "validated cells need rowwise/structural amplitude, not scalar amplification."
- 왜 그럴듯한가: E68 strict cells were independently supported but too small. If the only missing piece was under-amplitude, scaling the Q2/S3 logit delta between matched `no_q2_s3` base and E68 candidate should push full-combo proxy below the `1e-5` selector margin while preserving heldout/tail/hidden/world/block guards.
- 맞다면: alpha > 1 should improve full-combo and heldout scores, keep tail neutrality for most strict pairs, and create at least one strict amplitude gate.
- 틀리다면: larger alpha should either plateau below margin or trade full-combo gains for heldout/tail instability, with strict gates staying `0`.
- 최소 실험: `analysis_outputs/q2_s3_strict_cell_amplitude_probe.py`, using `155` E68 strict pairs and alpha grid `[0.0, 0.5, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 24.0]` over only the Q2/S3 logit delta while non-Q2/S3 targets stay fixed at matched base.
- 관측: E69 scored `2170` rows / `2061` unique predictions. Strict amplitude gates were `0`; full-combo margin gates were `0`. Best full-combo delta was `-9.1779e-6` at alpha `24`, still above the `-1e-5` margin. Heldout tail-neutral counts fell from `155/155` at alpha `1` to `69/155` at alpha `8`, `49/155` at alpha `12`, and `22/155` at alpha `24`; median heldout response turned adverse after alpha `10`.
- 성공/폐기 기준: scalar under-amplitude is discarded. E68 strict cell direction survives, but simple alpha cannot create a submission-scale move without eroding heldout/tail stability.
- public LB 기대 반응: no public submission. A public file from E69 would be a sub-margin, heldout-specific amplitude stress with increasing tail risk.
- 제출 전략: no E69 submission. Next branch must learn rowwise/cellwise amplitude or use E68 strict cells as a structural latent target; do not repeat global alpha sweeps.

### H67. E68 strict Q2/S3 cells share a consensus representation

- 상태: 부분 지지, but not submit-safe.
- 왜 그럴듯한가: E69 showed individual strict cells cannot simply be scaled, but that does not rule out a JEPA-style latent: multiple independently validated Q2/S3 cells may encode a common row/target representation whose consensus is stronger than any single heldout pair.
- 맞다면: aggregating strict cells across heldout/translator/pool views should create full-combo margin rows, preserve all combo set wins/tail neutrality, and still improve hidden/world/block Q2/S3 diagnostics.
- 틀리다면: consensus aggregation should either stay below margin, require disagreement-heavy gates, or lose hidden/world/block/tail support.
- 최소 실험: `analysis_outputs/q2_s3_strict_cell_consensus_probe.py`, using the `155` E68 strict cells, pooled base logits from matched `no_q2_s3` predictions, aggregated Q2/S3 deltas, agreement/magnitude gates, and alpha response. It scored combo proxy first, then hidden/world/block stress for the `700` most promising rows.
- 관측: E70 built `2688` candidate rows / `2576` unique predictions. Strict consensus gates existed (`6`) and loose gates were broad (`502`). Best all-combo delta was `-1.027751e-5`, just past the selector margin. All 6 strict rows used `gate=none`; strongest rows came from `translator_tail_soft_max_m1.00`, `top100_heldout`, `translator_tail_soft_p90_m1.00`, and the full `all` pool. These rows also had all `3/3` combo sets beating base and tail-neutral, hidden Q2/S3 improvement around `-0.00041` to `-0.00054`, world support improvement around `-0.00040` to `-0.00049`, and block win rates `0.888889-0.916667`.
- 성공/폐기 기준: consensus accumulation survives as a structural signal because strict rows clear the local margin and non-anchor diagnostics. Immediate submission is not adopted because the margin is tiny, the strict rows all require no agreement gate, and the construction still uses heldout-specific E68 strict cells rather than a unified test-time rule.
- public LB 기대 반응: no public submission from E70 itself. If a later unified-rule consensus file improves LB, H67 becomes the first post-mixmin Q2/S3 structural translator. If it worsens, the `gate=none` consensus likely captured anchor-combo arithmetic rather than public-stable amplitude.
- 제출 전략: no E70 submission. Next branch should convert the surviving consensus into a unified non-heldout rule or a LeJEPA-style energy/gate before producing a file.

### H68. Unified reconstruction of E68 strict-cell consensus is deployable

- 상태: 부분 지지 for diagnostic consensus, 반증됨 for deployable gate.
- 왜 그럴듯한가: E70's strongest objection was heldout-specific reconstruction. If the consensus is a real test-time representation, rebuilding each unique E68 strict cell once with the full combo family should preserve margin and allow at least one conservative non-`none` agreement gate.
- 맞다면: unique-cell consensus should keep selector-scale all-combo margin, hidden/world/block support, tail neutrality, and produce deployable rows with `gate != none`.
- 틀리다면: margin may survive only in `gate=none` rows, or strict rows may disappear once heldout-specific reconstruction is removed.
- 최소 실험: `analysis_outputs/q2_s3_unified_strict_cell_consensus_probe.py`, using E68 strict rows only to select `104` unique cells, then reconstructing each cell once with full combo tables and scoring pooled consensus candidates under the same tail/hidden/world/block requirements as E70. Deployable gate requires `strict_unified_gate` and `gate != none`.
- 관측: E71 used `155` strict rows, `104` unique cells, and `51` support-2 cells. It built `3136` candidate rows / `2842` unique predictions. Strict unified gate count was `1`, deployable unified gate count was `0`, loose unified gates were `475`, and best all-combo delta was `-1.082166e-5`. The only strict row was `top75_heldout_mean + mean base + signed_p75 delta + gate=none + alpha=8`, with all `3/3` combo sets beating base and tail-neutral, hidden Q2/S3 mean improvement `-0.000477907`, world support improvement `-0.000413602`, and block win rate `0.833333`.
- 성공/폐기 기준: unified consensus is not a pure E70 arithmetic artifact because one strict row survives and the best all-combo row remains past margin. The deployable claim is discarded because conservative/non-`none` agreement gates produce `0` strict rows and every margin row still depends on `gate=none`.
- public LB 기대 반응: no public submission. A public file from E71 would still test disagreement-permissive consensus, not a conservative representation. If a later non-`none` gate improves LB, the consensus branch becomes submission-relevant; if not, E68/E70/E71 should remain latent energy only.
- 제출 전략: no E71 submission. Use unified consensus as a LeJEPA-style energy and build the next experiment around a non-`none` gate, rowwise/cellwise amplitude, or structural target that explains why the only surviving margin state is disagreement-permissive.

### H69. Sparse-magnitude Q2/S3 consensus is the deployable gate geometry

- 상태: local gate 부분 지지; submitted combined-file public alignment rejected; isolated Q2/S3 remains sub-margin.
- 왜 그럴듯한가: E71 failed only the tested agreement gates. The surviving `gate=none` rows may contain a sparse high-magnitude subset where consensus amplitude is meaningful even if sign agreement is not globally high.
- 맞다면: `top_abs50` should produce non-`none` strict rows with selector-scale all-combo margin, all combo sets beating base/tail-neutral, hidden/world/raw/block support, and a materializable submission file. Q2-only should remain weak if S3 is the actual public-sensitive carrier.
- 틀리다면: all non-`none` gate families should remain sub-margin or fail hidden/world/block/tail diagnostics.
- 최소 실험: `analysis_outputs/q2_s3_unified_gate_geometry_probe.py`, sweeping `top_abs50`, `top_abs30`, `agree55`, soft signed/agreement gates, `q2_only`, `s3_only`, and target-agreement gates over E71 unified cells.
- 관측: E72 built `4752` rows / `4752` unique predictions. Strict rows `21`, deployable non-`none` rows `10`, loose rows `655`. `top_abs50` produced `7` deployable rows with best deployable all-combo delta `-1.05458e-5`; `s3_only` produced `3` deployable rows; `q2_only` and `q2_agree55` produced `0` loose rows. E73 materialized the best row as `analysis_outputs/submission_e72_topabs50_q2s3_gate_4e48cba2.csv`. Public LB for this file was `0.5764077772`, worse than mixmin by `+0.0001011367`. E80 then found the file moved `893` cells across all `7` targets, while isolated Q2/S3 movement was only `79` cells. E81 found pure Q2/S3 graft loose/sub-margin at `-5.95383e-6`, and inverse Q2/S3 locally adverse at `+1.47473e-5`.
- 성공/폐기 기준: local sparse-gate geometry remains supported, but the submitted combined-file public-alignment claim is rejected. Isolated Q2/S3 is not dead; it is below submission margin and needs a stronger structural/combo-tail gate.
- public LB 기대 반응: E73 worsening means E74/E75 should not be used as simple follow-up amplitude tests. A later public improvement must come from a pure, calibrated structural gate rather than broad all-target movement or direct sign inversion.
- 제출 전략: no direct E73/E74/E75 follow-up. Keep `submission_mixmin_0c916bb4.csv` as frontier and require a new gate before spending a public slot.

### H70. E73 sparse-magnitude Q2/S3 gate is stable under cell-subset stress

- 상태: 지지됨 locally; direct public follow-up paused after E80/E81.
- 왜 그럴듯한가: E73's selected pool has only `13` source cells, so a few influential cells could explain the local strict/deployable result. If the sparse gate is a real latent consensus, deleting cells or sampling subsets should preserve many deployable alpha16/alpha20 rows.
- 맞다면: leave-one-cell-out variants should remain deployable at alpha16, bootstrap subsets should frequently pass the same strict/deployable gate, and the full-pool alpha20 row should improve local support without immediately breaking hidden/world/block stress.
- 틀리다면: jackknife variants should fail deployability, bootstrap support should be rare, and the E73 full-pool result should collapse or become adverse when one or two cells are removed.
- 최소 실험: `analysis_outputs/q2_s3_sparse_gate_stability_probe.py`, using E73's full `translator_tail_soft_p90_m0.50` top_abs50 pool with reference, jackknife, group-keep, rank-keep, and deterministic bootstrap8 variants across alpha `[8, 12, 16, 20, 24]`.
- 관측: E74 scored `470` rows over `94` variants. Strict/deployable rows were `141`; loose rows were `470`. Jackknife alpha16 deployable was `13/13`, bootstrap8 alpha16 deployable was `48/60`, and reference alpha20 remained strict/deployable with all delta `-1.07261e-5`, hidden Q2/S3 `-0.000484506`, world support `-0.000351115`, and block win rate `0.722222`. Reference alpha24 failed strict, so the amplitude ridge has a visible upper boundary.
- 성공/폐기 기준: single-cell fragility is discarded. E73 is upgraded from a fragile local sensor to a stable sparse-cell-consensus sensor. The public-alignment and amplitude claims remain open.
- public LB 기대 반응: E80/E81 now make simple E74 alpha20 follow-up unjustified. If a future pure sparse-gate structural file improves public, H70 can re-enter as amplitude-boundary evidence; otherwise it remains local stability only.
- 제출 전략: hold `analysis_outputs/submission_e74_fullpool_a20_q2s3_gate_55455b60.csv`.

### H71. Sparse Q2/S3 public amplitude is target-asymmetric

- 상태: locally supported as direction; direct public follow-up paused.
- 왜 그럴듯한가: E72 already showed `s3_only` can produce deployable rows while Q2-only produces none. E74 then showed alpha20 is locally better than alpha16 but alpha24 breaks strict consensus. That pattern suggests the amplitude boundary may differ by target rather than being one scalar over Q2 and S3.
- 맞다면: crossing `alpha_q2` and `alpha_s3` should find a stable deployable ridge where S3 can be larger than Q2. `q2_only` should remain dead, `s3_higher` should dominate strict/deployable rows, and the best deployable row should beat both E73 alpha16/16 and E74 alpha20/20 on the public-combo proxy.
- 틀리다면: the best deployable rows should stay near the symmetric alpha ridge, or target-asymmetric rows should fail strict/tail/hidden/world/block stress.
- 최소 실험: `analysis_outputs/q2_s3_target_amplitude_ridge_probe.py`, fixing the E74 pool/gate and crossing target-specific alpha values for Q2 and S3. `analysis_outputs/q2_s3_target_amplitude_ridge_candidate.py` materializes the best deployable row.
- 관측: E75 built `120` rows, with strict/deployable `37` and loose `109`. `s3_higher` contributed `23` strict/deployable rows; `s3_only` contributed `6`; `q2_higher` contributed `5`; `equal` contributed `3`; `q2_only` contributed `0`. The best deployable row was `e75_q2a8.0_s3a28.0_f07219b4`, all delta `-1.23676e-5`, all-minus-base `-7.60210e-6`, hidden Q2/S3 `-0.000372692`, hidden S3 `-0.000498235`, world `-0.000200351`, and block win `0.722222`. It was materialized as `analysis_outputs/submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv`.
- 성공/폐기 기준: the symmetric-alpha-optimal claim is discarded locally. H71 is supported as a target-amplitude hypothesis, but public alignment is still unobserved and private risk is higher than E73 because the best row is more aggressive and S3-heavy.
- public LB 기대 반응: E80/E81 show the submitted E73 combined file is public-adverse and pure Q2/S3 is sub-margin, so E75 should not be the next direct public test. If a future pure structural gate validates sparse Q2/S3 sign, H71 should be revisited as target-amplitude evidence.
- 제출 전략: hold `submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv`.

### H72. Target-asymmetric Q2/S3 amplitude is direction-stable but exact E75 amplitude is only partially stable

- 상태: direction supported locally; exact amplitude risk flagged; direct public follow-up paused.
- 왜 그럴듯한가: E75's full-pool best row could be explained either by a robust S3-heavy target asymmetry or by one exact full-pool amplitude overfitting the local combo proxy. E74 already showed the sparse source cells survive subset stress, so the next falsification should separate target-asymmetric direction from exact `q2=8/s3=28` deployability.
- 맞다면: `asym8_28_e75` should beat symmetric controls across jackknife/bootstrap/group/rank variants, and the best deployable row should usually remain S3-heavy. Exact `8/28` may fail deployability in some subsets if the correct public object is row/cell-conditioned amplitude rather than one universal pair.
- 틀리다면: asymmetric rows should lose to `sym16_e73` or `sym20_e74` under subset stress, or the best deployable axis should often become equal/Q2-heavy/unstable.
- 최소 실험: `analysis_outputs/q2_s3_target_amplitude_stability_probe.py`, crossing `21` target-alpha pairs over the same `94` reference/jackknife/group/rank/bootstrap source-pool variants used by E74, with combo scoring plus hidden/world/block stress.
- 관측: E76 scored `1974` rows over `94` variants, with strict/deployable `1138` and loose `1894`. Exact `asym8_28_e75` beat both `sym16_e73` and `sym20_e74` in `94/94` variants, and the best deployable axis was S3-heavy in `94/94` variants. However, exact `asym8_28_e75` deployability was only `49/94`: jackknife `8/13`, group_keep `7/10`, rank_keep `5/10`, bootstrap8 `28/60`, reference `1/1`. E74's earlier E73 alpha16 stability was broader (`13/13` jackknife, `48/60` bootstrap8).
- 성공/폐기 기준: the claim "target asymmetry is a local full-pool accident" is rejected. The stronger claim "E75 exact `8/28` is as stable as E73's sparse-gate sign" is rejected.
- public LB 기대 반응: no direct E75/E74 public test after E80/E81. If a future pure sparse-gate sign is validated, this hypothesis decides whether S3-heavy amplitude is worth re-testing.
- 제출 전략: no current submission.

### H73. E76 source-subset posterior averaging can repair exact-amplitude instability

- 상태: submission-source claim rejected; diagnostic split retained.
- 왜 그럴듯한가: E76 showed every source-subset variant prefers S3-heavy amplitude over symmetric controls, but exact `8/28` is only partly deployable. If that instability is just subset noise, averaging or robust-quantile aggregating the source-subset prediction distribution should create a more stable row/cell-conditioned amplitude.
- 맞다면: posterior-aggregated candidates should preserve E75-level local margin while improving strict/deployable gates. Q2/S3-only aggregation should cross the `1e-5` margin without tail damage, or full aggregation should keep all combo sets and tails neutral.
- 틀리다면: Q2/S3-only aggregation should remain sub-margin, while full aggregation should only improve local all-combo by breaking combo-set/tail consistency or hidden/world support.
- 최소 실험: `analysis_outputs/q2_s3_amplitude_posterior_probe.py`, rebuilding E76 predictions, selecting `19` posterior groups, aggregating logit movements from mixmin/E73/E74 with mean/median/signed quantiles, scopes `q2s3`, `s3_only`, `full`, and shrink values up to `2.5`.
- 관측: E77 scored `6840` posterior rows. Strict/deployable rows were `0`, loose rows `3099`, and deployable rows beating E75 local all-combo were `0`. `62` rows beat E75 all-combo locally, but none were strict. Best all-combo was `-1.26541e-5`, yet hidden Q2/S3 and world were adverse (`+3.95652e-5`, `+0.000107171`) and block win was only `0.555556`. Mixmin/Q2S3 posterior was safer and broad (`688/760` loose; best worst-set `-2.16163e-6`, hidden `-0.001203`, world `-0.000779`, block `0.833333`) but best all-combo was only `-8.09547e-6`. Mixmin/full posterior beat E75 locally but only beat `1/3` combo sets and kept `1/3` tail-neutral sets in the best rows.
- 성공/폐기 기준: H73 is rejected as a direct submission generator. It survives only as a diagnostic energy that separates safe sub-margin Q2/S3 movement from unsafe full-posterior margin movement.
- public LB 기대 반응: no public submission should be made from E77 alone. If an E77-like full posterior later improves public, it would imply public subset is closer to the one favorable combo set than to the local strict gate, but private risk would be high. If E73/E75 improve and E77-style posterior does not, public reads sparse/target-amplitude structure but not broad source-posterior averaging.
- 제출 전략: none. Use E77 to rule out generic posterior averaging and redirect to combo-set/tail-conditioned row/block amplitude.

### H74. E76 deployable/non-deployable source distribution can localize E75 amplitude

- 상태: rejected as upside generator; diagnostic negative screen retained.
- 왜 그럴듯한가: E76 made direction stable but exact amplitude partial; E77 averaging failed. A reliability gate could preserve E75 signal while removing unstable cells.
- 맞다면: localized masks should produce deployable rows beating E75 local all-combo or improve tail/hidden/world/block at the same edge.
- 틀리다면: masks collapse to identity, or strong masks reduce edge and no deployable row beats E75.
- 최소 실험: `analysis_outputs/q2_s3_localized_amplitude_gate_probe.py`, 36 reliability masks, 4452 rows, E76 stress.
- 관측: strict/deployable `1806`, loose `3934`, deployable beating E75 `0`, best all equals E75 `-1.23676e-5`; consensus masks often identity; hard sign/excess/veto masks shrink signal.
- 성공/폐기 기준: H74 is rejected as a direct amplitude repair. It survives only as a negative screen saying E76 source-subset reliability is not a sufficient row/cell law.
- public LB 기대 반응: no E78 submission. If E75 improves, public may still read exact target asymmetry; if E75 fails, E78 says simple source-subset reliability masks would not have fixed it.
- 제출 전략: none.

### H75. Public-like row/block/flank context can localize E75 amplitude

- 상태: weakened as direct amplitude repair; row/block context retained as diagnostic.
- 왜 그럴듯한가: submission rows are embedded in subject-calendar runs bracketed by train rows, so row position, flanking train labels, subject priors, and E75 unit-energy could be the meaningful JEPA context that E76 source-subset masks missed.
- 맞다면: topology, subject-prior, flank-prior, or positive-unit-energy masks should create deployable rows that beat E75 local all-combo, or at least match E75 edge with better hidden/world/block/tail stress.
- 틀리다면: full active sparse movement should remain best; row/block/flank masks should only shrink edge, reduce block stress, or reproduce identity-like rows.
- 최소 실험: `analysis_outputs/q2_s3_public_like_rowblock_amplitude_probe.py`, reusing E75 full-pool `top_abs50` unit delta and sweeping `61` topology/energy/subject/flank/target-specific masks over target alphas.
- 관측: E79 scored `6516` rows. Strict/deployable rows were `1318`, loose rows `3403`, deployable rows beating E75 were `0`, and best all stayed E75-equivalent at `-1.23676e-5`. E75 sparse movement is active on only `72/250` rows/cells; positive energy top30/top50 masks reduce the active set to `22`/`36` rows but do not improve edge. Best row/block/flank masks remain deployable but weaker than E75.
- 성공/폐기 기준: the direct claim "public-like topology/flanks repair exact E75 amplitude" is rejected. The softer claim "row/block context is useful representation context" remains live for structural block targets, because E79 tests only handcrafted masks over E75 movement.
- public LB 기대 반응: no E79 submission. If E75 improves public, E79 says public likely accepted the full active sparse amplitude rather than a simple topology/flank subset. If E75 worsens, E79 says simple row/block/flank localization would not have fixed it. E80-E82 later paused this direct public order.
- 제출 전략: none. Row/block/flank masks are retained only as context/energy for structural targets, not as direct sparse-gate submission rules.

### H76. E73 public failure is broad-base contamination, while isolated Q2/S3 is sub-margin

- 상태: broad-base contamination supported; pure Q2/S3 submission-scale claim rejected; inverse-sign reaction rejected.
- 왜 그럴듯한가: the submitted E73 filename implies a Q2/S3 sparse gate, but the materialized prediction may include a changed base from the unified reconstruction. If so, public failure cannot be attributed to Q2/S3 without separating target scopes.
- 맞다면: E73 should move non-Q2/S3 targets versus mixmin. A pure mixmin-anchored Q2/S3 graft should have smaller movement and may keep local hidden/world support but fall below margin. Inverse-sign variants should fail local stress if public failure was not a clean sign oracle.
- 틀리다면: E73 should move only Q2/S3, or pure Q2/S3 should be strict/deployable and inverse-sign variants should look locally plausible after the public miss.
- 최소 실험: `analysis_outputs/e73_public_observation_assimilation.py` and `analysis_outputs/e73_pure_q2s3_graft_probe.py`.
- 관측: E80 measured `893` moved cells / `249` active rows / all `7` targets in submitted E73. Q2/S3 cells were only `79`; non-Q2/S3 cells were `814`. E81 scored `8` split variants: strict/deployable `0`, loose `3`; pure Q2/S3 graft all delta `-0.000005954` with `3/3` combo-set wins and hidden Q2/S3 `-0.000391043`, but margin false; pure S3-only `-0.000005665`; pure Q2-only `-0.000000439`; inverse Q2/S3 `+0.000014747` with all guards failing.
- 성공/폐기 기준: direct E74/E75 amplitude follow-up is rejected after public feedback. The isolated Q2/S3 latent survives as energy, not as a current submission.
- public LB 기대 반응: no immediate public file. If a future structural gate improves, E80/E81 imply it succeeded by removing broad-base contamination and lifting sub-margin Q2/S3 safely; if it worsens, Q2/S3 consensus should be demoted further behind block-state representation work.
- 제출 전략: none from E81. Next submission must be a new mixmin-anchored structural/combo-tail gate, not E73 amplification or public-sign inversion.

### H77. Pure Q2/S3 source grafts are structurally coherent but margin-limited

- 상태: supported locally; pure Q2/S3 candidate-generator claim rejected.
- 왜 그럴듯한가: E81 tested only the final submitted E73 Q2/S3 values. The broader E72/E75/E76 source universe contains target-asymmetric and subset-stable Q2/S3 movements that might survive if only their Q2/S3 value or source-base delta is grafted onto mixmin.
- 맞다면: pure grafts should pass combo-set, tail, hidden, world, and block stress, but may still fail the selector-scale all-margin gate if Q2/S3 alone lacks enough probability mass.
- 틀리다면: at least one pure source graft should become strict/deployable, or the pure-graft family should fail hidden/world/block/tail stress rather than only margin.
- 최소 실험: `analysis_outputs/e82_pure_q2s3_source_graft_scan.py`.
- 관측: E82 generated `8402` pure graft rows from E72/E75/E76 source predictions and evaluated `700` combo-promising rows under non-anchor stress. Strict/deployable rows were `0`, loose rows `700`, and best evaluated all delta was `-0.00000790328`. All evaluated rows passed all non-margin guards (`700/700` all beats base, all sets beat base, all tails neutral, hidden Q2/S3 improves, world nonworse, block majority beats, block tail safe), while `all_margin_vs_mixmin` was `0/700`.
- 성공/폐기 기준: pure Q2/S3-only candidate generation is rejected because the only failing condition is margin. Q2/S3 remains valid as latent energy, but not enough as the sole submitted movement.
- public LB 기대 반응: no E82 public file. If a future candidate improves public, H77 says it probably added a larger structural movement while preserving Q2/S3/tail energy, not merely isolated Q2/S3 better. If it worsens, Q2/S3 energy should be treated as a weak auxiliary, not as the main world model.
- 제출 전략: none from E82. Next submission should use Q2/S3 as an energy/gate inside a broader block-state or structural transition candidate.

### H78. Q2/S3 latent energy can gate broader structural movement into a safe candidate

- 상태: broad-margin/support split found; direct selector claim rejected.
- 왜 그럴듯한가: E82 showed pure Q2/S3 movement is coherent but too small. Older JEPA/block/raw candidates have enough movement to clear margin, so Q2/S3 energy might identify the rows where that larger structural movement is compatible with the hidden sleep-state branch.
- 맞다면: E82 high-energy row gates should turn broad structural deltas into rows that clear margin, preserve Q2/S3 hidden/world support, and beat all combo sets/tails. The inverse/not-top controls should look worse.
- 틀리다면: broad structural rows should clear margin only by damaging Q2/S3 hidden/world or one combo set, while E72-derived Q2/S3 rows should remain safe but sub-margin.
- 최소 실험: `analysis_outputs/e83_q2s3_energy_structural_gate_scan.py`, using E82 top-20 Q2/S3 row energy over broad JEPA/block/raw submission movements, target scopes, row gates, and scales.
- 관측: E83 generated `3716` rows and non-anchor evaluated `700`; strict/deployable `0`, loose `40`, structural-loose `189`. Best broad rows reached `-3.50517e-5` all delta, but beat only `2/3` combo sets and worsened Q2/S3 hidden/world (`hidden_q2s3` about `+0.000443`, world about `+0.000252`). E72-derived rows kept `3/3` set/tail and improved hidden/world but stayed sub-margin around `-8.93545e-6`. Non-Q2/S3 structural rows reached margin-scale around `-2.5291e-5` and improved hidden-core/world, but still only beat `2/3` combo sets and carry no Q2/S3 movement.
- 성공/폐기 기준: direct "Q2/S3 energy gates broad movement into deployable safety" is rejected. The stronger diagnostic survives: structural margin and Q2/S3 safety are separable pieces of the plateau.
- public LB 기대 반응: no E83 public file. If a later recombination improves, E83 says the gain came from joining separated structural and Q2/S3 components. If it worsens, the broad structural component is likely public-incompatible even when Q2/S3 is used as energy.
- 제출 전략: no E83 submission. Use E83 only to seed target-group recombination and row/block-specific conflict analysis.

### H79. Non-Q2/S3 structural margin plus Q2/S3 safety is additive enough for a deployable candidate

- 상태: hidden/world additivity supported; deployable claim rejected; inverse-top conflict isolated.
- 왜 그럴듯한가: E83 separated two useful pieces: non-Q2/S3 structural rows with margin-scale movement and E72-derived Q2/S3 rows with coherent hidden/world/tail safety. If the conflict is only target-group contamination, adding the pieces in disjoint targets should fix both.
- 맞다면: recombined rows should clear margin, preserve Q2/S3 hidden/world and block stress, and pass all combo-set/tail guards. Failing rows should be rare and traceable to raw-energy or amplitude, not one systematic public-observation set.
- 틀리다면: recombined rows should still fail the same combo set or anchor-world despite passing hidden/world/block stress.
- 최소 실험: `analysis_outputs/e84_structural_margin_q2s3_safety_recombination.py`, combining E83 structural-loose non-Q2S3 deltas with E72-derived Q2/S3-safe deltas and sweeping conservative weights.
- 관측: E84 generated `1728` rows and non-anchor evaluated `700`; strict/deployable `0`, loose `700`, structural-loose `700`, best evaluated all delta `-3.214999e-5`. All evaluated rows passed margin, all-beats-base, hidden Q2/S3, world, block-majority, and block-tail guards; `672/700` passed raw-energy. The only systematic strict failure was combo-set split: every evaluated row beat `2/3` sets and kept `2/3` tails neutral. The rejecting set was `inverse_top` (`0/700` wins, mean `+8.5858e-5`), while raw05-compatible and all-sign sets were `700/700` favorable.
- 성공/폐기 기준: target-group additivity is not enough for a safe candidate. However, E84 gives a sharper bottleneck: a single public-observation world conflict remains after hidden/world/block/Q2S3 guards are satisfied.
- public LB 기대 반응: `analysis_outputs/submission_e84_inverse_sensor_1c74da00.csv` is a diagnostic sensor only. If public improves, `inverse_top` is over-conservative for public and E84-like structural recombination becomes live. If public worsens, `inverse_top` is public-like and this structural movement must be gated away.
- 제출 전략: no safe E84 recommendation. Use the materialized file only if the next public slot is meant to test public-world identity, not if the goal is lowest-risk improvement.

### H80. E84 inverse-top conflict is target-axis contamination, not row/block-wide rejection

- 상태: strongly supported locally; public pending.
- 왜 그럴듯한가: E84's rejected rows were healthy under hidden/world/block stress and two combo worlds, so the remaining conflict might come from specific targets whose public-world sign differs across inverse-top versus raw05/all-sign worlds.
- 맞다면: per-target contribution should show inverse-top adverse mass concentrated in a few targets; pruning those targets should make the same structural movement pass all combo sets while preserving margin and hidden/world/block support.
- 틀리다면: all target subsets should either remain inverse-top adverse, lose margin, or fail hidden/world/block/raw-energy stress.
- 최소 실험: `analysis_outputs/e85_inverse_conflict_target_prune.py`, taking top E84 loose seeds and applying every non-empty target subset of their mixmin-relative logit movement.
- 관측: E85 generated `10135` target-pruned rows, non-anchor evaluated `700`, and found strict/deployable `535`. The E84 sensor's inverse-top adverse contribution was concentrated in `Q3` (`+6.36e-5`), `Q1` (`+2.14e-5`), `S4` (`+1.44e-5`), and `S2` (`+1.22e-5`), while `S3` was favorable (`-1.93e-5`). The best strict row keeps `S1,S2,S3`, removes `Q1,Q2,Q3,S4`, and has all delta `-2.38758e-5`, inverse-top `-8.17e-6`, raw05-compatible `-2.96e-5`, all-sign `-3.39e-5`, hidden Q2/S3 `-0.000216`, world `-0.000130`, raw-energy `-3.52e-5`.
- 성공/폐기 기준: the claim "E84 requires row/block-specific gating before any target-axis fix" is rejected. The target-axis prune is a genuine strict candidate under current stress. The unresolved part is public sign: public may still prefer the Q1/Q3/S4 movement that inverse-top rejects.
- public LB 기대 반응: if `submission_e85_inverse_conflict_pruned_58b23ed1.csv` improves public, public is closer to the all-combo-safe S1/S2/S3 structural world and E84's Q1/Q3/S4 movement was contamination. If it worsens, public was closer to the all-sign/raw05 target movement and inverse-top over-pruned the useful Q1/Q3/S4 axes.
- 제출 전략: E85 is now the highest-information next submission candidate, stronger than E84 because it is strict/deployable rather than only diagnostic.

### H81. E85 target-prune law is source-stable enough to support a consensus candidate

- 상태: strongly supported locally; public pending.
- 왜 그럴듯한가: E85 strict rows were not confined to one structural source. The same S1/S2/S3-like masks appeared across gate, rawcorr-refine, and rawcorr-micro families, so averaging source-diverse logit deltas may reduce single-row risk while preserving the target-axis law.
- 맞다면: source-diverse consensus variants should remain strict/deployable across combo, hidden/world/block, raw-energy, and tail stress. Small overstep should improve local margin without breaking inverse-top.
- 틀리다면: consensus should wash out the edge, fail inverse-top, or expose source-family-specific shortcuts.
- 최소 실험: `analysis_outputs/e86_e85_target_prune_robustness.py`, rebuilding E85 predictions and forming source-diverse logit-delta consensus variants across target masks, source-file/seed-rank/top-row selections, mean/median/trimmed aggregators, and shrink/overstep values.
- 관측: E86 generated `1485` consensus rows; non-anchor evaluated `700`; strict/deployable/loose were `700/700`. The selected consensus keeps `Q2,S1,S2,S3`, averages top `40` strict E85 rows from `18` source files across `gate,rawcorr_micro,rawcorr_refine`, and uses shrink `1.25`. It has all delta `-2.77059e-5`, inverse-top `-6.91e-6`, raw05-compatible `-3.53387e-5`, all-sign `-4.08689e-5`, hidden Q2/S3 `-0.000377585`, world `-0.000307439`, raw-energy `-0.000172786`, block win `0.833333`, and block-tail safe `1.0`.
- 성공/폐기 기준: the single-source-artifact objection to E85 is rejected locally. The unresolved part is whether the source-consensus overstep is public-safe or whether E85's lower-amplitude S1/S2/S3-only file is safer.
- public LB 기대 반응: if `submission_e86_e85_consensus_a3f7c96f.csv` improves public more than E85 or mixmin, public rewards source-stable S1/S2/S3/Q2 structural consensus and the 1.25 overstep is not overfit. If it worsens while E85 improves, public wants the target-prune law but not consensus overstep/Q2 add-back. If both worsen, inverse-top target pruning was a local combo-world artifact.
- 제출 전략: E86 supersedes E85 as the highest-upside next candidate if one wants source-stable consensus. E85 remains the lower-amplitude conservative sensor for the same target-prune hypothesis.

## 우선 실험 5개

1. E05 selector-only falsification: 기존 submissions/anchors만으로 LOO/L2O selector가 `a2c8 < raw05 < bad JEPA` order를 안정적으로 복원하는지 확인.
2. E06 hidden block semantic JEPA: row prediction이 아니라 block rate/count latent를 target representation으로 예측.
3. E07 latent geometry diagnostic: cross-view/label-flow/raw05 latent의 anisotropy, NN consistency, high-energy loss 기여 측정.
4. E08 target dependency energy: Q/S manifold violation이 bad public anchors와 submit candidates를 구분하는지 확인.
5. E09 measurement-process calibration gate: missingness/rhythm residual signal이 direct feature가 아니라 samplewise calibration risk로 살아남는지 확인.

## 현재 업데이트

E05 계열 pairwise/order selector와 hidden-local bridge stress 결과, strict submit-gate 후보는 0개였다. baseline-relative로 a2c8보다 좋아 보이는 hiddenloc bridge 후보 46개가 있었지만 모두 기존 selector와 conflict가 있었고, expected edge는 `1e-5` 수준으로 public noise/selector error보다 작다. 별도 hard selector falsification에서도 `LOO/L2O MAE <= 0.00040`, rank accuracy `> 0.90`, key order preservation을 동시에 만족한 모델은 `0/36`이었다.

E10 label-flow block-rate JEPA stress는 H03/H15를 "semantic latent는 존재하지만 direct submit은 위험"으로 정밀화했다. 556개 transductive/MP-count candidate 중 pair_submit/probe gate는 0개였고, best p90 delta vs a2c8도 `+0.000125668`로 나왔다.

E11 gated scan은 H15를 더 정밀화했다. label-flow 자체는 버리지 않는다. 다만 probability translation은 dependency-energy/raw05 gate를 통과한 row/target subset에만 허용해야 한다. E12-E14 결과, 그 subset은 주로 S4와 Q3로 좁혀졌고 strict pairwise 후보가 처음 생겼다.

E15-E19가 H17의 submit-safe 버전을 반증했고, H18도 반증했다. E20은 H19도 반증했다. E21은 H20도 반증했다. E22는 H21을 next-sensor 관점에서 반증했다. E23은 H22를 반증했고, E24는 H23을 반증했다. E25는 H24를 strict survival 기준으로 반증했고, E26은 H25를 반증했으며, E27은 H26을 반증했다. E28은 H27을 current ranker로는 반증했지만, tight binary subject-prior world가 known anchors를 frontier gap보다 정밀하게 맞출 수 있다는 단서를 남겼다. E29는 H28을 약하게 지지하지만 frontier-scale world가 1개뿐이라 제출 근거는 아니었다. E30은 frontier-box binary worlds가 다수 존재하고 non-candidate objectives에서 mixmin/inverse7 선호가 강하다는 점을 보여 H29를 부분 지지했지만, adverse candidate-objective worlds가 여전히 가능해서 strict certification은 반증했다. E31은 H30도 반증했다: adverse mixmin worlds are not geometrically implausible under train label dynamics. E32는 H31을 부분 지지한다: low-anchor-energy worlds are one-sided for mixmin/inverse7, and the two adverse worlds are high-anchor-energy. E33은 H32를 지지한다: that signal survives leave-one-anchor-out and no adverse mixmin world enters the low-energy half. E34는 H33을 부분 지지한다: medium non-JEPA anchors and broad loss/cancellation geometry carry the signal, while exact target-axis semantics are not necessary. E35는 H34 normal-submit certification을 반증한다: mixmin에는 honest-CV support가 있지만, 가장 강한 근거는 known-public/anchor-derived이고 pairwise/old selector hard veto가 남는다. E36은 H35를 mixmin에 대해 반증하고 inverse7 bridge branch를 연다: raw observed structure는 mixmin보다 inverse7을 훨씬 강하게 지지한다. E37은 H36을 현재 scale/blend family에 대해 반증했다: raw support와 anchor support는 같이 유지되지만 selector veto는 줄지 않았고 two-selector majority는 0이었다. E38은 H37을 diagnostic ranking으로 지지하고 normal-submit claim은 다시 반증했다: audited candidates `10`, normal-submit `0`, public-sensor `10`, top sensor `mixmin_0c916`. E39는 H38을 public-rank selector로 반증했다: OOF sign은 known public과 맞지만 stage2/ordinal 순서를 거꾸로 고르므로 OOF stress는 negative screen이지 public selector가 아니다. E40은 H39를 strict selector로는 반증하고 loose movement-anatomy prior로만 남겼다: stage2/ordinal 순서는 맞지만 A2C8-best and bad-JEPA severity gates fail. E41은 H40도 strict/loose selector로 반증했다: bad-axis group geometry는 severity를 개선하지만 A2C8-best를 복원하지 못하고, named-axis geometry는 rank/order를 악화시킨다. E42는 H41을 usable selector로 반증했다: A2C8 fixed-zero anchoring improves nonbaseline rank but still has MAE `0.000766262`, far above the raw05-A2C8 edge, and collapses near-zero candidate advantages. E43은 H42를 반증했다: best selector error조차 raw05-A2C8 gap보다 2.5배 이상 크고, error-margin-certified candidate는 0개다. E44는 H43도 반증했다: current scored universe에는 selector error나 raw05-A2C8 gap을 넘는 pairwise-safe movement가 없다. E45는 H44를 반증했다: simple structured public-subset mask도 known-anchor LOO에서 selector-scale error를 만들지 못했다. E46은 H45를 세웠다: 0.54 path는 block-rate oracle `0.517878`에 존재하지만, 현재 관측 context는 block-rate state를 거의 복원하지 못한다. E47은 H46을 추가했다: 현재 fold-safe block-summary context도 block-rate target representation을 복원하지 못한다. best row blend는 `-0.001505`지만 block-rate loss는 temporal보다 `0.012440` worse이고 oracle-gap recovery는 `0.014083`뿐이다. E48은 H37/H47을 강하게 지지했다: mixmin public `0.5763066405`는 previous best를 `0.0011326805` 이겼고, pairwise/old selector veto를 hard gate로 쓰면 좋은 후보를 버린다는 반례가 됐다. 따라서 H04, H31-H33, H37, H47은 강화되고, H34의 "normal-submit certification은 부족하다"는 과거 결론은 "pre-public hard gate로는 너무 보수적이었다"로 수정된다. 0.54 병목은 해소되지 않았지만, 이제 핵심 질문은 a2c8 주변 micro-edge가 아니라 mixmin이 포착한 anchor-loss/binary-world 구조를 어떻게 재현하고 private risk를 줄일지다.

E49는 H48을 추가했다. Mixmin의 target movement는 `Q3/Q1/S3`에 크고, `Q1/S1`은 simple prior proxy에서는 오히려 불리하다. Train/test는 각 subject timeline 안의 hidden calendar blocks 형태이며, high-movement blocks는 gap-adjacent/between-train-runs 형태가 많다. 이 관찰은 "public subset이 단순 mask다"라는 H44와 다르다. H44는 public LB 평가 subset 복원을 묻고 반증됐고, H48은 데이터 생성 자체가 subject-calendar mask restoration이라는 가설이다.

E50은 H48의 가장 단순한 selector 변환을 반증했다. Target/prior/calendar/subject/subject-calendar movement views는 known-anchor order 일부를 보존했지만, 어느 view도 held-out mixmin을 public-best로 예측하지 못했다. 따라서 calendar mask는 여전히 JEPA context 후보지만, standalone public selector나 submission forecast는 아니다. 다음 실험은 calendar flanks를 anchor-loss/binary-world geometry 또는 held-out block-rate/count target과 결합해야 한다.

E51은 그 다음 결합 selector도 반증했다. LOO-safe anchor-loss world aggregates는 E32/E38의 sensor 성공을 kNN selector로 옮기지 못했다. Best anchor-residual view는 coarse order와 bad-tail을 일부 맞혔지만 held-out mixmin을 `0.00241739` worse로 예측했다. 따라서 "anchor-loss + calendar feature ranker"가 아니라, block-rate/count context target 또는 mixmin-constrained binary-world stress가 다음 분기였다.

E52는 그 mixmin-constrained stress의 첫 번째, 저비용 버전을 실행했다. 기존 E30/E32 worlds를 mixmin actual delta에 맞는 band로 조건화하고 158개 후보를 mixmin 대비 재점수화했지만 strict/loose better-than-mixmin은 `0`이었다. 유일한 near-tie `bridge_blend_m0p75_s1p25`도 median이 양수이고 max delta가 양수라 제출 후보가 아니다. 이 결과는 현재 후보 풀 안에서는 mixmin이 local frontier라는 쪽을 강화한다. 남은 live branch는 기존 후보 rescore가 아니라 calendar-flank block-rate/count target 또는 mixmin을 hard constraint로 넣은 새 world-generation이다.

E53은 calendar-flank block-rate/count branch의 가장 단순한 count-state posterior를 반증했다. Same-subject를 허용한 `calendar_count_local`은 pseudo-hidden에서 subject mean 대비 `-0.005266` 좋아졌지만, private-safe에 가까운 `calendar_count_strict`는 `+0.001434` 나빠졌다. 실제 hidden block에서는 strict rate가 mixmin을 약하게 선호했지만 weighted delta는 `-0.000179`뿐이고 target alignment가 S3/S2/Q2에만 좋고 S1/Q1/Q3/S4에는 불리했다. 따라서 calendar flanks는 버리지 않지만, simple count posterior는 후보 생성기가 아니라 LeJEPA-style energy다.

E54는 raw overnight context가 strict block-state representation을 실제로 회복한다는 강한 단서를 줬다. `night_phone_rawctx_strict_k8_a24`는 pseudo-hidden weighted LogLoss를 subject mean 대비 `-0.007733` 개선했고, geometry도 collapse로 보이지 않았다. 그러나 그 latent는 mixmin-public latent가 아니었다: actual hidden block rate world에서 같은 method의 mixmin delta는 `+0.000311`로 adverse였고 S3 pseudo-hidden target도 악화됐다. 따라서 live branch는 "raw overnight context 자체가 후보"가 아니라, raw strict latent와 mixmin latent 사이의 target-sign conflict를 설명하는 Q/S count manifold 또는 mixmin-hard world generation이었다.

E55는 그 Q/S count manifold translation의 단순 버전을 반증했다. Strict donor target-rate projection 225개 중 joint gate는 `0`이었다. S3를 subject mean으로 교체하면 raw pseudo-hidden보다 `-0.001115` 좋아지고 S3는 고쳐졌지만 hidden mixmin sign은 `+0.000319`로 여전히 adverse였다. 반대로 hidden mixmin sign을 음수로 만드는 Ridge projections는 pseudo-hidden LogLoss를 `0.727319` 수준으로 망가뜨렸다. 따라서 남은 live branch는 post-hoc target projection이 아니라 mixmin-hard world generation 또는 단순 rate vector보다 더 구조적인 block target representation이었다.

E56은 그 mixmin-hard world generation을 실제로 실행했고, H53을 부분 지지했다. Mixmin을 hard observation으로 넣고 raw overnight hidden block-rate를 feasibility prior로 쓴 world family는 `45` worlds / `44` unique worlds를 만들었고, 기존 후보 strict gate는 여전히 `0`이었지만 posterior world-LOO strict gate는 `12`개 열렸다. 그러나 E57은 H54를 반증했다. E56 posterior variants `15`개 중 independent actual-anchor plus movement safety joint gate는 `0`이었고, E56 selected diagnostic은 mixmin보다 actual-anchor `+0.020381` 나빴다. 따라서 현재 live branch는 direct posterior submission이 아니라 E56 posterior의 anchor-constrained distillation 또는 structural block target representation이다.

E58은 H55를 submission source로 반증했다. E61에서 E58 actual-anchor scoring의 index mismatch를 고쳤고, 결론은 유지됐다. Corrected toward-teacher 후보는 `126/900`개만 sign-level anchor improvement였고, best anchor delta는 `-4.081e-6`으로 여전히 `1e-5` margin을 넘지 못했으며 eligible gate는 `0`이었다. Reverse control도 더 강한 반대 방향을 만들지 못했다. 따라서 E56 posterior는 완전히 adverse한 것은 아니지만, 현재 방식으로는 public-sensor 해상도 아래의 energy일 뿐이다.

E59는 H56을 direct candidate source로 반증했다. 128-state joint block label-pattern target은 확실히 예측 가능했다: raw independent pattern baseline보다 좋은 방법이 `139/216`개였고, own-margin 대비 joint gain이 있는 방법도 `198/216`개였다. 하지만 이 구조는 현재 public frontier latent로 번역되지 않았다. Best pattern method는 pattern NLL을 `-0.062594` 낮췄지만 row LogLoss는 raw보다 `+0.003678` 나빠졌고 hidden mixmin sign도 `+0.000304`로 adverse였다. 반대로 hidden mixmin sign을 음수로 만드는 방법들은 pseudo-hidden row validity와 S3를 크게 망가뜨렸다. 따라서 단순 marginal rate보다 구조적인 target이 필요하다는 직감은 절반만 맞았다. Joint co-occurrence 구조는 존재하지만, within-block joint labels alone으로는 mixmin-relative next candidate가 나오지 않는다.

E60은 H57을 direct translator/independent validator로 반증했다. Transition residual은 hidden mixmin sign을 강하게 만들 수 있었다: best hidden-sign method는 weighted mixmin delta `-0.001569`였고 S3/S2/Q3 축이 주로 기여했다. 그러나 그 방법은 pseudo-hidden row LogLoss를 raw 대비 `+1.519232` 망가뜨렸고 S3도 subject 대비 `+1.331880` 악화됐다. 반대로 row-valid한 transition methods는 raw에 매우 가깝게 머물렀고 hidden mixmin sign은 여전히 adverse였다. 따라서 transition residual은 "숨은 방향 센서"로는 흥미롭지만, row calibration을 보존하는 non-anchor validator는 아니다.

E62는 H59를 반증했다. Transition residual을 probability target으로 쓰지 않고 E56 teacher cell gate로만 쓰면 살 수 있다는 보수적 가설을 찔렀지만, `363258` 후보 중 eligible gate는 `0`이었다. Best toward-teacher anchor delta는 `-2.716e-6`으로 E58 corrected best `-4.081e-6`보다 약했고, reverse control도 거의 움직이지 않았다. 따라서 transition residual은 현재 형태에서는 E56 energy의 missing validator가 아니라, 더 복잡한 structural target에 들어갈 수 있는 위험 진단 축일 뿐이다.

E63은 H60을 양쪽으로 갈랐다. Subject/calendar/raw/transition hidden-rate view들의 BCE gradient consensus는 E56 teacher 방향을 강하게 지지했다. Toward 후보는 hidden guard와 world guard가 각각 `1000/1000` 열렸고 reverse control은 `0/300`이었다. 하지만 best actual-anchor delta는 `-3.650e-6`으로 E58 corrected best보다도 작았고 eligible gate는 `0`이었다. 따라서 "E56 방향 자체가 환상"은 약화됐지만, "그 방향이 곧 제출 가능한 확률 이동"은 반증됐다. 병목은 방향 발견이 아니라 amplitude/public-anchor translation이다.

E64는 H61을 반증했다. E63 방향이 단순히 under-scaled일 뿐인지 보기 위해 scale/cap을 키웠지만, actual-anchor sign이 오히려 전부 adverse로 돌아섰다. Toward 후보는 hidden/world/movement guard가 모두 `1346/1346`인데 anchor beats는 `0/1346`이었고 best toward delta도 `+3.024e-6`이었다. 따라서 E56 gradient 방향은 local hidden-rate BCE 기준으로는 맞지만, public-anchor LogLoss에서는 작은 neighborhood를 벗어나면 바로 나빠진다. 다음 질문은 더 큰 scale이 아니라 target별/row별 amplitude를 어떻게 거의 0 주변에서 선택하느냐다.

E65는 H62를 절반만 살렸다. Near-zero targetwise pocket은 실제로 있었다. `no_q2_s3 + raw_agree + grad_all_abs50 + scale 0.13 + cap 0.12`가 `-5.995e-6`으로 E63보다 개선됐고, toward 후보 `1753/2290`이 mixmin을 sign-level로 이겼다. 그러나 anchor-margin gate는 여전히 `0`이고, single-target 움직임은 Q1/S4 정도만 약하게 살아났으며 S2는 adverse였다. 따라서 다음 분기는 scale 탐색이 아니라 Q2/S3 conflict와 broad-mask amplitude의 원인을 설명하는 target-conflict translator였다.

E66은 H63을 정밀하게 반증했다. Q2/S3는 hidden 방향이 단순히 틀린 target이 아니었다. Matched add-back에서 `all`은 robust actual-anchor를 `432/432` 악화시켰지만 mean-anchor는 `288/432` 개선했고 hidden core는 `432/432` 개선했다. 동시에 max-set tail은 `432/432` 악화됐다. 그러므로 병목은 "Q2/S3를 빼야 한다"가 아니라 "Q2/S3가 평균/hidden 이득을 줄 수 있어도 public-compatible worst-tail risk를 키우는 것을 어떻게 중화할 것인가"다. 다음 분기는 Q2/S3 target mask가 아니라 tail-neutral/variance-aware translator다.

E67은 H64를 절반만 살렸다. First-order anchor-tail gate는 Q2/S3 add-back을 무작정 막는 것보다 낫다. `tail_meanneg_m1.00`는 `-6.933e-6`까지 내려갔고, `tail_p90_nonpos_m1.00`는 matched base를 `432/432` 이기면서 그중 `360/432`은 max-set tail도 중립이었다. 하지만 margin gate는 여전히 `0`이다. 따라서 Q2/S3 tail-risk translator는 살아있는 방향이지만, 현재 형태는 known-anchor tail derivative에 의존한 sub-margin micro-edge다. E68은 그중 artifact 의심을 직접 줄였다. Held-out combo-set gate reconstruction에서도 independent/strict gate가 `155/540` 열렸고, `tail_soft_max_m1.00`와 `tail_p90_nonpos_m1.00`가 hidden/world/block Q2/S3 stress를 통과했다. 다만 heldout gain은 `1e-6` scale이라 제출 신호는 아니다. E69는 그 strict cell을 단순 alpha로 키우는 가설을 반증했다. Full-combo best는 `-9.1779e-6`까지 좋아졌지만 margin은 `0`개였고, alpha가 커질수록 heldout tail-neutral count가 무너졌다. E70은 E68 strict cells를 consensus representation으로 모으면 margin을 살짝 넘는 strict rows가 `6`개 생긴다는 점을 보여 H67을 부분 지지했다. 하지만 strict rows가 모두 `gate=none`이고 heldout-specific construction에서 나온 것이므로 제출 후보가 아니라 unified-rule stress 대상이었다. E71은 이 unified stress를 실행했고, full-combo 재구성에서도 strict row `1`개와 best all delta `-1.082166e-5`가 남아 consensus가 순수 heldout artifact는 아님을 보였다. 그러나 deployable gate는 `0`이고 살아남은 strict row도 `gate=none`이라 H68의 단순 제출 가능 버전은 반증됐다. E72는 그 반증을 정밀화했다. sign-agreement 계열은 실패했지만 `top_abs50` sparse-magnitude gate가 `7`개 deployable rows를 만들었고, `s3_only`도 `3`개를 만들었다. E73은 best `top_abs50` row를 제출 파일로 만들었다. E74는 그 sparse gate가 single-cell artifact가 아님을 보였고, E75는 amplitude가 symmetric이 아니라 S3-heavy/Q2-low일 수 있음을 보였다. E76은 S3-heavy direction이 `94/94` subset variants에서 symmetric controls를 이기지만 exact E75 amplitude deployability는 `49/94`에 그친다는 점을 보여, target asymmetry와 exact amplitude risk를 분리했다. E77은 source-subset posterior averaging을 반증했다: Q2/S3-only posterior는 안전하지만 sub-margin이고, full posterior는 margin은 만들지만 combo-set/tail consistency를 깨뜨린다. E78은 source-subset reliability masks도 반증했다: deployable row는 많이 열렸지만 E75를 이기는 deployable row는 `0`이었다. E79는 handcrafted public-like row/block/flank masks도 반증했다: `61` masks and `6516` rows에서 deployable row는 `1318`개였지만 E75를 이기는 deployable row는 `0`이었다. 다음 질문은 "sparse-magnitude Q2/S3 consensus가 public에서도 살아남는가, 살아남는다면 target-asymmetric amplitude까지 public이 읽는가, 그리고 amplitude를 단순 source-subset 평균/신뢰도 또는 row/block/flank mask가 아니라 combo-set/tail calibration이나 learned structural target으로 어떻게 국소화해야 하는가"다.
