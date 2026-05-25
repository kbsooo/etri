# Phase 7 synthesis — S2 contradiction + id08/id10 비교

이번 Phase 7은 insight-only 마지막 점검이다. 목적은 S2 미스터리와 id08/id10 night-phone regime 차이를 닫는 것.

## 핵심 발견

1. **S2 contradiction은 subject별로 꽤 크다.** contradiction rate 상위 subject:

| subject_id | S2_only_high | S2_only_low | aligned | contradiction_rate |
|---|---|---|---|---|
| id03 | 8 | 4 | 21 | 0.364 |
| id01 | 4 | 7 | 30 | 0.268 |
| id10 | 1 | 7 | 25 | 0.242 |

2. **S2_only_high와 S2_only_low는 반대 생활축이 아니다.** S2_only_high는 Q2_rate=0.686, Q3_rate=0.629; S2_only_low는 Q2_rate=0.595, Q3_rate=0.548. 즉 S2는 단순 severity/latent S-axis로 설명되지 않는다.

   - S2_only_high axes: low_activity=-0.17, night_phone=-0.06, low_mobility_context=+0.01

   - S2_only_low axes: low_activity=+0.04, night_phone=-0.17, low_mobility_context=-0.03


3. **id08/id10은 둘 다 night-phone heavy지만 label grammar가 다르다.** id08: Q2=0.786, Q3=0.446, night_screen=55.6; id10: Q2=0.545, Q3=0.636, night_screen=103.2. id10은 밤폰이 더 극단적이고 Q3가 더 잘 붙는다. id08은 Q2-high지만 Q3가 덜 붙는다.


## 결론

- S2는 freeze/no-latent 대상이라는 판단이 더 강해졌다. S2 contradiction row가 Q/S/inward day 축과 일관되게 정렬되지 않는다.

- id08과 id10은 같은 night-phone family 안에서도 다른 라벨 언어를 가진다. 따라서 subject/regime card 없이 전역 규칙으로 Q2/Q3를 해석하면 위험하다.

- 이제 insight-only 단계는 충분히 닫아도 된다. 더 하면 raw diary 수집은 늘겠지만 큰 구조 결론은 크게 안 바뀔 가능성이 높다.


## Outputs
- `analysis/phase7_A_s2_contradiction_diary.md`
- `analysis/phase7_B_id08_id10_comparison.md`
- `analysis/phase7_*.csv`
- `analysis/figures/p7_*.png`
