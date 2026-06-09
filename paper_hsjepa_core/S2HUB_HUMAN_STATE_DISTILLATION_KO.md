# OG Human-State Distillation of S2-Hub HS-JEPA

## 실험 목적

직전 실험들로 competition-side decoder는 꽤 선명해졌다.

```text
S-stage factor encoder
  -> S2 listener/hub detector
  -> row-local driver/bridge solver
  -> route-consistent action field
```

하지만 이 구조가 논문형 HS-JEPA가 되려면 한 가지 질문을 반드시 답해야 한다.

> S2-hub / stagebridge action은 public-loss sensor가 만든 대회용 산물인가,
> 아니면 OG raw lifelog에서 만든 human-state representation으로도 설명되는가?

이번 실험은 S2-hub와 stagebridge action을 teacher로 두고,
OG raw lifelog 기반 cohort-relative human-state context가 그 action support를
얼마나 복원하는지 본다.

## 코드

```bash
python3 paper_hsjepa_core/s2hub_human_state_distillation.py
```

## 산출물

제출 후보:

- `submission_hsjepa_ogdistilled_s2hub_jackpot_38d995b0_uploadsafe.csv`
- `submission_hsjepa_ogdistilled_stagebridge_jackpot_96a9fd11_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/s2hub_human_state_distillation/s2hub_human_state_distillation_readout.json`
- `paper_hsjepa_core/outputs/s2hub_human_state_distillation/s2hub_jackpot_cell_student_frame.csv`
- `paper_hsjepa_core/outputs/s2hub_human_state_distillation/s2hub_jackpot_row_student_frame.csv`
- `paper_hsjepa_core/outputs/s2hub_human_state_distillation/s2hub_jackpot_og_gated_action_audit.csv`
- `paper_hsjepa_core/outputs/s2hub_human_state_distillation/stagebridge_jackpot_cell_student_frame.csv`
- `paper_hsjepa_core/outputs/s2hub_human_state_distillation/stagebridge_jackpot_row_student_frame.csv`
- `paper_hsjepa_core/outputs/s2hub_human_state_distillation/stagebridge_jackpot_og_gated_action_audit.csv`

## 실험 구조

Teacher:

- `s2hub_jackpot`: S2-hub decoder가 선택한 68 cells / 34 rows
- `stagebridge_jackpot`: stagebridge decoder가 선택한 82 cells / 41 rows

Student context:

- OG raw lifelog daily aggregation
- cohort-relative human-state latent
- subject normal distance
- peer normal distance
- personal/cohort axis disagreement
- target route margin
- target identity/context

평가 방식:

1. subject-held-out OOF cell support prediction
2. subject-held-out OOF row support prediction
3. full student로 teacher action amplitude를 OG human-state score로 gate
4. upload-safe diagnostic submission 생성

중요한 점:

public score는 teacher를 만드는 데는 이미 들어갔지만,
student context 자체는 public-free OG human-state representation이다.

## 결과 요약

### S2-Hub Teacher Distillation

Teacher:

```text
submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv
```

Teacher action:

| 항목 | 값 |
|---|---:|
| changed cells | 68 |
| changed rows | 34 |

Cell-level OOF:

| feature set | AUC | AP | positive rate |
|---|---:|---:|---:|
| all no-order | 0.779001 | 0.089745 | 0.038857 |
| human + target context | 0.775066 | 0.093683 | 0.038857 |
| human row context only | 0.524970 | 0.044202 | 0.038857 |

Row-level OOF:

| metric | value |
|---|---:|
| positive rows | 34 / 250 |
| AUC | 0.545343 |
| AP | 0.168100 |

OG-gated submission:

```text
submission_hsjepa_ogdistilled_s2hub_jackpot_38d995b0_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| changed cells | 68 |
| mean amp | 0.961749 |
| sign agreement | 0.985294 |
| H088 cosine | -0.004317 |
| upload-safe | true |

### Stagebridge Teacher Distillation

Teacher:

```text
submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv
```

Teacher action:

| 항목 | 값 |
|---|---:|
| changed cells | 82 |
| changed rows | 41 |

Cell-level OOF:

| feature set | AUC | AP | positive rate |
|---|---:|---:|---:|
| all no-order | 0.713656 | 0.088312 | 0.046857 |
| human + target context | 0.721669 | 0.094174 | 0.046857 |
| human row context only | 0.490839 | 0.049358 | 0.046857 |

Row-level OOF:

| metric | value |
|---|---:|
| positive rows | 41 / 250 |
| AUC | 0.492706 |
| AP | 0.170810 |

OG-gated submission:

```text
submission_hsjepa_ogdistilled_stagebridge_jackpot_96a9fd11_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| changed cells | 82 |
| mean amp | 0.953808 |
| sign agreement | 0.975610 |
| H088 cosine | -0.005708 |
| upload-safe | true |

## 핵심 해석

가장 중요한 숫자는 이것이다.

```text
S2-hub cell OOF AUC: 0.775
S2-hub row OOF AUC: 0.545
```

즉 OG human-state context는 cell/target route를 꽤 잘 설명한다.
하지만 어느 row를 고칠지는 거의 설명하지 못한다.

Stagebridge에서도 같은 패턴이다.

```text
stagebridge cell OOF AUC: 0.722
stagebridge row OOF AUC: 0.493
```

따라서 현재 HS-JEPA 분해는 더 명확해진다.

```text
OG Human-State Encoder
  -> target/route/action orientation을 제공

Listener / Assignment Solver
  -> 어느 row를 들을지 결정

Competition Decoder
  -> public/private action safety와 amplitude를 결정
```

## 왜 논문적으로 중요한가

이 실험은 HS-JEPA를 과장하지 않게 해준다.

틀린 주장:

```text
OG human-state encoder만 있으면 row-target correction을 직접 찾을 수 있다.
```

현재 증거가 지지하는 주장:

```text
OG human-state encoder는 action의 의미와 target route를 설명하지만,
row assignment는 별도 listener/assignment module이 필요하다.
```

이것은 JEPA 관점과 잘 맞는다.

- context encoder는 보이지 않는 action representation을 예측한다.
- 하지만 모든 downstream action을 직접 생성하지 않는다.
- action을 실제 row-target correction으로 번역하려면 listener/assignment decoder가 필요하다.

## 제출 판단

`ogdistilled_s2hub_jackpot`은 제출 후보라기보다 architecture diagnostic이다.

좋아질 경우:

```text
OG human-state action-health gate가 S2-hub decoder를 더 안전하게 만든다.
```

나빠질 경우:

```text
OG human-state는 route orientation에는 유용하지만,
amplitude gate로 직접 쓰면 public/private action field를 흐린다.
```

현재 public slot 우선순위는 여전히:

1. `submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv`
2. `submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv`
3. `submission_hsjepa_ogdistilled_s2hub_jackpot_38d995b0_uploadsafe.csv`

세 번째는 성능 1순위가 아니라,
HS-JEPA 본체와 decoder 연결성을 확인하는 제출이다.
