1. 가장 중요한 병목 진단 (5줄 요약)
   • 극단적인 데이터 불균형: 10명이라는 극소수 Subject의 개인 간 변동성(Subject Shift)과 450개라는 빈약한 라벨 수가 결합되어, 정규 지도학습 시 모델이 '상태'가 아닌 '개인의 고유 ID'를 외워버리는 치명적 과적합이 발생합니다.
   • 타겟의 상대성 오해: Q1~Q3, S1~S4 타겟은 절대적 고정 상태가 아닌 '평소 대비 오늘의 변동'을 의미하므로, 절대적인 수치 피처를 그대로 주입하면 Panel Drift와 Target Mean Shift에 무방비로 노출됩니다.
   • 시공간 격자의 경직성: 하루를 00시~24시의 고정된 물리적 격자로만 해석하여, 개인별 생체 리듬(Chronotype)의 차이와 불규칙한 이벤트 에피소드가 만들어내는 동적 맥락과 선후 관계를 포착하지 못하고 있습니다.
   • 결측치 처리의 도메인 부재: 대량의 센서 누락(Missingness)을 단순 노이즈나 제거 대상으로 취급함으로써, 기기 방치나 인위적 차단 등 결측 자체가 내포하는 심리적·상태적 시그널을 토큰 표상에 반영하지 못하고 있습니다.
   • 표상 변환 메커니즘의 부재: 방대한 무라벨 원천 데이터의 시계열 구조를 Transformer나 Diffusion 모델이 받아들이기 좋은 이산적 토큰(Discrete Token)이나 일관된 기하학적 공간으로 압축하는 자기지도학습(SSL) 레이어가 생략되어 있습니다.
2. 도메인 관점의 데이터 표상/엔지니어링 아이디어 100개
   Ⅰ. 하루를 다르게 쪼개는 대안적 타임 슬라이싱 (1~12)
3. Chronotype-aligned Day (생체시계 슬라이싱): 최근 7일간의 평균 수면 진입 시점을 기준으로 하루를 정의합니다. (예: 새벽 2시 취침자는 새벽 2시부터 익일 새벽 2시까지를 하루 토큰 패치로 구성)
4. First-Action Triggered Day: 아침에 깨어나 최초로 스마트폰 화면을 잠금 해제하거나 걸음 수가 발생한 시점을 Day Start(T=0)로 설정하여 개인별 타임라인을 정렬합니다.
5. Social Jetlag Window Slicing: 평일과 주말의 수면 중심점(Mid-sleep) 차이를 계산하고, 이 격차가 발생하는 금요일 밤~토요일 오전 구간을 별도의 프리-이벤트 세그먼트로 격리합니다.
6. Melatonin Onset Proxy Window: 일몰 시간 및 개인별 야간 스마트폰 블루라이트 노출 시작점부터 실제 수면 진입까지의 기간을 '하루의 마감 세그먼트'로 단독 캡슐화합니다.
7. Core Active Anchor Slicing: 일일 총 걸음수의 80%가 집중되는 고활동 구간(Core Active Phase)을 중심축으로 두고 앞뒤로 6시간씩 슬라이싱하여 동적 윈도우를 구성합니다.
8. Inter-Sleep Interval (ISI): 수면과 수면 사이의 순수 깨어있는 시간(Wake Episode) 전체를 하나의 독립된 시퀀스 길이로 취급하여 고정 격자 압박을 탈피합니다.
9. Battery Charging Cycle Slicing: 스마트폰 충전기 플러그인/플러그아웃 시점을 기준으로 '귀가 및 휴식 상태'와 '외출 및 외부 활동'의 물리적 경계를 재정의합니다.
10. Light-Pollution Boundary: 주변 조도 센서가 최저치로 떨어지는 소등 시점을 기준으로 하루의 심야 데이터 세그먼트 시작점을 동적 설정합니다.
11. Geographic Home-Stay Boundary: GPS상 '집'을 벗어난 첫 시점과 다시 복귀한 마지막 시점을 기준으로 외출(Active Era)과 잔류(Rest Era)로 이분할 슬라이싱합니다.
12. Commute-Informed Slicing: 이동 속도가 시속 15km 이상으로 지속되는 통근 에피소드를 감지하여, 통근 전(Pre-commute), 통근 중(Transit), 통근 후(Post-commute)로 하루를 3분할합니다.
13. Cognitive Fatigue Accumulation Window: 마지막 수면 종료 후 12시간이 지난 시점부터 취침 전까지의 고피로 구간(Fatigue Window)을 분리하여 후반부 센서 변동성에 가중치를 부여합니다.
14. Micro-nap Boundary: 낮 시간대 30분 이상의 가속도계 정지 및 폰 미사용 구간을 '미니 수면' 경계로 잡고 전후 활동 에너지 복원력을 평가하는 윈도우를 구성합니다.
    Ⅱ. Subject별 평소 루틴 대비 이탈도 (Deviation) 표상 (13-25)
15. Subject Z-Score Embedding: 각 센서 피처를 개인의 전체 기간 평균/표준편차로 정규화한 뒤, 이를 스칼라가 아닌 차원별 임베딩 벡터로 변환하여 입력합니다.
16. Personal Routine Entropy Vector: 요일별/시간대별 위치 및 행동의 정보 엔트로피를 계산하여, 오늘의 행동이 개인의 '평소 예측 가능성'에서 얼마나 벗어났는지 Routine Deviation Score를 표현합니다.
17. Home-Radius Deviation Metric: 평소 특정 요일에 이동하는 최대 반경 대비 오늘의 최대 이동 반경 비율을 로그 스케일링하여 부호화합니다.
18. App Usage Diversity Shift: 평소 자주 쓰는 상위 5개 앱의 사용 시간 비율과 오늘의 사용 시간 비율 간의 KL-Divergence를 벡터화합니다.
19. Velocity of Routine Breakdown: 루틴에서 벗어나기 시작한 시점(예: 평소엔 집에 있을 시간인데 외출 중)의 가속도 및 지속 시간을 통해 '루틴 이탈 속도'를 측정합니다.
20. Chronological Quantile Mapping: 오늘의 수면 지속 시간을 개인의 역대 수면 분포 상 몇 분위(Quantile)에 위치하는지로 매핑하여 상댓값 토큰으로 변환합니다.
21. Location Transition Matrix Deviation: 장소 A \rightarrow B \rightarrow C 전환 확률 행렬(Markov Chain)을 개인별로 구축하고, 오늘의 전환 행렬과 평소 행렬 간의 Frobenius Norm을 계산합니다.
22. Circadian Rhythm Amplitude Shift: 24시간 코사인 피팅(Cosine Fitting)을 통해 도출된 개인별 고유 진폭(Amplitude)과 위상(Phase)이 오늘 하루 동안 얼마나 Shift 되었는지 델타값을 임베딩합니다.
23. Personal Screen-Time Baseline Contrast: 개인별 주간/야간 스마트폰 사용량 베이스라인 대비 오늘의 사용량 초과/미달 분(Minute)을 정부호(Signed) 임베딩합니다.
24. Activity Intensity Quantile Vector: 가속도 센서의 Magnitude를 개인별 Threshold 기준으로 Low/Med/High로 재정의하여 개인화된 물리 활동 강도 토큰을 생성합니다.
25. Subjective Space-Time Budget Deviation: 개인이 주로 머무는 공간 Top 3의 체류 시간 예산(Time Budget) 배분이 평소 대비 얼마나 왜곡되었는지 10차원 벡터로 표현합니다.
26. Wake-up Delay Vector: 알람이 울린 후 또는 첫 폰 센서 활성화까지 걸린 시간이 개인 평균 대비 몇 분 지연되었는지 계량화합니다.
27. Social Communication Density Deviation: 평소 대비 오늘의 문자/통화/메시징 앱 활성화 빈도의 Z-score 벡터 레이어를 추가합니다.
    Ⅲ. 멀티 스케일(최근 7/14/28일) 기하학적 비교 (26-38)
28. 7-Day Dynamic Baseline Attenuation: 최근 7일간의 지수이동평균(EMA)을 베이스라인으로 잡고, 오늘의 센서 패턴과의 차이를 감쇠 함수(Decay Function)를 적용해 표현합니다.
29. 14-Day Sleep Debt Accumulation: 최근 14일간의 권장 수면 시간 대비 누적 수면 부족량(Sleep Debt)을 누적 차원 토큰으로 정의하여 피로 상태 타겟의 컨텍스트로 제공합니다.
30. 28-Day Monthly Rhythm Proxy: 장기적인 생체 리듬의 잠재적 영향력을 고려하여, 28일 윈도우 내에서의 상대적 Day Position을 사인/코사인 임베딩으로 인코딩합니다.
31. Multi-Scale Volatility Cascade: 최근 3일, 7일, 14일, 28일의 걸음 수 변동성(Volatility)이 계층적으로 감소하거나 증가하는 추세를 Haar Wavelet 변환의 계수 형태로 표현합니다.
32. Weekend-to-Weekday Transition Shock: 주말(토/일)의 불규칙성이 월요일/화요일 평일 센서 데이터에 미치는 잔존 충격량(Carry-over Effect)을 최근 7일 윈도우로 계산합니다.
33. Recent 7-Day Location Novelty Score: 최근 7일 동안 한 번도 방문하지 않았던 새로운 GPS 격자에 머문 시간의 총합을 계산하여 '낯선 환경 노출도'를 표현합니다.
34. 14-Day Screen Fatigue Index: 최근 14일간 야간 폰 사용 시간의 누적 선형 추세(Slope)를 구해 피로 누적 가속도를 표상합니다.
35. 28-Day Social Isolation Counter: 최근 28일간 외부 활동 및 통신 빈도가 지속적으로 하향 곡선을 그리는지 여부를 이진 트리 깊이(Tree Depth)로 부호화합니다.
36. 7-Day Circadian Phase Drift: 최근 7일간 취침 시점이 매일 조금씩 뒤로 밀리는 현상(Phase Drift)을 선형 회귀 기울기로 뽑아내어 임베딩합니다.
37. Multi-scale Missingness Frequency: 최근 3/7/14/28일간 발생한 센서 결측 에피소드의 빈도 변화율을 통해 기기 방치 또는 불규칙성 추세를 파악합니다.
38. Step Count Recovery Rate: 대량의 신체 활동이 있은 후(예: 걸음수 폭발) 최근 3일간 활동량이 급감하는 '신체적 회복기' 패턴을 7일/14일 평균과 비교하여 정규화합니다.
39. Dynamic Time Warping (DTW) Distance Evolution: 최근 7일간의 일일 시계열과 오늘 시계열 간의 DTW 거리가 점진적으로 멀어지는지 가까워지는지의 추세 벡터를 추출합니다.
40. Historical Context Memory Bank: 모델 입력 시, 현재 일자 데이터와 함께 최근 7일간의 대표 일일 임베딩 벡터를 고정 크기 메모리 뱅크 형태로 Concatenate하여 입력합니다.
    Ⅳ. 에피소드 중심 서사적 파싱 (39-50)
41. Sleep Fragmentation Token: 수면 중 가속도계 센서의 미세 움직임이나 폰 화면 켜짐 사건을 추출하여 '수면 분절성(Fragmentation)'의 밀도를 나타내는 가우시안 커널 밀도 토큰을 생성합니다.
42. Insomnia-Proxy Window: 새벽 1시~5시 사이에 폰이 켜지거나 뒤집히는 물리적 센서 변화가 발생한 에피소드를 '불면 가능성 시그널'로 묶어 시간-강도 튜플로 토큰화합니다.
43. Bedtime Procrastination Score: 침대에 누웠을 것으로 추정되는 시간(가속도 급감 및 홈 GPS)과 실제 마지막 폰 사용 종료 시간 사이의 갭을 '취침 미루기 미닛'으로 정의합니다.
44. Morning Sluggishness Episode: 기상 후 최초 1시간 동안의 걸음 수 축적 속도가 평소 기상 직후 패턴 대비 얼마나 완만(Sluggish)한지를 나타내는 S-곡선 피팅 파라미터입니다.
45. Phantom Phone Check Density: 화면은 켜졌으나 앱 실행이나 터치 입력 없이 수초 내에 다시 꺼진 사건(단순 화면 확인)의 시간당 빈도를 '불안/강박 에피소드'로 임베딩합니다.
46. Extended Sedentary Episode Block: 깨어 있는 동안 걸음 수가 0이고 폰 움직임도 없는 상태가 3시간 이상 지속된 에피소드를 '고정적 고립 상태' 토큰으로 지정합니다.
47. Missingness as an Intentional Episode: 센서 데이터가 완전히 끊긴 구간을 순수한 결측이 아니라, 기기 전원 오프 또는 극도의 로우 액티비티 상태인 '의도적 차단 에피소드(Blackout)'로 레이블링하여 토큰화합니다.
48. Geographic Escape Episode: 평소 활동 반경을 300% 이상 벗어난 원거리 이동 에피소드를 '여행/탈출' 상태로 정의하고, 해당 에피소드의 지속 시간을 인코딩합니다.
49. Binge Screen Usage Episode: 스마트폰을 한 번도 끄지 않고 연속으로 2시간 이상 활성화한 에피소드를 '컨텐츠 중독/도피' 토큰으로 추출합니다.
50. Sudden Midnight Mobility: 자정 이후에 GPS 위도가 변경되거나 걸음 수가 발생하는 이례적 야간 이동 에피소드를 '야간 활동성' 특이치 토큰으로 정의합니다.
51. Pre-Sleep Digital Consumption Velocity: 취침 전 30분 동안의 화면 전환 및 데이터 트래픽 속도(Velocity)를 계산하여 뇌 각성 유도 에피소드로 표상합니다.
52. Continuous Missingness Acceleration: 결측 구간의 길이가 전날 대비 기하급수적으로 길어지는 현상을 '참여도 저하 및 우울 지표' 에피소드로 정의합니다.
    Ⅴ. 멀티모달 Cross-Modal 상호작용 및 정렬 (51-63)
53. Screen-On vs. Acceleration Cross-Attention Matrix: 스마트폰 화면이 켜져 있는 시간축과 실제 사용자의 물리적 걸음 수/가속도 시간축 간의 Cross-Attention 맵을 스태틱 이미지 형태로 변환하여 구조적 입력으로 활용합니다.
54. GPS Velocity vs. Step Sync Coherence: GPS 기반 이동 속도와 걸음 수 센서의 동기화 정도를 계산합니다. (차량/대중교통 이용 시 GPS는 높고 걸음 수는 낮음 \rightarrow '수동적 이동 상태' 토큰)
55. Ambient Light vs. App Category Matching: 조도 센서가 극도로 낮은 암전 상태에서 주로 실행된 앱 카테고리(엔터테인먼트 vs 생산성)의 상호작용 매트릭스를 생성합니다.
56. Audio/Media State vs. Location Context: 이어폰 플러그인 또는 미디어 재생 상태와 현재 GPS 장소(집, 직장, 길거리)를 결합하여 '이동 중 청취', '휴식 중 청취' 등의 교차 토큰을 생성합니다.
57. Missingness-Location Dependency Profile: 데이터 결측이 주로 발생하는 특정 GPS 위치(예: 기지국 음영지역, 특정 건물 내)를 파악하여, 결측이 장소 특성인지 심리적 상태인지 분리하는 가중치 맵을 만듭니다.
58. Notification Response Latency Cross-Modal: 푸시 알림이 발생한 시점(시스템 로그)과 사용자가 스마트폰 가속도를 발생시키며 잠금을 해제한 시점 간의 갭(반응 지연 시간)을 통한 인지적 가용성 임베딩입니다.
59. Wifi Scan Dynamics vs. Screen-on correlation: 와이파이 AP 변경 빈도(주변 환경 변화)와 화면 켜짐 빈도의 상관계수를 실시간 계산하여 멀티모달 자극 민감도 지표를 구축합니다.
60. Asynchronous Multi-modal Imputation Embedding: 하나의 센서가 결측될 때 다른 센서들의 상태(예: GPS 결측 시 가속도는 활성화)를 조건부 확률 벡터로 채워 넣는 임베딩 레이어를 설계합니다.
61. Screen-on Duration normalized by Step Count: 오늘 걸은 1000걸음당 스마트폰 사용 시간 분(Minute)을 구하여, 물리적 활동 대 디지털 활동의 상대적 선호도 밸런스 지표를 표상합니다.
62. Location Entropy weighted by Screen Time: 스마트폰을 주로 사용하는 장소의 다양성을 Shannon Entropy로 계산하고, 이를 장소별 스마트폰 사용 시간으로 가중치를 부여합니다.
63. Charging State vs. Physical Immobility: 스마트폰이 충전 중일 때 사용자의 가속도가 잡히지 않는 '기기-사용자 동시 정지'와 충전 중임에도 사용자가 폰을 만지는 '기기 결착형 사용'을 분리하여 표상합니다.
64. Geographical Displacement vs. Screen Interaction Dispersal: 이동 거리 단위(km)당 화면 잠금 해제 횟수의 비율을 계산하여 이동 중 스마트폰 중독도 벡터를 생성합니다.
65. Multi-modal Contrastive Alignment Space: CLIP 구조를 모방하여, 하루의 [GPS/이동 시퀀스] 임베딩과 [스마트폰 사용 시퀀스] 임베딩이 서로 같은 날짜 벡터 공간에서 정렬되도록 대조 학습 프로젝션 레이어를 구성합니다.
    Ⅵ. Motif, Prototype 기반 Retrieval 표상 (64-75)
66. K-Shape Time-Series Motif Cluster ID: 무라벨 원천 데이터의 일일 걸음 수 시계열 패턴을 K-Shape 알고리즘으로 클러스터링하여 대표 '활동 모티프(Motif) ID'를 부여하고 이를 원핫 토큰으로 변환합니다.
67. Nearest Neighbor Day Retrieval Context: 현재 타겟 날짜의 센서 표현 벡터와 가장 유사한 과거 무라벨 날짜 Top 3를 코사인 유사도로 검색(Retrieval)하고, 그날들의 센서 표현을 컨텍스트로 함께 피딩합니다.
68. Day Prototype Representation via VQ-VAE: 일일 멀티모달 시계열 데이터를 이산화(Quantization)하는 VQ-VAE를 학습시켜, 하루를 16개의 코드북 벡터(Prototype Tokens) 시퀀스로 압축 변환합니다.
69. Graph-based Day Similarity Network: 모든 날짜를 노드로 하고 센서 유사도를 엣지로 하는 KNN 그래프를 구축하여, 각 날짜 노드의 GNN 임베딩을 추출함으로써 분포 시프트를 보정한 표상을 획득합니다.
70. Anomalous Day Soft-Labeling: 정상 루틴 모티프들과의 마할라노비스 거리를 계산하여, 오늘의 하루가 '얼마나 기이한 하루(Anomaly Score)였는지'를 나타내는 연속형 스코어 벡터를 주입합니다.
71. Circadian Rhythm Prototype Codebook: 24시간 센서 데이터를 각 서카디안 패턴 프로토타입 8개 유형으로 분류하고, 오늘 하루가 각 프로토타입에 속할 소프트 확률 분포를 입력값으로 할당합니다.
72. Topological Data Analysis (TDA) Persistence Landscape: 일일 가속도 및 GPS 포인트의 클라우드 데이터에 TDA를 적용하여 지속성 풍경 특징을 추출, 하루의 구조적 복잡성을 고정 차원 벡터화합니다.
73. Dynamic Time Warping Barycenter Average (DBA) Baseline: 개인별로 가장 전형적인 하루의 시계열 평균(DBA)을 미리 연산해 두고, 오늘 시계열과의 픽셀 단위 델타 맵을 생성하여 컨볼루션 입력화합니다.
74. Contextual Day Sub-sequence Matching: 하루를 4시간 단위의 6개 서브 시퀀스로 쪼갠 뒤, 각 서브 시퀀스가 전체 유저 데이터베이스의 어떤 시간대 모티프와 일치하는지 매칭 딕셔너리 지표화합니다.
75. Cross-Subject Motif Sharing Index: 10명의 유저 전체에서 공통으로 발견되는 '보편적 휴일 패턴', '보편적 마감 패턴' 등의 글로벌 모티프를 정의하고 오늘 하루가 해당 글로벌 패턴에 부합하는지 인덱싱합니다.
76. Day-level Self-Attention Pooling Vector: 일일 센서 데이터를 Transformer Encoder에 통과시킨 뒤, 클래스 토큰이 아닌 가우시안 혼합 모델(GMM) 기반 어텐션 풀링을 거친 고차원 고정 벡터 표상을 사용합니다.
77. DBSCAN Of Daily Venues: 오늘 방문한 GPS 좌표들을 DBSCAN 처리하여 추출된 '의미 있는 장소의 개수'와 '노이즈 포인트(단순 스쳐 지나간 길)의 비율'을 일일 프로토타입 벡터의 축으로 설정합니다.
    Ⅶ. Target별 특화 전용 데이터 뷰 (76-85)
78. [Q1 수면 질 특화] Pre-sleep Restlessness Index: 취침 전 2시간 동안 가속도 센서의 미세 진폭 변동성의 분산 값을 극대화한 뷰를 제공합니다.
79. [Q1 수면 질 특화] Sleep Stage Transition Proxy: 야간 폰 터치 전무 구간 중 가속도계의 주기적 뒤척임 패턴(30~45분 주기 신체 움직임)의 규칙성을 주파수 도메인(FFT)으로 변환한 파워 스펙트럼 뷰입니다.
80. [Q2 정서/우울 특화] Digital Isolation Speed: 외부 연락(통화, 메시지 앱) 빈도는 극감하면서 유튜브/넷플릭스 등 단방향 미디어 앱 사용 시간만 폭증하는 불균형 비율 뷰를 구축합니다.
81. [Q2 정서/우울 특화] Locational Constriction Vector: GPS 상 이동 반경이 집 반경 50m 이내로 극단적으로 좁혀진 상태의 지속 일수를 카운트한 누적 시계열 뷰입니다.
82. [Q3 스트레스 특화] Acceleration Jerk Metric: 일상 활동 중 가속도의 미분값인 'Jerk(급격한 가속도 변화량)'의 밀도를 계산하여 신체적 긴장도 및 초조함을 반영하는 뷰를 생성합니다.
83. [Q3 스트레스 특화] Screen-On Fragment Density: 스마트폰을 한 번 켜서 오래 쓰는 것이 아니라, 1~2분 간격으로 켰다 껐다를 반복하는 '극도의 산만함/초조함' 상태를 포착하는 포아송 분포 파라미터 뷰입니다.
84. [S1~S4 활력 특화] Circadian Power Peak Shift: 일일 걸음수 및 활동량의 피크(Peak)가 발생하는 시간대가 평소 대비 앞으로 당겨졌거나 뒤로 밀렸는지 파악하는 에너지 위상 뷰를 만듭니다.
85. [S1~S4 활력 특화] Physical Fatigue Recovery Slope: 전날 과도한 활동(평소 대비 걸음수 200%)이 있은 후, 오늘 오전 시간대의 활동성 회복 탄력성(Recovery Slope)을 모델링한 전용 뷰입니다.
86. [S1~S4 활력 특화] Total Energy Expenditure Proxy: 가속도 센서의 3축 적분값(METs 프록시)을 시간별로 누적하여, 신체 에너지 소모 곡선과 베이스라인 곡선 간의 면적 차이(AUC)를 계산하는 뷰입니다.
87. [Target Multi-Task Routing] Cross-Target Gate Vector: 7개 라벨 간의 상관관계를 고려하여, Q계열(심리)과 S계열(신체)에 각각 다른 가중치를 주도록 멀티모달 센서를 다르게 소프트-필터링(Soft-filtering)한 게이트 인터페이스 뷰를 구축합니다.
    Ⅷ. 시퀀스 모델(Transformer/Enc-Dec) 입력용 토큰화 (86-93)
88. Hierarchical Time-Scale Tokenizer: 1분을 단어 토큰, 1시간을 문장 토큰, 하루를 하나의 문서 토큰으로 계층화하여, 센서 수치를 분 단위 텍스트 형태의 토큰 링(Token Ring)으로 패치화합니다.
89. Quantized Sensor Word Vocabulary: 센서 데이터(가속도 강도, GPS 이동 속도 등)의 연속적인 값을 복합 벤치마킹을 통해 1000개의 고유한 '라이프로그 단어' 사전으로 양자화하여 BPE(Byte Pair Encoding) 토큰화를 적용합니다.
90. State-Duration Tuple Token: [행동 상태 토큰, 지속 시간 토큰]의 쌍(Tuple)으로 변환(예: [HOME_REST, 120min], [COMMUTE, 45min])하여 순서와 듀레이션을 Transformer가 명확히 인지하게 합니다.
91. Positional Sync Embedding for Missingness: 결측 구간에 대해 빈 토큰을 넣는 대신, 결측이 시작된 절대 시간과 지속 시간을 주입하는 고유의 'Missing-Positional Embedding' 레이어를 추가합니다.
92. Multi-modal Unified Token Sequence: 여러 센서 스트림을 따로 넣지 않고 시간 순서대로 인터리빙(Interleaving)하여 나열(예: GPS_Move \rightarrow Screen_On \rightarrow App_SNS \rightarrow Step_High)하는 싱글 트랙 토큰 시퀀스를 만듭니다.
93. Dynamic Time-Delta Token: 고정 시간 격자가 아닌 센서 이벤트가 바뀔 때만 토큰을 생성하되, 이전 토큰과의 시간 차이(Delta-T)를 양자화하여 독립된 토큰으로 시퀀스 사이에 삽입합니다.
94. Circadian Phase Fixed Token: 하루의 타임라인을 24개 고정 슬롯으로 만들고, 각 슬롯에 [활동 강도, 장소 안정성, 디지털 밀도]를 나타내는 3개의 특수 이산 토큰 조합으로 채워 넣습니다.
95. Task-Specific Special Tokens ([Q1], [S1]): BERT의 [CLS] 토큰처럼 시퀀스 맨 앞에 [Q1_SENSE], [S1_SENSE] 등 각 타겟 예측에 바이어스된 특수 토큰을 심어 인코더-디코더 연산을 유도합니다.
    Ⅸ. 라벨 부족 우회용 자기지도학습(SSL) Proxy Target (94-100)
96. Masked Lifelog Forecasting (MLF): 하루 시퀀스의 특정 시간대(예: 오후 2시~6시) 전체 멀티모달 센서 데이터를 마스킹하고, 전후 데이터를 통해 마스킹된 구간의 센서 분포를 복원하는 인코더-디코더 사전 학습을 진행합니다.
97. Subject-Invariant Contrastive Learning: 동일한 유저의 다른 날짜는 네거티브로, 서로 다른 유저라도 '동일한 루틴 패턴(예: 주말 늦잠)'을 가진 날짜는 포지티브로 묶어 유저 고유 ID에 과적합되지 않도록 유저 불변 표상을 학습시킵니다.
98. Temporal Order Permutation Restoration: 하루를 4개의 블록(새벽, 오전, 오후, 저녁)으로 쪼갠 뒤 무작위로 셔플하고, 디코더 모델이 올바른 시간 순서로 재배치하도록 하는 순서 복원 학습을 수행합니다.
99. Multi-modal Transformation Prediction: 시계열 데이터에 가우시안 노이즈 주입, 시간축 확대/축소, 값 반전 등의 변형을 가한 뒤 어떤 변형이 적용되었는지 분류하는 자가 지도 태스크를 수행합니다.
100. Tomorrow Sensor Context Conditioning: 오늘 데이터의 표상을 입력받아, '내일 오전의 첫 기상 시간 및 첫 걸음 수 격차'를 정량적으로 회귀 예측하게 하는 미래 바운딩 자가 학습을 진행합니다.
101. Pseudo-Label Distillation with Mean Constraints: 라벨이 없는 대량의 데이터에 의사 라벨을 생성하되, 분포 시프트를 막기 위해 전체 데이터셋의 타겟 평균 비율(Target Mean Ratio)을 제한 조건으로 걸어 학습시킵니다.
102. Sensor Cross-Synthesis (Cross-Generation): 스마트폰 사용량 및 앱 시퀀스 데이터만 보고 당일의 GPS 이동 궤적 및 걸음수 시계열 곡선을 생성해 내거나 그 반대를 수행하게 하는 인코더-디코더 기반 상호 증강 자기지도학습을 구축합니다.
103. 가장 유망한 Top 10 아이디어 선정 및 이유
     번호 아이디어 명칭 선택 이유 (과적합 방지 및 LB 일반화 관점)
     13 Subject Z-Score Embedding 타겟이 '평소 대비 오늘'이므로 개인 편차(Subject Shift)를 물리적으로 제거하는 가장 확실한 수학적 장치입니다.
     95 Subject-Invariant Contrastive Learning 모델이 10명의 유저 고유 패턴을 암기하는 것을 차단하고, 오직 '하루의 변동 상태'만 보게 강제하는 핵심 SSL입니다.
     66 Day Prototype via VQ-VAE 연속형 수치의 노이즈와 결측을 강건한 이산형 코드북 토큰으로 변환하여 Transformer의 다이나믹스 최적화를 돕습니다.
     94 Masked Lifelog Forecasting (MLF) 450개 라벨 병목을 무라벨 원천 데이터 수만 개로 깨부술 수 있는 전형적이면서도 강력한 생성 모델 기반 SSL입니다.
     88 State-Duration Tuple Token 고정 격자 패딩으로 인한 계산 낭비를 막고, 행동의 순서와 듀레이션을 동시에 보존하여 Transformer 입력 효율을 극대화합니다.
     1 Chronotype-aligned Day Slice 올빼미형 인간과 아침형 인간의 00시 센서를 동일 선상에서 비교하여 발생하는 도메인 왜곡과 변동성 시프트를 차단합니다.
     45 Missingness as Intentional Episode 결측을 '에러'가 아닌 '심리적 도피/방치'라는 중요한 고차원 상태 시그널로 역발상 전환하여 타겟 예측의 힌트를 제공합니다.
     27 14-Day Sleep Debt Accumulation Q1(수면), S1(활력) 등은 당일 센서뿐 아니라 누적된 생체 피로도에 종속되므로 타겟의 시간적 인과 관계를 보완합니다.
     51 Screen-On vs. Accel Cross-Attention 물리 활동과 디지털 몰입의 불일치성(예: 누워서 폰만 하기 vs 뛰어다니기)을 직접 연결하여 심리적 상태(Q2, Q3)를 날카롭게 짚어냅니다.
     99 Pseudo-Label with Mean Constraints Public LB와 Local OOF 간의 가장 큰 괴리 원인인 Target Mean Shift를 의사 라벨링 단계에서 정밀 제어하여 일반화 성능을 붙잡아둡니다.
104. 바로 실험 가능한 5개 실험 파이프라인
     [실험 1] VQ-VAE 토큰화 기반의 Masked Lifelog Forecasting 사전 학습
     • 설계: 대량의 무라벨 원천 데이터를 1시간 단위 패치로 묶어 가속도, GPS, 폰 상태를 연속형 변수로 VQ-VAE에 통과시켜 이산 토큰 시퀀스로 변환합니다. 이후, 하루 치 토큰의 30%를 마스킹하고 Transformer Decoder를 통해 이를 복원하는 사전 학습을 거친 후, 450개 라벨로 Fine-tuning합니다.
     • 과적합 위험 평가: VQ-VAE 코드북 크기가 너무 크면 특정 유저의 고유 노이즈까지 압축하므로 코드북 사이즈를 256 이하로 타이트하게 제한해야 합니다.
     [실험 2] Subject ID 제거를 위한 Adversarial Subject-Invariant 표상 학습
     • 설계: 인코더 뒷단에 두 개의 Head를 둡니다. 하나는 7개 타겟 라벨을 예측하고, 다른 하나는 Gradient Reversal Layer(GRL)를 거쳐 10명의 Subject ID를 분류하게 합니다. 모델이 유저가 누구인지는 맞추지 못하면서 오늘의 상대적 상태는 맞추도록 적대적 학습을 유도합니다.
     • 과적합 위험 평가: 유저 식별 정보가 너무 완벽히 지워지면 개인별 베이스라인 정보까지 손실될 수 있으므로, 입력 단에 아이디어 13번(Z-score 피처)을 먼저 결합해 준 상태에서 진행해야 안전합니다.
     [실험 3] [State-Duration] 튜플 토큰 트리거 기반 Encoder-Decoder 아키텍처
     • 설계: 일일 데이터를 시간 순서대로 이벤트가 변할 때만 이산 토큰화합니다. [HOME_REST, 180] \rightarrow [COMMUTE, 40] \rightarrow [WORK_ACTIVE, 240] \rightarrow [BLACKOUT_MISSING, 120]. 이 시퀀스를 T5나 BART 구조의 소형 인코더-디코더에 입력하고, 디코더의 첫 7개 아웃풋 토큰이 Q1~S4의 Binary 값을 생성하도록 배치합니다.
     • 과적합 위험 평가: 특정 에피소드 유형(예: 장시간 결측)이 데이터셋 전체에 지배적일 경우 디코더가 편향될 수 있으므로, 시간(Duration) 토큰은 로그 스케일링 후 양자화하여 주입합니다.
     [실험 4] 14일 누적 생체 부채(Temporal Debt) 컨텍스트 주입 효과 검증
     • 설계: 기존 베이스라인 모델 입력단에 아이디어 27번(14일간 누적 수면 부족 분량) 및 아이디어 32번(14일간 야간 스크린 사용 선형 추세 기울기)을 컨텍스트 임베딩 벡터로 변환하여, 일일 Transformer 패치 벡터의 맨 앞에 프리펜드(Prepending)하고 기존 타겟 분류 레이어와 연결합니다.
     • 과적합 위험 평가: 연속된 날짜가 Train/Valid로 쪼개질 때 데이터 누수(Data Leakage)가 발생할 수 있으므로, 반드시 Subject-wise 혹은 대규모 Group Time-Series Split으로 Validation을 격리해야 합니다.
     [실험 5] Target Mean Constraint 기반 무라벨 데이터 Pseudo-Label Distillation
     • 설계: 450개 라벨로 학습된 초기 소형 모델을 활용하여 전체 무라벨 데이터의 타겟 예측 확률(Soft Label)을 뽑아냅니다. 이때 예측된 무라벨의 positive 비율이 기존 450개 라벨의 positive 비율(\pm 5\%) 안으로 들어오도록 임계값(Threshold)을 동적으로 캘리브레이션한 뒤, 이 의사 라벨셋을 합쳐 전체 모델을 재학습(Distillation)합니다.
     • 과적합 위험 평가: 잘못된 예측이 확증 편향(Confirmation Bias)을 일으켜 Public LB를 망칠 수 있으므로, 의사 라벨의 손실 함수 가중치는 초기에는 0.2 수준으로 낮게 설정하고 점진적으로 올립니다.
105. 각 실험의 성공 기준 및 실패 시 도메인 관점의 해석 가이드
     [실험 1] 성공/실패 가이드
     • 성공 기준: 450개 라벨 세트에서의 Local OOF F1-Score가 베이스라인 대비 +0.04 이상 상승하고, 마스킹 복원 SSL Loss가 안정적으로 수렴합니다.
     • 실패 시 해석: SSL Loss는 떨어지는데 튜닝 후 라벨 예측 성능이 떨어진다면, VQ-VAE가 '상태 변동'이 아니라 센서 고유의 '하드웨어 노이즈 및 수집 주기 기하학'을 압축하는 데 치중한 것입니다. 패치 크기를 키우거나 가속도 축에 오그멘테이션을 더 강하게 가해야 합니다.
     [실험 2] 성공/실패 가이드
     • 성공 기준: Subject 분류 정확도가 10\% (임의 찍기 수준)에 수렴함과 동시에, Public LB 점수가 Local OOF 점수와 동기화되며 동반 상승합니다.
     • 실패 시 해석: 타겟 예측 성능까지 전멸한다면, 10명의 유저 경계를 지우는 과정에서 '상태 변동'을 나타내는 유효 성분까지 함께 소거된 것입니다. GRL의 가중치(람다)를 낮추거나, 유저를 완전히 지우기보다 유저 고유 베이스라인 피처를 명시적으로 분리 주입하는 방향으로 선회해야 합니다.
     [실험 3] 성공/실패 가이드
     • 성공 기준: 결측 구간(Missingness)이 많은 날짜들에서 타겟 클래스 예측 정확도가 대폭 상승하고, 시퀀스 길이가 가변적으로 줄어들어 학습 속도가 3배 이상 빨라집니다.
     • 실패 시 해석: 모델이 모든 타겟을 다수 클래스(Majority Class)로 고정 출력한다면, 이벤트 이산화 과정에서 미세한 수치 변동(예: 걸음걸이 속도의 미세한 저하)이 유실되어 '피로도'나 '스트레스'의 촉발 시그널이 텍스트성 토큰 뒤로 숨어버린 것입니다. 토큰 사전을 더 촘촘하게 재양자화(Granularity 강화)해야 합니다.
     [실험 4] 성공/실패 가이드
     • 성공 기준: 특히 수면 질(Q1)과 신체 활력(S1, S2) 타겟에서 대폭적인 성능 향상이 관찰되며, 월요일~화요일 데이터의 오예측률이 크게 감소합니다.
     • 실패 시 해석: Local OOF는 대폭 올랐으나 Public LB가 폭락한다면, 테스트 데이터셋에 존재하는 유저들의 타임라인 기록이 불연속적이거나 14일 치 연속 베이스라인을 잡을 수 없는 단절된 패널 데이터일 가능성이 높습니다. 이 경우 14일 고정 스케일 대신 아이디어 26번처럼 과거 데이터 개수에 비례해 가중치가 줄어드는 EMA 감쇠 표상으로 전환해야 합니다.
     [실험 5] 성공/실패 가이드
     • 성공 기준: Public LB 스코어의 변동성이 안정화되고, Local CV와 Public LB 간의 점수 격차(Gap)가 30\% 이상 좁혀집니다.
     • 실패 시 해석: 재학습 후 전반적인 성능이 오히려 후퇴한다면, 초기 450개 라벨 모델이 가졌던 편향(Bias)이 대량의 무라벨 데이터에 오염을 일으킨 것입니다. Constraint 조건을 더 엄격하게 조이거나, Soft Label을 그대로 쓰지 않고 최고 신뢰도 상위 5\% 데이터만 Hard Label로 변환하여 추가하는 큐레이션 알고리즘으로 변경해야 합니다.
