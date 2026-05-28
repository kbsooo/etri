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

- 상태: 강한 관찰 증거 있음; calendar-only selector utility는 E50에서 반증됨.
- 왜 그럴듯한가: E49 shows train/test is not a future split. Test rows are hidden calendar holes inside each subject timeline, often adjacent to or between train runs. This matches I-JEPA's context-target framing better than independent tabular rows: context is labeled calendar flanks, target is the hidden block's label-rate/count vector.
- 맞다면: mixmin movement should concentrate by subject/date block and target, simple train/subject/recent priors should not uniformly explain the gain, and a selector using calendar-mask movement features should explain mixmin as a new public anchor without breaking raw05/stage2/ordinal/bad-JEPA order.
- 틀리다면: calendar block topology will add little beyond target-level movement, simple priors will explain most of mixmin's public edge, or selector recalibration with calendar features will still fail mixmin and known-anchor order.
- 최소 실험: use `analysis_outputs/post_mixmin_observation_audit.py` outputs to build mixmin-relative calendar-block features: inside-train-calendar vs after-train-end, gap-adjacent vs between-train-runs, run length, subject, target movement, raw05 distance, and prior CE stress. Re-run known-anchor selector LOO/L2O with mixmin included.
- 관측: E49 found largest target movements `Q3 = 0.011540`, `Q1 = 0.010345`, `S3 = 0.009688`; `Q1` and `S1` are worse under all simple prior proxies; movement is subject-concentrated (`id05/id09/id08/id03/id01` top); top high-movement calendar masks are `gap_adjacent` or `between_train_runs`. E50 then tested this as a selector with mixmin included as a known anchor. The best `subject_calendar` view had MAE `0.000884106`, rank accuracy `0.833333`, and Spearman `0.833333`, but predicted held-out mixmin delta `0.00135162` instead of `0`; strict and loose selector views were both `0`.
- 성공/폐기 기준: the standalone selector version is weakened/falsified because calendar features do not explain mixmin as best. The broader context-target version remains alive only if calendar flanks help predict held-out block-rate/count representations or combine with anchor-loss/binary-world energy to lower mixmin-relative risk.
- public LB 기대 반응: a future public-improving candidate should not be a global prior tweak or a direct calendar-position tweak. It should preserve mixmin's anchor-loss direction while changing probabilities mostly on specific subject-calendar hidden blocks whose block-rate state is independently inferred.
- 제출 전략: no immediate submission. Do not use E50 predicted candidate scores as forecasts. Build a mixmin-relative candidate only after calendar context is coupled to anchor-loss/binary-world geometry or a stronger block-rate target stress.

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
