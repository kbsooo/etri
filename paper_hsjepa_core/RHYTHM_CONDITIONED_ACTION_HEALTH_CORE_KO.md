# Rhythm-Conditioned Action-Health Core

## 한 줄 요약

이 실험은 HS-JEPA의 rhythm temporal decoder와 listener residual interface가
실제 row-target action toxicity / safe assignment field로 이어지는지 검증한다.

```text
transported human-state grammar
  + listener residual interface
  + rhythm-conditioned temporal decoder
  -> hidden action-health / toxicity representation
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probabilities: `False`
- proprietary embedding API: `False`
- label as pretext target: `False`

## 판정

- verdict: `rhythm_conditioned_action_health_no_safe_assignment_boundary`
- subject delta vs listener-support baseline: `0.000000`
- row-block delta vs listener-support baseline: `0.000000`
- chronological delta vs listener-support baseline: `0.000000`
- chronological rhythm-temporal delta vs action-only: `0.000000`
- subject health-AUC delta vs listener-support baseline: `-0.006253`
- chronological health-AUC delta vs listener-support baseline: `-0.001439`
- subject toxic-tail-AUC delta vs listener-support baseline: `0.001081`
- chronological toxic-tail-AUC delta vs listener-support baseline: `-0.001028`
- accepted target count total: `0`

## Split Results

| split | feature_set | feature_count | health_auc | health_ap | toxic_tail_auc | toxic_tail_ap | selected_gain_sum | selected_cells | selected_positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | action_only | 31 | 0.513232 | 0.541453 | 0.518986 | 0.453380 | 0.000000 | 0 | NA |  |
| chronological_holdout | listener_support_baseline | 34 | 0.513204 | 0.541435 | 0.519060 | 0.457983 | 0.000000 | 0 | NA |  |
| chronological_holdout | rhythm_temporal_decoder | 50 | 0.513090 | 0.540848 | 0.518452 | 0.455720 | 0.000000 | 0 | NA |  |
| chronological_holdout | residual_listener_interface | 215 | 0.510873 | 0.534548 | 0.518183 | 0.453374 | 0.000000 | 0 | NA |  |
| chronological_holdout | rhythm_conditioned_action_health | 724 | 0.511765 | 0.536658 | 0.518031 | 0.453019 | 0.000000 | 0 | NA |  |
| row_block_holdout | action_only | 31 | 0.628251 | 0.614520 | 0.712995 | 0.563943 | 0.000000 | 0 | NA |  |
| row_block_holdout | listener_support_baseline | 34 | 0.634403 | 0.615776 | 0.710794 | 0.567620 | 0.000000 | 0 | NA |  |
| row_block_holdout | rhythm_temporal_decoder | 50 | 0.629081 | 0.613395 | 0.718697 | 0.577562 | 0.000000 | 0 | NA |  |
| row_block_holdout | residual_listener_interface | 215 | 0.628746 | 0.616175 | 0.712352 | 0.568546 | 0.000000 | 0 | NA |  |
| row_block_holdout | rhythm_conditioned_action_health | 724 | 0.631376 | 0.613345 | 0.711851 | 0.566641 | 0.000000 | 0 | NA |  |
| subject_heldout | action_only | 31 | 0.628329 | 0.610779 | 0.710532 | 0.557725 | 0.000000 | 0 | NA |  |
| subject_heldout | listener_support_baseline | 34 | 0.622653 | 0.601564 | 0.704426 | 0.554100 | 0.000000 | 0 | NA |  |
| subject_heldout | rhythm_temporal_decoder | 50 | 0.625262 | 0.606528 | 0.711023 | 0.558090 | 0.000000 | 0 | NA |  |
| subject_heldout | residual_listener_interface | 215 | 0.607859 | 0.587356 | 0.703900 | 0.557378 | 0.000000 | 0 | NA |  |
| subject_heldout | rhythm_conditioned_action_health | 724 | 0.616400 | 0.593863 | 0.705507 | 0.556908 | 0.000000 | 0 | NA |  |

## Chosen Target Policies

| split | feature_set | target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | tail_safe_policy_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject_heldout | action_only | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | action_only | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | action_only | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | action_only | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | action_only | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | action_only | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | action_only | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | listener_support_baseline | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | listener_support_baseline | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | listener_support_baseline | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | listener_support_baseline | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | listener_support_baseline | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | listener_support_baseline | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | listener_support_baseline | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_temporal_decoder | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_temporal_decoder | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_temporal_decoder | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_temporal_decoder | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_temporal_decoder | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_temporal_decoder | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_temporal_decoder | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | residual_listener_interface | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | residual_listener_interface | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | residual_listener_interface | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | residual_listener_interface | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | residual_listener_interface | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | residual_listener_interface | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | residual_listener_interface | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_conditioned_action_health | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_conditioned_action_health | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_conditioned_action_health | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_conditioned_action_health | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_conditioned_action_health | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_conditioned_action_health | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| subject_heldout | rhythm_conditioned_action_health | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | action_only | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | action_only | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | action_only | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | action_only | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | action_only | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | action_only | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | action_only | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | listener_support_baseline | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | listener_support_baseline | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | listener_support_baseline | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | listener_support_baseline | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | listener_support_baseline | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | listener_support_baseline | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | listener_support_baseline | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_temporal_decoder | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_temporal_decoder | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_temporal_decoder | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_temporal_decoder | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_temporal_decoder | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_temporal_decoder | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_temporal_decoder | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | residual_listener_interface | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | residual_listener_interface | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | residual_listener_interface | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | residual_listener_interface | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | residual_listener_interface | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | residual_listener_interface | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | residual_listener_interface | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_conditioned_action_health | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_conditioned_action_health | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_conditioned_action_health | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_conditioned_action_health | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_conditioned_action_health | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_conditioned_action_health | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| chronological_holdout | rhythm_conditioned_action_health | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | action_only | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | action_only | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | action_only | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | action_only | S1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | action_only | S2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | action_only | S3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | action_only | S4 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | listener_support_baseline | Q1 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | listener_support_baseline | Q2 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |
| row_block_holdout | listener_support_baseline | Q3 | False | predicted_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_tail_safe_policy_passed |

## 해석

positive이면:

```text
HS-JEPA core representation은 단순히 label geometry를 만들 뿐 아니라,
visible rhythm context와 listener residual을 통해 action-health field까지 읽을 수 있다.
```

negative이면:

```text
rhythm/residual representation은 label readout에는 도움이 되지만,
safe action assignment로 번역하려면 별도의 action-tail teacher나 adapter가 필요하다.
```

특히 `accepted target count total`이 0이면 다음 믿음은 죽는다.

```text
rhythm-conditioned residual interface alone is already an action-grade decoder.
```

현재 이 실험은 submission 후보가 아니다.
목적은 HS-JEPA core가 action-health로 확장되는지 반증하는 것이다.
