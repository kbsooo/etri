# Masked Row-Support Objective Probe

이 프로브는 hidden row-support를 HS-JEPA식 masked prediction target으로 삼을 수 있는지 검증한다.
raw feature 복원이 아니라, feature family를 가린 context에서 보이지 않는 row-support representation을 예측한다.

## Verdict

- Status: `masked_row_support_objective_supported_with_stress_boundary`
- Full composite row AUC: `0.8193`
- Full composite cell recall: `0.3289`
- Human-only cell recall: `0.2713`
- Prediction-only cell recall: `0.2348`
- Route-masked cell recall: `0.3056`
- Robust mask count: `8`
- Group stress full row AUC: `0.5584`
- Group stress full recall@K: `0.1830`

해석:

The row-support target is not a single-feature shortcut: human-only, prediction-only, and route-masked views all retain signal. However, row/order/subject/calendar held-out stress is much weaker than teacher-world transfer, so this is a representation objective, not yet an action-grade decoder.

다음 행동:

Train a dedicated masked row-support objective, but do not promote it to a submission decoder until group-heldout stress improves.

## Teacher-Transfer Mask Summary

| View | Mean row AUC | Mean row recall@K | Mean cell recall | Retention vs full |
| --- | ---: | ---: | ---: | ---: |
| `mask_cohort_social` | `0.8190` | `0.4107` | `0.3411` | `1.0400` |
| `mask_subject_peer` | `0.8169` | `0.3960` | `0.3411` | `1.0400` |
| `full_composite` | `0.8193` | `0.4132` | `0.3289` | `1.0000` |
| `mask_calendar_sequence` | `0.8128` | `0.3691` | `0.3081` | `0.9383` |
| `mask_target_route_margins` | `0.7811` | `0.3985` | `0.3056` | `0.9367` |
| `mask_latent_geometry` | `0.7728` | `0.4279` | `0.3008` | `0.9175` |
| `human_only_no_prediction` | `0.7250` | `0.2787` | `0.2713` | `0.8342` |
| `prediction_landscape_only` | `0.7215` | `0.3569` | `0.2348` | `0.7142` |

## Group-Heldout Stress Summary

| View | Stress | Mean row AUC | Mean recall@K | Mean BCE |
| --- | --- | ---: | ---: | ---: |
| `full_composite` | `calendar_mod_holdout` | `0.5869` | `0.2289` | `0.6500` |
| `full_composite` | `row_order_holdout` | `0.5803` | `0.1474` | `0.8203` |
| `full_composite` | `subject_mod_holdout` | `0.5080` | `0.1727` | `0.7002` |
| `human_only_no_prediction` | `calendar_mod_holdout` | `0.5483` | `0.1431` | `0.6600` |
| `human_only_no_prediction` | `row_order_holdout` | `0.5575` | `0.1882` | `0.9507` |
| `human_only_no_prediction` | `subject_mod_holdout` | `0.4141` | `0.1585` | `0.6812` |
| `mask_target_route_margins` | `calendar_mod_holdout` | `0.5693` | `0.1931` | `0.6456` |
| `mask_target_route_margins` | `row_order_holdout` | `0.5622` | `0.2239` | `0.8557` |
| `mask_target_route_margins` | `subject_mod_holdout` | `0.4474` | `0.1673` | `0.7334` |
| `prediction_landscape_only` | `calendar_mod_holdout` | `0.5387` | `0.2719` | `0.6906` |
| `prediction_landscape_only` | `row_order_holdout` | `0.5310` | `0.1742` | `0.7641` |
| `prediction_landscape_only` | `subject_mod_holdout` | `0.5705` | `0.1600` | `0.6979` |

## Boundary

- `teacher-transfer`가 강하다는 것은 row-support target이 완전히 public-specific hallucination은 아니라는 뜻이다.
- `group-heldout stress`가 약하다는 것은 아직 action-grade decoder로 바로 쓰기 어렵다는 뜻이다.
- 다음 HS-JEPA objective는 row-support를 masked representation target으로 학습하되, subject/date/order stress를 통과해야 submission decoder로 승격할 수 있다.
