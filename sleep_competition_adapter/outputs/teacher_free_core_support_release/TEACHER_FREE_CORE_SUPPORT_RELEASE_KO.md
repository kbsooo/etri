# Teacher-Free Core Support Release

## 목적

이 실험은 기존 action teacher 없이 HS-JEPA core geometry만으로 row-state frontier 일부를 재발견할 수 있는지 본다.

Support score는 다음만 사용한다.

- OG lifelog-derived human-state latent
- personal/cohort outlier score
- train-label nearest-neighbor target margin
- calendar edge signal

Public LB와 action teacher label은 support score 계산에 쓰지 않는다.

## Row-State Frontier 재발견

| reference | top_fraction | k | reference_rows | overlap_rows | recall | precision |
| --- | --- | --- | --- | --- | --- | --- |
| frontier_active_silence_rows | 0.100000 | 25 | 45 | 5 | 0.111111 | 0.200000 |
| frontier_active_silence_rows | 0.150000 | 38 | 45 | 6 | 0.133333 | 0.157895 |
| frontier_active_silence_rows | 0.180000 | 45 | 45 | 8 | 0.177778 | 0.177778 |
| frontier_active_silence_rows | 0.220000 | 55 | 45 | 11 | 0.244444 | 0.200000 |
| frontier_active_silence_rows | 0.280000 | 70 | 45 | 16 | 0.355556 | 0.228571 |
| row_state_vector_rows | 0.100000 | 25 | 45 | 5 | 0.111111 | 0.200000 |
| row_state_vector_rows | 0.150000 | 38 | 45 | 6 | 0.133333 | 0.157895 |
| row_state_vector_rows | 0.180000 | 45 | 45 | 8 | 0.177778 | 0.177778 |
| row_state_vector_rows | 0.220000 | 55 | 45 | 11 | 0.244444 | 0.200000 |
| row_state_vector_rows | 0.280000 | 70 | 45 | 16 | 0.355556 | 0.228571 |

## 생성된 후보

- `submission_hsjepa_teacher_free_core_support_release_8d9899fb_uploadsafe.csv`

base probability prior는 `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`다. 즉 row-state frontier file을 action anchor로 쓰지 않는다.

핵심 수치:

- changed rows: `40`
- changed cells: `160`
- mean abs logit move: `0.097056`
- max abs logit move: `0.271152`

Target action counts:

`{'S4': 40, 'Q2': 34, 'S2': 25, 'S1': 22, 'S3': 19, 'Q3': 18, 'Q1': 2}`

## 해석

좋아지면 HS-JEPA core가 teacher-free row support와 outlier route만으로도 action-grade correction 일부를 만들 수 있다는 뜻이다.

나빠지면 core geometry는 frontier row를 어느 정도 재발견할 수 있어도, target/listener-specific assignment 없이는 release가 아직 toxic하다는 뜻이다.
