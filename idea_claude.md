아래는 모델 튜닝이 아니라 **"하루를 어떻게 표현하느냐"**에 집중한 답이야. 라벨 의미는 네가 준 프레이밍("평소 대비 오늘")을 그대로 신뢰하고 갔어.

## 1. 병목 진단 (5줄)

1. **유효 표본은 450이 아니라 ~10이다.** subject가 10명뿐이라 subject 단위로 보면 사실상 LOSO 10-fold가 한계고, subject별 신호는 거의 다 암기된다. 진짜 제약은 날짜가 아니라 subject 수.
2. **라벨이 상대값("내 평소 대비")이라 절대 피처는 노이즈다.** 절대 활동량/수면시간이 아니라 *그 사람 baseline 대비 deviation*을 넣어야 하고, baseline은 반드시 unlabeled 날들로 만들어야 한다.
3. **OOF≠LB는 십중팔구 CV 설계 오류다.** random KFold는 같은 subject·인접 날짜가 train/valid에 섞여 누수가 난다. LOSO + 시간순 인과 split이 아니면 OOF는 의미가 없다.
4. **target mean shift / panel drift는 시간 누수와 base-rate 이동 두 갈래다.** test 날짜가 후반부에 몰려 base rate가 다르고, day-index를 안 넣으면 모델이 이걸 못 흡수한다. threshold·캘리브레이션이 시간에 따라 깨진다.
5. **진짜 레버는 unlabeled 데이터다.** 450행 위에 피처 100개 얹는 건 과적합 직행이고, SSL pretrain + per-subject baseline으로 unlabeled를 흡수하는 게 유일하게 generalization을 늘리는 길이다.

---

## 2. 데이터 엔지니어링 아이디어 100개

### A. 하루를 다르게 자르기 (1–12)

1. 자정 기준 폐기 → **기상시각~다음 기상시각(wake-to-wake)**을 한 "하루"로. 라벨이 수면을 끼고 평가되면 이게 자연 단위다.
2. **수면 onset~다음 onset(sleep-to-sleep)** 윈도우. S 타겟은 "어젯밤 잠"이 핵심이라 잠 episode가 윈도우 경계가 돼야 한다.
3. **설문 응답 시각을 윈도우의 끝으로 고정** → 응답 이후 데이터는 절대 피처에 넣지 않음 (미래 누수 차단).
4. **타겟별 causal cutoff 분리**: S는 취침 직전까지, Q는 설문시각까지만. 동일 윈도우를 쓰면 한쪽은 누수, 한쪽은 정보손실.
5. **circadian 시계로 리샘플**: 벽시계 대신 그 사람 습관적 midsleep을 0점으로 시간축 정렬 → 야간근무/올빼미형 보정.
6. "활동 day" = 첫 움직임~마지막 움직임. 깨어있는 구간만 잘라 주간 피처 계산.
7. 첫 폰 unlock ~ 마지막 폰 lock = "디지털 각성 구간". 수면센서 결측 시 수면 경계 대체값.
8. 하루를 4국면(이른아침/오전/오후/저녁밤)으로 자르되 경계를 고정시각이 아니라 그 사람 루틴 변곡점(출근/귀가 추정시각)으로.
9. **commute episode 기준 분할**: 출근전/근무/퇴근후. commute 유무 자체가 평일/휴일·재택 신호.
10. "마지막 밤"을 today와 분리해 별도 객체로 토큰화. today 라벨이 어젯밤 수면에 의존하니까.
11. 고정 bin이 아니라 **change-point detection**으로 가변 분할 → episode 경계를 데이터가 정하게.
12. 주간 위상: 요일을 원형 인코딩하되 "이 사람의 주중/주말 경계가 실제로 어디인지"(재택·교대)를 학습된 경계로.

### B. subject baseline & deviation (13–25)

13. **subject별 ECDF 변환**: 모든 피처를 그 사람 과거 분포의 percentile로. 라벨이 "평소 대비"라 percentile이 라벨 정의와 직결.
14. subject별 분포를 공통 reference로 **quantile mapping** → 스케일 통일, distribution shift 직접 완화.
15. **subject prototype day**: labeled+unlabeled 전부의 median trajectory. today와의 잔차가 deviation 피처.
16. **DTW barycenter**로 시간왜곡 보정한 prototype 만들고 today의 DTW 거리.
17. **잔차 day**: day-of-week+최근추세로 기대 day를 회귀 → residual = "오늘이 평소와 얼마나 다른가".
18. **subject별 행동 prior 만들고 today의 surprisal(−log likelihood)**. 텍스트 density의 per-token surprisal 발상을 하루 단위로.
19. **subject별 episode 전이 Markov 모델 → today 시퀀스의 perplexity** = 하루의 의외성.
20. 평균이 아니라 **분산구조로 subject 표현**: 루틴 경직형 vs 혼돈형 → 같은 deviation도 의미가 다르다.
21. z-score 대신 **robust z(중앙값/MAD)** → 이상치 많은 라이프로그에 안전.
22. "오늘 = 내 어떤 과거 날과 가장 닮았나"의 self-similarity rank.
23. baseline을 단일 스칼라가 아니라 **시간대별 곡선**으로(아침 baseline, 밤 baseline 따로).
24. deviation의 **방향(부호)과 크기를 분리 채널**로: "평소보다 많다/적다"와 "얼마나"를 따로.
25. subject별 정상영역을 one-class로 학습 → today가 그 영역 밖인 정도 = anomaly score.

### C. 최근 7/14/28일 & drift (26–37)

26. 최근 7/14/28일 rolling baseline 대비 today deviation을 윈도우별로.
27. **sleep debt**: 최근 7일 수면시간 누적 부족분.
28. **회복부채(activity debt)**: 최근 활동 deviation 누적.
29. **EWMA baseline**(반감기 가변) → 최근 가중. 단순 28일 평균보다 panel drift에 강함.
30. "추세 vs 오늘": 최근 14일 기울기 부호와 today 부호의 일치/배반.
31. **social jetlag**: 주중-주말 midsleep 차이를 rolling으로.
32. **변동성의 변동성**: 최근 7일 deviation의 분산이 커지는가(불안정화 신호).
33. day-index / week-index를 명시 피처로 → target mean shift를 모델이 흡수.
34. 캘린더 주 단위 base-rate detrend 값.
35. 최근 결측률 추세 → 센서 노후/이탈 모니터링.
36. "어제 echo": today와 yesterday 활동 시계열 cross-correlation, 최적 lag.
37. 마지막 N박 수면을 작은 시퀀스로 → decoder에 N-night 컨텍스트 입력.

### D. episode 분절 & 이벤트 표현 (38–50)

38. 하루를 **typed episode 시퀀스**로: (정지/이동/수면/폰버스트/결측) × duration × 시작시각 × 위치클러스터.
39. **episode = Transformer 토큰**: `[WAKE]@7:12 [STILL,2h]@home [MOVE,40m] ...` → "하루를 문장으로".
40. episode 전이행렬 엔트로피 = 하루의 무질서도.
41. **context switch 수**: 위치클러스터 전환 횟수 = 하루 파편화.
42. 가장 긴 정지+폰off 블록 = "quiet hours" 길이/시작.
43. 활동 burst의 **burstiness B (Goh-Barabási)**: 규칙적 vs 몰아치는.
44. inter-event time 분포: 폰 unlock 간격의 엔트로피.
45. 수면 윈도우 내 **micro-arousal proxy**: 짧은 움직임 burst 횟수 = 수면 분절.
46. 기상~첫 폰 unlock latency = 아침 둔함.
47. 기상~첫 외출(집 이탈) latency = 활동 시동.
48. episode duration을 절대값 말고 그 사람 그 episode-type 평소 길이의 percentile로.
49. episode를 SAX/quantile 이산화 → 어휘화 → motif 탐색 가능.
50. day를 **2D 이미지(시간×모달)** 또는 recurrence plot / GAF → ViT 입력.

### E. 결측을 신호로 (51–58)

51. 결측을 NaN이 아니라 **typed episode**로: `[MISSING,8h]@night` = 충전 = 정상.
52. **missingness fingerprint**: 결측의 시간대 패턴 자체를 피처(야간결측 vs 주간결측 구분).
53. 충전 episode 추정(야간 장기결측) → 취침 proxy.
54. 주간 결측 = 기기 미소지/외출패턴 변화 → 비정상 신호.
55. 모달 간 결측 동시성: 동시 결측(기기 off) vs 단일 모달 결측(센서 고장) 구분.
56. **결측률을 confounder로 명시 모델링** → 라벨과의 spurious 상관이 LB로 전이되지 않게.
57. 결측 직전/직후 행동으로 결측 원인 추정(자다가 끊김 vs 활동 중 끊김).
58. **"관측 가능했던 시간 비율"로 모든 카운트 피처 normalize** → 결측 길이 편향 제거.

### F. cross-modal 관계 (59–71)

59. GPS=집인데 가속도=고활동 → 실내운동/청소. **모순이 도메인 정보**.
60. 폰 과사용 + 가속도=걷는중 → 주의분산 보행.
61. 수면센서=수면인데 폰=unlock → 불면/분절수면 직접 측정.
62. GPS정지+폰off+저활동 = 진짜 휴식 vs GPS정지+폰고사용 = **cocooning(위축)**.
63. 모달 간 상태 일치도(agreement) 점수 → 데이터 품질 + 행동 신호 동시 포착.
64. **location entropy / normalized entropy** (digital phenotyping) — 기분·우울 검증된 마커.
65. **circadian movement**: 이동의 24h 주기성 power — 검증된 우울 마커.
66. home stay 비율, 방문 고유 장소 수, 집에서 최대 거리.
67. transition time: 장소 간 이동에 쓴 총 시간.
68. 이동 직전/직후 폰 사용 패턴(이동과 폰의 시간적 결합).
69. **수면 직전 90분 폰 사용량(sleep hygiene)** → S 타겟 강력 후보.
70. 기상 직후 30분 폰 사용 → 각성/기분 proxy.
71. 한 모달로 다른 모달 복원한 잔차 = **cross-modal anomaly**(GPS 가리고 가속도+폰으로 복원).

### G. retrieval / prototype / motif (72–80)

72. subject 내 day-embedding kNN → today 라벨 = 닮은 과거 날들의 soft vote.
73. **matrix profile**로 활동 시계열 motif/discord 탐색 → 반복 패턴 vs 이례.
74. day 클러스터링 → "하루 유형" 라벨, subject별 유형 분포.
75. prototype 거리 벡터: 모든 day-유형 prototype까지 거리 = 하루 표현.
76. **cross-subject retrieval**: 행동구조 닮은 타 subject의 비슷한 날 borrow(cold-start).
77. day-of-week 조건부 retrieval: 같은 요일 과거 날과만 비교.
78. motif 어휘로 하루를 bag-of-motifs 표현 → 작은 decoder 친화.
79. "이 하루가 이 subject에게 얼마나 전형적인가" typicality score.
80. retrieval 이웃들의 라벨 분산 = 예측 불확실성 추정.

### H. target별 view (81–86)

81. **S 타겟 view**: 야간 윈도우·수면구조·취침전 폰·micro-arousal 중심.
82. **Q 타겟 view**: 주간 활동 파편화·mobility entropy·장소 다양성·commute 중심.
83. 타겟별 윈도우 길이 다르게: S는 밤 12h, Q는 wake-to-survey.
84. 7개 타겟 multi-task로 묶되 SSL 임베딩 공유 → 어떤 타겟이 어떤 view를 공유하는지 학습.
85. 타겟별 subject 정규화 강도 다르게(절대값이 더 중요한 타겟이 있을 수 있음 → ablation으로 확인).
86. 타겟 간 상관 구조를 라벨 부족 보완에 활용(한 타겟을 다른 타겟의 보조 SSL 신호로).

### I. Transformer/Enc-Dec 입력 토큰화 (87–92)

87. 30분 bin × 멀티채널 = 48토큰/일 시계열 transformer 입력.
88. 가변길이 episode 토큰열 = "하루 문장"(의미적, enc-dec 친화).
89. **계층 토큰화**: episode→day→subject-history 2단계. 최근 며칠을 컨텍스트, today를 query.
90. **subject baseline 요약 토큰을 맨 앞에 prepend** → 모델이 내부에서 deviation을 계산(상대 라벨 직결).
91. 연속 피처를 subject quantile binning으로 어휘화 → embedding lookup.
92. 모달별 토큰 스트림 + `[SEP]` + cross-modal attention. 결측은 `[MASK]`가 아니라 전용 `[MISSING]` 토큰.

### J. 라벨 450개를 우회하는 self-supervised target (93–100)

93. **Masked Episode Modeling**: episode 하나 가리고 type/duration 복원(BERT 스타일).
94. **Cross-modal reconstruction**: GPS 통째로 가리고 가속도+폰으로 복원 → 모달 간 구조 학습.
95. **Next-day forecasting**: 오늘 day로 내일 day(또는 내일 수면) 예측 → enc-dec pretext.
96. **Temporal jigsaw**: episode 순서를 섞고 원래 순서/시각 복원.
97. **Day-augmentation contrastive**(time-warp, crop, channel dropout, jitter) → TS2Vec/TS-TCC 스타일 day embedding.
98. **Subject-adversarial(gradient reversal)**: subject 분류기를 역전파 반전 → subject-invariant 임베딩, distribution shift 직격.
99. **per-subject autoencoder anomaly pretrain**: 재구성 오차 = "오늘이 얼마나 이례적인가" = deviation 피처를 SSL로 직접 생성.
100.  **Sleep Regularity Index 자기예측**: 24h 떨어진 두 시점이 같은 sleep/wake 상태일 확률을 self-target으로 → 규칙성 임베딩.

---

## 3. Top 10 (이유 + 과적합 위험)

1. **수면/기상 앵커 재윈도우 + 타겟별 causal cutoff (#1–4)** — OOF≠LB의 가장 흔한 원인이 윈도우 누수다. S/Q에 다른 cutoff를 주면 누수 제거 + 정보손실 방지. 과적합 위험 낮음, 거의 무조건 해야 함.
2. **subject별 ECDF percentile 정규화 (#13)** — 라벨이 "상대값"이라 percentile이 라벨 정의 자체. 파라미터 없고 LB 전이 안정. 위험: test subject가 train에 없으면 baseline을 못 만든다 → subject 구성부터 확인.
3. **prototype/잔차 deviation (#15–17)** — "오늘이 평소와 다른 정도"를 피처가 직접 표현. 위험 중간: prototype을 labeled만으로 만들면 누수 → 반드시 unlabeled 포함, 시간순으로만.
4. **episode 토큰화 (#38–39)** — transformer 입력과 SSL의 공통 기반. 이게 없으면 J가 전부 불가. 위험 낮음(표현일 뿐).
5. **Masked Episode SSL pretrain (#93)** — 450 라벨 병목을 unlabeled로 우회하는 핵심. 위험: pretext가 라벨과 무관하면 헛수고 → frozen embedding vs raw feature를 LOSO로 비교 검증.
6. **subject-adversarial 표현 (#98)** — subject shift를 표현 단계에서 직접 제거. 위험 있음: 라벨이 subject base-rate와 상관되면 신호까지 지운다 → 4번 실험에서 명시 점검.
7. **결측 typed episode화 + coverage normalize (#51, #58)** — 결측은 라이프로그에서 비랜덤이라, 안 다루면 "결측률↔라벨" spurious 상관이 OOF만 띄우고 LB에서 죽는다. 위험 낮음, 누수 차단 효과 큼.
8. **per-subject surprisal/perplexity (#18–19)** — "하루의 의외성"을 단일 스칼라로. 독창적이고 상대 라벨과 직결. 위험: subject당 날짜가 적어 prior 추정 분산 큼 → pooled prior로 backoff 필요.
9. **취침 전 폰 사용(sleep hygiene, #69)** — S 타겟에 도메인적으로 가장 강한 단일 신호. 위험 낮음. cross-modal(#61, 수면 중 unlock)과 묶으면 더 강함.
10. **CV 재설계: LOSO + 시간순 인과 split** — 피처가 아니라 전제 조건. 이게 틀리면 위 9개의 검증이 전부 거짓말이 된다. OOF가 LB를 mirror하도록 split 자체를 LB 구조에 맞춰라.

> 공통 과적합 가드: 450행에 피처 100개는 금지. SSL로 임베딩을 얻고 **head는 작게(로지스틱/얕은 GBM)**, 피처는 LOSO 기반 selection으로 20개 내외만.

---

## 4. 바로 돌릴 수 있는 실험 5개

**실험 1 — 윈도우 재정의 + 타겟별 cutoff**
현재 피처 파이프라인을 wake-to-wake(또는 wake-to-survey)로 재구축. S는 취침 전까지, Q는 설문시각까지만 사용. 모델은 고정.

**실험 2 — subject ECDF 정규화 + deviation 피처**
모든 연속 피처를 subject 과거(unlabeled 포함, 시간순) percentile로 변환 + prototype 잔차 피처 추가.

**실험 3 — episode 토큰화 + Masked Episode SSL → frozen embedding**
unlabeled 전체로 MEM pretrain, day embedding을 frozen으로 뽑아 작은 head만 학습. raw feature 베이스라인과 비교.

**실험 4 — subject-adversarial 표현**
실험 3 인코더에 gradient-reversal subject 분류기 추가. 임베딩에서 subject를 못 맞히도록.

**실험 5 — per-subject 행동 surprisal 단일 피처**
subject별 episode 전이 Markov 모델 학습, today 시퀀스의 NLL/perplexity를 단일 피처로 추가.

---

## 5. 각 실험의 성공 기준 & 실패 해석

**실험 1**

- 성공: LOSO-OOF와 LB 격차 축소, 특히 S 타겟 개선.
- 실패(변화 없음): 누수 원인이 윈도우가 아니라 CV split 자체나 피처 정의에 있다 → 실험 외 누수 감사로 전환.
- 과적합: 거의 없음. 안 좋아져도 정보손실은 작음.

**실험 2**

- 성공: LOSO-CV 상승 + OOF-LB 격차 동시 축소(상대 라벨과 정렬됐다는 증거).
- 실패(LB만 하락): test subject가 train에 없거나, baseline 계산에 미래 날짜가 섞임 → percentile을 strictly past-only로 재계산하고 cold-start는 #76으로.
- 과적합: percentile은 파라미터가 없어 낮음. 다만 prototype 잔차가 labeled만으로 만들어졌으면 누수.

**실험 3**

- 성공: frozen SSL 임베딩이 raw feature 베이스라인을 LOSO에서 유의하게 능가.
- 실패(SSL ≈ random init): episode 분절이 너무 거칠거나 pretext가 라벨과 무관 → episode 정의를 세분화하고 pretext를 next-day forecasting(#95)으로 교체.
- 과적합: pretrain은 unlabeled라 안전. head가 크면 위험 → head를 더 줄여 재확인.

**실험 4**

- 성공: 임베딩의 subject 분류 정확도가 chance로 떨어지고 **동시에** LB 개선.
- 실패(subject 정확도는↓, LB도↓): 라벨이 subject base-rate와 상관 → subject 정보를 다 지우면 신호까지 손실. reversal 강도(λ)를 낮추고 subject 정규화를 따로 유지.
- 실패(subject 정확도 안 떨어짐): λ 부족 또는 임베딩 용량 과다 → λ 스케줄링.
- 과적합: subject-invariant는 일반화에 유리한 방향이지만, λ 과도 시 underfit. λ를 LOSO로 튜닝.

**실험 5**

- 성공: surprisal 단일 피처가 비자명한 OOF AUC를 갖고, 그 효과가 subject별로 부호 일관.
- 실패(subject별 분산 큼): subject당 날짜가 부족해 Markov prior가 불안정 → 전체 pooled prior + subject 보정의 hierarchical backoff로 전환.
- 과적합: 단일 피처라 위험 낮음. subject별로 부호가 뒤집히면 그건 과적합이 아니라 prior 추정 실패 신호.

---

남들이 잘 안 하는 포인트만 다시 추리면: **타겟별로 인과 cutoff를 다르게 두는 것**(#4), **결측을 confounder로 명시 모델링**(#56·#58), **subject 행동 perplexity / surprisal**(#18–19), **subject-adversarial로 shift를 표현 단계에서 제거**(#98), **per-subject autoencoder 재구성오차를 deviation 피처로 직접 생성**(#99) — 이 다섯 개가 비교 우위 날 만한 각도다. 특정 모달(가속도/GPS/폰)의 실제 스키마를 알려주면 episode 분절 규칙을 그 데이터에 맞춰 더 구체화해줄 수 있어.
