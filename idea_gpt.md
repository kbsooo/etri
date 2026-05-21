## 1. 가장 중요한 병목 진단 5줄

1. 이 문제의 하루는 `00:00~24:00`가 아니라 `전날 저녁 → 취침 → 수면 → 기상 후 회복`으로 이어지는 **behavioral day**에 가깝습니다.
2. 라벨은 절대값보다 “그 사람의 평소 대비 오늘”일 가능성이 높아, subject-independent featur([Dacon][1]) deviation representation\*\*이 중요합니다.
3. 라벨 450일은 너무 작으므로, 원천 로그를 이용해 **unlabeled day representation**을 먼저 만들고 label은 probing에 가깝게 써야 합니다.
4. Q1~Q3는 주관 상태, S1~S4는 수면 생리/행동에 가까워서 같은 feature view를 쓰면 일부 타깃은 손해를 볼 수 있습니다. 대회 설명상 Q1은 수면의 질, Q2는 취침 전 피로도, Q3는 스트레스, S1~S4는 수면시간·효율·지연·각성 관련 지표입니다. ([Dacon][1]) Public LB 일반화를 위해 “subject id 암기”, “test period target mean 추정”, “특정 사람의 루틴 fingerprint 과적합”을 피하고, **루틴 대비 변화량 + 안정적인 episode 구조** 중심으로 가야 합니다.

---

## 2. 데이터 엔지니어링 아이디어 100개

### A. 하루를 다르게 자르는 아이디어

1. **Sleep-to-sleep day**: 전날 주요 수면 종료 시점부터 다음 주요 수면 종료까지를 하루로 정의. Q1, S1~S4에 유리. 위험: 낮음.

2. **Evening-to-evening day**: 18시~다음날 18시로 자르기. 취침 전 피로 Q2, 스트레스 Q3에 유리. 위험: 낮음.

3. **Bedtime-anchored window**: 추정 취침 시각 기준 `-12h ~ +12h`를 하루로 재구성. 수면 직전 행동의 영향 포착. 위험: 중간.

4. **Wake-anchored window**: 추정 기상 시각 기준 `-8h ~ +16h`. 기상 후 회복, 낮 활동량, 낮잠 영향을 함께 표현. 위험: 낮음.

5. **Main sleep episode 중심 day**: 가장 긴 정지/수면 episode를 anchor로 삼고 전후 episode를 붙임. 수면 지표가 calendar boundary를 넘을 때 유리. 위험: 중간.

6. **Phone inactivity day**: 가장 긴 phone silence interval을 밤으로 보고 그 전후를 하루로 구성. sleep log가 noisy할 때 보완. 위험: 중간.

7. **Home-return-to-home-return day**: GPS에서 밤 home 복귀 시점부터 다음 home 복귀까지. 외출/귀가 리듬이 중요한 사람에게 유리. 위험: 높음, home 추정 과적합 가능.

8. **Circadian phase day**: subject별 median bedtime을 0 phase로 두고 하루를 phase coordinate로 변환. 사람별 늦잠/올빼미 차이 제거. 위험: 낮음.

9. **Workday behavioral day**: 첫 장거리 이동 또는 첫 외출을 day start로 정의. 출근/등교 루틴 deviation을 포착. 위험: 중간.

10. **Recovery day split**: 수면 종료 후 4시간을 별도 “recovery block”으로 분리. Q1과 Q2의 carry-over 효과에 유리. 위험: 낮음.

11. **Pre-sleep half-day**: 라벨 날짜의 수면 직전 6~10시간만 별도 view로 구성. Q2, Q3에 특화. 위험: 낮음.

12. **Post-sleep half-day**: 기상 후 6~10시간을 별도 view로 구성. Q1의 체감 품질, 회복감 proxy. 위험: 중간.

13. **Night-only day**: 21시~다음날 09시만 사용한 night representation. S1~S4와 Q1에 특화. 위험: 낮음.

14. **Social jetlag day**: 평일/주말 구분 대신 subject별 “평소보다 늦게 시작한 하루”를 별도 day type으로 인코딩. Q2/Q3에 유리. 위험: 중간.

15. **Transition day**: 전날과 오늘의 루틴이 급격히 바뀐 날을 별도 class로 취급. 여행, 일정 변화, 회복일 포착. 위험: 중간.

---

### B. subject별 평소 루틴 대비 deviation

16. **Personal routine residual**: 각 feature를 subject median day curve에서 뺀 residual sequence로 변환. 핵심 representation. 위험: 낮음.

17. **Routine percentile token**: 오늘의 취침, 기상, 이동량, phone 사용량을 subject 내 percentile로 표현. absolute scale 제거. 위험: 낮음.

18. **Late-than-usual bedtime**: 취침 시각이 본인 평소보다 얼마나 늦었는지. S3, Q2, Q3에 유리. 위험: 낮음.

19. **Early wake deviation**: 평소보다 얼마나 일찍 깼는지. S1, Q1, Q2에 유리. 위험: 낮음.

20. **Sleep regularity break**: 최근 2주 수면 midpoint variance 대비 오늘 midpoint 이탈. 수면 질과 피로에 유리. 위험: 낮음.

21. **Routine entropy spike**: 하루 episode 전이 패턴이 평소보다 불규칙한 정도. 스트레스/피로 proxy. 위험: 중간.

22. **Home-stay deviation**: 평소 대비 집에 머문 시간이 많거나 적은지. 우울/피로/휴식일 proxy 가능. 위험: 중간.

23. **Out-of-home novelty**: 평소 가지 않던 장소 cluster 방문 여부. 스트레스 또는 활력 proxy. 위험: 중간.

24. **Commuting compression**: 평소 이동 루틴보다 이동이 짧거나 사라진 날. 휴일, 재택, 컨디션 저하 포착. 위험: 중간.

25. **Evening stimulation deviation**: 평소 대비 저녁 phone/activity/mobility가 증가했는지. 입면 지연 S3에 유리. 위험: 낮음.

26. **Night fragmentation residual**: subject별 평소 야간 깨짐 패턴 대비 오늘의 interruption 증가. S4, Q1에 유리. 위험: 낮음.

27. **Rest-after-stress pattern**: 전날 고활동/고이동 이후 오늘 저활동이면 회복일 token 부여. Q2에 유리. 위험: 중간.

28. **Personal weekend effect 제거**: 요일 effect를 subject별로 제거한 residual day. Public shift 완화. 위험: 낮음.

29. **Subject routine archetype embedding**: 사람 자체를 id로 넣기보다 “regular sleeper”, “late sleeper”, “high mobility” 같은 archetype으로 변환. 위험: 중간.

30. **Deviation direction only**: 수치 크기보다 `평소보다 많음/적음/비슷함` ternary token으로 표현. 작은 라벨에서 robust. 위험: 낮음.

---

### C. 최근 7/14/28일과의 비교

31. **7-day acute deviation**: 최근 7일 평균 루틴 대비 오늘 이탈. 단기 컨디션 변화 포착. 위험: 낮음.

32. **28-day baseline deviation**: subject의 장기 baseline 대비 오늘 위치. 개인차 제거. 위험: 낮음.

33. **7 vs 28 fatigue accumulation**: 최근 7일 수면/활동이 28일 기준보다 나빠지는 추세인지. Q2에 유리. 위험: 낮음.

34. **Sleep debt ledger**: 최근 7/14일 동안 평소 수면시간보다 부족했던 누적량. S1, Q2, Q1에 유리. 위험: 낮음.

35. **Irregularity debt**: 최근 14일간 bedtime/waketime 흔들림의 누적. Q1/Q2/S3에 유리. 위험: 낮음.

36. **Mobility load accumulation**: 최근 7일 이동 거리·장소 전환이 평소보다 많았는지. 피로/스트레스 proxy. 위험: 중간.

37. **Recovery adequacy ratio**: 어제 high-load day 이후 오늘 수면이 충분히 늘었는지. Q1/Q2에 유리. 위험: 낮음.

38. **Rolling missingness health**: 최근 7일 결측 증가가 기기 미착용인지 생활 변화인지 episode로 해석. 위험: 중간.

39. **Recent phone-at-night streak**: 야간 phone 사용이 며칠 연속 지속됐는지. S3/S4/Q1에 유리. 위험: 낮음.

40. **Late bedtime streak**: 평소보다 늦은 취침이 연속된 길이. Q2, S3에 유리. 위험: 낮음.

41. **Weekend recovery contrast**: 평일 누적 부채가 주말 수면으로 회복됐는지. Q1/S1에 유리. 위험: 중간.

42. **Slope token**: 최근 7일의 수면/활동/missingness가 개선 중인지 악화 중인지 discrete token화. 위험: 낮음.

---

### D. 수면·기상·야간 phone·정지 episode

43. **Sleep onset candidate episode**: 야간 phone 종료 + 장시간 정지 + location home이 만나는 첫 시점을 입면 후보로 생성. S3에 유리. 위험: 중간.

44. **Wake candidate episode**: 아침 phone unlock + movement onset + location transition을 기상 후보로 생성. S1/S2에 유리. 위험: 중간.

45. **Pre-bed arousal score**: 취침 전 2시간의 phone burst, 이동, activity 증가를 arousal로 표현. S3/Q2에 유리. 위험: 낮음.

46. **Night phone intrusion count**: 추정 수면 구간 내 phone event burst 수. S4/Q1에 유리. 위험: 낮음.

47. **Long stillness purity**: 가장 긴 정지 episode 안에서 phone/GPS/activity interruption이 얼마나 적은지. S2에 유리. 위험: 낮음.

48. **Micro-awakening proxy**: 수면 중 짧은 phone/motion/GPS noise가 반복되는 패턴. S4에 유리. 위험: 중간.

49. **Sleep compression**: 침대에 있었던 시간 대비 실제 quiet sleep로 보이는 시간. S2/S3에 유리. 위험: 중간.

50. **Early morning fragmentation**: 기상 직전 2시간의 깨짐/phone 확인 증가. Q1에 유리. 위험: 낮음.

51. **Bedtime procrastination pattern**: home 도착 후 취침 후보까지의 지연이 평소보다 긴지. Q2/S3에 유리. 위험: 중간.

52. **Nocturnal mobility anomaly**: 밤 시간대 GPS 이동 또는 장소 변화. 수면 방해/외박/야간 활동 포착. 위험: 중간.

53. **Nap episode extraction**: 낮 시간 장시간 정지+phone silence를 낮잠 후보로 추출. Q2와 야간 S3에 영향. 위험: 중간.

54. **Sleep rebound marker**: 전날 짧은 수면 후 오늘 긴 수면 또는 늦잠. S1/Q1에 유리. 위험: 낮음.

55. **Alarm-like wake pattern**: 같은 시각 반복 기상 vs 자연 기상 추정. 수면 부족/사회적 압박 proxy. 위험: 중간.

---

### E. GPS·이동·정지·활동 domain view

56. **Place vocabulary**: GPS를 raw 좌표 대신 home/work/third-place/novel-place token으로 변환. 위험: 중간.

57. **Place transition grammar**: `home → work → food → home` 같은 장소 전이 sequence를 하루 문장으로 표현. Q2/Q3에 유리. 위험: 중간.

58. **Mobility radius deviation**: 오늘 생활 반경이 평소보다 좁거나 넓은지. 스트레스/피로/휴식일 proxy. 위험: 낮음.

59. **Dwell fragmentation**: 한 장소에 오래 머무는지, 짧게 자주 이동하는지. 정신적 부하 proxy. 위험: 중간.

60. **Evening return stability**: 귀가 시각과 이후 외출 여부. S3/Q2에 유리. 위험: 낮음.

61. **Last outside activity before bed**: 취침 전 마지막 외부 활동 종료 시점. 피로와 입면에 유리. 위험: 낮음.

62. **Commute stress proxy**: 이동 시간이 평소보다 길고 정체/정지-이동 반복이 많았는지. Q3/Q2에 유리. 위험: 중간.

63. **Indoor sedentary block**: home에서 긴 정지 episode가 낮에 발생했는지. 피로/회복/무기력 proxy. 위험: 중간.

64. **Activity rhythm amplitude**: 하루 활동이 낮에 집중됐는지 밤까지 퍼졌는지. 수면 질에 유리. 위험: 낮음.

65. **Last high-intensity activity lag**: 마지막 높은 activity와 취침 사이 간격. S3/Q1에 유리. 위험: 낮음.

---

### F. missingness를 정보로 쓰기

66. **Missingness episode token**: 결측을 단순 결측치가 아니라 `짧은 결측/긴 결측/야간 결측/이동 중 결측` episode로 표현. 위험: 낮음.

67. **Sensor disagreement missingness**: GPS는 있는데 phone/activity가 없는 경우 등 modal 간 비대칭 결측. 기기 상태와 생활 상태 분리. 위험: 중간.

68. **Night missingness as sleep proxy**: 밤의 phone/activity 결측이 수면 quietness인지 기기 미착용인지 다른 modal로 판별. 위험: 중간.

69. **Missingness onset time**: 하루 중 언제부터 로그가 사라지는지. 취침/외출/배터리/기기 미소지 proxy. 위험: 중간.

70. **Missingness recovery time**: 다시 로그가 나타나는 시각. 기상 또는 폰 사용 재개 proxy. 위험: 중간.

71. **Missingness regularity**: subject별 평소 결측 패턴과 다른 결측은 anomaly로 취급. 위험: 낮음.

72. **Cross-modal imputation confidence**: imputed value 자체보다 “이 구간을 얼마나 믿을 수 있는지” confidence token 추가. 위험: 낮음.

73. **Sensor coverage calendar**: 라벨 날짜별 사용 가능한 modal 조합을 representation에 포함. Public drift 방어. 위험: 낮음.

74. **Device-off night marker**: 취침 전 폰이 꺼진 듯한 패턴과 단순 미사용 패턴 분리. S3/S4에 유리. 위험: 중간.

75. **Missingness motif clustering**: 결측 패턴만으로 하루를 cluster하여 device behavior shift를 추적. 위험: 중간.

---

### G. GPS·phone·activity·sleep cross-modal 관계

76. **Home + phone silence + stillness consensus**: 세 modal이 동시에 수면을 가리키는 consensus score. S1/S2에 유리. 위험: 낮음.

77. **Phone active but physically still**: 몸은 정지인데 phone은 활발한 시간. 취침 전 doomscrolling proxy. S3/Q2에 유리. 위험: 낮음.

78. **Moving but phone silent**: 이동 중 phone 사용이 적은 패턴. 출퇴근/운전/운동 구분에 도움. 위험: 중간.

79. **GPS stationary but activity high**: 실내 운동/집안일/센서 noise 후보. Q2/Q3 해석에 도움. 위험: 중간.

80. **Late outside + late phone + short sleep chain**: 늦은 외출이 야간 phone과 짧은 수면으로 이어지는 causal chain token. Q1/Q2/S1에 유리. 위험: 중간.

81. **Stressful day chain**: 장소 전환 많음 → 저녁 phone 증가 → 늦은 취침 → 야간 깨짐. Q3/Q2/Q1 multi-target view. 위험: 중간.

82. **Recovery day chain**: 이동 적음 → 낮 정지 많음 → 이른 취침 → 긴 quiet sleep. Q2/S1/Q1에 유리. 위험: 낮음.

83. **Mismatch day**: 활동량은 낮은데 피로 proxy가 높은 날, 또는 이동은 많은데 수면이 좋은 날. subject-specific label noise 탐지. 위험: 중간.

84. **Modal lead-lag graph**: phone 종료가 sleep onset보다 앞서는지, activity 감소가 먼저인지 등 modal 간 시간차를 feature화. 위험: 중간.

85. **Day causal sketch**: 하루를 “load → arousal → sleep opportunity → sleep continuity → recovery” 5단계 latent chain으로 요약. 위험: 낮음.

---

### H. 비슷한 하루 retrieval, prototype, motif

86. **Subject-internal nearest days**: 같은 사람의 과거 비슷한 하루 k개를 찾아 label smoothing 또는 representation 보강. 위험: 중간.

87. **Cross-subject normalized retrieval**: subject-normalized residual끼리 비슷한 하루를 찾음. 사람 id 과적합 완화. 위험: 낮음.

88. **Good-sleep prototype**: label 있는 날 중 S1/S2/Q1 positive prototype과의 거리. 위험: 중간.

89. **Bad-night prototype**: 야간 phone intrusion + fragmented stillness + late sleep prototype과의 거리. 위험: 낮음.

90. **High-stress motif**: 장소 전환/야간 phone/짧은 수면이 결합된 motif cluster. Q3에 유리. 위험: 중간.

91. **Recovery motif**: 낮 활동 낮음 + 이른 취침 + 긴 quiet sleep motif. Q2/Q1에 유리. 위험: 낮음.

92. **Routine day prototype**: subject별 가장 평범한 날 prototype과 오늘 거리. 모든 타깃에 baseline feature. 위험: 낮음.

93. **Rare day detector**: test day가 train label day manifold 밖인지 표시. Public shift 방어. 위험: 낮음.

94. **Motif transition over week**: 하루 cluster가 최근 7일 동안 어떻게 변했는지 sequence로 표현. Q2/Q3에 유리. 위험: 중간.

95. **Counterfactual nearest day**: 오늘과 비슷하지만 수면 결과가 다른 날을 찾아 차이 feature 생성. 해석력 좋음. 위험: 높음, 라벨 수 적음.

---

### I. Transformer / Encoder-Decoder token화

96. **Episode token sequence**: 하루를 고정 bin이 아니라 `sleep_candidate`, `home_stay`, `commute`, `phone_burst`, `missing_block` token sequence로 변환. 위험: 낮음.

97. **Time-gap token**: episode 사이 간격을 token으로 넣어 event sequence 모델이 리듬을 학습하게 함. 위험: 낮음.

98. **Deviation token + raw token dual stream**: raw behavior token과 subject-normalized deviation token을 둘 다 입력. 위험: 낮음.

99. **Modality token**: GPS/phone/activity/sleep/missingness의 source embedding을 넣어 Transformer가 modal별 신뢰도를 학습. 위험: 낮음.

100.  **Self-supervised day caption**: 하루를 “late-bed, high-evening-phone, fragmented-night, low-morning-activity” 같은 pseudo-caption으로 변환하고 decoder가 caption을 복원하게 함. 위험: 낮음.

---

## 3. 가장 유망한 Top 10

| 순위 | 아이디어                                        | 유망한 이유                                                                            | 유리한 타깃  | 과적합 위험 |
| ---: | ----------------------------------------------- | -------------------------------------------------------------------------------------- | ------------ | ----------- |
|    1 | **Sleep-to-sleep day**                          | 라벨의 실제 의미가 수면 episode 중심이므로 calendar noise를 크게 줄일 수 있음          | Q1, S1~S4    | 낮음        |
|    2 | **Personal routine residual**                   | 약 10명 구조에서는 absolute feature보다 “평소 대비 변화”가 더 안정적                   | 전 타깃      | 낮음        |
|    3 | **Pre-bed arousal score**                       | 취침 전 phone/activity/mobility 증가는 피로, 스트레스, 입면 지연과 도메인적으로 연결됨 | Q2, Q3, S3   | 낮음        |
|    4 | **Night phone intrusion count**                 | 수면 중 각성, 수면 질 저하를 직접적으로 proxy할 수 있음                                | Q1, S4, S2   | 낮음        |
|    5 | **Sleep debt ledger**                           | 하루 상태는 단일 하루보다 최근 누적 수면 부족의 영향을 받음                            | Q1, Q2, S1   | 낮음        |
|    6 | **Home + phone silence + stillness consensus**  | 한 modal의 오류를 줄이고 sleep episode 추정을 robust하게 만듦                          | S1~S4        | 낮음        |
|    7 | **Episode token sequence**                      | Transformer/Encoder-Decoder에 수치 feature보다 자연스러운 입력 구조                    | 전 타깃      | 낮음        |
|    8 | **Subject-internal routine prototype distance** | 라벨이 적어도 subject별 평범한 하루와의 거리는 안정적으로 만들 수 있음                 | 전 타깃      | 낮음        |
|    9 | **Cross-subject normalized retrieval**          | 사람마다 scale은 다르지만 “늦은 취침+야간 phone+짧은 수면” 같은 패턴은 공유 가능       | Q1~Q3, S3/S4 | 중간        |
|   10 | **Missingness episode token**                   | 결측이 단순 noise가 아니라 수면, 폰 미사용, 기기 이탈, 생활 변화의 신호일 수 있음      | S1~S4, Q2    | 낮음~중간   |

핵심은 1, 2, 6, 7을 먼저 묶는 것입니다. 즉, **calendar day를 sleep episode 중심으로 재정렬하고, subject baseline을 제거한 뒤, cross-modal consensus episode로 token화**하는 방향이 가장 강합니다.

---

## 4. 바로 실험 가능한 5개 실험

### 실험 1. Calendar day vs Sleep-anchored day 비교

**구성**

- 기존 `00:00~24:00` feature set 유지.
- 새로 `main sleep episode 기준 -12h ~ +12h`, `18:00~18:00`, `wake-to-wake` view 생성.
- 같은 모델, 같은 CV에서 day slicing만 바꿔 비교.
- subject-wise CV와 time-wise CV를 둘 다 확인.

**성공 기준**

- Q1, S1, S2, S3, S4에서 sleep-anchored view가 calendar view보다 OOF macro F1 또는 AUC가 일관되게 상승.
- 특히 S3/S4에서 개선되면 sleep episode 재정렬이 맞다는 신호.

**실패 시 해석**

- 수면 episode 추정이 부정확하거나, official label date가 이미 특정 기준으로 정렬되어 있을 수 있음.
- 이 경우 calendar day를 버리지 말고 `calendar + sleep-anchored multi-view`로 ensemble/input concat하는 쪽이 낫습니다.

---

### 실험 2. Subject residual representation

**구성**

- 모든 daily/episode feature를 세 버전으로 생성:
  - raw value
  - subject median 대비 차이
  - subject percentile/rank

- subject id는 직접 넣지 않거나, 넣더라도 강한 regularization.
- `raw only`, `residual only`, `raw + residual` 비교.

**성공 기준**

- Public/local mismatch가 줄고, subject-wise CV에서 residual feature가 raw보다 안정적.
- Q1~Q3에서 특히 개선되면 “라벨이 절대 상태가 아니라 평소 대비 상태”라는 가설이 강화됨.

**실패 시 해석**

- subject별 baseline 추정 기간이 부족하거나, test subject가 train subject와 다를 가능성이 있음.
- residual 계산에 future leakage가 있거나, baseline window를 잘못 잡았을 수 있으므로 `past-only 28일 baseline`으로 다시 실험해야 합니다.

---

### 실험 3. Cross-modal sleep episode extractor

**구성**

밤 구간에서 다음 조건을 조합해 sleep episode 후보를 만듭니다.

- phone silence
- GPS home/stationary
- activity low
- missingness pattern
- long stillness

그 뒤 episode별로 다음 representation을 만듭니다.

- sleep opportunity length
- quiet sleep length
- interruption count
- first interruption time
- last phone before sleep
- first phone after wake
- consensus confidence

**성공 기준**

- S1~S4가 기존 sleep/table feature보다 개선.
- Q1도 함께 개선되면 수면 episode 품질 proxy가 주관 수면 질에도 연결된 것.

**실패 시 해석**

- modal 간 timestamp alignment가 어긋났거나, phone silence가 실제 수면이 아닌 기기 미사용일 수 있음.
- 이 경우 episode 자체보다 `confidence token`을 모델에 넣고, extractor threshold를 hard rule이 아닌 soft score로 바꿔야 합니다.

---

### 실험 4. Recent-history debt features

**구성**

최근 7/14/28일 기준으로 다음을 만듭니다.

- sleep debt
- late bedtime streak
- night phone streak
- irregularity debt
- mobility load accumulation
- recovery adequacy

단, label leakage 방지를 위해 예측 날짜 이후 데이터는 절대 사용하지 않습니다.

**성공 기준**

- Q2, Q3, Q1이 단일-day feature보다 개선.
- S1~S4보다 Q계열에서 더 좋아지면 “주관 상태는 누적 맥락이 중요하다”는 해석 가능.

**실패 시 해석**

- 라벨 날짜 주변의 원천 데이터 coverage가 부족하거나, rolling window가 subject drift를 따라가지 못했을 수 있음.
- 28일보다 7일이 좋으면 장기 baseline보다 acute deviation이 중요하고, 반대면 개인 루틴 안정성이 중요합니다.

---

### 실험 5. Episode-token self-supervised pretraining

**구성**

라벨 없는 원천 데이터를 이용해 하루를 token sequence로 만듭니다.

예시 token:

```text
[HOME_STAY_3H] [COMMUTE_40M] [WORK_STAY_6H] [EVENING_PHONE_BURST]
[LATE_HOME_RETURN] [PREBED_PHONE_90M] [SLEEP_CANDIDATE]
[NIGHT_INTRUSION_2] [WAKE_PHONE_07:40]
```

Self-supervised target:

- masked episode prediction
- next episode prediction
- day order prediction
- same-subject same-routine contrastive learning
- corrupted modality restoration
- tomorrow sleep debt prediction
- pseudo-caption reconstruction

이 encoder representation을 label 450일에만 linear probe 또는 small decoder로 fine-tune합니다.

**성공 기준**

- small supervised model보다 OOF 안정성 증가.
- label fold가 바뀌어도 representation의 target별 ranking이 크게 흔들리지 않음.
- Q1~Q3에서 특히 개선되면 unlabeled routine context가 효과적이라는 의미.

**실패 시 해석**

- token 설계가 너무 coarse해서 타깃과 연결되는 미세한 야간 패턴을 잃었을 수 있음.
- 반대로 token이 너무 detailed하면 subject fingerprint를 외운 것일 수 있음.
- 실패하면 `subject-normalized token`, `time-gap token`, `modality confidence token`을 추가하고 subject contrastive loss는 약하게 해야 합니다.

---

## 추가로 중요한 운영 원칙

가장 위험한 과적합은 “이 사람은 원래 늦게 자니까 label이 이렇다”를 외우는 것입니다. 이 대회에서는 오히려 “이 사람이 **평소보다** 늦게 잤는가”, “평소보다 야간 phone이 늘었는가”, “최근 7일 누적 부채가 커졌는가”가 더 안전한 신호입니다.

추천 실험 순서는 다음입니다.

```text
1) sleep-anchored slicing
2) subject residual / percentile
3) cross-modal sleep episode
4) recent debt features
5) episode-token SSL
```

이 5개를 한꺼번에 넣지 말고, `view 단위 ablation`으로 봐야 합니다. Public LB에 맞추기보다 subject-wise CV, time-wise CV, label mean shift stress test에서 동시에 버티는 representation을 우선 채택하는 게 더 안전합니다.

[1]: https://dacon.io/en/competitions/official/236690/overview/description?utm_source=chatgpt.com "제 5회 ETRI 휴먼이해 인공지능 논문경진대회"
