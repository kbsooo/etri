# Pruned State Decoder

This experiment treats v83 only as a diagnostic reference. Predictions are built from pruned encoder input families plus state decoders.

## Best Presets

| preset | feature_count | best_candidate | best_avg_log_loss |
| --- | --- | --- | --- |
| only_missingness | 520 | prototype | 0.667821 |
| no_missingness | 520 | prototype | 0.667842 |
| only_rhythm | 520 | prototype | 0.667901 |
| no_sleep | 520 | prototype | 0.667949 |
| only_deviation | 520 | prototype | 0.668203 |
| no_derivative | 520 | prototype | 0.668227 |
| no_phone | 520 | prototype | 0.668413 |
| no_temporal_delta | 520 | prototype | 0.668537 |
| no_rank | 520 | prototype | 0.668556 |
| no_raw | 520 | prototype | 0.668638 |
| no_gps | 520 | prototype | 0.668722 |
| full | 520 | prototype | 0.668763 |
| no_late_pool | 520 | prototype | 0.668835 |
| no_ratio | 520 | prototype | 0.668980 |
| only_cross_modal | 520 | prototype | 0.669598 |

## Best Candidates

| preset | candidate | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_missingness | prototype | 0.667821 | 0.697971 | 0.697694 | 0.675068 | 0.626661 | 0.648680 | 0.641128 | 0.687546 |
| no_missingness | prototype | 0.667842 | 0.696885 | 0.698201 | 0.674781 | 0.627566 | 0.648307 | 0.642963 | 0.686193 |
| only_rhythm | prototype | 0.667901 | 0.695684 | 0.698856 | 0.675139 | 0.628009 | 0.648228 | 0.642207 | 0.687186 |
| no_sleep | prototype | 0.667949 | 0.696604 | 0.697985 | 0.676784 | 0.628951 | 0.647652 | 0.641009 | 0.686659 |
| only_deviation | prototype | 0.668203 | 0.695401 | 0.701463 | 0.675968 | 0.627861 | 0.649219 | 0.640751 | 0.686755 |
| no_derivative | prototype | 0.668227 | 0.697628 | 0.700632 | 0.673723 | 0.628485 | 0.649673 | 0.641359 | 0.686091 |
| no_phone | prototype | 0.668413 | 0.695911 | 0.699574 | 0.674923 | 0.628733 | 0.649134 | 0.642629 | 0.687989 |
| no_temporal_delta | prototype | 0.668537 | 0.696406 | 0.702744 | 0.675440 | 0.629197 | 0.648285 | 0.640538 | 0.687146 |
| no_rank | prototype | 0.668556 | 0.696474 | 0.702405 | 0.677029 | 0.628534 | 0.647552 | 0.641538 | 0.686360 |
| no_raw | prototype | 0.668638 | 0.696098 | 0.700303 | 0.675383 | 0.629150 | 0.649271 | 0.642120 | 0.688137 |
| no_gps | prototype | 0.668722 | 0.695842 | 0.702968 | 0.675625 | 0.629076 | 0.648741 | 0.640863 | 0.687941 |
| full | prototype | 0.668763 | 0.696627 | 0.701001 | 0.675044 | 0.629927 | 0.649214 | 0.642663 | 0.686864 |
| no_late_pool | prototype | 0.668835 | 0.696043 | 0.702049 | 0.675145 | 0.629307 | 0.648618 | 0.643222 | 0.687458 |
| no_ratio | prototype | 0.668980 | 0.697836 | 0.701975 | 0.675551 | 0.628315 | 0.649905 | 0.640406 | 0.688875 |
| no_derivative | hgb | 0.669081 | 0.704957 | 0.737251 | 0.711295 | 0.607652 | 0.628848 | 0.609298 | 0.684263 |
| only_cross_modal | prototype | 0.669598 | 0.697034 | 0.703184 | 0.675059 | 0.632374 | 0.649349 | 0.642423 | 0.687764 |
| only_rhythm | hgb | 0.671701 | 0.707338 | 0.702863 | 0.728774 | 0.605007 | 0.657120 | 0.607099 | 0.693707 |
| only_cross_modal | hgb | 0.675870 | 0.716205 | 0.757967 | 0.731769 | 0.621417 | 0.645981 | 0.594383 | 0.663370 |
| no_raw | hgb | 0.677125 | 0.694643 | 0.734191 | 0.725317 | 0.622682 | 0.686283 | 0.614306 | 0.662452 |
| no_temporal_delta | hgb | 0.677272 | 0.700905 | 0.743982 | 0.726234 | 0.636386 | 0.653260 | 0.612780 | 0.667354 |
| full | hgb | 0.678372 | 0.708703 | 0.749798 | 0.706179 | 0.624872 | 0.669024 | 0.621833 | 0.668196 |
| no_gps | hgb | 0.678832 | 0.708651 | 0.726854 | 0.711163 | 0.625398 | 0.666857 | 0.624618 | 0.688284 |
| no_sleep | hgb | 0.679285 | 0.730007 | 0.740506 | 0.685876 | 0.633028 | 0.680976 | 0.619732 | 0.664868 |
| no_rank | hgb | 0.680305 | 0.731863 | 0.723643 | 0.697446 | 0.641858 | 0.681925 | 0.635177 | 0.650223 |
| only_deviation | hgb | 0.680331 | 0.748775 | 0.744676 | 0.694111 | 0.633800 | 0.636064 | 0.619109 | 0.685780 |
| no_missingness | hgb | 0.681675 | 0.714190 | 0.754407 | 0.695977 | 0.644449 | 0.662313 | 0.627503 | 0.672888 |
| no_ratio | hgb | 0.682058 | 0.742457 | 0.713768 | 0.731940 | 0.641013 | 0.644271 | 0.603391 | 0.697569 |
| no_phone | hgb | 0.684217 | 0.723951 | 0.743463 | 0.714496 | 0.643041 | 0.655981 | 0.636117 | 0.672468 |
| no_late_pool | hgb | 0.685834 | 0.714063 | 0.770276 | 0.686175 | 0.646152 | 0.669952 | 0.623703 | 0.690515 |
| only_missingness | hgb | 0.689130 | 0.706943 | 0.747712 | 0.725552 | 0.643031 | 0.647891 | 0.647139 | 0.705644 |

## Target-wise Selection

| target | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- |
| Q1 | no_raw__hgb | 0.694643 | 0.649217 |
| Q2 | only_missingness__prototype | 0.697694 | 0.649217 |
| Q3 | no_derivative__prototype | 0.673723 | 0.649217 |
| S1 | only_rhythm__hgb | 0.605007 | 0.649217 |
| S2 | no_derivative__hgb | 0.628848 | 0.649217 |
| S3 | only_cross_modal__hgb | 0.594383 | 0.649217 |
| S4 | no_rank__hgb | 0.650223 | 0.649217 |

## Summary

- Best global: `only_missingness__prototype` avg `0.667821`
- Target-wise avg: `0.649217`
- Best global drift vs reference: `0.138587`
- Target-wise drift vs reference: `0.119236`
