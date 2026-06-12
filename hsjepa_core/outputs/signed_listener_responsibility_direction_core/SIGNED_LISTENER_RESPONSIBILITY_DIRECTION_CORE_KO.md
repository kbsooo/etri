# Signed Listener Responsibility Direction Core

## 한 줄 요약

row-target responsibility를 찾은 뒤, 그 cell에서 raw 방향으로 움직일지 inverse 방향으로 움직일지를
HS-JEPA core representation으로 다시 예측했다.

```text
visible human-state context
  + target listener
  + raw/inverse direction listener
  -> hidden signed action-health field
  -> responsibility-high cell에서 안전한 방향만 release
```

## 왜 필요한 실험인가

직전 responsibility field core는 `어디를 봐야 하는가`를 listener-only보다 잘 복원했다.
하지만 기존 action decoder로 번역하면 OOF gain이 음수였다. 따라서 이번 hidden target은
cell 위치가 아니라 signed action direction이다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`
- masked-tail teacher score as feature: `False`
- label-informed peer margin as feature: `False`

## Verdict

- verdict: `signed_direction_core_positive_action_translation_repaired`
- responsibility source: `masked_pretext_listener_responsibility`
- best direction family: `action_geometry_direction`
- best direction AP lift: `0.114069`
- best responsibility-gated OOF gain: `1.640820`
- action-geometry responsibility-gated OOF gain: `1.640820`
- previous responsibility decoder OOF gain: `-0.565668`
- released test cells: `67`
- candidate: `submission_hsjepa_signed_listener_responsibility_direction_3a0fba1d_uploadsafe.csv`

## Direction Family Leaderboard

| feature_family | feature_count | positive_rate | auc | ap | ap_lift_vs_rate | pairwise_all_gain_sum | responsibility_gain_sum | responsibility_positive_rate | oracle_responsibility_gain_sum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| action_geometry_direction | 24 | 0.500000 | 0.630216 | 0.614069 | 0.114069 | -77.355303 | 1.640820 | 0.666667 | -2.396898 |
| responsibility_weighted_pretext_direction | 87 | 0.500000 | 0.510289 | 0.510547 | 0.010547 | -62.139807 | 0.283546 | 0.550000 | -1.948449 |
| masked_pretext_signed_direction | 85 | 0.500000 | 0.510592 | 0.510862 | 0.010862 | -67.772340 | -0.575508 | 0.533333 | -2.804029 |
| human_signed_direction | 245 | 0.500000 | 0.488926 | 0.490001 | -0.009999 | -81.179390 | -3.740024 | 0.516667 | -1.882959 |
| human_plus_pretext_signed_direction | 315 | 0.500000 | 0.491514 | 0.496753 | -0.003247 | -81.428648 | -4.098927 | 0.441667 | -1.964638 |
| direction_listener_only | 17 | 0.500000 | 0.484104 | 0.492421 | -0.007579 | -64.027902 | -5.674280 | 0.433333 | -2.627110 |

## Target-Level Direction Metrics

| feature_family | target | positive_rate | auc | ap | pairwise_gain_sum | pairwise_positive_rate |
| --- | --- | --- | --- | --- | --- | --- |
| action_geometry_direction | Q1 | 0.500000 | 0.507684 | 0.502357 | -5.431224 | 0.526667 |
| action_geometry_direction | Q2 | 0.500000 | 0.596738 | 0.568698 | -8.304044 | 0.568889 |
| action_geometry_direction | S4 | 0.500000 | 0.582459 | 0.572190 | -8.379216 | 0.540000 |
| action_geometry_direction | Q3 | 0.500000 | 0.600928 | 0.564783 | -9.974137 | 0.608889 |
| action_geometry_direction | S1 | 0.500000 | 0.711593 | 0.673631 | -12.059362 | 0.688889 |
| action_geometry_direction | S2 | 0.500000 | 0.648407 | 0.632938 | -15.256172 | 0.644444 |
| action_geometry_direction | S3 | 0.500000 | 0.680274 | 0.667574 | -17.951147 | 0.648889 |
| direction_listener_only | S4 | 0.500000 | 0.497368 | 0.496648 | 0.407368 | 0.520000 |
| direction_listener_only | S3 | 0.500000 | 0.537990 | 0.523008 | -7.390146 | 0.582222 |
| direction_listener_only | Q2 | 0.500000 | 0.436281 | 0.458927 | -8.279157 | 0.464444 |
| direction_listener_only | S2 | 0.500000 | 0.472598 | 0.477041 | -9.394757 | 0.455556 |
| direction_listener_only | S1 | 0.500000 | 0.423728 | 0.453422 | -11.593914 | 0.462222 |
| direction_listener_only | Q1 | 0.500000 | 0.435319 | 0.459292 | -12.778477 | 0.442222 |
| direction_listener_only | Q3 | 0.500000 | 0.433077 | 0.460052 | -14.998819 | 0.435556 |
| human_plus_pretext_signed_direction | Q1 | 0.500000 | 0.475881 | 0.491046 | -2.280043 | 0.480000 |
| human_plus_pretext_signed_direction | Q2 | 0.500000 | 0.508904 | 0.494482 | -5.073522 | 0.508889 |
| human_plus_pretext_signed_direction | S4 | 0.500000 | 0.462341 | 0.478543 | -6.361997 | 0.466667 |
| human_plus_pretext_signed_direction | Q3 | 0.500000 | 0.561778 | 0.554954 | -7.581812 | 0.568889 |
| human_plus_pretext_signed_direction | S1 | 0.500000 | 0.537580 | 0.549954 | -15.223846 | 0.517778 |
| human_plus_pretext_signed_direction | S2 | 0.500000 | 0.488025 | 0.497293 | -20.948651 | 0.466667 |
| human_plus_pretext_signed_direction | S3 | 0.500000 | 0.411536 | 0.445412 | -23.958777 | 0.406667 |
| human_signed_direction | S4 | 0.500000 | 0.468153 | 0.476887 | -3.407965 | 0.495556 |
| human_signed_direction | Q3 | 0.500000 | 0.541842 | 0.539520 | -6.396443 | 0.537778 |
| human_signed_direction | Q1 | 0.500000 | 0.479936 | 0.490500 | -8.063386 | 0.462222 |
| human_signed_direction | Q2 | 0.500000 | 0.472958 | 0.476311 | -10.522064 | 0.493333 |
| human_signed_direction | S1 | 0.500000 | 0.560696 | 0.557138 | -13.042821 | 0.551111 |
| human_signed_direction | S2 | 0.500000 | 0.478884 | 0.485187 | -17.523676 | 0.477778 |
| human_signed_direction | S3 | 0.500000 | 0.425541 | 0.447779 | -22.223035 | 0.451111 |
| masked_pretext_signed_direction | S4 | 0.500000 | 0.519560 | 0.521339 | -0.603016 | 0.520000 |
| masked_pretext_signed_direction | Q1 | 0.500000 | 0.515521 | 0.513499 | -1.706240 | 0.506667 |
| masked_pretext_signed_direction | Q3 | 0.500000 | 0.561869 | 0.556368 | -5.963691 | 0.548889 |
| masked_pretext_signed_direction | S2 | 0.500000 | 0.503143 | 0.503858 | -12.136496 | 0.493333 |
| masked_pretext_signed_direction | S3 | 0.500000 | 0.482081 | 0.494819 | -14.185701 | 0.462222 |
| masked_pretext_signed_direction | S1 | 0.500000 | 0.514180 | 0.518728 | -15.791471 | 0.491111 |
| masked_pretext_signed_direction | Q2 | 0.500000 | 0.474642 | 0.488393 | -17.385724 | 0.462222 |
| responsibility_weighted_pretext_direction | S4 | 0.500000 | 0.521346 | 0.518233 | -0.124307 | 0.540000 |
| responsibility_weighted_pretext_direction | Q1 | 0.500000 | 0.507237 | 0.505502 | -5.351668 | 0.486667 |
| responsibility_weighted_pretext_direction | Q3 | 0.500000 | 0.558178 | 0.550447 | -6.344521 | 0.544444 |
| responsibility_weighted_pretext_direction | S2 | 0.500000 | 0.525936 | 0.520800 | -8.449916 | 0.526667 |
| responsibility_weighted_pretext_direction | Q2 | 0.500000 | 0.464249 | 0.479794 | -13.467013 | 0.488889 |
| responsibility_weighted_pretext_direction | S1 | 0.500000 | 0.519993 | 0.519177 | -13.652744 | 0.520000 |
| responsibility_weighted_pretext_direction | S3 | 0.500000 | 0.472894 | 0.493110 | -14.749638 | 0.453333 |

## Fold Stability

| feature_family | fold | heldout_subjects | positive_rate | auc | ap |
| --- | --- | --- | --- | --- | --- |
| direction_listener_only | 0 | id03,id04 | 0.500000 | 0.471655 | 0.484870 |
| direction_listener_only | 1 | id08,id10 | 0.500000 | 0.464343 | 0.479714 |
| direction_listener_only | 2 | id01,id07 | 0.500000 | 0.503175 | 0.500730 |
| direction_listener_only | 3 | id05,id06 | 0.500000 | 0.501553 | 0.508135 |
| direction_listener_only | 4 | id02,id09 | 0.500000 | 0.486586 | 0.498870 |
| action_geometry_direction | 0 | id03,id04 | 0.500000 | 0.662269 | 0.637664 |
| action_geometry_direction | 1 | id08,id10 | 0.500000 | 0.559966 | 0.544949 |
| action_geometry_direction | 2 | id01,id07 | 0.500000 | 0.652823 | 0.649358 |
| action_geometry_direction | 3 | id05,id06 | 0.500000 | 0.599568 | 0.597828 |
| action_geometry_direction | 4 | id02,id09 | 0.500000 | 0.686336 | 0.656015 |
| human_signed_direction | 0 | id03,id04 | 0.500000 | 0.491116 | 0.494728 |
| human_signed_direction | 1 | id08,id10 | 0.500000 | 0.483281 | 0.484317 |
| human_signed_direction | 2 | id01,id07 | 0.500000 | 0.510517 | 0.507067 |
| human_signed_direction | 3 | id05,id06 | 0.500000 | 0.502629 | 0.509638 |
| human_signed_direction | 4 | id02,id09 | 0.500000 | 0.461510 | 0.471919 |
| masked_pretext_signed_direction | 0 | id03,id04 | 0.500000 | 0.510729 | 0.500488 |
| masked_pretext_signed_direction | 1 | id08,id10 | 0.500000 | 0.523486 | 0.519336 |
| masked_pretext_signed_direction | 2 | id01,id07 | 0.500000 | 0.495382 | 0.511118 |
| masked_pretext_signed_direction | 3 | id05,id06 | 0.500000 | 0.493346 | 0.502504 |
| masked_pretext_signed_direction | 4 | id02,id09 | 0.500000 | 0.526310 | 0.537415 |
| responsibility_weighted_pretext_direction | 0 | id03,id04 | 0.500000 | 0.507775 | 0.503449 |
| responsibility_weighted_pretext_direction | 1 | id08,id10 | 0.500000 | 0.529512 | 0.523388 |
| responsibility_weighted_pretext_direction | 2 | id01,id07 | 0.500000 | 0.476295 | 0.490129 |
| responsibility_weighted_pretext_direction | 3 | id05,id06 | 0.500000 | 0.490684 | 0.501385 |
| responsibility_weighted_pretext_direction | 4 | id02,id09 | 0.500000 | 0.540968 | 0.549280 |
| human_plus_pretext_signed_direction | 0 | id03,id04 | 0.500000 | 0.496298 | 0.490744 |
| human_plus_pretext_signed_direction | 1 | id08,id10 | 0.500000 | 0.514692 | 0.521046 |
| human_plus_pretext_signed_direction | 2 | id01,id07 | 0.500000 | 0.453833 | 0.478364 |
| human_plus_pretext_signed_direction | 3 | id05,id06 | 0.500000 | 0.497168 | 0.501852 |
| human_plus_pretext_signed_direction | 4 | id02,id09 | 0.500000 | 0.492550 | 0.494917 |

## Release Counts

| target | count |
| --- | --- |
| Q2 | 6 |
| S1 | 6 |
| S2 | 9 |
| S4 | 46 |

## 해석

좋은 결과:

```text
responsibility-high cell 안에서 signed direction gain이 양수로 바뀌면,
HS-JEPA core가 "어디를 볼지"뿐 아니라 "어느 방향이 안전한지"도 복원한다는 뜻이다.
```

나쁜 결과:

```text
direction AP가 좋아도 responsibility-gated OOF gain이 음수면,
방향 classifier는 action-health ranking을 읽지만 Log Loss utility로 번역되지 않은 것이다.
```
