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
