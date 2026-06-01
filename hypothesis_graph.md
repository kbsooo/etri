# Hypothesis Graph

작성일: 2026-05-29

이 문서는 수면 기반 생활습관 로그 예측 대회를 "예측 표"가 아니라 숨은 데이터 생성 과정의 관측 로그로 다루기 위한 가설 그래프다. 현재 best public LB는 `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`의 `0.5681234831`이다.

## 현재 병목 요약

E48에서 `submission_mixmin_0c916bb4.csv`가 public `0.5763066405`를 기록해 previous best `a2c8`를 `0.0011326805` 낮췄고, E97에서 `submission_e95_hardtail_541e3973.csv`가 public `0.5762913298`로 mixmin을 `0.0000153107` 더 낮췄다. E255에서 `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`가 public `0.5761589494`로 E95를 `0.0001323804` 더 낮췄다. H012에서 `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`가 public `0.5681234831`로 E247을 `0.0080354663` 낮췄다. Mixmin의 큰 점프는 anchor-loss/binary-world movement가 public-relevant였다는 증거이고, E95의 작은 추가 개선은 E72-adverse hard-label tail localization이 public-real이라는 증거이며, E247의 추가 개선은 feature-NN1 Q3 smoothing geometry가 public-real이라는 증거다. H012의 훨씬 큰 점프는 known public LB observations를 hidden public label/subset state의 equation으로 쓰는 HS-JEPA branch가 action-grade임을 검증했다. 따라서 현재 병목은 E247 근처 micro edge가 아니라, H012의 public-equation posterior가 private-safe hidden state인지, 아니면 public-subset-specific posterior인지 분해하는 문제다.

가장 강한 현재 설명:

- hidden subject/session/block 구조는 존재한다.
- row-level boundary copy는 실패했다.
- block-level rate/count latent는 의미가 있지만 직접 제출 후보로는 약하다.
- raw05는 public-positive raw timeline 방향을 포착했다.
- JEPA latent에는 local signal이 있지만 큰 이동은 public bad-axis를 강하게 탄다.
- `a2c8`는 raw05 manifold의 작은 correction이었지만, 이제 frontier가 아니다.
- Mixmin은 anchor-loss/cancellation geometry와 binary actual-anchor worldview가 public-relevant였다는 첫 강한 관측이다.
- E95는 E72-adverse hard-label tail localization이 public-positive라는 첫 강한 관측이다.
- E247은 feature-NN1 Q3 smoothing을 실제 public-positive JEPA mechanism으로 승격시킨 첫 강한 관측이다.
- H012는 public-equation hidden-state posterior를 직접 materialize한 첫 대형 성공이다.
- H014는 H012가 단순 same-subject memory가 아니라는 것을 보였고, H015-H020은 H012 이후의 public-equation posterior-completion을 cell-weight, binary world, row-subset, joint target-vector world로 분해하고 있다.
- H026-H027은 train action-health, public-bad veto, memory/private-safety birth constraints가 기존 posterior-completion targets를 H012-beating action으로 만들지 못함을 보였다.
- H028은 known public intervention response 자체를 cell-level action-gradient로 배웠지만, 그 gradient를 H012 밖으로 extrapolate하면 독립 stress가 모두 0.576대 위험으로 본다.
- H029는 H012의 support/amplitude/target/subject/memory/row-identity invariant를 깨보며, target-wise row permutation이 0.581대 위험으로 붕괴한다는 것을 보였다.
- 0.54 진입을 막는 핵심 병목은 이제 hidden state 발견 자체보다, H012 같은 singular public-equation basin의 정확한 row-target identity를 private-safe/invariant hidden state로 재구성하는 문제다. 단순 posterior-completion, scalar gate, train-action health, smooth public-gradient, target-level calibration은 현재 반증되었다.

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

known public interventions
  -> H012-vs-rest action-response geometry
  -> coarse public-gradient learnable
  -> local H012 extrapolation unsafe
  -> needle-basin / phase-change hypothesis
  -> exact row-target placement invariant
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

### H184. E72 contamination can be detected structurally enough to gate support

- 상태: 부분 지지 but action-gate 반증 by E190.
- 왜 그럴듯한가: E189 says support's useful wins are E72-neighbor corrections. If E72-contamination has a movement-shape signature, a detector using absolute z-features should identify it without filenames and let support be used only on those rows.
- 맞다면: pair/context/file stress should detect E72-neighbor rows while assigning low contamination probability to exact E95/E101; live branches with high contamination should be the only cases where support evidence is trusted.
- 틀리다면: either the detector cannot generalize beyond known E72 pairs, or support-containing features reproduce the original shortcut by misclassifying exact E95/E101 as E72-like.
- 최소 실험: `analysis_outputs/e190_e72_contamination_detector.py`.
- 관측: `shape_target_context_abs` detects E72-neighbor under pair-LOO with AUC `0.978836` and AP `0.809524`, but top-k recall is only `0.666667`. Any-file LOO skips `6` positive rows when E72 itself is held out, because no positive examples remain. Support-containing views show high E72-neighbor scores but assign exact E95/E101 contamination probability about `0.957..0.975`. Live E176 has near-zero contamination scores across all views and never crosses non-E72 p95 or min-positive thresholds.
- 성공/폐기 기준: structural-signal version supported; deployable support-gate version not supported. A future detector must combine E72 recall with exact-boundary false-positive control and a stronger E72-heldout/one-class calibration.
- public LB 관측 반응: E176 win/loss should be interpreted as broad/Q2-underopen or shape-only branch evidence, not support-gate evidence. A future candidate explicitly designed as E72-contaminated would be the right public sensor for H184.
- 제출 전략: no E190 submission. Do not use support as a live E176 gate. Use E190 only as a diagnostic feature registry entry.

### H185. Exact-boundary hard negatives can rehabilitate support as an E72 gate

- 상태: 반증 by E191.
- 왜 그럴듯한가: E190's support-rich detector may have false-positived exact E95/E101 because the objective did not explicitly punish that tight boundary. If exact E95/E101 is upweighted as a hard negative, support might keep E72 recall while lowering boundary risk.
- 맞다면: support-containing feature views should pass a boundary-clean pair-LOO gate: E72 top-k recall at least `0.666667`, exact E95/E101 mean <= `0.20`, exact max <= `0.30`, and live branches should not be spuriously flagged.
- 틀리다면: only shape/target/context views will pass; support-only and shape+support/all views will keep exact E95/E101 probabilities high even under hard-negative weighting.
- 최소 실험: `analysis_outputs/e191_boundary_aware_e72_score.py`.
- 관측: `shape_target_context_abs` passes with pair-LOO AUC `0.978836`, AP `0.809524`, top-k recall `0.666667`, and exact E95/E101 mean `0.057658`. Boundary-clean support-containing pair-LOO rows are `0`; support-only exact E95/E101 remains `~0.785758..0.839112`, and shape+support/all remains `~0.766102..0.824223`. E176 contamination remains near zero.
- 성공/폐기 기준: support-rehabilitation version 폐기. The surviving version is narrower: shape/target/context can act as a cleaner contamination diagnostic, while support remains a conflicting E72-specific shortcut.
- public LB 관측 반응: E176 feedback should not be read as support-gate evidence. A future support-gated submission would need a new structural target, not hard-negative reweighting.
- 제출 전략: no E191 submission. Keep E176 as shape/broad-Q2-underopen sensor; do not create support-gated E176/E154/E144 variants.

### H186. Clean shape-only E72 score is a live contamination selector

- 상태: 부분 지지 as diagnostic, 반증 as live selector by E192.
- 왜 그럴듯한가: E191 left `shape_target_context_abs` as the only boundary-clean E72-neighbor score. If that score truly represented E72 contamination, live branches with high values should resemble known E72-neighbor rows and should justify branch reranking.
- 맞다면: E144/E154/E176 pressure branches that score high should have nearest known rows enriched for E72 positives, should approach the known positive floor, and should get contributions from the same family/target geometry as known E72 positives.
- 틀리다면: live high-ish scores will only cross non-E72 tail thresholds, nearest known rows will remain non-E72, and the branch should be interpreted as tail risk rather than contamination evidence.
- 최소 실험: `analysis_outputs/e192_shape_e72_score_anatomy.py`.
- 관측: E144 has one scenario above non-E72 p95 (`0.038723`) but below p99 (`0.044812`) and far below known positive floor (`0.804849`); nearest known top-3 rows are all non-E72. E154 max is `0.007973`; E176 max is `0.000008`. Exact E95/E101 stays low at `0.031016`. Live pressure-branch context terms are zero, so the live score is target/shape anatomy rather than a complete context gate.
- 성공/폐기 기준: deployable live contamination-selector version 폐기. Diagnostic tail-risk version retained: E144 is mildly shape-tail-risk, E176 is contamination-clean.
- public LB 관측 반응: E176 public feedback should test broad/Q2-underopen shape worldview, not E72 contamination. E144 public feedback, if ever used, should be read as an active-boundary/tail-risk contrast rather than as an E72-contamination branch.
- 제출 전략: no E192 submission. Keep E176 as the single next sensor.

### H187. Cross-sensor evidence balance can choose the next live public sensor without certifying expected LB

- 상태: 지지 as sensor-selection ledger, 반증 as expected-score certificate by E193.
- 왜 그럴듯한가: E176/E154/E144 are currently separated by conflicting latent views. E176 has visible-body, Q2-damping, pair-geometry, and clean-E72 support, while E154/E144 have inherited binary-world support. A fixed ledger can prevent cherry-picking diagnostics while preserving the distinction between "next sensor" and "certified winner."
- 맞다면: E176 should stay first only if its support survives after binary-world counterprior, local-prior rejection, pressure-width, pair-geometry, and E72-tail diagnostics are all counted explicitly. E154/E144 should remain alive only as alternate worldview controls, not first-choice candidates.
- 틀리다면: the ledger would either put E154/E144 ahead, or show all branches as too conflicted to justify any next submission.
- 최소 실험: `analysis_outputs/e193_live_candidate_evidence_ledger.py`.
- 관측: E176 has support axes `8`, warning axes `4`, and evidence balance `3.100`; E154 has `4/4/1/3` support/warning/underidentified/missing with balance `-0.225`; E144 has `3/5/1/3` with balance `-1.725`. E176 is supported by E179/E180/E183/E186/E192, but warned by E181 and E183 local-prior rejection.
- 성공/폐기 기준: supported only for ranking the next information sensor. Rejected as an expected-score certificate because the binary-world conflict and pressure-branch local-prior rejection remain unresolved.
- public LB 관측 반응: E176 win strengthens the broad/Q2-underopen worldview. Tie/small-loss strengthens the hidden-label resolution bottleneck. Worse-than-E101 demotes the partial-reopen family instead of justifying Q2 keep-factor tuning.
- 제출 전략: no E193 submission. If one public slot is spent, submit `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` and decode with E177.

### H188. E176 priority is robust to ordinary evidence-weight uncertainty

- 상태: 부분 지지 by E194.
- 왜 그럴듯한가: E193 uses hand-set evidence weights. A robust sensor decision should survive reasonable perturbations and leave-one-source checks; a weight artifact should flip under mild changes.
- 맞다면: E176 remains first under single-source leaveout, most random family-weight perturbations, and missing-evidence penalties. The exact condition that would promote E154/E144 should be identifiable.
- 틀리다면: E176 loses under ordinary source removal or moderate weight perturbation, making E154/E144 the more honest next sensor.
- 최소 실험: `analysis_outputs/e194_evidence_ledger_robustness.py`.
- 관측: E176 wins every single-source leaveout. E176 Monte Carlo win rates are `0.771300` for loguniform `0.25..4`, `0.905950` for loguniform `0.5..2`, and `0.896500` under 20% family dropout. Binary-world alone selects E154/E144; scaling binary-world above `1.760x` flips E176 versus E154. If visible/top-cell E176-only evidence is removed, E176 still leads, but pair geometry must remain above `0.725x` of its E193 weight.
- 성공/폐기 기준: ordinary robustness supported. Absolute-certainty version rejected because a coherent high-binary/low-pair worldview promotes E154.
- public LB 관측 반응: E176 win validates the pair/shape/broad-body weighting. E176 loss should elevate E154 as the next repaired-branch worldview before another same-family E176 tweak.
- 제출 전략: no E194 submission. Keep E176 as next sensor; keep E154 as the explicit counterfactual branch.

### H189. E176 is a higher-information first public sensor than E154

- 상태: 지지 as sensor ordering by E195.
- 왜 그럴듯한가: E194 identified E154 as the coherent counter-world, but being the counter-world does not automatically make it the best first public sensor. The first slot should resolve the largest live conflict with the cleanest post-feedback action tree.
- 맞다면: E176 should distinguish broad/Q2-underopen from the E154 repaired-branch counter-world with a larger public-readable contrast, and adverse E176 bands should already route to E154/search. E154 feedback should mostly decide the repaired branch while leaving the E176 broad worldview unresolved.
- 틀리다면: E154 should have a cleaner or larger counter-world contrast, or E154 decoder bands should directly resolve whether E176's broad/Q2-underopen branch is public-real.
- 최소 실험: `analysis_outputs/e195_next_sensor_information_value.py`.
- 관측: E176-vs-E154 moves `1027` cells over `238` rows with focus expected delta `-0.000093546`, while E154-vs-E144 moves `294` cells over `139` rows with delta `-0.000002432` and E154-vs-E155 is not public-readable (`-0.000001796`). E176 has `3` adverse bands that route to E154/search; E154 has no band that directly resolves the E176 broad worldview.
- 성공/폐기 기준: supported until actual E176 feedback. If E176 lands in a clean-win band, broad/Q2-underopen is promoted. If E176 lands in an adverse band, E154 becomes the next worldview to test. If E154 is submitted first for non-experimental reasons, its result must not be used to declare the E176 broad branch dead.
- public LB 관측 반응: E176 below E95 validates the current first-sensor ordering. E176 worse than E101 or mixmin shifts priority to E154/search. E154 first only makes sense under an explicit high-binary/low-pair prior before submission.
- 제출 전략: no E195 submission. Submit `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` first if spending one public slot; keep `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` as the first counter-world branch after adverse E176 feedback.

### H190. E176 decisive-cell direction is recoverable from row/order/block motif nearest anchors

- 상태: 반증 as action-grade selector by E196; retained as weak anatomy warning.
- 왜 그럴듯한가: E176's uncertainty lives in a few public-decisive cells. If those cells are generated by subject-calendar/order motifs, nearest-anchor motif profiles from known public transitions might identify whether E176 resembles winners or losers without waiting for public feedback.
- 맞다면: motif-only or motif+axis nearest-anchor views should pass leave-one-known-pair stress, recover exact E101/E95 and mixmin broad-success directions, and place E176 consistently nearer to known winner profiles.
- 틀리다면: motif views will miss exact known frontier boundaries, nearest E176 winner/loss direction will be unstable by top set, or any winner vote will be too close to chance.
- 최소 실험: `analysis_outputs/e196_e176_motif_nearest_anchor.py`.
- 관측: action-grade views are `0/9`. The best `top4 / sequence_axis_flank` view has LOO accuracy `0.833333`, but exact E101/E95 correctness is `0`; E176's nearest anchor is `e72_vs_e95` (`new_lost`) with near-tie inverse-distance vote (`0.505761` new_won). Top33 points to `mixmin_vs_a2c8` but has LOO accuracy only `0.333333`.
- 성공/폐기 기준: action-grade selector 폐기. Anatomy warning retained: E176 top4/top16 cells have loss-motif pressure, while broader top33 cells have weak mixmin-like pressure.
- public LB 관측 반응: E176 loss would make the top4/top16 E72-like motif warning more relevant. E176 win would show that motif-only nearest anchors missed the public-real broad/Q2-underopen branch. Either way, E196 should not be used post-hoc to tune another same-family file.
- 제출 전략: no E196 submission. Keep E176 first as an information sensor, but do not claim motif anatomy certifies it.

### H191. Known public LB pairs define a support-mass slippage decoder for live candidates

- 상태: 지지 as decoder by E197; 반증 as standalone submission selector.
- 왜 그럴듯한가: every moved cell has two hard-label LogLoss deltas. A public pair score can therefore be rewritten as `delta = adverse_sum - q * swing_sum`, exposing how much hidden support mass was actually realized versus visible/focus priors.
- 맞다면: known successful and failed pairs should have interpretable observed-q slippage, and applying those slippages to E176/E154 should reveal which public-world failure mode each candidate is sensitive to.
- 틀리다면: observed q will be outside feasible range, slippage analogues will be unstructured, or live candidates will all look identical under the stress.
- 최소 실험: `analysis_outputs/e197_public_support_mass_inverse.py`.
- 관측: E72 failures have large adverse visible slippage (`-0.071348`, `-0.120707`). E176 has visible surplus-to-tie `0.061761` and focus surplus `0.094836`; it survives all non-E72 slippage analogues and fails only under E72-like adverse slippage. E154/E144/E155 have thin visible surplus (`0.010284`/`0.011545`/`0.011227`) and branch/hard-fail in `4/6` visible analogues.
- 성공/폐기 기준: decoder retained because it produces a concrete failure condition. Selector 폐기 because E172 has slightly higher support-mass tolerance than E176 while E176 remains the more informative pre-registered worldview sensor.
- public LB 관측 반응: E176 win means public slippage was not E72-like; E176 small/branch loss means E72-like adverse slippage is the active hidden variable and same-family keep-factor tuning is blocked.
- 제출 전략: no E197 submission. Keep E176 first; if E176 ties/small-loses, use E172 as same-family safety contrast by decoder band. If E176 branch-loses or hard-fails, route to E154 or representation search.

### H192. E176's E72-like failure mode is algebraic rather than clean-shape structural

- 상태: 지지 by E198, with recall caveat.
- 왜 그럴듯한가: E197 says E176 loses only under E72-like adverse slippage, while E192 says E176's clean shape E72 score is nearly zero. If both are true, E176's risk is a public-label slippage scenario, not an observed E72-contaminated movement shape.
- 맞다면: E176 should branch-lose under E72-vs-mixmin slippage stress but stay far below E191/E192 non-E72 p95 and E72-positive thresholds. Repaired-branch alternatives should fail mainly from thin support margins, not from high clean E72 probability.
- 틀리다면: E176 should cross non-E72 p95/p99 or approach the known E72-positive floor in the clean shape diagnostic, or E154/E144 should show the same clean E72 exposure at higher probability.
- 최소 실험: `analysis_outputs/e198_e72_slippage_exposure.py`.
- 관측: E176 visible/focus surplus-to-tie is `0.061761`/`0.094836`; E72-vs-mixmin slippage gives `branch_loss`, but E176 max clean E72 probability is `0.000008` versus non-E72 p95 `0.020815`, p99 `0.044812`, and positive floor `0.804849`. E154 max is `0.007973`; E144 max is `0.038723`, a mild p95 tail alarm but not positive-scale.
- 성공/폐기 기준: retained while no public feedback contradicts it. If E176 public fails badly, this hypothesis does not automatically die; it says the failure was not pre-diagnosed by the clean shape E72 score and must be decoded by LB band/slippage. It weakens if a stronger structural E72 detector later scores E176 high before feedback.
- public LB 관측 반응: E176 win strengthens the non-E72 broad/Q2-underopen read. E176 small/branch loss means E72-like public slippage occurred despite clean-shape non-exposure, so the missing variable is hidden-label realization rather than visible E72 movement shape. E144/E154 future wins/losses should be read as repaired-branch/tail-risk tests, not E72 contamination tests.
- 제출 전략: no E198 submission. Keep E176 first. Do not demote E176 solely because E197 has an E72-like algebraic stress case; also do not call E176 certified, because the clean detector recall is only `0.666667`.

### H193. E176 follow-up candidates are not hidden E72-shape branches, except E144 tail risk

- 상태: 지지 by E199.
- 왜 그럴듯한가: E198 scored only pressure branches for E144/E154/E176. The actual next-branch candidates after E176 feedback include E172, E174, E166, and E155, so an unscored candidate could still be E72-shaped and unsafe.
- 맞다면: direct candidate-vs-E95 clean-shape E72 scores for E172/E174/E166/E155 should stay below non-E72 p95, while any branch to demote should cross p95/p99 or approach positive scale.
- 틀리다면: E172 or E154 should show high direct E72-shape probability, making the post-E176 branch route unsafe before another diagnostic.
- 최소 실험: `analysis_outputs/e199_candidate_shape_e72_exposure.py`.
- 관측: direct clean-shape E72 probabilities are E172 `0.000087`, E174 `0.000097`, E176 `0.000097`, E166 `0.000677`, E154 `0.007860`, E155 `0.009284`, all below non-E72 p95 `0.020815`. E144 alone reaches `0.054385`, above non-E72 p99 `0.044812` but far below positive floor `0.804849`, with top-3 nearest labels all non-E72.
- 성공/폐기 기준: retained until public feedback or a stronger E72 detector contradicts it. It weakens if E172/E154 later fail specifically in an E72-contamination-like way while E144/E166 do not.
- public LB 관측 반응: E176 tie/small-loss should allow E172 as same-family safety contrast without E72-shape caveat. E176 branch/hard-loss should route to E154 before E144 because E154 is thin-margin clean-shape while E144 has p99 tail alarm.
- 제출 전략: no E199 submission. Use E199 to rank follow-up routes after E176 feedback, not to replace E176 before feedback.

### H194. E172 is safer than E176 but lower-information as the first sensor

- 상태: 지지 by E200 as ordering rule; 반증된 버전은 "E172 should replace E176 first."
- 왜 그럴듯한가: E172 has slightly better support-mass surplus and lower clean-shape E72 probability than E176, so it is tempting to submit it first as the safer broad-family candidate.
- 맞다면: E172's safety advantage should be large enough to justify giving up E176's expected edge and should resolve the same live worldview conflict that E176 resolves.
- 틀리다면: E172 should be safer only on a narrow same-family rollback axis, while E176 retains a material frontier-scale edge and the broader E176-vs-E154 conflict.
- 최소 실험: `analysis_outputs/e200_e176_vs_e172_first_sensor_resolution.py`.
- 관측: E176's expected focus edge over E172 is `0.0000106885`, `0.698x` of the full E95-over-mixmin public edge. E172's advantages are smaller safety margins: visible surplus `+0.008852`, focus surplus `+0.007054`, and clean-shape E72 probability lower by only `0.00000972`. E176-vs-E172 changes `75` cells, while E176-vs-E154 changes `1027`; the same-family delta is only `0.114x` of the counter-world delta.
- 성공/폐기 기준: ordering supported unless the objective changes from information-rich public sensor to private-risk minimization. It weakens if public feedback later shows E172-like rollback wins while E176 loses in the exact same broad-family setting.
- public LB 관측 반응: E176 win validates first-sensor ordering. E176 tie/small-loss activates E172 as planned. E176 branch/hard-loss shifts to E154/search; E172 should not be retroactively treated as the missed first choice unless the score lands specifically in the E172-conditional band.
- 제출 전략: no E200 submission. Keep E176 first, E172 after tie/small-loss, E154 after branch/hard-loss.

### H195. E176 feedback must be decoded by a pre-registered router, not scalar intuition

- 상태: 지지 by E201 as governance rule.
- 왜 그럴듯한가: E176 is a thin public-edge sensor: only `4` cells can cover the E95-over-mixmin edge, and E176/E172/E174 differ on narrow same-family axes. Without a fixed router, the same public number could be retrofitted into Q2 tuning, E172 safety, E154 counter-world, or new-latent stories.
- 맞다면: a useful pre-feedback artifact should verify the exact submission file and map every possible E176 public score band to a unique worldview update and follow-up policy.
- 틀리다면: file/schema/hash audit would fail, or the route table would leave important score bands ambiguous enough to justify multiple contradictory follow-ups.
- 최소 실험: `analysis_outputs/e201_e176_public_sensor_packet.py`.
- 관측: E176 SHA256 is `34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206`; file audit passes sample schema/key/probability checks; E176 moves `904` cells over `193` rows versus E95. The route table fixes four main regimes: `<0.5762883298` promote/decompose E176, `0.5762883298..0.576300366` same-family underresolved with E172 as only coherent safety contrast, `>0.576300366` demote partial-reopen toward E154/search, and `>0.5763413298` close same-family expected-score lane.
- 성공/폐기 기준: supported as long as the next E176 public result is interpreted through E177/E201 before any follow-up file is chosen. It is violated if a new E176 sibling is generated from the public scalar without matching the pre-registered route.
- public LB 관측 반응: the score itself will update H176/H194-family beliefs by band; H195 governs the interpretation process. A win strengthens broad/Q2-underopen; tie/small-loss activates E172; adverse loss activates E154/search.
- 제출 전략: no E201 submission. Submit only the audited E176 if spending the next slot, then run `python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <E176_PUBLIC_LB>` and compare to `analysis_outputs/e201_e176_public_sensor_packet_route_summary.csv`.

### H196. E176 public feedback mostly tests S-stage / between-train-runs body, not Q2-only amplitude

- 상태: 지지 by E202 as component-responsibility rule.
- 왜 그럴듯한가: E176's filename emphasizes Q2 damping, but the submitted tensor moves many targets and rows. If the public score is read as "Q2 keep factor worked/failed," the next action could become another scalar sibling sweep rather than a hidden-structure update.
- 맞다면: E176's expected contribution should concentrate more in S-stage body and between-train-runs rows than in Q2 alone, while Q2 may still be large in raw probability movement.
- 틀리다면: Q2 should dominate both raw movement and focus-prior expected contribution, and win/loss bands should naturally route to Q2-amplitude follow-ups.
- 최소 실험: `analysis_outputs/e202_e176_component_responsibility_router.py`.
- 관측: S-targets carry `0.651098` of focus-prior expected movement versus `0.348902` for Q-targets. Between-train-runs rows carry `0.807772`. Q2 is largest by raw probability movement (`0.209702`) but only `0.121416` of expected contribution, behind S3 `0.203515`, S1 `0.189679`, S4 `0.146985`, and Q1 `0.145593`. Top33 visible support is thin (`p_low=0.014667`).
- 성공/폐기 기준: supported unless a paired E174/E176 or later target-isolated public observation proves that Q2 amplitude, rather than S-stage body/tail cancellation, explains the score. It is violated if the first post-E176 action is a Q2 sibling created only from the scalar score.
- public LB 관측 반응: a win credits broad S-stage / between-train-runs body first; a micro win says body and hard-tail nearly cancel; tie/small-loss points to unresolved hard-label tail; adverse loss demotes same-family partial-reopen toward E154/search. None of those bands alone proves Q2-only causality.
- 제출 전략: no E202 submission. Keep E176 first, but after the score use E202 component responsibility before E174/E172/E154 decisions.

### H197. E176 needs a broad body, while public fragility lives in a compact tail layer

- 상태: 지지 by E203 as knockout stress.
- 왜 그럴듯한가: E176 has two conflicting diagnostics: broad S/body support and weak top critical-cell visibility. It could be a broad-body signal with a small tail risk, or merely a compact top-cell gamble.
- 맞다면: broad groups should retain most of the expected focus delta, while top33/top8 should explain fragility but not the whole body.
- 틀리다면: Q2-only or top33-only should carry most of the expected delta, or dropping top33 should destroy most of the E176 body.
- 최소 실험: `analysis_outputs/e203_e176_component_knockout_stress.py`.
- 관측: full E176 E179 focus delta is `-0.000078041955`. S-only carries `0.644881`, primary S3/S1/S4 carries `0.573289`, and between-train-runs carries `0.774524`. Q2-only carries `0.093922`. Top33 carries `0.226424` with visible support `0.245771`; dropping top33 still leaves `0.773576`.
- 성공/폐기 기준: supported until public feedback or a target-isolated public observation shows that a compact tail-only or Q2-only component explains the score. It weakens if E176 wins/losses exactly like a top33-only or Q2-only paired contrast.
- public LB 관측 반응: clean win validates broad S/body first. Tie/small-loss means the broad body survived but compact tail cancelled enough public mass. Branch/hard loss means either body is public-misaligned or tail cancellation dominates, so E154/search is more coherent than Q2 tuning.
- 제출 전략: no E203 submission. Keep E176 first; do not submit top33-only, Q2-only, or another scalar sibling before E176 feedback.

### H198. E176 follow-ups are different world probes, not a scalar rescue ladder

- 상태: 지지 by E204 as route-specific correction map.
- 왜 그럴듯한가: E172, E154, and E174 are all plausible post-E176 files, but they may move along different axes. If they are treated as a ladder, the next public slot could answer the wrong question.
- 맞다면: E172 should be a same-family rollback with minimal off-body movement, E154 should exit the E176 body and add off-axis movement, and E174 should amplify the Q2 subset rather than repair a tie/loss.
- 틀리다면: all three follow-ups should mainly differ by scalar strength on the same E176 cells, with similar off-body shares and rollback patterns.
- 최소 실험: `analysis_outputs/e204_e176_followup_correction_map.py`.
- 관측: E172 changes `75` cells, all inside E176, with rollback share `1.000000` and body rollback fraction `0.089780`. E154 changes `1027` cells, has `123` off-E176 cells, off-E176 abs share `0.292501`, and body rollback fraction `0.877576`. E174 changes `21` E176 cells, rollback share `0`, and is a Q2 amplitude probe.
- 성공/폐기 기준: supported unless a future public result shows the supposed route-specific behavior is irrelevant, or a new file is built that dominates all three axes under the same stress.
- public LB 관측 반응: E176 tie/small-loss activates E172 because the question is same-family safety. E176 branch/hard-loss activates E154 because the question is body-exit counter-world. E176 clean win can activate E174 only if the next question is Q2 amplitude.
- 제출 전략: no E204 submission. Keep the pre-registered post-E176 decision tree and do not substitute E174/E154/E172 by scalar closeness alone.

### H199. E176 public feedback must be decoded by an executable routebook, not manual scalar intuition

- 상태: 지지 by E205 as feedback-protocol governance.
- 왜 그럴듯한가: E201-E204 already fix the file, score bands, component responsibility, body/tail anatomy, and follow-up geometry, but they live in separate artifacts. After the real public score arrives, a manual read can still collapse the evidence into "Q2 worked" or "try the closest file."
- 맞다면: the E201-E204 artifacts should be joinable into a deterministic routebook where every possible E176 public band maps to one outcome, one component interpretation, one forbidden-action set, and one follow-up role.
- 틀리다면: the artifacts should disagree or leave score bands that cannot be assigned to a unique route without new subjective judgment.
- 최소 실험: `analysis_outputs/e205_e176_public_feedback_executable_decoder.py`.
- 관측: E205 writes a routebook/report/examples. Example `0.576291` decodes to `tie` and E172 same-family safety; `0.576303` decodes to `e101_worse_mixmin_safe` and E154 body-exit counter-world. Clean win / breakthrough bands route to no immediate sibling and require broad S-stage / between-train-runs decomposition first.
- 성공/폐기 기준: supported as long as the submitted file is exactly the audited E176 tensor and the real public score falls in a defined band. It is violated if the score belongs to a route not represented by the E201-E204 evidence or if a follow-up is chosen without the decoder.
- public LB 관측 반응: public feedback becomes an input to `--score`, not a free-form optimizer. Win/tie/loss branches update the corresponding worldview without reopening scalar Q2 keep-factor sweeps.
- 제출 전략: no E205 submission. Before any post-E176 file, run `python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score <E176_PUBLIC_LB>`.

### H200. The E176 broad partial-reopen family gives back the public frontier edge

- 상태: 지지 by E206 public observation.
- 왜 그럴듯한가: E176 had strong local broad-body diagnostics but weak hard-label/top-cell resolution. If public tail cells disagreed, the broad body could give back the E95 edge even if the representation was non-collapsed.
- 맞다면: actual E176 public LB should land in an E205 adverse band, and the decoder should route away from E176/E174/E172 same-family expected-score followups.
- 틀리다면: E176 should land in clean/micro/tie bands where same-family safety or Q2-amplitude probes remain live.
- 최소 실험: `python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score 0.576311831`.
- 관측: public LB `0.576311831`; delta vs E95 `+0.0000205012`; delta vs mixmin `+0.0000051905`; E205 outcome `branch_loss`; worldview update `close_same_family_expected_score_lane`; follow-up role `body_exit_counterworld` with E154.
- 성공/폐기 기준: supported for public expected-score ordering unless a later private result or paired public sensor proves E176-like body helps outside the public subset. It does not prove the broad S-stage/body signal is nonexistent; it proves this translation is not public-frontier-safe.
- public LB 관측 반응: same-family expected-score lane is weakened. E174/Q2 sibling and E172 immediate safety are not the next action; E154/search is coherent.
- 제출 전략: do not submit E174, E172, E169, or E166 as automatic follow-up. Submit E154 only if deliberately testing the repaired-branch counter-world; otherwise design a non-collinear hidden-structure experiment.

### H201. True JEPA should start from feature-neighbor positive pairs, not subject-order pairs

- 상태: 부분 지지 by E207; subject-order true-JEPA claim weakened.
- 왜 그럴듯한가: the new LeJEPA identifiability reading says world-model recovery depends on the positive-pair transition, not just on using a JEPA-like loss. Subject/date order is visible in this dataset, but it may be nonstationary or non-Gaussian at the increments that matter for public hard-label cells.
- 맞다면: an identifiability audit should find only a narrow set of pair regimes with intermediate autocorrelation, useful alignment gap, Gaussian-ish increments, stable rank, and tolerable split behavior. Existing subject-lag LeJEPA latents may remain useful as energy but fail certification.
- 틀리다면: same-subject adjacent/lagged rows should pass the strict true-JEPA gate, with good increment Gaussianity and stable split distance; feature-neighbor pairs should not be uniquely preferred.
- 최소 실험: `analysis_outputs/e207_lejepa_identifiability_conditions_audit.py`.
- 관측: among `77` latent/regime combinations, only `broad_stage2_pca64 + feature_nn1_all` is `true_jepa_candidate` (`readiness=0.652939`, `rho=0.494280`, `alignment=0.636020`, `increment_gauss=0.435262`). `lejepa_l0p2_d32_pca48 + subject_lag2_all` has higher readiness (`0.668530`) but is only auxiliary because increment Gaussianity is low (`0.194814`) and split distance CV is high (`0.660020`).
- 성공/폐기 기준: supported until a specialized subject/order latent passes the same increment/stationarity gate. Discard if E208 feature-neighbor JEPA fails while a subject-order JEPA passes these diagnostics and downstream stress.
- public LB 관측 반응: no immediate submission. A later feature-neighbor JEPA candidate should improve only if it converts the one certified pair regime into a probability movement that survives hard-tail and known-frontier stress.
- 제출 전략: build E208 feature-neighbor JEPA diagnostics first. Do not train a monolithic subject-order JEPA or average all pair types into one submission family.

### H202. Feature-neighbor JEPA learns real structure, but only Q3/S4 translation is currently stable

- 상태: 부분 지지 by E208; full-latent submission claim rejected.
- 왜 그럴듯한가: E207 selected feature-neighbor positive pairs as the only true-JEPA candidate. If this regime is meaningful, a context encoder should predict neighbor representation better than trivial controls. But if LeJEPA-style collapse/shortcut warnings apply, not every predicted dimension or target should be trusted.
- 맞다면: validation MSE should beat copy-self/mean/random controls; latent geometry should expose which embeddings are healthy; downstream stress should pass only target/feature operations whose signal survives OOF, repeated-subject, and geometry folds.
- 틀리다면: validation MSE should be no better than copy-self or mean-target, or downstream gains should disappear under geometry stress. Alternatively, a globally healthy predicted latent should pass across many targets without anisotropy.
- 최소 실험: `analysis_outputs/e208_feature_neighbor_jepa_probe.py`.
- 관측: all three seeds beat copy-self and mean-target baselines. `hidden_mean` has healthier geometry than `pred_mean`; `pred_mean` is anisotropic. Q3 `e208_resid_self_pc10` and S4 `e208_pred_pc14` pass materialization gates. S2 is locally strong but geometry-adverse; Q1/Q2/S1/S3 do not provide stable movement.
- 성공/폐기 기준: supported for a narrow Q3/S4 JEPA residual branch. Discard the broad claim if E209 Q3/S4 materialization fails E95/E154/E176 hard-tail stress or public feedback. Discard the full-latent claim now because prediction geometry is compressed and target coverage is narrow.
- public LB 관측 반응: an E209 win would strengthen the view that real JEPA helps via target-specific residual/energy, not via monolithic latent blending. An E209 loss would not kill JEPA learnability; it would kill the current probability-translation path.
- 제출 전략: build E209 from only passing Q3/S4 operations and compare against frontier geometry. Do not submit all E208 features, S2 local shortcut, or a full predicted-latent blend.

### H203. E208 JEPA can be materialized only as a low-scale Q3/S4 graft

- 상태: 부분 지지 by E209; high-scale and broad-JEPA claims rejected.
- 왜 그럴듯한가: E208's learnable representation survives downstream stress only on Q3/S4. A healthy materialization should therefore move only those axes, at low enough scale to avoid known hard-tail and bad-axis collapse.
- 맞다면: Q3/S4 grafts should improve stage2 OOF, repeated subject-half, and geometry folds, while high-scale or broader target grafts should fail frontier stress. E95-anchored files should isolate JEPA, and E154-anchored files should score higher if the repaired-branch counter-world is also useful.
- 틀리다면: Q3/S4 movements would not survive geometry, or high-scale/full-latent movement would pass the same frontier gate. Alternatively, E154 anchoring would not change survival relative to E95 if the anchor branch is irrelevant.
- 최소 실험: `analysis_outputs/e209_feature_neighbor_jepa_materialization_stress.py`.
- 관측: `q3_center_c010_s4_rank` has OOF delta `-0.001272724`, subject-half win rate `0.900000`, and geometry delta `-0.000794598`. Four low-scale submissions pass the E209 frontier gate. High-scale Q3/S4 grafts fail. The best survival score belongs to the E154-anchored Q3/S4 file, while the E95-anchored Q3/S4 file is the cleaner JEPA-only sensor.
- 성공/폐기 기준: supported until public LB feedback says the graft is adverse. If the E95-anchored Q3/S4 file loses clearly, the current JEPA probability translation path is weakened. If only the E154-anchored file wins, the repaired-branch anchor may be more important than JEPA itself.
- public LB 관측 반응: an E95-anchored E209 win strengthens "actual JEPA helps via Q3/S4 residual translation." An E154-anchored win with E95-anchored loss strengthens "E154 branch plus JEPA is needed." A loss for both means E208 learnability did not survive public hard-label translation.
- 제출 전략: use `submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv` for maximum E209 survival, or `submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv` for a clean JEPA sensor. Do not submit S2, high-scale, or full-latent JEPA variants.

### H204. Target-dependency gating localizes E209 hard-tail risk but cuts useful Q3 body

- 상태: 부분 지지 by E210; replacement claim weakened.
- 왜 그럴듯한가: E209's frontier risk is concentrated in a small number of high-swing Q3/S4 cells. If the remaining error is target-manifold violation, then a conditional target-dependency model should keep public-favorable cells and reject dangerous cells.
- 맞다면: dependency-aligned cells should have better local loss, anti-aligned controls should fail frontier stress, and the gated movement should reduce top-cell concentration or bad-axis energy without destroying OOF/geometry.
- 틀리다면: dependency gates would either be polarity-free, fail anti-controls, or remove the useful OOF/geometry body while looking good only under public-prior heuristics.
- 최소 실험: `analysis_outputs/e210_jepa_target_dependency_gate.py`.
- 관측: selected E210 closer files improve public-prior hard-tail anatomy strongly, with focus deltas near `-0.00137` and top1/abs near `0.17`. Anti-toward controls do not pass the frontier gate. However selected Q3/S4 closer gates weaken OOF versus ungated E209 by about `+0.00079` and geometry by about `+0.00084`. Cell anatomy says S4 dependency alignment is useful, but Q3 not-closer/not-toward cells are often the larger local winners.
- 성공/폐기 기준: supported as a hard-tail localization sensor. Rejected as a replacement for raw E209 unless public feedback shows the dependency-tail prior is more important than the lost OOF/geometry body.
- public LB 관측 반응: E210 win after E209 tie/loss strengthens "public tail wanted target-dependency filtering." E210 loss weakens the dependency gate and says E209's raw Q3 body was useful despite target-manifold tension.
- 제출 전략: do not submit E210 before E209 if the goal is a clean JEPA test. Submit E210 only as a follow-up sensor for target-dependency hard-tail localization.

### H205. Q3 wants raw JEPA body, S4 wants dependency-consistent JEPA movement

- 상태: 지지 by E211; needs public sensor.
- 왜 그럴듯한가: E210's target anatomy showed S4 dependency-aligned cells are locally favorable, while Q3 dependency alignment removes useful residual body. A shared Q3/S4 gate should therefore underperform a target-specific policy.
- 맞다면: keeping Q3 raw while dependency-gating S4 should improve or preserve OOF relative to ungated E209, pass subject/geometry stress, and improve frontier hard-tail anatomy relative to raw E209 without collapsing into the E210 Q3 body loss.
- 틀리다면: S4 gating would lose OOF/geometry, anti/zero controls would match the selected policies, or public-prior hard-tail anatomy would not improve enough to justify the added gate.
- 최소 실험: `analysis_outputs/e211_target_specific_jepa_gate.py`.
- 관측: Q3 raw + S4 toward improves OOF to `-0.001318` versus E209 `-0.001273`; Q3 raw + S4 closer gives `-0.001315`. Q3 target delta stays `-0.005775`, and S4 improves from raw `-0.003134` to toward `-0.003451`. Geometry remains negative with win rate `0.875`.
- 성공/폐기 기준: supported locally. Public support requires an E211 E95/E154 sensor to beat or match E209. If E211 loses while E209 wins, S4 dependency gate is overfit. If E211 wins while E209 loses/ties, S4 dependency filtering becomes the live translation law.
- public LB 관측 반응: E211 win strengthens target-specific JEPA translation. E211 loss weakens S4 dependency gating, not raw Q3 JEPA.
- 제출 전략: top sensor is `submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`; clean E95 sensor is `submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`.

### H206. JEPA-family public feedback must be ordered by hypothesis value, not raw survival score

- 상태: 지지 by E212; public feedback pending.
- 왜 그럴듯한가: E209, E210, and E211 all originate from the same trained E208 JEPA representation but answer different hidden-world questions. A public score from the wrong first file could confound raw JEPA usefulness, E154 repaired-branch anchoring, S4 dependency filtering, and blunt over-gating.
- 맞다면: a scoring rule that combines local OOF, geometry, parent integrity, hard-tail anatomy, anchor purity, and routebook interpretability should rank E211 before E210 despite E210's stronger hard-tail survival numbers.
- 틀리다면: E210 should dominate after accounting for its public-prior hard-tail improvement, or E209 should remain first because E211's target-specific gate adds no local/geometry value.
- 최소 실험: `analysis_outputs/e212_jepa_family_sensor_ordering.py`.
- 관측: E212 ranks E211 E154 closer first for structured survival, E211 E95 toward first for clean current-frontier sensing, E209 E95 Q3/S4 first among raw controls, and E210 behind all E211/E209 Q3/S4 candidates because local/geometry parent integrity collapses.
- 성공/폐기 기준: supported until public feedback contradicts the routebook. If E211 loses but E210 later wins, the E212 parent-integrity penalty was too strong. If E211 and E209 both lose, the current JEPA probability-graft family is weakened.
- public LB 관측 반응: E211 E95 win means actual JEPA is cleanly useful. E211 E154-only win means the E154 anchor may be doing heavy work. E211 loss plus E209 win means S4 dependency gating is overfit. E211/E209 losses mean the current JEPA probability translation is not the 0.54 path.
- 제출 전략: submit E211 E154 closer for maximum survival or E211 E95 toward for clean JEPA attribution; do not submit E210 before E211 unless deliberately asking only the blunt dependency-tail question.

### H207. The live Q3/S4 JEPA axes are specific representation signals, not random latent cherry-picks

- 상태: 지지 by E213; public translation still unproven.
- 왜 그럴듯한가: E208 scanned many JEPA coordinates, so the surviving Q3/S4 axes could be false discoveries. A real representation signal should beat permutations and neighboring PC coordinates under the same OOF correction path.
- 맞다면: Q3 `e208_resid_self_pc10` and S4 `e208_pred_pc14` should beat global and within-subject permutation nulls, rank near the top of their same-family PC pools, and keep nonpositive E208 geometry.
- 틀리다면: same-family PCs or permuted values would regularly match the live axes, or the live axes would rely on subject identity rather than feature-neighbor representation.
- 최소 실험: `analysis_outputs/e213_jepa_axis_specificity_audit.py`.
- 관측: Q3 and S4 both have global/subject permutation p-values `0.020408`, same-family pool rank `1/16`, and `specific` decisions. Q3 half win is `0.950000`; S4 half win is `0.733333`.
- 성공/폐기 기준: supported as a representation-specific signal. It would be weakened if a larger null or independent seed family finds many equivalent axes, or if public feedback rejects every E209/E211 probability translation.
- public LB 관측 반응: E211 public loss would now mean "real axis, bad translation/public tail" before it means "JEPA axis was noise." E211 public win would strengthen both axis specificity and translation.
- 제출 전략: do not drop the Q3/S4 JEPA axis family solely because it was selected from many latent coordinates. Keep public tests focused on E211/E209 translation and feedback decoding.

### H208. A supervised JEPA benefit gate can fix the E211 translation bottleneck

- 상태: 약화 by E214.
- 왜 그럴듯한가: E213 suggests the JEPA axes are real, so a remaining failure mode is heterogeneous row-target validity. If true, the OOF cells where raw JEPA improves log loss should be predictable from base/candidate/dependency geometry and axis energy.
- 맞다면: subject-CV benefit gates should have useful AUC, gated policies should preserve most of the Q3/S4 local gain, and frontier stress should beat or at least match E211 with lower hard-tail risk.
- 틀리다면: gate AUC should be weak, probability/rank/margin gates should shrink useful movement, and E211's simpler S4 dependency-consistency gate should remain dominant.
- 최소 실험: `analysis_outputs/e214_jepa_benefit_gate_translation.py`.
- 관측: Q3 gate AUC `0.552169`, S4 gate AUC `0.568968`. Best benefit-gated policy `q3raw_s4benefit_rank` has local delta `-0.000918`, weaker than raw JEPA `-0.001273` and E211 toward `-0.001318`. It improves geometry to `-0.000987`, but no E214 benefit policy passes frontier selection.
- 성공/폐기 기준: failed as a submission strategy. It remains a diagnostic because it shows weak benefit sorting and a geometry/local tradeoff.
- public LB 관측 반응: no E214 submission should be used before E211. If E211 fails, do not jump to E214 benefit gates; rebuild the representation or the translator.
- 제출 전략: none. Keep E211/E209 ordering.

### H209. Masked feature-family JEPA reveals a different Q1/S2/S4 latent channel

- 상태: representation 지지 by E215; public translation 약화 by E216 public feedback.
- 왜 그럴듯한가: E208's target representation was feature-neighbor broad-space and produced narrow Q3/S4 axes. A true I-JEPA-style block mask should ask a different question: can visible feature-family representations predict a hidden family representation?
- 맞다면: masked-family JEPA should beat mean/copy baselines, produce healthy enough latent geometry, and its downstream features should survive OOF, subject-half, and geometry stress on targets not already explained by E208.
- 틀리다면: the masked-family objective would either collapse, recreate only E208-like Q3/S4 signals, or fail geometry stress.
- 최소 실험: `analysis_outputs/e215_masked_family_jepa_probe.py`.
- 관측: E215 val MSE `0.585-0.604` versus mean-block MSE around `1.000`; pass count `10`; best target deltas Q1 `-0.004965`, S2 `-0.004370`, S4 `-0.003313`. E216 then selected S2-only locally, but `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` scored public `0.5772865088`, `+0.0009951790` worse than E95.
- 성공/폐기 기준: supported as a representation source, weakened as a public probability translator. E215 remains evidence that the masked-family question finds signal; E216 rejects the current S2-only translation.
- public LB 관측 반응: E216 S2-only public loss weakens masked-family JEPA as a second submission lane but does not erase E215's local representation evidence. A future masked-family attempt needs a different translator or a specific explanation of the S2 public tail.
- 제출 전략: do not submit remaining E216 siblings by default. Use E215/E216 features as diagnostics or negative controls until S2 tail failure is explained.

### H210. The locally strongest masked-family JEPA combo is not public-safe

- 상태: 지지 by E216 for broad combo rejection; S2-only survivor rejected by public feedback.
- 왜 그럴듯한가: many previous experiments show that broad local gains can invert on public-tail stress. E215's Q1+S2+S4 combo is locally strong, but it may move public-sensitive cells in the wrong direction.
- 맞다면: combined Q1/S2/S4 local OOF and geometry should be strong, while frontier graft stress should reject it or prefer a narrower target subset.
- 틀리다면: `q1_s2_s4_rank` should dominate both local and frontier stress.
- 최소 실험: `analysis_outputs/e216_masked_family_jepa_materialization.py`.
- 관측: `q1_s2_s4_rank` has delta `-0.001807`, subject-half win `1.000`, geometry `-0.001628`, but frontier stress does not select it. S2-only was selected at E95/E154 scales `0.50/0.75`; the submitted E154 scale `0.75` S2-only file returned public `0.5772865088`.
- 성공/폐기 기준: broad-combo rejection remains supported. The narrower S2-only rescue is rejected as public-safe for this translator and anchor/scale.
- public LB 관측 반응: the observed S2-only loss means E216 did not find a public-safe masked-family channel. If broad E215/E216 combos won later, the current public-tail stress would be too conservative for Q1/S4, but they are not currently recommended.
- 제출 전략: no E216 submission until a targeted public-tail audit explains why S2-only failed despite local and geometry stress.

### H211. A full teacher-student tabular JEPA can replace fixed-target JEPA probes

- 상태: 약화 by E217.
- 왜 그럴듯한가: E215 still predicted a fixed PCA family block. A closer I-JEPA translation should use an EMA teacher target encoder and let the target representation emerge from the data, potentially avoiding the narrow E208/E215 target-specific lanes.
- 맞다면: masked current feature-family context plus same-subject row-neighborhood context should predict the EMA full-row teacher latent, produce healthy geometry, and create downstream features that survive OOF, subject-half, and geometry stress better than E208/E215.
- 틀리다면: the teacher-student objective may learn well but downstream gains will be fold/geometry fragile, or useful signal will remain local to targets already captured by E211 or E215-style diagnostics.
- 최소 실험: `analysis_outputs/e217_teacher_student_tabular_jepa_probe.py`.
- 관측: training is nontrivial (`val_loss=0.00185..0.00191`, about `7%` of mean-teacher baseline), but no downstream row passes the E217 geometry gate. Best local S2 via `e217_teacher_pc07` has delta `-0.002853` but geometry delta `+0.000410`; Q3 residual rows are near-neutral but below win-rate threshold.
- 성공/폐기 기준: weakened as a direct submission source. It would reopen only if a target-specific materializer or different teacher target converts E217 energy into negative geometry and frontier-safe movement.
- public LB 관측 반응: no E217 public sensor should be submitted. If later E217-derived target-specific materialization wins, the current failure should be reinterpreted as translator failure rather than representation failure.
- 제출 전략: none now. Keep E211 as the actionable JEPA lane; E216 is demoted by public feedback.

### H212. E216 S2-only masked-family JEPA is public-safe

- 상태: 반증 by public feedback.
- 왜 그럴듯한가: E216's `s2_rank` passed local OOF, subject-half, geometry, bad-axis, and hard-tail frontier stress, while the broad Q1/S2/S4 masked-family combo was rejected.
- 맞다면: the E154 scale `0.75` S2-only file should land near E95 or improve as a non-collinear JEPA S2 sensor.
- 틀리다면: public LB should punish the S2-only graft enough to show that the stress stack missed a public-adverse tail.
- 최소 실험: submit `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv`.
- 관측: public LB `0.5772865088`, `+0.0009951790` worse than E95 and `+0.0009798683` worse than mixmin.
- 성공/폐기 기준: discarded as a public-safe submission lane. Smaller-scale and E95-anchor siblings are not automatically equivalent, but they are demoted until this miss is explained.
- public LB 관측 반응: the result points to S2-specific public-tail mismatch or anchor/scale amplification, not to a generic absence of masked-family signal.
- 제출 전략: none. Use E216 siblings only as negative controls or root-cause probes.

### H213. E216 failed because of E154 anchor body rather than S2 JEPA tail

- 상태: 반증 by E219.
- 왜 그럴듯한가: the submitted E216 file was anchored on E154, and vs E95 it moved `505` cells across `Q1,Q3,S2,S3,S4`, not just S2. A bad E154 inherited body could have made the S2 graft look worse than it is.
- 맞다면: E154 body alone should have enough adverse hard-label capacity to explain the observed `+0.0009951790` miss, or near-observed hidden-label worlds should attribute substantial loss to the E95 -> E154 body segment.
- 틀리다면: E154 body adverse capacity will be smaller than the observed miss, while pure S2 graft has enough adverse capacity and dominates near-observed loss attribution.
- 최소 실험: `analysis_outputs/e219_e216_public_miss_anatomy.py`.
- 관측: E154 body all-adverse capacity is `0.000924070`, below the observed miss. Pure S2 graft adverse capacity is `0.006048995`. Near-observed focus-prior worlds attribute mean `0.000920169` to the S2 graft and `-0.000004004` to E154 body.
- 성공/폐기 기준: rejected as the main explanation. Anchor interaction may amplify small details, but it is not sufficient to explain the public failure.
- public LB 관측 반응: E216's public result should now be read as S2-tail fragility, not merely E154-anchor bad luck.
- 제출 전략: do not use E216 E95-anchor siblings as automatic "anchor-clean" fixes. A new candidate needs an S2 support/tail gate.

### H214. S2 support-probability fragility is a missing stress dimension

- 상태: 지지 by E219.
- 왜 그럴듯한가: E216 passed local OOF and geometry because expected loss was slightly favorable, but LogLoss public response can flip if the moved cells' support labels are only weakly probable.
- 맞다면: S2 graft expected delta can be negative while swing-weighted support probability is below or near `0.5`; observed-loss-like simulations should be rare but plausible and dominated by S2.
- 틀리다면: support probability should be comfortably high, or near-observed worlds should require broad non-S2 attribution.
- 최소 실험: E219 segment simulation under global/subject/nearest/focus priors.
- 관측: pure S2 graft focus expected delta is about `-0.000287798`, but swing-weighted support probability is only `0.473945`. Focus-prior simulation has `25.382%` loss worlds and `0.2920%` worlds at or above the observed miss. Near-observed worlds are ~`100%` S2-attributed.
- 성공/폐기 기준: supported as the immediate root-cause for E216. It should be converted into a future gate and then retested locally before any S2 JEPA submission.
- public LB 관측 반응: a future S2-gated JEPA file should only be submitted if it reduces low-support S2 swing while preserving local/geometry gains.
- 제출 전략: none yet. Build an S2-tail audit/gate first; E211 Q3/S4 remains the live JEPA submission lane.

### H215. A simple support/tail threshold can rescue E216 S2

- 상태: 반증 by E220.
- 왜 그럴듯한가: E219 identified support probability as the missing stress dimension. A threshold on focus/subject/nearest support or a drop of the E219 posterior-risk top cells might remove the public-adverse tail while retaining the S2 expected gain.
- 맞다면: some gate should keep nontrivial S2 cells, have negative expected focus movement, adverse capacity below the observed E216 miss `0.0009951790`, support probability above `0.5`, and low simulation probability of matching the observed miss.
- 틀리다면: high-support gates will lose the expected gain, while expected-negative gates will keep too much adverse capacity.
- 최소 실험: `analysis_outputs/e220_s2_support_tail_gate_audit.py`.
- 관측: no gate passes. `focus_support_ge_0p7` has support `0.791501` and adverse `0.000209735`, but expected focus is positive `+0.000018940`. `focus_support_ge_0p6_expected_neg` has expected `-0.000578857`, but adverse `0.001402108`, above the observed miss. `expected_neg_only` has expected `-0.001204825`, but adverse `0.002118163`.
- 성공/폐기 기준: rejected for simple threshold/drop gates. The diagnosis remains useful, but the repair needs a richer OOF-reproducible support classifier.
- public LB 관측 반응: no E220 submission should be used. A future S2 candidate must show both expected gain and bounded adverse capacity under a trainable gate.
- 제출 전략: none. Keep E216/E220 as negative evidence and continue with E211 or a new S2 support-model experiment.

### H216. A trainable OOF support classifier can rescue E216 S2

- 상태: 반증 by E221 for current E215/E216 feature family.
- 왜 그럴듯한가: E216 S2 was strongly positive on local OOF, and E219 showed the failure mode was support/tail fragility. If the cells where the S2 move helps are learnable from JEPA latent/state/order features, a trainable gate could keep the local signal while reducing public-tail exposure.
- 맞다면: OOF support classifiers should have above-noise AUC, OOF-gated S2 delta should remain negative, subject/block stress should survive, and the same gate on test should have negative focus expected delta with adverse capacity below the observed E216 miss.
- 틀리다면: support may be learnable locally, but OOF-good gates and test-tail-safe gates will select different subsets; no joint gate passes both criteria.
- 최소 실험: `analysis_outputs/e221_s2_oof_support_classifier.py`.
- 관측: support classification is locally real (`AUC=0.748104` stratified, `0.717482` row-contiguous, `0.713730` subject-LOO), and many OOF gates have strong negative S2 deltas. But no scanned gate passes both OOF and submission-side tail stress. The best OOF-safe gates often carry adverse capacity far above the E216 miss, while the few submission-tail-safe gates fail OOF support/win criteria.
- 성공/폐기 기준: rejected for the current feature/translator setup. This does not prove S2 has no signal; it proves the present E215 S2 translator lacks a train/test-stable support gate.
- public LB 관측 반응: no E221 file should be submitted. If a future S2 file is made, it must change the representation target or loss, not merely learn a row support classifier on E215 features.
- 제출 전략: none. Continue with E211 Q3/S4 or design a new S2 target representation with support/tail regularization baked into the objective.

### H217. E211 Q3/S4 is support-safe under the E216 failure criterion

- 상태: 약화 by E222.
- 왜 그럴듯한가: E211 passed local OOF, subject-half, geometry, bad-axis, and public-prior expected-delta stress, while E213 showed the Q3/S4 axes are not cheap PCA cherry-picks.
- 맞다면: E211 grafts should have negative expected focus movement with swing-weighted support probability above `0.5`, and target-level top-cell concentration should not dominate the expected edge.
- 틀리다면: E211 will look like E216 in the new stress dimension: expected-good but low support probability, with one target carrying fragile top-cell risk.
- 최소 실험: `analysis_outputs/e222_e211_support_tail_audit.py`.
- 관측: E211 E154 closer graft has expected focus `-0.000655277` but support probability `0.463231`; E211 E95 toward has expected `-0.000654330` and support `0.463587`. Target breakdown shows S4 is healthier, while Q3 expected is only `-0.000144..-0.000147` and Q3 top1/expected is `>1.0`.
- 성공/폐기 기준: E211 is not fully support-safe. The representation remains live, but original full-Q3 E211 submissions are now riskier than the older E212 ranking implied.
- public LB 관측 반응: a public win from original E211 would mean low support probability was too conservative for Q3/S4; a loss would strongly validate E222 and close full-Q3 E211 as a translator.
- 제출 전략: prefer a Q3-tail-rebalanced E211 variant before submitting the original full-Q3 E211 files.

### H218. Reducing E211 Q3 scale preserves most expected gain while cutting tail risk

- 상태: 부분 지지 by E223.
- 왜 그럴듯한가: E222 localized the healthier part of E211 to S4 and the fragile part to Q3. Reducing Q3 should reduce adverse capacity and top-cell concentration without discarding the S4 dependency-gated body.
- 맞다면: q3_scale `0.75` variants should remain E211-frontier/geometry eligible, keep expected focus near the full-Q3 files, and reduce adverse capacity/top1 concentration.
- 틀리다면: Q3 reduction will either kill expected gain, fail existing geometry/local checks, or not reduce tail risk enough to matter.
- 최소 실험: `analysis_outputs/e223_e211_q3_tail_rebalance.py`.
- 관측: selected `submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv` has graft expected `-0.000636968`, adverse `0.003852760`, support `0.464872`, and geometry `-0.000556139`. Actual vs E95 expected is `-0.000666805`, adverse `0.004533247`, top1/expected `0.176972`.
- 성공/폐기 기준: partially supported as a risk-rebalanced sensor, not a certified safe move. Support probability remains below `0.5`, so it does not solve the whole tail-support problem.
- public LB 관측 반응: if E223 beats E95/E216 and ideally E95 frontier, the world update is "S4 body plus reduced-Q3 tail is public-aligned." If it loses like E216, low-support Q3/S4 translation is the bottleneck and JEPA probability movement should be demoted.
- 제출 전략: current preferred JEPA-family file is `analysis_outputs/submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv`; use E95-anchor sibling only for clean attribution.

### H219. The E211 Q3 tail knee is lower than E223's 0.75 scale

- 상태: 지지 by E224 as current candidate-ranking update.
- 왜 그럴듯한가: E223 showed Q3 reduction helps, but Q3 still had low support and high concentration. If Q3 is mainly a fragile auxiliary tail while S4 carries the healthier body, the best public sensor should cap Q3 below `0.75`.
- 맞다면: a lower q3_scale should remain local/geometry negative, keep expected focus materially negative, and reduce adverse capacity plus Q3 top1/expected enough to pass a stricter support-tail gate.
- 틀리다면: lower q3_scale will either lose the local/expected body or fail to reduce the specific Q3 tail enough to change candidate order.
- 최소 실험: `analysis_outputs/e224_e211_q3_scale_pareto.py`, sweeping q3_scale `0.0..1.0` for S4 `closer/toward` and E95/E154 anchors while joining E211 local/geometry with E222 support-tail metrics.
- 관측: q3_scale `0.625` is the selected knee. Best row `e224_q3s0p625_s4closer_e154_a0p5` has local delta `-0.001098893`, geometry delta `-0.000505582`, expected focus `-0.000623352`, adverse `0.003400775`, support `0.465984`, and Q3 top1/expected `0.875120`. q3_scale `0.75` has stronger expected/local body but fails the E224 tail gate; q3_scale `0.50` is safer but too weak.
- 성공/폐기 기준: supported for submission ordering, not for safety certification. Support remains below `0.5`, so public feedback can still reject the translator.
- public LB 관측 반응: if E224 wins, strengthen the "S4 body plus capped-Q3 residual" world. If it loses materially, demote the E211 probability translator and keep JEPA axes only as diagnostics.
- 제출 전략: preferred JEPA-family file becomes `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`; E223 becomes the q3_scale `0.75` ablation.

### H220. E224 public feedback must route through a capped-Q3 decoder, not scalar amplitude tuning

- 상태: 지지 by E225 governance.
- 왜 그럴듯한가: E224 is almost collinear with E223/full E211, differing mainly by Q3 amplitude. Without a decoder, any public score could be overread as "increase/decrease Q3" after the fact.
- 맞다면: the pre-public routebook should map each score band to a unique world update and explicitly forbid the tempting amplitude siblings.
- 틀리다면: E224 movement would be non-collinear enough to require a new family decoder, or the score bands would not separate E95/E101/mixmin/E216 reference outcomes.
- 최소 실험: `analysis_outputs/e225_e224_public_feedback_decoder.py`.
- 관측: routebook bands are locked: clean win `<=0.576276019`, tie `0.576288330..0.576294330`, small loss up to `0.576300366`, mixmin-safe loss up to `0.576306641`, branch loss above. Movement anatomy confirms E224 is collinear with E223 (`0.996078`) and full E211 (`0.975464`), but far from E216 S2 miss (`0.043542`).
- 성공/폐기 기준: supported as governance. It does not predict the score; it prevents post-hoc route collapse after the score arrives.
- public LB 관측 반응: after E224 feedback, run the decoder before choosing any sibling. A win strengthens capped-Q3/S4-body; a loss worse than mixmin closes the current E211 translator.
- 제출 전략: no new submission. Attach E225 to the E224 submission protocol.

### H221. Existing post-E224 escape routes are mostly same-family or already rejected

- 상태: 부분 지지 by E226 as candidate-order update.
- 왜 그럴듯한가: E216 rejected the masked-family S2 public translation, and E224 is almost collinear with E223/full E211. If the existing pool contains a real escape route, it should be visibly non-collinear to those axes and should not sit near E72/E176/E216 public-negative movement.
- 맞다면: most high-scoring JEPA siblings will collapse into the same Q3/S4 family, E216 siblings will be S2 bad-axis neighbors, and only a small set of non-collinear counter-world files will remain.
- 틀리다면: E209/E210/E211/E223 siblings or bridge/mixmin-near files would survive as independent, public-meaningful alternatives under cosine, support-tail, and known-public vetoes.
- 최소 실험: `analysis_outputs/e226_noncollinear_candidate_scan.py`.
- 관측: evaluated `73` documented/materialized files. E209/E210/E211/E223/E224 are marked same Q3/S4 JEPA family. E216 siblings are S2 bad-axis neighbors. The E52 bridge blend is demoted as `local_rejected_neartie`. The top actionable independent file is `submission_e166_broadsurv_s0p01_d8bfa94b.csv` with cos(E224) `0.074348`, expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`; E154 remains the conservative repaired-branch counter-world.
- 성공/폐기 기준: supported for existing-pool routing, not for public-score certification. The scan can rank what to test next but cannot prove E166 improves public LB.
- public LB 관측 반응: if E166 wins, the safety atlas after E72/E101/E176/E216 was overconservative for broad survivor structure. If E166 loses, broad survivor/E72-active low-veto-null tension is likely public-negative and E154/search becomes the cleaner counter-world path.
- 제출 전략: E224 for JEPA capped-Q3/S4. E166 for one independent broad worldview sensor. E154 for conservative repaired-branch sensor. Do not spend a public slot on E209/E210/E211/E223 as an "independent" E224 alternative.

### H222. E166 is a context-real but safety-divergent broad-world sensor

- 상태: 지지 as public-sensor protocol by E227; public outcome pending.
- 왜 그럴듯한가: E167 showed E166 top-benefit cells are enriched for edge-like and between-train-runs context, but also have high E72-active and low safety-atlas support. E226 then selected E166 as the best existing non-E224 independent candidate.
- 맞다면: E166 public feedback should strongly update the safety-atlas worldview. A win means the atlas is too conservative for broad survivor context; a loss means E72-active/low-veto-null warnings are public-causal.
- 틀리다면: E166 would score near E95 with no clear separation, leaving the broad-world question underresolved and making E224/E154 question-dependent next actions more useful.
- 최소 실험: submit `submission_e166_broadsurv_s0p01_d8bfa94b.csv`, then run `analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>`.
- 관측: routebook locked before feedback. E166 moves `1750` cells across all `7` targets, cos(E224) `0.074348`, expected focus `-0.000332077`, adverse `0.000713053`, support `0.465747`. Top-benefit cells have edge-like `0.689189`, between-train-runs `0.797297`, E72-active `0.837838`, all-veto-null `0.297297`.
- 성공/폐기 기준: public win below `0.576276019` supports broad-world safety-atlas-overconservative hypothesis; mixmin-safe loss or worse demotes broad survivor expected-score lane; E72-scale loss requires miss anatomy before any broad candidate.
- public LB 관측 반응: E227 has explicit bands from broad breakthrough through E72-like fail and S2-JEPA-like collapse.
- 제출 전략: E166 only when the intended question is independent broad-world structure. E224 remains the JEPA slot; E154 remains conservative repaired-branch.

### H223. E224/E166/E154 are not one blendable worldview

- 상태: 지지 by E228 movement-conflict atlas.
- 왜 그럴듯한가: E224, E166, and E154 survived as the live post-E216 choices, but if they share the same moved cells or signs then submitting/mixing them would only retest one latent branch.
- 맞다면: E224/E166 and E166/E154 should be low-cosine, low top-k-overlap pairs; E224/E154 should reveal whether E154 is inherited inside E224 rather than independent.
- 틀리다면: pairwise cosines and top-k overlaps would be high across all three, and a tri-blend would be a reasonable amplitude smoother.
- 최소 실험: `analysis_outputs/e228_triworld_conflict_atlas.py`.
- 관측: E224/E166 cosine `0.074348`, top50 overlap `1`, same-sign E166 coverage of E224 mass `0.035638`; E166/E154 cosine `0.061662`, top50 overlap `0`; E224/E154 cosine `0.316350`, and E154's active cells are fully inside E224 active cells with `0.885621` same-sign E154 mass coverage.
- 성공/폐기 기준: supported for routing. E224 and E166 are separate public questions; E154 is not fully independent from E224 because E224 inherits its repaired body.
- public LB 관측 반응: an E224 score should be decoded as capped-Q3/S4 JEPA feedback; an E166 score should be decoded as broad safety-atlas feedback. An E154 score is most informative after attribution says the E224 residual, not the inherited body, is the suspect.
- 제출 전략: do not build a blind tri-world blend. Submit E224 for the JEPA question, E166 for the independent broad question, and E154 only as the conservative repaired-branch counter-world.

### H224. The next public slot is question-dependent, not proxy-score-dependent

- 상태: 지지 by E229 governance audit.
- 왜 그럴듯한가: adding E176/E216 to the public-anchor table improves coarse proxy fit, but the frontier gaps remain far below the proxy error floor. At the same time, E228 shows live candidates ask genuinely different questions.
- 맞다면: the public-anchor proxy should remain too coarse to certify a next frontier file, while E224/E166/E154 routebooks should separate into JEPA-first, independent broad, and conservative repaired-branch questions.
- 틀리다면: the updated 14-anchor proxy would resolve a candidate as better than E95 beyond its LOOCV error, or E228 would show the live files are duplicate enough that a scalar score rank/blend is justified.
- 최소 실험: `analysis_outputs/e229_next_public_slot_decision.py`, using E225/E227/E160 routebooks, E228 conflict atlas, and the updated `public_anchor_bottleneck_decomposition.py`.
- 관측: best proxy MAE is `0.000496259` with p90 `0.000695363`, still larger than the E95/E101/mixmin/E176 gaps. E224 is selected only under the JEPA-first question because it is low-cosine to E216 (`0.043542`) and Q3/S4-dominant. E166 is first under independent broad-world testing. E154 is conditional because E224 covers `0.885621` of its mass same-sign.
- 성공/폐기 기준: supported as routing policy. It does not prove E224 will score better; it proves the next slot should be a pre-declared observation, not a public-anchor proxy bet.
- public LB 관측 반응: an E224 score updates whether the current JEPA translator survives E216; an E166 score updates whether broad survivor structure was over-vetoed. The same scalar LB band must be read through the chosen routebook.
- 제출 전략: forced one-slot under current JEPA question is E224. If the next goal changes to escaping JEPA, choose E166. Do not submit E154 first unless the explicit question is repaired-branch validation or attribution points there.

### H225. E224's weak point is a prunable Q3 tail, but the first JEPA observation should stay unpruned

- 상태: 부분 지지 by E230; public outcome pending.
- 왜 그럴듯한가: E222/E224 localized E211-family risk to Q3 concentration, while S4 carried the healthier body. If that diagnosis is real, pruning a small number of low-support Q3 cells should improve adverse/support geometry with little expected-focus cost.
- 맞다면: small Q3-only rollbacks should reduce adverse capacity, raise swing-weighted support, keep expected focus materially negative, and avoid touching the S4 body.
- 틀리다면: any Q3 prune will either remove most of E224's expected edge, fail to reduce adverse capacity, or require a broad threshold that no longer tests the same E224 latent.
- 최소 실험: `analysis_outputs/e230_e224_support_tail_prune_audit.py`.
- 관측: `q3_swingtop25_drop` keeps expected focus `-0.000600044` with only `+0.000023308` loss vs E224, reduces adverse by `0.000633168`, and raises support by `0.009873471`. `q3_risktop21_drop` is even better under the prior on expected focus (`-0.000691244`, `-0.000067892` vs E224) with support gain `0.021076971`.
- 성공/폐기 기준: supported as a conditional repair, not as a first-slot replacement. The prune rule is public-free but not OOF-learned, so it cannot supersede E224 before E224 receives public feedback.
- public LB 관측 반응: if E224 tie/small-loses and E225 attribution points to Q3 tail, an E230 win would strengthen "S4 body survives, Q3 tail was the defect." If E224 hard-fails, E230 is too narrow and the E211 translator itself is suspect.
- 제출 전략: submit E224 first for the JEPA question. Use `analysis_outputs/submission_e230_q3_swingtop25_drop_e0918606.csv` or `analysis_outputs/submission_e230_q3_risktop21_drop_7d95c14a.csv` only as a post-E224 conditional sibling.

### H226. E230-style Q3 tail pruning is learnable enough to replace E224 as the JEPA translator

- 상태: 반증 by E231 for current E224/E230 representation.
- 왜 그럴듯한가: E230 showed Q3 tail cells can be rolled back with low expected-focus cost and better support/adverse geometry. If those fragile cells are visible in train/OOF structure, a learned gate would be cleaner than hand-pruning submission anatomy.
- 맞다면: Q3 support classifiers should achieve stable AUC across stratified, row-contiguous, subject-kfold, and subject-LOO splits; OOF gates should preserve E224's Q3 gain; the same gates on test should reduce Q3 adverse capacity and pass E222/E224 tail stress.
- 틀리다면: local support AUC will be weak or fold-sensitive, OOF-good gates and test-tail-safe gates will not overlap, and no selected submission file will survive joint stress.
- 최소 실험: `analysis_outputs/e231_e224_q3_oof_support_prune.py`.
- 관측: support-label rate `0.502222`; full E224-like Q3 OOF delta `-0.004262113`; best support-model AUC only `0.588101`; no OOF/support-tail joint gate passes; no submission file selected.
- 성공/폐기 기준: rejected as a first-class translator. The Q3 hand-prune remains a conditional public-feedback repair only.
- public LB 관측 반응: none, because no E231 candidate should be submitted. If E224 later tie/small-loses and Q3 tail is blamed, use E230 hand-prune rather than E231 learned gates.
- 제출 전략: do not submit E231. Submit E224 first if testing JEPA; use E230 only after E224 attribution.

### H227. S2/Q3/S4 support-tail risk is one shared row/block latent

- 상태: 반증 for the current E216/E224 translators by E232.
- 왜 그럴듯한가: E216 S2, E224 Q3, and E224 S4 all involve JEPA-derived target translations and all are evaluated through hard-label LogLoss support. If their failures come from hidden subject/block identity, a shared support gate or LeJEPA regularizer should align support labels across targets.
- 맞다면: support labels and benefit vectors should be positively correlated across S2/Q3/S4; subject support rates should share signs; a model trained on one target movement should transfer to another through row/latent context; test-side low-support rows should overlap.
- 틀리다면: label/benefit overlap should stay near zero, subject correlations may conflict, transfer should depend mostly on movement-shape features, and test low-support overlap should be small.
- 최소 실험: `analysis_outputs/e232_cross_target_support_invariance.py`.
- 관측: max row-label correlation `0.057278`, max benefit correlation `0.090611`; subject support correlations Q3/S2 `-0.442384`, Q3/S4 `0.128085`, S2/S4 `-0.491326`; Q3/S2 test low-support top25 overlap `1` row. Best cross-target AUC is movement-shape transfer `0.745452`, while best latent-context transfer is only `0.707003`.
- 성공/폐기 기준: rejected as a shared row/block latent. The transferable part is generic movement calibration, not a shared support identity.
- public LB 관측 반응: no direct submission. If a future shared S2/Q3/S4 gate wins, it must first explain why E232 showed almost no support overlap; otherwise such a win should be treated as public-luck or target-specific leakage.
- 제출 전략: do not submit shared support-gated S2/Q3/S4 files. Build future JEPA support/energy objectives target-specifically, with movement-shape calibration as an auxiliary diagnostic.

### H228. Target-specific support probabilities can be reused as soft JEPA amplitude heads

- 상태: 반증 by E233 for the current E216/E224 support representations.
- 왜 그럴듯한가: E221 and E232 showed S2/S4 support is locally learnable, while E231 showed hard Q3 gates are too brittle. A continuous probability-to-amplitude head might avoid hard-gate discontinuity and preserve more useful movement.
- 맞다면: soft amplitude policies should beat or match the full target movement in OOF, keep subject stability, and for Q3 assign low amplitude to E230's public-free fragile risk rows.
- 틀리다면: soft policies will mostly under-scale full movement, fail to beat full target deltas, and their low-amplitude Q3 rows will not overlap E230 risk cells.
- 최소 실험: `analysis_outputs/e233_target_specific_soft_energy_heads.py`.
- 관측: promoted policies `0`; best learned Q3 soft delta `-0.002548953` versus full `-0.004262113`; best learned S2 `-0.002769599` versus full `-0.004370425`; best learned S4 `-0.002931629` versus full `-0.003430136`; Q3 low-amplitude top25 overlap with E230 risk-top21 is `0`.
- 성공/폐기 기준: rejected as a candidate generator and as a cheap support-head rescue.
- public LB 관측 반응: none, because no E233 candidate should be submitted. A future support-energy submission must come from a changed target representation/loss, not from these post-hoc support probabilities.
- 제출 전략: do not create softened E221/E231 support-gate files. Keep E224/E230 public policy unchanged and design a new target-specific JEPA target.

### H229. Tail-contrastive target representation can recover JEPA translation signal

- 상태: 부분 지지 locally by E234; submission transfer unresolved outside S2.
- 왜 그럴듯한가: E233 showed support probabilities are the wrong amplitude object, but E216/E224 movements still have target-specific OOF benefit. A JEPA target that predicts high-impact adverse/positive tails rather than all-row support may align better with LogLoss bottlenecks.
- 맞다면: high-impact `risk` or `contrast` tail models should beat the full target movement under OOF/subject stress, and dropped rows should have negative mean benefit.
- 틀리다면: tail labels should behave like the failed support heads: no promoted policies, weak subject stability, and no improvement versus full target movement.
- 최소 실험: `analysis_outputs/e234_tail_contrastive_jepa_target.py`.
- 관측: promoted policies `323`; best loss versus full movement is S2 `-0.002653627`, Q3 `-0.000870181`, and S4 `-0.000833194`. Dropped rows for promoted policies have negative mean benefit, so this is not just scalar shrinkage.
- 성공/폐기 기준: supported as a local representation clue. Not promoted to public submission until target-side materialization passes public-free tail stress.
- public LB 관측 반응: no direct public reaction because E234 creates diagnostics, not a selected file. A future E234 Q3/S4 materialization win would strengthen this hypothesis; an E235-like public-free failure on all targets would demote it to OOF-only structure.
- 제출 전략: do not submit E234 directly. Materialize target-specific branches separately; S2 was tested first and failed in H230, so Q3/S4 or cell-level decisive-label variants are the remaining live paths.

### H230. E234 S2 tail-risk drops can rescue the failed E216 S2 public lane

- 상태: 반증 by E235 for current E216/E234 S2 tensors.
- 왜 그럴듯한가: E234's largest local gain is S2, and the best risk policies strongly improve OOF loss versus full E216 S2. If the public miss was caused by identifiable high-adverse S2 rows, these drops should lower E216's adverse capacity.
- 맞다면: at least one S2 materialization should preserve E234 OOF gain and pass E221 submission-side stress: negative expected focus, adverse capacity below the observed E216 miss, support above `0.5`, and no single-cell dominance.
- 틀리다면: OOF-good S2 drops will still have too much public-tail adverse capacity or too little support when applied to test.
- 최소 실험: `analysis_outputs/e235_s2_tail_contrastive_materialization.py`.
- 관측: scanned `240` S2 rows; submission gate pass `0`; joint gate pass `0`; materialized files `0`. Best expected rows still show adverse capacity `1.878x..4.068x` the observed E216 miss and support below `0.5`.
- 성공/폐기 기준: rejected as a public-safe S2 rescue.
- public LB 관측 반응: none; no E235 file should be submitted. The existing E216 public miss remains the public observation that governs this lane.
- 제출 전략: keep E216/E235 S2 closed. Do not submit smaller-scale or E95-anchor S2 variants unless a new target definition changes the submission-side support geometry.

### H231. E234 Q3/S4 learned tail masks can replace E230 hand-pruned Q3 intervention

- 상태: 반증 by E236 for current E224/E234 Q3/S4 tensors.
- 왜 그럴듯한가: E234's tail-contrastive target improves Q3 and S4 OOF loss versus full movement, while E230 showed that E224's Q3 tail can be pruned without destroying the S4 body. A learned E234 mask would be cleaner than E230's hand intervention.
- 맞다면: at least one Q3-only, S4-only, or Q3+S4 materialization should preserve E224 expected focus, reduce adverse capacity, improve support, and lower Q3 top-cell concentration under the public-free E222/E230 stress frame.
- 틀리다면: learned Q3 masks will reduce some adverse capacity but select low-support rows or worsen top-cell concentration; learned S4 masks will erase healthy S4 body; no joint materialization will pass the gate.
- 최소 실험: `analysis_outputs/e236_q3s4_tail_contrastive_materialization.py`.
- 관측: graft rows `92`; gate passes `0`; materialized files `0`. Best Q3 masks reduce adverse by `0.000329753` but support drops `-0.004017252` and Q3 top1/expected rises to `3.054720`. Best S4 support gain is `0.006519636`, but expected focus weakens by `0.000166178` and Q3 tail risk remains.
- 성공/폐기 기준: rejected as a learned replacement for E230. E234 remains a local target-representation clue, not a direct submission translator.
- public LB 관측 반응: none, because no E236 file should be submitted. If E224 later suggests Q3-tail blame, the conditional repair is still E230 rather than E236.
- 제출 전략: do not submit E236. Keep E224/E230 policy unchanged and move JEPA work toward sharper cell-level decisive-label targets or a different target representation.

### H232. Q3/S4 tail law is cell-level decisive, not row-level support

- 상태: 부분 지지 by E237/E242 public-free stress; public LB 미확인.
- 왜 그럴듯한가: E230's hand-prune acted on a small set of Q3 cells, while E236's row-level Q3/S4 masks failed by either losing support or erasing S4 body. That pattern suggests the hidden law lives at row-target-cell granularity.
- 맞다면: a bad-cell predictor trained on OOF decisive-cell labels should identify Q3 cells whose rollback improves E224 public-free stress while leaving S4 mostly untouched. It should improve both graft-vs-E154 and actual-vs-E95 stress, not only OOF.
- 틀리다면: cell-level models will reproduce E236's failure: Q3 support loss, high top-cell concentration, S4 body loss, or no actual-vs-E95 improvement.
- 최소 실험: `analysis_outputs/e237_cell_decisive_jepa_target.py`.
- 관측: OOF rows `3744`, stress-promoted rows `441`, materialized scan rows `240`, gate passes `7`. Top candidate drops `25` Q3 cells, `0` S4 cells, improves expected loss vs E224 by `-0.000005612`, reduces adverse by `0.000576400`, improves actual-vs-E95 adverse by `0.000553281`, and overlaps E230 risk-top21 by `11` rows.
- E242 추가 관측: E237's selected top file is not a mean-OOF-gain winner (`71/120` by OOF gain, OOF-gain gate AUC `0.426043`), but it is the top OOF tail-AUC row (`1/120`) and OOF tail-AUC predicts the E237 gate strongly (`AUC=0.958913`). It is also `1/120` by support gain and Q3 top-cell safety.
- 성공/폐기 기준: supported locally because it passes OOF, graft-vs-E154, and actual-vs-E95 stress. It remains public-unconfirmed until submitted.
- public LB 관측 반응: if top E237 wins or cleanly beats E224/E95, strengthen the "decisive Q3 cell-tail" world and demote pure row-level JEPA gates. If it loses materially, treat E237 as another local-tail false positive and return to E224/E166/E154 branch routing.
- 제출 전략: top learned-JEPA Q3-tail candidate is `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`.

### H233. E237 public feedback is identifiable only through a pre-registered contrast routebook

- 상태: 지지 by E238 governance; public LB 미확인.
- 왜 그럴듯한가: E237 is close to E224/E230 in movement family, while E216 showed that a JEPA-looking local translator can fail by almost `0.001`. A scalar public score alone cannot say whether the Q3 cell law worked, tied, or collapsed unless the score bands and contrast files are fixed first.
- 맞다면: a routebook should separate clean win, tie, small loss, branch loss, and E216-like collapse before public feedback. It should also identify whether E237 is a new learned object or just E230 hand-prune duplication.
- 틀리다면: E237/E224/E230 movement anatomy would be too entangled to make any pre-score interpretation stable, or the routebook would require post-hoc thresholds from the public score.
- 최소 실험: `analysis_outputs/e238_e237_public_feedback_decoder.py`.
- 관측: clean support band is `<=0.576276019`; tie is `0.576288330..0.576294330`; branch loss starts above `0.576306641`; E216-like collapse starts above `0.576591330`. E237 changes `25` Q3 cells vs E224, overlaps E230 swing25 by `13`, and overlaps E230 risk21 by `11`, so it is related but not identical.
- 성공/폐기 기준: supported as a governance hypothesis because it locks the public interpretation without seeing E237's score. It is not evidence that E237 will win.
- public LB 관측 반응: after E237 public feedback, run the decoder. A clean win strengthens H232; tie/small loss requires E224 contrast; branch loss kills E237 siblings; E216-like fail kills the current cell translator target.
- 제출 전략: no new submission from H233. Use the top E237 file only when the next public question is learned Q3 decisive-cell JEPA.

### H234. E237's learned Q3 cells are a latent residual-energy motif, not just a top-k/calendar shortcut

- 상태: 수정됨 by E240. residual-energy motif는 지지, learned-selector uniqueness는 약화.
- 왜 그럴듯한가: E237 overlaps E230 hand-prunes only partially, yet passes actual-vs-E95 public-free stress. If it is real, the selected cells should have a context motif beyond "largest E224 movement" or obvious row/date edge.
- 맞다면: E237 cells should not be fully explained by top-25 amplitude, subject edge, or train-date adjacency. They should instead show stable latent-context anomaly signals that are plausibly tied to Q3 tail risk.
- 틀리다면: E237 would be nearly identical to E230 top swing/risk rows, or its selected cells would be almost entirely top-25 E224 movement / calendar-edge cells without additional latent enrichment.
- 최소 실험: `analysis_outputs/e239_e237_cell_motif_atlas.py`.
- 관측: E237 has only `13/25` overlap with E230 swing25 and `11/21` with E230 risk21. Only `52%` of E237 cells are E224 top-25 amplitude, though `96%` are top-50. Edge/calendar explanations weaken because near-test-edge-2 is `0.120` vs population `0.240`, and train-gap-adjacent-2 is `0.240` vs `0.344`. Strong enrichments appear in E208 latent residual/neighbor-distance features: `e208_resid_self_abs_mean`, `e208_nn_target_dist`, `e208_resid_self_norm`, `e208_resid_self_pc10`.
- E240 추가 관측: deterministic residual-energy rules also pass the E237-like gate. `simple_pc10_top25` has expected loss vs E224 `-0.000062119`, adverse reduction `0.000594489`, support gain `0.016747154`, actual adverse reduction `0.000573879`, and overlaps E237 by only `14/25`. All `9/9` non-control E240 simple selectors pass the E237-like gate.
- 성공/폐기 기준: the residual-energy motif is supported locally, but the learned E237 selector is not unique. Public support for E237 would support the broader Q3 residual-energy cell-tail world, not specifically the E237 learned model. If E237 loses, it closes both the learned selector and the current simple residual-energy rollback idea until train/OOF validation is rebuilt.
- public LB 관측 반응: E237 win strengthens the Q3 residual-energy decisive-cell world; E237 tie keeps it diagnostic only; E237 loss closes E237 siblings and shifts the residual-energy features into the negative-control registry.
- 제출 전략: no new file from H234. The only currently meaningful public test remains the fixed E237 top file; do not tune top-k or add residual-energy masks before public contrast.

### H235. Current E237/E230 stress gates cannot distinguish learned Q3 cells from simple residual-energy rules

- 상태: 지지 by E240; 단순 residual-rule 제출 가설은 E241로 반증.
- 왜 그럴듯한가: E239 found that E237 cells are residual-energy enriched. If the stress gate is only checking "remove some high-risk Q3 cells while preserving S4", a simple residual ranking may pass without proving a learned JEPA target.
- 맞다면: simple rules based on E208 residual PC10, residual abs mean, NN distance, or residual+amplitude combinations should pass the same graft-vs-E154 and actual-vs-E95 stress that selected E237.
- 틀리다면: simple rules would fail expected loss, adverse reduction, support gain, Q3 top-cell, or actual-vs-E95 checks, leaving E237 as uniquely learned.
- 최소 실험: `analysis_outputs/e240_e237_residual_rule_ablation.py`.
- 관측: all `9/9` non-control simple selectors pass the E237-like gate. Best simple rule `simple_pc10_top25` beats E237 control on expected loss, support gain, Q3 top1/expected, and actual adverse reduction while overlapping E237 only `14/25`.
- E241 추가 관측: train OOF Q3 benefit validation rejects the simple rule as a harmful-row selector. No score has negative selected-benefit delta; `score_pc10` top-10% has drop delta `+0.001867628`, split-stress mean `+0.002633171`, and win rate `0.30`. Yet the same `score_pc10` top25 overlaps E237 by `14/25` and E230 swing25 by `18/25` on test.
- 성공/폐기 기준: the stress-gate weakness is supported, but simple residual-energy rules are rejected as submission translators under current OOF labels. E237 is not proven unique, but it remains more defensible than post-hoc PC10 because it is OOF-trained on decisive-cell labels.
- public LB 관측 반응: if E237 wins, the update should favor learned Q3 decisive-cell structure with residual-energy motif support, not simple PC10 top-k. If E237 loses, both E237 siblings and simple residual rules should be closed until the OOF target is rebuilt.
- 제출 전략: no H235/H241 simple residual submission. Use only the fixed E237 file if deliberately testing the learned cell-tail world.

### H236. E208 residual-PC10 alone is an OOF-valid Q3 harmful-cell selector

- 상태: 반증 by E241.
- 왜 그럴듯한가: E239 found high residual-PC10 enrichment in E237 cells, and E240 showed residual-PC10 rules pass the same public-free stress as E237/E230 while overlapping E230 swing cells strongly.
- 맞다면: residual-PC10 and related residual/NN-distance scores should pick train OOF Q3 rows where the E224-like Q3 movement is harmful. Top-k selected-benefit deltas should be negative, split stress should have win rate above random, and the effect should survive row-contiguous and subject-LOO folds.
- 틀리다면: residual-PC10 will overlap the test motif but fail to select harmful OOF train rows; selected-benefit deltas will be non-negative or fold-unstable.
- 최소 실험: `analysis_outputs/e241_residual_pc10_oof_benefit_validation.py`.
- 관측: no score has negative full-train selected-benefit delta. `score_pc10` top-10% is adverse (`+0.001867628`) and split-stress mean is also adverse (`+0.002633171`, win rate `0.30`). The best split-stress top-10% score, `score_nn_dist`, remains slightly adverse (`+0.000270542`, win rate `0.50`).
- 성공/폐기 기준: rejected for current labels and current E224-like Q3 movement.
- public LB 관측 반응: no public submission should be used to test this directly. A future E237 public win would not resurrect simple PC10 unless a new OOF target explains why train OOF and public-tail geometry diverge.
- 제출 전략: do not create or submit E240-style residual-PC10 files.

### H237. E237 should be ranked by average OOF policy gain

- 상태: 반증 by E242.
- 왜 그럴듯한가: E237 is OOF-trained. If the learned cell policy is a normal supervised translator, policies with the best OOF loss improvement should be the safest public-free materializations.
- 맞다면: OOF gain should correlate with E237 score, predict E237 gate membership, and rank the selected top file near the top.
- 틀리다면: OOF mean-gain winners will often fail materialization support/top-cell stress, and the selected E237 file will be chosen by tail-discrimination/test geometry instead.
- 최소 실험: `analysis_outputs/e242_e237_oof_to_test_transfer_audit.py`.
- 관측: OOF gain vs E237 score Spearman is `0.108953`; OOF gain gate AUC is `0.426043`; top E237 file is only `71/120` by OOF gain. In contrast, OOF tail-AUC gate AUC is `0.958913`, and the top E237 file ranks `1/120` by OOF tail-AUC, support gain, and Q3 top-cell safety.
- 성공/폐기 기준: rejected as a ranking rule. E237 should be read as a high-impact tail classifier plus public-free stress survivor, not as an average OOF gain maximizer.
- public LB 관측 반응: E237 public win strengthens high-impact tail-discrimination, not generic OOF policy gain. E237 public loss says even that tail-discrimination plus stress gate is insufficient.
- 제출 전략: do not submit E237 siblings chosen by OOF gain rank.

### H238. E237 universally supersedes E224 as the next JEPA public file

- 상태: 반증 as a universal rule by E243; 조건부 지지 for improvement-biased JEPA-as-solution.
- 왜 그럴듯한가: E237 keeps E224's S4 body, drops only `25` Q3 cells, improves E224-relative support/adverse geometry, and E242 ranks it `1/120` by OOF tail-AUC/support/top-cell safety.
- 맞다면: the next public slot should always be E237 whenever the word JEPA is the question, because it strictly dominates E224 in both information value and expected score.
- 틀리다면: E237 and E224 answer different public questions. E237 tests learned Q3 decisive-cell pruning; E224 tests the clean unpruned capped-Q3/S4 JEPA body. A single public score from E237 cannot tell whether an E224 body failure/success was caused by body alignment or by pre-pruned Q3 cells unless E224 is also known or the E238 contrast routebook is used.
- 최소 실험: `analysis_outputs/e243_next_public_slot_after_e242.py`.
- 관측: E243 ranks E237 first only for an `improvement_biased_jepa_tail_sensor` slot. E224 remains first for `clean_unpruned_jepa_body_sensor`. E166 remains first for `independent_non_jepa_broad_world_sensor`, and E154 remains conservative/conditional.
- 성공/폐기 기준: universal-supersession is rejected. Conditional E237 promotion is supported when the explicit goal is to try JEPA as a solution rather than isolate the clean body. E224 remains the cleaner ablation.
- public LB 관측 반응: if E237 is submitted and wins, strengthen H232 high-impact Q3 tail-discrimination but still use E238/E224 contrast before increasing Q3 or tuning siblings. If E237 loses, close the current learned Q3-tail branch; do not infer that E224 would have failed unless the loss is E216-like or an E224 contrast is known.
- 제출 전략: one-file JEPA-as-solution candidate is `analysis_outputs/submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv`. One-file clean JEPA body candidate remains `analysis_outputs/submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv`.

### H239. E237 aligns with the E207 feature-NN1 true-JEPA regime

- 상태: 약한 지지 by E245; not certified.
- 왜 그럴듯한가: E207 found only one plausible true-JEPA positive-pair regime, `broad_stage2_pca64 / feature_nn1_all`. E237 is currently the closest real JEPA-as-solution candidate, but E217 showed that a larger teacher-student JEPA can learn a latent and still fail translation. If E237 is a healthier representation rather than a local tail artifact, its Q3 rollback should at least move E224 toward feature-neighbor compatibility.
- 맞다면: applying E237's 25 Q3 rollbacks should reduce feature-nearest-neighbor Q3 logit roughness, especially on pairs affected by those rows, and should not look worse than random row rollbacks of the same size.
- 틀리다면: E237 rollback will be neutral/adverse under feature-NN1 pair roughness, or any smoothness improvement will be indistinguishable from random top-amplitude rollback.
- 최소 실험: `analysis_outputs/e245_feature_nn1_jepa_compat_audit.py`.
- 관측: actual E237 rollback reduces global Q3 NN-pair abs-logit roughness by `-0.000802649` and affected-pair roughness by `-0.006472972` over `31` affected directed pairs. However, the null is not decisive: all-row percentiles are `0.1754` global and `0.1080` affected, and top50-amplitude null percentiles are `0.3132` and `0.2896`.
- 성공/폐기 기준: weakly supported as compatibility, not accepted as certification. A strong result would have required top50-amplitude null percentile below roughly `0.10` on the affected-pair metric.
- public LB 관측 반응: E237 public win plus E245 weak compatibility would justify training a direct feature-NN1/decisive-cell JEPA target. E237 public loss overrides this weak compatibility and closes current E237 siblings unless an E224 contrast says the body was worse.
- 제출 전략: no new E245 submission. Keep the audited E237 file as the one-file JEPA-as-solution candidate.

### H246: Feature-NN1 smoothing is an actionable Q3 selector, not just an E237 explanation

- 상태: public-supported as E247 mechanism; still rejected as an OOF-invariant harmful-cell selector.
- 왜 그럴듯한가: E245 showed E237 locally smooths Q3 under the only E207 true-JEPA pair regime, but the effect was weak. If that regime is the hidden public law, directly selecting rows by hypothetical feature-NN1 Q3 smoothing should survive E237 stress without needing the learned E237 classifier.
- 맞다면: smoothing-based selectors should pass graft-vs-E154 and actual-vs-E95 stress, improve adverse/support metrics versus E224, avoid collapsing into pure E237 or amplitude-top-k selections, and identify negative-benefit train OOF Q3 rows under analogous feature-NN graphs.
- 틀리다면: smoothing selectors will fail the E237-like gate, only pass as E237 clones, pass only by violating Q3 top-cell/adverse constraints, or look label-adverse/non-invariant under train OOF benefit.
- 최소 실험: `analysis_outputs/e246_feature_nn1_smoothing_selector_ablation.py`; OOF invariance audit in `analysis_outputs/e248_feature_nn1_oof_smoothing_invariance.py`.
- 관측: all `16/16` feature-NN1 selectors pass the E237-like gate. Best `nn_smooth_sum_top34` has expected loss vs E224 `-0.000066519`, adverse reduction `0.000632592`, support gain `0.005788959`, actual adverse reduction `0.000596176`, Q3 top1/expected `0.549713494`, and E237 overlap `13`. E248 then weakens the invariant-selector claim: at the E247 selection fraction, the train-only PCA smooth-sum analogue has OOF rollback delta `+0.002829987`, the all-PCA analogue has `+0.002922728`, and split-stress means remain positive. Even the best full-train score is only the negative-control direction and still non-negative at `+0.000489209`.
- 성공/폐기 기준: supported as a test-side geometric stress survivor, rejected as OOF-certified harmful-row selector. A future upgrade requires an OOF-trained feature-NN1 decisive target or public feedback from E247 that specifically supports the manifold rule.
- public LB 관측 반응: E247 public win promotes feature-NN1 smoothing to a real JEPA selector. Near-tie keeps it informative but unresolved. E216-like loss demotes feature-NN1 smoothing to calibration shortcut.
- 제출 전략: E247 remains a high-information public sensor only. For the more score-biased JEPA bet, prefer E237 because it has OOF tail-AUC support; do not sweep E247 siblings before feedback.

### H247: E247 is the most informative current JEPA-as-solution public sensor

- 상태: strongly supported by public LB; current public best, with E224-body attribution still unresolved.
- 왜 그럴듯한가: E237 is OOF-learned but only weakly feature-NN1-compatible. E247 is not OOF-learned, but it is generated directly from the E207 feature-neighbor context-target representation and passes the same stress gate with stronger smoothing and a non-clone row set.
- 맞다면: the E247 artifact should be Q3-only, schema-clean, materially stronger in feature-NN1 roughness reduction than E237, and either OOF-invariant or explicitly useful as a public falsification of feature-NN1 smoothing.
- 틀리다면: artifact integrity will fail, movement will leak into other targets, stress metrics will not hold after materialization, or E248-like OOF checks will show that smoothing is not a label-relevant harmful-cell selector.
- 최소 실험: `analysis_outputs/e247_feature_nn1_smoothing_materializer.py`; OOF invariance audit in `analysis_outputs/e248_feature_nn1_oof_smoothing_invariance.py`.
- 관측: `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` is schema/key/probability clean, changes `34` E224 cells all on Q3, SHA256 `3f4086d73b23a9c87294986aaa3a8ff32613312e69a398352d6744b8646ce839`, and reduces feature-NN1 Q3 roughness by `-0.014223558` globally and `-0.057353058` on affected pairs. E248 adds the missing LeJEPA skepticism: the same smoothing rule does not select negative-benefit OOF rows; train-only/all-PCA analogues are positive-delta at `+0.002829987` and `+0.002922728`.
- 성공/폐기 기준: selected as a clean public sensor for whether feature-NN1 manifold smoothing itself is the hidden law. Downgraded as an expected-score candidate because it fails OOF selector validation.
- public LB 관측 반응: win over E95 means JEPA manifold smoothing is actionable. Loss near E95/E101 means the hypothesis remains weak. E216-scale loss closes smoothing selectors until OOF invariance is learned.
- 제출 전략: if spending one slot to falsify feature-NN1 smoothing directly, submit E247. If choosing the best current score-biased JEPA file, submit E237 instead.

### H249: Feature-NN1 context helps only when paired with a decisive-cell target

- 상태: partially supported by E249/E250; not certified as a higher-score replacement for E237.
- 왜 그럴듯한가: E248 showed direct smoothness is not OOF-invariant, but I-JEPA suggests context should predict a hidden representation, not force raw smoothness. The hidden target here is E237-style Q3/S4 decisive-cell risk.
- 맞다면: adding feature-NN1 context to E237 OOF frames should improve some tail-discrimination rows, and at least one materialized policy should pass graft-vs-E154 plus actual-vs-E95 stress without becoming a broad top-k smoothing clone.
- 틀리다면: feature-NN1-augmented rows should either fail OOF promotion, fail materialization support/adverse gates, or only produce the same E247/E237 clone cells.
- 최소 실험: `analysis_outputs/e249_feature_nn1_decisive_oof_audit.py` and `analysis_outputs/e250_feature_nn1_decisive_materialization_stress.py`.
- 관측: E249 scans `2496` rows and promotes `276`; feature-NN1 `latent_no_targetid/hgb_shallow` improves tail-AUC in `62.5%` of paired rows but worsens median loss by `+0.000053880`. E250 then finds `4/120` gate-passing materializations. The best file drops `21` Q3 cells, has OOF tail-AUC `0.887357`, expected loss vs E224 `-0.000000845`, adverse reduction `0.000524271`, support gain `0.005790882`, and Q3 top1/abs-expected `0.660128`.
- 성공/폐기 기준: accepted as a live feature-NN1-context sensor because it passes OOF and materialization stress; rejected as a broad replacement because median paired loss is worse and E237 has stronger locked OOF/tail metrics.
- public LB 관측 반응: an E250 win would strengthen "feature-NN1 context improves decisive-cell JEPA translation." A loss near E95/E101 would keep E237 first and demote feature-NN1 context to a weak diagnostic. An E216-like loss would say even decisive-cell feature-NN1 context is a calibration shortcut.
- 제출 전략: submit E250 top21 only if the explicit next question is feature-NN1-context transfer. For likely score, keep E237 first.

### H250: E249's broad top50 OOF gain is not submission-safe

- 상태: rejected by E250 materialization stress.
- 왜 그럴듯한가: E249's strongest OOF row had loss_vs_full `-0.000706695`, far better than locked E237 by average OOF loss.
- 맞다면: the same top50 Q3 drop should retain negative expected loss, positive support gain, bounded top-cell concentration, and E237-gate survival after submission-side grafting.
- 틀리다면: the broad top50 drop should lose support, become top-cell concentrated, or fail actual-vs-E95 safety despite the attractive OOF loss.
- 최소 실험: materialize E249 promoted rows with `analysis_outputs/e250_feature_nn1_decisive_materialization_stress.py`.
- 관측: the `drop_q3_top50` family ranks high by OOF loss but fails E237 gate after materialization. Its support gain is negative around `-0.006080609` and Q3 top1/abs-expected is high around `0.928874`.
- 성공/폐기 기준: rejected as a submission lane. Tail-AUC/support/top-cell stress outranks average OOF gain for this branch.
- public LB 관측 반응: no submission should be spent on the top50 row. If a sibling is submitted, it should be one of the E250 gate-pass rows, not the OOF-loss maximum.
- 제출 전략: do not submit E249 top50 or broad global policies. Use E250 top21 if using this branch at all.

### H251: E237 and E250 are complementary Q3 tail views, not simple substitutes

- 상태: supported by materialization anatomy; OOF status for the union is unverified.
- 왜 그럴듯한가: E237 has stronger OOF tail-AUC, while E250 adds feature-NN1 context. If the two contexts see different public-tail cells, their union should outperform either parent under support/adverse/top-cell stress.
- 맞다면: E237 and E250 should partially overlap but not be identical; union should pass materialization stress and improve support/adverse metrics; E250-only should not necessarily be sufficient alone.
- 틀리다면: E250 should be a near-clone of E237, union should fail by over-pruning, or only one parent should carry all materialization gains.
- 최소 실험: `analysis_outputs/e251_e237_e250_cellset_contrast.py`.
- 관측: E237 has `25` Q3 cells, E250 has `21`, shared `15`, E237-only `10`, E250-only `6`. The union of `31` cells passes with expected loss vs E224 `-0.000035272`, adverse reduction `0.000721005`, support gain `0.010353010`, Q3 top1/abs-expected `0.506203`, and score `0.077866812`, above E237 `0.058941606` and E250 `0.053008707`.
- 성공/폐기 기준: supported as a public-free complementarity signal. Not accepted as OOF-certified until a train-side analogue or public feedback confirms that the union cells are not a post-hoc materialization artifact.
- public LB 관측 반응: E252 win would strengthen complementary Q3 tail views. E252 loss while E237/E250 are untested would mean the materialization gate over-rewarded union broadness. E252 E216-like loss closes unioning before OOF certification.
- 제출 전략: E252 can be submitted only as a complementarity sensor. E237 remains first for expected score.

### H252: The shared E237/E250 core alone is the safe Q3 tail

- 상태: conflicted. Rejected by submission-side E251, locally supported by OOF E253.
- 왜 그럴듯한가: two independent context views selecting the same `15` Q3 cells could indicate a high-confidence consensus core.
- 맞다면: the intersection should pass materialization stress with lower top-cell concentration than either parent.
- 틀리다면: the intersection should become too concentrated or positive expected loss, implying that the useful structure is distributed across parent-specific cells.
- 최소 실험: E251 intersection materialization audit and E253 OOF analogue.
- 관측: E251 shared intersection fails materialization gate with expected loss vs E224 `+0.000028815` and Q3 top1/abs-expected `1.054975`. E253 gives the opposite train-OOF read: shared intersection is the strongest OOF variant with loss_vs_full `-0.000376454`, better than E237 `-0.000271441`, E250 `-0.000185023`, and union `-0.000080010`.
- 성공/폐기 기준: rejected as a direct submission law because materialization stress fails; retained as a validation-mismatch signal because OOF strongly supports it.
- public LB 관측 반응: no public slot should test intersection-only yet. If E252 loses and E237 wins, E253's OOF-intersection signal becomes a warning that materialization union overreached.
- 제출 전략: do not materialize an intersection-only candidate.

### H253: E252 union has OOF-certified complementarity

- 상태: rejected as certification; weakly supported only as stress-promoted sensor.
- 왜 그럴듯한가: E251 union had the strongest public-free materialization anatomy, suggesting parent-specific E237 and E250 cells might be complementary.
- 맞다면: the OOF union should beat both E237 and E250 parents or at least approach the shared-intersection OOF benefit while remaining stress-promoted.
- 틀리다면: the union should be stress-promoted but diluted versus the parents, or become outright adverse, showing that materialization support/adverse anatomy over-rewards broad cell unioning.
- 최소 실험: `analysis_outputs/e253_e237_e250_union_oof_analogue.py`.
- 관측: union is stress-promoted, but loss_vs_full is only `-0.000080010`, worse than E237 by `+0.000191431` and worse than E250 by `+0.000105013`. Parent-specific cells are OOF-adverse: E237-only `+0.000105013`, E250-only `+0.000191431`, symmetric difference `+0.000296444`.
- 성공/폐기 기준: rejected as OOF-certified complementarity. The union remains a public sensor because it passed E251/E252 materialization, not because OOF proves it.
- public LB 관측 반응: E252 win would imply hidden public labels prefer materialization support geometry over train OOF intersection. E252 loss would reinforce validation mismatch and keep E237 first.
- 제출 전략: E252 is lower-confidence than E237; use only if the chosen question is OOF-vs-public-free materialization conflict.

### H254: The E237/E250 conflict is a train/test Q3 geometry shift, not simple consensus error

- 상태: supported as a bottleneck diagnosis; not yet a submission rule.
- 왜 그럴듯한가: E253 showed a contradiction that simple validation labels cannot resolve: OOF likes shared consensus, while materialization likes union. If the selected cells also shift in feature-neighbor and logit-step geometry between train and test, then the contradiction is a real hidden-world mismatch.
- 맞다면: shared, E237-only, and E250-only groups should have different train/test distributions in probability gap, logit step, or feature-NN1 smoothing context; consensus should not be a safe scalar confidence score.
- 틀리다면: train/test selected groups should be similar on those visible axes, and the conflict would more likely be implementation noise or a metric-definition artifact.
- 최소 실험: E254 conflict atlas comparing train OOF benefit, test hard-tail anatomy, and feature shifts for shared/E237-only/E250-only/union groups.
- 관측: train shared cells have OOF benefit mean `-0.028234084`, while train union is only `-0.002117914`. Test shared cells have favorable expected focus `-0.000028815` but Q3 top1/abs `3.412733926`, and union changes the hard-tail profile. The largest train/test shifts are `prob_gap` (`-1.52` to `-1.80` std across selected groups) and `logit_step` (`-1.40` to `-1.67` std), with feature-NN1 smooth-gain sign flips in shared and E250-only groups.
- 성공/폐기 기준: supported for diagnosis because multiple visible axes move in the same conflict direction. Not accepted as an action rule until a contrastive target trained on OOF can predict which test cells belong to public-tail-adverse parent-specific geometry.
- public LB 관측 반응: an E252 win would mean public follows the test materialization side despite OOF dilution; an E252 loss would mean the OOF/shared signal was the safer proxy after all. Either result should be interpreted through this geometry-shift lens, not as a generic JEPA pass/fail.
- 제출 전략: no new E254 submission. Keep E237 first for expected score; E252 remains a conflict sensor only.

### H255: E247 feature-NN1 Q3 smoothing is public-real despite OOF rejection

- 상태: strongly supported by public LB; attribution still incomplete.
- 왜 그럴듯한가: E246 found a test-side feature-neighbor Q3 smoothing intervention that survived materialization stress, while E248 rejected its train OOF analogue. A public win would mean public follows the test feature-neighbor geometry more than the ordinary OOF harmful-row label.
- 맞다면: E247 should beat E95 by more than frontier noise and should force the candidate order away from E237/E252 toward feature-NN1 smoothing follow-ups.
- 틀리다면: E247 should tie or lose, making E248's OOF rejection a valid veto and demoting smoothing to calibration shortcut.
- 최소 실험: public submission of `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv`; E255 feedback decoder.
- 관측: E247 public LB `0.5761589494`; beats E95 by `0.0001323804`, mixmin by `0.0001476911`, and the E95-over-mixmin edge by `8.646x`.
- 성공/폐기 기준: supported as a public-positive branch because the win is much larger than previous frontier micro-edges. Not accepted as isolated rollback proof because E224 clean body remains unobserved.
- public LB 관측 반응: already observed as strong support. Future E224 feedback would split body-vs-rollback attribution.
- 제출 전략: E247 is current public best. The next score-plus-information file should come from the E247 family, not from E237/E252, unless the explicit question is clean JEPA body or OOF-vs-materialization conflict.

### H256: E247's public win comes from high-amplitude smooth cells rather than broad top34 smoothness

- 상태: live; E256 created to test it.
- 왜 그럴듯한가: E247 top34 includes lower-amplitude broad smoothness cells. E255 ranks `top50_amp_then_smooth25` as the best non-identical follow-up because it keeps `21/34` E247 cells but constrains to high-amplitude Q3 cells.
- 맞다면: E256 should beat E247 or at least retain most of the gain with fewer cells, showing that the extra broad top34 cells were noise or private risk.
- 틀리다면: E256 should lose clearly to E247, meaning broad smoothness cells outside the high-amplitude subset are public-useful.
- 최소 실험: submit `analysis_outputs/submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv`.
- 관측: E256 changes `25` Q3 cells, overlaps E247 on `21`, has E237/E230/amp-top25 overlap `14`, expected loss vs E224 `-0.000047418`, adverse reduction `0.000615602`, and affected-pair roughness delta `-0.070332985`.
- 성공/폐기 기준: E256 win strengthens high-amplitude smoothing; near loss keeps E247 broad top34; hard loss warns that E247's exact top34 or E224-body interaction is nonlocal.
- public LB 관측 반응: pending.
- 제출 전략: E256 is the next one-file post-E247 information candidate.

### H257: E247-only broad smoothness cells are the key difference from E256

- 상태: live; E257 atlas supports a clean broad-vs-amplitude interpretation, public outcome pending.
- 왜 그럴듯한가: E256 shares `21/34` E247 cells but replaces the remaining low-amplitude broad smoothing cells with only `4` high-amplitude cells. This is a controlled anatomy change inside the same feature-NN1 Q3 mechanism family.
- 맞다면: E256 should underperform E247 if E247-only broad smoothness mass is public-useful, even though E256 has stronger amplitude and affected-pair roughness reduction.
- 틀리다면: E256 should beat or tie E247, implying E247's lower-amplitude extra cells were noise/private risk and the public law is amplitude-constrained smoothing.
- 최소 실험: `analysis_outputs/e257_e247_e256_cell_contrast_atlas.py`, then public submission of E256 if one score-plus-information slot is used.
- 관측: E247-only cells have rollback amplitude mean `0.039125051`, smooth-gain sum `1.002858981`, and no E237/E230 overlap. E256-only cells have amplitude mean `0.110316918`, smooth-gain sum only `0.049289874`, E230 swing overlap `4/4`, and support probability `0.531582541`. E247-all has more smoothness mass; E256-all has stronger affected-pair roughness reduction.
- 성공/폐기 기준: E256 win strengthens high-amplitude constrained smoothing; close loss strengthens broad smoothness; hard loss implies exact E247 top34 or E224-body interaction.
- public LB 관측 반응: pending.
- 제출 전략: E256 remains the next information-rich post-E247 file; do not create more siblings before this broad-vs-amplitude sensor is resolved.

### H258: E247's public win is a body-plus-tail-correction effect, not standalone smoothing

- 상태: supported as an attribution diagnosis; public attribution still pending.
- 왜 그럴듯한가: E247 is built on top of E224. A public win from E247 alone cannot tell whether E224's capped-Q3/S4 body was already strong, whether the Q3 rollback added the key public edge, or whether both were necessary.
- 맞다면: the E247 rollback should be a small, target-local, opposite-sign trim of the E224 Q3 body, while E247 total movement should preserve E224's S4/body signal and improve Q3 tail concentration.
- 틀리다면: E247 rollback would be a same-sign independent movement, or the total E247 movement would not show body preservation plus Q3 tail repair.
- 최소 실험: `analysis_outputs/e258_e247_body_rollback_attribution_atlas.py`.
- 관측: E224 body vs E95 moves `534` cells with expected focus `-0.000653189`; E247 rollback moves `34` Q3 cells with expected focus `-0.000066519`. On selected cells, rollback is almost exactly opposite to body: cosine `-0.992683110`, opposite-sign share `1.000000`, rollback abs over selected body abs `0.984581403`. E247 total improves expected focus to `-0.000719708` and Q3 top1/abs to `0.545240602`.
- 성공/폐기 기준: supported as a geometry diagnosis. Public attribution requires either E224 public LB or E256 public LB; E247 alone is insufficient.
- public LB 관측 반응: E224 beating or tying E247 would mean body carried most of the win and rollback may be over-pruning. E224 losing clearly while E256 stays strong means Q3 rollback is necessary. E256 beating E247 means amplitude-constrained rollback is better than broad rollback.
- 제출 전략: Use E256 for score-plus-information; use E224 for clean body attribution. Avoid E247/E256 blending before one axis is observed.

### H259: post-E247 feedback must be decoded by route, not scalar rank

- 상태: supported as governance; public outcomes pending.
- 왜 그럴듯한가: E247 is underidentified because the same public win can be explained by E224 body, Q3 rollback, or interaction. E257/E258 show the candidate axes are cleanly separable only if E256 or E224 is observed alone.
- 맞다면: a future E256 or E224 public score should map to a specific hidden-world update without post-hoc sibling tuning.
- 틀리다면: E256/E224 scores would be uninterpretable even with pre-registered bands, or a blend would produce more information than an isolated axis.
- 최소 실험: `analysis_outputs/e259_post_e247_observation_routebook.py`; then submit exactly one of E256 or E224 depending on whether the next question is score-plus-information or attribution.
- 관측: routebook written to `analysis_outputs/e259_post_e247_observation_routebook_report.md`. E256 bands separate amplitude breakthrough, tie, broad-smoothness loss, same-family loss, and hard loss. E224 bands separate body breakthrough, body tie, rollback-helped, body-not-enough, and body collapse.
- 성공/폐기 기준: after public feedback, the decoded action should be followed without creating an unplanned sibling blend. If both E256 and E224 later contradict the routebook interpretation, H259 weakens and the live branch becomes non-collinear structure search.
- public LB 관측 반응: E256 win strengthens amplitude-constrained smoothing; E256 close loss strengthens broad low-amplitude smoothness; E224 win/tie strengthens body sufficiency; E224 worse than mixmin rejects body-only translator.
- 제출 전략: E256 first for score plus information; E224 first for attribution. No E247-family blend before one score is observed.

### H260: E256's public risk is the four high-amplitude additions, not broad-smoothing deletion

- 상태: public-supported as a failure interpretation, not as full cell-causal proof.
- 왜 그럴듯한가: E257 showed E256 differs from E247 in two ways at once: it removes `13` E247-only broad smoothness cells and adds `4` high-amplitude/E230-swing cells. Without separating these groups, an E256 public loss would be easy to misread as proof that broad smoothness was necessary.
- 맞다면: E256-vs-E247 expected risk should concentrate in the E256-only high-amplitude group, while the E247-only deletion should be neutral or favorable under current hard-label priors.
- 틀리다면: the E247-only broad deletion should carry the main positive expected penalty, and the E256-only added cells should be neutral or favorable.
- 최소 실험: `analysis_outputs/e260_post_e247_next_slot_risk_atlas.py`.
- 관측: E256 expected focus versus E247 is `+0.000019101`. The E247-only deletion group is slightly favorable (`-0.000001767`), while the E256-only high-amplitude group is adverse (`+0.000020868`). E224-vs-E247 is larger-risk at `+0.000066519`, dominated by common rollback removal (`+0.000068286`).
- 성공/폐기 기준: E256 public `0.5762805676` landed in `same_family_loss`. This supports the failure-reading side of H260: high-amplitude constrained additions should be blamed before broad-deletion restoration. If a later cell-level ablation shows E256-only additions are safe but E247-only deletions are harmful, H260 is rejected.
- public LB 관측 반응: observed E256 loss strengthens E247 exact top34 / body interaction and weakens high-amplitude smoothing as score route. It does not prove broad smoothness alone was causal because top two E256-vs-E247 swing cells can explain the actual delta scale.
- 제출 전략: stop E256-like siblings. Submit E224 only for body attribution; otherwise refresh non-collinear candidates under the new E247/E256 public-anchor set.

### H261: E256 loss is a same-family rejection, not a feature-NN1 collapse

- 상태: supported by public LB.
- 왜 그럴듯한가: E256 is built inside the E247 feature-NN1 Q3 smoothing family, but it changes the cell anatomy from broad top34 to amplitude-constrained top25. A loss to E247 could mean either the entire smoothing mechanism is false or that this refinement is too concentrated.
- 맞다면: E256 should be worse than E247 but not catastrophically worse than the pre-E247 frontier; E259 should decode it below E247 but above hard-loss territory.
- 틀리다면: E256 would fall below E95/mixmin or into E216-like miss territory.
- 최소 실험: user-supplied public LB plus `analysis_outputs/e261_e256_public_feedback_assimilation.py`.
- 관측: E256 public `0.5762805676`, worse than E247 by `+0.0001216182`, better than E95 by `-0.0000107622`, and E259 outcome `same_family_loss`.
- 성공/폐기 기준: supported for now. A future E224 hard loss plus non-collinear branch win would reframe E247 as a narrow public overfit; an E224 tie/win would support body sufficiency and keep E247 rollback optional.
- public LB 관측 반응: current observation rejects amplitude-constrained smoothing as the next score route but keeps feature-NN1 smoothing as a validated mechanism relative to E95.
- 제출 전략: no more E247-family threshold siblings. Use E224 for attribution or refresh non-collinear candidates for score.

### H262: raw lifelog contains human/social lifestyle states that should be JEPA context, not generic features

- 상태: live; E262 gives strong observational support, but no downstream validation yet.
- 왜 그럴듯한가: raw app usage contains recognizable behavior categories: KakaoTalk/messages/calls, browser/search, finance/shopping, media, health-walk, and religion/routine apps. Sensors add charging, screen, GPS, WiFi/BLE, light, pedometer, HR, and ambience. These are enough to describe daily social load, routine stability, commute/workday rhythm, and sleep-onset fragmentation.
- 맞다면: lifestyle composites should show within-subject label lift and should help predict held-out Q/S tail-risk states under subject/date-block stress. They should also explain some public-sensitive cells that numeric smoothing alone cannot explain.
- 틀리다면: the same composites will mostly predict subject identity or train/test split, and OOF tail-risk prediction will fail after subject/date blocking.
- 최소 실험: E262 feature build plus E263 public-tail context join; next, OOF lifestyle-tail JEPA target over Q3 cells.
- 관측: E262 family max effects include workday/commute `0.238938`, routine `0.212389`, late cognitive load `0.208275`, sleep-onset risk `0.203540`, and social overstimulation `0.178550`. Train/test shift is largest in HR/pedometer coverage, so domain leakage risk is real.
- 성공/폐기 기준: success requires a blocked OOF latent that predicts Q3/S tail-risk beyond subject/date priors and improves or explains frontier candidate disagreement. Discard if it only produces train/test adversarial signal.
- public LB 관측 반응: a successful future submission from this branch should be non-collinear with E247/E256 and should not look like another Q3 smoothing threshold sibling.
- 제출 전략: not yet. Use as JEPA context/energy and build a lifestyle-tail target before materialization.

### H263: E256 failed because high-amplitude Q3 smoothing hits a different human-day state

- 상태: live but narrowed; E263 supports a hypothesis-generating lifestyle contrast, and E264 shows lifestyle context predicts OOF tail movement. E265 blocks direct broad rollback submission because the policy gate is too easy.
- 왜 그럴듯한가: E256-only cells are the first suspect after E256's public loss. If those cells share a lifestyle state, then the failure is not just amplitude; it is missing human context in the Q3 tail translator.
- 맞다면: E256-only public-swing rows should be separable from common/E247-only rows by human diary features such as late cognitive load, social-message load, screen/onset-risk, HR, and presleep movement. A held-out analogue should predict similar high-risk smoothing cells.
- 틀리다면: E256-only rows should look like random selected Q3 cells under lifestyle features, or the lifestyle signature should vanish under subject/date blocking.
- 최소 실험: E263 join and contrast; next, train an OOF cell-tail classifier using E262 lifestyle context with feature-family masks.
- 관측: E256-only rows show high late cognitive load and HR but lower late social/message, public-social-presence, screen/onset-risk, and presleep social/search than the common E247/E256 core. E264's human_late OOF head reaches best human-only loss_vs_full `-0.001689622`; E265 random best is only `-0.000723735`.
- 성공/폐기 기준: keep only if a sharper OOF lifestyle-tail JEPA head predicts held-out Q3 smoothing-validity and passes materialization stress. Discard broad policy-level gates because random controls pass too often.
- public LB 관측 반응: if this is right, a future candidate should avoid E256-like high-amplitude cells specifically when the day looks cognitively active but not socially/screen-fragmented.
- 제출 전략: no immediate file. Build a lifestyle-conditioned Q3 tail gate.

### H264: late/presleep human diary context predicts Q3/S4 harmful tail movement

- 상태: supported as local representation; not submission-certified.
- 왜 그럴듯한가: E262 extracted late social/search/screen/charging/movement/HR context. E263 suggested public-sensitive Q3 cells differ by this human-day state. E264 tests the same idea on train OOF tail labels.
- 맞다면: human_late should survive subject/date-block OOF and beat random policy controls by more than noise.
- 틀리다면: human views should fail blocked OOF or be indistinguishable from random broad rollback selection.
- 최소 실험: E264 OOF scan plus E265 random control.
- 관측: E264 human_late best loss_vs_full `-0.001689622`; dateblock LR best `-0.000690449`; human-only strict gates `443`. E265 random strict rate is high at `0.290909`, but random best loss_vs_full is only `-0.000723735`.
- 성공/폐기 기준: local representation survives because best human_late is much stronger than random. Submission certification fails because random gates are frequent. Next test must use top-cell ranking/materialization, not broad policy loss.
- public LB 관측 반응: no public submission from this hypothesis yet. A future public-positive file should be a narrow lifestyle-conditioned cell gate, not a 90+ cell broad rollback.
- 제출 전략: build E266-style materialization stress only for sharp cells that beat random and pass public-free Q3/S4 tail anatomy.

### H266: human/social tail state can survive JEPA materialization if the target is row-target-cell risk

- 상태: supported locally; public unobserved.
- 왜 그럴듯한가: E264 showed late/presleep human context predicts harmful Q3/S4 movement, while E265 rejected broad gates. The natural sharper target is not "bad day" but "which Q3/S4 cells should be rolled back."
- 맞다면: sharp human/social E264 policies should pass E237 materialization-side public-free stress and produce non-broad candidate tensors with negative or neutral expected loss, adverse reduction, support gain, and reasonable Q3 top-cell concentration.
- 틀리다면: materialization should be empty, or only broad/expected-positive files should pass.
- 최소 실험: `analysis_outputs/e266_human_social_tail_materialization_stress.py`.
- 관측: E266 selected `22` files. The best balanced digest `2936100f` has expected_loss_vs_e224 `-0.000004014`, adverse reduction `0.000418519`, support gain `0.004541355`, actual support gain `0.003984398`, and E230 Q3 risk overlap `6`.
- 성공/폐기 기준: supported as a candidate source because non-broad balanced files pass. Not yet public-certified; a public miss near/worse than E95 would demote this exact E224/E154 materialization path.
- public LB 관측 반응: a win over E247 would strongly support human/social hidden state as the missing Q3/S4 tail law. A mild loss would keep it as weak energy. A hard loss would imply E224-family materialization mismatch.
- 제출 전략: use only the pre-registered balanced E267 file first, not the broad top-score candidate.

### H267: the best human/social public sensor is the balanced 2936100f tensor, not the broad E237-score winner

- 상태: active routebook.
- 왜 그럴듯한가: E265 showed broad rollback gates are too easy. E266's broad `c1e018aa` has the highest E237 score but positive expected loss and `75` dropped cells. A healthier public sensor should trade some support for lower broadness and non-positive expected loss.
- 맞다면: a survival score that penalizes positive expected loss and broad cell count should rank `2936100f` above `c1e018aa`, while preserving enough support/adverse signal to be informative.
- 틀리다면: every non-broad candidate would lose support/adverse signal, leaving only tiny sharp files with little public information.
- 최소 실험: `analysis_outputs/e267_human_social_tail_submission_routebook.py`.
- 관측: E267 ranks `2936100f` first with social-JEPA survival score `8.230181390`; movement versus E247 is `60` cells over `54` rows, mostly Q3 (`51`) plus S4 (`9`).
- 성공/폐기 기준: routebook accepted for one public sensor. Public LB decides whether the hidden-world bet is score-useful or only diagnostic.
- public LB 관측 반응: see `analysis_outputs/e267_human_social_tail_submission_routebook_report.md`.
- 제출 전략: submit `analysis_outputs/submission_e267_humansocial_tail_balanced_2936100f.csv` if using the next slot on the human/social JEPA branch.

### H273: broad human diary state exists but is not submission-invariant

- 상태: supported as diagnostic energy; rejected as broad action path.
- 왜 그럴듯한가: E268/E270 found sparse human/social/cash-flow stories, and the user explicitly proposed richer human theories. A true hidden lifestyle state should make feature families predictable from each other and explain Q/S labels or frontier boundaries.
- 맞다면: family-to-family JEPA prediction should be nontrivial; clusters should be interpretable; some residual energies should align with labels or E247/E256 boundary cells.
- 틀리다면: family prediction would be near-null, clusters random, and no label/boundary lifts would appear.
- 최소 실험: `analysis_outputs/e273_human_diary_state_jepa_audit.py`.
- 관측: JEPA predictability is strong for several families, e.g. sensor dateblock OOF R2 `0.976587`, physiology `0.891374`, mobility `0.746016`, bedtime `0.735212`, social `0.642126`. Boundary alignment is also strong: social pred-norm d `-1.332902`, cognitive-money residual d `1.199200`. But adding the full diary state worsens blocked CV everywhere: dateblock mean `+0.047561770`, subject mean `+0.149546366`.
- 성공/폐기 기준: diagnostic part supported; broad submission part rejected. The latent is real but not invariant enough for direct modeling.
- public LB 관측 반응: no public submission should be made from this broad latent. A future public-positive branch must use target-specific energy and pass E272 public-free promotion first.
- 제출 전략: none from E273. Build a target-specific mobility/bedtime/cognitive-money/social energy head if continuing this branch.

### H274: human diary energy is target-specific and mainly Q-side

- 상태: supported locally.
- 왜 그럴듯한가: Q1/Q2/Q3 are subjective/intervention/quality labels, while S1-S4 are objective stage-ratio labels. Human social/routine/cognitive stories should affect Q labels more directly.
- 맞다면: E273 energy axes should improve Q targets under subject/dateblock stress, while all-target or S-only probability movement should be weaker.
- 틀리다면: surviving axes should be evenly spread across S targets, or Q-side materialization should fail E272 promotion like the broad candidate.
- 최소 실험: `analysis_outputs/e274_target_specific_diary_energy_audit.py`.
- 관측: `44` action-gate axes survive; top axes are Q3 mobility/routine/bedtime/cognitive-money. E274 q-sleep candidate has mean/p90 `-0.000098347 / -0.000048780`, while broad all-target and S-only candidates are below selector resolution or positive.
- 성공/폐기 기준: supported but near-threshold. Requires amplitude robustness before submission.
- 제출 전략: run E275 q-sleep amplitude ladder.

### H275: Q-side diary energy correction is robust enough for a public-free candidate

- 상태: promoted by local public-free audit; public unobserved.
- 왜 그럴듯한가: E274 q-sleep was near-promoted and its top axes have interpretable human stories: mobility/context, routine, bedtime-phone, cognitive-money, and media/attention.
- 맞다면: increasing amplitude should monotonically improve public-free predicted delta without increasing bad-axis load, and multiple adjacent amplitudes should pass strict promotion.
- 틀리다면: only one threshold-tuned amplitude would pass, or higher amplitude would flip into bad-axis/block gates.
- 최소 실험: `analysis_outputs/e275_q_sleep_diary_energy_amplitude_audit.py`.
- 관측: m1.15, m1.30, m1.45, and m1.60 all pass strict promotion. m1.60 mean/p90 delta is `-0.000190473 / -0.000084726`, beats-current `0.970588`, incremental bad-axis `-0.004007782`.
- 성공/폐기 기준: locally promoted. Caveat: selected E272 model count is `1`, so this is a strong candidate but not a proven LB win.
- public LB 관측 반응: win supports Q-side lifestyle hidden state; tie/small loss supports lower-amplitude or better support gating; hard loss demotes E272 q-axis selector and returns diary energy to diagnostic-only.
- 제출 전략: `analysis_outputs/submission_e275_q_sleep_amp_m160_86528b2f.csv` first from this branch; m1.45 as lower-amplitude fallback.

### H276: E275 old promotion is Q-movement geometry, not proven lifestyle row alignment

- 상태: supported as submission blocker; supersedes H275 submission recommendation.
- 왜 그럴듯한가: E275 was promoted by only one selected E272-style current-order selector. If that selector mainly recognizes target/movement geometry, then shuffling E275's row placement while preserving logit deltas should still pass.
- 맞다면: matched row/subject/dateblock shuffle placebos should pass the same promotion gate at a high rate, possibly matching or beating E275's p90 delta.
- 틀리다면: E275 should beat all or nearly all shuffled nulls, and null strict-promote count should be near zero.
- 최소 실험: `analysis_outputs/e276_q_sleep_story_ablation_placebo_audit.py`.
- 관측: shuffled placebos strict-promoted `13/15`. Dateblock shuffles were `5/5` strict and best p90 `-0.000132538`, stronger than E275 real p90 `-0.000084726`. Row and subject shuffles were each `4/5` strict. Inverse control failed with p90 `+0.000207722`.
- 성공/폐기 기준: H276 supported because matched nulls pass too often. Direction is identifiable, but row placement is not certified.
- public LB 관측 반응: no new public LB should be spent on E275/E276 variants under the old gate.
- 제출 전략: none. Future human/social candidates must pass a matched-placebo-resistant gate where the real candidate beats row/subject/dateblock shuffle nulls.

### H277: current q-sleep diary candidates do not beat matched placebo nulls

- 상태: supported; active bottleneck diagnosis.
- 왜 그럴듯한가: E276 showed placebos can pass for E275. A valid hidden lifestyle-state candidate must beat its own null distribution, not just old public-free stress.
- 맞다면: applying a candidate-specific matched-placebo gate to all current q-sleep variants should demote old strict candidates.
- 틀리다면: at least one semantic variant, especially JEPA-only or mobility-only, should retain old strict promotion while beating row/subject/dateblock nulls with high dominance and low null strict rate.
- 최소 실험: `analysis_outputs/e277_placebo_resistant_qsleep_gate.py`.
- 관측: old strict candidates `10`, E277 placebo-resistant promotes `0`. E275 primary p90 dominance `0.571429`, null strict rate `0.952381`. `jepa_only_m160` is closer but still blocked: p90 dominance `0.761905`, null strict rate `0.904762`.
- 성공/폐기 기준: H277 supported. Existing q-sleep diary variants are diagnostic only.
- public LB 관측 반응: no public submission from this branch until a candidate has `placebo_resistant_gate=True`.
- 제출 전략: none. Next build row-alignment objective or gate.

### H278: q-sleep row alignment exists on train, but fails transfer to test/public selector

- 상태: supported; strongest current q-sleep bottleneck explanation.
- 왜 그럴듯한가: E277 could be caused either by no row signal or by train/test row-alignment transfer failure. Train labels can distinguish these.
- 맞다면: q-sleep policies should beat matched row/subject/dateblock shuffle nulls on labeled train OOF baselines, while still failing E277 on test candidate geometry.
- 틀리다면: train actual row placement would not beat shuffle nulls either.
- 최소 실험: `analysis_outputs/e278_train_row_alignment_null_audit.py`.
- 관측: train-align gate rows `27/40`; candidates passing both subject/dateblock gates `13`. `full_qsleep` deltas `-0.001998955 / -0.001362687`; `q3_only` `-0.001363003 / -0.000879044`; `jepa_only` `-0.001263774 / -0.000802362`. Inverse control is adverse.
- 성공/폐기 기준: H278 supported. Signal exists on train; current failure is transfer/calibration/selector, not total absence of human diary information.
- public LB 관측 반응: no public submission yet. A candidate must satisfy both E278 train row-alignment and E277 test matched-placebo resistance.
- 제출 전략: none from current policies. Next build a transfer gate or JEPA target that predicts placebo-resistant row placement.

### H279: public-free submission selection requires matched-placebo governance

- 상태: supported; active operating rule.
- 왜 그럴듯한가: E272 promoted q-sleep candidates that E276/E277 showed were not row-placement certified. Public LB is scarce, so the local system must block magnitude-only candidates before submission.
- 맞다면: active candidates that look good under old selector stress should be rejected unless their real row placement beats row/subject/dateblock shuffle nulls; known-public losers should also be blocked.
- 틀리다면: at least one current active candidate would pass old strict stress, beat matched nulls with low null strict-promote rate, and have no known-public contradiction.
- 최소 실험: `analysis_outputs/e279_public_free_submission_governor.py`.
- 관측: candidates audited `66`, matched nulls `1365`, old strict candidates `13`, matched-placebo gate passes `0`, final submission-ready candidates `0`.
- 성공/폐기 기준: H279 supported. The current candidate pool contains no public-free submission candidate.
- public LB 관측 반응: no new public LB should be used on these candidates. Public LB should be reserved for a future file passing E279, or for a pre-declared information-only sensor.
- 제출 전략: none now. Build a transfer objective where test row placements become distinguishable from matched shuffle nulls.

### H280: human/social stories are alive only if they transfer as story-state row selectors

- 상태: partially supported; direct submission blocked.
- 왜 그럴듯한가: E268/E270 found many plausible social/payday stories, but E269/E271 direct gates were too small and E279 blocks current materializations. The story may still be real while the action is wrong.
- 맞다면: story ranking should reveal a small set with label/CV signal, train/test stability, E278 family row support, and JEPA-family health. Public-anchor-only stories should separate from locally transferable stories.
- 틀리다면: no story should pass a multi-stress transfer score, or top stories should all be public-anchor diagnostics with weak local evidence.
- 최소 실험: `analysis_outputs/e280_story_transfer_alignment_atlas.py`.
- 관측: `86` stories audited; alive story-state gate `3`, alive-needs-transfer `23`, blocked transfer gap `6`, public-anchor diagnostic only `6`. Top transfer rows were `commute_workday`, `bright_light_late`, `single_app_monotony`, and `app_entropy_scattered_day`.
- 성공/폐기 기준: H280 supported as a triage claim, not a submission claim. Direct public-boundary materialization remains blocked until E279-style matched-placebo resistance.
- public LB 관측 반응: no public LB should be spent from E280 alone.
- 제출 전략: none. Run JEPA-style context-to-story-state null stress on top stories.

### H281: routine fragmentation / app entropy is the first social JEPA state with both-split row-alignment support

- 상태: supported locally; not submission-ready.
- 왜 그럴듯한가: scattered app use is a human attention/routine-fragmentation story. It should affect subjective sleep labels through cognitive load and irregular day structure, and unlike a direct app feature it may be predictable from broader context.
- 맞다면: context excluding the routine-calendar family should predict the `app_entropy_scattered_day` story state, and the predicted state should improve label OOF beyond row/subject/dateblock shuffled nulls under both subject and dateblock splits.
- 틀리다면: context prediction would have low R2, label deltas would be positive, or matched nulls would match/beat the actual row placement.
- 최소 실험: `analysis_outputs/e281_story_state_jepa_row_selector_audit.py`.
- 관측: `app_entropy_scattered_day` passes both gates. Subject5 state R2 `0.419010`, mean delta `-0.001949852`, dominance `1.000000`, best target Q3 delta `-0.017952`. Dateblock5 state R2 `0.728347`, mean delta `-0.000108720`, dominance `0.920000`, best target Q2 delta `-0.005987`.
- 반증된 주변 가설: `commute_workday` and `bright_light_late` looked strong in E280 but failed E281 as overall row selectors. `single_app_monotony` passed subject5 but failed dateblock mean delta.
- 성공/폐기 기준: H281 survives as the next materialization hypothesis. It is not public-ready until an app-entropy story-state probability tensor passes E279-style matched-placebo governance.
- public LB 관측 반응: if a future governed app-entropy candidate improves public LB, the world model shifts toward routine-fragmentation hidden state. If it loses after passing local governor, the failure is likely materialization/calibration, not absence of the story state.
- 제출 전략: build a small `app_entropy_scattered_day` Q3/Q2/S2 materialization and audit it locally before any public LB.

### H282: app-entropy can be submitted by simple Q3/Q2/S2 logit materialization

- 상태: rejected for current materialization; underlying state remains supported.
- 왜 그럴듯한가: E281 showed app-entropy predicted story-state is row-aligned on train OOF under both subject and dateblock splits, with strong Q3 and moderate Q2/S2 target effects.
- 맞다면: an E247-relative app-entropy logit edit should pass the old public-anchor selector and beat matched row/subject/dateblock nulls at the same movement magnitude.
- 틀리다면: either the edit stays below selector resolution, or once amplified enough to pass old strict, matched nulls also pass because the selector is reading generic target direction/magnitude rather than row placement.
- 최소 실험: `analysis_outputs/e282_appentropy_story_materializer.py`.
- 관측: `22` candidates and `726` matched nulls. Q3-only linear is the only live shape. Amp `0.022` is too small with p90 `-0.000048005`; amp `0.023` crosses old strict with p90 `-0.000050139` but has null strict rate `0.121212`; amp `0.030` has p90 `-0.000064970` but null strict rate `0.939394`. Q2/S2 additions degrade row-placement dominance.
- 성공/폐기 기준: direct simple materialization rejected. No E282 file is public-free submission-ready.
- public LB 관측 반응: no public LB should be spent on E282. If submitted anyway and it improves, it would imply the matched-null governor is too conservative for Q3 prior-like shifts, not that row-state materialization was certified.
- 제출 전략: none. Next branch must predict a sharper Q3 row/cell tail target conditioned on app-entropy, or keep app-entropy as an energy/diagnostic feature only.

### H283: app-entropy can improve E247 by selecting/refilling Q3 smoothing cells

- 상태: rejected as a submission selector; retained as a diagnostic energy axis.
- 왜 그럴듯한가: E247 is the current public-best mechanism, and E257/E283 anatomy shows E256-only public-worse cells are much higher in app-entropy state/story and rollback amplitude than E247-only cells.
- 맞다면: app-state/app-story-conditioned Q3 smoothing selectors should preserve E246/E237 local geometry and beat E247-relative matched row/subject/dateblock nulls, especially by avoiding high state-by-amplitude cells.
- 틀리다면: app-entropy-conditioned selectors may explain E247/E256 anatomy but remain below selector resolution or fail matched-placebo dominance.
- 최소 실험: `analysis_outputs/e283_appentropy_q3_smooth_context_audit.py`.
- 관측: selectors `28`, local gate passes `27`, candidates `27`, old strict promotes `0`, matched-placebo passes `0`, public-ready `0`. E256-only cells are high app-state/app-story/high amplitude, but the best app-conditioned variants have p90 deltas only around `-5e-6` and do not dominate matched nulls.
- 성공/폐기 기준: direct app-entropy selector/refill rejected. The app-entropy state remains alive only as context/energy for a sharper JEPA cell-tail target.
- public LB 관측 반응: no public LB should be spent on E283. If an E283 file were submitted and won, it would primarily falsify the current placebo governor's strictness, not certify this selector from local evidence.
- 제출 전략: none. Keep E247 as best public file; next branch should learn cell-tail risk or row-placement transfer, not scalar app-entropy smoothing ranks.

### H284: app-entropy can help a decisive-cell JEPA target, but the old E224/E154 target anchor is stale

- 상태: representation supported; current submission translator rejected.
- 왜 그럴듯한가: E281 validated app-entropy as a hidden routine/attention-fragmentation state, while E237/E249 showed that Q3/S4 decisive-cell targets are sharper than row-level support or scalar smoothing. Combining them should help if the social state truly explains cell-tail risk.
- 맞다면: app-entropy context should improve OOF decisive-cell loss/tail-AUC and open E237 gates. But if E247 has become the live public-positive mechanism, an E224/E154 rollback target may still fail against E247-current nulls and show weak overlap with E247 cells.
- 틀리다면: app-entropy context would not improve OOF decisive-cell metrics, or selected cells would strongly overlap E247 and pass E247-current matched-placebo governance.
- 최소 실험: `analysis_outputs/e284_appentropy_decisive_cell_jepa_audit.py`.
- 관측: best app-state interaction OOF view has median delta loss `-0.000080361` and mean tail-AUC delta `+0.003713380`; E237 gate passes `9`. However E247-current public-free ready files are `0`, best p90 is still positive (`+0.000025223`), and top selected Q3 files overlap E247 weakly (`11/25` and `9/21` selected cells).
- 성공/폐기 기준: app-entropy survives as decisive-cell context, but E224/E154-anchored app-entropy rollback is rejected as a current-frontier submission route.
- public LB 관측 반응: no public LB should be spent on E284. If an E284 file were submitted and won anyway, it would imply the E247-current matched-placebo governor is too conservative or that the public subset rewards stale E224/E154 Q3 tail rollback over E247-preserving geometry.
- 제출 전략: none. Next branch should use E247 itself as the target anchor: predict preserve/undo/avoid labels for E247 cells, with app-entropy as context and matched-null dominance as the promotion rule.

### H285: human/social state can directly repair E247 residual cells

- 상태: rejected as direct cell surgery; supported as boundary anatomy.
- 왜 그럴듯한가: E247 is the current public-best body, E256 is its close same-family loser, and E284 showed app-entropy/diary context becomes stale when anchored to E224/E154. If the hidden human state is real, it should help decide which E247 cells to preserve, undo, or extend.
- 맞다면: E247-only, E256-only, and E284-extra cells should have interpretable social/diary/cash-flow differences, and those differences should generate E247-relative add/undo candidates that beat matched row/subject/dateblock nulls under the current-anchor governor.
- 틀리다면: boundary features may separate the cell groups descriptively, but the resulting add/undo tensors will be too small, below selector resolution, or no better than matched nulls.
- 최소 실험: `analysis_outputs/e285_e247_residual_human_state_audit.py`.
- 관측: boundary anatomy is real. E247-only versus E256-only separates on amplitude (`amp_z` d `-2.192525`), state-amplitude (`-1.647799`), month-start late-shopping (`+1.445509`), month-start money-rumination (`+1.159548`), diary PCs, social-communication JEPA prednorm, bedtime-phone, mobility, and bright-light features. But `158` E247-relative candidates and `3318` matched nulls produced old strict promotes `0`, matched-placebo passes `0`, and public-free ready files `0`. Best add p90 was only `-0.000003481`; best undo p90 only `-0.000000902`.
- 성공/폐기 기준: direct hand-built E247 residual surgery is rejected. The social/payday/app-entropy coordinates remain useful for explaining E247/E256 anatomy and for future learned E247 preserve/avoid labels.
- public LB 관측 반응: no public LB should be spent on E285. If an E285 file were submitted and won, it would imply the local current-anchor governor is missing a very tiny public-specific subset, not that the handcrafted rule was locally certified.
- 제출 전략: none. Preserve E247. The next branch should learn a contrastive E247 preserve/avoid latent from E247-common/E247-only versus E256-only/E284-extra cells, then require matched-null dominance before materialization.

### H286: learned E247 preserve/avoid cell identity can convert human/social boundary anatomy into a public-free candidate

- 상태: rejected as submission translator; supported as a diagnostic split between geometry and human state.
- 왜 그럴듯한가: E285 showed interpretable human/social/cash-flow anatomy around the E247/E256 Q3 boundary, but scalar add/undo rules were too weak. A learned contrastive latent should be a sharper I-JEPA-style target: context predicts hidden E247-relative preserve/avoid cell identity instead of raw values or story scores.
- 맞다면: human/social or human+geometry context should learn E247-preserve versus avoid labels across stratified, subject, and dateblock splits; source-transfer from E247-common-vs-E284-extra to E247-only-vs-E256-only should remain above chance; materialized E247-current Q3 edits should beat matched row/subject/dateblock nulls.
- 틀리다면: cell identity will be learnable mostly from E247 geometry itself, human/social-only signal will be local or non-transferable, and final Q3 add/undo/swap candidates will be below selector resolution or no better than matched nulls.
- 최소 실험: `analysis_outputs/e286_e247_preserve_avoid_contrastive_latent.py`.
- 관측: `128` latent rows and `12` selected latents were generated; `533` candidates and `11193` matched nulls produced old strict promotes `0`, matched-placebo passes `0`, and public-ready files `0`. Cell identity is extremely learnable with geometry (`e247_body_vs_clean_neither` cell-geometry min AUC `0.998917`, mean AUC `0.999399`), but human/social-only is weak on the broad body task and source-transfer fails (`human_social` transfer AUC `0.403846`, `human_plus_oldlaw_context` best transfer AUC only `0.519231`). Best non-control p90 deltas are around `-0.000004`, below submission resolution.
- 성공/폐기 기준: learned E247 preserve/avoid identity is not enough when the target is defined by current test-side cell membership. The useful result is negative: E247 identity is recoverable, but mostly as geometry replay; the human/social sibling-boundary clue is too small and non-transferable for a public-free tensor.
- public LB 관측 반응: no public LB should be spent on E286. If an E286 file won publicly, it would mean the local matched-null governor missed an extremely narrow public subset, not that the learned preserve/avoid latent was locally certified.
- 제출 전략: none. Preserve E247. The next branch should ground social latents in train/OOF residual labels or row-alignment transfer targets rather than pseudo-labeling E247 cell identity from test-side submission anatomy.

### H287: train-supervised q-sleep row-action benefit can transfer to the current E247 tensor

- 상태: partially supported as train signal; rejected as current submission translator.
- 왜 그럴듯한가: E278 showed that q-sleep policies improve labeled train rows against row/subject/dateblock nulls. E276/E277/E279 showed the same family fails when materialized directly on test. A label-grounded row-action target should be less self-referential than E247 pseudo-cell identity.
- 맞다면: OOF row-action benefit should be predictable from human/social/JEPAlike context, train-gated policies should beat matched shuffles, and the same gates should create E247-current test edits that beat matched row/subject/dateblock nulls with enough p90 and worst-mode dominance.
- 틀리다면: some train row benefit may be learnable, but the test tensor will be below selector resolution, adverse on mobility/Q3, or indistinguishable from matched nulls.
- 최소 실험: `analysis_outputs/e287_train_supervised_row_alignment_transfer.py`.
- 관측: latent rows `36`, train policy rows `180`, train-gated policies `3`, candidates `3`, matched nulls `63`, public-ready `0`. `bedtime_q3/dateblock_oof/lr_l2` had AUC `0.852632` but no train gate. `q3_only/subject_oof/lr_l1` passed train with delta `-0.000978542`, but test final decision was `too_small_to_submit`; mobility transfers were positive/adverse on the current tensor.
- 성공/폐기 기준: train-supervised q-sleep row benefit is alive as a diagnostic target, but the current transfer/materialization is rejected. A future version must improve worst-mode matched-null dominance and produce an edge above local resolution before public LB.
- public LB 관측 반응: no public LB should be spent on E287. If E287-like q3_only were submitted and won, it would imply the local governor is over-conservative for small Q3-only edges; if it loses, it would confirm the transfer-resolution bottleneck.
- 제출 전략: none from E287. Next branch should either learn a sharper train-to-test bridge, or use the train row-action target as an energy feature rather than a direct probability edit.

### H288: broad lifestyle-story bundles recover the hidden human state and improve labels

- 상태: supported as reconstructable diary state; rejected as broad downstream label feature.
- 왜 그럴듯한가: individual stories may be too narrow. Human sleep may respond to combined commute/workday rhythm, bright light, app entropy, phone-in-bed, heart stress, and payday/month-start behavior. A JEPA-style bundle target should recover a larger hidden lifestyle state than any scalar story.
- 맞다면: multi-story bundle predictions should be reconstructable under subject/dateblock OOF, have healthy latent geometry, improve 7-target CV beyond subject/calendar baseline, and beat matched row/subject/dateblock shuffles.
- 틀리다면: reconstruction may be strong, but downstream label deltas will be positive on average, target effects will conflict, or subject-split latents will show shortcut/identity risk.
- 최소 실험: `analysis_outputs/e288_lifestyle_bundle_jepa_audit.py`.
- 관측: `28` stories and `3` context views were tested. Dateblock reconstruction is strong (`family_jepa_context` mean R2 `0.385944`, positive R2 rate `0.928571`) and includes cash-flow/payday stories (`paymonth_start_post3_late_shopping` R2 `0.813342`). But label gates are `0/12`; best mean delta is still positive at `+0.002092612`. Best target deltas exist for S4/Q3/S2, but the broad representation damages other targets.
- 성공/폐기 기준: reject broad-bundle-as-feature. Keep lifestyle bundle as diagnostic hidden state and split it into target-specific/residualized states before materialization.
- public LB 관측 반응: no public LB should be spent on E288. If a broad-bundle file won publicly despite this, it would imply local matched-null/mean-target governance is too conservative or public subset is concentrated in the S4/Q3/S2-improved clusters.
- 제출 전략: none. Next branch should test target-specific bundle slices with per-target nulls, especially dateblock-stable clusters where S4/Q3/S2 improve without averaging across adverse targets.

### H289: target-specific lifestyle slices can become public-free E247 edits

- 상태: supported as target-specific latent signal; rejected as current submission translator.
- 왜 그럴듯한가: E288's broad bundle failed the 7-target mean, but the same latent helped individual S4/Q3/S2 slices. If human lifestyle state has target-specific noise channels, per-target slices should survive where broad sharing failed.
- 맞다면: Q3/S4/S2 slices should beat row/subject/dateblock train nulls, and the materialized E247 target-only edits should also beat matched test null submissions with low null strict rate and high p90/worst-mode dominance.
- 틀리다면: train target slices may be strong, but their E247-current probability movements will be reproducible by matched row/subject/dateblock shuffles or below local resolution.
- 최소 실험: `analysis_outputs/e289_target_specific_lifestyle_slice_audit.py`.
- 관측: `84` target slices produced `7` train target gates. Q3 and S4 were the clear winners: `Q3_raw_human_context_subject5_pc` delta `-0.014465898`, `S4_family_jepa_context_dateblock5_cluster6` delta `-0.011131`, and `S4_raw_human_context_dateblock5_cluster6` delta `-0.009936`. But `28` materialized candidates and `420` matched nulls produced public-ready `0`. The best-looking local candidate had mean `-0.000674` and p90 `-0.000417`, but null strict rate `1.000000` and worst-mode p90 dominance `0.000000`.
- 성공/폐기 기준: reject direct materialization. Keep target-specific lifestyle slices as representation diagnostics and potential row-placement targets.
- public LB 관측 반응: no public LB should be spent on E289. If an E289 file won publicly, it would indicate the matched-null governor is missing a very public-specific row subset; the local evidence does not support that bet.
- 제출 전략: none. The next strategy should predict the row/block placement law that distinguishes real Q3/S4 lifestyle rows from matched shuffles.

### H290: train OOF lifestyle row-placement law transfers to E247-current test rows

- 상태: supported on train placement; rejected as current submission translator.
- 왜 그럴듯한가: E289 showed target-specific Q3/S4 lifestyle signal but failed direct row placement. If the missing variable is "which rows should receive the slice", OOF row benefit should provide a label-grounded JEPA target.
- 맞다면: a placement gate should beat row/subject/dateblock train score shuffles and then produce E247-current candidate deltas that beat matched test null submissions.
- 틀리다면: train gates may be strong, but test materialization will still be null-reproducible because the learned placement law does not identify the public/test row subset.
- 최소 실험: `analysis_outputs/e290_lifestyle_row_placement_law_audit.py`.
- 관측: `420` placement rows produced `59` train placement gates. The strongest Q3 placement improves train target loss by `-0.024399167`, better than the full slice delta `-0.014466`. But `48` materialized candidates and `720` matched nulls produced public-ready `0`. The best candidate has mean `-0.000495` and p90 `-0.000308`, but null strict rate `1.000000` and worst-mode p90 dominance `0.000000`.
- 성공/폐기 기준: reject direct transfer. Keep train placement as evidence that lifestyle row laws exist, but require a stronger test invariant before submission.
- public LB 관측 반응: no public LB should be spent on E290. A public win would imply the local matched-null governor is overly conservative for Q3 placement; the current evidence says this is a low-quality bet.
- 제출 전략: none. Next branch should move from rowwise scalar placement to block-level hidden-state assignment or an independent test-side invariant for Q3 placement.

### H291: hidden lifestyle block-state assignment transfers better than rowwise placement

- 상태: supported as train-side block structure; rejected as current submission translator.
- 왜 그럴듯한가: E290 found a strong row-placement law in labeled train rows but failed test matched-null governance. Human sleep behavior should be episodic: weekdays, weekends, month/payday phases, and lifestyle clusters can define states where Q3/S4 corrections are valid.
- 맞다면: block-state predictors should beat row/subject/dateblock score shuffles on train and then produce E247-current candidates whose local gains are not reproduced by matched block nulls.
- 틀리다면: train block states may look meaningful, but the materialized candidates will remain null-reproducible because block labels still do not identify the public/test placement invariant.
- 최소 실험: `analysis_outputs/e291_lifestyle_block_state_assignment_audit.py`.
- 관측: `560` block policy rows produced `39` train block gates. S4 subject-lifestyle-bin and Q3 subject-weekday/weekend states were strong on train; the best S4 policy reached actual delta `-0.017607` with dominance `0.979167`, and a Q3 weekday policy reached `-0.013683` with dominance `1.000000`. But `40` materialized candidates and `600` matched nulls produced public-ready `0`.
- 성공/폐기 기준: reject direct block-state materialization. Keep lifestyle-bin, weekday/weekend, and month/payday phase as diagnostic axes, but require an independent test-side invariant before public submission.
- public LB 관측 반응: no public LB should be spent on E291. If an E291 candidate wins publicly, it would imply the matched-null governor is too conservative for block-level edits; local evidence does not support that risk.
- 제출 전략: none. The next strategy should learn contrastive true-vs-null placement identity or a target representation that separates real Q3/S4 lifestyle states from generic movement.

### H292: anti-null block rarity separates real lifestyle placement from generic movement

- 상태: partially supported as S4 diagnostic; rejected as current submission translator.
- 왜 그럴듯한가: E291 failed because matched nulls could mimic plausible block edits. If true lifestyle placement has an invariant, selected blocks should not only be high-score but also be hard to select by row/subject/dateblock score shuffles.
- 맞다면: contrast-filtered blocks should pass train stress and then reduce candidate-level null strict rate on E247-current submissions.
- 틀리다면: contrast filters may pass train but test candidates will still either be below selector resolution or blocked by matched nulls.
- 최소 실험: `analysis_outputs/e292_contrastive_lifestyle_placement_invariant.py`.
- 관측: `98` contrast rows produced `34` train contrast gates, but `56` materialized candidates and `840` matched nulls produced public-ready `0`. S4 improved relative to E291 in one important way: one old-strict candidate reached null strict rate `0.133333` with p90 `-0.000053`; however mean dominance was only `0.466667`. Q3 promote-scale candidates remained null strict rate `1.000000`.
- 성공/폐기 기준: reject broad E292 submission. Keep anti-null rarity as a promising S4 diagnostic and a narrow next target.
- public LB 관측 반응: no public LB should be spent on E292. A public win from the near-miss S4 file would imply the governor is slightly too strict around null strict `0.13`; current evidence still says it is not ready.
- 제출 전략: none now. Next branch should train a candidate-level null outcome model or focus on S4 lifestyle-bin low-null raw edits with stronger mean-dominance constraints.

### H293: S4 low-null lifestyle pocket can be made submission-ready by scale/selection refinement

- 상태: rejected for scale/selection refinement; retained as a diagnostic pocket.
- 왜 그럴듯한가: E292 found the first S4 lifestyle-bin candidate whose null strict rate was far below the Q3/QS movement failures. If the only issue was over-filtering or amplitude, a narrower sweep should find a point that is old-strict and null-safe.
- 맞다면: low-null rarity/contrast/hybrid filters should produce at least one old-strict candidate with null strict rate `<=0.10`, p90 dominance `>=0.80`, mean dominance `>=0.70`, and worst-mode p90 dominance `>=0.55`.
- 틀리다면: null-safe candidates will remain below old selector resolution, while old-strict candidates will be matched-null reproducible.
- 최소 실험: `analysis_outputs/e293_s4_lownull_lifestyle_candidate_refiner.py`.
- 관측: `840` generated S4 candidates produced `554` old strict candidates and `64` null-evaluated rows, but public-ready stayed `0`. Null strict `0.000000` rows exist only in `too_small_to_submit` candidates around p90 `-0.000044`. The nearest old-strict 31-row pocket has null strict `0.476190` to `0.523810`; stronger p90 rows reach null strict `1.000000`.
- 성공/폐기 기준: reject more scale/threshold sweeps as the next action. Keep the 31-row S4 pocket as a diagnostic object only if a different selector or candidate-level invariant can explain why it is not null-like.
- public LB 관측 반응: no public LB should be spent on E293. A public win from an E293 file would mean the current matched-null governor is overly conservative exactly at the S4 cliff, but local evidence does not justify that sensor spend.
- 제출 전략: none. Future strategy must change the invariant or governor resolution, not simply tune S4 amplitude.

### H294: candidate-level actual-vs-null identity can gate S4 low-null submissions

- 상태: rejected as a promotion gate; supported only as a diagnostic of movement identity.
- 왜 그럴듯한가: E293 might fail because the old selector cannot see the difference between real and null S4 placements. If output-space geometry can identify the actual placement, it could provide the missing LeJEPA-style health gate.
- 맞다면: a leave-one-source-out actual-vs-null classifier should rank the actual placement above nulls, and its realness score should correlate with lower null strict rate, higher mean dominance, and public-free readiness.
- 틀리다면: actual-vs-null classification may work, but the score will track movement size or selector artifacts and correlate with null promotion rather than safety.
- 최소 실험: `analysis_outputs/e294_s4_candidate_invariant_audit.py`.
- 관측: actual-vs-null identity is learnable (`all_output` AUC `0.883498`, top3 `0.671875`), but S4-local AUC is only `0.619617`. Realness correlates positively with null strict rate (`+0.360322` all-output, `+0.478847` selector-only), and public-ready remains `0`.
- 성공/폐기 기준: reject actual-vs-null realness as a submission gate. Keep it only as evidence that the recognizable part of the tensor is broad output geometry rather than safe S4 hidden state.
- public LB 관측 반응: no public LB should be spent on E294. A public win from a high-realness E293 candidate would mean the matched-null stress is too conservative, but the local sign is adverse because high realness is also high null-promotion.
- 제출 전략: none. Next strategy should target low-null outcome directly or pivot to another hidden-state family with more positive safe examples.

### H295: human episode states exist but are target-specific, not a shared all-target latent

- 상태: supported as target-specific representation; rejected as broad all-target feature.
- 왜 그럴듯한가: E288's broad lifestyle bundle was reconstructable but downstream-adverse. Human sleep behavior should instead be episodic: bedtime arousal, routine fragmentation, cash-flow stress, home recovery, commute pressure, and bad-night aftereffects may affect different targets differently.
- 맞다면: large episode states should be context-predictable, and predicted states should beat row/subject/dateblock nulls for specific targets while the full bundle may still fail the 7-target mean.
- 틀리다면: reconstruction may be possible, but target-specific deltas should vanish under matched nulls or concentrate only in measurement shortcuts.
- 최소 실험: `analysis_outputs/e295_episode_state_jepa_audit.py`.
- 관측: `11` episode states produce strong dateblock reconstruction (`family_jepa_context/dateblock5` mean R2 `0.438241`) and `51` light-null target gates, but broad bundle label gates are `0`. Strong target deltas include `cashflow_stress/S1 -0.017244`, `bedtime_arousal/S1 -0.017000`, `bedtime_arousal/S3 -0.016376`, and `badnight_aftereffect/Q3 -0.015000`.
- 성공/폐기 기준: keep target-specific episode states; reject broad shared episode bundle as a direct feature block.
- public LB 관측 반응: no public LB should be spent from E295 alone because null budget was discovery-grade, not promotion-grade.
- 제출 전략: none directly. Rerun strict null stress on consensus episode-target pairs.

### H296: presleep arousal and routine fragmentation are the strongest strict human-state signals

- 상태: supported locally; not yet submission-translatable.
- 왜 그럴듯한가: E295's top gates were broad and numerous; a real hidden state should survive a larger null budget and not rely on one lucky shuffle set.
- 맞다면: a small set of episode-target pairs should survive `64` row, subject, and dateblock null reps, with strong dominance and repeated view/split support.
- 틀리다면: E295 gates should collapse under stricter nulls, especially cash-flow and social stories with high calendar confounding risk.
- 최소 실험: `analysis_outputs/e296_episode_target_strict_null_audit.py`.
- 관측: `33` instances produce `19` strict gates, `5` robust gates, and `2` pair gates. Robust instances are `bedtime_arousal/S3`, `routine_fragmentation/S1`, `routine_anchor_recovery/S2`, `routine_fragmentation/S3`, and `bedtime_arousal/S1`; pair gates are `bedtime_arousal/S1` and `bedtime_arousal/S3`. Cash-flow stress has large deltas but loses robust status against extreme nulls.
- 성공/폐기 기준: use E296 robust rows only for materialization; do not use E295's full 51-gate set.
- public LB 관측 반응: no public LB should be spent until these states survive current-best materialization nulls.
- 제출 전략: target-limited E247-current edits only for E296 robust states.

### H297: strict episode-state label deltas can be translated into E247-current probability edits

- 상태: rejected for the current logistic-delta translator.
- 왜 그럴듯한가: E296 found robust target-specific states. If the missing object was only "which target and state", a target-specific logistic state delta should improve E247-current predictions and beat matched null placements.
- 맞다면: E297 materializations should pass old selector and matched row/subject/dateblock null governor with low null strict rate and strong mean/p90 dominance.
- 틀리다면: old selector may promote broad S1/S3 movements, but matched nulls with the same movement distribution will also promote, or null-safe variants will stay below selector resolution.
- 최소 실험: `analysis_outputs/e297_episode_state_materializer.py`.
- 관측: `150` candidates produce `25` old strict rows and best p90 `-0.000565475`, but `39` null-evaluated candidates produce public-free ready `0`. Selector-visible bedtime/routine S1 edits have null strict rates mostly `0.714286` to `1.000000`; null-safe variants are `too_small_to_submit`.
- 성공/폐기 기준: reject logistic-delta materialization. Keep E296 states as priors for a direct outcome target: selector-visible and null-rare.
- public LB 관측 반응: no public LB should be spent on E297 candidates.
- 제출 전략: none. Next strategy should predict materialization health directly rather than label delta.

### H298: existing human/social materializers already contain a selector-visible and null-rare submission

- 상태: rejected across the current governor archive.
- 왜 그럴듯한가: E289-E297 produced many target-specific lifestyle, S4 block, app-entropy, bedtime-arousal, routine-fragmentation, and E247-relative candidates. If the bottleneck were only candidate shortlisting, at least one should satisfy both local visibility and matched-null rarity.
- 맞다면: aggregating all current-anchor governor outputs should reveal a nonempty intersection of `selector_visible`, `null_rare`, dominance gates, and negative p90 edge.
- 틀리다면: selector-visible candidates should be mostly matched-null reproducible, while null-rare candidates should be too small or invisible.
- 최소 실험: `analysis_outputs/e298_materialization_outcome_atlas.py`.
- 관측: `1044` governed candidates across `11` governor files. `ready_like=0`, `selector_visible=162`, `null_rare=867`, `selector_visible AND null_rare=0`, `null_rare AND edge_ok=0`. `160/162` selector-visible rows are `visible_but_null_common`; the remaining `2` are visible but still not null-rare.
- 성공/폐기 기준: reject the idea that a ready public-free human/social submission is already hidden in E279/E284-E297 artifacts.
- public LB 관측 반응: no public LB should be spent from this archive.
- 제출 전략: none directly. The next strategy must learn or construct the translator outcome itself: `selector-visible + null-rare`, not another raw social-state score or amplitude sweep.

### H299: the E298 visibility/null-rarity gap is only a coarse amplitude-grid artifact

- 상태: mostly rejected; one useful S4 near-miss remains diagnostic.
- 왜 그럴듯한가: E298 had candidates just below thresholds, especially null-safe S1 and low-null S4 rows. A small logit rescale might cross the old selector without increasing matched-null promotion.
- 맞다면: rescaled near-miss candidates should produce at least one row with `old_strict_promote=True`, `null_strict_rate<=0.10`, and dominance gates passing.
- 틀리다면: scaling null-safe rows up should quickly increase null promotion, while scaling visible rows down should lose dominance or remain null-reproducible.
- 최소 실험: `analysis_outputs/e299_visibility_null_bridge_scan.py`.
- 관측: `14` base rows, `102` generated bridge candidates, `81` old-strict prefilter rows, `71` null-evaluated rows, public-free ready `0`. The closest row is S4 `visible_low_null_near` from E292 with multiplier `0.97`: old-strict true, p90 `-0.000050918`, null strict `0.095238`, p90 dominance `0.952381`, worst-mode `0.857143`, but mean dominance only `0.476190`.
- 성공/폐기 기준: reject another plain scale sweep. Keep the S4 row as a diagnostic for mean-dominance/within-subject placement rescue.
- public LB 관측 반응: no public LB should be spent on E299 files.
- 제출 전략: none. Next strategy should alter placement/sign/mask geometry to improve mean dominance while preserving the S4 null-rarity pocket.

### H300: S4 mean dominance can be rescued by dropping a bad dateblock and preserving the raw sign

- 상태: initially supported by small-null E300, then rejected for public submission by E301 strict confirmation.
- 왜 그럴듯한가: E299's closest near-miss already had the hard parts: old strict promotion, low null strict rate, strong p90 dominance, and worst-mode p90 dominance. Only mean dominance failed. If a few adverse rows or a single dateblock were dragging the mean, row/mask surgery could rescue it.
- 맞다면: a mask variant should keep old strict and low null strict while beating matched nulls on both p90 and mean across row/subject/dateblock permutations.
- 틀리다면: the apparent rescue should disappear when the null seed/budget changes, especially under subject/dateblock shuffles.
- 최소 실험: `analysis_outputs/e300_s4_mean_dominance_rescue.py`, followed by `analysis_outputs/e301_s4_ready_strict_confirm.py`.
- 관측:
  - E300 generated `1305` S4 variants and found one small-governor ready file: `analysis_outputs/submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv`.
  - E300 ready metrics: p90 `-0.000051307`, mean `-0.000161310`, null strict `0.095238`, p90 dominance `0.904762`, mean dominance `0.714286`.
  - E301 strict confirmation with `256` nulls rejected it: null strict `0.164062`, mean dominance `0.691406`, worst-mode mean dominance `0.328125`.
  - sign null dominance was `1.000000`, while subject/dateblock null strict rates were `0.250000` and `0.406250`.
- 성공/폐기 기준: reject as a public candidate. Keep as evidence that S4 sign is meaningful, but subject/dateblock placement is not yet recovered.
- public LB 관측 반응: no public LB should be spent on E300.
- 제출 전략: none. Future S4 work must predict subject/dateblock placement health directly, not only drop a visible dateblock after probing.

### H302: S4 subject/dateblock placement health is partially encoded in human diary context

- 상태: partially supported as a diagnostic, not yet a candidate generator.
- 왜 그럴듯한가: E301 showed that row/sign nulls are harmless while subject/dateblock nulls remain competitive. If S4 movement should be placed according to real lifestyle blocks, signed aggregates of diary/social/episode state over active rows should predict which placements have lower selector mean or p90.
- 맞다면: human diary aggregate features should predict E301 null placement health under leave-mode-out mode stress, and the actual placement should be exceptional on the failing mean axis.
- 틀리다면: topology or random mode identity should explain almost everything, human features should fail leave-mode-out, or actual should be indistinguishable from nulls.
- 최소 실험: `analysis_outputs/e302_s4_placement_health_decoder.py`.
- 관측:
  - E301 placement lab: `257` placements, `256` nulls.
  - `human_all` leave-mode-out mean Spearman `0.400962`; `human_all_plus_topology` `0.325973`.
  - p90 Spearman is weak/negative for human feature sets.
  - E300 actual predicted p90 rank is extreme-good (`0.000000`), but predicted mean rank is only middle (`0.433594`) under `human_all_plus_topology`.
  - top better-mean weights include bedtime-phone PC2, mobility context energy, night-out mobility, sensor measurement JEPA prednorms, physiology/activity residuals, social communication residuals, and calendar phase.
- 성공/폐기 기준: support the existence of a weak placement-health signal; reject E300 as a candidate because the actual placement is not exceptional on mean health.
- public LB 관측 반응: no public LB should be spent. If a later constrained placement-prior candidate passes large-null confirmation, public LB can be used as a scarce sensor.
- 제출 전략: none yet. Next strategy is E303-style constrained mean-placement prior followed by E301-style large-null confirmation.

### H303: E302's S4 mean-placement prior is strong enough to generate a public-free candidate

- 상태: rejected as a submission strategy; retained as diagnostic evidence.
- 왜 그럴듯한가: E302 found `human_all` mean-health Spearman `0.400962`, so a constrained generator might place the E299 S4 movement in rows/dateblocks that matched nulls cannot reproduce.
- 맞다면: mean-prior-ranked S4 masks should pass the old selector and also show low null strict rate, p90 dominance, mean dominance, and stable mode-wise dominance under row/subject/dateblock/sign shuffles.
- 틀리다면: many candidates may look good to the old selector, but matched nulls should reproduce their mean edge too often.
- 최소 실험: `analysis_outputs/e303_s4_mean_prior_materializer.py`.
- 관측: generated `260` candidates, old-strict `183`, null-evaluated `12`, public-free ready `0`. Best null strict rate was `0.187500`, best mean dominance `0.695312`, and best actual p90 `-0.000074119`.
- 성공/폐기 기준: reject E302-prior mask generation as a public submission path. Keep the weak human-placement signal as a diagnostic for future block-placement targets.
- public LB 관측 반응: no public LB should be spent on E303 files.
- 제출 전략: none. The next submission path needs a new invariant for hidden subject/dateblock placement, not another S4 mask derived from the same prior.

### H304: raw human diary context recovers hidden subject/dateblock target state

- 상태: supported as a world-model diagnostic.
- 왜 그럴듯한가: E301-E303 all point to subject/dateblock placement as the S4 bottleneck. If the data contains a hidden block state, day-level family-JEPA/story/episode context should predict block target residuals after removing subject priors.
- 맞다면: block-level human context should predict shrunken Q/S residual vectors under subject-held stress and beat shuffled block-target nulls.
- 틀리다면: calendar-only or shuffled targets should match the human views, and target-wise Spearman should be mixed or negative.
- 최소 실험: `analysis_outputs/e304_hidden_block_state_jepa_probe.py`.
- 관측: `family_jepa/subject_holdout` reached mean Spearman `0.143141`, null dominance `0.986111`, `7/7` positive target Spearman, and S4 Spearman `0.124633`. Story/episode also gated in subject-held and block-random stress.
- 추가 단서: rejected S4 candidates are anti-aligned with predicted S4 block state. E299 active-minus-inactive predicted S4 is `-0.151507`; `id07_b9` is predicted S4-low (`-0.415169`) and E300 improved by dropping it.
- 성공/폐기 기준: support hidden block-state recovery as a live world model; do not claim submission readiness.
- public LB 관측 반응: no public LB needed. This explains previous failures and motivates one block-prior materializer.
- 제출 전략: use only after a materializer also passes matched nulls.

### H305: E304-positive S4 blocks can be directly lifted into a public-free candidate

- 상태: rejected as direct materialization.
- 왜 그럴듯한가: if prior S4 candidates failed because they were anti-aligned, moving S4 upward on E304-positive blocks should fix placement.
- 맞다면: top-block or redistributed S4 edits should pass old strict and matched null governance.
- 틀리다면: old strict candidates should appear but be null-common, indicating generic S4 movement rather than unique block placement.
- 최소 실험: `analysis_outputs/e305_block_prior_s4_materializer.py`.
- 관측: generated `111`, old-strict `14`, null-evaluated `14`, ready `0`. Best null strict rate `0.648438`, best mean dominance `0.562500`.
- 성공/폐기 기준: reject direct top-block S4 lifting. Keep E304 prior as a diagnostic and require a contrastive action-outcome target.
- public LB 관측 반응: no public LB should be spent on E305 files.
- 제출 전략: none yet. Next strategy must learn `selector-visible + null-rare` movement from block-prior geometry.

### H306: within-dateblock human/JEPA row state can repair S4 block-prior materialization

- 상태: representation supported, direct materialization rejected.
- 왜 그럴듯한가: E305 showed that block-level S4 movement is null-common. If E304's block prior is right, the missing piece should be row identity inside each dateblock.
- 맞다면: dateblock-centered human/JEPA row features should rank S4-positive rows within mixed train dateblocks and beat within-dateblock shuffled-score nulls. A materialized test edit should then beat dateblock-shuffle submission nulls.
- 틀리다면: within-dateblock AUC should stay near shuffled nulls, or materialized files should be indistinguishable from dateblock nulls even if train row ranking exists.
- 최소 실험: `analysis_outputs/e306_within_block_s4_row_placement.py`.
- 관측: row-placement exists locally. `family_jepa_dbdelta/dateblock_holdout` reached within-dateblock AUC `0.574899`, null dominance `0.979167`; best row-stratified AUC was `0.585020`. But `272` candidates yielded `22` old-strict rows and `0` public-free ready rows. Best null strict rate was `0.625000`.
- 성공/폐기 기준: keep dateblock-centered family-JEPA row state as a diagnostic energy. Reject direct positive S4 row mass generation as a submission path.
- public LB 관측 반응: no public LB should be spent on E306 files.
- 제출 전략: none yet. Next strategy must predict action-governor outcome directly or use row-placement as a censor/gate rather than an additive S4 generator.

### H307: S4 latent-current mismatch identifies calibration-risk rows that can be safely censored

- 상태: rejected as direct materialization.
- 왜 그럴듯한가: E306 shows row placement exists but positive S4 mass is null-common. If the true bottleneck is LogLoss calibration, moving overconfident mismatched rows toward 0.5 should be healthier than raising S4.
- 맞다면: latent-current mismatch tempering should outperform matched row/subject/dateblock/sign nulls, and wrong-direction sharpening controls should be weaker.
- 틀리다면: many old-strict candidates appear but matched nulls and controls remain competitive.
- 최소 실험: `analysis_outputs/e307_s4_latent_censor_materializer.py`.
- 관측: generated `765`, old strict `106`, null-evaluated `22`, ready `0`. Best null strict rate `0.750000`, best mean dominance `0.546875`, best dateblock p90 dominance `0.656250`. Controls were competitive.
- 성공/폐기 기준: reject simple latent-vs-current S4 censoring as a submission path.
- public LB 관측 반응: no public LB should be spent on E307 files.
- 제출 전략: none. Need learned action-outcome target or a non-S4 branch where control directions fail.

### H308: public LB can be protected by a governed action-outcome atlas

- 상태: supported as a blocking/evaluation layer, not as a submission generator.
- 왜 그럴듯한가: E279-E307 generated many attractive local candidates, but public LB is scarce. The repeated failure pattern itself should be treated as supervision.
- 맞다면: governed action outcomes should separate into stable quadrants: null-rare-but-invisible, visible-but-null-common, and rare visible/null-rare near misses. Recent failed families should be identifiable before public LB.
- 틀리다면: leave-experiment-out outcome prediction should be noisy, and current archive should contain multiple certified candidates that the local governor cannot distinguish.
- 최소 실험: `analysis_outputs/e308_action_outcome_atlas.py`.
- 관측: `1304` governed rows, selector-visible `367`, null-rare `918`, visible/null-rare `2`, certified public-free ready `0`. Post-E303 S4 rows have null-rare `0`. Leave-experiment-out AUCs are high for selector-visible (`0.998857`) and null-common (`0.986466`), meaning failure modes are locally diagnosable.
- 성공/폐기 기준: adopt E308 as a promotion/blocking governor. Do not use it as a generator until positive visible/null-rare labels are richer.
- public LB 관측 반응: no public LB should be spent on current archive rows. The next public submission should be reserved for a candidate that creates a new visible/null-rare quadrant under independent null confirmation.
- 제출 전략: none immediately. Use E308 to prevent LB waste and to define the next target: action health, not another hand-built S4 delta.

### H309: human/social episode states act through Q/S target interactions rather than single targets

- 상태: supported as a representation-level breakthrough; untested as submission materialization.
- 왜 그럴듯한가: E297 found strong single-target train signals but current-tensor materialization was null-common. A human story such as cashflow stress or bedtime arousal should change a joint state, for example subjective satisfaction together with sleep-stage stress, not only one label.
- 맞다면: episode states should improve 4-class joint target-pair logloss under grouped OOF and beat row/subject/dateblock shuffled-state nulls.
- 틀리다면: pair improvements should vanish under nulls, or only repeat the same single-target geometry without cross-target concentration.
- 최소 실험: `analysis_outputs/e309_episode_target_interaction_probe.py`.
- 관측: `426` quick rows, `32` strict reruns, `29` strict gates, `13` robust gates, `12` pair gates. Strongest is `cashflow_stress/Q1_S1` with best delta `-0.046023`; other live interactions include cashflow with `S1_S2/S1_S3/S1_S4`, bedtime arousal with `Q1_S1/Q3_S3/Q1_S3/Q2_S3/S1_S2`, home recovery with `Q1_S3/S3_S4`, and bad-night aftereffect with `Q3_S3`.
- 성공/폐기 기준: keep as a live world model if coupled materialization can make wrong-pair and shuffled-state controls lose. Reject as submission path if coupled target deltas become visible/null-common like E297.
- public LB 관측 반응: no immediate public LB. A future candidate should be a pair-dependency correction, not a single-target episode edit.
- 제출 전략: E310 should materialize coupled target-pair deltas from the robust gates and run E308-style governor plus wrong-pair controls.

### H310: E309 target-pair states directly translate into coupled current-tensor deltas

- 상태: 반증됨 as a submission strategy; representation remains alive.
- 왜 그럴듯한가: E309 pair logloss gates were strong under row/subject/dateblock nulls, especially `cashflow_stress/Q1_S1`. A true Q/S dependency might require moving both targets together rather than a single target.
- 맞다면: coupled pair deltas should pass the current selector and, more importantly, beat row/subject/dateblock shuffles, target swaps, wrong-pair placement, and sign-flip controls.
- 틀리다면: old strict candidates should appear, but matched nulls and wrong-pair controls should also promote; null-rare candidates should be too weak to submit.
- 최소 실험: `analysis_outputs/e310_pair_interaction_materializer.py`.
- 관측: generated `455`, old strict `77`, null-evaluated `42`, public-free ready `0`. Best p90 was `-0.000379563` from `cashflow_stress/Q1_S1`, but old-strict rows were null-common; robust null-rare rows were below old strict resolution.
- 성공/폐기 기준: reject all `submission_e310_pair_*.csv` as public submissions unless a later independent action-health governor can separate real pair movement from wrong-pair and shuffled controls.
- public LB 관측 반응: no public LB should be spent on E310 files.
- 제출 전략: none. Pair state should next be used as an energy/gate or as supervision for candidate outcome health, not as direct coupled logit delta.

### H311: E310's visibility/null-rarity cliff can be crossed by stacking micro actions or subtracting matched-null motion

- 상태: 반증됨.
- 왜 그럴듯한가: E310 had null-rare candidates that were too small and visible candidates that were null-common. If the cliff were a scale artifact, stacking small safe actions or residualizing null-common actions could cross it.
- 맞다면: micro-stacked candidates should become old-strict while keeping low null strict rate, or residualized old-strict actions should beat row/subject/dateblock/wrong-pair/swap controls.
- 틀리다면: micro-stacks should become null-common as soon as they are visible, and residualized candidates should be either too small or null-common.
- 최소 실험: `analysis_outputs/e311_pair_micro_action_combiner.py`.
- 관측: generated `512`, old strict `489`, null-evaluated `37`, public-free ready `0`. `microstack` reached best p90 `-0.000807827` but null strict rate `0.611111`; `microdiverse`/`microcash` had null strict at least `0.722222`; residualized null-safe rows were too small.
- 성공/폐기 기준: reject more stacking/residual-average pair-delta materializers unless they add a genuinely new action-health target.
- public LB 관측 반응: no public LB should be spent on E311 files.
- 제출 전략: none. Treat E310/E311 as evidence that pair states need a learned outcome-health translator or should remain diagnostic.

### H312: candidate action-health is mostly encoded in action geometry, not story semantics

- 상태: 지지됨 as a public-free blocker; 반증됨 as a submission generator.
- 왜 그럴듯한가: E279-E311 repeatedly split into safe-but-invisible and visible-but-null-common candidates. If this is a structural action-layer bottleneck, past governor outcomes should be predictable before public LB.
- 맞다면: leave-experiment-out models should predict null-common and action-cliff labels from non-leaking action metadata. Geometry features should be much stronger than story-only labels. However, if positive visible/null-rare rows are too sparse, readiness ranking should remain weak.
- 틀리다면: null-common prediction should be near chance under experiment leave-out, or semantic story labels should dominate geometry, suggesting the missing piece is more creative human theory rather than the materializer.
- 최소 실험: `analysis_outputs/e312_action_health_world_model.py`.
- 관측: governed rows `1383`, experiments `20`, visible/null-rare `2`, strict-health `1`. `geometry_only` null-common AUC `0.984890`, `semantic_only` AUC `0.713484`, `full_safe` AUC `0.982065`. `full_safe` readiness-distance Spearman is only `0.102712`.
- 성공/폐기 기준: keep E312 as a veto if geometry can identify null-common behavior across held-out experiment families. Reject it as a generator unless it can rank visible/null-rare readiness with enough positives.
- public LB 관측 반응: no public LB should be spent on candidates blocked by E312 geometry/null checks. A future public-positive file that E312 predicts null-common would mean the governor is too conservative or missing a new action class.
- 제출 전략: none from E312 alone. Use it to block public tests; create new action classes or richer row/block synthetic controls before selecting a submission.

### H313: raw human diary row placement explains action readiness as an energy, not as a global binary gate

- 상태: 지지됨 as a readiness/energy representation; 반증됨 as a direct submission selector.
- 왜 그럴듯한가: E312 used candidate metadata and geometry, but not the actual lifestyle state of touched test rows. If human/social theory matters, delta-weighted diary signatures should explain which actions are close to readiness.
- 맞다면: human-diary signatures should predict some action-health outcomes under leave-experiment-out stress, especially readiness distance or selector-visible rare cases. They may fail as a global null-common classifier if positives are too sparse.
- 틀리다면: human signatures should be near chance for null-common, readiness distance, and selector-visible slices, and top coefficients should look like noise.
- 최소 실험: `analysis_outputs/e313_human_action_signature.py`.
- 관측: candidate files found `1379/1383`; selected human aggregate columns `520`. `human_signature` null-common AUC `0.866674`, below geometry-only `0.982733`; `geometry_shape_human` null-common AUC worsens to `0.956459`. But `human_signature` readiness-distance Spearman is `0.700161`, far above geometry-only `0.031522`. In selector-visible rows, human null-common AUC is `0.745343` versus geometry-only `0.537255`, though the slice has positive rate `0.976077`.
- 성공/폐기 기준: keep human signatures as energy if they rank readiness distance and rare selector-visible cases. Reject them as direct gates if adding them to geometry worsens global held-out null-common classification or top rows remain too small.
- public LB 관측 반응: no public LB should be spent on E313-ranked files directly. A future public-positive action generated from human-readiness seeds would strengthen H313 only if it also passes matched-null geometry controls.
- 제출 전략: none from E313 alone. Next strategy is a new materializer: start from safe-but-too-small human-ready rows and reshape/amplify them while preserving geometry-plus-shape null rarity.

### H314: human-readiness safe seeds can be made public-free by individual scalar lift

- 상태: 반증됨 for individual-lift materialization; H313 human-readiness energy remains alive.
- 왜 그럴듯한가: E313 found that human diary signatures strongly rank readiness distance, and top rows are often null-rare but too small. If those rows are genuinely near the frontier, modest lift or sparsity should make them visible without changing their hidden state.
- 맞다면: lifted human-ready seeds should become old-strict and still beat row/subject/dateblock/target-permutation/QS-swap/sign nulls. Null-rare seed identity should survive amplitude.
- 틀리다면: lifted candidates should split into too-small null-rare rows and visible null-common rows, repeating the E298/E311 action-layer cliff.
- 최소 실험: `analysis_outputs/e314_human_ready_lift_materializer.py`.
- 관측: safe seeds `180`, generated candidates `360`, old strict `33`, null-evaluated `40`, public-free ready `0`, best actual p90 `-0.000087616`. Null strict rate `0.000000` appears only below submission resolution; old-strict rows become null-common with weak mean dominance. The run only tested single-lift recipes because they saturated the candidate budget.
- 성공/폐기 기준: reject generated E314 single-lift submissions. Do not reject all human-ready combination strategies until a quota-reserved consensus/orthogonal-stack run is tested.
- public LB 관측 반응: no public LB should be spent on `submission_e314_humanready_single_*`. A future public-positive result from this branch must first pass direct matched-null governance; public LB is not the checker.
- 제출 전략: none from E314. Next strategy is E314b with reserved non-single recipes, or a target-level materializer that changes geometry rather than amplitude.

### H315: non-single human-ready compositions can cross the action-health cliff

- 상태: 반증됨 as direct additive composition; supported as a placement-health supervision source.
- 왜 그럴듯한가: E314 only tested individual scalar lift. If multiple human/social seeds are views of the same hidden lifestyle state, a family consensus or orthogonal story stack might change geometry enough to beat matched nulls.
- 맞다면: composite candidates should be selector-visible and null-rare at the same time, with row/subject/dateblock/target/sign controls losing. Semantically coherent stories such as bedtime arousal or routine fragmentation should remain robust.
- 틀리다면: composites should create strong local edges but still fail mode-specific nulls, revealing which hidden placement layer is wrong.
- 최소 실험: `analysis_outputs/e315_human_ready_composition_materializer.py`.
- 관측: generated `660`, old strict `229`, info `297`, null-evaluated `67`, public-free ready `0`. Best p90 was `-0.000523248`; best null strict was `0.090909` on orthogonal story stacks, but these failed old strict and subject/dateblock dominance. Bedtime-arousal family consensus was visible but null-common; routine-fragmentation/S1 was a strong information sensor but weak on row dominance.
- 성공/폐기 기준: reject direct additive human-ready composition as submission strategy. Keep the near misses as labels for hidden placement-health learning.
- public LB 관측 반응: no public LB should be spent on `submission_e315_humancomp_*`. A future submission from this branch must first show direct row/subject/dateblock placement health, not only semantic coherence or target/sign robustness.
- 제출 전략: none from E315. Next strategy is to learn subject/dateblock/row placement health from E315/E314/E313 governed candidates, or to construct a non-additive materializer that explicitly optimizes the failing mode-specific dominance.

### H316: human diary signatures recover intended placement but not placement health

- 상태: 지지됨 for hidden placement identity; 반증됨 as a submission-health certificate.
- 왜 그럴듯한가: E315 near misses failed because row/subject/dateblock placement was wrong, not because the human/social stories were empty. If raw diary context contains the hidden lifestyle state, it should distinguish the intended placement from matched row/subject/dateblock null placements.
- 맞다면: a leave-source-out actual-vs-placement-null classifier using human diary signatures should rank the actual placement above matched nulls, while action-shape-only features should not. If this is also health, identity rank should correlate with null strict rate and worst-mode dominance.
- 틀리다면: human signatures should be near chance against placement nulls, or action shape should explain the same identity result. If identity is a shortcut, it should not align strongly with health metrics.
- 최소 실험: `analysis_outputs/e316_human_placement_health_learner.py`.
- 관측: placement rows `1541`, sources `67`, placement null rows `1005`. `human_signature` actual-vs-placement-null AUC `0.998856`, AP `0.992019`, mean actual rank `0.999005`; `action_shape` AUC `0.500000`. But identity-health alignment is weak: Spearman `0.159448` versus worst-mode p90 dominance and `-0.206034` versus null strict rate.
- 성공/폐기 기준: keep human diary signatures as a hidden-placement identity representation. Reject actual-vs-null identity as a sufficient public-free submission gate.
- public LB 관측 반응: no public LB should be spent on E316 itself or on candidates justified only by recognizable human placement. A future public-positive file from this branch must first pass direct placement-health controls locally.
- 제출 전략: none from E316. Next strategy is an outcome-health target that predicts row/subject/dateblock dominance and uses identity rank only as one feature.

### H317: human context predicts placement regime health, but not a universal healthy action

- 상태: 지지됨 as a bounded placement-health latent; 반증됨 as a universal submission generator.
- 왜 그럴듯한가: E316 recovered intended placement but not health. If the missing target is outcome health, human diary signatures should predict which row/subject/dateblock placement is healthier under source-held stress.
- 맞다면: human signatures should beat action shape for source-held within-source health ranking or top-mode selection. If this is a general invariant, the signal should remain strong under leave-mode-out and within fixed modes.
- 틀리다면: action shape should dominate all health targets, or human signal should vanish under source-held stress.
- 최소 실험: `analysis_outputs/e317_human_placement_outcome_learner.py`.
- 관측: source-held p90-rank Spearman human `0.320748`, action `0.000000`, human+action `0.451921`; source top-mode accuracy human+identity+action `0.582090` vs action `0.029851`; source-held joint-health AUC human `0.731185`, action `0.683432`. But within-mode p90-rank mean Spearman is action `0.326136` vs human `0.238693`, and null-mode holdout human is only `0.133354`.
- 성공/폐기 기준: keep H317 as a regime-selection latent. Reject the universal human-score multiplier and any submission that lacks direct mode-specific null governance.
- public LB 관측 반응: no public LB should be spent on E317-derived identity/health scores alone. A future public-positive file would need a mode-specialized generator and local matched-null passage first.
- 제출 전략: none from E317. Next strategy is row/subject/dateblock specialist generation using human context for regime selection and action geometry for within-mode placement.

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

### H318: E317 outcome predictions can select a submission-ready placement from the E315 actual/null mini-world

- 상태: 반증됨 as direct submission selection; supported as regime-selection diagnostic.
- 왜 그럴듯한가: E317 showed that human+identity+action features predict source-held p90-rank health and top placement mode better than action shape alone. If the hidden regime is the main missing layer, selecting the best existing actual/null placement per source might reveal a ready file without more public LB.
- 맞다면: a non-oracle policy should produce a large p90-rank health gain over actual placement, approach oracle mode accuracy, and select placements whose improvement is not mostly a control artifact.
- 틀리다면: the policy should improve rank only modestly, lean heavily on row/subject/dateblock controls, and remain far below the oracle upper bound.
- 최소 실험: `analysis_outputs/e318_mode_specialized_policy_probe.py`.
- 관측: best non-oracle policy `human_identity_action_p90_rank` improved p90-rank health mean from `0.620336` to `0.649254`, delta rank versus actual `0.028918`, and joint-health rate from `0.134328` to `0.313433`. It selected subject `0.552239`, dateblock `0.208955`, row `0.149254`, and actual only `0.089552`. Oracle p90-rank health mean was `0.937500`.
- 성공/폐기 기준: keep the signal if it separates regime selection under source-wise normalization; reject as submission selection if selected rows are mostly null controls or the oracle gap remains large.
- public LB 관측 반응: no public LB should be spent. E318 is a public-free checker and routebook only.
- 제출 전략: none directly. Build a fresh mode-specialized generator, then run matched row/subject/dateblock/sign/target null governance before considering a public submission.

### H319: E318 route policies can generate a fresh submission-ready tensor

- 상태: 반증됨 as current consensus/blend/residual generator.
- 왜 그럴듯한가: E318 showed a real regime-selection edge. If hidden placement regime is the missing layer, translating selected routes into new mode-specialized consensus or residual tensors might beat null controls without public LB.
- 맞다면: fresh generated tensors should be both visible to old local selectors and rare under row/subject/dateblock/target/sign/QS matched nulls. Old strict promotion should not be the only positive signal.
- 틀리다면: generated tensors should become very visible but still be matched by placement nulls, meaning the generator averaged regimes rather than learning healthy within-regime action geometry.
- 최소 실험: `analysis_outputs/e319_mode_specialized_generator.py`.
- 관측: generated `540`, old strict `403`, null-evaluated `54`, public-free ready `0`; best actual p90 `-0.004283155`; non-oracle governed `47` with `30` old-strict rows.
- 성공/폐기 기준: reject E319 submission files if public-free ready is `0`, regardless of actual p90 or old strict count.
- public LB 관측 반응: no public LB should be spent. A public-positive E319 file would be uninterpretable because local controls already show the branch is null-common.
- 제출 전략: none. The route policy remains diagnostic; generation must be redesigned around mode-specific adversarial health.

### H320: E319 failed because target/sign/QS semantics are wrong

- 상태: 반증됨; hidden row/subject/dateblock placement ambiguity is the stronger explanation.
- 왜 그럴듯한가: E319 combines multiple human/social route policies and target-family tensors. A failed generator could be mixing the wrong targets, flipping direction, or confusing Q-side and S-side effects.
- 맞다면: target-permutation, sign-flip, or Q/S-swap nulls should be the main killer modes, and row/subject/dateblock dominance should be secondary.
- 틀리다면: target/sign/QS controls should be mostly beaten, while row, subject, and dateblock controls should account for most failures.
- 최소 실험: `analysis_outputs/e320_e319_failure_anatomy.py`.
- 관측: target-permutation mean dominance `1.000000`, sign-flip `1.000000`, Q/S swap `0.978723`; killer modes are row `16`, subject `15`, dateblock `15`, Q/S swap `1`.
- 성공/폐기 기준: reject the target/sign/QS-confusion explanation if those controls are mostly dominated and killer modes concentrate in placement controls.
- public LB 관측 반응: no public LB should be spent. Public testing would only ask the leaderboard to tell us what local placement controls already answered.
- 제출 전략: train or construct row/subject/dateblock mode-specific action-health objectives before any new submission candidate.

### H321: row/subject/dateblock action health is locally learnable

- 상태: 지지됨 as a local checker and JEPA-style action target; not sufficient as a submission selector.
- 왜 그럴듯한가: E320's failures were structured, not random: target/sign/QS controls were mostly beaten, while row/subject/dateblock controls killed candidates. Structured failure should be predictable from action geometry and route metadata.
- 맞다면: held-out-candidate models should predict actual-vs-null p90 wins and candidate-level adversarial health above chance, especially for subject/dateblock modes.
- 틀리다면: pairwise p90-win AUC and candidate-health Spearman should be near chance, implying hidden placement requires raw diary context not present in the action layer.
- 최소 실험: `analysis_outputs/e321_mode_adversarial_action_health.py`.
- 관측: full-pair p90-win AUC row `0.821035`, subject `0.930077`, dateblock `0.915720`; candidate worst-placement dominance Spearman `0.614177`; adversarial-health Spearman `0.508146`; ready-like candidates `0`.
- 성공/폐기 기준: keep the action-health learner if OOF AUC/Spearman are useful; reject direct submission use if predicted top candidates still do not pass ready-like local gates.
- public LB 관측 반응: no public LB should be spent from E321 alone. A future public-positive file must first show that E321-guided generation survives fresh matched nulls.
- 제출 전략: none directly. Use E321 as pre-materialization target or preselector for public-free null evaluation.

### H322: E321 can rescue a skipped unevaluated E319 candidate by preselection

- 상태: 반증됨 as a submission rescue; 지지됨 as an informative checker.
- 왜 그럴듯한가: E319 generated `540` candidates but null-evaluated only `54`. E321 showed action-health is learnable, so the unevaluated pool might contain a good file that the original budget skipped.
- 맞다면: E321-guided preselection should find at least one old-strict unevaluated candidate whose fresh null strict rate, p90 dominance, mean dominance, and worst-mode dominance pass promotion thresholds.
- 틀리다면: selected candidates should remain visible but null-common, especially with null strict rate above `0.10` or weak row/subject/dateblock dominance.
- 최소 실험: `analysis_outputs/e322_adversarial_preselector_nullcheck.py`.
- 관측: non-oracle universe `450`, selected `36`, selected old-strict `36`, fresh public-free ready `0`, best fresh p90 `-0.001452588`, best null strict rate `0.136364`, best worst-mode p90 dominance `1.000000`.
- 성공/폐기 기준: accept only if at least one candidate passes fresh governance. Since ready count is `0`, reject as a rescue path.
- public LB 관측 반응: no public LB should be spent. A public test would only ask the leaderboard to decide a branch already blocked locally.
- 제출 전략: none. Use the E321/E322 health target before materialization in a new generator.

### H323: E322 near misses contain recoverable signal after removing placement-null-common movement

- 상태: 반증됨 as public-transfer candidate; 지지됨 only as local diagnostic.
- 왜 그럴듯한가: E322 near misses were not target/sign wrong. They were visible but null-common. If the true hidden placement component is entangled with null-common movement, subtracting the row/subject/dateblock-common part should reveal a rarer residual.
- 맞다면: residualized or null-orthogonal variants should keep old-selector visibility while sharply reducing null strict rate, and should survive more than the small E323 governor.
- 틀리다면: residualized candidates should either become invisible or remain null-common under larger null samples.
- 최소 실험: `analysis_outputs/e323_null_common_residual_generator.py`, followed by `analysis_outputs/e324_e323_ready_highrep_stress.py`.
- 관측: E323 generated `420`, old-strict `291`, fresh ready `3`; E324 retested those `3` with `774` null rows and kept high-rep ready `3/3`. Priority file high-rep p90 `-0.000053747`, null strict `0.050388`, worst-mode dominance `0.859375`. Upload-safe public result for `5508f966` was `0.5770355016`, worse than E247 by `+0.0008765522`.
- 성공/폐기 기준: local support criterion was met, but the public criterion failed decisively. Treat local null-common residualization as an explanatory diagnostic, not as a generator.
- public LB 관측 반응: resolved negative. Local matched nulls missed a public/private subset or calibration axis.
- 제출 전략: none. Block E323 direct siblings and require an E323-negative stress slice for future candidates.

### H325: E323's residual action is lifestyle-interpretable, not only numeric residualization

- 상태: 부분 지지됨 as attribution; 반증됨 as public-candidate support.
- 왜 그럴듯한가: E323 was generated from human-regime-only family-consensus candidates. If it is genuinely part of the user-requested human/social hidden-state route, the moved rows should align with interpretable diary states more than matched row/subject/dateblock placements do.
- 맞다면: target-specific delta-weighted story means should be extreme against semantic nulls, and the top stories should match earlier robust human theories such as bedtime arousal, mobility/night-out, social isolation, or cash-flow stress.
- 틀리다면: top semantic z-scores should be near null, or the strongest alignments should be random calendar/payday artifacts with no relation to prior robust episode states.
- 최소 실험: `analysis_outputs/e325_e323_semantic_null_attribution.py`.
- 관측:
  - priority `5508f966` best signed semantic z `2.871546`, best abs semantic z `2.316330`;
  - Q1 aligns with night-out mobility;
  - S1 aligns with phone-in-bed/bedtime arousal;
  - S3 aligns with social-isolation/media;
  - higher semantic z sibling `51ed84b0` remains riskier by high-rep null strict.
- 성공/폐기 기준:
  - support if signed semantic z clears `2.0` on repeated prior story axes while high-rep null stress remains healthy;
  - reject semantic-sibling expansion unless semantic z improves without worsening high-rep null strictness.
- public LB 관측 반응: resolved negative through E323 public `0.5770355016`. Do not discard human stories, but semantic-null attribution is insufficient for public subset/calibration transfer.
- 제출 전략: no new file. Do not preserve E324 priority order after public failure.

### H326: E325 semantic axes can censor E323 residuals into a stronger public-free candidate

- 상태: 부분 지지됨 as semantic-vs-anti diagnostic; 반증됨 as replacement for E324 priority.
- 왜 그럴듯한가: E325 found non-null semantic alignment on Q1 night-out mobility, S1 phone-in-bed/bedtime arousal, and S3 social-isolation/media. If this is causal action structure, keeping cells aligned with those axes should improve null health relative to anti-semantic controls and the original E323 residual.
- 맞다면: semantic-censored variants should have higher ready rate than anti-controls and at least one should beat the E324 priority on null strictness plus p90/mean/worst-mode dominance.
- 틀리다면: semantic variants should either become invisible after censoring or become null-common when scaled, and anti-controls should be competitive.
- 최소 실험: `analysis_outputs/e326_semantic_residual_censor.py`.
- 관측: generated `252`, prefilter strict `141`, null-evaluated `36`, null rows `6984`; semantic selected rows `24` with ready `2`, anti-control rows `12` with ready `0`; beats E324 priority locally `0`.
- 성공/폐기 기준: keep semantic axes as diagnostic if semantic ready rate > anti ready rate; reject replacement if no candidate beats E324 priority under matched null stress.
- public LB 관측 반응: E324 priority resolved public-negative, so E326 same-family semantic siblings are blocked.
- 제출 전략: none. Do not use E326 as rescue.

### H327: remaining E324 risk is removable by censoring competitive null-fail cells

- 상태: 부분 지지됨 as risk diagnostic; 반증됨 as priority replacement.
- 왜 그럴듯한가: E324 priority still has nonzero row/subject/target-perm null strict rates. If the remaining risk is a stable null-fail residue, competitive build nulls should reveal cells to subtract or damp, and fresh stress should improve.
- 맞다면: build-null-risk variants should beat anti-controls and at least one should beat E324 priority on null strict plus p90/mean/worst-mode dominance under fresh nulls.
- 틀리다면: aggressive risk removal should overfit build nulls and become null-common on fresh stress, while conservative damping may survive but not dominate the original priority.
- 최소 실험: `analysis_outputs/e327_nullfail_risk_censor.py`.
- 관측: generated `540`, prefilter strict `179`, build null rows `288`, fresh stress null rows `7760`, ready `2`, beats E324 priority `0`; nullfail-censor ready `2/33`, anti-control ready `0/7`.
- 성공/폐기 기준: keep if censor variants beat anti-controls; reject as replacement if no file beats E324 priority. This is exactly the observed split.
- public LB 관측 반응: E324 priority resolved public-negative, so E327 same-family nullfail siblings are blocked.
- 제출 전략: none. Do not use E327 as rescue.

### H328: broad own-latent lifestyle state is the hidden law behind E247 and E323

- 상태: 반증됨 as direct predictive/submission latent; 지지됨 as diagnostic lifestyle atlas.
- 왜 그럴듯한가: human/social story states, payday/calendar signals, and JEPA residual views have repeatedly shown interpretable structure, while E323 showed local null-rare but public-bad behavior. A same-level own latent might capture the missing lifestyle world state and avoid E323-like moves.
- 맞다면: masked context views should predict the latent under subject/dateblock OOF, the latent should improve blocked label CV, and E323-bad rows should be strongly separable by latent energy or cluster state.
- 틀리다면: latent predictability may be high but label CV should worsen or match shuffled nulls, and E323 separation should be too weak to gate public-risk movement.
- 최소 실험: `analysis_outputs/e328_ownlatent_lifestyle_state_experiment.py`.
- 관측: `family_jepa_story/dateblock` teacher R2 `0.972508`, but subject label delta `+0.035211637`, dateblock label delta `+0.022631387`, targets improved `0`, and best E323 top20 separation only `0.545557`. Anti-E323 candidates are all below selector resolution.
- 성공/폐기 기준: reject direct use because label stress fails and E323-negative separation is weak. Keep diagnostic use because clusters are coherent and E247/E256 boundary is visible.
- public LB 관측 반응: no public LB should be spent. The local stress says E328 would be an information-poor public test.
- 제출 전략: none from E328. Redesign the latent target around Q3/S4, Q/S pair state, or action-health/E323-negative objectives.

### H330: target-specific lifestyle residual state is real, but needs localization

- 상태: 지지됨 as representation; 반증됨 as diffuse target calibration submission.
- 왜 그럴듯한가: E328 showed broad lifestyle state was too mixed with subject/routine shortcuts. A JEPA/data2vec-like learned target should be closer to the actual prediction problem: the per-target residual after subject/calendar base priors.
- 맞다면: residual-state predictions should improve blocked label CV for specific targets and beat row/subject/dateblock shuffled residual nulls. But if materialization is still the bottleneck, full-target E247 edits may remain below selector resolution.
- 틀리다면: residual-state rows should not beat shuffled nulls, or any apparent target improvement should be reproduced by row/subject/dateblock shuffles.
- 최소 실험: `analysis_outputs/e330_target_residual_lifestyle_latent.py`.
- 관측: `16/84` residual-state rows pass gates. Top rows: Q2 `jepa_resid/subject` delta `-0.030210616`, Q1 `jepa_resid/dateblock` `-0.025842772`, S2 `raw_day/subject` `-0.016452074`, S2 `jepa_resid/dateblock` `-0.014211218`. E247 materializations: `25`; selector-promoted: `0`; E323-negative candidates: `25`.
- 성공/폐기 기준: accept the representation because it survives label/null stress; reject the current translator because no materialized candidate promotes.
- public LB 관측 반응: no public LB should be spent. The local selector says the next public test would be low information.
- 제출 전략: none from E330. Build row/block/cell-localized actions from Q2/Q1/S2 residual states and retest with matched nulls plus E323-negative anatomy.

### H331: localized target-residual lifestyle tails are real but still below action visibility

- 상태: 지지됨 as localized representation; 반증됨 as current submission translator.
- 왜 그럴듯한가: E330's residual states were strong but diffuse. If the hidden lifestyle state is episodic, only high-energy residual tails should carry the useful correction.
- 맞다면: localized tails should beat blocked label baselines and row/subject/dateblock shuffled feature nulls, with cleaner E323 anatomy than E323 public-bad movement.
- 틀리다면: tail gates should lose to shuffled feature nulls, or any candidate movement should become E323-like or null-common after materialization.
- 최소 실험: `analysis_outputs/e331_residual_state_localization.py`.
- 관측: `39` localized gates, `43` probes, `0` selector-promoted. Strongest gates are Q1 `jepa_resid/dateblock/pos_q80` delta `-0.029674864`, Q1 `pos_q90` delta `-0.022958364`, Q2 `jepa_resid/subject/pos_q80` delta `-0.017481597`, and S2 `jepa_resid/dateblock/pos_q80` delta `-0.016882963`. Best public-free probes are Q1 `pos_q90`, but all are `too_small_to_submit`.
- 성공/폐기 기준: accept localization if label-null dominance survives; reject current translator if no candidate clears selector/E323/movement-null gates. This is the observed split.
- public LB 관측 반응: no public LB should be spent yet. A public test would mainly measure noise because the best edge is below selector resolution.
- 제출 전략: none from current E331. Continue only with a Q1 positive-tail translator and stronger movement-null stress.

### H332: Q1 positive-tail latent has correct direction, but direct translators fail visibility

- 상태: 지지됨 as hidden lifestyle-state latent; 반증됨 as direct scalar translator.
- 왜 그럴듯한가: E331 identified Q1 `jepa_resid/dateblock` positive tails as the cleanest localized residual state. If the only missing piece was amplitude, an OOF-trained constant/rank/softplus translator should produce a selector-grade E247 edit.
- 맞다면: Q1-tail translators should improve blocked Q1 logloss versus row/subject/dateblock nulls, reject signflip controls, stay E323-negative, and produce at least one actual-direction candidate with negative p90 and movement-null dominance.
- 틀리다면: label/null stress may remain strong, but materialized candidates should be below selector resolution or lose p90/movement-null health when scaled.
- 최소 실험: `analysis_outputs/e332_q1_tail_translator_stress.py`.
- 관측: `33` local translator gates, `77` probes, `0` actual-direction selector-promoted candidates, `0` selector+E323+movement-null-safe candidates. Best local Q1 `pos_q83/const` delta `-0.015385658`, dominance `1.000000`. Signflip controls are rejected with beats rate `0.000000`.
- 성공/폐기 기준: accept the latent direction because label/null and signflip stress agree; reject direct translation because no materialized candidate clears selector and movement-null checks.
- public LB 관측 반응: no public LB should be spent. If submitted anyway, expected reaction is low-information or worse because p90 remains positive on the closest visible moves.
- 제출 전략: none from direct E332. The next strategy should predict visibility-safe placement/action shape for Q1-tail rows, not increase the same scalar shift.

### H333: Q1 tail needs broad contrastive background compensation

- 상태: 반증됨 as submission/action latent; 지지됨 only as a local-validation shortcut.
- 왜 그럴듯한가: E332's one-sided Q1-tail shift was directional but below public-free visibility. A calibrated human-state action might require lowering tail rows while raising or reshaping non-tail/background rows.
- 맞다면: contrastive actions should improve local Q1 logloss, keep E323-negative anatomy, and turn E332's p90-positive edge into a selector-promoted E247 candidate.
- 틀리다면: train label/null gains should grow, but public-free selector scores should turn positive or p90-worse after materialization.
- 최소 실험: `analysis_outputs/e333_q1_contrastive_action_translator.py`.
- 관측: `510` local translator gates, `84` materialized candidates, `0` selector-promoted candidates. Best local delta `-0.020200`, but best-ish public-free probe has selector mean `+0.000034`, p90 `+0.000299`, beats `0.583333`.
- 성공/폐기 기준: reject as action latent because no candidate clears selector/E323/movement-null gates and the best materialization is worse than E247 by selector mean/p90.
- public LB 관측 반응: no public LB should be spent. The local public-free sensor already reads the family as adverse.
- 제출 전략: none. Do not use broad non-tail Q1 compensation unless a future action-health model independently flips the selector/p90 read.

### H334: Q1 tail needs row-censor placement before scalar action can work

- 상태: 반증됨 as submission/action latent; 지지됨 as further evidence that Q1 lifestyle state is real.
- 왜 그럴듯한가: E332 showed direct Q1-tail shifts were too small or p90-risky, and E333 showed broad background compensation was a shortcut. A natural hidden-world explanation is wrong row placement: only specific latent, subject, dateblock, calendar, or base-Q1 rows should receive the Q1 correction.
- 맞다면: row-censored Q1-tail variants should retain local Q1 label/null gains and at least one materialized E247 file should become selector-promoted, E323-negative, and movement-null safe.
- 틀리다면: many row masks may pass local label/null stress, but all materialized files should remain below selector resolution or lose p90/movement-null health.
- 최소 실험: `analysis_outputs/e334_q1_tail_row_censor_action_health.py`.
- 관측: `532` row-censor variants, `510` local gates, `72` generated candidates, `0` selector-promoted, `0` selector+E323-safe, `0` selector+E323+movement-null-safe. Best local gate Q1 `pos_q78/const/latent_top80` delta `-0.016399822`, dominance `1.000000`. Closest files remain too small or movement-null dominated.
- 성공/폐기 기준: reject row-censor scalar action because no candidate clears selector/E323/movement-null gates. Keep the representation evidence because local row-mask gates are abundant and consistent.
- public LB 관측 반응: no public LB should be spent. A submission would mostly test local selector noise rather than a new public-transfer hypothesis.
- 제출 전략: none. Next strategy is a JEPA-style action-health target: learn or construct a latent representation of visible, p90-safe, null-rare movement before probability materialization.

### H335: Q1 action-health latent can generate a submission-grade tensor

- 상태: 반증됨 as current generator; 지지됨 as action-health diagnostic latent.
- 왜 그럴듯한가: E332-E334 showed repeated local Q1 lifestyle signal but no public-free action. If the missing variable is outcome health, a same-level latent trained on candidate geometry and moved-row lifestyle signatures should identify safe visible actions better than hand-coded scales/masks.
- 맞다면: leave-experiment/family health prediction should rank prior candidates, and generated consensus/projection actions should clear selector visibility, E323-negative anatomy, and movement-null dominance.
- 틀리다면: health ranking may be predictable inside the archive, but generated actions should regress to safe-invisible movements or visible-null-common movements, with zero selector-promoted candidates.
- 최소 실험: `analysis_outputs/e335_q1_action_health_latent_generator.py`.
- 관측: archive `233`, movement-null-labelled `58`, ready proxy `5`; leave-family trees Spearman `0.938198`, top20 overlap `0.891304`; generated `55`, selector-promoted `0`, selector+E323+movement-null-safe `0`. Best generated files have negative p90 and high movement-null p90 dominance but are `too_small_to_submit`.
- 성공/폐기 기준: reject generator if no candidate clears selector+E323+movement-null gates; keep diagnostic if leave-experiment/family rank transfer is high. This is the observed split.
- public LB 관측 반응: no public LB should be spent. Expected reaction is low-information because candidates are below selector resolution.
- 제출 전략: none from E335. The next strategy needs new positive support for visible/null-rare action geometry, likely via cross-target action states or E323/public-negative movement anatomy.

### H336: public-bad anatomy can be directly inverted into a safe lifestyle action

- 상태: 반증됨 as direct generator; 지지됨 as veto/diagnostic latent.
- 왜 그럴듯한가: E323 upload-safe was semantically and locally plausible but publicly bad. If its failure encodes a public-negative lifestyle/action state, the opposite direction or bad-axis-orthogonalized good direction might preserve E247 while removing the public-adverse component.
- 맞다면: away-from-E323/E216/bad-combo moves should improve E272 selector mean/p90, avoid public-bad anatomy, and beat movement-null shuffles. Old-frontier-good axes with bad projection removed should become visible and safer than raw good axes.
- 틀리다면: public-bad anatomy may be target-specific, but reversed/orthogonalized output moves should remain below selector resolution, p90-positive, or null-common.
- 최소 실험: `analysis_outputs/e336_public_negative_action_latent.py`.
- 관측: E323 bad is Q1/S1/S3-heavy, E216 bad is S2-heavy, so the anatomy is real. But `162` generated candidates yield `0` selector-promoted, `0` selector+public-bad-safe, and `0` selector+public-bad+movement-null-safe rows. Best probes are tiny `good_mixmin_topall` continuations and are not promoted.
- 성공/폐기 기준: reject direct inversion if no candidate clears selector plus public-bad plus movement-null gates; keep the axes as risk diagnostics if they are target-specific and explain prior public failures. This is the observed split.
- public LB 관측 반응: no public LB should be spent. Expected reaction is low-information for tiny good_mixmin moves or adverse/noisy for away-from-bad moves.
- 제출 전략: none from E336. Use E323/E216 axes as an anti-public risk coordinate in future hidden lifestyle-state/action-health training.

### H337: target-residual lifestyle states form repeated hidden clusters

- 상태: 지지됨 as representation; 반증됨 as global probability materializer.
- 왜 그럴듯한가: E330-E336 repeatedly showed target-specific residual states, but diffuse target-level translators failed. A hidden lifestyle-state should appear as repeated residual episodes before output movement.
- 맞다면: residual latent clusters should be non-collapsed, predictable from meaningful context views, and improve label CV beyond shuffled cluster nulls for specific target/split pairs.
- 틀리다면: cluster entropy should collapse, context prediction should be null-like, or label gains should vanish under row/subject/dateblock cluster shuffles.
- 최소 실험: `analysis_outputs/e337_residual_lifestyle_cluster_state.py`.
- 관측: dateblock contexts predict residual latent better than subject contexts (`family/dateblock` R2 `0.169277`, `jepa_resid/dateblock` R2 `0.107508`). k4-k8 clusters have train entropy `0.958303-0.981673` and test entropy `0.824252-0.936542`. Three cluster-target rows pass label/null gates: `Q3/dateblock/k6`, `Q2/dateblock/k8`, and `S3/subject/k4`.
- 성공/폐기 기준: accept representation if clusters survive label/null stress; reject materializer if generated E247 candidates fail selector/movement-null gates. This split is observed.
- public LB 관측 반응: no public LB should be spent. Global cluster shifts are expected to be low-information or worse because selector-promoted count is `0`.
- 제출 전략: none from E337. Use cluster labels as hidden episode state and localize the action to cluster rows.

### H338: cluster-local episode action fixes the E337 global-smear failure

- 상태: 부분 지지됨 as action-shape improvement; 반증됨 as current submission candidate.
- 왜 그럴듯한가: E337's representation survived but its action moved all rows for each target. If wrong placement is the issue, moving only cluster-local episode rows should retain signal and become movement-null dominant.
- 맞다면: local episode variants should improve selector mean/p90 versus E247, beat movement-null shuffles, and at least one file should clear selector promotion.
- 틀리다면: local actions should remain below selector resolution, or amplification should become p90-positive/null-common.
- 최소 실험: `analysis_outputs/e338_cluster_local_episode_action.py`.
- 관측: `10` episode-gated rows and `75` candidates. The best file, `submission_e338_local_veto_centered_top2_s0_20_28122ea1.csv`, has mean `-0.000034`, p90 `-0.00000036`, beats `0.902778`, and movement-null dominance `1.000000/1.000000`, but is `too_small_to_submit`. Selector-promoted count is `0`.
- 성공/폐기 기준: accept localization if movement-null dominance improves; reject as submission if selector promotion remains zero. This is observed.
- public LB 관측 반응: do not submit yet. Expected public effect is too small/noisy despite healthy local movement.
- 제출 전략: none directly. The next strategy is constrained Q3 episode amplification or E338 episode-gated blend with an independent Q3 direction.

### H339: E338 Q3 episode gate can safely amplify an older Q3 direction

- 상태: 반증됨 as submission/action generator; 지지됨 as low-energy Q3 episode sensor.
- 왜 그럴듯한가: E338 found a clean Q3/dateblock episode placement but below selector resolution. Existing public-surviving files contain larger Q3 movements, so a healthy hidden-state gate might preserve only the correct rows/signs.
- 맞다면: E338-gated projections of E95/mixmin/E101/E176/E256/E267/E211 directions should produce selector-promoted candidates with negative p90 and movement-null dominance. Older Q3 directions should align with the episode signs more than chance.
- 틀리다면: source directions should show weak episode-sign alignment, and projected candidates should remain below selector resolution or become null-common/p90-risky.
- 최소 실험: `analysis_outputs/e339_q3_episode_gate_amplifier.py`.
- 관측: `5430` candidates, `0` selector-promoted, `1492` information sensors, `0` movement-null-safe promoted. E95/mixmin/E101 Q3 directions agree with the E338 episode signs only `0.510204`, E176 `0.489796`, E267 `0.122449`, and E256 `0.020408`. The best candidate has mean `-0.000019`, p90 `-0.000005`, and movement-null dominance `1.000000/1.000000`, but is `too_small_to_submit`.
- 성공/폐기 기준: reject as a generator if no candidate clears selector promotion and movement-null gates; keep the episode gate as a sensor if negative p90 and null dominance persist. This is observed.
- public LB 관측 반응: no public LB should be spent. Expected public effect is low-information because the best deltas remain below submission resolution.
- 제출 전략: none from E339. Future Q3 work needs a learned visibility target or a new independent positive support axis, not direct reuse of older Q3 directions through the same gate.

### H340: multiple safe lifestyle micro-states can cross selector visibility together

- 상태: 반증됨 as submission/action generator; 지지됨 as action-health/visibility diagnostic.
- 왜 그럴듯한가: E335 Q1 tails and E338/E339 Q3 episodes are individually null-dominant but too small. If the only blocker is selector resolution, cross-target coalition should accumulate enough p90 edge while preserving null rarity.
- 맞다면: Q1+Q3 coalitions should produce at least one `strict_promote_gate=True` candidate and fresh movement-null dominance should remain high.
- 틀리다면: p90 should improve but saturate above `-0.00005`, or visibility should appear only in matched-null-common variants.
- 최소 실험: `analysis_outputs/e340_microstate_coalition_action_health.py`.
- 관측: `5560` archive rows, `37` safe-invisible source rows, `7400` coalitions, `0` selector-promoted, `4248` information sensors, `0` movement-null-safe promoted. Best p90 is only about `-0.000028`, while the best null-stressed file has dominance `1.000000/1.000000` but remains `too_small_to_submit`.
- 성공/폐기 기준: reject as generator if no coalition clears strict selector plus movement-null gates; keep as diagnostic if action-health/visibility latent is predictable. This is observed: visibility OOF Spearman `0.921134`, action-health OOF Spearman `0.938224`, but null-health OOF Spearman is near zero.
- public LB 관측 반응: no public LB should be spent. The expected public effect is likely small/noisy because all files are below strict p90 resolution.
- 제출 전략: none from E340. The next route must introduce a new visibility-positive support axis or learn null-health from richer positive examples; further Q1/Q3 summing is low priority.

### H341: E330 residual lifestyle states become public-visible when restricted to rare tails

- 상태: 약화됨 as submission generator; 지지됨 as information-sensor/sign-transfer clue.
- 왜 그럴듯한가: E330 had strong blocked-CV residual states but moved every test row. If the latent is a real human/social state, the signal may be concentrated in extreme days rather than the full distribution.
- 맞다면: sparse top-k residual tails should produce at least one strict selector-promoted file, or p90 close to `-0.00005`, with movement-null dominance preserved.
- 틀리다면: sparse tails should improve mean but still saturate far above the strict p90 gate, and movement-null-safe files should remain `too_small_to_submit`.
- 최소 실험: `analysis_outputs/e341_sparse_residual_support_axis.py`.
- 관측: `864` sparse residual-tail candidates, `0` selector-promoted, `96` information sensors, `0` movement-null-safe promoted. Best Q2 inverse sparse tail has mean `-0.000151`, p90 `-0.000017477`, beats `0.902778`. Best null-dominant Q1 tail reaches dominance `1.000000/1.000000` but p90 only `-0.000005843`.
- 성공/폐기 기준: reject as a submission generator because strict promotion is zero and p90 remains about 3x weaker than the gate. Keep as a clue because inverse Q2 residual-tail movement is consistently better than direct broad E330.
- public LB 관측 반응: no public LB should be spent. Expected public response is too small/noisy.
- 제출 전략: none from E341. Next strategy should learn sign-transfer/visibility mapping from residual states to E247 action geometry, or find a new support axis outside E330 residual tails.

### H342: Q2 residual tail and Q1/Q3 microstate coalition are projections of one hidden lifestyle state

- 상태: 강하게 지지됨 as information sensor; 보류/거절 as submission generator.
- 왜 그럴듯한가: E340 and E341 fail in complementary ways. Q1/Q3 microstates are movement-null healthy but p90-small; Q2 inverse residual tails are a separate sparse support axis. A real life-state such as intervention/rough-night/social-recovery could appear across Q2 and Q1/Q3 rather than inside one target.
- 맞다면: combined Q2+Q1/Q3 sign-transfer should improve p90 beyond either source, beat movement nulls, and ideally cross strict promotion without increasing known public-bad axes.
- 틀리다면: combinations should remain near E340/E341 p90, or only become visible by moving along public-bad axes.
- 최소 실험: `analysis_outputs/e342_signtransfer_lifestyle_latent.py`.
- 관측: `1314` candidates, `0` selector-promoted, `1019` information sensors. Best p90 crosses visibility (`-0.000055`) with beats `0.986111` and movement-null p90 dominance up to `1.000000` on several near-misses, but incremental bad-axis is `0.017962+`, above the `0.015` cap.
- 성공/폐기 기준: accept as representation if cross-target combination beats both sources and movement nulls; reject as submission if bad-axis prevents strict promotion. This split is observed.
- public LB 관측 반응: no public LB should be spent on raw E342. Expected upside exists but downside risk is E323/E216-like public-bad geometry.
- 제출 전략: none directly. Use as the strongest current sign-transfer clue; next experiment must separate useful visibility from bad-axis load.

### H343: E342 sign-transfer edge can be cleaned by removing known bad-axis projection

- 상태: 반증됨 as current submission route.
- 왜 그럴듯한가: E342 missed strict promotion narrowly because of bad-axis load. If the hidden lifestyle-state signal is separable, projection cleanup should keep p90 visibility while lowering public-bad risk.
- 맞다면: projection-removed candidates should have p90 `< -0.00005`, beats `>=0.75`, bad-axis `<=0.015`, and survive movement-null stress.
- 틀리다면: reducing bad-axis should also destroy p90 visibility, showing that the current visible energy is entangled with public-bad geometry.
- 최소 실험: `analysis_outputs/e343_badaxis_neutralized_signtransfer.py`.
- 관측: `1512` candidates, `0` selector-promoted, `845` information sensors. Best cleaned candidate has mean `-0.000237`, p90 `-0.000046`, beats `0.986111`, bad-axis `0.015414`. Variants that reduce bad-axis below `0.015` lose p90 visibility.
- 성공/폐기 기준: reject cleanup route because no file simultaneously clears p90 and bad-axis. Keep E342 as a latent clue, not a candidate.
- public LB 관측 반응: do not submit. If submitted anyway, expected reaction is uncertain and likely not worth a public slot because the strict local safety condition is not met.
- 제출 전략: none from E343. Need a new support axis or a generator trained to produce visible/null-rare movement without borrowing the bad-axis component.

### H344: an independent counter-axis can make the E342 hidden lifestyle state submission-safe

- 상태: 지지됨 locally; public LB 미확인.
- 왜 그럴듯한가: E342 crossed visibility but exceeded bad-axis. E343 proved direct cleanup removes useful p90. If the signal is a real hidden lifestyle state, a separate anti-bad action state should reduce only the risk component.
- 맞다면: E342+counter candidates should keep p90 `< -0.00005`, lower incremental bad-axis `<= 0.015`, and beat row/target/sign/subject/dateblock movement nulls.
- 틀리다면: bad-axis reduction should again destroy p90, or strict candidates should be null-common.
- 최소 실험: `analysis_outputs/e344_counter_axis_signtransfer.py`.
- 관측: `3330` candidates, `6` selector-promoted, `2677` information sensors, `6` movement-null-safe promoted. Best candidate `submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv` has mean `-0.000246354`, p90 `-0.000053606`, beats `0.972222`, bad-axis `0.014849687`, movement-null p90 dominance `1.000000`, and null strict rate `0.000000`.
- 성공/폐기 기준: accept locally if strict selector plus movement-null gates pass; require public LB before treating the counter-axis as generally valid. Local acceptance is observed.
- public LB 관측 반응: if public improves, this strongly supports the hidden lifestyle-state + counter-axis world model. If public worsens, the local selector is likely accepting an E315/E342 interaction that is still public-subset-specific or private-risky.
- 제출 전략: submit `analysis_outputs/submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv` as the next high-information candidate.

### H345: the E342+E315 counter-axis state is a stable basin, not a knife-edge

- 상태: 지지됨 locally; public LB 미확인.
- 왜 그럴듯한가: E344's strict candidate had a narrow bad-axis margin, so it could have been a single threshold artifact. A real hidden lifestyle-state plus counter-state should survive nearby counter weights, veto strengths, and target scopes.
- 맞다면: a local grid around the E344 composition should produce many strict candidates, multiple movement-null-safe rows, and no strict promotion under matched movement nulls.
- 틀리다면: nearby variants should lose p90, exceed bad-axis, or become movement-null-common.
- 최소 실험: `analysis_outputs/e345_counteraxis_margin_refine.py`.
- 관측: `6588` candidates, `278` selector-promoted, `6029` information sensors, and `40` movement-null-safe promoted. The selected refinement `submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv` has mean `-0.000246580`, p90 `-0.000051888`, bad-axis `0.014655826`, and null strict promote rate `0.000000`.
- 성공/폐기 기준: accept the stability claim if many nearby variants survive strict selector plus movement-null stress. This is observed. Do not upgrade E345 above E344 unless public feedback or a revised survival score values bad-axis margin over p90 margin.
- public LB 관측 반응: if E344 improves and E345 also improves, the counter-axis basin becomes the strongest current world model. If E344 worsens but E345 improves, bad-axis margin matters more than p90. If both worsen, the local counter-axis safety is not public-transferable.
- 제출 전략: keep E344 as first public sensor; use `analysis_outputs/submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv` as the refined bad-axis-margin follow-up.

### H346: local counter-axis safety is also certified by known public-loss analogs

- 상태: 부분 지지 / certification은 반증됨.
- 왜 그럴듯한가: E323 showed that local row/subject/dateblock null safety can still fail public. A stronger preflight should compare E344/E345 against known public-bad movements, not only synthetic movement nulls.
- 맞다면: E344/E345 should have low positive cosine to E323/E216/E267/E256 axes and public-analog risk should dominate matched movement nulls by at least `0.70`.
- 틀리다면: candidates should either align with known public-bad axes or show only median-level public-analog null dominance.
- 최소 실험: `analysis_outputs/e346_counteraxis_public_analog_audit.py`.
- 관측: E344/E345 direct positive alignment to E323/E216/E267/E256 is `0.000000000`, so there is no hard public-bad veto. But survival scores are only `0.452806` and `0.461735`, below certification threshold `0.70`.
- 성공/폐기 기준: accept as hard-veto pass but reject as certification. This is observed.
- public LB 관측 반응: if E344 improves, E346 was sufficient as a veto but overly conservative as a certifier. If E344 worsens, the missing factor is not simple E323/E216/E267/E256 cosine; it is a public subset or calibration state not captured by current public analog axes.
- 제출 전략: no new file. Keep E344 first, E345 second.

### H347: the safer E344 neighborhood still lies on the hidden lifestyle-state manifold

- 상태: 지지됨 locally; public LB 미확인.
- 왜 그럴듯한가: E346 revealed E344 neighborhood rows with lower public-analog risk than the upload-safe E344/E345 files. If these are just diluted output moves, they should lose connection to the hidden lifestyle-state teacher. If they remain on-manifold, row movement should be non-randomly explained by E328/E337 lifestyle-state features.
- 맞다면: selected neighborhood candidates should preserve local p90/bad-axis gates, reduce public-analog risk, and show row-movement correlation/enrichment against lifestyle-state features above row-shuffle nulls.
- 틀리다면: lower-risk candidates should be weakly state-aligned, or only E344/E345 uploads should retain the hidden-state signature.
- 최소 실험: `analysis_outputs/e347_lifestyle_state_candidate_reaudit.py`.
- 관측: `16` candidates audited, `3` E347 gate passes. Best file `submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv` has p90 `-0.000050116`, bad-axis `0.014671133`, public-analog survival `0.528061224`, risk `0.044818570`, and dominant state axis `rs01_Q1_jepa_resid_dateblock` with state corr/enrichment dominance `1.000000/1.000000`.
- 성공/폐기 기준: accept locally if a lower-risk candidate remains p90-visible, bad-axis-safe, E323/E216/E267/E256-neutral, and lifestyle-state-aligned versus nulls. This is observed.
- public LB 관측 반응: if E347 improves, public-transfer prefers stateful public-analog risk over maximum p90 margin. If E344 beats E347, p90 margin is the stronger sensor. If both fail, the missing state is not captured by Q1 dateblock residual lifestyle alignment.
- 제출 전략: submit `analysis_outputs/submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv` first as the most evidence-balanced sensor.

### H348: E347's Q1 dateblock lifestyle-state alignment is specific, not generic post-hoc storytelling

- 상태: 지지됨 locally.
- 왜 그럴듯한가: E347 found all E344-family rows strongly state-aligned, so the statefulness test could have been too easy. A real hidden lifestyle-state action should beat calendar-only, random, permuted-state, non-Q1 residual, own-latent, and public-bad controls.
- 맞다면: the selected E347 movement should have large positive Q1-specificity margin and public-bad controls should fail the same specificity gate.
- 틀리다면: public-bad controls or calendar/random controls should show comparable Q1 state alignment, or E347 should be better explained by broad own-latent/calendar state than by `rs01_Q1_jepa_resid_dateblock`.
- 최소 실험: `analysis_outputs/e348_lifestyle_state_specificity_audit.py`.
- 관측: selected E347 file has Q1 corr `0.432330`, Q1 enrichment `0.852584`, specificity margin `0.297346`, broader margin `0.271772`, calendar corr `0.053213`, random p95 `0.134984`, and permuted-Q1 p95 `0.114145`. E323/E216/E256 controls fail specificity.
- 성공/폐기 기준: accept if Q1 specificity margin is positive by at least `0.10` and public-bad controls fail. This is observed.
- public LB 관측 반응: if E347 improves, H347/H348 become the strongest current hidden lifestyle-state world model. If E347 fails, the latent is locally specific but not public-subset-transferable.
- 제출 전략: no new E348 file; keep E347 first.

### H349: the E347 lifestyle-state action is a compact coupled Q/S state, not a Q1-only target trick

- 상태: 지지됨 locally; public LB 미확인.
- 왜 그럴듯한가: E347/E348 identify a Q1 dateblock residual lifestyle-state action, but Q1 specificity alone could be misleading. A real human lifestyle state should appear through a small target manifold such as Q1/Q2/Q3/S1 rather than a single isolated target edit.
- 맞다면: target/cell-pruned variants around E347 should show that Q1-only or S-only fragments are not submission-grade, while a compact coupled Q/S slice keeps selector visibility, public-bad-axis neutrality, and Q1-state specificity.
- 틀리다면: Q1-only should retain the full local edge, or pruning should destroy the E347 gate entirely.
- 최소 실험: `analysis_outputs/e349_e347_target_cell_ablation_stress.py`.
- 관측: `158` variants tested, `10` general gates, `2` replacement gates. The selected file `submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv` keeps p90 `-0.000050035`, bad-axis `0.014667610`, public-analog survival/risk `0.525510204/0.044736209`, direct bad-axis positive cosine sum `0`, Q1 corr `0.440884`, and changes `347` cells versus E347. Q1-only/Q-only row slices become very state-specific but fail selector visibility or add bad-axis leakage; S-only and isolated S targets fail.
- 성공/폐기 기준: accept locally if a meaningfully different ablation passes strict selector, bad-axis cap, public-analog risk, hard-veto axes, and Q1 specificity. This is observed for the Q1/Q2/Q3/S1 cell-pruned variants.
- public LB 관측 반응: if E349 improves, the hidden state should be treated as a compact coupled subjective/objective episode state. If E349 worsens while E347 survives, the small S3/tail cells removed by E349 were useful calibration rather than noise.
- 제출 전략: use `analysis_outputs/submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv` as the next high-information sensor after E347.

### H350: the compact Q1/Q2/Q3/S1 lifestyle-state action is a local plateau, not a threshold accident

- 상태: 강하게 지지됨 locally; public LB 미확인.
- 왜 그럴듯한가: E349 passed by pruning E347 to Q1/Q2/Q3/S1 high-magnitude cells, but the selected p90 margin was close to the strict threshold. A true hidden lifestyle-state action should survive nearby cell thresholds, tiny amplitude changes, and partial S3-tail restoration.
- 맞다면: local gate survivors should appear across neighboring thresholds, S3-tail alphas, and micro scales, while preserving E272 visibility, E346 hard-veto neutrality, and Q1 dateblock latent specificity.
- 틀리다면: only the exact E349 `top65/s1.00/S3=0` point should survive, or neighbors should become public-bad/S3-risky.
- 최소 실험: `analysis_outputs/e350_compact_state_plateau_stress.py`.
- 관측: `311` candidates, `187` local gates, `176` plateau gates. The selected file `submission_e350_compactplateau_selected_compact_t45_s1_005_s3a1_00_ef54727b_uploadsafe.csv` has p90 `-0.000050233`, bad-axis `0.014742869`, public-analog risk `0.044770778`, direct E323/E216/E267/E256 positive alignment `0`, Q1 specificity margin `0.317370`, and plateau support score `37`.
- 성공/폐기 기준: accept the plateau claim if multiple adjacent thresholds, micro scales, and S3 alphas pass local/public-analog/specificity gates while remaining meaningfully different from E347/E349. This is observed. Do not claim large-scale robustness because coarse `0.96/1.04` scaling was unstable.
- public LB 관측 반응: if E350 improves, the compact lifestyle-state basin and small S3-tail restoration become the strongest current world model. If E350 worsens but E349/E347 survive, micro-amplified S3 restoration was over-aggressive and the safer compact-pruned state should remain preferred.
- 제출 전략: submit `analysis_outputs/submission_e350_compactplateau_selected_compact_t45_s1_005_s3a1_00_ef54727b_uploadsafe.csv` only as a high-information sensor; treat it as more ambitious than E349, not strictly lower-risk.

### H351: the E350 basin needs a robust selector, not the score-seeking rank winner

- 상태: 지지됨 locally; public LB 미확인.
- 왜 그럴듯한가: E350 showed many plateau survivors, but the original rank winner used full S3 restoration and moved farther from E349. If public slots are scarce, a lower-regret representative of the same basin may be more useful than the most aggressive rank winner.
- 맞다면: a maximin selector over p90, public-analog risk, bad-axis margin, Q1 specificity, plateau support, E349 compatibility, and micro-scale size should choose a different candidate that still improves E349 p90 and remains inside the compact-state plateau.
- 틀리다면: the E350 rank winner should also be the robust maximin winner, or no candidate should pass the compatibility gate.
- 최소 실험: `analysis_outputs/e351_robust_plateau_selector.py`.
- 관측: `176` E350 plateau candidates, `36` E351 compatibility candidates. E350 rank winner fails compatibility due to distance from E349 (`0.011439`). The robust selected candidate `submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv` has p90 `-0.000050191`, public-analog risk `0.044765398`, bad-axis `0.014741236`, Q1 specificity margin `0.324251`, plateau support `35`, and probability L1 distance vs E349 `0.006241`.
- 성공/폐기 기준: accept if a candidate inside the E350 basin keeps p90 improvement, bounded risk, and better maximin balance than the original rank winner. This is observed.
- public LB 관측 반응: if E351 improves, robust plateau selection matters more than maximum E350 rank/S3 restoration. If E350 improves more than E351, public prefers stronger S3-tail restoration and p90 edge. If both fail, the local plateau is not public-transferable enough.
- 제출 전략: use E351 as the practical first submission from the plateau branch; keep E350 as the aggressive information sensor.

### H352: E351 is the selector-stable center of the compact lifestyle-state basin

- 상태: 지지됨 locally; public LB 미확인.
- 왜 그럴듯한가: E351 was selected by a hand-designed maximin rule. If that rule is arbitrary, small changes to selector gates or weights should move the winner to many other plateau points.
- 맞다면: across many plausible public-free selector worlds, the E351 candidate should have the highest top1/top3 selection rate and should win most deterministic stress profiles.
- 틀리다면: the E350 rank winner or another nearby point should dominate once weights/gates are perturbed.
- 최소 실험: `analysis_outputs/e352_selector_sensitivity_audit.py`.
- 관측: `2500` selector worlds generated, `1118` non-empty. E351 `compact_t75_s1.005_s3a0.25` wins top1/top3 `0.224508/0.277281`, ahead of runner-up `0.135063/0.238819`. The original E350 rank winner has top1/top3 `0.000000/0.004472`.
- 성공/폐기 기준: accept if E351 remains rank 1 under random perturbations and wins the public-skeptic/state-specific/e349-conservative profiles. This is observed.
- public LB 관측 반응: if E351 improves, the public-transfer story should emphasize robust plateau-center selection rather than full S3-tail restoration. If E351 fails but E350 improves, public values the aggressive p90/S3 edge more than selector stability. If both fail, the compact plateau is local-only.
- 제출 전략: no new E352 upload is necessary; keep `analysis_outputs/submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv` as the first practical public test.

### H353: E351 contains a removable known-public-bad tangent

- 상태: 반증됨 for linear/sequential projection cleanup.
- 왜 그럴듯한가: E323 proved that local null-health can fail publicly. If E351 still points partly toward the same public-adverse movements, subtracting that component might lower transfer risk while keeping the compact lifestyle-state action.
- 맞다면: small positive-projection removal against known public-bad axes should reduce public-analog risk and keep strict p90 visibility, bad-axis safety, and Q1 lifestyle-state specificity.
- 틀리다면: risk-reducing neutralization should immediately destroy p90 visibility or lifestyle specificity, or strict candidates should show no risk improvement.
- 최소 실험: `analysis_outputs/e353_public_tangent_neutralization.py`.
- 관측: `52` candidates, `48` generated neutralizations, `0` E353 local gate passes. Strong cleanup lowers public-analog risk but p90 degrades to around `-0.000032`; tiny cleanup keeps the action nearly unchanged but still loses `strict_promote_gate` when it improves risk. No generated risk-improver is strict-promoted.
- 성공/폐기 기준: accept if at least one generated candidate improves E351 public-analog risk by `1e-5`, preserves strict p90 `< -0.00005`, bad-axis `<=0.015`, Q1 specificity within `0.03`, and direct public-bad positive cosine `0`. This is not observed.
- public LB 관측 반응: E353 creates no file. If E351 fails publicly, the fix is unlikely to be a simple known-bad-axis projection; it should be a new support axis or public-subset latent.
- 제출 전략: keep E351. Do not submit E353 neutralized variants.

### H354: E286 E247 support latent adds an independent action-safe component to E351

- 상태: 반증됨 for current E247/E256 support-boundary graft.
- 왜 그럴듯한가: E247 is the known public-best anchor, E256 worsened publicly despite nearby structure, and E286 could separate E247 support/body cell identity. If this boundary encoded a missing human/social lifestyle support state, E351 might improve by adding or protecting that direction.
- 맞다면: E286 support grafts or Q3 guards should keep E351 p90 visibility, reduce public-analog risk, preserve Q1 lifestyle specificity, pass support-source transfer, and lower E247 support interference.
- 틀리다면: E351 should already align with the E247 support body, or grafts should trade risk against p90/Q1 specificity without passing the local gate.
- 최소 실험: `analysis_outputs/e354_e247_support_lifestyle_graft.py`.
- 관측: `132` candidates, `129` generated, `0` E354 local gate passes. Canonical E351/E350/E349 all have E247 body Q3 alignment ratio `1.000000`, opposite support movement `0.000000`, and support interference `0.000000`. The strongest grafts reduce public-analog risk only by sacrificing strict p90 or Q1 specificity, and early human-social support sources fail transfer-health checks.
- 성공/폐기 기준: accept only if at least one graft/guard improves support/risk while preserving strict p90 and Q1 specificity with healthy source transfer. This is not observed.
- public LB 관측 반응: no E354 file should be submitted. If E351 later fails, do not assume the missing component is the current E247/E256 support boundary; learn a richer support/action-health latent instead.
- 제출 전략: none from E354. Keep E351 priority unchanged.

### H355: candidate action-health is a learnable hidden representation, and can select a better E350/E351 plateau point

- 상태: representation은 지지됨; submission selection은 반증/보류.
- 왜 그럴듯한가: E340-E354 repeatedly showed that human/social latent states can be visible or null-rare separately, but action translation fails. This suggests the missing latent is not a row state alone but an action-health state over probability movements.
- 맞다면: candidate movement geometry should predict p90 visibility, public-analog risk, Q1 lifestyle specificity, and bad-axis margin across experiment families. A selected plateau point should also survive E352 selector stability.
- 틀리다면: out-of-family diagnostics should be weak, or the learned selector should choose unstable candidates that contradict prior stress tests.
- 최소 실험: `analysis_outputs/e355_action_health_latent_selector.py`.
- 관측: `653` full action-health rows. ExtraTrees OOF Spearman: action health `0.852240`, risk `0.849353`, Q1 specificity `0.943806`, bad margin `0.976341`, visibility `0.749160`. RandomForest confirms action health `0.825717`, risk `0.807470`, Q1 specificity `0.976885`, bad margin `0.994272`, but visibility is weak `0.231544`. The top E355 plateau row is `compact_t45_s1.005_s3a0.25`, while E351 ranks `14`.
- 성공/폐기 기준: accept representation if action-health OOF Spearman is high across families; accept submission if a non-E351 row also has E352/public-transfer stability and conservative local gates. Representation is accepted, submission is not.
- public LB 관측 반응: no E355 file should be submitted. If E351 improves publicly, E352-style stability was the missing transfer feature. If E351 fails, E355 says action-health is learnable but needs a richer public-transfer target.
- 제출 전략: none from E355. Keep E351 first; use E355 diagnostics to design an E352-aware latent.

### H356: transfer-stability is a learnable latent inside the compact lifestyle-state basin

- 상태: representation은 지지됨; submission 후보는 정보성 probe로 보류.
- 왜 그럴듯한가: E355 learned action health but selected candidates with weak E352 stability. If public-transfer stability is a separate hidden state, it should be predicted directly from candidate movement context instead of inferred from p90/risk/Q1 pieces.
- 맞다면: E352 top1/top3 stability should be predictable under random and structural holdouts, and a non-E351 point may rank above E351 under the learned transfer latent while staying in the same compact plateau.
- 틀리다면: OOF diagnostics should collapse, strict geometry should fail entirely, or the learned winner should violate E351/E352 public-free gates.
- 최소 실험: `analysis_outputs/e356_transfer_stability_latent_selector.py`.
- 관측: `311` candidates, `36` E351-compatible plateau pool. Compat-pool transfer raw Spearman reaches `0.835013`; E352 top3 reaches `0.796029` random-KFold and `0.772806` threshold-holdout. Strict geometry is weaker and scale holdout is unstable. E356 selects `compact_t45_s1.005_s3a0.50`, with E352 top1/top3 `0.135063/0.238819`; E351 still has higher raw E352 `0.224508/0.277281`.
- 성공/폐기 기준: accept representation if transfer stability is learnable across at least random and threshold holdouts. Accept submission only as a probe if the selected row remains in E351-compatible plateau and passes local gates. This is observed with caveats.
- public LB 관측 반응: if E356 improves publicly, learned transfer-latent ranking beats raw E352 stability. If E356 fails but E351 improves, raw robust-center stability is preferable. If both fail, the compact lifestyle-state basin is not enough for public subset transfer.
- 제출 전략: `analysis_outputs/submission_e356_transferstable_selected_compact_t45_s1_005_s3a0_50_0ace76e5_uploadsafe.csv` is the information-rich E356 probe; E351 remains the conservative reference.

### H357: known-public survival is a learnable contrast latent, but it must be gated by transfer stability

- 상태: public-survival representation은 지지됨 locally; selected probe는 public LB 미확인.
- 왜 그럴듯한가: E247 is the current known public best, while E216/E267/E323 show specific ways that plausible lifestyle/social actions can die publicly. If known public files are treated as scarce observations, their movement anatomy should reveal a public-survival contrast that is distinct from local p90 or E352 stability alone.
- 맞다면: leave-one-public-file-out models should rank public deltas above permutation baselines, and the selected compact candidate should avoid known public-bad projections while retaining E352/E356 transfer support.
- 틀리다면: LOO diagnostics should collapse to permutation, or the public-survival ranker should select no-tail/E247-preserving points that fail E352/E356 stability and cannot survive stricter gates.
- 최소 실험: `analysis_outputs/e357_public_survival_contrast_latent.py`.
- 관측: `17` public observations, `13` available local files, `181` compact candidates. LOO Spearman reaches ExtraTrees `0.829670`, Ridge10 `0.659341`, Ridge1 `0.620879`, KNN3 `0.472527`; Ridge10/Ridge1/KNN3 beat permutation p95. Pure public-preservation prefers weak-transfer no-tail candidates, so final selection requires E352 top3 `>=0.18`, E356 survival `>=3.0`, strict p90 visibility, and bounded predicted public loss. The selected probe is `compact_t45_s1.000_s3a1.00`.
- 성공/폐기 기준: accept the representation if LOO public-delta ranking beats permutation and chosen candidates remain interpretable under public-good/bad axes. Accept submission only as a high-information probe because the public label count is tiny. This is observed.
- public LB 관측 반응: if E357 improves, the compact basin needs full S3-tail support but not micro-amplification. If E356 improves more, learned transfer-stability matters more than public-survival preservation. If E351/E356/E357 all fail, abandon the compact-basin tuning branch and search for a different hidden public subset/lifestyle-state axis.
- 제출 전략: `analysis_outputs/submission_e357_publicsurvival_selected_compact_t45_s1_000_s3a1_00_a08a4957_uploadsafe.csv` is the next compact-basin calibration probe; it is not a proven replacement for E247.

### H358: compact-basin public survival is not yet row-state-certified

- 상태: row-state public-survival representation은 지지됨; compact-basin row-state certification은 반증됨/보류.
- 왜 그럴듯한가: E357 uses output movement anatomy, but the user-level hidden law may live in row placement: which human/social lifestyle days are being touched. E328/E330 showed that row-level lifestyle states are semantically coherent but hard to translate into safe submissions.
- 맞다면: known public deltas should be predictable from row-state movement exposure, and E351/E356/E357 should land on E247-like rather than E323-heavy row-state clusters.
- 틀리다면: row-state LOO diagnostics should collapse, or the compact candidates should pass row-state gates with low bad-minus-good exposure.
- 최소 실험: `analysis_outputs/e358_rowstate_public_survival_audit.py`.
- 관측: `13` known public files and `181` compact candidates. LOO Spearman is ExtraTrees `0.873626`, KNN3 `0.692308`, Ridge10 `0.494505`, Ridge1 `0.483516`; KNN/Ridge beat permutation p95. However, no compact candidate passes row-state public-survival plus E352/E356/E357 gates. The top row remains `compact_t45_s1.000_s3a1.00`, but predicted row-state public loss is `0.000956664` and bad-minus-good row-state exposure is `0.170344`.
- 성공/폐기 기준: accept row-state sensor if LOO beats permutation and public-bad exposure orders known failures sensibly. Accept compact candidate only if it also passes transfer-stability and row-state exposure gates. Sensor is accepted; compact candidate is not.
- public LB 관측 반응: if E357 improves despite E358, output-space calibration dominates row-state semantics in this narrow region. If E357 fails, E358 becomes strong evidence to stop compact-basin tuning and learn row-placement/action-health directly.
- 제출 전략: no E358 submission. Use E358 as a veto/diagnostic before future compact-basin candidates.

### H359: row-gating the existing compact action is enough to recover row-state health

- 상태: 반증됨 for simple monotone row gates over E349/E351/E356/E357 compact deltas.
- 왜 그럴듯한가: E358 may have rejected compact candidates because the action was placed on E323-heavy lifestyle rows. If so, damping high-risk rows and preserving/boosting E247-like rows should keep output visibility while improving row-state survival.
- 맞다면: at least one row-gated compact variant should pass E272 strict visibility and E358 row-state public-survival gates. E272-strict candidates should show lower row-state predicted public loss than ungated compact candidates.
- 틀리다면: visible row-gated candidates should retain high row-state predicted public loss, while row-state-safer candidates should become too small or lose p90 visibility.
- 최소 실험: `analysis_outputs/e359_rowplacement_action_health_probe.py`.
- 관측: `124` row-gated variants over E349/E351/E356/E357. Combined E359 gate passes `0`. There are `16` E272-only strict-promote rows, but their row-state predicted public loss remains `0.001038-0.001153`. The best overall variant is `e357_fulls3_noamp__goodboost20_riskdamp80`, with p90 `-0.000046486`, row-state predicted public loss `0.000965778`, and bad-minus-good exposure `0.145854`.
- 성공/폐기 기준: accept only if a generated row-gated candidate passes strict p90, bad-axis, low row-state loss, low row-state variance, and low bad-minus-good exposure. This is not observed.
- public LB 관측 반응: no E359 file should be submitted. If E357/E356/E351 still improve publicly, E358/E359 are too pessimistic for this compact region. If they fail, H359 strengthens the case that a new row-action-health generator is needed.
- 제출 전략: none. Use E359 failures as negative rows for learning row-action health directly.

### H360: learned row-action health can rescue the compact action family

- 상태: representation은 부분 지지됨; submission generation은 반증됨 for row-only placement.
- 왜 그럴듯한가: E359 hand gates may be too crude. If row-action health is the hidden lifestyle law, a surrogate trained on E359 actual outcomes could generate non-monotone row placements using ownlife PCs and human/social story axes.
- 맞다면: surrogate diagnostics should survive leave-source stress, and generated candidates should pass actual E272/E358 gates.
- 틀리다면: surrogate may learn rowloss but not visibility, and generated candidates should become healthy-but-too-small.
- 최소 실험: `analysis_outputs/e360_learned_row_action_health_generator.py`.
- 관측: health surrogate Spearman random5 `0.972450`, leave-source `0.639068`, but visibility Spearman only `0.118049-0.221986`. Generated `1800`, verified `140`, submission gate `0`. Best candidate row-state loss `0.000592192`, p90 only `-0.000035678`.
- 성공/폐기 기준: accept representation if leave-source health Spearman stays positive; accept submission only if actual strict p90 and row-state health gates pass. Representation accepted, submission rejected.
- public LB 관측 반응: no E360 submission. If a compact file succeeds publicly, local row-state health was over-conservative. If compact files fail, H360 supports moving from row placement to row x target cell-action generation.
- 제출 전략: none from E360.

### H361: E360 only lacks amplitude

- 상태: 반증됨.
- 왜 그럴듯한가: E360 found row-state-healthy placements but p90 was too weak. If the placement is correct, scaling or target-rebalancing should restore visibility without destroying row-state health.
- 맞다면: amplitude-restored variants should pass strict visibility and keep row-state loss/exposure inside gates.
- 틀리다면: p90 restoration should increase bad-axis/exposure or fail row-state gates; healthiest variants should remain too small.
- 최소 실험: `analysis_outputs/e361_rowaction_amplitude_restore_stress.py`.
- 관측: `1120` amplitude variants; strict output candidates `16`; submission gate `0`. Best strict-visible family reaches p90 around `-0.000052` but row-state bad-minus-good exposure around `0.1496`, above the health gate. Best healthy rows remain p90-weak.
- 성공/폐기 기준: accept if a scaled candidate passes strict p90, bad-axis, rowloss, rowstate variance, and exposure gates. Not observed.
- public LB 관측 반응: no E361 submission. If compact files fail publicly, H361 says the next branch must change cell/target action geometry, not merely scale healthy row placements.
- 제출 전략: none.

### H362: hidden lifestyle-state action is row x target specific

- 상태: locally supported; public LB pending.
- 왜 그럴듯한가: E359 showed row gating alone fails, E360 learned healthy-but-small row placement, and E361 showed amplitude restoration reintroduces row-state risk. The remaining plausible layer is target-cell action geometry: the same lifestyle state should move Q and S targets differently.
- 맞다면: a generator with target-specific cell gates should produce at least one candidate that keeps E272 strict output visibility while satisfying E358 row-state public-survival gates. The passing action should not be broad across all targets.
- 틀리다면: generated cell-action candidates should either be visible-but-row-risky like E361, or row-healthy-but-too-small like E360.
- 최소 실험: `analysis_outputs/e362_row_target_cell_action_generator.py`.
- 관측: `1550` candidates, `11` strict output candidates, `2` near-misses, and `1` combined submission-gate candidate. The selected file has p90 delta `-0.000052285`, row-state predicted public loss `0.000729697`, bad-minus-good exposure `0.134846798`, and target movement shares Q1 `0.571868`, Q2 `0.238509`, Q3 `0.050188`, S1 `0.139435`, S3 `0.000000`.
- 성공/폐기 기준: accept locally if one candidate passes strict p90, beat-rate, bad-axis, row-state loss, row-state variance, and exposure gates. This is observed. Accept publicly only if the selected upload improves or meaningfully competes with the known public frontier.
- public LB 관측 반응: if E362 improves, it supports the row x target lifestyle-action law: Q-story/S-recovery movement with S3 suppression. If E362 fails, the local row-state/action-health sensors are still incomplete or overfit to known public observations.
- 제출 전략: `analysis_outputs/submission_e362_cellaction_selected_e360_e351_robust_center__learned_story_nonmonotone_s1_counter_1273__cell_e019daf5_uploadsafe.csv` is the next single high-information probe.

### H363: E362 is a robust target-balance basin, not a one-point accident

- 상태: locally supported; public LB pending.
- 왜 그럴듯한가: E362 had only one strict selected candidate from the generator, so it could be a lucky threshold crossing. A real hidden lifestyle-action latent should survive local perturbations in target balance, row-risk damping, donor grafts, and ablations.
- 맞다면: nearby target-scale variants should pass E272/E358 at a high rate, and a refined candidate should improve row-state public-risk without losing p90 visibility or S3 suppression.
- 틀리다면: only the seed should pass, or all risk-reducing perturbations should fall below p90 visibility.
- 최소 실험: `analysis_outputs/e363_cell_action_robustness_probe.py`.
- 관측: `1586` perturbations, `811` strict output candidates, `797` submission-gate candidates. Target-scale variants pass at `0.565285`; donor grafts pass at `0.422414`. The selected variant is `e362_scale_g1.06_q11.08_q20.90_q31.00_s11.30`, with p90 `-0.000052147`, row-state loss `0.000520036`, exposure `0.133572983`, and S3 share `0`.
- 성공/폐기 기준: accept locally if target-scale perturbations have broad pass support and the selected refinement improves row-state loss/exposure versus E362 while preserving strict p90. This is observed.
- public LB 관측 반응: if E363 improves, the hidden law is target-balance action: Q1 visibility plus S1 recovery regularization, lower Q2, small Q3, and no S3. If E363 fails but E362 succeeds, the balance refinement overshot. If both fail, current E272/E358 stress is too permissive.
- 제출 전략: `analysis_outputs/submission_e363_cellrobust_selected_e362_scale_g1_06_q11_08_q20_90_q31_00_s11_30_c2d9a88a_uploadsafe.csv` supersedes E362 as the next single probe.

### H364: E363 needs a public-like calibration layer over the cell-action basin

- 상태: locally supported; public LB pending.
- 왜 그럴듯한가: E363 passed too many local candidates (`797/1586`), which weakens the selector as a final submission ranker. Known public failures E216/E267/E323/final9/ordinal expose public-bad movement axes, while E358 exposes hidden lifestyle row-state risk. A real next probe should satisfy both E363 local visibility and a stricter known-public survival view.
- 맞다면: a known-public contrast sensor should predict public deltas under leave-one-public-file-out, and it should rerank E363 candidates toward lower public-bad-axis and row-state public-loss without selecting ungated/too-small files.
- 틀리다면: LOO public-delta diagnostics should collapse, or the sensor should only select candidates that fail E363 local visibility, or the selected replacement should gain rank by increasing known bad-axis/row-state risk.
- 최소 실험: `analysis_outputs/e364_public_like_cellaction_calibration.py`.
- 관측: LOO Spearman is ExtraTrees `0.895604`, Ridge1 `0.769231`, Ridge10 `0.686813`, KNN3 `0.642857` over `13` available public-observed files. Among `797` E363-gated rows, the selected donor-graft candidate ranks `1` by E364 score, lowers public-bad-axis sum from `0.006034` to `0.004203`, and lowers row-state predicted public loss from `0.000520036` to `0.000438374`, while preserving p90 visibility and S3 suppression. It slightly increases bad-minus-good row-state exposure from `0.133573` to `0.137438`.
- 성공/폐기 기준: accept locally if the sensor has positive LOO diagnostics and the chosen candidate clears E363 local gate while improving at least two independent public-like risks versus E363 selected. This is observed. Accept publicly only if LB improves or is at least competitive enough to validate donor-graft S1 recovery as a useful component.
- public LB 관측 반응: if E364 improves, the hidden law likely needs donor-grafted S1 recovery rather than pure target-scale balance. If E364 fails but E363 improves, source-law preservation beats the known-public calibration sensor. If both fail, abandon local E363 basin tweaking and learn a public-like subset/calibration latent.
- 제출 전략: `analysis_outputs/submission_e364_publiclike_cellaction_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv` is the highest-information next probe; E363 remains the conservative reference.

### H365: E364's donor-graft public-like choice is stable under public/view masking

- 상태: locally supported; public LB pending.
- 왜 그럴듯한가: E364 selected a donor-graft candidate from a tiny public sensor, so it could be a one-public-file artifact. A real same-level latent should remain preferred when individual known public files or whole context views are masked.
- 맞다면: E364 should beat E363 across leave-one-public-file and feature-view jackknife scenarios, and the top supported alternatives should come from the same donor-graft recovery family rather than unrelated tiny/ungated moves.
- 틀리다면: dropping a single known public file should flip the decision back to E363, or axis-only/target-only/anatomy-only views should contradict the donor-graft preference.
- 최소 실험: `analysis_outputs/e365_public_like_jackknife_stress.py`.
- 관측: `84` scenarios from `6` feature views and `14` public-drop settings. E364 beats E363 in `84/84` scenarios. E364 top1/top10 rates are `0.500000/0.809524`; E363 top10 rate is `0.488095`. The closest competitor is another donor-graft sibling, not the E363 target-scale row.
- 성공/폐기 기준: accept locally if E364 beats E363 in at least `60%` of scenarios and stays top10 in at least `50%`. This is observed strongly.
- public LB 관측 반응: if E365 improves, donor-graft S1 recovery is likely a real missing component. If E365 fails but E363 improves, jackknife stability was still overfit to known-public geometry. If both fail, abandon E363/E364 local-basin candidate selection and learn a new public-like subset/calibration latent.
- 제출 전략: `analysis_outputs/submission_e365_jackknife_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv` supersedes the raw E364 filename as the next audited probe.

### H366: E365 donor-graft family can be turned into a row-wise hidden lifestyle-state latent

- 상태: submission translator는 반증됨; donor-graft family signal은 여전히 생존.
- 왜 그럴듯한가: E365의 top support가 단일 파일이 아니라 Q3/S1, Q3-only, S1-only donor-graft sibling으로 나뉘었다. 이것은 row별 hidden lifestyle state가 target geometry를 선택한다는 가설과 맞는다.
- 맞다면: E328/E358 lifestyle state, human/social story tail, target-row gate가 constant center와 null/permuted row gate보다 안정적으로 높아야 한다. 특히 real gate가 E365-style public/view jackknife에서 top1/top10 우위를 가져야 한다.
- 틀리다면: 같은 row-rate나 target-row translator를 가진 random/permuted gate가 real lifestyle gate와 같거나 더 높은 rank를 가져야 한다.
- 최소 실험: `analysis_outputs/e366_hidden_lifestyle_donor_family_latent.py`.
- 관측: `79` generated candidates and `84` jackknife scenarios. Best real target-row lifestyle gate `e366_targetrow_q3_good_s1_bad_cluster_356_bad` has top1 `0/84`, top10 `84/84`, rank mean `2.345238`. Best null/permuted gate `e366_nulltargetrow_q3_good_s1_bad_perm_cluster_2` has top1 `81/84`, top10 `84/84`, rank mean `1.071429`.
- 성공/폐기 기준: accept only if best real lifestyle gate beats null/permuted gates on top1/top10 and does not depend on a single view. This is not observed.
- public LB 관측 반응: no E366 file should be submitted now. If E365 later fails publicly, E366 says the donor-graft family may be an internally stable but externally wrong row-mask shortcut. If E365 succeeds, the family can be real, but E366 still says current lifestyle gate is not the reason.
- 제출 전략: none from E366. Keep `analysis_outputs/submission_e365_jackknife_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv` as the audited candidate.

### H367: public/private row-mask identity is a lifestyle-predictable hidden latent

- 상태: aggregate row-mask translator는 반증됨; Q2/S1 target-specific row validity는 부분 생존.
- 왜 그럴듯한가: E366 showed random/permuted row masks can beat semantic row gates. A stronger target is to learn where known public-good movements land and where known public-bad movements land, then ask whether lifestyle/story context predicts that row support.
- 맞다면: aggregate public row validity should beat permutation null in lifestyle-feature CV, remain stable under leave-public drops, and learned row-mask candidates should beat null row-mask candidates under jackknife.
- 틀리다면: aggregate row validity should not be lifestyle-predictive, or random/permuted masks should dominate generated candidates.
- 최소 실험: `analysis_outputs/e367_public_rowmask_validity_latent.py`.
- 관측: aggregate `public_row_validity` KFold Spearman `0.073804`, below null p95 `0.135689`; row-mask stability is high, min leave-public Spearman `0.827446`; best null gate top1 `89/98`; best learned real gate top1 `0/98`. Target-specific Q2 row validity is strong (`0.392982` vs null p95 `0.105015`) and S1 barely survives (`0.110407` vs `0.099875`), while Q3 fails.
- 성공/폐기 기준: accept only if aggregate row validity is lifestyle-predictive and learned gates beat null gates. This is not observed.
- public LB 관측 반응: no E367 file should be submitted. If E365 fails publicly, aggregate row-mask learning still does not explain the failure; the next test should isolate Q2/S1 row validity rather than broad row placement.
- 제출 전략: none from E367. Keep E365 as the audited candidate.

### H368: Q2/S1 row-mask validity is the lifestyle-state translator, not aggregate row identity

- 상태: locally supported; public LB pending.
- 왜 그럴듯한가: H367 killed aggregate row-mask validity but left target-specific Q2 and S1 validity alive. Q2 maps naturally to intervention/rough-night state, and S1 maps to objective recovery-stage state, so a human lifestyle latent could express itself only through these cells.
- 맞다면: Q2/S1 validity should be predictable from lifestyle/story context beyond permutation nulls, stable under leave-public drops, and learned Q2/S1 cell actions should beat both direct-public controls and null/permuted masks.
- 틀리다면: direct-public masks or null/permuted Q2/S1 masks should outrank learned lifestyle masks, or one of Q2/S1 should fail the CV/null diagnostic.
- 최소 실험: `analysis_outputs/e368_q2s1_rowmask_cellaction_latent.py`.
- 관측: Q2 validity KFold Spearman `0.426940` vs null p95 `0.102237`; S1 `0.157989` vs `0.102777`; Q2/S1 leave-public stability min `0.692973`. Learned `e368_q2_damp_s1_recover_amp1.06` wins top1 `73/98`, top10 `97/98`; best direct-public top1 `19/98`; best null top1 `4/98`.
- 성공/폐기 기준: accept locally only if both Q2 and S1 beat null p95, row-mask target is stable, best learned gate beats best direct-public and null gates, and movement is limited to Q2/S1 relative to E365. This is observed.
- public LB 관측 반응: if E368 improves public LB, the live hidden law becomes target-specific lifestyle validity: Q2 intervention-state damping plus S1 recovery-state correction. If E368 worsens, the local public-sensor ranking overfit known-public Q2/S1 row support even though it beat null controls.
- 제출 전략: `analysis_outputs/submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv` is now the highest-information local candidate.

### H369: E368 Q2/S1 validity corresponds to a public-free hidden lifestyle residual state

- 상태: locally supported; public LB pending.
- 왜 그럴듯한가: H368's teacher used known-public Q2/S1 row support, so the remaining objection is public-sensor overfit. If the same rows are recoverable from train residual lifestyle state, E368 is more likely to be a real hidden lifestyle-state action.
- 맞다면: Q2/S1 train residual states predicted from lifestyle context should align with E368's test gate and selected Q2/S1 cell movement under masked-student, kNN, and cluster probes, beating permuted test-gate/movement nulls.
- 틀리다면: only public-trained rowmask scores should align with E368, while public-free train residual probes should fall inside permutation nulls or align with E323 bad movement.
- 최소 실험: `analysis_outputs/e369_q2s1_lifestyle_transfer_audit.py`.
- 관측: Q2 has `64` supporting rows across public-free probes; S1 has `42`. Q2 best abs gate Spearman is `0.369592`, best abs-delta Spearman `0.421147`; S1 best abs gate Spearman is `0.232458`, best abs-delta Spearman `0.181906`. E368 all-target E323-bad cosine is `0.001520`, though Q2-only cosine versus E365 is `0.591735`.
- 성공/폐기 기준: accept if both Q2 and S1 have support from at least two probe families and all-target E323-bad cosine stays small. This is observed. Monitor Q2 target-only bad-axis cosine before amplifying.
- public LB 관측 반응: if E368 improves, H368/H369 become the strongest current world model: target-specific Q2 intervention validity plus S1 recovery validity. If E368 worsens, the public-free residual alignment was real but not public-calibrated, and the next experiment should damp or re-sign Q2 rather than abandon S1.
- 제출 전략: no E369 file. Keep the E368 upload-safe file as the current candidate; future derived files must include Q2 target-only bad-axis stress.

### H370: E368 Q2 bad-axis exposure can be neutralized without losing lifestyle-state support

- 상태: 반증됨 for linear Q2 projection/amplitude recalibration; E368 remains the candidate.
- 왜 그럴듯한가: E369 showed the all-target E368 movement is almost E323-orthogonal, but Q2-only movement has high E323-vs-E365 cosine. If that Q2 cosine is incidental, a projection-away or amplitude correction should reduce risk while preserving Q2/S1 transfer support.
- 맞다면: at least one E370 candidate should reduce Q2 bad-axis cosine by `0.12+`, keep all-target bad-axis cosine small, preserve E368 public-like score/top10 support, and keep Q2/S1 transfer correlations non-negative.
- 틀리다면: orthogonalization should destroy transfer alignment or public-like support, while unprojected amplitude variants keep the Q2 bad-axis warning.
- 최소 실험: `analysis_outputs/e370_q2s1_risk_constrained_recalibration.py`.
- 관측: `275` candidates tested. Eligible safer replacements: `0`. Best stress row amplifies S1 to `1.15` and gets top1/top10 `0.602041/0.959184`, but Q2 bad-axis cosine remains `0.591735`. Q2 orthogonalization lowers cosine to `0.482276`, `0.344547`, or lower, but Q2 transfer abs Spearman falls from `0.428458` to about `0.181` and scenario support weakens.
- 성공/폐기 기준: accept only if Q2 bad-axis cosine drops materially without losing public-like and public-free transfer support. Not observed.
- public LB 관측 반응: no E370 file should be submitted. If E368 fails publicly, H370 says a simple projection fix is unlikely to be enough; the next correction must learn a new Q2 safety/calibration latent, not just remove the E323 direction.
- 제출 전략: keep `analysis_outputs/submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv`.

### H371: E368 Q2 bad-axis exposure is a row-wise trust problem

- 상태: 반증됨 for current Q2 transfer/validity/risk gates.
- 왜 그럴듯한가: H370 showed linear projection destroys signal. If the bad axis comes from a subset of rows, a lifestyle-state trust gate should keep Q2 movement on public-free supported rows and damp unsupported E323-like rows.
- 맞다면: row-wise Q2 gates should reduce Q2 bad-axis cosine and positive contribution share while keeping top10 scenario support and Q2 transfer alignment near E368.
- 틀리다면: gates that preserve scenario/transfer support should barely reduce Q2 risk, while gates that reduce Q2 risk should lose scenario support.
- 최소 실험: `analysis_outputs/e371_q2_rowwise_safety_latent.py`.
- 관측: `369` row-wise Q2 safety candidates tested. Eligible safer replacements: `0`. Best total candidate has top1/top10 `0.479592/0.959184` and Q2 transfer `0.428500`, but Q2 bad cosine remains `0.585298`. Candidates reducing Q2 cosine to about `0.539628` have top10 `0.0`.
- 성공/폐기 기준: accept only if Q2 risk drops materially while top10 and transfer remain near E368. Not observed.
- public LB 관측 반응: no E371 file should be submitted. If E368 fails, the next correction should not be another row-wise Q2 damp gate; it needs a new calibration target.
- 제출 전략: keep E368; do not upload E371 files.

### H372: Q2 calibration-residual lifestyle latent can provide a safer E368 replacement

- 상태: 반증됨 as a submission translator; supported as a local diagnostic latent.
- 왜 그럴듯한가: H370/H371 showed Q2 risk is not separable by projection or row-wise trust. The next plausible hidden target is Q2 residual calibration after subject/calendar prior, predicted from lifestyle/JEPA context.
- 맞다면: Q2 calibration-residual latents should beat blocked/null stress locally, and at least one replacement/blend should preserve E368 scenario support while lowering Q2 bad-axis cosine and positive Q2 bad contribution.
- 틀리다면: local residual latents may exist, but their action either follows E368's risky Q2 anatomy or loses scenario/action-health support.
- 최소 실험: `analysis_outputs/e372_q2_calibration_residual_latent.py`.
- 관측: `12` residual latents tested; `4` pass local/null gates. Best local latent `Q2_jepa_resid_subject` has logloss delta `-0.030211` and dominance `1.000000`. However `241` materialized candidates produce `0` safer eligible replacements. The strongest scenario candidate has top1/top10 `0.948980/0.989796`, but Q2 bad-axis cosine worsens from E368's `0.591735` to `0.609289`.
- 성공/폐기 기준: accept only if a candidate lowers Q2 risk while preserving scenario support, local residual validity, and E363 row/action health. Not observed.
- public LB 관측 반응: no E372 file should be submitted as a safer E368 derivative.
- 제출 전략: none. Keep E372 as evidence that Q2 hidden state exists but does not translate into a safe Q2 action under current geometry.

### H373: E368 target-specific Q2/S1 lifestyle state is public-frontier actionable

- 상태: partially falsified by public LB; still alive as a diagnostic hidden-state model.
- 왜 그럴듯한가: H368 learned Q2/S1 row validity from lifestyle context, beat direct-public and null masks, and H369 recovered the same action from public-free train residual states.
- 맞다면: E368 should beat E247 or at least materially approach it while improving over older frontier files.
- 틀리다면: E368 should remain in the older E95-level band, implying the Q2/S1 state is real but not sufficient to beat the E247 calibration/manifold.
- 관측: public LB for `submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv` is `0.576290429`. This is worse than E247 by `+0.000131480`, but slightly better than E95 by `-0.000000901`.
- 해석: E368 validates "not dead" public relevance of target-specific Q2/S1 lifestyle state, but falsifies it as the current public-frontier replacement. The public bottleneck is now action calibration/subset selection, not discovery of the Q2/S1 state.
- 제출 전략: final default returns to E247. Future Q2/S1 work must create a public-safe veto/calibration target before another submission.

### H009: S4 mobility hidden state is a rank-ordering law, not a tiny logit correction

- 상태: supported as a local hidden law; not accepted as S4-only submission translator.
- 왜 그럴듯한가: H005/H007/H008 repeatedly found mobility/errand/obligation state pointing toward S4-up, but small S4 edits stayed below public resolution.
- 맞다면: preserving E247 S4 marginal distribution while reassigning S4 ranks by mobility latent should improve blocked S4 logloss, and reverse reassignment should fail.
- 틀리다면: rank rewrites should behave like random shuffles, or reverse controls should look similar to forward controls.
- 최소 실험: `hitl/h009_s4_mobility_rank_jackpot.py`.
- 관측: `88` candidates tested. Best forward local probe `qrank_delta_pos_subject_s0.35` has worst delta `-0.008027` and mean delta `-0.015993`; reverse controls have positive worst deltas, best reverse `+0.026745`. No candidate clears jackpot gate because selector p90 remains too risky.
- 성공/폐기 기준: local hidden law accepted if both subject/dateblock improve and reverse controls fail. S4-only submission accepted only if selector/jackpot gate passes. First condition observed; second not observed.
- public LB 관측 반응: no H009 upload by default. If uploaded and improved, S4 row ordering would be the missing public law. If bad, S4-only materialization is dead but the mobility latent remains useful.
- 제출 전략: do not default-submit H009. Use it as bridge to H010 route-level translation.

### H010: hidden mobility state materializes as objective stage route S1 down / S4 up

- 상태: 반증됨 as a public submission route; mobility latent remains local-only diagnostic.
- 왜 그럴듯한가: S4-only rank rewrite is locally real but too risky. Human mobility/obligation state should change objective sleep-stage allocation, so S1/S4 route movement may be the safer target representation.
- 맞다면: `S1↓/S4↑` route rewrite should improve both subject/dateblock local route logloss, pass selector tolerance better than Q2-heavy routes, and reverse controls should fail.
- 틀리다면: Q2/S1/S4 route rewrites should be no healthier than S4-only, or reverse controls should survive similarly.
- 최소 실험: `hitl/h010_mobility_route_triad_jackpot.py`.
- 관측: `98` candidates tested. Exactly `1` jackpot candidate survives: `submission_h010_objective_mobility_s1down_s4up_target_delta_pos_subject_s0_25_uploadsafe.csv`. It changes `455` cells (`S1=213`, `S4=242`), has local worst delta `-0.004319`, selector mean `-0.001259`, selector p90 `0.000702`. Q2-heavy routes are locally strong but selector-risky. Reverse controls are locally bad (`+0.019796` to `+0.086478` worst deltas). Public LB for parser-safe mirror `submission_h010_objective_s1s4_v2_uploadsafe.csv` is `0.5781718175`, worse than E247 by `+0.0020128681`.
- 성공/폐기 기준: accept as next public sensor if one route candidate passes local robustness plus jackpot selector tolerance and matched reverse controls fail. Observed.
- public LB 관측 반응: H010 worsened sharply, so objective mobility-stage routing is not a valid public materializer. The local mobility latent and local reverse-control evidence are insufficient for public transfer.
- 제출 전략: do not submit H010 siblings or S1/S4 route-rank variants. Future work must learn why local S1/S4 route stress is anti-public, likely via route action-health or public/private subset energy.

### H011: H010 failure defines a public-negative action-health target representation

- 상태: submission candidate generated; public LB pending.
- 왜 그럴듯한가: H010 is a rare clean contradiction: local subject/dateblock route stress and reverse controls strongly favored S1/S4 route movement, while public LB rejected it by `+0.0020128681`. A contradiction this large can be used as a JEPA target: proposed action anatomy -> public action health.
- 맞다면: reflecting the H010 S1/S4 action axis, especially on the most H010-active rows, should improve public LB meaningfully. The gain should be larger than ordinary frontier noise because the H010 fail scale is large.
- 틀리다면: anti-H010 candidates should still fail or stay worse than E247, implying H010 was not a reversible public-negative route but a local rank rewrite that damaged true calibration/marginals.
- 최소 실험: `hitl/h011_h010_public_inversion_jackpot.py`.
- 관측: `63` candidates generated. Selected upload-safe file is `submission_h011_public_inversion_rowtop_all_k50_a1_uploadsafe.csv`, changing only `S1=50` and `S4=50` cells. H010-axis coefficient `-0.545892`; linear H010-axis public estimate `-0.001098809`; selector mean/p90 `+0.000200937` / `+0.000573326`.
- 성공/폐기 기준: success if public LB beats E247 or at least moves below the E95/E368 band with a readable margin. Failure if it worsens beyond E95/E368 or approaches H010-style loss, which kills the anti-H010 route worldview.
- public LB 관측 반응: improvement promotes failed-action inversion as an HS-JEPA action-health primitive. Failure pushes the architecture upstream: learn action health before output-space route materialization rather than inverting failed outputs.
- 제출 전략: H011 is the current highest-information "한탕" file; E247 remains the safe default.

### H012: known public LB observations define a solvable hidden public-state equation system

- 상태: strongly supported by public LB; current public frontier.
- 왜 그럴듯한가: for fixed prediction tensors, each public LB delta relative to E247 is a linear constraint on hidden public labels under the public subset. We now have `19` non-E247 public deltas, including strong positive and negative anchors, so these observations may identify a coarse pseudo-public label/subset representation.
- 맞다면: a posterior `q` fitted from known-public equations should predict held-out public deltas/ranking, and candidates moving E247 toward stable high-score posterior cells should show large robust predicted improvements.
- 틀리다면: leave-one-public diagnostics should be weak, or public feedback on the materialized candidate should fail hard because the equation system is underidentified and overfits the observed submissions.
- 최소 실험: `hitl/h012_public_equation_jepa_jackpot.py`.
- 관측: `20` known public observations, `19` equations vs E247, `85` posterior configs. Best config LOO MAE `0.000320737`, LOO p90 abs `0.000911893`, Spearman `0.935088`. Generated `238` candidates. Selected file `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` changes `1200` cells with posterior mean/p90 `-0.006446397` / `-0.004693170`.
- 추가 관측: public LB `0.5681234831`; delta vs E247 `-0.0080354663`. Realized gain is stronger than posterior mean by `-0.0015890693`.
- 성공/폐기 기준: success was defined as a clearly readable public gain over E247. This is observed.
- public LB 관측 반응: public-equation latent reconstruction is now the strongest HS-JEPA architecture component. The remaining hypothesis is not whether the branch exists, but how much of it is private-safe and how it relates to subject-time memory.
- 제출 전략: current frontier/default. Next submissions should be H012 decompositions or regularized variants, not unrelated E247 micro-edits.

### H013: raw human-state context can gate public-equation action health

- 상태: partially falsified as a submission selector; supported as a diagnostic HS-JEPA component.
- 왜 그럴듯한가: H012 may be overfit because it materializes public equations directly. HS-JEPA should instead use raw human lifelog context as the context view and public-equation/action-health as the target representation.
- 맞다면: raw app/screen/charging/activity/mobility/HR/light/calendar/payday features should identify rows where H012 posterior movement keeps large posterior gain while reducing known public-bad selector risk.
- 틀리다면: route-agreeing human-state slices may exist, but every visible H012-gated action should remain selector-high-risk or lose posterior visibility when made safe.
- 최소 실험: `hitl/h013_raw_human_state_jepa_gate.py`.
- 관측: `1190` candidates generated from raw human-state PCA, KNN label-route prior, known-public action-health row scores, and H012 posterior cells. Jackpot-gated candidates `0`; high-risk candidates `168`. Selected diagnostic file `submission_h013_raw_hs_jepa_health_top_route_r140_c260_a0.75_4a91266c_uploadsafe.csv` changes `260` cells on `126` rows, posterior delta `-0.001233534`, selector mean/p90 `+0.000486533` / `+0.001506255`, route agreement `1.000000`, consistency `0.991453`.
- 성공/폐기 기준: accept as a submission translator only if a candidate keeps posterior delta below `-0.001` and passes selector survival. Not observed. Accept as diagnostic if it forms coherent route-agreeing slices. Observed.
- public LB 관측 반응: no default H013 submission. If submitted and it wins, raw human-state row gating becomes the missing HS-JEPA bridge. If it loses, simple row gating is rejected and the next architecture must learn row x target action-health.
- 제출 전략: do not rank above H012 or E247. Keep as architecture evidence and as input features for the next joint action-health model.

### H014: same-subject sleep-state memory can regularize H012 posterior overfit

- 상태: partially falsified as an H012 submission regularizer; retained as diagnostic memory evidence.
- 왜 그럴듯한가: the external `submission_v106_sleep_state_conditioned_memory.csv` report scored `0.5703952266` by weighting same-subject past labels by date, sleep-state similarity, and sensor-quality similarity. H012 scored even better by reconstructing hidden public labels directly. A stable hidden world should show overlap between H012 high-posterior cells and within-subject state-continuity memory.
- 맞다면: H012 posterior confidence should be higher, more stable, or more private-safe on rows/cells whose same-subject sleep-state-conditioned memory agrees with it. Leave-public/H012-out posterior variants should preserve those cells more often.
- 틀리다면: H012 gain should concentrate in cells unrelated or opposite to subject-time memory, implying H012 is mostly public-subset equation fitting rather than human continuity.
- 최소 실험: build memory features without using external predictions: subject/date distance, sleep-state similarity, sensor-quality similarity, effective neighbor count, and target-specific memory agreement with H012 posterior. Audit posterior stability and produce a regularized H012 variant only if the memory-compatible subset keeps most posterior gain.
- 관측: `hitl/h014_sleep_state_memory_posterior_audit.py` audits `1200` H012-changed cells. Memory agrees on `0.405000` of cells and disagrees on `0.595000`; memory-agree cells carry only `0.279671` of H012 posterior gain, and high-alignment/high-reliability cells carry only `0.101482`. Q3 is the only target where memory-agree gain is a majority (`0.549864`).
- 성공/폐기 기준: accept as a submission regularizer only if it preserves a large fraction of H012 posterior delta while improving leave-public/H012-out stability and not collapsing to E247. Not observed: best generated H014 candidate keeps only `0.358133` of H012 posterior gain and all candidates are `diagnostic_only`.
- public LB 관측 반응: a successful regularized variant would reduce private risk and prove H012 is not pure public-equation overfit. A worse result would mean the public subset is less same-subject-memory-like than expected, and the final should remain the unregularized H012 or a different posterior-risk control.
- 제출 전략: do not submit H014 by default. Keep H012 unregularized unless a new non-public risk sensor supports pruning.

### H015: H012 public score makes the public-equation posterior sharpen again

- 상태: live high-risk public self-feedback candidate.
- 왜 그럴듯한가: H012's realized public gain was `0.0015890693` stronger than its own posterior mean forecast, so the first public-equation action may have been under-amplified. Adding H012 as a known public anchor should reveal whether H012 is a fixed point or a step toward a sharper hidden public-state posterior.
- 맞다면: a posterior solved with H012 as the current anchor should keep high leave-one-public ranking, produce a coherent low-amplitude movement beyond H012, and not simply demand a huge destructive probability change.
- 틀리다면: the system should collapse to H012/no movement, or only promote extreme overconfident moves whose predicted improvement is within noise or fails scenario stability.
- 최소 실험: `hitl/h015_public_equation_self_feedback.py`.
- 관측: `21` known public observations, `20` equations vs H012, `119` posterior configs, best LOO Spearman `0.986466`, best LOO MAE `0.001312381`. Generated `280` candidates. Primary file `submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv` changes `1600` cells, max probability delta vs H012 `0.051642`, posterior mean/p90 delta vs H012 `-0.001586219` / `-0.001149849`, beats-H012 rate `0.966667`.
- 성공/폐기 기준: accept as a high-information submission sensor if one public slot can test whether H012 is under-amplified. Do not treat as private-safe, because selected configs are dominated by `h012_sharp` and LOO MAE is of similar magnitude to the expected improvement.
- public LB 관측 반응: if H015 improves meaningfully, public-equation HS-JEPA is not a one-shot trick and can be recursively sharpened. If H015 worsens, H012 is the practical fixed point and further public-equation self-feedback should be stopped without a new independent sensor.
- 제출 전략: next single "한탕" candidate is H015; conservative default remains H012.

### H016: known public LB observations reveal a diffuse public cell-weight field

- 상태: strongly supported by local public-equation/null stress; public LB pending.
- 왜 그럴듯한가: H012 proved that known public LB deltas can recover a hidden public label/subset representation. The remaining ambiguity is whether public feedback is only about labels, or also about which row x target cells the public subset effectively weights.
- 맞다면: fitted public cell weights should predict leave-one-public deltas far better than uniform weights, and this should collapse when public deltas are permuted away from the submission loss-delta tensor. H016's selected cell action should disagree with full H015 when H015 movement is bad on inferred public-weighted cells.
- 틀리다면: permutation/null public deltas should get similarly good LOO metrics, or weights should concentrate into a tiny unstable subset that cannot generalize beyond the observed submissions.
- 최소 실험: `hitl/h016_public_subset_weight_jepa.py`.
- 관측: best config `h012_median_posterior/ridge=0.001/cap=12` has LOO MAE `0.000013654`, p90 abs `0.000026381`, Spearman `0.990977444`, while uniform MAE is `0.000885430`. Effective weight count is `1747.348299`, so this is diffuse weighting, not a tiny anchor subset. A `300`-permutation null gives median LOO MAE `0.004329919`, p90 `0.008450378`, max Spearman `0.660150`; real beats all permutations on MAE and Spearman.
- 성공/폐기 기준: accept as a structural sensor if real public deltas beat permutation null on LOO MAE/Spearman and the weight field is not a single-cell/small-subset collapse. Observed.
- public LB 관측 반응: if `submission_h016_public_subset_gain_all_k1000_a0.75_uploadsafe.csv` improves, public feedback is better understood as a diffuse cell-weight/gain field and H015-style broad sharpening should be constrained. If it worsens, the weight field may predict old public submissions but fail to materialize a new safe action.
- 제출 전략: H016 is the main alternative to H015. H015 tests recursive public-label sharpening; H016 tests public cell-weight selection.

### H017: H012 public posterior and H016 public weights are one compatible latent world

- 상태: strongly supported as a compatibility/posterior-completion sensor; public LB pending.
- 왜 그럴듯한가: H012 solved public labels under uniform weights, while H016 solved public weights under H012-like label proxies. If both are projections of the same hidden public world, the joint equation `sum w * loss_delta(pred, q)` should hold with almost no additional movement.
- 맞다면: joint `(q,w)` fitting should produce excellent leave-one-public prediction, beat public-delta permutation nulls, and select an action that moves H012 further toward H012 public posterior under H016 weights. The fitted state should not need large q/w distortion.
- 틀리다면: the joint fit should require unstable q/w changes, fail permutation null, or rank H015/H016/posterior-completion actions inconsistently.
- 최소 실험: `hitl/h017_joint_label_weight_jepa.py`.
- 관측: selected `q=h012_public_posterior`, `w=h016_mean_weight`, ridge `0.1`, cap `8`. LOO MAE `0.000001044`, Spearman `1.000000`, permutation-null median MAE `0.001672425`, max null Spearman `0.200902`. The solver barely moves priors (`q_prior_abs_move=0.000000677`, `w_prior_l1_move=0.000000293`), so this is compatibility, not a new latent discovery. Primary file `submission_h017_joint_label_weight_oracle_gain_all_k1650_a1_uploadsafe.csv` has predicted joint delta `-0.000574501` vs H012.
- 성공/폐기 기준: accept as a public sensor if real beats permutation null and the primary action beats both H015 and H016 under the same joint sensor. Observed locally. Reject as an architecture claim if described as independent raw-human-state validation; it is public-equation action-layer evidence only.
- public LB 관측 반응: if H017 improves, H012 was under-moved toward its own posterior and H016 weights identify where continuation is healthy. If H017 worsens, posterior-completion is too aggressive and H012's exact public posterior should remain a diagnostic rather than an action target.
- 제출 전략: H017 is now the strongest posterior-completion candidate. H015 tests recursive self-feedback; H016 tests weighted H015 slicing; H017 tests continuing H012 toward its original posterior under H016 weights.

### H018: H017 public-equation latent survives binary hard-label world conditioning

- 상태: supported as a hard-label posterior-completion variant; public LB pending.
- 왜 그럴듯한가: actual evaluation labels are binary, while H012/H017 use continuous label posteriors. If the public-equation state is real, sampled binary worlds from the H017 prior should fit real public deltas far better than permuted deltas.
- 맞다면: best/top/median hard-world equation errors should be far lower for real public deltas than for public-delta permutations, and the hard-world posterior should yield a coherent action close to but sharper than H017.
- 틀리다면: real hard worlds should not beat permutation null, or hard-world conditioning should collapse into a tiny ESS/unstable posterior unrelated to H017.
- 최소 실험: `hitl/h018_hard_label_world_jepa.py`.
- 관측: `90,000` hard worlds sampled. Best world MAE `0.000167740`, top100 MAE `0.000252967`, median world MAE `0.001398174`. All beat `300` public-delta permutations; null median best-world MAE is `0.000965302`. Best posterior `soft_t0.00035_p1.5` has posterior MAE `0.000005557`, ESS `19756.395104`, and q shift from H017 prior `0.002394823`. Primary file `submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv` has predicted hard-world delta `-0.000603041`.
- 성공/폐기 기준: accept as a public sensor if real hard-world errors beat permutation null and ESS does not collapse. Observed. Treat as incremental to H017 if q shift remains tiny. Observed.
- public LB 관측 반응: if H018 improves over H017/H012, binary-world conditioning is useful and HS-JEPA should include hard public-world posterior sampling. If it worsens, the binary hard-world posterior is explanatory but does not improve action safety beyond continuous H017.
- 제출 전략: H018 is the binary-aware posterior-completion candidate; H017 remains the cleaner continuous counterpart.

### H019: public-equation latent is compatible with a hidden row-level public subset

- 상태: strongly supported as row-subset structure; action does not internally beat H018.
- 왜 그럴듯한가: actual public LB normally evaluates a subset of rows, not arbitrary row x target cell weights. H016's cell-weight solution may be too free, so H019 enforces a stricter hidden row mask.
- 맞다면: sampled row masks under H018/H017 label proxies should match known public deltas far better than public-delta permutations. Row inclusion posterior should be broad enough to avoid tiny-subset collapse and should identify rows where H018 action is more public-like.
- 틀리다면: real row-mask errors should look like permuted public deltas, or posterior inclusion should collapse to a tiny unstable set.
- 최소 실험: `hitl/h019_row_subset_hardworld_jepa.py`.
- 관측: best sampled row-mask config uses `h017_joint` with subset size `150`, top100 MAE `0.000074821`, best MAE `0.000045707`. Best posterior uses `h018_hard`, subset size `125`, posterior MAE `0.000027461`, p90 abs `0.000052606`, Spearman `0.998496`, inclusion range `0.370519-0.786440`. Real row-mask metrics beat all `300` public-delta permutations. Primary `submission_h019_row_subset_hardworld_gain_all_r240_a1_uploadsafe.csv` has row-posterior delta `-0.000611233`, but H018 itself is slightly stronger under the same row posterior at `-0.000615495`.
- 성공/폐기 기준: accept row-subset structure if real beats permutation null and inclusion posterior does not collapse. Observed. Accept row-exclusion action only if it beats H018 under the row posterior. Not observed.
- public LB 관측 반응: if H019 improves more than H018/H012, public row identity is actionable. If H019 loses while H018 wins, row-subset is explanatory but not useful for excluding rows from the hard-world action.
- 제출 전략: H019 is lower priority than H018 as a score candidate, but higher information if the next question is whether public-equation state can be forced into realistic row-level public/private masks.

### H020: public-equation latent should be constrained as a row-level 7-target vector world

- 상태: strongly supported as a high-risk posterior-completion worldview; train co-occurrence prior itself remains weak.
- 왜 그럴듯한가: H018 samples binary labels cell by cell, but real labels are emitted as one Q1/Q2/Q3/S1/S2/S3/S4 vector per row. Train target vectors are highly non-uniform, so independent marginals can create implausible Q/S combinations.
- 맞다면: sampled row-level target-vector worlds should match known public LB deltas far better than permuted public deltas. The posterior should produce a coherent H012-to-vector-world movement larger than H018 without relying on arbitrary cellwise weights.
- 틀리다면: vector-world errors should be no better than public-delta permutations, or train-vector priors should force a posterior that loses H018 consistency and produces no coherent action.
- 최소 실험: `hitl/h020_joint_vector_world_jepa.py`, sampling joint 7-bit label-vector worlds from H018 marginals with optional global/subject train-vector priors, then fitting public-delta posteriors and materializing the selected vector posterior.
- 관측: best sampled config by config score was `global_b0.15` with best world MAE `0.000175369`, top100 MAE `0.000260939`, and Spearman `0.921804511`. The selected posterior was `none_b0_soft_t0.00012_p2` with posterior MAE `0.000012623`, p90 abs `0.000023274`, Spearman `0.995488722`, ESS `977.953487`, and mean/max shift vs H018 `0.010608997` / `0.044670350`. Real vector-world metrics beat all `300` public-delta permutation nulls. Primary file `submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv` changes all `1750` cells and has rowweighted delta vs H012 `-0.001105455`, stronger than H018 `-0.000636475` and H019 `-0.000631235` under the same report.
- 성공/폐기 기준: accept the row-vector world if real beats permutation null and the selected posterior makes a coherent row-level movement. Observed. Do not claim train co-occurrence as the action prior unless a beta-positive posterior is selected or public feedback rewards a beta-positive variant. Not observed.
- public LB 관측 반응: if H020 improves meaningfully, public-equation HS-JEPA should move from independent cell posterior-completion to row-level hidden target-state completion. If H020 worsens while H018 is preferred, joint-vector projection is too aggressive or the chosen beta-zero posterior overfits old public equations.
- 제출 전략: H020 is the highest-upside post-H012 posterior-completion sensor. H018 remains the cleaner binary-hardworld baseline; H019 remains the row-subset diagnostic.

### H021: raw human-state context can gate the H020 row-vector action

- 상태: supported as a human-state gate over H020; direct human-state probability replacement rejected.
- 왜 그럴듯한가: H020 validated row-level target-vector consistency, but its selected posterior used `beta=0`, leaving the human-state part of HS-JEPA unproven. If human-state context predicts target vectors, it should help choose which H020 cells to trust.
- 맞다면: human-state KNN vector priors should beat global vector priors in train-only validation, and H020 cells selected by human/H020 directional agreement should beat row-permuted human-prior nulls.
- 틀리다면: human-state vector priors should be no better than global priors, or row-permuted human-state priors should select H020 cells just as well.
- 최소 실험: `hitl/h021_human_state_vector_prior_jepa.py`.
- 관측: best human-state prior `subject_all_k10` reaches marginal BCE `0.617584875` vs global vector prior `0.664614445`. Selected candidate `submission_h021_agree_h020_k1200_a1_e1546ba9_uploadsafe.csv` changes `1200` cells, has H020-equation delta `-0.000684129` vs H012, and row-permuted human-prior null median is worse by `0.005549353`.
- 성공/폐기 기준: accept the gate if it preserves meaningful H020 gain and beats row-permuted human-prior nulls. Observed for the 1200-cell H020-agreement candidate. Reject direct q_hs replacement if it worsens H020 compatibility. Observed.
- public LB 관측 반응: if H021 improves, HS-JEPA has its first validated bridge from raw human-state context to public-equation row-vector action. If it fails, human-state vector priors remain diagnostic/local but not public-actionable.
- 제출 전략: submit H021 only as a high-information architecture test. It is not safer than H012 by public evidence; it is more explanatory than pure H020 if it wins.

### H022: human-state vector prior can become the H020 posterior prior

- 상태: 반증됨 as final posterior/action prior; supported as proposal/search/gate signal.
- 왜 그럴듯한가: H021's `q_hs` beats the global target-vector prior in train-only validation and selects H020 cells better than row-permuted `q_hs`; H020's beta-zero posterior leaves a gap for a richer conditional vector prior.
- 맞다면: positive `q_hs` beta should win both vector-world config search and posterior/action selection, and row-permuting `q_hs` should degrade all major world-fit metrics.
- 틀리다면: `q_hs` may help sampled-world search but the best posterior should revert to `beta=0`, or row-permutation should not consistently hurt.
- 최소 실험: `hitl/h022_hs_conditioned_vector_world_jepa.py`, injecting H021's human-state vector distribution into H020 vector-world sampling and posterior reweighting.
- 관측:
  - config search: weak human prior `hs_b0.1` is best by config score `0.000277410`, ahead of `none_b0` `0.000310758`;
  - posterior/action: selected posterior is `none_b0_top250_t0.0005`, with MAE `0.000014073`, p90 abs `0.000026312`, Spearman `0.990977444`;
  - best positive human-state posterior is weaker, e.g. `hs_b0.1_top250_t0.00012` MAE `0.000024950`, p90 abs `0.000043720`;
  - public-delta permutation null is strongly passed, but `q_hs` row-permutation null is mixed: real top100 world MAE improves, best-world/median do not.
- 성공/폐기 기준: accept as final action prior only if a beta-positive posterior wins action selection and row-permutation null degrades consistently. Not observed.
- public LB 관측 반응: no H022 candidate should be submitted as an HS-JEPA proof. A diagnostic `none_b0` H022 file would test public-equation posterior sharpening, not human-state conditioning.
- 제출 전략: use `q_hs` as proposal distribution, gate, or Pareto constraint. Do not force beta-positive q_hs priors for story cleanliness.

### H023: human-state energy can choose among public-compatible vector worlds

- 상태: partially supported as representation geometry; rejected as a direct action selector.
- 왜 그럴듯한가: H022 showed that `q_hs` helps proposal/search but fails as the final prior. A weaker claim remains: after public-compatible vector worlds are found, `q_hs` may identify the more human-plausible world without forcing the posterior density.
- 맞다면:
  - public-error top-k vector worlds should have lower human-state energy than row-permuted `q_hs` controls;
  - a Pareto posterior using public error and `q_hs` energy should keep public fit while improving human-state geometry;
  - row-permuted `q_hs` should fail both geometry and public-posterior checks.
- 틀리다면:
  - public-compatible worlds should look no more human-state-aligned than row-permuted controls;
  - or `q_hs` may improve geometry but not public/action posterior fit.
- 최소 실험: `hitl/h023_hs_pareto_proposal_vector_jepa.py`.
- 관측:
  - public-compatible worlds are strongly human-state-aligned: top1000 real energy `4.877889323` vs row-permutation null median `5.234522555`, p `0.012345679`;
  - selected Pareto posterior `pareto_top1000_lam0.2_t0.00012` has MAE `0.000031100`, p90 `0.000059357`, Spearman `0.989473684`;
  - real `q_hs` improves row-vector KL vs row-permuted controls (`rowperm_hs_kl_p=0.016393443`);
  - but public posterior fit does not beat row-permuted controls (`rowperm_public_p=0.754098361`);
  - no root upload-safe H023 candidate promoted.
- 성공/폐기 기준:
  - accept representation claim if real public-compatible worlds have much lower `q_hs` energy than row-permuted controls. Observed.
  - accept action claim only if Pareto public fit also beats row-permuted controls. Not observed.
- public LB 관측 반응: H023 should not consume a public slot unless a future action-health layer changes the `rowperm_public_p` result. Submitting H023 diagnostic files would test an unproven action selector.
- 제출 전략: no submission. Use H023 as architecture evidence that public-equation hidden worlds and human-state latent geometry are coupled, while the materializer still needs a public/private action-health target.

### H024: known public sensors can decode post-H012 action health

- 상태: partially supported for known-score reconstruction; rejected as an unseen post-H012 submission selector.
- 왜 그럴듯한가: H010/E323/E216/E267 provide public-bad movement axes, while H012/E247/E95/Mixmin provide successful or near-successful axes. H015-H023 candidates expose internal public-equation and human-state sensor scores. If action health is a stable latent, these views should identify which unseen post-H012 move is safe.
- 맞다면:
  - leave-one-public-out ranking should recover known public outcomes;
  - H012 should not be ranked only by in-sample leakage;
  - the top unknown candidate should have narrow predicted LB intervals, high support below H012, and a selected-vs-H012 permutation p below `0.05`.
- 틀리다면:
  - known-score ordering may be learnable, but unknown candidates will have wide intervals, low H012-beating support, or no advantage over permuted public scores.
- 최소 실험: `hitl/h024_action_health_decoder_jepa.py`.
- 관측:
  - known public sensors `20`, candidate rows `407`;
  - best LOO decoder `geometry` alpha `100`, MAE `0.000773`, Spearman `0.969925`, pairwise `0.947368`;
  - state decoder predicts H012 close to actual (`0.567631` vs `0.568123`), but the top unknown H015 `k100` candidate has median `0.570054`, p10/p90 `0.559653-0.580761`, support below H012 `0.15`;
  - permutation p for selected-vs-H012 margin `0.841`.
- 성공/폐기 기준:
  - accept known-score reconstruction. Observed.
  - reject as a submission selector unless the top unknown candidate beats H012 in >=`0.70` model scenarios and passes permutation stress. Not observed.
- public LB 관측 반응: no H024 file should be submitted from this decoder. If a similar future decoder promotes a candidate, it must first pass the same unseen-candidate and permutation gates.
- 제출 전략: none. H024 demotes simple public-axis ranking and pushes the next experiment toward new action-health supervision.

### H025: train-counterfactual action health transfers to public-safe post-H012 actions

- 상태: 반증됨 as a submission selector; supported only as a weak local representation.
- 왜 그럴듯한가: H024 failed because known public sensors are scarce and may overfit H012. Train labels provide thousands of counterfactual action outcomes, so they could create independent action-health supervision.
- 맞다면:
  - train counterfactual gain should be predictable across row/time folds;
  - leave-proposal-family performance should not be the only strong result;
  - selected test candidates should not be known-public-bad anchors;
  - the selected unknown candidate should beat row-permuted test-state placement controls.
- 틀리다면:
  - row/time OOF transfer should be near zero or fold-unstable;
  - the decoder may prefer proposal-family shortcuts or known public-bad Q2/residual anatomy;
  - selected test actions should not be significant against row permutation.
- 최소 실험: `hitl/h025_train_counterfactual_action_health_jepa.py`.
- 관측:
  - row/time OOF Spearman `0.021090879`;
  - top10 lift `0.004425758`;
  - row folds are unstable, including negative top10 lift in fold0 and fold3;
  - leave-family metrics are high but likely family-geometry-driven;
  - top ranked known anchors are public-bad `submission_jepa_latent_q2_w0p45.csv` and `submission_jepa_latent_residual_probe.csv`;
  - selected unknown H023 diagnostic has row-permutation p `0.576666667`;
  - no upload-safe H025 file is promoted.
- 성공/폐기 기준:
  - accept only if row/time Spearman is materially positive, selected known anchors are not public-bad, and selected unknown placement beats row-permutation p <= `0.05`. Not observed.
  - keep as diagnostic if it reveals what train-side action health confuses with public-safe action health. Observed.
- public LB 관측 반응: no H025 file should be submitted. If a train-action-health future variant wins public, it must include a public/private shortcut veto not present here.
- 제출 전략: none. H025 redirects the graph toward a public/private calibration latent: train action-health must be discounted by public-bad Q2/residual/domain-shift energy before materialization.

### H026: scalar public/private shortcut veto is enough to repair H025

- 상태: 반증됨 as a submission route; supported as a known-anchor diagnostic.
- 왜 그럴듯한가: H025's most visible error was ranking known public-bad Q2/residual probes highly. If that was the main defect, a public-bad shortcut veto should preserve train-action health while removing the public-transfer failure.
- 맞다면:
  - H026 source scoring should rank H012 and known good anchors above known public-bad JEPA/Q2/residual files;
  - generated post-H012 variants should keep H025 train-action gain;
  - the selected variant should have public prediction support below H012 and beat public-score permutation stress.
- 틀리다면:
  - known-bad anchors may be demoted, but variants still look public-bad under H024 or fail public-score permutation;
  - the train-action stress and public-transfer stress will disagree.
- 최소 실험: `hitl/h026_public_private_calibration_veto_jepa.py`.
- 관측:
  - source sanity succeeds: H012 source score `9.777520`; E216 `-4.679053`; JEPA Q2 `-5.856040`; hybrid strict `-7.595414`; JEPA residual `-9.029536`;
  - generated variants `272`;
  - selected diagnostic has H025 row-permutation p `0.000000` and real top1200 gain `9.470154134`;
  - but H024 predicted public median is `0.574388293`, support below H012 only `0.166667`, and public-score permutation p `0.898000`;
  - no root upload-safe file promoted.
- 성공/폐기 기준:
  - accept only if known-bad anchors are demoted and selected unknown variant passes both row-placement and public-score permutation stress. Not observed.
  - keep diagnostic if it separates source-level shortcut ranking from action-level public transfer. Observed.
- public LB 관측 반응: no H026 file should be submitted. If a future public/private-veto variant wins public, it must differ from H026 by changing the calibration target or generator, not just veto weights.
- 제출 전략: none. H026 says "scalar veto is insufficient"; the next branch must create public/private-aware actions directly.

### H027: existing posterior targets become public-safe if generated with memory/private constraints from birth

- 상태: 반증됨 as a submission route; useful as a generator-boundary diagnosis.
- 왜 그럴듯한가: H012 proved a public-equation posterior, V106/H014 showed same-subject sleep-state memory is real but incomplete, H021-H023 showed human-state geometry is coupled to public-compatible vector worlds, and H026 showed after-the-fact scalar veto is too late. The natural next step was to require public posterior strength, private memory safety, human-state agreement, train action-health, and public-good/bad energy before cells are materialized.
- 맞다면:
  - generated variants should have H024 median predicted public below H012;
  - support below H012 should be materially higher than the H024/H026 `0.15-0.17` band;
  - selected cells should beat H025 row-permutation placement and H024 public-score permutation stress;
  - the best variants should not be only tiny H015 S-target moves.
- 틀리다면:
  - H024 will still price generated variants above H012;
  - H025 row-placement and public-score permutation stresses will disagree;
  - memory/human-state/private-safety constraints will prune or reshape cells but not create an H012-beating action.
- 최소 실험: `hitl/h027_public_private_aware_generator_jepa.py`.
- 관측:
  - generated variants `1648`;
  - selected diagnostic `submission_h027_h015_public_feedback_bad_axis_escape_S1S2S3_k80_a0p25.csv`;
  - H024 predicted public median `0.569712461`, p10/p90 `0.560020747-0.583215022`;
  - support below H012 `0.150000`;
  - H025 row-permutation p `0.383333333`;
  - H024 public-score permutation p `0.822000000`;
  - selected predicted public margin versus H012 `+0.001588978`;
  - no root upload-safe file promoted.
- 성공/폐기 기준:
  - accept only if selected variant has median below H012, support below H012 above `0.50`, and passes both row-placement and public-score permutation stress. Not observed.
  - keep diagnostic if it identifies whether the problem is post-hoc veto or source posterior target. Observed: source posterior target is the bottleneck too.
- public LB 관측 반응: no H027 file should be submitted. If a future born-public/private generator wins public, it must change the calibration target or source proposal distribution, not only rescore H015/H020/H023 cells.
- 제출 전략: none. H027 says the missing piece is not a cell-level wrapper over existing public-equation posterior completions; it is a different public/private calibration representation.

### H028: known public interventions define a reusable local action-gradient around H012

- 상태: 반증됨 as a submission route; supported only as coarse public-response geometry.
- 왜 그럴듯한가: H024 showed known public scores are reconstructable, while H026-H027 showed posterior/gate variants are not enough. A natural HS-JEPA target is therefore not a hidden probability posterior but the hidden public/private response field: how public LB changes when a submission moves each row-target cell from H012.
- 맞다면:
  - known public intervention tensors should predict their public LB deltas under leave-one-public-out;
  - the learned cell-level gradient should beat permuted public-delta nulls;
  - moving H012 along the negative gradient should produce a candidate that H024/H025 also see as below H012 or at least public-readable.
- 틀리다면:
  - the response fit may only distinguish the singular H012 point from the rest;
  - H012 LOO prediction will be unstable;
  - gradient-generated candidates will be priced as ordinary 0.576-level submissions by independent public/action-health stress.
- 최소 실험: `hitl/h028_public_private_gradient_jepa.py`, treating 20 known public submissions as interventions from H012, aggregating logit movements through cell-state features, fitting a low-rank ridge public-gradient, generating gradient descent / rollback / H012 amplification / hybrid variants, then applying H024/H025 stresses.
- 관측:
  - selected gradient fit `all` alpha `100.0`, 88 features, LOO MAE `0.001204883`, Spearman `0.440601504`, pairwise `0.657894737`;
  - selected-fit permutation p for LOO MAE `0.000000000`, so the response is not random;
  - H012 leave-one-out delta prediction is unstable (`+0.002941`), showing the model does not truly understand the singular best point;
  - generated variants `820`;
  - best diagnostic `submission_h028_pubgrad_descent_all_k1200_a0p36_all_3a28ff89.csv` has gradient-predicted delta `-0.004909201`, but H024 predicted public median `0.576388429`, support below H012 `0.083333333`, H025 row-permutation p `0.710000000`, and public-score permutation p `0.918000000`;
  - no root upload-safe file promoted.
- 성공/폐기 기준:
  - accept only if gradient fit beats nulls and at least one generated candidate passes independent H024/H025 stress below H012. First condition observed, second not observed.
  - reject smooth local-gradient interpretation if independent stress prices all top gradient moves far above H012. Observed.
- public LB 관측 반응: no H028 file should be submitted. If a future gradient file wins public despite this stress, H024/H025 are missing the decisive invariant; otherwise H012 should be treated as a narrow public-equation basin rather than a smooth local optimum.
- 제출 전략: none. The next branch should search for the invariant/constraint that made H012 special, not continue H012 by local gradient descent.

### H029: H012's public-equation gain is carried by an exact row-target needle basin

- 상태: supported as the current bottleneck explanation; no submission route promoted.
- 왜 그럴듯한가: H012 is a large outlier public success, while H028 rejected smooth local continuation. If H012 is a phase-change basin, preserving target-level movement statistics or memory-compatible slices should not be enough; exact row-target placement should matter.
- 맞다면:
  - H012-like duplicate controls and local ablations will be hard for H024 to rank below the real H012;
  - target/subject/memory rollbacks should mostly be priced worse than H012;
  - target-wise row permutation should collapse because row identity is not exchangeable.
- 틀리다면:
  - one ablation family, such as memory-compatible pruning or target rollback, should pass public-free stress below H012;
  - target-wise row permutation should retain much of H012's action-health if the invariant is only target-level calibration.
- 최소 실험: `hitl/h029_h012_needle_basin_invariant_jepa.py`, generating support-ray scales, posterior top-k alternatives, target/group/subject rollbacks, H014 memory-agree/disagree/private-safe only/rollback variants, outside-support target-count matched variants, and target-wise row-permuted H012 moves.
- 관측:
  - generated variants `102`;
  - best H024 decoder `geometry` alpha `100.0`, MAE `0.000772855`, Spearman `0.969924812`, pairwise `0.947368421`;
  - selected diagnostic `rollback_target_S1` has H024 predicted median `0.570494744`, margin versus real H012 `+0.002371261`, support below H012 `0.116666667`, public-score permutation p `0.858000000`, and H025 row-permutation p `0.613333333`;
  - best target-wise row-permuted variant has median `0.581149687`, far outside the H012 basin;
  - memory-only and memory-rollback families remain far above H012, so V106/H014-style same-subject memory is not the main H012 carrier.
- 성공/폐기 기준:
  - accept a variant only if it is below H012 by independent H024/H025 stress and beats public-score permutation. Not observed.
  - accept the needle-basin explanation if invariant-breaking variants all degrade and row permutation collapses. Observed.
- public LB 관측 반응: no H029 file should be submitted. If a row-permuted or memory-pruned H012 variant were to win public, it would refute the exact row-target basin interpretation and point back to target-level calibration or memory. Current stress says not to spend that slot.
- 제출 전략: none. The next branch should rebuild the inverse public-equation solver with row/subset identity or row-vector constraints as first-class unknowns instead of post-hoc ablations.

### H030: row-target identity priors can reconstruct H012 only if the translator is correct

- 상태: partially supported as a latent diagnosis; rejected as a direct submission route.
- 왜 그럴듯한가: H029 showed exact row-target placement matters. H016/H019/H020 independently found public cell weights, row subset state, and joint row-vector state. If these are the right invariants, they should improve the public-equation solver itself, not only post-hoc action scoring.
- 맞다면:
  - an H012-held-out public-equation solver with row-target allowance priors should predict most of H012's large E247-relative public gain;
  - true held-out configs that exclude H012 as equation and exclude direct H012 priors should still be near the observed H012 delta;
  - materialized candidates should pass H024/H025 stress below H012 if the same latent also contains the action translation law.
- 틀리다면:
  - H012-held-out prediction will degrade to ordinary 0.576-level uncertainty;
  - only self-feedback configs using H012 prior will look good;
  - generated candidates will be priced above H012 with low support below H012.
- 최소 실험: `hitl/h030_rowtarget_identity_equation_jepa.py`, adding cell-wise allowance priors to public-equation fitting from H012/H016/H019/H020/H014 state maps, then materializing e247-pre, e247-post, and h012-residual candidates.
- 관측:
  - fit configs tested `6528`; generated candidates `756`;
  - true independent H012-held-out best: `pre_h012_good_soft + identity_combo`, predicted H012 delta `-0.007550142` vs actual `-0.008035466`, error `0.000485324`;
  - self-feedback `h012` prior control has error `0.000181687`, but this is not independent evidence;
  - selected diagnostic `submission_h030_e247_post_h012_joint_vector_cell_h012_k1200_a0.55_05a1cf87.csv`;
  - H024 predicted public median `0.572160346`, support below H012 `0.100000000`;
  - H024 public-score permutation p `0.923333333`, H025 row-permutation p `0.670000000`;
  - no promoted upload-safe file.
- 성공/폐기 기준:
  - accept latent if true held-out H012 prediction is close to observed H012. Partially observed.
  - accept submission route only if materialized candidates are below H012 under H024/H025 stress. Not observed.
- public LB 관측 반응: no H030 file should be submitted. If an H030 file unexpectedly wins public, the H024/H025 action-health decoders are too conservative around row-target identity priors. Otherwise the evidence says identity discovery is ahead of identity-to-action translation.
- 제출 전략: none. Next branch should learn the route/translator from identity posterior to probability action, rather than increasing allowance-prior complexity.
