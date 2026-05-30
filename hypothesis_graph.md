# Hypothesis Graph

작성일: 2026-05-29

이 문서는 수면 기반 생활습관 로그 예측 대회를 "예측 표"가 아니라 숨은 데이터 생성 과정의 관측 로그로 다루기 위한 가설 그래프다. 현재 best public LB는 `submission_e95_hardtail_541e3973.csv`의 `0.5762913298`이다.

## 현재 병목 요약

E48에서 `submission_mixmin_0c916bb4.csv`가 public `0.5763066405`를 기록해 previous best `a2c8`를 `0.0011326805` 낮췄고, E97에서 `submission_e95_hardtail_541e3973.csv`가 public `0.5762913298`로 mixmin을 `0.0000153107` 더 낮췄다. Mixmin의 큰 점프는 anchor-loss/binary-world movement가 public-relevant였다는 증거이고, E95의 작은 추가 개선은 E72-adverse hard-label tail localization이 public-real이라는 증거다. 따라서 현재 병목은 "a2c8 근처 micro edge를 더 찾는 문제"가 아니라, mixmin/E95가 맞힌 hidden public world와 아직 못 맞힌 block-rate/calibration structure를 분리하는 문제다.

가장 강한 현재 설명:

- hidden subject/session/block 구조는 존재한다.
- row-level boundary copy는 실패했다.
- block-level rate/count latent는 의미가 있지만 직접 제출 후보로는 약하다.
- raw05는 public-positive raw timeline 방향을 포착했다.
- JEPA latent에는 local signal이 있지만 큰 이동은 public bad-axis를 강하게 탄다.
- `a2c8`는 raw05 manifold의 작은 correction이었지만, 이제 frontier가 아니다.
- Mixmin은 anchor-loss/cancellation geometry와 binary actual-anchor worldview가 public-relevant였다는 첫 강한 관측이다.
- E95는 E72-adverse hard-label tail localization이 public-positive라는 첫 강한 관측이다.
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

- 상태: 증거 있음 as diagnostic; rejected as public-safe selector.
- 왜 그럴듯한가: S2-S4 corr `0.478`, S2-S3 `0.394`, Q1-S1 `0.361`, Q2-Q3 `0.340` 등 target dependency가 존재한다.
- 맞다면: target dependency violation energy가 bad candidates를 구분해야 한다.
- 틀리다면: dependency correction이 anchor stress에서 일관 악화한다.
- 최소 실험: target dependency violation energy, targetwise temperature/intercept stress.
- 최근 증거: E93 fitted seven train-label conditional target models and empirical pattern/correlation energies. It did not reject the known public-negative E72 file. E72 improved target-manifold delta versus mixmin by `-0.001468687`, and live candidates were also all favorable, led by E86 `-0.000921783`. Known bad anchors such as `final9` and `bad_q2_jepa` looked even more target-manifold-consistent despite worse public LB, and public-LB sanity correlation was weak.
- 제출 전략: hard constraints 금지. Target dependency is useful as a consistency/diagnostic energy, but not as a submission ranker or E72 counter-gate.

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

### H82. E86 public risk decomposes into Q2 add-back, overstep, and inverse-top geometry

- 상태: contrast sensors built; public pending.
- 왜 그럴듯한가: E86 improved local all-combo margin versus E85 but changed more than one axis at once. It adds Q2 back, uses shrink `1.25`, and ranks by all-delta rather than inverse-top-prior. A single public score for E86 would otherwise be underidentified.
- 맞다면: no-Q2, no-overstep, and inverse-top-prior variants should all remain strict/deployable locally while creating different public interpretations if E86 fails.
- 틀리다면: one of the contrast variants should fail the same E86 stress, or all variants should collapse to nearly identical target movement and provide no diagnostic separation.
- 최소 실험: `analysis_outputs/e87_e86_risk_decomposition.py`, rebuilding the E86 consensus pool and selecting three public contrast files under the same combo, hidden/world/block, raw-energy, and tail stress.
- 관측: E87 rebuilt `1485` consensus rows and kept a strict/deployable universe of `700`. It wrote three contrasts: `analysis_outputs/submission_e87_noq2_source_consensus_a85c4e39.csv` (`S1,S2,S3`, shrink `1.25`, all delta `-2.69461e-5`), `analysis_outputs/submission_e87_q2_nooverstep_consensus_acd7add0.csv` (`Q2,S1,S2,S3`, shrink `1.00`, all delta `-2.42545e-5`), and `analysis_outputs/submission_e87_inverse_top_prior_consensus_5445ec28.csv` (`Q2,S1,S3`, shrink `1.25`, inverse-top delta `-2.06434e-5`).
- 성공/폐기 기준: success is not beating E86 locally; success is reducing interpretation entropy after public feedback. If E86 improves, H81 is strengthened and E87 remains diagnostic. If E86 worsens but one contrast improves, the corresponding risk axis becomes the next law. If all fail, demote the E85/E86 target-prune family and reopen row/block or all-sign/raw05-compatible target-axis recovery.
- public LB 기대 반응: no-Q2 improvement means Q2 add-back was contaminating; no-overstep improvement means shrink `1.25` overstepped calibration; inverse-top-prior improvement means public is closer to inverse-top geometry than all-delta geometry.
- 제출 전략: do not submit E87 before E86 unless the goal changes from highest-upside candidate to diagnostic contrast. After E86 public feedback, choose the single E87 file whose interpretation best separates the surviving hypothesis.

### H83. E86/E87 are second-order mixmin rollbacks with measurable E72-contamination risk

- 상태: supported as attribution/risk lens; public pending.
- 왜 그럴듯한가: E72 was a public-negative combined sparse-gate file. E85/E86/E87 are all mixmin-relative movements generated after the E72 miss, so their public risk should be judged by whether they avoid or reuse E72's failed row/cell manifold.
- 맞다면: E86/E87 movement should have negative signed correlation with mixmin-vs-a2c8 if they are rollbacks, and public-riskier variants should have higher row/cell overlap with E72-vs-mixmin.
- 틀리다면: E86/E87 should align positively with mixmin's original public-positive move, or E72 proximity should be low and indistinguishable across variants.
- 최소 실험: `analysis_outputs/e88_frontier_movement_attribution.py`, comparing mixmin, E72, E85, E86, and E87 logit movements across target cells, rows, subject/calendar/raw-domain context, and prior CE proxies.
- 관측: E86 has high-E72 cell mass `0.443457`, E72 overlap ratio `0.819288`, contamination index `0.772379`, row correlation with E72 failed movement `0.725471`, and signed cell correlation with mixmin-vs-a2c8 `-0.758417`. no-Q2 has lower contamination index `0.730408`; no-overstep keeps the same geometry as E86; inverse-top-prior is worst by contamination index `0.928415`.
- 성공/폐기 기준: success is not a new submission. Success is a sharper public-feedback decision tree. If E86 improves, H81 survives despite E72 proximity. If E86 fails and no-Q2 improves, Q2 add-back is the likely contaminant. If no-overstep improves, amplitude is the likely contaminant. If inverse-top-prior improves despite high E72 proximity, public-world identity is stranger than the E72 attribution lens predicts.
- public LB 기대 반응: E86 public result now carries downside evidence as well as upside evidence. A worse E86 score should not immediately kill target-prune; it should first route to no-Q2.
- 제출 전략: keep E86 as highest-upside information sensor if a single pre-feedback file must be chosen. Do not promote inverse-top-prior as a safety fallback; use it only as a diagnostic if the question is public-world geometry.

### H84. E72-contamination can be reduced by cell-level fallback to E85 without killing strict stress

- 상태: supported locally; public pending.
- 왜 그럴듯한가: E88 shows E86's extra local margin and E72 proximity are entangled, but E85 is a lower-amplitude target-pruned law from the same family. If E72 proximity is localized to a subset of cells, replacing only those cells with E85 movement may preserve the structural law while reducing the known public-negative manifold.
- 맞다면: a controlled E86-to-E85 fallback on high-E72 cells should keep combo, hidden/world/block, raw-energy, and tail stress while lowering E72 contamination below E86, no-Q2, and E85 controls.
- 틀리다면: all decontamination variants should either collapse margin below strict/deployable, worsen inverse-top/world/block stress, or reduce contamination only by shrinking movement to near-mixmin.
- 최소 실험: `analysis_outputs/e89_e86_e72_decontamination_scan.py`, sweeping E86/no-Q2 blends, high-E72 row/cell fallback, Q2-row removal, and projection-away from E72 failed delta.
- 관측: E89 generated `52` rows, evaluated all `52`, and found strict/deployable `37`. The selected `analysis_outputs/submission_e89_e72decontam_00d7807f.csv` starts from E86 and falls back to E85 on cells in the top `20%` of E72 failed absolute movement. It has all delta `-2.58960e-5`, inverse-top `-5.55392e-6`, raw05-compatible `-3.33148e-5`, all-sign `-3.88191e-5`, hidden Q2/S3 `-0.000216060`, world `-0.000140452`, block win `0.638889`, block-tail safe `0.944444`, and E72 contamination index `0.676361`.
- 성공/폐기 기준: H84 succeeds as a local risk-adjusted repair because contamination drops below E86 `0.772379`, no-Q2 `0.730408`, and E85 `0.734771` while strict/deployable remains true. It is not yet proven as a better public submission because it sacrifices E86's stronger hidden/world/block edge.
- public LB 기대 반응: if E89 improves public more than E86, public is punishing E72-contaminated cells more than it rewards E86's extra margin. If E86 improves more, public rewards source-consensus amplitude despite E72 proximity. If both fail, target-pruned rollback itself is likely a local combo-world artifact.
- 제출 전략: E86 remains highest-upside. E89 becomes the risk-adjusted fallback above no-Q2 and inverse-top-prior when the goal is lower downside after the E72 public miss.

### H85. E72 decontamination has a row-coherent Pareto knee, not only a minimum-contamination solution

- 상태: supported locally; public pending.
- 왜 그럴듯한가: E89's minimum-contamination cell fallback lowers E72 proximity most, but it also sacrifices hidden/world/block strength. If the hidden DGP is row/block-state-like, row-coherent fallback may be more public-readable than isolated cell fallback.
- 맞다면: a row-level E72 fallback should remain cleaner than E85/no-Q2 while preserving more E86 margin, hidden/world support, and block-tail safety than the minimum-contamination E89 file.
- 틀리다면: every cleaner-than-E85/no-Q2 row should either collapse hidden/world/block support or be dominated by the E89 min-contamination cell fallback.
- 최소 실험: `analysis_outputs/e90_e89_pareto_knee.py`, scoring strict E89 rows by decontamination, margin retention, hidden/world retention, block/tail safety, and row-coherence while penalizing projection-away repairs.
- 관측: E90 found `13` eligible strict rows and selected `analysis_outputs/submission_e90_e72pareto_28925de5.csv`: E86 with E85 fallback on top `10%` E72-contaminated rows. It has all delta `-2.69324e-5`, contamination `0.715784`, world `-0.000250999`, hidden Q2/S3 `-0.000299838`, block win `0.777778`, block-tail safe `1.0`, margin retention `0.798048`, world retention `0.681272`, and hidden retention `0.518671`.
- 성공/폐기 기준: supported if E90's public result beats E89 or E86, because public then rewards row-coherent structural retention after partial E72 removal. Weakened if E89 beats E90, meaning E72 cell contamination dominates. Rejected if E86 beats both, meaning E72 proximity was over-penalized.
- public LB 기대 반응: E90 should land between the high-upside E86 and low-contamination E89 if the tradeoff is real. A large deviation from that order is highly informative about whether public values contamination removal or structural retention.
- 제출 전략: use E90 when one slot should balance E86 upside and E72 downside. Keep E86 as the maximum-upside sensor and E89 as the minimum-contamination sensor.

### H86. E72-updated movement-fingerprint proxy can rank post-mixmin candidates

- 상태: rejected as selector; retained only as diagnostic.
- 왜 그럴듯한가: E72 is the first public-negative anchor after mixmin and is close to mixmin in movement geometry. If any cheap known-LB proxy could rank E86/E90/E89, adding E72 should improve frontier-scale resolution.
- 맞다면: the best LOOCV proxy should hold out mixmin near the true frontier, predict E72 worse than mixmin with the correct sign, and have error below the E72 public miss scale or at least below the E86/E90/E89 expected edge scale.
- 틀리다면: the proxy should mispredict mixmin or E72 by more than the entire E72 public miss, or rank post-mixmin candidates while failing the known frontier itself.
- 최소 실험: `analysis_outputs/e91_e72_updated_selector_collapse_audit.py`, reusing public-anchor movement features with 10 known public anchors and scoring only E85/E86/E87/E89/E90.
- 관측: best fixed proxy `raw05_a2c8_compat` has MAE `0.000543412` and p90 error `0.001010234`. It holds out mixmin at `0.5774493627` despite actual `0.5763066405`, error `+0.001142722`. It predicts E72-minus-mixmin `-0.0000460726` while actual is `+0.0001011367`.
- 성공/폐기 기준: rejected because proxy p90 error is `9.99x` the E72 public miss and the mixmin holdout error is `11.30x` the E72 miss. A selector that cannot rank the known frontier against E72 cannot choose E86/E90/E89.
- public LB 기대 반응: no submission. Future E86/E90/E89 public scores should be interpreted as sensors, not as validation of this proxy.
- 제출 전략: do not materialize an E91 proxy-ranked file. Choose E86, E90, or E89 by the hypothesis being tested: maximum source-consensus upside, row-coherent decontamination, or minimum contamination.

### H87. Hidden-block posterior alignment can select among E86/E90/E89

- 상태: rejected as public-safe selector; retained as representation diagnostic.
- 왜 그럴듯한가: the hidden-block posterior is the closest current JEPA-style target representation: context is subject-calendar/raw/block state, target is hidden block rate. If E90's row-coherent repair is genuinely more DGP-aligned than E89, this representation should prefer E90 without also preferring known-bad E72.
- 맞다면: E90 should improve posterior CE versus mixmin, reduce E72 failed-direction agreement versus E86, and not be dominated by the known public-negative E72 file.
- 틀리다면: the hidden-block posterior should rank E72 first, or reward candidates mainly by the same movement that failed public rather than by public-safe block coherence.
- 최소 실험: `analysis_outputs/e92_hidden_block_posterior_alignment_audit.py`, comparing mixmin-relative E72/E85/E86/no-Q2/E90/E89 movement against `hidden_block_posterior_block_summary.csv` posterior rates, endpoint rates, block-target R2, high-posterior-shift block concentration, and E72 failed-direction mass agreement.
- 관측: `failed_e72` is the hidden-block alignment leader and best posterior CE candidate (`posterior_ce_delta_all_vs_mixmin = -0.000287300`) despite being public-negative. Among unobserved post-mixmin candidates, no-Q2 and E86 have the strongest posterior CE (`-0.000257196`, `-0.000255621`), E90 is close (`-0.000250767`), and E89 has the highest block-target R2 (`0.356204`) plus lowest E72 direction mass among E86/E90/E89 (`0.635838`).
- 성공/폐기 기준: rejected as selector because a representation score that ranks known-bad E72 first is E72-tainted. The useful evidence is diagnostic separation: posterior CE favors no-Q2/E86, decontamination favors E89, and E90 remains an intermediate structural-retention compromise rather than an independently certified best.
- public LB 기대 반응: no submission. If E86 later improves, posterior alignment was useful despite E72 contamination. If E89 improves, E72 contamination dominates posterior CE. If E90 improves, row-coherent compromise is public-real even without being the posterior leader.
- 제출 전략: do not materialize an E92-ranked file. Keep E86/E90/E89 as hypothesis sensors; do not use hidden-block posterior CE alone as a public-safe ranking target.

### H88. Train target-manifold energy can counter-filter E72-tainted block alignment

- 상태: rejected as public-safe selector; retained as diagnostic.
- 왜 그럴듯한가: E92 showed hidden-block posterior CE rewards E72. A natural counter-hypothesis is that E72 is block-coherent but violates the Q/S target dependency manifold, so train target co-occurrence could act as a LeJEPA-style geometry health check.
- 맞다면: E72 should worsen conditional target self-consistency, empirical label-pattern NLL, or pair-correlation gap versus mixmin, while E86/E90/E89 should remain neutral or improve.
- 틀리다면: E72 should also look target-manifold-consistent, or known public-bad anchors should score well under the same energy.
- 최소 실험: `analysis_outputs/e93_target_manifold_counterenergy_audit.py`, fitting `target_j ~ other targets` logistic conditionals on train labels and scoring submissions by conditional logit residual, empirical pattern mixture NLL, nearest pattern NLL, and pair-correlation gap.
- 관측: E72 target-manifold delta mean was `-0.001468687` versus mixmin, so the counter-energy likes the failed public file. Live candidates were also favorable but smaller: E86 `-0.000921783`, no-Q2 `-0.000914184`, E90 `-0.000877945`, E89 `-0.000806467`, E85 `-0.000742113`. Worse public anchors also received favorable scores (`final9` `-0.020801364`, `bad_q2_jepa` `-0.002958703`), so this energy is not public-safe.
- 성공/폐기 기준: rejected as selector because it fails the known E72 counterexample and does not align monotonically with public LB among known anchors.
- public LB 기대 반응: no submission. If E86/E90/E89 public feedback later improves, target-manifold consistency may be a necessary but weak health signal. If they fail, E93 already warned that target consistency alone cannot protect against public mismatch.
- 제출 전략: do not rank by `target_manifold_delta_mean`. Keep dependency/manifold features as diagnostics only, especially for detecting gross bad-axis failures, not for selecting the next public file.

### H89. Soft representation health hides hard-label LogLoss tail risk

- 상태: supported as bottleneck explanation; not a standalone public selector.
- 왜 그럴듯한가: E92 and E93 both liked E72 even though E72 worsened public LB. LogLoss is evaluated on hard binary labels, so a movement can improve soft posterior/manifold consistency while creating a large positive-loss tail if the public labels fall on the opposite side.
- 맞다면: the hard-label direction that makes E72 wrong should expose substantial loss tail, and live candidates should trade off soft-health gain against this E72-adverse tail. Known public-bad anchors should have higher hard-tail exposure than mixmin.
- 틀리다면: E72's public miss should require nearly full adverse-label realization, or hard-tail exposure should not separate known public-bad anchors.
- 최소 실험: `analysis_outputs/e94_soft_health_hard_tail_audit.py`, computing candidate-minus-mixmin LogLoss deltas for hard labels `0/1`, defining the E72-adverse label per cell, and scoring E86/E90/E89/E85 plus known anchors by hard-tail exposure.
- 관측: E72 moved `893/1750` cells. Full E72-adverse exposure is `0.002330945`, while the observed public miss is only `0.0001011367`, or `4.3389%` of full exposure. Known public sanity is much stronger for hard-tail metrics than soft health: Spearman public LB is `0.793939` for E72-adverse exposure, `0.866667` for KL-if-mixmin-calibrated and hard worst-tail mean, but only `0.081935` for soft-health gain. Among E86/E90/E89, E89 has lowest E72-adverse exposure (`0.000799109`), E90 is middle (`0.000934031`), and E86 is highest (`0.001010242`), while E86 has the largest soft-health gain.
- 성공/폐기 기준: supported as a bottleneck explanation because it explains how E72 can pass soft JEPA-like health checks but fail public with a small hard-label tail realization. It is not a complete selector because E85 has even lower tail than E89 while less upside, and public subset identity is still unknown.
- public LB 기대 반응: if E89 beats E90/E86, hard-tail downside dominates. If E86 beats E89/E90, soft structural gain dominates despite tail exposure. If E85 beats all, public prefers the conservative floor over consensus/decontamination variants.
- 제출 전략: do not create an E94-ranked submission. Use E94 to clarify the tradeoff: E86 is max-upside soft-health, E90 is balanced row-coherent decontamination, E89 is lower-downside among the main three, and E85 is the conservative floor.

### H90. E72-adverse hard-tail exposure can be localized into a new post-E86 gate

- 상태: supported by public observation.
- 왜 그럴듯한가: E94 showed hard-tail exposure explains the E72 miss better than soft representation health. If that exposure is not just a scalar risk score, the risky cells should support a localized fallback that improves downside without fully reverting E86.
- 맞다면: an E86-derived fallback candidate should remain strict/deployable, reduce E72-adverse hard-tail exposure below E89 or E90, and keep local all-combo margin below the candidate it claims to dominate. It should not be equivalent to mixmin or a broad near-zero rollback.
- 틀리다면: every low-tail candidate should fail strict hidden/world/block stress, collapse to mixmin/E85, or only reproduce the already-known E89/E90 Pareto points.
- 최소 실험: `analysis_outputs/e95_hard_tail_gate_scan.py`, sweeping E86/E90 hard-tail row/cell fallback to E89/E85/mixmin plus scalar blends, with positive-tail masks, duplicate prediction deduping, and strict/non-strict tail separation.
- 관측: E95 generated `178` rows, evaluated `178`, found `112` strict rows and `19` strict non-dominated rows. Raw best non-control tail was `0.000146152` but failed strict stress, confirming that tail minimization alone is a rollback trap. The selected strict file `analysis_outputs/submission_e95_hardtail_541e3973.csv` starts from E86 and falls back to E85 on E72-adverse top-tail cells. It has all delta `-0.0000262074`, E72-adverse exposure `0.000788914`, world `-0.000132931`, hidden Q2/S3 `-0.000251140`, block win `0.750000`, and block-tail safe `0.972222`. Public E95 scored `0.5762913298`, improving over mixmin by `0.0000153107` and over failed E72 by `0.0001164474`.
- 성공/폐기 기준: supported because E95 beats E89 on both hard-tail exposure (`0.000788914 < 0.000799109`) and local margin (`-2.62074e-5 < -2.58960e-5`) while keeping non-trivial movement (`550` moved cells, active targets `Q2,S1,S2,S3`), then converts that local evidence into a public gain. Not a universal best because the public gain is only `58.42%` of the local margin, E86 keeps stronger upside, E90 keeps more row-coherent structural retention, and E85 has a slightly lower E96 p95 tail floor.
- public LB 관측 반응: E95 improved over mixmin, so public is sensitive to E72-adverse hard-tail localization. If E90/E86 later beats E95, structural/source-consensus upside dominates residual tail risk. If E85 beats E95, public rewards conservative tail floor more than retained E86 structure.
- 제출 전략: keep `analysis_outputs/submission_e95_hardtail_541e3973.csv` as the current frontier anchor. Next public candidates should be E95-relative and explicitly test more retained structure (`E90`/`E86`) or a more conservative floor (`E85`).

### H91. E72 public miss budget stress can distinguish hard-tail gate robustness from tail-floor conservatism

- 상태: supported as conditional stress; not a new submission source.
- 왜 그럴듯한가: E95 was selected using E72-adverse hard-tail exposure, but the public observation gives only a total miss (`+0.0001011367`), not which cells realized the adverse labels. A robust hard-tail candidate should survive many allocations of that miss budget, not only the exact cells emphasized by E95.
- 맞다면: when E72's observed miss is allocated over plausible E72-adverse hard-label cells, E95 should beat E89/E90/E86 across most complete-budget scenarios and should not rely solely on the E95 fallback mask.
- 틀리다면: E95 should only win in its own fallback cells, lose broadly to E89 or E85 in all/diffuse scenarios, or become worse than E90/E86 when the realized tail is row-coherent rather than cell-local.
- 최소 실험: `analysis_outputs/e96_public_miss_budget_tail_scenarios.py`, fixing the E72-minus-mixmin public miss as a LogLoss budget and generating deterministic/random allocations over target masks, E72 hard-tail masks, E95 fallback cells, and candidate movement masks.
- 관측: E96 generated `3894/3894` complete-budget scenarios over `1750` test-target cells. Failed E72 reconstructs `0.0001011367` in every scenario and mixmin is exactly `0`. Live mean conditional deltas were E95 `0.000057874`, E85 `0.000058977`, E89 `0.000059964`, E90 `0.000069295`, no-Q2 `0.000071237`, and E86 `0.000076162`. Live p95 deltas were E85 `0.000115304`, E95 `0.000115644`, E89 `0.000117735`, E90 `0.000129152`, E86 `0.000138751`, and no-Q2 `0.000138876`. E95 won `0.527478` of live scenarios, beat E89 `0.712378`, E90 `0.999486`, and E86 `0.998973`.
- 성공/폐기 기준: H91 supports E95 as the best mean/win-rate hard-tail sensor and strengthens it over E89/E90/E86. It rejects the stronger claim that E95 is the most conservative tail-floor candidate under every plausible realization: E85 has a slightly lower p95, and E95 loses most to E89 in diffuse low-amplitude Q2/Q2S3-bottom worlds.
- public LB 관측 반응: E95 did improve, so H91's ranking was directionally useful despite being a conditional hard-tail stress rather than a public-label fit. The realized public world was not so adverse to E95's retained E86 structure that the hard-tail budget dominated the whole score.
- 제출 전략: use E95 as the current frontier. Use E90/E86 to test retained-structure upside; use E85 only when the next public question is pure downside floor rather than hard-tail localization with retained E86 structure.

### H92. E95 as a known public anchor makes movement-fingerprint proxy usable for next ranking

- 상태: rejected.
- 왜 그럴듯한가: E95 is the first public-positive post-mixmin hard-tail move. Adding it to mixmin and failed E72 gives the known-LB table a local bracket around the current frontier, so a movement proxy might become sharp enough to rank E90/E86/E85.
- 맞다면: LOOCV movement regression should hold out E95/mixmin/E72 with errors below the E95 edge scale, preserve the E72-minus-mixmin sign, and produce future candidate spreads larger than its near-frontier error.
- 틀리다면: the best proxy should still have p90 error larger than E95's gain, fail one of the critical near-frontier holdout signs, or assign candidate scores that are not interpretable at frontier scale.
- 최소 실험: `analysis_outputs/e98_e95_updated_selector_audit.py`, adding E95 to `public_probe_observations.csv`, rerunning fixed LOOCV ridge proxy families, auditing E95/mixmin/E72 pair deltas, and scoring E90/E86/E85/E89/E87 candidates.
- 관측: known anchors increased to `11`. Best fixed proxy remained `raw05_a2c8_compat` with MAE `0.000520095` and p90 abs error `0.000816497`. This p90 error is `53.33x` the E95 edge over mixmin (`0.0000153107`) and `8.07x` the E72 miss over mixmin (`0.0001011367`). Mixmin-minus-E95 sign was correct but abs error was `0.0000619237`; E72-minus-mixmin sign was wrong, predicted `-0.0000305135` vs actual `+0.0001011367`; E72-minus-E95 sign was correct but abs error was `0.0000697264`.
- 성공/폐기 기준: rejected because the proxy still fails a known near-frontier sign and its error is much larger than the edge we need to rank. The future proxy spread is only `0.000015142`, so the ranking is not interpretable unless the near-frontier anchors can be held out correctly.
- public LB 관측 반응: if a proxy-ranked E86/E90/E85 file later improves, it should not retroactively validate H92 unless the proxy also becomes able to hold out E95/mixmin/E72. The current evidence says public slots remain sensors, not supervised LB-regression optimization targets.
- 제출 전략: no E98-ranked submission. Keep the next public file hypothesis-based: E90 for row-coherent retained structure, E86 for max source-consensus upside, or E85 for conservative p95 tail floor.

### H93. E95-conditioned local+tail transfer can rerank unresolved post-E95 candidates

- 상태: supported as a negative ranking update; not a submission generator.
- 왜 그럴듯한가: E96's tail worlds explained the E72 public miss, but after E95's public gain those worlds must also explain why the hard-tail fallback improved. A minimal local-margin plus tail-exposure transfer model can test whether E90/E86/E85 still look plausible after this second observation.
- 맞다면: many E96 scenarios should admit positive/interpretable alpha and lambda values that exactly reconstruct both E72 and E95. If E90/E86/E85 are true improvement candidates, they should beat E95 across a nontrivial share of those E95-conditioned worlds or have better mean/p95 predicted deltas.
- 틀리다면: E95 should remain the best mean/p95/winner candidate after conditioning, and E90/E86/E85 beat-E95 rates should collapse. If alpha/lambda are mostly negative or extreme, the whole two-term transfer view should be rejected.
- 최소 실험: `analysis_outputs/e99_e95_conditioned_tail_transfer.py`, solving `public_delta = alpha * local_all_delta + lambda * E96_tail_delta` for each complete E96 scenario using the observed E72 and E95 public deltas, then scoring E85/E86/no-Q2/E90/E89/E95.
- 관측: all `3894` complete E96 scenarios solved; `3849` had positive alpha/lambda, and `3452` passed the broad-plausible filter. Broad-plausible median alpha/lambda were `3.310470` and `1.345192`. E95 was winner mode, best mean, and best p95. Broad-plausible mean deltas were E95 `-0.000015311`, E89 `-0.000011477`, E85 `-0.000005652`, E90 `-0.000001938`, no-Q2 `-0.000000021`, and E86 `+0.000005034`. Beat-E95 rates were E89 `0.195829`, E85 `0.031866`, no-Q2 `0.023175`, E90 `0.002607`, and E86 `0.000290`.
- 성공/폐기 기준: H93 supports the negative ranking claim: E95-conditioned local+tail worlds do not justify an immediate E90/E86/E85 improvement bet. The remaining nontrivial counterfactual is E89, not because it dominates E95, but because it is the only unresolved file with material E95-beat rate under the conditioned worlds.
- public LB 관측 반응: if E89 later beats E95, public tail realization is closer to diffuse/cell-fallback E89 geometry than to E95's selected hard-tail cells. If E90/E86 beats E95 despite E99, then the two-term local+tail abstraction missed a row-coherent structural-retention effect.
- 제출 전략: no E99 file. Keep E95 as current frontier. If spending exactly one diagnostic slot for expected E95-beat probability, E89 is now the sharper counterfactual; E90 should be used only for the explicit row-coherent retained-structure question.

### H94. E89's E95-beat counterfactual is concentrated in Q2/S3 diffuse-tail worlds

- 상태: supported as a diagnostic public-world hypothesis; not a broad improvement claim.
- 왜 그럴듯한가: E99 gave E89 a nontrivial `0.195829` E95-beat rate while still keeping E95 best mean/p95. That pattern suggests E89 is not globally better, but may dominate a specific tail allocation that E95's hard-tail localization undercovers.
- 맞다면: E89-beats-E95 cases should cluster around a target/mask family with positive tail-surplus, and E89 should remain worse or neutral outside that family. The favorable slice should explain the E89 edge through tail advantage rather than local structural margin.
- 틀리다면: E89's beat cases should be diffuse across masks/orders, or should be driven by generic lower local loss rather than tail-surplus. Q2/S3 slices should not have much higher beat rate than the broad average.
- 최소 실험: `analysis_outputs/e100_e89_counterfactual_anatomy.py`, decomposing E99 broad-plausible scenarios by `mask_name`, `family_mask`, `order_name`, tail advantage, required tail advantage, and tail surplus.
- 관측: broad-plausible scenarios `3452`; overall E89 beat-E95 rate `0.195829`; E89 live win-rate `0.188876`; E95 live win-rate `0.800406`; mean E89-minus-E95 delta `+0.000003833`. E89-beating cases were `676` scenarios with mean tail surplus `+0.000002916` and top mask `q2s3`. The `q2s3` slice had `n=368`, beat rate `0.779891`, mean E89-minus-E95 `-0.000005030`, and mean tail surplus `+0.000003262`. Non-beating cases had top mask `s1s2s3` and mean tail surplus `-0.000004272`; `s1s2s3` and `e95_fallback_cells` did not provide material E89-beat support.
- 성공/폐기 기준: supported because the E89-favorable worlds are not broad. They are concentrated in Q2/S3 diffuse-tail allocations where E89's older E72-cell fallback gains enough tail surplus to overcome its local disadvantage versus E95.
- public LB 관측 반응: if `submission_e89_e72decontam_00d7807f.csv` beats E95, public labels likely realized more Q2/S3 diffuse E72-cell tail than E95 localized. If it loses, E95's hard-tail cells remain the better explanation and E89 should be retired as a near-term successor.
- 제출 전략: E89 is the next single public slot only as a Q2/S3 diffuse-tail sensor. Do not present it as a general lower-downside candidate or as evidence against E95 unless the public observation confirms it.

### H95. E95's remaining Q2/S3 tail risk is separable as a smaller rollback than full E89

- 상태: supported locally; public sensor pending.
- 왜 그럴듯한가: E100 showed E89's only E95-beat pocket is Q2/S3 diffuse-tail. Full E89 carries extra movement and is worse than E95 on broad mean. If the hidden world is truly "E95 over-localized or over-amplified Q2/S3 tail cells", then a small E95-relative Q2/S3 rollback should test that hypothesis more cleanly than full E89.
- 맞다면: E95-to-mixmin rollback on selected Q2/S3 cells should remain strict/deployable, lower E72-adverse exposure, keep combo/hidden/world/block support, and beat E95 in E95-conditioned broad and Q2/S3-tail scenarios with non-positive p95 risk.
- 틀리다면: Q2/S3 rollback should fail strict combo stress, lose local margin, only work under non-strict inverse-top-conflicted rows, or beat E95 only in the Q2/S3 slice while worsening broad-plausible scenarios.
- 최소 실험: `analysis_outputs/e101_q2s3_tail_graft_probe.py`, generating E95-based grafts from E89/E85/mixmin over Q2/S3 selectors and scoring them with E83 stress plus E96/E99 E95-conditioned transfer.
- 관측: E101 generated `618` rows, `612` grafts, `581` strict-like rows, and `54` pass rows. It materialized `analysis_outputs/submission_e101_q2s3tail_177569bc.csv`, which shrinks E95's effective Q2/S3 movement by `25%` toward mixmin on only `50` active cells versus E95. The selected file has all delta `-0.0000253724`, E72-adverse exposure `0.000692235` vs E95 `0.000788914`, hidden Q2/S3 `-0.000191316`, world `-0.000115685`, block win `0.75`, strict/deployable `true`, and E95-conditioned broad-plausible mean/p95/beat-E95 of `-0.0000162053`, `-0.000001564`, and `0.983488`.
- 성공/폐기 기준: supported locally because the candidate survives strict stress and has non-positive p95 in broad-plausible E95-conditioned worlds. It is still a public sensor, not proof: the transfer model may overweight the E72/E95 hard-tail abstraction, and the selected move is a small rollback rather than a new block-state representation.
- public LB 관측 반응: if E101 improves over E95, update the world model to "E95's retained E86 structure is useful, but Q2/S3 tail amplitude is too high; small rollback beats full E89." If E101 worsens, Q2/S3 rollback is overfit to tail-transfer stress and the active frontier remains E95; full E89 should only be used if the public question specifically remains diffuse Q2/S3 allocation.
- 제출 전략: next highest-information file is `analysis_outputs/submission_e101_q2s3tail_177569bc.csv`. It should be submitted before full E89 because it isolates the E100 hypothesis with fewer changed cells and less non-Q2/S3 movement.

### H96. E101's 50 active Q2/S3 cells are a hidden subject/block-local selector

- 상태: mostly rejected; weak edge-local variant remains live.
- 왜 그럴듯한가: E101 changes only 50 Q2/S3 cells. If those cells are concentrated in a few hidden submission blocks or subjects, then the next improvement after E101 should be a block-local rollback mask rather than a target-axis amplitude line.
- 맞다면: active cells should touch fewer blocks/subjects/rows than a target-count-preserving random Q2/S3 selection, have high max cells per hidden block/subject, or show strong context-type concentration.
- 틀리다면: active cells should be spread across many blocks and all subjects, with no significant block/subject concentration after preserving the Q2/S3 target counts. Any residual structure should be weak or tied to row position rather than block identity.
- 최소 실험: `analysis_outputs/e102_e101_active_cell_structure_audit.py`, building a 500-cell Q2/S3 atlas, attaching hidden block metadata, computing enrichment, and running a `20000`-draw target-count-preserving permutation null.
- 관측: E101 active cells are `50` cells across `48` rows, `26` hidden blocks, and all `10` subjects. Q2/S3 split is `11/39`, and active cells are exactly `25%` rollback toward mixmin. The strongest target-count null result is edge-or-near-edge rate `0.620` vs null mean `0.471289`, p `0.016999`; mean edge distance is `1.680` vs null `2.138444`, p `0.040848`. Block/subject concentration is absent: max cells per block is `4` with p `0.997300`, blocks touched `26` with p `0.935553`, and subjects touched `10` with p `1.0`.
- 성공/폐기 기준: reject the strong block/subject-local selector version. Keep only a weak edge-local calibration variant because edge proximity is the only non-random structure under the null.
- public LB 관측 반응: if E101 improves, the follow-up should first test Q2/S3 amplitude/edge-risk variants, not subject/block handcrafted masks. If E101 worsens, generic Q2/S3 rollback is weakened; edge-local rollback remains a lower-priority diagnostic because E102 did find a small edge signal.
- 제출 전략: no E102 submission. E101 remains the public sensor. E102 changes the post-E101 branch decision, not the next file.

### H97. E101's edge-local clue can replace the full Q2/S3 rollback with a sharper edge selector

- 상태: direct replacement rejected; amplitude-line diagnostic remains live.
- 왜 그럴듯한가: E102 found E101 active cells are unusually close to hidden block edges. If boundary rows are where E95 over-moves Q2/S3, an edge-local rollback might lower tail risk while changing fewer cells than E101.
- 맞다면: edge-only or edge-enriched masks should pass E101-style strict stress, improve E95-conditioned broad mean/p95, and preserve or improve E101's beat-E95 rate. A materialized E103 file should dominate E101 under mean, p95, and beat-rate together.
- 틀리다면: edge-only masks should fail strict or p95 stress, or improve mean only by sacrificing beat-rate. The best variants should collapse back to the same active-all amplitude line as E101 rather than a distinct edge selector.
- 최소 실험: `analysis_outputs/e103_edge_local_q2s3_amplitude_probe.py`, reusing E101's scoring and E95-conditioned transfer frame while scanning active/edge/interior/S3/Q2/top-gap masks and rollback alphas from E95 toward mixmin.
- 관측: E103 scanned `180` variants. `12` rows passed E103 stress, but `0` dominated E101. No submission was materialized. The best passing active-all alpha `0.375` improved broad mean/p95 versus E101 (`-0.000023425` / `-0.000002159`) but reduced beat-E95 rate to `0.980881` from E101's `0.983488`. Edge-only alpha `1.0` had a favorable mean but positive p95 (`+0.000007795`) and failed strict.
- 성공/폐기 기준: reject the direct edge-selector submission claim because edge masks do not dominate E101 and fail the p95/strict safety needed for a next public file. Keep edge proximity as a calibration-risk feature because it remains a non-random diagnostic and the active-all amplitude line still passes.
- public LB 관측 반응: E103 does not change the next public file. If E101 later improves, edge energy can guide amplitude follow-up stress. If E101 worsens, E103 says edge-local variants are not already strong enough to rescue the branch without a new independent signal.
- 제출 전략: no E103 submission. Keep `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` as the next sensor. Do not submit edge-only or top-gap edge masks before E101 public feedback.

### H98. E101 alpha 0.25 is an amplitude Pareto cliff, not a coarse-grid accident

- 상태: locally supported; no replacement submission.
- 왜 그럴듯한가: E103 found that higher active-all rollback alpha could improve broad mean/p95 but lower E101's beat-E95 scenario support. A fine grid is needed to know whether a nearby alpha can dominate E101 or whether the support drop starts immediately.
- 맞다면: alpha values just above `0.25` should improve mean/p95 only by sacrificing beat-rate; edge/interior submasks should not rescue the tradeoff; no row should dominate E101 on mean, p95, and beat-rate together.
- 틀리다면: a nearby alpha, edge mask, or top-gap mask should pass E101-style stress and dominate E101 across all three transfer metrics, creating a materialized E104 submission.
- 최소 실험: `analysis_outputs/e104_e101_amplitude_pareto_cliff.py`, fine-scanning alphas `0.000-0.500` by `0.005` over active-all, active-S3, top-gap, edge, and interior masks under the E101/E103 E95-conditioned transfer frame.
- 관측: E104 scanned `505` variants. `228` rows passed E101-style stress, but `0` dominated E101 and no file was materialized. For active-all, alpha `0.250` matches E101 at broad mean/p95/beat `-0.000016205` / `-0.000001564` / `0.983488`; the first alpha above E101 with beat-rate loss is `0.255`. Alpha `0.255` improves mean/p95 by about `3.02e-7` / `2.6e-8`, but lowers beat-rate by `0.000289687`. Best passing active-all alpha `0.380` improves mean/p95 to `-0.000023695` / `-0.000002181`, but beat-rate drops to `0.980881`. Edge/interior masks have `0` pass rows.
- 성공/폐기 기준: support the Pareto-cliff claim. E101 is not globally optimal for every transfer metric, but it is the local point that preserves scenario support before amplitude risk starts rising.
- public LB 관측 반응: if E101 improves public, H98 says follow-up should test risk-tolerant amplitude variants deliberately, not assume higher alpha is automatically better. If E101 worsens, higher-alpha variants should be deprioritized because they already sacrifice E101's scenario support locally.
- 제출 전략: no E104 submission. Keep `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` as the next sensor. Higher alpha is a post-feedback branch, not a pre-feedback replacement.

### H99. E101 tests a subject/block-local S3 tail label world, not global Q2/S3 prevalence

- 상태: supported as public-feedback framing; public result pending.
- 왜 그럴듯한가: E101 changes only `50` Q2/S3 cells. Whether it beats E95 depends entirely on the hidden hard labels in those cells. If the active-cell label world follows global train prevalence, E101 may be a bad bet even if local E95-conditioned stress likes it.
- 맞다면: E101's favorable labels should be S3-dominated and sensitive to subject/block-local priors. Under global train priors its expected public delta should be unfavorable, while subject priors should bring it closer to live. A public E101 win would therefore imply local S3 tail departure rather than generic Q2/S3 rollback quality.
- 틀리다면: global priors should already make E101 favorable, Q2 should contribute material swing mass, or E101 should require an implausibly large number of favorable cells even under subject priors.
- 최소 실험: `analysis_outputs/e105_e101_public_label_breakeven.py`, computing E101-minus-E95 hard-label deltas for every active cell, then simulating hidden labels under global and subject train priors.
- 관측: active cells `50` with Q2 `11` and S3 `39`; support labels split `25/25` between label 0 and label 1. All-support delta is `-0.000096679`, all-adverse delta is `+0.000211677`. The minimum high-impact supportive cells to beat E95 is `23/50`; to match E95's edge over mixmin is `25/50`. S3 contributes `0.935862` of total flip benefit. Under global priors, expected E101-vs-E95 delta is `+0.000048971` and beat probability `0.016610`; under subject priors, expected delta is `+0.000007854` and beat probability `0.335360`.
- 성공/폐기 기준: support the framing claim. E101 is not a global-prior correction; it is a high-information sensor for whether the active subject/block-local S3-heavy cells realize labels on the rollback-favorable side.
- public LB 관측 반응: if E101 beats E95, strengthen a local S3 tail-label world and revisit amplitude only inside that world. If E101 loses, weaken generic Q2/S3 rollback and reject E104 higher-alpha amplification unless a new independent stress source appears.
- 제출 전략: no E105 file. Submit E101 if using one public slot; use E105 to interpret the result.

### H100. Subject-prior support can pre-gate E101 into a better submission

- 상태: rejected as pre-feedback candidate generator; kept as interpretation energy.
- 왜 그럴듯한가: E105 showed subject priors raise E101 beat probability from `0.016610` under global priors to `0.335360`, suggesting subject-supported active cells might be the safer subset.
- 맞다면: subject-support or subject-expected masks should pass E101 stress and dominate E101, or at least replace it on broad mean/p95/beat while improving prior health.
- 틀리다면: prior-healthier masks should lose broad scenario support, or broad-transfer masks should become prior-unhealthy/global-prior shortcuts.
- 최소 실험: `analysis_outputs/e106_e101_subject_prior_gate.py`, scanning subject expected delta, subject-support quantiles, S3-only masks, flip-benefit ranking, global/subject expected rankings, and alphas `0.25/0.50/0.75/1.00`.
- 관측: `268` variants, E101-pass `12`, prior-healthier `56`, interesting non-replacements `6`, replacement/dominating rows `0`; no submission was materialized. `active_s3_all` alpha `0.25` is interpretable but has broad mean/p95/beat `-0.000015728` / `-0.000001195` / `0.973349`, weaker than E101 `-0.000016205` / `-0.000001564` / `0.983488`.
- 성공/폐기 기준: reject as a pre-feedback candidate generator because no subject-prior-gated row replaces or dominates E101.
- public LB 관측 반응: E101 public feedback remains needed. A positive E101 result can revive E106 rows as post-feedback contrasts; before feedback they should not replace E101.
- 제출 전략: no E106 file. Submit E101 if using one public slot.

### H101. E101 feedback should choose the next branch by conditional E99 worlds, not unconditional local ranking

- 상태: supported as pre-feedback decision map; public result pending.
- 왜 그럴듯한가: E104 and E106 disagree in risk profile, and E101 public delta is the missing sensor for which E99 tail world public occupies. The next decision should depend on the observed E101-vs-E95 delta, not on an unconditional average over all possible tail worlds.
- 맞다면: E101 edge/small win should condition to coherent E99 scenarios and identify a follow-up family; E101 loss should either select older controls or show model tension if the E99/E101 world cannot produce loss.
- 틀리다면: all hypothetical outcomes should give the same ranking, E106 masks should dominate after subject-local framing, or E101 loss should be easy to explain without model tension.
- 최소 실험: `analysis_outputs/e107_e101_feedback_decision_map.py`.
- 관측: candidate universe `292`, outcomes `6`, summary rows `1752`. Edge win, small win, and tie are within-tolerance. Strong win and both loss outcomes require nearest scenario matching. Edge/small wins rank E104 active-all high-alpha rows first; strict E101-pass follow-ups are lower alpha around `0.380`; E106 masks do not outrank E104. Loss outcomes remain near E101 tie and are marked tension.
- 성공/폐기 기준: support as decision-map. Use E107 after E101 public feedback; do not materialize a pre-feedback file.
- public LB 관측 반응: E101 win -> amplitude-up E104 branch. E101 loss -> falsify/strain the E99/E101 rollback model and demote E104/E106 follow-ups.
- 제출 전략: no E107 file. Keep `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` as the next public sensor.

### H102. E101-win amplitude follow-up should be pre-materialized but not pre-submitted

- 상태: supported as decision hygiene; public result pending.
- 왜 그럴듯한가: E107 already chooses E104 active-all amplitude-up after an E101 edge/small win, but leaving the next files implicit risks post-hoc candidate choice once the public result is known.
- 맞다면: the same E104 rows should be reproducible through the E101/E104 stress path, produce valid submission files, and keep the same conditional E107 ranking: high-alpha amp050 as top conditional upside, lower-alpha amp038 as the conservative E101-pass branch.
- 틀리다면: materialized files would not match E107 labels/tags, stress metrics would differ, or E101 tie/loss worlds would also justify the files.
- 최소 실험: `analysis_outputs/e108_e101_win_amplitude_followup.py`.
- 관측: two files were materialized. `analysis_outputs/submission_e108_if_e101win_amp050_079aab57.csv` is alpha `0.500`, not E101-pass, but ranks `1` vs E101 under both edge-win and small-win conditioned worlds. `analysis_outputs/submission_e108_if_e101win_strict_amp038_64514c53.csv` is alpha `0.380`, E101-pass, and ranks `54`/`49` under edge/small win. Tie worlds have positive p95 vs E101 and loss worlds are E107 model-tension cases.
- 성공/폐기 기준: support as a conditional materialization layer, not as a new pre-feedback submission. The files are valid only if E101 improves by edge/small-win scale.
- public LB 관측 반응: E101 edge/small win -> submit amp050 for upside or amp038 for conservative branch. E101 tie/loss -> do not submit E108; update the hidden-tail world model.
- 제출 전략: no immediate E108 submission. These are post-E101-win files only.

### H103. E101 tie/loss means the active Q2/S3 hard-label world failed, not that the same rollback should be amplified

- 상태: supported by active-cell hard-label simulation; public result pending.
- 왜 그럴듯한가: E107 marked E101 loss as model tension, but E105 showed E101 depends on only `50` active Q2/S3 labels. If a tie/loss happens, those active labels should reveal whether the same rollback direction remains alive.
- 맞다면: sampled tie/loss worlds should show missing high-impact support labels, especially S3; higher E101-style amplitudes should be worse than E101 in those buckets; retaining E95/E90/E86 active-cell behavior should look healthier.
- 틀리다면: E108 amp050/amp038 or subject-prior masks would still beat E101 in loss buckets, or loss buckets would be driven by a clean subject/block selector rather than broad active-cell support failure.
- 최소 실험: `analysis_outputs/e109_e101_tie_loss_label_world_audit.py`.
- 관측: under subject priors, outcome rates are edge win `0.142385`, small win `0.132400`, tie `0.125515`, small loss `0.355350`, large loss `0.244350`. Top10 support rate drops from `0.916933` in edge wins to `0.805226` in small loss and `0.719218` in large loss; support flip-share drops from `0.749273` to `0.650286` and `0.585604`. In subject small-loss worlds, E108 amp050/amp038 active mean vs E101 is `+0.000011723` / `+0.000006026`, beat-E101 rate `0`; E86/E90/E95 rank above E101 on active cells.
- 성공/폐기 기준: support as a negative branch rule. E101 tie/loss closes same-line E108 amplification and subject-prior rescue before any new public-world model is built.
- public LB 관측 반응: E101 win keeps H102 live. E101 tie/loss strengthens H103 and should redirect toward active-cell retention, E90/E86 retained-structure testing, or non-active diffuse-tail experiments, not E104/E106.
- 제출 전략: no E109 file. Use this as the loss-side decision map after E101 feedback.

### H104. E101 tie/loss can be rescued by non-active E89/diffuse-tail graft

- 상태: rejected as strict submission; diagnostic sensor branch remains.
- 왜 그럴듯한가: E109 says the E101-active cells fail in tie/loss worlds, but it does not test whether the older E89 diffuse-tail law survives outside those `50` cells. If E89's remaining signal is non-active Q2/S3 tail structure, restoring active cells while keeping non-active tail movement could isolate the useful part.
- 맞다면: active-restored E89/E85 or E95-to-E89/E85/E90/E86 non-active grafts should be active-loss-safe and also pass broad E95-conditioned mean/p95/beat stress. At least one strict candidate should be materialized.
- 틀리다면: active-loss-safe rows can exist, but broad E95-conditioned p95/mean remain positive and no strict candidate survives.
- 최소 실험: `analysis_outputs/e110_e101_negative_branch_nonactive_tail.py`.
- 관측: `45` unique candidates were built. Non-control active-loss-safe rows existed (`36`) and `8` rows were diagnostic sensors, but strict candidates were `0` and no submission was materialized. The best non-control row, non-active `S1/S2/S3` E86 alpha `0.25`, still had broad mean/p95 vs E95 `+0.000000714` / `+0.000002798`; active-restored E89/E85 variants also kept positive broad stress.
- 성공/폐기 기준: reject the automatic E101-negative fallback to full E89, active-restored E89/E85, or non-active grafts. Keep them only as explicit sensors if the slot is meant to test diffuse-tail structure rather than expected improvement.
- public LB 관측 반응: E101 win keeps H102/E108 live. E101 tie/loss closes E108 and also fails the simple non-active E89/graft rescue; it should trigger public-world-model rebuild or a deliberately different retained-structure sensor.
- 제출 전략: no E110 file. If E101 ties or loses, keep E95 as standing best and do not route automatically to E89/non-active grafts.

### H105. The E95 plateau is target-axis hard-tail surgery, not broad model improvement

- 상태: supported as current SAUNA world model; public E101 result pending.
- 왜 그럴듯한가: E72 was a locally attractive sparse/latent movement but failed public, while E95 improved by only `0.0000153107`. If the plateau is caused by LogLoss tail calibration rather than model capacity, public-positive movement should be target-axis and cell-risk selective.
- 맞다면: E72's public-negative movement should look broad across target axes, while E95's public-positive movement should be more target-pruned and closer to a hard-tail edit. E101 should then be the smallest sensor, changing only the remaining ambiguous Q2/S3/S3-heavy cells rather than reopening broad movement.
- 틀리다면: E95 and E72 should have similar target-axis geometry, or E95 should look like a larger global movement rather than a selective axis edit. Full E89/E90/E86 should be as clean as E101 around E95.
- 최소 실험: `analysis_outputs/e111_sauna_frontier_movement_atlas.py`.
- 관측: versus mixmin, E72 failed with public delta `+0.0001011367`, active cells `893`, L1 `2.203482`, Q-share `0.450788`, S-share `0.549212`, and cosine with E95 direction `0.327033`. E95 improved with public delta `-0.0000153107`, active cells `550`, L1 `1.509562`, Q-share only `0.019948`, S-share `0.980052`, and E95-confident movement share `0.386257`. E101 versus E95 changes only `50` Q2/S3 cells across `48` rows with S-target share `0.905306`.
- 성공/폐기 기준: support the plateau explanation if public-positive E95 is target-pruned and E101 remains the smallest coherent kill-test. Discard if a future public-positive file succeeds through broad Q/Q3/S4 movement without tail stress.
- public LB 관측 반응: E101 win means the target-axis surgery was directionally right but over-tight on Q2/S3 tail cells. E101 tie/loss means E95's current axis/tail surgery remains the standing law and broad fallback remains unjustified.
- 제출 전략: no E111 file. Submit E101 as the next observation if using one public slot.

### H106. S-axis movement survives because it carries subject/block state; Q-axis movement is temporal but hard to transfer

- 상태: supported as a refinement of H105.
- 왜 그럴듯한가: E111 showed E95 is S-heavy target-axis surgery, but submission geometry alone cannot say whether that axis is real or just public-tail luck. If S targets carry stronger subject/block state while Q targets carry short temporal persistence that is not safely observable in test, then E95's S-heavy survival and Q/Q3 contamination failure can coexist.
- 맞다면: S/E95-active targets should have larger subject-prior gains than inactive axes; Q targets may show higher local temporal persistence, but train/test adjacency should be sparse enough that direct temporal copy remains unsafe. Q/S pairwise correlations should be weak relative to within-axis correlations.
- 틀리다면: S and E95-active axes should not show stronger subject-prior structure, Q/S correlations should be high enough to justify broad target mixing, or test rows should be densely bracketed by nearby train labels so temporal Q structure is directly usable.
- 최소 실험: `analysis_outputs/e112_sauna_qs_temporal_axis_audit.py`.
- 관측: S-target mean subject-LOO logloss gain is `0.068724` vs Q-target `0.020146`; S subject-rate variance is `0.040376` vs Q `0.020313`. The three strongest subject-prior targets are exactly `S3`, `S2`, and `S1`, all E95-active. Q targets have stronger temporal persistence lift (`0.135700` vs S `0.087255`), led by `Q2`, `Q3`, `Q1`, but test rows are weakly bracketed by nearby train labels: prev<=3 days `0.340000`, next<=3 days `0.228000`, both sides `0.080000`. Pairwise correlations are within-S `0.260803`, within-Q `0.187934`, and Q-S only `0.030038`.
- 성공/폐기 기준: support the refined world model. E95 is not a row-neighbor temporal-copy solution; it is a restricted translation of subject/block S-state plus a small Q2 temporal-tail question. Discard if a future public-positive broad Q/Q3/S4 movement succeeds without target-tail stress.
- public LB 관측 반응: E101 win means the Q2/S3 boundary between temporal-tail and S-subject state was too tight in E95. E101 loss means S-subject-state surgery remains right and Q2 temporal rollback is not public-real.
- 제출 전략: no E112 file. Keep E101 as the next public kill-test; do not build direct Q1/Q3 temporal propagation without a stronger train/test adjacency bridge.

### H107. Visible raw lifelog context can replace missing Q temporal labels

- 상태: rejected as a submission-safe rescue route; retained only as diagnostic energy.
- 왜 그럴듯한가: E112 showed Q targets have stronger temporal persistence than S targets, but test label adjacency is sparse. If raw lifelog coverage carries the missing daily context, an I-JEPA-style context head should recover temporal target state without direct label neighbors.
- 맞다면: raw daily context should improve temporal holdout LogLoss over subject prior, especially on Q targets or E95-boundary targets, and random/temporal behavior should agree rather than diverge.
- 틀리다면: raw context may show AUC/ranking signal while worsening calibrated temporal LogLoss, or improve only random within-subject splits. That would mark a shortcut/collapse signal rather than a submission-safe representation.
- 최소 실험: `analysis_outputs/e113_sauna_raw_context_visibility_audit.py`, aggregating raw parquets into daily coverage/context features, then testing subject-prior, raw-only, and raw+subject-prior logistic heads under temporal-last25-by-subject and random-within-subject splits.
- 관측: raw coverage exists for all train/test rows (`1.000000`/`1.000000`) with `114` daily raw features, but raw+prior worsens temporal LogLoss versus subject prior on Q targets by `+0.038804`, S targets by `+0.058534`, and E95-active axes by `+0.059881`. Random split also worsens on average (`+0.007833` Q, `+0.016497` S), while Q2's random-only improvement conflicts with its temporal degradation. Only S3 has a small temporal gain (`-0.004643`).
- 성공/폐기 기준: reject broad raw-context probability movement because it fails temporal calibrated LogLoss after subject prior. Keep S3 raw context as weak diagnostic energy, not a new file family.
- public LB 관측 반응: broad Q/Q3 raw-context movement should not be submitted before a temporal calibration gain exists. If E101 improves, raw context can be revisited only as S3/Q2 boundary energy; if E101 loses, raw context does not rescue the Q temporal branch.
- 제출 전략: no E113 submission. Keep E101 as the next public kill-test.

### H108. Raw context can pre-validate E101's active-cell support labels

- 상태: rejected; E101 remains a public hard-label sensor rather than a raw-validated improvement candidate.
- 왜 그럴듯한가: E105 made E101 depend on only `50` active Q2/S3 cells, mostly S3 flip benefit. Even if broad raw-context prediction fails, raw context might still assign higher probability to the support labels that would make E101 beat E95.
- 맞다면: raw+subject-prior support probability should exceed subject-prior support probability on E101 active cells, especially on S3. Monte Carlo beat probability and expected E101-vs-E95 delta should improve relative to subject priors. Validation-gating raw to only temporal-valid targets should improve further.
- 틀리다면: raw support probability should fall below subject prior or reduce E101 beat probability, especially on the S3 cells that dominate flip benefit.
- 최소 실험: `analysis_outputs/e114_e101_raw_context_support_audit.py`, fitting full-train raw+subject-prior heads for Q2/S3 with leave-one-row subject-prior train features, then scoring E105's active cells by support-label probability and hard-label expected delta.
- 관측: subject prior gives expected E101-vs-E95 delta `+0.000003926`, beat probability `0.336655`, and mean support probability `0.587686`. Raw+prior worsens these to `+0.000007010`, `0.238325`, and `0.579426`; validation-gated raw is worse again at `+0.000007229` and `0.230710`. S3 owns `0.935862` of flip benefit, but raw S3 support probability is `0.589463` vs subject `0.604450`.
- 성공/폐기 기준: reject raw-context pre-validation. The raw head does not kill E101, because E101 was never a raw-context bet, but it removes a possible independent support source.
- public LB 관측 반응: if E101 wins, the support labels were not visible to this raw-context head; revisit hidden local S3 label-world or public subset structure. If E101 loses, raw context already pointed away from the active-cell support world.
- 제출 전략: no E114 submission. Keep E101 only as a public sensor, not as a raw-validated expected-improvement file.

### H109. E101 is the highest-actionability public sensor after raw-support failure

- 상태: supported as current decision rule, not as proof of public improvement.
- 왜 그럴듯한가: E114 removed raw support for E101, so the next file must be justified by information value. If E101 still dominates E89/E85/E90/E86 as a sensor, its public result should split E95-conditioned worlds into several actionable win/tie regimes while preserving a high E95-beat rate.
- 맞다면: in E72/E95-consistent broad-plausible worlds, E101 should have high outcome entropy, high actionable score, and win/tie bins that map to concrete post-feedback branches. Other pending controls should either collapse into loss-heavy outcomes or have much lower actionable information.
- 틀리다면: E89/E85/E90/E86 should provide comparable actionable information, or E101 should mostly collapse into a single ambiguous/tie/loss outcome after E114.
- 최소 실험: `analysis_outputs/e115_public_sensor_information_audit.py`, comparing control E101/E89/E85/E90/E86/mixmin outcome distributions across `3452` E95-conditioned broad-plausible worlds from E107/E99.
- 관측: E101 has actionable information score `1.613953`, entropy `1.728493`, beat-E95 rate `0.983488`, and win/tie/loss `0.911645/0.088355/0.000000`. E89 is much weaker (`0.233881`, beat `0.195829`, loss `0.580243`), and E85/E90/E86 are mostly loss-heavy with actionable scores `0.025735/0.011719/0.002573`.
- 성공/폐기 기준: support E101 as next public sensor because it is the only live file that is both directionally plausible and information-rich. Do not reinterpret this as public-label certainty; the branch still requires actual LB feedback.
- public LB 관측 반응: E101 win validates the S3-heavy Q2/S3 over-amplification branch and activates E108 amplitude-up. E101 tie/loss says the E99/E101 broad-world abstraction is incomplete and should be rebuilt, not rescued with same-line masks.
- 제출 전략: no E115 submission. Keep `analysis_outputs/submission_e101_q2s3tail_177569bc.csv` as the next public sensor.

### H110. E101 public feedback must be decoded before post-hoc reasoning

- 상태: supported as a procedural guardrail for the next public observation.
- 왜 그럴듯한가: E101 is a sensor, not a guaranteed improvement. If its public LB is interpreted after the fact, the same result could be rationalized into incompatible branches such as E108 amplification, E89 diffuse fallback, raw rescue, or model rebuild.
- 맞다면: exact LB bands should be enough to pre-register which world model is strengthened, which branch is allowed, and which tempting followups are forbidden.
- 틀리다면: E101 public deltas would not map cleanly to branch decisions, or the E107/E115 bands would be too ambiguous to prevent post-hoc candidate selection.
- 최소 실험: `analysis_outputs/e116_e101_public_feedback_decoder.py`, mapping future E101 LB to delta bands relative to E95 public `0.5762913298` with E115 rates and E107 tension flags.
- 관측: E116 defines strong win `<= 0.576261330`, edge win `(0.576261330, 0.576280330]`, small win `(0.576280330, 0.576288330]`, tie `(0.576288330, 0.576294330]`, and loss `> 0.576294330`. Win bands activate exact-delta rerun/E108 consideration; tie/loss bands keep E95 and block same-line rescue.
- 성공/폐기 기준: support if the decoder prevents branch ambiguity after E101 public feedback. It is not a model score and should be replaced only by a rerun using the actual observed delta.
- public LB 관측 반응: use the decoder first. Strong/edge/small win means the Q2/S3 rollback direction is public-real; tie/loss means rebuild the public-world model before another same-family file.
- 제출 전략: no E116 submission. Use the decoder as a guard before any post-E101 file.

### H111. A better E95-shaped candidate is already hidden in the documented submission universe

- 상태: mostly rejected; only known/conditional same-family neighbors remain.
- 왜 그럴듯한가: E95 improved public by only `0.0000153107`. If the improvement came from a general S-heavy hardtail law, prior scans and reports may already contain another candidate with the same target-axis geometry and lower E72-tail risk.
- 맞다면: among documented submissions there should be multiple large S-heavy, E95-aligned, lower-tail candidates not already explained by E85/E89/E101/E108.
- 틀리다면: the E95-like neighborhood should be tiny, dominated by already-known contrast files, and should not contain an untested lower-tail replacement.
- 최소 실험: `analysis_outputs/e117_e95_like_neighborhood_audit.py`, scanning referenced submissions, deduplicating prediction tensors, and measuring E95-direction cosine, Q/S movement share, E72-adverse hard-label exposure, and E95-relative edit size.
- 관측: E117 resolved `4477` referenced files and deduplicated them to `4031` unique tensors. Only `10` fell into the E95-like neighborhood. Only `4` had no higher E72-adverse exposure than E95, and they were E101, E85, and the two E108 post-E101-win variants. E101 is an E95-relative micro edit (`50` active cells vs E95, Q2/S3 share `1.000000`), not a standalone replacement. The closest non-E95 neighbor E89 has slightly higher E72-adverse exposure (`0.000799109`) than E95 (`0.000788914`).
- 성공/폐기 기준: reject the "just search old submissions harder" branch unless a newly generated file enters this neighborhood with lower tail risk and an independent stress argument. Do not use E108 before E101 public feedback because its lower tail is conditional on E101 winning.
- public LB 관측 반응: if E101 improves, it validates one of the only lower-tail E95-relative neighbors and opens E108 exact-delta rerun. If E101 ties/loses, there is no untested lower-tail E95-like candidate in the documented universe to auto-promote.
- 제출 전략: no E117 submission. Keep E101 as the next sensor; otherwise move to new structural/block-state generation.

### H112. E101 active cells are visible edge/flank transition-state calibration risk

- 상태: partially supported but not certified.
- 왜 그럴듯한가: E102 showed E101 active cells are edge-enriched, E105 showed S3-heavy subject-prior dependence, and E114 showed raw context cannot see the support labels. If hidden block transitions carry the missing signal, visible train-label flanks should improve E101 hard-label support over subject priors.
- 맞다면: active cells should be enriched for block-edge and flank-conflict contexts, and a flank-derived prior should raise E101 beat probability relative to subject priors.
- 틀리다면: flank priors should behave like global/subject priors, active cells should not be structurally enriched, or expected E101-vs-E95 delta should remain clearly adverse under every visible flank view.
- 최소 실험: `analysis_outputs/e118_e101_flank_label_support_audit.py`, scoring E101 active-cell hard-label deltas under global/subject/flank priors and target-count-preserving structure nulls.
- 관측: best flank prior `edge_endpoint_beta` raises beat-E95 probability to `0.437780` versus subject `0.337185` and global `0.015920`, but expected delta remains positive at `+0.000003014` per all cells. Active cells are edge/near-edge enriched (`0.620000` vs null `0.471289`, p `0.016999`) and flank-conflict enriched (`0.240000` vs null `0.149933`, p `0.048998`; conflict-given-both p `0.018649`).
- 성공/폐기 기준: support the edge/flank transition-state reading, but reject local certification because the best visible prior does not produce negative expected delta or high match probability against E95's public edge.
- public LB 관측 반응: if E101 wins, H112 strengthens and E108/E104 follow-ups should be rerun through exact E101-delta conditioning. If E101 ties or loses, the visible flank signal was real but insufficient, and same-line amplitude escalation should stay closed.
- 제출 전략: no E118 submission. Keep E101 as the next sensor; use E118 only to pre-register how to interpret that sensor.

### H113. Visible flank support can replace full E101 with a gated variant

- 상태: rejected before public feedback.
- 왜 그럴듯한가: E118 raised E101 beat-E95 probability under edge/flank priors from subject `0.337185` to `0.437780`, and active cells were enriched for edge and conflict contexts. If that support identifies the right cells, a flank-gated subset should reduce risk while retaining E101's benefit.
- 맞다면: flank/support/edge/flip-benefit selectors should produce at least one E101-pass variant that dominates full E101 on broad mean, broad p95, and broad beat-rate.
- 틀리다면: smaller visible-context gates should improve mean only by sacrificing scenario support, or fail p95/strict support before beating E101.
- 최소 실험: `analysis_outputs/e119_e101_flank_gate_variant_stress.py`, scanning E95-to-E101 movement over flank-support, expected-delta, edge, S3/Q2, conflict, and flip-benefit selectors.
- 관측: E119 generated `602` variants, `66` E101-pass rows, and `0` E101-dominating rows. Active-all scale `1.50` improved mean/p95 versus E101 but dropped beat-rate from `0.983488` to `0.980881`; scale `2.00` improved mean further but failed E101-pass and dropped beat-rate to `0.977984`. Gated rows such as `flip_benefit_best_top45`, `active_s3_all`, and `near_edge_first_top45` showed the same mean-vs-support tradeoff.
- 성공/폐기 기준: 폐기. E118 support remains interpretation energy, not a pre-feedback selector.
- public LB 관측 반응: if E101 later wins, use E119 as evidence that the full active-set law was necessary before amplitude-up; rerun exact-delta follow-ups rather than handcrafted flank gates. If E101 ties/loses, E119 prevents using flank support to rescue same-line gates.
- 제출 전략: no E119 submission. Do not replace E101 with a flank-gated file before public feedback.

### H114. E101 public small-loss means E95 is the standing hard-tail law

- 상태: supported by actual public feedback; same-line followups rejected.
- 왜 그럴듯한가: E116 pre-registered a loss-side branch where E101 fails to beat E95, E109/E110/E119 already showed that tie/loss should not be rescued by stronger same-line rollback, subject/flank gates, or non-active grafts. The actual E101 public result now lands in that branch.
- 맞다면: E101 should be worse than E95 but not necessarily catastrophic; it may still beat mixmin because most of E95's structural law remains. The exact result should be outside the favorable E99/E101 local stress distribution, implying model tension rather than ordinary amplitude tuning.
- 틀리다면: E101 would beat E95 or at least tie inside E116's near-zero band, or a pre-registered loss-side family would contain a strict follow-up candidate.
- 최소 실험: `analysis_outputs/e120_post_e101_public_observation_audit.py`, applying actual E101 public `0.5763003660` to the E116 decoder and cross-checking E107/E109/E110/E119 loss-side audits.
- 관측: E101 delta vs E95 is `+0.0000090362`, E116 outcome `small_loss`, exact E101 still beats mixmin by `0.0000062745`. It gives back `59.02%` of E95's mixmin gain and preserves `40.98%`. The actual public delta is `+0.0000252415` worse than the local E101 mean and `+0.0000106001` worse than local p95. E110 has non-control strict candidates `0`; E119 has E101-dominating rows `0`.
- 성공/폐기 기준: support H114 unless a new, non-same-line public-world model explains both E95 win and E101 small loss while producing a stress-surviving candidate. Reject automatic E108/E104/E106/E119/E89/non-active-graft followups.
- public LB 관측 반응: already observed. Future public candidates must state whether they are testing the two-point E95/E101 hard-tail boundary or a genuinely different hidden structure.
- 제출 전략: no immediate same-family submission. Keep E95 as frontier and rebuild the public-world model with E101 as a negative anchor.

### H115. E101 small-loss is a one-cell-scale S3 hard-label boundary, not an amplitude problem

- 상태: supported as the post-E101 boundary model; no direct submission branch.
- 왜 그럴듯한가: E101 is worse than E95 but still better than mixmin. That implies its active Q2/S3 rollback is partly public-real. The remaining difference is small enough that the determining object may be a few high-impact active cells rather than broad target amplitude.
- 맞다면: converting the observed public delta into E101 active-cell hard-label deltas should require most, but not all, available flip benefit. The exact-observed posterior should concentrate on high S3 support but not expose a clean visible gate.
- 틀리다면: the observed delta would require either almost no support, almost all support, a clean subject/block/edge selector, or a support pattern incompatible with E105/E118 priors.
- 최소 실험: `analysis_outputs/e121_e101_small_loss_inverse_posterior.py`, using actual E101 public `0.5763003660` as an aggregate active-cell budget and simulating `300000` label worlds per prior.
- 관측: all-support/all-adverse E101-vs-E95 deltas are `-0.0000966787` / `+0.0002116767`. The actual delta `+0.0000090362` requires `0.657165` of active flip benefit. Greedy top-flip supports first beat mixmin at `21`, match the observed boundary around `22`, and first beat E95 at `23`. Exact-observed worlds under local/flank priors have top10 support `~0.81-0.86`, top22 support `~0.73-0.74`, and S3 support `~0.58-0.60`; global prior makes the exact world rare (`0.007963`).
- 성공/폐기 기준: support if the exact boundary is a narrow high-impact S3 support budget and no clean visible gate appears. Discard if a non-public sensor later identifies the missing high-impact cells with stress-stable gains.
- public LB 관측 반응: already observed. Future same-family files must show an independent sensor for the missing high-impact S3 cells, not merely fit the E101 public delta.
- 제출 전략: no E121 submission. Keep E95 as current best; next file should test a different hidden structure or a newly validated S3-cell sensor.

### H116. Simple subject/flank/raw priors explain E101 small-loss, but cannot gate the next file

- 상태: supported as an explanation, rejected as a submission gate.
- 왜 그럴듯한가: E121 showed the exact public result is one high-impact S3-cell scale away from beating E95. If visible train-derived priors already forecast the small-loss branch, then the E99/E119 local transfer model was the wrong sensor. If those priors identify the boundary cells, same-line repair could remain possible.
- 맞다면: expectation-style subject/flank/raw priors should predict a positive but small E101-vs-E95 delta close to `+0.0000090362`, while the local transfer model may overestimate upside. A real gate would also need to downweight the critical rank-23 support cell that separates small loss from E95 win.
- 틀리다면: visible priors should predict a win or a large loss, fail the E116 branch, or expose a clean high-impact cell selector that E121 missed.
- 최소 실험: `analysis_outputs/e122_e101_independent_sensor_boundary_audit.py`, comparing pre-existing E119 local transfer, E118 train-flank priors, E114 raw-context priors, deterministic support gates, and E121 posterior cells.
- 관측: `raw_full_subject_prior_y1` expected `+0.000008889` with error `-0.000000148`; `flank_conflict_flat` expected `+0.000009521`; `flank_both_distance_beta` expected `+0.000009532`; `flank_subject` expected `+0.000007853`. E119 active-all local transfer expected `-0.000016205`, wrong sign. The critical rank `23` S3 cell still has high support under subject, edge, raw, and posterior views (`0.958333`, `0.972222`, `0.864418`, `0.940119`).
- 성공/폐기 기준: support the explanation because simple visible priors match the small-loss branch; reject the submission gate because no non-public view identifies rank `23` as adverse enough to stop before E95.
- public LB 관측 반응: already observed via E101. If a future file uses E121/E122 to choose cells, require an independent sensor not derived from the E101 public delta.
- 제출 전략: no E122 submission. Close same-line posterior gating; either search for a genuinely different S3-cell sensor or test a different hidden structure.

### H117. Cross-target transition motifs do not resolve the E95/E101 S3 boundary

- 상태: 반증됨 as a same-line gate; retained only as a collapse warning.
- 왜 그럴듯한가: E101's decisive boundary is S3-heavy and located near train-label flanks. If S3 is a noisy projection of a broader Q/S latent state, previous/next Q1/Q2/Q3/S1/S2/S4 states could identify the missing support/adverse cell better than direct S3 flank alone.
- 맞다면: a no-S3 transition-motif head should improve temporal S3 validation over subject prior or direct flank beta, and it should lower the critical rank-23 S3 support probability enough to justify stopping before the E95-beating support count.
- 틀리다면: motif heads should worsen temporal calibration or overfit interleaved context, and the rank-23 cell should remain support-like.
- 최소 실험: `analysis_outputs/e123_e101_transition_motif_s3_sensor.py`, using train-only neighbor-state motif features, temporal-tail/interleaved validation, and E101 active S3 boundary scoring.
- 관측: temporal-tail logloss deltas versus subject prior were `+0.135183` for `motif_no_s3`, `+0.246239` for `motif_full`, and `+0.349065` for `motif_plus_subject`; interleaved split was also worse. Rank-23 support stayed `0.943564` under no-S3 motif and `0.984326` under motif+subject. Motif aggregate expected E101 public deltas overshot the actual small loss (`~+0.000028` vs `+0.0000090362`).
- 성공/폐기 기준: discarded because the independent motif fails local temporal calibration and does not identify the decisive S3 cell. Keep it only as evidence that cross-target neighbor-state features can create unhealthy overconfident representations.
- public LB 관측 반응: no submission. If a future same-line file claims transition-motif support, it must first reverse this temporal validation failure and rank-23 support result without using public LB.
- 제출 전략: none. Same-line E101 repair remains closed; move to another hidden structure or a materially different S3-cell sensor.

### H118. The E99 two-term transfer world is incomplete after E101

- 상태: 부분 지지 후 수정 필요. E99 remains useful for E72/E95 hard-tail attribution, but rejected as a standalone post-E101 selector.
- 왜 그럴듯한가: E99 matched the failed E72 public sensor and the successful E95 public sensor with a compact `local_delta + hard_tail_delta` model. If the same hidden law governed E101, then the model should predict E101's small loss without seeing that score.
- 맞다면: broad-plausible scenarios should place E101 near the observed delta and preserve the public ordering `E95 < E101 < mixmin`, while leaving at least one future candidate with nontrivial E95-beat support.
- 틀리다면: E99 should overpredict E101, order-match scenarios should become rare, and the surviving E101-plausible subset should keep E95 dominant while making future candidates weak sensors rather than expected improvements.
- 최소 실험: `analysis_outputs/e124_e101_conditioned_tail_transfer.py`, rebuilding E96 scenarios with E101, solving E99 transfer on E72/E95 only, and using actual E101 as a held-out public sensor.
- 관측: broad-plausible worlds `3452` predicted mean E101 delta `-0.000031516` versus actual `-0.000006275`; only `57` worlds matched the E101 ordering, and only `57` were E101-sensor-plausible. Inside that subset E95 live win rate was `0.929825`; E89's beat-E95 rate was only `0.052632`, E85 `0.017544`, E90/E86 `0`.
- 성공/폐기 기준: support only the hard-tail-attribution part of E99; discard it as a post-E101 candidate ranker because E101 exposes a missing Q2/S3 boundary variable.
- public LB 관측 반응: already observed via E101. Future public files should not be selected by pre-E101 E99 broad order unless they test a explicitly different world.
- 제출 전략: no E124 submission. Keep E95 as frontier; same-line E89/E85/E90/E86 are not automatic successors.

### H119. E101 survivors are broad transfer-shrink worlds, not Q2/S3 diffuse-tail worlds

- 상태: supported; this weakens the E89/Q2S3 same-family continuation.
- 왜 그럴듯한가: E100 had found E89's main E95-beat pocket in `q2s3` tail worlds, and E101 was designed to isolate that pocket. If that worldview still survived E101, the E124 survivor set should be q2s3-enriched.
- 맞다면: E101-plausible worlds should have many `q2s3` mask scenarios, preserve E101's tail advantage over E95, and keep a high local-transfer alpha.
- 틀리다면: `q2s3` should have few or zero survivors; survivors should come from broad/all or high-hard-tail masks, with lower alpha and little E101-vs-E95 tail advantage.
- 최소 실험: `analysis_outputs/e125_e101_survivor_anatomy.py`, category/numeric/mask contrast of E124 E101-plausible worlds.
- 관측: `all`/`e72_top50_hard` masks are `43/57` survivors; `q2s3` has `0/368`; deterministic or `gamma=0` are `40/57`; median alpha collapses from `3.310470` to `0.791985`; median `tail_e101 - tail_e95` moves from `-0.000012634` to `~0`.
- 성공/폐기 기준: supported because the residual survivor world is broad transfer shrinkage, not Q2/S3 diffuse-tail. Discard only if a new independent S3-specific sensor later explains E101 while reviving q2s3 worlds without public fitting.
- public LB 관측 반응: already observed via E101. E125 says that the E101 public response should not be read as a cue to submit E89/full Q2S3 variants.
- 제출 전략: no E125 submission. Next candidate must leave same-line rollback or explain transfer-alpha collapse.

### H120. E101-compatible loss budget is mostly outside E101-active Q2/S3 cells

- 상태: supported; this closes the last cheap same-family rollback loophole.
- 왜 그럴듯한가: E125 rejected `q2s3` masks at scenario level, but broad/all survivors could still have spent their selected public-miss budget on E101-active Q2/S3 cells. If so, a more surgical E101-style gate might still be alive.
- 맞다면: E101-plausible worlds should allocate substantial budget mass to E101-active cells and q2s3 cells, with high E95-fallback share similar to broad-q2s3 worlds.
- 틀리다면: selected budget mass should be mostly outside E101-active cells, q2s3 share should be low, and the target/context composition should look broad/all-tail and transfer-shrink rather than Q2/S3 rollback.
- 최소 실험: `analysis_outputs/e126_e101_survivor_cell_budget_anatomy.py`, reconstructing E96/E124 selected cells and joining them to target, active-cell, fallback, hidden-block, and row-position metadata.
- 관측: E101-plausible worlds have q2s3 budget mass share `0.180513`, E101-active mass share `0.011234`, E95-fallback mass share `0.356179`, and between-train-runs mass share `0.621562`. Broad-q2s3 worlds have q2s3 share `1.000000` and E101-active share `0.584840`.
- 성공/폐기 기준: supported because public-compatible budget is not just a broad wrapper around the E101-changed cells. Discard only if a future independent public-free sensor finds a non-overfit S3-cell rule that explains E101 while also charging the E101-active cells.
- public LB 관측 반응: already observed via E101. E126 says the public response was not mainly about the 50 E101 moved cells; it was about a broader low-alpha tail surface.
- 제출 전략: no E126 submission. Do not submit E101/E89/Q2S3 same-line variants by default. Next candidate must predict transfer-shrinkage or test a different hidden structure.

### H121. Transfer-shrinkage field is visible as tail-neutral/low-alpha geometry, but not yet as a direct metadata gate

- 상태: partially supported; useful as a representation target and negative gate, not a submission generator.
- 왜 그럴듯한가: E126 implies that E101-compatible worlds are low-alpha and tail-neutral. If that is real rather than post-hoc, public-free scenario proxies should resemble the E101-compatible cell budget before a new probability move is made.
- 맞다면: `broad_tail_equal` or low-alpha proxy distributions should have low JS/TV distance to E101-compatible cell budget, while `q2s3` should remain far. Metadata views should recover some signal only when they include tail/fallback/E72 budget terms, not from target names alone.
- 틀리다면: all public-free proxies should look similarly weak, or a simple q2s3/target-only view should predict the field just as well.
- 최소 실험: `analysis_outputs/e127_transfer_shrinkage_field_predictability.py`, proxy distribution matching plus hidden-block-heldout category prediction.
- 관측: `broad_tail_equal` has JS `0.038002`, TV `0.173650`, Spearman `0.902053`, and top50 truth-mass capture `0.293969`; `broad_q2s3` has JS `0.508660` and Spearman `0.108504`. Best metadata view `target_context_tail_e72bin` has CV JS `0.073253` and top50 truth-mass capture `0.252521`; target-only has JS `0.316796`.
- 성공/폐기 기준: supports transfer-shrinkage as a public-free representation target. Discards the simpler claim that target/context metadata alone is enough to generate a submission.
- public LB 관측 반응: E101 already supplied the public sensor. E127 says future files should be filtered against tail-neutral/low-alpha density, not q2s3 or E101-active density.
- 제출 전략: no E127 submission. Build a transfer-shrinkage latent/gate and require it to clear selector-scale margin before any probability movement.

### H122. Transfer-shrinkage energy is a useful veto, not a standalone public selector

- 상태: partially supported as a risk decomposition; rejected as a direct submission ranker.
- 왜 그럴듯한가: E127's tail-neutral density aligns strongly with the E101-compatible budget field. If that energy is actionable, it should explain known public-anchor ordering and make live E85/E86/E89/E90/noQ2 risk differences explicit.
- 맞다면: active/Q2S3 rollback, tail-equal law residual, and E72-adverse exposure should correlate with known public deltas. A combined energy should not promote candidates that E124/E126 already mark as weak after E101.
- 틀리다면: those energy components should fail known-public sanity or collapse into an old same-family ranker that conflicts with post-E101 evidence.
- 최소 실험: `analysis_outputs/e128_transfer_shrinkage_energy_candidate_audit.py`, scoring known anchors and live candidates by E95-law alignment under tail-equal density, E101-active rollback, Q2/S3 rollback, E72-adverse exposure on E101-compatible density, and a combined risk index.
- 관측: individual metrics are strong: `q2s3_delta95_l1` Spearman with known public delta `0.958042`, `tail_equal_law_resid_ratio` `0.888112`, `e72_adverse_exposure_e101_plausible` `0.881119`, and `e101_active_delta95_l1` `0.874126`. The combined `transfer_shrinkage_risk_index` is much weaker at `0.440559`. It ranks live candidates E85/E89/noQ2/E90/E86, which conflicts with E124/E126's warning that same-family successors remain weak after E101.
- 성공/폐기 기준: support the component energies as veto/diagnostic features. Reject the compressed scalar ranker unless a future candidate also passes E124/E126-style public-world stress and creates selector-scale movement.
- public LB 관측 반응: E128 uses E95/E101/mixmin/E72/bad-anchor public observations only as sensors. It explains E101 as close-but-worse through active rollback, but does not justify a new public submission.
- 제출 전략: no E128 submission. Treat transfer-shrinkage energy as separate veto components, not a single score. A future file must be low on active/Q2S3 rollback and tail residual while also bringing independent upside evidence.

### H123. Existing submission universe does not hide a novel transfer-shrinkage-safe successor

- 상태: supported as a negative universe scan.
- 왜 그럴듯한가: E128's component vetoes are strong individually, but they were tested only on known anchors and five live candidates. A hidden old/local submission could satisfy the separated vetoes while avoiding the scalar-ranker failure.
- 맞다면: scanning the full local/documented submission universe should reveal at least one novel, material, low-veto candidate outside the E85/E86/E87/E89/E90/E95/E101/E108 hardtail family.
- 틀리다면: strict component gates should recover only E95/E101/E85-like same-family files, with no novel actionable survivors.
- 최소 실험: `analysis_outputs/e129_transfer_shrinkage_pareto_universe_audit.py`, deduplicated full local/report-referenced `submission*.csv` scan with strict separated veto gates.
- 관측: `116044` candidate paths produced `65865` unique prediction tensors. `gate_strict_veto` left `3` tensors, all same-family. `gate_strict_actionable` left only E85 and E101. `gate_strict_novel_actionable` was `0`; relaxed material survivors add only E89.
- 성공/폐기 기준: supported because even the very broad existing universe contains no novel low-veto material successor. Discard only if a future scan with a genuinely new representation family creates a non-same-family strict survivor.
- public LB 관측 반응: no new public submission. E129 explains why E128's veto components should not be turned into an old-file submit queue.
- 제출 전략: no E129 submission. Stop spending priority on existing-universe rank search; build new representation/movement that can satisfy the vetoes while producing selector-scale upside.

### H124. Tail-density fields can synthesize an E95 successor by local cell movement

- 상태: rejected as a direct synthesis rule; retained as a representation/veto target.
- 왜 그럴듯한가: E127 showed tail-neutral/low-alpha density predicts the E101-compatible budget field, and E129 showed old files do not contain a hidden successor. The next plausible step was to use the density field to create a new point near E95.
- 맞다면: E95-relative variants restricted to high-density cells should include at least one candidate that beats E95 locally, satisfies E128/E129 separated vetoes, and remains favorable under post-E101 sensor stress.
- 틀리다면: local-upside variants should systematically violate E72/E101 exposure gates, while veto-safe variants should be too small or non-strict.
- 최소 실험: `analysis_outputs/e130_tail_density_synthesis_probe.py`, moving E95 toward E86/E90/E89/E85/noQ2/mixmin under tail-equal, low-alpha, and density-score masks.
- 관측: `1792` variants were generated and `698` evaluated. `25` were local-strict against E95 and `19` were E129-veto-actionable before local strict, but their intersection was `0`; final submit-gate variants were `0`. Best local strict improvement was only `-0.000001512` and increased post-E101 sensor mean by about `+0.000003863`; best post-E101-safe micro-moves were `~1e-8` scale and not strict.
- 성공/폐기 기준: reject the direct density-shaped synthesis rule because local upside and transfer-shrinkage veto safety do not overlap. Retain the density as a LeJEPA-style health/veto signal.
- public LB 관측 반응: no public submission. A public test would be low-information because the local-stress-positive candidates are veto-adverse and the veto-safe candidates are immaterial.
- 제출 전략: no E130 submission. Future candidates need a new representation that disentangles "where density says public budget lives" from "where local probability movement produces safe upside."

### H125. Local-upside and veto-safe density atoms can be linearly recombined

- 왜 그럴듯한가: E130 found both ingredients separately: many local-strict E86/E90 low-alpha atoms and many E129-veto-safe mixmin/E85 atoms. A linear safe correction or hard-tail clipping might cancel the public-risk component while retaining local margin.
- 맞다면: E95-relative atom-combo candidates should contain at least one row that is local-strict, transfer-veto-actionable, and non-adverse under post-E101 sensor stress.
- 틀리다면: local-strict rows and veto-actionable rows should remain disjoint; risk-clipped local rows should either lose veto actionability or remain post-E101 adverse.
- 최소 실험: `analysis_outputs/e131_tail_density_atom_combo_probe.py`, combining E130 local atoms with E130 safe atoms in logit space and clipping hard-tail-risk cells from local atoms.
- 관측: `6384` candidate rows, `700` evaluated, `651` local-strict, and `208` veto-actionable, but `0` local-strict plus veto-actionable rows and `0` submit-gate rows. The best local row improved E95 by `-0.000001813` but stayed post-E101 adverse; no evaluated row had negative post-E101 sensor mean.
- 성공/폐기 기준: reject the linear recombination hypothesis. The disjointness is structural under the tested donor/mask family, not just missing blend weights.
- public LB 관측 반응: no submission. Any public test from this family would either test an already-rejected local-risk direction or an immaterial safe movement.
- 제출 전략: no E131 submission. Future work should stop treating transfer-shrinkage as a corrective blend over old directions and instead search for a new latent/movement direction that is safe before correction.

### H126. The E95 combo-set gradient contains a transfer-veto-safe tangent component

- 상태: rejected for the current gradient/mask family.
- 왜 그럴듯한가: E130/E131 could have failed because old donor directions were contaminated. A donor-free gradient computed directly at E95 might point toward local public-like combo improvement while still allowing masks to remove transfer-shrinkage risk.
- 맞다면: some E95 gradient-nullspace movement should be local-strict, E128/E129 veto-actionable, and favorable under post-E101 sensor stress.
- 틀리다면: local-improving gradient rows and transfer-veto-actionable rows should remain disjoint, or local-improving rows should fail hidden/block/Q2S3/world support while safe rows fail local strictness.
- 최소 실험: `analysis_outputs/e132_veto_nullspace_gradient_probe.py`, direct E95 combo gradient movement under all/LOO/single combo contexts and transfer-veto masks.
- 관측: `4590` gradient candidates produced `0` gradient local-strict rows, `843` veto-actionable rows, `0` local-strict plus veto-actionable rows, and `0` submit-gate rows. The strongest local row improved E95 local stress by `-0.000112772` but failed strict hidden/block support and had positive post-E101 p95 exposure; the strongest post-E101 sensor rows improved sensor mean but failed local strict structure.
- 성공/폐기 기준: reject the donor-free gradient tangent as a submission source. Revive only if a future gradient target is learned from a different structural latent and proves strict local support before vetoing.
- public LB 관측 반응: no public submission. A public test would be low-information because no candidate satisfies both local structure and transfer-veto safety.
- 제출 전략: no E132 submission. The next strategy is not another E95-neighborhood tangent move; it is a new latent target where local upside and tail safety are co-located before probability translation.

### H127. Visible metadata can recover the co-located local-safety field

- 상태: rejected as a direct latent target; retained as an atlas.
- 왜 그럴듯한가: E133's desired object is no longer a probability movement but a cell field where E95 local gradient reward, veto-null direction, low hard-tail adverse exposure, and transfer-shrinkage density overlap. If this field is visible through subject/target/context/block metadata, it could become a new JEPA-style target.
- 맞다면: a hidden-block-heldout categorical view should capture a material share of top co-located cells, and local reward mass inside safe density should be broad enough to support a probability movement.
- 틀리다면: local reward should mostly lie outside safe density, co-located top cells should shift target family relative to local top cells, and metadata CV should capture only weak top-cell mass.
- 최소 실험: `analysis_outputs/e133_local_safety_colocation_atlas.py`, cell-level atlas over E95 combo gradients, transfer-safe density, and hidden-block-CV categorical predictors.
- 관측: best context `all_sign` has only `0.161830` local reward mass in veto-null+density70. Its local top50 are `44%` Q2/S3 and `42%` S3, but co-located top50 are `2%` Q2/S3, `0%` E101-active, `40%` Q3, and `34%` Q1. Best category CV is `subject_target` with JS `0.240700` and top50 truth-mass capture `0.048280`.
- 성공/폐기 기준: reject simple metadata as a direct target generator. Keep the atlas because it identifies the target-family shift from Q2/S3 local reward to Q3/Q1 safe remainder.
- public LB 관측 반응: no submission. A public test is premature because E133 has not produced a probability movement or a selector-scale latent predictor.
- 제출 전략: none. Future work should test raw/run/block-context representations for the Q3/Q1-heavy co-located pocket rather than another Q2/S3 or metadata-only gate.

### H128. Raw/run/block context can recover the Q3/Q1-heavy safe remainder

- 상태: weakly supported as diagnostic signal, rejected as direct selector-scale target.
- 왜 그럴듯한가: E54 showed raw overnight context can recover strict pseudo-hidden block state, and E133 said the next target is no longer Q2/S3 local reward but a Q3/Q1-heavy co-located safe-remainder field.
- 맞다면: hidden-block-heldout raw/block embeddings or raw block kNN should materially beat metadata, capture a large share of the E133 co-located top cells, and keep Q2/S3 suppressed.
- 틀리다면: raw/block predictors should only weakly beat metadata or mostly reproduce target priors, leaving top-cell mass far below a reliable selector threshold.
- 최소 실험: `analysis_outputs/e134_raw_block_colocation_predictability.py`, predicting `all_sign_co_vetonull_density` with target/metadata ridge, raw overnight block embeddings, and target-wise raw block kNN under hidden-block holdout.
- 관측: best raw/block predictor `night_all_blockknn` captures top50 truth mass `0.073497` with cosine `0.498528` and JS `0.260922`. Best metadata-only predictor captures `0.063040`. The best top50 has `Q1:37,Q3:4,S4:9` and Q2/S3 fraction `0`.
- 성공/폐기 기준: reject as a direct latent selector because the improvement over metadata is small and top50 mass remains far from material recovery. Retain only as a weak energy that confirms Q2/S3 suppression.
- public LB 관측 반응: no submission. Any file made directly from E134 would test a weak raw-context ranking, not a credible public-improvement hypothesis.
- 제출 전략: none. Future work should either change the target representation or find an independent larger movement; raw overnight block kNN alone is not enough.

### H129. Existing prediction manifold can recover the Q3/Q1-heavy safe remainder

- 상태: rejected as a direct latent selector; retained only as a weak Q2/S3-suppression diagnostic.
- 왜 그럴듯한가: if the E133 safe remainder is a structure already exploited by some old submissions, then row-level prediction PCA, per-cell disagreement, uncertainty, or old-submission scalar fields should expose it better than raw/block context.
- 맞다면: prediction-manifold features should materially beat metadata and E134 raw/block recovery under hidden-block holdout, with a concentrated top-cell set that can become a gate.
- 틀리다면: prediction-manifold features should collapse to metadata-level recovery, mostly reflect target priors, or fail to beat raw/block visibility.
- 최소 실험: `analysis_outputs/e135_prediction_manifold_remainder_visibility.py`, using `12` known submission tensors to predict E133's `all_sign_co_vetonull_density` teacher over `1750` cells and `36` hidden blocks.
- 관측: best prediction-manifold result is `row_prediction_pca_meta` / `ridge` with top50 truth-mass capture `0.063430`, cosine `0.531360`, and JS `0.251301`. Best metadata-only is `0.063040`, and the E134 raw/block reference is higher at `0.073497`. The top50 remains Q3/Q1-heavy and Q2/S3-suppressed, but not selector-scale.
- 성공/폐기 기준: reject as a direct selector because it does not materially improve over metadata and is worse than E134 raw/block context. Retain only as evidence that old predictions agree with suppressing Q2/S3.
- public LB 관측 반응: no submission. A public file from E135 would be a weak old-manifold ranking, not a new hidden-world hypothesis.
- 제출 전략: none. The next branch must redefine the latent target or introduce independent supervision; do not build a submission by blending old predictions according to E135 visibility.

### H130. The safe remainder is visible only after block-target compression

- 상태: supported as the next live representation branch; not yet a submission strategy.
- 왜 그럴듯한가: E133/E134/E135 tried to recover sparse row-target cells. If the hidden data-generating law is block/run-level, the correct JEPA target is a block-target state, not individual cells.
- 맞다면: aggregating the same teacher by hidden block and target should improve hidden-block-heldout top-mass recovery beyond cell-level E134/E135 references, especially with raw block context. Row-total compression should be weaker if the target identity still matters.
- 틀리다면: block-target, block-family, and block-total representations should remain at or below the cell-level enrichment references, or only metadata should explain them through trivial target priors.
- 최소 실험: `analysis_outputs/e136_target_compression_visibility_audit.py`, aggregating `all_sign_co_vetonull_density` into row-total, block-target, block-family, and block-total units, then predicting each with metadata, raw views, old-prediction geometry, and raw+prediction features under hidden-block holdout.
- 관측: best compressed result is `block_target` / `all_raw_views_raw_pred` / `ridge` with top10 truth-mass `0.332698`, enrichment `3.326980`, and oracle top10 capture ratio `0.709652`. `night_all_raw` block-target alone reaches enrichment `3.236095`. Cell-level references are E134 `2.572395` and E135 `2.220050`. Row-total stays weak at `1.181643`.
- 성공/폐기 기준: keep the branch because block-target compression materially improves visibility. It still fails as a submission strategy until a probability movement from this compressed state passes E128/E129/E124-style tail and transfer stress.
- public LB 관측 반응: no public submission yet. A later block-target-state candidate should improve only if compressed state can be translated into calibrated cell movement without reviving Q2/S3/E101 exposure.
- 제출 전략: none now. Next experiment should test whether E136 top block-target states provide a safe movement direction or merely explain where the teacher mass aggregates.

### H131. E136 block-target state can make the current E95 gradient safe

- 상태: rejected for the current translator; H130 remains live.
- 왜 그럴듯한가: E136's compressed state captures where safe mass lives. If E132 failed mainly because it selected cells poorly, using E136 state masks should align the donor-free E95 gradient with local upside and transfer safety.
- 맞다면: block-target gated gradient variants should produce at least some local-strict and transfer-veto-actionable overlap, with post-E101 p95 nonpositive and a material E95-relative local gain.
- 틀리다면: local mean gains may appear, but strict structural gates and transfer-veto gates should remain empty, or post-E101 p95/tail exposure should stay adverse.
- 최소 실험: `analysis_outputs/e137_blocktarget_state_movement_probe.py`, using E136 predicted block-target state as hard/soft masks over E95 combo gradients across contexts, target scopes, shapes, and scales.
- 관측: `1980` block-target gradient variants and `698` evaluated variants produced `0` local strict, `0` transfer-veto-actionable, `0` local-and-veto, and `0` submit-gate candidates. Best local delta vs E95 is `-0.000043592`, and best post-E101 mean vs E95 is `-0.000040388`, but p95 stays positive (`0.000026205`), tail-equal law cosine is only about `0.66-0.70`, and E72 exposure is elevated.
- 성공/폐기 기준: reject the current translator because visibility does not become safe movement. Keep the state representation if a future translator learns direction/amplitude rather than multiplying the old gradient.
- public LB 관측 반응: no submission. A file from E137 would bet on mean local/post-E101 improvement while ignoring strict and transfer-veto failures, which is exactly the failure mode E95/E101 exposed.
- 제출 전략: none. Next branch should build a block-target-state direction model or hardtail-support translator, not another E95 gradient mask.

### H132. Block-target state becomes usable when intersected with transfer-safe veto-null masks

- 상태: rejected as sufficient; H130 remains live.
- 왜 그럴듯한가: E137 may have failed because it used E136 state without forcing transfer-shrinkage safety. E132 separately found many veto-actionable rows. If the missing structure is simply the overlap between those two maps, intersecting state and veto masks should create safe candidate movement.
- 맞다면: overlap variants should contain at least some local-strict plus transfer-veto-actionable rows, post-E101 p95 should be nonpositive, and the best candidates should preserve all-set tail neutrality and world/raw hidden structure.
- 틀리다면: overlap rows can improve local mean and transfer sensors, but strict all-set/tail/world/raw health remains broken and submit gates stay empty.
- 최소 실험: `analysis_outputs/e138_blocktarget_vetonull_overlap_probe.py`, intersecting E136 block-target state with veto-null / low-adverse masks under `all` and `raw05_compatible` gradient contexts.
- 관측: `1314` overlap variants and `698` evaluated variants produced `0` local strict rows, `373` transfer-veto-actionable rows, `0` local-strict plus transfer-veto-actionable rows, and `0` submit-gate rows. The best evaluated row improved local all by `-0.000030467` and post-E101 mean/p95 by `-0.000055772` / `-0.000015691`, but only `2/3` combo sets beat base, only `1/3` tails were neutral, hidden Q2/S3 was `+0.000084793`, and world support was `+0.001092051`.
- 성공/폐기 기준: reject simple state-veto overlap as a movement generator. It succeeds only as a diagnostic showing that transfer-veto safety can be found without restoring the full structural law.
- public LB 관측 반응: no submission. A file from E138 would chase favorable mean/post-E101 sensors while ignoring the exact strict-tail failure that E95/E101 exposed.
- 제출 전략: none. The next strategy must learn or construct a decoder that directly optimizes all-set tail neutrality and world/raw structure inside the block-target state, not multiply more masks onto the current gradient.

### H133. Combo-set sign consensus is the missing block-target decoder constraint

- 상태: rejected as sufficient; H130 remains live and narrower.
- 왜 그럴듯한가: E138's best rows failed some combo-set and tail criteria. If the current gradient was mostly right but internally conflicted across `inverse_top`, `raw05_compatible`, and `all_sign`, keeping only agreement cells should remove the unstable part.
- 맞다면: all-three or pairwise consensus decoders should produce at least some local-strict plus transfer-veto-actionable rows, and all-three rows with `3/3` combo-set wins should also improve tail/world/raw health.
- 틀리다면: combo-set mean wins may improve, but tail-neutral, world-nonworse, and raw-energy-nonworse gates should remain closed.
- 최소 실험: `analysis_outputs/e139_blocktarget_set_consensus_decoder_probe.py`, building `all3_min`, `all3_mean`, and pairwise min decoders before intersecting E136 state and E138 safety masks.
- 관측: `1188` variants and `698` evaluated rows produced `0` local strict, `190` transfer-veto-actionable, `0` local-and-veto, and `0` submit-gate rows. All evaluated rows passed all-margin and all-beats-base, but tail-neutral, world-nonworse, and raw-energy-nonworse each failed for `698/698` rows. The best all-three consensus rows reached `3/3` combo-set wins but only `1/3` tail-neutral sets.
- 성공/폐기 기준: reject combo-set sign consensus as the missing decoder. It solves mean-direction disagreement only, not the LogLoss tail/world law.
- public LB 관측 반응: no submission. A file from E139 would bet on local combo-set means while violating the same tail/world/raw constraints that explain the E101 near-miss.
- 제출 전략: none. The next decoder must be trained or constructed with tail-neutral/world/raw constraints as primitive objectives, not added as post-hoc masks or sign filters.

### H134. Tail/world-aware single-cell primitives can accumulate into a safe decoder

- 상태: rejected as sufficient; H130 remains live and now points at combo-set worst-tail balancing.
- 왜 그럴듯한가: E139 may have failed because it optimized mean combo gradients first and checked tail/world/raw later. If the decoder instead starts from single-cell directions that already satisfy local reward plus tail/world/raw nonworsening, accumulation might preserve the full law.
- 맞다면: support cells should contain many strict primitives, and top-k combinations should contain at least some local-strict plus transfer-veto-actionable rows with all-set tail neutrality.
- 틀리다면: primitive cells may satisfy world/raw and local reward, but accumulated movements should still fail exact combo-set worst-tail neutrality.
- 최소 실험: `analysis_outputs/e140_tailworld_primitive_decoder_probe.py`, evaluating both directions for every visible block-target/veto support cell, then combining tolerant primitive pools.
- 관측: `471` support cells and `942` micro rows produced `373` local-reward primitives, `119` tail/world/local primitives, and only `3` tolerance-level strict primitives with negligible reward. Combined variants `168` produced `0` local strict, `0` transfer-veto-actionable, and `0` submit-gate rows. All combined rows passed hidden-core/world/raw checks, but all `168/168` failed all-set tail neutrality and max tail-neutral count stayed `1/3`.
- 성공/폐기 기준: reject primitive tail/world awareness as sufficient. It fixes world/raw geometry but not combo-set worst-tail geometry.
- public LB 관측 반응: no submission. A file from E140 would still bet against the exact tail law that distinguished E95/E101.
- 제출 전략: none. The next strategy should explicitly decompose and balance the failing combo-set tail axes rather than broaden primitive selection.

### H135. E140's blocker is exact combo-tail failure rather than transfer-tail budget

- 상태: rejected; H130 is narrowed to transfer-tail budget.
- 왜 그럴듯한가: E140 reported all `168` combined rows failing all-set tail neutrality, so the obvious remaining blocker looked like combo-set worst-tail balancing.
- 맞다면: applying a small numerical tolerance to worst-tail deltas should still leave few or no relaxed structural survivors, or the relaxed survivors should become actionable once exact-zero artifacts are removed.
- 틀리다면: relaxed structural survivors should open, but E72-plausible exposure, transfer-veto, or post-E101 p95 should remain closed.
- 최소 실험: `analysis_outputs/e141_tail_tolerance_transfer_audit.py`, re-scoring E140 rows under tail tolerances and E95-relative transfer thresholds.
- 관측: at tolerance `1e-12`, tail pass rises to `129` and relaxed structural pass to `84`, but relaxed plus E72 exposure pass is `0`, relaxed plus post-E101 p95 pass is `0`, and relaxed actionable remains `0`. The minimum relaxed E72 gap is `+0.000003189534`; best relaxed p95 is still `+0.000000141478`.
- 성공/폐기 기준: reject exact combo-tail failure as the primary blocker. Keep combo-tail tolerance in the validator, but do not claim it creates a file.
- public LB 관측 반응: no submission. A file from relaxed E140 would be betting on tiny local reward while still exceeding the E95 transfer-tail budget.
- 제출 전략: none. The next strategy should explicitly minimize E72-plausible exposure and post-E101 p95 while preserving relaxed structural reward.

### H136. E140 relaxed structural rows are almost-correct moves contaminated by high E72-exposure cells

- 상태: supported locally; superseded by H137 as first submission; public pending.
- 왜 그럴듯한가: E141 opened relaxed structural rows but found E72-plausible exposure and post-E101 p95 as the remaining blockers. If the blockers are localized rather than global, rolling back high-excess cells should keep much of the local reward.
- 맞다면: clipped variants should preserve relaxed structural gates while making E72-plausible exposure no worse than E95 and post-E101 p95 nonpositive. The selected movement should not simply collapse back to E95.
- 틀리다면: clipping should either kill local all-minus-E95 reward, fail relaxed structural gates, or still leave E72/post-E101 positive.
- 최소 실험: `analysis_outputs/e142_transfer_budget_clipped_decoder_probe.py`, using E140 relaxed material parents and rolling back cells ranked by excess E72-plausible exposure.
- 관측: E142 generated `1844` variants from `11` parents. `670` remained relaxed structural, `35` passed E72 budget, all `35` also passed post-E101, and `35` passed submit-relaxed. The materialized file `submission_e142_transferclip_09a92236.csv` keeps `185` E95-relative changed cells, no Q2 movement, all-minus-E95 `-0.000010666782`, E72 gap `~0`, and post-E101 p95 `-0.000003762343`.
- 성공/폐기 기준: locally supported because it opened a candidate. Public LB will decide whether the E101-conditioned transfer-tail gate generalizes or overfits public sensors.
- public LB 관측 반응: if better than `0.5762913298`, strengthen H136 and H130's transfer-budget decoder view. If worse, reject simple excess-exposure clipping and treat post-E101/E72 gates as overconditioned diagnostics rather than selectors.
- 제출 전략: keep `analysis_outputs/submission_e142_transferclip_09a92236.csv` as the higher-upside fallback sensor after H137's active/Q2S3 repair.

### H137. E142's active/Q2S3 veto failure is repairable without killing the residual decoder

- 상태: supported locally; superseded by H138 as first submission; public pending.
- 왜 그럴듯한가: E101 public `0.5763003660` showed that Q2/S3 rollback was close but not frontier. E142 opens a broader residual decoder, but still fails the legacy active/Q2S3 gate. If the E101 lesson is a local overconditioning warning rather than a rejection of all residual movement, a small rollback on the most Q2/S3-weighted active cells should make E142 stricter without collapsing it to E95.
- 맞다면: E142-derived repairs should pass `gate_active_q2s3_not_more_than_e101`, original strict actionability, relaxed structural, E72-budget, and post-E101 p95 simultaneously, with local all-minus-E95 still around `1e-5`.
- 틀리다면: repairing active/Q2S3 should either destroy local reward, fail E72/post-E101 transfer gates, or leave strict actionability closed.
- 최소 실험: `analysis_outputs/e143_e142_active_q2s3_veto_repair.py`, rolling back E142-minus-E95 movement on E101-active/Q2S3/S3 masks and ranked tension masks.
- 관측: E143 generated `80` repair variants. All `80` remained relaxed-submit, and `15` passed original strict-submit. The selected `submission_e143_activeq2s3repair_68ca656f.csv` rolls back `21` top Q2/S3-weighted cells, keeps `164` changed cells, has local all-minus-E95 `-0.000009551358`, E72 gap `~0`, post-E101 p95 `-0.000003368915`, and passes active/Q2S3 and strict actionability.
- 성공/폐기 기준: locally supported. Public LB decides whether the stricter Q2/S3 repair is the correct next sensor or whether the old active/Q2S3 veto is overconservative.
- public LB 관측 반응: if E143 beats `0.5762913298`, strengthen the residual-decoder world and treat E101 as an active/Q2S3 pruning constraint. If E143 loses but E142 later wins, weaken the active/Q2S3 veto. If both lose, reject E101-conditioned transfer-budget clipping as a selector.
- 제출 전략: keep `analysis_outputs/submission_e143_activeq2s3repair_68ca656f.csv` as the conservative fallback after H138's finer boundary candidate.

### H138. E143's active/Q2S3 repair boundary is fine, not binary

- 상태: supported locally; public pending.
- 왜 그럴듯한가: E143 proved that the E142 residual decoder can survive the E101 active/Q2S3 lesson, but it used coarse masks and keep factors. If the real public-tail boundary is a small LogLoss cliff, full rollback of exactly `21` cells may be a conservative quantization artifact rather than the best sensor.
- 맞다면: a fine scan around E143 should find original-strict rows that retain slightly more E142 movement, beat E143 locally, and do not worsen post-E101 p95.
- 틀리다면: every row that beats E143 locally should fail original strict actionability, active/Q2S3, E72-budget, or post-E101 p95.
- 최소 실험: `analysis_outputs/e144_e143_active_boundary_refine.py`, sweeping top counts `14..24` and keep factors around E143 on Q2/S3-weighted, tension, and E101-active masks.
- 관측: E144 generated `206` repair variants, `32` original-strict variants, and `9` E144-submit variants. The selected `submission_e144_activeboundary_d7b4b331.csv` uses `top_q2s3_weighted_24`, keep factor `0.15`, rolls back `24` cells, keeps `185` changed cells, has local all-minus-E95 `-0.000009725930`, post-E101 p95 `-0.000003430489`, E72 gap `~0`, and passes active/Q2S3 plus strict actionability.
- 성공/폐기 기준: locally supported. Public LB decides whether E144's finer retained movement is real or whether E143's more conservative full rollback is safer.
- public LB 관측 반응: if E144 beats `0.5762913298`, strengthen the fine-boundary version of the residual-decoder world. If E144 loses but E143 wins, the retained `0.15` active tail was too optimistic. If E144, E143, and E142 all lose, reject this E101-conditioned transfer-budget branch as a selector.
- 제출 전략: submit `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` before E143; keep E143 as conservative fallback.

### H139. E144 public feedback must be decoded before same-family followups

- 상태: decoder registered; waiting for public observation.
- 왜 그럴듯한가: E144's local advantage over E143 is only `~1.75e-7`, while prior public observations moved by `1e-5` to `1e-3`. The next public score can easily be misread unless the branch rules are fixed in advance.
- 맞다면: E144 public LB can be mapped to stable actions: wins promote E144; a small loss no worse than E101 keeps E143 as a boundary contrast; worse-than-E101 blocks automatic E143/E142 rescue; worse-than-mixmin closes the branch.
- 틀리다면: the bands will be too coarse to guide action, or the next public result will require a hidden condition not represented by E95/E101/mixmin anchors.
- 최소 실험: `analysis_outputs/e145_e144_public_feedback_decoder.py`, mapping future E144 LB into seven pre-registered bands relative to E95, E101, and mixmin.
- 관측: E145 defines `breakthrough_win <=0.576271330`, `clean_win <=0.576284330`, `micro_win <=0.576289330`, `tie <=0.576293330`, `fine_loss_branch_alive <=0.576300366`, `branch_loss <=0.576306641`, and `hard_fail >0.576306641`.
- 성공/폐기 기준: public feedback must be interpreted through this decoder before any E143/E142 or new boundary followup. If the decoder gives no actionable branch, mark the active-boundary worldview underidentified rather than forcing a next file.
- public LB 관측 반응: E144 win strengthens H138. E144 fine-loss but no worse than E101 permits E143 as the clean contrast. Worse than E101 weakens H138 enough to block automatic same-family rescue. Worse than mixmin rejects the E142/E143/E144 transfer-budget branch.
- 제출 전략: no E145 submission. Consult `analysis_outputs/e145_e144_public_feedback_decoder.csv` immediately after E144 LB arrives.

### H140. E144's retained S3 tail is public-free prior-supported, not only local-gate supported

- 상태: locally supported; public pending.
- 왜 그럴듯한가: E144's advantage over E143 is only `~1.75e-7` locally. If the 24 retained cells are random strict-gate arithmetic, visible global/subject/flank priors should not systematically prefer E144 over E143.
- 맞다면: E144-vs-E143 differing cells should be concentrated in a coherent target/tail state, and public-free priors should expect E144-minus-E143 LogLoss deltas to be negative.
- 틀리다면: priors should split signs, prefer E143, or show the edge comes from unsupported high-conflict cells.
- 최소 실험: `analysis_outputs/e146_e144_e143_tail_prior_audit.py`, isolating only E144-vs-E143 differing cells and scoring hard-label deltas under global, subject, and train-flank priors.
- 관측: E144 differs from E143 in `24` cells, all `S3`, across `24` rows and `4` subjects. `21` cells move away from E95 versus E143 and `3` move toward E95. Flank-conflict cells are `0`. All `10/10` public-free priors prefer E144 over E143. Expected E144-minus-E143 deltas range from `-0.000010294767` under nearest-hard to `-0.000001097289` under subject prior. Simulated E144 beat probability ranges from `0.540545` to `0.925720`.
- 성공/폐기 기준: support H140 as a pre-public interpretation layer. Public LB can still kill the retained-tail movement, but if it does, the failure is hidden public S3-tail adversity rather than lack of public-free prior support.
- public LB 관측 반응: E144 win strengthens H138 and H140 together. E144 narrow loss weakens public transfer of visible S3 priors and makes E143 only a deliberate contrast on tail retention, not an expectation-ranked rescue. E144 worse than E101 still blocks automatic same-family rescue as H139 specified.
- 제출 전략: no E146 submission. Keep `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the next single file.

### H141. E144's whole E95-relative movement is visible-prior supported, with S3/Q3 as the stress axis

- 상태: locally supported; public pending.
- 왜 그럴듯한가: E146 validated only the 24-cell E144-over-E143 fine tail. A real next submission candidate must also make sense as a whole against E95, because public LB will score all 185 moved cells, not just the fine-tail delta.
- 맞다면: global, subject, and flank priors should prefer E144 over E95 on the full moved-cell set; most expected benefit should come from the inherited E143 body rather than the tiny E144-only delta; any adverse pockets should be target/component-specific enough to guide interpretation.
- 틀리다면: visible priors would split signs or prefer E95 globally, especially if E144 were only a local-gate artifact.
- 최소 실험: `analysis_outputs/e147_e144_e95_prior_world_audit.py`, scoring all E144-vs-E95 moved cells under global, subject, prev/next/nearest/both-flank, hard-nearest, edge-endpoint, and conflict-flat priors, then simulating E144-vs-E95 outcomes.
- 관측: E144 moves `185` cells across `108` rows and `9` subjects: Q3 `56`, S3 `47`, Q1 `38`, S2 `23`, S4 `21`, Q2/S1 `0`. All `10/10` public-free priors prefer E144 over E95. Expected deltas range from `-0.000049865515` to `-0.000012197928`, and simulated beat probability ranges from `0.583850` to `0.762700`. The inherited E143 body is favorable under nearest-hard (`-0.000024556352`), while the E144 fine-tail delta is mildly adverse there (`+0.000002882583`). Target stress is favorable on Q1/S4/S2 and adverse on S3/Q3 under nearest-hard.
- 성공/폐기 기준: support H141 as the pre-public whole-file interpretation layer. Public LB can still kill the branch, but a loss should first be localized to S3/Q3 or fine-tail/body components before broad family rollback.
- public LB 관측 반응: E144 win strengthens the E95-plus-transfer-budget-neutral residual worldview. E144 tie or fine loss means the visible-prior support was not enough on public's hidden S3/Q3 mix; consult H139 bands and E147 decomposition before selecting E143/E142. E144 worse than E101/mixmin weakens the entire E142/E143/E144 selector branch.
- 제출 전략: submit `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the next single file; do not create another file from E147 itself.

### H142. E144 public feedback can be pre-attributed by target/component worlds

- 상태: attribution decoder registered; public pending.
- 왜 그럴듯한가: E145 gives score bands, and E147 gives target/component priors, but public feedback will still be underidentified unless the possible bands are mapped to the hidden support patterns that make them happen.
- 맞다면: simulated label-worlds under visible priors should show distinct target/component responsibility for wins, fine losses, branch losses, and hard fails. In particular, a fine loss should not automatically imply the E144-only fine tail failed.
- 틀리다면: all outcomes would have similar target/component attribution, making post-public interpretation mostly arbitrary.
- 최소 실험: `analysis_outputs/e148_e144_public_outcome_attribution.py`, sampling `250000` label-worlds per prior over E147 cells and assigning each world to the E145 outcome bands.
- 관측: global/subject/nearest-hard win-rate masses are `0.745560` / `0.599760` / `0.635616`; branch-or-worse masses are `0.204972` / `0.333832` / `0.284852`. Fine-loss-alive is rare (`0.027696..0.033340`) and is not consistently a fine-tail-only event. Nearest-hard losses blame S3/Q3, global losses blame inherited-body/Q3/S2, and subject losses blame inherited-body/Q3/S3.
- 성공/폐기 기준: support H142 as a pre-public interpretation layer. After E144 feedback, use E145 for banding and E148 for attribution before any same-family followup.
- public LB 관측 반응: an E144 win should be credited to the target/component groups that carry negative conditional delta in the relevant band. A fine loss allows E143 only if attribution points to fine-tail/S3 retention. Branch loss or hard fail requires checking whether inherited-body and broad target slices failed before closing or rescuing the branch.
- 제출 전략: no E148 submission. Keep E144 as next file; freeze the interpretation rule.

### H143. E144 is a branch-pruned residual sensor, not a new broad successor law

- 상태: supported by anchor-geometry audit; public pending.
- 왜 그럴듯한가: E144 inherits almost all of E143/E142 movement, and E147/E148 did not tell whether the resulting file occupies a new latent direction or only a safer point on the same branch.
- 맞다면: E144 should be close to E142/E143 branch axes, mostly detached from known public-negative E72/E101 axes, and its fine E144-vs-E143 correction should be small relative to the inherited branch body.
- 틀리다면: E144 would have low cosine with E142/E143 branch axes, high independent alignment with the public-positive hardtail axis, or a large residual direction not explained by prior branch geometry.
- 최소 실험: `analysis_outputs/e149_e144_anchor_geometry_audit.py`, comparing logit deltas against E95 for mixmin, E72, E101, E142, E143, and E144, then measuring cosine/projection/residual ratios and target shares.
- 관측: E144 cosine with E143 branch axis is `0.991918719`, with E142 branch axis `0.952146833`, with E101 loss axis `-0.019625796`, and with E72 fail axis `-0.024358970`. Residual ratio is `0.126874959` versus E143 and `0.305640978` versus E142. E144 Q2/S3 share is only `0.161603888`, while E101 is `1.000000000`.
- 성공/폐기 기준: support H143 as a pre-public geometry layer. Public LB can still validate or reject the branch, but E144 should no longer be described as a broad representation breakthrough.
- public LB 관측 반응: E144 win strengthens the E142/E143 transfer-budget residual branch and the fine-boundary pruning. E144 loss weakens that branch; only a target/component read consistent with fine-tail/S3 failure should promote E143 as a contrast.
- 제출 전략: keep `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the next single file. Do not create a new geometry-derived submission from E149.

### H144. E144 post-feedback action must be decided by band plus attribution plus geometry

- 상태: decision contract registered; public pending.
- 왜 그럴듯한가: E145 bands alone are underidentified. E148 shows the same fine-loss band can be caused by fine-tail/S3, inherited-body, Q3/S2, or broad target-body shortfall, and E149 shows E144 is mostly E143 branch geometry.
- 맞다면: a single post-feedback interpreter should block mechanical same-family rescue and classify an observed E144 score into a constrained action.
- 틀리다면: E145 banding alone would be enough, and E143 would be justified whenever E144 lands in `fine_loss_branch_alive`.
- 최소 실험: `analysis_outputs/e150_e144_postfeedback_interpreter.py`, joining E145 bands, E148 attribution, and E149 geometry, with optional `--score <PUBLIC_LB>` classification.
- 관측: E150 generates `7` rows. `fine_loss_branch_alive` is `conditional_alive`, E143 is allowed only if attribution points to fine-tail/S3 retention, `branch_loss` blocks E143/E142 automatic rescue, and `hard_fail` closes the local boundary branch.
- 성공/폐기 기준: support H144 until actual E144 public feedback arrives. If the score is supplied, the interpreter must produce exactly one band and one allowed action.
- public LB 관측 반응: after E144 public feedback, run E150 first. A win promotes E144 but not broad breakthrough claims. A fine loss requires attribution before E143. Worse than E101 blocks same-family rescue. Worse than mixmin closes E142/E143/E144.
- 제출 전략: no E150 submission. It is the mandatory post-E144 decision gate.

### H145. The 0.5762913298 plateau is a selector-resolution and decoder bottleneck, not mainly missed old candidates

- 상태: supported by E151; public E144 still pending.
- 왜 그럴듯한가: E95's public edge over mixmin is only `0.0000153107`, E101's resolved loss is `0.0000090362`, and E144 is an even smaller E143-collinear branch refinement. Existing selector/proxy errors are much larger than these effects, while representation probes repeatedly find either local reward or tail safety but not submit-safe overlap.
- 맞다면: old submission universe search should have no novel strict successor; known-LB selector p90 should be far above the frontier edge; E130-E139 decoder families should fail submit gates; only E142/E143/E144-like hand-clipped branch candidates should survive.
- 틀리다면: either an old/non-same-family candidate should pass E129/E120/E149-style stress, or an ordinary validation selector should rank E95/E101/E144 with sub-`5e-6` error, or a broad model/decoder should pass strict/E72/post101 p95 gates without E143 collinearity.
- 최소 실험: `analysis_outputs/e151_plateau_resolution_bottleneck_audit.py`, joining E98, E120, and E129-E150 evidence.
- 관측: best known-LB selector p90 `0.0008164966` is `53.33x` the E95 edge; E101 actual-minus-local-mean optimism `0.0000252415` is `1.65x` the E95 edge; E129 strict novel actionable `0`; E130/E131/E132/E137/E138/E139 `submit_gate=0`; live branch counts are E142 `35`, E143 `15`, E144 `9`; E144 cosine with E143 `0.991918719`.
- 성공/폐기 기준: support H145 until a non-collinear decoder clears strict/E72/post101 p95 gates with local edge above `1e-5`, or a new validation object resolves E95/E101/E144 below `5e-6`.
- public LB 관측 반응: E144 remains the smallest public kill test. Win validates the narrow branch, not a broad representation breakthrough. Loss strengthens the decoder-overfit interpretation unless attribution isolates fine-tail/S3.
- 제출 전략: no E151 submission. Submit E144 first if using a slot; otherwise build an independent transfer-budget-neutral decoder rather than resweeping old blends.

### H146. Non-collinear signal exists, but current decoder gates are mutually incompatible

- 상태: supported by E152; no submission.
- 왜 그럴듯한가: E151 left a possible escape hatch: existing E137-E140 decoder rows might contain non-collinear signal that only needed projection away from E144. If true, branch orthogonalization should open strict/E72/post101/actionable candidates.
- 맞다면: E137-E140 source moves should have large residual ratios versus E144, but projected probability moves should split across incompatible gates: local/relaxed reward, E72 budget, post-E101 p95, and active-veto actionability should not coincide.
- 틀리다면: at least one branch-orthogonal projection should pass relaxed structural, E72-budget, post-E101, and active-veto/actionability simultaneously with material local gain.
- 최소 실험: `analysis_outputs/e152_branch_orthogonal_decoder_audit.py`, projecting selected E137-E140 moves into E95-plus-orthogonal and E144-plus-orthogonal families under full/top50/top100 masks and alphas `0.10..1.00`.
- 관측: source rows `4650`, candidate-interest rows `3953`, non-collinear source rows `4650`, projected rows `2880`; relaxed structural `349`, E72-budget `1208`, post-E101 `564`, active-veto actionable `122`, all-four intersection `0`. `relaxed_budget_post101` has `102` rows but actionable `False`; `budget_post101_actionable` has only `1` row but relaxed structural `False`.
- 성공/폐기 기준: support H146 until a decoder produces a non-collinear row with all-four intersection and local edge above `1e-5`. Discard only if a new representation-to-probability translator makes these gates coincide without using E144 public feedback.
- public LB 관측 반응: none directly; E152 produces no submission. E144 remains the public sensor. If E144 wins, H146 still says non-collinear expansion is unresolved; if E144 loses, H146 becomes stronger because even orthogonalized alternatives failed local stress.
- 제출 전략: no E152 submission. Next strategy should model the gate-intersection failure state itself, especially E138 relaxed-budget-post101 rows that fail active-veto and E139 budget-post101-actionable rows that fail relaxed structural.

### H147. E152 near misses fail mainly through S3 active-boundary actionability, while the actionable escape fails raw/world health

- 상태: supported by E153; no submission.
- 왜 그럴듯한가: E152 found `103` three-of-four near misses and no all-four row. If the failure were a global threshold artifact, blockers should be mixed or scalar-relaxable. If it is a real decoder-state conflict, near misses should concentrate in a specific gate/target anatomy.
- 맞다면: most near misses should pass relaxed/E72/post-E101 but fail the active-boundary/actionability gate, with target anatomy pointing to a concrete exposure axis. Any actionability-safe row should fail a different structural health condition rather than simply needing a small threshold relaxation.
- 틀리다면: missing-gate classes should be balanced, E72/post-E101/relaxed blockers should be common among near misses, or a near miss should become all-four under a small uniform tolerance without changing target anatomy.
- 최소 실험: `analysis_outputs/e153_gate_intersection_failure_atlas.py`, rebuilding E152 projected candidates, preserving candidate-row identity with `variant_pos`, attaching target/axis movement anatomy, and classifying gate blockers.
- 관측: projected rows `2880`, three-of-four near misses `103`, all-four rows `0`. `missing_actionable` has `102` rows, and `101/102` fail active/Q2S3 while E72/material/relaxed blockers are `0/102`. `missing_relaxed` has `1` row and fails raw/world health while action blockers are `0/1`. Missing-actionable target lift is S3 `+0.022774`, S4 `+0.020949`, S2 `+0.018800`, while Q2 is effectively absent.
- 성공/폐기 기준: support H147 until a decoder creates an all-four row by explicitly reducing S3 active-boundary exposure or preserving raw/world health. Discard only if an independent repair shows the E153 blocker split was an artifact of E152 candidate construction.
- public LB 관측 반응: none directly; no file is produced. If E144 improves, H147 remains a local decoder-expansion bottleneck. If E144 fails, H147 becomes stronger because the same S3/Q3/active-boundary weakness seen in E147/E148/E149 likely controls the branch.
- 제출 전략: no E153 submission. The next file must be generated from S3 active-boundary repair of the `102` missing-actionable rows or raw/world-health repair of the lone actionable row, and must pass all-four gates before materialization.

### H148. S3 active-boundary repair can open the E152 all-four gate, but only as an E144-collinear branch extension

- 상태: supported by E154; materialized candidate.
- 왜 그럴듯한가: E153 showed the dominant E152 near misses already pass relaxed/E72/post-E101 gates and fail only S3-heavy actionability. If the conflict is local rather than terminal, a tiny S3 rollback on the right active-boundary cells should open all-four without destroying local reward.
- 맞다면: S3-only rollback should create all-four rows; the surviving rows should target E101-active/S3 cells, keep E72/post-E101 safety, and remain close to the E142/E143/E144 residual branch rather than forming a broad new axis.
- 틀리다면: S3 rollback should either leave actionability closed, break relaxed/post-E101 health, or produce only non-material micro rows worse than E144.
- 최소 실험: `analysis_outputs/e154_s3_active_boundary_repair_probe.py`, rolling back selected S3 cells from E152 `missing_actionable` rows toward E95 and rescoring with the same relaxed/E72/post-E101/actionability/local-material gates.
- 관측: `7458` S3 repair rows from `102` sources produced `10` all-four rows and `10` materializable rows. Selected `submission_e154_s3repair_9f2e2e73.csv` uses `top_s3_e101_3`, keep `0.25`, and `3` S3 rollback cells. It has all-minus-E95 `-0.000012158050`, beats E144 locally, moves `294` cells versus E95, contains all `185` E144 cells, and has cosine with E144 `0.983569299` while staying nearly orthogonal to E72/E101 negative axes (`-0.031628728` / `-0.005523655`).
- 성공/폐기 기준: support H148 until public feedback rejects E154 or shows E144 is better. A public E154 win strengthens S3 active-boundary repair as the missing gate-intersection law. An E154 loss with E144 win means the added branch-orthogonal body or exact S3 rollback is overfit. Losses for both E154 and E144 close the transfer-budget residual branch as a public-sensor path.
- public LB 관측 반응: E154 is now the highest-information next public sensor because it tests the repaired all-four intersection directly. E144 remains the conservative same-branch contrast.
- 제출 전략: submit `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` first if using one slot for the current live hypothesis. Keep `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` as the contrast file, not the default first file.

### H149. The E154 branch body is a low-amplitude ridge, not an exact point

- 상태: supported by E155; materialized conservative control candidate.
- 왜 그럴듯한가: E154 may have passed all-four because the selected E152 source carries a robust E144-plus residual direction, not because every full-amplitude added cell is required. A low-amplitude interpolation should preserve health if the direction is real.
- 맞다면: E144->E154 logit interpolation at alpha below `1.0` should keep relaxed structural, E72-budget, post-E101, actionability, and local material gates open. Target-drop/target-only ablations should not show a single fragile target whose removal kills all-four.
- 틀리다면: only full E154 or the exact selected-source keep factor should pass all-four; lower body ratios should fail actionability, relaxed health, or E144 local edge.
- 최소 실험: `analysis_outputs/e155_e154_branch_body_ablation.py`, scoring body alphas, source S3 repair keep factors, and target drop/only ablations with the same health gates.
- 관측: `44` rows, `40` variants, `34` all-four variants, `27` submit variants, and `22` reduced-body submit variants. The materialized `submission_e155_bodytemp_d27e7965.csv` uses E144->E154 alpha `0.25`, body-norm ratio `0.25`, all-minus-E95 `-0.000010362491`, post-E101 p95 `-0.00000377`, and E72 gap `-0.00000108`. All `12/12` target-drop rows remain all-four and submit.
- 성공/폐기 기준: support until public feedback separates E154/E155/E144. If E154 and E155 both win, the repaired branch is robust. If E154 loses but E155 wins, full-body amplitude is overextended. If E155 loses while E154 wins, the lower-amplitude local edge was too weak or public requires the full body. If both lose, close the branch.
- public LB 관측 반응: E154 remains the first sensor for maximum information and edge. E155 is the conservative amplitude-control sensor, useful if downside risk matters or after an E154 loss.
- 제출 전략: keep `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` first; add `analysis_outputs/submission_e155_bodytemp_d27e7965.csv` ahead of E144 as the low-amplitude repaired-branch contrast.

### H150. The repaired low-body ridge decomposes into a tiny Q1/S2/S4 add-on over E144

- 상태: supported by E156; materialized low-body decomposition control.
- 왜 그럴듯한가: E155 target ablations showed that all target drops survived and Q1-only already cleared local submit criteria. That implies the E154 body may not require its extra Q3/S3 components even though E154 itself was opened by S3 active-boundary repair.
- 맞다면: a target-wise amplitude lattice over E144->E154 should produce all-four candidates with body norm below E155's `0.25`, and the minimum-body survivor should avoid some extra Q3/S3 movement while staying branch-collinear and public-negative-axis safe.
- 틀리다면: all body-norm `<0.25` target-axis candidates should fail all-four health or fail to beat E144 locally; only the diagonal E155 body should be coherent.
- 최소 실험: `analysis_outputs/e156_e154_target_axis_lattice.py`, scanning `Q1,Q3,S2,S3,S4` target-axis amplitudes over `0,0.25,0.50,0.75,1.0` with full non-anchor evaluation.
- 관측: `3125/3125` lattice variants were all-four after full evaluation, `2984` were strict candidates, and `85` used less body norm than E155 while beating E144. The selected file `submission_e156_targetaxis_757546d2.csv` uses `Q1+S2+S4` with alphas `0.25/0.75/0.25`, body ratio `0.171266667`, all-minus-E95 `-0.000010004`, post-E101 p95 `-0.000003712`, and E72 gap `-0.000002266`.
- 성공/폐기 기준: support until public feedback separates E154/E155/E156/E144. If E156 wins while E154/E155 lose, the live law becomes "tiny Q1/S2/S4 add-on only." If E156 loses while E144 wins, even that add-on is public-overfit. If E154/E155 win, E156 is only a downside-control diagnostic and not the main branch.
- public LB 관측 반응: E156 should not replace E154 as the first sensor because it has weaker local edge and is almost E144-collinear. It is useful as a third repaired-branch control before falling back to pure E144.
- 제출 전략: submit order for this branch is E154 -> E155 -> E156 -> E144, unless the goal is specifically to test the conservative unrepaired branch first.

### H151. E156's minimum-body axis choice is a body-selection artifact, not a target law

- 상태: supported by E157; materialized tuned low-body Pareto control.
- 왜 그럴듯한가: E156 made every lattice row all-four, so the selected Q1/S2/S4 row may reflect the objective "minimize body while barely beating E144" rather than a hidden target-axis law.
- 맞다면: finite differences over the lattice should show other axes, especially Q3, are still locally favorable; low-body rows that include Q3 should be able to dominate E155 on local/post-E101/E72 stress despite not being the minimum-body row.
- 틀리다면: Q1/S2/S4 should be uniquely favorable and Q3/S3 should look adverse or unstable under local/post-E101/E72 finite differences.
- 최소 실험: `analysis_outputs/e157_e156_axis_response_audit.py`, using the E156 scan to compute target-axis finite differences and E155-dominating low-body Pareto rows.
- 관측: all `3125` lattice rows are all-four and `2984` are strict. Every axis has favorable local and post-E101 finite differences, with Q3 strongest for all-minus (`-0.000000383335`) and post-E101 p95 (`-0.000000132956`). E72 gap is controlled almost entirely by S2 (`-0.000000714955`). Three rows use less body than E155 while improving local, post-E101 p95, and E72 gap; the selected `submission_e157_lowbodypareto_bd67930d.csv` uses Q1+Q3+S2+S4, body ratio `0.240336139`, all-minus `-0.000010404446`, post-E101 p95 `-0.000003807382`, and E72 gap `-0.000001671496`.
- 성공/폐기 기준: support until public feedback says target-axis-tuned low-body rows behave differently from diagonal E155. If E157 improves while E155 fails, target-axis tuning matters despite tiny local edge. If E155 improves and E157 fails, the tuned Pareto row overfit the local lattice. If both fail, the repaired low-body branch is not public-real.
- public LB 관측 반응: E157 is not a first sensor because its edge over E155 is only `~4.2e-8` local all-minus. It is an optional tuned-control after E154/E155, not evidence of a new broad latent.
- 제출 전략: keep E154 first, E155 second for clean amplitude interpretation, then E157 before E156 if the goal is target-axis-tuned low-body control. E156 remains the minimum-body control.

### H152. Repaired-branch controls are post-feedback instruments, not independent first sensors

- 상태: supported by E158 local distinguishability; pending public feedback.
- 왜 그럴듯한가: E154/E155/E157/E156/E144 are all E144-collinear, and E157/E156 were created inside a saturated all-four lattice. The risk is ranking tiny local edge differences as if they were public-readable independent signals.
- 맞다면: E155/E157/E156 pairwise local gaps should be below the public-readable guardrail, while E154 should remain meaningful mainly against unrepaired E144 and as a full-body interpretation sensor.
- 틀리다면: E154/E155/E157/E156 should separate at local deltas larger than `2e-6`, with materially different logit geometry or different stress gates.
- 최소 실험: `analysis_outputs/e158_repaired_branch_public_decoder.py`, computing live submission geometry, local stress gaps, pairwise distinguishability, and pre-registered public score bands.
- 관측: E154 vs E155 local gap is `-0.000001795559`, below `2e-6`; E157 vs E155 is only `-0.000000041955`; E156 vs E155 is `+0.000000358921`. E154 vs E144 is `-0.000002432120`, above guardrail. E155/E157/E156 cosines vs E144 are `0.998962769`/`0.999041566`/`0.999515751`.
- 성공/폐기 기준: support until public feedback shows a target-axis control like E157/E156 separates from E155 despite sub-guardrail local gaps. If E154 wins clearly, siblings should not be auto-submitted before exact-delta rebuild. If E154 loses or ties, E155 is the only clean same-family follow-up.
- public LB 관측 반응: E154 clean win validates the repaired all-four branch; E154 tie/small-loss makes E155 an amplitude-control; E154 hard-fail blocks E157/E156 micro-control rescue.
- 제출 전략: submit order remains `E154 -> E155 -> E157 -> E156 -> E144`, but this order is for information, not raw expected score.

### H153. E154 feedback must be decoded by component responsibility, not score band alone

- 상태: supported by E159; pending public feedback.
- 왜 그럴듯한가: E158 only says which score band E154 lands in. But E154 is a composite move: it contains inherited E144 body plus E154-specific adjustment and extra cells. A loss can therefore mean full-body overextension, inherited E144 branch failure, or target-prior mismatch; those imply different next actions.
- 맞다면: decomposing E154 into additive LogLoss segments should show that loss-side worlds can be assigned to specific target/component responsibility groups, and E155 should be justified only when the blame is concentrated in E154-added body rather than inherited E144 body.
- 틀리다면: component attribution should be diffuse or dominated by the same groups across wins and losses, making it useless for action; or the additive segment decomposition should not reproduce E154-vs-E95 direct deltas.
- 최소 실험: `analysis_outputs/e159_e154_public_outcome_attribution.py`, decomposing E95->E144, E144->E154-on-inherited-cells, and E154-extra-cell segments, while sharing hidden labels across duplicate row-target segments.
- 관측: E154 has `294` unique moved cells and `479` additive segments across `139` rows and `9` subjects. Additive segment sums match direct E154-vs-E95 hard-label deltas with max errors `1.75e-16` and `1.93e-16`. Component flip-benefit is dominated by inherited E144 body `3.292000000` versus E154 extra body `0.255975083` and E154 adjustment `0.203843941`. Focus-prior win mass remains meaningful (`0.728550` global, `0.601575` subject, `0.666680` nearest-hard), but hard-fail blame is inherited-body dominated under all focus priors.
- 성공/폐기 기준: support until E154 public feedback arrives. If E154 ties/small-loses and E159 points to added-body overextension, E155 is the clean follow-up. If E154 branch-loss/hard-fails with inherited-body blame, E155/E157/E156 are not rescues and the branch should fall back to E144 or representation search.
- public LB 관측 반응: E154 win credits only the groups with negative conditional contribution; E154 non-win must be read through E159 before any sibling submission. A scalar score alone is deliberately insufficient.
- 제출 전략: keep `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` first, but require E158+E159 interpretation before promoting `analysis_outputs/submission_e155_bodytemp_d27e7965.csv`.

### H154. E154 post-feedback action can be pre-committed as an executable interpreter

- 상태: supported by E160; pending public feedback.
- 왜 그럴듯한가: E158 and E159 are useful but separate. If the future E154 score requires manual synthesis, the branch can still drift into post-hoc score interpretation.
- 맞다면: a deterministic interpreter should map any E154 public score into exactly one E158 band, join the E159 component read, and mark E155/E157/E156 eligibility before seeing the score.
- 틀리다면: score bands and component attribution would conflict or leave multiple incompatible actions for the same outcome.
- 최소 실험: `analysis_outputs/e160_e154_postfeedback_interpreter.py`, building a seven-row decision table and validating score probes.
- 관측: E160 produced `7` decision rows. E155 gate is `not_needed` for win bands, `information_only` for tie and small_loss, and `not_recommended` for branch_loss/hard_fail. Score probes mapped `0.5763003660` to `small_loss` and `0.5762880000` to `micro_win`. Branch_loss/hard_fail component tops are inherited E144 body under all focus priors.
- 성공/폐기 기준: support until actual E154 feedback arrives. If E160 maps the score to branch_loss/hard_fail, sibling controls are blocked. If it maps tie/small_loss, E155 is only information-only unless the component read is added-body dominant. If it maps a win, promote E154 and rebuild anchor audits.
- public LB 관측 반응: run `python3 analysis_outputs/e160_e154_postfeedback_interpreter.py --score <PUBLIC_LB>` after E154 submission before choosing a follow-up.
- 제출 전략: E154 remains next. E160, not manual judgment, decides whether E155 is allowed afterward.

### H155. E154 attribution-risk pruning is diagnostic but not a public-readable successor

- 상태: supported by E161; no new submission.
- 왜 그럴듯한가: E159 shows branch/hard-fail worlds can blame inherited E144 body. If that blame is concentrated in identifiable cells, pruning high-risk cells toward E144 or E95 might reduce public-tail risk while preserving the repaired all-four state.
- 맞다면: top-risk cell pruning should produce all-four rows, reduce public-free expected LogLoss risk versus E154, and at least some rows should beat E154 by a public-readable local margin.
- 틀리다면: pruning may reduce expected risk but either break health/local edge or remain too close to E154 to justify a pre-feedback submission.
- 최소 실험: `analysis_outputs/e161_e154_inherited_body_pruning_audit.py`, using E159 cell-level risk to generate `1608` top-risk prune variants and rescoring them with the E154/E155 relaxed/E72/post-E101/actionability stack.
- 관측: `631/1608` pruning rows keep all-four health, `299` are control-grade, and `1226` are safer than E154 under focus expected risk. But submission-grade rows are `0`, public-readably better-than-E154 rows are `0`, and the best local delta versus E154 is only `-0.000000045921`, far below the `2e-6` guardrail.
- 성공/폐기 기준: support until E154 feedback. If E154 wins, pruning is unnecessary. If E154 tie/small-loses with added-body blame, E155 remains the cleaner amplitude-control; if inherited-body blame dominates but the branch is still alive, E161 rows become diagnostic controls rather than first-line submissions.
- public LB 관측 반응: none yet. E161 should not be submitted before E154 because it does not create a readable independent edge.
- 제출 전략: no E161 submission. Keep E154 first; keep E161 pruning as post-feedback diagnostic material.

### H156. The repaired-branch plateau is hidden-label resolution limited

- 상태: supported by E162; pending E154 public feedback.
- 왜 그럴듯한가: E158 and E161 show branch controls differ by `1e-6` scale local gaps. LogLoss on a hidden public subset can move more than that if a single high-swing row-target label realizes support/adverse differently.
- 맞다면: pairwise E154/E155/E157/E156/E161-control hard-label swings should be concentrated enough that one or a few cells can exceed the `2e-6` public-readable guardrail.
- 틀리다면: sibling differences should be distributed across many cells, so no single hidden label could dominate the score at the public-readable scale.
- 최소 실험: `analysis_outputs/e162_branch_readability_flip_thresholds.py`, computing pairwise hard-label deltas, swing concentration, and minimum top-swing cells for the public-readable guardrail.
- 관측: E154-vs-E155 has focus expected delta `+0.000000505`, but top1 swing `0.000010815`; E154-vs-E144 has top1 swing `0.000014420`; E157-vs-E155 has top1 swing `0.000002185`. For every live sibling/control pair, cells needed to reach the `2e-6` guardrail is `1`. E154-vs-E95 top1 swing is `0.000015340`, roughly the whole E95-over-mixmin edge.
- 성공/폐기 기준: support until a new candidate has a branch edge that remains larger than the top-cell swing concentration or is validated by public feedback. If E154 public score clearly wins despite this fragility, promote it as a new anchor but still rebuild exact-delta audits.
- public LB 관측 반응: E154 result should be interpreted as a hidden-label world observation, not as fine-grained ranking among E154/E155/E157/E156. A sibling win/loss without E154 context would be low-information.
- 제출 전략: keep E154 first. Do not submit sibling/pruning controls as expected-score candidates before E154 feedback.

### H157. The post-E95 plateau is broadly hard-label-resolution limited, while mixmin was a broad signal

- 상태: supported by E163; pending the next public sensor.
- 왜 그럴듯한가: E95 improved over mixmin by only `0.0000153107`, and E101 lost to E95 by only `0.0000090362`. If those public deltas are smaller than one or a few high-swing hard-label cells, local/CV ranking after E95 is underresolved even when the direction is real.
- 맞다면: known post-mixmin transitions should require only a few top hard-label cells to explain their actual public deltas, while the original mixmin-vs-a2c8 breakthrough should look broader. Live post-E95 candidates should all have one-cell readability fragility at the `2e-6` guardrail.
- 틀리다면: E95/E101/E72 public deltas should require many distributed cells, and live E154/E144/E142/E143 branch candidates should have top-cell swings below public-readable scale.
- 최소 실험: `analysis_outputs/e163_candidate_edge_breadth_audit.py`.
- 관측: mixmin-vs-a2c8 actual public delta `-0.0011326805` needs `25` top cells; E95-vs-mixmin actual delta `-0.0000153107` needs `1`; E101-vs-E95 actual delta `+0.0000090362` needs `1`; E101-vs-mixmin needs `1`; E72-vs-mixmin and E72-vs-E95 need `4` and `6`; live post-E95 candidates have `7/7` one-cell `2e-6` fragility.
- 성공/폐기 기준: support until a candidate demonstrates a broad low-tail-safe edge like mixmin or public feedback shows a post-E95 sibling transition with stable multi-cell attribution. If E154 wins, it becomes a new anchor but not a proof that sibling ranking was pre-feedback resolvable.
- public LB 관측 반응: E154 public feedback should be read as a world observation about the repaired branch. A tiny E154/E155/E157 difference is not enough to infer a reusable local ranker.
- 제출 전략: no E163 submission. Keep E154 first; require future candidates to either recover broad mixmin-scale structure or explicitly beat top-cell fragility.

### H158. The existing submission universe still contains a broad post-E95 branch

- 상태: supported by E164, but raw direct submission is rejected.
- 왜 그럴듯한가: E163 says post-E95 repaired-branch candidates are too narrow. If the plateau is not fundamental signal exhaustion, a previously generated latent/JEPAs branch may still contain a broad direction that was rejected only because direct amplitude was unsafe.
- 맞다면: scanning existing tracked submissions should find E95-relative rows with many moved cells, many rows, many top cells required to overturn the focus-prior expected edge, and low direct alignment with the E72/E101 failure axes.
- 틀리다면: every candidate would be E154-like one-cell fragile, known-bad-axis aligned, or locally expected-positive versus E95.
- 최소 실험: `analysis_outputs/e164_universe_broad_edge_screen.py`.
- 관측: `2052` tracked submission paths produced `1977` unique tensors. E164 found `198` broad-edge rows, `193` low-E72-axis rows, and `192` candidate-gate rows. The top row `submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv` has focus expected delta `-0.025880912`, cells-to-flip `54`, and top1/expected `0.029985445`.
- 성공/폐기 기준: support only if broad rows survive bad-axis geometry and amplitude control. E164 alone is not sufficient because known public-bad E72/LeJEPA rows can pass broadness-style gates.
- public LB 관측 반응: a raw broad JEPA public loss would not refute the branch, only the direct amplitude. A small scaled survivor win would strengthen H158.
- 제출 전략: do not submit raw E164 rows. Pass through E165/E166.

### H159. Broad survivor rows are not merely known public-bad geometry

- 상태: supported by E165 with medium confidence.
- 왜 그럴듯한가: E164 broadness could be shortcut/collapse if it lies in the span of public-bad moves. A LeJEPA-style geometry check should kill those rows before any submission.
- 맞다면: known public-bad broad controls should have high bad-span energy or max bad-axis cosine, while some broad candidates remain low-energy outside that span.
- 틀리다면: all broad rows should either fail geometry health or the health gate should also admit known public-bad controls.
- 최소 실험: `analysis_outputs/e165_broad_edge_bad_axis_geometry.py`.
- 관측: bad axes `a2c8,raw05,stage2,ordinal,final9,e72,q2_bad,lejepa_bad,resid_bad` reject known broad-bad controls. E165 scored `205` rows, including `192` E164 candidate rows, and left `90` geometry-health survivors. The top survivor has bad-span energy `0.450742441`, max bad-axis cosine `0.268538582`, and mean abs logit move `0.224398639`.
- 성공/폐기 기준: support is conditional on amplitude shrinkage. If a tiny scaled survivor fails public badly, H159 weakens because the current bad-axis basis is undercomplete.
- public LB 관측 반응: E166 win strengthens the claim that the survivor branch is not a known-bad shortcut. E166 loss says the bad-axis span missed the relevant public-negative geometry.
- 제출 전략: use broad survivors only after logit-scale shrinkage.

### H160. A tiny E95-to-broad-survivor step can beat top-cell fragility

- 상태: newly supported locally by E166; pending public feedback.
- 왜 그럴듯한가: raw broad survivors are too large, but their direction may encode a real latent branch. A `1%` logit step from E95 can keep distributed hard-label support while making the probability movement small enough to avoid full-JEPA collapse risk.
- 맞다면: scaled survivor rows should keep a large negative focus-prior expected delta, require many top cells to overturn that expected edge, stay outside known bad axes, and reject scaled known-bad controls.
- 틀리다면: after shrinking, broad edge should disappear, become one-cell fragile, align with bad axes, or allow known bad controls through the same gate.
- 최소 실험: `analysis_outputs/e166_broad_survivor_scale_probe.py`.
- 관측: `198` scaled rows were scored, `112` passed the scaled sensor gate, and `51` material rows passed scale `<=0.03`. Negative controls passed `0` gates. The selected file `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv` uses scale `0.01` toward `submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv`, with focus expected delta `-0.000332077`, cells-to-flip `74`, top1/expected `0.023369627`, bad-span energy `0.450742441`, max bad-axis cosine `0.268538582`, and mean/max abs logit move `0.002243986` / `0.013580886`.
- 성공/폐기 기준: if public improves over E95, broad-survivor latent becomes the main branch and should be amplitude/target-decomposed. If public loses but stays near E95, the branch may still be directionally partial but amplitude/target mixture is wrong. If it hard-fails, E165 geometry is undercomplete and this broad survivor family should be blocked.
- public LB 관측 반응: a win below `0.5762913298` is much more informative than another E154 sibling micro-edge because the candidate is broad and non-collinear with E154 (`cos 0.061661852`). A loss weakens the "existing broad latent" escape and returns priority to repaired-branch public sensors.
- 제출 전략: `submission_e166_broadsurv_s0p01_d8bfa94b.csv` is the broad-escape sensor. `submission_e154_s3repair_9f2e2e73.csv` remains the conservative repaired-branch sensor.

### H161. E166 is context-real but safety-atlas divergent

- 상태: supported by E167 with medium confidence; public feedback pending.
- 왜 그럴듯한가: E166 passed breadth and bad-axis checks, but broadness can still be a submission-manifold shortcut. A real broad latent should leave traces in hidden row/block/calendar context, while a safer branch should also align with the transfer-shrinkage and veto-null atlas.
- 맞다면: E166 focus cells should be enriched for non-random context such as edge-like or between-train-runs cells, but their safety-atlas metrics may explain why this branch remains risky.
- 틀리다면: target-count-matched permutation sets should show similar context rates and safety metrics, making E166 only a random broad perturbation.
- 최소 실험: `analysis_outputs/e167_broad_survivor_context_alignment.py`.
- 관측: E166 top-benefit focus cells are context-enriched: edge-like rate `0.689189` vs null `0.470842` (`z=3.902`, `p_high=0.000333`), between-train-runs `0.797297` vs `0.624658` (`z=3.293`, `p_high=0.001333`), and top-subject share `0.243243` vs `0.164563` (`z=3.498`). They are also safety-atlas adverse: all-veto-null `0.297297` vs `0.574158`, all-safe-density `0.117097` vs `0.243966`, broad-low-alpha mass `1.321365` vs `3.199735`, E101-plausible mass `0.238204` vs `0.533727`, while E72-active rate is high at `0.837838` vs `0.670369`.
- 성공/폐기 기준: support survives if public E166 wins or loses only slightly while attribution points to a missing safety-axis basis. It weakens if E166 hard-fails and the adverse safety-atlas metrics explain the miss without revealing a recoverable context subset.
- public LB 관측 반응: an E166 win says the safety atlas was too conservative or branch-bound and that hidden calendar context can beat current veto logic. An E166 loss says E72-active and low-veto-null divergence is the missing public-negative axis for this broad branch.
- 제출 전략: keep E166 as a single broad-escape sensor. Do not scale or same-family tune it before public feedback. If it wins, decompose amplitude/targets around the edge-like/between-train-runs context; if it loses, revise the bad-axis/safety-atlas gate before any broad JEPA-like retry.

### H162. E166's context signal can be safety-repaired without fully killing breadth

- 상태: supported by E168; materialized by E169.
- 왜 그럴듯한가: E167 showed two opposing facts in the same branch: hidden context enrichment and safety-atlas divergence. If those facts are not perfectly coupled, a context-high plus safety mask should keep material broad edge while improving veto/safe-density and reducing E72-active exposure.
- 맞다면: simple pre-public masks such as `edge-like OR between-train-runs` intersected with veto-null or high safe-density should keep expected delta below `-1e-4`, retain at least `20` cells-to-flip, keep top1/expected below `0.05`, and improve both context and safety metrics versus all-E166.
- 틀리다면: every safety-improving mask should become too small, top-cell fragile, context-poor, or expected-edge weak.
- 최소 실험: `analysis_outputs/e168_e166_safety_context_decoupling.py`.
- 관측: two policies pass. `context_high__veto` keeps `904` cells across `193` rows, expected delta `-0.000120457`, cells-to-flip `32`, top1/expected `0.048415`, edge-like `0.610619`, between-train-runs `0.819690`, veto `1.0`, safe-density `0.346150`, E72-active `0.268805`. `context_high__high_density_p50` is nearly identical. Strict edge-and-between masks are too top-cell fragile.
- 성공/폐기 기준: support holds if materialized tensors also pass bad-axis and amplitude stress. It weakens if public feedback on E169 says the safety repair removed the true broad signal or preserved the wrong public-negative cells.
- public LB 관측 반응: an E169 win says broad hidden-context signal is public-real but needs safety-veto masking. An E169 loss says either the broad branch is still wrong or the E168 safety proxy is not the right public-negative axis.
- 제출 전략: prefer the context-high veto mask before raw E166 when the public slot asks for balanced broad repair rather than deliberate safety-atlas falsification.

### H163. A materialized context-high safety mask is a healthier broad-branch sensor than raw E166

- 상태: supported locally by E169; public feedback pending.
- 왜 그럴듯한가: E166 is broad but safety-divergent. A healthier LeJEPA-style successor should preserve hidden-context breadth while lowering bad-axis energy, movement amplitude, and unsafe E72-active exposure.
- 맞다면: the materialized mask should pass the same breadth/bad-axis stress as E166 with lower bad-span energy and smaller mean logit movement, without becoming an E154/E101 same-family micro-control.
- 틀리다면: after materialization the mask should collapse into one-cell fragility, align with known bad axes, become too Q2/S3-specific, or lose material expected edge.
- 최소 실험: `analysis_outputs/e169_e166_context_safety_mask_materializer.py`.
- 관측: `submission_e169_ctx_veto_c5e806e3.csv` passes stress with expected delta `-0.000120457`, moved cells/rows `904/193`, cells-to-flip `32`, top1/expected `0.048415`, bad-span energy `0.295326`, max bad cosine `0.222381`, mean/max abs logit `0.001096`/`0.010206`, Q2/S3 share `0.347775`, and cosine to E154/E101/mixmin `0.087180`/`-0.021896`/`-0.020672`.
- 성공/폐기 기준: support until public feedback. A win promotes context/safety repaired broad latent as the next main branch. A loss demotes E168's safety repair and forces either raw E166 as a deliberate falsification test or a new safety-axis search.
- public LB 관측 반응: better than E95 (`<0.5762913298`) means the broad lane can survive when repaired by context-high/veto masking. Worse than E101 (`>0.5763003660`) means the repair is not enough and broad branch remains public-risky. Between those values is a weak branch-alive but not frontier read.
- 제출 전략: `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv` is the best balanced broad-branch candidate. `submission_e169_ctx_high_density_p50_51110c7e.csv` is a near-duplicate control. Raw E166 remains the sharper but riskier atlas-falsification sensor.

### H164. E169 is broad in expectation but still public hard-label-resolution limited

- 상태: supported by E170; public feedback pending.
- 왜 그럴듯한가: E169 fixes E166's safety/context conflict locally, but the public metric observes hidden hard labels. If the remaining public edge can be moved by only a few high-swing cells, E169 should be treated as a pre-registered sensor rather than a stable expected-score claim.
- 맞다면: E169-vs-E95 should have broad expected support, but `cells_for_2e6_guard` and `cells_for_e95_edge` should remain very small. Near-duplicate E169 variants should differ below useful public resolution.
- 틀리다면: E169-vs-E95 would need many top cells to move public LB, and E169 variants would separate by target/context in a way that creates a clear next-file ranking.
- 최소 실험: `analysis_outputs/e170_e169_public_feedback_decoder.py`.
- 관측: E169-vs-E95 moves `904` cells over `193` rows with expected delta `-0.000120457` and `32` cells-to-flip expected, but only `1` top cell reaches the `2e-6` guard and `4` cells cover the E95-over-mixmin edge. Between-train-runs carries `81.1%` of expected edge, not-E72-active carries `73.7%`, and target shares are distributed across S1/S3/Q2/S4/Q1/S2/Q3. The high-density p50 control differs from ctx-veto by only `10` Q2/S3 cells and `-0.000001377` expected delta.
- 성공/폐기 기준: a public score below E95 supports the context-high/veto broad latent. Tie/small loss keeps E95 as practical frontier and makes raw E166 information-only. Worse than E101 demotes E169 and shifts toward E154 or a new broad safety-axis search. Worse than mixmin closes near-duplicate E169 variants.
- public LB 관측 반응: interpret with E170 bands: `<=0.576261330` broad breakthrough; `<=0.576276019` clean win; `<=0.576288330` micro win; `<=0.576294330` tie; `<=0.576300366` small loss; `<=0.576306641` worse than E101 but still mixmin-safe; above mixmin is branch loss/hard fail.
- 제출 전략: if one broad-branch file is tested, submit `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv` and immediately run `python3 analysis_outputs/e170_e169_public_feedback_decoder.py --score <PUBLIC_LB>`. Do not submit `ctx_high_density_p50` before ctx-veto feedback.

### H165. E169's broad body and public-decisive cells have opposite visible-prior health

- 상태: supported by E171.
- 왜 그럴듯한가: E170 showed the broad body and top hard-label cells are different objects. A broad expected edge can coexist with top-cell visible-prior adversity if the candidate is a hidden-label sensor rather than a resolved selector.
- 맞다면: full E169 moved cells should be favorable under broad/global/subject priors, while the top swing cells that decide public readability should have low support and possibly fall below target-matched null support.
- 틀리다면: top swing sets would be at least as supported as target-matched nulls, and flank priors would agree with subject/global priors on a win.
- 최소 실험: `analysis_outputs/e171_e169_critical_cell_prior_audit.py`.
- 관측: full `visible_mean` simulation gives mean delta `-0.000022659` and win rate `0.868840`; subject gives win `0.853520`, focus_mean `0.994460`. But flank priors are weak/adverse (`nearest_beta` mean `+0.000005364`, `edge_endpoint_beta` `+0.000005106`, `flank_mean` `+0.000000790`). Top1 support is only `0.098648`, top4 swing-weighted support `0.330699`, top32 `0.247434`; top32 is below a target-matched null mean `0.353573` with `z=-2.703`, `p_low=0.001667`.
- 성공/폐기 기준: if E169 wins, the broad-body prior was more informative than critical-cell visible flank support. If E169 loses or small-loses, top-cell adversity explains the miss without killing the whole broad branch.
- public LB 관측 반응: E169 win promotes subject/global broad-body interpretation. E169 tie/small-loss says top critical cells overruled the body. Worse than mixmin says the body prior itself was public-misaligned, not just top-cell underresolution.
- 제출 전략: E169 remains a high-information sensor, not a stable expected-score claim. Do not use E171 to construct a top-cell prune unless the resulting tensor passes E169 breadth and E170 readability again.

### H166. E169's visible-prior adverse tail can be rolled back without killing the broad body

- 상태: supported locally by E172; public feedback pending.
- 왜 그럴듯한가: E171 split the same candidate into a visible-prior-favorable body and a visible-prior-adverse public-decisive tail. If those are separable, rolling back only visible-prior-positive-loss cells should keep E169's context/veto breadth while reducing public-tail risk.
- 맞다면: rollback variants should keep `>=820` moved cells, `>=24` cells-to-flip, focus expected edge `<= -8e-5`, and improve visible-prior p95/worse-than-E101 tail without moving into known bad axes.
- 틀리다면: any rollback should either destroy the broad edge, become one-cell fragile, keep visible-prior p95 positive, or align more strongly with E72/E101/Q2-bad axes.
- 최소 실험: `analysis_outputs/e172_e169_critical_tail_rollback_probe.py`.
- 관측: `67` variants were scored and `7` passed stress-gate. The selected `visible_positive_all_keep0p25` row rolls back `410` cells to `25%` of E169 movement, materializing `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv`. It keeps expected focus delta `-0.000112695`, moved cells/rows `904/193`, cells-to-flip `30`, and top1/expected `0.051750`; visible-prior p95 changes from E169 `+0.000010607` to `-0.000026683`, and visible worse-than-E101 from `0.058545` to `0.000050`. Bad-span energy improves from `0.295326` to `0.257874`.
- 성공/폐기 기준: support strengthens if E172 beats E95 or beats a future E169 score, because the broad body survived while the visible-positive-loss tail was the missing constraint. It weakens if E172 loses similarly to or worse than E169, because the visible-prior rollback did not match public labels.
- public LB 관측 반응: E172 win promotes visible-tail rollback as a real broad-branch constraint. E172 tie/small-loss keeps E95 practical and leaves E169 as information-only. E172 worse than mixmin says visible-prior damping overcorrected or the broad body is wrong.
- 제출 전략: submit `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv` before raw E169 when the goal is the strongest broad-branch expected-score candidate. Submit raw E169 only when deliberately asking the pure body-vs-critical-tail question.

### H167. E172 repairs prior-tail health but not the hidden hard-label resolution bottleneck

- 상태: supported by E173; public feedback pending.
- 왜 그럴듯한가: E172 was designed to fix visible-prior tail risk, not to change which high-swing public labels exist. If the broad body is unchanged, hard-label readability may remain nearly identical to E169 even while visible/flank priors improve.
- 맞다면: E172-vs-E95 should keep broad moved-cell support and improved prior moments, but still require only a few top swing cells to move public LB by the E95-over-mixmin edge.
- 틀리다면: E172 would either reduce top-cell swing/readability fragility materially or destroy broadness in exchange for prior-tail health.
- 최소 실험: `analysis_outputs/e173_e172_public_feedback_decoder.py`.
- 관측: E172-vs-E95 keeps `904/193` moved cells/rows, expected delta `-0.000112695`, and cells-to-flip `30`, while visible p95 changes to `-0.000026683` and visible worse-than-E101 to `0.000050`. However top1 swing remains `0.000005832`, cells for `2e-6` guard remains `1`, and cells for E95-over-mixmin edge remains `4`.
- 성공/폐기 기준: E172 public win promotes the view that prior-tail repair is enough despite readability fragility. Tie/small loss says tail health improved but hidden hard-label realization still dominates. Worse than mixmin says the broad body or visible-tail proxy is wrong.
- public LB 관측 반응: use E173 bands. `<=0.576276019` is clean support for tail repair; `0.576288330..0.576294330` is tie/underresolution; `0.576294330..0.576300366` is small loss; `>0.576306641` closes E172/E169 same-family broad-lane expected-score variants.
- 제출 전략: E173 originally made E172 the first broad expected-score candidate. H168/E174 supersedes that for upside: E174 is now sharper, while E172 remains the safer tail-repair contrast.

### H168. E172's visible-tail rollback is locally overconservative on a recoverable subset

- 상태: supported locally by E174; public feedback pending.
- 왜 그럴듯한가: E173 showed E172 repairs visible/flank priors but pays E162 focus-prior cost versus E169. If that cost is concentrated in a separable subset, reopening only those cells should recover edge without reopening the E171 visible-prior tail.
- 맞다면: some E172-to-E169 partial-reopen policies should improve E162 focus expected delta by at least `2e-6` versus E172 while keeping moved-cell breadth, visible p95/worse-than-E101, and bad-axis geometry inside E172-style stress guards.
- 틀리다면: any material reopening should either make visible p95 positive, increase worse-than-E101 materially, cross Q2/S3/bad-axis guards, or fail to recover a public-readable amount of focus edge.
- 최소 실험: `analysis_outputs/e174_e172_rollback_overcorrection_probe.py`.
- 관측: `46/80` policies pass the E174 gate. The selected `reopen_focus_cost_top75_to1p0` materializes `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`, with expected focus delta `-0.000124367` (`-0.000011672` vs E172), moved cells/rows `904/193`, cells-to-flip `33`, visible p95 `-0.000022709`, worse-than-E101 `0.000220`, bad-span energy `0.263996`, max bad cosine `0.163229`, and Q2/S3 share `0.339597`.
- 성공/폐기 기준: support strengthens if E174 beats E172/E95 or lands in the E173 clean/micro-win bands. It weakens if E174 loses while E172 later wins or ties better, especially with a read consistent with Q2/S3 or q2_bad over-reopening.
- public LB 관측 반응: E174 win means E172's tail repair was directionally right but too conservative. E174 tie/small-loss means the broad branch is still hidden-label underresolved or the reopened Q2/S3/S3 cells overfit public-free priors. E174 worse than mixmin closes this partial-reopening family until a new public-independent bad-axis explains the miss.
- 제출 전략: if using one broad expected-score slot now, E174 is the sharper candidate. E172 remains the safer contrast; raw E169 remains only the unrolled body-vs-tail sensor.

### H169. E174 must be decoded by pre-registered public bands, not scalar win/loss

- 상태: supported by E175 as decision hygiene; public feedback pending.
- 왜 그럴듯한가: E174 differs from E172 by only `75` reopened cells, and both retain the same broad `904/193` moved-cell body. A small public delta can be explained either by true partial-reopening benefit, hidden hard-label underresolution, or Q2/S3/q2_bad over-reopening.
- 맞다면: E174-vs-E172 should show a readable but thin responsibility map, with recovery concentrated in specific targets/contexts and with visible-tail margin spent but not collapsed. Public bands should imply different next actions before the score is known.
- 틀리다면: E174 public feedback could be interpreted by simple score ordering alone, or the E174-vs-E172 movement would be too diffuse/too tiny to assign responsibility.
- 최소 실험: `analysis_outputs/e175_e174_public_feedback_decoder.py`.
- 관측: E175 fixes score bands from breakthrough `<=0.576261330` through hard fail `>0.576341330`. E174-vs-E172 changes `75` cells over `65` rows, recovers expected focus delta `-0.000011672`, needs `5` expected-support cells to flip that recovery, and has top1 swing `0.000002996`. Recovery is mostly S3/Q2/S2/S1, while visible-tail margin versus E172 is spent by p95 `+0.000003974` and worse-than-E101 `+0.000169869`.
- 성공/폐기 기준: support strengthens if an E174 public score lands in a band whose prescribed next action remains coherent with later E172/E154 feedback. It weakens if E174's score cannot be explained by the fixed responsibility map and requires post-hoc threshold changes.
- public LB 관측 반응: use E175 bands. `<=0.576276019` promotes E174 as broad anchor; `0.576276019..0.576288330` keeps partial reopening alive but unresolved; `0.576288330..0.576300366` keeps E95 practical and points to E172 as contrast; `>0.576300366` demotes E174; `>0.576306641` closes same-family reopening as expected-score follow-up.
- 제출 전략: after submitting E174, run `python3 analysis_outputs/e175_e174_public_feedback_decoder.py --score <PUBLIC_LB>` before any E172/E169/E166/E154 decision. Do not tune top-N, keep factor, or Q2/S3 guard from a single scalar score.

### H170. E174's Q2 reopening is slightly over-opened relative to the rest of the partial-reopen body

- 상태: supported locally by E176; public feedback pending.
- 왜 그럴듯한가: E101 already showed that Q2/S3 tail rollback can be locally plausible but public-negative versus E95. E174 recovered useful S3/Q2/S2/S1 edge, but it also pushed Q2/S3 share to `0.339597`, close to the guard.
- 맞다면: damping reopened Q2 cells should reduce q2_bad/Q2S3 risk while giving up less than `2e-6` of E174's focus edge and retaining E172/E174 broadness.
- 틀리다면: any Q2 damping should either destroy materiality, fail broadness, or reduce risk only by paying a public-readable edge cost.
- 최소 실험: `analysis_outputs/e176_e174_component_ablation_probe.py`.
- 관측: `12/162` component ablation variants pass E176 gate. The selected `ablate_q2_to0p75` materializes `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`, giving up only `+0.000000983` focus delta versus E174 while improving max bad cosine `0.163229 -> 0.158126`, Q2/S3 share `0.339597 -> 0.334753`, visible p95 `-0.000022709 -> -0.000023096`, and worse-than-E101 `0.000220 -> 0.000192`.
- 성공/폐기 기준: support strengthens if E176 beats E95/E174 or if E174 later loses in a way consistent with Q2/q2_bad over-opening. It weakens if E174 beats E176, meaning the Q2 reopening was public-real at full strength.
- public LB 관측 반응: E176 win below E95 validates asymmetric Q2 damping inside partial reopening. E176 tie/small-loss keeps partial reopening underresolved and points back to E172/E154 depending on risk appetite. E176 worse than E101 says even the damped Q2 partial-reopen branch is not public-safe.
- 제출 전략: if submitting one risk-adjusted broad expected-score file now, prefer E176 over E174. Keep E174 as max-edge contrast and E172 as low-risk contrast.

### H171. E176 must be decoded as a Q2-amplitude public sensor, not as a scalar score rank

- 상태: supported as a pre-public decision rule by E177; public feedback pending.
- 왜 그럴듯한가: E176 differs from E174 only by damping `21` reopened Q2 cells. Its expected focus cost versus E174 is only `+0.000000983`, below normal public resolution, so a scalar public LB alone can easily invite post-hoc keep-factor tuning.
- 맞다면: a useful decoder should pre-register E176 bands, show that E176-vs-E174 is a small Q2-only contrast, and specify when E174, E172, or E154 can be considered without changing thresholds after public feedback.
- 틀리다면: E176's public score could be interpreted by ordinary ranking alone, or E176-vs-E174 would have broad enough movement that Q2 amplitude attribution is unnecessary.
- 최소 실험: `analysis_outputs/e177_e176_public_feedback_decoder.py`.
- 관측: E177 fixes bands from breakthrough `<=0.576261330` through hard fail `>0.576341330`. E176-vs-E95 has moved cells/rows `904/193`, expected focus delta `-0.000123384`, cells-to-flip `33`, top1 swing `0.000005832`, and cells for E95-over-mixmin edge `4`. E176-vs-E174 is only `21` Q2 cells over `21` rows, expected focus cost `+0.000000983`, cells-to-flip `2`, top1 swing `0.000000832`, and swing-weighted support `0.495994`.
- 성공/폐기 기준: support strengthens if E176 feedback can be mapped to the fixed E177 band table without changing the Q2 keep rule. It weakens if later public observations force an unanticipated interpretation not covered by E177, especially if E176 and E174 diverge in a way unrelated to Q2 amplitude.
- public LB 관측 반응: E176 below E95 validates Q/S-asymmetric partial reopening; tie/small-loss keeps E95 practical and makes E172/E174 only contrast sensors; worse-than-E101 demotes the damped partial-reopen family; E176 loss followed by E174 win says full Q2 reopening was public-real.
- 제출 전략: submit E176 first if using one risk-adjusted broad slot, then run `python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>`. Do not tune Q2 keep factors from that score.

### H172. The post-E95 plateau is a broad-signal plus hard-label-resolution law

- 상태: supported by E178; public feedback for E176 pending.
- 왜 그럴듯한가: E166/E169/E172/E174/E176 all have material focus-prior edges, so "no signal" is too simple. Yet E101's resolved public small loss and E162/E177 readability show that two to four high-swing cells can cover the full frontier edge.
- 맞다면: broad candidates should show expected deltas many times larger than the E95 public edge, while public-readable differences between safe siblings remain below selector resolution; current selector/proxy errors should be tens of times larger than the live edge.
- 틀리다면: a current validation object should rank E95/E101/E176 with error below `5e-6`, or a broad all-target candidate should beat E95 while increasing Q2/S3 and bad-axis exposure.
- 최소 실험: `analysis_outputs/e178_current_plateau_law_audit.py`.
- 관측: E166 focus edge is `-0.000332077` (`21.689x` E95 edge), E176 focus edge is `-0.000123384` (`8.059x` E95 edge), but E176 needs only `4` cells and E101 only `2` cells to swing an E95-over-mixmin edge. E98 selector p90 is `53.33x` that edge. E176-vs-E174 Q2 damping costs only `0.064x` E95 edge while reducing bad-axis and Q2/S3 exposure.
- 성공/폐기 기준: support strengthens if E176 lands in a tie/small-loss band where E177 explains the underresolution without spawning a new keep-factor variant. It weakens if E176 cleanly wins at readable scale, because then Q/S-asymmetric partial reopening was stronger than the hard-label-resolution warning.
- public LB 관측 반응: E176 `<=0.576276019` says target-amplitude calibration was the main remaining issue; E176 `0.576288330..0.576300366` preserves the plateau law; E176 `>0.576300366` demotes partial reopening; E176 `>0.576306641` closes the same-family expected-score lane.
- 제출 전략: no new E178 submission. Use E176 as the only current risk-adjusted public sensor and treat any follow-up as a worldview update, not scalar tuning.

### H173. E176 is visible-prior supported as a body but not certified at decisive-cell resolution

- 상태: partially supported by E179; hidden public labels remain unobserved.
- 왜 그럴듯한가: E176 was selected by broadness, visible-tail, bad-axis, and Q2-damping stress, but E178 showed that only `4` top cells can swing the E95-over-mixmin edge. A good local explanation must therefore separate full-body support from top-cell certification.
- 맞다면: E176's full body should have favorable visible-prior expected delta, while top public-decisive cells should look weak, ambiguous, or below target-matched null; Q2 damping should be supportable without implying another keep-factor scan.
- 틀리다면: the top4/top16/top33 decisive cells should be at least null-level or better under visible priors, or Q2 damping should look adverse under the same train-derived priors.
- 최소 실험: `analysis_outputs/e179_e176_critical_cell_visibility_audit.py`.
- 관측: full E176 body has visible-mean expected delta `-0.000050824`, visible win rate `0.999080`, and focus win rate `1.000000`. But top4 swing-weighted support is only `0.330699`, and top33 expected-flip support is `0.245771` versus null mean `0.335713` (`z=-1.983811`, `p_low=0.014667`). E176-vs-E174 Q2 damping is mildly supported: visible-mean delta `-0.000000191`, swing-weighted support `0.690495`, hard support rate `0.904762`.
- 성공/폐기 기준: support strengthens if E176 wins or ties in a way E177/E179 can decode without new tuning. It weakens if E176 hard-fails despite the full-body visible support, because then the visible-prior body is missing a public-negative axis. It is falsified as a certification claim if E176's top cells later prove public-favorable while local priors kept rejecting them.
- public LB 관측 반응: E176 win says the weak top-cell priors missed the hidden/public-tail realization; E176 tie/small loss says E179's top-cell warning was decisive; E176 worse than E101 demotes the partial-reopen family despite its full-body support.
- 제출 전략: no new E179 submission. Keep E176 as the only next broad expected-score sensor, decode with E177, and use E179 to decide whether a result was body validation or decisive-cell miss.

### H174. Visible priors explain some anchors but cannot certify frontier decisive cells

- 상태: supported by E180; does not certify E176.
- 왜 그럴듯한가: E179 made E176's top cells look weak, but the same visible-prior machinery may also understate successful known anchors. The real hidden structure might be that visible priors are useful body/tail diagnostics but poor top-cell selectors at frontier scale.
- 맞다면: known public winners should sometimes have weak visible top-cell support; visible-prior sign accuracy over known anchors should be mediocre; failed anchors may be explained when they are large/contaminated, while E95/E101-scale boundary remains unresolved.
- 틀리다면: known winners should have consistently high visible support and known failures should have consistently high adverse support, making E176's weak support a direct rejection signal.
- 최소 실험: `analysis_outputs/e180_known_anchor_decisive_cell_visibility.py`.
- 관측: E95-vs-mixmin public-positive top4 support is only `0.100896`; E101-vs-mixmin is also `0.100896`; mixmin-vs-a2c8 is `0.310904`. E176 top4 is `0.330699`, above known-winner mean `0.170898` and max `0.310904`. Failed E72 has high observed-adverse support, but E101-vs-E95 near loss has only `0.100896`. All-moved visible-prior sign accuracy across known anchors is `0.5`.
- 성공/폐기 기준: support strengthens if E176 feedback can be interpreted as hidden-tail underresolution rather than visible-prior certification. It weakens if future anchors show visible-prior top support consistently predicts public direction once more anchors are added.
- public LB 관측 반응: E176 win says weak visible top support is compatible with success, like E95. E176 tie/loss says visible priors still failed to resolve the exact boundary, not that their top-cell weakness alone was a veto.
- 제출 전략: no E180 submission. Keep E176 as sensor; do not prune or retune from visible top-cell support alone.

### H175. Current-anchor binary worlds are an adverse counterprior to E176

- 상태: supported by E181 as a counterprior; not a standalone selector.
- 왜 그럴듯한가: E180 only says visible priors are too weak to veto E176. A different latent representation, the binary hidden-label world pool that originally helped explain mixmin, may encode public-anchor constraints that visible priors miss.
- 맞다면: when existing binary worlds are reranked by all current public anchors, the lowest-residual worlds should give E176 mixed/adverse deltas versus E95, and may prefer another live branch such as E154/E144. E176 decisive-cell support should not become cleanly one-sided under those worlds.
- 틀리다면: current-anchor best binary worlds should also favor E176, or should be too noisy to distinguish E176 from E154/E144 in any coherent direction.
- 최소 실험: `analysis_outputs/e181_e176_binary_world_counterprior_audit.py`.
- 관측: best-5 current-anchor residual worlds give E176 mean delta `+0.000003920` versus E95 with negative rate `0.400`; best-10 gives `+0.000007442` with negative rate `0.300`. In contrast, E154 and E144 are negative in all best-5 worlds, averaging `-0.000051451` and `-0.000051445`. E176 best-5 top4 world support is `0.433633`, but top16 support is only `0.221275`, and best-10 top4 drops to `0.262881`.
- 성공/폐기 기준: support strengthens if a refreshed current-anchor binary-world pool keeps E154/E144 one-sided and E176 mixed/adverse. It weakens if regenerated worlds or E176 public feedback show that the inherited pool was stale or residual-rank overfit.
- public LB 관측 반응: E176 win weakens the inherited binary counterprior and says visible-body/Q2-underopen saw a public-real branch. E176 tie/loss strengthens H175, especially if E154/E144 later improve.
- 제출 전략: no E181 submission. Do not claim E176 is representation-wide best; treat it as a conditional visible-body sensor. Before replacing it with E154/E144, run a fresh current-anchor binary-world stress with explicit objectives.

### H176. Refreshed current-anchor binary worlds underidentify E176/E154/E144 signs

- 상태: supported by E182.
- 왜 그럴듯한가: E181's inherited world pool favored E154/E144, but its residuals were not frontier-precision and its worlds were generated before the current E95/E101 anchor structure was fully integrated. A truly current-anchor stress should either certify the repaired branch or expose that the inverse public-label problem remains underidentified.
- 맞다면: regenerated worlds should fit known public anchors at frontier scale while objective-pressure solves can still produce both favorable and adverse deltas for E176, E154, and E144. Strict residual-budget ranges should be hard or sparse because the frontier-scale hidden-label feasible region is thin.
- 틀리다면: at least one branch should become one-sided under all current-anchor scenarios, or E181's E154/E144 preference should survive as a refreshed certificate with adverse E176 pressure worlds only.
- 최소 실험: `analysis_outputs/e182_current_anchor_binary_world_refresh.py`.
- 관측: scenario fits have max absolute residuals `0.0000784319`, `0.0000513148`, and `0.0000762925`, all inside the raw05/A2C8 frontier-scale gap. Strict range incumbents appear in only `0.233` of candidate-direction rows. Objective-pressure worlds make E176/E154/E144 cross zero in `1.000` / `1.000` / `1.000` of scenarios, with E176 pressure spans around `-0.000421216..+0.000254123`, E154 `-0.00109286..+0.000923535`, and E144 `-0.000992245..+0.000838041`.
- 성공/폐기 기준: support strengthens if future public feedback shows both E176-family and repaired-branch outcomes are explainable only after adding a new hidden-label/cell selector. It weakens if a stronger exact MILP or new anchor collapses one branch to one-sided support without post-hoc tuning.
- public LB 관측 반응: E176 win means the visible-body branch realized one of the E182 favorable worlds. E176 loss plus E154/E144 win means the repaired-branch world was selected by public labels, not certified pre-public. E154/E144 loss after E176 loss would strengthen the broader underidentification/selector-resolution diagnosis.
- 제출 전략: E182 creates no submission and no priority inversion. Use E176 when the question is visible-body/Q2-underopen. Use E154/E144 only when deliberately testing repaired-branch validity with a decoder, not because E182 certifies expected improvement.

### H177. Visible priors are anti-selectors for E182 pressure branches

- 상태: supported by E183.
- 왜 그럴듯한가: E179/E180 already showed visible priors can support candidate bodies while failing at decisive-cell resolution. E182 then showed the live candidate signs are pressure-world underidentified. If the decisive pressure cells are hidden from train-derived priors, visible/subject/flank priors should not select the favorable branch.
- 맞다면: on the cells that differ between favorable pressure-min and adverse pressure-max worlds, visible/subject/flank priors should prefer the adverse max labels rather than the candidate-favorable min labels. This should hold across E176, E154, and E144 rather than being a single-candidate artifact.
- 틀리다면: at least one candidate branch, especially E176 because its full body is visible-supported, should have visible or subject/flank priors preferring the favorable pressure branch in most scenarios.
- 최소 실험: `analysis_outputs/e183_pressure_world_branch_anatomy.py`.
- 관측: visible-mean favorable-branch preference is `0.000` for E176/E154/E144 across scenarios. Subject and flank preference rates are also `0.000`. Support-gap coefficient-weighted means are high: E176 `0.797945`, E154 `0.973558`, E144 `0.888923`, so the disagreement is on candidate-driving cells. E176's global prior prefers the favorable branch in `1.000` of scenarios, but subject/flank/visible priors still prefer the adverse branch.
- 성공/폐기 기준: support strengthens if future public feedback can be explained by hidden pressure-cell labels that visible/subject/flank priors got wrong. It weakens if a new public-free representation, independent of these priors, predicts the pressure branch and also matches public feedback.
- public LB 관측 반응: E176/E154/E144 win despite E183 visible-prior rejection means the winning branch is hidden from current train-derived priors. A loss for all three would say the pressure-world favorable branches were feasible but not public-real.
- 제출 전략: no E183 submission. Treat visible priors as diagnostics and possible anti-selectors for pressure branches. If submitting E176/E154/E144, do it as an explicit worldview sensor with a decoder, not as visible-prior-certified expected improvement.

### H178. A shallow known-public metadata motif can select E182 pressure branches

- 상태: 반증됨 by E184.
- 왜 그럴듯한가: E183 only killed train-derived visible priors. Known public transitions include aggregate signs for mixmin, E95, E101, and E72, so their moved-cell metadata might encode a non-visible public-compatible motif.
- 맞다면: leave-one-pair and leave-one-family motif models should recover known public support-direction compatibility with stable polarity, and the same model should choose one coherent live pressure branch rather than flipping by feature set.
- 틀리다면: direct LOO/LOFO scores should be weak or polarity-inverted, and live branch preference should depend on fragile feature choices such as public-axis flags or swing.
- 최소 실험: `analysis_outputs/e184_public_anchor_motif_pressure_selector.py`.
- 관측: best direct pair-LOO model has sign accuracy `0.333` and AUC `0.425`; best direct family accuracy/AUC are `0.600` / `0.178`. Polarity-inverted pair accuracy can reach `1.000`, but family best-polarity accuracy is only `0.600`. Live pressure-branch preference is unstable: core and swing feature sets reject all favorable branches, while public-axis feature sets favor all three.
- 성공/폐기 기준: 폐기. A future version needs pre-specified polarity and stable family transfer, not only pair-level inversion after seeing results.
- public LB 관측 반응: if a future E176/E154/E144 public score matches one of the E184 feature-set branch preferences, it should not validate E184 unless the polarity/feature-set rule was fixed before feedback.
- 제출 전략: no E184 submission. Do not use shallow public-anchor metadata motif scores to rank E176/E154/E144.

### H179. Unconstrained known-LB pair movement structure can select live pressure branches

- 상태: 부분 반증 by E185.
- 왜 그럴듯한가: E184 may have failed because cell metadata was too shallow. Known public LB pairs contain richer movement-shape, support, bad-axis, and public-axis information, and the resolved E95/E101/mixmin boundary gives a real frontier-scale training target.
- 맞다면: leave-one-file and leave-one-pair decoders should preserve frontier ordering, especially E95/E101/mixmin/E72 edges, and branch preferences should be stable across feature sets. Reciprocal pairs should satisfy `P(A beats B)+P(B beats A) ~= 1`.
- 틀리다면: aggregate accuracy can look good while reciprocal orientation collapses or live branch preferences flip by feature set.
- 최소 실험: `analysis_outputs/e185_known_lb_pair_structural_decoder.py`.
- 관측: best file-LOO `shape_support_public_axis` has overall accuracy `0.811`, frontier accuracy `0.833`, and E95-edge accuracy `0.714`, but E95-edge reciprocity MAE is `0.081`. Best pair-LOO E95-edge accuracy reaches `0.786`, but reciprocity MAE is `0.146`. Branch preference flips: `shape_only` favors E144/E154 and rejects E176, while support/public-axis models favor E176.
- 성공/폐기 기준: 폐기 as an action-grade selector. A future pair decoder must fix reciprocal orientation before branch scores are usable.
- public LB 관측 반응: a future E176/E154/E144 score cannot validate E185 unless the same branch was selected by a reciprocity-healthy model before feedback.
- 제출 전략: no E185 submission. Use E185 only as evidence that pair-level signal exists and needs antisymmetric geometry.

### H180. Antisymmetric known-LB pair structure is a useful sensor-prior for E176

- 상태: supported but not certified by E186.
- 왜 그럴듯한가: Public LB pair ordering is antisymmetric by definition. If the E185 signal is real, forcing the representation to respect this geometry should improve frontier stress and stabilize live branch decisions.
- 맞다면: reciprocity error should collapse to zero, frontier/E95-edge stress should improve, and E176/E154/E144 branch choices should stop flipping across feature sets.
- 틀리다면: edge stress remains weak or branch preferences still flip after antisymmetry.
- 최소 실험: `analysis_outputs/e186_antisymmetric_pair_decoder.py`.
- 관측: best file-LOO has overall accuracy `0.795`, frontier accuracy `0.867`, micro accuracy `0.8125`, and E95-edge accuracy `0.857` with reciprocity MAE `0`. Pair-LOO `shape_only` reaches E95-edge accuracy `1.000`. E176 favorable pressure-min branch is selected in `3/3` scenarios across all feature sets, while E144/E154 are rejected in `3/3`.
- 반증 조건: the support-based model still misses the exact E95-vs-E101 boundary, predicting E101 over E95 with high confidence. If E176 public fails in the E177 demotion bands, E186 was a sensor-prior overfit to known anchors or a branch-level shortcut.
- public LB 관측 반응: E176 `<=0.576288330` would strengthen H180 and the Q2-underopen broad branch. E176 worse than E101 or mixmin would weaken H180 sharply and force a return to structural target design rather than pair-LB decoding.
- 제출 전략: if using one slot, submit `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as an E186-informed public sensor, not as a certified expected-score file.

### H181. The E95/E101 support-decoder miss is a removable family artifact

- 상태: 반증 by E187.
- 왜 그럴듯한가: E186 support models improve file-LOO frontier and E95-edge stress, but only the exact E95/E101 boundary is wrong. A single support family such as subject, flank, visible, or nearest could be the culprit.
- 맞다면: removing the culprit family should preserve support-model edge stress and E176 branch selection while restoring exact E95/E101 correctness.
- 틀리다면: all support-family ablations still invert E95/E101, and contribution mass is spread across multiple support families.
- 최소 실험: `analysis_outputs/e187_e95_e101_boundary_miss_anatomy.py`.
- 관측: shape-only and axis-no-support get E95/E101 correct, but every support-containing ablation tested gets it wrong. The adverse E95 contribution is distributed across flank, visible, subject, focus, nearest, global, and all-prior support families.
- 성공/폐기 기준: 폐기. This is not a one-family bug; support is a different frontier shortcut.
- public LB 관측 반응: E101's actual public `0.576300366` is exactly the sensor that kills the support-selector interpretation.
- 제출 전략: no support-decoder selected submission. Use support-decoder outputs only as hypothesis sensors with an explicit exact-boundary veto.

### H182. A small shape/support logit blend can repair the selector

- 상태: 반증 by E188.
- 왜 그럴듯한가: shape-only respects E95/E101 and selects E176, while support improves wider E95-edge stress. A low-alpha support prior might combine both.
- 맞다면: some `alpha > 0` should keep exact E95/E101 accuracy `1.0`, keep E176 favorable rate `1.0`, and raise file-LOO edge accuracy to at least `0.80`.
- 틀리다면: edge accuracy stays at shape-only level until exact E95/E101 flips.
- 최소 실험: `analysis_outputs/e188_shape_support_logit_blend_stress.py`.
- 관측: action-grade rows `0`. For all seven support variants, the best exact-boundary row is `alpha=0.0`; first exact-boundary failure appears at alpha `0.170..0.285`, before edge-band accuracy improves.
- 성공/폐기 기준: 폐기. Support cannot be smoothed into the selector without an external boundary veto.
- public LB 관측 반응: a future E176 public win would validate the branch sensor but still would not validate support as a general boundary selector unless exact E95/E101 remains explicitly handled.
- 제출 전략: no blend-generated submission. Keep E176 only as a predeclared sensor.

### H183. Support edge gain is a broad conditional frontier law

- 상태: 반증/정밀화 by E189.
- 왜 그럴듯한가: E186/E187 support models improve wider E95-edge file-LOO stress even though they miss exact E95/E101. If support captured a real conditional law, its wins over shape-only should appear across multiple frontier contexts and should provide a deployable gate.
- 맞다면: shape/support disagreements should show support rescues spread across E95/E101/mixmin/E72 and other frontier relations, and a non-file-identity structural gate should preserve E95/E101 while using support where it helps.
- 틀리다면: support rescues should concentrate in one anchor family, especially the already-failed E72 neighborhood, while shape-only wins should concentrate on the exact E95/E101 hardtail boundary.
- 최소 실험: `analysis_outputs/e189_shape_support_disagreement_atlas.py`.
- 관측: in the primary E95-edge file-LOO slice, support rescues `6` rows and shape-only wins `4` rows. Support rescues are E72-frontier-neighbor rows at rate `1.000`; shape-only wins are exact E95/E101 rows at rate `1.000`. A cheating file-identity gate can make E95-edge accuracy `1.000` and frontier accuracy `0.933333`, but it uses filenames, not a live structural selector.
- 성공/폐기 기준: broad-law version 폐기. The remaining supported version is narrower: support is an E72-contamination diagnostic. It may become useful again only if a public-free representation can identify E72-contaminated movement without file identity and without flipping E95/E101.
- public LB 관측 반응: a future E176 win would not validate support as a selector, because E189 shows support's known wins are E72-neighbor-specific. A future E72-like failure/win can validate or refute the contamination-diagnostic role.
- 제출 전략: no E189 submission. Keep `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` only as a broad/Q2-underopen plus shape-only-supported sensor.

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
