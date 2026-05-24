# Phase 4 synthesis — 데이터에서 읽은 생활/라벨 인사이트

이번 Phase 4는 모델을 만들지 않고, 데이터 자체에서 **사람별 생활 문맥과 라벨 사용 방식**을 읽는 데 집중했다.

## 핵심 인사이트

1. **Q1 personal anchor는 더 강해졌다.** subject별 Q1 rate가 0.146~0.848까지 벌어진다. 같은 라벨이라도 사람마다 기준점이 다르다.

2. **Q2 0→1은 한 가지 센서가 아니라 multi-family event처럼 보인다.** Q2 0→1에서 큰 축: mobility_context(-0.17z), physiology_light(-0.16z), activity(-0.09z).

3. **Day archetype은 라벨 해석의 배경이다.** 같은 Q2=1이라도 phone-heavy day, mobility/context-heavy day, rest/quiet day는 의미가 다를 수 있다.

4. **앱 사용은 행동 의미를 읽는 단서다.** Q2 contrast가 큰 app category 중 최상위는 `utility_home`이며, Q2=1과 Q2=0의 평균 차이는 +37.87 minutes-ish다.

5. **coverage는 품질 문제가 아니라 관측 과정이다.** `wifi_unique_bssid`의 low-vs-high contrast가 Q2에서 +0.205로 가장 크다.


## 이제 해야 할 연구

- subject별 fieldnote를 수작업으로 읽고 id03/id06/id08/id09/id10의 narrative를 고정한다.

- Q2 0→1 example days를 timeline으로 시각화해서, phone/media event인지 rest/recovery event인지 분리한다.

- 앱 category와 GPS/WiFi/BLE archetype을 합쳐 `day diary` 형태의 row-level 설명을 만든다.

- 모델링은 아직 보류. 지금은 데이터 generating process를 더 잘 명명하는 단계다.
