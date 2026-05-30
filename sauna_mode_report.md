# Sauna Mode Report

## 내가 발견한 가장 이상한 점

현재 frontier `submission_e95_hardtail_541e3973.csv`의 public LB `0.5762913298`은 broad model improvement처럼 보이지 않는다. E72는 넓게 움직였고 public에서 죽었지만, E95는 훨씬 target-pruned하게 움직이고 아주 작게 살아남았다.

## 그 이상함을 설명하는 현재 최강 세계관

이 대회의 현재 병목은 모델 capacity가 아니라 hidden block/state 신호를 row-level probability로 번역할 때 생기는 target-axis hard-tail calibration 실패다.

압축 문장:

> 0.576대 plateau는 숨은 구조가 없어서가 아니라, broad latent/structure movement가 Q/Q3/S4와 hard-label tail을 함께 건드리면서 LogLoss를 잃기 때문에 생긴다.

## 그 세계관이 맞다면 관측되어야 할 것

- public-positive E95는 broad movement가 아니라 target-axis surgery여야 한다.
- public-negative E72는 Q/Q3/S4 contamination 또는 낮은 E95-direction alignment를 보여야 한다.
- E101은 full E89보다 더 작은 kill-test여야 한다. 즉 E95의 남은 Q2/S3/S3-heavy ambiguity만 건드려야 한다.
- E101이 tie/loss이면 E108/E104/E106뿐 아니라 full E89/non-active graft 자동 fallback도 닫혀야 한다.

## 그 세계관을 죽일 수 있는 가장 작은 실험

`analysis_outputs/e111_sauna_frontier_movement_atlas.py`

submission geometry만 사용해 mixmin/E72/E85/E86/E89/E90/E95/E101/E108의 active cells, target-axis share, E95-confident movement share, E95-direction cosine을 비교했다.

## 실험 결과

- E72 vs mixmin: public delta `+0.0001011367`, active cells `893`, L1 `2.203482`, Q-share `0.450788`, S-share `0.549212`, cosine with E95 direction `0.327033`.
- E95 vs mixmin: public delta `-0.0000153107`, active cells `550`, L1 `1.509562`, Q-share `0.019948`, S-share `0.980052`.
- E101 vs E95: active cells `50`, active rows `48`, Q2/S3 share `1.0`, S-target share `0.905306`.
- E89 vs E95: active cells `158`, L1 `0.107468`, Q2/S3 share `0.299376`.

## 생각이 어떻게 바뀌었는지

E95를 단순 hardtail fallback으로만 보던 해석을 더 좁혔다. 지금 더 정확한 해석은 target-axis surgery다. E95는 실패한 E72류 movement에서 Q/Q3/S4 broad contamination을 거의 제거하고 S1/S2/S3 중심으로 남긴다.

## 추가 관찰: 왜 S축인가

`analysis_outputs/e112_sauna_qs_temporal_axis_audit.py`로 train label/order만 봤다.

- S-target subject-LOO logloss gain: `0.068724`, Q-target `0.020146`.
- strongest subject-prior targets: `S3`, `S2`, `S1`, 전부 E95-active.
- Q-target temporal persistence lift: `0.135700`, S-target `0.087255`.
- 하지만 test rows가 양쪽 train row로 3일 내 bracket되는 비율은 `0.080000`뿐이다.
- pairwise corr는 within-S `0.260803`, within-Q `0.187934`, Q-S `0.030038`.

따라서 E95가 S-heavy인 이유는 S축이 subject/block state를 더 잘 담기 때문으로 보인다. Q축도 temporal signal은 강하지만, test에 직접 전파할 train adjacency가 부족해서 broad Q/Q3 movement는 위험하다.

## 추가 관찰: raw context는 Q temporal state를 구하지 못함

`analysis_outputs/e113_sauna_raw_context_visibility_audit.py`로 visible raw lifelog context가 sparse Q temporal labels를 대체할 수 있는지 봤다.

- raw daily feature count: `114`.
- train/test raw coverage: `1.000000` / `1.000000`.
- temporal holdout에서 raw+subject-prior는 subject prior보다 Q targets `+0.038804`, S targets `+0.058534` 나빠졌다.
- random split에서도 평균적으로 Q `+0.007833`, S `+0.016497` 나빠졌다.
- 유일한 temporal gain은 S3 `-0.004643`뿐이다.
- Q2의 random-only 개선과 temporal degradation은 shortcut/collapse 경고다.

이 결과는 raw context rescue를 약화한다. Q temporal signal은 존재하지만 현재 보이는 raw coverage/head로는 submission-safe calibration으로 번역되지 않는다. S3만 약하게 살아남는 점은 오히려 E95의 S-subject-state 세계관과 맞는다.

## 추가 관찰: raw context는 E101도 미리 지지하지 못함

`analysis_outputs/e114_e101_raw_context_support_audit.py`로 E101의 `50` active cells만 봤다.

- subject prior 기준 E101 beat probability: `0.336655`.
- raw+prior 기준 E101 beat probability: `0.238325`.
- validation-gated raw 기준: `0.230710`.
- S3는 flip benefit의 `0.935862`를 차지하지만, raw S3 support probability는 `0.589463`으로 subject prior `0.604450`보다 낮다.

즉 raw context는 broad Q temporal rescue도 아니고, E101 active-cell label world를 미리 확인해주는 센서도 아니다. E101이 이기면 raw context가 보지 못한 public/local S3 hard-label world가 있었다는 뜻이고, 지면 raw context도 이미 그 방향을 약하게 반대한 셈이다.

## 추가 관찰: 그래도 E101이 다음 센서인 이유

`analysis_outputs/e115_public_sensor_information_audit.py`로 E101/E89/E85/E90/E86를 public sensor로 비교했다.

- E95-conditioned broad-plausible worlds: `3452`.
- E101 actionable information score: `1.613953`.
- E101 outcome entropy: `1.728493`.
- E101 beat-E95 rate: `0.983488`.
- E101 win/tie/loss: `0.911645` / `0.088355` / `0.000000`.
- E89 actionable information score: `0.233881`, beat-E95 `0.195829`, loss `0.580243`.
- E85/E90/E86 actionable scores: `0.025735`, `0.011719`, `0.002573`.

이 결과는 E101을 "raw가 지지하는 파일"로 되살리지 않는다. 대신 더 정확하게 만든다. E101은 현재 남은 세계관을 가장 많이 가르는 public sensor다. E89는 diffuse-tail 질문으로는 살아 있지만 다음 slot에서 E101보다 정보량이 낮고, E85/E90/E86는 대부분 "얼마나 지는가"를 묻는 파일에 가깝다.

## 추가 관찰: E101 점수 해석은 미리 고정해야 함

`analysis_outputs/e116_e101_public_feedback_decoder.py`로 E101 public LB band를 고정했다.

- strong win: `<= 0.576261330`.
- edge win: `(0.576261330, 0.576280330]`.
- small win: `(0.576280330, 0.576288330]`.
- tie: `(0.576288330, 0.576294330]`.
- loss: `> 0.576294330`.

이 decoder의 목적은 점수 예측이 아니다. E101 결과를 본 뒤 같은 결과를 입맛대로 해석하지 못하게 하는 장치다. win이면 E108 계열을 exact-delta rerun 뒤 고려할 수 있고, tie/loss면 같은 rollback line을 더 키우지 않는다.

## 추가 관찰: E95 같은 후보는 우주에 많지 않음

`analysis_outputs/e117_e95_like_neighborhood_audit.py`로 문서와 report에 이미 등장한 submission들을 다시 봤다.

- referenced names: `5277`.
- resolved files: `4477`.
- unique prediction tensors: `4031`.
- E95-like neighborhood count: `10`.
- E95보다 E72-adverse exposure가 낮거나 같은 E95-like 후보: `4`.
- 그 `4`개는 E101, E85, 그리고 E101-win 이후에만 의미가 있는 E108 두 파일이다.
- E101은 mixmin 기준 독립 후보라기보다 E95 기준 `50` cells, L1 `0.079624`, Q2/S3 share `1.000000`인 micro edit다.

이 결과는 "기존 submission 우주를 더 잘 뒤지면 E95보다 자연스럽게 좋은 후보가 있을 것"이라는 생각을 약화한다. E95 주변은 넓은 평야가 아니라 좁은 능선에 가깝다. 따라서 E101 결과 없이 E108을 앞당기거나, E89/E85/E90/E86를 자동 승격하는 건 여전히 근거가 약하다.

## 추가 관찰: E101은 완전한 blind sensor는 아니지만 flank가 인증하지도 않음

`analysis_outputs/e118_e101_flank_label_support_audit.py`로 E101의 `50` active cells를 visible train-label flanks 관점에서 다시 봤다.

- best flank prior `edge_endpoint_beta` beat-E95 probability: `0.437780`.
- subject prior beat-E95 probability: `0.337185`.
- global prior beat-E95 probability: `0.015920`.
- best flank prior expected delta/all cells: `+0.000003014`.
- active edge/near-edge rate: `0.620000` vs null `0.471289`, p `0.016999`.
- flank conflict rate: `0.240000` vs null `0.149933`, p `0.048998`.

이건 E101을 단순 public-only blind sensor로 보는 해석을 약화한다. active cells에는 실제 edge/flank transition-state 냄새가 있다. 하지만 expected delta가 아직 positive라서 로컬 인증은 아니다. 결론은 더 좁다. E101은 보이는 구조가 약하게 지지하는 transition-state sensor지만, public feedback 없이 E108이나 higher-alpha를 먼저 열 만큼 강하지 않다.

## 추가 관찰: flank support는 E101 대체 gate가 아님

`analysis_outputs/e119_e101_flank_gate_variant_stress.py`로 E118의 flank support를 실제 pre-feedback candidate gate로 바꿔봤다.

- variants: `602`.
- E101-pass rows: `66`.
- E101-dominating rows: `0`.
- materialized submission: `none`.
- active-all scale `1.50`은 broad mean을 E101보다 좋게 만들었지만 beat-rate를 `0.983488`에서 `0.980881`로 낮췄다.
- active-all scale `2.00`은 mean을 `-0.000029942`까지 낮췄지만 E101-pass를 잃고 beat-rate도 `0.977984`로 낮아졌다.

이 결과는 더 정확하다. flank signal은 E101 active cells가 random이 아니라 transition-state 쪽이라는 해석을 강화한다. 하지만 visible flank로 subset을 자르면 E101의 scenario support가 먼저 죽는다. 따라서 E119는 "E101을 더 작게 잘라 제출하자"는 shortcut을 닫는다.

## 추가 관찰: E101 public feedback은 small loss였다

`analysis_outputs/e120_post_e101_public_observation_audit.py`로 실제 E101 public LB를 E116 decoder에 넣었다.

- E101 public LB: `0.5763003660`.
- E95 대비 delta: `+0.0000090362`.
- mixmin 대비 delta: `-0.0000062745`.
- E116 outcome: `small_loss`.
- E95가 mixmin에서 얻은 gain 중 `59.02%`를 E101이 되돌려 놓았고, `40.98%`는 보존했다.
- local E101 stress mean/p95/beat는 `-0.0000162053` / `-0.000001564` / `0.983488`였지만, 실제 public은 local mean보다 `+0.0000252415`, local p95보다 `+0.0000106001` 나빴다.

이건 E101을 무의미한 파일로 만드는 결과가 아니다. E101은 mixmin보다 아직 좋다. 하지만 E95 frontier를 이길 만큼의 Q2/S3/S3-heavy support는 public에 없었다. 따라서 E95의 target-axis hard-tail surgery가 현재 standing law이고, E99/E101 local stress는 loss-side public tail을 과소평가했다.

## 추가 관찰: E101 small loss는 한두 개 고영향 S3 셀 규모의 경계다

`analysis_outputs/e121_e101_small_loss_inverse_posterior.py`로 E101 public delta를 active-cell hard-label budget으로 역변환했다.

- all-support E101-vs-E95 delta: `-0.0000966787`.
- all-adverse E101-vs-E95 delta: `+0.0002116767`.
- 실제 E101-vs-E95 delta `+0.0000090362`는 active flip benefit의 `0.657165`가 support로 실현된 세계에 해당한다.
- greedy top-flip support 기준 mixmin을 처음 이기는 지점은 `21`, 실제 관측에 가장 가까운 지점은 `22`, E95를 처음 이기는 지점은 `23`이다.
- exact-observed worlds는 local/flank prior에서 약 `4.4-4.7%`로 충분히 흔하지만, global prior에서는 `0.8%` 수준이다.

이 결과는 E101 방향이 완전히 틀렸다는 뜻이 아니다. E101은 E95를 이기기 직전까지 왔지만, public에서 고영향 S3 support가 대략 한 셀 부족했다. 그래서 병목은 "Q2/S3 rollback alpha를 더 미세하게 조절하자"가 아니라 "그 한두 개의 고영향 S3 support/adverse 셀을 public 없이 식별할 센서가 있는가"다.

## 추가 관찰: simple prior는 small loss를 설명하지만 제출 gate는 아니다

`analysis_outputs/e122_e101_independent_sensor_boundary_audit.py`로 E121의 열린 질문을 찔렀다.

- 실제 E101-vs-E95 public delta: `+0.0000090362`.
- `raw_full_subject_prior_y1` expected delta: `+0.000008889`.
- `flank_conflict_flat` expected delta: `+0.000009521`.
- `flank_both_distance_beta` expected delta: `+0.000009532`.
- E119 local-transfer active-all expected delta: `-0.000016205`.
- rank 22 S3 cell support probability: subject `0.104167`, edge `0.069444`, raw+prior `0.145957`, posterior `0.125880`.
- rank 23 S3 cell support probability: subject `0.958333`, edge `0.972222`, raw+prior `0.864418`, posterior `0.940119`.

이건 중요한 분리다. E101의 small loss는 완전히 예측 불가능한 일이 아니었다. 단순한 subject/flank/raw prior가 E119 local-transfer보다 훨씬 잘 맞췄다. 하지만 그건 제출 가능한 gate가 아니다. E95를 처음 이기게 만드는 rank 23 셀은 visible prior와 posterior 모두에서 여전히 support처럼 보인다.

따라서 E122의 결론은 "E101 실패는 설명된다"이지 "다음 E101 변형을 제출하자"가 아니다. 현재 같은 line은 닫힌 상태다.

## 추가 관찰: Q/S transition motif도 그 missing sensor가 아니다

`analysis_outputs/e123_e101_transition_motif_s3_sensor.py`로 마지막으로 싸고 날카로운 S3 셀 센서를 찔렀다.

- no-S3 transition motif는 이전/다음 Q1/Q2/Q3/S1/S2/S4 상태만 보고 S3를 예측한다.
- temporal-tail validation에서 subject prior 대비 logloss가 `+0.135183` 나빠졌다.
- full motif는 `+0.246239`, motif+subject는 `+0.349065`로 더 나빴다.
- rank 23 S3 cell support probability는 no-S3 motif `0.943564`, full motif `0.956191`, motif+subject `0.984326`이다.
- motif 계열 aggregate expected delta는 `+0.000027684`~`+0.000028398`로 실제 E101 small-loss `+0.0000090362`보다 훨씬 loss-heavy하게 overshoot한다.

이 결과는 rank 22를 그럴듯하게 adverse로 보는 착시를 만들지만, 핵심 rank 23을 해결하지 못하고 validation도 무너진다. 따라서 이건 JEPA-style context-target representation이 아니라 LeJEPA-style collapse/shortcut 경고에 가깝다.

## 추가 관찰: E99 transfer world는 E101을 held-out으로 맞추지 못했다

`analysis_outputs/e124_e101_conditioned_tail_transfer.py`로 E99의 두 항짜리 세계관을 다시 찔렀다. E99는 E72 실패와 E95 성공만 보고 `public_delta = alpha * local_delta + lambda * E72_tail_delta`를 맞춘 모델이다.

- broad-plausible worlds: `3452`.
- broad mean predicted E101 delta: `-0.000031516`.
- actual E101 delta vs mixmin: `-0.000006275`.
- E101 order-match worlds: `57`.
- E101 sensor-plausible worlds: `57`.
- 그 안에서 E95 live win rate: `0.929825`.
- 미래 후보 beat-E95: E89 `0.052632`, E85 `0.017544`, E90/E86 `0`.

이 결과는 E99를 완전히 버리라는 뜻은 아니다. E99는 E72/E95 hard-tail axis를 설명했다. 하지만 E101이라는 held-out public sensor를 통과하지 못했으므로, E99 broad order를 그대로 다음 제출 순서로 쓰면 안 된다. 현재 더 정확한 말은 이거다: hard-tail law는 real이고, Q2/S3 boundary variable은 아직 missing이다.

## 추가 관찰: E101-compatible 세계는 q2s3 세계가 아니다

`analysis_outputs/e125_e101_survivor_anatomy.py`로 E124에서 살아남은 57개 세계를 해부했다.

- E101-plausible worlds: `57/3452`.
- `all` 또는 `e72_top50_hard`: `43/57`.
- `q2s3`: `0/368`.
- deterministic 또는 `gamma=0`: `40/57`.
- median alpha: `3.310470 -> 0.791985`.
- median `tail_e101 - tail_e95`: `-0.000012634 -> ~0`.

이건 E100의 q2s3 diffuse-tail residual story를 거의 닫는다. E101을 맞춘 세계는 Q2/S3 cell을 더 잘 고른 세계가 아니라, E101의 local rollback margin을 강하게 압축하고 E101/E95 tail 차이를 거의 없애는 세계다.

## 다음으로 가장 정보량이 큰 행동

E95/E101을 동시에 만족하는 post-E101 public-world rebuild는 E121-E122로 1차 완료됐다.

이제 가장 정보량이 큰 행동은 같은 Q2/S3 rollback line을 더 키우는 것이 아니다. E101 결과는 E108/E104 higher-alpha, E106 subject-prior masks, E119 flank-gated variants, full E89, non-active graft automatic fallback, E121/E122 posterior-fitted gates, E123 transition-motif gates, pre-E101 E99-ranked successors, E100 q2s3 diffuse-tail successor를 닫는다. 다음 실험은 정말 다른 종류의 고영향 S3 셀 센서가 떠오르지 않는 한, 같은 line을 떠나 다른 hidden structure를 찌르는 것이다.

## 제출 후보

현재 즉시 제출할 same-family 후보는 없다.

Resolved sensor: `analysis_outputs/submission_e101_q2s3tail_177569bc.csv`

의도: E95의 target-axis hard-tail surgery가 Q2/S3/S3-heavy cells에서 너무 tight한지 검증했다.

결과: public `0.5763003660`, E95보다 `+0.0000090362` 나쁘고 mixmin보다 `-0.0000062745` 좋다.

실패 시 해석이 실제로 발생했다: E95의 현재 axis/tail surgery가 standing law다. 다음 제출은 이 small-loss boundary를 새로 설명하는 후보여야 하며, E108/E104/E106/E119 또는 E89/non-active graft를 자동으로 제출하지 않는다.

E121-E125 이후 추가 해석: E101은 support budget의 약 `65.7%`를 맞췄고 simple priors는 이 small-loss branch를 거의 정확히 설명한다. 하지만 E95를 이기는 데 필요한 greedy rank-23 S3 cell을 public 없이 adverse로 식별하지 못한다. Cross-target transition motif도 실패했고, E99 broad transfer world도 E101 held-out check를 통과하지 못했으며, q2s3 survivor story도 `0/368`로 죽었다. 따라서 지금 당장 제출할 same-family 파일은 없다.

## 추가 관찰: E101-compatible cell budget은 E101-active cells가 아니다

`analysis_outputs/e126_e101_survivor_cell_budget_anatomy.py`로 E124/E125에서 살아남은 57개 세계를 실제 선택 셀 budget까지 펼쳤다.

- E101-plausible q2s3 mass share: `0.180513`.
- E101-plausible E101-active mass share: `0.011234`.
- broad-q2s3 E101-active mass share: `0.584840`.
- E101-plausible E95-fallback mass share: `0.356179`.
- E101-plausible between-train-runs mass share: `0.621562`.

이건 마지막 cheap loophole을 닫는다. E101을 맞춘 세계가 broad/all mask였더라도, 혹시 실제 budget은 E101이 움직인 50개 Q2/S3 셀에 몰려 있을 수 있었다. 아니었다. E101-compatible public loss surface의 98.9%는 E101이 건드리지 않은 셀에서 온다.

현재 최강 세계관은 더 압축된다.

`0.5762913298` plateau는 E95의 S-heavy hard-tail surgery가 맞았기 때문에 생긴 것이지만, 그 다음 개선은 Q2/S3 rollback amplitude를 조절해서 나오지 않는다. Public이 E101에서 본 것은 active-cell support 부족이 아니라, E101/E95 차이가 거의 무의미해지는 broad low-alpha transfer-shrinkage field다.

다음으로 가장 정보량이 큰 행동은 이 transfer-shrinkage field를 public score 없이 예측할 수 있는 구조를 찾는 것이다. 같은 E101/E89/Q2S3 line 변형은 중단한다.

## 추가 관찰: transfer-shrinkage field는 보이지만 아직 제출 gate는 아니다

`analysis_outputs/e127_transfer_shrinkage_field_predictability.py`로 E126의 cell budget teacher가 public-free 구조에서 보이는지 확인했다.

- `broad_tail_equal` proxy: cosine `0.945388`, Spearman `0.902053`, JS `0.038002`, top50 truth-mass capture `0.293969`.
- `broad_low_alpha` proxy: JS `0.103608`, top50 truth-mass capture `0.228487`.
- `broad_q2s3` proxy: JS `0.508660`, Spearman `0.108504`.
- best metadata-only heldout view `target_context_tail_e72bin`: CV JS `0.073253`, top50 truth-mass capture `0.252521`.
- target-only metadata: CV JS `0.316796`, top50 truth-mass capture `0.037897`.

이 결과는 중요하다. E126의 transfer-shrinkage 해석은 post-hoc fantasy가 아니다. E101 결과를 직접 쓰지 않는 `tail_equal`/low-alpha scenario geometry가 그 budget field를 꽤 잘 본다. 다만 metadata-only view의 top50 mass capture는 25% 수준이라, 이것만으로 새 submission을 만들면 또 selector-noise에 걸릴 가능성이 높다.

현재 다음 질문은 더 선명하다.

`tail-neutral/low-alpha density`를 JEPA-style target representation으로 만들 수 있는가? 그리고 그 representation이 E72/E101 active-cell tail risk를 다시 만들지 않으면서 selector noise보다 큰 probability movement를 만들 수 있는가?

## 추가 관찰: transfer-shrinkage energy는 제출 셀렉터가 아니라 veto다

`analysis_outputs/e128_transfer_shrinkage_energy_candidate_audit.py`로 E127의 density를 candidate-risk energy로 바꿔 known public anchors와 live files에 걸어봤다.

- `q2s3_delta95_l1`의 known-public Spearman: `0.958042`.
- `tail_equal_law_resid_ratio`: `0.888112`.
- `e72_adverse_exposure_e101_plausible`: `0.881119`.
- `e101_active_delta95_l1`: `0.874126`.
- 하지만 combined `transfer_shrinkage_risk_index`: `0.440559`.
- 이 index의 live low-risk 순서는 E85, E89, noQ2, E90, E86이다.

즉, public이 말하는 위험 성분은 잡힌다. Q2/S3 rollback, E101-active rollback, E72-adverse exposure, tail-equal law residual은 각각 의미가 있다. 하지만 이걸 하나의 숫자로 합치는 순간 post-E101 세계관과 충돌한다. E124/E126은 이미 같은 family 후보들이 E101 이후 약하다고 말했고, E128 scalar ranker는 그 경고를 무시한다.

그래서 현재 결론은 더 좁다.

`transfer-shrinkage는 후보를 고르는 답이 아니라, 나쁜 후보를 해부하는 해부도다.`

다음으로 가장 정보량이 큰 행동은 E128 risk index 최저 후보를 제출하는 것이 아니다. active/Q2S3 rollback, tail-equal residual, E72 exposure를 분리된 veto로 유지한 채, 그 위에서 selector-noise보다 큰 새 representation movement를 만드는 것이다.

## 추가 관찰: 기존 submission universe에도 숨은 후계자는 없었다

`analysis_outputs/e129_transfer_shrinkage_pareto_universe_audit.py`로 E128의 분리된 veto를 전체 local/report-referenced submission universe에 걸었다.

- candidate paths: `116044`.
- unique prediction tensors: `65865`.
- duplicates skipped: `50178`.
- strict veto survivors: `3`, 전부 same-family.
- strict actionable survivors: `2` = E85, E101.
- relaxed material survivors: E85, E101, E89.
- novel strict actionable survivors: `0`.

이건 좋은 후보를 찾지 못했다는 단순 실패가 아니다. 꽤 강한 반증이다. E128 veto를 제대로 분리해도 기존 파일 더미 안에서 새 successor가 나오지 않는다. 살아남는 건 이미 해석된 E85/E89/E101 hardtail line뿐이고, 그 line은 E101 public small-loss와 E124/E126 이후 약해졌다.

현재 최강 세계관은 더 짧아진다.

`0.5762913298 plateau는 기존 후보 선택 실패가 아니다. E95가 맞힌 S-heavy hardtail surgery 주변에는 낮은 위험 후보가 매우 좁게 존재하고, 그 좁은 영역은 이미 E101/E85/E89로 설명된 같은 family다. 다음 개선은 old CSV rank가 아니라 새로운 representation이 이 geometry 안에 새 점을 만들어야 한다.`

다음으로 가장 정보량이 큰 행동은 full universe 재검색이 아니다. tail-neutral/low-alpha density를 target representation으로 삼되, active/Q2S3 rollback과 E72 exposure를 분리 veto로 걸고, E95 대비 selector-noise보다 큰 새 movement를 만드는 것이다.

## 추가 관찰: tail-density를 바로 movement로 번역하면 실패한다

`analysis_outputs/e130_tail_density_synthesis_probe.py`로 E129 이후 첫 constructive route를 찔렀다. E95에서 시작해 E127의 tail-equal/low-alpha/density masks 위에서만 E86/E90/E89/E85/noQ2/mixmin 쪽으로 일부 이동했다.

- variants: `1792`.
- evaluated variants: `698`.
- E95-relative local strict variants: `25`.
- E129-veto-actionable variants before local strict: `19`.
- local-strict plus E129-veto-actionable: `0`.
- final submit gate: `0`.
- best local strict improvement vs E95: `-0.000001512`.
- best local strict rows were post-E101 sensor-adverse; the safest post-E101 rows were only micro-moves around `1e-8` scale.

이 결과는 E127 density가 틀렸다는 뜻이 아니다. 반대로 더 정확한 결론은 이거다.

`density는 public-compatible budget 위치를 말해주지만, 그 위치에서 어떤 방향으로 얼마나 움직여야 LogLoss가 좋아지는지는 아직 말해주지 않는다.`

따라서 지금 당장 제출할 파일은 없다. 다음 행동은 density mask를 더 섞는 것이 아니라, local upside와 E72/E101 exposure safety가 같은 셀/타깃에서 겹치도록 만드는 새 representation 또는 movement direction을 찾는 것이다.

## 추가 관찰: local-upside와 safe atom은 섞어도 겹치지 않는다

`analysis_outputs/e131_tail_density_atom_combo_probe.py`로 E130의 마지막 cheap loophole을 찔렀다.

- local atoms: `14`.
- safe atoms: `22`.
- candidate rows: `6384`.
- evaluated candidates: `700`.
- local strict candidates: `651`.
- veto-actionable candidates: `208`.
- local-strict plus veto-actionable: `0`.
- final submit gate: `0`.
- best local improvement vs E95: `-0.000001813`.
- best evaluated post-E101 sensor mean: `+0.000002326`.

이건 단순히 "좋은 조합을 못 찾았다"가 아니다. local strict와 veto-actionable이 각각 많이 생겼는데 교집합이 0이라는 점이 핵심이다. 즉 E130의 실패는 alpha/grid가 거칠어서가 아니라 geometry가 갈라져 있어서 생긴다.

현재 가장 압축된 병목 문장은 이렇다.

`E95 이후 plateau의 병목은 density 위치나 blend weight가 아니라, local LogLoss를 줄이는 old-donor 방향과 post-E101 public-tail 안전 방향이 같은 latent tangent space에 있지 않다는 점이다.`

다음으로 가장 정보량이 큰 행동은 더 큰 blend가 아니다. density-aligned support, E95-relative local upside, E72/E101 safety가 처음부터 같은 셀/타깃에 놓이는 새 movement representation을 찾아야 한다.

## 추가 관찰: donor-free gradient도 같은 벽에 부딪힌다

`analysis_outputs/e132_veto_nullspace_gradient_probe.py`로 마지막 싼 변명을 제거했다. E130/E131은 old donor 방향을 썼기 때문에 실패했을 수 있었다. 그래서 이번에는 E86/E90/E85/E89를 쓰지 않고, E95 자체의 combo-set gradient에서 직접 작은 logit movement를 만들었다.

- gradient candidates: `4590`.
- evaluated candidates: `698`.
- veto-actionable gradient rows: `843`.
- local-strict gradient rows: `0`.
- local-strict plus veto-actionable: `0`.
- submit gate: `0`.
- best local gradient move: E95 대비 `-0.000112772`.
- best post-E101 sensor rows: sensor mean은 좋아지지만 local strict structure가 무너짐.

이 결과는 꽤 중요하다. "donor가 더러워서 local-upside와 safety가 안 겹친다"는 설명은 약해졌다. donor를 제거해도 겹치지 않는다. 현재 combo-local gradient 자체가 public-safe hard-tail geometry와 맞지 않는다.

현재 병목 문장을 조금 더 강하게 수정한다.

`E95 이후 plateau는 E95 근처의 확률 공간에서 local gradient와 public-safe tail geometry가 거의 직교하기 때문에 생긴다. 같은 공간에서 mask, blend, alpha, top-cell을 더 만져도 0.54 방향은 열리지 않는다.`

다음으로 가장 정보량이 큰 행동은 E95 tangent move가 아니다. hidden block/run law, calibrated hard-tail support, transfer-shrinkage field 같은 다른 representation target을 먼저 만들고, 그 representation 안에서 local upside와 tail safety가 처음부터 같이 나타나는지 봐야 한다.

## 추가 관찰: 안전한 remainder는 Q2/S3가 아니라 Q3/Q1 쪽으로 밀린다

`analysis_outputs/e133_local_safety_colocation_atlas.py`로 E132의 실패를 셀 단위로 해부했다.

- best context: `all_sign`.
- `all_sign`에서 local reward mass 중 veto-null+density70 안에 들어가는 비율: `0.161830`.
- `all_sign` local top50: Q2/S3 `44%`, S3 `42%`.
- `all_sign` co-located top50: Q2/S3 `2%`, E101-active `0%`, Q3 `40%`, Q1 `34%`.
- best metadata CV: `subject_target`, JS `0.240700`, top50 truth-mass capture `0.048280`.

이건 사소한 분포표가 아니다. local gradient가 원하는 곳은 여전히 Q2/S3 쪽인데, tail safety와 transfer-shrinkage를 통과시키면 그 보상은 거의 사라지고 Q3/Q1 쪽의 작은 safe remainder만 남는다. 게다가 그 remainder는 subject/target/context metadata로 잘 복원되지 않는다.

현재 가장 압축된 세계관:

`0.5762913298 이후의 벽은 Q2/S3를 조금 더 잘 고르는 문제가 아니다. Q2/S3는 local reward를 만들지만 public-tail safety에서 제거되고, 남는 안전한 보상은 Q3/Q1 쪽에 작고 diffuse하게 흩어져 있으며 단순 metadata로는 복원되지 않는다.`

다음으로 가장 정보량이 큰 행동은 raw/run/block context가 이 Q3/Q1-heavy safe remainder를 예측할 수 있는지 보는 것이다. 실패하면 0.576대 병목은 "확률 이동 부족"보다 "안전한 hidden-state target 자체가 관측 feature에서 약하다"는 쪽으로 더 강해진다.

## 추가 관찰: raw/block context도 safe remainder를 충분히 보지 못한다

`analysis_outputs/e134_raw_block_colocation_predictability.py`로 E133의 다음 질문을 바로 찔렀다. `all_sign_co_vetonull_density`를 teacher로 두고, hidden-block holdout에서 raw overnight block embedding과 metadata가 이 safe remainder를 얼마나 복원하는지 비교했다.

- cells: `1750`.
- hidden blocks: `36`.
- best predictor: `night_all_blockknn` / `target_knn8`.
- best top50 truth-mass capture: `0.073497`.
- best metadata-only top50 truth-mass capture: `0.063040`.
- best top50 target mix: `Q1:37,Q3:4,S4:9`.
- Q2/S3 fraction in best top50: `0.000000`.

raw/block은 완전히 무력하지 않다. Q2/S3를 잘 억제하고 metadata보다 조금 더 보긴 한다. 하지만 `0.073497`은 selector-scale recovery가 아니다. 이 정도로는 "raw context가 JEPA context가 되어 safe remainder를 직접 찾는다"라고 말할 수 없다.

따라서 현재 병목 문장은 다시 압축된다.

`0.5762913298 이후의 벽은 안전한 셀을 못 고른다는 수준이 아니라, 안전한 hidden-state target 자체가 현재 관측 raw/block context에서 약하게만 보인다는 데 있다.`

지금 당장 제출할 파일은 없다. 다음 행동은 E133/E134 ranking을 probability로 옮기는 것이 아니라, target representation 자체를 다시 바꾸는 것이다.

## 추가 관찰: 기존 submission manifold에도 safe remainder는 거의 보이지 않는다

`analysis_outputs/e135_prediction_manifold_remainder_visibility.py`로 남은 싼 가능성을 찔렀다. raw/block에서 안 보인다면, 혹시 기존 submission들의 예측 차이와 row-level prediction PCA에는 E133 safe remainder가 들어 있을 수 있었다.

- cells: `1750`.
- hidden blocks: `36`.
- submissions used: `12`.
- best predictor: `row_prediction_pca_meta` / `ridge`.
- best top50 truth-mass capture: `0.063430`.
- metadata-only top50 truth-mass capture: `0.063040`.
- E134 raw/block reference: `0.073497`.
- best top50 target mix: `Q1:11,Q3:38,S4:1`.
- Q2/S3 fraction: `0.000000`.

결론은 닫힌다. 기존 prediction manifold는 Q2/S3를 억제하는 건강한 방향성은 갖고 있지만, safe remainder를 찾는 selector는 아니다. metadata와 거의 같고 raw/block보다도 약하다.

현재 병목 문장은 더 날카로워진다.

`E95 이후 plateau는 좋은 old CSV를 못 고른 문제가 아니다. local gradient, raw/block context, 기존 prediction manifold 모두 safe remainder를 약하게만 보기 때문에, 다음 돌파구는 cell ranking이 아니라 target representation 자체를 바꾸는 데 있다.`

지금 제출할 파일은 없다. 다음으로 가장 정보량이 큰 행동은 E133 teacher를 그대로 맞히는 실험을 멈추고, hard-tail support나 block/run law처럼 더 직접적으로 probability movement를 낳을 target을 새로 정의하는 것이다.

## 추가 관찰: cell이 아니라 block-target으로 보면 신호가 살아난다

`analysis_outputs/e136_target_compression_visibility_audit.py`로 target 자체가 잘못됐는지 찔렀다. 같은 E133 teacher를 그대로 쓰되, 셀 단위가 아니라 row-total, block-target, block-family, block-total로 압축했다.

- row-total units: `250`.
- block-target units: `252`.
- block-family units: `108`.
- block-total units: `36`.
- best compressed predictor: `block_target` + `all_raw_views_raw_pred` / `ridge`.
- top10 truth-mass capture: `0.332698`.
- random top10 대비 enrichment: `3.326980`.
- oracle top10 capture ratio: `0.709652`.
- pure raw block-target best: `night_all_raw` / `ridge`, enrichment `3.236095`.
- row-total best: `1.181643`.
- cell-level references: E134 `2.572395`, E135 `2.220050`.

이 결과는 중요하다. E134/E135의 부정 결과는 "safe remainder가 없다"가 아니라 "cell-level로 물은 질문이 너무 희박했다"일 수 있다. row-total은 약한데 block-target은 강해진다. 즉 숨은 법칙은 row 전체가 아니라 hidden block x target 상태에 더 가깝다.

현재 세계관을 수정한다.

`0.5762913298 이후의 벽은 safe cell을 못 고르는 문제가 아니라, safe mass가 block-target state로 먼저 나타나고 cell-level probability movement로 번역되는 과정이 아직 없어서 생긴다.`

그래도 지금 제출할 파일은 없다. E136은 target representation discovery다. 다음으로 가장 정보량이 큰 행동은 E136의 block-target state가 실제로 어떤 cell movement 방향과 amplitude를 만들어낼 수 있는지, 그리고 그 movement가 E128/E129/E124 hardtail/transfer stress를 통과하는지 보는 것이다.

## 추가 관찰: 보이는 block-target state도 기존 gradient로는 움직일 수 없다

`analysis_outputs/e137_blocktarget_state_movement_probe.py`로 E136의 바로 다음 질문을 찔렀다.

질문은 단순했다.

`E136 block-target state로 E95 combo-gradient를 gate하면, E132에서 갈라졌던 local upside와 transfer safety가 만나는가?`

결과:

- block-target gradient variants: `1980`.
- evaluated variants: `698`.
- local strict variants: `0`.
- transfer-veto-actionable variants: `0`.
- local-strict plus transfer-veto-actionable: `0`.
- submit-gate variants: `0`.
- best local delta vs E95: `-0.000043592`.
- best post-E101 mean vs E95: `-0.000040388`.
- 하지만 post-E101 p95는 양수 `~0.000026`이고, tail-equal law alignment도 약하다.

이건 E136을 죽이는 결과가 아니다. 오히려 더 정확히 분해한다.

E136 state는 mean improvement가 생기는 곳을 찾는다. 하지만 현재 E95 local gradient는 그 state 안에서도 strict structure와 transfer-veto safety를 만들지 못한다. 즉 병목은 이제 context visibility가 아니라 decoder다.

현재 세계관:

`safe mass는 block-target state로 관측된다. 그러나 E95 근처의 기존 combo-gradient는 그 state를 public-safe probability movement로 번역하지 못한다. 0.576대 벽은 state를 못 보는 벽에서, state를 안전한 방향과 amplitude로 decode하지 못하는 벽으로 이동했다.`

지금 제출할 파일은 없다. 다음으로 가장 정보량이 큰 행동은 block-target state 안에서 gradient를 재사용하지 말고, hardtail support 또는 targetwise label-state를 직접 예측하는 decoder를 만드는 것이다.

## 추가 관찰: state와 veto-null을 겹쳐도 strict law는 열리지 않는다

`analysis_outputs/e138_blocktarget_vetonull_overlap_probe.py`로 E137의 마지막 싼 escape hatch를 찔렀다.

질문은 이것이었다.

`E136 block-target state와 E132/E128 transfer-safe veto-null/low-adverse mask를 겹치면, 기존 E95 gradient도 드디어 안전해지는가?`

결과:

- overlap variants: `1314`.
- evaluated variants: `698`.
- transfer-veto-actionable variants: `373`.
- local strict variants: `0`.
- local-strict plus transfer-veto-actionable: `0`.
- submit-gate variants: `0`.
- best local delta vs E95: `-0.000030467`.
- best post-E101 mean/p95 vs E95: `-0.000055772` / `-0.000015691`.
- 하지만 best row도 combo-set win은 `2/3`, tail-neutral은 `1/3`뿐이고 hidden Q2/S3와 world support는 adverse다.

이 결과는 미묘하지만 중요하다. E137에서는 transfer-veto가 완전히 닫혀 있었는데, E138에서는 `373`개가 열린다. 즉 block-target state와 transfer-safe field는 실제로 어느 정도 만난다. 그런데도 strict law는 하나도 열리지 않는다.

현재 세계관을 다시 압축한다.

`safe mass는 block-target state로 보이고 transfer-safe region과도 겹치지만, 그 안의 현재 gradient는 all-set tail-neutral/world-consistent law가 아니다. 0.576대 벽은 state visibility나 co-location이 아니라 calibrated decoder의 부재다.`

지금 제출할 파일은 없다. 다음으로 가장 정보량이 큰 행동은 mask를 더 겹치는 것이 아니라, block-target state 안에서 all-set tail neutrality와 world/raw hidden support를 보존하는 방향/amplitude decoder를 직접 만드는 것이다.

## 추가 관찰: combo-set consensus도 tail/world 법칙을 열지 못한다

`analysis_outputs/e139_blocktarget_set_consensus_decoder_probe.py`로 E138의 마지막 쉬운 변명을 찔렀다.

질문은 이것이었다.

`E138이 실패한 이유가 combo-set gradient sign conflict라면, inverse_top/raw05_compatible/all_sign이 동의하는 cell만 움직이면 strict law가 열리는가?`

결과:

- set-consensus variants: `1188`.
- evaluated variants: `698`.
- transfer-veto-actionable variants: `190`.
- local strict variants: `0`.
- local-strict plus transfer-veto-actionable: `0`.
- submit-gate variants: `0`.
- best local delta vs E95: `-0.000022029`.
- best post-E101 mean/p95 vs E95: `-0.000041506` / `-0.000010520`.
- 모든 evaluated row가 all-margin/all-beats-base는 통과했다.
- 그러나 tail-neutral, world-nonworse, raw-energy-nonworse는 `698/698` 전부 실패했다.
- all-three consensus로 `3/3` combo-set mean win을 만든 row도 tail-neutral은 `1/3`뿐이었다.

이건 E138보다 더 좁은 반증이다. 이제 sign conflict 핑계도 죽었다. combo-set 평균 방향은 맞출 수 있지만, LogLoss가 벌주는 worst-tail/world/raw 법칙은 전혀 열리지 않는다.

현재 세계관을 다시 압축한다.

`block-target state, transfer-safe overlap, combo-set mean consensus까지는 만들 수 있다. 하지만 현재 gradient 계열은 그 셋을 모두 만족해도 tail/world/raw hidden law를 보존하지 못한다. 0.576대 벽은 support나 sign의 문제가 아니라, worst-tail/world-aware decoder가 없는 문제다.`

지금 제출할 파일은 없다. 다음으로 가장 정보량이 큰 행동은 BCE-style 평균 gradient를 계속 필터링하는 것이 아니라, tail-neutral/world/raw nonworse를 primitive objective로 삼는 decoder를 만드는 것이다.

## 추가 관찰: world/raw는 열렸지만 combo-tail은 여전히 닫혀 있다

`analysis_outputs/e140_tailworld_primitive_decoder_probe.py`로 E139 이후의 가장 작은 decoder 질문을 찔렀다.

질문은 이것이었다.

`block-target/veto support 안의 각 cell을 양방향으로 micro-move 했을 때, local reward와 tail/world/raw nonworse를 동시에 만족하는 원자가 있고, 그것들을 합치면 strict law가 열리는가?`

결과:

- support cells: `471`.
- micro rows: `942`.
- local-reward primitives: `373`.
- tail/world/local primitives: `119`.
- tolerance-level strict primitives: `3`.
- combined variants: `168`.
- local strict variants: `0`.
- transfer-veto-actionable variants: `0`.
- submit-gate variants: `0`.
- best combined all-minus-E95: `-0.000017556`.
- best post-E101 mean vs E95: `-0.000007182`.
- 모든 combined row가 hidden-core/world/raw nonworse는 통과했다.
- 그러나 모든 combined row가 all-set tail neutrality는 실패했고, 최대 tail-neutral count도 `1/3`에 머물렀다.

이건 중요한 실패다. E139에서는 world/raw도 같이 실패했는데, E140은 decoder 목적을 바꾸자 world/raw는 열린다. 하지만 combo-set worst-tail은 여전히 닫혀 있다.

현재 세계관을 다시 압축한다.

`0.576대 벽의 남은 핵심은 block-target state도, transfer-safe support도, combo-set mean sign도, world/raw support도 아니다. 마지막으로 버티는 것은 combo-set worst-tail balancing이다. 평균적으로 좋아지는 움직임은 만들 수 있지만, LogLoss tail을 세 combo-set 모두에서 동시에 중립화하지 못한다.`

지금 제출할 파일은 없다. 다음으로 가장 정보량이 큰 행동은 어떤 combo-set tail axis가 계속 깨지는지 분해하고, 평균 reward를 조금 희생해서라도 `1/3` tail-neutral을 `3/3`으로 올리는 tail-balancing decoder를 만드는 것이다.

## 추가 관찰: tail 실패의 일부는 gate artifact였고, 진짜 벽은 transfer-tail budget이다

`analysis_outputs/e141_tail_tolerance_transfer_audit.py`로 E140의 tail 실패를 다시 찔렀다.

질문은 이것이었다.

`E140의 all-set tail neutrality 실패는 실제 tail-axis 실패인가, 아니면 raw05/all_sign의 1e-16 수준 numerical zero를 exact <=0 gate가 실패로 세는 artifact인가?`

결과:

- exact `0` tail pass: `0`.
- tolerance `1e-12` tail pass: `129`.
- tolerance `1e-12` relaxed structural pass: `84`.
- tolerance `1e-6` relaxed structural pass: `91`.
- relaxed + E72 exposure pass: `0`.
- relaxed + post-E101 p95 pass: `0`.
- relaxed actionable: `0`.
- E95 E72-plausible threshold: `0.001557335020`.
- minimum relaxed E72 exposure: `0.001560524555`.
- minimum gap: `+0.000003189534`.
- best relaxed post-E101 p95: `+0.000000141478`.

이건 E140 결론을 정정한다. combo-tail이 전부 닫힌 게 아니다. exact gate가 너무 빡빡했다. 하지만 tolerance를 주면 구조 row가 열리는데도 submission gate는 열리지 않는다.

현재 세계관을 다시 압축한다.

`0.576대 벽의 현재 최전선은 combo-tail exactness가 아니라 transfer-tail budget이다. E140 계열 움직임은 구조적으로는 거의 살아날 수 있지만, E95가 이미 차지한 E72-plausible exposure 예산을 약 3.2e-6만큼 초과하고 post-E101 p95를 양수로 남긴다.`

지금 제출할 파일은 없다. 다음으로 가장 정보량이 큰 행동은 local all-minus-E95 `~1e-5` 보상을 유지하면서 E72-plausible exposure를 E95 이하로 낮추는 budget-neutral correction을 찾는 것이다.

## 추가 관찰: transfer-tail budget은 clipping으로 열린다

`analysis_outputs/e142_transfer_budget_clipped_decoder_probe.py`로 E141이 남긴 병목을 바로 찔렀다.

질문은 이것이었다.

`E140 relaxed structural row는 전체가 틀린 움직임인가, 아니면 E72-plausible exposure를 쓰는 몇 개 cell만 E95로 되돌리면 살아나는가?`

결과:

- parent relaxed structural material rows: `11`.
- clipped variants: `1844`.
- relaxed structural variants: `670`.
- relaxed + E72-budget variants: `35`.
- relaxed + budget + post-E101 variants: `35`.
- submit-relaxed variants: `35`.
- materialized file: `analysis_outputs/submission_e142_transferclip_09a92236.csv`.
- selected row: parent `e140_score_top_local_25c44401`, rollback cells `55`, changed cells vs E95 `185`.
- target movement vs E95: Q1 `38`, Q2 `0`, Q3 `56`, S2 `23`, S3 `47`, S4 `21`.
- local all-minus-E95: `-0.000010666782`.
- E72-plausible gap vs E95: `~0`.
- post-E101 mean/p95/beat vs E95: `-0.000014379591` / `-0.000003762343` / `1.0`.

이건 중요한 변화다. E141에서 보인 budget wall은 완전히 불가능한 벽이 아니었다. 다만 uniform shrink로는 열리지 않았고, high excess-exposure cell을 완전히 롤백해야 열렸다.

현재 세계관을 다시 압축한다.

`E95 이후의 살아 있는 다음 움직임은 Q2/S3 rollback이 아니다. transfer-tail budget을 쓰는 cell을 제거한 Q1/Q3/S/S3 residual decoder다. public이 이것을 받아들이면 0.576대 벽은 "모델 capacity"가 아니라 "E95 law 위에 남은 transfer-budget-neutral tangent를 찾는 문제"로 더 좁아진다. public이 거절하면 E101-conditioned density gate가 selector로는 과적합이라는 뜻이다.`

E143 repair 전까지 제출 우선순위는 `analysis_outputs/submission_e142_transferclip_09a92236.csv`였다.

## 추가 관찰: E142의 마지막 active/Q2S3 리스크는 작게 고칠 수 있다

`analysis_outputs/e143_e142_active_q2s3_veto_repair.py`로 E142를 한 번 더 찔렀다.

질문은 이것이었다.

`E142가 E72-budget과 post-E101 p95는 통과하지만 active/Q2S3 strict gate를 실패한다면, 그 실패는 residual decoder 전체가 틀렸다는 뜻인가, 아니면 Q2/S3 active cell 일부만 과하게 남았다는 뜻인가?`

결과:

- repair variants: `80`.
- relaxed-submit repair variants: `80`.
- original-strict-submit repair variants: `15`.
- materialized file: `analysis_outputs/submission_e143_activeq2s3repair_68ca656f.csv`.
- selected repair: `top_q2s3_weighted_21`, keep factor `0.0`.
- rollback cells: `21`.
- changed cells vs E95: `164`.
- local all-minus-E95: `-0.000009551358`.
- E72-plausible gap vs E95: `~0`.
- post-E101 mean/p95/beat vs E95: `-0.000013131201` / `-0.000003368915` / `1.0`.
- active/Q2S3 gate and original strict actionability both pass.

이건 E142 해석을 다시 좁힌다. E142의 마지막 리스크는 residual decoder 전체의 실패가 아니라, E101 small-loss가 경고한 Q2/S3 active edge를 조금 덜어내야 하는 문제였다.

현재 세계관을 다시 압축한다.

`E95 이후의 다음 가망 있는 움직임은 transfer-budget-neutral residual decoder다. 다만 E101이 보여준 Q2/S3 active 과집중은 반드시 잘라야 한다. 그래서 E142보다 E143이 더 좋은 다음 센서다. E143이 public에서 좋아지면 "E95 law + residual decoder + active/Q2S3 pruning"이 강화되고, 실패하면 transfer-budget clipping 자체가 public-sensor overconditioning이었는지 의심해야 한다.`

E144 fine-boundary audit 전까지 제출 파일은 `analysis_outputs/submission_e143_activeq2s3repair_68ca656f.csv`였다.

## 추가 관찰: E143의 active/Q2S3 경계는 full rollback이 아니라 fine cliff다

`analysis_outputs/e144_e143_active_boundary_refine.py`로 E143의 마지막 경계를 더 촘촘히 찔렀다.

질문은 이것이었다.

`E143의 top21 full rollback은 진짜 최적 경계인가, 아니면 coarse grid가 만든 안전한 점일 뿐인가?`

결과:

- repair variants: `206`.
- original-strict repair variants: `32`.
- E144-submit variants: `9`.
- materialized file: `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.
- selected repair: `top_q2s3_weighted_24`, keep factor `0.15`.
- rollback cells: `24`.
- changed cells vs E95: `185`.
- local all-minus-E95: `-0.000009725930`.
- E143 local all-minus-E95: `-0.000009551358`.
- E72-plausible gap vs E95: `~0`.
- post-E101 mean/p95/beat vs E95: `-0.000013326583` / `-0.000003430489` / `1.0`.
- active/Q2S3 gate and original strict actionability both pass.

이건 E143 해석을 한 번 더 좁힌다. active/Q2S3 경계는 "21개를 전부 0으로 롤백해야 한다"가 아니라, `22..24`개 근처에서 아주 작은 retained movement를 허용하는 cliff다.

현재 세계관을 다시 압축한다.

`E95 이후의 다음 가망 있는 움직임은 여전히 transfer-budget-neutral residual decoder다. 하지만 그 decoder의 public-tail 안전성은 거친 full rollback보다 더 미세한 active/Q2S3 경계에서 결정된다. E144가 public에서 좋아지면 이 fine boundary가 실재한다는 뜻이고, E144는 실패하지만 E143이 살아나면 keep0.15가 public-tail을 너무 낙관한 것이다.`

지금 제출할 파일은 하나다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.

## 추가 관찰: E144 결과 해석은 미리 고정해야 한다

`analysis_outputs/e145_e144_public_feedback_decoder.py`로 E144 public feedback decoder를 만들었다.

질문은 이것이었다.

`E144의 public LB가 나오면, 어느 구간부터 fine-boundary 세계관이 살아나고, 어느 구간부터 E143/E142 자동 후속을 막아야 하는가?`

결과:

- `breakthrough_win`: `<=0.576271330`.
- `clean_win`: `(0.576271330, 0.576284330]`.
- `micro_win`: `(0.576284330, 0.576289330]`.
- `tie`: `(0.576289330, 0.576293330]`.
- `fine_loss_branch_alive`: `(0.576293330, 0.576300366]`.
- `branch_loss`: `(0.576300366, 0.576306641]`.
- `hard_fail`: `>0.576306641`.

현재 세계관을 다시 압축한다.

`E144는 점수 자체보다 해석 분기표가 중요하다. E144가 E95를 읽을 만큼 이기면 fine active/Q2S3 boundary가 살아난다. E95보다 지지만 E101보다 나쁘지 않으면 E143만 같은 family contrast로 남는다. E101보다 나쁘면 E143/E142를 자동으로 구하면 안 된다. mixmin보다 나쁘면 E142/E143/E144 branch 자체가 public-sensor overfit이다.`

다음으로 가장 정보량이 큰 행동은 E144를 제출한 뒤 `analysis_outputs/e145_e144_public_feedback_decoder.csv`로만 해석하는 것이다.

## 추가 관찰: E144의 retained S3 tail은 독립 prior도 지지한다

`analysis_outputs/e146_e144_e143_tail_prior_audit.py`로 E144와 E143의 차이만 분리했다.

질문은 이것이었다.

`E144가 E143보다 나은 이유는 local strict gate의 미세한 산술인가, 아니면 visible global/subject/flank prior도 E144의 retained tail을 지지하는가?`

결과:

- E144와 E143이 다른 셀: `24`.
- 전부 `S3`.
- rows/subjects touched: `24` / `4`.
- E143 대비 E95에서 멀어지는 셀: `21`.
- E143 대비 E95 쪽으로 돌아가는 셀: `3`.
- edge-like cells: `7`.
- flank-conflict cells: `0`.
- E144를 선호한 public-free prior: `10/10`.
- best expected prior: `nearest_hard085`, E144-minus-E143 `-0.000010294767`.
- weakest expected prior: `subject`, E144-minus-E143 `-0.000001097289`.
- simulated `p(E144 beats E143)`: subject prior `0.540545`, nearest-hard prior `0.925720`.

이건 E144 해석을 조금 강화한다. E144의 `keep0.15` retained S3 tail은 단지 local gate가 고른 숫자가 아니다. visible prior도 E143보다 E144를 더 자연스럽게 본다.

현재 세계관을 다시 압축한다.

`E144는 E143보다 작은 local edge만 가진 파일이지만, 그 edge는 24개의 S3 fine-tail 셀에 집중되어 있고 public-free prior도 같은 방향을 본다. 따라서 E144가 실패하면 "E143이 원래 더 안전했다"가 아니라 "public hidden S3 tail이 visible prior보다 더 adverse였다"로 읽어야 한다. E143은 기대값 rescue가 아니라 fine-tail retention contrast로만 남는다.`

E154 이전 기준으로는 제출 파일이 `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` 하나였다.

## 추가 관찰: E155보다 더 작은 Q1/S2/S4 target-axis repair가 있다

`analysis_outputs/e156_e154_target_axis_lattice.py`로 E154의 E144->E154 body를 target-axis별로 분해했다.

질문은 이것이었다.

`E155의 25% diagonal body가 정말 최소 coherent repair인가, 아니면 특정 target-axis 조각만으로도 all-four health가 살아나는가?`

결과:

- active lattice axes: `Q1,Q3,S2,S3,S4`.
- lattice variants: `3125`.
- all-four lattice rows: `3125`.
- strict candidates: `2984`.
- E155 body ratio `0.25`보다 작은 rows: `85`.
- selected file: `analysis_outputs/submission_e156_targetaxis_757546d2.csv`.
- selected axes: `Q1+S2+S4`.
- selected alphas: Q1 `0.25`, S2 `0.75`, S4 `0.25`.
- selected body ratio: `0.171266667`.
- selected all-minus-E95: `-0.000010004`.
- selected post-E101 p95: `-0.000003712`.
- selected E72 gap: `-0.000002266`.
- cosine vs E144/E155/E154: `0.999515751` / `0.998991027` / `0.985122955`.

이건 E155 해석을 한 번 더 낮춘다. E154 full body도 필요 없고, E155 diagonal 25% body도 최소가 아니다. 최소 survivor는 거의 E144 위에 붙은 작은 Q1/S2/S4 add-on이다. 다만 local edge는 E154/E155보다 약하고, geometry도 거의 E144/E155와 같은 방향이다.

현재 세계관을 다시 압축한다.

`repaired branch는 single point도 아니고 diagonal body도 아니다. 하지만 지금까지 찾은 낮은 amplitude survivor는 broad hidden law가 아니라 E144-collinear target-axis add-on이다. 따라서 E154가 첫 public sensor, E155가 amplitude-control, E156이 target-axis decomposition control이다. E156을 먼저 내면 질문이 너무 약해진다.`

E157 이전 기준의 제출 순서는 바뀌지 않았다. 첫 파일은 `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`, 둘째는 `analysis_outputs/submission_e155_bodytemp_d27e7965.csv`, 셋째 control은 `analysis_outputs/submission_e156_targetaxis_757546d2.csv`였다.

## 추가 관찰: E156의 Q1/S2/S4 선택은 target law가 아니라 body-minimization artifact다

`analysis_outputs/e157_e156_axis_response_audit.py`로 E156 lattice를 target-axis finite difference와 low-body Pareto 관점에서 다시 찔렀다.

질문은 이것이었다.

`E156 min-body가 말하는 Q1/S2/S4 target law가 진짜인가, 아니면 all-four gate가 이미 saturated되어 body objective가 고른 점인가?`

결과:

- lattice variants: `3125`.
- all-four lattice rows: `3125`.
- strict candidates: `2984`.
- all-minus-E95 span across the lattice: `0.000002432120`.
- Q3 local finite-diff mean: `-0.000000383335`.
- Q3 post-E101 finite-diff mean: `-0.000000132956`.
- S2 E72-gap finite-diff mean: `-0.000000714955`.
- E155-dominating low-body rows: `3`.
- selected file: `analysis_outputs/submission_e157_lowbodypareto_bd67930d.csv`.
- selected axes: `Q1+Q3+S2+S4`.
- selected alphas Q1/Q3/S2/S3/S4: `0.25/0.25/0.50/0.00/0.50`.
- selected body ratio: `0.240336139`.
- selected all-minus-E95: `-0.000010404446`.
- selected post-E101 p95: `-0.000003807382`.
- selected E72 gap: `-0.000001671496`.

이 결과는 E156의 해석을 다시 낮춘다. Q1/S2/S4만 살아남았다는 게 아니라, Q3는 local/post-E101에서 가장 좋은 축이지만 body norm 비용이 커서 minimum-body objective에서 빠진 것이다. S2는 E72 gap budget을 실질적으로 책임진다. 즉 E156은 target law가 아니라 saturated all-four lattice에서 body objective가 고른 한 점이다.

현재 세계관을 다시 압축한다.

`repaired branch의 낮은 amplitude 영역은 넓게 살아 있지만, 그 안에서 target-axis 선택은 아직 public 법칙이 아니라 micro-geometry다. E154는 가장 정보량 큰 repaired full-body sensor, E155는 깨끗한 amplitude-control, E157은 tuned low-body Pareto control, E156은 minimum-body decomposition control이다. E157/E156을 먼저 내면 E154/E155가 주는 해석력을 버리는 셈이다.`

현재 제출 순서는 `E154 -> E155 -> E157 -> E156 -> E144`다.

## 추가 관찰: repaired-branch control들은 첫 sensor가 아니라 public-feedback 도구다

`analysis_outputs/e158_repaired_branch_public_decoder.py`로 E154/E155/E157/E156/E144 stack을 한 번 더 압축했다.

질문은 이것이었다.

`E154, E155, E157, E156의 작은 local 차이는 public에서 읽을 수 있는 독립 신호인가, 아니면 E154 결과를 해석하기 위한 post-feedback control인가?`

결과:

- E154 vs E155 local all-minus gap: `-0.000001795559`.
- E154 vs E144 local all-minus gap: `-0.000002432120`.
- E157 vs E155 local all-minus gap: `-0.000000041955`.
- E156 vs E155 local all-minus gap: `+0.000000358921`.
- public-readable guardrail: `2e-6`.
- E155/E157/E156 cosine vs E144: `0.998962769` / `0.999041566` / `0.999515751`.
- decoder files:
  - `analysis_outputs/e158_repaired_branch_public_decoder_candidates.csv`
  - `analysis_outputs/e158_repaired_branch_public_decoder_pairwise.csv`
  - `analysis_outputs/e158_repaired_branch_public_decoder_bands.csv`
  - `analysis_outputs/e158_repaired_branch_public_decoder_report.md`

이 결과는 E154의 의미를 더 정확하게 만든다. E154가 첫 제출인 이유는 E155보다 public-readable하게 낫기 때문이 아니다. E154는 unrepaired E144 대비 full repaired all-four 질문을 가장 선명하게 묻기 때문에 첫 sensor다. 반대로 E155/E157/E156은 서로 너무 가까워서 public feedback 전 기대점수 순위로 쓰면 안 된다.

현재 세계관을 다시 압축한다.

`E154/E155/E157/E156은 점수 순위표가 아니라 하나의 branch를 해부하는 sensor stack이다. E154가 이기면 full repaired branch를 새 anchor로 삼고 형제 파일을 바로 내지 않는다. E154가 tie/small-loss면 E155만 깨끗한 amplitude-control이다. E154가 hard-fail이면 E157/E156으로 rescue하지 말고 E144 contrast 또는 representation search로 돌아간다.`

현재 제출 순서는 그대로 `E154 -> E155 -> E157 -> E156 -> E144`지만, 이 순서는 기대점수 순서가 아니라 질문 순서다.

## 추가 관찰: E154는 고립점이 아니라 낮은 amplitude ridge다

`analysis_outputs/e155_e154_branch_body_ablation.py`로 E154의 가장 위험한 부분을 분해했다.

질문은 이것이었다.

`E154가 all-four를 연 것은 정확히 그 full branch body가 필요했기 때문인가, 아니면 E144에서 E154 방향으로 조금만 움직여도 같은 hidden law가 살아나는가?`

결과:

- total rows: `44`.
- variant rows: `40`.
- all-four variants: `34`.
- E155-submit variants: `27`.
- reduced-body submit variants: `22`.
- selected file: `analysis_outputs/submission_e155_bodytemp_d27e7965.csv`.
- selected row: E144->E154 logit body alpha `0.25`.
- selected all-minus-E95: `-0.000010362491`.
- E144 all-minus-E95: `-0.000009725930`.
- E154 all-minus-E95: `-0.000012158050`.
- selected body-norm ratio: `0.25`.
- target-drop all-four: `12/12`.

이건 E154 해석을 바꾼다. E154는 single exact point가 아니다. 방향 자체는 훨씬 낮은 amplitude에서도 살아 있다. 다만 E155의 local edge는 E154보다 훨씬 작다. 그래서 public 센서로는 E154가 더 정보량이 크고, E155는 full-body overextension을 의심할 때 쓰는 보수적 amplitude-control이다.

현재 세계관을 다시 압축한다.

`E95 이후 살아 있는 branch는 E144 위에 있고, S3 active-boundary repair가 그 branch를 확장한다. E154는 full repaired branch를 묻는 센서이고, E155는 같은 방향을 25%만 믿는 센서다. E154가 이기면 full repair가 public-real이다. E154가 지고 E155가 이기면 방향은 맞지만 amplitude가 과했다. 둘 다 지면 repaired branch 자체를 닫아야 한다.`

지금 한 파일만 고르면 여전히 `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`다. `analysis_outputs/submission_e155_bodytemp_d27e7965.csv`는 두 번째, 더 보수적인 amplitude-control이다.

## 추가 관찰: S3 active-boundary repair가 all-four 교차점을 열었다

`analysis_outputs/e154_s3_active_boundary_repair_probe.py`로 E153의 가장 큰 blocker를 직접 찔렀다.

질문은 이것이었다.

`E152/E153에서 relaxed, E72-budget, post-E101은 통과하지만 actionability만 실패한 102개 near-miss가 정말 죽은 행인가, 아니면 몇 개의 S3 active-boundary cell만 덜어내면 살아나는가?`

결과:

- source missing-actionable rows: `102`.
- S3 repair rows: `7458`.
- all-four repairs: `10`.
- materialized rows: `10`.
- selected file: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.
- selected repair: `top_s3_e101_3`, keep `0.25`, rollback S3 cells `3`.
- selected all-minus-E95: `-0.000012158050`.
- E154 changed cells vs E95: `294`.
- E154 contains E144 cells: `185/185`.
- cosine vs E144/E143/E142: `0.983569299` / `0.975091856` / `0.939950819`.
- cosine vs E72/E101 negative axes: `-0.031628728` / `-0.005523655`.
- target L1 share: Q3 `0.356221`, Q1 `0.233468`, S3 `0.152445`, S2 `0.134198`, S4 `0.123668`, Q2/S1 almost zero.

이건 E153 해석을 바꾼다. E152의 all-four 실패는 terminal incompatibility가 아니었다. 정말 작은 S3 E101-active rollback만으로 all-four가 열린다. 하지만 이건 broad breakthrough도 아니다. E154는 E144의 185개 cell을 모두 포함하는 E144-collinear branch extension이다.

현재 세계관을 다시 압축한다.

`0.5762913298 이후의 살아 있는 움직임은 E144 branch 위에 있다. 다만 그 branch가 public-safe가 되려면 S3 active-boundary cell 몇 개를 정확히 덜어내야 한다. E154는 그 조건을 처음으로 만족한 all-four 후보이고, public이 받아들이면 S3 active-boundary repair가 실제 hidden law였다는 뜻이다. public이 거절하고 E144가 나중에 살아나면 E154의 추가 orthogonal body 또는 3-cell rollback이 과적합이었다는 뜻이다. 둘 다 거절되면 transfer-budget residual branch 자체를 닫아야 한다.`

지금 한 파일만 고르면 `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`는 더 보수적인 같은-branch contrast로 내려간다.

## 추가 관찰: near miss의 99%는 S3 active-boundary에서 죽는다

`analysis_outputs/e153_gate_intersection_failure_atlas.py`로 E152의 all-four 교차 실패를 분해했다.

질문은 이것이었다.

`E152의 3-of-4 near miss는 threshold를 조금 풀면 살아나는가, 아니면 서로 다른 gate들이 실제로 다른 hidden state를 요구하는가?`

결과:

- projected rows: `2880`.
- 3-of-4 near misses: `103`.
- all-four rows: `0`.
- `missing_actionable`: `102`.
- `missing_relaxed`: `1`.
- missing-actionable의 active/Q2S3 fail: `101/102`.
- missing-actionable의 action-cos fail: `50/102`.
- missing-actionable의 E72/material fail: `0/102`.
- missing-actionable의 relaxed fail: `0/102`.
- missing-relaxed의 raw/world relaxed fail: `1/1`.
- missing-actionable target lift: S3 `+0.022774`, S4 `+0.020949`, S2 `+0.018800`.
- Q2 share는 사실상 `0`.

현재 세계관을 다시 압축한다.

`q2s3라는 이름이 이제 부정확하다. E152 near miss를 죽이는 것은 Q2가 아니라 S3 active-boundary exposure다. relaxed/E72/post101은 통과하는 102개 후보가 S3 active-boundary actionability에서 죽고, actionability를 통과하는 유일한 후보는 Q1-heavy raw/world health에서 죽는다. 따라서 이 병목은 scalar threshold 문제가 아니라 decoder가 S3 active-boundary와 raw/world structural health를 동시에 만족하는 상태를 만들지 못하는 문제다.`

지금 제출할 파일은 변하지 않는다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.

## 추가 관찰: branch 밖 signal은 많지만 decoder 교집합은 없다

`analysis_outputs/e152_branch_orthogonal_decoder_audit.py`로 E151의 escape hatch를 직접 찔렀다.

질문은 이것이었다.

`E137-E140 안에 E144 branch와 다른 non-collinear signal이 이미 있고, 단지 E144 주변만 보느라 놓친 것인가?`

결과:

- source rows: `4650`.
- candidate-interest rows: `3953`.
- E144 기준 non-collinear source rows: `4650`.
- projected rows: `2880`.
- relaxed structural rows: `349`.
- E72-budget rows: `1208`.
- post-E101-safe rows: `564`.
- active-veto actionable rows: `122`.
- all-four intersection: `0`.
- best local projected move: `-0.0000455468`.
- `relaxed_budget_post101` intersection: `102`, best `-0.0000128032`, but active-veto/actionability fails.
- `budget_post101_actionable` intersection: `1`, best `-0.0000106142`, but relaxed structural fails.

현재 세계관을 다시 압축한다.

`0.576대 벽은 branch 밖 signal 부재가 아니다. Signal은 많다. 문제는 signal을 probability movement로 번역하는 순간 structural reward, E72 budget, post-E101 safety, active-veto actionability가 동시에 열리지 않는다는 점이다.`

그래서 E152는 제출 파일을 만들지 않는다. E144는 여전히 다음 public sensor다. E144를 기다리는 동안의 다음 질문은 "더 orthogonal한 방향을 찾자"가 아니라, `E138 relaxed-budget-post101 rows는 왜 active-veto에서 죽고, E139 budget-post101-actionable row는 왜 relaxed structural에서 죽는가?`다.

## 추가 관찰: 0.5762913298 plateau는 후보 탐색 실패보다 해상도/디코더 병목에 가깝다

`analysis_outputs/e151_plateau_resolution_bottleneck_audit.py`로 지금까지의 E98/E120/E129-E150 증거를 한 테이블로 묶었다.

질문은 이것이었다.

`0.5762913298 plateau는 좋은 후보를 못 고른 문제인가, 아니면 local-upside와 public-tail safety가 아주 좁은 branch에서만 만나는 문제인가?`

결과:

- E95가 mixmin을 이긴 폭: `0.0000153107`.
- best known-LB selector p90 error: `0.0008164966`, E95 edge의 `53.33x`.
- E101 actual-minus-local-mean optimism: `0.0000252415`, E95 edge의 `1.65x`.
- E144 local edge vs E95: `-0.0000097259`.
- E144-over-E143 local tiebreak: `-0.0000001746`.
- old submission universe의 strict novel actionable: `0`.
- E130/E131/E132/E137/E138/E139 representation/decoder families: 모두 `submit_gate=0`.
- live branch count: E142 relaxed `35`, E143 strict `15`, E144 submit `9`.
- E144 cosine with E143: `0.991918719`.

현재 세계관을 다시 압축한다.

`E95는 real S-heavy hardtail/calibration law다. 하지만 그 다음 residual structure는 기존 selector 해상도보다 작고, visible state를 probability movement로 디코딩하면 local reward와 public-tail safety가 분리된다. E142/E143/E144만 현재 둘이 만나는 좁은 지점이고, 그마저도 E143 branch와 거의 같은 방향이다.`

따라서 0.576대 벽은 이제 더 정확히 이렇게 보인다.

`좋은 모델을 더 돌리면 되는 벽이 아니라, representation-to-probability decoder가 public-tail-safe tangent를 만들어야 하는 벽이다. 기존 CSV 우주를 더 뒤지는 일은 대부분 닫혔다.`

지금 제출 후보는 변하지 않는다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.
E144를 기다리는 동안의 다음 local 행동은 blend/top-count sweep이 아니라, E143과 비공선인 transfer-budget-neutral residual representation을 만들고 strict/E72/post101 p95 gate를 통과시키는 것이다.

## 추가 관찰: E144 결과 이후 행동 규칙을 실행 가능하게 고정했다

`analysis_outputs/e150_e144_postfeedback_interpreter.py`로 E145/E148/E149를 하나의 decision gate로 합쳤다.

질문은 이것이었다.

`E144 public LB가 나오면, 점수 band만 보고 E143/E142로 자동 후퇴하는 실수를 막을 수 있는가?`

결과:

- interpreter rows: `7`.
- `fine_loss_branch_alive`: `conditional_alive`.
- E143 허용 조건: attribution이 fine-tail/S3 retention failure를 가리킬 때만.
- `branch_loss`: E143/E142 자동 rescue 금지.
- `hard_fail`: E142/E143/E144 local boundary branch close.
- 실제 점수가 나오면 실행할 명령:
  `python3 analysis_outputs/e150_e144_postfeedback_interpreter.py --score <PUBLIC_LB>`.

현재 세계관을 다시 압축한다.

`E144의 public score 하나만으로는 원인을 알 수 없다. E144가 fine-loss여도 그건 fine-tail 실패일 수도 있지만 inherited-body/Q3/S2 실패일 수도 있다. 따라서 다음 행동은 score band + attribution + geometry를 동시에 통과해야 한다. 이 규칙 없이는 public LB를 센서가 아니라 튜닝 타깃으로 오해하게 된다.`

지금 제출할 파일은 변하지 않는다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.

## 추가 관찰: E144는 새 법칙이 아니라 branch-pruned residual sensor다

`analysis_outputs/e149_e144_anchor_geometry_audit.py`로 E144의 logit movement를 known public anchor 방향에 놓고 봤다.

질문은 이것이었다.

`E144는 E95 이후의 새로운 넓은 successor law인가, 아니면 E142/E143 residual branch를 E72/E101 손실축에서 떨어뜨린 작은 정제인가?`

결과:

- E144-vs-E95 changed cells: `185`.
- E144 cosine with E101 loss axis: `-0.019625796`.
- E144 cosine with E72 fail axis: `-0.024358970`.
- E144 cosine with E142 branch axis: `0.952146833`.
- E144 cosine with E143 branch axis: `0.991918719`.
- residual ratio vs E142 axis: `0.305640978`.
- residual ratio vs E143 axis: `0.126874959`.
- E144 Q2/S3 share: `0.161603888`.
- E101 Q2/S3 share: `1.000000000`.

현재 세계관을 다시 압축한다.

`E144는 broad breakthrough가 아니다. E144는 E143 branch와 거의 같은 방향에 있는, public-negative E72/E101 축을 피한 branch-pruned residual sensor다. 그래서 E144가 이기면 새로운 거대한 법칙이 열린다기보다 E142/E143 transfer-budget residual branch와 fine active-boundary pruning이 public에서도 살아남는다는 뜻이다. E144가 지면 먼저 branch 자체와 S3/Q3/body attribution을 봐야지, 바로 E143를 자동 제출하면 안 된다.`

지금 제출할 파일은 변하지 않는다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.

## 추가 관찰: E144 전체도 E95 대비 visible prior가 지지한다

`analysis_outputs/e147_e144_e95_prior_world_audit.py`로 E144 전체와 E95의 차이를 분해했다.

질문은 이것이었다.

`E146이 본 24개 S3 fine-tail만이 아니라, E144의 185개 전체 이동이 E95 frontier 대비 public-free prior에서도 말이 되는가?`

결과:

- E144-vs-E95 moved cells: `185`.
- rows/subjects touched: `108` / `9`.
- target mix: Q3 `56`, S3 `47`, Q1 `38`, S2 `23`, S4 `21`.
- Q2/S1 movement: `0`.
- component mix: inherited E143 body `161`, E144 fine-tail delta `24`.
- edge-like cells: `62`.
- flank-conflict cells: `26`.
- E144를 선호한 public-free prior: `10/10`.
- expected E144-minus-E95 delta range: `-0.000049865515` to `-0.000012197928`.
- simulated `p(E144 beats E95)`: `0.583850` to `0.762700`.
- nearest-hard 기준 favorable target: Q1, S4, S2.
- nearest-hard 기준 adverse target: S3, Q3.
- nearest-hard 기준 inherited body는 favorable, fine-tail delta는 mild adverse.

현재 세계관을 다시 압축한다.

`E144는 단순히 E143보다 아주 조금 나은 local tweak가 아니다. E95 대비 전체 185개 이동도 visible prior에서는 일관되게 지지된다. 다만 그 지지는 inherited E143 body에서 주로 나오고, public에서 깨진다면 S3/Q3 또는 fine-tail retention 쪽에서 깨질 가능성이 높다. 따라서 E144가 실패하면 branch 전체를 즉시 버리거나 E143로 기계적으로 후퇴하지 말고, E145 band와 E147 target/component decomposition으로 실패 위치를 먼저 읽어야 한다.`

지금 제출할 파일은 변하지 않는다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.

## 추가 관찰: E144 결과를 보기 전에 책임 지도를 고정했다

`analysis_outputs/e148_e144_public_outcome_attribution.py`로 E144 public outcome attribution을 만들었다.

질문은 이것이었다.

`E144가 E145의 각 band에 떨어질 때, 그 결과를 만든 hidden label world는 어떤 target/component support pattern이어야 하는가?`

결과:

- prior마다 `250000`개 label-world를 샘플링했다.
- global prior win-rate mass: `0.745560`.
- subject prior win-rate mass: `0.599760`.
- nearest-hard prior win-rate mass: `0.635616`.
- global prior branch-or-worse mass: `0.204972`.
- subject prior branch-or-worse mass: `0.333832`.
- nearest-hard prior branch-or-worse mass: `0.284852`.
- fine-loss-alive mass: `0.027696..0.033340`.
- nearest-hard 기준 loss blame: S3/Q3.
- global 기준 loss blame: inherited body/Q3/S2.
- subject 기준 loss blame: inherited body/Q3/S3.

이건 E145의 후속 규칙을 더 엄격하게 만든다. E144가 fine-loss band에 들어간다고 해서 자동으로 E143을 내는 것은 아직 이르다. fine-loss도 fine-tail failure가 아닐 수 있고, inherited E143 body나 Q3/S2/S3 쪽의 broad support shortfall일 수 있다.

현재 세계관을 다시 압축한다.

`E144는 평균적으로 제출할 가치가 있는 다음 sensor지만, hidden public tail이 충분히 adversarial이면 질 수 있다. 그 실패는 하나의 실패가 아니다. fine-tail/S3 failure, inherited-body failure, Q3/S2 target-body failure가 서로 다른 세계관을 뜻한다. 따라서 E144 public 결과가 나오면 E145로 band를 정하고, E148로 책임 위치를 읽은 뒤에야 E143/E142/branch-close를 결정해야 한다.`

E154 이전 기준으로는 제출 파일이 `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` 하나였다.

## 추가 관찰: E154도 score band만으로는 해석하면 안 된다

`analysis_outputs/e159_e154_public_outcome_attribution.py`로 E154 public outcome attribution을 만들었다.

질문은 이것이었다.

`E154가 E158의 각 band에 떨어질 때, 그 결과는 E154가 새로 더한 body 때문인가, 아니면 이미 E144가 갖고 있던 inherited body 때문인가?`

결과:

- E154-vs-E95 unique moved cells: `294`.
- additive LogLoss segments: `479`.
- moved rows/subjects: `139` / `9`.
- component flip-benefit:
  - inherited E144 body: `3.292000000`.
  - E154 extra body: `0.255975083`.
  - E154 adjustment on E144 body: `0.203843941`.
- target flip-benefit: Q3 `1.316339056`, Q1 `0.861514603`, S3 `0.617644085`, S2 `0.502753066`, S4 `0.453568213`.
- public-free win mass:
  - global `0.728550`.
  - subject `0.601575`.
  - nearest-hard `0.666680`.
- branch-or-worse mass:
  - global `0.222590`.
  - subject `0.336125`.
  - nearest-hard `0.259610`.
- additive decomposition 검산: direct E154-vs-E95 hard-label delta와의 max error는 y=1 `1.75e-16`, y=0 `1.93e-16`.

현재 세계관을 다시 압축한다.

`E154는 여전히 지금 가장 정보량 높은 제출 후보지만, E154의 실패는 하나가 아니다. E154가 tie/small-loss에 들어가고 blame이 E154 extra/adjustment body에 있으면 E155가 의미 있는 amplitude-control이다. 하지만 branch-loss/hard-fail이 inherited E144 body에서 나오면 E155는 구조적으로 rescue가 아니다. 그 경우에는 E144 contrast를 보거나 이 branch를 닫아야 한다.`

지금 제출할 파일은 변하지 않는다. `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.

## 추가 관찰: E154 feedback 해석기를 실행 가능한 형태로 고정했다

`analysis_outputs/e160_e154_postfeedback_interpreter.py`를 만들었다.

질문은 이것이었다.

`E154 public score가 들어온 뒤, 우리가 즉석에서 해석을 바꾸지 않으려면 어떤 decision table을 미리 고정해야 하는가?`

결과:

- decision rows: `7`.
- E155 gate:
  - breakthrough/clean/micro win: `not_needed`.
  - tie: `information_only`.
  - small_loss: `information_only`.
  - branch_loss: `not_recommended`.
  - hard_fail: `not_recommended`.
- tie component read:
  - global: `e154_extra_body`.
  - subject: `e154_adjustment_on_e144_body`.
  - nearest-hard: `inherited_e144_body`.
- small_loss component read:
  - global: `e154_extra_body`.
  - subject/nearest-hard: `inherited_e144_body`.
- branch_loss/hard_fail component read:
  - all focus priors: `inherited_e144_body`.
- score probe:
  - `0.5763003660` -> `small_loss`.
  - `0.5762880000` -> `micro_win`.

현재 세계관을 다시 압축한다.

`E154가 tie/small_loss여도 E155는 clean rescue가 아니라 information-only amplitude contrast다. branch_loss/hard_fail이면 E155/E157/E156은 막힌다. 이제 E154 public feedback이 오면 손으로 해석하지 말고, 먼저 E160을 실행해야 한다.`

실행 명령:

```bash
python3 analysis_outputs/e160_e154_postfeedback_interpreter.py --score <PUBLIC_LB>
```

지금 제출할 파일은 여전히 `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` 하나다.

## 추가 관찰: E154의 위험 셀은 보이지만, 잘라내도 새 후보가 되지는 않는다

`analysis_outputs/e161_e154_inherited_body_pruning_audit.py`를 만들었다.

질문은 이것이었다.

`E159가 inherited E144 body blame을 보여줬다면, 그 위험 cell을 public-free prior로 미리 잘라내서 E154보다 더 좋은 후보를 만들 수 있는가?`

결과:

- pruning variants: `1608`.
- all-four health rows: `631`.
- control-grade rows: `299`.
- submission-grade rows: `0`.
- focus expected-risk 기준 E154보다 안전한 rows: `1226`.
- local all-minus 기준 E154보다 나은 rows: `180`.
- `2e-6` public-readable guardrail 기준 E154보다 나은 rows: `0`.
- best local delta vs E154: `-0.000000045921`.
- best focus expected-risk delta vs E154: `-0.000104369145`, 하지만 이 extreme prune은 health/local edge를 잃는다.

현재 세계관을 다시 압축한다.

`E154 내부의 위험 cell은 실제로 보인다. 그러나 그 위험을 잘라내는 순간 얻는 이득은 대부분 prior-risk 공간에서만 크고, public-readable probability edge로는 변환되지 않는다. 즉 plateau는 위험 cell 식별 부족이 아니라, 위험 감소를 충분한 local/public-safe movement로 번역하지 못하는 해상도 병목이다.`

따라서 E161은 새 submission을 만들지 않는다. E154가 여전히 다음 public sensor다. E161 pruning row들은 E154 feedback 이후 branch가 살아 있고 작은 component overextension만 의심될 때 사용할 diagnostic control이지, first-file replacement가 아니다.

## 추가 관찰: branch 후보 순위는 한두 개 hidden label 해상도 안에 있다

`analysis_outputs/e162_branch_readability_flip_thresholds.py`를 만들었다.

질문은 이것이었다.

`E154/E155/E157/E156/E161 같은 sibling control들이 너무 가깝다면, 그 가까움은 LogLoss가 실제로 보는 hidden row-target label 단위에서 얼마나 취약한가?`

결과:

- pairwise comparisons: `13`.
- 모든 live sibling/control pair에서 `2e-6` public-readable guardrail에 도달하는 데 필요한 top-swing cell 수: `1`.
- E154 vs E155:
  - moved cells `294`.
  - focus expected delta `+0.000000505`.
  - top1 swing `0.000010815`.
- E154 vs E144:
  - focus expected delta `+0.000000638`.
  - top1 swing `0.000014420`.
- E157 vs E155:
  - focus expected delta `-0.000000619`.
  - top1 swing `0.000002185`.
- E154 vs E95:
  - top1 swing `0.000015340`, 거의 E95가 mixmin에서 얻은 public edge 전체와 같은 크기다.

현재 세계관을 다시 압축한다.

`0.57629대 branch에서는 후보 간 평균 차이가 너무 작아서, 한 개 고영향 row-target label realization이 후보 순위보다 크다. 이 때문에 CV, prior, pruning, target-axis micro-control이 모두 그럴듯해 보여도 public에서는 안정적인 ranking 장치가 되지 않는다.`

따라서 다음 제출 후보는 바뀌지 않는다. E154는 "가장 나아 보여서"라기보다 "현재 branch 세계관을 가장 많이 가르는 센서"라서 먼저다. E155/E157/E156/E161은 E154 feedback 이후에만 의미가 있다.

## 추가 관찰: 이 취약성은 E154 sibling만의 문제가 아니다

`analysis_outputs/e163_candidate_edge_breadth_audit.py`를 만들었다.

질문은 이것이었다.

`E162의 one-cell fragility가 E154 sibling stack에만 생긴 지역 현상인가, 아니면 E95 이후 plateau 전체의 법칙인가?`

결과:

- audited pairs: `22`.
- known public transitions: `7`.
- 실제 public delta 전체를 top1 hard-label cell 하나로 움직일 수 있는 known transitions: `3/7`.
- top5 cells로 움직일 수 있는 known transitions: `5/7`.
- post-E95 live 후보 중 `2e-6` public-readable guardrail을 top1 cell 하나가 넘는 후보: `7/7`.
- mixmin vs a2c8:
  - actual delta `-0.0011326805`.
  - top1 swing `0.000046919`.
  - actual delta에 필요한 top cells `25`.
- E95 vs mixmin:
  - actual delta `-0.0000153107`.
  - top1 swing `0.000046477`.
  - actual delta에 필요한 top cells `1`.
- E101 vs E95:
  - actual delta `+0.0000090362`.
  - top1 swing `0.000011619`.
  - actual delta에 필요한 top cells `1`.
- E72 miss는 base에 따라 actual delta에 필요한 top cells가 `4` 또는 `6`뿐이다.

현재 세계관을 다시 압축한다.

`mixmin은 broad signal이었다. 하지만 E95 이후 frontier refinement는 broad signal이 아니라 high-leverage hidden label 몇 개의 해상도 안에서 흔들리는 calibration-tail surgery다. 그래서 E101처럼 방향은 맞아도 E95를 못 넘을 수 있고, E154/E155/E157/E156 같은 micro-control은 feedback 없이 안정적으로 rank할 수 없다.`

따라서 새 submission은 만들지 않는다. 지금 제출할 파일은 여전히 `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`다. 다만 이 파일도 "best일 가능성이 증명돼서"가 아니라 "repaired all-four branch가 실제 public hidden labels에서 살아 있는지 가장 많이 알려주는 센서"라서 제출 가치가 있다.

## 추가 관찰: broad escape branch는 아직 죽지 않았다

E163이 남긴 조건은 명확했다.

`post-E95 micro-control이 아니라, mixmin처럼 여러 hidden label을 동시에 요구하는 넓은 신호를 찾아야 한다.`

그래서 `analysis_outputs/e164_universe_broad_edge_screen.py`를 만들었다.

질문은 이것이었다.

`이미 만든 submission universe 안에 E95 이후에도 broad hard-label edge를 가진 후보가 남아 있는가?`

결과:

- tracked submission paths: `2052`.
- unique prediction tensors: `1977`.
- broad-edge rows vs E95: `198`.
- low-E72-axis broad rows: `193`.
- conservative candidate-gate rows: `192`.
- known public-bad rows that still pass broadness: `2`.

가장 강한 broad row는 `jepa/submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv`였다.

- focus expected delta vs E95: `-0.025880912`.
- cells to flip expected: `54`.
- top1/expected: `0.029985445`.
- moved cells: `1750`.

하지만 이걸 그대로 제출하면 안 된다. E164는 broadness가 필요조건임을 말했을 뿐이고, E72/LeJEPA처럼 public-bad인 row도 broadness를 통과했다.

그래서 `analysis_outputs/e165_broad_edge_bad_axis_geometry.py`를 붙였다.

질문은 이것이었다.

`broad candidate가 known public-bad/collapse geometry 안에 들어 있는가?`

결과:

- bad axes: `a2c8,raw05,stage2,ordinal,final9,e72,q2_bad,lejepa_bad,resid_bad`.
- scored rows: `205`.
- E164 candidate rows scored: `192`.
- geometry-health survivors: `90`.
- known public-bad broad controls: rejected.

즉, broad branch는 전부 죽지 않았다. 다만 raw amplitude가 너무 크다.

그래서 `analysis_outputs/e166_broad_survivor_scale_probe.py`를 만들었다.

질문은 이것이었다.

`E95에서 broad survivor 방향으로 아주 작게만 움직이면, broad edge는 남고 bad-axis 위험은 통제되는가?`

결과:

- source directions: `21`.
- scaled rows scored: `198`.
- negative-control scaled rows: `22`.
- negative-control sensor gates: `0`.
- scaled sensor-gate rows: `112`.
- material rows with scale `<=0.03`: `51`.
- materialized file: `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.

선택된 파일:

- source: `submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv`.
- scale: `0.01`.
- focus expected delta vs E95: `-0.000332077`.
- cells to flip expected: `74`.
- top1/expected: `0.023369627`.
- bad-span energy: `0.450742441`.
- max bad-axis: `q2_bad`, cosine `0.268538582`.
- mean/max abs logit move: `0.002243986` / `0.013580886`.
- cosine with E154/E101/mixmin: `0.061661852` / `-0.099145675` / `-0.137683489`.

현재 세계관을 다시 압축한다.

`E154 branch는 좁고 해상도 병목 안에 있다. E166 branch는 넓고 작다. E166은 점수 tweak가 아니라, E95가 놓친 broad latent branch가 아직 존재한다는 주장이다.`

따라서 다음 public 선택지는 둘로 갈라졌다.

- 보수적 해석 센서: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`.
- broad plateau-break 센서: `analysis_outputs/submission_e166_broadsurv_s0p01_d8bfa94b.csv`.

한 줄로 말하면:

`E154는 현재 세계관을 정밀하게 읽는다. E166은 현재 세계관을 깨려고 한다.`

## E167 업데이트: E166은 진짜인데 안전하지는 않다

가장 이상한 점:

`E166의 broad focus cell은 랜덤이 아니었다. 그런데 우리가 지금까지 안전하다고 믿어온 safety-atlas와는 반대로 갔다.`

실험:

`analysis_outputs/e167_broad_survivor_context_alignment.py`

E166 top-benefit `74` cells를 target-count preserving permutation null `3000`개와 비교했다.

결과:

- edge-like rate: `0.689189` vs null `0.470842`.
- between-train-runs rate: `0.797297` vs null `0.624658`.
- top-subject share: `0.243243` vs null `0.164563`.

즉 E166은 hidden row/block/calendar context를 실제로 건드린다.

하지만:

- all-veto-null rate: `0.297297` vs null `0.574158`.
- all-safe-density mean: `0.117097` vs null `0.243966`.
- E101-plausible mass: `0.238204` vs null `0.533727`.
- E72-active rate: `0.837838` vs null `0.670369`.

따라서 현재 세계관은 이렇게 바뀐다.

`E166은 broad latent hallucination이 아니다. 하지만 E154/E95 쪽 safety law가 인증한 후보도 아니다. E166은 "현재 safety atlas가 너무 보수적인가?"를 묻는 센서다.`

다음 행동:

E166은 제출할 수 있는 정보량 높은 파일이지만, 점수 기대값이 더 안전하다고 말할 수는 없다. public feedback 전에는 E166 scale-up이나 같은 계열 변형을 만들지 않는다.

제출 해석:

- E166이 E95를 이기면: hidden calendar context가 safety-atlas보다 강했고, broad branch를 amplitude/target/context별로 분해한다.
- E166이 지면: E72-active/low-veto-null conflict가 broad JEPA-like movement의 public-negative axis였다고 본다.

## E168-E169 업데이트: E166은 고칠 수 있었다

가장 이상한 점:

`E166은 안전하지 않았지만, 안전하게 만들려고 자르면 완전히 죽지는 않았다.`

E167 이후 가장 강한 부정 가설은 이것이었다.

`E166의 hidden-context signal과 safety-atlas divergence는 한 몸이다. 그러니 safety를 고치면 broad signal도 죽는다.`

E168은 이 가설을 직접 찔렀다.

실험:

`analysis_outputs/e168_e166_safety_context_decoupling.py`

핵심 mask는 단순했다.

- context_high = edge-like OR between-train-runs.
- safety = veto-null 또는 safe-density.

결과:

- decoupling-pass policies: `2`.
- `context_high__veto`: `904` cells, `193` rows.
- expected delta: `-0.000120457`.
- cells-to-flip: `32`.
- top1/expected: `0.048415`.
- edge-like: `0.610619`.
- between-train-runs: `0.819690`.
- veto: `1.0`.
- safe-density: `0.346150`.
- E72-active: `0.268805`.

즉 E166의 context signal은 safety divergence와 완전히 붙어 있지 않았다.

E169는 이 mask를 실제 submission tensor로 만들었다.

파일:

- `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv`.
- `analysis_outputs/submission_e169_ctx_high_density_p50_51110c7e.csv`.

가장 좋은 건 `ctx_veto`다.

- expected delta: `-0.000120457`.
- moved cells/rows: `904/193`.
- bad-span energy: `0.295326`.
- max bad cosine: `0.222381`.
- mean/max abs logit: `0.001096` / `0.010206`.
- Q2/S3 share: `0.347775`.
- cosine with E154/E101/mixmin: `0.087180` / `-0.021896` / `-0.020672`.

현재 세계관은 이렇게 바뀐다.

`raw E166은 broad latent가 진짜인지 묻는 공격적인 센서다. E169 ctx_veto는 그 broad latent가 safety-atlas와 공존할 수 있는지 묻는 더 균형 잡힌 센서다.`

다음 public 후보를 딱 하나 고르면 이제는 raw E166보다 `submission_e169_ctx_veto_c5e806e3.csv`가 더 합리적이다.

해석:

- E169가 E95를 이기면: broad hidden-context branch는 public-real이고, 필요한 것은 context-high/veto mask였다.
- E169가 E95보다 나쁘지만 E101 근처에서 버티면: broad branch는 살아 있으나 아직 public-tail selector가 모자란다.
- E169가 E101보다 나쁘면: E168 safety proxy가 틀렸거나, broad survivor branch 자체가 public-negative다.

## E170 업데이트: E169는 넓지만 아직 public hard-label 해상도 안에 있다

가장 이상한 점:

`E169는 broad repair인데도, public에서 읽히는 승패는 여전히 몇 개 hidden label에 걸려 있다.`

E170은 E169 제출 전 해석기를 먼저 고정했다.

실험:

`analysis_outputs/e170_e169_public_feedback_decoder.py`

결과:

- E169 vs E95 moved cells/rows: `904/193`.
- expected delta: `-0.000120457`.
- cells-to-flip expected: `32`.
- top1 swing: `0.000005832`.
- cells for `2e-6` guard: `1`.
- cells for E95-over-mixmin edge: `4`.
- between-train-runs share: `81.1%`.
- not-E72-active share: `73.7%`.
- high-density p50 sibling과의 차이: `10` Q2/S3 cells, expected delta `-0.000001377`.

이건 E169 해석을 더 좁힌다.

`E169는 raw E166보다 건강한 broad repair다. 하지만 public label 해상도 문제를 해결한 것은 아니다. 그래서 E169는 점수 기대값 순위가 아니라, context-high/veto broad latent가 public-real인지 묻는 센서다.`

다음 행동:

다음 broad-branch 제출 후보 하나를 고르면 여전히 `analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv`다. 다만 결과가 나오면 반드시 먼저 다음을 실행한다.

`python3 analysis_outputs/e170_e169_public_feedback_decoder.py --score <PUBLIC_LB>`

해석:

- `<=0.576261330`: broad breakthrough. E169를 새 anchor로 승격한다.
- `<=0.576276019`: clean win. target/context ablation으로 넘어간다.
- `<=0.576288330`: micro win. amplitude 증폭 금지, attribution 먼저.
- `<=0.576294330`: tie. E95 practical frontier 유지, raw E166은 information-only.
- `<=0.576300366`: small loss. high-density p50 금지, E154 vs raw E166은 질문 기준으로 선택.
- `<=0.576306641`: E101보다 나쁘지만 mixmin 근처. E169 demote, E154 우선.
- `>0.576306641`: branch loss/hard fail. E169/E166 same-family를 닫고 safety axis를 다시 만든다.

## E171 업데이트: E169의 몸통과 tail이 서로 다른 말을 한다

가장 이상한 점:

`E169 전체 body는 visible prior가 지지하지만, public 승패를 좌우할 top critical cells는 visible prior가 싫어한다.`

E171은 E170에서 드러난 약점을 직접 찔렀다.

실험:

`analysis_outputs/e171_e169_critical_cell_prior_audit.py`

결과:

- full E169 moved body under visible_mean:
  - mean delta vs E95: `-0.000022659`.
  - win rate: `0.868840`.
  - E95-edge-or-better rate: `0.638120`.
- subject prior:
  - mean delta `-0.000021115`.
  - win rate `0.853520`.
- focus_mean:
  - mean delta `-0.000053678`.
  - win rate `0.994460`.
- flank-only priors:
  - nearest_beta mean `+0.000005364`, win `0.388080`.
  - edge_endpoint_beta mean `+0.000005106`, win `0.389420`.
  - flank_mean mean `+0.000000790`, win `0.480740`.
- top critical support:
  - top1 visible support `0.098648`.
  - top4 `0.330699`.
  - top16 `0.266074`.
  - top32 `0.247434`.
- target-matched null:
  - top32 observed `0.247434`.
  - null mean `0.353573`.
  - z `-2.703`, p_low `0.001667`.

이건 현재 세계관을 더 정확하게 만든다.

`E169는 broad body hypothesis로는 살아 있다. 하지만 public에서 이길지 여부는 visible prior가 오히려 adverse하게 보는 top S1/Q3/S4/S2 hard-label tail에 걸려 있다.`

따라서 E169는 아직 다음 broad sensor로 가치가 있다. 하지만 이건 “안정적 기대점수 후보”가 아니라 “broad body와 critical tail 중 어느 쪽이 public을 지배하는지 묻는 센서”다.

해석:

- E169가 이기면: broad body prior가 top-tail visible adversity를 이긴 것이다.
- E169가 좁게 지면: broad branch 전체가 죽었다기보다 critical-cell tail이 public에서 adverse였다고 먼저 본다.
- E169가 mixmin보다 나쁘면: top-tail 문제가 아니라 body prior 자체가 public-misaligned였다고 본다.

## E172 업데이트: E169의 위험 tail은 몸통을 죽이지 않고 줄일 수 있다

가장 이상한 점:

`E169는 넓게 맞는 것처럼 보이는데, public을 결정할 수 있는 tail은 visible prior가 싫어한다. 그런데 이 둘은 완전히 붙어 있지 않았다.`

E172는 E171의 경고를 실제 intervention으로 바꿨다.

실험:

`analysis_outputs/e172_e169_critical_tail_rollback_probe.py`

결과:

- variants scored: `67`.
- stress-gate variants: `7`.
- materialized file: `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv`.
- 선택 policy: `visible_positive_all_keep0p25`.
- rollback cells: `410`.
- rollback 방식: visible-prior expected loss가 양수인 E169 movement를 `25%`만 남김.
- focus expected delta vs E95: `-0.000112695`.
- moved cells/rows: `904/193`.
- cells-to-flip expected: `30`.
- visible-prior p95:
  - E169 `+0.000010607`.
  - E172 `-0.000026683`.
- visible-prior worse-than-E101:
  - E169 `0.058545`.
  - E172 `0.000050`.
- bad-span energy:
  - E169 `0.295326`.
  - E172 `0.257874`.
- max bad cosine:
  - E169 `0.222381`.
  - E172 `0.142927`.

생각이 바뀐 점:

`E169는 best broad sensor였지만, E172가 더 나은 expected-score broad candidate다.`

E169의 몸통은 살아 있고, E171이 지적한 visible-prior adverse tail은 줄일 수 있었다. 이건 단순 shrink가 아니다. broad body는 유지하고 위험 셀만 damping한 것이다.

다음 행동:

딱 하나를 제출한다면 지금은 `analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv`가 더 낫다.

해석:

- E172가 E95를 이기면: broad context/veto body는 public-real이고, E171 visible-tail rollback이 missing constraint였다.
- E172가 tie/small loss면: broad branch는 살아 있지만 여전히 hidden public tail 해상도에 막혀 있다.
- E172가 mixmin보다 나쁘면: visible rollback이 과보정됐거나, broad body 자체가 public-misaligned다.

E169는 버리는 파일이 아니다. 다만 이제 역할이 바뀌었다. E169는 “unrolled body-vs-tail sensor”이고, E172는 “tail-repaired expected-score candidate”다.

## E173 업데이트: E172도 public hard-label 해상도 문제는 끝내지 못했다

가장 이상한 점:

`E172는 visible/flank prior tail을 크게 고쳤는데도, public-readable swing은 E169와 거의 같다.`

실험:

`analysis_outputs/e173_e172_public_feedback_decoder.py`

결과:

- E172 vs E95:
  - moved cells/rows `904/193`.
  - expected delta `-0.000112695`.
  - cells-to-flip expected `30`.
  - top1 swing `0.000005832`.
  - cells for `2e-6` guard `1`.
  - cells for E95-over-mixmin edge `4`.
- E172 vs E169:
  - rollback cells/rows `410/178`.
  - focus-prior expected cost `+0.000007762`.
  - cells-to-flip `3`.
  - rollback cost는 Q2/S2 쪽이 크고, Q1/Q3 rollback은 오히려 focus-prior favorable.
- prior-tail repair:
  - visible p95 `+0.000010607 -> -0.000026683`.
  - visible worse-than-E101 `0.058545 -> 0.000050`.
  - flank_mean mean `+0.000000777 -> -0.000035296`.
- context:
  - between-train-runs가 E172-vs-E95 expected edge의 `80.6%`.
  - not-E72-active cells가 `71.6%`.

생각이 바뀐 점:

`E172는 E169보다 더 좋은 expected-score 후보지만, 0.576 plateau의 핵심인 hidden hard-label resolution 병목은 그대로 남아 있다.`

즉 E172의 세계관은 이렇게 정리된다.

`broad context/veto body는 유지한다. visible-positive-loss tail은 줄인다. 하지만 public LB는 여전히 1~4개 high-swing hidden cells에 크게 흔들릴 수 있다.`

다음 행동:

E172를 제출하면 반드시 먼저 다음을 실행한다.

`python3 analysis_outputs/e173_e172_public_feedback_decoder.py --score <PUBLIC_LB>`

해석:

- `<=0.576276019`: tail repair가 public-real. E172를 새 broad anchor로 본다.
- `0.576288330..0.576294330`: tie. E95 practical frontier 유지. threshold tuning 금지.
- `0.576294330..0.576300366`: small loss. E169 자동 제출 금지, E154 또는 새 safety-axis를 선택.
- `>0.576306641`: E172/E169/E166 same-family broad lane expected-score followup을 닫는다.

## E174 업데이트: E172는 안전했지만 조금 과보수적이었다

내가 발견한 가장 이상한 점:

`E172는 visible-tail을 고쳤지만, 그 과정에서 recoverable body signal도 같이 너무 많이 접었다.`

실험:

`analysis_outputs/e174_e172_rollback_overcorrection_probe.py`

결과:

- `80`개 E172 rollback reopening 정책을 테스트.
- E174 gate 통과 `46`개.
- materialized:
  - `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`
- 선택 정책:
  - `reopen_focus_cost_top75_to1p0`
  - E172가 접었던 셀 중 focus recovery 상위 `75`개를 E169 쪽으로 완전히 되돌림.

핵심 수치:

- focus expected delta:
  - E172 `-0.000112695`
  - E174 `-0.000124367`
  - E174 vs E172 `-0.000011672`
- breadth:
  - moved cells/rows `904/193`
  - cells-to-flip `33`
  - top1/expected `0.046893`
- visible-tail:
  - visible mean `-0.000050633`
  - visible p95 `-0.000022709`
  - worse-than-E101 `0.000220`
- geometry:
  - bad-span energy `0.263996`
  - max bad cosine `0.163229`
  - Q2/S3 share `0.339597`

생각이 바뀐 점:

`E172의 방향은 맞았지만 keep 0.25는 유일한 안전점이 아니었다.`

E174는 E172보다 더 공격적이다. visible-tail guard는 살아 있지만, Q2/S3 share가 `0.34` guard 바로 아래라 margin은 얇다.

현재 최강 세계관:

`broad context/veto body는 살아 있고, visible-positive-loss tail은 줄여야 한다. 다만 모든 rollback cell을 똑같이 줄이면 body signal 일부를 과하게 잃는다. rollback cell 내부에도 JEPA-style energy ranking이 있다.`

다음으로 가장 정보량이 큰 행동:

딱 하나 제출한다면 지금은 `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`가 가장 날카롭다.

해석:

- E174가 E95/E172 기대보다 잘 나오면: E172는 과보수적이었고, partial reopening이 맞았다.
- E174가 tie/small loss면: broad branch는 여전히 hidden hard-label 해상도에 막혔거나, Q2/S3 reopening이 살짝 과했다.
- E174가 mixmin보다 나쁘면: 이 partial reopening family는 닫고, broad body 자체 또는 q2_bad axis를 다시 봐야 한다.

E172는 버리지 않는다. E174가 높은 기대값 후보라면, E172는 낮은 tail-risk contrast다.

## E175 업데이트: E174 점수 해석을 먼저 고정했다

내가 발견한 가장 이상한 점:

`E174는 E172보다 더 날카롭지만, public score 하나만 보고는 partial reopening 성공과 Q2/S3 과개방을 구분하기 어렵다.`

실험:

`analysis_outputs/e175_e174_public_feedback_decoder.py`

결과:

- report:
  - `analysis_outputs/e175_e174_public_feedback_decoder_report.md`
- E174 vs E95:
  - moved cells/rows `904/193`
  - expected focus delta `-0.000124367`
  - cells-to-flip `33`
  - top1 swing `0.000005832`
  - E95-over-mixmin edge를 설명하는 셀 수 `4`
- E174 vs E172:
  - changed cells/rows `75/65`
  - expected focus recovery `-0.000011672`
  - cells-to-flip `5`
  - top1 swing `0.000002996`
  - E95-over-mixmin edge를 설명하는 셀 수 `7`
- E174가 E172 대비 얻은 회복:
  - S3 `27.7%`
  - Q2 `25.3%`
  - S2 `23.0%`
  - S1 `12.6%`
  - not-E72-active cells `88.6%`
- E174가 E172 대비 쓴 tail margin:
  - visible p95 `+0.000003974`
  - worse-than-E101 probability `+0.000169869`

고정한 public band:

- `<=0.576276019`: E174를 broad anchor로 승격.
- `0.576276019..0.576288330`: micro win. partial reopening은 살아 있지만 아직 hidden-label 해상도 병목.
- `0.576288330..0.576300366`: E95 practical 유지. E172가 cleaner contrast.
- `>0.576300366`: E174 demote. top-N reopening siblings 금지.
- `>0.576306641`: E174/E172/E169 same-family reopening expected-score followup 닫기.

생각이 바뀐 점:

`E174는 제출 후보이지만, 그 점수는 tuning permission이 아니라 가설 관측값이다.`

다음 행동:

E174를 제출했다면 먼저 이것부터 실행한다.

`python3 analysis_outputs/e175_e174_public_feedback_decoder.py --score <PUBLIC_LB>`

그 전에는 E172/E169/E166/E154 중 다음 파일을 고르지 않는다.

## E176 업데이트: E174 안에서 Q2만 살짝 덜 열면 더 좋은 risk-adjusted 후보가 된다

내가 발견한 가장 이상한 점:

`E174는 top-75 full reopening 자체가 정답이 아니었다. Q2만 조금 덜 열어도 edge는 거의 유지되고 q2_bad/Q2S3 위험이 줄었다.`

실험:

`analysis_outputs/e176_e174_component_ablation_probe.py`

결과:

- `162`개 component ablation/damping 후보를 테스트.
- E176 gate 통과 `12`개.
- materialized:
  - `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- 선택 정책:
  - `ablate_q2_to0p75`
  - E174가 reopened한 Q2 cells만 keep `1.0 -> 0.75`.

핵심 수치:

- focus expected delta:
  - E174 `-0.000124367`
  - E176 `-0.000123384`
  - E176 vs E174 `+0.000000983`
  - E176 vs E172 `-0.000010689`
- breadth:
  - moved cells/rows `904/193`
  - cells-to-flip `33`
  - top1/expected `0.047267`
- risk 개선:
  - bad-span energy `0.263996 -> 0.261687`
  - max bad cosine `0.163229 -> 0.158126`
  - Q2/S3 share `0.339597 -> 0.334753`
  - visible p95 `-0.000022709 -> -0.000023096`
  - worse-than-E101 `0.000220 -> 0.000192`

생각이 바뀐 점:

`partial reopening은 맞아 보이지만, Q2는 S3/S2/S1과 같은 강도로 열면 안 된다.`

현재 최강 세계관:

`broad context/veto body는 살아 있고, visible-positive-loss tail은 줄여야 한다. 그 뒤 일부 rollback cell은 다시 열어야 하지만, Q와 S는 같은 amplitude law를 쓰면 tail risk가 커진다. E176은 S3/S2/S1-heavy partial reopening + Q2 under-open 법칙이다.`

다음으로 가장 정보량이 큰 행동:

딱 하나 제출한다면 이제는 E174보다 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`가 더 균형 잡힌 선택이다.

해석:

- E176이 좋아지면: Q/S-asymmetric partial reopening이 맞다.
- E176이 tie/small loss면: broad branch는 여전히 hidden hard-label 해상도에 막혔거나 partial reopening 자체가 과했다.
- E176이 나쁘고 E174가 나중에 좋으면: Q2 full reopening이 public-real이었다.
- E176이 mixmin보다 나쁘면: E174/E176/E172 same-family broad reopening은 기대 점수 후보가 아니라 실패한 latent family로 본다.

## E177 업데이트: E176 점수 해석을 먼저 잠갔다

가장 이상한 점:

E176은 E174보다 더 균형 잡힌 후보지만, E176과 E174의 차이는 너무 작다. E176-vs-E174는 Q2 `21` cells뿐이고 expected focus cost는 `+0.000000983`, top1 swing은 `0.000000832`다.

즉 E176 public 점수가 나오면 “Q2 keep을 0.65로 할까 0.85로 할까” 같은 연속 튜닝을 할 수 있는 정보량이 아니다. 그 점수는 Q2 amplitude 추정치가 아니라, Q/S-asymmetric partial reopening 세계관을 살릴지 죽일지 보는 센서다.

실험:

- `analysis_outputs/e177_e176_public_feedback_decoder.py`
- report: `analysis_outputs/e177_e176_public_feedback_decoder_report.md`

관측:

- E176-vs-E95:
  - moved cells/rows `904/193`
  - expected focus delta `-0.000123384`
  - cells-to-flip `33`
  - top1 swing `0.000005832`
  - E95-over-mixmin edge를 덮는 cells `4`
- E176-vs-E174:
  - Q2 `21` cells
  - expected focus cost `+0.000000983`
  - cells-to-flip `2`
  - top1 swing `0.000000832`
- E176-vs-E172:
  - expected focus recovery `-0.000010689`
  - S3/S2/Q2/S1 순으로 회복

해석 band:

- `<=0.576276019`: E176 broad/Q2-underopen anchor 검증
- `0.576276019..0.576288330`: micro-win, 아직 underresolved
- `0.576288330..0.576300366`: E95 practical, E172/E174는 contrast sensor
- `>0.576300366`: E176 demote
- `>0.576306641`: same-family reopening expected-score follow-up close

다음 행동:

E176을 제출한다면 결과는 반드시 다음으로 먼저 읽는다.

`python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>`

그 전에는 Q2 keep-factor sibling을 만들지 않는다. E174는 “full Q2가 public-real인가?”를 나중에 묻는 contrast이지, E176 결과를 보고 자동으로 따라갈 후보가 아니다.

## E178 업데이트: plateau의 가장 압축된 법칙

내가 발견한 가장 이상한 점:

`broad signal은 분명히 있는데, public에서 살아남는 edge는 몇 개 hard-label cell 해상도에 갇힌다.`

실험:

- `analysis_outputs/e178_current_plateau_law_audit.py`
- report: `analysis_outputs/e178_current_plateau_law_report.md`

결과:

- E101 public `0.5763003660`은 E95보다 `+0.0000090362` 나쁘고 mixmin보다 `-0.0000062745` 좋다.
- E166 broad raw edge는 `-0.000332077`, E95-over-mixmin public edge의 `21.689x`.
- E176 edge는 `-0.000123384`, E95 edge의 `8.059x`.
- 그런데 E176은 top hard-label `4` cells만으로 E95 edge 전체가 흔들리고, E101은 `2` cells면 된다.
- E98 best known-LB selector p90 error는 E95 edge의 `53.33x`.

생각이 바뀐 점:

`0.57629 plateau는 신호 없음이 아니다. broad body는 있다. 병목은 그 broad body를 public-safe hard-label/tail calibration으로 변환하는 해상도다.`

현재 최강 세계관:

`이 대회는 모델 capacity보다 public-tail resolution 문제다. E95 이후 후보들은 평균적으로 좋아 보여도, 몇 개 high-swing S/Q tail cell과 target별 calibration이 public을 결정한다. 그래서 CV가 조금 좋아진 파일, broad expected edge가 큰 파일, Q2/S3를 더 미세하게 만진 파일이 바로 frontier가 되지 않는다.`

다음으로 가장 정보량이 큰 행동:

새 파일을 만들지 않는다. 지금 한 장만 제출한다면 여전히:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

의도:

`broad hidden body는 살리고, Q2는 S3/S2/S1보다 덜 열어야 한다는 Q/S-asymmetric partial reopening 세계관을 테스트한다.`

기대 public 반응:

- `<=0.576276019`: E176 law가 readable scale로 맞다.
- `0.576288330..0.576300366`: plateau law가 유지된다. E95 practical, E172/E174는 contrast.
- `>0.576300366`: E176 demote.
- `>0.576306641`: same-family partial reopening lane을 닫는다.

## E179 업데이트: E176은 몸통은 보이지만 결정 셀은 아직 안 보인다

내가 발견한 가장 이상한 점:

`E176의 전체 방향과 Q2 damping은 train-derived prior로 지지되는데, 실제 public edge를 뒤집을 수 있는 top hard-label cells는 오히려 약하게 보인다.`

실험:

- `analysis_outputs/e179_e176_critical_cell_visibility_audit.py`
- report: `analysis_outputs/e179_e176_critical_cell_visibility_report.md`

결과:

- E176 full body visible-mean delta: `-0.000050824`.
- visible-mean simulated win rate: `0.999080`.
- E176-vs-E174 Q2 damping visible-mean delta: `-0.000000191`.
- Q2 damping support: `0.690495`, hard support rate `0.904762`.
- 하지만 top4 decisive-cell support는 `0.330699`.
- top33 expected-flip support는 `0.245771`, target-matched null `0.335713`보다 낮다 (`p_low=0.014667`).

생각이 바뀐 점:

`E176은 더 강해졌다기보다 더 정확히 정의됐다. 몸통과 Q2-underopen 가설은 local evidence가 있지만, public을 실제로 가르는 top-cell label은 아직 local에서 못 본다.`

다음으로 가장 정보량이 큰 행동:

여전히 새 파일을 만들지 않는다. 한 장만 낸다면:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

단, 의도는 "이길 것 같은 파일"보다 더 좁다.

`body-supported / Q2-underopened broad law가 hidden public tail과 맞는지 관측하는 파일`이다.

실패 시 해석:

- tie/small-loss: broad body는 맞아도 decisive-cell tail을 못 맞힌 것일 수 있다.
- worse than E101: partial-reopen family 자체를 demote한다.
- win: visible-prior가 약하게 본 top cells에서 hidden public tail이 E176 쪽으로 실현된 것이다.

## E180 업데이트: E179의 top-cell 약함은 hard veto가 아니다

내가 발견한 가장 이상한 점:

`성공한 E95 hardtail도 top4 visible support가 겨우 0.100896이었다.`

실험:

- `analysis_outputs/e180_known_anchor_decisive_cell_visibility.py`
- report: `analysis_outputs/e180_known_anchor_decisive_cell_visibility_report.md`

결과:

- E95-vs-mixmin public-positive top4 support: `0.100896`.
- E101-vs-mixmin public-positive top4 support: `0.100896`.
- mixmin-vs-a2c8 public-positive top4 support: `0.310904`.
- E176 top4 support: `0.330699`.
- E176은 known-winner top4 평균 `0.170898`과 max `0.310904`보다 높다.
- 하지만 visible-prior all-moved sign accuracy는 known anchors에서 `0.5`뿐이다.
- 실패한 E72는 observed-adverse support가 높다: `0.793304` vs mixmin, `0.696441` vs E95.
- 반면 E101-vs-E95 near loss는 observed-adverse top4 support도 `0.100896`이라 frontier boundary는 여전히 안 보인다.

생각이 어떻게 바뀌었는지:

`E179는 E176을 죽이는 근거가 아니었다. E179/E180을 합치면 결론은 “E176 top cell이 나쁘다”가 아니라 “visible prior는 body/tail diagnostic이지 frontier decisive-cell selector가 아니다”다.`

현재 최강 세계관:

`0.57629 plateau는 broad body signal 부족이 아니라, public을 실제로 가르는 high-swing cell direction을 visible context가 안정적으로 못 보는 문제다. E72 같은 큰 실패는 보이지만, E95/E101/E176 같은 frontier boundary는 아직 안 보인다.`

다음으로 가장 정보량이 큰 행동:

E176을 후보에서 내리지 않는다. 한 장만 제출한다면 여전히:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

단, E176을 “visible top-cell certified”라고 부르지 않는다. 이 파일은:

`body-supported + Q2-underopened broad law가 hidden public decisive cells와 맞는지 묻는 센서`

다음 local 연구 질문:

`visible prior보다 더 나은 decisive-cell representation을 만들 수 있는가?`

## E181 업데이트: E176은 representation-wide best가 아니다

내가 발견한 가장 이상한 점:

`visible/body 관점에서는 E176이 살아 있는데, current-anchor binary hidden-label worlds는 E176보다 E154/E144를 더 좋아한다.`

실험:

- `analysis_outputs/e181_e176_binary_world_counterprior_audit.py`
- report: `analysis_outputs/e181_e176_binary_world_counterprior_report.md`

결과:

- 기존 binary frontier-box worlds를 현재 known public anchors 전체로 다시 ranking했다.
- best current-anchor residual world: sum abs residual `0.000518340`, max abs residual `0.000194476`.
- best-5 residual worlds에서 E176은 E95 대비 평균 `+0.000003920`, negative rate `0.400`.
- best-10 residual worlds에서 E176은 평균 `+0.000007442`, negative rate `0.300`.
- 반면 E154와 E144는 best-5 residual worlds에서 모두 E95보다 좋다.
- E154 best-5 mean: `-0.000051451`.
- E144 best-5 mean: `-0.000051445`.
- E176 top-cell world support는 best-5 top4 `0.433633`이지만 top16은 `0.221275`로 약하다.

생각이 어떻게 바뀌었는지:

`E176은 아직 살아 있지만, “가장 강하게 지지되는 후보”라고 일반화하면 안 된다. 더 정확한 말은 E176은 visible-body/Q2-underopen worldview의 센서이고, binary hidden-world worldview는 E154/E144 쪽을 가리킨다는 것이다.`

현재 최강 세계관:

`0.57629 plateau는 하나의 selector가 약해서 생긴 게 아니라, latent view들이 서로 다른 세계를 가리키기 때문에 생긴다. visible priors는 broad body와 Q2 damping을 보지만, binary public-anchor worlds는 repaired narrow branch를 본다. 이 충돌이 풀리지 않으면 CV나 단순 blend는 계속 0.576 근처에서 흔들린다.`

그 세계관을 죽일 수 있는 가장 작은 실험:

`current anchors를 직접 반영한 binary-world pool을 새로 만들고, E176/E154/E144를 명시적 objective로 넣는다. 새 pool에서도 E154/E144가 one-sided이고 E176이 mixed/adverse면 E176 우선순위를 내려야 한다. 반대로 새 pool에서 E176이 살아나면 E181은 stale-world counterprior였던 것이다.`

다음으로 가장 정보량이 큰 행동:

제출 파일을 새로 만들지 않는다. 다음 local 실험은:

`E182: refreshed current-anchor binary-world stress with explicit E176/E154/E144 objectives`

현재 제출 후보 해석:

- E176: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- 의도: visible-body/Q2-underopen 세계관을 묻는 센서.
- 기대 public 반응: 이기면 E181 binary counterprior가 stale이거나 너무 보수적이었다는 뜻.
- 실패 시 해석: current-anchor binary-world counterprior가 맞았을 가능성이 커지고, E154/E144 branch를 다시 최상위로 올려야 한다.

## E182 업데이트: current-anchor binary world도 아직 한쪽을 못 고른다

내가 발견한 가장 이상한 점:

`E181은 E154/E144 쪽을 가리켰지만, current anchors로 binary world를 새로 만들고 E176/E154/E144를 직접 압박하면 셋 다 이기는 세계와 지는 세계가 나온다.`

실험:

- `analysis_outputs/e182_current_anchor_binary_world_refresh.py`
- report: `analysis_outputs/e182_current_anchor_binary_world_refresh_report.md`

결과:

- E101 public `0.5763003660`을 포함한 current anchors로 다시 MILP world를 만들었다.
- scenario fit max residuals: `0.0000784319`, `0.0000513148`, `0.0000762925`.
- strict residual-budget range incumbent rate: `0.233`.
- objective-pressure worlds에서 E176/E154/E144 zero-crossing rate: `1.000` / `1.000` / `1.000`.
- pressure span:
  - E176: `-0.000421216..+0.000254123`.
  - E154: `-0.00109286..+0.000923535`.
  - E144: `-0.000992245..+0.000838041`.

생각이 어떻게 바뀌었는지:

`E181은 E176을 보편 최강 후보에서 끌어내리는 데는 성공했지만, E154/E144를 자동 승격시키는 데는 실패했다. 새로 만든 current-anchor world에서도 hidden label space는 여전히 E176 쪽 세계와 E154/E144 쪽 세계를 모두 허용한다.`

현재 최강 세계관:

`0.57629 plateau는 candidate ranking 실패라기보다 hidden-label sign underidentification이다. public anchors는 known score들을 frontier scale로 맞추게 해주지만, 다음 live branch의 부호를 고정할 만큼 충분히 세계를 줄이지 못한다.`

그 세계관을 죽일 수 있는 가장 작은 실험:

`새 public feedback을 하나 더 얻거나, public 없이 high-swing decisive cell의 방향을 E176/E154/E144 사이에서 5e-6 이하 오차로 가르는 독립 representation을 만든다. 둘 중 하나 없이는 same-anchor inverse world만으로 우선순위를 뒤집을 수 없다.`

다음으로 가장 정보량이 큰 행동:

새 submission은 만들지 않는다. 한 장을 고른다면 여전히 질문을 먼저 정해야 한다.

- visible-body/Q2-underopen 세계관을 물을 거면 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`.
- repaired-branch 세계관을 물을 거면 `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`나 `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`에 먼저 E177/E160급 decoder를 붙인다.

제출 후보 해석:

E182 이후 E176, E154, E144 중 어느 것도 “인증된 expected-score 파일”이 아니다. 다음 제출은 점수 예측이 아니라 어느 hidden world가 public에서 실현되는지 보는 센서다.

## E183 업데이트: visible prior는 branch selector가 아니라 anti-selector다

내가 발견한 가장 이상한 점:

`E182에서 후보가 좋아지는 favorable pressure branch를 train-derived visible/subject/flank prior가 전혀 고르지 못한다. 세 후보 E176/E154/E144 모두에서 local/visible prior는 오히려 adverse branch를 고른다.`

실험:

- `analysis_outputs/e183_pressure_world_branch_anatomy.py`
- report: `analysis_outputs/e183_pressure_world_branch_anatomy_report.md`

결과:

- visible-mean favorable-branch preference:
  - E176: `0.000`
  - E154: `0.000`
  - E144: `0.000`
- subject prior와 flank-mean prior도 셋 모두 `0.000`.
- support-gap coefficient-weighted mean:
  - E176: `0.797945`
  - E154: `0.973558`
  - E144: `0.888923`
- average differing moved cells:
  - E176: `601.7`
  - E154: `282.7`
  - E144: `164.0`
- E176은 global prior만 favorable branch를 `1.000` 비율로 선호하지만, subject/flank/visible prior는 모두 반대다.

생각이 어떻게 바뀌었는지:

`visible prior는 후보 body의 건강 상태를 보는 데는 쓸 수 있지만, E182 pressure branch의 부호를 고르는 데는 오히려 반대 방향으로 작동한다. 따라서 E176이든 E154/E144든 visible-prior 인증 후보라고 부르면 안 된다.`

현재 최강 세계관:

`0.57629 plateau는 hidden-label sign underidentification이고, 지금의 visible/subject/flank prior는 그 sign을 풀지 못한다. 더 나쁘게는 branch-level에서는 anti-selector처럼 작동한다.`

그 세계관을 죽일 수 있는 가장 작은 실험:

`visible prior가 아닌 새로운 decisive-cell representation을 만들고, E182 pressure branch labels를 held-out/anchor-free 방식으로 예측하게 한다. 그 representation이 E176/E154/E144 중 하나의 favorable branch를 고르고 나중 public feedback과 맞으면 H177은 약해진다.`

다음으로 가장 정보량이 큰 행동:

새 submission은 만들지 않는다. 다음 행동은 두 갈래다.

- 제출 슬롯을 쓴다면, E176/E154/E144 중 하나를 “점수 후보”가 아니라 worldview sensor로 고르고 pre-registered decoder를 붙인다.
- local 실험을 계속한다면, visible prior와 독립적인 decisive-cell/pressure-branch representation을 만든다.

제출 후보 해석:

E183 이후 한 장만 고르라고 해도 답은 “인증된 후보”가 아니라 “어떤 세계관을 물을지”다.

- visible-body/Q2-underopen을 묻기: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- repaired-branch를 묻기: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv` 또는 `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`

실패 시 해석:

어느 파일이 지더라도 바로 같은 family sibling으로 도망가면 안 된다. 그 결과는 candidate quality보다 pressure-branch hidden labels가 어느 쪽이었는지를 먼저 말한다.

## E184 업데이트: known public motif도 아직 branch selector가 아니다

내가 발견한 가장 이상한 점:

`visible prior를 버리고 known public transition metadata로 selector를 만들어도 안정적인 branch 선택이 안 된다. 더 이상한 점은 signal이 없다는 게 아니라 polarity가 뒤집혀 보이고, feature set에 따라 E176/E154/E144 favorable branch 선택이 전부 뒤집힌다는 것이다.`

실험:

- `analysis_outputs/e184_public_anchor_motif_pressure_selector.py`
- report: `analysis_outputs/e184_public_anchor_motif_pressure_selector_report.md`

결과:

- best direct pair-LOO:
  - model: `meta_public_axis_plus_swing`
  - sign accuracy: `0.333`
  - AUC: `0.425`
- best direct family-level:
  - sign accuracy: `0.600`
  - AUC: `0.178`
- polarity-inverted pair signal은 강해 보일 수 있다.
  - best-polarity pair accuracy: `1.000`
  - 하지만 family best-polarity accuracy: `0.600`
- live pressure branch preference:
  - `meta_core`: favorable branch rate `0.000`
  - `meta_public_axis`: `1.000`
  - `meta_public_axis_plus_support_label`: `1.000`
  - `meta_public_axis_plus_swing`: `0.000`

생각이 어떻게 바뀌었는지:

`known public anchors에는 분명 residue signal이 있다. 하지만 그 signal은 아직 invariant가 아니다. polarity를 뒤집어야 pair가 맞거나, public-axis feature를 넣으면 branch 선택이 전부 반대로 바뀐다. 이건 selector가 아니라 shortcut/collapse 냄새가 난다.`

현재 최강 세계관:

`0.57629 plateau는 public anchor 몇 개로 shallow motif를 학습해 풀 수 있는 문제가 아니다. 현재 public observations는 hidden world를 줄여주지만, pressure branch sign을 안정적으로 고정할 만큼 충분한 invariant를 주지 못한다.`

그 세계관을 죽일 수 있는 가장 작은 실험:

`cell metadata classifier가 아니라 structural target을 만든다. 예를 들어 pressure-branch labels를 직접 쓰지 않고, held-out block/target transition state 또는 binary-world ensemble에서 반복적으로 살아남는 cell-state를 target representation으로 예측한다. 그 representation이 LOO/LOFO polarity를 미리 고정한 채 public anchors와 pressure branches를 동시에 설명하면 E184의 실패가 약해진다.`

다음으로 가장 정보량이 큰 행동:

새 submission은 만들지 않는다. 다음 local 실험은 shallow public-anchor classifier가 아니라 structural pressure-cell representation 쪽으로 가야 한다.

제출 후보 해석:

E184 이후에도 제출 후보 순위는 바뀌지 않는다.

- E176: visible-body/Q2-underopen worldview sensor.
- E154/E144: repaired-branch worldview sensor.
- 어느 쪽도 E184로 인증되지 않았다.

## E185/E186 업데이트: pair-level signal은 살아있지만 geometry가 병목이다

내가 발견한 가장 이상한 점:

`known public LB pair에는 cell metadata보다 강한 신호가 있다. 그런데 unconstrained decoder는 같은 pair의 양방향을 동시에 좋게 보는 reciprocal collapse를 일으킨다. 이건 점수 예측 문제가 아니라 representation geometry 문제다.`

실험:

- `analysis_outputs/e185_known_lb_pair_structural_decoder.py`
- `analysis_outputs/e186_antisymmetric_pair_decoder.py`
- reports:
  - `analysis_outputs/e185_known_lb_pair_structural_decoder_report.md`
  - `analysis_outputs/e186_antisymmetric_pair_decoder_report.md`

결과:

- E185 best file-LOO:
  - `shape_support_public_axis`
  - overall accuracy `0.811`
  - frontier accuracy `0.833`
  - E95-edge accuracy `0.714`
  - but E95-edge reciprocity MAE `0.081`
- E186 antisymmetric file-LOO:
  - `shape_support`
  - overall accuracy `0.795`
  - frontier accuracy `0.867`
  - micro accuracy `0.8125`
  - E95-edge accuracy `0.857`
  - reciprocity MAE `0`
- E186 branch decision:
  - E176 favorable pressure-min branch: selected `3/3`
  - E144/E154 favorable branch: rejected `3/3`

생각이 어떻게 바뀌었는지:

`0.57629 plateau는 signal absence가 아니다. pair-level public response signal은 있다. 문제는 그 signal을 action으로 바꾸는 representation geometry와 E95/E101 같은 exact frontier boundary calibration이다.`

현재 최강 세계관:

`E176은 visible-body/Q2-underopen sensor일 뿐 아니라, antisymmetric known-LB pair geometry에서도 가장 일관된 live branch다. 단, support-based decoder가 E95/E101 boundary를 틀리므로 인증 후보는 아니다.`

다음으로 가장 정보량이 큰 행동:

한 장만 제출한다면 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`다. Public LB가 좋아지면 E176 broad/Q2-underopen + antisymmetric-pair worldview가 강화된다. 나빠지면 E186은 known-anchor overfit 또는 branch shortcut으로 내려가고, 다음은 pair-LB decoder가 아니라 structural target representation으로 돌아가야 한다.

## E187/E188 업데이트: support decoder는 selector가 아니라 충돌하는 센서다

내가 발견한 가장 이상한 점:

`shape_only는 E95/E101 경계를 맞히고 E176도 고른다. support를 넣으면 wider edge stress는 좋아지지만, E95/E101을 거의 확신 있게 반대로 찍는다. 더 이상한 것은 이 오판이 특정 support family 하나가 아니라 support 전반에 퍼져 있다는 점이다.`

실험:

- `analysis_outputs/e187_e95_e101_boundary_miss_anatomy.py`
- `analysis_outputs/e188_shape_support_logit_blend_stress.py`
- reports:
  - `analysis_outputs/e187_e95_e101_boundary_miss_anatomy_report.md`
  - `analysis_outputs/e188_shape_support_logit_blend_stress_report.md`

결과:

- E187:
  - `shape_only` exact E95/E101 file-LOO accuracy `1.000`, E95 mean probability `0.762677`
  - support-containing variants exact E95/E101 accuracy `0.000`
  - support variants often wider E95-edge accuracy `0.857143`
  - adverse E95 contribution is distributed across flank/visible/subject/focus/nearest/global/all-prior support families
- E188:
  - action-grade blend rows `0`
  - all support variants have best exact-boundary row at `alpha=0.0`
  - first exact-boundary failure alpha `0.170..0.285`

생각이 어떻게 바뀌었는지:

`E186의 좋은 점은 antisymmetric geometry였지 support feature 전체가 아니다. support는 public-like residue를 들고 있지만 tight frontier boundary에서는 방향이 다른 shortcut이다. 그래서 E176을 고르는 support score는 auxiliary evidence일 뿐, selector가 아니다.`

현재 최강 세계관:

`0.57629 plateau는 wider edge signal과 exact frontier boundary signal이 서로 다른 latent view에서 나온다. shape geometry는 tight boundary에 건강하지만 edge stress가 약하고, support geometry는 wider edge에 강하지만 tight boundary를 깬다. 현재 병목은 이 둘을 섞는 문제가 아니라, 둘 중 무엇이 hidden public cell labels에 가까운지 판별할 structural target이 없다는 점이다.`

다음으로 가장 정보량이 큰 행동:

제출 후보는 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` 하나다. 단, 제출 이유는 “support decoder가 인증했다”가 아니라 “shape-only도 E176을 고르고, visible-body/Q2-underopen worldview가 아직 살아 있으며, public feedback이 가장 많은 세계관을 죽일 수 있다”로 좁혀졌다.

## E189 업데이트: support의 정체는 broad selector가 아니라 E72 오염 센서다

내가 발견한 가장 이상한 점:

`support가 wider E95-edge stress를 고치는 것처럼 보였지만, 실제로 고친 row는 전부 E72-neighbor였다. 반대로 shape-only가 support를 이긴 row는 전부 exact E95/E101 boundary였다. 즉 둘은 같은 문제를 다르게 푸는 것이 아니라, 서로 다른 숨은 센서를 보고 있다.`

실험:

- `analysis_outputs/e189_shape_support_disagreement_atlas.py`
- report: `analysis_outputs/e189_shape_support_disagreement_atlas_report.md`

결과:

- primary file-LOO E95-edge slice:
  - support rescue: `6`
  - shape-only win: `4`
- support rescue:
  - E72-frontier-neighbor share: `1.000`
  - exact E95/E101 share: `0.000`
- shape-only win:
  - exact E95/E101 share: `1.000`
  - E72-frontier-neighbor share: `0.000`
- filename gate:
  - E95-edge accuracy `1.000`
  - frontier accuracy `0.933333`
  - 하지만 live candidate에는 E72/E95/E101 filename identity가 없으므로 제출 규칙이 아니다.

생각이 어떻게 바뀌었는지:

`support-heavy decoder는 넓은 의미의 public selector가 아니다. 지금 관측된 useful part는 E72-contamination correction이다. E95/E101 같은 tight hardtail boundary에서는 shape-only가 더 건강하다. 따라서 E186에서 E176을 지지한 support evidence는 더 약해졌고, auxiliary sensor로만 남는다.`

현재 최강 세계관:

`0.57629 plateau는 하나의 selector가 모자란 문제가 아니라, 서로 다른 hidden sensor들이 각자 다른 boundary를 맞히는 문제다. support는 E72 오염을 보고, shape는 tight hardtail 경계를 본다. 우리가 아직 못 가진 것은 live sample/candidate에서 어느 센서를 믿어야 하는지 알려주는 구조적 E72-contamination detector다.`

그 세계관을 죽일 수 있는 가장 작은 실험:

`filename을 쓰지 않고 movement shape, target-axis, bad-axis, row/block context만으로 E72-neighbor contamination을 예측하는 detector를 만든다. 그 detector가 E72 rescue row를 잡고 E95/E101 row를 피하면서 live branch ranking까지 안정화하면 E189의 "support는 identity shortcut" 결론이 약해진다.`

다음으로 가장 정보량이 큰 행동:

새 submission은 만들지 않는다. 다음 제출 후보는 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`지만, 이유는 좁아졌다.

- 남은 근거: shape-only도 E176을 고른다.
- 남은 근거: broad/Q2-underopen worldview가 아직 살아 있다.
- 빠진 근거: support-heavy decoder가 E176을 인증했다는 해석.

제출 후보 해석:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`는 expected-score 인증 파일이 아니라, broad/Q2-underopen 세계관을 public에 묻는 센서다. Public LB가 좋아지면 E176 세계관과 shape-only branch sensor가 강화된다. 나빠지면 support를 더 섞는 쪽이 아니라, E72-contamination detector나 repaired-branch worldview 쪽으로 돌아가야 한다.

## E190 업데이트: filename-free E72 detector는 diagnostic이지 gate가 아니다

내가 발견한 가장 이상한 점:

`E72-neighbor는 파일명 없이도 어느 정도 구조적으로 보인다. 그런데 support feature를 많이 넣는 순간 exact E95/E101도 E72-contamination처럼 보인다. support가 고치는 문제와 support가 망치는 문제가 같은 feature view 안에서 분리되지 않는다.`

실험:

- `analysis_outputs/e190_e72_contamination_detector.py`
- report: `analysis_outputs/e190_e72_contamination_detector_report.md`

결과:

- E72-neighbor detection, pair-LOO:
  - best view: `shape_target_context_abs`
  - AUC `0.978836`
  - AP `0.809524`
  - top-k recall `0.666667`
- any-file LOO:
  - E72 자체를 hold out하면 positive가 모두 사라진다.
  - skipped positive rows `6`
- exact E95/E101 false positive:
  - `shape_target_context_abs`: `0.161306`
  - support/all views: `0.957..0.975`
- live branch:
  - E176 contamination score는 모든 view에서 거의 0.
  - E176은 non-E72 p95나 positive threshold를 한 번도 넘지 않는다.

생각이 어떻게 바뀌었는지:

`E72 contamination이라는 구조는 실제로 있다. 하지만 현재 detector는 support를 다시 살릴 만큼 건강하지 않다. support-rich view는 E189/E187의 실패를 그대로 반복한다. E176은 E72-contaminated branch가 아니므로 support로 보강할 이유가 더 약해졌다.`

현재 최강 세계관:

`support는 E72 오염 센서로 남지만, E176의 세계관은 support가 아니라 shape/broad-Q2-underopen 쪽이다. 0.57629 병목은 support를 잘 섞는 문제가 아니라, E72 오염과 tight hardtail boundary를 동시에 분리하는 invariant representation이 없다는 문제다.`

그 세계관을 죽일 수 있는 가장 작은 실험:

`E72 positive가 한 파일에만 묶이지 않도록 one-class/contrastive contamination target을 만들거나, exact E95/E101 false positive를 objective에 직접 넣은 detector를 만든다. 그 detector가 E72 recall을 유지하면서 E95/E101을 낮게 두고 live branch를 안정적으로 분리하면 E190의 gate 실패가 약해진다.`

다음으로 가장 정보량이 큰 행동:

새 submission은 만들지 않는다. 제출 후보는 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` 하나지만, E190 이후 이유는 더 분명하다.

- E176은 E72-contamination branch가 아니다.
- E176은 shape-only와 broad/Q2-underopen worldview를 묻는 파일이다.
- support gate를 E176에 붙이는 것은 지금 근거가 없다.

## E191 업데이트: hard negative를 줘도 support는 살아나지 않았다

내가 발견한 가장 이상한 점:

`exact E95/E101을 명시적인 hard negative로 넣어도 support view는 여전히 exact boundary를 E72-contamination처럼 본다. 반대로 shape/target/context view는 clean해진다. 즉 support 문제는 weight 문제가 아니라 representation 문제다.`

실험:

- `analysis_outputs/e191_boundary_aware_e72_score.py`
- report: `analysis_outputs/e191_boundary_aware_e72_score_report.md`

결과:

- best clean pair-LOO:
  - `shape_target_context_abs` / `plain_logit_c025`
  - AUC `0.978836`
  - AP `0.809524`
  - top-k recall `0.666667`
  - exact E95/E101 mean `0.057658`
- support-containing clean rows:
  - `0`
- support-only exact E95/E101 probability:
  - `0.785758..0.839112`
- shape+support/all exact E95/E101 probability:
  - `0.766102..0.824223`
- live E176:
  - contamination max around `0.000008`

생각이 어떻게 바뀌었는지:

`support는 E72 contamination을 보는 듯하지만, exact hardtail boundary와 분리되지 않는다. 이건 샘플 가중치나 prototype contrast로 고칠 수 있는 수준이 아니다. 현재 support는 gate가 아니라 현상 설명용 diagnostic이다.`

현재 최강 세계관:

`0.57629 병목의 한 축은 서로 다른 latent sensor가 각기 다른 boundary를 맞히는 데서 온다. shape/target/context는 tight E95/E101 boundary에 건강하고, support는 E72-neighbor correction에 반응하지만 exact boundary를 망친다. 이 둘을 섞는 것이 아니라, 언제 어떤 sensor를 믿을지 알려주는 새로운 structural target이 필요하다.`

다음으로 가장 정보량이 큰 행동:

새 submission은 만들지 않는다. 다음 제출 후보는 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` 하나다.

- 의도: broad/Q2-underopen hidden-tail sensor
- 기대 public 반응: `<=0.576276019`면 broad/Q2-underopen worldview 강화
- 실패 시 해석: support를 더 섞는 쪽이 아니라, shape/broad branch 자체 또는 public critical-cell tail이 틀렸다고 봐야 한다

## E192 업데이트: 남은 clean shape score는 gate가 아니라 tail-risk 현미경이다

내가 발견한 가장 이상한 점:

`E144는 clean shape E72 score에서 살짝 뜨지만, E72 positive처럼 보이지 않는다. nearest known rows가 전부 non-E72이고, known positive floor와는 두 자릿수 이상 떨어져 있다. 반면 E176은 거의 0에 붙어 있다.`

실험:

- `analysis_outputs/e192_shape_e72_score_anatomy.py`
- report: `analysis_outputs/e192_shape_e72_score_anatomy_report.md`

결과:

- exact E95/E101 score:
  - `0.031016`
- known thresholds:
  - non-E72 p95 `0.020815`
  - non-E72 p99 `0.044812`
  - E72 positive floor `0.804849`
- live branch:
  - E144 max `0.038723`, p95는 넘지만 p99와 positive floor는 못 넘음
  - E154 max `0.007973`
  - E176 max `0.000008`
- nearest known:
  - E144 top3 nearest는 모두 non-E72
  - E176 top3 nearest도 모두 non-E72 low-score context

생각이 어떻게 바뀌었는지:

`clean shape score를 live contamination gate로 쓰는 생각은 약해졌다. 이 score는 E144의 꼬리 위험을 표시할 수는 있지만, E72 contamination을 증명하지 않는다. E176은 이 관점에서 가장 깨끗하다.`

다음으로 가장 정보량이 큰 행동:

새 submission은 만들지 않는다. 다음 제출 후보는 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`다. 이 파일은 support/E72 gate가 아니라 broad/Q2-underopen 세계관을 묻는 센서다.

## E193 업데이트: E176은 인증된 승자가 아니라 가장 정보량 큰 센서다

내가 발견한 가장 이상한 점:

`E176을 지지하는 증거와 E154/E144를 지지하는 증거가 서로 다른 latent view에서 동시에 존재한다. 그래서 "어느 파일이 좋아 보이나"보다 "어떤 증거를 어떤 무게로 믿을 수 있나"가 더 중요한 문제가 됐다.`

실험:

- `analysis_outputs/e193_live_candidate_evidence_ledger.py`
- report: `analysis_outputs/e193_live_candidate_evidence_ledger_report.md`

결과:

- E176:
  - support `8`
  - warning `4`
  - evidence balance `3.100`
- E154:
  - support `4`
  - warning `4`
  - underidentified `1`
  - missing `3`
  - evidence balance `-0.225`
- E144:
  - support `3`
  - warning `5`
  - underidentified `1`
  - missing `3`
  - evidence balance `-1.725`

생각이 어떻게 바뀌었는지:

`E176은 "이길 것 같은 파일"이라기보다, 현재 살아 있는 세계관 중 가장 덜 모순적인 public 센서다. E154/E144는 죽은 후보가 아니라 inherited binary-world가 지지하는 alternate repaired-branch worldview다. 하지만 지금 증거 전체를 세면 첫 슬롯은 아니다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` 하나다.

- 의도: broad/Q2-underopen 세계관을 public 센서로 찌르기
- 기대 public 반응: 개선되면 E176 세계관 강화
- 실패 시 해석: tie/small-loss면 hidden-label resolution 병목 강화, worse-than-E101이면 partial-reopen family를 demote
- 금지: E176 스칼라 결과를 보고 Q2 keep factor를 다시 튜닝하지 않는다. 반드시 E177 decoder로 해석한다.

## E194 업데이트: E176 우선순위는 weight artifact는 아니지만, 반대 세계관은 E154다

내가 발견한 가장 이상한 점:

`E176을 고르는 결정은 한두 개 evidence source를 빼도 유지된다. 하지만 binary-world를 충분히 더 믿거나 pair geometry를 충분히 덜 믿으면 E154가 올라온다. 즉 반대편은 E144가 아니라 E154다.`

실험:

- `analysis_outputs/e194_evidence_ledger_robustness.py`
- report: `analysis_outputs/e194_evidence_ledger_robustness_report.md`

결과:

- single-source leaveout:
  - E176 win rate `1.000`
- random family-weight stress:
  - loguniform `0.25..4`: E176 win rate `0.771300`
  - loguniform `0.5..2`: E176 win rate `0.905950`
  - 20% family dropout: E176 win rate `0.896500`
- binary-world alone:
  - E154/E144 선택
- flip condition:
  - binary-world weight가 `1.760x`를 넘으면 E176보다 E154가 앞선다
  - visible/top-cell evidence를 제외하면 pair geometry가 `0.725x` 아래로 떨어질 때 E154가 앞선다

생각이 어떻게 바뀌었는지:

`E176은 weight artifact는 아니다. 하지만 "제출하면 이길 것"도 아니다. 현재 선택은 pair/shape/broad-body evidence를 binary-world counterprior보다 더 신뢰한다는 명시적 베팅이다. 이 베팅이 틀리면 다음은 E154 worldview를 봐야 한다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`다. E176이 나쁘게 나오면 같은 family 튜닝으로 도망가지 말고 E154 쪽 counter-world를 우선 재검토한다.

## E195 업데이트: E154는 반대 세계관이지만 첫 센서는 아니다

내가 발견한 가장 이상한 점:

`E154가 E176의 가장 강한 반대 세계관이라는 사실과, E154를 먼저 제출해야 한다는 결론은 다르다. 첫 제출은 가장 많은 세계관을 가르는 센서여야 한다.`

실험:

- `analysis_outputs/e195_next_sensor_information_value.py`
- report: `analysis_outputs/e195_next_sensor_information_value_report.md`

결과:

- E176:
  - sensor rank `1`
  - E176-vs-E154 moved cells/rows `1027/238`
  - focus expected delta `-0.000093546`
  - adverse decoder bands that route to E154/search `3`
- E154:
  - sensor rank `2`
  - E154-vs-E144 moved cells/rows `294/139`
  - local delta `-0.000002432`
  - E154-vs-E155 is not readable: `-0.000001796`

생각이 어떻게 바뀌었는지:

`E154는 죽은 후보가 아니라 E176 실패 후 가장 먼저 봐야 할 세계관이다. 하지만 E154를 먼저 내면 E176의 broad/Q2-underopen 세계관이 맞는지 틀린지 거의 모른 채 repaired-branch만 보게 된다. 그래서 첫 센서는 여전히 E176이다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` 하나다. Public LB가 나쁘면 그때 E154가 첫 counter-world로 올라온다. E176 점수를 보고 같은 family keep-factor를 다시 튜닝하는 행동은 금지한다.

## E196 업데이트: E176 motif 인증은 실패했다

내가 발견한 가장 이상한 점:

`E176의 top critical cells는 broad/Q2-underopen 세계관의 센서인데, row/order/block motif로 보면 top4/top16은 오히려 E72-vs-E95 loss motif에 가깝다. 다만 broader top33은 mixmin 쪽으로 약하게 이동한다.`

실험:

- `analysis_outputs/e196_e176_motif_nearest_anchor.py`
- report: `analysis_outputs/e196_e176_motif_nearest_anchor_report.md`

결과:

- action-grade motif views: `0/9`
- best view: `top4 / sequence_axis_flank`
- known-pair LOO accuracy: `0.833333`
- exact E101/E95 boundary correctness: `0`
- E176 nearest anchor in best view: `e72_vs_e95`, direction `new_lost`
- E176 inverse-distance vote: new_won `0.505761`, new_lost `0.494239`
- top33 nearest anchor: `mixmin_vs_a2c8`, but top33 LOO accuracy `0.333333`

생각이 어떻게 바뀌었는지:

`E176을 제출할 근거가 motif 인증으로 강화되지는 않았다. 오히려 critical top cells에는 약한 warning이 생겼다. 그래도 이 warning은 E176을 내리지 못한다. 이유는 motif selector가 exact E101/E95 boundary를 틀리기 때문이다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`다. E196은 E176 실패 시 해석에 쓸 warning이지, E176 제출 전 priority를 뒤집는 근거가 아니다.

## E197 업데이트: E176이 지는 세계는 더 좁아졌다

내가 발견한 가장 이상한 점:

`visible prior만 보면 E176은 충분히 이길 것처럼 보인다. 그런데 E72도 visible prior로는 좋아 보였고 public에서 크게 죽었다. 차이는 평균 support가 아니라 public slippage다.`

실험:

- `analysis_outputs/e197_public_support_mass_inverse.py`
- report: `analysis_outputs/e197_public_support_mass_report.md`

결과:

- known pair를 `delta = adverse_sum - q * swing_sum`으로 역분해했다.
- E72-vs-E95 visible slippage: `-0.071348`
- E72-vs-mixmin visible slippage: `-0.120707`
- E176 visible surplus-to-tie: `0.061761`
- E176 focus surplus-to-tie: `0.094836`
- E176 visible stress: clean-or-better `4/6`, win `4/6`, branch/hard fail `1/6`
- E172 visible surplus-to-tie: `0.070613`
- E154/E144/E155 visible surplus-to-tie: `0.010284` / `0.011545` / `0.011227`

생각이 어떻게 바뀌었는지:

`E176은 안전해서 1순위가 아니다. E176은 지는 조건이 이제 명확해서 1순위다. E176이 지려면 public hidden labels가 E72처럼 visible support를 강하게 배반해야 한다. 반면 E154 계열은 margin이 얇아서 작은 negative slippage에도 쉽게 branch-loss가 된다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`다. E176이 지면 같은 Q2 keep-factor를 튜닝하지 말고, E72-like adverse slippage가 활성화됐다고 보고 E172 safety contrast 또는 E154 counter-world로 분기한다.

## E198 업데이트: E176의 E72 위험은 shape가 아니라 slippage다

내가 발견한 가장 이상한 점:

`E176은 E72-like slippage stress에서는 질 수 있다. 그런데 clean E72 shape detector로 보면 E176은 E72와 전혀 닮지 않았다. 실패 조건은 보이지만, 실패의 shape signature는 보이지 않는다.`

실험:

- `analysis_outputs/e198_e72_slippage_exposure.py`
- report: `analysis_outputs/e198_e72_slippage_exposure_report.md`

결과:

- E191 clean detector:
  - AUC `0.978836`
  - AP `0.809524`
  - top-k recall `0.666667`
  - exact E95/E101 mean probability `0.057658`
- thresholds:
  - non-E72 p95 `0.020815`
  - non-E72 p99 `0.044812`
  - E72-positive floor `0.804849`
- E176:
  - visible surplus-to-tie `0.061761`
  - focus surplus-to-tie `0.094836`
  - visible E72-vs-E95 stress `small_loss`
  - visible E72-vs-mixmin stress `branch_loss`
  - clean shape E72 max probability `0.000008`
- E154:
  - visible surplus-to-tie `0.010284`
  - clean shape E72 max probability `0.007973`
- E144:
  - clean shape E72 max probability `0.038723`
  - p95 tail alarm은 있지만 p99/positive floor에는 못 미침

생각이 어떻게 바뀌었는지:

`E176을 "E72처럼 질 수 있다"와 "E72처럼 생겼다"는 같은 말이 아니다. 전자는 E197이 보여준 대수적 stress이고, 후자는 E198에서 지지되지 않았다. 그래서 E176을 내릴 이유는 늘지 않았지만, public에서 나쁘게 나오면 hidden-label slippage가 clean-shape detector 밖에서 발생했다는 뜻으로 읽어야 한다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`다. E176 실패 전에는 E72-demoted sibling을 만들지 않는다. 실패 후에는 scalar 점수 감으로 튜닝하지 말고 E177/E197 decoder band로 E172 safety contrast와 E154 counter-world 중 어디로 갈지 결정한다.

## E199 업데이트: E176 이후 분기 후보들도 대부분 E72 shape가 아니다

내가 발견한 가장 이상한 점:

`E198은 E176의 clean-shape E72 노출을 반증했지만, 정작 E176 실패 후 갈 후보들 중 일부는 아직 같은 방식으로 직접 점수화되지 않았다. 분기 정책의 약점은 E176이 아니라 follow-up 후보의 미진단 상태였다.`

실험:

- `analysis_outputs/e199_candidate_shape_e72_exposure.py`
- report: `analysis_outputs/e199_candidate_shape_e72_exposure_report.md`

결과:

- E172 direct E72 probability: `0.000087`
- E174 direct E72 probability: `0.000097`
- E176 direct E72 probability: `0.000097`
- E166 direct E72 probability: `0.000677`
- E154 direct E72 probability: `0.007860`
- E155 direct E72 probability: `0.009284`
- E144 direct E72 probability: `0.054385`
- thresholds:
  - non-E72 p95 `0.020815`
  - non-E72 p99 `0.044812`
  - E72-positive floor `0.804849`

생각이 어떻게 바뀌었는지:

`E172/E174/E166/E154/E155가 E72-shape 때문에 막혀 있는 것은 아니다. E172는 E176 tie/small-loss 후 same-family safety contrast로 남을 수 있고, E154는 E176 branch/hard-loss 후 E144보다 더 깔끔한 repaired-branch counter-world다. E144는 tail-risk control이지 첫 follow-up이 아니다.`

다음으로 가장 정보량이 큰 행동:

E176 제출 전 우선순위는 그대로다. 새 파일을 만들지 않는다. E176 public이 나오면:

- tie/small-loss: E172 safety contrast 우선
- branch/hard-loss: E154 repaired-branch counter-world 우선
- E144: p99 tail alarm control로 보류

## E200 업데이트: E172는 안전하지만 첫 센서는 아니다

내가 발견한 가장 이상한 점:

`E172는 E176보다 안전해 보인다. 그런데 안전하다는 사실이 곧 첫 제출 후보라는 뜻은 아니다. E172는 더 깨끗한 rollback contrast지만, E176이 묻는 broad/Q2-underopen 세계관 자체를 충분히 관측하지 못한다.`

실험:

- `analysis_outputs/e200_e176_vs_e172_first_sensor_resolution.py`
- report: `analysis_outputs/e200_e176_vs_e172_first_sensor_resolution_report.md`

결과:

- E176 expected edge over E172: `0.0000106885`
- 이 edge는 E95-over-mixmin public edge의 `0.698x`
- E172 visible surplus advantage: `0.008852`
- E172 focus surplus advantage: `0.007054`
- E172 clean-shape E72 probability advantage: `0.00000972`
- E176-vs-E172: `75` cells
- E176-vs-E154: `1027` cells
- same-family / counter-world expected-delta ratio: `0.114`

생각이 어떻게 바뀌었는지:

`E172의 장점은 인정해야 한다. 하지만 그 장점은 첫 센서를 바꿀 만큼 크지 않고, 질문도 좁다. E172-first는 "안전한 rollback이 맞나?"를 묻고, E176-first는 "broad/Q2-underopen 세계관이 public-real인가?"를 묻는다. 지금 필요한 것은 더 안전한 질문이 아니라 더 많은 세계관을 죽이는 질문이다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 여전히 `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` 하나다. E172는 E176이 tie/small-loss일 때만 같은 family의 safety contrast로 쓴다. E176이 branch/hard-loss이면 E172가 아니라 E154/search로 간다.

## E201 업데이트: E176은 이제 파일이 아니라 관측 프로토콜이다

내가 발견한 가장 이상한 점:

`E176을 제출하기로 정했어도, public 숫자를 본 뒤에 해석을 바꾸면 관측이 아니라 튜닝이 된다. 이 대회에서 위험한 것은 틀린 파일만이 아니라, 맞는 파일을 내고도 결과를 아무 방향으로나 해석하는 것이다.`

실험:

- `analysis_outputs/e201_e176_public_sensor_packet.py`
- report: `analysis_outputs/e201_e176_public_sensor_packet_report.md`

결과:

- E176 file: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- SHA256: `34d38587b04640327824b972f4cbc18ae03cab2f92802ac7c144f94b96184206`
- sample schema/key/probability audit: pass
- E176 vs E95: `904` cells, `193` rows
- target movement share:
  - Q2 `0.209702`
  - S4 `0.145285`
  - Q3 `0.141693`
  - S2 `0.130103`
  - Q1 `0.128746`
  - S3 `0.126307`
  - S1 `0.118164`

생각이 어떻게 바뀌었는지:

`이제 "E176을 낸다"가 아니라 "E176이라는 측정 장치를 작동시킨다"가 맞다. 0.5762883298보다 좋으면 broad/Q2-underopen 세계관이 살아남지만 sibling을 바로 만들지 않는다. 0.5762883298..0.576300366이면 E172 safety contrast만 의미 있다. 0.576300366보다 나쁘면 partial-reopen branch를 내리고 E154/search로 간다. 0.5763413298보다 나쁘면 same-family expected-score lane은 닫는다.`

다음으로 가장 정보량이 큰 행동:

제출한다면 E176 하나다. public 결과가 나오면 반드시:

`python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <E176_PUBLIC_LB>`

를 먼저 실행하고, `analysis_outputs/e201_e176_public_sensor_packet_route_summary.csv`와 맞춰본 뒤 다음 파일을 결정한다.

## E202 업데이트: E176은 Q2 실험이 아니라 S-stage/body 센서다

내가 발견한 가장 이상한 점:

`E176 파일명은 Q2 keep 0.75를 가리키지만, 실제 기대 책임은 Q2보다 S3/S1/S4와 between-train-runs body에 더 크다. 이름을 믿으면 public score를 잘못 읽게 된다.`

실험:

- `analysis_outputs/e202_e176_component_responsibility_router.py`
- report: `analysis_outputs/e202_e176_component_responsibility_report.md`

결과:

- S-target expected share: `0.651098`
- Q-target expected share: `0.348902`
- between-train-runs expected share: `0.807772`
- Q2 raw movement share: `0.209702`
- Q2 expected share: `0.121416`
- top expected contributors: S3 `0.203515`, S1 `0.189679`, S4 `0.146985`
- top33 visible-support `p_low`: `0.014667`

생각이 어떻게 바뀌었는지:

`E176이 좋게 나오면 "Q2 keep이 맞았다"가 아니라 "S-stage / between-train-runs body가 public에서 살았다"가 첫 해석이다. E176이 애매하거나 나쁘면 "Q2만 틀렸다"가 아니라 "hard-label tail/cancellation을 못 풀었다"가 첫 해석이다.`

다음으로 가장 정보량이 큰 행동:

제출 후보는 그대로 E176 하나다. 하지만 결과가 나오면 E201 score router와 E202 component router를 같이 보고 다음 행동을 정한다. Q2 sibling은 public 숫자 하나로 만들지 않는다.

## E203 업데이트: E176의 몸통과 꼬리를 분리했다

내가 발견한 가장 이상한 점:

`E176의 top33 cell은 중요하지만 전체 신호가 아니다. 넓은 body는 살아 있고, public에서 죽을 수 있는 부분은 compact tail/cancellation 층이다.`

실험:

- `analysis_outputs/e203_e176_component_knockout_stress.py`
- report: `analysis_outputs/e203_e176_component_knockout_stress_report.md`

결과:

- full E176 focus delta in E179 cell prior: `-0.000078041955`
- S-only share: `0.644881`
- primary S3/S1/S4 share: `0.573289`
- between-train-runs share: `0.774524`
- Q2-only share: `0.093922`
- top33 share: `0.226424`
- drop top33 leaves: `0.773576`
- top33 visible support: `0.245771`

생각이 어떻게 바뀌었는지:

`E176이 실패해도 broad body 자체가 없었다고 바로 읽으면 안 된다. 더 정밀한 해석은 body는 있는데 top33/hard-tail에서 cancellation이 public edge를 먹었다는 것이다. 반대로 E176이 이기면 Q2가 아니라 S-stage / between-train-runs body가 먼저 살아난다.`

다음으로 가장 정보량이 큰 행동:

E176 제출 순서는 유지한다. clean win일 때만 Q2 amplitude를 paired question으로 묻고, tie/loss면 E172 safety 또는 E154/search route로 간다.

## E204 업데이트: 후속 파일들은 같은 사다리가 아니다

내가 발견한 가장 이상한 점:

`E172, E154, E174는 E176 다음 후보처럼 보이지만 같은 축의 세기 조절이 아니다. 각각 같은-family rollback, body-exit counter-world, Q2 amplitude probe다.`

실험:

- `analysis_outputs/e204_e176_followup_correction_map.py`
- report: `analysis_outputs/e204_e176_followup_correction_map_report.md`

결과:

- E172:
  - changed cells `75`
  - off-E176 abs share `0.000000`
  - rollback share `1.000000`
  - body rollback fraction `0.089780`
- E154:
  - changed cells `1027`
  - off-E176 abs share `0.292501`
  - body rollback fraction `0.877576`
- E174:
  - changed cells `21`
  - rollback share `0.000000`
  - Q2 amplitude probe

생각이 어떻게 바뀌었는지:

`E176 결과가 애매하면 E172가 맞다. E176 결과가 나쁘면 E154가 맞다. E176 결과가 좋을 때만 E174가 의미 있는 질문이 된다. 이 셋은 점수 근처 후보가 아니라 서로 다른 세계관 질문이다.`

다음으로 가장 정보량이 큰 행동:

E176 public band를 먼저 보고, 그 band가 묻는 세계관에 맞는 follow-up만 선택한다. scalar로 가장 가까운 파일을 고르지 않는다.

## E205 업데이트: E176 결과 해석을 실행 파일로 고정했다

내가 발견한 가장 이상한 점:

`E201-E204가 이미 해석 규칙을 만들었는데도, 실제 public score가 나오면 사람이 다시 scalar 감각으로 해석할 위험이 남아 있었다. 이 위험은 모델 문제가 아니라 feedback protocol 문제다.`

실험:

- `analysis_outputs/e205_e176_public_feedback_executable_decoder.py`
- report: `analysis_outputs/e205_e176_public_feedback_executable_decoder_report.md`
- routebook: `analysis_outputs/e205_e176_public_feedback_executable_decoder_routebook.csv`
- examples: `analysis_outputs/e205_e176_public_feedback_executable_decoder_examples.csv`

결과:

- `0.576291` 예시는 `tie`로 해석되고 E172 same-family safety로 간다.
- `0.576303` 예시는 `e101_worse_mixmin_safe`로 해석되고 E154 body-exit counter-world로 간다.
- clean win / breakthrough는 즉시 sibling을 만들지 않고 broad S-stage / between-train-runs body를 먼저 분해한다.

생각이 어떻게 바뀌었는지:

`이제 E176은 파일 하나가 아니라 측정 프로토콜이다. score를 받으면 먼저 E205로 디코딩하고, 그 다음에만 follow-up을 고른다. Q2 amplitude, E172 safety, E154 counter-world, E174 probe는 같은 사다리가 아니라 score band가 묻는 서로 다른 질문이다.`

다음으로 가장 정보량이 큰 행동:

E176 public LB가 들어오면 `python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score <E176_PUBLIC_LB>`를 먼저 실행한다.

## E206 업데이트: E176은 branch loss였다

내가 발견한 가장 이상한 점:

`E176은 local evidence로는 넓은 S-stage / between-train-runs body가 살아 있었지만, public에서는 mixmin보다도 나빠졌다. body는 보였는데 public frontier edge는 돌아오지 않았다.`

실험:

- submission: `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`
- public LB: `0.576311831`
- decoder: `python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score 0.576311831`

결과:

- E95 대비 `+0.0000205012`
- mixmin 대비 `+0.0000051905`
- E101 대비 `+0.000011465`
- E205 outcome: `branch_loss`
- next coherent existing file: `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`

생각이 어떻게 바뀌었는지:

`E176/E174/E172/E169 같은 broad partial-reopen family를 expected-score 후보로 계속 미는 길은 약해졌다. 이 결과는 Q2 keep-factor의 실패가 아니라, broad body가 public hard-label/tail realization에서 frontier edge를 되돌려준 사건이다.`

다음으로 가장 정보량이 큰 행동:

E154로 repaired-branch counter-world를 묻거나, 아예 non-collinear hidden-block/sequence/target-dependency representation으로 돌아간다. E174/Q2 sibling과 E172 immediate safety는 이번 score의 다음 질문이 아니다.

## E207 업데이트: JEPA를 진짜로 쓰려면 pair부터 골라야 한다

내가 발견한 가장 이상한 점:

`기존 LeJEPA block-canvas는 subject lag2에서 그럴듯해 보이지만, LeJEPA 논문 조건으로 보면 increment가 너무 비정규적이고 split별 거리도 흔들린다. 즉 "좋은 latent"처럼 보이는 것과 "식별 가능한 JEPA transition"은 다르다.`

실험:

- `analysis_outputs/e207_lejepa_identifiability_conditions_audit.py`
- summary: `analysis_outputs/e207_lejepa_identifiability_conditions_audit_summary.csv`
- report: `analysis_outputs/e207_lejepa_identifiability_conditions_audit_report.md`

실험 결과:

- 전체 `77`개 latent/pair 조합 중 true-JEPA 후보는 `1`개뿐이다.
- 살아남은 조합은 `broad_stage2_pca64 + feature_nn1_all`.
- readiness `0.652939`, rho `0.494280`, alignment `0.636020`, increment Gaussian score `0.435262`.
- `lejepa_l0p2_d32_pca48 + subject_lag2_all`은 readiness `0.668530`이지만 increment Gaussian score `0.194814`, split distance CV `0.660020`이라 energy/auxiliary로 강등된다.

생각이 어떻게 바뀌었는지:

`JEPA를 쓴다면 subject-order row sequence를 크게 학습시키는 게 아니라, feature-neighbor positive pair를 중심으로 context-to-target representation을 예측해야 한다. 기존 subject/block LeJEPA는 버릴 필요는 없지만, submission 생성기보다는 gate/energy로 써야 한다.`

다음으로 가장 정보량이 큰 행동:

E208은 feature-neighbor JEPA다. context는 broad stage2 latent와 feature-family mask, target은 nearest-neighbor latent/hidden residual representation으로 두고, LeJEPA-style Gaussianity/isotropy/alignment diagnostics를 hard guard로 붙인다. E208 진단 전에는 새 JEPA submission을 만들지 않는다.

## E208 업데이트: JEPA를 실제로 학습시켰고, 신호는 Q3/S4에만 살아남았다

내가 발견한 가장 이상한 점:

`JEPA 학습 자체는 된다. 하지만 모든 target을 좋아지게 하는 만능 latent가 아니라, Q3 residual과 S4 prediction 쪽에만 안정적인 신호가 나온다. S2는 local에서는 좋아 보이지만 geometry에서 죽는다.`

실험:

- `analysis_outputs/e208_feature_neighbor_jepa_probe.py`
- report: `analysis_outputs/e208_feature_neighbor_jepa_probe_report.md`

실험 결과:

- JEPA validation MSE가 copy-self보다 전부 낮다.
  - `0.588331 < 0.812629`
  - `0.555652 < 0.885360`
  - `0.550826 < 0.815146`
- mean-target baseline도 전부 이긴다.
- `pred_mean`은 유용하지만 anisotropic하다: rank fraction `0.287411`, condition `1365.92`.
- `hidden_mean`은 더 건강하다: rank fraction `0.611836`, condition `44.0311`.
- downstream에서 Q3/S4만 materialization gate를 통과했다.
- gate pass count는 `8`.

생각이 어떻게 바뀌었는지:

`JEPA는 쓸 수 있다. 다만 "JEPA latent 전체를 넣자"가 아니라, JEPA가 만들어낸 residual/energy 중에서 Q3/S4에 안정적으로 살아남는 부분만 써야 한다. 이건 아이디어 차용이 아니라 실제 context-to-target representation 학습이다.`

다음으로 가장 정보량이 큰 행동:

E209를 만든다면 Q3 `e208_resid_self_pc10`와 S4 `e208_pred_pc14`만 물질화한다. S2는 local gain이 커도 geometry stress가 나쁘므로 아직 제출 후보가 아니다. E209는 반드시 E95/E154/E176 branch-loss geometry와 비교한 뒤에만 public slot을 쓴다.

## E209 업데이트: JEPA 신호를 실제 submission 후보로 옮겼다

내가 발견한 가장 이상한 점:

`JEPA는 전역적으로 강한 모델이 아니라, Q3/S4에만 좁고 날카로운 신호를 준다. 이 신호는 stage2 OOF와 geometry에서는 살아남지만, public hard-label 한두 셀에 여전히 취약하다.`

실험:

- `analysis_outputs/e209_feature_neighbor_jepa_materialization_stress.py`
- report: `analysis_outputs/e209_feature_neighbor_jepa_materialization_report.md`

실험 결과:

- `q3_center_c010_s4_rank`는 OOF delta `-0.001272724`, subject-half win rate `0.900000`, geometry delta `-0.000794598`.
- 제출 후보 4개를 만들었다.
- 가장 높은 survival score:
  `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv`
- JEPA 자체를 가장 깨끗하게 묻는 후보:
  `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv`

생각이 어떻게 바뀌었는지:

`JEPA를 쓴다는 건 이제 말뿐이 아니다. 실제 context-to-target JEPA를 학습했고, 그 latent에서 Q3/S4 확률 이동을 만들었다. 다만 이건 0.54로 가는 큰 문이 아니라, 현재로서는 Q3/S4 hard-tail을 찌르는 좁은 센서다.`

다음으로 가장 정보량이 큰 행동:

한 파일만 낸다면 목적을 정해야 한다. 점수 기대를 조금 더 보려면 E154-anchored 파일, JEPA가 실제로 frontier에 도움이 되는지 깨끗하게 보려면 E95-anchored 파일이다. 둘 다 지면 JEPA 학습 자체가 아니라 현재 probability translation이 죽는 것이다.

## E210 업데이트: target-dependency gate는 센서이지 대체재는 아니다

내가 발견한 가장 이상한 점:

`E210 gate는 public-prior hard-tail 수치를 크게 좋게 만들지만, ungated E209보다 OOF/geometry 신호를 많이 잃는다. 특히 S4는 dependency gate가 말이 되지만, Q3는 dependency-aligned 셀보다 non-aligned 셀이 더 좋은 경우가 많다.`

실험:

- `analysis_outputs/e210_jepa_target_dependency_gate.py`
- report: `analysis_outputs/e210_jepa_target_dependency_gate_report.md`

실험 결과:

- top E210 e154 closer 후보: expected focus delta `-0.001379`, top1/abs `0.171181`.
- 하지만 OOF는 `-0.000482`, ungated E209의 `-0.001273`보다 약하다.
- geometry도 `-0.000096`, ungated E209의 `-0.000939`보다 약하다.
- anti-toward control은 frontier gate를 통과하지 못해서, polarity가 완전히 무의미한 것은 아니다.

생각이 어떻게 바뀌었는지:

`target dependency는 버릴 신호가 아니다. 다만 E209를 바로 대체할 만큼 건강하지 않다. 지금은 public hard-tail이 dependency filtering을 원하는지 묻는 follow-up sensor다.`

다음으로 가장 정보량이 큰 행동:

JEPA 자체를 묻는다면 E209가 먼저다. E209가 애매하거나 tail 때문에 죽는다면, 그 다음 E210으로 “public tail이 target-dependency gate를 원했는가”를 물어보는 순서가 더 논리적이다.

## E211 업데이트: Q3와 S4는 같은 JEPA 신호라도 번역법이 다르다

내가 발견한 가장 이상한 점:

`Q3와 S4를 같이 gate하면 망가지는데, Q3는 raw JEPA body를 유지하고 S4만 dependency gate를 걸면 오히려 E209보다 OOF가 좋아진다.`

실험:

- `analysis_outputs/e211_target_specific_jepa_gate.py`
- report: `analysis_outputs/e211_target_specific_jepa_gate_report.md`

실험 결과:

- Q3 raw + S4 toward: OOF `-0.001318`, E209 ungated `-0.001273`보다 좋다.
- Q3 raw + S4 closer: OOF `-0.001315`.
- Q3 target delta는 `-0.005775`로 raw body를 유지한다.
- S4는 raw `-0.003134`에서 toward `-0.003451`로 좋아진다.

생각이 어떻게 바뀌었는지:

`이제 JEPA 병목은 "쓸까 말까"가 아니라 "target별로 어떻게 번역할까"다. Q3는 residual body, S4는 dependency-consistent movement로 보는 게 현재 가장 그럴듯하다.`

다음으로 가장 정보량이 큰 행동:

최대 기대 후보는 E211 E154 closer, 깨끗한 current-frontier 센서는 E211 E95 toward다. E209는 raw JEPA control로 남긴다.

## E212 업데이트: 이제 JEPA는 파일 하나가 아니라 실험 순서다

내가 발견한 가장 이상한 점:

`실제 JEPA를 쓰기 시작하자, 문제는 모델이 아니라 해석 순서가 됐다. E209/E210/E211은 모두 JEPA 계열이지만 같은 주장을 하지 않는다. E210은 hard-tail 수치가 좋아도 Q3 body를 많이 버리고, E211은 Q3 raw body와 S4 dependency gate를 동시에 보존한다.`

실험:

- `analysis_outputs/e212_jepa_family_sensor_ordering.py`
- report: `analysis_outputs/e212_jepa_family_sensor_ordering_report.md`

실험 결과:

- 최대 structured survival 1위:
  `analysis_outputs/submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv`
- clean current-frontier sensor 1위:
  `analysis_outputs/submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv`
- raw JEPA control:
  `analysis_outputs/submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv`
- E210은 hard-tail survival은 강하지만 local/geometry parent body 손실 때문에 다음 1순위에서는 빠졌다.

생각이 어떻게 바뀌었는지:

`JEPA를 쓴다는 답은 이제 "yes"다. 다만 정답은 큰 JEPA 모델이 아니라, JEPA representation을 target별로 번역하고 public feedback을 routebook으로 해석하는 것이다. Q3는 raw residual body, S4는 dependency-consistent movement라는 세계관이 현재 제일 강하다.`

다음으로 가장 정보량이 큰 행동:

점수 기대를 최대화한다면 E211 E154 closer를 제출한다. JEPA 자체의 깨끗한 효과를 보려면 E211 E95 toward를 제출한다. 어느 쪽이든 public 결과를 본 뒤 E212 routebook 없이 E209/E210 follow-up을 고르면 안 된다.
