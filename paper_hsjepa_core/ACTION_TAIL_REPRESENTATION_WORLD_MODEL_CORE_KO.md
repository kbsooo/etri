# Action-Tail Representation World Model Core

## 한 줄 요약

이 실험은 HS-JEPA의 다음 단계 질문을 검증한다.

```text
visible human-life context
  -> hidden row-level action-tail representation
  -> row-target action-health decoder
```

직전 실험은 rhythm/residual representation이 곧바로 action decoder가 되지 않는다는
negative boundary였다. 이번에는 action-tail 자체를 hidden target으로 만들고,
그 target을 context에서 예측할 수 있는지 본다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probabilities: `False`
- proprietary embedding API: `False`

## 중요한 경계

- label-derived action-tail teacher 사용: `True`

따라서 이 실험은 pure label-free core claim이 아니다.
정확한 위치는 `HS-JEPA core-to-decoder bridge`다.

## 판정

- verdict: `action_tail_policy_readout_positive_but_pretext_not_readable`
- accepted target count total: `87`
- positive health delta count: `2`
- positive toxic-tail delta count: `4`

best pretext:

```json
{
  "split": "chronological_holdout",
  "source": "relative_lifelog_context",
  "feature_count": 114,
  "teacher_mae": 0.3948399414603621,
  "teacher_mean_baseline_mae": 0.3932944207609489,
  "teacher_mae_lift_vs_mean": -0.0015455206994132165,
  "component_corr": 0.021000931967533765
}
```

best health delta vs listener:

```json
{
  "split": "row_block_holdout",
  "source": "relative_lifelog_context",
  "feature_set": "relative_lifelog_context_tail_plus_listener",
  "health_auc_delta_vs_listener": 0.002415117157974378,
  "toxic_tail_auc_delta_vs_listener": -0.001998299974067197,
  "selected_gain_delta_vs_listener": 0.04775827934547938,
  "accepted_target_delta_vs_listener": 0
}
```

best toxic-tail delta vs listener:

```json
{
  "split": "subject_heldout",
  "source": "transport_rhythm_context",
  "feature_set": "transport_rhythm_context_tail_plus_listener",
  "health_auc_delta_vs_listener": -0.0009685059208868196,
  "toxic_tail_auc_delta_vs_listener": 0.0014020659743653185,
  "selected_gain_delta_vs_listener": 0.6213150133478007,
  "accepted_target_delta_vs_listener": -1
}
```

## Pretext Results

| split | source | feature_count | teacher_mae | teacher_mean_baseline_mae | teacher_mae_lift_vs_mean | component_corr |
| --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | relative_lifelog_context | 114 | 0.394840 | 0.393294 | -0.001546 | 0.021001 |
| chronological_holdout | transport_rhythm_context | 56 | 0.395331 | 0.393294 | -0.002036 | 0.007707 |
| chronological_holdout | listener_rhythm_interface | 686 | 0.397434 | 0.393294 | -0.004140 | 0.006804 |
| row_block_holdout | relative_lifelog_context | 114 | 0.288923 | 0.284766 | -0.004158 | 0.035684 |
| row_block_holdout | transport_rhythm_context | 56 | 0.291377 | 0.284766 | -0.006611 | 0.039834 |
| row_block_holdout | listener_rhythm_interface | 686 | 0.291534 | 0.284766 | -0.006768 | 0.019587 |
| subject_heldout | relative_lifelog_context | 114 | 0.292170 | 0.286017 | -0.006152 | 0.002525 |
| subject_heldout | listener_rhythm_interface | 686 | 0.292985 | 0.286017 | -0.006968 | 0.003570 |
| subject_heldout | transport_rhythm_context | 56 | 0.299480 | 0.286017 | -0.013463 | -0.043698 |

## Action-Health Results

| split | source | feature_set | feature_count | health_auc | toxic_tail_auc | selected_gain_sum | selected_cells | accepted_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | relative_lifelog_context | listener_support_baseline | 34 | 0.509455 | 0.519164 | 5.251456 | 234 | Q2,S1,S2,S3,S4 |
| chronological_holdout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | 47 | 0.509455 | 0.519164 | 5.251456 | 234 | Q2,S1,S2,S3,S4 |
| chronological_holdout | transport_rhythm_context | listener_support_baseline | 34 | 0.509455 | 0.519164 | 5.251456 | 234 | Q2,S1,S2,S3,S4 |
| chronological_holdout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | 47 | 0.509455 | 0.519164 | 5.251456 | 234 | Q2,S1,S2,S3,S4 |
| chronological_holdout | listener_rhythm_interface | listener_support_baseline | 34 | 0.509455 | 0.519164 | 5.251456 | 234 | Q2,S1,S2,S3,S4 |
| chronological_holdout | listener_rhythm_interface | listener_rhythm_interface_tail_plus_listener | 47 | 0.509455 | 0.519164 | 5.251456 | 234 | Q2,S1,S2,S3,S4 |
| chronological_holdout | relative_lifelog_context | action_only | 31 | 0.508843 | 0.519204 | 3.399025 | 117 | Q1,Q2,S2,S3 |
| chronological_holdout | relative_lifelog_context | relative_lifelog_context_tail_representation | 44 | 0.508843 | 0.519204 | 3.399025 | 117 | Q1,Q2,S2,S3 |
| chronological_holdout | transport_rhythm_context | action_only | 31 | 0.508843 | 0.519204 | 3.399025 | 117 | Q1,Q2,S2,S3 |
| chronological_holdout | transport_rhythm_context | transport_rhythm_context_tail_representation | 44 | 0.508843 | 0.519204 | 3.399025 | 117 | Q1,Q2,S2,S3 |
| chronological_holdout | listener_rhythm_interface | action_only | 31 | 0.508843 | 0.519204 | 3.399025 | 117 | Q1,Q2,S2,S3 |
| chronological_holdout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | 44 | 0.508843 | 0.519204 | 3.399025 | 117 | Q1,Q2,S2,S3 |
| row_block_holdout | transport_rhythm_context | transport_rhythm_context_tail_representation | 44 | 0.602598 | 0.719279 | 1.641537 | 54 | Q1,Q2,Q3,S1,S4 |
| row_block_holdout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | 47 | 0.615251 | 0.724019 | 1.402744 | 207 | Q1,Q2,Q3,S1,S2,S3,S4 |
| row_block_holdout | relative_lifelog_context | relative_lifelog_context_tail_representation | 44 | 0.604758 | 0.717641 | 1.241762 | 117 | Q1,Q3,S4 |
| row_block_holdout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | 47 | 0.617641 | 0.722909 | 1.111513 | 144 | Q1,Q3,S1,S2,S3,S4 |
| row_block_holdout | listener_rhythm_interface | listener_rhythm_interface_tail_plus_listener | 47 | 0.614074 | 0.722279 | 1.069507 | 108 | Q1,Q2,Q3,S1,S2,S3,S4 |
| row_block_holdout | relative_lifelog_context | listener_support_baseline | 34 | 0.615226 | 0.724908 | 1.063755 | 270 | Q1,Q2,Q3,S1,S2,S3 |
| row_block_holdout | transport_rhythm_context | listener_support_baseline | 34 | 0.615226 | 0.724908 | 1.063755 | 270 | Q1,Q2,Q3,S1,S2,S3 |
| row_block_holdout | listener_rhythm_interface | listener_support_baseline | 34 | 0.615226 | 0.724908 | 1.063755 | 270 | Q1,Q2,Q3,S1,S2,S3 |
| row_block_holdout | relative_lifelog_context | action_only | 31 | 0.601291 | 0.719442 | 0.762083 | 144 | Q1,Q3,S4 |
| row_block_holdout | transport_rhythm_context | action_only | 31 | 0.601291 | 0.719442 | 0.762083 | 144 | Q1,Q3,S4 |
| row_block_holdout | listener_rhythm_interface | action_only | 31 | 0.601291 | 0.719442 | 0.762083 | 144 | Q1,Q3,S4 |
| row_block_holdout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | 44 | 0.601451 | 0.717175 | 0.733427 | 135 | Q1,Q3,S1 |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | 47 | 0.611423 | 0.721207 | 2.262650 | 171 | Q1,Q2,S2,S3,S4 |
| subject_heldout | relative_lifelog_context | listener_support_baseline | 34 | 0.612392 | 0.719805 | 1.641335 | 81 | Q1,Q2,Q3,S2,S3,S4 |
| subject_heldout | transport_rhythm_context | listener_support_baseline | 34 | 0.612392 | 0.719805 | 1.641335 | 81 | Q1,Q2,Q3,S2,S3,S4 |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | 34 | 0.612392 | 0.719805 | 1.641335 | 81 | Q1,Q2,Q3,S2,S3,S4 |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_plus_listener | 47 | 0.610516 | 0.718907 | 1.411433 | 126 | Q1,Q2,S1,S4 |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | 47 | 0.611014 | 0.718070 | 1.408812 | 288 | Q1,Q2,Q3,S3,S4 |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | 44 | 0.594109 | 0.713038 | 1.343845 | 90 | Q1,Q2,Q3,S1,S4 |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | 44 | 0.593007 | 0.714986 | 1.005774 | 117 | Q1,Q2,S1,S4 |
| subject_heldout | relative_lifelog_context | action_only | 31 | 0.596260 | 0.714852 | 0.843888 | 72 | Q1,Q3,S3,S4 |
| subject_heldout | transport_rhythm_context | action_only | 31 | 0.596260 | 0.714852 | 0.843888 | 72 | Q1,Q3,S3,S4 |
| subject_heldout | listener_rhythm_interface | action_only | 31 | 0.596260 | 0.714852 | 0.843888 | 72 | Q1,Q3,S3,S4 |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | 44 | 0.596016 | 0.712637 | 0.767582 | 63 | Q1,Q2,Q3,S1,S3,S4 |

## Chosen Policies

| split | source | feature_set | target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject_heldout | relative_lifelog_context | action_only | Q1 | True | predicted_gain | top_score | 0.050000 | 45 | 0.692809 | 0.600000 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | action_only | Q2 | False | health_weighted_utility | top_score | 0.100000 | 90 | 0.063617 | 0.511111 | fast_stress_policy_failed |
| subject_heldout | relative_lifelog_context | action_only | Q3 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.053057 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | action_only | S1 | False | tail_safe_utility | top_score | 0.100000 | 90 | 0.171650 | 0.544444 | fast_stress_policy_failed |
| subject_heldout | relative_lifelog_context | action_only | S2 | False | predicted_gain | top_score | 0.010000 | 9 | -0.758346 | 0.000000 | fast_stress_policy_failed |
| subject_heldout | relative_lifelog_context | action_only | S3 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.040047 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | action_only | S4 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.057975 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | listener_support_baseline | Q1 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.117284 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | listener_support_baseline | Q2 | True | predicted_gain | top_score | 0.020000 | 18 | 0.686054 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | listener_support_baseline | Q3 | True | tail_safe_utility | top_score | 0.020000 | 18 | 0.069413 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | listener_support_baseline | S1 | False | pessimistic_utility | top_score | 0.050000 | 45 | -0.036086 | 0.644444 | fast_stress_policy_failed |
| subject_heldout | relative_lifelog_context | listener_support_baseline | S2 | True | predicted_gain | top_score | 0.010000 | 9 | 0.255763 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | listener_support_baseline | S3 | True | predicted_gain | top_score | 0.010000 | 9 | 0.111583 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | listener_support_baseline | S4 | True | predicted_gain | top_score | 0.020000 | 18 | 0.401238 | 0.611111 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | Q1 | True | health_weighted_utility | top_score | 0.020000 | 18 | 0.253970 | 0.722222 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | Q2 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.066694 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | Q3 | True | predicted_gain | top_score | 0.010000 | 9 | 0.128053 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | S1 | True | predicted_gain | top_score | 0.010000 | 9 | 0.092709 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | S2 | False | tail_safe_utility | top_score | 0.020000 | 18 | 0.044676 | 0.388889 | fast_stress_policy_failed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | S3 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.022889 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_representation | S4 | True | predicted_gain | top_score | 0.010000 | 9 | 0.203268 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | Q1 | True | pessimistic_utility | top_score | 0.050000 | 45 | 0.163144 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | Q2 | True | tail_safe_utility | top_score | 0.100000 | 90 | 0.209873 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | Q3 | True | predicted_gain | top_score | 0.020000 | 18 | 0.223060 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | S1 | False | pessimistic_utility | top_score | 0.010000 | 9 | -0.029669 | 0.555556 | fast_stress_policy_failed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | S2 | False | tail_safe_utility | top_score | 0.020000 | 18 | -0.002446 | 0.611111 | fast_stress_policy_failed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | S3 | True | pessimistic_utility | top_score | 0.050000 | 45 | 0.084138 | 0.577778 | fast_stress_policy_passed |
| subject_heldout | relative_lifelog_context | relative_lifelog_context_tail_plus_listener | S4 | True | predicted_gain | top_score | 0.100000 | 90 | 0.728597 | 0.588889 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | action_only | Q1 | True | predicted_gain | top_score | 0.050000 | 45 | 0.692809 | 0.600000 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | action_only | Q2 | False | health_weighted_utility | top_score | 0.100000 | 90 | 0.063617 | 0.511111 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | action_only | Q3 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.053057 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | action_only | S1 | False | tail_safe_utility | top_score | 0.100000 | 90 | 0.171650 | 0.544444 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | action_only | S2 | False | predicted_gain | top_score | 0.010000 | 9 | -0.758346 | 0.000000 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | action_only | S3 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.040047 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | action_only | S4 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.057975 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | listener_support_baseline | Q1 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.117284 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | listener_support_baseline | Q2 | True | predicted_gain | top_score | 0.020000 | 18 | 0.686054 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | listener_support_baseline | Q3 | True | tail_safe_utility | top_score | 0.020000 | 18 | 0.069413 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | listener_support_baseline | S1 | False | pessimistic_utility | top_score | 0.050000 | 45 | -0.036086 | 0.644444 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | listener_support_baseline | S2 | True | predicted_gain | top_score | 0.010000 | 9 | 0.255763 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | listener_support_baseline | S3 | True | predicted_gain | top_score | 0.010000 | 9 | 0.111583 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | listener_support_baseline | S4 | True | predicted_gain | top_score | 0.020000 | 18 | 0.401238 | 0.611111 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | Q1 | True | predicted_gain | top_score | 0.050000 | 45 | 0.723837 | 0.644444 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | Q2 | True | predicted_gain | top_score | 0.020000 | 18 | 0.112284 | 0.611111 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | Q3 | False | health_weighted_utility | top_score | 0.100000 | 90 | 0.150041 | 0.544444 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | S1 | True | tail_safe_utility | top_score | 0.050000 | 45 | 0.141661 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | S2 | False | predicted_gain | top_score | 0.010000 | 9 | 0.175758 | 0.444444 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | S3 | False | health_weighted_utility | top_score | 0.020000 | 18 | -0.022333 | 0.555556 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_representation | S4 | True | tail_safe_utility | top_score | 0.010000 | 9 | 0.027992 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | Q1 | True | tail_safe_utility | top_score | 0.050000 | 45 | 0.203371 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | Q2 | True | predicted_gain | top_score | 0.010000 | 9 | 0.120955 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | Q3 | False | tail_safe_utility | top_score | 0.010000 | 9 | -0.013899 | 0.333333 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | S1 | False | health_weighted_utility | top_score | 0.010000 | 9 | -0.095769 | 0.555556 | fast_stress_policy_failed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | S2 | True | predicted_gain | top_score | 0.100000 | 90 | 1.449155 | 0.600000 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | S3 | True | tail_safe_utility | top_score | 0.010000 | 9 | 0.114213 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | transport_rhythm_context | transport_rhythm_context_tail_plus_listener | S4 | True | predicted_gain | top_score | 0.020000 | 18 | 0.374956 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | action_only | Q1 | True | predicted_gain | top_score | 0.050000 | 45 | 0.692809 | 0.600000 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | action_only | Q2 | False | health_weighted_utility | top_score | 0.100000 | 90 | 0.063617 | 0.511111 | fast_stress_policy_failed |
| subject_heldout | listener_rhythm_interface | action_only | Q3 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.053057 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | action_only | S1 | False | tail_safe_utility | top_score | 0.100000 | 90 | 0.171650 | 0.544444 | fast_stress_policy_failed |
| subject_heldout | listener_rhythm_interface | action_only | S2 | False | predicted_gain | top_score | 0.010000 | 9 | -0.758346 | 0.000000 | fast_stress_policy_failed |
| subject_heldout | listener_rhythm_interface | action_only | S3 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.040047 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | action_only | S4 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.057975 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | Q1 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.117284 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | Q2 | True | predicted_gain | top_score | 0.020000 | 18 | 0.686054 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | Q3 | True | tail_safe_utility | top_score | 0.020000 | 18 | 0.069413 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | S1 | False | pessimistic_utility | top_score | 0.050000 | 45 | -0.036086 | 0.644444 | fast_stress_policy_failed |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | S2 | True | predicted_gain | top_score | 0.010000 | 9 | 0.255763 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | S3 | True | predicted_gain | top_score | 0.010000 | 9 | 0.111583 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_support_baseline | S4 | True | predicted_gain | top_score | 0.020000 | 18 | 0.401238 | 0.611111 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | Q1 | True | health_weighted_utility | top_score | 0.020000 | 18 | 0.232490 | 0.722222 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | Q2 | True | predicted_gain | top_score | 0.010000 | 9 | 0.196181 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | Q3 | True | predicted_gain | top_score | 0.010000 | 9 | 0.012728 | 0.555556 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | S1 | True | predicted_gain | top_score | 0.050000 | 45 | 0.841314 | 0.600000 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | S2 | False | pessimistic_utility | top_score | 0.050000 | 45 | 0.009491 | 0.488889 | fast_stress_policy_failed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | S3 | False | health_weighted_utility | top_score | 0.050000 | 45 | -0.035074 | 0.577778 | fast_stress_policy_failed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_representation | S4 | True | pessimistic_utility | top_score | 0.010000 | 9 | 0.061132 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_plus_listener | Q1 | True | health_weighted_utility | top_score | 0.010000 | 9 | 0.120070 | 0.777778 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_plus_listener | Q2 | True | predicted_gain | top_score | 0.010000 | 9 | 0.284394 | 0.666667 | fast_stress_policy_passed |
| subject_heldout | listener_rhythm_interface | listener_rhythm_interface_tail_plus_listener | Q3 | False | predicted_gain | top_score | 0.010000 | 9 | -0.043578 | 0.555556 | fast_stress_policy_failed |

## 해석

positive이면:

```text
HS-JEPA는 visible context에서 action-tail representation을 예측할 수 있고,
그 representation은 release-grade action-health decoder에 기여한다.
```

negative이면:

```text
action-tail teacher를 만들었더라도 현재 visible context/world-model interface는
release-safe row-target assignment로 번역하기에 부족하다.
```

이번 실험이 중요한 이유는 실패해도 명확하다.
실패하면 다음 결론이 생긴다.

```text
action-tail은 단순히 row-level hidden vector로 만들면 충분하지 않다.
target-route/listener별 structured action-tail teacher가 필요하다.
```
