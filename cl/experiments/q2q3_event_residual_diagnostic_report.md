# Q2/Q3 event-residual diagnostic

## 목적

Phase 3의 `Q2/Q3 event/deviation residual` 가설을 submission 없이 OOF로만 점검했다. S-family는 보호하고, Q1은 tiny residual만 허용했다.

- candidate event/deviation numeric features: 3670

- folds: chrono_tail, interleaved hole, subject mirror

- models: subject anchor, nearest-label canary, raw event residual, capped event residual


## 1. Mean scores by family/model

| family | model | ll_mean | ll_mean_Q2Q3 | ll_Q1 | ll_Q2 | ll_Q3 | ll_S4 |
|---|---|---|---|---|---|---|---|
| chrono_tail | anchor_subject_prior | 0.6380 | 0.6785 | 0.6730 | 0.6761 | 0.6810 | 0.6550 |
| chrono_tail | event_capped_q1q2q3s4 | 0.6369 | 0.6778 | 0.6767 | 0.6675 | 0.6881 | 0.6451 |
| chrono_tail | event_raw_q1q2q3s4 | 0.7913 | 0.9522 | 1.0530 | 0.9477 | 0.9567 | 0.8011 |
| chrono_tail | neighbor_k3_canary | 0.9697 | 1.1168 | 1.1925 | 1.1195 | 1.1141 | 0.8710 |
| hole_v1 | anchor_subject_prior | 0.6259 | 0.6699 | 0.6871 | 0.6744 | 0.6654 | 0.6479 |
| hole_v1 | event_capped_q1q2q3s4 | 0.6177 | 0.6445 | 0.6796 | 0.6391 | 0.6499 | 0.6483 |
| hole_v1 | event_raw_q1q2q3s4 | 0.6982 | 0.7177 | 0.8786 | 0.7114 | 0.7239 | 0.8670 |
| hole_v1 | neighbor_k3_canary | 0.8118 | 0.8007 | 0.9649 | 0.8187 | 0.7827 | 0.9253 |
| mirror_v1 | anchor_subject_prior | 0.6423 | 0.6988 | 0.6861 | 0.7073 | 0.6903 | 0.6436 |
| mirror_v1 | event_capped_q1q2q3s4 | 0.6425 | 0.7040 | 0.6829 | 0.7152 | 0.6928 | 0.6380 |
| mirror_v1 | event_raw_q1q2q3s4 | 0.7680 | 0.9305 | 0.9857 | 0.9395 | 0.9216 | 0.7606 |
| mirror_v1 | neighbor_k3_canary | 0.9245 | 1.0687 | 1.0517 | 1.0836 | 1.0538 | 0.8302 |

## 2. Delta vs subject-anchor (negative is improvement)

| family | model | delta_ll_mean_vs_anchor | delta_ll_mean_Q2Q3_vs_anchor | delta_ll_Q1_vs_anchor | delta_ll_Q2_vs_anchor | delta_ll_Q3_vs_anchor | delta_ll_S4_vs_anchor |
|---|---|---|---|---|---|---|---|
| chrono_tail | anchor_subject_prior | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| chrono_tail | event_capped_q1q2q3s4 | -0.0011 | -0.0007 | 0.0037 | -0.0086 | 0.0071 | -0.0099 |
| chrono_tail | event_raw_q1q2q3s4 | 0.1533 | 0.2737 | 0.3800 | 0.2717 | 0.2757 | 0.1460 |
| chrono_tail | neighbor_k3_canary | 0.3317 | 0.4382 | 0.5195 | 0.4434 | 0.4331 | 0.2160 |
| hole_v1 | anchor_subject_prior | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| hole_v1 | event_capped_q1q2q3s4 | -0.0083 | -0.0254 | -0.0075 | -0.0353 | -0.0155 | 0.0003 |
| hole_v1 | event_raw_q1q2q3s4 | 0.0723 | 0.0478 | 0.1915 | 0.0370 | 0.0585 | 0.2191 |
| hole_v1 | neighbor_k3_canary | 0.1859 | 0.1308 | 0.2778 | 0.1443 | 0.1173 | 0.2774 |
| mirror_v1 | anchor_subject_prior | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| mirror_v1 | event_capped_q1q2q3s4 | 0.0002 | 0.0052 | -0.0032 | 0.0079 | 0.0025 | -0.0057 |
| mirror_v1 | event_raw_q1q2q3s4 | 0.1257 | 0.2318 | 0.2996 | 0.2322 | 0.2313 | 0.1170 |
| mirror_v1 | neighbor_k3_canary | 0.2822 | 0.3699 | 0.3656 | 0.3763 | 0.3635 | 0.1866 |

## 3. Movement audit

| family | target | mean_abs_delta_raw | p95_abs_delta_raw | mean_abs_delta_capped | p95_abs_delta_capped | mean_delta_capped |
|---|---|---|---|---|---|---|
| chrono_tail | Q1 | 0.2707 | 0.4387 | 0.0294 | 0.0300 | -0.0057 |
| chrono_tail | Q2 | 0.2866 | 0.5135 | 0.0957 | 0.1000 | 0.0045 |
| chrono_tail | Q3 | 0.2359 | 0.4408 | 0.0530 | 0.0550 | 0.0160 |
| chrono_tail | S4 | 0.2456 | 0.4822 | 0.0333 | 0.0350 | -0.0019 |
| hole_v1 | Q1 | 0.2548 | 0.4789 | 0.0295 | 0.0300 | 0.0002 |
| hole_v1 | Q2 | 0.2731 | 0.4726 | 0.0934 | 0.1000 | 0.0008 |
| hole_v1 | Q3 | 0.2354 | 0.4548 | 0.0516 | 0.0550 | 0.0126 |
| hole_v1 | S4 | 0.2145 | 0.4382 | 0.0336 | 0.0350 | 0.0050 |
| mirror_v1 | Q1 | 0.2593 | 0.4867 | 0.0292 | 0.0300 | 0.0007 |
| mirror_v1 | Q2 | 0.2584 | 0.4912 | 0.0917 | 0.1000 | 0.0028 |
| mirror_v1 | Q3 | 0.2237 | 0.4217 | 0.0523 | 0.0550 | 0.0140 |
| mirror_v1 | S4 | 0.2097 | 0.4395 | 0.0336 | 0.0350 | -0.0030 |

## 4. Most frequently selected features

| target | feature | selected_count |
|---|---|---|
| Q1 | anchor_logit | 9 |
| Q1 | anchor_p | 9 |
| Q1 | ble_deviceclass_1044_count__subj_delta | 9 |
| Q1 | future_Q3_mean | 9 |
| Q1 | near_Q1_mean | 9 |
| Q1 | near_Q3_mean | 9 |
| Q1 | near_S1_mean | 9 |
| Q1 | topapp_00_06_anyauth_time__subj_delta | 9 |
| Q1 | future_Q1_mean | 8 |
| Q1 | past_Q1_mean | 8 |
| Q1 | future_Q2_mean | 7 |
| Q1 | late_activity_last_hour__dev_weekday_mean__subj_z | 7 |
| Q2 | anchor_logit | 9 |
| Q2 | anchor_p | 9 |
| Q2 | future_Q2_mean | 9 |
| Q2 | near_Q2_mean | 9 |
| Q2 | near_Q3_mean | 9 |
| Q2 | past_Q2_mean | 9 |
| Q2 | past_Q1_mean | 7 |
| Q2 | topapp_all_google_time__subj_delta | 7 |
| Q2 | app_hourly_unique_max__subj_delta | 6 |
| Q2 | topapp_all_youtube_music_time__subj_delta | 6 |
| Q2 | q3x_late21_24_app_media_sum__subj_z | 5 |
| Q2 | steps_sum__weekday_vs_subject_mean__subj_z | 5 |
| Q3 | activity_sum_21_03__prev_abs_delta | 9 |
| Q3 | anchor_logit | 9 |
| Q3 | anchor_p | 9 |
| Q3 | near_Q2_mean | 9 |
| Q3 | near_Q3_mean | 9 |
| Q3 | past_Q1_mean | 9 |
| Q3 | q3x_day_app_media_sum__subj_delta | 9 |
| Q3 | topapp_all_youtube_time__subj_delta | 9 |
| Q3 | future_Q3_mean | 8 |
| Q3 | topapp_all_youtube_music_time__subj_delta | 8 |
| Q3 | near_Q1_mean | 7 |
| Q3 | past_Q3_mean | 7 |
| S4 | anchor_logit | 9 |
| S4 | anchor_p | 9 |
| S4 | ble_deviceclass_1044_count__subj_delta | 9 |
| S4 | near_S2_mean | 9 |
| S4 | near_S4_mean | 9 |
| S4 | topapp_00_06_anyauth_time__subj_delta | 9 |
| S4 | topapp_21_03_카카오뱅크_time__subj_delta | 8 |
| S4 | state_entropy__dev_weekday_mean | 7 |
| S4 | state_entropy__dev_weekday_mean__subj_delta | 7 |
| S4 | topapp_00_06_live스코어_time__subj_delta | 6 |
| S4 | topapp_00_06_teams_time__subj_delta | 6 |
| S4 | topapp_00_06_시프티_time__subj_delta | 6 |

## 5. Interpretation guide

- `neighbor_k3_canary`가 hole/mirror에서 강하고 chrono_tail에서 약하면, test가 hole-filling 성격일 때만 강한 temporal completion signal이다.

- `event_raw`가 좋아도 movement가 크면 public/private brittle 가능성이 크다. 최종 번역은 `event_capped` 쪽만 본다.

- Q1은 negative-control에서 coverage가 깨졌으므로, Q1 개선처럼 보여도 큰 의미를 두지 않는다.

- S-family는 freeze가 기본이다. 여기서는 S4만 tiny diagnostic residual을 허용했지만 anchor 대비 악화하면 즉시 폐기한다.


## 6. Automatic coarse conclusion

- chrono_tail: capped delta Q2=-0.0086, Q3=+0.0071, Q2Q3=-0.0007, mean=-0.0011.

- hole_v1: capped delta Q2=-0.0353, Q3=-0.0155, Q2Q3=-0.0254, mean=-0.0083.

- mirror_v1: capped delta Q2=+0.0079, Q3=+0.0025, Q2Q3=+0.0052, mean=+0.0002.


## Outputs

- `experiments/q2q3_event_residual_diagnostic_results.csv`

- `experiments/q2q3_event_residual_diagnostic_summary.csv`

- `experiments/q2q3_event_residual_diagnostic_shifts.csv`

- `experiments/q2q3_event_residual_diagnostic_selected_features.csv`
