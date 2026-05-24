# Phase 3 synthesis — Subject language + deviation/event grammar

## 0. 이번 라운드의 목적

Phase 1+2에서 나온 가설, 즉 **“이 대회는 공통 feature 예측 문제가 아니라 subject-specific measurement language + lifestyle regime + day-level deviation/event 문제”**라는 관점을 검증했다.

이번에는 submission을 만들지 않고, `analysis/phase3_explore.py`로 아래 5트랙을 만들었다.

- A. subject-specific label language map
- B. day deviation model
- C. long-rest / vacation event study
- D. GPS archaeology v2
- E. cluster-aware validation sketch

---

## 1. Q1은 subject-specific personal anchor로 보는 게 맞는가?

**대체로 맞다.**

subject별 Q1 prevalence 범위가 꽤 크다.

- id06: Q1 prevalence 0.146
- id03: Q1 prevalence 0.848
- 나머지는 대략 0.4~0.6대

이건 Q1이 전역적으로 같은 기준의 “오늘 상태”라기보다, **사람마다 응답 기준점이 다른 주관 라벨**임을 지지한다.

해석:

- Q1에 subject 정보가 없다는 기존 가정은 틀렸다.
- 다만 이것이 “Q1을 subject prior로 세게 블렌딩하자”는 뜻은 아니다.
- 더 정확한 모델은 `Q1 = personal anchor + 아주 작은 day residual`이다.
- Q1 coverage/deviation 신호는 Phase 1 negative-control에서 깨졌으므로 함부로 쓰면 안 된다.

모델 번역:

- Q1 movement cap: `0.00~0.03`
- coverage gating 금지
- subject별 baseline calibration은 허용, day-level aggressive move는 금지

---

## 2. Q2 day-signal은 어떤 event/deviation과 연결되는가?

이번 Phase 3에서는 Q2가 여전히 가장 움직일 만한 target으로 남았다.

Day-deviation family 기준으로는 Q2에서 다음 family들이 high-vs-low 차이를 보였다.

- gps/context: high70 - low30 ≈ +0.037
- routine/regularity: ≈ +0.037
- phone/app/screen: ≈ +0.022

효과가 크지는 않지만, Phase 1에서 Q2가 own-neighbor / other-neighbor / coverage / within-subject permutation을 통과했다는 점을 합치면, Q2는 여전히 **day-level event/deviation residual**을 넣을 가장 유력한 target이다.

Long-rest event에서는 12h+ proxy day의 Q2 rate가 normal보다 높았다.

- long_rest Q2 mean: 0.622
- normal Q2 mean: 0.569

Q2 transition에서도 0→1 transition이 long-rest proxy와 가장 강하게 같이 나타났다.

- Q2 0→1: long_rest_event rate 0.224
- stable_1: 0.170
- stable_0: 0.153
- 1→0: 0.120

해석:

- Q2는 단순 subject anchor보다 **routine/context deviation + long-rest/recovery/fatigue event**와 연결될 가능성이 있다.
- 단, long-rest가 모든 subject에서 같은 의미는 아니다. subject별 반복성과 cluster별 해석이 필요하다.

모델 번역:

- Q2 movement cap: `0.08~0.12` 후보
- feature family: temporal neighbor + routine deviation + GPS/context deviation + long-rest proxy

---

## 3. Q3는 Q1형인가 Q2형인가?

이번 subject별 Q3 relation만 보면, **대체로 Q2-like 쪽 힌트가 더 강하다.**

대부분 subject에서 `corr(Q3,Q2)`가 `corr(Q3,Q1)`보다 컸다.

예시:

- id06: corr(Q3,Q2)=0.639, corr(Q3,Q1)=0.295
- id10: corr(Q3,Q2)=0.702, corr(Q3,Q1)=0.103
- id03: corr(Q3,Q2)=0.593, corr(Q3,Q1)=-0.069
- id02: corr(Q3,Q2)=0.663, corr(Q3,Q1)=0.380

예외적으로 id07은 Q1-like/anchor-like로 분류됐다.

해석:

- Q3는 Q1 personal anchor보다는 Q2 temporal/event axis에 더 가까운 힌트가 많다.
- 하지만 Q3 자체가 Phase 1에서 Q2만큼 day-signal 검증을 통과한 것은 아니므로, Q2만큼 공격적으로 움직이면 안 된다.

모델 번역:

- Q3 movement cap: `0.03~0.06`
- Q2 event 동조가 확인된 row에서만 제한적으로 이동

---

## 4. S-family는 lifestyle/static regime으로 보는 게 맞는가?

현재까지는 **그렇게 보는 게 가장 안전하다.**

Phase 1에서 S-family는 subject-prior anchor 대비 다른 source가 전부 악화했고, Phase 3에서도 S-family는 subject별 prevalence 차이가 크다.

특히 S2는 여전히 별도 autopsy 대상이다.

- id03 S2 contradiction rate: 0.364
- id10: 0.242
- id01: 0.268

S2가 S1/S3/S4 majority와 충돌하는 subject가 꽤 있다. 이건 S2를 single S-latent factor로 같이 움직이면 위험하다는 뜻이다.

해석:

- S-family는 day-level feature보다 subject/lifestyle/static regime 성격이 강하다.
- S2는 S-family 내부에서도 semantics가 다르거나 응답 기준이 다른 target일 수 있다.

모델 번역:

- S1/S2/S3: freeze 기본
- S2: latent-based move 금지
- S4: corrected context/GPS가 subject-debiased 검증을 통과할 때만 small move

---

## 5. id08 outlier, id09 GPS-noise, id10 nomad는 어떻게 다르게 처리해야 하는가?

### id08

- lifestyle cluster에서 outlier/특수 regime 후보.
- Q2 prevalence가 0.786으로 높고, Q1/Q3와 패턴이 다르다.
- 단일 global model에서 id08이 residual/validation을 흔들 수 있다.

처리:

- id08 포함/제외 sensitivity 필요
- cluster-aware cap 적용
- 별도 대형 모델은 금지, residual cap 정도만

### id09

GPS dominant-cell share가 precision에 따라 크게 변한다.

- precision 3: dominant share 0.570
- precision 4: 0.260
- precision 5: 0.029

이건 좌표가 잘게 쪼개지는 noise-splitting 가능성을 강하게 시사한다.

처리:

- rounding precision 3 또는 radius clustering으로 home 복원
- corrected home-stay / location entropy 재계산

### id10

id10도 precision을 낮추면 dominant share가 올라가긴 하지만, Phase 2 해석상 실제 nomad regime 후보로 남는다.

- precision 3: 0.531
- precision 4: 0.403
- precision 5: 0.061

처리:

- home-based feature를 전역적으로 강하게 쓰지 않기
- mobility radius, dominant-place stability, unique-place count, sleep-location consistency 등 nomad-aware feature 사용

---

## 6. long-rest day는 system anomaly인가 behavior event인가?

이번 proxy 기준으로는 **system anomaly로 버리기보다 behavior event로 보는 게 더 안전하다.**

12h+ long-rest proxy는 subject별로 반복된다.

- id10: 11일
- id03: 11일
- id05: 9일
- id09: 9일
- id02: 8일
- id06: 6일

그리고 Q2와 약하게 연결된다.

- long_rest Q2 mean 0.622 vs normal 0.569
- Q2 0→1 transition에서 long_rest_event rate가 가장 높음

단, id06만 독점적인 현상은 아니었다. Phase 2에서 id06이 사례적으로 강했지만, proxy를 넓게 잡으면 여러 subject에 반복된다.

해석:

- long-rest는 sensor failure라기보다 휴식/회복/휴가/생활 리듬 변화 event 후보.
- 다만 subject별 의미가 다를 수 있으므로 global binary feature로 세게 쓰면 위험하다.

---

## 7. 모델로 번역한다면

현재 가장 그럴듯한 구조는 다음이다.

```text
base anchor
+ Q1 personal-anchor calibration, tiny residual only
+ Q2 event/deviation residual
+ Q3 Q2-coupled residual if supported
+ S-family mostly frozen
+ id09 corrected GPS features
+ id10 nomad-aware mobility features
+ id08/outlier cluster cap
```

초기 movement cap:

| Target | Cap | 이유 |
|---|---:|---|
| Q1 | 0.00~0.03 | personal anchor, coverage false signal |
| Q2 | 0.08~0.12 | day-signal이 가장 많이 검증됨 |
| Q3 | 0.03~0.06 | Q2-like 힌트는 있으나 Q2만큼 강하지 않음 |
| S1/S2/S3 | freeze | subject/static regime 강함 |
| S4 | 0.00~0.05 | corrected GPS/context 검증 통과 시만 |

---

## 8. 다음 작업 후보

1. **Q2/Q3 event-residual prototype**
   - Q2 transition + long-rest + routine/context deviation만 사용한 tiny residual head.
   - submission 전 diagnostic OOF만.

2. **id09 corrected GPS feature builder**
   - precision 3/radius clustering 기준 home-stay, entropy, mobility 재계산.
   - id10은 nomad-aware branch로 분리.

3. **S2 autopsy**
   - S2 contradiction row를 subject별로 모아 label semantics/방향성 확인.
   - S2는 움직이는 게 아니라 “움직이면 안 되는 조건”을 찾는 쪽.

4. **cluster-aware movement cap validation**
   - id08/outlier cluster에서 residual을 줄였을 때 masked validation 안정성이 좋아지는지 확인.

---

## 산출물

- `analysis/phase3_index.md`
- `analysis/phase3_A_subject_label_language.md`
- `analysis/phase3_B_day_deviation.md`
- `analysis/phase3_C_long_rest_event.md`
- `analysis/phase3_D_gps_archaeology_v2.md`
- `analysis/phase3_E_cluster_validation.md`
- `analysis/phase3_synthesis_report.md`
- `analysis/phase3_explore.py`
- `analysis/figures/p3_*.png`
- `analysis/phase3_*.csv`
