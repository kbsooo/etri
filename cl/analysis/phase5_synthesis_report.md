# Phase 5 synthesis — day diary와 Q2 transition taxonomy

Phase 5는 예측모델 없이 Q2 0→1 전환일을 사람이 읽을 수 있는 diary/taxonomy로 바꾼 분석이다.

## 핵심 발견

1. **Q2 0→1은 단일 현상이 아니라 여러 subtype이다.** 가장 큰 subtype들은 다음과 같다.

| type_name | n_days | Q1_rate | Q3_rate | S_family_mean | low_activity | night_phone | phone_internal | low_mobility_context | physio_light_low |
|---|---|---|---|---|---|---|---|---|---|
| night_phone + low_mobility_context | 23 | 0.652 | 0.652 | 0.576 | 0.229 | 0.648 | 0.416 | 0.485 | 0.405 |
| phone_internal | 21 | 0.571 | 0.810 | 0.690 | -0.358 | 0.072 | 0.377 | -0.470 | -0.306 |
| low_mobility_context | 20 | 0.650 | 0.800 | 0.662 | -0.082 | -0.316 | -0.401 | 0.539 | 0.004 |

2. **Q2 transition diary는 두 계열로 갈라진다.** 하나는 `low_mobility/context + low_activity` 계열, 다른 하나는 `night_phone/phone_internal` 계열이다. 즉 Q2는 ‘많이 움직임’이 아니라 `정지/실내/휴식/폰 내부 체류` 쪽 의미가 더 강하다.

3. **Q3는 Q2와 같지만은 않다.** Q2=1 내에서 Q3=1 minus Q3=0 차이는 night_phone=+0.107, phone_internal=-0.130, low_mobility_context=+0.102, Q1_rate=+0.003. Q3는 Q2의 rest/low-mobility보다 `phone/social/subjective co-state` 쪽을 더 볼 가능성이 있다.

4. **subject profile card가 필요하다.** id03/id06처럼 라벨 anchor가 다른 사람과 id08/id10처럼 night-phone regime인 사람은 같은 Q2=1이라도 의미가 다르다.


## 다음 순수 DS 작업

- Q2 subtype별 대표 날짜를 raw timeline으로 1분/10분 단위 plot: screen, app category, GPS radius, steps, HR.

- id08/id10 night-phone profile과 id06 rest/recovery profile을 분리해서 label semantics를 비교.

- Q3가 붙는 Q2=1과 안 붙는 Q2=1의 day diary를 더 많이 읽기.

- S2 contradiction card: S2만 다르게 켜지는 날짜들의 diary 생성.
