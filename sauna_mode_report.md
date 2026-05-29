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

지금 제출할 파일은 여전히 하나다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.

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

지금 제출할 파일은 여전히 하나다. `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`.
