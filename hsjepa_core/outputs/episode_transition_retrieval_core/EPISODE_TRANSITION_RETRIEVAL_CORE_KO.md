# Episode Transition Retrieval Core

## 한 줄 요약

이 실험은 HS-JEPA를 label predictor가 아니라 `다음 인간 생활 episode를 예측하는 world model`로 검증한다.

```text
visible current episode context
  -> predict hidden next-episode representation
  -> retrieve the actual next episode among candidate episodes
  -> freeze representation
  -> low-trust next-label probe
```

## 판정

- verdict: `transition_retrieval_rhythm_dominant_boundary`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`

## 왜 이것이 HS-JEPA Core인가

I-JEPA식 질문을 lifelog에 그대로 옮기면 다음과 같다.

```text
현재의 보이는 human-life context만 보고,
보이지 않는 다음 episode representation을 맞힐 수 있는가?
```

이 실험의 target은 Q/S label이나 submission correction이 아니다.
다음 row의 semantic lifelog representation 자체다.

## Subject-Heldout Retrieval

같은 subject가 train/validation에 동시에 들어가지 않는다.
`current_episode_identity`는 "오늘과 내일이 비슷하다"는 persistence baseline이고,
`subject_relative_context_to_next_state`가 HS-JEPA transition predictor다.

| method | folds | mean_candidate_count | top1_accuracy | top5_recall | mean_rank_pct | lift_top1_vs_random | lift_top5_vs_random | lift_rank_pct_vs_random |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_to_next_state | 5 | 138.000000 | 0.016026 | 0.052224 | 0.412122 | 0.008776 | 0.015972 | 0.087878 |
| current_episode_identity | 5 | 138.000000 | 0.000000 | 0.079885 | 0.421786 | -0.007251 | 0.043632 | 0.078214 |
| subject_relative_context_to_next_state | 5 | 138.000000 | 0.011453 | 0.059064 | 0.455389 | 0.004202 | 0.022812 | 0.044611 |
| rhythm_conditioned_subject_relative_to_next_state | 5 | 138.000000 | 0.012861 | 0.057615 | 0.455466 | 0.005611 | 0.021363 | 0.044534 |
| absolute_context_to_next_state | 5 | 138.000000 | 0.008709 | 0.043629 | 0.486292 | 0.001459 | 0.007376 | 0.013708 |
| global_next_center | 5 | 138.000000 | 0.007251 | 0.036253 | 0.500000 | 0.000000 | 0.000000 | 0.000000 |
| subject_next_center | 5 | 138.000000 | 0.007251 | 0.036253 | 0.500000 | 0.000000 | 0.000000 | 0.000000 |

## Chronological Retrieval

각 subject의 앞 episode로 predictor를 학습하고 뒤 episode를 retrieval한다.

| method | folds | mean_candidate_count | top1_accuracy | top5_recall | mean_rank_pct | lift_top1_vs_random | lift_top5_vs_random | lift_rank_pct_vs_random |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_to_next_state | 1 | 213.000000 | 0.009390 | 0.046948 | 0.411086 | 0.004695 | 0.023474 | 0.088914 |
| current_episode_identity | 1 | 213.000000 | 0.000000 | 0.065728 | 0.414253 | -0.004695 | 0.042254 | 0.085747 |
| subject_relative_context_to_next_state | 1 | 213.000000 | 0.009390 | 0.032864 | 0.426521 | 0.004695 | 0.009390 | 0.073479 |
| rhythm_conditioned_subject_relative_to_next_state | 1 | 213.000000 | 0.004695 | 0.032864 | 0.427496 | 0.000000 | 0.009390 | 0.072504 |
| absolute_context_to_next_state | 1 | 213.000000 | 0.004695 | 0.014085 | 0.474178 | 0.000000 | -0.009390 | 0.025822 |
| global_next_center | 1 | 213.000000 | 0.004695 | 0.023474 | 0.500000 | 0.000000 | 0.000000 | 0.000000 |
| subject_next_center | 1 | 213.000000 | 0.000000 | 0.009390 | 0.670963 | -0.004695 | -0.014085 | -0.170963 |

## Persistence와의 비교

- subject-relative predicted transition rank lift: `0.044611`
- rhythm-conditioned predicted transition rank lift: `0.044534`
- persistence rank lift: `0.078214`
- predicted minus persistence: `-0.033603`

이 값이 양수이면 HS-JEPA predictor가 단순히 현재 episode를 복사하는 것보다 미래 state를 더 잘 잡는다는 뜻이다.
음수이면 현재 상태 persistence가 더 강한 baseline이라는 뜻이다.

## Frozen Next-Label Probe

다음 episode representation이 Q/S label manifold도 조금 더 선형적으로 만드는지 low-trust probe로만 확인한다.
label은 pretext target이 아니라 freeze된 representation을 읽는 probe target이다.

### Subject-Heldout

| feature_set | folds | logloss | auc | average_precision | evaluated_rows |
| --- | --- | --- | --- | --- | --- |
| current_episode_identity | 5 | 0.676404 | 0.517250 | 0.640976 | 440 |
| calendar_to_next_state | 5 | 0.676458 | 0.511593 | 0.634766 | 440 |
| subject_relative_context_to_next_state | 5 | 0.676764 | 0.525249 | 0.638635 | 440 |
| rhythm_conditioned_subject_relative_to_next_state | 5 | 0.676826 | 0.523631 | 0.636714 | 440 |
| subject_next_center | 5 | 0.677010 | 0.500000 | 0.605775 | 440 |
| absolute_context_to_next_state | 5 | 0.677957 | 0.499389 | 0.624510 | 440 |

### Chronological

| feature_set | folds | logloss | auc | average_precision | evaluated_rows |
| --- | --- | --- | --- | --- | --- |
| subject_next_center | 1 | 0.661279 | 0.634236 | 0.720058 | 136 |
| subject_relative_context_to_next_state | 1 | 0.668165 | 0.539231 | 0.639435 | 136 |
| rhythm_conditioned_subject_relative_to_next_state | 1 | 0.668246 | 0.537822 | 0.636688 | 136 |
| absolute_context_to_next_state | 1 | 0.668453 | 0.521309 | 0.631594 | 136 |
| calendar_to_next_state | 1 | 0.668608 | 0.522234 | 0.630197 | 136 |
| current_episode_identity | 1 | 0.668641 | 0.517971 | 0.626078 | 136 |

## 현재 해석

strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA는 단순 static state encoder가 아니라,
visible human-life context에서 다음 human-state episode를 예측하는 transition world model이다.
```

negative이면 경계도 분명하다.

```text
현재 lifelog에서 미래 episode는 대부분 persistence/calendar/subject prior로 설명되고,
HS-JEPA transition predictor는 아직 persistence를 넘는 일반 transition law를 충분히 복원하지 못했다.
```
